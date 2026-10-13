"""AI advisor pages ("which X is best for me") rendered in the site's own header and footer.

The advisor itself (API route, video engine, examples) is made by the advisor-builder skill:
    node ~/.claude/skills/advisor-builder/scripts/scaffold.mjs advisor.json --repo .
which writes data/advisors/<slug>.json (config) and data/advisors/<slug>.page.json (page data).
This module turns each page.json into /<slug>/index.html. English only: the page has its
own language switch (the engine translates the form and the video in the browser).
"""

import glob
import json
import os
import re

from site_shell import ROOT, SITE, breadcrumb_ld, esc, page, write

DATA = os.path.join(ROOT, "data", "advisors")


def _plain(desc):
    """Criterion descriptions without the Ledger source note in brackets."""
    return re.sub(r"\s*\((?:Ledger|inverted Ledger)[^)]*\)", "", desc).strip()


def _body(pg, cfg):
    en = pg["i18n"]["en"]
    cta = pg.get("cta")
    cfg_js = json.dumps(pg["config"], ensure_ascii=False).replace("</", "<\\/")
    cap = lambda t: t[:1].upper() + t[1:]
    crit_rows = "".join(f"<tr><td><strong>{esc(c['label'])}</strong></td><td>{esc(cap(_plain(c['desc'])))}.</td></tr>" for c in cfg["criteria"])
    cands = cfg.get("candidates") or []
    cand_rows = "".join(f"<tr><td><strong>{esc(c['name'])}</strong></td><td>{esc(c.get('kind') or '')}</td></tr>" for c in sorted(cands, key=lambda c: c["name"].lower()))
    faq = "".join(f'<div class="faq"><h3>{esc(f["q"])}</h3><p>{esc(f["a"])}</p></div>' for f in pg.get("faq") or [])
    cta_html = (f'<a class="ctabox static" href="{esc(cta["href"])}"><b>{esc(cta["title"]["en"])}</b><span>{esc(cta["line"]["en"])}</span>'
                f'<i>{esc((cta.get("button") or {}).get("en") or "Contact us")}</i></a>') if cta else ""
    return f"""<main class="page"><div class="container"><div class="adv">
<section class="adv-intro">
<div class="adv-top"><span class="adv-eyebrow">{esc(pg["eyebrow"])}</span><span class="langs" id="langs" aria-label="Language"></span></div>
<h1 data-i18n="h1">{esc(en["h1"])}</h1>
<p class="lead" data-i18n="lead">{esc(en["lead"])}</p>
</section>
<div class="layout">
<section class="adv-card hero">
<form id="f"><div id="scenario"></div>
<div class="ask free"><textarea id="q" maxlength="500" rows="3" data-i18n-ph="ph" placeholder="{esc(en["ph"])}" aria-label="{esc(en["h1"])}"></textarea>
<button class="go" id="go" type="submit" data-i18n="go">{esc(en["go"])}</button></div>
<p class="hint" data-i18n="hint">{esc(en["hint"])}</p></form>
<div class="chips" id="chips"><span data-i18n="examples">Examples:</span></div>
</section>
<section class="adv-card stage" aria-label="Video">
<div class="screen" id="screen"><canvas id="cv" width="1280" height="720" role="img" aria-label="Animated recommendation"></canvas><button class="fsbtn" id="fsbtn" type="button" aria-label="Full screen" title="Full screen">&#x26F6;</button><span class="tapfs" id="tapfs">Tap for full screen</span></div>
<div class="controls">
<button class="ctl" id="play" type="button" disabled>Pause</button>
<button class="ctl" id="restart" type="button" disabled data-i18n="replay">Replay</button>
<div class="bar" id="bar" title="Seek"><i id="fill"></i></div>
<button class="ctl" id="voice" type="button" aria-pressed="false">Voice off</button>
<button class="ctl" id="dl" type="button" disabled data-i18n="download">Download video</button>
<button class="ctl" id="share" type="button" disabled data-i18n="share">Copy link</button>
</div>
<p class="status" id="status" role="status"></p>
</section>
</div>
<section class="adv-card plan" id="plan"></section>
{cta_html}
<section class="adv-card how">
<h2 data-i18n="howTitle">How it works</h2>
<ol><li data-i18n="how1">{esc(en["how1"])}</li><li data-i18n="how2">{esc(en["how2"])}</li><li data-i18n="how3">{esc(en["how3"])}</li></ol>
<p class="note" data-i18n="note">{esc(en["note"])}</p>
</section>
<section class="adv-card how"><h2>What the advisor weighs</h2>
<p class="note">Each product has a score from 0 to 5 on these {len(cfg["criteria"])} points in the {esc(cfg["source"]["name"])}. Your message decides which points matter and how much; the ranking is the weighted average of the scores.</p>
<div class="table-wrap"><table class="price-table"><thead><tr><th>What it checks</th><th>Meaning</th></tr></thead><tbody>{crit_rows}</tbody></table></div>
</section>
<section class="adv-card how"><h2>The {len(cands)} products it ranks</h2>
<p class="note">Products the Ledger could not rank fairly (no recent release, an unclear product line, or tools that reach tape only through other products) are left out. For backup software that writes to tape, use the <a href="/backup-software-finder">tape backup software finder</a> or the <a href="/best-tape-backup-software">best tape backup software</a> comparison.</p>
<div class="table-wrap"><table class="price-table"><thead><tr><th>Product</th><th>Type</th></tr></thead><tbody>{cand_rows}</tbody></table></div>
</section>
<section class="adv-card how" id="questions"><h2>{esc(pg.get("faqTitle") or "Questions")}</h2>{faq}</section>
</div></div></main>
<script>window.ADVISOR = {cfg_js};</script>
<script src="/_advisor/engine.js?v={pg["engineVersion"]}"></script>"""


def build_all():
    paths = []
    for f in sorted(glob.glob(os.path.join(DATA, "*.page.json"))):
        pg = json.load(open(f, encoding="utf-8"))
        cfg = json.load(open(f.replace(".page.json", ".json"), encoding="utf-8"))
        path = "/" + pg["slug"]
        ld = list(pg["structuredData"]) if isinstance(pg["structuredData"], list) else [pg["structuredData"]]
        ld.append(breadcrumb_ld([("Home", "/"), (pg["config"]["name"]["en"], path)]))
        head = f'<link rel="stylesheet" href="/_advisor/advisor.css?v={pg["engineVersion"]}" />\n'
        write(path, page(path, pg["title"], pg["description"], _body(pg, cfg), ld, extra_head=head))
        paths.append(path)
    return paths


if __name__ == "__main__":
    print(build_all())
