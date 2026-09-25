<!-- Updated: 2026-09-25 -->
# GEO Worked Examples

How the rules in `SKILL.md` look in practice. Every example uses `example.com`
and invented numbers. Evidence for each claim: `geo-evidence.md`.

---

## 1. robots.txt: visible in AI search, opted out of training

The business chose to stay in every AI search product but not to supply
training data. Blocking the training tokens has no documented effect on search
visibility [V].

```
# Search and user-initiated fetches: allowed
User-agent: Googlebot
User-agent: bingbot
User-agent: OAI-SearchBot
User-agent: PerplexityBot
User-agent: Claude-SearchBot
User-agent: Claude-User
User-agent: Applebot
Allow: /

# Model training: opted out (business decision)
User-agent: GPTBot
User-agent: ClaudeBot
User-agent: Google-Extended
User-agent: Applebot-Extended
User-agent: CCBot
Disallow: /
```

Do not block `Googlebot` to keep content out of AI Overviews: that removes the
page from Search entirely. Use `nosnippet`, `data-nosnippet` or `max-snippet`
instead [V].

## 2. Findings: how to phrase them

| Situation | Wrong (removed advice) | Right |
|-----------|------------------------|-------|
| No `/llms.txt` | "Critical: create llms.txt" | "Informational: /llms.txt absent (404). Google Search does not use it; other engines' use is unconfirmed. No action needed." |
| Long guide page | "Split into 134-167 word answer blocks" | No finding. Google: "There's no ideal page length" [V] |
| Generic listicle | "Rewrite passages to be more quotable for AI" | "High [V]: page restates common advice (commodity content). Add first-hand experience or original data." |
| `OAI-SearchBot` disallowed | "Low: consider allowing AI bots" | "High [V]: OAI-SearchBot is blocked, so the site cannot appear in ChatGPT search answers. Allow it if ChatGPT visibility is wanted." |
| `GPTBot` disallowed | "High: unblock GPTBot for AI visibility" | "Informational: GPTBot (training) is blocked. OpenAI documents its bots as independent; no effect on ChatGPT search." |
| FAQPage markup present | "Add FAQ schema for AI citations" | "Info [V]: the FAQ rich result is no longer shown in Google (since 2026-05-07). Keep the FAQ content if it helps users." |
| No author or dates | "Critical: add E-E-A-T signals" | "Medium [H] (heuristic): add a visible author and publication/update dates." |

Severity rule: only [V]-backed findings may be Critical or High. [H] findings
carry the word "heuristic" in the output.

## 3. Commodity vs non-commodity content

Google's own contrast in the AI optimization guide [V]:

- Commodity: "7 Tips for First-Time Homebuyers" (restates what every site says)
- Non-commodity: "Why We Waived the Inspection & Saved Money: A Look Inside the
  Sewer Line" (a first-hand account with a specific decision and its outcome)

Audit question per page: *what does this page contain that no other page on
the web has?* If the answer is nothing, flag it under Content Uniqueness.

## 4. Sample GEO-ANALYSIS.md excerpt

```markdown
# GEO Analysis: example.com (2026-09-25)

**GEO Readiness Score: 68/100** (heuristic weights)

## Crawler Access
| Token | Type | robots.txt | Effect |
|-------|------|-----------|--------|
| Googlebot | search | allowed | eligible for AI Overviews / AI Mode |
| OAI-SearchBot | search | **blocked** | not shown in ChatGPT search [V] |
| PerplexityBot | search | allowed | eligible |
| GPTBot | training | blocked | business choice, no search effect [V] |

## Indexability & Snippet Eligibility
- /pricing has `data-nosnippet` on the main table: not usable in AI answers [V]
- Search Console "Search generative AI" control: user to confirm "Include" [V]

## Informational
- /llms.txt: absent (404). Not used by Google Search; no action.

## Top 5 Changes
1. Allow OAI-SearchBot in robots.txt [V]
2. Remove `data-nosnippet` from /pricing main content [V]
3. Add original test data to /guides/heat-pump-sizing (commodity today) [V]
4. Connect Merchant Center feed for product pages [V]
5. Add visible author and update dates to guides [H] (heuristic)
```

## 5. Measurement readout

Search Console Generative AI report (manual export: Pages table):

- Report impressions per page and the trend; there are no queries or clicks to
  report, so never estimate AI traffic from this export [V].
- Compare the top pages with the standard Performance report (Web) to see which
  pages earn AI impressions without matching organic clicks.

Bing AI Performance (run on the synthetic fixtures in
`tests/fixtures/bing-ai-performance/`):

```
python scripts/bing_webmaster.py ai-performance example.com \
  --file trend.csv --file pages.csv --file queries.csv --json
```

Reads as: 56 sampled citations over 4 days; `/guides/heat-pump-sizing` holds 55%
of cited-page citations; top grounding query "heat pump size for 120 m2 house"
(12.5% citation share). Report it as "sampled Copilot/Bing citation data", never
as rankings or traffic [V].
