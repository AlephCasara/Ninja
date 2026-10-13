from __future__ import annotations

from pathlib import Path

import duckdb


ALLOWED_SPLITS = ("train", "validation", "untouched_test")


def _sql_string(value: str) -> str:
    """Return a DuckDB SQL string literal for an internally generated path."""

    return "'" + value.replace("'", "''") + "'"


def materialize_split_panels(
    *,
    aligned_path: Path,
    output_dir: Path,
) -> dict[str, tuple[Path, int]]:
    """Write one Parquet per split so development code need not open test rows."""

    output_dir.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    input_sql = _sql_string(str(aligned_path))
    con.execute(
        f"CREATE TEMP VIEW aligned_source AS SELECT * FROM read_parquet({input_sql})"
    )
    present = {
        str(row[0]): int(row[1])
        for row in con.execute(
            "SELECT split, count(*) FROM aligned_source GROUP BY split"
        ).fetchall()
    }
    unexpected = set(present) - set(ALLOWED_SPLITS) - {"outside"}
    if unexpected:
        con.close()
        raise ValueError(f"unexpected aligned split labels: {sorted(unexpected)}")

    result: dict[str, tuple[Path, int]] = {}
    for split in ALLOWED_SPLITS:
        path = output_dir / f"aligned_{split}.parquet"
        output_sql = _sql_string(str(path))
        con.execute(
            f"COPY (SELECT * FROM aligned_source WHERE split = '{split}' ORDER BY decision_time) "
            f"TO {output_sql} (FORMAT PARQUET, COMPRESSION ZSTD)"
        )
        result[split] = (path, present.get(split, 0))
    con.close()
    return result
