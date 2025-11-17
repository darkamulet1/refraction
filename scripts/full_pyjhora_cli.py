#!/usr/bin/env python
"""
full_pyjhora_cli.py

Generic CLI that produces the full PyJHora JSON snapshot for any birth chart.
"""

from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path

from v0min.core_time import make_birth_context
from v0min.full_extract import build_full_pyjhora_payload, save_payload, summarize_payload


def parse_local_datetime(date_str: str, time_str: str) -> datetime:
    try:
        year, month, day = (int(part) for part in date_str.split("-"))
    except ValueError as exc:
        raise ValueError(f"Invalid date '{date_str}'. Use YYYY-MM-DD.") from exc

    time_parts = time_str.split(":")
    if len(time_parts) == 2:
        time_parts.append("0")
    if len(time_parts) != 3:
        raise ValueError(f"Invalid time '{time_str}'. Use HH:MM[:SS].")
    try:
        hour, minute, second = (int(part) for part in time_parts)
    except ValueError as exc:
        raise ValueError(f"Invalid time component in '{time_str}'.") from exc
    return datetime(year, month, day, hour, minute, second)


def validate_coordinates(lat: float, lon: float) -> None:
    if not (-90.0 <= lat <= 90.0):
        raise ValueError(f"Latitude {lat} out of bounds (-90 to 90).")
    if not (-180.0 <= lon <= 180.0):
        raise ValueError(f"Longitude {lon} out of bounds (-180 to 180).")


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.strip().lower())
    slug = slug.strip("_")
    return slug or "person"


def main() -> None:
    parser = argparse.ArgumentParser(description="Produce a full PyJHora JSON snapshot for any chart.")
    parser.add_argument("--date", required=True, help="Local date in YYYY-MM-DD format.")
    parser.add_argument("--time", required=True, help="Local time in HH:MM[:SS] format.")
    parser.add_argument("--lat", required=True, type=float, help="Latitude in decimal degrees.")
    parser.add_argument("--lon", required=True, type=float, help="Longitude in decimal degrees.")
    parser.add_argument("--tz", required=True, help="IANA timezone name (e.g., Asia/Tehran).")
    parser.add_argument("--name", required=True, help="Person name stored in the snapshot.")
    parser.add_argument(
        "--location-name",
        help="Human-readable location label (defaults to person name).",
    )
    parser.add_argument(
        "--out",
        help="Destination JSON path (defaults to references/out/<slug>_full_pyjhora.json).",
    )
    parser.add_argument(
        "--print-only",
        action="store_true",
        help="Print summary only without writing a JSON file.",
    )
    parser.add_argument(
        "--no-print",
        action="store_true",
        help="Write JSON only; suppress stdout summary.",
    )

    args = parser.parse_args()
    if args.print_only and args.no_print:
        parser.error("--print-only and --no-print cannot be used together.")

    dt_local = parse_local_datetime(args.date, args.time)
    validate_coordinates(args.lat, args.lon)
    location_name = args.location_name or args.name

    bc = make_birth_context(
        dt_local,
        args.lat,
        args.lon,
        tz_name=args.tz,
        location_name=location_name,
    )
    payload = build_full_pyjhora_payload(bc, person=args.name, location_name=location_name)

    if not args.print_only:
        out_path = Path(
            args.out
            or Path("references/out") / f"{slugify(args.name)}_full_pyjhora.json"
        )
        save_payload(payload, out_path)
        if not args.no_print:
            print(f"Snapshot written to {out_path.resolve()}")

    if not args.no_print:
        for line in summarize_payload(payload):
            print(line)


if __name__ == "__main__":
    main()
