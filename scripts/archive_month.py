"""Archive the outgoing month's US prices as a snapshot in data/price-history.json.

    python3 scripts/archive_month.py 2026-09 "September 2026" 2026-09-17

Reads data/prices-<month>.json, summarises each generation the same way the site does
(markets.normalise: single new cartridges, odd prices and out-of-stock listings left out
of the range) and prepends a snapshot with slug like "sep-2026". Re-running replaces the
snapshot with the same slug. Then bump PRICE_MONTH in markets.py, the CURRENT_* labels in
build_prices.py, and add the slug to ARCHIVE_TITLES there.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import markets

month, label, iso = sys.argv[1], sys.argv[2], sys.argv[3]
raw = json.load(open(os.path.join(markets.DATA, f"prices-{month}.json"), encoding="utf-8"))
gens = markets.normalise(raw, 0, "us")
n = sum(len((g.get(i) or {}).get("datapoints", [])) for g in gens.values() for i in markets.ITEMS)
sellers = sorted({d["seller"] for g in gens.values() for i in markets.ITEMS for d in (g.get(i) or {}).get("datapoints", [])})


def money(v):
    return f"${v:,.2f}" if v < 1000 else f"${v:,.0f}"


def rng(item):
    if not item or item.get("low") is None:
        return "Not listed"
    return money(item["low"]) if abs(item["high"] - item["low"]) < .01 else f"{money(item['low'])}-{money(item['high'])}"


cartridges, drives = {}, {}
for gen, g in gens.items():
    c = g.get("cartridge") or {}
    if c.get("low") is not None:
        cartridges[gen] = {"range": rng(c), "perTB": f"${c['perTBLow']:.2f}-${c['perTBHigh']:.2f}/TB" if c["perTBHigh"] != c["perTBLow"] else f"${c['perTBLow']:.2f}/TB"}
    if (g.get("driveInternal") or {}).get("low") is not None or (g.get("driveExternal") or {}).get("low") is not None:
        drives[gen] = {"internal": rng(g.get("driveInternal")), "external": rng(g.get("driveExternal"))}
notes = [f"Single new cartridges and new standalone drives from {n} listings at {len(sellers)} US sellers ({', '.join(sellers)}), checked on {label.split()[0]} {iso[8:].lstrip('0')}, {iso[:4]}."
         .replace(f"{label.split()[0]} {iso[8:].lstrip('0')}, {iso[:4]}", f"{int(iso[8:])} {label}")]
c40 = (gens.get("LTO-10") or {}).get("cartridge40TB") or {}
if c40.get("low") is not None:
    notes.append(f"The 40 TB LTO-10 cartridge was listed at {rng(c40)} (${c40['perTBLow']:.2f}-${c40['perTBHigh']:.2f} per TB); the LTO-10 row above is the 30 TB cartridge.")
for mn in raw.get("marketNotes", []):
    if mn.get("text") and not mn["text"].startswith("Not found"):
        notes.append(mn["text"])
slug = f"{label.split()[0][:3].lower()}-{iso[:4]}"
snap = {
    "slug": slug, "label": label, "period": label, "published": iso,
    "source": f"Seller listings checked on {int(iso[8:])} {label} at US tape sellers, published as the {label} edition of the LTO price tracker.",
    "summary": f"The {label} edition of the LTO price tracker: {n} new listings from {len(sellers)} US tape sellers, with single-cartridge price ranges and new drive prices for LTO-6 to LTO-10.",
    "cartridges": cartridges, "drives": drives, "drivesNote": "Seller listings for new standalone SAS drives.", "notes": notes,
}
path = os.path.join(markets.DATA, "price-history.json")
hist = json.load(open(path, encoding="utf-8"))
hist["snapshots"] = [snap] + [s for s in hist["snapshots"] if s["slug"] != slug]
json.dump(hist, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"archived {slug}: {len(cartridges)} cartridge rows, {len(drives)} drive rows, {n} listings")
