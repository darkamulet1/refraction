## v0min Core Engine Specification (v0)

### 1. Purpose

`v0min` is the smallest, UI-free, Parashara Light-free layer of the PyJHora engine. It is designed to:

- Accept explicit birth context data (local datetime, latitude, longitude, timezone label, optional location name).
- Convert that context into the same Swiss-ephemeris inputs PyJHora legacy uses.
- Produce a sidereal “core chart” (lagna + nine graha longitudes) through the existing PyJHora ayanamsa and timing logic.
- Remain stable enough for higher layers (dashas, divisional charts, analytics, AI inference) to consume without depending on GUI, PDF parsers, or PL parity fixtures.

### 2. Canonical Data Model (v0 core schema)

Snapshots under `data/charts/*.yaml` are the source of truth (see `mehran_core.yaml`, `athena_core.yaml`). Each payload MUST follow this shape:

| Field | Type | Notes |
| --- | --- | --- |
| `person` | string | Human label (e.g., `"Mehran"`, `"Athena"`). |
| `datetime_local` | string | ISO-8601 local timestamp with offset, emitted via `BirthContext.dt_local.isoformat()`. |
| `location` | object | Describes the birth place exactly as supplied to `make_birth_context`. |
| `location.name` | string | Friendly place name (e.g., `"Tehran"`, `"Karaj"`). |
| `location.lat` | float | Latitude in decimal degrees (positive = north, negative = south). |
| `location.lon` | float | Longitude in decimal degrees (positive = east, negative = west). |
| `location.tz_name` | string | IANA timezone identifier (e.g., `"Asia/Tehran"`). |
| `ayanamsa` | string | Current default is `"LAHIRI"`. Other modes must be declared explicitly. |
| `time_resolution` | object | Captures timing metadata derived from the birth context. |
| `time_resolution.utc_offset_at_birth_hours` | float | Offset (hours) returned by the timezone database at that instant (includes DST, so Tehran examples show `4.5` or `3.5`). |
| `time_resolution.jd_utc` | float | Julian Day computed at UTC (kept for auditing and analytics; **not** fed into ephemeris). |
| `time_resolution.jd_local` | float | Julian Day computed from local civil time including DST via `swe.julday` (the canonical JD for all PyJHora ephemeris calls). |
| `time_resolution.jd_mode` | string | Currently `"LOCAL_WITH_DST"`; future schema updates must version this value if the JD standard changes. |
| `core_chart` | object | Output of `compute_core_chart`. See below. |

#### `core_chart` structure

The current core chart payload is a dictionary with:

- `ayanamsa_mode`: string (e.g., `"LAHIRI"`) — whatever was passed to `compute_core_chart`.
- `lagna_longitude_deg`: float — absolute ecliptic longitude of the ascendant in degrees `[0, 360)`.
- `planets`: object — mapping of graha names to absolute ecliptic longitudes in degrees `[0, 360)`. The canonical graha set (and order used in tests) is:
  - `Sun`, `Moon`, `Mars`, `Mercury`, `Jupiter`, `Venus`, `Saturn`, `Rahu`, `Ketu`.

This entire YAML layout is declared the **v0 core schema**. Future modifications MUST be:

- Backwards compatible (additive fields, same semantics), **or**
- Versioned explicitly (e.g., bump `jd_mode` and document migrations).

### 3. Timing & Ayanamsa Assumptions

- `make_birth_context` treats `datetime_local` + `tz_name` as authoritative. The timezone database (pytz/ZoneInfo) determines the UTC offset, including seasonal DST rules.
- `jd_local` is produced via `swe.julday(local_time_with_DST)` and is the **only** JD that drives `compute_core_chart`/Swiss ephemeris (matching PyJHora legacy behaviour). `jd_utc` remains available for diagnostics but is not consumed by the engine.
- v0 currently standardizes on the Lahiri ayanamsa; consumers may request another mode via `compute_core_chart(..., ayanamsa_mode="...")`. Any non-Lahiri use must be explicit.

### 4. Core API Contract

`v0min` exposes the following minimal API (see `src/v0min/*.py`):

- `make_birth_context(dt_local, lat, lon, tz_name, location_name=None) -> BirthContext`
  - Localizes the naive datetime, computes UTC, derives `jd_local`/`jd_utc`, and captures offsets using PyJHora utilities.
- `compute_core_chart(birth_context, ayanamsa_mode="LAHIRI") -> dict`
  - Uses `jd_local` together with `jhora.panchanga.drik` + `jhora.horoscope.chart.charts` to generate lagna + planet positions that match PyJHora legacy output.
- `save_core_chart(path, payload)` / `load_core_chart(path) -> dict`
  - Persist or read the YAML payloads defined above.

### 5. Compliance Tests

`tests/v0/test_core_chart_mehran.py` and `tests/v0/test_core_chart_athena.py` are the canonical regression suite for this spec. They reconstruct `BirthContext` objects from the YAML snapshots and assert that `compute_core_chart` reproduces lagna/planet longitudes within 0.1°. All future additions to v0min must keep these tests—and any new parity fixtures built by the CLI—in sync with this contract.
