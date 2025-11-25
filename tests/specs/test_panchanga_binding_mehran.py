from refraction_engine import run_panchanga

from ._utils import load_json


def test_panchanga_mehran_basic():
    payload = load_json("references/in/mehran_birth.json")
    result = run_panchanga(payload)

    assert "meta" in result, "Panchanga result should include meta"
    panchanga = result.get("panchanga")
    assert isinstance(panchanga, dict), "Panchanga payload missing"

    for key in ("vaara", "tithi", "nakshatra", "sunrise", "sunset"):
        assert key in panchanga, f"Missing panchanga.{key}"

    vaara = panchanga["vaara"]
    assert vaara.get("index") == 6, f"Expected vaara index 6 (Saturday), got {vaara}"

    tithi = panchanga["tithi"]
    assert tithi.get("index") == 3, f"Unexpected tithi index: {tithi}"
    assert tithi.get("paksha") == "SHUKLA", f"Unexpected tithi paksha: {tithi}"

    nakshatra = panchanga["nakshatra"]
    assert nakshatra.get("index") == 7, f"Unexpected nakshatra index: {nakshatra}"

    # Derived from current PyJHora output for Mehran's birth timestamp
    assert panchanga["yoga"].get("index") == 11, "Yoga index drift"
    assert panchanga["karana"].get("index") == 5, "Karana index drift"
