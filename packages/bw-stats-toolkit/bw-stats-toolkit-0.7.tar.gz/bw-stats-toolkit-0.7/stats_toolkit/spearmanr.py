# -*- coding: utf-8 -*
from __future__ import division
import numpy as np
from scipy import stats
from scipy import __version__ as scipy_version

_chk_asarray = stats.stats._chk_asarray


def spearmanr(a, b=None, axis=0):
    '''A Spearman rank-order correlation coefficient that handles ties correctly. A correct version is provided in Scipy 0.8.

This code from http://projects.scipy.org/pipermail/scipy-user/2009-January/019198.html

    Parameters
    ----------
    a, b : 1D or 2D array_like, b is optional

        One or two 1-D or 2-D arrays containing multiple variables and
        observations. Each column of m represents a variable, and each row
        entry a single observation of those variables. Also see axis below.
        Both arrays need to have the same length in the `axis` dimension.

    axis : int or None, optional
        If axis=0 (default), then each column represents a variable, with
        observations in the rows. If axis=0, the relationship is transposed:
        each row represents a variable, while the columns contain observations.
        If axis=None, then both arrays will be raveled


    Returns
    -------

    rho: float or array (2D square)
        Spearman correlation matrix or correlation coefficient (if only 2 variables
        are given as parameters. Correlation matrix is square with length
        equal to total number of variables (columns or rows) in a and b
        combined

    t: float or array (2D square)
        t-statistic for Null hypothesis of no correlation, has same
        dimension as rho

    p-value: float or array (2D square)
        p-value for the two-sided test, has same dimension as rho
    '''
    # Check if correct version is present
    major, minor = scipy_version.split(".")[:2]
    if int(major) >= 1 or int(minor) >= "8":
        return stats.stats.spearmanr(a, b, axis)

    a, axisout = _chk_asarray(a, axis)
    ar = np.apply_along_axis(stats.rankdata, axisout, a)

    br = None
    if not b is None:
        b, axisout = _chk_asarray(b, axis)
        br = np.apply_along_axis(stats.rankdata, axisout, b)
    n = a.shape[axisout]
    rs = np.corrcoef(ar, br, rowvar=axisout)

    t = rs * np.sqrt((n - 2) / ((rs + 1.0) * (1.0 - rs)))
    prob = stats.t.sf(np.abs(t), n - 2) * 2

    if rs.shape == (2, 2):
        return rs[1, 0], t[1, 0], prob[1, 0]
    else:
        return rs, t, prob
