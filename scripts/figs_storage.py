"""Figures for the LTO storage pages (docs/seo/lto-storage-keyword-plan-2026-10.md):
/lto-storage, /resources/how-to-store-lto-tapes, /resources/owc-lto-tape-drives and
/comparisons/lto-vs-object-storage. The pages place them with site_shell.figure(), so
PLACEMENT stays empty. Text is limited to units, product names and technical tokens.
"""

from draw_figures import *
from figs_guides import chip, drv, server


def _reel(cx, cy, r, col=INK2):
    b = f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{col}"/><circle cx="{cx}" cy="{cy}" r="{r*.72}" fill="#3a3550"/>'
    b += f'<circle cx="{cx}" cy="{cy}" r="{r*.26}" fill="{SURF2}"/>'
    for i in range(3):
        b += f'<circle cx="{cx}" cy="{cy}" r="{r*(.38+i*.11)}" fill="none" stroke="#fff" stroke-width="1.5" opacity=".18"/>'
    return b


def fig_how_it_works():
    """Cartridge reel -> tape past the head -> serpentine wraps across the tape width, between servo bands."""
    b = card(30, 40, 250, 340)
    b += cartridge(80, 70, 1.5, "LTO-9")
    b += _reel(155, 300, 52)
    b += f'<path d="M207 300 C 300 300, 320 160, 400 160" fill="none" stroke="{INK2}" stroke-width="8" stroke-linecap="round"/>'
    # drive head
    b += f'<rect x="390" y="118" width="70" height="84" rx="12" fill="{ACC}"/><rect x="404" y="132" width="42" height="56" rx="6" fill="#fff" opacity=".9"/>'
    for i in range(4):
        b += f'<rect x="{410 + i*8}" y="140" width="4" height="40" rx="2" fill="{ACC_D}"/>'
    b += f'<path d="M460 160 H500" stroke="{INK2}" stroke-width="8" stroke-linecap="round"/>'
    # tape strip with servo bands and data bands written back and forth
    x0, x1, y0 = 510, 920, 70
    b += f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="280" rx="10" fill="#3a3550"/>'
    for i in range(5):
        y = y0 + 12 + i * 63
        b += f'<rect x="{x0+8}" y="{y}" width="{x1-x0-16}" height="7" rx="3" fill="{AMBER}" opacity=".9"/>'
    for band in range(4):
        top = y0 + 26 + band * 63
        for w in range(4):
            y = top + 6 + w * 10
            right = w % 2 == 0
            col = ACC_100 if band != 1 else "#fff"
            b += f'<line x1="{x0+24}" y1="{y}" x2="{x1-24}" y2="{y}" stroke="{col}" stroke-width="4" stroke-linecap="round" opacity="{.95 if band == 1 else .45}"/>'
            hx = x1 - 30 if right else x0 + 30
            dx = 12 if right else -12
            b += f'<polygon points="{hx},{y-6} {hx+dx},{y} {hx},{y+6}" fill="{col}" opacity="{.95 if band == 1 else .45}"/>'
    b += chip(715, 395, "servo", 110, fill="#fff", col=AMBER, size=17)
    return svg(960, 430, b, "An LTO cartridge holds one reel of tape; the drive pulls it past the head, which writes bands of parallel tracks back and forth along the tape between prerecorded servo bands")


def fig_storage_system():
    """Server -> SAS/FC/Thunderbolt -> drive or library -> cartridges -> offsite copy."""
    b = card(30, 60, 190, 300) + server(70, 110, 110) + server(70, 190, 110)
    b += chip(125, 300, "LTFS", 96, fill=ACC_50, col=ACC_D, size=17)
    b += arrow(228, 210, 300, 210, ACC, 5)
    b += chip(264, 252, "SAS/FC", 80, size=13)
    b += card(306, 60, 250, 300, ACC_50)
    b += drv(336, 96, 190, 64)
    for i in range(3):
        for j in range(2):
            b += cartridge(338 + i * 64, 186 + j * 78, .5, "L9" if i == 0 and j == 0 else "", ACC if (i + j) % 2 == 0 else ACC_D)
    b += arrow(564, 210, 636, 210, ACC, 5)
    b += card(642, 60, 130, 300)
    for j in range(3):
        b += cartridge(668, 86 + j * 88, .78, "", ACC)
    b += arrow(780, 210, 836, 210, FAINT, 5, "2 10")
    b += shield(846, 140, 1.2) + f'<path d="M842 262 l40 -26 l40 26 v52 h-80 z" fill="{INK2}"/><rect x="868" y="282" width="28" height="32" rx="4" fill="#fff" opacity=".8"/>'
    b += chip(882, 352, "offsite", 110, size=16)
    return svg(960, 420, b, "An LTO storage system: a server with backup or LTFS software, a SAS or Fibre Channel link, a drive or library, the cartridges, and a second copy kept offsite")


def fig_access_vs_cost():
    """Time to first byte (log, left = fast) against storage cost per TB-month (log, up = dear); schematic, no prices."""
    x0, x1, y0, y1 = 120, 900, 60, 340
    b = f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" rx="14" fill="#fff" stroke="{LINE}" stroke-width="2"/>'
    ticks = [("ms", 0.04), ("s", 0.22), ("min", 0.42), ("h", 0.66), ("days", 0.9)]
    for lab, f in ticks:
        x = x0 + f * (x1 - x0)
        b += f'<line x1="{x}" y1="{y0+10}" x2="{x}" y2="{y1-10}" stroke="{SURF2}" stroke-width="2"/>' + text(x, y1 + 30, lab, 17, MUTED, 700, font=MONO)
    b += arrow(x0, y1 + 56, x1, y1 + 56, FAINT, 3)
    b += arrow(70, y1, 70, y0, FAINT, 3) + text(52, (y0 + y1) / 2, "$/TB", 16, MUTED, 700, font=MONO).replace("<text ", f'<text transform="rotate(-90 52 {(y0+y1)/2})" ')
    pts = [("S3 Standard", 0.05, 0.12, TEAL), ("Wasabi", 0.07, 0.32, TEAL), ("Glacier Flexible", 0.62, 0.58, TEAL),
           ("Deep Archive", 0.86, 0.74, TEAL), ("LTO library", 0.43, 0.84, ACC), ("LTO shelf", 0.7, 0.9, ACC_D)]
    for name, fx, fy, col in pts:
        x, y = x0 + fx * (x1 - x0), y0 + fy * (y1 - y0)
        b += f'<circle cx="{x}" cy="{y}" r="15" fill="{col}"/><circle cx="{x}" cy="{y}" r="6" fill="#fff"/>'
        anchor = "end" if fx > 0.8 else "start"
        dx = -24 if anchor == "end" else 24
        b += text(x + dx, y + 6, name, 18, INK, 700, anchor)
    return svg(960, 420, b, "Schematic: object storage classes answer in milliseconds but cost more per terabyte, cloud archive tiers are cheap but take hours, and LTO tape in a library answers in minutes at the lowest cost per terabyte")


def fig_storage_options():
    """Four ways to keep cartridges: jewel case, padded transport case, media cabinet, rack shelf."""
    b = ""
    # 1 jewel case: one cartridge standing on edge in a clear case
    b += card(30, 50, 210, 300) + f'<rect x="80" y="100" width="110" height="170" rx="12" fill="{ACC_50}" stroke="{ACC}" stroke-width="3"/>'
    b += f'<g transform="rotate(-90 135 185)">' + cartridge(85, 139, 1.0, "", ACC) + "</g>"
    b += chip(135, 310, "x1", 70, size=16)
    # 2 turtle-style transport case with handle and several cartridges
    b += card(258, 50, 210, 300) + f'<path d="M318 112 q45 -40 90 0" fill="none" stroke="{INK2}" stroke-width="10" stroke-linecap="round"/>'
    b += f'<rect x="282" y="112" width="162" height="160" rx="18" fill="{INK2}"/>'
    for i in range(5):
        b += f'<rect x="{296 + i*29}" y="132" width="22" height="120" rx="5" fill="{ACC if i % 2 == 0 else ACC_D}"/>'
    b += chip(363, 310, "x5 / x10 / x20", 150, size=15)
    # 3 media cabinet with drawers of cartridges
    b += card(486, 50, 210, 300) + f'<rect x="516" y="80" width="150" height="200" rx="10" fill="{SURF2}" stroke="{INK2}" stroke-width="4"/>'
    for r in range(4):
        y = 92 + r * 46
        b += f'<rect x="526" y="{y}" width="130" height="38" rx="5" fill="#fff" stroke="{LINE}" stroke-width="2"/>'
        for i in range(8):
            b += f'<rect x="{534 + i*15}" y="{y+6}" width="10" height="26" rx="2" fill="{ACC if (i + r) % 3 else ACC_D}"/>'
    b += shield(640, 250, .55, AMBER) + chip(591, 326, "fire / EMI", 120, size=15)
    # 4 rack shelf in a server rack
    b += card(714, 50, 216, 300) + f'<rect x="760" y="70" width="124" height="214" rx="8" fill="{INK2}"/>'
    for r in range(5):
        y = 80 + r * 40
        b += f'<rect x="770" y="{y}" width="104" height="32" rx="4" fill="#3a3550"/>'
        if r in (1, 2):
            for i in range(6):
                b += f'<rect x="{776 + i*16}" y="{y+4}" width="12" height="24" rx="2" fill="{ACC}"/>'
        else:
            b += f'<rect x="780" y="{y+12}" width="50" height="7" rx="3" fill="#fff" opacity=".6"/><circle cx="862" cy="{y+16}" r="4" fill="{GREEN}"/>'
    b += chip(822, 318, "19\"", 70, size=16)
    return svg(960, 400, b, "Four ways to keep LTO cartridges: a single jewel case on edge, a padded transport case for 5 to 20 cartridges, a media cabinet with drawers, and a shelf in a 19 inch rack")


def _laptop(x, y, s=1.0):
    return (f'<g transform="translate({x},{y}) scale({s})"><rect x="10" y="0" width="120" height="78" rx="8" fill="{INK2}"/><rect x="18" y="8" width="104" height="62" rx="4" fill="{ACC_100}"/>'
            f'<path d="M0 84 h140 l-10 10 h-120 z" fill="{INK2}"/></g>')


def _desk_drive(x, y, label, col=INK2):
    return (f'<g transform="translate({x},{y})"><rect width="200" height="96" rx="14" fill="{col}"/><rect x="18" y="30" width="110" height="16" rx="5" fill="#fff" opacity=".9"/>'
            f'<circle cx="170" cy="38" r="7" fill="{GREEN}"/>' + text(100, 80, label, 16, "#fff", 700, font=MONO) + "</g>")


def fig_owc_family():
    """Archive Pro (Thunderbolt) on one workstation, Archive Pro Ethernet shared over 10GbE."""
    b = card(30, 40, 430, 340) + _laptop(70, 100) + arrow(220, 150, 250, 150, ACC, 5)
    b += _desk_drive(240, 104, "LTO-9") + chip(340, 250, "Thunderbolt", 150, size=16)
    b += cartridge(300, 284, .62, "L9")
    b += card(490, 40, 440, 340)
    for i in range(3):
        b += _laptop(512 + i * 140, 70, .78)
    b += f'<rect x="530" y="168" width="380" height="10" rx="5" fill="{TEAL}"/>'
    for i in range(3):
        b += f'<line x1="{567 + i * 140}" y1="146" x2="{567 + i * 140}" y2="168" stroke="{TEAL}" stroke-width="5"/>'
    b += f'<line x1="720" y1="178" x2="720" y2="238" stroke="{TEAL}" stroke-width="5"/>' + chip(720, 208, "10GbE iSCSI", 160, size=16)
    b += _desk_drive(620, 240, "LTO-9")
    return svg(960, 420, b, "OWC Archive Pro connects one LTO drive to one computer over Thunderbolt; Archive Pro Ethernet shares the drive with several workstations over 10 gigabit iSCSI")


def fig_conditions():
    """Nested temperature (x) and humidity (y) boxes: shipping > in a drive > short-term storage > long-term storage."""
    x0, x1, y0, y1 = 110, 900, 40, 330
    tmin, tmax = -25, 55
    X = lambda t: x0 + (t - tmin) / (tmax - tmin) * (x1 - x0)
    Y = lambda h: y1 - h / 100 * (y1 - y0)
    b = f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" rx="12" fill="#fff" stroke="{LINE}" stroke-width="2"/>'
    boxes = [(-23, 49, 5, 80, SURF2, FAINT, "ship"), (10, 45, 10, 80, ACC_50, ACC_100, "drive"), (16, 32, 20, 80, ACC_100, ACC, "short"), (16, 25, 20, 50, ACC, ACC_D, "archive")]
    for t0, t1, h0, h1, fill, stroke, lab in boxes:
        b += f'<rect x="{X(t0)}" y="{Y(h1)}" width="{X(t1)-X(t0)}" height="{Y(h0)-Y(h1)}" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="3"/>'
    b += text((X(16) + X(25)) / 2, Y(35) + 6, "16-25", 17, "#fff", 700, font=MONO)
    for t in (-20, 0, 16, 25, 32, 45):
        b += f'<line x1="{X(t)}" y1="{y1}" x2="{X(t)}" y2="{y1+8}" stroke="{FAINT}" stroke-width="2"/>' + text(X(t), y1 + 30, f"{t}", 15, MUTED, 700, font=MONO)
    b += text(x1, y1 + 56, "°C", 16, MUTED, 700, "end", font=MONO)
    for h in (20, 50, 80):
        b += text(x0 - 12, Y(h) + 5, f"{h}%", 15, MUTED, 700, "end", font=MONO)
    b += f'<line x1="{X(52)}" y1="{y0+8}" x2="{X(52)}" y2="{y1-8}" stroke="{RED}" stroke-width="3" stroke-dasharray="6 6"/>' + text(X(52) - 8, y0 + 30, "52", 15, RED, 700, "end", font=MONO)
    return svg(960, 400, b, "Temperature and humidity ranges for LTO tape: long-term storage 16 to 25 °C and 20 to 50 percent, short-term storage up to 32 °C and 80 percent, in a drive 10 to 45 °C, shipping minus 23 to 49 °C, and tape damage above 52 °C")


FIGURES = {
    "lto-storage-how-it-works.svg": fig_how_it_works,
    "lto-storage-system.svg": fig_storage_system,
    "lto-vs-object-access-cost.svg": fig_access_vs_cost,
    "lto-storage-options.svg": fig_storage_options,
    "owc-lto-archive-pro.svg": fig_owc_family,
    "lto-storage-conditions.svg": fig_conditions,
}
PLACEMENT = []
