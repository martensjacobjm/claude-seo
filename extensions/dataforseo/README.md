# DataForSEO Extension for Claude SEO

Live SEO data via the [DataForSEO MCP server](https://github.com/dataforseo/mcp-server-typescript) (`dataforseo-mcp-server` 3.x). Adds 23 commands across 9 DataForSEO APIs: SERP analysis (organic, images, YouTube), keyword research, backlinks, on-page analysis, competitor analysis, content analysis, business listings, AI visibility checking, and LLM mention tracking.

## Prerequisites

- [Claude SEO](https://github.com/AgriciDaniel/claude-seo) installed
- Node.js 22+ (`dataforseo-mcp-server` 3.1.x requires `node >=22`)
- [DataForSEO account](https://app.dataforseo.com/register) with API credentials

## Installation

### Unix/macOS/Linux

```bash
git clone https://github.com/AgriciDaniel/claude-seo.git
cd claude-seo
./extensions/dataforseo/install.sh
```

### Windows

```powershell
git clone https://github.com/AgriciDaniel/claude-seo.git
cd claude-seo
.\extensions\dataforseo\install.ps1
```

The installer will:
1. Prompt for your DataForSEO API login and API password
2. Install the skill (with `references/tool-catalog.md`) and agent files
3. Configure the MCP server in `~/.claude/settings.json` as `npx -y dataforseo-mcp-server@3`
4. Pre-download the package

### Server version

The installer pins the **major** version: `dataforseo-mcp-server@3` (any 3.x, currently
3.1.1, released 2026-08-25). v3.0.0 (2026-08-11) replaced the ~80 per-endpoint v2 tools
(`serp_organic_live_advanced`, `backlinks_summary`, ...) with four generic tools:
`api_request`, `docs_search`, `docs_index`, `docs_list_sections`. The skills call
`api_request` with the DataForSEO endpoint path and keep the v2 tool name as a fallback,
so an existing 2.x setup keeps working. A future 4.x is not picked up until someone
checks it and bumps the pin. The v2-name to v3-path map is in
`skills/seo-dataforseo/references/tool-catalog.md`.

Sources: [npm registry metadata](https://registry.npmjs.org/dataforseo-mcp-server),
[server README](https://github.com/dataforseo/mcp-server-typescript#readme).

## Commands

### SERP Analysis

| Command | Description |
|---------|-------------|
| `/seo dataforseo serp <keyword>` | Google organic SERP results (also Bing/Yahoo) |
| `/seo dataforseo serp-images <keyword>` | Google Images SERP results (needs v3) |
| `/seo dataforseo serp-youtube <keyword>` | YouTube search results |
| `/seo dataforseo youtube <video_id>` | YouTube video deep analysis (info, comments, subtitles) |

### Keyword Research

| Command | Description |
|---------|-------------|
| `/seo dataforseo keywords <seed>` | Keyword ideas, suggestions, and related terms |
| `/seo dataforseo volume <keywords>` | Search volume for keyword list |
| `/seo dataforseo difficulty <keywords>` | Keyword difficulty scores |
| `/seo dataforseo intent <keywords>` | Search intent classification |
| `/seo dataforseo trends <keyword>` | Google Trends data over time |

### Domain & Competitor Analysis

| Command | Description |
|---------|-------------|
| `/seo dataforseo backlinks <domain>` | Full backlink profile with spam scores |
| `/seo dataforseo competitors <domain>` | Competing domains and traffic estimates |
| `/seo dataforseo ranked <domain>` | Keywords a domain ranks for |
| `/seo dataforseo intersection <domains>` | Keyword/backlink overlap (2-20 domains) |
| `/seo dataforseo traffic <domains>` | Bulk traffic estimation |
| `/seo dataforseo subdomains <domain>` | Subdomains with ranking data |
| `/seo dataforseo top-searches <domain>` | Top queries mentioning domain |

### Technical / On-Page

| Command | Description |
|---------|-------------|
| `/seo dataforseo onpage <url>` | On-page analysis (Lighthouse + content parsing) |
| `/seo dataforseo tech <domain>` | Technology stack detection |
| `/seo dataforseo whois <domain>` | WHOIS registration data |

### Content & Business Data

| Command | Description |
|---------|-------------|
| `/seo dataforseo content <keyword/url>` | Content analysis, search, and phrase trends |
| `/seo dataforseo listings <keyword>` | Business listings search |

### AI Visibility / GEO

| Command | Description |
|---------|-------------|
| `/seo dataforseo ai-scrape <query>` | ChatGPT web scraper for GEO visibility |
| `/seo dataforseo ai-mentions <keyword>` | LLM mention tracking across AI platforms |

## APIs Used

v3 has no module switch: `api_request` reaches every DataForSEO API your account can use.
(v2's `ENABLED_MODULES` variable is ignored by v3.)

| API | Purpose | Example Commands |
|--------|---------|-----------------|
| SERP | Search engine results | serp, serp-images, serp-youtube, youtube |
| KEYWORDS_DATA | Search volume, trends | volume, trends |
| DATAFORSEO_LABS | Keyword research, competitors | keywords, difficulty, intent, competitors, ranked, subdomains, top-searches |
| BACKLINKS | Link profiles | backlinks, intersection |
| ONPAGE | Page analysis (Lighthouse) | onpage |
| DOMAIN_ANALYTICS | Tech detection, WHOIS | tech, whois |
| BUSINESS_DATA | Business listings | listings |
| CONTENT_ANALYSIS | Content quality, trends | content |
| AI_OPTIMIZATION | ChatGPT scraper, LLM mentions | ai-scrape, ai-mentions |

## API Credits

DataForSEO charges per call. Live-mode list prices from DataForSEO's pricing pages,
fetched 2026-09-25 (USD; prices change, re-check before quoting):

| Endpoint | Live price | Source |
|---|---|---|
| Google Organic SERP | $0.002 per SERP of 10 results (depth 100 = 10 SERPs) | [pricing](https://dataforseo.com/pricing/google-serp/google-organic-serp-api) |
| Google Images SERP | $0.002 per SERP of up to 100 results; `site:`/`filetype:` etc. x5 | [pricing](https://dataforseo.com/pricing/google-serp/google-images-serp-api) |
| Google Ads search volume | $0.09 per task (up to 1,000 keywords) | [pricing](https://dataforseo.com/pricing/keywords-data/google-ads) |
| DataForSEO Labs (most endpoints) | $0.012 per task + $0.00012 per item | [pricing](https://dataforseo.com/pricing/dataforseo-labs/dataforseo-google-api) |
| Backlinks | $0.024 per request + $0.000036 per row | [pricing](https://dataforseo.com/pricing/backlinks/backlinks) |
| OnPage Instant Pages / Content Parsing | $0.00015 per page (basic) | [pricing](https://dataforseo.com/pricing/on-page/onpage-api) |
| Lighthouse | $0.005 per page | [pricing](https://dataforseo.com/pricing/on-page/lighthouse-api) |
| ChatGPT LLM Scraper | $0.004 per results page | [pricing](https://dataforseo.com/pricing/ai-optimization/llm-scraper) |
| LLM Mentions | $0.1 per request + $0.001 per row | [pricing](https://dataforseo.com/pricing/ai-optimization/llm-mentions) |

The earlier ranges in this file (for example "AI optimization ~$0.01", "on-page
$0.01-0.05 per page") did not match these pages and were removed. v3 `.ai` responses
omit the `cost` field; the skill passes `noAiMode: true` when it must report credits.
New accounts get $1 free credit ([MCP page](https://dataforseo.com/seo-mcp-server)); the minimum top-up is $50 ([pricing](https://dataforseo.com/pricing)).

## Field Filtering

`field-config.json` uses the v3 format (keyed by endpoint path) and ships empty: v3
already returns the trimmed `.ai` response by default (`depth`/`limit` default to 10,
empty fields dropped). Add paths to trim further; see the
[field configuration docs](https://github.com/dataforseo/mcp-server-typescript#field-configuration).
The old module-keyed v2 file is rejected by v3 and then ignored.

## Integration with Claude SEO

When installed, other Claude SEO skills automatically detect DataForSEO availability and use live data:

- **`/seo audit`**:Uses real SERP, backlink, and on-page data
- **`/seo technical`**:Uses on-page analysis for real technical data
- **`/seo content`**:Uses keyword volume, difficulty, and intent data
- **`/seo geo`**:Uses ChatGPT scraper and LLM mentions for GEO signals
- **`/seo plan`**:Uses competitor and keyword data for strategy
- **`/seo backlinks`**, **`/seo local`**, **`/seo maps`**, **`/seo images`**, **`/seo page`**: live backlink, local, maps, image SERP and SERP data

Skills detect DataForSEO when the `dataforseo` server's `api_request` tool (v3) or a v2
tool such as `serp_organic_live_advanced` is present, and say so when neither is.

## Troubleshooting

### MCP server not connecting

1. Check credentials: `cat ~/.claude/settings.json | grep DATAFORSEO` (v3 reads `DATAFORSEO_LOGIN`; `DATAFORSEO_USERNAME` is accepted as an alias)
2. Check Node: `node -v` must be 22 or newer
3. Test the API from a shell: `DATAFORSEO_LOGIN=... DATAFORSEO_PASSWORD=... npx -y dataforseo-mcp-server@3 request -X GET -p /v3/serp/google/locations`
4. Re-run installer: `./extensions/dataforseo/install.sh`

### Skills mention tools that do not exist

You are on v3 and a skill named a v2 tool. Look up its path in
`skills/seo-dataforseo/references/tool-catalog.md` and call `api_request`. To stay on
the old server instead, set the args to `dataforseo-mcp-server@2` (deprecated upstream:
[mcp-server-typescript-deprecated](https://github.com/dataforseo/mcp-server-typescript-deprecated)).

### API errors

- **401 Unauthorized**: Check username/password in settings.json
- **402 Payment Required**: Add credits at [app.dataforseo.com](https://app.dataforseo.com)
- **429 Rate Limited**: Wait and retry (DataForSEO allows up to 2,000 API calls per minute)

### Module not available

v3 has no modules. On the old v2 server, a missing tool meant its module was absent
from `ENABLED_MODULES`.

## Uninstall

### Unix/macOS/Linux

```bash
./extensions/dataforseo/uninstall.sh
```

### Windows

```powershell
.\extensions\dataforseo\uninstall.ps1
```

This removes the skill, agent, field config, and MCP server entry from settings.json.

## Links

- [DataForSEO API Docs](https://docs.dataforseo.com/)
- [DataForSEO MCP Server](https://github.com/dataforseo/mcp-server-typescript) / [npm](https://www.npmjs.com/package/dataforseo-mcp-server)
- [Claude SEO](https://github.com/AgriciDaniel/claude-seo)
