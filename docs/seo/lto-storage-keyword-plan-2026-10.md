# LTO storage keyword plan (October 2026)

Source: Ahrefs "matching terms" export for **lto storage**, Google US, 2026-10-17. There are 66 keywords.
Only 6 have a recorded US volume. Together they add up to about 400 searches a month: lto storage 150, lto tape storage 90, the OWC Mercury Pro LTO-9 drive 80, the OWC LTO-7 drive 30, lto data storage 30, lto vs object storage 30. The other 60 are long-tail variants. All recorded difficulties are 0, so one good page per topic should be enough to rank.

## Current coverage

- Every topic except 3 keywords already has a related page.
- **No page targets "LTO storage" or "LTO tape storage" by name.** `/lto-tape` covers the format, but its title and H1 never say "storage".
- Storage conditions are one short section on `/why-tape/lto-tape-lifespan`: 16 to 25 °C, 20 to 50% RH.
- Cases are one paragraph on `/resources/lto-cleaning-tapes-and-labels`.
- OWC appears only in a list of desktop drive brands. There is no page about its products.
- There is no LTO vs object storage comparison.
- `/lto-tape-news` is still the September roundup.

## Plan

Rank: priority order. N = new page, U = update an existing page.

| Rank | Page | Type | Keywords | Why it matters |
|---|---|---|---|---|
| 1 | **N1 `/lto-storage`** | new pillar | 22 (lto storage, lto tape storage, lto data storage, what is / how does LTO storage work, LTO storage system ...) | Head terms, about 270 searches/mo, AI Overview on the results page |
| 2 | **N2 `/resources/how-to-store-lto-tapes`** | new guide | 13 (temperature and humidity, cabinet, rack, case, box, offsite, rotation) | Clear buyer and how-to intent; we only cover it in passing today |
| 3 | **N3 `/resources/owc-lto-tape-drives`** | new guide | 5 (OWC Mercury Pro LTO-9 / LTO-7, Archive Pro LTO-9 / LTO-8, reviews) | About 130 searches/mo, transactional |
| 4 | **N4 `/comparisons/lto-vs-object-storage`** | new comparison | lto vs object storage (30) | No page yet. Links naturally to the Tape Archive Advisor (S3-to-tape gateways) |
| 5 | U3 `/why-tape/lto-tape-drive` | update | 11 drive and model terms (HPE, HP LTO-5 / LTO-6 6250, IBM, Quantum, rack mount, enclosure) | Add a model table and a rack mount section |
| 6 | U1 `/lto-tape-capacity` | update | 6 (LTO storage capacity, LTO-6 capacity, native LTO-6, raw vs actual) | FAQ answers in the format AI Overviews quote |
| 7 | U7 `/lto-tape-news` | update | 3 news terms | October roundup, plus "LTO tape storage news" in the title |
| 8 | U2 `/lto-tape-price-trend` | update | lto tape storage cost per tb 2026 | One H2 or FAQ with that wording |
| 9 | U4 `/lto-tape-library` | update | lto tape storage library | Wording, plus a link from the pillar |
| 10 | Small edits | update | none (supporting) | `/lto-tape`, `/why-tape/lto-tape-lifespan`, `/resources/lto-cleaning-tapes-and-labels` and the offsite blog post link to N1 and N2; no duplicated text |

**Skipped (3):** *storage fee lto*, *lto storage fee*, *how much is the storage fee lto*. These are almost certainly searches about the Philippine Land Transportation Office (vehicle impound fees), not tape.

**Covered only in part (2):** *lto storage and rotation london / harlow*. These are local UK vault searches. N2 explains offsite rotation and what to ask a vault provider. We don't make a local page, because we are not a vault service.

## Page briefs

### N1 `/lto-storage`: LTO Storage: How LTO Tape Stores Data, Capacity and Cost (2026)

**Avoiding overlap with `/lto-tape`:**
- `/lto-tape` stays "what the LTO format is" (the standard, generations, compatibility).
- N1 is "LTO as a storage tier": how data gets on tape, what a tape storage system is made of, what it costs to run, and how to keep cartridges.
- The two pages link to each other.

**Answer-first block:** an LTO storage definition of about 50 words.

**Sections:**
- How LTO tape storage works: tracks, wraps, servo, linear serpentine writing, LTFS. Diagram 1 shows the cartridge, drive head and data path.
- Parts of an LTO storage system: drive or library, server, software, cartridges, offsite copy. Diagram 2 shows a system map.
- Capacity, native vs compressed: a short table that links to the capacity chart.
- LTO storage cost per TB in 2026: generated from the price data, the same way the price pages do it.
- Where LTO storage fits: archive, backup copy, air gap. Also when not to use it.
- Storing the cartridges: summary and link to N2.
- FAQ: six questions, using the exact phrasings from the keyword list.

**Build:** a generated guide page (`build_guides.py`). It is added to `i18n.SCOPE`, so the 8 translations come through the TM workflow.

### N2 `/resources/how-to-store-lto-tapes`: How to Store LTO Tapes: Temperature, Humidity, Cases and Cabinets

**Sections:**
- **Conditions table:** short-term vs long-term storage, temperature, humidity and acclimatisation. Figures come from the Fujifilm, IBM and HPE media data sheets, verified and cited at writing time.
- **Cases and boxes:** jewel case, turtle case, transport cases.
- **Cabinets and racks:** media cabinets, fire-rated and magnetic-safe options, rack shelving. Kept generic: types and what to check, with no invented models or prices.
- **Offsite storage and rotation:** grandfather-father-son rotation, what to ask a vault provider, chain of custody. Links to the offsite blog post.
- **Handling:** checklist.

**Diagram:** a conditions gauge and a rotation calendar.

The lifespan page keeps its short summary and links to this guide.

### N3 `/resources/owc-lto-tape-drives`: OWC Mercury Pro and Archive Pro LTO Drives: What You Get

**Content:**
- A spec and price guide (we have not tested the drives hands-on):
  - drive mechanism inside;
  - interface (Thunderbolt and SAS);
  - bundled software;
  - Mac and Windows support;
  - the LTO-7, LTO-8 and LTO-9 variants;
  - Archive Pro vs Mercury Pro.
- Where it fits against HPE, IBM and Quantum drives and other desktop brands.
- Current prices, if they are in our seller data.

**Rule:** every spec is checked on OWC's own pages first, and the review keyword is answered honestly ("what owners report" only with sources).

### N4 `/comparisons/lto-vs-object-storage`: LTO Tape vs Object Storage (S3): Cost, Access and When to Use Each

**Content:**
- A cost per TB comparison table using our price data, with cloud list prices as dated and cited.
- Time to first byte, durability, offline air gap and lock-in.
- A section on S3-to-tape (Glacier-style tape tiers), linking to the Tape Archive Advisor and the Ledger-backed products.

**Diagram:** an access-time vs cost chart.

### Updates (U1 to U7)

- **U1 capacity:** FAQ entries "What is the native storage capacity of an LTO-6 tape?" (2.5 TB native, 6.25 TB compressed) and "Raw vs actual usable capacity" (LTFS index overhead, real compression ratios). Title becomes "LTO Tape Capacity Chart: LTO-1 to LTO-14 Storage Sizes".
- **U2 prices:** one H2 "LTO tape storage cost per TB in 2026", generated from the current month's data.
- **U3 drives:**
  - A model table: HPE StoreEver (current LTO-9 external and internal), legacy HP LTO-5 and LTO-6 (Ultrium 3000 and 6250) for used buyers, IBM (current and the old TotalStorage name), Quantum, and OWC with a link to N3.
  - A "rack mount kits and enclosures" section.
  - Every model name is checked against the vendor's site first.
- **U4 library:** "tape storage library" wording, plus a link from N1.
- **U7 news:** October 2026 roundup. Title pattern "LTO Tape Storage News: October 2026".

## Work order and effort

1. **Check Search Console first:** which page currently gets impressions for "lto storage" and "lto tape storage"? If `/lto-tape` already ranks, retitle it instead of building N1, so the site doesn't end up with two pages competing for the same term.
2. **N1 and N2** (highest value):
   - written in English, with 2 diagrams each in the site's figure style;
   - added to the sitemap, llms.txt and the Tools/Resources menus;
   - translated into the 8 languages through the TM.
3. **U1, U2, U4, U7** (small edits, one session).
4. **N3 and U3** (need fresh vendor checks).
5. **N4.**
6. **After each deploy:** submit to IndexNow; recheck Search Console 4 weeks later.

**Writing rules:**
- Site style: no dashes as punctuation, no hype, plain verified claims.
- Prices come from `data/` and are never typed by hand.
- Each new page gets an answer-first paragraph, an FAQ with FAQPage schema, and breadcrumb schema.

## Keyword map (all 66)

| Keyword | US vol | KD | Target | What covers it |
|---|---|---|---|---|
| lto storage | 150 | 0 | N1 /lto-storage | Pillar page |
| lto tape storage | 90 | 0 | N1 /lto-storage | Pillar page |
| owc mercury pro lto-9 tape storage drive | 80 | - | N3 /resources/owc-lto-tape-drives | New spec guide; also a row in the drive guide |
| owc mercury pro lto-7 tape storage drive | 30 | - | N3 /resources/owc-lto-tape-drives | New spec guide; also a row in the drive guide |
| lto data storage | 30 | 0 | N1 /lto-storage | Pillar page |
| [lto vs object storage] | 30 | - | N4 /comparisons/lto-vs-object-storage | New comparison |
| tape storage news today lto | 10 | - | U7 /lto-tape-news | Title/H1 + October roundup |
| owc archive pro lto-9 tape storage solution | 10 | - | N3 /resources/owc-lto-tape-drives | New spec guide; also a row in the drive guide |
| lto tape cartridge data storage | 10 | - | N1 /lto-storage | Pillar page |
| lto tape archival storage | 10 | - | N1 /lto-storage | Pillar page |
| owc archive pro lto-8 tape storage solution | 10 | - | N3 /resources/owc-lto-tape-drives | New spec guide; also a row in the drive guide |
| lto tape storage rack | 10 | - | N2 /resources/how-to-store-lto-tapes | Cases, boxes, cabinets, racks section |
| what is lto storage | 10 | - | N1 /lto-storage | Answer-first definition + how it works diagram |
| tape storage lto news today | 10 | - | U7 /lto-tape-news | Title/H1 + October roundup |
| lto tape storage cabinet | 10 | - | N2 /resources/how-to-store-lto-tapes | Cases, boxes, cabinets, racks section |
| hp tape drive tape storage lto 5 external | 10 | - | U3 /why-tape/lto-tape-drive | Model table (HPE, HP legacy, IBM, Quantum, desktop) + rack mount kits |
| lto tape data storage | - | - | N1 /lto-storage | Pillar page |
| lto magnetic tape cartridge data storage | - | - | N1 /lto-storage | Pillar page |
| lto ultrium storage enclosure | - | - | U3 /why-tape/lto-tape-drive | Model table (HPE, HP legacy, IBM, Quantum, desktop) + rack mount kits |
| lto storage capacity | - | - | U1 /lto-tape-capacity | FAQ: LTO-6 native capacity, raw vs usable |
| lto tape storage news | - | - | U7 /lto-tape-news | Title/H1 + October roundup |
| how does lto tape storage work? | - | - | N1 /lto-storage | Answer-first definition + how it works diagram |
| lto tape storage cartridge | - | - | N1 /lto-storage | Pillar page |
| lto offsite storage | - | - | N2 /resources/how-to-store-lto-tapes | Offsite and rotation section; links to the offsite blog post |
| hp storage hp lto-6 6250 rack mount | - | - | U3 /why-tape/lto-tape-drive | Model table (HPE, HP legacy, IBM, Quantum, desktop) + rack mount kits |
| how much is the storage fee lto | - | - | none | Skip: Philippine Land Transportation Office (vehicle impound fees), not tape |
| lto 6 tape storage capacity | - | - | U1 /lto-tape-capacity | FAQ: LTO-6 native capacity, raw vs usable |
| lto tape storage cost per tb 2026 | - | - | U2 /lto-tape-price-trend | H2 + FAQ "cost per TB in 2026" |
| lto tape storage case | - | - | N2 /resources/how-to-store-lto-tapes | Cases, boxes, cabinets, racks section |
| lto storage fee | - | - | none | Skip: Philippine Land Transportation Office (vehicle impound fees), not tape |
| lto tape storage library | - | - | U4 /lto-tape-library | Use the phrase "tape storage library"; link from pillar |
| lto 6 tape backup device with ssd storage | - | - | U3 /why-tape/lto-tape-drive | Model table (HPE, HP legacy, IBM, Quantum, desktop) + rack mount kits |
| native storage capacity of an lto-6 tape | - | - | U1 /lto-tape-capacity | FAQ: LTO-6 native capacity, raw vs usable |
| lto storage and rotation harlow | - | - | N2 /resources/how-to-store-lto-tapes | Partial: offsite rotation section (no local page; we are not a vault service) |
| storage fee lto | - | - | none | Skip: Philippine Land Transportation Office (vehicle impound fees), not tape |
| lto storage and rotation london | - | - | N2 /resources/how-to-store-lto-tapes | Partial: offsite rotation section (no local page; we are not a vault service) |
| lto storage case | - | - | N2 /resources/how-to-store-lto-tapes | Cases, boxes, cabinets, racks section |
| what is lto tape storage | - | - | N1 /lto-storage | Answer-first definition + how it works diagram |
| magnetic tape storage lto | - | - | N1 /lto-storage | Pillar page |
| hp storage hp lto-6 ultrium 6250 rack mount | - | - | U3 /why-tape/lto-tape-drive | Model table (HPE, HP legacy, IBM, Quantum, desktop) + rack mount kits |
| lto tape storage box | - | - | N2 /resources/how-to-store-lto-tapes | Cases, boxes, cabinets, racks section |
| lto storage meaning | - | - | N1 /lto-storage | Answer-first definition + how it works diagram |
| lto storage tapes | - | - | N1 /lto-storage | Pillar page |
| lto tape storage system | - | - | N1 /lto-storage | Pillar page |
| lto tape cartridge storage | - | - | N1 /lto-storage | Pillar page |
| lto tape storage conditions temperature humidity | - | - | N2 /resources/how-to-store-lto-tapes | New guide; lifespan page links to it |
| owc mercury pro lto-9 tape storage drive reviews | - | - | N3 /resources/owc-lto-tape-drives | New spec guide; also a row in the drive guide |
| lto storage drive | - | - | U3 /why-tape/lto-tape-drive | Model table (HPE, HP legacy, IBM, Quantum, desktop) + rack mount kits |
| lto tape media storage cabinet | - | - | N2 /resources/how-to-store-lto-tapes | Cases, boxes, cabinets, racks section |
| hpe storage lto ultrium tape drives | - | - | U3 /why-tape/lto-tape-drive | Model table (HPE, HP legacy, IBM, Quantum, desktop) + rack mount kits |
| lto storage system | - | - | N1 /lto-storage | Pillar page |
| tape storage lto | - | - | N1 /lto-storage | Pillar page |
| lto media storage | - | - | N1 /lto-storage | Pillar page |
| lto raw actual storage | - | - | U1 /lto-tape-capacity | FAQ: LTO-6 native capacity, raw vs usable |
| lto tapes storage | - | - | N1 /lto-storage | Pillar page |
| lto tape cartridge data center storage | - | - | N1 /lto-storage | Pillar page |
| storage lto | - | - | N1 /lto-storage | Pillar page |
| lto storage rack | - | - | N2 /resources/how-to-store-lto-tapes | Cases, boxes, cabinets, racks section |
| lto 8 storage | - | - | U1 /lto-tape-capacity | FAQ: LTO-6 native capacity, raw vs usable |
| ibm storage lto ultrium | - | - | U3 /why-tape/lto-tape-drive | Model table (HPE, HP legacy, IBM, Quantum, desktop) + rack mount kits |
| ibm total storage lto ultrium | - | - | U3 /why-tape/lto-tape-drive | Model table (HPE, HP legacy, IBM, Quantum, desktop) + rack mount kits |
| lto tape storage temperature | - | - | N2 /resources/how-to-store-lto-tapes | New guide; lifespan page links to it |
| lto storage cabinet | - | - | N2 /resources/how-to-store-lto-tapes | Cases, boxes, cabinets, racks section |
| hpe storage lto-9 ultrium external tape drive | - | - | U3 /why-tape/lto-tape-drive | Model table (HPE, HP legacy, IBM, Quantum, desktop) + rack mount kits |
| quantum lto-9 tape drive storage device | - | - | U3 /why-tape/lto-tape-drive | Model table (HPE, HP legacy, IBM, Quantum, desktop) + rack mount kits |
| lto 6 storage capacity | - | - | U1 /lto-tape-capacity | FAQ: LTO-6 native capacity, raw vs usable |
