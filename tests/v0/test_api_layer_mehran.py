from __future__ import annotations

from pathlib import Path

from v0min import api

REF_PATH = Path("references/out/mehran_full_pyjhora.json")


def _build_yaml() -> dict:
    return api.build_full_yaml_from_birth_json(str(REF_PATH))


def test_build_full_yaml_enrichment_and_meta_sources() -> None:
    payload = _build_yaml()
    assert payload.get("core_charts"), "core charts should be present"

    chakra = payload.get("chakra")
    assert chakra and chakra.get("schema_version") == "chakra.v1"
    strength = payload.get("strength_trends")
    assert strength and strength.get("meta", {}).get("planet_basis") == "total_rupa"
    assert "normalized" not in strength

    sources = payload.get("meta", {}).get("sources", {})
    assert "chakras" in sources
    assert "strength_trends" in sources
    assert sources["strength_trends"].get("chart_id") == "D1"


def test_compute_chakras_via_api() -> None:
    payload = _build_yaml()
    chakra = api.compute_chakras(payload)
    assert chakra
    assert "layers" in chakra
    assert "sarvatobhadra" in chakra["layers"]


def test_compute_strength_trends_via_api() -> None:
    payload = _build_yaml()
    block = api.compute_strength_trends(payload)
    assert block.get("planet_ranking")
    assert block.get("meta", {}).get("sign_basis") == "SAV"
    assert "normalized" not in block
