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


class ArcticShiftQueryTimeout(ArcticShiftError):
    pass


def _response_detail(response: httpx.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        return response.text[:1000]
    if isinstance(payload, dict):
        for key in ("detail", "error", "message"):
            if payload.get(key):
                return str(payload[key])[:1000]
    return str(payload)[:1000]


def _request_json(
    client: httpx.Client,
    path: str,
    params: dict[str, Any],
    *,
    attempts: int = 3,
) -> Any:
    delay = 1.0
    for attempt in range(attempts):
        response = client.get(path, params=params)
        detail = _response_detail(response)

        if response.status_code == 429 or response.status_code >= 500:
            if attempt + 1 == attempts:
                raise ArcticShiftError(
                    f"HTTP {response.status_code} from Arctic Shift: {detail}"
                )
            retry_after = response.headers.get("retry-after")
            wait = float(retry_after) if retry_after else delay
            time.sleep(min(wait, 30.0))
            delay *= 2.0
            continue

        if response.status_code == 422 and "timed out" in detail.lower():
            if attempt + 1 == attempts:
                raise ArcticShiftQueryTimeout(detail)
            time.sleep(delay)
            delay *= 2.0
            continue

        if response.is_error:
            raise ArcticShiftError(
                f"HTTP {response.status_code} from Arctic Shift: {detail}"
            )

        payload = response.json()
        if isinstance(payload, dict) and payload.get("error"):
            detail = str(payload["error"])
            if "timed out" in detail.lower():
                raise ArcticShiftQueryTimeout(detail)
            raise ArcticShiftError(detail)
        return payload
    raise ArcticShiftError("Arctic Shift request exhausted retries")


def _rows_from_payload(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict):
        rows = payload.get("data", [])
    elif isinstance(payload, list):
        rows = payload
    else:
        raise ArcticShiftError(
            f"unexpected Arctic Shift response type: {type(payload)!r}"
        )
    if not isinstance(rows, list):
        raise ArcticShiftError("Arctic Shift response data is not a list")
    return rows


def _iter_subreddit_interval(
    client: httpx.Client,
    *,
    subreddit: str,
    start_epoch: int,
    end_epoch: int,
    page_limit: int,
    seen_ids: set[str],
) -> Iterator[dict[str, Any]]:
    """Fetch one half-open [start, end) interval without silent truncation.

    Search results are capped by the API. A full page is therefore treated as
    evidence that the interval may be truncated and is recursively bisected.
    Query timeouts are handled the same way. The overlapping API boundaries are
    filtered client-side and IDs are deduplicated globally.
    """

    if start_epoch >= end_epoch:
        return

    params = {
        "subreddit": subreddit,
        # API dates are boundary filters. One second of overlap avoids losing
        # records exactly at our left edge; the half-open filter below restores
        # the intended interval semantics.
        "after": start_epoch - 1,
        "before": end_epoch,
        "sort": "asc",
        "limit": page_limit,
        "fields": POST_FIELDS,
    }
    try:
        payload = _request_json(client, "/api/posts/search", params)
        rows = _rows_from_payload(payload)
    except ArcticShiftQueryTimeout:
        rows = []
        saturated = True
    else:
        saturated = len(rows) >= page_limit

    span = end_epoch - start_epoch
    if saturated:
        if span <= 1:
            if rows:
                in_interval = [
                    row
                    for row in rows
                    if row.get("created_utc") is not None
                    and start_epoch
                    <= int(parse_utc(row["created_utc"]).timestamp())
                    < end_epoch
                ]
                if len(in_interval) < page_limit:
                    for row in in_interval:
                        post_id = str(row.get("id") or "")
                        if post_id and post_id not in seen_ids:
                            seen_ids.add(post_id)
                            yield row
                    return
            raise ArcticShiftError(
                f"interval density exceeds safe API limit for r/{subreddit} "
                f"at epoch second {start_epoch}; use a bulk/archive source"
            )

        midpoint = start_epoch + span // 2
        yield from _iter_subreddit_interval(
            client,
            subreddit=subreddit,
            start_epoch=start_epoch,
            end_epoch=midpoint,
            page_limit=page_limit,
            seen_ids=seen_ids,
        )
        yield from _iter_subreddit_interval(
            client,
            subreddit=subreddit,
            start_epoch=midpoint,
            end_epoch=end_epoch,
            page_limit=page_limit,
            seen_ids=seen_ids,
        )
        return

    for row in rows:
        post_id = str(row.get("id") or "")
        created_raw = row.get("created_utc")
        if not post_id or created_raw is None:
            continue
        created_epoch = int(parse_utc(created_raw).timestamp())
        if not (start_epoch <= created_epoch < end_epoch):
            continue
        if post_id in seen_ids:
            continue
        seen_ids.add(post_id)
        yield row


def iter_posts(
    *,
    subreddits: list[str],
    after: datetime,
    before: datetime,
    page_limit: int = 100,
    timeout_seconds: float = 60.0,
) -> Iterator[dict[str, Any]]:
    """Yield historical posts while preserving event timestamps.

    Arctic Shift explicitly has no uptime/performance guarantee and recommends
    bulk dumps for large processing jobs. This API adapter is therefore intended
    for bounded/reproducible source slices and smoke validation. It avoids cursor
    pagination ambiguity by recursively narrowing saturated/time-out intervals.
    """

    if not 1 <= page_limit <= 100:
        raise ValueError("Arctic Shift page_limit must be between 1 and 100")

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
            seen_ids: set[str] = set()
            yield from _iter_subreddit_interval(
                client,
                subreddit=subreddit,
                start_epoch=start_epoch,
                end_epoch=end_epoch,
                page_limit=page_limit,
                seen_ids=seen_ids,
            )
