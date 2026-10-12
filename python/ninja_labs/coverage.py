from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import duckdb

from ninja_labs.phase1 import interval_seconds


def _one(con: duckdb.DuckDBPyConnection, query: str, params: list[Any]) -> dict[str, Any]:
    cursor = con.execute(query, params)
    row = cursor.fetchone()
    columns = [column[0] for column in cursor.description]
    return dict(zip(columns, row, strict=True))


def build_coverage_report(
    *,
    observations_path: Path,
    market_path: Path,
    attention_path: Path,
    aligned_path: Path,
    market_interval: str,
    output_path: Path,
) -> dict[str, Any]:
    interval = interval_seconds(market_interval)
    con = duckdb.connect()

    observations = _one(
        con,
        """
        SELECT
            count(*) AS rows,
            min(published_at) AS min_published_at,
            max(published_at) AS max_published_at,
            min(available_at) AS min_available_at,
            max(available_at) AS max_available_at,
            count(DISTINCT author_id) FILTER (WHERE author_id IS NOT NULL) AS unique_authors,
            count(DISTINCT subreddit) FILTER (WHERE subreddit IS NOT NULL) AS unique_communities,
            count(*) FILTER (WHERE temporal_quality = 'archive_capture') AS archive_capture_rows,
            count(*) FILTER (WHERE temporal_quality = 'source_timestamp') AS source_timestamp_rows
        FROM read_parquet(?)
        """,
        [str(observations_path)],
    )

    market = _one(
        con,
        """
        WITH ordered AS (
            SELECT
                open_time,
                close_time,
                decision_time,
                epoch(open_time - lag(open_time) OVER (ORDER BY open_time)) AS gap_seconds
            FROM read_parquet(?)
        )
        SELECT
            count(*) AS rows,
            min(open_time) AS min_open_time,
            max(close_time) AS max_close_time,
            count(*) FILTER (WHERE gap_seconds > ?) AS gap_count,
            max(gap_seconds) AS max_gap_seconds
        FROM ordered
        """,
        [str(market_path), interval * 1.5],
    )

    attention = _one(
        con,
        """
        SELECT
            count(*) AS rows,
            min(window_start) AS min_window_start,
            max(window_end) AS max_window_end,
            count(*) FILTER (WHERE message_count = 0) AS zero_windows,
            count(*) FILTER (WHERE message_count > 0) AS nonzero_windows,
            max(message_count) AS max_message_count
        FROM read_parquet(?)
        """,
        [str(attention_path)],
    )

    split_rows = con.execute(
        """
        SELECT split, count(*) AS rows
        FROM read_parquet(?)
        GROUP BY split
        ORDER BY split
        """,
        [str(aligned_path)],
    ).fetchall()
    aligned = _one(
        con,
        """
        SELECT
            count(*) AS rows,
            count(*) FILTER (WHERE feature_window_end > decision_time) AS future_window_rows,
            count(*) FILTER (
                WHERE feature_max_available_at IS NOT NULL
                  AND feature_max_available_at > decision_time
            ) AS future_observation_rows,
            min(decision_time) AS min_decision_time,
            max(decision_time) AS max_decision_time
        FROM read_parquet(?)
        """,
        [str(aligned_path)],
    )
    con.close()

    aligned["rows_by_split"] = {name: count for name, count in split_rows}
    report = {
        "schema_version": 1,
        "observations": observations,
        "market": market,
        "attention": attention,
        "aligned": aligned,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, indent=2, default=str, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report
