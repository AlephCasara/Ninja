# Backtesting session protocol

This document is the operational entry point for a Ninja backtesting/research session.

It does not replace `BACKTESTING_POLICY.md`, `HISTORICAL_REPLAY.md`, the mathematical framework, or an experiment-specific specification. It defines how a session is opened, what may change while it is running, and what must exist at handoff.

## Scope v1

The current research program asks whether **point-in-time public off-market communication** provides reproducible incremental information about future crypto-market states beyond the market state itself.

In scope:

```text
public posts / discussions / news / official communication
activity and engagement snapshots available point-in-time
qualitative content and versioned semantic interpretation
narrative structure and divergence
public-information events
propagation when the available sources genuinely support it
market state used as baseline / susceptibility context
```

Out of scope for the current program:

```text
on-chain analytics
wallet forensics
rug-pull detection
smart-contract analysis
DEX microstructure
50x / 100x hunting as a discovery objective
RL trading policies
live capital allocation
```

Out-of-scope phenomena may be observed and recorded as future research candidates. They must not silently expand the active experiment.

## Session object

Every substantive backtesting session owns one `ExperimentSpec v2` document validated against:

```text
schemas/experiment-spec-v2.schema.json
```

The spec is the session boundary. It must be created before a replication/promotion run and should be created at the start of discovery once the question and data boundary are known.

## Session phases

A session declares exactly one phase:

```text
discovery
replication
generalization
economic
prospective
```

### Discovery

Purpose: find candidate structure in real point-in-time evidence.

Discovery may be adaptive. Feature ideas, representations and methods may change, but every material change must be recorded in the search/change log. Discovery never produces a promoted claim by itself.

Two discovery modes are allowed:

- `outcome_blind`: construct/cluster/characterize the information state without using future outcomes to choose the representation, then inspect outcome enrichment;
- `label_aware`: use outcomes inside an explicitly designated discovery partition to search for predictive structure.

A label-aware discovery result is still exploratory. It requires frozen replication on unseen evidence.

### Replication

Purpose: test a candidate whose definition was frozen before the replication evidence was inspected.

The candidate, representation, target, horizon, population, baseline and evaluation rule must be frozen. A material post-outcome change creates a new experiment generation.

### Generalization

Purpose: test whether a replicated relationship survives new regimes, events, sources, assets or populations appropriate to the claim.

### Economic

Purpose: translate surviving information into decisions and evaluate realistic execution economics. Information validity and strategy quality remain separate claims.

### Prospective

Purpose: run the frozen system against genuinely new observations. Research/LLM components have no live capital authority.

## Replay types

A session declares one primary replay type:

```text
state
event
propagation
strategy_overlay
```

The replay contract is defined in `HISTORICAL_REPLAY.md`.

## Evidence boundary

The session spec must make outcome access explicit.

Allowed policies:

```text
outcome_blind_discovery
label_aware_discovery
frozen_evaluation
prospective_only
```

A session may not claim an untouched/replication boundary that it has already inspected adaptively.

## Inputs that must be pinned

Before interpreting a replication/generalization/economic result, pin:

- code revision;
- dataset manifest IDs;
- information sources;
- market source(s);
- point-in-time availability rule;
- population / asset-universe construction rule;
- semantic extractor/model/prompt/schema version when qualitative interpretation is used;
- representation definition;
- target/outcome definition;
- horizons;
- baseline(s);
- relevant controls/falsifications.

## Representation boundary

The current v1 science separates:

```text
C_t = public communication state
M_t = observable market state
Y_t+h = future outcome
```

The primary incremental question is whether communication adds information beyond the market baseline.

Communication representations may contain activity, qualitative semantics, narrative structure, events and supported propagation variables. Rich content must not be collapsed to a convenience scalar and then treated as a test of the richer construct.

Market state is a baseline/context, not evidence that communication is predictive.

On-chain state is not part of the current v1 communication representation.

## Statistical methods

A session records the methods it actually uses and their relevant assumptions.

No method is mandatory merely because it is conventional. Bootstrap, permutation, FDR, effective-N diagnostics, purging, embargo, Hawkes, Transfer Entropy, survival models and other methods are selected when they match the scientific object and claim.

Software/unit tests establish implementation behavior, not empirical market evidence.

## Search and change log

Discovery is allowed to learn. It is not allowed to forget how it learned.

Material changes should be appended to a session log with:

```text
timestamp
change
reason
evidence already inspected when the change was made
whether the change invalidates any previous untouched boundary
```

Examples of material changes:

- new feature family;
- new target or horizon;
- new population filter;
- changed semantic prompt/schema;
- changed candidate definition;
- changed primary metric;
- changed exclusion rule.

Pure implementation fixes that do not change scientific meaning should still be tied to a code revision but need not create a new hypothesis generation.

## Result interpretation

Every completed session states:

- what was supported, rejected, weak, inconclusive or invalid;
- the exact population, period, representation, target and horizon to which that result applies;
- what a negative result **does not** reject;
- whether the result is discovery, replication, generalization, economic or prospective evidence;
- the plausible economic relevance, if any.

A negative result for activity counts does not reject semantic information, narrative structure or propagation. A failed strategy overlay does not by itself falsify the underlying information relationship.

## Minimal session artifacts

A clean session directory should contain only:

```text
SPEC.json              # ExperimentSpec v2
CHANGELOG.md            # append-only scientific/search changes
RESULTS.json            # machine-readable result when a run exists
REPORT.md               # interpretation when a run is completed
artifacts/               # manifests/figures/small derived evidence only
```

Large datasets, model weights and source archives remain outside Git.

During early discovery, `RESULTS.json` and `REPORT.md` may not exist yet. `SPEC.json` and `CHANGELOG.md` are sufficient to establish the research boundary.

## Recommended next-session sequence

For the next fresh research conversation, do not begin with a headline alpha test. Use two separate sessions:

### Session A — Replay Audit

Purpose: verify that real historical states can be reconstructed causally and reproducibly.

Recommended boundary:

```text
phase = discovery
replay_type = state
outcome_access = outcome_blind_discovery
claim = none; infrastructure/data-quality audit only
```

Audit a bounded sample of real decision times and verify:

- every included observation was available under the declared clock;
- mutable engagement is point-in-time or excluded;
- content/provenance can be traced to source artifacts;
- semantic interpretations are bound to the exact content hash and knowledge policy;
- market state uses only data available by decision time;
- repeated construction yields the same frozen-state hash;
- duplicate/restart boundaries do not change state counts;
- no future outcome is required to build the state.

A Replay Audit can be `PASSED` or `INVALID`; it does not produce `SUPPORTED` market evidence.

### Session B — First Discovery

Open only after Replay Audit is satisfactory. Start from the narrow v1 question: does public communication state add information beyond market state? Begin with the smallest representation appropriate to the data and preserve qualitative content for later semantic/narrative comparisons.

Do not add on-chain data, rug-pull detection, extreme-multiple hunting or RL merely because they are potentially profitable. Record them as deferred research if they arise.

## Session start checklist

Before analysis:

1. read `README.md`;
2. read `BACKTESTING_POLICY.md`;
3. read `HISTORICAL_REPLAY.md`;
4. read the relevant experiment document;
5. declare phase and replay type;
6. declare current scope and explicit exclusions;
7. pin code/data clocks and manifests available at session start;
8. declare outcome-access mode;
9. state the scientific question and the negative-result scope;
10. only then inspect/compute experiment outcomes.

## Session stop / handoff checklist

Before handing work to another chat/agent:

1. commit code/spec changes or clearly record the dirty state;
2. update `SPEC.json` if the scientific contract legitimately changed;
3. append all material adaptive changes to `CHANGELOG.md`;
4. record which outcome periods/data were inspected;
5. record current result status without promotion inflation;
6. list unresolved data-quality/leakage questions;
7. state the next allowed action;
8. do not leave an ambiguous "untouched" period after inspecting it.

The goal is that a fresh agent can continue the research without reconstructing scientific intent from chat history.
