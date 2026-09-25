#!/usr/bin/env bash
set -euo pipefail

echo "Removing Firecrawl extension..."

# Remove skill directory
rm -rf "${HOME}/.claude/skills/seo-firecrawl"
echo "v Removed skill files"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MCP_HELPER=""
for candidate in "${SCRIPT_DIR}/../claude_mcp_config.py" "${SCRIPT_DIR}/extensions/claude_mcp_config.py"; do
    if [ -f "${candidate}" ]; then MCP_HELPER="${candidate}"; break; fi
done

# Unregister the MCP server: `claude mcp remove firecrawl-mcp --scope user` (or
# ~/.claude.json directly without the CLI), plus the legacy entry that
# installers up to v1.8.1 wrote to ~/.claude/settings.json.
if [ -n "${MCP_HELPER}" ] && command -v python3 >/dev/null 2>&1; then
    python3 "${MCP_HELPER}" uninstall --name firecrawl-mcp || \
        echo "  Warning: Could not unregister the MCP server. Run: claude mcp remove firecrawl-mcp --scope user"
elif command -v claude >/dev/null 2>&1; then
    claude mcp remove firecrawl-mcp --scope user >/dev/null 2>&1 || true
    echo "  Ran: claude mcp remove 'firecrawl-mcp' --scope user. Also delete any mcpServers.firecrawl-mcp"
    echo "  entry from ~/.claude/settings.json by hand (old installers wrote one there)."
else
    echo "  Warning: Could not unregister the MCP server. Run: claude mcp remove firecrawl-mcp --scope user"
fi

echo ""
echo "v Firecrawl extension uninstalled."
echo "  Core Claude SEO skills are unchanged."
