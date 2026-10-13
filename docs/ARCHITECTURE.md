# Architecture

## Status

Phase 0 architecture freeze.

Ninja is one repository with three conceptual layers:

```text
WORLD
  -> Ninja Tools
  -> Observation
  -> Ninja Labs
  -> Evidence / Signal
  -> Ninja
  -> domain executor
```

The layers are responsibility boundaries, not mandatory services. Phase 0 keeps one repository, one Rust workspace, one Python research environment and one MCP surface.

The guiding rule is:

> Ninja is built outward from falsifiable experiments, not inward from capabilities. A capability is implemented when an experiment requires it.

## Layer 1 — Ninja Tools

Ninja Tools acquires, observes, extracts and preserves information.

Its question is:

> What can we observe?

Responsibilities include:

- discovery;
- historical-source access;
- targeted acquisition;
- prospective monitoring;
- browser/crawler escalation;
- extraction required to create observations;
- replay/preservation;
- acquisition provenance and challenge/failure reporting.

Ninja Tools owns capability adapters and routing around mature external software. It does not reimplement crawlers, browsers, archives or search systems merely to unify implementation language.

Canonical capability families are documented in `docs/NINJA_TOOLS.md` and `tools/catalog.json`.

## Layer 2 — Ninja Labs

Ninja Labs turns observations into scientific evidence.

Its question is:

> What can we demonstrate from the observations?

Responsibilities include:

- attention measurement;
- divergence and polarization;
- narrative structure and novelty;
- propagation and Hawkes processes;
- Transfer Entropy and directed-information diagnostics;
- event morphology;
- statistical estimation;
- ablation and robustness testing;
- chronological validation;
- experimental optimization through bounded tools such as Ax;
- information backtests;
- strategy/backtest promotion validation after an information effect survives.

Ninja Labs owns experimental rules. External scientific libraries are instruments, not epistemic authorities.

Ax, for example, may propose trials inside a preregistered train/validation search space. It must not gain access to an untouched final test window during optimization.

See `docs/NINJA_LABS.md`.

## Layer 3 — Ninja

Ninja consumes validated evidence and produces intelligence suitable for a domain decision system.

Its question is:

> What can we conclude from validated evidence?

Ninja may produce versioned objects such as:

- assessments;
- validated signals;
- opportunity or threat candidates;
- confidence/uncertainty summaries;
- historical-analogue distributions;
- deterministic candidate factors for promotion.

Ninja is not required to execute the final action.

For the current trading domain:

```text
Ninja
  -> validated market intelligence
  -> Master Trader
  -> execution / risk / capital authority
```

Research code, LLMs and experimental processes have no order authority.

## Core contracts

Implementation may place shared contracts in a `ninja-core` crate/package, but `core` is not a fourth product layer.

The minimum conceptual chain is:

```text
Observation -> Evidence -> Signal -> Assessment
```

### Observation

A causal, provenance-bearing record of something observed in an information source.

Observation v1 must be able to preserve at least:

```text
observation_id
source
source_type
platform
published_at
first_seen_at
collected_at
author_id?
thread_id?
parent_id?
entity_refs[]
content_ref
content_hash
engagement_snapshot?
structured_fields
provenance
```

Exact event timestamps must survive Bronze/Silver storage. Aggregated counts are derived Gold artifacts, not replacements for event-level history. This is required so later propagation/Hawkes experiments do not depend on reconstructing discarded timing information.

### Evidence

A result tied to an explicit hypothesis, dataset version, experiment configuration, code revision, metrics and validation procedure.

### Signal

An operational application of evidence that has survived its required validation gates.

### Assessment

A contextual Ninja conclusion. A domain executor may accept, reject or combine it with other constraints.

## Domain model

Ninja remains one repository. Trading and future business work are domain layers, not forks.

Shared science may include:

- attention;
- novelty;
- divergence;
- propagation;
- Hawkes estimation;
- event morphology;
- validation machinery.

Domain-specific science must remain isolated where meaning changes.

### Trading

Owns trading-specific:

- market targets;
- market baselines;
- asset/entity mapping;
- market susceptibility;
- execution-economics promotion criteria;
- Master Trader integration.

### Business

A future business domain may own:

- commercial targets;
- commercial baselines;
- commercial susceptibility;
- business opportunity definitions;
- Business Master integration.

Evidence from one domain does not validate a hypothesis in another domain.

## Research domains

The six analytical domains remain:

1. Attention
2. Divergence
3. Narrative
4. Propagation
5. Event Morphology
6. Susceptibility

These are analytical categories, not services.

## Data plane

The research data convention remains:

```text
Bronze: raw/replayable acquisition artifacts
Silver: normalized typed observations
Gold: experiment-ready features and panels
Query: DuckDB
Lineage: Git + DVC where justified
```

Large payloads should not be copied through MCP context when a file/object/Parquet reference is sufficient.

RAG or semantic knowledge systems may consume the same source material, but they do not replace the causal analytical store required for statistical work.

## MCP boundary

Phase 0 keeps one MCP server.

Conceptual namespaces may evolve toward:

```text
tools.*  acquisition / observation capabilities
labs.*   scientific / experiment capabilities
intel.*  validated intelligence capabilities
```

These namespaces do not justify separate daemons yet. Split MCPs only when deployment, resource, permission or security boundaries provide a measured reason.

## Trading runtime determinism

For a promoted implementation k:

```math
a_{k,t}=\pi_k(M_t,F_{k,t};\theta_k)
```

where:

- `M_t` is market state;
- `F_{k,t}` is the validated Ninja-derived input subset;
- `theta_k` is the frozen parameter set;
- `pi_k` is the deterministic promoted strategy/module;
- `a_{k,t}` is the action produced inside the execution host.

A runtime build must reproduce the same action for the same serialized inputs, code version and frozen parameters.

## Promotion path

```text
hypothesis
-> historical dataset
-> registered experiment
-> chronological OOS validation
-> frozen implementation
-> Master Trader backtest / walk-forward
-> dry-run / shadow
-> live approval
```

The immediate objective is not a trading strategy. It is the first falsifiable information backtest:

```text
market-only
vs
market + Ninja information feature
```

Only after an information effect survives should it be translated into strategy logic.

## Failure isolation

1. Research failures must not affect production execution.
2. Missing/stale Ninja feeds affect only consumers that declare those inputs.
3. `NINJA_ENABLED=false` must preserve existing Master Trader semantics after promotion begins.
4. Existing Master Trader risk controls remain authoritative.
5. Experimental agents, LLMs and Labs processes receive no direct order authority.

## Repository boundary

Current ownership remains:

```text
Ninja repository
  Tools
  Labs
  hypotheses
  datasets/manifests
  experiments
  candidate implementations
  validation evidence
        -> promotion
Master Trader repository/runtime
  promoted Ninja code
  runtime configs
  monitoring
  risk
  execution
```

The important invariant is experimental research versus promoted runtime authority, not the number of Git repositories.