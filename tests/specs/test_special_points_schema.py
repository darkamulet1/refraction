import jsonschema

import pytest

from refraction_engine import run_special_points

from ._utils import load_json


@pytest.mark.parametrize(
    "fixture",
    ["references/in/mehran_birth.json", "references/in/athena_birth.json"],
)
def test_special_points_schema(fixture):
    payload = load_json(fixture)
    schema = load_json("docs/specs/special_points_spec_v1.schema.json")
    result = run_special_points(payload)
    jsonschema.validate(instance=result, schema=schema)
