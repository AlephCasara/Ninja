# Research program

## Phase 1 objective

Before building a large live crawling stack, determine whether Ninja's proposed information factors contain reproducible incremental information.

The historical program is therefore the first product of the repository.

## Important current status

No Ninja-native historical cross-platform validation has yet been completed.

Existing evidence comes from published research and public dataset discovery. Phase 1 exists to reproduce, reject or refine those findings using a controlled pipeline.

## Research sequence

### Stage 0 — reproducibility substrate

Required before hypothesis testing:

- canonical UTC time representation;
- immutable dataset manifests;
- content/data hashes;
- explicit source and retrieval provenance;
- asset/entity alias registry;
- market-data alignment tests;
- no-lookahead tests;
- deterministic experiment configuration;
- frozen train/validation/test boundaries.

### Stage 1 — single-platform replication

Do **not** combine platforms first.

For each usable platform independently:

1. construct attention counts and author breadth;
2. normalize for intraday/weekly seasonality;
3. calculate candidate attention surprise;
4. join to market data causally;
5. test future volatility/volume/jump/MAE;
6. test return only as a secondary target.

Purpose: establish whether the simplest literature-backed phenomenon is reproducible.

### Stage 2 — cross-platform factorization

Only after Stage 1:

- compare platform signals;
- estimate common attention factor;
- retain platform residuals;
- run source ablations.

Required comparisons:

```text
market only
market + X
market + Reddit
market + News
market + each available source
market + common attention
market + platform residuals
market + all validated components
```

### Stage 3 — information structure

Add:

- disagreement;
- polarization;
- homogeneity;
- narrative entropy;
- novelty;
- change-point features.

Each feature family must beat a simpler count/attention model before being retained.

### Stage 4 — propagation

Estimate:

- cross-platform activation times;
- platform ordering;
- lag distributions;
- Hawkes models;
- transfer-entropy variants.

The primary question is incremental value beyond attention intensity.

### Stage 5 — event morphology

Build an event corpus without using future price outcomes to label event importance.

Candidate families:

- hack/exploit;
- depeg;
- exchange outage;
- withdrawal halt;
- listing/delisting;
- regulation/enforcement;
- lawsuit;
- protocol/network outage;
- governance/upgrade;
- geopolitical escalation;
- macro/policy announcement;
- corporate/first-party announcement;
- rumor/unconfirmed claim.

Test whether morphology/context similarity predicts similarity of future response distributions.

### Stage 6 — strategy overlay

Only factors surviving earlier stages may be tested against actual Master Trader decisions.

Examples:

- Keltner entry + Ninja factor;
- FundingFade entry + Ninja factor;
- OITrend opportunity + Ninja factor.

No strategy is rewritten. Ninja is evaluated as incremental information.

## Dual event discovery

To prevent hindsight bias, two complementary datasets are required.

### Market-first events

Events selected only from market data:

- return shocks;
- volume shocks;
- volatility jumps;
- OI/funding anomalies;
- liquidation cascades where available.

Then inspect the **past** information state.

### Information-first events

Events selected only from information data:

- attention bursts;
- narrative emergence;
- propagation bursts;
- event-family activation.

Then open the future market labels.

Both directions are necessary.

## Negative controls

Every event-study family requires controls.

Controls should match, where practical:

- asset;
- time of day/day of week;
- broad market regime;
- volatility state;
- liquidity/volume state;
- BTC/market direction;
- funding/OI regime.

The key comparison is not:

> what happened before famous crashes?

It is:

> what differed between pre-event windows and comparable windows where the event did not occur?

## Dataset policy

Given limited local storage, the program is selective.

Principles:

- query/download shards, not entire archives;
- Bronze data may be disposable when reproducible from a manifest;
- Silver/Gold derived data should be much smaller;
- keep hashes, source identifiers and query manifests;
- preserve only raw material required for audit or impossible to reacquire;
- never commit large datasets to Git.

Candidate public historical sources identified for evaluation include large Twitter/X-derived corpora, Arctic Shift Reddit archives, crypto-news datasets and public exchange market history.

Each source must receive a data-quality note before use.

## Time and lookahead policy

A reconstructed historical item has lower epistemic quality than a prospectively captured point-in-time observation.

Historical backtests must not use mutable present-day engagement as though it existed at publication time.

Safe/safer historical fields include:

- original timestamp;
- text/content;
- author/account identity at record time where available;
- reply/repost relationships where historical timestamps are preserved;
- information derived solely from text available at that time.

Potentially contaminated fields include:

- current likes/views/upvotes;
- current search ranking;
- current follower counts;
- later-edited content.

Prospective Ninja must record `first_seen_at` to solve this more cleanly.

## Targets

Priority order:

### Tier 1

- future realized volatility;
- future volume;
- jump probability;
- MAE;
- tail loss / stop-hit probability;
- liquidity deterioration.

### Tier 2

- breakout probability;
- mean-reversion failure;
- regime transition.

### Tier 3

- directional return;
- expected return.

## Statistical controls

Minimum expectations:

- chronological split, never random train/test for headline claims;
- untouched final test interval;
- embargo/purging where labels overlap;
- block bootstrap for dependent time series;
- permutation/surrogate tests where appropriate;
- multiple-hypothesis correction (e.g. FDR);
- leave-one-asset-out stress;
- leave-one-regime-out stress;
- drop-best-event robustness;
- report effect size and uncertainty, not only p-values.

## Effective sample size

Messages are not independent experiments.

One million messages about one event may still represent one event episode.

Results must distinguish:

- number of messages;
- unique authors;
- independent source/platform count;
- number of time windows;
- number of event episodes;
- effective/clustered sample size.

## Baseline discipline

Every model needs a market-only baseline.

For example:

[
RV_{t+h}=f(RV_t,Volume_t,Return_t,Funding_t,OI_t,Regime_t)
]

Ninja value is:

[
Delta Performance
=
Performance(Market+Ninja)
-
Performance(MarketOnly)
]

A factor that is statistically interesting but adds no useful OOS performance is not promoted.

## Example metrics

Regression:

- OOS (R^2);
- MAE/RMSE;
- likelihood;
- calibration where probabilistic.

Rare-event classification:

- PR-AUC;
- ROC-AUC;
- Brier score;
- log loss;
- calibration curves.

Strategy overlay:

- profit factor;
- max drawdown;
- expected shortfall;
- MAE/MFE;
- filtered winners vs filtered losers;
- opportunity cost;
- net return after fees/slippage.

## Promotion ladder

```text
idea
→ literature-backed
→ preregistered
→ replicated
→ validated OOS
→ prospective shadow
→ production candidate
→ Master Trader approval
```

There is no automatic promotion.

## First experiment set

The first implementation milestone should create four reproducible experiment families:

- **E1 Attention Replication**
- **E2 Information Structure**
- **E3 Propagation**
- **E4 Event Morphology**

E1 must work before the project invests heavily in E3/E4.

If simple attention cannot be reconstructed and evaluated honestly, sophisticated propagation models are premature.
