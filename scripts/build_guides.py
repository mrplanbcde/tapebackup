"""LTO guide pages from the October 2026 SEO plan (docs/seo/seo-plan-2026-10.md).

Each page targets one keyword cluster from docs/seo/keyword-map-us.csv. Prices
come from the current market (build_prices), specs from build_prices.SPECS, and
news from data/news.json, so a monthly refresh updates every page.
"""

import json
import os

import build_prices as BP
from build_articles import article, sec, table
from build_prices import CURRENT_LABEL, GENS, READ_BY, ROADMAP, SPECS, date_text, fallback_note, per_tb, rng
from site_shell import ROOT, esc, figure

PUBLISHED = "2026-10-03"


def drive_rng(item):
    return rng(item, False) + fallback_note(item) if (item or {}).get("low") is not None else "Not listed"


def spec_rows(gens):
    return [[g if g not in GENS else f'<a href="/lto-tape-price-trend/{g.lower().replace("-", "")}-price">{g}</a>',
             str(SPECS[g]["year"]), SPECS[g]["native"], f"{SPECS[g]['compressed']} ({SPECS[g]['ratio']})", f"{SPECS[g]['speed']} MB/s"] for g in gens]


def link_grid(items):
    return '<div class="link-grid">' + "".join(f'<a href="{h}">{esc(t)}<span>{esc(s)}</span></a>' for t, h, s in items) + "</div>"


GUIDE_LINKS = [
    ("What is LTO tape", "/lto-tape", "The format in one page"),
    ("LTO capacity chart", "/lto-tape-capacity", "LTO-1 to LTO-14"),
    ("LTO tape drive buying guide", "/why-tape/lto-tape-drive", "Which drive to buy"),
    ("LTO tape libraries", "/lto-tape-library", "Autoloaders and libraries"),
    ("LTO tape lifespan", "/why-tape/lto-tape-lifespan", "How long tapes last"),
    ("LTFS explained", "/resources/ltfs", "Tape as a file system"),
    ("LTO tape data recovery", "/resources/lto-tape-data-recovery", "Reading old tapes"),
    ("Cleaning tapes and labels", "/resources/lto-cleaning-tapes-and-labels", "Supplies and handling"),
    ("LTO tape news", "/lto-tape-news", "What changed this month"),
]


def more_guides(skip):
    return sec("More guides", "Other LTO guides", link_grid([x for x in GUIDE_LINKS if x[1] != skip]))


# ---------------------------------------------------------------- pillar

def build_pillar(current):
    path = "/lto-tape"
    g = current["generations"]
    l9, l10 = g["LTO-9"], g["LTO-10"]
    where = "" if BP.MKT.is_us else f" in {BP.MKT.country}"
    sections = [
        sec("The basics", "What LTO tape is", """
<p>LTO (Linear Tape-Open) is an open standard for magnetic data tape, set by the LTO Program, whose members are HPE, IBM and Quantum. A cartridge holds a single reel of half-inch tape; the drive pulls it past a head that writes many parallel tracks, end to end and back again. The format is called Ultrium, which is why cartridges are labelled "LTO Ultrium".</p>
<p>Only two companies make LTO tape: Fujifilm and Sony. Cartridges sold under HPE, IBM, Quantum or Dell labels contain tape from one of them, and every certified cartridge of a generation works in every brand of drive of that generation. See <a href="/lto-tape-brand">LTO tape brands</a>.</p>"""),
        sec("Generations", "LTO generations at a glance", f"""
<p>A new generation arrives every two to four years and roughly doubles capacity. The current generation is LTO-10, and LTO-9 is the one most people buy.</p>
{table(["Generation", "Released", "Native capacity", "Compressed", "Native speed"], spec_rows(list(SPECS)[4:]), "LTO generations")}
<p>Compressed figures assume data that compresses 2.5 to 1. Video, images and encrypted files do not, so plan on native capacity. Older generations and the roadmap to LTO-14 are in the <a href="/lto-tape-capacity">LTO capacity chart</a>.</p>"""),
        sec("Compatibility", "Which drive reads which tape", """
<p>Drives up to LTO-7 read two generations back and write one back. LTO-8 and LTO-9 drives read and write one generation back only. LTO-10 drives use LTO-10 media only.</p>
<ul>""" + "".join(f"<li>{esc(READ_BY[x])}</li>" for x in GENS) + """</ul>
<p>This is the rule that decides when an archive has to be migrated: once no drive you own can read a generation, its tapes become a recovery job. See <a href="/resources/lto-tape-migration">LTO tape migration</a>.</p>"""),
        sec("Cost", "What LTO tape costs", f"""
<p>As of {date_text()}, an 18 TB LTO-9 cartridge costs {rng(l9['cartridge'], True)}{where}, or {per_tb(l9['cartridge'])} per TB, which makes it the cheapest LTO media per terabyte. A 30 TB LTO-10 cartridge costs {rng(l10['cartridge'], True)}. The drive is the larger cost: a new internal LTO-9 drive is listed at {drive_rng(l9.get('driveInternal'))}.</p>
<p>Because the drive is a fixed cost and media is cheap, tape gets cheaper per terabyte the more you store. Below about 15 TB, disk or cloud is usually cheaper; for large archives, tape wins. See the <a href="/lto-tape-price-trend">LTO price tracker</a> and the <a href="/comparisons/tape-vs-cloud-5-year-cost">tape vs cloud cost comparison</a>.</p>"""),
        sec("Why use it", "What LTO tape is good at", """
<ul>
<li><strong>Cheap capacity.</strong> The lowest media cost per terabyte of any storage you can buy and keep yourself.</li>
<li><strong>Offline copies.</strong> A cartridge on a shelf is out of reach of ransomware and of mistakes made on the network. WORM cartridges cannot be overwritten at all.</li>
<li><strong>Long life.</strong> Manufacturers rate cartridges for 30 years of archival storage in the right conditions. See <a href="/why-tape/lto-tape-lifespan">LTO tape lifespan</a>.</li>
<li><strong>No power when idle.</strong> A stored cartridge uses no electricity.</li>
<li><strong>Fast streaming.</strong> Current drives write up to 400 MB/s native, faster than a single hard drive.</li>
</ul>
<p>The trade-offs: access is sequential, so finding one file takes tens of seconds to minutes, you need a drive and backup software or LTFS, and old generations must be migrated before their drives disappear.</p>"""),
        sec("How it is used", "How people use LTO tape", """
<p><strong>Backup software</strong> such as Veeam, Commvault, Bacula or Catalogic DPX writes backup copies to tape and keeps the catalogue. See <a href="/best-tape-backup-software">best tape backup software</a>.</p>
<p><strong>LTFS</strong> formats a tape so it mounts like a disk, with files you can drag and drop; it is common in film and video work. See <a href="/resources/ltfs">LTFS explained</a>.</p>
<p><strong>Libraries and autoloaders</strong> hold many cartridges and change them automatically. See <a href="/lto-tape-library">LTO tape libraries</a>.</p>"""),
        more_guides(path),
    ]
    faqs = [
        ("What does LTO stand for?", "Linear Tape-Open, an open magnetic tape standard created by HPE, IBM and Quantum. The tape format itself is called Ultrium."),
        ("How much data does an LTO tape hold?", "LTO-9 holds 18 TB native and LTO-10 holds 30 TB, or 40 TB on the newer cartridge. Vendors also quote compressed figures 2.5 times higher, which only apply to data that compresses."),
        ("Is LTO tape still used?", "Yes. LTO shipped 160.3 exabytes of capacity in 2025, and shipments in the first quarter of 2026 were up 57% on a year earlier, driven by archives, AI training data and offline backup copies."),
        ("How long does LTO tape last?", "Manufacturers rate LTO cartridges for 30 years of archival storage at 16 to 25 °C and 20 to 50% humidity. In practice the limit is usually drive availability, so plan to migrate every two or three generations."),
        ("How much does LTO tape cost?", f"An 18 TB LTO-9 cartridge costs {rng(l9['cartridge'], True)}{where} as of {date_text()}, about {per_tb(l9['cartridge'])} per TB. A new LTO-9 drive costs {drive_rng(l9.get('driveInternal'))}."),
        ("Do I need special software for LTO tape?", "Yes, either backup software that supports tape drives or LTFS, which lets the operating system mount a tape like a disk. Windows, macOS and Linux all have free LTFS tools."),
    ]
    return article(path, "LTO Tape: What It Is, Capacity, Lifespan and Cost",
                   "What LTO tape is, how much each generation holds, which drives read which tapes, how long cartridges last and what LTO-9 and LTO-10 cost today.",
                   "LTO Tape Explained",
                   f"LTO (Linear Tape-Open) is the standard magnetic tape for backup and archive: an LTO-9 cartridge holds 18 TB and costs {rng(l9['cartridge'], True)}{where}, an LTO-10 cartridge holds 30 TB or 40 TB, and cartridges are rated for 30 years on a shelf.",
                   "LTO tape guide", sections, faqs, PUBLISHED, [("Home", "/"), ("LTO tape", path)])


# ---------------------------------------------------------------- capacity chart

def build_capacity(current):
    path = "/lto-tape-capacity"
    rm = [[x[0], "Roadmap", x[1], f"{x[2]} (2.5:1)", "Not announced"] for x in ROADMAP]
    sections = [
        sec("Chart", "LTO capacity by generation", f"""
{table(["Generation", "Released", "Native capacity", "Compressed", "Native speed"], spec_rows(list(SPECS)) + rm, "LTO capacity chart")}
<p>Native capacity is what the tape holds. Compressed capacity assumes the drive can compress the data 2 to 1 (up to LTO-5) or 2.5 to 1 (LTO-6 onward). LTO-10 has two cartridges: the standard 30 TB cartridge and a 40 TB cartridge that shipped in 2026 and works in the same drives.</p>"""),
        sec("Native or compressed", "Which number to plan with", """
<p>Plan with native capacity. Video, photos, audio, already-compressed backups and encrypted data barely compress, so they fill a cartridge at about its native size. Databases, logs and text can beat the 2.5 to 1 ratio. Turn on drive compression anyway: it costs nothing and helps when the data allows it.</p>
<p>Formatting also takes a little space: LTFS reserves room for its index partition, so a formatted LTO-9 cartridge offers slightly less than 18 TB to files.</p>"""),
        sec("How many tapes", "How many cartridges you need", f"""
{table(["Data", "LTO-8 (12 TB)", "LTO-9 (18 TB)", "LTO-10 (30 TB)"], [[f"{tb} TB"] + [str(-(-tb // n)) for n in (12, 18, 30)] for tb in (10, 50, 100, 500, 1000)], "Cartridges per data size")}
<p>One copy, native capacity, full cartridges. Multiply by the number of copies you keep, and allow extra when many small jobs leave cartridges part full. The <a href="/backup-calculator">backup calculator</a> does this with prices.</p>"""),
        sec("Roadmap", "LTO-11 to LTO-14", """
<p>In November 2025 the LTO Program cut its future capacity targets to favour reliability and cost per terabyte: LTO-11 is now planned at 70 TB native (175 TB compressed) and LTO-14 at 365 TB native (913 TB compressed). No LTO-11 product or release date has been announced. Past generations have arrived two to four years apart, and LTO-10 shipped in 2025.</p>"""),
        sec("Physical size", "Cartridge dimensions", """
<p>Every LTO generation uses the same cartridge shell: 102 × 105.4 × 21.5 mm (about 4.0 × 4.1 × 0.8 inches). That is why one library slot fits any generation and why the label, not the size, tells cartridges apart.</p>"""),
        more_guides(path),
    ]
    faqs = [
        ("What is the capacity of LTO-9?", "18 TB native, or 45 TB with 2.5 to 1 compression."),
        ("What is the capacity of LTO-8?", "12 TB native, or 30 TB with 2.5 to 1 compression."),
        ("What is the capacity of LTO-10?", "30 TB native (75 TB compressed) on the standard cartridge, and 40 TB native (100 TB compressed) on the cartridge that shipped in 2026."),
        ("What is the capacity of LTO-7 and LTO-6?", "LTO-7 holds 6 TB native (15 TB compressed) and LTO-6 holds 2.5 TB native (6.25 TB compressed)."),
        ("When will LTO-11 come out?", "No date has been announced. The November 2025 roadmap plans LTO-11 at 70 TB native; generations have historically arrived two to four years apart."),
        ("Are all LTO tapes the same size?", "Yes. Every generation uses the same 102 × 105.4 × 21.5 mm cartridge, so they fit the same slots and cases."),
    ]
    return article(path, "LTO Tape Capacity Chart: LTO-1 to LTO-14 Sizes",
                   "Native and compressed capacity of every LTO generation from LTO-1 to LTO-10, the LTO-11 to LTO-14 roadmap, speeds, release years and cartridges per TB.",
                   "LTO Tape Capacity by Generation",
                   "LTO-9 holds 18 TB native (45 TB compressed), LTO-10 holds 30 TB or 40 TB native (75 or 100 TB compressed), and LTO-8 holds 12 TB native; plan with native capacity, because video, images and encrypted data do not compress.",
                   "Capacity chart", sections, faqs, PUBLISHED, [("Home", "/"), ("LTO tape", "/lto-tape"), ("Capacity chart", path)])


# ---------------------------------------------------------------- drive buying guide

def build_drive_guide(current):
    path = "/why-tape/lto-tape-drive"
    g = current["generations"]
    rows = []
    for gen in ("LTO-10", "LTO-9", "LTO-8", "LTO-7", "LTO-6"):
        gg = g[gen]
        rows.append([f'<a href="/lto-tape-price-trend/{gen.lower().replace("-", "")}-price">{gen}</a>', SPECS[gen]["native"].replace(" or ", " / "),
                     esc(drive_rng(gg.get("driveInternal"))), esc(drive_rng(gg.get("driveExternal"))), SPECS[gen]["reads"]])
    l9 = g["LTO-9"]
    sections = [
        sec("Prices", "LTO tape drive prices by generation", f"""
{table(["Generation", "Native capacity", "Internal drive", "External drive", "Reads"], rows, "LTO drive prices")}
<p>New standalone drives listed at the sellers we checked on {date_text()}. Internal drives fit a 5.25-inch bay; external drives come in a desktop enclosure with their own power supply. LTO-10 drives so far ship only as full-height units.</p>
{figure("lto-drive-compatibility.svg", "Which LTO drive reads and writes which cartridge generation", "Filled squares: the drive reads and writes that generation. Half squares: read only. From LTO-8 on, drives reach back one generation, and LTO-10 drives read only LTO-10.", 960, 450)}"""),
        sec("Which generation", "Which LTO generation to buy", f"""
<ul>
<li><strong>LTO-9 for most buyers.</strong> The cheapest media per terabyte ({per_tb(l9['cartridge'])} per TB), mature half-height drives, and it reads your LTO-8 tapes.</li>
<li><strong>LTO-10 for large archives.</strong> 30 TB or 40 TB per cartridge means fewer tapes to handle, but media costs more per terabyte and the drive reads nothing older.</li>
<li><strong>LTO-8 to match an existing estate</strong> or to read LTO-7 tapes. New drives are still on sale.</li>
<li><strong>LTO-7 or LTO-6 only to read old tapes.</strong> Buy one to recover or migrate an archive, not to start one.</li>
</ul>"""),
        sec("Form factor", "Internal, external or in a library", f"""
<p><strong>Internal half-height</strong> drives are the cheapest way in if your server has a free 5.25-inch bay and airflow. <strong>External desktop</strong> drives cost more but sit next to any server or workstation. <strong>Full-height</strong> drives are faster on some generations and are mostly used in libraries. <strong>Library drives</strong> are sold as modules for a specific library and do not work standalone. If you will need more than one cartridge per backup run, look at an <a href="/lto-tape-library">autoloader or library</a> instead of a single drive.</p>
{figure("lto-drive-form-factors.svg", "Internal half-height, external desktop and library LTO tape drives", "Left to right: an internal half-height SAS drive in a 5.25-inch bay, an external desktop drive (SAS, Thunderbolt or USB), and full-height drives inside a library.")}"""),
        sec("Interface", "SAS, Fibre Channel, Thunderbolt or USB", """
<ul>
<li><strong>SAS</strong> is the standard for standalone drives. The host needs a SAS HBA, not a RAID controller; external drives use SFF-8088 or, on newer models, SFF-8644 cables, so match the HBA port to the drive.</li>
<li><strong>Fibre Channel</strong> is used in libraries and SAN environments.</li>
<li><strong>Thunderbolt and USB</strong> desktop drives (MagStor, mLogic, OWC, Symply and others) wrap a SAS drive in an enclosure with a bridge. They are the easy option for Mac and video workstations.</li>
</ul>
<p>A drive also needs software: backup software that lists the drive model as supported, or LTFS for drag-and-drop use. See <a href="/resources/ltfs">LTFS explained</a>.</p>"""),
        sec("Brands", "HPE, IBM, Quantum, Dell or a desktop brand", """
<p>Current LTO drive mechanisms come from IBM, and the brands differ in firmware, enclosure, bundled software, support and warranty. Pick the brand your backup software and server vendor support, then compare the exact part number between sellers, because the same drive is often listed thousands apart.</p>"""),
        sec("Used drives", "Buying a used or refurbished drive", """
<p>A used drive is reasonable for reading old tapes. Ask for the head and tape-motion hours, a recent firmware version and a return period, and test it with a cartridge you can afford to lose before trusting it with an archive. Avoid drives sold as untested; a bad head can damage the tapes you put in it.</p>"""),
        sec("Before you buy", "Checklist", """
<ol>
<li>Generation: which tapes do you need to read, and which will you write?</li>
<li>Interface: does the host have a SAS HBA with the right port, or Thunderbolt?</li>
<li>Software: is the exact drive model on your backup software's compatibility list?</li>
<li>Capacity: how many cartridges per backup? More than one or two means an autoloader.</li>
<li>Cleaning cartridge and labels: see <a href="/resources/lto-cleaning-tapes-and-labels">cleaning tapes and labels</a>.</li>
</ol>"""),
        more_guides(path),
    ]
    faqs = [
        ("How much does an LTO-9 tape drive cost?", f"New internal LTO-9 drives were listed at {drive_rng(l9.get('driveInternal'))} and external desktop drives at {drive_rng(l9.get('driveExternal'))} as of {date_text()}."),
        ("Which LTO drive should I buy?", "LTO-9 for most new setups: cheapest media per terabyte and it reads LTO-8. Choose LTO-10 for very large archives, and LTO-6 or LTO-7 only to read old tapes."),
        ("Can a new LTO drive read old tapes?", "Only one generation back from LTO-8 onward: LTO-9 drives read LTO-8, LTO-8 drives read LTO-7, and LTO-10 drives read only LTO-10. Drives up to LTO-7 read two generations back."),
        ("Do I need a SAS card for an LTO drive?", "Yes for internal and external SAS drives: use a SAS HBA, not a RAID controller. Thunderbolt and USB desktop drives connect directly."),
        ("Can I use an LTO drive with a Mac?", "Yes, with a Thunderbolt desktop drive or a SAS drive on a Thunderbolt-to-SAS adapter, plus LTFS or Mac backup software that supports tape."),
        ("Is it worth buying a used LTO drive?", "For reading old tapes, yes, if the seller states head hours and offers returns. For new archives, buy new: a failing drive can damage cartridges."),
    ]
    return article(path, "LTO Tape Drive Buying Guide 2026: Prices and Models",
                   "Which LTO tape drive to buy in 2026: LTO-8, LTO-9 and LTO-10 drive prices, internal vs external, SAS vs Thunderbolt, compatibility and used drives.",
                   "LTO Tape Drive Buying Guide",
                   f"For most buyers the right LTO tape drive in 2026 is LTO-9: new internal drives cost {drive_rng(l9.get('driveInternal'))}, it uses the cheapest media per terabyte and it reads LTO-8 tapes; LTO-10 suits very large archives but reads no older generation.",
                   "Drive buying guide", sections, faqs, PUBLISHED, [("Home", "/"), ("Why tape", "/why-tape"), ("LTO tape drive", path)])


# ---------------------------------------------------------------- libraries

def build_library(current):
    path = "/lto-tape-library"
    sections = [
        sec("When you need one", "Drive, autoloader or library", """
<p>A single drive is enough while each backup fits on one cartridge and someone changes tapes. Once a job spans several cartridges, runs overnight, or you rotate tapes offsite every week, an automated changer pays for itself in staff time and missed backups.</p>
<ul>
<li><strong>Autoloader:</strong> one drive and a magazine of about 8 to 16 slots in 1U or 2U. Good for a small office or a single server.</li>
<li><strong>Small library:</strong> one or more drives and 25 to 50 slots per module, expandable by stacking modules. Good for a mid-size estate or several backup streams.</li>
<li><strong>Enterprise library:</strong> hundreds to thousands of slots and dozens of drives, partitioned between applications.</li>
</ul>"""),
        sec("Models", "Common autoloaders and small libraries", f"""
{table(["Model", "Type", "Slots (base unit)", "Notes"], [
            ["HPE StoreEver 1/8 G2", "Autoloader", "8", "1U, one drive"],
            ["Dell PowerVault TL1000 / IBM TS2900", "Autoloader", "9", "1U, one half-height drive"],
            ["Quantum SuperLoader 3", "Autoloader", "16", "2U, two 8-slot magazines"],
            ["Quantum Scalar i3", "Library", "25", "3U modules, scales up"],
            ["IBM TS4300 / Dell PowerVault ML3", "Library", "40", "3U modules, scales up"],
            ["HPE StoreEver MSL3040", "Library", "40", "3U modules, scales up"],
            ["Qualstar Q-Series, Spectra Stack", "Library", "Varies", "Modular, LTO-9 and LTO-10 drives"],
        ], "LTO autoloaders and libraries")}
<p>Slot counts are for the base unit with its standard configuration; check the data sheet for the drive generations each model supports. Library drives are sold as modules for that library.</p>"""),
        sec("What to check", "Buying checklist", """
<ul>
<li><strong>Drive generation and count.</strong> Two drives let you copy tape to tape and run backup and restore at the same time.</li>
<li><strong>Interface.</strong> SAS for one host, Fibre Channel to share the library across a SAN.</li>
<li><strong>Barcode reader and labels.</strong> Libraries track cartridges by barcode, so every tape needs a label in the right format. See <a href="/resources/lto-cleaning-tapes-and-labels">labels and cleaning tapes</a>.</li>
<li><strong>Mail slots.</strong> I/O slots let you take cartridges offsite without opening the magazine.</li>
<li><strong>Software support.</strong> The library model, not just the drive, must be on your backup software's support list.</li>
<li><strong>Partitioning and encryption key management</strong> if several applications or teams share it.</li>
</ul>"""),
        sec("Capacity", "How much a library holds", f"""
<p>Multiply slots by native capacity: a 40-slot library holds 720 TB on LTO-9 or 1.2 PB on 30 TB LTO-10 cartridges, before compression. Keep a few slots for cleaning cartridges and for tapes waiting to go offsite. Cartridge prices are in the <a href="/lto-tape-price-trend">LTO price tracker</a>.</p>"""),
        more_guides(path),
    ]
    faqs = [
        ("What is the difference between an autoloader and a tape library?", "An autoloader has one drive and a single magazine of about 8 to 16 slots. A library has one or more drives, more slots, and can usually be expanded with extra modules."),
        ("How many tapes does a small LTO library hold?", "Base modules typically hold 25 to 50 cartridges, which is 450 to 900 TB on LTO-9, and most can be expanded by stacking modules."),
        ("Do tape libraries need barcode labels?", "Yes. The library identifies each cartridge by its barcode label, so every data and cleaning cartridge needs one in the format the library expects."),
        ("Can I mix LTO generations in one library?", "Usually yes, with drives of each generation, as long as the library and your backup software support both. Each drive still only reads its supported generations."),
    ]
    return article(path, "LTO Tape Libraries and Autoloaders: Buying Guide",
                   "When you need an LTO autoloader or tape library, common models from HPE, IBM, Dell and Quantum, slot counts, and what to check before buying.",
                   "LTO Tape Libraries and Autoloaders",
                   "An LTO autoloader holds one drive and about 8 to 16 cartridges, while a library holds one or more drives and 25 or more slots per module; move to one when a backup spans several cartridges or nobody is there to change tapes.",
                   "Library guide", sections, faqs, PUBLISHED, [("Home", "/"), ("LTO tape", "/lto-tape"), ("Tape libraries", path)])


# ---------------------------------------------------------------- LTFS

def build_ltfs(current):
    path = "/resources/ltfs"
    sections = [
        sec("What it is", "What LTFS does", """
<p>LTFS (Linear Tape File System) formats an LTO cartridge from LTO-5 onward into two partitions: a small one that holds the file index and a large one that holds the files. Mount the tape and it appears as a drive or folder; you copy files to and from it with the normal file manager or command line, and any other LTFS system can read it without the software that wrote it.</p>
<p>That self-describing format is why LTFS is the standard for exchanging tapes between companies, especially in film, TV and post-production.</p>"""),
        sec("Software", "Free LTFS software", f"""
{table(["Tool", "Systems", "Notes"], [
            ["IBM Storage Archive Single Drive Edition", "Windows, Linux, macOS", "Free; formerly Spectrum Archive SDE"],
            ["HPE StoreOpen with LTFS", "Windows, macOS, Linux", "Free; for HPE drives"],
            ["Quantum LTFS", "Windows, macOS, Linux", "For Quantum drives"],
            ["LTFS reference implementation", "Linux, macOS", "Open source on GitHub"],
            ["WinLtfs", "Windows", "Community open-source tools"],
        ], "LTFS software")}
<p>Desktop drive makers usually bundle one of these. Paid tools for media workflows add catalogues, checksums and spanning across tapes.</p>"""),
        sec("How to use it", "Format and mount a tape", """
<p>With the open-source tools on Linux, format a blank cartridge with <code>mkltfs</code> and mount it with <code>ltfs</code>, pointing both at the drive's device, then copy files into the mount point as usual. Unmount before ejecting: LTFS writes the final index on unmount, and a tape pulled without it may only show the files up to the last index.</p>
<p>The graphical tools do the same with a format button and a drive letter or volume.</p>"""),
        sec("Limits", "What LTFS is not good at", """
<ul>
<li><strong>Small files.</strong> Every file costs index space and tape movement; pack thousands of small files into an archive first.</li>
<li><strong>Deleting.</strong> Deleted files do not free space. Space comes back only when you reformat the whole cartridge.</li>
<li><strong>Random access.</strong> Opening a file in the middle of a tape means winding to it, which can take a minute or two.</li>
<li><strong>Backup.</strong> LTFS is a file system, not backup software: it does not schedule, version or verify anything by itself.</li>
</ul>"""),
        sec("Compatibility", "LTFS versions and drives", """
<p>LTFS works on LTO-5 and every later generation. Newer LTFS versions read tapes written by older ones, but an old tool may refuse a tape formatted with a newer index version, so use the same or a newer version when exchanging tapes. The drive must still read the cartridge generation; see the <a href="/lto-tape-capacity">LTO capacity chart</a> for compatibility.</p>"""),
        more_guides(path),
    ]
    faqs = [
        ("What is LTFS?", "Linear Tape File System: a format that lets an LTO-5 or newer tape be mounted like a disk, with files you copy normally and an index stored on the tape itself."),
        ("Is LTFS free?", "Yes. IBM, HPE and Quantum offer free LTFS software for their drives, and an open-source reference implementation is on GitHub."),
        ("Does LTFS work on Mac and Windows?", "Yes. IBM and HPE provide LTFS for Windows and macOS, and Thunderbolt desktop drives usually ship with it."),
        ("Can I delete files on an LTFS tape?", "You can delete them from the index, but the space is not reused until you reformat the whole cartridge."),
        ("Is LTFS a backup?", "No. It is a file system. Use backup or archive software for scheduling, versions and verification, or add checksums and a second copy yourself."),
    ]
    return article(path, "LTFS Explained: Use LTO Tape Like a Disk",
                   "What LTFS (Linear Tape File System) is, free LTFS software for Windows, macOS and Linux, how to format and mount a tape, and its limits.",
                   "LTFS: The Linear Tape File System",
                   "LTFS (Linear Tape File System) lets an LTO-5 or newer tape mount like a disk, so you copy files with the normal file manager and any LTFS system can read the tape; free tools exist from IBM, HPE and Quantum and as open source.",
                   "LTFS guide", sections, faqs, PUBLISHED, [("Home", "/"), ("Resources", "/resources"), ("LTFS", path)])


# ---------------------------------------------------------------- data recovery

def build_recovery(current):
    path = "/resources/lto-tape-data-recovery"
    rows = [[x, SPECS[x]["native"], ", ".join(d for d in SPECS if x in _readable_by(d))] for x in list(SPECS)[1:]]
    sections = [
        sec("Step 1", "Find a drive that can read the tape", f"""
<p>The generation is printed on the cartridge and in the last two characters of the barcode label (L5 for LTO-5, L6 for LTO-6 and so on). Then find a drive that reads it:</p>
{table(["Cartridge", "Native capacity", "Drives that read it"], rows, "Which drive reads which LTO tape")}
<p>LTO-2 to LTO-5 drives are now only sold used. Buy from a seller who states head hours and offers returns, and test the drive with a cartridge you do not need.</p>"""),
        sec("Step 2", "Find out what wrote the tape", """
<p>A drive returns raw blocks; the software that wrote them decides how you get files back.</p>
<ul>
<li><strong>LTFS:</strong> mount it with any LTFS tool and copy the files. See <a href="/resources/ltfs">LTFS explained</a>.</li>
<li><strong>tar or other Unix tools:</strong> read it back with the same tool on Linux.</li>
<li><strong>Backup software</strong> (Backup Exec, NetBackup, Commvault, ArcServe, Retrospect, Veeam, Spectrum Protect and others): you need that product, ideally the same or a newer version. If the catalogue is gone, most products can rebuild it by reading the tape, often called inventory and catalogue or import.</li>
</ul>
<p>The first blocks of the tape usually name the format; a recovery lab or the software vendor can tell you what wrote it.</p>"""),
        sec("Encryption", "Encrypted tapes", """
<p>Drives from LTO-4 onward can encrypt with AES-256. If a tape was encrypted by the drive or the backup software, it cannot be read without the key, and no lab can recover it without one. Look for the key in the backup software, the library's key manager or your key management server before anything else.</p>"""),
        sec("Damaged tapes", "When to stop and call a lab", """
<p>Stop retrying and send the cartridge to a data recovery lab if the tape is snapped, creased or wet, the leader pin is detached, the cartridge rattles or was dropped, or the drive reports a medium error repeatedly. Every extra attempt in a drive can stretch the tape or damage the head. Labs can splice tape, replace the cartridge shell and read past bad sections, and they charge by the cartridge and the work involved, so ask for a quote and a no-recovery, no-fee policy.</p>"""),
        sec("Then migrate", "Copy it to current media", """
<p>Once the data is back, copy it to current media and verify it, so you are not in the same position again in five years. See <a href="/resources/lto-tape-migration">LTO tape migration</a>.</p>"""),
        more_guides(path),
    ]
    faqs = [
        ("How do I read an old LTO tape?", "Find a drive of the same generation or one or two generations newer (see the table), connect it with a SAS HBA, and read the tape with the software that wrote it, or with an LTFS tool if it was written with LTFS."),
        ("Can an LTO-8 drive read LTO-6 tapes?", "No. LTO-8 drives read only LTO-7 and LTO-8. An LTO-6 tape needs an LTO-6 or LTO-7 drive."),
        ("What if I no longer have the backup software?", "Install the same or a newer version of that product and rebuild its catalogue from the tape. A recovery lab can also read most backup formats."),
        ("Can data be recovered from an encrypted LTO tape without the key?", "No. LTO drive encryption uses AES-256, and without the key the data cannot be read."),
        ("Can a broken LTO tape be recovered?", "Often, by a lab: snapped or damaged tape can be spliced and the cartridge shell replaced. Stop using it in a drive as soon as you see physical damage."),
    ]
    return article(path, "LTO Tape Data Recovery: Read Old LTO-2 to LTO-8",
                   "How to recover data from old LTO tapes: which drive reads which generation, backup software formats, encrypted tapes, and when to use a recovery lab.",
                   "LTO Tape Data Recovery",
                   "To recover data from an old LTO tape, find a drive that reads its generation (LTO-8 and newer read only one generation back), then read it with the software that wrote it or an LTFS tool; encrypted tapes need their key, and physically damaged tapes belong in a lab.",
                   "Recovery guide", sections, faqs, PUBLISHED, [("Home", "/"), ("Resources", "/resources"), ("LTO tape data recovery", path)])


def _readable_by(drive):
    """Generations a drive of this generation reads, as a list."""
    names = list(SPECS)
    i = names.index(drive)
    back = 2 if i < names.index("LTO-8") else (1 if drive != "LTO-10" else 0)
    return names[max(0, i - back):i + 1]


# ---------------------------------------------------------------- lifespan

def build_lifespan(current):
    path = "/why-tape/lto-tape-lifespan"
    sections = [
        sec("The 30-year figure", "Where the 30 years comes from", """
<p>Fujifilm, Sony and the drive vendors rate LTO cartridges for 30 years of archival storage. The figure comes from accelerated ageing tests of the magnetic coating and base film, and it assumes the cartridge is stored in controlled conditions and handled correctly. A cartridge kept in a hot car or a damp basement will not last that long.</p>"""),
        sec("Storage conditions", "How to store LTO tapes", """
<ul>
<li><strong>Temperature and humidity:</strong> 16 to 25 °C and 20 to 50% relative humidity for long-term storage, kept stable.</li>
<li><strong>Acclimatise before use:</strong> give cartridges about a day in the room with the drive if they come from a colder or warmer place.</li>
<li><strong>Keep them in their cases,</strong> upright, away from dust, direct sunlight and strong magnetic fields.</li>
<li><strong>Do not drop them.</strong> A dropped cartridge can lose its leader pin or shift the reel; test it before trusting it.</li>
</ul>"""),
        sec("Wear", "Loads and passes", """
<p>A cartridge is rated for many thousands of loads; LTO-9 media is rated for 20,000 load and unload cycles. An archive tape that is written once and read occasionally will never get near that. Tapes used for daily backups wear faster, which is one reason to rotate them and replace them on a schedule.</p>"""),
        sec("The real limit", "Drives run out before tapes do", f"""
<p>The tape usually outlives the drives that can read it. LTO-8 and newer drives read only one generation back, and new drives for older generations disappear within a few years. A perfectly preserved LTO-5 tape is useless without a working LTO-5, LTO-6 or LTO-7 drive.</p>
<p>So the practical lifespan of an archive is set by your migration plan: copy to current media every two or three generations, and keep at least one working drive for every generation still on your shelves. See <a href="/resources/lto-tape-migration">LTO tape migration</a>.</p>"""),
        sec("Compared", "Tape vs hard drive lifespan", """
<p>Hard drives are usually replaced after 4 to 6 years in service, and a drive left unpowered on a shelf for years is not designed for archival storage. Tape is designed to sit unpowered. See <a href="/why-tape/lto-vs-hdd">LTO vs HDD</a>.</p>"""),
        sec("Check", "Keep checking the archive", """
<p>Read a sample of cartridges back every year or two and compare checksums. Backup software can verify tapes on a schedule. It is the only way to know the archive is still readable before you need it.</p>"""),
        more_guides(path),
    ]
    faqs = [
        ("How long do LTO tapes last?", "Manufacturers rate them for 30 years of archival storage at 16 to 25 °C and 20 to 50% relative humidity. Drive availability usually ends earlier, so migrate every two or three generations."),
        ("What is the shelf life of LTO-9 tape?", "30 years in archival conditions, and the cartridge is rated for 20,000 load and unload cycles."),
        ("Does LTO tape degrade if not used?", "Slowly, and much more slowly than a hard drive left unpowered, as long as it is stored cool, dry and stable. Read samples back periodically to check."),
        ("Should I rewind or re-tension LTO tapes?", "No routine re-tensioning is needed for LTO. Store cartridges properly and let the drive handle tension when it reads them."),
    ]
    return article(path, "How Long Do LTO Tapes Last? Lifespan and Storage",
                   "LTO tape lifespan explained: the 30-year archival rating, storage temperature and humidity, load cycles, and why drive compatibility is the real limit.",
                   "How Long Do LTO Tapes Last?",
                   "LTO cartridges are rated for 30 years of archival storage at 16 to 25 °C and 20 to 50% humidity, but the practical limit is usually the drives: LTO-8 and newer read only one generation back, so plan to migrate every two or three generations.",
                   "Lifespan guide", sections, faqs, PUBLISHED, [("Home", "/"), ("Why tape", "/why-tape"), ("LTO tape lifespan", path)])


# ---------------------------------------------------------------- cleaning and labels

def build_supplies(current):
    path = "/resources/lto-cleaning-tapes-and-labels"
    sections = [
        sec("Cleaning", "LTO cleaning cartridges", """
<p>One universal LTO cleaning cartridge works in drives of every generation. It is rated for up to 50 cleanings, fewer in some drives, and the drive refuses it once it is used up.</p>
<p>Clean only when the drive asks for it. LTO drives signal when cleaning is needed and libraries can clean automatically; cleaning on a fixed schedule just wears the head. If a drive asks for cleaning very often, suspect a bad cartridge or a failing head.</p>"""),
        sec("Labels", "Barcode labels", """
<p>Libraries and autoloaders identify cartridges by barcode. The standard LTO label has six characters you choose, then a two-character media code: for example 000001L9 is an LTO-9 data cartridge and 000001L8 an LTO-8 one. WORM cartridges use their own codes (LZ for LTO-9 WORM, LY for LTO-8 WORM), and cleaning cartridges start with CLN.</p>
<p>Buy labels printed for your generation, keep the numbers unique across the whole library, and never put a label over the cartridge's write-protect switch or edges.</p>"""),
        sec("Cases and transport", "Cases for storage and offsite copies", """
<p>Keep each cartridge in its jewel case on a shelf, and use padded turtle-style cases for 5, 10 or 20 cartridges when moving tapes offsite. Avoid loose cartridges in a box: drops and dust are the most common causes of handling damage.</p>"""),
        sec("Disposal", "Destroying old tapes", """
<p>Erasing or overwriting a tape takes as long as filling it. For tapes with sensitive data, use a tape shredder or a destruction service that issues a certificate. Degaussing needs a degausser rated for high-coercivity barium ferrite media, and it also erases the servo tracks, so the cartridge cannot be reused afterwards.</p>"""),
        more_guides(path),
    ]
    faqs = [
        ("How many times can an LTO cleaning tape be used?", "Up to 50 times, fewer in some drives. The cartridge records its uses and the drive rejects it when it is used up."),
        ("How often should I clean an LTO drive?", "Only when the drive or library asks for it. Scheduled cleaning wears the head without benefit."),
        ("What does L9 mean on an LTO label?", "It is the media code for an LTO-9 data cartridge. L8 is LTO-8, L7 is LTO-7, and WORM cartridges use different codes such as LZ for LTO-9 WORM."),
        ("How do I safely destroy LTO tapes?", "Shred them or use a destruction service with a certificate. Degaussing works only with a degausser rated for the media, and the cartridge cannot be reused afterwards."),
    ]
    return article(path, "LTO Cleaning Tapes, Barcode Labels and Cases",
                   "LTO cleaning cartridges (how many uses, when to clean), barcode label codes like L9 and LZ, cases for offsite tapes, and how to destroy old tapes.",
                   "LTO Cleaning Tapes, Labels and Handling",
                   "A universal LTO cleaning cartridge works in every generation and lasts up to 50 cleanings, but clean only when the drive asks; library barcode labels end in a media code such as L9 for LTO-9 data or LZ for LTO-9 WORM.",
                   "Supplies guide", sections, faqs, PUBLISHED, [("Home", "/"), ("Resources", "/resources"), ("Cleaning tapes and labels", path)])


# ---------------------------------------------------------------- news

def build_news(current):
    path = "/lto-tape-news"
    with open(os.path.join(ROOT, "data", "news.json"), encoding="utf-8") as f:
        news = json.load(f)
    g = current["generations"]
    l9, l10 = g["LTO-9"], g["LTO-10"]
    where = "" if BP.MKT.is_us else f" in {BP.MKT.country}"
    items = "".join(f'<article class="faq-card"><h3>{esc(n["headline"])}</h3><p>{esc(n["summary"])}</p><p class="updated-note">{esc(n["source"])}, {esc(n["date"])}. <a href="{esc(n["url"])}" rel="nofollow noopener">Source</a></p></article>' for n in news["items"])
    sections = [
        sec("Prices", f"LTO prices in {CURRENT_LABEL}", f"""
<p>LTO-9 cartridges cost {rng(l9['cartridge'], True)}{where} ({per_tb(l9['cartridge'])} per TB) and 30 TB LTO-10 cartridges {rng(l10['cartridge'], True)}, checked on {date_text()}. Media prices have been broadly flat through 2026, while hard drive prices rose sharply. Every listing is in the <a href="/lto-tape-price-trend">LTO price tracker</a>, and earlier months in the <a href="/lto-tape-price-trend/history">price history</a>.</p>"""),
        f'<section class="section-card"><p class="eyebrow">News</p><h2>{esc(news["title"])}</h2></section><section class="faq-grid" aria-label="LTO tape news">{items}</section>',
        more_guides(path),
    ]
    faqs = [
        ("Are LTO tape shipments growing?", "Yes again in 2026. The LTO Program reported 160.3 EB shipped in 2025, down 9% from the 2024 record, and a 57% rise in the first quarter of 2026."),
        ("Is there a 40 TB LTO-10 tape?", "Yes. 40 TB LTO-10 cartridges from Fujifilm and IBM began shipping in 2026 and work in existing LTO-10 drives."),
        ("Are half-height LTO-10 drives available?", "Not yet at the sellers we checked in September 2026. LTO-10 drives so far ship as full-height units."),
    ]
    return article(path, f"LTO Tape News: {news['month']} Roundup | TapeBackup",
                   f"LTO tape news for {news['month']}: shipments, 40 TB LTO-10 cartridges, LTO-10 drives, the roadmap and current LTO-9 and LTO-10 prices.",
                   f"LTO Tape News, {news['month']}",
                   news["answer"], "News roundup", sections, faqs, PUBLISHED, [("Home", "/"), ("LTO tape news", path)])


def build_all(current):
    return [build_pillar(current), build_capacity(current), build_drive_guide(current), build_library(current), build_ltfs(current),
            build_recovery(current), build_lifespan(current), build_supplies(current), build_news(current)]
