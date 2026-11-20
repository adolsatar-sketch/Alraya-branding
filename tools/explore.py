"""Research stage: black-and-white explorations, kept as working evidence in
design-process/. Not shown to the client.

    python3 tools/explore.py
"""
import os, sys, math, json, subprocess
sys.path.insert(0, os.path.dirname(__file__))
from vec import *
from pen import Skel, vstroke, profile
import identity as I

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "design-process", "explorations")
CRIT = ["التميّز", "التذكّر", "الملاءمة", "قوة الفكرة", "جودة الرسم", "الحجم الصغير", "الإنتاج", "الاختلاف"]


def flat(layers):
    return union(*[p for p, _ in layers])


def tile_ra(w=128):
    t = I.squircle(0, 0, 1000)
    sk = Skel(585, -60).L(585, 330).C(585, 620, 430, 790, 120, 850).C(40, 865, -20, 870, -80, 872)
    return diff(t, vstroke(sk, w))


def E():
    ex = []

    def add(slug, name, cat, shape, verdict, scores, pick=None):
        ex.append(dict(slug=slug, name=name, cat=cat, shape=shape, verdict=verdict, scores=scores, pick=pick))

    # ---------------- negative space
    add("void-ra", "راء في الفراغ", "فراغ سلبي", flat(I.d03_symbol()),
        "كتلة واحدة يحملها فراغ على شكل راء. تُقرأ وتُتذكّر من النظرة الأولى.", [5, 5, 4, 5, 4, 5, 5, 5], "03")
    add("void-ra-even", "راء بقناة ثابتة", "فراغ سلبي", tile_ra(150),
        "القناة الثابتة تجعل الراء أقرب لطريق أو خط سير. الاستدقاق في النسخة المختارة أوضح.", [4, 4, 4, 4, 3, 4, 5, 4])
    add("void-alif", "ألف في الفراغ", "فراغ سلبي", diff(I.squircle(0, 0, 1000), rect(440, -10, 120, 760)),
        "يشبه زر الإيقاف المؤقت. استُبعد.", [1, 2, 2, 2, 3, 4, 5, 1])
    add("void-swoosh", "انحناءة صاعدة", "فراغ سلبي",
        diff(I.squircle(0, 0, 1000), vstroke(Skel(-60, 900).C(300, 860, 700, 600, 1060, 120), profile((0, 60), (0.5, 140), (1, 60)))),
        "حركة صاعدة عامة تذكّر بشعارات رياضية. لا علاقة لها بالاسم.", [1, 2, 2, 1, 3, 4, 4, 1])
    # ---------------- letters
    add("ra-alif-joint", "«را» في عقدة", "حروفي", flat(I.d01_symbol()),
        "ألف قائمة وراء تمر أمامها: عنصران يلتقيان في مفصل واحد، ومقطع «را» يُقرأ فوراً.", [4, 4, 5, 4, 4, 4, 4, 4], "01")
    add("ra-alif-plain", "«را» بلا مفصل", "حروفي",
        union(vstroke(Skel(250, 0).L(250, 860), 170), vstroke(Skel(640, 250).L(640, 560).C(640, 790, 470, 920, 60, 960), profile((0, 170), (0.5, 160), (1, 6)), end="taper")),
        "مجرد حرفين متجاورين. بلا التقاء لا توجد فكرة.", [2, 2, 4, 2, 4, 4, 5, 2])
    lo = vstroke(Skel(0, -240).L(0, 0).C(0, 190, -90, 420, -470, 600), profile((0, 200), (0.5, 200), (1, 4)), end="taper")
    add("ra-r-halfturn", "راء وr بنصف دورة", "حروفي", union(lo, rotate(lo, 180, 0, 0)),
        "الفكرة صحيحة لغوياً لكن الشكل يُقرأ حرف S. استُبعد.", [3, 3, 3, 4, 3, 4, 4, 3])
    r1 = vstroke(Skel(20, 0).L(20, 330).C(20, 620, -60, 800, -330, 880), profile((0, 150), (0.4, 150), (1, 4)), end="taper")
    add("ra-mirror-pair", "راءان متقابلتان", "حروفي", union(r1, mirror_x(r1, 0)),
        "يشبه ذيل سمكة أو شوكة. استُبعد.", [2, 2, 2, 2, 3, 3, 4, 2])
    stem = rect(0, 0, 170, 820)
    bowl = diff(P().M(0, 0).L(360, 0).C(560, 0, 680, 120, 680, 300).C(680, 480, 560, 600, 360, 600).L(0, 600).Z().path(),
                P().M(170, 170).L(360, 170).C(460, 170, 515, 215, 515, 300).C(515, 385, 460, 430, 360, 430).L(170, 430).Z().path())
    tail = vstroke(Skel(980, 0).L(980, 470).C(980, 760, 760, 880, 330, 900), profile((0, 170), (0.4, 170), (1, 4)), end="taper")
    add("R-ra-cross", "R وراء متقاطعتان", "حروفي", union(stem, bowl, poly((380, 430), (550, 430), (900, 820), (730, 820)), tail),
        "يُقرأ «RJ». استُبعد.", [2, 2, 3, 3, 3, 3, 4, 2])
    add("R-ra-horn", "R بذيل راء", "حروفي",
        union(stem, bowl, vstroke(Skel(470, 430).C(470, 700, 330, 960, -330, 1060), profile((0, 160), (1, 4)), end="taper")),
        "يقترب من رمز الوصفة الطبية ℞. استُبعد.", [2, 2, 2, 2, 3, 3, 4, 2])
    add("Y-ya", "Y والياء", "حروفي", flat(I.d05_symbol()),
        "مساران يلتقيان في نقطة ويكملان خطاً واحداً، ونقطتا الياء تحته. يربط الاسمين بحرف واحد.", [4, 4, 4, 4, 4, 5, 5, 5], "05")
    add("Y-ya-notch", "Y بفصل حاد", "حروفي",
        union(diff(stroke(P().M(-300, 0).L(0, 470).L(300, 0).path(), 178, "butt", "miter"), rect(-2000, -2000, 4000, 2000)), rect(-89, 520, 178, 320), diamond(-100, 990, 166), diamond(100, 990, 166)),
        "الفصل الأفقي يقطع الحرف إلى قطعتين بلا سبب. النسخة المختارة تجعل الالتقاء هو الفكرة.", [3, 3, 4, 3, 3, 4, 4, 4])
    # ---------------- structure / knot
    def staple(w, s, right=True):
        return diff(rect(0, 0, s, s), rect(w, w, s - w, s - 2 * w) if right else rect(0, w, s - w, s - 2 * w))
    a = staple(140, 620); b = move(staple(140, 620, False), 300, 0)
    add("woven-staples", "قطعتان متشابكتان", "بنيوي", union(a, b),
        "يشبه حلقات سلسلة أو شعارات تقنية. استُبعد.", [2, 2, 3, 3, 2, 4, 4, 2])
    add("L-members", "زاويتان متعاشقتان", "بنيوي",
        union(rect(0, 0, 170, 900), rect(-450, 0, 620, 170), rect(-280, 0, 170, 900), rect(-280, 730, 620, 170)),
        "قريب جداً من اتجاه سابق (التعاشق). استُبعد لتجنب التكرار.", [2, 3, 3, 3, 3, 5, 5, 1])
    fold = union(rect(0, 0, 200, 560), poly((0, 560), (200, 560), (-180, 940), (-380, 940)))
    add("hinge", "مستويان على مفصل", "بنيوي", fold,
        "مفصل بين مستويين، لكنه يكرر فكرة «الطيّة» السابقة.", [2, 3, 3, 3, 3, 4, 5, 1])
    add("three-uprights", "إيقاع ا ل ا", "بنيوي",
        union(rect(0, 0, 120, 900), rect(260, 0, 120, 900), rect(520, 300, 120, 600), rect(780, 0, 120, 900)),
        "يقرأ كباركود أو أعمدة مبنى. استُبعد.", [1, 2, 2, 2, 3, 4, 5, 2])
    # ---------------- seal centres
    ringp = diff(circle(0, 0, 500), circle(0, 0, 476))
    add("seal-phi", "الألف داخل التاء", "ختم", flat(I.d06_badge()),
        "أول حرف يخترق حلقة آخر حرف، والاسمان على الختم. هادئ ومؤسسي ويُعرف بلا كتابة.", [4, 4, 5, 4, 4, 4, 4, 4], "06")
    add("seal-diamond-alif", "معيّن فيه ألف", "ختم", union(ringp, diff(diamond(0, 0, 420, 600), rect(-34, -190, 68, 380))),
        "يشبه فتحة نقود أو عيناً. استُبعد.", [2, 2, 2, 2, 3, 4, 4, 3])
    add("seal-four-dots", "النقاط الأربع", "ختم",
        union(ringp, *[diamond(x, y, 200) for x, y in ((0, -115), (0, 115), (-115, 0), (115, 0))]),
        "زخرفة عامة تشبه شعارات معروفة. استُبعد.", [1, 2, 3, 2, 3, 5, 5, 2])
    add("seal-loop-dots", "حلقة ونقاط", "ختم",
        union(ringp, diff(circle(0, 40, 170), circle(0, 40, 95)), diamond(-75, -230, 95), diamond(75, -230, 95), diamond(-75, 310, 95), diamond(75, 310, 95)),
        "يُقرأ وجهاً. استُبعد.", [2, 2, 3, 2, 3, 4, 4, 2])
    add("seal-keystone", "حجر العقد", "ختم",
        union(ringp, diff(poly((-200, -260), (200, -260), (140, 260), (-140, 260)), poly((-36, -170), (36, -200), (36, 170), (-36, 170)))),
        "يشبه دلواً. استُبعد.", [1, 2, 3, 3, 3, 4, 5, 2])
    # ---------------- lettering
    b2, d2 = I.d02_letters()
    add("mono-word", "الراية بخط واحد", "حروفي", union(b2, d2),
        "أساس الحروف المرسومة: سماكة واحدة وزوايا قائمة. وحده لا يحمل فكرة، فصار أساساً للاتجاه 02.", [3, 3, 4, 2, 4, 4, 5, 3])
    add("line-to-mass", "من الخط إلى الكتلة", "حروفي", flat(I.d02_word()),
        "الحروف تبدأ خطاً مرسوماً وتنتهي كتلة، على خط قطع صاعد واحد. التحول جزء من الحروف نفسها.", [5, 4, 5, 5, 4, 3, 3, 5], "02")
    add("line-to-mass-flat", "قطع أفقي", "حروفي",
        union(inter(union(b2, d2), rect(-200, -300, 2000, 800)), outline(diff(union(b2, d2), rect(-200, -300, 2000, 800)), 7)),
        "القطع الأفقي يبدو كمنسوب صبّ، لكنه يلغي الإحساس بالتقدّم من أول الكلمة لآخرها.", [3, 3, 4, 3, 4, 3, 3, 4])
    b4, d4 = I.d04_letters()
    add("signature", "التوقيع", "حروفي", union(b4, d4),
        "حروف مرسومة بقلم متغيّر السماكة، وذيل الراء يمتد تحت الألف. يُعرف من شكله وحده.", [5, 4, 4, 4, 4, 3, 4, 5], "04")
    add("signature-ya-ta", "«ية» من التوقيع", "حروفي", flat(I.d04_symbol()),
        "الياء والتاء ونقاطهما الأربع: النسخة المختصرة للتوقيع، مأخوذة من الحروف نفسها.", [4, 4, 4, 4, 4, 4, 4, 4])
    add("stencil", "الاسم بالاستنسل", "حروفي",
        diff(union(b2, d2), rect(-100, -330, 2000, 40)),
        "قطع واحد عبر الكلمة. يبقى «الكلمة مع إضافة»، وهي المشكلة التي نريد تجاوزها. استُبعد.", [2, 2, 3, 2, 3, 3, 4, 2])
    return ex


def svg_bw(shape, pad=0.08):
    x0, y0, x1, y1 = bounds(shape)
    w, h = x1 - x0, y1 - y0
    s = max(w, h); p = s * pad
    vb = f"{x0 - p - (s - w) / 2:.0f} {y0 - p - (s - h) / 2:.0f} {s + 2 * p:.0f} {s + 2 * p:.0f}"
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}"><path fill="#000" d="{d(shape, 1)}"/></svg>'


def main():
    os.makedirs(OUT, exist_ok=True)
    ex = E()
    cells = []
    rows = []
    for i, e in enumerate(ex, 1):
        fn = f"{i:02d}-{e['slug']}.svg"
        sv = svg_bw(e["shape"])
        open(os.path.join(OUT, fn), "w").write(sv)
        tot = sum(e["scores"])
        tag = f"<b style='color:#7D161A'>→ {e['pick']}</b>" if e["pick"] else ""
        cells.append(f'<div class="c"><div class="s">{sv}</div><p><span>{i:02d}</span> {e["name"]} {tag}</p></div>')
        rows.append(f"| {i:02d} | {e['name']} | {e['cat']} | " + " | ".join(str(x) for x in e["scores"]) +
                    f" | **{tot}** | {('اختير ← ' + e['pick']) if e['pick'] else 'استُبعد / مرجع'} | {e['verdict']} |")
    html = ('<!doctype html><html dir="rtl" lang="ar"><meta charset="utf-8"><style>body{margin:0;padding:24px;background:#fff;font:14px system-ui;color:#111}'
            '.g{display:grid;grid-template-columns:repeat(6,1fr);gap:14px}.c{border:1px solid #ddd}.s svg{display:block;width:100%;height:auto}'
            '.c p{margin:0;padding:6px 8px;border-top:1px solid #eee}.c span{font-family:monospace;color:#888}h1{font-size:18px}</style>'
            f'<h1>استكشافات الراية — أبيض وأسود ({len(ex)})</h1><div class="g">{"".join(cells)}</div></html>')
    hp = os.path.join(ROOT, "design-process", "contact-sheet.html")
    open(hp, "w").write(html)
    js = (f"const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();const p=await b.newPage({{viewport:{{width:1500,height:900}}}});"
          f"await p.goto('file://{hp}');await p.screenshot({{path:'{os.path.join(ROOT, 'design-process', 'contact-sheet.png')}',fullPage:true}});await b.close();}})();")
    jp = os.path.join(ROOT, "design-process", ".sheet.js")
    open(jp, "w").write(js)
    subprocess.run(["node", jp], check=True)
    os.remove(jp)
    md = ["# مرحلة البحث — داخلي، لا يُعرض على العميل", "",
          f"{len(ex)} استكشافاً بالأبيض والأسود. كل شكل حُكم عليه بلا قصة أولاً، ثم بالمعايير (1–5).", "",
          "| # | الاستكشاف | النوع | " + " | ".join(CRIT) + " | المجموع | القرار | الملاحظة |",
          "|---|---|---|" + "---|" * len(CRIT) + "---|---|---|"] + rows + ["",
          "## قاعدة الاختيار",
          "- يُستبعد أي شكل يشبه أيقونة إنترنت أو شعار مقاولات تقليدياً أو حرفاً لاتينياً آخر.",
          "- لا يُكتب لشكل ضعيف قصة لتبريره.",
          "- اختير لكل منطق (فراغ، حروف، التقاء، تحوّل، توقيع، ختم) أقوى شكل فقط."]
    open(os.path.join(ROOT, "design-process", "README.md"), "w").write("\n".join(md))
    print(len(ex), "explorations")


if __name__ == "__main__":
    main()
