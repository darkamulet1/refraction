#!/usr/bin/env python
"""
CLI utility to export events.v1 payloads (sign entries, retrograde changes, eclipses, ...).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from v0min import api


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export PyJHora event timelines (sign entries, eclipses, retrogrades).")
    parser.add_argument("--birth-json", required=True, help="Path to *_full_pyjhora.json payload.")
    parser.add_argument("--start", required=True, help="Start datetime (ISO 8601, local).")
    parser.add_argument("--end", required=True, help="End datetime (ISO 8601, local).")
    parser.add_argument("--event-types", help="Comma separated event types (SIGN_ENTRY,CONJUNCTION,ECLIPSE,RETROGRADE,SANKRANTI).")
    parser.add_argument("--planets", help="Comma separated planet names (Sun,Moon,Mars,...).")
    parser.add_argument("--systems", help="Comma separated systems (D1,D9,...).")
    parser.add_argument("--max-events", type=int, default=500)
    parser.add_argument("--include-house-entries", action="store_true", help="Include HOUSE_ENTRY events.")
    parser.add_argument("--include-vakra-segments", action="store_true", help="Include RETROGRADE_SEGMENT events.")
    parser.add_argument("--vakra-planets", help="Comma separated planet names for vakra segment tracking.")
    parser.add_argument("--out", help="Destination JSON file; prints to stdout if omitted.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = json.loads(Path(args.birth_json).read_text(encoding="utf-8"))
    event_types = args.event_types.split(",") if args.event_types else None
    planets = args.planets.split(",") if args.planets else None
    systems = args.systems.split(",") if args.systems else None
    vakra_planets = args.vakra_planets.split(",") if args.vakra_planets else None
    snapshot = api.compute_events(
        payload,
        start=args.start,
        end=args.end,
        event_types=event_types,
        planets=planets,
        systems=systems,
        max_events=args.max_events,
        include_house_entries=args.include_house_entries,
        include_vakra_segments=args.include_vakra_segments,
        vakra_planets=vakra_planets,
    )
    data = json.dumps(snapshot, indent=2, ensure_ascii=False)
    if args.out:
        Path(args.out).write_text(data + "\n", encoding="utf-8")
        print(f"Wrote events snapshot: {Path(args.out).resolve()}")
    else:
        print(data)


if __name__ == "__main__":
    main()
