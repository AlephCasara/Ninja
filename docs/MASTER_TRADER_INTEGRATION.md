# Master Trader integration

## Goal

A validated Ninja should feel like another member of the Master Trader fleet, not like a second trading system.

Master Trader already provides:

- Freqtrade strategy execution;
- receiver-managed execution for signal bots;
- `bots_config.json` as the fleet registry/source of truth;
- per-strategy runtime configs;
- dry-run/live modes;
- monitoring;
- portfolio circuit breaking;
- capital-account semantics.

Ninja should integrate into those mechanisms.

## Global family switch

Proposed behavior:

```text
NINJA_ENABLED=false
  → ignore all Ninja-family bots and Ninja-only feed services

NINJA_ENABLED=true
  → load Ninja-family entries that are individually enabled
```

This is a family-level kill switch.

It does not replace per-bot configuration.

## Per-Ninja configuration

A future registry entry could look conceptually like:

```json
{
  "NinjaExampleV1": {
    "family": "ninja",
    "active": true,
    "runtime_config": "NinjaExampleV1.json",
    "port": 8110,
    "timeframe": "15m",
    "type": "attention-propagation"
  }
}
```

The actual `dry_run` flag should remain in the strategy runtime config, consistent with the existing Master Trader model.

The example name and fields are illustrative until the first Ninja is validated.

## Runtime artifact types

### Standalone Ninja strategy

A normal Freqtrade strategy.

It may open and manage its own trades.

### Ninja overlay

A deterministic Python module imported by an existing strategy.

Example:

```text
KeltnerBounceV1
+ validated event-risk gate
```

This should be used only if the overlay adds OOS value over the original strategy.

### Ninja risk/regime module

A deterministic module that selects among predefined risk behaviors.

It does not invent risk settings at runtime.

## Live data dependencies

A Ninja may depend on public-information features.

For example:

```text
Last30Days / crawler / public feed
        ↓
normalization
        ↓
typed feature file/cache
        ↓
Ninja strategy
```

This should follow the same causal discipline already used by external funding/OI inputs:

- timestamp data at observation;
- detect staleness;
- never fabricate historical values;
- do not copy current observations backward into old candles;
- define failure behavior explicitly.

## Promotion into Master Trader

A candidate Ninja should move through:

```text
historical research
→ frozen implementation
→ backtest / walk-forward
→ Master Trader dry-run
→ prospective evidence
→ human live approval
```

There is no separate global `POLICY` mode.

Dry-run/shadow status belongs to each promoted Ninja.

## Strategy comparison

For a standalone Ninja:

```text
Ninja strategy
vs
appropriate market-only / simple-strategy baselines
```

For an overlay:

```text
OriginalStrategy
vs
OriginalStrategy + NinjaOverlay
```

Required analysis includes:

- trade count;
- winners/losers;
- MAE/MFE;
- max drawdown;
- expected shortfall;
- opportunity cost;
- fees/slippage;
- regime stability.

## Existing fleet must remain intact

The first Master Trader PR should prove:

```text
NINJA_ENABLED=false
→ current fleet semantics unchanged
```

The integration should not change existing strategies merely because Ninja exists.

## What stays out of Master Trader

Unless required by a promoted bot, Master Trader should not contain:

- historical corpora;
- notebooks;
- experiment search code;
- model-training code;
- large embedding indexes;
- literature artifacts.

Only promoted runtime code and the minimum live data adapters it requires should cross the boundary.

## LLM rule

A runtime Ninja must never ask an LLM what trade to make.

An upstream model may transform unstructured text into typed fields.

For example:

```text
raw post
  ↓
event_family = operational_disruption
first_party = true
confirmation = confirmed
```

The Ninja strategy may then use those fields through deterministic Python logic.

## Naming

The six research domains should not be named as runtime bots by default.

Runtime bot names should describe a validated behavior only after it exists.

That keeps the ontology honest:

```text
Attention
Propagation
Event Morphology
    = research domains

<future validated strategy name>
    = runtime Ninja
```
