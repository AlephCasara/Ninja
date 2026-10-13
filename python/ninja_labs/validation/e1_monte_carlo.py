from __future__ import annotations

import json
import math
import statistics
from pathlib import Path
from typing import Any

import numpy as np

from ninja_labs.attention.estimators import (
    robust_attention_surprise,
    seasonal_robust_attention_surprise,
)
from ninja_labs.util import git_commit, sha256_json, utc_now
from ninja_labs.validation.core import pearson_r


def _synthetic_world(
    *,
    seed: int,
    length: int,
    period: int,
    cycles: int,
    bursts: int,
) -> tuple[np.ndarray, set[int], float, float]:
    rng = np.random.default_rng(seed)
    index = np.arange(length)
    daily_phase = float(rng.uniform(-math.pi, math.pi))
    weekly_phase = float(rng.uniform(-math.pi, math.pi))
    base = float(rng.uniform(3.0, 8.0))
    daily_amplitude = float(rng.uniform(2.0, 8.0))
    weekly_amplitude = float(rng.uniform(0.0, 5.0))
    mean = (
        base
        + daily_amplitude
        * (1.0 + np.sin(2.0 * math.pi * index / 96.0 + daily_phase))
        / 2.0
        + weekly_amplitude
        * (1.0 + np.sin(2.0 * math.pi * index / period + weekly_phase))
        / 2.0
    )
    counts = rng.poisson(mean).astype(float)
    warmup = period * cycles
    candidates = np.arange(warmup + 50, length - 50)
    if len(candidates) < bursts:
        raise ValueError("synthetic world is too short for requested bursts")
    burst_indices = rng.choice(candidates, size=bursts, replace=False)
    burst_sizes = rng.integers(18, 36, size=bursts)
    counts[burst_indices] += burst_sizes
    return counts, set(int(value) for value in burst_indices), daily_phase, weekly_phase


def _quantile(values: list[float], q: float) -> float:
    return float(np.quantile(np.asarray(values, dtype=float), q))


def run_e1_monte_carlo_validation(
    *,
    seed: int = 20261013,
    worlds: int = 64,
    length: int = 8000,
    period: int = 672,
    cycles: int = 8,
    bursts_per_world: int = 8,
    score_threshold: float = 4.0,
) -> dict[str, Any]:
    """Stress the exact E1 seasonal estimator across many randomized worlds."""

    if worlds < 16:
        raise ValueError("worlds must be >= 16")
    if period != 672 or cycles != 8:
        raise ValueError("E1 v1 Monte Carlo gate must test period=672, cycles=8")
    warmup = period * cycles
    if length <= warmup + 200:
        raise ValueError("length leaves too little post-warmup evaluation data")

    world_records: list[dict[str, float | int]] = []
    total_bursts = 0
    detected_bursts = 0
    total_null_bins = 0
    false_positives = 0
    rolling_daily_abs: list[float] = []
    seasonal_daily_abs: list[float] = []
    seasonal_weekly_abs: list[float] = []

    for world in range(worlds):
        world_seed = seed + world * 1009
        counts, burst_indices, daily_phase, weekly_phase = _synthetic_world(
            seed=world_seed,
            length=length,
            period=period,
            cycles=cycles,
            bursts=bursts_per_world,
        )
        rolling = robust_attention_surprise(
            counts.tolist(), lookback=96, zero_mad_policy="poisson"
        )
        seasonal = seasonal_robust_attention_surprise(
            counts.tolist(),
            period=period,
            cycles=cycles,
            zero_mad_policy="poisson",
        )

        indices = np.arange(warmup, length)
        rolling_values = [float(rolling[index]) for index in indices]
        seasonal_values = [float(seasonal[index]) for index in indices]
        daily_phase_values = np.sin(
            2.0 * math.pi * indices / 96.0 + daily_phase
        ).tolist()
        weekly_phase_values = np.sin(
            2.0 * math.pi * indices / period + weekly_phase
        ).tolist()

        rolling_daily = abs(pearson_r(rolling_values, daily_phase_values))
        seasonal_daily = abs(pearson_r(seasonal_values, daily_phase_values))
        seasonal_weekly = abs(pearson_r(seasonal_values, weekly_phase_values))
        rolling_daily_abs.append(rolling_daily)
        seasonal_daily_abs.append(seasonal_daily)
        seasonal_weekly_abs.append(seasonal_weekly)

        burst_scores = [float(seasonal[index]) for index in burst_indices]
        detected = sum(score > score_threshold for score in burst_scores)
        total_bursts += len(burst_scores)
        detected_bursts += detected

        null_scores = [
            abs(float(seasonal[index]))
            for index in range(warmup, length)
            if index not in burst_indices
        ]
        fp = sum(score > score_threshold for score in null_scores)
        total_null_bins += len(null_scores)
        false_positives += fp
        world_records.append(
            {
                "world": world,
                "seed": world_seed,
                "burst_recall": detected / len(burst_scores),
                "false_positive_rate": fp / len(null_scores),
                "rolling_daily_abs_r": rolling_daily,
                "seasonal_daily_abs_r": seasonal_daily,
                "seasonal_weekly_abs_r": seasonal_weekly,
            }
        )

    aggregate_recall = detected_bursts / total_bursts
    aggregate_fpr = false_positives / total_null_bins
    metrics = {
        "worlds": worlds,
        "evaluated_bins": total_null_bins + total_bursts,
        "total_bursts": total_bursts,
        "burst_recall": aggregate_recall,
        "false_positive_rate": aggregate_fpr,
        "median_rolling_daily_abs_r": statistics.median(rolling_daily_abs),
        "p10_rolling_daily_abs_r": _quantile(rolling_daily_abs, 0.10),
        "median_seasonal_daily_abs_r": statistics.median(seasonal_daily_abs),
        "p95_seasonal_daily_abs_r": _quantile(seasonal_daily_abs, 0.95),
        "median_seasonal_weekly_abs_r": statistics.median(seasonal_weekly_abs),
        "p95_seasonal_weekly_abs_r": _quantile(seasonal_weekly_abs, 0.95),
        "p05_world_burst_recall": _quantile(
            [float(record["burst_recall"]) for record in world_records], 0.05
        ),
        "p95_world_false_positive_rate": _quantile(
            [float(record["false_positive_rate"]) for record in world_records], 0.95
        ),
    }

    criteria = {
        "aggregate_burst_recall_at_least_0_95": aggregate_recall >= 0.95,
        "aggregate_false_positive_rate_at_most_0_06": aggregate_fpr <= 0.06,
        "p95_daily_nuisance_abs_r_at_most_0_06": metrics[
            "p95_seasonal_daily_abs_r"
        ]
        <= 0.06,
        "p95_weekly_nuisance_abs_r_at_most_0_06": metrics[
            "p95_seasonal_weekly_abs_r"
        ]
        <= 0.06,
        "rolling_baseline_retains_nuisance": metrics["median_rolling_daily_abs_r"]
        >= 0.20,
        "seasonal_estimator_improves_nuisance": metrics[
            "median_seasonal_daily_abs_r"
        ]
        < metrics["median_rolling_daily_abs_r"] * 0.25,
    }
    passed = all(criteria.values())
    payload: dict[str, Any] = {
        "schema_version": 1,
        "kind": "e1-attention-monte-carlo-validation",
        "status": "VALIDATED_FOR_E1" if passed else "FAILED_MONTE_CARLO_GATE",
        "created_at": utc_now().isoformat().replace("+00:00", "Z"),
        "code_commit": git_commit(),
        "seed": seed,
        "configuration": {
            "period": period,
            "cycles": cycles,
            "worlds": worlds,
            "length": length,
            "bursts_per_world": bursts_per_world,
            "score_threshold": score_threshold,
        },
        "metrics": metrics,
        "criteria": criteria,
        "passed": passed,
        "scientific_boundary": (
            "Monte Carlo estimator validation only. It tests measurement behavior across randomized synthetic worlds; it does not establish N1 or market predictive value."
        ),
    }
    payload["result_sha256"] = sha256_json(payload)
    return payload


def write_e1_monte_carlo_validation(
    path: Path, *, seed: int = 20261013, worlds: int = 64
) -> dict[str, Any]:
    payload = run_e1_monte_carlo_validation(seed=seed, worlds=worlds)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return payload
