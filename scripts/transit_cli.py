#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from v0min.transit_extract import build_transit_payload


def _parse_datetime(date_str: str, time_str: str | None) -> str:
    if not time_str:
        time_str = "00:00:00"
    return f"{date_str}T{time_str}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a transit snapshot.")
    parser.add_argument("--birth-json", required=True, help="Path to full natal JSON payload.")
    parser.add_argument("--transit-date", required=True, help="Transit date (YYYY-MM-DD).")
    parser.add_argument("--transit-time", help="Transit time (HH:MM:SS).")
    parser.add_argument("--tz", help="Timezone override for the transit datetime.")
    parser.add_argument("--out", help="Output JSON path.")
    parser.add_argument("--print-only", action="store_true", help="Print summary only.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    natal_path = Path(args.birth_json)
    if not natal_path.exists():
        raise FileNotFoundError(natal_path)

    natal_payload = json.loads(natal_path.read_text(encoding="utf-8"))
    transit_dt = _parse_datetime(args.transit_date, args.transit_time)
    payload = build_transit_payload(
        natal_payload,
        transit_datetime_local=transit_dt,
        tz_name=args.tz,
    )

    out_path_template = args.out or f"{natal_path.stem}_transit_{args.transit_date.replace('-', '')}.json"
    out_path = Path(out_path_template)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Transit snapshot written to {out_path.resolve()}")

    print(
        f"Transit for {payload['reference_person']} @ {payload['transit_datetime_local']} "
        f"({payload['location']['name']})"
    )
    for graha in payload["grahas"]:
        print(
            f"{graha['name']}: transit house {graha['transit_house_from_natal_lagna']} "
            f"from natal Lagna"
        )



if __name__ == "__main__":
    main()
