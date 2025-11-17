from __future__ import annotations

from typing import Any, Dict, Iterable, Optional

from . import (
    ashtakavarga,
    avastha_strength,
    graha_yuddha,
    harsha,
    shadbala,
    tatkalika_bala,
    upagraha_bala,
    vargiya,
)

ENGINE_REGISTRY = {
    "shadbala": shadbala.compute,
    "vargiya": vargiya.compute,
    "ashtakavarga": ashtakavarga.compute,
    "harsha": harsha.compute,
    "avastha": avastha_strength.compute,
    "graha_yuddha": graha_yuddha.compute,
    "tatkalika": tatkalika_bala.compute,
    "upagraha": upagraha_bala.compute,
}

DEFAULT_ACTIVE = ("shadbala", "vargiya", "ashtakavarga")


def compute_strength_all(
    context: Dict[str, Any],
    *,
    active_only: bool = True,
    include: Optional[Iterable[str]] = None,
) -> Dict[str, Any]:
    """
    Run the selected strength engines and merge their outputs.
    """

    requested = set(DEFAULT_ACTIVE if active_only else ENGINE_REGISTRY.keys())
    if include:
        requested.update(_normalize_engine_name(name) for name in include)

    results: Dict[str, Any] = {}
    for key in requested:
        func = ENGINE_REGISTRY.get(key)
        if not func:
            continue
        block = func(context)
        if block:
            results.update(block)
    return results


def _normalize_engine_name(name: str) -> str:
    lowered = name.lower()
    if lowered.endswith("_bala"):
        lowered = lowered[:-5]
    return lowered
