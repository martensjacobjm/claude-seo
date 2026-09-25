#!/usr/bin/env python3
"""Post-edit schema validation hook for Claude Code.

Validates JSON-LD schema after file edits. Exit codes:
  0 = no issues (or not an HTML-like file / no JSON-LD)
  1 = warnings only (non-blocking; Claude Code shows the first stderr line)
  2 = blocking errors (placeholder text, deprecated Google types). For a
      PostToolUse hook the edit has already happened; Claude Code shows the
      stderr text to Claude so it can fix the markup.

Type status as of 2026-09-24. Sources:
  https://developers.google.com/search/updates
  https://developers.google.com/search/docs/appearance/structured-data/search-gallery
  https://developers.google.com/search/docs/appearance/structured-data/math-solvers
Every node with an @type is checked, at any nesting depth (including @graph
members and values such as mainEntity). Type names are normalised, so
"HowTo", "schema:HowTo" and "https://schema.org/HowTo" are treated alike.

Input: Claude Code passes the hook event as JSON on stdin; the edited path is
read from tool_input.file_path (https://code.claude.com/docs/en/hooks).
For manual use, pass the path as a positional argument instead.
Pass --json to print findings as JSON on stdout (always emitted, including
{"status": "skipped"} when nothing is validated).

Hook configuration (this plugin ships it in hooks/hooks.json):
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/validate-schema.py\""
          }
        ]
      }
    ]
  }
}

Note: matcher filters by tool name only (Edit, Write). The script itself
checks if the file contains schema markup before validating.
"""

import argparse
import json
import re
import sys
import os
from typing import Any, Dict, Iterator, List, Optional, Tuple

BLOCKING = "error"
WARNING = "warning"

# Deprecated: Google no longer shows these features. Blocking.
# Course info, estimated salary, learning video and vehicle listing were
# Google feature names, not schema.org types (schema.org/<name> is 404), so
# those keys only catch hand-made markup that invented the type name.
# Docs for them were removed Sep 9, 2025 (search/updates).
DEPRECATED_TYPES: Dict[str, str] = {
    "HowTo": "deprecated: how-to rich results removed September 2023",  # see HOWTO_EXEMPT_WITH
    "SpecialAnnouncement": "deprecated July 31, 2025; docs removed Sep 9, 2025",
    "CourseInfo": "deprecated: course info no longer shown; docs removed Sep 9, 2025",
    "EstimatedSalary": "deprecated: estimated salary no longer shown; docs removed Sep 9, 2025",
    "LearningVideo": "deprecated: learning video no longer shown; docs removed Sep 9, 2025",
    "VehicleListing": "deprecated: vehicle listing no longer shown; docs removed Sep 9, 2025",
}

# Valid schema.org types with no (or a phasing-out) Google rich result.
# Non-blocking warnings.
NO_RICH_RESULT_TYPES: Dict[str, str] = {
    "FAQPage": (
        "valid schema.org, but Google FAQ rich results are no longer shown "
        "since May 7, 2026 (docs removed June 15, 2026); do not add for Google"
    ),
    "ClaimReview": (
        "being phased out of Google Search; still supported by Fact Check Explorer"
    ),
}

# Google's math-solver doc still documents a MathSolver accompanying a HowTo
# (via MathSolver.assesses), so HowTo in the same JSON-LD block as a
# MathSolver is only a warning.
HOWTO_EXEMPT_WITH = "MathSolver"
HOWTO_WITH_MATHSOLVER = (
    "no how-to rich result since September 2023; allowed here because the "
    "block also has a MathSolver (Google math-solver doc)"
)

# Placeholder tokens left over from templates. Only bracketed tokens and the
# all-caps whole word REPLACE / REPLACE_ME match, so ordinary words such as
# "replacement" or "[1]" footnotes don't trigger a block.
PLACEHOLDER_PATTERNS = [
    re.compile(
        r"\[(?:Business Name|Company Name|City|State|Street|ZIP|Phone|Address|"
        r"Email|URL|[A-Za-z ]*\bURL\b[^\]]*|[A-Za-z ]+ Name|YYYY-MM-DD[^\]]*|"
        r"INSERT[^\]]*|Your [^\]]*)\]"
    ),
    re.compile(r"\bREPLACE(?:_ME)?\b"),
]

# Likely dummy data that is not bracketed (non-blocking warnings): long zero
# runs in phone numbers, "example"/"exempel" street names or domains, lorem
# ipsum. Warnings only, since real data can occasionally match.
DUMMY_PATTERNS = [
    (re.compile(r"\+?\d[\d\s-]*0{6,}\d*"), "phone number with a long run of zeros"),
    (re.compile(r"\b(?:Example|Exempel)(?:vägen|gatan|\s+(?:Street|Road|Avenue|Ave|St))\b\s*\d*", re.I),
     "example/exempel street address"),
    (re.compile(r"\bexample\.(?:com|org|net|se)\b", re.I), "example domain"),
    (re.compile(r"\blorem ipsum\b", re.I), "lorem ipsum text"),
]

Finding = Tuple[str, str]  # (severity, message)


def validate_jsonld(content: str) -> List[Finding]:
    """Validate JSON-LD blocks in HTML content. Returns (severity, message) pairs."""
    findings: List[Finding] = []
    pattern = r'<script\s+type=["\']application/ld\+json["\']\s*>(.*?)</script>'
    blocks = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)

    if not blocks:
        return []  # No schema found; not an error

    for i, block in enumerate(blocks, 1):
        block = block.strip()
        try:
            data = json.loads(block)
        except json.JSONDecodeError as e:
            findings.append((WARNING, f"Block {i}: Invalid JSON; {e}"))
            continue

        has_mathsolver = HOWTO_EXEMPT_WITH in {
            name for node, _ in _walk(data, f"Block {i}") for name in _type_names(node)
        }
        items = data if isinstance(data, list) else [data]
        for item in items:
            if isinstance(item, dict):
                findings.extend(_validate_schema_object(item, i, has_mathsolver))

    return findings


def _type_names(obj: dict) -> List[str]:
    """Return normalised @type names (string or list; IRIs and prefixes stripped)."""
    value = obj.get("@type")
    if isinstance(value, str):
        raw = [value]
    elif isinstance(value, list):
        raw = [t for t in value if isinstance(t, str)]
    else:
        raw = []
    return [re.split(r"[/:#]", t.rstrip("/"))[-1] for t in raw]


def _walk(value: Any, path: str) -> Iterator[Tuple[dict, str]]:
    """Yield (node, path) for every dict with an @type, at any depth."""
    if isinstance(value, dict):
        if "@type" in value:
            yield value, path
        for key, child in value.items():
            if isinstance(child, (dict, list)):
                yield from _walk(child, f"{path}.{key}")
    elif isinstance(value, list):
        for n, child in enumerate(value):
            if isinstance(child, (dict, list)):
                yield from _walk(child, f"{path}[{n}]")


def _check_types(obj: dict, where: str, has_mathsolver: bool) -> List[Finding]:
    """Flag deprecated and no-rich-result types on one node."""
    findings: List[Finding] = []
    for short in _type_names(obj):
        if short == "HowTo" and has_mathsolver:
            findings.append((WARNING, f"{where}: @type 'HowTo': {HOWTO_WITH_MATHSOLVER}"))
        elif short in DEPRECATED_TYPES:
            findings.append((BLOCKING, f"{where}: @type '{short}' is {DEPRECATED_TYPES[short]}"))
        elif short in NO_RICH_RESULT_TYPES:
            findings.append((WARNING, f"{where}: @type '{short}' is {NO_RICH_RESULT_TYPES[short]}"))
    return findings


def _validate_schema_object(obj: dict, block_num: int, has_mathsolver: bool = False) -> List[Finding]:
    """Validate a top-level schema object and every nested typed node."""
    findings: List[Finding] = []
    prefix = f"Block {block_num}"

    # Check @context (top level only; nested nodes inherit it)
    if "@context" not in obj:
        findings.append((WARNING, f"{prefix}: Missing @context"))
    elif obj["@context"] not in ("https://schema.org", "http://schema.org",
                                 "https://schema.org/", "http://schema.org/"):
        findings.append((WARNING, f"{prefix}: @context should be 'https://schema.org'"))

    # Missing @type: top-level object, or each direct @graph member
    graph = obj.get("@graph")
    if isinstance(graph, list):
        for n, node in enumerate(graph):
            if isinstance(node, dict) and "@type" not in node:
                findings.append((WARNING, f"{prefix}.@graph[{n}]: Missing @type"))
    elif "@type" not in obj:
        findings.append((WARNING, f"{prefix}: Missing @type"))

    # Type status for every typed node at any depth
    for node, where in _walk(obj, prefix):
        findings.extend(_check_types(node, where, has_mathsolver))

    # Check for placeholder text (blocking)
    text = json.dumps(obj, ensure_ascii=False)
    seen = set()
    for pat in PLACEHOLDER_PATTERNS:
        for m in pat.finditer(text):
            if m.group(0) not in seen:
                seen.add(m.group(0))
                findings.append((BLOCKING, f"{prefix}: Contains placeholder text: {m.group(0)}"))
    for pat, label in DUMMY_PATTERNS:
        m = pat.search(text)
        if m and m.group(0).strip() not in seen:
            seen.add(m.group(0).strip())
            findings.append((WARNING, f"{prefix}: Possible dummy data ({label}): {m.group(0).strip()}"))

    return findings


def _parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse CLI args. Unknown args are ignored so the hook never blocks on usage."""
    parser = argparse.ArgumentParser(
        description="Validate JSON-LD schema in an edited HTML-like file (Claude Code hook). "
                    "Reads the Claude Code hook JSON from stdin when no file is given."
    )
    parser.add_argument("file", nargs="?", default="", help="Path of the edited file")
    parser.add_argument("--json", action="store_true", help="Print findings as JSON")
    args, _unknown = parser.parse_known_args(argv)
    return args


def _path_from_stdin() -> str:
    """Read the edited file path from Claude Code hook JSON on stdin."""
    try:
        if sys.stdin is None or sys.stdin.isatty():
            return ""
        raw = sys.stdin.read()
    except (OSError, ValueError):
        return ""
    if not raw.strip():
        return ""
    try:
        event = json.loads(raw)
    except json.JSONDecodeError:
        return ""
    if not isinstance(event, dict):
        return ""
    tool_input = event.get("tool_input")
    if isinstance(tool_input, dict):
        path = tool_input.get("file_path") or tool_input.get("path") or ""
        if isinstance(path, str) and path:
            if not os.path.isabs(path) and isinstance(event.get("cwd"), str):
                path = os.path.join(event["cwd"], path)
            return path
    return ""


def _skip(args: argparse.Namespace, filepath: str, reason: str) -> None:
    """Exit 0 without validating; with --json, still print a JSON result."""
    if args.json:
        print(json.dumps({"file": filepath, "status": "skipped", "reason": reason,
                          "errors": [], "warnings": []}, indent=2))
    sys.exit(0)


VALID_EXTENSIONS = (".html", ".htm", ".jsx", ".tsx", ".vue", ".svelte", ".php", ".ejs")


def main():
    args = _parse_args()
    filepath = args.file or _path_from_stdin()

    if not filepath:
        _skip(args, filepath, "no file path given (argument or hook stdin)")
    if not os.path.isfile(filepath):
        _skip(args, filepath, "file not found")
    # Only validate HTML-like files
    if not filepath.lower().endswith(VALID_EXTENSIONS):
        _skip(args, filepath, "not an HTML-like file")

    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except (OSError, IOError) as e:
        _skip(args, filepath, f"read error: {e}")

    findings = validate_jsonld(content)
    critical = [m for sev, m in findings if sev == BLOCKING]
    warnings = [m for sev, m in findings if sev == WARNING]

    if args.json:
        status = "block" if critical else ("warn" if warnings else "pass")
        print(json.dumps({"file": filepath, "status": status,
                          "errors": critical, "warnings": warnings}, indent=2))
    else:
        # stderr: the only stream Claude Code shows to Claude for exit 2
        # (PostToolUse), and whose first line it shows for exit 1.
        lines: List[str] = []
        if critical:
            lines.append(f"Schema validation ERRORS in {filepath} (fix required):")
            lines.extend(f"  - {e}" for e in critical)
        if warnings:
            lines.append(f"Schema validation warnings in {filepath}:")
            lines.extend(f"  - {w}" for w in warnings)
        if lines:
            print("\n".join(lines), file=sys.stderr)

    if critical:
        sys.exit(2)  # Claude sees stderr and should fix the markup
    if warnings:
        sys.exit(1)  # Warnings only; non-blocking
    sys.exit(0)


if __name__ == "__main__":
    main()
