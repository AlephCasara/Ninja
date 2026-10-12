from __future__ import annotations

from datetime import UTC, datetime, timedelta

from ninja_labs.coverage import build_coverage_report
from ninja_labs.phase1 import (
    build_aligned_panel,
    build_attention_gold,
    write_market_dataset,
    write_reddit_dataset,
)


def dt(hour: int, minute: int = 0) -> datetime:
    return datetime(2025, 1, 1, hour, minute, tzinfo=UTC)


def test_coverage_report_records_causal_and_market_health(tmp_path):
    observations = tmp_path / "observations.parquet"
    market = tmp_path / "market.parquet"
    attention = tmp_path / "attention.parquet"
    aligned = tmp_path / "aligned.parquet"
    coverage = tmp_path / "coverage.json"

    write_reddit_dataset(
        [
            {
                "id": "a",
                "author": "alice",
                "created_utc": int(dt(0, 1).timestamp()),
                "retrieved_on": int(dt(0, 2).timestamp()),
                "subreddit": "Bitcoin",
                "title": "BTC",
                "selftext": "",
                "url": "https://example.invalid/a",
            }
        ],
        bronze_path=tmp_path / "bronze.jsonl",
        silver_path=observations,
        collected_at=dt(1),
        manifest_id="test",
    )
    rows = []
    for index in range(4):
        open_time = dt(0) + timedelta(minutes=15 * index)
        close_time = open_time + timedelta(minutes=15) - timedelta(milliseconds=1)
        rows.append(
            {
                "symbol": "BTCUSDT",
                "interval": "15m",
                "open_time": open_time,
                "close_time": close_time,
                "decision_time": close_time + timedelta(milliseconds=1),
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
        )
    write_market_dataset(rows, silver_path=market)
    build_attention_gold(
        observations_path=observations,
        output_path=attention,
        start=dt(0),
        end=dt(1),
        interval="15m",
    )
    splits = {
        "train": (dt(0), dt(0, 30)),
        "validation": (dt(0, 30), dt(0, 45)),
        "untouched_test": (dt(0, 45), dt(1)),
    }
    build_aligned_panel(
        attention_path=attention,
        market_path=market,
        output_path=aligned,
        splits=splits,
    )

    report = build_coverage_report(
        observations_path=observations,
        market_path=market,
        attention_path=attention,
        aligned_path=aligned,
        market_interval="15m",
        output_path=coverage,
    )
    assert report["observations"]["rows"] == 1
    assert report["observations"]["archive_capture_rows"] == 1
    assert report["market"]["gap_count"] == 0
    assert report["aligned"]["future_window_rows"] == 0
    assert report["aligned"]["future_observation_rows"] == 0
    assert report["aligned"]["rows_by_split"] == {
        "train": 2,
        "untouched_test": 1,
        "validation": 1,
    }
