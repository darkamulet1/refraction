from __future__ import annotations

from datetime import datetime
from pathlib import Path

from v0min.core_space import compute_core_chart
from v0min.core_time import make_birth_context
from v0min.io_core import load_core_chart


SNAPSHOT_PATH = Path("data/charts/mehran_core.yaml")
TOLERANCE_DEG = 0.1


def test_core_chart_matches_snapshot() -> None:
    snapshot = load_core_chart(SNAPSHOT_PATH)
    dt_with_tz = datetime.fromisoformat(snapshot["datetime_local"])
    dt_naive = dt_with_tz.replace(tzinfo=None)

    location = snapshot["location"]
    bc = make_birth_context(
        dt_naive,
        location["lat"],
        location["lon"],
        tz_name=location["tz_name"],
        location_name=location.get("name"),
    )

    chart = compute_core_chart(bc, ayanamsa_mode=snapshot.get("ayanamsa"))

    expected_chart = snapshot["core_chart"]
    lagna_expected = expected_chart["lagna_longitude_deg"]
    lagna_actual = chart["lagna_longitude_deg"]
    assert abs(lagna_actual - lagna_expected) <= TOLERANCE_DEG, (
        f"Lagna mismatch: got {lagna_actual}, expected {lagna_expected}"
    )

    for name, expected_value in expected_chart["planets"].items():
        actual_value = chart["planets"].get(name)
        assert actual_value is not None, f"{name} missing from computed chart"
        diff = abs(actual_value - expected_value)
        assert diff <= TOLERANCE_DEG, f"{name} mismatch: got {actual_value}, expected {expected_value}"
