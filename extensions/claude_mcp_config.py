#!/usr/bin/env python3
"""Register, unregister and migrate Claude SEO extension MCP servers.

Shared helper for the extension installers (extensions/*/install.sh|ps1 and
uninstall.sh|ps1). Claude Code reads user-scope MCP servers from
``~/.claude.json`` (top-level ``mcpServers``) and project-scope servers from
``.mcp.json``. It does NOT read ``mcpServers`` from ``~/.claude/settings.json``,
which is where installers up to v1.8.1 wrote them, so those servers never
loaded. See https://code.claude.com/docs/en/mcp.

Commands:

  install    Register a stdio server at user scope. With the ``claude`` CLI on
             PATH this runs ``claude mcp remove <name> --scope user`` (errors
             ignored, so reinstall is idempotent) and then
             ``claude mcp add --env K=V ... --transport stdio --scope user
             <name> -- <command> <args...>``. Without the CLI (or if it fails)
             the server is merged into ~/.claude.json directly (backup first,
             other keys untouched, atomic write) and the equivalent
             ``claude mcp add`` command is printed with secrets masked.
             Finally the legacy settings.json entry is removed.
  uninstall  ``claude mcp remove <name> --scope user`` when the CLI exists,
             then removes any remaining top-level entry from ~/.claude.json and
             the legacy settings.json entry.
  remove-legacy
             Only remove the legacy settings.json entry (backup first).
  status     Exit 0 when <name> is registered at user scope in ~/.claude.json,
             1 otherwise. Prints nothing.
  has-legacy Exit 0 when ~/.claude/settings.json holds a legacy
             ``mcpServers.<name>`` entry that has every ``--env-keys`` value.

Secrets never travel through argv of this script or through a shell string:
the installer exports them as environment variables and names them with
``--env-keys``; this script reads them from its own environment. Values listed
in ``--secret-keys`` are never printed. ``--reuse-legacy`` fills env keys that
are unset from the legacy settings.json entry (so a user migrating from an old
install does not have to re-enter a key).

Usage:
  DATAFORSEO_LOGIN=... DATAFORSEO_PASSWORD=... FIELD_CONFIG_PATH=... \\
    python3 claude_mcp_config.py install --name dataforseo \\
      --env-keys DATAFORSEO_LOGIN,DATAFORSEO_PASSWORD,FIELD_CONFIG_PATH \\
      --secret-keys DATAFORSEO_PASSWORD -- npx -y dataforseo-mcp-server@3
  python3 claude_mcp_config.py uninstall --name dataforseo
  python3 claude_mcp_config.py status --name nanobanana-mcp

Add ``--json`` for a machine-readable JSON summary on the last line.
Exit codes: 0 success, 1 not registered (status/has-legacy), 2 error.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import time

CLI_TIMEOUT = 120


def home_dir():
    return os.path.expanduser("~")


def user_config_path():
    """~/.claude.json: where Claude Code keeps user-scope MCP servers."""
    return os.path.join(home_dir(), ".claude.json")


def legacy_settings_path():
    """~/.claude/settings.json: where old installers wrongly wrote mcpServers."""
    return os.path.join(home_dir(), ".claude", "settings.json")


class ConfigError(Exception):
    pass


def say(msg):
    print(msg, flush=True)


def load_json(path):
    """Return the parsed object, {} for a missing/empty file; raise on bad JSON."""
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()
    if not text.strip():
        return {}
    try:
        data = json.loads(text)
    except ValueError as exc:
        raise ConfigError("%s is not valid JSON (%s); left untouched" % (path, exc))
    if not isinstance(data, dict):
        raise ConfigError("%s does not contain a JSON object; left untouched" % path)
    return data


def backup(path):
    """Copy path to path.claude-seo-backup-<timestamp> (owner-only perms)."""
    if not os.path.exists(path):
        return None
    dest = "%s.claude-seo-backup-%s" % (path, time.strftime("%Y%m%d-%H%M%S"))
    n = 1
    while os.path.exists(dest):
        n += 1
        dest = "%s.claude-seo-backup-%s-%d" % (path, time.strftime("%Y%m%d-%H%M%S"), n)
    shutil.copy2(path, dest)
    try:
        os.chmod(dest, 0o600)
    except OSError:
        pass
    return dest


def write_json_atomic(path, data):
    """Write JSON via temp file + os.replace, keeping the original file mode."""
    directory = os.path.dirname(path) or "."
    os.makedirs(directory, exist_ok=True)
    mode = 0o600
    if os.path.exists(path):
        mode = stat.S_IMODE(os.stat(path).st_mode)
    fd, tmp = tempfile.mkstemp(prefix=".claude-seo-", suffix=".tmp", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        os.chmod(tmp, mode)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def find_claude():
    """Path of a usable `claude` CLI, or None.

    On Windows an npm `claude.cmd`/`.bat` shim is skipped: batch files re-parse
    their arguments through cmd.exe, so a secret containing `"`, `&`, `^` or
    `%` could be mangled or interpreted. The direct ~/.claude.json merge is
    used instead.
    """
    path = shutil.which("claude")
    if path and os.name == "nt" and path.lower().endswith((".cmd", ".bat")):
        say("  i  Found %s (batch shim); writing ~/.claude.json directly so "
            "secrets are not re-parsed by cmd.exe." % path)
        return None
    return path


def redact(text, secrets):
    for value in secrets:
        if value:
            text = text.replace(value, "****")
    return text


def run_cli(argv, secrets):
    """Run the claude CLI; return (returncode, redacted combined output)."""
    try:
        proc = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              stdin=subprocess.DEVNULL, timeout=CLI_TIMEOUT)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 127, redact(str(exc), secrets)
    out = proc.stdout.decode("utf-8", "replace").strip()
    return proc.returncode, redact(out, secrets)


def indent(text):
    return "\n".join("     " + line for line in text.splitlines())


def shell_quote(arg):
    if arg and all(c.isalnum() or c in "@%+=:,./-_" for c in arg):
        return arg
    return "'" + arg.replace("'", "'\"'\"'") + "'"


def cli_add_argv(name, command, env, claude="claude"):
    argv = [claude, "mcp", "add"]
    for key, value in env.items():
        argv += ["--env", "%s=%s" % (key, value)]
    # Another option must sit between the variadic --env and the server name.
    argv += ["--transport", "stdio", "--scope", "user", name, "--"] + command
    return argv


def equivalent_command(name, command, env, secret_keys):
    shown = {k: ("<%s>" % k if k in secret_keys else v) for k, v in env.items()}
    return " ".join(shell_quote(a) for a in cli_add_argv(name, command, shown))


# ---------------------------------------------------------------- legacy file

def legacy_entry(name):
    path = legacy_settings_path()
    try:
        settings = load_json(path)
    except (ConfigError, OSError):
        return None
    servers = settings.get("mcpServers")
    if isinstance(servers, dict) and isinstance(servers.get(name), dict):
        return servers[name]
    return None


def remove_legacy(name):
    """Drop mcpServers.<name> from ~/.claude/settings.json (backup first)."""
    path = legacy_settings_path()
    if not os.path.exists(path):
        return False
    settings = load_json(path)
    servers = settings.get("mcpServers")
    if not isinstance(servers, dict) or name not in servers:
        return False
    saved = backup(path)
    del servers[name]
    if not servers:
        del settings["mcpServers"]
    write_json_atomic(path, settings)
    say("  ✓ Removed legacy '%s' entry from %s (Claude Code never loaded MCP "
        "servers from that file). Backup: %s" % (name, path, saved))
    return True


# ------------------------------------------------------------ ~/.claude.json

def file_registered(name):
    try:
        cfg = load_json(user_config_path())
    except (ConfigError, OSError):
        return False
    servers = cfg.get("mcpServers")
    return isinstance(servers, dict) and name in servers


def file_add(name, command, env):
    path = user_config_path()
    cfg = load_json(path)
    servers = cfg.get("mcpServers")
    if servers is None:
        servers = cfg["mcpServers"] = {}
    elif not isinstance(servers, dict):
        raise ConfigError("%s: mcpServers is not an object; left untouched" % path)
    saved = backup(path)
    servers[name] = {"type": "stdio", "command": command[0],
                     "args": list(command[1:]), "env": dict(env)}
    write_json_atomic(path, cfg)
    say("  ✓ Registered '%s' at user scope in %s%s" % (
        name, path, " (backup: %s)" % saved if saved else ""))


def file_remove(name):
    path = user_config_path()
    if not os.path.exists(path):
        return False
    cfg = load_json(path)
    servers = cfg.get("mcpServers")
    if not isinstance(servers, dict) or name not in servers:
        return False
    saved = backup(path)
    del servers[name]
    write_json_atomic(path, cfg)
    say("  ✓ Removed '%s' from %s (backup: %s)" % (name, path, saved))
    return True


# ------------------------------------------------------------------ commands

def collect_env(keys, reuse_legacy, name):
    env = {}
    legacy = legacy_entry(name) if reuse_legacy else None
    legacy_env = legacy.get("env", {}) if isinstance(legacy, dict) else {}
    for key in keys:
        value = os.environ.get(key)
        if not value and isinstance(legacy_env, dict):
            value = legacy_env.get(key)
        if not value:
            raise ConfigError("environment variable %s is not set" % key)
        env[key] = value
    return env


def cmd_install(args):
    command = list(args.command)
    if not command:
        raise ConfigError("missing server command after --")
    env = collect_env(args.env_keys, args.reuse_legacy, args.name)
    secrets = [env[k] for k in args.secret_keys if k in env]
    method = None

    claude = find_claude()
    if claude:
        # Idempotent reinstall: drop an existing user-scope entry first.
        run_cli([claude, "mcp", "remove", args.name, "--scope", "user"], secrets)
        code, out = run_cli(cli_add_argv(args.name, command, env, claude), secrets)
        if code == 0:
            method = "claude-cli"
            say("  ✓ Registered '%s' with: claude mcp add --scope user" % args.name)
            if out:
                say(indent(out))
        else:
            say("  ⚠  `claude mcp add` failed (exit %d); writing ~/.claude.json "
                "directly instead." % code)
            if out:
                say(indent(out))

    if method is None:
        if not claude:
            say("  i  No usable `claude` CLI on PATH; writing ~/.claude.json directly.")
            say("     A running Claude Code session can overwrite that file: if the server")
            say("     is missing later (`/mcp`), quit Claude Code and rerun this installer.")
        file_add(args.name, command, env)
        method = "file"
        say("     Equivalent command (fill in the <...> values):")
        say("     " + equivalent_command(args.name, command, env, args.secret_keys))

    migrated = remove_legacy(args.name)
    return {"status": "ok", "name": args.name, "method": method,
            "config": user_config_path(), "legacy_removed": migrated}


def cmd_uninstall(args):
    method = []
    claude = find_claude()
    if claude:
        code, out = run_cli([claude, "mcp", "remove", args.name, "--scope", "user"], [])
        if code == 0:
            method.append("claude-cli")
            say("  ✓ Removed '%s' with: claude mcp remove %s --scope user"
                % (args.name, args.name))
        else:
            say("  i  `claude mcp remove %s --scope user` exited %d "
                "(usually: not registered at user scope)." % (args.name, code))
    # Covers a missing CLI and entries the CLI did not remove.
    if file_remove(args.name):
        method.append("file")
    migrated = remove_legacy(args.name)
    if not method and not migrated:
        say("  ✓ No '%s' MCP server registration found." % args.name)
    return {"status": "ok", "name": args.name, "method": method,
            "legacy_removed": migrated}


def split_keys(value):
    return [k.strip() for k in value.split(",") if k.strip()] if value else []


def main(argv=None):
    # Windows consoles/pipes may use a legacy code page: never crash on ✓/⚠.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(errors="replace")
            except (ValueError, OSError):
                pass
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("action", choices=["install", "uninstall", "remove-legacy", "status", "has-legacy"])
    parser.add_argument("--name", required=True, help="MCP server name")
    parser.add_argument("--env-keys", type=split_keys, default=[],
                        help="comma-separated env vars to pass to the server")
    parser.add_argument("--secret-keys", type=split_keys, default=[],
                        help="comma-separated env vars that must never be printed")
    parser.add_argument("--reuse-legacy", action="store_true",
                        help="fill unset env vars from the legacy settings.json entry")
    parser.add_argument("--json", action="store_true", help="print a JSON summary")
    parser.epilog = "install: append -- <command> [args...] (the server command)"
    argv = list(sys.argv[1:] if argv is None else argv)
    command = []
    if "--" in argv:
        split = argv.index("--")
        argv, command = argv[:split], argv[split + 1:]
    args = parser.parse_args(argv)
    args.command = command

    try:
        if args.action == "status":
            return 0 if file_registered(args.name) else 1
        if args.action == "has-legacy":
            entry = legacy_entry(args.name)
            env = entry.get("env") if isinstance(entry, dict) else None
            ok = isinstance(env, dict) and all(env.get(k) for k in args.env_keys)
            return 0 if ok else 1
        if args.action == "remove-legacy":
            removed = remove_legacy(args.name)
            if args.json:
                print(json.dumps({"status": "ok", "name": args.name, "legacy_removed": removed}))
            return 0
        result = cmd_install(args) if args.action == "install" else cmd_uninstall(args)
    except (ConfigError, OSError) as exc:
        say("  ✗ %s" % exc)
        if args.json:
            print(json.dumps({"status": "error", "name": args.name, "error": str(exc)}))
        return 2
    if args.json:
        print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
