from __future__ import annotations

import json

from ninja_labs import sealed_e1


def test_sealed_runner_cannot_promote_secondary_result(monkeypatch, tmp_path):
    seal = {
        "seal_sha256": "seal-123",
        "confirmatory": {
            "primary_target": "future_rv",
            "primary_horizon_bins": 16,
            "primary_candidate": "market_plus_seasonal_attention",
            "primary_loss": "mse",
            "minimum_relative_loss_improvement": 0.005,
            "alpha": 0.05,
        },
    }

    def fake_verify(**kwargs):
        return seal

    def fake_run(**kwargs):
        payload = {
            "status_counts": {"SUPPORTED": 2},
            "comparisons": [
                {
                    "target": "future_rv",
                    "horizon_bins": 16,
                    "candidate": "market_plus_seasonal_attention",
                    "status": "INCONCLUSIVE",
                    "relative_loss_improvement": 0.003,
                    "ci95_low": -0.001,
                    "ci95_high": 0.007,
                    "p_value": 0.08,
                    "q_value": 0.12,
                    "n_train": 1000,
                    "n_validation": 300,
                    "effective_n": 120.0,
                },
                {
                    "target": "future_rv",
                    "horizon_bins": 96,
                    "candidate": "market_plus_attention_structure",
                    "status": "SUPPORTED",
                    "relative_loss_improvement": 0.04,
                },
            ],
            "untouched_test_opened": False,
            "result_sha256": "old",
        }
        kwargs["output_path"].write_text(json.dumps(payload), encoding="utf-8")
        return payload

    monkeypatch.setattr(sealed_e1, "verify_e1_preregistration_seal", fake_verify)
    monkeypatch.setattr(sealed_e1, "run_e1_train_validation", fake_run)

    output = tmp_path / "result.json"
    payload = sealed_e1.run_sealed_e1_train_validation(
        manifest_path=tmp_path / "manifest.json",
        config_path=tmp_path / "config.toml",
        seal_path=tmp_path / "seal.json",
        output_path=output,
    )

    assert payload["primary_confirmatory_result"]["status"] == "INCONCLUSIVE"
    assert payload["comparisons"][0]["role"] == "PRIMARY_CONFIRMATORY"
    assert payload["comparisons"][1]["role"] == "SECONDARY_OR_EXPLORATORY"
    assert payload["comparisons"][1]["status"] == "SUPPORTED"
    assert payload["preregistration"]["verified"] is True
    assert payload["untouched_test_opened"] is False
