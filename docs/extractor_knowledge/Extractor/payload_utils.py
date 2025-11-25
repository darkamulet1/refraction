from __future__ import annotations

from datetime import datetime
from typing import Dict, Tuple

from jhora.panchanga import drik

from v0min.core_time import BirthContext, make_birth_context


def build_birth_context_from_payload(payload: Dict[str, object]) -> Tuple[BirthContext, drik.Place]:
    """
    Construct a BirthContext + drik.Place pair from a canonical *_full_pyjhora.json payload.
    """

    birth_data = payload.get("birth_data", {})
    location = birth_data.get("location", {})
    tz_name = birth_data.get("timezone_name", "UTC")

    dt_local = datetime.fromisoformat(birth_data["datetime_local"])
    dt_naive = dt_local.replace(tzinfo=None)

    bc = make_birth_context(
        dt_naive,
        float(location.get("lat", 0.0)),
        float(location.get("lon", 0.0)),
        tz_name=tz_name,
        location_name=location.get("name"),
    )
    place_name = location.get("name") or bc.location_name or "Birth Place"
    place = drik.Place(place_name, bc.latitude, bc.longitude, bc.utc_offset_hours)
    return bc, place


def get_chart_positions(payload: Dict[str, object], chart_id: str = "D1"):
    """
    Retrieve raw planet positions for the requested chart from the payload.
    """

    vargas = payload.get("vargas") or {}
    chart = vargas.get(chart_id)
    if chart:
        return chart.get("raw_positions")
    core_chart = payload.get("core_chart")
    if chart_id == "D1" and core_chart:
        return core_chart.get("raw_positions")
    return None


__all__ = ["build_birth_context_from_payload", "get_chart_positions"]
