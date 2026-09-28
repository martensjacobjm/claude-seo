"""Guards for the DataForSEO MCP v3 migration (agricidaniel/claude-seo#319).

dataforseo-mcp-server 3.x exposes only `api_request`, `docs_search`,
`docs_index` and `docs_list_sections`; the 2.x per-endpoint tools are gone.
These tests keep every v2 tool name in skills and agents paired with the v3
form, keep the installers on the 3.x major and keep the extension mirror in
sync. Static file checks only, no network access.
"""

import os
import re

import pytest

from conftest import ROOT

CATALOG = os.path.join(ROOT, "skills", "seo-dataforseo", "references", "tool-catalog.md")
SCAN_DIRS = ("skills", "agents", "extensions")
# v2 tool name prefixes (npm dataforseo-mcp-server@2.9.13)
V2_NAME = re.compile(
    r"`((?:serp|kw_data|dataforseo_labs|backlinks|business_data|on_page|"
    r"domain_analytics|content_analysis|merchant|ai_optimization|ai_opt)_[a-z0-9_]+)`"
)


def _catalog_names():
    names = set()
    with open(CATALOG, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("| `"):
                names.update(V2_NAME.findall(line.split("|")[1]))
    return names


def _markdown_files():
    for top in SCAN_DIRS:
        for dirpath, _, files in os.walk(os.path.join(ROOT, top)):
            for name in files:
                if name.endswith(".md"):
                    yield os.path.join(dirpath, name)


def test_catalog_maps_all_v2_tools():
    # 2.9.13 shipped 90 per-endpoint tools; every one needs a v3 path.
    assert len(_catalog_names()) == 90


def test_v2_names_have_v3_form():
    catalog = _catalog_names()
    problems = []
    for path in _markdown_files():
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        used = set(V2_NAME.findall(text))
        if not used:
            continue
        rel = os.path.relpath(path, ROOT)
        if "api_request" not in text:
            problems.append(f"{rel}: v2 tool names without api_request")
        unknown = used - catalog
        if unknown:
            problems.append(f"{rel}: not in tool-catalog.md: {sorted(unknown)}")
    assert not problems, "\n".join(problems)


@pytest.mark.parametrize("name", ["install.sh", "install.ps1"])
def test_installers_pin_v3_major(name):
    with open(os.path.join(ROOT, "extensions", "dataforseo", name), encoding="utf-8") as fh:
        text = fh.read()
    assert re.search(r"""DFSE_?PACKAGE\s*=\s*["']dataforseo-mcp-server@3["']""", text, re.I)
    # npx must never run the bare (unpinned) package name
    assert not re.search(r"npx[^\n]*dataforseo-mcp-server(?!@3)", text)


@pytest.mark.parametrize("rel", [
    "skills/seo-dataforseo/SKILL.md",
    "skills/seo-dataforseo/references/tool-catalog.md",
])
def test_extension_skill_mirror_in_sync(rel):
    ext = os.path.join(ROOT, "extensions", "dataforseo", rel)
    with open(os.path.join(ROOT, rel), encoding="utf-8") as a, open(ext, encoding="utf-8") as b:
        assert a.read() == b.read()


def test_extension_agent_mirror_in_sync():
    with open(os.path.join(ROOT, "agents", "seo-dataforseo.md"), encoding="utf-8") as a, \
            open(os.path.join(ROOT, "extensions", "dataforseo", "agents", "seo-dataforseo.md"),
                 encoding="utf-8") as b:
        assert a.read() == b.read()
