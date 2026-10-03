"""Turn an Ahrefs "matching terms" export into a tape keyword map.

    python3 scripts/seo_keyword_map.py <ahrefs-export.csv> docs/seo/keyword-map.csv

"LTO" also means the Philippine Land Transportation Office, limited-time
offers in fast food, lithium titanate batteries, link-time optimisation and
more, so most of an LTO export is noise. NOISE drops that; CLUSTERS assigns
each remaining keyword to the page that should rank for it (first match wins).
"""

import csv
import io
import re
import sys

NOISE = re.compile(r"""philippine|portal|licen[sc]e|plate|violation|registration|regist|motor|exhaust|pipe|muffler|helmet|mirror|enforcer|
    memorandum|ordinance|restriction|student|permit|renew|orcr|or/cr|ltms|tambutso|paano|bawal|pasok|exam|driving|driver|vehicle|car\b|cars\b|
    bacoor|bacolod|quezon|office|holiday|impound|vlogger|stunt|plaka|fee\b|penalt|obstruction|e30|
    food|menu|burger|sandwich|restaurant|chipotle|taco|arby|mcdonald|burger\ king|kfc|popeye|starbucks|shake\ shack|whataburger|dairy|
    sonic\b|freddy|jimmy|dutch\ bros|chick|soda|drink|flavor|sauce|pizza|coffee|ingredient|limited\ time|promo|seasonal|red\ ?bull|celsius|bubly|re-lyte|ghost|
    batter|lithium|titanate|cell|bms|lifepo4|lfp|scib|toshiba|yinlong|yinglong|lishen|xs\ power|car\ audio|d4s|down4sound|ah\ lto|\d+ah|bus\ bars|anode|
    voltage|charg|discharge|energy\ density|pouch|18650|nichicon|plannano|titan|ecklers|maritime|power\ bank|power\ solutions|
    crypto|coin|token|staking|network|wallet|lto\ to\ usd|interest\ rates|bank\b|
    leupold|thermal|tracker|white\ ultrium|lto\ 6\.0|rifle|minn\ kota|ultrex|hofstede|pdi\ idv|orientation|
    airport|flights|\bto\ lto|lto\ to\ |\bpdx|\bdfw|\bphx|\blax|\bsfo|\btij|owatonna|chicago|mexico|
    llvm|gcc|gentoo|compiler|lld|cachyos|mynixos|\bv\ lang|
    ring|ultrium\ metal|ultrium\ studios|ultrium\ medicine|hj\ ultrium|medical|
    marketing|business|slang|meaning\ in\ work|consulting|ventures|logistics|trucking|insurance|financing|management\ company|car\ rental|
    rollout|layoff|strategy|professional\ speaker|speakers|venture\ x|casio|aoi\ lto|joi\ lto|junji|chixroni|oh-lto|gold\ cask|fiktive|kasko|
    rj\ speed|thin\ lto|fat\ lto|lto\ kg|lto\ oz|lto\ top|lto\ deck|lto\ car|lto\ auto|lto\ material|lto\ cycle|lto\ machine|lto\ system|
    lto\ services|lto\ website|lto\ online|lto\ requirements|lto\ log\ in|lto\ training|lto\ shipping|lto\ region|lto\ e30|60138|66210|66160|
    treasure|target\ lto|gyselinck|norman|ao-vdm|holographic|lto\ logo|lto\ label\b|lto\ business|lto\ news\ philippines|lto\ coding|
    show\ lto\ fund|lto\ zellen|batera|bateria|lto\ product\ meaning|lto\ optimization|lto\ work|parking|lto\ ticket|lto\ lifespan|lto\ cycle""", re.I | re.X)

TAPEISH = re.compile(r"tape|ultrium|ltfs|cartridge|drive|lto[ -]?\d|backup|archiv|storage|library|autoloader|linear|powervault|storeever|"
                     r"scalar|spectra|qualstar|storagetek|unitex|mlogic|owc|recover|capacity|generation|roadmap|consortium|media|"
                     r"^lto$|^what is (an? )?lto|lto (meaning|definition|acronym|abbreviation|stands|full form)|what does lto|whats? an? lto|"
                     r"^lto (price|calculator|news|encryption|migration|reader|world|tracker\b)|dlt|магнитн|накопител|ленточн|磁带", re.I)

# (cluster, target page, status) — first match wins, so specific clusters come first.
CLUSTERS = [
    # "LTO" alone mostly means the Philippine LTO or a limited-time offer: count it, don't plan for it.
    ("Ambiguous head terms", "/lto-tape (secondary)", "mixed intent",
     r"^(lto|ultrium|what is (an? )?lto\??|whats? (an? )?lto|what('s| is) lto|what does lto( stand for| mean)?\??|lto (meaning|definition|acronym|abbreviation|full form|mean|means|stands for|stand for)|define lto|lto\.|a lto|what lto|lto acronym meaning|what lto stands for|lto stands for)$"),
    ("Data recovery", "/resources/lto-tape-data-recovery", "new", r"recover"),
    ("LTFS", "/resources/ltfs", "new", r"ltfs"),
    ("Backup and archive software", "/best-tape-backup-software", "exists", r"software|backup service|archive software"),
    ("News", "/lto-tape-news", "new", r"news"),
    ("Roadmap and LTO-11", "/lto-roadmap", "new", r"roadmap|lto[ -]?11|release date|consortium|generations|versions"),
    ("Lifespan and shelf life", "/why-tape/lto-tape-lifespan", "new", r"lifespan|shelf life|archival life|how long|longevity|last\b|end of service"),
    ("Price and cost", "/lto-tape-price-trend", "exists", r"price|cost|calculator|cheap|tracker\b"),
    ("Cleaning, labels, accessories", "/resources/lto-cleaning-tapes-and-labels", "new", r"clean|label|barcode|case\b|rack|shredder|destruction|dimensions|close up"),
    ("Libraries and autoloaders", "/lto-tape-library", "new", r"librar|autoloader|robot|scalar|spectra|qualstar|storagetek|sl150|ml3|msl"),
    ("Migration and conversion", "/resources/lto-tape-migration", "exists", r"migrat|conversion|transfer|to cloud"),
    ("Comparisons", "/why-tape/lto-vs-hdd", "exists", r"\bvs\b|versus|object storage"),
    ("Capacity and sizes", "/lto-tape-capacity", "new", r"capacity|sizes|\btb\b|native"),
    ("Drives", "/why-tape/lto-tape-drive", "exists", r"drive|reader|writer|deck|powervault|storeever|unitex|mlogic|owc|thunderbolt|usb|rent"),
    ("Generation pages", "/lto-N (per generation)", "expand", r"lto[ -]?\d|ultrium \d|ultrium[ -]?\d"),
    ("Cartridges and brands", "/lto-tape-brand", "exists", r"cartridge|fujifilm|fuji|hpe|ibm|quantum|dell|emc|sony|tapes\b|media"),
    ("What is LTO (pillar)", "/lto-tape", "new", r"."),
]
GEN = re.compile(r"(?:lto|ultrium)[ -]?(\d{1,2})\b", re.I)


def classify(k):
    for name, page, status, rx in CLUSTERS:
        if re.search(rx, k, re.I):
            if name == "Generation pages":
                m = GEN.search(k)
                g = m.group(1) if m else ""
                page = f"/lto-tape-price-trend/lto{g}-price" if g in ("6", "7", "8", "9", "10") else "/lto-tape (older generations section)"
            return name, page, status
    return None


def main(src, out):
    t = open(src, encoding="utf-16").read()
    rows = list(csv.DictReader(io.StringIO(t), delimiter="\t"))
    kept, dropped = [], 0
    for r in rows:
        k = r["Keyword"].strip()
        if NOISE.search(k) or not TAPEISH.search(k):
            dropped += 1
            continue
        name, page, status = classify(k)
        kept.append({"keyword": k, "volume": int(r["Volume"] or 0), "kd": r["Difficulty"], "traffic_potential": r["Traffic potential"],
                     "parent": r["Parent Keyword"], "cluster": name, "target_page": page, "page_status": status})
    kept.sort(key=lambda x: (x["cluster"], -x["volume"]))
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(kept[0].keys()))
        w.writeheader()
        w.writerows(kept)
    print(f"{len(rows)} keywords, {dropped} dropped as not about tape, {len(kept)} mapped -> {out}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
