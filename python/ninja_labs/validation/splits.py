from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timedelta

SplitWindow = tuple[datetime, datetime]


def _validate_splits(splits: Mapping[str, SplitWindow]) -> list[tuple[str, datetime, datetime]]:
    if not splits:
        raise ValueError("splits must not be empty")
    ordered = sorted(
        ((name, window[0], window[1]) for name, window in splits.items()),
        key=lambda item: item[1],
    )
    previous_end: datetime | None = None
    for name, start, end in ordered:
        if start >= end:
            raise ValueError(f"split {name!r} must have start < end")
        if previous_end is not None and start < previous_end:
            raise ValueError("split windows must not overlap")
        previous_end = end
    return ordered


def assign_purged_split(
    *,
    decision_time: datetime,
    label_end_time: datetime,
    splits: Mapping[str, SplitWindow],
    embargo: timedelta = timedelta(0),
) -> str:
    """Assign a sample while enforcing label purging and boundary embargo.

    Split windows are half-open: ``[start, end)``.

    A sample is ``purged`` when its forward label reaches past the end of the
    split that contains its decision time. For every split except the first,
    the leading ``embargo`` interval is excluded and reported as ``embargoed``.
    This prevents a headline experiment from silently allowing labels or nearby
    dependence to leak across chronological boundaries.
    """

    if decision_time.tzinfo is None or label_end_time.tzinfo is None:
        raise ValueError("decision_time and label_end_time must be timezone-aware")
    if label_end_time < decision_time:
        raise ValueError("label_end_time must not precede decision_time")
    if embargo < timedelta(0):
        raise ValueError("embargo must not be negative")

    ordered = _validate_splits(splits)
    for index, (name, start, end) in enumerate(ordered):
        if start <= decision_time < end:
            if index > 0 and decision_time < start + embargo:
                return "embargoed"
            if label_end_time > end:
                return "purged"
            return name
    return "outside"


def split_counts(
    samples: list[tuple[datetime, datetime]],
    *,
    splits: Mapping[str, SplitWindow],
    embargo: timedelta = timedelta(0),
) -> dict[str, int]:
    counts: dict[str, int] = {}
    for decision_time, label_end_time in samples:
        assignment = assign_purged_split(
            decision_time=decision_time,
            label_end_time=label_end_time,
            splits=splits,
            embargo=embargo,
        )
        counts[assignment] = counts.get(assignment, 0) + 1
    return dict(sorted(counts.items()))
