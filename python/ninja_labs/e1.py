from __future__ import annotations

import json
import math
import random
import tomllib
from collections.abc import Sequence
from datetime import datetime
from pathlib import Path
from typing import Any

import duckdb
import numpy as np
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    log_loss,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from ninja_labs.attention.estimators import seasonal_robust_attention_surprise
from ninja_labs.util import git_commit, sha256_file, sha256_json, utc_now
from ninja_labs.validation.core import benjamini_hochberg, effective_sample_size


MARKET_FEATURES = (
    "return_1",
    "rv_4",
    "rv_16",
    "rv_96",
    "log_volume",
    "volume_log_ratio_96",
    "week_sin",
    "week_cos",
)

REGRESSION_TARGETS = ("future_rv", "future_volume_surprise", "mae")
CLASSIFICATION_TARGETS = ("jump",)


def _read_toml(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        return tomllib.load(handle)


def _read_manifest(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    artifacts = payload.get("artifacts", {})
    for key in ("gold_train", "gold_validation"):
        if key not in artifacts:
            raise ValueError(f"dataset manifest is missing required artifact {key!r}")
    return payload


def _artifact_path(manifest_path: Path, record: dict[str, Any]) -> Path:
    path = Path(record["path"])
    if path.is_file():
        return path
    candidate = manifest_path.parent / path
    if candidate.is_file():
        return candidate
    raise FileNotFoundError(path)


def _load_split(path: Path, expected_split: str) -> list[dict[str, Any]]:
    con = duckdb.connect()
    rows = con.execute(
        """
        SELECT decision_time, open, high, low, close, volume,
               message_count, unique_author_count, author_hhi,
               author_entropy_normalized, split
        FROM read_parquet(?)
        ORDER BY decision_time
        """,
        [str(path)],
    ).fetchall()
    con.close()
    result: list[dict[str, Any]] = []
    for row in rows:
        split = str(row[10])
        if split != expected_split:
            raise ValueError(
                f"physical {expected_split} artifact contains split={split!r}"
            )
        result.append(
            {
                "decision_time": row[0],
                "open": float(row[1]),
                "high": float(row[2]),
                "low": float(row[3]),
                "close": float(row[4]),
                "volume": float(row[5]),
                "message_count": int(row[6]),
                "unique_author_count": int(row[7]),
                "author_hhi": float(row[8]),
                "author_entropy_normalized": float(row[9]),
                "split": split,
            }
        )
    return result


def _validate_grid(rows: Sequence[dict[str, Any]], *, seconds: int = 900) -> None:
    for previous, current in zip(rows, rows[1:]):
        delta = (current["decision_time"] - previous["decision_time"]).total_seconds()
        if delta != seconds:
            raise ValueError(
                "E1 requires a contiguous 15-minute market grid; "
                f"found gap {delta}s at {current['decision_time']}"
            )


def _rolling_rv(returns: Sequence[float | None], index: int, window: int) -> float | None:
    start = index - window + 1
    if start < 1:
        return None
    values = returns[start : index + 1]
    if any(value is None for value in values):
        return None
    return math.sqrt(sum(float(value) ** 2 for value in values))


def _median(values: Sequence[float]) -> float:
    ordered = sorted(float(value) for value in values)
    n = len(ordered)
    middle = n // 2
    if n % 2:
        return ordered[middle]
    return 0.5 * (ordered[middle - 1] + ordered[middle])


def _build_features(rows: list[dict[str, Any]], cfg: dict[str, Any]) -> None:
    closes = [row["close"] for row in rows]
    volumes = [row["volume"] for row in rows]
    counts = [float(row["message_count"]) for row in rows]
    returns: list[float | None] = [None]
    for index in range(1, len(rows)):
        returns.append(math.log(closes[index] / closes[index - 1]))

    attention_cfg = cfg["attention"]
    seasonal = seasonal_robust_attention_surprise(
        counts,
        period=int(attention_cfg["seasonal_period"]),
        cycles=int(attention_cfg["seasonal_cycles"]),
        zero_mad_policy=str(attention_cfg["zero_mad_policy"]),
    )

    for index, row in enumerate(rows):
        row["return_1"] = returns[index]
        for window in (4, 16, 96):
            row[f"rv_{window}"] = _rolling_rv(returns, index, window)
        row["log_volume"] = math.log1p(max(row["volume"], 0.0))
        if index >= 96:
            reference = volumes[index - 96 : index]
            center = _median(reference)
            row["volume_log_ratio_96"] = math.log(
                (row["volume"] + 1e-12) / (center + 1e-12)
            )
        else:
            row["volume_log_ratio_96"] = None

        dt: datetime = row["decision_time"]
        minute_of_week = dt.weekday() * 1440 + dt.hour * 60 + dt.minute
        phase = 2.0 * math.pi * minute_of_week / (7.0 * 1440.0)
        row["week_sin"] = math.sin(phase)
        row["week_cos"] = math.cos(phase)

        row["seasonal_attention_surprise"] = seasonal[index]
        if index >= 2 and all(
            seasonal[position] is not None
            for position in (index - 2, index - 1, index)
        ):
            row["attention_acceleration"] = (
                float(seasonal[index])
                - 2.0 * float(seasonal[index - 1])
                + float(seasonal[index - 2])
            )
        else:
            row["attention_acceleration"] = None
        row["author_breadth"] = (
            row["unique_author_count"] / row["message_count"]
            if row["message_count"] > 0
            else 0.0
        )


def _build_target(
    rows: Sequence[dict[str, Any]],
    index: int,
    *,
    horizon: int,
    target: str,
    jump_sigma: float,
) -> float | int | None:
    row = rows[index]
    split = row["split"]
    end = index + horizon
    if end >= len(rows):
        return None
    future = rows[index + 1 : end + 1]
    if any(item["split"] != split for item in future):
        return None

    close_now = row["close"]
    if target == "future_rv":
        previous = close_now
        total = 0.0
        for item in future:
            ret = math.log(item["close"] / previous)
            total += ret * ret
            previous = item["close"]
        return math.sqrt(total)

    if target == "future_volume_surprise":
        if index < 96:
            return None
        trailing = [rows[position]["volume"] for position in range(index - 96, index)]
        expected = _median(trailing)
        future_mean = sum(item["volume"] for item in future) / horizon
        return math.log((future_mean + 1e-12) / (expected + 1e-12))

    if target == "mae":
        return min(item["low"] / close_now - 1.0 for item in future)

    if target == "jump":
        if index < 96:
            return None
        recent_returns = [
            math.log(rows[position]["close"] / rows[position - 1]["close"])
            for position in range(index - 95, index + 1)
        ]
        sigma = float(np.std(np.asarray(recent_returns), ddof=1))
        cumulative = math.log(rows[end]["close"] / close_now)
        threshold = jump_sigma * sigma * math.sqrt(horizon)
        return int(abs(cumulative) > threshold)

    raise ValueError(f"unsupported target: {target}")


def _valid_number(value: Any) -> bool:
    return value is not None and math.isfinite(float(value))


def _matrix(
    rows: Sequence[dict[str, Any]],
    indices: Sequence[int],
    features: Sequence[str],
) -> np.ndarray:
    return np.asarray(
        [[float(rows[index][feature]) for feature in features] for index in indices],
        dtype=float,
    )


def _paired_block_inference(
    differences: Sequence[float],
    *,
    block_size: int,
    resamples: int,
    seed: int,
) -> dict[str, float]:
    values = [float(value) for value in differences]
    if not values:
        raise ValueError("loss differences must not be empty")
    block_size = min(block_size, len(values))
    blocks = [values[start : start + block_size] for start in range(0, len(values), block_size)]
    rng = random.Random(seed)

    bootstrap_means: list[float] = []
    for _ in range(resamples):
        sample: list[float] = []
        while len(sample) < len(values):
            sample.extend(rng.choice(blocks))
        bootstrap_means.append(sum(sample[: len(values)]) / len(values))
    bootstrap_means.sort()
    low = bootstrap_means[int(0.025 * (resamples - 1))]
    high = bootstrap_means[int(0.975 * (resamples - 1))]

    null_means: list[float] = []
    for _ in range(resamples):
        total = 0.0
        count = 0
        for block in blocks:
            sign = -1.0 if rng.random() < 0.5 else 1.0
            total += sign * sum(block)
            count += len(block)
        null_means.append(total / count)
    observed = sum(values) / len(values)
    p_greater = (1 + sum(value >= observed for value in null_means)) / (resamples + 1)

    return {
        "mean_loss_improvement": observed,
        "ci95_low": low,
        "ci95_high": high,
        "p_value": p_greater,
        "effective_n": effective_sample_size(values),
    }


def _regression_metrics(y: np.ndarray, pred: np.ndarray) -> dict[str, float]:
    return {
        "mse": float(mean_squared_error(y, pred)),
        "rmse": float(math.sqrt(mean_squared_error(y, pred))),
        "mae": float(mean_absolute_error(y, pred)),
        "r2": float(r2_score(y, pred)),
    }


def _classification_metrics(y: np.ndarray, prob: np.ndarray) -> dict[str, float]:
    return {
        "brier": float(brier_score_loss(y, prob)),
        "log_loss": float(log_loss(y, prob, labels=[0, 1])),
        "pr_auc": float(average_precision_score(y, prob)),
    }


def run_e1_train_validation(
    *,
    manifest_path: Path,
    config_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    """Run E1 development evaluation without opening the untouched-test file."""

    manifest = _read_manifest(manifest_path)
    cfg = _read_toml(config_path)
    if cfg["experiment"].get("stage") != "train_validation":
        raise ValueError("E1 development runner requires stage=train_validation")
    forbidden = set(cfg["data"].get("forbidden_splits", []))
    if "untouched_test" not in forbidden:
        raise ValueError("E1 config must explicitly forbid untouched_test")

    train_path = _artifact_path(manifest_path, manifest["artifacts"]["gold_train"])
    validation_path = _artifact_path(
        manifest_path, manifest["artifacts"]["gold_validation"]
    )
    train_rows = _load_split(train_path, "train")
    validation_rows = _load_split(validation_path, "validation")
    if not train_rows or not validation_rows:
        raise ValueError("train and validation artifacts must both be non-empty")

    rows = train_rows + validation_rows
    _validate_grid(rows)
    _build_features(rows, cfg)
    train_end = len(train_rows)
    embargo = int(cfg["validation"]["embargo_bins"])
    minimum_gain = float(cfg["experiment"]["minimum_relative_loss_improvement"])
    bootstrap_block = int(cfg["validation"]["bootstrap_block_size"])
    resamples = int(cfg["validation"]["bootstrap_resamples"])
    jump_sigma = float(cfg["targets"]["jump_sigma"])
    base_seed = int(cfg["experiment"]["random_seed"])

    group_features = {
        name: list(features) for name, features in cfg["feature_groups"].items()
    }
    if "market_only" not in group_features:
        raise ValueError("E1 feature_groups must include market_only")

    comparisons: list[dict[str, Any]] = []
    p_values: list[float] = []
    p_indices: list[int] = []

    for horizon in [int(value) for value in cfg["targets"]["horizons_bins"]]:
        for target in (*REGRESSION_TARGETS, *CLASSIFICATION_TARGETS):
            target_values = [
                _build_target(
                    rows,
                    index,
                    horizon=horizon,
                    target=target,
                    jump_sigma=jump_sigma,
                )
                for index in range(len(rows))
            ]

            all_extra = sorted(
                {feature for features in group_features.values() for feature in features}
            )
            required = list(MARKET_FEATURES) + all_extra
            train_indices = [
                index
                for index in range(train_end)
                if target_values[index] is not None
                and all(_valid_number(rows[index].get(feature)) for feature in required)
            ]
            validation_indices = [
                index
                for index in range(train_end + embargo, len(rows))
                if target_values[index] is not None
                and all(_valid_number(rows[index].get(feature)) for feature in required)
            ]
            if len(train_indices) < 500 or len(validation_indices) < 250:
                comparisons.append(
                    {
                        "horizon_bins": horizon,
                        "target": target,
                        "status": "INVALID",
                        "reason": "insufficient common support after causal warmup/purge/embargo",
                        "n_train": len(train_indices),
                        "n_validation": len(validation_indices),
                    }
                )
                continue

            y_train = np.asarray([target_values[index] for index in train_indices], dtype=float)
            y_val = np.asarray([target_values[index] for index in validation_indices], dtype=float)

            prediction_by_group: dict[str, np.ndarray] = {}
            metrics_by_group: dict[str, dict[str, float]] = {}
            per_row_loss: dict[str, np.ndarray] = {}
            for group, extras in group_features.items():
                features = list(MARKET_FEATURES) + extras
                x_train = _matrix(rows, train_indices, features)
                x_val = _matrix(rows, validation_indices, features)
                if target in REGRESSION_TARGETS:
                    model = Pipeline(
                        [
                            ("scale", StandardScaler()),
                            ("model", Ridge(alpha=float(cfg["models"]["ridge_alpha"]))),
                        ]
                    )
                    model.fit(x_train, y_train)
                    pred = model.predict(x_val)
                    prediction_by_group[group] = pred
                    metrics_by_group[group] = _regression_metrics(y_val, pred)
                    per_row_loss[group] = (y_val - pred) ** 2
                else:
                    if len(np.unique(y_train)) < 2 or len(np.unique(y_val)) < 2:
                        prediction_by_group = {}
                        break
                    model = Pipeline(
                        [
                            ("scale", StandardScaler()),
                            (
                                "model",
                                LogisticRegression(
                                    C=float(cfg["models"]["logistic_c"]),
                                    max_iter=int(cfg["models"]["max_iter"]),
                                    random_state=base_seed,
                                ),
                            ),
                        ]
                    )
                    model.fit(x_train, y_train.astype(int))
                    prob = model.predict_proba(x_val)[:, 1]
                    prediction_by_group[group] = prob
                    metrics_by_group[group] = _classification_metrics(y_val.astype(int), prob)
                    per_row_loss[group] = (y_val - prob) ** 2

            if not prediction_by_group:
                comparisons.append(
                    {
                        "horizon_bins": horizon,
                        "target": target,
                        "status": "INVALID",
                        "reason": "classification target has one class in train or validation",
                        "n_train": len(train_indices),
                        "n_validation": len(validation_indices),
                    }
                )
                continue

            baseline_loss = per_row_loss["market_only"]
            baseline_mean = float(np.mean(baseline_loss))
            for group in group_features:
                if group == "market_only":
                    continue
                candidate_loss = per_row_loss[group]
                loss_improvement = baseline_loss - candidate_loss
                inference = _paired_block_inference(
                    loss_improvement.tolist(),
                    block_size=bootstrap_block,
                    resamples=resamples,
                    seed=base_seed + horizon * 101 + len(comparisons) * 17,
                )
                candidate_mean = float(np.mean(candidate_loss))
                relative_gain = (
                    (baseline_mean - candidate_mean) / baseline_mean
                    if baseline_mean > 0
                    else 0.0
                )
                record = {
                    "horizon_bins": horizon,
                    "target": target,
                    "candidate": group,
                    "features": list(MARKET_FEATURES) + group_features[group],
                    "n_train": len(train_indices),
                    "n_validation": len(validation_indices),
                    "baseline_metrics": metrics_by_group["market_only"],
                    "candidate_metrics": metrics_by_group[group],
                    "baseline_primary_loss": baseline_mean,
                    "candidate_primary_loss": candidate_mean,
                    "relative_loss_improvement": relative_gain,
                    **inference,
                    "status": "PENDING_FDR",
                }
                p_indices.append(len(comparisons))
                p_values.append(float(inference["p_value"]))
                comparisons.append(record)

    if p_values:
        q_values = benjamini_hochberg(p_values)
        alpha = float(cfg["validation"]["fdr_alpha"])
        for index, q_value in zip(p_indices, q_values, strict=True):
            record = comparisons[index]
            record["q_value"] = q_value
            gain = float(record["relative_loss_improvement"])
            ci_low = float(record["ci95_low"])
            ci_high = float(record["ci95_high"])
            p_value = float(record["p_value"])
            if gain >= minimum_gain and ci_low > 0 and q_value <= alpha:
                status = "SUPPORTED"
            elif gain >= minimum_gain and p_value <= 0.05:
                status = "WEAK"
            elif gain <= -minimum_gain or ci_high < 0:
                status = "REJECTED"
            else:
                status = "INCONCLUSIVE"
            record["status"] = status

    status_counts: dict[str, int] = {}
    for record in comparisons:
        status = str(record["status"])
        status_counts[status] = status_counts.get(status, 0) + 1

    payload: dict[str, Any] = {
        "schema_version": 1,
        "kind": "ninja-e1-train-validation",
        "experiment_id": cfg["experiment"]["id"],
        "hypothesis_id": cfg["experiment"]["hypothesis"],
        "stage": "train_validation",
        "created_at": utc_now().isoformat().replace("+00:00", "Z"),
        "code_commit": git_commit(),
        "dataset_manifest_id": manifest["manifest_id"],
        "dataset_manifest_sha256": sha256_file(manifest_path),
        "experiment_config_sha256": sha256_file(config_path),
        "untouched_test_opened": False,
        "input_artifacts": {
            "train": {
                "path": str(train_path),
                "sha256": sha256_file(train_path),
                "rows": len(train_rows),
            },
            "validation": {
                "path": str(validation_path),
                "sha256": sha256_file(validation_path),
                "rows": len(validation_rows),
            },
        },
        "primary_loss": "squared_error / Brier by target family",
        "multiple_testing": {
            "method": "Benjamini-Hochberg",
            "family_size": len(p_values),
            "alpha": float(cfg["validation"]["fdr_alpha"]),
        },
        "minimum_relative_loss_improvement": minimum_gain,
        "status_counts": status_counts,
        "comparisons": comparisons,
        "scientific_boundary": (
            "Development result only. The untouched 2025 artifact was not opened. "
            "Any final-test evaluation requires a separately frozen specification."
        ),
    }
    payload["result_sha256"] = sha256_json(payload)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return payload
