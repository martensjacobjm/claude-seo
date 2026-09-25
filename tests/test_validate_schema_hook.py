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
