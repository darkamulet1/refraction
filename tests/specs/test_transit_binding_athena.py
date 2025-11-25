from refraction_engine import run_transit

from ._utils import load_json


def _prepare_transit_payload(base_path: str):
    payload = load_json(base_path)
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
    return payload


def test_transit_athena_basic():
    payload = _prepare_transit_payload("references/in/athena_birth.json")
    result = run_transit(payload)
    frame = result["frames"][0]

    assert frame["frame_id"] == "TRANSIT"
    assert frame["ascendant"]["house_index"] == 1
    assert "planets" in frame and len(frame["planets"]) >= 6
