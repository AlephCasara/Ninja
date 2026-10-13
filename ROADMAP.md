# Roadmap

> **Rule:** Ninja is built outward from falsifiable experiments, not inward from capabilities. A capability is implemented when an experiment requires it.

The immediate program objective is the first reproducible, falsifiable historical information backtest. Tool breadth, model sophistication and additional domains are subordinate to that objective.

## Phase 0 — architecture freeze — substantially complete

- [x] Define Ninja as a research/validation project
- [x] Define six research domains and hypothesis registry
- [x] Define Ninja Tools, Ninja Labs and Ninja intelligence boundaries
- [x] Establish Rust core/tooling + Python research boundary
- [x] Keep one repository; trading/business are domain layers, not forks
- [x] Keep one MCP surface initially
- [x] Preserve Master Trader as execution/risk/capital authority
- [x] Define `Observation v1` and `ExperimentSpec v1`
- [x] Extend tool taxonomy to distinguish acquisition from Labs instruments
- [ ] Align the large README terminology with the frozen architecture without deleting the scientific material

**Gate:** architecture and contracts agree on `Tools -> Labs -> Ninja`; documentation debt does not block experiments.

## Phase 1 — historical validation substrate — live-validated implementation; canonical materialization pending

```text
Arctic Shift Reddit
        -> Bronze
        -> Observation v1 / Silver
        -> attention Gold

Binance BTCUSDT 15m
        -> market Silver

attention + market
        -> causally aligned Gold
        -> coverage + manifest
```

Completed:

- [x] Arctic Shift API adapter for bounded smoke/gap work
- [x] streaming subreddit-JSONL ingestion for the canonical corpus
- [x] Binance public market adapter
- [x] content/artifact hashes and manifests
- [x] causal `available_at` and market `decision_time`
- [x] no-lookahead tests
- [x] frozen chronological train/validation/untouched-test periods
- [x] Bronze/Silver/Gold materializers
- [x] exact event timestamps preserved for later E3/Hawkes
- [x] coverage audit for temporal quality, market gaps, missingness and split counts
- [x] offline CI tests
- [x] live smoke against Arctic Shift + Binance
- [x] smoke showed zero market gaps and zero future-window/future-observation violations

Pending canonical-data gate:

- [ ] download `r/Bitcoin` and `r/CryptoCurrency` subreddit JSONL inputs
- [ ] materialize the canonical 2021-2025 dataset
- [ ] inspect final coverage/gaps/temporal-quality report
- [x] commit a resolver-generated `uv.lock` before the first headline E1 result

Canonical command:

```text
uv run ninja-labs phase1 build --config domains/trading/configs/phase1-btc-reddit.toml
```

**Gate:** a successful smoke proves the pipeline, not completeness of the five-year corpus.

## Phase 1.5 — scientific validation harness — generic harness complete

Purpose:

> verify that Ninja's laboratory can recover known truths and reject constructed false relationships before real hypotheses are allowed to generate headline claims.

Generic controls:

- [x] deterministic synthetic AR(1) generator
- [x] deterministic known lagged-effect generator
- [x] estimator-recovery self-test
- [x] block permutation preserving local dependence
- [x] moving-block bootstrap primitive
- [x] block shuffle, circular shift and time-reversal primitives
- [x] time-series effective sample size diagnostic
- [x] Benjamini-Hochberg FDR correction
- [x] chronological label purging
- [x] boundary embargo
- [x] headline-result eligibility gate
- [x] `validation-result-v1` contract
- [x] anti-confirmation protocol documentation
- [x] deterministic `ninja-labs validation selftest` command
- [x] E1 attention estimator controlled-world validation
- [x] E1 64-world Monte Carlo calibration
- [x] E1 full backtester signal/null validation with untouched-test isolation
- [x] clean-Git evidence requirement for preregistration artifacts
- [x] pass Python/Rust/Markdown CI on the completed harness

Every estimator used later must then receive its **own** validation suite:

```text
synthetic recovery
+ null calibration
+ negative controls
+ sensitivity analysis
+ empirical chronological OOS
+ generalization stress
```

This applies independently to:

- attention surprise estimators;
- negative-binomial residuals;
- acceleration/breadth/concentration measures;
- change-point detectors;
- stance/disagreement estimators;
- narrative/novelty estimators;
- Hawkes implementations;
- Transfer Entropy estimators;
- event-morphology distances;
- susceptibility/interactions.

**Gate:** passing the generic self-test does not validate N1-N10. A method that cannot recover a constructed truth or behaves badly under null worlds may not interpret market data.

## Phase 2 — E1 Attention Replication / first information backtest

Question:

> Does abnormal public attention add stable chronological out-of-sample information beyond conventional market data?

Before touching the untouched test, freeze feature definitions, horizons, primary metrics, hypothesis family, rejection criteria and minimum meaningful effect.

Required sequence:

- [x] validate raw-count and attention estimators on synthetic/null suites
- [ ] build preregistered attention features
- [ ] evaluate market-only baseline
- [ ] evaluate market + raw count
- [ ] evaluate market + normalized attention
- [ ] evaluate market + attention structure
- [ ] test future realized volatility
- [ ] test volume surprise
- [ ] test jumps
- [ ] test MAE
- [ ] enforce horizon-dependent purging/embargo
- [ ] report raw N, windows/events/clusters where applicable, and effective N
- [ ] apply registered multiple-testing correction
- [ ] run block bootstrap/permutation controls
- [ ] run regime/event/source ablations where applicable
- [ ] publish `SUPPORTED`, `WEAK`, `INCONCLUSIVE`, `REJECTED` or `INVALID`

Target interface:

```text
uv run ninja-labs experiment run <E1 config>
```

**Gate:** E1 is the first empirical gate. No sophisticated later model is rescued simply because it is mathematically interesting.

## Phase 2.5 — E1 generalization

A surviving E1 factor must be attacked for transportability:

- [ ] leave-one-regime-out
- [ ] drop-best-event
- [ ] leave-one-event-out where event episodes are identifiable
- [ ] source/community ablation
- [ ] alternative periods
- [ ] later, asset-transfer tests
- [ ] prospective shadow comparison when justified

**Gate:** one dominant episode or regime is not a general Ninja factor.

## Phase 3 — Ninja Labs experiment optimization / Ax

Ax enters only after the fixed E1 pipeline is scientifically and operationally correct.

- [x] Ax exists in the Labs instrument catalog
- [ ] define a bounded adapter around Ninja-owned experiment/trial contracts
- [ ] allow adaptive search only over preregistered train/validation spaces
- [ ] make final untouched test unavailable to Ax
- [ ] compare Ax against fixed/random/grid baselines
- [ ] record every adaptive trial and stopping condition

**Gate:** Ax is an experimental instrument, not an epistemic authority.

## Phase 4 — second stream / E2 information structure

- [ ] select a second reliable timestamped information stream
- [ ] run source/platform ablation
- [ ] estimate common attention and platform residuals
- [ ] validate stance/disagreement estimators synthetically before claims
- [ ] validate narrative/novelty/change-point estimators synthetically before claims
- [ ] run E2 incremental tests against attention-only baselines
- [ ] build cross-source entity/narrative alignment required for propagation

GDELT/news remains a strong candidate subject to temporal-quality review.

## Phase 5 — E3 propagation / Hawkes / directed information

### E3.0 — estimator validation

Before historical interpretation:

- [ ] simulate known Hawkes processes and recover known excitation structure
- [ ] calibrate Hawkes null/false-positive behavior
- [ ] include time-reversal/surrogate diagnostics where appropriate
- [ ] simulate known directed dependencies for Transfer Entropy
- [ ] verify TE direction recovery and surrogate bias correction

### E3.1 — nonparametric timing

- [ ] first activation per process
- [ ] activation order
- [ ] cross-source latency
- [ ] event-aligned lead/lag diagnostics

### E3.2 — baseline Hawkes

- [ ] benchmark candidate/reference implementations
- [ ] start with the smallest defensible multivariate model
- [ ] estimate baseline intensity and self/cross excitation
- [ ] derive integrated excitation / branching matrix
- [ ] check spectral-radius stability when assumptions permit
- [ ] run residual/time-rescaling/goodness-of-fit diagnostics

### E3.3 — incremental information

Compare:

```text
market + attention
vs
market + attention + propagation
```

- [ ] chronological OOS comparison
- [ ] sensitivity to event definition/binning/estimator
- [ ] test market->social reverse explanation
- [ ] add surrogate-corrected directed-information diagnostics

**Gate:** richer propagation models must beat attention-only and simpler propagation baselines OOS.

## Phase 6 — E4 Event Morphology

- [ ] freeze event ontology v0 before outcome inspection
- [ ] create a reviewed event gold set blinded to future price response
- [ ] validate morphology-distance behavior on synthetic/controlled examples
- [ ] benchmark rules / compact classifier / local LLM extraction
- [ ] test event-response similarity on held-out event episodes
- [ ] test historical analogue distributions
- [ ] compare morphology against simpler category/matched-control baselines

**Gate:** messages are not independent events; morphology inference must use event-level/effective sample size.

## Phase 7 — prospective collection

- [ ] design point-in-time acquisition
- [ ] integrate Last30Days for reconnaissance where useful
- [ ] add changedetection-style sentinels when page-change history matters
- [ ] store `published_at`, `first_seen_at`, `collected_at`
- [ ] preserve replayable evidence selectively
- [ ] compare historical reconstruction quality against prospective capture

## Phase 8 — first promoted Ninja implementation

Only factors surviving validation may be promoted:

- [ ] choose the smallest useful artifact: strategy, overlay or risk/regime module
- [ ] freeze implementation and parameters
- [ ] integrate with Master Trader without changing baseline semantics
- [ ] run dry/shadow
- [ ] collect prospective outcomes

## Phase 9 — live approval

Require:

```text
historical OOS
+ robustness/generalization
+ strategy backtest / walk-forward
+ prospective dry/shadow
+ execution economics
```

then compare the original strategy/fleet against the same strategy/fleet plus the frozen Ninja component. Human approval remains required before live capital.

## Future domain — business

Business remains a domain placeholder during trading validation. Shared methods may later be reused, but business targets, baselines, susceptibility and evidence require independent validation. Trading evidence never automatically validates a business hypothesis.
