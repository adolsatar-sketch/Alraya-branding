"""The five ALRAYA logo directions.

Each direction builds layered geometry. A layer is (geometry, role) where
role is 'p' (primary: indigo) or 'a' (accent: maroon). Colour schemes are
applied at render time, so every variant is the same drawing.
"""
import math
from shapely.ops import unary_union, transform
from shapely import affinity
from geo import (text, rect, poly, circle, ring, diamond, arc_warp, norm,
                 bounds, path_d)

AR_PLEX = "ibm-plex-sans-arabic-arabic-700-normal.woff2"
AR_NASKH = "amiri-arabic-700-normal.woff2"
AR_GEO = "alexandria-arabic-800-normal.woff2"
AR_KUFI = "reem-kufi-arabic-700-normal.woff2"
EN_BOLD = "archivo-latin-700-normal.woff2"
EN_X = "archivo-latin-800-normal.woff2"
EN_SEMI = "archivo-latin-600-normal.woff2"


def U(*gs):
    return unary_union([g for g in gs if g is not None and not g.is_empty])


def shift(layers, dx, dy, s=1.0):
    return [(affinity.translate(affinity.scale(L[0], s, s, origin=(0, 0)), dx, dy),) + tuple(L[1:])
            for L in layers]


def tag(layers, part):
    return [(L[0], L[1], part) for L in layers]


def lbounds(layers):
    return bounds(*[L[0] for L in layers])


def to_origin(layers):
    b = lbounds(layers)
    return shift(layers, -b[0], -b[1])


def size(layers):
    b = lbounds(layers)
    return b[2] - b[0], b[3] - b[1]


def en_word(s, h, font=EN_BOLD, track=0.18):
    """Latin caps scaled so cap height == h, bbox at origin."""
    g, _ = text(s, font, 1000, track=track)
    b = g.bounds
    k = h / (b[3] - b[1])
    return norm(affinity.scale(g, k, k, origin=(0, 0)))


def ar_word(s, h, font=AR_PLEX):
    """Arabic run scaled so the alif of the font is h tall. Bbox at origin."""
    g, _ = text(s, font, 1000)
    r, _ = text("ا", font, 1000)
    rb = r.bounds
    k = h / (rb[3] - rb[1])
    return norm(affinity.scale(g, k, k, origin=(0, 0)))


def text_block(ar, en, gap):
    """Arabic over English, right-aligned (RTL reading start)."""
    aw, ah = ar.bounds[2], ar.bounds[3]
    ew, eh = en.bounds[2], en.bounds[3]
    W = max(aw, ew)
    return [(affinity.translate(ar, W - aw, 0), "p", "ar"),
            (affinity.translate(en, W - ew, ah + gap), "p", "en")]


def beside(text_layers, mark_layers, gap, valign=0.5):
    """Mark on the right (where Arabic reading starts), text on its left."""
    tw, th = size(text_layers)
    mw, mh = size(mark_layers)
    H = max(th, mh)
    t = shift(to_origin(text_layers), 0, (H - th) * valign)
    m = shift(to_origin(mark_layers), tw + gap, (H - mh) * 0.5)
    return t + m


# ================================================================ 01 grid
# Square kufic: every stroke is one module wide, every gap one module.
KUFIC = {"accents": [(10, 8), (12, 8), (12, 0), (14, 0)], "W": 15, "H": 9}


def _kufic_cells():
    cells = set()

    def v(c, r0, r1):
        cells.update((c, r) for r in range(r0, r1 + 1))

    def h(r, c0, c1):
        cells.update((c, r) for c in range(c0, c1 + 1))
    v(0, 0, 6)                         # alif
    v(2, 0, 6); h(6, 2, 4)             # lam, joined to ra
    v(4, 5, 8); h(8, 4, 6)             # ra: drops under the line, tail to the left
    v(8, 0, 6)                         # alif
    v(10, 4, 6); h(6, 10, 12)          # ya, joined to ta
    v(12, 2, 6); v(14, 2, 6); h(2, 12, 14); h(6, 12, 14)   # ta marbuta: a square loop
    return cells


def grid_mark(m=100):
    W = KUFIC["W"]
    cell = lambda c, r: rect((W - 1 - c) * m, r * m, m, m)
    body = U(*[cell(c, r) for c, r in _kufic_cells()])
    dots = U(*[cell(c, r) for c, r in KUFIC["accents"]])
    return [(body, "p"), (dots, "a")]


def grid_lockup():
    mk = grid_mark()
    w, h = size(mk)
    en = en_word("ALRAYA", 100 * 0.78, EN_BOLD, track=0.62)
    en = affinity.translate(en, w - en.bounds[2], h + 100 * 0.9)
    return tag(mk, "mk") + [(en, "p", "en")]


def grid_icon():
    return grid_mark()


# ================================================================ 02 seal
def seal_symbol(R=300):
    """The alif (first letter) passing through the loop of ta marbuta
    (last letter)."""
    loop = ring(0, 0, 0.50 * R, 0.30 * R)
    bw = 0.20 * R
    alif = rect(-bw / 2, -0.92 * R, bw, 1.84 * R)
    return loop, alif


def seal_badge(R=500, lettered=True):
    rin = 0.64 * R
    band = ring(0, 0, R, rin)
    lw = 0.022 * R
    inner_line = ring(0, 0, rin - 0.05 * R, rin - 0.05 * R - lw)
    mid = (R + rin) / 2
    if lettered:
        ar = ar_word("الراية", 0.17 * R, AR_NASKH)
        b = ar.bounds
        k = 0.30 * R / b[3]
        ar = affinity.scale(ar, k, k, origin=(0, 0))
        b = ar.bounds
        ar = affinity.translate(ar, -b[2] / 2, -b[3] * 0.52)
        ar = arc_warp(ar, mid, top=True)
        en = en_word("ALRAYA", 0.115 * R, EN_BOLD, track=0.5)
        eb = en.bounds
        en = affinity.translate(en, -eb[2] / 2, -eb[3] / 2)
        en = arc_warp(en, mid, top=False)
        seps = U(diamond(-mid, 0, 0.075 * R), diamond(mid, 0, 0.075 * R))
        band = band.difference(U(ar, en, seps))
    loop, alif = seal_symbol(rin * 0.86)
    return [(U(band, inner_line, loop), "p"), (alif, "a")]


def seal_lockup():
    bd = seal_badge()
    bw, bh = size(bd)
    ar = ar_word("الراية", bh * 0.40, AR_NASKH)
    en = en_word("ALRAYA", bh * 0.105, EN_BOLD, track=0.40)
    tb = text_block(ar, en, bh * 0.10)
    rule = rect(0, 0, bh * 0.010, bh * 0.70)
    out = beside(tb, [(rule, "a", "rule")], bh * 0.09)
    return beside(out, tag(bd, "mk"), bh * 0.09)


def seal_icon():
    return seal_badge(lettered=False)


# ================================================================ 03 fold
def fold_mark(w=200, stem=560, tail=540, ang=45):
    """One band folded once: the stem shows its face (indigo), the folded
    tail shows its back (maroon). The band draws a ra (ر)."""
    a = math.radians(ang)
    dx, dy = -math.sin(a), math.cos(a)
    ux, uy = dx, 1 + dy
    n = math.hypot(ux, uy)
    ux, uy = ux / n, uy / n
    px, py = w, stem
    big = 10000
    strip = rect(0, 0, w, stem + big)
    nx, ny = -uy, ux
    if ny > 0:
        nx, ny = -nx, -ny
    hp = poly((px + ux * big + nx * big, py + uy * big + ny * big),
              (px - ux * big + nx * big, py - uy * big + ny * big),
              (px - ux * big, py - uy * big), (px + ux * big, py + uy * big))
    st = strip.intersection(hp)
    below = strip.difference(hp)

    def refl(x, y, z=None):
        rx, ry = x - px, y - py
        d = rx * ux + ry * uy
        return px + 2 * d * ux - rx, py + 2 * d * uy - ry
    tl = transform(refl, below)
    ex, ey = px + dx * tail, py + dy * tail
    qx, qy = -dy, dx
    cut = poly((ex + qx * big, ey + qy * big), (ex - qx * big, ey - qy * big),
               (ex - qx * big - dx * big, ey - qy * big - dy * big),
               (ex + qx * big - dx * big, ey + qy * big - dy * big))
    tl = tl.intersection(cut)
    return [(st, "p"), (tl, "a")]


def fold_lockup():
    mk = fold_mark()
    mw, mh = size(mk)
    ar = ar_word("الراية", mh * 0.40, AR_PLEX)
    en = en_word("ALRAYA", mh * 0.075, EN_BOLD, track=0.55)
    tb = text_block(ar, en, mh * 0.10)
    return beside(tb, tag(mk, "mk"), mh * 0.10, valign=0.28)


def fold_icon():
    return fold_mark()


# ================================================================ 04 angle
def angle_mark(S=600):
    """A Latin A whose right leg is an Arabic alif, standing taller than the
    apex. Leg and base meet at a right angle."""
    t = 0.19 * S
    W = 0.74 * S
    top = 0.20 * S
    alif = rect(W - t, 0, t, S)
    ang = math.atan2(S - top, W - t)
    hx = t / math.sin(ang)
    slope = poly((W - t, top), (W - t, top + hx * math.tan(ang)), (hx, S), (0, S))
    cb_y = top + (S - top) * 0.56
    bar = rect(0, cb_y, W - t, t * 0.78).intersection(poly((W - t, top), (W - t, S), (0, S)))
    return [(U(alif, slope), "p"), (bar, "a")]


def angle_lockup():
    mk = angle_mark()
    mw, mh = size(mk)
    ar = ar_word("الراية", mh * 0.62, AR_GEO)
    en = en_word("ALRAYA", mh * 0.13, EN_X, track=0.42)
    tb = text_block(ar, en, mh * 0.12)
    return beside(tb, tag(mk, "mk"), mh * 0.20)


def angle_icon():
    return angle_mark()


# ================================================================ 05 lock
def lock_mark(S=600, t=150, g=26):
    """Two identical pieces, each a kufic lam (ل), turned to face each other
    and locked into one square around an open centre."""
    a = U(rect(S - t, t + g, t, S - t - g), rect(0, S - t, S - t, t))
    b = affinity.rotate(a, 180, origin=(S / 2, S / 2))
    return [(a, "p"), (b, "a")]


def lock_lockup():
    mk = lock_mark()
    mw, mh = size(mk)
    ar = ar_word("الراية", mh * 0.62, AR_KUFI)
    en = en_word("ALRAYA", mh * 0.12, EN_BOLD, track=0.50)
    tb = text_block(ar, en, mh * 0.13)
    return beside(tb, tag(mk, "mk"), mh * 0.22)


def lock_icon():
    return lock_mark()


DIRS = [
    ("01", "grid", grid_lockup, grid_icon),
    ("02", "seal", seal_lockup, seal_icon),
    ("03", "fold", fold_lockup, fold_icon),
    ("04", "angle", angle_lockup, angle_icon),
    ("05", "lock", lock_lockup, lock_icon),
]

SCHEMES = {
    "full": {"p": "#262E5D", "a": "#7D161A"},
    "rev": {"p": "#FFFFFF", "a": "#D7A3A5"},
    "mono": {"p": "#262E5D", "a": "#262E5D"},
    "black": {"p": "#000000", "a": "#000000"},
    "white": {"p": "#FFFFFF", "a": "#FFFFFF"},
}


def svg(layers, colors=None, pad=0.06, bg=None, sq=False):
    colors = colors or SCHEMES["full"]
    layers = to_origin(layers)
    w, h = size(layers)
    p = max(w, h) * pad
    if sq:
        s = max(w, h)
        layers = shift(layers, (s - w) / 2, (s - h) / 2)
        w = h = s
    vb = f"{-p:.1f} {-p:.1f} {w + 2 * p:.1f} {h + 2 * p:.1f}"
    body = "".join(f'<path fill="{colors[L[1]]}" d="{path_d(L[0])}"/>' for L in layers)
    bgr = (f'<rect x="{-p:.1f}" y="{-p:.1f}" width="{w+2*p:.1f}" height="{h+2*p:.1f}" fill="{bg}"/>'
           if bg else "")
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}">{bgr}{body}</svg>'
