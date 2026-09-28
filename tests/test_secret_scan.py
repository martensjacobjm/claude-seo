"""Tests for scripts/secret_scan.py (offline; fixture repo built in tmp)."""

import json
import os
import subprocess
import sys

import pytest

import secret_scan as ss
from conftest import ROOT

SCRIPT = os.path.join(ROOT, "scripts", "secret_scan.py")
# Built at runtime so this file never contains a realistic-looking secret.
PASSWORD = "Fl" + "ytt" + "Salen" + "2025" + "!q"
GH_TOKEN = "gh" + "p_" + "Zx81" * 9
GOOGLE_KEY = "AI" + "za" + "Sy" + "B" * 33


def _git(repo, *args, env=None):
    base = ["git", "-C", str(repo), "-c", "user.name=Test", "-c", "user.email=test@example.com",
            "-c", "commit.gpgsign=false", "-c", "init.defaultBranch=main"]
    subprocess.run(base + list(args), check=True, capture_output=True, env=env)


@pytest.fixture
def repo(tmp_path):
    r = tmp_path / "site"
    r.mkdir()
    _git(r, "init", "-q")
    (r / "upload-to-server.sh").write_text(
        f'#!/bin/sh\nSFTP_USER="webmaster"\nSFTP_PASSWORD="{PASSWORD}"\n'
        'curl -k https://example.com/health\n', encoding="utf-8")
    (r / "index.html").write_text("<html><body>Hej</body></html>", encoding="utf-8")
    _git(r, "add", "-A")
    _git(r, "commit", "-q", "-m", "initial upload")
    # delete the secret in a later commit: it must still be found in history
    (r / "upload-to-server.sh").write_text(
        '#!/bin/sh\nSFTP_PASSWORD="${SFTP_PASSWORD}"\n', encoding="utf-8")
    (r / "README.md").write_text("Password: your_password_here\n", encoding="utf-8")
    _git(r, "add", "-A")
    _git(r, "commit", "-q", "-m", "remove password")
    return r


def test_mask_keeps_only_two_chars_each_side():
    assert ss.mask("abcdefghij") == "ab********ij"
    assert ss.mask("short") == "********"
    assert PASSWORD not in ss.mask(PASSWORD)


def test_known_token_formats_detected():
    reg = ss.SecretRegistry()
    text = (f"token: {GH_TOKEN}\nkey = '{GOOGLE_KEY}'\n"
            "-----BEGIN OPENSSH PRIVATE KEY-----\n"
            "AKIA" + "ABCDEFGHIJKLMNOP\n")
    rules = {f["rule"] for f in ss.scan_text(text, "notes.txt", reg)}
    assert {"github-token", "google-api-key", "private-key-block", "aws-access-key-id"} <= rules


def test_generic_rules_and_placeholders():
    reg = ss.SecretRegistry()
    text = ("set PASS=Hemlig123x\n"
            "password = os.environ['X']\n"
            "password: string\n"
            "bypass = something\n"
            "**Lösenord:** Sommar2025\n"
            "DB=mysql://app:Sommar2025@db.example.com/site\n")
    found = ss.scan_text(text, "deploy.bat", reg)
    lines = sorted(f["line"] for f in found)
    assert lines == [1, 5, 6]
    # same value in two places -> same secret id
    ids = {f["secret_id"] for f in found if f["line"] in (5, 6)}
    assert len(ids) == 1


def test_working_tree_scan_is_clean_but_history_has_secret(repo):
    res = ss.run_scan(str(repo))
    assert not [f for f in res["findings"] if f["severity"] == "high"]
    assert res["exit_code"] == 0

    res = ss.run_scan(str(repo), git_history=True)
    hist = [f for f in res["findings"] if f["source"] == "git_history" and f["severity"] == "high"]
    assert hist, res["findings"]
    f = hist[0]
    assert f["file"] == "upload-to-server.sh" and f["line"] == 3
    assert f["commit"] and f["still_in_working_tree"] is False
    assert f["masked_value"] == PASSWORD[:2] + "*" * 8 + PASSWORD[-2:]
    assert res["secrets_only_in_history"]
    assert res["exit_code"] == 1
    assert any(x["rule"] == "curl-insecure-tls" and x["severity"] == "warning"
               for x in res["findings"])
    # the full secret must never appear anywhere in the output
    assert PASSWORD not in json.dumps(res, ensure_ascii=False)


def test_ignore_file_and_binary_skip(repo):
    vendor = repo / "vendor"
    vendor.mkdir()
    (vendor / "lib.js").write_text(f"const t = '{GH_TOKEN}';\n", encoding="utf-8")
    (repo / "logo.png").write_bytes(b"\x89PNG\x00\x00" + GH_TOKEN.encode())
    (repo / "keep.txt").write_text(f"{GH_TOKEN}\n", encoding="utf-8")
    (repo / ".secretscanignore").write_text("# third party\nvendor/\nkeep.txt\n", encoding="utf-8")
    res = ss.run_scan(str(repo))
    assert not [f for f in res["findings"] if f["rule"] == "github-token"]
    assert res["stats"]["skipped_binary"] == 1
    assert res["stats"]["skipped_ignored"] >= 1


def test_github_remote_reported_without_credentials(repo):
    _git(repo, "remote", "add", "origin", f"https://bot:{GH_TOKEN}@github.com/acme/site.git")
    res = ss.run_scan(str(repo))
    assert res["remote"]["github"] == "acme/site"
    assert res["remote"]["remotes"][0]["credentials_in_url"] is True
    assert GH_TOKEN not in json.dumps(res)
    assert any("visibility" in a for a in res["advice"])


def test_cli_exit_codes(repo, tmp_path):
    out = subprocess.run([sys.executable, SCRIPT, str(repo), "--git-history"],
                         capture_output=True, text=True)
    assert out.returncode == 1
    assert PASSWORD not in out.stdout
    data = json.loads(out.stdout)
    assert data["summary"]["by_severity"]["high"] >= 1
    clean = subprocess.run([sys.executable, SCRIPT, str(repo)], capture_output=True, text=True)
    assert clean.returncode == 0
    missing = subprocess.run([sys.executable, SCRIPT, str(tmp_path / "nope")],
                             capture_output=True, text=True)
    assert missing.returncode == 2
