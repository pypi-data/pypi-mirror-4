import logging
from math import pi

import numpy as np
import numpy.matlib

from scipy.special import hankel1

import matplotlib.pyplot as plt

from empirical.domain import (
    ArcSegment,
    Domain,
    )
from empirical.problem import (
    BVP,
    Scattering,
    )


def laplace_bc(z):
    r = np.abs(z)
    th = np.arctan2(z.imag, z.real)
    return np.power(r, 10) * np.cos(10 * th)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    print('Solving MFS scattering problems for convergence studies.')
    print('Converging circular boundary, Laplace solution:')
    boundary = ArcSegment(0+0j, 1.0, 0, 2 * pi, M=5, qtype='c')
    d = Domain(boundary, -1)
    boundary.set_bc(-1, 1, 0, lambda t: laplace_bc(boundary.Z(t)))
    d.add_mfs_basis(boundary, N=5, tau=-0.05)
    p = BVP(d)
    p.set_overall_wavenumber(0)
    p.solve()
    print('BVP.A: ', p.A)
    print('BVP.rhs: ', p.rhs)
    print('BVP.coeffs: ', p.coeffs)
    print('Residual norm:', p.bc_residual_norm())

    norms = dict()
    norms[5] = p.bc_residual_norm()

    for N in range(6, 201, 1):
        p.update_basis_n(N)
        p.update_quadrature_m(N)
        p.solve()
        norms[N] = p.bc_residual_norm()

    for N, norm in norms.items():
        print(N, norm)

    plt.figure('Boundary norms')
    plt.plot(list(norms.keys()), np.log10(list(norms.values())), '.-')
    plt.figure('Domain plot')
    d.plot()
    plt.show()

    print('Converging circular boundary, Helmholtz solution:')
    boundary = ArcSegment(0+0j, 1.0, 0, 2 * pi, M=5, qtype='c')
    d = Domain([], [], boundary, 1)
    boundary.set_bc(1, 1, 0, lambda t: laplace_bc(boundary.Z(t)))
    d.add_mfs_basis(boundary, N=5, tau=0.05)
    p = Scattering(d, [])
    p.set_overall_wavenumber(100)
    p.set_incident_planewave(pi / 6)
    p.solve()
    print('BVP.A: ', p.A)
    print('BVP.rhs: ', p.rhs)
    print('BVP.coeffs: ', p.coeffs)
    print('Residual norm:', p.bc_residual_norm())

    norms = dict()
    norms[5] = p.bc_residual_norm()

    for N in range(5, 301, 1):
        p.update_basis_n(N)
        p.update_quadrature_m(N)
        p.solve(method='lu factor')
        norms[N] = p.bc_residual_norm()

    for N, norm in norms.items():
        print(N, norm)

    plt.figure('Boundary norms')
    plt.plot(list(norms.keys()), np.log10(list(norms.values())), '.')
    plt.figure('Domain plot')
    d.plot()
    plt.show()
