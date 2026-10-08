from draw_figures import *
import json, math, re

_DATA = os.path.join(ROOT, "data")
_HIST = json.load(open(os.path.join(_DATA, "price-history.json"), encoding="utf-8"))["snapshots"]
_SEP = json.load(open(os.path.join(_DATA, "prices-2026-09.json"), encoding="utf-8"))["generations"]
_RANGE = re.compile(r"\$\s*([\d,]+(?:\.\d+)?)\s*-\s*\$\s*([\d,]+(?:\.\d+)?)")


def _rng(s):
    m = _RANGE.search(s or "")
    return (float(m.group(1).replace(",", "")), float(m.group(2).replace(",", ""))) if m else None


def _fmt(v):
    return f"${v:,.0f}"


# ------------------------------------------------ cartridges per petabyte
_CAP = {"LTO-6": 2.5, "LTO-7": 6, "LTO-8": 12, "LTO-9": 18, "LTO-10": 30}
_NEED = {g: math.ceil(1000 / c) for g, c in _CAP.items()}  # 400, 167, 84, 56, 34


def _pb_fig(hl):
    def make():
        b = text(40, 52, "1 PB", 32, INK, 700, "start") + text(158, 52, "= 1,000 TB", 20, MUTED, 600, "start")
        # legend: one icon stands for 10 cartridges
        b += f'<rect x="700" y="28" width="12" height="26" rx="2.5" fill="{ACC}"/><rect x="702.5" y="32" width="7" height="8" rx="1" fill="#fff"/>'
        b += text(722, 49, "= 10", 20, MUTED, 600, "start")
        defs = ""
        for i in range(5):
            col = ACC if list(_CAP)[i] == hl else "#b9b3cf"
            defs += (f'<pattern id="p{i}" x="206" y="{84 + i * 62}" width="14" height="28" patternUnits="userSpaceOnUse">'
                     f'<rect x="1" y="1" width="12" height="26" rx="2.5" fill="{col}"/><rect x="3.5" y="5" width="7" height="8" rx="1" fill="#fff"/></pattern>')
        b = f"<defs>{defs}</defs>" + b
        for i, g in enumerate(_CAP):
            y = 84 + i * 62
            on = g == hl
            n = _NEED[g]
            col = ACC if on else "#8d86a8"
            if on:
                b += f'<rect x="28" y="{y-8}" width="904" height="52" rx="14" fill="{ACC_50}" stroke="{ACC}" stroke-width="2"/>'
            b += text(46, y + 28, g, 22, ACC_D if on else INK2, 700, "start")
            b += text(188, y + 27, f"{_CAP[g]:g} TB", 15, MUTED, 600, "end")
            # n cartridges = n/10 icons of 14 px, so row length is proportional to n
            b += f'<rect x="206" y="{y}" width="{n * 1.4:.1f}" height="28" fill="url(#p{i})"/>'
            b += text(912, y + 28, f"{n}", 30, col, 700, "end")
        return svg(960, 420, b, f"Cartridges needed for 1 PB: {', '.join(f'{g} {n}' for g, n in _NEED.items())}")
    return make


def _pb_placement(hl):
    n = _NEED[hl]
    others = [f"{_NEED[g]} on {g}" for g in _CAP if g != hl]
    ex = " (the 30 TB cartridge)" if hl == "LTO-10" else ""
    return {
        "path": f"/lto-tape-price-trend/{hl.lower().replace('-', '')}-price",
        "file": f"{hl.lower().replace('-', '')}-cartridges-per-pb.svg",
        "alt": f"Rows of small cartridge icons showing how many cartridges 1 PB needs on each generation from LTO-6 to LTO-10, with {hl} highlighted at {n}.",
        "caption": (f"One petabyte (1,000 TB) at native capacity takes {n} {hl} cartridges{ex}, compared with "
                    + ", ".join(others[:-1]) + " and " + others[-1]
                    + ". Each icon stands for 10 cartridges. See the <a href=\"/lto-tape-capacity\">capacity table</a> for the per-cartridge figures."),
        "w": 960, "h": 420,
    }


# ------------------------------------------------ price history (vertical floating bars)
def _hist_points():
    pts = []
    order = ["sep-oct-2025", "nov-dec-2025", "jan-2026", "mar-2026", "aug-2026"]
    by = {s["slug"]: s for s in _HIST}
    short = {"sep-oct-2025": "Sep-Oct 25", "nov-dec-2025": "Nov-Dec 25", "jan-2026": "Jan 26", "mar-2026": "Mar 26", "aug-2026": "Aug 26"}
    for slug in order:
        c = by[slug]["cartridges"]
        pts.append((short[slug], {g: _rng(c.get(g, {}).get("range")) for g in ("LTO-8", "LTO-9")}))
    c = {g: _SEP[g]["cartridge"] for g in ("LTO-8", "LTO-9")}
    pts.append(("Sep 26", {g: (round(v["lowUSD"]), round(v["highUSD"])) for g, v in c.items()}))
    return pts


def fig_history():
    lo_v, hi_v, y_top, y_bot = 30, 130, 80, 340
    sc = (y_bot - y_top) / (hi_v - lo_v)
    Y = lambda v: y_bot - (v - lo_v) * sc
    b = text(40, 46, "USD", 18, MUTED, 700, "start")
    for g, col, x in (("LTO-8", TEAL, 620), ("LTO-9", ACC, 760)):
        b += f'<rect x="{x}" y="28" width="22" height="22" rx="6" fill="{col}"/>' + text(x + 32, 46, g, 19, INK, 700, "start")
    for t in range(40, 130, 20):
        b += f'<line x1="86" y1="{Y(t):.1f}" x2="930" y2="{Y(t):.1f}" stroke="{LINE}" stroke-width="2"/>' + text(76, Y(t) + 5, f"{t}", 15, MUTED, 600, "end")
    pts = _hist_points()
    gw = 140
    for i, (lab, d) in enumerate(pts):
        cx = 86 + gw * (i + .5) + 6
        b += text(cx, 372, lab, 16, INK2, 700)
        for j, (g, col) in enumerate((("LTO-8", TEAL), ("LTO-9", ACC))):
            r = d.get(g)
            if not r:
                continue
            x = cx - 48 + j * 52
            lo, hi = r
            b += f'<rect x="{x}" y="{Y(hi):.1f}" width="44" height="{(hi-lo)*sc:.1f}" rx="10" fill="{col}"/>'
            b += text(x + 22, Y(hi) - 7, f"{hi:.0f}", 14, col, 700) + text(x + 22, Y(lo) + 18, f"{lo:.0f}", 14, col, 700)
    return svg(960, 400, b, "LTO-8 and LTO-9 cartridge price ranges, September-October 2025 to September 2026")


# ------------------------------------------------ one snapshot (horizontal floating bars)
def _snap_fig(slug):
    s = next(x for x in _HIST if x["slug"] == slug)
    rows = []
    for g, v in s["cartridges"].items():
        r = _rng(v.get("range"))
        if r:
            rows.append((g, r, v.get("perTB")))
    top = 350
    x0, x1 = 150, 700
    X = lambda v: x0 + v / top * (x1 - x0)
    h = 150 + len(rows) * 52
    b = text(40, 54, s["label"], 30, INK, 700, "start")
    ya, yb = 96, h - 56
    for t in range(0, top + 1, 50):
        b += f'<line x1="{X(t):.1f}" y1="{ya}" x2="{X(t):.1f}" y2="{yb}" stroke="{LINE}" stroke-width="2"/>' + text(X(t), yb + 26, f"${t}", 15, MUTED, 600)
    for i, (g, (lo, hi), per) in enumerate(rows):
        y = ya + 12 + i * 52
        b += text(40, y + 25, g, 20, INK, 700, "start")
        b += f'<rect x="{X(lo):.1f}" y="{y}" width="{max(X(hi)-X(lo), 8):.1f}" height="34" rx="9" fill="{ACC}"/>'
        b += text(max(X(hi), X(lo) + 8) + 12, y + 24, f"${lo:,.0f}-${hi:,.0f}", 17, INK2, 700, "start")
        if per:
            b += text(930, y + 24, per.replace("about ", "~"), 17, MUTED, 600, "end")
    return svg(960, h, b, f"LTO cartridge price ranges by generation, {s['label']}"), h


def _snap_fig_fn(slug):
    return lambda: _snap_fig(slug)[0]


def _snap_placement(slug):
    s = next(x for x in _HIST if x["slug"] == slug)
    return {
        "path": f"/lto-tape-price-trend/{slug}",
        "file": f"snapshot-{slug}.svg",
        "alt": f"Horizontal bars showing the low to high LTO cartridge price range for each generation in the {s['label']} snapshot.",
        "caption": f"Cartridge price ranges per generation in the {s['label']} snapshot, in US dollars. The bar spans the low to high price and the figure on the right is the per terabyte estimate where one was recorded.",
        "w": 960, "h": _snap_fig(slug)[1],
    }


# ------------------------------------------------ capacity ladder
def fig_capacity():
    gens = [("LTO-5", 1.5, 2), ("LTO-6", 2.5, 2.5), ("LTO-7", 6, 2.5), ("LTO-8", 12, 2.5), ("LTO-9", 18, 2.5), ("LTO-10", 30, 2.5)]
    base, sc = 330, 2.6
    b = f'<line x1="40" y1="{base}" x2="920" y2="{base}" stroke="{LINE}" stroke-width="3"/>'
    b += f'<rect x="40" y="30" width="26" height="18" rx="4" fill="{ACC}"/>' + text(74, 46, "TB", 16, INK2, 700, "start")
    b += f'<rect x="130" y="30" width="26" height="18" rx="4" fill="none" stroke="{ACC}" stroke-width="2.5" stroke-dasharray="5 4"/>' + text(164, 46, "2:1  2.5:1", 16, INK2, 700, "start")
    for i, (g, nat, r) in enumerate(gens):
        cx = 120 + i * 144
        x = cx - 40
        comp = nat * r
        b += f'<rect x="{x}" y="{base-comp*sc:.1f}" width="80" height="{comp*sc:.1f}" rx="8" fill="none" stroke="{ACC}" stroke-width="2.5" stroke-dasharray="7 6"/>'
        if g == "LTO-10":
            c40 = 40 * r
            b += f'<rect x="{x}" y="{base-c40*sc:.1f}" width="80" height="{c40*sc:.1f}" rx="8" fill="none" stroke="{ACC}" stroke-width="2.5" stroke-dasharray="7 6" opacity=".6"/>'
            b += f'<rect x="{x}" y="{base-40*sc:.1f}" width="80" height="{40*sc:.1f}" rx="8" fill="{ACC_100}"/>'
        b += f'<rect x="{x}" y="{base-nat*sc:.1f}" width="80" height="{max(nat*sc, 6):.1f}" rx="6" fill="{ACC}"/>'
        b += text(cx, base + 30, g, 20, INK, 700)
        if g == "LTO-10":
            b += text(cx, base + 58, "30 | 40", 20, ACC, 700) + text(cx, base + 84, f"{30*r:g} | {40*r:g}", 17, MUTED, 600)
        else:
            b += text(cx, base + 58, f"{nat:g}", 20, ACC, 700) + text(cx, base + 84, f"{comp:g}", 17, MUTED, 600)
    return svg(960, 440, b, "Native and compressed capacity in TB for LTO-5 to LTO-10")


# ------------------------------------------------ shipped capacity
def fig_shipped():
    base, sc = 340, 1.3
    b = f'<line x1="60" y1="{base}" x2="900" y2="{base}" stroke="{LINE}" stroke-width="3"/>'
    for x, yr, v, col in ((130, "2024", 176.5, ACC_D), (330, "2025", 160.3, ACC)):
        b += f'<rect x="{x}" y="{base-v*sc:.1f}" width="120" height="{v*sc:.1f}" rx="12" fill="{col}"/>'
        b += text(x + 60, base - v * sc - 14, f"{v} EB", 26, INK, 700) + text(x + 60, base + 34, yr, 22, INK2, 700)
    # change 2024 -> 2025
    b += f'<rect x="256" y="150" width="68" height="34" rx="17" fill="#fff" stroke="{LINE}" stroke-width="2"/>'
    b += f'<path d="M268 160 l8 12 l8 -12 z" fill="{RED}"/>' + text(314, 174, "9%", 18, RED, 700, "end")
    # Q1 2026 chip
    b += card(560, 130, 280, 150, ACC_50).replace(f'stroke="{LINE}"', f'stroke="{GREEN}"')
    b += f'<path d="M610 245 v-80 m-24 26 l24 -26 l24 26" stroke="{GREEN}" stroke-width="12" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
    b += text(790, 205, "+57%", 46, GREEN, 700, "end") + text(790, 248, "Q1 2026", 22, INK2, 700, "end")
    b += arrow(460, 255, 548, 220, GREEN, 4, "2 9")
    return svg(960, 420, b, "Capacity of LTO shipped: 176.5 EB in 2024, 160.3 EB in 2025, and a 57 percent rise in Q1 2026")


# ------------------------------------------------ LTO-10 30 vs 40 TB
def _reel(cx, cy, r):
    g = f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#fff" stroke="{INK2}" stroke-width="3"/><circle cx="{cx}" cy="{cy}" r="{r*.18:.1f}" fill="{INK2}"/>'
    for k in range(3):
        a = math.radians(90 + k * 120)
        g += f'<circle cx="{cx+r*.55*math.cos(a):.1f}" cy="{cy-r*.55*math.sin(a):.1f}" r="{r*.2:.1f}" fill="{INK2}"/>'
    return g


def fig_30_40():
    base = 320
    b = f'<line x1="120" y1="{base}" x2="840" y2="{base}" stroke="{LINE}" stroke-width="3"/>'
    b += cartridge(210, base - 138, 1.5, "LTO-10", ACC_D)
    b += cartridge(560, base - 184, 2.0, "LTO-10", ACC)
    b += _reel(738, base - 30, 22)
    b += text(285, base + 52, "30 TB", 34, ACC_D, 700) + text(660, base + 52, "40 TB", 34, ACC, 700)
    b += f'<rect x="425" y="190" width="110" height="40" rx="20" fill="#fff" stroke="{LINE}" stroke-width="2"/>' + text(480, 218, "+10 TB", 22, INK2, 700)
    return svg(960, 420, b, "LTO-10 cartridges of 30 TB and 40 TB side by side")


FIGURES = {
    "lto-price-history.svg": fig_history,
    "lto-capacity-ladder.svg": fig_capacity,
    "lto-capacity-shipped.svg": fig_shipped,
    "lto-10-30-vs-40-tb.svg": fig_30_40,
}
for _g in _CAP:
    FIGURES[f"{_g.lower().replace('-', '')}-cartridges-per-pb.svg"] = _pb_fig(_g)
for _s in ("aug-2026", "mar-2026", "jan-2026", "nov-dec-2025", "sep-oct-2025"):
    FIGURES[f"snapshot-{_s}.svg"] = _snap_fig_fn(_s)

PLACEMENT = [_pb_placement(g) for g in _CAP] + [
    {"path": "/lto-tape-price-trend/history", "file": "lto-price-history.svg",
     "alt": "Floating bars showing the low to high cartridge price of LTO-8 and LTO-9 at six points in time from September-October 2025 to September 2026, in US dollars.",
     "caption": "Cartridge price ranges for LTO-8 and LTO-9 across our snapshots. Earlier snapshots were rounded ranges, so compare the direction of movement rather than exact amounts. The snapshots are listed on the <a href=\"/lto-tape-price-trend/aug-2026\">August 2026</a> and <a href=\"/lto-tape-price-trend/sep-oct-2025\">September-October 2025</a> pages.",
     "w": 960, "h": 400},
] + [_snap_placement(s) for s in ("aug-2026", "mar-2026", "jan-2026", "nov-dec-2025", "sep-oct-2025")] + [
    {"path": "/lto-tape-capacity", "file": "lto-capacity-ladder.svg",
     "alt": "Bars of native LTO capacity rising from LTO-5 at 1.5 TB to LTO-10 at 30 TB, with dashed outlines showing compressed capacity and a lighter extension for the 40 TB LTO-10 cartridge.",
     "caption": "Native capacity roughly doubles or triples each generation or two, from 1.5 TB on LTO-5 to 30 TB on LTO-10, with a 40 TB LTO-10 cartridge also available. The dashed outline shows the compressed figure at 2:1 for LTO-5 and 2.5:1 for LTO-6 and newer, which depends on how well your data compresses.",
     "w": 960, "h": 440},
    {"path": "/resources/tape-storage-market", "file": "lto-capacity-shipped.svg",
     "alt": "Two bars showing LTO capacity shipped, 176.5 EB in 2024 and 160.3 EB in 2025, with an up arrow chip for plus 57 percent in Q1 2026.",
     "caption": "The LTO Program reported 2024 as a record at 176.5 EB, 2025 about 9% lower at 160.3 EB, and Q1 2026 up 57% year on year. No total was published for Q1 2026, so it is shown as a change rather than a bar.",
     "w": 960, "h": 420},
    {"path": "/lto-tape-news", "file": "lto-10-30-vs-40-tb.svg",
     "alt": "Two LTO-10 cartridges side by side, the 30 TB one smaller and the 40 TB one larger with a film reel symbol.",
     "caption": "The 40 TB LTO-10 cartridge uses an aramid base film and works in existing LTO-10 drives; LTO-10 drives are full height.",
     "w": 960, "h": 420},
]
