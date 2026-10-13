from __future__ import annotations

import json

import pytest

from ninja_labs import e1_final, e1_robustness
from ninja_labs.util import sha256_file, sha256_json


def _hashed(payload: dict) -> dict:
    result = dict(payload)
    result["result_sha256"] = sha256_json(result)
    return result


def _base_files(tmp_path, *, primary_status: str = "SUPPORTED", robustness_passed: bool = True):
    config = tmp_path / "e1.toml"
    config.write_text(
        """
[experiment]
id = "E1-fixture"
hypothesis = "N1"
random_seed = 20261013

[confirmatory]
primary_target = "future_rv"
primary_horizon_bins = 16
primary_candidate = "market_plus_seasonal_attention"
primary_loss = "mse"
minimum_relative_loss_improvement = 0.005
alpha = 0.05

[models]
ridge_alpha = 1.0

[validation]
bootstrap_block_size = 96
bootstrap_resamples = 499
embargo_bins = 96

[feature_groups]
market_plus_seasonal_attention = ["seasonal_attention_surprise", "attention_acceleration"]
""".strip()
        + "\n",
        encoding="utf-8",
    )
    untouched = tmp_path / "NEVER_OPEN_DURING_SEAL.parquet"
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "manifest_id": "fixture-manifest",
                "artifacts": {
                    "gold_train": {"path": "train.parquet", "sha256": "train", "rows": 10},
                    "gold_validation": {"path": "validation.parquet", "sha256": "validation", "rows": 10},
                    "gold_untouched_test": {
                        "path": str(untouched),
                        "sha256": "untouched-manifest-sha",
                        "rows": 10,
                        "bytes": 123,
                    },
                },
            }
        ),
        encoding="utf-8",
    )
    prereg = tmp_path / "prereg.json"
    prereg.write_text(json.dumps({"seal_sha256": "prereg-seal"}), encoding="utf-8")

    tv = tmp_path / "train-validation.json"
    tv_payload = _hashed(
        {
            "kind": "ninja-e1-train-validation",
            "untouched_test_opened": False,
            "dataset_manifest_sha256": sha256_file(manifest),
            "experiment_config_sha256": sha256_file(config),
            "preregistration": {"seal_sha256": "prereg-seal"},
            "primary_confirmatory_result": {
                "status": primary_status,
                "target": "future_rv",
                "horizon_bins": 16,
                "candidate": "market_plus_seasonal_attention",
                "relative_loss_improvement": 0.01,
            },
        }
    )
    tv.write_text(json.dumps(tv_payload), encoding="utf-8")

    robustness = tmp_path / "robustness.json"
    robust_payload = _hashed(
        {
            "kind": "ninja-e1-robustness",
            "status": "PASSED" if robustness_passed else "FAILED",
            "passed": robustness_passed,
            "untouched_test_opened": False,
            "dataset_manifest_sha256": sha256_file(manifest),
            "experiment_config_sha256": sha256_file(config),
            "preregistration_seal_sha256": "prereg-seal",
            "train_validation_result_sha256": sha256_file(tv),
        }
    )
    robustness.write_text(json.dumps(robust_payload), encoding="utf-8")
    return manifest, config, prereg, tv, robustness, untouched


def test_final_seal_does_not_open_untouched_test(monkeypatch, tmp_path):
    manifest, config, prereg, tv, robustness, untouched = _base_files(tmp_path)
    monkeypatch.setattr(
        e1_final,
        "verify_e1_preregistration_seal",
        lambda **kwargs: {"seal_sha256": "prereg-seal"},
    )
    seal = e1_final.create_e1_final_test_seal(
        manifest_path=manifest,
        config_path=config,
        preregistration_seal_path=prereg,
        train_validation_result_path=tv,
        robustness_result_path=robustness,
        output_path=tmp_path / "final-seal.json",
    )
    assert seal["status"] == "SEALED"
    assert seal["untouched_test"]["opened_by_seal_creation"] is False
    assert seal["untouched_test"]["sha256_from_manifest"] == "untouched-manifest-sha"
    assert not untouched.exists()


def test_final_seal_rejects_non_supported_primary(monkeypatch, tmp_path):
    manifest, config, prereg, tv, robustness, _ = _base_files(
        tmp_path, primary_status="INCONCLUSIVE"
    )
    monkeypatch.setattr(
        e1_final,
        "verify_e1_preregistration_seal",
        lambda **kwargs: {"seal_sha256": "prereg-seal"},
    )
    with pytest.raises(ValueError, match="primary is SUPPORTED"):
        e1_final.create_e1_final_test_seal(
            manifest_path=manifest,
            config_path=config,
            preregistration_seal_path=prereg,
            train_validation_result_path=tv,
            robustness_result_path=robustness,
            output_path=tmp_path / "final-seal.json",
        )


def test_final_seal_rejects_failed_robustness(monkeypatch, tmp_path):
    manifest, config, prereg, tv, robustness, _ = _base_files(
        tmp_path, robustness_passed=False
    )
    monkeypatch.setattr(
        e1_final,
        "verify_e1_preregistration_seal",
        lambda **kwargs: {"seal_sha256": "prereg-seal"},
    )
    with pytest.raises(ValueError, match="robustness passes"):
        e1_final.create_e1_final_test_seal(
            manifest_path=manifest,
            config_path=config,
            preregistration_seal_path=prereg,
            train_validation_result_path=tv,
            robustness_result_path=robustness,
            output_path=tmp_path / "final-seal.json",
        )


def test_existing_access_ledger_blocks_test_before_any_data_open(monkeypatch, tmp_path):
    ledger = tmp_path / "access.json"
    ledger.write_text("{}\n", encoding="utf-8")
    monkeypatch.setattr(
        e1_final,
        "verify_e1_final_test_seal",
        lambda **kwargs: {"seal_sha256": "final-seal"},
    )
    with pytest.raises(FileExistsError, match="access ledger already exists"):
        e1_final.run_e1_final_test(
            manifest_path=tmp_path / "missing-manifest.json",
            config_path=tmp_path / "missing-config.toml",
            preregistration_seal_path=tmp_path / "missing-prereg.json",
            train_validation_result_path=tmp_path / "missing-tv.json",
            robustness_result_path=tmp_path / "missing-robust.json",
            final_test_seal_path=tmp_path / "missing-final-seal.json",
            access_ledger_path=ledger,
            output_path=tmp_path / "never-written.json",
        )


def test_robustness_stops_when_primary_not_supported(monkeypatch, tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text("{}\n", encoding="utf-8")
    config = tmp_path / "config.toml"
    config.write_text(
        """
[experiment]
id = "E1-fixture"

[confirmatory]
primary_target = "future_rv"
primary_horizon_bins = 16
primary_candidate = "market_plus_seasonal_attention"
""".strip()
        + "\n",
        encoding="utf-8",
    )
    tv = tmp_path / "tv.json"
    tv.write_text(
        json.dumps(
            {
                "kind": "ninja-e1-train-validation",
                "untouched_test_opened": False,
                "dataset_manifest_sha256": sha256_file(manifest),
                "experiment_config_sha256": sha256_file(config),
                "preregistration": {"seal_sha256": "pre"},
                "primary_confirmatory_result": {
                    "status": "REJECTED",
                    "target": "future_rv",
                    "horizon_bins": 16,
                    "candidate": "market_plus_seasonal_attention",
                },
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        e1_robustness,
        "verify_e1_preregistration_seal",
        lambda **kwargs: {"seal_sha256": "pre"},
    )
    result = e1_robustness.run_e1_robustness(
        manifest_path=manifest,
        config_path=config,
        preregistration_seal_path=tmp_path / "pre.json",
        train_validation_result_path=tv,
        output_path=tmp_path / "robustness.json",
    )
    assert result["passed"] is False
    assert result["checks"]["primary_validation_eligibility"]["passed"] is False
    assert result["untouched_test_opened"] is False
