from refraction_engine import run_refraction_core

from ._utils import load_json


def test_refraction_core_bundle_athena():
    payload = load_json("references/in/athena_birth.json")
    bundle = run_refraction_core(payload)

    assert bundle["person"]["id"] == payload["person"]["id"]
    frames = bundle.get("frames") or {}

    for key in ("core_chart", "panchanga", "dashas_vimshottari", "strengths"):
        assert key in frames, f"Missing subframe {key}"
        assert isinstance(frames[key], dict) and frames[key], f"{key} frame empty"
