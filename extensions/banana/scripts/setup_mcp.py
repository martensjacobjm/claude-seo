#!/usr/bin/env python3
"""
Setup script for Claude Banana MCP server in Claude Code.

Registers @ycse/nanobanana-mcp as a user-scope MCP server with the user's
Google AI API key. Claude Code reads user-scope MCP servers from
~/.claude.json (written by `claude mcp add --scope user`); it never reads
`mcpServers` from ~/.claude/settings.json, where older versions of this
script wrote them (https://code.claude.com/docs/en/mcp).

With the `claude` CLI on PATH this runs `claude mcp remove nanobanana-mcp
--scope user` and `claude mcp add ... --scope user`. Without it, the entry is
merged into the top-level `mcpServers` of ~/.claude.json (backup first, other
keys untouched). A legacy settings.json entry is removed (backup first).

Usage:
    python3 setup_mcp.py                    # Interactive (prompts for key, hidden)
    GOOGLE_AI_API_KEY=... python3 setup_mcp.py   # Non-interactive
    python3 setup_mcp.py --key YOUR_KEY     # Non-interactive (key lands in shell history)
    python3 setup_mcp.py --check            # Verify existing setup
    python3 setup_mcp.py --remove           # Remove MCP config
    python3 setup_mcp.py --json             # Add to any command: JSON summary on the last line
    python3 setup_mcp.py --help             # Show usage
"""

import getpass
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import time
from pathlib import Path

USER_CONFIG_PATH = Path.home() / ".claude.json"
LEGACY_SETTINGS_PATH = Path.home() / ".claude" / "settings.json"
MCP_NAME = "nanobanana-mcp"
MCP_PACKAGE = "@ycse/nanobanana-mcp"
MCP_COMMAND = ["npx", "-y", MCP_PACKAGE + "@latest"]
DEFAULT_MODEL = "gemini-3.1-flash-image-preview"


def load_json(path: Path) -> dict:
    """Load a JSON object; {} for a missing or empty file. Raises ValueError on bad JSON."""
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        return {}
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError(f"{path} does not contain a JSON object")
    return data


def backup(path: Path):
    """Copy path to path.claude-seo-backup-<timestamp> with owner-only permissions."""
    if not path.exists():
        return None
    dest = Path(f"{path}.claude-seo-backup-{time.strftime('%Y%m%d-%H%M%S')}")
    n = 1
    while dest.exists():
        n += 1
        dest = Path(f"{path}.claude-seo-backup-{time.strftime('%Y%m%d-%H%M%S')}-{n}")
    shutil.copy2(path, dest)
    try:
        os.chmod(dest, 0o600)
    except OSError:
        pass
    return dest


def save_json(path: Path, data: dict) -> None:
    """Atomic write that keeps the original file mode (0600 for new files)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o600
    fd, tmp = tempfile.mkstemp(prefix=".claude-seo-", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
        os.chmod(tmp, mode)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def find_claude():
    """The `claude` CLI, skipping Windows .cmd/.bat shims (cmd.exe re-parses secrets)."""
    path = shutil.which("claude")
    if path and os.name == "nt" and path.lower().endswith((".cmd", ".bat")):
        return None
    return path


def run_claude(argv, secret=""):
    try:
        proc = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              stdin=subprocess.DEVNULL, timeout=120)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 127, str(exc)
    out = proc.stdout.decode("utf-8", "replace").strip()
    if secret:
        out = out.replace(secret, "****")
    return proc.returncode, out


def user_entry():
    servers = load_json(USER_CONFIG_PATH).get("mcpServers")
    if isinstance(servers, dict) and isinstance(servers.get(MCP_NAME), dict):
        return servers[MCP_NAME]
    return None


def legacy_entry():
    try:
        servers = load_json(LEGACY_SETTINGS_PATH).get("mcpServers")
    except (ValueError, OSError):
        return None
    if isinstance(servers, dict) and isinstance(servers.get(MCP_NAME), dict):
        return servers[MCP_NAME]
    return None


def remove_legacy() -> bool:
    """Remove mcpServers.nanobanana-mcp from ~/.claude/settings.json (backup first)."""
    if legacy_entry() is None:
        return False
    settings = load_json(LEGACY_SETTINGS_PATH)
    saved = backup(LEGACY_SETTINGS_PATH)
    del settings["mcpServers"][MCP_NAME]
    if not settings["mcpServers"]:
        del settings["mcpServers"]
    save_json(LEGACY_SETTINGS_PATH, settings)
    print(f"Removed legacy '{MCP_NAME}' entry from {LEGACY_SETTINGS_PATH} "
          f"(Claude Code never loaded it from there). Backup: {saved}")
    return True


def mask(key: str) -> str:
    return "..." + key[-4:] if len(key) > 12 else "(set)" if key else "(not set)"


def check_setup() -> dict:
    """Check if MCP is registered at user scope."""
    entry = user_entry()
    legacy = legacy_entry() is not None
    if entry is not None:
        env = entry.get("env", {}) or {}
        print(f"MCP server '{MCP_NAME}' is registered at user scope in {USER_CONFIG_PATH}.")
        print(f"  Command: {' '.join([entry.get('command', '')] + list(entry.get('args', [])))}")
        print(f"  API Key: {mask(env.get('GOOGLE_AI_API_KEY', ''))}")
        print(f"  Model:   {env.get('NANOBANANA_MODEL', DEFAULT_MODEL)}")
    else:
        print(f"MCP server '{MCP_NAME}' is NOT registered at user scope ({USER_CONFIG_PATH}).")
    if legacy:
        print(f"  Note: a legacy entry exists in {LEGACY_SETTINGS_PATH}; Claude Code ignores it."
              " Run this script again (without --check) to migrate it.")
    return {"registered": entry is not None, "legacy_entry": legacy}


def remove_mcp() -> dict:
    """Remove the user-scope registration and any legacy entry."""
    method = []
    claude = find_claude()
    if claude:
        code, _ = run_claude([claude, "mcp", "remove", MCP_NAME, "--scope", "user"])
        if code == 0:
            method.append("claude-cli")
            print(f"Ran: claude mcp remove {MCP_NAME} --scope user")
    if user_entry() is not None:
        cfg = load_json(USER_CONFIG_PATH)
        saved = backup(USER_CONFIG_PATH)
        del cfg["mcpServers"][MCP_NAME]
        save_json(USER_CONFIG_PATH, cfg)
        method.append("file")
        print(f"Removed '{MCP_NAME}' from {USER_CONFIG_PATH} (backup: {saved})")
    legacy = remove_legacy()
    if not method and not legacy:
        print(f"'{MCP_NAME}' is not registered.")
    return {"removed": method, "legacy_removed": legacy}


def setup_mcp(api_key: str) -> dict:
    """Register the MCP server at user scope."""
    if not api_key or not api_key.strip():
        print("Error: API key cannot be empty.")
        sys.exit(1)
    api_key = api_key.strip()
    env = {"GOOGLE_AI_API_KEY": api_key, "NANOBANANA_MODEL": DEFAULT_MODEL}

    method = None
    claude = find_claude()
    if claude:
        run_claude([claude, "mcp", "remove", MCP_NAME, "--scope", "user"])
        argv = [claude, "mcp", "add"]
        for k, v in env.items():
            argv += ["--env", f"{k}={v}"]
        # --env is variadic: another option must precede the server name.
        argv += ["--transport", "stdio", "--scope", "user", MCP_NAME, "--"] + MCP_COMMAND
        code, out = run_claude(argv, api_key)
        if code == 0:
            method = "claude-cli"
            print(f"Registered '{MCP_NAME}' with: claude mcp add --scope user")
        else:
            print(f"`claude mcp add` failed (exit {code}): {out}")
    if method is None:
        cfg = load_json(USER_CONFIG_PATH)
        servers = cfg.setdefault("mcpServers", {})
        if not isinstance(servers, dict):
            raise ValueError(f"{USER_CONFIG_PATH}: mcpServers is not an object")
        saved = backup(USER_CONFIG_PATH)
        servers[MCP_NAME] = {"type": "stdio", "command": MCP_COMMAND[0],
                             "args": MCP_COMMAND[1:], "env": env}
        save_json(USER_CONFIG_PATH, cfg)
        method = "file"
        print(f"Registered '{MCP_NAME}' in {USER_CONFIG_PATH}"
              + (f" (backup: {saved})" if saved else ""))
        print("Equivalent command: claude mcp add --env GOOGLE_AI_API_KEY=<key> "
              f"--env NANOBANANA_MODEL={DEFAULT_MODEL} --transport stdio --scope user "
              f"{MCP_NAME} -- {' '.join(MCP_COMMAND)}")
    legacy = remove_legacy()

    print(f"\nMCP server '{MCP_NAME}' configured successfully!")
    print(f"  Package: {MCP_PACKAGE}")
    print(f"  Model:   {DEFAULT_MODEL}")
    print("\nRestart Claude Code for changes to take effect.")
    print("Generated images will be saved to: ~/Documents/nanobanana_generated/")
    return {"method": method, "legacy_removed": legacy}


def main() -> None:
    args = sys.argv[1:]
    as_json = "--json" in args

    if "--help" in args or "-h" in args:
        print("Usage: python3 setup_mcp.py [OPTIONS]")
        print()
        print("Options:")
        print("  --key KEY        Provide API key non-interactively (prefer GOOGLE_AI_API_KEY env)")
        print("  --check          Verify existing setup")
        print("  --remove         Remove MCP configuration")
        print("  --json           Print a JSON summary on the last line")
        print("  --help, -h       Show this help message")
        print()
        print("Get a free API key at: https://aistudio.google.com/apikey")
        sys.exit(0)

    try:
        if "--check" in args:
            result = check_setup()
        elif "--remove" in args:
            result = remove_mcp()
        else:
            api_key = None
            for i, arg in enumerate(args):
                if arg == "--key" and i + 1 < len(args):
                    api_key = args[i + 1]
                    break
            if not api_key:
                api_key = os.environ.get("GOOGLE_AI_API_KEY")
            if not api_key:
                print("Claude Banana - MCP Setup")
                print("=" * 40)
                print("\nGet your free API key at: https://aistudio.google.com/apikey")
                print()
                try:
                    api_key = getpass.getpass("Enter your Google AI API key: ")
                except (EOFError, KeyboardInterrupt):
                    print("\nError: No input received. Provide a key with --key or set GOOGLE_AI_API_KEY env var.")
                    sys.exit(1)
            result = setup_mcp(api_key)
    except (ValueError, OSError) as exc:
        print(f"Error: {exc}")
        if as_json:
            print(json.dumps({"status": "error", "error": str(exc)}))
        sys.exit(1)
    if as_json:
        print(json.dumps(dict(status="ok", name=MCP_NAME, **result)))


if __name__ == "__main__":
    main()
