"""Animated JS clips (autoplay, pausable, 12 seconds) at the top of five pages.

    add_clips(root)   # root = the site folder or a staged market build, with build_prices' market selected

The animation itself is /jsvideo.js. This module only writes the data it needs into the page:
- #jsv-data: structure (bar lengths, generation names), never translated
- #jsv-text: every word and every price, so the language editions translate and localise it
Numbers come from the market being built, so the euro pages show euro prices.
"""

import json
import math
import os
import re

import build_prices as BP
from site_shell import esc

TAG = '<script src="/jsvideo.js" defer></script>'
PAGES = {
    "/lto-tape-price-trend": "prices",
    "/why-tape/lto-tape-drive": "drive",
    "/backup-calculator": "calc",
    "/lto-tape-price-trend/lto10-price": "lto10",
    "/backup-software-finder": "finder",
}


def _mid(item):
    lo, hi = (item or {}).get("low"), (item or {}).get("high")
    return None if lo is None else (lo + (hi if hi is not None else lo)) / 2


def _per_tb(item):
    lo, hi = (item or {}).get("perTBLow"), (item or {}).get("perTBHigh")
    if lo is None:
        return "n/a"
    s = BP.MKT.sym
    return f"{s}{lo:.2f}-{s}{hi:.2f}" if hi is not None and abs(hi - lo) > 0.004 else f"{s}{lo:.2f}"


def _clip(name):
    g = BP.MKT.generations
    if name == "prices":
        gens = ["LTO-6", "LTO-7", "LTO-8", "LTO-9", "LTO-10"]
        mids = [(_mid({"low": g[x]["cartridge"].get("perTBLow"), "high": g[x]["cartridge"].get("perTBHigh")}) or 0) for x in gens]
        top = max(mids) or 1
        best = min(range(len(gens)), key=lambda i: mids[i] or 1e9)
        data = {"dur": 12, "best": best, "bars": [{"g": x, "w": round(m / top, 3)} for x, m in zip(gens, mids)]}
        text = {"title": "Price per terabyte", "sub": f"LTO cartridges, native capacity, {BP.date_text()}",
                "cheap": "Cheapest per TB", "note": "Older does not mean cheaper per TB",
                "cap": f"Cartridge price per native TB for LTO-6 to LTO-10, from seller listings checked on {BP.date_text()}. {gens[best]} has the lowest cost per terabyte."}
        for i, x in enumerate(gens):
            text[f"r{i}"] = _per_tb(g[x]["cartridge"])
        return data, text
    if name == "drive":
        l9 = g["LTO-9"]
        data = {"dur": 12, "gen": "LTO-9", "v1": "LTO-9", "v3": "SAS"}
        text = {"title": "How to choose an LTO drive", "s1": "Generation", "s2": "Form factor", "s3": "Interface", "s4": "Compatibility",
                "v2": "Half-height or desktop", "v4": "Reads one generation back", "internal": "Internal drive", "external": "External drive",
                "pi": BP.short_rng(l9["driveInternal"]), "pe": BP.short_rng(l9["driveExternal"]),
                "cap": "Four checks for any LTO drive: generation, form factor, interface and compatibility. The LTO-9 drive prices shown are from seller listings."}
        return data, text
    if name == "calc":
        c, d = _mid(g["LTO-9"]["cartridge"]), _mid(g["LTO-9"]["driveInternal"])
        data = {"dur": 12, "gen": "LTO-9", "n": 12}
        text = {"title": "How many LTO tapes do you need?", "l1": "Data to protect", "l2": "Copies", "l3": "Recovery time", "l4": "Recovery point",
                "v3": "Hours", "v4": "Daily", "btn": "Show my recommendation", "rec": "Recommended", "carts": "cartridges", "media": "Media", "drive": "One drive",
                "m1": BP.money0(12 * c) if c else "n/a", "m2": BP.money0(d) if d else "n/a",
                "cap": "Example: 100 TB with two copies needs 12 LTO-9 cartridges. Enter your own numbers in the calculator below."}
        return data, text
    if name == "lto10":
        l = g["LTO-10"]
        data = {"dur": 12}
        text = {"title": "LTO-10 at a glance", "fh": "Full-height drives only", "nr": "Reads LTO-10 only",
                "p30": BP.short_rng(l["cartridge"]), "t30": _per_tb(l["cartridge"]) + " / TB",
                "p40": BP.short_rng(l.get("cartridge40TB")) if (l.get("cartridge40TB") or {}).get("low") is not None else "",
                "t40": (_per_tb(l.get("cartridge40TB")) + " / TB") if (l.get("cartridge40TB") or {}).get("low") is not None else "",
                "cap": "LTO-10 comes as a 30 TB or a 40 TB cartridge. Only full-height drives exist so far, and they read LTO-10 only."}
        return data, text
    data = {"dur": 12}
    text = {"title": "Which backup software fits?", "q1": "Mostly virtual estate", "q2": "Large mixed estate", "q3": "Small budget", "q4": "Microsoft 365 data",
            "more": "Contact us to know more vendors",
            "cap": "Match your environment to a shortlist: Veeam, Commvault, Nakivo or Veeam for Microsoft 365. Contact us to know more vendors."}
    return data, text


def _block(name):
    data, text = _clip(name)
    text.update({"play": "Play", "pause": "Pause"})
    cap = text.pop("cap")
    dj = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    tj = json.dumps(text, ensure_ascii=False).replace("</", "<\\/")
    return (f'<section class="section-card jsv-card"><div class="jsv" data-clip="{name}" role="group">'
            '<div class="jsv-stage"></div><div class="jsv-bar">'
            '<button class="jsv-btn" type="button"><svg class="i-play" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M7 4.5v15l13-7.5z" fill="currentColor"/></svg>'
            '<svg class="i-pause" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M6 4h4v16H6zM14 4h4v16h-4z" fill="currentColor"/></svg></button>'
            '<div class="jsv-track"><i></i></div><span class="jsv-time">0:00 / 0:12</span></div></div>'
            f'<p class="jsv-cap">{esc(cap)}</p>'
            f'<script type="application/json" id="jsv-data">{dj}</script>'
            f'<script type="application/json" id="jsv-text" data-i18n>{tj}</script></section>')


def add_clips(root):
    n = 0
    for path, name in PAGES.items():
        f = os.path.join(root, *path.strip("/").split("/"), "index.html")
        if not os.path.exists(f):
            continue
        s = open(f, encoding="utf-8").read()
        if 'class="jsv"' in s:
            continue
        main = s.find('<main class="page">')
        first = s.find('<section class="section-card', main) if main >= 0 else -1
        if first < 0:
            print(f"clip not placed (no anchor): {path}")
            continue
        s = s[:first] + _block(name) + s[first:]
        s = s.replace("</body>", TAG + "\n</body>", 1)
        open(f, "w", encoding="utf-8").write(s)
        n += 1
    return n
