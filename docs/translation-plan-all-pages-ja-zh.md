# Handoff: translate every page into all languages, then add Japanese and Chinese

Audience: a coding agent working in `~/coldmail/tapebackup` (tapebackup.org, static site, deployed by Vercel when `main` is pushed).
Written: 2026-10-12.

## Goal

1. **Part A:** translate the 34 English-only pages into the six existing languages (de, fr, it, es, nl, pl). That makes all 7 site languages complete.
2. **Part B:** add **Japanese (`ja`)** and **Simplified Chinese (`zh`, hreflang `zh-Hans`)** as new editions covering all 66 English pages.

When both parts are done, every English URL in `sitemap.xml` has 8 translations (66 × 9 = 594 URLs).

Do Part A before Part B. Part A extends the pipeline to new page types, and Part B then reuses that work.

## Current state (verify before starting)

```bash
cd ~/coldmail/tapebackup
python3 scripts/i18n.py status          # TM size and missing segments per language
grep -c "<loc>" sitemap.xml             # 258 today = 66 EN + 32 × 6 translated
```

- Languages: en plus de, fr, it, es, nl, pl, listed in `scripts/i18n.py` → `LANGS`, `LANG_META`, and `data/i18n/languages.json`.
- 32 English pages are translated. They are the paths in `i18n.SCOPE`.
- **34 English pages are not translated.**

| Group | Count | Paths |
|---|---|---|
| Blog | 23 | `/blog` (index) and 22 posts under `/blog/<slug>` |
| Tape Q&A | 6 | `/tape-q-and-a` (index) and 5 answers under `/tape-q-and-a/<slug>` |
| Archived price snapshots | 5 | `/lto-tape-price-trend/{aug-2026,mar-2026,jan-2026,nov-dec-2025,sep-oct-2025}` |

To list them exactly:

```bash
python3 - <<'EOF'
import re,sys; sys.path.insert(0,'scripts'); import i18n
locs=re.findall(r'<loc>https://tapebackup.org([^<]*)</loc>',open('sitemap.xml').read())
en=[l.rstrip('/') or '/' for l in locs if not re.match(r'/(de|fr|it|es|nl|pl|ja|zh)(/|$)',l)]
print('\n'.join(p for p in en if p not in set(i18n.SCOPE)))
EOF
```

## How the translation pipeline works

Read these before editing anything: `scripts/i18n.py`, `scripts/i18n_tool.py`, `scripts/markets.py`, `scripts/build_site.py` (`build_languages`, `main`), `data/i18n/GLOSSARY.md`, `docs/europe-language-plan.md`.

1. `python3 scripts/build_site.py` builds English into the repo root.
2. `build_languages()` handles each language in turn:
   1. Selects that language's **market** (`markets.LANG_TO_MARKET`): EUR with VAT for de, fr, it, es and nl; PLN for pl.
   2. Rebuilds the generated pages into `.build/<lang>/` using that market's prices (`data/eu/prices-<lang>-2026-09.json`).
   3. Calls `i18n.render_language(lang, …)`. This function only translates the paths in `SCOPE` that exist in `.build/<lang>/`.
3. `render_language` splits each page into text segments.
   - Inline tags are masked as `<a1>…</a1>`.
   - Numbers become `{0}`, `{1}` placeholders.
   - Each segment is looked up in the translation memory `data/i18n/tm/<lang>.*.json`.
   - Segments with no TM entry are left in English and written to `data/i18n/segments/<lang>.json`.
4. Numbers, money and ISO dates are localized after translation by `localize_numbers` (`FMT`, `DATE_FMT`, `LOC_RE`).
5. `add_alternates_to_english()` writes hreflang links and the language switcher into the English SCOPE pages.
6. `videos.embed_all(i18n.LANGS)` embeds YouTube players into `/<lang>/` copies. `chatbot.build()` adds the assistant widget.

### Translation-memory workflow, per language

```bash
python3 scripts/i18n_tool.py export <lang> 1 1        # writes .build/i18n-batches/<lang>-1.json (missing segments)
# translate that JSON (keep keys, fill values) → e.g. .build/i18n-batches/<lang>-1.out.json
python3 scripts/i18n_tool.py merge <lang> 1 .build/i18n-batches/<lang>-1.out.json
python3 scripts/i18n_tool.py check <lang>              # validator; must print zero problems
```

The validator (`i18n_tool.py`) rejects:

- Changed, missing or extra `<aN>` tags or `{N}` placeholders.
- **Any digit written outside a placeholder.** Write numbers out as words ("cztery"), or keep the `{N}`.
- Titles over 60 characters and descriptions over 155 characters (`LIMITS`).

A large export can be split into several batches. Run one translation agent per language in parallel; each language has its own TM files, so they do not collide.

### Translation rules (follow `data/i18n/GLOSSARY.md`)

- Keep product names, vendor names, part numbers, LTO generation names, units, and everything in `DNT` and the seller names in English.
- Use the register given per language in the glossary.
- Never translate URLs, code, or terminal commands.
- Shorten rather than overflow the title and description limits.
- Write natural, human prose in the target language. Do not translate word for word.

## Part A: the 34 English-only pages × 6 languages

### A1. Why these pages are missing today

These pages are not built by the market builders:

- The blog posts are hand-published HTML in `blog/`, plus `scripts/generate_blog_posts.py` and `scripts/blog_posts_2026_10.py`.
- The Q&A pages come from `scripts/generate_tape_qa.py`.
- The snapshots are frozen pages.

None of them is ever written into `.build/<lang>/`, so `render_language` skips them even if they are added to SCOPE.

### A2. Pipeline change

In `build_languages()`, after the market build for a language, **copy the finished English HTML** of these pages into the staging folder:

- Copy `ROOT/<path>/index.html` to `.build/<lang>/<path>/index.html`.
- Copy after `blog_site_header()`, `apply_qa_noindex()`, `qa_page_schema()`, `answer_first_panels()` and `blog_related_links()` have run, so the translated copies inherit those fixes.
- Then add the 34 paths to `SCOPE`, or to a second list `SCOPE_STATIC` that `render_language` and `add_alternates_to_english` iterate as well.
- Keep the lists data-driven: glob `blog/*/index.html` and `tape-q-and-a/*/index.html`. New posts should then be picked up automatically, with their segments reported as missing until translated.

### A3. Content decisions

- **Blog and snapshot prices stay as written.** The blog posts quote US dollar prices (for example `best-value-per-terabyte-tape-backup-us`), and snapshots are historical records.
  - Do not convert the money. `localize_numbers` will reformat `$1,234` into local number style, which is fine.
  - Where a post compares US prices, add one translated sentence near the top that says the figures are US dollar prices, and link to the local price page `/<lang>/lto-tape-price-trend`.
  - Add the sentence as a segment through the TM, not by editing the English.
- **Noindex is carried over.** Q&A pages listed in `data/qa-noindex.json` must stay `noindex` in every language. The translated copy inherits the English `<meta robots>`; verify that `render_page` does not overwrite it.
- **Blog post text is long.** About 22 posts × ~1,500 words per language. Batch per post, and give the translator the glossary plus 2–3 already-translated pages from the same language as a style reference.
- **The `/blog` index and the home-page blog cards** (`data/home-blog.json`) must link to the translated post URLs in each language. Check that `render_page` rewrites internal links to `/<lang>/…` for these new paths.
- **Inline SVG figures** in blog posts contain only product names, generation names and numbers, so the files are shared. Translate their `alt` text and `<figcaption>`, which pass through the TM.
- **JS clips** (`jsvideo.py`): the text lives in `<script id="jsv-text" data-i18n>` JSON and is already translated through the TM. No change is needed.
- **YouTube embeds**: the one blog video (`/blog/offsite-tape-backups-…`) will now also be embedded on its `/<lang>/` copies, because `embed_all` loops over the languages.

### A4. Done criteria for Part A

- The build log shows each language with `segments translated` at 100% (`total/total`).
- `python3 scripts/i18n.py status` reports 0 missing for every language.
- The sitemap has 66 × 7 = 462 URLs, and every page carries hreflang alternates for all 7 languages plus `x-default`.

## Part B: add Japanese (`ja`) and Simplified Chinese (`zh`)

### B1. Register the languages

| Where | ja | zh |
|---|---|---|
| `i18n.LANGS` | add `"ja"` | add `"zh"` |
| `i18n.LANG_META` | locale `ja_JP`, hreflang `ja`, html `lang="ja"` | locale `zh_CN`, hreflang `zh-Hans`, html `lang="zh-Hans"` |
| `data/i18n/languages.json` | `{"name": "日本語", "indexable": false}` | `{"name": "简体中文", "indexable": false}` |
| URL prefix | `/ja/` | `/zh/` |

- Keep `indexable: false` until a human has reviewed a sample of pages. While false, the pages build with `noindex` and stay out of the hreflang sets on English pages.
- Search the code for every hard-coded language list (`de|fr|it|es|nl|pl`, for example in sitemap building, `vercel.json` rewrites and `middleware.js` language detection) and add `ja` and `zh` to each:

```bash
grep -rn "nl.*pl\|\"pl\"" scripts/ *.js vercel.json
```

- **Do not edit or commit `middleware.js`.** Another session owns it. If it needs ja/zh, write that down in the report for the user.

### B2. Market and prices

Each language needs a market, or `build_languages` skips it ("no price data yet").

- **Option 1 (recommended to start):** map `ja` and `zh` to the **US market** (USD) in `markets.LANG_TO_MARKET`. Then `build_languages` uses `data/prices-2026-09.json`.
  - Add a translated note on the price pages: "Prices are US seller listings in US dollars."
  - This needs no new research.
- **Option 2 (later):** research Japanese seller listings (JPY, with tax) and Chinese ones (CNY, 含税). Store them as `data/apac/prices-ja-2026-09.json` and `prices-zh-2026-09.json` in the same schema as `data/eu/prices-de-2026-09.json`, and add `jp` and `cn` markets.
- Ask the user before choosing Option 2.

If Option 2 is used, or if any money is shown in local style:

- Extend `LOC_RE` and the money symbol handling for `¥`, `￥`, `円` and `元`.
- Japanese puts the symbol before the number (`¥12,800`) or `円` after it (`12,800円`).
- Chinese uses `¥` or `￥` before the number, or `元` after it.

### B3. Number and date formatting

Add these to `FMT` and `DATE_FMT` in `scripts/i18n.py`:

```python
FMT["ja"] = {"dec": ".", "grp": ",", "after": False, "min_grp": 4}
FMT["zh"] = {"dec": ".", "grp": ",", "after": False, "min_grp": 4}
DATE_FMT["ja"] = "{y}年{m}月{d}日"   # strip leading zeros: 2026年9月30日
DATE_FMT["zh"] = "{y}年{m}月{d}日"
```

`DATE_FMT` currently keeps zero padding, so add an int() step for ja and zh. Units stay as `TB`, `MB/s` and so on. CJK text has no space between a number and a CJK character; a space before a Latin unit is fine.

### B4. Length limits for CJK

A CJK character is about twice as wide as a Latin one in search results.

- Titles: about 30–32 characters.
- Descriptions: about 80 (ja) or 78 (zh).
- Make `LIMITS` in `i18n_tool.py` language-aware. An easy rule: count each character in the `　-鿿＀-￯` range as 2 and check the total against 60 and 155.

### B5. Fonts and layout

- Space Grotesk, Hanken Grotesk and Space Mono have **no CJK glyphs**.
- For `html[lang="ja"]` and `html[lang|="zh"]`, add a fallback stack in the shared CSS:
  - ja: `"Hiragino Sans", "Noto Sans JP", "Yu Gothic", sans-serif`
  - zh: `"PingFang SC", "Noto Sans SC", "Microsoft YaHei", sans-serif`
- Keep the Latin fonts first so numbers and product names keep the site look.
- Use system fonts only. Do not load a multi-MB web font. If a web font is needed, use Google Fonts with `&text=` subsetting or `display=swap`.
- Add `word-break: normal; line-break: strict; overflow-wrap: anywhere` for CJK body text.
- Allow headings to wrap.
- Check that the line height (1.6–1.8) suits CJK text.
- Check buttons and table headers for overflow at 375 px width.

### B6. UI strings that live outside the TM

Add `ja` and `zh` entries to each of these:

- `chat-widget.js` → the `T` dictionary (en/de/fr/it/es/nl/pl today): widget title, placeholder, limit message and error message.
- `scripts/videos.py` → `LABEL`, `PLAY`, `ONYT`. For example `LABEL["ja"] = "動画（英語）"` and `LABEL["zh"] = "视频（英文）"`.
- The language-switcher labels come from `languages.json` → `name`.
- `scripts/chatbot.py` / `api/chat.js`: check whether the assistant is told to answer in the page language. Add ja and zh if a language list exists.
- `llms.txt` and `llms-full.txt`: update the "languages" line in `build_llms`.

### B7. Glossary additions (`data/i18n/GLOSSARY.md`)

- **Japanese:**
  - Use です/ます form.
  - Use standard IT katakana: テープ, ドライブ, カートリッジ, バックアップ, アーカイブ, ライブラリ.
  - Write "LTO-9" and "TB" as is.
  - Use full-width punctuation (、。「」) and half-width digits.
- **Chinese (Simplified, mainland usage):**
  - Use these terms: 磁带, 磁带机, 磁带库, 备份, 归档, 带库, 离线, 勒索软件.
  - Use full-width punctuation (，。：「」 or “”) and half-width digits.
  - Do not use Traditional characters.
- For both languages, keep brand names (Veeam, Commvault, IBM, HPE, Quantum and so on) in Latin script, and keep the `DNT` list untouched.

### B8. Translate

Run the same TM workflow for `ja` and `zh` over **all 66 pages** (the 32 core pages plus the 34 from Part A):

```bash
python3 scripts/build_site.py          # the first run lists all segments as missing for ja/zh
python3 scripts/i18n_tool.py export ja 1 1
python3 scripts/i18n_tool.py export zh 1 1
```

- Split into batches of about 300 segments.
- Use one agent per language per batch.
- After merging, run `check` for each language and rebuild.

## QA checklist (both parts)

- [ ] `python3 scripts/build_site.py` finishes. Every language line reads `N/N segments translated`.
- [ ] `python3 scripts/i18n_tool.py check <lang>` returns clean for all 8 non-English languages.
- [ ] No English sentence is left in a translated page. Spot-check 5 pages per language with `get_page_text`.
- [ ] hreflang: every page lists the published set plus `x-default`, and the `ja` and `zh-Hans` codes are correct.
- [ ] The language switcher appears on blog posts, Q&A pages and snapshots in every language.
- [ ] Internal links on `/<lang>/…` pages stay inside the same language where a translation exists.
- [ ] `noindex` Q&A pages stay noindex in every language. Unreviewed languages are noindex and absent from the sitemap or English hreflang.
- [ ] Phone width (375 px): no horizontal scroll on the translated blog posts with wide tables (`.article-layout > * { min-width: 0 }` is already in `blog-static.css`), or on the ja/zh pages.
- [ ] Take Playwright screenshots of the `/ja/` and `/zh/` home page, price page, one blog post and the calculator. Check that the CJK fonts render with no tofu boxes.
- [ ] The JS clips and YouTube facades show translated labels.
- [ ] The sitemap count matches the expected total, and the `lastmod` values are sensible.
- [ ] `llms.txt` lists all languages.

## Deploy and rules

```bash
git add -A -- . ':!middleware.js'
git commit -m "i18n: translate blog, Q&A and snapshots; add ja and zh editions" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
git push            # Vercel deploys tapebackup.org automatically
```

- **Never commit `middleware.js`.** Another session owns it.
- **Never put an API key in the repo.** The repo is public. The chatbot key lives only in Vercel environment variables.
- Commit TM files (`data/i18n/tm/*.json`) together with the code that needs them.
- Deploy Part A on its own before starting Part B.
- After the deploy, submit the new URLs to IndexNow (key `a0ed351786eb61e63fa37794b1135e32`, endpoint `https://api.indexnow.org/indexnow`, host `tapebackup.org`) in batches of up to 10,000. Only submit indexable URLs, so skip ja and zh until they are flipped to `indexable: true`.
- Flipping ja or zh to `indexable: true` is the user's decision after review. Report and ask; do not flip it yourself.

## Report back to the user

- Per language: pages written, segments translated, and validator result.
- Any pages that could not be translated, with the reason.
- Decisions taken (the market option for ja and zh, the font approach).
- Anything that needs the user: the `middleware.js` changes, the review before indexing, and the JPY/CNY price research.
