import logging

import numpy as np


log = logging.getLogger(__name__)


class Lagrange:

    def __init__(self, nodes, evals):
        self.nodes = nodes
        self.evals = evals
        self.N = self.nodes.size
        self.diffs = np.empty((self.N, self.N))
        for i in range(self.N):
            self.diffs[i, :] = self.nodes[i] - self.nodes

    def lagrange(self, i, x):
        ans = np.ones_like(x)
        for j in range(self.N):
            if i == j:
                continue
            ans *= (x - self.nodes[j]) / self.diffs[i, j]
        return ans

    def __call__(self, x):
        ans = np.zeros_like(x)
        for i in range(self.N):
            ans += self.evals[i] * self.lagrange(i, x)
        return ans


class Newton:

    def __init__(self, nodes, evals):
        self.nodes = nodes
        self.evals = evals
        self.N = self.nodes.size
        self.a = np.copy(evals)
        for j in range(1, self.N):
            for i in range(self.N - 1, j - 1, -1):
                self.a[i] = ((self.a[i] - self.a[i-1]) /
                             (nodes[i] - nodes[i - j]))

    def __call__(self, x):
        ans = np.ones_like(x) * self.a[-1]
        for i in range(self.N - 2, -1, -1):
            ans = ans * (x - self.nodes[i]) + self.a[i]
        return ans


class LagrangeBivariate:

    def __init__(self, x_nodes, y_nodes, evals_grid):
        self.x_nodes = x_nodes
        self.y_nodes = y_nodes
        self.N = self.x_nodes.size
        self.M = self.y_nodes.size
        self.evals = evals_grid

        self.diffs_x = np.empty((self.N, self.N))
        for i in range(self.N):
            self.diffs_x[i, :] = self.x_nodes[i] - self.x_nodes

        self.diffs_y = np.empty((self.M, self.M))
        for i in range(self.M):
            self.diffs_y[i, :] = self.y_nodes[i] - self.y_nodes

    def lagrange_x(self, i, x):
        ans = np.ones_like(x)
        for j in range(self.N):
            if i == j:
                continue
            ans *= (x - self.x_nodes[j]) / self.diffs_x[i, j]
        return ans

    def lagrange_y(self, i, y):
        ans = np.ones_like(y)
        for j in range(self.M):
            if i == j:
                continue
            ans *= (y - self.y_nodes[j]) / self.diffs_y[i, j]
        return ans

    def __call__(self, x):
        ans = np.zeros_like(x, dtype=self.evals.dtype)
        for i in range(self.N):
            for j in range(self.M):
                ans += self.evals[j, i] * (self.lagrange_x(i, x.real) *
                                           self.lagrange_y(j, x.imag))
        return ans
