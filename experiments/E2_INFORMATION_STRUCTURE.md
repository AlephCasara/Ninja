# E2 — Information Structure

**Status:** design only. Requires usable E1 data.

## Question

Does the *structure* of public discussion provide incremental information beyond attention intensity?

## Feature families

### Divergence

- mean stance;
- variance;
- polarization;
- cross-platform disagreement.

### Semantic structure

- semantic homogeneity;
- topic entropy;
- narrative concentration;
- novelty;
- emergence/change points.

## Core ablation

```text
market only
market + attention
market + attention + stance
market + attention + disagreement
market + attention + narrative structure
market + all validated E2 components
```

## Requirement

Any E2 factor must outperform the corresponding simpler attention-only model on untouched chronological data.

If it does not, complexity is rejected.
