from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from ninja_labs.util import parse_utc, sha256_file


class ArcticShiftAuditError(RuntimeError):
    pass


def repair_partial_jsonl_tail(path: Path) -> int:
    """Truncate only a definitely incomplete final JSONL record.

    A valid JSONL file ends in a newline. If a crash left a partial tail, retain
    every complete line and remove bytes after the final newline. A non-empty
    file containing no newline is not repaired automatically because there is no
    complete record we can prove safe to preserve.
    """

    if not path.exists() or path.stat().st_size == 0:
        return 0
    with path.open("rb+") as handle:
        handle.seek(0, 2)
        size = handle.tell()
        handle.seek(size - 1)
        if handle.read(1) == b"\n":
            return 0

        scan = min(size, 1024 * 1024)
        handle.seek(size - scan)
        tail = handle.read(scan)
        last_newline = tail.rfind(b"\n")
        if last_newline < 0:
            raise ArcticShiftAuditError(
                f"cannot safely repair {path}: non-empty file has no complete newline-terminated record in the final {scan} bytes"
            )
        truncate_at = size - scan + last_newline + 1
        removed = size - truncate_at
        handle.truncate(truncate_at)
        return removed


def audit_subreddit_posts_jsonl(
    *,
    path: Path,
    subreddit: str,
    after: datetime,
    before: datetime,
) -> dict[str, Any]:
    """Audit raw canonical JSONL before it is accepted as a dataset source."""

    if not path.is_file():
        raise FileNotFoundError(path)
    start = parse_utc(after)
    end = parse_utc(before)
    if start >= end:
        raise ValueError("after must precede before")

    file_size = path.stat().st_size
    ends_with_newline = True
    if file_size:
        with path.open("rb") as handle:
            handle.seek(-1, 2)
            ends_with_newline = handle.read(1) == b"\n"

    seen_ids: set[str] = set()
    rows = 0
    duplicate_ids = 0
    malformed_rows = 0
    missing_required = 0
    wrong_subreddit = 0
    outside_interval = 0
    out_of_order = 0
    missing_retrieved_on = 0
    first_seen_before_published = 0
    min_created: datetime | None = None
    max_created: datetime | None = None
    previous_created: datetime | None = None

    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            rows += 1
            try:
                raw = json.loads(line)
            except json.JSONDecodeError:
                malformed_rows += 1
                continue
            if not isinstance(raw, dict):
                malformed_rows += 1
                continue

            post_id = str(raw.get("id") or "")
            created_raw = raw.get("created_utc")
            if not post_id or created_raw is None:
                missing_required += 1
                continue
            try:
                created = parse_utc(created_raw)
            except (TypeError, ValueError, OverflowError):
                malformed_rows += 1
                continue

            if post_id in seen_ids:
                duplicate_ids += 1
            else:
                seen_ids.add(post_id)

            if raw.get("subreddit") != subreddit:
                wrong_subreddit += 1
            if not (start <= created < end):
                outside_interval += 1
            if previous_created is not None and created < previous_created:
                out_of_order += 1
            previous_created = created
            min_created = created if min_created is None else min(min_created, created)
            max_created = created if max_created is None else max(max_created, created)

            retrieved_raw = raw.get("retrieved_on")
            if retrieved_raw is None:
                missing_retrieved_on += 1
            else:
                try:
                    retrieved = parse_utc(retrieved_raw)
                except (TypeError, ValueError, OverflowError):
                    malformed_rows += 1
                else:
                    if retrieved < created:
                        first_seen_before_published += 1

    passed = all(
        value == 0
        for value in (
            malformed_rows,
            missing_required,
            duplicate_ids,
            wrong_subreddit,
            outside_interval,
            out_of_order,
            first_seen_before_published,
        )
    ) and ends_with_newline

    return {
        "schema_version": 1,
        "kind": "arctic-shift-jsonl-source-audit",
        "passed": passed,
        "path": str(path),
        "subreddit": subreddit,
        "after": start.isoformat().replace("+00:00", "Z"),
        "before": end.isoformat().replace("+00:00", "Z"),
        "bytes": file_size,
        "sha256": sha256_file(path),
        "rows": rows,
        "unique_ids": len(seen_ids),
        "duplicate_ids": duplicate_ids,
        "malformed_rows": malformed_rows,
        "missing_required_rows": missing_required,
        "wrong_subreddit_rows": wrong_subreddit,
        "outside_interval_rows": outside_interval,
        "out_of_order_rows": out_of_order,
        "missing_retrieved_on_rows": missing_retrieved_on,
        "first_seen_before_published_rows": first_seen_before_published,
        "ends_with_newline": ends_with_newline,
        "min_created_at": min_created.isoformat().replace("+00:00", "Z") if min_created else None,
        "max_created_at": max_created.isoformat().replace("+00:00", "Z") if max_created else None,
    }
