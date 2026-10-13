from __future__ import annotations

import json
from datetime import UTC, datetime

import pytest

from ninja_labs.adapters.arctic_shift_file import (
    ArcticShiftFileError,
    iter_posts_jsonl,
)


def dt(day: int) -> datetime:
    return datetime(2025, 1, day, tzinfo=UTC)


def test_jsonl_adapter_filters_time_subreddit_and_duplicates(tmp_path):
    first = tmp_path / "r_Bitcoin_posts.jsonl"
    second = tmp_path / "r_CryptoCurrency_posts.jsonl"
    rows = [
        {"id": "old", "created_utc": int(dt(1).timestamp()), "subreddit": "Bitcoin"},
        {"id": "a", "created_utc": int(dt(2).timestamp()), "subreddit": "Bitcoin"},
        {"id": "wrong", "created_utc": int(dt(2).timestamp()), "subreddit": "Other"},
    ]
    first.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
    second.write_text(
        json.dumps({"id": "a", "created_utc": int(dt(2).timestamp()), "subreddit": "CryptoCurrency"})
        + "\n"
        + json.dumps({"id": "b", "created_utc": int(dt(3).timestamp()), "subreddit": "CryptoCurrency"})
        + "\n",
        encoding="utf-8",
    )

    result = list(
        iter_posts_jsonl(
            files=[first, second],
            after=dt(2),
            before=dt(4),
            subreddits={"Bitcoin", "CryptoCurrency"},
        )
    )
    assert [row["id"] for row in result] == ["a", "b"]


def test_jsonl_adapter_rejects_invalid_json(tmp_path):
    path = tmp_path / "bad.jsonl"
    path.write_text("{not-json}\n", encoding="utf-8")
    with pytest.raises(ArcticShiftFileError, match="invalid JSONL"):
        list(
            iter_posts_jsonl(
                files=[path],
                after=dt(1),
                before=dt(4),
            )
        )
