import jsonschema
import pytest

from ._utils import load_json


@pytest.mark.parametrize(
    "fixture",
    [
        "references/in/mehran_birth.json",
        "references/in/athena_birth.json",
        "references/in/minimal_birth.json",
    ],
)
def test_core_input_matches_schema(fixture: str):
    schema = load_json("docs/specs/core_input_spec_v1.schema.json")
    payload = load_json(fixture)
    jsonschema.validate(instance=payload, schema=schema)
