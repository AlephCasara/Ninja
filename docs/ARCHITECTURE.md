# Architecture

## Scope

Ninja owns research, validation and candidate implementation of alternative-information strategies. Master Trader owns production execution.

A promoted Ninja runs as deterministic Python inside the Master Trader fleet. No mandatory `NinjaState` service or generic policy engine is required.

## Runtime determinism

For implementation (k):

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

- $M_t$ is market state;
- $F_{k,t}$ is the subset of Ninja-derived inputs used by the implementation;
- $\theta_k$ is the frozen parameter set;
- $\pi_k$ is the Python strategy or module;
- $a_{k,t}$ is the resulting action.

A runtime build must reproduce the same action for the same serialized inputs, code version and parameters.

## Research domains

Ninja organizes research into six domains:

1. Attention
2. Divergence
3. Narrative
4. Propagation
5. Event Morphology
6. Susceptibility

These are analytical categories, not required services. One candidate implementation may combine several domains.

## Runtime artifact types

Validated research may be promoted as:

### Standalone strategy

A Freqtrade strategy with its own entry, exit and risk logic.

### Strategy overlay

Deterministic logic used by an existing Master Trader strategy.

### Risk or regime module

Deterministic selection among predefined risk behaviors.

Use the smallest runtime artifact that preserves the validated effect.

## Promotion path

```text
hypothesis
→ historical dataset
→ registered experiment
→ chronological OOS validation
→ frozen Python implementation
→ Master Trader backtest / walk-forward
→ dry-run / shadow
→ live approval
```

Research code has no order authority.

## Live information inputs

A promoted Ninja may require current public-information data. Inputs can come from Last30Days, dedicated crawlers, public web/news collectors or source-specific adapters.

The runtime strategy should consume timestamped typed values, following the same causal-data discipline used by existing external funding and OI inputs:

- record observation time;
- detect staleness;
- do not backfill current observations into historical candles;
- define missing-data behavior explicitly.

The collector may use probabilistic extraction. Trade decisions remain deterministic.

## Research data layers

Bronze / Silver / Gold are research-storage conventions, not runtime requirements.

### Bronze

Raw or near-raw observations with provenance.

### Silver

Normalized observations, entities, event extraction and semantic representations.

### Gold

Features and time-series panels used by experiments.

## Research notation

For analysis:

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

A runtime implementation consumes only the required subset:

```math
F_{k,t}
\subseteq
N_{a,t}
```

The complete vector does not need to be serialized in production.

## Master Trader runtime

Master Trader already provides:

- the bot registry;
- per-bot runtime configuration;
- live/dry-run execution;
- monitoring;
- portfolio risk controls;
- capital-account semantics;
- validation and health tooling.

Ninja should reuse those mechanisms.

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

## Family switch

Target behavior:

```text
NINJA_ENABLED=false
  → Ninja-family bots and Ninja-only feeds are not started

NINJA_ENABLED=true
  → individually enabled Ninja bots may run
```

Per-bot runtime configuration remains authoritative for active/dry-run/live behavior.

The implementation can use a registry field, Compose profile or startup filter. That choice belongs in the Master Trader PR.

## Failure isolation

1. `NINJA_ENABLED=false` preserves the existing fleet.
2. A failed Ninja feed does not stop unrelated bots.
3. Missing or stale input follows the affected Ninja's declared behavior.
4. Existing Master Trader risk controls remain authoritative.
5. LLMs and research processes have no direct order authority.

## Repository boundary

Current ownership:

```text
Ninja repository
  research
  data manifests
  experiments
  candidate implementations
  validation evidence
        ↓ promotion
Master Trader repository/runtime
  promoted Ninja code
  runtime configs
  monitoring
  risk
  execution
```

A future monorepo is compatible with this design. The relevant boundary is experimental research versus promoted runtime code.
