"""«الراية» lettering engine (v4).

One correct Arabic structure, fixed metrics, several pens:

    ا | لـر | ا | يـة
    alif (isolated) · lam initial joined to ra final · alif (isolated)
    · ya initial joined to ta marbuta final

All letters are drawn as skeletons (centre lines) and stroked with a pen
model. Every style shares the same rules:
  - alif and lam are the same height (A); the ya tooth is T high; the
    ta loop sits on the baseline and is about 1.3 T tall;
  - ra drops below the baseline by D, the ya dots hang at the same depth;
  - the white space between separated letters is the same gap G;
  - dots are made by the same pen as the letters (round pen -> round dot,
    flat pen -> square dot, broad nib -> one short nib stroke).
Nothing is cut or filled after drawing.
"""
import math
from vec import P, union, diff, rect, circle, ellipse, stroke, move, scale, bounds, to_origin, poly, simplify
from pen import Skel, vstroke, profile


class Style:
    def __init__(self, name, W, A, T, D, G, pen="round", Wh=None, nib=None, wmin=None,
                 loop_w=1.0, ra_reach=1.0, dot=1.15, lam_r=None, tail=None):
        self.name, self.W, self.A, self.T, self.D, self.G = name, W, A, T, D, G
        self.pen = pen            # round | flat | nib
        self.Wh = Wh or W         # horizontal weight (optical contrast)
        self.nib = nib            # nib angle (deg) for broad-nib
        self.wmin = wmin          # thinnest nib stroke
        self.loop_w = loop_w
        self.ra_reach = ra_reach
        self.dot = dot
        self.lam_r = lam_r or W * 1.25
        self.tail = tail


def _cap(style):
    return "round" if style.pen == "round" else "butt"


def _mono(path, w, style):
    return stroke(path, w, _cap(style), "round" if style.pen == "round" else "miter")


def _nibw(style):
    """Broad-nib width as a function of stroke direction."""
    a = math.radians(style.nib)

    def f(t):
        # t: unit tangent. Width = full when moving perpendicular to the nib edge
        s = abs(t[0] * math.sin(a) - t[1] * math.cos(a))
        return style.wmin + (style.W - style.wmin) * s
    return f


def _stroke(sk, style, w=None, start="butt", end="butt"):
    """Stroke a Skel with the style's pen. Horizontal runs use Wh."""
    if style.pen == "nib":
        return nibstroke(sk, style)
    from pen import sample
    pts, tans, us, tot = sample(sk, 40)
    # direction-aware weight for optical contrast: horizontals use Wh
    W, Wh = (w or style.W), (w or style.Wh)

    def width(u):
        # find tangent at u
        i = min(len(us) - 1, max(0, int(u * (len(us) - 1))))
        t = tans[i]
        h = abs(t[0])        # 1 = horizontal
        return W + (Wh - W) * (h ** 2)
    if style.pen == "round":
        p = vstroke(sk, width)
        # round ends
        a, b = pts[0], pts[-1]
        wa, wb = width(0), width(1)
        return union(p, circle(a[0], a[1], wa / 2), circle(b[0], b[1], wb / 2))
    return vstroke(sk, width, start=start, end=end)


def nibstroke(sk, style):
    """Broad-nib stroke: the outline is the sweep of a flat nib held at a
    fixed angle, so thick and thin follow the direction of the stroke.
    Built per segment as (path + h) forward and (path - h) back, simplified
    with the non-zero rule, then refitted as Béziers."""
    from pen import sample
    import skia
    a = math.radians(style.nib)
    hx, hy = math.cos(a) * style.W / 2, math.sin(a) * style.W / 2
    parts = []
    for seg in sk.segs:
        one = Skel(*seg[0]); one.segs = [seg]; one.cur = seg[3]
        pts, tans, us, tot = sample(one, 48)
        chain = [(x + hx, y + hy) for x, y in pts] + [(x - hx, y - hy) for x, y in pts[::-1]]
        p = skia.Path(); p.moveTo(*chain[0])
        for q in chain[1:]:
            p.lineTo(*q)
        p.close()
        p.setFillType(skia.PathFillType.kWinding)
        parts.append(simplify(p))
        # nib footprint at the joint keeps segments continuous
        x, y = pts[-1]
        parts.append(poly((x - hx, y - hy), (x + hx, y + hy), (x + hx + 0.01, y + hy + 0.01), (x - hx + 0.01, y - hy + 0.01)))
    return smooth(union(*parts))


def smooth(path, err=0.8):
    """Refit a polygonal outline with cubic Béziers (clean, few points)."""
    from vec import contours, segments
    from pen import fit
    res = []
    for c in contours(path):
        pts = []
        for cmd, ps in segments(c):
            for q in ps:
                pts.append((q.x(), q.y()))
        if len(pts) < 4:
            continue
        # split at corners (direction change > 40deg) to keep crisp nib corners
        n = len(pts)
        corners = [0]
        for i in range(1, n - 1):
            ax, ay = pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]
            bx, by = pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]
            la, lb = math.hypot(ax, ay), math.hypot(bx, by)
            if la < 1e-6 or lb < 1e-6:
                continue
            cosang = (ax * bx + ay * by) / (la * lb)
            if cosang < math.cos(math.radians(40)):
                corners.append(i)
        corners.append(n - 1)
        b = P().M(*pts[0])
        for s, e in zip(corners, corners[1:]):
            seg = pts[s:e + 1]
            if len(seg) <= 2:
                b.L(*seg[-1])
                continue
            for cv in fit(seg, err):
                b.C(*cv[1], *cv[2], *cv[3])
        b.Z()
        res.append(b.path())
    return union(*res)


# ------------------------------------------------------------------ skeletons
def skeleton(st):
    """Return list of (Skel, kind) and dot centres, laid out right-to-left
    from x=0 (right edge of the first alif's stem)."""
    W, A, T, D, G = st.W, st.A, st.T, st.D, st.G
    sk = []
    x = 0.0
    # 1. alif
    xa1 = x - W / 2
    sk.append((Skel(xa1, -A).L(xa1, 0), "v"))
    # 2. lam (initial) -> join -> ra (final)
    xl = xa1 - W - G
    r = st.lam_r
    jx = xl - r - W * 0.9 * st.ra_reach      # where the join meets the ra head
    lam = Skel(xl, -A).L(xl, -r).C(xl, -r * 0.45, xl - r * 0.55, 0, xl - r, 0).L(jx, 0)
    sk.append((lam, "lam"))
    # ra: continues from the join, turns down and sweeps left under the line
    rw = W * 2.6 * st.ra_reach
    tail = st.tail or (jx - rw, D)
    ra = Skel(jx + W * 0.02, 0).C(jx - W * 0.55, 0, jx - W * 0.85, D * 0.18, jx - W * 0.95, D * 0.42) \
        .C(jx - W * 1.1, D * 0.82, tail[0] + W * 0.9, tail[1], tail[0], tail[1])
    sk.append((ra, "ra"))
    # 3. alif: the gap is measured from the ra's body at the baseline
    ra_left = jx - W * 1.0 - W / 2
    xa2 = ra_left - G - W / 2
    sk.append((Skel(xa2, -A).L(xa2, 0), "v"))
    # 4. ya (initial tooth) -> join -> ta marbuta (final loop)
    xy = xa2 - W - G
    ry = W * 0.9
    Lh = T * 1.32 * st.loop_w           # loop height (outer, roughly)
    lr = (Lh - W) / 2                   # loop centre-line radius
    lw = lr * 1.06
    lcx = xy - ry - W * 0.7 - lw
    ya = Skel(xy, -T).L(xy, -ry).C(xy, -ry * .45, xy - ry * .55, 0, xy - ry, 0).L(lcx + lw * 0.15, 0)
    sk.append((ya, "ya"))
    k = 0.5523
    loop = (Skel(lcx + lw * 0.15, 0).C(lcx - lw * 0.30, 0, lcx - lw, -lr * (1 - k), lcx - lw, -lr)
            .C(lcx - lw, -lr - lr * k, lcx - lw * k, -2 * lr, lcx, -2 * lr)
            .C(lcx + lw * k, -2 * lr, lcx + lw, -lr - lr * k, lcx + lw, -lr)
            .C(lcx + lw, -lr * 0.40, lcx + lw * 0.70, -W * 0.10, lcx + lw * 0.30, 0))
    sk.append((loop, "loop"))
    # dots: same pen, a pair under the ya tooth and a pair over the loop
    d = W * st.dot
    gap = W * 0.38
    dy_ya = D * 0.62
    dy_ta = -2 * lr - W / 2 - W * 0.55 - d / 2
    dots = [(xy - (d + gap) / 2, dy_ya), (xy + (d + gap) / 2, dy_ya),
            (lcx - (d + gap) / 2, dy_ta), (lcx + (d + gap) / 2, dy_ta)]
    return sk, dots, d


def dot_shape(st, cx, cy, d):
    if st.pen == "round":
        return circle(cx, cy, d / 2)
    if st.pen == "nib":
        # one short nib stroke: a parallelogram whose angle is the nib's
        a = math.radians(st.nib)
        hx, hy = math.cos(a) * st.W / 2, math.sin(a) * st.W / 2
        l = d * 0.62
        return smooth(union(poly((cx - l / 2 - hx, cy - hy), (cx - l / 2 + hx, cy + hy), (cx + l / 2 + hx, cy + hy), (cx + l / 2 - hx, cy - hy))))
    return rect(cx - d / 2, cy - d / 2, d, d)


def parts(st):
    """Each letter group of «الراية» on its own, plus its dots.
    keys: alif1, lamra, ra, alif2, yata, ya_dots, ta_dots"""
    sk, dots, d = skeleton(st)
    out = {}
    names = ["alif1", "lam", "ra", "alif2", "ya", "loop"]
    for (s, kind), nm in zip(sk, names):
        out[nm] = _stroke(s, st)
    out["lamra"] = union(out["lam"], out["ra"])
    out["yata"] = union(out["ya"], out["loop"])
    out["ya_dots"] = union(*[dot_shape(st, x, y, d) for x, y in dots[:2]])
    out["ta_dots"] = union(*[dot_shape(st, x, y, d) for x, y in dots[2:]])
    out["skel"] = {nm: s for (s, kind), nm in zip(sk, names)}
    return out


def word(st):
    """«الراية» as (letters_path, dots_path)."""
    sk, dots, d = skeleton(st)
    parts = []
    for s, kind in sk:
        if st.pen == "flat" and kind == "v":
            parts.append(_stroke(s, st))
        else:
            parts.append(_stroke(s, st))
    letters = union(*parts)
    dp = union(*[dot_shape(st, x, y, d) for x, y in dots])
    return letters, dp


# ------------------------------------------------------------------ styles
STYLES = {
    # light monoline, round pen: a technical-drawing line
    "line": Style("line", W=46, A=560, T=190, D=200, G=96, pen="round", dot=1.35),
    # heavy, flat pen, tight: built mass
    "mass": Style("mass", W=118, A=520, T=210, D=190, G=86, pen="flat", Wh=104, dot=1.0, lam_r=120, loop_w=1.34),
    # medium, flat ends, horizontals slightly lighter (optical)
    "sans": Style("sans", W=88, A=560, T=200, D=200, G=96, pen="flat", Wh=76, dot=1.05),
    # high contrast: heavy uprights, fine joins (a signature)
    "contrast": Style("contrast", W=122, A=600, T=205, D=215, G=84, pen="flat", Wh=40, dot=0.86, lam_r=150),
    # round, medium: calm and institutional
    "round": Style("round", W=82, A=540, T=195, D=195, G=100, pen="round", dot=1.25),
}


# ------------------------------------------------------------------ angular kufic
def angular(W=92, A=560, T=210, D=200, G=92, c=None):
    """Geometric kufic: straight strokes, 45° turns, square dots.
    Same structure and metrics rules as the curved styles."""
    c = c or W * 1.1            # chamfer at every turn
    s = []
    xa1 = -W / 2
    s.append(P().M(xa1, -A).L(xa1, 0).path())
    xl = xa1 - W - G
    jx = xl - W * 2.2
    s.append(P().M(xl, -A).L(xl, -c).L(xl - c, 0).L(jx, 0).path())
    # ra: a short run, then a 45° drop under the line, finishing level
    rx = jx
    ra = P().M(jx + 1, 0).L(rx - W * 0.4, 0).L(rx - W * 0.4 - D * 0.75, D * 0.75).L(rx - W * 0.4 - D * 0.75 - W * 0.55, D * 0.75).path()
    s.append(ra)
    ra_left = rx - W * 0.4 - W / 2
    xa2 = ra_left - G - W / 2 - W * 0.2
    s.append(P().M(xa2, -A).L(xa2, 0).path())
    xy = xa2 - W - G
    Lh = T * 1.45
    lw = Lh * 0.92                         # loop width (centre-line)
    lh = Lh - W                            # loop height (centre-line)
    lx1 = xy - W * 1.6                     # loop right side
    lx0 = lx1 - lw
    k = W * 0.9
    s.append(P().M(xy, -T).L(xy, -c).L(xy - c, 0).L(lx1, 0).path())
    loop = P().M(lx1, 0).L(lx0 + k, 0).L(lx0, -k).L(lx0, -lh + k).L(lx0 + k, -lh).L(lx1 - k, -lh).L(lx1, -lh + k).L(lx1, 0).Z().path()
    s.append(loop)
    letters = union(*[stroke(p, W, "butt", "miter", 4) for p in s])
    d = W
    gap = W * 0.38
    cx = (lx0 + lx1) / 2
    dots = [(xy - (d + gap) / 2, D * 0.62), (xy + (d + gap) / 2, D * 0.62),
            (cx - (d + gap) / 2, -lh - W / 2 - W * 0.55 - d / 2), (cx + (d + gap) / 2, -lh - W / 2 - W * 0.55 - d / 2)]
    dp = [rect(x - d / 2, y - d / 2, d, d) for x, y in dots]
    parts = {"alif1": stroke(s[0], W, "butt", "miter"), "lamra": union(stroke(s[1], W, "butt", "miter", 4), stroke(s[2], W, "butt", "miter", 4)),
             "alif2": stroke(s[3], W, "butt", "miter"), "yata": union(stroke(s[4], W, "butt", "miter", 4), stroke(s[5], W, "butt", "miter", 4)),
             "ya_dots": union(*dp[:2]), "ta_dots": union(*dp[2:])}
    parts["centre"] = s
    parts["W"] = W
    parts["dot_rects"] = [(x - d / 2, y - d / 2, d) for x, y in dots]
    return letters, union(*dp), parts
