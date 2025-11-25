#!/usr/bin/env python
"""
matching_cli.py

Generate PyJHora compatibility reports between two charts.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict

from v0min.matching_extract import (
    build_matching_report_from_files,
    matching_schema_template,
    save_matching_report,
)


def slugify(value: str) -> str:
    slug = "".join(ch.lower() if ch.isalnum() else "_" for ch in value.strip())
    slug = "_".join(filter(None, slug.split("_")))
    return slug or "chart"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compute PyJHora Ashtakoota + Dosha matching between two charts.")
    parser.add_argument("--chart1", help="Path to the first *_full_pyjhora.json chart.")
    parser.add_argument("--chart2", help="Path to the second *_full_pyjhora.json chart.")
    parser.add_argument(
        "--out",
        help="Destination JSON file. Defaults to <name1>_<name2>_MATCHING.json under references/out.",
    )
    parser.add_argument(
        "--method",
        default="North",
        choices=["North", "South", "north", "south"],
        help="Ashtakoota method (default: North).",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print a human-readable summary after generating the report.",
    )
    parser.add_argument(
        "--no-naalu",
        action="store_true",
        help="Skip the Naalu Porutham block in the JSON output.",
    )
    parser.add_argument(
        "--no-filters",
        action="store_true",
        help="Skip the database filter flags block in the JSON output.",
    )
    parser.add_argument(
        "--schema-only",
        action="store_true",
        help="Print the JSON schema template and exit.",
    )
    return parser.parse_args()


def _determine_output_path(report: Dict[str, object], explicit: str | None) -> Path:
    if explicit:
        return Path(explicit)
    slug1 = slugify(str(report["meta"]["chart_ref_1"]))
    slug2 = slugify(str(report["meta"]["chart_ref_2"]))
    return Path("references/out") / f"{slug1}_{slug2}_MATCHING.json"


def _print_summary(report: Dict[str, object]) -> None:
    total = report["total"]
    print(f"Total: {total['score']:.2f}/{total['max']} ({total['grade']})")
    print("Ashtakoota components:")
    for key, component in report["ashtakoota"]["components"].items():
        detail = component.get("detail") or ""
        print(f"  {key:12s} -> {component['score']:.2f}/{component['max']} {detail}")
    print("Dosha flags:")
    for key, value in report["dosha_flags"].items():
        print(f"  {key}: {value}")
    if "naalu_porutham" in report:
        print("Naalu Porutham:")
        for name, info in report["naalu_porutham"].items():
            detail = info.get("details") or ""
            print(f"  {name:12s} -> {info['is_compatible']} {detail}")
    if "filters" in report:
        filters = report["filters"]
        print(f"Filters: eligible={filters['is_db_eligible']} (min_score={filters['minimum_score']})")
        for key, value in filters["flags"].items():
            print(f"  {key}: {value}")
    if report["narrative_flags"]:
        print("Narrative:")
        for line in report["narrative_flags"]:
            print(f"  - {line}")


def main() -> None:
    args = parse_args()
    if args.schema_only:
        print(json.dumps(matching_schema_template(), indent=2, ensure_ascii=False))
        return
    if not args.chart1 or not args.chart2:
        raise SystemExit("--chart1 and --chart2 are required unless --schema-only is used.")

    report = build_matching_report_from_files(
        args.chart1,
        args.chart2,
        method=args.method,
        include_naalu_porutham=not args.no_naalu,
        include_filters=not args.no_filters,
    )
    out_path = _determine_output_path(report, args.out)
    save_matching_report(report, out_path)
    print(f"Matching snapshot written to {out_path.resolve()}")

    if args.verbose:
        _print_summary(report)


if __name__ == "__main__":
    main()
