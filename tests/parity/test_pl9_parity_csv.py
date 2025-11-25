import csv
from pathlib import Path

import pytest

CSV_PATH = Path("references/parity/Parity_comparison__PL9_vs_PyJHora_.csv")
SMALL_ERROR_ARCSEC = 120.0  # 2 arcminutes
MIN_SMALL_ERROR_ROWS = 5


def _load_rows():
    if not CSV_PATH.exists():
        pytest.skip(f"Parity CSV not found at {CSV_PATH}")
    with CSV_PATH.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [row for row in reader]
    if not rows:
        pytest.skip("Parity CSV is empty")
    return rows


def _parse_delta(row):
    try:
        return abs(float(row.get("delta_arcsec", "0").strip() or 0.0))
    except (TypeError, ValueError):
        return 0.0


def test_pl9_parity_has_small_error_rows():
    rows = _load_rows()
    deltas = [_parse_delta(row) for row in rows]
    small = [delta for delta in deltas if delta <= SMALL_ERROR_ARCSEC]
    assert len(small) >= MIN_SMALL_ERROR_ROWS, (
        f"Expected at least {MIN_SMALL_ERROR_ROWS} small-error rows <= {SMALL_ERROR_ARCSEC} arcsec"
    )
    assert max(deltas) > 100000, "Expected some large outliers in parity CSV for contrast"


# TODO: future parity test comparing new refraction_engine outputs vs PL9.
# def test_refraction_engine_matches_pl9():
#     """
#     Outline:
#       1. Iterate all unique chart_id values in the CSV.
#       2. For each chart, load a corresponding references/in/<chart>_birth.json.
#       3. Run run_core_chart or run_refraction_core from refraction_engine.pipeline.
#       4. Extract the target planet's absolute longitude.
#       5. Compare against PL9_deg with a tight tolerance (e.g. < 10 arcseconds).
#     """
#     raise NotImplementedError
