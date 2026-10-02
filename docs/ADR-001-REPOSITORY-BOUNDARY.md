# ADR-001 — Ninja / Master Trader repository boundary

**Status:** revised  
**Date:** 2026-10-02

## Context

The project has two separate placement questions:

1. where research and experimental dependencies should live;
2. where validated trading code should execute.

They do not require the same repository boundary.

## Decision

### Research

Ninja remains a separate repository during the research phase.

It contains:

- historical information datasets and manifests;
- literature and mathematical framework;
- feature engineering;
- Event Morphology research;
- Hawkes and information-flow experiments;
- local-model evaluation;
- failed hypotheses;
- validation evidence;
- candidate implementations.

### Runtime

Validated Ninja implementations normally execute in Master Trader.

A promoted artifact may be:

- a Freqtrade strategy;
- a deterministic overlay used by an existing strategy;
- a deterministic risk/regime module;
- an optional feed service required by one of those implementations.

It uses the same registry, monitoring, risk controls and live/dry-run semantics as the existing fleet.

## Rationale

Research may require large datasets, browser automation, embeddings, PyTorch, graph libraries and other experimental dependencies. Those dependencies do not belong in the trading runtime unless a promoted implementation requires them.

The separation therefore isolates research without creating a second trading system.

## Invariant

Research code has no order authority. Promotion requires a concrete deterministic implementation.

```text
Ninja research
        ↓
validated Python artifact
        ↓
Master Trader fleet
        ↓
shared risk / monitoring / execution
```

## Family switch

Target behavior:

```text
NINJA_ENABLED=false
→ Ninja family absent; existing fleet unchanged

NINJA_ENABLED=true
→ individually enabled Ninja bots may run
```

## Live data

Promoted Ninjas may depend on optional collector/feed services. These services provide data; they do not own trading decisions.

## Monorepo alternative

A future monorepo is compatible with the decision:

```text
Master-Trader/
  research/ninja/
  ft_userdata/user_data/strategies/Ninja*.py
  services/ninja-data/
```

Repository topology is secondary to the research/runtime boundary.

## Superseded design

The earlier mandatory chain

```text
NinjaState → Policy Engine → Master Trader
```

is not part of the current architecture. A research feature vector remains useful analytically, but is not required in production.
