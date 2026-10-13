from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

from jsonschema import Draft202012Validator

from ninja_labs.replay import (
    AvailabilityPolicy,
    KnowledgePolicy,
    PricePoint,
    ReplayType,
    SemanticInterpretation,
    UniverseCandidateSnapshot,
    compute_market_path_outcome,
    freeze_point_in_time_universe,
    freeze_replay_state,
)

ROOT = Path(__file__).resolve().parents[1]


def dt(minute: int = 0) -> datetime:
    return datetime(2025, 1, 1, 12, minute, tzinfo=UTC)


def validate(schema_name: str, instance: dict) -> None:
    schema = json.loads((ROOT / "schemas" / schema_name).read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(instance)


def semantic() -> SemanticInterpretation:
    return SemanticInterpretation(
        interpretation_id="sem-1",
        observation_id="obs-1",
        observation_content_hash="content-hash",
        extractor_id="document-extractor",
        extractor_version="v1",
        generated_at=dt(10),
        knowledge_policy=KnowledgePolicy.DOCUMENT_ONLY,
        outcome_blind=True,
        grounded_in_inputs=True,
        fields={"actor": "Example"},
        context_max_available_at=dt(0),
        prompt_hash="prompt-hash",
        model_id="model-v1",
    )


def replay_state():
    observation = {
        "observation_id": "obs-1",
        "content_hash": "content-hash",
        "published_at": dt(0),
        "first_seen_at": dt(0),
        "available_at": dt(0),
        "source_id": "source-1",
        "platform": "example",
    }
    return freeze_replay_state(
        replay_type=ReplayType.STATE,
        domain="trading.crypto",
        subject_id="BTCUSDT",
        decision_time=dt(1),
        observations=[observation],
        interpretations=[semantic()],
        market_rows=[
            {
                "decision_time": dt(0),
                "symbol": "BTCUSDT",
                "interval": "1m",
                "close": 100.0,
            }
        ],
        information_builder=lambda rows, interpretations: {
            "message_count": len(rows),
            "semantic_count": len(interpretations),
        },
        market_builder=lambda rows: {"last_close": rows[-1]["close"]},
        representation_version="state-v1",
        dataset_manifest_ids=["manifest-1"],
        code_revision="abc123",
        availability_policy=AvailabilityPolicy.EXPLICIT,
        frozen_at=dt(20),
    )


def test_semantic_interpretation_record_matches_schema() -> None:
    validate("semantic-interpretation-v1.schema.json", semantic().as_record())


def test_frozen_replay_state_record_matches_schema() -> None:
    validate("replay-state-v2.schema.json", replay_state().as_record())


def test_replay_outcome_record_matches_schema() -> None:
    state = replay_state()
    outcome = compute_market_path_outcome(
        state=state,
        prices=[
            PricePoint(dt(1), 100.0),
            PricePoint(dt(2), 101.0),
            PricePoint(dt(3), 99.0),
        ],
        horizon_end=dt(3),
        max_reference_delay_seconds=0,
        max_path_gap_seconds=60,
        multiples=(2.0,),
        created_at=dt(20),
    )
    validate("replay-outcome-v2.schema.json", outcome.as_record())


def test_frozen_universe_record_matches_schema() -> None:
    candidate = UniverseCandidateSnapshot(
        subject_id="BTCUSDT",
        attributes_as_of=dt(0),
        eligible_from=dt(0),
        eligible_until=None,
        attributes={"liquid": True},
        evidence_ref="fixture:btc",
    )
    universe = freeze_point_in_time_universe(
        as_of=dt(1),
        domain="trading.crypto",
        eligibility_rule_id="listed-liquid-v1",
        candidate_snapshots=[candidate],
        eligibility_predicate=lambda attrs: bool(attrs["liquid"]),
        dataset_manifest_ids=["manifest-1"],
        frozen_at=dt(20),
    )
    validate("replay-universe-v1.schema.json", universe.as_record())
