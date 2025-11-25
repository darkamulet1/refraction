"""Manual parity analysis between PL9 and legacy PyJHora engine."""

from __future__ import annotations

import csv
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

CSV_PATH = Path("references/parity/Parity_comparison__PL9_vs_PyJHora_.csv")
TOP_N = 8


def _load_rows() -> List[Dict[str, str]]:
    if not CSV_PATH.exists():
        raise SystemExit(
            f"CSV file not found at {CSV_PATH}. "
            "Place Parity_comparison__PL9_vs_PyJHora_.csv under references/parity/."
        )
    with CSV_PATH.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [row for row in reader]
    if not rows:
        raise SystemExit("CSV contained no rows.")
    return rows


def _parse_delta(row: Dict[str, str]) -> float:
    try:
        return float(row.get("delta_arcsec", "0").strip() or 0.0)
    except (TypeError, ValueError):
        return 0.0


def _basic_stats(values: List[float]) -> Dict[str, float]:
    sorted_vals = sorted(values)
    return {
        "count": len(values),
        "min": sorted_vals[0],
        "max": sorted_vals[-1],
        "median": statistics.median(sorted_vals),
        "p90": sorted_vals[int(0.9 * (len(sorted_vals) - 1))],
        "p95": sorted_vals[int(0.95 * (len(sorted_vals) - 1))],
    }


def _group_by_chart(
    rows: List[Dict[str, str]]
) -> List[Tuple[str, int, float, float]]:
    grouped: Dict[str, List[float]] = defaultdict(list)
    for row in rows:
        grouped[row.get("chart_id", "").strip()].append(abs(_parse_delta(row)))
    entries: List[Tuple[str, int, float, float]] = []
    for chart_id, values in grouped.items():
        entries.append(
            (
                chart_id or "<unknown>",
                len(values),
                max(values),
                statistics.mean(values),
            )
        )
    return sorted(entries, key=lambda item: item[2])


def _sorted_rows(rows: List[Dict[str, str]], reverse: bool) -> List[Dict[str, str]]:
    return sorted(rows, key=lambda row: abs(_parse_delta(row)), reverse=reverse)


def main() -> None:
    rows = _load_rows()
    deltas = [abs(_parse_delta(row)) for row in rows]
    stats = _basic_stats(deltas)

    print("=== PL9 vs PyJHora Parity Report ===")
    print(f"CSV: {CSV_PATH}")
    print(f"Total rows: {stats['count']}")
    print(
        "delta_arcsec stats -> "
        f"min:{stats['min']:.3f}  max:{stats['max']:.3f}  "
        f"median:{stats['median']:.3f}  p90:{stats['p90']:.3f}  p95:{stats['p95']:.3f}"
    )
    print()

    print("Per-chart summary (sorted by max delta_arcsec):")
    print(f"{'chart':<8}{'rows':>6}{'max arcsec':>14}{'mean arcsec':>16}")
    for chart_id, count, max_delta, mean_delta in _group_by_chart(rows):
        print(f"{chart_id:<8}{count:>6}{max_delta:>14.3f}{mean_delta:>16.3f}")
    print()

    best = _sorted_rows(rows, reverse=False)[:TOP_N]
    worst = _sorted_rows(rows, reverse=True)[:TOP_N]

    def _print_table(title: str, subset: List[Dict[str, str]]) -> None:
        print(title)
        print(f"{'chart':<8}{'planet':<10}{'PL9_deg':>12}{'PyJHora_deg':>14}{'delta_arcsec':>16}")
        for row in subset:
            print(
                f"{row.get('chart_id',''):8}"
                f"{row.get('planet',''):10}"
                f"{row.get('PL9_deg',''):>12}"
                f"{row.get('PyJHora_deg',''):>14}"
                f"{float(row.get('delta_arcsec',0)):>16.3f}"
            )
        print()

    _print_table(f"Top {TOP_N} best matches", best)
    _print_table(f"Top {TOP_N} worst mismatches", worst)


if __name__ == "__main__":
    main()
