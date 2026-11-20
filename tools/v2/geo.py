"""Geometry helpers for the ALRAYA logo directions.

Text is shaped with HarfBuzz (correct Arabic joining) and converted to
outlines, so every logo is pure vector geometry with no font dependency.
"""
import io, math, os
from functools import lru_cache
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
from shapely.geometry import Polygon, MultiPolygon, box
from shapely.ops import unary_union
from shapely import affinity

FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "fonts")


@lru_cache(None)
def load(name):
    f = TTFont(os.path.join(FONT_DIR, name))
    f.flavor = None
    buf = io.BytesIO()
    f.save(buf)
    data = buf.getvalue()
    return TTFont(io.BytesIO(data)), hb.Font(hb.Face(data))


class FlatPen(BasePen):
    def __init__(self, gs, steps=12):
        super().__init__(gs)
        self.contours, self.cur, self.steps = [], [], steps

    def _moveTo(self, p):
        self.cur = [p]

    def _lineTo(self, p):
        self.cur.append(p)

    def _curveToOne(self, p1, p2, p3):
        p0 = self.cur[-1]
        for i in range(1, self.steps + 1):
            t = i / self.steps
            mt = 1 - t
            self.cur.append((
                mt**3*p0[0] + 3*mt*mt*t*p1[0] + 3*mt*t*t*p2[0] + t**3*p3[0],
                mt**3*p0[1] + 3*mt*mt*t*p1[1] + 3*mt*t*t*p2[1] + t**3*p3[1]))

    def _qCurveToOne(self, p1, p2):
        p0 = self.cur[-1]
        for i in range(1, self.steps + 1):
            t = i / self.steps
            mt = 1 - t
            self.cur.append((mt*mt*p0[0] + 2*mt*t*p1[0] + t*t*p2[0],
                             mt*mt*p0[1] + 2*mt*t*p1[1] + t*t*p2[1]))

    def _closePath(self):
        if len(self.cur) > 2:
            self.contours.append(self.cur)
        self.cur = []

    _endPath = _closePath


def glyph_geom(tt, gname):
    gs = tt.getGlyphSet()
    pen = FlatPen(gs)
    gs[gname].draw(pen)
    if not pen.contours:
        return None

    def sarea(c):
        return sum(c[i][0] * c[i - 1][1] - c[i - 1][0] * c[i][1] for i in range(len(c))) / 2
    areas = [sarea(c) for c in pen.contours]
    main = max(range(len(areas)), key=lambda i: abs(areas[i]))
    sign = 1 if areas[main] > 0 else -1
    fills = [Polygon(c).buffer(0) for c, a in zip(pen.contours, areas) if a * sign > 0]
    holes = [Polygon(c).buffer(0) for c, a in zip(pen.contours, areas) if a * sign < 0]
    g = unary_union(fills)
    if holes:
        g = g.difference(unary_union(holes))
    return g


def text(s, font, size, track=0.0, rtl=None, features=None):
    """Shape `s` and return a shapely geometry in SVG coords.
    Origin: x=0 at the left edge of the run, y=0 at the baseline (y down).
    `track` is extra spacing in em units (Latin only)."""
    tt, hfont = load(font)
    upem = tt["head"].unitsPerEm
    buf = hb.Buffer()
    buf.add_str(s)
    buf.guess_segment_properties()
    hb.shape(hfont, buf, features or {})
    order = tt.getGlyphOrder()
    x = 0
    parts = []
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        g = glyph_geom(tt, order[info.codepoint])
        if g is not None and not g.is_empty:
            g = affinity.translate(g, x + pos.x_offset, pos.y_offset)
            parts.append(g)
        x += pos.x_advance + track * upem
    if track:
        x -= track * upem
    geom = unary_union(parts)
    k = size / upem
    geom = affinity.scale(geom, k, -k, origin=(0, 0))
    return geom, x * k


def path_d(geom, nd=1):
    """Shapely (Multi)Polygon -> SVG path data (evenodd-safe, nonzero-safe)."""
    if geom is None or geom.is_empty:
        return ""
    polys = geom.geoms if hasattr(geom, "geoms") else [geom]
    out = []
    f = lambda v: (("%." + str(nd) + "f") % v).rstrip("0").rstrip(".") if nd else str(round(v))
    for p in polys:
        if p.is_empty or p.geom_type != "Polygon":
            continue
        rings = [p.exterior] + list(p.interiors)
        for i, r in enumerate(rings):
            cs = list(r.coords)[:-1]
            # exterior CCW in y-down == clockwise visually; enforce opposite winding for holes
            ccw = r.is_ccw
            if (i == 0) != ccw:
                cs = cs[::-1]
            out.append("M" + "L".join(f(x) + " " + f(y) for x, y in cs) + "Z")
    return "".join(out)


def bounds(*geoms):
    g = unary_union([x for x in geoms if x is not None and not x.is_empty])
    return g.bounds


def place(geom, x=0, y=0, s=1.0):
    return affinity.translate(affinity.scale(geom, s, s, origin=(0, 0)), x, y)


def fit_width(geom, w):
    b = geom.bounds
    return affinity.scale(geom, w / (b[2] - b[0]), w / (b[2] - b[0]), origin=(0, 0))


def norm(geom):
    """Move geometry so its bbox starts at 0,0."""
    b = geom.bounds
    return affinity.translate(geom, -b[0], -b[1])


def arc_warp(geom, R, top=True, seg=4.0):
    """Bend a horizontal text run (centred on x=0, baseline y=0) around a circle
    of radius R centred at the origin. top=True: text reads along the top arc."""
    geom = geom.segmentize(seg)

    def tf(x, y):
        if top:
            a = -math.pi / 2 + x / R
            r = R - y
        else:
            a = math.pi / 2 - x / R
            r = R + y
        return r * math.cos(a), r * math.sin(a)

    def ring(r):
        return [tf(x, y) for x, y in r.coords]

    polys = geom.geoms if hasattr(geom, "geoms") else [geom]
    res = []
    for p in polys:
        res.append(Polygon(ring(p.exterior), [ring(i) for i in p.interiors]).buffer(0))
    return unary_union(res)


def circle(cx, cy, r, res=128):
    from shapely.geometry import Point
    return Point(cx, cy).buffer(r, resolution=res)


def ring(cx, cy, r_out, r_in):
    return circle(cx, cy, r_out).difference(circle(cx, cy, r_in))


def rect(x, y, w, h):
    return box(x, y, x + w, y + h)


def poly(*pts):
    return Polygon(pts)


def diamond(cx, cy, s):
    h = s / 2
    return Polygon([(cx, cy - h), (cx + h, cy), (cx, cy + h), (cx - h, cy)])
