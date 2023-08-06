__all__ = [
    "clenshaw_curtis",
    "gauss",
    "legendre_gauss_lobatto",
    "periodic_trapezoid",
    "trapezoid",
    ]


import logging
from math import (
    pi,
    floor,
    )

import numpy as np
import numpy.fft
import numpy.linalg


log = logging.getLogger(__name__)


def periodic_trapezoid(N):
    shift = 1 / N
    x = np.linspace(-1 + shift, 1 - shift, N)
    w = np.ones(N) * (2.0 / float(N))
    return (x, w)


def trapezoid(N):
    x = np.linspace(-1, 1, N + 1)
    w = np.ones(N + 1) * (2.0 / float(N))
    w[0] = w[-1] = 1.0 / float(N)
    return (x, w)


def clenshaw_curtis(N):
    theta = pi * np.linspace(1, 0, N + 1)
    x = np.cos(theta)
    W = np.kron(-1.0 / ((np.arange(1, floor(N / 2) + 1) ** 2) - 0.25), [0, 1])
    if N % 2 == 1:
        W = np.concatenate([W, [0]])
    W = np.fft.ifft(np.concatenate([[4], W, W[-2::-1]])).real
    w = np.concatenate([[0.5 * W[0]], W[1:N], [0.5 * W[0]]])
    return (x, w)


def gauss(N):
    if N > 300:
        log.warning('Finding gauss quadrature for large N is slow.')
        log.warning('There are O(M^3) operations, M = %d, M^3 = %d' %
                    (N, N ** 3))
    beta = 0.5 / np.sqrt(1.0 - (2.0 * np.arange(1, N)) ** -2)
    T = np.diag(beta, 1) + np.diag(beta, -1)
    [W, V] = np.linalg.eig(T)
    i = np.argsort(W)
    x = W[i]
    w = 2 * V[0, i] ** 2
    return (x, w)


def legendre_gauss_lobatto(N):
    # Use the Chebyshev-Gauss-Lobatto nodes as the first guess
    x = np.cos(np.linspace(0, pi, N))
    # The Legendre Vandermonde Matrix
    P = np.zeros((N, N))
    # Compute P_(N) using the recursion relation
    # Compute its first and second derivatives and
    # update x using the Newton-Raphson method.
    xold = 2
    while np.amax(np.abs(x - xold)) > (1e-15):
        xold = x
        P[:, 0] = 1
        P[:, 1] = x
        for k in range(2, N):
            P[:, k] = ((2 * k - 1) * x * P[:, k - 1] -
                       (k - 1) * P[:, k - 2]) / k
        x = xold - (x * P[:, N - 1] - P[:, N - 2]) / (N * P[:, N - 1])

    w = 2.0 / ((N - 1) * N * np.square(P[:, N - 1]))

    return (np.array(x[::-1]), np.array(w[::-1]))
