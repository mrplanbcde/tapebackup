"""Fetch ECB euro reference rates and store USD/PLN conversion factors.

    python3 scripts/fetch_fx.py

Writes data/eu/fx-<month>.json. Used only where a figure has no local price
source (cloud list prices are published in USD; a few rough estimates in the
guides are converted and marked approximate).
"""

import json
import os
import re
import urllib.request

from markets import DATA, PRICE_MONTH

URL = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"


def main():
    xml = urllib.request.urlopen(URL, timeout=30).read().decode()
    day = re.search(r"time=['\"](\d{4}-\d{2}-\d{2})['\"]", xml).group(1)
    rates = {m.group(1): float(m.group(2)) for m in re.finditer(r"currency=['\"](\w{3})['\"]\s+rate=['\"]([\d.]+)['\"]", xml)}
    usd, pln = rates["USD"], rates["PLN"]
    out = {"source": URL, "date": day, "eur_per": {"USD": usd, "PLN": pln},
           "per_usd": {"USD": 1.0, "EUR": round(1 / usd, 6), "PLN": round(pln / usd, 6)}}
    path = os.path.join(DATA, "eu", f"fx-{PRICE_MONTH}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out))


if __name__ == "__main__":
    main()
