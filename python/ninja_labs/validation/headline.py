from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def assess_headline_eligibility(record: Mapping[str, Any]) -> dict[str, Any]:
    """Return whether an experiment result may be treated as a headline claim.

    This does not decide whether a hypothesis is true. It only checks that the
    experiment supplied the minimum anti-confirmation evidence required before
    a result can be promoted beyond exploratory status.
    """

    failures: list[str] = []

    if not record.get("preregistered", False):
        failures.append("experiment was not preregistered")

    for field in ("experiment_id", "hypothesis_id", "primary_metric"):
        if not record.get(field):
            failures.append(f"missing {field}")

    sample = record.get("sample", {})
    raw_n = sample.get("raw_n")
    effective_n = sample.get("effective_n")
    if not isinstance(raw_n, (int, float)) or raw_n <= 0:
        failures.append("raw sample size is missing or invalid")
    if not isinstance(effective_n, (int, float)) or effective_n <= 0:
        failures.append("effective sample size is missing or invalid")
    elif isinstance(raw_n, (int, float)) and effective_n > raw_n:
        failures.append("effective sample size cannot exceed raw sample size")

    validation = record.get("validation", {})
    if validation.get("synthetic_recovery_passed") is not True:
        failures.append("synthetic recovery did not pass")
    if validation.get("null_calibration_passed") is not True:
        failures.append("null calibration did not pass")
    if validation.get("negative_controls_passed") is not True:
        failures.append("negative controls did not pass")

    split_policy = record.get("split_policy", {})
    if split_policy.get("chronological") is not True:
        failures.append("headline split is not chronological")
    if split_policy.get("purging") is not True:
        failures.append("label purging was not enforced")
    if split_policy.get("embargo") is not True:
        failures.append("boundary embargo was not enforced")

    multiple_testing = record.get("multiple_testing", {})
    family_size = multiple_testing.get("family_size")
    method = multiple_testing.get("method")
    if not isinstance(family_size, int) or family_size <= 0:
        failures.append("multiple-testing family size is missing or invalid")
    elif family_size > 1 and method in {None, "", "none", "not_applicable"}:
        failures.append("multiple-testing correction missing for family_size > 1")

    untouched = record.get("untouched_test", {})
    accesses = untouched.get("access_count")
    frozen_before_access = untouched.get("frozen_before_access")
    if not isinstance(accesses, int) or accesses < 0:
        failures.append("untouched-test access count is missing or invalid")
    elif accesses > 1:
        failures.append("untouched test was accessed more than once")
    if accesses and frozen_before_access is not True:
        failures.append("experiment was not frozen before untouched-test access")

    falsification = record.get("falsification", {})
    if not falsification.get("rejection_rule"):
        failures.append("missing explicit rejection rule")
    if not falsification.get("minimum_meaningful_effect"):
        failures.append("missing minimum meaningful effect")

    return {
        "eligible": not failures,
        "failures": failures,
    }
