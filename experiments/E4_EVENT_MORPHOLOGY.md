# E4 — Event Morphology

**Status:** Ninja hypothesis; design only.

## Question

Can structurally similar information events be mapped to similar future market-response distributions even when their wording, actors and historical context differ?

## Event representation

Candidate fields:

```text
actor_class
action
target_class
event_family
domain
direction
authority
confirmation
scope
novelty
affected_entities
semantic_embedding
market_context
```

## Hard constraint

No historical event label may encode knowledge of the future market reaction.

Bad:

```text
severity = 0.95 because BTC later crashed
```

Allowed:

```text
first_party = true
withdrawals_paused = true
scope = exchange-wide
confirmation = official
```

Financial impact must be learned from outcomes.

## Main test

Let (d_M(i,j)) be event/morphology distance and (d_R(i,j)) be response-distance.

Test whether:

[
E[d_R(i,j)mid d_M(i,j)	ext{ small}]
<
E[d_R(i,k)mid k	ext{ matched control}]
]

on held-out events.

## Response vector

Candidate horizons:

```text
5m / 15m / 1h / 4h / 24h / 3d
```

Candidate outputs:

- abnormal return;
- realized volatility;
- volume;
- liquidity;
- funding/OI;
- MAE/MFE;
- jump/tail indicators.

## Analog forecasting

Only if the main test survives OOS may Ninja construct historical analog distributions for a new event.

The output should be a distribution/risk profile, not a prose prediction.
