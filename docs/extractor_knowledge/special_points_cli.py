#!/usr/bin/env python
"""
CLI utility to export the special_points.v1 block from a *_full_pyjhora.json snapshot.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from v0min.special_points_extract import compute_special_points_block


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate the PyJHora special_points.v1 payload (Arudhas/Sphutas/Graha Drishti/Pinda) "
            "from a *_full_pyjhora.json file."
        )
    )
    parser.add_argument("--birth-json", required=True, help="Path to *_full_pyjhora.json payload.")
    parser.add_argument(
        "--include-arudhas",
        dest="include_arudhas",
        action="store_const",
        const=True,
        help="Include Arudha details (default: True).",
    )
    parser.add_argument(
        "--exclude-arudhas",
        dest="include_arudhas",
        action="store_const",
        const=False,
        help="Exclude Arudha details.",
    )
    parser.add_argument(
        "--include-sphutas",
        dest="include_sphutas",
        action="store_const",
        const=True,
        help="Include sphuta points (default: True).",
    )
    parser.add_argument(
        "--exclude-sphutas",
        dest="include_sphutas",
        action="store_const",
        const=False,
        help="Exclude sphuta points.",
    )
    parser.add_argument(
        "--include-special-charts",
        dest="include_special_charts",
        action="store_const",
        const=True,
        help="Include special lagna/chart outputs (default: False).",
    )
    parser.add_argument(
        "--exclude-special-charts",
        dest="include_special_charts",
        action="store_const",
        const=False,
        help="Exclude special lagna/chart outputs.",
    )
    parser.add_argument(
        "--include-graha-drishti",
        dest="include_graha_drishti",
        action="store_const",
        const=True,
        help="Include graha drishti heatmaps (default: True).",
    )
    parser.add_argument(
        "--exclude-graha-drishti",
        dest="include_graha_drishti",
        action="store_const",
        const=False,
        help="Exclude graha drishti heatmaps.",
    )
    parser.add_argument(
        "--drishti-systems",
        help="Comma-separated list of graha drishti systems to include (parashari, jaimini).",
    )
    parser.add_argument(
        "--include-pinda",
        dest="include_pinda",
        action="store_const",
        const=True,
        help="Include pinda chakra values (default: True).",
    )
    parser.add_argument(
        "--exclude-pinda",
        dest="include_pinda",
        action="store_const",
        const=False,
        help="Exclude pinda chakra values.",
    )
    parser.add_argument(
        "--include-upagrahas",
        dest="include_upagrahas",
        action="store_const",
        const=True,
        help="Include upagraha positions (default: True).",
    )
    parser.add_argument(
        "--exclude-upagrahas",
        dest="include_upagrahas",
        action="store_const",
        const=False,
        help="Exclude upagraha positions.",
    )
    parser.add_argument(
        "--include-sahamas",
        dest="include_sahamas",
        action="store_const",
        const=True,
        help="Include sahama calculations (default: True).",
    )
    parser.add_argument(
        "--exclude-sahamas",
        dest="include_sahamas",
        action="store_const",
        const=False,
        help="Exclude sahama calculations.",
    )
    parser.add_argument(
        "--include-star-metrics",
        dest="include_star_metrics",
        action="store_const",
        const=True,
        help="Include star metric flags such as Mrityu Bhaga and Pushkara (default: True).",
    )
    parser.add_argument(
        "--exclude-star-metrics",
        dest="include_star_metrics",
        action="store_const",
        const=False,
        help="Exclude star metric calculations.",
    )
    parser.add_argument(
        "--out",
        help="Destination path for the special points JSON. If omitted, the payload is printed to stdout.",
    )
    parser.add_argument(
        "--no-print",
        action="store_true",
        help="Suppress stdout output when --out is used.",
    )
    parser.set_defaults(
        include_arudhas=None,
        include_sphutas=None,
        include_special_charts=None,
        include_graha_drishti=None,
        include_pinda=None,
        drishti_systems=None,
        include_upagrahas=None,
        include_sahamas=None,
        include_star_metrics=None,
    )
    return parser.parse_args()


def _build_config(args: argparse.Namespace) -> Dict[str, Any]:
    cfg: Dict[str, Any] = {"enabled": True}
    cfg["include_arudhas"] = True if args.include_arudhas is None else args.include_arudhas
    cfg["include_sphutas"] = True if args.include_sphutas is None else args.include_sphutas
    cfg["include_special_charts"] = False if args.include_special_charts is None else args.include_special_charts
    cfg["include_graha_drishti"] = True if args.include_graha_drishti is None else args.include_graha_drishti
    cfg["include_pinda"] = True if args.include_pinda is None else args.include_pinda
    cfg["include_upagrahas"] = True if args.include_upagrahas is None else args.include_upagrahas
    cfg["include_sahamas"] = True if args.include_sahamas is None else args.include_sahamas
    cfg["include_star_metrics"] = True if args.include_star_metrics is None else args.include_star_metrics
    if args.drishti_systems:
        systems = [item.strip().lower() for item in args.drishti_systems.split(",") if item.strip()]
        if systems:
            cfg["drishti_systems"] = systems
    return cfg


def load_payload(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(data: Dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    payload = load_payload(Path(args.birth_json))
    cfg = _build_config(args)
    block = compute_special_points_block(payload, config=cfg)
    if args.out:
        write_json(block, Path(args.out))
        if not args.no_print:
            print(f"Wrote special points payload to {Path(args.out).resolve()}")
    else:
        print(json.dumps(block, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
