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

## Scientific validation policy

All experiments follow [`docs/BACKTESTING_POLICY.md`](../docs/BACKTESTING_POLICY.md).

There is no universal synthetic-recovery or Monte-Carlo prerequisite for empirical Ninja hypotheses. Validation must match the scientific object and the claim. Synthetic data may be used for software/mathematical correctness when justified, but it is not a substitute for evidence from real historical or prospective information systems.

The common research progression is:

```text
discovery on real point-in-time evidence
→ scoped candidate hypothesis
→ replication on evidence not used to invent the candidate
→ generalization / robustness appropriate to the phenomenon
→ economic translation
→ prospective shadow
```

Specific feature families may require additional controls: Hawkes, Transfer Entropy, semantic extraction, network measures, change points and morphology each have different assumptions and therefore do not share one mandatory null/calibration recipe.

## Promotion sequence

```text
real-data discovery
→ candidate representation / relationship
→ scoped replication hypothesis
→ chronological or event-held-out replication
→ generalization stress appropriate to the claim
→ economic translation / strategy overlay
→ prospective shadow
→ deterministic runtime candidate
```

Preregistration is used when appropriate to separate a confirmatory/replication claim from prior exploration; it is not a ban on exploratory science.

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

A confirmatory headline `results.json` should satisfy the generic provenance/anti-hindsight metadata in `schemas/validation-result-v1.schema.json`. Experiment-specific controls are defined by `docs/BACKTESTING_POLICY.md` and the experiment contract, not by a universal synthetic gate.

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

E1 is the simplest activity/attention baseline experiment. Its result is informative but does not gate qualitatively different hypotheses in E2–E4; semantic structure, propagation and morphology may contain information even when simple activity counts do not.
