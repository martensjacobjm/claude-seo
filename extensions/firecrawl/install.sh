#!/usr/bin/env bash
set -euo pipefail

# Firecrawl Extension Installer for Claude SEO
# Wraps everything in main() to prevent partial execution on network failure

main() {
    SKILL_DIR="${HOME}/.claude/skills/seo-firecrawl"
    AGENT_DIR="${HOME}/.claude/agents"
    SEO_SKILL_DIR="${HOME}/.claude/skills/seo"

    echo "════════════════════════════════════════"
    echo "║   Firecrawl Extension - Installer    ║"
    echo "║   For Claude SEO                     ║"
    echo "════════════════════════════════════════"
    echo ""

    # Check prerequisites
    if [ ! -d "${SEO_SKILL_DIR}" ]; then
        echo "x Claude SEO is not installed."
        echo "  Install it first: curl -fsSL https://raw.githubusercontent.com/AgriciDaniel/claude-seo/main/install.sh | bash"
        exit 1
    fi
    echo "v Claude SEO detected"

    if ! command -v node >/dev/null 2>&1; then
        echo "x Node.js is required but not installed."
        echo "  Install Node.js 20+: https://nodejs.org/"
        exit 1
    fi

    NODE_VERSION=$(node -v | sed 's/v//' | cut -d. -f1)
    if [ "${NODE_VERSION}" -lt 20 ]; then
        echo "x Node.js 20+ required (found v${NODE_VERSION})."
        echo "  Update: https://nodejs.org/"
        exit 1
    fi
    echo "v Node.js v$(node -v | sed 's/v//') detected"

    if ! command -v npx >/dev/null 2>&1; then
        echo "x npx is required but not found (comes with npm)."
        exit 1
    fi
    echo "v npx detected"

    # python3 runs the shared MCP registration helper (extensions/claude_mcp_config.py)
    if ! command -v python3 >/dev/null 2>&1; then
        echo "x python3 is required to register the MCP server."
        exit 1
    fi
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    MCP_HELPER=""
    for candidate in "${SCRIPT_DIR}/../claude_mcp_config.py" "${SCRIPT_DIR}/extensions/claude_mcp_config.py"; do
        if [ -f "${candidate}" ]; then MCP_HELPER="${candidate}"; break; fi
    done
    if [ -z "${MCP_HELPER}" ]; then
        echo "x Cannot find extensions/claude_mcp_config.py."
        echo "  Run this script from the claude-seo repo: ./extensions/firecrawl/install.sh"
        exit 1
    fi
    if command -v claude >/dev/null 2>&1; then
        echo "v claude CLI detected (MCP server will be added with: claude mcp add --scope user)"
    else
        echo "i claude CLI not on PATH: the MCP server will be written to ~/.claude.json directly"
    fi

    # Prompt for credentials
    echo ""
    echo "Firecrawl API key required."
    echo "Sign up at: https://www.firecrawl.dev/app/sign-up"
    echo "Free tier: 500 credits/month"
    echo ""

    read -rsp "Firecrawl API key: " FIRECRAWL_API_KEY
    echo ""
    if [ -z "${FIRECRAWL_API_KEY}" ]; then
        echo "x API key cannot be empty."
        exit 1
    fi

    # Check if running from repo or standalone
    if [ -f "${SCRIPT_DIR}/skills/seo-firecrawl/SKILL.md" ]; then
        SOURCE_DIR="${SCRIPT_DIR}"
    elif [ -f "${SCRIPT_DIR}/extensions/firecrawl/skills/seo-firecrawl/SKILL.md" ]; then
        SOURCE_DIR="${SCRIPT_DIR}/extensions/firecrawl"
    else
        echo "x Cannot find extension source files."
        echo "  Run this script from the claude-seo repo: ./extensions/firecrawl/install.sh"
        exit 1
    fi

    # Install skill
    echo ""
    echo "-> Installing Firecrawl skill..."
    mkdir -p "${SKILL_DIR}"
    cp "${SOURCE_DIR}/skills/seo-firecrawl/SKILL.md" "${SKILL_DIR}/SKILL.md"

    # Register the MCP server at user scope. Claude Code reads user-scope MCP
    # servers from ~/.claude.json (via `claude mcp add --scope user`), never
    # from ~/.claude/settings.json, where installers up to v1.8.1 wrote them.
    echo "-> Registering MCP server (user scope)..."

    # The API key reaches the helper through the environment only: never argv,
    # never string interpolation into code, never echoed.
    FIRECRAWL_API_KEY="${FIRECRAWL_API_KEY}" \
    python3 "${MCP_HELPER}" install --name firecrawl-mcp \
        --env-keys FIRECRAWL_API_KEY --secret-keys FIRECRAWL_API_KEY \
        -- npx -y firecrawl-mcp || {
        echo "  Warning: Could not register the MCP server automatically. Run:"
        echo "     claude mcp add --env FIRECRAWL_API_KEY=<key> --transport stdio --scope user \\"
        echo "       firecrawl-mcp -- npx -y firecrawl-mcp"
        echo "  See: extensions/firecrawl/docs/FIRECRAWL-SETUP.md"
    }
    unset FIRECRAWL_API_KEY

    # Pre-warm npx package
    echo "-> Pre-downloading firecrawl-mcp..."
    npx -y firecrawl-mcp --help >/dev/null 2>&1 || true

    echo ""
    echo "v Firecrawl extension installed successfully!"
    echo ""
    echo "Usage:"
    echo "  1. Start Claude Code:  claude"
    echo "  2. Run commands:"
    echo "     /seo firecrawl crawl https://example.com"
    echo "     /seo firecrawl map https://example.com"
    echo "     /seo firecrawl scrape https://example.com/page"
    echo "     /seo firecrawl search \"query\" https://example.com"
    echo ""
    echo "Documentation: extensions/firecrawl/README.md"
    echo "To uninstall: ./extensions/firecrawl/uninstall.sh"
}

main "$@"
