import logging
from math import pi
import unittest

import numpy as np

from empirical.domain import (
    ArcSegment,
    Domain,
    )
from empirical.basis import MFSBasis
from empirical.problem import Scattering


log = logging.getLogger(__name__)
        

class ScatteringTests(unittest.TestCase):

    def test_set_incident_planewave(self):
        s1 = ArcSegment(0, 1, 0, 2 * pi, M=50)
        s2 = ArcSegment(3-1j, 1, 0, 2 * pi, M=50)
        d = Domain([], [], [s1, s2], [1, 1])
        s1.set_bc(1, 1, 0)
        s2.set_bc(1, 1, 0)
        d.add_mfs_basis(s1, tau=0.05, N=40)
        d.add_mfs_basis(s2, tau=0.05, N=30)
        p = Scattering(d, [])

        self.assertRaises(ValueError, p.set_incident_planewave, pi / 6)

        p.set_overall_wavenumber(30)
        p.set_incident_planewave(pi / 6)

        self.assertTrue(callable(s1.f))
        self.assertTrue(callable(s2.f))

        f1 = s1.f(s1.t)
        f2 = s2.f(s2.t)

        self.assertFalse(np.all(f1 == 0))
        self.assertFalse(np.all(f2 == 0))

        # Now test that the 'metallic' (not air) domains have a BC of 0.
        s1 = ArcSegment(0, 1, 0, 2 * pi, M=50)
        s2 = ArcSegment(3-1j, 1, 0, 2 * pi, M=50)
        s3 = ArcSegment(0, 1, 0, 2 * pi, M=50)
        s4 = ArcSegment(3-1j, 1, 0, 2 * pi, M=50)
        d1 = Domain([], [], [s1, s2], [1, 1])
        d2 = Domain([s3, s4], [-1, -1])
        s1.set_bc(1, 1, 0)
        s2.set_bc(1, 1, 0)
        s3.set_bc(-1, 1, 0)
        s4.set_bc(-1, 1, 0)
        d1.add_mfs_basis(s1, tau=0.05, N=40)
        d1.add_mfs_basis(s2, tau=0.05, N=30)
        d2.add_mfs_basis(s3, tau=-0.05, N=40)
        d2.add_mfs_basis(s4, tau=-0.05, N=30)
        d2.refractive_index = 3.5
        p = Scattering(d1, d2)

        self.assertRaises(ValueError, p.set_incident_planewave, pi / 6)

        p.set_overall_wavenumber(30)
        p.set_incident_planewave(pi / 6)

        self.assertTrue(callable(s1.f))
        self.assertTrue(callable(s2.f))
        self.assertTrue(callable(s3.f))
        self.assertTrue(callable(s4.f))

        f1 = s1.f(s1.t)
        f2 = s2.f(s2.t)
        f3 = s3.f(s3.t)
        f4 = s4.f(s4.t)

        self.assertFalse(np.all(f1 == 0))
        self.assertFalse(np.all(f2 == 0))
        self.assertTrue(np.all(f3 == 0))
        self.assertTrue(np.all(f4 == 0))
