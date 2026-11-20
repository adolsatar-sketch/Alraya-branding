"""ALRAYA identity v3 — six logo directions, drawn as vector paths.

Every direction exposes build() -> dict of named artworks. An artwork is a
list of layers (path, role) where role is:
  'p' primary (indigo), 'a' accent (maroon), 'h' hairline/detail (primary).
Colour schemes are applied at export time, so every version is the same
drawing.
"""
import math
from vec import (P, rect, rrect, circle, ellipse, diamond, poly, union, diff, inter,
                 stroke, outline, move, scale, rotate, mirror_x, tf, bounds, text, caps,
                 to_origin, size, simplify)
from pen import Skel, vstroke, profile

EN = "archivo-latin-700-normal.woff2"
EN_SB = "archivo-latin-600-normal.woff2"
AR_PLEX = "ibm-plex-sans-arabic-arabic-700-normal.woff2"
AR_PLEX_M = "ibm-plex-sans-arabic-arabic-500-normal.woff2"
AR_NASKH = "amiri-arabic-700-normal.woff2"
AR_GEO = "alexandria-arabic-800-normal.woff2"
DESC_AR = "مقاولات عامة واستشارات هندسية"
DESC_EN = "GENERAL CONTRACTING & ENGINEERING CONSULTANCY"
NIB = -28


# ================================================================== helpers
def L(*pairs):
    return [(p, r) for p, r in pairs if p is not None and p.countVerbs()]


def lb(layers):
    return bounds(*[p for p, _ in layers])


def lsize(layers):
    x0, y0, x1, y1 = lb(layers)
    return x1 - x0, y1 - y0


def lmove(layers, dx, dy, s=1.0):
    return [(move(scale(p, s), dx, dy), r) for p, r in layers]


def lorigin(layers):
    x0, y0, _, _ = lb(layers)
    return lmove(layers, -x0, -y0)


def lheight(layers, h):
    w0, h0 = lsize(layers)
    return lorigin(lmove(lorigin(layers), 0, 0, h / h0))


def lwidth(layers, w):
    w0, h0 = lsize(layers)
    return lorigin(lmove(lorigin(layers), 0, 0, w / w0))


def mono(layers, role="p"):
    return [(p, role) for p, _ in layers]


def flat(layers):
    return union(*[p for p, _ in layers])


def arabic(s, font, alif_h):
    """Outlined Arabic text scaled so the font's alif is alif_h tall."""
    g, _ = text(s, font, 1000)
    a, _ = text("ا", font, 1000)
    x0, y0, x1, y1 = bounds(a)
    k = alif_h / (y1 - y0)
    return to_origin(scale(g, k))


def latin(s, cap_h, track=0.45, font=EN):
    return caps(s, font, cap_h, track)


def right_align(rows, gap):
    """Stack layer-lists vertically, right-aligned (Arabic reading start)."""
    W = max(lsize(r)[0] for r in rows)
    out, y = [], 0
    for r in rows:
        r = lorigin(r)
        w, h = lsize(r)
        out += lmove(r, W - w, y)
        y += h + gap
    return out


def centre(rows, gap):
    W = max(lsize(r)[0] for r in rows)
    out, y = [], 0
    for r in rows:
        r = lorigin(r)
        w, h = lsize(r)
        out += lmove(r, (W - w) / 2, y)
        y += h + gap
    return out


def beside(left, right, gap, valign=0.5):
    """left block | gap | right block (the symbol sits on the right, where
    Arabic reading starts)."""
    left, right = lorigin(left), lorigin(right)
    lw, lh = lsize(left)
    rw, rh = lsize(right)
    H = max(lh, rh)
    return lmove(left, 0, (H - lh) * valign) + lmove(right, lw + gap, (H - rh) * 0.5)


def name_block(ar, en_h, gap, en_track=0.5):
    """Arabic name (layers) over ALRAYA, right aligned."""
    en = [(latin("ALRAYA", en_h, en_track), "p")]
    return right_align([ar, en], gap)


def arc_map(path, R, top=True, steps=6):
    """Bend a horizontal run (centred on x=0, baseline y=0) around a circle.
    Curves are split into short pieces and their control points mapped, so
    the result stays a clean Bézier outline."""
    from vec import segments
    import skia

    def f(x, y):
        if top:
            a = -math.pi / 2 + x / R
            r = R - y
        else:
            a = math.pi / 2 - x / R
            r = R + y
        return r * math.cos(a), r * math.sin(a)

    out = skia.Path()
    cur = None
    for cmd, pts in segments(path):
        q = [(p.x(), p.y()) for p in pts]
        if cmd == "M":
            cur = q[0]; out.moveTo(*f(*cur))
        elif cmd == "Z":
            out.close()
        else:
            if cmd == "L":
                a, b = cur, q[0]
                c = [a, (a[0] + (b[0] - a[0]) / 3, a[1] + (b[1] - a[1]) / 3),
                     (a[0] + 2 * (b[0] - a[0]) / 3, a[1] + 2 * (b[1] - a[1]) / 3), b]
            elif cmd == "Q":
                a, c1, b = cur, q[0], q[1]
                c = [a, (a[0] + 2 / 3 * (c1[0] - a[0]), a[1] + 2 / 3 * (c1[1] - a[1])),
                     (b[0] + 2 / 3 * (c1[0] - b[0]), b[1] + 2 / 3 * (c1[1] - b[1])), b]
            else:
                c = [cur] + q
            n = max(1, int(math.hypot(c[3][0] - c[0][0], c[3][1] - c[0][1]) / (R * 0.12)))
            pieces = _split(c, n)
            for pc in pieces:
                out.cubicTo(*f(*pc[1]), *f(*pc[2]), *f(*pc[3]))
            cur = q[-1]
    return simplify(out)


def _split(c, n):
    res = []
    rest = c
    for i in range(n, 1, -1):
        t = 1 / i
        a, b = _dc(rest, t)
        res.append(a)
        rest = b
    res.append(rest)
    return res


def _dc(c, t):
    p0, p1, p2, p3 = c
    l = lambda a, b: (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
    a = l(p0, p1); b = l(p1, p2); cc = l(p2, p3)
    d = l(a, b); e = l(b, cc); m = l(d, e)
    return (p0, a, d, m), (m, e, cc, p3)


def seal_ring(R, ar_layers_path, en_path, sep, inner=0.70, line=0.022):
    pass


# ================================================================== 01 العقدة
def d01_symbol(g=30):
    """«را»: the alif (plan, a straight axis) stands on the sweep of the ra
    (execution). Where they meet, the ra passes in front: one joint, two
    members."""
    w = 170
    ra = vstroke(Skel(640, 250).L(640, 560).C(640, 800, 470, 930, -50, 950),
                 profile((0, w), (0.42, w), (0.78, 100), (1, 4)), start=NIB, end="taper")
    alif = vstroke(Skel(330, -10).L(330, 1060), profile((0, w * 0.96), (1, w)), start=NIB)
    alif = diff(alif, stroke(ra, g * 2))
    return L((alif, "p"), (ra, "a"))


def d01_word(h):
    return [(arabic("الراية", AR_PLEX, h), "p")]


# ================================================================== 02 من الخط إلى الكتلة
def d02_letters(w=86, A=-600):
    hw = w / 2
    s = []
    s.append(stroke(P().M(1380, A).L(1380, hw).path(), w))
    xl, r = 1200, 110
    s.append(stroke(P().M(xl, A).L(xl, -r).C(xl, -r * .45, xl - r * .55, 0, xl - r, 0).L(1000, 0).path(), w))
    s.append(stroke(P().M(1012, 0).C(962, 0, 946, 40, 941, 95).C(931, 190, 871, 250, 760, 262).path(), w))
    s.append(stroke(P().M(660, A).L(660, hw).path(), w))
    xy = 470
    s.append(stroke(P().M(xy, -230).L(xy, -r).C(xy, -r * .45, xy - r * .55, 0, xy - r, 0).L(266, 0).path(), w))
    R = 132
    cx, cy = 196, -R
    s.append(diff(circle(cx, cy, R + hw), circle(cx, cy, R - hw)))
    dz = w
    dots = union(rect(xy - dz - 16, 128, dz, dz), rect(xy + 16, 128, dz, dz),
                 rect(cx - dz - 16, cy - R - hw - 60 - dz, dz, dz), rect(cx + 16, cy - R - hw - 60 - dz, dz, dz))
    return union(*s), dots


D02_CUT = ((1480, 40), (40, -720))   # the rising line between drawing and building


def d02_cut_half():
    (x0, y0), (x1, y1) = D02_CUT
    return poly((x0, y0), (x0 + 400, y0 + 3000), (x1 - 400, y1 + 3000), (x1, y1))


def d02_word(hair=7):
    body, dots = d02_letters()
    full = union(body, dots)
    mass = inter(full, d02_cut_half())
    drawn = diff(full, d02_cut_half())
    return L((mass, "p"), (outline(drawn, hair), "h"))


def d02_solid():
    body, dots = d02_letters()
    return L((union(body, dots), "p"))


def _ta_parts(w=86):
    hw, R = w / 2, 132
    cx, cy = 196, -R
    ring_ = diff(circle(cx, cy, R + hw), circle(cx, cy, R - hw))
    dz = w
    dots = union(rect(cx - dz - 16, cy - R - hw - 60 - dz, dz, dz), rect(cx + 16, cy - R - hw - 60 - dz, dz, dz))
    return union(ring_, dots)


def d02_symbol():
    """The ta marbuta with its two dots, lifted from the word: half drawn,
    half built — the same rising cut as the word."""
    ta = _ta_parts()
    half = poly((420, -640), (420, 60), (-30, 60), (-30, 60))
    return L((inter(ta, half), "p"), (outline(diff(ta, half), 7), "h"))


def d02_symbol_solid():
    return L((_ta_parts(), "p"))


# ================================================================== 03 الفراغ الحامل
def squircle(x, y, s, r=0.20):
    k = s * r; h = k * 0.30
    return (P().M(x + k, y).L(x + s - k, y).C(x + s - h, y, x + s, y + h, x + s, y + k).L(x + s, y + s - k)
            .C(x + s, y + s - h, x + s - h, y + s, x + s - k, y + s).L(x + k, y + s)
            .C(x + h, y + s, x, y + s - h, x, y + s - k).L(x, y + k).C(x, y + h, x + h, y, x + k, y).Z().path())


def d03_channel():
    sk = Skel(585, -60).L(585, 330).C(585, 620, 430, 790, 120, 850).C(40, 865, -20, 870, -80, 872)
    return vstroke(sk, profile((0, 128), (0.45, 128), (0.86, 70), (1, 46)))


def d03_symbol():
    tile = squircle(0, 0, 1000)
    return L((diff(tile, d03_channel()), "p"))


# ================================================================== 04 التوقيع العربي
def d04_letters(V=118, Hh=58, A=-680):
    s = []
    s.append(vstroke(Skel(1390, A).L(1390, 0), profile((0, V * .92), (.5, V), (1, V * .86)), start=NIB))
    s.append(vstroke(Skel(1195, A).L(1195, -120).C(1195, -45, 1160, 0, 1090, 0).L(990, 0),
                     profile((0, V * .92), (.62, V), (.80, Hh), (1, Hh)), start=NIB))
    s.append(vstroke(Skel(1012, 0).C(972, 0, 950, 14, 945, 58).C(937, 172, 860, 268, 700, 300)
                     .C(620, 315, 560, 316, 500, 312),
                     profile((0, Hh), (.13, V * .95), (.40, V * 1.05), (.85, 22), (1, 4)), end="taper"))
    s.append(vstroke(Skel(735, A + 30).L(735, 0), profile((0, V * .92), (.5, V), (1, V * .86)), start=NIB))
    xy = 540
    s.append(vstroke(Skel(xy, -230).L(xy, -110).C(xy, -40, xy - 35, 0, xy - 100, 0).L(300, 0),
                     profile((0, V * .9), (.45, V * .95), (.72, Hh), (1, Hh)), start=NIB))
    loop = (Skel(305, 0).C(170, 0, 90, -60, 90, -165).C(90, -270, 170, -330, 245, -330)
            .C(330, -330, 390, -270, 390, -185).C(390, -90, 340, -28, 290, -8))
    s.append(vstroke(loop, profile((0, Hh), (.22, V * .95), (.48, 26), (.74, V * .9), (1, Hh * .9))))
    dot = lambda x, y: diamond(x, y, 96, 112)
    dots = union(dot(xy - 62, 150), dot(xy + 58, 150), dot(190, -430), dot(300, -430))
    return union(*s), dots


def d04_word():
    b, dd = d04_letters()
    return L((b, "p"), (dd, "a"))


def d04_symbol():
    """«ية» lifted from the word: the tooth of ya, the loop of ta and their
    four dots — the only dots in the name."""
    b, dd = d04_letters()
    box = rect(40, -520, 628, 780)
    return L((inter(b, box), "p"), (inter(dd, box), "a"))


# ================================================================== 05 نقطة التحول
def d05_symbol(w=178, spread=300, jy=470, H=840, gap=28, dsz=166, dy=152):
    """Y of ALRAYA and ya of الراية: two paths meet in one point and leave as
    one line. The two dots of ya sit under it. The right path tucks into the
    left one: that seam is the turning point."""
    top = rect(-3000, -3000, 6000, 3000)
    left = diff(stroke(P().M(-spread, 0).L(0, jy).L(0, H).path(), w, "butt", "miter", 4), top)
    right = diff(stroke(P().M(spread, 0).L(0, jy).path(), w, "butt"), top)
    right = diff(right, stroke(left, gap * 2), rect(-w / 2 - gap, jy, w + 2 * gap, H))
    stemcut = rect(-3000, H, 6000, 3000)
    left = diff(left, stemcut)
    dots = union(diamond(-dsz * 0.6, H + dy, dsz), diamond(dsz * 0.6, H + dy, dsz))
    return L((left, "p"), (right, "p"), (dots, "a"))


# ================================================================== 06 ختم الراية
def d06_core(R=300, g=24):
    """Alif through the loop of ta marbuta: first letter and last letter,
    woven — the alif passes over the loop at the bottom and under it at the top."""
    loop = vstroke(Skel(0, -0.40 * R).C(0.30 * R, -0.40 * R, 0.46 * R, -0.18 * R, 0.46 * R, 0.08 * R)
                   .C(0.46 * R, 0.36 * R, 0.25 * R, 0.52 * R, 0, 0.52 * R)
                   .C(-0.25 * R, 0.52 * R, -0.46 * R, 0.36 * R, -0.46 * R, 0.08 * R)
                   .C(-0.46 * R, -0.18 * R, -0.30 * R, -0.40 * R, 0.0, -0.40 * R),
                   profile((0, 0.07 * R), (0.25, 0.20 * R), (0.5, 0.09 * R), (0.75, 0.20 * R), (1, 0.07 * R)))
    alif = vstroke(Skel(0, -0.98 * R).L(0, 0.92 * R), profile((0, 0.17 * R), (1, 0.19 * R)), start=NIB)
    top_half = rect(-R, -R * 2, 2 * R, R * 2.08)
    a_front = diff(alif, inter(stroke(loop, g * 2), top_half))
    loop_c = diff(loop, diff(stroke(alif, g * 2), top_half))
    return loop_c, a_front


def d06_badge(R=500, lettered=True):
    rin = 0.66 * R
    band = diff(circle(0, 0, R), circle(0, 0, rin))
    lw = 0.016 * R
    keep = []
    mid = (R + rin) / 2
    if lettered:
        ar = arabic("الراية", AR_NASKH, 0.17 * R)
        x0, y0, x1, y1 = bounds(ar)
        k = 0.31 * R / (y1 - y0)
        ar = scale(ar, k)
        x0, y0, x1, y1 = bounds(ar)
        ar = move(ar, -(x0 + x1) / 2, -(y0 + y1) / 2 - 0.004 * R)
        ar = arc_map(ar, mid, True)
        en = latin("ALRAYA", 0.105 * R, 0.62)
        x0, y0, x1, y1 = bounds(en)
        en = move(en, -(x0 + x1) / 2, -(y0 + y1) / 2)
        en = arc_map(en, mid, False)
        seps = union(diamond(-mid, 0, 0.07 * R, 0.09 * R), diamond(mid, 0, 0.07 * R, 0.09 * R))
        band = diff(band, ar, en, seps)
    inner = diff(circle(0, 0, rin - 0.055 * R), circle(0, 0, rin - 0.055 * R - lw))
    loop, alif = d06_core(rin * 0.88)
    return L((union(band, inner, loop), "p"), (alif, "a"))


def d06_symbol():
    loop, alif = d06_core(300)
    return L((loop, "p"), (alif, "a"))


# ================================================================== words & lockups
def ar_kerned(font, alif_h, groups=("ا", "لر", "ا", "ية"), gaps=None):
    """«الراية» set group by group (the letters that join stay joined), with
    the space between groups set by eye instead of the font's defaults."""
    a, _ = text("ا", font, 1000)
    x0, y0, x1, y1 = bounds(a)
    k = alif_h / (y1 - y0)
    gaps = gaps or [0.0] * (len(groups) - 1)
    x = 0
    out = []
    # Arabic runs right to left: place the first group on the right
    shapes = [text(g, font, 1000) for g in groups]
    total = []
    cur = 0
    for i, (p, adv) in enumerate(shapes):
        gx0, _, gx1, _ = bounds(p)
        out.append(move(p, -gx1 + cur, 0))
        if i < len(shapes) - 1:
            nx0, _, nx1, _ = bounds(shapes[i + 1][0])
            cur = cur - (gx1 - gx0) - gaps[i] * 1000
    return to_origin(scale(union(*out), k))


WORD = {
    "01": dict(font=AR_PLEX, gaps=(0.075, 0.07, 0.065)),
    "03": dict(font=AR_GEO, gaps=(0.07, 0.06, 0.06)),
    "05": dict(font="reem-kufi-arabic-700-normal.woff2", gaps=(0.06, 0.05, 0.05)),
    "06": dict(font=AR_NASKH, gaps=(0.06, 0.05, 0.04)),
}


def word(n, alif_h):
    if n == "02":
        return lheight(d02_word(), alif_h * 1.62)
    if n == "04":
        return lheight(d04_word(), alif_h * 1.64)
    w = WORD[n]
    return [(ar_kerned(w["font"], alif_h, gaps=w["gaps"]), "p")]


def en_name(cap_h, track=0.48):
    """ALRAYA with pair spacing adjusted by eye (the open A–Y and L–R pairs)."""
    letters = "ALRAYA"
    adj = {("L", "R"): -0.05, ("A", "Y"): -0.10, ("Y", "A"): -0.10, ("R", "A"): -0.02, ("A", "L"): -0.03}
    x = 0
    out = []
    for i, ch in enumerate(letters):
        g = caps(ch, EN, cap_h, 0)
        gw, _ = size(g)
        out.append(move(g, x, 0))
        if i < len(letters) - 1:
            x += gw + cap_h * (track + adj.get((ch, letters[i + 1]), 0))
    return union(*out)


def desc(h_ar):
    """Arabic and English descriptor lines."""
    ar = arabic(DESC_AR, AR_PLEX_M, h_ar)
    en = caps(DESC_EN, EN_SB, h_ar * 0.42, 0.16)
    return ar, en


SYMBOL = {
    "01": d01_symbol, "02": d02_symbol, "03": d03_symbol,
    "04": d04_symbol, "05": d05_symbol, "06": lambda: d06_badge(lettered=False),
}


def symbol(n):
    return lorigin(SYMBOL[n]())


def lockups(n):
    """All compositions for one direction (layer lists at origin)."""
    out = {}
    sym = symbol(n)
    S = 1000
    sym = lheight(sym, S)
    out["symbol"] = sym
    if n in ("02", "04"):
        wd = word(n, 520)
        ww, wh = lsize(wd)
        en = [(en_name(wh * 0.085), "p")]
        out["primary_ar"] = wd
        out["ar_en"] = right_align([wd, en], wh * 0.16)
        hz_sym = lheight(sym, wh * 0.95)
        out["horizontal"] = beside(out["ar_en"], hz_sym, wh * 0.22, 0.5)
        out["stacked"] = centre([lheight(sym, wh * 0.85), wd, en], wh * 0.13)
    elif n == "06":
        badge = lorigin(d06_badge())
        out["circular"] = badge
        wd = word(n, 330)
        ww, wh = lsize(wd)
        en = [(en_name(wh * 0.16, 0.5), "p")]
        block = right_align([wd, en], wh * 0.22)
        bh = lsize(badge)[1]
        rule = [(rect(0, 0, bh * 0.008, bh * 0.66), "a")]
        out["horizontal"] = beside(beside(block, rule, bh * 0.08), lheight(badge, bh), bh * 0.08)
        out["primary_ar"] = beside(wd, lheight(badge, wh * 1.25), wh * 0.3)
        out["ar_en"] = out["horizontal"]
        out["stacked"] = centre([lheight(badge, 1000), wd, en], 110)
    else:
        wd = word(n, 420)
        ww, wh = lsize(wd)
        en = [(en_name(wh * 0.15), "p")]
        block = right_align([wd, en], wh * 0.20)
        th = lsize(block)[1]
        out["primary_ar"] = beside(wd, lheight(sym, wh * 1.18), wh * 0.32)
        out["ar_en"] = beside(block, lheight(sym, th * 1.02), th * 0.24)
        out["horizontal"] = out["ar_en"]
        out["stacked"] = centre([lheight(sym, wh * 1.5), wd, en], wh * 0.20)
    # descriptor lockup: horizontal + both descriptor lines under a fine rule
    hz = out["horizontal"]
    hw_, hh_ = lsize(hz)
    dar, den = desc(hh_ * 0.11)
    dl = right_align([[(dar, "p")], [(den, "p")]], hh_ * 0.07)
    dl = lwidth(dl, min(lsize(dl)[0], hw_)) if lsize(dl)[0] > hw_ else dl
    rule = [(rect(0, 0, hw_, max(2, hh_ * 0.006)), "a")]
    out["descriptor"] = right_align([hz, rule, dl], hh_ * 0.12)
    return out


def emboss(n, layers):
    """Single-colour production version: hairline detail becomes solid so it
    survives embroidery, foil, emboss and engraving."""
    if n == "02":
        return None
    return mono(layers)
