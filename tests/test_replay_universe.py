from __future__ import annotations

from datetime import UTC, datetime

from ninja_labs.replay import UniverseCandidateSnapshot, freeze_point_in_time_universe


def dt(day: int) -> datetime:
    return datetime(2025, 1, day, tzinfo=UTC)


def snapshot(
    subject: str,
    *,
    as_of: int,
    start: int,
    end: int | None = None,
    liquid: bool = True,
) -> UniverseCandidateSnapshot:
    return UniverseCandidateSnapshot(
        subject_id=subject,
        attributes_as_of=dt(as_of),
        eligible_from=dt(start),
        eligible_until=dt(end) if end is not None else None,
        attributes={"liquid": liquid},
        evidence_ref=f"fixture:{subject}:{as_of}",
    )


def test_point_in_time_universe_excludes_future_listings_and_past_delistings():
    universe = freeze_point_in_time_universe(
        as_of=dt(5),
        domain="trading",
        eligibility_rule_id="listed-and-liquid-v1",
        candidate_snapshots=[
            snapshot("SURVIVOR", as_of=4, start=1),
            snapshot("FUTURE_100X", as_of=10, start=10),
            snapshot("DELISTED", as_of=3, start=1, end=4),
            snapshot("ILLIQUID", as_of=4, start=1, liquid=False),
        ],
        eligibility_predicate=lambda attrs: bool(attrs["liquid"]),
        dataset_manifest_ids=["assets-v1"],
        frozen_at=dt(20),
    )

    assert universe.member_ids == ("SURVIVOR",)


def test_later_candidate_snapshot_does_not_rewrite_earlier_universe():
    candidates = [
        snapshot("ASSET", as_of=2, start=1, liquid=True),
        snapshot("ASSET", as_of=8, start=1, liquid=False),
    ]
    early = freeze_point_in_time_universe(
        as_of=dt(5),
        domain="trading",
        eligibility_rule_id="liquid-v1",
        candidate_snapshots=candidates,
        eligibility_predicate=lambda attrs: bool(attrs["liquid"]),
        dataset_manifest_ids=["assets-v1"],
    )
    late = freeze_point_in_time_universe(
        as_of=dt(9),
        domain="trading",
        eligibility_rule_id="liquid-v1",
        candidate_snapshots=candidates,
        eligibility_predicate=lambda attrs: bool(attrs["liquid"]),
        dataset_manifest_ids=["assets-v1"],
    )

    assert early.member_ids == ("ASSET",)
    assert late.member_ids == ()
    assert early.universe_hash != late.universe_hash
