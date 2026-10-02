# Hypothesis registry

This file prevents research drift.

Each hypothesis has a fixed conceptual claim, baseline, target class and promotion requirement. Individual experiment files may refine implementation details but may not silently rewrite the hypothesis after seeing results.

## N1 — Attention predicts state change

**Status:** replication target.

**Claim:** abnormal attention adds information about future market activity/risk beyond conventional market variables.

Initial targets:

- realized volatility;
- volume surprise;
- jump probability;
- maximum adverse excursion.

Baseline:

$$
Y_{t+h}=f(M_t)
$$

Candidate model:

$$
Y_{t+h}=f(M_t,ATT_t)
$$

Promotion requires positive incremental out-of-sample performance, not merely in-sample significance.

## N2 — Common attention exists, but platform residuals matter

**Status:** literature-backed / replication target.

**Claim:** a cross-platform common attention factor exists, while platform-specific residual attention may contain additional information.

Test sequence:

1. build per-platform attention series;
2. estimate a common component;
3. preserve residuals;
4. compare common-only, platform-only and combined models.

No platform merging before this ablation.

## N3 — Disagreement is distinct from average sentiment

**Status:** literature-backed / replication target.

**Claim:** dispersion, polarization and homogeneity contain information not captured by mean stance.

Ablation:

~~~text
market
market + mean stance
market + disagreement
market + stance + disagreement
~~~

A candidate polarization statistic is:

$$
P=E[|s|]-|E[s]|
$$

The formula is provisional and must compete with other dispersion measures.

## N4 — Narrative structure beats message count alone

**Status:** literature-backed motivation / replication target.

**Claim:** topic entropy, concentration and novelty provide incremental information beyond message count/attention.

Candidate normalized narrative entropy:

$$
H_N(t)
=
-
\frac{
\sum_{k=1}^{K}\pi_{k,t}\log\pi_{k,t}
}{
\log K
}
$$

Candidate concentration:

$$
C_N(t)=1-H_N(t)
$$

Tests must compare directly against count-only and attention-only baselines.

## N5 — Propagation carries incremental information

**Status:** Ninja hypothesis with methodological precedent.

**Claim:** cross-platform timing, excitation and directed information flow add predictive/state information after conditioning on attention levels.

Candidate features:

- first activation;
- activation order;
- latency;
- Hawkes excitation;
- branching/reproduction proxies;
- Transfer Entropy / Effective Transfer Entropy.

Core comparison:

$$
\mathcal{L}(M+ATT+TRN)
<
\mathcal{L}(M+ATT)
$$

on untouched chronological data.

## N6 — Attention and credibility are orthogonal dimensions

**Status:** literature-backed motivation / replication target.

**Claim:** high attention does not imply high truth/confirmation probability, and the interaction produces different market responses.

Candidate state classes:

~~~text
high attention + confirmed
high attention + unconfirmed
low attention + confirmed
low attention + unconfirmed
~~~

A candidate interaction diagnostic is:

$$
CredibilityGap_t
=
AttentionSurprise_t
\left(
1-Confirmation_t
\right)
$$

This exact scalar form is a Ninja hypothesis, not a validated production metric.

## N7 — Event morphology generalizes across superficially different events

**Status:** Ninja hypothesis.

**Claim:** historical events near one another in morphology/context space have more similar future response distributions than matched controls.

A candidate event distance may combine:

$$
d_E(i,j)
=
w_c d_{categorical}(i,j)
+
w_s
\left[
1-\cos(z_i,z_j)
\right]
+
w_n d_{numeric}(i,j)
+
w_m d_{market}(i,j)
$$

Weights may not be hand-tuned on the final test set.

Core test:

$$
E\!\left[
d_R(R_i,R_j)
\mid
d_E(i,j)\le c
\right]
<
E\!\left[
d_R(R_i,R_k)
\mid
k\in\text{matched controls}
\right]
$$

on held-out events.

## N8 — Shock × transmission × susceptibility interaction matters

**Status:** literature-motivated Ninja core hypothesis.

**Claim:** information shocks have stronger or different effects when propagation is strong and the market is financially susceptible.

Candidate model family:

$$
Y_{t+h}
=
f\!\left(
M_t,
Q_t,
T_t,
S_t,
Q_tT_t,
Q_tS_t,
T_tS_t,
Q_tT_tS_t
\right)
+
\epsilon_{t+h}
$$

A simpler model should be preferred unless interactions produce robust incremental value.

## N9 — Ninja is initially more useful for risk/state than direction

**Status:** current prior, not a fact.

**Claim:** Ninja factors improve forecasts of volatility, jumps, liquidity, MAE or regime changes more robustly than directional returns.

Primary target ordering:

1. realized volatility;
2. volume surprise;
3. jump/tail probability;
4. MAE / stop-hit probability;
5. liquidity deterioration;
6. regime transition;
7. directional return.

This ordering must be tested rather than assumed.

## N10 — A validated Ninja factor can improve an existing Master Trader strategy without replacing it

**Status:** future integration hypothesis.

Example experimental question:

> Among historical Keltner entries, can a frozen Ninja factor reduce maximum drawdown or stop rate without destroying expected value through excessive filtering?

Comparison:

~~~text
original strategy
vs
same strategy + frozen Ninja policy
~~~

The original strategy remains the explicit baseline.

## Candidate metrics under investigation

These are not production definitions.

### Attention surprise — robust form

$$
AZ_t
=
\frac{
x_t-\operatorname{median}(x)
}{
1.4826\,MAD(x)+\epsilon
}
$$

### Attention surprise — count-model form

Assume:

$$
N_t\sim NB(\mu_t,\phi)
$$

with:

$$
Var(N_t)
=
\mu_t+\frac{\mu_t^2}{\phi}
$$

Then:

$$
AS_t
=
\frac{
N_t-\mu_t
}{
\sqrt{
\mu_t+\mu_t^2/\phi
}
}
$$

### Author concentration

$$
HHI=\sum_u s_u^2
$$

### Author entropy

$$
H_A
=
-
\frac{
\sum_u s_u\log s_u
}{
\log U
}
$$

### Polarization candidate

$$
P
=
E[|s|]-|E[s]|
$$

### Narrative entropy

$$
H_N
=
-
\frac{
\sum_k\pi_k\log\pi_k
}{
\log K
}
$$

### Semantic homogeneity

$$
H_S
=
\frac{2}{n(n-1)}
\sum_{i<j}
\cos(z_i,z_j)
$$

### Novelty

$$
Novelty_i
=
1-
\max_{j\in\mathcal H_t}
\cos(z_i,z_j)
$$

### Effective attention

For weights $w_i$:

$$
N_{\mathrm{eff}}
=
\frac{
\left(
\sum_i w_i
\right)^2
}{
\sum_i w_i^2
}
$$

Candidate:

$$
EchoRatio
=
1-\frac{N_{\mathrm{eff}}}{N}
$$

### Propagation latency

$$
L_{p\to q}
=
t_q^\*-t_p^\*
$$

where $t_p^\*$ is the first threshold-crossing time on platform $p$.

### Effective Transfer Entropy

$$
ETE_{X\to Y}
=
TE_{X\to Y}
-
E\!\left[
TE_{X^{shuffle}\to Y}
\right]
$$

### Net directed information flow

$$
NetFlow_{X,Y}
=
ETE_{X\to Y}
-
ETE_{Y\to X}
$$

All formulas remain provisional until their estimator, sampling assumptions and robustness protocol are specified in an experiment.
