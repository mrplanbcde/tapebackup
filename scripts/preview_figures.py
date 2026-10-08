"""Render figures to PNG contact sheets for review.

    python3 scripts/preview_figures.py [pattern ...]   # file-name substrings; default: figures from figs_*.py
Writes .build/fig-preview/sheet-N.png (6 figures per sheet) and prints each figure's size.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import draw_figures as d
from playwright.sync_api import sync_playwright

pats = sys.argv[1:]
figs, _ = d.all_figures()
names = [n for n in figs if (any(p in n for p in pats) if pats else n not in d.FIGURES)]
out = os.path.join(d.ROOT, ".build", "fig-preview"); os.makedirs(out, exist_ok=True)
for i in range(0, len(names), 6):
    chunk = names[i:i + 6]
    cells = "".join(f'<div style="width:960px;margin:0 0 14px"><div style="font:12px monospace;color:#555">{n}</div>{figs[n]()}</div>' for n in chunk)
    html = f'<body style="margin:12px;background:#fff;display:grid;grid-template-columns:960px 960px;gap:0 14px">{cells}</body>'
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1960, "height": 1400}); pg.set_content(html)
        pg.screenshot(path=os.path.join(out, f"sheet-{i // 6 + 1}.png"), full_page=True); b.close()
print(f"{len(names)} figures -> {os.path.relpath(out, d.ROOT)}/sheet-N.png")
