#!/usr/bin/env python3
"""
Credential scanner for website repositories (working tree + optional git history).

Built for the "static site deployed by SFTP" failure mode: passwords typed
into upload scripts, deployment guides and READMEs, then pushed to a public
repository. The scanner looks for:

* Known token formats: GitHub (ghp_/gho_/ghu_/ghs_/ghr_, github_pat_),
  Google API keys (AIza...), AWS access key IDs and secret keys, Slack tokens
  and webhooks, Stripe keys, PEM/OpenSSH/PGP private key blocks and JWTs.
* Generic assignments such as ``password = "..."``, ``set PASS=...``,
  ``$env:SFTP_PASSWORD = '...'``, ``"api_key": "..."`` or ``**Password:** ...``
  in shell, batch, PowerShell, Python, JavaScript, JSON, YAML, .env, INI and
  Markdown files (Swedish/Norwegian/German password words included).
  A Shannon-entropy check grades generic values and placeholders are skipped.
* Connection strings and URLs with ``user:pass@`` credentials.
* Command-line credentials: ``curl -u user:pass``, ``sshpass -p``,
  ``lftp -u user,pass``, ``pscp/plink -pw``, WinSCP ``/password=``.
* ``curl --insecure`` / ``curl -k`` (reported as a warning, not a secret).

Secrets are NEVER printed in full: every value is masked to its first 2 and
last 2 characters (values shorter than 8 characters are masked completely).
Identical values are grouped under a per-run id (S1, S2, ...) so you can see
that one password appears in 7 files without the tool emitting a hash of it.

With ``--git-history`` every commit reachable from any ref (``git log -p
--all``, bounded by ``--max-commits``) is scanned, so a password that was
committed and later deleted is still reported. Deleting a file does not
remove it from history: rotate the credential first, then rewrite history.

The scanner also reports whether the repository's git remote points at
GitHub and suggests checking the repository visibility (no API call is made).

Ignore rules: a ``.secretscanignore`` file in the scanned directory holds
glob patterns (one per line, ``#`` comments, ``dir/`` for directories)
matched against the repo-relative path and the file name. A line containing
``secretscan:allow`` is skipped. ``.git``, binary files and files larger than
``--max-file-size`` are skipped.

Exit codes: 0 = no high-severity findings, 1 = at least one high finding,
2 = usage error (path missing, not a git repo with --git-history, ...).

Usage:
    python secret_scan.py /path/to/site
    python secret_scan.py /path/to/site --git-history --max-commits 1000
    python secret_scan.py /path/to/site --git-history --text
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import hmac
import json
import math
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from typing import Dict, Iterable, List, Optional, Tuple

SEVERITY_ORDER = {"high": 3, "medium": 2, "low": 1, "warning": 0}
DEFAULT_MAX_FILE_SIZE = 1_000_000
DEFAULT_MAX_COMMITS = 500
MAX_LINE_LENGTH = 4000  # minified bundles: skip absurdly long lines
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", ".tox",
             ".mypy_cache", ".pytest_cache", "dist", "build", ".next", ".cache"}
IGNORE_FILE = ".secretscanignore"
ALLOW_MARKER = "secretscan:allow"

# Extensions (and extension-less names) where generic "password = ..." rules run.
GENERIC_EXTS = {
    ".sh", ".bash", ".zsh", ".bat", ".cmd", ".ps1", ".psm1", ".py", ".js",
    ".mjs", ".cjs", ".ts", ".json", ".yaml", ".yml", ".env", ".md",
    ".markdown", ".txt", ".ini", ".cfg", ".conf", ".toml", ".php",
    ".properties", ".xml", ".html", ".htm", ".rb", ".config",
}

# --- Known token formats -----------------------------------------------------
# (rule id, regex, severity, capture group holding the secret)
TOKEN_RULES: List[Tuple[str, "re.Pattern[str]", str, int]] = [
    ("github-token", re.compile(r"\b(gh[pousr]_[A-Za-z0-9]{36,255})\b"), "high", 1),
    ("github-fine-grained-pat", re.compile(r"\b(github_pat_[A-Za-z0-9_]{22,255})\b"), "high", 1),
    ("google-api-key", re.compile(r"\b(AIza[0-9A-Za-z_\-]{35})(?![0-9A-Za-z_\-])"), "high", 1),
    ("aws-access-key-id", re.compile(r"\b((?:AKIA|ASIA|ABIA|ACCA)[0-9A-Z]{16})\b"), "high", 1),
    ("aws-secret-access-key", re.compile(
        r"(?i)aws_?secret_?access_?key[\"']?\s*[:=]\s*[\"']?([A-Za-z0-9/+=]{40})(?![A-Za-z0-9/+=])"),
     "high", 1),
    ("slack-token", re.compile(r"\b(xox[abposr]-[0-9A-Za-z-]{10,})\b"), "high", 1),
    ("slack-webhook", re.compile(
        r"(https://hooks\.slack\.com/services/T[A-Z0-9]+/B[A-Z0-9]+/[A-Za-z0-9]+)"), "high", 1),
    ("stripe-live-key", re.compile(r"\b((?:sk|rk)_live_[0-9A-Za-z]{16,})\b"), "high", 1),
    ("stripe-test-key", re.compile(r"\b((?:sk|rk)_test_[0-9A-Za-z]{16,})\b"), "medium", 1),
    ("private-key-block", re.compile(
        r"(-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP |ENCRYPTED )?PRIVATE KEY(?: BLOCK)?-----)"),
     "high", 1),
    ("jwt", re.compile(
        r"\b(eyJ[A-Za-z0-9_-]{8,}\.eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,})\b"), "medium", 1),
]

# user:pass@host in any scheme (ftp, sftp, mysql, postgres, mongodb, redis, https ...)
URL_CRED_RE = re.compile(
    r"\b([a-zA-Z][a-zA-Z0-9+.\-]{1,20})://([^\s:/@'\"<>]{1,128}):([^\s@/'\"<>]{1,256})@([^\s/'\"<>:]+)")

# Command-line credentials.
CLI_RULES: List[Tuple[str, "re.Pattern[str]", str]] = [
    ("curl-user-password", re.compile(
        r"\bcurl\b[^\n|;&]*?(?:\s-u\s*|\s--user[\s=]+)[\"']?[^\s:\"']+:([^\s\"']+)"), "high"),
    ("sshpass-password", re.compile(r"\bsshpass\s+-p\s*[\"']?([^\s\"']+)"), "high"),
    ("lftp-user-password", re.compile(r"\blftp\b[^\n]*?\s-u\s+[\"']?[^\s,\"']+,([^\s\"']+)"), "high"),
    ("putty-pw-flag", re.compile(r"\b(?:pscp|plink|psftp)(?:\.exe)?\b[^\n]*?\s-pw\s+[\"']?([^\s\"']+)"), "high"),
    ("winscp-password", re.compile(r"(?i)/password=[\"']?([^\s\"']+)"), "high"),
]
CURL_INSECURE_RE = re.compile(r"\bcurl\b[^\n|;&]*?(?:\s--insecure\b|\s-[a-zA-Z]*k[a-zA-Z]*\b)")

# Generic assignments. Keys include common non-English password words.
KEY_WORDS = (
    r"pass(?:word|wd|phrase)?|pwd|secret|client[_\-]?secret|api[_\-]?key|apikey|"
    r"access[_\-]?key|auth[_\-]?token|access[_\-]?token|token|private[_\-]?key|"
    r"l(?:ö|o|oe)senord|passord|passwort|kennwort|contrase(?:ñ|n)a|mot[_\- ]de[_\- ]passe"
)
# KEY (possibly prefixed, e.g. SFTP_PASSWORD, $env:FTP_PASS) then := / : / =
GENERIC_RE = re.compile(
    r"(?i)(?P<key>[A-Za-z0-9_$.\-]*(?:" + KEY_WORDS + r")[A-Za-z0-9_]*)"
    r"(?P<sep>[\"'`*\]\s]*\s*(?::=|=>|=|:)\s*[`*]*\s*)"
    r"(?P<val>\"[^\"\n]{1,256}\"|'[^'\n]{1,256}'|`[^`\n]{1,256}`|[^\s\"'`,;<>)*]{1,256})"
)

PLACEHOLDER_RE = re.compile(
    r"(?i)^(?:x+|\*+|\.+|-+|_+|#+|0+|<.*>|\[.*\]|\{.*\}|\$\{?.*\}?|%[A-Za-z0-9_]+%|"
    r"\$[A-Za-z_][A-Za-z0-9_]*|\$\(.*\)|process\.env.*|os\.environ.*|os\.getenv.*|"
    r"getenv.*|env\(.*|input\(.*|getpass.*|none|null|nil|true|false|undefined|"
    r"(?:your|my|the|ditt|ert|min)[_\- ]?.*|.*(?:here|här)|changeme|change_me|"
    r"example.*|sample|dummy|test|testing|placeholder|redacted|secret|password|"
    r"passwd|pass|pwd|token|api[_\-]?key|lösenord|losenord|required|optional|"
    r"string|str|int|bool|\.\.\.|…|todo|tbd|n/?a|false|off|on|yes|no)$"
)
# Values that are code, not literals (function calls, attribute access, etc.).
CODE_VALUE_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*(?:\(.*)?$")


def shannon_entropy(value: str) -> float:
    """Shannon entropy in bits per character."""
    if not value:
        return 0.0
    counts: Dict[str, int] = {}
    for ch in value:
        counts[ch] = counts.get(ch, 0) + 1
    n = len(value)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def mask(value: str) -> str:
    """Mask a secret: keep the first 2 and last 2 characters only.

    Values shorter than 8 characters are fully masked, because showing four
    characters of a six-character password would reveal most of it.
    """
    if len(value) < 8:
        return "*" * 8
    return f"{value[:2]}{'*' * 8}{value[-2:]}"


def is_placeholder(value: str) -> bool:
    """True for obvious placeholders, variable references and code."""
    v = value.strip().strip("\"'`").strip()
    if not v:
        return True
    if PLACEHOLDER_RE.match(v):
        return True
    return False


class SecretRegistry:
    """Assigns stable per-run ids (S1, S2, ...) to identical secret values.

    Uses an HMAC with a random per-run key so nothing derived from the secret
    is ever emitted or persisted.
    """

    def __init__(self) -> None:
        self._key = os.urandom(32)
        self._ids: Dict[bytes, str] = {}

    def id_for(self, value: str) -> str:
        digest = hmac.new(self._key, value.encode("utf-8", "replace"), hashlib.sha256).digest()
        if digest not in self._ids:
            self._ids[digest] = f"S{len(self._ids) + 1}"
        return self._ids[digest]

    def __len__(self) -> int:
        return len(self._ids)


def _generic_applies(path: str) -> bool:
    base = os.path.basename(path).lower()
    if base.startswith(".env") or base in {"dockerfile", "makefile", ".netrc", ".npmrc", ".pypirc"}:
        return True
    ext = os.path.splitext(base)[1]
    if not ext:
        return True  # extension-less notes/scripts (e.g. "deploy", "update_mobile")
    return ext in GENERIC_EXTS


KEYWORD_RE = re.compile(r"(?i)(?:" + KEY_WORDS + r")")
KEY_SEPARATORS = "_-.$:"


def key_is_credential_name(key: str) -> bool:
    """True if a keyword sits on a word boundary inside the key.

    Accepts SFTP_PASSWORD, $env:FTP_PASS, ftpPassword, api-key, "Lösenord";
    rejects bypass, compass, passenger, tokenizer.
    """
    for m in KEYWORD_RE.finditer(key):
        s, e = m.start(), m.end()
        before = key[s - 1] if s > 0 else ""
        after = key[e] if e < len(key) else ""
        left_ok = (not before or before in KEY_SEPARATORS or before.isdigit()
                   or (before.islower() and key[s].isupper()))
        right_ok = (not after or after in KEY_SEPARATORS or after.isdigit()
                    or (after.isupper() and not key[e - 1].isupper()) or key[e:].lower() == "s")
        if left_ok and right_ok:
            return True
    return False


def _grade_generic(key: str, value: str) -> Optional[str]:
    """Return severity for a generic key/value pair, or None to drop it."""
    if not key_is_credential_name(key.strip("$*`\"'")):
        return None
    quoted = value[:1] in "\"'`"
    v = value.strip("\"'`").strip()
    if is_placeholder(v) or len(v) < 4:
        return None
    if not quoted and CODE_VALUE_RE.match(v) and not any(c.isdigit() for c in v):
        # bare identifiers like `password = getPassword()` or `token: string`
        if "(" in v or "." in v or v.islower() or v.isupper():
            return None
    if v.startswith(("http://", "https://")) and "@" not in v:
        return None
    ent = shannon_entropy(v)
    k = key.lower()
    is_password_word = bool(re.search(
        r"pass|pwd|l(?:ö|o|oe)senord|passord|passwort|kennwort|contrase|mot.de.passe", k))
    if ent < 1.5:
        return "low"
    if is_password_word and len(v) >= 6:
        return "high"  # human passwords are low-entropy but still passwords
    if len(v) >= 16 and ent >= 3.5:
        return "high"
    if len(v) >= 8 and ent >= 3.0:
        return "medium"
    return "low"


def scan_text(text: str, path: str, registry: SecretRegistry,
              line_offset: Optional[Dict[int, int]] = None) -> List[dict]:
    """Scan text and return findings (masked). line_offset maps index->line no."""
    findings: List[dict] = []
    generic_ok = _generic_applies(path)
    for idx, line in enumerate(text.splitlines()):
        if len(line) > MAX_LINE_LENGTH or ALLOW_MARKER in line:
            continue
        lineno = line_offset[idx] if line_offset is not None else idx + 1
        spans: List[Tuple[int, int]] = []

        def add(rule: str, severity: str, value: str, start: int, end: int,
                extra: Optional[dict] = None) -> None:
            for s, e in spans:
                if start < e and end > s:
                    return
            spans.append((start, end))
            item = {"file": path, "line": lineno, "rule": rule, "severity": severity,
                    "masked_value": mask(value) if value else None,
                    "secret_id": registry.id_for(value) if value else None}
            if extra:
                item.update(extra)
            findings.append(item)

        for rule, rx, sev, grp in TOKEN_RULES:
            for m in rx.finditer(line):
                add(rule, sev, m.group(grp), m.start(grp), m.end(grp))
        for m in URL_CRED_RE.finditer(line):
            pw = m.group(3)
            if is_placeholder(pw) or pw.startswith(("$", "%")):
                continue
            add("url-embedded-credentials", "high", pw, m.start(3), m.end(3),
                {"scheme": m.group(1).lower(), "host": m.group(4)})
        for rule, rx, sev in CLI_RULES:
            for m in rx.finditer(line):
                pw = m.group(1)
                if is_placeholder(pw) or pw.startswith(("$", "%")):
                    continue
                add(rule, sev, pw, m.start(1), m.end(1))
        if CURL_INSECURE_RE.search(line):
            findings.append({"file": path, "line": lineno, "rule": "curl-insecure-tls",
                             "severity": "warning", "masked_value": None, "secret_id": None,
                             "note": "TLS certificate verification disabled (--insecure/-k)"})
        if generic_ok:
            for m in GENERIC_RE.finditer(line):
                key, val = m.group("key"), m.group("val")
                sev = _grade_generic(key, val)
                if not sev:
                    continue
                raw = val.strip("\"'`").strip()
                vs = m.start("val") + (1 if val[:1] in "\"'`" else 0)
                add("generic-credential-assignment", sev, raw, vs, vs + len(raw),
                    {"key": key.strip("$*`\"'")[:60],
                     "entropy": round(shannon_entropy(raw), 2)})
    return findings


# --- file walking --------------------------------------------------------------

def load_ignore(root: str, extra_file: Optional[str] = None) -> List[str]:
    """Read glob patterns from .secretscanignore (and an optional extra file)."""
    patterns: List[str] = []
    for p in [os.path.join(root, IGNORE_FILE), extra_file]:
        if p and os.path.isfile(p):
            with open(p, encoding="utf-8", errors="replace") as fh:
                for raw in fh:
                    line = raw.strip()
                    if line and not line.startswith("#"):
                        patterns.append(line)
    return patterns


def is_ignored(rel_path: str, patterns: Iterable[str], is_dir: bool = False) -> bool:
    """Match a posix relative path (file or directory) against ignore globs."""
    rel = rel_path.replace(os.sep, "/")
    while rel.startswith("./"):
        rel = rel[2:]
    base = rel.rsplit("/", 1)[-1]
    for pat in patterns:
        if pat.endswith("/"):
            d = pat.rstrip("/").lstrip("/")
            if not is_dir:
                # file inside an ignored directory
                parts = rel.split("/")[:-1]
                for i in range(len(parts)):
                    sub = "/".join(parts[: i + 1])
                    if fnmatch.fnmatch(sub, d) or fnmatch.fnmatch(parts[i], d):
                        return True
                continue
            if fnmatch.fnmatch(rel, d) or fnmatch.fnmatch(base, d):
                return True
            continue
        if fnmatch.fnmatch(rel, pat) or fnmatch.fnmatch(base, pat):
            return True
    return False


def _is_binary(chunk: bytes) -> bool:
    return b"\x00" in chunk


def scan_tree(root: str, registry: SecretRegistry, patterns: List[str],
              max_file_size: int) -> Tuple[List[dict], dict]:
    """Scan the working tree under root."""
    findings: List[dict] = []
    stats = {"files_scanned": 0, "skipped_binary": 0, "skipped_large": 0, "skipped_ignored": 0}
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root)
        dirnames[:] = sorted(
            d for d in dirnames if d not in SKIP_DIRS
            and not is_ignored(os.path.normpath(os.path.join(rel_dir, d)), patterns, is_dir=True))
        for name in sorted(filenames):
            full = os.path.join(dirpath, name)
            rel = os.path.normpath(os.path.relpath(full, root)).replace(os.sep, "/")
            if name == IGNORE_FILE or is_ignored(rel, patterns):
                stats["skipped_ignored"] += 1
                continue
            try:
                if os.path.islink(full) or not os.path.isfile(full):
                    continue
                if os.path.getsize(full) > max_file_size:
                    stats["skipped_large"] += 1
                    continue
                with open(full, "rb") as fh:
                    data = fh.read()
            except OSError:
                continue
            if _is_binary(data[:8192]):
                stats["skipped_binary"] += 1
                continue
            stats["files_scanned"] += 1
            text = data.decode("utf-8", errors="replace")
            findings.extend(scan_text(text, rel, registry))
    return findings, stats


# --- git ------------------------------------------------------------------------

def _git(root: str, *args: str, timeout: int = 300) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", root, "-c", "core.quotepath=false", *args],
                          capture_output=True, timeout=timeout)


def git_toplevel(root: str) -> Optional[str]:
    """Return the git top-level directory for root, or None."""
    try:
        r = _git(root, "rev-parse", "--show-toplevel")
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode != 0:
        return None
    return r.stdout.decode("utf-8", "replace").strip() or None


HUNK_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")


def scan_history(root: str, registry: SecretRegistry, patterns: List[str],
                 max_commits: int) -> Tuple[List[dict], dict]:
    """Scan added lines of every commit reachable from any ref (bounded)."""
    top = git_toplevel(root) or root
    prefix = os.path.relpath(os.path.abspath(root), os.path.abspath(top))
    prefix = "" if prefix == "." else prefix.replace(os.sep, "/") + "/"
    base_args = ["log", "-p", "--all", f"--max-count={max_commits}", "--no-color",
                 "--no-ext-diff", "--no-renames", "--unified=0",
                 "--format=@@COMMIT@@ %H %cI"]
    r = _git(top, *base_args, "--diff-merges=first-parent")
    if r.returncode != 0:
        r = _git(top, *base_args)
    if r.returncode != 0:
        return [], {"error": r.stderr.decode("utf-8", "replace").strip()[:300]}
    out = r.stdout.decode("utf-8", errors="replace")
    findings: List[dict] = []
    commits = 0
    commit = date = None
    cur_file: Optional[str] = None
    new_line = 0
    buf_lines: List[str] = []
    buf_nums: List[int] = []

    def flush() -> None:
        nonlocal buf_lines, buf_nums
        if cur_file and buf_lines:
            rel = cur_file[len(prefix):] if prefix and cur_file.startswith(prefix) else cur_file
            if (not prefix or cur_file.startswith(prefix)) and not is_ignored(rel, patterns):
                offs = {i: n for i, n in enumerate(buf_nums)}
                for f in scan_text("\n".join(buf_lines), rel, registry, offs):
                    f["commit"] = commit[:12] if commit else None
                    f["commit_date"] = date
                    findings.append(f)
        buf_lines, buf_nums = [], []

    in_header = False
    for line in out.split("\n"):
        if line.startswith("@@COMMIT@@ "):
            flush()
            parts = line.split()
            commit, date = parts[1], parts[2] if len(parts) > 2 else None
            commits += 1
            cur_file = None
            in_header = False
            continue
        if line.startswith("diff --git "):
            flush()
            cur_file = None
            in_header = True
            continue
        if in_header and line.startswith("+++ "):
            flush()
            target = line[4:].strip()
            cur_file = None if target == "/dev/null" else (target[2:] if target.startswith("b/") else target)
            continue
        m = HUNK_RE.match(line)
        if m:
            new_line = int(m.group(1))
            in_header = False
            continue
        if in_header:
            continue
        if cur_file and line.startswith("+"):
            buf_lines.append(line[1:])
            buf_nums.append(new_line)
            new_line += 1
    flush()
    return findings, {"commits_scanned": commits, "max_commits": max_commits}


def remote_info(root: str) -> dict:
    """Describe git remotes without leaking embedded credentials."""
    info = {"is_git_repo": False, "remotes": [], "github": None, "advice": []}
    if not git_toplevel(root):
        return info
    info["is_git_repo"] = True
    try:
        r = _git(root, "remote", "-v")
    except (OSError, subprocess.SubprocessError):
        return info
    seen = set()
    for line in r.stdout.decode("utf-8", "replace").splitlines():
        parts = line.split()
        if len(parts) < 2 or (parts[0], parts[1]) in seen:
            continue
        seen.add((parts[0], parts[1]))
        url = parts[1]
        has_creds = bool(re.match(r"^[a-z+]+://[^/@]+:[^/@]+@", url))
        safe = re.sub(r"^([a-z+]+://)[^/@]+@", r"\1***@", url)
        entry = {"name": parts[0], "url": safe, "credentials_in_url": has_creds}
        m = re.search(r"github\.com[:/]+([^/\s]+)/([^/\s]+?)(?:\.git)?/?$", url)
        if m:
            slug = f"{m.group(1)}/{m.group(2)}"
            entry["github_repo"] = slug
            info["github"] = slug
        info["remotes"].append(entry)
        if has_creds:
            info["advice"].append(
                f"Remote '{parts[0]}' embeds credentials in .git/config; switch to a credential helper.")
    if info["github"]:
        slug = info["github"]
        info["advice"].append(
            f"Remote is GitHub ({slug}). Check visibility: open https://github.com/{slug} in a "
            f"logged-out browser window, or run `gh repo view {slug} --json visibility`. "
            "If it is public, treat every secret found (including history) as compromised.")
    return info


def summarize(findings: List[dict], registry: SecretRegistry) -> dict:
    """Aggregate counts by severity, rule and file."""
    by_sev: Dict[str, int] = {}
    by_rule: Dict[str, int] = {}
    by_file: Dict[str, int] = {}
    for f in findings:
        by_sev[f["severity"]] = by_sev.get(f["severity"], 0) + 1
        by_rule[f["rule"]] = by_rule.get(f["rule"], 0) + 1
        by_file[f["file"]] = by_file.get(f["file"], 0) + 1
    return {"total": len(findings), "by_severity": by_sev, "by_rule": by_rule,
            "by_file": dict(sorted(by_file.items(), key=lambda kv: -kv[1])),
            "distinct_secret_values": len(registry)}


def run_scan(path: str, git_history: bool = False, max_commits: int = DEFAULT_MAX_COMMITS,
             max_file_size: int = DEFAULT_MAX_FILE_SIZE, ignore_file: Optional[str] = None,
             min_severity: str = "warning") -> dict:
    """Run the full scan and return the JSON-serialisable result."""
    root = os.path.abspath(path)
    registry = SecretRegistry()
    patterns = load_ignore(root, ignore_file)
    tree_findings, stats = scan_tree(root, registry, patterns, max_file_size)
    for f in tree_findings:
        f["source"] = "working_tree"
    hist_findings: List[dict] = []
    hist_stats: Optional[dict] = None
    if git_history:
        hist_findings, hist_stats = scan_history(root, registry, patterns, max_commits)
        present = {(f["secret_id"]) for f in tree_findings if f["secret_id"]}
        for f in hist_findings:
            f["source"] = "git_history"
            f["still_in_working_tree"] = f["secret_id"] in present if f["secret_id"] else None
    threshold = SEVERITY_ORDER.get(min_severity, 0)
    all_findings = [f for f in tree_findings + hist_findings
                    if SEVERITY_ORDER.get(f["severity"], 0) >= threshold]
    removed_only = sorted({f["secret_id"] for f in hist_findings
                           if f["secret_id"] and f.get("still_in_working_tree") is False})
    remote = remote_info(root)
    high = sum(1 for f in all_findings if f["severity"] == "high")
    advice = list(remote["advice"])
    if high:
        advice.insert(0, "Rotate every high-severity credential now (change the SFTP/hosting "
                         "password, revoke tokens); then remove them from files and history "
                         "(git filter-repo or BFG) and force-push.")
    if removed_only:
        advice.append(f"{len(removed_only)} secret value(s) exist only in git history: deleting "
                      "the file did not remove them from the repository.")
    return {
        "tool": "secret_scan",
        "scanned_path": root,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "git_history": git_history,
        "stats": {**stats, **({"history": hist_stats} if hist_stats else {})},
        "remote": {k: v for k, v in remote.items() if k != "advice"},
        "summary": summarize(all_findings, registry),
        "secrets_only_in_history": removed_only,
        "findings": all_findings,
        "advice": advice,
        "exit_code": 1 if high else 0,
    }


def format_text(res: dict) -> str:
    """Human-readable summary (still masked)."""
    s = res["summary"]
    lines = [f"Secret scan: {res['scanned_path']}",
             f"Findings: {s['total']} {s['by_severity']} | distinct values: {s['distinct_secret_values']}"]
    if res["git_history"]:
        lines.append(f"History: {res['stats'].get('history')}")
    for f in res["findings"]:
        where = f"{f['file']}:{f['line']}"
        if f.get("commit"):
            where += f" @ {f['commit']}"
        lines.append(f"  [{f['severity']:<7}] {f['rule']:<30} {where}  {f.get('masked_value') or ''} "
                     f"{f.get('secret_id') or ''}")
    for a in res["advice"]:
        lines.append(f"! {a}")
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Scan a site repository for committed credentials.")
    parser.add_argument("path", help="Directory to scan")
    parser.add_argument("--git-history", action="store_true",
                        help="Also scan every commit reachable from any ref (git log -p --all)")
    parser.add_argument("--max-commits", type=int, default=DEFAULT_MAX_COMMITS,
                        help=f"Commit limit for --git-history (default {DEFAULT_MAX_COMMITS})")
    parser.add_argument("--max-file-size", type=int, default=DEFAULT_MAX_FILE_SIZE,
                        help="Skip files larger than this many bytes (default 1 MB)")
    parser.add_argument("--ignore-file", help="Extra ignore-glob file (in addition to .secretscanignore)")
    parser.add_argument("--min-severity", choices=list(SEVERITY_ORDER), default="warning",
                        help="Drop findings below this severity")
    parser.add_argument("--text", action="store_true", help="Human-readable output instead of JSON")
    args = parser.parse_args(argv)

    if not os.path.isdir(args.path):
        print(json.dumps({"error": f"not a directory: {args.path}"}), file=sys.stderr)
        return 2
    if args.git_history and not git_toplevel(args.path):
        print(json.dumps({"error": "--git-history requires a git repository"}), file=sys.stderr)
        return 2
    res = run_scan(args.path, args.git_history, args.max_commits, args.max_file_size,
                   args.ignore_file, args.min_severity)
    print(format_text(res) if args.text else json.dumps(res, indent=2, ensure_ascii=False))
    return res["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
