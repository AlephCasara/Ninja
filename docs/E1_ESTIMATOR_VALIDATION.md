# E1 estimator validation

> **Policy status:** transitional/legacy for E1 scientific authority. `docs/BACKTESTING_POLICY.md` supersedes any universal synthetic/Monte-Carlo prerequisite or claim that E1 gates qualitatively different Ninja research. These documents remain implementation history until the corresponding code is surgically aligned.


E1 may not interpret historical market data until each candidate estimator has demonstrated that it measures the intended object in controlled worlds and does not manufacture excessive signal under null worlds.

## Scientific rule

The estimator validation suite is not designed to prove that an estimator is useful. It is designed to make estimator failure observable before empirical market data can reward an implementation mistake.

For each estimator family, record:

1. the mathematical estimand;
2. synthetic worlds where the expected behavior is known;
3. null worlds where the expected effect is absent;
4. nuisance worlds containing seasonality, trend, overdispersion, dependence, bursts or concentration as appropriate;
5. sensitivity to tuning choices;
6. failure criteria fixed before empirical E1 evaluation.

A candidate that fails this stage is not allowed to produce a headline historical E1 result.

## E1 candidate families

### Raw count

Estimand: causal message volume in `(t-window, t]`.

Required checks:

- exact recovery from synthetic event timestamps;
- correct zero windows;
- no future-event inclusion;
- invariance to event input order;
- explicit boundary semantics.

### Robust attention surprise

Candidate:

```math
AZ_t = \frac{N_t-\operatorname{median}(W_t)}{1.4826\,MAD(W_t)+\epsilon}
```

Required checks:

- near-zero center under stationary count worlds;
- positive response to injected bursts;
- robustness to isolated extreme outliers in the trailing reference window;
- causal trailing reference only;
- sensitivity across preregistered reference-window lengths;
- explicit behavior when MAD is zero.

### Negative-binomial attention residual

Candidate:

```math
AS_t = \frac{N_t-\mu_t}{\sqrt{\mu_t+\mu_t^2/\phi}}
```

Required checks:

- recover approximately standardized residual behavior when counts are generated from a known NB process;
- distinguish Poisson-like from strongly overdispersed worlds;
- seasonality adjustment must use only information available at `t`;
- burst response must survive after expected seasonal intensity is removed;
- parameter misspecification sensitivity must be reported.

### Attention acceleration

Candidate:

```math
\Delta^2 A_t = (A_t-A_{t-1})-(A_{t-1}-A_{t-2})
```

Required checks:

- exact finite-difference recovery on deterministic ramps/impulses;
- no spurious acceleration on constant series;
- sign behavior checked on increasing/decreasing ramps;
- sensitivity to noise and smoothing, if smoothing is later introduced.

### Author breadth / HHI / entropy

For author shares `s_u`:

```math
HHI=\sum_u s_u^2
```

and normalized entropy:

```math
H_A=-\frac{\sum_u s_u\log s_u}{\log U}.
```

Required checks:

- one-author concentration gives maximal HHI and minimal entropy;
- equal-share authors reduce HHI and increase entropy;
- permutation of author labels leaves statistics unchanged;
- duplicate/echo worlds distinguish raw volume from breadth;
- empty and single-author windows have explicit semantics.

## Null calibration

Every statistical estimator later used for inference must receive a larger estimator-specific null suite than the generic Phase 1.5 smoke.

The suite should contain at minimum:

- independent autocorrelated series;
- block-shuffled relationships;
- circularly shifted relationships;
- time-reversed controls where meaningful;
- nuisance seasonality without injected signal.

The number of null worlds and acceptance criterion must be preregistered before examining the empirical market result.

## Effective N

Every historical E1 report must distinguish, where applicable:

```text
N_raw
N_authors
N_windows
N_events_or_clusters
N_effective
```

Messages are not treated as independent experiments merely because they are separate rows.

## Promotion into empirical E1

Estimator-specific status is one of:

```text
VALIDATED_FOR_E1
REJECTED_ESTIMATOR
INCONCLUSIVE_ESTIMATOR
```

Only `VALIDATED_FOR_E1` candidates may enter the frozen E1 empirical comparison. A rejected estimator remains recorded; it is not silently replaced after seeing market outcomes.
