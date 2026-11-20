"""Builds index.html — ALRAYA identity (v5).

    python3 tools/build5.py

v1–v4 stay untouched in their folders. Additional options are curated
from earlier rounds and also written as standalone SVG files in extras/.
"""
import os, re, sys, shutil
sys.path.insert(0, os.path.dirname(__file__))
import identity5 as I
import mock3 as M
from vec import d as pd
from build3 import font_css, old_assets

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.dirname(__file__)

D = [
    dict(n="01", name="حلقة التاء",
         say="الرمز هو التاء المربوطة التي يُختم بها اسم «الراية»: حلقة مغلقة ونقطتان. شكل واحد يُعرف من بعيد، ويعمل بلون واحد على الخوذة والختم وصورة الحساب.",
         apps=("helmet", "avatar"), wipe="up", min=16),
    dict(n="02", name="اللوحة",
         say="الاسم مكتوب داخل لوحة، كما تُكتب أسماء المشاريع على لوحات المواقع. جاهز للواجهات والسيارات واللوحات، ويُقرأ من مسافة بعيدة.",
         apps=("board", "car"), wipe="rtl", min=40),
    dict(n="03", name="را",
         say="«را» أول ما يُسمع من الاسم بعد «الـ»، بخط عريض متين. رمز من حرفين يُقرأ فوراً، ويُنفَّذ بسهولة بالقص والتطريز.",
         apps=("vest", "desk"), wipe="rtl", min=16),
    dict(n="04", name="ستة بستة",
         say="«الراية» و«ALRAYA» ستة أحرف في كل لغة، فوُضع الاسمان بالعرض نفسه فوق بعضهما. هوية بلغتين متكافئتين، مناسبة للمراسلات الرسمية والجهات الأجنبية.",
         apps=("letter", "folder"), wipe="both", min=40),
    dict(n="05", name="التركيب",
         say="راءٌ مركّبة من قطعتين، جذع مستقيم وذيل منحنٍ، تلتقيان على خط واحد كما تُركَّب القطع في الموقع. العلامة عن دقة التنفيذ، وتبقى واضحة بلون واحد.",
         apps=("vest", "board"), wipe="up", min=24, compare=True),
    dict(n="06", name="ختم الراية",
         say="ختم دائري هادئ: النشاط بالعربية أعلى الحلقة، وALRAYA أسفلها، والاسم في المركز. مناسب للوثائق والمخططات المعتمدة والمراسلات الرسمية.",
         apps=("letter", "folder"), wipe="seal", min=40),
]
BY = {x["n"]: x for x in D}
REC = [("01", "أقوى رمز بين الستة بالحجم الصغير وبلون واحد، والحرف فيه من اسم الشركة نفسه."),
       ("06", "يلبّي ميل العميل إلى الشعار الدائري المؤسسي، ويصلح ختماً رسمياً على الوثائق والمخططات.")]
APPS = ("helmet", "vest", "desk", "letter", "folder", "board", "car", "avatar", "insta")
APPS_DEFAULT = "01"
EXTRAS = [  # (id, name, source)
    ("v3-03", "الفراغ الحامل", ("v3", "03-bearing-void", "03")),
    ("v3-05", "نقطة التحول", ("v3", "05-turning-point", "05")),
    ("v3-01", "العقدة", ("v3", "01-al-uqda", "01")),
    ("v3-06", "ختم الألف والتاء", ("v3", "06-seal", "06")),
    ("v2-01", "الشبكة الكوفية", ("v2", "01")),
    ("v2-03", "الطيّة", ("v2", "03")),
    ("v2-04", "الزاوية", ("v2", "04")),
    ("v2-05", "التعاشق", ("v2", "05")),
    ("v1-06", "نقطة الإسناد", ("v1", "06")),
]
LK, DIMS = {}, {}
FILL = {"p": "var(--p)", "a": "var(--a)", "h": "var(--h)"}


def paths(layers, nd=0):
    return "".join(f'<path fill="{FILL[r]}" d="{pd(p, nd)}"/>' for p, r in layers)


def sprite():
    out = []
    for x in D:
        n = x["n"]
        for kind in ("symbol", "word", "horizontal", "stacked", "descriptor", "circular", "stamp"):
            lk = LK[n]
            layers = lk.get("circular") or lk["stacked"] if kind == "stamp" else lk.get(kind)
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


# ------------------------------------------------------------------ reveal
def scene(x):
    """The mark alone, revealed the way it is read. Clip rectangles are
    driven by scroll (site3.js / data-wipe)."""
    n = x["n"]
    lay = I.lorigin(LK[n]["symbol"])
    w, h = I.lsize(lay)
    pad = max(w, h) * 0.06
    vb = f"{-pad:.0f} {-pad:.0f} {w + 2 * pad:.0f} {h + 2 * pad:.0f}"
    big = max(w, h) * 3
    def clip(cid, mode, s, e):
        return (f'<clipPath id="{cid}"><rect data-wipe="{s} {e} {mode}" data-box="{-pad:.0f} {-pad:.0f} {w + 2 * pad:.0f} {h + 2 * pad:.0f}" '
                f'x="0" y="0" width="0" height="0"/></clipPath>')
    art = ""
    mode = x["wipe"]
    P = [L for L in lay if L[1] == "p"]
    A = [L for L in lay if L[1] == "a"]
    if mode == "up":
        art += clip(f"k{n}", "up", .06, .46) + f'<g clip-path="url(#k{n})">{paths(P)}</g>'
        art += f'<g class="fill drop" style="--s:.44;--e:.58">{paths(A)}</g>'
    elif mode == "rtl":
        art += clip(f"k{n}", "rtl", .06, .5) + f'<g clip-path="url(#k{n})">{paths(P)}</g>'
        art += f'<g class="fill grow" style="--s:.46;--e:.58">{paths(A)}</g>'
    elif mode == "both":
        # Arabic arrives from the right, ALRAYA from the left, the rule meets them
        art += clip(f"k{n}", "rtl", .06, .4) + f'<g clip-path="url(#k{n})">{paths(P)}</g>'
        art += f'<g class="fill grow" style="--s:.4;--e:.54">{paths(A)}</g>'
    elif mode == "meet":
        art += clip(f"k{n}", "ltr", .06, .4) + f'<g clip-path="url(#k{n})">{paths(P)}</g>'
        art += f'<g class="fill riseY" style="--s:.38;--e:.54">{paths(A)}</g>'
    else:
        art += f'<circle class="pen guide" pathLength="1" cx="{w / 2:.0f}" cy="{h / 2:.0f}" r="{w / 2:.0f}" style="--s:.02;--e:.22"/>'
        art += clip(f"k{n}", "rtl", .18, .5) + f'<g clip-path="url(#k{n})">{paths(P)}</g>'
        art += f'<g class="fill grow" style="--s:.46;--e:.58">{paths(A)}</g>'
    return f'<svg class="sc-art" viewBox="{vb}" role="img" aria-label="{x["name"]}" style="{M.SCH["full"]}">{art}</svg>'


# ------------------------------------------------------------------ sections
def opening():
    marks = "".join(f'<span style="--i:{i}">{use(x["n"], "symbol", "rev")}</span>' for i, x in enumerate(D))
    return f'''<header class="open" id="top" data-nav="البداية">
  <p class="op-1">قبل أن يُبنى المشروع… تُبنى الفكرة.</p>
  <h1 class="op-2">الراية</h1>
  <p class="op-3">ستة اتجاهات لهوية شركة مقاولات عامة واستشارات هندسية.</p>
  <div class="op-marks" aria-hidden="true">{marks}</div>
  <p class="op-sig"><span>هوية بصرية وتصميم</span><b>عَدول</b><i dir="ltr">Adol</i></p>
</header>'''


def board():
    cells = "".join(f'<a class="lu-c fx" style="--dl:{i * .05:.2f}s" href="#d{x["n"]}">{use(x["n"], "horizontal", "black", "lu-l", x["name"])}'
                    f'<span><i dir="ltr">{x["n"]}</i>{x["name"]}</span></a>' for i, x in enumerate(D))
    return f'''<section class="lineup sec" id="board" data-nav="الخيارات الستة" data-r>
  <div class="sec-h"><h2 class="fx">الخيارات الستة</h2><p class="sub fx" style="--dl:.06s">بالأسود، وبالحجم نفسه، وعلى الخلفية نفسها.</p></div>
  <div class="lu-g">{cells}</div>
</section>'''


def chapter(x):
    n = x["n"]
    fns = {a: f for a, _, f in M.ALL}
    nms = {a: nm for a, nm, _ in M.ALL}
    apps = "".join(f'<figure class="ca fx" style="--dl:{j * .08:.2f}s"><div class="mk-w">{fns[k](n, uid=f"c{n}{k}", sw=False)}</div><figcaption>{nms[k]}</figcaption></figure>' for j, k in enumerate(x["apps"]))
    sizes = "".join(f'<div style="width:{s}px;height:{s}px">{use(n, "symbol", "full")}</div>' for s in (16, 24, 40, 80))
    return f'''<section class="chap d{n}" id="d{n}" data-nav="{n} · {x["name"]}">
  <div class="scene" data-scene>
    <div class="pin">
      <div class="sc-h"><span class="sc-n" dir="ltr">{n}<i>/06</i></span><h2>{x["name"]}</h2></div>
      {scene(x)}
      <p class="sc-story">{x["say"]}</p>
    </div>
  </div>
  <div class="after">
    <div class="proof" data-r>
      <div class="pf pf-w fx">{use(n, "horizontal", "full", "pf-l")}</div>
      <div class="pf pf-b fx" style="--dl:.06s">{use(n, "horizontal", "rev", "pf-l")}</div>
      <div class="pf pf-k fx" style="--dl:.12s">{use(n, "horizontal", "black", "pf-l")}</div>
    </div>
    <div class="row2" data-r>
      <div class="pf-s fx">{use(n, "symbol", "full", "pf-i")}<span>النسخة المختصرة المعتمدة</span></div>
      <div class="sz fx" style="--dl:.06s"><p>بالمقاس الفعلي</p><div class="szs">{sizes}</div><p class="szn">أصغر مقاس اختُبر وبقي واضحاً: <bdi dir="ltr">{x["min"]}px</bdi></p></div>
    </div>
    {compare_strip(x) if x.get("compare") else ""}
    <div class="ch-apps" data-r>{apps}</div>
  </div>
</section>'''


def compare_strip(x):
    n = x["n"]
    app = M.helmet(n, uid=f"cs{n}", sw=False)
    return f'''<div class="cmp4" data-r>
      <figure class="fx"><div class="c4">{use(n, "symbol", "full", "c4i")}</div><figcaption>العلامة وحدها</figcaption></figure>
      <figure class="fx" style="--dl:.06s"><div class="c4">{use(n, "horizontal", "full", "c4l")}</div><figcaption>الاسم مع العلامة</figcaption></figure>
      <figure class="fx" style="--dl:.12s"><div class="c4">{use(n, "horizontal", "black", "c4l")}</div><figcaption>لون واحد</figcaption></figure>
      <figure class="fx" style="--dl:.18s"><div class="c4 c4a">{app}</div><figcaption>على الخوذة</figcaption></figure>
    </div>'''


def apps():
    chips = "".join(f'<button type="button" class="chip{" on" if x["n"] == APPS_DEFAULT else ""}" data-k="{x["n"]}" aria-pressed="{"true" if x["n"] == APPS_DEFAULT else "false"}"><i dir="ltr">{x["n"]}</i>{x["name"]}</button>' for x in D)
    figs = ""
    for k, nm, fn in M.ALL:
        if k in APPS:
            figs += f'<figure class="ap fx"><div class="mk-w">{fn(APPS_DEFAULT, uid="a" + k)}</div><figcaption>{nm}</figcaption></figure>'
    return f'''<section class="apps sec" id="apps" data-nav="التطبيقات">
  <div class="sec-h" data-r><h2 class="fx">التطبيقات</h2><p class="sub fx" style="--dl:.06s">اختر خياراً فيتغيّر في كل التطبيقات معاً. الشعار نفسه في كل مكان.</p></div>
  <div class="switch" role="group" aria-label="اختيار الخيار">{chips}</div>
  <div class="ap-g" data-r>{figs}</div>
</section>'''


def recommend():
    cards = "".join(f'<article class="rc fx" style="--dl:{.08 + i * .12:.2f}s"><div class="rc-l">{use(n, "horizontal", "rev", "rl")}</div>'
                    f'<h3><i dir="ltr">{n}</i>{BY[n]["name"]}</h3><p>{why}</p></article>' for i, (n, why) in enumerate(REC))
    return f'''<section class="rec" id="rec" data-nav="التوصية"><div class="rec-in" data-r>
  <h2 class="fx">نرشّح خيارين</h2>
  <div class="rc-g">{cards}</div>
</div></section>'''


def extras_assets(v1vb, v2vb):
    """Write each additional option as a standalone SVG (extras/) and return
    {id: (svg_markup_for_page, file)}."""
    os.makedirs(os.path.join(ROOT, "extras"), exist_ok=True)
    v1 = open(os.path.join(ROOT, "v1", "index.html"), encoding="utf-8").read()
    v2 = open(os.path.join(ROOT, "v2", "index.html"), encoding="utf-8").read()
    out = {}
    for eid, name, src in EXTRAS:
        fn = f"extras/alraya-option-{eid}.svg"
        if src[0] == "v3":
            s = open(os.path.join(ROOT, "v3", "logos", src[1], "svg", f"alraya-{src[2]}-horizontal-full.svg"), encoding="utf-8").read()
            s = s.split("\n", 1)[1] if s.startswith("<?xml") else s
        elif src[0] == "v2":
            g = re.search(r'<g id="G-%s-lockup">(.*?)</g>' % src[1], v2, re.S).group(1)
            vb = v2vb[src[1]]
            g = g.replace("var(--p)", "#262E5D").replace("var(--a)", "#7D161A")
            s = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}">{g}</svg>'
        else:
            m = re.search(r'<symbol id="M-%s-lockup-full" viewBox="([^"]+)">(.*?)</symbol>' % src[1], v1, re.S)
            s = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{m.group(1)}">{m.group(2)}</svg>'
        open(os.path.join(ROOT, fn), "w", encoding="utf-8").write(s)
        out[eid] = fn
    return out


def extras(files):
    cells = "".join(f'<figure class="xo fx" style="--dl:{(i % 5) * .04:.2f}s"><div class="xo-w"><img src="{files[eid]}" alt="{name}" loading="lazy" decoding="async"></div>'
                    f'<figcaption><b>{name}</b><a href="{files[eid]}" download>SVG</a></figcaption></figure>' for i, (eid, name, _) in enumerate(EXTRAS))
    return f'''<section class="xtra sec" id="extra" data-nav="خيارات إضافية" data-r>
  <div class="sec-h"><h2 class="fx">خيارات إضافية للاختيار</h2><p class="sub fx" style="--dl:.06s">من مراحل البحث السابقة، بعد استبعاد المكرر والضعيف. كل منها متاح كبديل، وملفه جاهز.</p></div>
  <div class="xo-g">{cells}</div>
</section>'''


def ending():
    return '''<footer class="end" id="end" data-nav="الخاتمة"><div class="end-in" data-r>
  <p class="end-q fx">الشعار الذي سنختاره اليوم،<br>سيوقّع مشاريع الراية لسنوات.</p>
  <p class="end-sig fx" style="--dl:.2s"><span>هوية بصرية وتصميم</span><b>عَدول</b><i dir="ltr">Adol</i></p>
</div></footer>'''


def nav():
    items = [("top", "البداية"), ("board", "الخيارات الستة")] + [(f"d{x['n']}", f"{x['n']} · {x['name']}") for x in D] + \
            [("apps", "التطبيقات"), ("rec", "التوصية"), ("extra", "خيارات إضافية"), ("end", "الخاتمة")]
    links = "".join(f'<a href="#{i}"><i></i><span>{t}</span></a>' for i, t in items)
    return (f'<nav class="nav" aria-label="أقسام العرض">{links}</nav>'
            f'<div class="mbar"><button type="button" class="mbar-b" aria-expanded="false" aria-controls="mbar-l"><span class="mbar-c">البداية</span><i></i></button>'
            f'<div class="mbar-p"><i></i></div><nav class="mbar-l" id="mbar-l" aria-label="أقسام العرض">{links}</nav></div>')


def build():
    for x in D:
        LK[x["n"]] = I.lockups(x["n"])
    spr = sprite()
    v1s, v1vb, v2g, v2vb = old_assets()
    files = extras_assets(v1vb, v2vb)
    body = "".join(['<div class="prog" aria-hidden="true"><i></i></div>', nav(), "<main>", opening(), board(),
                    "".join(chapter(x) for x in D), apps(), recommend(), extras(files), ending(), "</main>"])
    sprite_svg = f'<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>{spr}</defs></svg>'
    css = "".join(open(os.path.join(TOOLS, f), encoding="utf-8").read() for f in ("site3.css", "site4.css", "site5.css"))
    js = open(os.path.join(TOOLS, "site3.js"), encoding="utf-8").read() + open(os.path.join(TOOLS, "site5.js"), encoding="utf-8").read()
    visible = re.sub(r"<[^>]+>", " ", body) + "ALRAYA·—–«»،؛؟0123456789px/×±%:.()@°SVG"
    html = ('<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="theme-color" content="#1B2046">'
            '<title>الراية — ستة خيارات للهوية</title>'
            '<meta name="description" content="ستة خيارات لشعار الراية للمقاولات العامة والاستشارات الهندسية. هوية بصرية وتصميم: عَدول.">'
            f'<style>{font_css(set(visible))}{css}</style></head><body>{sprite_svg}{body}<script>{js}</script></body></html>')
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(html)
    print(f"index.html {len(html) / 1024:.0f} KB")


if __name__ == "__main__":
    build()
