import unittest

import numpy as np

from empirical.quadrature import (
    periodic_trapezoid,
    trapezoid,
    clenshaw_curtis,
    gauss,
    legendre_gauss_lobatto,
    )


def function(x):
    return x * np.sin(30 * x) + np.cos(5 * x)


def function_integral(x):
    return (-(1 / 30) * x * np.cos(30 * x) +
             (1 / 5) * np.sin(5 * x) +
             (1 / 900) * np.sin(30 * x))

integration_value = function_integral(1) - function_integral(-1)
N = 250


class QuadratureTest(unittest.TestCase):

    def test_pt(self):
        x, w = periodic_trapezoid(N)
        self.assertEqual(x.shape, (N,))
        self.assertEqual(w.shape, (N,))
        self.assertNotIn(-1, x)
        self.assertNotIn(1, x)
        integrate = np.sum(x * w)
        self.assertAlmostEqual(integrate, 0, places=10)
        integrate = np.sum(function(x) * w)
        self.assertAlmostEqual(integrate, integration_value, places=4)

    def test_t(self):
        x, w = trapezoid(N)
        self.assertEqual(x.shape, (N + 1,))
        self.assertEqual(w.shape, (N + 1,))
        self.assertEqual(x[0], -1)
        self.assertEqual(x[-1], 1)
        integrate = np.sum(x * w)
        self.assertAlmostEqual(integrate, 0, places=10)
        integrate = np.sum(function(x) * w)
        self.assertAlmostEqual(integrate, integration_value, places=2)

    def test_c(self):
        # Even N
        x, w = clenshaw_curtis(N)
        self.assertEqual(x.shape, (N + 1,))
        self.assertEqual(w.shape, (N + 1,))
        self.assertEqual(x[0], -1)
        self.assertEqual(x[-1], 1)
        integrate = np.sum(x * w)
        self.assertAlmostEqual(integrate, 0, places=10)
        integrate = np.sum(function(x) * w)
        self.assertAlmostEqual(integrate, integration_value, places=10)
        # Odd N
        x, w = clenshaw_curtis(N + 1)
        self.assertEqual(x.shape, (N + 2,))
        self.assertEqual(w.shape, (N + 2,))
        self.assertEqual(x[0], -1)
        self.assertEqual(x[-1], 1)
        integrate = np.sum(x * w)
        self.assertAlmostEqual(integrate, 0, places=10)
        integrate = np.sum(function(x) * w)
        self.assertAlmostEqual(integrate, integration_value, places=10)

    def test_g(self):
        x, w = gauss(N)
        self.assertEqual(x.shape, (N,))
        self.assertEqual(w.shape, (N,))
        integrate = np.sum(x * w)
        self.assertAlmostEqual(integrate, 0, places=10)
        integrate = np.sum(function(x) * w)
        self.assertAlmostEqual(integrate, integration_value, places=10)

    def test_g_long(self):
        # Taking N > 300 will output a logging message.
        # I don't yet have a framework to test that it does get logged.
        x, w = gauss(301)
        self.assertEqual(x.shape, (301,))
        self.assertEqual(w.shape, (301,))
        integrate = np.sum(x * w)
        self.assertAlmostEqual(integrate, 0, places=10)
        integrate = np.sum(function(x) * w)
        self.assertAlmostEqual(integrate, integration_value, places=10)

    def test_g_long(self):
        x, w = legendre_gauss_lobatto(N)
        self.assertEqual(x.shape, (N,))
        self.assertEqual(w.shape, (N,))
        integrate = np.sum(x * w)
        self.assertAlmostEqual(integrate, 0, places=10)
        integrate = np.sum(function(x) * w)
        self.assertAlmostEqual(integrate, integration_value, places=10)
