#!/usr/bin/env python3
"""
Validate that the Claude Banana MCP server is properly configured.

Checks:
1. ~/.claude.json has the user-scope MCP entry (Claude Code reads user-scope
   MCP servers from there, never from ~/.claude/settings.json)
2. API key is present
3. Node.js/npx is available
4. Output directory exists or can be created

Usage:
    python3 validate_setup.py
"""

import json
import shutil
import sys
from pathlib import Path

SETTINGS_PATH = Path.home() / ".claude.json"  # user-scope MCP servers live here
LEGACY_SETTINGS_PATH = Path.home() / ".claude" / "settings.json"
MCP_NAME = "nanobanana-mcp"
OUTPUT_DIR = Path.home() / "Documents" / "nanobanana_generated"


def check(label: str, passed: bool, detail: str = "") -> bool:
    status = "PASS" if passed else "FAIL"
    msg = f"  [{status}] {label}"
    if detail:
        msg += f": {detail}"
    print(msg)
    return passed


def main() -> int:
    print("Claude Banana - Setup Validation")
    print("=" * 40)
    results = []

    # 1. Settings file exists
    results.append(check(
        "Claude Code user config ~/.claude.json exists",
        SETTINGS_PATH.exists(),
        str(SETTINGS_PATH),
    ))

    if not SETTINGS_PATH.exists():
        print("\nCannot continue without ~/.claude.json. Register the server with:")
        print("  claude mcp add --env GOOGLE_AI_API_KEY=<key> --transport stdio --scope user "
              "nanobanana-mcp -- npx -y @ycse/nanobanana-mcp@latest")
        return 1

    # 2. Load and parse settings
    try:
        with open(SETTINGS_PATH) as f:
            settings = json.load(f)
        results.append(check("~/.claude.json is valid JSON", True))
    except json.JSONDecodeError as e:
        results.append(check("~/.claude.json is valid JSON", False, str(e)))
        return 1

    # 3. MCP entry exists
    servers = settings.get("mcpServers", {})
    has_mcp = MCP_NAME in servers
    results.append(check(f"MCP server '{MCP_NAME}' registered at user scope", has_mcp))
    if not has_mcp:
        try:
            legacy = json.loads(LEGACY_SETTINGS_PATH.read_text()).get("mcpServers", {})
        except (OSError, ValueError, AttributeError):
            legacy = {}
        if isinstance(legacy, dict) and MCP_NAME in legacy:
            print(f"  [INFO] '{MCP_NAME}' is only in {LEGACY_SETTINGS_PATH}, which Claude Code "
                  "does not read MCP servers from. Rerun the banana installer or setup_mcp.py.")

    if has_mcp:
        mcp = servers[MCP_NAME]

        # 4. Command is npx
        results.append(check(
            "Command is 'npx'",
            mcp.get("command") == "npx",
            mcp.get("command", "(missing)"),
        ))

        # 5. Package is correct
        args = mcp.get("args", [])
        has_pkg = any(a == "@ycse/nanobanana-mcp" or a.startswith("@ycse/nanobanana-mcp@")
                      for a in args if isinstance(a, str))
        results.append(check(
            "Package is @ycse/nanobanana-mcp",
            has_pkg,
            str(args),
        ))

        # 6. API key present
        env = mcp.get("env", {})
        key = env.get("GOOGLE_AI_API_KEY", "")
        results.append(check(
            "GOOGLE_AI_API_KEY is set",
            bool(key),
            f"...{key[-4:]}" if len(key) > 12 else "(empty or short)",
        ))

        # 7. Model configured (optional: the package has a default)
        model = env.get("NANOBANANA_MODEL", "")
        results.append(check(
            "NANOBANANA_MODEL",
            True,
            model or "(not set, will use package default)",
        ))

    # 8. Node.js/npx available
    has_npx = shutil.which("npx") is not None
    results.append(check(
        "npx is available in PATH",
        has_npx,
        shutil.which("npx") or "not found",
    ))

    # 9. Output directory
    if OUTPUT_DIR.exists():
        results.append(check("Output directory exists", True, str(OUTPUT_DIR)))
    else:
        try:
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            results.append(check("Output directory created", True, str(OUTPUT_DIR)))
        except OSError as e:
            results.append(check("Output directory writable", False, str(e)))

    # Summary
    passed = sum(1 for r in results if r)
    total = len(results)
    print(f"\n{'=' * 40}")
    print(f"Results: {passed}/{total} checks passed")

    if passed == total:
        print("Status: Ready to generate images!")
        return 0
    else:
        print("Status: Some checks failed. Fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
