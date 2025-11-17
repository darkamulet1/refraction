#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from datetime import datetime, date
from pathlib import Path

from v0min.core_time import make_birth_context
from v0min.panchanga_calendar_extract import build_panchanga_calendar


def _parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a Panchanga calendar JSON payload.")
    parser.add_argument("--date-start", required=True, help="Start date (YYYY-MM-DD).")
    parser.add_argument("--date-end", required=True, help="End date (YYYY-MM-DD).")
    parser.add_argument("--lat", type=float, required=True, help="Latitude in decimal degrees.")
    parser.add_argument("--lon", type=float, required=True, help="Longitude in decimal degrees.")
    parser.add_argument("--tz", required=True, help="IANA timezone name.")
    parser.add_argument("--name", required=True, help="Person label.")
    parser.add_argument("--location-name", help="Optional location name label.")
    parser.add_argument("--out", help="Output JSON path.")
    parser.add_argument("--print-only", action="store_true", help="Print summary only.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    start = _parse_date(args.date_start)
    end = _parse_date(args.date_end)
    if end < start:
        raise ValueError("date-end must be >= date-start")

    bc_dt = datetime.combine(start, datetime.min.time())
    bc = make_birth_context(
        bc_dt,
        args.lat,
        args.lon,
        tz_name=args.tz,
        location_name=args.location_name or args.name,
    )

    calendar = build_panchanga_calendar(bc, start, end)

    if not args.print_only:
        out_path = Path(args.out or f"references/out/{args.name.lower()}_panchanga_calendar.json")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(calendar, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Calendar written to {out_path.resolve()}")

    print(
        f"Panchanga calendar generated for {calendar['place']['name']} "
        f"from {calendar['range']['start']} to {calendar['range']['end']}"
    )


if __name__ == "__main__":
    main()
