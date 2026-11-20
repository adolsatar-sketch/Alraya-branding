"""Builds index.html — ALRAYA, six logo directions (v3).

    python3 tools/build3.py

Earlier versions stay in v1/ and v2/ untouched.
"""
import base64, io, math, os, re, sys

sys.path.insert(0, os.path.dirname(__file__))
from fontTools import subset
from fontTools.ttLib import TTFont

import identity as I
import mock3 as M
from vec import d as pd, bounds, tf, move, scale, P
from pen import Skel

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.dirname(__file__)
FONTS = os.path.join(TOOLS, "fonts")

# ================================================================== content
D = [
    dict(n="01", name="العقدة", slug="01-al-uqda",
         story="التخطيط والتنفيذ ليسا مرحلتين منفصلتين؛ قوتهما في نقطة الاتصال.",
         build=["ألفٌ قائمة: محور التخطيط.", "راءٌ تمرّ أمامها: مسار التنفيذ.", "معاً يكتبان «را»، أول مقطع في الاسم."],
         why="رمز من حرفين في الاسم، يُقرأ فوراً، ويُطرَّز ويُحفر بلون واحد.",
         apps=("card", "facade"), min_icon=16),
    dict(n="02", name="من الخط إلى الكتلة", slug="02-line-to-mass",
         story="خطٌ بدأ على الورق، وانتهى كتلةً قائمة.",
         build=["حروف مرسومة بسماكة واحدة على شبكة واحدة.", "خط قطع صاعد يفصل المرسوم عن المبني.", "أول الكلمة مخطط، وآخرها بناء."],
         why="يحكي عمل الشركة كاملاً داخل اسمها: من الاستشارة إلى التنفيذ.",
         apps=("folder", "board"), min_icon=24),
    dict(n="03", name="الفراغ الحامل", slug="03-bearing-void",
         story="أقوى جزء في المشروع قد لا يُرى، لكنه يحمل كل ما يُرى.",
         build=["كتلة واحدة بزوايا ناعمة.", "فراغٌ يشقّها على شكل راء.", "القناة تضيق كلما ابتعدت، كما يضيق ذيل الراء بالقلم."],
         why="أوضح الرموز الستة بالحجم الصغير، ويُقرأ حرفاً عربياً من النظرة الأولى.",
         apps=("helmet", "avatar"), min_icon=16),
    dict(n="04", name="التوقيع العربي", slug="04-signature",
         story="اسم الشركة نفسه يصبح رمزها؛ توقيعٌ لا يُستبدل باسم آخر.",
         build=["حروف مرسومة بقلم متغيّر السماكة، لا بخط جاهز.", "رؤوس الألفات مقطوعة بزاوية القلم.", "ذيل الراء يمتد تحت الألف، والنقاط الأربع بالماروني."],
         why="علامة حروفية خاصة يمكن تسجيلها، ونسختها المختصرة «ية» من حروفها نفسها.",
         apps=("letter", "emboss"), min_icon=24),
    dict(n="05", name="نقطة التحول", slug="05-turning-point",
         story="بين الفكرة والمشروع نقطةٌ حاسمة؛ الراية هي التي تضبطها.",
         build=["مساران يلتقيان في نقطة واحدة.", "ويكملان خطاً واحداً إلى الأسفل.", "Y في ALRAYA، ونقطتا الياء في الراية."],
         why="يجمع الاسمين في حرف واحد، ويبقى واضحاً من 16px إلى لوحة الطريق.",
         apps=("car", "gate"), min_icon=16),
    dict(n="06", name="ختم الراية", slug="06-seal",
         story="علامة اعتماد توضع على المشروع، من أول مخطط إلى لحظة التسليم.",
         build=["ألف الراية تخترق حلقة التاء: أول حرف وآخر حرف.", "الاسم بالعربية أعلى الختم، وبالإنكليزية أسفله.", "نسخة بلا كتابة تبقى واضحة حتى 24px."],
         why="يلبّي الحاجة إلى ختم رسمي على المخططات والوثائق، بهدوء مؤسسي.",
         apps=("stamp", "vest"), min_icon=24),
]
BY = {x["n"]: x for x in D}
REC = [
    ("03", "يعمل من 16px إلى واجهة المكتب بلون واحد، ويُحفر ويُطرَّز بلا تبسيط. الراء فيه تربطه بالاسم مباشرة.",
     ["الوضوح", "الحجم الصغير", "التذكّر", "الإنتاج"]),
    ("04", "اسمٌ مرسوم لا يشبه أي خط جاهز، يمكن تسجيله، ويحمل الهوية العربية للشركة. نسخته المختصرة من حروفه نفسها.",
     ["التميّز", "الارتباط بالاسم", "صلاحية لسنوات", "العربي والإنكليزي"]),
]
APPS_DEFAULT = "03"

# ================================================================== geometry
SPRITE_KINDS = {
    "symbol": "symbol", "primary": "primary_ar", "horizontal": "ar_en", "stacked": "stacked", "descriptor": "descriptor",
}
LK = {}


def load():
    for x in D:
        LK[x["n"]] = I.lockups(x["n"])


def kind_layers(n, kind):
    lk = LK[n]
    if kind == "circular":
        return lk.get("circular")
    if kind == "stamp":
        return lk.get("circular") or lk["stacked"]
    if kind == "horizontal" and n in ("02", "04", "06"):
        return lk["horizontal"]
    return lk[SPRITE_KINDS[kind]]


FILL = {"p": "var(--p)", "a": "var(--a)", "h": "var(--h)"}


def paths(layers, nd=0, cls=None):
    groups = {}
    for p, r in layers:
        groups.setdefault(r, []).append(p)
    out = []
    for r in ("p", "h", "a"):
        if r in groups:
            c = f' class="{cls} r{r}"' if cls else ""
            out.append(f'<path{c} fill="{FILL[r]}" d="{"".join(pd(q, nd) for q in groups[r])}"/>')
    return "".join(out)


def sprite():
    out, dims = [], {}
    for x in D:
        n = x["n"]
        for kind in ("symbol", "primary", "horizontal", "stacked", "descriptor", "circular", "stamp"):
            layers = kind_layers(n, kind)
            if layers is None:
                continue
            layers = I.lorigin(layers)
            w, h = I.lsize(layers)
            out.append(f'<g id="G-{n}-{kind}">{paths(layers)}</g>')
            for al, par in (("c", "xMidYMid"), ("r", "xMaxYMid"), ("l", "xMinYMid")):
                out.append(f'<symbol id="L-{n}-{kind}-{al}" viewBox="0 0 {w:.0f} {h:.0f}" preserveAspectRatio="{par} meet"><use href="#G-{n}-{kind}"/></symbol>')
            dims[f"{n}-{kind}"] = (w, h)
    return "".join(out), dims


DIMS = {}


def use(n, kind, sch="full", cls="", al="c", label=""):
    w, h = DIMS[f"{n}-{kind}"]
    lab = f' role="img" aria-label="{label}"' if label else ' aria-hidden="true"'
    return (f'<svg class="{cls}" viewBox="0 0 {w:.0f} {h:.0f}"{lab}><use href="#L-{n}-{kind}-{al}" width="{w:.0f}" height="{h:.0f}" style="{M.SCH[sch]}"/></svg>')


# ------------------------------------------------------------------ scene geometry
def skel_d(sk):
    s = f"M{sk.segs[0][0][0]:.0f} {sk.segs[0][0][1]:.0f}"
    for (a, b, c, e) in sk.segs:
        s += f"C{b[0]:.0f} {b[1]:.0f} {c[0]:.0f} {c[1]:.0f} {e[0]:.0f} {e[1]:.0f}"
    return s


def norm_tf(raw_layers, H=1000):
    x0, y0, x1, y1 = I.lb(raw_layers)
    k = H / (y1 - y0)
    return (lambda x, y: ((x - x0) * k, (y - y0) * k)), k, (x0, y0)


def tfd(dstr, f, k):
    """Transform an svg path string of M/L/C absolute commands."""
    toks = re.findall(r"[MLCZ]|-?\d+\.?\d*", dstr)
    out, i, cmd = [], 0, None
    nums = []
    for tk in toks:
        if tk in "MLCZ":
            cmd = tk; out.append(tk)
        else:
            nums.append(float(tk))
            if len(nums) == 2:
                x, y = f(*nums); out.append(f"{x:.0f} {y:.0f}"); nums = []
    return " ".join(out)


def word_block(n, alif_h=300):
    lk = LK[n]
    if n in ("02", "04"):
        return None
    wd = I.word(n, alif_h)
    ww, wh = I.lsize(wd)
    en = [(I.en_name(wh * (0.16 if n == "06" else 0.15), 0.5), "p")]
    return I.right_align([wd, en], wh * 0.2)


def scene(x):
    """The pinned reveal for one direction. Elements carry --s/--e: the
    window of scroll progress in which they animate."""
    n = x["n"]
    st = lambda s, e: f'style="--s:{s};--e:{e}"'
    art, lines = "", ""
    if n == "01":
        raw = I.d01_symbol()
        f, k, _ = norm_tf(raw)
        sym = I.lheight(raw, 1000)
        alif, ra = [L for L in sym if L[1] == "p"], [L for L in sym if L[1] == "a"]
        la = tfd(skel_d(Skel(330, -10).L(330, 1060)), f, k)
        lr = tfd(skel_d(Skel(640, 250).L(640, 560).C(640, 800, 470, 930, -50, 950)), f, k)
        lines = (f'<path class="ln draw" pathLength="1" d="{la}" {st(.02, .22)}/>'
                 f'<path class="ln draw acc" pathLength="1" d="{lr}" {st(.12, .34)}/>')
        art = (f'<g class="fill grow" {st(.30, .48)}>{paths(alif)}</g>'
               f'<g class="fill grow" {st(.40, .58)}>{paths(ra)}</g>')
        box = I.lb(sym)
    elif n == "02":
        raw = I.d02_word()
        f, k, _ = norm_tf(raw, 600)
        wl = I.lheight(raw, 600)
        b2, d2 = I.d02_letters()
        solid = I.lheight([(I.union(b2, d2), "p")], 600)
        line = [L for L in wl if L[1] == "h"]
        from vec import outline, union as U
        hair = I.lheight([(outline(U(b2, d2), 7), "h")], 600)
        (cx0, cy0), (cx1, cy1) = I.D02_CUT
        a0, a1 = f(cx0, cy0), f(cx1, cy1)
        ang = math.degrees(math.atan2(a1[1] - a0[1], a1[0] - a0[0]))
        # the pour: solid letters clipped by a half-plane that rises to the cut
        base = f"translate({a0[0]:.0f} {a0[1]:.0f}) rotate({ang:.2f})"
        art = (f'<clipPath id="pour"><rect data-pour="0.30 0.62 -1100" data-base="{base}" x="-400" y="-2400" width="3400" height="2400" transform="{base} translate(0 -1100)"/></clipPath>'
               f'<g class="fill fade" {st(.02, .30)}>{paths(hair)}</g>'
               f'<g clip-path="url(#pour)">{paths(solid)}</g>'
               f'<line class="ln draw acc cutl" pathLength="1" x1="{a0[0]:.0f}" y1="{a0[1]:.0f}" x2="{a1[0]:.0f}" y2="{a1[1]:.0f}" {st(.22, .36)}/>')
        box = I.lb(wl)
    elif n == "03":
        raw = I.d03_symbol()
        f, k, _ = norm_tf(raw)
        tile = I.lheight([(I.squircle(0, 0, 1000), "p")], 1000)
        ch = tfd(skel_d(Skel(585, -60).L(585, 330).C(585, 620, 430, 790, 120, 850).C(40, 865, -20, 870, -80, 872)), f, k)
        sym = I.lheight(raw, 1000)
        art = (f'<g class="fill tile" {st(.02, .16)}>{paths(tile)}</g>'
               f'<path class="ln draw void" pathLength="1" d="{ch}" {st(.16, .48)}/>'
               f'<g class="fill fade" {st(.46, .56)}>{paths(sym)}</g>')
        box = I.lb(sym)
    elif n == "04":
        raw = I.d04_word()
        f, k, _ = norm_tf(raw, 700)
        wl = I.lheight(raw, 700)
        sk = [Skel(1390, -680).L(1390, 0), Skel(1195, -680).L(1195, -120).C(1195, -45, 1160, 0, 1090, 0).L(990, 0),
              Skel(1012, 0).C(972, 0, 950, 14, 945, 58).C(937, 172, 860, 268, 700, 300).C(620, 315, 560, 316, 500, 312),
              Skel(735, -650).L(735, 0), Skel(540, -230).L(540, -110).C(540, -40, 505, 0, 440, 0).L(300, 0),
              Skel(305, 0).C(170, 0, 90, -60, 90, -165).C(90, -270, 170, -330, 245, -330).C(330, -330, 390, -270, 390, -185).C(390, -90, 340, -28, 290, -8)]
        lines = "".join(f'<path class="ln draw" pathLength="1" d="{tfd(skel_d(s), f, k)}" {st(round(.02 + i * .06, 2), round(.14 + i * .06, 2))}/>' for i, s in enumerate(sk))
        art = (f'<g class="fill fade" {st(.44, .60)}>{paths([L for L in wl if L[1] == "p"])}</g>'
               f'<g class="fill drop" {st(.58, .70)}>{paths([L for L in wl if L[1] == "a"])}</g>')
        box = I.lb(wl)
    elif n == "05":
        raw = I.d05_symbol()
        f, k, _ = norm_tf(raw)
        sym = I.lheight(raw, 1000)
        L1 = tfd("M-300 0 L0 470", f, k); L2 = tfd("M300 0 L0 470", f, k); L3 = tfd("M0 470 L0 840", f, k)
        lines = (f'<path class="ln draw" pathLength="1" d="{L1}" {st(.02, .22)}/><path class="ln draw" pathLength="1" d="{L2}" {st(.02, .22)}/>'
                 f'<circle class="pt fade" cx="{f(0, 470)[0]:.0f}" cy="{f(0, 470)[1]:.0f}" r="16" {st(.20, .26)}/>'
                 f'<path class="ln draw acc" pathLength="1" d="{L3}" {st(.26, .40)}/>')
        art = (f'<g class="fill fade" {st(.40, .54)}>{paths([L for L in sym if L[1] == "p"])}</g>'
               f'<g class="fill drop" {st(.54, .66)}>{paths([L for L in sym if L[1] == "a"])}</g>')
        box = I.lb(sym)
    else:
        raw = I.d06_badge()
        f, k, _ = norm_tf(raw)
        sym = I.lheight(raw, 1000)
        core = I.lheight(I.d06_badge(lettered=False), 1000)
        c = f(0, 0)
        lines = f'<circle class="ln draw" pathLength="1" cx="{c[0]:.0f}" cy="{c[1]:.0f}" r="{500 * k:.0f}" {st(.02, .24)}/>'
        art = (f'<g class="fill fade" {st(.20, .40)}>{paths(core)}</g>'
               f'<g class="fill fade" {st(.40, .58)}>{paths(sym)}</g>')
        box = I.lb(sym)
    x0, y0, x1, y1 = box
    pad = 60
    vb = f"{x0 - pad:.0f} {y0 - pad:.0f} {x1 - x0 + 2 * pad:.0f} {y1 - y0 + 2 * pad:.0f}"
    return (f'<svg class="sc-art" viewBox="{vb}" role="img" aria-label="الشعار {n}" style="{M.SCH["full"]}">'
            f'{art}{lines}</svg>')


# ------------------------------------------------------------------ craft panels (real construction)
def craft(x):
    n = x["n"]
    G = "#7D161A"
    if n == "01":
        raw = I.d01_symbol()
        f, k, _ = norm_tf(raw)
        sym = I.lheight(raw, 1000)
        la = tfd(skel_d(Skel(330, -10).L(330, 1060)), f, k)
        lr = tfd(skel_d(Skel(640, 250).L(640, 560).C(640, 800, 470, 930, -50, 950)), f, k)
        cons = (f'<g opacity=".16">{paths(sym)}</g><path d="{la}" class="cl"/><path d="{lr}" class="cl"/>'
                + "".join(f'<circle cx="{f(*p)[0]:.0f}" cy="{f(*p)[1]:.0f}" r="9" class="nd"/>' for p in ((330, -10), (330, 1060), (640, 250), (640, 560), (-50, 950))))
        before = I.lheight([(I.union(I.vstroke(Skel(330, -10).L(330, 1060), 170), I.vstroke(Skel(640, 250).L(640, 560).C(640, 800, 470, 930, -50, 950), 170)), "p")], 1000)
        cap = ("المساران قبل السماكة: محور مستقيم للألف، ومنحنى واحد للراء.",
               "سماكة ثابتة: الذيل ثقيل والمفصل مغلق.", "الذيل يدقّ حتى نقطة، والراء تمرّ أمام الألف بفاصل ثابت.",
               "ارتفاع الألف 1.3 من ارتفاع الراء، فيقف المحور أعلى من المسار.")
        after = sym
    elif n == "02":
        wl = I.lheight(I.d02_word(), 600)
        f, k, _ = norm_tf(I.d02_word(), 600)
        (cx0, cy0), (cx1, cy1) = I.D02_CUT
        a0, a1 = f(cx0, cy0), f(cx1, cy1)
        b2, d2 = I.d02_letters()
        solid = I.lheight([(I.union(b2, d2), "p")], 600)
        grid = "".join(f'<line x1="{-200}" y1="{y:.0f}" x2="3000" y2="{y:.0f}" class="gl"/>' for y in (f(0, -600)[1], f(0, 0)[1], f(0, -230)[1]))
        cons = (f'{grid}<g opacity=".16">{paths(solid)}</g><line x1="{a0[0]:.0f}" y1="{a0[1]:.0f}" x2="{a1[0]:.0f}" y2="{a1[1]:.0f}" class="cl acc"/>')
        from vec import outline, union as U, inter, rect as R
        flatcut = I.lheight([(inter(U(b2, d2), R(-200, -300, 2000, 800)), "p"), (outline(I.diff(U(b2, d2), R(-200, -300, 2000, 800)), 7), "h")], 600)
        before, after = flatcut, wl
        cap = ("ثلاثة خطوط فقط: رأس الألف، ورأس الياء، والسطر. وخط القطع الصاعد بالماروني.",
               "قطع أفقي: يشبه منسوب صبّ، ولا يتقدّم مع القراءة.", "قطع صاعد: أول الكلمة خط، وآخرها كتلة.",
               "السماكة 86 وحدة في كل الحروف، والنقاط مربعات بالسماكة نفسها.")
    elif n == "03":
        sym = I.lheight(I.d03_symbol(), 1000)
        f, k, _ = norm_tf(I.d03_symbol())
        ch = tfd(skel_d(Skel(585, -60).L(585, 330).C(585, 620, 430, 790, 120, 850).C(40, 865, -20, 870, -80, 872)), f, k)
        cons = (f'<g opacity=".16">{paths(sym)}</g><path d="{ch}" class="cl acc"/>'
                f'<rect x="0" y="0" width="1000" height="1000" class="gl" fill="none"/>'
                f'<line x1="500" y1="-40" x2="500" y2="1040" class="gl"/><line x1="-40" y1="500" x2="1040" y2="500" class="gl"/>')
        from vec import diff as DF
        from pen import vstroke as VS
        even = I.lheight([(DF(I.squircle(0, 0, 1000), VS(Skel(585, -60).L(585, 330).C(585, 620, 430, 790, 120, 850).C(40, 865, -20, 870, -80, 872), 128)), "p")], 1000)
        before, after = even, sym
        cap = ("مسار الراء على مربع 1000×1000: الجذع يبدأ يمين المركز بـ 85 وحدة.",
               "قناة بعرض ثابت: تبدو طريقاً أكثر مما تبدو حرفاً.", "القناة تضيق من 128 إلى 46 وحدة: تصبح راءً مكتوبة.",
               "زوايا الكتلة بنصف قطر 20٪ ومقابض طويلة، فتبدو ناعمة لا مستديرة.")
    elif n == "04":
        wl = I.lheight(I.d04_word(), 700)
        f, k, _ = norm_tf(I.d04_word(), 700)
        sk = [Skel(1390, -680).L(1390, 0), Skel(1195, -680).L(1195, -120).C(1195, -45, 1160, 0, 1090, 0).L(990, 0),
              Skel(1012, 0).C(972, 0, 950, 14, 945, 58).C(937, 172, 860, 268, 700, 300).C(620, 315, 560, 316, 500, 312),
              Skel(735, -650).L(735, 0), Skel(540, -230).L(540, -110).C(540, -40, 505, 0, 440, 0).L(300, 0),
              Skel(305, 0).C(170, 0, 90, -60, 90, -165).C(90, -270, 170, -330, 245, -330).C(330, -330, 390, -270, 390, -185).C(390, -90, 340, -28, 290, -8)]
        cons = f'<g opacity=".16">{paths(wl)}</g>' + "".join(f'<path d="{tfd(skel_d(s), f, k)}" class="cl"/>' for s in sk)
        from pen import vstroke as VS
        before = I.lheight([(VS(Skel(1390, -680).L(1390, 0), 118), "p"), (VS(Skel(1195, -680).L(1195, 0), 118), "p")], 700)
        after = I.lheight([(VS(Skel(1390, -680).L(1390, 0), I.profile((0, 118 * .92), (.5, 118), (1, 118 * .86)), start=I.NIB), "p"),
                           (VS(Skel(1195, -680).L(1195, 0), I.profile((0, 118 * .92), (.5, 118), (1, 118 * .86)), start=I.NIB), "p")], 700)
        cap = ("ستة مسارات للقلم، تُرسم بترتيب القراءة من اليمين.",
               "ألف بسماكة ثابتة ورأس مستقيم: يبدو مقصوصاً بالمسطرة.", "انتفاخ خفيف في الوسط ورأس بزاوية القلم 28°: يبدو مكتوباً.",
               "الألف أطول من السطر بـ 3.8 مرة من سماكتها، وذيل الراء ينزل تحت السطر بقدر ارتفاع الياء.")
    elif n == "05":
        sym = I.lheight(I.d05_symbol(), 1000)
        f, k, _ = norm_tf(I.d05_symbol())
        L1, L2, L3 = tfd("M-300 0 L0 470", f, k), tfd("M300 0 L0 470", f, k), tfd("M0 470 L0 840", f, k)
        j = f(0, 470)
        cons = (f'<g opacity=".16">{paths(sym)}</g><path d="{L1}" class="cl"/><path d="{L2}" class="cl"/><path d="{L3}" class="cl acc"/>'
                f'<circle cx="{j[0]:.0f}" cy="{j[1]:.0f}" r="14" class="nd"/>')
        from vec import union as U, diff as DF, rect as R, stroke as S, diamond as DM
        notch = I.lheight([(U(DF(S(P().M(-300, 0).L(0, 470).L(300, 0).path(), 178, "butt", "miter"), R(-2000, -2000, 4000, 2000)), R(-89, 520, 178, 320)), "p"),
                           (U(DM(-100, 990, 166), DM(100, 990, 166)), "a")], 1000)
        before, after = notch, sym
        cap = ("ثلاثة مسارات تلتقي في نقطة واحدة على ارتفاع 56٪.",
               "فصل أفقي: الحرف ينقسم إلى قطعتين بلا معنى.", "الذراع اليمنى تدخل تحت اليسرى: الالتقاء هو الفكرة.",
               "زاوية الذراعين 32° عن العمود، والنقطتان بعرض الجذع تقريباً.")
    else:
        sym = I.lheight(I.d06_badge(), 1000)
        f, k, _ = norm_tf(I.d06_badge())
        c = f(0, 0)
        cons = (f'<g opacity=".16">{paths(sym)}</g>' + "".join(f'<circle cx="{c[0]:.0f}" cy="{c[1]:.0f}" r="{r * k:.0f}" class="cl{a}"/>' for r, a in ((500, ""), (330, ""), (415, " acc"))))
        from vec import union as U, diff as DF, circle as C, rect as R
        rin = 0.66 * 500
        R0 = rin * 0.88
        flat = I.lheight([(U(DF(C(0, 0, 500), C(0, 0, rin)), DF(C(0, 0, 0.5 * R0), C(0, 0, 0.3 * R0))), "p"), (R(-0.09 * R0, -0.95 * R0, 0.18 * R0, 1.85 * R0), "a")], 1000)
        before, after = flat, I.lheight(I.d06_badge(lettered=False), 1000)
        cap = ("ثلاث دوائر: حافة الختم، وحافة المركز، وخط الكتابة بينهما.",
               "حلقة هندسية بسماكة ثابتة: تشبه رمزاً تقنياً عاماً.", "حلقة التاء بسماكة القلم، والألف تمرّ فوقها من أسفل وتحتها من أعلى.",
               "الكتابة على خط وسط الحزام تماماً، والعربي أكبر من الإنكليزي بثلاث مرات تقريباً.")
    W, H = I.lsize(after)

    def fig(layers, extra_cls=""):
        x0, y0, x1, y1 = I.lb(layers)
        p = 40
        return f'<svg viewBox="{x0 - p:.0f} {y0 - p:.0f} {x1 - x0 + 2 * p:.0f} {y1 - y0 + 2 * p:.0f}" aria-hidden="true" style="{M.SCH["black"]}">{paths(layers)}</svg>'
    x0, y0, x1, y1 = I.lb(after)
    p = 60
    consvg = f'<svg class="cons" viewBox="{x0 - p:.0f} {y0 - p:.0f} {x1 - x0 + 2 * p:.0f} {y1 - y0 + 2 * p:.0f}" aria-hidden="true" style="{M.SCH["black"]}">{cons}</svg>'
    return f'''<div class="craft" data-r>
  <figure class="cf cf-c fx">{consvg}<figcaption>{cap[0]}</figcaption></figure>
  <div class="cf-ba">
    <figure class="cf fx" style="--dl:.08s"><span class="tag">قبل</span>{fig(before)}<figcaption>{cap[1]}</figcaption></figure>
    <figure class="cf fx" style="--dl:.16s"><span class="tag on">بعد</span>{fig(after)}<figcaption>{cap[2]}</figcaption></figure>
  </div>
  <p class="cf-n fx" style="--dl:.22s">{cap[3]}</p>
</div>'''


# ================================================================== sections
def opening():
    return '''<header class="open" id="top" data-nav="البداية">
  <svg class="op-line" viewBox="0 0 1000 20" preserveAspectRatio="none" aria-hidden="true"><path d="M0 10 H1000" pathLength="1"/><rect class="op-mass" x="0" y="4" width="1000" height="12"/></svg>
  <p class="op-1">قبل أن يُبنى المشروع… تُبنى الفكرة.</p>
  <h1 class="op-2">الراية</h1>
  <p class="op-3">ستة اتجاهات. هوية واحدة ستقود المرحلة القادمة.</p>
  <p class="op-sig"><span>هوية بصرية وتصميم</span><b>عَدول</b><i dir="ltr">Adol</i></p>
  <a class="op-cue" href="#story" aria-label="ابدأ العرض"><i></i></a>
</header>'''


def story():
    return '''<section class="story sec" id="story" data-nav="الراية" data-r>
  <p class="kick fx">الراية · ALRAYA</p>
  <p class="st-1 fx" style="--dl:.06s">شركة مقاولات عامة واستشارات هندسية.<br>ترسم المشروع، ثم تبنيه.</p>
  <p class="st-2 fx" style="--dl:.14s">الشعار المطلوب يُقرأ على مخطط بحجم الكف، وعلى لوحة موقع من بعيد؛ بالعربية أولاً، والإنكليزية معها.</p>
</section>'''


def lineup(id_, nav, title, sub, sch="black", bg=""):
    cells = "".join(f'<a class="lu-c fx" style="--dl:{i * .05:.2f}s" href="#d{x["n"]}">{use(x["n"], "horizontal", sch, "lu-l", label=x["name"])}'
                    f'<span><i dir="ltr">{x["n"]}</i>{x["name"]}</span></a>' for i, x in enumerate(D))
    return f'''<section class="lineup sec {bg}" id="{id_}" data-nav="{nav}" data-r>
  <div class="sec-h"><h2 class="fx">{title}</h2><p class="sub fx" style="--dl:.06s">{sub}</p></div>
  <div class="lu-g">{cells}</div>
</section>'''


def chapter(i, x):
    n = x["n"]
    apps = "".join(f'<figure class="ca fx" style="--dl:{j * .08:.2f}s">{dict((a, f) for a, _, f in M.ALL)[k](n, uid=f"c{n}{k}", sw=False)}<figcaption>{dict((a, nm) for a, nm, _ in M.ALL)[k]}</figcaption></figure>'
                   for j, k in enumerate(x["apps"]))
    build = "".join(f"<li>{b}</li>" for b in x["build"])
    return f'''<section class="chap d{n}" id="d{n}" data-nav="{n} · {x["name"]}">
  <div class="scene" data-scene>
    <div class="pin">
      <div class="sc-h"><span class="sc-n" dir="ltr">{n}<i>/06</i></span><h2>{x["name"]}</h2></div>
      {scene(x)}
      <p class="sc-story">{x["story"]}</p>
    </div>
  </div>
  <div class="after">
    <div class="proof" data-r>
      <div class="pf pf-w fx">{use(n, "horizontal", "black", "pf-l")}</div>
      <div class="pf pf-b fx" style="--dl:.08s">{use(n, "horizontal", "white", "pf-l")}</div>
      <div class="pf pf-s fx" style="--dl:.16s">{use(n, "symbol", "black", "pf-i")}</div>
    </div>
    <div class="txt" data-r>
      <ul class="bl fx">{build}</ul>
      <p class="why fx" style="--dl:.1s"><span>لماذا يناسب الراية</span>{x["why"]}</p>
    </div>
    {craft(x)}
    <div class="ch-apps" data-r>{apps}</div>
  </div>
</section>'''


def apps():
    chips = "".join(f'<button type="button" class="chip{" on" if x["n"] == APPS_DEFAULT else ""}" data-k="{x["n"]}" aria-pressed="{"true" if x["n"] == APPS_DEFAULT else "false"}"><i dir="ltr">{x["n"]}</i>{x["name"]}</button>' for x in D)
    figs = ""
    wide = {"vest", "insta"}
    for k, nm, fn in M.ALL:
        cls = "w2" if k in wide else "w1"
        figs += f'<figure class="ap {cls} fx">{fn(APPS_DEFAULT, uid="a" + k)}<figcaption>{nm}</figcaption></figure>'
    return f'''<section class="apps sec" id="apps" data-nav="التطبيقات">
  <div class="sec-h" data-r><h2 class="fx">الشعار في عمل الشركة</h2><p class="sub fx" style="--dl:.06s">اختر اتجاهاً: يتغيّر الشعار في كل التطبيقات معاً، والنسخة المختصرة هي المعتمدة من الشعار نفسه.</p></div>
  <div class="switch" role="group" aria-label="اختيار الاتجاه">{chips}</div>
  <div class="ap-g" data-r>{figs}</div>
</section>'''


def recommend():
    cards = ""
    for i, (n, why, crit) in enumerate(REC):
        chips = "".join(f"<li>{c}</li>" for c in crit)
        cards += (f'<article class="rc fx" style="--dl:{.08 + i * .12:.2f}s"><div class="rc-l">{use(n, "horizontal", "rev", "rl")}</div>'
                  f'<h3><i dir="ltr">{n}</i>{BY[n]["name"]}</h3><p>{why}</p><ul>{chips}</ul></article>')
    return f'''<section class="rec" id="rec" data-nav="التوصية"><div class="rec-in" data-r>
  <h2 class="fx">نرشّح اتجاهين</h2>
  <p class="sub fx" style="--dl:.05s">المعيار: الوضوح، والتميّز، والارتباط بالشركة، وقابلية التطبيق، والصلاحية لسنوات، والعمل بالعربي والإنكليزي، والتذكّر بعد نظرة واحدة.</p>
  <div class="rc-g">{cards}</div>
  <p class="rec-n fx" style="--dl:.4s">إذا كانت الأولوية للطابع المؤسسي التقليدي، يبقى «ختم الراية» (06) الخيار الأهدأ.</p>
</div></section>'''


def early(v1syms, v1vb, v2groups, v2vb):
    old1 = [("01", "المقياس"), ("02", "السارية"), ("03", "الشدّة"), ("04", "الركيزة"), ("05", "الخاتَم"), ("06", "نقطة الإسناد")]
    old2 = [("01", "الشبكة"), ("02", "الختم"), ("03", "الطيّة"), ("04", "الزاوية"), ("05", "التعاشق")]
    c1 = "".join(f'<figure><svg viewBox="{v1vb[n]}" aria-hidden="true"><use href="#O1-{n}" x="{v1vb[n].split()[0]}" y="{v1vb[n].split()[1]}" width="{v1vb[n].split()[2]}" height="{v1vb[n].split()[3]}"/></svg><figcaption>{nm}</figcaption></figure>' for n, nm in old1)
    c2 = "".join(f'<figure><svg viewBox="{v2vb[n]}" aria-hidden="true" style="{M.SCH["full"]}"><use href="#O2-{n}"/></svg><figcaption>{nm}</figcaption></figure>' for n, nm in old2)
    return f'''<section class="early sec" id="early" data-nav="الاستكشافات الأولى">
  <details class="ex" data-r>
    <summary class="fx"><span>الاستكشافات الأولى</span><em>مرحلة بحث سابقة: الجولة الأولى والثانية. ليست ضمن الخيارات.</em><i aria-hidden="true"></i></summary>
    <div class="ex-in">
      <p class="ex-t">الجولة الأولى</p><div class="ex-g">{c1}</div>
      <p class="ex-t">الجولة الثانية</p><div class="ex-g">{c2}</div>
      <p class="ex-n">النسختان الكاملتان محفوظتان للرجوع: <a href="v1/">v1</a> · <a href="v2/">v2</a></p>
    </div>
  </details>
</section>'''


def ending():
    return '''<footer class="end" id="end" data-nav="الخاتمة"><div class="end-in" data-r>
  <p class="end-q fx">الشعار الذي سنختاره اليوم،<br>سيوقّع مشاريع الراية لسنوات.</p>
  <p class="end-sig fx" style="--dl:.2s"><span>هوية بصرية وتصميم</span><b>عَدول</b><i dir="ltr">Adol</i></p>
</div></footer>'''


def nav():
    items = [("top", "البداية"), ("story", "الراية"), ("board", "الاتجاهات الستة")] + [(f"d{x['n']}", f"{x['n']} · {x['name']}") for x in D] + \
            [("compare", "المقارنة"), ("apps", "التطبيقات"), ("rec", "التوصية"), ("early", "الاستكشافات الأولى"), ("end", "الخاتمة")]
    links = "".join(f'<a href="#{i}"><i></i><span>{t}</span></a>' for i, t in items)
    return (f'<nav class="nav" aria-label="أقسام العرض">{links}</nav>'
            f'<div class="mbar"><button type="button" class="mbar-b" aria-expanded="false" aria-controls="mbar-l"><span class="mbar-c">البداية</span><i></i></button>'
            f'<div class="mbar-p"><i></i></div><nav class="mbar-l" id="mbar-l" aria-label="أقسام العرض">{links}</nav></div>')


# ================================================================== old versions
def old_assets():
    v1 = open(os.path.join(ROOT, "v1", "index.html"), encoding="utf-8").read()
    v1syms, v1vb = [], {}
    for n in ("01", "02", "03", "04", "05", "06"):
        m = re.search(r'<symbol id="M-%s-lockup-full" viewBox="([^"]+)">(.*?)</symbol>' % n, v1, re.S)
        v1vb[n] = m.group(1)
        v1syms.append(f'<symbol id="O1-{n}" viewBox="{m.group(1)}">{m.group(2)}</symbol>')
    v2 = open(os.path.join(ROOT, "v2", "index.html"), encoding="utf-8").read()
    v2g, v2vb = [], {}
    for n in ("01", "02", "03", "04", "05"):
        g = re.search(r'<g id="G-%s-lockup">(.*?)</g>' % n, v2, re.S).group(1)
        vb = re.search(r'<symbol id="L-%s-lockup-c" viewBox="([^"]+)"' % n, v2).group(1)
        v2vb[n] = vb
        v2g.append(f'<g id="O2-{n}">{g}</g>')
    return v1syms, v1vb, v2g, v2vb


# ================================================================== fonts
FACES = [
    ("PlexAr", 400, "ibm-plex-sans-arabic-arabic-400-normal.woff2", "ar"),
    ("PlexAr", 400, "ibm-plex-sans-arabic-latin-400-normal.woff2", "la"),
    ("PlexAr", 500, "ibm-plex-sans-arabic-arabic-500-normal.woff2", "ar"),
    ("PlexAr", 500, "ibm-plex-sans-arabic-latin-500-normal.woff2", "la"),
    ("PlexAr", 600, "ibm-plex-sans-arabic-arabic-600-normal.woff2", "ar"),
    ("PlexAr", 600, "ibm-plex-sans-arabic-latin-600-normal.woff2", "la"),
    ("PlexAr", 700, "ibm-plex-sans-arabic-arabic-700-normal.woff2", "ar"),
    ("PlexAr", 700, "ibm-plex-sans-arabic-latin-700-normal.woff2", "la"),
    ("PlexMono", 500, "ibm-plex-mono-latin-500-normal.woff2", "la"),
]
RANGES = {"ar": "U+0600-06FF,U+200C-200F,U+FB50-FDFF,U+FE70-FEFC", "la": "U+0000-00FF,U+2010-2027,U+2030-206F,U+2212"}


def font_css(chars):
    css = []
    for fam, wt, fn, rg in FACES:
        f = TTFont(os.path.join(FONTS, fn))
        cmap = f.getBestCmap()
        want = [ord(c) for c in chars if ord(c) in cmap]
        o = subset.Options(); o.layout_features = ["*"]; o.flavor = "woff2"; o.name_IDs = []; o.notdef_outline = True
        s = subset.Subsetter(o); s.populate(unicodes=want); s.subset(f)
        b = io.BytesIO(); f.flavor = "woff2"; f.save(b)
        css.append(f'@font-face{{font-family:"{fam}";src:url(data:font/woff2;base64,{base64.b64encode(b.getvalue()).decode()}) format("woff2");'
                   f'font-weight:{wt};font-style:normal;font-display:swap;unicode-range:{RANGES[rg]}}}')
    return "".join(css)


# ================================================================== assemble
def build():
    global DIMS
    load()
    spr, DIMS = sprite()
    v1s, v1vb, v2g, v2vb = old_assets()
    body = "".join([
        '<div class="prog" aria-hidden="true"><i></i></div>', nav(), "<main>",
        opening(), story(),
        lineup("board", "الاتجاهات الستة", "الاتجاهات الستة", "بالأسود فقط، والحجم البصري نفسه. الشكل قبل القصة."),
        "".join(chapter(i, x) for i, x in enumerate(D)),
        lineup("compare", "المقارنة", "المقارنة", "الستة معاً بالشروط نفسها: أسود، والحجم نفسه، والخلفية نفسها، بلا موكابات."),
        apps(), recommend(), early(v1s, v1vb, v2g, v2vb), ending(), "</main>",
    ])
    sprite_svg = ('<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>'
                  + spr + "".join(v1s) + "".join(v2g) + "</defs></svg>")
    css = open(os.path.join(TOOLS, "site3.css"), encoding="utf-8").read()
    js = open(os.path.join(TOOLS, "site3.js"), encoding="utf-8").read()
    visible = re.sub(r"<[^>]+>", " ", body) + "ALRAYA·—–«»،؛؟0123456789px/×±%:.()@°"
    html = ('<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
            '<meta name="theme-color" content="#1B2046">'
            '<title>الراية — ستة اتجاهات للهوية</title>'
            '<meta name="description" content="ستة اتجاهات لشعار الراية للمقاولات العامة والاستشارات الهندسية. هوية بصرية وتصميم: عَدول.">'
            f'<style>{font_css(set(visible))}{css}</style></head><body>{sprite_svg}{body}<script>{js}</script></body></html>')
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(html)
    print(f"index.html {len(html) / 1024:.0f} KB")


if __name__ == "__main__":
    build()
