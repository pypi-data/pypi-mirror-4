import logging
from math import pi

import numpy as np
from numpy.random import rand

from scipy.interpolate import griddata

import matplotlib.pyplot as plt

from empirical.eim import EI
from empirical.quadrature import legendre_gauss_lobatto


def f(x, mu1, mu2):
    return 1.0 / np.sqrt(np.square(x.real - mu1) + np.square(x.imag - mu2))


def f_interpolate(nodes, values):
    points = np.empty((nodes.size, 2))
    points[:, 0] = nodes.real
    points[:, 1] = nodes.imag
    return lambda x: griddata(points, values, (x.real, x.imag), method='cubic')


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    print("Solving a 2d eim problem, this may take awhile.")
    print("(Total of 5625 spatial values and 2500 parameter values)")

    nodes, weights = legendre_gauss_lobatto(75)
    nodes += 1
    nodes /= 2
    xx, yy = np.meshgrid(nodes, nodes)
    nodes = np.empty(xx.size, dtype='complex')
    nodes.real = xx.flat
    nodes.imag = yy.flat
    weights, dummy = np.meshgrid(weights, weights)
    weights = weights.flatten()
    params = np.linspace(-1, -0.01, 50)
    xx, yy = np.meshgrid(params, params)
    params = np.empty((xx.size, 2))
    params[:, 0] = xx.flat
    params[:, 1] = yy.flat
    ei = EI(f, f_interpolate, nodes, weights, params)
    ei.solve(M=50)
    test_params = -0.01 + rand(100, 2) * -0.99
    print("M  | L2 norm")
    max_norm = float('-inf')
    for i in range(100):
        max_norm = max(max_norm, ei.L2_norm(test_params[i, 0],
                                            test_params[i, 1], M=5))
    print(" 5 |", max_norm)
    max_norm = float('-inf')
    for p in test_params:
        max_norm = max(max_norm, ei.L2_norm(test_params[i, 0],
                                            test_params[i, 1], M=10))
    print("10 |", max_norm)
    max_norm = float('-inf')
    for p in test_params:
        max_norm = max(max_norm, ei.L2_norm(test_params[i, 0],
                                            test_params[i, 1], M=15))
    print("15 |", max_norm)
    max_norm = float('-inf')
    for p in test_params:
        max_norm = max(max_norm, ei.L2_norm(test_params[i, 0],
                                            test_params[i, 1], M=20))
    print("20 |", max_norm)
    max_norm = float('-inf')
    for p in test_params:
        max_norm = max(max_norm, ei.L2_norm(test_params[i, 0],
                                            test_params[i, 1], M=25))
    print("25 |", max_norm)
    max_norm = float('-inf')
    for p in test_params:
        max_norm = max(max_norm, ei.L2_norm(test_params[i, 0],
                                            test_params[i, 1], M=30))
    print("30 |", max_norm)
    max_norm = float('-inf')
    for p in test_params:
        max_norm = max(max_norm, ei.L2_norm(test_params[i, 0],
                                            test_params[i, 1], M=35))
    print("35 |", max_norm)
    max_norm = float('-inf')
    for p in test_params:
        max_norm = max(max_norm, ei.L2_norm(test_params[i, 0],
                                            test_params[i, 1], M=40))
    print("40 |", max_norm)
    max_norm = float('-inf')
    for p in test_params:
        max_norm = max(max_norm, ei.L2_norm(test_params[i, 0],
                                            test_params[i, 1], M=45))
    print("45 |", max_norm)
    max_norm = float('-inf')
    for p in test_params:
        max_norm = max(max_norm, ei.L2_norm(test_params[i, 0],
                                            test_params[i, 1], M=50))
    print("50 |", max_norm)
