from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ninja_labs.util import git_commit, sha256_json, utc_now
from ninja_labs.validation.core import (
    benjamini_hochberg,
    effective_sample_size,
    ols_slope,
    pearson_r,
)
from ninja_labs.validation.resampling import block_permutation_test, block_shuffle
from ninja_labs.validation.splits import assign_purged_split
from ninja_labs.validation.synthetic import generate_ar1, generate_lagged_relation, generate_null_pair


def run_validation_selftest(*, seed: int = 1729) -> dict[str, Any]:
    checks: dict[str, dict[str, Any]] = {}

    x, y = generate_lagged_relation(
        800,
        effect=0.85,
        lag=3,
        noise_sigma=0.8,
        seed=seed,
    )
    slope = ols_slope(x, y)
    correlation = pearson_r(x, y)
    permutation = block_permutation_test(
        x,
        y,
        statistic=pearson_r,
        block_size=16,
        n_resamples=199,
        seed=seed + 1,
    )
    recovery_passed = 0.55 <= slope <= 1.15 and correlation > 0.45 and permutation["p_value"] <= 0.05
    checks["synthetic_recovery"] = {
        "passed": recovery_passed,
        "known_effect": 0.85,
        "estimated_slope": slope,
        "correlation": correlation,
        "block_permutation_p": permutation["p_value"],
    }

    null_rejections = 0
    null_trials = 40
    for trial in range(null_trials):
        nx, ny = generate_null_pair(360, phi=0.55, seed=seed + 10_000 + trial * 17)
        null_test = block_permutation_test(
            nx,
            ny,
            statistic=pearson_r,
            block_size=12,
            n_resamples=99,
            seed=seed + 20_000 + trial * 31,
        )
        if null_test["p_value"] <= 0.05:
            null_rejections += 1
    false_positive_rate = null_rejections / null_trials
    checks["null_calibration"] = {
        "passed": false_positive_rate <= 0.15,
        "trials": null_trials,
        "alpha": 0.05,
        "false_positives": null_rejections,
        "false_positive_rate": false_positive_rate,
        "acceptance_ceiling": 0.15,
    }

    shuffled_y = block_shuffle(y, block_size=16, seed=seed + 2)
    shuffled_r = pearson_r(x, shuffled_y)
    checks["negative_control"] = {
        "passed": abs(shuffled_r) < abs(correlation) * 0.5,
        "original_abs_r": abs(correlation),
        "block_shuffled_abs_r": abs(shuffled_r),
    }

    weak_dependence = generate_ar1(1000, phi=0.05, seed=seed + 3)
    strong_dependence = generate_ar1(1000, phi=0.9, seed=seed + 4)
    weak_ess = effective_sample_size(weak_dependence, max_lag=30)
    strong_ess = effective_sample_size(strong_dependence, max_lag=30)
    checks["effective_n"] = {
        "passed": strong_ess < weak_ess and 1 <= strong_ess <= 1000 and weak_ess <= 1000,
        "weak_dependence_effective_n": weak_ess,
        "strong_dependence_effective_n": strong_ess,
    }

    adjusted = benjamini_hochberg([0.001, 0.01, 0.04, 0.20])
    checks["multiple_testing"] = {
        "passed": adjusted == sorted(adjusted) and all(0 <= value <= 1 for value in adjusted),
        "input_p": [0.001, 0.01, 0.04, 0.20],
        "adjusted_q": adjusted,
    }

    from datetime import UTC, datetime, timedelta

    splits = {
        "train": (
            datetime(2025, 1, 1, tzinfo=UTC),
            datetime(2025, 2, 1, tzinfo=UTC),
        ),
        "validation": (
            datetime(2025, 2, 1, tzinfo=UTC),
            datetime(2025, 3, 1, tzinfo=UTC),
        ),
    }
    purged = assign_purged_split(
        decision_time=datetime(2025, 1, 31, 18, tzinfo=UTC),
        label_end_time=datetime(2025, 2, 1, 18, tzinfo=UTC),
        splits=splits,
        embargo=timedelta(hours=24),
    )
    embargoed = assign_purged_split(
        decision_time=datetime(2025, 2, 1, 12, tzinfo=UTC),
        label_end_time=datetime(2025, 2, 1, 18, tzinfo=UTC),
        splits=splits,
        embargo=timedelta(hours=24),
    )
    valid = assign_purged_split(
        decision_time=datetime(2025, 2, 2, 12, tzinfo=UTC),
        label_end_time=datetime(2025, 2, 2, 18, tzinfo=UTC),
        splits=splits,
        embargo=timedelta(hours=24),
    )
    checks["purging_embargo"] = {
        "passed": purged == "purged" and embargoed == "embargoed" and valid == "validation",
        "cross_boundary_sample": purged,
        "boundary_sample": embargoed,
        "valid_sample": valid,
    }

    passed = all(check["passed"] for check in checks.values())
    payload: dict[str, Any] = {
        "schema_version": 1,
        "kind": "ninja-scientific-validation-selftest",
        "seed": seed,
        "created_at": utc_now().isoformat().replace("+00:00", "Z"),
        "code_commit": git_commit(),
        "passed": passed,
        "checks": checks,
    }
    payload["result_sha256"] = sha256_json(payload)
    return payload


def write_validation_selftest(path: Path, *, seed: int = 1729) -> dict[str, Any]:
    payload = run_validation_selftest(seed=seed)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return payload
