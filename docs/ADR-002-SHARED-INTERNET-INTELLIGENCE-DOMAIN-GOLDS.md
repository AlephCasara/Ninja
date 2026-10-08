# ADR-002 — Shared Internet Intelligence substrate and domain Gold layers

**Status:** accepted for architecture  
**Date:** 2026-10-08

## Context

Ninja began as a research/validation project for public-information signals used by Master Trader. A second consumer now needs many of the same expensive upstream capabilities: Business Master requires public Internet observations to estimate demand, competition, creative patterns and business economics before spending capital on experiments.

The expensive upstream problems are largely domain-agnostic:

- discovery;
- HTTP/browser/archive acquisition;
- challenge handling and retries;
- point-in-time capture;
- raw-payload preservation;
- hashes/manifests and provenance;
- timestamp semantics such as `published_at`, `first_seen_at` and `collected_at`;
- deduplication;
- canonical entity resolution;
- historical snapshots;
- normalization;
- reproducible dataset construction.

Duplicating those capabilities into `Ninja Trade`, `Ninja Business`, Master Trader and Business Master would create divergent crawlers, timestamp semantics, provenance rules and storage systems.

At the same time, the *meaning* of normalized observations is domain-specific. A ranking trajectory may become a trading-information feature in one research program and a demand/saturation feature in another. Shared acquisition does not imply a universal score or a universal downstream model.

## Decision

Keep **one Ninja repository and one shared Internet Intelligence substrate** for now.

Ninja may serve multiple downstream domains through a layered data model:

```text
                         NINJA

Discovery / Acquisition / Capture / Provenance
                         │
                         ▼
                       BRONZE
              raw point-in-time reality
                         │
                         ▼
                       SILVER
          normalized entities + observations
                         │
             ┌───────────┴───────────┐
             ▼                       ▼
        GOLD / TRADE            GOLD / BUSINESS
             │                       │
   validated market/info      decision-grade business
        research features          market features
             │                       │
             ▼                       ▼
       MASTER TRADER           BUSINESS MASTER
```

### Bronze — shared

Bronze preserves acquired reality and enough metadata to reproduce or audit later transformations.

Typical contents include:

- WARC/WACZ or equivalent raw captures where appropriate;
- raw API/JSON/HTML payloads;
- content hashes;
- source URL/source identity;
- acquisition method;
- `published_at` when supplied by the source;
- `first_seen_at` when first observed by Ninja;
- `collected_at` for the concrete capture;
- capture/provider metadata;
- reproducibility manifests.

Bronze does **not** assign trading or business meaning.

### Silver — shared

Silver contains domain-neutral normalized reality.

Typical responsibilities include:

- canonical entities and source aliases;
- normalized observations and units;
- deduplication/near-duplicate identity;
- relationships among entities/documents/assets;
- point-in-time snapshots;
- source/provenance references;
- normalized timestamps;
- normalized text/media metadata where useful.

Silver should not contain a generic `NinjaScore` or a universal economic interpretation.

### Gold — domain-specific

Gold contains small, decision-oriented feature sets derived for a concrete consumer or research domain.

Gold schemas may share implementation primitives, but their semantics and validation criteria remain separate.

#### Trade Gold

The existing financial-information research remains valid. Candidate feature families include the current Ninja research domains, such as:

- attention;
- divergence;
- narrative structure;
- propagation;
- event morphology;
- market susceptibility/context.

Only validated features should be promoted into Master Trader runtime artifacts, following ADR-001 and the existing research ladder.

#### Business Gold

Business Market Intelligence initially organizes candidate features into four families:

```text
MARKET INTELLIGENCE
│
├── DEMAND
│   ├── views
│   ├── searches
│   ├── rankings
│   ├── growth
│   └── velocity
│
├── COMPETITION
│   ├── sellers
│   ├── advertisers
│   ├── products
│   ├── prices
│   └── saturation proxies
│
├── CREATIVE
│   ├── title
│   ├── thumbnail
│   ├── hook
│   ├── format
│   ├── duration
│   ├── script
│   └── observed performance
│
└── ECONOMICS
    ├── price
    ├── offer
    ├── ranking/sales proxies
    ├── reviews
    ├── fulfillment
    └── monetization structure
```

These are **feature families, not mandatory services, universal schemas or assumed truths**. Each concrete feature must retain source/provenance, observation time, derivation/version information and an explicit interpretation boundary.

Business Gold may produce small decision-grade artifacts such as:

```text
entity/reference
feature name + value
observation window
freshness
source/provenance
input lineage or dataset reference
confidence/quality metadata when justified
```

Business Master converts relevant Gold outputs into its own evidence/hypothesis model. Ninja does not own Business Master's economic decisions, capital allocation, experiments, ledger, monetization or execution policy.

## Consumer boundaries

### Master Trader

Consumes only promoted deterministic trading artifacts or typed feeds justified by validated Ninja research. Master Trader retains order/risk authority.

### Business Master

Consumes only decision-grade market intelligence required to form priors, rank opportunities and reduce uncertainty before real-world experiments. Business Master retains economic interpretation, portfolio/capital authority, business execution and first-party economic truth.

Therefore:

```text
Ninja knows/reconstructs public reality.
Consumers decide what that reality means for their own objective.
```

## Why not `Ninja Trade` and `Ninja Business` forks now?

Forks would duplicate the highest-cost infrastructure while the acquisition and normalization invariants are still shared.

A single repository currently gives:

- one acquisition router;
- one point-in-time/provenance model;
- one archive/capture pipeline;
- one canonical entity model;
- one storage lifecycle;
- one set of causal-data invariants;
- reuse of collectors across multiple consumers;
- less operational and dependency drift.

Domain separation happens at Gold and at downstream consumer boundaries rather than by copying Bronze/Silver infrastructure.

## When a split would become justified

A future repository/runtime split is allowed if evidence shows a concrete incompatibility, for example:

1. one domain requires materially different security/authority boundaries;
2. dependency/runtime requirements make a shared deployment operationally harmful;
3. release cadence or availability requirements become incompatible;
4. storage/acquisition policies diverge enough that shared infrastructure creates coupling rather than reuse;
5. organizational ownership requires independent lifecycle management.

If none of those conditions exists, repository topology should not be used as a substitute for clean domain boundaries.

A split should preferentially preserve a reusable shared acquisition/storage core rather than fork the whole project.

## Tool/provider rule

Ninja owns contracts and routing, not crawler brands.

Potential acquisition implementations may include native HTTP clients, Crawlee, Scrapy, Playwright-family browsers, archives/Common Crawl, Firecrawl, Spider or other providers where measured behavior justifies them.

Adding a tool is not an architectural milestone. The acquisition router should choose the smallest reliable path for the source and workload.

## Non-goals

This ADR does **not**:

- turn Ninja into Business Master;
- give Ninja trading or business-action authority;
- require downloading the entire Internet;
- require every Bronze/Silver/Gold layer to be a separate service;
- require a data lake technology before workload evidence exists;
- require all four Business Gold families to be implemented immediately;
- replace the existing Ninja scientific validation rules for trading research.

## Invariants

1. Point-in-time semantics and provenance survive every layer.
2. Derived features are traceable to their inputs or reproducible dataset references.
3. Shared Bronze/Silver data remains semantically neutral with respect to downstream objectives.
4. Gold meaning is domain-specific.
5. Ninja never acquires downstream capital/order/business authority merely because it provides data.
6. Consumers should receive the smallest decision-grade artifact they need, not the entire historical corpus.
