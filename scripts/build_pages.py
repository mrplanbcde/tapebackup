"""Build the non-price pages: restored guides, tools, contact, homepage, 404.

The guides under data/legacy-pages/ were captured from the React app that ran
the site until June 2026. When that app was replaced by a homepage-only file,
these URLs silently started rendering the homepage. They are now plain HTML.
"""

import json
import os
import re

from bs4 import BeautifulSoup, NavigableString, Tag

from site_shell import GENS, ROOT, SITE, breadcrumb_ld, esc, faq_html, faq_ld, hubspot_cta, page, slug_for, write

KEEP_BLOCK = {"h1", "h2", "h3", "h4", "p", "ul", "ol", "table", "blockquote", "pre", "hr"}
INLINE = {"strong", "b", "em", "i", "a", "code", "br", "span", "sup", "sub", "small"}
DROP = {"svg", "script", "style", "input", "select", "textarea", "form", "canvas", "nav", "img", "label", "noscript"}
ALLOWED_ATTRS = {"a": {"href"}, "td": {"colspan", "rowspan"}, "th": {"colspan", "rowspan"}}

LEGACY = {
    "/why-tape": ("why-tape", "Why Use Tape Storage? Benefits of LTO Backup", "Why LTO tape still wins for long-term archives: lowest cost per TB, offline air-gap protection against ransomware, WORM media and decades of shelf life."),
    "/why-tape/lto-tape-drive": ("why-tape__lto-tape-drive", "What Is an LTO Tape Drive? Generations and Specs", "How LTO tape drives work, what Linear Tape-Open means, generation capacities from LTO-1 to LTO-10, compatibility rules and when a tape drive makes sense."),
    "/why-tape/lto-vs-hdd": ("why-tape__lto-vs-hdd", "LTO Tape vs HDD for Long-Term Storage | TapeBackup", "LTO tape vs hard drives for backup and archive: lifespan, cost per TB, ransomware protection, access speed and which one fits your data."),
    "/resources": ("resources", "Tape Backup Resources and LTO Guides | TapeBackup", "LTO tape backup resources: price guides, buying advice for used tapes, backup software reviews, vendor links and official LTO references in one place."),
    "/resources/cheap-lto-tapes": ("resources__cheap-lto-tapes", "Cheap LTO Tapes: How to Buy Used Tape Safely", "How to buy cheap or used LTO tapes without losing data: what to check, which sellers and generations to avoid, and when new media is worth paying for."),
    "/resources/tape-backup-software/catalogicdpx": ("resources__tape-backup-software__catalogicdpx", "Catalogic DPX Review: Tape Backup and LTO Support", "Catalogic DPX reviewed as tape backup software: LTO drive and library support, NDMP, disk to tape workflows, encryption and where it fits."),
    "/about": ("about", "About TapeBackup.org: Independent LTO Tape Resource", "About TapeBackup.org, an independent LTO tape resource, plus a plain guide to what LTO means, how linear tape works and why it is still used."),
    "/comparisons": ("comparisons", "Tape vs Disk vs Cloud Backup Compared | TapeBackup", "LTO tape, disk and cloud backup compared on cost per TB, recovery speed, ransomware protection, lifespan and energy use, with guidance on each."),
    "/lto-tape-brand": ("lto-tape-brand", "LTO Tape Brands: Who Really Makes Your Cartridges", "Only Fujifilm and Sony make LTO tape. See how HPE, IBM, Quantum and Dell cartridges compare, and whether the brand on the label matters."),
    "/best-tape-backup-software": ("best-tape-backup-software", "Best Tape Backup Software in 2026 | TapeBackup", "The best tape backup software for LTO in 2026 compared: Catalogic DPX, Veeam, Commvault and others on tape support, licensing and migration paths."),
}

# Price claims in the restored guides that the September 2026 research contradicts.
PRICE_FIXES = [
    ("Drives range from $3,000 (LTO-8) to $6,500 (LTO-9).", "New standalone drives list from about $4,850 (LTO-8) to $13,500 (LTO-9) as of September 2026."),
    ("LTO-9 tapes cost ~$70-90 (18 TB = $4-5/TB). LTO-10 approaches $3-4/TB.", "LTO-9 tapes cost about $92 to $112 in September 2026 ($5.14 to $6.20 per TB). LTO-10 30 TB tapes run about $8.50 to $10 per TB."),
    ("tape media costing approximately $3-6 per TB", "tape media costing roughly $5 to $7 per TB on LTO-8 and LTO-9"),
    ("LTO-8 tapes (12 TB native) typically cost $70-90, translating to approximately $6-7.50 per TB", "LTO-8 tapes (12 TB native) cost about $70 to $80 in September 2026, roughly $5.80 to $6.70 per TB"),
    ("LTO-9 tapes (18 TB native) provide similar per-TB pricing, while LTO-10 (30 TB native) is expected to approach $3-4 per TB at volume.", "LTO-9 tapes (18 TB native) are slightly cheaper per TB at about $5.10 to $6.20, while LTO-10 30 TB tapes still cost about $8.50 to $10 per TB."),
    ("The primary investment is the tape drive itself ($3,000-$6,500)", "The primary investment is the tape drive itself (about $4,850 to $13,500 for new LTO-8 and LTO-9 drives in September 2026)"),
    ("cost-efficiency ($3-6/TB)", "cost-efficiency (about $5 to $6 per TB on LTO-9)"),
    ("~$90 - $110", "~$70 - $80"),
    ("~$140 - $170", "~$92 - $112"),
    ("~$250 - $350+", "~$256 - $300 (30 TB)"),
    ("~$70 - $85", "Rarely worth it, new is ~$70 - $80"),
    ("~$110 - $130", "Rarely worth it, new is ~$92 - $112"),
]

DROP_SECTIONS = {"Downloadable Resources"}


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
    for old, new in PRICE_FIXES:
        flow = flow.replace(esc(old).replace("&#x27;", "'"), esc(new)).replace(old, new)
    h1 = re.search(r"<h1>(.*?)</h1>", flow)
    h1_text = h1.group(1) if h1 else title
    flow = flow.replace(h1.group(0), "", 1) if h1 else flow
    lead = ""
    m = re.match(r"\s*<p>(.*?)</p>", flow)
    if m:
        lead = m.group(1)
        flow = flow[m.end():]
    body_sections = split_sections(flow)
    related = ""
    if path == "/resources":
        related = """<section class="section-card"><p class="eyebrow">Price guides and tools</p><h2>LTO price guides and buying tools</h2><div class="link-grid">
<a href="/lto-tape-price-trend">LTO price tracker<span>September 2026 tape and drive prices</span></a>
<a href="/lto-tape-price-trend/history">LTO price history<span>Snapshots since September 2025</span></a>
<a href="/backup-calculator">Backup calculator<span>Cartridges and cost for your data</span></a>
<a href="/backup-software-finder">Software finder<span>Match software to your tape use</span></a>
<a href="/lto-tape-brand">LTO tape brands<span>Who really makes the tape</span></a>
<a href="/tape-q-and-a">Tape Q&amp;A<span>Short answers to tape questions</span></a></div></section>"""
    if "$" in body_sections and path in ("/why-tape/lto-tape-drive", "/about", "/resources/cheap-lto-tapes", "/comparisons", "/why-tape"):
        related += '<section class="section-card"><p class="eyebrow">Current prices</p><h2>Check current LTO prices</h2><p>Prices on this page are rounded guidance. For seller listings checked in September 2026, see the <a href="/lto-tape-price-trend">LTO price tracker</a> and the <a href="/lto-tape-price-trend/history">price history</a>.</p></section>'
    crumbs = [("Home", "/")]
    segs = path.strip("/").split("/")
    if len(segs) > 1:
        parent = "/" + segs[0]
        crumbs.append((LEGACY[parent][1].split(":")[0].split("|")[0].strip() if parent in LEGACY else segs[0].title(), parent))
    crumbs.append((re.sub(r"<[^>]+>", "", h1_text), path))
    body = f"""<section class="hero"><div class="container"><div class="hero-copy" style="max-width:860px">
<h1 style="max-width:none">{h1_text}</h1>{f'<p>{lead}</p>' if lead else ''}</div></div></section>
<main class="page"><div class="container"><div class="section-stack">{body_sections}{related}</div></div></main>"""
    ld = [breadcrumb_ld(crumbs), {"@context": "https://schema.org", "@type": "Article", "headline": re.sub(r"<[^>]+>", "", h1_text), "description": desc, "dateModified": "2026-09-17",
          "author": {"@type": "Organization", "name": "TapeBackup.org"}, "publisher": {"@type": "Organization", "name": "TapeBackup.org", "url": SITE}, "mainEntityOfPage": SITE + path}]
    write(path, page(path, title, desc, body, ld, og_type="article"))
    return path


# ---------------------------------------------------------------- tools

def build_calculator(current):
    path = "/backup-calculator"
    gens = current["generations"]
    mid = lambda item: round((item["lowUSD"] + item["highUSD"]) / 2, 2) if item.get("lowUSD") is not None else None
    model = {g: {"tb": gens[g]["nativeTB"], "tape": mid(gens[g]["cartridge"]), "drive": mid(gens[g].get("driveInternal", {})) or mid(gens[g].get("driveExternal", {}))} for g in ["LTO-8", "LTO-9", "LTO-10"]}
    model_json = json.dumps(model)
    body = f"""<section class="hero"><div class="container hero-grid"><div class="hero-copy">
<p class="eyebrow">Tool</p><h1>Tape Backup Capacity and Cost Calculator</h1>
<p>Enter how much data you protect, how many copies you keep and how fast you need it back. The calculator recommends tape, disk, cloud or a mix, and estimates cartridges and media cost from September 2026 LTO prices.</p></div>
<aside class="hero-panel"><p class="panel-label">Prices used</p><p class="panel-copy">Midpoints of seller listings from the <a href="/lto-tape-price-trend">LTO price tracker</a>: LTO-8 tapes ${model['LTO-8']['tape']:.0f}, LTO-9 tapes ${model['LTO-9']['tape']:.0f}, LTO-10 30 TB tapes ${model['LTO-10']['tape']:.0f}.</p></aside></div></section>
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
</section>
<section class="section-card"><p class="eyebrow">How it works</p><h2>How the calculator decides</h2>
<ul><li>Under 15 TB, a tape drive rarely pays for itself, so disk plus cloud is recommended.</li><li>If you need recovery in minutes, the first copy has to live on disk or flash, with tape for long-term and offline copies.</li><li>Otherwise LTO-8 is suggested under 50 TB, LTO-9 up to 500 TB, and LTO-9 or LTO-10 above that.</li><li>Cartridge counts use native capacity with no compression, and costs use the midpoint of current seller listings. Drive cost is one new internal drive where one is listed.</li></ul>
<p>Estimates exclude software, HBAs, libraries, tax and shipping. See the <a href="/lto-tape-price-trend">LTO price tracker</a> for the listings behind these numbers.</p></section>
</div></div></main>
<script>
(function(){{
var M={model_json};
var f=document.getElementById('calc'),out=document.getElementById('calc-result');
function usd(n){{return '$'+Math.round(n).toLocaleString('en-US');}}
function est(gen,total){{var g=M[gen];var n=Math.ceil(total/g.tb);var s='<p><strong>'+gen+' estimate:</strong> '+n+' cartridges ('+g.tb+' TB native each), about '+usd(n*g.tape)+' in media';if(g.drive){{s+=' plus about '+usd(g.drive)+' for one drive';}}return s+'.</p>';}}
f.addEventListener('submit',function(e){{
e.preventDefault();
var tb=parseFloat(document.getElementById('capacity').value),copies=parseInt(document.getElementById('copies').value,10),rto=document.getElementById('rto').value,rpo=document.getElementById('rpo').value;
var h,t;
if(!tb||tb<=0){{h='Enter your data size';t='<p>Type the total amount of data you need to protect, in terabytes.</p>';}}
else if(rpo==='continuous'&&rto==='days'){{h='Check these requirements';t='<p>You chose real-time backups but accept recovery taking days. Teams that need continuous protection usually need fast recovery too. Choose a faster recovery time, or a daily or weekly recovery point.</p>';}}
else{{
var total=tb*copies;
if(tb<15){{h=rto==='instant'?'Recommended: SSD or HDD plus cloud':'Recommended: NAS (HDD) plus cloud archive';t='<p>With '+tb+' TB, the cost of a tape drive is hard to justify. Keep a local disk copy for fast restores and a cloud cold-tier copy offsite.</p>'+est('LTO-8',total);}}
else if(rto==='instant'){{h='Recommended: disk or flash first, LTO tape second';t='<p>Instant recovery means your first copy must be on disk or flash. For '+total+' TB across all copies, keep only recent restore points on disk and put long-term, offline copies on LTO tape.</p>'+est(tb<500?'LTO-9':'LTO-10',total);}}
else{{var gen=tb<50?'LTO-8':(tb<500?'LTO-9':'LTO-10');h='Recommended: '+(tb<500?gen:'LTO-9 or LTO-10')+' tape';
t=tb<50?'<p>LTO-8 (12 TB native) keeps drive cost down for this data size and still gives you offline copies.</p>':(tb<500?'<p>LTO-9 (18 TB native) has the lowest media cost per terabyte in 2026 and fewer cartridges to handle than LTO-8.</p>':'<p>At this size density matters. LTO-9 has the lowest cost per TB; LTO-10 needs fewer cartridges and library slots but costs more per TB and needs new full-height drives.</p>');
t+=est(tb<500?gen:'LTO-9',total);if(tb>=500){{t+=est('LTO-10',total);}}
t+='<p>With '+total+' TB across all copies, tape gives you an air gap against ransomware and avoids cloud restore fees.</p>';}}
if(rpo==='continuous'&&h.indexOf('tape')>-1){{t+='<p><em>Real-time recovery points need a disk buffer in front of tape (disk to disk to tape).</em></p>';}}
}}
out.innerHTML='<h3>'+h+'</h3>'+t;out.hidden=false;
}});
}})();
</script>"""
    desc = "Free tape backup calculator: enter data size, copies and recovery targets to get a tape, disk or cloud recommendation with 2026 LTO cartridge costs."
    ld = [breadcrumb_ld([("Home", "/"), ("Backup calculator", path)]),
          {"@context": "https://schema.org", "@type": "WebApplication", "name": "Tape Backup Capacity and Cost Calculator", "applicationCategory": "UtilitiesApplication", "operatingSystem": "Any", "url": SITE + path, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}}]
    write(path, page(path, "Tape Backup Calculator: LTO Capacity and Cost", desc, body, ld))
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
    body = f"""<section class="hero"><div class="container hero-grid"><div class="hero-copy">
<p class="eyebrow">Tool</p><h1>Tape Backup Software Finder</h1>
<p>Hardware is half the job. Answer four questions to get a shortlist of backup software that fits how you use tape, the size of your estate and your budget.</p></div>
<aside class="hero-panel"><p class="panel-label">Want the detail?</p><p class="panel-copy">Read the full <a href="/best-tape-backup-software">best tape backup software comparison</a> or the <a href="/resources/tape-backup-software/catalogicdpx">Catalogic DPX review</a>.</p></aside></div></section>
<main class="page"><div class="container"><div class="section-stack">
<section class="section-card"><h2>Find your backup software</h2>
<form class="tool-form" id="finder">{fields}<button class="tool-submit" type="submit">Show my match</button></form>
<div class="tool-result" id="finder-result" hidden aria-live="polite"></div></section>
<section class="section-card"><p class="eyebrow">Shortlist</p><h2>Software this finder recommends from</h2>
<ul><li><strong>Catalogic DPX</strong>: tape-focused enterprise backup with broad drive, library and NDMP support.</li><li><strong>Veeam Backup &amp; Replication</strong>: the common choice for virtualized estates, with tape jobs as a secondary target.</li><li><strong>Commvault</strong>: large, feature-rich platform with deep cloud integration.</li><li><strong>Nakivo</strong>: lower-cost option for smaller environments that need basic tape support.</li><li><strong>Veeam for Microsoft 365 and CloudCasa</strong>: SaaS and Kubernetes backup.</li></ul></section>
</div></div></main>
<script>
(function(){{
var f=document.getElementById('finder'),out=document.getElementById('finder-result');
function val(n){{return f.querySelector('input[name="'+n+'"]:checked').value;}}
f.addEventListener('submit',function(e){{
e.preventDefault();
var env=val('env'),tape=val('tape'),scale=val('scale'),prio=val('prio'),v,r;
if(tape==='heavy'||(tape==='secondary'&&prio==='value')){{v='Catalogic DPX';r='Catalogic DPX is built around tape. It supports a very wide range of LTO drives and libraries, including older ones, handles NDMP well and costs less than most enterprise suites when tape is central. <a href="/resources/tape-backup-software/catalogicdpx">Read the DPX review</a>.';}}
else if(env==='saas'){{v='Veeam for Microsoft 365';r='For SaaS data, Veeam for Microsoft 365 is the market leader. If you also run Kubernetes, look at CloudCasa.';}}
else if(tape==='none'){{if(env==='virtual'){{v='Veeam Backup & Replication';r='For a virtual, disk-based estate Veeam is the standard choice and works well with disk and cloud targets.';}}else{{v='Acronis or Commvault';r='For mixed environments without tape, Acronis has strong security features and Commvault has deep cloud integration.';}}}}
else if(scale==='small'){{v='Nakivo';r='For smaller environments that need basic tape support without an enterprise price, Nakivo is a solid option.';}}
else{{v='Veeam or Catalogic DPX';r='Veeam is the popular choice for virtualization. Compare it with Catalogic DPX if your data is growing, because DPX licensing and tape handling often give a lower total cost.';}}
out.innerHTML='<h3>Your match: '+v+'</h3><p>'+r+'</p><p><a href="/best-tape-backup-software">Compare all tape backup software</a></p>';out.hidden=false;
}});
}})();
</script>"""
    desc = "Answer four questions to find tape backup software that fits your environment, tape usage and budget: Catalogic DPX, Veeam, Commvault or Nakivo."
    ld = [breadcrumb_ld([("Home", "/"), ("Software finder", path)])]
    write(path, page(path, "Tape Backup Software Finder: Match LTO Software", desc, body, ld))
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
    per_tb_9 = f"${l9['perTBLow']:.0f}-{l9['perTBHigh']:.0f}"
    with open(os.path.join(ROOT, "data", "home-template.html"), encoding="utf-8") as f:
        tpl = f.read()
    blog = json.load(open(os.path.join(ROOT, "data", "home-blog.json"), encoding="utf-8"))
    cards = "".join(
        f'<article class="news-card"><a href="{esc(b["href"])}" style="display:contents"><div class="news-thumb"><span class="gloss"></span><span class="tcart"></span><span class="cat">{esc(b["cat"])}</span></div><div class="news-body"><span class="date">{esc(b["date"])}</span><h3>{esc(b["h"])}</h3><div class="more"><span class="textlink">Read more<span class="arr">{ARROW}</span></span></div></div></a></article>'
        for b in blog
    )
    out = tpl.replace("{{PER_TB_9}}", per_tb_9).replace("{{LTO9_RANGE}}", f"${l9['lowUSD']:.0f} to ${l9['highUSD']:.0f}").replace("{{BLOG_CARDS}}", cards)
    write("/", out)
    return "/"


ARROW = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>'


def build_all(current):
    paths = []
    for path, (key, title, desc) in LEGACY.items():
        paths.append(build_legacy(path, key, title, desc))
    paths += [build_calculator(current), build_finder(), build_contact(), build_home(current)]
    build_404()
    return paths
