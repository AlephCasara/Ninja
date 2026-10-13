from __future__ import annotations

import json
import tomllib
from datetime import datetime
from pathlib import Path
from typing import Any

from ninja_labs.phase1 import interval_seconds
from ninja_labs.util import git_commit, parse_utc, sha256_file, sha256_json, utc_now


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_toml(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        return tomllib.load(handle)


def _artifact_path(manifest_path: Path, record: dict[str, Any]) -> Path:
    path = Path(record["path"])
    if path.is_file():
        return path
    candidate = manifest_path.parent / path
    if candidate.is_file():
        return candidate
    raise FileNotFoundError(path)


def _expected_rows(start: datetime, end: datetime, interval_seconds_value: int) -> int:
    seconds = (end - start).total_seconds()
    if seconds <= 0:
        raise ValueError("split start must precede end")
    return int(seconds // interval_seconds_value)


def evaluate_e1_dataset_quality(
    *,
    manifest_path: Path,
    config_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    """Reject structurally incomplete E1 datasets before preregistration."""

    manifest = _read_json(manifest_path)
    config = _read_toml(config_path)
    policy = config.get("data_quality")
    if not isinstance(policy, dict):
        raise ValueError("E1 config requires a [data_quality] policy")

    coverage_record = manifest.get("artifacts", {}).get("coverage")
    if not isinstance(coverage_record, dict):
        raise ValueError("manifest lacks coverage artifact")
    coverage_path = _artifact_path(manifest_path, coverage_record)
    coverage = _read_json(coverage_path)

    observations = coverage.get("observations", {})
    market = coverage.get("market", {})
    attention = coverage.get("attention", {})
    aligned = coverage.get("aligned", {})
    checks: dict[str, dict[str, Any]] = {}

    def record(name: str, passed: bool, **details: Any) -> None:
        checks[name] = {"passed": bool(passed), **details}

    archive_fraction = float(observations.get("archive_capture_fraction", 0.0))
    min_archive = float(policy["min_archive_capture_fraction"])
    record(
        "archive_capture_fraction",
        archive_fraction >= min_archive,
        observed=archive_fraction,
        minimum=min_archive,
    )

    source_fraction = float(observations.get("source_timestamp_fraction", 1.0))
    max_source = float(policy["max_source_timestamp_fraction"])
    record(
        "source_timestamp_fraction",
        source_fraction <= max_source,
        observed=source_fraction,
        maximum=max_source,
    )

    first_seen_before = int(observations.get("first_seen_before_published_rows", -1))
    record(
        "timestamp_order",
        first_seen_before == 0,
        first_seen_before_published_rows=first_seen_before,
    )

    rows_by_year = observations.get("rows_by_year", {})
    required_years = [int(value) for value in policy["required_years"]]
    min_per_year = int(policy["min_observations_per_year"])
    deficient_years = {
        str(year): int(rows_by_year.get(str(year), 0))
        for year in required_years
        if int(rows_by_year.get(str(year), 0)) < min_per_year
    }
    record(
        "year_coverage",
        not deficient_years,
        required_years=required_years,
        minimum_per_year=min_per_year,
        rows_by_year=rows_by_year,
        deficient_years=deficient_years,
    )

    rows_by_community = observations.get("rows_by_community", {})
    required_communities = [str(value) for value in policy["required_communities"]]
    min_per_community = int(policy["min_observations_per_community"])
    deficient_communities = {
        community: int(rows_by_community.get(community, 0))
        for community in required_communities
        if int(rows_by_community.get(community, 0)) < min_per_community
    }
    record(
        "community_coverage",
        not deficient_communities,
        required_communities=required_communities,
        minimum_per_community=min_per_community,
        rows_by_community=rows_by_community,
        deficient_communities=deficient_communities,
    )

    market_gap_count = int(market.get("gap_count", -1))
    market_span_coverage = float(market.get("coverage_fraction_inside_observed_span", 0.0))
    min_market_span = float(policy["min_market_span_coverage_fraction"])
    record(
        "market_continuity",
        market_gap_count == 0 and market_span_coverage >= min_market_span,
        gap_count=market_gap_count,
        observed_span_coverage=market_span_coverage,
        minimum_span_coverage=min_market_span,
    )

    future_window_rows = int(aligned.get("future_window_rows", -1))
    future_observation_rows = int(aligned.get("future_observation_rows", -1))
    record(
        "causal_alignment",
        future_window_rows == 0 and future_observation_rows == 0,
        future_window_rows=future_window_rows,
        future_observation_rows=future_observation_rows,
    )

    nonzero_fraction = float(attention.get("nonzero_fraction", 0.0))
    min_nonzero = float(policy["min_nonzero_attention_fraction"])
    record(
        "attention_presence",
        nonzero_fraction >= min_nonzero,
        observed_nonzero_fraction=nonzero_fraction,
        minimum_nonzero_fraction=min_nonzero,
    )

    interval = interval_seconds(str(config["experiment"]["base_interval"]))
    manifest_splits = manifest.get("config", {}).get("splits", {})
    rows_by_split = aligned.get("rows_by_split", {})
    min_split_fraction = float(policy["min_aligned_split_coverage_fraction"])
    split_details: dict[str, Any] = {}
    splits_passed = True
    for split in ("train", "validation", "untouched_test"):
        raw = manifest_splits.get(split)
        if not isinstance(raw, dict):
            split_details[split] = {"error": "missing split in manifest"}
            splits_passed = False
            continue
        start = parse_utc(raw["start"])
        end = parse_utc(raw["end"])
        expected = _expected_rows(start, end, interval)
        observed = int(rows_by_split.get(split, 0))
        fraction = observed / expected if expected else 0.0
        split_details[split] = {
            "observed_rows": observed,
            "expected_rows": expected,
            "coverage_fraction": fraction,
        }
        if fraction < min_split_fraction or fraction > 1.000001:
            splits_passed = False
    record(
        "split_coverage",
        splits_passed,
        minimum_fraction=min_split_fraction,
        splits=split_details,
    )

    retrieval_lag = observations.get("retrieval_lag", {})
    passed = all(value["passed"] for value in checks.values())
    payload: dict[str, Any] = {
        "schema_version": 1,
        "kind": "e1-canonical-dataset-quality-gate",
        "status": "ACCEPTED" if passed else "REJECTED",
        "passed": passed,
        "created_at": utc_now().isoformat().replace("+00:00", "Z"),
        "code_commit": git_commit(),
        "dataset_manifest_id": manifest.get("manifest_id"),
        "dataset_manifest_sha256": sha256_file(manifest_path),
        "experiment_config_sha256": sha256_file(config_path),
        "coverage_sha256": sha256_file(coverage_path),
        "policy": policy,
        "checks": checks,
        "diagnostics": {
            "retrieval_lag": retrieval_lag,
            "observation_rows": int(observations.get("rows", 0)),
            "unique_authors": int(observations.get("unique_authors", 0)),
        },
        "scientific_boundary": (
            "Acceptance means the historical substrate meets preregistered structural and temporal quality thresholds. "
            "It does not imply that attention predicts markets."
        ),
    }
    payload["result_sha256"] = sha256_json(payload)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return payload
