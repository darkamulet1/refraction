#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
compare.py — Compare PyJHora YAML/CSV outputs against JHora reference tables.

Examples:
  # Single comparison
  python compare.py --ref JHORA_D1.txt --test "بازتاب/output/Mehran_D1.csv"

  # Single comparison for D9
  python compare.py --ref JHORA_D9.txt --test "بازتاب/output/Mehran_D9_m1.csv"

  # Batch mode with glob
  python compare.py --ref JHORA_D1.txt --tests "بازتاب/output/Mehran_D1*.csv"

  # Mixing CSV/YAML is fine
  python compare.py --ref JHORA_D9.txt --tests "بازتاب/output/Mehran_D9_*.yaml"
"""

from __future__ import annotations
import re
import csv
import math
import argparse
import sys
from pathlib import Path
from typing import Dict, Iterable, Tuple, List, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ZODIAC_INDEX = {
    "ar": 0,
    "ta": 1,
    "ge": 2,
    "cn": 3,
    "le": 4,
    "vi": 5,
    "li": 6,
    "sc": 7,
    "sg": 8,
    "sa": 8,
    "cp": 9,
    "aq": 10,
    "pi": 11,
}

REF_TO_TEST_NAME = {
    "lagna": "ascendant",
    "sun": "sun☉",
    "moon": "moon☾",
    "mars": "mars♂",
    "mercury": "mercury☿",
    "jupiter": "jupiter♃",
    "venus": "venus♀",
    "saturn": "saturn♄",
    "rahu": "raagu☊",
    "ketu": "kethu☋",
}

NAME_NORMALIZE = {
    "ascendant": "ascendant",
    "sun": "sun☉",
    "moon": "moon☾",
    "mars": "mars♂",
    "mercury": "mercury☿",
    "jupiter": "jupiter♃",
    "venus": "venus♀",
    "saturn": "saturn♄",
    "rahu": "raagu☊",
    "kethu": "kethu☋",
    "ketu": "kethu☋",
    "raagu": "raagu☊",
    "lagna": "ascendant",
}


def arcmin_delta(a_deg: float, b_deg: float) -> float:
    d = abs(a_deg - b_deg)
    if d > 180.0:
        d = 360.0 - d
    return d * 60.0


def _deg_from_tokens(parts: List[str]) -> float:
    if len(parts) < 4:
        raise ValueError(f"Cannot parse degree triplet from: {parts}")
    deg = float(parts[0])
    sign = parts[1].lower()
    mins = float(parts[2])
    secs = float(parts[3])
    z = ZODIAC_INDEX.get(sign[:2])
    if z is None:
        raise ValueError(f"Unknown sign {sign}")
    return z * 30.0 + deg + mins / 60.0 + secs / 3600.0


def parse_jhora_line(line: str) -> Optional[Tuple[str, float]]:
    s = line.strip()
    if not s or s.lower().startswith("body"):
        return None
    body = s.split()[0].replace("(R)", "").strip()
    cleaned = (
        s.replace("°", " ")
        .replace("’", " ")
        .replace("′", " ")
        .replace("″", " ")
        .replace("'", " ")
        .replace('"', " ")
    )
    tokens = cleaned.split()
    for i in range(1, len(tokens) - 3):
        try:
            float(tokens[i])
            sign = tokens[i + 1].lower()
            if sign[:2] not in ZODIAC_INDEX:
                continue
            float(tokens[i + 2])
            float(tokens[i + 3])
            abs_deg = _deg_from_tokens([tokens[i], tokens[i + 1], tokens[i + 2], tokens[i + 3]])
            mapped = REF_TO_TEST_NAME.get(body.lower(), body.lower())
            mapped = NAME_NORMALIZE.get(mapped, mapped).lower()
            return mapped, abs_deg
        except Exception:
            continue
    return None


def read_jhora_table(path: Path) -> Dict[str, float]:
    out: Dict[str, float] = {}
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            item = parse_jhora_line(line)
            if item is None:
                continue
            name, deg = item
            out[name] = deg
    return out


def read_pyjhora_csv(path: Path) -> Dict[str, float]:
    out: Dict[str, float] = {}
    with path.open(encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            body_raw = (row.get("body") or "").strip()
            if not body_raw:
                continue
            key = NAME_NORMALIZE.get(body_raw.lower(), body_raw.lower())
            deg_str = row.get("absolute_longitude_deg") or row.get("abs_deg")
            if deg_str is None:
                continue
            deg = float(deg_str)
            out[key] = deg
    return out


def read_pyjhora_yaml(path: Path) -> Dict[str, float]:
    try:
        import yaml  # type: ignore
    except ModuleNotFoundError:
        raise SystemExit("PyYAML not installed; install with `pip install pyyaml` or use CSV outputs.")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    out: Dict[str, float] = {}
    for pos in data.get("positions", []):
        body_raw = str(pos.get("body", "")).strip()
        if not body_raw:
            continue
        key = NAME_NORMALIZE.get(body_raw.lower(), body_raw.lower())
        deg = float(pos["absolute_longitude_deg"])
        out[key] = deg
    return out


def read_pyjhora_any(path: Path) -> Dict[str, float]:
    return read_pyjhora_csv(path) if path.suffix.lower() == ".csv" else read_pyjhora_yaml(path)


def compare_one(
    ref_map: Dict[str, float], test_map: Dict[str, float]
) -> Tuple[List[Tuple[str, float]], float, Tuple[str, float]]:
    common = sorted(set(ref_map) & set(test_map))
    deltas: List[Tuple[str, float]] = []
    for key in common:
        d = arcmin_delta(ref_map[key], test_map[key])
        deltas.append((key, d))
    if not deltas:
        return [], float("nan"), ("", float("nan"))
    mean_delta = sum(d for _, d in deltas) / len(deltas)
    worst = max(deltas, key=lambda x: x[1])
    return deltas, mean_delta, worst


def fmt_row(name: str, mean_delta: float, worst: Tuple[str, float]) -> str:
    worst_name, worst_val = worst
    return f"{name:32} -> mean delta = {mean_delta:6.3f} arcmin | max delta = {worst_val:6.3f} arcmin ({worst_name})"


def main():
    ap = argparse.ArgumentParser(description="Compare PyJHora outputs against JHora reference.")
    ap.add_argument("--ref", required=True, help="Path to JHora reference text (e.g., JHORA_D1.txt).")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--test", help="Single PyJHora file (CSV or YAML).")
    g.add_argument("--tests", help="Glob pattern for multiple PyJHora files.")
    ap.add_argument("--per-body", action="store_true", help="Print per-body deltas for single comparison.")
    args = ap.parse_args()

    ref_map = read_jhora_table(Path(args.ref))

    if args.test:
        test_path = Path(args.test)
        test_map = read_pyjhora_any(test_path)
        deltas, mean_delta, worst = compare_one(ref_map, test_map)
        print(fmt_row(test_path.name, mean_delta, worst))
        if args.per_body and deltas:
            for k, v in sorted(deltas, key=lambda x: x[0]):
                print(f"  - {k:12} : {v:6.3f} arcmin")
        missing_in_test = sorted(set(ref_map) - set(test_map))
        missing_in_ref = sorted(set(test_map) - set(ref_map))
        if missing_in_test:
            print(f"  (ignored; not in test): {', '.join(missing_in_test)}")
        if missing_in_ref:
            print(f"  (ignored; not in ref) : {', '.join(missing_in_ref)}")
        return

    matches = sorted(Path(".").glob(args.tests))
    if not matches:
        print(f"No files matched pattern: {args.tests}")
        return
    rows = []
    for p in matches:
        try:
            test_map = read_pyjhora_any(p)
            deltas, mean_delta, worst = compare_one(ref_map, test_map)
            rows.append((p.name, mean_delta, worst))
        except Exception as exc:
            rows.append((p.name, float("inf"), ("ERROR", float("inf"))))
            print(f"{p.name:32} -> ERROR: {exc}")
    rows.sort(key=lambda r: r[1])
    print("\n=== Summary (best -> worst) ===")
    for name, mean_delta, worst in rows:
        print(fmt_row(name, mean_delta, worst))


if __name__ == "__main__":
    main()
