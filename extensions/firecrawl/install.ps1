# Firecrawl Extension Installer for Claude SEO (Windows)
$ErrorActionPreference = 'Stop'

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "  Firecrawl Extension - Installer" -ForegroundColor Cyan
Write-Host "  For Claude SEO" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

$SkillDir = "$env:USERPROFILE\.claude\skills\seo-firecrawl"
$SeoSkillDir = "$env:USERPROFILE\.claude\skills\seo"

# Check prerequisites
if (-not (Test-Path $SeoSkillDir)) {
    Write-Host "x Claude SEO is not installed." -ForegroundColor Red
    Write-Host "  Install it first: irm https://raw.githubusercontent.com/AgriciDaniel/claude-seo/main/install.ps1 | iex"
    exit 1
}
Write-Host "v Claude SEO detected" -ForegroundColor Green

$nodeVersion = (node -v 2>$null) -replace 'v',''
if (-not $nodeVersion) {
    Write-Host "x Node.js is required but not installed." -ForegroundColor Red
    exit 1
}
$major = [int]($nodeVersion -split '\.')[0]
if ($major -lt 20) {
    Write-Host "x Node.js 20+ required (found v$nodeVersion)." -ForegroundColor Red
    exit 1
}
Write-Host "v Node.js v$nodeVersion detected" -ForegroundColor Green

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

# Prompt for API key
Write-Host ""
Write-Host "Firecrawl API key required." -ForegroundColor Yellow
Write-Host "Sign up at: https://www.firecrawl.dev/app/sign-up"
Write-Host "Free tier: 500 credits/month"
Write-Host ""

$apiKey = Read-Host "Firecrawl API key" -AsSecureString
$apiKeyPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($apiKey))
if ([string]::IsNullOrWhiteSpace($apiKeyPlain)) {
    Write-Host "x API key cannot be empty." -ForegroundColor Red
    exit 1
}

# Determine source directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SourceDir = $null
if (Test-Path "$ScriptDir\skills\seo-firecrawl\SKILL.md") {
    $SourceDir = $ScriptDir
} elseif (Test-Path "$ScriptDir\extensions\firecrawl\skills\seo-firecrawl\SKILL.md") {
    $SourceDir = "$ScriptDir\extensions\firecrawl"
} else {
    Write-Host "x Cannot find extension source files." -ForegroundColor Red
    exit 1
}

# Install skill
Write-Host ""
Write-Host "=> Installing Firecrawl skill..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path $SkillDir | Out-Null
Copy-Item "$SourceDir\skills\seo-firecrawl\SKILL.md" "$SkillDir\SKILL.md" -Force

# Register the MCP server at user scope
Write-Host "=> Registering MCP server (user scope)..." -ForegroundColor Yellow
$python = Find-Python
$mcpHelper = Find-McpHelper $ScriptDir
$registered = $false
if ($null -ne $python -and $null -ne $mcpHelper) {
    # The key reaches the helper through the environment only (never argv,
    # never string interpolation into code, never echoed). Splatting keeps the
    # literal '--' separator intact for the native command.
    $env:FIRECRAWL_API_KEY = $apiKeyPlain
    $helperArgs = @($python.Pre) + @($mcpHelper, 'install', '--name', 'firecrawl-mcp',
        '--env-keys', 'FIRECRAWL_API_KEY', '--secret-keys', 'FIRECRAWL_API_KEY',
        '--', 'npx', '-y', 'firecrawl-mcp')
    try {
        & $python.Exe @helperArgs
        $registered = ($LASTEXITCODE -eq 0)
    } catch {
        $registered = $false
    } finally {
        Remove-Item Env:FIRECRAWL_API_KEY -ErrorAction SilentlyContinue
    }
} elseif ($null -eq $python) {
    Write-Host "  Warning: Python 3 not found; cannot register the MCP server automatically." -ForegroundColor Yellow
} else {
    Write-Host "  Warning: extensions\claude_mcp_config.py not found (run from the claude-seo repo)." -ForegroundColor Yellow
}
if (-not $registered) {
    Write-Host "  Register it yourself (replace <key>):"
    Write-Host "    claude mcp add --env FIRECRAWL_API_KEY=<key> --transport stdio --scope user ``"
    Write-Host "      firecrawl-mcp -- npx -y firecrawl-mcp"
    Write-Host "  and delete any mcpServers.firecrawl-mcp entry from ~\.claude\settings.json."
    Write-Host "  See: extensions\firecrawl\docs\FIRECRAWL-SETUP.md"
}
$apiKeyPlain = $null

# Pre-warm
Write-Host "=> Pre-downloading firecrawl-mcp..." -ForegroundColor Yellow
npx -y firecrawl-mcp --help 2>$null | Out-Null

Write-Host ""
Write-Host "v Firecrawl extension installed!" -ForegroundColor Green
Write-Host ""
Write-Host "Usage:"
Write-Host "  /seo firecrawl crawl https://example.com"
Write-Host "  /seo firecrawl map https://example.com"
Write-Host "  /seo firecrawl scrape https://example.com/page"
