# Skillkarta: vem gör vad i varje fas

Hemsida är dirigenten. Tabellerna nedan säger vilken skill som tar en fas djupare om den
finns, vad hemsida gör själv om den saknas, och vad fasen alltid ska leverera. Skillnamnen
står exakt som de heter; i en miljö kan de ha ett prefix (`marketingskills:`,
`anthropic-skills:`, `claude-seo:`). Status per 2026-09-25.

## Upptäckt: gör så här varje gång

1. Läs listan över tillgängliga skills i den aktuella miljön. En skill finns bara om den
   står där. Gissa aldrig utifrån att den brukar finnas.
2. Kontrollera beskrivningen, inte bara namnet. Två skills kan heta lika (se Namnkrockar).
3. Claude Code: `/seo`-kommandon finns bara om claude-seo-pluginen är installerad. Syns
   inget `/seo` i kommandolistan eller skill-listan: använd reserven.
4. claude.ai: det finns inga `/seo`-kommandon och inga repo-skript. Uppladdade skills och
   kodkörning i sandlådan är allt. Nätåtkomst kan saknas; be då om HTML eller skärmdumpar.
5. Saknas skillen: kör reserven och fortsätt. Skriv i leveransen vilka skills som användes
   och vilka som saknades.
6. Betalda API:er (DataForSEO, Google Ads, BigQuery): fråga ägaren innan anrop som kostar.

## Källorna

| Källa | Miljö | Kännetecken |
|-------|-------|-------------|
| claude-seo | Claude Code (plugin) | `/seo`-kommandon, Python-skript, hook för schemavalidering, subagenter |
| marketingskills | Claude Code eller uppladdad | Rena instruktioner; beskrivningen börjar ofta "When the user wants to" |
| Jacobs claude.ai-skills | claude.ai, ibland även Claude Code | `astro`, `react`, `vue`, `web-artifacts-builder`, `webapp-testing`, `theme-factory`, `canvas-design`, `brand-guidelines`, `skill-evidens`, `doc-coauthoring`, `pdf`, `xlsx`, `scrapling`, `article-extractor` |

## Fas 0 Brief och fakta

| Skill | Källa | Används till |
|-------|-------|--------------|
| `product-marketing-context` | marketingskills | Positionering, målgrupp och erbjudande som ett återanvändbart dokument |
| `doc-coauthoring` | claude.ai | Skriva briefen tillsammans med ägaren |
| `pdf`, `xlsx` | claude.ai | Läsa ägarens prislistor, intyg och kundlistor |

Reserv: `faktablad-mall.md`. Leverans: faktablad med källa per rad och en lista över det
som saknas. Fakta om företaget kommer bara från ägaren, oavsett vad en skill föreslår.

## Fas 1 Strategi

| Skill | Källa | Används till |
|-------|-------|--------------|
| `seo-plan` (`/seo plan`) | claude-seo | Branschmall, arkitektur, innehållsplan |
| `site-architecture` | marketingskills | Sidhierarki, URL-struktur, navigering, internlänkar |
| `content-strategy` | marketingskills | Ämnen och innehållspelare |
| `seo-dataforseo` (`/seo dataforseo`) | claude-seo (tillägg) | Sökvolym, avsikt, SERP. Följ skillens egna verktygsnamn; MCP-servern byts mot v3 |
| `seo-google` (`/seo google keywords`) | claude-seo | Keyword Planner, kräver Google Ads-konto |
| `seo-programmatic` (`/seo programmatic`), `programmatic-seo` | claude-seo, marketingskills | Bara om sajten ska ha många mallsidor |
| `seo-competitor-pages`, `competitor-alternatives` | claude-seo, marketingskills | Jämförelsesidor, bara med verifierbara uppgifter om konkurrenten |
| `seo-hreflang` (`/seo hreflang`) | claude-seo | Planera språk och regioner om sajten blir flerspråkig |
| `pricing-strategy` | marketingskills | Prissida, bara om ägaren vill ha stöd i prissättningen |
| `scrapling`, `article-extractor` | claude.ai | Läsa konkurrenters sidor; respektera robots.txt och villkor |

Reserv: fas 1 i `skapa-fas.md`. Leverans: sidkarta (URL, sökavsikt, målgrupp, tjänst,
ort) och en rad om hur sökvolym togs fram eller att den saknas. Hitta aldrig på volymer.

## Fas 2 Innehåll

| Skill | Källa | Används till |
|-------|-------|--------------|
| `copywriting` | marketingskills | Rubriker, värdeerbjudande, sidtext |
| `copy-editing` | marketingskills | Putsa befintlig text |
| `seo-content` (`/seo content`) | claude-seo | E-E-A-T och tunt innehåll |
| `marketing-psychology` | marketingskills | Framing och socialt bevis, bara med sanna uppgifter |
| `social-content` | marketingskills | Delningstexter vid lansering |

Reserv: avsnittet Innehåll i SKILL.md och `eeat-framework.md`. Leverans: text per sida där
varje faktapåstående går att spåra till faktabladet.

## Fas 3 Bygge

| Skill | Källa | Används till |
|-------|-------|--------------|
| `astro` | claude.ai | Förstahandsval för innehållssajter: statisk HTML ut |
| `react`, `vue` | claude.ai | När sajten behöver appfunktioner; kräver SSR eller SSG så att innehållet finns i initial HTML |
| `theme-factory` | claude.ai | Färger och typsnitt |
| `canvas-design` | claude.ai | Statiska bilder som Open Graph-bild |
| `web-artifacts-builder` | claude.ai | Bara prototyp att visa ägaren. Klientrenderad React i en fil, inte en produktionssajt |
| `seo-images` (`/seo images`) | claude-seo | Alt-text, format, storlek, konvertering till WebP och AVIF |
| `seo-image-gen` (`/seo image-gen`) | claude-seo (tillägg) | Illustrationer och OG-bilder, aldrig som bevis för personal eller utförda jobb |

Reserv: Teknisk checklista i SKILL.md och `cwv-thresholds.md`. Leverans: kod,
prestandabudget, tillgänglighetskontroll, mobilkontroll.

## Fas 4 Teknisk SEO och AI-sök

| Skill | Källa | Används till |
|-------|-------|--------------|
| `seo-technical` (`/seo technical`) | claude-seo | Crawlning, indexering, säkerhet, JavaScript-rendering |
| `seo-schema` (`/seo schema`) | claude-seo | Generera och validera JSON-LD |
| `schema-markup` | marketingskills | JSON-LD i båda miljöerna |
| `seo-sitemap` (`/seo sitemap generate`) | claude-seo | XML-sitemap |
| `seo-geo` (`/seo geo`) | claude-seo | AI-crawlers, utdrag, mätning i AI-sök |
| `ai-seo` | marketingskills | AI-sök i båda miljöerna |
| `seo-hreflang` (`/seo hreflang`) | claude-seo | Bara vid flera språk |

Reserv: Crawlers, Strukturerad data och `scripts/validate_schema.py`. Leverans: robots.txt,
sitemap, canonical per sida, JSON-LD som passerar validering utan block och utan varning.

## Fas 5 Lokalt

| Skill | Källa | Används till |
|-------|-------|--------------|
| `seo-local` (`/seo local`) | claude-seo | GBP, NAP, citeringar, platssidor |
| `seo-maps` (`/seo maps`) | claude-seo | NAP över Google, Bing, Apple och OSM; geo-grid kostar via DataForSEO |

Reserv: avsnittet Lokalt företag och `local-schema-types.md`. Leverans: NAP-tabell och
profilchecklista.

## Fas 6 Konvertering och mätning

| Skill | Källa | Används till |
|-------|-------|--------------|
| `page-cro` | marketingskills | Startsida och landningssidor |
| `form-cro` | marketingskills | Kontakt- och offertformulär |
| `signup-flow-cro` | marketingskills | Bara om sajten har konton eller provperiod |
| `popup-cro` | marketingskills | Bara om ägaren vill ha popup; inget som täcker innehållet på mobil |
| `analytics-tracking` | marketingskills | Mätplan, händelser, samtycke |
| `seo-google` (`/seo google`) | claude-seo | Search Console, GA4 |

Reserv: avsnittet Mätning. Leverans: formulär testat hela vägen, mätplan, Search Console
och Bing Webmaster Tools verifierade.

## Fas 7 QA-grind

| Skill | Källa | Används till |
|-------|-------|--------------|
| `webapp-testing` | claude.ai | Playwright: formulär, konsolfel, skärmdumpar i mobilbredd |
| `seo-audit` (`/seo audit`) | claude-seo | Full granskning av testmiljön eller den färdiga sajten |
| `seo-page` (`/seo page`) | claude-seo | En sida i taget |
| `seo-google` (`/seo google pagespeed`) | claude-seo | Lighthouse och CrUX |
| `seo-audit` | marketingskills | Diagnos när claude-seo saknas |

Reserv: `qa-grind.md`. Leverans: ifylld QA-tabell där alla blockerande rader är pass.

## Fas 8 Lansering och uppföljning

| Skill | Källa | Används till |
|-------|-------|--------------|
| `seo-google` (`/seo google inspect`, `sitemaps`, `gen-ai-report`) | claude-seo | Indexering, sitemapstatus, rapporten för generativ AI |
| `seo-backlinks` (`/seo backlinks ai-performance`) | claude-seo | Läsa Bing AI Performance-export |
| `seo-backlinks` (`/seo backlinks`) | claude-seo | Länkprofil efter några månader |
| `xlsx` | claude.ai | Läsa exporter i båda miljöerna |
| `seo-audit` (`/seo audit`) | claude-seo | Uppföljande granskning |

Reserv: fas 8 i `skapa-fas.md`. Leverans: lanseringslogg, baslinjeexporter, plan för
uppföljning.

## Övriga

| Skill | Källa | Används till |
|-------|-------|--------------|
| `seo` (`/seo`) | claude-seo | Orkestratorn; vidarebefordrar till underskills |
| `skill-evidens` | claude.ai | När hemsida själv eller en delegerad skill ska evidensgranskas |

## Namnkrockar och förbehåll

- `seo-audit` finns i både claude-seo och marketingskills. claude-seo: "Full website SEO
  audit with parallel subagent delegation". marketingskills: "When the user wants to audit,
  review, or diagnose SEO issues". Skriv vilken som användes.
- `brand-guidelines` är Anthropics egen färg- och typsnittsprofil. Använd den aldrig för
  en kunds sajt; använd `theme-factory` eller ägarens egen profil.
- `seo-plan` nämner "domain authority". Det är ett tredjepartsmått, inget Google använder.
- `marketing-psychology`, `popup-cro`: brådska, knapphet och nedräkning bara när de är sanna.
- `page-cro`, `form-cro`, `copywriting`: omdömen bara om de är verkliga, med källa och
  samtycke.
- `schema-markup`, `seo-schema`: inga egna stjärnbetyg i markup, ingen FAQPage eller HowTo
  för rich results.
- `ai-seo`, `seo-geo`: `llms.txt` är information, inte en åtgärd.
- `seo-dataforseo`, `seo-maps`: kostar pengar per anrop. Fråga först.

All utdata från skills ovan går genom konfliktregeln i SKILL.md innan den används.
