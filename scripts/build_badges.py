"""Link badges for sellers and vendors, the /badges embed page, and the press chart.

    assets/badges/price-tracker-light.svg, -dark.svg     "Listed on the LTO Price Tracker" (sellers)
    assets/badges/archive-advisor-light.svg, -dark.svg   "Ranked in the Tape Archive Advisor" (archive vendors)
    assets/press/lto-cost-per-tb-<month>.svg               cost per TB chart for the monthly price note
    /badges                                              copy-paste embed code (noindex utility page)

Outreach drafts that use these live outside the repo in ~/coldmail/tapebackup-outreach.
"""

import os

import build_prices as BP
from build_prices import GENS, date_text
from markets import PRICE_MONTH
from site_shell import ROOT, SITE, esc, page, write

ACC, ACC_D, INK, MUTED, SURF = "#5b27d6", "#4a1fb0", "#161320", "#6e6a7c", "#f7f6fa"
FONT = "'Space Grotesk','Hanken Grotesk',system-ui,-apple-system,'Segoe UI',sans-serif"
MONO = "'Space Mono',ui-monospace,Menlo,monospace"
BADGES = {
    "price-tracker": ("LISTED ON THE", "LTO Price Tracker", "/lto-tape-price-trend", "Sellers whose LTO listings we track"),
    "archive-advisor": ("RANKED IN THE", "Tape Archive Advisor", "/tape-archive-advisor", "Archive software ranked by the advisor"),
}


def badge_svg(top, main, dark):
    bg, fg, sub, edge = (INK, "#fff", "#c9c2e8", "#2e2940") if dark else ("#fff", INK, MUTED, "#dedce6")
    mark = (f'<rect x="14" y="16" width="44" height="40" rx="8" fill="{ACC}"/><rect x="20" y="22" width="32" height="13" rx="3" fill="#fff"/>'
            f'<rect x="20" y="40" width="5" height="10" rx="1.5" fill="#fff" opacity=".45"/><rect x="29" y="40" width="5" height="10" rx="1.5" fill="#fff" opacity=".45"/>'
            f'<rect x="38" y="40" width="5" height="10" rx="1.5" fill="#fff" opacity=".45"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="260" height="72" viewBox="0 0 260 72" role="img" aria-label="{esc(top.title())} {esc(main)}, TapeBackup.org">'
            f'<title>{esc(top.title())} {esc(main)}, TapeBackup.org</title>'
            f'<rect x="1" y="1" width="258" height="70" rx="14" fill="{bg}" stroke="{edge}" stroke-width="2"/>{mark}'
            f'<text x="72" y="26" font-family="{MONO}" font-size="9.5" font-weight="700" letter-spacing="1.4" fill="{sub}">{esc(top)}</text>'
            f'<text x="72" y="45" font-family="{FONT}" font-size="16" font-weight="700" fill="{fg}">{esc(main)}</text>'
            f'<text x="72" y="60" font-family="{MONO}" font-size="9.5" font-weight="700" fill="{ACC if not dark else "#b9a6f5"}">tapebackup.org</text></svg>\n')


def cost_chart(current):
    """Horizontal bars: cost per native TB by generation, plus the 40 TB LTO-10 cartridge."""
    g = current["generations"]
    rows = []
    for x in GENS:
        c = g[x]["cartridge"]
        if c.get("perTBLow") is not None:
            rows.append((x, c["perTBLow"], c["perTBHigh"]))
    c40 = g["LTO-10"].get("cartridge40TB") or {}
    if c40.get("low") is not None:
        rows.append(("LTO-10 40 TB", c40["low"] / 40, (c40.get("high") or c40["low"]) / 40))
    top = max(hi for _, _, hi in rows) * 1.45
    W, H, x0, x1 = 960, 110 + 64 * len(rows), 220, 900
    b = (f'<rect width="{W}" height="{H}" rx="22" fill="{SURF}"/>'
         f'<text x="40" y="52" font-family="{FONT}" font-size="26" font-weight="700" fill="{INK}">LTO cartridge cost per native TB, US sellers</text>'
         f'<text x="40" y="80" font-family="{MONO}" font-size="14" fill="{MUTED}">Low and high new listings, checked {esc(date_text())}. Source: tapebackup.org</text>')
    for i, (name, lo, hi) in enumerate(rows):
        y = 110 + i * 64
        X = lambda v: x0 + v / top * (x1 - x0)
        col = ACC if name == "LTO-9" else ACC_D if "40" in name else "#9a96a8"
        b += f'<text x="{x0-16}" y="{y+28}" font-family="{FONT}" font-size="20" font-weight="700" fill="{INK}" text-anchor="end">{esc(name)}</text>'
        b += f'<rect x="{x0}" y="{y+8}" width="{x1-x0}" height="30" rx="8" fill="#fff"/>'
        b += f'<rect x="{x0}" y="{y+8}" width="{X(lo)-x0}" height="30" rx="8" fill="{col}" opacity=".35"/><rect x="{X(lo)}" y="{y+8}" width="{max(4, X(hi)-X(lo))}" height="30" rx="4" fill="{col}"/>'
        b += f'<text x="{X(hi)+10}" y="{y+29}" font-family="{MONO}" font-size="16" font-weight="700" fill="{INK}">${lo:.2f} to ${hi:.2f}</text>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img"><title>LTO cartridge cost per native TB</title>{b}</svg>\n'


def build_all(current):
    out = os.path.join(ROOT, "assets", "badges")
    os.makedirs(out, exist_ok=True)
    for key, (top, main, _, _) in BADGES.items():
        for dark in (False, True):
            open(os.path.join(out, f"{key}-{'dark' if dark else 'light'}.svg"), "w", encoding="utf-8").write(badge_svg(top, main, dark))
    press = os.path.join(ROOT, "assets", "press")
    os.makedirs(press, exist_ok=True)
    if BP.MKT.is_us:
        open(os.path.join(press, f"lto-cost-per-tb-{PRICE_MONTH}.svg"), "w", encoding="utf-8").write(cost_chart(current))
    cards = ""
    for key, (top, main, href, who) in BADGES.items():
        for variant in ("light", "dark"):
            src = f"{SITE}/assets/badges/{key}-{variant}.svg"
            code = f'<a href="{SITE}{href}"><img src="{src}" alt="{top.title()} {main} on TapeBackup.org" width="260" height="72"></a>'
            cards += (f'<section class="section-card"><p class="eyebrow">{esc(who)}, {variant}</p><h2>{esc(main)} badge</h2>'
                      f'<p><img src="/assets/badges/{key}-{variant}.svg" alt="{esc(top.title())} {esc(main)}" width="260" height="72" style="{"background:#161320;padding:12px;border-radius:12px" if variant == "dark" else ""}"></p>'
                      f'<p>Copy this code into your page:</p><pre style="white-space:pre-wrap;word-break:break-all;background:#f0eef5;padding:14px;border-radius:12px;font-size:13px">{esc(code)}</pre></section>')
    body = f"""<section class="hero"><div class="container"><div class="hero-copy" style="max-width:860px">
<p class="eyebrow">Badges</p><h1 style="max-width:none">TapeBackup.org badges</h1>
<p>Sellers listed in our LTO price tracker and archive products ranked in our tape archive advisor are welcome to show one of these badges. Each links to the page you appear on. Use them as they are; please do not change the wording.</p></div></div></section>
<main class="page"><div class="container"><div class="section-stack">{cards}
<section class="section-card"><p class="eyebrow">Questions</p><h2>Corrections and questions</h2><p>If a price, product name or ranking looks wrong, tell us on the <a href="/contact">contact page</a> and we will check it.</p></section>
</div></div></main>"""
    write("/badges", page("/badges", "TapeBackup.org Badges for Sellers and Vendors",
                          "Badges for LTO sellers listed in the TapeBackup.org price tracker and archive software ranked in the tape archive advisor, with embed code.",
                          body, robots="noindex, follow"))
    return 4
