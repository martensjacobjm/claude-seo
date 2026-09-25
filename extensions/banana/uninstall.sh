#!/usr/bin/env bash
set -euo pipefail

main() {
    echo "→ Uninstalling Banana Image Generation extension..."

    # Remove skill (includes copied scripts and references)
    rm -rf "${HOME}/.claude/skills/seo-image-gen"

    # Remove agent
    rm -f "${HOME}/.claude/agents/seo-image-gen.md"

    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    MCP_HELPER=""
    for candidate in "${SCRIPT_DIR}/../claude_mcp_config.py" "${SCRIPT_DIR}/extensions/claude_mcp_config.py"; do
        if [ -f "${candidate}" ]; then MCP_HELPER="${candidate}"; break; fi
    done
    # Keep the MCP server if the standalone banana skill still uses it
    if [ -d "${HOME}/.claude/skills/banana" ]; then
        echo "  ℹ  Standalone banana skill detected at ~/.claude/skills/banana/"
        echo "  ℹ  Keeping the nanobanana-mcp server registration (used by standalone skill)"
    else
        # Unregister the MCP server: `claude mcp remove nanobanana-mcp --scope user` (or
        # ~/.claude.json directly without the CLI), plus the legacy entry that
        # installers up to v1.8.1 wrote to ~/.claude/settings.json.
        if [ -n "${MCP_HELPER}" ] && command -v python3 >/dev/null 2>&1; then
            python3 "${MCP_HELPER}" uninstall --name nanobanana-mcp || \
                echo "  ⚠  Could not unregister the MCP server. Run: claude mcp remove nanobanana-mcp --scope user"
        elif command -v claude >/dev/null 2>&1; then
            claude mcp remove nanobanana-mcp --scope user >/dev/null 2>&1 || true
            echo "  Ran: claude mcp remove 'nanobanana-mcp' --scope user. Also delete any mcpServers.nanobanana-mcp"
            echo "  entry from ~/.claude/settings.json by hand (old installers wrote one there)."
        else
            echo "  ⚠  Could not unregister the MCP server. Run: claude mcp remove nanobanana-mcp --scope user"
        fi
    fi

    echo "✓ Banana Image Generation extension uninstalled."
}

main "$@"
