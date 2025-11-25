from refraction_engine import run_core_chart, run_panchanga

from ._utils import load_json


def test_minimal_payload_runs_core_chart():
    payload = load_json("references/in/minimal_birth.json")
    result = run_core_chart(payload)
    assert result["meta"]["schema_version"] == "core_chart_spec_v1"
    frame = result["frames"][0]
    assert frame["ascendant"]["sign_index"] in range(1, 13)


def test_minimal_payload_runs_panchanga():
    payload = load_json("references/in/minimal_birth.json")
    result = run_panchanga(payload)
    assert result["meta"]["schema_version"] == "panchanga_spec_v1"
    assert "tithi" in result["panchanga"]
