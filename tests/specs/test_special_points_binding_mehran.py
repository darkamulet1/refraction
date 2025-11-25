from refraction_engine import run_special_points

from ._utils import load_json


def test_special_points_mehran_structure():
    payload = load_json("references/in/mehran_birth.json")
    result = run_special_points(payload)

    assert "meta" in result
    assert "frames" in result
    special_lagnas = result["frames"]["special_lagnas"]
    assert isinstance(special_lagnas, list)
    assert len(special_lagnas) == 4

    ids = {lagna["id"] for lagna in special_lagnas}
    expected = {"BHAVA_LAGNA", "HORA_LAGNA", "GHATI_LAGNA", "SREE_LAGNA"}
    assert ids == expected

    for lagna in special_lagnas:
        assert "longitude_deg" in lagna
        assert 1 <= lagna["sign_index"] <= 12
        assert 1 <= lagna["nakshatra_index"] <= 27
