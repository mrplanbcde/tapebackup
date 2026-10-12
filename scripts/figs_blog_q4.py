from draw_figures import *
"""Chart figures for the Q4 2026 English blog posts (value, TCO, energy).

All prices are US seller-listing midpoints, September 2026. Every number drawn
comes from the post data; axes carry no tick values on purpose.
"""
import math

GLACIER = "#cfe3ea"   # light teal-grey for cloud storage
GLACIER_D = "#2d6f88"  # text on / about it


# ------------------------------------------------------------ small icons
def i_drive(x, y, s=1.0, color=INK2):
    w, h = 64 * s, 30 * s
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{6*s}" fill="{color}"/>'
            f'<rect x="{x+8*s}" y="{y+9*s}" width="{34*s}" height="{7*s}" rx="{2*s}" fill="{INK}"/>'
            f'<circle cx="{x+w-11*s}" cy="{y+12*s}" r="{4*s}" fill="{GREEN}"/>')


def i_library(x, y, s=1.0, color=INK):
    g = f'<rect x="{x}" y="{y}" width="{56*s}" height="{64*s}" rx="{6*s}" fill="{color}"/>'
    for r in range(3):
        g += f'<rect x="{x+6*s}" y="{y+7*s+r*19*s}" width="{44*s}" height="{14*s}" rx="{3*s}" fill="{INK2}"/>'
        for k in range(4):
            g += f'<rect x="{x+10*s+k*10*s}" y="{y+10*s+r*19*s}" width="{7*s}" height="{8*s}" rx="{1.5*s}" fill="{ACC if (r + k) % 3 else ACC_100}"/>'
    return g


def i_soft(x, y, s=1.0, color=INK2):
    g = f'<rect x="{x}" y="{y}" width="{62*s}" height="{50*s}" rx="{7*s}" fill="#fff" stroke="{color}" stroke-width="{3.5*s}"/>'
    g += f'<rect x="{x}" y="{y}" width="{62*s}" height="{12*s}" rx="{6*s}" fill="{color}"/>'
    for k in range(3):
        g += f'<rect x="{x+9*s}" y="{y+19*s+k*9*s}" width="{(40-k*10)*s}" height="{5*s}" rx="{2.5*s}" fill="{ACC_100}"/>'
    return g


def i_bolt(cx, cy, s=1.0, color=AMBER):
    return f'<path d="M{cx+4*s} {cy-26*s} L{cx-16*s} {cy+4*s} H{cx-1*s} L{cx-6*s} {cy+26*s} L{cx+16*s} {cy-6*s} H{cx+1*s} Z" fill="{color}"/>'


def i_van(x, y, s=1.0, color=TEAL):
    return (f'<g transform="translate({x},{y}) scale({s})"><rect width="50" height="30" rx="5" fill="{color}"/>'
            f'<path d="M50 8 h14 l10 11 v11 h-24 z" fill="{INK2}"/><circle cx="14" cy="32" r="7" fill="{INK}"/><circle cx="60" cy="32" r="7" fill="{INK}"/></g>')


def i_person(cx, y, s=1.0, color=INK2):
    return (f'<circle cx="{cx}" cy="{y+13*s}" r="{12*s}" fill="{color}"/>'
            f'<path d="M{cx-22*s} {y+52*s} a{22*s} {22*s} 0 0 1 {44*s} 0 z" fill="{color}"/>')


def i_migrate(x, y, s=1.0):
    g = cartridge(x, y + 6 * s, .34 * s, "", FAINT) + cartridge(x + 50 * s, y + 6 * s, .34 * s, "", ACC)
    g += f'<path d="M{x+14*s} {y+2*s} C{x+24*s} {y-14*s} {x+56*s} {y-14*s} {x+66*s} {y}" stroke="{INK2}" stroke-width="{4*s}" fill="none" stroke-linecap="round"/>'
    g += f'<path d="M{x+58*s} {y-2*s} l{9*s} {3*s} l{1*s} {-10*s}" stroke="{INK2}" stroke-width="{4*s}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
    return g


def legend(items, x, y, gap=34):
    """items: (label, fill, extra-attrs) laid out left to right; returns svg."""
    g, cx = "", x
    for lab, fill, extra in items:
        g += f'<rect x="{cx}" y="{y-16}" width="22" height="22" rx="6" fill="{fill}"{extra}/>' + text(cx + 30, y + 1, lab, 17, INK, 700, "start")
        cx += 30 + len(lab) * 9.6 + gap
    return g


HATCH = (f'<defs><pattern id="hatchR" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
         f'<rect width="9" height="9" fill="#fff"/><rect width="4" height="9" fill="{RED}" opacity=".55"/></pattern></defs>')


# ------------------------------------------------------------ 1. cost per TB
def fig_cost_per_tb():
    sizes = (50, 100, 250, 500, 1000, 2000)
    series = (("LTO-8", TEAL, (136.99, 71.49, 32.20, 32.20, 19.25, 12.73)),
              ("LTO-9", ACC, (218.11, 112.11, 48.11, 48.11, 26.91, 16.31)),
              ("LTO-10", INK2, (482.27, 246.69, 104.24, 103.68, 56.57, 32.87)))
    y_top, y_bot, lo, hi = 92, 362, 10, 560
    Y = lambda v: y_bot - (math.log10(v) - math.log10(lo)) / (math.log10(hi) - math.log10(lo)) * (y_bot - y_top)
    X = lambda i: 150 + i * 132
    b = text(40, 48, "$ per TB", 20, INK, 700, "start") + text(140, 48, "log scale", 16, MUTED, 600, "start")
    b += legend([(n, c, "") for n, c, _ in series], 560, 48)
    b += card(40, 72, 880, 316)
    for v in (10, 20, 50, 100, 200, 500):
        b += f'<line x1="70" y1="{Y(v):.1f}" x2="890" y2="{Y(v):.1f}" stroke="{SURF2}" stroke-width="2"/>'
    # two drives from 500 TB
    b += f'<rect x="{X(3)-30}" y="{y_top-6}" width="{X(5)-X(3)+60}" height="{y_bot-y_top+12}" rx="12" fill="{ACC_50}"/>'
    b += f'<line x1="{X(3)-30}" y1="{y_top-6}" x2="{X(3)-30}" y2="{y_bot+6}" stroke="{ACC_100}" stroke-width="3" stroke-dasharray="6 6"/>'
    b += text(X(5) + 20, y_top + 18, "two drives", 16, ACC_D, 700, "end")
    for i, s in enumerate(sizes):
        b += text(X(i), 416, f"{s:,} TB", 17, INK2, 700)
    for n, col, vals in series:
        pts = " ".join(f"{X(i)},{Y(v):.1f}" for i, v in enumerate(vals))
        b += f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="4.5" stroke-linejoin="round" stroke-linecap="round"/>'
        for i, v in enumerate(vals):
            b += f'<circle cx="{X(i)}" cy="{Y(v):.1f}" r="6.5" fill="#fff" stroke="{col}" stroke-width="4"/>'
    # value labels at 50 TB (left), 500 TB (on the flat 250-500 run) and 2000 TB (right)
    for n, col, vals in series:
        b += text(X(0) - 14, Y(vals[0]) + 6, f"${vals[0]:.2f}", 16, col, 700, "end")
        dy = 26 if n == "LTO-8" else -14
        b += text(X(3) - 16, Y(vals[3]) + dy, f"${vals[3]:.2f}", 16, col, 700, "end")
    for (n, col, vals), dy in zip(series, (14, -4, 0)):
        b += text(X(5) + 14, Y(vals[5]) + 6 + dy, f"${vals[5]:.2f}", 16, col, 700, "start")
    return svg(960, 440, b, "Total cost per TB stored for LTO-8, LTO-9 and LTO-10 at 50 to 2,000 TB, September 2026")


# ------------------------------------------------------------ 2. media vs drive
def fig_media_vs_drive():
    rows = (("LTO-6", "", 15.20, 22.58), ("LTO-7", "", 10.00, 13.33), ("LTO-8", "", 5.83, 6.67),
            ("LTO-9", "", 5.14, 6.20), ("LTO-10", "30 TB", 8.53, 10.00), ("LTO-10", "40 TB", 12.28, 13.88))
    b = card(30, 30, 560, 400) + card(620, 30, 310, 400)
    b += text(56, 72, "Media $ per TB", 20, INK, 700, "start")
    b += text(646, 72, "Drive price", 20, INK, 700, "start")
    x0, sc = 176, 15.0   # $0 at x0, px per dollar
    b += f'<line x1="{x0}" y1="96" x2="{x0}" y2="408" stroke="{LINE}" stroke-width="2"/>'
    for i, (g, sub, lo, hi) in enumerate(rows):
        y = 100 + i * 52
        best = g == "LTO-9"
        if best:
            b += f'<rect x="44" y="{y}" width="532" height="46" rx="10" fill="{ACC_50}"/>'
        if sub:
            b += text(56, y + 21, g, 17, INK, 700, "start") + text(56, y + 40, sub, 15, MUTED, 600, "start")
        else:
            b += text(56, y + 30, g, 17, INK, 700, "start")
        xa, xb = x0 + lo * sc, x0 + hi * sc
        col = ACC if best else ("#b9b5c6" if not g.startswith("LTO-10") else INK2)
        b += f'<rect x="{xa:.1f}" y="{y+11}" width="{xb-xa:.1f}" height="24" rx="8" fill="{col}"/>'
        lab = f"${lo:.2f} to ${hi:.2f}"
        if xb + 12 + len(lab) * 8.4 < 572:
            b += text(xb + 12, y + 29, lab, 15, ACC_D if best else INK2, 700, "start")
        else:
            b += text(xa - 12, y + 29, lab, 15, INK2, 700, "end")
        if best:
            b += f'<rect x="{xb+150}" y="{y+10}" width="76" height="26" rx="13" fill="{GREEN}"/>' + text(xb + 188, y + 28, "lowest", 15, "#fff", 700)
    # drives
    base, k = 380, 230 / 23558
    for i, (g, v, col) in enumerate((("LTO-8", 6474, TEAL), ("LTO-9", 10600, ACC), ("LTO-10", 23558, INK2))):
        cx = 676 + i * 100
        h = v * k
        b += f'<rect x="{cx-30}" y="{base-h:.1f}" width="60" height="{h:.1f}" rx="10" fill="{col}"/>'
        b += text(cx, base - h - 12, f"${v:,}", 17, col, 700) + text(cx, base + 30, g, 17, INK, 700)
    b += f'<line x1="640" y1="{base}" x2="912" y2="{base}" stroke="{LINE}" stroke-width="3"/>'
    b += text(876, base - 52, "full", 15, "#fff", 700) + text(876, base - 32, "height", 15, "#fff", 700)
    return svg(960, 460, b, "LTO media cost per TB by generation, and LTO-8, LTO-9 and LTO-10 drive prices, September 2026")


# ------------------------------------------------------------ 3. five-year TCO
def fig_tco_5yr():
    groups = (("100 TB", (7824, 11824, 25781), 5532, 8615),
              ("500 TB", (19247, 26911, 56567), 27660, 43074),
              ("1,000 TB", (25545, 32623, 66019), 55321, 86147))
    cols = (TEAL, ACC, INK2)
    base, k = 384, 262 / 141468
    K = lambda v: f"${v/1000:.1f}K"
    b = HATCH
    b += legend([("LTO-8", TEAL, ""), ("LTO-9", ACC, ""), ("LTO-10", INK2, ""),
                 ("Glacier", GLACIER, f' stroke="{GLACIER_D}" stroke-width="1.5"'),
                 ("restore", "url(#hatchR)", f' stroke="{RED}" stroke-width="2"')], 40, 44, 26)
    b += text(920, 44, "two copies", 16, MUTED, 600, "end")
    b += f'<line x1="40" y1="{base}" x2="920" y2="{base}" stroke="{LINE}" stroke-width="3"/>'
    bw, pitch = 52, 62
    for gi, (lab, tape, gl, rs) in enumerate(groups):
        gx = 82 + gi * 290
        if gi:
            b += f'<line x1="{gx-30}" y1="90" x2="{gx-30}" y2="{base}" stroke="{SURF2}" stroke-width="2"/>'
        for j, v in enumerate(tape):
            x = gx + j * pitch
            h = v * k
            b += f'<rect x="{x}" y="{base-h:.1f}" width="{bw}" height="{h:.1f}" rx="8" fill="{cols[j]}"/>'
            b += text(x + bw / 2, base - h - 10, K(v), 15, cols[j], 700)
        x = gx + 3 * pitch
        hs, hr = gl * k, rs * k
        b += f'<rect x="{x}" y="{base-hs-hr:.1f}" width="{bw}" height="{hr:.1f}" rx="8" fill="url(#hatchR)" stroke="{RED}" stroke-width="2.5"/>'
        b += f'<rect x="{x}" y="{base-hs:.1f}" width="{bw}" height="{hs:.1f}" rx="6" fill="{GLACIER}" stroke="{GLACIER_D}" stroke-width="1.5"/>'
        ly = min(base - hs - hr - 10, base - tape[2] * k - 34)
        b += text(x + bw / 2, ly - 20, "+" + K(rs), 15, RED, 700)
        b += text(x + bw / 2, ly, K(gl), 15, GLACIER_D, 700)
        if base - hs - hr - ly > 24:
            b += f'<line x1="{x+bw/2}" y1="{ly+8}" x2="{x+bw/2}" y2="{base-hs-hr-6:.1f}" stroke="{FAINT}" stroke-width="2" stroke-dasharray="3 4"/>'

        b += text(gx + (3 * pitch + bw) / 2, base + 32, lab, 19, INK, 700)
    return svg(960, 440, b, "Five-year cost of LTO-8, LTO-9 and LTO-10 with two copies against Glacier Deep Archive plus one full restore")


# ------------------------------------------------------------ 4. TCO components
def fig_tco_components():
    b = card(30, 30, 270, 390, ACC_50)
    b += f'<rect x="58" y="50" width="214" height="34" rx="17" fill="{ACC}"/>' + text(165, 73, "in our numbers", 16, "#fff", 700)
    # solid blocks
    b += f'<rect x="58" y="104" width="214" height="146" rx="14" fill="{ACC}"/>'
    b += i_drive(133, 136, 1.0, "#fff").replace(f'fill="{INK}"', f'fill="{ACC_100}"') + text(165, 222, "Drives", 20, "#fff", 700)
    b += f'<rect x="58" y="262" width="214" height="146" rx="14" fill="{ACC_D}"/>'
    b += cartridge(137, 282, .56, "", ACC_100) + text(165, 380, "Cartridges", 20, "#fff", 700)
    # dashed blocks
    b += f'<rect x="330" y="30" width="600" height="390" rx="18" fill="#fff" stroke="{LINE}" stroke-width="2"/>'
    b += f'<rect x="356" y="50" width="214" height="34" rx="17" fill="#fff" stroke="{MUTED}" stroke-width="2" stroke-dasharray="5 4"/>'
    b += text(463, 73, "not in our numbers", 16, MUTED, 700)
    items = (("Library", lambda cx, cy: i_library(cx - 28, cy - 34)),
             ("Software", lambda cx, cy: i_soft(cx - 31, cy - 25)),
             ("Power", lambda cx, cy: i_bolt(cx, cy)),
             ("Offsite", lambda cx, cy: i_van(cx - 37, cy - 20)),
             ("Staff time", lambda cx, cy: i_person(cx, cy - 28)),
             ("Migration", lambda cx, cy: i_migrate(cx - 41, cy - 12)))
    for i, (lab, icon) in enumerate(items):
        x = 356 + (i % 3) * 190
        y = 104 + (i // 3) * 158
        b += f'<rect x="{x}" y="{y}" width="172" height="146" rx="14" fill="{SURF}" stroke="{FAINT}" stroke-width="2.5" stroke-dasharray="8 6"/>'
        b += icon(x + 86, y + 58)
        b += text(x + 86, y + 124, lab, 18, INK2, 700)
    return svg(960, 450, b, "What goes into five-year tape TCO: drives and cartridges are counted, library, software, power, offsite, staff and migration are not")


# ------------------------------------------------------------ 5. energy kWh
def fig_energy_kwh():
    rows = (("Disk array, always on", 4415, INK2, lambda y: hdd(50, y + 1, .45)),
            ("Tape library, always on", 804, ACC, lambda y: i_library(44, y - 4, .8)),
            ("Standalone tape drive, on only while writing", 16, TEAL, lambda y: i_drive(40, y + 12, .9)),
            ("Cloud archive", None, GLACIER_D, lambda y: cloud(36, y + 2, .5)))
    x0, ppd = 140, 178.0   # 1 kWh at x0, px per decade
    b = text(40, 50, "kWh per year, 500 TB", 20, INK, 700, "start") + text(920, 50, "log scale", 16, MUTED, 600, "end")
    for i, (lab, v, col, icon) in enumerate(rows):
        y = 78 + i * 90
        b += card(30, y - 8, 900, 80)
        b += icon(y)
        b += text(x0, y + 20, lab, 17, INK, 700, "start")
        if v is None:
            b += f'<rect x="{x0}" y="{y+32}" width="360" height="26" rx="8" fill="none" stroke="{GLACIER_D}" stroke-width="2.5" stroke-dasharray="8 6"/>'
            b += text(x0 + 180, y + 51, "in the provider's bill", 15, GLACIER_D, 700)
        else:
            w = math.log10(v) * ppd
            b += f'<rect x="{x0}" y="{y+32}" width="{w:.1f}" height="26" rx="8" fill="{col}"/>'
            b += text(x0 + w + 12, y + 52, f"{v:,} kWh", 18, col, 700, "start")
    return svg(960, 440, b, "Modelled energy per year for a 500 TB archive: disk array 4,415 kWh, tape library 804 kWh, standalone drive 16 kWh")


# ------------------------------------------------------------ 6. operating cost
def fig_energy_opcost():
    rows = (("Cloud archive storage bill", 5532, TEAL, lambda y: cloud(36, y + 2, .5)),
            ("Disk array power", 574, INK2, lambda y: hdd(50, y + 1, .45)),
            ("Tape library power", 105, ACC, lambda y: i_library(44, y - 4, .8)),
            ("Standalone drive power", 2, ACC_D, lambda y: i_drive(40, y + 12, .9)))
    x0, k = 140, 640 / 5532
    b = text(40, 50, "Operating cost per year, 500 TB", 20, INK, 700, "start")
    for i, (lab, v, col, icon) in enumerate(rows):
        y = 78 + i * 90
        b += card(30, y - 8, 900, 80)
        b += icon(y)
        b += text(x0, y + 20, lab, 17, INK, 700, "start")
        w = max(v * k, 6)
        b += f'<rect x="{x0}" y="{y+32}" width="{w:.1f}" height="26" rx="{min(8, w/2):.1f}" fill="{col}"/>'
        b += text(x0 + w + 12, y + 52, f"${v:,}", 18, col, 700, "start")
    return svg(960, 440, b, "Operating cost per year for 500 TB: cloud archive $5,532, disk power $574, tape library power $105, standalone drive power $2")


FIGURES = {
    "blog-value-cost-per-tb.svg": fig_cost_per_tb,
    "blog-value-media-vs-drive.svg": fig_media_vs_drive,
    "blog-tco-5yr.svg": fig_tco_5yr,
    "blog-tco-components.svg": fig_tco_components,
    "blog-energy-kwh.svg": fig_energy_kwh,
    "blog-energy-opcost.svg": fig_energy_opcost,
}

PLACEMENT = []
