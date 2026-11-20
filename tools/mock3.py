"""Application mockups (vector, with light, material and shadow).

Every logo is placed with <use> of an approved symbol: L-{dir}-{kind}-{align}
(kind: symbol | horizontal | stacked | primary | circular | descriptor).
Colours come from CSS custom properties --p (primary), --a (accent),
--h (drawn line). A mockup can therefore never show a different mark.
"""
IND, MAR, IVO, INK = "#262E5D", "#7D161A", "#F3F0E9", "#1C2033"
SCH = {
    "full": f"--p:{IND};--a:{MAR};--h:{IND}",
    "rev": "--p:#FFFFFF;--a:#D7A3A5;--h:#FFFFFF",
    "mono": f"--p:{IND};--a:{IND};--h:{IND}",
    "white": "--p:#FFFFFF;--a:#FFFFFF;--h:#FFFFFF",
    "black": "--p:#111;--a:#111;--h:#111",
    "ink": "--p:#2B3A8C;--a:#2B3A8C;--h:#2B3A8C",
    "deep": "--p:#1A2047;--a:#1A2047;--h:#1A2047",
}
DESC_AR = "مقاولات عامة واستشارات هندسية"
DESC_EN = "GENERAL CONTRACTING &amp; ENGINEERING CONSULTANCY"


def logo(d, kind, x, y, w, h, sch="full", al="c", sw=True, extra=""):
    cls = ' class="sw"' if sw else ""
    return (f'<use{cls} href="#L-{d}-{kind}-{al}" data-kind="{kind}" data-al="{al}" x="{x:.0f}" y="{y:.0f}" '
            f'width="{w:.0f}" height="{h:.0f}" style="{SCH[sch]}" {extra}/>')


def t(x, y, s, size=20, w=400, fill=INK, anchor="end", ls=0, op=1):
    a = {"end": "start", "start": "end", "middle": "middle"}[anchor]
    return (f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{w}" fill="{fill}" direction="rtl" '
            f'text-anchor="{a}" font-family="PlexAr" letter-spacing="{ls}" opacity="{op}">{s}</text>')


def te(x, y, s, size=12, w=500, fill=INK, anchor="start", ls=0, op=1):
    return (f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{w}" fill="{fill}" direction="ltr" '
            f'text-anchor="{anchor}" font-family="PlexAr" letter-spacing="{ls}" opacity="{op}">{s}</text>')


def field(xr, y, label, width, size=14, fill="#6B6E7E", line="#CFCAC0"):
    return t(xr, y, label, size, 500, fill) + f'<rect x="{xr - width}" y="{y + 12}" width="{width}" height="1.4" fill="{line}"/>'


def wrap(vb, body, label, uid):
    return f'<svg viewBox="{vb}" role="img" aria-label="{label}" class="mk" data-uid="{uid}">{body}</svg>'


def defs(uid):
    """Shared light, grain and shadow definitions (ids are scoped per mockup)."""
    return f'''<defs>
<filter id="sh{uid}" x="-20%" y="-20%" width="140%" height="160%"><feGaussianBlur in="SourceAlpha" stdDeviation="14"/><feOffset dy="18"/><feComponentTransfer><feFuncA type="linear" slope=".28"/></feComponentTransfer><feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="shs{uid}" x="-20%" y="-20%" width="140%" height="160%"><feGaussianBlur in="SourceAlpha" stdDeviation="5"/><feOffset dy="6"/><feComponentTransfer><feFuncA type="linear" slope=".22"/></feComponentTransfer><feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="gr{uid}" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="4" result="n"/><feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 .07 0"/><feComposite in2="SourceGraphic" operator="in"/><feBlend in="SourceGraphic" mode="multiply"/></filter>
<radialGradient id="vg{uid}" cx="50%" cy="38%" r="75%"><stop offset="0" stop-color="#fff" stop-opacity=".0"/><stop offset="1" stop-color="#000" stop-opacity=".18"/></radialGradient>
<linearGradient id="fl{uid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".10"/></linearGradient>
</defs>'''


def bg(uid, c1, c2, W=1200, H=800):
    return (f'<linearGradient id="bg{uid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient>'
            f'<rect width="{W}" height="{H}" fill="url(#bg{uid})"/>')


def vignette(uid, W=1200, H=800):
    return f'<rect width="{W}" height="{H}" fill="url(#vg{uid})" pointer-events="none"/>'


# ------------------------------------------------------------------ 1 helmet
def helmet(d, uid="hm", sw=True):
    def one(cx, base, body, dark, light, sch, k=1.0, gid="a"):
        W, H = 205 * k, 270 * k
        dome = (f'M{cx - W},{base} C{cx - W},{base - H * .86} {cx - W * .55},{base - H} {cx},{base - H} '
                f'C{cx + W * .55},{base - H} {cx + W},{base - H * .86} {cx + W},{base} Z')
        brim = (f'M{cx - W - 46 * k},{base - 6 * k} H{cx + W + 46 * k} Q{cx + W + 62 * k},{base + 22 * k} {cx + W + 20 * k},{base + 32 * k} '
                f'H{cx - W - 20 * k} Q{cx - W - 62 * k},{base + 22 * k} {cx - W - 46 * k},{base - 6 * k} Z')
        g = f'''<radialGradient id="dm{uid}{gid}" cx="38%" cy="22%" r="85%"><stop offset="0" stop-color="{light}"/><stop offset=".55" stop-color="{body}"/><stop offset="1" stop-color="{dark}"/></radialGradient>
<linearGradient id="br{uid}{gid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{light}"/><stop offset="1" stop-color="{dark}"/></linearGradient>'''
        s = g + f'<ellipse cx="{cx}" cy="{base + 52 * k}" rx="{W + 80 * k}" ry="{20 * k}" fill="#000" opacity=".22" filter="url(#shs{uid})"/>'
        s += f'<path d="{dome}" fill="url(#dm{uid}{gid})"/>'
        rib = f'M{cx},{base - H * .995} C{cx - W * .05},{base - H * .7} {cx - W * .06},{base - H * .3} {cx - W * .06},{base - 4}'
        s += f'<path d="M{cx - W * .16},{base - 4} C{cx - W * .18},{base - H * .6} {cx - W * .09},{base - H * .93} {cx},{base - H * .995} C{cx + W * .09},{base - H * .93} {cx + W * .18},{base - H * .6} {cx + W * .16},{base - 4} Z" fill="#fff" opacity=".10"/>'
        s += f'<path d="{brim}" fill="url(#br{uid}{gid})"/>'
        s += f'<path d="M{cx - W * .62},{base - H * .78} C{cx - W * .4},{base - H * .95} {cx - W * .12},{base - H * .99} {cx + W * .05},{base - H * .97}" fill="none" stroke="#fff" stroke-width="{10 * k}" stroke-linecap="round" opacity=".35"/>'
        lw, lh = 190 * k, 120 * k
        s += logo(d, "symbol", cx - lw / 2, base - 78 * k - lh, lw, lh, sch, "c", sw)
        return s
    b = defs(uid) + bg(uid, "#E9E5DD", "#D5CEC1")
    b += f'<rect y="560" width="1200" height="240" fill="#CBC3B4"/><rect y="560" width="1200" height="3" fill="#fff" opacity=".35"/>'
    b += one(355, 540, "#F4F2EC", "#C9C4B8", "#FFFFFF", "full", gid="w")
    b += one(860, 540, "#2A3264", "#141936", "#4B568F", "rev", gid="i")
    b += vignette(uid)
    return wrap("0 0 1200 800", b, "خوذة الموقع", uid)


# ------------------------------------------------------------------ 2 vest
def vest(d, uid="vs", sw=True):
    Y, Yd, SIL, SIL2 = "#DCE33A", "#B8BF22", "#BFC4CB", "#EEF1F4"

    def shape(cx, top, back):
        w = 240
        p = (f'M{cx - 72},{top} C{cx - 98},{top + 12} {cx - 140},{top + 12} {cx - 158},{top + 4} L{cx - 172},{top + 32} '
             f'C{cx - 180},{top + 126} {cx - 214},{top + 158} {cx - w},{top + 172} L{cx - w + 6},{top + 540} Q{cx - w + 9},{top + 562} {cx - w + 32},{top + 562} '
             f'L{cx + w - 32},{top + 562} Q{cx + w - 9},{top + 562} {cx + w - 6},{top + 540} L{cx + w},{top + 172} '
             f'C{cx + 214},{top + 158} {cx + 180},{top + 126} {cx + 172},{top + 32} L{cx + 158},{top + 4} C{cx + 140},{top + 12} {cx + 98},{top + 12} {cx + 72},{top} ')
        p += f'C{cx + 42},{top + 24} {cx - 42},{top + 24} {cx - 72},{top} Z' if back else f'L{cx + 10},{top + 262} L{cx - 10},{top + 262} Z'
        return p
    b = defs(uid) + bg(uid, "#EAE6DE", "#D8D1C5")
    b += f'<linearGradient id="mesh{uid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E2E84A"/><stop offset="1" stop-color="{Y}"/></linearGradient>'
    for i, (cx, back) in enumerate(((330, False), (870, True))):
        top = 80
        sp = shape(cx, top, back)
        b += f'<clipPath id="vc{uid}{i}"><path d="{sp}"/></clipPath>'
        b += f'<path d="{sp}" fill="#000" opacity=".25" filter="url(#sh{uid})" transform="translate(0,6)"/>'
        b += f'<path d="{sp}" fill="url(#mesh{uid})"/>'
        g = f'<g clip-path="url(#vc{uid}{i})">'
        g += f'<rect x="{cx - 260}" y="{top}" width="520" height="580" fill="url(#fl{uid})"/>'
        for yb in (top + 395, top + 472):
            g += f'<rect x="{cx - 260}" y="{yb}" width="520" height="46" fill="{SIL}"/><rect x="{cx - 260}" y="{yb + 20}" width="520" height="5" fill="{SIL2}"/>'
        for xb in (cx - 158, cx + 114):
            g += f'<rect x="{xb}" y="{top}" width="44" height="395" fill="{SIL}"/><rect x="{xb + 19}" y="{top}" width="5" height="395" fill="{SIL2}"/>'
        if not back:
            g += f'<rect x="{cx - 2}" y="{top + 262}" width="4" height="320" fill="{Yd}"/>'
        g += "</g>"
        b += g
        b += f'<path d="{sp}" fill="none" stroke="{Yd}" stroke-width="3"/>'
        if not back:
            px, py = cx + 22, top + 206
            b += f'<rect x="{px}" y="{py}" width="84" height="84" rx="8" fill="{IND}" filter="url(#shs{uid})"/>'
            b += f'<rect x="{px + 4}" y="{py + 4}" width="76" height="76" rx="6" fill="none" stroke="#fff" stroke-opacity=".35" stroke-dasharray="3 3"/>'
            b += logo(d, "symbol", px + 14, py + 14, 56, 56, "rev", "c", sw)
        else:
            px, py = cx - 112, top + 178
            b += f'<rect x="{px}" y="{py}" width="224" height="170" rx="10" fill="{IND}" filter="url(#shs{uid})"/>'
            b += f'<rect x="{px + 5}" y="{py + 5}" width="214" height="160" rx="7" fill="none" stroke="#fff" stroke-opacity=".3" stroke-dasharray="3 3"/>'
            b += logo(d, "stacked", px + 26, py + 22, 172, 126, "rev", "c", sw)
    b += vignette(uid)
    return wrap("0 0 1200 800", b, "فست العمل الميداني", uid)


# ------------------------------------------------------------------ 3 notebook & pen
def desk(d, uid="dk", sw=True):
    b = defs(uid) + bg(uid, "#C9C1B2", "#B7AE9E")
    b += f''
    # notebook
    b += f'<g filter="url(#sh{uid})" transform="rotate(-6 380 400)"><rect x="170" y="120" width="420" height="580" rx="14" fill="{IND}"/>'
    b += f'<rect x="170" y="120" width="420" height="580" rx="14" fill="url(#fl{uid})"/>'
    b += f'<rect x="520" y="120" width="16" height="580" fill="{MAR}"/>'
    b += logo(d, "symbol", 255, 300, 190, 190, "rev", "c", sw)
    b += f'<rect x="170" y="120" width="10" height="580" fill="#000" opacity=".18"/></g>'
    # pen
    b += f'<g filter="url(#shs{uid})" transform="rotate(14 820 420)"><rect x="800" y="120" width="40" height="560" rx="20" fill="{IND}"/>'
    b += f'<linearGradient id="pn{uid}" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity=".25"/><stop offset=".45" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".25"/></linearGradient>'
    b += f'<rect x="800" y="120" width="40" height="560" rx="20" fill="url(#pn{uid})"/>'
    b += f'<path d="M800,640 L820,720 L840,640 Z" fill="#C9CCD4"/><rect x="814" y="150" width="12" height="170" rx="6" fill="#C8CBD2"/>'
    b += logo(d, "symbol", 804, 420, 32, 32, "rev", "c", sw) + "</g>"
    # card on desk
    b += f'<g filter="url(#shs{uid})" transform="rotate(4 980 640)"><rect x="880" y="560" width="250" height="140" rx="5" fill="{IVO}"/>'
    b += logo(d, "horizontal", 920, 600, 170, 60, "full", "c", sw) + "</g>"
    b += vignette(uid)
    return wrap("0 0 1200 800", b, "دفتر وقلم", uid)


# ------------------------------------------------------------------ 4 letterhead
def letterhead(d, uid="lh", sw=True):
    b = defs(uid) + bg(uid, "#D9D3C7", "#C9C1B3")
    x, y, w, h = 330, 50, 540, 764
    b += f'<g filter="url(#sh{uid})"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#FFFFFF"/></g>'
    b += logo(d, "horizontal", x + w - 50 - 200, y + 46, 200, 92, "full", "r", sw)
    b += f'<rect x="{x + 50}" y="{y + 168}" width="{w - 100}" height="1.6" fill="{MAR}"/>'
    b += field(x + w - 50, y + 214, "التاريخ", 150, 13) + field(x + w - 50, y + 250, "المرجع", 150, 13) + field(x + w - 50, y + 286, "الموضوع", 260, 13)
    b += f'<rect x="{x + 50}" y="{y + h - 78}" width="{w - 100}" height="1" fill="#DCD8CF"/>'
    b += t(x + w - 50, y + h - 46, DESC_AR, 12.5, 500, IND)
    b += te(x + 50, y + h - 46, "ALRAYA", 11, 600, IND, "start", 3)
    b += f'<g filter="url(#shs{uid})" transform="rotate(-8 230 640)"><rect x="70" y="560" width="300" height="200" fill="#fff"/><rect x="70" y="560" width="300" height="200" fill="url(#fl{uid})"/>'
    b += logo(d, "symbol", 190, 610, 60, 60, "mono", "c", sw) + f'<rect x="120" y="700" width="200" height="1" fill="#DCD8CF"/></g>'
    b += vignette(uid)
    return wrap("0 0 1200 860", b, "الورق الرسمي", uid)


# ------------------------------------------------------------------ 5 drawings folder
def folder(d, uid="fd", sw=True):
    b = defs(uid) + bg(uid, "#CFC8BB", "#BDB4A4")
    sx, sy, sw_, sh = 470, 60, 690, 470
    b += f'<g filter="url(#sh{uid})" transform="rotate(2 800 300)"><rect x="{sx}" y="{sy}" width="{sw_}" height="{sh}" fill="#F8F9FB"/>'
    b += f'<rect x="{sx + 16}" y="{sy + 16}" width="{sw_ - 32}" height="{sh - 32}" fill="none" stroke="{IND}" stroke-width="1.4"/>'
    for i in range(1, 9):
        b += f'<line x1="{sx + 16 + i * 52}" y1="{sy + 16}" x2="{sx + 16 + i * 52}" y2="{sy + sh - 16}" stroke="#E1E4EC"/>'
        b += f'<line x1="{sx + 16}" y1="{sy + 16 + i * 52}" x2="{sx + 16 + 8 * 52}" y2="{sy + 16 + i * 52}" stroke="#E1E4EC"/>'
    tx = sx + 16 + 8 * 52; tw = sx + sw_ - 16 - tx
    b += f'<rect x="{tx}" y="{sy + 16}" width="{tw}" height="{sh - 32}" fill="#fff" stroke="{IND}" stroke-width="1.4"/>'
    b += logo(d, "horizontal", tx + 18, sy + 32, tw - 36, 86, "full", "c", sw)
    for i, r in enumerate(["المشروع", "عنوان اللوحة", "رقم اللوحة", "المقياس", "التاريخ", "التصميم", "التدقيق"]):
        yy = sy + 136 + i * 44
        b += f'<line x1="{tx}" y1="{yy}" x2="{tx + tw}" y2="{yy}" stroke="{IND}"/>' + t(tx + tw - 12, yy + 27, r, 13, 500, "#6B6E7E")
    b += "</g>"
    fx, fy, fw, fh = 60, 170, 540, 560
    b += f'<g filter="url(#sh{uid})"><path d="M{fx},{fy + 20} Q{fx},{fy} {fx + 20},{fy} H{fx + 190} L{fx + 222},{fy + 28} H{fx + fw - 18} Q{fx + fw},{fy + 28} {fx + fw},{fy + 46} V{fy + fh - 8} Q{fx + fw},{fy + fh} {fx + fw - 8},{fy + fh} H{fx + 8} Q{fx},{fy + fh} {fx},{fy + fh - 8} Z" fill="{IND}"/></g>'
    b += f'<rect x="{fx}" y="{fy + 28}" width="{fw}" height="{fh - 28}" fill="url(#fl{uid})"/>'
    b += logo(d, "stacked", fx + 120, fy + 100, fw - 240, 250, "rev", "c", sw)
    b += f'<rect x="{fx + 60}" y="{fy + 400}" width="{fw - 120}" height="1.5" fill="#D7A3A5"/>'
    b += t(fx + fw - 60, fy + 446, "ملف المخططات", 21, 600, "#fff")
    b += field(fx + fw - 60, fy + 488, "المشروع", fw - 240, 14, "#C7CADB", "#5A6190")
    b += vignette(uid)
    return wrap("0 0 1200 800", b, "ملف المخططات", uid)


# ------------------------------------------------------------------ 6 business card
def card(d, uid="cd", sw=True):
    b = defs(uid) + bg(uid, "#2A3160", "#1B2046")
    b += f'<g filter="url(#sh{uid})" transform="rotate(-7 420 330)"><rect x="160" y="180" width="520" height="300" rx="8" fill="{IVO}"/>'
    b += logo(d, "stacked", 300, 220, 240, 220, "full", "c", sw) + "</g>"
    b += f'<g filter="url(#sh{uid})" transform="rotate(5 800 520)"><rect x="560" y="400" width="520" height="300" rx="8" fill="{IVO}"/>'
    r = 1040
    b += t(r, 470, "الاسم الكامل", 26, 600, IND) + t(r, 502, "المسمى الوظيفي", 16, 400, "#5B5F72")
    b += f'<rect x="{r - 40}" y="522" width="40" height="3" fill="{MAR}"/>'
    b += t(r, 574, "الهاتف", 15, 400, "#5B5F72") + t(r, 602, "البريد الإلكتروني", 15, 400, "#5B5F72") + t(r, 630, "العنوان", 15, 400, "#5B5F72")
    b += logo(d, "symbol", 600, 590, 74, 74, "full", "c", sw) + "</g>"
    b += vignette(uid)
    return wrap("0 0 1200 800", b, "بطاقة عمل", uid)


# ------------------------------------------------------------------ 7 site board
def board(d, uid="bd", sw=True):
    b = defs(uid)
    b += f'<linearGradient id="sky{uid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#C9D3DF"/><stop offset="1" stop-color="#EDE6D8"/></linearGradient>'
    b += f'<rect width="1200" height="800" fill="url(#sky{uid})"/>'
    b += f'<path d="M0,560 L1200,540 L1200,800 L0,800 Z" fill="#CDBFA6"/><path d="M0,560 L1200,540 L1200,560 L0,580 Z" fill="#fff" opacity=".2"/>'
    for px in (310, 890):
        b += f'<rect x="{px - 13}" y="420" width="26" height="250" fill="#6E7380"/><rect x="{px - 13}" y="420" width="8" height="250" fill="#fff" opacity=".15"/>'
    x, y, w, h = 150, 70, 900, 420
    b += f'<g filter="url(#sh{uid})"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#fff"/></g>'
    b += f'<rect x="{x}" y="{y}" width="{w}" height="150" fill="{IND}"/>'
    b += logo(d, "horizontal", x + w - 40 - 330, y + 24, 330, 102, "rev", "r", sw)
    b += t(x + 40, y + 70, DESC_AR, 20, 500, "#fff", "start") + te(x + 40, y + 104, DESC_EN, 11.5, 500, "#C7CADB", "start", 1)
    for i, (r, lw) in enumerate([("المشروع", 560), ("صاحب العمل", 560), ("الجهة المشرفة", 560), ("مدة التنفيذ", 260)]):
        b += field(x + w - 40, y + 198 + i * 54, r, lw, 18, IND)
    b += f'<rect x="{x}" y="{y + h - 12}" width="{w}" height="12" fill="{MAR}"/>'
    b += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#fl{uid})"/>'
    return wrap("0 0 1200 800", b, "لوحة موقع مشروع", uid)


# ------------------------------------------------------------------ 8 car
def car(d, uid="cr", sw=True):
    b = defs(uid) + bg(uid, "#E3DED4", "#D3CBBD")
    b += f'<rect y="600" width="1200" height="200" fill="#BFB6A6"/><ellipse cx="600" cy="612" rx="500" ry="22" fill="#000" opacity=".25" filter="url(#shs{uid})"/>'
    body = ("M110,560 L110,452 Q110,420 142,414 L470,402 L540,300 Q558,278 588,278 L770,278 Q805,278 824,304 L896,402 "
            "L1052,412 Q1090,418 1094,452 L1098,560 Q1098,584 1074,584 L134,584 Q110,584 110,560 Z")
    b += f'<linearGradient id="cb{uid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".6" stop-color="#F1F1EE"/><stop offset="1" stop-color="#CFCFCB"/></linearGradient>'
    b += f'<path d="{body}" fill="url(#cb{uid})" stroke="#BEBEB8" stroke-width="2"/>'
    b += '<path d="M574,304 Q582,294 594,294 L704,294 L704,396 L494,402 Z" fill="#33394E"/><path d="M720,294 L770,294 Q796,294 810,314 L872,396 L720,396 Z" fill="#33394E"/>'
    b += '<path d="M580,300 L640,300 L600,392 L540,394 Z" fill="#fff" opacity=".12"/>'
    b += '<line x1="712" y1="296" x2="712" y2="570" stroke="#BDBDB7" stroke-width="2"/><line x1="470" y1="404" x2="470" y2="570" stroke="#BDBDB7" stroke-width="2"/>'
    b += f'<rect x="110" y="520" width="988" height="9" fill="{MAR}"/>'
    b += logo(d, "symbol", 744, 418, 110, 86, "full", "c", sw)
    b += logo(d, "horizontal", 160, 424, 280, 78, "full", "c", sw)
    for cx in (290, 935):
        b += f'<circle cx="{cx}" cy="584" r="68" fill="#1F2229"/><circle cx="{cx}" cy="584" r="34" fill="#A2A6AF"/><circle cx="{cx}" cy="584" r="12" fill="#6B6F78"/>'
    b += vignette(uid)
    return wrap("0 0 1200 800", b, "سيارة الشركة", uid)


# ------------------------------------------------------------------ 9 emboss
def emboss(d, uid="em", sw=True):
    b = defs(uid)
    b += f'''<filter id="eb{uid}" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur in="SourceAlpha" stdDeviation="2.4" result="b"/>
<feSpecularLighting in="b" surfaceScale="4" specularConstant=".9" specularExponent="18" lighting-color="#fff" result="s"><feDistantLight azimuth="235" elevation="38"/></feSpecularLighting>
<feComposite in="s" in2="SourceAlpha" operator="in" result="s2"/>
<feOffset in="SourceAlpha" dx="2.5" dy="3" result="o"/><feGaussianBlur in="o" stdDeviation="2" result="ob"/><feComposite in="SourceAlpha" in2="ob" operator="out" result="edge"/>
<feFlood flood-color="#000" flood-opacity=".4"/><feComposite in2="ob" operator="in" result="shd"/>
<feMerge><feMergeNode in="shd"/><feMergeNode in="SourceGraphic"/><feMergeNode in="s2"/></feMerge></filter>'''
    b += f'<linearGradient id="pp{uid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#F7F4EC"/><stop offset="1" stop-color="#E6E0D3"/></linearGradient></defs>'
    b += f'<rect width="1200" height="800" fill="url(#pp{uid})"/><rect width="1200" height="800" fill="#fff" filter="url(#gr{uid})"/>'
    b += f'<g filter="url(#eb{uid})">' + logo(d, "stacked", 380, 170, 440, 440, "deep", "c", sw).replace('style="', 'style="opacity:.13;') + "</g>"
    b += f'<g filter="url(#eb{uid})" opacity=".9">' + logo(d, "stacked", 380, 170, 440, 440, "white", "c", sw).replace('style="', 'style="opacity:.55;') + "</g>"
    b += t(600, 720, "ختم بارز على ورق قطني", 16, 500, "#8A8576", "middle")
    b += vignette(uid)
    return wrap("0 0 1200 800", b, "ختم بارز", uid)


# ------------------------------------------------------------------ 10 ink stamp
def stamp(d, uid="st", sw=True):
    b = defs(uid)
    b += f'''<filter id="ink{uid}" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency=".035" numOctaves="2" seed="7" result="t"/>
<feDisplacementMap in="SourceGraphic" in2="t" scale="5" result="dsp"/><feTurbulence type="fractalNoise" baseFrequency="1.4" numOctaves="1" seed="2" result="sp"/>
<feColorMatrix in="sp" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -1.3 1.75" result="mask"/><feComposite in="dsp" in2="mask" operator="in"/></filter></defs>'''
    b += f'<rect width="1200" height="800" fill="#F5F1E8"/><rect width="1200" height="800" fill="#fff" filter="url(#gr{uid})"/>'
    for i in range(14):
        b += f'<rect x="120" y="{150 + i * 36}" width="{520 if i % 4 else 380}" height="2" fill="#D8D3C6"/>'
    b += f'<g filter="url(#ink{uid})" opacity=".86" transform="rotate(-9 840 410)">'
    b += f'<circle cx="840" cy="410" r="228" fill="none" stroke="#2B3A8C" stroke-width="7"/><circle cx="840" cy="410" r="212" fill="none" stroke="#2B3A8C" stroke-width="2.5"/>'
    b += logo(d, "stamp", 650, 220, 380, 380, "ink", "c", sw) + "</g>"
    b += vignette(uid)
    return wrap("0 0 1200 800", b, "ختم حبر", uid)


# ------------------------------------------------------------------ 11 site gate
def gate(d, uid="gt", sw=True):
    b = defs(uid)
    b += f'<linearGradient id="sk{uid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#B8C6D6"/><stop offset="1" stop-color="#E7E1D4"/></linearGradient>'
    b += f'<rect width="1200" height="800" fill="url(#sk{uid})"/><rect y="600" width="1200" height="200" fill="#C7B99F"/>'
    # hoarding panels
    for x in range(0, 1200, 150):
        b += f'<rect x="{x}" y="250" width="148" height="350" fill="{IND}"/><rect x="{x}" y="250" width="3" height="350" fill="#000" opacity=".18"/>'
    b += f'<rect y="250" width="1200" height="350" fill="url(#fl{uid})"/>'
    # gate frame
    b += f'<rect x="420" y="200" width="360" height="400" fill="#1A2047"/><rect x="440" y="300" width="320" height="300" fill="#2E3668"/>'
    for i in range(9):
        b += f'<rect x="{452 + i * 36}" y="300" width="4" height="300" fill="#4A538A"/>'
    b += f'<rect x="420" y="200" width="360" height="100" fill="#fff"/>'
    b += logo(d, "horizontal", 450, 214, 300, 72, "full", "c", sw)
    b += logo(d, "symbol", 90, 340, 160, 160, "rev", "c", sw) + logo(d, "symbol", 950, 340, 160, 160, "rev", "c", sw)
    b += f'<rect x="0" y="592" width="1200" height="8" fill="{MAR}"/>'
    b += t(600, 680, "بوابة موقع العمل", 16, 500, "#5B5F72", "middle")
    return wrap("0 0 1200 800", b, "بوابة موقع العمل", uid)


# ------------------------------------------------------------------ 12 avatar
def avatar(d, uid="av", sw=True):
    b = defs(uid) + bg(uid, "#ECE8E0", "#E0DAD0")
    b += f'<g filter="url(#sh{uid})"><rect x="390" y="90" width="420" height="620" rx="46" fill="#fff"/></g>'
    b += f'<circle cx="600" cy="300" r="120" fill="{IND}"/>'
    b += logo(d, "symbol", 525, 225, 150, 150, "rev", "c", sw)
    b += t(600, 470, "الراية", 26, 700, INK, "middle") + te(600, 500, "@alraya", 15, 500, "#8A8DA0", "middle")
    b += f'<rect x="440" y="540" width="320" height="1" fill="#ECE9E2"/>'
    for i, (n, l) in enumerate((("—", "منشورات"), ("—", "متابعون"), ("—", "يتابع"))):
        b += t(500 + i * 100, 590, n, 18, 600, INK, "middle") + t(500 + i * 100, 616, l, 12, 400, "#8A8DA0", "middle")
    for i, cx in enumerate((210, 990)):
        b += f'<circle cx="{cx}" cy="400" r="{70 - i * 0}" fill="#fff" filter="url(#shs{uid})"/>'
        b += logo(d, "symbol", cx - 44, 356, 88, 88, "full", "c", sw)
    return wrap("0 0 1200 800", b, "صورة الحساب", uid)


# ------------------------------------------------------------------ 13 instagram
def insta(d, uid="ig", sw=True):
    b = defs(uid) + bg(uid, "#E6E1D8", "#D9D2C6")
    posts = []
    s = f'<rect width="340" height="340" fill="{IND}"/>' + logo(d, "symbol", 262, 28, 50, 50, "rev", "r", sw)
    s += t(312, 220, "عنوان المنشور", 30, 700, "#fff") + t(312, 252, "سطر قصير يوضح الفكرة.", 14, 400, "#C7CADB")
    s += f'<rect x="276" y="276" width="36" height="3" fill="#D7A3A5"/>'
    posts.append(s)
    s = f'<pattern id="hp{uid}" width="12" height="12" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="12" height="12" fill="#D9D6CF"/><rect width="2" height="12" fill="#CBC7BE"/></pattern>'
    s += f'<rect width="340" height="340" fill="#fff"/><rect width="340" height="252" fill="url(#hp{uid})"/>' + t(170, 132, "صورة من الموقع", 14, 500, "#8E8B84", "middle")
    s += logo(d, "horizontal", 18, 268, 130, 54, "full", "l", sw) + t(322, 290, "اسم المشروع", 14, 600, IND) + t(322, 312, "المرحلة", 11, 400, "#6B6E7E")
    posts.append(s)
    s = f'<rect width="340" height="340" fill="{IVO}"/>' + t(312, 62, "إعلان", 13, 600, MAR) + t(312, 108, "عنوان الإعلان", 28, 700, IND)
    s += t(312, 136, "تفاصيل مختصرة في سطر أو سطرين.", 13, 400, INK) + f'<rect x="28" y="214" width="284" height="1.4" fill="#CFCAC0"/>'
    s += logo(d, "horizontal", 28, 232, 284, 82, "full", "c", sw)
    posts.append(s)
    for i, p in enumerate(posts):
        x = 60 + i * 370
        b += f'<g filter="url(#sh{uid})" transform="translate({x},230)"><rect width="340" height="340" fill="#fff"/>{p}</g>'
    return wrap("0 0 1200 800", b, "منشورات إنستغرام", uid)


# ------------------------------------------------------------------ 14 office facade
def facade(d, uid="of", sw=True):
    b = defs(uid)
    b += f'<linearGradient id="wl{uid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E9E3D7"/><stop offset="1" stop-color="#D6CDBD"/></linearGradient>'
    b += f'<rect width="1200" height="800" fill="url(#wl{uid})"/>'
    for i in range(0, 1200, 120):
        b += f'<rect x="{i}" y="0" width="1" height="620" fill="#000" opacity=".06"/>'
    b += f'<rect y="620" width="1200" height="180" fill="#B9AF9E"/><rect y="620" width="1200" height="4" fill="#fff" opacity=".3"/>'
    # glazing
    b += f'<rect x="260" y="330" width="680" height="290" fill="#2E3A55"/>'
    for i in range(1, 4):
        b += f'<rect x="{260 + i * 170}" y="330" width="6" height="290" fill="#1C2236"/>'
    b += f'<path d="M260,330 L520,330 L360,620 L260,620 Z" fill="#fff" opacity=".07"/>'
    # fascia with letters (built-up letters cast a shadow)
    b += f'<rect x="220" y="150" width="760" height="150" fill="{IND}"/><rect x="220" y="296" width="760" height="6" fill="#000" opacity=".2"/>'
    b += f'<g filter="url(#shs{uid})">' + logo(d, "horizontal", 300, 172, 600, 106, "rev", "c", sw) + "</g>"
    # projecting blade sign
    b += f'<rect x="1040" y="160" width="8" height="200" fill="#6E7380"/><g filter="url(#shs{uid})"><rect x="1000" y="190" width="160" height="160" rx="8" fill="#fff"/></g>'
    b += logo(d, "symbol", 1025, 215, 110, 110, "full", "c", sw)
    b += vignette(uid)
    return wrap("0 0 1200 800", b, "واجهة المكتب", uid)


ALL = [
    ("helmet", "خوذة الموقع", helmet), ("vest", "فست العمل الميداني", vest), ("desk", "دفتر وقلم", desk),
    ("letter", "الورق الرسمي", letterhead), ("folder", "ملف المخططات", folder), ("card", "بطاقة العمل", card),
    ("board", "لوحة موقع المشروع", board), ("car", "سيارة الشركة", car), ("emboss", "ختم بارز", emboss),
    ("stamp", "ختم حبر", stamp), ("gate", "بوابة موقع العمل", gate), ("avatar", "صورة الحساب", avatar),
    ("insta", "منشورات إنستغرام", insta), ("facade", "واجهة المكتب", facade),
]
