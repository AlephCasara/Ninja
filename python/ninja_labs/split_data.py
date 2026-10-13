from __future__ import annotations

from pathlib import Path

import duckdb


ALLOWED_SPLITS = ("train", "validation", "untouched_test")


def materialize_split_panels(
    *,
    aligned_path: Path,
    output_dir: Path,
) -> dict[str, tuple[Path, int]]:
    """Write one Parquet per split so development code need not open test rows."""

    output_dir.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    present = {
        str(row[0]): int(row[1])
        for row in con.execute(
            "SELECT split, count(*) FROM read_parquet(?) GROUP BY split",
            [str(aligned_path)],
        ).fetchall()
    }
    unexpected = set(present) - set(ALLOWED_SPLITS) - {"outside"}
    if unexpected:
        con.close()
        raise ValueError(f"unexpected aligned split labels: {sorted(unexpected)}")

    result: dict[str, tuple[Path, int]] = {}
    for split in ALLOWED_SPLITS:
        path = output_dir / f"aligned_{split}.parquet"
        # Split is a controlled enum, not user input.
        con.execute(
            f"COPY (SELECT * FROM read_parquet(?) WHERE split = '{split}' ORDER BY decision_time) "
            "TO ? (FORMAT PARQUET, COMPRESSION ZSTD)",
            [str(aligned_path), str(path)],
        )
        result[split] = (path, present.get(split, 0))
    con.close()
    return result
