# Firecrawl Setup Guide

## 1. Get Your API Key

1. Go to [firecrawl.dev/app/sign-up](https://www.firecrawl.dev/app/sign-up)
2. Create a free account (500 credits/month included)
3. Navigate to **API Keys** in the dashboard
4. Copy your API key (starts with `fc-`)

## 2. Run the Installer

The installer handles everything automatically:

```bash
./extensions/firecrawl/install.sh
```

It will prompt for your API key and configure the MCP server.

## 3. Manual MCP Configuration

Claude Code loads user-scope MCP servers from `~/.claude.json`, not from
`~/.claude/settings.json` ([Claude Code MCP docs](https://code.claude.com/docs/en/mcp)).
If the installer fails, register the server with the CLI (the leading space keeps the
key out of bash/zsh history when `HISTCONTROL=ignorespace` / `HIST_IGNORE_SPACE` is set):

```bash
 claude mcp add --env FIRECRAWL_API_KEY=fc-your-api-key-here \
  --transport stdio --scope user firecrawl-mcp -- npx -y firecrawl-mcp
```

Keep another option between `--env` and the server name (`--env` takes several pairs);
`--` separates the server command. Check with `claude mcp get firecrawl-mcp`; remove
with `claude mcp remove firecrawl-mcp --scope user`.

Without the CLI, close Claude Code and add this to the top-level `mcpServers` object
of `~/.claude.json` (back it up first; keep all other keys):

```json
{
  "mcpServers": {
    "firecrawl-mcp": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "firecrawl-mcp"],
      "env": {
        "FIRECRAWL_API_KEY": "fc-your-api-key-here"
      }
    }
  }
}
```

An `mcpServers.firecrawl-mcp` entry in `~/.claude/settings.json` (installers up to
v1.8.1) is never loaded; delete it, or rerun the installer, which does so.

## 4. Verify Installation

Start Claude Code and try:

```
/seo firecrawl map https://example.com
```

You should see a list of discovered URLs. If you get a "tool not available" error, restart Claude Code to reload MCP servers.

## 5. Understanding Credits

| Operation | Credits Used |
|-----------|-------------|
| `crawl` | 1 per page crawled |
| `scrape` | 1 per page |
| `map` | 0.5 per URL discovered |
| `search` | 1 per result returned |

**Free tier**: 500 credits/month resets on your billing date.

**Tip**: Use `map` first (cheap) to see how many pages a site has, then decide how many to `crawl` (more expensive).
