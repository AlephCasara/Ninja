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

Canonical API:

```text
https://arctic-shift.photon-reddit.com
```

Initial endpoint:

```text
/api/posts/search
```

Initial communities:

```text
r/Bitcoin
r/CryptoCurrency
```

### Why it is suitable for E1

The API provides historical public Reddit records with the fields needed by the first attention experiment, including:

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
- Search requests can time out for broad/high-volume queries.
- Search pagination is based on `created_utc`; the initial adapter is designed for bounded subreddit post streams, not arbitrary all-Reddit firehose reconstruction.
- Present `score` and `num_comments` values are mutable. Upstream notes that engagement fields are updated after initial archival. They are therefore excluded from the first E1 causal feature set.
- A historical archive capture is not identical to a true prospective `first_seen_at`. The distinction remains in the Observation contract.

If source density or pagination uncertainty becomes material, Ninja should move the affected interval to Arctic Shift bulk archives or another replayable source instead of silently treating an incomplete API extract as canonical.

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
Bronze
  raw Arctic Shift records

Silver
  Observation v1 Parquet
  closed market-candle Parquet

Gold
  dense attention windows
  causal market + attention panel
```

Event-level timestamps are retained in Silver even though E1 begins with aggregated attention. This is a deliberate requirement for later E3 propagation/Hawkes experiments.

## Causal invariant

Every information feature used at market decision time `t` must satisfy:

```text
feature_window_end <= t
and
max(observation.available_at) <= t
```

A violation is an error, not a warning.
