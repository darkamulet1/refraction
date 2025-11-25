from pathlib import Path
import importlib
import ast
from .model import CorePrimitives
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple, Union


def _parse_lang_list(path: Path) -> Dict[str, List[str]]:
    if not path.exists():
        return {}
    data: Dict[str, List[str]] = {}
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return data
    for raw in text.splitlines():
        raw = raw.strip()
        if not raw or raw.startswith("#") or "=" not in raw:
            continue
        key, value = raw.split("=", 1)
        values = [item.strip() for item in value.split(",") if item.strip()]
        data[key.strip().upper()] = values
    return data


def _build_named_rows(values: Iterable[Any], prefix: str = "") -> List[Dict[str, Any]]:
    rows = []
    for value in values:
        rows.append({"name": f"{prefix}{value}", "label": str(value)})
    return rows


def _find_package_dir(pyjhora_root: Path) -> Optional[Path]:
    candidates = [pyjhora_root / "jhora", pyjhora_root / "src" / "jhora"]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def _load_const_module(pyjhora_root: Path):
    try:
        return importlib.import_module("jhora.const")
    except Exception:
        return None


def _collect_ast_assignments(const_path: Path) -> list[Tuple[str, Any]]:
    try:
        src = const_path.read_text(encoding="utf-8")
        tree = ast.parse(src)
    except Exception:
        return []
    assignments: list[Tuple[str, Any]] = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    value = None
                    try:
                        value = ast.literal_eval(node.value)
                    except Exception:
                        value = _value_from_ast(node.value)
                    assignments.append((target.id, value))
    return assignments


def _value_from_ast(node: ast.AST):
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Str):
        return node.s
    if isinstance(node, ast.Num):
        return node.n
    if isinstance(node, ast.Tuple):
        return tuple(_value_from_ast(elt) for elt in node.elts)
    if isinstance(node, ast.List):
        return [_value_from_ast(elt) for elt in node.elts]
    if isinstance(node, ast.Dict):
        result = {}
        for key_node, val_node in zip(node.keys, node.values):
            key = _value_from_ast(key_node)
            val = _value_from_ast(val_node)
            if key is not None:
                result[key] = val
        return result
    if isinstance(node, ast.Attribute):
        return f"{_value_from_ast(node.value)}.{node.attr}" if hasattr(node, "attr") else None
    if isinstance(node, ast.Name):
        return node.id
    return None

def _normalize_name(text: str) -> str:
    return " ".join(word.capitalize() for word in text.replace("_", " ").split())


def extract_ayanamsa_modes(const_module, const_path: Path, assignments: Sequence[Tuple[str, Any]]) -> List[Dict[str, Any]]:
    entries: dict = {}
    assign_map = {name: value for name, value in assignments}
    if const_module and hasattr(const_module, "available_ayanamsa_modes"):
        entries = getattr(const_module, "available_ayanamsa_modes") or {}
    else:
        entries = assign_map.get("available_ayanamsa_modes") or {}
        if not entries:
            for name, value in assign_map.items():
                if "AYAN" in name.upper() and isinstance(value, dict):
                    entries = value
                    break
    ordered = []
    def _ayan_sort_key(item):
        key, value = item
        if isinstance(value, (int, float)):
            return (0, value, str(key))
        return (1, str(value), str(key))
    items = sorted(entries.items(), key=_ayan_sort_key)
    for idx, (key, value) in enumerate(items):
        entry_id = value if isinstance(value, (int, float)) else idx
        ordered.append(
            {
                "id": entry_id,
                "name": _normalize_name(str(key)),
                "internal_constant": str(key),
                "value": value,
            }
        )
    return ordered


def extract_house_systems(const_module, const_path: Path, assignments: Sequence[Tuple[str, Any]]) -> List[Dict[str, Any]]:
    entries: dict = {}
    assign_map = {name: value for name, value in assignments}
    if const_module and hasattr(const_module, "available_house_systems"):
        entries = getattr(const_module, "available_house_systems") or {}
    else:
        entries = assign_map.get("available_house_systems") or {}
        if not entries:
            for fallback in ("indian_house_systems", "western_house_systems"):
                part = assign_map.get(fallback)
                if isinstance(part, dict):
                    entries.update(part)
    systems: List[Dict[str, Any]] = []
    for key, value in entries.items():
        tradition = "Unknown"
        if isinstance(key, int):
            tradition = "Indian"
        else:
            text = str(value).lower()
            if any(term in text for term in ("equal", "sripati", "kp", "varnada", "lagna", "bhaava", "indian")):
                tradition = "Indian"
            elif any(term in text for term in ("placidus", "koch", "porphyrius", "regiomontanus", "campanus", "vehlow", "alca", "morinus", "azimuthal", "topocentric")):
                tradition = "Western"
        systems.append(
            {
                "id": str(key),
                "name": str(value),
                "internal_constant": str(key),
                "tradition": tradition,
            }
        )
    return systems


def _determine_default_house_system(const_module) -> Optional[Union[int, str]]:
    for attr in ("_DEFAULT_HOUSE_SYSTEM", "_DEFAULT_BHAAVA_METHOD", "bhaava_madhya_method"):
        if const_module and hasattr(const_module, attr):
            return getattr(const_module, attr)
    return None

def parse_const(pyjhora_root: Path) -> (CorePrimitives, dict):
    cp = CorePrimitives()
    defaults: Dict[str, Any] = {}
    package_dir = _find_package_dir(pyjhora_root)
    const_path = package_dir / "const.py" if package_dir else pyjhora_root / "jhora" / "const.py"
    lang_path = package_dir / "lang" / "list_values_en.txt" if package_dir else pyjhora_root / "jhora" / "lang" / "list_values_en.txt"
    assignments = _collect_ast_assignments(const_path)
    const_module = _load_const_module(pyjhora_root) if const_path.exists() else None
    if const_path.exists():
        if const_module:
            const = const_module
            if hasattr(const, "_DEFAULT_AYANAMSA_MODE"):
                defaults["ayanamsa_mode"] = getattr(const, "_DEFAULT_AYANAMSA_MODE")
            if hasattr(const, "_DEFAULT_LANGUAGE"):
                defaults["language"] = getattr(const, "_DEFAULT_LANGUAGE")
            if hasattr(const, "division_chart_factors"):
                cp.vargas = [
                    {
                        "id": f"D{int(factor)}",
                        "name": f"Divisional chart D{int(factor)}",
                        "divisor": factor,
                        "implemented": True,
                    }
                    for factor in getattr(const, "division_chart_factors", [])
                ]
            if hasattr(const, "division_chart_factors"):
                defaults["division_chart_factors"] = getattr(const, "division_chart_factors")
            if hasattr(const, "bhaava_madhya_method"):
                defaults["default_bhaava_method"] = getattr(const, "bhaava_madhya_method")
        cp.ayanamsa = extract_ayanamsa_modes(const_module, const_path, assignments)
        cp.house_systems = extract_house_systems(const_module, const_path, assignments)
        default_house = _determine_default_house_system(const_module)
        if default_house is not None:
            defaults["default_house_system"] = default_house
    if not cp.rasis or not cp.planets:
        for name, val in assignments:
            if isinstance(val, (list, tuple)):
                if name.upper().startswith("RASI") or name.upper().endswith("RASIS"):
                    cp.rasis = [dict(name=str(x)) for x in val]
                if name.upper().startswith("PLANET") or name.upper().endswith("PLANETS"):
                    cp.planets = [dict(name=str(x)) for x in val]
    # language-based fallbacks
    lang_values = _parse_lang_list(lang_path)
    if lang_values:
        if not cp.planets and "PLANET_NAMES" in lang_values:
            cp.planets = [{"name": name} for name in lang_values["PLANET_NAMES"]]
        if not cp.rasis and "RAASI_LIST" in lang_values:
            cp.rasis = [{"name": name} for name in lang_values["RAASI_LIST"]]
        if not cp.ayanamsa and "AYANAMSA_LIST" in lang_values:
            cp.ayanamsa = [{"name": name} for name in lang_values["AYANAMSA_LIST"]]

    return cp, defaults
