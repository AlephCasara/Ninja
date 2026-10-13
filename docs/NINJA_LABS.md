# Ninja Labs

## Purpose

Ninja Labs is the scientific analysis, experimentation and validation layer of Ninja.

Its question is:

> What can we demonstrate from the observations acquired by Ninja Tools?

Ninja Labs does not own web acquisition. It consumes typed observations and research datasets, constructs candidate information variables, tests hypotheses and emits versioned evidence suitable for the Ninja intelligence layer.

```text
Ninja Tools
    -> Observation
    -> Ninja Labs
    -> Evidence / validated Signal candidate
    -> Ninja
```

## Scientific authority

The methodology belongs to Ninja, not to any external package.

External scientific software is an instrument. A library may estimate a Hawkes model, fit a classifier, suggest an Ax trial or run a backtest, but it does not decide:

- what hypothesis is being tested;
- what baseline must be beaten;
- what target is legitimate;
- which data are causally available;
- which split is untouched;
- which robustness checks are mandatory;
- whether a result constitutes evidence;
- whether a factor is promoted.

## Core responsibilities

Ninja Labs owns or coordinates:

### Feature science

- attention;
- attention surprise and acceleration;
- source/author breadth and concentration;
- divergence and polarization;
- narrative entropy and concentration;
- novelty and emergence;
- change-point detection;
- propagation timing;
- Hawkes-derived propagation features;
- Transfer Entropy / directed-information diagnostics;
- event morphology;
- domain-specific susceptibility interactions.

### Statistical validation

- chronological train/validation/test splits;
- purging and embargo where labels overlap;
- dependence-aware bootstrap;
- placebo/permutation/surrogate tests;
- multiple-hypothesis correction;
- calibration diagnostics;
- leave-one-asset-out / leave-one-regime-out tests where appropriate;
- drop-best-event robustness;
- ablation against simpler baselines;
- untouched final test evaluation.

### Experiment management

Every headline result must be traceable to an explicit experiment contract containing at least:

```text
experiment_id
hypothesis_id
dataset_manifest
code_revision
domain
targets
baselines
features/search_space
train_window
validation_window
untouched_test_window
metrics
robustness_checks
stopping_rules
random_seeds where relevant
```

The concrete `ExperimentSpec v1` schema is a Phase 0 deliverable.

## Information backtest versus strategy backtest

Ninja Labs distinguishes two validation stages.

### Information backtest

Question:

> Does a Ninja information variable add stable out-of-sample information beyond the conventional baseline?

Example:

```text
market-only
vs
market + normalized attention
```

This is the immediate target of E1.

### Strategy backtest

Question:

> Can a previously validated information effect improve an executable strategy after fees, slippage, latency, turnover and risk constraints?

Strategy backtests happen after information value is established. They must not substitute for the original scientific test.

## Ax boundary

Meta Ax is a Ninja Labs instrument for bounded adaptive experiment design and Bayesian optimization.

Ax may help choose the next trial inside a Ninja-owned experiment contract, for example across:

- attention windows;
- normalization variants;
- minimum-support thresholds;
- regularization;
- feature combinations;
- prediction horizons;
- selected model hyperparameters.

Ax must not:

- define the scientific hypothesis;
- silently change the target or baseline;
- optimize on the untouched final test set;
- repeatedly inspect the final test and feed the result back into search;
- promote a result merely because it is the best observed trial.

Target flow:

```text
Hypothesis
    -> ExperimentSpec
    -> train/validation search space
    -> Ax suggests TrialSpec
    -> evaluate
    -> record TrialResult
    -> freeze candidate
    -> untouched chronological test
    -> Evidence
```

Ax is introduced after the fixed E1 pipeline works end-to-end, so adaptive optimization cannot hide errors in data alignment or validation.

## Hawkes boundary

Hawkes processes belong to Ninja Labs propagation science.

The initial E3 question is not whether Hawkes is mathematically expressive. It is:

> Does propagation structure add incremental chronological OOS information beyond attention-only baselines?

Required progression:

```text
activation timing
    -> activation order / latency
    -> simple multivariate Hawkes baseline
    -> fit/stability diagnostics
    -> derived propagation features
    -> OOS incremental-information test
    -> richer models only if justified
```

Initial candidate outputs include:

- baseline intensity;
- self excitation;
- cross excitation;
- integrated excitation matrix;
- branching/reproduction proxies;
- spectral radius where model assumptions apply;
- propagation persistence/decay measures.

The first historical dataset must therefore preserve event-level timestamps and source/process identity even though E1 initially aggregates attention.

## Hawkes implementation policy

No Hawkes library is canonical during Phase 0.

When E3 begins, Ninja Labs should benchmark candidate/reference implementations on:

- software correctness on deterministic/unit fixtures;
- multivariate support;
- likelihood/estimation behavior;
- numerical stability;
- diagnostics;
- reproducibility;
- maintenance state;
- performance on the actual Ninja event volume.

For critical headline evidence, implementation checks or an independent/reference implementation may be useful for software correctness. Empirical evidence must still come from the real point-in-time information system and mechanism-appropriate validation.

## Python research plane

Python is a first-class Labs language because the scientific ecosystem materially improves correctness and research velocity.

Expected instrument families include:

- NumPy / SciPy;
- statsmodels;
- scikit-learn;
- Polars / Arrow / Parquet;
- DuckDB;
- Ax / BoTorch where justified;
- point-process/Hawkes libraries after benchmarking;
- Freqtrade or Master Trader adapters at promotion validation.

The environment should be reproducible and managed declaratively for the repository; use `uv` for the Python project/environment workflow rather than ad-hoc imperative package installation.

Heavy research should prefer lazy/chunked scans and bounded batch jobs rather than unnecessary long-lived in-memory services.

## Data contract

Labs consumes Bronze/Silver/Gold research layers:

```text
Bronze
  raw/replayable acquisition artifacts
        ->
Silver
  normalized typed Observation records
        ->
Gold
  experiment-ready features and aligned panels
```

Event-level Silver data is authoritative for temporal research. Gold aggregations are reproducible derivatives.

RAG/semantic knowledge systems may consume the same source corpus for agent reasoning, but they do not replace the causal structured dataset used for statistical validation.

## Domain boundaries

Shared Labs methods are domain-neutral only where their mathematical meaning transfers.

For example, the same attention-surprise implementation may be reused by trading and business experiments. The following remain domain-specific:

- targets;
- baselines;
- susceptibility/context variables;
- success thresholds;
- promotion criteria;
- economic interpretation.

A trading result never automatically validates a business result.

## E1 is the current gate

E1 Attention Replication is the first end-to-end Labs target.

Required comparison:

```text
market-only
market + raw count
market + normalized attention
market + attention structure
```

Primary targets remain:

- future realized volatility;
- future volume surprise;
- jump probability;
- maximum adverse excursion.

Directional return remains secondary.

A positive result requires stable incremental chronological OOS information and robustness. A negative or inconclusive result is also a valid scientific delivery.

## MCP exposure

Labs may eventually expose MCP capabilities such as:

```text
labs.experiment_run
labs.experiment_status
labs.trial_suggest
labs.trial_complete
labs.feature_compute
labs.validate
labs.evidence_get
```

These names are conceptual, not a Phase 0 commitment to separate services or to expose every internal scientific function to agents.

Phase 0 keeps one MCP server and adds agent-facing Labs capabilities only when an experiment needs them.

## Anti-vibe-coding rule

No new scientific abstraction is promoted merely because it is interesting.

A new Labs capability should answer at least one of:

1. Which registered hypothesis requires it?
2. Which simpler baseline does it compete against?
3. Which dataset and target will test it?
4. What result would falsify or reject it?
5. What downstream decision changes if it succeeds?

If those questions have no concrete answers, the capability remains a research note rather than implementation work.