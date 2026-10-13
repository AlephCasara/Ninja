# Semantic instrument validation

**Status:** required measurement policy for semantic/LLM-derived fields used in Ninja scientific claims.

Semantic models are measurement instruments, not historical oracles. A modern model applied retrospectively may contain post-event knowledge in its parameters even when the prompt contains only an old document. Outcome blindness in the prompt is therefore necessary but not sufficient.

## Measurement classes

### Document-grounded extraction

Fields such as actor, action, target, quoted claim, confirmation wording or explicit entity may be used retrospectively when each output is auditable against the historical input. Critical categorical fields should retain source evidence spans/refs where practical.

### Historical-context interpretation

Any external context used by the extractor must itself have `available_at <= decision_time` and be recorded in the interpretation provenance.

### Prospective interpretation

For live/prospective evidence, the model output must actually have been generated no later than the decision time.

## Human-audited calibration

Before semantic fields support replication/generalization/economic claims, validate the frozen extractor on a real human-reviewed sample stratified across relevant years, sources and event/content classes. Record at least:

- sample construction and size;
- annotation protocol and adjudication;
- model/checkpoint, prompt/schema and extractor versions;
- per-field precision/recall/F1 or appropriate agreement/error measures;
- confusion matrices for categorical fields where useful;
- error slices by source/time/event class when sample size permits;
- abstention/missing behavior;
- known failure modes and acceptable-use scope.

The gold set must be independent of future market outcomes for fields intended to describe the information itself.

## Temporal-contamination rule

A retrospective LLM output may not support a claim merely because it was instructed to ignore future knowledge. Prefer document-grounded fields whose values can be verified directly from the historical evidence. Claims requiring historical world knowledge must use a time-bounded context corpus or prospective extraction.

## Drift/version rule

Changing model checkpoint/provider, prompt, schema, decoding behavior or post-processing creates a new measurement-instrument version. Reusing a prior validation artifact requires an explicit equivalence justification; otherwise recalibrate.

## Evidence hierarchy

```text
raw historical evidence
  -> human-reviewed measurement target
  -> frozen semantic instrument
  -> measured error/uncertainty
  -> replay representation
  -> empirical market relationship
```

Measurement validity does not establish market predictiveness, and market predictiveness cannot retroactively validate a bad measurement instrument.
