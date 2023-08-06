__all__ = [
    "EMFS",
    ]

import copy
import logging

import numpy as np
import numpy.linalg


log = logging.getLogger(__name__)


class EMFS:
    """Class for computing empirical method of fundamental solutions.
    """

    def __init__(self, problem, solve_function, parameters_list,
                 first_parameter=None):
        """Creates an EMFS object out of the given problem.

        The given problem is cloned using the `copy.deepcopy` method for each
        new parameter set. It is then prepared for use using the given
        `solve_function`, which takes the cloned problem as the first
        argument, and the parameter set as keyword arguments. It is responsible
        for updating the problem and solving it.

        The new problems for each parameter set are saved using memoization, so
        that it does not have to be generated more than once for the given
        parameter set.
        """
        self.base_problem = problem
        self.x_values = problem.x()
        self.solve_function = solve_function
        self.parameters_list = parameters_list

        if first_parameter is None:
            first_parameter = 0

        if isinstance(first_parameter, int):
            first_parameter = parameters_list[first_parameter]

        first_problem = copy.deepcopy(problem)
        solve_function(first_problem, **first_parameter)

        self.x = np.empty(0, dtype='complex')
        self.norms = []
        self.a = []
        self.b = []
        self.fa = []
        self.fb = []
        self.bases = []
        self.M = 0
        self.B = np.asmatrix(np.empty((0, 0), dtype='complex'))
        self.Bp = np.asmatrix(np.empty((0, 0), dtype='complex'))
        self._insert_basis(first_problem)

    def _base_rhs(self, **parameters):
        rhs = np.empty((self.x_values.size), dtype='complex')
        for i in range(self.x_values.size):
            rhs[i] = (self.a[i](**parameters) * self.fa[i](self.x_values[i]) +
                      self.b[i](**parameters) * self.fb[i](self.x_values[i]))
        return rhs

    def add_basis(self):
        errors = np.zeros((len(self.parameters_list)))
        for i in range(len(self.parameters_list)):
            params = self.parameters_list[i]
            errors[i] = np.max(self.point_solution(self.x_values, **params) -
                               self._base_rhs(**params))
        e_i = np.argmax(errors)

        params = self.parameters_list[e_i]
        problem = copy.deepcopy(self.base_problem)
        solve_function(problem, **params)
        self._insert_basis(problem)

        return errors[e_i]

    def _problem_point_solution(self, problem, point):
        u = 0
        for n in range(len(problem.domains)):
            d = problem.domains[n]
            for i in range(len(problem.bases)):
                b = problem.bases[i]
                n0 = problem.basis_noff[i]
                n1 = n0 + b.N
                if b in d.bases:
                    coeff = problem.coeffs[n0:n1]
                    Ad = b.matrix(problem.k, point)
                    u += Ad * coeff
        return u

    def _insert_basis(self, problem):
        # Now, find the maximums, and store the information
        if self.M > 0:
            alphas = np.linalg.solve(self.B, problem.point_solution(self.x))
        u_max = float('-inf')
        for s in problem.segments:
            for x in s.x:
                x = np.asarray(x)
                u = self._problem_point_solution(problem, x)
                for i in range(self.M):
                    u -= ((alphas[i] / self.norms[i]) *
                          self._problem_point_solution(problem, x))
                if u > u_max:
                    u_max = u
                    x_max = x
                    a = s.a
                    b = s.b
                    fa = s.fa
                    fb = s.fb

        self.M += 1
        self.bases += [problem]
        self.x = np.concatenate([self.x, [x_max]])
        self.norms += [u_max]
        if callable(a):
            self.a += [a]
        else:
            def _a(**params):
                return a
            self.a += [_a]
        if callable(b):
            self.b += [b]
        else:
            def _b(**params):
                return b
            self.b += [_b]
        self.fa += [fa]
        self.fb += [fb]

        # Use the already computed values. They don't change with the new
        # basis addition, except for the normalization at the end.
        B = np.asmatrix(np.zeros((self.M, self.M)))
        B[:-1, :-1] = self.B
        Bp = np.asmatrix(np.zeros((self.M, self.M)))
        Bp[:-1, :-1] = self.Bp

        for i in range(self.M - 1):
            B[-1, i] = self.problems[i].point_solution(x_k) / self.norms[i]
            Bp[-1, i] = self.problems[i].point_solution(x_k, 1) / self.norms[i]
        B[-1, -1] = 1
        Bp[-1, -1] = problem.point_solution(x_k, 1) / norm

        # Orthoganize the matrices, using a modified Gram-Schmidt process:
        for i in range(self.M - 1):
            norm = np.dot(B[:, i], B[:, i])
            normp = np.dot(Bp[:, i], B[:, i])
            for j in range(i + 1, self.M):
                B[:, j] -= B[:, i] * (np.dot(B[:, i], B[:, j]) / norm)
                Bp[:, j] -= Bp[:, i] * (np.dot(Bp[:, i], Bp[:, j]) / normp)

        self.B = B
        self.Bp = Bp

        log.debug('New B matrix:\n%s', self.B)
        log.debug('New Bp matrix:\n%s', self.Bp)
        log.debug('New x: %s', self.x)
        log.debug('New norm: %s', self.norms)

    def coeffs(self, **parameters):
        A = np.asmatrix(np.zeros((self.M, self.M), dtype='complex'))
        for i in range(self.M):
            for j in range(self.M):
                A[i, j] = (self.a[i](**parameters) *
                           self.bases[i].point_solution(self.x[i]))
                A[i, j] += (self.b[i](**parameters) *
                            self.bases[i].point_solution(self.x[i], 1))
        rhs = np.empty((self.M), dtype='complex')
        for i in range(self.M):
            rhs[i] = (self.a[i](**parameters) * self.fa[i](self.x[i]) +
                      self.b[i](**parameters) * self.fb[i](self.x[i]))
        return np.linalg.solve(A, rhs)

    def point_solution(self, points, **parameters):
        c = self.coeffs(**parameters)
        soln = np.zeros_like(points, dtype='complex')
        for i in range(self.M):
            soln += c[i] * self.bases[i].point_solution(points)
        return soln

    def solve(self, tolerance=1e-8):
        error = float('inf')
        while error > tolerance:
            error = self.add_basis()
            log.info('New basis function added, maximum error was %s', error)

        log.info('Tolerance of %s reached.', tolerance)
