from __future__ import annotations

import httpx

from ninja_labs.adapters import arctic_shift_stream
from ninja_labs.util import parse_utc


class _Response:
    is_error = False

    def json(self):
        return {"data": []}


class _Client:
    calls = 0

    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def get(self, *args, **kwargs):
        type(self).calls += 1
        if type(self).calls == 1:
            raise httpx.RemoteProtocolError("simulated incomplete chunked read")
        return _Response()


def test_stream_downloader_retries_transient_transport_errors(monkeypatch, tmp_path):
    _Client.calls = 0
    monkeypatch.setattr(arctic_shift_stream.httpx, "Client", _Client)
    monkeypatch.setattr(arctic_shift_stream.time, "sleep", lambda _: None)

    output = tmp_path / "posts.jsonl"
    report = arctic_shift_stream.download_subreddit_posts_jsonl(
        subreddit="Bitcoin",
        after=parse_utc("2025-01-01T00:00:00Z"),
        before=parse_utc("2025-01-02T00:00:00Z"),
        output_path=output,
        request_interval_seconds=0.0,
    )

    assert report["requests"] == 2
    assert report["retries"] == 1
    assert report["downloaded_rows"] == 0
    assert output.is_file()
