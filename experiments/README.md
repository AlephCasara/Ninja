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

## Promotion sequence

```text
feature prototype
→ experiment
→ replication
→ validation
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

Large source datasets do not belong in Git.

## First four experiments

- [E1 Attention Replication](E1_ATTENTION_REPLICATION.md)
- [E2 Information Structure](E2_INFORMATION_STRUCTURE.md)
- [E3 Propagation](E3_PROPAGATION.md)
- [E4 Event Morphology](E4_EVENT_MORPHOLOGY.md)

E1 is the gate for expensive research. If basic attention cannot be reproduced honestly, Ninja should not jump directly into sophisticated cascade models.
