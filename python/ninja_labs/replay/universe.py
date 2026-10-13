from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from ninja_labs.util import iso_utc, parse_utc, sha256_json, utc_now

EligibilityPredicate = Callable[[Mapping[str, Any]], bool]


@dataclass(frozen=True, slots=True)
class UniverseCandidateSnapshot:
    subject_id: str
    attributes_as_of: datetime
    eligible_from: datetime
    eligible_until: datetime | None
    attributes: Mapping[str, Any]
    evidence_ref: str

    def scientific_record(self) -> dict[str, Any]:
        return {
            "subject_id": self.subject_id,
            "attributes_as_of": iso_utc(self.attributes_as_of),
            "eligible_from": iso_utc(self.eligible_from),
            "eligible_until": (
                iso_utc(self.eligible_until) if self.eligible_until is not None else None
            ),
            "attributes": dict(self.attributes),
            "evidence_ref": self.evidence_ref,
        }


@dataclass(frozen=True, slots=True)
class FrozenUniverse:
    schema_version: int
    universe_id: str
    universe_hash: str
    as_of: datetime
    domain: str
    eligibility_rule_id: str
    dataset_manifest_ids: tuple[str, ...]
    member_ids: tuple[str, ...]
    member_fingerprints: Mapping[str, str]
    frozen_at: datetime

    def as_record(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "universe_id": self.universe_id,
            "universe_hash": self.universe_hash,
            "as_of": iso_utc(self.as_of),
            "domain": self.domain,
            "eligibility_rule_id": self.eligibility_rule_id,
            "dataset_manifest_ids": list(self.dataset_manifest_ids),
            "member_ids": list(self.member_ids),
            "member_fingerprints": dict(self.member_fingerprints),
            "frozen_at": iso_utc(self.frozen_at),
        }


def freeze_point_in_time_universe(
    *,
    as_of: datetime,
    domain: str,
    eligibility_rule_id: str,
    candidate_snapshots: Iterable[UniverseCandidateSnapshot],
    eligibility_predicate: EligibilityPredicate,
    dataset_manifest_ids: Iterable[str],
    frozen_at: datetime | None = None,
) -> FrozenUniverse:
    """Freeze the eligible population using only snapshots available by ``as_of``.

    For each subject the latest candidate snapshot known by ``as_of`` is used.
    Later snapshots cannot alter earlier universes.
    """

    point = parse_utc(as_of)
    latest: dict[str, UniverseCandidateSnapshot] = {}
    for candidate in candidate_snapshots:
        attributes_as_of = parse_utc(candidate.attributes_as_of)
        eligible_from = parse_utc(candidate.eligible_from)
        eligible_until = (
            parse_utc(candidate.eligible_until)
            if candidate.eligible_until is not None
            else None
        )
        if attributes_as_of > point or eligible_from > point:
            continue
        if eligible_until is not None and point >= eligible_until:
            continue
        current = latest.get(candidate.subject_id)
        if current is None or parse_utc(current.attributes_as_of) < attributes_as_of:
            latest[candidate.subject_id] = candidate
        elif parse_utc(current.attributes_as_of) == attributes_as_of:
            if sha256_json(current.scientific_record()) != sha256_json(
                candidate.scientific_record()
            ):
                raise ValueError(
                    f"conflicting universe snapshots for {candidate.subject_id} at {iso_utc(attributes_as_of)}"
                )

    selected = {
        subject_id: candidate
        for subject_id, candidate in latest.items()
        if eligibility_predicate(candidate.attributes)
    }
    fingerprints = {
        subject_id: sha256_json(candidate.scientific_record())
        for subject_id, candidate in selected.items()
    }
    member_ids = tuple(sorted(fingerprints))
    manifests = tuple(sorted(str(value) for value in dataset_manifest_ids))
    scientific_record = {
        "schema_version": 1,
        "as_of": iso_utc(point),
        "domain": domain,
        "eligibility_rule_id": eligibility_rule_id,
        "dataset_manifest_ids": list(manifests),
        "member_ids": list(member_ids),
        "member_fingerprints": dict(sorted(fingerprints.items())),
    }
    universe_hash = sha256_json(scientific_record)
    return FrozenUniverse(
        schema_version=1,
        universe_id=f"universe:{universe_hash[:24]}",
        universe_hash=universe_hash,
        as_of=point,
        domain=domain,
        eligibility_rule_id=eligibility_rule_id,
        dataset_manifest_ids=manifests,
        member_ids=member_ids,
        member_fingerprints=dict(sorted(fingerprints.items())),
        frozen_at=parse_utc(frozen_at or utc_now()),
    )
