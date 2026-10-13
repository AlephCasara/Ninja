from __future__ import annotations

from datetime import UTC, datetime, timedelta

import duckdb

from ninja_labs.split_data import materialize_split_panels


def test_materialize_split_panels_separates_untouched_test(tmp_path):
    aligned = tmp_path / "aligned.parquet"
    con = duckdb.connect()
    con.execute(
        """
        CREATE TABLE aligned (
            decision_time TIMESTAMPTZ,
            split VARCHAR,
            value DOUBLE
        )
        """
    )
    start = datetime(2024, 1, 1, tzinfo=UTC)
    rows = []
    for index, split in enumerate(("train", "train", "validation", "untouched_test")):
        rows.append((start + timedelta(minutes=15 * index), split, float(index)))
    con.executemany("INSERT INTO aligned VALUES (?,?,?)", rows)
    con.execute("COPY aligned TO ? (FORMAT PARQUET)", [str(aligned)])
    con.close()

    result = materialize_split_panels(aligned_path=aligned, output_dir=tmp_path / "splits")
    assert result["train"][1] == 2
    assert result["validation"][1] == 1
    assert result["untouched_test"][1] == 1

    con = duckdb.connect()
    assert con.execute(
        "SELECT DISTINCT split FROM read_parquet(?)", [str(result["train"][0])]
    ).fetchall() == [("train",)]
    assert con.execute(
        "SELECT DISTINCT split FROM read_parquet(?)", [str(result["validation"][0])]
    ).fetchall() == [("validation",)]
    assert con.execute(
        "SELECT DISTINCT split FROM read_parquet(?)", [str(result["untouched_test"][0])]
    ).fetchall() == [("untouched_test",)]
    con.close()
