# Trading Domain

Trading is Ninja's first validation domain and current implementation priority.

This domain owns financial meaning that must not leak into shared Ninja science:

- market targets;
- market-only baselines;
- asset/entity aliases used by experiments;
- market susceptibility/context;
- execution-economics promotion criteria;
- Master Trader integration.

Shared methods such as attention, divergence, propagation/Hawkes, morphology and validation belong in Ninja Labs when they are genuinely domain-neutral.

## Current gate

E1 Attention Replication is the first end-to-end experiment.

The immediate comparison is information value, not strategy profitability:

```text
market-only
vs
market + Ninja information features
```

Only validated information effects may proceed to strategy backtests and Master Trader promotion.

## Phase 1 canonical substrate

The canonical historical input path is:

```text
Arctic Shift subreddit JSONL
+ Binance BTCUSDT 15m
-> Observation v1
-> dense attention panel
-> causal aligned market panel
-> E1 Attention Replication
```

Canonical config:

```text
domains/trading/configs/phase1-btc-reddit.toml
```

Expected external inputs:

```text
.ninja-inputs/arctic-shift/r_Bitcoin_posts.jsonl
.ninja-inputs/arctic-shift/r_CryptoCurrency_posts.jsonl
```

These files are intentionally excluded from Git. Their SHA-256 values and byte sizes are written into the dataset manifest so a scientific result identifies the exact historical source corpus.

The API-backed `phase1-smoke.toml` remains a bounded integration check and targeted-gap path, not the five-year canonical acquisition method.
