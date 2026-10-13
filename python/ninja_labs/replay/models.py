from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Mapping

from ninja_labs.util import iso_utc, parse_utc


class ReplayType(str, Enum):
    STATE = "state"
    EVENT = "event"
    PROPAGATION = "propagation"
    STRATEGY_OVERLAY = "strategy_overlay"


class AvailabilityPolicy(str, Enum):
    EXPLICIT = "explicit_available_at"
    PUBLISHED = "published"
    FIRST_SEEN = "first_seen"


class KnowledgePolicy(str, Enum):
    DOCUMENT_ONLY = "document_only"
    HISTORICAL_CONTEXT = "historical_context"
    PROSPECTIVE = "prospective"


@dataclass(frozen=True, slots=True)
class SemanticInterpretation:
    interpretation_id: str
    observation_id: str
    observation_content_hash: str
    extractor_id: str
    extractor_version: str
    generated_at: datetime
    knowledge_policy: KnowledgePolicy
    outcome_blind: bool
    grounded_in_inputs: bool
    fields: Mapping[str, Any]
    context_max_available_at: datetime | None = None
    prompt_hash: str | None = None
    model_id: str | None = None

    def validate_for(
        self,
        *,
        decision_time: datetime,
        observation_content_hash: str,
    ) -> None:
        decision_time = parse_utc(decision_time)
        if self.observation_content_hash != observation_content_hash:
            raise ValueError("semantic interpretation content hash does not match observation")
        if not self.outcome_blind:
            raise ValueError("semantic interpretation is not outcome-blind")
        if not self.grounded_in_inputs:
            raise ValueError("semantic interpretation is not grounded in its declared inputs")
        if (
            self.context_max_available_at is not None
            and parse_utc(self.context_max_available_at) > decision_time
        ):
            raise ValueError("semantic interpretation used context from after decision_time")
        if self.knowledge_policy is KnowledgePolicy.HISTORICAL_CONTEXT and self.context_max_available_at is None:
            raise ValueError("historical_context interpretation requires context_max_available_at")
        if (
            self.knowledge_policy is KnowledgePolicy.PROSPECTIVE
            and parse_utc(self.generated_at) > decision_time
        ):
            raise ValueError("prospective interpretation was generated after decision_time")

    def scientific_record(self) -> dict[str, Any]:
        record = {
            "interpretation_id": self.interpretation_id,
            "observation_id": self.observation_id,
            "observation_content_hash": self.observation_content_hash,
            "extractor_id": self.extractor_id,
            "extractor_version": self.extractor_version,
            "knowledge_policy": self.knowledge_policy.value,
            "outcome_blind": self.outcome_blind,
            "grounded_in_inputs": self.grounded_in_inputs,
            "context_max_available_at": (
                iso_utc(self.context_max_available_at)
                if self.context_max_available_at is not None
                else None
            ),
            "prompt_hash": self.prompt_hash,
            "model_id": self.model_id,
            "fields": dict(self.fields),
        }
        if self.knowledge_policy is KnowledgePolicy.PROSPECTIVE:
            record["generated_at"] = iso_utc(self.generated_at)
        return record

    def as_record(self) -> dict[str, Any]:
        return {
            **self.scientific_record(),
            "generated_at": iso_utc(self.generated_at),
        }


@dataclass(frozen=True, slots=True)
class CausalSlice:
    decision_time: datetime
    availability_policy: AvailabilityPolicy
    observations: tuple[Mapping[str, Any], ...]
    observation_fingerprints: Mapping[str, str]
    interpretations: tuple[SemanticInterpretation, ...]
    market_rows: tuple[Mapping[str, Any], ...]
    market_fingerprints: Mapping[str, str]
    max_input_available_at: datetime | None


@dataclass(frozen=True, slots=True)
class FrozenReplayState:
    schema_version: int
    state_id: str
    state_hash: str
    replay_type: ReplayType
    domain: str
    subject_id: str
    decision_time: datetime
    availability_policy: AvailabilityPolicy
    representation_version: str
    dataset_manifest_ids: tuple[str, ...]
    code_revision: str
    observation_ids: tuple[str, ...]
    observation_fingerprints: Mapping[str, str]
    interpretation_ids: tuple[str, ...]
    interpretation_fingerprints: Mapping[str, str]
    market_fingerprints: Mapping[str, str]
    max_input_available_at: datetime | None
    information_state: Mapping[str, Any]
    market_state: Mapping[str, Any]
    frozen_at: datetime

    def as_record(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "state_id": self.state_id,
            "state_hash": self.state_hash,
            "replay_type": self.replay_type.value,
            "domain": self.domain,
            "subject_id": self.subject_id,
            "decision_time": iso_utc(self.decision_time),
            "availability_policy": self.availability_policy.value,
            "representation_version": self.representation_version,
            "dataset_manifest_ids": list(self.dataset_manifest_ids),
            "code_revision": self.code_revision,
            "observation_ids": list(self.observation_ids),
            "observation_fingerprints": dict(self.observation_fingerprints),
            "interpretation_ids": list(self.interpretation_ids),
            "interpretation_fingerprints": dict(self.interpretation_fingerprints),
            "market_fingerprints": dict(self.market_fingerprints),
            "max_input_available_at": (
                iso_utc(self.max_input_available_at)
                if self.max_input_available_at is not None
                else None
            ),
            "information_state": dict(self.information_state),
            "market_state": dict(self.market_state),
            "frozen_at": iso_utc(self.frozen_at),
        }
