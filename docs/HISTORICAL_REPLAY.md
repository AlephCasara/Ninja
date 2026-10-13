# Historical replay formalism

## Purpose

Historical replay is the executable boundary between Ninja's information science and future outcomes.

Its primary invariant is:

> the representation of the world at time `t` is frozen before any observation from `t+h` is revealed.

The replay engine does not decide which scientific method is correct. It creates a causal research surface on which State Replay, Event Replay, Propagation Replay and later strategy experiments can be run without silently mixing future information into the state.

## 1. Three separate objects

Ninja separates:

```text
Observation -> SemanticInterpretation -> FrozenReplayState
                                         |
                                         +---- future hidden
                                         |
                                         v
                                   ReplayOutcome
```

### Observation

An observation is source evidence and provenance. It must preserve source clocks, content hash/reference, author/thread relationships and point-in-time engagement snapshots when available.

Replay identity uses a **causal scientific fingerprint**: content plus replay-relevant clocks/fields. Reacquisition bookkeeping such as a new local collection time, storage path or retrieval reference may change without changing the historical scientific state; those details remain auditable through dataset manifests/provenance. By contrast, a changed `available_at`, source-native relationship, engagement snapshot or other replay-relevant field is a scientific conflict and must not be silently deduplicated.

No source is assigned an inferred economic entity merely because of the community or channel from which it came. A post in `r/CryptoCurrency`, for example, is not automatically a BTC observation.

### SemanticInterpretation

A semantic interpretation is a versioned scientific instrument applied to one or more observations. Typical outputs may include:

- entities;
- actor/action/target tuples;
- event type;
- claim/factuality/uncertainty;
- source authority descriptors;
- stance;
- novelty representation;
- narrative membership;
- embeddings or other qualitative structure.

The interpretation contract records the observation content hash, extractor/model version and knowledge policy.

An interpretation used in replay must be outcome-blind and grounded in its declared inputs.

A modern model may be used retrospectively for **document-only extraction** when its input is restricted to the historical evidence and the extracted fields are auditable against that evidence. This does not make the model's internal world knowledge causally historical; claims that require external context must use an explicit historical-context cutoff or prospective extraction. Semantic measurements used beyond discovery must follow [`SEMANTIC_INSTRUMENT_VALIDATION.md`](SEMANTIC_INSTRUMENT_VALIDATION.md).

### FrozenReplayState

For subject/asset `a` and decision time `t`, define the observations causally available under clock policy `c`:

$$
\mathcal O_{a,t}^{(c)} = \{o_i : \tau_c(o_i) \le t\}.
$$

Let a versioned semantic extractor produce:

$$
z_i^{(v)} = \phi_v(o_i, C_{\le t}),
$$

where any context $C$ must itself be available by `t`.

The information representation is

$$
N_{a,t}^{(v)} = F_v\left(\mathcal O_{a,t}^{(c)}, Z_{a,t}^{(v)}\right),
$$

and the conventional market state is

$$
M_{a,t}^{(u)} = G_u(\mathcal M_{a,\le t}).
$$

The frozen replay state is

$$
X_{a,t}^{(v,u,c)} = \left(N_{a,t}^{(v)}, M_{a,t}^{(u)}\right).
$$

The serialized scientific content of $X$ is hashed. Wall-clock research metadata such as when the replay was generated does not alter this state hash. Market rows are also fingerprinted under an explicit row identity; exact duplicates are deduplicated and conflicting values for the same market identity are invalid rather than order-dependent.

## 2. Freeze/reveal separation

Only after $X_{a,t}$ exists may future outcomes be computed:

$$
Y_{a,t,H} = H_Y(\mathcal M_{a,(t,t+H]}).
$$

This is intentionally a separate module and schema.

The future outcome is linked to `state_id` and `state_hash`; it cannot mutate the frozen state. Outcome construction must also declare the maximum allowed delay between `decision_time` and the reference price plus the maximum allowed gap inside the revealed market path. Exceeding either tolerance invalidates that outcome instead of silently shifting the effective entry time or bridging missing market history. Conflicting prices at the same timestamp are invalid.

This provides a structural rule against a common research error:

```text
future winner
-> inspect what it looked like before winning
-> invent feature from the winner
-> claim prediction
```

That workflow is allowed only as explicitly labelled **discovery**. The resulting feature/rule must then be frozen and replicated on data not used to invent it.

## 3. Causal clock policies

Different scientific questions may require different clocks. Ninja therefore does not silently collapse them.

Candidate policies include:

- `published`: when the source says the item was published;
- `first_seen`: when Ninja/archive evidence first observed it;
- `explicit_available_at`: a dataset-specific causal availability rule.

The same hypothesis may be tested under more than one predeclared clock as a sensitivity analysis. The clock may not be selected after inspecting which one produces the preferred market result.

## 4. Qualitative AI as a measurement instrument

LLMs are permitted as qualitative observation instruments, not as oracles of future financial meaning.

The preferred separation is:

```text
historical content
-> typed qualitative extraction
-> information/network representation
-> empirical relationship with later outcome
```

rather than:

```text
historical content
-> LLM says "bullish"
-> backtest the LLM opinion
```

If an interpretation uses historical context beyond the document itself, `context_max_available_at <= decision_time` is mandatory.

Prospective model outputs must actually have been generated no later than the decision time.

## 5. State, event and propagation replay

The same freeze/reveal contract supports different scientific objects.

### State Replay

$$
P(Y_{t+h}\mid M_t,N_t)
\quad\text{vs}\quad
P(Y_{t+h}\mid M_t).
$$

Appropriate for continuously evolving activity, semantic state, entropy, narrative concentration, network state and susceptibility.

### Event Replay

For event $e_i$:

$$
e_i=(t_i,c_i,z_i,g_i,s_i),
$$

where `c` is morphology, `z` semantic representation, `g` propagation/network state and `s` market context.

The scientific object is the conditional response distribution of held-out or later events, not merely a mean return around famous examples.

### Propagation Replay

A propagation state can include point-process intensity, cascade topology, source diversity, activation order, latency, cross-platform transitions and Hawkes/other process estimates.

Those representations must be computed from events known by the freeze time.

## 6. Extreme-opportunity outcomes without winner bias

Ninja may explicitly study rare multiples such as 2x, 5x, 10x, 50x and 100x. They are **outcomes**, not privileged feature definitions.

For reference price $P_t$ and multiple $m>1$, define first passage:

$$
\tau_m(t)=\inf\{u>t: P_u/P_t \ge m\}.
$$

If the multiple is not reached within horizon $H$, the observation is right-censored at $t+H$.

Also record path quantities such as:

$$
MFE_H(t)=\max_{u\in[t,t+H]}\left(P_u/P_t-1\right),
$$

$$
MAE_H(t)=\min_{u\in[t,t+H]}\left(P_u/P_t-1\right),
$$

and adverse excursion before first passage.

### Point-in-time universe requirement

Tail research must start from the eligible universe $U_t$ that actually existed at `t`:

$$
U_t=\{a: a\text{ existed and met the declared point-in-time eligibility rule at }t\}.
$$

The population should include, where data permit:

- future extreme winners;
- ordinary assets;
- assets that failed;
- delisted assets;
- illiquid assets;
- assets that briefly pumped and collapsed.

Selecting known winners first and searching backward is not a confirmatory design.

### Two legitimate discovery lanes

**Outcome-blind emergence discovery** may cluster or characterize $X_t$ without future labels, then inspect whether discovered states are enriched for tail outcomes.

**Label-aware exploratory discovery** may use tail labels inside a designated discovery partition to learn candidate rules. Those rules remain exploratory until frozen and replicated on a later/held-out point-in-time universe.

Neither lane permits the replication set to influence the representation or detector.

## 7. Multi-objective outcome vector

To avoid making one financial objective define the entire science, a replay may attach a vector of later outcomes:

$$
Y_{t,H}=\left(
R_H,
RV_H,
Jump_H,
Volume_H,
MFE_H,
MAE_H,
\tau_{2x},
\tau_{5x},
\tau_{10x},
\tau_{50x},
\tau_{100x},
\ldots
\right).
$$

A representation is therefore not constructed solely to explain 100x winners, BTC volatility or any other single target.

Specific experiments choose subsets of $Y$ and declare those choices in the experiment contract.

## 8. Discovery, replication and promotion

```text
causal replay states
        ↓
discovery
        ↓
candidate relationship
        ↓
freeze representation/detector/target/population
        ↓
replication on unseen evidence
        ↓
generalization
        ↓
economic strategy overlay
        ↓
prospective shadow
        ↓
capital
```

A failed detector rejects that detector under its tested conditions. It does not reject every other representation of the underlying information process.

## 9. Code boundary

The current implementation lives in `python/ninja_labs/replay/`:

- `models.py`: typed causal state and semantic interpretation contracts;
- `core.py`: causal slicing and state freeze, currently emitting ReplayState v2;
- `universe.py`: point-in-time population freeze for survivorship-safe studies;
- `outcomes.py`: future path and first-passage labels, currently emitting ReplayOutcome v2.

The v1 replay-state/outcome schemas remain preserved for compatibility; breaking replay-contract changes advance the schema version rather than mutating historical records.

The design intentionally keeps outcome computation out of the state-construction module.
