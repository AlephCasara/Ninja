from __future__ import annotations

from datetime import UTC, datetime, timedelta

import duckdb
import pytest

from ninja_labs.phase1 import (
    build_aligned_panel,
    build_attention_gold,
    split_for_time,
    validate_splits,
    write_market_dataset,
    write_reddit_dataset,
)


def dt(hour: int, minute: int = 0) -> datetime:
    return datetime(2025, 1, 1, hour, minute, tzinfo=UTC)


def test_attention_uses_available_at_not_published_at(tmp_path):
    raw = {
        "id": "abc123",
        "author": "alice",
        "created_utc": int(dt(0, 1).timestamp()),
        "retrieved_on": int(dt(0, 16).timestamp()),
        "subreddit": "Bitcoin",
        "title": "BTC",
        "selftext": "test",
        "url": "https://example.invalid/post",
    }
    bronze = tmp_path / "bronze.jsonl"
    observations = tmp_path / "observations.parquet"
    attention = tmp_path / "attention.parquet"

    write_reddit_dataset(
        [raw],
        bronze_path=bronze,
        silver_path=observations,
        collected_at=dt(1),
        manifest_id="test-manifest",
    )
    build_attention_gold(
        observations_path=observations,
        output_path=attention,
        start=dt(0),
        end=dt(0, 30),
        interval="15m",
    )

    rows = duckdb.connect().execute(
        "SELECT window_end, message_count FROM read_parquet(?) ORDER BY window_end",
        [str(attention)],
    ).fetchall()
    assert rows[0][1] == 0
    assert rows[1][1] == 1


def test_market_decision_time_is_after_close(tmp_path):
    market = tmp_path / "market.parquet"
    close = dt(0, 14) + timedelta(seconds=59, milliseconds=999)
    write_market_dataset(
        [
            {
                "symbol": "BTCUSDT",
                "interval": "15m",
                "open_time": dt(0),
                "close_time": close,
                "decision_time": dt(0, 15),
                "open": 1.0,
                "high": 2.0,
                "low": 0.5,
                "close": 1.5,
                "volume": 10.0,
                "quote_volume": 15.0,
                "trade_count": 2,
                "taker_buy_base_volume": 4.0,
                "taker_buy_quote_volume": 6.0,
            }
        ],
        silver_path=market,
    )
    decision, close_time = duckdb.connect().execute(
        "SELECT decision_time, close_time FROM read_parquet(?)", [str(market)]
    ).fetchone()
    assert decision > close_time


def test_split_overlap_is_rejected():
    splits = {
        "train": (dt(0), dt(1)),
        "validation": (dt(0, 30), dt(2)),
        "untouched_test": (dt(2), dt(3)),
    }
    with pytest.raises(ValueError, match="overlap"):
        validate_splits(splits)


def test_split_boundaries_are_left_closed_right_open():
    splits = {
        "train": (dt(0), dt(1)),
        "validation": (dt(1), dt(2)),
        "untouched_test": (dt(2), dt(3)),
    }
    validate_splits(splits)
    assert split_for_time(dt(0), splits) == "train"
    assert split_for_time(dt(1), splits) == "validation"
    assert split_for_time(dt(2), splits) == "untouched_test"
    assert split_for_time(dt(3), splits) == "outside"


def test_alignment_rejects_future_available_information(tmp_path):
    attention = tmp_path / "attention.parquet"
    market = tmp_path / "market.parquet"
    aligned = tmp_path / "aligned.parquet"

    con = duckdb.connect()
    con.execute(
        """
        CREATE TABLE attention (
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
    con.execute(
        "INSERT INTO attention VALUES (?,?,?,?,?,?,?)",
        [dt(0, 15), 1, 1, 1.0, 0.0, 0.0, dt(0, 16)],
    )
    con.execute("COPY attention TO ? (FORMAT PARQUET)", [str(attention)])
    con.close()

    write_market_dataset(
        [
            {
                "symbol": "BTCUSDT",
                "interval": "15m",
                "open_time": dt(0),
                "close_time": dt(0, 15) - timedelta(milliseconds=1),
                "decision_time": dt(0, 15),
                "open": 1.0,
                "high": 2.0,
                "low": 0.5,
                "close": 1.5,
                "volume": 10.0,
                "quote_volume": 15.0,
                "trade_count": 2,
                "taker_buy_base_volume": 4.0,
                "taker_buy_quote_volume": 6.0,
            }
        ],
        silver_path=market,
    )
    splits = {
        "train": (dt(0), dt(1)),
        "validation": (dt(1), dt(2)),
        "untouched_test": (dt(2), dt(3)),
    }
    with pytest.raises(ValueError, match="lookahead"):
        build_aligned_panel(
            attention_path=attention,
            market_path=market,
            output_path=aligned,
            splits=splits,
        )


def test_reddit_silver_does_not_infer_btc_entity_from_subreddit(tmp_path):
    raw = {
        "id": "general-crypto-post",
        "author": "alice",
        "created_utc": int(dt(0, 1).timestamp()),
        "retrieved_on": int(dt(0, 2).timestamp()),
        "subreddit": "CryptoCurrency",
        "title": "A general market discussion",
        "selftext": "No asset entity has been resolved yet.",
        "url": "https://example.invalid/post",
    }
    bronze = tmp_path / "bronze.jsonl"
    observations = tmp_path / "observations.parquet"
    write_reddit_dataset(
        [raw],
        bronze_path=bronze,
        silver_path=observations,
        collected_at=dt(1),
        manifest_id="test-manifest",
    )

    (entity_refs_json,) = duckdb.connect().execute(
        "SELECT entity_refs_json FROM read_parquet(?)", [str(observations)]
    ).fetchone()
    assert entity_refs_json == "[]"
