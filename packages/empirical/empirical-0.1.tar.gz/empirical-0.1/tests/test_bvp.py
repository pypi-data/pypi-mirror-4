import logging
from math import (
    isinf,
    isnan,
    pi,
    )
import unittest

import numpy as np
import numpy.ma as ma

from scipy.special import hankel1

from empirical.domain import (
    Segment,
    ArcSegment,
    RadialSegment,
    Domain,
    )
from empirical.basis import MFSBasis
from empirical.problem import BVP
from empirical.quadrature import (
    clenshaw_curtis,
    gauss,
    periodic_trapezoid,
    trapezoid,
    )


log = logging.getLogger(__name__)


class BVPTests(unittest.TestCase):

    def test_constructor(self):
        s = ArcSegment(0, 1, 0, 2 * pi)
        d = Domain([], [], s, -1)
        bvp = BVP(d)
        self.assertIn(d, bvp.domains)
        self.assertIn(s, bvp.segments)

        s1 = ArcSegment(3-1j, 1, 0, 2 * pi)
        d = Domain([], [], [s, s1], [-1, -1])
        bvp = BVP(d)
        self.assertIn(d, bvp.domains)
        self.assertIn(s, bvp.segments)
        self.assertIn(s1, bvp.segments)

    def tt_update_n(self):
        s = ArcSegment(0, 1, 0, 2 * pi)
        s1 = ArcSegment(3-1j, 1, 0, 2 * pi)
        d = Domain([], [], [s, s1], [-1, -1])
        bvp = BVP(d)
        bvp.update_n(45)
        self.assertEqual(len(bvp.rhs), 0)
        self.assertEqual(s.N, 45)
        self.assertEqual(s1.N, 45)

    def test_set_overall_wavenumber(self):
        s1 = ArcSegment(0, 1, 0, 2 * pi, M=50)
        s2 = ArcSegment(3-1j, 1, 0, 2 * pi, M=50)
        d = Domain([], [], [s1, s2], [-1, -1])
        bvp = BVP(d)

        # Ensure we know the starting state:
        self.assertEqual(d.refractive_index, 1.0)

        bvp.set_overall_wavenumber(5.0)
        self.assertEqual(d.refractive_index, 1.0)
        self.assertEqual(d.k, 5.0)
        self.assertEqual(bvp.k, 5.0)

        d.refractive_index = 3.0
        bvp.set_overall_wavenumber(4.0)
        self.assertEqual(d.refractive_index, 3.0)
        self.assertEqual(d.k, 12.0)
        self.assertEqual(bvp.k, 4.0)

        self.assertRaises(ValueError, bvp.set_overall_wavenumber, float('nan'))
        d.refractive_index = float('nan')
        self.assertRaises(ValueError, bvp.set_overall_wavenumber, 5)

    def test_setup_basis_dofs(self):
        s1 = ArcSegment(0, 1, 0, 2 * pi)
        s2 = ArcSegment(3-1j, 1, 0, 2 * pi)
        d = Domain([], [], [s1, s2], [-1, -1])
        d.add_mfs_basis(s1, tau=0.05, N=40)
        d.add_mfs_basis(s2, tau=0.05, N=30)
        bvp = BVP(d)
        bvp.setup_basis_dofs()

        self.assertEqual(bvp.N, 70)
        for b in bvp.bases:
            self.assertIn(b, d.bases)
        for d in d.bases:
            self.assertIn(d, bvp.bases)

        self.assertEqual(len(bvp.basis_noff), 2)
        self.assertIn(0, bvp.basis_noff)
        self.assertTrue(30 in bvp.basis_noff or 40 in bvp.basis_noff)

    def test_fill_bc_matrix_dirichlet(self):
        s1 = ArcSegment(0, 1, 0, 2 * pi, M=50)
        s2 = ArcSegment(3-1j, 1, 0, 2 * pi, M=50)
        d = Domain([], [], [s1, s2], [1, 1])
        s1.set_bc(1, 1, 0)
        s2.set_bc(1, 1, 0)
        d.k = 1
        d.add_mfs_basis(s1, tau=0.05, N=40)
        d.add_mfs_basis(s2, tau=0.05, N=30)
        bvp = BVP(d)
        bvp.fill_bc_matrix()

        self.assertEqual(bvp.sqrt_weights.size, 100)
        self.assertEqual(bvp.N, 70)
        self.assertEqual(bvp.A.shape, (100, 70))

        x = np.concatenate([s.x.flatten() for s in bvp.segments])
        w = np.sqrt(np.concatenate([s.w.flatten() for s in bvp.segments]))
        q = np.concatenate([b.q.flatten() for b in bvp.bases])
        for i in range(100):
            for j in range(70):
                dist = np.abs(x[i] - q[j])
                val = 0.25j * hankel1(0, dist)
                self.assertAlmostEqual(bvp.A[i, j], w[i] * val, places=14)

    def test_fill_bc_matrix_neumann(self):
        s1 = ArcSegment(0, 1, 0, 2 * pi, M=50)
        s2 = ArcSegment(3-1j, 1, 0, 2 * pi, M=50)
        d = Domain([], [], [s1, s2], [1, 1])
        s1.set_bc(1, 0, 1)
        s2.set_bc(1, 0, 1)
        d.k = 3
        d.add_mfs_basis(s1, tau=0.05, N=40)
        d.add_mfs_basis(s2, tau=0.05, N=30)
        bvp = BVP(d)
        bvp.fill_bc_matrix()

        self.assertEqual(bvp.sqrt_weights.size, 100)
        self.assertEqual(bvp.N, 70)
        self.assertEqual(bvp.A.shape, (100, 70))

        x = np.concatenate([s.x.flatten() for s in bvp.segments])
        w = np.sqrt(np.concatenate([s.w.flatten() for s in bvp.segments]))
        nx = np.concatenate([s.nx.flatten() for s in bvp.segments])
        q = np.concatenate([b.q.flatten() for b in bvp.bases])
        for i in range(100):
            norm = nx[i] / np.abs(nx[i])
            for j in range(70):
                d = x[i] - q[j]
                r = np.abs(d)
                dr = d / r
                H1 = -3 * 0.25j * hankel1(1, 3 * r)
                val = H1 * (dr.real * norm.real + dr.imag * norm.imag)
                self.assertAlmostEqual(bvp.A[i, j], w[i] * val, places=14)

    def test_fill_bc_matrix_robin(self):
        s1 = ArcSegment(0, 1, 0, 2 * pi, M=50)
        s2 = ArcSegment(3-1j, 1, 0, 2 * pi, M=50)
        d = Domain([], [], [s1, s2], [1, 1])
        s1.set_bc(1, 0.3, 0.5)
        s2.set_bc(1, 0.3, 0.5)
        d.k = 2
        d.add_mfs_basis(s1, tau=0.05, N=40)
        d.add_mfs_basis(s2, tau=0.05, N=30)
        bvp = BVP(d)
        bvp.fill_bc_matrix()

        self.assertEqual(bvp.sqrt_weights.size, 100)
        self.assertEqual(bvp.N, 70)
        self.assertEqual(bvp.A.shape, (100, 70))

        x = np.concatenate([s.x.flatten() for s in bvp.segments])
        w = np.sqrt(np.concatenate([s.w.flatten() for s in bvp.segments]))
        nx = np.concatenate([s.nx.flatten() for s in bvp.segments])
        q = np.concatenate([b.q.flatten() for b in bvp.bases])
        for i in range(100):
            norm = nx[i] / np.abs(nx[i])
            for j in range(70):
                d = x[i] - q[j]
                r = np.abs(d)
                dr = d / r
                h0 = 0.3 * 0.25j * hankel1(0, 2 * r)
                h1 = 0.5 * -2 * 0.25j * hankel1(1, 2 * r)
                val = h0 + h1 * (d+r.real * norm.real + dr.imag * norm.imag)
                self.assertAlmostEqual(bvp.A[i, j], w[i] * val, places=14)

    def test_fill_rhs(self):
        s1 = ArcSegment(0, 1, 0, 2 * pi, M=50)
        s2 = ArcSegment(3-1j, 1, 0, 2 * pi, M=50)
        d = Domain([], [], [s1, s2], [1, 1])
        s1.set_bc(1, 1, 0)
        s2.set_bc(1, 1, 0, lambda t: np.ones(t.size))
        d.add_mfs_basis(s1, tau=0.05, N=40)
        d.add_mfs_basis(s2, tau=0.05, N=30)
        bvp = BVP(d)
        bvp.fill_rhs()

        self.assertEqual(ma.masked_equal(bvp.rhs, 0).count(), 50)
        self.assertEqual(ma.masked_not_equal(bvp.rhs, 0).count(), 50)

    def test_solve(self):
        s1 = ArcSegment(0, 1, 0, 2 * pi, M=50)
        s2 = ArcSegment(3-1j, 1, 0, 2 * pi, M=50)
        d = Domain([], [], [s1, s2], [1, 1])
        s1.set_bc(1, 1, 0)
        s2.set_bc(1, 1, 0)
        d.add_mfs_basis(s1, tau=0.05, N=40)
        d.add_mfs_basis(s2, tau=0.05, N=30)
        d.k = 3
        bvp = BVP(d)
        coeffs = bvp.solve()

        self.assertTrue(np.all(coeffs == bvp.coeffs))
        self.assertEqual(coeffs.size, 70)
