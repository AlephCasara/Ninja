# Ninja Tools

## Purpose

Ninja Tools is the capability layer between Ninja research/agents and external acquisition, preservation, parsing, data, semantic, statistical and promotion-validation systems.

It is not a vendored collection of third-party projects. Ninja keeps those projects in their native implementations and owns the contracts, routing, provenance and agent-facing interface around them.

The canonical inventory is `tools/catalog.json`.

## Architecture

```text
Claude Code / Hermes / future MCP clients
                 |
                 v
        ninja-tooling (Rust)
        CLI + MCP stdio server
                 |
        typed capability adapters
                 |
      +----------+-----------+----------------+
      |          |           |                |
 discovery   acquisition  preservation    analysis
      |          |           |                |
 Common       HTTP /       WARC/WACZ       DuckDB
 Crawl        crawlers      Browsertrix    Parquet
 SearXNG      browsers                     DVC lineage
 Last30Days                               Python research
```

The MCP server is intentionally a thin capability/control surface. Large payloads belong in files/object stores/Parquet, not copied through agent context unless the caller explicitly needs them.

## Process model

Memory pressure is controlled primarily through process lifetime and data movement:

1. Rust owns the default resident Ninja control plane, contracts and orchestration.
2. Python is a supported research plane for scientific/statistical/backtesting/ML work where it is the better tool.
3. External tools run in their native runtime.
4. Prefer ephemeral/batch execution for heavy extraction, semantic and statistical jobs when latency does not require residency.
5. Prefer streaming, iterators, bounded queues and Parquet scans over whole-corpus resident objects.
6. A service becomes long-lived only when its latency/throughput/library requirements justify the resident memory cost, regardless of language.

The rule is not `Python is banned`. The rule is `Rust is the default core; Python is used deliberately where the scientific ecosystem creates value`.

## Capability ladder

### Discovery

Use multiple discovery surfaces because no single index sees the whole web:

- Common Crawl index/corpus;
- self-hosted SearXNG;
- RSS/Atom/sitemaps;
- source-specific search/archive APIs;
- Last30Days for current reconnaissance.

Discovery results are leads. They become research evidence only after reproducible acquisition/preservation.

### Acquisition

Prefer the cheapest method that preserves the required information:

```text
archive/feed/API
      -> ordinary HTTP
      -> browser-like HTTP
      -> normal browser
      -> hardened/alternate browser
      -> authorized human/session handoff when interaction is required
```

Candidate/native tools include curl_cffi, Crawlee or Scrapy, Playwright, Patchright, Camoufox and CloakBrowser as a benchmarked challenger.

Do not make any single browser engine a hard dependency of the scientific model.

### Challenge handling

Challenges are a first-class acquisition outcome. Adapters should record, where observable:

- challenge detected;
- passive/JavaScript challenge;
- interactive challenge;
- retry/escalation path;
- human/session handoff;
- final acquisition status;
- latency and failure reason.

The project does not store credentials in Git, bypass paywalls/authentication, or expose a generic CAPTCHA-breaking primitive. Authorized sessions and human resolution may be preserved/reused according to the source's access model.

### Preservation

For mutable/high-value web evidence, preserve enough raw material to audit what Ninja actually saw.

Preferred artifacts:

- content/raw response hash (SHA-256 or stronger as adopted by the manifest schema);
- retrieval metadata;
- raw response or source payload where policy/storage permits;
- WARC/WACZ capture for pages whose future replay matters;
- extraction output separately from the raw evidence.

Browsertrix/Webrecorder-style capture is a preservation capability, not the default crawler for every source.

### Extraction and normalization

Candidate tools:

- Trafilatura for article/main-content extraction;
- Docling for complex documents/PDFs/tables;
- source-specific parsers when structured source data exists;
- semantic models only after deterministic parsing/rules are insufficient.

Raw acquisition and extracted text are separate artifacts with separate hashes/versions.

### Analytical substrate

Preferred initial data plane:

```text
Bronze: raw/replayable acquisition artifacts
Silver: normalized typed observations in Parquet
Gold: experiment-ready features/panels in Parquet
Query: DuckDB
Lineage: Git + DVC
```

PostgreSQL or another resident database is introduced only when concurrent prospective collection requires it.

### Python research plane

Python is explicitly supported for workloads where its scientific ecosystem is an advantage, including:

- NumPy/SciPy/statsmodels/scikit-learn style statistical work;
- time-series and econometric validation;
- feature prototyping and ablations;
- notebooks and exploratory analysis;
- ML/embedding/classifier evaluation;
- purged CV, CPCV, bootstrap/placebo and multiple-testing workflows;
- Freqtrade backtesting, walk-forward analysis and promotion adapters.

Python code used for headline evidence must be reproducible: pinned environment, frozen experiment configuration, dataset/artifact versions, no-lookahead tests, recorded code commit and preserved outputs.

For large jobs, prefer Polars/DuckDB/Arrow/Parquet-style lazy or chunked processing rather than materializing whole datasets into resident DataFrames. A long-lived Python service is allowed only when there is an operational reason for residency; measure its memory footprint rather than rejecting it on language identity alone.

Critical statistical tests should eventually have independent/reference implementations where practical; one third-party package should not be the sole arbiter of whether alpha exists.

### Promotion validation

Freqtrade belongs at the promotion boundary, after a feature/factor survives its research test. E1/E2-style information-value experiments must not be replaced by strategy backtests.

## Agent integration

### Claude Code

The repository commits `.mcp.json` with a project-scoped `ninja-tooling` stdio server.

On first use, build/start cost is paid by Cargo; subsequent release builds reuse Cargo artifacts.

The current server exposes:

- `ninja_tool_catalog` — canonical capability/tool inventory;
- `ninja_tool_doctor` — local PATH availability for probeable CLI tools.

This is deliberately smaller than exposing every command from every browser/crawler package.

### Hermes

Hermes supports local stdio MCP servers. Two supported approaches are:

1. import the Claude Code agent/configuration where that workflow is already used; or
2. point Hermes directly at the same command:

```yaml
mcp_servers:
  ninja-tooling:
    command: cargo
    args:
      - run
      - --quiet
      - --release
      - -p
      - ninja-tooling
      - --
      - mcp
```

Run the agent from the repository root so Cargo resolves the workspace.

## CLI

Without an agent:

```bash
cargo run -p ninja-tooling -- catalog
cargo run -p ninja-tooling -- doctor
cargo run --release -p ninja-tooling -- mcp
```

`doctor` is observational. A missing tool is not permission to install it silently.

## Adapter design rules

A future adapter should expose a capability, not mirror an upstream package's entire command surface.

Good:

```text
acquire_article(url, capture_policy)
search_reddit(query, time_window)
capture_page(url, replay=true)
query_gold(sql_or_named_query)
```

Bad:

```text
run_shell(command)
run_any_browser_method(name, arbitrary_json)
```

Each adapter should define:

- typed input;
- typed output/reference to large output;
- tool/version identity;
- bounded timeout/resource policy;
- provenance fields;
- failure/challenge states;
- deterministic configuration where the experiment depends on it.

## Why MCP instead of agent-specific plugins

Claude Code and Hermes both consume MCP. A single server therefore provides:

- one capability contract;
- one permission surface;
- one audit point;
- one place to filter tools;
- no duplicated integration logic per coding agent.

The CLI and MCP should share the same Rust domain code so humans, CI and agents observe the same catalog and diagnostics.

## Near-term implementation order

1. Keep catalog + doctor stable and compile-tested.
2. Select the first canonical dataset/source for E1.
3. Add only the acquisition adapter needed for that source.
4. Add observation/manifest contracts and causal alignment.
5. Introduce DVC metadata when the dataset is actually created.
6. Add WARC/WACZ preservation for mutable sources that need replay.
7. Add browser/challenge adapters only for sources where HTTP/archive paths are insufficient.
8. Build the Python research environment for E1 statistical validation and backtesting only when the first experiment requires it.

Ninja Tools grows from demonstrated research needs, while the architecture remains capable of much broader web acquisition later.
