from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ninja_labs.util import git_commit, git_is_dirty, sha256_file, sha256_json, utc_now


def artifact_record(path: Path, *, rows: int | None = None) -> dict[str, Any]:
    record: dict[str, Any] = {
        "path": str(path),
        "sha256": sha256_file(path),
        "bytes": path.stat().st_size,
    }
    if rows is not None:
        record["rows"] = rows
    return record


def write_manifest(
    path: Path,
    *,
    manifest_id: str,
    config: dict[str, Any],
    sources: list[dict[str, Any]],
    artifacts: dict[str, dict[str, Any]],
    notes: list[str],
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema_version": 1,
        "manifest_id": manifest_id,
        "created_at": utc_now().isoformat().replace("+00:00", "Z"),
        "code_commit": git_commit(),
        "code_dirty": git_is_dirty(),
        "config": config,
        "sources": sources,
        "artifacts": artifacts,
        "notes": notes,
    }
    payload["manifest_sha256"] = sha256_json(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return payload
