from __future__ import annotations

import json
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path
from typing import Any

from ninja_labs.util import parse_utc


class ArcticShiftFileError(RuntimeError):
    pass


def iter_posts_jsonl(
    *,
    files: list[Path],
    after: datetime,
    before: datetime,
    subreddits: set[str] | None = None,
) -> Iterator[dict[str, Any]]:
    """Stream Arctic Shift subreddit post JSONL files without loading them whole.

    The Arctic Shift download tool emits subreddit-specific JSONL files such as
    ``r_Bitcoin_posts.jsonl``. Filtering remains explicit so a mislabeled input
    file cannot silently contaminate the canonical E1 corpus.
    """

    start_epoch = int(after.timestamp())
    end_epoch = int(before.timestamp())
    seen_ids: set[str] = set()

    for path in files:
        if not path.is_file():
            raise ArcticShiftFileError(f"Arctic Shift JSONL file not found: {path}")

        with path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as error:
                    raise ArcticShiftFileError(
                        f"invalid JSONL in {path}:{line_number}: {error}"
                    ) from error
                if not isinstance(row, dict):
                    raise ArcticShiftFileError(
                        f"expected object in {path}:{line_number}, got {type(row)!r}"
                    )

                post_id = str(row.get("id") or "")
                created_raw = row.get("created_utc")
                subreddit = row.get("subreddit")
                if not post_id or created_raw is None:
                    continue
                if subreddits is not None and subreddit not in subreddits:
                    continue

                created_epoch = int(parse_utc(created_raw).timestamp())
                if not (start_epoch <= created_epoch < end_epoch):
                    continue
                if post_id in seen_ids:
                    continue
                seen_ids.add(post_id)
                yield row
