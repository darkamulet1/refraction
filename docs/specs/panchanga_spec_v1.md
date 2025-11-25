# panchanga_spec_v1

## Purpose
Normative schema for the Panchanga payload emitted by Refraction Engine V1. Focuses on Moon-based calendar data (tithi, Moon’s nakshatra, yoga, karana) plus contextual timing windows.  
Keeps the spec engine-agnostic and references PyJHora only by naming the relevant concepts.

## Specification

```yaml
panchanga:
  reference:
    datetime_utc: string     # ISO-8601 timestamp
    timezone: string         # IANA timezone string
    location:
      latitude: number
      longitude: number
      elevation_m?: number

  tithi:
    index: integer            # 1..30
    name: string              # e.g., "Prathamai","Amavasai"
    paksha: string            # "SHUKLA" | "KRISHNA"
    remaining_percentage: float  # 0.0..1.0 (optional)

  nakshatra:
    index: integer            # 1..27 (Moon's nakshatra index)
    name: string              # uppercase, e.g., "PUNARVASU"
    pada: integer             # 1..4 (Moon’s pada/quarter)
    lord: string              # Graha lord (e.g., "JUPITER")
    span_deg: float           # 0.0.. <13.3333 (progress through nakshatra)

  yoga:
    index: integer
    name: string

  karana:
    index: integer
    name: string

  hora_lord: string           # Planet ID or name currently ruling the hora

  sunrise: string             # ISO-8601 local or UTC string
  sunset: string              # ISO-8601 string

  auspicious_windows:
    - start: string
      end: string
      tag?: string

  inauspicious_windows:
    - start: string
      end: string
      tag?: string
```

## Nakshatra note

- `panchanga.nakshatra` always refers to the **Moon’s Nakshatra** at the reference moment and location (used for dasha seeds, daily calendars, and festival calculators).  
- Nakshatra data for the Ascendant and other planets is defined separately in `core_chart_spec_v1`.  
- `lord` should mirror the Graha associated with the nakshatra per `CorePrimitives` (e.g., Jupiter for Punarvasu).
