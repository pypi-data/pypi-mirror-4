#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for linear least-squares fitter.

:author: Ludwig Schwardt
:license: Modified BSD

"""

import numpy as np
from numpy.testing import *

from scikits.fitting import LinearLeastSquaresFit, NotFittedError

class TestLinearLeastSquaresFit(TestCase):
    """Fit linear regression model to data from a known model, and compare."""

    def setUp(self):
        self.params = np.array([0.1, -0.2, 0.0, 0.5, 0.5])
        self.N = 1000
        self.x = np.random.randn(len(self.params), self.N)
        self.y = np.dot(self.params, self.x)
        t = np.arange(0., 10., 10. / self.N)
        self.poly_x = np.vander(t, 5).T
        self.poly_y = np.dot(self.params, self.poly_x)

    def test_fit_eval(self):
        """LinearLeastSquaresFit: Basic function fitting and evaluation using data from a known function."""
        interp = LinearLeastSquaresFit()
        self.assertRaises(NotFittedError, interp, self.x)
        interp.fit(self.x, self.y)
        y = interp(self.x)
        assert_almost_equal(interp.params, self.params, decimal=10)
        assert_almost_equal(y, self.y, decimal=10)

    def test_cov_params(self):
        """LinearLeastSquaresFit: Obtain sample statistics of parameters and compare to calculated covariance matrix."""
        interp = LinearLeastSquaresFit()
        std_y = 1.0
        M = 200
        param_set = np.zeros((len(self.params), M))
        for n in range(M):
            yn = self.poly_y + std_y * np.random.randn(len(self.poly_y))
            interp.fit(self.poly_x, yn, std_y)
            param_set[:, n] = interp.params
        mean_params = param_set.mean(axis=1)
        norm_params = param_set - mean_params[:, np.newaxis]
        cov_params = np.dot(norm_params, norm_params.T) / M
        std_params = np.sqrt(np.diag(interp.cov_params))
        self.assertTrue((np.abs(mean_params - self.params) / std_params < 0.25).all(),
                        "Sample mean parameter vector differs too much from true value")
        self.assertTrue((np.abs(cov_params - interp.cov_params) / np.abs(interp.cov_params) < 1.0).all(),
                        "Sample parameter covariance matrix differs too much from expected one")

    def test_vs_numpy(self):
        """LinearLeastSquaresFit: Compare fitter to np.linalg.lstsq."""
        interp = LinearLeastSquaresFit()
        interp.fit(self.x, self.y)
        params = np.linalg.lstsq(self.x.T, self.y)[0]
        assert_almost_equal(interp.params, params, decimal=10)
        rcond = 1e-3
        interp = LinearLeastSquaresFit(rcond)
        interp.fit(self.poly_x, self.poly_y)
        params = np.linalg.lstsq(self.poly_x.T, self.poly_y, rcond)[0]
        assert_almost_equal(interp.params, params, decimal=10)

if __name__ == "__main__":
    run_module_suite()
