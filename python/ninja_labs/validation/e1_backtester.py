from __future__ import annotations

import json
import math
import random
import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import duckdb
import numpy as np

from ninja_labs.e1 import run_e1_train_validation
from ninja_labs.util import git_commit, git_is_dirty, sha256_json, utc_now


def _write_panel(
    root: Path,
    *,
    seed: int,
    signal: bool,
    n_train: int,
    n_validation: int,
    period: int,
    horizon: int,
) -> tuple[Path, Path]:
    root.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    total = n_train + n_validation
    start = datetime(2023, 1, 1, tzinfo=UTC)
    price = 100.0
    high_remaining = 0
    rows: list[tuple[Any, ...]] = []

    for index in range(total):
        phase = 2.0 * math.pi * (index % period) / period
        message_count = max(
            0,
            int(round(7.0 + 2.0 * math.sin(phase) + rng.gauss(0.0, 1.1))),
        )
        attention_event = rng.random() < 0.035
        if attention_event:
            message_count += 26

        volatility_event = attention_event if signal else rng.random() < 0.035
        sigma = 0.010 if high_remaining > 0 else 0.0012
        log_return = 0.0 if index == 0 else rng.gauss(0.0, sigma)
        previous_close = price
        price *= math.exp(log_return)
        span = max(0.0015, abs(log_return) * 0.35 + 0.001)
        high = max(previous_close, price) * (1.0 + span)
        low = min(previous_close, price) * (1.0 - span)
        volume = max(
            1.0,
            120.0 + 18.0 * math.sin(index / 17.0) + rng.gauss(0.0, 8.0),
        )
        unique_authors = (
            max(1, min(message_count, int(round(message_count * 0.72))))
            if message_count
            else 0
        )
        author_hhi = 1.0 / unique_authors if unique_authors else 0.0
        author_entropy = 1.0 if unique_authors > 1 else 0.0
        split = "train" if index < n_train else "validation"
        rows.append(
            (
                start + timedelta(minutes=15 * index),
                previous_close,
                high,
                low,
                price,
                volume,
                message_count,
                unique_authors,
                author_hhi,
                author_entropy,
                split,
            )
        )

        if high_remaining > 0:
            high_remaining -= 1
        if volatility_event:
            high_remaining = max(high_remaining, horizon)

    database = duckdb.connect()
    database.execute(
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
    database.executemany("INSERT INTO panel VALUES (?,?,?,?,?,?,?,?,?,?,?)", rows)
    train_path = root / "train.parquet"
    validation_path = root / "validation.parquet"
    database.execute(
        "COPY (SELECT * FROM panel WHERE split='train' ORDER BY decision_time) "
        "TO ? (FORMAT PARQUET, COMPRESSION ZSTD)",
        [str(train_path)],
    )
    database.execute(
        "COPY (SELECT * FROM panel WHERE split='validation' ORDER BY decision_time) "
        "TO ? (FORMAT PARQUET, COMPRESSION ZSTD)",
        [str(validation_path)],
    )
    database.close()
    return train_path, validation_path


def _write_config(
    path: Path,
    *,
    seed: int,
    period: int,
    cycles: int,
    horizon: int,
    bootstrap_resamples: int,
    minimum_gain: float,
) -> None:
    path.write_text(
        f"""[experiment]
id = \"synthetic-e1-backtester\"
hypothesis = \"N1-synthetic\"
stage = \"train_validation\"
random_seed = {seed}
minimum_relative_loss_improvement = {minimum_gain}

[data]
allowed_splits = [\"train\", \"validation\"]
forbidden_splits = [\"untouched_test\"]

[attention]
seasonal_period = {period}
seasonal_cycles = {cycles}
zero_mad_policy = \"poisson\"

[targets]
horizons_bins = [{horizon}]
jump_sigma = 3.0

[models]
ridge_alpha = 1.0
logistic_c = 1.0
max_iter = 2000

[validation]
bootstrap_block_size = {period}
bootstrap_resamples = {bootstrap_resamples}
fdr_alpha = 0.05
embargo_bins = {horizon}

[feature_groups]
market_only = []
market_plus_seasonal_attention = [\"seasonal_attention_surprise\", \"attention_acceleration\"]
""",
        encoding="utf-8",
    )


def _run_world(
    root: Path,
    *,
    seed: int,
    signal: bool,
    n_train: int,
    n_validation: int,
    period: int,
    cycles: int,
    horizon: int,
    bootstrap_resamples: int,
    minimum_gain: float,
) -> dict[str, Any]:
    train_path, validation_path = _write_panel(
        root,
        seed=seed,
        signal=signal,
        n_train=n_train,
        n_validation=n_validation,
        period=period,
        horizon=horizon,
    )
    manifest_path = root / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "manifest_id": f"synthetic-{'signal' if signal else 'null'}-{seed}",
                "artifacts": {
                    "gold_train": {"path": str(train_path)},
                    "gold_validation": {"path": str(validation_path)},
                    "gold_untouched_test": {
                        "path": str(root / "MUST_NOT_OPEN.parquet")
                    },
                },
            }
        ),
        encoding="utf-8",
    )
    config_path = root / "experiment.toml"
    _write_config(
        config_path,
        seed=seed,
        period=period,
        cycles=cycles,
        horizon=horizon,
        bootstrap_resamples=bootstrap_resamples,
        minimum_gain=minimum_gain,
    )
    output_path = root / "result.json"
    payload = run_e1_train_validation(
        manifest_path=manifest_path,
        config_path=config_path,
        output_path=output_path,
    )
    primary = next(
        record
        for record in payload["comparisons"]
        if record.get("target") == "future_rv"
        and record.get("horizon_bins") == horizon
        and record.get("candidate") == "market_plus_seasonal_attention"
    )
    return {
        "seed": seed,
        "truth": "signal" if signal else "null",
        "status": primary["status"],
        "relative_gain": primary["relative_loss_improvement"],
        "p_value": primary["p_value"],
        "q_value": primary["q_value"],
        "ci95_low": primary["ci95_low"],
        "ci95_high": primary["ci95_high"],
        "effective_n": primary["effective_n"],
        "untouched_test_opened": payload["untouched_test_opened"],
    }


def run_e1_backtester_validation(
    *,
    seed: int = 314159,
    null_worlds: int = 12,
    n_train: int = 5000,
    n_validation: int = 2500,
    period: int = 96,
    cycles: int = 4,
    horizon: int = 16,
    bootstrap_resamples: int = 199,
    minimum_gain: float = 0.005,
    max_null_discovery_fraction: float = 0.10,
) -> dict[str, Any]:
    """Validate the complete E1 train/validation runner on known worlds.

    This is deliberately separate from the attention-estimator Monte Carlo gate.
    It tests the whole statistical path: causal feature construction, target
    construction, common support, model fitting, paired block inference, FDR,
    effect-size gating, and the untouched-test boundary.
    """

    if null_worlds <= 0:
        raise ValueError("null_worlds must be positive")
    if n_train <= period * cycles + 500:
        raise ValueError("n_train is too short for seasonal warmup plus inference")
    if n_validation < 500:
        raise ValueError("n_validation must be at least 500")

    with tempfile.TemporaryDirectory(prefix="ninja-e1-backtester-") as temporary:
        base = Path(temporary)
        signal_result = _run_world(
            base / "signal",
            seed=seed,
            signal=True,
            n_train=n_train,
            n_validation=n_validation,
            period=period,
            cycles=cycles,
            horizon=horizon,
            bootstrap_resamples=bootstrap_resamples,
            minimum_gain=minimum_gain,
        )
        null_results = []
        for offset in range(null_worlds):
            null_results.append(
                _run_world(
                    base / f"null-{offset:03d}",
                    seed=seed + 100_000 + offset,
                    signal=False,
                    n_train=n_train,
                    n_validation=n_validation,
                    period=period,
                    cycles=cycles,
                    horizon=horizon,
                    bootstrap_resamples=bootstrap_resamples,
                    minimum_gain=minimum_gain,
                )
            )

    null_discoveries = sum(
        result["status"] in {"SUPPORTED", "WEAK"} for result in null_results
    )
    null_discovery_fraction = null_discoveries / null_worlds
    null_gains = np.asarray(
        [float(result["relative_gain"]) for result in null_results], dtype=float
    )
    null_p95_gain = float(np.quantile(null_gains, 0.95))
    all_untouched_closed = (
        signal_result["untouched_test_opened"] is False
        and all(result["untouched_test_opened"] is False for result in null_results)
    )

    criteria = {
        "known_signal_is_supported": signal_result["status"] == "SUPPORTED",
        "known_signal_exceeds_minimum_effect": float(signal_result["relative_gain"])
        >= minimum_gain,
        "known_signal_exceeds_null_p95": float(signal_result["relative_gain"])
        > null_p95_gain,
        "null_discovery_fraction_within_limit": null_discovery_fraction
        <= max_null_discovery_fraction,
        "untouched_test_remains_closed": all_untouched_closed,
    }
    passed = all(criteria.values())
    payload: dict[str, Any] = {
        "schema_version": 1,
        "kind": "e1-backtester-end-to-end-validation",
        "created_at": utc_now().isoformat().replace("+00:00", "Z"),
        "code_commit": git_commit(),
        "code_dirty": git_is_dirty(),
        "seed": seed,
        "configuration": {
            "null_worlds": null_worlds,
            "n_train": n_train,
            "n_validation": n_validation,
            "period": period,
            "cycles": cycles,
            "horizon": horizon,
            "bootstrap_resamples": bootstrap_resamples,
            "minimum_gain": minimum_gain,
            "max_null_discovery_fraction": max_null_discovery_fraction,
        },
        "criteria": criteria,
        "metrics": {
            "signal_relative_gain": signal_result["relative_gain"],
            "signal_status": signal_result["status"],
            "signal_p_value": signal_result["p_value"],
            "signal_q_value": signal_result["q_value"],
            "signal_ci95_low": signal_result["ci95_low"],
            "signal_ci95_high": signal_result["ci95_high"],
            "null_discoveries": null_discoveries,
            "null_discovery_fraction": null_discovery_fraction,
            "null_p95_relative_gain": null_p95_gain,
            "untouched_test_opened_anywhere": not all_untouched_closed,
        },
        "signal_world": signal_result,
        "null_worlds": null_results,
        "passed": passed,
        "status": "VALIDATED_FOR_E1" if passed else "BACKTESTER_VALIDATION_FAILED",
        "scientific_boundary": (
            "This validates the complete E1 development backtester on controlled "
            "synthetic worlds. It does not establish N1 or empirical market value."
        ),
    }
    payload["result_sha256"] = sha256_json(payload)
    return payload


def write_e1_backtester_validation(
    path: Path,
    **kwargs: Any,
) -> dict[str, Any]:
    payload = run_e1_backtester_validation(**kwargs)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return payload
