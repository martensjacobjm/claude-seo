"""Tests for the PostToolUse schema validation hook."""

import json
import os
import subprocess
import sys

from conftest import FIXTURES, ROOT, load_hook

HOOK = os.path.join(ROOT, "hooks", "validate-schema.py")
SCHEMA = os.path.join(FIXTURES, "schema")


def _run(stdin_payload=None, args=()):
    return subprocess.run([sys.executable, HOOK, *args], input=stdin_payload,
                          capture_output=True, text=True, timeout=30)


def test_deprecated_type_and_placeholder_block_via_hook_stdin():
    payload = json.dumps({"tool_input": {"file_path": os.path.join(SCHEMA, "deprecated-howto.html")}})
    proc = _run(payload)
    assert proc.returncode == 2
    assert "HowTo" in proc.stderr and "[Your Company]" in proc.stderr


def test_valid_article_passes_with_json_output():
    proc = _run(args=(os.path.join(SCHEMA, "valid-article.html"), "--json"))
    assert proc.returncode == 0
    assert json.loads(proc.stdout)["status"] == "pass"


def test_nested_types_are_found():
    hook = load_hook()
    content = open(os.path.join(SCHEMA, "deprecated-howto.html"), encoding="utf-8").read()
    messages = " ".join(str(f) for f in hook.validate_jsonld(content))
    assert "HowTo" in messages


def test_dummy_data_is_a_warning_not_a_block():
    proc = _run(args=(os.path.join(SCHEMA, "dummy-localbusiness.html"), "--json"))
    out = json.loads(proc.stdout)
    assert proc.returncode == 1
    warnings = " ".join(out["warnings"])
    assert "0000000" in warnings and "Exempelvägen" in warnings
    assert out["errors"] == []


def test_swedish_placeholders_block():
    proc = _run(args=(os.path.join(SCHEMA, "swedish-placeholders.html"), "--json"))
    out = json.loads(proc.stdout)
    assert proc.returncode == 2
    errors = " ".join(out["errors"])
    assert "[FÖRETAGSNAMN]" in errors and "[Telefon]" in errors and "[Ditt område]" in errors
    assert "[1]" not in errors
