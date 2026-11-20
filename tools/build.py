"""Builds index.html: the ALRAYA logo-directions presentation.

    python3 tools/build.py

Previous version is kept untouched in v1/index.html. The six early
explorations are read from it and shown as thumbnails.
"""
import base64, io, os, re, sys

sys.path.insert(0, os.path.dirname(__file__))
from fontTools import subset
from fontTools.ttLib import TTFont

import marks
from marks import to_origin, size
from geo import path_d
import apps as A

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(os.path.dirname(__file__), "fonts")

# ---------------------------------------------------------------- content
DIRS = [
    dict(n="01", key="grid", name="الشبكة", fn=marks.grid_lockup, ic=marks.grid_icon,
         idea="كلمة «الراية» مبنية على شبكة وحدات متساوية: كل خط بعرض وحدة، وكل فراغ بعرض وحدة، كما يُرسم المخطط على شبكة.",
         rel="الشعار هو الاسم نفسه بالخط الكوفي المربع، ونقاطه الأربع باللون الماروني.",
         min_icon=24, min_lock=36),
    dict(n="02", key="seal", name="الختم", fn=marks.seal_lockup, ic=marks.seal_icon,
         idea="ختم دائري مؤسسي يصلح لاعتماد المخططات والوثائق، ورمزه في الوسط يذكّر بعلامة القطر في المخططات الإنشائية.",
         rel="الرمز يجمع أول حرف في الاسم، الألف، بحلقة آخر حرف، التاء المربوطة؛ والاسم بالعربية أعلى الختم وبالإنكليزية أسفله.",
         min_icon=16, min_lock=48),
    dict(n="03", key="fold", name="الطيّة", fn=marks.fold_lockup, ic=marks.fold_icon,
         idea="شريط واحد ينثني مرة واحدة، فيظهر وجهه بالنيلي وظهره بالماروني، كما تُثنى الصفيحة وقضبان الحديد.",
         rel="الشريط المثني يرسم حرف الراء، والراية نفسها قماش يُطوى ويُنشر.",
         min_icon=24, min_lock=36),
    dict(n="04", key="angle", name="الزاوية", fn=marks.angle_lockup, ic=marks.angle_icon,
         idea="حرف A ساقه اليمنى قائمة، تلتقي بالقاعدة في زاوية قائمة مثل زاوية الرسم الهندسي.",
         rel="الساق القائمة ألف «الراية»، والحرف كله A في «ALRAYA»؛ الاسمان يبدآن بالحرف نفسه.",
         min_icon=16, min_lock=28),
    dict(n="05", key="lock", name="التعاشق", fn=marks.lock_lockup, ic=marks.lock_icon,
         idea="قطعتان متطابقتان تتعاشقان في مربع واحد: المقاولات والاستشارات الهندسية في شركة واحدة.",
         rel="كل قطعة لامٌ كوفية، من «ال» في أول الاسم.",
         min_icon=16, min_lock=28),
]
REC = [
    ("02", "يلبّي الحاجة إلى ختم رسمي على المخططات والوثائق، والاسمان فيه واضحان، ونسخته المختصرة تبقى مقروءة حتى 16px."),
    ("01", "يُقرأ فيه الاسم مباشرة في كل تطبيق، ولأنه مبني من مربعات يُنفَّذ بسهولة بالقص والطلاء والحفر على المعدن."),
]
OLD = [("01", "المقياس"), ("02", "السارية"), ("03", "الشدّة"), ("04", "الركيزة"), ("05", "الخاتَم"), ("06", "نقطة الإسناد")]
APPS_DEFAULT = REC[0][0]


# ---------------------------------------------------------------- geometry -> svg
def layer_paths(layers, cls=False):
    out = []
    for L in layers:
        g, role = L[0], L[1]
        part = L[2] if len(L) > 2 else "mk"
        fill = "var(--p)" if role == "p" else "var(--a)"
        c = f' class="pt {part} r{role}"' if cls else ""
        out.append(f'<path{c} fill="{fill}" d="{path_d(g, 0)}"/>')
    return "".join(out)


GEOM = {}


def geoms():
    for d in DIRS:
        lk = to_origin(d["fn"]())
        ic = to_origin(d["ic"]())
        GEOM[d["n"]] = {"lockup": lk, "icon": ic}


def defs():
    out = []
    for n, kinds in GEOM.items():
        for kind, layers in kinds.items():
            w, h = size(layers)
            out.append(f'<g id="G-{n}-{kind}">{layer_paths(layers)}</g>')
            for al, par in (("c", "xMidYMid"), ("r", "xMaxYMid"), ("l", "xMinYMid")):
                out.append(f'<symbol id="L-{n}-{kind}-{al}" viewBox="0 0 {w:.0f} {h:.0f}" '
                           f'preserveAspectRatio="{par} meet"><use href="#G-{n}-{kind}"/></symbol>')
    return out


def dims():
    return {f"{n}-{k}": [round(size(l)[0]), round(size(l)[1])] for n, ks in GEOM.items() for k, l in ks.items()}


def use_svg(n, kind, scheme="full", cls="", al="c", label=""):
    w, h = size(GEOM[n][kind])
    lab = f' role="img" aria-label="{label}"' if label else ' aria-hidden="true"'
    return (f'<svg class="{cls}" viewBox="0 0 {w:.0f} {h:.0f}"{lab}>'
            f'<use href="#L-{n}-{kind}-{al}" width="{w:.0f}" height="{h:.0f}" style="{A.SCH[scheme]}"/></svg>')


def stage_svg(n):
    layers = GEOM[n]["lockup"]
    w, h = size(layers)
    return (f'<svg class="rv" viewBox="0 0 {w:.0f} {h:.0f}" role="img" aria-label="الشعار {n}" '
            f'style="{A.SCH["full"]}">{layer_paths(layers, cls=True)}</svg>')


def old_symbols():
    s = open(os.path.join(ROOT, "v1", "index.html"), encoding="utf-8").read()
    out = []
    for n, _ in OLD:
        m = re.search(r'<symbol id="M-%s-lockup-full"[^>]*>.*?</symbol>' % n, s, re.S)
        out.append(m.group(0).replace('id="M-', 'id="O-'))
    vbs = {n: re.search(r'<symbol id="M-%s-lockup-full" viewBox="([^"]+)"' % n, s).group(1) for n, _ in OLD}
    return out, vbs


# ---------------------------------------------------------------- page parts
def hero():
    return f'''<header class="hero" id="top" data-nav="البداية" data-r>
  <div class="top fx"><span class="brand">الراية</span><span class="kicker" dir="ltr">ALRAYA · LOGO DIRECTIONS</span></div>
  <div class="hero-b">
    <h1 class="h1 fx" style="--dl:.1s">خمسة اتجاهات<br><span>لشعار الراية</span></h1>
    <p class="lede fx" style="--dl:.3s">الراية للمقاولات العامة والاستشارات الهندسية. خمسة شعارات مختلفة في الشكل والفكرة: تُعرض أولاً معاً بلا شرح، ثم كلٌّ في قسمه مع نسخه واختباراته وتطبيقاته.</p>
  </div>
  <p class="credit fx" style="--dl:.5s"><span>هوية بصرية وتصميم</span> <b>عَدول</b> <span class="lat" dir="ltr">Adol</span></p>
  <a class="cue fx" style="--dl:.7s" href="#compare"><span>المقارنة</span><i></i></a>
</header>'''


def compare():
    cells = "".join(
        f'<a class="cmp-c fx" style="--dl:{i * .06:.2f}s" href="#d{d["n"]}"><span class="cmp-n" dir="ltr">{d["n"]}</span>'
        f'{use_svg(d["n"], "lockup", cls="cmp-l", label="الاتجاه " + d["n"])}</a>' for i, d in enumerate(DIRS))
    icons = "".join(
        f'<div class="cmp-i fx" style="--dl:{.3 + i * .05:.2f}s"><span class="cmp-n" dir="ltr">{d["n"]}</span>'
        f'{use_svg(d["n"], "icon", cls="cmp-ic")}</div>' for i, d in enumerate(DIRS))
    return f'''<section class="sec cmp" id="compare" data-nav="المقارنة" data-r>
  <div class="sec-h"><p class="kicker fx">المقارنة</p><h2 class="fx" style="--dl:.05s">الخيارات الخمسة</h2>
  <p class="sub fx" style="--dl:.1s">بالحجم نفسه، وعلى الخلفية نفسها، ومن دون شرح.</p></div>
  <div class="cmp-g">{cells}</div>
  <h3 class="sub-h fx">النسخ المختصرة</h3>
  <div class="cmp-ig">{icons}</div>
</section>'''


def direction(i, d):
    n = d["n"]
    W, H = size(GEOM[n]["lockup"])
    variants = f'''
    <div class="vr vr-w fx">{use_svg(n, "icon", "full", "vi")}<span class="tc">النسخة المختصرة</span></div>
    <div class="vr vr-i fx" style="--dl:.06s">{use_svg(n, "lockup", "mono", "vl")}<span class="tc">لون واحد</span></div>
    <div class="vr vr-d fx" style="--dl:.12s">{use_svg(n, "lockup", "rev", "vl")}<span class="tc">على خلفية داكنة</span></div>
    <div class="vr vr-b fx" style="--dl:.18s">{use_svg(n, "lockup", "white", "vl")}<span class="tc">أبيض على أسود</span></div>
    <div class="vr vr-w fx" style="--dl:.24s">{use_svg(n, "lockup", "black", "vl")}<span class="tc">أسود على أبيض</span></div>'''
    ih = "".join(f'<div class="sz"><div style="height:{s}px;width:{s}px">{use_svg(n, "icon")}</div><span class="mono" dir="ltr">{s}px</span></div>'
                 for s in (16, 24, 32, 48))
    lh = "".join(f'<div class="sz"><div style="height:{s}px;width:{s * W / H:.0f}px">{use_svg(n, "lockup")}</div><span class="mono" dir="ltr">{s}px</span></div>'
                 for s in (28, 36, 48, 64))
    mini = (f'<figure class="mf fx">{A.helmet_one_svg(n)}<figcaption>خوذة</figcaption></figure>'
            f'<figure class="mf fx" style="--dl:.08s">{A.card_svg(n)}<figcaption>بطاقة العمل</figcaption></figure>'
            f'<figure class="mf fx" style="--dl:.16s">{A.avatar(n, sw=False)}<figcaption>صورة الحساب</figcaption></figure>')
    return f'''<section class="sec dir d{n}" id="d{n}" data-nav="{n} · {d["name"]}">
  <header class="dir-h" data-r>
    <p class="idx fx"><span class="num" dir="ltr">{n}</span><span class="of" dir="ltr">/ 05</span></p>
    <h2 class="fx" style="--dl:.06s">{d["name"]}</h2>
  </header>
  <figure class="stage" data-r title="اضغط لإعادة الحركة">{stage_svg(n)}</figure>
  <dl class="story" data-r>
    <div class="row fx"><dt>الفكرة</dt><dd>{d["idea"]}</dd></div>
    <div class="row fx" style="--dl:.08s"><dt>علاقتها بالراية</dt><dd>{d["rel"]}</dd></div>
  </dl>
  <div class="vars" data-r>{variants}</div>
  <div class="tests" data-r>
    <div class="t-row fx"><p class="t-l">الأيقونة بالمقاس الفعلي</p><div class="szs">{ih}</div></div>
    <div class="t-row fx" style="--dl:.08s"><p class="t-l">الشعار الكامل بالمقاس الفعلي</p><div class="szs">{lh}</div></div>
    <p class="t-note fx" style="--dl:.14s">أصغر مقاس اختُبر على الشاشة وبقي واضحاً: الأيقونة <bdi dir="ltr">{d["min_icon"]}px</bdi>، والشعار الكامل <bdi dir="ltr">{d["min_lock"]}px</bdi> ارتفاعاً. تحت ذلك تُستخدم الأيقونة.</p>
  </div>
  <div class="mini" data-r>{mini}</div>
</section>'''


def chips():
    return "".join(
        f'<button type="button" class="chip{" on" if d["n"] == APPS_DEFAULT else ""}" data-k="{d["n"]}" aria-pressed="{"true" if d["n"] == APPS_DEFAULT else "false"}">'
        f'<span dir="ltr">{d["n"]}</span> {d["name"]}</button>' for d in DIRS)


def apps_section():
    k = APPS_DEFAULT
    groups = [
        ("a-helmet", "خوذة الموقع", "الأيقونة على الخوذة البيضاء بالألوان الكاملة، وعلى النيلية بالأبيض.", [("w12", A.helmets(k))]),
        ("a-vest", "سترة العمل الميداني", "الأيقونة على رقعة صغيرة في الصدر، والشعار الكامل على لوحة في الظهر، وكلاهما بعيد عن الشرائط العاكسة.", [("w12", A.vest(k))]),
        ("a-desk", "دفتر وقلم", "الأيقونة على الغلاف والقلم، والشعار الكامل على ورق الملاحظات.", [("w12", A.desk(k))]),
        ("a-card", "بطاقة العمل والورق الرسمي", "وجه البطاقة للشعار، وظهرها للاسم والتواصل. الحقول فارغة لتُملأ ببيانات حقيقية.", [("w12", A.stationery(k))]),
        ("a-docs", "ملف المخططات", "الشعار على الملف وفي جدول عنوان كل لوحة.", [("w12", A.drawings(k))]),
        ("a-site", "لوحة المشروع وسيارة الشركة", "لوحة تُقرأ من بعيد، وسيارة تحمل الأيقونة على الباب والشعار الكامل على الجانب.", [("w12", A.board(k)), ("w12", A.car(k))]),
        ("a-insta", "قوالب إنستغرام", "ثلاثة قوالب أساسية: منشور نصي، وصورة من الموقع، وإعلان.", [("w4", s) for s in A.insta(k)]),
    ]
    g = ""
    for gid, h, p, figs in groups:
        f = "".join(f'<figure class="ap {c} fx" style="--dl:{j * .08:.2f}s">{s}</figure>' for j, (c, s) in enumerate(figs))
        g += f'<div class="ag" data-r id="{gid}"><div class="ag-h fx"><h3>{h}</h3><p>{p}</p></div><div class="ag-g">{f}</div></div>'
    return f'''<section class="sec apps" id="apps" data-nav="التطبيقات">
  <header class="sec-h" data-r><p class="kicker fx">التطبيقات</p><h2 class="fx" style="--dl:.05s">الشعار في عمل الشركة</h2>
  <p class="sub fx" style="--dl:.1s">الشعار الكامل والأيقونة المعتمدة نفسهما في كل تطبيق. اختر اتجاهاً لترى التطبيقات به.</p></header>
  <div class="switch" role="group" aria-label="اختيار الاتجاه"><span>الاتجاه</span>{chips()}</div>
  {g}
</section>'''


def guide():
    sw = [("نيلي داكن", "#262E5D", "38 46 93", "اللون الأساسي"),
          ("ماروني", "#7D161A", "125 22 26", "لون التمييز"),
          ("عاجي", "#F3F0E9", "243 240 233", "خلفية مساندة"),
          ("أبيض", "#FFFFFF", "255 255 255", "خلفية مساندة")]
    swatches = "".join(
        f'<div class="sw-c fx" style="--dl:{i * .05:.2f}s"><i style="background:{hx}"></i><b>{nm}</b>'
        f'<span class="mono" dir="ltr">{hx}</span><span class="mono" dir="ltr">RGB {rgb}</span><em>{use}</em></div>'
        for i, (nm, hx, rgb, use) in enumerate(sw))
    k = REC[0][0]
    bgs = (f'<div class="bg-c ok fx" style="background:#F3F0E9">{use_svg(k, "lockup", "full", "bl", label="")}<span>عاجي</span></div>'
           f'<div class="bg-c ok fx" style="background:#fff;--dl:.05s">{use_svg(k, "lockup", "full", "bl")}<span>أبيض</span></div>'
           f'<div class="bg-c ok dk fx" style="background:#262E5D;--dl:.1s">{use_svg(k, "lockup", "rev", "bl")}<span>نيلي: النسخة البيضاء</span></div>'
           f'<div class="bg-c no dk fx" style="background:#262E5D;--dl:.15s">{use_svg(k, "lockup", "full", "bl")}<span>لا: الألوان الكاملة على النيلي</span></div>'
           f'<div class="bg-c no dk fx" style="background:#7D161A;--dl:.2s">{use_svg(k, "lockup", "full", "bl")}<span>لا: على الماروني</span></div>'
           f'<div class="bg-c no fx" style="background:#fff;--dl:.25s"><div class="squash">{use_svg(k, "lockup", "full", "bl")}</div><span>لا: تغيير النسب</span></div>')
    W, H = size(GEOM[k]["lockup"])
    p = H * 0.25
    cs = (f'<svg class="cs" viewBox="{-p * 1.6:.0f} {-p * 1.6:.0f} {W + p * 3.2:.0f} {H + p * 3.2:.0f}" aria-label="المساحة الآمنة">'
          f'<rect x="{-p:.0f}" y="{-p:.0f}" width="{W + 2 * p:.0f}" height="{H + 2 * p:.0f}" fill="#EDEAE2"/>'
          f'<rect x="0" y="0" width="{W:.0f}" height="{H:.0f}" fill="#fff"/>'
          f'<use href="#L-{k}-lockup-c" width="{W:.0f}" height="{H:.0f}" style="{A.SCH["full"]}"/>'
          f'<rect x="{-p:.0f}" y="{-p:.0f}" width="{W + 2 * p:.0f}" height="{H + 2 * p:.0f}" fill="none" stroke="#7D161A" stroke-width="{H * .008:.1f}" stroke-dasharray="{H * .03:.0f} {H * .02:.0f}"/>'
          f'<rect x="{W:.0f}" y="{H / 2 - p / 2:.0f}" width="{p:.0f}" height="{p:.0f}" fill="#7D161A" opacity=".25"/>'
          f'<text x="{W + p / 2:.0f}" y="{H / 2 + p * 1.1:.0f}" font-size="{p * .32:.0f}" text-anchor="middle" fill="#7D161A" font-family="PlexMono" direction="ltr">x</text></svg>')
    rows = "".join(f'<tr><td><span class="mono" dir="ltr">{d["n"]}</span> {d["name"]}</td><td dir="ltr">{d["min_lock"]}px</td><td dir="ltr">{d["min_icon"]}px</td></tr>' for d in DIRS)
    return f'''<section class="sec guide" id="guide" data-nav="الدليل">
  <header class="sec-h" data-r><p class="kicker fx">الدليل</p><h2 class="fx" style="--dl:.05s">قواعد الاستخدام</h2>
  <p class="sub fx" style="--dl:.1s">القواعد الأساسية فقط. تُستكمل بعد اختيار الاتجاه.</p></header>
  <div class="gb" data-r><h3 class="sub-h fx">الألوان</h3><div class="sw-g">{swatches}</div>
  <p class="g-note fx">على الخلفيات الداكنة يتحوّل الماروني في الشعار إلى ماروني فاتح <bdi class="mono" dir="ltr">#D7A3A5</bdi> حتى يبقى ظاهراً.</p></div>
  <div class="gb" data-r><h3 class="sub-h fx">الخطوط</h3>
    <div class="ft fx"><p class="ft-s">الراية للمقاولات العامة والاستشارات الهندسية</p><p class="ft-n" dir="ltr">IBM Plex Sans Arabic <span>· Regular · Medium · SemiBold · Bold</span></p><p class="ft-u">خط النصوص بالعربية والإنكليزية في المطبوعات والموقع.</p></div>
    <p class="g-note fx">حروف الشعار مرسومة ومحوّلة إلى أشكال، ولا تُكتب بلوحة المفاتيح. يُستخدم ملف الشعار المعتمد دائماً.</p></div>
  <div class="gb" data-r><h3 class="sub-h fx">الشعار على الخلفيات</h3><div class="bg-g">{bgs}</div>
  <p class="g-note fx">الأمثلة بالاتجاه {k}، والقاعدة نفسها لكل الاتجاهات.</p></div>
  <div class="gb gb2" data-r>
    <div><h3 class="sub-h fx">المساحة الآمنة</h3><div class="cs-w fx">{cs}</div>
    <p class="g-note fx">يُترك حول الشعار فراغ لا يقل عن ربع ارتفاعه <bdi dir="ltr">(x)</bdi> من كل جهة.</p></div>
    <div><h3 class="sub-h fx">أصغر مقاس</h3>
    <table class="mt fx"><thead><tr><th>الاتجاه</th><th>الشعار الكامل (ارتفاع)</th><th>الأيقونة</th></tr></thead><tbody>{rows}</tbody></table>
    <p class="g-note fx">قيست على شاشة عادية بكثافة بكسل واحدة. في الطباعة يُعتمد ما يعادلها بعد تجربة مطبوعة.</p></div>
  </div>
</section>'''


def recommend():
    by = {d["n"]: d for d in DIRS}
    cards = "".join(
        f'<article class="rc fx" style="--dl:{.1 + i * .12:.2f}s"><div class="rc-logo">{use_svg(n, "lockup", "rev", "rl")}</div>'
        f'<h3><span class="num" dir="ltr">{n}</span>{by[n]["name"]}</h3><p>{why}</p></article>' for i, (n, why) in enumerate(REC))
    return f'''<section class="rec-s" id="rec" data-nav="التوصية"><div class="rec" data-r>
  <p class="kicker fx">التوصية</p><h2 class="fx" style="--dl:.05s">نرشّح اتجاهين</h2>
  <div class="rec-g">{cards}</div>
  <p class="next fx" style="--dl:.4s">الخطوة التالية: اختيار اتجاه واحد، ثم تجهيز ملفات الشعار النهائية ودليل الاستخدام الكامل.</p>
</div></section>'''


def old_use(n, vb):
    x, y, w, h = vb.split()
    return f'<use href="#O-{n}-lockup-full" x="{x}" y="{y}" width="{w}" height="{h}"/>'


def early(vbs):
    cells = "".join(
        f'<figure class="ex fx" style="--dl:{i * .05:.2f}s"><svg viewBox="{vbs[n]}" aria-hidden="true">{old_use(n, vbs[n])}</svg>'
        f'<figcaption><span class="mono" dir="ltr">{n}</span> {nm}</figcaption></figure>' for i, (n, nm) in enumerate(OLD))
    return f'''<section class="sec early" id="early" data-nav="استكشافات أولية" data-r>
  <div class="sec-h"><p class="kicker fx">أرشيف</p><h2 class="fx h2s" style="--dl:.05s">استكشافات أولية</h2>
  <p class="sub fx" style="--dl:.1s">المرحلة الأولى من العمل. ليست ضمن الخيارات الخمسة، وتبقى مرجعاً.</p></div>
  <div class="ex-g">{cells}</div>
</section>'''


def footer():
    return '''<footer class="sign" data-r><div class="sign-i fx">
  <span class="sign-l">هوية بصرية وتصميم</span><span class="sign-n">عَدول</span><span class="sign-e" dir="ltr">Adol</span>
</div></footer>'''


# ---------------------------------------------------------------- fonts
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
RANGES = {"ar": "U+0600-06FF,U+200C-200F,U+FB50-FDFF,U+FE70-FEFC",
          "la": "U+0000-00FF,U+2010-2027,U+2030-206F,U+2212"}


def font_css(chars):
    css = []
    for fam, wt, fn, rg in FACES:
        f = TTFont(os.path.join(FONTS, fn))
        cmap = f.getBestCmap()
        want = [ord(c) for c in chars if ord(c) in cmap]
        opts = subset.Options()
        opts.layout_features = ["*"]
        opts.flavor = "woff2"
        opts.name_IDs = []
        opts.notdef_outline = True
        sub = subset.Subsetter(opts)
        sub.populate(unicodes=want)
        sub.subset(f)
        buf = io.BytesIO()
        f.flavor = "woff2"
        f.save(buf)
        b64 = base64.b64encode(buf.getvalue()).decode()
        css.append(f'@font-face{{font-family:"{fam}";src:url(data:font/woff2;base64,{b64}) format("woff2");'
                   f'font-weight:{wt};font-style:normal;font-display:block;unicode-range:{RANGES[rg]}}}')
    return "".join(css)


# ---------------------------------------------------------------- assemble
def build():
    geoms()
    olds, vbs = old_symbols()
    body = "".join([
        '<div class="prog" aria-hidden="true"><i></i></div>',
        nav(),
        "<main>", hero(), compare(),
        "".join(direction(i, d) for i, d in enumerate(DIRS)),
        apps_section(), guide(), recommend(), early(vbs), footer(), "</main>",
    ])
    sprite = ('<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>'
              + "".join(defs()) + "".join(olds) + "</defs></svg>")
    css = open(os.path.join(os.path.dirname(__file__), "site.css"), encoding="utf-8").read()
    js = open(os.path.join(os.path.dirname(__file__), "site.js"), encoding="utf-8").read()
    js = js.replace("__DIMS__", repr(dims()).replace("'", '"'))
    visible = re.sub(r"<[^>]+>", " ", body) + css + "ALRAYA·—–«»،؛؟0123456789px/×±%:.()"
    fonts = font_css(set(visible))
    html = ('<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
            '<title>الراية — خمسة اتجاهات للشعار</title>'
            '<meta name="description" content="خمسة اتجاهات لشعار الراية للمقاولات العامة والاستشارات الهندسية.">'
            f'<style>{fonts}{css}</style></head><body>{sprite}{body}<script>{js}</script></body></html>')
    out = os.path.join(ROOT, "index.html")
    open(out, "w", encoding="utf-8").write(html)
    print("wrote", out, f"{len(html) / 1024:.0f} KB")


def nav():
    items = [("top", "البداية"), ("compare", "المقارنة")] + [(f"d{d['n']}", f"{d['n']} · {d['name']}") for d in DIRS] + \
            [("apps", "التطبيقات"), ("guide", "الدليل"), ("rec", "التوصية"), ("early", "استكشافات أولية")]
    links = "".join(f'<a href="#{i}"><i></i><span>{t}</span></a>' for i, t in items)
    return (f'<nav class="nav" aria-label="أقسام العرض">{links}</nav>'
            f'<div class="mnav"><button type="button" class="mnav-b" aria-expanded="false" aria-controls="mnav-l">'
            f'<span class="mnav-c">البداية</span><i></i></button><div class="mnav-l" id="mnav-l">{links}</div></div>')


if __name__ == "__main__":
    build()
