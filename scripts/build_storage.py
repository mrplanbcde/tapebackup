"""LTO storage pages from docs/seo/lto-storage-keyword-plan-2026-10.md (N1 to N4).

    /lto-storage                          N1 pillar: LTO as a storage tier
    /resources/how-to-store-lto-tapes     N2 conditions, cases, cabinets, racks, offsite
    /resources/owc-lto-tape-drives        N3 OWC Mercury Pro and Archive Pro
    /comparisons/lto-vs-object-storage    N4 tape vs S3-style object storage

Prices come from the current market (build_prices) and data/cloud-prices-2026-09.json;
vendor facts come from data/research/storage-pages-2026-10.json (sources kept there).
Figures are drawn by scripts/figs_storage.py.
"""

import json
import os

import build_prices as BP
from build_articles import article, cloud_data, sec, table
from build_guides import drive_rng, link_grid, more_guides, spec_rows
from build_prices import GENS, SPECS, date_text, per_tb, rng
from site_shell import ROOT, esc, figure

PUBLISHED = "2026-10-17"


def research():
    p = os.path.join(ROOT, "data", "research", "storage-pages-2026-10.json")
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}


def _where():
    return "" if BP.MKT.is_us else f" in {BP.MKT.country}"


def cost_rows(g):
    rows = []
    for x in GENS:
        c = g[x]["cartridge"]
        rows.append([f'<a href="/lto-tape-price-trend/{x.lower().replace("-", "")}-price">{x}</a>', SPECS[x]["native"], rng(c, True), per_tb(c), drive_rng(g[x].get("driveInternal"))])
    return rows


# ---------------------------------------------------------------- N1 pillar

def build_pillar(current):
    path = "/lto-storage"
    g = current["generations"]
    l9, l10 = g["LTO-9"], g["LTO-10"]
    where = _where()
    sections = [
        sec("Definition", "What LTO storage is", """
<p>LTO storage means keeping data on LTO (Linear Tape-Open) magnetic tape cartridges instead of on disks or in a cloud service. A drive writes the data to a cartridge, and the cartridge then sits in a library slot or on a shelf, powered off, until the data is needed again. It is the usual choice for archives, long-term backup copies and offline copies that ransomware cannot reach.</p>
<p>LTO is an open standard set by HPE, IBM and Quantum, so cartridges and drives of the same generation work together whatever the brand. The format itself is explained on <a href="/lto-tape">what is LTO tape</a>; this page is about using it as storage.</p>"""),
        sec("How it works", "How LTO tape storage works", f"""
{figure("lto-storage-how-it-works.svg", "An LTO cartridge with its single reel, the tape running past the drive head, and bands of tracks written back and forth along the tape between servo bands", "Each cartridge holds one reel of half-inch tape. The drive pulls the tape past its head and writes a band of parallel tracks along the whole length, then reverses and writes the next set on the way back. Servo bands written at the factory keep the head on track.", 960, 430)}
<ul>
<li><strong>One reel per cartridge.</strong> When a cartridge is loaded, the drive pulls the tape out by its leader pin and winds it onto a reel inside the drive.</li>
<li><strong>Linear serpentine recording.</strong> The head writes many tracks at once while the tape streams past, then shifts slightly and writes in the opposite direction. A full cartridge is written in many such end-to-end passes.</li>
<li><strong>Servo tracks.</strong> Factory-written servo bands let the head follow the tape precisely, which is what allows thousands of tracks on half an inch of tape.</li>
<li><strong>Verify while writing.</strong> The drive reads each block back just after writing it and rewrites it if needed, and every block carries error correction.</li>
<li><strong>Compression and encryption in the drive.</strong> Drives compress data on the fly and, from LTO-4 onward, can encrypt it with AES-256.</li>
<li><strong>Cartridge memory.</strong> A small chip in each cartridge records its history, such as how often it was loaded.</li>
</ul>
<p>Because the tape is read in order, finding one file means winding to it, which takes tens of seconds to a couple of minutes. Reading or writing large amounts in sequence is fast: an LTO-9 drive streams up to {SPECS['LTO-9']['speed']} MB/s native.</p>"""),
        sec("The parts", "What an LTO storage system is made of", f"""
{figure("lto-storage-system.svg", "A server with backup or LTFS software connected over SAS or Fibre Channel to an LTO drive or library with cartridges, and a second set of cartridges kept offsite", "A working LTO storage system needs five things: cartridges, a drive or library, a server with the right connection, software that writes to tape, and somewhere safe to keep the second copy.", 960, 420)}
{table(["Part", "What it does", "Guide"], [
    ["Cartridges", "Hold the data; one generation per drive family", '<a href="/lto-tape-price-trend">LTO prices</a>'],
    ["Drive", "Reads and writes cartridges; internal, external or in a library", '<a href="/why-tape/lto-tape-drive">Drive buying guide</a>'],
    ["Library or autoloader", "Holds many cartridges and loads them with a robot", '<a href="/lto-tape-library">LTO tape libraries</a>'],
    ["Server and connection", "SAS or Fibre Channel, or Thunderbolt for desktop drives", '<a href="/why-tape/lto-tape-drive">Interfaces</a>'],
    ["Software", "Backup or archive software, or LTFS to use tape like a disk", '<a href="/backup-software-finder">Software finder</a>'],
    ["A place for the second copy", "Offsite storage protects against fire, flood and theft", '<a href="/resources/how-to-store-lto-tapes">How to store LTO tapes</a>'],
], "Parts of an LTO storage system")}"""),
        sec("Capacity", "How much an LTO cartridge stores", f"""
{table(["Generation", "Released", "Native capacity", "Compressed", "Native speed"], spec_rows(GENS), "LTO storage capacity by generation")}
<p>Plan with the native figure. Compressed capacity assumes data that compresses 2.5 to 1, and video, photos, encrypted files and existing backups barely compress. An LTO-6 cartridge, still common in older archives, holds 2.5 TB native. Every generation from LTO-1 to the LTO-14 roadmap is in the <a href="/lto-tape-capacity">LTO capacity chart</a>.</p>"""),
        sec("Cost", "LTO tape storage cost per TB in 2026", f"""
{table(["Generation", "Native capacity", "Cartridge price", "Cost per TB", "Internal drive"], cost_rows(g), "LTO storage cost per TB")}
<p>Prices are new seller listings{where} checked on {date_text()}. LTO-9 is the cheapest media per terabyte at {per_tb(l9['cartridge'])}; LTO-10 costs {per_tb(l10['cartridge'])} per TB. The drive is the large fixed cost, so the cost per terabyte of the whole system falls the more data you store. For a full five-year comparison with cloud archive storage, see <a href="/comparisons/tape-vs-cloud-5-year-cost">tape vs cloud cost</a>, and for your own numbers use the <a href="/backup-calculator">backup calculator</a>.</p>"""),
        sec("Fit", "When LTO storage is the right choice", """
<p><strong>Good fit:</strong> archives that grow by tens of terabytes or more, a second or third backup copy that must be offline, data you must keep for years (research data, video masters, medical images, records), and anyone who wants storage with no monthly bill and no power draw while idle.</p>
<p><strong>Poor fit:</strong> small data sets below roughly 15 TB, where disks or cloud storage cost less than a drive; data that users open every day; and teams with nobody to handle cartridges, rotation and restore tests. For those, disk or object storage usually works better. See <a href="/comparisons/lto-vs-object-storage">LTO vs object storage</a> and <a href="/comparisons">tape, disk and cloud compared</a>.</p>"""),
        sec("Keeping cartridges", "How LTO cartridges should be stored", """
<p>For long-term storage, keep cartridges cool, dry and stable, in their cases, standing on edge, away from dust, sunlight and strong magnetic fields, and give them time to adjust to the room before loading them in a drive. Keep a second copy at another site. The full checklist, with temperature and humidity figures, cases, cabinets, racks and offsite rotation, is in <a href="/resources/how-to-store-lto-tapes">how to store LTO tapes</a>.</p>"""),
        sec("Choosing software", "Which software writes to LTO storage", """
<p>Backup software such as Veeam or Commvault treats tape as a target for backup copies. Archive software moves files to tape and keeps a catalogue, and LTFS lets a single cartridge be mounted like a disk. To compare backup products, use the <a href="/backup-software-finder">tape backup software finder</a>; for archive products, try the <a href="/tape-archive-advisor">tape archive advisor</a>.</p>"""),
        more_guides(path),
    ]
    faqs = [
        ("What is LTO storage?", "LTO storage is keeping data on LTO (Linear Tape-Open) tape cartridges. A drive writes the data, and the cartridges sit in a library or on a shelf, powered off, until the data is needed. It is used for archives, long-term backup copies and offline copies."),
        ("How does LTO tape storage work?", "The drive pulls the tape from the cartridge past its head, writes bands of parallel tracks along the whole tape, then reverses and writes the next band, guided by factory-written servo tracks. It verifies each block as it writes and can compress and encrypt the data."),
        ("How much data can LTO storage hold?", f"An LTO-9 cartridge holds 18 TB native and an LTO-10 cartridge 30 TB, or 40 TB on the newer cartridge. LTO-8 holds 12 TB and LTO-6 2.5 TB. A library multiplies that by its number of slots."),
        ("How much does LTO tape storage cost per TB in 2026?", f"LTO-9 media costs about {per_tb(l9['cartridge'])} per TB{where} as of {date_text()}, the lowest of any generation, and LTO-10 about {per_tb(l10['cartridge'])}. A drive adds a fixed cost of {drive_rng(l9.get('driveInternal'))} for a new internal LTO-9 drive."),
        ("What is an LTO storage system?", "Cartridges, a drive or tape library, a server connected by SAS, Fibre Channel or Thunderbolt, backup or archive software or LTFS, and a place to keep the second copy offsite."),
        ("Is LTO storage still used?", "Yes. LTO shipped 160.3 exabytes of capacity in 2025 and shipments rose 57% in the first quarter of 2026, mainly for archives, AI training data and offline backup copies."),
    ]
    return article(path, "LTO Storage: How LTO Tape Stores Data, Capacity and Cost",
                   "What LTO storage is, how LTO tape storage works, the parts of an LTO storage system, capacity by generation and the 2026 cost per TB.",
                   "LTO Storage Explained",
                   f"LTO storage keeps data on LTO tape cartridges that sit powered off in a library or on a shelf: an LTO-9 cartridge stores 18 TB native for about {per_tb(l9['cartridge'])} per TB{where}, cartridges are rated for 30 years, and a copy on the shelf is out of reach of ransomware.",
                   "LTO storage guide", sections, faqs, PUBLISHED, [("Home", "/"), ("LTO storage", path)])


# ---------------------------------------------------------------- N4 LTO vs object storage

def cloud_extra():
    """S3 Standard and Backblaze B2 list prices from data/research/storage-pages-2026-10.json (None when not verified)."""
    c = research().get("cloud", {})
    s3 = c.get("awsS3", {})
    st, eg = s3.get("storageStandardFirst50TB_usEast1", {}), s3.get("egressInternetFirst10TB_usEast1", {})
    b2 = c.get("backblazeB2", {})
    return {"s3_gb": st.get("value"), "s3_egress": eg.get("value"), "s3_url": st.get("humanPage", "https://aws.amazon.com/s3/pricing/"),
            "b2_tb": b2.get("storage", {}).get("value"), "b2_egress": "Free up to 3x the data stored, then $0.01/GB" if b2.get("egressRule") else None,
            "b2_url": b2.get("storage", {}).get("url", "https://www.backblaze.com/cloud-storage/pricing"), "seen": st.get("seen")}


def build_lto_vs_object(current):
    from build_articles import GIB_PER_TB, BINARY_TB, tape_cost
    from build_prices import money0
    path = "/comparisons/lto-vs-object-storage"
    g = current["generations"]
    l9 = g["LTO-9"]
    M = BP.MKT
    conv = M.from_usd
    cloud, region = cloud_data()
    p = cloud["providers"]
    ex = cloud_extra()
    tb = 100
    two = tape_cost(tb, g, 2)
    five = lambda gb: money0(conv(gb * GIB_PER_TB * tb * 12 * 5))
    rows = [[f"LTO-9 tape, two copies (<a href=\"/lto-tape-price-trend/lto9-price\">prices</a>)", f"{money0(two['lo'])} to {money0(two['hi'])} once",
             "Minutes in a library, longer from a shelf", "None; you own the cartridges"]]
    if ex["s3_gb"]:
        rows.append([f'<a href="{ex["s3_url"]}" rel="nofollow noopener" target="_blank">AWS S3 Standard</a>', five(ex["s3_gb"]), "Milliseconds", f"${ex['s3_egress']}/GB egress" if ex["s3_egress"] else "Egress charged"])
    w = p.get("wasabi", {})
    if w.get("storagePerGBMonth"):
        rows.append(['<a href="https://wasabi.com/pricing" rel="nofollow noopener" target="_blank">Wasabi</a>', money0(conv(w["storagePerGBMonth"] * 1000 * BINARY_TB["wasabi"] * tb * 12 * 5)), "Milliseconds", "No egress fee within its policy; 90-day minimum"])
    if ex["b2_tb"]:
        rows.append([f'<a href="{ex["b2_url"]}" rel="nofollow noopener" target="_blank">Backblaze B2</a>', money0(conv(ex["b2_tb"] * tb * 12 * 5)), "Milliseconds", ex["b2_egress"] or "See pricing page"])
    fl, da = p["aws_glacier_flexible_retrieval"], p["aws_glacier_deep_archive"]
    rows.append(['<a href="https://aws.amazon.com/s3/pricing/" rel="nofollow noopener" target="_blank">AWS S3 Glacier Flexible Retrieval</a>', five(fl["storagePerGBMonth"]), "Minutes to hours", "Retrieval and egress fees; 90-day minimum"])
    rows.append(['<a href="https://aws.amazon.com/s3/pricing/" rel="nofollow noopener" target="_blank">AWS S3 Glacier Deep Archive</a>', five(da["storagePerGBMonth"]), "Hours", "Retrieval and egress fees; 180-day minimum"])
    where = _where()
    restore = money0(conv(tb * GIB_PER_TB * (da["retrievalPerGB"]["bulk"] + da["egressPerGB"])))
    sections = [
        sec("The short answer", "LTO tape or object storage?", f"""
<p>Object storage (Amazon S3 and services that speak the same API, in the cloud or on your own servers) keeps every object online behind an API, so any application can read it in milliseconds. LTO tape keeps data on cartridges that are mostly offline, so a read takes minutes in a library, but each terabyte costs a fraction of standard object storage to keep for years, and a cartridge on a shelf is out of reach of attacks on the network.</p>
<p>Most organisations that hold a lot of data use both: object storage for data that is read often, and tape for the archive and the offline copy. Several products now present tape itself through an S3 interface, which is covered below.</p>"""),
        sec("Access and cost", "Access time against cost per terabyte", figure("lto-vs-object-access-cost.svg", "A chart of time to first byte against cost per terabyte: S3 Standard and Wasabi are fast and dear, Glacier Flexible and Deep Archive are cheap and slow, LTO in a library is cheap and answers in minutes, LTO on a shelf is cheapest", "Object storage classes answer in milliseconds and cost the most per terabyte; cloud archive classes are cheap but take hours to restore; LTO tape in a library answers in minutes at the lowest cost per terabyte. The positions are schematic, not to scale.", 960, 420)),
        sec("Cost", f"Five years of {tb} TB: tape against object storage", f"""
{table(["Option", f"{tb} TB for 5 years", "Time to first byte", "Getting data out"], rows, "LTO tape vs object storage cost")}
<p>Tape: two copies of {tb} TB on LTO-9 cartridges plus {two['drives']} internal drive{'s' if two['drives'] > 1 else ''}, at new seller prices{where} checked on {date_text()}; the cartridges are bought once. Cloud: list storage prices for {region} times five years, before request, retrieval and egress fees{", checked on 17 October 2026" if ex['seen'] == "2026-10-17" else (f", checked on {ex['seen']}" if ex['seen'] else "")}. Reading all {tb} TB back out of Glacier Deep Archive with bulk retrieval and internet egress adds about {restore}. Object storage keeps one logical copy across several devices or sites; tape keeps exactly the copies you make, so the two-copy figure is the fair comparison.</p>
<p>For more sizes and every cloud archive tier, see <a href="/comparisons/tape-vs-cloud-5-year-cost">tape vs cloud: 5-year cost</a>.</p>"""),
        sec("Side by side", "How they differ beyond price", table(["", "LTO tape", "Object storage"], [
            ["Access", "Sequential; load a cartridge, wind to the data", "Random access to any object through an HTTP API"],
            ["Time to first byte", "About one to two minutes in a library", "Milliseconds for standard classes, hours for cloud archive classes"],
            ["Throughput", f"Up to {SPECS['LTO-9']['speed']} MB/s native per LTO-9 drive, more with more drives", "Scales with parallel requests and network bandwidth"],
            ["Ransomware protection", "Offline cartridges are physically out of reach; WORM media cannot be rewritten", "Object Lock or immutability settings, enforced by the service"],
            ["Ongoing cost", "Almost none once written; no power while on a shelf", "A monthly charge for every terabyte, plus requests and egress"],
            ["Lock-in", "Open LTO format and LTFS; plan migrations every few generations", "API is standard, but egress fees make leaving expensive at scale"],
            ["Skills", "Cartridge handling, rotation, restore tests", "Buckets, access keys, lifecycle policies"],
        ], "LTO tape and object storage compared")),
        sec("Both at once", "S3 on top of tape", f"""
<p>An S3-to-tape gateway accepts objects through the S3 or S3 Glacier API and writes them to LTO cartridges in a library, often keeping recent objects on disk. Applications that already speak S3 can then archive to tape without tape-specific software. Examples scored in our Ledger include Spectra BlackPearl, Grau Data XtreemStore, PoINT Archival Gateway, Versity ScoutAM with its S3 gateway, and QStar. To compare them for your own data size and team, try the <a href="/tape-archive-advisor">tape archive advisor</a>.</p>"""),
        sec("Decision", "When to choose which", f"""
<ul>
<li><strong>Choose object storage</strong> when applications read the data often, when you need it from anywhere, or when the data set is small (below roughly 15 TB, a drive costs more than years of cloud storage).</li>
<li><strong>Choose LTO tape</strong> for archives that grow by tens of terabytes or more, for data you must keep for many years, and for the offline copy in a 3-2-1 plan.</li>
<li><strong>Use both</strong> when the archive must be reachable by S3 applications but stored cheaply: put an S3-to-tape gateway in front of a library, or keep hot data in object storage and tier the rest to tape.</li>
</ul>
<p>How LTO storage works and what it costs per terabyte today is in <a href="/lto-storage">LTO storage explained</a>.</p>"""),
        more_guides(path),
    ]
    faqs = [
        ("Is LTO tape cheaper than object storage?", f"Than standard object storage such as S3 Standard or Wasabi, yes, by a wide margin: two copies of {tb} TB on LTO-9 cost {money0(two['lo'])} to {money0(two['hi'])} once{where}, drive included. Against cloud archive tiers it depends on size and restores: five years of {tb} TB in Glacier Deep Archive costs {five(da['storagePerGBMonth'])} in storage, less than tape, but reading it all back once adds about {restore}. From about 500 TB, or with regular restores, tape costs less."),
        ("Is LTO tape faster than object storage?", "For streaming large files, an LTO-9 drive writes up to 400 MB/s native. For the first byte of a random file, object storage is far faster: milliseconds against about a minute or two for tape in a library."),
        ("Can I use S3 with tape?", "Yes. S3-to-tape gateways such as Spectra BlackPearl, Grau Data XtreemStore and PoINT Archival Gateway accept S3 or S3 Glacier requests and store the objects on LTO cartridges."),
        ("Is object storage safe from ransomware?", "It can be, with Object Lock or immutability enabled and strict access keys. Tape adds a physical air gap: a cartridge on a shelf cannot be reached over the network at all."),
        ("Should I replace tape with object storage?", "Usually not completely. Many sites keep frequently used data in object storage and use tape for the archive and the offline copy, because tape costs less per terabyte the longer data is kept."),
    ]
    return article(path, "LTO Tape vs Object Storage (S3): Cost, Speed, Safety",
                   f"LTO tape vs object storage compared: five-year cost for {tb} TB, time to first byte, ransomware protection, lock-in and S3-to-tape gateways.",
                   "LTO Tape vs Object Storage",
                   f"Object storage answers in milliseconds but charges every month; LTO tape answers in minutes from a library but two copies of {tb} TB on LTO-9 cost {money0(two['lo'])} to {money0(two['hi'])} once{where}, and offline cartridges are out of reach of ransomware, so most large archives use both.",
                   "Comparison", sections, faqs, PUBLISHED, [("Home", "/"), ("Comparisons", "/comparisons"), ("LTO vs object storage", path)])


# ---------------------------------------------------------------- N2 how to store LTO tapes

# Media specs from vendor data sheets; filled from data/research/storage-pages-2026-10.json, source URLs kept there.
IBM_SHEET = "https://www.ibm.com/downloads/documents/es-es/107a02e95dc8f8a9"
FUJI_SHEET = "https://asset.fujifilm.com/www/us/files/2024-01/ce72cf783970aa0d05d4463e4febcb62/FB_LTO9_SellSheet_V1.pdf"
OT_GUIDE = "https://www.overlandtandberg.com/MVImages/channel_newsletters/10_23/LTO_Tape_Handling_Guide.pdf"
IBM_HANDLING = "https://www.ibm.com/docs/en/STAKKZ/con_LTOdrive_cartridges_handling_environment.html"
DELL_KB = "https://www.dell.com/support/kbdoc/en-au/000122049/how-to-handle-backup-tapes"
COND = {
    "rows": [
        ("Long-term (archival) storage", {"temp": "16 to 25 °C (61 to 77 °F)", "rh": "20 to 50%", "note": "IBM recommended storage; Fujifilm long term"}),
        ("Shorter-term storage", {"temp": "16 to 32 °C (61 to 90 °F)", "rh": "20 to 80%", "note": "IBM allowable storage; Fujifilm allows up to 35 °C short term"}),
        ("In a drive (recommended)", {"temp": "15 to 25 °C (59 to 77 °F)", "rh": "20 to 50%", "note": "Fujifilm LTO-9 recommended operating range"}),
        ("In a drive (allowed)", {"temp": "10 to 45 °C (50 to 113 °F)", "rh": "10 to 80%", "note": "IBM operating range"}),
        ("Shipping", {"temp": "−23 to 49 °C (−9 to 120 °F)", "rh": "5 to 80%", "note": "IBM; the tape itself must not go above 52 °C (Fujifilm)"}),
    ],
    "fig_alt": "Temperature and humidity bands for LTO tapes: a narrow long-term storage band at 16 to 25 °C and 20 to 50% humidity inside wider bands for short-term storage, use in a drive and shipping",
    "fig_caption": "The long-term storage band is the narrowest: 16 to 25 °C and 20 to 50% relative humidity. Cartridges tolerate wider ranges for a short time, in a drive or in transit, but the 30-year rating assumes the narrow band.",
    "source_line": f'Figures from the <a href="{IBM_SHEET}" rel="nofollow noopener" target="_blank">IBM LTO Ultrium data cartridge data sheet</a> (LTO-9 and LTO-10) and the <a href="{FUJI_SHEET}" rel="nofollow noopener" target="_blank">Fujifilm LTO-9 data sheet</a>. The <a href="{OT_GUIDE}" rel="nofollow noopener" target="_blank">Overland-Tandberg tape handling guide</a> gives the same archive range. All ranges assume no condensation; IBM sets a maximum wet bulb temperature of 26 °C.',
    "acclimatise": f'IBM, Dell and Overland-Tandberg all ask for 24 hours in the room with the drive before use, or longer if needed to avoid condensation (<a href="{IBM_HANDLING}" rel="nofollow noopener" target="_blank">IBM</a>, <a href="{DELL_KB}" rel="nofollow noopener" target="_blank">Dell</a>).',
    "magnets": "IBM says not to expose cartridges to stray magnetic fields above 100 oersteds, and Overland-Tandberg advises keeping them 8 to 12 cm (3 to 5 inches) from high-current cables, power supplies and motors.",
    "answer": "Store LTO tapes at 16 to 25 °C (61 to 77 °F) and 20 to 50% relative humidity for the long term, standing upright in their cases, away from magnets and sunlight; give them 24 hours in the drive room before use, and keep a second copy at another site.",
    "faqs": [
        ("What temperature should LTO tapes be stored at?", "16 to 25 °C (61 to 77 °F) for long-term storage, according to IBM and Fujifilm. For a shorter time, IBM allows 16 to 32 °C, and the tape itself must never go above 52 °C."),
        ("What humidity is best for storing LTO tapes?", "20 to 50% relative humidity for long-term storage, without condensation. Short-term storage can go up to 80%, but stable and dry is what the 30-year rating assumes."),
        ("Should LTO tapes be stored flat or upright?", "Upright. Overland-Tandberg says media should be stored vertically, and Dell says to keep tapes in their cases, upright, and never stacked."),
        ("How long should a tape acclimatise before use?", "24 hours in the room with the drive, or longer if it came from somewhere much colder or more humid, so no condensation forms in the drive."),
        ("Can I keep LTO tapes in a normal fire safe?", "A safe rated only for paper is not enough, because it lets the inside get far hotter than tape tolerates. Use a safe or cabinet rated for magnetic media (UL 72 Class 150 in the US), or keep a second copy offsite."),
        ("How should tapes be stored offsite?", "In a climate-controlled place with the same conditions as onsite, carried in padded cases, encrypted, and logged so you always know which cartridge is where."),
    ],
}


def build_store_guide(current):
    path = "/resources/how-to-store-lto-tapes"
    c = COND
    rows = [[esc(k), esc(v["temp"]), esc(v["rh"]), esc(v.get("note", ""))] for k, v in c["rows"]]
    sections = [
        sec("Conditions", "Temperature and humidity for LTO tapes", f"""
{figure("lto-storage-conditions.svg", c["fig_alt"], c["fig_caption"], 960, 400)}
{table(["Use", "Temperature", "Relative humidity", "Note"], rows, "LTO tape storage conditions")}
<p>{c["source_line"]}</p>
<ul>
<li><strong>Keep it stable.</strong> Slow, small changes do no harm; daily swings and condensation do. A closed cupboard in an air-conditioned office is better than a garage or an outside wall.</li>
<li><strong>Acclimatise before use.</strong> {c["acclimatise"]}</li>
<li><strong>Away from magnets, heat and sun.</strong> {c["magnets"]} Keep them out of direct sunlight and off radiators.</li>
</ul>
<p>These conditions are what the 30-year archival rating assumes. More on how long tapes last is in <a href="/why-tape/lto-tape-lifespan">LTO tape lifespan</a>.</p>"""),
        sec("Cases, cabinets and racks", "Where to put the cartridges", f"""
{figure("lto-storage-options.svg", "Four ways to keep LTO cartridges: a single jewel case standing on edge, a padded transport case for 5 to 20 cartridges, a media cabinet with drawers, and a shelf in a 19 inch rack", "From one cartridge to a few hundred: keep each tape in its case on edge, carry them in padded cases, and store larger collections in a media cabinet or on rack shelving in a room with stable conditions.", 960, 400)}
{table(["Option", "Best for", "What to check"], [
    ["Jewel case (the case the cartridge ships in)", "Every cartridge on a shelf", "Store it standing on edge, like a book, not lying flat in a pile"],
    ["Padded transport case (turtle case) for 5, 10 or 20 cartridges", "Carrying tapes offsite and back", "Foam slots that hold each cartridge, a latch that locks, a place for a seal or tag"],
    ["Storage box or drawer insert", "Small archives in an office cupboard", "Slots that keep cartridges upright and separated; dust lid"],
    ["Media cabinet", "Tens to hundreds of cartridges in one room", "Drawers sized for LTO, a lock, and for important archives a fire rating made for magnetic media, which must keep the inside cooler than a paper safe"],
    ["Rack shelf or library", "Cartridges next to the drives in a server room", "Shelves sized for LTO cartridges in a 19 inch rack; for many cartridges a <a href='/lto-tape-library'>tape library</a> stores and loads them for you"],
], "Ways to store LTO cartridges")}
<p>A paper fire safe is not enough for tape: it is designed to keep paper below the point where it burns, which is far hotter than tape tolerates. Look for a cabinet or safe rated for magnetic media (in the US, UL 72 Class 150 is the rating for magnetic tape and film, against Class 350 for paper), or rely on a second copy at another site. Barcode labels and cleaning cartridges are covered in <a href="/resources/lto-cleaning-tapes-and-labels">cleaning tapes, labels and cases</a>.</p>"""),
        sec("Offsite", "Offsite storage and rotation", f"""
{figure("offsite-tape-rotation.svg", "A set of cartridges leaving the building each week for an offsite location while the previous set comes back", "A simple weekly rotation: one set of tapes leaves the building, the previous set comes back to be reused or kept, so one complete copy is always somewhere else.", 960, 420)}
<p>One copy of the data should always be somewhere a fire, flood or break-in at the main site cannot reach. With tape that means taking cartridges out of the building on a schedule:</p>
<ul>
<li><strong>Daily, weekly, monthly sets.</strong> A common scheme (often called grandfather, father, son) keeps daily tapes for a week or two, weekly tapes for a month or two and monthly tapes for a year or more, with the newest weekly or monthly set offsite.</li>
<li><strong>Archive copies.</strong> For an archive that is written once, make two copies and keep one at another site from the start.</li>
<li><strong>A log.</strong> Record which cartridge is where, who moved it and when. Backup software and libraries can track this as "vaulting".</li>
<li><strong>Encrypt what travels.</strong> A cartridge in a car or a courier van can be lost; drive encryption (AES-256, LTO-4 and later) means a lost tape exposes nothing.</li>
</ul>
<p>If you use a vault company, ask where and how they store tapes (temperature and humidity control), how quickly they can return a cartridge, how they record chain of custody, and how they transport cartridges between sites. Why offsite tapes still matter is argued in <a href="/blog/offsite-tape-backups-still-beat-most-good-enough-plans">offsite tape backups still beat most "good enough" plans</a>.</p>"""),
        sec("Handling", "Handling checklist", """
<ul>
<li>Hold cartridges by the shell; never touch the tape or pull the leader pin.</li>
<li>Do not drop them. A dropped cartridge should be tested, or retired, before it holds the only copy of anything.</li>
<li>Keep them in their cases whenever they are out of a drive or library.</li>
<li>Label with proper barcode labels, not handwritten stickers that can peel off inside a drive.</li>
<li>Store them upright, never stacked flat in piles, and never leave them in a car.</li>
<li>Read a sample of cartridges back every year or two to check the archive is still readable.</li>
</ul>"""),
        more_guides(path),
    ]
    faqs = c["faqs"]
    return article(path, "How to Store LTO Tapes: Temperature, Cases, Cabinets",
                   "How to store LTO tapes: storage temperature and humidity from the media specs, cases, cabinets and racks, offsite rotation and a handling checklist.",
                   "How to Store LTO Tapes",
                   c["answer"], "Storage guide", sections, faqs, PUBLISHED,
                   [("Home", "/"), ("Resources", "/resources"), ("How to store LTO tapes", path)])


# ---------------------------------------------------------------- N3 OWC LTO drives

OWC_SEEN = "17 October 2026"
OWC_TB = [  # (SKU, generation, onboard storage, US list price on OWC's store) incl. Hedge Canister
    ("OWCTBLTMP70000H", "LTO-7", "None", 5999.99), ("OWCTBLTMP70N04H", "LTO-7", "4 TB", 7149.99), ("OWCTBLTMP70N08H", "LTO-7", "8 TB", 8749.99),
    ("OWCTBLTMP80000H", "LTO-8", "None", 8799.99), ("OWCTBLTMP80N04H", "LTO-8", "4 TB", 9949.99), ("OWCTBLTMP80N08H", "LTO-8", "8 TB", 11199.99),
    ("OWCTBLTMP90000H", "LTO-9", "None", 12499.99), ("OWCTBLTMP90N04H", "LTO-9", "4 TB", 13649.99), ("OWCTBLTMP90N08H", "LTO-9", "8 TB", 14899.99),
]
OWC_ETH = [("OWC10GLTMP08H", "LTO-8", 11499.99, "In stock"), ("OWC10GLTMP09H", "LTO-9", 14999.99, "Ships: pending")]
OWC_LINKS = {
    "archive_pro": "https://www.owc.com/solutions/archive-pro",
    "archive_pro_eth": "https://www.owc.com/solutions/archive-pro-ethernet",
    "launch_2020": "https://owc.com/news/owc-introduces-mercury-pro-lto-solution-making-archiving-seamless",
    "launch_eth": "https://www.owc.com/news/other-world-computing-owc-launches-owc-archive-pro-ethernet-network-based-lto-backup-and-archiving-solution",
    "techradar": "https://www.techradar.com/reviews/owc-mercury-pro-lto-lto-9",
    "larryjordan": "https://larryjordan.com/?p=132746",
    "store": "https://eshop.macsales.com/item/OWC/TBLTMP90000H/",
}


def build_owc(current):
    path = "/resources/owc-lto-tape-drives"
    g = current["generations"]
    L = OWC_LINKS
    usd = lambda v: f"${v:,.2f}"
    ext = drive_rng(g["LTO-9"].get("driveExternal"))
    xd = g["LTO-9"].get("driveExternal") or {}
    if xd.get("low") is not None and BP.MKT.is_us:
        owc_vs = ("OWC's LTO-9 kit is inside that range, and it also includes the Thunderbolt enclosure and Hedge Canister." if xd["low"] <= 12499.99 <= (xd.get("high") or xd["low"])
                  else "OWC's LTO-9 kit costs more than those drives, partly because it includes the Thunderbolt enclosure and Hedge Canister." if 12499.99 > (xd.get("high") or xd["low"])
                  else "OWC's LTO-9 kit costs less than those drives and also includes the Thunderbolt enclosure and Hedge Canister.")
    else:
        owc_vs = "OWC's prices are US list prices in US dollars, and the kits include the Thunderbolt enclosure and Hedge Canister."
    where = _where()
    tb_rows = [[f"<code>{sku}</code>", gen, onb, usd(price)] for sku, gen, onb, price in OWC_TB]
    eth_rows = [[f"<code>{sku}</code>", gen, usd(price), esc(av)] for sku, gen, price, av in OWC_ETH]
    sections = [
        sec("The range", "OWC's LTO drives today", f"""
{figure("owc-lto-archive-pro.svg", "On the left, one computer connected to an OWC Archive Pro LTO-9 drive over Thunderbolt; on the right, three workstations sharing an Archive Pro Ethernet drive over 10 gigabit iSCSI", "Archive Pro connects one LTO drive to one Mac or PC over Thunderbolt. Archive Pro Ethernet puts the drive on the network so several workstations can use it over 10 gigabit iSCSI.", 960, 420)}
<p>OWC (Other World Computing) sells LTO tape drives in desktop enclosures, aimed mainly at Mac users and video teams. There are two current product lines:</p>
<ul>
<li><a href="{L['archive_pro']}" rel="nofollow noopener" target="_blank">OWC Archive Pro</a>: a desktop LTO-7, LTO-8 or LTO-9 drive that connects over Thunderbolt, with an optional built-in SSD of 4 or 8 TB for staging data.</li>
<li><a href="{L['archive_pro_eth']}" rel="nofollow noopener" target="_blank">OWC Archive Pro Ethernet</a>: the same idea as a network appliance, sharing the drive over 10 gigabit Ethernet (iSCSI), launched in April 2025.</li>
</ul>
<p>The <strong>Mercury Pro LTO</strong> is the earlier name of the Thunderbolt drive. OWC's current manual is titled "Archive Pro LTO | Mercury Pro LTO" and calls Mercury Pro owners legacy users, so the Mercury Pro LTO-9 and LTO-7 models people search for are, in practice, sold today as Archive Pro. We found no OWC LTO-10 product as of {OWC_SEEN}.</p>"""),
        sec("History", "From Mercury Pro LTO to Archive Pro", table(["When", "What changed", "Source"], [
            ["September 2020", "Mercury Pro LTO launched: LTO-8 with an IBM drive, Thunderbolt 3, myLTO software, $4,499 including a tape and a cleaning cartridge", f'<a href="{L["launch_2020"]}" rel="nofollow noopener" target="_blank">OWC</a>'],
            ["August 2021", "Units ship with ArGest Backup Desktop Edition", "Trade press"],
            ["2022", "LTO-9 version reviewed at $6,299 direct from OWC", f'<a href="{L["techradar"]}" rel="nofollow noopener" target="_blank">TechRadar</a>'],
            ["January 2025", "OWC and Hedge partner; kits with an \"H\" in the part number include Hedge Canister", "OWC store"],
            ["April 2025", "Archive Pro Ethernet launched, LTO-7, LTO-8 and LTO-9, from $7,799", f'<a href="{L["launch_eth"]}" rel="nofollow noopener" target="_blank">OWC</a>'],
            [OWC_SEEN, "Archive Pro Thunderbolt sold in LTO-7, LTO-8 and LTO-9; versions without Canister sold out or no longer for sale", f'<a href="{L["store"]}" rel="nofollow noopener" target="_blank">OWC store</a>'],
        ], "OWC LTO product history")),
        sec("Specifications", "Archive Pro and Archive Pro Ethernet compared", table(["", "Archive Pro (Thunderbolt)", "Archive Pro Ethernet"], [
            ["Generations", "LTO-7, LTO-8, LTO-9", "LTO-8, LTO-9 (LTO-7 no longer for sale)"],
            ["Drive inside", "IBM LTO Ultrium drive (IBM Ultrium 9 in the LTO-9 model)", "IBM LTO drive (IBM Ultrium 9 in the LTO-9 model)"],
            ["Connection", "Thunderbolt 3 (USB-C, up to 40 Gb/s); the drive is SAS inside and needs the ATTO SAS driver", "Two 10 GbE ports for iSCSI plus a 1 GbE management port"],
            ["Speed OWC quotes (LTO-9)", "Up to 300 MB/s native", "Up to 400 MB/s native"],
            ["Extra", "Optional 4 or 8 TB onboard SSD, extra Thunderbolt port, Mini-SAS HD port", "Shared by several workstations"],
            ["Software included", "Hedge Canister on \"H\" kits", "Hedge Canister and ATTO Xtend SAN iSCSI initiator for Mac"],
            ["Operating systems", "macOS 11 to macOS 26, Windows 10 and 11, Windows Server 2022, Linux", "macOS 13 to macOS 26, Windows 10 and 11, Windows Server 2022, Linux"],
            ["Tape format", "LTFS", "LTFS"],
            ["Warranty", "3 years (OWC limited warranty)", "See OWC"],
        ], "OWC Archive Pro specifications")),
        sec("Prices", "OWC LTO drive prices", f"""
<p>US list prices on OWC's own store on {OWC_SEEN}. Every current kit includes Hedge Canister.</p>
{table(["Part number", "Generation", "Onboard SSD", "Price"], tb_rows, "OWC Archive Pro Thunderbolt prices")}
{table(["Part number", "Generation", "Price", "Availability"], eth_rows, "OWC Archive Pro Ethernet prices")}
<p>For comparison, external LTO-9 drives from other brands are listed at {ext}{where} in our <a href="/lto-tape-price-trend/lto9-price">LTO-9 price tracker</a>. {owc_vs} Resellers have listed the LTO-9 model without software for less, so compare the full kit before you buy.</p>"""),
        sec("Compatibility", "Which tapes each model reads", f"""
{table(["Model", "Reads", "Writes"], [[f"Archive Pro {x}", esc(SPECS[x]["reads"]), esc(SPECS[x]["writes"])] for x in ("LTO-9", "LTO-8", "LTO-7")], "OWC drive compatibility")}
<p>The LTO rules are the same whatever the enclosure: an LTO-9 drive reads and writes LTO-8 and LTO-9 cartridges and nothing older. If your archive is on LTO-6 or LTO-7, check which model can still read it before you choose. LTO-7 is now three generations old, so the LTO-7 kit mainly makes sense for reading or extending an existing LTO-7 archive.</p>"""),
        sec("Reviews", "What reviewers said", f"""
<ul>
<li><a href="{L['techradar']}" rel="nofollow noopener" target="_blank">TechRadar Pro</a> reviewed the Mercury Pro LTO-9 in 2022: tape economics look good, but managing an archive spread over many 18 TB tapes is harder than it looks, and the $6,299 price then did not include the ArGest licence.</li>
<li><a href="{L['larryjordan']}" rel="nofollow noopener" target="_blank">Larry Jordan</a>, a video editing trainer, tested a Mercury Pro LTO-8 loaner unit in 2021 and recommended it for media archiving despite the upfront cost.</li>
</ul>
<p>We found no independent review of the current Archive Pro or Archive Pro Ethernet as of {OWC_SEEN}. We have not tested these drives ourselves.</p>"""),
        sec("Who it suits", "When an OWC drive makes sense", f"""
<p><strong>Good fit:</strong> a Mac-based video or photo studio that wants one box to plug in over Thunderbolt, with archiving software included and nothing to install inside a computer. Archive Pro Ethernet suits a small team that wants several editors to share one drive.</p>
<p><strong>Look elsewhere:</strong> if you already have a server with a SAS port, a bare external SAS drive from HPE, IBM or Quantum costs less; if you need LTO-10, OWC does not offer it yet; if you need a library for many cartridges, see <a href="/lto-tape-library">LTO tape libraries</a>. Other desktop Thunderbolt brands are covered in the <a href="/why-tape/lto-tape-drive">LTO drive buying guide</a>, and other archive software, including YoYotta and Archiware P5, in the <a href="/tape-archive-advisor">tape archive advisor</a>.</p>"""),
        more_guides(path),
    ]
    faqs = [
        ("Is the OWC Mercury Pro LTO still sold?", "Under a new name. OWC now sells the Thunderbolt LTO drive as the Archive Pro, and its manual covers both Archive Pro and Mercury Pro LTO. LTO-7, LTO-8 and LTO-9 versions are listed."),
        ("Which drive is inside the OWC Archive Pro?", "An IBM LTO Ultrium drive; the LTO-9 model uses an IBM Ultrium 9 mechanism. The original 2020 Mercury Pro LTO used an IBM LTO-8 drive."),
        ("How much does the OWC Archive Pro LTO-9 cost?", f"{usd(12499.99)} on OWC's US store on {OWC_SEEN} for the kit with Hedge Canister, or up to {usd(14899.99)} with an 8 TB onboard SSD. The Archive Pro Ethernet LTO-9 is listed at {usd(14999.99)}."),
        ("Does the OWC Archive Pro work with Windows?", "Yes. OWC lists Windows 10 and 11 and Windows Server 2022 as well as macOS and Linux. It connects over Thunderbolt, so the PC needs a Thunderbolt port."),
        ("Does OWC make an LTO-10 drive?", f"Not as of {OWC_SEEN}. The Archive Pro and Archive Pro Ethernet are sold with LTO-7, LTO-8 and LTO-9 drives."),
        ("What is the difference between Archive Pro and Archive Pro Ethernet?", "Archive Pro connects to one computer over Thunderbolt. Archive Pro Ethernet sits on the network and shares the drive with several workstations over 10 gigabit iSCSI."),
    ]
    return article(path, "OWC Mercury Pro and Archive Pro LTO Drives: 2026 Guide",
                   "OWC Mercury Pro LTO and Archive Pro LTO-7, LTO-8 and LTO-9 drives: what changed, specs, Thunderbolt vs Ethernet, current prices and reviews.",
                   "OWC Mercury Pro and Archive Pro LTO Drives",
                   f"OWC now sells its Thunderbolt LTO drive, formerly the Mercury Pro LTO, as the Archive Pro in LTO-7, LTO-8 and LTO-9 versions with an IBM drive inside and Hedge Canister included, from {usd(5999.99)} for LTO-7 to {usd(12499.99)} for LTO-9 on OWC's US store; Archive Pro Ethernet shares a drive over 10 GbE, and there is no OWC LTO-10 drive yet.",
                   "Drive guide", sections, faqs, PUBLISHED, [("Home", "/"), ("Resources", "/resources"), ("OWC LTO drives", path)])


def build_all(current):
    out = [build_pillar(current), build_store_guide(current), build_owc(current), build_lto_vs_object(current)]
    return out
