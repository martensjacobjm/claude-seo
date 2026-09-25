# Skills för claude.ai

Den här mappen gör om repots belagda SEO-kunskap till skills som går att ladda upp i
claude.ai och Claude Desktop. Källorna ligger här, de färdiga paketen i `dist/`.

## Paketen

| Paket | Vad det är |
|-------|------------|
| `dist/hemsida.skill` | Skapa, renovera och granska hemsida. Leder ett nybygge i nio faser (0 brief och faktablad, 1 strategi, 2 innehåll, 3 bygge, 4 teknisk SEO och AI-sök, 5 lokalt, 6 konvertering och mätning, 7 QA-grind, 8 lansering och uppföljning), har ett renoveringsläge som jämför repo mot livesajt och letar efter läckta hemligheter, och ett granskningsläge med rapportmall. Evidensnivåer [V]/[R]/[H], crawlertabell och robots.txt, teknisk checklista med Core Web Vitals, strukturerad data, lokalt företag, innehåll och mätning. Innehåller ett litet schemavalideringsskript. |
| `dist/skill-evidens.skill` | Byggs av en annan källmapp (`skill-evidens/`) och paketeras här när den mappen finns och har en giltig SKILL.md. |

## Varför inte repots egna skills direkt

Repots skills (till exempel `seo-geo`, `seo-schema`, `seo-technical`) är skrivna för
Claude Code. De hänvisar till `scripts/`-mappen, till `/seo`-kommandon, till subagenter
och till varandras referensfiler med repo-sökvägar. Inget av det finns i claude.ai, så
ett direktpaket skulle ge instruktioner som inte går att följa. `hemsida` tar i stället
in deras kunskap på svenska och bär med sig referensfilerna som kopior. Det enda skript
som följer med är schemavalideringen, eftersom den bara använder Pythons standardbibliotek.

## Hemsida som dirigent

`hemsida` är byggd för att fungera ensam, men använder andra skills när de finns i miljön:
claude-seo-pluginens `/seo`-kommandon i Claude Code (till exempel `/seo plan`, `/seo schema`,
`/seo audit`, `/seo google`), marketingskills (till exempel `copywriting`, `site-architecture`,
`form-cro`, `analytics-tracking`) och Jacobs claude.ai-skills (till exempel `astro`,
`webapp-testing`, `theme-factory`). Kartan per fas, med reserv när en skill saknas och vad
fasen ska leverera, står i `hemsida/references/skill-karta.md`.

Skillen kontrollerar alltid vilka skills som faktiskt finns och antar aldrig. Den skiljer
på Claude Code (plugin-kommandon, skript, hooks) och claude.ai (bara uppladdade skills).
Säger en delegerad skill något som strider mot hemsidas evidensregler, till exempel
`llms.txt`, fasta styckelängder, FAQPage för rich results eller egna stjärnbetyg i markup,
gäller hemsida och avvikelsen skrivs ut.

## En enda källa

Referensfilerna i `hemsida`-paketet skrivs inte för hand. `build.py` kopierar dem vid
varje bygge från repots kanoniska filer:

| I paketet | Från repot |
|-----------|------------|
| `references/geo-evidence.md` | `skills/seo-geo/references/geo-evidence.md` |
| `references/geo-examples.md` | `skills/seo-geo/references/geo-examples.md` |
| `references/ranking-signals.md` | `skills/seo/references/ranking-signals.md` |
| `references/schema-types.md` | `skills/seo/references/schema-types.md` |
| `references/cwv-thresholds.md` | `skills/seo/references/cwv-thresholds.md` |
| `references/local-schema-types.md` | `skills/seo/references/local-schema-types.md` |
| `references/eeat-framework.md` | `skills/seo/references/eeat-framework.md` |
| `references/local-eeat-evidence.md` | `skills/seo/references/local-eeat-evidence.md` |
| `scripts/validate_schema.py` | `hooks/validate-schema.py` |

Handskrivet i `hemsida/` är `SKILL.md` och de svenska referensfilerna: `rapportmall.md`,
`skapa-fas.md`, `skill-karta.md`, `faktablad-mall.md`, `qa-grind.md`, `renovera.md` och
`exempel-bygge.md`. De är inga kopior och ligger direkt i källmappen. Ändras en kanonisk
fil i repot: bygg om, så följer ändringen med.

## Bygga om

```
python3 claude-ai-skills/build.py
```

Skriptet paketerar varje undermapp som har en SKILL.md till `dist/<namn>.skill`,
validerar med skill-creators `quick_validate.py` om den finns (annars med inbyggda
kontroller av frontmatter och radgränser) och skriver en JSON-rapport. Bygget är
deterministiskt: samma källor ger byte-identiska paket, så en ombyggnad utan ändringar
ger ingen diff.

Användbara flaggor:

- `--check` bygger i en tillfällig mapp och misslyckas om paketen i `dist/` är inaktuella.
- `--only hemsida` bygger bara ett paket.
- `--strict` räknar mappar utan SKILL.md som fel.

Testerna ligger i `tests/test_claude_ai_skills.py` och körs med `python3 -m pytest tests -q`.
Ett av dem kontrollerar att `dist/hemsida.skill` är ombyggt efter senaste ändring.

## Ladda upp

Enligt Claudes hjälpcenter (kontrollerat 2026-09-25) laddas egna skills upp under
**Customize > Skills**: knappen "+", sedan "Create skill" och "Upload a skill". I det
svenska gränssnittet kan menynamnen skilja sig; i Desktop har Jacob hittills gått via
Inställningar och Skills. Skills kräver att kodkörning är påslagen ("Code execution and
file creation" under Settings > Capabilities på Free, Pro och Max).

Hjälpcentret beskriver uppladdningen som en ZIP-fil med skillmappen i roten. En
`.skill`-fil är just en sådan ZIP. Tar dialogen inte emot filen: byt ändelsen till `.zip`
och ladda upp igen, innehållet är detsamma.

En installerad skill uppdateras inte av sig själv. Efter en ombyggnad: ladda upp det nya
paketet och ersätt den gamla versionen.

## Versionshantering

`dist/` är versionshanterad, trots att repots `.gitignore` annars utesluter alla
`dist/`-mappar, så att Jacob kan ladda ner paketen direkt från GitHub. Undantaget står i
`.gitignore` (`!claude-ai-skills/dist/`). Paketen är små och byggs deterministiskt.
