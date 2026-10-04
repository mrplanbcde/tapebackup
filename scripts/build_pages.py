"""Build the non-price pages: restored guides, tools, contact, homepage, 404.

The guides under data/legacy-pages/ were captured from the React app that ran
the site until June 2026. When that app was replaced by a homepage-only file,
these URLs silently started rendering the homepage. They are now plain HTML.
"""

import html
import json
import os
import re

from bs4 import BeautifulSoup, NavigableString, Tag

import build_prices as BP
from markets import brand_of
from site_shell import GENS, ROOT, SITE, breadcrumb_ld, esc, faq_html, faq_ld, hubspot_cta, page, slug_for, write, figure

KEEP_BLOCK = {"h1", "h2", "h3", "h4", "p", "ul", "ol", "table", "blockquote", "pre", "hr"}
INLINE = {"strong", "b", "em", "i", "a", "code", "br", "span", "sup", "sub", "small"}
DROP = {"svg", "script", "style", "input", "select", "textarea", "form", "canvas", "nav", "img", "label", "noscript"}
ALLOWED_ATTRS = {"a": {"href"}, "td": {"colspan", "rowspan"}, "th": {"colspan", "rowspan"}}

LEGACY = {
    "/why-tape": ("why-tape", "Tape Storage and Tape Backup: Why LTO Still Wins", "Why LTO tape still wins for long-term archives: lowest cost per TB, offline air-gap protection against ransomware, WORM media and decades of shelf life."),
    "/why-tape/lto-vs-hdd": ("why-tape__lto-vs-hdd", "LTO Tape vs HDD for Long-Term Storage | TapeBackup", "LTO tape vs hard drives for backup and archive: lifespan, cost per TB, ransomware protection, access speed and which one fits your data."),
    "/resources": ("resources", "Tape Backup Resources and LTO Guides | TapeBackup", "LTO tape backup resources: price guides, buying advice for used tapes, backup software reviews, vendor links and official LTO references in one place."),
    "/resources/cheap-lto-tapes": ("resources__cheap-lto-tapes", "Cheap LTO Tapes: How to Buy Used Tape Safely", "How to buy cheap or used LTO tapes without losing data: what to check, which sellers and generations to avoid, and when new media is worth paying for."),
    "/resources/tape-backup-software/catalogicdpx": ("resources__tape-backup-software__catalogicdpx", "Catalogic DPX Review: Tape Backup and LTO Support", "Catalogic DPX reviewed as tape backup software: LTO drive and library support, NDMP, disk to tape workflows, encryption and where it fits."),
    "/about": ("about", "About TapeBackup.org: Independent LTO Tape Resource", "About TapeBackup.org, an independent LTO tape resource, plus a plain guide to what LTO means, how linear tape works and why it is still used."),
    "/comparisons": ("comparisons", "Tape vs Disk vs Cloud Backup Compared | TapeBackup", "LTO tape, disk and cloud backup compared on cost per TB, recovery speed, ransomware protection, lifespan and energy use, with guidance on each."),
    "/lto-tape-brand": ("lto-tape-brand", "LTO Tape Brands: Who Really Makes Your Cartridges", "Only Fujifilm and Sony make LTO tape. See how HPE, IBM, Quantum and Dell cartridges compare, and whether the brand on the label matters."),
    "/best-tape-backup-software": ("best-tape-backup-software", "Best Tape Backup Software in 2026 | TapeBackup", "The best tape backup software for LTO in 2026 compared: Catalogic DPX, Veeam, Commvault and others on tape support, licensing and migration paths."),
}

def fx_round(usd, step):
    """A rough USD estimate in the current market's currency, rounded to a sensible step."""
    v = BP.MKT.from_usd(usd)
    if not BP.MKT.is_us:
        step = step * (5 if BP.MKT.currency == "PLN" and step < 50 else 1)
    return int(round(v / step) * step) if step else v


def fxm(usd, step):
    return f"{BP.MKT.sym}{fx_round(usd, step):,}"


def price_facts():
    """Figures the guides quote, computed from the current market's listings."""
    g = BP.MKT.generations
    c = lambda gen: g[gen]["cartridge"]
    drive = lambda gen: g[gen].get("driveInternal") or {}
    l8, l9 = c("LTO-8"), c("LTO-9")
    sym = BP.MKT.sym
    lo89 = min(x for x in (l8.get("perTBLow"), l9.get("perTBLow")) if x is not None)
    hi89 = max(x for x in (l8.get("perTBHigh"), l9.get("perTBHigh")) if x is not None)
    cur_plural = {"USD": "dollars", "EUR": "euros", "PLN": "złoty"}[BP.MKT.currency]
    return {
        "lto9_pertb0": BP.per_tb0(l9), "lto9_pertb": BP.per_tb(l9), "lto8_pertb": BP.per_tb(l8),
        "lto10_pertb": BP.per_tb(c("LTO-10")), "lto10_pertb0": BP.per_tb0(c("LTO-10")),
        "lto6_rng0": BP.rng0(c("LTO-6")), "lto7_rng0": BP.rng0(c("LTO-7")), "lto8_rng0": BP.rng0(l8),
        "lto9_rng0": BP.rng0(l9), "lto10_rng0": BP.rng0(c("LTO-10")),
        "media_pertb_89": f"{sym}{round(lo89)} to {sym}{round(hi89)}",
        "drive_lo8": BP.money0(drive("LTO-8").get("low")) if drive("LTO-8").get("low") else "n/a",
        "drive_hi9": BP.money0(drive("LTO-9").get("high")) if drive("LTO-9").get("high") else "n/a",
        "drive8_rng0": BP.rng0(drive("LTO-8")), "drive9_rng0": BP.rng0(drive("LTO-9")),
        "hdd_pertb": f"{fxm(15, 5)} to {fxm(30, 5)}", "cloud_pertb_year": f"{fxm(20, 5)} to {fxm(50, 5)}+",
        "ext_premium": f"{fxm(1000, 500)} to {fxm(2000, 500)}", "lib_from": fxm(5000, 500),
        "tco_tape": fxm(75000, 5000), "tco_disk": fxm(300000, 10000), "tco_cloud": fxm(2000000, 100000),
        "tco10y_tape": f"{fxm(5, 1)} to {fxm(10, 1)}", "tco10y_cloud": f"{fxm(200, 10)} to {fxm(500, 10)}+",
        "month": BP.CURRENT_LABEL, "cur_plural": cur_plural,
        "temp_install": "50-110°F (10-43°C)" if BP.MKT.is_us else "10-43°C",
        "temp_store": "60-90°F (16-32°C)" if BP.MKT.is_us else "16-32°C",
        "usd_word": "$" if BP.MKT.is_us else "USD ",
    }


def brand_split(gen):
    """Price range of major-brand (HPE/IBM/Quantum/Dell) and OEM (Fujifilm/Sony) single cartridges."""
    dps = [d for d in (BP.MKT.generations[gen]["cartridge"].get("datapoints") or []) if not d.get("pack")]
    major = [d["price"] for d in dps if brand_of(d) in ("HPE", "IBM", "Quantum", "Dell")]
    oem = [d["price"] for d in dps if brand_of(d) in ("Fujifilm", "Sony")]
    f = lambda xs: BP.rng0({"low": min(xs), "high": max(xs)}) if xs else "Not listed"
    return f(major), f(oem)


def price_rewrites():
    """(old, new) replacements for prices quoted in the restored guides, filled from current listings."""
    F = price_facts()
    rw = [
        ("Drives range from $3,000 (LTO-8) to $6,500 (LTO-9).", "New standalone drives list from about {drive_lo8} (LTO-8) to {drive_hi9} (LTO-9) as of {month}."),
        ("LTO-9 tapes cost ~$70-90 (18 TB = $4-5/TB). LTO-10 approaches $3-4/TB.", "LTO-9 tapes cost about {lto9_rng0} in {month} ({lto9_pertb} per TB). LTO-10 30 TB tapes run about {lto10_pertb} per TB."),
        ("tape media costing approximately $3-6 per TB", "tape media costing roughly {media_pertb_89} per TB on LTO-8 and LTO-9"),
        ("LTO-8 tapes (12 TB native) typically cost $70-90, translating to approximately $6-7.50 per TB", "LTO-8 tapes (12 TB native) cost about {lto8_rng0} in {month}, roughly {lto8_pertb} per TB"),
        ("LTO-9 tapes (18 TB native) provide similar per-TB pricing, while LTO-10 (30 TB native) is expected to approach $3-4 per TB at volume.", "LTO-9 tapes (18 TB native) cost {lto9_pertb} per TB, while LTO-10 30 TB tapes still cost {lto10_pertb} per TB."),
        ("The primary investment is the tape drive itself ($3,000-$6,500)", "The primary investment is the tape drive itself (about {drive_lo8} to {drive_hi9} for new LTO-8 and LTO-9 drives in {month})"),
        ("with tape libraries ranging from $5,000 to hundreds of thousands of dollars", "with tape libraries ranging from {lib_from} to hundreds of thousands of {cur_plural}"),
        ("cost-efficiency ($3-6/TB)", "cost-efficiency (about {lto9_pertb0} per TB on LTO-9)"),
        ("<strong>$3-6/TB</strong> for LTO-10 media (vs $15-30/TB for disk)", "<strong>{lto9_pertb0} per TB</strong> for LTO-9 media and {lto10_pertb0} for LTO-10 (vs {hdd_pertb} per TB for disk)"),
        ("<td>$3-6</td><td>$15-30</td><td>$20-50+/year</td>", "<td>{media_pertb_89}</td><td>{hdd_pertb}</td><td>{cloud_pertb_year}/year</td>"),
        ("<td>$5-10</td><td>$15-30</td><td>$200-500+</td>", "<td>{tco10y_tape}</td><td>{hdd_pertb}</td><td>{tco10y_cloud}</td>"),
        ("<p>$5-10</p><p>per TB</p>", "<p>{media_pertb_89}</p><p>per TB</p>"),
        ("<p>$15-30</p><p>per TB</p>", "<p>{hdd_pertb}</p><p>per TB</p>"),
        ("<p>$20-50+</p><p>per TB/year</p>", "<p>{cloud_pertb_year}</p><p>per TB/year</p>"),
        ("Tape = ~$75K | Disk = ~$300K | Cloud = ~$2M+", "Tape = ~{tco_tape} | Disk = ~{tco_disk} | Cloud = ~{tco_cloud}+"),
        ("~$75K", "~{tco_tape}"), ("~$300K", "~{tco_disk}"), ("~$2M+", "~{tco_cloud}+"),
        ("<h4>LTO-8 Drives</h4><p>$3,000-4,500</p>", "<h4>LTO-8 Drives</h4><p>{drive8_rng0}</p>"),
        ("<h4>LTO-9 Drives</h4><p>$4,500-6,500</p>", "<h4>LTO-9 Drives</h4><p>{drive9_rng0}</p>"),
        ("$1.12 billion in 2024", "{usd_word}1.12 billion in 2024"),
        ("$1.85 billion by 2033", "{usd_word}1.85 billion by 2033"),
        ("(50-110°F, 20-80% humidity)", "({temp_install}, 20-80% humidity)"),
        ("at 60-90°F with 20-80% humidity", "at {temp_store} with 20-80% humidity"),
        ("<h3>Modern Standard (Readily Available)Recommended</h3>", "<h3>Modern Standard (Readily Available), Recommended</h3>"),
        ("<h3>Bleeding Edge (New Release)New</h3>", "<h3>Bleeding Edge (New Release)</h3>"),
        ("Data centers spend approximately 75% of their energy consumption on cooling systems.", "Cooling can account for 30 to 40% of a data center's energy use."),
        ("<p>Tier 1:Disk", "<p>Tier 1: Disk"),
        ("supporting the latest LTO-9 drives", "supporting current LTO-9 and LTO-10 drives"),
        ("<p>80 MB/s • Added WORM and encryption</p>", "<p>80 MB/s • Added WORM</p>"),
        ("Compact 1U rackmount size, most common for libraries", "Compact form factor, most common in desktop units and libraries"),
        ("<p>400 MB/s • 45 TB compressed • Current gen</p>", "<p>400 MB/s • 45 TB compressed • Mainstream generation</p>"),
        ("<h4>LTO-10 (2026)</h4>", "<h4>LTO-10 (2025)</h4>"),
        ("which will double capacities again.", "which raises capacity to 30 TB per cartridge, and 40 TB with the newer cartridge."),
        ("(often exceeding 400 MB/s native)", "(up to 400 MB/s native)"),
        ("with the two vendors explicitly requested for deep-dive analysis:", "with two vendors that deserve a closer look:"),
        (" Criteria 1:", " Criterion 1:"), (" Criteria 2:", " Criterion 2:"), (" Criteria 3:", " Criterion 3:"), (" Criteria 4:", " Criterion 4:"), (" Criteria 5:", " Criterion 5:"), ("<p>Tier 2:Cl", "<p>Tier 2: Cl"), ("<p>Tier 3:", "<p>Tier 3: "),
        ("<td>~$250 - $350+</td>", "<td>~{lto10_rng0} (30 TB)</td>"),
    ]
    # Brand guide: LTO-3 to LTO-5 are estimates (converted); LTO-6 to LTO-9 come from the listings, split by brand.
    for old, lo, hi in (("~$30 - $50", 30, 50), ("~$15 - $20", 15, 20), ("~$35 - $60", 35, 60), ("~$20 - $25", 20, 25), ("~$30 - $45", 30, 45)):
        rw.append((f"<td>{old}</td>", f"<td>~{fxm(lo, 5)} to {fxm(hi, 5)}</td>"))
    rows = []
    for gen, old_major, old_oem in (("LTO-6", "~$40 - $55", "~$30 - $35"), ("LTO-7", "~$60 - $80", "~$50 - $60"),
                                    ("LTO-8", "~$70 - $80", "Rarely worth it, new is ~$70 - $80"),
                                    ("LTO-9", "~$92 - $112", "Rarely worth it, new is ~$92 - $112")):
        major, oem = brand_split(gen)
        rows.append((gen, old_major, old_oem, major, oem))
    return [(o, n.format(**F)) for o, n in rw], rows


def apply_price_rewrites(flow):
    rw, brand_rows = price_rewrites()
    for old, new in rw:
        flow = flow.replace(esc(old).replace("&#x27;", "'"), new).replace(old, new)
    for gen, old_major, old_oem, major, oem in brand_rows:
        # the brand table rows, whose price cells follow the generation and capacity cells
        pat = re.compile(r"(<tr><td>" + re.escape(gen) + r"(?: ⭐)?</td><td>[^<]*</td><td>)[^<]*(</td><td>)[^<]*(</td>)")
        flow = pat.sub(lambda m: f"{m.group(1)}{esc(major)}{m.group(2)}{esc(oem)}{m.group(3)}", flow)
    return flow


DROP_SECTIONS = {"Downloadable Resources"}


# ---------------------------------------------------------------- lists to tables
# Pages with more than five bullet groups read better with the parallel ones as tables.

def _table(headers, rows):
    th = "".join(f"<th>{h}</th>" for h in headers)
    return '<div class="table-wrap"><table><tr>' + th + "</tr>" + "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows) + "</table></div>"


def _items(ul_html):
    return [re.sub(r"^\s*(?:<p>)?\s*[•✓]?\s*", "", re.sub(r"</p>\s*$", "", li.strip())).strip() for li in re.findall(r"<li>(.*?)</li>", ul_html, re.S)]


def _split(item):
    label, _, text = item.partition(": ")
    return [f"<strong>{label.strip()}</strong>", text.strip()]


def _ul_after(flow, marker):
    i = flow.index(marker)
    m = re.compile(r"<ul>.*?</ul>", re.S).search(flow, i)
    return m


def _replace_ul(flow, marker, build):
    m = _ul_after(flow, marker)
    return flow[:m.start()] + build(_items(m.group(0))) + flow[m.end():]


def lists_to_tables(path, flow):
    if path == "/best-tape-backup-software":
        flow = _replace_ul(flow, "2.3 Criterion 3", lambda it: _table(["Requirement", "Why it matters"], [_split(x) for x in it]))
        # DPX: the block-level mechanism and the tape features become one feature table
        m1 = _ul_after(flow, "Technical Deep Dive: The Block-Level Advantage")
        m2 = _ul_after(flow, "Enterprise Tape Features:")
        feats = [_split(x) for x in _items(m1.group(0)) + _items(m2.group(0))]
        flow = flow[:m2.start()] + flow[m2.end():]
        flow = flow.replace("<h4>Enterprise Tape Features:</h4>", "", 1)
        flow = flow[:m1.start()] + _table(["Catalogic DPX feature", "How it works"], feats) + flow[m1.end():]
        flow = _replace_ul(flow, "Technical Deep Dive: Byte-Level Replication", lambda it: _table(["i2Backup feature", "How it works"], [_split(x) for x in it]))
        # ICBC: challenges and outcomes pair up row by row
        before = _ul_after(flow, "4.1 The Challenge")
        after = _ul_after(flow, "4.3 The Outcome")
        b_items, a_items = [_split(x) for x in _items(before.group(0))], [_split(x) for x in _items(after.group(0))]
        pair = {"Cost": "Cost Reduction", "Complexity": "Simplified Operations", "Agility": "Efficiency Gains"}
        a_by = {re.sub("<[^>]+>", "", a[0]): a for a in a_items}
        rows = [[b[0], b[1], a_by[pair[re.sub("<[^>]+>", "", b[0])]][0] + "<br>" + a_by[pair[re.sub("<[^>]+>", "", b[0])]][1]] for b in b_items]
        flow = flow[:after.start()] + flow[after.end():]
        flow = flow[:before.start()] + _table(["Problem with NBU", "Detail", "Result after i2Backup"], rows) + flow[before.end():]
    if path == "/why-tape":
        # cost, energy and tier cards
        m = re.search(r"<h3>LTO Tape</h3><p>(.*?)</p><p>(.*?)</p><p>(.*?)</p><h3>Disk Storage</h3><p>(.*?)</p><p>(.*?)</p><p>(.*?)</p><h3>Cloud Storage</h3><p>(.*?)</p><p>(.*?)</p><p>(.*?)</p>", flow)
        g = m.groups()
        flow = flow[:m.start()] + _table(["Storage", "Cost", "Unit", "What drives the cost"], [["LTO Tape", g[0], g[1], g[2]], ["Disk Storage", g[3], g[4], g[5]], ["Cloud Storage", g[6], g[7], g[8]]]) + flow[m.end():]
        flow = _replace_ul(flow, "<h3>Comparison</h3>", lambda it: _table(["Storage", "Typical lifespan"], [_split(x) for x in it]))
        flow = _replace_ul(flow, "The 3-2-1-1-0 Backup Rule", lambda it: _table(["Number", "Rule"], [[re.match(r"<strong>(.*?)</strong>", x).group(1), re.sub(r"^<strong>.*?</strong>\s*", "", x)] for x in it]))
        p = _ul_after(flow, "<h3>Protection Against</h3>")
        s = _ul_after(flow, "<h3>Additional Security</h3>")
        pi, si = _items(p.group(0)), _items(s.group(0))
        flow = flow[:s.start()] + flow[s.end():]
        flow = flow.replace("<h3>Additional Security</h3>", "", 1)
        flow = flow[:p.start()] + _table(["Protection against", "Additional security"], list(map(list, zip(pi, si)))) + flow[p.end():]
        flow = flow.replace("<h3>Protection Against</h3>", "<h3>Protection and security</h3>", 1)
        m = re.search(r"<h3>Tape Storage</h3><p>(.*?)</p><p>(.*?)</p><h3>Disk Arrays</h3><p>(.*?)</p><p>(.*?)</p><h3>Cloud Storage</h3><p>(.*?)</p><p>(.*?)</p>", flow)
        g = m.groups()
        flow = flow[:m.start()] + _table(["Storage", "Power", "Note"], [["Tape Storage", g[0], g[1]], ["Disk Arrays", g[2], g[3]], ["Cloud Storage", g[4], g[5]]]) + flow[m.end():]
        m = re.search(r"<p>1</p><h3>(.*?)</h3><p>(.*?)</p><p>2</p><h3>(.*?)</h3><p>(.*?)</p><p>3</p><h3>(.*?)</h3><p>(.*?)</p>", flow)
        g = m.groups()
        flow = flow[:m.start()] + _table(["Tier", "Storage", "Role"], [["1", g[0], g[1]], ["2", g[2], g[3]], ["3", g[4], g[5]]]) + flow[m.end():]
    if path in ("/comparisons", "/why-tape/lto-vs-hdd"):
        heads = (["When to Choose LTO Tape", "When to Choose Disk Storage", "When to Choose Cloud Storage"] if path == "/comparisons"
                 else ["When LTO Is the Better Choice", "When HDD Is the Better Choice"])
        cols = []
        for h in heads:
            m = re.search(r"<h3>" + re.escape(h) + r"</h3>\s*(<ul>.*?</ul>)", flow, re.S)
            cols.append(_items(m.group(1)))
            flow = flow[:m.start()] + ("\x00" if not cols[1:] else "") + flow[m.end():]
        n = max(len(c) for c in cols)
        rows = [[c[i] if i < len(c) else "" for c in cols] for i in range(n)]
        flow = flow.replace("\x00", _table(heads, rows), 1)
    return flow

# SEO fixes from the October 2026 Search Console review (pages ranking 9 to 100).
H1_FIX = {
    "/why-tape": "Why Use Tape Storage for Backup and Archive?",
    "/comparisons": "Tape vs Disk vs Cloud Backup Compared",
}
LEAD_FIX = {
    "/why-tape": "Tape storage keeps a copy of your data offline, on media that costs little per terabyte and lasts decades on a shelf. Here is where it beats disk and cloud, and where it does not.",
    "/comparisons": "Each option below is compared on cost per terabyte, restore speed, ransomware protection, lifespan and energy use, so you can pick the right mix for recent backups and long-term copies.",
    "/resources": "Guides, charts and references for buying and running LTO tape: prices, capacity, drives, software, migration and data recovery.",
}
# (insert after section card n, figure file, alt text, caption)
LEGACY_FIGURES = {
    "/why-tape": [
        (0, ("tape-disk-cloud-cost.svg", "Relative 10-year cost per terabyte: tape 1x, disk about 3x, cloud 40x or more",
             "Over ten years, keeping a terabyte on disk costs about three times as much as on tape, and in a standard cloud tier forty times or more, using the ranges in our <a href=\"/comparisons\">tape, disk and cloud comparison</a>.")),
        (2, ("tape-air-gap.svg", "Ransomware reaches networked disks; a cartridge on a shelf is out of reach",
             "Ransomware can encrypt anything it can reach over the network. A cartridge ejected to a shelf, especially a WORM cartridge, is out of its reach.")),
    ],
    "/comparisons": [
        (0, ("tape-disk-cloud-scorecard.svg", "Tape, disk and cloud rated on cost, restore speed, offline safety, lifespan and energy",
             "More dots is better. Tape leads on cost per terabyte, offline safety, lifespan and energy; disk leads on restore speed; cloud sits in between and charges to read data back.")),
    ],
    "/resources": [
        (0, ("lto-guide-map.svg", "Prices, capacity, drives and software: the path through the LTO guides",
             "A practical order: check <a href=\"/lto-tape-price-trend\">prices</a>, size the archive with the <a href=\"/backup-calculator\">calculator</a>, choose a <a href=\"/why-tape/lto-tape-drive\">drive</a>, then pick <a href=\"/best-tape-backup-software\">software</a> or <a href=\"/resources/ltfs\">LTFS</a>.")),
    ],
}

# AEO: a direct, quotable answer shown first on each guide (checked against the page content and Sep 2026 prices).
ANSWERS = {
    "/why-tape": "Tape is used for archives because it has the lowest cost per terabyte for data you rarely read (about {lto9_pertb0} per TB on LTO-9 in {month}), a cartridge on a shelf is offline and out of reach of ransomware, and it draws no power when idle.",
    "/why-tape/lto-tape-drive": "An LTO tape drive reads and writes Linear Tape-Open cartridges. Each generation roughly doubles capacity (LTO-9 holds 18 TB native, LTO-10 holds 30 TB or 40 TB), and drives up to LTO-9 read and write the previous generation, while LTO-10 drives only use LTO-10 media.",
    "/why-tape/lto-vs-hdd": "For long-term archives LTO tape usually beats hard drives: cartridges are rated for decades on a shelf, cost less per terabyte and sit offline. Hard drives win when you need fast random access or only store a few terabytes.",
    "/comparisons": "Tape is cheapest for large, rarely read archives and gives an offline copy; disk is best for fast restores of recent data; cloud is easiest for offsite copies but costs more over time and charges to get data back. Most teams combine disk for recent backups with tape or cloud for long-term copies.",
    "/best-tape-backup-software": "The best tape backup software depends on how central tape is: Catalogic DPX is strongest when tape is the main archive target, Veeam and Commvault suit virtualized or large mixed estates that use tape as a secondary copy, and Nakivo is a lower-cost option for small environments.",
    "/resources": "Start with the LTO price tracker for current tape and drive prices, the buying guide for used tapes, the backup software comparison, and the official LTO Program site for specifications.",
    "/resources/cheap-lto-tapes": "Used LTO tapes are safe to buy if you verify them before trusting data to them: buy from sellers who state load counts and offer returns, avoid unknown-history bulk lots, and run a full write and read-back test on every cartridge.",
    "/resources/tape-backup-software/catalogicdpx": "Catalogic DPX is enterprise backup software with strong native tape support: it drives most LTO drives and libraries, handles NDMP, supports disk-to-tape and direct-to-tape jobs, and encrypts tape copies for air-gapped retention.",
    "/lto-tape-brand": "Only Fujifilm and Sony manufacture LTO tape. HPE, IBM, Quantum and Dell cartridges contain tape from one of those two, so any certified cartridge of the right generation works in any brand of LTO drive.",
    "/about": "TapeBackup.org is an independent resource on LTO tape backup that tracks tape and drive prices from seller listings and explains how to buy and run tape. It is not affiliated with the LTO Program or any vendor."
}


GUIDE_FAQS = {
    "/why-tape": [
        [
            "Is tape backup still used in 2026?",
            "Yes. The LTO Program reported 160.3 exabytes of LTO capacity shipped in 2025, and shipped capacity in the first quarter of 2026 was 57% higher than a year earlier. Tape is used for long-term archives, offline copies and compliance retention rather than day-to-day restores."
        ],
        [
            "How much does tape cost per terabyte?",
            "New LTO-9 cartridges cost about {lto9_pertb} per native terabyte in {month}, and LTO-8 about {lto8_pertb}. A drive is a separate one-off cost, from roughly {drive_lo8} for LTO-8 to {drive_hi9} for LTO-9."
        ],
        [
            "How does tape protect against ransomware?",
            "A cartridge that has been removed from the drive is offline, so no network attack can reach it. WORM cartridges add a second layer by physically preventing overwrites, and LTO drives support hardware AES-256 encryption for tapes that leave the building."
        ],
        [
            "How long does LTO tape last?",
            "LTO cartridges are rated for about 30 years of archival life in controlled storage. The practical limit is usually drive availability rather than the media, because a drive generation only reads one or two generations back."
        ]
    ],
    "/why-tape/lto-tape-drive": [
        [
            "Which LTO tapes work in which drive?",
            "From LTO-8 onwards a drive reads and writes its own generation and the one before it. LTO-9 drives use LTO-9 and LTO-8 media; LTO-10 drives are the exception and use LTO-10 media only, so keep an older drive if you still need to read LTO-9 or earlier tapes."
        ],
        [
            "How fast is an LTO tape drive?",
            "LTO-9 writes at up to 400 MB/s native, which is about 1.4 TB per hour. Real throughput depends on whether your source can feed the drive steadily; if it cannot, the drive stops and repositions, which is slower and wears the media."
        ],
        [
            "Do I need a special card for a tape drive?",
            "Yes, almost always. Standalone LTO drives are SAS, so the host needs a SAS HBA and the right cable. Thunderbolt models exist for workstations and cost more."
        ],
        [
            "Should I buy an internal or external drive?",
            "Internal half-height drives are cheaper and fit a server or library. External desktop units include a power supply and enclosure and cost roughly {ext_premium} more for the same mechanism."
        ]
    ],
    "/why-tape/lto-vs-hdd": [
        [
            "Is tape cheaper than hard drives?",
            "For capacity you keep and rarely read, yes, once you pass the cost of the drive. LTO-9 media costs about {lto9_pertb0} per TB against roughly {hdd_pertb} per TB for enterprise hard drives, but a tape drive costs thousands up front, so small archives stay cheaper on disk."
        ],
        [
            "Which lasts longer, tape or a hard drive?",
            "Tape. Cartridges are rated for about 30 years in storage, while hard drives are typically replaced every three to seven years and degrade when left unpowered for long periods."
        ],
        [
            "Is tape slower than disk?",
            "For a single file, yes: a tape has to load and wind to the right spot, which takes tens of seconds to minutes. For large sequential reads and writes an LTO-9 drive at 400 MB/s keeps up with most disk arrays."
        ]
    ],
    "/comparisons": [
        [
            "Is tape or cloud cheaper for a long-term archive?",
            "Cloud archive tiers are cheaper to start because there is no hardware to buy; tape wins over several years at scale because the media is a one-off cost and reading it back is free. The break-even depends on how much you store, how long you keep it and how often you restore."
        ],
        [
            "What is the 3-2-1 backup rule?",
            "Keep three copies of your data on two different kinds of media with one copy offsite. Tape is commonly the offsite or offline copy because a cartridge can be removed and stored elsewhere."
        ],
        [
            "Can I use tape and cloud together?",
            "Yes, and most teams do. Recent backups sit on disk for fast restores, an offline tape copy covers ransomware and long retention, and a cloud copy covers site loss."
        ]
    ],
    "/resources/cheap-lto-tapes": [
        [
            "Is it safe to buy used LTO tapes?",
            "It can be, if you test them. Buy from sellers who state the load count and accept returns, avoid unknown-history bulk lots, and write and read back a full cartridge before trusting any data to it."
        ],
        [
            "How many times can an LTO tape be used?",
            "LTO cartridges are specified for hundreds of full file passes, but a used tape's remaining life is unknown unless the seller shares the load count. Drives log this in the cartridge memory, which your backup software can read."
        ],
        [
            "Are cheap LTO tapes fake?",
            "Counterfeit and relabelled cartridges do appear in marketplace listings, often as an older generation relabelled as a newer one. A drive will reject or misreport these, which is another reason to test before use."
        ]
    ],
    "/lto-tape-brand": [
        [
            "Does the brand of LTO tape matter?",
            "Not much. Only Fujifilm and Sony make LTO tape, so an HPE, IBM, Quantum or Dell cartridge contains tape from one of them. Any certified cartridge of the right generation works in any brand of LTO drive."
        ],
        [
            "Why do some brands cost more?",
            "Price differences come from packaging, barcode labelling, warranty terms and the reseller channel rather than the tape itself. Pre-labelled library packs and WORM versions carry a premium."
        ],
        [
            "Do tape libraries require matching media?",
            "No. Libraries need the right generation and, for automation, barcode labels in the format the library expects. The brand on the shell is not a requirement."
        ]
    ],
    "/best-tape-backup-software": [
        [
            "What software do I need to write to LTO tape?",
            "Any backup product with native tape support, or LTFS if you want to use the tape like a filesystem. LTFS is free and good for media archives; backup software adds catalogues, scheduling, verification and retention."
        ],
        [
            "Is LTFS enough on its own?",
            "For a small media archive, often yes. It breaks down when you need a searchable catalogue across many cartridges, automated rotation, verification records or multi-copy retention policies."
        ],
        [
            "Which backup software is cheapest for tape?",
            "Catalogic DPX is usually the lowest total cost when tape is the main target, and Nakivo is the cheaper option for small environments. Veeam and Commvault cost more but cover large virtual estates more thoroughly."
        ]
    ],
    "/backup-calculator": [
        [
            "How many LTO tapes do I need?",
            "Divide your data by the native capacity of the generation and multiply by the number of copies, ignoring compression: 100 TB with two copies is about 12 LTO-9 cartridges. Compression only helps with compressible data and should not be counted on for planning."
        ],
        [
            "When is tape cheaper than disk or cloud?",
            "From roughly 15 TB upwards, once the cost of the drive is spread across enough cartridges. Below that, a NAS plus a cloud cold tier is usually cheaper and simpler."
        ],
        [
            "Does compression change the number of tapes?",
            "Only for compressible data. Vendors quote 2.5:1, but video and images are already compressed and encrypted files cannot be compressed, so they store close to native capacity."
        ]
    ],
    "/backup-software-finder": [
        [
            "Which backup software is best for tape libraries?",
            "Catalogic DPX has the widest drive and library support and handles NDMP, which matters for NAS backups. Veeam and Commvault support tape well as a secondary copy in larger virtual estates."
        ],
        [
            "Can I back up Microsoft 365 to tape?",
            "Not directly. Back up the SaaS data with a tool such as Veeam for Microsoft 365, then copy its repository to tape if you need an offline or long-retention copy."
        ]
    ]
}


def clean_inline(node):
    """Return sanitized inline HTML for a node."""
    if isinstance(node, NavigableString):
        return esc(str(node)).replace("&#x27;", "'").replace("&quot;", '"')
    if not isinstance(node, Tag) or node.name in DROP:
        return ""
    if node.name == "button":
        return "".join(clean_inline(c) for c in node.children)
    inner = "".join(clean_inline(c) for c in node.children)
    name = {"b": "strong", "i": "em"}.get(node.name, node.name)
    if name == "br":
        return "<br>"
    if name == "a":
        href = node.get("href", "")
        if not href or href == "#":
            return inner
        ext = ' rel="noopener" target="_blank"' if href.startswith("http") else ""
        return f'<a href="{esc(href)}"{ext}>{inner}</a>'
    if name in ("strong", "em", "code", "sup", "sub"):
        return f"<{name}>{inner}</{name}>" if inner.strip() else inner
    return inner


def clean_block(node):
    name = node.name
    if name in ("h5", "h6"):
        name = "h4"
    if name in ("ul", "ol"):
        items = "".join(f"<li>{render_flow(li)}</li>" for li in node.find_all("li", recursive=False))
        return f"<{name}>{items}</{name}>" if items else ""
    if name == "table":
        rows = []
        for tr in node.find_all("tr"):
            cells = "".join(f"<{c.name}>{''.join(clean_inline(x) for x in c.children).strip()}</{c.name}>" for c in tr.find_all(["th", "td"], recursive=False))
            rows.append(f"<tr>{cells}</tr>")
        return f'<div class="table-wrap"><table>{"".join(rows)}</table></div>'
    if name == "hr":
        return ""
    inner = "".join(clean_inline(c) for c in node.children).strip()
    if not inner:
        return ""
    return f"<{name}>{inner}</{name}>"


def render_flow(container):
    """Flatten arbitrary nested markup into clean block HTML."""
    out, inline_buf = [], []

    def flush():
        text = "".join(inline_buf).strip()
        inline_buf.clear()
        if text and re.sub(r"<[^>]+>", "", text).strip():
            out.append(f"<p>{text}</p>")

    for child in container.children:
        if isinstance(child, NavigableString):
            if str(child).strip():
                inline_buf.append(clean_inline(child))
            continue
        if not isinstance(child, Tag) or child.name in DROP:
            continue
        if child.get("aria-label", "").lower() == "breadcrumb":
            continue
        if child.name in KEEP_BLOCK or child.name in ("h5", "h6"):
            if child.name == "p" and child.find(["div", "ul", "table", "h2", "h3"]):
                flush()
                out.append(render_flow(child))
                continue
            flush()
            out.append(clean_block(child))
        elif child.name in INLINE or child.name == "button":
            if child.find(["div", "p", "h2", "h3", "ul", "table"]):
                flush()
                out.append(render_flow(child))
            else:
                inline_buf.append(clean_inline(child))
        else:
            flush()
            out.append(render_flow(child))
    flush()
    return "".join(x for x in out if x)


def split_sections(flow_html):
    """Group the flat flow into section cards at each h2."""
    parts = re.split(r"(?=<h2>)", flow_html)
    sections = []
    for part in parts:
        if not part.strip():
            continue
        m = re.match(r"<h2>(.*?)</h2>", part)
        heading = re.sub(r"<[^>]+>", "", m.group(1)) if m else ""
        if heading in DROP_SECTIONS or heading.startswith("Continue with official"):
            continue
        sections.append(f'<section class="section-card legacy-content">{part}</section>')
    return "".join(sections)


def build_legacy(path, key, title, desc):
    with open(os.path.join(ROOT, "data", "legacy-pages", key + ".json"), encoding="utf-8") as f:
        raw = json.load(f)["html"]
    soup = BeautifulSoup(raw, "html.parser")
    flow = render_flow(soup)
    flow = re.sub(r"<li>(?:\s*[\u2713\u2714\u221a\u2022\u2705]\s*)+", "<li>", flow)
    flow = re.sub(r"<p>(?:\s*[\u2713\u2714\u221a\u2705]\s*)+</p>", "", flow)
    flow = apply_price_rewrites(flow)
    flow = lists_to_tables(path, flow)
    h1 = re.search(r"<h1>(.*?)</h1>", flow)
    h1_text = H1_FIX.get(path, h1.group(1) if h1 else title)
    flow = flow.replace(h1.group(0), "", 1) if h1 else flow
    lead = ""
    m = re.match(r"\s*<p>(.*?)</p>", flow)
    if m:
        lead = LEAD_FIX.get(path, m.group(1))
        flow = flow[m.end():]
    body_sections = split_sections(flow)
    for after, (name, alt, cap) in sorted(LEGACY_FIGURES.get(path, []), reverse=True):
        cards = list(re.finditer(r"</section>", body_sections))
        at = cards[min(after, len(cards) - 1)].end()
        body_sections = body_sections[:at] + f'<section class="section-card">{figure(name, alt, cap)}</section>' + body_sections[at:]
    related = ""
    if path == "/resources":
        related = """<section class="section-card"><p class="eyebrow">Price guides and tools</p><h2>LTO price guides and buying tools</h2><div class="link-grid">
<a href="/lto-tape-price-trend">LTO price tracker<span>September 2026 tape and drive prices</span></a>
<a href="/lto-tape-price-trend/history">LTO price history<span>Snapshots since September 2025</span></a>
<a href="/backup-calculator">Backup calculator<span>Cartridges and cost for your data</span></a>
<a href="/backup-software-finder">Software finder<span>Match software to your tape use</span></a>
<a href="/comparisons/tape-vs-cloud-5-year-cost">Tape vs cloud, 5-year cost<span>What an archive really costs</span></a>
<a href="/resources/lto-tape-migration">LTO tape migration<span>Move an archive to newer media</span></a>
<a href="/resources/tape-storage-market">Tape storage market<span>Shipments, supply and prices</span></a>
<a href="/lto-tape">What is LTO tape<span>The format in one page</span></a>
<a href="/lto-tape-capacity">LTO capacity chart<span>LTO-1 to LTO-14</span></a>
<a href="/why-tape/lto-tape-drive">LTO tape drive buying guide<span>Which drive to buy</span></a>
<a href="/lto-tape-library">LTO tape libraries<span>Autoloaders and libraries</span></a>
<a href="/resources/ltfs">LTFS explained<span>Tape as a file system</span></a>
<a href="/resources/lto-tape-data-recovery">LTO tape data recovery<span>Reading old tapes</span></a>
<a href="/why-tape/lto-tape-lifespan">LTO tape lifespan<span>How long tapes last</span></a>
<a href="/resources/lto-cleaning-tapes-and-labels">Cleaning tapes and labels<span>Supplies and handling</span></a>
<a href="/lto-tape-news">LTO tape news<span>What changed this month</span></a>
<a href="/lto-tape-brand">LTO tape brands<span>Who really makes the tape</span></a>
<a href="/tape-q-and-a">Tape Q&amp;A<span>Short answers to tape questions</span></a></div></section>"""
    if re.search(r"[$€]|zł", body_sections) and path in ("/why-tape/lto-tape-drive", "/about", "/resources/cheap-lto-tapes", "/comparisons", "/why-tape"):
        related += '<section class="section-card"><p class="eyebrow">Current prices</p><h2>Check current LTO prices</h2><p>Prices on this page are rounded guidance. For seller listings checked in September 2026, see the <a href="/lto-tape-price-trend">LTO price tracker</a> and the <a href="/lto-tape-price-trend/history">price history</a>.</p></section>'
    crumbs = [("Home", "/")]
    segs = path.strip("/").split("/")
    if len(segs) > 1:
        parent = "/" + segs[0]
        crumbs.append(("Why tape" if parent == "/why-tape" else LEGACY[parent][1].split(":")[0].split("|")[0].strip() if parent in LEGACY else segs[0].title(), parent))
    crumbs.append((html.unescape(re.sub(r"<[^>]+>", "", h1_text)), path))
    facts = price_facts()
    answer = f'<p><strong>{esc(ANSWERS[path].format(**facts))}</strong></p>' if path in ANSWERS else ""
    body = f"""<section class="hero"><div class="container"><div class="hero-copy" style="max-width:860px">
<h1 style="max-width:none">{h1_text}</h1>{answer}{f'<p>{lead}</p>' if lead else ''}</div></div></section>
<main class="page"><div class="container"><div class="section-stack">{body_sections}{related}</div></div></main>"""
    faqs = [(q, a.format(**facts)) for q, a in GUIDE_FAQS.get(path, [])]
    if faqs:
        body = body.replace("</div></div></main>", faq_html(faqs, "Frequently asked questions") + "</div></div></main>", 1)
    ld = [breadcrumb_ld(crumbs), {"@context": "https://schema.org", "@type": "Article", "headline": html.unescape(re.sub(r"<[^>]+>", "", h1_text)), "description": desc, "dateModified": "2026-09-20",
          "author": {"@type": "Organization", "name": "TapeBackup.org"}, "publisher": {"@type": "Organization", "name": "TapeBackup.org", "url": SITE}, "mainEntityOfPage": SITE + path}]
    if faqs:
        ld.append(faq_ld(faqs))
    write(path, page(path, title, desc, body, ld, og_type="article"))
    return path


# ---------------------------------------------------------------- tools

JS_LOCALE = {"en": "en-US", "de": "de-DE", "fr": "fr-FR", "it": "it-IT", "es": "es-ES", "nl": "nl-NL", "pl": "pl-PL"}


def i18n_json(el_id, strings):
    """Strings a page script needs, in a JSON block that scripts/i18n.py translates like page text."""
    blob = json.dumps(strings, ensure_ascii=False).replace("</", "<\\/")
    return f'<script type="application/json" id="{el_id}" data-i18n>{blob}</script>'


def build_calculator(current):
    path = "/backup-calculator"
    gens = current["generations"]
    mid = lambda item: round((item["low"] + item["high"]) / 2, 2) if (item or {}).get("low") is not None else None
    model = {g: {"tb": gens[g]["nativeTB"], "tape": mid(gens[g]["cartridge"]), "drive": mid(gens[g].get("driveInternal")) or mid(gens[g].get("driveExternal"))} for g in ["LTO-8", "LTO-9", "LTO-10"]}
    cfg = {"model": model, "locale": JS_LOCALE[BP.MKT.lang], "currency": BP.MKT.currency}
    facts = price_facts()
    L = {
        "est": "<p><strong>{gen} estimate:</strong> {n} cartridges ({tb} TB native each), about {media} in media.</p>",
        "est_drive": "<p><strong>{gen} estimate:</strong> {n} cartridges ({tb} TB native each), about {media} in media plus about {drive} for one drive.</p>",
        "h_invalid": "Enter your data size",
        "t_invalid": "<p>Type the total amount of data you need to protect, in terabytes.</p>",
        "h_conflict": "Check these requirements",
        "t_conflict": "<p>You chose real-time backups but accept recovery taking days. Teams that need continuous protection usually need fast recovery too. Choose a faster recovery time, or a daily or weekly recovery point.</p>",
        "h_small_instant": "Recommended: SSD or HDD plus cloud",
        "h_small": "Recommended: NAS (HDD) plus cloud archive",
        "t_small": "<p>With {tb} TB, the cost of a tape drive is hard to justify. Keep a local disk copy for fast restores and a cloud cold-tier copy offsite.</p>",
        "h_instant": "Recommended: disk or flash first, LTO tape second",
        "t_instant": "<p>Instant recovery means your first copy must be on disk or flash. For {total} TB across all copies, keep only recent restore points on disk and put long-term, offline copies on LTO tape.</p>",
        "h_tape": "Recommended: {gen} tape",
        "h_tape_big": "Recommended: LTO-9 or LTO-10 tape",
        "t_lto8": "<p>LTO-8 (12 TB native) keeps drive cost down for this data size and still gives you offline copies.</p>",
        "t_lto9": "<p>LTO-9 (18 TB native) has the lowest media cost per terabyte in 2026 and fewer cartridges to handle than LTO-8.</p>",
        "t_big": "<p>At this size density matters. LTO-9 has the lowest cost per TB; LTO-10 needs fewer cartridges and library slots but costs more per TB and needs new full-height drives.</p>",
        "t_airgap": "<p>With {total} TB across all copies, tape gives you an air gap against ransomware and avoids cloud restore fees.</p>",
        "t_continuous": "<p><em>Real-time recovery points need a disk buffer in front of tape (disk to disk to tape).</em></p>",
    }
    body = f"""<section class="hero"><div class="container hero-grid"><div class="hero-copy">
<p class="eyebrow">Tool</p><h1>LTO Tape Backup Calculator</h1>
<p><strong>Tape pays off from roughly 15 TB of data: below that, disk plus cloud is cheaper; above it, LTO-8 or LTO-9 media at about {facts['media_pertb_89']} per TB beats keeping long-term copies on disk.</strong></p>
<p>Enter how much data you protect, how many copies you keep and how fast you need it back. The calculator recommends tape, disk, cloud or a mix, and estimates cartridges and media cost from {BP.CURRENT_LABEL} LTO prices{'' if BP.MKT.is_us else ' in ' + BP.MKT.country}.</p></div>
<aside class="hero-panel"><p class="panel-label">Prices used</p><p class="panel-copy">Midpoints of seller listings from the <a href="/lto-tape-price-trend">LTO price tracker</a>: LTO-8 tapes {BP.money0(model['LTO-8']['tape'])}, LTO-9 tapes {BP.money0(model['LTO-9']['tape'])}, LTO-10 30 TB tapes {BP.money0(model['LTO-10']['tape'])}.</p></aside></div></section>
<main class="page"><div class="container"><div class="section-stack">
<section class="section-card"><h2>Calculate your backup setup</h2>
<form class="tool-form" id="calc" novalidate>
<div><label for="capacity">Total data to protect (TB)</label><input id="capacity" type="number" min="1" step="1" value="50" inputmode="decimal" required></div>
<div><label for="copies">Number of copies</label><select id="copies"><option value="1">1 copy (risky)</option><option value="2" selected>2 copies</option><option value="3">3 copies (3-2-1 standard)</option></select></div>
<div><label for="rto">Recovery time objective</label><p class="hint">How fast do you need data back?</p><select id="rto"><option value="instant">Minutes (mission critical)</option><option value="hours" selected>Within hours (standard)</option><option value="days">Within days (archive)</option></select></div>
<div><label for="rpo">Recovery point objective</label><p class="hint">How much recent data can you afford to lose?</p><select id="rpo"><option value="continuous">Seconds (real time)</option><option value="daily" selected>24 hours (daily backups)</option><option value="weekly">A week (weekly backups)</option></select></div>
<button class="tool-submit" type="submit">Show my recommendation</button>
</form>
<div class="tool-result" id="calc-result" hidden aria-live="polite"></div>
{figure("lto-cartridges-per-100tb.svg", "Cartridges needed for 100 TB: 9 LTO-8, 6 LTO-9 or 4 LTO-10", "One copy of 100 TB needs 9 LTO-8, 6 LTO-9 or 4 LTO-10 cartridges at native capacity, before compression.", 960, 440)}
</section>
<section class="section-card"><p class="eyebrow">How it works</p><h2>How the calculator decides</h2>
<ul><li>Under 15 TB, a tape drive rarely pays for itself, so disk plus cloud is recommended.</li><li>If you need recovery in minutes, the first copy has to live on disk or flash, with tape for long-term and offline copies.</li><li>Otherwise LTO-8 is suggested under 50 TB, LTO-9 up to 500 TB, and LTO-9 or LTO-10 above that.</li><li>Cartridge counts use native capacity with no compression, and costs use the midpoint of current seller listings. Drive cost is one new internal drive where one is listed.</li></ul>
<p>Estimates exclude software, HBAs, libraries, {'tax' if BP.MKT.is_us else 'delivery'} and shipping. See the <a href="/lto-tape-price-trend">LTO price tracker</a> for the listings behind these numbers.</p></section>
{faq_html([(q, a.format(**facts)) for q, a in GUIDE_FAQS["/backup-calculator"]], "Backup calculator FAQ")}
</div></div></main>
<script type="application/json" id="calc-cfg">{json.dumps(cfg)}</script>
{i18n_json("calc-i18n", L)}
<script>
(function(){{
var C=JSON.parse(document.getElementById('calc-cfg').textContent),L=JSON.parse(document.getElementById('calc-i18n').textContent),M=C.model;
var f=document.getElementById('calc'),out=document.getElementById('calc-result');
var nf=new Intl.NumberFormat(C.locale),cf=new Intl.NumberFormat(C.locale,{{style:'currency',currency:C.currency,maximumFractionDigits:0}});
function fill(s,v){{return s.replace(/\{{(\w+)\}}/g,function(m,k){{return k in v?v[k]:m;}});}}
function est(gen,total){{var g=M[gen];var n=Math.ceil(total/g.tb);var v={{gen:gen,n:nf.format(n),tb:nf.format(g.tb),media:cf.format(n*g.tape)}};if(g.drive){{v.drive=cf.format(g.drive);return fill(L.est_drive,v);}}return fill(L.est,v);}}
f.addEventListener('submit',function(e){{
e.preventDefault();
var tb=parseFloat(document.getElementById('capacity').value),copies=parseInt(document.getElementById('copies').value,10),rto=document.getElementById('rto').value,rpo=document.getElementById('rpo').value;
var h,t,tape=false;
if(!tb||tb<=0){{h=L.h_invalid;t=L.t_invalid;}}
else if(rpo==='continuous'&&rto==='days'){{h=L.h_conflict;t=L.t_conflict;}}
else{{
var total=tb*copies,v={{tb:nf.format(tb),total:nf.format(total)}};
if(tb<15){{h=rto==='instant'?L.h_small_instant:L.h_small;t=fill(L.t_small,v)+est('LTO-8',total);}}
else if(rto==='instant'){{h=L.h_instant;t=fill(L.t_instant,v)+est(tb<500?'LTO-9':'LTO-10',total);tape=true;}}
else{{var gen=tb<50?'LTO-8':(tb<500?'LTO-9':'LTO-10');h=tb<500?fill(L.h_tape,{{gen:gen}}):L.h_tape_big;tape=true;
t=tb<50?L.t_lto8:(tb<500?L.t_lto9:L.t_big);
t+=est(tb<500?gen:'LTO-9',total);if(tb>=500){{t+=est('LTO-10',total);}}
t+=fill(L.t_airgap,v);}}
if(rpo==='continuous'&&tape){{t+=L.t_continuous;}}
}}
out.innerHTML='<h3>'+h+'</h3>'+t;out.hidden=false;
}});
}})();
</script>"""
    desc = "Free tape backup calculator: enter data size, copies and recovery targets to get a tape, disk or cloud recommendation with 2026 LTO cartridge costs."
    ld = [faq_ld([(q, a.format(**facts)) for q, a in GUIDE_FAQS["/backup-calculator"]]), breadcrumb_ld([("Home", "/"), ("Backup calculator", path)]),
          {"@context": "https://schema.org", "@type": "WebApplication", "name": "LTO Tape Backup Calculator", "applicationCategory": "UtilitiesApplication", "operatingSystem": "Any", "url": SITE + path, "offers": {"@type": "Offer", "price": "0", "priceCurrency": BP.MKT.currency}}]
    write(path, page(path, "LTO Calculator: Tapes Needed and Tape Backup Cost", desc, body, ld))
    return path


def build_finder():
    path = "/backup-software-finder"
    q = [
        ("env", "1. What is your primary environment?", [("virtual", "Mostly virtual machines"), ("physical", "Heavy physical or Unix"), ("mixed", "Mixed or hybrid"), ("saas", "Microsoft 365 or SaaS only")], "mixed"),
        ("tape", "2. How will you use tape?", [("heavy", "Primary archive or large library"), ("secondary", "Secondary copy"), ("none", "No tape, disk or cloud only")], "secondary"),
        ("scale", "3. How many workloads?", [("small", "1 to 50"), ("mid", "51 to 500 or more")], "mid"),
        ("prio", "4. What matters most?", [("value", "Cost effectiveness"), ("feature", "Modern and cloud features")], "value"),
    ]
    fields = "".join(
        f'<fieldset class="choice-grid"><legend>{esc(label)}</legend>' + "".join(
            f'<label><input type="radio" name="{name}" value="{v}"{" checked" if v == default else ""}>{esc(t)}</label>' for v, t in opts) + "</fieldset>"
        for name, label, opts, default in q
    )
    L = {
        "match": "Your match: {v}",
        "compare": '<a href="/best-tape-backup-software">Compare all tape backup software</a>',
        "r_dpx": 'Catalogic DPX is built around tape. It supports a very wide range of LTO drives and libraries, including older ones, handles NDMP well and costs less than most enterprise suites when tape is central. <a href="/resources/tape-backup-software/catalogicdpx">Read the DPX review</a>.',
        "r_saas": "For SaaS data, Veeam for Microsoft 365 is the market leader. If you also run Kubernetes, look at CloudCasa.",
        "r_virtual": "For a virtual, disk-based estate Veeam is the standard choice and works well with disk and cloud targets.",
        "v_mixed_notape": "Acronis or Commvault",
        "r_mixed_notape": "For mixed environments without tape, Acronis has strong security features and Commvault has deep cloud integration.",
        "r_small": "For smaller environments that need basic tape support without an enterprise price, Nakivo is a solid option.",
        "v_default": "Veeam or Catalogic DPX",
        "r_default": "Veeam is the popular choice for virtualization. Compare it with Catalogic DPX if your data is growing, because DPX licensing and tape handling often give a lower total cost.",
    }
    body = f"""<section class="hero"><div class="container hero-grid"><div class="hero-copy">
<p class="eyebrow">Tool</p><h1>Find the Right Tape Backup Software</h1>
<p><strong>If tape is your main archive, Catalogic DPX is usually the best fit; for mostly virtual estates using tape as a second copy, Veeam; for small environments on a budget, Nakivo.</strong></p>
<p>Hardware is half the job. Answer four questions to get a shortlist of backup software that fits how you use tape, the size of your estate and your budget.</p></div>
<aside class="hero-panel"><p class="panel-label">Want the detail?</p><p class="panel-copy">Read the full <a href="/best-tape-backup-software">best tape backup software comparison</a> or the <a href="/resources/tape-backup-software/catalogicdpx">Catalogic DPX review</a>.</p></aside></div></section>
<main class="page"><div class="container"><div class="section-stack">
<section class="section-card"><h2>Find your backup software</h2>
<form class="tool-form" id="finder">{fields}<button class="tool-submit" type="submit">Show my match</button></form>
<div class="tool-result" id="finder-result" hidden aria-live="polite"></div>
{figure("tape-backup-software-finder.svg", "Four questions point to Catalogic DPX, Veeam, Commvault or Nakivo", "Tape as the main archive points to Catalogic DPX, a mostly virtual estate with tape as a second copy to Veeam, a large mixed estate to Commvault, and a small budget to Nakivo.", 960, 440)}</section>
<section class="section-card"><p class="eyebrow">Shortlist</p><h2>Software this finder recommends from</h2>
<ul><li><strong>Catalogic DPX</strong>: tape-focused enterprise backup with broad drive, library and NDMP support.</li><li><strong>Veeam Backup &amp; Replication</strong>: the common choice for virtualized estates, with tape jobs as a secondary target.</li><li><strong>Commvault</strong>: large, feature-rich platform with deep cloud integration.</li><li><strong>Nakivo</strong>: lower-cost option for smaller environments that need basic tape support.</li><li><strong>Veeam for Microsoft 365 and CloudCasa</strong>: SaaS and Kubernetes backup.</li></ul></section>
{faq_html([tuple(x) for x in GUIDE_FAQS["/backup-software-finder"]], "Software finder FAQ")}
</div></div></main>
{i18n_json("finder-i18n", L)}
<script>
(function(){{
var L=JSON.parse(document.getElementById('finder-i18n').textContent);
var f=document.getElementById('finder'),out=document.getElementById('finder-result');
function val(n){{return f.querySelector('input[name="'+n+'"]:checked').value;}}
f.addEventListener('submit',function(e){{
e.preventDefault();
var env=val('env'),tape=val('tape'),scale=val('scale'),prio=val('prio'),v,r;
if(tape==='heavy'||(tape==='secondary'&&prio==='value')){{v='Catalogic DPX';r=L.r_dpx;}}
else if(env==='saas'){{v='Veeam for Microsoft 365';r=L.r_saas;}}
else if(tape==='none'){{if(env==='virtual'){{v='Veeam Backup & Replication';r=L.r_virtual;}}else{{v=L.v_mixed_notape;r=L.r_mixed_notape;}}}}
else if(scale==='small'){{v='Nakivo';r=L.r_small;}}
else{{v=L.v_default;r=L.r_default;}}
out.innerHTML='<h3>'+L.match.replace('{{v}}',v)+'</h3><p>'+r+'</p><p>'+L.compare+'</p>';out.hidden=false;
}});
}})();
</script>"""
    desc = "Answer four questions to find tape backup software that fits your environment, tape usage and budget: Catalogic DPX, Veeam, Commvault or Nakivo."
    ld = [faq_ld([tuple(x) for x in GUIDE_FAQS["/backup-software-finder"]]), breadcrumb_ld([("Home", "/"), ("Software finder", path)])]
    write(path, page(path, "Tape Backup Software Finder: Which LTO Software Fits", desc, body, ld))
    return path


def build_contact():
    path = "/contact"
    body = f"""<section class="hero"><div class="container hero-grid"><div class="hero-copy">
<p class="eyebrow">Contact</p><h1>Contact TapeBackup.org</h1>
<p>Ask for the LTO pricebook, send a question about tape backup, or suggest a correction to our price data. Use the form below and we will reply by email.</p></div>
<aside class="hero-panel"><p class="panel-label">We welcome</p><ul class="source-list"><li>LTO pricing and pricebook requests</li><li>Technical questions about LTO drives and media</li><li>Corrections to prices or guides</li><li>Partnerships, guest articles and case studies</li></ul></aside></div></section>
<main class="page"><div class="container"><div class="section-stack">
{hubspot_cta("Send us a message", "Tell us what you need, including the LTO generation and quantity if you are asking about prices.")}
<section class="section-card"><p class="eyebrow">Before you write</p><h2>Answers that may already exist</h2><div class="link-grid">
<a href="/lto-tape-price-trend">Current LTO prices<span>September 2026 tapes and drives</span></a>
<a href="/tape-q-and-a">Tape Q&amp;A<span>Short answers to common questions</span></a>
<a href="/backup-calculator">Backup calculator<span>Estimate cartridges and cost</span></a></div></section>
</div></div></main>"""
    desc = "Contact TapeBackup.org to request the LTO tape pricebook, ask a tape backup question, or send a correction to our LTO price data."
    write(path, page(path, "Contact TapeBackup.org: LTO Pricebook and Questions", desc, body, [breadcrumb_ld([("Home", "/"), ("Contact", path)])], hubspot=True))
    return path


def build_404():
    body = """<section class="hero"><div class="container"><div class="hero-copy" style="max-width:760px"><p class="eyebrow">404</p><h1 style="max-width:none">Page not found</h1><p>The page you asked for does not exist or has moved.</p></div></div></section>
<main class="page"><div class="container"><div class="section-stack"><section class="section-card"><h2>Try one of these</h2><div class="link-grid">
<a href="/">Home<span>TapeBackup.org</span></a><a href="/lto-tape-price-trend">LTO prices<span>September 2026</span></a><a href="/tape-q-and-a">Tape Q&amp;A<span>Answers</span></a><a href="/blog">Blog<span>Real-world LTO</span></a></div></section></div></div></main>"""
    html_ = page("/404", "Page Not Found | TapeBackup.org", "The page you are looking for does not exist on TapeBackup.org. Try the LTO price tracker, Tape Q&A or the blog.", body, robots="noindex, follow")
    write("/404.html", html_)
    return None


# ---------------------------------------------------------------- homepage

def build_home(current):
    gens = current["generations"]
    l9 = gens["LTO-9"]["cartridge"]
    sym = BP.MKT.sym
    per_tb_9 = f"{sym}{l9['perTBLow']:.0f}-{sym}{l9['perTBHigh']:.0f}"
    with open(os.path.join(ROOT, "data", "home-template.html"), encoding="utf-8") as f:
        tpl = f.read()
    blog = json.load(open(os.path.join(ROOT, "data", "home-blog.json"), encoding="utf-8"))
    cards = "".join(
        f'<article class="news-card"><a href="{esc(b["href"])}" style="display:contents"><div class="news-thumb"><span class="gloss"></span><span class="tcart"></span><span class="cat">{esc(b["cat"])}</span></div><div class="news-body"><span class="date">{esc(b["date"])}</span><h3>{esc(b["h"])}</h3><div class="more"><span class="textlink">Read more<span class="arr">{ARROW}</span></span></div></div></a></article>'
        for b in blog
    )
    where = "" if BP.MKT.is_us else f" in {BP.MKT.country}"
    out = (tpl.replace("{{PER_TB_9}}", per_tb_9).replace("{{LTO9_RANGE}}", f"{sym}{l9['low']:.0f} to {sym}{l9['high']:.0f}")
           .replace("for an 18 TB LTO-9 cartridge in September 2026)", f"for an 18 TB LTO-9 cartridge{where} in September 2026)").replace("{{BLOG_CARDS}}", cards))
    write("/", out)
    return "/"


ARROW = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>'


def build_all(current):
    paths = []
    for path, (key, title, desc) in LEGACY.items():
        paths.append(build_legacy(path, key, title, desc))
    paths += [build_calculator(current), build_finder(), build_contact(), build_home(current)]
    if BP.MKT.is_us:
        build_404()
    return paths
