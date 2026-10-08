"""Scene figures for the blog posts and Q&A answers (see PLACEMENT at the bottom)."""
from draw_figures import *
import math
from draw_figures import _head


# ------------------------------------------------------------ helpers
def drive(x, y, w=200, h=64, led=GREEN, color=INK2):
    g = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="{color}"/>'
    g += f'<rect x="{x+14}" y="{y+h*0.3}" width="{w*0.55}" height="{h*0.2}" rx="4" fill="{INK}"/>'
    g += f'<rect x="{x+14}" y="{y+h*0.62}" width="{w*0.25}" height="6" rx="3" fill="{FAINT}"/>'
    g += f'<circle cx="{x+w-20}" cy="{y+h*0.35}" r="7" fill="{led}"/>'
    g += f'<rect x="{x+w-40}" y="{y+h*0.62}" width="26" height="6" rx="3" fill="{FAINT}" opacity=".7"/>'
    return g


def term(x, y, w, h, lines, title_col=INK2):
    g = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{INK}"/>'
    g += f'<rect x="{x}" y="{y}" width="{w}" height="28" rx="12" fill="{title_col}"/><rect x="{x}" y="{y+16}" width="{w}" height="12" fill="{title_col}"/>'
    for i, c in enumerate((RED, AMBER, GREEN)):
        g += f'<circle cx="{x+18+i*18}" cy="{y+14}" r="5" fill="{c}"/>'
    for i, (ind, lw, c) in enumerate(lines):
        g += f'<rect x="{x+18+ind}" y="{y+46+i*22}" width="{lw}" height="9" rx="4" fill="{c}"/>'
    return g


def warn(cx, cy, s=1.0, color=AMBER):
    p = f'{cx},{cy-30*s} {cx+34*s},{cy+26*s} {cx-34*s},{cy+26*s}'
    return (f'<polygon points="{p}" fill="{color}" stroke="{color}" stroke-width="{8*s}" stroke-linejoin="round"/>'
            f'<rect x="{cx-3*s}" y="{cy-12*s}" width="{6*s}" height="22*s" fill="#fff"/>'.replace("22*s", f"{20*s}") +
            f'<circle cx="{cx}" cy="{cy+18*s}" r="{3.6*s}" fill="#fff"/>')


def tag(x, y, label, color=AMBER, rot=-12):
    return (f'<g transform="translate({x},{y}) rotate({rot})"><path d="M0 0 h96 a8 8 0 0 1 8 8 v36 a8 8 0 0 1-8 8 h-96 l-26-26 z" fill="{color}"/>'
            f'<circle cx="-6" cy="26" r="6" fill="#fff"/>' + text(52, 35, label, 24, "#fff", 700) + '</g>')


def pc(x, y, s=1.0):
    return (f'<g transform="translate({x},{y}) scale({s})"><rect width="70" height="120" rx="10" fill="{INK2}"/>'
            f'<rect x="12" y="14" width="46" height="8" rx="3" fill="{FAINT}"/><rect x="12" y="30" width="46" height="8" rx="3" fill="{FAINT}"/>'
            f'<circle cx="35" cy="96" r="8" fill="{GREEN}"/></g>')


def magnifier(cx, cy, r=34, color=ACC):
    a = math.pi / 4
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#fff" fill-opacity=".55" stroke="{color}" stroke-width="9"/>'
            f'<line x1="{cx+r*math.cos(a)}" y1="{cy+r*math.sin(a)}" x2="{cx+r*2.1*math.cos(a)}" y2="{cy+r*2.1*math.sin(a)}" stroke="{color}" stroke-width="12" stroke-linecap="round"/>')


def check(cx, cy, s=1.0, color=GREEN):
    return f'<path d="M{cx-12*s} {cy} l{9*s} {10*s} l{17*s} {-20*s}" fill="none" stroke="{color}" stroke-width="{7*s}" stroke-linecap="round" stroke-linejoin="round"/>'


def cross(cx, cy, s=1.0, color=RED):
    return (f'<path d="M{cx-12*s} {cy-12*s} l{24*s} {24*s} M{cx+12*s} {cy-12*s} l{-24*s} {24*s}" stroke="{color}" stroke-width="{7*s}" stroke-linecap="round"/>')


def doc(x, y, w=60, h=76, color="#fff", lines=3, lc=ACC_100):
    g = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{color}" stroke="{LINE}" stroke-width="2"/>'
    for i in range(lines):
        g += f'<rect x="{x+10}" y="{y+14+i*14}" width="{(w-20)*(1 if i%2==0 else .7)}" height="6" rx="3" fill="{lc}"/>'
    return g


def folder(x, y, w=90, color=AMBER):
    return (f'<path d="M{x} {y+10} a8 8 0 0 1 8-8 h26 l10 12 h{w-44} a8 8 0 0 1 8 8 v{w*0.62} a8 8 0 0 1-8 8 h-{w-16} a8 8 0 0 1-8-8z" fill="{color}"/>')


def wrench(cx, cy, s=1.0, color=INK2, rot=45):
    return (f'<g transform="translate({cx},{cy}) rotate({rot}) scale({s})"><rect x="-6" y="-10" width="12" height="62" rx="6" fill="{color}"/>'
            f'<circle cx="0" cy="-14" r="16" fill="{color}"/><rect x="-6" y="-34" width="12" height="20" fill="{SURF}"/></g>')


def coin(cx, cy, r=22, color=AMBER, sym="$"):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}"/><circle cx="{cx}" cy="{cy}" r="{r-6}" fill="none" stroke="#fff" stroke-width="2.5"/>' + text(cx, cy + r * 0.34, sym, r * 0.95, "#fff", 700)


def server(x, y, w=200, h=34, col=INK2, led=GREEN):
    g = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{col}"/>'
    g += f'<rect x="{x+12}" y="{y+h/2-4}" width="{w*0.4}" height="8" rx="3" fill="{FAINT}"/><circle cx="{x+w-16}" cy="{y+h/2}" r="5" fill="{led}"/>'
    return g


def wave(cx, cy, r, color=FAINT, n=3, side=1):
    g = ""
    for i in range(n):
        rr = r + i * 16
        g += f'<path d="M{cx+side*rr*0.7:.1f} {cy-rr*0.7:.1f} A{rr} {rr} 0 0 {1 if side>0 else 0} {cx+side*rr*0.7:.1f} {cy+rr*0.7:.1f}" fill="none" stroke="{color}" stroke-width="5" stroke-linecap="round"/>'
    return g


def pill(cx, cy, w, label, fill="#fff", col=INK, border=LINE, size=19):
    return (f'<rect x="{cx-w/2}" y="{cy-19}" width="{w}" height="38" rx="19" fill="{fill}" stroke="{border}" stroke-width="2"/>'
            + text(cx, cy + 7, label, size, col, 700, font=MONO))


def bug(cx, cy, s=1.0, color=RED):
    g = f'<g transform="translate({cx},{cy}) scale({s})">'
    for dy in (-12, 4, 20):
        g += f'<path d="M-18 {dy} L-34 {dy-8} M18 {dy} L34 {dy-8}" stroke="{color}" stroke-width="4" stroke-linecap="round"/>'
    g += f'<ellipse cx="0" cy="8" rx="20" ry="26" fill="{color}"/><circle cx="0" cy="-24" r="12" fill="{color}"/>'
    g += f'<path d="M-6 -34 l-8 -12 M6 -34 l8 -12" stroke="{color}" stroke-width="4" stroke-linecap="round"/><line x1="0" y1="-16" x2="0" y2="34" stroke="#fff" stroke-width="3"/>'
    return g + "</g>"


def vault_door(cx, cy, r=60):
    g = f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{INK2}" stroke="{FAINT}" stroke-width="6"/>'
    for c, s in ((1, 0), (-.5, .87), (-.5, -.87)):
        g += f'<line x1="{cx}" y1="{cy}" x2="{cx+r*.65*c:.1f}" y2="{cy+r*.65*s:.1f}" stroke="{FAINT}" stroke-width="6" stroke-linecap="round"/>'
    return g


# ------------------------------------------------------------ 1 cheap dream
def f_cheap_dream():
    b = f'<path d="M0 250 H960 V378 a22 22 0 0 1-22 22 H22 a22 22 0 0 1-22-22z" fill="{SURF2}"/><rect x="0" y="250" width="960" height="4" fill="{LINE}"/>'
    b += drive(150, 150, 230, 80) + tag(120, 110, "$500") + text(265, 285, "LTO-6", 24, MUTED, 700)
    b += f'<ellipse cx="660" cy="262" rx="150" ry="34" fill="{INK}"/><ellipse cx="660" cy="270" rx="110" ry="22" fill="#000" opacity=".5"/>'
    b += f'<path d="M520 262 q140 -52 280 0" fill="none" stroke="{ACC}" stroke-width="3" stroke-dasharray="3 8"/>'
    b += cartridge(610, 100, .62, "", ACC, -14) + cartridge(700, 150, .5, "", ACC_D, 18)
    b += f'<path d="M640 190 v40" stroke="{FAINT}" stroke-width="3" stroke-dasharray="3 8"/>'
    b += text(450, 190, "$", 54, AMBER, 700) 
    for k in range(3):
        b += f'<ellipse cx="660" cy="{330+k*24}" rx="{110-k*30}" ry="{14-k*3}" fill="none" stroke="{ACC}" stroke-width="3" opacity="{.7-k*.2}"/>'
    b += arrow(400, 215, 490, 240, ACC, 5, "2 10")
    return svg(960, 400, b, "A cheap LTO-6 drive price tag next to a rabbit hole full of falling cartridges")


# ------------------------------------------------------------ 2 paperweight
def f_paperweight():
    b = f'<rect x="120" y="300" width="720" height="14" rx="6" fill="{INK2}"/><rect x="150" y="314" width="18" height="60" fill="{INK2}"/><rect x="792" y="314" width="18" height="60" fill="{INK2}"/>'
    for i, (dx, dy, r) in enumerate(((0, 0, -3), (30, -4, 4), (-20, -8, -7), (60, -10, 6))):
        b += f'<g transform="rotate({r} {400+dx} {270+dy})">' + doc(330 + dx, 220 + dy, 150, 78, "#fff", 2) + "</g>"
    b += drive(310, 150, 240, 86, ACC_D) + f'<rect x="312" y="150" width="236" height="86" rx="9" fill="none" stroke="{INK}" stroke-width="3"/>'
    b += f'<rect x="440" y="168" width="84" height="38" rx="6" fill="{INK}"/>' + text(482, 195, "ERR 5", 19, RED, 700, font=MONO)
    b += f'<circle cx="528" cy="170" r="8" fill="{RED}"/>'
    b += tag(630, 130, "$6,000", RED, 10)
    b += f'<path d="M270 130 q-70 -20 -90 40 M690 270 q80 -40 70 -100" fill="none" stroke="{FAINT}" stroke-width="4" stroke-dasharray="4 10"/>'
    b += cartridge(170, 190, .6, "", ACC, -8) + cartridge(215, 252, .5, "", TEAL, 10)
    b += wave(570, 190, 50, RED, 0)
    return svg(960, 400, b, "A pricey LTO-7 drive showing an error sits on loose papers like a paperweight")


# ------------------------------------------------------------ 3 rabbit hole stairs
def f_rabbit_stairs():
    b = ""
    steps = 5
    for i in range(steps):
        x, y = 50 + i * 170, 60 + i * 52
        b += f'<rect x="{x}" y="{y+90}" width="170" height="{392-y-90}" fill="{ACC_100}" opacity="{1-i*.1}"/>'
        b += f'<rect x="{x}" y="{y+90}" width="170" height="10" fill="{ACC_D}" opacity=".4"/>'
        cx = x + 85
        if i == 0:
            b += cartridge(cx - 50, y + 10, .7, "", ACC) + cartridge(cx + 2, y + 24, .55, "", ACC_D)
        elif i == 1:
            b += drive(cx - 55, y + 24, 110, 50)
        elif i == 2:
            b += f'<rect x="{cx-45}" y="{y+22}" width="90" height="56" rx="6" fill="{GREEN}"/><rect x="{cx-30}" y="{y+70}" width="60" height="14" fill="{AMBER}"/><rect x="{cx-30}" y="{y+34}" width="26" height="16" rx="3" fill="#fff" opacity=".8"/>' + text(cx + 16, y + 56, "SAS", 15, "#fff", 700, font=MONO)
        elif i == 3:
            b += doc(cx - 32, y + 4, 64, 84, "#fff", 4, ACC)
        else:
            b += f'<rect x="{cx-48}" y="{y+8}" width="96" height="74" rx="8" fill="#fff" stroke="{INK2}" stroke-width="4"/><rect x="{cx-48}" y="{y+8}" width="96" height="16" rx="8" fill="{INK2}"/><path d="M{cx-22} {y+60} l12 -20 l12 14 l14 -22" stroke="{ACC}" stroke-width="5" fill="none" stroke-linecap="round"/>'
    return svg(960, 420, b, "Stairs descend from a few cheap cartridges to a drive, a SAS card, a catalog and backup software")


# ------------------------------------------------------------ 4 built it
def f_built_it():
    b = f'<g opacity=".9">' + "".join(f'<rect x="{70+k*14}" y="{110+k*18}" width="200" height="120" rx="12" fill="#fff" stroke="{LINE}" stroke-width="2"/>' for k in range(3)) + "</g>"
    b += "".join(f'<rect x="{110+k*14}" y="{150+k*18+j*18}" width="{110-j*16}" height="8" rx="4" fill="{FAINT}"/>' for k in (2,) for j in range(3))
    b += f'<rect x="60" y="100" width="240" height="240" rx="0" fill="none"/>'
    b += cross(170, 215, 2.2, RED).replace("stroke-width=\"15.4\"", "stroke-width=\"12\" opacity=\".75\"") if False else ""
    b += f'<path d="M70 110 L290 300 M290 110 L70 300" stroke="{RED}" stroke-width="10" stroke-linecap="round" opacity=".55"/>'
    b += term(380, 90, 270, 220, [(0, 120, ACC_100), (20, 150, TEAL), (20, 90, AMBER), (0, 60, ACC_100), (20, 180, GREEN), (20, 110, FAINT), (0, 140, ACC_100), (0, 70, FAINT)])
    b += wrench(675, 110, 1.0, AMBER, 40)
    b += cartridge(700, 190, 1.1, "", ACC)
    b += f'<rect x="745" y="206" width="70" height="44" rx="6" fill="{INK}" opacity="0"/>'
    b += doc(780, 70, 90, 100, "#fff", 4, ACC_100)
    b += text(755, 320, "FossilSafe", 19, ACC_D, 700)
    b += arrow(660, 235, 690, 235, ACC, 5)+ arrow(790, 200, 825, 178, ACC, 4)
    return svg(960, 400, b, "A heavy crossed-out software suite on the left, a hand-written script in a terminal on the right, and a cartridge carrying its own index")


# ------------------------------------------------------------ 5 noise, bugs
def f_noise_bugs():
    b = f'<rect x="60" y="250" width="840" height="100" rx="16" fill="{SURF2}"/>'
    b += drive(120, 190, 240, 86) + wave(390, 200, 24, ACC, 4) + wave(90, 200, 24, ACC, 3, -1)
    b += text(240, 310, "LTO-5", 24, MUTED, 700)
    b += hdd(590, 150, .9, "#b9b5c6") + f'<path d="M575 130 L690 280 M690 130 L575 280" stroke="{INK2}" stroke-width="8" stroke-linecap="round" opacity=".0"/>'
    b += bug(520, 150, 1.0)
    b += pill(650, 330, 120, "/dev/st0") + pill(790, 330, 130, "/dev/nst0") + pill(790, 280, 130, "/dev/sg1", "#fff", AMBER, AMBER)
    b += f'<path d="M495 205 q40 40 100 20" fill="none" stroke="{FAINT}" stroke-width="3" stroke-dasharray="3 9"/>'
    b += text(790, 230, "?", 56, AMBER, 700)
    b += f'<rect x="690" y="100" width="190" height="60" rx="10" fill="{INK}"/>' + f'<rect x="704" y="118" width="70" height="8" rx="4" fill="{GREEN}"/><rect x="704" y="134" width="120" height="8" rx="4" fill="{FAINT}"/>'
    return svg(960, 400, b, "A noisy tape drive, a bug, and several confusing device names on a Linux terminal")


# ------------------------------------------------------------ 6 iceberg
def f_iceberg():
    b = f'<path d="M0 170 H960 V398 a22 22 0 0 1-22 22 H22 a22 22 0 0 1-22-22z" fill="{ACC_50}"/><path d="M0 170 q60 -12 120 0 t120 0 t120 0 t120 0 t120 0 t120 0 t120 0 t120 0" fill="none" stroke="{TEAL}" stroke-width="4"/>'
    b += f'<polygon points="400,170 440,110 480,150 520,70 560,150 590,120 620,170" fill="#fff" stroke="{LINE}" stroke-width="3" stroke-linejoin="round"/>'
    b += f'<polygon points="400,170 300,230 250,320 330,390 480,405 640,390 700,310 660,230 620,170" fill="{ACC_100}" stroke="{ACC}" stroke-width="3" stroke-linejoin="round" opacity=".95"/>'
    b += cartridge(488, 88, .36, "", ACC) 
    b += drive(310, 235, 140, 44) + pill(520, 252, 84, "HBA", "#fff", ACC_D, ACC)
    b += f'<g transform="translate(574,238)">' + "".join(f'<rect x="0" y="{k*12}" width="50" height="9" rx="3" fill="{INK2}"/>' for k in range(3)) + "</g>"
    b += doc(340, 300, 54, 70, "#fff", 3, ACC) + f'<g transform="translate(420,310)"><circle cx="20" cy="24" r="20" fill="none" stroke="{INK2}" stroke-width="5"/><path d="M20 12 v14 l9 6" stroke="{INK2}" stroke-width="5" fill="none" stroke-linecap="round"/></g>'
    b += f'<g transform="translate(510,312)"><rect width="46" height="46" rx="6" fill="{GREEN}"/><path d="M12 24 l8 8 l16 -18" stroke="#fff" stroke-width="6" fill="none" stroke-linecap="round"/></g>'
    b += f'<g transform="translate(590,318)">' + wrench(20, 20, .6, AMBER, 40) + "</g>"
    return svg(960, 420, b, "An iceberg: the cheap cartridge is the visible tip, drives, HBA, library, catalog, cleaning and restores sit below the waterline")


# ------------------------------------------------------------ 7 one bad archive
def f_bad_archive():
    b = card(40, 40, 880, 150) + card(40, 220, 880, 160)
    # loose files on tape
    b += f'<rect x="90" y="100" width="780" height="30" rx="15" fill="{INK2}"/>'
    for k in range(12):
        c = ACC if k != 6 else RED
        b += f'<rect x="{104+k*62}" y="{104}" width="50" height="22" rx="5" fill="{c}"/>'
    b += cross(750, 160, .0, RED)
    b += f'<path d="M{104+6*62+10} 96 l22 36" stroke="{RED}" stroke-width="3" opacity="0"/>' 
    b += text(110, 166, "files", 18, MUTED, 600, "start", MONO) + check(836, 160, .8)
    # one big tar block
    b += f'<rect x="90" y="270" width="780" height="40" rx="20" fill="{INK2}"/><rect x="104" y="274" width="752" height="32" rx="8" fill="{AMBER}"/>'
    b += f'<path d="M520 270 l16 14 l-14 10 l16 14 l-10 8" stroke="{INK}" stroke-width="5" fill="none" stroke-linejoin="round"/>'
    b += f'<path d="M104 290 h752" stroke="{INK}" stroke-width="2" stroke-dasharray="2 10" opacity=".4"/>'
    b += text(110, 348, "tar", 20, MUTED, 600, "start", MONO) + cross(836, 345, .8)
    b += f'<g transform="translate(470,320) rotate(8)"><circle cx="20" cy="20" r="0"/></g>'
    return svg(960, 420, b, "Many separate files on a tape stay readable, but one cracked tar archive block can lose everything inside it")


# ------------------------------------------------------------ 8 linux scripts
def f_linux_scripts():
    b = term(60, 70, 250, 250, [(0, 90, ACC_100), (0, 150, TEAL), (14, 100, AMBER), (14, 130, FAINT), (0, 60, ACC_100), (0, 170, GREEN), (14, 80, FAINT)])
    chips = (("tar", 470, 90), ("mt", 640, 120), ("LTFS", 790, 100), ("sha256", 520, 220), ("cron", 760, 220), ("barcode", 640, 330))
    pts = [(c[1], c[2]) for c in chips]
    paths = ["M310 150 C 400 100, 420 120, 470 90", "M470 90 C 520 40, 600 160, 640 120", "M640 120 C 700 70, 740 140, 790 100",
             "M790 100 C 880 140, 860 190, 760 220", "M760 220 C 700 270, 600 190, 520 220", "M520 220 C 440 260, 560 340, 640 330",
             "M310 240 C 400 280, 440 200, 520 220", "M470 90 C 400 200, 560 150, 640 330", "M640 120 C 580 200, 700 230, 760 220"]
    for p in paths:
        b += f'<path d="{p}" fill="none" stroke="{ACC}" stroke-width="3" opacity=".55"/>'
    for l, x, y in chips:
        b += pill(x, y, 30 + 15 * len(l), l, "#fff", INK, ACC)
    b += f'<circle cx="150" cy="365" r="0"/>' + text(860, 340, "?", 80, AMBER, 700) + warn(870, 300, .0)
    return svg(960, 400, b, "A script terminal whose tar, mt, LTFS, checksum, cron and barcode pieces are tangled together")


# ------------------------------------------------------------ 9 tape is dead
def f_tape_dead():
    b = f'<path d="M0 300 H960 V378 a22 22 0 0 1-22 22 H22 a22 22 0 0 1-22-22z" fill="{SURF2}"/><rect x="0" y="300" width="960" height="4" fill="{LINE}"/>'
    b += f'<path d="M330 304 V150 a90 90 0 0 1 180 0 V304 z" fill="#fff" stroke="{FAINT}" stroke-width="5"/>' + text(420, 175, "TAPE", 32, MUTED, 700) + text(420, 215, "RIP", 22, FAINT, 700)
    b += f'<path d="M386 235 h68 M420 225 v40" stroke="{FAINT}" stroke-width="4"/>'
    b += cartridge(560, 235, .8, "LTO", ACC, 8)
    b += f'<path d="M640 238 C 640 200 690 210 690 170" fill="none" stroke="{GREEN}" stroke-width="6" stroke-linecap="round"/><path d="M690 175 c 30 -40 70 -20 60 10 c -30 10 -50 5 -60 -10z" fill="{GREEN}"/><path d="M688 190 c -34 -34 -74 -16 -62 14 c 30 8 50 2 62 -14z" fill="{GREEN}" opacity=".8"/>'
    b += f'<g transform="translate(100,170)">' + server(0, 0, 130, 30) + server(0, 38, 130, 30) + server(0, 76, 130, 30, INK2, RED) + "</g>"
    b += f'<g transform="translate(790,200)"><rect width="110" height="104" rx="8" fill="{INK}"/>' + "".join(f'<rect x="10" y="{10+k*30}" width="90" height="22" rx="4" fill="{INK2}"/>' + "".join(f'<rect x="{16+j*22}" y="{14+k*30}" width="16" height="14" rx="2" fill="{ACC}"/>' for j in range(4)) for k in range(3)) + "</g>"
    b += arrow(720, 320, 770, 320, ACC, 4, "2 8") if False else ""
    b += f'<circle cx="170" cy="130" r="0"/>'
    return svg(960, 400, b, "A tombstone marked tape with a healthy LTO cartridge sprouting from the grave beside a rack of cartridges")


# ------------------------------------------------------------ 10 test restore
def f_test_restore():
    b = pill(250, 70, 120, "LTFS") + pill(480, 70, 120, "tar") + pill(710, 70, 160, "catalog")
    for x in (250, 480, 710):
        b += f'<path d="M{x} 92 V140" stroke="{FAINT}" stroke-width="4" stroke-dasharray="4 8"/>'
    b += f'<path d="M250 140 H710" stroke="{FAINT}" stroke-width="4" stroke-dasharray="4 8"/><path d="M480 140 V175" stroke="{ACC}" stroke-width="4"/>'
    b += cartridge(110, 200, 1.3, "LTO", ACC) 
    b += arrow(250, 240, 400, 240, ACC, 6)
    b += f'<path d="M290 205 a60 60 0 0 1 100 0" fill="none" stroke="{ACC}" stroke-width="4"/>'
    b += folder(420, 190, 150, AMBER) + doc(450, 190, 54, 70, "#fff", 3) + doc(510, 196, 54, 70, "#fff", 3)
    b += f'<circle cx="640" cy="260" r="60" fill="{GREEN}"/>' + check(640, 260, 2.2, "#fff")
    b += magnifier(790, 245, 34, ACC_D)
    b += f'<rect x="772" y="231" width="36" height="8" rx="4" fill="{ACC}"/><rect x="772" y="247" width="24" height="8" rx="4" fill="{ACC}"/>'
    return svg(960, 380, b, "Whichever format you pick, the test is a restore from a cartridge to a folder that ends in a green check")


# ------------------------------------------------------------ 11 rogue drive
def f_rogue():
    cx, cy = 480, 190
    b = drive(cx - 130, cy - 45, 260, 90)
    b += f'<path d="M{cx} {cy-110} A110 110 0 0 1 {cx+130} {cy-70}" fill="none" stroke="{RED}" stroke-width="8" stroke-linecap="round"/>' + _head(cx + 133, cy - 62, cx + 110, cy - 100, RED)
    b += f'<path d="M{cx} {cy+110} A110 110 0 0 1 {cx-130} {cy+70}" fill="none" stroke="{RED}" stroke-width="8" stroke-linecap="round"/>' + _head(cx - 133, cy + 62, cx - 110, cy + 100, RED)
    b += f'<path d="M{cx+160} {cy+20} A160 160 0 0 1 {cx+120} {cy+95}" fill="none" stroke="{AMBER}" stroke-width="6" stroke-linecap="round"/>'
    b += cartridge(cx - 40, cy - 110, .55, "", ACC, -10) 
    for dx, dy in ((-170, -20), (-185, 10), (-160, 40)):
        b += f'<path d="M{cx+dx} {cy+dy} l-26 -8" stroke="{RED}" stroke-width="5" stroke-linecap="round"/>'
    b += warn(cx + 230, cy - 80, .9, AMBER)
    sus = ((150, "drop"), (480, "reel"), (810, "wire"))
    for x, k in sus:
        b += f'<rect x="{x-90}" y="310" width="180" height="80" rx="16" fill="#fff" stroke="{LINE}" stroke-width="2"/>'
        if k == "drop":
            b += f'<path d="M{x} 322 c 22 28 26 40 0 52 c -26 -12 -22 -24 0 -52z" fill="{TEAL}"/>'
        elif k == "reel":
            b += f'<circle cx="{x}" cy="350" r="28" fill="{INK2}"/><circle cx="{x}" cy="350" r="9" fill="#fff"/>' + "".join(f'<line x1="{x}" y1="350" x2="{x+22*c:.1f}" y2="{350+22*s:.1f}" stroke="#fff" stroke-width="4"/>' for c, s in ((1, 0), (-.5, .87), (-.5, -.87)))
        else:
            b += f'<path d="M{x-40} 370 C {x-20} 320 {x+10} 380 {x+40} 330" fill="none" stroke="{INK2}" stroke-width="6" stroke-linecap="round"/><circle cx="{x-40}" cy="370" r="7" fill="{INK2}"/><circle cx="{x+40}" cy="330" r="7" fill="{INK2}"/>'
        b += text(x + 64, 360, "?", 34, AMBER, 700)
    return svg(960, 420, b, "A tape drive stuck in a rewind-eject loop above three suspects: dirty heads, a bad reel and a loose cable")


# ------------------------------------------------------------ 12 home lto
def f_home():
    b = f'<path d="M60 250 L250 90 L440 250 z" fill="{ACC_D}"/><rect x="95" y="250" width="310" height="140" fill="#fff" stroke="{LINE}" stroke-width="3"/>'
    b += f'<rect x="120" y="300" width="260" height="10" rx="4" fill="{INK2}"/>' + drive(135, 250, 150, 50) + cartridge(300, 255, .45, "", ACC) + cartridge(335, 255, .45, "", TEAL)
    b += f'<rect x="150" y="345" width="180" height="10" rx="4" fill="{INK2}"/>' + "".join(cartridge(160 + k * 36, 322, .32, "", (ACC, ACC_D, TEAL)[k % 3]) for k in range(5))
    b += f'<rect x="215" y="150" width="70" height="60" rx="8" fill="{ACC_100}"/><line x1="250" y1="150" x2="250" y2="210" stroke="{ACC_D}" stroke-width="3"/><line x1="215" y1="180" x2="285" y2="180" stroke="{ACC_D}" stroke-width="3"/>'
    # checklist
    b += card(520, 70, 220, 300) + f'<rect x="600" y="58" width="60" height="26" rx="8" fill="{INK2}"/>'
    for i in range(5):
        y = 110 + i * 52
        b += f'<rect x="545" y="{y}" width="30" height="30" rx="7" fill="#fff" stroke="{ACC}" stroke-width="3"/>' + check(560, y + 15, .7, GREEN)
        b += f'<rect x="590" y="{y+10}" width="{120 - (i%3)*20}" height="10" rx="5" fill="{ACC_100}"/>'
    # offsite bag
    b += arrow(750, 240, 800, 240, ACC, 5) + f'<rect x="810" y="190" width="110" height="130" rx="14" fill="{AMBER}"/><path d="M840 190 q30 -50 60 0" fill="none" stroke="{INK2}" stroke-width="7"/>'
    b += cartridge(832, 235, .66, "", ACC)
    return svg(960, 420, b, "A small home tape setup with a labelled shelf, a checklist of ticked habits and a bag taking a cartridge offsite")


# ------------------------------------------------------------ 13 used library
def f_library():
    b = f'<rect x="210" y="70" width="540" height="270" rx="14" fill="{INK2}"/><rect x="226" y="86" width="508" height="190" rx="8" fill="{INK}"/>'
    for r in range(3):
        for c in range(9):
            if (r, c) in ((1, 4), (2, 7), (0, 2)):
                continue
            b += f'<rect x="{240+c*53}" y="{96+r*60}" width="42" height="50" rx="5" fill="{(ACC, ACC_D, TEAL)[(r+c)%3]}"/>'
    b += f'<rect x="226" y="290" width="200" height="34" rx="6" fill="{INK}"/><circle cx="700" cy="307" r="8" fill="{RED}"/>'
    b += f'<g transform="rotate(-6 560 310)">' + drive(480, 288, 200, 40, "#6e6a7c") + "</g>"
    b += wave(790, 150, 30, RED, 3) + wave(170, 150, 30, RED, 3, -1) + warn(850, 90, .9, AMBER)
    b += f'<g transform="rotate(5 120 300)"><rect x="60" y="270" width="110" height="80" rx="4" fill="{AMBER}" opacity=".9"/><rect x="74" y="290" width="70" height="8" rx="4" fill="#fff"/><rect x="74" y="308" width="52" height="8" rx="4" fill="#fff"/></g>'
    b += text(115, 345, "?", 60, "#fff", 700) if False else text(150, 335, "?", 36, "#fff", 700)
    b += wrench(820, 300, 1.3, MUTED, 40) + f'<circle cx="770" cy="372" r="6" fill="{FAINT}"/><circle cx="880" cy="365" r="6" fill="{FAINT}"/><circle cx="845" cy="385" r="5" fill="{FAINT}"/>'
    b += f'<rect x="160" y="352" width="60" height="10" rx="4" fill="{FAINT}" transform="rotate(-14 190 357)"/>'
    return svg(960, 410, b, "A noisy secondhand tape library with missing cartridges, a loose drive, a mystery password note and a wrench")


# ------------------------------------------------------------ 14 which drive
def f_which_drive():
    b = drive(60, 175, 150, 56)
    roads = ((270, "LTO-5", 6, ACC_D), (200, "LTO-7", 3, ACC), (130, "LTO-9", 2, TEAL))
    b += f'<rect x="220" y="196" width="14" height="14" fill="{FAINT}"/>'
    for i, (y, lab, n, col) in enumerate(((70, "LTO-5", 7, ACC_D), (200, "LTO-7", 4, ACC), (330, "LTO-9", 2, TEAL))):
        b += f'<path d="M234 203 C 300 203, 320 {y}, 400 {y}" fill="none" stroke="{FAINT}" stroke-width="40" stroke-linecap="round" opacity=".35"/>'
        b += f'<path d="M234 203 C 300 203, 320 {y}, 400 {y} H 640" fill="none" stroke="#fff" stroke-width="4" stroke-dasharray="14 12"/>'
        b += f'<rect x="420" y="{y-46}" width="120" height="30" rx="8" fill="{col}"/>' + text(480, y - 24, lab, 18, "#fff", 700, font=MONO)
        b += f'<rect x="465" y="{y-16}" width="10" height="26" fill="{INK2}"/>'
        for k in range(n):
            b += cartridge(650 + (k % 4) * 66, y - 38 + (k // 4) * 36, .5, "", col)
    b += text(110, 270, "?", 60, AMBER, 700) 
    return svg(960, 400, b, "A fork in the road from one tape drive to LTO-5, LTO-7 or LTO-9, with more cartridges piled at the end of the older road")


# ------------------------------------------------------------ 15 sas path
def f_sas_path():
    y = 190
    b = f'<line x1="120" y1="{y}" x2="840" y2="{y}" stroke="{LINE}" stroke-width="14" stroke-linecap="round"/>'
    b += pc(60, y - 70, 1.1)
    b += f'<g transform="translate(220,{y-60})"><rect width="100" height="100" rx="8" fill="{GREEN}"/><rect x="8" y="76" width="64" height="16" fill="{AMBER}"/><rect x="10" y="12" width="40" height="22" rx="3" fill="#fff" opacity=".8"/>' + text(50, 62, "HBA", 20, "#fff", 700, font=MONO) + "</g>"
    b += f'<path d="M320 {y} C 380 {y-70}, 430 {y+70}, 490 {y}" fill="none" stroke="{INK2}" stroke-width="10" stroke-linecap="round"/><rect x="316" y="{y-10}" width="22" height="20" rx="4" fill="{INK}"/><rect x="478" y="{y-10}" width="22" height="20" rx="4" fill="{INK}"/>'
    b += text(405, y - 62, "SAS", 22, ACC_D, 700, font=MONO) + warn(405, y + 80, .6, AMBER)
    b += f'<rect x="500" y="{y-45}" width="130" height="90" rx="10" fill="#fff" stroke="{INK2}" stroke-width="4"/>' + "".join(f'<rect x="514" y="{y-30+k*24}" width="{102 - k*18}" height="10" rx="4" fill="{ACC_100}"/>' for k in range(3))
    b += f'<path d="M630 {y} h40" stroke="{INK2}" stroke-width="10" stroke-linecap="round"/>'
    b += drive(670, y - 45, 190, 90, ACC_D) + check(826, y + 62, 1.0, GREEN) if False else drive(670, y - 45, 190, 90, ACC_D)
    b += f'<circle cx="835" cy="{y+90}" r="26" fill="{GREEN}"/>' + check(835, y + 90, .9, "#fff")
    b += f'<g opacity=".9">' + "".join(f'<circle cx="{150+k*60}" cy="{y+120}" r="0"/>' for k in range(1)) + "</g>"
    b += text(405, 330, "?", 54, MUTED, 700)
    b += f'<path d="M700 {y-70} l50 -0" stroke="none"/>'
    return svg(960, 400, b, "A chain from host to HBA to SAS cable to enclosure to a used LTO-8 drive, where the suspicious link is the cable and not the drive")


# ------------------------------------------------------------ 16 mainframe + open
def f_mainframe():
    b = f'<rect x="50" y="60" width="180" height="150" rx="12" fill="{INK}"/><rect x="62" y="74" width="156" height="122" rx="6" fill="{INK2}"/>' + text(140, 150, "Z", 66, ACC_100, 700)
    b += f'<rect x="80" y="86" width="100" height="6" rx="3" fill="{FAINT}"/>'
    for k in range(3):
        b += server(60, 250 + k * 44, 160, 34, INK2, GREEN)
    b += text(140, 236, "", 14)
    b += arrow(235, 135, 330, 215, ACC, 5) + arrow(235, 290, 330, 235, ACC, 5)
    b += f'<path d="M330 150 L430 200 V250 L330 300 Z" fill="{ACC_100}" stroke="{ACC}" stroke-width="3" stroke-linejoin="round"/>' + hdd(350, 175, .7, ACC_D)
    b += arrow(440, 225, 520, 225, ACC, 5)
    b += card(530, 130, 180, 190, ACC_50) + "".join(cartridge(548 + (k % 2) * 80, 150 + (k // 2) * 54, .5, "", (ACC, ACC_D, TEAL, ACC)[k]) for k in range(4))
    b += f'<rect x="548" y="270" width="144" height="8" rx="4" fill="{INK2}"/>'
    b += arrow(715, 225, 780, 225, ACC, 5, "2 10") + shield(796, 170, 1.4)
    return svg(960, 420, b, "A mainframe and open-systems servers feed one backup disk, then a shared tape archive with a protected copy")


# ------------------------------------------------------------ 17 multi tier pyramid
def f_pyramid():
    b = ""
    cx = 340
    tiers = ((70, 150, ACC_D), (150, 250, ACC), (230, 350, TEAL))
    # trapezoid layers
    layers = [(70, 140, 70, 180, ACC_D), (150, 140, 180, 270, ACC), (230, 140, 270, 360, TEAL)]
    b += f'<polygon points="340,50 420,140 260,140" fill="{ACC_D}"/>'
    b += f'<polygon points="255,150 425,150 495,240 185,240" fill="{ACC}"/>'
    b += f'<polygon points="180,250 500,250 580,340 100,340" fill="{TEAL}"/>'
    b += f'<g transform="translate(305,86)"><rect width="70" height="44" rx="8" fill="#fff"/><rect x="10" y="12" width="34" height="8" rx="4" fill="{ACC}"/><circle cx="56" cy="16" r="5" fill="{GREEN}"/></g>'
    b += f'<path d="M290 205 a22 22 0 0 1 4-42 a28 28 0 0 1 50-4 a22 22 0 0 1 24 28 z" fill="#fff" opacity=".9"/>'
    b += f'<path d="M400 205 v-8" stroke="none"/>'
    for k in range(4):
        b += cartridge(170 + k * 70, 270, .5, "", "#fff", 0)
    # right: speed/cost arrows
    b += arrow(700, 340, 700, 85, ACC, 6) + arrow(790, 75, 790, 340, TEAL, 6)
    b += f'<path d="M660 90 l20 -20 l20 20 z" fill="{ACC}" opacity="0"/>'
    b += f'<g transform="translate(684,10)"><path d="M0 0 l12 -22 h24 l-8 18 h14 l-34 40 l8 -26 z" fill="{AMBER}" transform="translate(0,22) scale(.9)"/></g>'
    b += coin(790, 40, 20, AMBER)
    b += shield(850, 150, 1.0) 
    return svg(960, 420, b, "A three-layer pyramid from a fast disk appliance through cloud object storage down to tape, with speed rising one way and cost falling the other")


# ------------------------------------------------------------ 18 packaging
def f_packaging():
    b = f'<rect x="150" y="150" width="400" height="220" rx="10" fill="{AMBER}"/><path d="M150 150 L110 108 H590 L550 150 z" fill="#c27a14"/>'
    b += f'<rect x="170" y="165" width="360" height="190" rx="8" fill="{ACC_50}"/>'
    # bubble wrap around cartridge
    b += f'<rect x="240" y="180" width="220" height="150" rx="22" fill="#fff" stroke="{TEAL}" stroke-width="3" opacity=".95"/>'
    for r in range(3):
        for c in range(7):
            pass
    b += "".join(f'<circle cx="{250+c*30}" cy="{190+r*0}" r="0"/>' for r in range(1) for c in range(1))
    for pos in [(255, 195), (285, 195), (315, 195), (345, 195), (375, 195), (405, 195), (435, 195), (255, 315), (285, 315), (315, 315), (345, 315), (375, 315), (405, 315), (435, 315), (250, 225), (250, 255), (250, 285), (450, 225), (450, 255), (450, 285)]:
        b += f'<circle cx="{pos[0]}" cy="{pos[1]}" r="11" fill="none" stroke="{TEAL}" stroke-width="3"/>'
    b += cartridge(270, 210, 1.1, "", ACC)
    b += f'<rect x="172" y="167" width="50" height="186" rx="8" fill="{TEAL}" opacity=".18"/><rect x="478" y="167" width="50" height="186" rx="8" fill="{TEAL}" opacity=".18"/>'
    b += arrow(80, 330, 80, 190, ACC, 6)
    b += f'<g transform="translate(700,150)"><path d="M0 0 h70 c0 40 -10 60 -35 70 c-25 -10 -35 -30 -35 -70z" fill="#fff" stroke="{RED}" stroke-width="5"/><path d="M35 70 v50 M10 120 h50" stroke="{RED}" stroke-width="6" stroke-linecap="round"/><path d="M20 20 l12 18 l-8 10 l14 12" fill="none" stroke="{RED}" stroke-width="3"/></g>'
    b += f'<g transform="translate(830,160)">' + "".join(f'<path d="M{k*0} {k*0}"/>' for k in range(1)) + "</g>"
    b += f'<rect x="680" y="290" width="200" height="60" rx="8" fill="{AMBER}"/><rect x="680" y="290" width="200" height="14" fill="#c27a14"/>'
    b += check(780, 330, 1.0, "#fff") if False else ""
    b += check(910, 330, 0)
    return svg(960, 420, b, "A cartridge wrapped in bubble wrap and packed snugly upright in a box with cushioning on every side, next to a fragile glass icon")


# ------------------------------------------------------------ 19 warranty remedies
def f_warranty_remedies():
    b = cartridge(70, 160, 1.3, "", ACC)
    b += f'<circle cx="170" cy="155" r="26" fill="{RED}"/>' + text(170, 166, "!", 34, "#fff", 700)
    b += '' and f'<g transform="translate(60,30)"><path d="M0 0 h110 a8 8 0 0 1 8 8 v66 a8 8 0 0 1-8 8 h-110 z" fill="#fff" stroke="{LINE}" stroke-width="2"/><rect x="14" y="14" width="70" height="8" rx="4" fill="{ACC_100}"/><rect x="14" y="32" width="90" height="8" rx="4" fill="{ACC_100}"/><rect x="14" y="50" width="50" height="8" rx="4" fill="{ACC_100}"/></g>'
    rows = ((100, "repair"), (210, "replace"), (320, "refund"))
    for y, k in rows:
        b += f'<path d="M230 205 C 300 205, 320 {y+20}, 400 {y+20}" fill="none" stroke="{ACC}" stroke-width="4" stroke-dasharray="1 9" stroke-linecap="round"/>'
        b += card(410, y - 28, 230, 96, ACC_50 if k == "replace" else "#fff")
        if k == "repair":
            b += wrench(480, y + 8, 1.0, INK2, 40) + cartridge(540, y - 12, .5, "", ACC) 
        elif k == "replace":
            b += cartridge(450, y - 14, .5, "", ACC_D, -8) + arrow(505, y + 14, 545, y + 14, ACC, 4) + cartridge(560, y - 14, .5, "", ACC)
        else:
            b += cartridge(450, y - 14, .5, "", ACC_D) + arrow(505, y + 14, 545, y + 14, ACC, 4) + coin(595, y + 18, 24, AMBER, "$")
    b += doc(740, 140, 130, 150, "#fff", 4, ACC_100) + f'<rect x="755" y="250" width="70" height="8" rx="4" fill="{ACC}"/>'
    b += f'<path d="M648 200 H730" stroke="{FAINT}" stroke-width="4" stroke-dasharray="4 8"/>' + check(805, 232, .0)
    b += check(838, 232, .0)
    return svg(960, 420, b, "A defective cartridge branches into three remedies: repair, replacement or refund, with a receipt as the proof of purchase")


# ------------------------------------------------------------ 20 warranty covered / not
def f_warranty_scope():
    b = card(40, 40, 430, 340, "#fff") + card(490, 40, 430, 340, "#fff")
    b += f'<rect x="40" y="40" width="430" height="46" rx="18" fill="{GREEN}"/><rect x="40" y="60" width="430" height="26" fill="{GREEN}"/>' + check(255, 63, .8, "#fff")
    b += f'<rect x="490" y="40" width="430" height="46" rx="18" fill="{RED}"/><rect x="490" y="60" width="430" height="26" fill="{RED}"/>' + cross(705, 63, .7, "#fff")
    # covered: factory flaw + infinity ribbon
    b += cartridge(120, 150, 1.5, "", ACC) + f'<g transform="translate(280,170)"><circle r="46" cx="40" cy="40" fill="{ACC_50}" stroke="{ACC}" stroke-width="4"/>' + f'<path d="M14 40 c0 -18 24 -18 26 0 c2 18 26 18 26 0 c0 -18 -24 -18 -26 0 c-2 18 -26 18 -26 0z" fill="none" stroke="{ACC}" stroke-width="6"/></g>'
    b += f'<path d="M160 178 l14 18 l-10 10 l16 16" fill="none" stroke="{INK}" stroke-width="3"/>'
    # not covered: dropped, wet, fire
    b += cartridge(520, 190, .7, "", ACC, 28) + f'<path d="M520 130 v40 M560 120 v40" stroke="none"/>'
    b += f'<path d="M590 160 c 24 36 28 50 0 64 c -30 -14 -24 -28 0 -64z" fill="{TEAL}"/>'
    b += f'<path d="M700 235 C 680 205 700 190 700 160 C 724 180 740 200 730 235 C 724 250 706 252 700 235z" fill="{AMBER}"/><path d="M712 240 C 704 228 710 218 714 210 C 722 222 726 232 720 240z" fill="#ffd27a"/>'
    b += cartridge(780, 190, .7, "", ACC_D, -10) + f'<path d="M780 240 l36 -26 l-8 28 l30 -10" stroke="{RED}" stroke-width="5" fill="none" stroke-linecap="round"/>'
    b += f'<rect x="520" y="310" width="360" height="12" rx="6" fill="{LINE}"/>'
    return svg(960, 420, b, "Two panels: a factory defect on a cartridge is covered for life, while damage from a drop, water, fire or a crushed case is not")


FIGURES = {
    "blog-cheap-dream.svg": f_cheap_dream,
    "blog-paperweight.svg": f_paperweight,
    "blog-rabbit-stairs.svg": f_rabbit_stairs,
    "blog-built-it.svg": f_built_it,
    "blog-noise-bugs.svg": f_noise_bugs,
    "blog-iceberg.svg": f_iceberg,
    "blog-bad-archive.svg": f_bad_archive,
    "blog-linux-scripts.svg": f_linux_scripts,
    "blog-tape-dead.svg": f_tape_dead,
    "blog-test-restore.svg": f_test_restore,
    "blog-rogue-drive.svg": f_rogue,
    "blog-home-lto.svg": f_home,
    "blog-used-library.svg": f_library,
    "blog-which-drive.svg": f_which_drive,
    "blog-sas-path.svg": f_sas_path,
    "qa-mainframe.svg": f_mainframe,
    "qa-pyramid.svg": f_pyramid,
    "qa-packaging.svg": f_packaging,
    "qa-warranty-remedies.svg": f_warranty_remedies,
    "qa-warranty-scope.svg": f_warranty_scope,
}

_B = "/blog/"
_Q = "/tape-q-and-a/"
PLACEMENT = [
    {"path": _B + "500-dreams-and-magnetic-tape-fantasies-the-addictive-illusion-of-cheap-lto-storage", "file": "blog-cheap-dream.svg",
     "alt": "A cheap LTO-6 drive with a price tag beside a hole that cartridges are tumbling into.",
     "caption": "A bargain drive looks like a shortcut, but in the story it is the first step into a rabbit hole of tapes and gear.", "w": 960, "h": 400},
    {"path": _B + "6-000-for-a-paperweight-when-enterprise-grade-storage-quietly-fails-you", "file": "blog-paperweight.svg",
     "alt": "An expensive LTO-7 drive showing an error code and resting on loose papers like a paperweight.",
     "caption": "An enterprise price tag did not buy enterprise support, so a dead drive ended up holding down paper.", "w": 960, "h": 400},
    {"path": _B + "buying-a-few-cheap-lto-tapes-is-how-the-rabbit-hole-starts", "file": "blog-rabbit-stairs.svg",
     "alt": "A staircase going down from cartridges to a drive, a SAS card, a catalog and backup software.",
     "caption": "Each cheap cartridge leads to the next purchase and the next question, one step further down.", "w": 960, "h": 420},
    {"path": _B + "i-built-it-because-nothing-else-worked-the-raw-messy-reality-of-reinventing-tape-backup-software", "file": "blog-built-it.svg",
     "alt": "A crossed-out heavy software stack on one side and a terminal feeding a self-describing cartridge on the other.",
     "caption": "When the available tools felt bloated or half-baked, the answer was to write a small one whose tapes describe themselves.", "w": 960, "h": 400},
    {"path": _B + "i-replaced-hard-drives-with-tape-and-accidentally-signed-up-for-a-lifetime-of-noise-bugs-and-obs", "file": "blog-noise-bugs.svg",
     "alt": "A noisy tape drive with sound waves, a bug, and several confusing Linux device names.",
     "caption": "The hardware was the easy part; the noise, the bugs and the device files were what turned tape into a hobby.", "w": 960, "h": 400},
    {"path": _B + "lto-tape-backup-costs-workflow-reality", "file": "blog-iceberg.svg",
     "alt": "An iceberg with one cartridge above the water and a drive, HBA, library, catalog and tools below.",
     "caption": "The cheap cartridge is the visible tip; the drives, adapters, catalogs and cleaning are the part that decides the real cost.", "w": 960, "h": 420},
    {"path": _B + "one-bad-archive-and-it-s-gone-forever-the-brutal-trade-off-nobody-warns-you-about-in-tape-storag", "file": "blog-bad-archive.svg",
     "alt": "Two tape strips, one holding many separate files and one holding a single tar block with a crack.",
     "caption": "Bundling everything into one archive streams well, but a single bad spot can take the whole bundle with it.", "w": 960, "h": 420},
    {"path": _B + "scriptable-linux-tape-backups-still-have-a-process-problem", "file": "blog-linux-scripts.svg",
     "alt": "A script terminal connected by tangled lines to tar, mt, LTFS, checksum, cron and barcode pieces.",
     "caption": "Every script makes sense alone, but together they form a web that only its author can untangle on restore day.", "w": 960, "h": 400},
    {"path": _B + "tape-is-dead-right-then-why-are-people-quietly-building-backup-systems-around-it-again", "file": "blog-tape-dead.svg",
     "alt": "A tombstone reading tape with a green sprout growing from an LTO cartridge in front of it.",
     "caption": "Tape keeps being declared dead, and people keep quietly building backup systems around it anyway.", "w": 960, "h": 400},
    {"path": _B + "the-best-lto-backup-software-is-usually-the-one-youll-actually-test", "file": "blog-test-restore.svg",
     "alt": "Three software options above a cartridge that is restored into a folder and ends in a green check.",
     "caption": "LTFS, tar or a cataloged suite can all work, and the only proof is a restore that actually comes back.", "w": 960, "h": 380},
    {"path": _B + "the-day-my-tape-drive-went-rogue-inside-the-frustrating-reality-of-lto-6-failures", "file": "blog-rogue-drive.svg",
     "alt": "A tape drive caught in a loop of rewinding and ejecting above three suspects marked with question marks.",
     "caption": "The drive clicked, stopped and remounted over and over, and the usual suspects were heads, media and cabling.", "w": 960, "h": 420},
    {"path": _B + "the-home-lto-setup-gets-real-when-you-stop-treating-it-like-a-toy", "file": "blog-home-lto.svg",
     "alt": "A small home shelf with a tape drive and labelled cartridges, a checklist, and a bag carrying a cartridge offsite.",
     "caption": "A home setup becomes real backup when rotation, checks and an offsite copy become routine.", "w": 960, "h": 420},
    {"path": _B + "used-lto-libraries-are-chaos-and-thats-why-people-love-them", "file": "blog-used-library.svg",
     "alt": "A loud secondhand tape library with missing cartridges, a loose drive, a password note and a wrench.",
     "caption": "Decommissioned libraries arrive noisy and fussy, and reviving one is half the appeal.", "w": 960, "h": 410},
    {"path": _B + "which-lto-drive-should-you-buy-without-regretting-it-later", "file": "blog-which-drive.svg",
     "alt": "A drive at a fork in the road with paths to LTO-5, LTO-7 and LTO-9, each ending in a pile of cartridges.",
     "caption": "The generation you pick quietly sets media count, compatibility and how painful growth will be later.", "w": 960, "h": 400},
    {"path": _B + "your-used-lto-8-drive-isnt-broken-until-the-sas-path-stops-lying", "file": "blog-sas-path.svg",
     "alt": "A chain from host to HBA to SAS cable to enclosure to a drive, with a warning on the cable link.",
     "caption": "Before blaming the drive, check every link on the path to it, because the cable or adapter is often the real culprit.", "w": 960, "h": 400},
    {"path": _Q + "mainframe-open-systems-archive", "file": "qa-mainframe.svg",
     "alt": "A mainframe and a stack of open-systems servers feeding one backup disk, then a shared tape archive and a protected copy.",
     "caption": "Both worlds back up into one disk tier and then share one tape archive for long-term retention.", "w": 960, "h": 420},
    {"path": _Q + "multi-tier-data-protection-strategy", "file": "qa-pyramid.svg",
     "alt": "A three-layer pyramid of disk, cloud and tape, with speed rising toward the top and cost falling toward the base.",
     "caption": "Fast recovery sits at the top, durable object storage in the middle and low-cost offline tape at the base.", "w": 960, "h": 420},
    {"path": _Q + "what-are-the-recommended-packaging-practices-for-shipping-enterprise-tape-cartridges-safely-for-return-or-transport", "file": "qa-packaging.svg",
     "alt": "A cartridge wrapped in bubble wrap and packed upright in a snug box, beside a fragile glass icon.",
     "caption": "Wrap each cartridge on every side and fill the box so nothing can shift in transit.", "w": 960, "h": 420},
    {"path": _Q + "what-warranty-coverage-is-typically-offered-for-enterprise-tape-media-cartridges-used-in-backup-and-archival-storage", "file": "qa-warranty-remedies.svg",
     "alt": "A defective cartridge branching into repair, replacement or refund, with a receipt as proof of purchase.",
     "caption": "When a defect qualifies, the vendor usually repairs, replaces or refunds, and the claim starts with proof of purchase.", "w": 960, "h": 420},
    {"path": _Q + "what-warranty-protections-are-commonly-provided-for-enterprise-tape-media-cartridges-used-in-backup-and-archival-storage-systems", "file": "qa-warranty-scope.svg",
     "alt": "Two panels: a factory-defect cartridge marked covered for life, and a dropped, wet or burned cartridge marked not covered.",
     "caption": "The protection is for manufacturing defects, not for damage caused by handling or the environment.", "w": 960, "h": 420},
]
