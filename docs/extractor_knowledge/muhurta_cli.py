#!/usr/bin/env python
"""
CLI utility to export muhurta.v1 windows from a *_full_pyjhora.json snapshot.
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

from v0min.muhurta_extract import MuhurtaConfig, compute_muhurta_windows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compute Muhurta windows for a given activity and date range.")
    parser.add_argument("--birth-json", required=True, help="Path to *_full_pyjhora.json payload.")
    parser.add_argument("--activity", default="CLASS_START", help="Activity type (CLASS_START, PROJECT_LAUNCH, TRAVEL).")
    parser.add_argument("--start-date", required=True, help="Start date YYYY-MM-DD (inclusive).")
    parser.add_argument("--end-date", required=True, help="End date YYYY-MM-DD (inclusive).")
    parser.add_argument("--step-minutes", type=int, default=30, help="Window size in minutes (default: 30).")
    parser.add_argument("--max-windows", type=int, help="Maximum number of windows to return.")
    parser.add_argument(
        "--weights-json",
        help="Optional JSON object of rule weights (e.g., '{\"RAHUKALAM\": -90.0}').",
    )
    parser.add_argument("--out", help="Destination file for JSON output (stdout if omitted).")
    parser.add_argument(
        "--print-top",
        type=int,
        help="Print the top N windows to stdout in addition to writing JSON.",
    )
    parser.add_argument(
        "--no-print",
        action="store_true",
        help="Suppress success messages when writing to --out.",
    )
    return parser.parse_args()


def load_payload(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(data: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    payload = load_payload(Path(args.birth_json))
    weights = None
    if args.weights_json:
        weights = json.loads(args.weights_json)
    config = MuhurtaConfig(
        activity_type=args.activity,
        start_date=args.start_date,
        end_date=args.end_date,
        step_minutes=args.step_minutes,
        max_windows=args.max_windows,
        weights=weights,
    )
    result = compute_muhurta_windows(payload, config)
    if args.out:
        write_json(result, Path(args.out))
        if not args.no_print:
            print(f"Wrote muhurta payload to {Path(args.out).resolve()}")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.print_top:
        top_n = min(args.print_top, len(result.get("windows", [])))
        print(f"Top {top_n} windows:")
        for window in result.get("windows", [])[:top_n]:
            print(f"  {window['start_iso']} – {window['end_iso']} :: {window['tier']} (score={window['score']})")


if __name__ == "__main__":
    main()
