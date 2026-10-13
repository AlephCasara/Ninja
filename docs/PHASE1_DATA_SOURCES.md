# Phase 1 data sources

## Objective

Phase 1 exists to build the first reproducible historical substrate for E1 Attention Replication. The initial vertical slice is deliberately narrow:

```text
historical Reddit attention
        +
BTCUSDT spot market state
        ->
causally aligned information panel
```

The source choice is an experimental dependency, not a permanent platform commitment.

## Historical information — Arctic Shift

Base service:

```text
https://arctic-shift.photon-reddit.com
```

Initial communities:

```text
r/Bitcoin
r/CryptoCurrency
```

### Two acquisition modes

Ninja deliberately uses two Arctic Shift paths for different workloads.

#### API mode — smoke tests and targeted gaps

Endpoint:

```text
/api/posts/search
```

The API adapter is bounded, paced and loss-aware. It recursively subdivides a time interval when a query times out or returns a full result page instead of assuming a capped page is complete. If even a one-second interval cannot be represented safely, acquisition fails and requires a bulk/archive path.

API mode is useful for:

- short live smoke tests;
- targeted historical slices;
- filling/rechecking small gaps;
- source diagnostics.

It is **not** the preferred way to materialize the five-year canonical E1 corpus.

#### JSONL mode — canonical historical corpus

Arctic Shift exposes a subreddit download tool. For each canonical community, download **posts** and retain the post JSONL; E1 does not require comments yet. The expected post files are:

```text
r_Bitcoin_posts.jsonl
r_CryptoCurrency_posts.jsonl
```

Place them under:

```text
.ninja-inputs/arctic-shift/
```

The files can be produced by the Arctic Shift download tool; compatible subreddit-level retrievers may also be used if they preserve the same underlying records. The Ninja adapter streams JSONL line by line, filters the frozen experiment interval/community set, deduplicates post IDs, and never materializes the entire input in memory.

The source files are not committed to Git. Their SHA-256 and byte size are recorded in the dataset manifest.

This path avoids thousands of API calls, avoids downloading all of Reddit, and preserves the selective-laboratory design of Ninja. Full all-Reddit monthly dumps remain a fallback, not the default.

### Why Arctic Shift is suitable for E1

Records expose the fields needed by the first attention experiment, including:

- `id`;
- `author`;
- `created_utc`;
- `retrieved_on`;
- `subreddit`;
- title/body material.

`retrieved_on` is especially important. Ninja uses it as an archive-capture approximation for when the record was available to the collector. When it exists:

```text
published_at = created_utc
first_seen_at = retrieved_on
available_at = max(created_utc, retrieved_on)
available_at_basis = archive_capture
```

If `retrieved_on` is absent, Ninja falls back to the source timestamp and records the weaker temporal quality explicitly.

### Known limitations

- Arctic Shift explicitly provides no uptime/performance guarantee.
- Search requests can time out for broad/high-volume queries and can ask clients to slow down.
- Present `score` and `num_comments` values are mutable. Upstream notes that engagement fields are updated after initial archival. They are therefore excluded from the first E1 causal feature set.
- A historical archive capture is not identical to a true prospective `first_seen_at`. The distinction remains in the Observation contract.
- JSONL files are external research inputs. Their hashes identify the exact source corpus used by an experiment.

## Live smoke evidence

A real-source seven-day smoke test completed successfully against Arctic Shift API + Binance for:

```text
2025-01-01 <= t < 2025-01-08
r/Bitcoin
BTCUSDT 15m
```

Observed output:

```text
Reddit observations       1,901
unique authors            1,487
archive-capture rows      1,901
weak source-time rows         0
market candles              672
market gaps                   0
attention windows            672
non-zero windows             612
zero windows                  60
max posts / 15m               23
future-window violations       0
future-observation violations  0
```

The 672 market rows are exactly seven days of 15-minute candles. The smoke therefore validates the acquisition → Bronze → Silver → Gold → causal alignment path, not the scientific E1 hypothesis itself.

The bounded API smoke required several minutes even for one week, reinforcing the decision to use subreddit JSONL downloads for the canonical 2021–2025 corpus.

## Market baseline — Binance public market data

Market-data-only base URL:

```text
https://data-api.binance.vision
```

Initial endpoint:

```text
/api/v3/klines
```

Initial market:

```text
BTCUSDT spot
15m klines
```

The public market-data endpoint does not require API authentication. Binance also publishes downloadable daily/monthly public datasets, which remain a candidate for bulk reproduction if REST acquisition becomes unnecessarily slow.

For a kline:

```text
open_time
close_time
decision_time = first instant after close_time
```

Ninja must not use the completed candle as market state before `decision_time`.

## Canonical E1 period

The initial full config freezes:

```text
2021-01-01 <= dataset < 2026-01-01

train          2021-01-01 -> 2024-01-01
validation     2024-01-01 -> 2025-01-01
untouched_test 2025-01-01 -> 2026-01-01
```

These windows are configuration, not evidence. They may only be changed before the untouched test is used; any later change must create a new experiment version and explain why.

## Storage

```text
External source input
  subreddit JSONL, hashed but not committed

Bronze
  filtered raw Arctic Shift records

Silver
  Observation v1 Parquet
  closed market-candle Parquet

Gold
  dense attention windows
  causal market + attention panel

Audit
  coverage.json
  manifest.json
```

Event-level timestamps are retained in Silver even though E1 begins with aggregated attention. This is a deliberate requirement for later E3 propagation/Hawkes experiments.

## Coverage audit

Every materialization emits `coverage.json`, including:

- observation time range and temporal-quality counts;
- unique authors/communities;
- market row count and candle gaps;
- zero/non-zero attention windows;
- aligned rows by split;
- future-window and future-observation violations.

The canonical dataset is not admitted to E1 merely because it materializes successfully. Its coverage audit must first be reviewed.

## Causal invariant

Every information feature used at market decision time `t` must satisfy:

```text
feature_window_end <= t
and
max(observation.available_at) <= t
```

A violation is an error, not a warning.
