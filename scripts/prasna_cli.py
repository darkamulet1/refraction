#!/usr/bin/env python
"""
CLI utility to compute Prasna/KP snapshots from a *_full_pyjhora.json payload.
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

from v0min.prasna_extract import PrasnaConfig, compute_prasna_snapshot


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Prasna (Horary/KP) snapshots.")
    parser.add_argument("--birth-json", required=True, help="Path to *_full_pyjhora.json payload.")
    parser.add_argument(
        "--scheme",
        default="KP_249",
        choices=["PRASNA_108", "KP_249", "NAADI_1800"],
        help="Prasna scheme to use.",
    )
    parser.add_argument(
        "--mode",
        "--seed-mode",
        dest="seed_mode",
        choices=["manual", "time_seed", "random"],
        help="Seeding mode: manual, time_seed, or random.",
    )
    parser.add_argument(
        "--number",
        type=int,
        help="Horary/KP number (required for manual mode).",
    )
    parser.add_argument(
        "--time-override",
        help="ISO8601 datetime used for time_seed mode (defaults to now).",
    )
    parser.add_argument(
        "--random-seed",
        type=int,
        help="Random seed for random mode (defaults to current time).",
    )
    parser.add_argument(
        "--kp-max-depth",
        type=int,
        help="Limit the number of KP chain levels in the summary.",
    )
    parser.add_argument(
        "--out",
        help="Destination JSON file. Prints to stdout if omitted.",
    )
    return parser.parse_args()


def load_payload(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(data: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    seed_mode = args.seed_mode or ("manual" if args.number is not None else "time_seed")
    config = PrasnaConfig(
        scheme=args.scheme,
        seed_mode=seed_mode,
        manual_number=args.number,
        time_override=args.time_override,
        random_seed=args.random_seed,
        kp_chain_max_depth=args.kp_max_depth,
    )
    payload = load_payload(Path(args.birth_json))
    snapshot = compute_prasna_snapshot(payload, config=config)
    if args.out:
        write_json(snapshot, Path(args.out))
        print(f"Wrote prasna snapshot to {Path(args.out).resolve()}")
    else:
        print(json.dumps(snapshot, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
