# Experiments

Experiments are the bridge between scientific ideas and Ninja factors.

A scout is a **feature family**. A hypothesis is a **claim**. An experiment is the controlled test that can reject or promote that claim.

Do not create one "bot" per hypothesis. Hypotheses frequently require features from multiple scouts.

## Experiment families

| Family | Primary purpose | Depends on |
|---|---|---|
| E1 Attention Replication | establish simplest historical signal | Attention |
| E2 Information Structure | test disagreement/narrative structure | Attention, Divergence, Narrative |
| E3 Propagation | test directed/cascade information | Attention, Propagation |
| E4 Event Morphology | test structural event analogs | Event Morphology, Narrative, Susceptibility |
| E5 Strategy Overlay | test incremental value in Master Trader | validated prior experiments |

## Mandatory validation sequence

Before a feature family is allowed to produce a headline empirical claim, its estimator must first survive the Phase 1.5 controls defined in `docs/SCIENTIFIC_VALIDATION_PROTOCOL.md`:

```text
implementation
→ synthetic recovery
→ null calibration
→ negative controls
→ sensitivity checks
→ chronological OOS experiment
→ generalization stress
```

The generic harness self-test proves only that the laboratory controls themselves work. Hawkes, Transfer Entropy, attention surprise, change points, morphology distances and other estimators each require their own recovery/null suite.

## Promotion sequence

```text
feature prototype
→ estimator validation
→ preregistered experiment
→ chronological OOS validation
→ generalization stress
→ frozen feature version
→ prospective shadow
→ deterministic runtime candidate
```

## Required artifacts per completed experiment

Each experiment directory should eventually contain:

```text
SPEC.md
config.yaml
results.json
REPORT.md
artifacts/
  manifests/
  figures/
```

A headline `results.json` must satisfy the metadata/gate represented by `schemas/validation-result-v1.schema.json` and `ninja_labs.validation.headline.assess_headline_eligibility`.

Large source datasets do not belong in Git.

## Result states

Completed experiments retain failures as first-class knowledge assets:

```text
SUPPORTED
WEAK
INCONCLUSIVE
REJECTED
INVALID
```

`REJECTED` means a valid experiment failed its criterion. `INVALID` means the experiment could not answer the question because of leakage, estimator, data-quality or protocol failure.

## First four experiments

- [E1 Attention Replication](E1_ATTENTION_REPLICATION.md)
- [E2 Information Structure](E2_INFORMATION_STRUCTURE.md)
- [E3 Propagation](E3_PROPAGATION.md)
- [E4 Event Morphology](E4_EVENT_MORPHOLOGY.md)

E1 is the gate for expensive research. If basic attention cannot be reproduced honestly, Ninja should not jump directly into sophisticated cascade models.
