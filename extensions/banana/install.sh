#!/usr/bin/env bash
set -euo pipefail

# Banana Image Generation Extension Installer for Claude SEO
# Wraps everything in main() to prevent partial execution on network failure

main() {
    SKILL_DIR="${HOME}/.claude/skills/seo-image-gen"
    AGENT_DIR="${HOME}/.claude/agents"
    SEO_SKILL_DIR="${HOME}/.claude/skills/seo"

    echo "════════════════════════════════════════"
    echo "║  Banana Image Gen - SEO Extension    ║"
    echo "║  For Claude SEO                      ║"
    echo "════════════════════════════════════════"
    echo ""

    # Check prerequisites
    if [ ! -d "${SEO_SKILL_DIR}" ]; then
        echo "✗ Claude SEO is not installed."
        echo "  Install it first: curl -fsSL https://raw.githubusercontent.com/AgriciDaniel/claude-seo/main/install.sh | bash"
        exit 1
    fi
    echo "✓ Claude SEO detected"

    if ! command -v node >/dev/null 2>&1; then
        echo "✗ Node.js is required but not installed."
        echo "  Install Node.js 20+: https://nodejs.org/"
        exit 1
    fi

    NODE_VERSION=$(node -v | sed 's/v//' | cut -d. -f1)
    if [ "${NODE_VERSION}" -lt 20 ]; then
        echo "✗ Node.js 20+ required (found v${NODE_VERSION})."
        echo "  Update: https://nodejs.org/"
        exit 1
    fi
    echo "✓ Node.js v$(node -v | sed 's/v//') detected"

    if ! command -v npx >/dev/null 2>&1; then
        echo "✗ npx is required but not found (comes with npm)."
        exit 1
    fi
    echo "✓ npx detected"

    # python3 runs the shared MCP registration helper (extensions/claude_mcp_config.py)
    if ! command -v python3 >/dev/null 2>&1; then
        echo "✗ python3 is required to register the MCP server."
        exit 1
    fi
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    MCP_HELPER=""
    for candidate in "${SCRIPT_DIR}/../claude_mcp_config.py" "${SCRIPT_DIR}/extensions/claude_mcp_config.py"; do
        if [ -f "${candidate}" ]; then MCP_HELPER="${candidate}"; break; fi
    done
    if [ -z "${MCP_HELPER}" ]; then
        echo "✗ Cannot find extensions/claude_mcp_config.py."
        echo "  Run this script from the claude-seo repo: ./extensions/banana/install.sh"
        exit 1
    fi
    if command -v claude >/dev/null 2>&1; then
        echo "✓ claude CLI detected (MCP server will be added with: claude mcp add --scope user)"
    else
        echo "ℹ claude CLI not on PATH: the MCP server will be written to ~/.claude.json directly"
    fi

    # Check if running from repo or standalone
    if [ -f "${SCRIPT_DIR}/skills/seo-image-gen/SKILL.md" ]; then
        SOURCE_DIR="${SCRIPT_DIR}"
    elif [ -f "${SCRIPT_DIR}/extensions/banana/skills/seo-image-gen/SKILL.md" ]; then
        SOURCE_DIR="${SCRIPT_DIR}/extensions/banana"
    else
        echo "✗ Cannot find extension source files."
        echo "  Run this script from the claude-seo repo: ./extensions/banana/install.sh"
        exit 1
    fi

    # Claude Code reads user-scope MCP servers from ~/.claude.json (written by
    # `claude mcp add --scope user`), never from ~/.claude/settings.json, where
    # installers up to v1.8.1 (and older standalone banana installs) wrote them.
    if python3 "${MCP_HELPER}" status --name nanobanana-mcp; then
        echo "✓ nanobanana-mcp already registered at user scope (~/.claude.json)"
        # Only clean up a leftover legacy settings.json entry, if any.
        python3 "${MCP_HELPER}" remove-legacy --name nanobanana-mcp || true
    elif python3 "${MCP_HELPER}" has-legacy --name nanobanana-mcp --env-keys GOOGLE_AI_API_KEY; then
        echo "→ Migrating nanobanana-mcp from ~/.claude/settings.json (never loaded there)..."
        python3 "${MCP_HELPER}" install --name nanobanana-mcp --reuse-legacy \
            --env-keys GOOGLE_AI_API_KEY --secret-keys GOOGLE_AI_API_KEY \
            -- npx -y @ycse/nanobanana-mcp@latest || {
            echo "✗ Could not register the MCP server."
            echo "  See: extensions/banana/docs/BANANA-SETUP.md"
            exit 1
        }
    else
        echo ""
        echo "Google AI API key required for image generation."
        echo "Get a free key at: https://aistudio.google.com/apikey"
        echo ""

        read -rsp "Google AI API key (GOOGLE_AI_API_KEY): " BANANA_API_KEY
        echo ""
        if [ -z "${BANANA_API_KEY}" ]; then
            echo "✗ API key cannot be empty."
            exit 1
        fi

        # The key reaches the helper through the environment only: never argv,
        # never string interpolation into code, never echoed.
        echo "→ Registering nanobanana-mcp server (user scope)..."
        GOOGLE_AI_API_KEY="${BANANA_API_KEY}" \
        python3 "${MCP_HELPER}" install --name nanobanana-mcp \
            --env-keys GOOGLE_AI_API_KEY --secret-keys GOOGLE_AI_API_KEY \
            -- npx -y @ycse/nanobanana-mcp@latest || {
            echo "✗ Could not register the MCP server. Run:"
            echo "     claude mcp add --env GOOGLE_AI_API_KEY=<key> --transport stdio --scope user \\"
            echo "       nanobanana-mcp -- npx -y @ycse/nanobanana-mcp@latest"
            echo "  See: extensions/banana/docs/BANANA-SETUP.md"
            exit 1
        }
        unset BANANA_API_KEY
    fi

    # Install skill
    echo ""
    echo "→ Installing seo-image-gen skill..."
    mkdir -p "${SKILL_DIR}"
    cp "${SOURCE_DIR}/skills/seo-image-gen/SKILL.md" "${SKILL_DIR}/SKILL.md"

    # Install agent
    echo "→ Installing seo-image-gen agent..."
    mkdir -p "${AGENT_DIR}"
    cp "${SOURCE_DIR}/agents/seo-image-gen.md" "${AGENT_DIR}/seo-image-gen.md"

    # Copy scripts and references to skill directory for ${CLAUDE_SKILL_DIR} resolution
    echo "→ Installing scripts and references..."
    mkdir -p "${SKILL_DIR}/scripts" "${SKILL_DIR}/references"
    cp "${SOURCE_DIR}/scripts/"*.py "${SKILL_DIR}/scripts/"
    cp "${SOURCE_DIR}/references/"*.md "${SKILL_DIR}/references/"

    # Pre-warm npx package
    echo "→ Pre-downloading nanobanana-mcp..."
    npx -y @ycse/nanobanana-mcp@latest --help >/dev/null 2>&1 || true

    echo ""
    echo "✓ Banana Image Generation extension installed successfully!"
    echo ""
    echo "Usage:"
    echo "  1. Start Claude Code:  claude"
    echo "  2. Run commands:"
    echo "     /seo image-gen og \"Professional SaaS dashboard\""
    echo "     /seo image-gen hero \"Dramatic sunset over city skyline\""
    echo "     /seo image-gen product \"Wireless headphones on marble\""
    echo "     /seo image-gen infographic \"SEO ranking factors 2026\""
    echo "     /seo image-gen custom \"Any creative concept\""
    echo "     /seo image-gen batch \"Product variations\" 3"
    echo ""
    echo "Full docs: extensions/banana/README.md"
    echo "To uninstall: ./extensions/banana/uninstall.sh"
}

main "$@"
