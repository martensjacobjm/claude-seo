# Exempel: evidensgranskningen av claude-seo (2026-09-24 och 2026-09-25)

Ett verkligt fall, förkortat. Repot är claude-seo, en SEO-skill för Claude Code. Målet var
sub-skillen seo-geo (AI-sökning), och granskningen spred sig till seo-content, seo-local,
seo-schema, seo-google och skripten. Allt nedan finns i repots commits `b4a722f`
(evidensrundan) och `7d09834` (exempel och tester) och i `CHANGELOG.md` under [Unreleased].

## 1. Utlösande källa

Google publicerade "Guide to Optimizing for Generative AI Features on Google Search",
https://developers.google.com/search/docs/fundamentals/ai-optimization-guide, senast
uppdaterad 2026-07-10. Enligt guiden bygger AI-funktionerna på samma rankings- och
kvalitetssystem som vanlig sök, det finns inget krav på chunkning, "no ideal page length",
inget behov av att skriva om för AI, ingen särskild schema-markup, och llms.txt används inte
av Google Search. Search Centrals changelog 2026-06-15 säger att llms.txt-filer inte behövs
för Google Search.

## 2. Inventering (utdrag)

| ID | Påstående i seo-geo före | Typ | Angiven källa |
|----|--------------------------|-----|---------------|
| P01 | "Optimal passage length: 134-167 words for AI citation" | regel | ingen |
| P02 | "The emerging llms.txt standard provides AI crawlers with structured content guidance" | regel | ingen |
| P03 | "92% of AI Overview citations come from top-10 ranking pages" | siffra | "Industry data" |
| P04 | "AI-referred sessions growth 527% (Jan-May 2025)" | siffra | SparkToro |
| P05 | "Content with multi-modal elements sees 156% higher selection rates" | siffra | ingen |
| P06 | "ChatGPT: Wikipedia (47.9%), Reddit (11.3%)" | siffra | ingen |
| P07 | "Allow GPTBot for AI search visibility" | regel | ingen |
| P08 | YouTube-korrelation "0.737" med AI-synlighet | siffra | Ahrefs |

## 3. Verifiering (utdrag)

| ID | Primärkälla | Status | Åtgärd |
|----|-------------|--------|--------|
| P01 | Googles AI-optimeringsguide, 2026-07-10: "no ideal page length", inget chunkningskrav | Motsagd | Struken |
| P02 | Samma guide + changelog 2026-06-15; llmstxt.org är ett förslag, inte en standard | Motsagd | Informativ statuskontroll utan poäng |
| P03 | Ingen primärkälla hittad | Overifierad | Struken |
| P04 | Ingen primärkälla hittad | Overifierad | Struken |
| P05 | Ingen källa alls | Overifierad | Struken |
| P06 | Ingen primärkälla hittad | Overifierad | Struken |
| P07 | OpenAI:s botsida: GPTBot används för träning, OAI-SearchBot för ChatGPT-sök | Motsagd | Vänd: OAI-SearchBot styr sök, GPTBot är träning |
| P08 | Ingen primärkälla hittad | Overifierad | Struken i seo-geo, seo-google, seo-dataforseo, dess tilläggsspegel och en skript-docstring |

P08 visar varför steg 4 kräver sökning i hela repot: siffran ströks först ur seo-geo
och seo-google men låg kvar i seo-dataforseo och `youtube_search.py`. Den ströks där i en
senare omgång, och changeloggen bär spår av båda omgångarna (Fixed säger "still in
seo-dataforseo", Changed säger att den är borttagen). Faktalinsen i steg 7 ska fånga sådant.

## 4. Fel mot rätt formulering

Så här ser tabellen ut i målskillens exempelfil (`geo-examples.md`). Den levererades i en
andra commit, efter att användaren fick be om den. Leverera den i första.

| Situation | Fel (borttaget råd) | Rätt |
|-----------|---------------------|------|
| Ingen `/llms.txt` | "Critical: create llms.txt" | "Informational: /llms.txt absent (404). Google Search does not use it; other engines' use is unconfirmed. No action needed." |
| Lång guidesida | "Split into 134-167 word answer blocks" | Inget fynd. Google: "There's no ideal page length" [V] |
| `OAI-SearchBot` blockerad | "Low: consider allowing AI bots" | "High [V]: OAI-SearchBot is blocked, so the site cannot appear in ChatGPT search answers." |
| `GPTBot` blockerad | "High: unblock GPTBot for AI visibility" | "Informational: GPTBot (training) is blocked. No effect on ChatGPT search." |
| Ingen författare eller datum | "Critical: add E-E-A-T signals" | "Medium [H] (heuristic): add a visible author and publication/update dates." |

## 5. Registret (utdrag ur `geo-evidence.md`)

```markdown
| [Guide to Optimizing for Generative AI Features](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide) | Last updated 2026-07-10 | ... llms.txt not used by Google Search (neither helps nor harms); no chunking requirement, "no ideal page length"; no need to rewrite for AI ... |

## 5. Removed Claims (no primary source found, 2026-09-24)

Do not re-introduce these without a fetched primary source:

- "Optimal passage length: 134-167 words" (contradicted by Google: no ideal length, no chunking requirement)
- "92% of AI Overview citations come from top-10 pages" / "47% below position 5"
- "156% higher selection rates" for multi-modal content
- "527% AI-referred sessions growth" (SparkToro)
- "Allow GPTBot for AI search visibility" (GPTBot is training-only)
- llms.txt as an "emerging standard" to implement
```

## 6. Forskning med förbehåll

GEO-artikeln (Aggarwal m.fl., KDD 2024, arXiv 2311.09735) graderades [R-peer] och fick
behålla sitt resultat (upp till 40 % bättre synlighet på GEO-bench), men med förbehållet att
det mättes med källan redan i ett fast sammanhang. En översikt från 2026 (arXiv 2607.14035)
graderades [R-preprint, en författare] eftersom den inte är granskad. Ingen av dem fick
driva Critical eller High.

## 7. Tester och vad de hittade

Granskningen lade till två skript (`crux_bigquery.py`, en parser för Bing AI Performance-
exporter). Andra commiten lade till 23 pytest-tester mot syntetiska fixtures i
`tests/fixtures/`, med en README som säger att filerna är syntetiska och siffrorna uppfunna.
Första körningen hittade ett riktigt fel: parsern kastade `FileNotFoundError` för en saknad
fil när den anropades som bibliotek, i stället för att returnera en varning. Felet rättades
och fördes in under Fixed. CI fick ett steg som kör testerna.

## 8. Lärdomar som blev regler i den här skillen

- Exempel levereras med rättelsen, inte efter påstötning (steg 5).
- Sök efter strukna påståenden i hela repot, även speglar och docstrings (steg 4).
- Märk slutsatser av frånvaro: "API:t har ingen generativ-AI-typ" byggde på att värdet
  saknades i en enum, och står i registret som "Inference from absence" (steg 3).
- Changeloggen är också påståenden och ska stämma mot diffen (steg 7).
- Pusha allt och vänta på grön CI före merge; en commit som pushades under mergen
  förlorades ur mergen (steg 8).
