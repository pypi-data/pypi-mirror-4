import copy
import logging
from math import pi

import numpy as np
import numpy.ma as ma

import empirical.basis
import empirical.quadrature
import empirical.utils


log = logging.getLogger(__name__)


class Segment:

    """Contains a description of a line segment.

    """

    def __init__(self, Z, Zp, M=20, qtype='c', quadrule=None):
        """Creates a segment object using given functions.

        Creates a line segment using the given functions. The argument t should
        be in the range [0, 1].

        Parameters
        ==========
        - `M` is the number of points to use
        - `qtype` is the discretization to use

        Discretization (controlled by `qtype`)
        ======================================
        - 'p' uses the periodic trapezoid method,
          `empirical.quadrature.periodic_trapezoid`
        - 't' uses the trapezoid method, `empirical.quadrature.trapezoid`
        - 'c' uses the Clenshaw-Curtis method, `empirical.quadrature.clenshaw_curtis`
        - 'g' uses the Gauss method, `empirical.quadrature.gauss`
        """
        self.Z = Z
        self.Zp = Zp
        napprox = 100

        self.recalc_quadrature(M=M, qtype=qtype, quadrule=quadrule)

        self.approxv = self.Z(np.linspace(0, 1, napprox))

    def __copy__(self):
        seg = Segment(self.Z, self.Zp, self.M, self.qtype, self.quadrule)
        for attr in ['bc_side', 'fa', 'fb', 'g', 'a', 'b']:
            if hasattr(self, attr):
                a = getattr(self, attr)
                setattr(seg, attr, a)
        seg.dom_pos_side = self.dom_pos_side
        seg.dom_neg_side = self.dom_neg_side
        return seg

    def __deepcopy__(self, memo=None):
        if memo is None:
            memo = dict()

        seg = Segment(self.Z, self.Zp, self.M, self.qtype, self.quadrule)
        for attr in ['bc_side', 'fa', 'fb', 'g', 'a', 'b']:
            if hasattr(self, attr):
                a = getattr(self, attr)
                if not a in memo:
                    memo[a] = copy.deepcopy(a, memo)
                setattr(seg, attr, memo[a])
        if not self.dom_pos_side in memo:
            memo[self.dom_pos_side] = copy.deepcopy(self.dom_pos_side, memo)
        if not self.dom_neg_side in memo:
            memo[self.dom_neg_side] = copy.deepcopy(self.dom_neg_side, memo)
        seg.dom_pos_side = memo[self.dom_pos_side]
        seg.dom_neg_side = memo[self.dom_neg_side]
        return seg

    def recalc_quadrature(self, M=20, qtype=None, quadrule=None):
        """Recalculate quadrature points, weights, and associated values.

        This will recalculate:
        - `self.t` to M points in [0, 1]
        - `self.x` to the values of `self.Z(self.t)`
        - `self.speed`
        - `self.w`
        - `self.nx`
        """
        if quadrule is None:
            if qtype is None:
                quadrule = self.quadrule
                qtype = self.qtype
            elif qtype == 'p':
                quadrule = empirical.quadrature.periodic_trapezoid
            elif qtype == 't':
                quadrule = empirical.quadrature.trapezoid
            elif qtype == 'g':
                quadrule = empirical.quadrature.gauss
            elif qtype == 'c':
                quadrule = empirical.quadrature.clenshaw_curtis
            else:
                raise ValueError('Unknown quadrature type %s' % qtype)

        self.quadrule = quadrule
        self.qtype = qtype
        self.M = M

        # quadrule must give monotonic increasing z in [-1, 1]
        z, self.w = quadrule(M)
        self.t = (1 + z) / 2.0
        self.x = self.Z(self.t)
        dZdt = self.Zp(self.t)
        self.speed = np.abs(dZdt)
        self.w = self.w / 2.0 * self.speed
        self.nx = complex(0, -1) * dZdt / self.speed

    def Zn(self, t):
        zp = self.Zp(t)
        return -1j * zp / np.abs(zp)

    def set_bc(self, normals_side, a, b, f=None):
        """Set the boundary condition.

        Imposes the condition (a * u) + (b * du/dn) = f.
        If `f` is None (default), the homogenous condition is set.
        If normals_positive is True, then the condition is applied to the
        positive normal side. If False, it is applied to the negative normals
        side.
        """
        if normals_side != 1 and normals_side != -1:
            raise ValueError("Can't interpret normals_side value: %s" %
                             normals_side)
        self.bc_side = normals_side

        if normals_side == 1:
            if not hasattr(self, 'dom_pos_side') or self.dom_pos_side is None:
                raise ValueError('Positive normal side not connected ' +
                                 'to a domain!')
        else:
            if not hasattr(self, 'dom_neg_side') or self.dom_neg_side is None:
                raise ValueError('Negative normal side not connected ' +
                                 'to a domain!')

        if f is None:
            self.f = lambda t: np.zeros_like(t)
        else:
            self.f = f

        self.a = a
        self.b = b

    def set_matching_condition(self, a, b, f=None, g=None):
        if (not hasattr(self, 'dom_pos_side') or
            not hasattr(self, 'dom_neg_side') or
            not isinstance(self.dom_pos_side, Domain) or
            not isinstance(self.dom_neg_side, Domain)):
            raise ValueError('Both sides of the segment must be connected ' +
                             'to a Domain object!')
        self.bc_side = 0

        if f is None:
            f = lambda t: np.zeroes_like(t)
        if g is None:
            g = lambda t: np.zeroes_like(t)
        self.f = f
        self.g = g

        if len(a) != 2 or len(b) != 2:
            raise ValueError('a and b must be of size 1x2!')
        self.a = a
        self.b = b

    def scale(self, factor):
        """Scales the segment about the origin."""
        self.x *= factor
        self.w *= factor
        self.speed *= factor
        Z = self.Z
        Zp = self.Zp
        self.Z = lambda t: factor * Z(t)
        self.Zp = lambda t: factor * Zp(t)
        self.approxv *= factor

    def dist(self, t):
        """Crude estimate of distance between self and t."""
        if isinstance(t, Domain):
            d = float('inf')
            for s in t.seg:
                d = min(d, self.dist(s))
            return d
        if isinstance(t, Segment):
            t = t.x
        d = float('inf')
        for i in range(self.x.size):
            d = min(d, np.min(np.abs(t - self.x[i])))
        return d

    def plot(self, show_normals=False, pm=1, show_arrow=False):
        import matplotlib.pyplot as plt
        plt.gcf()

        x = self.x.real
        y = self.x.imag
        if np.abs(self.Z(0) - self.Z(1)) < 1e-15:
            x = np.concatenate([x, [self.x[0].real]])
            y = np.concatenate([y, [self.x[0].imag]])
            
        h = plt.plot(x, y, '.-')

        if show_normals:
            l = 0.1
            for i in range(self.x.size):
                h += plt.plot([self.x[i].real,
                               self.x[i].real + l * pm * self.nx[i].real],
                              [self.x[i].imag,
                               self.x[i].imag + l * pm * self.nx[i].imag],
                              'k-'
                              )
        if show_arrow:
            t = 0.5 + pm * 0.04 * np.array([complex(-1, 1),
                                            complex(1, 0),
                                            complex(-1, -1)])
            x = self.Z(t)
            h += plt.plot(x.real, x.imag, '-')

        plt.axis('equal')

        return h

    def __repr__(self):
        content = ("<Segment:" +
                   "\n\tquadrule: %s" % self.quadrule.__name__ +
                   "\n\tt: %s" % self.t.shape +
                   "\n\tw: %s" % self.w.shape +
                   "\n\tx: %s" % self.x.shape +
                   "\n\tnx: %s" % self.nx.shape +
                   "\n\tspeed: %s" % self.speed.shape +
                   "\n\tapproxv: %s" % self.approxv.shape +
                   "\n\tZ: %s" % self.Z.__name__ +
                   "\n\tZp: %s" % self.Zp.__name__ +
                   "\n\ta: %s" % self.a +
                   "\n\tb: %s" % self.b +
                   "\n\tf: %s" % self.f +
                   "\n>")
        return content


class LineSegment(Segment):

    def Z(self, t):
        return self.t0 + (self.dx * t)

    def Zp(self, t):
        return self.dx * np.ones_like(t)

    def __init__(self, t0, t1, M=20, qtype='g', quadrule=None):
        """Creates a segment object describing an arc.

        Creates an arc, centered at center=[xc, yc], with a radius of R, and
        between angles t0 and t1. If (t1 - t0) is approximately 2 * pi, it is
        assumed that a circle is being created, and a periodic discretization
        will be used.
        """
        self.t0 = t0
        self.t1 = t1
        self.dx = (t1 - t0)

        self.recalc_quadrature(M, qtype, quadrule)

        self.approxv = np.array([t0, t1])

    def __copy__(self):
        seg = LineSegment(self.t0, self.t1, self.M, self.qtype, self.quadrule)
        for attr in ['bc_side', 'fa', 'fb', 'g', 'a', 'b']:
            if hasattr(self, attr):
                a = getattr(self, attr)
                setattr(seg, attr, a)
        seg.dom_pos_side = self.dom_pos_side
        seg.dom_neg_side = self.dom_neg_side
        return seg

    def __deepcopy__(self, memo=None):
        if memo is None:
            memo = dict()

        seg = LineSegment(self.t0, self.t1, self.M, self.qtype, self.quadrule)
        for attr in ['bc_side', 'fa', 'fb', 'g', 'a', 'b']:
            if hasattr(self, attr):
                a = getattr(self, attr)
                if not a in memo:
                    memo[a] = copy.deepcopy(a, memo)
                setattr(seg, attr, memo[a])
        if not self.dom_pos_side in memo:
            memo[self.dom_pos_side] = copy.deepcopy(self.dom_pos_side, memo)
        if not self.dom_neg_side in memo:
            memo[self.dom_neg_side] = copy.deepcopy(self.dom_neg_side, memo)
        seg.dom_pos_side = memo[self.dom_pos_side]
        seg.dom_neg_side = memo[self.dom_neg_side]
        return seg


class ArcSegment(Segment):

    def Z(self, t):
        return (self.center +
                self.R * np.exp(complex(0, 1) *
                                (self.t0 + t * (self.t1 - self.t0))))

    def Zp(self, t):
        return (((self.t1 - self.t0) * self.R) *
                complex(0, 1) * np.exp(complex(0, 1) *
                                       (self.t0 + t * (self.t1 - self.t0))))

    def __init__(self, center, R, t0, t1, M=20, qtype='c', quadrule=None):
        """Creates a segment object describing an arc.

        Creates an arc, centered at center=[xc, yc], with a radius of R, and
        between angles t0 and t1. If (t1 - t0) is approximately 2 * pi, it is
        assumed that a circle is being created, and a periodic discretization
        will be used.
        """
        self.center = center
        self.R = R
        self.t0 = t0
        self.t1 = t1
        if abs(t1 - t0 - 2 * pi) < 1e-15:
            qtype = 'p'

        self.recalc_quadrature(M, qtype, quadrule)

        self.approxv = self.Z(np.linspace(0, 1, 50))

    def __copy__(self):
        seg = ArcSegment(self.center, self.R, self.t0, self.t1, self.M,
                         self.qtype, self.quadrule)
        for attr in ['bc_side', 'fa', 'fb', 'g', 'a', 'b']:
            if hasattr(self, attr):
                a = getattr(self, attr)
                setattr(seg, attr, a)
        seg.dom_pos_side = self.dom_pos_side
        seg.dom_neg_side = self.dom_neg_side
        return seg

    def __deepcopy__(self, memo=None):
        if memo is None:
            memo = dict()

        seg = ArcSegment(self.center, self.R, self.t0, self.t1, self.M,
                         self.qtype, self.quadrule)
        for attr in ['bc_side', 'fa', 'fb', 'g', 'a', 'b']:
            if hasattr(self, attr):
                a = getattr(self, attr)
                if not a in memo:
                    memo[a] = copy.deepcopy(a, memo)
                setattr(seg, attr, memo[a])
        if not self.dom_pos_side in memo:
            memo[self.dom_pos_side] = copy.deepcopy(self.dom_pos_side, memo)
        if not self.dom_neg_side in memo:
            memo[self.dom_neg_side] = copy.deepcopy(self.dom_neg_side, memo)
        seg.dom_pos_side = memo[self.dom_pos_side]
        seg.dom_neg_side = memo[self.dom_neg_side]
        return seg

    def __repr__(self):
        content = ("<ArcSegment:" +
                   "\n\tcenter: %s" % self.center +
                   "\n\tR: %s" % self.R +
                   "\n\tt0: %s" % self.t0 +
                   "\n\tt1: %s" % self.t1 +
                   "\n\tquadrule: %s" % self.quadrule.__name__ +
                   "\n\tt: %s" % self.t.shape +
                   "\n\tw: %s" % self.w.shape +
                   "\n\tx: %s" % self.x.shape +
                   "\n\tnx: %s" % self.nx.shape +
                   "\n\tspeed: %s" % self.speed.shape +
                   "\n\tapproxv: %s" % self.approxv.shape +
                   "\n\tZ: %s" % self.Z.__name__ +
                   "\n\tZp: %s" % self.Zp.__name__ +
                   "\n\ta: %s" % self.a +
                   "\n\tb: %s" % self.b +
                   "\n\tf: %s" % self.f +
                   "\n>")
        return content


class RadialSegment(Segment):

    def Z(self, t):
        return np.exp(2j * pi * t) * self.radius(2 * pi * t)

    def Zp(self, t):
        e = np.exp(2j * pi * t)
        f = self.radius(2 * pi * t)
        fp = self.radiusp(2 * pi * t)
        return 2 * pi * ((1j * e * f) + (e * fp))

    def __init__(self, f, fp, M=20):
        """Creates a segment object describing a periodic, radial function.

        The function f(theta) describes the radius as a function of angle,
        where theta is in [0, 2 * pi]. The function fp describes the derivative
        of f.
        """
        self.radius = f
        self.radiusp = fp

        self.recalc_quadrature(M=M, qtype='p')

        self.approxv = self.Z(np.linspace(0, 1, 100))

    def __copy__(self):
        seg = RadialSegment(self.radius, self.radiusp, self.M)
        for attr in ['bc_side', 'f', 'g', 'a', 'b']:
            if hasattr(self, attr):
                a = getattr(self, attr)
                setattr(seg, attr, a)
        seg.dom_pos_side = self.dom_pos_side
        seg.dom_neg_side = self.dom_neg_side
        return seg

    def __deepcopy__(self, memo=None):
        if memo is None:
            memo = dict()

        seg = RadialSegment(self.radius, self.radiusp, self.M)
        for attr in ['bc_side', 'fa', 'fb', 'g', 'a', 'b']:
            if hasattr(self, attr):
                a = getattr(self, attr)
                if not a in memo:
                    memo[a] = copy.deepcopy(a, memo)
                setattr(seg, attr, memo[a])
        if not self.dom_pos_side in memo:
            memo[self.dom_pos_side] = copy.deepcopy(self.dom_pos_side, memo)
        if not self.dom_neg_side in memo:
            memo[self.dom_neg_side] = copy.deepcopy(self.dom_neg_side, memo)
        seg.dom_pos_side = memo[self.dom_pos_side]
        seg.dom_neg_side = memo[self.dom_neg_side]
        return seg

    def __repr__(self):
        content = ("<RadialSegment:" +
                   "\n\tradius: %s" % self.radius.__name__ +
                   "\n\tradiusp: %s" % self.radiusp.__name__ +
                   "\n\tquadrule: %s" % self.quadrule.__name__ +
                   "\n\tt: %s" % self.t.shape +
                   "\n\tw: %s" % self.w.shape +
                   "\n\tx: %s" % self.x.shape +
                   "\n\tnx: %s" % self.nx.shape +
                   "\n\tspeed: %s" % self.speed.shape +
                   "\n\tapproxv: %s" % self.approxv.shape +
                   "\n\tZ: %s" % self.Z.__name__ +
                   "\n\tZp: %s" % self.Zp.__name__ +
                   "\n\ta: %s" % self.a +
                   "\n\tb: %s" % self.b +
                   "\n\tf: %s" % self.f +
                   "\n>")
        return content


def approximate_polygon(segments, senses):
    v = []
    for i in range(len(segments)):
        # Drop the last point, and use the appropriate direction.
        if senses[i] == 1:
            v += [segments[i].approxv]
        else:
            v += [segments[i].approxv[::-1]]
    return np.concatenate(v)


def stack_quadrature_points(segments, senses):
    x = []
    nx = []
    for i in range(len(segments)):
        if senses[i] == 1:
            x += [segments[i].x]
            nx += [segments[i].nx]
        else:
            x += [segments[i].x[::-1]]
            nx += [segments[i].nx[::-1]]
    return (np.concatenate(x), np.concatenate(nx))


class Domain:

    def __copy__(self):
        if self.exterior:
            dom = Domain([], [], self.segments, self.senses,
                         k=self.k, n=self.n)
        else:
            dom = Domain(self.segments, self.senses, k=self.k, n=self.n)

        return dom

    def __deepcopy__(self, memo=None):
        if memo is None:
            memo = dict()

        segs = []
        for s in self.segments:
            if not s in memo:
                memo[s] = copy.deepcopy(s, memo)
            segs.append(memo[s])

        if self.exterior:
            dom = Domain([], [], segs, list(self.senses), k=self.k, n=self.n)
        else:
            base = [self.segs[i] for i in range(len(segs))
                    if self.spiece[i] == 0]
            senses = [self.senses[i] for i in range(len(segs))
                      if self.spiece[i] == 0]
            holes = [self.segs[i] for i in range(len(segs))
                     if self.spiece[i] != 0]
            hole_senses = [self.senses[i] for i in range(len(segs))
                           if self.spiece[i] != 0]
            dom = Domain(base, list(senses), holes, list(hole_senses),
                         k=self.k, n=self.n)

        for b in self.bases:
            dom.bases.append(copy.deepcopy(b, memo))

        return dom

    def __init__(self, *args, k=float('nan'), n=1.0):
        self.perimeter = 0
        self.segments = []
        self.senses = []
        self.bases = []
        self.refractive_index = n
        self.k = k
        self.spiece = []

        if len(args) == 0:
            self.__init__([], [])
            return
        elif isinstance(args[0], Segment):
            self.area = 0
            self.exterior = False
            self.add_segment(args[0], args[1])
        elif len(args[0]) > 0:
            self.area = 0
            self.exterior = False
            for i in range(len(args[0])):
                self.add_segment(args[0][i], args[1][i])
        else:
            self.area = float('inf')
            self.exterior = True

        if len(args) > 2:
            if isinstance(args[2], Segment):
                self.add_segment(args[2], args[3], hole=True)
            else:
                for i in range(len(args[2])):
                    self.add_segment(args[2][i], args[3][i], hole=True)

        if np.any(self.normals_check() == False):
            log.warning('Probable bad sense of segment normals!')

    def add_segment(self, seg, sense, hole=False):
        self.segments += [seg]
        self.senses += [sense]

        if not hole:
            # Outer boundary is 'piece number 0', for all segments on it
            self.spiece += [0]
        else:
            if len(self.spiece) == 0:
                self.spiece += [1]
            else:
                self.spiece += [max(self.spiece) + 1]

        self.perimeter += np.sum(seg.w)

        xdn = (seg.x.conjugate() * seg.nx).real
        area = np.sum(seg.w * xdn) / 2
        if hole:
            self.area -= area
        else:
            self.area += area

        if sense == -1:
            if hasattr(seg, 'dom_neg_side'):
                if not seg.dom_neg_side is None:
                    log.warning('segment already bordering a domain on' +
                                ' negative side!')
            seg.dom_neg_side = self
        elif sense == 1:
            if hasattr(seg, 'dom_pos_side'):
                if not seg.dom_pos_side is None:
                    log.warning('segment already bordering a domain on' +
                                ' positive side!')
            seg.dom_pos_side = self

    def normals_check(self):
        eps = 1e-8
        t = 0.5
        p = np.zeros(len(self.segments), dtype='complex')
        for j in range(len(self.segments)):
            s = self.segments[j]
            p[j] = s.Z(t) + eps * self.senses[j] * s.Zn(t)

        return ~self.inside(p)

    def _get_segments(self, piece):
        segs = []
        senses = []
        for i in range(len(self.spiece)):
            if self.spiece[i] == piece:
                segs += [self.segments[i]]
                senses += [self.senses[i]]
        return (segs, senses)

    def inside(self, points):
        if not isinstance(points, np.ndarray):
            raise ValueError('The points passed to Domain.inside() ' +
                             'must be a numpy array!')
        if self.exterior:
            i = np.ones_like(points, dtype='bool')
        else:
            v = approximate_polygon(*self._get_segments(0))
            i = empirical.utils.in_polygon(points, v)

        # If there are no holes, we're done.
        if len(self.spiece) == 0:
            return i
        # This line is necessary to avoid calling max([]) where
        # the array is empty.

        # Remove points from each hole:
        for p in range(1, max(self.spiece) + 1):
            v = approximate_polygon(*self._get_segments(p))
            i &= ~empirical.utils.in_polygon(points, v)

        return i

    def x(self):
        x = []
        for i in range(len(self.segments)):
            if self.senses[i] == 1:
                x += [self.segments[i].x]
            else:
                x += [self.segments[i].x[::-1]]
        return np.concatenate(x)

    def nx(self):
        nx = []
        for i in range(len(self.segments)):
            if self.senses[i] == 1:
                nx += [self.seg[i].nx]
            else:
                nx += [-self.seg[i].nx[::-1]]
        return np.concatenate(nx)

    def speed(self):
        speed = []
        for i in range(len(self.segments)):
            if self.senses[i] == 1:
                speed += [self.seg[i].speed]
            else:
                speed += [self.seg[i].speed[::-1]]
        return np.concatenate(speed)

    def w(self):
        w = []
        for i in range(len(self.segments)):
            if self.senses[i] == 1:
                w += [self.seg[i].w]
            else:
                w += [self.seg[i].w[::-1]]
        return np.concatenate(w)

    def bounding_box(self, exterior_pad=0.5):
        if len(self.segments) == 0 and self.exterior:
            return [0, 0, 0, 0]
        bb = np.array([float('inf'), float('-inf'),
                       float('inf'), float('-inf')])
        for s in self.segments:
            bb[0] = min(bb[0], np.min(s.x.real))
            bb[1] = max(bb[1], np.max(s.x.real))
            bb[2] = min(bb[2], np.min(s.x.imag))
            bb[3] = max(bb[3], np.max(s.x.imag))
        if self.exterior:
            bb += np.multiply(exterior_pad, [-1, 1, -1, 1])

        return bb

    def center(self):
        bb = self.bounding_box()
        return [0.5 * (bb[0] + bb[1]),
                0.5 * (bb[2] + bb[3])]

    def diam(self):
        x = self.x()
        c = self.center()
        return np.max(np.abs(x - c))

    def grid(self, dx, dy, bb=None):
        if dx < 0:
            raise ValueError('dx must be positive!')
        if bb is None:
            bb = self.bounding_box()

        xx, yy = np.meshgrid(np.arange(bb[0], bb[1], dx),
                             np.arange(bb[2], bb[3], dy))
        zz = np.empty(xx.size)
        zz = (xx.reshape((xx.size,)) +
              complex(0, 1) * yy.reshape((yy.size,)))
        zz = ma.array(zz)
        zz.mask = ~self.inside(zz)
        return zz.compressed()

    def add_mfs_basis(self, *args, **kwargs):
        basis = empirical.basis.MFSBasis(*args, **kwargs)
        self.bases.append(basis)
        basis.domain = self
        if np.any(self.inside(basis.q)):
            log.warning('There are basis points inside the domain!')

    def __repr__(self):
        content = ("<Domain:" +
                   "\n\tsegments: %s" % len(self.segments) +
                   "\n\tsenses: %s" % self.senses +
                   "\n\tbases: %s" % len(self.bases) +
                   "\n\tarea: %s" % self.area +
                   "\n\tperimeter: %s" % self.perimeter +
                   "\n\texterior: %s" % self.exterior +
                   "\n\tk: %s" % self.k +
                   "\n\trefractive_index: %s" % self.refractive_index +
                   "\n\tspiece: %s" % self.spiece +
                   "\n>")
        return content

    def plot(self, grid_interior=True, dx=0.03, dy=0.03):
        import matplotlib.pyplot as plt

        h = []
        for s in self.segments:
            h += s.plot()

        for b in self.bases:
            h += b.plot()

        if grid_interior:
            zz = self.grid(dx, dy)
            h += [plt.plot(zz.real, zz.imag, '.', markersize=1)]

        return h
