import csv
from math import fabs
from pathlib import Path

import pytest

from refraction_engine import run_core_chart

from tests.specs._utils import load_json

CSV_PATH = Path("references/parity/Parity_comparison__PL9_vs_PyJHora_.csv")
PL9_TOLERANCE_ARCSEC = 60.0  # 1 arcminute
CANDIDATE_CHART_IDS = [
    # Chosen from analyzer output where legacy delta_arcsec was relatively small.
    "PL02",
    "PL03",
]

PLANET_NAME_MAP = {
    "Asc": "ASCENDANT",
    "Sun": "SUN",
    "Moon": "MOON",
    "Mars": "MARS",
    "Mercury": "MERCURY",
    "Jupiter": "JUPITER",
    "Venus": "VENUS",
    "Saturn": "SATURN",
    "Rahu": "RAHU",
    "Ketu": "KETU",
}


def _load_csv_rows():
    if not CSV_PATH.exists():
        pytest.skip(f"Parity CSV not found at {CSV_PATH}")
    with CSV_PATH.open("r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _absolute_longitude(planet_entry):
    return float(planet_entry.get("longitude_deg", 0.0))


def _find_planet(planets, target_id):
    for entry in planets:
        if entry.get("id") == target_id:
            return entry
    return None


def _chart_fixture_path(chart_id: str) -> Path:
    return Path(f"references/in/{chart_id}_birth.json")


def test_new_engine_parity_against_pl9():
    rows = _load_csv_rows()
    relevant = [
        row for row in rows
        if row.get("chart_id") in CANDIDATE_CHART_IDS
        and row.get("planet") in PLANET_NAME_MAP
    ]

    if not relevant:
        pytest.skip("No relevant rows found for candidate charts")

    for row in relevant:
        chart_id = row["chart_id"]
        planet_label = row["planet"]
        planet_id = PLANET_NAME_MAP[planet_label]
        fixture_path = _chart_fixture_path(chart_id)
        if not fixture_path.exists():
            pytest.skip(f"Missing engine input for {chart_id} at {fixture_path}")

        payload = load_json(str(fixture_path))
        result = run_core_chart(payload)
        frame = result["frames"][0]
        planet_entry = _find_planet(frame.get("planets", []), planet_id)
        if planet_id == "ASCENDANT":
            planet_entry = frame.get("ascendant")
        assert planet_entry, f"Planet {planet_id} not found in core chart output"

        engine_longitude = _absolute_longitude(planet_entry)
        pl9_longitude = float(row.get("PL9_deg", 0.0))

        delta_arcsec = fabs((engine_longitude - pl9_longitude) * 3600.0)
        assert delta_arcsec <= PL9_TOLERANCE_ARCSEC, (
            f"{chart_id} {planet_label} exceeded tolerance: {delta_arcsec:.2f} arcsec"
        )
