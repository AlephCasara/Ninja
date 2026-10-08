# Agent guidance

Ninja is a research and information-acquisition project that promotes only validated deterministic artifacts into Master Trader.

## Read first

Before changing code or experiments, read:

- `docs/ADR-002-CORE-LANGUAGE-AND-TOOLING.md`
- `docs/NINJA_TOOLS.md`
- `CONTRIBUTING.md`

## Implementation boundary

- Resident Ninja core, contracts, orchestration and agent-facing tooling are Rust-first.
- Do not introduce a long-lived Python service into Ninja core.
- Do not rewrite mature external tools merely to make them Rust. Wrap them behind typed adapters and keep the upstream/native implementation.
- Python may be used behind an isolated batch adapter when a scientific/data package materially improves correctness or research velocity. The process should be disposable and bounded, not a resident control plane.
- Do not add Go merely for language diversity. Introduce a second systems language only when a measured workload justifies the additional toolchain and maintenance cost.
- Master Trader remains the production execution host. A promoted Freqtrade artifact may therefore require a small Python strategy/adapter because that is the host interface; that adapter is not the Ninja core.

## Tooling

The canonical external-tool catalog is `tools/catalog.json`.

Use:

```bash
cargo run -p ninja-tooling -- catalog
cargo run -p ninja-tooling -- doctor
```

Do not assume that a catalogued tool is installed. `doctor` reports discoverable CLI binaries where probing is defined.

Claude Code can load the project-scoped MCP server from `.mcp.json`. Hermes can import the Claude Code MCP configuration or point its own MCP configuration at the same `cargo run ... mcp` command.

The MCP surface is intentionally narrow. Do not add a generic shell-execution tool. Add capability-specific adapters with typed inputs/outputs, bounded resource use, provenance and failure reporting.

## Data and memory discipline

- Prefer streaming and bounded queues over loading corpora into memory.
- Large analytical data belongs in Parquet and is queried through DuckDB; do not keep dataset-sized resident objects without a measured reason.
- Dataset/artifact lineage belongs in DVC once the first canonical dataset is selected.
- Every acquired observation must preserve timestamps and provenance required by the no-lookahead policy.
- Raw/high-value web evidence should be hashable and replayable where practical (for example WARC/WACZ capture for mutable sources).

## Research safety rails

- No LLM or agent receives trading authority.
- Discovery/synthesis tools such as Last30Days are reconnaissance, not authoritative experiment inputs.
- Do not treat current mutable engagement fields as historical point-in-time data.
- Do not silently install tools, store credentials in the repo, or bypass authentication/paywalls.
- Interactive access challenges require an authorized/session-aware path or human handoff rather than an untracked workaround.
