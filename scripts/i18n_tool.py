"""Helpers for translating segments in batches and checking the result.

    python3 scripts/i18n_tool.py export <lang> <parts> <part>
        writes .build/i18n-batches/<lang>-<part>.json: the untranslated segments of
        that part as [{id, key, ctx, example, maxlen}]
    python3 scripts/i18n_tool.py merge <lang> <part> <translations.json>
        validates {id: translation} against the batch and stores the good ones in
        data/i18n/tm/<lang>.<part>.json; prints every rejected id with the reason
    python3 scripts/i18n_tool.py check <lang>
        validates the whole translation memory for a language
    python3 scripts/i18n_tool.py set <lang> <fixes.json>
        replaces existing translations ({English key: new translation}) after review

Segments come from data/i18n/segments/<lang>.json, which scripts/build_site.py
rewrites on every build with whatever is still untranslated.
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import i18n  # noqa: E402

BATCH_DIR = os.path.join(i18n.ROOT, ".build", "i18n-batches")
LIMITS = {"title": 60, "meta og:title": 60, "meta twitter:title": 60,
          "meta description": 155, "meta og:description": 155, "meta twitter:description": 155}


def seg_rows(lang):
    with open(os.path.join(i18n.I18N, "segments", f"{lang}.json"), encoding="utf-8") as f:
        return json.load(f)


def maxlen(row):
    lims = [LIMITS[c] for c in row["ctx"] if c in LIMITS]
    return min(lims) if lims else None


def export(lang, parts, part, label=None):
    label = label or str(part)
    rows = seg_rows(lang)
    rows.sort(key=lambda r: (min(i18n.SCOPE.index(p) for p in r["pages"]) if r["pages"] else 99, r["key"]))
    chunk = [r for i, r in enumerate(rows) if i % parts == part - 1]
    out = [{"id": f"{lang}{label}-{i}", "key": r["key"], "ctx": r["ctx"], "example": r["example"], "maxlen": maxlen(r)} for i, r in enumerate(chunk)]
    os.makedirs(BATCH_DIR, exist_ok=True)
    path = os.path.join(BATCH_DIR, f"{lang}-{label}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    words = sum(len(re.sub(r"</?[a-z]+\d+/?>|\{\w+\}", " ", r["key"]).split()) for r in out)
    print(f"{path}: {len(out)} segments, {words} words")


def rendered_len(row, tgt):
    """Approximate final length: placeholders replaced by the English example's values."""
    ex_vals = re.findall(r"\S*\d\S*", row.get("example", ""))
    s = re.sub(r"</?[a-z]+\d+/?>", "", tgt)
    s = re.sub(r"\{(\d+)\}", lambda m: ex_vals[int(m.group(1))] if int(m.group(1)) < len(ex_vals) else "0000", s)
    return len(s.replace("&amp;", "&"))


def problems(row, tgt):
    errs = []
    if not isinstance(tgt, str) or not tgt.strip():
        return ["empty"]
    if not i18n.valid_translation(row["key"], tgt):
        a, b = i18n.tokens_of(row["key"]), i18n.tokens_of(tgt)
        errs.append(f"tokens differ: expected {a}, got {b}")
    if re.search(r"(?<![{\w])\d", re.sub(r"\{\w+\}|</?[a-z]+\d+/?>", "", tgt)):
        errs.append("contains digits outside placeholders")
    if "—" in tgt or " – " in tgt:
        errs.append("uses an em or en dash as punctuation")
    lim = row.get("maxlen") or maxlen(row)
    if lim and rendered_len(row, tgt) > lim:
        errs.append(f"too long: about {rendered_len(row, tgt)} characters, limit {lim}")
    return errs


def merge(lang, part, file):
    with open(os.path.join(BATCH_DIR, f"{lang}-{part}.json"), encoding="utf-8") as f:
        batch = {r["id"]: r for r in json.load(f)}
    with open(file, encoding="utf-8") as f:
        got = json.load(f)
    tm_path = os.path.join(i18n.I18N, "tm", f"{lang}.{part}.json")
    tm = json.load(open(tm_path, encoding="utf-8")) if os.path.exists(tm_path) else {}
    ok, bad = 0, []
    for sid, tgt in got.items():
        row = batch.get(sid)
        if not row:
            bad.append((sid, ["unknown id"]))
            continue
        errs = problems(row, tgt)
        if errs:
            bad.append((sid, errs))
            continue
        tm[row["key"]] = tgt.strip()
        ok += 1
    os.makedirs(os.path.dirname(tm_path), exist_ok=True)
    with open(tm_path, "w", encoding="utf-8") as f:
        json.dump(tm, f, ensure_ascii=False, indent=1, sort_keys=True)
    missing = [sid for sid in batch if batch[sid]["key"] not in tm]
    print(f"merged {ok}, rejected {len(bad)}, still untranslated in this batch {len(missing)}")
    for sid, errs in bad:
        print(f"  {sid}: {'; '.join(errs)}")


def set_fixes(lang, file):
    """Override existing translations: {English key: new translation}, stored in tm/<lang>.zfix.json (loaded last)."""
    with open(file, encoding="utf-8") as f:
        got = json.load(f)
    tm_all = i18n.load_tm(lang)
    path = os.path.join(i18n.I18N, "tm", f"{lang}.zfix.json")
    fixes = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
    ok, bad = 0, []
    for key, tgt in got.items():
        if key not in tm_all:
            bad.append((key, ["key not in translation memory"]))
            continue
        errs = problems({"key": key, "ctx": [], "example": ""}, tgt)
        errs = [e for e in errs if not e.startswith("too long")]
        if errs:
            bad.append((key, errs))
            continue
        fixes[key] = tgt.strip()
        ok += 1
    with open(path, "w", encoding="utf-8") as f:
        json.dump(fixes, f, ensure_ascii=False, indent=1, sort_keys=True)
    print(f"fixed {ok}, rejected {len(bad)}")
    for key, errs in bad:
        print(f"  {key[:80]!r}: {'; '.join(errs)}")


def add_keys(lang, file):
    """Add translations keyed by the English key ({key: translation}) for segments not in any batch."""
    with open(file, encoding="utf-8") as f:
        got = json.load(f)
    path = os.path.join(i18n.I18N, "tm", f"{lang}.add.json")
    tm = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
    ok, bad = 0, []
    for key, tgt in got.items():
        errs = [e for e in problems({"key": key, "ctx": [], "example": ""}, tgt) if not e.startswith("too long")]
        if errs:
            bad.append((key, errs))
            continue
        tm[key] = tgt.strip()
        ok += 1
    with open(path, "w", encoding="utf-8") as f:
        json.dump(tm, f, ensure_ascii=False, indent=1, sort_keys=True)
    print(f"added {ok}, rejected {len(bad)}")
    for key, errs in bad:
        print(f"  {key[:80]!r}: {'; '.join(errs)}")


def check(lang):
    tm = i18n.load_tm(lang)
    n = 0
    for key, tgt in tm.items():
        row = {"key": key, "ctx": [], "example": ""}
        errs = [e for e in problems(row, tgt) if not e.startswith("too long")]
        if errs:
            n += 1
            print(f"  {key[:80]!r}: {'; '.join(errs)}")
    print(f"{lang}: {len(tm)} entries, {n} with problems")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "export":
        export(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5] if len(sys.argv) > 5 else None)
    elif cmd == "merge":
        merge(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == "check":
        check(sys.argv[2])
    elif cmd == "add":
        add_keys(sys.argv[2], sys.argv[3])
    elif cmd == "set":
        set_fixes(sys.argv[2], sys.argv[3])
