#!/usr/bin/env python3
"""Build uploadable claude.ai skill packages (.skill) from claude-ai-skills/.

Every sub-folder of claude-ai-skills/ that holds a SKILL.md is packaged as
dist/<name>.skill: a zip with the skill folder at the archive root, the layout
skill-creator's package_skill.py produces and claude.ai expects on upload.

Some skills pull canonical files from the repo at build time (single source of
truth). They are listed in CANONICAL_COPIES and copied into a staging folder,
never into the source folder, so the repo keeps exactly one copy of each.

Packages are deterministic: entries are sorted, timestamps and permissions are
fixed, so rebuilding unchanged sources gives byte-identical files.

Each staged skill is validated with skill-creator's quick_validate.py when it
can be imported (needs PyYAML), and always with the built-in frontmatter and
line-limit checks below.

Usage:
    python3 claude-ai-skills/build.py                 # build into claude-ai-skills/dist
    python3 claude-ai-skills/build.py --out /tmp/x    # build elsewhere
    python3 claude-ai-skills/build.py --check         # fail if dist/ is stale
    python3 claude-ai-skills/build.py --only hemsida
    python3 claude-ai-skills/build.py --src other/folder --out /tmp/x

Output: JSON on stdout. Exit code 0 on success, 1 on validation failure or a
stale dist/ (--check), 2 on usage errors.
"""

import argparse
import hashlib
import io
import json
import os
import re
import shutil
import sys
import tempfile
import zipfile
from typing import Dict, List, Optional, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DEFAULT_OUT = os.path.join(HERE, "dist")

# Canonical repo files copied into a skill at build time: {skill: {dest: repo source}}.
CANONICAL_COPIES: Dict[str, Dict[str, str]] = {
    "hemsida": {
        "references/geo-evidence.md": "skills/seo-geo/references/geo-evidence.md",
        "references/geo-examples.md": "skills/seo-geo/references/geo-examples.md",
        "references/ranking-signals.md": "skills/seo/references/ranking-signals.md",
        "references/schema-types.md": "skills/seo/references/schema-types.md",
        "references/cwv-thresholds.md": "skills/seo/references/cwv-thresholds.md",
        "references/local-schema-types.md": "skills/seo/references/local-schema-types.md",
        "references/eeat-framework.md": "skills/seo/references/eeat-framework.md",
        "scripts/validate_schema.py": "hooks/validate-schema.py",
    },
}

SKILL_MD_MAX_LINES = 500
REFERENCE_MAX_LINES = 200  # repo rule; canonical copies over it are reported as warnings

FIXED_DATE = (1980, 1, 1, 0, 0, 0)
EXCLUDE_DIRS = {"__pycache__", "node_modules", ".pytest_cache"}
EXCLUDE_FILES = {".DS_Store", "Thumbs.db"}
EXCLUDE_SUFFIXES = (".pyc", ".pyo", ".bak", ".tmp", ".swp")
ROOT_EXCLUDE_DIRS = {"evals"}
SKIP_FOLDERS = {"dist", "__pycache__"}

ALLOWED_KEYS = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}

SKILL_CREATOR_CANDIDATES = [
    os.environ.get("SKILL_CREATOR_DIR", ""),
    os.path.expanduser("~/.claude/skills/skill-creator"),
]


def discover(src: str, only: Optional[List[str]]) -> List[str]:
    """Return sorted skill folder names under src (default claude-ai-skills/)."""
    names = []
    for entry in sorted(os.listdir(src)):
        path = os.path.join(src, entry)
        if entry in SKIP_FOLDERS or entry.startswith(".") or not os.path.isdir(path):
            continue
        if only and entry not in only:
            continue
        names.append(entry)
    return names


def _excluded(rel: str) -> bool:
    parts = rel.split("/")
    if any(p in EXCLUDE_DIRS for p in parts):
        return True
    if len(parts) > 1 and parts[0] in ROOT_EXCLUDE_DIRS:
        return True
    name = parts[-1]
    return name in EXCLUDE_FILES or name.endswith(EXCLUDE_SUFFIXES)


def stage(src_root: str, name: str, staging_root: str) -> Tuple[str, List[str]]:
    """Copy the skill source plus its canonical files into staging_root/name."""
    src = os.path.join(src_root, name)
    dest = os.path.join(staging_root, name)
    copied = []
    for dirpath, dirnames, filenames in os.walk(src):
        dirnames[:] = sorted(d for d in dirnames if d not in EXCLUDE_DIRS)
        for fn in sorted(filenames):
            rel = os.path.relpath(os.path.join(dirpath, fn), src).replace(os.sep, "/")
            if _excluded(rel):
                continue
            target = os.path.join(dest, rel)
            os.makedirs(os.path.dirname(target), exist_ok=True)
            shutil.copyfile(os.path.join(dirpath, fn), target)
    for rel, repo_rel in sorted(CANONICAL_COPIES.get(name, {}).items()):
        source = os.path.join(REPO, repo_rel)
        if not os.path.isfile(source):
            raise FileNotFoundError(f"canonical source missing: {repo_rel}")
        if os.path.exists(os.path.join(src, rel)):
            raise FileExistsError(
                f"{name}/{rel} exists in the source folder; canonical copies must not be duplicated")
        target = os.path.join(dest, rel)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        shutil.copyfile(source, target)
        copied.append(rel)
    return dest, copied


def parse_frontmatter(text: str) -> Tuple[Optional[Dict[str, str]], str]:
    """Minimal stdlib frontmatter reader: top-level keys and scalar values."""
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return None, "no YAML frontmatter"
    data: Dict[str, str] = {}
    current = None
    for line in match.group(1).split("\n"):
        top = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if top:
            current = top.group(1)
            value = top.group(2).strip()
            if value in (">", "|", ">-", "|-"):
                value = ""
            elif value and value[0] not in "\"'[{" and (": " in value or " #" in value):
                data["__yaml_error__"] = (
                    f"plain YAML value for '{current}' contains ': ' or ' #'; "
                    "quote it or use a folded block (>)")
            data[current] = value.strip('"').strip("'")
        elif current and line.startswith((" ", "\t")) and current != "metadata":
            data[current] = (data[current] + " " + line.strip()).strip()
    return data, ""


def builtin_validate(skill_dir: str) -> Tuple[List[str], List[str]]:
    """Frontmatter and line-limit checks equivalent to quick_validate plus repo rules."""
    errors: List[str] = []
    warnings: List[str] = []
    skill_md = os.path.join(skill_dir, "SKILL.md")
    if not os.path.isfile(skill_md):
        return ["SKILL.md not found"], warnings
    text = open(skill_md, encoding="utf-8").read()
    fm, err = parse_frontmatter(text)
    if fm is None:
        return [err], warnings
    if "__yaml_error__" in fm:
        errors.append(fm.pop("__yaml_error__"))
    unexpected = set(fm) - ALLOWED_KEYS
    if unexpected:
        errors.append(f"unexpected frontmatter keys: {', '.join(sorted(unexpected))}")
    name = fm.get("name", "")
    desc = fm.get("description", "")
    if not name:
        errors.append("missing name")
    elif not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", name) or len(name) > 64:
        errors.append(f"name '{name}' must be kebab-case, max 64 characters")
    elif name != os.path.basename(skill_dir):
        errors.append(f"name '{name}' does not match folder '{os.path.basename(skill_dir)}'")
    if not desc:
        errors.append("missing description")
    elif len(desc) > 1024:
        errors.append(f"description is {len(desc)} characters (max 1024)")
    elif "<" in desc or ">" in desc:
        errors.append("description contains angle brackets")
    nested = []
    for dirpath, _dirs, files in os.walk(skill_dir):
        for fn in files:
            if fn == "SKILL.md" and dirpath != skill_dir:
                nested.append(os.path.relpath(os.path.join(dirpath, fn), skill_dir))
    if nested:
        errors.append(f"extra SKILL.md files: {', '.join(sorted(nested))}")
    lines = text.count("\n") + (0 if text.endswith("\n") else 1)
    if lines > SKILL_MD_MAX_LINES:
        errors.append(f"SKILL.md has {lines} lines (max {SKILL_MD_MAX_LINES})")
    ref_dir = os.path.join(skill_dir, "references")
    if os.path.isdir(ref_dir):
        for fn in sorted(os.listdir(ref_dir)):
            with open(os.path.join(ref_dir, fn), encoding="utf-8", errors="replace") as fh:
                n = sum(1 for _ in fh)
            if n > REFERENCE_MAX_LINES:
                warnings.append(f"references/{fn} has {n} lines (repo rule: under {REFERENCE_MAX_LINES})")
    return errors, warnings


def skill_creator_validate(skill_dir: str) -> Tuple[Optional[bool], str]:
    """Run skill-creator's quick_validate.validate_skill if it can be imported."""
    candidates = [c for c in SKILL_CREATOR_CANDIDATES if c]
    synced = os.path.expanduser("~/.claude/skills/synced")
    if os.path.isdir(synced):
        for entry in sorted(os.listdir(synced)):
            candidates.append(os.path.join(synced, entry, "skill-creator"))
    for base in candidates:
        script = os.path.join(base, "scripts", "quick_validate.py")
        if not os.path.isfile(script):
            continue
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("quick_validate", script)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            ok, message = module.validate_skill(skill_dir)
            return bool(ok), message
        except ImportError as exc:  # PyYAML missing
            return None, f"quick_validate not usable: {exc}"
    return None, "skill-creator quick_validate.py not found"


def write_zip(skill_dir: str, out_path: str) -> List[str]:
    """Write a deterministic zip with the skill folder at the archive root."""
    parent = os.path.dirname(skill_dir)
    entries = []
    for dirpath, _dirs, files in os.walk(skill_dir):
        for fn in files:
            full = os.path.join(dirpath, fn)
            entries.append(os.path.relpath(full, parent).replace(os.sep, "/"))
    entries.sort()
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for arc in entries:
            info = zipfile.ZipInfo(arc, date_time=FIXED_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = (0o100755 if arc.endswith(".py") else 0o100644) << 16
            with open(os.path.join(parent, arc), "rb") as fh:
                zf.writestr(info, fh.read(), compresslevel=9)
    data = buf.getvalue()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "wb") as fh:
        fh.write(data)
    return entries


def sha256(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def build(out_dir: str, only: Optional[List[str]], src: str = HERE) -> Dict:
    """Build all skills into out_dir and return a JSON-serialisable report."""
    report = {"src": src, "out_dir": out_dir, "skills": [], "status": "pass"}
    with tempfile.TemporaryDirectory() as staging:
        for name in discover(src, only):
            item = {"name": name}
            if not os.path.isfile(os.path.join(src, name, "SKILL.md")):
                item.update(status="skipped", reason="no SKILL.md in folder yet")
                report["skills"].append(item)
                continue
            try:
                skill_dir, copied = stage(src, name, staging)
            except (FileNotFoundError, FileExistsError) as exc:
                item.update(status="fail", errors=[str(exc)])
                report["skills"].append(item)
                report["status"] = "fail"
                continue
            errors, warnings = builtin_validate(skill_dir)
            qv_ok, qv_msg = skill_creator_validate(skill_dir)
            if qv_ok is False:
                errors.append(f"quick_validate: {qv_msg}")
            item.update(canonical_copies=copied, errors=errors, warnings=warnings,
                        quick_validate=qv_msg if qv_ok is not None else f"skipped: {qv_msg}")
            if errors:
                item["status"] = "fail"
                report["status"] = "fail"
            else:
                out_path = os.path.join(out_dir, f"{name}.skill")
                entries = write_zip(skill_dir, out_path)
                item.update(status="pass", package=out_path, files=entries,
                            bytes=os.path.getsize(out_path), sha256=sha256(out_path))
            report["skills"].append(item)
    return report


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Build claude.ai .skill packages from claude-ai-skills/.")
    parser.add_argument("--out", default=DEFAULT_OUT, help="output directory (default: claude-ai-skills/dist)")
    parser.add_argument("--src", default=HERE, help="folder holding the skill sources (default: claude-ai-skills)")
    parser.add_argument("--only", nargs="+", help="build only these skill folders")
    parser.add_argument("--check", action="store_true",
                        help="build into a temp dir and fail if the packages in --out differ")
    parser.add_argument("--strict", action="store_true", help="treat skipped folders as failures")
    args = parser.parse_args(argv)
    src = os.path.abspath(args.src)
    out_dir = os.path.abspath(args.out)

    if args.only:
        missing = [n for n in args.only if n not in discover(src, None)]
        if missing:
            print(json.dumps({"status": "error", "error": f"unknown skill folder(s): {missing}"}))
            return 2

    if args.check:
        with tempfile.TemporaryDirectory() as tmp:
            report = build(tmp, args.only, src)
            stale = []
            for item in report["skills"]:
                if item.get("status") != "pass":
                    continue
                current = os.path.join(out_dir, f"{item['name']}.skill")
                if not os.path.isfile(current) or sha256(current) != item["sha256"]:
                    stale.append(item["name"])
                item["package"] = current
            report.update(mode="check", out_dir=out_dir, stale=stale)
            if stale:
                report["status"] = "fail"
    else:
        report = build(out_dir, args.only, src)

    if args.strict and any(i.get("status") == "skipped" for i in report["skills"]):
        report["status"] = "fail"
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
