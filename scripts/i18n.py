"""Turn market builds into translated language editions (/de/, /fr/, ...).

How it works
------------
1. build_site.py renders each in-scope page for a European market in English,
   with that market's prices, into .build/<lang>/ (see markets.py).
2. This module cuts every page into segments: the inner HTML of each element
   that holds text and only inline markup, plus <title>, meta descriptions,
   aria-labels, JSON-LD strings and the data-i18n JSON blocks that page
   scripts read. Inside a segment, inline tags become <a1>..</a1>, <b2>..</b2>,
   <br3/> and every token containing a digit (prices, part numbers, LTO-9,
   dates) becomes {0}, {1}, ... so the same sentence has the same key whatever
   this month's prices are.
3. data/i18n/tm/<lang>.json maps each masked English segment to its
   translation. Rendering swaps segments in, puts the real tags and values
   back, localizes numbers and currency (92,45 € / € 92,45 / 92,45 zł),
   rewrites internal links to the language, and sets lang, canonical, hreflang
   and the language switch.
4. Segments with no translation stay English and are listed by
   `python3 scripts/i18n.py missing <lang>` so a refresh only needs the delta.

A language is published (indexable, in the sitemap) only when
data/i18n/languages.json marks it "indexable": true.
"""

import copy
import html
import json
import os
import re
import sys

from bs4 import BeautifulSoup, Comment, NavigableString, Tag

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
I18N = os.path.join(ROOT, "data", "i18n")
STAGE = os.path.join(ROOT, ".build")
SITE = "https://tapebackup.org"

LANG_META = {
    "en": {"name": "English", "locale": "en_US"},
    "de": {"name": "Deutsch", "locale": "de_DE"},
    "fr": {"name": "Français", "locale": "fr_FR"},
    "it": {"name": "Italiano", "locale": "it_IT"},
    "es": {"name": "Español", "locale": "es_ES"},
    "nl": {"name": "Nederlands", "locale": "nl_NL"},
    "pl": {"name": "Polski", "locale": "pl_PL"},
}
LANGS = ["de", "fr", "it", "es", "nl", "pl"]

# Pages that exist in every language. Everything else (blog, Q&A, archives) stays English.
SCOPE = [
    "/", "/lto-tape-price-trend", "/lto-tape-price-trend/lto6-price", "/lto-tape-price-trend/lto7-price",
    "/lto-tape-price-trend/lto8-price", "/lto-tape-price-trend/lto9-price", "/lto-tape-price-trend/lto10-price",
    "/lto-tape-price-trend/history", "/comparisons/tape-vs-cloud-5-year-cost", "/backup-calculator",
    "/backup-software-finder", "/about", "/contact", "/why-tape", "/why-tape/lto-tape-drive", "/why-tape/lto-vs-hdd",
    "/comparisons", "/lto-tape-brand", "/resources", "/resources/cheap-lto-tapes", "/resources/lto-tape-migration",
    "/resources/tape-storage-market", "/best-tape-backup-software", "/resources/tape-backup-software/catalogicdpx",
]
SCOPE_SET = set(SCOPE)

INLINE = {"a", "strong", "b", "em", "i", "span", "code", "br", "sup", "sub", "small", "abbr", "time", "mark", "u", "s", "input", "wbr", "img"}
VOID = {"br", "input", "wbr", "img"}
SKIP = {"script", "style", "code", "pre", "svg", "noscript", "template"}
HINT = {"a": "a", "strong": "b", "b": "b", "em": "i", "i": "i", "span": "s", "br": "br", "sup": "sup", "sub": "sub", "small": "sm", "input": "in", "img": "img", "code": "c"}
LD_KEYS = {"name", "text", "headline", "description"}
LD_URL_KEYS = {"item", "url", "mainEntityOfPage"}

# Names that are never translated (brands, products, sellers). Seller names are added from the price data.
DNT = {"TapeBackup", "TapeBackup.org", "LTO Tape Info", "Catalogic DPX", "Veeam", "Commvault", "Nakivo", "Acronis",
       "CloudCasa", "Fujifilm", "Sony", "HPE", "IBM", "Quantum", "Dell", "MagStor", "Symply", "LTFS", "WORM", "Ultrium",
       "ULTRIUM", "LTFS · WORM READY", "TapeBackup LTO Tape Info", "Q&A", "Blog"}

NUM = r"\d(?:[\d,]*\d)?(?:\.\d+)?"
PH_RE = re.compile(
    r"(?:[$€]|zł)\s?" + NUM                                                     # money: $92.45, €81.90, zł368.00
    + r"|(?<![\w])\d+(?:[-/:.]\d+)+(?![\w])"                                   # 3-2-1, 2026-09-17, 2.5:1, 1.44
    + r"|(?<![\w-])(?=[A-Za-z0-9-]*\d)[A-Z][A-Za-z0-9]*(?:-[A-Za-z0-9]+)+"   # LTO-9, AES-256, TD-L92AN-BR
    + r"|(?<![\w-])[A-Z][A-Za-z]+\d[A-Za-z0-9]*"                              # BC040A, TS2260, LTX6000G
    + r"|" + NUM                                                               # 18, 1,000 (units like TB stay text)
)
ENTITY = re.compile(r"&(?:#\d+|#x[0-9a-fA-F]+|\w+);")
TAG_TOKEN = re.compile(r"</?([a-z]+)(\d+)(/?)>")


# ---------------------------------------------------------------- masking

def mask(inner):
    """Masked key, tag table and placeable values for a segment's inner HTML."""
    out, tags, values, stack = [], {}, [], []
    k = 0
    for part in re.split(r"(<[^>]+>)", inner):
        if not part:
            continue
        if part.startswith("<"):
            m = re.match(r"<\s*(/)?\s*([a-zA-Z0-9]+)", part)
            if not m:
                out.append(html.escape(part, quote=False))
                continue
            closing, name = bool(m.group(1)), m.group(2).lower()
            hint = HINT.get(name, "x")
            if closing:
                for i in range(len(stack) - 1, -1, -1):
                    if stack[i][0] == name:
                        _, idx = stack.pop(i)
                        out.append(f"</{hint}{idx}>")
                        tags[(idx, "close")] = part
                        break
                continue
            k += 1
            if name in VOID or part.endswith("/>"):
                out.append(f"<{hint}{k}/>")
                tags[(k, "void")] = part
            else:
                out.append(f"<{hint}{k}>")
                tags[(k, "open")] = part
                stack.append((name, k))
            continue
        # text: keep entities literal, mask digit tokens
        pieces = re.split(f"({ENTITY.pattern})", part)
        for piece in pieces:
            if not piece:
                continue
            if ENTITY.fullmatch(piece):
                out.append(piece)
                continue

            def rep(m):
                values.append(m.group(0))
                return "{" + str(len(values) - 1) + "}"
            out.append(PH_RE.sub(rep, piece))
    key = re.sub(r"\s+", " ", "".join(out)).strip()
    return key, tags, values


def tokens_of(s):
    return sorted(re.findall(r"</?[a-z]+\d+/?>", s)), sorted(re.findall(r"\{\d+\}", s)), sorted(re.findall(r"\{[a-z_]+\}", s))


def valid_translation(key, tgt):
    a, b = tokens_of(key), tokens_of(tgt)
    return a == b


def unmask(tgt, tags, values):
    def tag_rep(m):
        name, idx, void = m.group(1), int(m.group(2)), m.group(3)
        if m.group(0).startswith("</"):
            return tags.get((idx, "close"), "")
        if void:
            return tags.get((idx, "void"), "")
        return tags.get((idx, "open"), "")
    s = TAG_TOKEN.sub(tag_rep, tgt)
    return re.sub(r"\{(\d+)\}", lambda m: values[int(m.group(1))], s)


def has_letters(key):
    stripped = re.sub(r"</?[a-z]+\d+/?>|\{\d+\}|&\w+;", "", key)
    return bool(re.search(r"[A-Za-z]", stripped))


# ---------------------------------------------------------------- number localization

FMT = {
    "de": {"dec": ",", "grp": ".", "after": True, "min_grp": 4},
    "fr": {"dec": ",", "grp": " ", "after": True, "min_grp": 4},
    "it": {"dec": ",", "grp": ".", "after": True, "min_grp": 4},
    "es": {"dec": ",", "grp": ".", "after": True, "min_grp": 5},
    "nl": {"dec": ",", "grp": ".", "after": False, "min_grp": 4},
    "pl": {"dec": ",", "grp": " ", "after": True, "min_grp": 5},
}
NBSP = " "
UNIT_AFTER = re.compile(r"\s+(?:[KMGTPE]i?B|[KMGTP]o|[KMG]B/s|[MG]o/s)\b")
ISO_DATE = re.compile(r"(?<![\w/.:-])((?:19|20)\d\d)-(\d\d)-(\d\d)(?![\w/:-]|\.\d)")
DATE_FMT = {"de": "{d}.{m}.{y}", "fr": "{d}/{m}/{y}", "it": "{d}/{m}/{y}", "es": "{d}/{m}/{y}", "nl": "{d}-{m}-{y}", "pl": "{d}.{m}.{y}"}
LOC_RE = re.compile(
    r"(?P<sym>[$€]|zł)\s?(?P<mnum>\d(?:[\d,]*\d)?(?:\.\d+)?)(?:[-–](?P<mnum2>\d(?:[\d,]*\d)?(?:\.\d+)?)(?![\w.]))?"
    r"|(?<![\w.,/:\-])(?P<num>\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+\.\d+)(?![\d])(?!\.\d)(?![A-Za-z]*\d)"
)


def fmt_number(raw, lang):
    f = FMT[lang]
    intpart, _, dec = raw.replace(",", "").partition(".")
    if len(intpart) >= f["min_grp"]:
        groups = []
        while len(intpart) > 3:
            groups.insert(0, intpart[-3:])
            intpart = intpart[:-3]
        groups.insert(0, intpart)
        intpart = f["grp"].join(groups)
    return intpart + (f["dec"] + dec if dec else "")


def french_spacing(text):
    """Non-breaking spaces French typography expects: before ; : ! ? and inside « »."""
    text = re.sub(r"[ \u00a0\u202f]*([;!?])", "\u202f\\1", text)
    text = re.sub(r"(?<=\w)[ \u00a0]*:(?=\s)", "\u00a0:", text)
    text = re.sub(r"«[ \u00a0]*", "«\u00a0", text)
    return re.sub(r"[ \u00a0]*»", "\u00a0»", text)


def localize_numbers(text, lang):
    if lang == "fr":
        text = french_spacing(text)
    if lang not in FMT or not re.search(r"\d", text):
        return text
    f = FMT[lang]

    def rep(m):
        if (m.group("num") and re.fullmatch(r"\d{1,2}\.\d{1,2}", m.group("num")) and not text[:m.start()].strip()
                and re.match(r"\s+[A-ZÄÖÜÉÈÀÁÍÓÚŁŚŻŹĆŃ]", text[m.end():]) and not UNIT_AFTER.match(text[m.end():])):
            return m.group(0)  # a section number such as "2.1 Criterion"
        if m.group("sym"):
            sym, n = m.group("sym"), fmt_number(m.group("mnum"), lang)
            if m.group("mnum2"):  # "$3,000-4,500": one symbol for the whole range
                n = f"{n}–{fmt_number(m.group('mnum2'), lang)}"
            return f"{n}{NBSP}{sym}" if f["after"] else f"{sym}{NBSP}{n}"
        return fmt_number(m.group("num"), lang)
    text = ISO_DATE.sub(lambda m: DATE_FMT[lang].format(y=m.group(1), m=m.group(2), d=m.group(3)), text)
    out = LOC_RE.sub(rep, text)
    num = r"\d[\d.,  ]*"
    if f["after"]:
        out = re.sub(rf"({num}){NBSP}([$€]|zł)\s?[-–]\s?({num}){NBSP}\2", rf"\1–\3{NBSP}\2", out)
    else:
        out = re.sub(rf"([$€]){NBSP}({num})\s?[-–]\s?\1{NBSP}({num})", rf"\1{NBSP}\2–\3", out)
    return out


# ---------------------------------------------------------------- page segmentation

def skipped(el):
    for p in [el] + list(el.parents):
        if isinstance(p, Tag) and (p.name in SKIP or p.has_attr("data-i18n-skip")):
            return True
    return False


def has_block_descendant(el):
    return any(isinstance(d, Tag) and d.name not in INLINE for d in el.descendants)


def has_text(el):
    return any(isinstance(t, NavigableString) and not isinstance(t, Comment) and t.strip() for t in el.descendants)


def text_elements(body):
    """Elements whose inner HTML is one translation segment."""
    found = []

    def walk(el):
        if not isinstance(el, Tag) or el.name in SKIP or el.has_attr("data-i18n-skip"):
            return
        if not has_block_descendant(el) and has_text(el):
            found.append(el)
            return
        direct = [c for c in el.children if isinstance(c, NavigableString) and not isinstance(c, Comment) and c.strip()]
        if direct:
            # mixed content: wrap each run of text and inline tags so it becomes its own segment
            run = []
            for c in list(el.children):
                if (isinstance(c, NavigableString) and not isinstance(c, Comment)) or (isinstance(c, Tag) and c.name in INLINE and not has_block_descendant(c)):
                    run.append(c)
                    continue
                _wrap(run, found)
                run = []
                walk(c)
            _wrap(run, found)
            return
        for c in list(el.children):
            walk(c)

    def _wrap(run, acc):
        if not any((isinstance(x, NavigableString) and x.strip()) or (isinstance(x, Tag) and has_text(x)) for x in run):
            return
        span = BeautifulSoup("", "html.parser").new_tag("span")
        span["data-i18n-run"] = "1"
        run[0].insert_before(span)
        for x in run:
            span.append(x.extract())
        acc.append(span)

    walk(body)
    return found


def page_segments(soup):
    """(kind, target, key, tags, values, context) for every translatable string on a page."""
    segs = []
    head = soup.head
    if head and head.title and head.title.string:
        k, t, v = mask(html.escape(head.title.string, quote=False))
        segs.append(("title", head.title, k, t, v, "title"))
    for m in soup.find_all("meta"):
        if m.get("name") in ("description", "twitter:title", "twitter:description") or m.get("property") in ("og:title", "og:description"):
            k, t, v = mask(html.escape(m.get("content", ""), quote=False))
            segs.append(("meta", m, k, t, v, "meta " + (m.get("name") or m.get("property"))))
    body = soup.body or soup
    for el in text_elements(body):
        if skipped(el):
            continue
        k, t, v = mask(el.decode_contents())
        segs.append(("html", el, k, t, v, el.name))
    for el in body.find_all(True):
        if skipped(el):
            continue
        for attr in ("aria-label", "alt", "title", "placeholder"):
            if el.has_attr(attr) and el[attr].strip():
                k, t, v = mask(html.escape(el[attr], quote=False))
                segs.append(("attr", (el, attr), k, t, v, f"{el.name}@{attr}"))
    for sc in soup.find_all("script", type="application/ld+json"):
        data = json.loads(sc.string or "{}")
        for path, s in _ld_strings(data):
            k, t, v = mask(html.escape(s, quote=False))
            segs.append(("ld", (sc, path), k, t, v, "json-ld " + path[-1]))
    for sc in soup.find_all("script", attrs={"data-i18n": True}):
        data = json.loads(sc.string or "{}")
        for key, s in data.items():
            k, t, v = mask(s)
            segs.append(("js", (sc, key), k, t, v, "script text"))
    return segs


def _ld_strings(node, path=()):
    if isinstance(node, dict):
        for k, v in node.items():
            if isinstance(v, str) and k in LD_KEYS:
                yield path + (k,), v
            elif isinstance(v, (dict, list)):
                yield from _ld_strings(v, path + (k,))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from _ld_strings(v, path + (i,))


UNIT_WORDS = {"TB", "GB", "MB", "KB", "EB", "PB", "MB/s", "GB/s", "TB/h", "x", "yr"}


def translatable(key, dnt):
    if not has_letters(key):
        return False
    bare = re.sub(r"\s+", " ", re.sub(r"</?[a-z]+\d+/?>", " ", key)).strip()
    if bare in dnt or bare.replace("&amp;", "&") in dnt:
        return False
    words = re.sub(r"\{\d+\}|[^\w/ ]", " ", bare).split()
    return not (words and all(w in UNIT_WORDS for w in words))


# ---------------------------------------------------------------- links and head

def lang_url(path, lang):
    if lang == "en":
        return SITE + ("/" if path == "/" else path)
    return f"{SITE}/{lang}" + ("" if path == "/" else path)


def rewrite_href(href, lang):
    if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
        return href
    absolute = href.startswith(SITE)
    rel = href[len(SITE):] if absolute else href
    if not rel.startswith("/") or rel.startswith("//"):
        return href
    path, frag = (rel.split("#", 1) + [""])[:2]
    path = path.rstrip("/") or "/"
    if path not in SCOPE_SET:
        return href
    new = f"/{lang}" + ("" if path == "/" else path) + (f"#{frag}" if frag else "")
    return (SITE + new) if absolute else new


def switcher_html(path, current, langs):
    items = []
    for code in ["en"] + langs:
        label = code.upper()
        href = ("/" if path == "/" else path) if code == "en" else (f"/{code}" + ("" if path == "/" else path))
        if path not in SCOPE_SET:
            href = "/" if code == "en" else f"/{code}"
        cls = ' class="on" aria-current="page"' if code == current else ""
        items.append(f'<a href="{href}" hreflang="{code}" lang="{code}"{cls}>{label}</a>')
    return f'<span class="lang-switch" data-i18n-skip aria-label="Language">{"".join(items)}</span>'


def set_head(soup, path, lang, langs, indexable=True):
    root = soup.html
    root["lang"] = lang
    head = soup.head
    for link in head.find_all("link", rel="alternate"):
        if link.get("hreflang"):
            link.decompose()
    canonical = head.find("link", rel="canonical")
    if canonical:
        canonical["href"] = lang_url(path, lang)
    for m in head.find_all("meta", property="og:url"):
        m["content"] = lang_url(path, lang)
    for m in head.find_all("meta", property=re.compile(r"^og:locale")):
        m.decompose()
    loc = soup.new_tag("meta", property="og:locale", content=LANG_META[lang]["locale"])
    head.append(loc)
    if path in SCOPE_SET:
        for code in ["en"] + langs:
            head.append(soup.new_tag("link", rel="alternate", hreflang=code, href=lang_url(path, code)))
        head.append(soup.new_tag("link", rel="alternate", hreflang="x-default", href=lang_url(path, "en")))
    robots = head.find("meta", attrs={"name": "robots"})
    if robots and lang != "en" and not indexable:
        robots["content"] = "noindex, follow"


def add_switcher(soup, path, lang, langs):
    for old in soup.select(".lang-switch"):
        old.decompose()
    bar = soup.select_one(".topbar .wrap")
    if bar:
        bar.append(BeautifulSoup(switcher_html(path, lang, langs), "html.parser"))


# ---------------------------------------------------------------- rendering

def load_tm(lang):
    """Translation memory for a language: tm/<lang>.json plus any tm/<lang>.<part>.json batch files."""
    tm = {}
    folder = os.path.join(I18N, "tm")
    if not os.path.isdir(folder):
        return tm
    for name in sorted(os.listdir(folder)):
        if name == f"{lang}.json" or (name.startswith(f"{lang}.") and name.endswith(".json")):
            with open(os.path.join(folder, name), encoding="utf-8") as f:
                tm.update(json.load(f))
    return tm


def load_langs():
    p = os.path.join(I18N, "languages.json")
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def staged_file(lang, path):
    return os.path.join(STAGE, lang, "index.html" if path == "/" else path.lstrip("/") + "/index.html")


def out_file(lang, path):
    return os.path.join(ROOT, lang, "index.html" if path == "/" else path.lstrip("/") + "/index.html")


def render_page(src_html, path, lang, tm, dnt, langs, indexable, stats):
    soup = BeautifulSoup(src_html, "html.parser")
    segs = page_segments(soup)
    ld_data = {}
    js_data = {}
    for kind, target, key, tags, values, ctx in segs:
        raw = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", unmask(key, tags, values)))).strip()
        if not translatable(key, dnt) or raw in dnt:
            tgt = key
        else:
            stats["total"] += 1
            tgt = tm.get(key)
            if tgt is None or not valid_translation(key, tgt):
                stats["missing_n"] += 1
                stats["missing"].setdefault(key, {"ctx": set(), "pages": set(), "example": ""})
                stats["missing"][key]["ctx"].add(ctx)
                stats["missing"][key]["pages"].add(path)
                stats["missing"][key]["example"] = stats["missing"][key]["example"] or re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", unmask(key, tags, values)))).strip()
                tgt = key
        out = unmask(tgt, tags, values)
        if kind == "title":
            target.string = localize_numbers(html.unescape(out), lang)
        elif kind == "meta":
            target["content"] = localize_numbers(html.unescape(out), lang)
        elif kind == "html":
            frag = BeautifulSoup(out, "html.parser")
            target.clear()
            for node in list(frag.contents):
                target.append(node)
            if target.get("data-i18n-run"):
                target.unwrap()
        elif kind == "attr":
            el, attr = target
            el[attr] = localize_numbers(html.unescape(out), lang)
        elif kind == "ld":
            sc, p = target
            data = ld_data.setdefault(id(sc), (sc, json.loads(sc.string)))[1]
            node = data
            for step in p[:-1]:
                node = node[step]
            node[p[-1]] = localize_numbers(html.unescape(out), lang)
        elif kind == "js":
            sc, k = target
            data = js_data.setdefault(id(sc), (sc, json.loads(sc.string)))[1]
            data[k] = localize_numbers(out, lang)
    for sc, data in ld_data.values():
        _ld_links(data, lang)
        if isinstance(data, dict) and data.get("@type") in ("Article", "WebApplication", "FAQPage", "BreadcrumbList"):
            data["inLanguage"] = lang
        sc.string = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    for sc in soup.find_all("script", type="application/ld+json"):
        if id(sc) not in ld_data:
            data = json.loads(sc.string or "{}")
            _ld_links(data, lang)
            sc.string = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    for sc, data in js_data.values():
        sc.string = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    body = soup.body or soup
    for t in list(body.find_all(string=True)):
        if isinstance(t, Comment) or skipped(t.parent) or not (re.search(r"\d", t) or (lang == "fr" and re.search(r"[;:!?«»]", t))):
            continue
        t.replace_with(localize_numbers(str(t), lang))
    for h in soup.find_all(["h1", "h2"]):
        for t in list(h.find_all(string=True)):
            if "LTO-" in t:
                t.replace_with(re.sub(r"LTO-(\d+)", "LTO\u2011\\1", str(t)))  # keep "LTO-10" on one line
    for a in soup.find_all("a", href=True):
        a["href"] = rewrite_href(a["href"], lang)
    set_head(soup, path, lang, langs, indexable)
    add_switcher(soup, path, lang, langs)
    return str(soup)


def _ld_links(node, lang):
    if isinstance(node, dict):
        for k, v in list(node.items()):
            if k in LD_URL_KEYS and isinstance(v, str):
                node[k] = rewrite_href(v, lang)
            else:
                _ld_links(v, lang)
    elif isinstance(node, list):
        for v in node:
            _ld_links(v, lang)


def seller_names():
    names = set()
    for f in [os.path.join(ROOT, "data", "prices-2026-09.json")] + [os.path.join(ROOT, "data", "eu", x) for x in os.listdir(os.path.join(ROOT, "data", "eu")) if x.startswith("prices-")]:
        if not os.path.exists(f):
            continue
        data = json.load(open(f, encoding="utf-8"))
        for g in data.get("generations", {}).values():
            for item in g.values():
                if isinstance(item, dict):
                    for d in item.get("datapoints", []):
                        names.add(d.get("seller", ""))
                        names.add(re.sub(r"^\d+__", "", (d.get("sku") or "").strip()))
    return {n for n in names if n}


def render_language(lang, langs_published):
    cfg = load_langs()[lang]
    tm = load_tm(lang)
    dnt = DNT | seller_names()
    stats = {"total": 0, "missing": {}, "missing_n": 0}
    written = []
    for path in SCOPE:
        src = staged_file(lang, path)
        if not os.path.exists(src):
            continue
        with open(src, encoding="utf-8") as f:
            out = render_page(f.read(), path, lang, tm, dnt, langs_published, cfg.get("indexable", False), stats)
        dst = out_file(lang, path)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, "w", encoding="utf-8") as f:
            f.write(out)
        written.append(path)
    missing = stats["missing"]
    seg_file = os.path.join(I18N, "segments", f"{lang}.json")
    os.makedirs(os.path.dirname(seg_file), exist_ok=True)
    rows = [{"key": k, "ctx": sorted(v["ctx"]), "pages": sorted(v["pages"]), "example": v["example"]} for k, v in missing.items()]
    with open(seg_file, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)
    return written, stats["total"], stats["missing_n"]


def add_alternates_to_english(langs_published):
    """English in-scope pages point at their published translations and get the language switch."""
    if not langs_published:
        return
    for path in SCOPE:
        f = os.path.join(ROOT, "index.html" if path == "/" else path.lstrip("/") + "/index.html")
        if not os.path.exists(f):
            continue
        soup = BeautifulSoup(open(f, encoding="utf-8").read(), "html.parser")
        set_head(soup, path, "en", langs_published)
        add_switcher(soup, path, "en", langs_published)
        open(f, "w", encoding="utf-8").write(str(soup))


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "status":
        for lang in LANGS:
            p = os.path.join(I18N, "segments", f"{lang}.json")
            n = len(json.load(open(p))) if os.path.exists(p) else "?"
            print(f"{lang}: {len(load_tm(lang))} translated segments, {n} missing")
    elif cmd == "missing":
        lang = sys.argv[2]
        print(open(os.path.join(I18N, "segments", f"{lang}.json"), encoding="utf-8").read())


if __name__ == "__main__":
    main()
