# ADR-002 — Core language and tooling boundary

## Status

Accepted.

## Context

Ninja is still early enough that its implementation language can be chosen before a large runtime surface exists. The project will process large historical datasets, coordinate external acquisition tools, expose capabilities to coding agents, and eventually produce deterministic artifacts for Master Trader.

Memory is a constrained resource, but treating that constraint as a blanket ban on every Python process would force Ninja to reimplement mature scientific and acquisition libraries. That would increase validation risk and slow the research program.

The architectural question is therefore not "Rust, Go or Python everywhere?" It is which code must remain resident and controlled by Ninja, and which capabilities should remain external/native tools.

## Decision

### Resident core: Rust

Rust is the primary language for:

- long-lived Ninja services;
- data/contracts and schemas owned by Ninja;
- orchestration and bounded pipelines;
- provenance/manifests implemented by Ninja;
- agent-facing CLI/MCP tooling;
- future high-throughput components that benefit from predictable memory ownership.

The initial Rust toolchain targets Rust 1.88+ and uses the official Rust MCP SDK for the agent interface.

### External tools remain native

Ninja does not rewrite Scrapy, Crawlee, Playwright, Patchright, Camoufox, Browsertrix, Docling, DVC, DuckDB, Freqtrade or similar tools merely to unify implementation language.

Ninja owns adapters and contracts around capabilities. The upstream tool remains responsible for its native implementation and update cadence.

### Python is not the resident core

Python may run behind an isolated adapter when a scientific/data capability materially benefits from the Python ecosystem and reimplementation would reduce correctness or research velocity.

Such adapters should be:

- batch/disposable rather than resident by default;
- resource bounded;
- version pinned;
- invoked through a typed Ninja contract;
- reproducible from experiment configuration;
- replaceable without changing the experiment's conceptual contract.

### Do not add Go yet

Go is not prohibited. It is deferred.

Adding Rust and Go at project inception would create two build systems, dependency graphs, testing surfaces and sets of conventions before a workload demonstrates the need. A Go service can be introduced later if a measured network/concurrency workload shows a material maintenance or performance advantage.

### Master Trader host boundary

Promoted Ninja research still executes through Master Trader. Because Master Trader/Freqtrade uses Python strategy interfaces, a promoted artifact may include a small deterministic Python strategy/adapter required by that host.

That host adapter does not make the Ninja research/control core Python.

## Agent/tool interface

Ninja exposes its own tooling surface through one MCP server implemented in Rust. Claude Code, Hermes and future MCP-compatible agents consume the same interface.

The first MCP surface exposes only:

- canonical tool catalog;
- local tool/environment diagnostics.

It intentionally does not expose arbitrary shell execution. Capability-specific adapters are added as the research program actually needs them.

## Consequences

Positive:

- predictable resident memory and no Python runtime requirement for Ninja core;
- one agent integration instead of agent-specific tool wrappers;
- external tools can be upgraded/replaced independently;
- research can still use mature scientific libraries where justified;
- avoids premature Rust/Go polyglot complexity.

Costs:

- adapter boundaries must be designed and versioned;
- some workflows will cross process boundaries;
- the team must distinguish resident software from batch research dependencies;
- a promoted Freqtrade strategy can still contain Python because Master Trader owns the production host API.

## Revisit conditions

Revisit this ADR if:

- profiling shows Rust core is not solving the actual memory bottleneck;
- a persistent Python workload proves materially simpler and remains within a measured resource envelope;
- a network service has requirements where Go provides a clear maintenance/performance advantage;
- Master Trader changes its runtime interface away from Python/Freqtrade.
