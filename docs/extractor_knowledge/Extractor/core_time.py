from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import pytz
import swisseph as swe

from jhora import utils


@dataclass(frozen=True)
class BirthContext:
    """Normalized birth metadata shared across v0min modules."""

    dt_local: datetime
    dt_utc: datetime
    latitude: float
    longitude: float
    tz_name: str
    utc_offset_hours: float
    jd_utc: float
    jd_local: float
    location_name: Optional[str] = None


def _ensure_timezone(dt: datetime, tz_name: str) -> datetime:
    tz = pytz.timezone(tz_name)
    if dt.tzinfo is None:
        return tz.localize(dt)
    return dt.astimezone(tz)


def make_birth_context(
    dt_local_naive: datetime,
    lat: float,
    lon: float,
    tz_name: str = "Asia/Tehran",
    location_name: Optional[str] = None,
) -> BirthContext:
    """
    Construct a BirthContext from explicit datetime/place inputs.

    The datetime is localized with pytz (matching legacy utils usage) and the
    Julian day is delegated to jhora.utils.julian_day_number to guarantee parity
    with the existing engine math.
    """

    dt_local = _ensure_timezone(dt_local_naive, tz_name)
    dt_utc = dt_local.astimezone(pytz.UTC)
    offset = dt_local.utcoffset()
    if offset is None:
        raise ValueError(f"Unable to resolve UTC offset for timezone {tz_name}")
    utc_offset_hours = offset.total_seconds() / 3600.0

    dob_tuple_utc = (dt_utc.year, dt_utc.month, dt_utc.day)
    seconds_utc = dt_utc.second + dt_utc.microsecond / 1_000_000
    tob_tuple_utc = (dt_utc.hour, dt_utc.minute, seconds_utc)
    jd_utc = utils.julian_day_number(dob_tuple_utc, tob_tuple_utc)

    local_hour = (
        dt_local.hour
        + dt_local.minute / 60.0
        + dt_local.second / 3600.0
        + dt_local.microsecond / 3_600_000_000
    )
    jd_local = swe.julday(dt_local.year, dt_local.month, dt_local.day, local_hour)

    return BirthContext(
        dt_local=dt_local,
        dt_utc=dt_utc,
        latitude=float(lat),
        longitude=float(lon),
        tz_name=tz_name,
        utc_offset_hours=utc_offset_hours,
        jd_utc=jd_utc,
        jd_local=jd_local,
        location_name=location_name,
    )


__all__ = ["BirthContext", "make_birth_context"]
