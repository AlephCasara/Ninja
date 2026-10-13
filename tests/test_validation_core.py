from __future__ import annotations

from ninja_labs.validation.core import benjamini_hochberg, effective_sample_size
import numpy as np


def generate_ar1(n: int, *, phi: float, seed: int) -> list[float]:
    rng = np.random.default_rng(seed)
    noise = rng.normal(size=n)
    values = np.zeros(n, dtype=float)
    for i in range(1, n):
        values[i] = phi * values[i - 1] + noise[i]
    return values.tolist()


def test_benjamini_hochberg_is_monotone_in_sorted_input():
    adjusted = benjamini_hochberg([0.001, 0.01, 0.04, 0.20])
    assert adjusted == sorted(adjusted)
    assert adjusted[0] <= 0.01
    assert adjusted[-1] == 0.20


def test_effective_n_drops_under_strong_serial_dependence():
    weak = generate_ar1(1000, phi=0.05, seed=11)
    strong = generate_ar1(1000, phi=0.90, seed=12)
    weak_n = effective_sample_size(weak, max_lag=30)
    strong_n = effective_sample_size(strong, max_lag=30)
    assert 1 <= strong_n < weak_n <= 1000
