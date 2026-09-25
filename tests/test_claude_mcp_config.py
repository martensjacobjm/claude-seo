"""Tests for extensions/claude_mcp_config.py and the extension installers.

Claude Code reads user-scope MCP servers from ~/.claude.json, not from
~/.claude/settings.json. These tests run the helper and the bash installers in
a throwaway HOME with stub `node`/`npx` and, where needed, a fake `claude` CLI
that logs its argv. No network access.
"""

import json
import os
import shutil
import stat
import subprocess
import sys

import pytest

from conftest import ROOT

HELPER = os.path.join(ROOT, "extensions", "claude_mcp_config.py")
PASSWORD = 'p"a\'s$s\\w`o\\"rd=1 &x'

pytestmark = pytest.mark.skipif(os.name == "nt", reason="uses POSIX shell stubs")


def _write_exe(path, text):
    with open(path, "w") as fh:
        fh.write(text)
    os.chmod(path, 0o755)


@pytest.fixture
def sandbox(tmp_path):
    home = tmp_path / "home"
    (home / ".claude" / "skills" / "seo").mkdir(parents=True)
    (home / ".claude" / "settings.json").write_text(json.dumps({
        "theme": "dark",
        "mcpServers": {
            "dataforseo": {"command": "npx", "env": {"DATAFORSEO_USERNAME": "old"}},
            "other": {"command": "x"},
        },
    }))
    (home / ".claude.json").write_text(json.dumps({
        "numStartups": 5,
        "projects": {"/p": {"mcpServers": {"loc": {"command": "y"}}}},
        "mcpServers": {"keepme": {"type": "stdio", "command": "z"}},
    }))
    os.chmod(home / ".claude.json", 0o600)
    bindir = tmp_path / "bin"
    bindir.mkdir()
    os.symlink(sys.executable, bindir / "python3")
    _write_exe(bindir / "node", "#!/bin/sh\necho v22.11.0\n")
    _write_exe(bindir / "npx", "#!/bin/sh\nexit 0\n")
    return {"tmp": tmp_path, "home": home, "bin": bindir,
            "env": {"HOME": str(home), "PATH": "%s:/usr/bin:/bin" % bindir,
                    "LANG": "C.UTF-8"}}


def _add_fake_claude(sb):
    log = sb["tmp"] / "claude.log"
    _write_exe(sb["bin"] / "claude",
               "#!%s\nimport json, sys\n"
               "open(%r, 'a').write(json.dumps(sys.argv[1:]) + '\\n')\n"
               "if sys.argv[1:3] == ['mcp', 'remove']: sys.exit(1)\n"
               "print('Added: ' + ' '.join(sys.argv[1:]))\n" % (sys.executable, str(log)))
    return log


def _calls(log):
    return [json.loads(line) for line in log.read_text().splitlines()]


def _run(args, sb, extra_env=None, stdin=""):
    env = dict(sb["env"], **(extra_env or {}))
    return subprocess.run(args, env=env, input=stdin, capture_output=True, text=True,
                          timeout=60)


def _json(path):
    return json.loads(path.read_text())


def test_helper_without_cli_merges_user_config(sandbox):
    res = _run([sys.executable, HELPER, "install", "--name", "dataforseo",
                "--env-keys", "DATAFORSEO_LOGIN,DATAFORSEO_PASSWORD",
                "--secret-keys", "DATAFORSEO_PASSWORD", "--json",
                "--", "npx", "-y", "dataforseo-mcp-server@3"],
               sandbox, {"DATAFORSEO_LOGIN": "me", "DATAFORSEO_PASSWORD": PASSWORD})
    assert res.returncode == 0, res.stdout + res.stderr
    assert PASSWORD not in res.stdout
    assert json.loads(res.stdout.splitlines()[-1])["method"] == "file"
    cfg = _json(sandbox["home"] / ".claude.json")
    assert cfg["numStartups"] == 5 and cfg["projects"]["/p"]["mcpServers"]["loc"]
    assert cfg["mcpServers"]["keepme"] == {"type": "stdio", "command": "z"}
    assert cfg["mcpServers"]["dataforseo"] == {
        "type": "stdio", "command": "npx", "args": ["-y", "dataforseo-mcp-server@3"],
        "env": {"DATAFORSEO_LOGIN": "me", "DATAFORSEO_PASSWORD": PASSWORD}}
    assert stat.S_IMODE(os.stat(sandbox["home"] / ".claude.json").st_mode) == 0o600
    settings = _json(sandbox["home"] / ".claude" / "settings.json")
    assert settings == {"theme": "dark", "mcpServers": {"other": {"command": "x"}}}
    backups = [p.name for p in sandbox["home"].iterdir() if "claude-seo-backup" in p.name]
    assert backups, "~/.claude.json was not backed up"


def test_helper_with_cli_runs_remove_then_add(sandbox):
    log = _add_fake_claude(sandbox)
    res = _run([sys.executable, HELPER, "install", "--name", "firecrawl-mcp",
                "--env-keys", "FIRECRAWL_API_KEY", "--secret-keys", "FIRECRAWL_API_KEY",
                "--", "npx", "-y", "firecrawl-mcp"],
               sandbox, {"FIRECRAWL_API_KEY": PASSWORD})
    assert res.returncode == 0, res.stdout + res.stderr
    assert PASSWORD not in res.stdout  # the fake CLI echoes it; the helper must redact
    assert _calls(log) == [
        ["mcp", "remove", "firecrawl-mcp", "--scope", "user"],
        ["mcp", "add", "--env", "FIRECRAWL_API_KEY=" + PASSWORD, "--transport", "stdio",
         "--scope", "user", "firecrawl-mcp", "--", "npx", "-y", "firecrawl-mcp"],
    ]
    assert "firecrawl-mcp" not in _json(sandbox["home"] / ".claude.json")["mcpServers"]


def test_helper_refuses_to_touch_invalid_json(sandbox):
    (sandbox["home"] / ".claude.json").write_text("{broken")
    res = _run([sys.executable, HELPER, "install", "--name", "x", "--env-keys", "K",
                "--", "npx"], sandbox, {"K": "v"})
    assert res.returncode == 2
    assert (sandbox["home"] / ".claude.json").read_text() == "{broken"


@pytest.mark.skipif(shutil.which("bash") is None, reason="bash not available")
@pytest.mark.parametrize("with_cli", [True, False])
def test_dataforseo_install_and_uninstall(sandbox, with_cli):
    log = _add_fake_claude(sandbox) if with_cli else None
    script = os.path.join(ROOT, "extensions", "dataforseo", "install.sh")
    for _ in range(2):  # reinstall must be idempotent
        res = _run(["bash", script], sandbox, stdin='my"login\n%s\n' % PASSWORD)
        assert res.returncode == 0, res.stdout + res.stderr
        assert PASSWORD not in res.stdout + res.stderr
    field_config = str(sandbox["home"] / ".claude" / "skills" / "seo"
                       / "dataforseo-field-config.json")
    env = {"DATAFORSEO_LOGIN": 'my"login', "DATAFORSEO_PASSWORD": PASSWORD,
           "FIELD_CONFIG_PATH": field_config}
    if with_cli:
        add = ["mcp", "add"]
        for key, value in env.items():
            add += ["--env", "%s=%s" % (key, value)]
        add += ["--transport", "stdio", "--scope", "user", "dataforseo", "--",
                "npx", "-y", "dataforseo-mcp-server@3"]
        assert _calls(log) == [["mcp", "remove", "dataforseo", "--scope", "user"], add] * 2
    else:
        entry = _json(sandbox["home"] / ".claude.json")["mcpServers"]["dataforseo"]
        assert entry["args"] == ["-y", "dataforseo-mcp-server@3"] and entry["env"] == env
    assert "dataforseo" not in _json(sandbox["home"] / ".claude" / "settings.json")["mcpServers"]

    res = _run(["bash", os.path.join(ROOT, "extensions", "dataforseo", "uninstall.sh")], sandbox)
    assert res.returncode == 0, res.stdout + res.stderr
    cfg = _json(sandbox["home"] / ".claude.json")
    assert sorted(cfg["mcpServers"]) == ["keepme"] and cfg["numStartups"] == 5
    if with_cli:
        assert _calls(log)[-1] == ["mcp", "remove", "dataforseo", "--scope", "user"]
    assert not (sandbox["home"] / ".claude" / "skills" / "seo-dataforseo").exists()
