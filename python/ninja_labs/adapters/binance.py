from __future__ import annotations

import time
from collections.abc import Iterator
from datetime import datetime, timedelta
from typing import Any

import httpx

from ninja_labs.util import parse_utc

BASE_URL = "https://data-api.binance.vision"


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
        return response.json()
    raise RuntimeError("Binance request exhausted retries")


def _millis(value: datetime) -> int:
    return int(value.timestamp() * 1000)


def iter_klines(
    *,
    symbol: str,
    interval: str,
    after: datetime,
    before: datetime,
    timeout_seconds: float = 60.0,
) -> Iterator[dict[str, Any]]:
    """Yield closed Binance spot klines from the public market-data API."""

    start_ms = _millis(after)
    end_ms = _millis(before)
    headers = {
        "User-Agent": "AlephCasara-Ninja/0.1 research contact via GitHub",
        "Accept": "application/json",
    }

    with httpx.Client(
        base_url=BASE_URL,
        headers=headers,
        timeout=timeout_seconds,
        follow_redirects=True,
    ) as client:
        cursor = start_ms
        while cursor < end_ms:
            payload = _request_json(
                client,
                "/api/v3/klines",
                {
                    "symbol": symbol,
                    "interval": interval,
                    "startTime": cursor,
                    "endTime": end_ms - 1,
                    "limit": 1000,
                },
            )
            if not isinstance(payload, list):
                raise RuntimeError(
                    f"unexpected Binance response type: {type(payload)!r}"
                )
            if not payload:
                break

            last_close_ms = cursor
            for row in payload:
                if len(row) < 11:
                    raise RuntimeError("malformed Binance kline row")
                open_time = parse_utc(row[0])
                close_time = parse_utc(row[6])
                if open_time >= before:
                    return
                decision_time = close_time + timedelta(milliseconds=1)
                last_close_ms = max(last_close_ms, int(close_time.timestamp() * 1000))
                yield {
                    "symbol": symbol,
                    "interval": interval,
                    "open_time": open_time,
                    "close_time": close_time,
                    "decision_time": decision_time,
                    "open": float(row[1]),
                    "high": float(row[2]),
                    "low": float(row[3]),
                    "close": float(row[4]),
                    "volume": float(row[5]),
                    "quote_volume": float(row[7]),
                    "trade_count": int(row[8]),
                    "taker_buy_base_volume": float(row[9]),
                    "taker_buy_quote_volume": float(row[10]),
                }

            next_cursor = last_close_ms + 1
            if next_cursor <= cursor:
                raise RuntimeError("Binance pagination cursor did not advance")
            cursor = next_cursor
