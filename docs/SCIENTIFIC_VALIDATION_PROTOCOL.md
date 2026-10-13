# Scientific validation protocol

This document defines cross-experiment safeguards under [`BACKTESTING_POLICY.md`](BACKTESTING_POLICY.md). It does **not** prescribe one universal estimator, null model, simulation, resampling scheme or backtest form.

## Scientific authority

The hypothesis, source structure and replay type determine the validation design. Statistical methods are instruments; familiarity is not scientific authority.

## Minimum cross-experiment safeguards

A confirmatory/replication claim should document, where applicable:

- point-in-time provenance and causal clocks;
- the historical population/event universe actually eligible at each time;
- representation and target frozen before replication outcome inspection;
- chronological or event-held-out evidence not used to invent the candidate;
- raw and effective sample units appropriate to the phenomenon;
- search/multiple-testing history when many candidates were explored;
- effect size, uncertainty and practical relevance;
- controls/falsifications chosen for the specific mechanism;
- sensitivity across relevant regimes, events, assets and sources;
- an untouched or prospective stage when the claim warrants promotion.

Not every safeguard applies identically to State Replay, Event Replay, Propagation Replay, Tail Opportunity or Strategy Overlay. The experiment contract must state what applies and why.

## Software correctness is not empirical evidence

Unit tests and controlled fixtures may verify timestamp alignment, estimator algebra, serialization, deterministic replay, resampling code or point-process implementations. Passing those tests demonstrates software/mathematical behavior only. It does not establish that the corresponding phenomenon exists in markets or information networks.

## Controls and falsification

Controls should be derived from the real phenomenon whenever possible: temporal reversal, matched historical controls, unrelated-entity controls, source/propagation ablations, real-data permutations preserving relevant dependence, and leave-event/regime/source-out stresses.

A negative result is scoped to the tested representation, population, target, horizon and method.

## Discovery versus replication

Discovery may explore aggressively but produces candidates, not promoted claims. Replication freezes the candidate definition before inspecting new evidence. Generalization and prospective shadow follow when justified.

## Statistical tools

Bootstrap, permutation, FDR, effective-sample diagnostics, purging/embargo, Bayesian methods, information-theoretic estimators, point processes and other tools remain available when their assumptions match the experiment. None is a project-wide prerequisite by default.

## Core rule

> Validate the actual claim with evidence appropriate to the actual information system. Never substitute a convenient methodological convention for the scientific object.
