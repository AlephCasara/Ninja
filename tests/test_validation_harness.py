from __future__ import annotations

from ninja_labs.validation.harness import run_validation_selftest


def test_validation_harness_selftest_passes_deterministically():
    result = run_validation_selftest(seed=1729)
    assert result["passed"] is True
    assert all(check["passed"] for check in result["checks"].values())
