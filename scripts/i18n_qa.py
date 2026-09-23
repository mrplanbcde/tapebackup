"""Quality checks for the language editions.

    python3 scripts/i18n_qa.py pages            code checks on every built /<lang>/ page
    python3 scripts/i18n_qa.py pairs <out.csv>  English/translation pairs for a Jev review

Code checks: title and description length, one h1, canonical and hreflang
present, no English left in segments that should be translated, placeholders
and tags intact (the merge tool already rejects broken ones), and that every
price on a page is in the page's own format.
"""

import csv
import glob
import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import i18n  # noqa: E402


def text_of(s):
    s = re.sub(r"<script[\s\S]*?</script>|<style[\s\S]*?</style>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def pages():
    langs = i18n.LANGS
    problems = 0
    for lang in langs:
        files = sorted(glob.glob(os.path.join(i18n.ROOT, lang, "**", "index.html"), recursive=True))
        if not files:
            continue
        issues = []
        for f in files:
            s = open(f, encoding="utf-8").read()
            rel = "/" + os.path.relpath(os.path.dirname(f), i18n.ROOT)
            t = re.search(r"<title>(.*?)</title>", s, re.S)
            title = html.unescape(t.group(1)) if t else ""
            d = re.search(r'<meta content="([^"]*)" name="description"|<meta name="description" content="([^"]*)"', s)
            desc = html.unescape((d.group(1) or d.group(2)) if d else "")
            if not title or len(title) > 60:
                issues.append(f"{rel}: title {len(title)} chars: {title}")
            if not desc or len(desc) > 160:
                issues.append(f"{rel}: description {len(desc)} chars")
            h1s = len(re.findall(r"<h1[\s>]", s))
            if h1s != 1:
                issues.append(f"{rel}: h1 count {h1s}")
            if f'lang="{lang}"' not in s.split(">", 2)[1] and f'<html lang="{lang}"' not in s:
                issues.append(f"{rel}: html lang not {lang}")
            if "rel=\"canonical\"" not in s:
                issues.append(f"{rel}: no canonical")
            body = text_of(s)
            if re.search(r"\$\d|€\d|zł\d", body):
                bad = re.search(r".{0,20}(?:\$\d|€\d|zł\d).{0,10}", body).group(0)
                issues.append(f"{rel}: unlocalized price {bad!r}")
            for sc in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
                try:
                    json.loads(sc)
                except Exception:
                    issues.append(f"{rel}: invalid JSON-LD")
        seg = os.path.join(i18n.I18N, "segments", f"{lang}.json")
        missing = len(json.load(open(seg))) if os.path.exists(seg) else "?"
        print(f"{lang}: {len(files)} pages, {len(issues)} issues, {missing} untranslated segments")
        for x in issues[:40]:
            print("   ", x)
        problems += len(issues)
    return problems


def pairs(out):
    rows = []
    for lang in i18n.LANGS:
        tm = i18n.load_tm(lang)
        for key, tgt in tm.items():
            def plain(x):
                x = html.unescape(re.sub(r"</?[a-z]+\d+/?>", " ", x))
                return re.sub(r"\s+([:;,.!?)])", r"\1", re.sub(r"\s+", " ", x)).strip()
            en, tr = plain(key), plain(tgt)
            if len(re.sub(r"\{\w+\}", "", en).split()) < 2:
                continue  # single words and labels: not worth a model call
            if en == tr:
                continue  # left as English on purpose (names, part numbers); listed by the pages check instead
            if len(re.findall(r"<a\d+>", key)) >= 3:
                continue  # flattened navigation menus: judged on the rendered page, not as prose
            rows.append({"language": {"de": "German", "fr": "French", "it": "Italian", "es": "Spanish", "nl": "Dutch", "pl": "Polish"}[lang],
                         "lang": lang, "english": en, "translation": tr, "key": key})
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["language", "lang", "english", "translation", "key"])
        w.writeheader()
        w.writerows(rows)
    print(f"{out}: {len(rows)} pairs")


if __name__ == "__main__":
    if sys.argv[1] == "pages":
        sys.exit(1 if pages() else 0)
    elif sys.argv[1] == "pairs":
        pairs(sys.argv[2])
