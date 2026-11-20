"""Variable-width pen: skeleton curves + width profile -> clean Bézier outline.

The outline is sampled from the skeleton's offsets, then refitted with
Philip J. Schneider's least-squares cubic fitting, so each side of a stroke
comes back as a handful of smooth cubic segments (like a hand-drawn
Illustrator path), not a polyline.
"""
import math
import skia
from vec import P, simplify, union, diff, inter, poly

# ------------------------------------------------------------------ skeleton
class Skel:
    """A chain of cubic segments. Lines are stored as cubics too."""

    def __init__(self, x, y):
        self.segs = []
        self.cur = (x, y)

    def L(self, x, y):
        a = self.cur
        self.segs.append((a, (a[0] + (x - a[0]) / 3, a[1] + (y - a[1]) / 3),
                          (a[0] + 2 * (x - a[0]) / 3, a[1] + 2 * (y - a[1]) / 3), (x, y)))
        self.cur = (x, y)
        return self

    def C(self, x1, y1, x2, y2, x, y):
        self.segs.append((self.cur, (x1, y1), (x2, y2), (x, y)))
        self.cur = (x, y)
        return self


def _bez(s, t):
    (a, b, c, d) = s
    mt = 1 - t
    return (mt ** 3 * a[0] + 3 * mt * mt * t * b[0] + 3 * mt * t * t * c[0] + t ** 3 * d[0],
            mt ** 3 * a[1] + 3 * mt * mt * t * b[1] + 3 * mt * t * t * c[1] + t ** 3 * d[1])


def _dbez(s, t):
    (a, b, c, d) = s
    mt = 1 - t
    x = 3 * mt * mt * (b[0] - a[0]) + 6 * mt * t * (c[0] - b[0]) + 3 * t * t * (d[0] - c[0])
    y = 3 * mt * mt * (b[1] - a[1]) + 6 * mt * t * (c[1] - b[1]) + 3 * t * t * (d[1] - c[1])
    if abs(x) < 1e-9 and abs(y) < 1e-9:
        x, y = d[0] - a[0], d[1] - a[1]
    n = math.hypot(x, y) or 1
    return x / n, y / n


def sample(sk, per_seg=60):
    """Points, unit tangents and normalised arc position u in [0,1]."""
    pts, tans = [], []
    for i, s in enumerate(sk.segs):
        for k in range(per_seg + (1 if i == len(sk.segs) - 1 else 0)):
            t = k / per_seg
            pts.append(_bez(s, t))
            tans.append(_dbez(s, t))
    L = [0.0]
    for i in range(1, len(pts)):
        L.append(L[-1] + math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]))
    tot = L[-1] or 1
    return pts, tans, [l / tot for l in L], tot


# ------------------------------------------------------------------ fitting
def _q(c, t):
    return _bez(c, t)


def _q1(c, t):
    (a, b, cc, d) = c
    mt = 1 - t
    return (3 * mt * mt * (b[0] - a[0]) + 6 * mt * t * (cc[0] - b[0]) + 3 * t * t * (d[0] - cc[0]),
            3 * mt * mt * (b[1] - a[1]) + 6 * mt * t * (cc[1] - b[1]) + 3 * t * t * (d[1] - cc[1]))


def _q2(c, t):
    (a, b, cc, d) = c
    return (6 * (1 - t) * (cc[0] - 2 * b[0] + a[0]) + 6 * t * (d[0] - 2 * cc[0] + b[0]),
            6 * (1 - t) * (cc[1] - 2 * b[1] + a[1]) + 6 * t * (d[1] - 2 * cc[1] + b[1]))


def _norm(v):
    n = math.hypot(*v) or 1
    return (v[0] / n, v[1] / n)


def _chord(pts):
    u = [0.0]
    for i in range(1, len(pts)):
        u.append(u[-1] + math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]))
    return [x / (u[-1] or 1) for x in u]


def _gen(pts, u, t1, t2):
    a = pts[0]; b = pts[-1]
    C = [[0, 0], [0, 0]]
    X = [0, 0]
    for p, t in zip(pts, u):
        mt = 1 - t
        A1 = (t1[0] * 3 * mt * mt * t, t1[1] * 3 * mt * mt * t)
        A2 = (t2[0] * 3 * mt * t * t, t2[1] * 3 * mt * t * t)
        C[0][0] += A1[0] * A1[0] + A1[1] * A1[1]
        C[0][1] += A1[0] * A2[0] + A1[1] * A2[1]
        C[1][1] += A2[0] * A2[0] + A2[1] * A2[1]
        b0 = mt ** 3 + 3 * mt * mt * t
        b1 = 3 * mt * t * t + t ** 3
        tmp = (p[0] - (a[0] * b0 + b[0] * b1), p[1] - (a[1] * b0 + b[1] * b1))
        X[0] += A1[0] * tmp[0] + A1[1] * tmp[1]
        X[1] += A2[0] * tmp[0] + A2[1] * tmp[1]
    C[1][0] = C[0][1]
    det = C[0][0] * C[1][1] - C[0][1] * C[1][0]
    seg = math.hypot(b[0] - a[0], b[1] - a[1])
    if abs(det) < 1e-12:
        al = ar = seg / 3
    else:
        al = (X[0] * C[1][1] - X[1] * C[0][1]) / det
        ar = (C[0][0] * X[1] - C[1][0] * X[0]) / det
    eps = 1e-6 * seg
    if al < eps or ar < eps:
        al = ar = seg / 3
    return (a, (a[0] + t1[0] * al, a[1] + t1[1] * al), (b[0] + t2[0] * ar, b[1] + t2[1] * ar), b)


def _err(pts, c, u):
    m, idx = 0, len(pts) // 2
    for i, (p, t) in enumerate(zip(pts, u)):
        q = _q(c, t)
        dd = (q[0] - p[0]) ** 2 + (q[1] - p[1]) ** 2
        if dd > m:
            m, idx = dd, i
    return m, idx


def _reparam(pts, u, c):
    out = []
    for p, t in zip(pts, u):
        d = _q(c, t); d1 = _q1(c, t); d2 = _q2(c, t)
        num = (d[0] - p[0]) * d1[0] + (d[1] - p[1]) * d1[1]
        den = d1[0] ** 2 + d1[1] ** 2 + (d[0] - p[0]) * d2[0] + (d[1] - p[1]) * d2[1]
        out.append(t if abs(den) < 1e-12 else min(1, max(0, t - num / den)))
    return out


def fit(pts, err=0.6, t1=None, t2=None):
    """Fit cubic Bézier segments through pts. Returns list of 4-point tuples."""
    if len(pts) < 2:
        return []
    t1 = t1 or _norm((pts[1][0] - pts[0][0], pts[1][1] - pts[0][1]))
    t2 = t2 or _norm((pts[-2][0] - pts[-1][0], pts[-2][1] - pts[-1][1]))
    return _fit(pts, t1, t2, err * err)


def _fit(pts, t1, t2, e2):
    if len(pts) == 2:
        a, b = pts
        dd = math.hypot(b[0] - a[0], b[1] - a[1]) / 3
        return [(a, (a[0] + t1[0] * dd, a[1] + t1[1] * dd), (b[0] + t2[0] * dd, b[1] + t2[1] * dd), b)]
    u = _chord(pts)
    c = _gen(pts, u, t1, t2)
    m, idx = _err(pts, c, u)
    if m < e2:
        return [c]
    if m < e2 * 16:
        for _ in range(12):
            u = _reparam(pts, u, c)
            c = _gen(pts, u, t1, t2)
            m, idx = _err(pts, c, u)
            if m < e2:
                return [c]
    idx = max(1, min(len(pts) - 2, idx))
    tc = _norm((pts[idx - 1][0] - pts[idx + 1][0], pts[idx - 1][1] - pts[idx + 1][1]))
    return _fit(pts[:idx + 1], t1, tc, e2) + _fit(pts[idx:], (-tc[0], -tc[1]), t2, e2)


# ------------------------------------------------------------------ pen
def vstroke(sk, width, start="butt", end="butt", err=0.6, per_seg=60):
    """Variable-width stroke along a skeleton.

    width: number or function u -> width (u = 0..1 along the arc).
    start/end: 'butt', 'taper' (width already 0 there), or an angle in
    degrees for a nib cut (the end is cut along that direction)."""
    wf = width if callable(width) else (lambda u, w=width: w)
    pts, tans, us, tot = sample(sk, per_seg)
    L, R = [], []
    for p, t, u in zip(pts, tans, us):
        n = (-t[1], t[0])
        w = max(wf(u), 0.0) / 2
        L.append((p[0] + n[0] * w, p[1] + n[1] * w))
        R.append((p[0] - n[0] * w, p[1] - n[1] * w))
    # nib cuts extend the stroke a little so the cut has material
    lc = fit(L, err)
    rc = fit(R[::-1], err)
    b = P().M(*lc[0][0])
    for c in lc:
        b.C(*c[1], *c[2], *c[3])
    b.L(*rc[0][0])
    for c in rc:
        b.C(*c[1], *c[2], *c[3])
    b.Z()
    out = simplify(b.path())
    for which, spec in (("s", start), ("e", end)):
        if isinstance(spec, (int, float)) and not isinstance(spec, bool):
            p = pts[0] if which == "s" else pts[-1]
            t = tans[0] if which == "s" else tans[-1]
            if which == "s":
                t = (-t[0], -t[1])
            a = math.radians(spec)
            dx, dy = math.cos(a), math.sin(a)
            big = 5000
            # half-plane on the far side of the cut line (beyond the end)
            nx, ny = -dy, dx
            if nx * t[0] + ny * t[1] < 0:
                nx, ny = -nx, -ny
            hp = poly((p[0] + dx * big, p[1] + dy * big), (p[0] - dx * big, p[1] - dy * big),
                      (p[0] - dx * big + nx * big, p[1] - dy * big + ny * big),
                      (p[0] + dx * big + nx * big, p[1] + dy * big + ny * big))
            out = diff(out, hp)
    return out


def ease(a, b, k=1.0):
    """Smooth width ramp helper: returns f(u) from a to b."""
    return lambda u: a + (b - a) * (0.5 - 0.5 * math.cos(math.pi * min(1, max(0, u)) ** k))


def profile(*stops):
    """Piecewise smooth width profile: profile((0,w0),(0.4,w1),(1,0))."""
    stops = sorted(stops)

    def f(u):
        for (u0, w0), (u1, w1) in zip(stops, stops[1:]):
            if u0 <= u <= u1:
                t = (u - u0) / ((u1 - u0) or 1)
                t = 0.5 - 0.5 * math.cos(math.pi * t)
                return w0 + (w1 - w0) * t
        return stops[-1][1] if u > stops[-1][0] else stops[0][1]
    return f
