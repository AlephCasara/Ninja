# E1 — Attention Replication

**Status:** preregistered design; data pipeline not yet executed.

## Question

Does abnormal public attention provide incremental information about future market state after conditioning on conventional market data?

## Scope

Start with the best timestamped historical source that can be reconstructed reproducibly.

Do not require cross-platform data for the first pass.

## Candidate features

- message count;
- unique-author count;
- attention surprise;
- attention acceleration;
- author concentration;
- author entropy.

## Baseline

Market-only features:

- lagged return;
- realized volatility;
- volume;
- broad market/BTC regime;
- funding/OI where the asset/time period supports them.

## Primary targets

1. future realized volatility;
2. future volume surprise;
3. jump probability;
4. maximum adverse excursion.

Directional return is secondary.

## Horizons

Initial candidates:

```text
15m
1h
4h
24h
```

The final set must be frozen before the untouched test window is evaluated.

## Required comparisons

```text
market-only
market + raw count
market + normalized attention
market + attention structure
```

## Success

A result is not successful because a coefficient has p < 0.05.

Success requires useful, stable incremental OOS performance plus robustness across time/asset subsets.

## Failure

E1 fails if the effect:

- disappears chronologically OOS;
- exists only through mutable/lookahead-contaminated fields;
- is economically negligible;
- is dominated by one asset/event;
- cannot be reconstructed reliably enough for live use.

## Decision

E1 is the gating experiment for the rest of Ninja's more expensive modeling.
