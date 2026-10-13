from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable, Sequence

from ninja_labs.replay.models import FrozenReplayState
from ninja_labs.util import iso_utc, parse_utc, sha256_json, utc_now


@dataclass(frozen=True, slots=True)
class PricePoint:
    at: datetime
    price: float


@dataclass(frozen=True, slots=True)
class FirstPassage:
    multiple: float
    hit: bool
    at: datetime | None
    seconds_from_reference: float | None
    adverse_excursion_before_hit: float

    def as_record(self) -> dict[str, Any]:
        return {
            "multiple": self.multiple,
            "hit": self.hit,
            "at": iso_utc(self.at) if self.at is not None else None,
            "seconds_from_reference": self.seconds_from_reference,
            "adverse_excursion_before_hit": self.adverse_excursion_before_hit,
        }


@dataclass(frozen=True, slots=True)
class ReplayOutcome:
    schema_version: int
    outcome_id: str
    outcome_hash: str
    state_id: str
    state_hash: str
    subject_id: str
    decision_time: datetime
    reference_time: datetime
    reference_price: float
    reference_delay_seconds: float
    max_reference_delay_seconds: float
    max_observed_path_gap_seconds: float
    max_path_gap_seconds: float
    horizon_end: datetime
    outcome_definition_id: str
    reference_policy: str
    terminal_return: float
    max_forward_return: float
    min_forward_return: float
    realized_variation: float
    first_passage: tuple[FirstPassage, ...]
    created_at: datetime

    def as_record(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "outcome_id": self.outcome_id,
            "outcome_hash": self.outcome_hash,
            "state_id": self.state_id,
            "state_hash": self.state_hash,
            "subject_id": self.subject_id,
            "decision_time": iso_utc(self.decision_time),
            "reference_time": iso_utc(self.reference_time),
            "reference_price": self.reference_price,
            "reference_delay_seconds": self.reference_delay_seconds,
            "max_reference_delay_seconds": self.max_reference_delay_seconds,
            "max_observed_path_gap_seconds": self.max_observed_path_gap_seconds,
            "max_path_gap_seconds": self.max_path_gap_seconds,
            "horizon_end": iso_utc(self.horizon_end),
            "outcome_definition_id": self.outcome_definition_id,
            "reference_policy": self.reference_policy,
            "terminal_return": self.terminal_return,
            "max_forward_return": self.max_forward_return,
            "min_forward_return": self.min_forward_return,
            "realized_variation": self.realized_variation,
            "first_passage": [value.as_record() for value in self.first_passage],
            "created_at": iso_utc(self.created_at),
        }


def compute_market_path_outcome(
    *,
    state: FrozenReplayState,
    prices: Iterable[PricePoint],
    horizon_end: datetime,
    max_reference_delay_seconds: float,
    max_path_gap_seconds: float,
    multiples: Sequence[float] = (2.0, 5.0, 10.0, 50.0, 100.0),
    outcome_definition_id: str = "market-path-v1",
    reference_policy: str = "first_at_or_after_decision",
    created_at: datetime | None = None,
) -> ReplayOutcome:
    """Reveal path outcomes after a frozen replay state.

    Tail multiples are labels on the future path. They never participate in
    ``freeze_replay_state`` and therefore cannot choose or alter the frozen
    information representation.
    """

    if reference_policy != "first_at_or_after_decision":
        raise ValueError("unsupported reference_policy")

    horizon = parse_utc(horizon_end)
    if horizon <= state.decision_time:
        raise ValueError("horizon_end must be after decision_time")
    if any(value <= 1.0 for value in multiples):
        raise ValueError("tail multiples must be greater than 1")
    if max_reference_delay_seconds < 0 or max_path_gap_seconds <= 0:
        raise ValueError("gap tolerances must be non-negative/positive")

    path_by_time: dict[str, PricePoint] = {}
    for point in prices:
        at = parse_utc(point.at)
        if not (state.decision_time <= at <= horizon):
            continue
        normalized = PricePoint(at, float(point.price))
        key = iso_utc(at)
        existing = path_by_time.get(key)
        if existing is not None and existing.price != normalized.price:
            raise ValueError(f"conflicting price observations at {key}")
        path_by_time.setdefault(key, normalized)

    path = sorted(path_by_time.values(), key=lambda point: point.at)
    if not path:
        raise ValueError("no price observations in reveal window")
    if any(point.price <= 0 for point in path):
        raise ValueError("prices must be positive")

    reference = path[0]
    reference_delay_seconds = (reference.at - state.decision_time).total_seconds()
    if reference_delay_seconds > max_reference_delay_seconds:
        raise ValueError("reference price exceeds allowed decision-time delay")

    path_gap_seconds = [
        (current.at - previous.at).total_seconds()
        for previous, current in zip(path, path[1:], strict=False)
    ]
    terminal_gap_seconds = (horizon - path[-1].at).total_seconds()
    path_gap_seconds.append(terminal_gap_seconds)
    max_observed_path_gap_seconds = max(path_gap_seconds, default=0.0)
    if max_observed_path_gap_seconds > max_path_gap_seconds:
        raise ValueError("market path contains a gap larger than allowed")

    ratios = [point.price / reference.price for point in path]
    terminal_return = ratios[-1] - 1.0
    max_forward_return = max(ratios) - 1.0
    min_forward_return = min(ratios) - 1.0

    realized_variation = 0.0
    for previous, current in zip(path, path[1:], strict=False):
        log_return = math.log(current.price / previous.price)
        realized_variation += log_return * log_return

    passage: list[FirstPassage] = []
    for multiple in sorted(set(float(value) for value in multiples)):
        hit_index: int | None = None
        for index, ratio in enumerate(ratios):
            if ratio >= multiple:
                hit_index = index
                break
        stop_index = hit_index if hit_index is not None else len(path) - 1
        adverse = min(ratios[: stop_index + 1]) - 1.0
        hit_point = path[hit_index] if hit_index is not None else None
        passage.append(
            FirstPassage(
                multiple=multiple,
                hit=hit_point is not None,
                at=hit_point.at if hit_point is not None else None,
                seconds_from_reference=(
                    (hit_point.at - reference.at).total_seconds()
                    if hit_point is not None
                    else None
                ),
                adverse_excursion_before_hit=adverse,
            )
        )

    scientific_record = {
        "schema_version": 2,
        "state_id": state.state_id,
        "state_hash": state.state_hash,
        "subject_id": state.subject_id,
        "decision_time": iso_utc(state.decision_time),
        "reference_time": iso_utc(reference.at),
        "reference_price": reference.price,
        "reference_delay_seconds": reference_delay_seconds,
        "max_reference_delay_seconds": float(max_reference_delay_seconds),
        "max_observed_path_gap_seconds": max_observed_path_gap_seconds,
        "max_path_gap_seconds": float(max_path_gap_seconds),
        "horizon_end": iso_utc(horizon),
        "outcome_definition_id": outcome_definition_id,
        "reference_policy": reference_policy,
        "terminal_return": terminal_return,
        "max_forward_return": max_forward_return,
        "min_forward_return": min_forward_return,
        "realized_variation": realized_variation,
        "first_passage": [value.as_record() for value in passage],
    }
    outcome_hash = sha256_json(scientific_record)
    return ReplayOutcome(
        schema_version=2,
        outcome_id=f"outcome:{outcome_hash[:24]}",
        outcome_hash=outcome_hash,
        state_id=state.state_id,
        state_hash=state.state_hash,
        subject_id=state.subject_id,
        decision_time=state.decision_time,
        reference_time=reference.at,
        reference_price=reference.price,
        reference_delay_seconds=reference_delay_seconds,
        max_reference_delay_seconds=float(max_reference_delay_seconds),
        max_observed_path_gap_seconds=max_observed_path_gap_seconds,
        max_path_gap_seconds=float(max_path_gap_seconds),
        horizon_end=horizon,
        outcome_definition_id=outcome_definition_id,
        reference_policy=reference_policy,
        terminal_return=terminal_return,
        max_forward_return=max_forward_return,
        min_forward_return=min_forward_return,
        realized_variation=realized_variation,
        first_passage=tuple(passage),
        created_at=parse_utc(created_at or utc_now()),
    )
