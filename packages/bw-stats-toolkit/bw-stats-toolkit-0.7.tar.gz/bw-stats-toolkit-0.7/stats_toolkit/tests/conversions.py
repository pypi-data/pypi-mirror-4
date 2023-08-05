import unittest
from numpy import allclose
from stats_toolkit.distributions import UncertaintyBase
from stats_toolkit.utils import construct_params_array


class ConversionTestCase(unittest.TestCase):
    def get_right_1d_array(self):
        params = construct_params_array()
        params['amount'] = 1
        params['maximum'] = 2
        params['minimum'] = 0
        params['sigma'] = 3
        return params

    def get_right_2d_array(self):
        params = construct_params_array(2)
        params['amount'] = (1, 2)
        params['sigma'] = (3, 4)
        params['maximum'] = 10
        params['minimum'] = 0
        return params

    def test_1d_dict(self):
        values = {"amount": 1.0,
            "sigma": 3.0,
            "maximum": 2.0,
            "minimum": 0.0,
            "negative": False,
            }
        self.sa_allclose(
            UncertaintyBase.from_dicts(values),
            self.get_right_1d_array(),
            )

    def test_1d_tuple(self):
        values = (1, 3, 0, 2)
        self.sa_allclose(
            UncertaintyBase.from_tuples(values),
            self.get_right_1d_array(),
            )

    def test_2d_dict(self):
        values = (
            {"amount": 1.0,
            "sigma": 3.0,
            "maximum": 10.0,
            "minimum": 0.0,
            "negative": False},
            {"amount": 2.0,
            "sigma": 4.0,
            "maximum": 10.0,
            "minimum": 0.0,
            "negative": False}
            )
        self.sa_allclose(
            UncertaintyBase.from_dicts(*values),
            self.get_right_2d_array(),
            )

    def test_2d_tuple(self):
        values = (
            (1, 3, 0, 10),
            (2, 4, 0, 10),
            )
        self.sa_allclose(
            UncertaintyBase.from_tuples(*values),
            self.get_right_2d_array(),
            )

    def sa_allclose(self, a, b):
        """allclose for structured arrays"""
        for name in a.dtype.names:
            print name, a[name], b[name]
            self.assertTrue(allclose(a[name], b[name]))
        return True
