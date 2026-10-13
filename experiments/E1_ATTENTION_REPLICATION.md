# E1 — Attention Replication

**Status:** preregistered design; Phase 1 substrate live-smoke validated; canonical corpus and empirical E1 execution pending.

## Question

Does abnormal public attention provide incremental information about future market state after conditioning on conventional market data?

## Scope

Start with the best timestamped historical source that can be reconstructed reproducibly.

Do not require cross-platform data for the first pass.

## Candidate features

- message count;
- unique-author count;
- attention surprise;
- attention acceleration;
- author concentration;
- author entropy.

## Phase 1.5 estimator gate

Before any candidate attention estimator is allowed to influence the headline E1 comparison, it must pass an estimator-specific validation suite under `docs/SCIENTIFIC_VALIDATION_PROTOCOL.md`.

At minimum:

```text
known synthetic behavior
→ estimator recovery
→ autocorrelation-aware null/permutation controls
→ sensitivity to window/seasonality choices
→ false-positive calibration
→ only then historical E1 data
```

Raw count is the simplest reference and must remain available as a baseline. A more elaborate normalization is rejected if it cannot outperform or robustly complement the simpler representation.

## Baseline

Market-only features:

- lagged return;
- realized volatility;
- volume;
- broad market/BTC regime;
- funding/OI where the asset/time period supports them.

## Primary targets

1. future realized volatility;
2. future volume surprise;
3. jump probability;
4. maximum adverse excursion.

Directional return is secondary.

## Horizons

Initial candidates:

```text
15m
1h
4h
24h
```

The final primary/secondary horizon set must be frozen before the untouched test window is evaluated.

Every horizon must use label-aware purging. Boundary embargo must be explicit rather than assumed.

## Required comparisons

```text
market-only
market + raw count
market + normalized attention
market + attention structure
```

## Anti-confirmation requirements

Before opening the final untouched test:

- freeze the primary target/metric and minimum meaningful effect;
- register primary, secondary and exploratory hypotheses;
- register the multiple-testing family and correction method;
- record all attempted variants/trials, including failures;
- report raw N and effective/clustered N where applicable;
- run dependence-aware bootstrap/permutation controls;
- verify the result is not dominated by one event/regime/community;
- freeze code, features and parameters before final-test access.

Random train/test splitting is not a headline validation method for this time-series experiment.

## Success

A result is not successful because a coefficient has `p < 0.05`.

Success requires useful, stable incremental chronological OOS performance, an effect above the preregistered minimum meaningful threshold, corrected inference where multiple tests are interpreted, and survival of the required robustness/negative controls.

## Failure

E1 fails if the effect:

- disappears chronologically OOS;
- exists only through mutable/lookahead-contaminated fields;
- is below the minimum meaningful effect;
- is dominated by one event/regime/community;
- fails estimator recovery or null calibration;
- appears under negative controls at an unacceptable rate;
- cannot be reconstructed reliably enough for live use.

If data or protocol defects prevent E1 from answering the question, classify the experiment as `INVALID`, not `REJECTED`.

## Decision

E1 is the gating empirical experiment for the rest of Ninja's more expensive modeling. Positive, negative and inconclusive outcomes are all valid deliveries when the experiment itself passes the scientific-validation gate.
