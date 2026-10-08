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

import build_articles  # noqa: E402
import build_guides  # noqa: E402
import build_pages  # noqa: E402
import build_prices  # noqa: E402
import i18n  # noqa: E402
import markets  # noqa: E402
import shutil  # noqa: E402
import site_shell  # noqa: E402
import videos  # noqa: E402
import chatbot  # noqa: E402
from site_shell import GENS, ROOT, SITE, esc, slug_for  # noqa: E402


def rel(*p):
    return os.path.join(ROOT, *p)


BLOG_TEXT_FIXES = {
    "blog/index.html": [
        ("<h1>Recent articles about real-world LTO backup workflows</h1>", "<h1>LTO Tape Backup Blog: Real-World Tape Workflows</h1>"),
        ("<p>Clearer titles, direct links, and standalone article pages for the latest TapeBackup.org posts on LTO media, restore workflows, offsite rotation, and the messy practical side of tape.</p>",
         "<p>Field notes on running LTO tape: used drives and libraries, backup software, offsite rotation, home archives, and the restores that go wrong.</p>"),
        ('<span class="signal-chip">Static archive</span>', '<span class="signal-chip">Offsite rotation</span>'),
        ('<span class="signal-chip">Direct article routing</span>', '<span class="signal-chip">Used drives and libraries</span>'),
        ('<p class="panel-label">Reader note</p>', '<p class="panel-label">Looking for prices?</p>'),
        ('<p class="panel-copy">This blog index is now published as a static page so the listing always shows the intended human-readable titles instead of falling back to slug strings.</p>',
         '<p class="panel-copy">Current LTO-6 to LTO-10 tape and drive prices are in the <a href="/lto-tape-price-trend">LTO price tracker</a>; buying advice is in the <a href="/lto-tape">LTO tape guide</a>.</p>'),
    ],
}
# One drawing per post, inserted after the first paragraph of the article body (see scripts/draw_figures.py).
BLOG_FIGURES = {
    "offsite-tape-backups-still-beat-most-good-enough-plans": ("offsite-tape-rotation.svg", 960, 440,
        "Tapes leave the building, travel to a vault and rotate back, outside the blast radius",
        "Offsite rotation: cartridges leave the site, sit in a vault outside the blast radius of a fire, flood or attack, and rotate back on a schedule."),
    "backup-strategy-gets-serious-when-your-archive-outgrows-disks": ("loose-disks-vs-tape.svg", 960, 420,
        "A pile of loose disks next to a neat case of LTO cartridges",
        "Loose disks pile up with no catalogue and no rotation; the same archive on LTO fits in one case of labelled cartridges."),
}
BLOG_INDEX_FIGURE = ("lto-cartridge-shelf.svg", 960, 300, "LTO cartridges on a shelf")


def blog_fixes():
    n = 0
    for rel_path, pairs in BLOG_TEXT_FIXES.items():
        f = rel(*rel_path.split("/"))
        s = open(f, encoding="utf-8").read()
        new = s
        for a, b in pairs:
            new = new.replace(a, b)
        name, w, h, alt = BLOG_INDEX_FIGURE
        if name not in new:
            new = new.replace('<section class="listing-grid"', f'<figure class="page-figure"><img src="/assets/figures/{name}" alt="{alt}" width="{w}" height="{h}" loading="lazy" decoding="async"></figure>\n<section class="listing-grid"', 1)
        if new != s:
            open(f, "w", encoding="utf-8").write(new)
            n += 1
    for slug, (name, w, h, alt, cap) in BLOG_FIGURES.items():
        f = rel("blog", slug, "index.html")
        s = open(f, encoding="utf-8").read()
        if name in s:
            continue
        fig = f'<figure class="page-figure"><img src="/assets/figures/{name}" alt="{esc(alt)}" width="{w}" height="{h}" loading="lazy" decoding="async"><figcaption>{esc(cap)}</figcaption></figure>'
        s = re.sub(r'(<section class="article-body"><p>.*?</p>)', lambda m: m.group(1) + fig, s, count=1, flags=re.S)
        open(f, "w", encoding="utf-8").write(s)
        n += 1
    return n


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


def apply_qa_noindex():
    """Noindex off-topic Q&A pages listed in data/qa-noindex.json (reversible: remove a slug and rebuild)."""
    slugs = set(json.load(open(rel("data", "qa-noindex.json"), encoding="utf-8"))["slugs"])
    for f in glob.glob(rel("tape-q-and-a", "*", "index.html")):
        slug = f.split(os.sep)[-2]
        s = open(f, encoding="utf-8").read()
        want = "noindex, follow" if slug in slugs else "index, follow"
        new = re.sub(r'<meta name="robots" content="[^"]*"', f'<meta name="robots" content="{want}"', s, count=1)
        if new != s:
            open(f, "w", encoding="utf-8").write(new)
    return slugs


PANEL_RE = re.compile(r'<p class="panel-label">(?:Reader note|Why this page exists|Short answer|In short)</p>\s*<p class="panel-copy">.*?</p>', re.S)

GUIDE_LINKS = [
    (("price", "cheap", "cost", "buy", "dollar", "500", "000"), "/lto-tape-price-trend", "LTO tape prices, September 2026"),
    (("software", "script", "linux", "built"), "/best-tape-backup-software", "Best tape backup software in 2026"),
    (("drive", "sas", "rogue", "lto-6", "lto-8", "paperweight"), "/why-tape/lto-tape-drive", "How LTO tape drives work"),
    (("offsite", "archive", "strategy", "disks", "hard"), "/why-tape/lto-vs-hdd", "LTO tape vs HDD for long-term storage"),
    (("home", "libraries", "used"), "/resources/cheap-lto-tapes", "How to buy used LTO tapes safely"),
]


def first_sentences(text, limit=320):
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    out = ""
    for part in parts:
        if len(out) + len(part) > limit and out:
            break
        out = (out + " " + part).strip()
    return out


def answer_first_panels():
    """AEO: swap the boilerplate hero side panel for a quotable short answer (Q&A) or summary (blog)."""
    changed = 0
    for f in glob.glob(rel("tape-q-and-a", "*", "index.html")) + glob.glob(rel("blog", "*", "index.html")):
        s = open(f, encoding="utf-8").read()
        if "/tape-q-and-a/" in f:
            block = re.search(r'<div class="answer-copy">(.*?)</div>', s, re.S)
            paras = [html.unescape(re.sub(r"<[^>]+>", "", p)).strip() for p in re.findall(r"<p>(.*?)</p>", block.group(1), re.S)] if block else []
            if not paras:
                continue
            label, text = "Short answer", first_sentences(" ".join(paras))
        else:
            m = re.search(r'<meta name="description" content="([^"]*)"', s)
            label, text = "In short", html.unescape(m.group(1)) if m else ""
        new = PANEL_RE.sub(lambda _: f'<p class="panel-label">{label}</p>\n            <p class="panel-copy">{esc(text)}</p>', s, count=1)
        if new != s:
            open(f, "w", encoding="utf-8").write(new)
            changed += 1
    return changed


def blog_related_links():
    """Internal linking: every post links to 3 related posts and 2 matching guides (posts had only the blog index linking in)."""
    posts = {}
    for f in glob.glob(rel("blog", "*", "index.html")):
        slug = f.split(os.sep)[-2]
        s = open(f, encoding="utf-8").read()
        h = re.search(r'"headline":"(.*?)","description"', s, re.S)
        title = json.loads('"' + h.group(1) + '"') if h else slug
        d = re.search(r'<meta name="description" content="([^"]*)"', s)
        text = (title + " " + (html.unescape(d.group(1)) if d else "")).lower()
        stop = {"about", "their", "there", "these", "those", "which", "while", "where", "until", "being", "every", "still", "really", "without", "because", "people"}
        posts[slug] = (f, title, set(w for w in re.findall(r"[a-z0-9-]+", text) if len(w) > 4 and w not in stop))
    for slug, (f, title, words) in posts.items():
        others = sorted((len(words & w2), s2) for s2, (_, _, w2) in posts.items() if s2 != slug)
        picks = [s2 for _, s2 in reversed(others)][:3]
        guides = [(u, t) for keys, u, t in GUIDE_LINKS if any(k in slug for k in keys)][:2] or [("/lto-tape-price-trend", "LTO tape prices, September 2026"), ("/why-tape", "Why use tape storage")]
        items = "".join(f'<li><a href="/blog/{p}">{esc(posts[p][1])}</a></li>' for p in picks) + "".join(f'<li><a href="{u}">{esc(t)}</a></li>' for u, t in guides)
        html_block = f'<!-- related:start --><section class="related-reading" style="max-width:760px;margin:2.5rem auto 0;padding:0 1rem"><h2>Related on TapeBackup</h2><ul>{items}</ul></section><!-- related:end -->'
        s = open(f, encoding="utf-8").read()
        s = re.sub(r"\s*<!-- related:start -->.*?<!-- related:end -->", "", s, flags=re.S)
        s = re.sub(r"\n(?:[ \t]*\n)+([ \t]*</main>)", r"\n\1", s)
        if "</main>" in s:
            s = s.replace("</main>", html_block + "\n      </main>", 1)
        else:
            s = s.replace("<footer", html_block + "\n<footer", 1)
        open(f, "w", encoding="utf-8").write(s)
    return len(posts)


def qa_page_schema():
    """Each Q&A page is one question with one answer: mark it up as QAPage so answer engines can use it."""
    n = 0
    for f in glob.glob(rel("tape-q-and-a", "*", "index.html")):
        s = open(f, encoding="utf-8").read()
        q = re.search(r"<h1>(.*?)</h1>", s, re.S)
        block = re.search(r'<div class="answer-copy">(.*?)</div>', s, re.S)
        if not q or not block:
            continue
        question = html.unescape(re.sub(r"<[^>]+>", "", q.group(1))).strip()
        answer = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", block.group(1)))).strip()
        slug = f.split(os.sep)[-2]
        ld = {"@context": "https://schema.org", "@type": "QAPage", "mainEntity": {"@type": "Question", "name": question,
              "text": question, "answerCount": 1, "acceptedAnswer": {"@type": "Answer", "text": answer,
              "url": f"{SITE}/tape-q-and-a/{slug}"}}}
        tag = '<script type="application/ld+json" data-qa-schema>' + json.dumps(ld, ensure_ascii=False).replace("</", "<\\/") + "</script>"
        s2 = re.sub(r'[ \t]*<script type="application/ld\+json" data-qa-schema>.*?</script>\n?', "", s, flags=re.S)
        s2 = s2.replace("</head>", tag + "\n  </head>", 1)
        if s2 != s:
            open(f, "w", encoding="utf-8").write(s2)
            n += 1
    return n


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
    for path in ["/resources/lto-tape-migration", "/resources/tape-storage-market", "/comparisons/tape-vs-cloud-5-year-cost", "/backup-calculator", "/backup-software-finder", "/best-tape-backup-software", "/why-tape", "/why-tape/lto-tape-drive", "/why-tape/lto-vs-hdd", "/lto-tape", "/lto-tape-capacity", "/lto-tape-library", "/lto-tape-news", "/resources/ltfs", "/resources/lto-tape-data-recovery", "/why-tape/lto-tape-lifespan", "/resources/lto-cleaning-tapes-and-labels",
                
                 "/comparisons", "/lto-tape-brand", "/resources", "/resources/cheap-lto-tapes", "/resources/tape-backup-software/catalogicdpx", "/about", "/contact"]:
        add(path, idx(path), "0.7", "monthly")
    add("/blog", rel("blog", "index.html"), "0.8", "weekly")
    for f in sorted(glob.glob(rel("blog", "*", "index.html"))):
        add("/blog/" + f.split(os.sep)[-2], f, "0.7", "monthly")
    add("/tape-q-and-a", rel("tape-q-and-a", "index.html"), "0.8", "monthly")
    noindex = set(json.load(open(rel("data", "qa-noindex.json"), encoding="utf-8"))["slugs"])
    for f in sorted(glob.glob(rel("tape-q-and-a", "*", "index.html"))):
        if f.split(os.sep)[-2] in noindex:
            continue
        add("/tape-q-and-a/" + f.split(os.sep)[-2], f, "0.5", "yearly")

    for path, _, _, _ in entries:
        file = idx(path)
        assert os.path.exists(file), f"sitemap entry without a file: {path}"
    langs = published_langs()

    def alternates(p):
        if p not in i18n.SCOPE_SET or not langs:
            return ""
        links = [f'    <xhtml:link rel="alternate" hreflang="{c}" href="{i18n.lang_url(p, c)}"/>' for c in ["en"] + langs]
        links.append(f'    <xhtml:link rel="alternate" hreflang="x-default" href="{i18n.lang_url(p, "en")}"/>')
        return "\n".join(links) + "\n"

    urls = []
    for p, d, pr, fq in entries:
        urls.append(f"  <url>\n    <loc>{i18n.lang_url(p, 'en')}</loc>\n    <lastmod>{d}</lastmod>\n    <changefreq>{fq}</changefreq>\n    <priority>{pr}</priority>\n{alternates(p)}  </url>\n")
        if p in i18n.SCOPE_SET:
            for lang in langs:
                urls.append(f"  <url>\n    <loc>{i18n.lang_url(p, lang)}</loc>\n    <lastmod>{d}</lastmod>\n    <changefreq>{fq}</changefreq>\n    <priority>{pr}</priority>\n{alternates(p)}  </url>\n")
    with open(rel("sitemap.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + "".join(urls) + "</urlset>\n")
    return len(urls)


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
        if (x.get("driveInternal") or {}).get("low") is not None:
            drive.append(f"internal drive {P.rng(x['driveInternal'], False)}")
        if (x.get("driveExternal") or {}).get("low") is not None:
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
        f"- [Why tape]({SITE}/why-tape), [LTO tape explained]({SITE}/lto-tape), [LTO capacity chart]({SITE}/lto-tape-capacity), [LTO tape drive buying guide]({SITE}/why-tape/lto-tape-drive), [LTO tape libraries]({SITE}/lto-tape-library), [LTFS]({SITE}/resources/ltfs), [LTO tape data recovery]({SITE}/resources/lto-tape-data-recovery), [LTO tape lifespan]({SITE}/why-tape/lto-tape-lifespan), [LTO tape news]({SITE}/lto-tape-news), [LTO vs HDD]({SITE}/why-tape/lto-vs-hdd), [LTO tape brands]({SITE}/lto-tape-brand).",
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
            for d in sorted(item["datapoints"], key=lambda d: d["price"]):
                full.append(f"| {d.get('sku', '')} | {d['seller']} | ${d['price']:,.2f} | {P.clean_note(d.get('note'))} |")
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


def published_langs():
    cfg = i18n.load_langs()
    return [l for l in i18n.LANGS if cfg.get(l, {}).get("indexable")]


def build_languages():
    """Build each European market into .build/<lang>, then translate into /<lang>/."""
    report = []
    langs = published_langs()
    built = []
    for lang in i18n.LANGS:
        code = markets.LANG_TO_MARKET[lang]
        if not os.environ.get("TB_FAKE_EU") and not os.path.exists(os.path.join(markets.DATA, markets.MARKETS[code]["file"])):
            report.append(f"{lang}: skipped, no price data yet")
            continue
        stage = os.path.join(i18n.STAGE, lang)
        shutil.rmtree(stage, ignore_errors=True)
        site_shell.set_out_root(stage)
        try:
            _, cur = build_prices.build_all(code)
            build_pages.build_all(cur)
            build_articles.build_all(cur)
            build_guides.build_all(cur)
        finally:
            site_shell.set_out_root(ROOT)
        shutil.rmtree(os.path.join(ROOT, lang), ignore_errors=True)
        written, total, missing = i18n.render_language(lang, langs)
        built.append(lang)
        report.append(f"{lang}: {len(written)} pages, {total - missing}/{total} segments translated" + ("" if lang in langs else " (noindex)"))
    build_prices.set_market("us")
    i18n.add_alternates_to_english(langs)
    return report


def main():
    price_paths, current = build_prices.build_all()
    page_paths = build_pages.build_all(current) + build_articles.build_all(current) + build_guides.build_all(current)
    n = apply_meta_overrides()
    print(f"blog fixes: {blog_fixes()}")
    apply_qa_noindex()
    print(f"QAPage schema: {qa_page_schema()}")
    print(f"answer-first panels: {answer_first_panels()}, blog posts with related links: {blog_related_links()}")
    for f in glob.glob(rel("blog", "*", "index.html")) + glob.glob(rel("tape-q-and-a", "*", "index.html")):
        t = re.search(r"<title>(.*?)</title>", open(f, encoding="utf-8").read(), re.S)
        if t and len(html.unescape(t.group(1))) > 60:
            print(f"warning: title over 60 chars, add it to data/meta-overrides.json: {os.path.relpath(f, ROOT)}")
    for line in build_languages():
        print(line)
    print(f"video embeds: {videos.embed_all(i18n.LANGS)}")
    count = build_sitemap(build_prices.CURRENT_ISO)
    build_llms(current)
    kb, widgets = chatbot.build()
    print(f"assistant: {kb} chars of reference, widget added to {widgets} pages")
    print(f"price pages: {len(price_paths)}, other pages: {len(page_paths)}, meta overrides changed: {n}, sitemap urls: {count}")


if __name__ == "__main__":
    main()
