import copy
import logging
from math import (
    isinf,
    isnan,
    pi,
    )
import unittest

import numpy as np

from scipy.special import hankel1

from empirical.domain import (
    Segment,
    ArcSegment,
    RadialSegment,
    Domain,
    )
from empirical.basis import MFSBasis
from empirical.quadrature import (
    clenshaw_curtis,
    gauss,
    periodic_trapezoid,
    trapezoid,
    )


log = logging.getLogger(__name__)


class MFSBasisTest(unittest.TestCase):

    def test_constructor_points(self):
        points = np.ones(30)
        b = MFSBasis(points)
        self.assertEqual(b.N, 30)
        self.assertTrue(np.all(b.q == points))
        self.assertFalse(hasattr(b, 'Z'))

    def test_constructor_seg(self):
        s = ArcSegment(0, 1, 0, 2 * pi)
        b = MFSBasis(s)
        r = np.abs(b.q)
        self.assertAlmostEqual(np.min(r), 1, places=15)
        self.assertAlmostEqual(np.max(r), 1, places=15)

    def test_constructor_seg_tau(self):
        s = ArcSegment(0, 1, 0, 2 * pi)
        b = MFSBasis(s, tau=0.05)
        r = np.abs(b.q)
        self.assertAlmostEqual(np.min(r), np.max(r), places=15)
        self.assertNotAlmostEqual(np.max(r), 1, places=15)

    def test_constructor_seg_n(self):
        s = ArcSegment(0, 1, 0, 2 * pi)
        b = MFSBasis(s, N=50)
        self.assertEqual(b.N, 50)
        self.assertEqual(b.t.shape[0], 50)
        self.assertEqual(b.q.shape[0], 50)
        r = np.abs(b.q)
        self.assertAlmostEqual(np.min(r), 1, places=15)
        self.assertAlmostEqual(np.max(r), 1, places=15)

    def test_constructor_seg_nmult(self):
        s = ArcSegment(0, 1, 0, 2 * pi)
        b = MFSBasis(s, N=50, n_multiplier=3)
        self.assertEqual(b.N, 150)
        self.assertEqual(b.t.shape[0], 150)
        self.assertEqual(b.q.shape[0], 150)
        r = np.abs(b.q)
        self.assertAlmostEqual(np.min(r), 1, places=15)
        self.assertAlmostEqual(np.max(r), 1, places=15)

    def test_constructor_seg_real_only(self):
        s = ArcSegment(0, 1, 0, 2 * pi)
        b = MFSBasis(s)
        self.assertFalse(b.real_only)

        b = MFSBasis(s, real_only=True)
        self.assertTrue(b.real_only)

    def test_update_n(self):
        s = ArcSegment(0, 1, 0, 2 * pi)
        b = MFSBasis(s, N=20)
        self.assertEqual(b.N, 20)
        self.assertEqual(b.t.shape[0], 20)
        self.assertEqual(b.q.shape[0], 20)
        r = np.abs(b.q)
        self.assertAlmostEqual(np.min(r), 1, places=15)
        self.assertAlmostEqual(np.max(r), 1, places=15)

        b.update_n(40)
        self.assertEqual(b.N, 40)
        self.assertEqual(b.t.shape[0], 40)
        self.assertEqual(b.q.shape[0], 40)
        r = np.abs(b.q)
        self.assertAlmostEqual(np.min(r), 1, places=15)
        self.assertAlmostEqual(np.max(r), 1, places=15)

    def test_matrix_helmholtz_no_derivatives(self):
        s = ArcSegment(0, 1, 0, 2 * pi, M=50)
        b = MFSBasis(s, N=50, tau=0.05)
        A = b.matrix(5, s.x)
        self.assertEqual(A.shape, (50, 50))
        self.assertTrue(np.any(A.imag != 0))

        for i in range(50):
            for j in range(b.N):
                dist = np.abs(s.x.flat[i] - b.q.flat[j])
                self.assertEqual(A[i, j], 0.25j * hankel1(0, 5 * dist))

        b = MFSBasis(s, N=20, tau=0.05)
        A = b.matrix(3, s.x)
        self.assertEqual(A.shape, (50, 20))
        self.assertTrue(np.any(A.imag != 0))

        for i in range(50):
            for j in range(b.N):
                dist = np.abs(s.x.flat[i] - b.q.flat[j])
                self.assertEqual(A[i, j], 0.25j * hankel1(0, 3 * dist))

        b = MFSBasis(s, N=20, tau=0.05, real_only=True)
        A = b.matrix(1, s.x)
        self.assertEqual(A.shape, (50, 20))
        self.assertTrue(np.all(A.imag == 0))

        for i in range(50):
            for j in range(b.N):
                dist = np.abs(s.x.flat[i] - b.q.flat[j])
                self.assertEqual(A[i, j], (0.25j * hankel1(0, dist)).real)

    def test_matrix_helmholtz_normal_derivatives(self):
        s = ArcSegment(0, 1, 0, 2 * pi, M=50)
        b = MFSBasis(s, N=50, tau=0.05)
        A = b.matrix(5, s, plain_function=False, normal_derivative=True)
        self.assertEqual(A.shape, (50, 50))
        self.assertTrue(np.any(A.imag != 0))

        for i in range(50):
            for j in range(b.N):
                d = s.x.flat[i] - b.q.flat[j]
                r = np.abs(d)
                dr = d / r
                nx = s.nx.flat[i]
                nx /= np.abs(nx)
                H1 = -5 * 0.25j * hankel1(1, 5 * r)
                val = H1 * (dr.real * nx.real + dr.imag * nx.imag)
                self.assertAlmostEqual(A[i, j], val, places=14)

        b = MFSBasis(s, N=50, tau=0.05, real_only=True)
        A = b.matrix(5, s, plain_function=False, normal_derivative=True)
        self.assertEqual(A.shape, (50, 50))
        self.assertTrue(np.all(A.imag == 0))

        for i in range(50):
            for j in range(b.N):
                dist = np.abs(s.x.flat[i] - b.q.flat[j])
                d = s.x.flat[i] - b.q.flat[j]
                r = np.abs(d)
                dr = d / r
                nx = s.nx.flat[i]
                nx /= np.abs(nx)
                H1 = -5 * 0.25j * hankel1(1, 5 * r)
                val = H1.real * (dr.real * nx.real + dr.imag * nx.imag)
                self.assertAlmostEqual(A[i, j], val, places=14)

    def test_matrix_helmholtz_xy_derivatives(self):
        s = ArcSegment(0, 1, 0, 2 * pi, M=50)
        b = MFSBasis(s, N=50, tau=0.05)
        Ax, Ay = b.matrix(5, s, plain_function=False, xy_derivative=True)
        self.assertEqual(Ax.shape, (50, 50))
        self.assertEqual(Ay.shape, (50, 50))
        self.assertTrue(np.any(Ax.imag != 0))
        self.assertTrue(np.any(Ay.imag != 0))

        for i in range(50):
            for j in range(b.N):
                d = s.x.flat[i] - b.q.flat[j]
                r = np.abs(d)
                dr = d / r
                H1 = -5 * 0.25j * hankel1(1, 5 * r)
                valx = H1 * dr.real
                valy = H1 * dr.imag
                self.assertAlmostEqual(Ax[i, j], valx, places=14)
                self.assertAlmostEqual(Ay[i, j], valy, places=14)

        b = MFSBasis(s, N=50, tau=0.05, real_only=True)
        Ax, Ay = b.matrix(5, s, plain_function=False, xy_derivative=True)
        self.assertEqual(Ax.shape, (50, 50))
        self.assertEqual(Ay.shape, (50, 50))
        self.assertTrue(np.all(Ax.imag == 0))
        self.assertTrue(np.all(Ay.imag == 0))

        for i in range(50):
            for j in range(b.N):
                d = s.x.flat[i] - b.q.flat[j]
                r = np.abs(d)
                dr = d / r
                H1 = -5 * 0.25j * hankel1(1, 5 * r)
                valx = H1.real * dr.real
                valy = H1.real * dr.imag
                self.assertAlmostEqual(Ax[i, j], valx, places=14)
                self.assertAlmostEqual(Ay[i, j], valy, places=14)

    def test_matrix_laplace_no_derivatives(self):
        s = ArcSegment(0, 1, 0, 2 * pi, M=50)
        b = MFSBasis(s, N=50, tau=0.05)
        A = b.matrix(0, s.x)
        self.assertEqual(A.shape, (50, 50))
        self.assertTrue(np.all(A.imag == 0))

        for i in range(50):
            for j in range(b.N):
                dist = np.abs(s.x.flat[i] - b.q.flat[j])
                self.assertEqual(A[i, j], -np.log(dist) / (2 * pi))

    def test_matrix_laplace_normal_derivative(self):
        s = ArcSegment(0, 1, 0, 2 * pi, M=50)
        b = MFSBasis(s, N=50, tau=0.05)
        A = b.matrix(0, s, plain_function=False, normal_derivative=True)
        self.assertEqual(A.shape, (50, 50))
        self.assertTrue(np.all(A.imag == 0))

        for i in range(50):
            for j in range(b.N):
                d = s.x.flat[i] - b.q.flat[j]
                r = np.abs(d)
                dr = d / r
                nx = s.nx.flat[i]
                nx /= np.abs(nx)
                laplace = -1 / (2 * pi * r)
                val = laplace * (dr.real * nx.real + dr.imag * nx.imag)
                self.assertAlmostEqual(A[i, j], val, places=14)

    def test_matrix_laplace_xy_derivative(self):
        s = ArcSegment(0, 1, 0, 2 * pi, M=50)
        b = MFSBasis(s, N=50, tau=0.05)
        Ax, Ay = b.matrix(0, s, plain_function=False, xy_derivative=True)
        self.assertEqual(Ax.shape, (50, 50))
        self.assertEqual(Ay.shape, (50, 50))
        self.assertTrue(np.all(Ax.imag == 0))
        self.assertTrue(np.all(Ay.imag == 0))

        for i in range(50):
            for j in range(b.N):
                d = s.x.flat[i] - b.q.flat[j]
                r = np.abs(d)
                dr = d / r
                laplace = -1 / (2 * pi * r)
                valx = laplace * dr.real
                valy = laplace * dr.imag
                self.assertAlmostEqual(Ax[i, j], valx, places=14)
                self.assertAlmostEqual(Ay[i, j], valy, places=14)

    def test_matrix_size(self):
        s = ArcSegment(0, 1, 0, 2 * pi, M=50)
        b = MFSBasis(s, N=50, tau=0.05)
        A = b.matrix(0, s.x)
        self.assertEqual(A.shape, (50, 50))

        s = ArcSegment(0, 1, 0, 2 * pi, M=20)
        b = MFSBasis(s, N=50, tau=0.05)
        A = b.matrix(0, s.x)
        self.assertEqual(A.shape, (20, 50))

        s = ArcSegment(0, 1, 0, 2 * pi, M=50)
        b = MFSBasis(s, N=20, tau=0.05)
        A = b.matrix(0, s.x)
        self.assertEqual(A.shape, (50, 20))

    def test_copy(self):
        f = lambda t: 5+3j * t
        b = MFSBasis(f, 50, True, 0.5, 5)
        c = copy.copy(b)
        self.assertIs(b.Z, c.Z)
        self.assertEqual(b.N, c.N)
        self.assertEqual(b.real_only, c.real_only)
        self.assertEqual(b.n_multiplier, c.n_multiplier)
        self.assertIs(b.q, c.q)
        self.assertIs(b.t, c.t)

    def test_deepcopy(self):
        f = lambda t: 5+3j * t
        b = MFSBasis(f, 50, True, 0.5, 5)
        c = copy.deepcopy(b)
        self.assertIs(b.Z, c.Z)
        self.assertEqual(b.N, c.N)
        self.assertEqual(b.real_only, c.real_only)
        self.assertEqual(b.n_multiplier, c.n_multiplier)
        self.assertIsNot(b.q, c.q)
        self.assertIsNot(b.t, c.t)

    def test_repr(self):
        for N in [20, 30, 84, 29]:
            for n_mult in [1, 2, 3]:
                b = MFSBasis(np.empty(N), n_multiplier=n_mult)
                self.assertEquals("<MFSBasis: N=" + str(N) +
                                  ", n_multiplier=" + str(n_mult) +
                                  ", real_only=False>",
                                  repr(b))

    def test_plot(self):
        from matplotlib.lines import Line2D
        s = ArcSegment(0, 1, 0, 2 * pi, M=50)
        b = MFSBasis(s, N=50, tau=0.05)
        h = b.plot()
        self.assertEqual(len(h), 1)
        self.assertIsInstance(h[0], Line2D)
