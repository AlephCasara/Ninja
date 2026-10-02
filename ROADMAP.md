# Roadmap

## Phase 0 — foundation — current

- [x] Define Ninja / Master Trader boundary
- [x] Define six scout families
- [x] Record scientific foundation
- [x] Create hypothesis registry
- [x] Define validation ladder
- [x] Define Master Trader deterministic policy boundary
- [x] State clearly that independent historical validation is still pending

## Phase 1 — historical validation substrate

- [ ] Select first historical social/information corpus
- [ ] Select matching market-data universe
- [ ] Implement dataset manifests and hashes
- [ ] Implement UTC causal alignment
- [ ] Implement entity/asset aliases
- [ ] Implement no-lookahead tests
- [ ] Freeze train/validation/test periods

## Phase 2 — E1 Attention Replication

- [ ] Build first Attention Scout feature set
- [ ] Reproduce simple attention statistics
- [ ] Test volatility
- [ ] Test volume
- [ ] Test jumps
- [ ] Test MAE
- [ ] Publish positive or negative result

**Gate:** do not escalate infrastructure merely because E1 is interesting in-sample.

## Phase 3 — Cross-platform / structure

- [ ] Add second information platform
- [ ] Run platform ablation
- [ ] Estimate common attention
- [ ] Preserve platform residuals
- [ ] Run E2 disagreement/narrative tests

## Phase 4 — Propagation

- [ ] Activation timing
- [ ] Hawkes prototype
- [ ] Transfer-entropy prototype
- [ ] Compare propagation vs attention-only

## Phase 5 — Event Morphology

- [ ] Freeze event ontology v0
- [ ] Create reviewed event gold set
- [ ] Benchmark rules / compact classifier / local LLM extraction
- [ ] Test event-response similarity
- [ ] Test historical analog distributions

## Phase 6 — prospective collection

- [ ] Design live point-in-time acquisition
- [ ] Integrate Last30Days as one collector/provider
- [ ] Add dedicated source adapters where justified
- [ ] Store first_seen_at
- [ ] Compare historical-reconstruction factors with prospective factors

## Phase 7 — Master Trader shadow

- [ ] Add optional Ninja client PR
- [ ] Prove Ninja OFF parity
- [ ] Log Ninja State beside trade opportunities
- [ ] Accumulate prospective outcomes
- [ ] No trade modification

## Phase 8 — first deterministic policy

Only if a factor survives:

```text
historical OOS
+ robustness
+ prospective shadow
+ execution economics
```

Then create a policy candidate and test:

```text
MasterTrader baseline
vs
same strategy + frozen Ninja policy
```

Human approval remains required for promotion.
