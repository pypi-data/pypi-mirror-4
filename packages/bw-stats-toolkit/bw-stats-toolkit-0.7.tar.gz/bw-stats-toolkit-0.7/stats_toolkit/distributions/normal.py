from __future__ import division
from base import UncertaintyBase
from numpy import random, zeros, isnan, arange
from scipy import stats
from stats_toolkit.errors import InvalidParamsError
from stats_toolkit.utils import one_row_params_array


class NormalUncertainty(UncertaintyBase):
    id = 3
    description = "Normal uncertainty"

    @classmethod
    def validate(cls, params):
        super(NormalUncertainty, cls).validate(params)
        if isnan(params['sigma']).sum() or (params['sigma'] <= 0).sum():
            raise InvalidParamsError("Real, positive sigma values are required for normal uncertainties.")

    @classmethod
    def random_variables(cls, params, size, seeded_random=None):
        if not seeded_random:
            seeded_random = random
        return seeded_random.normal(
            params['amount'],
            params['sigma'],
            size=(size, params.shape[0])).T

    @classmethod
    def cdf(cls, params, vector):
        vector = cls.check_2d_inputs(params, vector)
        results = zeros(vector.shape)
        for row in range(params.shape[0]):
            results[row, :] = stats.norm.cdf(vector[row, :],
                loc=params['amount'][row], scale=params['sigma'][row])
        return results

    @classmethod
    def ppf(cls, params, percentages):
        percentages = cls.check_2d_inputs(params, percentages)
        results = zeros(percentages.shape)
        for row in range(percentages.shape[0]):
            results[row, :] = stats.norm.ppf(percentages[row, :],
                loc=params['amount'][row], scale=params['sigma'][row])
        return results

    @classmethod
    @one_row_params_array
    def statistics(cls, params):
        return {'mean': float(params['amount']), 'mode': float(params['amount']),
            'median': float(params['amount']),
            'lower': float(params['amount'] - 2 * params['sigma']),
            'upper': float(params['amount'] + 2 * params['sigma'])}

    @classmethod
    @one_row_params_array
    def pdf(cls, params, xs=None):
        if xs == None:
            if isnan(params['minimum']):
                lower = params['amount'] - params['sigma'] * \
                    cls.standard_deviations_in_default_range
            else:
                lower = params['minimum']
            if isnan(params['maximum']):
                upper = params['amount'] + params['sigma'] * \
                    cls.standard_deviations_in_default_range
            else:
                upper = params['maximum']
            xs = arange(lower, upper, (upper - lower) / \
                cls.default_number_points_in_pdf)

        ys = stats.norm.pdf(xs, params['amount'], params['sigma'])
        return xs, ys.reshape(ys.shape[1])
