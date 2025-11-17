#!/usr/bin/env python
"""
CLI utility to export Varshaphal/Tajaka snapshots for a given year.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from jhora.panchanga import drik

from v0min.core_time import make_birth_context
from v0min.varshaphal_extract import (
    compute_varshaphal_snapshot,
    compute_varshaphal_subperiods,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a PyJHora Varshaphal/Tajaka snapshot from an existing *_full_pyjhora.json file."
    )
    parser.add_argument("--birth-json", required=True, help="Path to *_full_pyjhora.json payload.")
    parser.add_argument("--year", required=True, type=int, help="Target Gregorian year for the solar return.")
    parser.add_argument(
        "--include",
        action="append",
        choices=["sahams", "dashas", "tajaka_aspects"],
        help="Optional sections to include explicitly. Defaults to all blocks.",
    )
    parser.add_argument(
        "--include-maasa",
        action="store_true",
        help="Include Maasa (monthly) sub-period charts.",
    )
    parser.add_argument(
        "--maasa-months",
        nargs="+",
        type=int,
        help="Restrict Maasa charts to specific month indices (1..12). Implies --include-maasa.",
    )
    parser.add_argument(
        "--include-sixty-hour",
        action="store_true",
        help="Include 60-hour Tajaka sub-period charts.",
    )
    parser.add_argument(
        "--sixty-indices",
        nargs="+",
        type=int,
        help="Restrict 60-hour charts to specific indices (0-based). Implies --include-sixty-hour.",
    )
    parser.add_argument(
        "--out",
        help="Destination path for the Varshaphal JSON. If omitted, the payload is printed to stdout.",
    )
    parser.add_argument(
        "--no-print",
        action="store_true",
        help="Suppress printing to stdout when --out is used.",
    )
    return parser.parse_args()


def load_birth_snapshot(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_context_from_snapshot(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    birth_data = snapshot["birth_data"]
    location = birth_data.get("location", {})
    dt_local = datetime.fromisoformat(birth_data["datetime_local"])
    bc = make_birth_context(
        dt_local.replace(tzinfo=None),
        location.get("lat"),
        location.get("lon"),
        tz_name=birth_data["timezone_name"],
        location_name=location.get("name"),
    )
    place_name = location.get("name") or birth_data.get("person") or "Birth Place"
    place = drik.Place(place_name, bc.latitude, bc.longitude, bc.utc_offset_hours)
    context = {
        "birth_context": bc,
        "place": place,
        "ayanamsa_mode": snapshot.get("core_chart", {}).get("ayanamsa_mode", "LAHIRI"),
        "location_name": location.get("name"),
    }
    return context


def write_json(data: Dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    birth_path = Path(args.birth_json)
    birth_snapshot = load_birth_snapshot(birth_path)
    context = build_context_from_snapshot(birth_snapshot)
    snapshot = compute_varshaphal_snapshot(context, args.year, include=args.include)
    include_maasa = args.include_maasa or bool(args.maasa_months)
    include_sixty = args.include_sixty_hour or bool(args.sixty_indices)
    if include_maasa or include_sixty:
        snapshot["subperiods"] = compute_varshaphal_subperiods(
            context,
            args.year,
            include_maasa=include_maasa,
            include_sixty_hour=include_sixty,
            maasa_months=args.maasa_months,
            sixty_indices=args.sixty_indices,
        )

    if args.out:
        write_json(snapshot, Path(args.out))
        if not args.no_print:
            print(f"Wrote Varshaphal snapshot to {Path(args.out).resolve()}")
    else:
        print(json.dumps(snapshot, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
