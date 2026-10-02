# Mathematical framework

## Purpose

This document formalizes the quantitative objects behind Ninja. Every proposed concept must reduce to an observable or estimable random variable, a timestamped estimator, an explicit null hypothesis, an out-of-sample validation path, and, only if it survives, a deterministic serving representation.

Nothing here is a production signal merely because it has a mathematical definition.

## 1. State-space view

For asset $a$, source $p$, time $t$, define the information history

$$
\mathcal{I}_{a,p}(t)=\{o_i:\ a\in entity(o_i),\ source(o_i)=p,\ t_i\le t\}.
$$

Define conventional market state

$$
M_{a,t}=[r,RV,V,L,OI,F,Q,B,\ldots]_{a,t},
$$

where the components may include lagged returns, realized volatility, volume, liquidity/spread/depth, open interest, funding, liquidations/order flow, and broad-market/BTC regime.

Ninja estimates

$$
N_{a,t}=[ATT,DIV,NAR,TRN,EVT,CTX]_{a,t}.
$$

The central empirical question is incremental:

$$
\Delta_h=
\mathcal{L}(Y_{t+h},\hat f(M_t))
-
\mathcal{L}(Y_{t+h},\hat g(M_t,N_t)).
$$

A Ninja factor is useful only if $\Delta_h>0$ on untouched chronological data under an appropriate loss, after accounting for complexity, multiple testing and economic relevance.

---

## 2. Attention Scout

### 2.1 Counting process

For source $p$, asset $a$, interval $(t-\Delta,t]$:

$$
N_{a,p,t}^{(\Delta)}
=
\sum_i
\mathbf{1}
[a\in entity(o_i),p_i=p,t-\Delta<t_i\le t].
$$

Raw counts are not directly comparable because of intraday seasonality, day-of-week effects, platform growth, asset popularity and bursty overdispersion.

### 2.2 Robust attention surprise

A low-assumption estimator is

$$
AZ_{a,p,t}
=
\frac{
N_{a,p,t}-\operatorname{median}(\mathcal W_{a,p,t})
}{
1.4826\operatorname{MAD}(\mathcal W_{a,p,t})+\epsilon
}.
$$

The reference window must be trailing and causally aligned.

### 2.3 Negative-Binomial attention residual

Because social counts are commonly overdispersed, consider

$$
N_t\sim NB(\mu_t,\phi),
$$

with

$$
Var(N_t)=\mu_t+\frac{\mu_t^2}{\phi}.
$$

Then

$$
AS_t=
\frac{N_t-\mu_t}
{\sqrt{\mu_t+\mu_t^2/\phi}}.
$$

A conditional mean may include seasonality:

$$
\log\mu_t=
\beta_0+f_{hour}(t)+f_{dow}(t)+f_{trend}(t)+\gamma_a+\gamma_p.
$$

This is a candidate estimator, not a committed production definition.

### 2.4 Attention acceleration

For normalized attention $A_t$,

$$
\Delta A_t=A_t-A_{t-1},
$$

and

$$
\Delta^2A_t=(A_t-A_{t-1})-(A_{t-1}-A_{t-2}).
$$

The second difference is a candidate acceleration measure.

### 2.5 Breadth and concentration

Let author $u$ contribute $n_u$ messages, total $N=\sum_u n_u$, and share

$$
s_u=\frac{n_u}{N}.
$$

Herfindahl concentration:

$$
HHI=\sum_u s_u^2.
$$

Normalized author entropy:

$$
H_A=
-\frac{\sum_u s_u\log s_u}{\log U}.
$$

Simple breadth:

$$
Breadth=\frac{U}{N}.
$$

High message count from eight accounts is not the same state as the same count from thousands of independent authors.

### 2.6 Effective attention

When near-duplicate posts are clustered or down-weighted, define

$$
N_{eff}
=
\frac{(\sum_i w_i)^2}{\sum_i w_i^2}.
$$

Candidate echo measure:

$$
EchoRatio=1-\frac{N_{eff}}{N}.
$$

This application is a Ninja hypothesis. The mathematics is standard effective-sample-size logic; its financial value is unvalidated.

---

## 3. Cross-platform attention

For $P$ sources,

$$
\mathbf A_{a,t}=
[A_{a,1,t},\ldots,A_{a,P,t}]^\top.
$$

Ninja does not collapse this vector before platform-level tests.

A simple common component is

$$
F_t=w_1^\top\mathbf A_t
$$

using the first principal component.

A platform residual is

$$
R_{p,t}=A_{p,t}-\hat\lambda_pF_t.
$$

A richer dynamic factor model is

$$
A_{p,t}=\lambda_pF_t+\epsilon_{p,t},
$$

with, for example,

$$
F_t=\rho F_{t-1}+\eta_t.
$$

The common factor asks what attention is shared. Residuals ask whether one platform is unusually active after removing the common component.

---

## 4. Divergence Scout

Let stance/classifier output be $s_i\in[-1,1]$.

Mean:

$$
\mu_s=E[s].
$$

Variance:

$$
\sigma_s^2=E[(s-\mu_s)^2].
$$

A candidate polarization statistic is

$$
P=E[|s|]-|E[s]|.
$$

This distinguishes a neutral crowd from two extreme opposing camps even when both have mean zero.

For source distributions $P_p(s)$ and $P_q(s)$, Jensen-Shannon divergence is

$$
JSD(P_p,P_q)
=
\frac12 KL(P_p\|M)+\frac12 KL(P_q\|M),
$$

where

$$
M=\frac12(P_p+P_q).
$$

This is a candidate cross-platform disagreement measure.

### Semantic homogeneity

For normalized text embeddings $z_i$,

$$
H_S=
\frac{2}{n(n-1)}
\sum_{i=1}^{n-1}
\sum_{j=i+1}^{n}
\cos\!\left(z_i,z_j\right)
$$

High homogeneity can mean echo chamber, coordination or genuine convergence on a real event. Directional interpretation must be empirical.

---

## 5. Narrative Scout

Let topic proportions be

$$
\pi_t=[\pi_{1,t},\ldots,\pi_{K,t}].
$$

Normalized narrative entropy:

$$
H_N(t)
=
-
\frac{\sum_k\pi_{k,t}\log\pi_{k,t}}{\log K}.
$$

Candidate concentration:

$$
C_N(t)=1-H_N(t).
$$

### Semantic novelty

For event/post embedding $z_i$ and a historical reference set $\mathcal H_t$:

$$
Novelty_i
=
1-\max_{j\in\mathcal H_t}\cos(z_i,z_j).
$$

A distribution-aware alternative is Mahalanobis distance:

$$
D_M^2(z_i)
=
(z_i-\mu_t)^\top\Sigma_t^{-1}(z_i-\mu_t).
$$

Regularization is required in high dimensions.

### Narrative emergence

A deliberately testable candidate is

$$
Emergence_t=
Novelty_t
\times
AttentionAcceleration_t
\times
Breadth_t.
$$

The multiplicative form is not privileged. Additive, spline and nonlinear alternatives must compete against it.

### Change-point formulation

For feature process $X_t$, estimate a change time

$$
\tau^\*
=
\inf\{t:\mathcal D(P_{X,\mathrm{pre}},P_{X,\mathrm{post}})>\theta\}.
$$

Candidate methods include CUSUM, Bayesian Online Change Point Detection, energy distance and kernel MMD.

---

## 6. Propagation Scout

### 6.1 Activation time

Define source activation

$$
t_p^\*=\inf\{t:A_{p,t}>\theta_p\}.
$$

Cross-source latency:

$$
L_{p\to q}=t_q^\*-t_p^\*.
$$

This is preferable to casually calling the quantity velocity, because no physical spatial distance is assumed.

### 6.2 Activation order

For event $e$,

$$
\Pi_e=rank(t_1^\*,\ldots,t_P^\*).
$$

The empirical question is whether signatures such as Reddit → X → News or Official → News → X condition future market-response distributions.

---

## 7. Multivariate Hawkes processes

For process/source $p$:

$$
\lambda_p(t)
=
\mu_p(t)
+
\sum_q\int_0^t\phi_{pq}(t-s)dN_q(s).
$$

For exponential kernel

$$
\phi_{pq}(\tau)
=
\alpha_{pq}e^{-\beta_{pq}\tau}\mathbf 1_{\tau>0},
$$

the integrated excitation is

$$
G_{pq}
=
\int_0^\infty\phi_{pq}(\tau)d\tau
=
\frac{\alpha_{pq}}{\beta_{pq}}.
$$

$G_{pq}$ can be interpreted as expected direct offspring in process $p$ generated by one event in $q$, under model assumptions.

For a stationary linear multivariate Hawkes process, a standard stability condition is

$$
\rho(G)<1,
$$

where $\rho(G)$ is the spectral radius.

Scalar branching intuition:

$$
E[C]=\frac{1}{1-n},\quad n<1.
$$

Multivariate cumulative amplification is related to

$$
(I-G)^{-1}.
$$

Ninja does not assume $\rho(G)$ is automatically a risk signal. The test is

$$
Market+Attention
\quad\text{vs}\quad
Market+Attention+HawkesFeatures.
$$

Potential failure modes include nonstationarity, hidden common causes, incomplete platform sampling and kernel misspecification.

---

## 8. Information theory and Transfer Entropy

Correlation cannot distinguish Social → Market from Market → Social.

Transfer entropy is

$$
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
$$

Interpretation: information about $Y_{t+1}$ contributed by the past of $X$ beyond the past of $Y$.

Finite samples create bias. A surrogate-corrected form is

$$
ETE_{X\to Y}
=
TE_{X\to Y}
-
E[TE_{X^{shuffle}\to Y}].
$$

Block shuffles are preferable when autocorrelation matters.

Candidate net flow:

$$
NetFlow_{X,Y}
=
ETE_{X\to Y}-ETE_{Y\to X}.
$$

This is evidence of asymmetric predictive information under the estimator, not proof of causality.

Conditional TE is closer to the Ninja question:

$$
TE_{X\to Y\mid Z}
=
I(X_{past};Y_{future}\mid Y_{past},Z_{past}),
$$

where $Z$ may represent common news or market state.

---

## 9. Event Morphology

Represent event $e_i$ as

$$
e_i=(t_i,c_i,z_i,m_i),
$$

where $c_i$ contains categorical morphology, $z_i$ semantic representation and $m_i$ numerical/context metadata.

Candidate categorical fields:

- actor class;
- action class;
- target class;
- event family;
- domain;
- authority;
- confirmation;
- scope.

A mixed event distance may be

$$
d_E(i,j)
=
w_c d_G(c_i,c_j)
+
w_s[1-\cos(z_i,z_j)]
+
w_n d_M(m_i,m_j)
+
w_x d_X(x_i,x_j).
$$

Weights cannot be tuned on the final test set.

### Response vector

For horizon $h$,

$$
R_i(h)
=
[
AR_i(h),
RV_i(h),
VZ_i(h),
L_i(h),
OI_i(h),
F_i(h),
MAE_i(h),
MFE_i(h),
J_i(h)
].
$$

### Core morphology test

If morphology carries transferable structure:

$$
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
$$

This must be evaluated on held-out events.

### Analog response distribution

Only after the previous test survives:

$$
w_i(e)
\propto
\exp\left(-\frac{d_E(e,i)^2}{2\sigma^2}\right),
$$

and

$$
\hat P(R\mid e)
=
\frac{\sum_i w_i(e)\delta_{R_i}}{\sum_i w_i(e)}.
$$

The output is a historical conditional distribution, not prose prediction.

---

## 10. Susceptibility Scout

Define market susceptibility

$$
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
$$

The core systems model is

$$
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
+\epsilon_{t+h},
$$

where $Q$ is information shock, $T$ transmission and $S$ susceptibility.

The interaction terms are hypotheses, not requirements.

### Local susceptibility interpretation

A useful operational definition is

$$
\chi(S)
=
\frac{\partial E[Y\mid Q,S]}{\partial Q}.
$$

The question becomes: does the marginal response to information shock become larger in particular financial states?

---

## 11. Market-response targets

### Realized volatility

$$
RV_{t,h}
=
\sqrt{\sum_{i=1}^{h}r_{t+i}^2}.
$$

### Jump indicator

A simple research label is

$$
J_{t,h}
=
\mathbf 1[
|r_{t,t+h}|>k\hat\sigma_t
].
$$

More rigorous jump tests may later replace this.

### Maximum adverse excursion

For a long entry:

$$
MAE_{t,h}
=
\min_{u\in[t,t+h]}
\frac{P_u-P_t}{P_t}.
$$

### Maximum favorable excursion

$$
MFE_{t,h}
=
\max_{u\in[t,t+h]}
\frac{P_u-P_t}{P_t}.
$$

These are especially relevant for evaluating Ninja as a risk overlay rather than a trade generator.

---

## 12. Hazard formulation

For time-to-event $T^\*$, a hazard model may be appropriate:

$$
\lambda(t\mid X_t)
=
\lambda_0(t)\exp(\beta^\top X_t),
$$

with $X_t=[M_t,N_t]$.

Targets may include jump arrival, stop-hit arrival, liquidity stress onset or volatility-regime transition.

---

## 13. Statistical validation

### Chronological partition

Headline tests require

$$
Train<Validation<Test.
$$

The final test window remains untouched until feature definitions, model family and hyperparameters are frozen.

### Purging and embargo

When labels overlap, train and validation rows can share future information mechanically. Overlapping labels must be purged and an embargo applied where appropriate.

### Multiple testing

Candidate controls include:

- Benjamini-Hochberg FDR;
- family-wise controls for narrow confirmatory families;
- White Reality Check / SPA-style controls for model/strategy search;
- nested validation.

### Dependence-aware resampling

IID bootstrap is often invalid.

Candidate methods:

- moving-block bootstrap;
- stationary bootstrap;
- cluster bootstrap by event/asset.

### Surrogate tests

Useful nulls include:

- circular time shift;
- block shuffle;
- source-label permutation;
- event-time permutation preserving intraday seasonality.

### Drop-best-event robustness

Repeat headline results after removing the single most favorable event. A result that disappears is classified as tail-dependent.

---

## 14. Model comparison

Regression:

$$
\Delta R^2_{OOS}
=
R^2_{OOS}(M+N)-R^2_{OOS}(M).
$$

Probabilistic prediction:

$$
\Delta Brier=Brier(M)-Brier(M+N),
$$

and

$$
\Delta LogLoss=LogLoss(M)-LogLoss(M+N).
$$

Rare-event classification should report PR-AUC as well as ROC-AUC.

Statistical significance alone is insufficient. Effect size, calibration and regime stability matter.

---

## 15. Economic validation

A factor that predicts volatility may still be useless to Master Trader.

The actual comparison is

$$
Strategy_{baseline}
\quad\text{vs}\quad
Strategy_{baseline+NinjaPolicy}.
$$

Required outputs include:

- trades filtered;
- winners filtered;
- losers filtered;
- change in profit factor;
- change in maximum drawdown;
- change in expected shortfall;
- change in MAE/MFE;
- opportunity cost;
- fees/slippage;
- regime dependence.

---

## 16. Deterministic serving boundary

Conceptually,

$$
NinjaState_{a,t}^{(v)}
=
\mathcal F_v(
Observations_{\le t},
Market_{\le t}
).
$$

The same version $v$, given the same serialized point-in-time inputs, must reproduce the same output within a declared numerical tolerance.

A language model can participate only if its checkpoint/schema/output handling is frozen or persisted. Trading action still consumes only typed/versioned factors.

---

## 17. Null hypotheses

Attention:

$$
H_{0,ATT}:
NinjaAttention
\text{ adds no OOS information beyond }M.
$$

Propagation:

$$
H_{0,TRN}:
Propagation
\text{ adds no OOS information beyond attention level}.
$$

Morphology:

$$
H_{0,EVT}:
Morphology-near events
\text{ do not have more similar response distributions}.
$$

Systems interaction:

$$
H_{0,INT}:
Shock\times Transmission\times Susceptibility
\text{ adds no useful OOS information}.
$$

Failure to reject is a valid project result.

---

## 18. Priority hierarchy

Mathematical sophistication is not evidence.

Research priority:

1. robust attention normalization;
2. platform-separated ablation;
3. disagreement/narrative structure;
4. propagation timing;
5. Hawkes / information flow;
6. event morphology;
7. criticality/multifractal exploratory work.

The source map and literature motivation live in [SCIENTIFIC_FOUNDATION.md](SCIENTIFIC_FOUNDATION.md).
