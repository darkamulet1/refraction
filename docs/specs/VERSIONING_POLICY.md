# VERSIONING_POLICY.md

Versioning rules for Refraction Engine specifications and outputs. Applies to every extractor (core_chart, panchanga, dashas_vimshottari, and future modules).

---

## Spec Naming & Payload Tagging
1. Each spec uses a monotonic suffix `*_spec_vN` (e.g., `core_chart_spec_v1`, `panchanga_spec_v1`).
2. All extractor outputs MUST set `meta.schema_version = "<name>_spec_vN"`, enabling clients to detect payload shape.
3. Example: `core_chart_spec_v2` would appear in the JSON as:
   ```json
   {
     "meta": {
       "schema_version": "core_chart_spec_v2",
       ...
     },
     ...
   }
   ```

## When to Bump Versions
### Mandatory bump (breaking change)
* Removing a field.
* Changing a field’s type or meaning (e.g., switching `sign_index` range or reformatting `planets` arrays).
* Renaming frames/levels without providing backwards-compatible aliases.
* Tightening validation such that previously valid payloads would now fail.

### Same version (non-breaking change)
* Adding new optional fields.
* Adding new frames/levels/periods where absence is permitted by schema.
* Expanding enum values when existing IDs remain stable.
* Fixing typos in descriptions or comments.

If uncertain, treat the change as breaking and increment `vN+1`.

## Compatibility Strategy
* Current engine only emits the latest spec version for each extractor.
* Legacy payloads (older schema_version) are considered read-only; client tooling is responsible for migration until a dedicated upgrade script exists.
* When introducing `*_spec_v2`, maintain the `*_spec_v1` docs/schemas for reference, but runtime output switches entirely to v2.

## Testing Impact
* Every version bump must update:
  - `docs/specs/<name>_spec_vN*.md/json` example files.
  - `docs/specs/<name>_spec_vN*.schema.json` to enforce the new contract.
  - Golden tests (`tests/specs/test_<name>_binding_*.py`) so assertions match the new schema.
  - Schema tests (`tests/specs/test_<name>_schema.py`) to target the new version.
* Guard suite (`pytest tests/specs`) must pass after these updates.

---

## Contributor Checklist
1. **Breaking change?** If yes, bump the spec to `vN+1` and update every payload’s `meta.schema_version`.
2. **Schema updated?** Ensure `docs/specs/<name>_spec_vN.schema.json` matches the new structure.
3. **Examples & docs?** Refresh the example JSON/MD files to mirror the new version.
4. **Tests adjusted?** Update golden/schema tests so they expect the new version and run `pytest tests/specs`.
5. **Communication?** Document the change (e.g., changelog or roadmap) so downstream consumers know a new spec version exists.
