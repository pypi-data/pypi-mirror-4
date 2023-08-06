__all__ = [
    "in_polygon",
    ]


import logging

import numpy as np

from scipy.special import hankel1

log = logging.getLogger(__name__)


def in_polygon(points, vertices):
    from matplotlib.path import Path
    v = np.empty((vertices.size, 2))
    v[:, 0] = vertices.real
    v[:, 1] = vertices.imag
    path = Path(v)
    p = np.empty((points.size, 2))
    p[:, 0] = points.real
    p[:, 1] = points.imag
    return path.contains_points(p)
