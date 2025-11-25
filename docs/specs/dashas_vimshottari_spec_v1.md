# dashas_vimshottari_spec_v1

## Purpose
Defines the canonical output of the Vimsottari Mahadasa extractor `run_dashas_vimshottari`.

## Specification

```yaml
dashas_vimshottari_spec_v1:
  meta:
    schema_version: string  # "dashas_vimshottari_spec_v1"
    timestamp_utc: string

  person:
    name?: string
    birth_date: string
    birth_time: string
    timezone: string

  config_echo:
    zodiac_type: string
    ayanamsa_mode?: string
    ayanamsa_value_deg?: number
    house_system: string
    node_mode: string

  frames:
    - frame_id: string                # e.g., "VIMSOTTARI_MAHADASHA"
      description?: string
      levels:
        - level: "MAHADASHA"
          periods:
            - order_index: integer
              planet_id: string       # "KETU", "VENUS", ...
              start: string           # ISO-8601 (UTC)
              end: string             # ISO-8601 (UTC)
              duration_years: number  # canonical duration from PyJHora constants
```

## Schema
See `docs/specs/dashas_vimshottari_spec_v1.schema.json`.
