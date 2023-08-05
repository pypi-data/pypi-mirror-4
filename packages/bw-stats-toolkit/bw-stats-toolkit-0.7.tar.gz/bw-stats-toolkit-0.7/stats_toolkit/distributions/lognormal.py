from __future__ import division
from base import UncertaintyBase
from numpy import random, zeros, exp, log, isnan, arange, abs
from scipy import stats
from stats_toolkit.errors import InvalidParamsError, ImproperBoundsError
from stats_toolkit.utils import one_row_params_array


class LognormalUncertainty(UncertaintyBase):
    id = 2
    description = "Lognormal uncertainty"

    @classmethod
    def transform_negative(cls, params):
        """Log-transform mean. Default is that this is done ahead of time."""
        params['negative'] = params['amount'] < 0
        params['amount'] = log(abs(params['amount']))
        return params

    @classmethod
    def validate(cls, params, transform=False):
        """Custom validation because mean gets log-transformed"""
        if transform:
            cls.transform_negative(params)
        # No mean value
        if isnan(params['amount']).sum():
            raise InvalidParamsError("Mean values must always be defined.")
        # No sigma
        if isnan(params['sigma']).sum() or (params['sigma'] <= 0).sum():
            raise InvalidParamsError("Real, positive sigma values are required for lognormal uncertainties.")
        # Minimum <= Maximum
        if (params['minimum'] >= params['maximum']).sum():
            raise ImproperBoundsError
        # Mean out of (minimum, maximum) range
        means = exp(params['amount'])
        neg_mask = params['negative']
        if (params['minimum'] > means)[~neg_mask].sum() or \
                (params['minimum'] > -1 * means)[neg_mask].sum() or \
                (params['maximum'] < means)[~neg_mask].sum() or \
                (params['maximum'] < -1 * means)[neg_mask].sum():
            raise ImproperBoundsError

    @classmethod
    def random_variables(cls, params, size, seeded_random=None,
            transform=False):
        if transform:
            cls.transform_negative(params)
        if not seeded_random:
            seeded_random = random
        data = seeded_random.lognormal(
            params['amount'],
            params['sigma'],
            size=(size, params.shape[0])).T
        # Negative is needed because log loses sign information.
        # User is responsible for setting 'negative' bit correctly
        # Error handling not included, as this loop is called many times
        data[params['negative'], :] = -1 * data[params['negative'], :]
        return data

    @classmethod
    def cdf(cls, params, vector, transform=False):
        if transform:
            cls.transform_negative(params)
        vector = cls.check_2d_inputs(params, vector)
        # Vector is now shape (1,n). Correct vector sign.
        vector[params['negative']] = -1 * vector[params['negative']]
        results = zeros(vector.shape)
        for row in range(params.shape[0]):
            # SciPy doesn't seem to handle lognormal distributions with means
            # less than one correctly.
            results[row, :] = stats.norm.cdf(log(vector[row, :]),
                params['sigma'][row], loc=params['amount'][row])
        return results

    @classmethod
    def ppf(cls, params, percentages, transform=False):
        if transform:
            cls.transform_negative(params)
        percentages = cls.check_2d_inputs(params, percentages)
        results = zeros(percentages.shape)
        for row in range(percentages.shape[0]):
            # SciPy doesn't seem to handle lognormal distributions with means
            # less than one correctly.
            # results[row, :] = stats.lognorm.ppf(percentages[row, :],
            #     params['sigma'][row], loc=params['amount'][row])
            results[row, :] = exp(stats.norm.ppf(percentages[row, :],
                params['sigma'][row], loc=params['amount'][row]))
        results[params['negative']] = -1 * results[params['negative']]
        return results

    @classmethod
    @one_row_params_array
    def statistics(cls, params, transform=False):
        if transform:
            cls.transform_negative(params)
        negative = -1 if bool(params['negative']) else 1
        mu = float(params['amount'])
        sigma = float(params['sigma'])
        geometric_mu = exp(mu)
        geometric_sigma = exp(sigma)
        mean = exp(mu + sigma ** 2 / 2)
        mode = exp(mu - sigma ** 2)
        ci_95_lower = geometric_mu / (geometric_sigma ** 2)
        ci_95_upper = geometric_mu * (geometric_sigma ** 2)
        if negative == -1:
            ci_95_lower, ci_95_upper = ci_95_upper, ci_95_lower
        return {'median': negative * geometric_mu, 'mode': negative * mode,
            'mean': negative * mean, 'lower': negative * ci_95_lower,
            'upper': negative * ci_95_upper}

    @classmethod
    @one_row_params_array
    def pdf(cls, params, xs=None, transform=False):
        """Generate probability distribution function for lognormal distribution.

Done by hand to avoid problematic SciPy lognormal pdf function, and deal with neagtive funkiness. Will choose a minimum of 1e-9 if mean is smallish to make a nicer graph."""
        if transform:
            cls.transform_negative(params)

        is_negative = bool(params['negative'])
        neg_multiplier = -1 if is_negative else 1
        # Mean is positive and log-transformed
        mean = float(params['amount'])
        sigma = float(params['sigma'])
        if xs == None:
            std_devs = cls.standard_deviations_in_default_range
            # Min, max are positive, in correct order
            maximum, minimum = (float(params['maximum']),
                float(params['minimum']))
            if is_negative:
                minimum, maximum = maximum * neg_multiplier, minimum * \
                    neg_multiplier

            if isnan(minimum):
                if 1e-5 < exp(mean) < 10:
                    # Graph looks much nicer if it starts from zero
                    minimum = 1e-9
                else:
                    minimum = exp(mean - sigma * std_devs)
            if isnan(maximum):
                maximum = exp(mean + sigma * std_devs)

            xs = arange(minimum, maximum, (maximum - minimum) / \
                cls.default_number_points_in_pdf)

        else:
            xs = xs * neg_multiplier

        # (2 * pi) ** 0.5 = 2.5066282746310002
        ys = 1 / (xs * sigma * 2.5066282746310002) * exp(-(log(xs) - mean
            ) ** 2 / (2 * sigma ** 2))

        if len(ys.shape) == 2:
            ys = ys.reshape(ys.shape[1])

        return xs * neg_multiplier, ys
