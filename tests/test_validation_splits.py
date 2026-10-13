from __future__ import annotations

from datetime import UTC, datetime, timedelta

from ninja_labs.validation.splits import assign_purged_split


def test_cross_boundary_labels_are_purged_and_leading_boundary_is_embargoed():
    splits = {
        "train": (
            datetime(2025, 1, 1, tzinfo=UTC),
            datetime(2025, 2, 1, tzinfo=UTC),
        ),
        "validation": (
            datetime(2025, 2, 1, tzinfo=UTC),
            datetime(2025, 3, 1, tzinfo=UTC),
        ),
    }
    embargo = timedelta(hours=24)

    assert (
        assign_purged_split(
            decision_time=datetime(2025, 1, 31, 18, tzinfo=UTC),
            label_end_time=datetime(2025, 2, 1, 18, tzinfo=UTC),
            splits=splits,
            embargo=embargo,
        )
        == "purged"
    )
    assert (
        assign_purged_split(
            decision_time=datetime(2025, 2, 1, 12, tzinfo=UTC),
            label_end_time=datetime(2025, 2, 1, 18, tzinfo=UTC),
            splits=splits,
            embargo=embargo,
        )
        == "embargoed"
    )
    assert (
        assign_purged_split(
            decision_time=datetime(2025, 2, 2, 12, tzinfo=UTC),
            label_end_time=datetime(2025, 2, 2, 18, tzinfo=UTC),
            splits=splits,
            embargo=embargo,
        )
        == "validation"
    )
