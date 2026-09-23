"""Price markets: which seller data, currency and tax rules a build uses.

The English site is the "us" market (US sellers, USD, prices before tax). Each
European language edition is built as its own market from data/eu/, in the
local currency with VAT included, and then translated by scripts/i18n.py.

Builders never format numbers for a locale. They write English-format numbers
with the market's currency symbol ($92.45, €81.90, zł368.00); i18n.py turns
those into 92,45 € / € 81,90 / 368,00 zł for each language at render time.
"""

import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

PRICE_MONTH = "2026-09"

MARKETS = {
    "us": {"lang": "en", "country": "the United States", "country_short": "US", "currency": "USD", "sym": "$", "vat": 0.0,
           "file": f"prices-{PRICE_MONTH}.json"},
    "de": {"lang": "de", "country": "Germany", "country_short": "Germany", "currency": "EUR", "sym": "€", "vat": 0.19,
           "file": f"eu/prices-de-{PRICE_MONTH}.json"},
    "fr": {"lang": "fr", "country": "France", "country_short": "France", "currency": "EUR", "sym": "€", "vat": 0.20,
           "file": f"eu/prices-fr-{PRICE_MONTH}.json", "fallback": "de"},
    "it": {"lang": "it", "country": "Italy", "country_short": "Italy", "currency": "EUR", "sym": "€", "vat": 0.22,
           "file": f"eu/prices-it-{PRICE_MONTH}.json", "fallback": "de"},
    "es": {"lang": "es", "country": "Spain", "country_short": "Spain", "currency": "EUR", "sym": "€", "vat": 0.21,
           "file": f"eu/prices-es-{PRICE_MONTH}.json", "fallback": "de"},
    "nl": {"lang": "nl", "country": "the Netherlands", "country_short": "Netherlands", "currency": "EUR", "sym": "€", "vat": 0.21,
           "seller_region": "the Netherlands and Belgium",
           "file": f"eu/prices-nl-{PRICE_MONTH}.json", "fallback": "de"},
    "pl": {"lang": "pl", "country": "Poland", "country_short": "Poland", "currency": "PLN", "sym": "zł", "vat": 0.23,
           "file": f"eu/prices-pl-{PRICE_MONTH}.json"},
}

LANG_TO_MARKET = {m["lang"]: code for code, m in MARKETS.items()}

ITEMS = ("cartridge", "cartridge40TB", "worm", "driveInternal", "driveExternal")
DROP_NOTE = re.compile(r"excluded|price not accurate|listing error", re.I)
PACK_NOTE = re.compile(r"(\d+)\s*-?\s*pack", re.I)

# Brand from part number, used to split "major brand" and "OEM" (Fujifilm/Sony) prices.
BRANDS = [
    ("Fujifilm", re.compile(r"^(?:1[5-9]\d{6})\b|fujifilm", re.I)),
    ("Sony", re.compile(r"^LTX|sony", re.I)),
    ("HPE", re.compile(r"^(?:C79\d\d|Q20\d\d|Q1G|BC0\d\d|BB87|EH9)|\bhpe\b", re.I)),
    ("IBM", re.compile(r"^(?:00V|38L|01PL|02XW|03PL|46X|35P|3850|3580)|\bibm\b", re.I)),
    ("Quantum", re.compile(r"^(?:MR-|TD-)|quantum", re.I)),
    ("Dell", re.compile(r"\bdell\b", re.I)),
]


def brand_of(dp):
    text = f"{dp.get('sku', '')} {dp.get('note', '')}"
    for name, rx in BRANDS:
        if rx.search(dp.get("sku", "") or "") or rx.search(text):
            return name
    return ""


def _load(rel):
    fake = os.environ.get("TB_FAKE_EU")
    if fake and rel.startswith("eu/prices-"):
        rel = os.path.relpath(fake, DATA)
    p = os.path.join(DATA, rel)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def _norm_dp(dp, vat, src_market, sym=""):
    price = dp.get("price", dp.get("priceUSD"))
    if price is None:
        return None
    note = (dp.get("note") or "").strip()
    if DROP_NOTE.search(note):
        return None
    gross = float(price)
    net_note = ""
    if vat and dp.get("vatIncluded") is False:
        gross = round(gross * (1 + vat), 2)
        net_note = "VAT added to the net price"
    m = PACK_NOTE.search(note)
    pack = int(m.group(1)) if m and int(m.group(1)) > 1 else None
    note = re.sub(r"seen \d{4}-\d{2}-\d{2};?\s*", "", note).strip(" ;")
    if sym:
        note = re.sub(r"\+\s?(?:EUR|€|zł|PLN)?\s?(\d+(?:[.,]\d{1,2})?)\s*(?:EUR|€|zł|PLN)?\s*(shipping|delivery)", lambda m: f"+{sym}{m.group(1).replace(',', '.')} {m.group(2)}", note)
    if net_note:
        note = f"{note}; {net_note}" if note else net_note
    sku = re.sub(r"^\d+__", "", (dp.get("sku") or "").strip())
    return {"seller": dp.get("seller", ""), "sku": sku, "price": gross, "url": dp.get("url", ""),
            "note": note, "pack": pack, "unit": round(gross / pack, 2) if pack else None, "market": src_market}


OUT_OF_STOCK = re.compile(r"(?:^|;\s*)(?:out of stock|sold out)(?:$|[;,])", re.I)


def _summarise(dps, native_tb):
    """Range of single-unit prices. Out-of-stock listings and prices under half or over twice the
    median, or more than 1.75 times it, stay in the listing tables but not in the headline range."""
    singles = [d for d in dps if not d["pack"]]
    if not singles:
        return {"low": None, "high": None, "perTBLow": None, "perTBHigh": None, "datapoints": dps}
    prices = sorted(d["price"] for d in singles)
    median = prices[len(prices) // 2] if len(prices) % 2 else (prices[len(prices) // 2 - 1] + prices[len(prices) // 2]) / 2
    for d in singles:
        odd = len(prices) >= 4 and not (0.5 * median <= d["price"] <= 1.75 * median)
        oos = bool(OUT_OF_STOCK.search(d["note"]))
        d["in_range"] = not (odd or oos)
        if not d["in_range"] and "not counted in the range" not in d["note"]:
            d["note"] = (d["note"] + "; " if d["note"] else "") + "not counted in the range"
    counted = [d["price"] for d in singles if d["in_range"]] or prices
    lo, hi = min(counted), max(counted)
    return {"low": lo, "high": hi, "perTBLow": round(lo / native_tb, 2) if native_tb else None,
            "perTBHigh": round(hi / native_tb, 2) if native_tb else None, "datapoints": dps}


def normalise(raw, vat, src_market, sym=""):
    gens = {}
    for gen, g in raw["generations"].items():
        native = g.get("nativeTB")
        out = {"nativeTB": native, "status": g.get("status", ""), "notes": g.get("notes", "")}
        for item in ITEMS:
            if item not in g:
                continue
            dps = [x for x in (_norm_dp(d, vat, src_market, sym) for d in g[item].get("datapoints", [])) if x]
            tb = 40 if item == "cartridge40TB" else native
            out[item] = _summarise(dps, tb if item in ("cartridge", "cartridge40TB", "worm") else None)
        gens[gen] = out
    return gens


class Market:
    def __init__(self, code, fx=None):
        cfg = MARKETS[code]
        self.code = code
        self.lang = cfg["lang"]
        self.country = cfg["country"]
        self.country_short = cfg["country_short"]
        self.seller_region = cfg.get("seller_region", cfg["country"])
        self.currency = cfg["currency"]
        self.sym = cfg["sym"]
        self.vat = cfg["vat"]
        self.is_us = code == "us"
        self.fx = fx or {}
        raw = _load(cfg["file"])
        if raw is None:
            raise SystemExit(f"missing price data for market {code}: data/{cfg['file']}")
        self.raw = raw
        self.as_of = raw.get("asOf", "")
        self.generations = normalise(raw, self.vat, code, self.sym)
        self.fallback_used = []
        fb = cfg.get("fallback")
        if fb:
            fb_raw = _load(MARKETS[fb]["file"])
            if fb_raw:
                fb_gens = normalise(fb_raw, MARKETS[fb]["vat"], fb, MARKETS[fb]["sym"])
                for gen, g in self.generations.items():
                    for item in ITEMS:
                        mine = g.get(item)
                        theirs = fb_gens.get(gen, {}).get(item)
                        if theirs and theirs["low"] is not None and (not mine or mine["low"] is None):
                            dps = [dict(d, note=(d["note"] + "; " if d["note"] else "") + f"seller in {MARKETS[fb]['country']}") for d in theirs["datapoints"]]
                            tb = 40 if item == "cartridge40TB" else g["nativeTB"]
                            g[item] = _summarise(dps, tb if item in ("cartridge", "cartridge40TB", "worm") else None)
                            self.fallback_used.append((gen, item))
        self.market_notes = raw.get("marketNotes", [])
        self.sellers_tried = raw.get("sellersTried", [])

    # USD per unit of this market's currency is not needed; builders need the other way round.
    def from_usd(self, usd):
        """Convert a USD amount into this market's currency at the ECB reference rate."""
        if self.is_us:
            return usd
        return usd * self.fx["per_usd"][self.currency]

    def blocked_sellers(self):
        return [s["seller"] for s in self.sellers_tried if "block" in (s.get("result") or "").lower()]

    def sellers_used(self):
        names = set()
        for g in self.generations.values():
            for item in ITEMS:
                for d in (g.get(item) or {}).get("datapoints", []):
                    if d["market"] == self.code:
                        names.add(d["seller"])
        return sorted(names)


def load_fx():
    fx = _load(f"eu/fx-{PRICE_MONTH}.json")
    if not fx:
        raise SystemExit("missing data/eu/fx file; run scripts/fetch_fx.py")
    return fx
