from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

from ninja_labs.adapters.arctic_shift import iter_posts
from ninja_labs.adapters.binance import iter_klines
from ninja_labs.manifest import artifact_record, write_manifest
from ninja_labs.phase1 import (
    build_aligned_panel,
    build_attention_gold,
    validate_splits,
    write_market_dataset,
    write_reddit_dataset,
)
from ninja_labs.util import iso_utc, parse_utc, sha256_json, utc_now


def load_config(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        config = tomllib.load(handle)
    required = {"dataset", "reddit", "market", "attention", "splits"}
    missing = required - set(config)
    if missing:
        raise ValueError(f"missing config sections: {sorted(missing)}")
    return config


def _parse_splits(raw: dict[str, Any]) -> dict[str, tuple[Any, Any]]:
    splits = {
        name: (parse_utc(values["start"]), parse_utc(values["end"]))
        for name, values in raw.items()
    }
    validate_splits(splits)
    return splits


def run_phase1(config_path: Path) -> Path:
    config = load_config(config_path)
    dataset = config["dataset"]
    start = parse_utc(dataset["start"])
    end = parse_utc(dataset["end"])
    if start >= end:
        raise ValueError("dataset.start must precede dataset.end")
    splits = _parse_splits(config["splits"])

    collected_at = utc_now()
    manifest_seed = {
        "dataset_id": dataset["id"],
        "start": iso_utc(start),
        "end": iso_utc(end),
        "collected_at": iso_utc(collected_at),
        "config": config,
    }
    manifest_id = sha256_json(manifest_seed)[:24]
    output_root = Path(dataset.get("output_root", ".ninja-data"))
    run_dir = output_root / dataset["id"] / manifest_id

    bronze_reddit = run_dir / "bronze" / "reddit_posts.jsonl"
    silver_observations = run_dir / "silver" / "observations.parquet"
    silver_market = run_dir / "silver" / "market.parquet"
    gold_attention = run_dir / "gold" / "attention.parquet"
    gold_aligned = run_dir / "gold" / "aligned.parquet"
    manifest_path = run_dir / "manifest.json"

    reddit_cfg = config["reddit"]
    reddit_rows = iter_posts(
        subreddits=list(reddit_cfg["subreddits"]),
        after=start,
        before=end,
        page_limit=int(reddit_cfg.get("page_limit", 100)),
        timeout_seconds=float(reddit_cfg.get("timeout_seconds", 60.0)),
    )
    observation_count = write_reddit_dataset(
        reddit_rows,
        bronze_path=bronze_reddit,
        silver_path=silver_observations,
        collected_at=collected_at,
        manifest_id=manifest_id,
    )

    market_cfg = config["market"]
    market_rows = iter_klines(
        symbol=str(market_cfg["symbol"]),
        interval=str(market_cfg["interval"]),
        after=start,
        before=end,
        timeout_seconds=float(market_cfg.get("timeout_seconds", 60.0)),
    )
    market_count = write_market_dataset(market_rows, silver_path=silver_market)

    attention_count = build_attention_gold(
        observations_path=silver_observations,
        output_path=gold_attention,
        start=start,
        end=end,
        interval=str(config["attention"]["interval"]),
    )
    aligned_count = build_aligned_panel(
        attention_path=gold_attention,
        market_path=silver_market,
        output_path=gold_aligned,
        splits=splits,
    )

    normalized_config = {
        "dataset": {
            **dataset,
            "start": iso_utc(start),
            "end": iso_utc(end),
        },
        "reddit": reddit_cfg,
        "market": market_cfg,
        "attention": config["attention"],
        "splits": {
            name: {"start": iso_utc(window[0]), "end": iso_utc(window[1])}
            for name, window in splits.items()
        },
    }
    artifacts = {
        "bronze_reddit": artifact_record(bronze_reddit, rows=observation_count),
        "silver_observations": artifact_record(
            silver_observations, rows=observation_count
        ),
        "silver_market": artifact_record(silver_market, rows=market_count),
        "gold_attention": artifact_record(gold_attention, rows=attention_count),
        "gold_aligned": artifact_record(gold_aligned, rows=aligned_count),
    }
    sources = [
        {
            "id": "arctic-shift",
            "role": "historical-information",
            "endpoint": "https://arctic-shift.photon-reddit.com/api/posts/search",
            "query": {
                "subreddits": list(reddit_cfg["subreddits"]),
                "after": iso_utc(start),
                "before": iso_utc(end),
                "sort": "asc",
            },
            "causal_clock": "retrieved_on when available; otherwise created_utc",
        },
        {
            "id": "binance-public-market-data",
            "role": "market-baseline",
            "endpoint": "https://data-api.binance.vision/api/v3/klines",
            "query": {
                "symbol": market_cfg["symbol"],
                "interval": market_cfg["interval"],
                "after": iso_utc(start),
                "before": iso_utc(end),
            },
            "causal_clock": "decision_time is immediately after candle close",
        },
    ]
    notes = [
        "Mutable Reddit score/num_comments fields are intentionally excluded from E1 causal features.",
        "Observation.available_at is the only timestamp used to construct attention features.",
        "Event-level observations are preserved so later propagation/Hawkes work does not require reconstructed timestamps.",
        "The untouched_test split is labeled in the aligned panel but Phase 2 optimizers must not use it for adaptive search.",
    ]
    write_manifest(
        manifest_path,
        manifest_id=manifest_id,
        config=normalized_config,
        sources=sources,
        artifacts=artifacts,
        notes=notes,
    )
    return manifest_path
