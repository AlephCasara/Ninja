from __future__ import annotations

import json
import pytest
from ninja_labs.preregistration import create_e1_preregistration_seal, verify_e1_preregistration_seal
from ninja_labs.util import git_commit, sha256_file

def _write_fixture(tmp_path, *, dataset_accepted: bool = True, quality_dirty: bool = False, quality_commit: str | None = None):
    coverage = tmp_path / "coverage.json"
    coverage.write_text(json.dumps({"schema_version":2,"observations":{"rows":1000,"archive_capture_rows":990,"source_timestamp_rows":10},"market":{"gap_count":0},"aligned":{"future_window_rows":0,"future_observation_rows":0,"rows_by_split":{"train":600,"validation":200,"untouched_test":200}}}), encoding="utf-8")
    untouched = tmp_path / "THIS_FILE_MUST_NOT_BE_OPENED.parquet"
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"manifest_id":"fixture-manifest","code_commit":git_commit(),"code_dirty":False,"artifacts":{"coverage":{"path":str(coverage),"sha256":sha256_file(coverage),"bytes":coverage.stat().st_size},"gold_train":{"path":"train.parquet","sha256":"train-sha","rows":600,"bytes":1},"gold_validation":{"path":"validation.parquet","sha256":"validation-sha","rows":200,"bytes":1},"gold_untouched_test":{"path":str(untouched),"sha256":"sealed-test-sha-from-manifest","rows":200,"bytes":123}}}), encoding="utf-8")
    config = tmp_path / "e1.toml"
    config.write_text("""[experiment]
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
""", encoding="utf-8")
    dataset_quality = tmp_path / "dataset-quality.json"
    dataset_quality.write_text(json.dumps({"kind":"e1-canonical-dataset-quality-gate","code_commit":quality_commit or git_commit(),"code_dirty":quality_dirty,"passed":dataset_accepted,"status":"ACCEPTED" if dataset_accepted else "REJECTED","dataset_manifest_sha256":sha256_file(manifest),"experiment_config_sha256":sha256_file(config),"result_sha256":"dataset-quality-result"}), encoding="utf-8")
    return manifest, config, dataset_quality, untouched

def _create_seal(tmp_path, fixture):
    manifest, config, dataset_quality, _ = fixture
    return create_e1_preregistration_seal(manifest_path=manifest, config_path=config, dataset_quality_path=dataset_quality, output_path=tmp_path/"seal.json")

def test_preregistration_seal_does_not_open_untouched_test(tmp_path):
    fixture=_write_fixture(tmp_path); manifest,config,_,untouched=fixture; seal=_create_seal(tmp_path,fixture)
    assert seal["status"]=="SEALED_FOR_TRAIN_VALIDATION"
    assert seal["confirmatory"]["primary_horizon_bins"]==16
    assert seal["data_quality"]["gate_status"]=="ACCEPTED"
    assert seal["untouched_test"]["opened_by_preregistration"] is False
    assert seal["untouched_test"]["sha256_from_dataset_manifest"]=="sealed-test-sha-from-manifest"
    assert not untouched.exists()
    verified=verify_e1_preregistration_seal(seal_path=tmp_path/"seal.json",manifest_path=manifest,config_path=config)
    assert verified["seal_sha256"]==seal["seal_sha256"]

def test_preregistration_rejects_failed_dataset_quality_gate(tmp_path):
    with pytest.raises(ValueError, match="dataset has not passed"):
        _create_seal(tmp_path,_write_fixture(tmp_path,dataset_accepted=False))

def test_preregistration_rejects_dataset_gate_from_different_config(tmp_path):
    fixture=_write_fixture(tmp_path); manifest,config,dataset_quality,_=fixture
    quality=json.loads(dataset_quality.read_text()); quality["experiment_config_sha256"]="0"*64; dataset_quality.write_text(json.dumps(quality))
    with pytest.raises(ValueError, match="different E1 config"):
        _create_seal(tmp_path,fixture)

def test_preregistration_rejects_dirty_dataset_quality_evidence(tmp_path):
    with pytest.raises(ValueError, match="dirty Git state"):
        _create_seal(tmp_path,_write_fixture(tmp_path,quality_dirty=True))

def test_preregistration_rejects_dataset_quality_from_different_commit(tmp_path):
    with pytest.raises(ValueError, match="different code commit"):
        _create_seal(tmp_path,_write_fixture(tmp_path,quality_commit="0"*40))

def test_preregistration_seal_detects_posthoc_config_change(tmp_path):
    fixture=_write_fixture(tmp_path); manifest,config,_,_=fixture; _create_seal(tmp_path,fixture)
    config.write_text(config.read_text()+"# posthoc mutation\n")
    with pytest.raises(ValueError, match="config changed"):
        verify_e1_preregistration_seal(seal_path=tmp_path/"seal.json",manifest_path=manifest,config_path=config)
