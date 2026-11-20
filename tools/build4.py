"""Builds index.html — ALRAYA identity, six directions (v4).

    python3 tools/build4.py

Earlier versions stay untouched in v1/, v2/ and v3/.
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
import identity4 as I
import letters as Lt
import mock3 as M
from vec import d as pd, bounds, rect
from build3 import font_css, old_assets

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.dirname(__file__)

D = [
    dict(n="01", name="الكتلة والفراغ", tag="رمز",
         origin="بدأت من الراء كما تُكتب داخل الكلمة: متصلةً باللام، على سطر الكتابة.",
         form="الراء نفسها صارت فراغاً يشقّ كتلةً صلبة. الكتلة لا تُقرأ من دون الفراغ.",
         link="في البناء، ما يحمل المشروع غالباً لا يُرى. هنا يصبح هذا الجزء الخفي هو الحرف.",
         craft=("خط الوسط للراء مأخوذ من راء الكلمة نفسها ومكبَّر 1.55 مرة، وعرضه عرض قلم الكلمة.",
                "قبل: شقٌّ مستقيم. يقسم الكتلة ولا يقول شيئاً.", "بعد: راء متصلة تدخل من سطر الكتابة وتخرج من الأسفل."),
         apps=("helmet", "vest"), min_sym=16),
    dict(n="02", name="الخط المرسوم", tag="كلمة",
         origin="بدأت من قلم المخطط الهندسي: سماكة واحدة لا تتغير، وطرف مدوّر.",
         form="الكلمة كلها مرسومة بخط واحد، كما تُرسم المحاور والحدود على المخطط.",
         link="الاستشارة الهندسية تبدأ بخط دقيق على الورق. هذا الاتجاه يقدّم الراية من جهة التصميم.",
         craft=("ثلاثة خطوط تضبط الكلمة: رأس الألف واللام، ورأس الياء، والسطر. والراء والياء تنزلان بالعمق نفسه.",
                "قبل: مسافات غير متساوية بين الحروف المنفصلة.", "بعد: الفراغ بين ا | لـ ، ر | ا ، ا | يـ واحد."),
         apps=("folder", "letter"), min_sym=24),
    dict(n="03", name="الملتقى", tag="رمز ثنائي",
         origin="بدأت من حرف مشترك: الياء في «الراية» وY في «ALRAYA»، في الموضع الخامس من الاسمين.",
         form="مساران يلتقيان في نقطة واحدة ويكملان خطاً واحداً، ونقطتا الياء تحت الحرف.",
         link="الاستشارة والتنفيذ مساران يلتقيان في شركة واحدة، والاسمان العربي والإنكليزي في حرف واحد.",
         craft=("ثلاثة محاور تلتقي على ارتفاع 56٪ من الحرف. النقطتان مربعتان مثل نقاط الكلمة.",
                "قبل: نقطتان على شكل معيّن: زخرفة لا علاقة لها بالحروف.", "بعد: نقطتان مربعتان بقلم الكلمة نفسه."),
         apps=("car", "avatar"), min_sym=16),
    dict(n="04", name="الخاتمة", tag="رمز من الكلمة",
         origin="بدأت من نهاية الاسم: «ية»، الحلقة المغلقة والنقاط الأربع.",
         form="حلقة التاء مغلقة كعمل مكتمل، والنقاط الأربع هي كل نقاط الاسم.",
         link="الراية تُعرف بما تسلّمه في النهاية: مشروعٌ مكتمل.",
         craft=("الياء والتاء ونقاطهما كما هي في الكلمة، بلا تكبير ولا تعديل.",
                "قبل: حلقة دائرية مثالية: تبدو حرف «o» لاتينياً.", "بعد: حلقة أعرض قليلاً من ارتفاعها، تجلس على السطر كتاء عربية."),
         apps=("desk", "insta"), min_sym=16),
    dict(n="05", name="الكوفي الهندسي", tag="كلمة",
         origin="بدأت من المسطرة والزاوية: خطوط مستقيمة، وانعطافات بزاوية 45°.",
         form="كل حرف مبني من خطوط مستقيمة بسماكة واحدة؛ الحلقة مثمّنة، والنقاط مربعات بعرض الخط.",
         link="يشبه طريقة الرسم في الموقع: قياسات واضحة وزوايا محسوبة، ويُنفَّذ بسهولة بالقص والطلاء.",
         craft=("كل انعطاف مقطوع بزاوية 45° بطول يساوي عرض الخط تقريباً.",
                "قبل: زوايا قائمة حادة: الحروف تبدو صناديق.", "بعد: الانعطاف المقطوع يعيد للحرف حركته العربية."),
         apps=("board", "helmet"), min_sym=24),
    dict(n="06", name="ختم الراية", tag="ختم",
         origin="بدأ من ختم الاعتماد الدائري الذي يوضع على المخططات والوثائق.",
         form="الاسم بالعربية أعلى الحلقة وبالإنكليزية أسفلها، وفي المركز راءٌ واحدة بالقلم المدوّر.",
         link="علامة هادئة للوثائق والمراسلات الرسمية، تُعرف من مركزها وحده حتى من دون الكتابة.",
         craft=("ثلاث دوائر: حافة الختم، وحافة المركز، وخط الكتابة بينهما في المنتصف تماماً.",
                "قبل: مركز فارغ: حلقة كتابة بلا علامة.", "بعد: راء واحدة في المركز تكفي لتعريف الختم."),
         apps=("letter", "vest"), min_sym=24),
]
BY = {x["n"]: x for x in D}
REC = [("01", "أقوى رمز بين الستة: يبقى واضحاً بحجم 16px، ويعمل بلون واحد على الخوذة والفست والسيارة، والراء فيه من الكلمة نفسها."),
       ("03", "يجمع الاسمين العربي والإنكليزي في حرف واحد، ويُقرأ من بعيد على اللوحات والسيارات، ونقاطه من نقاط الكلمة.")]
APPS = ("helmet", "vest", "desk", "letter", "folder", "board", "car", "avatar", "insta")
APPS_DEFAULT = "01"
LK, DIMS = {}, {}
FILL = {"p": "var(--p)", "a": "var(--a)", "h": "var(--h)"}


def paths(layers, nd=0, cls=None):
    out = []
    for p, r in layers:
        c = f' class="{cls}"' if cls else ""
        out.append(f'<path{c} fill="{FILL[r]}" d="{pd(p, nd)}"/>')
    return "".join(out)


def kind_layers(n, kind):
    lk = LK[n]
    if kind == "primary":
        kind = "primary_ar"
    if kind == "stamp":
        return lk.get("circular") or lk["stacked"]
    if kind == "circular":
        return lk.get("circular")
    return lk.get(kind)


def sprite():
    out = []
    for x in D:
        n = x["n"]
        for kind in ("symbol", "word", "horizontal", "stacked", "descriptor", "circular", "stamp"):
            layers = kind_layers(n, kind)
            if not layers:
                continue
            layers = I.lorigin(layers)
            w, h = I.lsize(layers)
            out.append(f'<g id="G-{n}-{kind}">{paths(layers)}</g>')
            for al, par in (("c", "xMidYMid"), ("r", "xMaxYMid"), ("l", "xMinYMid")):
                out.append(f'<symbol id="L-{n}-{kind}-{al}" viewBox="0 0 {w:.0f} {h:.0f}" preserveAspectRatio="{par} meet"><use href="#G-{n}-{kind}"/></symbol>')
            DIMS[f"{n}-{kind}"] = (w, h)
    return "".join(out)


def use(n, kind, sch="full", cls="", label=""):
    w, h = DIMS[f"{n}-{kind}"]
    lab = f' role="img" aria-label="{label}"' if label else ' aria-hidden="true"'
    return f'<svg class="{cls}" viewBox="0 0 {w:.0f} {h:.0f}"{lab}><use href="#L-{n}-{kind}-c" width="{w:.0f}" height="{h:.0f}" style="{M.SCH[sch]}"/></svg>'


# ------------------------------------------------------------------ scenes
def scene(n):
    sd = I.scene_data(n)
    st = lambda s, e: f'style="--s:{s};--e:{e}"'
    fin = sd["final"]
    art = ""
    if n == "01":
        art += f'<g class="fill tile" {st(.02, .14)}>{paths([(sd["block"], "p")])}</g>'
        for dd, w, cap in sd["lines"]:
            art += f'<path class="pen void" pathLength="1" d="{dd}" stroke-width="{w:.0f}" stroke-linecap="{cap}" {st(.14, .52)}/>'
        art += f'<g class="fill fade" {st(.50, .56)}>{paths(fin)}</g>'
    elif n in ("02", "04", "05"):
        k = len(sd["lines"])
        for i, (dd, w, cap) in enumerate(sd["lines"]):
            s0 = .04 + i * (.42 / k)
            art += f'<path class="pen ink" pathLength="1" d="{dd}" stroke-width="{w:.1f}" stroke-linecap="{cap}" stroke-linejoin="{"round" if cap == "round" else "miter"}" {st(round(s0, 3), round(s0 + .42 / k * 1.4, 3))}/>'
        acc = "var(--a)" if n in ("04", "05") else "var(--p)"
        for x, y, r in sd.get("dots", []):
            art += f'<circle class="drop" cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{acc}" {st(.48, .58)}/>'
        for x, y, s in sd.get("rects", []):
            art += f'<rect class="drop" x="{x:.1f}" y="{y:.1f}" width="{s:.1f}" height="{s:.1f}" fill="{acc}" {st(.48, .58)}/>'
        art += f'<g class="fill fade" {st(.58, .62)}>{paths(fin)}</g>'
    elif n == "03":
        for i, (dd, w, cap) in enumerate(sd["lines"]):
            s0 = (.04, .04, .26)[i]
            art += f'<path class="pen guide{" acc" if i == 2 else ""}" pathLength="1" d="{dd}" {st(s0, s0 + .2)}/>'
        art += f'<g class="fill fade" {st(.40, .52)}>{paths([L for L in fin if L[1] == "p"])}</g>'
        art += f'<g class="fill drop" {st(.52, .62)}>{paths([L for L in fin if L[1] == "a"])}</g>'
    else:
        art += f'<circle class="pen guide" pathLength="1" cx="0" cy="0" r="500" {st(.02, .22)}/>'
        art += f'<g class="fill fade" {st(.18, .36)}>{paths([L for L in fin if L[1] == "p"])}</g>'
        art += f'<g class="fill grow" {st(.36, .54)}>{paths([L for L in fin if L[1] == "a"])}</g>'
    x0, y0, x1, y1 = I.lb(fin)
    p = max(x1 - x0, y1 - y0) * 0.05
    return (f'<svg class="sc-art" viewBox="{x0 - p:.0f} {y0 - p:.0f} {x1 - x0 + 2 * p:.0f} {y1 - y0 + 2 * p:.0f}" role="img" aria-label="{BY[n]["name"]}" style="{M.SCH["full"]}">{art}</svg>')


# ------------------------------------------------------------------ craft (real construction)
def craft(x):
    n = x["n"]
    import math
    from vec import union, diff, stroke, P, circle
    from identity4 import block, void_ra, sym03, sym01
    lines = ""
    if n in ("02", "05", "04"):
        if n == "05":
            l, dd, pr = Lt.angular()
            final = [(l, "p"), (dd, "p")]
            W, A, T, Dd = pr["W"], 560, 210, 200
            cen = "".join(f'<path d="{pd(p)}" class="cl"/>' for p in pr["centre"])
        else:
            st = Lt.STYLES["line" if n == "02" else "round"]
            l, dd = Lt.word(st)
            final = [(l, "p"), (dd, "p")]
            W, A, T, Dd = st.W, st.A, st.T, st.D
            from build_util import skel_d
            sk, dots, _ = Lt.skeleton(st)
            cen = "".join(f'<path d="{skel_d(s)}" class="cl"/>' for s, _ in sk)
        x0, y0, x1, y1 = I.lb(final)
        lines = "".join(f'<line x1="{x0 - 80:.0f}" y1="{y:.0f}" x2="{x1 + 80:.0f}" y2="{y:.0f}" class="gl"/><text x="{x1 + 90:.0f}" y="{y + 8:.0f}" class="ml">{t}</text>'
                        for y, t in ((-A, "A"), (-T, "T"), (0, "0"), (Dd, "D")))
        cons = f'<g opacity=".14">{paths(final)}</g>{lines}{cen}'
        if n == "02":
            st = Lt.STYLES["line"]
            bad = Lt.Style("bad", W=st.W, A=st.A, T=st.T, D=st.D, G=st.G * 0.55, pen="round", dot=st.dot)
            lb_, db_ = Lt.word(bad)
            before = [(lb_, "p"), (db_, "p")]
            after = final
        elif n == "05":
            l2, d2, _ = Lt.angular(c=0.01)
            before, after = [(l2, "p"), (d2, "p")], final
        else:
            pr = Lt.parts(Lt.STYLES["round"])
            ya = pr["ya"]; tdots = pr["ta_dots"]; ydots = pr["ya_dots"]
            lx0, ly0, lx1, ly1 = bounds(pr["loop"])
            r = (ly1 - ly0) / 2
            circ = diff(circle((lx0 + lx1) / 2, (ly0 + ly1) / 2, r), circle((lx0 + lx1) / 2, (ly0 + ly1) / 2, r - Lt.STYLES["round"].W))
            before = [(union(ya, circ), "p"), (union(tdots, ydots), "p")]
            after = [(pr["yata"], "p"), (union(tdots, ydots), "p")]
    elif n == "01":
        final = sym01()
        v, sk = void_ra()
        from build_util import skel_d
        cons = (f'<g opacity=".14">{paths(final)}</g><rect x="0" y="0" width="1000" height="1000" class="gl" fill="none"/>'
                f'<line x1="-40" y1="360" x2="1040" y2="360" class="gl"/><path d="{skel_d(sk)}" class="cl acc"/>')
        before = [(diff(block(), rect(430, -10, 150, 1020)), "p")]
        after = final
    elif n == "03":
        final = sym03()
        cons = (f'<g opacity=".14">{paths(final)}</g><path d="M-300 0L0 470" class="cl"/><path d="M300 0L0 470" class="cl"/><path d="M0 470L0 840" class="cl acc"/>'
                f'<circle cx="0" cy="470" r="14" class="nd"/>')
        from vec import diamond
        f = sym03()
        before = [L for L in f if L[1] == "p"] + [(union(diamond(-90, 1000, 150), diamond(90, 1000, 150)), "p")]
        after = final
    else:
        final = I.badge06()
        cons = (f'<g opacity=".14">{paths(final)}</g>' + "".join(f'<circle cx="0" cy="0" r="{r}" class="cl{a}"/>' for r, a in ((500, ""), (330, ""), (415, " acc"))))
        before = I.badge06()
        before = [L for L in before if L[1] == "p"]
        after = final
    x0, y0, x1, y1 = I.lb(final)
    pad = max(x1 - x0, y1 - y0) * 0.08
    consvg = f'<svg class="cons" viewBox="{x0 - pad:.0f} {y0 - pad:.0f} {x1 - x0 + 2 * pad + (220 if lines else 0):.0f} {y1 - y0 + 2 * pad:.0f}" aria-hidden="true" style="{M.SCH["black"]}">{cons}</svg>'

    def fig(layers):
        a0, b0, a1, b1 = I.lb(layers)
        q = max(a1 - a0, b1 - b0) * 0.06
        return f'<svg viewBox="{a0 - q:.0f} {b0 - q:.0f} {a1 - a0 + 2 * q:.0f} {b1 - b0 + 2 * q:.0f}" aria-hidden="true" style="{M.SCH["black"]}">{paths(layers)}</svg>'
    c = x["craft"]
    return f'''<div class="craft" data-r>
  <figure class="cf cf-c fx">{consvg}<figcaption>{c[0]}</figcaption></figure>
  <div class="cf-ba">
    <figure class="cf fx" style="--dl:.08s"><span class="tag">قبل</span>{fig(before)}<figcaption>{c[1]}</figcaption></figure>
    <figure class="cf fx" style="--dl:.16s"><span class="tag on">بعد</span>{fig(after)}<figcaption>{c[2]}</figcaption></figure>
  </div>
</div>'''


# ------------------------------------------------------------------ sections
def opening():
    return '''<header class="open" id="top" data-nav="البداية">
  <svg class="op-line" viewBox="0 0 1000 20" preserveAspectRatio="none" aria-hidden="true"><path d="M0 10 H1000" pathLength="1"/><rect class="op-mass" x="0" y="4" width="1000" height="12"/></svg>
  <p class="op-1">قبل أن يُبنى المشروع… تُبنى الفكرة.</p>
  <h1 class="op-2">الراية</h1>
  <p class="op-3">ستة اتجاهات للهوية. كل اسمٍ فيها مرسوم حرفاً حرفاً.</p>
  <p class="op-sig"><span>هوية بصرية وتصميم</span><b>عَدول</b><i dir="ltr">Adol</i></p>
  <a class="op-cue" href="#board" aria-label="ابدأ العرض"><i></i></a>
</header>'''


def lineup(id_, nav, title, sub, kind="horizontal"):
    cells = "".join(f'<a class="lu-c fx" style="--dl:{i * .05:.2f}s" href="#d{x["n"]}">{use(x["n"], kind, "black", "lu-l", x["name"])}'
                    f'<span><i dir="ltr">{x["n"]}</i>{x["name"]}</span></a>' for i, x in enumerate(D))
    return f'''<section class="lineup sec" id="{id_}" data-nav="{nav}" data-r>
  <div class="sec-h"><h2 class="fx">{title}</h2><p class="sub fx" style="--dl:.06s">{sub}</p></div>
  <div class="lu-g">{cells}</div>
</section>'''


def words():
    cells = "".join(f'<div class="wd fx" style="--dl:{i * .04:.2f}s">{use(x["n"], "word", "black", "wd-l", "الراية")}<span><i dir="ltr">{x["n"]}</i></span></div>' for i, x in enumerate(D))
    return f'''<section class="words sec" id="words" data-nav="الكلمة وحدها" data-r>
  <div class="sec-h"><h2 class="fx">«الراية» وحدها</h2><p class="sub fx" style="--dl:.06s">ستة أقلام على بنية واحدة: ارتفاع الألف واللام واحد، وسن الياء واحد، والفراغ بين الحروف المنفصلة واحد. لا خط جاهز، ولا قصّ.</p></div>
  <div class="wd-g">{cells}</div>
</section>'''


def chapter(x):
    n = x["n"]
    fns = {a: f for a, _, f in M.ALL}
    nms = {a: nm for a, nm, _ in M.ALL}
    apps = "".join(f'<figure class="ca fx" style="--dl:{j * .08:.2f}s">{fns[k](n, uid=f"c{n}{k}", sw=False)}<figcaption>{nms[k]}</figcaption></figure>' for j, k in enumerate(x["apps"]))
    return f'''<section class="chap d{n}" id="d{n}" data-nav="{n} · {x["name"]}">
  <div class="scene" data-scene>
    <div class="pin">
      <div class="sc-h"><span class="sc-n" dir="ltr">{n}<i>/06</i></span><h2>{x["name"]}</h2><em>{x["tag"]}</em></div>
      {scene(n)}
      <p class="sc-story">{x["form"]}</p>
    </div>
  </div>
  <div class="after">
    <div class="proof" data-r>
      <div class="pf pf-w fx">{use(n, "horizontal", "full", "pf-l")}</div>
      <div class="pf pf-b fx" style="--dl:.08s">{use(n, "horizontal", "rev", "pf-l")}</div>
      <div class="pf pf-s fx" style="--dl:.16s">{use(n, "symbol", "black", "pf-i")}<span>النسخة المختصرة المعتمدة</span></div>
    </div>
    <div class="txt" data-r>
      <dl class="st3 fx"><div><dt>من أين بدأت</dt><dd>{x["origin"]}</dd></div><div><dt>ما يقوله الشكل</dt><dd>{x["form"]}</dd></div><div><dt>الصلة بالراية</dt><dd>{x["link"]}</dd></div></dl>
      <div class="sz fx" style="--dl:.1s"><p>بالمقاس الفعلي</p><div class="szs">{"".join(f'<div style="width:{s}px;height:{s}px">{use(n, "symbol", "full")}</div>' for s in (16, 24, 40, 80))}</div><p class="szn">أصغر مقاس اختُبر وبقي واضحاً: <bdi dir="ltr">{x["min_sym"]}px</bdi>.</p></div>
    </div>
    {craft(x)}
    <div class="ch-apps" data-r>{apps}</div>
  </div>
</section>'''


def apps():
    chips = "".join(f'<button type="button" class="chip{" on" if x["n"] == APPS_DEFAULT else ""}" data-k="{x["n"]}" aria-pressed="{"true" if x["n"] == APPS_DEFAULT else "false"}"><i dir="ltr">{x["n"]}</i>{x["name"]}</button>' for x in D)
    figs = ""
    for k, nm, fn in M.ALL:
        if k not in APPS:
            continue
        cls = "w2" if k in ("vest", "insta") else "w1"
        figs += f'<figure class="ap {cls} fx">{fn(APPS_DEFAULT, uid="a" + k)}<figcaption>{nm}</figcaption></figure>'
    return f'''<section class="apps sec" id="apps" data-nav="التطبيقات">
  <div class="sec-h" data-r><h2 class="fx">الشعار في عمل الشركة</h2><p class="sub fx" style="--dl:.06s">اختر اتجاهاً فيتغيّر في كل التطبيقات معاً. الشعار نفسه في كل مكان، والنسخة المختصرة مأخوذة منه.</p></div>
  <div class="switch" role="group" aria-label="اختيار الاتجاه">{chips}</div>
  <div class="ap-g" data-r>{figs}</div>
</section>'''


def recommend():
    cards = "".join(f'<article class="rc fx" style="--dl:{.08 + i * .12:.2f}s"><div class="rc-l">{use(n, "horizontal", "rev", "rl")}</div>'
                    f'<h3><i dir="ltr">{n}</i>{BY[n]["name"]}</h3><p>{why}</p></article>' for i, (n, why) in enumerate(REC))
    return f'''<section class="rec" id="rec" data-nav="التوصية"><div class="rec-in" data-r>
  <h2 class="fx">نرشّح اتجاهين</h2>
  <p class="sub fx" style="--dl:.05s">بحسب الوضوح، والتميّز، والارتباط بالشركة، وسهولة التطبيق، والعمل بالعربي والإنكليزي.</p>
  <div class="rc-g">{cards}</div>
  <p class="rec-n fx" style="--dl:.4s">وإذا كانت الأولوية للطابع المؤسسي الهادئ، فـ«ختم الراية» (06) هو الخيار الأقرب.</p>
</div></section>'''


V3 = [("01", "01-al-uqda", "العقدة"), ("02", "02-line-to-mass", "من الخط إلى الكتلة"), ("03", "03-bearing-void", "الفراغ الحامل"),
      ("04", "04-signature", "التوقيع العربي"), ("05", "05-turning-point", "نقطة التحول"), ("06", "06-seal", "ختم الراية")]


def previous(v1vb, v2vb):
    c3 = "".join(f'<figure><img src="v3/logos/{slug}/svg/alraya-{n}-horizontal-full.svg" alt="{nm}" loading="lazy" decoding="async"><figcaption>{nm}</figcaption></figure>' for n, slug, nm in V3)
    o1 = [("01", "المقياس"), ("02", "السارية"), ("03", "الشدّة"), ("04", "الركيزة"), ("05", "الخاتَم"), ("06", "نقطة الإسناد")]
    c1 = "".join(f'<figure><svg viewBox="{v1vb[n]}" aria-hidden="true"><use href="#O1-{n}" x="{v1vb[n].split()[0]}" y="{v1vb[n].split()[1]}" width="{v1vb[n].split()[2]}" height="{v1vb[n].split()[3]}"/></svg><figcaption>{nm}</figcaption></figure>' for n, nm in o1)
    o2 = [("01", "الشبكة"), ("02", "الختم"), ("03", "الطيّة"), ("04", "الزاوية"), ("05", "التعاشق")]
    c2 = "".join(f'<figure><svg viewBox="{v2vb[n]}" aria-hidden="true" style="{M.SCH["full"]}"><use href="#O2-{n}"/></svg><figcaption>{nm}</figcaption></figure>' for n, nm in o2)
    return f'''<section class="prev sec" id="prev" data-nav="الاستكشافات السابقة" data-r>
  <div class="sec-h"><h2 class="fx h2s">الاستكشافات السابقة</h2><p class="sub fx" style="--dl:.06s">مراحل سابقة من البحث، محفوظة للرجوع. ليست ضمن الخيارات.</p></div>
  <p class="ex-t fx">الجولة الثالثة</p><div class="ex-g fx">{c3}</div>
  <p class="ex-t fx">الجولة الثانية</p><div class="ex-g fx">{c2}</div>
  <p class="ex-t fx">الجولة الأولى</p><div class="ex-g fx">{c1}</div>
  <p class="ex-n fx">العروض الكاملة: <a href="v1/">الأولى</a> · <a href="v2/">الثانية</a> · <a href="v3/">الثالثة</a></p>
</section>'''


def ending():
    return '''<footer class="end" id="end" data-nav="الخاتمة"><div class="end-in" data-r>
  <p class="end-q fx">الشعار الذي سنختاره اليوم،<br>سيوقّع مشاريع الراية لسنوات.</p>
  <p class="end-sig fx" style="--dl:.2s"><span>هوية بصرية وتصميم</span><b>عَدول</b><i dir="ltr">Adol</i></p>
</div></footer>'''


def nav():
    items = [("top", "البداية"), ("board", "الاتجاهات الستة"), ("words", "الكلمة وحدها")] + [(f"d{x['n']}", f"{x['n']} · {x['name']}") for x in D] + \
            [("compare", "المقارنة"), ("apps", "التطبيقات"), ("rec", "التوصية"), ("prev", "الاستكشافات السابقة"), ("end", "الخاتمة")]
    links = "".join(f'<a href="#{i}"><i></i><span>{t}</span></a>' for i, t in items)
    return (f'<nav class="nav" aria-label="أقسام العرض">{links}</nav>'
            f'<div class="mbar"><button type="button" class="mbar-b" aria-expanded="false" aria-controls="mbar-l"><span class="mbar-c">البداية</span><i></i></button>'
            f'<div class="mbar-p"><i></i></div><nav class="mbar-l" id="mbar-l" aria-label="أقسام العرض">{links}</nav></div>')


def build():
    for x in D:
        LK[x["n"]] = I.lockups(x["n"])
    spr = sprite()
    v1s, v1vb, v2g, v2vb = old_assets()
    body = "".join([
        '<div class="prog" aria-hidden="true"><i></i></div>', nav(), "<main>", opening(),
        lineup("board", "الاتجاهات الستة", "الاتجاهات الستة", "بالأسود فقط، وبالحجم البصري نفسه. الشكل قبل القصة."),
        words(), "".join(chapter(x) for x in D),
        lineup("compare", "المقارنة", "المقارنة", "الرموز المختصرة الستة معاً: أسود، والحجم نفسه، والخلفية نفسها.", "symbol"),
        apps(), recommend(), previous(v1vb, v2vb), ending(), "</main>",
    ])
    sprite_svg = ('<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>'
                  + spr + "".join(v1s) + "".join(v2g) + "</defs></svg>")
    css = open(os.path.join(TOOLS, "site3.css"), encoding="utf-8").read() + open(os.path.join(TOOLS, "site4.css"), encoding="utf-8").read()
    js = open(os.path.join(TOOLS, "site3.js"), encoding="utf-8").read()
    visible = re.sub(r"<[^>]+>", " ", body) + "ALRAYA·—–«»،؛؟0123456789px/×±%:.()@°"
    html = ('<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="theme-color" content="#1B2046">'
            '<title>الراية — ستة اتجاهات للهوية</title>'
            '<meta name="description" content="ستة اتجاهات لشعار الراية للمقاولات العامة والاستشارات الهندسية. هوية بصرية وتصميم: عَدول.">'
            f'<style>{font_css(set(visible))}{css}</style></head><body>{sprite_svg}{body}<script>{js}</script></body></html>')
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(html)
    print(f"index.html {len(html) / 1024:.0f} KB")


if __name__ == "__main__":
    build()
