import json
from pathlib import Path

import jsonschema
import pytest

from refraction_engine import run_transit

from ._utils import load_json


def _load_schema():
    path = Path(__file__).resolve().parents[2] / "docs" / "specs" / "transit_spec_v1.schema.json"
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


@pytest.mark.parametrize(
    "fixture_path",
    ["references/in/mehran_birth.json", "references/in/athena_birth.json"],
)
def test_transit_matches_schema(fixture_path):
    payload = load_json(fixture_path)
    birth = payload.get("birth", {})
    location = birth.get("location", {})
    payload["reference"] = {
        "datetime_local": birth.get("datetime_local"),
        "timezone_name": birth.get("timezone_name"),
        "location": {
            "latitude": location.get("latitude") or location.get("lat"),
            "longitude": location.get("longitude") or location.get("lon"),
            "place_name": location.get("name"),
        },
    }
    schema = _load_schema()
    result = run_transit(payload)
    jsonschema.validate(instance=result, schema=schema)
