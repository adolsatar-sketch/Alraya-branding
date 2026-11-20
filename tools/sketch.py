"""Quick preview helper: render named shapes (black on white) to a PNG sheet."""
import os, sys, subprocess
sys.path.insert(0, os.path.dirname(__file__))
from vec import d, bounds

SP = os.environ.get("SP", "/tmp")


def svg_of(paths, pad=0.08, fills=None):
    x0, y0, x1, y1 = bounds(*paths)
    w, h = x1 - x0, y1 - y0
    s = max(w, h)
    p = s * pad
    vb = f"{x0 - p - (s - w) / 2:.1f} {y0 - p - (s - h) / 2:.1f} {s + 2 * p:.1f} {s + 2 * p:.1f}"
    fills = fills or ["#111"] * len(paths)
    body = "".join(f'<path fill="{f}" d="{d(q)}"/>' for q, f in zip(paths, fills))
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}">{body}</svg>'


def sheet(items, out, cell=300, cols=4):
    html = ['<html><body style="margin:0;background:#ddd;display:grid;grid-template-columns:repeat(%d,%dpx);gap:8px;padding:8px">' % (cols, cell)]
    for name, paths, fills in items:
        sv = svg_of(paths, fills=fills).replace("<svg ", f'<svg width="{cell}" height="{cell}" ')
        html.append(f'<div style="background:#fff;position:relative">{sv}<span style="position:absolute;bottom:4px;left:6px;font:12px sans-serif">{name}</span>'
                    f'<div style="position:absolute;top:6px;right:6px;width:24px;height:24px">{sv.replace(f"width=\"{cell}\" height=\"{cell}\"", "width=\"24\" height=\"24\"")}</div></div>')
    html.append("</body></html>")
    hp = os.path.join(SP, "sheet.html")
    open(hp, "w").write("".join(html))
    rows = (len(items) + cols - 1) // cols
    js = f"""const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();const p=await b.newPage({{viewport:{{width:{cols*(cell+8)+8},height:{rows*(cell+8)+8}}}}});await p.goto('file://{hp}');await p.screenshot({{path:'{out}',fullPage:true}});await b.close();}})();"""
    jp = os.path.join(SP, "sheet.js")
    open(jp, "w").write(js)
    subprocess.run(["node", jp], check=True)
