# Core Research Contracts

## Status

Phase 0 v1 contract freeze.

The contracts are domain-neutral. Trading-specific targets, baselines and susceptibility variables belong in trading experiment configuration, not in the core schema.

Machine-readable drafts live in:

- `schemas/observation-v1.schema.json`
- `schemas/experiment-spec-v1.schema.json`

## Observation v1

`Observation` is the boundary between Ninja Tools and Ninja Labs.

It represents something acquired or reconstructed from an information source with enough provenance and temporal semantics to be used or rejected by a causal experiment.

### Required identity

```text
schema_version
observation_id
source_id
source_type
platform
collected_at
content_hash
provenance
```

### Temporal semantics

The central rule is that source publication time and causal availability are not silently treated as equivalent.

Observation v1 can record:

```text
published_at
first_seen_at
collected_at
available_at
available_at_basis
```

`available_at` is the timestamp at which the experiment permits the observation to become causally available. Its basis must be explicit:

```text
first_seen
published
archive_capture
collected
reconstructed
```

A historical source that only exposes publication time may use `available_at = published_at` only under an explicitly documented reconstruction policy. That observation has weaker epistemic status than a prospective first-seen record.

No experiment may silently replace an unknown first-seen timestamp with a present-day collection timestamp and then treat the result as historical availability.

### Event-level preservation

Bronze/Silver must retain event-level timestamps when the source provides them.

E1 may aggregate observations into hourly/daily attention features, but those Gold panels must be reproducible from event-level Silver data. This preserves the information needed by E3/Hawkes later.

### Relationships

Optional fields include:

```text
author_id
thread_id
parent_id
entity_refs[]
```

These should be preserved when they are source-native because author/source breadth, thread structure, independent-source counts and propagation models may depend on them. Inferred entities or event semantics belong in a separate versioned `SemanticInterpretation`; community membership alone must not manufacture an entity reference.

### Content

Observation v1 stores references and hashes rather than requiring large payloads inline:

```text
content_ref
content_hash
content_type
```

`content_ref` may point to a file, object, WARC/WACZ record, dataset row group or other replayable artifact.

### Mutable metrics

Likes, views, upvotes, ranking and similar values are snapshots, not timeless attributes.

If recorded they must include an `as_of` timestamp. A current engagement value must never be treated as the value that existed at publication time unless the source genuinely provides historical snapshots.

### Provenance

Provenance records at least:

```text
collector_id
collector_version
retrieval_ref
raw_ref?
dataset_manifest_id?
```

Additional source/access metadata may be added without changing the causal meaning of the base contract.

## ExperimentSpec v1

`ExperimentSpec` is the boundary between a research hypothesis and an executable Ninja Labs experiment.

Its purpose is to stop experimental degrees of freedom from silently changing after results are observed.

### Required identity

```text
schema_version
experiment_id
hypothesis_id
domain
dataset_manifest_ids[]
code_revision
```

### Scientific definition

An experiment declares:

```text
targets[]
baselines[]
fixed_features[]
search_space
metrics
splits
robustness_checks[]
stopping_rules
```

The actual representation may evolve, but those decisions must be explicit before final-test evaluation.

### Chronological splits

The contract distinguishes:

```text
train
validation
untouched_test
```

Optional purging/embargo metadata is recorded when labels or windows overlap.

The untouched test window is read-once evidence for a frozen candidate. Repeated adaptive use converts it into training information and invalidates its role as the final test.

### Adaptive search

Adaptive optimization is optional.

When enabled, the contract records:

```text
engine
allowed_windows
search_space
trial_budget
stopping_rule
```

For Ax, `allowed_windows` must exclude `untouched_test`.

Ax proposes trials; Ninja Labs owns the hypothesis, target, baseline, metrics, constraints and final interpretation.

### Reproducibility

Each completed experiment record should be resolvable to:

- exact code revision;
- exact dataset manifest(s);
- frozen experiment spec;
- package/environment lock state;
- trial history where adaptive search was used;
- output metrics/artifacts;
- final status: positive, negative or inconclusive.

## ExperimentSpec v2

`schemas/experiment-spec-v2.schema.json` is the active session-level experiment contract for new backtesting work. v1 is retained for compatibility with experiments created under the older fixed train/validation/untouched-test model.

Version 2 adds explicit:

```text
scientific_question
phase
replay_type
scope / exclusions
evidence boundary and outcome-access policy
point-in-time data/population rules
communication and market representations
outcome definitions / horizons
experiment-specific statistical design
negative-result scope / economic relevance
reproducibility metadata
```

Unlike v1, v2 does not require every session to pretend to be a supervised-learning train/validation/test exercise. Discovery may be adaptive and event/propagation studies may use boundaries appropriate to their scientific object. Replication/generalization/economic/prospective phases require a frozen candidate; replication/generalization/economic phases require an explicit frozen evaluation boundary, while prospective work accepts only genuinely new observations.

Operational rules are in [BACKTESTING_SESSION.md](BACKTESTING_SESSION.md).

## Contract evolution

Breaking semantic changes require a new schema version.

Adding optional metadata that does not change causal or scientific meaning may remain within v1.

The schemas are intentionally small. Domain objects are layered on top rather than expanding the core contract until it knows about every future trading or business concept.
## Replay contracts

Historical replay uses versioned schemas:

```text
semantic-interpretation-v1.schema.json
replay-state-v1.schema.json      # legacy compatibility
replay-state-v2.schema.json      # active hardened replay state
replay-universe-v1.schema.json
replay-outcome-v1.schema.json    # legacy compatibility
replay-outcome-v2.schema.json    # active hardened market-path outcome
```

State v2 adds market-row fingerprints and strategy-overlay replay type. Outcome v2 adds explicit reference-delay/path-gap tolerances. v1 remains immutable for historical compatibility.

`SemanticInterpretation` binds qualitative extraction to the exact observation content hash and records its model/extractor version and knowledge policy.

`ReplayState` is frozen from causal observations, semantic interpretations and market history available by `decision_time`. It contains no future outcome. Observation and market-row scientific fingerprints include replay-relevant causal/scientific fields needed to detect conflicting duplicate records. Reacquisition bookkeeping remains auditable through manifests/provenance without changing an otherwise identical historical state.

`ReplayUniverse` freezes the point-in-time eligible population under a versioned rule so future winners, failures and delistings cannot be selected with hindsight.

`ReplayOutcome` is computed only after the state is frozen and is linked back by `state_id/state_hash`. Its reference-price policy records the decision-to-reference delay and an explicit maximum allowed delay; excessive gaps invalidate outcome construction. Tail multiples are labels, not feature-construction inputs.

See [HISTORICAL_REPLAY.md](HISTORICAL_REPLAY.md).
