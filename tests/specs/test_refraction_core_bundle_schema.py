import jsonschema
import pytest

from refraction_engine import run_refraction_core

from ._utils import load_json


@pytest.mark.parametrize(
    "fixture",
    [
        "references/in/mehran_birth.json",
        "references/in/athena_birth.json",
    ],
)
def test_refraction_core_bundle_schema(fixture: str):
    schema = load_json("docs/specs/refraction_core_bundle_spec_v1.schema.json")
    payload = load_json(fixture)
    bundle = run_refraction_core(payload)

    jsonschema.validate(instance=bundle, schema=schema)
