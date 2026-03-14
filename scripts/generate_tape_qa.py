from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass
from datetime import date
from html import escape, unescape
from pathlib import Path
from typing import Iterable


ROOT = Path("/private/tmp/tapebackup-static-project")
DOWNLOADS = Path("/Users/dali/Downloads/download")
TODAY = date.today().isoformat()
SITE = "https://tapebackup.org"

EXISTING_ORDER = [
    "resilient-data-protection-architecture",
    "hybrid-cloud-object-storage",
    "collaborative-video-production-archive",
    "multi-tier-data-protection-strategy",
    "mainframe-open-systems-archive",
    "ai-media-workflow-automation",
    "ai-analytics-storage-at-scale",
    "modern-data-infrastructure-for-ai",
    "modern-backup-infrastructure",
]


@dataclass
class Entry:
    slug: str
    question: str
    answer_paragraphs: list[str]
    theme: str
    deck: str
    source_order: int

    @property
    def word_count(self) -> int:
        return len(" ".join(self.answer_paragraphs).split())


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", unescape(value)).strip()


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return re.sub(r"-{2,}", "-", slug)


def strip_markdown(value: str) -> str:
    text = re.sub(r"[*_`#>]+", "", value)
    text = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text)
    return clean_text(text)


def truncate(value: str, limit: int) -> str:
    value = clean_text(value)
    if len(value) <= limit:
        return value
    shortened = value[: limit - 3].rstrip()
    if " " in shortened:
        shortened = shortened.rsplit(" ", 1)[0]
    return shortened + "..."


def first_sentence(paragraphs: Iterable[str]) -> str:
    joined = " ".join(clean_text(p) for p in paragraphs)
    match = re.search(r"^(.+?[.!?])(?:\s|$)", joined)
    sentence = match.group(1) if match else joined
    return truncate(sentence, 145)


def detect_theme(question: str, answer: str) -> str:
    question_lower = question.lower()
    haystack = f"{question} {answer}".lower()
    if any(word in haystack for word in ["webinar", "webinars", "on-demand"]):
        return "Knowledge resources"
    if any(word in haystack for word in ["meeting", "request", "outreach", "submit", "submitting", "contact"]):
        return "Buyer journey"
    if any(word in question_lower for word in ["4k", "video", "editing", "editor", "nvme", "media asset", "production workflow"]):
        return "Media workflows"
    if any(word in question_lower for word in ["archive", "archives", "archival", "retention", "library", "libraries"]):
        return "Archive strategy"
    if any(word in haystack for word in ["4k", "video", "media", "editor", "editing", "nvme", "asset management"]):
        return "Media workflows"
    if any(word in haystack for word in ["backup", "ransomware", "recovery", "data protection"]):
        return "Data protection"
    if any(word in haystack for word in ["cloud", "object storage", "data center"]):
        return "Hybrid cloud"
    if any(word in haystack for word in ["ai", "machine learning", "analytics", "gpu"]):
        return "AI infrastructure"
    return "LTO strategy"


def parse_existing_entry(slug: str, index: int) -> Entry:
    path = ROOT / "tape-q-and-a" / slug / "index.html"
    text = path.read_text()
    theme = clean_text(re.search(r'<p class="eyebrow">(.*?)</p>', text, re.S).group(1))
    question = clean_text(re.search(r"<h1>(.*?)</h1>", text, re.S).group(1))
    deck = clean_text(re.search(r'<p class="lead">(.*?)</p>', text, re.S).group(1))
    answer_block = re.search(r'<div class="answer-copy">(.*?)</div>', text, re.S).group(1)
    answer_paragraphs = [clean_text(p) for p in re.findall(r"<p>(.*?)</p>", answer_block, re.S)]
    return Entry(slug=slug, question=question, answer_paragraphs=answer_paragraphs, theme=theme, deck=deck, source_order=index)


def parse_markdown_entry(path: Path, index: int) -> Entry | None:
    lines = path.read_text().replace("\r\n", "\n").splitlines()
    question_lines: list[str] = []
    answer_lines: list[str] = []
    section = None
    saw_content = False
    for raw_line in lines:
        plain = strip_markdown(raw_line)
        lower = plain.lower()
        if lower in {"q", "question"} or lower.startswith("question"):
            section = "question"
            continue
        if lower == "a" or lower.startswith("answer"):
            section = "answer"
            continue
        if lower == "faq" or lower.startswith("faq"):
            break
        if not plain:
            if section == "question" and question_lines and question_lines[-1] != "":
                question_lines.append("")
            if section == "answer" and answer_lines and answer_lines[-1] != "":
                answer_lines.append("")
            continue
        saw_content = True
        if section == "question":
            question_lines.append(plain)
        elif section == "answer":
            answer_lines.append(plain)
    if not saw_content:
        return None
    question = clean_text(" ".join(line for line in question_lines if line))
    paragraph_chunks = re.split(r"\n\s*\n", "\n".join(answer_lines).strip())
    answer_paragraphs = [clean_text(chunk) for chunk in paragraph_chunks if clean_text(chunk)]
    if not question or not answer_paragraphs:
        return None
    answer_text = " ".join(answer_paragraphs)
    return Entry(
        slug=slugify(question),
        question=question,
        answer_paragraphs=answer_paragraphs,
        theme=detect_theme(question, answer_text),
        deck=first_sentence(answer_paragraphs),
        source_order=index,
    )


def q_label(number: int) -> str:
    return f"Q {number:02d}"


def answer_minutes(entry: Entry) -> str:
    minutes = max(1, round(entry.word_count / 220))
    return f"{minutes} min"


def nav_item(entry: Entry, number: int, current_slug: str | None = None) -> str:
    current = " current" if current_slug == entry.slug else ""
    title = truncate(entry.question, 88)
    return (
        f'                <a class="detail-link{current}" href="/tape-q-and-a/{entry.slug}">\n'
        f'                  <div class="card-meta"><span class="q-pill">{q_label(number)}</span>'
        f'<span class="theme-chip">{escape(entry.theme)}</span></div>\n'
        f'                  <strong>{escape(title)}</strong>\n'
        f"                </a>"
    )


def hub_nav_item(entry: Entry, number: int) -> str:
    title = truncate(entry.question, 82)
    return (
        f'              <a class="nav-item" href="/tape-q-and-a/{entry.slug}">\n'
        f'                <div class="nav-meta"><span class="q-pill">{q_label(number)}</span>'
        f'<span class="theme-chip">{escape(entry.theme)}</span></div>\n'
        f'                <strong class="nav-title">{escape(title)}</strong>\n'
        f"              </a>"
    )


def hub_card(entry: Entry, number: int, featured: bool = False) -> str:
    featured_class = " featured" if featured else ""
    side = ""
    if featured:
        side = """
              <div class="card-side visual-side">
                <div class="card-meta"><span class="meta-chip">1 min</span><span class="theme-chip">{theme}</span></div>
                <p class="visual-note">Offline media gives backup strategy a visible shape: generations, cartridges, rotation, and real-world isolation.</p>
                <div class="cassette-strip compact" aria-hidden="true">
                  <span class="cassette cassette-10"><span class="cassette-label">10</span></span>
                  <span class="cassette cassette-8"><span class="cassette-label">8</span></span>
                  <span class="cassette cassette-7"><span class="cassette-label">7</span></span>
                  <span class="cassette cassette-6"><span class="cassette-label">6</span></span>
                  <span class="cassette cassette-5"><span class="cassette-label">5</span></span>
                </div>
              </div>""".format(theme=escape(entry.theme))
    return (
        f'            <a class="qa-card{featured_class}" href="/tape-q-and-a/{entry.slug}">\n'
        f'              <div class="card-copy">\n'
        f'                <div class="card-meta"><span class="q-pill">{q_label(number)}</span>'
        f'<span class="theme-chip">{escape(entry.theme)}</span><span class="meta-chip">{entry.word_count} words</span></div>\n'
        f'                <h3 class="card-title">{escape(entry.question)}</h3>\n'
        f'                <p class="deck">{escape(entry.deck)}</p>\n'
        f'                <span class="card-cta">Open question page</span>\n'
        f'              </div>\n'
        f"{side}\n"
        f"            </a>"
    )


def related_card(entry: Entry, number: int) -> str:
    title = truncate(entry.question, 86)
    return (
        f'                <a class="related-card" href="/tape-q-and-a/{entry.slug}">\n'
        f'                  <div class="card-meta"><span class="q-pill">{q_label(number)}</span><span class="theme-chip">{escape(entry.theme)}</span></div>\n'
        f'                  <h3>{escape(title)}</h3>\n'
        f'                  <p>{escape(entry.deck)}</p>\n'
        f"                </a>"
    )


def pager_cell(label: str, entry: Entry, number: int) -> str:
    title = truncate(entry.question, 96)
    return (
        f'<a href="/tape-q-and-a/{entry.slug}"><span>{escape(label)}</span>'
        f'<strong>{escape(q_label(number) + " - " + title)}</strong></a>'
    )


def render_hub(entries: list[Entry]) -> str:
    count = len(entries)
    new_count = count - len(EXISTING_ORDER)
    nav = "\n".join(hub_nav_item(entry, idx + 1) for idx, entry in enumerate(entries))
    cards = "\n".join(hub_card(entry, idx + 1, featured=(idx == 0)) for idx, entry in enumerate(entries))
    description = "LTO Tape questions and answers covering backup, archive, media workflows, storage infrastructure, and long-term retention."
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Tape Q&amp;A | TapeBackup.org</title>
    <meta name="description" content="{escape(description)}" />
    <meta name="robots" content="index, follow" />
    <link rel="canonical" href="{SITE}/tape-q-and-a" />
    <meta property="og:type" content="website" />
    <meta property="og:title" content="Tape Q&amp;A | TapeBackup.org" />
    <meta property="og:description" content="{escape(description)}" />
    <meta property="og:url" content="{SITE}/tape-q-and-a" />
    <meta property="og:image" content="{SITE}/og-image.png" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="Tape Q&amp;A | TapeBackup.org" />
    <meta name="twitter:description" content="{escape(description)}" />
    <meta name="twitter:image" content="{SITE}/og-image.png" />
    <meta name="theme-color" content="#183976" />
    <link rel="icon" href="/favicon.png" type="image/png" />
    <link rel="stylesheet" href="/tape-q-and-a.css" />
    <script type="application/ld+json">{json.dumps({"@context": "https://schema.org", "@type": "CollectionPage", "name": "Tape Q&A", "url": f"{SITE}/tape-q-and-a", "description": description}, ensure_ascii=False)}</script>
  </head>
  <body>

    <div class="site-shell">
      <header class="topbar">
        <div class="container topbar-inner">
          <a class="brand" href="/home">
            <img src="/assets/logo-BdaQDFFQ.png" alt="TapeBackup logo" />
            <span class="brand-copy"><strong>LTO Tape Info</strong><span>Tape Q&amp;A atlas</span></span>
          </a>
          <nav class="topnav" aria-label="Primary"><a href="/home">Home</a>
          <a href="/why-tape">Why Tape</a>
          <a href="/resources">Resources</a>
          <a href="/blog">Blog</a>
          <a href="/tape-q-and-a" class="current">Q&amp;A</a>
          <a href="/contact">Contact</a>
          </nav>
        </div>
      </header>

      <section class="hero">
        <div class="container hero-grid">
          <div class="hero-copy">
            <p class="eyebrow">Tape knowledge atlas</p>
            <h1>LTO Tape FAQs</h1>
            <p>LTO Tape questions and answers collected in one place, covering the most frequent topics around backup, archive, compatibility, recovery, media workflows, and long-term storage.</p>
            <div class="signal-row">
              <span class="signal-chip">{count} dedicated pages</span>
              <span class="signal-chip">{new_count} new additions</span>
              <span class="signal-chip">Built for search and sharing</span>
            </div>
          </div>
          <aside class="hero-panel">
            <p class="panel-label">Section brief</p>
            <p class="panel-copy">This hub now brings together {count} standalone answers across backup strategy, media workflows, archive planning, storage education, and buyer questions so visitors can move from broad research to a single detailed answer quickly.</p>
            <div class="metrics">
              <div class="metric"><strong>{count}</strong><span>Standalone answers</span></div>
              <div class="metric"><strong>{new_count}</strong><span>New topics added</span></div>
              <div class="metric"><strong>250</strong><span>Words per answer</span></div>
            </div>
          </aside>
        </div>
      </section>

      <main class="page">
        <div class="container intro-band">
          <header class="section-head">
            <p class="eyebrow">Reading structure</p>
            <h2>Browse the atlas first, then open the question that matters.</h2>
            <p>The hub is organized as one guided reading surface: a compact orientation, a fast navigator for the full library, and detailed question cards that can be opened as standalone landing pages.</p>
          </header>
          <aside class="intro-visual" aria-label="LTO tape visuals">
            <figure class="photo-card">
              <img src="/assets/hero-tape-backup-n4hgCCaQ.jpg" alt="LTO tape backup hardware and cartridges" />
              <figcaption class="photo-caption">LTO tape is physical, readable, and easy to map to backup generations and retention workflows.</figcaption>
            </figure>
            <section class="compat-card">
              <p class="panel-label">LTO compatibility feel</p>
              <div class="cassette-strip" aria-hidden="true">
                <span class="cassette cassette-10"><span class="cassette-label">10</span></span>
                <span class="cassette cassette-8"><span class="cassette-label">8</span></span>
                <span class="cassette cassette-7"><span class="cassette-label">7</span></span>
                <span class="cassette cassette-6"><span class="cassette-label">6</span></span>
                <span class="cassette cassette-5"><span class="cassette-label">5</span></span>
                <span class="cassette cassette-4"><span class="cassette-label">4</span></span>
                <span class="cassette cassette-3"><span class="cassette-label">3</span></span>
                <span class="cassette cassette-2"><span class="cassette-label">2</span></span>
                <span class="cassette cassette-1"><span class="cassette-label">1</span></span>
              </div>
            </section>
          </aside>
        </div>

        <div class="container hub-layout">
          <aside class="navigator">
            <p class="eyebrow">Navigator</p>
            <h2>Browse the library</h2>
            <p>Start anywhere. The rail keeps every question one click away, while the main canvas highlights the strongest entry points.</p>
            <nav class="nav-list" aria-label="Q&amp;A navigator">
{nav}
            </nav>
          </aside>

          <section class="hub-main" aria-label="Tape Q&amp;A cards">
            <div class="card-grid">
{cards}
            </div>
          </section>
        </div>
      </main>

      <footer class="footer">
        <div class="container footer-inner">
          <span>TapeBackup.org Q&amp;A atlas</span>
          <nav class="footer-links" aria-label="Footer">
            <a href="/home">Home</a>
            <a href="/blog">Blog</a>
            <a href="/resources">Resources</a>
            <a href="/contact">Contact</a>
          </nav>
        </div>
      </footer>
    </div>

  </body>
</html>
"""


def render_detail(entries: list[Entry], idx: int) -> str:
    entry = entries[idx]
    prev_entry = entries[idx - 1] if idx > 0 else None
    next_entry = entries[idx + 1] if idx + 1 < len(entries) else None
    related = [entries[(idx + offset) % len(entries)] for offset in range(1, 4)]
    rail = "\n".join(nav_item(item, pos + 1, current_slug=entry.slug) for pos, item in enumerate(entries))
    related_html = "\n".join(related_card(item, entries.index(item) + 1) for item in related)
    pager_left = pager_cell("Previous", prev_entry, idx) if prev_entry else "<div></div>"
    pager_right = pager_cell("Next", next_entry, idx + 2) if next_entry else "<div></div>"
    answer_html = "\n".join(f"<p>{escape(paragraph)}</p>" for paragraph in entry.answer_paragraphs)
    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": entry.question,
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": " ".join(entry.answer_paragraphs),
                },
            }
        ],
    }
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{escape(q_label(idx + 1))} | Tape Q&amp;A | TapeBackup.org</title>
    <meta name="description" content="{escape(entry.deck)}" />
    <meta name="robots" content="index, follow" />
    <link rel="canonical" href="{SITE}/tape-q-and-a/{entry.slug}" />
    <meta property="og:type" content="website" />
    <meta property="og:title" content="{escape(entry.question)}" />
    <meta property="og:description" content="{escape(entry.deck)}" />
    <meta property="og:url" content="{SITE}/tape-q-and-a/{entry.slug}" />
    <meta property="og:image" content="{SITE}/og-image.png" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{escape(entry.question)}" />
    <meta name="twitter:description" content="{escape(entry.deck)}" />
    <meta name="twitter:image" content="{SITE}/og-image.png" />
    <meta name="theme-color" content="#183976" />
    <link rel="icon" href="/favicon.png" type="image/png" />
    <link rel="stylesheet" href="/tape-q-and-a.css" />
    <script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>
  </head>
  <body>

    <div class="site-shell">
      <header class="topbar">
        <div class="container topbar-inner">
          <a class="brand" href="/home">
            <img src="/assets/logo-BdaQDFFQ.png" alt="TapeBackup logo" />
            <span class="brand-copy"><strong>LTO Tape Info</strong><span>Tape Q&amp;A atlas</span></span>
          </a>
          <nav class="topnav" aria-label="Primary"><a href="/home">Home</a>
          <a href="/why-tape">Why Tape</a>
          <a href="/resources">Resources</a>
          <a href="/blog">Blog</a>
          <a href="/tape-q-and-a" class="current">Q&amp;A</a>
          <a href="/contact">Contact</a>
          </nav>
        </div>
      </header>

      <section class="hero detail-hero">
        <div class="container hero-grid">
          <div class="hero-copy">
            <p class="eyebrow">{escape(entry.theme)}</p>
            <h1>{escape(entry.question)}</h1>
            <p>{escape(entry.deck)}</p>
            <div class="signal-row">
              <span class="signal-chip">{q_label(idx + 1)}</span>
              <span class="signal-chip">{entry.word_count} words</span>
              <span class="signal-chip">~{answer_minutes(entry)} answer</span>
            </div>
          </div>
          <aside class="hero-panel">
            <p class="panel-label">Reader note</p>
            <p class="panel-copy">This page is built as a standalone answer with its own metadata, related links, and a question rail, so it works equally well as a landing page or part of the wider Q&amp;A sequence.</p>
          </aside>
        </div>
      </section>

      <main class="page">
        <div class="container article-layout">
          <article class="article-card">
            <div class="breadcrumbs"><a href="/home">Home</a><span>/</span><a href="/tape-q-and-a">Tape Q&amp;A</a><span>/</span><span>{q_label(idx + 1)}</span></div>
            <header class="article-header">
              <div class="detail-meta"><span class="q-pill">{q_label(idx + 1)}</span><span class="theme-chip">{escape(entry.theme)}</span><span class="meta-chip">Standalone page</span></div>
              <h2 class="detail-title">{escape(entry.question)}</h2>
              <p class="lead">{escape(entry.deck)}</p>
            </header>

            <section class="answer-shell" aria-label="Answer">
              <span class="answer-badge">A</span>
              <div class="answer-copy">{answer_html}</div>
            </section>

            <div class="pager">{pager_left}{pager_right}</div>

            <section class="related-section" aria-labelledby="related-heading">
              <h2 class="related-heading" id="related-heading">Keep exploring</h2>
              <div class="related-grid">
{related_html}
              </div>
            </section>
          </article>

          <aside class="detail-sidebar">
            <section class="sidebar-block sidebar-visual">
              <p class="panel-label">LTO visual</p>
              <div class="cassette-strip compact" aria-hidden="true">
                <span class="cassette cassette-10"><span class="cassette-label">10</span></span>
                <span class="cassette cassette-8"><span class="cassette-label">8</span></span>
                <span class="cassette cassette-7"><span class="cassette-label">7</span></span>
                <span class="cassette cassette-6"><span class="cassette-label">6</span></span>
                <span class="cassette cassette-5"><span class="cassette-label">5</span></span>
              </div>
              <p class="sidebar-copy">LTO media gives the topic a physical shape: cartridges, generations, compatibility, and real offline separation.</p>
            </section>
            <section class="sidebar-block">
              <h2 class="sidebar-title">Question rail</h2>
              <p class="sidebar-copy">Use the rail to move through the full set without losing the design or the reading context.</p>
              <nav class="detail-list" aria-label="Question list">
{rail}
              </nav>
            </section>
            <section class="sidebar-block">
              <h2 class="sidebar-title">This page at a glance</h2>
              <ul class="note-list">
                <li>Theme: {escape(entry.theme)}</li>
                <li>Answer length: about {entry.word_count} words</li>
                <li>Format: one question, one dedicated answer page</li>
              </ul>
            </section>
          </aside>
        </div>
      </main>

      <footer class="footer">
        <div class="container footer-inner">
          <span>TapeBackup.org Q&amp;A atlas</span>
          <nav class="footer-links" aria-label="Footer">
            <a href="/tape-q-and-a">Q&amp;A hub</a>
            <a href="/blog">Blog</a>
            <a href="/resources">Resources</a>
            <a href="/contact">Contact</a>
          </nav>
        </div>
      </footer>
    </div>

  </body>
</html>
"""


def update_sitemap(entries: list[Entry]) -> None:
    path = ROOT / "sitemap.xml"
    text = path.read_text()
    lines = [
        "  <!-- Tape Q&A -->",
        "  <url>",
        f"    <loc>{SITE}/tape-q-and-a</loc>",
        f"    <lastmod>{TODAY}</lastmod>",
        "    <changefreq>weekly</changefreq>",
        "    <priority>0.7</priority>",
        f'    <xhtml:link rel="alternate" hreflang="en" href="{SITE}/tape-q-and-a"/>',
        f'    <xhtml:link rel="alternate" hreflang="de" href="{SITE}/tape-q-and-a"/>',
        f'    <xhtml:link rel="alternate" hreflang="pl" href="{SITE}/tape-q-and-a"/>',
        "  </url>",
        "",
    ]
    for entry in entries:
        lines.extend(
            [
                "  <url>",
                f"    <loc>{SITE}/tape-q-and-a/{entry.slug}</loc>",
                f"    <lastmod>{TODAY}</lastmod>",
                "    <changefreq>monthly</changefreq>",
                "    <priority>0.6</priority>",
                f'    <xhtml:link rel="alternate" hreflang="en" href="{SITE}/tape-q-and-a/{entry.slug}"/>',
                "  </url>",
                "",
            ]
        )
    block = "\n".join(lines).rstrip()
    updated = re.sub(
        r"  <!-- Tape Q&A -->.*?(?=  <!-- Blog / Knowledge Center -->)",
        block + "\n\n",
        text,
        flags=re.S,
    )
    path.write_text(updated)


def write_site(entries: list[Entry]) -> None:
    (ROOT / "tape-q-and-a.html").write_text(render_hub(entries))
    qa_root = ROOT / "tape-q-and-a"
    expected = {entry.slug for entry in entries}
    for child in qa_root.iterdir():
        if child.is_dir() and child.name not in expected:
            shutil.rmtree(child)
    for idx, entry in enumerate(entries):
        detail_dir = qa_root / entry.slug
        detail_dir.mkdir(parents=True, exist_ok=True)
        (detail_dir / "index.html").write_text(render_detail(entries, idx))
    update_sitemap(entries)


def build_entries() -> list[Entry]:
    entries = [parse_existing_entry(slug, idx) for idx, slug in enumerate(EXISTING_ORDER)]
    seen = {entry.question.lower() for entry in entries}
    md_files = [
        path
        for path in sorted(DOWNLOADS.glob("q*.md"))
        if re.fullmatch(r"q(?: \(\d+\))?\.md", path.name)
    ]
    next_order = len(entries)
    for path in md_files:
        entry = parse_markdown_entry(path, next_order)
        if not entry:
            continue
        key = entry.question.lower()
        if key in seen:
            continue
        seen.add(key)
        entries.append(entry)
        next_order += 1
    return entries


def main() -> None:
    entries = build_entries()
    write_site(entries)
    print(f"Generated {len(entries)} Q&A pages.")


if __name__ == "__main__":
    main()
