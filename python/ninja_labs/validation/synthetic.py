from __future__ import annotations

import random


def generate_ar1(
    n: int,
    *,
    phi: float,
    sigma: float = 1.0,
    seed: int,
) -> list[float]:
    if n <= 1:
        raise ValueError("n must be greater than one")
    if abs(phi) >= 1:
        raise ValueError("stationary AR(1) requires abs(phi) < 1")
    if sigma <= 0:
        raise ValueError("sigma must be positive")

    rng = random.Random(seed)
    values = [rng.gauss(0.0, sigma)]
    for _ in range(1, n):
        values.append(phi * values[-1] + rng.gauss(0.0, sigma))
    return values


def generate_lagged_relation(
    n: int,
    *,
    effect: float,
    lag: int,
    phi_x: float = 0.35,
    phi_noise: float = 0.25,
    noise_sigma: float = 1.0,
    seed: int,
) -> tuple[list[float], list[float]]:
    """Return aligned x/y samples with a known lagged effect.

    ``y[t] = effect * x[t-lag] + autocorrelated_noise[t]``. The returned
    sequences are aligned so each x value is the known parent of the matching
    y value. This is intended for estimator-recovery tests, not market realism.
    """

    if lag <= 0 or lag >= n:
        raise ValueError("lag must satisfy 0 < lag < n")
    x = generate_ar1(n, phi=phi_x, sigma=1.0, seed=seed)
    noise = generate_ar1(
        n,
        phi=phi_noise,
        sigma=noise_sigma,
        seed=seed + 1_000_003,
    )
    y = noise.copy()
    for index in range(lag, n):
        y[index] += effect * x[index - lag]
    return x[:-lag], y[lag:]


def generate_null_pair(
    n: int,
    *,
    phi: float = 0.5,
    seed: int,
) -> tuple[list[float], list[float]]:
    """Generate independent but individually autocorrelated processes."""

    x = generate_ar1(n, phi=phi, sigma=1.0, seed=seed)
    y = generate_ar1(n, phi=phi, sigma=1.0, seed=seed + 7_919)
    return x, y
