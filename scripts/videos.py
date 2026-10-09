"""Embed the tapebackup.org YouTube videos on their matching pages.

Runs from build_site.py after every page (English and /<lang>/) is written.
The player is a click-to-load facade: a thumbnail and play button that swaps in
a youtube-nocookie iframe, so pages load no YouTube code until a visitor clicks.
Each embed also adds a VideoObject JSON-LD block. Idempotent per page.
"""

import json
import os
import re

from site_shell import ROOT, SITE, esc

UPLOADED = "2026-10-04"

# page path -> video. "after": insert before the Nth section-card in <main> (1 = top of main, right under the page intro).
VIDEOS = {
    "lto-tape-price-trend": dict(id="73UkF_u3a7Q", dur="PT1M7S", after=1,
        title="LTO Tape Prices September 2026: LTO-9 Still Cheapest per TB",
        desc="Monthly LTO price update for September 2026: price per terabyte, cartridge and drive prices for LTO-6 to LTO-10."),
    "lto-tape": dict(id="2Fal_k0P6Yc", dur="PT1M38S", after=2,
        title="What Is LTO Tape? Linear Tape-Open Explained in Under 2 Minutes",
        desc="What LTO tape is, how a drive writes it, capacity by generation, the compatibility rule, what it costs in 2026 and why people keep it offline."),
    "why-tape/lto-tape-drive": dict(id="OUqB74x6AgQ", dur="PT1M44S", after=1,
        title="Which LTO Tape Drive to Buy in 2026 (LTO-9 vs LTO-10, SAS vs Thunderbolt)",
        desc="A buyer's guide to LTO drives: generation, form factor, interface, read/write compatibility, part numbers and used drives."),
    "comparisons/tape-vs-cloud-5-year-cost": dict(id="ZPs0eTwLnmQ", dur="PT2M11S", after=2,
        title="Tape vs Cloud: Backup Kung-Fu (500 TB, 5 Years, Real 2026 Prices)",
        desc="An 8-bit arcade fight between LTO tape and cloud archive storage, scored with real 2026 prices for a 500 TB archive over five years."),
    "resources/ltfs": dict(id="e1ANLap0inI", dur="PT1M34S", after=2,
        title="How to Use LTFS on Linux, Mac and Windows (LTO Tape Like a USB Drive)",
        desc="How LTFS works, the free tools for each OS, the Linux commands step by step, the Mac and Windows apps, and why you must always unmount."),
    "backup-calculator": dict(id="spbiOvrW-zQ", dur="PT49S", after=1,
        title="How Many LTO Tapes Do You Need? Free Backup Calculator Walkthrough",
        desc="A walkthrough of the free tapebackup.org backup calculator: data size, copies, recovery targets and the recommended LTO setup."),
    "lto-tape-price-trend/lto10-price": dict(id="73UkF_u3a7Q", dur="PT1M7S", after=1,
        title="LTO Tape Prices September 2026: LTO-9 Still Cheapest per TB",
        desc="Monthly LTO price update for September 2026, including LTO-10 cartridge and drive prices and the 40 TB cartridge."),
    "backup-software-finder": dict(id="e1ANLap0inI", dur="PT1M34S", after=1,
        title="How to Use LTFS on Linux, Mac and Windows (LTO Tape Like a USB Drive)",
        desc="The free route to tape: how LTFS works, the free tools for each OS and the Linux commands step by step."),
    "blog/offsite-tape-backups-still-beat-most-good-enough-plans": dict(id="z4awYQws8Lw", dur="PT39S", after="figure",
        title="Why Your Backup Tapes Need to Leave the Building (Offsite Tape Rotation)",
        desc="Why one tape set should always be outside the building, and how a weekly offsite rotation keeps it there."),
}

LABEL = {"en": "Watch", "de": "Video (Englisch)", "fr": "Vidéo (en anglais)", "it": "Video (in inglese)",
         "es": "Vídeo (en inglés)", "nl": "Video (Engels)", "pl": "Wideo (po angielsku)"}
PLAY = {"en": "Play video", "de": "Video abspielen", "fr": "Lire la vidéo", "it": "Riproduci il video",
        "es": "Reproducir el vídeo", "nl": "Video afspelen", "pl": "Odtwórz wideo"}

ONYT = {"en": "Watch on YouTube", "de": "Auf YouTube ansehen", "fr": "Voir sur YouTube", "it": "Guarda su YouTube",
        "es": "Ver en YouTube", "nl": "Bekijk op YouTube", "pl": "Obejrzyj na YouTube"}

SCRIPT = ('<script>document.addEventListener("click",function(e){var b=e.target.closest(".yt-facade");if(!b)return;'
          'var f=document.createElement("iframe");f.src="https://www.youtube-nocookie.com/embed/"+b.dataset.yt+"?autoplay=1&rel=0";'
          'f.title=b.dataset.title;f.allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture";'
          'f.allowFullscreen=true;b.replaceWith(f);});</script>')


def block(v, lang):
    thumb = f"https://i.ytimg.com/vi/{v['id']}/hqdefault.jpg"
    return (f'<section class="section-card video-card" id="video"><p class="eyebrow">{LABEL[lang]}</p>'
            f'<h2>{esc(v["title"])}</h2>'
            f'<div class="video-embed"><button type="button" class="yt-facade" data-yt="{v["id"]}" data-title="{esc(v["title"])}" aria-label="{PLAY[lang]}: {esc(v["title"])}">'
            f'<img src="{thumb}" alt="" width="480" height="360" loading="lazy" decoding="async"><span class="yt-play" aria-hidden="true"></span></button></div>'
            f'<p class="video-link"><a href="https://youtu.be/{v["id"]}" rel="noopener">{ONYT[lang]}</a></p></section>')


def schema(v, path):
    return json.dumps({
        "@context": "https://schema.org", "@type": "VideoObject", "name": v["title"], "description": v["desc"],
        "thumbnailUrl": [f"https://i.ytimg.com/vi/{v['id']}/maxresdefault.jpg", f"https://i.ytimg.com/vi/{v['id']}/hqdefault.jpg"],
        "uploadDate": UPLOADED, "duration": v["dur"],
        "embedUrl": f"https://www.youtube-nocookie.com/embed/{v['id']}", "contentUrl": f"https://youtu.be/{v['id']}",
        "publisher": {"@type": "Organization", "name": "TapeBackup.org", "url": SITE},
    }, ensure_ascii=False)


def embed(file, v, lang, path):
    s = open(file, encoding="utf-8").read()
    if f'data-yt="{v["id"]}"' in s:
        return False
    b = block(v, lang)
    if v["after"] == "figure":
        new, n = re.subn(r'(<section class="article-body">.*?</figure>)', lambda m: m.group(1) + b, s, count=1, flags=re.S)
    else:
        main = s.index('<main class="page">')
        starts = [m.start() for m in re.finditer(r'<section class="section-card"', s[main:])]
        if len(starts) < v["after"]:
            return False
        i = main + starts[v["after"] - 1]
        new, n = s[:i] + b + s[i:], 1
    if not n:
        return False
    ld = f'<script type="application/ld+json">{schema(v, path)}</script>\n'
    new = new.replace("</head>", ld + "</head>", 1).replace("</body>", SCRIPT + "\n</body>", 1)
    open(file, "w", encoding="utf-8").write(new)
    return True


def embed_all(langs):
    n = 0
    for path, v in VIDEOS.items():
        for lang in ["en"] + list(langs):
            f = os.path.join(ROOT, *([] if lang == "en" else [lang]), *path.split("/"), "index.html")
            if os.path.exists(f) and embed(f, v, lang, path):
                n += 1
    return n
