from __future__ import annotations

import json
import math
from datetime import UTC, datetime, timedelta

import duckdb

from ninja_labs.e1 import run_e1_train_validation


def _write_panel(path, *, start, n, split):
    con = duckdb.connect()
    con.execute(
        """
        CREATE TABLE panel (
            decision_time TIMESTAMPTZ,
            open DOUBLE,
            high DOUBLE,
            low DOUBLE,
            close DOUBLE,
            volume DOUBLE,
            message_count BIGINT,
            unique_author_count BIGINT,
            author_hhi DOUBLE,
            author_entropy_normalized DOUBLE,
            split VARCHAR
        )
        """
    )
    rows = []
    for index in range(n):
        global_index = int((start - datetime(2023, 1, 1, tzinfo=UTC)).total_seconds() / 900) + index
        close = 100.0 + 0.015 * global_index + 1.8 * math.sin(global_index / 11.0)
        open_price = close * (1.0 - 0.0005 * math.sin(global_index / 3.0))
        volume = 120.0 + 25.0 * (1.0 + math.sin(global_index / 13.0))
        messages = 4 + (global_index % 9)
        unique = max(1, min(messages, 2 + (global_index % 6)))
        hhi = 1.0 / unique
        entropy = 1.0 if unique > 1 else 0.0
        rows.append(
            (
                start + timedelta(minutes=15 * index),
                open_price,
                close * 1.003,
                close * 0.997,
                close,
                volume,
                messages,
                unique,
                hhi,
                entropy,
                split,
            )
        )
    con.executemany("INSERT INTO panel VALUES (?,?,?,?,?,?,?,?,?,?,?)", rows)
    con.execute("COPY panel TO ? (FORMAT PARQUET)", [str(path)])
    con.close()


def test_e1_train_validation_does_not_require_or_open_untouched_test(tmp_path):
    train = tmp_path / "train.parquet"
    validation = tmp_path / "validation.parquet"
    missing_test = tmp_path / "THIS_FILE_MUST_NOT_BE_OPENED.parquet"
    start = datetime(2023, 1, 1, tzinfo=UTC)
    _write_panel(train, start=start, n=900, split="train")
    _write_panel(
        validation,
        start=start + timedelta(minutes=15 * 900),
        n=420,
        split="validation",
    )

    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "manifest_id": "fixture-manifest",
                "artifacts": {
                    "gold_train": {"path": str(train)},
                    "gold_validation": {"path": str(validation)},
                    "gold_untouched_test": {"path": str(missing_test)},
                },
            }
        ),
        encoding="utf-8",
    )

    config = tmp_path / "e1.toml"
    config.write_text(
        """
[experiment]
id = "fixture-e1"
hypothesis = "N1"
stage = "train_validation"
random_seed = 1729
minimum_relative_loss_improvement = 0.001

[data]
allowed_splits = ["train", "validation"]
forbidden_splits = ["untouched_test"]

[attention]
seasonal_period = 24
seasonal_cycles = 3
zero_mad_policy = "poisson"

[targets]
horizons_bins = [1, 4]
jump_sigma = 1.0

[models]
ridge_alpha = 1.0
logistic_c = 1.0
max_iter = 1000

[validation]
bootstrap_block_size = 24
bootstrap_resamples = 49
fdr_alpha = 0.05
embargo_bins = 24

[feature_groups]
market_only = []
market_plus_raw_count = ["message_count"]
market_plus_seasonal_attention = ["seasonal_attention_surprise", "attention_acceleration"]
market_plus_attention_structure = ["message_count", "unique_author_count", "author_breadth", "author_hhi", "author_entropy_normalized"]
market_plus_all_validated = ["message_count", "seasonal_attention_surprise", "attention_acceleration", "unique_author_count", "author_breadth", "author_hhi", "author_entropy_normalized"]
""".strip()
        + "\n",
        encoding="utf-8",
    )

    output = tmp_path / "result.json"
    payload = run_e1_train_validation(
        manifest_path=manifest,
        config_path=config,
        output_path=output,
    )
    assert output.is_file()
    assert payload["untouched_test_opened"] is False
    assert set(payload["input_artifacts"]) == {"train", "validation"}
    assert not missing_test.exists()
    assert payload["multiple_testing"]["family_size"] > 0
    assert payload["comparisons"]
