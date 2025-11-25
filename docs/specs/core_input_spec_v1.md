# core_input_spec_v1

## Purpose
Defines the canonical request payload that every Refraction Engine extractor accepts.  
All runtime helpers (`run_core_chart`, `run_panchanga`, …) assume this schema when parsing incoming data.

## Specification

```yaml
core_input_spec_v1:
  person?:
    id?: string
    label?: string

  birth:
    datetime_local: string        # ISO-8601 local timestamp (e.g., "1997-06-07T20:28:36")
    timezone_name: string         # IANA timezone identifier (e.g., "Asia/Tehran")
    location:
      name?: string
      lat: number
      lon: number

  config:
    zodiac_type: string           # "SIDEREAL" | "TROPICAL"
    ayanamsa_mode?: string        # required when zodiac_type == SIDEREAL
    ayanamsa_value_deg?: number   # required when ayanamsa_mode == "USER_DEFINED"
    house_system: string          # IDs from CorePrimitives house_systems catalog
    node_mode?: string            # "TRUE" | "MEAN" (default "TRUE")
    include_bodies?:              # default = CorePrimitives.planets ids
      - string
```

- All additional per-extractor knobs must be nested under `config` so the shared parser can validate them.

## Schema
See `docs/specs/core_input_spec_v1.schema.json` for the machine-readable validation rules that power the parser and tests.
