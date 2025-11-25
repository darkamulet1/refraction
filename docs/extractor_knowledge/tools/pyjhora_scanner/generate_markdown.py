from .model import ScanResult
from typing import List, Dict, Iterable, Tuple, Optional
from datetime import datetime

try:
    from jhora import const as _jhora_const
except Exception:
    _jhora_const = None


def _safe(value: Optional[str]) -> str:
    return "<<MISSING>>" if value is None else str(value)


def _snippet(text: Optional[str]) -> str:
    if not text:
        return ""
    return text.strip().split("\n", 1)[0]


def _build_tree(names: Iterable[str]) -> Dict[str, dict]:
    tree: Dict[str, dict] = {}
    for name in sorted(names):
        parts = name.split(".")
        current = tree
        for part in parts:
            current = current.setdefault(part, {})
    return tree


def _render_tree(lines: List[str], name: str, subtree: dict, indent: str = "") -> None:
    lines.append(f"{indent}- `{name}`")
    for child in sorted(subtree.keys()):
        _render_tree(lines, child, subtree[child], indent + "  ")


def _function_table(
    funcs: List, include_private: bool = False, limit: int = 999
) -> List[str]:
    filtered = [f for f in funcs if include_private or f.is_public]
    if not filtered:
        return []
    lines = ["| Function | Signature | Doc |", "|---|---|---|"]
    for f in filtered[:limit]:
        lines.append(f"| `{f.name}` | `{f.signature}` | {_snippet(f.docstring)} |")
    return lines


def _group_functions(
    funcs: List, categories: List[Tuple[str, str, List[str]]]
) -> List[Tuple[str, str, List]]:
    remaining = list(funcs)
    grouped: List[Tuple[str, str, List]] = []
    for title, description, keywords in categories:
        matched = []
        for func in list(remaining):
            haystack = f"{func.name} {func.docstring or ''}".lower()
            if any(keyword in haystack for keyword in keywords):
                matched.append(func)
                remaining.remove(func)
        if matched:
            grouped.append((title, description, matched))
    if remaining:
        grouped.append(
            (
                "Additional helpers",
                "Other public utilities surfaced by the module.",
                remaining,
            )
        )
    return grouped


def _describe_modules(names: Iterable[str]) -> str:
    names = sorted(names)
    return ", ".join(names) if names else "None discovered."


def generate_markdown(scan: ScanResult) -> str:
    lines: List[str] = []
    lines.append("# PyJHora Structural Map for Extractor Design")
    lines.append("")
    lines.append("## 1. Meta & Overview")
    lines.append("")
    lines.append(f"- **Version**: {_safe(scan.version)}")
    lines.append("- **Engine scope**: Panchanga core, divisional charts, dashas, strengths, yogas, match, transit, prediction, UI helpers")
    lines.append(f"- **Default ayanamsa**: {_safe(scan.defaults.get('ayanamsa_mode'))}")
    lines.append("- **Safe entry points**: see section 16")
    lines.append("")

    lines.append("---")
    lines.append("## 2. Package Structure Tree")
    lines.append("")
    package_tree = _build_tree(scan.package_tree.keys())
    if "jhora" in package_tree:
        _render_tree(lines, "jhora", package_tree["jhora"])
    else:
        lines.append("<<Unable to discover package tree>>")
    lines.append("")

    lines.append("---")
    lines.append("## 3. Core Primitives & Defaults")
    lines.append("")
    if scan.core_primitives.planets:
        lines.append("### Planets")
        lines.append("| Index | Name |")
        lines.append("|---:|---|")
        for idx, planet in enumerate(scan.core_primitives.planets):
            lines.append(f"| {idx} | {planet.get('name')} |")
    else:
        lines.append("- Planets: <<Not captured>>")
    lines.append("")
    if scan.core_primitives.rasis:
        lines.append("### Rasis (Signs)")
        lines.append("| Index | Name |")
        lines.append("|---:|---|")
        for idx, rasi in enumerate(scan.core_primitives.rasis, 1):
            lines.append(f"| {idx} | {rasi.get('name')} |")
    else:
        lines.append("- Rasis: <<Not captured>>")
    lines.append("")
    if scan.core_primitives.vargas:
        lines.append("### Varga options")
        lines.append("| ID | Description | Divisor | Implemented |")
        lines.append("|---|---|---:|---|")
        for entry in scan.core_primitives.vargas:
            lines.append(
                f"| {entry.get('id')} | {entry.get('name')} | {entry.get('divisor')} | {entry.get('implemented')} |"
            )
    else:
        lines.append("- Varga list: <<Not discovered automatically>>")
    lines.append("")
    if scan.core_primitives.ayanamsa:
        lines.append("### Ayanamsa modes")
        lines.append("| Index | Name | Value |")
        lines.append("|---:|---|---|")
        for idx, mode in enumerate(scan.core_primitives.ayanamsa):
            lines.append(f"| {idx} | {mode.get('name')} | {mode.get('value','')} |")
    else:
        lines.append("- Ayanamsa modes: <<Not discovered>>")
    lines.append("")
    if scan.core_primitives.house_systems:
        lines.append("### House systems")
        lines.append("| ID | Name | Tradition |")
        lines.append("|---|---|---|")
        for hs in scan.core_primitives.house_systems:
            lines.append(f"| {hs.get('id')} | {hs.get('name')} | {hs.get('tradition')} |")
    else:
        lines.append("- House systems: <<Not discovered>>")
    lines.append("")
    lines.append("Place structure used across modules:")
    lines.append("```py")
    lines.append("Place(name: str, latitude: float, longitude: float, timezone: float, elevation: float = None)")
    lines.append("```")
    lines.append("")

    lines.append("---")
    lines.append("## 4. Panchanga Engine")
    lines.append("")
    panchanga_modules = [name for name in scan.package_tree if name.startswith("jhora.panchanga")]
    lines.append(f"- **Modules**: {_describe_modules(panchanga_modules)}")
    drik = scan.package_tree.get("jhora.panchanga.drik")
    if drik:
        lines.append("- **Default ayanamsa binding**: uses `_DEFAULT_AYANAMSA_MODE` and exposes `set_ayanamsa_mode` for runtime adjustments.")
        lines.append("- Functions cover sunrise/sunset, lunar/tamil months, samvatsara, tithi/nakshatra/yoga/karana, special lagnas, upagrahas, event scanning, festival/vratha lists, conjunction/transit helpers.")
        categories = [
            (
                "Planetary & positional data",
                "Longitude, speed, ascendant, declination, retrograde timings.",
                ["planet", "graha", "longitude", "ascendant", "speed", "retrograde", "declination"],
            ),
            (
                "Tithi/Nakshatra/Yoga basics",
                "Core panchanga essentials and paksha/vaara markers.",
                ["tithi", "nakshatra", "yoga", "karana", "vaara", "paksha"],
            ),
            (
                "Calendar/season helpers",
                "Lunar/tamil month math, ritus, samvatsara, vedic dates, festival search.",
                ["lunar_month", "tamil", "ritu", "samvatsara", "vedic", "panchaka", "mahalaya"],
            ),
            (
                "Special lagnas & upagrahas",
                "Bhrigu bindu, vighati/pranapada, indu, maandi, shiva vaasa, upagraha longitudes.",
                ["lagna", "upagraha", "bhrigu", "panchaka", "shiva", "guli", "maandi", "indu"],
            ),
            (
                "Event & transit search",
                "Sankranti, conjunctions, planet entries, eclipses, sankatahara.",
                ["sankranti", "conjunction", "eclipse", "transit", "entry", "next_", "previous_", "graha_drek"],
            ),
            (
                "Festivals & vrathas",
                "Aggregators for pradosham, amavasya, ekadashi, manvaadhi, ashtaka, srartha, chandradharshan.",
                ["festival", "vratha", "special_vratha", "pradosham", "srartha", "chandra", "mahalaya"],
            ),
        ]
        grouped = _group_functions(drik.functions, categories)
        for title, description, functions in grouped:
            lines.append(f"### {title}")
            lines.append(description)
            table = _function_table(functions)
            if table:
                lines.extend(table)
            else:
                lines.append("_No public functions tagged for this category._")
            lines.append("")
    else:
        lines.append("- `jhora.panchanga.drik` not imported.")
    lines.append("")
    vratha = scan.package_tree.get("jhora.panchanga.vratha")
    lines.append("### `jhora.panchanga.vratha` overview")
    if vratha:
        lines.append("- Handles pradosham, sankranti, amavasya/pournami, ekadashi, srartha, sankatahara, shivarathri, moondraam pirai, festivals, festivals CSV based lookups.")
        table = _function_table(vratha.functions)
        if table:
            lines.extend(table)
        else:
            lines.append("_No public functions detected._")
    else:
        lines.append("- Vratha module missing.")
    lines.append("")

    lines.append("---")
    lines.append("## 5. Chart Modules & Strengths")
    lines.append("")
    chart_modules = [name for name in scan.package_tree if ".horoscope.chart" in name]
    lines.append(f"- **Chart modules discovered**: {_describe_modules(chart_modules)}")
    key_modules = [
        "jhora.horoscope.chart.charts",
        "jhora.horoscope.chart.house",
        "jhora.horoscope.chart.ashtakavarga",
        "jhora.horoscope.chart.dosha",
        "jhora.horoscope.chart.raja_yoga",
        "jhora.horoscope.chart.sphuta",
        "jhora.horoscope.chart.arudhas",
    ]
    for module_name in key_modules:
        mod = scan.package_tree.get(module_name)
        if not mod:
            continue
        lines.append(f"### `{module_name}`")
        lines.append(f"- {_snippet(mod.docstring) or 'No module docstring captured.'}")
        table = _function_table(mod.functions, limit=8)
        if table:
            lines.extend(table)
        else:
            lines.append("_No public functions discovered._")
        lines.append("")

    strength_mod = scan.package_tree.get("jhora.horoscope.chart.strength")
    lines.append("---")
    lines.append("## 6. Strength Calculations (`strength.py`)")
    lines.append("")
    if strength_mod:
        targeted = [
            "harsha_bala",
            "_kshetra_bala",
            "_sthana_bala",
            "_sapthavargaja_bala",
            "pancha_vargeeya_bala",
            "dwadhasa_vargeeya_bala",
            "_dig_bala",
            "_divaratri_bala",
            "_paksha_bala",
            "_cheshta_bala",
            "_naisargika_bala",
            "_drik_bala",
            "shad_bala",
            "bhava_bala",
        ]
        functions = [f for f in strength_mod.functions if f.name in targeted]
        if functions:
            lines.append("- Harsha, Kshetra, Sapthavargaja, Sthana, OjhaYugma, Kendra, Drekkana, Navamsa, Pancha/Dwadasha Vargeeya, Dig, Divaratri, Paksha, Cheshta, Naisargika, Drik, Shad, Bhava balas are available.")
            lines.extend(_function_table(functions, include_private=True))
        else:
            lines.append("- Specific bala helpers not tagged (module scanned but mapping missing).")
    else:
        lines.append("- Strength module not imported.")
    lines.append("")

    lines.append("---")
    lines.append("## 7. Yoga Detection")
    lines.append("")
    yoga_mod = scan.package_tree.get("jhora.horoscope.chart.yoga")
    if yoga_mod:
        lines.append("- Yoga definitions loaded via `jhora/lang/yoga_msgs_<lang>.json` and consumed by `get_yoga_details`/`get_yoga_details_for_all_charts`.")
        table = _function_table([f for f in yoga_mod.functions if f.is_public])
        if table:
            lines.extend(table)
        else:
            lines.append("_No public yoga functions captured._")
    else:
        lines.append("- Yoga module not imported.")
    lines.append("")

    lines.append("---")
    lines.append("## 8. Dasha Systems")
    lines.append("")
    graha = sorted(name for name in scan.dasha_modules if ".graha." in name)
    raasi = sorted(name for name in scan.dasha_modules if ".raasi." in name)
    annual = sorted(name for name in scan.dasha_modules if ".annual." in name)
    lines.append(f"- **Graha dashas**: {_describe_modules(graha)}")
    lines.append(f"- **Rasi dashas**: {_describe_modules(raasi)}")
    lines.append(f"- **Annual/Sudharshana**: {_describe_modules(annual)}")
    lines.append("")
    for heading, modules in [
        ("Graha dashas", graha),
        ("Rasi dashas", raasi),
        ("Annual dashas", annual),
    ]:
        if not modules:
            continue
        lines.append(f"### {heading}")
        for module_name in modules[:6]:
            mod = scan.package_tree.get(module_name)
            if not mod:
                continue
            lines.append(f"- `{module_name}` – {_snippet(mod.docstring)}")
            table = _function_table(mod.functions, limit=4)
            if table:
                lines.extend(table)
        lines.append("")

    lines.append("---")
    lines.append("## 9. Transit, Tajaka & Saham")
    lines.append("")
    transit_modules = sorted(scan.transit_modules.keys())
    lines.append(f"- Modules: {_describe_modules(transit_modules)}")
    if _jhora_const and hasattr(_jhora_const, "_saham_list"):
        sahams = getattr(_jhora_const, "_saham_list")
        lines.append(f"- Saham catalog: {len(sahams)} points (e.g., {', '.join(sahams[:5])} ...)")
    lines.append("")
    for module_name in transit_modules:
        mod = scan.package_tree.get(module_name)
        if not mod:
            continue
        lines.append(f"### `{module_name}`")
        lines.append(f"- {_snippet(mod.docstring)}")
        lines.extend(_function_table(mod.functions, limit=6))
        lines.append("")

    lines.append("---")
    lines.append("## 10. Match & Prediction")
    lines.append("")
    match_modules = sorted(scan.match_modules.keys())
    pred_modules = sorted(scan.prediction_modules.keys())
    lines.append(f"- Match modules: {_describe_modules(match_modules)}")
    lines.append(f"- Prediction modules: {_describe_modules(pred_modules)}")
    lines.append("")
    for module_name in match_modules + pred_modules:
        mod = scan.package_tree.get(module_name)
        if not mod:
            continue
        lines.append(f"### `{module_name}`")
        lines.append(f"- {_snippet(mod.docstring)}")
        lines.extend(_function_table(mod.functions, limit=5))
        lines.append("")

    lines.append("---")
    lines.append("## 11. UI Modules (Presentation layer)")
    lines.append("")
    ui_modules = sorted(name for name in scan.package_tree if name.startswith("jhora.ui"))
    if ui_modules:
        lines.append("- UI widgets aim to display panchanga, chart, calendar, match, vratha, dasha, and transit data.")
        for module_name in ui_modules:
            lines.append(f"- `{module_name}`")
    else:
        lines.append("- No UI modules discovered.")
    lines.append("")

    lines.append("---")
    lines.append("## 12. Data Files (`jhora/data/`)")
    lines.append("")
    if scan.data_files:
        lines.append("| File | Purpose | Consumers |")
        lines.append("|---|---|---|")
        for entry in scan.data_files[:20]:
            lines.append(f"| {entry.get('path')} | {entry.get('purpose','')} | {entry.get('consumers','')} |")
    else:
        lines.append("- No data files indexed.")
    lines.append("")

    lines.append("---")
    lines.append("## 13. Tests as Contract (`jhora/tests/`)")
    lines.append("")
    if scan.tests:
        lines.append("| File | Test | Description |")
        lines.append("|---|---|---|")
        for test in scan.tests[:10]:
            lines.append(f"| {test.file} | {test.test_name} | {_snippet(test.description)} |")
    else:
        lines.append("- No tests captured.")
    lines.append("")

    lines.append("---")
    lines.append("## 14. Experimental & Unstable Features")
    lines.append("")
    if scan.experimental_modules:
        lines.append("| Module | Flags | Notes |")
        lines.append("|---|---|---|")
        for module_name in scan.experimental_modules:
            mod = scan.package_tree.get(module_name)
            lines.append(f"| `{module_name}` | experimental | {_snippet(mod.docstring) or 'Marked via keyword scan.'} |")
    else:
        lines.append("- No experimental markers detected.")
    lines.append("")

    lines.append("---")
    lines.append("## 15. Global Defaults & Configuration")
    lines.append("")
    if scan.defaults:
        lines.append("| Key | Value |")
        lines.append("|---|---|")
        for key, value in scan.defaults.items():
            lines.append(f"| {key} | {value} |")
    else:
        lines.append("- No defaults recorded.")
    lines.append("")

    lines.append("---")
    lines.append("## 16. Extractor Design & Safe Entry Points")
    lines.append("")
    if scan.safe_entry_points:
        lines.append("| Entry | Reason |")
        lines.append("|---|---|")
        for entry in scan.safe_entry_points[:20]:
            lines.append(f"| `{entry}` | Public non-experimental function |")
    else:
        lines.append("- No safe entry points captured.")
    lines.append("")

    lines.append(f"_Document generated: {datetime.utcnow().isoformat()}Z_")
    return "\n".join(lines)
