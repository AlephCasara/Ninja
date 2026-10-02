# E3 — Propagation

**Status:** design only. Requires at least two sufficiently reliable timestamped information streams.

## Question

Does *how information spreads* contain incremental market information beyond how much attention exists?

## Step 1 — nonparametric timing

Measure:

- first activation per source;
- activation order;
- cross-source latency;
- lagged cross-correlation as diagnostic only.

## Step 2 — point-process model

Candidate multivariate Hawkes model:

$
lambda_p(t)
=
mu_p(t)
+
sum_q
int_0^t
phi_{pq}(t-s),dN_q(s)
$

Derived candidates:

- self excitation;
- cross excitation;
- integrated excitation matrix;
- branching/reproduction proxies.

## Step 3 — directed information

Estimate transfer-entropy variants with shuffled/surrogate bias correction.

Primary comparison:

```text
market + attention
vs
market + attention + propagation
```

## Failure criteria

Propagation is rejected as a production factor if:

- results are unstable to binning/estimator choices;
- direction reverses under conditional controls;
- apparent social→market flow is explained by market→social response;
- incremental OOS value is negligible.
