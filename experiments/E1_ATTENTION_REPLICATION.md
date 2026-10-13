# E1 — Attention Replication

**Status:** preregistered design; estimator-specific controlled-world validation passed; canonical corpus materialization and empirical E1 execution pending.

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

Controlled-world testing already found one useful failure: the simple rolling robust AZ retained strong deterministic periodic structure, while same-phase seasonal normalization removed almost all of it in the synthetic seasonal world. Therefore rolling AZ is baseline/diagnostic only; the causal same-week-phase seasonal estimator is the normalized-attention candidate for E1 v1.

## Baseline

Market-only features:

- lagged return;
- realized volatility;
- volume;
- calendar phase;
- broad market/BTC regime where available without changing the frozen E1 v1 specification.

Funding/OI are not added post hoc to E1 v1 merely because validation results are disappointing. They require a new preregistered experiment version if promoted into the baseline.

## Preregistered primary comparison

The confirmatory E1 v1 test is frozen before any real train/validation outcome is inspected:

```text
target:       future realized volatility
horizon:      4 hours (16 × 15-minute bins)
baseline:     market-only
candidate:    market + seasonal attention surprise + attention acceleration
primary loss: mean squared error
minimum useful relative loss improvement: 0.5%
alpha:        0.05
```

The 4-hour horizon was chosen a priori as a compromise: 15 minutes is highly sensitive to archive/timestamp precision, while 24 hours creates heavy label overlap and weakens effective sample size. Four hours is long enough for public-information transmission to be plausible while retaining substantially more independent episodes than the 24-hour target.

This primary comparison may not be replaced by a more favorable secondary result after train/validation is observed.

## Secondary targets and horizons

Secondary target families remain:

1. future realized volatility;
2. future volume surprise;
3. jump probability;
4. maximum adverse excursion.

Secondary horizons are 15m, 1h and 24h. Directional return is not a confirmatory E1 v1 target.

Every horizon must use label-aware purging. Boundary embargo must be explicit rather than assumed.

## Required comparisons

```text
market-only
market + raw count
market + seasonal normalized attention
market + attention structure
market + all validated attention features
```

The full comparison family is reported. Benjamini-Hochberg correction is applied to the registered E1 candidate-comparison family. A secondary/exploratory comparison cannot be relabeled as the primary test because its corrected result is stronger.

## Two seals

E1 uses two distinct locks:

1. **Preregistration seal** — created after canonical-dataset coverage validation and estimator validation, but before train/validation outcomes are inspected. It binds the exact dataset manifest, E1 config, estimator-validation artifact, primary comparison and code revision. It does not open the physical `untouched_test` artifact.
2. **Final-test seal** — created only after train/validation analysis and candidate selection are complete. It freezes the selected code/features/parameters before a single authorized evaluation of 2025.

A changed config or changed dataset manifest invalidates the preregistration seal and requires a new experiment version rather than silent mutation.

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

The primary E1 v1 result is `SUPPORTED` only if the preregistered 4-hour seasonal-attention comparison achieves at least the minimum meaningful loss improvement, its dependence-aware confidence interval excludes zero in the beneficial direction, and the registered multiple-testing interpretation is satisfied.

General E1 success additionally requires useful, stable incremental chronological OOS performance and survival of robustness/negative controls.

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
