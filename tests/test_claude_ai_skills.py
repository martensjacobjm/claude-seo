"""Tests for claude-ai-skills/build.py and the packaged claude.ai skills."""

import json
import os
import re
import subprocess
import sys
import zipfile

from conftest import ROOT

BUILD = os.path.join(ROOT, "claude-ai-skills", "build.py")
SRC = os.path.join(ROOT, "claude-ai-skills")

HEMSIDA_COPIES = {
    "references/geo-evidence.md": "skills/seo-geo/references/geo-evidence.md",
    "references/geo-examples.md": "skills/seo-geo/references/geo-examples.md",
    "references/ranking-signals.md": "skills/seo/references/ranking-signals.md",
    "references/schema-types.md": "skills/seo/references/schema-types.md",
    "references/cwv-thresholds.md": "skills/seo/references/cwv-thresholds.md",
    "references/local-schema-types.md": "skills/seo/references/local-schema-types.md",
    "references/eeat-framework.md": "skills/seo/references/eeat-framework.md",
    "references/local-eeat-evidence.md": "skills/seo/references/local-eeat-evidence.md",
    "scripts/validate_schema.py": "hooks/validate-schema.py",
}


def _build(*args):
    proc = subprocess.run([sys.executable, BUILD, *args], capture_output=True, text=True, timeout=120)
    return proc.returncode, json.loads(proc.stdout)


def _frontmatter(text):
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    assert match, "SKILL.md must start with YAML frontmatter"
    keys = dict(re.findall(r"^([a-z-]+):\s*(.*)$", match.group(1), re.MULTILINE))
    return keys


def test_hemsida_package_contents(tmp_path):
    code, report = _build("--only", "hemsida", "--out", str(tmp_path))
    assert code == 0, report
    item = report["skills"][0]
    assert item["status"] == "pass" and not item["errors"]
    package = tmp_path / "hemsida.skill"
    assert package.is_file()
    with zipfile.ZipFile(package) as zf:
        names = zf.namelist()
        assert names == sorted(names)
        assert all(n.startswith("hemsida/") for n in names)
        skill_md = zf.read("hemsida/SKILL.md").decode("utf-8")
        fm = _frontmatter(skill_md)
        assert fm["name"] == "hemsida"
        desc = fm["description"]
        assert 0 < len(desc) <= 1024 and "<" not in desc and ">" not in desc
        for word in ("hemsida", "webbplats", "sökoptimering", "Google Business Profile", "website audit"):
            assert word in desc
        assert set(fm) <= {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}
        assert len(skill_md.splitlines()) < 500
        # Copied references are byte-identical to the canonical repo files.
        for dest, source in HEMSIDA_COPIES.items():
            with open(os.path.join(ROOT, source), "rb") as fh:
                assert zf.read(f"hemsida/{dest}") == fh.read(), dest
            assert f"`{dest}`" in skill_md or dest.startswith("scripts/"), f"{dest} not referenced"
        assert "hemsida/references/rapportmall.md" in names
        assert sum(1 for n in names if n.endswith("/SKILL.md")) == 1


def test_canonical_copies_are_not_duplicated_in_source():
    for dest in HEMSIDA_COPIES:
        assert not os.path.exists(os.path.join(SRC, "hemsida", dest)), dest


def test_line_limits_for_authored_files():
    for dirpath, _dirs, files in os.walk(SRC):
        if os.sep + "dist" in dirpath or "__pycache__" in dirpath:
            continue
        for fn in files:
            path = os.path.join(dirpath, fn)
            lines = len(open(path, encoding="utf-8").read().splitlines())
            if fn == "SKILL.md":
                assert lines < 500, path
            elif (os.path.basename(dirpath) == "references" and fn.endswith(".md")
                  and os.path.join(SRC, "hemsida") in dirpath):
                assert lines < 200, path


def test_swedish_writing_rules():
    for rel in ("hemsida/SKILL.md", "hemsida/references/rapportmall.md", "README.md"):
        text = open(os.path.join(SRC, rel), encoding="utf-8").read()
        assert "—" not in text, f"em dash in {rel}"
        assert " – " not in text, f"en dash as punctuation in {rel}"
        assert not re.search(r"handlar inte om .{1,80} utan om", text), rel


def test_build_is_deterministic(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    _build("--only", "hemsida", "--out", str(a))
    _build("--only", "hemsida", "--out", str(b))
    assert (a / "hemsida.skill").read_bytes() == (b / "hemsida.skill").read_bytes()


def test_committed_hemsida_package_is_current():
    code, report = _build("--only", "hemsida", "--check")
    assert code == 0, f"run: python3 claude-ai-skills/build.py  ({report.get('stale')})"


def test_extra_skill_folders_are_packaged_and_validated(tmp_path):
    src = tmp_path / "src"
    good = src / "skill-evidens"
    good.mkdir(parents=True)
    (good / "SKILL.md").write_text("---\nname: skill-evidens\ndescription: Test skill.\n---\n\n# Test\n")
    bad = src / "trasig"
    bad.mkdir()
    (bad / "SKILL.md").write_text("---\nname: trasig\ndescription: Trigga: på engelska\n---\n")
    (src / "tom").mkdir()
    code, report = _build("--src", str(src), "--out", str(tmp_path / "out"))
    by_name = {i["name"]: i for i in report["skills"]}
    assert by_name["skill-evidens"]["status"] == "pass"
    assert (tmp_path / "out" / "skill-evidens.skill").is_file()
    assert by_name["trasig"]["status"] == "fail"
    assert by_name["tom"]["status"] == "skipped"
    assert code == 1


def test_bundled_validator_runs_standalone(tmp_path):
    _build("--only", "hemsida", "--out", str(tmp_path))
    with zipfile.ZipFile(tmp_path / "hemsida.skill") as zf:
        zf.extractall(tmp_path / "x")
    page = tmp_path / "sida.html"
    page.write_text('<script type="application/ld+json">{"@context":"https://schema.org",'
                    '"@type":"HowTo","name":"x"}</script>')
    proc = subprocess.run([sys.executable, str(tmp_path / "x" / "hemsida" / "scripts" / "validate_schema.py"),
                           str(page), "--json"], capture_output=True, text=True, timeout=30)
    assert proc.returncode == 2
    assert json.loads(proc.stdout)["status"] == "block"
