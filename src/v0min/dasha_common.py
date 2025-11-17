from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Literal, Optional

DashaLevel = Literal["MD", "AD", "PD", "SD"]
DashaSystem = Literal[
    "VIMSHOTTARI",
    "ASHTOTTARI",
    "DWADASOTTARI",
    "DWISATPATHI",
    "SHODASOTTARI",
    "PANCHOTTARI",
    "SHASTIHAYANI",
    "YOGINI",
    "KALACHAKRA",
    "NARAYANA",
    "PATTAYINI_VARSHIKA",
    "BRAHMA_RAASI",
    "CHAKRA_RAASI",
    "CHARA_RAASI",
    "LAGNAMSAKA_RAASI",
    "NAVAMSA_RAASI",
    "MANDOOKA_RAASI",
    "PARYAAYA_RAASI",
    "PADHANADHAMSA_RAASI",
    "SANDHYA_RAASI",
    "STHIRA_RAASI",
    "TARA_LAGNA_RAASI",
    "TRIKONA_RAASI",
    "VARNADA_RAASI",
    "YOGARDHA_RAASI",
]

DASHAS_SUPPORTED: List[DashaSystem] = [
    "VIMSHOTTARI",
    "ASHTOTTARI",
    "DWADASOTTARI",
    "DWISATPATHI",
    "SHODASOTTARI",
    "PANCHOTTARI",
    "SHASTIHAYANI",
    "YOGINI",
    "KALACHAKRA",
    "NARAYANA",
    "PATTAYINI_VARSHIKA",
    "BRAHMA_RAASI",
    "CHAKRA_RAASI",
    "CHARA_RAASI",
    "LAGNAMSAKA_RAASI",
    "NAVAMSA_RAASI",
    "MANDOOKA_RAASI",
    "PARYAAYA_RAASI",
    "PADHANADHAMSA_RAASI",
    "SANDHYA_RAASI",
    "STHIRA_RAASI",
    "TARA_LAGNA_RAASI",
    "TRIKONA_RAASI",
    "VARNADA_RAASI",
    "YOGARDHA_RAASI",
]

ENGINE_BY_SYSTEM: Dict[DashaSystem, str] = {
    "VIMSHOTTARI": "PYJHORA_VIMSHOTTARI",
    "ASHTOTTARI": "PYJHORA_ASHTOTTARI",
    "DWADASOTTARI": "PYJHORA_DWADASOTTARI",
    "DWISATPATHI": "PYJHORA_DWISATPATHI",
    "SHODASOTTARI": "PYJHORA_SHODASOTTARI",
    "PANCHOTTARI": "PYJHORA_PANCHOTTARI",
    "SHASTIHAYANI": "PYJHORA_SHASTIHAYANI",
    "YOGINI": "PYJHORA_YOGINI",
    "KALACHAKRA": "PYJHORA_KALACHAKRA",
    "NARAYANA": "PYJHORA_NARAYANA",
    "PATTAYINI_VARSHIKA": "PYJHORA_PATTAYINI",
    "BRAHMA_RAASI": "PYJHORA_BRAHMA_RAASI",
    "CHAKRA_RAASI": "PYJHORA_CHAKRA_RAASI",
    "CHARA_RAASI": "PYJHORA_CHARA_RAASI",
    "LAGNAMSAKA_RAASI": "PYJHORA_LAGNAMSAKA_RAASI",
    "NAVAMSA_RAASI": "PYJHORA_NAVAMSA_RAASI",
    "MANDOOKA_RAASI": "PYJHORA_MANDOOKA_RAASI",
    "PARYAAYA_RAASI": "PYJHORA_PARYAAYA_RAASI",
    "PADHANADHAMSA_RAASI": "PYJHORA_PADHANADHAMSA_RAASI",
    "SANDHYA_RAASI": "PYJHORA_SANDHYA_RAASI",
    "STHIRA_RAASI": "PYJHORA_STHIRA_RAASI",
    "TARA_LAGNA_RAASI": "PYJHORA_TARA_LAGNA_RAASI",
    "TRIKONA_RAASI": "PYJHORA_TRIKONA_RAASI",
    "VARNADA_RAASI": "PYJHORA_VARNADA_RAASI",
    "YOGARDHA_RAASI": "PYJHORA_YOGARDHA_RAASI",
}

PLANET_NAMES = ["SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN", "RAHU", "KETU"]


@dataclass
class DashaPeriod:
    level: DashaLevel
    system: str
    lord: str
    sublord: Optional[str]
    start_jd: float
    end_jd: Optional[float]
    start_iso: str
    end_iso: Optional[str]


@dataclass
class DashaTimeline:
    schema_version: str
    system: str
    engine: str
    system_type: str
    levels: List[str]
    periods: List[DashaPeriod]


__all__ = [
    "DashaLevel",
    "DashaSystem",
    "DashaPeriod",
    "DashaTimeline",
    "DASHAS_SUPPORTED",
    "ENGINE_BY_SYSTEM",
    "PLANET_NAMES",
]
