"""Compare a new month's price files with the previous month before publishing.

    python3 scripts/check_price_refresh.py 2026-09 2026-10

For every market and generation it prints the low/high range then and now, the number of
datapoints, and flags moves over 30% or lost items, so odd scrapes are caught before a build.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import markets

old_m, new_m = sys.argv[1], sys.argv[2]
FILES = {"us": "prices-{}.json", **{l: "eu/prices-%s-{}.json" % l for l in ("de", "fr", "it", "es", "nl", "pl")}}
VAT = {"us": 0, "de": .19, "fr": .2, "it": .22, "es": .21, "nl": .21, "pl": .23}
problems = 0
for mk, pat in FILES.items():
    paths = [os.path.join(markets.DATA, pat.format(m)) for m in (old_m, new_m)]
    if not os.path.exists(paths[1]):
        print(f"{mk}: MISSING {paths[1]}"); problems += 1; continue
    old, new = (json.load(open(p, encoding="utf-8")) for p in paths)
    try:
        go, gn = (markets.normalise(x, markets.MARKETS[mk]["vat"], mk) for x in (old, new))
    except Exception as e:
        print(f"{mk}: SCHEMA ERROR {e}"); problems += 1; continue
    print(f"== {mk} asOf {new.get('asOf')}")
    for gen in go:
        for item in markets.ITEMS:
            a, b = (go.get(gen) or {}).get(item), (gn.get(gen) or {}).get(item)
            if not a and not b:
                continue
            na, nb = len((a or {}).get("datapoints", [])), len((b or {}).get("datapoints", []))
            la, lb = (a or {}).get("low"), (b or {}).get("low")
            flag = ""
            if la is not None and lb is None:
                flag = " LOST"
            elif la and lb and abs(lb - la) / la > .30:
                flag = " MOVE>30%"
            if nb < na * .5:
                flag += " FEWER-DATAPOINTS"
            if flag:
                problems += 1
            print(f"  {gen:7} {item:14} {la}-{(a or {}).get('high')} ({na}) -> {lb}-{(b or {}).get('high')} ({nb}){flag}")
print(f"\n{problems} flags")
