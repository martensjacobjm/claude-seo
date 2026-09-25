# Firecrawl Extension Uninstaller for Claude SEO (Windows)
$ErrorActionPreference = 'Stop'

Write-Host "Removing Firecrawl extension..." -ForegroundColor Yellow

$SkillDir = "$env:USERPROFILE\.claude\skills\seo-firecrawl"

if (Test-Path $SkillDir) {
    Remove-Item -Recurse -Force $SkillDir
    Write-Host "v Removed skill files" -ForegroundColor Green
}

# Shared MCP registration helper (extensions/claude_mcp_config.py). It runs
# `claude mcp add --scope user` (user-scope servers live in ~/.claude.json;
# Claude Code never reads mcpServers from ~/.claude/settings.json, where
# installers up to v1.8.1 wrote them), falls back to a JSON-safe merge into
# ~/.claude.json, and removes the legacy settings.json entry (backup first).
function Find-Python {
    foreach ($name in @('python3', 'python', 'py')) {
        $cmd = Get-Command -Name $name -CommandType Application -ErrorAction SilentlyContinue |
            Select-Object -First 1
        if ($null -eq $cmd) { continue }
        $pre = @()
        if ($name -eq 'py') { $pre = @('-3') }
        try {
            # Skips the Microsoft Store "python" alias, which exits non-zero.
            & $cmd.Source @pre -c "import sys; sys.exit(0 if sys.version_info >= (3, 7) else 1)" 2>$null | Out-Null
            if ($LASTEXITCODE -eq 0) { return [pscustomobject]@{ Exe = $cmd.Source; Pre = $pre } }
        } catch { }
    }
    return $null
}

function Find-McpHelper([string]$Dir) {
    foreach ($candidate in @((Join-Path $Dir '..\claude_mcp_config.py'), (Join-Path $Dir 'extensions\claude_mcp_config.py'))) {
        if (Test-Path $candidate) { return (Resolve-Path $candidate).Path }
    }
    return $null
}

# Unregister the MCP server: `claude mcp remove firecrawl-mcp --scope user` (or
# ~/.claude.json directly without the CLI), plus the legacy entry that
# installers up to v1.8.1 wrote to ~/.claude/settings.json.
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = Find-Python
$mcpHelper = Find-McpHelper $ScriptDir
$unregistered = $false
if ($null -ne $python -and $null -ne $mcpHelper) {
    $helperArgs = @($python.Pre) + @($mcpHelper, 'uninstall', '--name', 'firecrawl-mcp')
    try {
        & $python.Exe @helperArgs
        $unregistered = ($LASTEXITCODE -eq 0)
    } catch {
        $unregistered = $false
    }
} elseif ($null -ne (Get-Command -Name claude -ErrorAction SilentlyContinue)) {
    try { & claude mcp remove firecrawl-mcp --scope user 2>&1 | Out-Null } catch { }
    Write-Host "  Ran: claude mcp remove firecrawl-mcp --scope user" -ForegroundColor Green
    Write-Host "  Python 3 not found: delete any mcpServers.firecrawl-mcp entry from ~\.claude\settings.json by hand."
    $unregistered = $true
}
if (-not $unregistered) {
    Write-Host "  Warning: Could not unregister the MCP server. Run: claude mcp remove firecrawl-mcp --scope user" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "v Firecrawl extension uninstalled." -ForegroundColor Green
Write-Host "  Core Claude SEO skills are unchanged."
