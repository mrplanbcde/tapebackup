"""Shared page shell for the static TapeBackup.org pages.

Every generated page gets the same head (GA, canonical, OG, fonts, CSS),
the same header and footer, and optional JSON-LD blocks. Keeping this in one
place is what stops titles, canonicals and nav links drifting apart again.
"""

import html
import json
import os

SITE = "https://tapebackup.org"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_ROOT = ROOT  # where write() puts pages; market builds point this at a staging folder


def set_out_root(path):
    global OUT_ROOT
    OUT_ROOT = path
HUBSPOT_PORTAL = "147689578"
HUBSPOT_FORM = "3f49124b-a1cb-4f2b-a54f-8f0c266fa59d"

GENS = ["LTO-6", "LTO-7", "LTO-8", "LTO-9", "LTO-10"]


def esc(s):
    return html.escape(str(s), quote=True)


def slug_for(gen):
    return "lto" + gen.split("-")[1] + "-price"


def canonical(path):
    return SITE + ("/" if path == "/" else path)


def write(path, content):
    """Write a page for a URL path using clean-URL file layout."""
    if path == "/":
        rel = "index.html"
    elif path.endswith(".html") or path.endswith(".xml") or path.endswith(".txt"):
        rel = path.lstrip("/")
    else:
        rel = path.lstrip("/") + "/index.html"
    full = os.path.join(OUT_ROOT, rel)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    return rel


BRAND_SVG = """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true"><rect x="3" y="6" width="18" height="12" rx="3" stroke="#fff" stroke-width="1.8"/><circle cx="8" cy="12" r="2.2" fill="#fff"/><circle cx="16" cy="12" r="2.2" fill="#fff"/><line x1="10.2" y1="12" x2="13.8" y2="12" stroke="#fff" stroke-width="1.4"/></svg>"""


def brand():
    return f"""<a class="brand" href="/" aria-label="TapeBackup.org home"><span class="mark">{BRAND_SVG}</span><span class="wm"><span class="t1">TapeBackup</span><span class="t2">LTO Tape Info</span></span></a>"""


def header():
    price_links = "".join(
        f'<a href="/lto-tape-price-trend/{slug_for(g)}">{g} Price<span>{cap}</span></a>'
        for g, cap in zip(GENS, ["2.5 TB native", "6 TB native", "12 TB native", "18 TB native", "30 / 40 TB native"])
    )
    return f"""<div class="topbar"><div class="wrap"><a href="/tape-q-and-a">Tape Q&amp;A</a><span class="sep"></span><a href="/lto-tape-price-trend">LTO Prices</a><span class="sep"></span><a href="/contact">Contact Us</a></div></div>
<header class="site-header"><div class="wrap">{brand()}
<nav class="topnav" aria-label="Primary">
<a href="/why-tape">Why Tape</a>
<div class="price-dropdown"><a href="/lto-tape-price-trend">LTO Prices</a><div class="price-dropdown-menu"><a href="/lto-tape-price-trend">All generations<span>September 2026 prices</span></a>{price_links}<a href="/lto-tape-price-trend/history">Price history<span>Archived snapshots since 2025</span></a></div></div>
<div class="price-dropdown"><a href="/backup-calculator">Tools</a><div class="price-dropdown-menu"><a href="/backup-calculator">Backup calculator<span>Media and cost estimate</span></a><a href="/backup-software-finder">Software finder<span>Match software to your tape use</span></a><a href="/best-tape-backup-software">Best tape backup software<span>2026 comparison</span></a></div></div>
<a href="/blog">Blog</a>
<a href="/tape-q-and-a">Q&amp;A</a>
</nav>
<div class="header-right"><a class="btn btn-primary btn-sm" href="/contact">Get Pricebook</a></div>
</div></header>"""


def footer():
    cols = [
        ("LTO Prices", [("Price tracker", "/lto-tape-price-trend")] + [(f"{g} Price", f"/lto-tape-price-trend/{slug_for(g)}") for g in GENS] + [("Price history", "/lto-tape-price-trend/history")]),
        ("Resources", [("Tape Q&A", "/tape-q-and-a"), ("Blog", "/blog"), ("Why Tape", "/why-tape"), ("Guides", "/resources"), ("LTO tape brands", "/lto-tape-brand"), ("Comparisons", "/comparisons")]),
        ("Tools", [("Backup calculator", "/backup-calculator"), ("Software finder", "/backup-software-finder"), ("Best tape backup software", "/best-tape-backup-software")]),
        ("Company", [("About", "/about"), ("Contact", "/contact"), ("Sitemap", "/sitemap.xml")]),
    ]
    col_html = "".join(
        f'<div class="fcol"><h4>{esc(h)}</h4>' + "".join(f'<a href="{href}">{esc(t)}</a>' for t, href in links) + "</div>"
        for h, links in cols
    )
    return f"""<footer class="footer"><div class="wrap"><div class="footer-top"><div>{brand()}<p class="blurb">TapeBackup.org is an independent resource for LTO tape backup technology, pricing, and workflows. Not affiliated with the LTO Program.</p></div>{col_html}</div>
<div class="footer-bot"><span>&copy; 2026 TapeBackup.org. Independent LTO tape backup resource.</span><div class="links"><a href="/about">About</a><a href="/contact">Contact</a><a href="/sitemap.xml">Sitemap</a></div></div></div></footer>"""


def breadcrumb_ld(crumbs):
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name, "item": canonical(path)}
            for i, (name, path) in enumerate(crumbs)
        ],
    }


def faq_ld(faqs):
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs
        ],
    }


def faq_html(faqs, label):
    cards = "".join(f'<article class="faq-card"><h3>{esc(q)}</h3><p>{esc(a)}</p></article>' for q, a in faqs)
    return f'<section class="faq-grid" aria-label="{esc(label)}">{cards}</section>'


def hubspot_cta(heading, text):
    return f"""<section class="cta-band"><p class="eyebrow">Pricebook</p><h2>{esc(heading)}</h2><p>{esc(text)}</p>
<div class="hubspot-shell"><div class="hs-form-frame" data-region="eu1" data-form-id="{HUBSPOT_FORM}" data-portal-id="{HUBSPOT_PORTAL}"></div></div>
<div class="cta-actions"><a class="cta-secondary" href="/lto-tape-price-trend/history">See price history</a></div></section>"""


def page(path, title, description, body, jsonld=(), hubspot=False, og_type="website", robots="index, follow", extra_head=""):
    assert len(title) <= 60, (path, len(title), title)
    assert 70 <= len(description) <= 160, (path, len(description), description)
    ld = "".join(
        '<script type="application/ld+json">' + json.dumps(block, ensure_ascii=False).replace("</", "<\\/") + "</script>\n"
        for block in jsonld
    )
    hs = '<script src="https://js-eu1.hsforms.net/forms/embed/147689578.js" defer></script>\n' if hubspot else ""
    url = canonical(path)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<script async src="https://www.googletagmanager.com/gtag/js?id=G-L2S102SRML"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-L2S102SRML');</script>
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}" />
<meta name="robots" content="{robots}" />
<link rel="canonical" href="{url}" />
<meta property="og:type" content="{og_type}" />
<meta property="og:site_name" content="TapeBackup.org" />
<meta property="og:title" content="{esc(title)}" />
<meta property="og:description" content="{esc(description)}" />
<meta property="og:url" content="{url}" />
<meta property="og:image" content="{SITE}/og-image.png" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{esc(title)}" />
<meta name="twitter:description" content="{esc(description)}" />
<meta name="twitter:image" content="{SITE}/og-image.png" />
<meta name="theme-color" content="#5b27d6" />
<link rel="icon" href="/favicon.png" type="image/png" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link rel="stylesheet" href="/tape-q-and-a.css" />
<link rel="stylesheet" href="/pages.css" />
<script defer src="/assets/outbound-links.js"></script>
{hs}{ld}{extra_head}</head>
<body class="price-page">
<div class="site-shell">
{header()}
{body}
{footer()}
</div>
</body>
</html>
"""
