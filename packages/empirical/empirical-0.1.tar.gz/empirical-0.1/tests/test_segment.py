from math import pi
import unittest

import numpy as np

from empirical.domain import (
    Segment,
    LineSegment,
    ArcSegment,
    RadialSegment,
    Domain,
    )
from empirical.quadrature import (
    clenshaw_curtis,
    gauss,
    periodic_trapezoid,
    trapezoid,
    )


class SegmentTest(unittest.TestCase):

    def test_constructor(self):
        Z = lambda t: np.exp(2j * pi * t)
        Zp = lambda t: 2j * pi * np.exp(2j * pi * t)
        seg = Segment(Z, Zp, 35, qtype='p')
        self.assertIs(seg.Z, Z)
        self.assertIs(seg.Zp, Zp)
        self.assertEqual(seg.M, 35)
        self.assertEqual(seg.qtype, 'p')
        self.assertIs(seg.quadrule, periodic_trapezoid)
        self.assertTrue(np.all(Z(np.linspace(0, 1, 100)) == seg.approxv))
        z, w = periodic_trapezoid(35)
        t = (1 + z) / 2.0
        self.assertTrue(np.all(t == seg.t))
        self.assertTrue(np.all(Z(t) == seg.x))
        dZdt = Zp(t)
        speed = np.abs(dZdt)
        self.assertTrue(np.all(speed == seg.speed))
        w *= speed / 2.0
        self.assertTrue(np.all(w == seg.w))
        nx = -1j * dZdt / speed
        self.assertTrue(np.all(nx == seg.nx))

        seg = Segment(Z, Zp, 35, qtype='t')
        self.assertEqual(seg.qtype, 't')
        self.assertIs(seg.quadrule, trapezoid)

        seg = Segment(Z, Zp, 35, qtype='c')
        self.assertEqual(seg.qtype, 'c')
        self.assertIs(seg.quadrule, clenshaw_curtis)

        seg = Segment(Z, Zp, 35, qtype='g')
        self.assertEqual(seg.qtype, 'g')
        self.assertIs(seg.quadrule, gauss)

        func = lambda N: (np.linspace(0, 2, N), np.ones(N) / N)
        seg = Segment(Z, Zp, 35, quadrule=func)
        self.assertIs(seg.quadrule, func)

        self.assertRaises(ValueError, Segment, Z, Zp, qtype='not a valid type')

    def test_recalc_quadrature(self):
        Z = lambda t: np.exp(2j * pi * t)
        Zp = lambda t: 2j * pi * np.exp(2j * pi * t)
        seg = Segment(Z, Zp, 20)

        seg.recalc_quadrature(35, qtype='p')
        self.assertEqual(seg.M, 35)
        self.assertEqual(seg.qtype, 'p')
        self.assertIs(seg.quadrule, periodic_trapezoid)

        seg.recalc_quadrature(200)
        self.assertEqual(seg.M, 200)
        self.assertEqual(seg.qtype, 'p')
        self.assertIs(seg.quadrule, periodic_trapezoid)

        seg.recalc_quadrature(20, qtype='t')
        self.assertEqual(seg.M, 20)
        self.assertEqual(seg.qtype, 't')
        self.assertIs(seg.quadrule, trapezoid)

        seg.recalc_quadrature(40, qtype='c')
        self.assertEqual(seg.M, 40)
        self.assertEqual(seg.qtype, 'c')
        self.assertIs(seg.quadrule, clenshaw_curtis)

        seg.recalc_quadrature(50, qtype='g')
        self.assertEqual(seg.M, 50)
        self.assertEqual(seg.qtype, 'g')
        self.assertIs(seg.quadrule, gauss)

        func = lambda N: (np.linspace(0, 2, N), np.ones(N) / N)
        seg.recalc_quadrature(55, quadrule=func)
        self.assertEqual(seg.M, 55)
        self.assertIsNone(seg.qtype)
        self.assertIs(seg.quadrule, func)

        self.assertRaises(ValueError, seg.recalc_quadrature, qtype='not a valid type')

    def test_set_bc(self):
        seg = ArcSegment(0, 1, 0, 2 * pi)
        d = Domain([], [], seg, 1)
        seg.set_bc(1, 1, 0)

        self.assertEqual(seg.a, 1)
        self.assertEqual(seg.b, 0)
        self.assertEqual(seg.bc_side, 1)
        self.assertEqual(seg.dom_pos_side, d)

        seg.set_bc(1, 0.3, 0.4)

        self.assertEqual(seg.a, 0.3)
        self.assertEqual(seg.b, 0.4)
        self.assertEqual(seg.bc_side, 1)
        self.assertEqual(seg.dom_pos_side, d)

        f = lambda t: np.ones(t.size)
        seg.set_bc(1, 1, 0, f)

        self.assertEqual(seg.a, 1)
        self.assertEqual(seg.b, 0)
        self.assertEqual(seg.bc_side, 1)
        self.assertEqual(seg.dom_pos_side, d)
        self.assertIs(f, seg.f)

        self.assertRaises(ValueError, seg.set_bc, -1, 1, 0)
        self.assertRaises(ValueError, seg.set_bc, -5, 1, 0)
        self.assertRaises(ValueError, seg.set_bc, 5, 1, 0)


    def test_bc_domains(self):
        seg = ArcSegment(0, 1, 0, 2 * pi)
        d = Domain(seg, -1)
        seg.set_bc(-1, 1, 0)

        self.assertEqual(seg.a, 1)
        self.assertEqual(seg.b, 0)
        self.assertEqual(seg.bc_side, -1)
        self.assertEqual(seg.dom_neg_side, d)

        s1 = ArcSegment(0, 1, 0, 2 * pi)
        s2 = ArcSegment(0, 2, 0, 2 * pi)
        d = Domain(s2, -1, s1, 1)
        s2.set_bc(-1, 1, 0)
        s1.set_bc(1, 1, 0)

        self.assertEqual(s1.a, 1)
        self.assertEqual(s1.b, 0)
        self.assertEqual(s1.bc_side, 1)
        self.assertEqual(s1.dom_pos_side, d)
        self.assertEqual(s2.a, 1)
        self.assertEqual(s2.b, 0)
        self.assertEqual(s2.bc_side, -1)
        self.assertEqual(s2.dom_neg_side, d)

        s1.set_bc(1, 3, 4)
        s2.set_bc(-1, 1, 2)

        self.assertEqual(s1.a, 3)
        self.assertEqual(s1.b, 4)
        self.assertEqual(s1.bc_side, 1)
        self.assertEqual(s1.dom_pos_side, d)
        self.assertEqual(s2.a, 1)
        self.assertEqual(s2.b, 2)
        self.assertEqual(s2.bc_side, -1)
        self.assertEqual(s2.dom_neg_side, d)

        f1 = lambda t: np.abs(t) * np.ones(t.size)
        f2 = lambda t: 0.5 * np.cos(np.abs(t))
        s1.set_bc(1, 1, 3, f1)
        s2.set_bc(-1, 2, 4, f2)

        self.assertEqual(s1.a, 1)
        self.assertEqual(s1.b, 3)
        self.assertIs(s1.f, f1)
        self.assertEqual(s1.bc_side, 1)
        self.assertEqual(s1.dom_pos_side, d)
        self.assertEqual(s2.a, 2)
        self.assertEqual(s2.b, 4)
        self.assertIs(s2.f, f2)
        self.assertEqual(s2.bc_side, -1)
        self.assertEqual(s2.dom_neg_side, d)

        self.assertRaises(ValueError, s1.set_bc, -1, 1, 0)
        self.assertRaises(ValueError, s2.set_bc, 1, 1, 0)


class RadialTest(unittest.TestCase):

    @staticmethod
    def r(t):
        return 1 + 0.3 * np.cos(3 * t)

    @staticmethod
    def rp(t):
        return -0.9 * np.sin(3 * t)

    def setUp(self):
        self.seg = RadialSegment(RadialTest.r, RadialTest.rp)

    def test_circle(self):
        # Not an efficient way to create a circle, but works to test.
        seg = RadialSegment(lambda t: 1, lambda t: 0)
        t = np.linspace(0, 1, 50)
        z_mag = np.abs(seg.Z(t))
        self.assertAlmostEqual(np.max(z_mag), 1, places=15)
        self.assertAlmostEqual(np.min(z_mag), 1, places=15)

        zp_mag = np.abs(seg.Zp(t))
        self.assertAlmostEqual(np.max(zp_mag), 2 * pi, places=14)
        self.assertAlmostEqual(np.min(zp_mag), 2 * pi, places=14)

    def test_quadrature(self):
        self.assertEqual(self.seg.quadrule, periodic_trapezoid)

    def test_z(self):
        t = np.linspace(0, 1, 50)
        z = self.seg.Z(t)
        zp = self.seg.Zp(t)
        r = RadialTest.r(t * 2 * pi)
        rp = RadialTest.rp(t * 2 * pi)
        d = 2 * pi * ((1j * z) + (np.exp(2j * pi * t) * rp))
        for i in range(len(t)):
            self.assertAlmostEqual(np.abs(z[i]), r[i], places=14)
            self.assertAlmostEqual(zp[i], d[i], places=14)


class LineTest(unittest.TestCase):

    def test_constructor(self):
        a = -0.5+0.3j
        b = 2-5j
        seg = LineSegment(a, b)
        self.assertAlmostEqual(seg.Z(0), a, places=14)
        self.assertAlmostEqual(seg.Z(1), b, places=14)
        dx = b - a
        for x in seg.x:
            self.assertTrue(abs(((x - b) / dx).imag) < 1e-14)


class CircleTest(unittest.TestCase):

    def setUp(self):
        self.seg = ArcSegment(0, 1, 0, 2 * pi)

    def test_Z(self):
        t = np.linspace(0, 1, 50)
        z = self.seg.Z(t)
        sin = np.sin(2 * pi * t)
        cos = np.cos(2 * pi * t)
        self.assertAlmostEqual(np.max(z.real - cos), 0, places=14)
        self.assertAlmostEqual(np.min(z.imag - sin), 0, places=14)

    def test_Zp(self):
        t = np.linspace(0, 1, 50)
        zp = self.seg.Zp(t)
        sin = 2 * pi * np.sin(2 * pi * t)
        cos = 2 * pi * np.cos(2 * pi * t)
        self.assertAlmostEqual(np.max(zp.real + sin), 0, places=14)
        self.assertAlmostEqual(np.min(zp.imag - cos), 0, places=14)

    def test_Zn(self):
        t = np.linspace(0, 1, 50)
        zn = self.seg.Zn(t)
        sin = np.sin(2 * pi * t)
        cos = np.cos(2 * pi * t)
        self.assertAlmostEqual(np.max(zn.real - cos), 0, places=14)
        self.assertAlmostEqual(np.min(zn.imag - sin), 0, places=14)

