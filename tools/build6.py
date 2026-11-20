"""Builds index.html — ALRAYA identity development (v6).

    python3 tools/build6.py

The five directions come from the approved reference board
(design-process/v6/approved-reference-board.png), redrawn in identity6.py.

The current-logo sections appear only when a real file of the company's
current logo is placed in assets/ as current-logo.svg / .png / .jpg / .webp.
Observations about it are read from assets/current-logo-notes.txt (one per
line) and are never generated. Without the file these sections are omitted.
"""
import os, re, sys, base64
sys.path.insert(0, os.path.dirname(__file__))
import identity6 as I
import mock3 as M
from vec import d as pd, bounds, union
from identity import lorigin, lsize
from build3 import font_css

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.dirname(__file__)

D = [
    dict(n="01", slug="01-steel-joint", name=I.NAMES["01"], min=24,
         say="عمود فولاذي وكمرتان تلتقيان عند صفيحة واحدة مثبّتة بالبراغي، والعمود قائم على قاعدته. نقطة الاتصال هي ما يجعل الهيكل متماسكاً، ولهذا هي الجزء الأحمر في العلامة.",
         use="الموقع والمعدات والخوذ", mean="الاتصال الذي يحمل الهيكل",
         apps=("helmet", "letter")),
    dict(n="02", slug="02-frame", name=I.NAMES["02"], min=32,
         say="على اليسار شبكة التخطيط، وعلى اليمين مبنى من ثلاثة طوابق يقوم عليها. العلامة تجمع العملين: الاستشارة التي ترسم، والمقاولة التي تبني.",
         use="المخططات والتقارير والواجهات", mean="من المخطط إلى المبنى",
         apps=("folder", "car")),
    dict(n="03", slug="03-upright", name=I.NAMES["03"], min=16,
         say="حرف A مبني كمنشأ: دعامة مائلة وعمودان وكمرة تربطها على أساس واحد. يُقرأ حرفاً من ALRAYA ويُرى هيكلاً قائماً.",
         use="الملابس والسيارات والأحجام الصغيرة", mean="الحرف الأول هيكلاً قائماً",
         apps=("vest", "gate")),
    dict(n="04", slug="04-portal", name=I.NAMES["04"], min=16,
         say="عمودان وجسر علوي يقفله حجر مفتاح في الوسط، فوق درجات. حجر المفتاح يمسك نصفي الجسر معاً، والبوابة أول ما يراه الداخل إلى المشروع.",
         use="المكتب والمراسلات الرسمية", mean="المدخل الثابت",
         apps=("facade", "letter")),
    dict(n="05", slug="05-survey-point", name=I.NAMES["05"], min=24,
         say="قبل أن يُبنى شيء يُحدَّد موقعه: علامات المساحة على الدائرة، ومستطيل التوقيع بزواياه ونقطة مركزه، ثم البوابة على قاعدتها. العلامة عن الدقة التي تسبق التنفيذ.",
         use="الاستشارات والمخططات والوثائق", mean="الدقة قبل التنفيذ",
         apps=("board", "desk")),
]
BY = {x["n"]: x for x in D}
LK, DIMS = {}, {}
FILL = {"p": "var(--p)", "a": "var(--a)"}
FNS = {k: f for k, _, f in M.ALL}
APP_NAME = {k: nm for k, nm, _ in M.ALL}
APP_NAME["board"] = "لوحة المشروع في الموقع"


def paths(layers, nd=0):
    return "".join(f'<path fill="{FILL[r]}" d="{pd(p, nd)}"/>' for p, r in layers)


def sprite():
    out = []
    for x in D:
        n = x["n"]
        for kind in ("symbol", "horizontal", "stacked", "stamp"):
            layers = LK[n]["stacked" if kind == "stamp" else kind]
            layers = lorigin(layers)
            w, h = lsize(layers)
            out.append(f'<g id="G-{n}-{kind}">{paths(layers)}</g>')
            for al, par in (("c", "xMidYMid"), ("r", "xMaxYMid"), ("l", "xMinYMid")):
                out.append(f'<symbol id="L-{n}-{kind}-{al}" viewBox="0 0 {w:.0f} {h:.0f}" preserveAspectRatio="{par} meet"><use href="#G-{n}-{kind}"/></symbol>')
            DIMS[f"{n}-{kind}"] = (w, h)
    return "".join(out)


def use(n, kind, sch="full", cls="", label=""):
    w, h = DIMS[f"{n}-{kind}"]
    lab = f' role="img" aria-label="{label}"' if label else ' aria-hidden="true"'
    return f'<svg class="{cls}" viewBox="0 0 {w:.0f} {h:.0f}"{lab}><use href="#L-{n}-{kind}-c" width="{w:.0f}" height="{h:.0f}" style="{M.SCH[sch]}"/></svg>'


# ------------------------------------------------------------------ the reveal
def reveal(n, uid, sch="full", label=""):
    """The mark in the order it is built: the frame is drawn, the plan lines
    appear, the structure rises from its base, the beam closes, the survey
    point settles, and the maroon part is set last. The markup rests in its
    final state; site6.js plays the build once when the mark comes into view."""
    ps, guide = I.parts(n)
    x0, y0, x1, y1 = bounds(*[p for p, _, _ in ps])
    pad = 24
    vb = f"{x0 - pad:.0f} {y0 - pad:.0f} {x1 - x0 + 2 * pad:.0f} {y1 - y0 + 2 * pad:.0f}"
    box = f"{x0 - pad:.0f} {y0 - pad:.0f} {x1 - x0 + 2 * pad:.0f} {y1 - y0 + 2 * pad:.0f}"
    defs, body = "", ""
    for i, (p, role, st) in enumerate(ps):
        g = f'<path fill="{FILL[role]}" d="{pd(p, 0)}"/>'
        if st == "frame" and guide:
            if guide[0] == "circle":
                _, cx, cy, r, w = guide
                gd = f"M{cx},{cy - r} A{r},{r} 0 1 0 {cx},{cy + r} A{r},{r} 0 1 0 {cx},{cy - r}"
            else:
                pts = guide[1]
                w = guide[2]
                gd = "M" + " L".join(f"{a:.1f},{b:.1f}" for a, b in pts) + " Z"
            defs += (f'<mask id="m{uid}{i}" maskUnits="userSpaceOnUse" x="{x0 - pad:.0f}" y="{y0 - pad:.0f}" width="{x1 - x0 + 2 * pad:.0f}" height="{y1 - y0 + 2 * pad:.0f}">'
                     f'<path data-st="frame" d="{gd}" fill="none" stroke="#fff" stroke-width="{w}" stroke-linecap="butt" pathLength="1" stroke-dasharray="1.02 1.02" stroke-dashoffset="0"/></mask>')
            body += f'<g mask="url(#m{uid}{i})">{g}</g>'
        elif st in ("build", "beam"):
            mode = "up" if st == "build" else "ltr"
            defs += f'<clipPath id="c{uid}{i}"><rect data-st="{st}" data-m="{mode}" data-box="{box}" x="{x0 - pad:.0f}" y="{y0 - pad:.0f}" width="{x1 - x0 + 2 * pad:.0f}" height="{y1 - y0 + 2 * pad:.0f}"/></clipPath>'
            body += f'<g clip-path="url(#c{uid}{i})">{g}</g>'
        else:
            bx0, by0, bx1, by1 = bounds(p)
            body += f'<g data-st="{st}" data-c="{(bx0 + bx1) / 2:.0f} {(by0 + by1) / 2:.0f}">{g}</g>'
    lab = f' role="img" aria-label="{label}"' if label else ' aria-hidden="true"'
    return f'<svg class="rv" data-rv viewBox="{vb}"{lab} style="{M.SCH[sch]}"><defs>{defs}</defs>{body}</svg>'


# ------------------------------------------------------------------ sections
def opening():
    marks = "".join(f'<a href="#d{x["n"]}" class="op-m" style="--i:{i}" aria-label="{x["n"]} {x["name"]}">{reveal(x["n"], "o" + x["n"], "rev")}<span>{x["name"]}</span></a>' for i, x in enumerate(D))
    return f'''<header class="op" id="top" data-nav="البداية">
  <div class="op-bg" aria-hidden="true"></div>
  <div class="op-in">
    <p class="op-k">الراية · مقاولات عامة واستشارات هندسية</p>
    <h1>تطوير هوية الراية</h1>
    <p class="op-s">خمسة اتجاهات مقترحة للشعار، مرسومة من جديد للمراجعة والاختيار.</p>
    <div class="op-g" data-rv-group>{marks}</div>
  </div>
</header>'''


def current_logo():
    """Sections 2-4, only with a real file of the current logo."""
    src = None
    for ext in ("svg", "png", "jpg", "jpeg", "webp"):
        f = os.path.join(ROOT, "assets", f"current-logo.{ext}")
        if os.path.exists(f):
            src = f"assets/current-logo.{ext}"
            break
    if not src:
        return ""
    notes_f = os.path.join(ROOT, "assets", "current-logo-notes.txt")
    notes = [l.strip() for l in open(notes_f, encoding="utf-8")] if os.path.exists(notes_f) else []
    notes = [l for l in notes if l]
    src_line = ""
    sf = os.path.join(ROOT, "assets", "current-logo-source.txt")
    if os.path.exists(sf):
        src_line = f'<figcaption>{open(sf, encoding="utf-8").read().strip()}</figcaption>'
    out = f'''<section class="sec cur" id="current" data-nav="الشعار الحالي">
  <div class="wrap" data-r>
    <h2 class="fx">الشعار الحالي</h2>
    <figure class="cur-f fx"><img src="{src}" alt="الشعار الحالي لشركة الراية" loading="lazy" decoding="async">{src_line}</figure>
  </div>
</section>'''
    if notes:
        li = "".join(f'<li class="fx" style="--dl:{i * .06:.2f}s">{t}</li>' for i, t in enumerate(notes))
        out += f'''<section class="sec cur-n" id="observe" data-nav="ملاحظات">
  <div class="wrap" data-r><h2 class="fx">ملاحظات على الشعار الحالي</h2><ul class="notes">{li}</ul></div>
</section>'''
    marks = "".join(f'<span style="--i:{i}">{use(x["n"], "symbol", "full")}</span>' for i, x in enumerate(D))
    out += f'''<section class="sec move" id="move" data-nav="إلى الاتجاهات">
  <div class="wrap mv" data-r>
    <img class="mv-old" src="{src}" alt="" aria-hidden="true">
    <div class="mv-new">{marks}</div>
    <p class="mv-t fx">من الشعار الحالي إلى خمسة اتجاهات مقترحة.</p>
  </div>
</section>'''
    return out


def direction(i, x):
    n = x["n"]
    apps = "".join(f'<figure class="app fx" style="--dl:{j * .08:.2f}s"><div class="app-w">{FNS[k](n, uid=f"d{n}{k}", sw=False)}</div><figcaption>{APP_NAME[k]}</figcaption></figure>' for j, k in enumerate(x["apps"]))
    sizes = "".join(f'<span style="--s:{s}px">{use(n, "symbol", "full")}<i dir="ltr">{s}</i></span>' for s in (16, 24, 32, 48))
    files = f"logos/{x['slug']}/svg/alraya-{n}-horizontal-full.svg"
    return f'''<section class="sec dir{" alt" if i % 2 else ""}" id="d{n}" data-nav="{n} · {x["name"]}">
  <div class="wrap">
    <div class="dir-h" data-r>
      <div class="dir-art">{reveal(n, "d" + n, "full", x["name"])}</div>
      <div class="dir-t">
        <p class="dir-n fx" dir="ltr">{n}<i>/05</i></p>
        <h2 class="fx">{x["name"]}</h2>
        <p class="dir-s fx" style="--dl:.06s">{x["say"]}</p>
      </div>
    </div>
    <div class="pr" data-r>
      <figure class="fx"><div class="pr-c pr-sym">{use(n, "symbol", "full")}</div><figcaption>العلامة وحدها</figcaption></figure>
      <figure class="fx" style="--dl:.05s"><div class="pr-c">{use(n, "horizontal", "full", "pr-l")}</div><figcaption>الاسم مع العلامة</figcaption></figure>
      <figure class="fx" style="--dl:.1s"><div class="pr-c pr-k">{use(n, "horizontal", "black", "pr-l")}</div><figcaption>لون واحد</figcaption></figure>
      <figure class="fx" style="--dl:.15s"><div class="pr-c pr-i">{use(n, "horizontal", "white", "pr-l")}</div><figcaption>على النيلي</figcaption></figure>
    </div>
    <div class="sz fx" data-r><div class="sz-r">{sizes}</div><p>بالمقاس الفعلي على الشاشة. أصغر مقاس بقي واضحاً في الاختبار: <bdi dir="ltr">{x["min"]}px</bdi> · <a href="{files}" download>ملف SVG</a></p></div>
    <div class="apps" data-r>{apps}</div>
  </div>
</section>'''


def compare():
    rows = ""
    for i, x in enumerate(D):
        n = x["n"]
        rows += f'''<a class="cr fx" style="--dl:{i * .05:.2f}s" href="#d{n}">
      <span class="cr-n" dir="ltr">{n}</span>
      <span class="cr-sym">{use(n, "symbol", "full")}</span>
      <span class="cr-name"><b>{x["name"]}</b><em>{x["mean"]}</em><small>الأنسب: {x["use"]}</small></span>
      <span class="cr-lk">{use(n, "horizontal", "black")}</span>
      <span class="cr-k cr-use"><i>الأنسب</i>{x["use"]}</span>
      <span class="cr-k cr-min"><i>أصغر مقاس</i><bdi dir="ltr">{x["min"]}px</bdi></span>
    </a>'''
    return f'''<section class="sec cmp" id="compare" data-nav="المقارنة">
  <div class="wrap" data-r>
    <h2 class="fx">الاتجاهات الخمسة جنباً إلى جنب</h2>
    <p class="sub fx" style="--dl:.05s">بالحجم نفسه والترتيب نفسه، للمقارنة واختيار اتجاه واحد يُستكمل.</p>
    <div class="cr-g">{rows}</div>
  </div>
</section>'''


def ending():
    return '''<footer class="end" id="end" data-nav="الخاتمة"><div class="wrap" data-r>
  <p class="end-q fx">هذه اتجاهات مقترحة للنقاش والاختيار، وليست هوية معتمدة.<br>بعد اختيار اتجاه واحد تُستكمل نسخه وتطبيقاته.</p>
  <p class="sig fx" style="--dl:.15s">تطوير الهوية البصرية — <b>عَدول</b> <span aria-hidden="true">|</span> <bdi dir="ltr">Adol</bdi></p>
</div></footer>'''


def nav(has_current):
    items = [("top", "البداية")]
    if has_current:
        items += [("current", "الشعار الحالي")]
    items += [(f"d{x['n']}", f"{x['n']} · {x['name']}") for x in D] + [("compare", "المقارنة"), ("end", "الخاتمة")]
    dots = "".join(f'<a href="#{i}"><i></i><span>{t}</span></a>' for i, t in items)
    links = "".join(f'<a href="#{i}">{t}</a>' for i, t in items)
    return (f'<nav class="dots" aria-label="أقسام العرض">{dots}</nav>'
            f'<div class="tb"><a class="tb-b" href="#top">الراية</a><span class="tb-c" aria-live="polite">البداية</span>'
            f'<button type="button" class="tb-m" aria-expanded="false" aria-controls="tb-l">الأقسام</button>'
            f'<nav class="tb-l" id="tb-l" aria-label="أقسام العرض">{links}</nav></div>')


def build():
    for x in D:
        LK[x["n"]] = I.lockups(x["n"])
    spr = sprite()
    cur = current_logo()
    body = "".join([nav(bool(cur)), "<main>", opening(), cur,
                    "".join(direction(i, x) for i, x in enumerate(D)), compare(), ending(), "</main>"])
    sprite_svg = f'<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>{spr}</defs></svg>'
    css = open(os.path.join(TOOLS, "site6.css"), encoding="utf-8").read()
    js = open(os.path.join(TOOLS, "site6.js"), encoding="utf-8").read()
    visible = re.sub(r"<[^>]+>", " ", body) + "ALRAYA·—–«»،؛؟0123456789px/×±%:.()@°SVG|"
    html = ('<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="theme-color" content="#1B2046">'
            '<title>تطوير هوية الراية — خمسة اتجاهات مقترحة</title>'
            '<meta name="description" content="خمسة اتجاهات مقترحة لشعار الراية للمقاولات العامة والاستشارات الهندسية. تطوير الهوية البصرية: عَدول.">'
            f'<style>{font_css(set(visible))}{css}</style></head><body>{sprite_svg}{body}<script>{js}</script></body></html>')
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(html)
    print(f"index.html {len(html) / 1024:.0f} KB")


if __name__ == "__main__":
    build()
