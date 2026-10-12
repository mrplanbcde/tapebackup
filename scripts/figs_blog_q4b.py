from draw_figures import *
# Figures for the Q4 blog posts on tape security (blog-sec-*) and backup software integration (blog-int-*).


# ------------------------------------------------------------ helpers
def key(x, y, s=1.0, color=ACC):
    """Key lying horizontally, bow at (x, y), about 64x26 at s=1."""
    return (f'<g transform="translate({x},{y}) scale({s})"><circle cx="12" cy="0" r="12" fill="{color}"/><circle cx="12" cy="0" r="5" fill="#fff"/>'
            f'<rect x="22" y="-4" width="42" height="8" rx="3" fill="{color}"/><rect x="48" y="2" width="6" height="11" rx="2" fill="{color}"/>'
            f'<rect x="57" y="2" width="6" height="8" rx="2" fill="{color}"/></g>')


def lock(cx, cy, s=1.0, color=GREEN, body="#fff"):
    """Padlock centred on (cx, cy), about 28x34 at s=1."""
    return (f'<g transform="translate({cx},{cy}) scale({s})"><path d="M-8 -2 v-7 a8 8 0 0 1 16 0 v7" fill="none" stroke="{color}" stroke-width="4"/>'
            f'<rect x="-13" y="-3" width="26" height="20" rx="4" fill="{color}"/><circle cx="0" cy="6" r="3" fill="{body}"/></g>')


def server(x, y, w=140, units=2, col=INK2):
    g = ""
    for i in range(units):
        yy = y + i * 30
        g += f'<rect x="{x}" y="{yy}" width="{w}" height="24" rx="5" fill="{col}"/>'
        g += f'<rect x="{x+12}" y="{yy+9}" width="{w*0.4}" height="6" rx="3" fill="{FAINT}"/><circle cx="{x+w-16}" cy="{yy+12}" r="5" fill="{GREEN}"/>'
    return g


def database(cx, y, w=70, h=74, color=TEAL):
    rx, ry = w / 2, 10
    g = f'<rect x="{cx-rx}" y="{y}" width="{w}" height="{h}" fill="{color}"/>'
    g += f'<ellipse cx="{cx}" cy="{y+h}" rx="{rx}" ry="{ry}" fill="{color}"/>'
    for k in (1, 2):
        g += f'<path d="M{cx-rx} {y+k*h/3} a{rx} {ry} 0 0 0 {w} 0" fill="none" stroke="#fff" stroke-width="3" opacity=".6"/>'
    g += f'<ellipse cx="{cx}" cy="{y}" rx="{rx}" ry="{ry}" fill="#fff" stroke="{color}" stroke-width="3"/>'
    return g


def drive(x, y, w=160, h=52, color=INK2):
    g = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="{color}"/>'
    g += f'<rect x="{x+14}" y="{y+16}" width="{w*0.5}" height="10" rx="4" fill="{INK}"/>'
    g += f'<rect x="{x+14}" y="{y+33}" width="{w*0.22}" height="6" rx="3" fill="{FAINT}"/>'
    return g + lock(x + w - 26, y + 24, .8, GREEN, color)


def pill(cx, cy, w, label, fill="#fff", col=INK, border=LINE, size=16, h=30):
    return (f'<rect x="{cx-w/2}" y="{cy-h/2}" width="{w}" height="{h}" rx="{h/2}" fill="{fill}" stroke="{border}" stroke-width="2"/>'
            + text(cx, cy + size * 0.36, label, size, col, 700))


def library(x, y, w=230, h=300):
    g = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{INK2}"/>'
    g += f'<rect x="{x+14}" y="{y+14}" width="{w-28}" height="{h-110}" rx="8" fill="{INK}"/>'
    rows, cols = 5, 6
    sw = (w - 48) / cols
    for r in range(rows):
        for c in range(cols):
            col = ACC if (r * 2 + c) % 5 else ACC_100
            g += f'<rect x="{x+24+c*sw:.1f}" y="{y+26+r*((h-134)/rows):.1f}" width="{sw-6:.1f}" height="{(h-134)/rows-8:.1f}" rx="3" fill="{col}"/>'
    g += f'<rect x="{x+14}" y="{y+h-84}" width="{w-28}" height="8" rx="4" fill="{FAINT}"/>'
    g += f'<rect x="{x+w/2-18}" y="{y+h-92}" width="36" height="24" rx="5" fill="{TEAL}"/>'
    for k in range(2):
        g += f'<rect x="{x+20+k*((w-40)/2)}" y="{y+h-60}" width="{(w-40)/2-8}" height="40" rx="6" fill="{INK}"/>'
        g += f'<circle cx="{x+20+(k+1)*((w-40)/2)-24}" cy="{y+h-40}" r="5" fill="{GREEN}"/>'
    return g


def arm(cx, cy, color=ACC):
    """Robot picker: rail, carriage and gripper."""
    return (f'<rect x="{cx-26}" y="{cy-22}" width="52" height="8" rx="4" fill="{INK2}"/><rect x="{cx-10}" y="{cy-16}" width="20" height="20" rx="4" fill="{color}"/>'
            f'<rect x="{cx-3}" y="{cy+2}" width="6" height="12" fill="{color}"/><path d="M{cx-14} {cy+24} v-10 h28 v10" fill="none" stroke="{color}" stroke-width="5" stroke-linecap="round"/>')


def col_title(cx, s):
    return text(cx, 62, s, 20, INK, 700)


# ------------------------------------------------------------ figures
def f_key_models():
    xs = (30, 340, 650)
    b = ""
    for i, x in enumerate(xs):
        b += card(x, 24, 280, 412, ACC_50 if i == 1 else "#fff")
    # shared bottom: drive + cartridge + AES tag
    for x in xs:
        b += drive(x + 22, 318) + cartridge(x + 200, 320, .52, "", ACC)
        b += f'<rect x="{x+42}" y="384" width="120" height="32" rx="16" fill="{GREEN}"/>' + lock(x + 62, 397, .6, "#fff", GREEN)
        b += text(x + 112, 406, "AES-256", 16, "#fff", 700)
    # 1 application-managed
    cx = 170
    b += col_title(cx, "Application-managed")
    b += server(cx - 85, 92, 140, 3) + key(cx + 66, 122, .8)
    b += text(cx, 200, "Backup software", 17, INK2, 600)
    b += arrow(cx, 216, cx, 304, ACC, 4) + key(cx + 14, 254, .7)
    # 2 library-managed
    cx = 480
    b += col_title(cx, "Library-managed")
    b += database(cx - 60, 88, 64, 60) + key(cx - 82, 168, .7, ACC)
    b += text(cx - 60, 204, "Key manager", 16, INK2, 600)
    b += server(cx + 18, 98, 96, 2) + text(cx + 66, 204, "Backup", 16, INK2, 600)
    b += key(cx + 44, 168, .7, FAINT) + f'<path d="M{cx+58} 158 l20 20 M{cx+78} 158 l-20 20" stroke="{RED}" stroke-width="4" stroke-linecap="round"/>'
    b += f'<rect x="{cx-128}" y="262" width="256" height="114" rx="14" fill="none" stroke="{ACC}" stroke-width="3" stroke-dasharray="7 6"/>'
    b += text(cx - 114, 290, "Library", 16, ACC_D, 700, "start")
    b += arrow(cx - 60, 214, cx - 60, 256, ACC, 4) + pill(cx + 10, 234, 70, "KMIP", "#fff", ACC_D, ACC_100, 15, 28)
    # 3 system-managed
    cx = 790
    b += col_title(cx, "System-managed")
    b += database(cx - 50, 86, 60, 52) + key(cx + 4, 112, .7)
    b += text(cx - 20, 176, "Key manager", 16, INK2, 600)
    b += arrow(cx - 50, 186, cx - 50, 212, ACC, 4)
    b += f'<rect x="{cx-110}" y="216" width="120" height="40" rx="8" fill="{INK2}"/>' + text(cx - 50, 242, "Host driver", 16, "#fff", 700)
    b += pill(cx + 70, 236, 100, "IBM drivers", "#fff", TEAL, TEAL, 15, 28)
    b += arrow(cx - 50, 262, cx - 50, 304, ACC, 4)
    return svg(960, 460, b, "Three ways to manage LTO encryption keys: application, library and system managed")


def f_features_by_gen():
    heads = (("WORM",), ("AES-256", "encryption"), ("LTFS", "partitions"), ("Offline when", "ejected"))
    start = (3, 4, 5, 3)
    x0, y0, cw, ch = 210, 102, 178, 41
    b = ""
    for j, h in enumerate(heads):
        cx = x0 + j * cw + cw / 2
        if len(h) == 1:
            b += text(cx, 72, h[0], 18, INK, 700)
        else:
            b += text(cx, 60, h[0], 18, INK, 700) + text(cx, 84, h[1], 16, MUTED, 600)
    for i in range(8):
        g = 3 + i
        y = y0 + i * ch
        b += f'<rect x="40" y="{y}" width="880" height="{ch-4}" rx="10" fill="{"#fff" if i % 2 == 0 else SURF2}"/>'
        b += text(70, y + 25, f"LTO-{g}", 18, INK, 700, "start", MONO)
        for j in range(4):
            cx = x0 + j * cw + cw / 2
            cy = y + (ch - 4) / 2
            if g >= start[j]:
                col = INK2 if j == 3 else ACC
                b += f'<rect x="{cx-50}" y="{cy-14}" width="100" height="28" rx="14" fill="{col}"/>'
                b += f'<path d="M{cx-9} {cy} l6 6 l12 -12" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'
            else:
                b += f'<rect x="{cx-50}" y="{cy-14}" width="100" height="28" rx="14" fill="none" stroke="{FAINT}" stroke-width="2" stroke-dasharray="5 5"/>'
    return svg(960, 450, b, "WORM from LTO-3, AES-256 encryption from LTO-4, LTFS partitions from LTO-5")


def f_software_map():
    soft = (("Veeam", ""), ("Commvault", ""), ("Nakivo", ""), ("Bacula / Bareos", "open source"), ("LTFS tools", "no catalogue"))
    b = ""
    bus = 360
    for i, (name, tagl) in enumerate(soft):
        y = 52 + i * 74
        cy = y + 29
        b += card(30, y, 300, 58)
        b += text(52, cy + 7, name, 19, INK, 700, "start")
        if tagl:
            col = GREEN if tagl == "open source" else RED
            b += pill(268, cy, 112, tagl, "#fff", col, col, 15, 28)
        dash = ' stroke-dasharray="6 7"' if name == "LTFS tools" else ""
        b += f'<line x1="330" y1="{cy}" x2="{bus}" y2="{cy}" stroke="{FAINT if dash else ACC}" stroke-width="4" stroke-linecap="round"{dash}/>'
    b += f'<line x1="{bus}" y1="81" x2="{bus}" y2="377" stroke="{ACC}" stroke-width="4" stroke-linecap="round"/>'
    lanes = ("Library control", "Catalogue", "Tape format")
    for k, lab in enumerate(lanes):
        y = 74 + k * 116
        cy = y + 41
        b += card(404, y, 230, 82, ACC_50)
        b += arrow(bus, cy, 396, cy, ACC, 4)
        ix = 442
        if k == 0:
            b += arm(ix, cy)
        elif k == 1:
            b += database(ix, cy - 20, 40, 36, ACC)
        else:
            b += cartridge(ix - 21, cy - 19, .42, "", ACC)
        b += text(474, cy + 7, lab, 19, INK, 700, "start")
        b += arrow(634, cy, 680, cy, FAINT, 4)
    b += card(690, 40, 240, 380)
    b += library(705, 62, 210, 300)
    b += text(810, 398, "LTO library", 18, INK, 700)
    return svg(960, 460, b, "Backup software must handle library control, the catalogue and the tape format")


def f_tradeoffs():
    x0, x1, y0, y1 = 150, 910, 40, 370
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    b = f'<rect x="{x0}" y="{y0}" width="{mx-x0}" height="{my-y0}" fill="{ACC}" opacity=".07"/>'
    b += f'<rect x="{mx}" y="{y0}" width="{x1-mx}" height="{my-y0}" fill="{GREEN}" opacity=".09"/>'
    b += f'<rect x="{x0}" y="{my}" width="{mx-x0}" height="{y1-my}" fill="{FAINT}" opacity=".10"/>'
    b += f'<rect x="{mx}" y="{my}" width="{x1-mx}" height="{y1-my}" fill="{TEAL}" opacity=".08"/>'
    b += f'<line x1="{mx}" y1="{y0}" x2="{mx}" y2="{y1}" stroke="{LINE}" stroke-width="2" stroke-dasharray="6 6"/>'
    b += f'<line x1="{x0}" y1="{my}" x2="{x1}" y2="{my}" stroke="{LINE}" stroke-width="2" stroke-dasharray="6 6"/>'
    b += arrow(x0, y1, x1 + 24, y1, INK2, 3) + arrow(x0, y1, x0, y0 - 16, INK2, 3)
    b += text(x0 + 4, y1 + 26, "low", 15, MUTED, 600, "start") + text(x1 + 20, y1 + 26, "high", 15, MUTED, 600, "end")
    b += text(mx, y1 + 66, "Restore without the software", 18, INK, 700)
    b += text(x0 - 12, y1 - 8, "low", 15, MUTED, 600, "end") + text(x0 - 12, y0 + 6, "high", 15, MUTED, 600, "end")
    b += f'<g transform="rotate(-90 70 {my})">' + text(70, my + 6, "Built-in automation and catalogue", 18, INK, 700) + "</g>"
    pts = ((240, 110, ACC, ("Commercial suite", "own tape format")),
           (620, 110, GREEN, ("Suite writing LTFS",)),
           (210, 232, INK2, ("Open source", "Bacula, Bareos")),
           (640, 304, TEAL, ("LTFS with tar or copy",)))
    for x, y, c, lab in pts:
        b += f'<circle cx="{x}" cy="{y}" r="22" fill="{c}" opacity=".22"/><circle cx="{x}" cy="{y}" r="11" fill="{c}"/>'
        if len(lab) == 1:
            b += text(x + 34, y + 7, lab[0], 18, INK, 700, "start")
        else:
            b += text(x + 34, y - 4, lab[0], 18, INK, 700, "start") + text(x + 34, y + 20, lab[1], 16, MUTED, 600, "start")
    return svg(960, 460, b, "Backup approaches by built-in automation and by restore without the original software")


FIGURES = {
    "blog-sec-key-models.svg": f_key_models,
    "blog-sec-features-by-gen.svg": f_features_by_gen,
    "blog-int-software-map.svg": f_software_map,
    "blog-int-tradeoffs.svg": f_tradeoffs,
}

PLACEMENT = []
