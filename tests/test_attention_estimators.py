from __future__ import annotations

import math

from ninja_labs.attention.estimators import (
    author_structure,
    attention_acceleration,
    estimate_nb_moments,
    negative_binomial_residual,
    robust_attention_surprise,
)


def test_robust_attention_surprise_is_causal_and_handles_zero_mad():
    counts = [0.0] * 96 + [8.0, 0.0]
    scores = robust_attention_surprise(counts, lookback=96, zero_mad_policy="poisson")
    assert scores[95] is None
    assert scores[96] == 8.0
    # The previous burst may influence the next reference window, but the next
    # current observation is never included in its own reference statistics.
    assert scores[97] is not None


def test_negative_binomial_moment_and_residual_edge_cases():
    mu, phi = estimate_nb_moments([2, 2, 2, 2, 2])
    assert mu == 2.0
    assert math.isinf(phi)
    assert negative_binomial_residual(2, mu=2, phi=phi) == 0.0
    assert negative_binomial_residual(4, mu=2, phi=phi) > 0


def test_attention_acceleration_truth_table():
    assert attention_acceleration([3, 3, 3, 3]) == [None, None, 0.0, 0.0]
    assert attention_acceleration([0, 1, 2, 3]) == [None, None, 0.0, 0.0]
    assert attention_acceleration([0, 0, 0, 10, 0, 0]) == [
        None,
        None,
        0.0,
        10.0,
        -20.0,
        10.0,
    ]


def test_author_structure_distinguishes_echo_from_breadth_and_is_label_invariant():
    echo = author_structure(["one"] * 100)
    broad = author_structure([f"u{i}" for i in range(100)])
    balanced_a = author_structure([f"u{i % 10}" for i in range(100)])
    balanced_b = author_structure([f"renamed{i % 10}" for i in range(100)])

    assert echo["hhi"] == 1.0
    assert echo["entropy_normalized"] == 0.0
    assert broad["hhi"] < balanced_a["hhi"] < echo["hhi"]
    assert broad["breadth"] == 1.0
    assert balanced_a["hhi"] == balanced_b["hhi"]
    assert balanced_a["entropy_normalized"] == balanced_b["entropy_normalized"]
