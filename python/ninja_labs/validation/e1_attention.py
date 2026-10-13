from __future__ import annotations

import json
import math
import random
import statistics
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from ninja_labs.attention.estimators import (
    author_structure,
    attention_acceleration,
    estimate_nb_moments,
    negative_binomial_residual,
    robust_attention_surprise,
    seasonal_robust_attention_surprise,
)
from ninja_labs.util import git_commit, sha256_json, utc_now
from ninja_labs.validation.core import pearson_r


def _poisson(lam: float, rng: random.Random) -> int:
    if lam < 0:
        raise ValueError("lam must be non-negative")
    if lam == 0:
        return 0
    if lam > 30:
        raise ValueError("synthetic Poisson helper supports lam <= 30")
    threshold = math.exp(-lam)
    product = 1.0
    count = 0
    while product > threshold:
        count += 1
        product *= rng.random()
    return count - 1


def generate_nb_counts(n: int, *, mu: float, phi: float, seed: int) -> list[int]:
    """Generate NB counts through the Gamma-Poisson mixture."""

    if n <= 0 or mu <= 0 or phi <= 0:
        raise ValueError("n, mu and phi must be positive")
    rng = random.Random(seed)
    scale = mu / phi
    result: list[int] = []
    for _ in range(n):
        lam = rng.gammavariate(phi, scale)
        result.append(_poisson(lam, rng))
    return result


def generate_seasonal_counts(
    n: int,
    *,
    base: float,
    amplitude: float,
    period: int,
    seed: int,
    burst_indices: Sequence[int] = (),
    burst_size: int = 20,
) -> list[int]:
    if n <= 0 or base <= 0 or period <= 1:
        raise ValueError("invalid seasonal-count configuration")
    rng = random.Random(seed)
    bursts = set(int(index) for index in burst_indices)
    result: list[int] = []
    for index in range(n):
        lam = base + amplitude * (1.0 + math.sin(2.0 * math.pi * index / period)) / 2.0
        value = _poisson(lam, rng)
        if index in bursts:
            value += burst_size
        result.append(value)
    return result


def _finite(values: Sequence[float | None]) -> list[float]:
    return [float(value) for value in values if value is not None and math.isfinite(value)]


def _mean(values: Sequence[float]) -> float:
    return sum(values) / len(values)


def run_e1_estimator_validation(*, seed: int = 20261013) -> dict[str, Any]:
    checks: dict[str, dict[str, Any]] = {}

    burst_indices = (240, 480, 720)
    counts = generate_seasonal_counts(
        900,
        base=5.0,
        amplitude=0.0,
        period=96,
        seed=seed,
        burst_indices=burst_indices,
        burst_size=24,
    )
    az = robust_attention_surprise(counts, lookback=96, zero_mad_policy="poisson")
    ordinary = [
        float(value)
        for index, value in enumerate(az)
        if value is not None and index not in burst_indices
    ]
    bursts = [float(az[index]) for index in burst_indices if az[index] is not None]
    ordinary_center = statistics.median(ordinary)
    ordinary_abs_95 = sorted(abs(value) for value in ordinary)[int(0.95 * (len(ordinary) - 1))]
    min_burst = min(bursts)
    checks["robust_attention_surprise"] = {
        "passed": abs(ordinary_center) < 0.5 and min_burst > max(4.0, ordinary_abs_95 * 1.5),
        "lookback": 96,
        "ordinary_median": ordinary_center,
        "ordinary_abs_p95": ordinary_abs_95,
        "burst_scores": bursts,
        "zero_mad_policy": "poisson",
    }

    zero_world = [0.0] * 100 + [8.0]
    zero_az = robust_attention_surprise(zero_world, lookback=96, zero_mad_policy="poisson")
    checks["zero_mad_policy"] = {
        "passed": zero_az[-1] == 8.0,
        "first_post_zero_score": zero_az[-1],
        "policy": "poisson",
    }

    true_mu = 6.0
    true_phi = 8.0
    nb_counts = generate_nb_counts(12_000, mu=true_mu, phi=true_phi, seed=seed + 1)
    mu_hat, phi_hat = estimate_nb_moments(nb_counts)
    true_residuals = [
        negative_binomial_residual(value, mu=true_mu, phi=true_phi) for value in nb_counts
    ]
    residual_mean = _mean(true_residuals)
    residual_variance = statistics.variance(true_residuals)
    checks["negative_binomial"] = {
        "passed": (
            abs(mu_hat - true_mu) / true_mu < 0.05
            and abs(phi_hat - true_phi) / true_phi < 0.25
            and abs(residual_mean) < 0.08
            and 0.85 <= residual_variance <= 1.15
        ),
        "n": len(nb_counts),
        "true_mu": true_mu,
        "estimated_mu": mu_hat,
        "true_phi": true_phi,
        "estimated_phi": phi_hat,
        "residual_mean": residual_mean,
        "residual_variance": residual_variance,
    }

    constant = attention_acceleration([5.0] * 10)
    ramp = attention_acceleration([float(index) for index in range(10)])
    impulse = attention_acceleration([0.0, 0.0, 0.0, 10.0, 0.0, 0.0])
    checks["attention_acceleration"] = {
        "passed": (
            all(value == 0.0 for value in constant[2:])
            and all(value == 0.0 for value in ramp[2:])
            and impulse[3] == 10.0
            and impulse[4] == -20.0
            and impulse[5] == 10.0
        ),
        "impulse_output": impulse,
    }

    concentrated = author_structure(["a"] * 100)
    diffuse = author_structure([f"u{index}" for index in range(100)])
    balanced = author_structure([f"u{index % 10}" for index in range(100)])
    relabeled = author_structure([f"x{index % 10}" for index in range(100)])
    checks["author_structure"] = {
        "passed": (
            concentrated["hhi"] == 1.0
            and concentrated["entropy_normalized"] == 0.0
            and diffuse["hhi"] < balanced["hhi"] < concentrated["hhi"]
            and abs(float(diffuse["entropy_normalized"]) - 1.0) < 1e-12
            and abs(float(balanced["hhi"]) - float(relabeled["hhi"])) < 1e-12
            and abs(float(balanced["entropy_normalized"]) - float(relabeled["entropy_normalized"])) < 1e-12
        ),
        "concentrated": concentrated,
        "balanced": balanced,
        "diffuse": diffuse,
    }

    # This check intentionally demonstrates a failure mode of the simple rolling
    # AZ, then requires the seasonal estimator to remove that nuisance.
    period = 96
    cycles = 14
    seasonal = generate_seasonal_counts(
        4_000,
        base=4.0,
        amplitude=8.0,
        period=period,
        seed=seed + 2,
    )
    rolling_az = robust_attention_surprise(seasonal, lookback=period, zero_mad_policy="poisson")
    rolling_values = _finite(rolling_az)
    rolling_phase = [
        math.sin(2.0 * math.pi * index / period)
        for index in range(period, len(seasonal))
    ]
    rolling_r = pearson_r(rolling_values, rolling_phase)

    seasonal_az = seasonal_robust_attention_surprise(
        seasonal,
        period=period,
        cycles=cycles,
        zero_mad_policy="poisson",
    )
    seasonal_values = _finite(seasonal_az)
    seasonal_phase = [
        math.sin(2.0 * math.pi * index / period)
        for index in range(period * cycles, len(seasonal))
    ]
    seasonal_r = pearson_r(seasonal_values, seasonal_phase)
    checks["seasonality_control"] = {
        "passed": abs(rolling_r) > 0.4 and abs(seasonal_r) < 0.15,
        "period": period,
        "cycles": cycles,
        "rolling_az_phase_correlation": rolling_r,
        "seasonal_az_phase_correlation": seasonal_r,
        "finding": "simple rolling AZ retains strong periodic nuisance and is baseline-only",
    }

    passed = all(check["passed"] for check in checks.values())
    status = "VALIDATED_FOR_E1" if passed else "REJECTED_ESTIMATOR_SUITE"
    payload: dict[str, Any] = {
        "schema_version": 1,
        "kind": "e1-attention-estimator-validation",
        "seed": seed,
        "created_at": utc_now().isoformat().replace("+00:00", "Z"),
        "code_commit": git_commit(),
        "passed": passed,
        "status": status,
        "checks": checks,
        "scientific_boundary": (
            "This validates estimator mechanics on controlled worlds only; it does not validate N1 or market usefulness."
        ),
    }
    payload["result_sha256"] = sha256_json(payload)
    return payload


def write_e1_estimator_validation(path: Path, *, seed: int = 20261013) -> dict[str, Any]:
    payload = run_e1_estimator_validation(seed=seed)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return payload
