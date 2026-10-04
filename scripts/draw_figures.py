"""Draw the explanatory figures in assets/figures/ as SVG.

    python3 scripts/draw_figures.py

Figures carry as little text as possible (generation names, TB, product names)
because the same file is shown on every language edition; the explanation is
in the page's translated <figcaption> and alt text.
"""

import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "figures")

INK, INK2, MUTED, FAINT = "#161320", "#39354a", "#6e6a7c", "#9a96a8"
LINE, SURF, SURF2 = "#dedce6", "#f7f6fa", "#f0eef5"
ACC, ACC_D, ACC_100, ACC_50 = "#5b27d6", "#4a1fb0", "#e6dcfb", "#f2ecfd"
GREEN, AMBER, RED, TEAL = "#1f9d6b", "#d98a1c", "#d4483b", "#2a8fb8"
FONT = "'Space Grotesk','Hanken Grotesk',system-ui,-apple-system,'Segoe UI',sans-serif"
MONO = "'Space Mono',ui-monospace,Menlo,monospace"


def svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img">'
            f'<title>{title}</title><rect width="{w}" height="{h}" rx="22" fill="{SURF}"/>{body}</svg>\n')


def text(x, y, s, size=18, fill=INK, weight=600, anchor="middle", font=FONT):
    return f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{s}</text>'


def cartridge(x, y, s=1.0, label="", color=ACC, tilt=0):
    """LTO cartridge seen from the front, 100x92 at s=1, with a label strip."""
    w, h = 100 * s, 92 * s
    g = f'<g transform="translate({x},{y}) rotate({tilt} {w/2} {h/2})">'
    g += f'<rect width="{w}" height="{h}" rx="{9*s}" fill="{color}"/>'
    g += f'<path d="M{w-20*s} 0 h{11*s} a{9*s} {9*s} 0 0 1 {9*s} {9*s} v{11*s} z" fill="#000" opacity=".18"/>'
    g += f'<rect x="{10*s}" y="{12*s}" width="{w-20*s}" height="{34*s}" rx="{4*s}" fill="#fff"/>'
    g += f'<rect x="{10*s}" y="{12*s}" width="{w-20*s}" height="{8*s}" rx="{3*s}" fill="{color}" opacity=".25"/>'
    if label:
        g += text(w / 2, 40 * s, label, size=15 * s, fill=INK, weight=700, font=MONO)
    for i in range(4):
        g += f'<rect x="{(22 + i * 15) * s}" y="{62*s}" width="{8*s}" height="{20*s}" rx="{2*s}" fill="#fff" opacity=".35"/>'
    return g + "</g>"


def hdd(x, y, s=1.0, color=INK2):
    w, h = 84 * s, 110 * s
    g = f'<g transform="translate({x},{y})"><rect width="{w}" height="{h}" rx="{10*s}" fill="{color}"/>'
    g += f'<circle cx="{w/2}" cy="{46*s}" r="{30*s}" fill="#fff" opacity=".9"/><circle cx="{w/2}" cy="{46*s}" r="{6*s}" fill="{color}"/>'
    g += f'<path d="M{w-14*s} {h-16*s} L{w/2+12*s} {54*s}" stroke="#fff" stroke-width="{5*s}" stroke-linecap="round"/>'
    g += f'<circle cx="{w-14*s}" cy="{h-16*s}" r="{6*s}" fill="#fff"/>'
    return g + "</g>"


def cloud(x, y, s=1.0, color=TEAL):
    return (f'<g transform="translate({x},{y}) scale({s})"><path d="M30 80 a28 28 0 0 1 4-55 a38 38 0 0 1 70-6 a30 30 0 0 1 36 30 a26 26 0 0 1-6 51 z" fill="{color}"/>'
            f'<path d="M30 80 h104" stroke="#fff" stroke-width="0" /></g>')


def arrow(x1, y1, x2, y2, color=FAINT, width=4, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}" stroke-linecap="round"{d}/>'
            + _head(x2, y2, x1, y1, color))


def _head(x, y, fx, fy, color):
    import math
    a = math.atan2(y - fy, x - fx)
    p = [(x, y), (x - 16 * math.cos(a - .45), y - 16 * math.sin(a - .45)), (x - 16 * math.cos(a + .45), y - 16 * math.sin(a + .45))]
    return f'<polygon points="{" ".join(f"{px:.1f},{py:.1f}" for px, py in p)}" fill="{color}"/>'


def shield(x, y, s=1.0, color=GREEN):
    return (f'<g transform="translate({x},{y}) scale({s})"><path d="M30 0 L58 10 V34 C58 52 46 64 30 70 C14 64 2 52 2 34 V10 Z" fill="{color}"/>'
            f'<path d="M18 35 L27 44 L43 26" fill="none" stroke="#fff" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/></g>')


def card(x, y, w, h, fill="#fff"):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="{fill}" stroke="{LINE}" stroke-width="2"/>'


def write(name, content):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(content)


# ---------------------------------------------------------------- figures

def fig_tiers():
    b = card(40, 60, 250, 300) + card(355, 60, 250, 300, ACC_50) + card(670, 60, 250, 300)
    b += hdd(123, 110, 1.0) + text(165, 300, "HDD", 22)
    for i, (dx, dy) in enumerate(((395, 140), (430, 120), (465, 100))):
        b += cartridge(dx, dy, .82, "LTO", ACC if i == 2 else ACC_D)
    b += f'<rect x="385" y="222" width="190" height="10" rx="5" fill="{INK2}"/>'
    b += shield(450, 245, .7) + text(480, 330, "LTO", 22)
    b += cloud(718, 140, 1.15)
    b += arrow(298, 210, 345, 210, ACC, 5) + arrow(613, 210, 660, 210, ACC, 5, "2 10")
    return svg(960, 420, b, "Disk for recent backups, LTO tape for the offline copy, cloud for offsite")


def fig_cartridges_100tb():
    rows = (("LTO-8", 12, 9, ACC_D), ("LTO-9", 18, 6, ACC), ("LTO-10", 30, 4, TEAL))
    b = text(480, 58, "100 TB", 30, INK, 700)
    for i, (gen, tb, n, col) in enumerate(rows):
        y = 100 + i * 110
        b += card(40, y - 8, 880, 96)
        b += text(70, y + 36, gen, 22, INK, 700, "start") + text(70, y + 64, f"{tb} TB", 16, MUTED, 500, "start")
        for k in range(n):
            b += cartridge(200 + k * 70, y + 8, .6, "", col)
        b += text(890, y + 52, f"× {n}", 30, col, 700, "end")
    return svg(960, 440, b, "Cartridges needed for 100 TB: 9 LTO-8, 6 LTO-9 or 4 LTO-10")


def fig_drive_forms():
    b = card(40, 50, 270, 330) + card(345, 50, 270, 330) + card(650, 50, 270, 330)
    # internal half-height drive in a 5.25-inch bay
    b += f'<rect x="80" y="140" width="190" height="80" rx="8" fill="{INK2}"/><rect x="95" y="160" width="110" height="14" rx="4" fill="#fff" opacity=".85"/>'
    b += f'<circle cx="245" cy="180" r="8" fill="{GREEN}"/><rect x="70" y="128" width="210" height="104" rx="10" fill="none" stroke="{FAINT}" stroke-width="3" stroke-dasharray="6 6"/>'
    b += text(175, 290, "HH", 24) + text(175, 322, "SAS", 16, MUTED, 500)
    # external desktop drive
    b += f'<rect x="395" y="110" width="170" height="130" rx="14" fill="{ACC}"/><rect x="410" y="135" width="105" height="14" rx="4" fill="#fff" opacity=".9"/>'
    b += f'<circle cx="540" cy="142" r="8" fill="{GREEN}"/><rect x="410" y="210" width="140" height="8" rx="4" fill="#fff" opacity=".3"/>'
    b += f'<path d="M565 220 C600 230 600 280 560 290" stroke="{INK2}" stroke-width="5" fill="none" stroke-linecap="round"/>'
    b += text(480, 290, "SAS · TB · USB", 18)
    # library module in a rack
    b += f'<rect x="700" y="90" width="170" height="200" rx="10" fill="{INK}"/>'
    for i in range(4):
        b += f'<rect x="712" y="{104 + i * 44}" width="146" height="34" rx="5" fill="{INK2}"/>'
        for k in range(5):
            b += f'<rect x="{720 + k * 27}" y="{110 + i * 44}" width="20" height="22" rx="3" fill="{ACC if (i + k) % 3 else ACC_100}"/>'
    b += text(785, 322, "FH · FC · SAS", 16, MUTED, 500)
    return svg(960, 420, b, "Internal half-height, external desktop and library LTO tape drives")


def fig_compat():
    gens = [f"LTO-{i}" for i in range(4, 11)]
    reads = {"LTO-5": (3, 5, 4), "LTO-6": (4, 6, 5), "LTO-7": (5, 7, 6), "LTO-8": (7, 8, 7), "LTO-9": (8, 9, 8), "LTO-10": (10, 10, 10)}
    drives = list(reads)
    x0, y0, cw, ch = 210, 110, 100, 52
    b = (f'<rect x="{x0+cw*2}" y="40" width="40" height="26" rx="6" fill="{ACC}"/>' + text(x0 + cw * 2 + 52, 60, "R/W", 20, INK2, 700, "start")
         + f'<rect x="{x0+cw*4}" y="40" width="40" height="26" rx="6" fill="#fff" stroke="{LINE}" stroke-width="2"/><rect x="{x0+cw*4}" y="40" width="20" height="26" rx="6" fill="{ACC}" opacity=".55"/>'
         + text(x0 + cw * 4 + 52, 60, "R", 20, INK2, 700, "start"))
    for j, g in enumerate(gens):
        b += text(x0 + j * cw + cw / 2, y0 - 14, g.replace("LTO-", "L"), 17, MUTED, 700, font=MONO)
    for i, d in enumerate(drives):
        y = y0 + i * ch
        b += text(x0 - 24, y + 33, d, 18, INK, 700, "end")
        lo, hi, wlo = reads[d]
        for j, g in enumerate(gens):
            n = int(g.split("-")[1])
            x = x0 + j * cw
            b += f'<rect x="{x+6}" y="{y+6}" width="{cw-12}" height="{ch-12}" rx="8" fill="#fff" stroke="{LINE}" stroke-width="2"/>'
            if lo <= n <= hi:
                if n >= wlo:
                    b += f'<rect x="{x+6}" y="{y+6}" width="{cw-12}" height="{ch-12}" rx="8" fill="{ACC}"/>'
                else:
                    b += f'<path d="M{x+14} {y+6} h{(cw-12)/2-8} v{ch-12} h-{(cw-12)/2-8} a8 8 0 0 1-8-8 v-{ch-28} a8 8 0 0 1 8-8z" fill="{ACC}" opacity=".55"/>'
    return svg(960, 450, b, "Which LTO drive reads and writes which cartridge generation")


def fig_finder():
    b = card(40, 40, 880, 360)
    b += cartridge(80, 70, .7, "", ACC) + text(240, 120, "Catalogic DPX", 22, INK, 700, "start")
    b += f'<g transform="translate(88,180)"><rect width="56" height="40" rx="6" fill="{TEAL}"/><rect x="10" y="10" width="36" height="20" rx="3" fill="#fff" opacity=".8"/><rect x="18" y="44" width="20" height="8" fill="{TEAL}"/></g>'
    b += text(240, 210, "Veeam", 22, INK, 700, "start")
    b += f'<g transform="translate(86,255)">' + "".join(f'<rect x="{k*20}" y="{30-k*12}" width="16" height="{20+k*12}" rx="3" fill="{INK2}"/>' for k in range(3)) + "</g>"
    b += text(240, 290, "Commvault", 22, INK, 700, "start")
    b += f'<g transform="translate(88,330)"><circle cx="18" cy="18" r="17" fill="{AMBER}"/><text x="18" y="25" font-family="{FONT}" font-size="20" font-weight="700" fill="#fff" text-anchor="middle">¢</text></g>'
    b += text(240, 360, "Nakivo", 22, INK, 700, "start")
    for y in (112, 202, 282, 352):
        b += arrow(170, y - 6, 220, y - 6, ACC, 4)
    b += f'<rect x="560" y="90" width="320" height="270" rx="16" fill="{ACC_50}"/>'
    for i, w in enumerate((240, 200, 260, 180)):
        b += f'<rect x="590" y="{120 + i * 58}" width="28" height="28" rx="6" fill="#fff" stroke="{ACC}" stroke-width="3"/>'
        b += f'<path d="M596 {134 + i*58} l6 7 l11 -13" stroke="{ACC}" stroke-width="4" fill="none" stroke-linecap="round"/>' if i < 3 else ""
        b += f'<rect x="632" y="{128 + i * 58}" width="{w}" height="12" rx="6" fill="{ACC_100}"/>'
    return svg(960, 440, b, "Four questions point to Catalogic DPX, Veeam, Commvault or Nakivo")


def fig_shelf():
    b = f'<rect x="60" y="200" width="840" height="18" rx="6" fill="{INK2}"/><rect x="80" y="218" width="20" height="50" fill="{INK2}"/><rect x="860" y="218" width="20" height="50" fill="{INK2}"/>'
    cols = (ACC_D, ACC, TEAL, ACC, INK2, ACC_D, ACC, TEAL, ACC)
    for i, c in enumerate(cols):
        b += cartridge(90 + i * 88, 96 + (i % 2) * 4, .78, f"L{5 + i % 6}", c, (-4 if i == 4 else 0))
    return svg(960, 300, b, "LTO cartridges on a shelf")


def fig_guide_map():
    tiles = (("tag", "LTO"), ("calc", "TB"), ("drive", "SAS"), ("soft", "LTFS"))
    b = ""
    for i, (kind, lbl) in enumerate(tiles):
        x = 50 + i * 225
        b += card(x, 120, 185, 200, ACC_50 if i % 2 == 0 else "#fff")
        cx = x + 92
        if kind == "tag":
            b += f'<path d="M{cx-40} 160 h50 l30 30 l-40 40 l-40 -40 z" fill="{ACC}"/><circle cx="{cx-22}" cy="178" r="7" fill="#fff"/>'
        elif kind == "calc":
            b += f'<rect x="{cx-35}" y="155" width="70" height="90" rx="10" fill="{INK2}"/><rect x="{cx-25}" y="165" width="50" height="20" rx="4" fill="#fff"/>'
            b += "".join(f'<rect x="{cx-25+(k%3)*18}" y="{195+(k//3)*18}" width="13" height="13" rx="3" fill="{ACC_100}"/>' for k in range(6))
        elif kind == "drive":
            b += f'<rect x="{cx-50}" y="175" width="100" height="55" rx="10" fill="{ACC}"/><rect x="{cx-38}" y="190" width="56" height="10" rx="3" fill="#fff"/><circle cx="{cx+32}" cy="195" r="6" fill="{GREEN}"/>'
        else:
            b += f'<rect x="{cx-45}" y="160" width="90" height="75" rx="10" fill="#fff" stroke="{INK2}" stroke-width="4"/><rect x="{cx-45}" y="160" width="90" height="16" rx="8" fill="{INK2}"/>'
            b += "".join(f'<rect x="{cx-33}" y="{186+k*14}" width="{60-k*12}" height="8" rx="4" fill="{ACC_100}"/>' for k in range(3))
        b += text(cx, 290, lbl, 20, INK, 700)
        if i < 3:
            b += arrow(x + 190, 220, x + 218, 220, ACC, 4)
    return svg(960, 420, b, "Prices, capacity, drives and software: the path through the LTO guides")


def fig_offsite():
    b = f'<circle cx="190" cy="220" r="150" fill="{RED}" opacity=".08"/><circle cx="190" cy="220" r="150" fill="none" stroke="{RED}" stroke-width="3" stroke-dasharray="8 10" opacity=".6"/>'
    b += f'<rect x="120" y="160" width="140" height="130" rx="8" fill="{INK2}"/><path d="M110 165 L190 110 L270 165 z" fill="{INK}"/>'
    for k in range(3):
        b += f'<rect x="{135 + k * 40}" y="190" width="28" height="36" rx="4" fill="{ACC_100}"/>'
    b += f'<path d="M244 98 C232 116 222 126 224 142 C226 158 238 166 250 166 C264 166 274 156 274 140 C274 126 266 118 262 108 C258 118 254 122 250 122 C252 112 250 104 244 98 Z" fill="{AMBER}"/><path d="M250 132 C244 142 242 148 244 154 C246 160 256 160 258 154 C260 148 256 140 250 132 Z" fill="#ffd27a"/>'
    # van
    b += f'<g transform="translate(400,215)"><rect width="130" height="62" rx="10" fill="{ACC}"/><path d="M130 18 h36 l22 24 v20 h-58 z" fill="{ACC_D}"/>'
    b += f'<circle cx="34" cy="66" r="14" fill="{INK}"/><circle cx="150" cy="66" r="14" fill="{INK}"/></g>'
    b += cartridge(430, 160, .45, "", ACC_D) + cartridge(470, 160, .45, "", ACC_D)
    # vault
    b += f'<rect x="700" y="140" width="190" height="170" rx="16" fill="{INK}"/><circle cx="795" cy="225" r="54" fill="{INK2}" stroke="{FAINT}" stroke-width="6"/>'
    b += "".join(f'<line x1="795" y1="225" x2="{795 + 40 * c}" y2="{225 + 40 * s}" stroke="{FAINT}" stroke-width="6" stroke-linecap="round"/>' for c, s in ((1, 0), (-.5, .87), (-.5, -.87)))
    b += shield(830, 110, .7)
    b += arrow(300, 250, 390, 250, ACC, 5) + arrow(600, 250, 690, 250, ACC, 5)
    b += f'<path d="M790 340 C 600 410, 330 410, 190 380" stroke="{FAINT}" stroke-width="4" fill="none" stroke-dasharray="4 10"/>' + _head(190, 380, 230, 392, FAINT)
    return svg(960, 440, b, "Tapes leave the building, travel to a vault and rotate back, outside the blast radius")


def fig_cost_bars():
    rows = (("tape", 1, "1×"), ("disk", 3, "3×"), ("cloud", 40, "40×+"))
    b = ""
    for i, (kind, v, lbl) in enumerate(rows):
        y = 70 + i * 115
        if kind == "tape":
            b += cartridge(60, y, .8, "LTO", ACC)
        elif kind == "disk":
            b += hdd(68, y - 10, .82)
        else:
            b += cloud(40, y - 4, .85)
        w = 26 if v == 1 else (78 if v == 3 else 640)
        col = ACC if kind == "tape" else (INK2 if kind == "disk" else TEAL)
        b += f'<rect x="210" y="{y+20}" width="{w}" height="40" rx="10" fill="{col}"/>'
        if v == 40:
            b += f'<path d="M560 {y+12} l-14 56 M580 {y+12} l-14 56" stroke="{SURF}" stroke-width="10"/>'
        b += text(210 + w + 20, y + 50, lbl, 26, col, 700, "start")
    return svg(960, 420, b, "Relative 10-year cost per terabyte: tape 1x, disk about 3x, cloud 40x or more")


def fig_air_gap():
    b = cloud(60, 90, 1.2, "#cfd8e3")
    b += f'<g transform="translate(120,130)"><circle cx="20" cy="20" r="18" fill="{RED}"/>' + "".join(
        f'<line x1="{20+12*c}" y1="{20+12*s}" x2="{20+28*c}" y2="{20+28*s}" stroke="{RED}" stroke-width="4" stroke-linecap="round"/>' for c, s in ((1, 0), (-1, 0), (.7, .7), (-.7, .7), (.7, -.7), (-.7, -.7))) + "</g>"
    b += f'<rect x="330" y="120" width="150" height="190" rx="12" fill="{INK2}"/>' + "".join(
        f'<rect x="345" y="{138+k*40}" width="120" height="28" rx="5" fill="{RED}" opacity="{.75 - k * .12}"/>' for k in range(4))
    b += f'<path d="M230 170 L300 190 L270 205 L325 225" stroke="{RED}" stroke-width="6" fill="none" stroke-linejoin="round" stroke-linecap="round"/>'
    b += f'<line x1="520" y1="215" x2="600" y2="215" stroke="{FAINT}" stroke-width="6" stroke-dasharray="10 12" stroke-linecap="round"/>'
    b += f'<line x1="545" y1="190" x2="575" y2="240" stroke="{RED}" stroke-width="6" stroke-linecap="round"/><line x1="575" y1="190" x2="545" y2="240" stroke="{RED}" stroke-width="6" stroke-linecap="round"/>'
    b += f'<rect x="640" y="280" width="270" height="14" rx="6" fill="{INK2}"/>'
    for k in range(3):
        b += cartridge(650 + k * 86, 196, .72, "WORM" if k == 1 else "LTO", ACC if k != 1 else ACC_D)
    b += shield(745, 92, .9)
    return svg(960, 400, b, "Ransomware reaches networked disks; a cartridge on a shelf is out of reach")


def fig_scorecard():
    crit = ("coin", "clock", "shield", "hourglass", "plug")
    scores = {"tape": (3, 2, 3, 3, 3), "disk": (2, 3, 1, 1, 1), "cloud": (1, 1, 2, 2, 2)}
    b = ""
    heads = (("tape", 380), ("disk", 580), ("cloud", 780))
    b += cartridge(338, 30, .8, "LTO", ACC) + hdd(546, 22, .75) + cloud(712, 40, .85)
    for i, c in enumerate(crit):
        y = 160 + i * 52
        b += f'<rect x="60" y="{y-6}" width="840" height="44" rx="10" fill="{"#fff" if i % 2 == 0 else SURF2}"/>'
        ix = 130
        if c == "coin":
            b += f'<circle cx="{ix}" cy="{y+16}" r="15" fill="{AMBER}"/><circle cx="{ix}" cy="{y+16}" r="8" fill="none" stroke="#fff" stroke-width="3"/>'
        elif c == "clock":
            b += f'<circle cx="{ix}" cy="{y+16}" r="15" fill="none" stroke="{INK2}" stroke-width="4"/><path d="M{ix} {y+7} v10 l7 5" stroke="{INK2}" stroke-width="4" fill="none" stroke-linecap="round"/>'
        elif c == "shield":
            b += shield(ix - 14, y - 2, .45)
        elif c == "hourglass":
            b += f'<path d="M{ix-12} {y} h24 l-10 16 l10 16 h-24 l10 -16 z" fill="{TEAL}"/>'
        else:
            b += f'<path d="M{ix-6} {y} v10 M{ix+6} {y} v10 M{ix-12} {y+10} h24 v6 a12 12 0 0 1-24 0z M{ix} {y+28} v6" stroke="{INK2}" stroke-width="4" fill="{INK2}" stroke-linecap="round"/>'
        for kind, cx in heads:
            sc = scores[kind][i]
            for k in range(3):
                b += f'<circle cx="{cx - 28 + k * 28}" cy="{y+16}" r="10" fill="{ACC if k < sc else LINE}"/>'
    return svg(960, 440, b, "Tape, disk and cloud rated on cost, restore speed, offline safety, lifespan and energy")


def fig_disks_vs_tape():
    b = card(40, 40, 420, 340) + card(500, 40, 420, 340, ACC_50)
    import random
    random.seed(4)
    for k in range(9):
        b += f'<g transform="rotate({random.randint(-25, 25)} {110 + (k % 3) * 110} {130 + (k // 3) * 80})">' + hdd(70 + (k % 3) * 110, 80 + (k // 3) * 80, .62, (INK2, "#55506a", "#6e6a7c")[k % 3]) + "</g>"
    b += f'<rect x="545" y="120" width="330" height="190" rx="18" fill="{INK2}"/><rect x="560" y="135" width="300" height="160" rx="12" fill="{INK}"/>'
    for k in range(5):
        b += cartridge(573 + k * 57, 168, .5, "", ACC if k % 2 else ACC_D, 0)
    b += shield(680, 60, .8)
    return svg(960, 420, b, "A pile of loose disks next to a neat case of LTO cartridges")


FIGURES = {
    "tape-disk-cloud-tiers.svg": fig_tiers,
    "lto-cartridges-per-100tb.svg": fig_cartridges_100tb,
    "lto-drive-form-factors.svg": fig_drive_forms,
    "lto-drive-compatibility.svg": fig_compat,
    "tape-backup-software-finder.svg": fig_finder,
    "lto-cartridge-shelf.svg": fig_shelf,
    "lto-guide-map.svg": fig_guide_map,
    "offsite-tape-rotation.svg": fig_offsite,
    "tape-disk-cloud-cost.svg": fig_cost_bars,
    "tape-air-gap.svg": fig_air_gap,
    "tape-disk-cloud-scorecard.svg": fig_scorecard,
    "loose-disks-vs-tape.svg": fig_disks_vs_tape,
}

if __name__ == "__main__":
    for name, fn in FIGURES.items():
        write(name, fn())
    print(f"{len(FIGURES)} figures in {os.path.relpath(OUT, ROOT)}")
