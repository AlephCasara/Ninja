# Roadmap

## Phase 0 — foundation — current

- [x] Define Ninja as a research/validation project
- [x] Define six research domains
- [x] Record scientific foundation
- [x] Create hypothesis registry
- [x] Define validation ladder
- [x] Align promoted Ninja implementations with the existing Master Trader bot fleet
- [x] State clearly that independent historical validation is still pending
- [x] Define shared Bronze/Silver Internet Intelligence substrate with domain-specific Gold layers for downstream consumers

## Phase 0.5 — shared intelligence boundary

Architecture only; do not escalate implementation merely because another consumer exists.

- [x] Keep one Ninja repository while acquisition/provenance/normalization invariants remain shared
- [x] Keep Bronze and Silver domain-neutral
- [x] Keep Trade Gold and Business Gold semantically separate
- [x] Preserve Master Trader as trading authority and Business Master as business/capital authority
- [ ] Define the smallest typed Gold export contract required by the first Business Master integration
- [ ] Reuse existing acquisition/capture tooling before adding new crawler frameworks
- [ ] Split repositories/runtimes only if measured dependency, security, availability or lifecycle incompatibilities justify it

See `docs/ADR-002-SHARED-INTERNET-INTELLIGENCE-DOMAIN-GOLDS.md`.

## Phase 1 — historical validation substrate

- [ ] Select first historical social/information corpus
- [ ] Select matching market-data universe
- [ ] Implement dataset manifests and hashes
- [ ] Implement UTC causal alignment
- [ ] Implement entity/asset aliases
- [ ] Implement no-lookahead tests
- [ ] Freeze train/validation/test periods

## Phase 2 — E1 Attention Replication

- [ ] Build first attention feature set
- [ ] Reproduce simple attention statistics
- [ ] Test volatility
- [ ] Test volume
- [ ] Test jumps
- [ ] Test MAE
- [ ] Publish positive or negative result

**Gate:** do not escalate infrastructure merely because E1 is interesting in-sample.

## Phase 3 — cross-platform / information structure

- [ ] Add second information platform
- [ ] Run platform ablation
- [ ] Estimate common attention
- [ ] Preserve platform residuals
- [ ] Run E2 disagreement/narrative tests

## Phase 4 — propagation

- [ ] Activation timing
- [ ] Hawkes prototype
- [ ] Transfer Entropy prototype
- [ ] Compare propagation against attention-only baselines

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
- [ ] Compare historical reconstruction against prospective capture

## Phase 7 — first promoted Ninja implementation

Only after a factor or factor combination survives historical validation:

- [ ] choose the smallest useful runtime artifact: standalone strategy, overlay or risk/regime module
- [ ] freeze Python implementation and parameters
- [ ] add it to the Master Trader fleet as a Ninja-family component
- [ ] add `NINJA_ENABLED` family-level control
- [ ] prove `NINJA_ENABLED=false` preserves current fleet semantics
- [ ] run the promoted Ninja in dry-run / shadow
- [ ] collect prospective outcomes

## Phase 8 — live approval

Only if the implementation survives:

```text
historical OOS
+ robustness checks
+ prospective dry-run/shadow
+ execution economics
```

then compare:

```text
baseline strategy/fleet
vs
baseline + promoted Ninja implementation
```

Human approval remains required before live capital is enabled.
