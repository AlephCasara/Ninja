# Scientific foundation

## Epistemic status

This document records the literature that motivates Ninja.

It does **not** claim that Ninja has already replicated these findings.

The initial scientific task is replication and falsification on Ninja-controlled historical datasets.

## Core thesis

The project treats markets as coupled information/financial systems.

The current working model is:

[
Y_{a,t+h}
=
g(
M_{a,t},
Q_{a,t},
T_{a,t},
S_{a,t},
interactions
)
+epsilon
]

where:

- (M): conventional market state;
- (Q): information shock;
- (T): transmission/propagation state;
- (S): financial susceptibility;
- (Y): future market response.

Initial response variables are volatility, volume, jumps, liquidity, maximum adverse excursion and tail risk. Directional return is secondary.

## Attention is not sentiment

A central reference is Cookson et al., *The Social Signal* (Journal of Financial Economics, 2024), which studies Twitter, StockTwits and Seeking Alpha.

Reported findings include a much stronger common component in investor **attention** than in sentiment across platforms, while platform-specific differences remain informative.

Reference:
https://www.sciencedirect.com/science/article/pii/S0304405X2400093X

Implications for Ninja:

1. keep platforms separate in raw/normalized features;
2. estimate a common attention factor only after platform-specific series exist;
3. retain platform residuals;
4. never reduce all social data to one sentiment score.

## Attention and crypto volatility

Research using large crypto/Twitter samples reports that social-media attention can contain information for future cryptocurrency volatility, with heterogeneous effects by asset and specification.

Reference:
https://www.sciencedirect.com/science/article/pii/S1059056021001337

Ninja replication target:

[
MarketOnly
quad vs quad
MarketOnly + Attention
]

for future realized volatility.

## Social attention as amplifier, not truth detector

A study of merger rumors found that Twitter attention amplified market reactions to rumors without making the rumor more likely to be true.

Reference:
https://www.sciencedirect.com/science/article/pii/S0165410120300367

Implication:

[
Attention 
eq Credibility
]

Ninja therefore models separately:

- attention;
- authority;
- confirmation;
- credibility-related observable properties.

## Attention × vulnerability

Recent banking-crisis research on Silicon Valley Bank provides evidence consistent with social-media attention amplifying reactions when underlying institutions were already vulnerable.

Reference:
https://www.sciencedirect.com/science/article/pii/S0304405X25002260

This motivates the interaction:

[
Impact
=
f(Shock, Transmission, Susceptibility)
]

rather than treating social information as an independent causal force.

## Disagreement

Research in social finance shows that disagreement carries information distinct from average sentiment and can be associated with trading activity.

References:

- https://afajof.org/issue/volume-75-issue-1/
- https://www.sciencedirect.com/science/article/pii/S0148296318300067

Ninja candidate observables:

[
mean(s), Var(s), Polarization(s)
]

A possible polarization statistic is:

[
Polarization
=
E[|s|]-|E[s]|
]

This is a Ninja candidate formula, not a literature-standard production metric.

## Semantic homogeneity / echo chambers

Recent work using very large social-media samples finds that semantic homogeneity can contain information beyond average sentiment.

Reference:
https://www.sciencedirect.com/science/article/abs/pii/S1544612326005350

Candidate Ninja measure:

[
Homogeneity_t
=
rac{2}{n(n-1)}
sum_{i<j}
cos(z_i,z_j)
]

where (z_i) are text embeddings.

The exact implementation requires validation.

## News novelty and entropy

International financial-news research has found that topic frequency, sentiment and unusualness/entropy can help explain or predict market outcomes including risk measures.

Reference:
https://www.sciencedirect.com/science/article/abs/pii/S0304405X18303180

This motivates separate Narrative Scout features:

- topic entropy;
- narrative concentration;
- novelty;
- emergence.

## Information flow and transfer entropy

Transfer entropy attempts to measure whether the past of one process contributes information about another process beyond the latter's own history.

[
TE_{X	o Y}
=
sum p(y_{t+1},y_t^{(k)},x_t^{(l)})
log
rac{
p(y_{t+1}mid y_t^{(k)},x_t^{(l)})
}{
p(y_{t+1}mid y_t^{(k)})
}
]

A PLOS ONE study applied this framework to social-media/stock data and found heterogeneous directional information-flow relationships.

Reference:
https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0257686

A 2025 study reported that semantic-network structure in social discussions and multivariate information-flow measures contained information for market volume beyond simple message counts.

Reference:
https://www.sciencedirect.com/science/article/pii/S0378437125000408

Ninja must use finite-sample corrections, surrogate/permutation tests and, where practical, conditional/multivariate formulations.

## Hawkes processes and propagation

A multivariate Hawkes process can model self- and cross-exciting event streams:

[
lambda_p(t)
=
mu_p(t)
+
sum_q
int_0^t
phi_{pq}(t-s)dN_q(s)
]

For integrated excitation matrix

[
G_{pq}=int_0^infty phi_{pq}(u),du
]

the spectral radius (ho(G)) is related to stability/branching behavior under standard Hawkes assumptions.

Hawkes processes have been used both for social cascades and financial/event-stream research, including crypto/social-media applications.

References:

- https://arxiv.org/abs/1708.06401
- https://arxiv.org/abs/1806.11093

Ninja hypothesis:

> estimated cascade/reproduction structure may improve market-state/risk forecasts beyond attention level alone.

This is **not yet validated by Ninja**.

## Event morphology

Ninja proposes representing events by structural properties rather than exact wording:

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
```

Financial event-extraction and event-evolution knowledge-graph research provides precedent for structured representations of financial events.

Reference:
https://www.sciencedirect.com/science/article/pii/S0957417424008650

Ninja's stronger hypothesis is:

> events close in morphology/context space should exhibit more similar response distributions than matched controls.

That specific composition is a **Ninja hypothesis**, not an established result.

## Complexity science

Useful imported ideas include:

- heavy tails and scaling;
- multiscale behavior;
- network topology;
- self/cross-excitation;
- cascades;
- entropy and information flow;
- regime transitions;
- agent interactions.

The project does **not** assume literal physical equivalence between markets and fluids. Navier–Stokes equations are not justified merely because markets and turbulence can share statistical regularities.

Multifractal and econophysics research may be explored later, but point processes, network science, information theory and change-point methods have higher initial priority.

Representative references:

- Lux & Marchesi agent model: https://www.nature.com/articles/17290
- Bouchaud on criticality: https://arxiv.org/abs/2407.10284

## Scientific hierarchy

Ninja labels claims with one of these statuses:

1. **literature-backed**
2. **replication target**
3. **Ninja hypothesis**
4. **replicated**
5. **validated OOS**
6. **production candidate**
7. **production**

No claim may skip directly from literature-backed to production.

## What would falsify the project thesis?

The thesis loses practical value if, after rigorous testing:

- Ninja features add no incremental OOS information over market-only baselines;
- apparent effects disappear under chronological validation;
- effects are dominated by lookahead/reconstruction artifacts;
- signals are too delayed for their economic horizon;
- gains are too small after trading costs/opportunity cost;
- results fail across assets/regimes;
- feature reliability is inadequate in prospective point-in-time data.

A negative result is a successful scientific outcome.
