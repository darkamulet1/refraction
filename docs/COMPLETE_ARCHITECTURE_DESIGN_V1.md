# 🏗️ طراحی کامل معماری Refraction Engine V1

**بر اساس**: PyJHora Knowledge Pack (21,166 lines)  
**تاریخ**: 2025-11-25  
**نسخه**: 2.0 (Post Gap #1 & #3)

---

## 📐 معماری کلی

```
┌─────────────────────────────────────────────────────────────┐
│                      USER INTERFACE                          │
│  (React/FastAPI - Future Phase)                             │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                  REFRACTION ENGINE V1                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Parsers    │  │  Validators  │  │   Config     │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                  │                  │              │
│  ┌──────▼──────────────────▼──────────────────▼───────┐    │
│  │            Extractor Factory                        │    │
│  │  (core_chart, panchanga, dashas, strengths, ...)   │    │
│  └──────────────────────┬──────────────────────────────┘    │
│                         │                                    │
│  ┌──────────────────────▼──────────────────────────────┐    │
│  │              graha.py (Gap #1) ✅                   │    │
│  │  - GrahaID, RasiID, NakshatraID enums              │    │
│  │  - Bidirectional mappings                          │    │
│  │  - Calculation utilities                           │    │
│  │  - CorePrimitives sync                             │    │
│  └──────────────────────┬──────────────────────────────┘    │
└──────────────────────────┼──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                      PYJHORA V4.5.5                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ drik module  │  │charts module │  │ dhasa module │     │
│  │  (panchanga) │  │  (divisional)│  │ (vimsottari) │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │strength mod  │  │  yoga module │  │transit module│     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                   SWISS EPHEMERIS                            │
│  (High-precision astronomical calculations)                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 ساختار پروژه

```
refraction-engine-v1/
├── src/
│   └── refraction_engine/
│       ├── __init__.py
│       │
│       ├── core/                          # 🆕 Core components
│       │   ├── __init__.py
│       │   ├── graha.py                   # ✅ Gap #1 - DONE
│       │   ├── primitives_parser.py       # 🆕 CorePrimitives parser
│       │   ├── config.py                  # 🆕 Engine configuration
│       │   └── validation.py              # 🆕 Input validation
│       │
│       ├── extractors/                    # 🆕 Extractors folder
│       │   ├── __init__.py
│       │   ├── base.py                    # Base extractor class
│       │   ├── core_chart.py              # 🔄 Refactored
│       │   ├── panchanga.py               # 🔄 Refactored
│       │   ├── dashas_vimshottari.py      # 🔄 Refactored
│       │   ├── strengths.py               # 🔄 Refactored
│       │   ├── special_points.py          # 🆕 Future
│       │   ├── yogas.py                   # 🆕 Future
│       │   └── transits.py                # 🆕 Future
│       │
│       ├── factory.py                     # 🆕 Extractor factory
│       ├── utils.py                       # Utilities
│       └── exceptions.py                  # Custom exceptions
│
├── tests/
│   ├── refraction_engine/
│   │   ├── test_graha.py                  # ✅ Gap #1 - DONE
│   │   ├── test_primitives_parser.py      # 🆕
│   │   ├── test_config.py                 # 🆕
│   │   └── test_validation.py             # 🆕
│   │
│   ├── specs/                             # Schema & binding tests
│   │   ├── test_core_chart*.py            # ✅ Existing
│   │   ├── test_panchanga*.py             # ✅ Existing
│   │   ├── test_dashas*.py                # ✅ Existing
│   │   └── test_strengths*.py             # ✅ Existing
│   │
│   └── parity/                            # ✅ Gap #3 - DONE
│       ├── test_parity_arezoo.py
│       └── test_parity_arman.py
│
├── docs/
│   ├── specs/                             # Spec definitions
│   │   ├── core_input_spec_v1.md          # ✅ Existing
│   │   ├── core_chart_spec_v1.md          # ✅ Existing
│   │   ├── panchanga_spec_v1.md           # ✅ Existing  
│   │   ├── dashas_vimshottari_spec_v1.md  # ✅ Existing
│   │   ├── strengths_spec_v1.md           # 🆕 TODO
│   │   ├── special_points_spec_v1.md      # 🆕 TODO
│   │   ├── yogas_spec_v1.md               # 🆕 TODO
│   │   └── engine_config_spec_v1.yaml     # 🆕 TODO
│   │
│   └── pyjhora_knowledge/                 # ✅ Knowledge pack
│       ├── reference/                     # Markdown docs
│       ├── inventory/                     # API inventory
│       ├── primitives/                    # CorePrimitives.json
│       ├── maps/                          # Structural maps
│       └── ...
│
├── scripts/
│   ├── run_guard_suite.sh                 # ✅ Existing
│   └── run_parity_suite.sh                # ✅ Gap #3 - DONE
│
├── references/
│   ├── in/                                # Input fixtures
│   │   ├── mehran_birth.json
│   │   ├── arezoo_birth.json
│   │   └── ...
│   │
│   └── out/                               # Golden outputs
│       ├── mehran_core_bundle.json
│       └── ...
│
└── .github/
    └── workflows/
        └── ci.yml                         # ✅ Gap #3 - CI with parity
```

---

## 🔧 Core Components (New)

### 1. primitives_parser.py

```python
"""
CorePrimitives Parser
Parses CorePrimitives.json and provides structured access.
"""

from pathlib import Path
from typing import Dict, List, Any
import json

class PrimitivesParser:
    """Parse and validate CorePrimitives.json"""
    
    def __init__(self, primitives_path: Path = None):
        if primitives_path is None:
            primitives_path = Path(__file__).parent.parent.parent / 'docs' / 'pyjhora_knowledge' / 'primitives' / 'CorePrimitives.json'
        
        with open(primitives_path) as f:
            self._data = json.load(f)
        
        self._validate()
        self._parse()
    
    def _validate(self):
        """Validate structure of CorePrimitives.json"""
        required_keys = ['planets', 'rasis', 'ayanamsa_modes', 'house_systems', 'nakshatra_lords', 'vaara_names']
        for key in required_keys:
            if key not in self._data:
                raise ValueError(f"Missing required key: {key}")
    
    def _parse(self):
        """Parse raw data into structured formats"""
        # Parse planets (handle string tuples)
        self.planets = self._parse_planet_list(self._data['planets'])
        
        # Parse ayanamsa modes
        self.ayanamsa_modes = {
            mode['internal_constant']: mode
            for mode in self._data['ayanamsa_modes']
        }
        
        # Parse house systems
        self.house_systems = {
            hs['id']: hs
            for hs in self._data['house_systems']
        }
        
        # Parse nakshatra lords (direct list)
        self.nakshatra_lords = self._data['nakshatra_lords']
        
        # Parse vaara names
        self.vaara_names = self._data['vaara_names']
    
    def _parse_planet_list(self, raw_planets: List[str]) -> List[tuple]:
        """
        Parse planet list from string tuples to actual tuples
        
        Input: ["(12, 1)", "(22, -1)", ...]
        Output: [(12, 1), (22, -1), ...]
        """
        import ast
        return [ast.literal_eval(p) for p in raw_planets]
    
    def get_ayanamsa_id(self, name: str) -> int:
        """Get ayanamsa ID by name"""
        mode = self.ayanamsa_modes.get(name.upper())
        if not mode:
            raise ValueError(f"Unknown ayanamsa: {name}")
        return mode['id']
    
    def get_house_system_id(self, name: str) -> str:
        """Get house system ID by name"""
        for hs_id, hs_data in self.house_systems.items():
            if hs_data['name'].upper() == name.upper():
                return hs_id
        raise ValueError(f"Unknown house system: {name}")
    
    def get_nakshatra_lord(self, nakshatra_index: int) -> int:
        """Get lord of nakshatra (0-26)"""
        if not 0 <= nakshatra_index < 27:
            raise ValueError(f"Invalid nakshatra index: {nakshatra_index}")
        return self.nakshatra_lords[nakshatra_index]


# Singleton instance
_primitives = None

def get_primitives() -> PrimitivesParser:
    """Get singleton PrimitivesParser instance"""
    global _primitives
    if _primitives is None:
        _primitives = PrimitivesParser()
    return _primitives
```

---

### 2. config.py

```python
"""
Engine Configuration System
Handles all Refraction Engine configuration options.
"""

from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, validator
from .primitives_parser import get_primitives


class ZodiacType(str, Enum):
    SIDEREAL = "SIDEREAL"
    TROPICAL = "TROPICAL"


class NodeMode(str, Enum):
    TRUE = "TRUE"
    MEAN = "MEAN"


class EngineConfig(BaseModel):
    """Central configuration for Refraction Engine"""
    
    # Zodiac settings
    zodiac_type: ZodiacType = ZodiacType.SIDEREAL
    ayanamsa_mode: str = "LAHIRI"
    ayanamsa_value_deg: Optional[float] = None  # For USER_DEFINED
    
    # House settings
    house_system: str = "5"  # EQUAL (Whole Sign)
    
    # Planet settings
    node_mode: NodeMode = NodeMode.TRUE
    include_bodies: List[str] = Field(
        default_factory=lambda: [
            "SUN", "MOON", "MERCURY", "VENUS", "MARS",
            "JUPITER", "SATURN", "RAHU", "KETU"
        ]
    )
    
    # Language
    language: str = "en"
    
    # Calculation type
    calculation_type: str = "drik"  # or "ss" for Surya Siddhanta
    
    @validator('ayanamsa_mode')
    def validate_ayanamsa(cls, v):
        """Validate against CorePrimitives"""
        primitives = get_primitives()
        if v.upper() not in primitives.ayanamsa_modes:
            valid = list(primitives.ayanamsa_modes.keys())
            raise ValueError(f"Invalid ayanamsa. Valid options: {valid}")
        return v.upper()
    
    @validator('house_system')
    def validate_house_system(cls, v):
        """Validate against CorePrimitives"""
        primitives = get_primitives()
        if v not in primitives.house_systems:
            valid = list(primitives.house_systems.keys())
            raise ValueError(f"Invalid house system. Valid options: {valid}")
        return v
    
    @validator('include_bodies')
    def validate_bodies(cls, v):
        """Validate planet list"""
        from .graha import GRAHA_STRING_IDS
        valid_bodies = list(GRAHA_STRING_IDS.values())
        for body in v:
            if body not in valid_bodies:
                raise ValueError(f"Invalid body: {body}. Valid options: {valid_bodies}")
        return v
    
    def to_pyjhora_params(self) -> Dict[str, Any]:
        """Convert to PyJHora-compatible parameters"""
        primitives = get_primitives()
        
        return {
            'ayanamsa_mode': self.ayanamsa_mode,
            'ayanamsa_id': primitives.get_ayanamsa_id(self.ayanamsa_mode),
            'house_system': self.house_system,
            'node_mode': self.node_mode.value,
            'calculation_type': self.calculation_type,
            'language': self.language,
        }
    
    class Config:
        use_enum_values = True


# Default configuration
DEFAULT_CONFIG = EngineConfig()
```

---

### 3. validation.py

```python
"""
Input Validation Layer
Validates all inputs against specs before processing.
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field, validator
from datetime import datetime
import jsonschema


class BirthInput(BaseModel):
    """Birth data input validation"""
    
    datetime_local: str = Field(..., description="ISO-8601 local timestamp")
    timezone_name: str = Field(..., description="IANA timezone (e.g., Asia/Tehran)")
    location: Dict[str, Any] = Field(..., description="Location data")
    
    @validator('datetime_local')
    def validate_datetime(cls, v):
        """Validate ISO-8601 format"""
        try:
            datetime.fromisoformat(v)
        except ValueError:
            raise ValueError(f"Invalid datetime format: {v}. Expected ISO-8601")
        return v
    
    @validator('location')
    def validate_location(cls, v):
        """Validate location has required fields"""
        if 'lat' not in v or 'lon' not in v:
            raise ValueError("Location must have 'lat' and 'lon' fields")
        
        lat, lon = v['lat'], v['lon']
        if not -90 <= lat <= 90:
            raise ValueError(f"Invalid latitude: {lat}")
        if not -180 <= lon <= 180:
            raise ValueError(f"Invalid longitude: {lon}")
        
        return v


class CoreInputPayload(BaseModel):
    """Complete input payload validation (core_input_spec_v1)"""
    
    person: Optional[Dict[str, str]] = None
    birth: BirthInput
    config: Dict[str, Any]
    
    @validator('config')
    def validate_config(cls, v):
        """Validate config section"""
        required = ['zodiac_type', 'house_system']
        for field in required:
            if field not in v:
                raise ValueError(f"Missing required config field: {field}")
        return v


def validate_input(payload: Dict[str, Any], schema_name: str) -> List[str]:
    """
    Validate input payload against JSON schema
    
    Returns:
        List of error messages (empty if valid)
    """
    from pathlib import Path
    
    # Load schema
    schema_path = Path(__file__).parent.parent.parent / 'docs' / 'specs' / f'{schema_name}.schema.json'
    
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema not found: {schema_path}")
    
    import json
    with open(schema_path) as f:
        schema = json.load(f)
    
    # Validate
    errors = []
    try:
        jsonschema.validate(instance=payload, schema=schema)
    except jsonschema.ValidationError as e:
        errors.append(str(e))
    
    return errors


def validate_core_input(payload: Dict[str, Any]) -> CoreInputPayload:
    """
    Validate core input payload (with Pydantic)
    
    Raises:
        ValidationError if invalid
    
    Returns:
        Validated payload object
    """
    return CoreInputPayload(**payload)
```

---

## 🏭 Extractor Factory

### factory.py

```python
"""
Extractor Factory
Creates and manages extractor instances.
"""

from typing import Dict, Any
from .config import EngineConfig
from .extractors.base import BaseExtractor


class ExtractorFactory:
    """Factory for creating extractors"""
    
    def __init__(self, config: EngineConfig = None):
        self.config = config or EngineConfig()
        self._extractors: Dict[str, type] = {}
        self._register_extractors()
    
    def _register_extractors(self):
        """Register all available extractors"""
        from .extractors.core_chart import CoreChartExtractor
        from .extractors.panchanga import PanchangaExtractor
        from .extractors.dashas_vimshottari import VimsottariDashaExtractor
        from .extractors.strengths import StrengthsExtractor
        
        self._extractors = {
            'core_chart': CoreChartExtractor,
            'panchanga': PanchangaExtractor,
            'dashas_vimshottari': VimsottariDashaExtractor,
            'strengths': StrengthsExtractor,
        }
    
    def create_extractor(self, name: str, payload: Dict[str, Any]) -> BaseExtractor:
        """
        Create extractor instance
        
        Args:
            name: Extractor name ('core_chart', 'panchanga', etc.)
            payload: Input payload
        
        Returns:
            Extractor instance
        
        Raises:
            ValueError if extractor not found
        """
        if name not in self._extractors:
            available = list(self._extractors.keys())
            raise ValueError(f"Unknown extractor: {name}. Available: {available}")
        
        extractor_class = self._extractors[name]
        return extractor_class(payload, self.config)
    
    def extract_all(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run all extractors and create bundle
        
        Returns:
            Complete refraction_core_bundle
        """
        bundle = {
            'meta': {
                'schema_version': 'refraction_core_bundle_spec_v1',
                'timestamp_utc': datetime.utcnow().isoformat(),
            },
            'person': payload.get('person', {}),
            'config_echo': self.config.dict(),
            'frames': {}
        }
        
        # Run each extractor
        for name in ['core_chart', 'panchanga', 'dashas_vimshottari', 'strengths']:
            try:
                extractor = self.create_extractor(name, payload)
                result = extractor.extract()
                bundle['frames'][name] = result
            except Exception as e:
                # Log error but continue
                bundle['frames'][name] = {'error': str(e)}
        
        return bundle
```

---

## 🔄 Base Extractor Class

### extractors/base.py

```python
"""
Base Extractor Class
All extractors inherit from this.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from datetime import datetime

from ..config import EngineConfig
from ..core.graha import *


class BaseExtractor(ABC):
    """Base class for all extractors"""
    
    def __init__(self, payload: Dict[str, Any], config: EngineConfig):
        self.payload = payload
        self.config = config
        self._parse_payload()
    
    def _parse_payload(self):
        """Parse common payload fields"""
        birth = self.payload['birth']
        
        # Birth data
        self.datetime_local = birth['datetime_local']
        self.timezone_name = birth['timezone_name']
        self.location = birth['location']
        
        # Person (optional)
        self.person = self.payload.get('person', {})
        
        # Parse datetime
        from datetime import datetime
        self.dt = datetime.fromisoformat(self.datetime_local)
        
        # Calculate JD
        self.jd = self._calculate_jd()
        
        # Create Place
        self.place = self._create_place()
    
    def _calculate_jd(self) -> float:
        """Calculate Julian Day from datetime"""
        import jhora.horoscope.chart.charts as charts
        from jhora import utils
        
        date_tuple = (self.dt.year, self.dt.month, self.dt.day)
        time_tuple = (self.dt.hour, self.dt.minute, self.dt.second)
        
        return utils.julian_day_number(date_tuple, time_tuple)
    
    def _create_place(self):
        """Create PyJHora Place object"""
        from jhora.panchanga import drik
        import pytz
        
        # Get timezone offset
        tz = pytz.timezone(self.timezone_name)
        offset = tz.utcoffset(self.dt).total_seconds() / 3600
        
        return drik.Place(
            self.location.get('name', 'Unknown'),
            self.location['lat'],
            self.location['lon'],
            offset
        )
    
    @abstractmethod
    def extract(self) -> Dict[str, Any]:
        """
        Extract data and return result
        
        Must be implemented by subclasses
        """
        pass
    
    def create_meta(self, schema_version: str, **kwargs) -> Dict[str, Any]:
        """Create standard meta section"""
        meta = {
            'schema_version': schema_version,
            'timestamp_utc': datetime.utcnow().isoformat(),
            'jd_utc': self.jd,
        }
        
        # Add ayanamsa if sidereal
        if self.config.zodiac_type == "SIDEREAL":
            from jhora.panchanga import drik
            drik.set_ayanamsa_mode(self.config.ayanamsa_mode)
            meta['ayanamsa_deg'] = drik.get_ayanamsa_value(self.jd)
        
        meta.update(kwargs)
        return meta
```

---

**ادامه در فایل بعدی...**
