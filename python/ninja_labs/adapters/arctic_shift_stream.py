from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx

from ninja_labs.adapters.arctic_shift import BASE_URL, POST_FIELDS
from ninja_labs.util import parse_utc, sha256_file


def _last_jsonl_record(path: Path) -> dict[str, Any] | None:
    if not path.exists() or path.stat().st_size == 0:
        return None
    with path.open("rb") as handle:
        handle.seek(0, 2)
        position = handle.tell()
        chunk = b""
        while position > 0 and chunk.count(b"\n") < 2:
            size = min(64 * 1024, position)
            position -= size
            handle.seek(position)
            chunk = handle.read(size) + chunk
        lines = [line for line in chunk.splitlines() if line.strip()]
        if not lines:
            return None
        return json.loads(lines[-1])


def download_subreddit_posts_jsonl(
    *,
    subreddit: str,
    after: datetime,
    before: datetime,
    output_path: Path,
    resume: bool = True,
    request_interval_seconds: float = 0.5,
    timeout_seconds: float = 90.0,
) -> dict[str, Any]:
    """Stream one subreddit using the same cursor strategy as Arctic Shift UI."""

    start_ms = int(after.timestamp() * 1000)
    end_ms = int(before.timestamp() * 1000)
    if start_ms >= end_ms:
        raise ValueError("after must precede before")
    if request_interval_seconds < 0:
        raise ValueError("request_interval_seconds must be non-negative")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if resume and output_path.exists() else "w"
    current_ms = start_ms
    existing_rows = 0
    previous_id: str | None = None
    previous_created_ms: int | None = None
    if mode == "a":
        last = _last_jsonl_record(output_path)
        if last is not None and last.get("created_utc") is not None:
            previous_id = str(last.get("id") or "") or None
            previous_created_ms = int(parse_utc(last["created_utc"]).timestamp() * 1000)
            current_ms = max(start_ms, previous_created_ms)
            with output_path.open("r", encoding="utf-8") as existing:
                existing_rows = sum(1 for _ in existing)

    headers = {
        "User-Agent": "AlephCasara-Ninja/0.1 research contact via GitHub",
        "Accept": "application/json",
    }
    downloaded_rows = 0
    requests = 0
    retries = 0

    with httpx.Client(
        base_url=BASE_URL,
        headers=headers,
        timeout=timeout_seconds,
        follow_redirects=True,
    ) as client, output_path.open(mode, encoding="utf-8") as handle:
        while current_ms < end_ms:
            params = {
                "subreddit": subreddit,
                "before": end_ms,
                "after": current_ms,
                "limit": "auto",
                "sort": "asc",
                "fields": POST_FIELDS,
                "meta-app": "ninja-canonical-download",
            }
            delay = 1.0
            payload: Any | None = None
            for attempt in range(6):
                if request_interval_seconds:
                    time.sleep(request_interval_seconds)
                requests += 1
                try:
                    response = client.get("/api/posts/search", params=params)
                except httpx.TimeoutException:
                    response = None
                if response is not None and not response.is_error:
                    payload = response.json()
                    if not (isinstance(payload, dict) and payload.get("error")):
                        break
                retries += 1
                if attempt == 5:
                    detail = response.text[:500] if response is not None else "timeout"
                    raise RuntimeError(f"Arctic Shift download failed after retries: {detail}")
                time.sleep(delay)
                delay = min(delay * 2.0, 30.0)
            if payload is None:
                raise RuntimeError("Arctic Shift returned no payload")
            rows = payload.get("data", []) if isinstance(payload, dict) else payload
            if not isinstance(rows, list):
                raise RuntimeError("unexpected Arctic Shift download payload")
            if not rows:
                break

            max_created_ms = current_ms
            wrote_this_page = 0
            for row in rows:
                if not isinstance(row, dict) or row.get("created_utc") is None:
                    continue
                created_ms = int(parse_utc(row["created_utc"]).timestamp() * 1000)
                if not (start_ms <= created_ms < end_ms):
                    continue
                row_id = str(row.get("id") or "")
                if row_id and row_id == previous_id and created_ms == previous_created_ms:
                    continue
                handle.write(
                    json.dumps(
                        row,
                        ensure_ascii=False,
                        sort_keys=True,
                        separators=(",", ":"),
                    )
                    + "\n"
                )
                previous_id = row_id or None
                previous_created_ms = created_ms
                max_created_ms = max(max_created_ms, created_ms)
                downloaded_rows += 1
                wrote_this_page += 1

            handle.flush()
            if max_created_ms <= current_ms:
                current_ms += 1000
            else:
                current_ms = max_created_ms
            if wrote_this_page == 0:
                current_ms += 1000

    total_rows = existing_rows + downloaded_rows
    return {
        "source": "arctic-shift-download-tool-compatible",
        "subreddit": subreddit,
        "after": after.isoformat(),
        "before": before.isoformat(),
        "path": str(output_path),
        "existing_rows": existing_rows,
        "downloaded_rows": downloaded_rows,
        "total_rows": total_rows,
        "requests": requests,
        "retries": retries,
        "bytes": output_path.stat().st_size if output_path.exists() else 0,
        "sha256": sha256_file(output_path) if output_path.exists() else None,
    }
