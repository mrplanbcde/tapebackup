"""Put the explanatory figures from scripts/figs_*.py onto their pages.

    add_figures(root)   # root = the site folder, or a staged language build

Runs from build_site.py on the English site and on every staged market build
(before translation, so each alt text and caption becomes a translatable segment).
A page that already shows the figure file is left alone, so a rebuild is idempotent.
Blog posts and Q&A answers are hand-published HTML, so they are edited in place.
"""

import os
import re

import draw_figures
from site_shell import esc, figure

# Pages where the figure goes before the first section card instead of after it.
BEFORE_FIRST_CARD = {"/contact"}


def _insert(s, path, fig_html):
    if path.startswith("/blog/"):
        new, n = re.subn(r'(<section class="article-body">(?:<h[23][^>]*>.*?</h[23]>)?<p>.*?</p>)', lambda m: m.group(1) + fig_html, s, count=1, flags=re.S)
        return new if n else None
    if path.startswith("/tape-q-and-a/"):
        new, n = re.subn(r'(<div class="answer-copy"><p>.*?</p>)', lambda m: m.group(1) + fig_html, s, count=1, flags=re.S)
        return new if n else None
    main = s.find('<main class="page">')
    if main < 0:
        return None
    card = f'<section class="section-card">{fig_html}</section>'
    cards = [m.start() for m in re.finditer(r'<section class="section-card', s[main:])]
    if not cards:
        return None
    if path in BEFORE_FIRST_CARD:
        i = main + cards[0]
        return s[:i] + card + s[i:]
    end = s.find("</section>", main + cards[0])
    if end < 0:
        return None
    end += len("</section>")
    return s[:end] + card + s[end:]


def add_figures(root):
    _, placements = draw_figures.all_figures()
    n = 0
    for p in placements:
        f = os.path.join(root, *p["path"].strip("/").split("/"), "index.html")
        if not os.path.exists(f):
            continue
        s = open(f, encoding="utf-8").read()
        if f'/assets/figures/{p["file"]}"' in s:
            continue
        fig_html = figure(p["file"], p["alt"], p["caption"], p.get("w", 960), p.get("h", 420))
        new = _insert(s, p["path"], fig_html)
        if new is None:
            print(f"figure not placed (no anchor): {p['path']}")
            continue
        open(f, "w", encoding="utf-8").write(new)
        n += 1
    return n


def write_files():
    """Write every figure SVG (the existing drawings plus figs_*.py) to assets/figures."""
    figs, _ = draw_figures.all_figures()
    for name, fn in figs.items():
        draw_figures.write(name, fn())
    return len(figs)
