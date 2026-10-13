from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from ninja_labs.replay import (
    AvailabilityPolicy,
    FrozenReplayState,
    PricePoint,
    ReplayType,
    compute_market_path_outcome,
)


def dt(day: int, hour: int = 0) -> datetime:
    return datetime(2025, 1, day, hour, tzinfo=UTC)


def frozen_state() -> FrozenReplayState:
    return FrozenReplayState(
        schema_version=1,
        state_id="replay:fixture",
        state_hash="f" * 64,
        replay_type=ReplayType.STATE,
        domain="trading",
        subject_id="TESTUSDT",
        decision_time=dt(1),
        availability_policy=AvailabilityPolicy.EXPLICIT,
        representation_version="v1",
        dataset_manifest_ids=("manifest",),
        code_revision="abc",
        observation_ids=(),
        observation_fingerprints={},
        interpretation_ids=(),
        interpretation_fingerprints={},
        max_input_available_at=dt(1),
        information_state={},
        market_state={},
        frozen_at=dt(10),
    )


def test_tail_labels_are_revealed_after_state_and_use_first_passage():
    state = frozen_state()
    prices = [
        PricePoint(dt(1), 1.0),
        PricePoint(dt(2), 0.8),
        PricePoint(dt(3), 2.1),
        PricePoint(dt(4), 5.2),
        PricePoint(dt(5), 11.0),
    ]

    outcome = compute_market_path_outcome(
        state=state,
        prices=prices,
        horizon_end=dt(5),
        multiples=(2, 5, 10, 50, 100),
    )
    passage = {item.multiple: item for item in outcome.first_passage}

    assert passage[2.0].hit is True
    assert passage[2.0].at == dt(3)
    assert passage[2.0].adverse_excursion_before_hit == pytest.approx(-0.2)
    assert passage[5.0].at == dt(4)
    assert passage[10.0].at == dt(5)
    assert passage[50.0].hit is False
    assert passage[100.0].hit is False
    assert outcome.max_forward_return == pytest.approx(10.0)
    assert outcome.state_hash == state.state_hash


def test_outcome_ignores_prices_beyond_horizon():
    state = frozen_state()
    outcome = compute_market_path_outcome(
        state=state,
        prices=[
            PricePoint(dt(1), 1.0),
            PricePoint(dt(2), 1.2),
            PricePoint(dt(20), 1000.0),
        ],
        horizon_end=dt(3),
        multiples=(100,),
    )

    assert outcome.max_forward_return == pytest.approx(0.2)
    assert outcome.first_passage[0].hit is False


def test_outcome_hash_does_not_depend_on_wall_clock_creation_time():
    state = frozen_state()
    prices = [PricePoint(dt(1), 1.0), PricePoint(dt(2), 2.0)]
    a = compute_market_path_outcome(
        state=state,
        prices=prices,
        horizon_end=dt(2),
        created_at=dt(10),
    )
    b = compute_market_path_outcome(
        state=state,
        prices=prices,
        horizon_end=dt(2),
        created_at=dt(11),
    )
    assert a.outcome_hash == b.outcome_hash
