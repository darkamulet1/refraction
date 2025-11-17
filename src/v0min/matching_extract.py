from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from jhora import const
from jhora.horoscope.match import compatibility as compat

ENGINE_NAME = "PYJHORA_MATCHING"
BAD_MARS_HOUSES = {1, 2, 4, 7, 8, 12}


@dataclass(frozen=True)
class ChartContext:
    name: str
    nakshatra_index: int
    nakshatra_pada: int
    lagna_deg: float
    moon_deg: float
    venus_deg: float
    mars_deg: float
    ayanamsa: str


@dataclass(frozen=True)
class ComponentDefinition:
    func_name: str
    detail_map: Optional[Dict[float, str]]
    max_score: float


COMPONENT_DEFS: Dict[str, ComponentDefinition] = {
    "varna": ComponentDefinition("varna_porutham", compat.varna_results, compat.varna_max_score),
    "vashya": ComponentDefinition("vasiya_porutham", compat.vasiya_results, compat.vasiya_max_score),
    "tara": ComponentDefinition("tara_porutham", compat.nakshathra_results, compat.nakshathra_max_score),
    "yoni": ComponentDefinition("yoni_porutham", compat.yoni_results, compat.yoni_max_score),
    "graha_maitri": ComponentDefinition(
        "maitri_porutham",
        compat.raasi_adhipathi_results,
        compat.raasi_adhipathi_max_score,
    ),
    "gana": ComponentDefinition("gana_porutham", compat.gana_results, compat.gana_max_score),
    "bhakoota": ComponentDefinition("bahut_porutham", compat.raasi_results, compat.raasi_max_score),
    "nadi": ComponentDefinition("naadi_porutham", compat.naadi_results, compat.naadi_max_score),
}

RAJJU_ZONES = [
    ("HEAD", set(compat.head_rajju)),
    ("NECK", set(compat.neck_rajju)),
    ("STOMACH", set(compat.stomach_rajju)),
    ("WAIST", set(compat.waist_rajju)),
    ("FOOT", set(compat.foot_rajju)),
]


def _rajju_zone_for_nakshatra(nakshatra_number: int) -> Optional[str]:
    for label, zone in RAJJU_ZONES:
        if nakshatra_number in zone:
            return label
    return None


def _chart_context(payload: Dict[str, Any]) -> ChartContext:
    birth = payload["birth_data"]
    panchanga = payload["panchanga_at_birth"]["nakshatra"]
    core_chart = payload["core_chart"]
    planets = core_chart["planets"]

    def _planet_deg(name: str) -> float:
        value = planets.get(name)
        if value is None:
            raise KeyError(f"Missing planet '{name}' in core_chart.planets")
        return float(value)

    return ChartContext(
        name=birth.get("person", "Unknown"),
        nakshatra_index=int(panchanga["index"]),
        nakshatra_pada=int(panchanga["pada"]),
        lagna_deg=float(core_chart["lagna_longitude_deg"]),
        moon_deg=float(planets["Moon"]),
        venus_deg=float(planets["Venus"]),
        mars_deg=float(planets["Mars"]),
        ayanamsa=core_chart.get("ayanamsa_mode", "UNKNOWN"),
    )


def _normalize_score(value: Any) -> float:
    if value is None:
        return 0.0
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    return float(value)


def _compute_component(ak: compat.Ashtakoota, name: str, cfg: ComponentDefinition) -> Dict[str, Any]:
    raw_result = getattr(ak, cfg.func_name)()
    if isinstance(raw_result, tuple):
        score, max_score = raw_result
    else:
        score = raw_result
        max_score = cfg.max_score
    score = _normalize_score(score)
    max_score = float(max_score) if max_score is not None else None
    detail = None
    if cfg.detail_map and score in cfg.detail_map:
        detail = cfg.detail_map[score]
    return {
        "score": score,
        "max": max_score,
        "detail": detail,
    }


def _grade_from_score(score: float) -> str:
    if score >= 30:
        return "Excellent"
    if score >= 24:
        return "Good"
    if score >= 18:
        return "Medium"
    return "Poor"


def _house_from_reference(reference_deg: float, planet_deg: float) -> int:
    diff = (planet_deg - reference_deg) % 360.0
    return int(diff // 30.0) + 1


def _has_mangal_dosha(chart: ChartContext) -> bool:
    references = (chart.lagna_deg, chart.moon_deg, chart.venus_deg)
    for ref in references:
        house = _house_from_reference(ref, chart.mars_deg)
        if house in BAD_MARS_HOUSES:
            return True
    return False


def _narrative_flags(report: Dict[str, Any]) -> List[str]:
    flags: List[str] = []
    total_score = report["total"]["score"]
    doshas = report["dosha_flags"]

    if not doshas["mangal_dosha_chart_1"] and not doshas["mangal_dosha_chart_2"]:
        flags.append("No Mangal dosha detected for either chart.")
    if doshas["nadi_dosha"]:
        flags.append("Nadi dosha present; same Nadi type for both charts.")
    if doshas["bhakoot_dosha"]:
        flags.append("Bhakoot dosha flagged (Moon sign incompatibility).")
    if total_score >= 30 and not doshas["nadi_dosha"] and not doshas["bhakoot_dosha"]:
        flags.append("High compatibility with clean Nadi and Bhakoot scores.")
    if total_score < 18:
        flags.append("Overall score is low; further analysis recommended.")
    return flags


def _stri_dirgha_threshold(method: str) -> int:
    if method.lower().startswith("south"):
        return int(const.sthree_dheerga_threshold_south)
    return int(const.sthree_dheerga_threshold)


def _build_naalu_porutham_block(ak: compat.Ashtakoota, method: str) -> Dict[str, Dict[str, Any]]:
    count_from_girl = ak.count_from_girl
    boy_sum = ak.boy_nakshatra_number
    girl_sum = ak.girl_nakshatra_number
    mahendra_ok = bool(ak.mahendra_porutham())
    vedha_ok = bool(ak.vedha_porutham())
    rajju_ok = bool(ak.rajju_porutham())
    stri_ok = bool(ak.sthree_dheerga_porutham())
    boy_zone = _rajju_zone_for_nakshatra(boy_sum)
    girl_zone = _rajju_zone_for_nakshatra(girl_sum)
    rajju_type = boy_zone if boy_zone and boy_zone == girl_zone else None
    threshold = _stri_dirgha_threshold(method)

    return {
        "Mahendra": {
            "is_compatible": mahendra_ok,
            "score": 1.0 if mahendra_ok else 0.0,
            "details": f"Star distance from girl to boy: {count_from_girl}",
        },
        "Vedha": {
            "is_compatible": vedha_ok,
            "score": None,
            "details": f"Nakshatra sum={boy_sum + girl_sum}",
        },
        "Rajju": {
            "is_compatible": rajju_ok,
            "score": None,
            "type": rajju_type,
            "details": f"Boy zone={boy_zone or 'UNKNOWN'}, Girl zone={girl_zone or 'UNKNOWN'}",
        },
        "Stri_Dirgha": {
            "is_compatible": stri_ok,
            "score": None,
            "details": f"Count from girl={count_from_girl}, threshold>{threshold}",
        },
    }


def _build_filters_block(total_score: float, method: str, naalu: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    min_score = (
        const.compatibility_minimum_score_south
        if method.lower().startswith("south")
        else const.compatibility_minimum_score_north
    )
    flags = {
        "meets_min_score": total_score >= min_score,
        "mahendra_porutham": naalu["Mahendra"]["is_compatible"],
        "vedha_porutham": naalu["Vedha"]["is_compatible"],
        "rajju_porutham": naalu["Rajju"]["is_compatible"],
        "stri_dirgha_porutham": naalu["Stri_Dirgha"]["is_compatible"],
    }
    is_db_eligible = all(flags.values())
    return {"is_db_eligible": is_db_eligible, "minimum_score": min_score, "flags": flags}


def compute_ashtakoota_matching(
    payload_one: Dict[str, Any],
    payload_two: Dict[str, Any],
    *,
    method: str = "North",
    chart_ref_1: Optional[str] = None,
    chart_ref_2: Optional[str] = None,
    source_one: Optional[str] = None,
    source_two: Optional[str] = None,
    include_naalu_porutham: bool = True,
    include_filters: bool = True,
) -> Dict[str, Any]:
    """
    Public entry point that builds the full matching report. Backwards-compatible with the original skeleton name.
    """

    return build_matching_report(
        payload_one,
        payload_two,
        method=method,
        chart_ref_1=chart_ref_1,
        chart_ref_2=chart_ref_2,
        source_one=source_one,
        source_two=source_two,
        include_naalu_porutham=include_naalu_porutham,
        include_filters=include_filters,
    )


def build_matching_report(
    payload_one: Dict[str, Any],
    payload_two: Dict[str, Any],
    *,
    method: str = "North",
    chart_ref_1: Optional[str] = None,
    chart_ref_2: Optional[str] = None,
    source_one: Optional[str] = None,
    source_two: Optional[str] = None,
    include_naalu_porutham: bool = True,
    include_filters: bool = True,
) -> Dict[str, Any]:
    chart_one = _chart_context(payload_one)
    chart_two = _chart_context(payload_two)
    chart_ref_1 = chart_ref_1 or chart_one.name
    chart_ref_2 = chart_ref_2 or chart_two.name

    ak = compat.Ashtakoota(
        chart_one.nakshatra_index,
        chart_one.nakshatra_pada,
        chart_two.nakshatra_index,
        chart_two.nakshatra_pada,
        method=method,
    )

    component_results: Dict[str, Dict[str, Any]] = {}
    total_score = 0.0
    total_max = 0.0
    for key, cfg in COMPONENT_DEFS.items():
        component = _compute_component(ak, key, cfg)
        component_results[key] = component
        if component["score"] is not None:
            total_score += component["score"]
        if component["max"] is not None:
            total_max += component["max"]

    meta = {
        "engine": ENGINE_NAME,
        "method": method,
        "ayanamsa": chart_one.ayanamsa,
        "chart_ref_1": chart_ref_1,
        "chart_ref_2": chart_ref_2,
        "source_file_1": source_one,
        "source_file_2": source_two,
    }

    dosha_flags = {
        "mangal_dosha_chart_1": _has_mangal_dosha(chart_one),
        "mangal_dosha_chart_2": _has_mangal_dosha(chart_two),
        "nadi_dosha": component_results["nadi"]["score"] == 0.0,
        "bhakoot_dosha": component_results["bhakoota"]["score"] == 0.0,
        "rajju_conflict": not ak.rajju_porutham(),
        "vedha_conflict": not ak.vedha_porutham(),
        "stri_dirgha_issue": not ak.sthree_dheerga_porutham(),
        "mahendra_benefit": ak.mahendra_porutham(),
    }

    report = {
        "meta": meta,
        "ashtakoota": {
            "score": total_score,
            "max": total_max,
            "components": component_results,
        },
        "total": {
            "score": total_score,
            "max": total_max,
            "grade": _grade_from_score(total_score),
        },
        "dosha_flags": dosha_flags,
        "narrative_flags": [],
    }
    report["narrative_flags"] = _narrative_flags(report)
    naalu_block = _build_naalu_porutham_block(ak, method)
    if include_naalu_porutham:
        report["naalu_porutham"] = naalu_block
    if include_filters:
        report["filters"] = _build_filters_block(total_score, method, naalu_block)
    return report


def build_matching_report_from_files(
    chart_one_path: Path | str,
    chart_two_path: Path | str,
    *,
    method: str = "North",
    include_naalu_porutham: bool = True,
    include_filters: bool = True,
) -> Dict[str, Any]:
    path_one = Path(chart_one_path)
    path_two = Path(chart_two_path)
    payload_one = json.loads(path_one.read_text(encoding="utf-8"))
    payload_two = json.loads(path_two.read_text(encoding="utf-8"))
    return build_matching_report(
        payload_one,
        payload_two,
        method=method,
        source_one=str(path_one),
        source_two=str(path_two),
        include_naalu_porutham=include_naalu_porutham,
        include_filters=include_filters,
    )


def save_matching_report(report: Dict[str, Any], out_path: Path | str) -> Path:
    path = Path(out_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def matching_schema_template() -> Dict[str, Any]:
    components = {
        name: {
            "score": None,
            "max": cfg.max_score,
            "detail": None,
        }
        for name, cfg in COMPONENT_DEFS.items()
    }
    return {
        "meta": {
            "engine": ENGINE_NAME,
            "method": "North",
            "ayanamsa": None,
            "chart_ref_1": None,
            "chart_ref_2": None,
            "source_file_1": None,
            "source_file_2": None,
        },
        "ashtakoota": {
            "score": None,
            "max": 36.0,
            "components": components,
        },
        "total": {"score": None, "max": 36.0, "grade": None},
        "dosha_flags": {
            "mangal_dosha_chart_1": None,
            "mangal_dosha_chart_2": None,
            "nadi_dosha": None,
            "bhakoot_dosha": None,
            "rajju_conflict": None,
            "vedha_conflict": None,
            "stri_dirgha_issue": None,
            "mahendra_benefit": None,
        },
        "narrative_flags": [],
        "naalu_porutham": {
            "Mahendra": {"is_compatible": None, "score": None, "details": None},
            "Vedha": {"is_compatible": None, "score": None, "details": None},
            "Rajju": {"is_compatible": None, "score": None, "type": None, "details": None},
            "Stri_Dirgha": {"is_compatible": None, "score": None, "details": None},
        },
        "filters": {
            "is_db_eligible": None,
            "minimum_score": None,
            "flags": {
                "meets_min_score": None,
                "mahendra_porutham": None,
                "vedha_porutham": None,
                "rajju_porutham": None,
                "stri_dirgha_porutham": None,
            },
        },
    }


__all__ = [
    "compute_ashtakoota_matching",
    "build_matching_report",
    "build_matching_report_from_files",
    "save_matching_report",
    "matching_schema_template",
]
