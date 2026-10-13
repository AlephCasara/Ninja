from __future__ import annotations

import json
import tomllib
from pathlib import Path
from typing import Any

from ninja_labs.util import git_commit, sha256_file, sha256_json, utc_now


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_toml(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        return tomllib.load(handle)


def _artifact_path(manifest_path: Path, record: dict[str, Any]) -> Path:
    path = Path(record["path"])
    if path.is_file():
        return path
    candidate = manifest_path.parent / path
    if candidate.is_file():
        return candidate
    raise FileNotFoundError(path)


def create_e1_preregistration_seal(
    *,
    manifest_path: Path,
    config_path: Path,
    dataset_quality_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    """Seal E1 before train/validation without opening untouched-test data."""

    manifest = _read_json(manifest_path)
    config = _read_toml(config_path)
    dataset_quality = _read_json(dataset_quality_path)

    manifest_commit = manifest.get("code_commit")
    if not manifest_commit or manifest.get("code_dirty") is not False:
        raise ValueError("canonical dataset manifest was not produced from a clean Git state")
    if dataset_quality.get("code_dirty") is not False:
        raise ValueError("dataset quality artifact was produced from a dirty Git state")
    if dataset_quality.get("code_commit") != manifest_commit:
        raise ValueError("dataset quality artifact was produced from a different code commit")

    if config.get("experiment", {}).get("stage") != "train_validation":
        raise ValueError("E1 preregistration requires experiment.stage=train_validation")

    allowed = set(config.get("data", {}).get("allowed_splits", []))
    forbidden = set(config.get("data", {}).get("forbidden_splits", []))
    if allowed != {"train", "validation"}:
        raise ValueError("E1 preregistration must allow exactly train and validation")
    if "untouched_test" not in forbidden:
        raise ValueError("E1 preregistration must explicitly forbid untouched_test")

    confirmatory = config.get("confirmatory")
    if not isinstance(confirmatory, dict):
        raise ValueError("E1 config requires a [confirmatory] section")
    required_confirmatory = {
        "primary_target",
        "primary_horizon_bins",
        "primary_candidate",
        "primary_loss",
        "minimum_relative_loss_improvement",
        "alpha",
    }
    missing = required_confirmatory - set(confirmatory)
    if missing:
        raise ValueError(f"missing confirmatory fields: {sorted(missing)}")

    experiment_minimum = float(
        config.get("experiment", {}).get("minimum_relative_loss_improvement", -1.0)
    )
    confirmatory_minimum = float(confirmatory["minimum_relative_loss_improvement"])
    if abs(experiment_minimum - confirmatory_minimum) > 1e-12:
        raise ValueError("experiment and confirmatory minimum effect thresholds disagree")

    manifest_sha = sha256_file(manifest_path)
    config_sha = sha256_file(config_path)
    if dataset_quality.get("kind") != "e1-canonical-dataset-quality-gate":
        raise ValueError("unexpected dataset quality artifact kind")
    if dataset_quality.get("passed") is not True or dataset_quality.get("status") != "ACCEPTED":
        raise ValueError("canonical E1 dataset has not passed its quality gate")
    if dataset_quality.get("dataset_manifest_sha256") != manifest_sha:
        raise ValueError("dataset quality gate was produced from a different manifest")
    if dataset_quality.get("experiment_config_sha256") != config_sha:
        raise ValueError("dataset quality gate was produced from a different E1 config")

    artifacts = manifest.get("artifacts", {})
    required_artifacts = {
        "gold_train",
        "gold_validation",
        "gold_untouched_test",
        "coverage",
    }
    missing_artifacts = required_artifacts - set(artifacts)
    if missing_artifacts:
        raise ValueError(f"dataset manifest is missing artifacts: {sorted(missing_artifacts)}")

    coverage_path = _artifact_path(manifest_path, artifacts["coverage"])
    coverage = _read_json(coverage_path)
    aligned = coverage.get("aligned", {})
    market = coverage.get("market", {})
    observations = coverage.get("observations", {})

    if int(aligned.get("future_window_rows", -1)) != 0:
        raise ValueError("coverage audit reports future feature-window leakage")
    if int(aligned.get("future_observation_rows", -1)) != 0:
        raise ValueError("coverage audit reports future observation leakage")
    if int(market.get("gap_count", -1)) != 0:
        raise ValueError("coverage audit reports market gaps")

    rows_by_split = aligned.get("rows_by_split", {})
    for split in ("train", "validation", "untouched_test"):
        if int(rows_by_split.get(split, 0)) <= 0:
            raise ValueError(f"coverage audit has no rows for split {split}")

    # Important: use only manifest metadata for the untouched artifact. Never
    # call sha256_file() or otherwise open the physical test file here.
    untouched_record = artifacts["gold_untouched_test"]
    untouched_metadata = {
        "sha256_from_dataset_manifest": untouched_record.get("sha256"),
        "rows_from_dataset_manifest": untouched_record.get("rows"),
        "bytes_from_dataset_manifest": untouched_record.get("bytes"),
        "opened_by_preregistration": False,
    }

    payload: dict[str, Any] = {
        "schema_version": 1,
        "kind": "ninja-e1-preregistration-seal",
        "status": "SEALED_FOR_TRAIN_VALIDATION",
        "created_at": utc_now().isoformat().replace("+00:00", "Z"),
        "code_commit": git_commit(),
        "experiment_id": config["experiment"]["id"],
        "hypothesis_id": config["experiment"]["hypothesis"],
        "dataset_manifest_id": manifest["manifest_id"],
        "dataset_manifest_sha256": manifest_sha,
        "experiment_config_sha256": config_sha,
        "dataset_quality_sha256": sha256_file(dataset_quality_path),
        "dataset_quality_result_sha256": dataset_quality.get("result_sha256"),
        "coverage_sha256": sha256_file(coverage_path),
        "confirmatory": {
            "primary_target": str(confirmatory["primary_target"]),
            "primary_horizon_bins": int(confirmatory["primary_horizon_bins"]),
            "primary_candidate": str(confirmatory["primary_candidate"]),
            "primary_loss": str(confirmatory["primary_loss"]),
            "minimum_relative_loss_improvement": confirmatory_minimum,
            "alpha": float(confirmatory["alpha"]),
        },
        "analysis_family": {
            "horizons_bins": [int(value) for value in config["targets"]["horizons_bins"]],
            "feature_groups": sorted(config["feature_groups"].keys()),
            "fdr_method": "Benjamini-Hochberg",
            "fdr_alpha": float(config["validation"]["fdr_alpha"]),
        },
        "data_quality": {
            "gate_status": dataset_quality["status"],
            "market_gap_count": int(market["gap_count"]),
            "future_window_rows": int(aligned["future_window_rows"]),
            "future_observation_rows": int(aligned["future_observation_rows"]),
            "observation_rows": int(observations.get("rows", 0)),
            "archive_capture_rows": int(observations.get("archive_capture_rows", 0)),
            "source_timestamp_rows": int(observations.get("source_timestamp_rows", 0)),
            "rows_by_split": rows_by_split,
        },
        "untouched_test": untouched_metadata,
        "scientific_boundary": (
            "This seal is created before train/validation outcomes are observed. "
            "It binds the accepted canonical dataset, frozen experiment configuration and clean code revision; "
            "it authorizes train+validation only and does not authorize opening the untouched test artifact."
        ),
    }
    payload["seal_sha256"] = sha256_json(payload)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return payload


def verify_e1_preregistration_seal(
    *,
    seal_path: Path,
    manifest_path: Path,
    config_path: Path,
) -> dict[str, Any]:
    seal = _read_json(seal_path)
    if seal.get("kind") != "ninja-e1-preregistration-seal":
        raise ValueError("unexpected preregistration seal kind")
    if seal.get("status") != "SEALED_FOR_TRAIN_VALIDATION":
        raise ValueError("preregistration seal is not valid for train/validation")
    if seal.get("dataset_manifest_sha256") != sha256_file(manifest_path):
        raise ValueError("dataset manifest changed after preregistration")
    if seal.get("experiment_config_sha256") != sha256_file(config_path):
        raise ValueError("experiment config changed after preregistration")
    if seal.get("data_quality", {}).get("gate_status") != "ACCEPTED":
        raise ValueError("preregistration seal lacks an accepted dataset quality gate")
    expected = dict(seal)
    stored_hash = expected.pop("seal_sha256", None)
    if stored_hash != sha256_json(expected):
        raise ValueError("preregistration seal hash mismatch")
    if seal.get("untouched_test", {}).get("opened_by_preregistration") is not False:
        raise ValueError("invalid preregistration untouched-test state")
    return seal
