__all__ = [
    "MFSBasis",
    ]


import logging
from math import (
    ceil,
    pi,
    )

import numpy as np
import numpy.linalg
import numpy.matlib

from scipy.special import hankel1

import empirical.domain


log = logging.getLogger(__name__)


class MFSBasis:

    """Represents a basis set using the method of fundamental solutions.

    An MFSBasis object is defined by several key elements:
    * `self.N` - The number of charge points that should be used. To change
                 this value, `update_n()` should be called.
    * `self.q` - A numpy array of the charge points, stored as x + y j.
    * `self.real_only` - Whether to use only the real value of the fundamental
      solution to compute matrix values.
    * `self.n_multiplier` - This can be used to scale the value of `N` passed
      to `update_n()`.
    * `self.Z` - If a function (or a `empirical.mps.domain.Segment`) was used to create

      this MFSBasis, then this is the function used to generate charge points.
      If this attribute is not present, then a list of charge points was passed
      to the constructor, and the number of points cannot be altered using
      `update_n()`.
    * `self.t` - If `self.Z` exists, then this is the array of parameter values
      used to generate `self.q`.
    """

    def __copy__(self):
        basis = MFSBasis(self.q)
        if hasattr(self, 'Z'):
            basis.Z = self.Z
        basis.N = self.N
        basis.q = self.q
        basis.t = self.t
        basis.n_multiplier = self.n_multiplier
        basis.real_only = self.real_only
        return basis

    def __deepcopy__(self, memo=None):
        if memo is None:
            memo = dict()
        basis = MFSBasis(self.q)
        if hasattr(self, 'Z'):
            basis.Z = self.Z
        basis.q = np.copy(self.q)
        basis.t = np.copy(self.t)
        basis.N = self.N
        basis.n_multiplier = self.n_multiplier
        basis.real_only = self.real_only
        return basis

    def __init__(self, points, N=20, real_only=False, tau=0,
                 n_multiplier=1):
        """Constructs an MFSBasis from a list of charge points.

        Parameters
        ==========
        * `points` - Can be any of the following:
          1. A `empirical.domain.Segment` object. The object's `Z` function
             is then used for `self.Z`.
          2. A callable function. It is assumed that this function takes
             parameters in the [0, 1] range. If `tau` is nonzero, then the
             values will be translated in the imaginary direction by `tau`.
          3. A numpy array of points, with points[:] = x + y j.
        * `N` - The number of charge points to create. If `points` is a numpy
          array, this value is ignored.
        * `tau` - If nonzero, then the parameter values passed to `self.Z` will
          be scaled by this amount in the complex direction.
        * `n_multiplier` - A scale to be applied when `update_n()` is called.
          Note that this also applies to initial point generation. This value
          does not have to be an integer.
        """
        self.real_only = real_only
        self.n_multiplier = n_multiplier

        if isinstance(points, empirical.domain.Segment):
            MFSBasis.__init__(self, points.Z, N=N, real_only=real_only,
                              tau=tau, n_multiplier=n_multiplier)
        elif isinstance(points, np.ndarray):
            self.q = points
            self.N = self.q.size
        elif callable(points):
            if tau == 0:
                self.Z = points
            else:
                self.Z = lambda t: points(t + complex(0, tau))
            self.update_n(N)

    def update_n(self, N):
        """Updates the number of charge points.

        If there is no generating function, then a warning is logged, and the
        points remain the same.
        """
        if not hasattr(self, 'Z'):
            log.warning('Cannot update number of basis functions without a' +
                        ' generating function!')
            return
        self.N = ceil(N * self.n_multiplier)
        self.t = np.linspace(1 / self.N, 1, self.N)
        self.q = self.Z(self.t)


    def matrix(self, k, points, normals=None, plain_function=True,
               normal_derivative=False, xy_derivative=False):
        """Generates matrices of the fundamental solutions evaluations.

        If `points` is a `empirical.domain.Segment`, then it's points and normals
        are used.

        If `normal_derivative` or `xy_derivative` is True, then the normals
        must be specified somehow.

        Results are returned as either a single matrix or, in the case of
        multiple evaluations, a tuple of matrices.

        The return value will have the following elements, in order, depending
        upon the boolean parameters:
        * `plain_function` - The fundamental solution.
        * `normal_derivative` - The normal derivative of the fundamental
          solution.
        * `xy_derivative` - The first derivative of the fundamental solution,
          in both the x and y directions.
        """
        if isinstance(points, empirical.domain.Segment):
            return self.matrix(k, points.x,
                               normals=points.nx,
                               plain_function=plain_function,
                               normal_derivative=normal_derivative,
                               xy_derivative=xy_derivative)
        N = self.N
        M = points.size
        d = (np.matlib.repmat(points.reshape(M, 1), 1, N) -
             np.matlib.repmat(self.q.reshape(1, N), M, 1))
        r = np.abs(d)

        if k != 0:
            kr = k * r

        results = []

        if plain_function:
            if k == 0:
                matrix_0 = -np.log(r) / (2 * pi)
            else:
                matrix_0 = 0.25j * hankel1(0, kr)
                if self.real_only:
                    matrix_0 = matrix_0.real
            results.append(matrix_0)

        if normal_derivative or xy_derivative:
            if k == 0:
                matrix_1 = -1 / (2 * pi * r)
            else:
                matrix_1 = -k * 0.25j * hankel1(1, kr)
                if self.real_only:
                    matrix_1 = matrix_1.real
            dr = d / r
            if normal_derivative:
                nx = np.matlib.repmat(normals.reshape(M, 1), 1, N)
                nx /= np.abs(nx)
                matrix_n = matrix_1 * (dr.real * nx.real + dr.imag * nx.imag)
                results.append(matrix_n)
            if xy_derivative:
                matrix_x = matrix_1 * dr.real
                matrix_y = matrix_1 * dr.imag
                results.append(matrix_x)
                results.append(matrix_y)

        if len(results) == 1:
            return results[0]
        return tuple(results)

    def __repr__(self):
        return ("<MFSBasis: N=%s, n_multiplier=%s, real_only=%s>" %
                (self.N, self.n_multiplier, self.real_only))

    def plot(self):
        import matplotlib.pyplot as plt
        plt.gcf()

        x = self.q.real
        y = self.q.imag
        if (np.abs(self.Z(0) - self.Z(1))) < 1e-15:
            z = self.Z(1)
            x = np.concatenate([x, [z.real]])
            y = np.concatenate([y, [z.imag]])
        h = plt.plot(x, y, '*')

        plt.axis('equal')

        return h
