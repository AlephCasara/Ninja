from __future__ import annotations

from ninja_labs.validation.core import ols_slope, pearson_r
from ninja_labs.validation.resampling import block_permutation_test, block_shuffle
import numpy as np


def generate_lagged_relation(n: int, *, effect: float, lag: int, seed: int, noise_sigma: float = 1.0) -> tuple[list[float], list[float]]:
    rng = np.random.default_rng(seed)
    x = rng.normal(size=n)
    y = rng.normal(scale=noise_sigma, size=n)
    for i in range(lag, n):
        y[i] += effect * x[i - lag]
    return x[:-lag].tolist(), y[lag:].tolist()


def test_known_lagged_effect_is_recovered_and_survives_block_null():
    x, y = generate_lagged_relation(
        800,
        effect=0.85,
        lag=3,
        noise_sigma=0.8,
        seed=1729,
    )
    slope = ols_slope(x, y)
    test = block_permutation_test(
        x,
        y,
        statistic=pearson_r,
        block_size=16,
        n_resamples=199,
        seed=1730,
    )
    assert 0.55 <= slope <= 1.15
    assert test["observed"] > 0.45
    assert test["p_value"] <= 0.05


def test_block_shuffle_breaks_broad_alignment_without_changing_length():
    x, y = generate_lagged_relation(400, effect=1.0, lag=2, seed=42)
    shuffled = block_shuffle(y, block_size=10, seed=99)
    assert len(shuffled) == len(y)
    assert sorted(shuffled) == sorted(y)
    assert abs(pearson_r(x, shuffled)) < abs(pearson_r(x, y))
