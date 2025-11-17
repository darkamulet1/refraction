from __future__ import annotations

import contextlib
import io
import re
from dataclasses import dataclass
from html import unescape
from typing import Any, Dict, List, Optional

from jhora import const, utils
from jhora.horoscope.chart import charts
from jhora.horoscope.prediction import general as general_prediction
from jhora.horoscope.prediction import longevity as longevity_prediction
from jhora.horoscope.prediction import naadi_marriage as naadi_prediction

from v0min import payload_utils

PREDICTIONS_SCHEMA_VERSION = "predictions.v1"
ENGINE_NAME = "PYJHORA_PREDICTIONS"

_DEFAULT_SECTION_SOURCE = "GENERAL"
_SECTION_ID_OVERRIDES = {
    "planets": "PLANETS_IN_HOUSES",
    "houses": "HOUSE_LORDS",
}


def _normalize_section_id(title: str) -> str:
    candidate = _SECTION_ID_OVERRIDES.get(title.lower())
    if candidate:
        return candidate
    normalized = re.sub(r"[^A-Za-z0-9]+", "_", title).strip("_")
    return normalized.upper() or "SECTION"


def _extract_paragraphs(html_text: str) -> List[str]:
    text = unescape(html_text or "")
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</?b>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"</?html>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    paragraphs = [segment.strip() for segment in text.split("\n")]
    return [segment for segment in paragraphs if segment]


def _clean_language(config: Optional[Dict[str, Any]]) -> str:
    cfg_lang = (config or {}).get("language")
    if isinstance(cfg_lang, str) and cfg_lang:
        return cfg_lang
    return getattr(utils, "_DEFAULT_LANGUAGE", "en")  # type: ignore[attr-defined]


def _build_general_predictions(
    jd_local: float,
    place,
    language: str,
) -> Dict[str, Any]:
    previous_language = utils.language if hasattr(utils, "language") else None
    utils.set_language(language)
    raw_sections = general_prediction.get_prediction_details(jd_local, place, language=language)
    sections: List[Dict[str, Any]] = []
    full_text: List[str] = []
    for title, html_text in raw_sections.items():
        paragraphs = _extract_paragraphs(html_text)
        if not paragraphs:
            continue
        sections.append(
            {
                "id": _normalize_section_id(title),
                "title": title,
                "source": _DEFAULT_SECTION_SOURCE,
                "paragraphs": paragraphs,
            }
        )
        full_text.extend(paragraphs)
    if previous_language:
        utils.set_language(previous_language)
    return {
        "sections": sections,
        "raw": {"full_text": full_text},
    }


def _silent_call(func, *args, **kwargs):
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        return func(*args, **kwargs)


def _build_naadi_marriage_block(
    planet_positions: List,
    gender: int,
) -> Dict[str, Any]:
    try:
        yogas = _silent_call(naadi_prediction._check_marriage_yogas, planet_positions, gender)  # type: ignore[attr-defined]
    except Exception:
        yogas = None
    if not yogas:
        return {"enabled": False, "paragraphs": [], "notes": None}
    paragraphs = []
    for index, (flag, message) in enumerate(yogas, start=1):
        label = f"Yoga-{index}: {message or 'No indication'}"
        if not flag and not message:
            continue
        paragraphs.append(label if flag else f"{label} (not triggered)")
    return {
        "enabled": any(flag for flag, _ in yogas),
        "paragraphs": paragraphs,
        "notes": None,
    }


def _build_longevity_block(jd_local: float, place) -> Dict[str, Any]:
    try:
        span_index = longevity_prediction.life_span_range(jd_local, place)
        span_label = const.aayu_types[span_index] if 0 <= span_index < len(const.aayu_types) else "Unknown"
        summary = f"Life span classification: {span_label}"
        return {"enabled": True, "summary": summary, "paragraphs": [summary]}
    except Exception:
        return {"enabled": False, "summary": None, "paragraphs": []}


def compute_predictions_block(full_payload: Dict[str, Any], config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Build predictions.v1 payload from a *_full_pyjhora.json snapshot.
    """

    bc, place = payload_utils.build_birth_context_from_payload(full_payload)
    language = _clean_language(config)

    include_general = config.get("include_general", True) if config else True
    include_naadi = config.get("include_naadi_marriage", True) if config else True
    include_longevity = config.get("include_longevity", True) if config else True
    gender_value = (config or {}).get("gender")
    gender = 0
    if isinstance(gender_value, str):
        token = gender_value.strip().lower()
        if token in {"female", "f", "woman", "girl"}:
            gender = 1
    elif isinstance(gender_value, (int, float)):
        gender = 1 if int(gender_value) == 1 else 0

    block: Dict[str, Any] = {
        "schema_version": PREDICTIONS_SCHEMA_VERSION,
        "engine": ENGINE_NAME,
    }
    if include_general:
        block["general"] = _build_general_predictions(bc.jd_local, place, language)

    chart_positions = payload_utils.get_chart_positions(full_payload, "D1")
    if chart_positions is None:
        chart_positions = charts.rasi_chart(bc.jd_local, place)

    if include_naadi:
        block["naadi_marriage"] = _build_naadi_marriage_block(chart_positions, gender)

    if include_longevity:
        block["longevity"] = _build_longevity_block(bc.jd_local, place)

    return block


__all__ = ["compute_predictions_block", "PREDICTIONS_SCHEMA_VERSION"]
