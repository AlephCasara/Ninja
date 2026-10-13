from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence
from datetime import datetime
from typing import Any

from ninja_labs.replay.models import (
    AvailabilityPolicy,
    CausalSlice,
    FrozenReplayState,
    ReplayType,
    SemanticInterpretation,
)
from ninja_labs.util import iso_utc, parse_utc, sha256_json, utc_now

InformationBuilder = Callable[
    [Sequence[Mapping[str, Any]], Sequence[SemanticInterpretation]],
    Mapping[str, Any],
]
MarketBuilder = Callable[[Sequence[Mapping[str, Any]]], Mapping[str, Any]]


def observation_causal_time(
    observation: Mapping[str, Any],
    policy: AvailabilityPolicy,
) -> datetime:
    if policy is AvailabilityPolicy.EXPLICIT:
        field = "available_at"
    elif policy is AvailabilityPolicy.PUBLISHED:
        field = "published_at"
    elif policy is AvailabilityPolicy.FIRST_SEEN:
        field = "first_seen_at"
    else:  # pragma: no cover - Enum makes this defensive only.
        raise ValueError(f"unsupported availability policy: {policy}")

    value = observation.get(field)
    if value is None:
        raise ValueError(
            f"observation {observation.get('observation_id', '<unknown>')} has no {field}"
        )
    return parse_utc(value)


def build_causal_slice(
    *,
    decision_time: datetime,
    observations: Iterable[Mapping[str, Any]],
    interpretations: Iterable[SemanticInterpretation] = (),
    market_rows: Iterable[Mapping[str, Any]] = (),
    availability_policy: AvailabilityPolicy = AvailabilityPolicy.EXPLICIT,
    market_time_field: str = "decision_time",
) -> CausalSlice:
    """Return only inputs that could be used at ``decision_time``.

    The function is deliberately upstream of feature construction. Reducers used
    by ``freeze_replay_state`` never receive observations or market rows from the
    future.
    """

    decision = parse_utc(decision_time)
    observations_by_id: dict[str, Mapping[str, Any]] = {}
    observation_hashes: dict[str, str] = {}
    observation_times: dict[str, datetime] = {}
    input_times: list[datetime] = []

    for observation in observations:
        causal_time = observation_causal_time(observation, availability_policy)
        if causal_time > decision:
            continue
        observation_id = str(observation["observation_id"])
        content_hash = str(observation["content_hash"])
        existing_hash = observation_hashes.get(observation_id)
        if existing_hash is not None and existing_hash != content_hash:
            raise ValueError(f"observation {observation_id} has conflicting content hashes")
        if observation_id not in observations_by_id:
            observations_by_id[observation_id] = dict(observation)
            observation_hashes[observation_id] = content_hash
            observation_times[observation_id] = causal_time
            input_times.append(causal_time)

    eligible_observations = sorted(
        observations_by_id.values(),
        key=lambda row: (
            observation_times[str(row["observation_id"])],
            str(row["observation_id"]),
        ),
    )

    interpretations_by_id: dict[str, SemanticInterpretation] = {}
    for interpretation in interpretations:
        content_hash = observation_hashes.get(interpretation.observation_id)
        if content_hash is None:
            continue
        interpretation.validate_for(
            decision_time=decision,
            observation_content_hash=content_hash,
        )
        existing = interpretations_by_id.get(interpretation.interpretation_id)
        if existing is not None and sha256_json(existing.scientific_record()) != sha256_json(
            interpretation.scientific_record()
        ):
            raise ValueError(
                f"interpretation {interpretation.interpretation_id} has conflicting scientific content"
            )
        if existing is None:
            interpretations_by_id[interpretation.interpretation_id] = interpretation
            if interpretation.context_max_available_at is not None:
                input_times.append(parse_utc(interpretation.context_max_available_at))

    eligible_interpretations = sorted(
        interpretations_by_id.values(),
        key=lambda item: (item.observation_id, item.interpretation_id),
    )

    eligible_market: list[Mapping[str, Any]] = []
    for row in market_rows:
        value = row.get(market_time_field)
        if value is None:
            raise ValueError(f"market row has no {market_time_field}")
        row_time = parse_utc(value)
        if row_time <= decision:
            eligible_market.append(dict(row))
            input_times.append(row_time)

    eligible_market.sort(key=lambda row: parse_utc(row[market_time_field]))

    max_input = max(input_times) if input_times else None
    if max_input is not None and max_input > decision:
        raise AssertionError("causal slice contains future input")

    return CausalSlice(
        decision_time=decision,
        availability_policy=availability_policy,
        observations=tuple(eligible_observations),
        interpretations=tuple(eligible_interpretations),
        market_rows=tuple(eligible_market),
        max_input_available_at=max_input,
    )


def freeze_replay_state(
    *,
    replay_type: ReplayType,
    domain: str,
    subject_id: str,
    decision_time: datetime,
    observations: Iterable[Mapping[str, Any]],
    interpretations: Iterable[SemanticInterpretation],
    market_rows: Iterable[Mapping[str, Any]],
    information_builder: InformationBuilder,
    market_builder: MarketBuilder,
    representation_version: str,
    dataset_manifest_ids: Sequence[str],
    code_revision: str,
    availability_policy: AvailabilityPolicy = AvailabilityPolicy.EXPLICIT,
    market_time_field: str = "decision_time",
    frozen_at: datetime | None = None,
) -> FrozenReplayState:
    causal = build_causal_slice(
        decision_time=decision_time,
        observations=observations,
        interpretations=interpretations,
        market_rows=market_rows,
        availability_policy=availability_policy,
        market_time_field=market_time_field,
    )

    information_state = dict(
        information_builder(causal.observations, causal.interpretations)
    )
    market_state = dict(market_builder(causal.market_rows))

    observation_fingerprints = {
        str(row["observation_id"]): str(row["content_hash"])
        for row in causal.observations
    }
    observation_ids = tuple(sorted(observation_fingerprints))
    interpretation_fingerprints = {
        item.interpretation_id: sha256_json(item.scientific_record())
        for item in causal.interpretations
    }
    interpretation_ids = tuple(sorted(interpretation_fingerprints))
    scientific_record = {
        "schema_version": 1,
        "replay_type": replay_type.value,
        "domain": domain,
        "subject_id": subject_id,
        "decision_time": iso_utc(causal.decision_time),
        "availability_policy": availability_policy.value,
        "representation_version": representation_version,
        "dataset_manifest_ids": sorted(str(value) for value in dataset_manifest_ids),
        "code_revision": code_revision,
        "observation_ids": list(observation_ids),
        "observation_fingerprints": dict(sorted(observation_fingerprints.items())),
        "interpretation_ids": list(interpretation_ids),
        "interpretation_fingerprints": dict(sorted(interpretation_fingerprints.items())),
        "max_input_available_at": (
            iso_utc(causal.max_input_available_at)
            if causal.max_input_available_at is not None
            else None
        ),
        "information_state": information_state,
        "market_state": market_state,
    }
    state_hash = sha256_json(scientific_record)
    state_id = f"replay:{state_hash[:24]}"

    return FrozenReplayState(
        schema_version=1,
        state_id=state_id,
        state_hash=state_hash,
        replay_type=replay_type,
        domain=domain,
        subject_id=subject_id,
        decision_time=causal.decision_time,
        availability_policy=availability_policy,
        representation_version=representation_version,
        dataset_manifest_ids=tuple(sorted(str(value) for value in dataset_manifest_ids)),
        code_revision=code_revision,
        observation_ids=observation_ids,
        observation_fingerprints=dict(sorted(observation_fingerprints.items())),
        interpretation_ids=interpretation_ids,
        interpretation_fingerprints=dict(sorted(interpretation_fingerprints.items())),
        max_input_available_at=causal.max_input_available_at,
        information_state=information_state,
        market_state=market_state,
        frozen_at=parse_utc(frozen_at or utc_now()),
    )
