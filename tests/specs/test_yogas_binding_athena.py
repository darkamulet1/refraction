from refraction_engine import run_yogas
from ._utils import load_json


def test_yogas_athena_structure():
    payload = load_json("references/in/athena_birth.json")
    result = run_yogas(payload)

    assert "frames" in result
    yogas = result["frames"]["yogas"]
    summary = result["frames"]["summary"]

    assert isinstance(yogas, list)
    assert summary["total_yogas"] == len(yogas)
    assert summary["active_yogas"] == sum(1 for y in yogas if y.get("active"))

    assert "by_category" in summary
    assert "by_tier" in summary

    assert all(1 <= y.get("tier", 0) <= 4 for y in yogas)
