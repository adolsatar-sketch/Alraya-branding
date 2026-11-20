"""Vector core for the ALRAYA identity (v3).

Shapes are skia Paths holding real line / quadratic / cubic segments.
Booleans use Skia PathOps, which keeps curves as curves, so the exported
SVG stays light and editable in Illustrator.
"""
import io, math, os
from functools import lru_cache
import skia
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen

FONT_DIR = os.path.join(os.path.dirname(__file__), "fonts")
K = 0.5522847498  # circle kappa


# ------------------------------------------------------------------ building
class P:
    """Small path builder: P().M(x,y).L(..).C(..).Z()"""

    def __init__(self, path=None):
        self.p = path if path is not None else skia.Path()

    def M(self, x, y): self.p.moveTo(x, y); return self
    def L(self, x, y): self.p.lineTo(x, y); return self
    def Q(self, x1, y1, x, y): self.p.quadTo(x1, y1, x, y); return self
    def C(self, x1, y1, x2, y2, x, y): self.p.cubicTo(x1, y1, x2, y2, x, y); return self
    def Z(self): self.p.close(); return self

    def path(self):
        return self.p


def poly(*pts):
    b = P().M(*pts[0])
    for q in pts[1:]:
        b.L(*q)
    return b.Z().path()


def rect(x, y, w, h):
    p = skia.Path()
    p.addRect(skia.Rect.MakeXYWH(x, y, w, h))
    return p


def ellipse(cx, cy, rx, ry):
    """Four cubic arcs (no conics, so SVG output is exact)."""
    kx, ky = rx * K, ry * K
    return (P().M(cx + rx, cy).C(cx + rx, cy + ky, cx + kx, cy + ry, cx, cy + ry)
            .C(cx - kx, cy + ry, cx - rx, cy + ky, cx - rx, cy)
            .C(cx - rx, cy - ky, cx - kx, cy - ry, cx, cy - ry)
            .C(cx + kx, cy - ry, cx + rx, cy - ky, cx + rx, cy).Z().path())


def circle(cx, cy, r):
    return ellipse(cx, cy, r, r)


def rrect(x, y, w, h, r):
    k = r * (1 - K)
    return (P().M(x + r, y).L(x + w - r, y).C(x + w - k, y, x + w, y + k, x + w, y + r)
            .L(x + w, y + h - r).C(x + w, y + h - k, x + w - k, y + h, x + w - r, y + h)
            .L(x + r, y + h).C(x + k, y + h, x, y + h - k, x, y + h - r)
            .L(x, y + r).C(x, y + k, x + k, y, x + r, y).Z().path())


def diamond(cx, cy, w, h=None):
    h = h or w
    return poly((cx, cy - h / 2), (cx + w / 2, cy), (cx, cy + h / 2), (cx - w / 2, cy))


# ------------------------------------------------------------------ booleans
def wind(p):
    """Normalise to non-zero winding with correctly oriented holes, so the
    SVG renders the same everywhere without fill-rule tricks."""
    if p is None:
        return skia.Path()
    r = skia.AsWinding(p)
    return r if r is not None else p


def _op(a, b, op):
    r = skia.Op(a, b, op)
    return wind(r) if r is not None else skia.Path()


def union(*ps):
    ps = [p for p in ps if p is not None and p.countVerbs()]
    if not ps:
        return skia.Path()
    # pairwise ops: skia's OpBuilder can drop inner contours of rings
    r = ps[0]
    for p in ps[1:]:
        q = skia.Op(r, p, skia.PathOp.kUnion_PathOp)
        r = q if q is not None else r
    if len(ps) == 1:
        r = skia.Simplify(r) or r
    return wind(r)


def diff(a, *bs):
    for b in bs:
        if b is not None and b.countVerbs():
            a = _op(a, b, skia.PathOp.kDifference_PathOp)
    return a


def inter(a, b):
    return _op(a, b, skia.PathOp.kIntersect_PathOp)


def xor(a, b):
    return _op(a, b, skia.PathOp.kXOR_PathOp)


def simplify(p):
    r = skia.Simplify(p)
    return wind(r) if r is not None else p


# ------------------------------------------------------------------ strokes
CAPS = {"butt": skia.Paint.kButt_Cap, "round": skia.Paint.kRound_Cap, "square": skia.Paint.kSquare_Cap}
JOINS = {"miter": skia.Paint.kMiter_Join, "round": skia.Paint.kRound_Join, "bevel": skia.Paint.kBevel_Join}


def stroke(path, w, cap="butt", join="miter", miter=8):
    paint = skia.Paint(AntiAlias=True, StrokeWidth=w, Style=skia.Paint.kStroke_Style,
                       StrokeCap=CAPS[cap], StrokeJoin=JOINS[join], StrokeMiter=miter)
    out = skia.Path()
    paint.getFillPath(path, out, None, 1.0)
    return simplify(clean(out))


def contours(path):
    """Split a path into its separate closed contours."""
    out, cur = [], None
    for cmd, pts in segments(path):
        if cmd == "M":
            if cur is not None:
                out.append(cur)
            cur = skia.Path(); cur.moveTo(pts[0])
        elif cmd == "L": cur.lineTo(pts[0])
        elif cmd == "Q": cur.quadTo(pts[0], pts[1])
        elif cmd == "C": cur.cubicTo(pts[0], pts[1], pts[2])
        elif cmd == "Z": cur.close()
    if cur is not None:
        out.append(cur)
    return out


def outline(path, w):
    """Hairline contour of a filled shape (the drawn line, centred on the edge).
    Each contour is stroked on its own so holes keep their rings."""
    return union(*[stroke(c, w, "butt", "miter") for c in contours(path)])


# ------------------------------------------------------------------ transforms
def tf(path, a=1, b=0, c=0, d=1, e=0, f=0):
    m = skia.Matrix()
    m.setAll(a, c, e, b, d, f, 0, 0, 1)
    out = skia.Path(path)
    out.transform(m)
    return out


def move(p, dx, dy):
    return tf(p, e=dx, f=dy)


def scale(p, sx, sy=None, ox=0, oy=0):
    sy = sx if sy is None else sy
    return tf(p, sx, 0, 0, sy, ox - ox * sx, oy - oy * sy)


def rotate(p, deg, ox=0, oy=0):
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    return tf(p, c, s, -s, c, ox - c * ox + s * oy, oy - s * ox - c * oy)


def mirror_x(p, ox=0):
    return tf(p, -1, 0, 0, 1, 2 * ox, 0)


def mirror_y(p, oy=0):
    return tf(p, 1, 0, 0, -1, 0, 2 * oy)


def bounds(*ps):
    r = None
    for p in ps:
        if p is None or not p.countVerbs():
            continue
        b = p.computeTightBounds()
        r = b if r is None else skia.Rect.MakeLTRB(min(r.left(), b.left()), min(r.top(), b.top()),
                                                   max(r.right(), b.right()), max(r.bottom(), b.bottom()))
    if r is None:
        return (0, 0, 0, 0)
    return (r.left(), r.top(), r.right(), r.bottom())


# ------------------------------------------------------------------ svg out
def _f(v, nd):
    s = f"{v:.{nd}f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def segments(path):
    """Yield (cmd, [points]) with conics converted to quadratic curves."""
    it = skia.Path.Iter(path, False)
    V = skia.Path.Verb
    while True:
        verb, pts = it.next()
        if verb == V.kDone_Verb:
            return
        if verb == V.kMove_Verb:
            yield "M", [pts[0]]
        elif verb == V.kLine_Verb:
            yield "L", [pts[1]]
        elif verb == V.kQuad_Verb:
            yield "Q", pts[1:3]
        elif verb == V.kConic_Verb:
            q = skia.Path.ConvertConicToQuads(pts[0], pts[1], pts[2], it.conicWeight(), 1)
            for i in range(1, len(q) - 1, 2):
                yield "Q", [q[i], q[i + 1]]
        elif verb == V.kCubic_Verb:
            yield "C", pts[1:4]
        elif verb == V.kClose_Verb:
            yield "Z", []


def d(path, nd=1):
    out = []
    for cmd, pts in segments(path):
        out.append(cmd + " ".join(_f(c, nd) for q in pts for c in (q.x(), q.y())))
    return "".join(out)


def clean(path):
    """Rebuild a path without conics."""
    out = skia.Path()
    for cmd, pts in segments(path):
        if cmd == "M": out.moveTo(pts[0])
        elif cmd == "L": out.lineTo(pts[0])
        elif cmd == "Q": out.quadTo(pts[0], pts[1])
        elif cmd == "C": out.cubicTo(pts[0], pts[1], pts[2])
        else: out.close()
    out.setFillType(path.getFillType())
    return out


def count_points(path):
    return path.countPoints()


# ------------------------------------------------------------------ text
@lru_cache(None)
def font(name):
    f = TTFont(os.path.join(FONT_DIR, name))
    f.flavor = None
    buf = io.BytesIO()
    f.save(buf)
    data = buf.getvalue()
    return TTFont(io.BytesIO(data)), hb.Font(hb.Face(data))


class SkPen(BasePen):
    def __init__(self, gs):
        super().__init__(gs)
        self.p = skia.Path()

    def _moveTo(self, pt): self.p.moveTo(*pt)
    def _lineTo(self, pt): self.p.lineTo(*pt)
    def _curveToOne(self, a, b, c): self.p.cubicTo(*a, *b, *c)
    def _qCurveToOne(self, a, b): self.p.quadTo(*a, *b)
    def _closePath(self): self.p.close()
    _endPath = _closePath


@lru_cache(None)
def _glyph(name, gname):
    tt, _ = font(name)
    pen = SkPen(tt.getGlyphSet())
    tt.getGlyphSet()[gname].draw(pen)
    p = pen.p
    p.setFillType(skia.PathFillType.kWinding)
    return simplify(p)


def text(s, name, size, track=0.0, features=None):
    """Shaped text as one path. Baseline y=0, x from 0. Returns (path, advance)."""
    tt, hf = font(name)
    upem = tt["head"].unitsPerEm
    buf = hb.Buffer()
    buf.add_str(s)
    buf.guess_segment_properties()
    hb.shape(hf, buf, features or {})
    order = tt.getGlyphOrder()
    x = 0
    parts = []
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        g = _glyph(name, order[info.codepoint])
        if g.countVerbs():
            parts.append(move(g, x + pos.x_offset, pos.y_offset))
        x += pos.x_advance + track * upem
    if track:
        x -= track * upem
    k = size / upem
    return tf(union(*parts), k, 0, 0, -k, 0, 0), x * k


def caps(s, name, cap_h, track=0.2):
    """Latin caps scaled to an exact cap height, top-left at 0,0."""
    p, _ = text(s, name, 1000, track)
    x0, y0, x1, y1 = bounds(p)
    k = cap_h / (y1 - y0)
    p = scale(p, k)
    x0, y0, _, _ = bounds(p)
    return move(p, -x0, -y0)


def to_origin(p):
    x0, y0, _, _ = bounds(p)
    return move(p, -x0, -y0)


def size(*ps):
    x0, y0, x1, y1 = bounds(*ps)
    return x1 - x0, y1 - y0
