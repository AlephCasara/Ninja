from __future__ import annotations

import math
import statistics
from collections import Counter
from collections.abc import Sequence
from typing import Literal


def robust_attention_surprise(
    counts: Sequence[float],
    *,
    lookback: int,
    zero_mad_policy: Literal["poisson", "epsilon"] = "poisson",
    epsilon: float = 1e-9,
) -> list[float | None]:
    """Causal robust attention surprise using only trailing observations.

    The current count is never included in its reference window. When the
    trailing MAD is zero, the caller must choose an explicit fallback policy.
    `poisson` uses sqrt(max(median, 1)) as a conservative scale; `epsilon`
    implements the literal epsilon-stabilized formula and is expected to be
    extremely sensitive after long all-zero periods.
    """

    xs = [float(value) for value in counts]
    if lookback < 2:
        raise ValueError("lookback must be >= 2")
    if epsilon <= 0:
        raise ValueError("epsilon must be positive")
    if any(not math.isfinite(value) or value < 0 for value in xs):
        raise ValueError("counts must be finite and non-negative")

    result: list[float | None] = [None] * len(xs)
    for index in range(lookback, len(xs)):
        reference = xs[index - lookback : index]
        center = float(statistics.median(reference))
        mad = float(statistics.median(abs(value - center) for value in reference))
        if mad > 0:
            scale = 1.4826 * mad
        elif zero_mad_policy == "poisson":
            scale = math.sqrt(max(center, 1.0))
        elif zero_mad_policy == "epsilon":
            scale = epsilon
        else:  # pragma: no cover - protected by Literal/type checking at development time
            raise ValueError(f"unsupported zero_mad_policy: {zero_mad_policy}")
        result[index] = (xs[index] - center) / max(scale, epsilon)
    return result


def estimate_nb_moments(values: Sequence[float]) -> tuple[float, float]:
    """Estimate NB mean and dispersion phi by method of moments.

    Parameterization is Var(N) = mu + mu^2 / phi. If sample variance is not
    greater than the mean, phi is +inf and the model reduces to Poisson-like
    variance for the standardized-residual calculation.
    """

    xs = [float(value) for value in values]
    if len(xs) < 2:
        raise ValueError("at least two observations are required")
    if any(not math.isfinite(value) or value < 0 for value in xs):
        raise ValueError("values must be finite and non-negative")
    mu = sum(xs) / len(xs)
    variance = statistics.variance(xs)
    if mu <= 0:
        return 0.0, math.inf
    excess = variance - mu
    if excess <= 0:
        return mu, math.inf
    return mu, (mu * mu) / excess


def negative_binomial_residual(count: float, *, mu: float, phi: float) -> float:
    """Standardized residual for Var(N)=mu+mu^2/phi."""

    count = float(count)
    mu = float(mu)
    phi = float(phi)
    if not math.isfinite(count) or count < 0:
        raise ValueError("count must be finite and non-negative")
    if not math.isfinite(mu) or mu < 0:
        raise ValueError("mu must be finite and non-negative")
    if not (math.isinf(phi) or (math.isfinite(phi) and phi > 0)):
        raise ValueError("phi must be positive or +inf")
    variance = mu if math.isinf(phi) else mu + (mu * mu) / phi
    if variance <= 0:
        return 0.0 if count == mu else math.copysign(math.inf, count - mu)
    return (count - mu) / math.sqrt(variance)


def attention_acceleration(values: Sequence[float]) -> list[float | None]:
    """Second finite difference with explicit unavailable first two points."""

    xs = [float(value) for value in values]
    if any(not math.isfinite(value) for value in xs):
        raise ValueError("values must be finite")
    result: list[float | None] = [None] * len(xs)
    for index in range(2, len(xs)):
        result[index] = xs[index] - 2.0 * xs[index - 1] + xs[index - 2]
    return result


def author_structure(authors: Sequence[str | None]) -> dict[str, float | int]:
    """Return volume-independent author breadth/concentration diagnostics."""

    cleaned = [str(author) for author in authors if author not in (None, "", "[deleted]")]
    n = len(cleaned)
    if n == 0:
        return {
            "message_count": 0,
            "unique_author_count": 0,
            "breadth": 0.0,
            "hhi": 0.0,
            "entropy": 0.0,
            "entropy_normalized": 0.0,
        }
    counts = Counter(cleaned)
    unique = len(counts)
    shares = [count / n for count in counts.values()]
    hhi = sum(share * share for share in shares)
    entropy = -sum(share * math.log(share) for share in shares if share > 0)
    entropy_normalized = entropy / math.log(unique) if unique > 1 else 0.0
    return {
        "message_count": n,
        "unique_author_count": unique,
        "breadth": unique / n,
        "hhi": hhi,
        "entropy": entropy,
        "entropy_normalized": entropy_normalized,
    }
