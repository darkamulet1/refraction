from __future__ import annotations

from typing import Any, Dict, Optional

from jhora import const

from v0min.strength import shadbala as shadbala_module
from v0min.strength import vargiya as vargiya_module
from v0min.core_time import BirthContext


def compute_shadbala_block(
    bc: BirthContext,
    ayanamsa_mode: str = const._DEFAULT_AYANAMSA_MODE,
) -> Dict[str, Any]:
    context = {
        "birth_context": bc,
        "ayanamsa_mode": ayanamsa_mode,
    }
    return shadbala_module.compute(context)["shadbala"]


def compute_misc_balas(
    bc: BirthContext,
    ayanamsa_mode: str = const._DEFAULT_AYANAMSA_MODE,  # kept for future extensions
) -> Dict[str, Any]:
    context = {
        "birth_context": bc,
        "ayanamsa_mode": ayanamsa_mode,
    }
    return vargiya_module.compute(context)


__all__ = ["compute_shadbala_block", "compute_misc_balas"]
