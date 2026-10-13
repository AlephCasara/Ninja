from __future__ import annotations

import json

from ninja_labs.dataset_quality import evaluate_e1_dataset_quality
from ninja_labs.util import sha256_file


def _fixture(tmp_path, *, missing_year: bool = False, archive_fraction: float = 0.99):
    coverage = tmp_path / "coverage.json"
    rows = 10_000
    archive_rows = int(rows * archive_fraction)
    coverage.write_text(
        json.dumps(
            {
                "schema_version": 2,
                "observations": {
                    "rows": rows,
                    "unique_authors": 5000,
                    "archive_capture_rows": archive_rows,
                    "source_timestamp_rows": rows - archive_rows,
                    "archive_capture_fraction": archive_rows / rows,
                    "source_timestamp_fraction": (rows - archive_rows) / rows,
                    "first_seen_before_published_rows": 0,
                    "rows_by_year": {} if missing_year else {"2021": rows},
                    "rows_by_community": {"Bitcoin": 4000, "CryptoCurrency": 6000},
                    "retrieval_lag": {
                        "rows": archive_rows,
                        "p50_seconds": 20.0,
                        "p95_seconds": 90.0,
                        "p99_seconds": 180.0,
                    },
                },
                "market": {
                    "gap_count": 0,
                    "coverage_fraction_inside_observed_span": 1.0,
                },
                "attention": {"nonzero_fraction": 0.75},
                "aligned": {
                    "future_window_rows": 0,
                    "future_observation_rows": 0,
                    "rows_by_split": {
                        "train": 96,
                        "validation": 96,
                        "untouched_test": 96,
                    },
                },
            }
        ),
        encoding="utf-8",
    )
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "manifest_id": "fixture-dataset",
                "config": {
                    "splits": {
                        "train": {
                            "start": "2021-01-01T00:00:00Z",
                            "end": "2021-01-02T00:00:00Z",
                        },
                        "validation": {
                            "start": "2021-01-02T00:00:00Z",
                            "end": "2021-01-03T00:00:00Z",
                        },
                        "untouched_test": {
                            "start": "2021-01-03T00:00:00Z",
                            "end": "2021-01-04T00:00:00Z",
                        },
                    }
                },
                "artifacts": {
                    "coverage": {
                        "path": str(coverage),
                        "sha256": sha256_file(coverage),
                        "bytes": coverage.stat().st_size,
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    config = tmp_path / "e1.toml"
    config.write_text(
        """
[experiment]
base_interval = "15m"

[data_quality]
min_archive_capture_fraction = 0.95
max_source_timestamp_fraction = 0.05
required_years = [2021]
min_observations_per_year = 1000
required_communities = ["Bitcoin", "CryptoCurrency"]
min_observations_per_community = 1000
min_market_span_coverage_fraction = 0.9999
min_aligned_split_coverage_fraction = 0.999
min_nonzero_attention_fraction = 0.05
""".strip()
        + "\n",
        encoding="utf-8",
    )
    return manifest, config


def test_dataset_quality_gate_accepts_structurally_complete_fixture(tmp_path):
    manifest, config = _fixture(tmp_path)
    result = evaluate_e1_dataset_quality(
        manifest_path=manifest,
        config_path=config,
        output_path=tmp_path / "quality.json",
    )
    assert result["passed"] is True
    assert result["status"] == "ACCEPTED"
    assert all(check["passed"] for check in result["checks"].values())
    assert result["diagnostics"]["retrieval_lag"]["p95_seconds"] == 90.0


def test_dataset_quality_gate_rejects_missing_required_year(tmp_path):
    manifest, config = _fixture(tmp_path, missing_year=True)
    result = evaluate_e1_dataset_quality(
        manifest_path=manifest,
        config_path=config,
        output_path=tmp_path / "quality.json",
    )
    assert result["passed"] is False
    assert result["status"] == "REJECTED"
    assert result["checks"]["year_coverage"]["passed"] is False


def test_dataset_quality_gate_rejects_weak_archive_timestamp_coverage(tmp_path):
    manifest, config = _fixture(tmp_path, archive_fraction=0.80)
    result = evaluate_e1_dataset_quality(
        manifest_path=manifest,
        config_path=config,
        output_path=tmp_path / "quality.json",
    )
    assert result["passed"] is False
    assert result["checks"]["archive_capture_fraction"]["passed"] is False
    assert result["checks"]["source_timestamp_fraction"]["passed"] is False
