# core_chart_spec_v1

## Purpose
Describes the required input & output contracts for the `refraction_engine.core_chart` extractor. All inputs must match `core_chart_input_v1`, and outputs must follow `core_chart_v1`. The extractor stays PyJHora-friendly (references to `jhora.panchanga.drik` / `jhora.horoscope.chart.charts` implied) but contains no implementation details or `v0min` references.

## Input schema (`core_chart_input_v1`)

```yaml
core_chart_input_v1:
  person:
    name: string
    birth_date: string      # ISO-8601 date yyyy-mm-dd
    birth_time: string      # ISO-8601 time HH:MM:SS
    timezone: string        # IANA timezone
  location:
    latitude: number
    longitude: number
    elevation_m?: number
  config:
    ayanamsa_mode: string    # matches keys from CorePrimitives ayanamsa_modes
    house_system: string     # keys from CorePrimitives house_systems
    divisional_factor?: integer  # default 1, e.g., D1=1, D9=9
    node_mode?: string        # "mean" | "true"
    output_sections?:        # subset of standard sections
      - core
      - panchanga
      - dashas
      - strengths
      - yogas
      - special_points
      - transits
  meta:
    request_id?: string
```

## Output schema (`core_chart_v1`)

```yaml
core_chart_v1:
  meta:
    timestamp_utc: string        # ISO-8601
    ayanamsa_deg: number?
    jd_utc: number?
  person:
    name: string
    birth_date: string
    birth_time: string
    timezone: string
  config_echo:
    ayanamsa_mode: string
    house_system: string
    divisional_factor: integer
    node_mode: string
  frames:
    - frame_id: string          # e.g., "D1","D9"
      description: string
      jd: number
      place:
        latitude: number
        longitude: number
      ascendant:
        longitude_deg: float
        degree_in_sign: float
        sign_index: integer
        sign_name: string
        house_index: integer
        nakshatra_index: integer
        nakshatra_name: string
        nakshatra_pada: integer
      planets:
        - id: string
          name: string
          longitude_deg: float
          degree_in_sign: float
          sign_index: integer
          sign_name: string
          house_index: integer
          retrograde: boolean
          speed_deg_per_day?: float
          nakshatra_index: integer
          nakshatra_name: string
          nakshatra_pada: integer
      houses:
        - index: integer           # 1..12
          start_deg: float
          end_deg: float
          cusp_deg: float
          sign_index: integer
          sign_name: string
```

## Nakshatra conventions

- `nakshatra_index`: 1-based standard ordering (1=Ashwini, 2=Bharani, ..., 27=Revati), consistent with `docs/pyjhora_knowledge/primitives/CorePrimitives.json`.  
- `nakshatra_pada`: 1..4, determined by dividing the 13°20′ nakshatra span into four equal parts (each ≈3°20′).  
- `nakshatra_name` should match the uppercase string given in `CorePrimitives`.  
- All longitude fields are sidereal and match PyJHora output (via `charts.divisional_chart` or `drik` helpers).
