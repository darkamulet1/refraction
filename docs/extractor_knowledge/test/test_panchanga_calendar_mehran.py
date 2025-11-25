from __future__ import annotations

from datetime import date, datetime, timedelta

import pytz

from jhora import utils
from jhora.panchanga import drik

from v0min.core_time import make_birth_context
from v0min.panchanga_calendar_extract import build_panchanga_calendar


def _build_birth_context():
    return make_birth_context(
        datetime(1997, 6, 7, 20, 28, 36),
        35.6892,
        51.3890,
        tz_name="Asia/Tehran",
        location_name="Tehran",
    )


def _place_for_date(bc, current_date: date):
    tz = pytz.timezone(bc.tz_name)
    dt = tz.localize(datetime(current_date.year, current_date.month, current_date.day, 5, 30, 0))
    offset_hours = dt.utcoffset().total_seconds() / 3600.0
    return drik.Place(bc.location_name or "Birth Place", bc.latitude, bc.longitude, offset_hours)


def test_calendar_matches_panchanga_components() -> None:
    bc = _build_birth_context()
    start = date(1997, 6, 6)
    end = start + timedelta(days=2)

    calendar = build_panchanga_calendar(bc, start, end)
    assert calendar["engine"] == "PYJHORA_PANCHANGA_CALENDAR"
    assert len(calendar["days"]) == 3

    day_key = "1997-06-07"
    day_entry = calendar["days"][day_key]
    jd_local = day_entry["reference_jd_local"]
    place = _place_for_date(bc, datetime.strptime(day_key, "%Y-%m-%d").date())

    assert day_entry["weekday"]["id"] == drik.vaara(jd_local)
    tithi_data = drik.tithi(jd_local, place)
    assert day_entry["tithi"]["local_name"] == utils.TITHI_LIST[int(tithi_data[0]) - 1]
    nak_data = drik.nakshatra(jd_local, place)
    assert day_entry["nakshatra"]["local_name"] == utils.NAKSHATRA_LIST[int(nak_data[0]) - 1]

    sunrise = day_entry["sunrise"]
    assert "local_time" in sunrise and sunrise["local_time"]
    sunset = day_entry["sunset"]
    assert "local_time" in sunset and sunset["local_time"]
