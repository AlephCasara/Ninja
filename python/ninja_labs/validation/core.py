from __future__ import annotations

import math
from collections.abc import Sequence


def _as_floats(values: Sequence[float]) -> list[float]:
    result = [float(value) for value in values]
    if not result:
        raise ValueError("values must not be empty")
    if not all(math.isfinite(value) for value in result):
        raise ValueError("values must be finite")
    return result


def pearson_r(x: Sequence[float], y: Sequence[float]) -> float:
    xs = _as_floats(x)
    ys = _as_floats(y)
    if len(xs) != len(ys):
        raise ValueError("x and y must have equal length")
    if len(xs) < 2:
        raise ValueError("at least two observations are required")

    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    dx = [value - mean_x for value in xs]
    dy = [value - mean_y for value in ys]
    denom = math.sqrt(sum(value * value for value in dx) * sum(value * value for value in dy))
    if denom == 0:
        return 0.0
    return sum(a * b for a, b in zip(dx, dy, strict=True)) / denom


def ols_slope(x: Sequence[float], y: Sequence[float]) -> float:
    xs = _as_floats(x)
    ys = _as_floats(y)
    if len(xs) != len(ys):
        raise ValueError("x and y must have equal length")
    if len(xs) < 2:
        raise ValueError("at least two observations are required")

    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    centered_x = [value - mean_x for value in xs]
    denominator = sum(value * value for value in centered_x)
    if denominator == 0:
        raise ValueError("x has zero variance")
    numerator = sum(
        dx * (value_y - mean_y)
        for dx, value_y in zip(centered_x, ys, strict=True)
    )
    return numerator / denominator


def autocorrelation(values: Sequence[float], lag: int) -> float:
    xs = _as_floats(values)
    if lag <= 0 or lag >= len(xs):
        raise ValueError("lag must satisfy 0 < lag < len(values)")

    mean_x = sum(xs) / len(xs)
    denominator = sum((value - mean_x) ** 2 for value in xs)
    if denominator == 0:
        return 0.0
    numerator = sum(
        (xs[index] - mean_x) * (xs[index - lag] - mean_x)
        for index in range(lag, len(xs))
    )
    return numerator / denominator


def effective_sample_size(
    values: Sequence[float], *, max_lag: int | None = None
) -> float:
    """Estimate time-series effective N using a positive autocorrelation sum.

    This is a diagnostic, not a universal estimator. Positive autocorrelations
    are accumulated until the first non-positive lag. Experiments with natural
    clusters/events should additionally report cluster/event counts.
    """

    xs = _as_floats(values)
    n = len(xs)
    if n < 3:
        return float(n)

    if max_lag is None:
        max_lag = max(1, min(n - 1, int(math.sqrt(n))))
    if not 1 <= max_lag < n:
        raise ValueError("max_lag must satisfy 1 <= max_lag < len(values)")

    rho_sum = 0.0
    for lag in range(1, max_lag + 1):
        rho = autocorrelation(xs, lag)
        if rho <= 0:
            break
        rho_sum += rho

    estimate = n / (1.0 + 2.0 * rho_sum)
    return max(1.0, min(float(n), estimate))


def benjamini_hochberg(p_values: Sequence[float]) -> list[float]:
    """Return Benjamini-Hochberg FDR-adjusted q-values in input order."""

    ps = [float(value) for value in p_values]
    if not ps:
        raise ValueError("p_values must not be empty")
    if any(not math.isfinite(value) or value < 0 or value > 1 for value in ps):
        raise ValueError("p-values must be finite and in [0, 1]")

    m = len(ps)
    ordered = sorted(enumerate(ps), key=lambda item: item[1])
    adjusted_sorted = [1.0] * m
    running = 1.0
    for reverse_index in range(m - 1, -1, -1):
        _, p_value = ordered[reverse_index]
        rank = reverse_index + 1
        candidate = min(1.0, p_value * m / rank)
        running = min(running, candidate)
        adjusted_sorted[reverse_index] = running

    result = [1.0] * m
    for sorted_index, (original_index, _) in enumerate(ordered):
        result[original_index] = adjusted_sorted[sorted_index]
    return result
