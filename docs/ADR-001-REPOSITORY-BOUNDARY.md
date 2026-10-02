# ADR-001 — Ninja / Master Trader repository boundary

**Status:** revised  
**Date:** 2026-10-02

## Context

Two separate questions were being mixed together:

1. where should Ninja research live?
2. where should validated Ninja trading code execute?

They do not need the same answer.

## Decision

### Research

Ninja remains a separate repository during the research phase.

It owns:

- historical information datasets/manifests;
- literature and mathematical framework;
- feature engineering;
- event morphology research;
- Hawkes / information-flow experiments;
- local-model evaluation;
- failed hypotheses;
- validation evidence;
- candidate implementations.

### Runtime

Validated Ninja implementations should normally execute **inside the Master Trader runtime model**.

A promoted Ninja may become:

- a Freqtrade strategy;
- a deterministic overlay used by an existing strategy;
- a deterministic risk/regime module;
- an optional data-feed service required by one of those implementations.

It should use the same registry, monitoring, risk and live/dry-run concepts as the existing fleet.

## Why this split

The research stack may require large datasets, browsers, embeddings, PyTorch, graph libraries and experimental dependencies.

The runtime bot should not.

Separating research from production therefore has operational value without requiring Ninja to become a permanent external trading microservice.

## Required invariant

Research code has zero order authority.

Promotion requires a concrete deterministic implementation.

Conceptually:

```text
Ninja research repository
        ↓
validated Python artifact
        ↓
Master Trader fleet
        ↓
shared risk / monitoring / execution
```

## Global enable/disable

The intended Master Trader behavior is:

```text
NINJA_ENABLED=false
→ Ninja family absent; current fleet unchanged

NINJA_ENABLED=true
→ individually enabled Ninja bots may run
```

This matches the existing multi-bot architecture more closely than introducing a separate generic Ninja policy runtime.

## Live data

A Ninja that needs current public-information features may depend on optional collector/feed services.

Those services can remain separately packaged if useful, but they are data providers, not trading authorities.

## Alternative: monorepo

A future monorepo is still valid.

For example:

```text
Master-Trader/
  research/ninja/
  ft_userdata/user_data/strategies/Ninja*.py
  services/ninja-data/
```

The repository layout is secondary.

The important distinction is:

- experimental research;
- promoted deterministic runtime code.

## Consequence

The original idea of a mandatory `NinjaState → Policy Engine → Master Trader` chain is rejected as unnecessary abstraction.

A research feature vector may still be useful analytically, but it is not a required production component.
