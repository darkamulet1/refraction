import jsonschema
import pytest

from refraction_engine import run_strengths

from ._utils import load_json


@pytest.mark.parametrize(
    "fixture",
    [
        "references/in/mehran_birth.json",
        "references/in/athena_birth.json",
    ],
)
def test_strengths_schema(fixture: str):
    schema = load_json("docs/specs/strengths_spec_v1.schema.json")
    payload = load_json(fixture)
    result = run_strengths(payload)

    jsonschema.validate(instance=result, schema=schema)
