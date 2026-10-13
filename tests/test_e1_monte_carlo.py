from __future__ import annotations

from ninja_labs.validation.e1_monte_carlo import run_e1_monte_carlo_validation


def test_e1_monte_carlo_gate_passes_multiple_randomized_worlds():
    payload = run_e1_monte_carlo_validation(
        seed=20261013,
        worlds=16,
        length=8000,
    )
    assert payload["passed"] is True
    assert payload["status"] == "VALIDATED_FOR_E1"
    metrics = payload["metrics"]
    assert metrics["worlds"] == 16
    assert metrics["evaluated_bins"] > 40_000
    assert metrics["burst_recall"] >= 0.95
    assert metrics["false_positive_rate"] <= 0.06
    assert metrics["p95_seasonal_daily_abs_r"] <= 0.06
    assert metrics["p95_seasonal_weekly_abs_r"] <= 0.06
    assert metrics["median_seasonal_daily_abs_r"] < metrics["median_rolling_daily_abs_r"] * 0.25
