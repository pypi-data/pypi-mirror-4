import logging

import numpy as np


log = logging.getLogger(__name__)


class EI:

    def __init__(self, f, f_interpolate,
                 quadrature_nodes, quadrature_weights,
                 parameters):
        """Creates an EI object, without calculating any basis functions.

        Parameters
        ==========
        * f: The function to construct an EI for. This must be a callable
             object that takes an element from `quadrature_nodes` as the first
             argument, followed by the parameters.
        * f_interpolate: A callable that will generate an interpolation. The
             call signature is f_interpolate(nodes, values), where nodes are
             the points at which the interpolation is based, and values are the
             values of the function at that point. In this way, the user can
             fine tune the method used to interpolate the calculated grid of
             values used in the EI representation.
        * quadrature_nodes: A numpy array containing the candidate point set
             for quadrature nodes.
        * quadrature_weights: The corresponding weights for the given nodes.
             These are used to calculate the L2 norms.
        * parameters: The candidate set of parameters. This is a numpy array,
             with shape (M, d), where d is the dimension of the parameter
             space.
        """
        self.f = f
        self.f_interpolate = f_interpolate
        self.nodes = quadrature_nodes
        self.weights = quadrature_weights
        self.parameters = parameters

        self.Q = np.mat(np.zeros((quadrature_nodes.size, 0)))
        self.basis_max_x = np.zeros(0, dtype=quadrature_nodes.dtype)
        self.basis_params = []
        self.B = np.mat(np.zeros((0, 0)))
        self.M = 0
        self.interpolants = []
        self.last_correction = float('inf')

    def ensure_capacity(self, M):
        if self.Q.shape[1] < M:
            Q = np.mat(np.empty((self.nodes.size, M)))
            Q[:, :self.M] = self.Q[:, :self.M]
            self.Q = Q
        if self.basis_max_x.size < M:
            t = np.empty(M, dtype=self.basis_max_x.dtype)
            t[:self.M] = self.basis_max_x[:self.M]
            self.basis_max_x = t
        if self.B.shape[0] < M:
            B = np.mat(np.zeros((M, M)))
            B[:self.M, :self.M] = self.B[:self.M, :self.M]
            self.B = B

    def add_basis(self):
        self.ensure_capacity(self.M + 1)

        # Find the maximum interpolant:
        max_params = None
        max_value = float('-inf')
        for i in range(self.parameters.shape[0]):
            params = self.parameters[i]
            # If there are no bases yet, use zero:
            if self.M == 0:
                I = np.zeros_like(self.nodes)
            else:
                I = np.reshape(self.Q[:, :self.M] *
                               self.get_coeff(lambda x: self.f(x, *params)),
                               self.nodes.shape)
            maximum = np.amax(np.abs(self.f(self.nodes, *params) - I))
            if maximum > max_value:
                max_value = maximum
                max_params = params
        self.basis_params.append(max_params)
        log.debug("New basis parameters: %s", max_params)

        # Now the base function for this interpolant is:
        ksi = lambda x: self.f(x, *max_params)

        # And the last interpolant at the new maximum is:
        if self.M == 0:
            I = np.zeros((self.nodes.size, 1))
        else:
            I = self.Q[:, :self.M] * self.get_coeff(ksi)

        diff = ksi(self.nodes).reshape((self.nodes.size, 1)) - I
        max_index = np.argmax(np.abs(diff))
        new_max_x = self.nodes[max_index]
        log.debug("New basis maximum at x: %s", new_max_x)
        self.basis_max_x[self.M] = new_max_x
        self.Q[:, self.M] = (np.reshape(diff, (self.nodes.size, 1)) /
                             (ksi(new_max_x) - I[max_index]))

        self.interpolants.append(self.f_interpolate(self.nodes,
                                                    self.Q[:, self.M].flat))

        for j in range(self.M):
            self.B[j, self.M] = 0
            self.B[self.M, j] = self.Q[max_index, j]
        self.B[self.M, self.M] = 1

        #log.debug("B matrix is now:\n%s", self.B[:, :])

        self.M += 1

        log.info("Added new basis function (#%s), maximum correction is %s",
                 self.M, max_value)
        self.last_correction = max_value
        # Return the value that the interpolation was corrected by:
        return max_value

    def get_coeff(self, f, M=None):
        if M is None:
            M = self.M

        if M < 0 or M > self.M:
            raise ValueError("M value %s is outside acceptable range " % M +
                             "of [0, %s]" % self.M)

        b = f(self.basis_max_x[:M])
        y = np.linalg.solve(self.B[:M, :M], b.flat)
        return y.reshape((M, 1))

    def solve(self, M=None, tolerance=1e-10):
        if M is None:
            while self.last_correction > tolerance:
                self.add_basis()
        else:
            self.ensure_capacity(M)
            for i in range(M):
                self.add_basis()

    def __call__(self, x, *params, M=None):
        if M is None:
            M = self.M

        if M == 0:
            return 0

        if M < 0 or M > self.M:
            raise ValueError("M value %s is outside acceptable range " % M +
                             "of [0, %s]" % self.M)

        phi = self.get_coeff(lambda x: self.f(x, *params), M)
        ans = np.zeros_like(x)
        for i in range(M):
            ans += (phi[i, 0] * self.interpolants[i](x))
        return ans

    def L2_norm(self, *params, M=None):
        if M is None:
            M = self.M

        if M < 0 or M > self.M:
            raise ValueError("M value %s is outside acceptable range " % M +
                             "of [0, %s]" % self.M)

        f_values = self.f(self.nodes, *params)
        calc = self(self.nodes, *params, M=M)

        return np.sqrt(np.sum(self.weights *
                              np.abs(np.square(f_values - calc))))
