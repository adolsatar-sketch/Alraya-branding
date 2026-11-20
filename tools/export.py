"""Exports every logo version as SVG (editable), PDF (vector) and PNG.

    python3 tools/export.py
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
import cairosvg
from vec import d, bounds
import identity as I

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "logos")
DIRS = [("01", "01-al-uqda", "العقدة"), ("02", "02-line-to-mass", "من الخط إلى الكتلة"),
        ("03", "03-bearing-void", "الفراغ الحامل"), ("04", "04-signature", "التوقيع العربي"),
        ("05", "05-turning-point", "نقطة التحول"), ("06", "06-seal", "ختم الراية")]
SCHEMES = {
    "full": {"p": "#262E5D", "a": "#7D161A", "h": "#262E5D"},
    "mono": {"p": "#262E5D", "a": "#262E5D", "h": "#262E5D"},
    "black": {"p": "#000000", "a": "#000000", "h": "#000000"},
    "white": {"p": "#FFFFFF", "a": "#FFFFFF", "h": "#FFFFFF"},
    "on-indigo": {"p": "#FFFFFF", "a": "#D7A3A5", "h": "#FFFFFF"},
    "production": {"p": "#000000", "a": "#000000", "h": "#000000"},
}
ROLE_NAME = {"p": "primary", "a": "accent", "h": "drawn-line"}
PNG_SCHEMES = ("full", "black", "white", "on-indigo")


def svg_doc(layers, colors, title, pad=0.0):
    x0, y0, x1, y1 = bounds(*[p for p, _ in layers])
    w, h = x1 - x0, y1 - y0
    p = max(w, h) * pad
    groups = {}
    for path, role in layers:
        groups.setdefault(role, []).append(path)
    body = ""
    for role in ("p", "h", "a"):
        if role in groups:
            ds = "".join(d(q, 1) for q in groups[role])
            body += f'<g id="{ROLE_NAME[role]}"><path fill="{colors[role]}" d="{ds}"/></g>'
    vb = f"{x0 - p:.1f} {y0 - p:.1f} {w + 2 * p:.1f} {h + 2 * p:.1f}"
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" '
            f'width="{w + 2 * p:.0f}" height="{h + 2 * p:.0f}"><title>{title}</title>{body}</svg>\n'), w, h


def main():
    manifest = {}
    count = 0
    for n, slug, name in DIRS:
        base = os.path.join(OUT, slug)
        for sub in ("svg", "pdf", "png"):
            os.makedirs(os.path.join(base, sub), exist_ok=True)
        lk = I.lockups(n)
        manifest[n] = {"slug": slug, "name": name, "files": []}
        for kind, layers in lk.items():
            for sch, colors in SCHEMES.items():
                use = layers
                if sch == "production":
                    if n == "02":
                        # the drawn hairline cannot be embroidered or engraved:
                        # production uses the fully built letters
                        if kind == "symbol":
                            use = I.lheight(I.d02_symbol_solid(), I.lsize(layers)[1])
                        elif kind in ("primary_ar",):
                            use = I.lheight(I.d02_solid(), I.lsize(layers)[1])
                        else:
                            continue
                fn = f"alraya-{n}-{kind}-{sch}"
                doc, w, h = svg_doc(use, colors, f"ALRAYA {n} {kind} {sch}")
                open(os.path.join(base, "svg", fn + ".svg"), "w").write(doc)
                cairosvg.svg2pdf(bytestring=doc.encode(), write_to=os.path.join(base, "pdf", fn + ".pdf"))
                if sch in PNG_SCHEMES:
                    W = 2400
                    cairosvg.svg2png(bytestring=doc.encode(), write_to=os.path.join(base, "png", fn + ".png"),
                                     output_width=W, output_height=int(W * h / w) if w >= h else None)
                manifest[n]["files"].append(fn)
                count += 1
    json.dump(manifest, open(os.path.join(OUT, "manifest.json"), "w"), ensure_ascii=False, indent=1)
    readme = ["# ملفات الشعارات", "",
              "لكل اتجاه مجلد فيه ثلاث صيغ: `svg` (قابل للتحرير في Illustrator)، `pdf` (Vector)، و`png` (شفاف، عرض 2400px).", "",
              "## التكوينات",
              "- `symbol`: الرمز المختصر.",
              "- `primary_ar`: الشعار العربي الرئيسي.",
              "- `ar_en`: العربي والإنكليزي.",
              "- `horizontal`: التكوين الأفقي.",
              "- `stacked`: التكوين العمودي.",
              "- `descriptor`: الأفقي مع وصف النشاط بالعربية والإنكليزية.",
              "- `circular`: التكوين الدائري (الختم).", "",
              "## النسخ اللونية",
              "- `full`: النيلي والماروني.",
              "- `mono`: لون واحد (نيلي).",
              "- `black` / `white`.",
              "- `on-indigo`: للخلفية النيلية.",
              "- `production`: لون واحد للحفر والتطريز والختم البارز. في الاتجاه 02 تُستخدم الحروف المبنية كاملة لأن الخط الرفيع لا يُطرَّز.", "",
              "كل ملف SVG مقسّم إلى طبقات: `primary` و`accent` و`drawn-line`."]
    open(os.path.join(OUT, "README.md"), "w").write("\n".join(readme))
    print(count, "versions x (svg+pdf) + png")


if __name__ == "__main__":
    main()
