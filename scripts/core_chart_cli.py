#!/usr/bin/env python
"""
core_chart_cli.py — Produce v0min core chart snapshots without PL/PDF tooling.

Example:
    python scripts/core_chart_cli.py --date 2004-01-27 --time 14:45:35 \
        --lat 35.84 --lon 50.96 --tz Asia/Tehran --name Athena --location-name Karaj
"""

from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path

from v0min.core_space import compute_core_chart
from v0min.core_time import make_birth_context
from v0min.io_core import save_core_chart


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


def build_payload(name: str, bc, chart: dict) -> dict:
    return {
        "person": name,
        "datetime_local": bc.dt_local.isoformat(),
        "location": {
            "name": bc.location_name,
            "lat": bc.latitude,
            "lon": bc.longitude,
            "tz_name": bc.tz_name,
        },
        "ayanamsa": chart.get("ayanamsa_mode"),
        "time_resolution": {
            "utc_offset_at_birth_hours": bc.utc_offset_hours,
            "jd_utc": bc.jd_utc,
            "jd_local": bc.jd_local,
            "jd_mode": "LOCAL_WITH_DST",
        },
        "core_chart": chart,
    }


def print_summary(bc, chart: dict) -> None:
    print(f"Local datetime: {bc.dt_local.isoformat()}")
    print(f"UTC offset at birth: {bc.utc_offset_hours} h")
    print(f"Julian Day (UTC): {bc.jd_utc}")
    print(f"Julian Day (local): {bc.jd_local}")
    print(f"Lagna longitude: {chart['lagna_longitude_deg']:.6f}°")
    print("Planets (deg):")
    for name, value in chart["planets"].items():
        print(f"  - {name:<7} {value:.6f}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate v0min core chart YAML snapshots.")
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
        "--ayanamsa",
        default="LAHIRI",
        help="Ayanamsa mode passed to compute_core_chart (default: LAHIRI).",
    )
    parser.add_argument(
        "--out",
        help="Destination YAML path (defaults to data/charts/<name>_core.yaml).",
    )
    parser.add_argument(
        "--print-only",
        action="store_true",
        help="Print core chart summary without writing a YAML file.",
    )
    parser.add_argument(
        "--no-print",
        action="store_true",
        help="Write YAML only; suppress stdout summary.",
    )

    args = parser.parse_args()
    if args.print_only and args.no_print:
        parser.error("--print-only and --no-print cannot be used together.")

    dt_local = parse_local_datetime(args.date, args.time)
    validate_coordinates(args.lat, args.lon)

    location_name = args.location_name or args.name
    ayanamsa_mode = args.ayanamsa.upper()

    bc = make_birth_context(
        dt_local,
        args.lat,
        args.lon,
        tz_name=args.tz,
        location_name=location_name,
    )
    chart = compute_core_chart(bc, ayanamsa_mode=ayanamsa_mode)
    payload = build_payload(args.name, bc, chart)

    if not args.print_only:
        out_path = Path(
            args.out
            or Path("data/charts") / f"{slugify(args.name)}_core.yaml"
        )
        save_core_chart(out_path, payload)
        if not args.no_print:
            print(f"Saved snapshot to {out_path}")

    if not args.no_print:
        print_summary(bc, chart)


if __name__ == "__main__":
    main()
