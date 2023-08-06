import logging
from math import (
    isinf,
    isnan,
    pi,
    )
import unittest

import numpy as np

from empirical.interpolate import (
    Lagrange,
    Newton,
    LagrangeBivariate,
    )
from empirical.quadrature import (
    gauss,
    clenshaw_curtis,
    legendre_gauss_lobatto,
    )


log = logging.getLogger(__name__)


class InterpolationTest(unittest.TestCase):

    def test_lagrange(self):
        test_points = np.linspace(-1, 1, 500)

        for N in [10, 15, 20, 25, 30]:
            for x in [np.linspace(-1, 1, N), legendre_gauss_lobatto(N)[0],
                      clenshaw_curtis(N)[0], gauss(N)[0]]:
                for f in [lambda x: np.sin(x), lambda x: np.cos(x),
                          lambda x: 3 + 2 * x + 8 * x ** 2 + 5 * x ** 8]:
                    y = f(x)
                    interp = Lagrange(x, y)
                    expected = f(test_points)
                    actual = interp(test_points)
                    self.assertLessEqual(np.amax(np.abs(expected - actual)),
                                         1e-8)

    def test_newton(self):
        test_points = np.linspace(-1, 1, 500)

        for N in [10, 15, 20, 25, 30]:
            for x in [np.linspace(-1, 1, N), legendre_gauss_lobatto(N)[0],
                      clenshaw_curtis(N)[0], gauss(N)[0]]:
                for f in [lambda x: np.sin(x), lambda x: np.cos(x),
                          lambda x: 3 + 2 * x + 8 * x ** 2 + 5 * x ** 8]:
                    y = f(x)
                    interp = Newton(x, y)
                    expected = f(test_points)
                    actual = interp(test_points)
                    self.assertLessEqual(np.amax(np.abs(expected - actual)),
                                         1e-8)

    def test_lagrange_bivariate_linspace(self):
        test_points = np.linspace(-1, 1, 100)
        xx, yy = np.meshgrid(test_points, test_points)
        test_points = np.empty(xx.size, dtype='complex')
        test_points.real = xx.flat
        test_points.imag = yy.flat

        for N in [10, 15, 20]:
            for M in [10, 15, 20]:
                x = np.linspace(-1, 1, N)
                y = np.linspace(-1, 1, M)
                xx, yy = np.meshgrid(x, y)
                for f in [lambda x, y: np.sin(x) * np.sin(y),
                          lambda x, y: np.cos(x) * np.cos(y)]:
                    interp = LagrangeBivariate(x, y, f(xx, yy))
                    expected = f(test_points.real, test_points.imag)
                    actual = interp(test_points)
                    self.assertLessEqual(np.amax(np.abs(expected - actual)),
                                         1e-8)

    def test_lagrange_bivariate_lgl(self):
        test_points = np.linspace(-1, 1, 100)
        xx, yy = np.meshgrid(test_points, test_points)
        test_points = np.empty(xx.size, dtype='complex')
        test_points.real = xx.flat
        test_points.imag = yy.flat

        for N in [10, 15, 20]:
            for M in [10, 15, 20]:
                x = legendre_gauss_lobatto(N)[0]
                y = legendre_gauss_lobatto(M)[0]
                xx, yy = np.meshgrid(x, y)
                for f in [lambda x, y: np.sin(x) * np.sin(y),
                          lambda x, y: np.cos(x) * np.cos(y)]:
                    interp = LagrangeBivariate(x, y, f(xx, yy))
                    expected = f(test_points.real, test_points.imag)
                    actual = interp(test_points)
                    self.assertLessEqual(np.amax(np.abs(expected - actual)),
                                         1e-8)
