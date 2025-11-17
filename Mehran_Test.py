#!/usr/bin/env python
"""
Generate a YAML snapshot for Mehran's chart directly from PyJHora internals.

The script avoids the GUI and exercises the core APIs: it computes the requested
divisional chart, annotates each body with sign/nakshatra data, and writes a
machine-friendly YAML file for regression comparison against PL/JHora.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import date, datetime, time
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple, Union

import swisseph as swe
from jhora import const, utils
from jhora.horoscope.chart import charts
from jhora.panchanga import drik

# Ensure English resources are loaded so utils exposes PLANET/RASI labels.
utils.set_language(const._DEFAULT_LANGUAGE)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

STAR_SPAN_DEG = 360.0 / 27.0  # 13 deg 20'
_swe_version_attr = getattr(swe, "version", None)
if callable(_swe_version_attr):
    SWISSEPH_VERSION = _swe_version_attr()
else:
    SWISSEPH_VERSION = getattr(swe, "__version__", _swe_version_attr if isinstance(_swe_version_attr, str) else "unknown")


@dataclass(frozen=True)
class BirthContext:
    """Simple container for the user supplied birth data."""

    name: str
    birth_date: date
    birth_time: time
    latitude: float
    longitude: float
    timezone_offset_hours: float
    place_label: str
    ayanamsha_mode: str
    chart_factor: int
    calc_type: str
    node_mode: str
    chart_method: int
    precision: int

    @property
    def datetime_iso(self) -> str:
        return datetime.combine(self.birth_date, self.birth_time).isoformat()

    @property
    def julian_day(self) -> float:
        return utils.julian_day_number(
            (self.birth_date.year, self.birth_date.month, self.birth_date.day),
            (self.birth_time.hour, self.birth_time.minute, self.birth_time.second),
        )

    @property
    def place(self) -> drik.Place:
        return drik.Place(
            self.place_label,
            round(self.latitude, 6),
            round(self.longitude, 6),
            round(self.timezone_offset_hours, 4),
        )


def parse_timezone_offset(raw: str) -> float:
    """Parse timezone offsets such as '+05:30' or -4.5 into float hours."""
    if isinstance(raw, (int, float)):
        return float(raw)
    token = raw.strip()
    if not token:
        raise ValueError("Timezone offset cannot be empty.")
    sign = -1.0 if token.startswith("-") else 1.0
    payload = token[1:] if token[0] in "+-" else token
    if ":" in payload:
        hours, minutes = payload.split(":", 1)
        return sign * (float(hours) + float(minutes) / 60.0)
    return float(token)


def parse_time(value: str) -> time:
    """Parse HH:MM[:SS] strings into datetime.time."""
    parts = [int(part) for part in value.split(":")]
    if len(parts) == 2:
        parts.append(0)
    return time(parts[0], parts[1], parts[2])


def to_body_label(body_id: Union[str, int]) -> str:
    if body_id == const._ascendant_symbol or (isinstance(body_id, str) and body_id.upper().startswith("L")):
        return "Ascendant"
    if isinstance(body_id, int):
        try:
            return utils.PLANET_NAMES[body_id]
        except IndexError as exc:
            raise ValueError(f"Unknown planetary index {body_id}") from exc
    return str(body_id)


def nakshatra_details(longitude: float) -> Dict[str, Any]:
    """Return nakshatra metadata for a nirayana longitude."""
    nak_index, pada, remainder = drik.nakshatra_pada(longitude)
    progress = remainder / STAR_SPAN_DEG if STAR_SPAN_DEG else 0.0
    return {
        "nakshatra_index": nak_index,
        "nakshatra_name": utils.NAKSHATRA_LIST[nak_index - 1],
        "pada": pada,
        "within_star_deg": round(remainder, 6),
        "within_star_dms": utils.to_dms(remainder, is_lat_long="plong"),
        "progress_percent": round(progress * 100.0, 4),
    }


def build_positions(ctx: BirthContext) -> Tuple[List[Dict[str, Any]], float]:
    """Compute divisional chart positions and ayanamsha."""
    jd = ctx.julian_day
    drik.set_ayanamsa_mode(ctx.ayanamsha_mode, None, jd)
    try:
        if hasattr(drik, "NODE_MODE"):
            drik.NODE_MODE = "true" if ctx.node_mode == "true" else "mean"
        if hasattr(drik, "TRUE_NODE"):
            drik.TRUE_NODE = ctx.node_mode == "true"
    except Exception:
        pass
    try:
        if hasattr(swe, "set_nodetype") and hasattr(swe, "TRUE_NODE") and hasattr(swe, "MEAN_NODE"):
            swe.set_nodetype(swe.TRUE_NODE if ctx.node_mode == "true" else swe.MEAN_NODE)
    except Exception:
        pass
    planet_positions = charts.divisional_chart(
        jd,
        ctx.place,
        ayanamsa_mode=ctx.ayanamsha_mode,
        divisional_chart_factor=ctx.chart_factor,
        chart_method=ctx.chart_method,
        years=1,
        months=1,
        sixty_hours=1,
        calculation_type=ctx.calc_type,
        pravesha_type=0,
    )
    retrograde_planets = set(drik.planets_in_retrograde(jd, ctx.place))
    ayanamsha_value = drik.get_ayanamsa_value(jd)
    positions: List[Dict[str, Any]] = []
    for body_id, (sign_index, longitude_in_sign) in planet_positions:
        absolute_longitude = (sign_index * 30.0) + longitude_in_sign
        entry = {
            "body": to_body_label(body_id),
            "raw_id": body_id,
            "sign_index": sign_index,
            "sign_name": utils.RAASI_LIST[sign_index],
            "sign_short": utils.RAASI_SHORT_LIST[sign_index],
            "longitude_in_sign_deg": round(longitude_in_sign, ctx.precision),
            "longitude_in_sign_dms": utils.to_dms(longitude_in_sign, is_lat_long="plong"),
            "absolute_longitude_deg": round(absolute_longitude % 360.0, ctx.precision),
            "absolute_longitude_dms": utils.to_dms(absolute_longitude % 360.0, is_lat_long="plong"),
            "retrograde": isinstance(body_id, int) and body_id in retrograde_planets,
        }
        entry.update(nakshatra_details(absolute_longitude % 360.0))
        positions.append(entry)
    return positions, ayanamsha_value


def serialize_yaml(payload: Dict[str, Any]) -> str:
    """Serialize payload to YAML, optionally using PyYAML when present."""
    try:
        import yaml  # type: ignore

        return yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)
    except ModuleNotFoundError:
        pass

    def _scalar(value: Any) -> str:
        if isinstance(value, str):
            return json.dumps(value, ensure_ascii=False)
        if isinstance(value, bool):
            return "true" if value else "false"
        if value is None:
            return "null"
        if isinstance(value, (int, float)):
            return repr(value)
        return json.dumps(str(value), ensure_ascii=False)

    def _emit(value: Any, indent: int = 0) -> str:
        prefix = "  " * indent
        if isinstance(value, dict):
            lines: List[str] = []
            for key, val in value.items():
                if isinstance(val, (dict, list)):
                    lines.append(f"{prefix}{key}:")
                    lines.append(_emit(val, indent + 1))
                else:
                    lines.append(f"{prefix}{key}: {_scalar(val)}")
            return "\n".join(lines)
        if isinstance(value, list):
            lines: List[str] = []
            for item in value:
                if isinstance(item, (dict, list)):
                    lines.append(f"{prefix}-")
                    lines.append(_emit(item, indent + 1))
                else:
                    lines.append(f"{prefix}- {_scalar(item)}")
            return "\n".join(lines)
        return f"{prefix}{_scalar(value)}"

    return _emit(payload)


def divisional_label(factor: int) -> str:
    mapping = {
        1: "Rasi",
        2: "Hora",
        3: "Drekkana",
        4: "Chaturthamsa",
        7: "Saptamsa",
        8: "Ashtamsa",
        9: "Navamsa",
        10: "Dasamsa",
        12: "Dvadasamsa",
        16: "Shodasamsa",
        20: "Vimsamsa",
        24: "Siddhamsa",
        27: "Nakshatramsa",
        30: "Trimsamsa",
        40: "Khavedamsa",
        45: "Akshavedamsa",
        60: "Shashtiamsa",
    }
    suffix = mapping.get(factor)
    return f"D{factor} ({suffix})" if suffix else f"D{factor}"


def build_payload(ctx: BirthContext) -> Dict[str, Any]:
    positions, ayanamsha_value = build_positions(ctx)
    return {
        "metadata": {
            "name": ctx.name,
            "location": ctx.place_label,
            "coordinates": {"latitude": ctx.latitude, "longitude": ctx.longitude},
            "timezone_offset_hours": ctx.timezone_offset_hours,
            "local_datetime": ctx.datetime_iso,
            "julian_day": ctx.julian_day,
            "ayanamsha_mode": ctx.ayanamsha_mode,
            "ayanamsha_value_deg": round(ayanamsha_value, 8),
            "ayanamsha_value_dms": utils.to_dms(ayanamsha_value, is_lat_long="plong"),
            "divisional_chart_factor": ctx.chart_factor,
            "divisional_chart_label": divisional_label(ctx.chart_factor),
            "calculation_type": ctx.calc_type,
            "node_mode": ctx.node_mode,
            "chart_method": ctx.chart_method,
            "precision_digits": ctx.precision,
            "swisseph_version": SWISSEPH_VERSION,
            "generator": "PyJHora core API",
        },
        "positions": positions,
    }


def write_output(path: Path, payload: Dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(serialize_yaml(payload), encoding="utf-8")
    return path


def write_csv_sibling(yaml_path: Path, payload: Dict[str, Any]) -> Path:
    try:
        import csv
    except Exception:
        return yaml_path
    csv_path = yaml_path.with_suffix(".csv")
    rows = []
    for position in payload.get("positions", []):
        rows.append(
            {
                "body": position.get("body", ""),
                "sign": position.get("sign_short", ""),
                "lon_in_sign_deg": position.get("longitude_in_sign_deg", ""),
                "abs_deg": position.get("absolute_longitude_deg", ""),
                "nakshatra": position.get("nakshatra_name", ""),
                "pada": position.get("pada", ""),
            }
        )
    fieldnames = list(rows[0].keys()) if rows else ["body", "sign", "lon_in_sign_deg", "abs_deg", "nakshatra", "pada"]
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return csv_path


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate YAML output for a PyJHora chart.")
    parser.add_argument("--name", default="Mehran", help="Label used inside the YAML metadata.")
    parser.add_argument("--location", default="Tehran, IR", help="Location string for metadata.")
    parser.add_argument("--date", default="1997-06-07", help="Birth date (YYYY-MM-DD).")
    parser.add_argument("--time", default="20:28:36", help="Birth time (24h HH:MM[:SS]).")
    parser.add_argument("--lat", default="35.6892", help="Latitude in decimal degrees.")
    parser.add_argument("--lon", default="51.3890", help="Longitude in decimal degrees.")
    parser.add_argument("--tz", default="+04:30", help="Timezone offset, e.g. +05:30 or -04.")
    parser.add_argument("--ayanamsha", default="Lahiri", help="Ayanamsha label (Lahiri, Raman, etc.).")
    parser.add_argument(
        "--chart-factor",
        type=int,
        default=1,
        help="Divisional factor (1=D1, 9=D9, 60=D60 ...).",
    )
    parser.add_argument(
        "--chart-method",
        type=int,
        default=1,
        help="Divisional chart method (0/1/2 depending on varga implementation).",
    )
    parser.add_argument("--calc-type", default="drik", help="Calculation pipeline (drik / surya_sidhantha).")
    parser.add_argument(
        "--node-mode",
        choices=["true", "mean"],
        default="true",
        help="Select true or mean node for Rahu/Ketu.",
    )
    parser.add_argument(
        "--precision",
        type=int,
        default=6,
        help="Decimal digits for longitude rounding.",
    )
    parser.add_argument(
        "--output",
        default="\u0628\u0627\u0632\u062a\u0627\u0628/output/Mehran_D1.yaml",
        help="Destination YAML file path.",
    )
    return parser.parse_args(argv)


def build_context(args: argparse.Namespace) -> BirthContext:
    chart_factor = int(args.chart_factor)
    if chart_factor < 1:
        raise ValueError("Divisional chart factor must be positive.")
    return BirthContext(
        name=args.name,
        birth_date=date.fromisoformat(args.date),
        birth_time=parse_time(args.time),
        latitude=float(args.lat),
        longitude=float(args.lon),
        timezone_offset_hours=parse_timezone_offset(args.tz),
        place_label=args.location,
        ayanamsha_mode=args.ayanamsha.strip().upper(),
        chart_factor=chart_factor,
        calc_type=args.calc_type.lower(),
        node_mode=args.node_mode,
        chart_method=int(args.chart_method),
        precision=int(args.precision),
    )


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv)
    context = build_context(args)
    payload = build_payload(context)
    final_path = write_output(Path(args.output).expanduser(), payload)
    write_csv_sibling(final_path, payload)
    print(f"PyJHora YAML written to {final_path} (CSV sibling generated).")


if __name__ == "__main__":
    main()
