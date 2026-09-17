"""Build every generated page, then refresh metadata, sitemap and llms files.

    python3 scripts/build_site.py

Blog posts and Q&A pages are hand-published HTML; this script only rewrites
their <title>, description and social tags from data/meta-overrides.json.
Everything under lto-tape-price-trend/, the guides, tools and homepage are
fully generated. Needs beautifulsoup4 (pip install beautifulsoup4).
"""

import glob
import html
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import build_pages  # noqa: E402
import build_prices  # noqa: E402
from site_shell import GENS, ROOT, SITE, esc, slug_for  # noqa: E402


def rel(*p):
    return os.path.join(ROOT, *p)


def apply_meta_overrides():
    with open(rel("data", "meta-overrides.json"), encoding="utf-8") as f:
        overrides = json.load(f)
    changed = 0
    for path, meta in overrides.items():
        file = rel(path.lstrip("/"), "index.html")
        if not os.path.exists(file):
            raise SystemExit(f"meta override for missing page: {path}")
        s = open(file, encoding="utf-8").read()
        t, d = esc(meta["title"]), esc(meta["description"])
        new = re.sub(r"<title>.*?</title>", f"<title>{t}</title>", s, count=1, flags=re.S)
        new = re.sub(r'<meta name="description" content="[^"]*"', f'<meta name="description" content="{d}"', new, count=1)
        for prop, val in (("og:title", t), ("og:description", d)):
            new = re.sub(rf'<meta property="{prop}" content="[^"]*"', f'<meta property="{prop}" content="{val}"', new, count=1)
        for name, val in (("twitter:title", t), ("twitter:description", d)):
            new = re.sub(rf'<meta name="{name}" content="[^"]*"', f'<meta name="{name}" content="{val}"', new, count=1)
        if path == "/blog" and "application/ld+json" not in new:
            posts = []
            for p in sorted(glob.glob(rel("blog", "*", "index.html"))):
                ps = open(p, encoding="utf-8").read()
                h = re.search(r'"headline":"(.*?)","', ps)
                slug = p.split(os.sep)[-2]
                posts.append({"@type": "BlogPosting", "headline": json.loads('"' + h.group(1) + '"') if h else slug, "url": f"{SITE}/blog/{slug}"})
            ld = {"@context": "https://schema.org", "@type": "Blog", "name": "TapeBackup.org Blog", "url": f"{SITE}/blog", "blogPost": posts}
            new = new.replace("</head>", '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + "</script>\n  </head>", 1)
        if new != s:
            open(file, "w", encoding="utf-8").write(new)
            changed += 1
    return changed


def git_date(file):
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", file], cwd=ROOT, capture_output=True, text=True).stdout.strip()
        return out or None
    except Exception:
        return None


def page_date(file, default):
    s = open(file, encoding="utf-8").read()
    m = re.search(r'"dateModified":\s*"(\d{4}-\d{2}-\d{2})', s)
    return m.group(1) if m else (git_date(os.path.relpath(file, ROOT)) or default)


def build_sitemap(today):
    entries = []

    def add(path, file, prio, freq):
        entries.append((path, page_date(file, today), prio, freq))

    idx = lambda path: rel("index.html") if path == "/" else rel(path.lstrip("/"), "index.html")
    add("/", idx("/"), "1.0", "weekly")
    add("/lto-tape-price-trend", idx("/lto-tape-price-trend"), "0.9", "monthly")
    for gen in GENS:
        add(f"/lto-tape-price-trend/{slug_for(gen)}", idx(f"/lto-tape-price-trend/{slug_for(gen)}"), "0.9", "monthly")
    add("/lto-tape-price-trend/history", idx("/lto-tape-price-trend/history"), "0.7", "monthly")
    hist = json.load(open(rel("data", "price-history.json"), encoding="utf-8"))
    for snap in hist["snapshots"]:
        entries.append((f"/lto-tape-price-trend/{snap['slug']}", snap["published"], "0.5", "yearly"))
    for path in ["/backup-calculator", "/backup-software-finder", "/best-tape-backup-software", "/why-tape", "/why-tape/lto-tape-drive", "/why-tape/lto-vs-hdd",
                 "/comparisons", "/lto-tape-brand", "/resources", "/resources/cheap-lto-tapes", "/resources/tape-backup-software/catalogicdpx", "/about", "/contact"]:
        add(path, idx(path), "0.7", "monthly")
    add("/blog", rel("blog", "index.html"), "0.8", "weekly")
    for f in sorted(glob.glob(rel("blog", "*", "index.html"))):
        add("/blog/" + f.split(os.sep)[-2], f, "0.7", "monthly")
    add("/tape-q-and-a", rel("tape-q-and-a", "index.html"), "0.8", "monthly")
    for f in sorted(glob.glob(rel("tape-q-and-a", "*", "index.html"))):
        add("/tape-q-and-a/" + f.split(os.sep)[-2], f, "0.5", "yearly")

    for path, _, _, _ in entries:
        file = idx(path)
        assert os.path.exists(file), f"sitemap entry without a file: {path}"
    body = "".join(
        f"  <url>\n    <loc>{SITE}{'' if p == '/' else p}{'/' if p == '/' else ''}</loc>\n    <lastmod>{d}</lastmod>\n    <changefreq>{fq}</changefreq>\n    <priority>{pr}</priority>\n  </url>\n"
        for p, d, pr, fq in entries
    )
    with open(rel("sitemap.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + "</urlset>\n")
    return len(entries)


def build_llms(current):
    P = build_prices
    g = current["generations"]
    lines = [
        "# TapeBackup.org: LTO Tape Backup and Price Tracker",
        "",
        "> Independent reference for LTO (Linear Tape-Open) tape backup: current LTO-6 to LTO-10 cartridge and drive prices from seller listings, price history since September 2025, buying guides, backup software comparisons and short technical answers.",
        "",
        f"## Current LTO prices ({P.CURRENT_LABEL}, checked {P.CURRENT_DATE_TEXT})",
    ]
    for gen in GENS:
        x = g[gen]
        drive = []
        if x.get("driveInternal", {}).get("lowUSD") is not None:
            drive.append(f"internal drive {P.rng(x['driveInternal'], False)}")
        if x.get("driveExternal", {}).get("lowUSD") is not None:
            drive.append(f"external drive {P.rng(x['driveExternal'], False)}")
        lines.append(f"- [{gen} price guide]({SITE}/lto-tape-price-trend/{slug_for(gen)}): {x['nativeTB']:g} TB native; cartridge {P.rng(x['cartridge'], True)} ({P.per_tb(x['cartridge'])} per TB); WORM {P.rng(x.get('worm', {}), True)}; " + ("; ".join(drive) or "no new standalone drive listed") + ".")
    lines.append(f"- LTO-10 40 TB cartridge: {P.rng(g['LTO-10']['cartridge40TB'], True)} ({P.per_tb(g['LTO-10']['cartridge40TB'])} per TB). LTO-10 drives are full height only and do not read older generations.")
    lines += [
        "",
        "## Core pages",
        f"- [LTO price tracker]({SITE}/lto-tape-price-trend): all generations side by side with method and market notes.",
        f"- [LTO price history]({SITE}/lto-tape-price-trend/history): archived snapshots from September 2025 onward.",
        f"- [Backup calculator]({SITE}/backup-calculator): tape, disk or cloud recommendation with cartridge count and media cost.",
        f"- [Tape backup software finder]({SITE}/backup-software-finder) and [best tape backup software 2026]({SITE}/best-tape-backup-software).",
        f"- [Why tape]({SITE}/why-tape), [LTO tape drives explained]({SITE}/why-tape/lto-tape-drive), [LTO vs HDD]({SITE}/why-tape/lto-vs-hdd), [LTO tape brands]({SITE}/lto-tape-brand).",
        f"- [Tape Q&A]({SITE}/tape-q-and-a) and [blog]({SITE}/blog).",
        "",
        "## Full data",
        f"- [llms-full.txt]({SITE}/llms-full.txt): every current listing with seller and part number, plus the price history table.",
        "",
    ]
    open(rel("llms.txt"), "w", encoding="utf-8").write("\n".join(lines))

    full = ["# TapeBackup.org LTO price data", "", f"Checked {P.CURRENT_DATE_TEXT}. New items, USD, listed price before tax and shipping.", ""]
    for gen in GENS:
        x = g[gen]
        full.append(f"## {gen} ({x['nativeTB']:g} TB native)")
        for key, label in (("cartridge", "Cartridge"), ("cartridge40TB", "40 TB cartridge"), ("worm", "WORM cartridge"), ("driveInternal", "Internal drive"), ("driveExternal", "External drive")):
            item = x.get(key)
            if not item or not item.get("datapoints"):
                continue
            full.append(f"### {label}: {P.rng(item, key.startswith('cart') or key == 'worm')}")
            full.append("| Part | Seller | Price | Note |")
            full.append("| --- | --- | --- | --- |")
            for d in sorted(item["datapoints"], key=lambda d: d["priceUSD"]):
                full.append(f"| {d.get('sku', '')} | {d['seller']} | ${d['priceUSD']:,.2f} | {P.clean_note(d.get('note'))} |")
            full.append("")
    hist = json.load(open(rel("data", "price-history.json"), encoding="utf-8"))
    full.append("## Cartridge price history")
    head = ["Generation", P.CURRENT_LABEL] + [s["label"] for s in hist["snapshots"]]
    full.append("| " + " | ".join(head) + " |")
    full.append("|" + " --- |" * len(head))
    for gen in ["LTO-5"] + GENS:
        cur = g.get(gen)
        row = [gen, P.rng(cur["cartridge"], True) if cur else ""] + [s.get("cartridges", {}).get(gen, {}).get("range", "") for s in hist["snapshots"]]
        full.append("| " + " | ".join(row) + " |")
    full.append("")
    full.append("## Market notes")
    for n in current["marketNotes"]:
        full.append(f"- {n['text']} ({n['url']})")
    open(rel("llms-full.txt"), "w", encoding="utf-8").write("\n".join(full) + "\n")


def main():
    price_paths, current = build_prices.build_all()
    page_paths = build_pages.build_all(current)
    n = apply_meta_overrides()
    count = build_sitemap(build_prices.CURRENT_ISO)
    build_llms(current)
    print(f"price pages: {len(price_paths)}, other pages: {len(page_paths)}, meta overrides changed: {n}, sitemap urls: {count}")


if __name__ == "__main__":
    main()
