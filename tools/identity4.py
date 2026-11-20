"""ALRAYA identity v4 — six directions on one lettering system.

Every «الراية» here comes from letters.py: one correct structure, fixed
metrics (alif = lam height, one tooth height, one descent, equal gaps),
and a single pen per direction. Symbols are taken from the same letters.

Layers are (path, role): 'p' indigo, 'a' maroon.
"""
import math
import letters as Lt
from vec import (P, rect, rrect, circle, diamond, poly, union, diff, inter, stroke, move, scale,
                 rotate, bounds, caps, to_origin, size, simplify)
from pen import Skel, vstroke
from identity import (L, lb, lsize, lmove, lorigin, lheight, lwidth, right_align, centre, beside,
                      arc_map, arabic, EN, EN_SB, AR_PLEX_M, DESC_AR, DESC_EN)

NAMES = {"01": "الكتلة والفراغ", "02": "الخط المرسوم", "03": "الملتقى",
         "04": "الخاتمة", "05": "الكوفي الهندسي", "06": "ختم الراية"}
STYLE = {"01": "mass", "02": "line", "03": "sans", "04": "round", "06": "sans"}


# ================================================================== words
def word_layers(n):
    """«الراية» for direction n (letters indigo, dots maroon where the
    direction uses an accent)."""
    if n == "05":
        l, d, _ = Lt.angular()
    else:
        l, d = Lt.word(Lt.STYLES[STYLE[n]])
    acc = "a" if n in ("03", "05") else "p"
    return L((l, "p"), (d, acc))


def en_name(cap_h, track=0.5):
    letters = "ALRAYA"
    adj = {("L", "R"): -0.05, ("A", "Y"): -0.10, ("Y", "A"): -0.10, ("R", "A"): -0.02, ("A", "L"): -0.03}
    x, out = 0, []
    for i, ch in enumerate(letters):
        g = caps(ch, EN, cap_h, 0)
        gw, _ = size(g)
        out.append(move(g, x, 0))
        if i < len(letters) - 1:
            x += gw + cap_h * (track + adj.get((ch, letters[i + 1]), 0))
    return union(*out)


# ================================================================== 01 الكتلة والفراغ
def block(S=1000):
    k2 = S * 0.20
    h = k2 * 0.30
    return (P().M(k2, 0).L(S - k2, 0).C(S - h, 0, S, h, S, k2).L(S, S - k2).C(S, S - h, S - h, S, S - k2, S)
            .L(k2, S).C(h, S, 0, S - h, 0, S - k2).L(0, k2).C(0, h, h, 0, k2, 0).Z().path())


VOID_RA = None


def void_ra(S=1000):
    """The connected ra of the word (ـر), drawn as empty space: the join
    enters from the right edge on the writing line, the ra drops and leaves
    through the bottom. Same proportions and flat ends as the word's ra."""
    st = Lt.STYLES["mass"]
    k = 1.55                       # the word's ra, enlarged
    W, D = st.W * k, st.D * k
    yb, jx = S * 0.36, S * 0.66
    sk = (Skel(S + 80, yb).L(jx, yb)
          .C(jx - W * 0.55, yb, jx - W * 0.85, yb + D * 0.18, jx - W * 0.95, yb + D * 0.42)
          .C(jx - W * 1.1, yb + D * 0.82, jx - W * 2.0, yb + D * 1.05, jx - W * 3.3, S + 80))
    return vstroke(sk, W * 0.98), sk


def sym01():
    """A block, and through it the ra of the word as empty space: the
    unseen work that carries the visible one."""
    v, _ = void_ra()
    return L((diff(block(), v), "p"))


# ================================================================== 02 الخط المرسوم
def sym02():
    """Short version: the word itself, unchanged (wordmark direction)."""
    return word_layers("02")


# ================================================================== 03 الملتقى
def sym03(w=176, spread=300, jy=470, H=840, gap=28):
    """Y of ALRAYA and ya of الراية: two paths meet and leave as one line;
    the two dots of ya sit under it, drawn square like the dots of the word."""
    top = rect(-3000, -3000, 6000, 3000)
    left = diff(stroke(P().M(-spread, 0).L(0, jy).L(0, H).path(), w, "butt", "miter", 4), top)
    right = diff(stroke(P().M(spread, 0).L(0, jy).path(), w, "butt"), top)
    right = diff(right, stroke(left, gap * 2), rect(-w / 2 - gap, jy, w + 2 * gap, H))
    left = diff(left, rect(-3000, H, 6000, 3000))
    d = w * 0.86
    g = w * 0.36
    dots = union(rect(-g / 2 - d, H + w * 0.5, d, d), rect(g / 2, H + w * 0.5, d, d))
    return L((union(left, right), "p"), (dots, "a"))


# ================================================================== 04 القائم والحامل
def sym04():
    """«ية» from the round word: the tooth of ya, the closed loop of ta and
    the four round dots — how the name ends, kept whole."""
    pr = Lt.parts(Lt.STYLES["round"])
    return L((pr["yata"], "p"), (union(pr["ya_dots"], pr["ta_dots"]), "a"))


# ================================================================== 05 الكوفي الهندسي
def sym05():
    """Short version: the kufic word itself (wordmark direction)."""
    return word_layers("05")


# ================================================================== 06 ختم الراية
SEAL = Lt.Style("seal", W=124, A=540, T=230, D=200, G=100, pen="round", dot=1.3)


def core06():
    """An isolated ra drawn with the seal's round pen: a short head, a
    steady drop, and a tail that turns toward the next letter."""
    W = SEAL.W
    sk = Skel(70, -250).C(70, -120, 62, -10, 20, 70).C(-30, 165, -150, 228, -300, 238)
    return Lt._stroke(sk, SEAL), None


def badge06(R=500, lettered=True):
    rin = 0.66 * R
    band = diff(circle(0, 0, R), circle(0, 0, rin))
    lw = 0.016 * R
    mid = (R + rin) / 2
    if lettered:
        l, d = Lt.word(Lt.STYLES["sans"])
        ar = union(l, d)
        x0, y0, x1, y1 = bounds(ar)
        k = 0.30 * R / (y1 - y0)
        ar = scale(ar, k)
        x0, y0, x1, y1 = bounds(ar)
        ar = move(ar, -(x0 + x1) / 2, -(y0 + y1) / 2)
        ar = arc_map(ar, mid, True)
        en = en_name(0.105 * R, 0.62)
        x0, y0, x1, y1 = bounds(en)
        en = move(en, -(x0 + x1) / 2, -(y0 + y1) / 2)
        en = arc_map(en, mid, False)
        seps = union(circle(-mid, 0, 0.035 * R), circle(mid, 0, 0.035 * R))
        band = diff(band, ar, en, seps)
    inner = diff(circle(0, 0, rin - 0.05 * R), circle(0, 0, rin - 0.05 * R - lw))
    ra, _ = core06()
    x0, y0, x1, y1 = bounds(ra)
    k = (rin * 1.42) / max(x1 - x0, y1 - y0)
    ra = scale(ra, k)
    x0, y0, x1, y1 = bounds(ra)
    ra = move(ra, -(x0 + x1) / 2, -(y0 + y1) / 2)
    return L((union(band, inner), "p"), (ra, "a"))


SYM = {"01": sym01, "02": sym02, "03": sym03, "04": sym04, "05": sym05, "06": lambda: badge06(lettered=False)}


def symbol(n):
    return lorigin(SYM[n]())


def desc(h_ar):
    ar = arabic(DESC_AR, AR_PLEX_M, h_ar)
    en = caps(DESC_EN, EN_SB, h_ar * 0.42, 0.16)
    return ar, en


def lockups(n):
    out = {}
    sym = lheight(symbol(n), 1000)
    out["symbol"] = sym
    wd = lheight(word_layers(n), 560)
    ww, wh = lsize(wd)
    en = [(en_name(wh * (0.075 if n == "02" else 0.10)), "p")]
    out["primary_ar"] = wd if n in ("02", "05") else None
    block = right_align([wd, en], wh * 0.14)
    if n in ("02", "05"):
        out["ar_en"] = block
        out["horizontal"] = block
        out["stacked"] = block
    elif n == "06":
        badge = lorigin(badge06())
        out["circular"] = badge
        bh = lsize(badge)[1]
        rule = [(rect(0, 0, bh * 0.008, bh * 0.62), "a")]
        out["horizontal"] = beside(beside(lheight(block, bh * 0.56), rule, bh * 0.08), badge, bh * 0.08)
        out["ar_en"] = out["horizontal"]
        out["primary_ar"] = beside(lheight(wd, bh * 0.42), badge, bh * 0.12)
        out["stacked"] = centre([badge, lheight(block, bh * 0.52)], bh * 0.10)
    else:
        th = lsize(block)[1]
        out["primary_ar"] = beside(wd, lheight(sym, wh * 1.0), wh * 0.26)
        out["ar_en"] = beside(block, lheight(sym, th), th * 0.22)
        out["horizontal"] = out["ar_en"]
        out["stacked"] = centre([lheight(sym, th * 1.15), block], th * 0.18)
    hz = out["horizontal"]
    hw_, hh_ = lsize(hz)
    dar, den = desc(hh_ * 0.11)
    dl = right_align([[(dar, "p")], [(den, "p")]], hh_ * 0.07)
    if lsize(dl)[0] > hw_:
        dl = lwidth(dl, hw_)
    out["descriptor"] = right_align([hz, [(rect(0, 0, hw_, max(2, hh_ * 0.006)), "a")], dl], hh_ * 0.12)
    out["word"] = wd
    return {k: v for k, v in out.items() if v is not None}


# ================================================================== scene data
def scene_data(n):
    """Raw geometry for the scroll reveal: the final art plus the pen
    centre-lines that draw it (same coordinates, so drawing them at the
    pen's width rebuilds the logo exactly)."""
    from vec import d as pd
    from build_util import skel_d
    if n == "01":
        v, sk = void_ra()
        return dict(final=sym01(), block=block(), lines=[(skel_d(sk), Lt.STYLES["mass"].W * 1.55 * 0.98, "butt")])
    if n in ("02", "04"):
        st = Lt.STYLES["line" if n == "02" else "round"]
        sk, dots, dd = Lt.skeleton(st)
        keep = range(6) if n == "02" else (4, 5)
        lines = [(skel_d(sk[i][0]), st.W, "round") for i in keep]
        dl = dots if n == "02" else dots
        final = word_layers("02") if n == "02" else sym04()
        return dict(final=final, lines=lines, dots=[(x, y, dd / 2) for x, y in dl])
    if n == "03":
        return dict(final=sym03(), lines=[("M-300 0L0 470", 176, "butt"), ("M300 0L0 470", 176, "butt"), ("M0 470L0 840", 176, "butt")])
    if n == "05":
        l, dd, pr = Lt.angular()
        return dict(final=word_layers("05"), lines=[(pd(p), pr["W"], "butt") for p in pr["centre"]], rects=pr["dot_rects"])
    b = badge06()
    return dict(final=b, ring=500)
