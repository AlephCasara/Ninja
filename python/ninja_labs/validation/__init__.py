"""Scientific validation primitives for Ninja Labs.

The validation package exposes reusable statistical and falsification primitives.
Domain experiments own hypotheses and select controls that match the scientific
object under docs/BACKTESTING_POLICY.md; no primitive is a universal gate.
"""

from ninja_labs.validation.core import (
    benjamini_hochberg,
    effective_sample_size,
    ols_slope,
    pearson_r,
)
from ninja_labs.validation.headline import assess_headline_eligibility
from ninja_labs.validation.resampling import (
    block_permutation_test,
    circular_shift,
    moving_block_bootstrap,
)
from ninja_labs.validation.splits import assign_purged_split

__all__ = [
    "assess_headline_eligibility",
    "assign_purged_split",
    "benjamini_hochberg",
    "block_permutation_test",
    "circular_shift",
    "effective_sample_size",
    "moving_block_bootstrap",
    "ols_slope",
    "pearson_r",
]
