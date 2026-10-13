# Ninja Backtesting Policy

**Status:** project-level scientific policy.

This document defines how Ninja designs, interprets and promotes historical tests. It exists to preserve the scientific intent of the project across humans, coding agents and future model sessions.

If an experiment-specific document conflicts with this policy on scientific authority, discovery, validation or interpretation, this policy takes precedence until the conflict is explicitly resolved in a reviewed revision.

The canonical scientific motivation remains in `README.md`, `docs/MATHEMATICAL_FRAMEWORK.md`, `docs/COMPLEXITY_AND_INFORMATION_DYNAMICS.md`, `docs/SCIENTIFIC_FOUNDATION.md` and `docs/HYPOTHESES.md`.

---

## 1. Terminal objective

Ninja is not a statistics project whose terminal objective is significance, estimator elegance or benchmark performance.

Ninja exists to discover public-information structure that can improve automated economic decisions and ultimately produce superior economic returns.

The research objective is therefore:

> discover information that is available before a decision, is reproducibly related to future economic states, survives historical and prospective replication, and can improve decisions after realistic costs and constraints.

Scientific rigor is required because false structure can lose capital. Scientific openness is equally required because an overly narrow method can discard real structure and therefore discard profit.

Ninja must protect against both errors:

```text
false positive
  noise is promoted as information
  -> capital loss

false negative
  real information is rejected because the representation/test was wrong
  -> opportunity loss
```

A failed test rejects only the hypothesis actually tested. It does not automatically reject a broader information family, source, mechanism or the Ninja program.

---

## 2. Scientific object: a coupled information-market system

Ninja studies the joint evolution of an information environment and an economic system.

The original working model remains:

```math
Y_{t+h}=f(M_t,Q_t,T_t,S_t)+\epsilon_{t+h}
```

where:

- `M_t` is conventional market state;
- `Q_t` is information shock/content;
- `T_t` is transmission/propagation;
- `S_t` is market susceptibility/context.

The research-domain notation remains useful:

```math
N_{a,t}=[ATT,DIV,NAR,TRN,EVT,CTX]_{a,t}
```

but these are **families of observables and representations**, not mandatory scalar indicators and not a global `NinjaScore`.

Examples include:

- **ATT** — posts, comments, views, likes, reposts, unique authors, breadth, concentration, engagement velocity and acceleration;
- **DIV** — disagreement, stance dispersion, semantic dispersion, cross-source divergence;
- **NAR** — narrative clusters, novelty, entropy, concentration, emergence, change points;
- **TRN** — cascade growth, activation order, latency, network structure, Hawkes-derived quantities, directed information flow;
- **EVT** — actor, action, target, event family, authority, confirmation, scope and semantic representation;
- **CTX** — volatility, liquidity, leverage, funding, open interest, positioning and market regime.

No one family is privileged a priori as the true representation of information.

---

## 3. Qualitative information is first-class data

Ninja must not reduce public information to counts or sentiment merely because those variables are easier to backtest.

A public-information observation may contain:

```text
content
source
actor / author
timestamp
entities
claims
events
relationships
certainty / confirmation
authority
novelty
narrative context
engagement trajectory
reply/repost graph
cross-source propagation
```

AI systems may act as scientific observation instruments that transform unstructured information into versioned structured interpretations.

The correct separation is:

```text
raw/replayable observation
        ↓
versioned semantic interpretation
        ↓
scientific representation / feature
        ↓
empirical relationship
        ↓
economic decision rule
```

Semantic extraction and financial meaning are separate problems. An extractor may classify `actor`, `action`, `target` or `confirmation`; it must not assign financial impact merely because a language model finds an event intuitively bullish or bearish.

Semantic instruments must be evaluated on real reviewed examples when their errors can materially affect a claim. Model/version provenance must be retained so the same raw corpus can be reinterpreted later.

---

## 4. Observation must remain separable from interpretation

Bronze/Silver data should preserve the world as faithfully as possible. Experiment-specific interpretation belongs in versioned derived layers.

Do not irreversibly hard-code an asset, event class or financial interpretation into a raw social observation because it came from a topical community.

For example:

```text
r/CryptoCurrency post
!= automatically a BTC observation
```

Entity resolution, event extraction and semantic classification must be explicit derived operations with their own version/provenance.

This rule exists so future models and better scientific representations can revisit the same historical evidence without reacquiring it.

---

## 5. Point-in-time historical replay is the foundation

A valid Ninja historical test reconstructs what could have been known at time `t` and never substitutes later state for earlier state.

For each replay point:

```text
information available by t
+ market state available by t
        ↓ freeze
future after t
        ↓ reveal only after freeze
response measurement
```

Mutable social fields require special care.

If a post had 2,000 likes at 10:15 and 200,000 likes at 18:00, a replay decision at 10:15 may use only the state known by 10:15. Final likes, final views, final replies or later edits are future information.

When historical snapshots do not exist, the field must be excluded from that point-in-time claim or explicitly treated as a non-causal retrospective descriptor.

Publication time, first-seen/archive time and collection time must remain separate clocks when they answer different questions.

---

## 6. Backtesting has multiple scientific forms

There is no single universal Ninja backtest.

### 6.1 State replay

Question:

> does the current information state add reproducible information about a future market state beyond conventional market information?

Conceptually:

```math
P(R_{t+h}\mid M_t,N_t)
\quad\text{vs}\quad
P(R_{t+h}\mid M_t)
```

This is appropriate for continuous quantities such as activity, narrative state, divergence, propagation state and market susceptibility.

### 6.2 Event replay

Question:

> do historically similar information events, conditional on relevant context, exhibit reproducibly different response distributions?

An event can be represented as:

```math
e_i=(t_i,c_i,z_i,g_i,s_i)
```

where `c` is categorical morphology, `z` semantic representation, `g` propagation/network state and `s` market context.

This is appropriate for announcements, regulation, hacks, listings, outages, geopolitical events, public-figure statements and other discrete information shocks.

### 6.3 Propagation replay

Question:

> does the way information diffuses carry incremental information beyond the content/activity already known?

Candidate tools include activation timing, cascade topology, point processes, Hawkes models, network measures and directed-information estimators.

### 6.4 Strategy overlay

Question:

> can a previously demonstrated information effect improve an executable decision process after costs, latency, liquidity, risk and opportunity cost?

This is downstream of information discovery. A poor trading rule does not by itself falsify an information phenomenon.

---

## 7. Discovery and confirmation are different scientific activities

Ninja must preserve a high-recall discovery phase without confusing discovery with proof.

### Discovery

Discovery may explore:

- alternative semantic representations;
- event ontologies;
- nonlinear relationships;
- network states;
- change points;
- information-theoretic quantities;
- conditional interactions;
- new mathematical representations;
- clustering and analog structure;
- new target definitions;
- methods suggested by observed anomalies.

Discovery results are candidates. They are not promoted alpha.

The search log must be retained so later evidence is interpreted in light of how much search occurred.

### Replication

A candidate becomes a replication hypothesis only after its detector/representation, population, target, horizon and comparison are specified before examining the replication outcome.

Replication should use data not used to invent the candidate whenever practical.

### Generalization

A replicated pattern is then stressed across relevant dimensions such as:

- later time periods;
- different regimes;
- other assets;
- other sources/platforms;
- event subclasses;
- alternate but defensible measurements.

### Prospective shadow

Strong historical effects should ultimately be recorded prospectively before capital is authorized.

The strongest protection against accidental hindsight is not a synthetic universe; it is a frozen rule encountering genuinely new observations.

---

## 8. Statistical and mathematical methods are central, not sovereign

Ninja may use advanced statistics, probability, information theory, network science, econometrics, machine learning, physics-inspired methods and complexity science.

The expected level is not limited to elementary financial statistics. Depending on the scientific question, legitimate instruments may include:

- robust and dependence-aware statistics;
- state-space and nonlinear models;
- point processes and Hawkes processes;
- entropy, mutual information, Transfer Entropy and directed information;
- change-point methods;
- graph/network statistics;
- heavy-tail and extreme-value methods;
- survival/hazard models;
- multiscale and multifractal methods;
- Bayesian models;
- causal/time-direction diagnostics;
- representation learning and semantic models;
- machine learning when it can be evaluated without leakage;
- agent-based or mechanism models when they answer a defined mechanism question.

No method becomes authoritative merely because it is standard in quantitative finance, common in published backtesting, familiar to an agent, or easy to implement.

For every major method, the experiment must be able to answer:

1. What scientific question does this method answer?
2. Which assumptions does it impose on this data-generating process?
3. What structure can it erase or misinterpret?
4. What simpler or alternative representation should it be compared against?
5. What result would count against the specific hypothesis?

Statistical tools assess evidence. They do not define the ontology of the phenomenon.

---

## 9. Synthetic data and Monte Carlo are not default scientific gates

Ninja does **not** require Monte Carlo, synthetic worlds or generic null-world simulation before a real-information hypothesis may be studied.

They must not be used as universal epistemic prerequisites for public-information research.

A simulated world contains the mechanisms chosen by the researcher. It therefore cannot be treated as an independent authority over whether a novel real-world phenomenon is allowed to exist.

Synthetic/simulation methods remain legitimate in narrower roles when explicitly justified, for example:

- software/unit correctness of an estimator with a known mathematical identity;
- numerical stability checks;
- testing an explicitly proposed mechanism model;
- exploring consequences of assumptions in an agent-based model;
- power/sensitivity studies for a specific registered test when the simulation model is itself appropriate.

Passing such a simulation proves only the stated property. It is not empirical market evidence and it must not substitute for historical or prospective replication.

Existing E1 Monte Carlo and synthetic-backtester prerequisites introduced on 2026-10-13 are considered legacy/non-authoritative scientific gates until removed from code and experiment documents.

---

## 10. Nulls, controls and falsification should match the phenomenon

Controls are valuable only when the null construction preserves the structure required by the question.

Depending on the hypothesis, valid controls may include:

- chronological future-versus-past direction checks;
- matched historical controls;
- entity controls;
- source controls;
- event-class controls;
- ablations;
- block/surrogate permutations when their invariants are scientifically defensible;
- negative-control outcomes;
- cross-asset placebo relationships;
- time reversal where direction is part of the claim.

Do not use an IID shuffle, random split or generic permutation merely because it produces a convenient p-value.

A control should challenge the proposed mechanism/relationship while preserving nuisance structure that would otherwise create a misleading comparison.

---

## 11. Multiple testing and search accounting

The search space is enormous. Selection bias and researcher degrees of freedom are first-order risks.

Ninja therefore records:

- what was explored;
- which transformations were tried;
- which targets/horizons were inspected;
- which candidates were promoted to replication;
- which results failed;
- whether a claim is exploratory, replicative or confirmatory.

Multiple-testing corrections such as FDR are appropriate for a defined family of formal simultaneous claims. They are not a substitute for separating discovery from replication, and they must not be applied mechanically to heterogeneous exploratory work as though every idea were the same statistical hypothesis.

---

## 12. Effective sample size is multidimensional

Message count is not independent evidence count.

Every experiment should report the units relevant to its claim, for example:

```text
N_messages
N_unique_authors
N_independent_sources
N_communities
N_platforms
N_time_windows
N_event_episodes
N_assets
N_regimes
N_effective where estimable
```

A million messages may still represent a handful of underlying events or one market regime.

Small-N results are allowed in discovery, particularly for rare qualitative events, but must be labelled with uncertainty. `INCONCLUSIVE` or `UNDERPOWERED/LOW-PRECISION` interpretations are preferable to treating absence of statistical significance as evidence of absence.

---

## 13. Rare extreme opportunities require a dedicated tail track

Ninja's economic objective includes the possibility of discovering information structures associated with rare, extremely asymmetric opportunities such as assets that multiply many times in value.

This is not well represented by optimizing average squared error on a large-cap asset.

A dedicated tail-opportunity research track must preserve a **point-in-time investable universe**, including failed, delisted and illiquid assets where data are available, to avoid survivorship and winner-selection bias.

Candidate outcome families include:

```text
maximum forward return over horizon
time to 2x / 5x / 10x / 50x / 100x
maximum adverse excursion before the multiple
probability of catastrophic loss / delisting
liquidity and executable capacity before/during the move
lead time between information state and move
persistence versus pump-and-collapse morphology
```

Candidate evaluation may require methods suited to rare events and heavy tails rather than ordinary regression alone, such as:

- extreme-value/tail modelling;
- survival/time-to-event analysis;
- rare-event classification;
- ranking/retrieval metrics;
- precision/recall at the extreme tail;
- expected utility and opportunity-cost analysis;
- event/case-control designs with point-in-time controls.

A valid tail study must start from the full eligible historical universe at each time. It must not begin by selecting famous winners and then searching backward for explanatory signals.

The goal is not to prove that every 10x/100x move is predictable. It is to test whether pre-move information/network/market states shift the probability distribution enough to support profitable asymmetric allocation.

---

## 14. Profit is the terminal metric, but raw P&L is not a scientific shortcut

The terminal objective is economic performance.

However, unconstrained maximization of historical raw P&L is degenerate: it can reward leverage, concentration, illiquidity, survivorship bias and a single lucky event.

Economic promotion should therefore report the dimensions that determine whether a profit can actually be captured, including:

```text
net P&L / terminal wealth
growth rate
max drawdown
risk of ruin / catastrophic loss
expected shortfall
fees and slippage
latency
turnover
liquidity/capacity
opportunity cost
concentration of profits by event/asset/regime
```

The exact objective function belongs to the strategy/portfolio question. Ninja should not impose one universal risk-adjusted metric on every information experiment.

Information can be economically useful by improving more than long/short direction. It may improve:

- trade/no-trade selection;
- asset ranking;
- position sizing;
- risk reduction;
- regime detection;
- entry/exit timing;
- stop/target placement;
- capital allocation;
- tail-opportunity selection.

---

## 15. Scope negative results precisely

Never write:

```text
Reddit failed.
Attention failed.
Social information failed.
Ninja failed.
```

when the actual test was:

```text
r/Bitcoin
message count + seasonal normalization
BTC future RV
4-hour horizon
specific baseline/model
specific historical period
```

Negative evidence should be recorded at the resolution of the tested claim.

A failed representation may motivate a different representation if that alternative has independent scientific rationale. It must not be invented solely to rescue a disappointing replication result on the same held-out data.

---

## 16. E1 is a baseline experiment, not a gate on the rest of Ninja

E1 remains useful as a simple single-platform activity/attention replication because it is cheap, interpretable and literature-motivated.

It answers a narrow question:

> do simple activity/attention representations add information beyond market state in this source/population?

E1 failure must not automatically deprioritize semantic information, event morphology, propagation, network structure, divergence or other qualitatively different mechanisms.

Those families have their own hypotheses and may contain information even when simple counts do not.

The existing text that treats E1 as an epistemic gate for all expensive Ninja research is superseded by this policy and should be revised.

---

## 17. Recommended empirical program

The program should remain staged without turning the stages into a single ladder where one representation can veto unrelated representations.

### Stage A — historical substrate

- replayable raw evidence;
- point-in-time timestamps;
- engagement snapshots where available;
- market history;
- source/entity provenance;
- universe membership and tradability history;
- semantic interpretation versioning.

### Stage B — simple activity baseline

- counts;
- unique authors;
- breadth/concentration;
- engagement dynamics where historically available;
- simple future-state targets.

Purpose: establish cheap baselines, not prove/disprove Ninja.

### Stage C — semantic/information structure

- event extraction;
- novelty;
- narrative clustering;
- entropy/concentration;
- disagreement/divergence;
- qualitative source/authority structure.

### Stage D — propagation/network dynamics

- cascade topology;
- activation timing;
- cross-source spread;
- Hawkes and alternative point-process representations;
- directed information flow.

### Stage E — event morphology and analogs

- structured event representation;
- context-aware historical analogs;
- response-distribution similarity.

### Stage F — coupled complexity states

Study interactions among information shock, transmission and susceptibility rather than assuming globally stationary linear relationships.

### Stage G — tail-opportunity research

Study rare asymmetric opportunities over a point-in-time full asset universe.

### Stage H — replication/generalization

Freeze candidate definitions and test on unseen historical/prospective evidence.

### Stage I — strategy/economic translation

Translate surviving information into executable decision rules and evaluate realistic economics.

### Stage J — prospective shadow and capital approval

No research model or LLM receives direct capital authority. Prospective evidence precedes live approval.

---

## 18. Backtest experiment contract

Before a replication or promotion claim, record at least:

```text
experiment_id
scientific_question
claim_scope
phase = discovery | replication | generalization | economic | prospective
information_sources
point_in_time_availability_rule
semantic_extractor + version if applicable
observation_representation
market_state_representation
population / asset universe
universe construction rule
target / response definition
horizons
controls / baselines
method and assumptions
search history relevant to candidate selection
sample-size units
leakage checks
replication dataset boundary
economic interpretation
what a negative result would and would not reject
code revision
dataset manifest
```

Additional preregistration is appropriate where the claim is confirmatory or where the search space creates substantial selection risk. Preregistration is not a ban on exploratory science; it separates exploration from later evidence.

---

## 19. Prohibited methodological shortcuts

Do not:

- introduce a universal scientific gate because it is conventional in quant finance;
- require Monte Carlo or synthetic-world success for all empirical information hypotheses;
- let one failed activity-count experiment veto semantic, morphology or propagation research;
- replace historical engagement with final/current mutable engagement;
- collapse rich qualitative information into sentiment/counts for convenience and then claim to have tested the richer hypothesis;
- hard-code entity interpretation into raw observations without an explicit derivation;
- use random IID train/test splitting where time/dependence makes it invalid;
- inspect a replication/final period and then silently change the candidate while continuing to call the period untouched;
- equate predictive information with causal proof;
- equate statistical significance with economic value;
- equate lack of significance with evidence of no effect when the study is low precision;
- select famous historical winners first and call the resulting analysis a tail-prediction backtest;
- allow an LLM's intuitive financial judgement to become the target or weight without empirical validation.

---

## 20. Agent anti-bias rule

Coding/research agents are themselves a source of methodological prior bias.

A model may preferentially suggest methods that are common in its training distribution. Familiarity is not scientific justification.

Before adding a new mandatory gate, objective, statistical method or experiment hierarchy, an agent must:

1. identify the Ninja scientific question it serves;
2. show compatibility with the project's coupled information-market model;
3. explain why existing simpler or more direct empirical validation is insufficient;
4. state the assumptions and failure modes it introduces;
5. distinguish software correctness from empirical evidence;
6. obtain an explicit project-level rationale in documentation rather than silently changing scientific authority inside code.

If a proposed method would change what counts as evidence for the entire project, it requires an explicit policy/document revision. It must not appear first as an implementation convenience.

---

## 21. Handoff rule

Before changing Ninja experiments, backtesting, scientific validation or promotion logic, read at minimum:

1. `README.md`
2. `docs/BACKTESTING_POLICY.md`
3. `docs/MATHEMATICAL_FRAMEWORK.md`
4. `docs/COMPLEXITY_AND_INFORMATION_DYNAMICS.md`
5. the relevant experiment specification

The purpose of this rule is continuity: future sessions may change tools and implementations, but they must not silently change what Ninja is trying to discover.
