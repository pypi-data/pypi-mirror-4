"""Unified interface to SciPy function fitting routines.

This module provides a unified interface to the fitting of functions to data with
SciPy. All fitting routines conform to the following simple method interface:

- __init__(p) : set parameters of interpolation function, e.g. polynomial degree
- fit(x, y) : fit given input-output data
- __call__(x) / eval(x) : evaluate function on new input data

Each interpolation routine falls in one of two categories: scatter fitting or
grid fitting. They share the same interface, only differing in the definition
of input data x.

Scatter-fitters operate on unstructured scattered input data (i.e. not on a
grid). The input data consists of a sequence of ``x`` coordinates and a sequence
of corresponding ``y`` data, where the order of the ``x`` coordinates does not
matter and their location can be arbitrary. The ``x`` coordinates can have an
arbritrary dimension (although most classes are specialised for 1-D or 2-D
data). If the dimension is bigger than 1, the coordinates are provided as an
array of column vectors. These fitters have ScatterFit as base class.

Grid-fitters operate on input data that lie on a grid. The input data consists
of a sequence of x-axis tick sequences and the corresponding array of y data.
These fitters have GridFit as base class.

The module is organised as follows:

Scatter fitters
---------------

- :class:`ScatterFit` : Abstract base class for scatter fitters
- :class:`LinearLeastSquaresFit` : Fit linear regression model to data using SVD
- :class:`Polynomial1DFit` : Fit polynomial to 1-D data
- :class:`Polynomial2DFit` : Fit polynomial to 2-D data
- :class:`PiecewisePolynomial1DFit` : Fit piecewise polynomial to 1-D data
- :class:`Independent1DFit` : Interpolate N-dimensional matrix along given axis
- :class:`Delaunay2DScatterFit` : Interpolate scalar function of 2-D data, based on
                                  Delaunay triangulation (scattered data version)
- :class:`NonLinearLeastSquaresFit` : Fit a generic function to data, based on
                                      non-linear least squares optimisation.
- :class:`GaussianFit` : Fit Gaussian curve to multi-dimensional data
- :class:`Spline1DFit` : Fit a B-spline to 1-D data
- :class:`Spline2DScatterFit` : Fit a B-spline to scattered 2-D data
- :class:`RbfScatterFit` : Do radial basis function (RBF) interpolation

Grid fitters
------------

- :class:`GridFit` : Abstract base class for grid fitters
- :class:`Delaunay2DGridFit` : Interpolate scalar function defined on 2-D grid,
                               based on Delaunay triangulation
- :class:`Spline2DGridFit` : Fit a B-spline to 2-D data on a rectangular grid

Helper functions
----------------

- :func:`squash` : Flatten array, but not necessarily all the way to a 1-D array
- :func:`unsquash' : Restore an array that was reshaped by :func:`squash`
- :func:`sort_grid` : Ensure that the coordinates of a rectangular grid are in
                      ascending order
- :func:`desort_grid` : Undo the effect of :func:`sort_grid`
- :func:`vectorize_fit_func` : Factory that creates vectorised version of
                               function to be fitted to data
- :func:`randomise` : Randomise fitted function parameters by resampling
                      residuals

"""

import os.path as _osp

def _setup_test():
    """Create test() method that will run unit tests via nose."""
    args = ['', '--exe', '-w', __path__[0]]
    try:
        import nose as _nose
    except ImportError:
        def test():
            print('Could not load nose. Unit tests not available.')
        return test
    else:
        import functools
        return functools.partial(_nose.run, 'scikits.fitting', argv=args)
test = _setup_test()

from generic import *
from utils import *
from delaunay import *
from gaussian import *
from linlstsq import *
from nonlinlstsq import *
from poly import *
from rbf import *
from spline import *
