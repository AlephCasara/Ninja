# Master Trader integration

## Goal

Ninja must add optional information without converting Master Trader into an agentic trading system.

The integration is deliberately asymmetric:

- Ninja may be complex internally;
- Master Trader receives a small deterministic contract.

## Operating modes

### OFF

No Ninja dependency.

```text
NINJA_ENABLED=false
```

Existing Master Trader behavior is unchanged.

### SHADOW

Ninja features are read and logged beside strategy opportunities, but cannot alter orders.

```text
NINJA_ENABLED=true
NINJA_MODE=shadow
```

This should be the first live integration mode.

### POLICY

Only explicitly approved policies may alter behavior.

```text
NINJA_ENABLED=true
NINJA_MODE=policy
```

A policy must name the supporting experiment and version.

## Feature contract

Illustrative shape:

```json
{
  "schema": "ninja.features/1.0",
  "generated_at": "2026-10-02T01:00:00Z",
  "valid_until": "2026-10-02T02:00:00Z",
  "assets": {
    "SOL": {
      "features": {
        "attention_surprise_1h": 3.42,
        "attention_acceleration_1h": 2.18,
        "polarization_1h": 0.72,
        "narrative_entropy_4h": 0.34,
        "propagation_signal_1h": 1.83
      },
      "quality": {
        "coverage": 0.91,
        "feature_version": "nf-1.0",
        "source_failures": []
      }
    }
  }
}
```

This is a contract example, not a frozen schema.

## Why no `NinjaScore`

A scalar score would force arbitrary weights between attention, propagation, novelty, disagreement and context before evidence exists.

Master Trader should initially receive individually versioned factors.

## Policy contract

A production-capable Ninja action is a deterministic policy.

Illustrative shape:

```yaml
policy_id: keltner-event-risk-v1
status: shadow
strategy: KeltnerBounceV1
experiment_id: E4-KELTNER-003
feature_contract: ninja.features/1.x
requirements:
  max_staleness_seconds: 900
  min_quality: 0.85
conditions:
  # Values intentionally omitted until historical validation freezes them.
action:
  type: block_new_entry
failure_mode: ignore_ninja
```

The policy must define:

- target strategy;
- required factor version;
- freshness requirement;
- quality requirement;
- deterministic conditions;
- action type;
- behavior on missing Ninja data;
- experiment supporting the rule.

## Action classes

Ninja may eventually support only a small set of action primitives:

### Observe

No effect. Logging only.

### Entry gate

```text
ALLOW
BLOCK
```

No model-generated explanation is required at decision time.

### Position-size multiplier

A frozen finite set is safer than arbitrary continuous model sizing:

```text
0.00
0.25
0.50
0.75
1.00
```

Exact choices require validation.

### Risk mode

Switch between predefined Master Trader risk profiles.

Example conceptual states:

```text
normal
cautious
halt-new-risk
```

### Strategy input

Expose a numeric factor to strategy code.

This should be used only when direct feature conditioning outperforms simpler gates.

## What Ninja may never do by default

- place exchange orders;
- modify wallet credentials;
- dynamically write strategy code in production;
- ask an LLM for BUY/SELL;
- let an LLM choose arbitrary leverage;
- alter stops/TPs from prose reasoning;
- silently fail open when a policy declares Ninja input mandatory.

## Strategy evaluation

For each integration candidate:

```text
OriginalStrategy
vs
OriginalStrategy + NinjaPolicy
```

The original strategy remains the baseline.

Required analysis includes:

- trades removed;
- winners removed;
- losers removed;
- change in MAE/MFE;
- change in max drawdown;
- opportunity cost;
- fees/slippage;
- regime dependence.

## Shadow event log

Master Trader should eventually record enough information to replay the counterfactual:

```text
decision_time
strategy
pair
baseline_signal
baseline_action
ninja_feature_version
ninja_features
ninja_policy_version
ninja_would_action
actual_action
future_outcome
```

In shadow mode:

```text
actual_action = baseline_action
```

This produces forward evidence without risk.

## Fail isolation

An unavailable Ninja feed must not stop unrelated Master Trader operation.

Default integration rule:

```text
Ninja failure → existing strategies continue unchanged
```

A future policy may explicitly choose fail-closed for **new entries** if the policy itself has demonstrated that the factor is a required risk control. Exits/position management should not become dependent on social-data availability without very strong evidence.

## Bot/scout naming

Ninja's internal workers should not be called trading bots because they do not trade.

Recommended runtime names:

```text
ninja-attention
ninja-divergence
ninja-narrative
ninja-propagation
ninja-events
ninja-susceptibility
ninja-state
ninja-serving
```

A future Master Trader strategy using a validated Ninja factor may receive a separate strategy name, but the data scouts themselves remain information services.

## PR boundary for Master Trader

The first Master Trader PR should remain small:

1. optional Ninja configuration;
2. read-only feature client;
3. schema/freshness validation;
4. shadow logging;
5. tests proving `NINJA_ENABLED=false` is behaviorally identical to current baseline.

It should **not** introduce crawlers, embeddings, LLM dependencies or research datasets into Master Trader.
