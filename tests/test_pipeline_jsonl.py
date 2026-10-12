from __future__ import annotations

import json
from datetime import UTC, datetime

from ninja_labs.pipeline import _reddit_input


def test_reddit_jsonl_mode_hashes_source_files(tmp_path):
    source = tmp_path / "r_Bitcoin_posts.jsonl"
    source.write_text(
        json.dumps(
            {
                "id": "abc",
                "created_utc": int(datetime(2025, 1, 2, tzinfo=UTC).timestamp()),
                "retrieved_on": int(datetime(2025, 1, 2, 0, 0, 5, tzinfo=UTC).timestamp()),
                "subreddit": "Bitcoin",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    rows, metadata = _reddit_input(
        {
            "mode": "jsonl",
            "subreddits": ["Bitcoin"],
            "files": [str(source)],
        },
        start=datetime(2025, 1, 1, tzinfo=UTC),
        end=datetime(2025, 1, 3, tzinfo=UTC),
    )
    assert [row["id"] for row in rows] == ["abc"]
    assert metadata["id"] == "arctic-shift-download-tool-jsonl"
    file_record = metadata["query"]["files"][0]
    assert file_record["path"] == str(source)
    assert len(file_record["sha256"]) == 64
    assert file_record["bytes"] == source.stat().st_size
