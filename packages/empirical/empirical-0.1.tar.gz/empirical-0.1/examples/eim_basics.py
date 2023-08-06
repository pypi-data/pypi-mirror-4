import logging
from math import pi

import numpy as np
from numpy.random import rand

from scipy.interpolate import (
    interp1d,
    interp2d,
    )

import matplotlib.pyplot as plt

from empirical.eim import EI
from empirical.quadrature import legendre_gauss_lobatto


def f1(x, mu):
    return 1.0 / (1.0 + np.multiply(mu, np.square(x)))


def f1_interpolate(nodes, values):
    return interp1d(nodes, values, kind='cubic', copy=False)


def f2(x, mu):
    return np.power(1 + x, mu)


def f2_interpolate(nodes, values):
    return interp1d(nodes, values, kind='cubic', copy=False)


def f3(x, mu):
    return np.cos(mu * x)


def f3_interpolate(nodes, values):
    return interp1d(nodes, values, kind='cubic', copy=False)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    print("Solving basic eim demonstrations, not CPU intensive.")

    print("Example #1")
    nodes, weights = legendre_gauss_lobatto(151)
    params = np.linspace(1, 25, 150).reshape((150, 1))
    ei = EI(f1, f1_interpolate, nodes, weights, params)
    ei.solve(M=25)
    test_params = 1 + rand(100) * 24
    print("M  | L2 norm")
    max_norm = float('-inf')
    for p in test_params:
        max_norm = max(max_norm, ei.L2_norm(p, M=5))
    print(" 5 |", max_norm)
    max_norm = float('-inf')
    for p in test_params:
        max_norm = max(max_norm, ei.L2_norm(p, M=10))
    print("10 |", max_norm)
    max_norm = float('-inf')
    for p in test_params:
        max_norm = max(max_norm, ei.L2_norm(p, M=15))
    print("15 |", max_norm)
    max_norm = float('-inf')
    for p in test_params:
        max_norm = max(max_norm, ei.L2_norm(p, M=20))
    print("20 |", max_norm)
    max_norm = float('-inf')
    for p in test_params:
        max_norm = max(max_norm, ei.L2_norm(p, M=25))
    print("25 |", max_norm)

    print("Example #2")
    nodes, weights = legendre_gauss_lobatto(151)
    params = np.linspace(1, 4, 150).reshape((150, 1))
    ei = EI(f2, f2_interpolate, nodes, weights, params)
    ei.solve(M=25)
    test_params = 1 + rand(100) * 4
    print("M  | L2 norm")
    max_norm = float('-inf')
    for p in test_params:
        max_norm = max(max_norm, ei.L2_norm(p, M=5))
    print(" 5 |", max_norm)
    max_norm = float('-inf')
    for p in test_params:
        max_norm = max(max_norm, ei.L2_norm(p, M=10))
    print("10 |", max_norm)
    max_norm = float('-inf')
    for p in test_params:
        max_norm = max(max_norm, ei.L2_norm(p, M=15))
    print("15 |", max_norm)
    max_norm = float('-inf')
    for p in test_params:
        max_norm = max(max_norm, ei.L2_norm(p, M=20))
    print("20 |", max_norm)
    max_norm = float('-inf')
    for p in test_params:
        max_norm = max(max_norm, ei.L2_norm(p, M=25))
    print("25 |", max_norm)

    print("Example #3")
    nodes, weights = legendre_gauss_lobatto(351)
    nodes *= pi
    params = np.linspace(0, 4, 350).reshape((350, 1))
    ei = EI(f3, f3_interpolate, nodes, weights, params)
    ei.solve(M=25)
    test_params = rand(100) * 4
    print("M  | L2 norm")
    max_norm = float('-inf')
    for p in test_params:
        max_norm = max(max_norm, ei.L2_norm(p, M=5))
    print(" 5 |", max_norm)
    max_norm = float('-inf')
    for p in test_params:
        max_norm = max(max_norm, ei.L2_norm(p, M=10))
    print("10 |", max_norm)
    max_norm = float('-inf')
    for p in test_params:
        max_norm = max(max_norm, ei.L2_norm(p, M=15))
    print("15 |", max_norm)
    max_norm = float('-inf')
    for p in test_params:
        max_norm = max(max_norm, ei.L2_norm(p, M=20))
    print("20 |", max_norm)
    max_norm = float('-inf')
    for p in test_params:
        max_norm = max(max_norm, ei.L2_norm(p, M=25))
    print("25 |", max_norm)
