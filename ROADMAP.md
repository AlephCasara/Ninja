# Roadmap

> **Rule:** Ninja is built outward from falsifiable experiments, not inward from capabilities. A capability is implemented when an experiment requires it.

The immediate program objective is the first reproducible, falsifiable historical information backtest. Tool breadth, model sophistication and additional domains are subordinate to that objective.

## Phase 0 — architecture freeze — in progress

- [x] Define Ninja as a research/validation project
- [x] Define six research domains
- [x] Record scientific foundation
- [x] Create hypothesis registry
- [x] Define validation ladder
- [x] Establish Rust core/tooling + Python research boundary
- [x] Define Ninja Tools as the acquisition/observation/preservation layer
- [x] Define Ninja Labs as the scientific analysis/experimentation/validation layer
- [x] Define Ninja as the intelligence/assessment layer
- [x] Keep one Ninja repository; treat trading and future business work as domain layers, not forks
- [x] Keep one MCP surface initially; conceptual `tools.*`, `labs.*`, `intel.*` namespaces do not imply separate daemons
- [x] Preserve Master Trader as the current execution/risk/capital authority
- [ ] Align README terminology with the frozen architecture without deleting the existing mathematical/scientific material
- [ ] Extend `tools/catalog.json` taxonomy to distinguish acquisition tools from Labs instruments
- [ ] Define `Observation v1` and `ExperimentSpec v1` contracts
- [ ] Add a minimal repository skeleton for Labs and domain-specific experiment configuration only where required by Phase 1/E1

**Phase 0 exit condition:** architecture documents, contracts and roadmap agree on `Tools -> Labs -> Ninja`, with no competing runtime model.

## Phase 1 — historical validation substrate

Priority vertical slice:

```text
historical information source
        -> Bronze
        -> Observation v1 / Silver
        -> attention Gold panel
        -> causally aligned market panel
```

Initial working candidate: historical Reddit data + BTC market data, subject to a final source-quality check before implementation.

- [ ] Select the first canonical historical information corpus
- [ ] Select matching market-data source/universe
- [ ] Implement the single acquisition adapter required by that corpus
- [ ] Implement dataset manifests and content/source hashes
- [ ] Implement UTC causal alignment
- [ ] Implement entity/asset aliases only as needed by the first corpus
- [ ] Implement no-lookahead tests
- [ ] Freeze train/validation/untouched-test periods
- [ ] Materialize Bronze/Silver/Gold with DuckDB/Parquet-compatible schemas
- [ ] Record exact event timestamps rather than retaining only aggregated counts
- [ ] Preserve source/platform/author/thread relationships when available so later E3/Hawkes work remains possible

**Gate:** do not add another crawler, browser or source merely because it is available. Add only what is necessary to complete the first reproducible dataset.

## Phase 2 — E1 Attention Replication / first information backtest

Question:

> Does abnormal public attention add stable chronological out-of-sample information beyond conventional market data?

- [ ] Build the preregistered attention feature set
- [ ] Reproduce simple attention statistics
- [ ] Evaluate market-only baseline
- [ ] Evaluate market + raw count
- [ ] Evaluate market + normalized attention
- [ ] Evaluate market + attention structure
- [ ] Test future realized volatility
- [ ] Test volume surprise
- [ ] Test jumps
- [ ] Test MAE
- [ ] Run robustness/ablation checks required by E1
- [ ] Publish a positive, negative or inconclusive result with immutable experiment metadata

Target reproducible interface:

```text
uv run ninja-labs experiment run <E1 config>
```

The exact CLI shape may change; reproducibility is the invariant.

**Gate:** no propagation or morphology result is promoted ahead of a failed basic attention gate merely because the later mathematics is more interesting.

## Phase 3 — Ninja Labs experiment optimization / Ax

Ax enters after the fixed E1 pipeline is known to be scientifically and operationally correct.

- [ ] Add Ax to the Labs instrument catalog
- [ ] Define a bounded Ax adapter around Ninja-owned `ExperimentSpec` / `TrialSpec` contracts
- [ ] Allow Ax to explore only preregistered train/validation spaces
- [ ] Make untouched final test data inaccessible during adaptive optimization
- [ ] Compare Ax against fixed/random/grid baselines on trial count, compute cost and final OOS result
- [ ] Record every adaptive trial and stopping condition

Candidate search dimensions include feature windows, normalization variants, regularization, minimum support and prediction horizons.

**Gate:** Ax is an experimental instrument, not an epistemic authority. Adaptive search must never become repeated tuning on the final test window.

## Phase 4 — second stream / cross-platform information structure

- [ ] Select the second reliable timestamped information stream
- [ ] Prefer structured historical datasets/APIs before live recrawling
- [ ] Run platform/source ablation
- [ ] Estimate common attention
- [ ] Preserve platform/source residuals
- [ ] Run E2 disagreement/narrative tests
- [ ] Build cross-source entity/narrative alignment required for propagation work

GDELT/news is a strong candidate for this phase, subject to source-quality and temporal-coverage checks against the chosen E1 period.

## Phase 5 — E3 propagation / Hawkes

The Phase 1 schema must make this possible without reconstructing discarded event timing.

### E3.1 — nonparametric timing

- [ ] Estimate first activation per source/process
- [ ] Estimate activation order
- [ ] Estimate cross-source latency
- [ ] Run event-aligned lead/lag diagnostics

### E3.2 — baseline Hawkes model

- [ ] Benchmark candidate/reference Hawkes implementations
- [ ] Start with the smallest defensible multivariate model, preferably an exponential-kernel baseline
- [ ] Estimate baseline intensity and self/cross excitation
- [ ] Derive integrated excitation / branching matrix
- [ ] Check stability via spectral radius where model assumptions support it
- [ ] Run residual/time-rescaling/goodness-of-fit diagnostics

### E3.3 — incremental-information test

Compare:

```text
market + attention
vs
market + attention + propagation/Hawkes features
```

- [ ] Run chronological OOS comparison
- [ ] Test sensitivity to estimator/binning/event-definition choices
- [ ] Check whether apparent social->market effects are better explained by market->social response
- [ ] Add Transfer Entropy / surrogate-corrected directed-information diagnostics where justified

### E3.4 — richer models only after survival

Possible later work:

- marked Hawkes;
- semantic marks/modulation;
- time-varying coupling;
- exposure/adoption models;
- other nonlinear point-process variants.

**Gate:** sophistication is not evidence. Richer propagation models must beat attention-only and simpler propagation baselines OOS.

## Phase 6 — E4 Event Morphology

- [ ] Freeze event ontology v0
- [ ] Create reviewed event gold set
- [ ] Benchmark rules / compact classifier / local LLM extraction
- [ ] Test event-response similarity
- [ ] Test historical analogue distributions
- [ ] Compare morphology against simpler event/category baselines

## Phase 7 — prospective collection

After the historical substrate is useful enough to justify live observation:

- [ ] Design live point-in-time acquisition
- [ ] Integrate Last30Days as reconnaissance/discovery where useful
- [ ] Add changedetection-style sentinels where ongoing page change history has value
- [ ] Add dedicated source adapters only where justified
- [ ] Store `published_at`, `first_seen_at` and `collected_at`
- [ ] Preserve replayable evidence selectively
- [ ] Compare historical reconstruction quality against prospective capture

## Phase 8 — first promoted Ninja implementation

Only after a factor or factor combination survives historical information validation:

- [ ] choose the smallest useful runtime artifact: standalone strategy, overlay or risk/regime module
- [ ] freeze Python implementation and parameters
- [ ] add it to the Master Trader fleet as a Ninja-family component
- [ ] add `NINJA_ENABLED` family-level control
- [ ] prove `NINJA_ENABLED=false` preserves current fleet semantics
- [ ] run the promoted Ninja in dry-run / shadow
- [ ] collect prospective outcomes

## Phase 9 — live approval

Only if the implementation survives:

```text
historical OOS
+ robustness checks
+ strategy backtest / walk-forward
+ prospective dry-run/shadow
+ execution economics
```

then compare:

```text
baseline strategy/fleet
vs
baseline + promoted Ninja implementation
```

Human approval remains required before live capital is enabled.

## Future domain — business

Business remains a domain placeholder during the trading validation program.

Shared methods may later be reused, but business-specific targets, baselines, susceptibility and evidence must be validated independently. Trading evidence never automatically validates a business hypothesis.