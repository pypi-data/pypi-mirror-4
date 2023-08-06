import logging
from math import pi

import numpy as np
import numpy.matlib

from scipy.special import hankel1

import matplotlib.pyplot as plt

from empirical.domain import (
    LineSegment,
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
    print('Solving MFS scattering problems for analytic continuation studies.')
    print('Circular boundary, Laplace solution, circular charge points:')
    boundary = ArcSegment(0+0j, 1.0, 0, 2 * pi, M=100, qtype='c')
    d = Domain(boundary, -1)
    boundary.set_bc(-1, 1, 0, lambda t: laplace_bc(boundary.Z(t)))
    d.add_mfs_basis(boundary, N=100, tau=-0.05)
    p = BVP(d)
    p.set_overall_wavenumber(0)
    p.solve()
    print('Residual norm:', p.bc_residual_norm())

    print('Circular boundary, Laplace solution, square charge points:')
    boundary = ArcSegment(0+0j, 1.0, 0, 2 * pi, M=100, qtype='c')
    d = Domain(boundary, -1)
    boundary.set_bc(-1, 1, 0, lambda t: laplace_bc(boundary.Z(t)))
    charges_bot   = LineSegment(-1.5-1.5j, 1.5-1.5j, M=25)
    charges_right = LineSegment(1.5-1.5j, 1.5+1.5j, M=25)
    charges_top   = LineSegment(1.5+1.5j, -1.5+1.5j, M=25)
    charges_left  = LineSegment(-1.5+1.5j, -1.5-1.5j, M=25)
    d.add_mfs_basis(charges_bot, N=25)
    d.add_mfs_basis(charges_right, N=25)
    d.add_mfs_basis(charges_top, N=25)
    d.add_mfs_basis(charges_left, N=25)
    p = BVP(d)
    p.set_overall_wavenumber(0)
    p.solve()
    print('Residual norm:', p.bc_residual_norm())

    print('Square boundary, Laplace solution, analytically continued charge points:')
    boundary_bot   = LineSegment(1-1j, -1-1j, M=25)
    boundary_right = LineSegment(1+1j, 1-1j, M=25)
    boundary_top   = LineSegment(-1+1j, 1+1j, M=25)
    boundary_left  = LineSegment(-1-1j, -1+1j, M=25)
    d = Domain([boundary_bot, boundary_right, boundary_top, boundary_left], [-1, -1, -1, -1])
    boundary_bot.set_bc(-1, 1, 0, lambda t: laplace_bc(boundary.Z(t)))
    boundary_right.set_bc(-1, 1, 0, lambda t: laplace_bc(boundary.Z(t)))
    boundary_top.set_bc(-1, 1, 0, lambda t: laplace_bc(boundary.Z(t)))
    boundary_left.set_bc(-1, 1, 0, lambda t: laplace_bc(boundary.Z(t)))
    d.add_mfs_basis(boundary_bot, N=25, tau=0.05)
    d.add_mfs_basis(boundary_right, N=25, tau=0.05)
    d.add_mfs_basis(boundary_top, N=25, tau=0.05)
    d.add_mfs_basis(boundary_left, N=25, tau=0.05)
    p = BVP(d)
    p.set_overall_wavenumber(0)
    p.solve()
    print('Residual norm:', p.bc_residual_norm())

    print('Square boundary, Laplace solution, square charge points:')
    boundary_bot   = LineSegment(-1-1j, 1-1j, M=25)
    boundary_right = LineSegment(1-1j, 1+1j, M=25)
    boundary_top   = LineSegment(1+1j, -1+1j, M=25)
    boundary_left  = LineSegment(-1+1j, -1-1j, M=25)
    d = Domain([boundary_bot, boundary_right, boundary_top, boundary_left], [-1, -1, -1, -1])
    boundary_bot.set_bc(-1, 1, 0, lambda t: laplace_bc(boundary.Z(t)))
    boundary_right.set_bc(-1, 1, 0, lambda t: laplace_bc(boundary.Z(t)))
    boundary_top.set_bc(-1, 1, 0, lambda t: laplace_bc(boundary.Z(t)))
    boundary_left.set_bc(-1, 1, 0, lambda t: laplace_bc(boundary.Z(t)))
    charges_bot   = LineSegment(-1.5-1.5j, 1.5-1.5j, M=25)
    charges_right = LineSegment(1.5-1.5j, 1.5+1.5j, M=25)
    charges_top   = LineSegment(1.5+1.5j, -1.5+1.5j, M=25)
    charges_left  = LineSegment(-1.5+1.5j, -1.5-1.5j, M=25)
    d.add_mfs_basis(charges_bot, N=25)
    d.add_mfs_basis(charges_right, N=25)
    d.add_mfs_basis(charges_top, N=25)
    d.add_mfs_basis(charges_left, N=25)
    p = BVP(d)
    p.set_overall_wavenumber(0)
    p.solve()
    print('Residual norm:', p.bc_residual_norm())
