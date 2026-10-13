# E1 Robustness and Final-Test Vault

> **Policy status:** transitional/legacy for E1 scientific authority. `docs/BACKTESTING_POLICY.md` supersedes any universal synthetic/Monte-Carlo prerequisite or claim that E1 gates qualitatively different Ninja research. These documents remain implementation history until the corresponding code is surgically aligned.


E1 treats the 2025 split as a scarce scientific resource rather than another tuning window.

## Release sequence

```text
canonical dataset accepted
        ↓
controlled-world estimator gate
        ↓
64-world Monte Carlo estimator gate
        ↓
full E1 backtester signal/null gate
        ↓
clean-code evidence check
        ↓
preregistration seal
        ↓
2021–2023 train / 2024 validation
        ↓
PRIMARY must be SUPPORTED
        ↓
robustness gate on 2021–2024 only
        ↓
final-test seal
        ↓
one 2025 primary evaluation
```

If the preregistered primary comparison is `WEAK`, `INCONCLUSIVE`, `REJECTED`, or `INVALID`, the robustness runner does not search for a rescue path and 2025 remains sealed.

## Frozen robustness gates

Before any empirical E1 outcome was observed, E1 v1 registered:

- four chronological validation blocks, with at least three showing positive incremental gain;
- drop the best validation block and require remaining aggregate gain to stay positive;
- leave each training year (2021, 2022, 2023) out in turn, requiring at least two of three refits to retain positive validation gain;
- 32 attention negative controls using 96-bin block permutation;
- at most 10% of negative controls may reach the minimum meaningful 0.5% gain;
- the observed primary gain must exceed the p95 negative-control gain.

These checks reproduce the exact common-support population used by the original E1 comparison. They do not silently increase N by dropping features that were required in the registered comparison family.

## Final-test seal

The final-test seal can only be created if:

1. the preregistration seal still verifies;
2. the exact sealed train/validation artifact reports the primary comparison as `SUPPORTED`;
3. the robustness artifact reports `PASSED`;
4. manifest, experiment configuration, train/validation result and robustness result hashes all match.

Creating the final-test seal uses only the untouched-test metadata already stored in the dataset manifest. It does **not** resolve, hash, or read the physical 2025 Parquet.

## Single-access ledger

The final evaluator creates an access ledger with `status=STARTED` **before** resolving or hashing the physical untouched-test file. If that ledger already exists, the evaluator refuses to run again.

A crashed or failed final evaluation therefore consumes that access attempt rather than silently allowing repeated looks at 2025. A new attempt requires a new preregistered experiment generation and explicit scientific justification.

## Final evaluation

The final evaluator:

- verifies the final-test seal;
- creates the access ledger;
- checks the physical 2025 artifact against the SHA-256 already frozen in the manifest;
- refits the frozen baseline and candidate using development data only;
- evaluates only the preregistered `future_rv`, 4-hour, seasonal-attention primary comparison;
- uses the frozen embargo, block inference, minimum meaningful effect and alpha;
- emits no secondary 2025 fishing results.

The result is `SUPPORTED`, `REJECTED`, or `INCONCLUSIVE`. A negative final result is a valid scientific delivery.
