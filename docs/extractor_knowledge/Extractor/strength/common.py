from __future__ import annotations

from datetime import datetime
from typing import Any, Tuple

from jhora.panchanga import drik

from v0min.core_time import BirthContext


def resolve_place(context: Dict[str, Any]) -> drik.Place:
    place = context.get("place")
    if place is not None:
        return place
    bc: BirthContext = context["birth_context"]
    label = context.get("location_name") or bc.location_name or "Birth Place"
    return drik.Place(label, bc.latitude, bc.longitude, bc.utc_offset_hours)


def resolve_context_components(context: Dict[str, Any]) -> Tuple[BirthContext, drik.Place, str]:
    bc: BirthContext = context["birth_context"]
    place = resolve_place(context)
    ayanamsa_mode = (context.get("ayanamsa_mode") or "LAHIRI").upper()
    return bc, place, ayanamsa_mode


def resolve_dob_tob(context: Dict[str, Any]) -> Tuple[Tuple[int, int, int], Tuple[int, int, float]]:
    """
    Convert the stored BirthContext datetime into tuples expected by the
    upstream PyJHora helpers (year, month, day) / (hour, minute, seconds).
    """

    bc: BirthContext = context["birth_context"]
    dt: datetime = bc.dt_local
    dob_tuple = (dt.year, dt.month, dt.day)
    seconds = dt.second + dt.microsecond / 1_000_000
    tob_tuple = (dt.hour, dt.minute, seconds)
    return dob_tuple, tob_tuple


def resolve_drik_date(context: Dict[str, Any]) -> Tuple[drik.Date, Tuple[int, int, float]]:
    """
    PyJHora's drik helpers expect a Date struct plus a time tuple. This mirrors
    how the UI layer calls into drik.panchanga.
    """

    bc: BirthContext = context["birth_context"]
    dt: datetime = bc.dt_local
    dob = drik.Date(dt.year, dt.month, dt.day)
    seconds = dt.second + dt.microsecond / 1_000_000
    tob = (dt.hour, dt.minute, seconds)
    return dob, tob
