"""ALRAYA identity v5 — six directions built on sound Arabic typefaces.

Every Arabic word is shaped by HarfBuzz from a professional typeface (so
joins, proportions and dots are the type designer's), converted to
outlines, and only spaced by eye between separate letter groups. Marks are
taken from the same typefaces, so a mark and its word always match.

Layers: (path, role) — 'p' indigo, 'a' maroon.
"""
from vec import (P, rect, rrect, circle, diamond, poly, union, diff, inter, stroke, move, scale,
                 bounds, text, caps, to_origin, size)
from identity import (L, lb, lsize, lmove, lorigin, lheight, lwidth, right_align, centre, beside,
                      arc_map, EN, EN_SB)

F = {
    "kufam": "kufam-arabic-800-normal.woff2",
    "nkufi": "noto-kufi-arabic-arabic-800-normal.woff2",
    "nkufi7": "noto-kufi-arabic-arabic-700-normal.woff2",
    "changa": "changa-arabic-800-normal.woff2",
    "readex": "readex-pro-arabic-700-normal.woff2",
    "tajawal": "tajawal-arabic-800-normal.woff2",
    "alex": "alexandria-arabic-800-normal.woff2",
    "amiri": "amiri-arabic-700-normal.woff2",
    "plex": "ibm-plex-sans-arabic-arabic-700-normal.woff2",
    "plexm": "ibm-plex-sans-arabic-arabic-500-normal.woff2",
}
DESC_AR = "مقاولات عامة واستشارات هندسية"
DESC_EN = "GENERAL CONTRACTING & ENGINEERING CONSULTANCY"
NAMES = {"01": "حلقة التاء", "02": "اللوحة", "03": "را", "04": "ستة بستة", "05": "الأداة", "06": "ختم الراية"}


def glyphs(s, font):
    g, adv = text(s, F[font], 1000)
    return g


def word(font, groups=("ا", "لر", "ا", "ية"), gaps=(0.07, 0.065, 0.06)):
    """«الراية» set group by group: letters that join stay joined (shaped as
    one run), the space between separate groups is set by eye."""
    shapes = [text(g, F[font], 1000)[0] for g in groups]
    out, cur = [], 0
    for i, p in enumerate(shapes):
        x0, _, x1, _ = bounds(p)
        out.append(move(p, -x1 + cur, 0))
        cur = cur - (x1 - x0) - (gaps[i] * 1000 if i < len(gaps) else 0)
    return to_origin(union(*out))


def en(cap_h, track=0.5, font=EN):
    letters = "ALRAYA"
    adj = {("L", "R"): -0.05, ("A", "Y"): -0.10, ("Y", "A"): -0.10, ("R", "A"): -0.02, ("A", "L"): -0.03}
    x, out = 0, []
    for i, ch in enumerate(letters):
        g = caps(ch, font, cap_h, 0)
        gw, _ = size(g)
        out.append(move(g, x, 0))
        if i < 5:
            x += gw + cap_h * (track + adj.get((ch, letters[i + 1]), 0))
    return union(*out)


def en_width(width, cap_h):
    """ALRAYA tracked so it is exactly `width` wide."""
    lo, hi = 0.0, 3.0
    for _ in range(30):
        mid = (lo + hi) / 2
        w = size(en(cap_h, mid))[0]
        lo, hi = (mid, hi) if w < width else (lo, mid)
    return en(cap_h, (lo + hi) / 2)


def split_dots(g, font_h):
    """Separate dots from letters by size (dots are the small closed shapes)."""
    from vec import contours
    cs = contours(g)
    box = [bounds(c) for c in cs]

    def inside(i, j):
        a, b = box[i], box[j]
        return a[0] >= b[0] and a[1] >= b[1] and a[2] <= b[2] and a[3] <= b[3]
    dots, letters = [], []
    for i, c in enumerate(cs):
        x0, y0, x1, y1 = box[i]
        small = max(x1 - x0, y1 - y0) < font_h * 0.26
        held = any(inside(i, j) for j in range(len(cs)) if j != i)
        (dots if small and not held else letters).append(i)
    keep = lambda idx: diff(g, union(*[cs[i] for i in range(len(cs)) if i not in idx]))
    return keep(letters), keep(dots)


# ------------------------------------------------------------------ 01 حلقة التاء
def sym01():
    """The ta marbuta of Kufam: a closed drop with two dots. The name ends
    with it."""
    g = glyphs("ة", "kufam")
    x0, y0, x1, y1 = bounds(g)
    loop, dots = split_dots(g, y1 - y0)
    return L((loop, "p"), (dots, "a"))


# ------------------------------------------------------------------ 02 اللوحة
def plate02(word_h=300):
    w = word("nkufi", gaps=(0.075, 0.07, 0.065))
    w = scale(w, word_h / size(w)[1])
    w = to_origin(w)
    ww, wh = size(w)
    px, py = wh * 0.42, wh * 0.36
    W, H = ww + 2 * px, wh + 2 * py
    r = H * 0.10
    plate = rrect(0, 0, W, H, r)
    # maroon foot: a strip along the bottom of the plate
    return W, H, w, plate, (px, py)


def sym02():
    W, H, w, plate, (px, py) = plate02()
    face = diff(plate, move(w, px, py))
    strip = rect(0, H + H * 0.06, W, H * 0.07)
    return L((face, "p"), (strip, "a"))


# ------------------------------------------------------------------ 03 را
def sym03():
    """«را» in Changa: the first sound of the name after the article."""
    return L((glyphs("را", "changa"), "p"))


# ------------------------------------------------------------------ 04 ستة بستة
def block04():
    w = word("tajawal", gaps=(0.07, 0.065, 0.06))
    w = scale(w, 400 / size(w)[1])
    w = to_origin(w)
    ww, wh = size(w)
    e = en_width(ww, wh * 0.16)
    rule_y = wh + wh * 0.12
    rule = rect(0, rule_y, ww, wh * 0.025)
    e = move(e, 0, rule_y + wh * 0.025 + wh * 0.12)
    return L((w, "p"), (rule, "a"), (e, "p"))


def sym04():
    """Short version: the two names, six letters over six, in a square."""
    w = word("tajawal", gaps=(0.07, 0.065, 0.06))
    w = to_origin(scale(w, 400 / size(w)[1]))
    ww, wh = size(w)
    e = en_width(ww, wh * 0.16)
    S = ww * 1.30
    tile = rrect(0, 0, S, S, S * 0.12)
    ox = (S - ww) / 2
    tot = wh + wh * 0.12 + wh * 0.025 + wh * 0.12 + size(e)[1]
    oy = (S - tot) / 2
    cut = union(move(w, ox, oy), move(rect(0, wh + wh * 0.12, ww, wh * 0.025), ox, oy),
                move(e, ox, oy + wh + wh * 0.12 + wh * 0.025 + wh * 0.12))
    return L((diff(tile, cut), "p"))


# ------------------------------------------------------------------ 05 الأداة
def sym05():
    """«ال» and «AL»: both names begin with the same article. The Arabic lam
    and the Latin L face each other across one axis."""
    ar = glyphs("ال", "alex")
    x0, y0, x1, y1 = bounds(ar)
    H = y1 - y0
    lat = caps("AL", EN, H * 0.74, 0.08)
    lw, lh = size(lat)
    ar = to_origin(ar)
    aw, ah = size(ar)
    gap = H * 0.16
    # align baselines: Latin caps sit on the Arabic baseline
    base = ah - (y1 - 0) if False else None
    a0 = bounds(text("ا", F["alex"], 1000)[0])
    k = H / 1000
    lat = move(lat, 0, ah - lh - (y1 - 0) * 0)  # bottoms aligned
    ar_b = bounds(ar)
    lat = move(lat, 0, 0)
    axis = rect(lw + gap / 2 - H * 0.012, -H * 0.10, H * 0.024, ah + H * 0.20)
    ar = move(ar, lw + gap, 0)
    # bottoms aligned to the Arabic baseline (alif foot)
    return L((lat, "p"), (axis, "a"), (ar, "p"))


# ------------------------------------------------------------------ 06 ختم الراية
def seal06(R=500, lettered=True):
    lw = R * 0.03
    outer = diff(circle(0, 0, R), circle(0, 0, R - lw))
    rin = R * 0.70
    inner = diff(circle(0, 0, rin), circle(0, 0, rin - lw * 0.6))
    mid = (R - lw + rin) / 2
    parts = [outer, inner]
    acc = []
    if lettered:
        d = text(DESC_AR, F["nkufi7"], 1000)[0]
        x0, y0, x1, y1 = bounds(d)
        k = 0.11 * R / (y1 - y0)
        d = scale(d, k)
        x0, y0, x1, y1 = bounds(d)
        d = move(d, -(x0 + x1) / 2, -(y0 + y1) / 2)
        parts.append(arc_map(d, mid, True))
        e = en(0.085 * R, 0.55)
        x0, y0, x1, y1 = bounds(e)
        e = move(e, -(x0 + x1) / 2, -(y0 + y1) / 2)
        parts.append(arc_map(e, mid, False))
        acc.append(union(circle(-mid, 0, R * 0.025), circle(mid, 0, R * 0.025)))
    w = word("amiri", gaps=(0.05, 0.05, 0.04))
    x0, y0, x1, y1 = bounds(w)
    k = (rin * 1.45) / (x1 - x0)
    w = scale(w, k)
    x0, y0, x1, y1 = bounds(w)
    w = move(w, -(x0 + x1) / 2, -(y0 + y1) / 2 - R * 0.03)
    bar = rect(-rin * 0.16, (y1 - y0) / 2 + R * 0.06, rin * 0.32, R * 0.018)
    acc.append(bar)
    return L((union(*parts, w), "p"), (union(*acc), "a"))


SYM = {"01": sym01, "02": sym02, "03": sym03, "04": lambda: block04(), "05": sym05, "06": lambda: seal06()}
WORD = {"01": ("kufam", (0.07, 0.06, 0.06)), "02": ("nkufi", (0.075, 0.07, 0.065)), "03": ("changa", (0.06, 0.055, 0.05)),
        "04": ("tajawal", (0.07, 0.065, 0.06)), "05": ("alex", (0.07, 0.06, 0.06)), "06": ("amiri", (0.05, 0.05, 0.04))}


def word_layers(n):
    f, g = WORD[n]
    return L((word(f, gaps=g), "p"))


def symbol(n):
    return lorigin(SYM[n]())


def desc(h):
    ar = to_origin(text(DESC_AR, F["plexm"], 1000)[0])
    ar = scale(ar, h / size(ar)[1])
    e = caps(DESC_EN, EN_SB, h * 0.40, 0.16)
    return to_origin(ar), e


def lockups(n):
    out = {}
    wd = lheight(word_layers(n), 520)
    ww, wh = lsize(wd)
    out["word"] = wd
    sym = symbol(n)
    if n == "02":
        W, H, w, plate, (px, py) = plate02(520)
        face = diff(plate, move(w, px, py))
        e = en_width(W * 0.62, H * 0.085)
        ew, eh = size(e)
        hz = L((face, "p"), (move(e, W - ew, H + H * 0.16), "p"))
        out["horizontal"] = hz
        out["stacked"] = hz
        out["symbol"] = lheight(sym, 1000)
    elif n == "04":
        b = lorigin(block04())
        out["horizontal"] = b
        out["stacked"] = b
        out["symbol"] = lheight(sym, 1000)
    elif n == "06":
        s = lorigin(seal06())
        sh = lsize(s)[1]
        out["symbol"] = lheight(s, 1000)
        out["circular"] = s
        blk = right_align([lheight(wd, sh * 0.30), [(en(sh * 0.055, 0.5), "p")]], sh * 0.07)
        rule = [(rect(0, 0, sh * 0.006, sh * 0.56), "a")]
        out["horizontal"] = beside(beside(blk, rule, sh * 0.07), s, sh * 0.07)
        out["stacked"] = centre([s, blk], sh * 0.08)
    else:
        e = [(en(wh * 0.12, 0.5), "p")]
        blk = right_align([wd, e], wh * 0.16)
        bh = lsize(blk)[1]
        sh = {"01": 1.05, "03": 0.92, "05": 0.80}[n]
        out["horizontal"] = beside(blk, lheight(sym, bh * sh), bh * 0.24)
        out["stacked"] = centre([lheight(sym, bh * 1.1), blk], bh * 0.16)
        out["symbol"] = lheight(sym, 1000)
    hz = out["horizontal"]
    hw, hh = lsize(hz)
    dar, den = desc(hh * 0.10)
    dl = right_align([[(dar, "p")], [(den, "p")]], hh * 0.06)
    if lsize(dl)[0] > hw:
        dl = lwidth(dl, hw)
    out["descriptor"] = right_align([hz, [(rect(0, 0, hw, max(2, hh * 0.005)), "a")], dl], hh * 0.12)
    return out
