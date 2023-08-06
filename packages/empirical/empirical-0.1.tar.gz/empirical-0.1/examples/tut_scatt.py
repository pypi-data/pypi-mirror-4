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
from empirical.problem import Scattering


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    print('Solving homogenous Dirichlet (sound-soft) scattering problem...')
    plt.figure('homogenous Dirichlet (sound-soft)')
    tref = RadialSegment(lambda q: 1 + 0.3 * np.cos(3 * q),
                         lambda q: -0.9 * np.sin(3 * q),
                         M=250)
    d = Domain([], [], tref, 1)
    tref.set_bc(1, 1, 0)
    d.add_mfs_basis(tref, N=200, tau=0.05)
    p = Scattering(d, [])
    p.set_overall_wavenumber(30)
    p.set_incident_planewave(pi / 6)
    p.solve()
    print('Residual norm:', p.bc_residual_norm())
    p.show_three_fields()

    print('Solving homogenous Neumann (sound-hard) scattering problem...')
    plt.figure('homogenous Neumann (sound-hard)')
    tref = RadialSegment(lambda q: 1 + 0.3 * np.cos(3 * q),
                         lambda q: -0.9 * np.sin(3 * q),
                         M=250)
    d = Domain([], [], tref, 1)
    tref.set_bc(1, 0, 1)
    d.add_mfs_basis(tref, N=200, tau=0.05)
    p = Scattering(d, [])
    p.set_overall_wavenumber(30)
    p.set_incident_planewave(pi / 6)
    p.solve()
    print('Residual norm:', p.bc_residual_norm())
    p.show_three_fields()

    print('Solving homogenous Robin (impedance) scattering problem...')
    plt.figure('homogenous Robin (impedance)')
    tref = RadialSegment(lambda q: 1 + 0.3 * np.cos(3 * q),
                         lambda q: -0.9 * np.sin(3 * q),
                         M=250)
    d = Domain([], [], tref, 1)
    tref.set_bc(1, 30j, 1)
    d.add_mfs_basis(tref, N=200, tau=0.05)
    p = Scattering(d, [])
    p.set_overall_wavenumber(30)
    p.set_incident_planewave(pi / 6)
    p.solve()
    print('Residual norm:', p.bc_residual_norm())
    p.show_three_fields()

    plt.show()
