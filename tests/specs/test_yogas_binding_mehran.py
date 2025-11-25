from refraction_engine import run_yogas
from ._utils import load_json

VALID_CATEGORIES = {
    "PANCHA_MAHAPURUSHA",
    "RAJA",
    "WEALTH",
    "DOSHA",
    "CHANDRA",
    "SURYA",
    "NABHASA",
    "SPECIAL",
    "OTHER",
}


def test_yogas_mehran_structure():
    payload = load_json("references/in/mehran_birth.json")
    result = run_yogas(payload)

    assert "frames" in result
    yogas = result["frames"]["yogas"]
    summary = result["frames"]["summary"]

    assert isinstance(yogas, list)
    assert yogas, "No yogas detected for Mehran"

    assert summary["total_yogas"] == len(yogas)
    assert 0 <= summary["active_yogas"] <= summary["total_yogas"]

    categories = {y["category"] for y in yogas if y.get("category")}
    assert categories.issubset(VALID_CATEGORIES)

    for yoga in yogas:
        assert 1 <= yoga.get("tier", 0) <= 4
        assert yoga.get("active") in {True, False}
        assert yoga.get("strength") in {"STRONG", "MODERATE", "WEAK"}
