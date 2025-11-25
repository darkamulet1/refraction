from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence, Tuple

import pytz

from jhora import const, utils
from jhora.horoscope.chart import charts, house
from jhora.panchanga import drik

from v0min import payload_utils
from v0min.core_time import BirthContext, make_birth_context


CHAKRA_SCHEMA_VERSION = "chakra.v1"
DEFAULT_LAYERS = [
    "sarvatobhadra",
    "kaala",
    "kota",
    "shoola",
    "tripataki",
    "surya_kalanala",
    "chandra_kalanala",
    "saptha_shalaka",
    "pancha_shalaka",
]

PLANET_NAME_MAP = list(getattr(utils, "PLANET_NAMES", []))
if not PLANET_NAME_MAP:
    PLANET_NAME_MAP = [
        "Sun",
        "Moon",
        "Mars",
        "Mercury",
        "Jupiter",
        "Venus",
        "Saturn",
        "Rahu",
        "Ketu",
    ]
NAKSHATRA_SHORT_NAMES = list(getattr(utils, "NAKSHATRA_SHORT_LIST", []))
if not NAKSHATRA_SHORT_NAMES:
    NAKSHATRA_SHORT_NAMES = [
        "Ash",
        "Bha",
        "Kri",
        "Roh",
        "Mri",
        "Ard",
        "Pun",
        "Pus",
        "Ashl",
        "Mag",
        "PPh",
        "UPh",
        "Has",
        "Chi",
        "Swa",
        "Vis",
        "Anu",
        "Jye",
        "Mul",
        "PAsh",
        "UAsh",
        "Shr",
        "Dha",
        "Sha",
        "PBh",
        "UBh",
        "Rev",
        "Abh",
    ]
RAASI_SHORT_NAMES = list(getattr(utils, "RAASI_SHORT_LIST", []))
if not RAASI_SHORT_NAMES:
    RAASI_SHORT_NAMES = [
        "Ar",
        "Ta",
        "Ge",
        "Cn",
        "Le",
        "Vi",
        "Li",
        "Sc",
        "Sg",
        "Cp",
        "Aq",
        "Pi",
    ]

ABHIJIT_ORDER = getattr(const, "abhijit_order_of_stars", list(range(len(NAKSHATRA_SHORT_NAMES))))
ABHIJITH_INDEX = getattr(const, "_ABHIJITH_STAR_INDEX", 21)

TRIPATAKI_POSITIONS = [
    (1, 3),
    (1, 4),
    (2, 5),
    (3, 5),
    (4, 5),
    (5, 4),
    (5, 3),
    (5, 2),
    (4, 1),
    (3, 1),
    (2, 1),
    (1, 2),
]

PANCHA_TEMPLATE = {
    1: (1, 2),
    2: (1, 1.5),
    3: (1.5, 1),
    4: (2, 1),
    5: (3, 1),
    6: (4, 1),
    7: (5, 1),
    8: (6, 1),
    9: (6.5, 1),
    10: (7, 1.5),
    11: (7, 2),
    12: (7, 3),
    13: (7, 4),
    14: (7, 5),
    15: (7, 6),
    16: (7, 6.5),
    17: (6.5, 7),
    18: (6, 7),
    19: (5, 7),
    20: (4, 7),
    21: (3, 7),
    22: (2, 7),
    23: (1.5, 7),
    24: (1, 6.5),
    25: (1, 6),
    26: (1, 5),
    27: (1, 4),
    28: (1, 3),
}

SAPTHA_TEMPLATE = {
    1: (7, 1),
    2: (8, 1),
    3: (9, 2),
    4: (9, 3),
    5: (9, 4),
    6: (9, 5),
    7: (9, 6),
    8: (9, 7),
    9: (9, 8),
    10: (8, 9),
    11: (7, 9),
    12: (6, 9),
    13: (5, 9),
    14: (4, 9),
    15: (3, 9),
    16: (2, 9),
    17: (1, 8),
    18: (1, 7),
    19: (1, 6),
    20: (1, 5),
    21: (1, 4),
    22: (1, 3),
    23: (1, 2),
    24: (2, 1),
    25: (3, 1),
    26: (4, 1),
    27: (5, 1),
    28: (6, 1),
}

CHANDRA_TEMPLATE = {
    1: (5, 1),
    2: (4, 1),
    3: (4, 3),
    4: (4, 4),
    5: (4, 5),
    6: (3, 4),
    7: (2, 4),
    8: (2, 5),
    9: (2, 6),
    10: (3, 6),
    11: (4, 6),
    12: (5, 6),
    13: (4, 7),
    14: (4, 8),
    15: (5, 8),
    16: (6, 8),
    17: (6, 7),
    18: (6, 6),
    19: (6, 5),
    20: (7, 6),
    21: (8, 6),
    22: (8, 5),
    23: (8, 4),
    24: (7, 4),
    25: (6, 4),
    26: (5, 4),
    27: (6, 3),
    28: (6, 2),
}

SURYA_TEMPLATE = {
    1: (8, 15),
    2: (5, 15),
    3: (3, 15),
    4: (1, 14),
    5: (1, 10),
    6: (1, 8),
    7: (1, 6),
    8: (1, 4),
    9: (1, 1),
    10: (3, 1),
    11: (4, 1),
    12: (5, 1),
    13: (6, 1),
    14: (7, 1),
    15: (8, 1),
    16: (9, 1),
    17: (10, 1),
    18: (11, 1),
    19: (12, 1),
    20: (13, 1),
    21: (15, 1),
    22: (15, 4),
    23: (15, 6),
    24: (15, 8),
    25: (15, 10),
    26: (15, 14),
    27: (13, 15),
    28: (11, 15),
}


@dataclass
class ChakraConfig:
    datetime_override: Optional[str] = None
    place_override: Optional[Dict[str, float]] = None
    include_layers: Optional[List[str]] = None
    layer_params: Optional[Dict[str, Dict[str, Any]]] = None

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ChakraConfig":
        return ChakraConfig(
            datetime_override=data.get("datetime_override"),
            place_override=data.get("place_override"),
            include_layers=data.get("include_layers"),
            layer_params=data.get("layer_params"),
        )


def compute_chakra_snapshot(
    birth_payload: Dict[str, Any],
    config: Optional[ChakraConfig] = None,
) -> Dict[str, Any]:
    cfg = config or ChakraConfig()
    bc, place = _build_chakra_context(birth_payload, cfg)
    ayanamsa_mode = _resolve_ayanamsa_mode(birth_payload)
    planet_positions = payload_utils.get_chart_positions(birth_payload, "D1")
    if not planet_positions:
        planet_positions = charts.rasi_chart(bc.jd_local, place, ayanamsa_mode=ayanamsa_mode)
    moon_long = planet_positions[2][1]
    moon_star = drik.nakshatra_pada(moon_long[0] * 30.0 + moon_long[1])[0]
    sun_long = planet_positions[1][1]
    sun_star = drik.nakshatra_pada(sun_long[0] * 30.0 + sun_long[1])[0]

    layers_to_include = [layer.lower() for layer in (cfg.include_layers or DEFAULT_LAYERS)]
    layer_params = cfg.layer_params or {}
    layers: Dict[str, Dict[str, Any]] = {}
    for layer in layers_to_include:
        params = layer_params.get(layer, {})
        if layer == "sarvatobhadra":
            layers[layer] = _build_sarvatobhadra_layer(planet_positions)
        elif layer == "kaala":
            base_star = params.get("base_star") or sun_star
            layers[layer] = _build_kaala_layer(planet_positions, base_star)
        elif layer == "kota":
            birth_star_pada = drik.nakshatra_pada(planet_positions[2][1][0] * 30.0 + planet_positions[2][1][1])
            layers[layer] = _build_kota_layer(
                planet_positions,
                moon_star,
                birth_star_pada[1],
                place,
            )
        elif layer == "shoola":
            base_star = params.get("base_star") or moon_star
            layers[layer] = _build_shoola_layer(planet_positions, base_star)
        elif layer == "tripataki":
            layers[layer] = _build_tripataki_layer(planet_positions)
        elif layer == "surya_kalanala":
            base_star = params.get("base_star") or sun_star
            layers[layer] = _build_surya_kalanala_layer(planet_positions, base_star)
        elif layer == "chandra_kalanala":
            base_star = params.get("base_star") or moon_star
            layers[layer] = _build_chandra_kalanala_layer(planet_positions, base_star)
        elif layer == "saptha_shalaka":
            base_star = params.get("base_star") or 1
            layers[layer] = _build_saptha_shalaka_layer(planet_positions, base_star)
        elif layer == "pancha_shalaka":
            base_star = params.get("base_star") or 1
            layers[layer] = _build_pancha_shalaka_layer(planet_positions, base_star)
        else:
            layers[layer] = {
                "name": layer,
                "grid": [],
                "hits": [],
                "meta": {"notes": "Layer not implemented in chakra.v1"},
            }

    return {
        "schema_version": CHAKRA_SCHEMA_VERSION,
        "datetime_local": bc.dt_local.isoformat(),
        "jd_utc": bc.jd_utc,
        "place": {
            "name": place.Place,
            "latitude": place.latitude,
            "longitude": place.longitude,
            "tz_offset_hours": place.timezone,
        },
        "ayanamsa": ayanamsa_mode,
        "layers": layers,
    }


def _resolve_ayanamsa_mode(payload: Dict[str, Any]) -> str:
    return payload.get("core_chart", {}).get("ayanamsa_mode", const._DEFAULT_AYANAMSA_MODE)


def _build_chakra_context(
    payload: Dict[str, Any],
    cfg: ChakraConfig,
) -> Tuple[BirthContext, drik.Place]:
    base_context, base_place = payload_utils.build_birth_context_from_payload(payload)
    location_name = base_place.Place
    latitude = base_place.latitude
    longitude = base_place.longitude
    tz_name = base_context.tz_name
    tz_offset = base_place.timezone
    if cfg.place_override:
        latitude = float(cfg.place_override.get("lat", latitude))
        longitude = float(cfg.place_override.get("lon", longitude))
        tz_offset = float(cfg.place_override.get("tz_offset_hours", tz_offset))
        location_name = cfg.place_override.get("name", location_name)
    dt_local = base_context.dt_local
    if cfg.datetime_override:
        dt_local = _parse_datetime(cfg.datetime_override, tz_name)
        tz_name = dt_local.tzinfo.tzname(dt_local) if dt_local.tzinfo else tz_name
    dt_naive = dt_local.replace(tzinfo=None)
    resolved_context = make_birth_context(
        dt_naive,
        latitude,
        longitude,
        tz_name=tz_name,
        location_name=location_name,
    )
    place = drik.Place(location_name, latitude, longitude, tz_offset)
    return resolved_context, place


def _parse_datetime(value: str, fallback_tz: str) -> datetime:
    dt = datetime.fromisoformat(value)
    if dt.tzinfo:
        return dt.astimezone(pytz.timezone(dt.tzinfo.tzname(dt) or fallback_tz))
    tz = pytz.timezone(fallback_tz)
    return tz.localize(dt)


def _build_sarvatobhadra_layer(planet_positions: List) -> Dict[str, Any]:
    grid_values = [
        ["ii", 23, 24, 25, 26, 27, 1, 2, "a"],
        [22, "rii", "g", "s", "d", "ch", "l", "u", 3],
        [28, "kh", "ai", 11, 12, 1, "lu", "a", 4],
        [21, "j", 10, "ah", "Rikita Fri", "o", 2, "v", 5],
        [20, "bh", 9, "Jaya Thu", "Pooma Sat", "Nanda Sun Tue", 3, "k", 6],
        [19, "y", 8, "am", "Bhadra Mon Wed", "au", 4, "h", 7],
        [18, "n", "e", 7, 6, 5, "luu", "d", 8],
        [17, "ri", "t", "r", "p", "t~", "m", "uu", 9],
        ["i", 16, 15, 14, 13, 12, 11, 10, "aa"],
    ]
    grid: List[Dict[str, Any]] = []
    hits: Dict[str, Dict[str, Any]] = {}
    star_cell_map: Dict[int, str] = {}
    for row_idx, row in enumerate(grid_values):
        for col_idx, value in enumerate(row):
            cell_id = f"SARVA_R{row_idx}C{col_idx}"
            cell: Dict[str, Any] = {"id": cell_id, "row": row_idx, "col": col_idx}
            border_cell = row_idx in (0, 8) or col_idx in (0, 8)
            if isinstance(value, int):
                if border_cell:
                    cell["type"] = "nakshatra"
                    cell["label"] = NAKSHATRA_SHORT_NAMES[value - 1]
                    star_cell_map[value] = cell_id
                else:
                    cell["type"] = "rasi"
                    cell["label"] = RAASI_SHORT_NAMES[value - 1]
            else:
                cell["type"] = "label"
                cell["label"] = value
            grid.append(cell)
    for planet_id, (sign_idx, deg) in planet_positions:
        absolute_deg = sign_idx * 30.0 + deg
        nakshatra_index = drik.nakshatra_pada(absolute_deg)[0]
        cell_id = star_cell_map.get(nakshatra_index)
        if not cell_id:
            continue
        entry = hits.setdefault(
            cell_id,
            {"cell_id": cell_id, "objects": [], "tags": []},
        )
        entry["objects"].append(_make_object_payload(planet_id))
    return {
        "name": "Sarvatobhadra",
        "grid": grid,
        "hits": list(hits.values()),
        "meta": {
            "source": "PYJHORA",
            "reference_chart": "D1",
        },
    }


def _build_kaala_layer(planet_positions: List, base_star: int) -> Dict[str, Any]:
    stars_inner = [4, 25, 18, 11]
    stars_outer = [
        [5, 6, 7],
        [3, 2, 1],
        [26, 27, 28],
        [24, 23, 22],
        [19, 20, 21],
        [17, 16, 15],
        [12, 13, 14],
        [10, 9, 8],
    ]
    inner_positions = [((base_star - 1 + (idx - 1)) % 28) for idx in stars_inner]
    inner_labels = [NAKSHATRA_SHORT_NAMES[i] for i in inner_positions]
    outer_positions = [
        [((base_star - 1 + (ele - 1)) % 28) for ele in row] for row in stars_outer
    ]
    outer_labels = [
        [NAKSHATRA_SHORT_NAMES[i] for i in row] for row in outer_positions
    ]
    for planet_id, (sign_idx, deg) in planet_positions:
        absolute_deg = sign_idx * 30.0 + deg
        nak = drik.nakshatra_pada(absolute_deg)[0] - 1
        if nak > const._ABHIJITH_STAR_INDEX:
            nak += 1
        label = _object_label(planet_id)
        if nak in inner_positions:
            idx = inner_positions.index(nak)
            inner_labels[idx] = f"{inner_labels[idx]}\n{label}"
        else:
            try:
                ridx, cidx = _find_index(outer_positions, nak)
                outer_labels[ridx][cidx] = f"{outer_labels[ridx][cidx]}\n{label}"
            except ValueError:
                continue
    grid = []
    for idx, (star, label) in enumerate(zip(inner_positions, inner_labels)):
        grid.append(
            {
                "id": f"KAALA_INNER_{idx}",
                "ring": "inner",
                "segment_index": idx,
                "nakshatra": NAKSHATRA_SHORT_NAMES[star],
                "label": label,
            }
        )
    for seg_idx, row in enumerate(outer_labels):
        for step_idx, label in enumerate(row):
            grid.append(
                {
                    "id": f"KAALA_OUTER_{seg_idx}_{step_idx}",
                    "ring": "outer",
                    "segment_index": seg_idx,
                    "step": step_idx,
                    "label": label,
                }
            )
    return {
        "name": "Kaala",
        "grid": grid,
        "hits": [],
        "meta": {"source": "PYJHORA"},
    }


def _build_kota_layer(
    planet_positions: List,
    birth_star: int,
    birth_pada: int,
    place: drik.Place,
) -> Dict[str, Any]:
    star_grid = [
        [1, 7, 8, 14, 15, 21, 22, 28],
        [2, 6, 9, 13, 16, 20, 23, 27],
        [3, 5, 10, 12, 17, 19, 24, 26],
        [4, 11, 18, 25],
    ]
    star_labels = _rotate_kota_grid(star_grid, birth_star)
    cell_map: Dict[str, Dict[str, Any]] = {}
    grid: List[Dict[str, Any]] = []
    for layer_idx, row in enumerate(star_labels):
        for col_idx, label in enumerate(row):
            cell_id = f"KOTA_L{layer_idx}_C{col_idx}"
            cell = {
                "id": cell_id,
                "layer": layer_idx,
                "position": col_idx,
                "nakshatra": label,
            }
            grid.append(cell)
            cell_map[label] = cell
    hits: Dict[str, Dict[str, Any]] = {}
    for planet_id, (sign_idx, deg) in planet_positions:
        absolute_deg = sign_idx * 30.0 + deg
        nak = drik.nakshatra_pada(absolute_deg)[0]
        label = NAKSHATRA_SHORT_NAMES[nak - 1]
        cell = cell_map.get(label)
        if not cell:
            continue
        entry = hits.setdefault(
            cell["id"], {"cell_id": cell["id"], "objects": [], "tags": []}
        )
        entry["objects"].append(_make_object_payload(planet_id))
    moon_house = planet_positions[2][1][0]
    kota_lord = PLANET_NAME_MAP[house.house_owner_from_planet_positions(planet_positions, moon_house)]
    kota_paala = PLANET_NAME_MAP[
        const.kota_paala_lord_for_star_paadha[birth_star - 1][birth_pada - 1]
    ]
    return {
        "name": "Kota",
        "grid": grid,
        "hits": list(hits.values()),
        "meta": {
            "kota_lord": kota_lord,
            "kota_paala": kota_paala,
            "source": "PYJHORA",
        },
    }


def _build_shoola_layer(planet_positions: List, base_star: int) -> Dict[str, Any]:
    template = {
        1: (5, 1),
        2: (4, 2),
        3: (4, 3),
        4: (4, 4),
        5: (4, 5),
        6: (4, 6),
        7: (4, 7),
        8: (3, 10),
        9: (2, 11),
        10: (1, 10),
        11: (1, 9),
        12: (1, 8),
        13: (2, 7),
        14: (4, 10),
        15: (5, 11),
        16: (6, 10),
        17: (6, 9),
        18: (6, 8),
        19: (6, 8),
        20: (7, 10),
        21: (8, 11),
        22: (9, 10),
        23: (9, 9),
        24: (9, 8),
        25: (8, 7),
        26: (6, 4),
        27: (6, 3),
        28: (6, 2),
    }
    star_map: Dict[int, Dict[str, Any]] = {}
    for offset, (x, y) in template.items():
        nak = ((base_star - 1) + (offset - 1)) % 28
        star_map[nak + 1] = {
            "id": f"SHOOLA_{nak+1}",
            "coords": (x, y),
            "label": NAKSHATRA_SHORT_NAMES[nak],
        }
    for planet_id, (sign_idx, deg) in planet_positions:
        absolute_deg = sign_idx * 30.0 + deg
        nak = drik.nakshatra_pada(absolute_deg)[0]
        cell = star_map.get(nak)
        if not cell:
            continue
        label = _object_label(planet_id)
        cell["label"] = f"{cell['label']}\n{label}"
    grid = [
        {"id": value["id"], "label": value["label"], "coords": value["coords"]}
        for value in star_map.values()
    ]
    return {
        "name": "Shoola",
        "grid": grid,
        "hits": [],
        "meta": {"source": "PYJHORA"},
    }


def _build_tripataki_layer(planet_positions: List) -> Dict[str, Any]:
    grid: List[Dict[str, Any]] = []
    cell_lookup: Dict[int, Dict[str, Any]] = {}
    for idx, (x, y) in enumerate(TRIPATAKI_POSITIONS):
        sign_idx = idx % len(RAASI_SHORT_NAMES)
        cell_id = f"TRIPATAKI_{sign_idx+1}"
        cell = {
            "id": cell_id,
            "sign_index": sign_idx,
            "label": RAASI_SHORT_NAMES[sign_idx],
            "coords": {"x": x, "y": y},
        }
        grid.append(cell)
        cell_lookup[sign_idx] = cell
    hits: Dict[str, Dict[str, Any]] = {}
    for planet_id, (sign_idx, _) in planet_positions:
        if isinstance(planet_id, str):
            continue
        cell = cell_lookup.get(sign_idx)
        if not cell:
            continue
        entry = hits.setdefault(
            cell["id"],
            {"cell_id": cell["id"], "objects": [], "tags": []},
        )
        entry["objects"].append(_make_object_payload(planet_id))
    return {
        "name": "Tripataki",
        "grid": grid,
        "hits": list(hits.values()),
        "meta": {"source": "PYJHORA"},
    }


def _build_surya_kalanala_layer(planet_positions: List, base_star: int) -> Dict[str, Any]:
    return _build_star_layer("surya_kalanala", SURYA_TEMPLATE, base_star, planet_positions)


def _build_chandra_kalanala_layer(planet_positions: List, base_star: int) -> Dict[str, Any]:
    return _build_star_layer("chandra_kalanala", CHANDRA_TEMPLATE, base_star, planet_positions)


def _build_saptha_shalaka_layer(planet_positions: List, base_star: int) -> Dict[str, Any]:
    return _build_star_layer("saptha_shalaka", SAPTHA_TEMPLATE, base_star, planet_positions)


def _build_pancha_shalaka_layer(planet_positions: List, base_star: int) -> Dict[str, Any]:
    return _build_star_layer("pancha_shalaka", PANCHA_TEMPLATE, base_star, planet_positions)


def _build_star_layer(
    layer_name: str,
    template: Dict[int, Tuple[float, float]],
    base_star: int,
    planet_positions: List,
) -> Dict[str, Any]:
    total = len(ABHIJIT_ORDER)
    grid: List[Dict[str, Any]] = []
    cell_lookup: Dict[int, Dict[str, Any]] = {}
    for template_idx, (x, y) in sorted(template.items()):
        position = ((base_star - 1) + (template_idx - 1)) % total
        encoded_index = position + 1
        actual_star = ABHIJIT_ORDER[position] + 1
        cell = {
            "id": f"{layer_name.upper()}_{encoded_index}",
            "encoded_index": encoded_index,
            "nakshatra_index": actual_star,
            "nakshatra": NAKSHATRA_SHORT_NAMES[ABHIJIT_ORDER[position]],
            "coords": {"x": x, "y": y},
        }
        grid.append(cell)
        cell_lookup[encoded_index] = cell
    hits: Dict[str, Dict[str, Any]] = {}
    for planet_id, (sign_idx, deg) in planet_positions:
        absolute_deg = sign_idx * 30.0 + deg
        nak = drik.nakshatra_pada(absolute_deg)[0]
        encoded = _encode_nakshatra_index(nak)
        cell = cell_lookup.get(encoded)
        if not cell:
            continue
        entry = hits.setdefault(
            cell["id"],
            {"cell_id": cell["id"], "objects": [], "tags": []},
        )
        entry["objects"].append(_make_object_payload(planet_id))
    pretty_name = layer_name.replace("_", " ").title()
    return {
        "name": pretty_name,
        "grid": grid,
        "hits": list(hits.values()),
        "meta": {"source": "PYJHORA", "base_star": base_star},
    }


def _encode_nakshatra_index(actual_index: int) -> int:
    encoded = actual_index
    if encoded > ABHIJITH_INDEX:
        encoded += 1
    return encoded


def _rotate_kota_grid(grid: Sequence[Sequence[int]], birth_star: int) -> List[List[str]]:
    rotated: List[List[str]] = []
    ordered = [NAKSHATRA_SHORT_NAMES[i] for i in const.abhijit_order_of_stars]
    for row in grid:
        rotated_row: List[str] = []
        for ele in row:
            idx = ((birth_star - 1) + (ele - 1)) % 28
            rotated_row.append(ordered[idx])
        rotated.append(rotated_row)
    return rotated


def _find_index(table: Sequence[Sequence[int]], target: int) -> Tuple[int, int]:
    for row_idx, row in enumerate(table):
        for col_idx, value in enumerate(row):
            if value == target:
                return row_idx, col_idx
    raise ValueError("Value not found")


def _make_object_payload(planet_id) -> Dict[str, str]:
    if planet_id == const._ascendant_symbol or planet_id == "L":
        return {"type": "lagna", "name": "Ascendant"}
    idx = int(planet_id)
    return {"type": "planet", "name": PLANET_NAME_MAP[idx]}


def _object_label(planet_id) -> str:
    payload = _make_object_payload(planet_id)
    return payload["name"]


__all__ = [
    "compute_chakra_snapshot",
    "ChakraConfig",
    "CHAKRA_SCHEMA_VERSION",
]
