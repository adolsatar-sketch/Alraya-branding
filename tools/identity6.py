"""ALRAYA v6 — the five directions approved from the client's reference board
(design-process/v6/approved-reference-board.png), redrawn as clean vector.

Rules used for every mark (1000-unit canvas):
  ring / outline stroke  S  = 34
  structural member      M  = 56  (columns, beams)
  fine construction line F  = 10, dashes 34 on / 22 off
  accent (maroon) is used once per mark, on the element that carries the idea.
Layers: (path, role) — 'p' indigo, 'a' maroon.
"""
import math
from vec import (P, rect, rrect, circle, ellipse, poly, union, diff, inter, stroke, move, scale,
                 rotate, bounds, text, caps, to_origin, size)
from identity import L, lsize, lorigin, lheight, lmove, right_align, centre, beside, EN, EN_SB
from identity5 import word as ar_word, en as en_name, desc, F as FONTS

S, M, FL = 34, 56, 10
NAMES = {"01": "العقدة الفولاذية", "02": "الإطار", "03": "القائم", "04": "البوابة", "05": "نقطة القياس"}
WORD = {"01": ("nkufi", (0.075, 0.07, 0.065)), "02": ("nkufi", (0.075, 0.07, 0.065)), "03": ("nkufi", (0.075, 0.07, 0.065)),
        "04": ("amiri", (0.05, 0.05, 0.04)), "05": ("amiri", (0.05, 0.05, 0.04))}


def ring(cx=500, cy=500, r=480, w=S):
    return diff(circle(cx, cy, r), circle(cx, cy, r - w))


def dashes(x0, y0, x1, y1, w=FL, on=34, off=22):
    """A dashed construction line as filled pieces (no stroke attributes)."""
    L_ = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / L_, (y1 - y0) / L_
    out, t = [], 0
    while t < L_:
        e = min(L_, t + on)
        out.append(stroke(P().M(x0 + ux * t, y0 + uy * t).L(x0 + ux * e, y0 + uy * e).path(), w))
        t = e + off
    return union(*out)


def bar(x0, y0, x1, y1, w):
    return stroke(P().M(x0, y0).L(x1, y1).path(), w, "butt")


# ================================================================== 01 العقدة الفولاذية
def parts01():
    """A steel column and two beams meet at one bolted plate; the column
    stands on a base plate. One joint holds the whole frame."""
    R = 480
    inside = circle(500, 500, R - S - 22)
    cx = 470
    # column in elevation: two flanges with the web gap between them
    col = union(rect(cx - 66, 120, 52, 640), rect(cx + 14, 120, 52, 640))
    # two parallel beams rising to the right, passing the column at the joint
    k = math.tan(math.radians(16))
    def beam(dy):
        y_at = lambda x: 360 + dy - (x - cx) * k
        return poly((40, y_at(40)), (960, y_at(960)), (960, y_at(960) + 44), (40, y_at(40) + 44))
    beams = union(beam(-50), beam(16))
    gap = 18
    beams = diff(beams, rect(cx - 82 - gap, 300 - gap, 164 + 2 * gap, 140 + 2 * gap))
    # bolted plate at the joint (maroon) with four bolt holes
    plate = rect(cx - 82, 300, 164, 140)
    holes = union(*[circle(cx + dx, 370 + dy, 13) for dx in (-40, 40) for dy in (-34, 34)])
    plate = diff(plate, holes)
    col = diff(col, rect(cx - 90, 292, 180, 156))
    # base plate (maroon line) and footing
    base_plate = rect(cx - 150, 762, 300, 26)
    footing = rect(cx - 230, 806, 460, 44)
    pedestal = rect(cx - 110, 788, 220, 18)
    bolts = union(rect(cx - 120, 738, 20, 24), rect(cx + 100, 738, 20, 24))
    return [(ring(r=R), "p", "frame"), (inter(union(col, footing, pedestal, bolts), inside), "p", "build"),
            (inter(beams, inside), "p", "beam"), (base_plate, "a", "build"), (plate, "a", "accent")], ("circle", 500, 500, R - S / 2, 90)


# ================================================================== 02 الإطار
def parts02():
    """A three-storey frame drawn in projection inside a hexagon: on the left
    the grid it is planned on, on the right the slabs and columns it becomes."""
    cx, cy, R = 500, 520, 470
    pts = [(cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a))) for a in (-90, -30, 30, 90, 150, 210)]
    hexo = poly(*pts)
    inner = poly(*[(cx + (R - S) * math.cos(math.radians(a)), cy + (R - S) * math.sin(math.radians(a))) for a in (-90, -30, 30, 90, 150, 210)])
    edge = diff(hexo, inner)
    # maroon: the upper-right edges (the side that is built)
    acc_zone = poly((cx, cy - R - 10), (cx + R + 20, cy - R / 2 - 10), (cx + R + 20, cy + R / 2 + 40), (cx, cy - 40))
    edge_a = inter(edge, acc_zone)
    edge_p = diff(edge, acc_zone)
    clip = inner
    # planning grid (left): fine lines and square nodes, open at the ends
    gx = [200, 300]
    gy = [400, 540, 680]
    # grid lines stop short of each node (no closed cells), as on a setting-out plan
    gap = 30
    segs = []
    ys = [330] + gy + [770]
    for x in gx:
        for a, b in zip(ys, ys[1:]):
            y0_ = a + (gap if a in gy else 0); y1_ = b - (gap if b in gy else 0)
            segs.append(rect(x - FL / 2, y0_, FL, y1_ - y0_))
    xs_ = [150] + gx + [480]
    for y in gy:
        for a, b in zip(xs_, xs_[1:]):
            x0_ = a + (gap if a in gx else 0); x1_ = b - (gap if b in gx else 0)
            segs.append(rect(x0_, y - FL / 2, x1_ - x0_, FL))
    grid = union(*segs)
    nodes = union(*[rect(x - 16, y - 16, 32, 32) for x in gx for y in gy])
    # built frame (right): front face + side receding up to the left
    W2 = 40
    fx0, fx1 = 650, 840
    floors = [400, 540, 680, 800]
    dx, dy = -150, -60                   # depth direction (oblique)
    front = union(rect(fx0 - W2 / 2, 380, W2, 440), rect(fx1 - W2 / 2, 360, W2, 460),
                  *[rect(fx0, y - 14, fx1 - fx0, 28) for y in floors[:-1]])
    side = union(rect(fx0 + dx - W2 / 2, 380 + dy, W2, 440 - 40),
                 *[stroke(P().M(fx0, y).L(fx0 + dx, y + dy).path(), 28) for y in floors[:-1]],
                 stroke(P().M(fx1, floors[0] - 20).L(fx1 + dx, floors[0] - 20 + dy).path(), 22))
    frame = union(front, side)
    ground = rect(150, 806, 720, 26)
    # dashed projection lines: from the plan grid to the frame it becomes
    dl = union(*[dashes(320, y, fx0 + dx - 30, y + dy * 0.6) for y in gy])
    nodes = union(nodes)
    grid = union(grid, ground)
    hexg = [(cx + (R - S / 2) * math.cos(math.radians(a)), cy + (R - S / 2) * math.sin(math.radians(a))) for a in (-90, -30, 30, 90, 150, 210)]
    return [(edge_p, "p", "frame"), (inter(union(grid, nodes), clip), "p", "plan"), (inter(dl, clip), "p", "plan"),
            (inter(union(frame, rect(150, 806, 720, 26)), clip), "p", "build"), (edge_a, "a", "accent")], ("poly", hexg, 90)


# ================================================================== 03 القائم
def parts03():
    """An A built like a structure: a raking strut, two columns and one beam
    that ties them, standing on a footing."""
    base_y = 860
    # raking strut from the footing up to the tall column
    strut = poly((120, base_y), (230, base_y), (650, 230), (650, 100), (560, 100))
    strut = inter(strut, rect(0, 0, 1000, base_y))
    col_tall = rect(760, 60, 96, base_y - 60)
    col_in = rect(590, 380, 96, base_y - 380)
    col_in = diff(col_in, rect(0, 0, 1000, 0))
    # beam (maroon) tying strut and columns, rising toward the tall column
    beam = poly((290, 640), (870, 520), (870, 590), (330, 700))
    beam = union(beam)
    # keep the beam from overlapping: cut a clear gap around it in the indigo parts
    g = 16
    parts = union(strut, col_tall, col_in)
    parts = diff(parts, stroke(beam, g * 2))
    foot = union(rect(80, base_y + 18, 840, 40), rect(100, base_y - 6, 150, 24), rect(740, base_y - 6, 136, 24), rect(572, base_y - 6, 132, 24))
    return [(foot, "p", "build"), (parts, "p", "build"), (beam, "a", "accent")], None


# ================================================================== 04 البوابة
def portal(cx, top, bot, span, colw, cap=True):
    """Two columns with capitals and bases under one lintel."""
    out = []
    for sx in (-1, 1):
        x = cx + sx * span / 2
        out.append(rect(x - colw / 2, top + 70, colw, bot - top - 140))
        if cap:
            out.append(rect(x - colw / 2 - 18, top + 50, colw + 36, 22))
            out.append(rect(x - colw / 2 - 26, bot - 70, colw + 52, 24))
            out.append(rect(x - colw / 2 - 40, bot - 40, colw + 80, 30))
    return union(*out)


def parts04():
    """A portal: two columns and a lintel, locked at the centre by a keystone.
    The keystone holds the two halves together."""
    R = 480
    inside = circle(500, 500, R - S - 22)
    cx = 500
    cols = portal(cx, 250, 800, 420, 70)
    # entablature in two halves, separated by the keystone
    lint = union(rect(170, 240, 660, 60), rect(150, 200, 700, 26))
    key = poly((cx - 72, 170), (cx + 72, 170), (cx + 24, 300), (cx - 24, 300))
    lint = diff(lint, stroke(key, 30))
    steps = union(rect(200, 830, 600, 40), rect(160, 878, 680, 46))
    return [(ring(r=R), "p", "frame"), (inter(union(cols, steps), inside), "p", "build"),
            (inter(lint, inside), "p", "beam"), (key, "a", "accent")], ("circle", 500, 500, R - S / 2, 90)


# ================================================================== 05 نقطة القياس
def parts05():
    """A portal set out on a surveyed frame: the circle carries four level
    marks, a dashed setting-out rectangle fixes the corners and the centre."""
    R = 470
    rg = ring(r=R, w=26)
    tick = 30
    gaps = union(rect(500 - 30, 0, 60, 80), rect(500 - 30, 920, 60, 80), rect(0, 470, 80, 60), rect(920, 470, 80, 60))
    rg = diff(rg, gaps)
    ticks = union(rect(500 - 9, 6, 18, 110), rect(500 - 9, 884, 18, 110), rect(6, 491, 110, 18), rect(884, 491, 110, 18))
    # setting-out rectangle (dashed) with corner squares and centre point
    x0, y0, x1, y1 = 255, 210, 745, 760
    so = union(dashes(x0, y0, x1, y0), dashes(x0, y0, x0, y1), dashes(x1, y0, x1, y1),
               dashes(500, y0 - 40, 500, y1), dashes(200, 505, 800, 505))
    corners = union(rect(x0 - 22, y0 - 22, 44, 44), rect(x1 - 22, y0 - 22, 44, 44))
    centre_pt = rect(500 - 22, 505 - 22, 44, 44)
    cols = portal(500, 300, 760, 360, 64)
    lint = union(rect(250, 290, 500, 46), rect(225, 270, 550, 24))
    body = union(cols, lint)
    # keep the dashed lines from crossing the solid parts
    so = diff(so, stroke(body, 28), stroke(centre_pt, 28))
    base = rect(220, 790, 560, 50)
    return [(union(rg, ticks), "p", "frame"), (union(so, corners), "p", "plan"), (body, "p", "build"),
            (centre_pt, "p", "point"), (base, "a", "accent")], ("circle", 500, 500, 440, 150)


PARTS = {"01": parts01, "02": parts02, "03": parts03, "04": parts04, "05": parts05}


def parts(n):
    """[(path, role, stage)], guide — the mark split into the order it is built
    (frame, plan, build, beam, point, accent) for the reveal on the site."""
    return PARTS[n]()


def raw(n):
    ps, _ = parts(n)
    out = []
    for role in ("p", "a"):
        g = [p for p, r, _ in ps if r == role]
        if g:
            out.append((union(*g), role))
    return L(*out)


SYM = {n: (lambda n=n: raw(n)) for n in PARTS}


def symbol(n):
    return lorigin(SYM[n]())


def word_layers(n):
    f, g = WORD[n]
    return L((ar_word(f, gaps=g), "p"))


def lockups(n):
    out = {}
    wd = lheight(word_layers(n), 520)
    ww, wh = lsize(wd)
    out["word"] = wd
    sym = symbol(n)
    e = [(en_name(wh * 0.12, 0.5), "p")]
    blk = right_align([wd, e], wh * 0.16)
    bh = lsize(blk)[1]
    out["symbol"] = lheight(sym, 1000)
    out["horizontal"] = beside(blk, lheight(sym, bh * 1.35), bh * 0.24)
    out["stacked"] = centre([lheight(sym, bh * 1.6), blk], bh * 0.18)
    hz = out["horizontal"]
    hw, hh = lsize(hz)
    dar, den = desc(hh * 0.10)
    dl = right_align([[(dar, "p")], [(den, "p")]], hh * 0.06)
    out["descriptor"] = right_align([hz, [(rect(0, 0, hw, max(2, hh * 0.005)), "a")], dl], hh * 0.12)
    return out
