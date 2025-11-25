# EXTRACTOR_TEMPLATE_V1

Developer checklist for introducing any new Refraction Engine extractor. Each step mirrors the patterns already used for `core_chart`, `panchanga`, and `dashas_vimshottari`.

---

## Step 1 – Author `<name>_spec_v1.example.json`

1. Create `docs/specs/<name>_spec_v1.example.json` describing the canonical payload:
   - `meta`: includes `schema_version`, `timestamp_utc`, plus optional engine metadata.
   - `person`: `id`, `label/name`, `birth_date`, `birth_time`, `timezone`.
   - `config_echo`: echo the resolved engine config (zodiac type, ayanamsa_mode, house_system, node_mode, include_bodies, etc.).
   - `frames`: main container for extractor results. Follow the “frame → levels → periods/items” nesting used in existing specs.
2. Link to earlier examples for structure inspiration:
   - `docs/specs/core_chart_spec_v1.md`
   - `docs/specs/panchanga_spec_v1.md`
   - `docs/specs/dashas_vimshottari_spec_v1.md`
3. Use IDs/indexes from CorePrimitives; do not invent new localized strings in the spec.

## Step 2 – Provide `<name>_spec_v1.schema.json`

1. Define the JSON Schema in `docs/specs/<name>_spec_v1.schema.json` (draft-07):
   - Require `meta`, `person`, `config_echo`, and `frames` at top level.
   - Ensure `meta.schema_version` is a string constant (e.g., `"dashas_vimshottari_spec_v1"`).
   - `frames` is an array; each frame requires `frame_id` and either `levels` or `data` (depending on the extractor).
2. Conventions to reuse:
   - Indices/IDs are integers/strings from CorePrimitives constants (`nakshatra_index`, `planet_id`, `vaara.index`, etc.).
   - Avoid schema fields that encode localized names; localized labels live in CorePrimitives or UI layers.
   - Additional properties are allowed inside nested nodes only when future expansion is expected; otherwise set `"additionalProperties": false` for stability.
3. Store example data (from Step 1) beside the schema to guide future contributors.

## Step 3 – Implement `run_<name>` in `src/refraction_engine`

1. Add `run_<name>(payload: dict) -> dict` inside `src/refraction_engine/<name>.py` (or extend an existing module):
   - Reuse `_parse_core_chart_input` (or the shared input parser) for input normalization.
   - Build PyJHora configuration via `_build_pyjhora_config` and load canonical constants from `CorePrimitives.json`.
   - Only consume PyJHora APIs listed in `docs/specs/api_whitelist_core_chart_v1.example.json` or a future `<name>` whitelist.
   - Keep the extractor pure: return dicts, no side-effects/logging, rely on spec fields only.
2. Update `src/refraction_engine/__init__.py` to export the new `run_<name>` function.

## Step 4 – Golden Tests (`tests/specs/test_<name>_binding_*.py`)

1. Add per-person golden tests (at least `Mehran` and `Athena`):
   - Load `references/in/<person>_birth.json` via `tests/specs/_utils.load_json`.
   - Invoke `run_<name>` and assert the invariant facts: stable ID order, sign indexes, period counts, etc.
   - Assertions should use indexes/codes (e.g., `nakshatra_index`, `planet_id`) instead of localized names.
2. For multi-frame outputs (dashas), assert chronological ordering, number of periods, and that exactly one element carries `is_current=True` when relevant.

## Step 5 – Schema Test (`tests/specs/test_<name>_schema.py`)

1. Create `tests/specs/test_<name>_schema.py`:
   - Parametrize over Mehran and Athena payloads.
   - Load the schema from `docs/specs/<name>_spec_v1.schema.json`.
   - Validate the extractor output against the schema using `jsonschema.validate`.
2. Include minimal/edge cases (e.g., payload with optional fields omitted) when the schema allows it (`tests/specs/test_minimal_payloads.py` is an example reference).

## Step 6 – Guard Suite Integration

1. Ensure the new binding and schema tests live under `tests/specs/` so `pytest tests/specs` triggers them automatically.
2. If you maintain a guard script (e.g., `scripts/run_guard_suite.sh`), append the new tests there.
3. Optional but recommended: note the extractor in the README or roadmap once it is fully guarded.

---

## Extractor Author Checklist

- [ ] `<name>_spec_v1.example.json` written with meta/person/config/frames.
- [ ] `<name>_spec_v1.schema.json` created and validated against the example payload.
- [ ] `run_<name>` implemented in `src/refraction_engine/` using shared parsers + CorePrimitives.
- [ ] Golden tests added (`tests/specs/test_<name>_binding_mehran.py`, `..._athena.py`).
- [ ] Schema test added (`tests/specs/test_<name>_schema.py`) with Mehran/Athena parametrization.
- [ ] Guard suite (`pytest tests/specs`) passes locally with the new extractor enabled.
