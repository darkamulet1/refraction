from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional

from jhora import utils
from jhora.panchanga import drik
from jhora.horoscope.dhasa.graha import vimsottari

PLANET_NAME_MAP = {
    0: "SUN",
    1: "MOON",
    2: "MARS",
    3: "MERCURY",
    4: "JUPITER",
    5: "VENUS",
    6: "SATURN",
    7: "RAHU",
    8: "KETU",
}


@dataclass
class VimPeriod:
    md_lord: str
    ad_lord: Optional[str]
    pd_lord: Optional[str]
    start_jd_local: float
    end_jd_local: float
    start_iso_local: str
    end_iso_local: str


@dataclass
class VimshottariTimeline:
    engine: str
    seed: str
    birth_jd_local: float
    md: List[VimPeriod]
    md_ad: List[VimPeriod]
    md_ad_pd: List[VimPeriod]


def _place_from_birth_context(bc: BirthContext) -> drik.Place:
    label = bc.location_name or "Birth Place"
    return drik.Place(label, bc.latitude, bc.longitude, bc.utc_offset_hours)


def _planet_name(index: Optional[int]) -> Optional[str]:
    if index is None:
        return None
    return PLANET_NAME_MAP.get(index, str(index))


def _jd_to_iso(jd: float) -> str:
    year, month, day, fractional_hours = utils.jd_to_gregorian(jd)
    total_seconds = round(fractional_hours * 3600)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{year:04d}-{month:02d}-{day:02d}T{hours:02d}:{minutes:02d}:{seconds:02d}"


def _md_periods(mahadasas: "vimsottari.Dict") -> List[VimPeriod]:
    periods: List[VimPeriod] = []
    for lord, start in mahadasas.items():
        duration_days = vimsottari.vimsottari_dict[lord] * vimsottari.year_duration
        end = start + duration_days
        periods.append(
            VimPeriod(
                md_lord=_planet_name(lord),
                ad_lord=None,
                pd_lord=None,
                start_jd_local=start,
                end_jd_local=end,
                start_iso_local=_jd_to_iso(start),
                end_iso_local=_jd_to_iso(end),
            )
        )
    return periods


def _md_ad_periods(mahadasas: "vimsottari.Dict") -> List[VimPeriod]:
    periods: List[VimPeriod] = []
    for md_lord, md_start in mahadasas.items():
        bhuktis = vimsottari._vimsottari_bhukti(md_lord, md_start)
        for ad_lord, ad_start in bhuktis.items():
            duration_days = (
                vimsottari.vimsottari_dict[ad_lord]
                * vimsottari.vimsottari_dict[md_lord]
                / vimsottari.human_life_span_for_vimsottari_dhasa
            ) * vimsottari.year_duration
            end = ad_start + duration_days
            periods.append(
                VimPeriod(
                    md_lord=_planet_name(md_lord),
                    ad_lord=_planet_name(ad_lord),
                    pd_lord=None,
                    start_jd_local=ad_start,
                    end_jd_local=end,
                    start_iso_local=_jd_to_iso(ad_start),
                    end_iso_local=_jd_to_iso(end),
                )
            )
    return periods


def _md_ad_pd_periods(mahadasas: "vimsottari.Dict") -> List[VimPeriod]:
    periods: List[VimPeriod] = []
    for md_lord, md_start in mahadasas.items():
        bhuktis = vimsottari._vimsottari_bhukti(md_lord, md_start)
        for ad_lord, ad_start in bhuktis.items():
            antaras = vimsottari._vimsottari_antara(md_lord, ad_lord, ad_start)
            for pd_lord, pd_start in antaras.items():
                duration_days = (
                    vimsottari.vimsottari_dict[pd_lord]
                    * (vimsottari.vimsottari_dict[md_lord] / vimsottari.human_life_span_for_vimsottari_dhasa)
                    * (vimsottari.vimsottari_dict[ad_lord] / vimsottari.human_life_span_for_vimsottari_dhasa)
                ) * vimsottari.year_duration
                end = pd_start + duration_days
                periods.append(
                    VimPeriod(
                        md_lord=_planet_name(md_lord),
                        ad_lord=_planet_name(ad_lord),
                        pd_lord=_planet_name(pd_lord),
                        start_jd_local=pd_start,
                        end_jd_local=end,
                        start_iso_local=_jd_to_iso(pd_start),
                        end_iso_local=_jd_to_iso(end),
                    )
                )
    return periods


def build_vimshottari_timeline(
    jd_local: float,
    place: drik.Place,
    seed: str = "MOON",
) -> VimshottariTimeline:
    """
    Construct the full Vimshottari (MD/AD/PD) timeline for the supplied birth context.
    """

    mahadasas = vimsottari.vimsottari_mahadasa(jd_local, place)
    md_periods = _md_periods(mahadasas)
    md_ad_periods = _md_ad_periods(mahadasas)
    md_ad_pd_periods = _md_ad_pd_periods(mahadasas)

    return VimshottariTimeline(
        engine="PYJHORA_VIMSHOTTARI",
        seed=seed.upper(),
        birth_jd_local=jd_local,
        md=md_periods,
        md_ad=md_ad_periods,
        md_ad_pd=md_ad_pd_periods,
    )


def filter_periods(
    periods: Iterable[VimPeriod],
    *,
    start_jd: Optional[float] = None,
    end_jd: Optional[float] = None,
    md_lord: Optional[str] = None,
    ad_lord: Optional[str] = None,
    pd_lord: Optional[str] = None,
) -> List[VimPeriod]:
    """
    Utility helper to filter VimPeriod sequences by JD ranges or lords.
    """

    filtered: List[VimPeriod] = []
    for period in periods:
        if start_jd is not None and period.end_jd_local <= start_jd:
            continue
        if end_jd is not None and period.start_jd_local >= end_jd:
            continue
        if md_lord and period.md_lord != md_lord:
            continue
        if ad_lord and period.ad_lord != ad_lord:
            continue
        if pd_lord and period.pd_lord != pd_lord:
            continue
        filtered.append(period)
    return filtered


__all__ = [
    "VimPeriod",
    "VimshottariTimeline",
    "build_vimshottari_timeline",
    "filter_periods",
]
