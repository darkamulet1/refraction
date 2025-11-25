import ast
import json
import re
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.pyjhora_scanner.const_parser import parse_const


DATA_ROOT = REPO_ROOT / "src" / "jhora" / "data"
LANG_ROOT = REPO_ROOT / "src" / "jhora" / "lang"


def _parse_languages():
    languages = {}
    for path in sorted(LANG_ROOT.glob("list_values_*.txt")):
        code = path.name.replace("list_values_", "").replace(".txt", "")
        data = {}
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            values = [item.strip() for item in value.split(",") if item.strip()]
            data[key.strip().upper()] = values
        languages[code] = data
    return languages


def _purpose_from_path(path: Path) -> str:
    name = path.name.lower()
    if "ephe" in path.parts or path.suffix in (".se1", ".se2", ".sef", ".sefstars", ".zip", ".txt"):
        if "ephe" in path.parts:
            return "Swiss Ephemeris data file (" + path.name + ")"
    if "world_cities" in name:
        return "World cities database with timezone offsets"
    if "pancha_pakshi" in name:
        return "Pancha Pakshi Sastra data"
    if "marriage_compatibility" in name or "compatibility" in name:
        return "Marriage compatibility score database"
    if name.endswith(".csv"):
        return "Tabular dataset used by Panchanga/match components"
    return "Supporting data file"


def _find_consumers(file_name: str) -> list[str]:
    try:
        output = subprocess.run(
            ["rg", "-l", "--fixed-strings", "--no-messages", file_name, str(REPO_ROOT)],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return []
    lines = [line.strip() for line in output.stdout.splitlines() if line.strip()]
    modules = []
    for line in sorted(set(lines)):
        rel = Path(line).relative_to(REPO_ROOT)
        modules.append(str(rel))
        if len(modules) >= 8:
            break
    return modules


def build_core_primitives():
    cp, defaults = parse_const(REPO_ROOT)
    languages = _parse_languages()
    adi = defaults.get("division_chart_factors", [])
    vargas = [
        {"id": f"D{int(factor)}", "name": f"Divisional Chart D{int(factor)}", "divisor": factor, "implemented": True}
        for factor in adi
    ]
    planets = [entry.get("name") for entry in cp.planets if entry.get("name")]
    rasis = [entry.get("name") for entry in cp.rasis if entry.get("name")]
    if not planets:
        planets = languages.get("en", {}).get("PLANET_NAMES", [])
    if not rasis:
        rasis = languages.get("en", {}).get("RAASI_LIST", [])
    return {
        "planets": planets,
        "rasis": rasis,
        "vargas": vargas,
        "ayanamsa_modes": cp.ayanamsa,
        "house_systems": cp.house_systems,
        "defaults": defaults,
        "languages": languages,
    }


def build_data_map():
    entries = []
    if not DATA_ROOT.exists():
        return {"files": entries}
    for file in sorted(DATA_ROOT.rglob("*")):
        if not file.is_file():
            continue
        rel = file.relative_to(REPO_ROOT)
        entries.append(
            {
                "path": str(rel),
                "purpose": _purpose_from_path(file),
                "consumed_by": _find_consumers(file.name),
            }
        )
    return {"files": entries}


def build_tests_contract():
    canonical = [
        {
            "file": "jhora/tests/pvr_tests.py",
            "scope": "panchanga|dashas|charts",
            "notes": "Extensive regression suite that verifies panchanga, charts, dashas, and transit calculations from the PVR Rao book.",
        },
        {
            "file": "jhora/tests/test_yogas.py",
            "scope": "charts|yogas",
            "notes": "Validates yoga detection helpers (Sunapha, Kemadruma, Raja yogas, etc.).",
        },
        {
            "file": "jhora/tests/test_ui.py",
            "scope": "ui",
            "notes": "Smoke tests for the PyQt chart/panchanga UIs.",
        },
    ]
    def gather_representative(file_path):
        path = REPO_ROOT / "src" / file_path
        cases = []
        if not path.exists():
            return cases
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_") and len(cases) < 3:
                desc = ast.get_docstring(node) or ""
                cases.append(
                    {
                        "file": str(file_path),
                        "test_name": node.name,
                        "description": desc,
                        "inputs": {},
                        "expected": {},
                    }
                )
        return cases

    representative_cases = []
    for target in ["jhora/tests/pvr_tests.py", "jhora/tests/test_yogas.py"]:
        representative_cases.extend(gather_representative(target))
    return {"canonical_suites": canonical, "representative_cases": representative_cases}


def build_experimental_md():
    markers = ["EXPERIMENTAL", "NOT FULLY IMPLEMENTED", "UNDER TESTING", "TODO"]
    md_lines = ["# Experimental & Hidden Capabilities", ""]
    md_lines.append("## Experimental markers found in code")
    entries = {}
    for marker in markers:
        try:
            output = subprocess.run(
                ["rg", "-n", "--null", "--no-heading", "--fixed-strings", marker, str(REPO_ROOT / "src" / "jhora")],
                capture_output=True,
                text=True,
                check=False,
            )
        except FileNotFoundError:
            continue
        segments = output.stdout.split("\x00")
        for i in range(0, len(segments) - 2, 3):
            module_path, line_no, snippet = segments[i], segments[i + 1], segments[i + 2]
            if not module_path or not line_no:
                continue
        try:
            rel = Path(module_path).relative_to(REPO_ROOT)
        except ValueError:
            continue
        cleaned = snippet.splitlines()[0].strip() if snippet else ""
        entries.setdefault(str(rel), []).append(f"{line_no}: {cleaned}")
    if entries:
        for module, hits in entries.items():
            md_lines.append(f"- `{module}`")
            for hit in hits[:3]:
                md_lines.append(f"  - {hit}")
    else:
        md_lines.append("- None detected.")

    md_lines.append("\n## Hidden capabilities referenced in README/PyPI docs")
    hidden_features = [
        ("src/v0min/varshaphal_extract.py", "Annual Varshaphal/Tajaka engine with optional maasa/60-hour charts."),
        ("src/v0min/prasna_extract.py", "Prasna & KP-Adhipathi engine for KP-249/Prasna-108/Naadi-1800 numbers."),
        ("src/v0min/chakra_extract.py", "Multi-layer chakra dashboards (Sarvatobadra, Kaala, Kota, Shoola, Tripataki, etc.)."),
        ("src/v0min/muhurta_extract.py", "Muhurta optimizer that scores windows around activities such as CLASS_START, TRAVEL, and PROJECT_LAUNCH."),
        ("src/v0min/panchanga_extras_extract.py", "Pancha Pakshi + Vratha/festival snapshot generator."),
        ("src/v0min/event_scan_extract.py", "Timeline scanner for sign entries, retrogrades, Sankranti, eclipses, and event filtering."),
    ]
    for module, desc in hidden_features:
        md_lines.append(f"- `{module}` - {desc}")

    md_lines.append("\n## NEWLY DISCOVERED CAPABILITIES")
    new_caps = [
        "`src/v0min/varshaphal_extract.py` - exposes the annual Varshaphal, monthly Maasa Pravesh, and 60-hour Tajaka charts per the README notes and CLI references.",
        "`src/v0min/prasna_extract.py` - generates KP/Prasna/Naadi charts plus KP Adhipathi chains described under the \"Prasna / KP-Adhipathi Engine\" section of README.",
        "`src/v0min/chakra_extract.py` - compiles chakras (Sarvatobadra, Kaala, Kota, Shoola, Tripataki, Surya/Chandra Kalanala, Saptha/Pancha Shalaka) into `chakra.v1` payloads.",
        "`src/v0min/muhurta_extract.py` - scores windows by weights (RahuKalam, Benefic Lagna, etc.) for activities such as `CLASS_START`, matching the README sample.",
        "`src/v0min/panchanga_extras_extract.py` - exports Pancha Pakshi, day schedule, and vratha/festival lists referenced in README under \"Panchanga Extras\".",
        "`src/v0min/event_scan_extract.py` - timelines of sign entries, retrogrades, Sankranti/eclipses, and interpolated events directly mentioned in README.",
    ]
    if new_caps:
        for cap in new_caps:
            md_lines.append(f"- {cap}")
    else:
        md_lines.append("- None.")
    return "\n".join(md_lines)


def build_ui_catalog():
    ui_dir = REPO_ROOT / "src" / "jhora" / "ui"
    lines = ["# UI Modules Catalog", ""]
    lines.append("These modules are presentation-layer widgets/dialogs and should not be treated as core engine APIs.")
    lines.append("")
    for module in sorted(ui_dir.glob("*.py")):
        if module.name.startswith("__"):
            continue
        name = module.stem
        desc = "PyQt6 interface for " + name.replace("_", " ")
        lines.append(f"- `jhora.ui.{name}` - {desc}")
    return "\n".join(lines)


def main():
    primitives = build_core_primitives()
    primitives_path = REPO_ROOT / "pyjhora_knowledge" / "primitives" / "CorePrimitives.json"
    primitives_path.write_text(json.dumps(primitives, indent=2), encoding="utf-8")

    data_map = build_data_map()
    data_map_path = REPO_ROOT / "pyjhora_knowledge" / "data_map" / "PyJHora_Data_Files_Map.json"
    data_map_path.write_text(json.dumps(data_map, indent=2), encoding="utf-8")

    tests_contract = build_tests_contract()
    tests_contract_path = REPO_ROOT / "pyjhora_knowledge" / "tests_contract" / "PyJHora_Tests_Contract.json"
    tests_contract_path.write_text(json.dumps(tests_contract, indent=2), encoding="utf-8")

    experimental_md = build_experimental_md()
    experimental_path = REPO_ROOT / "pyjhora_knowledge" / "experimental" / "Experimental_and_Hidden.md"
    experimental_path.write_text(experimental_md, encoding="utf-8")

    ui_md = build_ui_catalog()
    ui_path = REPO_ROOT / "pyjhora_knowledge" / "ui_catalog" / "UI_Modules.md"
    ui_path.write_text(ui_md, encoding="utf-8")


if __name__ == "__main__":
    main()
