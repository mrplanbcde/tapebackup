# TapeBackup.org SEO plan, October 2026

Inputs: Search Console (last 28 days, 2 to 29 September 2026), the Ahrefs "matching terms" export for *linear tape open* (Google US, 1,000 keywords), the Ahrefs content gap for Google Germany against backupworks.com, ltoworld.com, datacenterdisk.com and lto.org, and a 20-keyword SERP sample. Keyword map: `docs/seo/keyword-map-us.csv` (rebuild with `scripts/seo_keyword_map.py`).

## 1. Where we stand

- 71 clicks and 6,001 impressions in 28 days. The price tracker brings most of it: 50 clicks, 3,320 impressions, average position 5.3.
- Price keywords rank 5 to 8 (lto tape price, lto-9 tape price, lto-10 drive price). They are small: Ahrefs puts all price and cost terms in the export at about 160 searches a month.
- The impressions with no clicks are the broad terms: tape backup software (position 28), lto tape drive (18), lto tape (25), lto backup software (25).
- The six language editions went live on 23 September. Germany is already the second country by clicks, and we rank 3rd for "lto speicher".

## 2. Competitors

| Domain | Type | Where it beats us |
|---|---|---|
| backupworks.com | Retailer with deep content | Drives and media for every generation, LTO-10 release and roadmap page, LTFS |
| ltoworld.com | Retailer | Media and desktop drives |
| buy.hpe.com | Vendor | Drives, LTO-10 |
| datacenterdisk.com | Independent price page | Price per TB, LTO tape prices (our closest like-for-like rival) |
| lto.org | Consortium | "lto 9", "lto-10", "lto 8", "lto tapes", roadmap; ranks for 19 of 25 German gap terms |

Benchmark against lto.org for the generation and "what is" terms, and against backupworks.com for drives.

## 3. The tape keyword universe (Ahrefs, Google US)

Of the 1,000 keywords, 594 are not about tape: the Philippine Land Transportation Office, fast-food "limited time offers", lithium titanate batteries, Leupold thermal trackers, compiler link-time optimisation, Ultrium rings. The remaining 406 tape keywords add up to about 19,100 searches a month. 7,400 of those are head terms such as "lto meaning", "lto" and "what is lto", where most searchers want something else; we count them but do not plan around them. That leaves about **11,700 addressable searches a month**.

| Cluster | Keywords | Searches/month | Top terms (volume / difficulty) | Target page | Action |
|---|---|---|---|---|---|
| Drives | 99 | 3,480 | lto tape drive 1,000/2, lto drive 250/6, lto 8 tape drive 70/3, ibm lto 9 tape drive 60/0 | /why-tape/lto-tape-drive | Rewrite as the drive buyer's guide |
| What is LTO (pillar) | 31 | 2,010 | lto tape 1,100/12, lto storage 150/0, lto tape storage 90/3, linear tape open 70/0 | /lto-tape | New |
| Generation pages | 66 | 1,700 | lto-9 100/12, lto 10 90/6, lto-8 80/8, lto 8 tape 70/4, lto-7 60/1 | /lto-tape-price-trend/lto{6..10}-price | Expand into full generation pages |
| Data recovery | 56 | 1,410 | lto tape data recovery 90, recover lto 4/5/6 30 each | /resources/lto-tape-data-recovery | New |
| Cartridges and brands | 19 | 520 | lto tapes 250/18, lto tape cartridge 50 | /lto-tape-brand | Extend |
| Capacity and sizes | 23 | 500 | lto 8 capacity 80/3, lto tape capacity 60/3, lto tape sizes 40/1 | /lto-tape-capacity | New (chart LTO-1 to LTO-14) |
| News | 5 | 390 | lto tape news 250, lto tape news today 70 | /lto-tape-news | New, monthly |
| Libraries and autoloaders | 21 | 380 | lto tape library 80/6, spectra / qualstar LTO-9 libraries | /lto-tape-library | New |
| LTFS | 8 | 320 | ltfs 250/18 | /resources/ltfs | New |
| Lifespan and shelf life | 13 | 240 | lto tape lifespan 40/0, how long do lto tapes last 20 | /why-tape/lto-tape-lifespan | New |
| Cleaning, labels, accessories | 14 | 200 | lto tape shredder 30, lto tape labels 20/0 | /resources/lto-cleaning-tapes-and-labels | New, low priority |
| Migration | 6 | 160 | lto-10 migration 30, lto tape data to cloud 30 | /resources/lto-tape-migration | Extend |
| Price and cost | 10 | 160 | lto price 40/26, lto calculator 30 | /lto-tape-price-trend, /backup-calculator | Keep fresh |
| Software | 4 | 90 | lto backup software 40/0 | /best-tape-backup-software | See note |
| Comparisons | 3 | 80 | lto tape vs hard drive 40 | /why-tape/lto-vs-hdd | Keep |
| Roadmap and LTO-11 | 7 | 70 | lto-11, lto 11 release date | /lto-tape-capacity + news | Section, not a page |

Note: this export was seeded with "linear tape open", so it under-counts backup software. Search Console shows "tape backup software" alone at 162 impressions a month at position 28. Pull a second Ahrefs export seeded with "tape backup" before planning that cluster.

Most of these terms have difficulty 0 to 12, so a page that answers them well can reach the top 10 without many links.

## 4. Work plan

### Phase 1, October: the big low-difficulty clusters (about 7,200 searches a month)
1. **Drive buyer's guide** at /why-tape/lto-tape-drive: drive per generation with current price range, internal vs external vs Thunderbolt/USB, read/write compatibility table, brand notes (HPE StoreEver, IBM, Quantum, Dell PowerVault, MagStor, OWC, mLogic), FAQ. Title aimed at "LTO tape drive".
2. **Generation pages**: turn the five price pages into the page for each generation (title pattern "LTO-9 tape: capacity, speed, compatibility and price 2026"). Add specs, compatibility, release year, drives that read it and the current price block. Keep the URLs and the price content so current price rankings carry over.
3. **/lto-tape pillar**: what LTO tape is, how it works, generations at a glance, capacity, lifespan, cost, who uses it; links to every generation page, the drive guide and the tracker.
4. **/lto-tape-capacity**: one chart, native and compressed for LTO-1 to LTO-10 plus the roadmap to LTO-14; answers "lto 8 capacity", "lto tape sizes" and similar.

### Phase 2, November: new topics we have no page for (about 2,500 searches a month)
5. **/resources/lto-tape-data-recovery**: reading old tapes (LTO-2 to LTO-6), which drive reads which generation, when to send tapes to a lab. 56 small keywords add up to 1,410 a month.
6. **/lto-tape-news**: a monthly post built from the price refresh (price moves, shipments, roadmap news). Gives us a reason to be cited and to be crawled often.
7. **/lto-tape-library**: small libraries and autoloaders (Quantum Scalar i3, Dell ML3, Spectra, Qualstar) with prices.
8. **/resources/ltfs**: what LTFS is, how to use it on Linux, macOS and Windows, which tools are free.
9. **/why-tape/lto-tape-lifespan**: the 30-year claim, storage conditions, load cycles, when to migrate.

### Phase 3, December: software, links, Europe
10. **Software page**: after the "tape backup" export, rebuild /best-tape-backup-software as an independent comparison table (Veeam, Commvault, Bacula, Iperius, BackupAssist, Nakivo, Catalogic, Uranium) with tape features and prices. Its competition is vendor blogs and thin listicles (gitnux, worldmetrics, wifitalents, zipdo).
11. **Links**: offer the monthly price index to storage press (Blocks & Files, The Register, TechRadar Pro, StorageNewsletter) and to forums (r/DataHoarder, ServeTheHome). DataCenterDisk is already quoted in the press for the same data.
12. **Europe**: translate every new page into the six languages. Germany first: lto.org owns "lto 9", "lto-10", "lto 8" and "lto tapes" there (up to 200 a month each), and our German generation pages currently target "Preis" only.

## 5. On every new or rewritten page
- Answer first (two sentences), then a table, then the detail; FAQ block with FAQPage schema.
- Internal links: pillar ↔ generation pages ↔ drive guide ↔ tracker; every new page links to the price for the generation it mentions.
- Titles at 60 characters or fewer and descriptions at 155 or fewer, in every language (the build's QA already checks this).
- Submit to IndexNow after each deploy.

## 6. Measuring it
- Monthly from Search Console: clicks and average position per cluster (keyword map CSV is the lookup).
- Targets for the end of December 2026: "lto tape drive" in the top 10, at least three generation terms ("lto-9", "lto 8", "lto-10") in the top 10, 300 clicks a month across the site.

## 7. Data still to get from Ahrefs
- Matching terms seeded with "tape backup" and with "tape drive" (software and broad drive demand).
- Top pages of lto.org and backupworks.com (which page wins which keyword).
- Content gaps for France, Italy, Spain, the Netherlands and Poland (same four competitors).
