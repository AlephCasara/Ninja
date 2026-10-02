# Complexity and information dynamics

## Scope

Ninja draws on complexity science, but it must distinguish a useful mathematical transfer from metaphor.

The project does **not** claim that financial markets literally obey fluid-dynamics equations.

It does claim that several mathematical structures developed for complex systems are relevant because the observed system contains:

- many interacting heterogeneous agents;
- feedback;
- nonlinear amplification;
- heavy-tailed responses;
- endogenous/exogenous interaction;
- network-mediated propagation;
- multiscale temporal structure;
- regime changes;
- cascades.

The object of study is a coupled socio-financial system.

Let

$$
\mathcal S(t)
=
[
\mathcal G(t),
\mathcal I(t),
\mathcal M(t)
],
$$

where:

- \(\mathcal G(t)\) is interaction/network structure;
- \(\mathcal I(t)\) is information and attention state;
- \(\mathcal M(t)\) is financial-market state.

A public-information event can perturb \(\mathcal I\), alter \(\mathcal G\) through diffusion, and interact with \(\mathcal M\).

This is best understood as a partially observed state-estimation problem.

---

## 1. Why complexity methods are relevant

Financial systems exhibit well-known empirical regularities:

- heavy-tailed return distributions;
- volatility clustering;
- weak linear predictability of raw returns;
- long-memory-like behavior in activity/volatility;
- abrupt regime changes;
- cross-sectional dependence;
- intermittent bursts.

Social-information systems exhibit:

- bursty arrivals;
- highly skewed author activity;
- cascade-size distributions;
- self-excitation;
- community structure;
- strong seasonality;
- rapidly changing topology.

That overlap motivates:

- point processes;
- network science;
- information theory;
- change-point models;
- multiscale analysis.

---

## 2. What transfers from turbulence intuition

The turbulence analogy is useful at the level of **intermittency, cascades and scale**, not literal mechanics.

Transferable ideas:

### Intermittency

Long quiet intervals interrupted by intense bursts.

Operational equivalents:

- burst detection;
- waiting-time distributions;
- conditional intensity models.

### Cascades

A local perturbation generates descendants.

Operational equivalents:

- Hawkes excitation;
- repost/reply cascades;
- cross-platform activation;
- response amplification.

### Multiscale structure

A pattern can look different at 1 minute, 1 hour and 1 day.

Operational equivalents:

- multi-horizon attention;
- horizon-dependent transfer entropy;
- multiresolution change detection;
- exploratory wavelet/multifractal analysis.

### State-dependent amplification

The same perturbation can have different outcomes in different system states.

This maps directly to

$$
Shock\times Transmission\times Susceptibility.
$$

What does **not** transfer automatically:

- conservation of mass;
- literal pressure fields;
- incompressibility;
- Navier-Stokes momentum equations;
- physical velocity.

Ninja must never rename a social variable with a physical term unless it has an explicit mathematical definition.

---

## 3. Branching and self-excitation

For a scalar branching process with reproduction mean \(n<1\),

$$
E[C]=\frac{1}{1-n}.
$$

This gives a useful interpretation:

- \(n\ll1\): dying cascade;
- \(n\to1^{-}\): strong amplification;
- \(n\ge1\): stationary assumptions fail / explosive behavior may occur.

For multitype systems, let \(G\) be the offspring/excitation matrix. Stability of a linear Hawkes system requires, under standard assumptions,

$$
\rho(G)<1.
$$

Ninja's scientific question is not whether a social system is "critical" in the abstract.

It is:

> Does estimated cascade amplification improve forecasts of market state transitions or tail risk?

---

## 4. Endogenous vs exogenous activity

For a Hawkes process,

$$
\lambda(t)
=
\mu(t)
+
\sum_{t_i<t}\phi(t-t_i),
$$

where \(\mu(t)\) is background intensity and the summation is endogenous excitation.

This decomposition is attractive because Ninja needs to distinguish:

$$
News\to Social\to Market
$$

from

$$
Market\to Social
$$

and from common external causes.

However, incomplete source coverage means "exogenous" can never be inferred solely because the model assigns something to the background rate.

---

## 5. Multiplex network representation

Information lives on multiple layers.

Define

$$
\mathcal G
=
\{
G_X,
G_{Reddit},
G_{News},
G_{YouTube},
G_{Discord},
\ldots
\}.
$$

Nodes may represent:

- authors;
- communities;
- entities/assets;
- narratives;
- institutions.

Edges may represent:

- reply;
- repost;
- co-mention;
- semantic similarity;
- temporal following;
- cross-platform propagation.

This multiplex view preserves platform topology rather than collapsing all social activity into one graph.

Candidate graph statistics include:

- degree / weighted degree;
- clustering coefficient;
- modularity;
- assortativity;
- component size;
- spectral radius;
- community-crossing rate;
- cascade depth/breadth;
- source-to-source latency.

No graph statistic is retained unless it is stable under sampling and useful out of sample.

---

## 6. Information diversity

If community attention shares are \(p_c\),

$$
H_C
=
-\frac{\sum_c p_c\log p_c}{\log K}.
$$

Similarly, platform entropy is

$$
H_P
=
-\frac{\sum_p p_p\log p_p}{\log P}.
$$

These differ from author entropy and narrative entropy.

Ninja therefore treats entropy as a **family**:

- author entropy: who is speaking?
- community entropy: where is discussion happening?
- platform entropy: how distributed is attention across sources?
- narrative entropy: how distributed is content across topics?

A generic "entropy score" would be scientifically ambiguous.

---

## 7. Information topology

For a semantic graph \(G_t\), possible change statistics include:

$$
\Delta \lambda_1(A_t)
$$

for the dominant adjacency eigenvalue,

$$
\Delta Q_t
$$

for modularity change,

or distributional graph distance

$$
D(G_t,G_{t-k}).
$$

These measures are exploratory until they beat simpler baselines such as topic entropy and message-count change.

---

## 8. Mutual information and directional flow

Mutual information is

$$
I(X;Y)
=
\sum_{x,y}
p(x,y)
\log
\frac{p(x,y)}{p(x)p(y)}.
$$

It can capture nonlinear dependence but is nondirectional.

Use cases:

- feature redundancy analysis;
- screening nonlinear relationships;
- measuring information shared across platforms.

For temporal direction, Ninja uses Transfer Entropy or conditional predictive models instead.

---

## 9. Criticality

The concept of criticality is relevant only in a constrained sense.

Ninja asks:

> Are there observable states in which the response distribution to a small information shock becomes strongly amplified?

Candidate observables:

- Hawkes branching ratio / spectral radius;
- cascade-size tail behavior;
- network flickering;
- correlation structure;
- susceptibility interactions.

The project does **not** claim thermodynamic criticality.

---

## 10. Critical slowing down

Classical early-warning theory suggests some systems nearing bifurcation may exhibit:

- rising autocorrelation;
- rising variance;
- slower recovery.

Evidence in finance is mixed.

Therefore critical-slowing indicators are exploratory and must beat standard volatility/regime baselines.

Null:

$$
H_0:
CSD\ features
\text{ add no information beyond conventional state variables.}
$$

---

## 11. Self-organized criticality

SOC models produce avalanche-like dynamics and often heavy-tailed event sizes.

If Ninja tests cascade tails, the correct procedure is not "it looks straight on a log-log plot."

A defensible tail analysis should:

1. estimate a lower cutoff \(x_{min}\);
2. fit candidate heavy-tail distributions;
3. compare power-law, lognormal, exponential and related alternatives;
4. use likelihood-ratio or bootstrap-based goodness-of-fit diagnostics.

Even a good power-law fit would not identify SOC as the causal mechanism.

SOC therefore remains explanatory inspiration unless it yields validated measurable variables.

---

## 12. Multifractality

A generic multifractal scaling relation is

$$
Z(q,s)\sim s^{\tau(q)}.
$$

Nonlinear \(\tau(q)\) suggests multiscaling.

Potential Ninja applications:

- attention intensity;
- cascade activity;
- coupling between attention and volatility.

But multifractal estimators can be fragile under:

- finite samples;
- nonstationarity;
- heavy tails;
- estimator choice.

Therefore multifractality is not part of the initial production roadmap.

---

## 13. Agent-based models

An agent-based model can test mechanism plausibility.

Agents may:

- observe market state;
- observe peers;
- adopt narratives;
- repost;
- trade;
- switch communities.

If local rules reproduce heavy tails, volatility clustering or cascade shapes, that is useful.

But it does not identify the real mechanism because many micro-models can reproduce the same macro statistics.

ABMs belong in Ninja as mechanism laboratories, not as evidence substitutes or production predictors.

---

## 14. Regimes as latent states

Let \(Z_t\) be a latent regime.

A generic model is

$$
P(Z_t\mid Z_{t-1})
$$

with emissions

$$
X_t\mid Z_t\sim P_{\theta_{Z_t}}.
$$

Candidate methods:

- Hidden Markov Models;
- Markov-switching regression;
- Bayesian change-point models.

A latent-state model must beat simpler change-point/threshold models OOS before adoption.

---

## 15. Susceptibility as a response derivative

The term "susceptibility" is useful if operationalized.

Let \(Q\) be information shock and \(S\) the current market state.

Define local susceptibility:

$$
\chi(S)
=
\frac{\partial E[Y\mid Q,S]}{\partial Q}.
$$

This asks whether the marginal effect of information shock changes with leverage, liquidity, volatility, OI, funding or other state variables.

That is a clean mathematical translation of the "same cyclone, different environment" intuition.

---

## 16. Nonlinearity

Ninja assumes nonlinearity is possible, not guaranteed.

Preferred model ladder:

1. linear/logistic baseline;
2. explicit interactions;
3. splines / GAM;
4. tree boosting;
5. more complex models only if justified.

A sophisticated nonlinear model that fails to improve untouched chronological data is rejected.

---

## 17. Emergence as a measurable concept

"Emergence" should mean that a collective statistic contains information not trivially reducible to one local observation.

Conceptually,

$$
EmergentState_t
=
f(
distribution,
network,
temporal\ dynamics
).
$$

Possible examples:

- cross-community synchronization;
- cascade reproduction;
- narrative convergence;
- platform activation sequence.

A feature earns the label only if it adds OOS information beyond simpler local counts.

---

## 18. Priority order

### Tier A — immediate

- attention normalization;
- entropy;
- concentration/breadth;
- change detection;
- cross-platform timing;
- simple interactions.

### Tier B — after data quality is established

- multivariate Hawkes;
- conditional Transfer Entropy;
- dynamic factor models;
- event-morphology metric learning.

### Tier C — exploratory

- criticality diagnostics;
- multifractal analysis;
- ABM;
- network early-warning measures.

The ordering exists to stop scientific sophistication from outrunning evidence.

---

## 19. Core systems thesis

The strongest current systems-level hypothesis is

$$
ResponseDistribution_{t+h}
=
f(
MarketState_t,
Shock_t,
Transmission_t,
Susceptibility_t
).
$$

The practical criterion is

$$
\mathcal L(M+Q+T+S)
<
\mathcal L(M)
$$

on untouched chronological data.

If that inequality fails in practically meaningful terms, the additional complexity is not justified.

---

## 20. Interpretation rule

Ninja should tie language to estimators.

Allowed:

> The estimated Hawkes branching ratio increased.

Not allowed:

> The market reached criticality.

Allowed:

> Cross-platform activation latency fell from hours to minutes.

Not allowed:

> Information pressure exploded.

unless "pressure" has a formally defined variable.

Complexity science is a source of mathematical tools, not a license for metaphorical overreach.
