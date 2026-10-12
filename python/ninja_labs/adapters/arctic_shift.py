from __future__ import annotations

import time
from collections.abc import Iterator
from datetime import datetime
from typing import Any

import httpx

from ninja_labs.util import parse_utc

BASE_URL = "https://arctic-shift.photon-reddit.com"
POST_FIELDS = "id,author,created_utc,retrieved_on,subreddit,title,selftext,url"


class ArcticShiftError(RuntimeError):
    pass


def _request_json(
    client: httpx.Client,
    path: str,
    params: dict[str, Any],
    *,
    attempts: int = 5,
) -> Any:
    delay = 1.0
    for attempt in range(attempts):
        response = client.get(path, params=params)
        if response.status_code == 429 or response.status_code >= 500:
            if attempt + 1 == attempts:
                response.raise_for_status()
            retry_after = response.headers.get("retry-after")
            wait = float(retry_after) if retry_after else delay
            time.sleep(min(wait, 30.0))
            delay *= 2.0
            continue
        response.raise_for_status()
        payload = response.json()
        if isinstance(payload, dict) and payload.get("error"):
            raise ArcticShiftError(str(payload["error"]))
        return payload
    raise ArcticShiftError("Arctic Shift request exhausted retries")


def iter_posts(
    *,
    subreddits: list[str],
    after: datetime,
    before: datetime,
    page_limit: int = 100,
    timeout_seconds: float = 60.0,
) -> Iterator[dict[str, Any]]:
    """Yield historical posts in ascending event-time order.

    Arctic Shift has no uptime guarantee. Pagination intentionally advances on
    created_utc and deduplicates IDs. E1 uses subreddit-bounded post streams,
    where more than 100 posts in one second is not expected. If that assumption
    becomes false, the acquisition manifest must flag the source interval and
    the adapter should move to archive/bulk extraction rather than silently
    pretending the page cursor is lossless.
    """

    headers = {
        "User-Agent": "AlephCasara-Ninja/0.1 research contact via GitHub",
        "Accept": "application/json",
    }
    start_epoch = int(after.timestamp())
    end_epoch = int(before.timestamp())

    with httpx.Client(
        base_url=BASE_URL,
        headers=headers,
        timeout=timeout_seconds,
        follow_redirects=True,
    ) as client:
        for subreddit in subreddits:
            cursor = start_epoch
            seen_ids: set[str] = set()
            while cursor < end_epoch:
                params = {
                    "subreddit": subreddit,
                    "after": cursor,
                    "before": end_epoch,
                    "sort": "asc",
                    "limit": page_limit,
                    "fields": POST_FIELDS,
                }
                payload = _request_json(client, "/api/posts/search", params)
                if isinstance(payload, dict):
                    rows = payload.get("data", [])
                elif isinstance(payload, list):
                    rows = payload
                else:
                    raise ArcticShiftError(
                        f"unexpected Arctic Shift response type: {type(payload)!r}"
                    )
                if not rows:
                    break

                last_timestamp = cursor
                emitted = 0
                for row in rows:
                    post_id = str(row.get("id") or "")
                    created_raw = row.get("created_utc")
                    if not post_id or created_raw is None:
                        continue
                    created_at = parse_utc(created_raw)
                    created_epoch = int(created_at.timestamp())
                    last_timestamp = max(last_timestamp, created_epoch)
                    if created_epoch >= end_epoch or post_id in seen_ids:
                        continue
                    seen_ids.add(post_id)
                    emitted += 1
                    yield row

                next_cursor = last_timestamp
                if next_cursor <= cursor:
                    next_cursor = cursor + 1
                cursor = next_cursor
                if emitted == 0 and cursor >= end_epoch:
                    break
