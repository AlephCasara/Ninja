# Contributing

Ninja is both software and an empirical research project.

A contribution that produces an impressive chart but cannot be causally replayed is not considered evidence.

## Core rules

1. **No lookahead.** Inputs must be available at or before the decision timestamp.
2. **Chronological OOS.** Random train/test splits are not acceptable for headline market claims.
3. **No arbitrary thresholds.** Thresholds require preregistration or derivation on training data only.
4. **Market-only baseline required.** Ninja must prove incremental information.
5. **Negative results stay documented.** Failed hypotheses are project knowledge.
6. **Raw message count is not effective sample size.** Report episodes/windows/authors as appropriate.
7. **Do not silently merge platforms.** Platform-specific results precede combined models.
8. **No LLM trading authority.** Models may structure information; financial action remains deterministic.
9. **Reproducibility over novelty.** A simpler replicated effect beats an elaborate unreplicated model.
10. **No production from literature alone.** Published evidence is motivation, not local validation.

## Experiment record

Each headline experiment should record:

```text
experiment_id
hypothesis_id
date_registered
datasets + versions
train window
validation window
test window
features
market baseline
target
metrics
multiple-testing treatment
result
robustness checks
decision
code commit
artifact hashes
```

## Required result language

Prefer:

> "Attention Surprise improved 4h volatility OOS RMSE by X% in the frozen test window."

Avoid:

> "Attention predicts the market."

Claims must match the population, time period, target and test actually run.

## Research code

Research code may be exploratory, but a result cannot be promoted until:

- the experiment has a deterministic configuration;
- inputs have manifests/hashes;
- no-lookahead tests pass;
- rerunning the code reproduces the headline metrics;
- the final test set was not used for feature selection.

## Models and LLMs

When a language model/classifier is used:

- record model/checkpoint/version;
- freeze prompts or schema;
- preserve model output used in the experiment;
- evaluate extraction accuracy on a reviewed gold set;
- separate semantic extraction from financial weighting;
- do not ask the model to infer future market impact for historical events.

## Pull requests

A PR that changes a feature definition must explicitly state whether it invalidates prior experiment artifacts.

A PR that changes Master Trader-facing behavior must link the supporting Ninja experiment and policy version.
