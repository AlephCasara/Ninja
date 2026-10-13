from __future__ import annotations

from typing import Any

from ninja_labs.adapters import arctic_shift


class DummyClient:
    pass


def _row(post_id: str, created_utc: int) -> dict[str, Any]:
    return {
        "id": post_id,
        "created_utc": created_utc,
        "author": "alice",
        "retrieved_on": created_utc + 1,
        "subreddit": "Bitcoin",
        "title": "BTC",
        "selftext": "",
        "url": "https://example.invalid",
    }


def test_full_page_is_recursively_split(monkeypatch):
    calls: list[tuple[int, int]] = []

    def fake_request(client, path, params, attempts=3):
        start = int(params["after"]) + 1
        end = int(params["before"])
        calls.append((start, end))
        if (start, end) == (0, 10):
            return [_row(f"root-{i}", i % 10) for i in range(100)]
        if (start, end) == (0, 5):
            return [_row("a", 1), _row("b", 4)]
        if (start, end) == (5, 10):
            return [_row("c", 5), _row("d", 9)]
        raise AssertionError((start, end))

    monkeypatch.setattr(arctic_shift, "_request_json", fake_request)
    rows = list(
        arctic_shift._iter_subreddit_interval(
            DummyClient(),
            subreddit="Bitcoin",
            start_epoch=0,
            end_epoch=10,
            page_limit=100,
            seen_ids=set(),
        )
    )
    assert [row["id"] for row in rows] == ["a", "b", "c", "d"]
    assert calls == [(0, 10), (0, 5), (5, 10)]


def test_query_timeout_is_recursively_split(monkeypatch):
    def fake_request(client, path, params, attempts=3):
        start = int(params["after"]) + 1
        end = int(params["before"])
        if (start, end) == (0, 10):
            raise arctic_shift.ArcticShiftQueryTimeout("Query timed out")
        return [_row(f"{start}-{end}", start)]

    monkeypatch.setattr(arctic_shift, "_request_json", fake_request)
    rows = list(
        arctic_shift._iter_subreddit_interval(
            DummyClient(),
            subreddit="Bitcoin",
            start_epoch=0,
            end_epoch=10,
            page_limit=100,
            seen_ids=set(),
        )
    )
    assert len(rows) == 2
    assert {row["created_utc"] for row in rows} == {0, 5}
