from draw_figures import *
import random


# ------------------------------------------------------------ helpers
def drv(x, y, w=130, h=58, col=INK2, led=GREEN):
    return (f'<g transform="translate({x},{y})"><rect width="{w}" height="{h}" rx="9" fill="{col}"/>'
            f'<rect x="{w*.1}" y="{h*.36}" width="{w*.55}" height="{h*.2}" rx="4" fill="#fff" opacity=".88"/>'
            f'<circle cx="{w*.82}" cy="{h*.46}" r="{h*.09}" fill="{led}"/></g>')


def mini(x, y, w=40, h=36, col=ACC):
    return (f'<g transform="translate({x},{y})"><rect width="{w}" height="{h}" rx="{w*.1}" fill="{col}"/>'
            f'<rect x="{w*.12}" y="{h*.14}" width="{w*.76}" height="{h*.36}" rx="{w*.05}" fill="#fff"/></g>')


def barcode(x, y, w, h, seed=3, col=INK):
    r = random.Random(seed)
    b, cx = "", x
    while cx < x + w - 4:
        bw = r.choice((2, 2, 3, 4, 5))
        if r.random() < .6:
            b += f'<rect x="{cx}" y="{y}" width="{bw}" height="{h}" fill="{col}"/>'
        cx += bw + r.choice((2, 3))
    return b


def check(cx, cy, r=18, col=GREEN):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{col}"/><path d="M{cx-r*.45} {cy+r*.02} l{r*.33} {r*.35} l{r*.62} {-r*.7}" '
            f'fill="none" stroke="#fff" stroke-width="{r*.24}" stroke-linecap="round" stroke-linejoin="round"/>')


def cross(cx, cy, r=18, col=RED):
    d = r * .4
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{col}"/><path d="M{cx-d} {cy-d} L{cx+d} {cy+d} M{cx+d} {cy-d} L{cx-d} {cy+d}" '
            f'stroke="#fff" stroke-width="{r*.24}" stroke-linecap="round"/>')


def chip(cx, cy, s, w=None, fill="#fff", col=INK, size=18, stroke=LINE):
    w = w or len(s) * size * .56 + 30
    return (f'<rect x="{cx-w/2}" y="{cy-19}" width="{w}" height="38" rx="19" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
            + text(cx, cy + size * .34, s, size, col, 700))


def server(x, y, w=70, col=INK2):
    b = f'<g transform="translate({x},{y})">'
    for i in range(2):
        b += f'<rect y="{i*30}" width="{w}" height="26" rx="6" fill="{col}"/><circle cx="{w-12}" cy="{13+i*30}" r="4" fill="{GREEN}"/><rect x="10" y="{10+i*30}" width="{w*.4}" height="6" rx="3" fill="#fff" opacity=".8"/>'
    return b + "</g>"


def dbase(x, y, w=64, col=TEAL):
    b = f'<g transform="translate({x},{y})"><path d="M0 12 v40 a{w/2} 12 0 0 0 {w} 0 v-40" fill="{col}"/>'
    b += f'<ellipse cx="{w/2}" cy="12" rx="{w/2}" ry="12" fill="{col}"/><ellipse cx="{w/2}" cy="12" rx="{w/2}" ry="12" fill="#fff" opacity=".3"/>'
    b += f'<path d="M0 30 a{w/2} 12 0 0 0 {w} 0" fill="none" stroke="#fff" stroke-width="3" opacity=".7"/></g>'
    return b


def magnifier(x, y, s=1.0, col=INK2):
    return (f'<g transform="translate({x},{y}) scale({s})"><circle cx="30" cy="30" r="24" fill="#fff" fill-opacity=".55" stroke="{col}" stroke-width="7"/>'
            f'<path d="M48 48 L72 72" stroke="{col}" stroke-width="10" stroke-linecap="round"/></g>')


def drop(cx, cy, s=1.0, col=TEAL):
    return f'<path transform="translate({cx},{cy}) scale({s})" d="M0 -22 C14 -4 18 2 18 10 a18 18 0 0 1 -36 0 C-18 2 -14 -4 0 -22 z" fill="{col}"/>'


def snow(cx, cy, r=18, col=TEAL):
    import math
    b = ""
    for k in range(3):
        a = math.pi * k / 3
        b += f'<line x1="{cx-r*math.cos(a):.1f}" y1="{cy-r*math.sin(a):.1f}" x2="{cx+r*math.cos(a):.1f}" y2="{cy+r*math.sin(a):.1f}" stroke="{col}" stroke-width="4" stroke-linecap="round"/>'
    return b


def bolt(cx, cy, s=1.0, col=AMBER):
    return f'<path transform="translate({cx},{cy}) scale({s})" d="M6 -22 L-12 4 H-1 L-6 22 L12 -4 H1 z" fill="{col}"/>'


def plug_off(cx, cy, s=1.0):
    b = (f'<g transform="translate({cx},{cy}) scale({s})"><path d="M-8 -22 v12 M8 -22 v12 M-14 -10 h28 v8 a14 14 0 0 1 -28 0 z M0 6 v16" '
         f'stroke="{MUTED}" stroke-width="4" fill="{MUTED}" stroke-linecap="round"/>'
         f'<path d="M-24 22 L24 -24" stroke="{RED}" stroke-width="6" stroke-linecap="round"/></g>')
    return b


def calendar(x, y, w=44, col=ACC):
    return (f'<g transform="translate({x},{y})"><rect width="{w}" height="{w*.9}" rx="7" fill="#fff" stroke="{col}" stroke-width="4"/>'
            f'<rect width="{w}" height="{w*.28}" rx="6" fill="{col}"/><rect x="{w*.2}" y="{w*.46}" width="{w*.18}" height="{w*.14}" fill="{col}" opacity=".5"/>'
            f'<rect x="{w*.5}" y="{w*.46}" width="{w*.18}" height="{w*.14}" fill="{col}" opacity=".5"/><rect x="{w*.2}" y="{w*.68}" width="{w*.18}" height="{w*.1}" fill="{col}" opacity=".5"/></g>')


def folder(x, y, w=70, col=TEAL):
    return (f'<g transform="translate({x},{y})"><path d="M0 8 a6 6 0 0 1 6 -6 h20 l8 10 h{w-34} a6 6 0 0 1 6 6 v{w*.55} a6 6 0 0 1 -6 6 h{-(w-12)} a6 6 0 0 1 -6 -6 z" fill="{col}"/></g>')


def dash(x1, y1, x2, y2, col=FAINT):
    return arrow(x1, y1, x2, y2, col, 4, "2 9")


# ------------------------------------------------------------ 1 library
def fig_library():
    b = card(40, 40, 300, 340) + card(500, 40, 420, 340, ACC_50)
    empty = {(0, 2), (3, 0), (2, 1)}
    hl = (1, 2)
    for r in range(4):
        for c in range(3):
            x, y = 62 + c * 90, 62 + r * 78
            if (r, c) in empty:
                b += f'<rect x="{x}" y="{y}" width="70" height="62" rx="9" fill="none" stroke="{LINE}" stroke-width="3" stroke-dasharray="6 6"/>'
            else:
                col = ACC if (r + c) % 2 else ACC_D
                b += f'<rect x="{x-5}" y="{y-5}" width="80" height="72" rx="10" fill="{SURF2}"/>' + cartridge(x, y, .7, "", col)
    sx, sy = 62 + hl[1] * 90, 62 + hl[0] * 78
    b += f'<rect x="{sx-6}" y="{sy-6}" width="82" height="74" rx="11" fill="none" stroke="{GREEN}" stroke-width="4"/>'
    # rail + picker
    b += f'<rect x="395" y="60" width="14" height="300" rx="7" fill="{LINE}"/>'
    b += f'<rect x="368" y="170" width="68" height="56" rx="12" fill="{INK2}"/><rect x="380" y="182" width="44" height="14" rx="4" fill="#fff" opacity=".85"/><circle cx="402" cy="212" r="5" fill="{GREEN}"/>'
    b += arrow(sx + 74, sy + 30, 364, 196, GREEN, 5)
    # drives
    b += drv(560, 100, 270, 70, INK2) + drv(560, 250, 270, 70, INK2)
    b += arrow(440, 196, 548, 150, GREEN, 5) + dash(440, 206, 548, 270)
    b += f'<rect x="850" y="104" width="22" height="62" rx="6" fill="{ACC}"/>' * 0
    return svg(960, 420, b, "Tape library with a magazine of cartridges, a robot picker and two drives")


# ------------------------------------------------------------ 2 brands
def fig_brands():
    b = ""
    for i, n in enumerate(("Fujifilm", "Sony")):
        y = 110 + i * 130
        b += card(40, y, 210, 90) + text(145, y + 55, n, 28, INK, 700)
        b += arrow(256, y + 45, 392, 200 + i * 20 if False else 205 + i * 30, ACC, 5)
    b += card(395, 120, 170, 190, ACC_50) + cartridge(430, 160, 1.0, "", ACC)
    b += text(480, 300, "LTO", 22, ACC_D, 700) if False else ""
    ys = (65, 140, 215, 290)
    for i, n in enumerate(("HPE", "IBM", "Quantum", "Dell")):
        y = ys[i]
        b += arrow(572, 215, 640, y + 36, ACC, 4)
        b += card(648, y, 270, 70)
        b += cartridge(668, y + 11, .5, "", ACC)
        b += f'<rect x="676" y="{y+34}" width="34" height="8" rx="3" fill="{ACC_100}"/>' * 0
        b += f'<rect x="740" y="{y+16}" width="150" height="38" rx="8" fill="{SURF2}"/>' + text(815, y + 43, n, 22, INK, 700)
    return svg(960, 420, b, "Fujifilm and Sony make the tape; HPE, IBM, Quantum and Dell put their labels on the same cartridge")


# ------------------------------------------------------------ 3 lifespan
def fig_lifespan():
    b = card(40, 30, 880, 360)
    x0, x1 = 160, 880
    # top: shelf conditions
    b += f'<rect x="70" y="150" width="70" height="10" rx="4" fill="{INK2}"/>' + cartridge(78, 76, .62, "", ACC)
    b += snow(100, 62, 14) + drop(128, 62, .6)
    b += text(620, 70, "16–25 °C", 20, MUTED, 600) + text(780, 70, "20–50 %", 20, MUTED, 600)
    # long bar
    b += f'<rect x="{x0}" y="112" width="{x1-x0}" height="40" rx="20" fill="{ACC}"/>'
    for k in range(1, 6):
        xx = x0 + (x1 - x0) * k / 6
        b += f'<line x1="{xx}" y1="124" x2="{xx}" y2="140" stroke="#fff" stroke-width="3" opacity=".6"/>'
    b += text(520, 141, "30", 30, "#fff", 700) + calendar(822, 119, 28, "#fff") * 0
    b += f'<path d="M{x0} 112 v40" stroke="{ACC_D}" stroke-width="0"/>'
    # drives expire earlier
    rows = (("L5", .30), ("L6", .43), ("L7", .56))
    for i, (g, f) in enumerate(rows):
        y = 205 + i * 56
        b += drv(70, y - 14, 74, 36, INK2)
        xe = x0 + (x1 - x0) * f
        b += f'<rect x="{x0}" y="{y-8}" width="{xe-x0}" height="24" rx="12" fill="{MUTED}" opacity=".55"/>'
        b += cross(xe + 22, y + 4, 15) + text(xe + 60, y + 11, g, 20, MUTED, 700, "start", MONO)
    return svg(960, 420, b, "A 30 year rated cartridge outlasts the drives that can read it")


# ------------------------------------------------------------ 4 migration
def fig_migration():
    b = '<defs><g id="a"><rect width="26" height="22" rx="3" fill="%s"/><rect x="3" y="3" width="20" height="8" rx="2" fill="#fff"/></g>' % MUTED
    b += '<g id="c"><rect width="48" height="42" rx="6" fill="%s"/><rect x="5" y="5" width="38" height="16" rx="3" fill="#fff"/></g></defs>' % ACC
    b += text(480, 56, "500 TB", 34, INK, 700)
    b += card(40, 84, 380, 300) + card(540, 84, 380, 300, ACC_50)
    for i in range(84):
        b += f'<use href="#a" x="{62+(i%12)*28.5:.1f}" y="{138+(i//12)*30}"/>'
    for i in range(28):
        b += f'<use href="#c" x="{572+(i%7)*47}" y="{138+(i//7)*52}"/>'
    b += text(230, 112, "LTO-7", 22, MUTED, 700) + text(230, 370, "84 × 6 TB", 20, MUTED, 600)
    b += text(730, 112, "LTO-9", 22, ACC_D, 700) + text(730, 370, "28 × 18 TB", 20, ACC_D, 600)
    b += drv(440, 200, 80, 44, ACC) + arrow(424, 262, 534, 262, ACC, 5)
    return svg(960, 420, b, "500 TB on 84 LTO-7 cartridges of 6 TB moves to 28 LTO-9 cartridges of 18 TB")


# ------------------------------------------------------------ 5 cleaning + labels
def fig_cleaning():
    b = card(40, 50, 270, 320) + card(345, 50, 270, 320, ACC_50) + card(650, 50, 270, 320)
    # cleaning cartridge with brush
    b += cartridge(95, 110, 1.6, "CLN", TEAL)
    b += text(175, 340, "× 50", 26, TEAL, 700)
    # label
    b += f'<rect x="372" y="105" width="216" height="140" rx="12" fill="#fff" stroke="{INK2}" stroke-width="3"/>'
    b += barcode(390, 120, 180, 56, 7)
    b += text(455, 215, "000123", 26, INK, 700, "middle", MONO)
    b += f'<rect x="518" y="190" width="54" height="34" rx="8" fill="{ACC}"/>' + text(545, 215, "L9", 24, "#fff", 700, "middle", MONO)
    b += f'<path d="M545 252 v22 M545 274 l-8 -10 M545 274 l8 -10" stroke="{ACC}" stroke-width="4" fill="none" stroke-linecap="round"/>' * 0
    b += cartridge(460, 275, .55, "", ACC) * 0
    b += text(480, 340, "L9 = LTO-9", 22, ACC_D, 700)
    # case
    b += f'<rect x="690" y="110" width="190" height="150" rx="14" fill="{SURF2}" stroke="{INK2}" stroke-width="5"/>'
    b += f'<rect x="690" y="110" width="26" height="150" rx="10" fill="{INK2}"/>'
    b += cartridge(735, 130, 1.0, "", ACC) + f'<rect x="735" y="238" width="100" height="6" rx="3" fill="{LINE}"/>'
    b += text(785, 340, "×5 ×10 ×20", 22, MUTED, 700)
    return svg(960, 420, b, "A cleaning cartridge, a barcode label ending in the generation code, and a storage case")


# ------------------------------------------------------------ 6 used tape
def fig_used():
    b = card(40, 40, 330, 340, ACC_50)
    b += cartridge(110, 150, 1.6, "", ACC_D)
    b += f'<path d="M200 150 l14 24 l-10 14 l16 20" stroke="{RED}" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
    b += magnifier(250, 200, 1.3)
    b += f'<circle cx="150" cy="310" r="0" fill="{GREEN}"/>'
    # right 2x2
    pos = ((410, 40), (665, 40), (410, 215), (665, 215))
    for (x, y) in pos:
        b += card(x, y, 245, 165)
    # 1 generation matches drive
    x, y = pos[0]
    b += mini(x + 28, y + 60, 60, 54, ACC) + text(x + 58, y + 140, "L5–L9", 18, MUTED, 700, "middle", MONO)
    b += f'<path d="M{x+96} {y+86} h20" stroke="{FAINT}" stroke-width="4" stroke-linecap="round"/>' + drv(x + 122, y + 62, 90, 48, INK2)
    b += check(x + 214, y + 30, 16)
    # 2 cracked shell
    x, y = pos[1]
    b += mini(x + 70, y + 40, 100, 90, MUTED) + f'<path d="M{x+130} {y+40} l-18 28 l14 10 l-16 30" stroke="{RED}" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
    b += cross(x + 214, y + 30, 16)
    # 3 humidity / mould
    x, y = pos[2]
    b += mini(x + 40, y + 50, 100, 90, MUTED) + "".join(f'<circle cx="{x+px}" cy="{y+py}" r="{r}" fill="{GREEN}" opacity=".85"/>' for px, py, r in ((70, 110, 8), (88, 120, 6), (112, 108, 7), (100, 82, 5)))
    b += drop(x + 170, y + 100, .9) + cross(x + 214, y + 30, 16)
    # 4 test before archive
    x, y = pos[3]
    b += mini(x + 25, y + 62, 60, 54, ACC) + f'<path d="M{x+92} {y+88} h24" stroke="{FAINT}" stroke-width="4" stroke-linecap="round"/>' + drv(x + 122, y + 62, 90, 48, INK2)
    b += f'<path d="M{x+30} {y+135} h60" stroke="{LINE}" stroke-width="0"/>' + check(x + 214, y + 30, 16)
    return svg(960, 420, b, "Used tape checks: matching generation and a test pass are good; cracks, mould and damp storage are not")


# ------------------------------------------------------------ 7 recovery
def fig_recovery():
    b = ""
    xs = (40, 270, 500, 730)
    for i, x in enumerate(xs):
        b += card(x, 80, 190, 250, ACC_50 if i == 3 else "#fff")
        b += f'<circle cx="{x+28}" cy="{80+4}" r="18" fill="{ACC}"/>' + text(x + 28, 90, str(i + 1), 20, "#fff", 700)
    for x in xs[:3]:
        b += arrow(x + 194, 205, x + 226, 205, ACC, 5)
    # 1 cartridge with label
    b += cartridge(70, 130, 1.3, "", MUTED) * 0
    b += cartridge(75, 120, 1.4, "", ACC_D)
    b += f'<rect x="75" y="256" width="140" height="48" rx="8" fill="#fff" stroke="{INK2}" stroke-width="3"/>' + barcode(85, 262, 70, 24, 5)
    b += f'<rect x="165" y="266" width="42" height="28" rx="7" fill="{ACC}"/>' + text(186, 287, "L5", 20, "#fff", 700, "middle", MONO)
    # 2 drives
    for k, g in enumerate(("L5", "L6", "L7")):
        y = 125 + k * 66
        b += drv(292, y, 90, 50, INK2) + text(440, y + 33, g, 22, ACC_D, 700, "middle", MONO)
    # 3 software
    b += folder(535, 120, 84, TEAL) + text(577, 250, "LTFS", 24, INK, 700) + text(577, 288, "tar", 22, MUTED, 700, "middle", MONO)
    # 4 copy to new media
    b += cartridge(775, 118, 1.2, "L9", ACC)
    b += f'<path d="M800 235 v20" stroke="{FAINT}" stroke-width="0"/>' + shield(790, 250, .85)
    return svg(960, 420, b, "Read the generation from the label, find a drive that reads it, identify the software, then copy to current media")


# ------------------------------------------------------------ 8 DPX
def fig_dpx():
    b = card(40, 50, 190, 320)
    b += server(85, 80, 100) + server(85, 160, 100) + dbase(103, 245, 64) + text(135, 350, "", 1)
    b += arrow(236, 210, 296, 210, ACC, 5)
    b += f'<rect x="300" y="120" width="250" height="180" rx="20" fill="{ACC}"/>' + text(425, 190, "Catalogic", 30, "#fff", 700) + text(425, 232, "DPX", 40, "#fff", 700)
    b += f'<rect x="420" y="258" width="10" height="0"/>' + chip(425, 340, "AES-256", 150, "#fff", ACC_D, 18, LINE)
    b += arrow(556, 210, 616, 210, ACC, 5)
    b += f'<rect x="620" y="140" width="190" height="130" rx="14" fill="{SURF2}"/>' + drv(640, 195, 150, 60, INK2)
    b += cartridge(650, 148, .5, "", ACC) + cartridge(702, 148, .5, "", ACC_D) + cartridge(754, 148, .5, "", ACC)
    b += arrow(715, 278, 715, 318, GREEN, 4, "2 8") * 0
    b += f'<path d="M830 205 H870" stroke="{FAINT}" stroke-width="4" stroke-dasharray="2 9" stroke-linecap="round"/>'
    b += shield(850, 200, .95) * 0
    b += f'<rect x="842" y="150" width="82" height="110" rx="16" fill="#fff" stroke="{LINE}" stroke-width="2"/>' * 0
    b += shield(860, 145, 1.0) + f'<path d="M815 230 H850" stroke="{GREEN}" stroke-width="0"/>'
    b += dash(812, 190, 856, 180, GREEN)
    b += f'<path d="M870 245 v30 M852 262 h36" stroke="{GREEN}" stroke-width="0"/>'
    b += f'<g transform="translate(849,232)"><path d="M0 22 L30 0 L60 22 V50 H0 z" fill="{INK2}"/><rect x="22" y="30" width="16" height="20" fill="#fff" opacity=".85"/></g>'
    return svg(960, 420, b, "Servers and a database back up through Catalogic DPX to tape drives and cartridges, with an offsite copy")


# ------------------------------------------------------------ 9 vendors
def fig_vendors():
    b = card(40, 30, 330, 250, ACC_50) + card(400, 30, 520, 250)
    b += bolt(80, 72, .9, ACC) + f'<g transform="translate(442,52)"><rect x="0" y="12" width="14" height="24" fill="{INK2}"/><rect x="18" y="0" width="14" height="36" fill="{INK2}"/><rect x="36" y="8" width="14" height="28" fill="{INK2}"/></g>'
    for i, n in enumerate(("Catalogic DPX", "Information2")):
        b += chip(205, 130 + i * 70, n, 250, "#fff", ACC_D, 20, ACC_100)
    big = (("Veritas NetBackup", "Commvault"), ("Veeam", "Arcserve"), ("Dell", "Cohesity"), ("Rubrik", "Data Protector"))
    for r, row in enumerate(big):
        for c, n in enumerate(row):
            b += chip(535 + c * 240, 122 + r * 44, n, 220, "#f7f6fa", INK, 18)
    b += cartridge(430, 320, .8, "LTO", ACC) * 0
    b += cartridge(430, 312, .9, "LTO", ACC) + drv(535, 330, 110, 52, INK2)
    b += arrow(205, 286, 440, 318, ACC, 4) + arrow(660, 286, 500, 318, ACC, 4)
    return svg(960, 420, b, "Agile challengers and big incumbents all write to the same LTO cartridge")


# ------------------------------------------------------------ 10 LTO vs HDD
def fig_vs():
    b = card(40, 40, 420, 340) + card(500, 40, 420, 340, ACC_50)
    b += hdd(90, 90, 1.0) + bolt(210, 130, 1.4, AMBER) + calendar(250, 100, 56, INK2) + text(278, 185, "3–7", 26, INK2, 700)
    b += f'<rect x="90" y="262" width="340" height="2" fill="{LINE}"/>'
    b += cartridge(550, 100, 1.1, "", ACC) + f'<rect x="530" y="200" width="160" height="10" rx="4" fill="{INK2}"/>' + plug_off(730, 130, 1.1) + calendar(785, 100, 56, ACC) + text(813, 185, "20–30+", 26, ACC_D, 700)
    b += f'<rect x="550" y="262" width="340" height="2" fill="{LINE}"/>'
    # bottom: who suits
    b += bolt(170, 322, .9, AMBER) + text(280, 332, "&lt; 20 TB", 30, INK2, 700)
    b += shield(590, 290, .75) + text(730, 332, "50 TB +", 30, ACC_D, 700)
    return svg(960, 420, b, "A powered hard drive with a 3 to 7 year life next to an unpowered LTO cartridge rated 20 to 30 years or more")


# ------------------------------------------------------------ 11 generations
def fig_gens():
    gens = (("LTO-5", "1.5 TB"), ("LTO-6", "2.5 TB"), ("LTO-7", "6 TB"), ("LTO-8", "12 TB"), ("LTO-9", "18 TB"), ("LTO-10", "30 TB"))
    cols = (MUTED, "#55506a", ACC_D, ACC, TEAL, INK2)
    b = f'<rect x="50" y="296" width="860" height="14" rx="6" fill="{INK2}"/>'
    for i, (g, tb) in enumerate(gens):
        s = .62 + .1 * i
        cx = 120 + i * 144
        w, h = 100 * s, 92 * s
        b += cartridge(cx - w / 2, 296 - h, s, f"L{5+i}", cols[i])
        b += text(cx, 346, g, 22, INK, 700) + text(cx, 376, tb, 18, MUTED, 600)
    b += arrow(110, 70, 850, 70, FAINT, 5) * 0
    return svg(960, 420, b, "LTO-5 to LTO-10 cartridges in a row, growing in capacity with each generation")


# ------------------------------------------------------------ 12 contact
def fig_contact():
    b = cartridge(380, 70, 1.5, "", ACC)
    b += f'<rect x="300" y="170" width="360" height="200" rx="20" fill="#fff" stroke="{INK2}" stroke-width="5"/>'
    b += f'<path d="M304 176 L480 296 L656 176" fill="none" stroke="{INK2}" stroke-width="5" stroke-linejoin="round"/>'
    b += f'<path d="M304 366 L420 270 M656 366 L540 270" stroke="{LINE}" stroke-width="4" stroke-linecap="round"/>'
    b += f'<g transform="translate(690,70)"><path d="M0 26 a26 26 0 0 1 26 -26 h124 a26 26 0 0 1 26 26 v56 a26 26 0 0 1 -26 26 h-70 l-34 30 v-30 h-20 a26 26 0 0 1 -26 -26 z" fill="{ACC}"/>'
    b += "".join(f'<circle cx="{58+k*32}" cy="54" r="8" fill="#fff"/>' for k in range(3)) + "</g>"
    b += check(180, 300, 0) * 0
    return svg(960, 420, b, "An envelope with an LTO cartridge peeking out and a chat bubble")


FIGURES = {
    "lto-library-anatomy.svg": fig_library,
    "lto-brands-one-tape.svg": fig_brands,
    "lto-30-year-shelf.svg": fig_lifespan,
    "lto-migration-500tb.svg": fig_migration,
    "lto-cleaning-and-labels.svg": fig_cleaning,
    "lto-used-tape-checks.svg": fig_used,
    "lto-recovery-path.svg": fig_recovery,
    "dpx-to-tape.svg": fig_dpx,
    "tape-software-vendors.svg": fig_vendors,
    "lto-vs-hdd-shelf.svg": fig_vs,
    "lto-generations-lineup.svg": fig_gens,
    "lto-contact-envelope.svg": fig_contact,
}

PLACEMENT = [
    {"path": "/lto-tape-library", "file": "lto-library-anatomy.svg", "w": 960, "h": 420,
     "alt": "A tape library with a magazine of cartridges, a robot picker on a rail and two drives, with an arrow carrying one cartridge from a slot to a drive.",
     "caption": "In a library a robot picker moves cartridges between the slots and the drives, so a backup that spans many tapes runs without anyone swapping media. See <a href=\"/resources/lto-cleaning-tapes-and-labels\">labels and cleaning tapes</a> for the barcodes a library relies on."},
    {"path": "/lto-tape-brand", "file": "lto-brands-one-tape.svg", "w": 960, "h": 420,
     "alt": "Fujifilm and Sony both feed the same cartridge, which then carries the HPE, IBM, Quantum or Dell label.",
     "caption": "Only Fujifilm and Sony manufacture the tape, so an HPE, IBM, Quantum or Dell cartridge is usually the same media with a different sticker. The price difference mostly pays for the brand, warranty and pre-printed labels."},
    {"path": "/why-tape/lto-tape-lifespan", "file": "lto-30-year-shelf.svg", "w": 960, "h": 420,
     "alt": "A long 30 year bar for a cartridge on a cool, dry shelf above three shorter bars for the drive generations that stop being available earlier.",
     "caption": "The 30 year rating assumes 16 to 25 °C and 20 to 50% humidity, but the drives that can read an old generation disappear sooner than the tape wears out. Plan to copy to current media, as in the <a href=\"/resources/lto-tape-migration\">migration guide</a>."},
    {"path": "/resources/lto-tape-migration", "file": "lto-migration-500tb.svg", "w": 960, "h": 420,
     "alt": "A grid of 84 LTO-7 cartridges of 6 TB on the left, a drive and arrow in the middle, and a grid of 28 LTO-9 cartridges of 18 TB on the right, labelled 500 TB.",
     "caption": "The same 500 TB needs 84 LTO-7 cartridges but only 28 LTO-9 cartridges, so a migration also shrinks what you store, label and handle."},
    {"path": "/resources/lto-cleaning-tapes-and-labels", "file": "lto-cleaning-and-labels.svg", "w": 960, "h": 420,
     "alt": "A cleaning cartridge marked CLN, a barcode label ending in L9 and a storage case.",
     "caption": "One universal cleaning cartridge is rated for up to 50 cleanings, and the last two characters of a data barcode give the generation, for example L9 for LTO-9. Keep each cartridge in a case on the shelf and in a padded case when it travels."},
    {"path": "/resources/cheap-lto-tapes", "file": "lto-used-tape-checks.svg", "w": 960, "h": 420,
     "alt": "A used cartridge under a magnifier next to four checks: matching generation and a test pass are ticked, a cracked shell and mould or damp storage are crossed.",
     "caption": "Check that the generation matches your drive, reject cracked shells and signs of mould or damp, and test a used tape before it holds anything you cannot replace."},
    {"path": "/resources/lto-tape-data-recovery", "file": "lto-recovery-path.svg", "w": 960, "h": 420,
     "alt": "Four steps: read the generation from the barcode label, find a drive that reads it, identify the software that wrote the tape, then copy to current media.",
     "caption": "The last two characters of the barcode, such as L5, give the generation and so the drives that can read it. Once the data is back, copy it to current media as described in the <a href=\"/resources/lto-tape-migration\">migration guide</a>."},
    {"path": "/resources/tape-backup-software/catalogicdpx", "file": "dpx-to-tape.svg", "w": 960, "h": 420,
     "alt": "Servers and a database send data to Catalogic DPX, which writes it with AES-256 encryption to a tape drive and cartridges, with a copy going offsite under a shield.",
     "caption": "DPX copies backups from servers and databases to tape with AES-256 encryption, and the cartridges can leave the building as an air-gapped copy."},
    {"path": "/best-tape-backup-software", "file": "tape-software-vendors.svg", "w": 960, "h": 440,
     "alt": "Two groups of backup software vendors, agile challengers and established incumbents, all connected to one LTO cartridge and drive.",
     "caption": "The report groups Catalogic DPX and Information2 as agile challengers and Veritas, Commvault, Veeam and the other incumbents separately, but all of them write to the same LTO cartridges."},
    {"path": "/why-tape/lto-vs-hdd", "file": "lto-vs-hdd-shelf.svg", "w": 960, "h": 420,
     "alt": "A powered hard drive rated for 3 to 7 years beside an unpowered LTO cartridge on a shelf rated for 20 to 30 years or more.",
     "caption": "A hard drive needs power and is typically used for 3 to 7 years, while an LTO cartridge sits offline and is rated for 20 to 30 years or more. Tape tends to win on cost once an archive passes about 50 TB, and a disk suits under 20 TB or fast restores."},
    {"path": "/about", "file": "lto-generations-lineup.svg", "w": 960, "h": 420,
     "alt": "LTO-5 to LTO-10 cartridges in a row, each larger than the last, labelled with native capacity.",
     "caption": "tapebackup.org tracks LTO media and drives generation by generation, from LTO-5 at 1.5 TB to LTO-10 at 30 TB native."},
    {"path": "/contact", "file": "lto-contact-envelope.svg", "w": 960, "h": 420,
     "alt": "An envelope with an LTO cartridge peeking out and a chat bubble beside it.",
     "caption": "Send a message with the LTO generation and quantity if you are asking about prices."},
]
