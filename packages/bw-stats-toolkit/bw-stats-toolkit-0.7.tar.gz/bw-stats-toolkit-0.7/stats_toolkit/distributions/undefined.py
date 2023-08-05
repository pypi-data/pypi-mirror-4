from __future__ import division
from base import UncertaintyBase
from numpy import repeat, tile
from stats_toolkit.errors import UndefinedDistributionError


class UndefinedUncertainty(UncertaintyBase):
    """Undefined or unknown uncertainty"""
    id = 0
    description = "Undefined or unknown uncertainty"

    @classmethod
    def random_variables(cls, params, size, seeded_random=None):
        return repeat(params['amount'], size).reshape((params.shape[0],
            size))

    @classmethod
    def cdf(cls, params, vector):
        raise UndefinedDistributionError("Can't calculate percentages for an undefined distribution.")

    @classmethod
    def ppf(cls, params, percentages):
        return tile(params['amount'].reshape((params.shape[0], 1)),
            percentages.shape[1])


class NoUncertainty(UndefinedUncertainty):
    id = 1
    description = "No uncertainty"
