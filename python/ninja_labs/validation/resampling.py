from __future__ import annotations

import random
from collections.abc import Callable, Sequence

Statistic = Callable[[Sequence[float], Sequence[float]], float]


def _validate_block_size(length: int, block_size: int) -> None:
    if length <= 1:
        raise ValueError("at least two observations are required")
    if block_size <= 0 or block_size > length:
        raise ValueError("block_size must satisfy 1 <= block_size <= len(values)")


def _blocks(values: Sequence[float], block_size: int) -> list[list[float]]:
    return [
        [float(value) for value in values[start : start + block_size]]
        for start in range(0, len(values), block_size)
    ]


def circular_shift(values: Sequence[float], shift: int) -> list[float]:
    xs = [float(value) for value in values]
    if not xs:
        raise ValueError("values must not be empty")
    normalized = shift % len(xs)
    if normalized == 0:
        return xs.copy()
    return xs[-normalized:] + xs[:-normalized]


def time_reverse(values: Sequence[float]) -> list[float]:
    return [float(value) for value in reversed(values)]


def block_shuffle(
    values: Sequence[float], *, block_size: int, seed: int
) -> list[float]:
    xs = [float(value) for value in values]
    _validate_block_size(len(xs), block_size)
    chunks = _blocks(xs, block_size)
    random.Random(seed).shuffle(chunks)
    return [value for chunk in chunks for value in chunk]


def moving_block_bootstrap(
    values: Sequence[float],
    *,
    block_size: int,
    n_resamples: int,
    seed: int,
) -> list[list[float]]:
    """Moving-block bootstrap preserving local serial structure."""

    xs = [float(value) for value in values]
    _validate_block_size(len(xs), block_size)
    if n_resamples <= 0:
        raise ValueError("n_resamples must be positive")

    starts = list(range(0, len(xs) - block_size + 1))
    rng = random.Random(seed)
    samples: list[list[float]] = []
    for _ in range(n_resamples):
        sample: list[float] = []
        while len(sample) < len(xs):
            start = rng.choice(starts)
            sample.extend(xs[start : start + block_size])
        samples.append(sample[: len(xs)])
    return samples


def block_permutation_test(
    x: Sequence[float],
    y: Sequence[float],
    *,
    statistic: Statistic,
    block_size: int,
    n_resamples: int,
    seed: int,
    alternative: str = "two-sided",
) -> dict[str, float]:
    """Block-permutation test that preserves within-block order in ``y``.

    The null destroys broad alignment between x and y while retaining local
    dependence inside y blocks. The returned p-value uses the +1 correction so
    it is never exactly zero.
    """

    xs = [float(value) for value in x]
    ys = [float(value) for value in y]
    if len(xs) != len(ys):
        raise ValueError("x and y must have equal length")
    _validate_block_size(len(xs), block_size)
    if n_resamples <= 0:
        raise ValueError("n_resamples must be positive")
    if alternative not in {"two-sided", "greater", "less"}:
        raise ValueError("unsupported alternative")

    observed = float(statistic(xs, ys))
    chunks = _blocks(ys, block_size)
    rng = random.Random(seed)
    null_statistics: list[float] = []
    for _ in range(n_resamples):
        shuffled = chunks.copy()
        rng.shuffle(shuffled)
        permuted = [value for chunk in shuffled for value in chunk]
        null_statistics.append(float(statistic(xs, permuted)))

    if alternative == "two-sided":
        extreme = sum(abs(value) >= abs(observed) for value in null_statistics)
    elif alternative == "greater":
        extreme = sum(value >= observed for value in null_statistics)
    else:
        extreme = sum(value <= observed for value in null_statistics)

    p_value = (extreme + 1.0) / (n_resamples + 1.0)
    return {
        "observed": observed,
        "p_value": p_value,
        "null_mean": sum(null_statistics) / len(null_statistics),
        "null_min": min(null_statistics),
        "null_max": max(null_statistics),
    }
