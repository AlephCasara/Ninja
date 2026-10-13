from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from ninja_labs.replay import (
    AvailabilityPolicy,
    KnowledgePolicy,
    ReplayType,
    SemanticInterpretation,
    build_causal_slice,
    freeze_replay_state,
)


def dt(hour: int, minute: int = 0) -> datetime:
    return datetime(2025, 1, 1, hour, minute, tzinfo=UTC)


def observation(
    observation_id: str,
    *,
    published_at: datetime,
    first_seen_at: datetime,
    available_at: datetime,
) -> dict:
    return {
        "observation_id": observation_id,
        "content_hash": f"hash-{observation_id}",
        "published_at": published_at,
        "first_seen_at": first_seen_at,
        "available_at": available_at,
        "author_id": "alice",
    }


def test_causal_slice_excludes_future_information_before_feature_builder():
    decision = dt(1)
    past = observation(
        "past",
        published_at=dt(0, 10),
        first_seen_at=dt(0, 11),
        available_at=dt(0, 11),
    )
    future = observation(
        "future",
        published_at=dt(1, 10),
        first_seen_at=dt(1, 11),
        available_at=dt(1, 11),
    )
    market = [
        {"decision_time": dt(0, 45), "close": 10.0},
        {"decision_time": dt(1, 15), "close": 99.0},
    ]

    causal = build_causal_slice(
        decision_time=decision,
        observations=[past, future],
        market_rows=market,
    )

    assert [row["observation_id"] for row in causal.observations] == ["past"]
    assert [row["close"] for row in causal.market_rows] == [10.0]
    assert causal.max_input_available_at == dt(0, 45)


def test_clock_policy_is_explicit_and_changes_historical_availability():
    post = observation(
        "post",
        published_at=dt(0, 10),
        first_seen_at=dt(1, 10),
        available_at=dt(1, 10),
    )

    published = build_causal_slice(
        decision_time=dt(0, 30),
        observations=[post],
        availability_policy=AvailabilityPolicy.PUBLISHED,
    )
    first_seen = build_causal_slice(
        decision_time=dt(0, 30),
        observations=[post],
        availability_policy=AvailabilityPolicy.FIRST_SEEN,
    )

    assert len(published.observations) == 1
    assert len(first_seen.observations) == 0


def test_semantic_interpretation_cannot_use_future_context():
    post = observation(
        "post",
        published_at=dt(0, 10),
        first_seen_at=dt(0, 11),
        available_at=dt(0, 11),
    )
    interpretation = SemanticInterpretation(
        interpretation_id="sem-1",
        observation_id="post",
        observation_content_hash="hash-post",
        extractor_id="event-extractor",
        extractor_version="v1",
        generated_at=dt(4),
        knowledge_policy=KnowledgePolicy.HISTORICAL_CONTEXT,
        outcome_blind=True,
        grounded_in_inputs=True,
        context_max_available_at=dt(2),
        fields={"actor": "Example", "action": "announces"},
    )

    with pytest.raises(ValueError, match="after decision_time"):
        build_causal_slice(
            decision_time=dt(1),
            observations=[post],
            interpretations=[interpretation],
        )


def test_retroactive_document_only_extraction_may_be_generated_later_but_not_use_future_context():
    post = observation(
        "post",
        published_at=dt(0, 10),
        first_seen_at=dt(0, 11),
        available_at=dt(0, 11),
    )
    interpretation = SemanticInterpretation(
        interpretation_id="sem-1",
        observation_id="post",
        observation_content_hash="hash-post",
        extractor_id="document-only-event-extractor",
        extractor_version="v1",
        generated_at=dt(4),
        knowledge_policy=KnowledgePolicy.DOCUMENT_ONLY,
        outcome_blind=True,
        grounded_in_inputs=True,
        context_max_available_at=dt(0, 11),
        fields={"actor": "Example", "action": "announces"},
    )

    causal = build_causal_slice(
        decision_time=dt(1),
        observations=[post],
        interpretations=[interpretation],
    )
    assert [item.interpretation_id for item in causal.interpretations] == ["sem-1"]


def test_frozen_state_hash_depends_only_on_causal_scientific_inputs():
    post = observation(
        "post",
        published_at=dt(0, 10),
        first_seen_at=dt(0, 11),
        available_at=dt(0, 11),
    )
    future = observation(
        "future",
        published_at=dt(2),
        first_seen_at=dt(2),
        available_at=dt(2),
    )

    def information_builder(rows, interpretations):
        return {
            "message_count": len(rows),
            "semantic_count": len(interpretations),
        }

    def market_builder(rows):
        return {"last_close": rows[-1]["close"] if rows else None}

    kwargs = dict(
        replay_type=ReplayType.STATE,
        domain="trading",
        subject_id="BTCUSDT",
        decision_time=dt(1),
        observations=[post, future],
        interpretations=[],
        market_rows=[
            {"decision_time": dt(0, 45), "close": 100.0},
            {"decision_time": dt(2), "close": 200.0},
        ],
        information_builder=information_builder,
        market_builder=market_builder,
        representation_version="state-v1",
        dataset_manifest_ids=["manifest-1"],
        code_revision="abc123",
    )
    state_a = freeze_replay_state(**kwargs, frozen_at=dt(3))
    state_b = freeze_replay_state(**kwargs, frozen_at=dt(4))

    assert state_a.state_hash == state_b.state_hash
    assert state_a.information_state["message_count"] == 1
    assert state_a.market_state["last_close"] == 100.0
    assert state_a.max_input_available_at <= state_a.decision_time


def test_causal_slice_deduplicates_same_observation_id_before_reducers():
    post = observation(
        "same",
        published_at=dt(0, 10),
        first_seen_at=dt(0, 11),
        available_at=dt(0, 11),
    )
    causal = build_causal_slice(
        decision_time=dt(1),
        observations=[post, dict(post)],
    )
    assert len(causal.observations) == 1


def test_document_only_interpretation_fingerprint_ignores_research_generation_time():
    post = observation(
        "post",
        published_at=dt(0, 10),
        first_seen_at=dt(0, 11),
        available_at=dt(0, 11),
    )

    def interpretation(generated_at):
        return SemanticInterpretation(
            interpretation_id="sem-1",
            observation_id="post",
            observation_content_hash="hash-post",
            extractor_id="extractor",
            extractor_version="v1",
            generated_at=generated_at,
            knowledge_policy=KnowledgePolicy.DOCUMENT_ONLY,
            outcome_blind=True,
            grounded_in_inputs=True,
            context_max_available_at=dt(0, 11),
            fields={"event_type": "announcement"},
        )

    def info(rows, interpretations):
        return {"events": len(interpretations)}

    def market(rows):
        return {}

    common = dict(
        replay_type=ReplayType.EVENT,
        domain="trading",
        subject_id="BTCUSDT",
        decision_time=dt(1),
        observations=[post],
        market_rows=[],
        information_builder=info,
        market_builder=market,
        representation_version="events-v1",
        dataset_manifest_ids=["manifest"],
        code_revision="abc",
    )
    a = freeze_replay_state(
        **common,
        interpretations=[interpretation(dt(3))],
        frozen_at=dt(5),
    )
    b = freeze_replay_state(
        **common,
        interpretations=[interpretation(dt(4))],
        frozen_at=dt(6),
    )
    assert a.state_hash == b.state_hash
