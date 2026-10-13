# Scientific validation protocol

## Purpose

Ninja experiments exist to give hypotheses a fair opportunity to fail.

The objective is not to produce a positive result. A negative or inconclusive result is a valid research asset when the experiment was capable of detecting a meaningful effect and the data were fit for the question.

## Four validation layers

Every proposed factor or estimator must be considered at four distinct layers.

### 1. Estimator validation

Before real market claims, verify on synthetic data that the implementation recovers a known property or parameter within a preregistered tolerance.

Examples:

- attention detector finds injected bursts at a controlled false-positive rate;
- Hawkes implementation recovers a known excitation matrix from simulated events;
- Transfer Entropy estimator recovers a known directed dependency;
- change-point detector recovers an injected change time.

A method that cannot recover a truth constructed by Ninja is not allowed to interpret historical market data.

### 2. Null calibration and negative controls

Verify that the method does not manufacture effects when the relationship is deliberately destroyed.

Candidate controls include:

- block permutation;
- circular time shift;
- time reversal where direction matters;
- block/surrogate shuffles;
- source/platform permutation;
- author permutation;
- event-label permutation;
- matched random controls.

Null construction must preserve relevant nuisance structure such as autocorrelation, seasonality or cluster size whenever possible. IID shuffling is not automatically valid for time series.

### 3. Empirical chronological OOS validation

Only after estimator and null gates pass may a factor be compared on real historical data.

The central comparison is incremental:

```text
market-only
vs
market + Ninja factor
```

Headline evaluation must be chronological. Random train/test splitting is prohibited when it allows future information or neighboring dependent samples to leak into training.

### 4. Generalization / transport validation

A surviving effect must be stressed outside the easiest episode or regime.

Depending on the hypothesis, tests may include:

- leave-one-regime-out;
- leave-one-event-out;
- drop-best-event;
- leave-one-source/platform-out;
- leave-one-asset-out;
- alternative time periods;
- prospective shadow collection.

A result that disappears when one famous event is removed is evidence about that event, not yet a general Ninja factor.

## Effective sample size

Ninja must never equate message count with independent evidence.

Every headline result should report, where applicable:

```text
N_raw
N_authors
N_windows
N_events
N_clusters
N_effective
```

The initial Labs helper estimates time-series effective N from positive serial autocorrelation. This is a diagnostic only. Event/cluster structure may require a different estimator and must be reported separately.

## Purging and embargo

Forward labels must not cross a split boundary.

For a sample with decision time `t` and label end `t+h`, the sample is purged from a split if `t+h` extends beyond that split's end.

An experiment may also define an embargo interval at the start of later splits to reduce dependence near chronological boundaries.

These controls are horizon-dependent. A 24-hour target generally requires a stronger boundary exclusion than a 15-minute target.

## Untouched test policy

The final test interval is treated as a one-use evidence surface.

Workflow:

```text
train
  -> exploration / fitting
validation
  -> comparison / selection / bounded adaptive search
freeze
  -> code + features + parameters + metrics + rejection criteria
untouched test
  -> final evaluation
```

Any material change motivated by the test result creates a new experiment generation. The already-opened interval is no longer untouched for that generation.

Ax or any other optimizer must not access the final untouched test while suggesting trials.

## Multiple testing

Before running a family of related tests, record the family and classify outcomes as primary, secondary or exploratory.

When multiple formal hypotheses are interpreted together, apply an appropriate correction such as Benjamini-Hochberg FDR. Correction does not replace effect-size, uncertainty, stability or OOS requirements.

All trials, including failures, must remain in experiment metadata. Selecting only the best result from a large hidden search is invalid.

## Minimum meaningful effect

Statistical significance is not sufficient.

Each preregistered experiment must state a minimum effect large enough to matter for the research question. Examples include minimum relative loss improvement, minimum calibration improvement, minimum information gain or minimum strategy-level economic improvement after costs.

## Headline-result gate

`ninja_labs.validation.headline.assess_headline_eligibility` rejects promotion when required anti-confirmation metadata are absent.

A headline record must include at least:

- experiment and hypothesis IDs;
- preregistration flag;
- primary metric;
- raw and effective sample sizes;
- passed synthetic recovery;
- passed null calibration;
- passed negative controls;
- chronological split policy;
- purging;
- embargo;
- multiple-testing family/method;
- untouched-test access count;
- proof the experiment was frozen before test access;
- explicit rejection rule;
- minimum meaningful effect.

The JSON contract is `schemas/validation-result-v1.schema.json`.

## Phase 1.5 self-test

The harness includes a deterministic self-test:

```text
uv run ninja-labs validation selftest
```

It checks that the generic validation machinery can:

1. recover a known lagged synthetic effect;
2. reject block-permuted alignment;
3. maintain an acceptable false-positive rate across independent autocorrelated null worlds;
4. report lower effective N under stronger autocorrelation;
5. perform Benjamini-Hochberg correction;
6. purge cross-boundary labels and embargo boundary samples.

This self-test validates the generic laboratory controls. It does **not** validate N1-N10, Hawkes, Transfer Entropy, attention surprise or any market hypothesis. Each estimator still requires its own recovery/null suite before empirical promotion.

## E1 end-to-end backtester gate

Estimator recovery alone is insufficient for E1. Before preregistration, the complete train/validation backtester must also pass controlled worlds through the exact production analysis path.

The gate runs one world where attention is deliberately coupled to future volatility and a family of null worlds where attention and volatility are independent. It exercises causal feature construction, forward targets, common support, model fitting, paired block inference, effect-size thresholds, FDR and the untouched-test boundary.

The default preregistration gate requires at least 12 null worlds. The known-signal world must be `SUPPORTED`, exceed the minimum meaningful effect and beat the p95 null gain. The allowed fraction of null `SUPPORTED`/`WEAK` discoveries is capped before empirical E1. The untouched-test artifact must remain unopened in every synthetic world.

```text
uv run ninja-labs validation e1-backtester --null-worlds 12
```

A passing result validates the E1 backtester mechanics, not N1 itself.

## Clean-code evidence

Scientific artifacts record both the Git commit and whether the worktree was dirty when they were produced. Preregistration rejects estimator, Monte Carlo, backtester, dataset-quality or canonical-manifest evidence produced from a dirty Git state, and requires those artifacts to identify the same clean code revision. Runtime scratch/data directories are ignored by Git and are not evidence-bearing source changes.

## Result taxonomy

Scientific results should be retained even when they fail.

Recommended terminal states:

```text
SUPPORTED
WEAK
INCONCLUSIVE
REJECTED
INVALID
```

`INVALID` means the experiment could not answer its question because a data, estimator, leakage or protocol failure occurred. It is different from `REJECTED`, where the experiment was valid and the hypothesis failed its preregistered criterion.

## Core rule

> A positive result is useful only if the same machinery was demonstrably capable of returning no result.
