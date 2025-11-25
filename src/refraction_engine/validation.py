"""
Input Validation
Validates payloads against JSON schemas.
"""

from pathlib import Path
from typing import Any, Dict, List

import jsonschema


def validate_input(payload: Dict[str, Any], schema_name: str) -> List[str]:
    """
    Validate payload against JSON schema.

    Returns:
        List of errors (empty if valid)
    """
    import json

    schema_path = (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "specs"
        / f"{schema_name}.schema.json"
    )

    if not schema_path.exists():
        return [f"Schema not found: {schema_name}"]

    with schema_path.open("r", encoding="utf-8") as f:
        schema = json.load(f)

    errors: List[str] = []
    try:
        jsonschema.validate(instance=payload, schema=schema)
    except jsonschema.ValidationError as e:
        errors.append(str(e))

    return errors
