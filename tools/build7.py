"""Builds index.html — ALRAYA identity presentation (v7).

    python3 tools/build7.py

One long scroll: opening → (current logo, why, transition: only with a real
file) → the five directions → comparison and choice → closing → earlier
options for review → signature.

The current-logo sections appear only when a real file of the company's
current logo exists as assets/current-logo.svg / .png / .jpg / .webp.
Observations are read from assets/current-logo-notes.txt (one per line) and
are never generated here.

Application images are photographs (assets/photos, see CREDITS.md). The logo
is placed on each photo as the same vector symbol used everywhere else.
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
import identity6 as I
import mock3 as M
from vec import d as pd, bounds
from identity import lorigin, lsize
from build3 import font_css

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.dirname(__file__)

D = [
    dict(n="01", slug="01-steel-joint", name=I.NAMES["01"], min=24,
         say="عمود فولاذي وكمرتان تلتقيان عند صفيحة واحدة مثبّتة بالبراغي. نقطة الاتصال هي ما يمسك الهيكل كله، ولهذا هي الجزء الماروني في العلامة.",
         mean="الاتصال الذي يحمل الهيكل", use="الموقع والمعدات والخوذ", apps=("helmet", "board")),
    dict(n="02", slug="02-frame", name=I.NAMES["02"], min=32,
         say="على اليسار شبكة التخطيط، وعلى اليمين مبنى من ثلاثة طوابق يقوم عليها. العلامة تجمع عملَي الشركة: الاستشارة التي ترسم، والمقاولة التي تبني.",
         mean="من المخطط إلى المبنى", use="المخططات والتقارير", apps=("letter", "notebook", "car")),
    dict(n="03", slug="03-upright", name=I.NAMES["03"], min=16,
         say="حرف A مبني كمنشأ: دعامة مائلة وعمودان وكمرة تربطها على أساس واحد. يُقرأ حرفاً من ALRAYA، ويُرى هيكلاً قائماً.",
         mean="الحرف الأول هيكلاً قائماً", use="الملابس والسيارات والأحجام الصغيرة", apps=("vest", "helmet", "car")),
    dict(n="04", slug="04-portal", name=I.NAMES["04"], min=16,
         say="عمودان وجسر علوي يقفله حجر مفتاح في الوسط. حجر المفتاح يمسك نصفَي الجسر معاً، والبوابة أول ما يراه الداخل إلى المشروع.",
         mean="المدخل الثابت", use="المكتب والمراسلات الرسمية", apps=("board", "letter")),
    dict(n="05", slug="05-survey-point", name=I.NAMES["05"], min=24,
         say="قبل أن يُبنى شيء يُحدَّد موقعه: علامات المساحة على الدائرة، ومستطيل التوقيع بزواياه ونقطة مركزه، ثم البوابة على قاعدتها. العلامة عن الدقة التي تسبق التنفيذ.",
         mean="الدقة قبل التنفيذ", use="الاستشارات والمخططات والوثائق", apps=("notebook", "vest")),
]
LK, DIMS = {}, {}
FILL = {"p": "var(--p)", "a": "var(--a)"}

# photographs: size of the file, label, and where the logo sits (photo pixels)
#   kind, centre x, centre y, width, rotate°, skewY°, colour scheme, blend, opacity
PHOTOS = {
    "helmet": dict(size=(1400, 1050), label="خوذة الموقع", logo=("symbol", 668, 540, 236, -5, 0, "full", "multiply", .88)),
    "vest": dict(size=(1600, 1200), label="سترة السلامة", logo=("horizontal", 236, 846, 340, 8, 0, "full", "normal", .9)),
    "letter": dict(size=(1400, 1050), label="الورق الرسمي", logo=("horizontal", 905, 205, 230, 0, 0, "full", "multiply", .94),
                   extra='<rect x="400" y="282" width="605" height="2.2" fill="#7D161A" opacity=".8"/>'),
    "notebook": dict(size=(1420, 1065), label="دفتر وقلم", logo=("stacked", 820, 500, 250, -.6, 0, "full", "multiply", .92)),
    "board": dict(size=(1400, 1050), label="لوحة المشروع", matrix="matrix(.508 -.19 0 .55 370 320)", logo=("descriptor", 500, 470, 760, 0, 0, "full", "multiply", .93)),
    "car": dict(size=(1200, 510), view=(0, 0, 1132, 510), label="سيارة الشركة", wide=True, logo=("horizontal", 676, 224, 150, 0, -3.8, "full", "multiply", .9)),
}

PREV = [("01", "01-ta-ring", "حلقة التاء", "horizontal"), ("02", "02-nameplate", "اللوحة", "horizontal"), ("03", "03-ra", "را", "horizontal"),
        ("04", "04-six-by-six", "ستة بستة", "horizontal"), ("05", "05-assembled-ra", "التركيب", "horizontal"),
        ("06", "06-seal", "ختم الراية", "circular"), ("07", "07-ascent", "الصعود", "horizontal")]
OLDER = [("v3-03", "الفراغ الحامل"), ("v3-05", "نقطة التحول"), ("v3-01", "العقدة"), ("v3-06", "ختم الألف والتاء"),
         ("v2-01", "الشبكة الكوفية"), ("v2-03", "الطيّة"), ("v2-04", "الزاوية"), ("v2-05", "التعاشق"), ("v1-06", "نقطة الإسناد")]


def paths(layers, nd=0):
    return "".join(f'<path fill="{FILL[r]}" d="{pd(p, nd)}"/>' for p, r in layers)


def sprite():
    out = []
    for x in D:
        n = x["n"]
        for kind in ("symbol", "horizontal", "stacked", "descriptor"):
            layers = lorigin(LK[n][kind])
            w, h = lsize(layers)
            out.append(f'<g id="G-{n}-{kind}">{paths(layers)}</g>')
            out.append(f'<symbol id="L-{n}-{kind}-c" viewBox="0 0 {w:.0f} {h:.0f}"><use href="#G-{n}-{kind}"/></symbol>')
            DIMS[f"{n}-{kind}"] = (w, h)
    return "".join(out)


def use(n, kind, sch="full", cls="", label=""):
    w, h = DIMS[f"{n}-{kind}"]
    lab = f' role="img" aria-label="{label}"' if label else ' aria-hidden="true"'
    return f'<svg class="{cls}" viewBox="0 0 {w:.0f} {h:.0f}"{lab}><use href="#L-{n}-{kind}-c" width="{w:.0f}" height="{h:.0f}" style="{M.SCH[sch]}"/></svg>'


# ------------------------------------------------------------------ the reveal
def reveal(n, uid, sch="full", label=""):
    """The mark in the order it is built. The markup rests in its final
    state; site7.js plays the build once when the mark comes into view.
      frame  — the outline is drawn
      plan   — setting-out / grid lines are drawn across
      build  — the structure rises from its base
      beam   — the two sides of the beam close toward the middle
      point  — the survey point settles
      accent — the maroon part is set last
    """
    ps, guide = I.parts(n)
    x0, y0, x1, y1 = bounds(*[p for p, _, _ in ps])
    pad = 24
    bx, by, bw, bh = x0 - pad, y0 - pad, x1 - x0 + 2 * pad, y1 - y0 + 2 * pad
    box = f"{bx:.0f} {by:.0f} {bw:.0f} {bh:.0f}"
    full = f'x="{bx:.0f}" y="{by:.0f}" width="{bw:.0f}" height="{bh:.0f}"'
    defs, body = "", ""
    for i, (p, role, st) in enumerate(ps):
        g = f'<path fill="{FILL[role]}" d="{pd(p, 0)}"/>'
        if st == "frame" and guide:
            if guide[0] == "circle":
                _, cx, cy, r, w = guide
                gd = f"M{cx},{cy - r} A{r},{r} 0 1 0 {cx},{cy + r} A{r},{r} 0 1 0 {cx},{cy - r}"
            else:
                w = guide[2]
                gd = "M" + " L".join(f"{a:.1f},{b:.1f}" for a, b in guide[1]) + " Z"
            defs += (f'<mask id="m{uid}{i}" maskUnits="userSpaceOnUse" {full}>'
                     f'<path data-st="frame" d="{gd}" fill="none" stroke="#fff" stroke-width="{w}" pathLength="1" stroke-dasharray="1.02 1.02" stroke-dashoffset="0"/></mask>')
            body += f'<g mask="url(#m{uid}{i})">{g}</g>'
        elif st in ("build", "plan"):
            mode = "up" if st == "build" else "ltr"
            defs += f'<clipPath id="c{uid}{i}"><rect data-st="{st}" data-m="{mode}" data-box="{box}" {full}/></clipPath>'
            body += f'<g clip-path="url(#c{uid}{i})">{g}</g>'
        elif st == "beam":
            # the two sides close toward the middle of the beam
            px0, _, px1, _ = bounds(p)
            mid = (px0 + px1) / 2
            defs += (f'<clipPath id="c{uid}{i}"><rect data-st="beam" data-m="ltr" data-box="{bx:.0f} {by:.0f} {mid - bx:.0f} {bh:.0f}" x="{bx:.0f}" y="{by:.0f}" width="{mid - bx:.0f}" height="{bh:.0f}"/>'
                     f'<rect data-st="beam" data-m="rtl" data-box="{mid:.0f} {by:.0f} {bx + bw - mid:.0f} {bh:.0f}" x="{mid:.0f}" y="{by:.0f}" width="{bx + bw - mid:.0f}" height="{bh:.0f}"/></clipPath>')
            body += f'<g clip-path="url(#c{uid}{i})">{g}</g>'
        else:
            cx0, cy0, cx1, cy1 = bounds(p)
            body += f'<g data-st="{st}" data-c="{(cx0 + cx1) / 2:.0f} {(cy0 + cy1) / 2:.0f}">{g}</g>'
    lab = f' role="img" aria-label="{label}"' if label else ' aria-hidden="true"'
    return f'<svg class="rv" data-rv viewBox="{box}"{lab} style="{M.SCH[sch]}"><defs>{defs}</defs>{body}</svg>'


# ------------------------------------------------------------------ photographs
def photo(n, key, uid):
    """A photograph with the direction's vector logo placed on it."""
    ph = PHOTOS[key]
    W, H = ph["size"]
    kind, cx, cy, w, rot, skew, sch, blend, op = ph["logo"]
    lw, lh = DIMS[f"{n}-{kind}"]
    h = w * lh / lw
    if kind == "symbol" and lw < lh * .9:      # tall mark: fit by height
        h = w; w = h * lw / lh
    tf = ph.get("matrix", "") + f" translate({cx} {cy})" + (f" rotate({rot})" if rot else "") + (f" skewY({skew})" if skew else "")
    logo = (f'<g transform="{tf.strip()}" style="mix-blend-mode:{blend};{M.SCH[sch]}" opacity="{op}">'
            f'<use href="#L-{n}-{kind}-c" x="{-w / 2:.1f}" y="{-h / 2:.1f}" width="{w:.1f}" height="{h:.1f}"/></g>')
    extra = f'<g style="mix-blend-mode:multiply">{ph["extra"]}</g>' if ph.get("extra") else ""
    cls = "shot wide" if ph.get("wide") else "shot"
    vx, vy, vw, vh = ph.get("view", (0, 0, W, H))
    return (f'<figure class="{cls} fx"><svg viewBox="{vx} {vy} {vw} {vh}" role="img" aria-label="تصور تطبيقي: {ph["label"]}" style="isolation:isolate">'
            f'<image href="assets/photos/{key}.jpg" width="{W}" height="{H}" preserveAspectRatio="xMidYMid slice"/>{extra}{logo}</svg>'
            f'<figcaption><b>تصور تطبيقي</b> · {ph["label"]}</figcaption></figure>')


# ------------------------------------------------------------------ sections
def opening():
    return '''<header class="op" id="top" data-nav="البداية">
  <svg class="op-lines" viewBox="0 0 1600 900" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
    <path class="ln l1" pathLength="1" d="M0 640 H1600"/><path class="ln l2" pathLength="1" d="M420 900 V0"/>
    <path class="ln l3" pathLength="1" d="M1180 900 V0"/><path class="ln l4" pathLength="1" d="M0 260 H1600"/>
    <rect class="pt p1" x="412" y="632" width="16" height="16"/><rect class="pt p2" x="1172" y="632" width="16" height="16"/>
    <rect class="pt p3" x="412" y="252" width="16" height="16"/><rect class="pt p4" x="1172" y="252" width="16" height="16"/>
  </svg>
  <div class="op-in">
    <p class="op-k">الراية · مقاولات عامة واستشارات هندسية</p>
    <h1>تطوير هوية الراية</h1>
    <p class="op-s">خمسة اتجاهات مقترحة للشعار، للمراجعة والاختيار.</p>
  </div>
  <a class="op-cue" href="#intro" aria-label="ابدأ العرض"><i></i></a>
</header>'''


def current_logo():
    """The company's current logo, the reasons for development, and the
    transition — only with a real file. Returns (html, src)."""
    src = None
    for ext in ("svg", "png", "jpg", "jpeg", "webp"):
        if os.path.exists(os.path.join(ROOT, "assets", f"current-logo.{ext}")):
            src = f"assets/current-logo.{ext}"
            break
    if not src:
        return "", None
    notes_f = os.path.join(ROOT, "assets", "current-logo-notes.txt")
    notes = [l.strip() for l in open(notes_f, encoding="utf-8") if l.strip()] if os.path.exists(notes_f) else []
    sf = os.path.join(ROOT, "assets", "current-logo-source.txt")
    cap = f'<figcaption>{open(sf, encoding="utf-8").read().strip()}</figcaption>' if os.path.exists(sf) else ""
    out = f'''<section class="sec cur" id="current" data-nav="الشعار الحالي"><div class="wrap" data-r>
  <p class="eyebrow fx">نقطة البداية</p><h2 class="fx">الشعار الحالي</h2>
  <figure class="cur-f fx"><img src="{src}" alt="الشعار الحالي لشركة الراية" decoding="async">{cap}</figure>
</div></section>'''
    if notes:
        li = "".join(f'<li class="fx" style="--dl:{i * .06:.2f}s">{t}</li>' for i, t in enumerate(notes))
        out += f'''<section class="sec why" id="why" data-nav="سبب التطوير"><div class="wrap" data-r>
  <p class="eyebrow fx">سبب التطوير</p><h2 class="fx">ما الذي يحتاجه الشعار ليصير أوضح</h2><ul class="notes">{li}</ul>
</div></section>'''
    return out, src


def intro(src):
    """The turn toward the new directions. With the current logo it steps
    back while the five marks arrive; without it, the five marks arrive."""
    marks = "".join(f'<a href="#d{x["n"]}" style="--i:{i}" aria-label="{x["name"]}">{use(x["n"], "symbol", "rev")}<span>{x["name"]}</span></a>' for i, x in enumerate(D))
    old = f'<img class="in-old" src="{src}" alt="" aria-hidden="true">' if src else ""
    head = "من الشعار الحالي إلى خمسة اتجاهات" if src else "خمسة اتجاهات، كل واحد من فكرة هندسية واحدة"
    return f'''<section class="intro" id="intro" data-nav="الاتجاهات"><div class="wrap" data-r>
  {old}
  <h2 class="fx">{head}</h2>
  <p class="in-s fx" style="--dl:.08s">كل اتجاه معروض وحده: العلامة، ثم قصتها، ثم شكلها مع الاسم وعلى تطبيقات واقعية.</p>
  <div class="in-g">{marks}</div>
</div></section>'''


def direction(i, x):
    n = x["n"]
    shots = "".join(photo(n, k, f"{n}{k}") for k in x["apps"])
    base = f"logos/{x['slug']}/svg/alraya-{n}"
    return f'''<section class="dir" id="d{n}" data-nav="{n} · {x["name"]}">
  <div class="stage" data-r>
    <p class="st-n fx" dir="ltr">{n}<i> / 05</i></p>
    <div class="st-art">{reveal(n, "d" + n, "full", x["name"])}</div>
    <h2 class="fx">{x["name"]}</h2>
    <p class="st-m fx" style="--dl:.06s">{x["mean"]}</p>
  </div>
  <div class="wrap">
    <p class="story fx" data-r>{x["say"]}</p>
    <div class="lk" data-r>
      <figure class="lk-a fx"><div class="pn">{use(n, "horizontal", "full", "", "الراية — " + x["name"])}</div><figcaption>الاسم مع العلامة</figcaption></figure>
      <figure class="fx" style="--dl:.06s"><div class="pn">{use(n, "horizontal", "black")}</div><figcaption>لون واحد</figcaption></figure>
      <figure class="fx" style="--dl:.12s"><div class="pn pn-i">{use(n, "horizontal", "white")}</div><figcaption>على النيلي</figcaption></figure>
    </div>
    <div class="shots" data-r>{shots}</div>
    <p class="dl fx" data-r>ملفات SVG: <a href="{base}-symbol-full.svg" download>العلامة</a> · <a href="{base}-horizontal-full.svg" download>الاسم مع العلامة</a> · <a href="{base}-horizontal-black.svg" download>لون واحد</a>
      <span>أصغر مقاس واضح في الاختبار: <bdi dir="ltr">{x["min"]}px</bdi></span></p>
  </div>
</section>'''


def compare():
    cards = ""
    for i, x in enumerate(D):
        n = x["n"]
        cards += f'''<article class="cc fx" style="--dl:{i * .05:.2f}s" data-pick="{n}" data-name="{x["name"]}">
      <a class="cc-a" href="#d{n}" aria-label="عرض {x["name"]}"><span class="cc-n" dir="ltr">{n}</span>{use(n, "symbol", "full", "cc-s")}</a>
      <h3>{x["name"]}</h3>
      <p>{x["mean"]}</p>
      <p class="cc-u">الأنسب: {x["use"]}</p>
      <button type="button" class="cc-b" aria-pressed="false">أفضّل هذا الاتجاه</button>
    </article>'''
    return f'''<section class="sec cmp" id="compare" data-nav="المقارنة والاختيار"><div class="wrap" data-r>
  <p class="eyebrow fx">المقارنة والاختيار</p>
  <h2 class="fx">الاتجاهات الخمسة جنباً إلى جنب</h2>
  <p class="sub fx" style="--dl:.05s">بالحجم نفسه والترتيب نفسه. اختر الاتجاه الأقرب لك.</p>
  <div class="cc-g">{cards}</div>
  <div class="pick" aria-live="polite" hidden><p>اختيارك: <b class="pick-n"></b></p>
    <button type="button" class="pick-c">نسخ الاختيار</button><button type="button" class="pick-x">إلغاء</button></div>
</div></section>'''


def closing():
    return '''<section class="close" id="close" data-nav="الخاتمة"><div class="wrap" data-r>
  <p class="fx">هذه اتجاهات مقترحة للنقاش والاختيار، وليست هوية معتمدة.</p>
  <p class="fx" style="--dl:.1s">بعد اختيار اتجاه واحد تُستكمل نسخه وألوانه وتطبيقاته.</p>
</div></section>'''


def previous():
    def cell(src, name, i):
        return (f'<figure class="pv fx" style="--dl:{(i % 4) * .04:.2f}s"><div class="pv-w"><img src="{src}" alt="{name}" loading="lazy" decoding="async"></div>'
                f'<figcaption><b>{name}</b><a href="{src}" download>SVG</a></figcaption></figure>')
    a = "".join(cell(f"v5/logos/{slug}/svg/alraya-{n}-{kind}-full.svg", name, i) for i, (n, slug, name, kind) in enumerate(PREV))
    b = "".join(cell(f"extras/alraya-option-{eid}.svg", name, i) for i, (eid, name) in enumerate(OLDER))
    arch = " · ".join(f'<a href="v{k}/">العرض {lab}</a>' for k, lab in ((6, "السادس"), (5, "الخامس"), (4, "الرابع"), (3, "الثالث"), (2, "الثاني"), (1, "الأول")))
    return f'''<section class="sec prev" id="previous" data-nav="نسخ سابقة"><div class="wrap">
  <div data-r><p class="eyebrow fx">للمراجعة فقط</p>
  <h2 class="fx">نسخ سابقة للمراجعة</h2>
  <p class="sub fx" style="--dl:.05s">خيارات عُرضت في الجولات السابقة من هذا العمل، كما كانت. ليست الشعار الحالي للشركة، وليست ضمن الاتجاهات الخمسة.</p></div>
  <h3 class="pv-h">الجولة السابقة</h3>
  <div class="pv-g" data-r>{a}</div>
  <h3 class="pv-h">من جولات أقدم</h3>
  <div class="pv-g" data-r>{b}</div>
  <p class="pv-arch">العروض السابقة كاملة: {arch}</p>
</div></section>'''


def footer():
    return '''<footer class="end" id="end"><div class="wrap">
  <p class="sig">تطوير الهوية البصرية — <b>عَدول</b> <span aria-hidden="true">|</span> <bdi dir="ltr">Adol</bdi></p>
  <p class="cred">صور التطبيقات فوتوغرافية من Unsplash، والشعار مركّب عليها للتوضيح. ليست صوراً لمشاريع الشركة.</p>
</div></footer>'''


def nav(has_current):
    items = [("top", "البداية")]
    if has_current:
        items += [("current", "الشعار الحالي")]
    items += [("intro", "الاتجاهات")] + [(f"d{x['n']}", f"{x['n']} · {x['name']}") for x in D] + \
             [("compare", "المقارنة والاختيار"), ("previous", "نسخ سابقة")]
    dots = "".join(f'<a href="#{i}"><i></i><span>{t}</span></a>' for i, t in items)
    links = "".join(f'<a href="#{i}">{t}</a>' for i, t in items)
    return (f'<nav class="dots" aria-label="أقسام العرض">{dots}</nav>'
            f'<div class="tb"><a class="tb-b" href="#top">الراية</a><span class="tb-c">البداية</span>'
            f'<button type="button" class="tb-m" aria-expanded="false" aria-controls="tb-l">الأقسام</button>'
            f'<nav class="tb-l" id="tb-l" aria-label="أقسام العرض">{links}</nav></div>')


def build():
    for x in D:
        LK[x["n"]] = I.lockups(x["n"])
    spr = sprite()
    cur, src = current_logo()
    body = "".join([nav(bool(cur)), "<main>", opening(), cur, intro(src),
                    "".join(direction(i, x) for i, x in enumerate(D)), compare(), closing(), previous(), "</main>", footer()])
    sprite_svg = f'<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>{spr}</defs></svg>'
    css = open(os.path.join(TOOLS, "site7.css"), encoding="utf-8").read()
    js = open(os.path.join(TOOLS, "site7.js"), encoding="utf-8").read()
    visible = re.sub(r"<[^>]+>", " ", body) + "ALRAYA·—–«»،؛؟0123456789px/×±%:.()@°SVG|✓تم النسخ"
    html = ('<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="theme-color" content="#1B2046">'
            '<title>تطوير هوية الراية — خمسة اتجاهات مقترحة</title>'
            '<meta name="description" content="خمسة اتجاهات مقترحة لشعار الراية للمقاولات العامة والاستشارات الهندسية. تطوير الهوية البصرية: عَدول.">'
            f'<style>{font_css(set(visible))}{css}</style></head><body>{sprite_svg}{body}<script>{js}</script></body></html>')
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(html)
    print(f"index.html {len(html) / 1024:.0f} KB")


if __name__ == "__main__":
    build()
