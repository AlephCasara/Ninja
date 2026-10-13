from __future__ import annotations

import json
import math
import random
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from ninja_labs.e1 import (
    MARKET_FEATURES,
    _artifact_path,
    _build_features,
    _build_target,
    _load_split,
    _matrix,
    _read_manifest,
    _read_toml,
    _valid_number,
    _validate_grid,
)
from ninja_labs.preregistration import verify_e1_preregistration_seal
from ninja_labs.util import git_commit, sha256_file, sha256_json, utc_now


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _block_permutation_indices(length: int, block_size: int, seed: int) -> np.ndarray:
    if length <= 0 or block_size <= 0:
        raise ValueError("length and block_size must be positive")
    blocks = [list(range(start, min(start + block_size, length))) for start in range(0, length, block_size)]
    random.Random(seed).shuffle(blocks)
    return np.asarray([index for block in blocks for index in block], dtype=int)


def _ridge(alpha: float) -> Pipeline:
    return Pipeline(
        [
            ("scale", StandardScaler()),
            ("model", Ridge(alpha=alpha)),
        ]
    )


def _relative_gain(baseline_loss: np.ndarray, candidate_loss: np.ndarray) -> float:
    baseline = float(np.mean(baseline_loss))
    candidate = float(np.mean(candidate_loss))
    return (baseline - candidate) / baseline if baseline > 0 else 0.0


def run_e1_robustness(
    *,
    manifest_path: Path,
    config_path: Path,
    preregistration_seal_path: Path,
    train_validation_result_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    """Stress the preregistered E1 primary result without opening 2025."""

    seal = verify_e1_preregistration_seal(
        seal_path=preregistration_seal_path,
        manifest_path=manifest_path,
        config_path=config_path,
    )
    result = _read_json(train_validation_result_path)
    if result.get("kind") != "ninja-e1-train-validation":
        raise ValueError("unexpected train/validation result kind")
    if result.get("untouched_test_opened") is not False:
        raise ValueError("train/validation result reports untouched-test access")
    if result.get("dataset_manifest_sha256") != sha256_file(manifest_path):
        raise ValueError("train/validation result used a different dataset manifest")
    if result.get("experiment_config_sha256") != sha256_file(config_path):
        raise ValueError("train/validation result used a different E1 config")
    if result.get("preregistration", {}).get("seal_sha256") != seal["seal_sha256"]:
        raise ValueError("train/validation result is not bound to this preregistration seal")

    primary = result.get("primary_confirmatory_result")
    if not isinstance(primary, dict):
        raise ValueError("train/validation result lacks primary_confirmatory_result")

    cfg = _read_toml(config_path)
    confirmatory = cfg["confirmatory"]
    target = str(confirmatory["primary_target"])
    horizon = int(confirmatory["primary_horizon_bins"])
    candidate_group = str(confirmatory["primary_candidate"])
    if target != "future_rv":
        raise ValueError("E1 v1 robustness implementation expects future_rv primary target")
    if primary.get("target") != target or int(primary.get("horizon_bins", -1)) != horizon:
        raise ValueError("train/validation primary does not match preregistered target/horizon")
    if primary.get("candidate") != candidate_group:
        raise ValueError("train/validation primary does not match preregistered candidate")

    manifest = _read_manifest(manifest_path)
    train_path = _artifact_path(manifest_path, manifest["artifacts"]["gold_train"])
    validation_path = _artifact_path(manifest_path, manifest["artifacts"]["gold_validation"])
    train_rows = _load_split(train_path, "train")
    validation_rows = _load_split(validation_path, "validation")
    rows = train_rows + validation_rows
    _validate_grid(rows)
    _build_features(rows, cfg)
    train_end = len(train_rows)

    candidate_extras = list(cfg["feature_groups"][candidate_group])
    baseline_features = list(MARKET_FEATURES)
    candidate_features = baseline_features + candidate_extras
    required = candidate_features
    target_values = [
        _build_target(
            rows,
            index,
            horizon=horizon,
            target=target,
            jump_sigma=float(cfg["targets"]["jump_sigma"]),
        )
        for index in range(len(rows))
    ]
    train_indices = [
        index
        for index in range(train_end)
        if target_values[index] is not None
        and all(_valid_number(rows[index].get(feature)) for feature in required)
    ]
    embargo = int(cfg["validation"]["embargo_bins"])
    validation_indices = [
        index
        for index in range(train_end + embargo, len(rows))
        if target_values[index] is not None
        and all(_valid_number(rows[index].get(feature)) for feature in required)
    ]
    if len(train_indices) < 500 or len(validation_indices) < 250:
        raise ValueError("insufficient support for E1 robustness gate")

    alpha = float(cfg["models"]["ridge_alpha"])
    y_train = np.asarray([target_values[index] for index in train_indices], dtype=float)
    y_val = np.asarray([target_values[index] for index in validation_indices], dtype=float)
    x_base_train = _matrix(rows, train_indices, baseline_features)
    x_base_val = _matrix(rows, validation_indices, baseline_features)
    x_candidate_train = _matrix(rows, train_indices, candidate_features)
    x_candidate_val = _matrix(rows, validation_indices, candidate_features)

    baseline_model = _ridge(alpha)
    candidate_model = _ridge(alpha)
    baseline_model.fit(x_base_train, y_train)
    candidate_model.fit(x_candidate_train, y_train)
    baseline_pred = baseline_model.predict(x_base_val)
    candidate_pred = candidate_model.predict(x_candidate_val)
    baseline_loss = (y_val - baseline_pred) ** 2
    candidate_loss = (y_val - candidate_pred) ** 2
    observed_gain = _relative_gain(baseline_loss, candidate_loss)

    recorded_gain = primary.get("relative_loss_improvement")
    if recorded_gain is not None and abs(float(recorded_gain) - observed_gain) > 1e-10:
        raise ValueError("robustness refit does not reproduce the sealed primary validation gain")

    robustness_cfg = cfg["robustness"]
    checks: dict[str, dict[str, Any]] = {}

    # Chronological validation blocks: assess stability rather than a single aggregate.
    block_count = int(robustness_cfg["validation_time_blocks"])
    positions = np.array_split(np.arange(len(validation_indices)), block_count)
    block_gains: list[float] = []
    for position in positions:
        if len(position) == 0:
            raise ValueError("validation block is empty")
        block_gains.append(_relative_gain(baseline_loss[position], candidate_loss[position]))
    positive_blocks = sum(gain > 0 for gain in block_gains)
    minimum_positive = int(robustness_cfg["min_positive_validation_blocks"])
    checks["validation_time_blocks"] = {
        "passed": positive_blocks >= minimum_positive,
        "gains": block_gains,
        "positive_blocks": positive_blocks,
        "minimum_positive": minimum_positive,
    }

    best_block = int(np.argmax(np.asarray(block_gains)))
    retained = np.concatenate([position for index, position in enumerate(positions) if index != best_block])
    drop_best_gain = _relative_gain(baseline_loss[retained], candidate_loss[retained])
    require_drop_best = bool(robustness_cfg["require_drop_best_block_positive"])
    checks["drop_best_validation_block"] = {
        "passed": (drop_best_gain > 0) if require_drop_best else True,
        "dropped_block": best_block,
        "relative_gain_after_drop": drop_best_gain,
    }

    # Leave-one-training-year-out: the result should not require one historical year.
    leave_years = [int(value) for value in robustness_cfg["leave_one_train_year_out"]]
    leave_year_records: list[dict[str, Any]] = []
    for year in leave_years:
        subset = [index for index in train_indices if rows[index]["decision_time"].year != year]
        if len(subset) < 500:
            leave_year_records.append({"year": year, "status": "INVALID", "n_train": len(subset)})
            continue
        y_subset = np.asarray([target_values[index] for index in subset], dtype=float)
        base = _ridge(alpha)
        cand = _ridge(alpha)
        base.fit(_matrix(rows, subset, baseline_features), y_subset)
        cand.fit(_matrix(rows, subset, candidate_features), y_subset)
        base_loss = (y_val - base.predict(x_base_val)) ** 2
        cand_loss = (y_val - cand.predict(x_candidate_val)) ** 2
        gain = _relative_gain(base_loss, cand_loss)
        leave_year_records.append({"year": year, "status": "VALID", "n_train": len(subset), "relative_gain": gain})
    valid_year_gains = [float(item["relative_gain"]) for item in leave_year_records if item["status"] == "VALID"]
    positive_years = sum(gain > 0 for gain in valid_year_gains)
    min_positive_years = int(robustness_cfg["min_positive_leave_one_year_runs"])
    checks["leave_one_train_year_out"] = {
        "passed": len(valid_year_gains) == len(leave_years) and positive_years >= min_positive_years,
        "runs": leave_year_records,
        "positive_runs": positive_years,
        "minimum_positive": min_positive_years,
    }

    # Negative control: destroy broad temporal alignment of attention extras while
    # preserving market features and within-block local structure.
    negative_runs = int(robustness_cfg["negative_control_runs"])
    negative_block = int(robustness_cfg["negative_control_block_size"])
    seed = int(cfg["experiment"]["random_seed"])
    extra_start = len(baseline_features)
    negative_gains: list[float] = []
    for run in range(negative_runs):
        train_perm = _block_permutation_indices(len(train_indices), negative_block, seed + run * 1009 + 11)
        val_perm = _block_permutation_indices(len(validation_indices), negative_block, seed + run * 1009 + 29)
        shuffled_train = x_candidate_train.copy()
        shuffled_val = x_candidate_val.copy()
        shuffled_train[:, extra_start:] = x_candidate_train[train_perm, extra_start:]
        shuffled_val[:, extra_start:] = x_candidate_val[val_perm, extra_start:]
        model = _ridge(alpha)
        model.fit(shuffled_train, y_train)
        shuffled_loss = (y_val - model.predict(shuffled_val)) ** 2
        negative_gains.append(_relative_gain(baseline_loss, shuffled_loss))

    minimum_gain = float(confirmatory["minimum_relative_loss_improvement"])
    negative_success_fraction = sum(gain >= minimum_gain for gain in negative_gains) / len(negative_gains)
    negative_p95 = float(np.quantile(np.asarray(negative_gains), 0.95))
    max_success = float(robustness_cfg["max_negative_control_success_fraction"])
    require_above_p95 = bool(robustness_cfg["require_observed_gain_above_negative_control_p95"])
    checks["negative_control"] = {
        "passed": (
            negative_success_fraction <= max_success
            and (observed_gain > negative_p95 if require_above_p95 else True)
        ),
        "runs": negative_runs,
        "minimum_meaningful_gain": minimum_gain,
        "success_fraction": negative_success_fraction,
        "maximum_success_fraction": max_success,
        "p95_relative_gain": negative_p95,
        "median_relative_gain": float(np.median(np.asarray(negative_gains))),
        "observed_relative_gain": observed_gain,
    }

    primary_supported = primary.get("status") == "SUPPORTED"
    checks["primary_validation_eligibility"] = {
        "passed": primary_supported,
        "primary_status": primary.get("status"),
        "rule": "2025 remains sealed unless the preregistered primary comparison is SUPPORTED on train/validation",
    }

    passed = all(check["passed"] for check in checks.values())
    payload: dict[str, Any] = {
        "schema_version": 1,
        "kind": "ninja-e1-robustness",
        "status": "PASSED" if passed else "FAILED",
        "passed": passed,
        "created_at": utc_now().isoformat().replace("+00:00", "Z"),
        "code_commit": git_commit(),
        "experiment_id": cfg["experiment"]["id"],
        "dataset_manifest_sha256": sha256_file(manifest_path),
        "experiment_config_sha256": sha256_file(config_path),
        "preregistration_seal_sha256": seal["seal_sha256"],
        "train_validation_result_sha256": sha256_file(train_validation_result_path),
        "train_validation_internal_result_sha256": result.get("result_sha256"),
        "untouched_test_opened": False,
        "primary": {
            "target": target,
            "horizon_bins": horizon,
            "candidate": candidate_group,
            "validation_status": primary.get("status"),
            "reproduced_relative_gain": observed_gain,
        },
        "checks": checks,
        "scientific_boundary": (
            "Robustness uses train+validation only. Failure preserves the untouched test for a new preregistered generation rather than granting the current hypothesis another chance."
        ),
    }
    payload["result_sha256"] = sha256_json(payload)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    return payload
