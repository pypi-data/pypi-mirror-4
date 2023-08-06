import logging
from math import pi

import numpy as np
import numpy.matlib

from scipy.special import hankel1

import matplotlib.pyplot as plt

from empirical.domain import (
    RadialSegment,
    Domain,
    )
from empirical.emfs import EMFS
from empirical.problem import Scattering


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    print('Solving EMFS using the Helmholtz scattering problem as a base.')

    seg = RadialSegment(lambda q: 1 + 0.3 * np.cos(3 * q),
                        lambda q: -0.9 * np.sin(3 * q),
                        M=400)
    dom = Domain([], [], seg, 1)
    seg.set_bc(1, 5j, 1)
    dom.add_mfs_basis(seg, N=400, tau=0.05)
    prob = Scattering(dom, [])
    prob.set_overall_wavenumber(5)
    prob.set_incident_planewave(pi / 6)

    def solver(problem, k, theta):
        problem.segments[0].set_bc(1, complex(0, k), 1)
        problem.set_overall_wavenumber(k)
        problem.set_incident_planewave(theta)
        problem.solve()

    emfs = EMFS(prob, solver, [dict({'k': k, 'theta': theta * pi / 30})
                               for k in range(101)
                               for theta in range(11)])
    emfs.solve()
