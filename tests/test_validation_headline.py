from __future__ import annotations

from ninja_labs.validation.headline import assess_headline_eligibility


def valid_record() -> dict:
    return {
        "experiment_id": "E1-attention-rv-4h-v1",
        "hypothesis_id": "N1",
        "primary_metric": "oos_rmse_delta",
        "preregistered": True,
        "sample": {"raw_n": 1000, "effective_n": 420.0},
        "split_policy": {
            "chronological": True,
            "purging": True,
            "embargo": True,
        },
        "multiple_testing": {"family_size": 6, "method": "benjamini-hochberg"},
        "untouched_test": {"access_count": 1, "frozen_before_access": True},
        "falsification": {
            "rejection_rule": "reject if incremental OOS gain is not positive",
            "minimum_meaningful_effect": "at least 1% relative RMSE improvement",
        },
    }


def test_complete_record_is_headline_eligible():
    assessment = assess_headline_eligibility(valid_record())
    assert assessment == {"eligible": True, "failures": []}


def test_repeated_test_peeking_is_rejected():
    record = valid_record()
    record["untouched_test"]["access_count"] = 2
    assessment = assess_headline_eligibility(record)
    assert assessment["eligible"] is False
    assert "untouched test was accessed more than once" in assessment["failures"]
