# Ninja Tools

## Purpose

Ninja Tools is Ninja's acquisition, observation and preservation arsenal.

Its question is:

> What can we observe, reconstruct or preserve well enough to support a scientific experiment?

Ninja Tools is intentionally distinct from Ninja Labs:

```text
WORLD
  -> Ninja Tools
  -> Observation
  -> Ninja Labs
  -> Evidence / Signal
```

Tools obtains information. Labs determines whether that information contains reproducible, useful structure.

Ninja Tools is not a vendored collection of third-party projects. Mature projects remain in their native implementations. Ninja owns the capability contracts, routing, provenance, escalation policy and agent-facing interface around them.

The canonical inventory is `tools/catalog.json`.

## Architecture

```text
Claude Code / Hermes / future MCP clients
                 |
                 v
        ninja-tooling (Rust)
        CLI + MCP stdio server
                 |
        deterministic routing
                 |
        typed capability adapters
                 |
   +-------------+--------------+----------------+
   |             |              |                |
 discovery   historical     targeted         prospective
             acquisition    acquisition      observation
   |             |              |                |
 SearXNG      Common Crawl    HTTP/browser    watchers
 Last30Days   Arctic Shift    crawlers        source APIs
 GDELT        archives/APIs   protocol obs.   page changes
 SurfSense                   preservation      capture
                 |
                 +--------------------+
                                      v
                                preservation
                                WARC/WACZ/hash
                                      |
                                      v
                                 Observation
```

Large payloads belong in files/object stores/Parquet or replayable artifacts. MCP should normally return typed metadata and references rather than copying entire corpora into agent context.

## Capability classes

### 1. Discovery

Discovery answers:

> Where should Ninja look?

Candidate surfaces include:

- SearXNG;
- Last30Days;
- SurfSense;
- GDELT discovery/query surfaces;
- RSS/Atom/sitemaps;
- Common Crawl index;
- source-specific search APIs.

Discovery output is a lead, not automatically research evidence.

### 2. Historical acquisition

Historical acquisition answers:

> What information existed, or can be reconstructed, for a past experiment window?

Prefer structured or archived sources before attempting expensive reconstruction.

Candidate sources include:

- Arctic Shift for historical Reddit data;
- GDELT event/news history;
- Common Crawl indexes and WARC records;
- exchange/public market archives;
- government/institutional archives;
- source-specific historical APIs or bulk datasets.

For backtesting, this capability class is generally more valuable than building a live crawler first.

### 3. Targeted acquisition

Targeted acquisition answers:

> We know which source/object matters. How do we retrieve it reliably?

Prefer the cheapest method that preserves the required information. The default escalation order is conceptual rather than a guarantee that every source will traverse every step:

```text
archive/feed/API
      -> ordinary HTTP
      -> browser-like HTTP
      -> Crawl4AI / crawler
      -> normal deterministic browser
      -> authorized authenticated browser session
      -> semantic browser fallback
      -> alternate browser engine
      -> authorized human/session handoff
```

Candidate/native tools include:

- `curl_cffi` for cheap browser-like HTTP;
- Crawl4AI for agent-oriented crawling/extraction;
- Crawlee or Scrapy for frontier/concurrency/retry-heavy crawls;
- Playwright for ordinary deterministic browser automation;
- Browser Control as the preferred path for an existing Chromium browser and authorized authenticated sessions;
- Stagehand as a semantic fallback when deterministic DOM interaction is materially fragile;
- Patchright, Camoufox and CloakBrowser as measured challengers rather than automatic defaults;
- source-specific clients whenever a structured interface exists.

Do not make any single crawler or browser engine a hard dependency of the scientific model. Tool promotion is based on measured acquisition success, latency, maintenance cost and downstream information gain.

### 4. Protocol observation and interface reconstruction

Protocol observation answers:

> What structured interface did an authorized browser/application actually use, and can a repeated browser action be replaced by a narrower reproducible adapter?

Preferred tools include:

- mitmproxy for authorized HTTP(S)/WebSocket observation, replay and debugging;
- mitmproxy2swagger for producing candidate OpenAPI descriptions from captured flows.

Protocol observation is an interoperability/debugging capability, not an authorization bypass. Captured traffic can contain credentials, session identifiers or private payloads, so adapters must scope captures deliberately, sanitize secrets before durable storage and record capture provenance.

A generated OpenAPI description is a hypothesis about an interface until controlled validation confirms the relevant methods, fields and state transitions.

### 5. Prospective observation

Prospective observation answers:

> From now on, what changed and when did Ninja actually see it?

Candidate capabilities include:

- changedetection-style sentinels;
- source webhooks/APIs;
- periodic collectors;
- page/content hashes;
- replayable browser capture where justified;
- watchlists seeded by discovery systems.

Prospective collection is especially important for reliable `first_seen_at` timestamps.

### 6. Extraction required for observation

Extraction converts acquired material into a typed observation without performing the scientific interpretation that belongs to Labs.

Candidate tools include:

- Trafilatura for main-content extraction;
- Docling for complex documents/PDFs/tables;
- Crawl4AI when acquisition and bounded extraction are naturally coupled;
- source-specific parsers when structured source data exists;
- deterministic field extraction;
- semantic extraction only when deterministic parsing is insufficient.

Raw acquisition and extracted output are separate artifacts with separate identities/hashes.

### 7. Preservation

For mutable/high-value evidence, preserve enough raw material to audit what Ninja actually observed.

Preferred artifacts include:

- content/raw-response hash;
- retrieval metadata;
- raw response/source payload where policy/storage permits;
- WARC/WACZ capture where future replay matters;
- extraction output separately from the raw evidence.

Browsertrix Crawler is the preferred selective replay-preservation candidate for browser-derived evidence. It is a sidecar capability, not the default crawler for every source.

## Deterministic routing

`ninja-tooling` exposes a deterministic route planner. It recommends tools; it does not execute arbitrary commands or silently install software.

CLI:

```bash
cargo run -p ninja-tooling -- route authenticated-browser
cargo run -p ninja-tooling -- route dynamic-web --preserve
cargo run -p ninja-tooling -- route dynamic-web --inspect-protocol --preserve
```

MCP:

```text
ninja_tool_route({
  "profile": "authenticated-browser",
  "preserve": true,
  "inspect_protocol": false
})
```

Supported profiles:

```text
discovery
historical
static-web
high-throughput-web
dynamic-web
authenticated-browser
semantic-browser
protocol-observation
replay-capture
complex-document
```

Routing is intentionally explicit and falsifiable. A profile maps to ordered primary tools, fallbacks and optional sidecars. Experiments can later compare that policy against alternatives without changing scientific semantics.

## Challenge handling

Acquisition challenges are explicit outcomes, not hidden failures.

Adapters should record, where observable:

- challenge detected;
- passive/JavaScript challenge;
- interactive challenge;
- retry/escalation path;
- authorized session or human handoff when applicable;
- final acquisition status;
- latency;
- failure reason;
- tool/engine identity.

A challenge never silently changes Ninja's authorization boundary. Authentication, CAPTCHA, paywall or anti-abuse controls are not permission to bypass them. If the required information is unavailable through an authorized route, the acquisition may fail and that failure is part of the observation record.

Ninja Tools may compare acquisition techniques scientifically by coverage, success rate, latency, cost, maintenance burden and downstream information gain. Sophistication that does not improve usable evidence can be rejected later without deleting the broader capability from the catalog.

Credentials or secrets do not belong in Git. Access-control boundaries remain explicit in adapters and experiment manifests.

## Observation boundary

The primary output of Tools is a typed Observation or a reference to raw material from which one can be deterministically reconstructed.

Observation v1 is finalized in Phase 0. It must preserve enough temporal detail for later propagation work, including exact event timestamps when available.

Important temporal fields include:

```text
published_at
first_seen_at
collected_at
```

Present-day mutable fields such as current likes/views/ranking must never be silently backfilled as if they were historical point-in-time values.

## Data handoff

Tools feeds the research data plane:

```text
Bronze: raw/replayable acquisition artifacts
Silver: normalized typed observations
Gold: experiment-ready features/panels
```

Tools primarily owns Bronze acquisition provenance and the path into Silver observations. Gold analytical feature construction belongs to Ninja Labs.

DuckDB, Polars, statistical libraries, Ax and backtesting systems are therefore Labs instruments even when they appear in a shared project-level tool inventory.

## Process model

1. Rust owns the default resident Ninja control/orchestration plane, contracts, deterministic routing and agent-facing MCP surface.
2. External acquisition tools run in their native runtime.
3. Prefer ephemeral/batch execution for expensive extraction/capture when latency does not require residency.
4. Prefer streaming, iterators, bounded queues and file/object references over whole-corpus resident objects.
5. A service becomes long-lived only when latency/throughput requirements justify it.
6. Protocol captures and authenticated-browser state are sensitive artifacts and receive explicit retention/sanitization policy.

Ninja does not rewrite Scrapy, Crawlee, Playwright, Crawl4AI, Stagehand, Browser Control, mitmproxy, Camoufox, Browsertrix or similar systems merely to standardize implementation language.

## Agent integration

The repository commits `.mcp.json` with a project-scoped `ninja-tooling` stdio server.

The current server exposes:

- `ninja_tool_catalog` — canonical capability/tool inventory;
- `ninja_tool_doctor` — locally discoverable CLI diagnostics;
- `ninja_tool_route` — deterministic acquisition routing by workload profile.

This remains intentionally smaller than exposing arbitrary commands from every external package.

Potential future Tools-level capabilities include:

```text
tools.discover
tools.acquire
tools.capture
tools.watch
tools.archive
tools.status
```

Names are conceptual until a real experiment requires the adapter.

## Adapter design rules

A future adapter exposes a bounded capability rather than mirroring an upstream package's complete command surface.

Good examples:

```text
acquire_article(url, capture_policy)
search_reddit(query, time_window)
capture_page(url, replay=true)
inspect_authorized_flow(target, capture_policy)
watch_resource(target, policy)
retrieve_historical_events(query, interval)
```

Each adapter should define:

- typed input;
- typed output or reference to large output;
- tool/version identity;
- bounded timeout/resource policy;
- provenance fields;
- temporal semantics;
- failure/challenge states;
- authorization/sensitivity boundary where relevant;
- deterministic configuration where an experiment depends on it.

## Why MCP

Claude Code, Hermes and future MCP clients can consume one project capability surface.

This provides:

- one contract vocabulary;
- one permission/audit surface;
- one tool catalog;
- one deterministic routing policy;
- no duplicated integration logic per coding agent.

Phase 0 keeps one MCP server for the whole project. `tools.*`, future `labs.*` and `intel.*` are conceptual namespaces; separate daemons are introduced only after a measured deployment or permission need exists.

## Near-term implementation order

1. Keep catalog, doctor and deterministic routing stable and compile-tested.
2. Select the first canonical historical source for E1.
3. Add only the acquisition adapter required by that source.
4. Finalize Observation v1, manifests and causal alignment.
5. Produce Bronze/Silver input for E1.
6. Preserve event-level timestamps/source identity so E3/Hawkes remains possible later.
7. Promote Browser Control/Crawl4AI/protocol-observation/preservation adapters only when an actual experiment or business-domain acquisition requires them.
8. Benchmark Stagehand and alternate browser engines only where the preferred deterministic route measurably underperforms.
9. Add prospective watchers after historical validation creates a reason to collect point-in-time evidence going forward.

Ninja Tools can maintain a broad arsenal in its catalog. Implementation priority is determined by scientific or domain need, not by the number of available tools.
