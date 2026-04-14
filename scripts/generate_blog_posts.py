from __future__ import annotations

import html
import json
import random
import re
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path


ROOT = Path("/Users/dali/Documents/tapebackup")
SITE = "https://tapebackup.org"
TODAY = date(2026, 4, 14)
RANDOM_SEED = 20260414
NEW_POST_RANGE_START = date(2026, 3, 1)
NEW_POST_RANGE_END = date(2026, 4, 13)

NEW_SOURCES = [
    Path("/Users/dali/Downloads/download/one-bad-archive-and-it-s-gone-forever-the-brutal-trade-off-nobody-warns-you-about-in-tape-storag.md"),
    Path("/Users/dali/Downloads/download/i-replaced-hard-drives-with-tape-and-accidentally-signed-up-for-a-lifetime-of-noise-bugs-and-obs.md"),
    Path("/Users/dali/Downloads/download/500-dreams-and-magnetic-tape-fantasies-the-addictive-illusion-of-cheap-lto-storage.md"),
    Path("/Users/dali/Downloads/download/6-000-for-a-paperweight-when-enterprise-grade-storage-quietly-fails-you.md"),
    Path("/Users/dali/Downloads/download/i-built-it-because-nothing-else-worked-the-raw-messy-reality-of-reinventing-tape-backup-software.md"),
    Path("/Users/dali/Downloads/download/the-day-my-tape-drive-went-rogue-inside-the-frustrating-reality-of-lto-6-failures.md"),
]


@dataclass
class Post:
    slug: str
    title: str
    description: str
    category: str
    published: date
    minutes: int
    body_html: str


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return re.sub(r"-{2,}", "-", slug)


def reading_minutes(text: str) -> int:
    return max(1, round(len(text.split()) / 220))


def summarize_paragraph(text: str) -> str:
    summary = clean_text(text)
    if len(summary) <= 170:
        return summary
    shortened = summary[:167].rstrip()
    if " " in shortened:
        shortened = shortened.rsplit(" ", 1)[0]
    return shortened + "..."


def format_display_date(value: date) -> str:
    return f"{value.strftime('%B')} {value.day}, {value.year}"


def normalize_title(raw: str) -> str:
    value = raw.strip()
    if value.startswith("**") and value.endswith("**"):
        value = value[2:-2].strip()
    value = value.strip()
    if value.startswith('"') and value.endswith('"'):
        value = value[1:-1]
    if value.startswith("“") and value.endswith("”"):
        value = value[1:-1]
    return clean_text(value)


def detect_category(title: str, body: str) -> str:
    haystack = f"{title} {body}".lower()
    if any(term in haystack for term in ["lto-6", "lto-7", "drive", "sas", "hardware", "paperweight", "failure", "crc errors"]):
        return "Technology"
    if any(term in haystack for term in ["software", "ltfs", "fossilsafe", "tar", "workflow", "linux", "self-describing"]):
        return "Guide"
    if any(term in haystack for term in ["cheap", "cost", "price", "$500", "$6,000", "expensive", "budget", "cost per terabyte"]):
        return "Analysis"
    return "Industry"


def paragraph_to_html(paragraph: str) -> str:
    safe = html.escape(clean_text(paragraph))
    return f"<p>{safe}</p>"


def heading_to_html(heading: str) -> str:
    safe = html.escape(clean_text(heading))
    return f"<h2>{safe}</h2>"


def parse_markdown_post(path: Path, published: date) -> Post:
    lines = path.read_text().replace("\r\n", "\n").splitlines()
    title = ""
    blocks: list[tuple[str, str]] = []
    current: list[str] = []
    current_kind = "p"

    def flush() -> None:
        nonlocal current, current_kind
        text = "\n".join(current).strip()
        if text:
            blocks.append((current_kind, clean_text(text)))
        current = []
        current_kind = "p"

    for line in lines:
        stripped = line.strip()
        if not stripped:
            flush()
            continue
        if not title:
            title = normalize_title(stripped)
            continue
        if stripped.startswith("## "):
            flush()
            blocks.append(("h2", clean_text(stripped[3:])))
            continue
        current.append(stripped)

    flush()

    paragraphs = [text for kind, text in blocks if kind == "p"]
    opening = ""
    for paragraph in paragraphs[:3]:
        candidate = clean_text(f"{opening} {paragraph}")
        opening = candidate.strip()
        if len(opening) >= 140:
            break
    description = summarize_paragraph(opening or paragraphs[0])
    body_html = "".join(
        heading_to_html(text) if kind == "h2" else paragraph_to_html(text)
        for kind, text in blocks
    )
    full_text = " ".join(paragraphs)
    return Post(
        slug=slugify(path.stem),
        title=title,
        description=description,
        category=detect_category(title, full_text),
        published=published,
        minutes=reading_minutes(full_text),
        body_html=body_html,
    )


def parse_existing_post(path: Path) -> Post:
    text = path.read_text()
    title = clean_text(re.search(r"<title>(.*?) \| TapeBackup\.org</title>", text, re.S).group(1))
    description = clean_text(re.search(r'<meta name="description" content="(.*?)" />', text, re.S).group(1))
    category = clean_text(re.search(r'"articleSection":"(.*?)"', text, re.S).group(1))
    published_text = re.search(r'"datePublished":"(\d{4}-\d{2}-\d{2})"', text, re.S).group(1)
    published = date.fromisoformat(published_text)
    min_match = re.search(r'<span class="pill alt">(\d+) min read</span>', text)
    minutes = int(min_match.group(1)) if min_match else 1
    body_match = re.search(r'<section class="article-body">(.*?)</section>', text, re.S)
    body_html = body_match.group(1) if body_match else ""
    return Post(
        slug=path.parent.name,
        title=title,
        description=description,
        category=category,
        published=published,
        minutes=minutes,
        body_html=body_html,
    )


def render_article(post: Post) -> str:
    title = html.escape(post.title)
    description = html.escape(post.description)
    category = html.escape(post.category)
    url = f"{SITE}/blog/{post.slug}"
    iso_date = post.published.isoformat()
    display_date = format_display_date(post.published)
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{title} | TapeBackup.org</title>
    <meta name="description" content="{description}" />
    <meta name="robots" content="index, follow" />
    <link rel="canonical" href="{url}" />
    <meta property="og:type" content="article" />
    <meta property="og:title" content="{title}" />
    <meta property="og:description" content="{description}" />
    <meta property="og:url" content="{url}" />
    <meta property="og:image" content="{SITE}/og-image.png" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{title}" />
    <meta name="twitter:description" content="{description}" />
    <meta name="twitter:image" content="{SITE}/og-image.png" />
    <meta name="theme-color" content="#183976" />
    <link rel="icon" href="/favicon.png" type="image/png" />
    <link rel="stylesheet" href="/blog-static.css" />
    <script defer src="/assets/outbound-links.js"></script>
    <script type="application/ld+json">{json.dumps({"@context": "https://schema.org", "@type": "BlogPosting", "headline": post.title, "description": post.description, "datePublished": iso_date, "dateModified": iso_date, "mainEntityOfPage": url, "url": url, "author": {"@type": "Organization", "name": "TapeBackup.org"}, "publisher": {"@type": "Organization", "name": "TapeBackup.org", "logo": {"@type": "ImageObject", "url": f"{SITE}/favicon.png"}}, "articleSection": post.category}, separators=(",", ":"))}</script>
  </head>
  <body>
    <div class="site-shell">
      <header class="topbar">
        <div class="container topbar-inner">
          <a class="brand" href="/home">
            <img src="/assets/logo-BdaQDFFQ.png" alt="TapeBackup logo" />
            <span class="brand-copy"><strong>LTO Tape Info</strong><span>Static article page</span></span>
          </a>
          <nav class="topnav" aria-label="Primary">
            <a href="/home">Home</a>
            <a href="/about">About LTO</a>
            <a href="/why-tape">Why Tape</a>
            <a href="/tape-q-and-a">Q&amp;A</a>
            <a href="/blog" class="current">Blog</a>
            <a href="/contact">Contact</a>
          </nav>
        </div>
      </header>

      <section class="hero">
        <div class="container hero-grid">
          <div class="hero-copy">
            <p class="eyebrow">{category} article</p>
            <h1>{title}</h1>
            <p>{description}</p>
            <div class="signal-row">
              <span class="signal-chip">{category}</span>
              <span class="signal-chip">{post.minutes} min read</span>
              <span class="signal-chip">{display_date}</span>
            </div>
          </div>
          <aside class="hero-panel">
            <p class="panel-label">Why this page exists</p>
            <p class="panel-copy">This article is published as a standalone static page so it resolves directly on TapeBackup.org, carries its own metadata, and remains crawlable even when the single-page app routing layer is bypassed.</p>
          </aside>
        </div>
      </section>

      <main class="page">
        <div class="container article-layout">
          <article class="article-card">
            <div class="breadcrumbs"><a href="/home">Home</a><span>/</span><a href="/blog">Blog</a><span>/</span><span>{category}</span></div>
            <header class="article-header">
              <div class="detail-meta">
                <span class="pill">{category}</span>
                <span class="pill alt">{post.minutes} min read</span>
                <span class="pill alt">{display_date}</span>
              </div>
              <h2 class="detail-title">{title}</h2>
              <p class="lead">{description}</p>
            </header>
            <section class="article-body">{post.body_html}</section>
            <a class="back-link" href="/blog">Back to Blog</a>
          </article>

          <aside class="sidebar">
            <section class="sidebar-card">
              <h2>Article signal</h2>
              <p>Recent tape-storage discussion distilled into a standalone TapeBackup.org article page with direct indexing metadata and a stable canonical URL.</p>
            </section>
            <section class="sidebar-card">
              <h2>Need a deeper LTO plan?</h2>
              <p>Browse the site resources, compare storage approaches, or contact the team for help deciding when tape belongs in your backup workflow.</p>
              <a class="cta" href="/contact">Talk to TapeBackup</a>
            </section>
          </aside>
        </div>
      </main>
    </div>
  </body>
</html>
"""


def render_listing(posts: list[Post]) -> str:
    cards = []
    for post in posts:
        title = html.escape(post.title)
        description = html.escape(post.description)
        category = html.escape(post.category)
        display_date = format_display_date(post.published)
        cards.append(
            f"""
  <article class="listing-card">
    <div class="listing-card-top">
      <span class="pill">{category}</span>
      <span class="pill alt">{post.minutes} min read</span>
    </div>
    <h2>{title}</h2>
    <div class="listing-date">{display_date}</div>
    <p>{description}</p>
    <a class="listing-link" href="/blog/{post.slug}">Read article -&gt;</a>
  </article>"""
        )

    count = len(posts)
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Blog | TapeBackup.org</title>
    <meta name="description" content="Recent TapeBackup.org articles about LTO tape backup, archive workflows, offsite copies, and real-world tape operations." />
    <meta name="robots" content="index, follow" />
    <link rel="canonical" href="{SITE}/blog" />
    <meta property="og:type" content="website" />
    <meta property="og:title" content="TapeBackup.org Blog" />
    <meta property="og:description" content="Recent TapeBackup.org articles about LTO tape backup, archive workflows, offsite copies, and real-world tape operations." />
    <meta property="og:url" content="{SITE}/blog" />
    <meta property="og:image" content="{SITE}/og-image.png" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="TapeBackup.org Blog" />
    <meta name="twitter:description" content="Recent TapeBackup.org articles about LTO tape backup, archive workflows, offsite copies, and real-world tape operations." />
    <meta name="twitter:image" content="{SITE}/og-image.png" />
    <meta name="theme-color" content="#183976" />
    <link rel="icon" href="/favicon.png" type="image/png" />
    <link rel="stylesheet" href="/blog-static.css" />
    <script defer src="/assets/outbound-links.js"></script>
  </head>
  <body>
    <div class="site-shell">
      <header class="topbar">
        <div class="container topbar-inner">
          <a class="brand" href="/home">
            <img src="/assets/logo-BdaQDFFQ.png" alt="TapeBackup logo" />
            <span class="brand-copy"><strong>LTO Tape Info</strong><span>Blog archive</span></span>
          </a>
          <nav class="topnav" aria-label="Primary">
            <a href="/home">Home</a>
            <a href="/about">About LTO</a>
            <a href="/why-tape">Why Tape</a>
            <a href="/tape-q-and-a">Q&amp;A</a>
            <a href="/blog" class="current">Blog</a>
            <a href="/contact">Contact</a>
          </nav>
        </div>
      </header>

      <section class="hero listing-hero">
        <div class="container hero-grid">
          <div class="hero-copy">
            <p class="eyebrow">TapeBackup.org blog</p>
            <h1>Recent articles about real-world LTO backup workflows</h1>
            <p>Clearer titles, direct links, and standalone article pages for the latest TapeBackup.org posts on LTO media, restore workflows, offsite rotation, and the messy practical side of tape.</p>
            <div class="signal-row">
              <span class="signal-chip">{count} recent posts</span>
              <span class="signal-chip">Static archive</span>
              <span class="signal-chip">Direct article routing</span>
            </div>
          </div>
          <aside class="hero-panel">
            <p class="panel-label">Reader note</p>
            <p class="panel-copy">This blog index is now published as a static page so the listing always shows the intended human-readable titles instead of falling back to slug strings.</p>
          </aside>
        </div>
      </section>

      <main class="page">
        <div class="container">
          <section class="listing-grid" aria-label="Blog posts">{"".join(cards)}
          </section>
        </div>
      </main>
    </div>
  </body>
</html>
"""


def update_sitemap(posts: list[Post]) -> None:
    path = ROOT / "sitemap.xml"
    text = path.read_text()

    blog_lines = [
        "  <!-- Blog / Knowledge Center -->",
        "  <url>",
        f"    <loc>{SITE}/blog</loc>",
        f"    <lastmod>{TODAY.isoformat()}</lastmod>",
        "    <changefreq>weekly</changefreq>",
        "    <priority>0.7</priority>",
        f'    <xhtml:link rel="alternate" hreflang="en" href="{SITE}/blog"/>',
        "  </url>",
        "",
        "  <!-- Blog Articles -->",
        "",
    ]

    for post in posts:
        blog_lines.extend(
            [
                "  <url>",
                f"    <loc>{SITE}/blog/{post.slug}</loc>",
                f"    <lastmod>{TODAY.isoformat()}</lastmod>",
                "    <changefreq>monthly</changefreq>",
                "    <priority>0.6</priority>",
                f'    <xhtml:link rel="alternate" hreflang="en" href="{SITE}/blog/{post.slug}"/>',
                "  </url>",
                "",
            ]
        )

    block = "\n".join(blog_lines).rstrip()
    updated = re.sub(
        r"  <!-- Blog / Knowledge Center -->.*?</urlset>",
        block + "\n</urlset>",
        text,
        flags=re.S,
    )
    path.write_text(updated)


def assign_dates(paths: list[Path]) -> dict[Path, date]:
    total_days = (NEW_POST_RANGE_END - NEW_POST_RANGE_START).days + 1
    all_days = [NEW_POST_RANGE_START + timedelta(days=index) for index in range(total_days)]
    chooser = random.Random(RANDOM_SEED)
    picked = sorted(chooser.sample(all_days, len(paths)), reverse=True)
    return {path: picked[index] for index, path in enumerate(sorted(paths))}


def main() -> None:
    new_slugs = {slugify(path.stem) for path in NEW_SOURCES}
    existing_paths = [
        path
        for path in sorted((ROOT / "blog").glob("*/index.html"))
        if path.parent.name not in new_slugs
    ]
    existing_posts = [parse_existing_post(path) for path in existing_paths]
    date_map = assign_dates(NEW_SOURCES)
    new_posts = [parse_markdown_post(path, date_map[path]) for path in NEW_SOURCES]

    for post in new_posts:
        detail_dir = ROOT / "blog" / post.slug
        detail_dir.mkdir(parents=True, exist_ok=True)
        (detail_dir / "index.html").write_text(render_article(post))

    all_posts = sorted(existing_posts + new_posts, key=lambda post: (post.published, post.slug), reverse=True)
    (ROOT / "blog" / "index.html").write_text(render_listing(all_posts))
    update_sitemap(all_posts)

    for post in new_posts:
        print(f"{post.published.isoformat()}  {post.slug}")


if __name__ == "__main__":
    main()
