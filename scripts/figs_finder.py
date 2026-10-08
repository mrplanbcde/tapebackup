"""Figures for /backup-software-finder: how the four questions pick software, and what the software has to do.

Text is limited to product names, generation names and technical tokens so every language edition shares the files.
"""

from draw_figures import *


def _server(x, y, w=64, fill=INK2, rows=3):
    g = ""
    for i in range(rows):
        yy = y + i * 24
        g += f'<rect x="{x}" y="{yy}" width="{w}" height="18" rx="5" fill="{fill}"/><circle cx="{x + w - 11}" cy="{yy + 9}" r="3.5" fill="{GREEN}"/><rect x="{x + 9}" y="{yy + 7}" width="{w * .42}" height="4" rx="2" fill="#fff" opacity=".65"/>'
    return g


def _vm_stack(x, y):
    g = ""
    for i in range(3):
        g += f'<rect x="{x + i * 10}" y="{y + i * 10}" width="50" height="38" rx="7" fill="#fff" stroke="{ACC}" stroke-width="3"/>'
    g += f'<rect x="{x + 20}" y="{y + 20}" width="50" height="38" rx="7" fill="{ACC_50}" stroke="{ACC}" stroke-width="3"/><rect x="{x + 30}" y="{y + 31}" width="30" height="5" rx="2.5" fill="{ACC}"/>'
    return g


def _scale(x, y):
    """Small estate (one box) next to a large one (many boxes)."""
    g = f'<rect x="{x}" y="{y + 18}" width="22" height="22" rx="5" fill="{ACC}"/>'
    for r in range(3):
        for c in range(3):
            g += f'<rect x="{x + 38 + c * 17}" y="{y + 2 + r * 17}" width="13" height="13" rx="3.5" fill="{ACC}" opacity="{.35 + .2 * ((r + c) % 3)}"/>'
    return g


def _coin(x, y, r=22):
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="{AMBER}"/><circle cx="{x}" cy="{y}" r="{r - 6}" fill="none" stroke="#fff" stroke-width="3" opacity=".8"/>'
            + text(x, y + 8, "$", 22, "#fff", 700))


def fig_finder_map():
    b = ""
    crit = [("1", _vm_stack), ("2", None), ("3", _scale), ("4", None)]
    ys = [34, 120, 206, 292]
    for (n, fn), y in zip(crit, ys):
        b += card(40, y, 330, 74)
        b += f'<circle cx="68" cy="{y + 37}" r="15" fill="{ACC}"/>' + text(68, y + 43, n, 17, "#fff", 700)
        if n == "1":
            b += _vm_stack(150, y + 6)
            b += f'<g transform="translate(262,{y + 12})">' + _server(0, 4, 54, INK2, 2) + "</g>"
        elif n == "2":
            b += cartridge(130, y + 14, .5, "LTO", ACC) + cartridge(190, y + 14, .5, "", ACC_D)
            b += f'<g transform="translate(262,{y + 12})"><rect width="60" height="26" rx="6" fill="{INK2}"/><circle cx="48" cy="13" r="3.5" fill="{GREEN}"/><rect x="9" y="11" width="24" height="4" rx="2" fill="#fff" opacity=".7"/></g>'
        elif n == "3":
            b += _scale(168, y + 14)
        else:
            b += _coin(190, y + 37) + f'<rect x="234" y="{y + 30}" width="84" height="14" rx="7" fill="{ACC_100}"/><rect x="234" y="{y + 30}" width="52" height="14" rx="7" fill="{ACC}"/>'
    outs = [("Veeam", ACC, 52), ("Commvault", ACC_D, 148), ("Nakivo", TEAL, 244), ("Veeam M365", INK2, 340)]
    for name, col, y in outs:
        b += f'<rect x="590" y="{y - 22}" width="330" height="64" rx="16" fill="#fff" stroke="{LINE}" stroke-width="2"/>'
        b += f'<rect x="606" y="{y - 8}" width="36" height="36" rx="10" fill="{col}"/><rect x="614" y="{y + 2}" width="20" height="9" rx="2" fill="#fff"/><rect x="614" y="{y + 15}" width="20" height="5" rx="2" fill="#fff" opacity=".45"/>'
        b += text(662, y + 17, name, 24, INK, 700, "start")
    # routes: criteria column -> outcomes
    for y1, y2 in ((71, 74), (157, 170), (243, 266), (329, 362)):
        b += f'<path d="M372 {y1} C 470 {y1}, 480 {y2 + 10}, 584 {y2 + 10}" fill="none" stroke="{ACC}" stroke-width="3.5" stroke-linecap="round" opacity=".55"/>'
        b += f'<polygon points="584,{y2 + 10 - 7} 598,{y2 + 10} 584,{y2 + 10 + 7}" fill="{ACC}" opacity=".7"/>'
    return svg(960, 420, b, "Four questions about your environment, tape use, size and budget lead to Veeam, Commvault, Nakivo or Veeam for Microsoft 365")


def fig_software_job():
    """Estate -> backup software (catalogue, schedule, encrypt) -> LTO library -> vault, with the six things to check."""
    b = card(30, 40, 170, 190) + _server(68, 78, 94) + _vm_stack(76, 160)
    b += arrow(206, 135, 262, 135, ACC, 5)
    b += f'<rect x="268" y="30" width="270" height="210" rx="22" fill="{ACC}"/>'
    b += f'<rect x="290" y="52" width="226" height="30" rx="9" fill="#fff" opacity=".95"/>' + text(403, 74, "Veeam · Commvault · Nakivo", 15, ACC_D, 700)
    # three jobs: catalogue (list + magnifier), schedule (clock), encrypt (lock)
    b += f'<g transform="translate(296,104)"><rect width="60" height="60" rx="12" fill="#fff" opacity=".18"/><rect x="14" y="14" width="26" height="5" rx="2.5" fill="#fff"/><rect x="14" y="26" width="32" height="5" rx="2.5" fill="#fff"/><rect x="14" y="38" width="20" height="5" rx="2.5" fill="#fff"/><circle cx="43" cy="42" r="9" fill="none" stroke="#fff" stroke-width="4"/><path d="M50 49 l8 8" stroke="#fff" stroke-width="4" stroke-linecap="round"/></g>'
    b += f'<g transform="translate(372,104)"><rect width="60" height="60" rx="12" fill="#fff" opacity=".18"/><circle cx="30" cy="30" r="19" fill="none" stroke="#fff" stroke-width="4"/><path d="M30 18 v13 l9 6" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></g>'
    b += f'<g transform="translate(448,104)"><rect width="60" height="60" rx="12" fill="#fff" opacity=".18"/><rect x="16" y="29" width="28" height="22" rx="6" fill="#fff"/><path d="M21 29 v-6 a9 9 0 0 1 18 0 v6" fill="none" stroke="#fff" stroke-width="4"/></g>'
    b += text(403, 205, "AES-256", 17, "#fff", 700, font=MONO)
    b += arrow(544, 135, 600, 135, ACC, 5)
    b += card(606, 40, 170, 190, ACC_50)
    for i in range(3):
        b += cartridge(630 + (i % 2) * 62, 62 + (i // 2) * 52, .5, "L9" if i == 0 else "", ACC if i != 1 else ACC_D)
    b += f'<rect x="630" y="170" width="124" height="38" rx="8" fill="{INK2}"/><rect x="642" y="184" width="62" height="7" rx="3.5" fill="#fff" opacity=".7"/><circle cx="735" cy="189" r="5" fill="{GREEN}"/>'
    b += arrow(782, 135, 832, 135, ACC, 5, "2 10")
    b += shield(838, 100, .9) + f'<path d="M836 180 l34 -22 l34 22 v30 h-68 z" fill="{INK2}"/><rect x="858" y="190" width="24" height="20" rx="4" fill="#fff" opacity=".8"/>'
    # the six checks
    tokens = ["LTO", "LTFS", "SAS / FC", "WORM", "AES-256", "NDMP"]
    for i, t in enumerate(tokens):
        x = 30 + i * 150
        b += f'<rect x="{x}" y="276" width="136" height="104" rx="16" fill="#fff" stroke="{LINE}" stroke-width="2"/>'
        b += f'<circle cx="{x + 28}" cy="{300}" r="13" fill="{GREEN}"/><path d="M{x + 21} 300 l5 5 l9 -11" fill="none" stroke="#fff" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>'
        b += text(x + 68, 352, t, 21 if len(t) < 7 else 18, INK, 700, font=MONO)
    return svg(960, 420, b, "Backup software connects your servers to an LTO library with catalogue, schedule and encryption, and should be checked for six tape features")


FIGURES = {
    "finder-decision-map.svg": fig_finder_map,
    "tape-software-job.svg": fig_software_job,
}
PLACEMENT = []
