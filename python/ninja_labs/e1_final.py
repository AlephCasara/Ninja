from __future__ import annotations

import json
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
    _paired_block_inference,
    _read_manifest,
    _read_toml,
    _valid_number,
    _validate_grid,
)
from ninja_labs.preregistration import verify_e1_preregistration_seal
from ninja_labs.util import git_commit, sha256_file, sha256_json, utc_now


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _verify_internal_hash(payload: dict[str, Any], field: str = "result_sha256") -> None:
    stored = payload.get(field)
    if not isinstance(stored, str):
        raise ValueError(f"artifact lacks {field}")
    copy = dict(payload)
    copy.pop(field, None)
    if sha256_json(copy) != stored:
        raise ValueError(f"artifact {field} mismatch")


def _ridge(alpha: float) -> Pipeline:
    return Pipeline([("scale", StandardScaler()), ("model", Ridge(alpha=alpha))])


def create_e1_final_test_seal(
    *,
    manifest_path: Path,
    config_path: Path,
    preregistration_seal_path: Path,
    train_validation_result_path: Path,
    robustness_result_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    """Freeze the exact primary E1 test without opening the physical 2025 file."""

    prereg = verify_e1_preregistration_seal(
        seal_path=preregistration_seal_path,
        manifest_path=manifest_path,
        config_path=config_path,
    )
    tv = _read_json(train_validation_result_path)
    robustness = _read_json(robustness_result_path)
    _verify_internal_hash(tv)
    _verify_internal_hash(robustness)

    if tv.get("kind") != "ninja-e1-train-validation":
        raise ValueError("unexpected train/validation artifact kind")
    if tv.get("untouched_test_opened") is not False:
        raise ValueError("train/validation artifact reports untouched-test access")
    if tv.get("dataset_manifest_sha256") != sha256_file(manifest_path):
        raise ValueError("train/validation artifact used a different manifest")
    if tv.get("experiment_config_sha256") != sha256_file(config_path):
        raise ValueError("train/validation artifact used a different config")
    if tv.get("preregistration", {}).get("seal_sha256") != prereg["seal_sha256"]:
        raise ValueError("train/validation artifact is not bound to this preregistration seal")

    primary = tv.get("primary_confirmatory_result")
    if not isinstance(primary, dict) or primary.get("status") != "SUPPORTED":
        raise ValueError("final test remains locked unless the preregistered primary is SUPPORTED")

    if robustness.get("kind") != "ninja-e1-robustness":
        raise ValueError("unexpected robustness artifact kind")
    if robustness.get("passed") is not True or robustness.get("status") != "PASSED":
        raise ValueError("final test remains locked unless robustness passes")
    if robustness.get("untouched_test_opened") is not False:
        raise ValueError("robustness artifact reports untouched-test access")
    if robustness.get("preregistration_seal_sha256") != prereg["seal_sha256"]:
        raise ValueError("robustness artifact uses a different preregistration seal")
    if robustness.get("train_validation_result_sha256") != sha256_file(train_validation_result_path):
        raise ValueError("robustness artifact uses a different train/validation result")
    if robustness.get("dataset_manifest_sha256") != sha256_file(manifest_path):
        raise ValueError("robustness artifact uses a different manifest")
    if robustness.get("experiment_config_sha256") != sha256_file(config_path):
        raise ValueError("robustness artifact uses a different config")

    cfg = _read_toml(config_path)
    confirmatory = cfg["confirmatory"]
    manifest = _read_manifest(manifest_path)
    untouched_record = manifest["artifacts"].get("gold_untouched_test")
    if not isinstance(untouched_record, dict):
        raise ValueError("manifest lacks gold_untouched_test artifact")

    frozen = {
        "target": str(confirmatory["primary_target"]),
        "horizon_bins": int(confirmatory["primary_horizon_bins"]),
        "candidate": str(confirmatory["primary_candidate"]),
        "primary_loss": str(confirmatory["primary_loss"]),
        "minimum_relative_loss_improvement": float(confirmatory["minimum_relative_loss_improvement"]),
        "alpha": float(confirmatory["alpha"]),
        "candidate_features": list(MARKET_FEATURES)
        + list(cfg["feature_groups"][str(confirmatory["primary_candidate"])]),
        "baseline_features": list(MARKET_FEATURES),
        "ridge_alpha": float(cfg["models"]["ridge_alpha"]),
        "bootstrap_block_size": int(cfg["validation"]["bootstrap_block_size"]),
        "bootstrap_resamples": int(cfg["validation"]["bootstrap_resamples"]),
        "test_embargo_bins": int(cfg["validation"]["embargo_bins"]),
    }

    payload: dict[str, Any] = {
        "schema_version": 1,
        "kind": "ninja-e1-final-test-seal",
        "status": "SEALED",
        "created_at": utc_now().isoformat().replace("+00:00", "Z"),
        "code_commit": git_commit(),
        "experiment_id": cfg["experiment"]["id"],
        "dataset_manifest_sha256": sha256_file(manifest_path),
        "experiment_config_sha256": sha256_file(config_path),
        "preregistration_seal_sha256": prereg["seal_sha256"],
        "train_validation_result_sha256": sha256_file(train_validation_result_path),
        "train_validation_internal_result_sha256": tv["result_sha256"],
        "robustness_result_sha256": sha256_file(robustness_result_path),
        "robustness_internal_result_sha256": robustness["result_sha256"],
        "frozen_primary": frozen,
        "untouched_test": {
            "sha256_from_manifest": untouched_record.get("sha256"),
            "rows_from_manifest": untouched_record.get("rows"),
            "bytes_from_manifest": untouched_record.get("bytes"),
            "opened_by_seal_creation": False,
        },
        "scientific_boundary": (
            "Seal creation does not open 2025. It only freezes a train/validation-supported, robustness-passed primary comparison for one final evaluation."
        ),
    }
    payload["seal_sha256"] = sha256_json(payload)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def verify_e1_final_test_seal(
    *,
    seal_path: Path,
    manifest_path: Path,
    config_path: Path,
    preregistration_seal_path: Path,
    train_validation_result_path: Path,
    robustness_result_path: Path,
) -> dict[str, Any]:
    seal = _read_json(seal_path)
    if seal.get("kind") != "ninja-e1-final-test-seal" or seal.get("status") != "SEALED":
        raise ValueError("invalid E1 final-test seal")
    expected = dict(seal)
    stored = expected.pop("seal_sha256", None)
    if stored != sha256_json(expected):
        raise ValueError("final-test seal hash mismatch")
    if seal.get("dataset_manifest_sha256") != sha256_file(manifest_path):
        raise ValueError("manifest changed after final-test seal")
    if seal.get("experiment_config_sha256") != sha256_file(config_path):
        raise ValueError("config changed after final-test seal")
    prereg = _read_json(preregistration_seal_path)
    if seal.get("preregistration_seal_sha256") != prereg.get("seal_sha256"):
        raise ValueError("preregistration seal changed after final-test seal")
    if seal.get("train_validation_result_sha256") != sha256_file(train_validation_result_path):
        raise ValueError("train/validation result changed after final-test seal")
    if seal.get("robustness_result_sha256") != sha256_file(robustness_result_path):
        raise ValueError("robustness result changed after final-test seal")
    if seal.get("untouched_test", {}).get("opened_by_seal_creation") is not False:
        raise ValueError("invalid final-test seal access state")
    return seal


def run_e1_final_test(
    *,
    manifest_path: Path,
    config_path: Path,
    preregistration_seal_path: Path,
    train_validation_result_path: Path,
    robustness_result_path: Path,
    final_test_seal_path: Path,
    access_ledger_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    """Open and evaluate the untouched test exactly once per access ledger."""

    seal = verify_e1_final_test_seal(
        seal_path=final_test_seal_path,
        manifest_path=manifest_path,
        config_path=config_path,
        preregistration_seal_path=preregistration_seal_path,
        train_validation_result_path=train_validation_result_path,
        robustness_result_path=robustness_result_path,
    )
    if access_ledger_path.exists():
        raise FileExistsError(
            f"final-test access ledger already exists: {access_ledger_path}; create a new preregistered experiment generation rather than reopening 2025"
        )

    access_ledger_path.parent.mkdir(parents=True, exist_ok=True)
    started = {
        "schema_version": 1,
        "kind": "ninja-e1-final-test-access",
        "status": "STARTED",
        "started_at": utc_now().isoformat().replace("+00:00", "Z"),
        "final_test_seal_sha256": seal["seal_sha256"],
        "code_commit": git_commit(),
    }
    # Exclusive creation happens before resolving or hashing the physical test file.
    with access_ledger_path.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(started, indent=2, sort_keys=True) + "\n")

    manifest = _read_manifest(manifest_path)
    cfg = _read_toml(config_path)
    train_path = _artifact_path(manifest_path, manifest["artifacts"]["gold_train"])
    validation_path = _artifact_path(manifest_path, manifest["artifacts"]["gold_validation"])
    test_record = manifest["artifacts"]["gold_untouched_test"]
    test_path = _artifact_path(manifest_path, test_record)
    physical_test_sha = sha256_file(test_path)
    expected_test_sha = seal["untouched_test"]["sha256_from_manifest"]
    if expected_test_sha and physical_test_sha != expected_test_sha:
        raise ValueError("physical untouched-test artifact does not match the sealed manifest")

    train_rows = _load_split(train_path, "train")
    validation_rows = _load_split(validation_path, "validation")
    test_rows = _load_split(test_path, "untouched_test")
    if not train_rows or not validation_rows or not test_rows:
        raise ValueError("final test requires non-empty train, validation and untouched-test artifacts")
    rows = train_rows + validation_rows + test_rows
    _validate_grid(rows)
    _build_features(rows, cfg)

    frozen = seal["frozen_primary"]
    target = str(frozen["target"])
    horizon = int(frozen["horizon_bins"])
    if target != "future_rv":
        raise ValueError("E1 v1 final evaluator supports the preregistered future_rv primary")
    baseline_features = list(frozen["baseline_features"])
    candidate_features = list(frozen["candidate_features"])
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

    dev_end = len(train_rows) + len(validation_rows)
    dev_indices = [
        index
        for index in range(dev_end)
        if target_values[index] is not None
        and all(_valid_number(rows[index].get(feature)) for feature in candidate_features)
    ]
    test_start = dev_end + int(frozen["test_embargo_bins"])
    test_indices = [
        index
        for index in range(test_start, len(rows))
        if target_values[index] is not None
        and all(_valid_number(rows[index].get(feature)) for feature in candidate_features)
    ]
    if len(dev_indices) < 1000 or len(test_indices) < 1000:
        raise ValueError("insufficient common support for final E1 evaluation")

    y_dev = np.asarray([target_values[index] for index in dev_indices], dtype=float)
    y_test = np.asarray([target_values[index] for index in test_indices], dtype=float)
    alpha = float(frozen["ridge_alpha"])
    baseline = _ridge(alpha)
    candidate = _ridge(alpha)
    baseline.fit(_matrix(rows, dev_indices, baseline_features), y_dev)
    candidate.fit(_matrix(rows, dev_indices, candidate_features), y_dev)
    baseline_loss = (y_test - baseline.predict(_matrix(rows, test_indices, baseline_features))) ** 2
    candidate_loss = (y_test - candidate.predict(_matrix(rows, test_indices, candidate_features))) ** 2
    baseline_mean = float(np.mean(baseline_loss))
    candidate_mean = float(np.mean(candidate_loss))
    relative_gain = (baseline_mean - candidate_mean) / baseline_mean if baseline_mean > 0 else 0.0
    inference = _paired_block_inference(
        (baseline_loss - candidate_loss).tolist(),
        block_size=int(frozen["bootstrap_block_size"]),
        resamples=int(frozen["bootstrap_resamples"]),
        seed=int(cfg["experiment"]["random_seed"]) + 9091,
    )

    minimum_gain = float(frozen["minimum_relative_loss_improvement"])
    alpha_level = float(frozen["alpha"])
    if relative_gain >= minimum_gain and float(inference["ci95_low"]) > 0 and float(inference["p_value"]) <= alpha_level:
        status = "SUPPORTED"
    elif relative_gain <= -minimum_gain or float(inference["ci95_high"]) < 0:
        status = "REJECTED"
    else:
        status = "INCONCLUSIVE"

    payload: dict[str, Any] = {
        "schema_version": 1,
        "kind": "ninja-e1-final-test",
        "status": status,
        "created_at": utc_now().isoformat().replace("+00:00", "Z"),
        "code_commit": git_commit(),
        "experiment_id": seal["experiment_id"],
        "final_test_seal_sha256": seal["seal_sha256"],
        "untouched_test_opened": True,
        "untouched_test_sha256": physical_test_sha,
        "primary": {
            "target": target,
            "horizon_bins": horizon,
            "candidate": frozen["candidate"],
            "n_development": len(dev_indices),
            "n_test": len(test_indices),
            "baseline_primary_loss": baseline_mean,
            "candidate_primary_loss": candidate_mean,
            "relative_loss_improvement": relative_gain,
            **inference,
            "minimum_meaningful_relative_gain": minimum_gain,
            "alpha": alpha_level,
        },
        "secondary_test_results": None,
        "scientific_boundary": (
            "This artifact contains the one preregistered primary evaluation on the formerly untouched 2025 split. No secondary test fishing is performed."
        ),
    }
    payload["result_sha256"] = sha256_json(payload)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")

    completed = {
        **started,
        "status": "COMPLETED",
        "completed_at": utc_now().isoformat().replace("+00:00", "Z"),
        "untouched_test_sha256": physical_test_sha,
        "output_path": str(output_path),
        "output_sha256": sha256_file(output_path),
        "result_status": status,
    }
    access_ledger_path.write_text(json.dumps(completed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload
