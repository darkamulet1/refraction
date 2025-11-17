#!/usr/bin/env python
"""
Produce a standard PyJHora Rāśi (D1) chart for Mehran using the production
Horoscope flow. Run with:

    $env:PYTHONPATH = "src"
    python scripts/jhora_chart_mehran.py
"""

from __future__ import annotations

from jhora import utils
from jhora.horoscope.chart import charts
from jhora.horoscope.main import Horoscope
from jhora.panchanga import drik


BIRTH_DATE = drik.Date(1997, 6, 7)
BIRTH_TIME = "20:28:36"
LATITUDE = 35.6892
LONGITUDE = 51.3890
TIMEZONE_OFFSET_HOURS = 4.5  # Asia/Tehran at 1997-06-07
LOCATION_LABEL = "Tehran, IR"
AYANAMSA_MODE = "LAHIRI"


def angle_summary(sign_index: int, degrees_in_sign: float) -> tuple[str, str, float]:
    """Convert a sign index and intra-sign longitude to display-friendly values."""
    sign_name = utils.RAASI_LIST[int(sign_index)]
    deg_str = utils.to_dms(degrees_in_sign, is_lat_long="plong")
    absolute_degrees = (int(sign_index) * 30.0 + degrees_in_sign) % 360.0
    return sign_name, deg_str, absolute_degrees


def main() -> None:
    utils.set_language("en")
    horoscope = Horoscope(
        place_with_country_code=LOCATION_LABEL,
        latitude=LATITUDE,
        longitude=LONGITUDE,
        timezone_offset=TIMEZONE_OFFSET_HOURS,
        date_in=BIRTH_DATE,
        birth_time=BIRTH_TIME,
        ayanamsa_mode=AYANAMSA_MODE,
        calculation_type="drik",
    )

    planet_positions = charts.rasi_chart(
        horoscope.julian_day,
        horoscope.Place,
        ayanamsa_mode=horoscope.ayanamsa_mode,
    )

    asc_sign_idx, asc_long = planet_positions[0][1]
    asc_sign, asc_deg_str, asc_abs = angle_summary(asc_sign_idx, asc_long)

    print("PyJHora Rāśi Chart – Mehran")
    print("-" * 40)
    print(f"Ascendant : {asc_sign:>8}  {asc_deg_str:<12} (abs {asc_abs:9.6f}°)")

    for planet_id, (sign_idx, deg_in_sign) in planet_positions[1:]:
        planet_name = utils.PLANET_NAMES[int(planet_id)]
        sign_name, deg_str, abs_deg = angle_summary(sign_idx, deg_in_sign)
        print(f"{planet_name:9}: {sign_name:>8}  {deg_str:<12} (abs {abs_deg:9.6f}°)")


if __name__ == "__main__":
    main()
