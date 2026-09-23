# tapebackup.org: European language plan

Written 2026-09-23 from the Search Console export of 2026-08-30 (last 3 months), the current site build (53 indexable pages, ~60,000 words including page furniture) and the old React app's German and Polish strings.

## 1. What the data says

Europe is a quarter of the site's search impressions and almost nobody clicks, because every page is in English and every price is in US dollars from US sellers.

| Country | Impressions | Clicks | Avg. position | Language |
|---|---|---|---|---|
| United Kingdom | 1,694 | 5 | 26.1 | English (nothing to translate) |
| Germany | 976 | 6 | 10.4 | German |
| Netherlands | 795 | 0 | 7.6 | Dutch |
| Italy | 331 | 0 | 10.9 | Italian |
| France | 201 | 4 | 11.2 | French |
| Spain | 165 | 4 | 11.5 | Spanish |
| Poland | 158 | 1 | 9.6 | Polish |
| Switzerland + Austria | 168 | 2 | 9.5 | German |
| Belgium | 89 | 1 | 7.4 | Dutch / French |
| Sweden, Finland, Norway, Denmark | 270 | 2 | 8.0 | English works |
| Czechia, Hungary, Romania, Greece, Portugal | 300 | 5 | 7.0 | too small each |

Total Europe: 5,610 impressions, 36 clicks (25% of impressions, 37% of clicks). Pages already rank on page one in Germany, the Netherlands, Poland and the Nordics; they just do not get clicked.

Three more signals:

- German and Spanish queries already appear in the export ("lto-10 laufwerk preis", "anschaffungskosten", "kosten", "precios", "prix"), each with one or two impressions. People search in their own language and land on an English page.
- The old React app already carried German and Polish strings for the price pages, brand guide and contact page (27 translated titles each). They are recoverable from git (`git show 6f9662b:assets/index-k7LtoPrice.js`) and show that a German version was intended.
- European prices differ from US prices. On 2026-09-23 Alternate.de listed LTO-9 cartridges at €80.90 to €93.90 including VAT, below the $92.45 to $111.55 US range. A German page that shows US dollar prices is not a price tracker for a German reader.

## 2. Priority and scope

**Order: German, then Polish, then Italian, French and Spanish together, then decide Dutch.**

| Phase | Language | Why now | Pages | Words to translate |
|---|---|---|---|---|
| 1 | German (`/de/`) | Largest EU market (1,144 impressions across DE, AT, CH), queries already in German, legacy strings exist, EU sellers fetchable | Tier A + Tier B + top 5 blog posts | ~34,000 |
| 2 | Polish (`/pl/`) | Legacy strings exist; a Polish speaker can review in house; Senetic and other Polish sellers fetchable | Tier A + Tier B | ~29,000 |
| 3 | Italian, French, Spanish (`/it/`, `/fr/`, `/es/`) | 700 impressions combined at positions 11 to 12; Spanish also reaches Latin America (Brazil alone is 265 impressions in Portuguese, worth a look later) | Tier A only, Tier B after 8 weeks if DE traffic proves the model | ~11,000 each |
| 4 | Dutch (`/nl/`) | 884 impressions at position 7.6, but Dutch IT buyers overwhelmingly search and read in English; measure whether German lifts clicks first | Decide after phase 1 results | ~11,000 |

Not planned: Russian, Ukrainian, Turkish (outside the EU sales focus), Nordic languages (English serves them; positions are already 6 to 10).

### Page tiers

**Tier A, the money pages (11 pages, ~11,000 words).** Everything a buyer searching "LTO-9 Preis" or "prezzo LTO-8" needs:

- `/lto-tape-price-trend` and the five generation guides (LTO-6 to LTO-10)
- `/lto-tape-price-trend/history`
- `/comparisons/tape-vs-cloud-5-year-cost`
- `/backup-calculator`
- `/about`, `/contact`

**Tier B, the guides (9 pages, ~18,000 words).** `/why-tape`, `/why-tape/lto-tape-drive`, `/why-tape/lto-vs-hdd`, `/comparisons`, `/lto-tape-brand`, `/resources`, `/resources/cheap-lto-tapes`, `/resources/lto-tape-migration`, `/resources/tape-storage-market`, `/best-tape-backup-software`, `/backup-software-finder`, `/resources/tape-backup-software/catalogicdpx`.

**Tier C, editorial (blog and Q&A).** 18 blog posts (~18,000 words) and the 5 indexable Q&A pages. Translate only the posts that draw impressions: `offsite-tape-backups`, `tape-is-dead`, `which-lto-drive-should-you-buy`, `buying-a-few-cheap-lto-tapes`, `the-best-lto-backup-software`. The rest wait until a language shows clicks. The 57 noindexed Q&A pages are never translated.

**Never translated, in any language:** the five archived price snapshots (historic US data; they get a German banner and a link, not a translation), part numbers, seller names, product names, the noindexed Q&A pages.

## 3. The part that is not translation: European prices

Translating the price pages without European prices gives a German reader a page they cannot use. Each language phase therefore includes a **price layer for its market**, collected the same way the US layer is (seller product pages, part number, price, date seen) and stored beside it:

```
data/prices-2026-09.json        US sellers, USD (exists)
data/prices-eu-2026-09.json     EU sellers, EUR incl. VAT, per country where it differs
```

Sellers that answered a plain fetch with prices on 2026-09-23: Alternate.de (DE), LDLC (FR), Senetic (PL, sells across the EU), backup-store.de (DE). Blocked or empty: Amazon.de, Galaxus, Insight, Bechtle, Jacob, Reichelt (redirects to a JS search). Expect roughly the same coverage the US layer has: three to five specialist sellers per market, no big-box retailers.

Page behaviour:

- `/de/` pages show EUR (incl. 19% VAT, with the net figure in the note) first and the US range second, so the comparison is visible.
- Cost per TB, the calculator and the five-year tape vs cloud page compute from the EUR layer on `/de/`; cloud prices use AWS Frankfurt / Azure Germany West Central list prices, which the research script can fetch the same way it fetched us-east-1.
- The price history page gains an EU column from the first EU snapshot onward; no back-filling.
- Refresh cadence stays monthly, both layers together, one commit.

Without this layer the German pages would still rank for "was kostet LTO-9", but would answer in dollars. That is the difference between a translated site and a European one.

## 4. Technical design

The site is generated by `scripts/build_site.py`; almost every English string lives in Python (`GEN_COPY`, `ANSWERS`, `GUIDE_FAQS`, the article bodies, `site_shell.py` header and footer) or in captured HTML under `data/legacy-pages/`. The plan keeps that, adding a language dimension rather than a second site.

- **URLs:** language prefix, English slugs kept: `/de/lto-tape-price-trend/lto9-price`. Same rule as mrplanb.com's `/de/`, which keeps the page mapping 1:1 and makes hreflang, the sitemap and the language switch trivial. Localized slugs are worth perhaps a few percent in ranking and cost a redirect table forever; not worth it.
- **`site_shell.page()`** takes a `lang` argument: sets `<html lang>`, the canonical under the prefix, `hreflang` links to every sibling (`en`, `de`, … and `x-default` pointing at English), the localized header and footer, and the language switch (a small "EN | DE" in the top bar that maps the current path).
- **Strings:** move the English copy blocks into `data/i18n/en/*.json` (one file per builder), add `data/i18n/de/*.json` and so on. A builder reads its language's file and falls back to English for any missing key, so a half-translated language still builds but is flagged.
- **Legacy guides** (captured HTML): translate the HTML files themselves into `data/legacy-pages/de/`, the way mrplanb's blog was done, because the sanitizer already handles their structure.
- **Blog and Q&A:** translated HTML under `blog-de/<slug>/index.html`, published as `/de/blog/<slug>`; `apply_meta_overrides` and the QAPage schema step run per language.
- **Sitemap:** one `sitemap.xml` with `xhtml:link rel="alternate"` entries per URL, plus per-language `lastmod`. IndexNow submission includes every language after each build.
- **Formatting:** decimal comma and `€` after the number in German, Polish, Italian, French, Spanish (`92,45 €`); dates as "17. September 2026" / "17 września 2026". Part numbers, seller names and SKUs stay exactly as in the US data.
- **Structured data:** FAQ and QAPage answers are translated with the visible text (Google requires them to match). `Article.inLanguage` is set per page.
- **`llms.txt`:** a `/de/llms.txt` generated from the same data, because AI assistants answer German questions from German sources.
- **Noindex until reviewed:** a new language builds with `noindex` and off the sitemap until QA passes; flipping one flag indexes it and submits it.

## 5. Production pipeline (per language)

1. **Glossary first.** Copy `~/mrplanb-theme/scripts/translate/GLOSSARY.md` (Sie-form, "Backup" stays "Backup", never-translate list, decimal comma) and add the tape terms: LTO generations, cartridge (Kassette), drive (Laufwerk), library (Bibliothek/Library), WORM, LTFS, native vs compressed (nativ / komprimiert; the legacy strings used "komprimiert"), half-height, autoloader, cost per TB. Each language gets one file; agents read it in full before translating anything.
2. **Machine-assisted first pass by agents**, one batch per tier, with the brief adapted from `AGENT-BRIEF-STATIC.md`: same structure, same numbers, same links with the prefix added, titles at or under 60 characters, descriptions 120 to 155. German runs about 25% longer than English, so titles get shortened the same way mrplanb's did (`h1` keeps the full headline, `<title>` is the short one).
3. **Code checks** (`scripts/translate/qa-page.py`, to write): every number, part number, price, URL and table cell in the source appears in the translation; heading and table counts match; no leftover English paragraphs (word-list detector per language, as in mrplanb's `qa-blog.mjs`); title and description lengths; JSON-LD parses and matches visible text.
4. **Jev checks at scale** (the `jev-bulk-judge` skill, which already audited the English site): one request per paragraph pair asking whether the translation is natural for an IT-professional reader, whether it changes the meaning, and whether the glossary terms were kept. Threshold below 0.5 goes to a human; everything else ships. This is the step that makes five languages affordable: reading 30,000 words per language by hand does not scale, sampling the paragraphs Jev flags does.
5. **Human spot check** of the Tier A pages by a native reader (Polish in house; German, Italian, French, Spanish by a reviewer for one to two hours per language on the money pages only).
6. **Index, submit, watch.** Flip the flag, rebuild, push, IndexNow. Watch Search Console per country for eight weeks: impressions on `/de/` URLs, clicks, and whether German queries move from the English page to the German one.

## 6. Phases and effort

| Phase | What | Effort |
|---|---|---|
| 0 | i18n of the generator, hreflang, sitemap alternates, language switch, string extraction, QA scripts, per-language noindex flag | 2 days |
| 1 | German: EU price layer (4 to 5 DE sellers), Tier A + B + 5 posts, glossary, agent translation, code + Jev QA, review, launch | 3 to 4 days, then monthly refresh alongside the US layer |
| 2 | Polish: reuse legacy strings where they still match, Polish sellers (Senetic, x-kom, Morele), Tier A + B | 2 days |
| 3 | Italian, French, Spanish: Tier A each, EU sellers where they exist (LDLC for France; Italian and Spanish sellers still to find, otherwise show EUR from German sellers with a note) | 1 day each |
| 4 | Dutch: go/no-go from phase 1 data; Tier A only if go | 1 day |
| ongoing | Monthly price refresh across layers, new blog posts translated only into languages that show clicks | half a day a month |

Effort counts agent runs and review time, not wall-clock waiting. Phase 0 and 1 together are the first two weeks.

## 7. Decisions needed

1. **Slugs:** English slugs under a prefix (recommended, as mrplanb) or localized slugs.
2. **EU price layer in phase 1, or translation only first?** Recommended: with prices, because that is what makes `/de/` worth ranking. Translation only would be a day faster and much weaker.
3. **Polish review:** who in the team reads the Polish pages.
4. **Dutch:** measure first (recommended) or include from the start.
5. **Blog scope:** five posts for German only, or none until the guides show traffic.

## 8. What success looks like

Eight weeks after the German launch: German-language queries land on `/de/` pages instead of the English ones, the Germany, Austria and Switzerland click-through rate rises from 0.6% toward the 2% the site gets in France and Spain, and Search Console shows the EUR price pages as the top German landing pages. If that happens, phases 2 and 3 follow on the same tooling with no new design work. If it does not, stop after Polish and keep the two languages current.
