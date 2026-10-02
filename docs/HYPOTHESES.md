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

[
Y_{t+h}=f(M_t)
]

Candidate model:

[
Y_{t+h}=f(M_t,ATT_t)
]

Promotion requires positive incremental OOS performance, not merely in-sample significance.

## N2 — Common attention exists, but platform residuals matter

**Status:** literature-backed / replication target.

**Claim:** a cross-platform common attention factor exists, while platform-specific residual attention may contain additional information.

Test sequence:

1. build per-platform attention series;
2. estimate common component;
3. preserve residuals;
4. compare common-only, platform-only and combined models.

No platform merging before this ablation.

## N3 — Disagreement is distinct from average sentiment

**Status:** literature-backed / replication target.

**Claim:** dispersion/polarization/homogeneity contain information not captured by mean stance.

Ablation:

```text
market
market + mean stance
market + disagreement
market + stance + disagreement
```

## N4 — Narrative structure beats message count alone

**Status:** literature-backed motivation / replication target.

**Claim:** topic entropy, concentration and novelty provide incremental information beyond message count/attention.

Tests must compare directly against count-only baselines.

## N5 — Propagation carries incremental information

**Status:** Ninja hypothesis with methodological precedent.

**Claim:** cross-platform timing, excitation and directed information flow add predictive/state information after conditioning on attention levels.

Candidate features:

- first activation;
- activation order;
- latency;
- Hawkes excitation;
- branching/reproduction proxies;
- transfer entropy / effective transfer entropy.

## N6 — Attention and credibility are orthogonal dimensions

**Status:** literature-backed motivation / replication target.

**Claim:** high attention does not imply high truth/confirmation probability and the interaction produces different market responses.

Candidate state classes:

```text
high attention + confirmed
high attention + unconfirmed
low attention + confirmed
low attention + unconfirmed
```

## N7 — Event morphology generalizes across superficially different events

**Status:** Ninja hypothesis.

**Claim:** historical events near one another in morphology/context space have more similar future response distributions than matched controls.

A candidate event distance may combine:

[
d(i,j)=
w_c d_{categorical}
+w_s(1-cos(z_i,z_j))
+w_n d_{numeric}
+w_m d_{market-context}
]

Weights may not be hand-tuned on the final test set.

## N8 — Shock × transmission × susceptibility interaction matters

**Status:** literature-motivated Ninja core hypothesis.

**Claim:** information shocks have stronger/different effects when propagation is strong and the market is financially susceptible.

Candidate model family:

[
Y =
f(M,Q,T,S,Q	imes T,Q	imes S,T	imes S,Q	imes T	imes S)
]

A simpler model should be preferred unless interactions produce robust incremental value.

## N9 — Ninja is initially more useful for risk/state than direction

**Status:** current prior, not a fact.

**Claim:** Ninja factors improve forecasts of volatility, jumps, liquidity, MAE or regime changes more robustly than directional returns.

This must be tested rather than assumed.

## N10 — A validated Ninja factor can improve an existing Master Trader strategy without replacing it

**Status:** future integration hypothesis.

Example experimental question:

> Among historical Keltner entries, can a frozen Ninja factor reduce maximum drawdown/stop rate without destroying expected value through excessive filtering?

Comparison:

```text
original strategy
vs
same strategy + frozen Ninja policy
```

No new trading logic is accepted unless the original strategy remains the explicit baseline.

## Candidate metrics under investigation

These are not production definitions.

### Attention surprise

Robust form:

[
AZ_t =
rac{x_t-operatorname{median}(x)}
{1.4826,MAD(x)+epsilon}
]

Count-model form:

[
AS_t =
rac{N_t-mu_t}
{sqrt{mu_t+mu_t^2/phi}}
]

for a Negative-Binomial baseline.

### Author concentration

[
HHI=sum_u s_u^2
]

### Author entropy

[
H_A=
-rac{sum_u s_ulog s_u}{log U}
]

### Polarization candidate

[
P=E[|s|]-|E[s]|
]

### Narrative entropy

[
H_N=
-rac{sum_k pi_klogpi_k}{log K}
]

### Semantic homogeneity

[
H_S=
rac{2}{n(n-1)}
sum_{i<j}cos(z_i,z_j)
]

### Novelty

Simple semantic form:

[
Novelty_i =
1-max_{jin history}cos(z_i,z_j)
]

### Echo/effective attention candidate

For weights (w_i):

[
N_{eff}
=
rac{(sum_i w_i)^2}{sum_i w_i^2}
]

Candidate:

[
EchoRatio=1-rac{N_{eff}}{N}
]

### Propagation latency

[
L_{p	o q}=t_q^*-t_p^*
]

where (t_p^*) is the first threshold-crossing time on platform (p).

### Net information flow

Candidate:

[
NetFlow_{X,Y}
=
ETE_{X	o Y}-ETE_{Y	o X}
]

All formulas remain provisional until their estimator, sampling assumptions and robustness protocol are specified in an experiment.
