import jsonschema
import pytest

from refraction_engine import run_yogas
from ._utils import load_json


@pytest.mark.parametrize("fixture", [
    "references/in/mehran_birth.json",
    "references/in/athena_birth.json",
])
def test_yogas_matches_schema(fixture: str):
    schema = load_json("docs/specs/yogas_spec_v1.schema.json")
    payload = load_json(fixture)
    result = run_yogas(payload)

    jsonschema.validate(instance=result, schema=schema)
