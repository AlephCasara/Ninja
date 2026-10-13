from __future__ import annotations

import json

import pytest

from ninja_labs.preregistration import (
    create_e1_preregistration_seal,
    verify_e1_preregistration_seal,
)
from ninja_labs.util import sha256_file


def _write_fixture(tmp_path):
    coverage = tmp_path / "coverage.json"
    coverage.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "observations": {
                    "rows": 1000,
                    "archive_capture_rows": 990,
                    "source_timestamp_rows": 10,
                },
                "market": {"gap_count": 0},
                "aligned": {
                    "future_window_rows": 0,
                    "future_observation_rows": 0,
                    "rows_by_split": {
                        "train": 600,
                        "validation": 200,
                        "untouched_test": 200,
                    },
                },
            }
        ),
        encoding="utf-8",
    )

    untouched = tmp_path / "THIS_FILE_MUST_NOT_BE_OPENED.parquet"
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "manifest_id": "fixture-manifest",
                "artifacts": {
                    "coverage": {
                        "path": str(coverage),
                        "sha256": sha256_file(coverage),
                        "bytes": coverage.stat().st_size,
                    },
                    "gold_train": {"path": "train.parquet", "sha256": "train-sha", "rows": 600, "bytes": 1},
                    "gold_validation": {"path": "validation.parquet", "sha256": "validation-sha", "rows": 200, "bytes": 1},
                    "gold_untouched_test": {
                        "path": str(untouched),
                        "sha256": "sealed-test-sha-from-manifest",
                        "rows": 200,
                        "bytes": 123,
                    },
                },
            }
        ),
        encoding="utf-8",
    )

    config = tmp_path / "e1.toml"
    config.write_text(
        """
[experiment]
id = "E1-fixture"
hypothesis = "N1"
stage = "train_validation"
minimum_relative_loss_improvement = 0.005

[data]
allowed_splits = ["train", "validation"]
forbidden_splits = ["untouched_test"]

[confirmatory]
primary_target = "future_rv"
primary_horizon_bins = 16
primary_candidate = "market_plus_seasonal_attention"
primary_loss = "mse"
minimum_relative_loss_improvement = 0.005
alpha = 0.05

[targets]
horizons_bins = [1, 4, 16, 96]

[validation]
fdr_alpha = 0.05

[feature_groups]
market_only = []
market_plus_seasonal_attention = ["seasonal_attention_surprise", "attention_acceleration"]
""".strip()
        + "\n",
        encoding="utf-8",
    )

    estimator = tmp_path / "estimator.json"
    estimator.write_text(
        json.dumps(
            {
                "kind": "e1-attention-estimator-validation",
                "passed": True,
                "status": "VALIDATED_FOR_E1",
                "result_sha256": "controlled-world-result",
            }
        ),
        encoding="utf-8",
    )
    return manifest, config, estimator, untouched


def test_preregistration_seal_does_not_open_untouched_test(tmp_path):
    manifest, config, estimator, untouched = _write_fixture(tmp_path)
    seal_path = tmp_path / "seal.json"

    seal = create_e1_preregistration_seal(
        manifest_path=manifest,
        config_path=config,
        estimator_validation_path=estimator,
        output_path=seal_path,
    )

    assert seal["status"] == "SEALED_FOR_TRAIN_VALIDATION"
    assert seal["confirmatory"]["primary_horizon_bins"] == 16
    assert seal["untouched_test"]["opened_by_preregistration"] is False
    assert seal["untouched_test"]["sha256_from_dataset_manifest"] == "sealed-test-sha-from-manifest"
    assert not untouched.exists()
    verified = verify_e1_preregistration_seal(
        seal_path=seal_path,
        manifest_path=manifest,
        config_path=config,
    )
    assert verified["seal_sha256"] == seal["seal_sha256"]


def test_preregistration_seal_detects_posthoc_config_change(tmp_path):
    manifest, config, estimator, _ = _write_fixture(tmp_path)
    seal_path = tmp_path / "seal.json"
    create_e1_preregistration_seal(
        manifest_path=manifest,
        config_path=config,
        estimator_validation_path=estimator,
        output_path=seal_path,
    )
    config.write_text(config.read_text(encoding="utf-8") + "# posthoc mutation\n", encoding="utf-8")
    with pytest.raises(ValueError, match="config changed"):
        verify_e1_preregistration_seal(
            seal_path=seal_path,
            manifest_path=manifest,
            config_path=config,
        )
