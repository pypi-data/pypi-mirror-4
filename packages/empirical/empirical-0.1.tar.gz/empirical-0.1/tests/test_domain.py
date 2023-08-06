import logging
from math import (
    isinf,
    isnan,
    pi,
    )
import unittest

import numpy as np

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


class DomainTest(unittest.TestCase):

    def setUp(self):
        self.seg = ArcSegment(0, 1, 0, 2 * pi)
        self.d = Domain([], [], self.seg, -1)

    def test_external_constructor(self):
        d = Domain()
        self.assertTrue(d.exterior)
        self.assertTrue(isinf(d.area))
        self.assertTrue(isnan(d.k))
        self.assertEqual(d.refractive_index, 1)
        self.assertEqual(d.perimeter, 0)
        self.assertEqual(len(d.bases), 0)
        self.assertEqual(len(d.segments), 0)
        self.assertEqual(len(d.senses), 0)

        d = Domain([], [])
        self.assertTrue(d.exterior)
        self.assertTrue(isinf(d.area))
        self.assertTrue(isnan(d.k))
        self.assertEqual(d.refractive_index, 1)
        self.assertEqual(d.perimeter, 0)
        self.assertEqual(len(d.bases), 0)
        self.assertEqual(len(d.segments), 0)
        self.assertEqual(len(d.senses), 0)

        seg = self.seg
        d = self.d
        self.assertTrue(d.exterior)
        self.assertTrue(isinf(d.area))
        self.assertTrue(isnan(d.k))
        self.assertEqual(d.refractive_index, 1)
        self.assertNotEqual(d.perimeter, 0)
        self.assertEqual(len(d.bases), 0)
        self.assertEqual(len(d.segments), 1)
        self.assertEqual(len(d.senses), 1)

    def test_add_basis(self):
        seg = self.seg
        d = self.d
        d.add_mfs_basis(seg, N=200, tau=0.05)
        self.assertEqual(len(d.bases), 1)
        basis = d.bases[0]
        self.assertIsInstance(basis, MFSBasis)
        self.assertFalse(np.any(d.inside(basis.q)))

    def test_inside(self):
        seg = self.seg
        d = self.d
        self.assertEqual(d.inside(np.array([[0+0j]])).size, 1)
        self.assertFalse(np.any(d.inside(np.array([[0+0j]]))))
        self.assertTrue(np.any(d.inside(np.array([[1.5+0j]]))))
        self.assertTrue(np.any(d.inside(np.array([[0+1.5j]]))))
        self.assertTrue(np.any(d.inside(np.array([[1.5+1.5j]]))))
        self.assertTrue(np.any(d.inside(np.array([[0.8+0.8j]]))))

    def test_x(self):
        s1 = ArcSegment(0, 1, 0, 2 * pi, M=50)
        s2 = ArcSegment(3-1j, 1, 0, 2 * pi, M=50)
        d = Domain([], [], [s1, s2], [-1, -1])

        dx = d.x()

        for x in dx:
            self.assertTrue(x in s1.x or x in s2.x)

        for x in s1.x:
            self.assertTrue(x in dx)
        for x in s2.x:
            self.assertTrue(x in dx)

    def test_internal_constructor(self):
        s = ArcSegment(0, 1, 0, 2 * pi)
        d = Domain(s, -1)
        self.assertFalse(d.exterior)
        self.assertEqual(d.area, pi)
        self.assertTrue(isnan(d.k))
        self.assertEqual(d.refractive_index, 1)
        self.assertEqual(d.perimeter, 2 * pi)
        self.assertEqual(len(d.bases), 0)
        self.assertEqual(len(d.segments), 1)
        self.assertEqual(len(d.senses), 1)
        self.assertIs(d.segments[0], s)
        self.assertEqual(d.senses[0], -1)

        s2 = ArcSegment(0, 2, 0, 2 * pi)
        d = Domain(s2, -1, s, 1)
        self.assertFalse(d.exterior)
        self.assertEqual(d.area, pi * 4 - pi)
        self.assertTrue(isnan(d.k))
        self.assertEqual(d.refractive_index, 1)
        self.assertEqual(d.perimeter, (2 * pi * 2) + (2 * pi))
        self.assertEqual(len(d.bases), 0)
        self.assertEqual(len(d.segments), 2)
        self.assertEqual(len(d.senses), 2)
        self.assertIs(d.segments[0], s2)
        self.assertEqual(d.senses[0], -1)
        self.assertIs(d.segments[1], s)
        self.assertEqual(d.senses[1], 1)
