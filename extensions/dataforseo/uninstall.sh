#!/usr/bin/env bash
set -euo pipefail

main() {
    echo "→ Uninstalling DataForSEO extension..."

    # Remove skill
    rm -rf "${HOME}/.claude/skills/seo-dataforseo"

    # Remove agent
    rm -f "${HOME}/.claude/agents/seo-dataforseo.md"

    # Remove field config
    rm -f "${HOME}/.claude/skills/seo/dataforseo-field-config.json"

    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    MCP_HELPER=""
    for candidate in "${SCRIPT_DIR}/../claude_mcp_config.py" "${SCRIPT_DIR}/extensions/claude_mcp_config.py"; do
        if [ -f "${candidate}" ]; then MCP_HELPER="${candidate}"; break; fi
    done

    # Unregister the MCP server: `claude mcp remove dataforseo --scope user` (or
    # ~/.claude.json directly without the CLI), plus the legacy entry that
    # installers up to v1.8.1 wrote to ~/.claude/settings.json.
    if [ -n "${MCP_HELPER}" ] && command -v python3 >/dev/null 2>&1; then
        python3 "${MCP_HELPER}" uninstall --name dataforseo || \
            echo "  ⚠  Could not unregister the MCP server. Run: claude mcp remove dataforseo --scope user"
    elif command -v claude >/dev/null 2>&1; then
        claude mcp remove dataforseo --scope user >/dev/null 2>&1 || true
        echo "  Ran: claude mcp remove 'dataforseo' --scope user. Also delete any mcpServers.dataforseo"
        echo "  entry from ~/.claude/settings.json by hand (old installers wrote one there)."
    else
        echo "  ⚠  Could not unregister the MCP server. Run: claude mcp remove dataforseo --scope user"
    fi

    echo "✓ DataForSEO extension uninstalled."
}

main "$@"
