"""
Engine Configuration
Central config for all extractors.
"""

from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class ZodiacType(str, Enum):
    SIDEREAL = "SIDEREAL"
    TROPICAL = "TROPICAL"


class NodeMode(str, Enum):
    TRUE = "TRUE"
    MEAN = "MEAN"


class EngineConfig(BaseModel):
    """Central configuration for extractors."""

    zodiac_type: ZodiacType = ZodiacType.SIDEREAL
    ayanamsa_mode: str = "LAHIRI"
    house_system: str = "5"
    node_mode: NodeMode = NodeMode.TRUE
    include_bodies: List[str] = Field(
        default_factory=lambda: [
            "SUN",
            "MOON",
            "MERCURY",
            "VENUS",
            "MARS",
            "JUPITER",
            "SATURN",
            "RAHU",
            "KETU",
        ]
    )

    class Config:
        use_enum_values = True


DEFAULT_CONFIG = EngineConfig()
