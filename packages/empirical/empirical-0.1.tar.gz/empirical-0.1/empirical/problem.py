__all__ = [
    "BVP",
    "Problem",
    "Scattering",
    ]


import copy
import logging
from math import (
    isnan,
    )

import numpy as np
import numpy.matlib
import numpy.ma

import scipy.linalg as la
from scipy.special import hankel1

import empirical.domain


log = logging.getLogger(__name__)


class Problem:

    def x(self):
        x = []
        for s in self.segments:
            x += [s.x]
        return np.concatenate(x)

    def fill_quadrature_weights(self):
        weights = []
        for s in self.segments:
            weights += [np.sqrt(s.w)]
        weights = np.concatenate(weights)
        self.sqrt_weights = weights.reshape((weights.size, 1))

    def setup_basis_dofs(self):
        self.bases = []
        for d in self.domains:
            for b in d.bases:
                if b not in self.bases:
                    self.bases += [b]
        self.N = 0
        self.basis_noff = np.zeros(len(self.bases), dtype='int')
        for i in range(len(self.bases)):
            self.basis_noff[i] = self.N
            self.N += self.bases[i].N
        if self.N == 0:
            log.warning('No basis sets in the problem!')
        return self.N

    def fill_bc_matrix(self, **kwargs):
        if (not hasattr(self, 'N') or
            not hasattr(self, 'basis_noff') or
            self.N is None or
            self.basis_noff is None):
            self.setup_basis_dofs()

        if (not hasattr(self, 'sqrt_weights') or self.sqrt_weights is None):
            self.fill_quadrature_weights()

        A = np.asmatrix(np.zeros((self.sqrt_weights.size, self.N),
                                 dtype='complex'))
        m = 0
        for s in self.segments:
            if s.bc_side == 1:
                d = s.dom_pos_side
            else:
                d = s.dom_neg_side
            # Set up for a block copy. The block is MxN, where
            # M = the number of quadrature points (from the segments)
            # N = the number of collocation points (from the bases)
            # There will be a separate block calculation for each combination
            # of segment and basis function. If a particular basis does not
            # apply to a given segment, then that block remains 0.
            mend = m + s.x.size
            for i in range(len(self.bases)):
                b = self.bases[i]
                if b in d.bases:
                    n0 = self.basis_noff[i]
                    n1 = n0 + b.N
                    # Get the block matrix values from the basis function:
                    if callable(s.a):
                        coeff_a = s.a(**kwargs)
                    else:
                        coeff_a = s.a
                    if callable(s.b):
                        coeff_b = s.b(**kwargs)
                    else:
                        coeff_b = s.b
                    if np.all([coeff_b == 0]):
                        Ablock = coeff_a * b.matrix(d.k, s)
                    elif np.all([coeff_a == 0]):
                        Ablock = coeff_b * b.matrix(d.k, s,
                                                    plain_function=False,
                                                    normal_derivative=True)
                    else:
                        Ablock, Anblock = b.matrix(d.k, s,
                                                   normal_derivative=True)
                        Ablock = coeff_a * Ablock + coeff_b * Anblock
                    weights = np.matlib.repmat(self.sqrt_weights[m:mend],
                                               1, b.N)
                    np.multiply(Ablock, weights, A[m:mend, n0:n1])
            m += s.x.size
        self.A = A

    def point_solution(self, points):
        if not hasattr(self, 'coeffs'):
            raise ValueError('No coefficients, must solve first!')

        di = float('nan') * np.empty(points.size)
        u = float('nan') * np.empty(points.size, dtype='complex')
        for n in range(len(self.domains)):
            d = self.domains[n]
            ii = d.inside(points)
            if not np.any(ii):
                continue
            di[ii] = n
            u[ii] = 0
            for i in range(len(self.bases)):
                b = self.bases[i]
                n0 = self.basis_noff[i]
                n1 = n0 + b.N
                if b in d.bases:
                    coeff = self.coeffs[n0:n1]
                    Ad = b.matrix(self.k, points[ii])
                    u[ii] += (Ad * coeff).flat
        return (u, di)

    def grid_bounding_box(self):
        bounding_box = [float('inf'), float('-inf'),
                        float('inf'), float('-inf')]
        for d in self.domains:
            bb = d.bounding_box()
            bounding_box[0] = min(bounding_box[0], bb[0])
            bounding_box[1] = max(bounding_box[1], bb[1])
            bounding_box[2] = min(bounding_box[2], bb[2])
            bounding_box[3] = max(bounding_box[3], bb[3])
        return bounding_box

    def grid_solution(self, dx, dy, bounding_box=None):
        if bounding_box is None:
            bb = self.grid_bounding_box()
        else:
            bb = bounding_box
        xx, yy = np.meshgrid(np.arange(bb[0], bb[1], dx),
                             np.arange(bb[2], bb[3], dy))
        zz = xx.reshape((xx.size,)) + 1j * yy.reshape((yy.size,))
        u, di = self.point_solution(zz)
        u = u.reshape(xx.shape)
        di = di.reshape(xx.shape)
        return (u, xx, yy, di)

    def set_overall_wavenumber(self, k):
        if isnan(k):
            raise ValueError('k must be a number!')
        self.k = k
        for d in self.domains:
            if isnan(d.refractive_index):
                raise ValueError('Each domain index must be a number!')
            d.k = d.refractive_index * k
            for b in d.bases:
                b.k = d.k

    def update_basis_n(self, N):
        for d in self.domains:
            for b in d.bases:
                b.update_n(N)
        # Signal the need for a recalculation:
        self.basis_noff = None
        self.N = None
        self.A = None

    def update_quadrature_m(self, M):
        for d in self.domains:
            for s in d.segments:
                s.recalc_quadrature(M=M)
        # Signal the need for a recalculation:
        self.M = None
        self.A = None


class BVP(Problem):

    def __copy__(self):
        bvp = BVP(self.domains)
        for attr in ['k', 'A', 'M', 'N', 'basis_noff', 'sqrt_weights',
                     'bases', 'rhs', 'coeffs']:
            if hasattr(self, attr):
                a = getattr(self, attr)
                setattr(bvp, attr, a)
        return bvp

    def __deepcopy__(self, memo=None):
        if memo is None:
            memo = dict()

        doms = [copy.deepcopy(d, memo) for d in self.domains]
        bvp = BVP(doms)
        for attr in ['k', 'A', 'M', 'N', 'basis_noff', 'sqrt_weights',
                     'bases', 'rhs', 'coeffs']:
            if hasattr(self, attr):
                a = getattr(self, attr)
                setattr(bvp, attr, copy.deepcopy(a, memo))
        return bvp

    def __init__(self, domains):
        self.segments = []
        if isinstance(domains, empirical.domain.Domain):
            self.domains = [domains]
            for s in domains.segments:
                if s not in self.segments:
                    self.segments += [s]
        else:
            self.domains = domains.copy()
            for d in domains:
                for s in d.segments:
                    if s not in self.segments:
                        self.segments += [s]

    def fill_rhs(self, **params):
        self.fill_quadrature_weights()
        rhs = []
        for s in self.segments:
            if callable(s.f):
                f = s.f(s.t)
            else:
                f = s.f
            rhs += [f.reshape(s.t.size)]
        rhs = np.concatenate(rhs)
        rhs = rhs.reshape((rhs.size, 1))
        self.rhs = np.multiply(rhs, self.sqrt_weights)
        return self.rhs

    def linsolve(self, method='least squares', solve_func=None, **kwargs):
        """Solve the system and return the coefficient vector result.

        The coefficient vector is not stored internally when this method is
        used. Use `solve_coeffs` to call setup functions and store the result
        automatically.

        Methods
        =======
        * 'least squares' - Uses a least squares algorithm.
        * 'lu factor' - Uses an LU factorization. The BC matrix must be square.
        * 'user function' - Uses the function given by `solve_func`.

        `solve_func` is called like: solve_func(A, rhs, **kwargs), where A is
        the BC matrix and rhs is the right-hand side vector.
        """
        A = self.A
        rhs = self.rhs

        if method == 'lu factor':
            log.info('Solving system using LU factorization.')
            if A.shape[0] != A.shape[1]:
                raise ValueError('The BC matrix must be square! shape: %s' %
                                 A.shape)
            coeff = la.lu_solve(la.lu_factor(A), rhs)
        elif method == 'least squares':
            log.info('Solving system using least squares.')
            coeff, res, rank, s = la.lstsq(A, rhs)
            log.info('Residues: %s', res)
            log.info('Matrix shape: %s, effective rank: %d', A.shape, rank)
        elif method == 'user function':
            coeff = solve_func(A, rhs, **kwargs)
        else:
            raise ValueError('Unknown method %s.' % method)

        return coeff

    def solve(self, **kwargs):
        """Solves for the coefficient vector.

        If the quadrature weights are not set up, calls `fill_quad_weights`.
        If the right hand side vector is not set up, calls `fill_rhs`.
        Then calls `setup_basis_dofs` and `fill_bc_matrix`, followed by
        `linsolve(**kwargs)`, storing the result as `self.coeffs`.

        The coefficient vector is returned.
        """
        self.fill_quadrature_weights()
        self.fill_rhs()
        self.setup_basis_dofs()
        self.fill_bc_matrix()

        self.coeffs = self.linsolve(**kwargs)
        # Reshape to allow for matrix multiplication:
        self.coeffs = np.asmatrix(self.coeffs.reshape((self.coeffs.size, 1)))
        return self.coeffs

    def bc_residual_norm(self):
        """Calculates the 2-norm of the residual, (A * coeffs) - rhs."""
        y = np.dot(self.A, self.coeffs)
        return la.norm(y - self.rhs.reshape((self.sqrt_weights.size, 1)), 2)


class Scattering(BVP):

    def __copy__(self):
        air_doms = []
        doms = []
        for d in self.domains:
            if d.is_air == 1:
                air_doms += [d]
            else:
                doms += [d]
        scatt = Scattering(air_doms, doms)
        for attr in ['incident_angle', 'incident_type', 'k', 'A', 'M', 'N',
                     'basis_noff', 'sqrt_weights', 'bases', 'rhs', 'coeffs',
                     'ui', 'uix', 'uiy']:
            if hasattr(self, attr):
                a = getattr(self, attr)
                setattr(scatt, attr, a)

        return scatt

    def __deepcopy__(self, memo=None):
        if memo is None:
            memo = dict()

        air_doms = []
        doms = []
        for d in self.domains:
            if d.is_air == 1:
                air_doms += [d]
            else:
                doms += [d]
        scatt = Scattering(air_doms, doms)
        for attr in ['incident_angle', 'incident_type', 'k', 'A', 'M', 'N',
                     'basis_noff', 'sqrt_weights', 'bases', 'rhs', 'coeffs',
                     'ui', 'uix', 'uiy']:
            if hasattr(self, attr):
                a = getattr(self, attr)
                setattr(scatt, attr, copy.deepcopy(a, memo))

        return scatt

    def __init__(self, air_domains, domains):
        if isinstance(air_domains, empirical.domain.Domain):
            air_domains = [air_domains]
        if isinstance(domains, empirical.domain.Domain):
            domains = [domains]
        if len(air_domains) == 0:
            raise ValueError('Must have at least one air domain!')

        BVP.__init__(self, air_domains + domains)
        for d in air_domains:
            d.is_air = 1
        for d in domains:
            d.is_air = 0

        n = air_domains[0].refractive_index
        for d in air_domains:
            if n != d.refractive_index:
                log.warning('All air domains need the same refractive index!')

    def set_incident_planewave(self, angle):
        """Sets up the inhomogenous boundary conditions for a planewave.

        The angle given must be in [0, 2 * pi], and the wavenumber must
        already be set.
        """
        if not hasattr(self, 'k') or isnan(self.k):
            raise ValueError('Set up wavenumber before the incident wave')

        self.incident_angle = angle
        self.incident_type = 'planewave'
        kvec = self.k * np.exp(complex(0, angle))
        def _ui(x):
            return np.exp(1j * (kvec.conjugate() * x).real)

        def _uix(x):
            return 1j * kvec.real * _ui(x)

        def _uiy(x):
            return 1j * kvec.imag * _ui(x)

        self.set_incident_wave(_ui, _uix, _uiy)

    def set_incident_point_source(self, point):
        if not hasattr(self, 'k') or isnan(self.k):
            raise ValueError('Set up wavenumber before the incident wave')

        def _ui(x):
            return 0.25j * hankel1(0, self.k * np.abs(x - point))

        def _uix(x):
            d = x - point
            r = np.abs(d)
            return -0.25j * self.k * d.real / r * hankel1(1, self.k * r)

        def _uiy(x):
            d = x - point
            r = np.abs(d)
            return -0.25j * self.k * d.imag / r * hankel1(1, self.k * r)

        self.set_incident_wave(_ui, _uix, _uiy)

    def set_incident_wave(self, ui, uix, uiy):
        if not hasattr(self, 'k') or isnan(self.k):
            raise ValueError('Set up wavenumber before the incident wave')

        self.ui = ui
        self.uix = uix
        self.uiy = uiy

        for s in self.segments:
            if s.bc_side == 1:
                d = s.dom_pos_side
            else:
                d = s.dom_neg_side
            if d.is_air == 1:
                # Air-to-metallic boundary
                # Optimize calling when Dirichlet or Neumann BCs are present
                def _f(t):
                    z = s.Z(t)
                    zn = s.Zn(t)
                    return (-s.a * self.ui(z) +
                             s.b * (self.uix(z) * zn.real +
                                    self.uiy(z) * zn.imag))

                s.f = _f
            else:
                # Internal-to-metallic boundary
                # f = homogenous BCs
                s.f = lambda t: np.zeros_like(t)

    def point_incidient_wave(self, points):
        di = np.empty(points.size)
        di[:] = float('nan')
        u = np.zeros(points.size, dtype='complex')
        for n in range(len(self.domains)):
            d = self.domains[n]
            ii = d.inside(points)
            di[ii] = n
            u[ii] = self.ui(points[ii])
        return (u, di)

    def grid_incident_wave(self, dx=0.03, dy=0.03, bb=None):
        if bb is None:
            bb = self.grid_bounding_box()
        xx, yy = np.meshgrid(np.arange(bb[0], bb[1], dx),
                             np.arange(bb[2], bb[3], dy))
        zz = xx.reshape(xx.size) + 1j * yy.reshape(yy.size)
        u, di = self.point_incidient_wave(zz)
        u = u.reshape(xx.shape)
        di = di.reshape(xx.shape)
        return (u, xx, yy, di)

    def show_three_fields(self, imag=False, dx=0.03, dy=0.03, bb=None):
        import matplotlib.pyplot as plt
        import matplotlib.cm as cm
        hfac = 0.95
        vfac = 0.9
        hgap = 0.5 * (1 - hfac)
        vgap = 0.4 * (1 - vfac)

        if bb is None:
            bb = self.grid_bounding_box()

        # Matplotlib's y-direction is reversed for us.
        # Switch the direction of our y-points in the grid by swapping
        # bounding box y-values and negating the dy step.
        bb = [bb[0], bb[1], bb[3], bb[2]]
        dy = -dy

        plt.axes([hgap / 3, vgap, hfac / 3, vfac])
        ui, xx, yy, di = self.grid_incident_wave(dx, dy, bb)
        us, xx, yy, di = self.grid_solution(dx, dy, bb)
        ut = ui + us
        if imag:
            plt.imshow(ui.imag, cmap=cm.jet, aspect=1)
            plt.title('Im[u_i]')
        else:
            plt.imshow(ui.real, cmap=cm.jet, aspect=1)
            plt.title('Re[u_i]')
        plt.colorbar()
        plt.hold(True)

        plt.axes([(hgap + 1) / 3, vgap, hfac / 3, vfac])
        if imag:
            plt.imshow(us.imag, cmap=cm.jet)
            plt.title('Im[u_s]')
        else:
            plt.imshow(us.real, cmap=cm.jet)
            plt.title('Re[u_s]')
        plt.colorbar()
        plt.hold(True)

        plt.axes([(hgap + 2) / 3, vgap, hfac / 3, vfac])
        if imag:
            plt.imshow(ut.imag, cmap=cm.jet, aspect=1)
            plt.title('Im[u_i + u_s]')
        else:
            plt.imshow(ut.real, cmap=cm.jet, aspect=1)
            plt.title('Re[u_i + u_s]')
        plt.colorbar()
        plt.hold(True)
