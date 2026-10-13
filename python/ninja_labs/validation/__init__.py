"""Scientific validation primitives for Ninja Labs.

The validation package exists to make falsification controls reusable and
mandatory. Domain experiments should own hypotheses; this package owns generic
mechanisms such as purging, resampling, null tests and headline gates.
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
