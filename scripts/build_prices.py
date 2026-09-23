"""Build the LTO price tracker: hub, per-generation guides, history and archives.

Data lives in data/:
  prices-YYYY-MM.json         current US seller listings (one file per refresh)
  eu/prices-<cc>-YYYY-MM.json current European seller listings, one per market
  price-history.json          earlier US snapshots, newest first

Every function here renders for the market set with set_market() (see
scripts/markets.py): "us" is the English site; the other markets are built in
English with local prices and translated by scripts/i18n.py.

To publish a new month: add the new price files, move the outgoing month's
summary into price-history.json as a new snapshot, bump PRICE_MONTH in
markets.py and the CURRENT_* labels below, and rerun scripts/build_site.py.
"""

import json
import math
import os
import re

from markets import MARKETS, Market, load_fx
from site_shell import GENS, ROOT, breadcrumb_ld, esc, faq_html, faq_ld, hubspot_cta, page, slug_for, write

CURRENT_LABEL = "September 2026"
CURRENT_DATE_TEXT = "17 September 2026"
CURRENT_ISO = "2026-09-17"
NATIVE = {"LTO-5": 1.5, "LTO-6": 2.5, "LTO-7": 6, "LTO-8": 12, "LTO-9": 18, "LTO-10": 30}
COMPRESSED = {"LTO-6": "6.25 TB", "LTO-7": "15 TB", "LTO-8": "30 TB", "LTO-9": "45 TB", "LTO-10": "75 TB"}

MKT = None      # the market being rendered
US = None       # the US market, for comparison lines on European pages
_FX = None


def set_market(code):
    """Select the market every helper below renders for."""
    global MKT, US, _FX
    if _FX is None:
        try:
            _FX = load_fx()
        except SystemExit:
            _FX = {"per_usd": {"USD": 1.0}}
    US = US or Market("us", _FX)
    MKT = US if code == "us" else Market(code, _FX)
    return MKT


def current_data():
    """Generations plus market notes for the current market, in the shape the builders use."""
    # Market context comes from the US research notes (industry news with sources). The European
    # files' marketNotes are the researchers' method notes and are not shown on the site.
    notes = [n for n in US.raw.get("marketNotes", []) if not n["text"].startswith("Not found")]
    return {"generations": MKT.generations, "marketNotes": notes, "asOf": MKT.as_of}


def date_text():
    """The date prices were checked, for the current market."""
    if MKT.is_us or not MKT.as_of:
        return CURRENT_DATE_TEXT
    y, m, d = MKT.as_of.split("-")
    return f"{int(d)} {['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][int(m) - 1]} {y}"


def load(name):
    with open(os.path.join(ROOT, "data", name), encoding="utf-8") as f:
        return json.load(f)


def money(v, cents=None, sym=None):
    if v is None:
        return "not found"
    sym = sym or MKT.sym
    if cents is None:
        cents = v < 1000 and abs(v - round(v)) > 0.001
    return f"{sym}{v:,.2f}" if cents else f"{sym}{v:,.0f}"


def money0(v, sym=None):
    """Whole-unit amount, e.g. $8,254."""
    return money(v, False, sym)


def rng(item, cents=None, sym=None):
    lo, hi = (item or {}).get("low"), (item or {}).get("high")
    if lo is None:
        return "Not listed"
    if hi is None or abs(hi - lo) < 0.01:
        return money(lo, cents, sym)
    return f"{money(lo, cents, sym)} to {money(hi, cents, sym)}"


def rng0(item, sym=None):
    """Rounded range for prose, e.g. $256 to $300."""
    lo, hi = (item or {}).get("low"), (item or {}).get("high")
    if lo is None:
        return "not listed"
    sym = sym or MKT.sym
    a, b = f"{sym}{math.floor(lo):,}", f"{sym}{math.ceil(hi):,}"
    return a if a == b else f"{a} to {b}"


def short_rng(item, sym=None):
    """Whole-unit range for headlines, e.g. $92-$112."""
    lo, hi = (item or {}).get("low"), (item or {}).get("high")
    if lo is None:
        return "n/a"
    sym = sym or MKT.sym
    f = lambda x: f"{sym}{math.floor(x):,}" if x < 1000 else f"{sym}{round(x):,}"
    g = lambda x: f"{sym}{math.ceil(x):,}" if x < 1000 else f"{sym}{round(x):,}"
    return f(lo) if hi is None or abs(hi - lo) < 0.01 else f"{f(lo)}-{g(hi)}"


def per_tb(item, sym=None):
    if (item or {}).get("perTBLow") is None:
        return "n/a"
    sym = sym or MKT.sym
    if abs(item["perTBHigh"] - item["perTBLow"]) < 0.005:
        return f"{sym}{item['perTBLow']:.2f}"
    return f"{sym}{item['perTBLow']:.2f} to {sym}{item['perTBHigh']:.2f}"


def per_tb0(item, sym=None):
    """Rounded cost per TB for prose, e.g. $5 to $6."""
    if (item or {}).get("perTBLow") is None:
        return "n/a"
    sym = sym or MKT.sym
    a, b = round(item["perTBLow"]), round(item["perTBHigh"])
    return f"{sym}{a}" if a == b else f"{sym}{a} to {sym}{b}"


def mid(item, key="low", key2="high"):
    item = item or {}
    if item.get(key) is None:
        return None
    return (item[key] + item[key2]) / 2


def cheapest_per_tb(gens):
    """The generation with the lowest midpoint cost per native TB."""
    cands = [(mid(gens[g]["cartridge"], "perTBLow", "perTBHigh"), g) for g in GENS if gens[g]["cartridge"].get("perTBLow") is not None]
    return min(cands)[1] if cands else "LTO-9"


def compare_word(a, b):
    """How a compares with b: 'about the same', 'slightly more', 'roughly twice as much'..."""
    if a is None or b is None:
        return "about the same"
    r = a / b
    if r < 0.93:
        return "slightly less" if r > 0.8 else "noticeably less"
    if r <= 1.07:
        return "about the same"
    if r < 1.35:
        return "slightly more"
    if r < 1.7:
        return "about half as much again"
    if r < 2.5:
        return "roughly twice as much"
    return f"about {round(r)} times as much"


def unit_price(dp):
    return dp.get("unit")


def clean_note(note):
    note = re.sub(r"seen \d{4}-\d{2}-\d{2};?\s*", "", note or "").strip(" ;")
    return note[:1].upper() + note[1:] if note else ""


def table(headers, rows, label, num_cols=()):
    num = ' class="num"'
    th = "".join(f"<th{num if i in num_cols else ''}>{esc(h)}</th>" for i, h in enumerate(headers))
    body = "".join(
        "<tr>" + "".join(f"<td{num if i in num_cols else ''}>{c}</td>" for i, c in enumerate(r)) + "</tr>"
        for r in rows
    )
    return f'<div class="table-wrap"><table class="price-table" aria-label="{esc(label)}"><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>'


def listing_rows(dps, packs=False):
    rows = []
    items = [d for d in dps if bool(d.get("pack")) == packs]
    items.sort(key=lambda d: (d["unit"] if packs else d["price"]))
    for d in items:
        seller = f'<a href="{esc(d["url"])}" rel="nofollow noopener" target="_blank">{esc(d["seller"])}</a>' if d.get("url") else esc(d["seller"])
        price = money(d["price"], True)
        if packs:
            price = f"{money(d['price'], True)} ({money(d['unit'], True)} each)"
        rows.append([esc(d.get("sku") or ""), seller, price, esc(clean_note(d.get("note"))) if not packs else ""])
    return rows


def sources_list(gdata):
    seen = {}
    for key in ("cartridge", "cartridge40TB", "worm", "driveInternal", "driveExternal"):
        for d in gdata.get(key, {}).get("datapoints", []):
            seen.setdefault(d["seller"], d.get("url"))
    return "".join(f"<li>{esc(s)}</li>" for s in sorted(seen))


def and_list(names):
    names = list(names)
    if not names:
        return ""
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]


def currency_phrase():
    """How prices on this edition are expressed, for method notes."""
    if MKT.is_us:
        return "US dollars, listed prices before tax and shipping"
    cur = {"EUR": "euros", "PLN": "Polish złoty"}[MKT.currency]
    return f"{cur}, including {round(MKT.vat * 100)}% VAT, before shipping"


def sellers_phrase():
    return "US sellers" if MKT.is_us else f"sellers in {MKT.country}"


def neighbours(gen):
    i = GENS.index(gen)
    return GENS[max(0, i - 1): i + 2]


# ---------------------------------------------------------------- history helpers

def history_rows_for(gen, history):
    rows = []
    suffix = "" if MKT.is_us else " (US)"
    for snap in history["snapshots"]:
        c = snap.get("cartridges", {}).get(gen)
        d = snap.get("drives", {}).get(gen)
        if not c and not d:
            continue
        drive = f"Internal {d['internal']}; external {d['external']}" if d else "Not recorded"
        rows.append([f'<a href="/lto-tape-price-trend/{snap["slug"]}">{esc(snap["label"])}{suffix}</a>', esc(c["range"]) if c else "Not recorded", esc(drive)])
    return rows


def range_per_tb(text, gen):
    nums = [float(x.replace(",", "")) for x in re.findall(r"\$([\d,]+(?:\.\d+)?)", text)]
    if not nums or gen not in NATIVE:
        return ""
    lo, hi = nums[0], nums[1] if len(nums) > 1 else nums[0]
    cap = NATIVE[gen]
    return f"${lo / cap:.2f} to ${hi / cap:.2f}" if hi != lo else f"${lo / cap:.2f}"


# ---------------------------------------------------------------- generation guide

GEN_COPY = {
    "LTO-6": {
        "lead": "LTO-6 is a legacy generation. Cartridges are still easy to buy, but new standalone drives have almost disappeared, so most buyers here are feeding an existing drive or library.",
        "verdict": "Buy LTO-6 media to keep an installed drive or library running. For a new deployment, LTO-8 or LTO-9 costs far less per terabyte.",
        "title": "LTO-6 Price 2026: 2.5TB Tape and Drive Costs | TapeBackup",
    },
    "LTO-7": {
        "lead": "LTO-7 media is plentiful and new drives are still sold, but several drive SKUs now show call for availability. LTO-8 drives read and write LTO-7 cartridges, which keeps demand for the media alive.",
        "verdict": "LTO-7 makes sense for estates already standardized on it. Per terabyte, LTO-7 media now costs {lto7_vs_new} LTO-8 or LTO-9.",
        "title": "LTO-7 Price 2026: 6TB Tape and Drive Costs | TapeBackup",
    },
    "LTO-8": {
        "lead": "LTO-8 is the previous mainstream generation. Media and new half-height drives are in stock at several sellers, and drive prices vary widely between them for similar SAS models.",
        "verdict": "LTO-8 media now costs {lto8_vs_9} per terabyte as LTO-9. It is still a sensible buy if you already run LTO-8 drives or need to read LTO-7 tapes.",
        "title": "LTO-8 Price 2026: 12TB Tape and Drive Costs | TapeBackup",
    },
    "LTO-9": {
        "lead": "LTO-9 is the volume generation in 2026 and has {lto9_rank} cost per native terabyte of any LTO cartridge on sale. Media and half-height SAS drives are broadly in stock.",
        "verdict": "For most new tape deployments LTO-9 is the default: {lto9_reason}, mature drives, and wide library support.",
        "title": "LTO-9 Price 2026: 18TB Tape and Drive Costs | TapeBackup",
    },
    "LTO-10": {
        "lead": "LTO-10 is the current generation. Standard cartridges hold 30 TB and a newer 40 TB cartridge now ships in the same drives. Only full-height drives are on sale so far, and they cannot read older LTO generations.",
        "verdict": "LTO-10 pays off when density matters more than cost per terabyte: large archives, full libraries, or long retention where fewer cartridges save handling.",
        "title": "LTO-10 Price 2026: 30TB and 40TB Tape Costs | TapeBackup",
    },
}


def gen_copy(gen, gens):
    """GEN_COPY with the comparisons filled in from the current market's prices."""
    pt = lambda g: mid(gens[g]["cartridge"], "perTBLow", "perTBHigh")
    lto7_vs = compare_word(pt("LTO-7"), min(x for x in (pt("LTO-8"), pt("LTO-9")) if x is not None) if (pt("LTO-8") or pt("LTO-9")) else None)
    lto8_vs = compare_word(pt("LTO-8"), pt("LTO-9"))
    cheapest = cheapest_per_tb(gens)
    fill = {
        "lto7_vs_new": {"about the same": "about the same as", "slightly less": "slightly less than", "noticeably less": "less than"}.get(lto7_vs, lto7_vs + " as"),
        "lto8_vs_9": {"about the same": "about the same", "slightly less": "slightly less", "noticeably less": "less"}.get(lto8_vs, lto8_vs.replace(" as much", "")),
        "lto9_rank": "the lowest" if cheapest == "LTO-9" else "one of the lowest",
        "lto9_reason": "the cheapest media per terabyte" if cheapest == "LTO-9" else "low media cost per terabyte",
    }
    rel = {"about the same": "about the same per terabyte as", "slightly more": "slightly more per terabyte than",
           "slightly less": "slightly less per terabyte than", "noticeably less": "less per terabyte than"}.get(lto8_vs, lto8_vs + " per terabyte as")
    verdict8 = f"LTO-8 media now costs {rel} LTO-9. It is still a sensible buy if you already run LTO-8 drives or need to read LTO-7 tapes."
    c = dict(GEN_COPY[gen])
    c["lead"] = c["lead"].format(**fill)
    c["verdict"] = verdict8 if gen == "LTO-8" else c["verdict"].format(**fill)
    return c


def answer_sentence(gen, g):
    """One quotable, dated sentence answering 'how much does <gen> cost' (snippets and AI answers)."""
    c, wi, de = g["cartridge"], g.get("driveInternal", {}), g.get("driveExternal", {})
    where = "" if MKT.is_us else f" in {MKT.country}"
    s = f"As of {date_text()}, a new {gen} tape ({g['nativeTB']:g} TB native) costs {rng(c, True)}{where}, or {per_tb(c)} per TB"
    drives = []
    if wi.get("low") is not None:
        drives.append(f"internal drives {rng(wi, False)}{fallback_note(wi)}")
    if de.get("low") is not None:
        drives.append(f"external drives {rng(de, False)}{fallback_note(de)}")
    return s + ("; " + " and ".join(drives) if drives else "") + "."


def drive_cell(wi, de, sym=None):
    """History-table text for internal and external drive prices."""
    a, b = rng(wi, False, sym), rng(de, False, sym)
    if a == b == "Not listed":
        return "Not listed"
    return f"Internal {a}; external {b}"


def fallback_note(item):
    """' (seller in Germany)' when an item's listings all come from the fallback market."""
    dps = (item or {}).get("datapoints") or []
    if MKT.is_us or not dps or any(d.get("market") == MKT.code for d in dps):
        return ""
    return f" (seller in {MARKETS[dps[0]['market']]['country']})"


def gen_faqs(gen, g):
    c, wi, de = g["cartridge"], g.get("driveInternal", {}), g.get("driveExternal", {})
    faqs = [
        (f"How much does an {gen} tape cost in {CURRENT_LABEL}?",
         f"New single {gen} cartridges were listed at {rng(c, True)} at the specialist {sellers_phrase()} we checked on {date_text()}, which works out to {per_tb(c)} per native terabyte."),
    ]
    spread = "differ by several thousand dollars between sellers" if MKT.is_us else "differ widely between sellers"
    if wi.get("low") is not None:
        faqs.append((f"How much is an internal {gen} tape drive?",
                     f"New internal half-height SAS {gen} drives were listed at {rng(wi, False)}. Prices for similar models {spread}, so compare the exact part number."))
    if de.get("low") is not None:
        faqs.append((f"How much is an external {gen} tape drive?",
                     f"External desktop SAS {gen} drives were listed at {rng(de, False)}." + (" Only full-height LTO-10 drives were on sale." if gen == "LTO-10" else "")))
    if (g.get("worm") or {}).get("low") is not None:
        faqs.append((f"Do {gen} WORM cartridges cost more?",
                     f"Yes. {gen} WORM cartridges were listed at {rng(g['worm'], True)}, compared with {rng(c, True)} for standard data cartridges."))
    if gen == "LTO-10":
        c40 = g.get("cartridge40TB") or {}
        if c40.get("low") is not None:
            faqs.append(("Is the 40 TB LTO-10 cartridge worth it?",
                         f"40 TB LTO-10 cartridges were listed at {rng(c40, True)}, or {per_tb(c40)} per TB, compared with {per_tb(c)} for 30 TB cartridges. They make sense when library slots or handling matter more than media cost."))
        faqs.append(("Can LTO-10 drives read LTO-9 tapes?",
                     "No. LTO-10 drives do not read or write earlier LTO generations, so keep an LTO-9 or older drive for existing archives."))
    if not MKT.is_us:
        uc = US.generations[gen]["cartridge"]
        faqs.append((f"Are {gen} tapes cheaper in the US?",
                     f"US sellers listed new {gen} cartridges at {rng(uc, True, '$')} before sales tax on {CURRENT_DATE_TEXT}. Prices in {MKT.country} above include VAT, so compare net prices if you can reclaim it."))
    faqs.append((f"How have {gen} prices changed?",
                 f"See the {gen} price history table on this page, which lists every TapeBackup.org snapshot since September 2025."))
    return faqs


def blocked_not_used():
    """Blocked shops that were not reached some other way (e.g. through a price comparison site)."""
    used = " ".join(MKT.sellers_used()).lower()
    out = []
    for name in MKT.blocked_sellers():
        stem = re.sub(r"\.(de|fr|it|es|nl|be|pl|com|co\.uk)$", "", name.lower().split(" (")[0].strip())
        if stem and stem not in used:
            out.append(name)
    return out


def method_blocked_sentence():
    if MKT.is_us:
        return "Amazon, B&amp;H, CDW and Connection blocked automated checks or showed no price, so big-box pricing is not included."
    blocked = blocked_not_used()
    if not blocked:
        return ""
    return f"{esc(and_list(blocked))} blocked automated checks or showed no price, so {'it is' if len(blocked) == 1 else 'they are'} not included."


def build_gen_page(gen, g, history, current):
    copy = gen_copy(gen, current["generations"])
    path = f"/lto-tape-price-trend/{slug_for(gen)}"
    c, wi, de, worm = g["cartridge"], g.get("driveInternal", {}), g.get("driveExternal", {}), g.get("worm", {})
    native = g.get("nativeTB")
    cap_text = f"{native:g} TB native" + (f", up to {COMPRESSED[gen]} compressed" if gen in COMPRESSED else "")

    desc = f"{gen} tapes cost {short_rng(c)} ({per_tb(c).replace(' to ', '-')}/TB) at {sellers_phrase()} in {CURRENT_LABEL}. Drive prices, WORM media and price history."
    if len(desc) > 155:
        desc = f"{gen} tapes cost {short_rng(c)} at {sellers_phrase()} in {CURRENT_LABEL}. Drive prices, WORM media, cost per TB and price history."
    if len(desc) > 155:
        desc = f"{gen} tapes cost {short_rng(c)} in {CURRENT_LABEL}. Drive prices, WORM media, cost per TB and price history."

    stats = [
        (short_rng(c), f"New single {gen} cartridge, {native:g} TB native"),
        (f"{per_tb(c).replace(' to ', '-')}", "Cost per native TB"),
        (short_rng(wi) if wi.get("low") is not None else "Not listed", "Internal half-height SAS drive" if gen != "LTO-10" else "No bare internal drive listed"),
        (short_rng(de) if de.get("low") is not None else "Not listed", "External desktop SAS drive" + (" (full height)" if gen == "LTO-10" else "")),
    ]
    stats_html = "".join(f'<div class="stat-card"><strong>{esc(a)}</strong><span>{esc(b)}</span></div>' for a, b in stats)

    us_line = ""
    if not MKT.is_us:
        uc = US.generations[gen]["cartridge"]
        us_line = f" US sellers listed the same generation at {rng(uc, True, '$')} before sales tax ({per_tb(uc, '$')} per TB)."
    parts = []
    parts.append(f"""<section class="section-card" id="cartridge-prices"><p class="eyebrow">Cartridge listings</p><h2>{gen} cartridge prices by seller</h2>
<p>New single {gen} data cartridges ({native:g} TB native), sorted by price. Range: <strong>{rng(c, True)}</strong>, or {per_tb(c)} per native TB.{us_line}</p>
{table(["Part number", "Seller", "Price", "Note"], listing_rows(c["datapoints"]), f"{gen} cartridge prices", num_cols=(2,)) if c["datapoints"] else "<p>No new single cartridges were listed at the sellers checked.</p>"}
<p class="updated-note">Prices checked on {date_text()}. Sale prices change often; confirm at the seller before ordering.</p></section>""")

    pack_rows = listing_rows(c["datapoints"], packs=True)
    if pack_rows:
        parts.append(f"""<section class="section-card" id="multipacks"><p class="eyebrow">Bulk buying</p><h2>{gen} 5, 10 and 20 packs</h2>
<p>Packs are not always cheaper per cartridge than a single tape on sale, so compare the per-unit price.</p>
{table(["Part number", "Seller", "Pack price (per cartridge)", ""], pack_rows, f"{gen} multipack prices", num_cols=(2,))}</section>""")

    if gen == "LTO-10" and (g.get("cartridge40TB") or {}).get("datapoints"):
        c40 = g["cartridge40TB"]
        parts.append(f"""<section class="section-card" id="lto10-40tb"><p class="eyebrow">Higher capacity</p><h2>LTO-10 40 TB cartridge prices</h2>
<p>The 40 TB LTO-10 cartridge uses an aramid base film and works in existing LTO-10 drives. Range: <strong>{rng(c40, True)}</strong>, or {per_tb(c40)} per TB, against {per_tb(c)} for the 30 TB cartridge.</p>
{table(["Part number", "Seller", "Price", "Note"], listing_rows(c40["datapoints"]), "LTO-10 40TB cartridge prices", num_cols=(2,))}</section>""")

    if (worm or {}).get("datapoints"):
        parts.append(f"""<section class="section-card" id="worm"><p class="eyebrow">Write once media</p><h2>{gen} WORM cartridge prices</h2>
<p>WORM (write once, read many) cartridges cannot be overwritten, which is why they are used for compliance and ransomware-resistant copies. Range: <strong>{rng(worm, True)}</strong>.</p>
{table(["Part number", "Seller", "Price", "Note"], listing_rows(worm["datapoints"]), f"{gen} WORM prices", num_cols=(2,))}</section>""")

    drive_parts = []
    for label, item in (("Internal drives", wi), ("External desktop drives", de)):
        if (item or {}).get("datapoints"):
            drive_parts.append(f"<h3>{label}: {rng(item, False)}</h3>" + table(["Part number", "Seller", "Price", "Note"], listing_rows(item["datapoints"]), f"{gen} {label}", num_cols=(2,)))
    drive_note = ""
    if gen == "LTO-6" and not (wi or {}).get("datapoints"):
        drive_note = "<p>No new internal LTO-6 drive was listed. Refurbished drives are mostly sold by quote, so check warranty terms and head hours before buying used.</p>"
    if gen == "LTO-10":
        if MKT.is_us:
            drive_note = "<p>No half-height LTO-10 drive and no bare internal LTO-10 drive was listed at the sellers checked. Library add-on drives exist, for example a Qualstar Q-Series LTO-10 SAS full-height add-on at $23,509.</p>"
        elif not (wi or {}).get("datapoints"):
            drive_note = "<p>No half-height LTO-10 drive and no bare internal LTO-10 drive was listed at the sellers checked. LTO-10 drives so far ship as full-height units, in desktop enclosures or as library modules.</p>"
    parts.append(f"""<section class="section-card" id="drive-prices"><p class="eyebrow">Hardware</p><h2>{gen} tape drive prices</h2>
<p>New standalone SAS drives. You also need a SAS HBA in the host, and backup software that supports the drive.</p>{drive_note}{''.join(drive_parts) or '<p>No new standalone drive listings were found.</p>'}</section>""")

    if MKT.is_us:
        hist_rows = [[f"<strong>{CURRENT_LABEL} (current)</strong>", esc(rng(c, True)), esc(drive_cell(wi, de))]]
        hist_intro = "Each row links to the archived snapshot it came from. Earlier snapshots used rounded guide ranges, and the March 2026 drive figures were estimates rather than seller listings, so compare directions rather than exact dollars."
    else:
        ug = US.generations[gen]
        hist_rows = [[f"<strong>{CURRENT_LABEL}, {MKT.country_short} (current)</strong>", esc(rng(c, True)), esc(drive_cell(wi, de))],
                     [f"{CURRENT_LABEL} (US)", esc(rng(ug["cartridge"], True, "$")), esc(drive_cell(ug.get("driveInternal"), ug.get("driveExternal"), "$"))]]
        hist_intro = f"Prices in {MKT.country} are tracked from {CURRENT_LABEL}. Earlier rows are US snapshots in US dollars before sales tax: rounded guide ranges, with March 2026 drive figures that were estimates rather than seller listings, so compare directions rather than exact amounts."
    hist_rows += history_rows_for(gen, history)
    parts.append(f"""<section class="section-card" id="price-history"><p class="eyebrow">Price history</p><h2>{gen} price history</h2>
<p>{hist_intro}</p>
{table(["Snapshot", "Cartridge price", "Drive price"], hist_rows, f"{gen} price history")}
<p><a href="/lto-tape-price-trend/history">See the price history for every generation</a></p></section>""")

    comp_rows = []
    for n in neighbours(gen):
        ng = current["generations"][n]
        comp_rows.append([f'<a href="/lto-tape-price-trend/{slug_for(n)}">{n}</a>' if n != gen else f"<strong>{n}</strong>", f"{ng['nativeTB']:g} TB", esc(rng(ng["cartridge"], True)), esc(per_tb(ng["cartridge"]))])
    parts.append(f"""<section class="section-card" id="compare"><p class="eyebrow">Compare</p><h2>{gen} compared with nearby generations</h2>
{table(["Generation", "Native capacity", "Cartridge price", "Per native TB"], comp_rows, f"{gen} comparison")}
<p>{esc(copy['verdict'])}</p></section>""")

    with open(os.path.join(ROOT, "data", "price-guide-prose", slug_for(gen).replace("-price", "") + ".html"), encoding="utf-8") as f:
        parts.append(f.read())

    vat_note = "" if MKT.is_us else f" Prices include {round(MKT.vat * 100)}% VAT; where a seller showed a net price, VAT was added."
    parts.append(f"""<section class="section-card" id="sources"><p class="eyebrow">Method</p><h2>Where these {gen} prices come from</h2>
<p>We loaded seller product pages on {date_text()} and recorded the listed price, part number and stock note. Only new items are included unless a note says otherwise.{vat_note} {method_blocked_sentence()} Sellers used for {gen}:</p>
<ul class="source-list">{sources_list(g)}</ul></section>""")

    parts.append(hubspot_cta(f"Get the {gen} pricebook", f"Request the latest pricebook to compare {gen} media and drives from HPE, IBM, Quantum, Fujifilm and Sony before you buy."))
    faqs = gen_faqs(gen, g)
    parts.append(faq_html(faqs, f"{gen} price FAQ"))

    body = f"""<section class="hero"><div class="container hero-grid"><div class="hero-copy">
<p class="eyebrow">{gen} price · updated {CURRENT_LABEL}</p>
<h1>{gen} Price Guide</h1>
<p><strong>{esc(answer_sentence(gen, g))}</strong> {esc(copy['lead'])}</p>
<div class="signal-row"><span class="signal-chip">{esc(cap_text)}</span><span class="signal-chip">Tapes {esc(short_rng(c))}</span><span class="signal-chip">Checked {date_text()}</span></div>
</div>
<aside class="hero-panel"><p class="panel-label">Buyer summary</p><p class="panel-copy">{esc(copy['verdict'])}</p>
<div class="metrics"><div class="metric"><strong>{esc(short_rng(c))}</strong><span>Cartridge</span></div><div class="metric"><strong>{esc(per_tb(c).replace(' to ', '-'))}</strong><span>Per native TB</span></div><div class="metric"><strong>{len(c['datapoints'])}</strong><span>Listings checked</span></div></div>
</aside></div></section>
<main class="page"><div class="container">
<div class="stats-grid">{stats_html}</div>
<div class="section-stack">{''.join(parts)}</div>
</div></main>"""

    ld = [
        {"@context": "https://schema.org", "@type": "Article", "headline": f"{gen} Price Guide ({CURRENT_LABEL})", "description": desc,
         "dateModified": CURRENT_ISO, "datePublished": "2026-03-16", "author": {"@type": "Organization", "name": "TapeBackup.org"},
         "publisher": {"@type": "Organization", "name": "TapeBackup.org", "url": "https://tapebackup.org"}, "mainEntityOfPage": f"https://tapebackup.org{path}"},
        breadcrumb_ld([("Home", "/"), ("LTO Prices", "/lto-tape-price-trend"), (f"{gen} Price", path)]),
        faq_ld(faqs),
    ]
    write(path, page(path, copy["title"], desc, body, ld, hubspot=True, og_type="article"))
    return path


# ---------------------------------------------------------------- hub

def build_hub(current, history):
    path = "/lto-tape-price-trend"
    gens = current["generations"]
    cheap = cheapest_per_tb(gens)
    rows = []
    for gen in GENS:
        g = gens[gen]
        rows.append([f'<a href="/lto-tape-price-trend/{slug_for(gen)}"><strong>{gen}</strong></a>', f"{g['nativeTB']:g} TB", esc(rng(g["cartridge"], True)), esc(per_tb(g["cartridge"])), esc(rng(g.get("worm", {}), True)), esc(rng(g.get("driveInternal", {}), False)), esc(rng(g.get("driveExternal", {}), False))])
        c40 = g.get("cartridge40TB") or {}
        if gen == "LTO-10" and c40.get("low") is not None:
            rows.append([f'<a href="/lto-tape-price-trend/lto10-price#lto10-40tb"><strong>LTO-10 40 TB</strong></a>', "40 TB", esc(rng(c40, True)), esc(per_tb(c40)), "Not listed", "Uses LTO-10 drives", "Uses LTO-10 drives"])
    summary = table(["Generation", "Native", "Cartridge", "Per native TB", "WORM cartridge", "Internal drive", "External drive"], rows, "LTO price summary")

    jan = next(s for s in history["snapshots"] if s["slug"] == "jan-2026")
    mar = next(s for s in history["snapshots"] if s["slug"] == "mar-2026")
    change_rows = []
    for gen in GENS:
        g = gens[gen]
        row = [f"<strong>{gen}</strong>", esc(jan["cartridges"][gen]["range"]), esc(mar["cartridges"][gen]["range"]), esc(rng(US.generations[gen]["cartridge"], True, "$"))]
        if not MKT.is_us:
            row.append(esc(rng(g["cartridge"], True)))
        change_rows.append(row)
    if MKT.is_us:
        change_head = ["Generation", "January 2026", "March 2026", CURRENT_LABEL]
    else:
        change_head = ["Generation", "January 2026 (US)", "March 2026 (US)", f"{CURRENT_LABEL} (US)", f"{CURRENT_LABEL} ({MKT.country_short})"]
    changes = table(change_head, change_rows, "LTO cartridge price change in 2026")

    notes = "".join(
        f'<li>{esc(n["text"])} <a href="{esc(n["url"])}" rel="nofollow noopener" target="_blank">Source</a></li>'
        for n in current["marketNotes"] if not n["text"].startswith("Not found") and n.get("url")
    )

    guides = "".join(
        f'<a href="/lto-tape-price-trend/{slug_for(gen)}">{gen} price guide<span>Tapes {esc(short_rng(gens[gen]["cartridge"]))}, {gens[gen]["nativeTB"]:g} TB native</span></a>'
        for gen in GENS
    )
    archive_links = "".join(
        f'<a href="/lto-tape-price-trend/{s["slug"]}">{esc(s["label"])}<span>Archived snapshot</span></a>' for s in history["snapshots"]
    )

    l10 = gens["LTO-10"]
    c40 = l10.get("cartridge40TB") or {}
    faqs = [
        ("What is the cheapest LTO tape per terabyte in 2026?",
         f"{cheap}. New {gens[cheap]['nativeTB']:g} TB {cheap} cartridges were listed at {rng(gens[cheap]['cartridge'], True)}, or {per_tb(gens[cheap]['cartridge'])} per native TB"
         + (f", slightly below LTO-8 at {per_tb(gens['LTO-8']['cartridge'])}." if cheap == "LTO-9" and gens["LTO-8"]["cartridge"].get("perTBLow") is not None else ".")),
        ("How much does an LTO-10 tape cost?",
         f"30 TB LTO-10 cartridges were listed at {rng(l10['cartridge'], True)}" + (f" and the newer 40 TB cartridge at {rng(c40, True)}" if c40.get("low") is not None else "") + f" on {date_text()}."),
        ("How much does an LTO-9 tape drive cost?",
         f"New internal half-height SAS LTO-9 drives were listed at {rng(gens['LTO-9']['driveInternal'], False)} and external desktop SAS drives at {rng(gens['LTO-9']['driveExternal'], False)}."),
        ("Are LTO tape prices going up in 2026?",
         ("" if MKT.is_us else "At US sellers, ") + ("Cartridge" if MKT.is_us else "cartridge") + " prices are flat to slightly higher than in early 2026, while listed drive prices are well above the estimates published earlier in the year. One seller announced a general LTO tape price increase from 1 September 2026, but its prices still match other sellers."),
        ("Where can I see older LTO prices?",
         "Every earlier snapshot, from September 2025 onwards, is kept on the LTO price history page with links to the full archived tables."),
    ]

    if MKT.is_us:
        changes_intro = "<p>The January and March 2026 editions were compiled from different sources and rounded, so small differences are noise. The clear moves: LTO-6 and LTO-7 media got more expensive as supply thinned, LTO-8 and LTO-9 rose a little, and LTO-10 30 TB held steady.</p>"
        drive_para = f"<p>Drive prices look very different. The March 2026 edition estimated LTO-9 internal drives at $4,500 to $6,500; seller listings in {CURRENT_LABEL} run from {rng(gens['LTO-9']['driveInternal'], False)}. Part of that gap is method (estimates versus listings), so treat it as a warning to get quotes rather than a precise increase.</p>"
        method = "We load product pages at specialist tape resellers (Tape4Backup, LTO World, BackupWorks, TapeandMedia, MagStor, DatacenterDisk and StoragePartsDirect in this edition) and record the listed price, part number and stock note. We exclude listings the seller marks as inaccurate and prices that look like listing errors. Amazon, B&amp;H, CDW, Connection and the HPE Store blocked automated checks or showed no price, so big-box and used-market prices are not included. When a new edition is published, the previous one moves to the price history."
    else:
        changes_intro = f"<p>Prices in {MKT.country} are tracked from {CURRENT_LABEL}, so the history below comes from US sellers. The January and March 2026 US editions were compiled from different sources and rounded, so small differences are noise. The clear moves: LTO-6 and LTO-7 media got more expensive as supply thinned, LTO-8 and LTO-9 rose a little, and LTO-10 30 TB held steady.</p>"
        drive_para = f"<p>Drive prices look very different. The March 2026 US edition estimated LTO-9 internal drives at $4,500 to $6,500; US seller listings in {CURRENT_LABEL} run from {rng(US.generations['LTO-9']['driveInternal'], False, '$')}. Part of that gap is method (estimates versus listings), so treat it as a warning to get quotes rather than a precise increase.</p>"
        blocked = blocked_not_used()
        method = (f"We load product pages at sellers in {MKT.seller_region} ({esc(and_list(MKT.sellers_used()))} in this edition) and record the listed price, part number and stock note."
                  f" Prices include {round(MKT.vat * 100)}% VAT; where a seller showed a net price, VAT was added. We exclude listings the seller marks as inaccurate and prices that look like listing errors."
                  + (f" {esc(and_list(blocked))} blocked automated checks or showed no price, so {'it is' if len(blocked) == 1 else 'they are'} not included." if blocked else "")
                  + (f" Where no seller in {MKT.country} listed an item, the table shows a listing from Germany and says so in the note." if MKT.fallback_used else "")
                  + " When a new edition is published, the previous one moves to the price history.")

    glance = (f"{cheap} media has the lowest cost per native terabyte. LTO-10 30 TB tapes cost {rng0(l10['cartridge'])}"
              + (", and the 40 TB cartridge is now in stock." if c40.get("low") is not None else ".")
              + " Drives cost far more than earlier estimates suggested.")
    body = f"""<section class="hero"><div class="container hero-grid"><div class="hero-copy">
<p class="eyebrow">LTO price tracker · {CURRENT_LABEL}</p>
<h1>LTO Tape Prices: LTO-6 to LTO-10</h1>
<p><strong>As of {date_text()}, the cheapest LTO media per terabyte{'' if MKT.is_us else ' in ' + MKT.country} is {cheap} at {rng(gens[cheap]['cartridge'], True)} per {gens[cheap]['nativeTB']:g} TB cartridge ({per_tb(gens[cheap]['cartridge'])} per TB); LTO-10 30 TB cartridges cost {rng(l10['cartridge'], True)}.</strong> Current cartridge and drive prices for every LTO generation still on sale, taken from seller listings on {date_text()}, with cost per terabyte and links to each earlier snapshot.</p>
<div class="signal-row"><span class="signal-chip">{sum(len((gens[g].get(k) or {}).get('datapoints', [])) for g in GENS for k in ('cartridge', 'worm', 'driveInternal', 'driveExternal'))} listings checked</span><span class="signal-chip">{cheap} cheapest per TB</span><span class="signal-chip">Updated {date_text()}</span></div>
</div>
<aside class="hero-panel"><p class="panel-label">At a glance</p><p class="panel-copy">{esc(glance)}</p>
<div class="metrics"><div class="metric"><strong>{esc(short_rng(gens['LTO-9']['cartridge']))}</strong><span>LTO-9 tape</span></div><div class="metric"><strong>{esc(short_rng(l10['cartridge']))}</strong><span>LTO-10 30 TB tape</span></div><div class="metric"><strong>{esc(short_rng(gens['LTO-9']['driveInternal']))}</strong><span>LTO-9 internal drive</span></div></div>
</aside></div></section>
<main class="page"><div class="container"><div class="section-stack">
<section class="section-card" id="summary"><p class="eyebrow">Summary</p><h2>LTO tape and drive prices, {CURRENT_LABEL}</h2>
<p>New items only, {currency_phrase()}. Ranges cover single cartridges; see each generation guide for packs and individual listings.</p>
{summary}
<p class="updated-note">Checked {date_text()}.{' No new internal LTO-6 or LTO-10 drive, and only one new external LTO-6 drive, was listed at the sellers checked.' if MKT.is_us else ''}</p></section>
<section class="section-card" id="changes"><p class="eyebrow">What changed</p><h2>How LTO cartridge prices moved in 2026</h2>
{changes_intro}
{changes}
{drive_para}
<p><a href="/lto-tape-price-trend/history">Full LTO price history</a></p></section>
<section class="section-card" id="market"><p class="eyebrow">Market context</p><h2>What is moving the LTO market</h2><ul class="source-list">{notes}</ul></section>
<section class="section-card" id="guides"><p class="eyebrow">By generation</p><h2>LTO price guides by generation</h2><div class="link-grid">{guides}</div></section>
<section class="section-card" id="archive"><p class="eyebrow">Archive</p><h2>Earlier LTO price snapshots</h2><div class="link-grid">{archive_links}<a href="/lto-tape-price-trend/history">All history<span>Every generation side by side</span></a></div></section>
<section class="section-card" id="method"><p class="eyebrow">Method</p><h2>How we collect LTO prices</h2>
<p>{method}</p></section>
{hubspot_cta("Get the latest LTO pricebook", "Request the pricebook to compare HPE, IBM, Quantum, Fujifilm and Sony media and drives across LTO-6 to LTO-10.")}
{faq_html(faqs, "LTO price FAQ")}
</div></div></main>"""

    desc = f"LTO tape prices for {CURRENT_LABEL}: LTO-6 to LTO-10 cartridges, WORM media and drives from seller listings, with cost per TB and price history."
    ld = [
        {"@context": "https://schema.org", "@type": "Article", "headline": f"LTO Tape Prices: LTO-6 to LTO-10 ({CURRENT_LABEL})", "description": desc, "dateModified": CURRENT_ISO,
         "datePublished": "2025-10-01", "author": {"@type": "Organization", "name": "TapeBackup.org"}, "publisher": {"@type": "Organization", "name": "TapeBackup.org", "url": "https://tapebackup.org"}, "mainEntityOfPage": "https://tapebackup.org" + path},
        breadcrumb_ld([("Home", "/"), ("LTO Prices", path)]),
        faq_ld(faqs),
    ]
    write(path, page(path, "LTO Tape Price Tracker 2026: LTO-6 to LTO-10 Costs", desc, body, ld, hubspot=True, og_type="article"))
    return path


# ---------------------------------------------------------------- history + archives

def build_history(current, history):
    path = "/lto-tape-price-trend/history"
    snaps = history["snapshots"]
    gens_all = ["LTO-5"] + GENS
    if MKT.is_us:
        head = ["Generation", f"{CURRENT_LABEL} (current)"] + [s["label"] for s in snaps]
    else:
        head = ["Generation", f"{CURRENT_LABEL}, {MKT.country_short}", f"{CURRENT_LABEL}, US"] + [f"{s['label']} (US)" for s in snaps]
    rows = []
    for gen in gens_all:
        cur = current["generations"].get(gen)
        row = [f"<strong>{gen}</strong>", esc(rng(cur["cartridge"], True)) if cur else "Not tracked"]
        if not MKT.is_us:
            ucur = US.generations.get(gen)
            row.append(esc(rng(ucur["cartridge"], True, "$")) if ucur else "Not tracked")
        for s in snaps:
            c = s.get("cartridges", {}).get(gen)
            row.append(esc(c["range"]) if c else "")
        rows.append(row)
    drive_rows = []
    for gen in GENS:
        cur = current["generations"][gen]
        m = next(s for s in snaps if s["slug"] == "mar-2026")["drives"].get(gen, {})
        r = [f"<strong>{gen}</strong>", esc(rng(cur.get("driveInternal", {}), False)), esc(rng(cur.get("driveExternal", {}), False))]
        if not MKT.is_us:
            ug = US.generations[gen]
            r += [esc(rng(ug.get("driveInternal", {}), False, "$")), esc(rng(ug.get("driveExternal", {}), False, "$"))]
        r += [esc(m.get("internal", "")), esc(m.get("external", ""))]
        drive_rows.append(r)
    cards = "".join(
        f'<a href="/lto-tape-price-trend/{s["slug"]}">{esc(s["label"])}<span>{esc(s["summary"].split(". ")[0].rstrip(".") + ".")}</span></a>' for s in snaps
    )
    if MKT.is_us:
        intro = "Every LTO price snapshot TapeBackup.org has published since September 2025, side by side. Current prices live on the <a href=\"/lto-tape-price-trend\">LTO price tracker</a>; when a new edition goes out, the previous one is archived here."
        drive_head = ["Generation", f"Internal, {CURRENT_LABEL}", f"External, {CURRENT_LABEL}", "Internal, March 2026", "External, March 2026"]
        drive_intro = f"Drive prices were first tracked in March 2026 as estimated street ranges. The {CURRENT_LABEL} figures are seller listings for new standalone SAS drives."
        panel = f"{len(snaps) + 1} editions from September 2025 to {CURRENT_LABEL}. Older editions mixed individual listings and rounded guide ranges, so read the trend, not the cents."
    else:
        intro = f"Every LTO price snapshot TapeBackup.org has published since September 2025, side by side. Prices in {MKT.country} start with the {CURRENT_LABEL} edition; the older columns are US snapshots in US dollars before sales tax. Current prices live on the <a href=\"/lto-tape-price-trend\">LTO price tracker</a>."
        drive_head = ["Generation", f"Internal, {MKT.country_short}", f"External, {MKT.country_short}", f"Internal, US {CURRENT_LABEL}", f"External, US {CURRENT_LABEL}", "Internal, US March 2026", "External, US March 2026"]
        drive_intro = f"US drive prices were first tracked in March 2026 as estimated street ranges. The {CURRENT_LABEL} figures are seller listings for new standalone SAS drives, in {MKT.country} including VAT and in the US before sales tax."
        panel = f"{len(snaps) + 1} US editions from September 2025 to {CURRENT_LABEL}, plus the first {MKT.country_short} edition. Older editions mixed individual listings and rounded guide ranges, so read the trend, not the cents."
    body = f"""<section class="hero"><div class="container hero-grid"><div class="hero-copy">
<p class="eyebrow">LTO price history</p><h1>LTO Tape Price History</h1>
<p>{intro}</p>
</div><aside class="hero-panel"><p class="panel-label">Snapshots</p><p class="panel-copy">{panel}</p></aside></div></section>
<main class="page"><div class="container"><div class="section-stack">
<section class="section-card" id="cartridges"><p class="eyebrow">Media</p><h2>LTO cartridge price history</h2>{table(head, rows, "LTO cartridge price history")}</section>
<section class="section-card" id="drives"><p class="eyebrow">Hardware</p><h2>LTO drive price history</h2>
<p>{drive_intro}</p>
{table(drive_head, drive_rows, "LTO drive price history")}</section>
<section class="section-card" id="snapshots"><p class="eyebrow">Archive</p><h2>Archived snapshots</h2><div class="link-grid">{cards}</div></section>
</div></div></main>"""
    desc = "LTO tape price history from September 2025 to 2026: LTO-5 to LTO-10 cartridge and drive prices from every archived TapeBackup.org snapshot."
    ld = [breadcrumb_ld([("Home", "/"), ("LTO Prices", "/lto-tape-price-trend"), ("Price history", path)])]
    write(path, page(path, "LTO Tape Price History: 2025 to 2026 | TapeBackup", desc, body, ld))
    return path


ARCHIVE_TITLES = {
    "aug-2026": "LTO Tape Prices August 2026 (Archive) | TapeBackup",
    "mar-2026": "LTO Tape and Drive Prices March 2026 (Archive)",
    "jan-2026": "LTO Tape Prices January 2026 (Archive) | TapeBackup",
    "nov-dec-2025": "LTO Tape Prices Nov to Dec 2025 (Archive) | TapeBackup",
    "sep-oct-2025": "LTO Tape Prices Sep to Oct 2025 (Archive) | TapeBackup",
}


def build_archive(snap, history):
    path = f"/lto-tape-price-trend/{snap['slug']}"
    parts = []
    rows = []
    for gen in ["LTO-5"] + GENS:
        c = snap.get("cartridges", {}).get(gen)
        if not c:
            continue
        rows.append([f"<strong>{gen}</strong>", f"{NATIVE[gen]:g} TB", esc(c["range"]), esc(c.get("perTB") or range_per_tb(c["range"], gen)), esc(c.get("trend", "").capitalize()), esc(c.get("previous", ""))])
    has_trend = any(r[4] for r in rows)
    has_prev = any(r[5] for r in rows)
    headers = ["Generation", "Native", "Cartridge price", "Per native TB"] + (["Trend"] if has_trend else []) + (["Previous range"] if has_prev else [])
    rows = [r[:4] + ([r[4]] if has_trend else []) + ([r[5]] if has_prev else []) for r in rows]
    parts.append(f'<section class="section-card" id="cartridges"><p class="eyebrow">Media</p><h2>LTO cartridge prices, {esc(snap["label"])}</h2>{table(headers, rows, "Cartridge prices")}</section>')

    vendor_blocks = []
    for gen in ["LTO-5"] + GENS:
        c = snap.get("cartridges", {}).get(gen)
        if c and c.get("vendors"):
            vendor_blocks.append(f"<h3>{gen}: {esc(c['range'])}</h3>" + table(["Brand or part", "Price"], [[esc(v), esc(p)] for v, p in c["vendors"]], f"{gen} prices", num_cols=(1,)))
    if vendor_blocks:
        parts.append(f'<section class="section-card" id="by-brand"><p class="eyebrow">By brand</p><h2>Prices by manufacturer</h2>{"".join(vendor_blocks)}</section>')

    if snap.get("drives"):
        drows = [[f"<strong>{g}</strong>", esc(d["internal"]), esc(d["external"])] for g, d in snap["drives"].items()]
        vend = "".join(
            f"<h3>{esc(v['vendor'])}</h3>" + table(["Generation", "Internal or module", "External"], [[esc(a), esc(b), esc(c)] for a, b, c in v["rows"]], v["vendor"])
            for v in snap.get("driveVendors", [])
        )
        parts.append(f'<section class="section-card" id="drives"><p class="eyebrow">Hardware</p><h2>LTO drive prices, {esc(snap["label"])}</h2><p>Estimated street prices for single standalone drives.</p>{table(["Generation", "Internal or module", "External or tabletop"], drows, "Drive prices")}{vend}</section>')

    if snap.get("notes"):
        parts.append('<section class="section-card" id="notes"><p class="eyebrow">Notes</p><h2>Notes on this snapshot</h2><ul>' + "".join(f"<li>{esc(n)}</li>" for n in snap["notes"]) + "</ul></section>")

    others = "".join(
        f'<a href="/lto-tape-price-trend/{s["slug"]}">{esc(s["label"])}<span>Archived snapshot</span></a>' for s in history["snapshots"] if s["slug"] != snap["slug"]
    )
    parts.append(f'<section class="section-card" id="more"><p class="eyebrow">More history</p><h2>Other LTO price snapshots</h2><div class="link-grid"><a href="/lto-tape-price-trend">{CURRENT_LABEL} prices<span>Current edition</span></a><a href="/lto-tape-price-trend/history">All history<span>Every generation side by side</span></a>{others}</div></section>')

    body = f"""<section class="hero"><div class="container hero-grid"><div class="hero-copy">
<p class="eyebrow">Archived LTO prices · {esc(snap['period'])}</p><h1>LTO Tape Prices: {esc(snap['label'])}</h1>
<p>{esc(snap['summary'])}</p></div>
<aside class="hero-panel"><p class="panel-label">Archived snapshot</p><p class="panel-copy">{esc(snap['source'])}</p></aside></div></section>
<main class="page"><div class="container">
<div class="archive-banner">This is an archived price snapshot and is no longer updated. For current prices see the <a href="/lto-tape-price-trend">{CURRENT_LABEL} LTO price tracker</a>.</div>
<div class="section-stack">{''.join(parts)}</div></div></main>"""
    gens_listed = [g for g in ["LTO-5"] + GENS if g in snap.get("cartridges", {})]
    desc = f"Archived LTO tape prices for {snap['period']}: {gens_listed[0]} to {gens_listed[-1]} cartridge prices" + (" and drive prices" if snap.get("drives") else "") + ", kept for price history."
    if len(desc) > 158:
        desc = f"Archived LTO prices for {snap['label']}: {gens_listed[0]} to {gens_listed[-1]} cartridges" + (" and drives" if snap.get("drives") else "") + ", kept for price history."
    ld = [breadcrumb_ld([("Home", "/"), ("LTO Prices", "/lto-tape-price-trend"), ("Price history", "/lto-tape-price-trend/history"), (snap["label"], path)])]
    write(path, page(path, ARCHIVE_TITLES[snap["slug"]], desc, body, ld))
    return path


def build_all(market="us"):
    """Build the price pages for one market. Archives exist only in English (US data)."""
    set_market(market)
    current = current_data()
    history = load("price-history.json")
    paths = [build_hub(current, history), build_history(current, history)]
    for gen in GENS:
        paths.append(build_gen_page(gen, current["generations"][gen], history, current))
    if MKT.is_us:
        for snap in history["snapshots"]:
            paths.append(build_archive(snap, history))
    return paths, current


if __name__ == "__main__":
    print("\n".join(build_all()[0]))
