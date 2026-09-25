# Banana Extension Setup Guide

## Google AI API Key

1. Go to [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. Sign in with your Google account
3. Click "Create API key"
4. Copy the key. You'll need it during installation

**Free tier limits:**
- ~10 requests per minute (RPM)
- ~500 requests per day (RPD)
- Resets at midnight Pacific time

## MCP Server Configuration

The installer registers the server at user scope. Claude Code reads user-scope MCP
servers from `~/.claude.json`, not from `~/.claude/settings.json`
([Claude Code MCP docs](https://code.claude.com/docs/en/mcp)). To set it up manually
(the leading space keeps the key out of bash/zsh history when `HISTCONTROL=ignorespace`
/ `HIST_IGNORE_SPACE` is set):

```bash
 claude mcp add --env GOOGLE_AI_API_KEY=your-api-key-here \
  --transport stdio --scope user nanobanana-mcp -- npx -y @ycse/nanobanana-mcp@latest
```

Or run `GOOGLE_AI_API_KEY=... python3 ~/.claude/skills/seo-image-gen/scripts/setup_mcp.py`
(prompts with hidden input when the variable is unset). Without the `claude` CLI, close
Claude Code and add this to the top-level `mcpServers` object of `~/.claude.json`
(back it up first; keep all other keys):

```json
{
  "mcpServers": {
    "nanobanana-mcp": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@ycse/nanobanana-mcp@latest"],
      "env": {
        "GOOGLE_AI_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

The server reads `GOOGLE_AI_API_KEY` ([package README](https://www.npmjs.com/package/@ycse/nanobanana-mcp)).
An entry in `~/.claude/settings.json` is never loaded; rerun the installer to move it.

## Verifying Installation

Run the validation script:
```bash
python3 ~/.claude/skills/seo-image-gen/scripts/validate_setup.py
```

Or check manually:
1. `ls ~/.claude/skills/seo-image-gen/SKILL.md`:skill file exists
2. `ls ~/.claude/agents/seo-image-gen.md`:agent file exists
3. `claude mcp get nanobanana-mcp`: MCP server registered (user scope, `~/.claude.json`)

## Common Issues

### "MCP tools not available"
- Restart Claude Code after installing the extension
- Verify your API key is valid at [aistudio.google.com](https://aistudio.google.com)
- Check `claude mcp get nanobanana-mcp` (or `/mcp` in Claude Code). An entry only in
  `~/.claude/settings.json` is never loaded: rerun the installer to move it

### "Rate limited (429)"
- Free tier: ~10 requests/minute, ~500/day
- Wait 60 seconds and retry
- For batch operations, add delays between requests

### "IMAGE_SAFETY" error
- The safety filter flagged your prompt (often a false positive)
- Claude will suggest rephrased alternatives automatically
- Common triggers: certain color descriptions, implied scenarios
- See `references/prompt-engineering.md` Safety Rephrase section

### "Node.js version too old"
- Requires Node.js 18+
- Update via nvm: `nvm install 18 && nvm use 18`
- Or download from [nodejs.org](https://nodejs.org/)

### Generated images not appearing
- Default output directory: `~/Documents/nanobanana_generated/`
- Check the path returned by Claude after generation
- Verify disk space is available

## ImageMagick (Optional)

For post-processing (WebP conversion, cropping, background removal):

```bash
# Ubuntu/Pop!_OS
sudo apt install imagemagick

# Verify
magick --version
```

If `magick` (v7) is not available, the scripts fall back to `convert` (v6).
