"""Five buyer-question blog posts (October 2026), each with two figures from scripts/figs_blog_q4*.py.

    python3 scripts/blog_posts_2026_10.py

Numbers are September 2026 US seller-listing midpoints from data/prices-2026-09.json and the
5-year model on /comparisons/tape-vs-cloud-5-year-cost. Writes blog/<slug>/index.html, rebuilds
the blog listing and the homepage cards, then runs build_site.py.
"""

import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_blog_posts as G  # noqa: E402
import draw_figures  # noqa: E402
from site_shell import figure  # noqa: E402

_FIGS = draw_figures.all_figures()[0]


def fig(name, alt, cap):
    """A figure at the SVG's own size (read from its viewBox)."""
    w, h = re.search(r'viewBox="0 0 (\d+) (\d+)"', _FIGS[name]()).groups()
    return figure(name, alt, cap, int(w), int(h))

ROOT = Path(__file__).resolve().parent.parent
PUBLISHED = date(2026, 10, 12)


def tbl(headers, rows):
    th = "".join(f"<th>{h}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="table-wrap"><table class="post-table"><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>'


def faq(items):
    html = "<h2>Frequently asked questions</h2>" + "".join(f"<h3>{q}</h3><p>{a}</p>" for q, a in items)
    ld = {"@context": "https://schema.org", "@type": "FAQPage",
          "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in items]}
    # answers may hold links; the JSON-LD copy is plain text
    import re
    for e in ld["mainEntity"]:
        e["acceptedAnswer"]["text"] = re.sub(r"<[^>]+>", "", e["acceptedAnswer"]["text"])
    return html + f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>'


POSTS = []

# ------------------------------------------------------------------ 1. value per TB
POSTS.append(dict(
    slug="best-value-per-terabyte-tape-backup-us",
    title="Best Value per TB in Tape Backup, US 2026",
    description="Which tape backup systems give the best value per terabyte for long-term storage in the US? LTO-8, LTO-9 and LTO-10 compared on media and total cost.",
    category="Pricing",
    body=f"""<p><strong>On media alone, LTO-9 is the cheapest tape per terabyte in the US, at $5.14 to $6.20 per TB in September 2026. Once you count the drive, an LTO-8 system costs less per terabyte stored for almost any archive a single team runs, because an LTO-8 drive costs about $4,100 less than an LTO-9 drive. LTO-10 makes sense when density matters more than price.</strong></p>
<p>The figures below use the midpoint of new US seller listings from our <a href="/lto-tape-price-trend">LTO price tracker</a>, checked on 17 September 2026, before tax and shipping.</p>
<h2>Media cost per terabyte</h2>
<p>Cartridge price divided by native capacity is the number most comparisons quote. It favours the two newest mainstream generations by a wide margin over older ones.</p>
{tbl(["Generation", "Native capacity", "Cartridge price", "Per native TB"], [
    ["LTO-6", "2.5 TB", "$38 to $56", "$15.20 to $22.58"],
    ["LTO-7", "6 TB", "$60 to $80", "$10.00 to $13.33"],
    ["LTO-8", "12 TB", "$70 to $80", "$5.83 to $6.67"],
    ["<strong>LTO-9</strong>", "18 TB", "$92 to $112", "<strong>$5.14 to $6.20</strong>"],
    ["LTO-10", "30 TB", "$256 to $300", "$8.53 to $10.00"],
    ["LTO-10 (40 TB cartridge)", "40 TB", "$491 to $555", "$12.28 to $13.88"],
])}
{fig("blog-value-media-vs-drive.svg", "Media cost per TB by LTO generation next to the midpoint drive price for LTO-8, LTO-9 and LTO-10", "LTO-9 has the lowest media cost per terabyte, but its drive costs about $10,600 against $6,474 for LTO-8 and $23,558 for a full-height LTO-10 drive.")}
<h2>Total cost per terabyte stored</h2>
<p>A tape system is cartridges plus at least one drive. Spread the drive over the archive and the order changes. We count one copy, one drive below 500 TB and two drives from 500 TB, so a backup and a restore can run at the same time.</p>
{tbl(["Archive size", "LTO-8", "LTO-9", "LTO-10"], [
    ["100 TB", "<strong>$71 per TB</strong>", "$112 per TB", "$247 per TB"],
    ["500 TB", "<strong>$32 per TB</strong>", "$48 per TB", "$104 per TB"],
    ["1,000 TB", "<strong>$19 per TB</strong>", "$27 per TB", "$57 per TB"],
    ["2,000 TB", "<strong>$13 per TB</strong>", "$16 per TB", "$33 per TB"],
])}
{fig("blog-value-cost-per-tb.svg", "Total cost per TB stored for LTO-8, LTO-9 and LTO-10 from 50 TB to 2,000 TB", "Counting the drive, LTO-8 stays cheapest per terabyte stored at every size we checked, and the gap to LTO-9 narrows as the archive grows.")}
<p>LTO-9 saves about $0.58 per terabyte on media against LTO-8 at midpoint prices, while its drive costs about $4,100 more. It takes roughly 7 PB per drive before the media saving pays back the drive.</p>
<h2>Why many buyers still pick LTO-9</h2>
<p>Price per terabyte is not the only measure of value. LTO-9 needs 56 cartridges per petabyte against 84 for LTO-8, which means fewer library slots, fewer labels and less handling. An LTO-9 drive also reads and writes LTO-8 cartridges, so it carries an existing LTO-8 archive forward, while an LTO-8 drive reads back only to LTO-7. If you expect to grow past a few hundred terabytes or to buy a library, LTO-9 is usually the safer long-term choice. See the <a href="/lto-tape-price-trend/lto9-price">LTO-9 price guide</a> and the <a href="/lto-tape-price-trend/lto8-price">LTO-8 price guide</a>.</p>
<h2>Where LTO-10 fits</h2>
<p>LTO-10 holds 30 TB per cartridge, or 40 TB on the newer cartridge, so it packs the most data into a library slot. In September 2026 only full-height drives were on sale, at $22,165 to $24,950, and LTO-10 drives read LTO-10 only. That makes it a choice for large libraries short on slots rather than for value per terabyte. Details are in the <a href="/lto-tape-price-trend/lto10-price">LTO-10 price guide</a>.</p>
<h2>Older generations</h2>
<p>LTO-6 and LTO-7 cartridges cost two to four times as much per terabyte as LTO-9 and the drives are older stock. Buy them only to read or extend an archive you already have.</p>
{faq([
    ("What is the cheapest LTO tape per terabyte in 2026?", "LTO-9, at $5.14 to $6.20 per native TB from US sellers in September 2026. LTO-8 is close behind at $5.83 to $6.67."),
    ("Is LTO-8 still worth buying in 2026?", "For an archive below a few petabytes, yes on cost: the drive is about $4,100 cheaper than LTO-9. LTO-9 is the better long-term choice if you need fewer cartridges or want to read LTO-8 tapes in future."),
    ("When does LTO-10 give the best value?", "When library slots or floor space are the constraint. Per terabyte, LTO-10 media and drives cost more than LTO-9 at current prices."),
    ("Does compression change the cost per terabyte?", "Only for data that compresses. Vendors quote 2.5 to 1, but video, images and encrypted files store close to native capacity, so plan on native figures."),
]) }
<p>Size your own archive with the <a href="/backup-calculator">backup calculator</a>, or ask us for a <a href="/contact">volume quote on cartridges</a>.</p>""",
))

# ------------------------------------------------------------------ 2. five-year TCO
POSTS.append(dict(
    slug="tape-backup-5-year-total-cost-of-ownership",
    title="Tape Backup 5-Year TCO: Systems Compared",
    description="The tape backup systems with the lowest 5-year total cost of ownership, compared at 100 TB, 500 TB and 1 PB against cloud archive storage.",
    category="Pricing",
    body=f"""<p><strong>Over five years, an LTO-8 or LTO-9 system holding two copies is the cheapest way to keep 500 TB or more in the US: about $19,200 for LTO-8 and $26,900 for LTO-9 at September 2026 prices, against $27,660 for five years of Glacier Deep Archive before any restore. Below about 100 TB, cloud archive storage usually costs less unless you restore often.</strong></p>
<p>Our model counts what you buy once: cartridges for two copies and the drives (one below 500 TB, two from 500 TB). Prices are midpoints of new US seller listings from the <a href="/lto-tape-price-trend">price tracker</a>. The cloud figure is AWS S3 Glacier Deep Archive list pricing for US East, from our <a href="/comparisons/tape-vs-cloud-5-year-cost">tape vs cloud 5-year cost</a> page.</p>
<h2>Five-year cost compared</h2>
{tbl(["Archive", "LTO-8, two copies", "LTO-9, two copies", "LTO-10, two copies", "Glacier Deep Archive, 5 years", "One full Glacier restore"], [
    ["100 TB", "$7,824", "$11,824", "$25,781", "<strong>$5,532</strong>", "$8,615"],
    ["500 TB", "<strong>$19,247</strong>", "$26,911", "$56,567", "$27,660", "$43,074"],
    ["1,000 TB", "<strong>$25,545</strong>", "$32,623", "$66,019", "$55,321", "$86,147"],
])}
{fig("blog-tco-5yr.svg", "Five-year cost of LTO-8, LTO-9 and LTO-10 with two copies against Glacier Deep Archive at 100 TB, 500 TB and 1 PB", "Tape costs most of its money in year one and little after; cloud archive costs the same every month, and a full restore can cost more than the storage itself.")}
<p>Tape's cost is front-loaded and then nearly flat, so the longer you keep the data, the better tape looks. A cloud archive costs the same each month and charges again to read data back: one full restore of 500 TB from Glacier Deep Archive with bulk retrieval and internet egress costs about $43,074 on top of storage.</p>
<h2>Which tape system has the lowest TCO</h2>
{tbl(["System", "Best fit", "Five-year cost notes"], [
    ["Standalone LTO-8 drive", "Up to a few hundred TB, manual tape changes", "Lowest total cost today; drive about $6,474"],
    ["Standalone LTO-9 drive", "Growing archives, existing LTO-8 tapes", "About $4,100 more for the drive, fewer cartridges per PB"],
    ["Autoloader or small library", "Jobs that span several cartridges, unattended backups", "Adds the library chassis and a powered device; prices vary by model, see the <a href='/lto-tape-library'>library guide</a>"],
    ["LTO-10 full-height drive or library", "Very large archives short on slots", "Highest drive cost; pays off through density, not price"],
])}
<h2>What a full TCO also includes</h2>
<p>Our numbers leave out costs that depend on your setup, so add them for your own case: backup software licences, a library or autoloader, power, offsite storage for the second copy, staff time, and a migration to newer media when the drives near end of support.</p>
{fig("blog-tco-components.svg", "The cost blocks of a 5-year tape TCO, with drives and cartridges counted and the rest marked as not included", "Drives and cartridges are the part we price here. Software, a library, power, offsite storage, staff time and the next migration depend on your environment.")}
<p>Power is the smallest of these for tape: see our <a href="/blog/tape-backup-energy-use-and-operating-cost">energy and operating cost comparison</a>. Software is often the largest, so compare tape features in the <a href="/backup-software-finder">software finder</a>.</p>
{faq([
    ("Is tape cheaper than cloud over five years?", "From roughly 500 TB, yes in our model: two LTO-8 copies cost about $19,200 and two LTO-9 copies about $26,900, against $27,660 for five years of Glacier Deep Archive at 500 TB, before any restore fees."),
    ("What is not included in these tape costs?", "Software licences, a library or autoloader, power, offsite storage, staff time and the migration at the end of the drive's life."),
    ("How many tape drives do I need?", "One drive is enough for a small archive. From about 500 TB we count two, so a backup and a restore can run at the same time and a drive failure does not stop you."),
    ("When is LTO-10 the cheapest option?", "Not at current prices. LTO-10 costs more per terabyte in media and drives; it is chosen for density in large libraries."),
]) }""",
))

# ------------------------------------------------------------------ 3. encryption and security
POSTS.append(dict(
    slug="tape-backup-encryption-security-compared",
    title="Tape Encryption and Security, Side by Side",
    description="Which tape backup systems have the best encryption and security? AES-256 in LTO drives, key management options, WORM and air gap compared side by side.",
    category="Security",
    body=f"""<p><strong>Every LTO drive from LTO-4 onward encrypts in hardware with AES-256, whichever brand is on the front, so the drive is not what separates one tape system from another. What differs is how the encryption keys are managed: by the backup software, by the tape library through an external key manager, or by the host's tape driver. Add WORM cartridges and a copy that is offline when ejected, and tape covers the threats disk and cloud copies struggle with.</strong></p>
<h2>What every current LTO drive has</h2>
<p>Encryption, write-once media and the LTFS file system arrived in different generations and are part of the LTO standard, so they behave the same on HPE, IBM, Quantum and Dell drives of the same generation.</p>
{tbl(["Feature", "Since", "What it protects against"], [
    ["WORM cartridges", "LTO-3", "Overwriting or deleting data, including by ransomware or an insider"],
    ["AES-256 hardware encryption", "LTO-4", "Reading a lost or stolen cartridge"],
    ["LTFS partitions", "LTO-5", "Lock-in: the tape stays readable without the original backup software"],
    ["Offline when ejected", "All generations", "Anything that travels over the network"],
])}
{fig("blog-sec-features-by-gen.svg", "Security features by LTO generation: WORM from LTO-3, AES-256 encryption from LTO-4, LTFS partitions from LTO-5", "Any LTO-5 or newer drive supports all three. The drive compresses data before it encrypts it, so encryption does not reduce capacity.")}
<h2>The three ways to manage keys, compared</h2>
{tbl(["Method", "Where the key lives", "Good for", "Watch out for"], [
    ["Application-managed", "The backup software's database", "One backup product, simple setups", "Keys are tied to that software. Back up its key store, or a lost database means unreadable tapes"],
    ["Library-managed", "An external key manager the library reaches over KMIP", "Several applications sharing a library, audits and compliance", "Needs a key manager that is always reachable; on some library models it is a licensed feature"],
    ["System-managed", "A key manager reached by the host's tape device driver", "IBM environments", "Mostly limited to IBM drivers and platforms"],
])}
{fig("blog-sec-key-models.svg", "Application-managed, library-managed and system-managed encryption keys, each ending at an LTO drive with AES-256", "The drive encrypts the same way in all three. The choice is who holds the key: the backup software, a key manager through the library, or the host's driver.")}
<p>Whichever method you choose, the rule is the same: an encrypted cartridge without its key cannot be read, by you or anyone else. Keep the keys in at least two places, separate from the tapes.</p>
<h2>Tape, disk and cloud security side by side</h2>
{tbl(["", "LTO tape", "Disk backup", "Cloud object storage"], [
    ["Offline copy", "Yes, once ejected", "No, always online", "No, reachable with credentials"],
    ["Immutability", "WORM cartridges", "Immutable snapshots or hardened repositories, depending on product", "Object Lock in compliance mode"],
    ["Encryption at rest", "AES-256 in the drive", "Depends on array or software", "On by default at major providers"],
    ["Reachable by ransomware", "Only while mounted", "Yes, over the network", "Through stolen credentials or API keys"],
])}
<p>The strongest setups combine them: recent backups on disk for speed, and an encrypted tape copy that leaves the building. See <a href="/blog/offsite-tape-backups-still-beat-most-good-enough-plans">why offsite tape still wins</a> and our <a href="/comparisons">tape, disk and cloud comparison</a>.</p>
{faq([
    ("Does tape encryption reduce capacity or speed?", "Not noticeably. The drive compresses data first and then encrypts it in hardware, so native and compressed capacity stay the same."),
    ("Which LTO generations support hardware encryption?", "LTO-4 and every generation since, including LTO-9 and LTO-10, with AES-256."),
    ("Is WORM the same as encryption?", "No. WORM stops data from being changed or deleted; encryption stops it from being read without the key. For ransomware protection you usually want both."),
    ("What happens if I lose the encryption key?", "The data on that cartridge cannot be recovered. Store keys in a key manager or in your backup software's protected key store, with a copy kept away from the tapes."),
]) }""",
))

# ------------------------------------------------------------------ 4. energy and operating cost
POSTS.append(dict(
    slug="tape-backup-energy-use-and-operating-cost",
    title="Tape Backup Energy Use and Operating Cost",
    description="Which tape backup options are the most energy efficient, and how do they compare with disk and cloud on operating cost? A 500 TB model with assumptions.",
    category="Analysis",
    body=f"""<p><strong>A standalone LTO drive that is switched on only while it writes is the most energy-efficient way to keep an archive: a cartridge on a shelf uses no power at all. In our 500 TB model, a disk array kept online uses about 4,400 kWh a year, a small tape library left on all year about 800 kWh, and a standalone drive used only for writing about 16 kWh.</strong></p>
<p>Energy figures depend on your hardware, so below are the assumptions behind each number. Swap in the values from your own data sheets to redo the sums.</p>
<h2>How the options compare on energy</h2>
{tbl(["Option", "Assumption", "kWh per year"], [
    ["Disk array, always on", "32 hard drives of 20 TB (500 TB plus parity and spares) at about 7 W each, plus 50% for enclosure and controllers, plus 50% for cooling", "About 4,415"],
    ["Tape library, always on", "About 60 W idle for a small library with its drive, plus 50% for cooling, plus the writing below", "About 804"],
    ["Standalone tape drive, on only while writing", "One full 500 TB write a year at 400 MB/s (about 347 hours) at about 30 W, plus 50% for cooling", "About 16"],
    ["Cloud archive", "Energy is part of the provider's price", "Not billed separately"],
])}
{fig("blog-energy-kwh.svg", "Modelled energy use per year for a 500 TB archive on disk, a tape library, a standalone tape drive and cloud archive", "A disk array draws power around the clock; tape draws power only while a drive or library is switched on.")}
<h2>Operating cost per year</h2>
<p>At $0.13 per kWh, close to the US commercial average, the power bill is small for tape and noticeable for disk. For cloud archive storage, the monthly bill is the operating cost.</p>
{tbl(["Option, 500 TB", "Operating cost per year", "What drives it"], [
    ["Cloud archive (Glacier Deep Archive)", "About $5,532", "Storage billed every month; restores billed on top"],
    ["Disk array power", "About $574", "Drives, enclosures and cooling running all year; drives replaced every few years"],
    ["Tape library power", "About $105", "Library idle draw plus writing"],
    ["Standalone tape drive power", "About $2", "Only the hours spent writing"],
])}
{fig("blog-energy-opcost.svg", "Operating cost per year for 500 TB: cloud archive storage bill, disk array power, tape library power and standalone drive power", "For a 500 TB archive the cloud bill dwarfs any power bill, and tape's power cost is close to zero once cartridges leave the drive.")}
<h2>Other operating costs to plan for</h2>
<p>Power is only part of the picture. Disk arrays need drives replaced every three to seven years. Tape needs cleaning cartridges, offsite storage for the second copy, a periodic read check and a migration to newer media every two or three drive generations. Cloud adds retrieval and egress fees whenever you read data back.</p>
<p>The full five-year comparison, including hardware, is in <a href="/blog/tape-backup-5-year-total-cost-of-ownership">tape backup 5-year TCO</a>, and drive choices in the <a href="/why-tape/lto-tape-drive">LTO drive buyer's guide</a>.</p>
{faq([
    ("Does tape use power when it is stored?", "No. A cartridge on a shelf uses no electricity. Only the drive or library uses power, and only while it is switched on."),
    ("Is a tape library worth its extra power?", "Usually yes if jobs span several cartridges or run unattended. A small library adds tens of watts of idle draw, which costs roughly $100 a year in our model."),
    ("How can I cut tape energy further?", "Power down standalone drives between jobs, eject cartridges to the shelf, and schedule large writes together so the drive streams without stopping."),
    ("Is cloud storage more energy efficient than tape?", "You cannot measure it directly: the energy is inside the provider's price and data centre. For cold data, tape on a shelf uses less energy than any always-on system."),
]) }""",
))

# ------------------------------------------------------------------ 5. software integration
POSTS.append(dict(
    slug="tape-backup-software-integration-tradeoffs",
    title="Tape Backup Software Integration Tradeoffs",
    description="Which tape backup solutions integrate best with Veeam, Commvault, Nakivo and open-source tools, and what are the tradeoffs in format, catalogue and cost?",
    category="Software",
    body=f"""<p><strong>The tape systems that integrate best are the ones on your backup software's compatibility list. Current LTO drives and libraries from HPE, IBM, Quantum and Dell work with Veeam, Commvault and the other mainstream products when the exact model, firmware and host adapter are listed. The real tradeoffs sit in the software: built-in automation and a searchable catalogue against being able to read the tapes without that software.</strong></p>
<h2>How common backup software works with tape</h2>
{tbl(["Software", "Tape support", "Tape format", "Best for", "Tradeoff"], [
    ["Veeam Backup &amp; Replication", "Libraries and standalone drives; backup-to-tape and file-to-tape jobs with GFS retention", "Veeam's own", "Mostly virtual estates (VMware, Hyper-V)", "Tape is a second copy of disk backups; restores go through Veeam"],
    ["Commvault", "Libraries across a very wide range of platforms and workloads", "Commvault's own", "Large mixed physical, virtual and cloud estates", "Cost and complexity"],
    ["Nakivo", "Tape libraries, autoloaders and standalone drives", "Nakivo's own", "Small and mid-size environments", "Fewer enterprise features than the large suites"],
    ["Bacula / Bareos", "Libraries through an autochanger, standalone drives", "Open source", "Linux teams that run their own tooling", "You build and maintain scheduling, catalogue and monitoring"],
    ["LTFS tools", "Single drives, and libraries with some tools", "LTFS, an open standard", "Media archives, data exchange", "No catalogue across cartridges and no scheduling"],
])}
{fig("blog-int-software-map.svg", "Backup software products connected to library control, catalogue and tape format, feeding an LTO library", "Every product has to drive the library, keep a catalogue and choose a tape format; LTFS tools skip the catalogue, and open-source tools leave more of the work to you.")}
<h2>The tradeoffs that matter</h2>
<p><strong>Format.</strong> Most suites write their own tape format, so you need that software, or its recovery tools, to restore. LTFS keeps the files readable on any LTFS system, which matters for archives kept for decades. Some backup and archive products can write LTFS as an option.</p>
<p><strong>Catalogue.</strong> A suite's catalogue finds one file across hundreds of cartridges in seconds. Without it you are searching tape by tape. Back up the catalogue itself, ideally to the same tapes.</p>
<p><strong>Library control.</strong> Barcode inventory, mail slots for offsite tapes, cleaning and partitioning are handled by the software. Check that your library model, not only the drive, is supported.</p>
<p><strong>Encryption keys.</strong> If the software manages the keys, losing its database means losing access to encrypted tapes. See <a href="/blog/tape-backup-encryption-security-compared">tape encryption and security compared</a>.</p>
{fig("blog-int-tradeoffs.svg", "Tradeoff chart of automation and catalogue against restoring without the original software, for commercial suites, open source tools and LTFS", "Commercial suites give the most automation but tie restores to the software; LTFS gives the most portability with the least automation.")}
<h2>Integration checklist</h2>
{tbl(["Check", "Why"], [
    ["Drive and library on the compatibility list", "Model, firmware and host adapter must all be listed for support to apply"],
    ["Interface", "SAS for one host; Fibre Channel to share a library across a SAN"],
    ["Format option", "LTFS output if tapes must outlive the software"],
    ["Catalogue backup", "A restore without the catalogue means rescanning every cartridge"],
    ["Licensing model", "Per socket, per workload or per capacity changes the cost as the archive grows"],
])}
<p>Get a shortlist for your environment from the <a href="/backup-software-finder">tape backup software finder</a>, compare products in <a href="/best-tape-backup-software">best tape backup software 2026</a>, or read about the free route in the <a href="/resources/ltfs">LTFS guide</a>.</p>
{faq([
    ("Which tape drives work with Veeam and Commvault?", "Current LTO drives and libraries from the major brands are supported when the exact model and firmware are on the product's compatibility list. Check the list before you buy."),
    ("Can I read my tapes without the backup software?", "Only if they were written in LTFS or another open format. Most suites write their own format, so restores go through that software or its recovery tools."),
    ("Is LTFS enough on its own?", "For a small media archive, often yes. It lacks a catalogue across cartridges, scheduling and retention rules, which backup software provides."),
    ("Do I need a library to automate tape backups?", "Only when a backup spans more cartridges than fit in one drive. A single drive works for small archives if someone changes the tapes."),
]) }""",
))


def main():
    new = []
    for p in POSTS:
        words = len(p["body"].split())
        post = G.Post(slug=p["slug"], title=p["title"], description=p["description"], category=p["category"],
                      published=PUBLISHED, minutes=max(3, round(words / 200)), body_html=p["body"])
        d = ROOT / "blog" / post.slug
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(G.render_article(post))
        new.append(post)
        assert len(post.title) + len(" | TapeBackup.org") <= 60, post.title
        assert len(post.description) <= 155, (post.slug, len(post.description))
    slugs = {p.slug for p in new}
    others = [G.parse_existing_post(f) for f in sorted((ROOT / "blog").glob("*/index.html")) if f.parent.name not in slugs]
    posts = sorted(others + new, key=lambda x: (x.published, x.slug), reverse=True)
    (ROOT / "blog" / "index.html").write_text(G.render_listing(posts))
    home = [{"href": f"/blog/{p.slug}", "cat": p.category, "date": "Oct 2026", "h": p.title} for p in new[:3]]
    (ROOT / "data" / "home-blog.json").write_text(json.dumps(home, ensure_ascii=False, indent=2) + "\n")
    subprocess.run([sys.executable, str(ROOT / "scripts" / "build_site.py")], check=True)
    for p in new:
        print(p.published, p.slug, p.minutes, "min")


if __name__ == "__main__":
    main()
