# ADR-001 — Ninja / Master Trader repository boundary

**Status:** provisional architecture decision  
**Date:** 2026-10-02

## Context

There are two defensible implementation positions.

### Position A — separate Ninja repository

Ninja has a research lifecycle substantially different from Master Trader:

- historical social/news datasets;
- crawling and scraping;
- large temporary data;
- embeddings and local models;
- NLP/event extraction;
- Hawkes/network/information-theory research;
- experimental dependencies;
- frequent failed hypotheses;
- research artifacts;
- serving code that may evolve independently.

Master Trader, by contrast, is primarily a deterministic trading/operations runtime containing:

- Freqtrade strategies;
- signal receivers;
- risk controls;
- monitoring;
- portfolio logic;
- execution.

A separate repository reduces dependency and data/research contamination of the trading runtime.

### Position B — everything inside Master Trader

This is also technically defensible.

Advantages:

- one repository;
- atomic code changes;
- easier local development;
- no cross-repo version management;
- integration tests live beside strategies;
- less organizational overhead.

If Ninja ultimately becomes only a small set of deterministic Python features, a separate repository could become unnecessary architecture.

## Decision

The **logical boundary is required; the physical repository boundary is provisional**.

Today Ninja remains a separate repository because the current work is primarily

$$
research + data + probabilistic\ extraction
$$

rather than

$$
production\ trading\ logic.
$$

However, Ninja must be designed so its serving component can later be:

- moved into a Master Trader package;
- vendored;
- used as a git subtree/submodule;
- deployed as a local sidecar/service;
- consumed by files, IPC or HTTP;

without changing the scientific semantics of the feature contract.

## Required boundary

Regardless of repository topology:

~~~text
Unstructured / probabilistic research
        ↓
Ninja feature contract
════════ deterministic boundary ════════
Master Trader policy / risk / execution
~~~

This boundary matters more than whether GitHub shows one repository or two.

## Why separate during the research phase

### Dependency isolation

Research may require:

- Polars / DuckDB;
- embedding runtimes;
- PyTorch / transformers;
- graph libraries;
- Hawkes / Transfer Entropy estimators;
- browser/crawler stacks.

The trading runtime should not inherit these dependencies unless operationally necessary.

### Data isolation

Large corpora and temporary caches do not belong in the trading deployment context.

### Failure isolation

A broken crawler, expired browser session or unavailable local model must not affect trading execution.

### Epistemic isolation

Experimental features should not become accidental production assumptions merely because they live beside strategy code.

### Independent release cadence

Ninja may iterate quickly on data science while Master Trader remains conservative.

## What would justify merging later?

Revisit this ADR if most of the following become true:

1. Ninja live serving is small;
2. research dependencies are not needed by serving;
3. only a few stable deterministic factors survive;
4. cross-repository versioning creates more complexity than it removes;
5. Master Trader maintainers prefer a single release unit;
6. dependency/data isolation can be preserved inside a monorepo.

A future layout could be:

~~~text
Master-Trader/
  ninja/
    serving/
    policies/
    schemas/
~~~

while heavy historical research remains elsewhere or archived.

## What would justify permanent separation?

Keep Ninja separate if it becomes a reusable information engine with:

- multiple consumers;
- substantial independent data acquisition;
- separate deployment cadence;
- large model/runtime dependencies;
- non-Master-Trader research use;
- independent feature/version serving.

## Contract-first integration

Master Trader should depend on a **contract**, not Ninja internals.

For example:

~~~text
ninja.features/1.x
~~~

Master Trader should not import:

- crawler implementations;
- LLM clients;
- embedding models;
- historical-dataset code.

## First Master Trader integration PR

The initial integration should ideally contain only:

1. optional Ninja configuration;
2. read-only feature-contract client;
3. schema and freshness validation;
4. shadow logging;
5. tests proving Ninja OFF parity.

No scientific model needs to live in that PR.

## Consequence

The objection that Ninja should simply live inside Master Trader is treated as a valid architectural alternative.

The current two-repository decision is a **research-phase optimization**, not an ideological commitment.

The design is successful only if moving the deterministic serving layer into Master Trader later would be straightforward.
