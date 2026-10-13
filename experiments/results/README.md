# Experiment results

Completed Ninja experiments remain discoverable regardless of outcome.

Do not delete or hide failed experiments merely because a later specification performs better. Negative results prevent repeated research and are part of the evidence base.

Terminal states:

- `SUPPORTED` — passed the preregistered evidence and robustness gates;
- `WEAK` — directionally interesting but below the promotion standard;
- `INCONCLUSIVE` — valid experiment, insufficient evidence either way;
- `REJECTED` — valid experiment failed the preregistered criterion;
- `INVALID` — data, estimator, leakage or protocol failure prevented the experiment from answering the question.

A result should identify its hypothesis/experiment version, dataset manifest, code revision, validation controls, effective sample-size diagnostics, multiple-testing family, untouched-test access state and explicit rejection rule.

`REJECTED` is not a software failure. `INVALID` is not evidence against the hypothesis.
