# Master Trader integration

## Objective

Promoted Ninja implementations run through the existing Master Trader fleet model.

Master Trader already provides:

- Freqtrade strategy execution;
- receiver-managed execution for signal bots;
- `bots_config.json` as the fleet registry/source of truth;
- per-strategy runtime configs;
- dry-run/live modes;
- monitoring;
- portfolio circuit breaking;
- capital-account semantics.

Ninja should reuse these mechanisms rather than introduce a second runtime.

## Family switch

Proposed behavior:

```text
NINJA_ENABLED=false
  → ignore Ninja-family bots and Ninja-only feeds

NINJA_ENABLED=true
  → load individually enabled Ninja-family entries
```

This is a family-level switch. Per-bot configuration remains authoritative.

## Per-Ninja configuration

Illustrative registry entry:

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

The example is not a frozen schema. The runtime `dry_run` flag should remain in the strategy configuration, consistent with the current Master Trader setup.

## Supported runtime forms

### Standalone strategy

A normal Freqtrade strategy that owns its entry, exit and risk logic.

### Strategy overlay

Deterministic logic imported by an existing strategy.

Example:

```text
KeltnerBounceV1
+ validated event-risk gate
```

The overlay is retained only if it improves the original strategy out of sample.

### Risk or regime module

Deterministic selection among predefined risk behaviors.

## Live data dependencies

A Ninja may depend on public-information features:

```text
Last30Days / crawler / public feed
        ↓
normalization
        ↓
typed feature file or cache
        ↓
Ninja strategy
```

Causal-data requirements:

- timestamp observations when seen;
- detect stale inputs;
- never copy current observations backward into historical candles;
- define failure behavior for missing data.

## Promotion

```text
historical research
→ frozen implementation
→ backtest / walk-forward
→ Master Trader dry-run
→ prospective evidence
→ human live approval
```

Dry-run/shadow status belongs to each promoted implementation. There is no global `POLICY` mode.

## Evaluation

For a standalone strategy, compare against appropriate market-only or simple-strategy baselines.

For an overlay:

```text
OriginalStrategy
vs
OriginalStrategy + NinjaOverlay
```

Report at least:

- trade count;
- winners and losers;
- MAE/MFE;
- maximum drawdown;
- expected shortfall;
- opportunity cost;
- fees/slippage;
- regime stability.

## Compatibility requirement

The first Master Trader integration must prove:

```text
NINJA_ENABLED=false
→ existing fleet semantics unchanged
```

Existing strategies should not change because the Ninja integration is present.

## What remains outside Master Trader

Unless required by a promoted implementation, Master Trader should not contain:

- historical corpora;
- notebooks;
- experiment-search code;
- model-training code;
- large embedding indexes;
- literature artifacts.

Only promoted runtime code and the minimum live data adapters it requires should cross the boundary.

## LLM use

An upstream model may convert unstructured text into typed fields:

```text
raw post
  ↓
event_family = operational_disruption
first_party = true
confirmation = confirmed
```

The trading implementation consumes those fields through deterministic Python. It does not request BUY/SELL decisions from an LLM.

## Naming

Attention, Propagation, Event Morphology and the other domains are research categories. Runtime names should identify a concrete validated implementation, not a research domain.
