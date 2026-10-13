from __future__ import annotations

import json
import math
import uuid
from collections import Counter, defaultdict
from collections.abc import Iterable
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import duckdb

from ninja_labs.util import canonical_json_bytes, iso_utc, parse_utc, sha256_bytes

OBSERVATION_COLUMNS = (
    "schema_version",
    "observation_id",
    "source_id",
    "source_type",
    "platform",
    "published_at",
    "first_seen_at",
    "collected_at",
    "available_at",
    "available_at_basis",
    "temporal_quality",
    "author_id",
    "thread_id",
    "parent_id",
    "entity_refs_json",
    "content_ref",
    "content_hash",
    "structured_fields_json",
    "provenance_json",
    "subreddit",
)


def interval_seconds(value: str) -> int:
    unit = value[-1]
    amount = int(value[:-1])
    factors = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    if unit not in factors or amount <= 0:
        raise ValueError(f"unsupported interval: {value}")
    return amount * factors[unit]


def _reddit_observation(
    raw: dict[str, Any],
    *,
    collected_at: datetime,
    bronze_ref: str,
    manifest_id: str,
) -> tuple[Any, ...]:
    post_id = str(raw["id"])
    published_at = parse_utc(raw["created_utc"])
    retrieved_raw = raw.get("retrieved_on")
    if retrieved_raw is not None:
        retrieved_at = parse_utc(retrieved_raw)
        available_at = max(published_at, retrieved_at)
        basis = "archive_capture"
        temporal_quality = "archive_capture"
        first_seen_at: datetime | None = retrieved_at
    else:
        available_at = published_at
        basis = "published"
        temporal_quality = "source_timestamp"
        first_seen_at = None

    content_payload = {
        "id": post_id,
        "author": raw.get("author"),
        "created_utc": raw.get("created_utc"),
        "subreddit": raw.get("subreddit"),
        "title": raw.get("title"),
        "selftext": raw.get("selftext"),
        "url": raw.get("url"),
    }
    content_hash = sha256_bytes(canonical_json_bytes(content_payload))
    source_id = f"reddit:{post_id}"
    structured = {
        "subreddit": raw.get("subreddit"),
        "title": raw.get("title"),
        "selftext": raw.get("selftext"),
        "url": raw.get("url"),
    }
    provenance = {
        "collector_id": "arctic-shift",
        "collector_version": "api-v1",
        "retrieval_ref": "https://arctic-shift.photon-reddit.com/api/posts/search",
        "raw_ref": bronze_ref,
        "dataset_manifest_id": manifest_id,
    }
    return (
        1,
        str(uuid.uuid5(uuid.NAMESPACE_URL, source_id)),
        source_id,
        "reddit_post",
        "reddit",
        published_at,
        first_seen_at,
        collected_at,
        available_at,
        basis,
        temporal_quality,
        raw.get("author"),
        post_id,
        None,
        json.dumps([], separators=(",", ":")),
        f"{bronze_ref}#{source_id}",
        content_hash,
        json.dumps(structured, ensure_ascii=False, separators=(",", ":")),
        json.dumps(provenance, separators=(",", ":")),
        raw.get("subreddit"),
    )


def write_reddit_dataset(
    rows: Iterable[dict[str, Any]],
    *,
    bronze_path: Path,
    silver_path: Path,
    collected_at: datetime,
    manifest_id: str,
) -> int:
    bronze_path.parent.mkdir(parents=True, exist_ok=True)
    silver_path.parent.mkdir(parents=True, exist_ok=True)
    bronze_ref = str(bronze_path)

    con = duckdb.connect()
    con.execute(
        """
        CREATE TABLE observations (
            schema_version INTEGER,
            observation_id VARCHAR,
            source_id VARCHAR,
            source_type VARCHAR,
            platform VARCHAR,
            published_at TIMESTAMPTZ,
            first_seen_at TIMESTAMPTZ,
            collected_at TIMESTAMPTZ,
            available_at TIMESTAMPTZ,
            available_at_basis VARCHAR,
            temporal_quality VARCHAR,
            author_id VARCHAR,
            thread_id VARCHAR,
            parent_id VARCHAR,
            entity_refs_json VARCHAR,
            content_ref VARCHAR,
            content_hash VARCHAR,
            structured_fields_json VARCHAR,
            provenance_json VARCHAR,
            subreddit VARCHAR
        )
        """
    )
    placeholders = ",".join(["?"] * len(OBSERVATION_COLUMNS))
    insert_sql = f"INSERT INTO observations VALUES ({placeholders})"
    batch: list[tuple[Any, ...]] = []
    count = 0

    with bronze_path.open("w", encoding="utf-8") as bronze:
        for raw in rows:
            bronze.write(
                json.dumps(raw, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
                + "\n"
            )
            batch.append(
                _reddit_observation(
                    raw,
                    collected_at=collected_at,
                    bronze_ref=bronze_ref,
                    manifest_id=manifest_id,
                )
            )
            count += 1
            if len(batch) >= 1000:
                con.executemany(insert_sql, batch)
                batch.clear()
        if batch:
            con.executemany(insert_sql, batch)

    con.execute(
        "COPY observations TO ? (FORMAT PARQUET, COMPRESSION ZSTD)",
        [str(silver_path)],
    )
    con.close()
    return count


def write_market_dataset(
    rows: Iterable[dict[str, Any]],
    *,
    silver_path: Path,
) -> int:
    silver_path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.execute(
        """
        CREATE TABLE market (
            symbol VARCHAR,
            interval VARCHAR,
            open_time TIMESTAMPTZ,
            close_time TIMESTAMPTZ,
            decision_time TIMESTAMPTZ,
            open DOUBLE,
            high DOUBLE,
            low DOUBLE,
            close DOUBLE,
            volume DOUBLE,
            quote_volume DOUBLE,
            trade_count BIGINT,
            taker_buy_base_volume DOUBLE,
            taker_buy_quote_volume DOUBLE
        )
        """
    )
    insert_sql = "INSERT INTO market VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
    batch: list[tuple[Any, ...]] = []
    count = 0
    for row in rows:
        batch.append(tuple(row[key] for key in (
            "symbol",
            "interval",
            "open_time",
            "close_time",
            "decision_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "quote_volume",
            "trade_count",
            "taker_buy_base_volume",
            "taker_buy_quote_volume",
        )))
        count += 1
        if len(batch) >= 2000:
            con.executemany(insert_sql, batch)
            batch.clear()
    if batch:
        con.executemany(insert_sql, batch)
    con.execute("COPY market TO ? (FORMAT PARQUET, COMPRESSION ZSTD)", [str(silver_path)])
    con.close()
    return count


def _window_end(value: datetime, seconds: int) -> datetime:
    epoch = int(value.timestamp())
    boundary = ((epoch // seconds) + 1) * seconds
    return datetime.fromtimestamp(boundary, tz=UTC)


def build_attention_gold(
    *,
    observations_path: Path,
    output_path: Path,
    start: datetime,
    end: datetime,
    interval: str,
) -> int:
    seconds = interval_seconds(interval)
    con = duckdb.connect()
    rows = con.execute(
        """
        SELECT available_at, author_id, subreddit
        FROM read_parquet(?)
        WHERE available_at >= ? AND available_at < ?
        ORDER BY available_at
        """,
        [str(observations_path), start, end],
    ).fetchall()
    con.close()

    buckets: dict[datetime, dict[str, Any]] = defaultdict(
        lambda: {
            "message_count": 0,
            "authors": Counter(),
            "sources": set(),
            "max_available_at": None,
        }
    )
    for available_at, author_id, subreddit in rows:
        available = parse_utc(available_at)
        window_end = _window_end(available, seconds)
        bucket = buckets[window_end]
        bucket["message_count"] += 1
        if author_id:
            bucket["authors"][str(author_id)] += 1
        if subreddit:
            bucket["sources"].add(str(subreddit))
        current_max = bucket["max_available_at"]
        if current_max is None or available > current_max:
            bucket["max_available_at"] = available

    complete: list[tuple[Any, ...]] = []
    cursor = _window_end(start - timedelta(microseconds=1), seconds)
    while cursor <= end:
        if cursor <= start:
            cursor += timedelta(seconds=seconds)
            continue
        bucket = buckets.get(cursor)
        if bucket is None:
            complete.append(
                (
                    cursor - timedelta(seconds=seconds),
                    cursor,
                    0,
                    0,
                    0.0,
                    0.0,
                    0.0,
                    None,
                )
            )
        else:
            authors: Counter[str] = bucket["authors"]
            author_total = sum(authors.values())
            unique_authors = len(authors)
            if author_total:
                probabilities = [count / author_total for count in authors.values()]
                hhi = sum(p * p for p in probabilities)
                entropy = -sum(p * math.log(p) for p in probabilities if p > 0)
                entropy_norm = entropy / math.log(unique_authors) if unique_authors > 1 else 0.0
            else:
                hhi = 0.0
                entropy = 0.0
                entropy_norm = 0.0
            complete.append(
                (
                    cursor - timedelta(seconds=seconds),
                    cursor,
                    int(bucket["message_count"]),
                    unique_authors,
                    float(hhi),
                    float(entropy),
                    float(entropy_norm),
                    bucket["max_available_at"],
                )
            )
        cursor += timedelta(seconds=seconds)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.execute(
        """
        CREATE TABLE attention (
            window_start TIMESTAMPTZ,
            window_end TIMESTAMPTZ,
            message_count BIGINT,
            unique_author_count BIGINT,
            author_hhi DOUBLE,
            author_entropy DOUBLE,
            author_entropy_normalized DOUBLE,
            max_available_at TIMESTAMPTZ
        )
        """
    )
    if complete:
        con.executemany("INSERT INTO attention VALUES (?,?,?,?,?,?,?,?)", complete)
    con.execute("COPY attention TO ? (FORMAT PARQUET, COMPRESSION ZSTD)", [str(output_path)])
    con.close()
    return len(complete)


def split_for_time(value: datetime, splits: dict[str, tuple[datetime, datetime]]) -> str:
    memberships = [name for name, (start, end) in splits.items() if start <= value < end]
    if len(memberships) > 1:
        raise ValueError(f"split overlap at {iso_utc(value)}: {memberships}")
    return memberships[0] if memberships else "outside"


def validate_splits(splits: dict[str, tuple[datetime, datetime]]) -> None:
    required = {"train", "validation", "untouched_test"}
    if set(splits) != required:
        raise ValueError(f"splits must be exactly {sorted(required)}")
    ordered = sorted((start, end, name) for name, (start, end) in splits.items())
    for start, end, name in ordered:
        if start >= end:
            raise ValueError(f"invalid split {name}: start must precede end")
    for (_, previous_end, previous_name), (next_start, _, next_name) in zip(
        ordered, ordered[1:]
    ):
        if next_start < previous_end:
            raise ValueError(f"split overlap: {previous_name} and {next_name}")


def build_aligned_panel(
    *,
    attention_path: Path,
    market_path: Path,
    output_path: Path,
    splits: dict[str, tuple[datetime, datetime]],
) -> int:
    validate_splits(splits)
    con = duckdb.connect()
    attention_rows = con.execute(
        """
        SELECT window_end, message_count, unique_author_count, author_hhi,
               author_entropy, author_entropy_normalized, max_available_at
        FROM read_parquet(?) ORDER BY window_end
        """,
        [str(attention_path)],
    ).fetchall()
    market_rows = con.execute(
        """
        SELECT symbol, interval, open_time, close_time, decision_time,
               open, high, low, close, volume, quote_volume, trade_count
        FROM read_parquet(?) ORDER BY decision_time
        """,
        [str(market_path)],
    ).fetchall()
    con.close()

    aligned: list[tuple[Any, ...]] = []
    index = 0
    latest: tuple[Any, ...] | None = None
    for market in market_rows:
        decision_time = parse_utc(market[4])
        while index < len(attention_rows) and parse_utc(attention_rows[index][0]) <= decision_time:
            latest = attention_rows[index]
            index += 1
        if latest is None:
            continue
        feature_window_end = parse_utc(latest[0])
        max_available_raw = latest[6]
        if feature_window_end > decision_time:
            raise ValueError("lookahead: feature window ends after market decision time")
        if max_available_raw is not None and parse_utc(max_available_raw) > decision_time:
            raise ValueError("lookahead: observation became available after market decision time")
        aligned.append(
            (
                *market,
                split_for_time(decision_time, splits),
                feature_window_end,
                int(latest[1]),
                int(latest[2]),
                float(latest[3]),
                float(latest[4]),
                float(latest[5]),
                parse_utc(max_available_raw) if max_available_raw is not None else None,
            )
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.execute(
        """
        CREATE TABLE aligned (
            symbol VARCHAR,
            market_interval VARCHAR,
            open_time TIMESTAMPTZ,
            close_time TIMESTAMPTZ,
            decision_time TIMESTAMPTZ,
            open DOUBLE,
            high DOUBLE,
            low DOUBLE,
            close DOUBLE,
            volume DOUBLE,
            quote_volume DOUBLE,
            trade_count BIGINT,
            split VARCHAR,
            feature_window_end TIMESTAMPTZ,
            message_count BIGINT,
            unique_author_count BIGINT,
            author_hhi DOUBLE,
            author_entropy DOUBLE,
            author_entropy_normalized DOUBLE,
            feature_max_available_at TIMESTAMPTZ
        )
        """
    )
    if aligned:
        con.executemany("INSERT INTO aligned VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", aligned)
    con.execute("COPY aligned TO ? (FORMAT PARQUET, COMPRESSION ZSTD)", [str(output_path)])
    con.close()
    return len(aligned)
