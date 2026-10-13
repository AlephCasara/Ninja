from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, ValidationError

ROOT = Path(__file__).resolve().parents[1]


def load_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_session_template_matches_v2_top_level_contract() -> None:
    schema = load_json("schemas/experiment-spec-v2.schema.json")
    template = load_json("experiments/templates/session-spec-v2.json")

    assert template["schema_version"] == 2
    assert set(schema["required"]).issubset(template)
    assert template["phase"] in schema["properties"]["phase"]["enum"]
    assert template["replay_type"] in schema["properties"]["replay_type"]["enum"]
    assert template["evidence_boundary"]["outcome_access"] in {
        "outcome_blind_discovery",
        "label_aware_discovery",
    }
    assert template["evidence_boundary"]["candidate_frozen"] is False


def test_v2_contract_freezes_non_discovery_evaluation() -> None:
    schema = load_json("schemas/experiment-spec-v2.schema.json")
    conditions = schema["allOf"]

    frozen = next(
        item
        for item in conditions
        if item["if"]["properties"]["phase"].get("enum")
        == ["replication", "generalization", "economic"]
    )
    boundary = frozen["then"]["properties"]["evidence_boundary"]

    assert "evaluation_boundary" in boundary["required"]
    assert boundary["properties"]["candidate_frozen"] == {"const": True}
    assert boundary["properties"]["outcome_access"] == {"const": "frozen_evaluation"}


def test_v2_contract_reserves_prospective_mode_for_new_observations() -> None:
    schema = load_json("schemas/experiment-spec-v2.schema.json")
    prospective = next(
        item
        for item in schema["allOf"]
        if item["if"]["properties"]["phase"].get("const") == "prospective"
    )
    boundary = prospective["then"]["properties"]["evidence_boundary"]["properties"]

    assert boundary["candidate_frozen"] == {"const": True}
    assert boundary["outcome_access"] == {"const": "prospective_only"}


def validator() -> Draft202012Validator:
    schema = load_json("schemas/experiment-spec-v2.schema.json")
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def test_session_template_validates_against_full_json_schema() -> None:
    validator().validate(load_json("experiments/templates/session-spec-v2.json"))


def test_full_schema_rejects_unfrozen_replication() -> None:
    spec = deepcopy(load_json("experiments/templates/session-spec-v2.json"))
    spec["phase"] = "replication"
    spec["evidence_boundary"].update(
        outcome_access="frozen_evaluation",
        candidate_frozen=False,
        evaluation_boundary="2025-01-01/2025-12-31",
    )
    with pytest.raises(ValidationError):
        validator().validate(spec)


def test_full_schema_requires_dataset_manifest_and_coverage_checks() -> None:
    spec = deepcopy(load_json("experiments/templates/session-spec-v2.json"))
    spec["data"]["dataset_manifest_ids"] = []
    with pytest.raises(ValidationError):
        validator().validate(spec)

    spec = deepcopy(load_json("experiments/templates/session-spec-v2.json"))
    spec["design"].pop("coverage_checks")
    with pytest.raises(ValidationError):
        validator().validate(spec)
