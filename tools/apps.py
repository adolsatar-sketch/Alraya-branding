"""Application scenes. Every logo is placed with <use> of the approved
symbol (lockup or icon), so an application can never drift from the logo.

Symbol ids: L-{dir}-{kind}-{align}; kind in lockup|icon, align in c|r|l.
Colours come from CSS custom properties --p (primary) and --a (accent).
"""

IND, MAR, IVO, INK, MUT = "#262E5D", "#7D161A", "#F3F0E9", "#1C2033", "#6B6E7E"
SCH = {
    "full": f"--p:{IND};--a:{MAR}",
    "rev": "--p:#FFFFFF;--a:#D7A3A5",
    "mono": f"--p:{IND};--a:{IND}",
    "white": "--p:#FFFFFF;--a:#FFFFFF",
    "black": "--p:#000;--a:#000",
}
DESC_AR = "مقاولات عامة واستشارات هندسية"
DESC_EN = "General Contracting &amp; Engineering Consultancy"


def logo(d, kind, x, y, w, h, scheme="full", align="c", sw=True):
    cls = ' class="sw"' if sw else ""
    return (f'<use{cls} href="#L-{d}-{kind}-{align}" data-kind="{kind}" data-al="{align}" '
            f'x="{x}" y="{y}" width="{w}" height="{h}" style="{SCH[scheme]}"/>')


def t(x, y, s, size=20, w=400, fill=INK, anchor="end", extra=""):
    """Arabic text. anchor: 'end' = right edge at x (default), 'start' = left
    edge at x, 'middle' = centred. Direction is set explicitly so every
    browser resolves the anchor the same way."""
    a = {"end": "start", "start": "end", "middle": "middle"}[anchor]
    return (f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{w}" fill="{fill}" '
            f'direction="rtl" text-anchor="{a}" font-family="PlexAr" {extra}>{s}</text>')


def te(x, y, s, size=14, w=500, fill=INK, anchor="start", ls=0):
    """Latin text."""
    return (f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{w}" fill="{fill}" '
            f'text-anchor="{anchor}" font-family="PlexAr" letter-spacing="{ls}" direction="ltr">{s}</text>')


def field(x_right, y, label, width, size=15, fill=MUT, line="#C9C5BC"):
    """A labelled blank line (no invented data)."""
    return (t(x_right, y, label, size, 500, fill) +
            f'<rect x="{x_right - width}" y="{y + 12}" width="{width}" height="1.5" fill="{line}"/>')


def svgwrap(vb, body, label):
    return f'<svg viewBox="{vb}" role="img" aria-label="{label}">{body}</svg>'


def shadow(cx, cy, rx, ry, op=0.16):
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#000" opacity="{op}"/>'


# ------------------------------------------------------------------ helmet
def helmet_one(d, cx, base, fill, edge, scheme, sw=True, k=1.0):
    W, H = 175 * k, 250 * k
    dome = (f'M{cx - W},{base} C{cx - W},{base - H * .82} {cx - W * .52},{base - H} {cx},{base - H} '
            f'C{cx + W * .52},{base - H} {cx + W},{base - H * .82} {cx + W},{base} Z')
    rib = (f'M{cx - W * .30},{base - 6 * k} C{cx - W * .33},{base - H * .7} {cx - W * .2},{base - H * .93} {cx},{base - H * .97}')
    rib2 = (f'M{cx + W * .30},{base - 6 * k} C{cx + W * .33},{base - H * .7} {cx + W * .2},{base - H * .93} {cx},{base - H * .97}')
    brim = (f'M{cx - W - 40 * k},{base - 4 * k} H{cx + W + 40 * k} '
            f'Q{cx + W + 52 * k},{base + 18 * k} {cx + W + 18 * k},{base + 26 * k} '
            f'H{cx - W - 18 * k} Q{cx - W - 52 * k},{base + 18 * k} {cx - W - 40 * k},{base - 4 * k} Z')
    lw, lh = 150 * k, 98 * k
    return (shadow(cx, base + 40 * k, W + 70 * k, 16 * k) +
            f'<path d="{dome}" fill="{fill}" stroke="{edge}" stroke-width="2"/>'
            f'<path d="{rib}" fill="none" stroke="{edge}" stroke-width="{5 * k}" opacity=".35" stroke-linecap="round"/>'
            f'<path d="{rib2}" fill="none" stroke="{edge}" stroke-width="{5 * k}" opacity=".35" stroke-linecap="round"/>'
            f'<path d="{brim}" fill="{fill}" stroke="{edge}" stroke-width="2"/>'
            + logo(d, "icon", cx - lw / 2, base - 72 * k - lh, lw, lh, scheme, "c", sw))


def helmets(d, sw=True):
    b = helmet_one(d, 330, 470, "#FBFAF6", "#CFCAC0", "full", sw)
    b += helmet_one(d, 870, 470, IND, "#1A2049", "rev", sw)
    return svgwrap("0 150 1200 400", b, "خوذتا موقع")


# ------------------------------------------------------------------ vest
def vest_shape(cx, top, back=False):
    w = 230
    neck = 0 if back else 1
    p = (f'M{cx - 70},{top} C{cx - 95},{top + 10} {cx - 135},{top + 10} {cx - 150},{top + 4} '
         f'L{cx - 165},{top + 30} C{cx - 172},{top + 120} {cx - 205},{top + 150} {cx - w},{top + 165} '
         f'L{cx - w + 5},{top + 520} Q{cx - w + 8},{top + 540} {cx - w + 30},{top + 540} '
         f'L{cx + w - 30},{top + 540} Q{cx + w - 8},{top + 540} {cx + w - 5},{top + 520} '
         f'L{cx + w},{top + 165} C{cx + 205},{top + 150} {cx + 172},{top + 120} {cx + 165},{top + 30} '
         f'L{cx + 150},{top + 4} C{cx + 135},{top + 10} {cx + 95},{top + 10} {cx + 70},{top} ')
    if back:
        p += f'C{cx + 40},{top + 22} {cx - 40},{top + 22} {cx - 70},{top} Z'
    else:
        p += f'L{cx + 10},{top + 250} L{cx - 10},{top + 250} Z'
    return p


def vest(d, sw=True):
    Y, Ye = "#D9E021", "#AEB51A"
    SIL, SIL2 = "#C4C8CE", "#E9ECEF"
    body = ""
    for i, (cx, back) in enumerate(((330, False), (870, True))):
        top = 70
        shape = vest_shape(cx, top, back)
        cid = f"vc{i}{d}"
        body += f'<clipPath id="{cid}"><path d="{shape}"/></clipPath>'
        body += shadow(cx, top + 560, 250, 14, .12)
        body += f'<path d="{shape}" fill="{Y}" stroke="{Ye}" stroke-width="2"/>'
        g = f'<g clip-path="url(#{cid})">'
        # two horizontal reflective bands
        for yb in (top + 380, top + 455):
            g += f'<rect x="{cx - 260}" y="{yb}" width="520" height="44" fill="{SIL}"/><rect x="{cx - 260}" y="{yb + 19}" width="520" height="6" fill="{SIL2}"/>'
        if not back:
            # vertical shoulder bands on the outer side of each panel
            for xb in (cx - 150, cx + 108):
                g += f'<rect x="{xb}" y="{top}" width="42" height="380" fill="{SIL}"/><rect x="{xb + 18}" y="{top}" width="6" height="380" fill="{SIL2}"/>'
            g += f'<rect x="{cx - 2}" y="{top + 250}" width="4" height="300" fill="{Ye}"/>'
        else:
            for xb in (cx - 150, cx + 108):
                g += f'<rect x="{xb}" y="{top}" width="42" height="380" fill="{SIL}"/><rect x="{xb + 18}" y="{top}" width="6" height="380" fill="{SIL2}"/>'
        g += "</g>"
        body += g
        if not back:
            # chest patch on the wearer's left, clear of every band
            px, py = cx + 22, top + 205
            body += f'<rect x="{px}" y="{py}" width="82" height="82" rx="6" fill="{IND}"/>'
            body += logo(d, "icon", px + 11, py + 11, 60, 60, "rev", "c", sw)
        else:
            px, py = cx - 102, top + 165
            body += f'<rect x="{px}" y="{py}" width="204" height="150" rx="8" fill="{IND}"/>'
            body += logo(d, "lockup", px + 18, py + 22, 168, 106, "rev", "c", sw)
    body += t(330 + 14, 700, "الأمام", 18, 500, MUT, "middle") + t(870, 700, "الخلف", 18, 500, MUT, "middle")
    return svgwrap("0 0 1200 720", body, "سترة العمل الميداني")


# ------------------------------------------------------------------ desk
def desk(d, sw=True):
    b = ""
    # notebook
    x, y, w, h = 150, 90, 380, 520
    b += f'<rect x="{x + 10}" y="{y + 14}" width="{w}" height="{h}" rx="10" fill="#000" opacity=".14"/>'
    b += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{IND}"/>'
    b += f'<rect x="{x + w - 52}" y="{y}" width="14" height="{h}" fill="{MAR}"/>'
    b += logo(d, "icon", x + 95, y + 170, 170, 150, "rev", "c", sw)
    # open letter pad
    x2, y2 = 610, 70
    b += f'<rect x="{x2 + 8}" y="{y2 + 12}" width="400" height="560" fill="#000" opacity=".10"/>'
    b += f'<rect x="{x2}" y="{y2}" width="400" height="560" fill="#FFFFFF"/>'
    b += logo(d, "lockup", x2 + 230, y2 + 34, 140, 70, "full", "r", sw)
    for i in range(12):
        b += f'<rect x="{x2 + 34}" y="{y2 + 150 + i * 32}" width="332" height="1" fill="#DCD8CF"/>'
    # pen
    px, py = 1060, 90
    b += f'<rect x="{px + 6}" y="{py + 8}" width="34" height="500" rx="17" fill="#000" opacity=".14"/>'
    b += f'<rect x="{px}" y="{py}" width="34" height="500" rx="17" fill="{IND}"/>'
    b += f'<path d="M{px},{py + 470} L{px + 17},{py + 540} L{px + 34},{py + 470} Z" fill="#C8CBD3"/>'
    b += f'<rect x="{px + 12}" y="{py + 20}" width="10" height="150" rx="5" fill="{MAR}"/>'
    b += logo(d, "icon", px + 3, py + 240, 28, 28, "rev", "c", sw)
    return svgwrap("0 0 1200 680", b, "دفتر وقلم")


# ------------------------------------------------------------------ card + letterhead
def card_front(d, x, y, w=520, h=290, sw=True):
    return (f'<rect x="{x + 8}" y="{y + 10}" width="{w}" height="{h}" rx="6" fill="#000" opacity=".12"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{IVO}"/>'
            + logo(d, "lockup", x + w * .22, y + h * .24, w * .56, h * .52, "full", "c", sw))


def card_back(d, x, y, w=520, h=290, sw=True):
    r = x + w - 40
    return (f'<rect x="{x + 8}" y="{y + 10}" width="{w}" height="{h}" rx="6" fill="#000" opacity=".12"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{IND}"/>'
            + t(r, y + 70, "الاسم الكامل", 26, 600, "#FFFFFF")
            + t(r, y + 102, "المسمى الوظيفي", 16, 400, "#C7CADB")
            + f'<rect x="{r - 40}" y="{y + 124}" width="40" height="3" fill="#D7A3A5"/>'
            + t(r, y + 176, "الهاتف", 15, 400, "#C7CADB")
            + t(r, y + 204, "البريد الإلكتروني", 15, 400, "#C7CADB")
            + t(r, y + 232, "العنوان", 15, 400, "#C7CADB")
            + logo(d, "icon", x + 36, y + h - 96, 60, 60, "rev", "c", sw))


def stationery(d, sw=True):
    b = card_front(d, 70, 70, sw=sw) + card_back(d, 70, 400, sw=sw)
    # letterhead A4
    x, y, w, h = 690, 40, 450, 636
    b += f'<rect x="{x + 8}" y="{y + 10}" width="{w}" height="{h}" fill="#000" opacity=".10"/>'
    b += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#FFFFFF"/>'
    b += logo(d, "lockup", x + w - 40 - 150, y + 34, 150, 76, "full", "r", sw)
    b += f'<rect x="{x + 40}" y="{y + 130}" width="{w - 80}" height="1.5" fill="{MAR}"/>'
    b += field(x + w - 40, y + 172, "التاريخ", 120, 13)
    b += field(x + w - 40, y + 204, "الموضوع", 200, 13)
    b += f'<rect x="{x + 40}" y="{y + h - 64}" width="{w - 80}" height="1" fill="#DCD8CF"/>'
    b += t(x + w - 40, y + h - 36, DESC_AR, 12, 500, IND)
    b += te(x + 40, y + h - 36, "ALRAYA", 11, 600, IND, "start", 3)
    return svgwrap("0 0 1200 720", b, "بطاقة عمل وورق رسمي")


# ------------------------------------------------------------------ drawings
def drawings(d, sw=True):
    b = ""
    # drawing sheet behind
    sx, sy, sw_, sh = 470, 50, 690, 480
    b += f'<rect x="{sx + 8}" y="{sy + 10}" width="{sw_}" height="{sh}" fill="#000" opacity=".10"/>'
    b += f'<rect x="{sx}" y="{sy}" width="{sw_}" height="{sh}" fill="#FDFDFB"/>'
    b += f'<rect x="{sx + 16}" y="{sy + 16}" width="{sw_ - 32}" height="{sh - 32}" fill="none" stroke="{IND}" stroke-width="1.5"/>'
    for i in range(1, 9):
        b += f'<line x1="{sx + 16 + i * 52}" y1="{sy + 16}" x2="{sx + 16 + i * 52}" y2="{sy + sh - 16}" stroke="#E4E6EE" stroke-width="1"/>'
    for i in range(1, 9):
        b += f'<line x1="{sx + 16}" y1="{sy + 16 + i * 52}" x2="{sx + 16 + 8 * 52}" y2="{sy + 16 + i * 52}" stroke="#E4E6EE" stroke-width="1"/>'
    # title block (right side of sheet)
    tx = sx + 16 + 8 * 52
    tw = sx + sw_ - 16 - tx
    b += f'<rect x="{tx}" y="{sy + 16}" width="{tw}" height="{sh - 32}" fill="#FFFFFF" stroke="{IND}" stroke-width="1.5"/>'
    b += logo(d, "lockup", tx + 20, sy + 34, tw - 40, 84, "full", "c", sw)
    rows = ["المشروع", "عنوان اللوحة", "رقم اللوحة", "المقياس", "التاريخ", "التصميم", "التدقيق"]
    for i, r in enumerate(rows):
        yy = sy + 140 + i * 44
        b += f'<line x1="{tx}" y1="{yy}" x2="{tx + tw}" y2="{yy}" stroke="{IND}" stroke-width="1"/>'
        b += t(tx + tw - 12, yy + 27, r, 13, 500, MUT)
    # folder in front
    fx, fy, fw, fh = 60, 150, 520, 520
    b += f'<rect x="{fx + 10}" y="{fy + 14}" width="{fw}" height="{fh}" rx="6" fill="#000" opacity=".16"/>'
    b += f'<path d="M{fx},{fy + 20} Q{fx},{fy} {fx + 20},{fy} H{fx + 180} L{fx + 210},{fy + 26} H{fx + fw - 20} Q{fx + fw},{fy + 26} {fx + fw},{fy + 46} V{fy + fh - 6} Q{fx + fw},{fy + fh} {fx + fw - 6},{fy + fh} H{fx + 6} Q{fx},{fy + fh} {fx},{fy + fh - 6} Z" fill="{IND}"/>'
    b += logo(d, "lockup", fx + 70, fy + 120, fw - 140, 170, "rev", "c", sw)
    b += f'<rect x="{fx + 60}" y="{fy + 380}" width="{fw - 120}" height="1.5" fill="#D7A3A5"/>'
    b += t(fx + fw - 60, fy + 420, "ملف المخططات", 20, 600, "#FFFFFF")
    b += field(fx + fw - 60, fy + 462, "المشروع", fw - 230, 14, "#C7CADB", "#5A6190")
    return svgwrap("0 0 1200 720", b, "ملف مخططات")


# ------------------------------------------------------------------ site board
def board(d, sw=True):
    b = f'<rect x="0" y="560" width="1200" height="160" fill="#CFC6B4"/>'
    for px in (300, 900):
        b += f'<rect x="{px - 12}" y="380" width="24" height="230" fill="#7E838F"/>'
    x, y, w, h = 150, 60, 900, 400
    b += f'<rect x="{x + 10}" y="{y + 12}" width="{w}" height="{h}" fill="#000" opacity=".14"/>'
    b += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#FFFFFF"/>'
    b += f'<rect x="{x}" y="{y}" width="{w}" height="140" fill="{IND}"/>'
    b += logo(d, "lockup", x + w - 40 - 330, y + 22, 330, 96, "rev", "r", sw)
    b += t(x + 40 + 330, y + 64, DESC_AR, 20, 500, "#FFFFFF", "end")
    b += te(x + 40, y + 98, DESC_EN, 13, 500, "#C7CADB", "start", 1)
    rows = [("المشروع", 560), ("صاحب العمل", 560), ("الجهة المشرفة", 560), ("مدة التنفيذ", 260)]
    for i, (r, lw) in enumerate(rows):
        b += field(x + w - 40, y + 186 + i * 52, r, lw + 0, 18, IND)
    b += f'<rect x="{x}" y="{y + h - 12}" width="{w}" height="12" fill="{MAR}"/>'
    return svgwrap("0 20 1200 620", b, "لوحة موقع مشروع")


# ------------------------------------------------------------------ car
def car(d, sw=True):
    b = f'<rect x="0" y="600" width="1200" height="120" fill="#D4CEC2"/>' + shadow(600, 600, 470, 18, .2)
    body = ("M120,520 L120,430 Q120,405 145,400 L500,392 L560,300 Q575,282 600,282 L760,282 Q790,282 806,305 "
            "L866,392 L1040,402 Q1075,406 1080,440 L1084,520 Q1084,540 1064,540 L140,540 Q120,540 120,520 Z")
    b += f'<path d="{body}" fill="#FAFAF8" stroke="#C9C9C4" stroke-width="2"/>'
    # windows
    b += '<path d="M585,306 Q592,298 602,298 L700,298 L700,388 L528,392 Z" fill="#3B4258"/>'
    b += '<path d="M716,298 L760,298 Q782,298 794,316 L846,392 L716,390 Z" fill="#3B4258"/>'
    b += '<line x1="708" y1="300" x2="708" y2="530" stroke="#C9C9C4" stroke-width="2"/>'
    b += '<line x1="500" y1="400" x2="500" y2="530" stroke="#C9C9C4" stroke-width="2"/>'
    # bed rail stripe
    b += f'<rect x="120" y="500" width="964" height="8" fill="{MAR}"/>'
    # door logo (icon) and bed lockup
    b += logo(d, "icon", 735, 410, 100, 76, "full", "c", sw)
    b += logo(d, "lockup", 165, 410, 300, 62, "full", "c", sw)
    for cx in (290, 930):
        b += f'<circle cx="{cx}" cy="540" r="62" fill="#22252E"/><circle cx="{cx}" cy="540" r="30" fill="#9A9EA8"/>'
    return svgwrap("0 230 1200 450", b, "سيارة الشركة")


# ------------------------------------------------------------------ instagram
def insta(d, sw=True):
    out = []
    # 1: statement
    s = f'<rect width="600" height="600" fill="{IND}"/>'
    s += logo(d, "icon", 470, 50, 80, 80, "rev", "r", sw)
    s += t(550, 380, "عنوان المنشور", 54, 700, "#FFFFFF")
    s += t(550, 430, "سطر قصير يوضح الفكرة.", 24, 400, "#C7CADB")
    s += f'<rect x="490" y="470" width="60" height="4" fill="#D7A3A5"/>'
    out.append(svgwrap("0 0 600 600", s, "قالب منشور نصي"))
    # 2: site photo frame
    s = f'<rect width="600" height="600" fill="#FFFFFF"/>'
    s += '<defs><pattern id="hp' + d + '" width="14" height="14" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="14" height="14" fill="#E3E1DB"/><rect width="2" height="14" fill="#D3D0C8"/></pattern></defs>'
    s += f'<rect x="0" y="0" width="600" height="460" fill="url(#hp{d})"/>'
    s += t(300, 240, "مكان صورة من الموقع", 22, 500, "#8E8B84", "middle")
    s += logo(d, "lockup", 40, 488, 200, 80, "full", "l", sw)
    s += t(560, 520, "اسم المشروع", 22, 600, IND) + t(560, 552, "المرحلة", 16, 400, MUT)
    out.append(svgwrap("0 0 600 600", s, "قالب صورة من الموقع"))
    # 3: announcement
    s = f'<rect width="600" height="600" fill="{IVO}"/>'
    s += t(550, 110, "إعلان", 22, 600, MAR)
    s += t(550, 190, "عنوان الإعلان", 50, 700, IND)
    s += t(550, 236, "تفاصيل مختصرة في سطر أو سطرين.", 22, 400, INK)
    s += f'<rect x="50" y="400" width="500" height="1.5" fill="#CFCAC0"/>'
    s += logo(d, "lockup", 50, 430, 500, 120, "full", "c", sw)
    out.append(svgwrap("0 0 600 600", s, "قالب إعلان"))
    return out


# ------------------------------------------------------------------ avatar
def avatar(d, sw=True):
    s = f'<rect width="600" height="600" fill="#E9E5DC"/>'
    s += f'<circle cx="300" cy="300" r="230" fill="#FFFFFF"/>'
    s += logo(d, "icon", 160, 160, 280, 280, "full", "c", sw)
    return svgwrap("0 0 600 600", s, "صورة الحساب")


# ------------------------------------------------------------------ per-direction minis
def helmet_one_svg(d):
    b = f'<rect width="600" height="600" fill="#E8E3D8"/>' + helmet_one(d, 300, 430, "#FBFAF6", "#CFCAC0", "full", False, 1.15)
    return svgwrap("0 0 600 600", b, "خوذة")


def card_svg(d):
    b = f'<rect width="600" height="600" fill="#DDD7CB"/>'
    b += card_back(d, 80, 300, 480, 250, sw=False)
    b += card_front(d, 40, 30, 480, 250, sw=False)
    return svgwrap("0 0 600 600", b, "بطاقة العمل")
