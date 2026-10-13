from __future__ import annotations

from ninja_labs.validation.e1_attention import run_e1_estimator_validation


def test_e1_estimator_validation_suite_passes_controlled_worlds():
    payload = run_e1_estimator_validation(seed=20261013)
    assert payload["passed"] is True
    assert payload["status"] == "VALIDATED_FOR_E1"
    assert payload["checks"]["robust_attention_surprise"]["passed"] is True
    assert payload["checks"]["negative_binomial"]["passed"] is True
    assert payload["checks"]["attention_acceleration"]["passed"] is True
    assert payload["checks"]["author_structure"]["passed"] is True
    seasonality = payload["checks"]["seasonality_control"]
    assert seasonality["passed"] is True
    assert abs(seasonality["rolling_az_phase_correlation"]) > 0.4
    assert abs(seasonality["seasonal_az_phase_correlation"]) < 0.15
