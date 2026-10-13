from __future__ import annotations

from ninja_labs.validation.e1_backtester import run_e1_backtester_validation


def test_e1_backtester_recovers_known_signal_without_null_discoveries():
    payload = run_e1_backtester_validation(
        null_worlds=2,
        n_train=5000,
        n_validation=2500,
        bootstrap_resamples=99,
        max_null_discovery_fraction=0.0,
    )

    assert payload["passed"] is True
    assert payload["status"] == "VALIDATED_FOR_E1"
    assert payload["criteria"]["known_signal_is_supported"] is True
    assert payload["metrics"]["signal_relative_gain"] >= 0.005
    assert payload["metrics"]["null_discoveries"] == 0
    assert payload["metrics"]["untouched_test_opened_anywhere"] is False
