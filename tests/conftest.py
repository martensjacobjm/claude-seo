"""Shared pytest setup: make scripts/ and hooks/ importable."""

import importlib.util
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURES = os.path.join(ROOT, "tests", "fixtures")
sys.path.insert(0, os.path.join(ROOT, "scripts"))


def load_hook():
    """Import hooks/validate-schema.py (hyphenated file name) as a module."""
    path = os.path.join(ROOT, "hooks", "validate-schema.py")
    spec = importlib.util.spec_from_file_location("validate_schema", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
