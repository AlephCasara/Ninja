from __future__ import annotations

import json
from datetime import UTC, datetime

import pytest

from ninja_labs.adapters.arctic_shift_audit import (
    ArcticShiftAuditError,
    audit_subreddit_posts_jsonl,
    repair_partial_jsonl_tail,
)


def _row(post_id: str, created: int, *, subreddit: str = "Bitcoin", retrieved: int | None = None):
    return {
        "id": post_id,
        "created_utc": created,
        "retrieved_on": retrieved if retrieved is not None else created + 10,
        "subreddit": subreddit,
        "author": "user",
        "title": "title",
    }


def _write(path, rows, *, final_newline: bool = True):
    text = "\n".join(json.dumps(row, sort_keys=True) for row in rows)
    if final_newline:
        text += "\n"
    path.write_text(text, encoding="utf-8")


def test_source_audit_accepts_ordered_unique_jsonl(tmp_path):
    path = tmp_path / "r_Bitcoin_posts.jsonl"
    _write(path, [_row("a", 100), _row("b", 110), _row("c", 120)])
    result = audit_subreddit_posts_jsonl(
        path=path,
        subreddit="Bitcoin",
        after=datetime.fromtimestamp(90, tz=UTC),
        before=datetime.fromtimestamp(130, tz=UTC),
    )
    assert result["passed"] is True
    assert result["rows"] == 3
    assert result["unique_ids"] == 3
    assert result["duplicate_ids"] == 0
    assert result["out_of_order_rows"] == 0
    assert result["ends_with_newline"] is True


def test_source_audit_rejects_duplicate_and_out_of_order_rows(tmp_path):
    path = tmp_path / "bad.jsonl"
    _write(path, [_row("a", 110), _row("a", 100)])
    result = audit_subreddit_posts_jsonl(
        path=path,
        subreddit="Bitcoin",
        after=datetime.fromtimestamp(90, tz=UTC),
        before=datetime.fromtimestamp(130, tz=UTC),
    )
    assert result["passed"] is False
    assert result["duplicate_ids"] == 1
    assert result["out_of_order_rows"] == 1


def test_source_audit_reports_missing_retrieved_on_without_faking_failure(tmp_path):
    path = tmp_path / "source-time.jsonl"
    row = _row("a", 100)
    row.pop("retrieved_on")
    _write(path, [row])
    result = audit_subreddit_posts_jsonl(
        path=path,
        subreddit="Bitcoin",
        after=datetime.fromtimestamp(90, tz=UTC),
        before=datetime.fromtimestamp(130, tz=UTC),
    )
    assert result["passed"] is True
    assert result["missing_retrieved_on_rows"] == 1


def test_repair_partial_tail_preserves_complete_records(tmp_path):
    path = tmp_path / "partial.jsonl"
    first = json.dumps(_row("a", 100), sort_keys=True) + "\n"
    partial = '{"id":"broken"'
    path.write_text(first + partial, encoding="utf-8")
    removed = repair_partial_jsonl_tail(path)
    assert removed == len(partial.encode("utf-8"))
    assert path.read_text(encoding="utf-8") == first


def test_repair_refuses_nonempty_file_with_no_proven_complete_record(tmp_path):
    path = tmp_path / "unsafe.jsonl"
    path.write_text('{"id":"broken"', encoding="utf-8")
    with pytest.raises(ArcticShiftAuditError, match="cannot safely repair"):
        repair_partial_jsonl_tail(path)
