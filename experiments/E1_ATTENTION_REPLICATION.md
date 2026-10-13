# E1 — Simple Activity / Attention Replication

**Status:** baseline experiment design; canonical corpus materialization and empirical execution pending.

**Authority:** this experiment follows [`docs/BACKTESTING_POLICY.md`](../docs/BACKTESTING_POLICY.md).

## Purpose

E1 is the simplest real-data baseline in the Ninja research program.

It asks:

> do simple observable activity/attention representations from one information source add reproducible information about future market state beyond conventional market data?

E1 is deliberately narrow. It does **not** test the full Ninja theory, semantic content, event morphology, propagation structure or the combined `Information Shock × Transmission × Susceptibility` hypothesis.

A negative E1 result therefore rejects only the scoped activity/attention representation that was tested. It does not veto E2–E4 or other qualitatively different information hypotheses.

## Scope

Start with a timestamped historical source that can be reconstructed reproducibly and aligned point-in-time to market data.

Cross-platform data is not required for the first E1 pass.

The information source must preserve raw/replayable evidence needed by later semantic experiments even if E1 itself uses only simple activity features.

## Candidate observable families

Initial simple representations may include:

- message/post count;
- unique-author count;
- comment/reply count when point-in-time history exists;
- views/likes/reposts/shares when point-in-time snapshots exist;
- engagement velocity/acceleration when reconstructable;
- activity surprise relative to a causal historical baseline;
- activity acceleration;
- author/source concentration;
- author/source breadth or entropy.

No normalization method is privileged merely because it is statistically familiar. Raw counts remain an explicit baseline against more elaborate transforms.

Final/current mutable engagement fields may not be backfilled into earlier replay times.

## Market baseline

Candidate market-only information includes variables available at decision time, such as:

- lagged returns;
- realized volatility;
- volume;
- liquidity where available;
- broad-market/BTC regime;
- funding/open interest where available and historically reliable.

The exact baseline used in a replication claim must be recorded before the replication outcome is inspected.

## Response families

E1 may investigate future market-state variables including:

1. realized volatility;
2. volume surprise;
3. jump probability;
4. maximum adverse excursion;
5. maximum favorable excursion;
6. liquidity deterioration where reliable data exist;
7. stop-hit / barrier outcomes where operationally meaningful.

Directional return remains secondary for the initial activity-baseline study, but it is not prohibited from exploratory analysis.

## Horizons

Initial exploratory horizons may include:

```text
15m
1h
4h
24h
```

Additional horizons require scientific rationale rather than post-hoc selection solely because they produce a favorable result.

Label overlap, temporal dependence and point-in-time precision must be handled appropriately for each horizon.

## Discovery versus replication

E1 may begin with exploratory analysis on a designated discovery interval.

Discovery may compare alternative defensible activity representations and horizons. The search history is retained.

A headline replication claim requires a candidate to be frozen before evaluation on the replication evidence:

```text
source/population
observable representation
market baseline
target
horizon
comparison metric
point-in-time rules
negative-result scope
```

The replication period must not be used to invent or tune the candidate while still being described as untouched replication evidence.

## Required comparisons

At minimum, retain interpretable comparisons such as:

```text
market-only
market + raw activity
market + normalized activity
market + activity structure/breadth
```

More complex models may be explored, but they must be compared against simpler representations so apparent value is not merely model complexity.

## Statistics and controls

E1 uses statistical methods appropriate to the observed real time series and the claim under study.

Possible tools include:

- dependence-aware confidence intervals/bootstrap where justified;
- chronological replication;
- effective sample-size diagnostics;
- event/regime/community ablations;
- matched or temporal controls;
- multiple-testing correction for a defined family of formal simultaneous claims.

There is **no universal Monte Carlo, synthetic-world or synthetic-backtester prerequisite** for E1 empirical study.

Synthetic examples may be used to verify software/mathematical implementation properties when appropriate, but passing them is not empirical evidence and is not an authority over whether the real information relationship may be investigated.

## Success

E1 evidence is interesting when simple information activity adds stable, reproducible out-of-sample information beyond the recorded market baseline by a practically meaningful amount.

Statistical significance alone is not success.

Economic relevance is considered after information value is established; E1 itself does not need to produce a complete trading strategy.

## Negative / inconclusive results

A valid negative result should be reported precisely, for example:

```text
source: r/Bitcoin
representation: message count + specified normalization
target: BTC realized volatility
horizon: 4h
period: specified discovery/replication windows
result: no incremental replicated information under this design
```

Do not generalize that result to `Reddit`, `social information`, `semantic content`, `propagation`, `event morphology` or `Ninja` as a whole.

If the study is too low-precision or data quality is insufficient to distinguish a useful effect from no effect, report the result as inconclusive rather than treating non-significance as proof of absence.

## Relationship to later experiments

E1 establishes a cheap and interpretable baseline.

Later experiments ask different questions:

- **E2** — does semantic/narrative/divergence structure add information beyond market state and simple activity?
- **E3** — does propagation/network/directed-information structure add information beyond simpler representations?
- **E4** — do event morphology and context-aware analogs carry reproducible response structure?

Those hypotheses may succeed even if E1 simple activity does not.
