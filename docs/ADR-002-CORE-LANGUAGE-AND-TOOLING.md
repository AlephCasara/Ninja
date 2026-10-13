# ADR-002 — Core language and tooling boundary

## Status

Accepted.

## Context

Ninja is still early enough that its implementation language can be chosen before a large runtime surface exists. The project will process large historical datasets, coordinate external acquisition tools, expose capabilities to coding agents, and eventually produce deterministic artifacts for Master Trader.

Memory is a constrained resource, but treating that constraint as a blanket ban on Python would force Ninja to reimplement mature scientific, quantitative and acquisition libraries. That would increase validation risk and slow the research program.

The architectural question is therefore not "Rust, Go or Python everywhere?" It is which responsibilities benefit from a systems-language core and which responsibilities benefit from the scientific Python ecosystem.

## Decision

### Rust is the default implementation language

Rust is the primary/default language for code owned by Ninja, especially:

- long-lived Ninja services;
- data contracts and schemas owned by Ninja;
- orchestration and bounded pipelines;
- provenance/manifests implemented by Ninja;
- agent-facing CLI/MCP tooling;
- acquisition routing and process supervision;
- future high-throughput components that benefit from predictable memory ownership.

The initial Rust toolchain targets Rust 1.88+ and uses the official Rust MCP SDK for the agent interface.

New core/runtime code should start in Rust unless another language has a concrete technical advantage for that workload.

### Python is a first-class research language

Python is explicitly supported where it materially improves scientific correctness, validation quality or research velocity. Expected uses include:

- statistical analysis and econometrics;
- time-series research;
- machine-learning and semantic-model evaluation;
- feature prototyping;
- backtesting, walk-forward analysis and Freqtrade integration;
- notebooks and exploratory analysis;
- scientific libraries whose validated/reference implementations are Python-native;
- batch data transformations where a Python implementation is substantially simpler and resource use is bounded.

Python research code is not second-class or considered a temporary defect. It must follow the same reproducibility rules as Rust code: pinned dependencies, deterministic experiment configuration where applicable, dataset/artifact versions, no-lookahead tests and recorded code commits.

For heavy Python jobs, prefer batch/ephemeral execution, streaming/chunking and explicit memory limits. A long-lived Python service is allowed when latency, library constraints or operational simplicity justify it, but should be a conscious measured choice rather than the default control-plane architecture.

### External tools remain native

Ninja does not rewrite Scrapy, Crawlee, Playwright, Patchright, Camoufox, Browsertrix, Docling, DVC, DuckDB, Freqtrade or similar tools merely to unify implementation language.

Ninja owns adapters and contracts around capabilities. The upstream tool remains responsible for its native implementation and update cadence.

### Do not add Go yet

Go is not prohibited. It is deferred.

Adding Rust and Go at project inception would create two systems-language build systems, dependency graphs, testing surfaces and sets of conventions before a workload demonstrates the need. A Go service can be introduced later if a measured network/concurrency workload shows a material maintenance or performance advantage.

### Master Trader host boundary

Promoted Ninja research still executes through Master Trader. Because Master Trader/Freqtrade uses Python strategy interfaces, a promoted artifact may include a deterministic Python strategy/adapter required by that host.

That is a normal supported Python boundary, not an exception that must be removed.

## Agent/tool interface

Ninja exposes its own tooling surface through one MCP server implemented in Rust. Claude Code, Hermes and future MCP-compatible agents consume the same interface.

The first MCP surface exposes only:

- canonical tool catalog;
- local tool/environment diagnostics.

It intentionally does not expose arbitrary shell execution. Capability-specific adapters are added as the research program actually needs them.

## Consequences

Positive:

- predictable resident memory for the default control plane;
- full access to the Python scientific/quantitative ecosystem where it creates real value;
- one agent integration instead of agent-specific tool wrappers;
- external tools can be upgraded/replaced independently;
- avoids premature Rust/Go polyglot complexity;
- language choice follows workload rather than ideology.

Costs:

- Rust/Python boundaries must be designed and versioned where they cross;
- some workflows will cross process boundaries;
- Python environments still require dependency discipline;
- the team must distinguish core/runtime requirements from research convenience.

## Practical rule

Use the smallest justified runtime for each job:

```text
resident control/orchestration/high-throughput service -> Rust by default
scientific/statistical/backtesting/ML research          -> Python when advantageous
mature external tool                                   -> use its native implementation
second systems language                                -> only after measured justification
```

## Revisit conditions

Revisit this ADR if:

- profiling shows Rust core is not solving the actual memory bottleneck;
- a persistent Python workload proves operationally superior and remains within a measured resource envelope;
- a network service has requirements where Go provides a clear maintenance/performance advantage;
- Master Trader changes its runtime interface away from Python/Freqtrade.
