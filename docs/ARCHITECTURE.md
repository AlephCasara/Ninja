# Architecture

## Decision

Ninja is a **research and strategy-development project**.

Master Trader is the **runtime**.

The purpose of Ninja is to discover, validate and package deterministic trading logic. Once a Ninja implementation is promoted, it should run inside the Master Trader fleet using the same operational model as the existing bots.

There is no mandatory `NinjaState` runtime service and no generic Ninja policy engine.

## Determinism

A runtime Ninja (k) is a deterministic Python program.

Conceptually:

```math
a_{k,t}
=
\pi_k(
M_t,
F_{k,t};
\theta_k
)
```

where:

- $M_t$ is conventional market state;
- $F_{k,t}$ is the subset of Ninja-derived inputs required by that implementation;
- $\theta_k$ is the frozen parameter set;
- $\pi_k$ is the Python strategy/module;
- $a_{k,t}$ is the resulting action.

Given the same inputs, code version and parameters, the same action must be produced.

That is the relevant deterministic boundary.

## Research architecture

The six Ninja domains organize research:

1. Attention
2. Divergence
3. Narrative
4. Propagation
5. Event Morphology
6. Susceptibility

They are **not** six required services and do not map one-to-one to runtime bots.

A candidate strategy may combine any subset of these domains.

Example:

```text
candidate Ninja
  attention surprise
  + propagation latency
  + funding state
  + open interest state
        ↓
  deterministic Python strategy
```

## Research outputs

A successful research line may produce one of three runtime artifact classes.

### Standalone strategy

A new Freqtrade strategy with its own entry, exit and risk logic.

### Strategy overlay

A deterministic module or feature used by an existing Master Trader strategy.

### Risk/regime module

A deterministic module used to change predefined risk behavior or block new entries under validated conditions.

The project should prefer the simplest artifact that captures the validated effect.

## Promotion path

```text
hypothesis
→ historical dataset
→ registered experiment
→ chronological OOS validation
→ deterministic implementation
→ Master Trader dry-run
→ live approval
```

Research code has no trading authority.

Promotion happens by moving a concrete implementation into the Master Trader runtime.

## Live information inputs

Some Ninjas may require current public-information data.

Those inputs can be produced by:

- Last30Days;
- dedicated crawlers;
- public web/news collectors;
- source-specific adapters;
- deterministic feature calculators.

The resulting data should be exposed to a strategy as typed values or files.

This is analogous to the existing Master Trader pattern in which strategies consume external funding or OI data.

The collector may be complex. The strategy decision remains deterministic.

## Historical data layers

Bronze / Silver / Gold remain useful for research.

### Bronze

Raw or near-raw observations and provenance.

### Silver

Normalized observations, entities, event extraction and semantic representations.

### Gold

Research features and time-series panels.

These layers belong to the Ninja research process. They are not a required runtime abstraction in Master Trader.

## Research feature notation

For analysis, Ninja uses:

```math
N_{a,t}
=
[
ATT,
DIV,
NAR,
TRN,
EVT,
CTX
]_{a,t}
```

This is mathematical notation for the candidate feature space.

A runtime Ninja consumes only what it needs:

```math
F_{k,t}
\subseteq
N_{a,t}
```

There is no requirement to serialize the entire vector in production.

## Master Trader runtime

The Master Trader fleet already provides the correct operational structure:

- strategy registry;
- per-bot runtime configs;
- live/dry-run execution;
- monitoring;
- portfolio risk controls;
- capital-account semantics;
- health and validation tooling.

Ninja should reuse this machinery.

Conceptually:

```text
Master Trader
├── existing bots
│   ├── FundingFadeV1
│   ├── KeltnerBounceV1
│   ├── OITrendPullbackV1
│   └── ...
│
└── Ninja family
    ├── <validated Ninja 1>
    ├── <validated Ninja 2>
    └── <validated Ninja 3>
```

## Family-level switch

The intended global behavior is:

```text
NINJA_ENABLED=false
  → no Ninja-tagged bot or Ninja-only feed is started

NINJA_ENABLED=true
  → individually enabled Ninja bots may run
```

Each Ninja still retains its own runtime config and dry-run/live status.

The exact implementation may use a registry field, Compose profile or startup filter. The behavior matters more than the mechanism.

## Failure isolation

1. `NINJA_ENABLED=false` must preserve the existing Master Trader fleet.
2. A failed Ninja collector must not stop unrelated bots.
3. A Ninja requiring a missing/stale feed must follow its own declared fail behavior.
4. Existing Master Trader risk controls remain authoritative.
5. No LLM or research process receives direct order authority.

## Repository boundary

The current split is:

```text
Ninja repository
  research
  data manifests
  experiments
  candidate implementations
  validation evidence
        ↓ promotion
Master Trader repository/runtime
  promoted Ninja Python code
  bot configs
  monitoring
  risk
  execution
```

This is not a requirement to run Ninja as an external production microservice.

A monorepo remains possible later. The important separation is between experimental research and promoted deterministic runtime code.
