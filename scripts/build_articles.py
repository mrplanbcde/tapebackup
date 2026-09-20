"""Hand-written article pages that answer searches no existing page covered.

Each entry supplies its own body HTML; the shared shell adds head, nav and footer.
Numbers come from data/prices-2026-09.json and data/price-history.json (via
build_prices) or from a cited source, so a price refresh updates them too.
"""

import json
import os

from build_prices import CURRENT_DATE_TEXT, CURRENT_LABEL, load, per_tb, rng, short_rng
from site_shell import ROOT, SITE, breadcrumb_ld, esc, faq_html, faq_ld, hubspot_cta, page, write

TODAY_ISO = "2026-09-20"


def sec(eyebrow, heading, body, anchor=None):
    a = f' id="{anchor}"' if anchor else ""
    return f'<section class="section-card"{a}><p class="eyebrow">{esc(eyebrow)}</p><h2>{esc(heading)}</h2>{body}</section>'


def table(headers, rows, label):
    th = "".join(f"<th>{esc(h)}</th>" for h in headers)
    tb = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="table-wrap"><table class="price-table" aria-label="{esc(label)}"><thead><tr>{th}</tr></thead><tbody>{tb}</tbody></table></div>'


def article(path, title, desc, h1, answer, eyebrow, sections, faqs, published, crumbs):
    body = f"""<section class="hero"><div class="container"><div class="hero-copy" style="max-width:900px">
<p class="eyebrow">{esc(eyebrow)}</p><h1 style="max-width:none">{esc(h1)}</h1>
<p><strong>{esc(answer)}</strong></p></div></div></section>
<main class="page"><div class="container"><div class="section-stack">
{''.join(sections)}
{hubspot_cta("Get the LTO pricebook", "Request current LTO media and drive pricing before you budget a migration or a refresh.")}
{faq_html(faqs, esc(h1) + " FAQ")}
</div></div></main>"""
    ld = [
        {"@context": "https://schema.org", "@type": "Article", "headline": h1, "description": desc,
         "datePublished": published, "dateModified": TODAY_ISO,
         "author": {"@type": "Organization", "name": "TapeBackup.org"},
         "publisher": {"@type": "Organization", "name": "TapeBackup.org", "url": SITE},
         "mainEntityOfPage": SITE + path},
        breadcrumb_ld(crumbs),
        faq_ld(faqs),
    ]
    write(path, page(path, title, desc, body, ld, hubspot=True, og_type="article"))
    return path


# ---------------------------------------------------------------- tape migration

def build_migration(current):
    g = current["generations"]
    path = "/resources/lto-tape-migration"
    l9, l10 = g["LTO-9"], g["LTO-10"]
    ex = []
    for src, tapes_src, tb, read_mbs in (("LTO-5 (1.5 TB)", 334, 500, 140), ("LTO-6 (2.5 TB)", 200, 500, 160), ("LTO-7 (6 TB)", 84, 500, 300)):
        n9 = -(-tb // 18)
        cost = f"${n9 * l9['cartridge']['lowUSD']:,.0f} to ${n9 * l9['cartridge']['highUSD']:,.0f}"
        hours = tb * 1e6 / (read_mbs * 3600) + tb * 1e6 / (400 * 3600)  # read at source speed, write at LTO-9 speed
        ex.append([src, f"{tapes_src} cartridges", f"{n9} LTO-9 cartridges", cost, f"{hours / 24:.0f} days on one drive pair"])

    sections = [
        sec("When to migrate", "Signs it is time to move an archive to newer media", """
<ul>
<li><strong>Your drive generation is going out of the market.</strong> New LTO-6 drives are effectively gone and several LTO-7 models now show call for availability. When a drive dies and cannot be replaced, the tapes it wrote become a recovery project.</li>
<li><strong>The compatibility window has closed.</strong> Each LTO drive reads one generation back (LTO-9 reads LTO-8), and LTO-10 drives read only LTO-10. An LTO-5 tape needs an LTO-5, LTO-6 or LTO-7 drive; nothing newer will mount it.</li>
<li><strong>Cartridge count is the real cost.</strong> 500 TB on LTO-5 is 334 cartridges to store, label, handle and eventually read back. The same archive is 28 LTO-9 cartridges.</li>
<li><strong>You cannot prove the archive is readable.</strong> If nothing has been restored from those tapes in years, a migration is also the verification pass you have been postponing.</li>
</ul>"""),
        sec("Cost and time", "What migrating 500 TB actually costs", f"""
<p>Media cost is the easy part to budget: divide the archive by the native capacity of the target generation and multiply by the cartridge price. At {CURRENT_DATE_TEXT}, LTO-9 media costs {rng(l9['cartridge'], True)} per 18 TB cartridge ({per_tb(l9['cartridge'])} per TB), and a new internal LTO-9 drive runs {rng(l9['driveInternal'], False)}.</p>
{table(["Source archive", "Cartridges today", "On LTO-9", "New media cost", "Read plus write time"], ex, "LTO migration cost examples")}
<p>The time column adds reading at the source generation's rated speed (LTO-5 up to 140 MB/s, LTO-6 160 MB/s, LTO-7 300 MB/s) to writing at LTO-9's 400 MB/s, running flat out with no stoppages. The old drive is usually the bottleneck, which is why the LTO-5 row takes about two thirds longer than the LTO-7 row for the same 500 TB. Run the read and the write on separate drives in parallel and you approach the slower of the two figures rather than their sum.</p>
<p>Budget for the things that are not media: a SAS HBA per drive, a server with enough disk to stage data if you are not copying tape to tape, backup software or LTFS tooling, and staff time to load cartridges unless you have a library.</p>"""),
        sec("How to do it", "A migration plan that does not lose data", """
<ol>
<li><strong>Inventory first.</strong> List every cartridge, its generation, its label and what your catalogue says is on it. Cartridges whose contents nobody can identify are the ones that turn a migration into an archaeology project.</li>
<li><strong>Decide the target generation.</strong> LTO-9 is the cheapest per terabyte and its drives still read LTO-8. LTO-10 halves the cartridge count again but costs more per terabyte and reads nothing older, so it suits a fresh archive better than a migration.</li>
<li><strong>Keep the old drive until the end.</strong> Do not decommission the only drive that can read your source media until the new copy is verified, and keep one working drive for the old generation afterwards if any tapes stay behind.</li>
<li><strong>Copy, then verify by reading back.</strong> Checksums written at copy time only prove what the buffer held. Read the new cartridges back and compare hashes against the source before you retire anything.</li>
<li><strong>Migrate the catalogue too.</strong> A perfect copy with no index is an unsearchable pile. Whether you use backup software or LTFS, make sure the new tapes are recorded where restores will actually look.</li>
<li><strong>Keep two copies during the move.</strong> The window where an archive exists only on cartridges that are being rewritten is the riskiest moment in its life.</li>
</ol>"""),
        sec("Tape to tape or via disk", "Two ways to move the data", """
<p><strong>Tape to tape</strong> needs two drives on one host and copies without a staging area. It is the simplest path when both generations are in the same library or on the same SAS bus, and it keeps the data under one tool's control the whole way.</p>
<p><strong>Through disk</strong> stages the source on a disk pool first, then writes the new cartridges. It is slower and needs the space, but it lets you deduplicate, re-catalogue, or repack many part-full old cartridges into full new ones, and it decouples a slow old drive from a fast new one.</p>
<p>Repacking matters more than it looks: an archive written years ago in small jobs often leaves cartridges half full, so the real cartridge count can be well above the raw capacity maths.</p>"""),
        sec("Outsourcing", "When to hand a migration to a service", """
<p>A service makes sense when nobody still has a working drive for the source generation, when the archive is large enough that months of drive time would block other work, or when a data centre move or shutdown puts a date on it. Ask any provider three things: how they verify each cartridge after writing, whether the chain of custody is documented for media leaving your site, and what happens to unreadable cartridges. The answers to those separate a migration service from a shipping company.</p>
<p>See the current <a href="/lto-tape-price-trend">LTO price tracker</a> for media and drive prices, and the <a href="/backup-calculator">backup calculator</a> to size the target generation.</p>"""),
    ]
    faqs = [
        ("Can an LTO-9 drive read LTO-6 tapes?", "No. LTO-9 drives read and write LTO-9 and LTO-8 media only. LTO-6 cartridges need an LTO-6, LTO-7 or LTO-8 drive, and LTO-8 drives read LTO-7 but not LTO-6, so keep a drive of the right generation until the migration is finished."),
        ("How long does it take to migrate 100 TB of tape?", "About six days of continuous copying on a single LTO-9 drive at 400 MB/s, counting the read and the write. Older source drives are slower: reading 100 TB from LTO-5 media takes roughly eight days on its own."),
        ("How much does it cost to migrate 500 TB to LTO-9?", f"Media alone is 28 cartridges, or {rng(l9['cartridge'], True)} each, which is about $2,600 to $3,200 in {CURRENT_LABEL}. Add a drive from {rng(l9['driveInternal'], False)} if you do not already have one, plus an HBA, software and staff time."),
        ("Should I migrate to LTO-9 or LTO-10?", f"LTO-9 for most migrations: it costs {per_tb(l9['cartridge'])} per TB against {per_tb(l10['cartridge'])} for LTO-10, and its drives still read your LTO-8 tapes. Choose LTO-10 when cartridge count or library slots matter more than media cost."),
        ("How do I verify a tape migration?", "Read every new cartridge back and compare checksums with the source, not just the checksums recorded at write time. Restore a sample of real files, confirm the new tapes are in the catalogue your restores use, and keep the source media until all of that passes."),
    ]
    return article(path, "LTO Tape Migration: Move an Archive to New Media",
                   "How to migrate an LTO archive to newer media: drive compatibility limits, cartridge counts, cost and time for 500 TB, and how to verify the copy.",
                   "LTO Tape Migration",
                   "Migrate an LTO archive before the drives that can read it disappear: LTO-9 drives read only LTO-9 and LTO-8, and LTO-10 drives read nothing older, so every generation you skip narrows the window for reading the old tapes.",
                   "Migration guide", sections, faqs, "2026-09-20",
                   [("Home", "/"), ("Resources", "/resources"), ("LTO tape migration", path)])


# ---------------------------------------------------------------- tape market

def build_market(current):
    path = "/resources/tape-storage-market"
    g = current["generations"]
    notes = {n["text"][:40]: n for n in current["marketNotes"]}
    src = lambda frag, label: next((f'<a href="{esc(n["url"])}" rel="nofollow noopener" target="_blank">{esc(label)}</a>' for k, n in notes.items() if frag in n["text"]), esc(label))
    ship = src("160.3 EB", "LTO Program")
    reg = src("only Sony and Fujifilm", "The Register")
    bf = src("2025 dip may reflect", "Blocks & Files")
    dd = src("largely stable at $4-6/TB", "DatacenterDisk")

    price_rows = [[gen, f"{g[gen]['nativeTB']:g} TB", esc(rng(g[gen]["cartridge"], True)), esc(per_tb(g[gen]["cartridge"]))] for gen in ["LTO-6", "LTO-7", "LTO-8", "LTO-9", "LTO-10"]]

    sections = [
        sec("Shipments", "How much tape capacity ships each year", f"""
<p>The LTO Program reports compressed capacity shipped each year. 2024 set a record at 176.5 EB. 2025 came in at 160.3 EB, about 9% lower, and the first quarter of 2026 shipped 57% more capacity than the same quarter a year earlier ({ship}).</p>
{table(["Year", "LTO capacity shipped", "Change"], [["2024", "176.5 EB", "Record"], ["2025", "160.3 EB", "Down about 9%"], ["Q1 2026", "Up 57% year over year", "LTO-9 volume plus the LTO-10 ramp"]], "LTO capacity shipped")}
<p>Two readings of the 2025 dip circulate. One ties it to trade uncertainty making buyers cautious ({reg}); the other suggests buyers were waiting for LTO-10 before committing to a new generation ({bf}). The Q1 2026 rebound supports the second.</p>"""),
        sec("Supply", "Only two companies make the tape", f"""
<p>Every LTO cartridge on the market contains tape made by Fujifilm or Sony ({reg}); HPE, IBM, Quantum and Dell put their names on media made by those two. That concentration is a risk when a plant or a material is disrupted, and it is also why tape pricing has not followed the hard drive market: {dd} reports tape holding at roughly $4 to $6 per TB through 2026 while hard drive prices rose sharply, because the tape supply chain sits outside the NAND shortage and hyperscale drive demand.</p>
<p>The 40 TB LTO-10 cartridge depends on an aramid base film, and its early price premium was blamed partly on tight supply of that film.</p>"""),
        sec("Prices", f"What LTO media costs now ({CURRENT_LABEL})", f"""
{table(["Generation", "Native capacity", "Cartridge price", "Per native TB"], price_rows, "LTO media prices")}
<p>LTO-9 is the cheapest media per terabyte on sale. Legacy generations cost more per terabyte, not less: LTO-6 now runs {per_tb(g['LTO-6']['cartridge'])} per TB against {per_tb(g['LTO-9']['cartridge'])} for LTO-9. Full listings, drive prices and every earlier snapshot are on the <a href="/lto-tape-price-trend">price tracker</a> and in the <a href="/lto-tape-price-trend/history">price history</a>.</p>"""),
        sec("Generations", "Where the format is going", """
<p>LTO-10 shipped in 2025 at 30 TB native, and a 40 TB cartridge for the same drives arrived in 2026. Two things make LTO-10 a bigger step than usual for buyers: the drives are full height only so far, and they do not read earlier generations at all, which breaks the one-generation-back rule every LTO buyer has relied on. The published roadmap continues past LTO-10, but roadmap capacities have historically been targets rather than dates.</p>
<p>For anyone planning an archive today, that makes LTO-9 the conservative choice and LTO-10 the density choice. See <a href="/resources/lto-tape-migration">LTO tape migration</a> for what the compatibility change means for old tapes.</p>"""),
        sec("Demand", "Who is actually buying tape", """
<p>The demand that shows up in shipment figures comes from a few places: hyperscale and cloud providers keeping cold data off spinning disk, AI teams retaining training corpora and checkpoints they cannot afford to keep on flash, media and entertainment archives, and regulated industries with retention mandates. What these have in common is data that must exist for years and is read rarely, which is the one workload where tape's economics and its offline nature both count.</p>"""),
    ]
    faqs = [
        ("Is the tape storage market growing or shrinking?", "Capacity shipped fell about 9% in 2025 to 160.3 EB after a record 176.5 EB in 2024, then rebounded with first-quarter 2026 shipments up 57% year over year. Measured in exabytes the market is growing over time, even though unit sales are concentrated in fewer, larger cartridges."),
        ("Who manufactures LTO tape?", "Only Fujifilm and Sony make the tape itself. HPE, IBM, Quantum and Dell sell cartridges containing media from those two manufacturers."),
        ("Why is tape cheaper than hard drives in 2026?", "Tape media held at roughly $4 to $6 per TB while hard drive prices rose sharply, because tape production is not competing for the same supply chain as drives and flash. The trade-off is that tape needs a drive up front and gives sequential rather than random access."),
        ("How big is an LTO-10 tape?", "30 TB native for the standard cartridge and 40 TB for the higher-capacity version introduced in 2026. Both work in the same LTO-10 drives, which do not read earlier generations."),
    ]
    return article(path, "Tape Storage Market 2026: Shipments, Supply, Prices",
                   "LTO tape market data for 2026: capacity shipped in 2025 and Q1 2026, why only two companies make tape, current media prices per TB and where LTO-10 fits.",
                   "Tape Storage Market in 2026",
                   "LTO shipments fell about 9% in 2025 to 160.3 exabytes, then rebounded with first-quarter 2026 capacity up 57% year over year, while media stayed at roughly $5 to $6 per terabyte as hard drive prices climbed.",
                   "Market data", sections, faqs, "2026-09-20",
                   [("Home", "/"), ("Resources", "/resources"), ("Tape storage market", path)])




# ---------------------------------------------------------------- 5-year TCO

SIZES = [50, 100, 500, 1000]
LTO9_TB = 18


def tape_cost(tb, g, copies):
    """One-off cost of an LTO-9 archive: cartridges plus drives (two drives from 500 TB)."""
    cart, drive = g["LTO-9"]["cartridge"], g["LTO-9"]["driveInternal"]
    n = -(-tb // LTO9_TB) * copies
    drives = 2 if tb >= 500 else 1
    return {"cartridges": n,
            "lo": n * cart["lowUSD"] + drives * drive["lowUSD"],
            "hi": n * cart["highUSD"] + drives * drive["highUSD"],
            "media_lo": n * cart["lowUSD"], "media_hi": n * cart["highUSD"],
            "drives": drives}


def cloud_year(tb, per_gb_month):
    return tb * 1000 * per_gb_month * 12


def breakeven_years(tape, per_year):
    return tape["lo"] / per_year, tape["hi"] / per_year


def build_tco(current):
    g = current["generations"]
    cloud = load("cloud-prices-2026-09.json")
    p = cloud["providers"]
    deep = p["aws_glacier_deep_archive"]
    path = "/comparisons/tape-vs-cloud-5-year-cost"
    per_gb = deep["storagePerGBMonth"]
    restore_per_gb = deep["retrievalPerGB"]["bulk"] + deep["egressPerGB"]

    rows = []
    for tb in SIZES:
        one, two = tape_cost(tb, g, 1), tape_cost(tb, g, 2)
        five = cloud_year(tb, per_gb) * 5
        lo, hi = breakeven_years(one, cloud_year(tb, per_gb))
        rows.append([f"<strong>{tb:,} TB</strong>",
                     f"${one['lo']:,.0f} to ${one['hi']:,.0f}<br><span class='updated-note'>{one['cartridges']} cartridges, {one['drives']} drive{'s' if one['drives'] > 1 else ''}</span>",
                     f"${two['lo']:,.0f} to ${two['hi']:,.0f}",
                     f"${five:,.0f}",
                     f"${tb * 1000 * restore_per_gb:,.0f}",
                     f"{lo:.1f} to {hi:.1f} years"])

    prov = []
    for key, label, url in (
        ("aws_glacier_deep_archive", "AWS S3 Glacier Deep Archive", "https://aws.amazon.com/s3/pricing/"),
        ("aws_glacier_flexible_retrieval", "AWS S3 Glacier Flexible Retrieval", "https://aws.amazon.com/s3/pricing/"),
        ("azure_blob_archive", "Azure Blob Storage Archive", "https://azure.microsoft.com/en-us/pricing/details/storage/blobs/"),
        ("gcs_archive", "Google Cloud Storage Archive", "https://cloud.google.com/storage/pricing"),
        ("backblaze_b2", "Backblaze B2", "https://www.backblaze.com/cloud-storage/pricing"),
        ("wasabi", "Wasabi", "https://wasabi.com/pricing"),
    ):
        x = p[key]
        gb = x.get("storagePerGBMonth") or (x.get("storagePerTBMonth", 0) / 1000)
        five = gb * 100 * 1000 * 12 * 5
        ret = x.get("retrievalPerGB") or x.get("dataRetrievalPerGB")
        if isinstance(ret, dict):
            ret_txt = f"${ret['bulk']:.4f} bulk, ${ret['standard']:.2f} standard" if "bulk" in ret else f"${ret['standard']:.2f} standard, ${ret['high']:.2f} high priority"
        elif isinstance(ret, (int, float)):
            ret_txt = f"${ret:.2f}" if ret else "none"
        else:
            ret_txt = "none"
        eg = x.get("egressPerGB")
        eg_txt = "free within policy" if eg == 0 else f"${eg:.3f}".rstrip("0")
        mind = x.get("minStorageDays")
        prov.append([f'<a href="{url}" rel="nofollow noopener" target="_blank">{esc(label)}</a>',
                     f"${gb:.5f}".rstrip("0"), f"${five:,.0f}", ret_txt, eg_txt,
                     f"{mind} days" if mind else "none"])

    t100, t500, t1000 = tape_cost(100, g, 1), tape_cost(500, g, 1), tape_cost(1000, g, 1)
    c100, c500 = cloud_year(100, per_gb) * 5, cloud_year(500, per_gb) * 5
    be100 = breakeven_years(t100, cloud_year(100, per_gb))
    be500 = breakeven_years(t500, cloud_year(500, per_gb))

    sections = [
        sec("The numbers", f"Five-year cost of keeping an archive, {CURRENT_LABEL} list prices", f"""
<p>Tape here is LTO-9 at {rng(g['LTO-9']['cartridge'], True)} per 18 TB cartridge plus a new internal drive at {rng(g['LTO-9']['driveInternal'], False)} (two drives from 500 TB up, so a copy can be read back while another is written). Cloud is AWS S3 Glacier Deep Archive at ${per_gb:.5f} per GB-month, one copy, kept for the full five years. The restore column is what it costs to pull the whole archive out of Glacier once, at bulk retrieval plus internet egress.</p>
{table(["Archive", "Tape, one copy", "Tape, two copies", "Glacier Deep Archive, 5 years", "One full restore from Glacier", "Break-even, one tape copy"], rows, "Five-year tape versus cloud archive cost")}
<p>These are list prices for media, drives and storage. They exclude racks, staff, software, cloud request charges and the disk you stage data on at either end.</p>"""),
        sec("Reading the table", "Cloud wins small, tape wins big", f"""
<p><strong>Below roughly 100 TB, cloud archive is cheaper over five years.</strong> A 100 TB archive costs about ${c100:,.0f} in Glacier Deep Archive for five years, while one tape copy costs ${t100['lo']:,.0f} to ${t100['hi']:,.0f}, most of it the drive. The tape only pays for itself after {be100[0]:.1f} to {be100[1]:.1f} years at that size.</p>
<p><strong>Around 500 TB the two meet.</strong> One tape copy of 500 TB costs ${t500['lo']:,.0f} to ${t500['hi']:,.0f} against ${c500:,.0f} for five years of Glacier, so tape is clearly cheaper at the low end of drive pricing and about level if you pay top of market. It breaks even in {be500[0]:.1f} to {be500[1]:.1f} years. At 1 PB the drive is a rounding error: media alone is ${t1000['media_lo']:,.0f} to ${t1000['media_hi']:,.0f}, a one-off cost against ${cloud_year(1000, per_gb) * 5:,.0f} of storage fees.</p>
<p>The reason is simple. A tape drive is a fixed cost that does not care how much data you have; cartridges then cost about {per_tb(g['LTO-9']['cartridge'])} per TB once. Cloud archive has no entry cost and bills every month forever.</p>"""),
        sec("Restores", "The number that changes the answer", f"""
<p>Reading an archive back from tape costs drive time. Reading it back from cloud archive costs money: pulling 100 TB out of Glacier Deep Archive is about ${100 * 1000 * restore_per_gb:,.0f} at bulk retrieval (${deep['retrievalPerGB']['bulk']:.4f} per GB) plus internet egress (${deep['egressPerGB']:.2f} per GB), and standard retrieval is ${deep['retrievalPerGB']['standard']:.2f} per GB instead of ${deep['retrievalPerGB']['bulk']:.4f}.</p>
<p>Two details decide whether that number ever lands on your invoice:</p>
<ul>
<li><strong>Retrieval tier.</strong> Bulk retrieval from Deep Archive takes up to 48 hours. If you need it faster you pay the standard rate, which is {deep['retrievalPerGB']['standard'] / deep['retrievalPerGB']['bulk']:.0f} times more per GB.</li>
<li><strong>Where the data goes.</strong> Egress is free to other services inside the same provider and charged when it leaves for the internet, so a restore into your own data centre costs full egress.</li>
</ul>
<p>Azure Archive carries the same ${p['azure_blob_archive']['storagePerGBMonth']:.5f} per GB-month headline as Deep Archive but has no bulk tier: retrieving 1 TB is ${1000 * p['azure_blob_archive']['dataRetrievalPerGB']['standard']:,.2f} at standard priority against ${1000 * deep['retrievalPerGB']['bulk']:,.2f} on AWS, before egress.</p>"""),
        sec("Provider prices", f"Cloud archive list prices, {cloud['asOf']}", f"""
{table(["Service", "$/GB-month", "100 TB for 5 years", "Retrieval per GB", "Egress per GB", "Minimum storage"], prov, "Cloud archive list prices")}
<p>US region list prices before committed-use discounts, taken from each provider's own pricing data on {cloud['asOf']}. Notes that matter when you model this yourself:</p>
<ul>
<li>Google prices per <strong>gibibyte</strong>, not gigabyte, which makes it about 7% more expensive than the raw number suggests.</li>
<li>Wasabi and Backblaze include egress only within a policy: Wasabi while monthly egress stays at or below what you store, Backblaze up to three times your average stored data.</li>
<li>Minimum storage duration bites on deletion. Delete from Deep Archive after a month and you still pay the remaining {deep['minStorageDays']} days; Google Archive charges a full year.</li>
<li>AWS adds {deep['perObjectOverheadKB']} KB of metadata to every archived object, so millions of small files cost far more than their raw size. Pack them into larger archives before upload.</li>
</ul>"""),
        sec("What the table leaves out", "Costs on both sides", """
<p><strong>Tape:</strong> a SAS HBA per drive, somewhere climate-controlled to keep cartridges, courier or vault fees for the offsite copy, backup software or LTFS tooling, a drive refresh every several years, and staff time to load, verify and label media. Budget one migration during a long retention period, because drives only read one generation back (see <a href="/resources/lto-tape-migration">LTO tape migration</a>).</p>
<p><strong>Cloud:</strong> upload requests, minimum storage duration, early-deletion fees, retrieval tiers, egress, and the chance that list prices change during a ten-year retention. The full restore cost belongs in the budget even if you never plan to use it, because that is what a disaster looks like.</p>
<p><strong>Both:</strong> the staging disk at each end, and the second copy you should keep either way. Most teams end up with disk for recent restores, tape for offline retention and a cloud copy for site loss, which is the <a href="/comparisons">3-2-1 split</a> rather than a single winner.</p>"""),
    ]
    faqs = [
        ("Is tape cheaper than cloud storage?", f"It depends on size and retention. At 100 TB over five years, AWS S3 Glacier Deep Archive costs about ${c100:,.0f} against ${t100['lo']:,.0f} to ${t100['hi']:,.0f} for one LTO-9 tape copy including a drive, so cloud is cheaper. At 500 TB tape costs ${t500['lo']:,.0f} to ${t500['hi']:,.0f} against ${c500:,.0f} for cloud, so tape is level or cheaper, and by 1 PB it is less than half the cost."),
        ("What does it cost to restore 100 TB from Glacier Deep Archive?", f"About ${100 * 1000 * restore_per_gb:,.0f} at {CURRENT_LABEL} list prices: ${deep['retrievalPerGB']['bulk']:.4f} per GB for bulk retrieval plus ${deep['egressPerGB']:.2f} per GB of internet egress. Standard retrieval costs ${deep['retrievalPerGB']['standard']:.2f} per GB instead."),
        ("How long before a tape drive pays for itself?", f"At 100 TB, {be100[0]:.1f} to {be100[1]:.1f} years against Glacier Deep Archive. At 500 TB, {be500[0]:.1f} to {be500[1]:.1f} years. The drive is a fixed cost, so the more you store the faster it is repaid."),
        ("How many LTO-9 tapes is 1 PB?", f"{-(-1000 // LTO9_TB)} cartridges for one copy at 18 TB native each, about ${t1000['media_lo']:,.0f} to ${t1000['media_hi']:,.0f} of media. Compression does not help for already-compressed archive data."),
        ("Which cloud archive tier is cheapest?", f"AWS S3 Glacier Deep Archive and Azure Blob Archive share the lowest headline rate at ${per_gb:.5f} per GB-month, but AWS is far cheaper to read back because it offers a bulk retrieval tier. Wasabi and Backblaze cost more per month and include egress within policy limits."),
    ]
    return article(path, "Tape vs Cloud: 5-Year Archive Cost Compared",
                   f"What a 50 TB to 1 PB archive costs over five years on LTO-9 tape versus AWS Glacier Deep Archive, Azure, Google and others, with {cloud['asOf']} list prices.",
                   "Tape vs Cloud: The Five-Year Cost of an Archive",
                   f"Over five years, 100 TB costs about ${c100:,.0f} in AWS S3 Glacier Deep Archive against ${t100['lo']:,.0f} to ${t100['hi']:,.0f} for one LTO-9 tape copy including the drive, but at 500 TB tape costs ${t500['lo']:,.0f} to ${t500['hi']:,.0f} against ${c500:,.0f} for cloud.",
                   "Cost comparison", sections, faqs, "2026-09-20",
                   [("Home", "/"), ("Comparisons", "/comparisons"), ("Tape vs cloud 5-year cost", path)])


def build_all(current):
    return [build_migration(current), build_market(current), build_tco(current)]
