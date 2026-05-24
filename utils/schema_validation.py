"""Schema validation helpers using jsonschema.

Provides lightweight validation utilities and example schema-loading functions.
"""
from pathlib import Path
from typing import Any, Dict
import json
import jsonschema

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schemas"


def load_schema(name: str) -> Dict[str, Any]:
    """Load a JSON schema from the `schemas/` directory.

    Args:
        name: file name (e.g., 'faq_schema.json')

    Returns:
        Parsed schema dict.
    """
    path = SCHEMA_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Schema {name} not found at {path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def validate_json(instance: Dict[str, Any], schema_name: str) -> None:
    """Validate an instance against the named schema.

    Raises `jsonschema.ValidationError` on failure.
    """
    schema = load_schema(schema_name)
    jsonschema.validate(instance=instance, schema=schema)


def is_valid(instance: Dict[str, Any], schema_name: str) -> bool:
    try:
        validate_json(instance, schema_name)
        return True
    except jsonschema.ValidationError:
        return False


__all__ = ["load_schema", "validate_json", "is_valid"]
