# Ninja

**Ninja is an alternative-information research engine for Master Trader.**

Markets do not react only to price, volume, funding or open interest. They also react to information: an event appears, people notice it, communities retransmit it, narratives converge or disagree, and that information interacts with the current financial state of the market.

Ninja exists to measure that process.

It is **not** an AI trader. It does not ask a language model whether BTC should be bought or sold. Its job is to turn noisy, unstructured public information into timestamped, testable quantitative factors. Only factors that survive historical and out-of-sample validation may cross the deterministic boundary into Master Trader.

> **Current status:** research foundation. The scientific ideas below have meaningful support in the literature, but Ninja has **not yet independently validated them on its own historical cross-platform dataset**. Reproducing or falsifying them is Phase 1.

---

## Contents

1. [Ninja in plain language](#ninja-in-plain-language)
2. [The core idea: Shock → Transmission × Susceptibility](#the-core-idea-shock--transmission--susceptibility)
3. [What Ninja is actually trying to measure](#what-ninja-is-actually-trying-to-measure)
4. [The six scouts](#the-six-scouts)
5. [From internet noise to deterministic action](#from-internet-noise-to-deterministic-action)
6. [Scientific model](#scientific-model)
7. [Mathematical core](#mathematical-core)
   - [Attention](#1-attention)
   - [Cross-platform attention](#2-cross-platform-attention)
   - [Divergence and polarization](#3-divergence-and-polarization)
   - [Narrative entropy and novelty](#4-narrative-entropy-and-novelty)
   - [Propagation and Hawkes processes](#5-propagation-and-hawkes-processes)
   - [Transfer Entropy](#6-transfer-entropy)
   - [Event Morphology](#7-event-morphology)
   - [Susceptibility](#8-susceptibility)
8. [Complexity science: what transfers and what does not](#complexity-science-what-transfers-and-what-does-not)
9. [Research program](#research-program)
10. [The first four experiments](#the-first-four-experiments)
11. [Historical data strategy](#historical-data-strategy)
12. [How Ninja is allowed to become action](#how-ninja-is-allowed-to-become-action)
13. [Master Trader integration](#master-trader-integration)
14. [Ninja OFF / SHADOW / POLICY](#ninja-off--shadow--policy)
15. [Repository boundary: separate project or part of Master Trader?](#repository-boundary-separate-project-or-part-of-master-trader)
16. [Role of LLMs, embeddings and local models](#role-of-llms-embeddings-and-local-models)
17. [Validation rules](#validation-rules)
18. [Current evidence status](#current-evidence-status)
19. [Roadmap](#roadmap)
20. [Project map and deeper technical documents](#project-map-and-deeper-technical-documents)

---

# Ninja in plain language

Imagine two price drops that look similar on a chart.

In the first case:

- price is stretched;
- volatility is normal;
- social activity is normal;
- there is no new event;
- the market may simply be oversold.

In the second case:

- price is stretched;
- discussion of an exchange problem has suddenly exploded;
- several independent communities are repeating the same new claim;
- propagation across platforms is accelerating;
- first-party confirmation is appearing;
- open interest is elevated;
- funding is extreme;
- liquidity is deteriorating.

A pure technical strategy may initially see two similar price patterns.

Ninja asks whether the **information state surrounding the market** can distinguish them.

The project therefore tries to answer questions such as:

- Is collective attention unusually high?
- Is the attention broad or concentrated in a handful of accounts?
- Are independent communities converging on the same event?
- Is the discussion becoming more polarized?
- Is a genuinely new narrative emerging?
- Which platform saw the event first?
- How quickly did it spread?
- Does social activity appear to lead the market, or merely react to it?
- Is the event structurally similar to historical events with known outcomes?
- Is the current market in a state where a small information shock can be amplified?

This is not "sentiment analysis" in the ordinary sense.

The real target is a **quantitative information state**.

---

# The core idea: Shock → Transmission × Susceptibility

Ninja starts from three ideas.

## 1. Shock

Did genuinely new information appear?

Examples:

- exploit;
- exchange outage;
- listing/delisting;
- regulation;
- legal action;
- geopolitical escalation;
- first-party corporate announcement;
- sudden narrative formation;
- unusual community attention.

## 2. Transmission

How is that information spreading?

Examples:

- one account → many accounts;
- Reddit → X → news;
- official source → news → retail communities;
- rapid cross-platform activation;
- deep repost/reply cascade;
- rising self-excitation;
- falling propagation latency.

## 3. Susceptibility

How vulnerable is the market to amplification at that moment?

Examples:

- elevated open interest;
- extreme funding;
- thin liquidity;
- high realized volatility;
- liquidation pressure;
- unstable market regime;
- existing technical overextension.

The central systems hypothesis is:

```math
\boxed{
\text{Response Distribution}_{t+h}
=
f(
\text{Market State}_t,
\text{Shock}_t,
\text{Transmission}_t,
\text{Susceptibility}_t
)
}
```

The same event can produce different outcomes in different market states.

That is the mathematical version of the "same cyclone, different environment" intuition.

---

# What Ninja is actually trying to measure

Ninja does **not** attempt to infer a single number such as:

```text
social_sentiment = -0.61
```

That would collapse too much information.

Instead, the project treats the information environment as a multidimensional state:

```math
N_{a,t}
=
[ATT,DIV,NAR,TRN,EVT,CTX]_{a,t}
```

where:

- **ATT** = attention;
- **DIV** = divergence / disagreement;
- **NAR** = narrative structure;
- **TRN** = transmission / propagation;
- **EVT** = event morphology;
- **CTX** = financial susceptibility / market context.

There is intentionally **no global NinjaScore**.

A scalar score would force arbitrary weights before evidence exists.

---

# The six scouts

The six scouts are **feature families**, not trading bots.

| Scout | Main question | Example outputs |
|---|---|---|
| **Attention** | Is collective attention abnormal? | attention surprise, acceleration, breadth, concentration |
| **Divergence** | Do people/platforms agree? | stance variance, polarization, semantic homogeneity, cross-platform divergence |
| **Narrative** | What is the information structure? | novelty, entropy, concentration, emergence, change points |
| **Propagation** | How does information spread? | activation order, latency, Hawkes excitation, directed information flow |
| **Event Morphology** | What kind of event is this structurally? | actor/action/target/family/authority/confirmation/scope |
| **Susceptibility** | Can the current market amplify the event? | volatility, liquidity, funding, OI, liquidation and regime state |

A future runtime may expose workers such as:

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

But these services do not place trades.

---

# From internet noise to deterministic action

```mermaid
flowchart LR
    A[Public information<br/>social / news / official sources] --> B[Acquisition]
    B --> C[Timestamped observations]
    C --> D[Normalization / semantic extraction]
    D --> E[Six Ninja Scouts]
    E --> F[Ninja State]
    F --> G[Historical validation]
    G -->|fails| X[Reject]
    G -->|survives OOS| H[Versioned factor]
    H --> I[Prospective shadow]
    I -->|survives| J[Deterministic policy]
    J --> K[Master Trader]
```

The key rule is:

```math
\boxed{
Information
\rightarrow
Evidence
\rightarrow
Policy
}
```

Information never becomes action directly.

---

# Scientific model

Let the conventional market state be

```math
M_{a,t}
=
[
r,
RV,
V,
L,
OI,
F,
Q,
B,
\ldots
]_{a,t}
```

where the vector may include:

- lagged returns;
- realized volatility;
- volume;
- liquidity / spread / depth;
- open interest;
- funding;
- liquidations / order flow;
- broad-market or BTC regime.

Let Ninja state be

```math
N_{a,t}
=
[
ATT,
DIV,
NAR,
TRN,
EVT,
CTX
]_{a,t}.
```

For future target $Y_{a,t+h}$, the core test is not whether a Ninja coefficient looks interesting.

It is whether Ninja adds predictive information beyond market data:

```math
\Delta_h
=
\mathcal L(
Y_{t+h},
\hat f(M_t)
)
-
\mathcal L(
Y_{t+h},
\hat g(M_t,N_t)
).
```

If:

```math
\Delta_h \le 0
```

out of sample, the additional complexity is not justified.

This is the central scientific criterion of the project.

---

# Mathematical core

The following section summarizes the main mathematical families directly in the README. Full derivations, assumptions and failure modes are preserved in [docs/MATHEMATICAL_FRAMEWORK.md](docs/MATHEMATICAL_FRAMEWORK.md).

---

## 1. Attention

### Raw counting process

For asset $a$, platform $p$, interval $(t-\Delta,t]$:

```math
N_{a,p,t}^{(\Delta)}
=
\sum_i
\mathbf 1[
a\in entity(o_i),
p_i=p,
t-\Delta<t_i\le t
].
```

Raw counts are not enough because activity is highly seasonal and overdispersed.

### Robust attention surprise

A first candidate:

```math
AZ_{a,p,t}
=
\frac{
N_{a,p,t}
-
\operatorname{median}(\mathcal W_{a,p,t})
}{
1.4826
\operatorname{MAD}(\mathcal W_{a,p,t})
+\epsilon
}.
```

This measures how abnormal the current attention level is relative to a trailing historical baseline.

### Negative-Binomial attention surprise

Social counts often have variance much larger than their mean.

Assume:

```math
N_t\sim NB(\mu_t,\phi)
```

with:

```math
Var(N_t)
=
\mu_t+\frac{\mu_t^2}{\phi}.
```

Then:

```math
AS_t
=
\frac{N_t-\mu_t}
{\sqrt{\mu_t+\mu_t^2/\phi}}.
```

A baseline intensity may include:

```math
\log\mu_t
=
\beta_0
+
f_{hour}(t)
+
f_{dow}(t)
+
f_{trend}(t)
+
\gamma_a
+
\gamma_p.
```

This lets Ninja compare attention across different assets, platforms and times of day more honestly than raw count.

### Attention acceleration

For normalized attention $A_t$:

```math
\Delta A_t=A_t-A_{t-1}
```

and

```math
\Delta^2A_t
=
(A_t-A_{t-1})
-
(A_{t-1}-A_{t-2}).
```

This measures not only whether attention is high, but whether its growth itself is accelerating.

### Author concentration

If author $u$ produces share $s_u$ of messages:

```math
HHI
=
\sum_u s_u^2.
```

A high HHI means attention is concentrated among few authors.

### Author entropy

```math
H_A
=
-
\frac{
\sum_u s_u\log s_u
}{
\log U
}.
```

High entropy means attention is distributed across many authors.

### Effective attention

Ten thousand messages copied from a small cluster of accounts do not equal ten thousand independent observations.

Given redundancy weights $w_i$:

```math
N_{\text{eff}}
=
\frac{
(\sum_i w_i)^2
}{
\sum_i w_i^2
}.
```

A candidate echo statistic is:

```math
EchoRatio
=
1-\frac{N_{\text{eff}}}{N}.
```

This is a Ninja hypothesis that must be validated.

---

## 2. Cross-platform attention

For $P$ sources:

```math
\mathbf A_{a,t}
=
[
A_{a,1,t},
A_{a,2,t},
\ldots,
A_{a,P,t}
]^\top.
```

Ninja keeps these separate first.

A simple common-attention factor can be estimated using PCA:

```math
F_t
=
w_1^\top\mathbf A_t.
```

Platform-specific residual:

```math
R_{p,t}
=
A_{p,t}
-
\hat\lambda_p F_t.
```

This gives two different objects:

- **common attention** — what many platforms share;
- **platform residual** — unusual activity on one platform after removing the common component.

A richer dynamic factor model is:

```math
A_{p,t}
=
\lambda_pF_t+\epsilon_{p,t}
```

with latent dynamics such as:

```math
F_t
=
\rho F_{t-1}+\eta_t.
```

The project will not decide in advance whether common attention or platform residuals are more useful.

That is an empirical question.

---

## 3. Divergence and polarization

Mean sentiment alone loses structure.

Let stance values be:

```math
s_i\in[-1,1].
```

Mean:

```math
\mu_s=E[s].
```

Variance:

```math
\sigma_s^2
=
E[(s-\mu_s)^2].
```

Two populations can both have mean zero:

```text
Population A:
everyone neutral

Population B:
50% extremely bullish
50% extremely bearish
```

They are not the same information state.

A candidate polarization measure is:

```math
P
=
E[|s|]-|E[s]|.
```

For platform distributions $P_p(s)$ and $P_q(s)$, Ninja may use Jensen-Shannon divergence:

```math
JSD(P_p,P_q)
=
\frac12 KL(P_p\|M)
+
\frac12 KL(P_q\|M),
```

where:

```math
M
=
\frac12(P_p+P_q).
```

### Semantic homogeneity

For normalized embeddings $z_i$:

```math
H_S
=
\frac{2}{n(n-1)}
\sum_{i<j}
z_i^\top z_j.
```

This can help distinguish:

- many independent perspectives;
- a highly repetitive echo chamber;
- coordinated narratives;
- genuine convergence on one real event.

Interpretation remains empirical.

---

## 4. Narrative entropy and novelty

Let topic proportions be:

```math
\pi_t
=
[
\pi_{1,t},\ldots,\pi_{K,t}
].
```

Normalized Shannon entropy:

```math
H_N(t)
=
-
\frac{
\sum_k\pi_{k,t}\log\pi_{k,t}
}{
\log K
}.
```

Narrative concentration:

```math
C_N(t)
=
1-H_N(t).
```

High concentration means discussion is converging on fewer narratives.

### Novelty

For embedding $z_i$ and historical reference set $\mathcal H_t$:

```math
Novelty_i
=
1-
\max_{j\in\mathcal H_t}
\cos(z_i,z_j).
```

A distribution-aware alternative is Mahalanobis distance:

```math
D_M^2(z_i)
=
(z_i-\mu_t)^\top
\Sigma_t^{-1}
(z_i-\mu_t).
```

### Narrative emergence

A deliberately falsifiable Ninja candidate is:

```math
Emergence_t
=
Novelty_t
\times
AttentionAcceleration_t
\times
Breadth_t.
```

This exact multiplicative form is **not assumed to be correct**.

It must compete against:

- additive models;
- splines;
- tree models;
- simpler baselines.

### Change-point detection

Narrative change can also be represented as a sequential change problem:

```math
\tau^*
=
\inf
\{
t:
\mathcal D(
P_{X,\text{pre}},
P_{X,\text{post}}
)
>
\theta
\}.
```

Candidate methods include:

- CUSUM;
- Bayesian Online Change Point Detection;
- energy distance;
- kernel MMD.

---

## 5. Propagation and Hawkes processes

### Activation time

For source $p$:

```math
t_p^*
=
\inf
\{
t:
A_{p,t}>\theta_p
\}.
```

Cross-platform latency:

```math
L_{p\to q}
=
t_q^*-t_p^*.
```

This is more precise than calling it "velocity" because social platforms do not have a physical spatial distance.

### Activation order

For event $e$:

```math
\Pi_e
=
rank(
t_1^*,
\ldots,
t_P^*
).
```

Examples:

```text
Reddit → X → News
Official Source → News → X
X → Reddit → YouTube
```

These patterns may themselves carry information.

### Multivariate Hawkes process

For source/type $p$:

```math
\lambda_p(t)
=
\mu_p(t)
+
\sum_q
\int_0^t
\phi_{pq}(t-s)dN_q(s).
```

With exponential kernel:

```math
\phi_{pq}(\tau)
=
\alpha_{pq}
e^{-\beta_{pq}\tau}
\mathbf 1_{\tau>0}.
```

Integrated excitation:

```math
G_{pq}
=
\int_0^\infty
\phi_{pq}(\tau)d\tau
=
\frac{\alpha_{pq}}{\beta_{pq}}.
```

Interpretation:

```math
G_{pq}
\approx
\text{expected direct offspring in process }p
\text{ produced by one event in }q.
```

For a stationary linear Hawkes process:

```math
\rho(G)<1
```

is the standard stability condition.

In the scalar case, if branching ratio is $n<1$:

```math
E[C]
=
\frac{1}{1-n}.
```

As $n\to1^{-}$, expected cascade amplification grows sharply.

In the multivariate case:

```math
(I-G)^{-1}
```

is related to cumulative excitation/amplification under the model assumptions.

Ninja does **not** assume that a large $\rho(G)$ automatically predicts financial risk.

The actual test is:

```math
Market+Attention
\quad
\text{vs}
\quad
Market+Attention+HawkesFeatures.
```

If Hawkes adds nothing out of sample, it is removed.

---

## 6. Transfer Entropy

Correlation cannot distinguish:

```math
Social\to Market
```

from:

```math
Market\to Social.
```

Transfer Entropy attempts to measure directional predictive information.

```math
TE_{X\to Y}
=
\sum
p(y_{t+1},y_t^{(k)},x_t^{(l)})
\log
\frac{
p(y_{t+1}\mid y_t^{(k)},x_t^{(l)})
}{
p(y_{t+1}\mid y_t^{(k)})
}.
```

Interpretation:

> How much extra information about the future of $Y$ is provided by the past of $X$, beyond the past of $Y$ itself?

Finite samples produce bias.

A surrogate-corrected form is:

```math
ETE_{X\to Y}
=
TE_{X\to Y}
-
E[
TE_{X^{shuffle}\to Y}
].
```

Candidate directional diagnostic:

```math
NetFlow_{X,Y}
=
ETE_{X\to Y}
-
ETE_{Y\to X}.
```

A more relevant form for Ninja is conditional Transfer Entropy:

```math
TE_{X\to Y\mid Z}
=
I(
X_{past};
Y_{future}
\mid
Y_{past},
Z_{past}
).
```

Here $Z$ can represent:

- current market state;
- common news source;
- broad-market movement;
- another platform.

This helps reduce false conclusions such as:

```text
X → BTC
```

when the true structure is:

```text
macro announcement
   ├──→ X
   └──→ BTC
```

Transfer Entropy is evidence of asymmetric predictive information under a chosen estimator. It is **not automatic proof of causality**.

---

## 7. Event Morphology

The same class of event rarely repeats with identical wording.

Ninja therefore represents an event structurally.

For event $e_i$:

```math
e_i
=
(
t_i,
c_i,
z_i,
m_i
)
```

where:

- $t_i$ = timestamp;
- $c_i$ = categorical morphology;
- $z_i$ = semantic embedding;
- $m_i$ = numerical/context state.

Candidate categorical fields:

```text
actor_class
action_class
target_class
event_family
domain
direction
authority
confirmation
scope
affected_entities
```

A mixed event distance may be:

```math
d_E(i,j)
=
w_c d_G(c_i,c_j)
+
w_s
[
1-\cos(z_i,z_j)
]
+
w_n d_M(m_i,m_j)
+
w_x d_X(x_i,x_j).
```

The weights $w$ cannot be tuned on the final test set.

### Market-response vector

For horizon $h$:

```math
R_i(h)
=
[
AR_i,
RV_i,
VZ_i,
L_i,
OI_i,
F_i,
MAE_i,
MFE_i,
J_i
].
```

### Core morphology hypothesis

If morphology is meaningful:

```math
E[
d_R(R_i,R_j)
\mid
d_E(i,j)\le c
]
<
E[
d_R(R_i,R_k)
\mid
k\in matched\ controls
].
```

In plain language:

> events that are structurally close should produce more similar market-response distributions than matched unrelated events.

If that inequality does not survive held-out events, the event-morphology hypothesis fails.

### Historical analog distribution

Only if morphology works:

```math
w_i(e)
\propto
\exp
\left(
-\frac{
d_E(e,i)^2
}{
2\sigma^2
}
\right).
```

Then:

```math
\hat P(R\mid e)
=
\frac{
\sum_i
w_i(e)\delta_{R_i}
}{
\sum_i w_i(e)
}.
```

The output is not:

> "BTC will fall 6%."

It is something closer to:

```text
Among structurally similar historical events:
P(jump > 3σ within 4h)      = ...
P(drawdown > 5% in 24h)    = ...
median volatility increase = ...
median volume surprise      = ...
```

That remains quantitative and auditable.

---

## 8. Susceptibility

Define market susceptibility as:

```math
S_{a,t}
=
[
RV_t,
Spread_t,
Depth_t,
OI_z,
Funding_z,
Liquidation_z,
Volume_z,
Beta_t,
Regime_t,
LeverageProxy_t,
\ldots
].
```

The core interaction model is:

```math
Y_{t+h}
=
f(
M_t,
Q_t,
T_t,
S_t,
Q_tT_t,
Q_tS_t,
T_tS_t,
Q_tT_tS_t
)
+
\epsilon_{t+h}
```

where:

- $Q$ = information shock;
- $T$ = transmission;
- $S$ = susceptibility.

A useful operational definition is:

```math
\chi(S)
=
\frac{
\partial E[Y\mid Q,S]
}{
\partial Q
}.
```

This asks:

> how does the marginal effect of an information shock change as the financial state changes?

That is one of the cleanest mathematical translations of the project thesis.

---

# Complexity science: what transfers and what does not

Ninja uses ideas from complexity science because both markets and information networks show:

- many interacting heterogeneous agents;
- feedback;
- nonlinear amplification;
- bursts;
- heavy tails;
- cascades;
- regime changes;
- network effects;
- multiscale structure.

But the project explicitly rejects careless physical analogy.

## What may transfer

- intermittency;
- cascade mathematics;
- branching processes;
- self/cross-excitation;
- entropy;
- information flow;
- network topology;
- change-point detection;
- multiscale analysis;
- nonlinear state dependence;
- agent interactions.

## What does not automatically transfer

- conservation of mass;
- literal pressure;
- incompressibility;
- physical velocity;
- Navier-Stokes equations.

The turbulence analogy is useful at the level of **intermittency and cascades**, not literal mechanics.

The detailed discussion is in [docs/COMPLEXITY_AND_INFORMATION_DYNAMICS.md](docs/COMPLEXITY_AND_INFORMATION_DYNAMICS.md).

---

## Criticality

Ninja does not claim that markets are literally thermodynamic critical systems.

The operational question is narrower:

> Are there states in which small information shocks produce disproportionately large response distributions?

Candidate observables include:

- Hawkes branching ratio;
- spectral radius;
- cascade-size distributions;
- network flickering;
- susceptibility interactions.

---

## Critical slowing down

Some systems near bifurcation exhibit:

- increasing autocorrelation;
- increasing variance;
- slower recovery.

Evidence in finance is mixed.

Therefore these indicators are exploratory and must beat conventional volatility/regime baselines.

---

## Self-organized criticality

SOC provides a useful conceptual model for avalanche-like behavior.

But a power-law-looking chart is not sufficient evidence.

A defensible test would compare:

- power law;
- lognormal;
- exponential;
- related heavy-tail alternatives;

with fitted cutoffs and likelihood/bootstrap diagnostics.

SOC is explanatory inspiration unless it produces validated state variables.

---

## Multifractality

A generic scaling relation is:

```math
Z(q,s)
\sim
s^{\tau(q)}.
```

Nonlinear $\tau(q)$ suggests multiscaling.

Potential future applications include:

- attention activity;
- cascade intensity;
- volatility-information coupling.

But multifractal estimators are sensitive to finite samples and nonstationarity, so this remains exploratory.

---

## Agent-based models

ABMs can test whether simple local rules can generate observed macro patterns.

They may help explore:

- copying behavior;
- narrative switching;
- attention cascades;
- volatility clustering.

But reproducing stylized facts does not identify the true mechanism.

ABMs are mechanism laboratories, not validation substitutes.

---

# Research program

The project is deliberately staged.

Ninja should not start with the most sophisticated mathematics.

The order is:

```text
simple, falsifiable effects
        ↓
cross-platform structure
        ↓
information structure
        ↓
propagation
        ↓
event morphology
        ↓
strategy overlays
        ↓
prospective live validation
```

---

## Stage 0 — Reproducibility substrate

Before any headline experiment:

- UTC-normalized timestamps;
- immutable dataset manifests;
- source/retrieval provenance;
- hashes;
- entity/asset aliases;
- causal market alignment;
- no-lookahead tests;
- frozen chronological splits.

---

## Stage 1 — Single-platform replication

For each source independently:

1. construct attention counts;
2. normalize for seasonality;
3. calculate attention surprise;
4. join to market data causally;
5. test future volatility;
6. test future volume;
7. test jumps;
8. test MAE;
9. treat directional return as secondary.

This is the first scientific gate.

---

## Stage 2 — Cross-platform factorization

Only after individual platforms work:

```text
market only
market + X
market + Reddit
market + News
market + YouTube
market + common attention
market + platform residuals
market + validated combinations
```

This directly answers:

- which platform adds information?
- which platform only duplicates others?
- which platform leads for which event type?
- does the common factor generalize better than platform-specific activity?

---

## Stage 3 — Information structure

Add:

- disagreement;
- polarization;
- semantic homogeneity;
- narrative entropy;
- novelty;
- change points.

Every feature family must beat simpler attention-only models.

---

## Stage 4 — Propagation

Estimate:

- activation times;
- activation order;
- cross-platform latency;
- Hawkes models;
- Transfer Entropy.

Primary test:

```math
Market+Attention
\quad
\text{vs}
\quad
Market+Attention+Propagation.
```

---

## Stage 5 — Event Morphology

Build an event corpus containing categories such as:

- hack/exploit;
- depeg;
- exchange outage;
- withdrawal halt;
- listing/delisting;
- regulation/enforcement;
- lawsuit;
- network outage;
- governance/upgrade;
- geopolitical escalation;
- macro/policy announcement;
- first-party announcement;
- rumor.

Then test whether morphology similarity predicts response similarity.

---

## Stage 6 — Strategy overlay

Only validated factors may be tested against actual Master Trader strategies.

Examples:

```text
Keltner baseline
vs
Keltner + Ninja policy

FundingFade baseline
vs
FundingFade + Ninja policy

OITrend baseline
vs
OITrend + Ninja policy
```

The original strategy remains the baseline.

---

# The first four experiments

The current preregistered experiment families are:

| Experiment | Purpose | Status |
|---|---|---|
| **E1 Attention Replication** | reproduce/falsify simple attention effects | design/preregistered |
| **E2 Information Structure** | test disagreement, entropy, novelty | design |
| **E3 Propagation** | test timing, Hawkes, Transfer Entropy | design |
| **E4 Event Morphology** | test structural event analogs | design |

Detailed specifications:

- [E1 — Attention Replication](experiments/E1_ATTENTION_REPLICATION.md)
- [E2 — Information Structure](experiments/E2_INFORMATION_STRUCTURE.md)
- [E3 — Propagation](experiments/E3_PROPAGATION.md)
- [E4 — Event Morphology](experiments/E4_EVENT_MORPHOLOGY.md)

The gating rule is explicit:

> If E1 cannot reproduce a simple attention effect honestly, Ninja should not jump directly into sophisticated cascade models.

---

# Historical data strategy

The first research phase uses historical information sources and market data.

The project should not attempt to download the entire internet.

Instead, Ninja should operate as a **selective historical laboratory**.

Candidate historical sources include:

- public X/Twitter-derived corpora;
- Arctic Shift Reddit archives;
- crypto/news datasets;
- public websites/archives;
- government and institutional sources;
- public exchange OHLCV;
- funding;
- open interest;
- liquidation data where reconstructable.

The storage philosophy is:

```text
temporary Bronze
      ↓
normalized Silver
      ↓
small analytical Gold
```

Raw public data may be deleted after reproducibility manifests/hashes are preserved when it can be regenerated.

The approximately 200 GB local constraint should therefore be treated as a working-set limit, not as a reason to abandon historical research.

---

## Time causality

Historical reconstruction has a major trap.

A document may have:

```text
published_at = 13:30
```

but the research system may only have observed it at:

```text
first_seen_at = 14:17
```

A simulated decision at 14:00 cannot use it.

Prospective Ninja therefore records at least:

```text
published_at
first_seen_at
collected_at
```

Historical datasets that cannot reconstruct first-seen time receive lower epistemic confidence.

Mutable present-day fields such as:

- current likes;
- current views;
- current upvotes;
- current ranking;

must not be treated as if they existed at publication time.

---

# How Ninja is allowed to become action

A feature does not become a trading rule because it looks convincing.

The promotion ladder is:

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

A promoted factor becomes a versioned object.

Example:

```text
feature:
  name: attention_surprise_1h
  version: att-1.2
  estimator: negbin-residual
  source_set: [...]
  max_staleness: ...
  quality_contract: ...
```

Only then can a deterministic policy reference it.

---

## Policy action classes

Ninja itself does not place orders.

Allowed policy outputs are intentionally narrow:

### Observe

Log only.

### Entry gate

```text
ALLOW
BLOCK
```

### Position-size multiplier

Potentially a frozen finite set such as:

```text
0.00
0.25
0.50
0.75
1.00
```

Exact values require validation.

### Risk mode

Examples:

```text
normal
cautious
halt-new-risk
```

### Strategy input

Expose a validated numeric factor to strategy code.

---

## Example policy contract

```yaml
policy_id: keltner-event-risk-v1
status: shadow
strategy: KeltnerBounceV1
experiment_id: E4-KELTNER-003
feature_contract: ninja.features/1.x

requirements:
  max_staleness_seconds: 900
  min_quality: 0.85

action:
  type: block_new_entry

failure_mode: ignore_ninja
```

Threshold values are intentionally absent until established by a frozen validation process.

---

# Master Trader integration

Master Trader is deterministic today.

Ninja must preserve that property.

The intended relationship is:

```text
NINJA
  research / extraction / models
          ↓
  versioned typed factors
════════ deterministic boundary ════════
MASTER TRADER
  policies / risk / execution
```

The first Master Trader integration should be small:

1. optional Ninja configuration;
2. read-only feature client;
3. schema/freshness validation;
4. shadow logging;
5. tests proving Ninja OFF parity.

Master Trader should **not** import:

- crawlers;
- browser automation;
- LLM clients;
- embedding models;
- historical research code.

---

# Ninja OFF / SHADOW / POLICY

## OFF

```text
NINJA_ENABLED=false
```

Master Trader behaves exactly as it does today.

This parity should be tested.

## SHADOW

```text
NINJA_ENABLED=true
NINJA_MODE=shadow
```

Ninja features are logged beside trade opportunities.

No order is changed.

A shadow record should include:

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

In shadow:

```text
actual_action = baseline_action
```

## POLICY

```text
NINJA_ENABLED=true
NINJA_MODE=policy
```

Only explicitly approved versioned policies may alter behavior.

---

# Repository boundary: separate project or part of Master Trader?

This is intentionally not treated as settled forever.

There are two technically defensible positions.

## Separate Ninja repository

Advantages:

- isolates research dependencies;
- isolates large data;
- isolates crawlers and LLM runtimes;
- allows a faster research cadence;
- prevents experimental features from contaminating trading code;
- enables reuse by other trading engines.

## Everything inside Master Trader

Advantages:

- one repository;
- atomic changes;
- simpler local development;
- no cross-repo version coordination;
- integration tests live beside strategies;
- less organizational overhead.

## Current decision

The **logical boundary is mandatory**.

The **physical repository boundary is provisional**.

Today Ninja is separate because the current workload is dominated by:

```math
research+data+probabilistic\ extraction
```

rather than:

```math
production\ trading\ logic.
```

If the live serving surface eventually becomes very small, it may be correct to move that serving layer into Master Trader.

The full architectural decision is documented in:

[ADR-001 — Ninja / Master Trader repository boundary](docs/ADR-001-REPOSITORY-BOUNDARY.md)

---

# Role of LLMs, embeddings and local models

Ninja may use probabilistic models before the deterministic boundary.

The correct pattern is:

```text
unstructured text
      ↓
rules / embeddings / classifier / LLM
      ↓
typed observation
      ↓
statistics / factor construction
      ↓
validation
      ↓
deterministic factor contract
```

Not:

```text
LLM
 ↓
BUY / SELL
```

---

## Suggested routing

| Task | Likely tool |
|---|---|
| cashtags, URLs, numbers, literal fields | Python / regex |
| entity alias resolution | rules + embeddings |
| semantic deduplication | embeddings |
| narrative clustering | embeddings / statistics |
| simple typed event extraction | compact classifier / Needle candidate |
| ambiguous extraction | fast local LLM |
| hard semantic cases | larger local LLM |
| financial weighting | statistical model |
| trade decision | deterministic Master Trader policy |

The actual routing will be benchmarked.

---

## Extraction versus financial meaning

This distinction is fundamental.

A model may extract:

```text
actor_type = exchange
action = withdrawal_pause
first_party = true
confirmation = confirmed
```

But it should not invent:

```text
financial_severity = 0.93
```

The financial consequence must be learned from historical outcomes.

> **Semantic extraction may be probabilistic. Financial weighting must be empirical.**

---

# Validation rules

Ninja is structurally vulnerable to overfitting because it can generate many features.

Suppose the project considers:

```math
40\ features
\times
10\ horizons
\times
20\ assets
\times
7\ targets
\times
5\ regimes
=
280{,}000
```

possible combinations.

Some will look excellent by chance.

Therefore headline claims require:

- chronological train/validation/test;
- untouched final test;
- purging/embargo for overlapping labels;
- dependence-aware bootstrap;
- multiple-hypothesis correction;
- permutation/surrogate tests where appropriate;
- leave-one-asset-out stress;
- leave-one-regime-out stress;
- drop-best-event robustness.

---

## Effective sample size

Messages are not independent experiments.

One million tweets about one event may still represent essentially one event episode.

Ninja therefore distinguishes:

```text
messages
unique authors
independent communities
independent platforms
time windows
event episodes
effective sample size
```

Raw post count is never treated as statistical N without justification.

---

## Market-only baseline

Every claim must beat a conventional baseline.

Example:

```math
RV_{t+4h}
=
f(
RV_t,
Volume_t,
Return_t,
Funding_t,
OI_t,
Regime_t
).
```

Then compare:

```math
MarketOnly
```

against:

```math
Market+Ninja.
```

A factor that is interesting but adds no OOS value is not promoted.

---

## Statistical metrics

Depending on target:

### Regression

- OOS $R^2$;
- MAE;
- RMSE;
- likelihood.

### Rare-event classification

- PR-AUC;
- ROC-AUC;
- Brier score;
- log loss;
- calibration.

### Strategy overlay

- profit factor;
- max drawdown;
- expected shortfall;
- MAE/MFE;
- winners removed;
- losers removed;
- opportunity cost;
- fees/slippage.

---

# Current evidence status

The project intentionally labels what is known and what is not.

| Area | Current status |
|---|---|
| Attention | literature-backed; Ninja replication pending |
| Cross-platform attention | literature-backed; replication pending |
| Disagreement/polarization | literature-backed; replication pending |
| Narrative entropy/novelty | literature-backed motivation; replication pending |
| Propagation/Hawkes | methodological precedent; Ninja application pending |
| Transfer Entropy | methodological precedent; Ninja application pending |
| Event Morphology | Ninja hypothesis; unvalidated |
| Shock × Transmission × Susceptibility | core Ninja hypothesis; unvalidated as a combined model |
| Master Trader policy value | unvalidated |

Ninja has **not yet**:

- completed its first canonical historical corpus;
- reproduced attention/volatility effects independently;
- run a native cross-platform event study;
- estimated a production-quality Hawkes model;
- validated cross-platform Transfer Entropy;
- validated Event Morphology;
- demonstrated incremental OOS value over a market-only baseline;
- produced a factor approved for trading authority.

Therefore no current Ninja factor should be described as proven alpha.

---

# Scientific foundation

The project draws on multiple existing research lines:

- investor attention across social platforms;
- attention and cryptocurrency volatility;
- disagreement and trading activity;
- semantic homogeneity / echo chambers;
- financial-news entropy and unusualness;
- directed information flow;
- Hawkes processes;
- financial event extraction;
- event-evolution knowledge graphs;
- econophysics and complex-systems market models.

The full source map, literature interpretation and caveats are documented in:

[Scientific foundation](docs/SCIENTIFIC_FOUNDATION.md)

The project uses published evidence as **motivation**, not as local proof.

---

# Roadmap

## Phase 0 — foundation

- [x] Define Ninja / Master Trader boundary
- [x] Define the six scouts
- [x] Record scientific foundation
- [x] Formalize mathematical framework
- [x] Formalize complexity-science interpretation
- [x] Create hypothesis registry
- [x] Define historical validation program
- [x] Define Master Trader deterministic boundary
- [x] Record repo-boundary ADR

## Phase 1 — historical validation substrate

- [ ] Select first historical information corpus
- [ ] Select matching market universe
- [ ] Implement manifests and hashes
- [ ] Implement causal UTC alignment
- [ ] Implement entity aliases
- [ ] Implement no-lookahead tests
- [ ] Freeze train/validation/test windows

## Phase 2 — E1 Attention Replication

- [ ] Build Attention Scout v0
- [ ] Test volatility
- [ ] Test volume
- [ ] Test jumps
- [ ] Test MAE
- [ ] Publish positive or negative result

## Phase 3 — cross-platform / information structure

- [ ] Add second information source
- [ ] Run platform ablation
- [ ] Estimate common attention
- [ ] Preserve platform residuals
- [ ] Run disagreement/narrative tests

## Phase 4 — propagation

- [ ] Activation timing
- [ ] Hawkes prototype
- [ ] Transfer Entropy prototype
- [ ] Compare propagation vs attention-only

## Phase 5 — Event Morphology

- [ ] Freeze ontology v0
- [ ] Create reviewed event gold set
- [ ] Benchmark rules / compact classifiers / local LLMs
- [ ] Test morphology-response similarity
- [ ] Test analog response distributions

## Phase 6 — prospective collection

- [ ] Design point-in-time live acquisition
- [ ] Integrate Last30Days as one collector/provider
- [ ] Add dedicated source adapters where justified
- [ ] Store first_seen_at
- [ ] Compare retrospective reconstruction against prospective capture

## Phase 7 — Master Trader shadow

- [ ] Add optional Ninja client PR
- [ ] Prove Ninja OFF parity
- [ ] Log Ninja State beside trade opportunities
- [ ] Accumulate prospective outcomes
- [ ] Do not modify trades

## Phase 8 — first deterministic policy

Only after:

```text
historical OOS
+
robustness
+
prospective shadow
+
execution economics
```

may a Ninja policy become a production candidate.

---

# Project map and deeper technical documents

The README is intended to explain the complete project at a high level.

The files below exist for deeper technical review, not because the core concept is hidden from the README.

| Document | Purpose |
|---|---|
| [Mathematical framework](docs/MATHEMATICAL_FRAMEWORK.md) | complete equations, estimators, nulls and validation logic |
| [Complexity and information dynamics](docs/COMPLEXITY_AND_INFORMATION_DYNAMICS.md) | complexity science, network theory, criticality, ABM, multifractals |
| [Scientific foundation](docs/SCIENTIFIC_FOUNDATION.md) | literature and evidence map |
| [Architecture](docs/ARCHITECTURE.md) | logical/runtime architecture and data layers |
| [Repository-boundary ADR](docs/ADR-001-REPOSITORY-BOUNDARY.md) | Ninja vs Master Trader repo tradeoff |
| [Hypothesis registry](docs/HYPOTHESES.md) | preregistered N1–N10 hypotheses |
| [Research program](docs/RESEARCH_PROGRAM.md) | staged empirical protocol |
| [Master Trader integration](docs/MASTER_TRADER_INTEGRATION.md) | feature/policy boundary and runtime integration |
| [Validation status](docs/VALIDATION_STATUS.md) | exactly what is and is not validated |
| [Experiments](experiments/README.md) | E1–E4 experimental program |
| [Roadmap](ROADMAP.md) | project phases |
| [Contributing](CONTRIBUTING.md) | scientific contribution rules |

---

# Current thesis

The strongest current working hypothesis is:

```math
\boxed{
\text{Market Response}
=
f(
\text{Information Shock},
\text{Propagation},
\text{Market Susceptibility},
\text{Market State}
)
}
```

The project is not designed to prove that equation.

It is designed to make every component measurable enough to **reject it if it is wrong**.

A beautiful model that does not add incremental out-of-sample information is discarded.

That is the central rule of Ninja.
