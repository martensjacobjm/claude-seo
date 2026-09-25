# Inventering: sökmönster och tabell

Steg 1 i SKILL.md. Kör mönstren över **hela** målskillen, inte bara SKILL.md. Mönstren
hittar kandidater; varje träff läses i sitt sammanhang innan den förs in i tabellen.

## 1. Sökmönster

Byt `MAL` mot målskillens mapp. `-n` ger radnummer, `-i` ignorerar skiftläge,
`-E` slår på utökade reguljära uttryck.

```bash
MAL=skills/seo-geo

# Procent, andelar, promille
grep -rnE '[0-9]+([.,][0-9]+)?[[:space:]]?(%|procent|percent|‰)' "$MAL"

# Multiplar och tillväxt ("3x", "2.5x more likely", "527% growth")
grep -rnE '\b[0-9]+([.,][0-9]+)?[[:space:]]?(x|times|gånger)\b' "$MAL"

# Korrelationer och koefficienter (0.737, r = 0.4)
grep -rnE '(\b0[.,][0-9]{2,}\b|\br[[:space:]]?=)' "$MAL"

# Intervall med enhet ("134-167 words", "40-60 ord", "1-3% density")
grep -rnE '\b[0-9]+[[:space:]]?(-|to|till)[[:space:]]?[0-9]+[[:space:]]?(words|ord|characters|tecken|ms|s|%|px|KB|MB)' "$MAL"

# Stora tal och användarsiffror ("900M", "1.5 billion", "2,5 miljarder")
grep -rnEi '\b[0-9]+([.,][0-9]+)?[[:space:]]?(k|m|b|t|million|billion|trillion|miljon|miljoner|miljard|miljarder)\b' "$MAL"

# Årtal och datum
grep -rnE '\b(19|20)[0-9]{2}(-[01][0-9](-[0-3][0-9])?)?\b' "$MAL"

# Versionsnummer (schema.org 30.1, Lighthouse 13, v3)
grep -rnE '\bv?[0-9]+\.[0-9]+(\.[0-9]+)?\b' "$MAL"

# Källhänvisningar utan källa
grep -rnEi '(studies show|research shows|data shows|according to|industry data|experts|studier visar|forskning visar|enligt|undersökningar)' "$MAL"

# Superlativ och absoluta ord
grep -rnEi '\b(always|never|only|best|optimal|guaranteed|must|all|every|no one|alltid|aldrig|enda|bäst|optimal|garanterat|måste|samtliga)\b' "$MAL"

# Rekommendationer och betyg som styr åtgärder
grep -rnEi '\b(critical|high|should|recommend|required|kritisk|hög|bör|rekommendera|krav)\b' "$MAL"

# Namngivna aktörer som ofta citeras utan primärkälla
grep -rnEi '\b(ahrefs|semrush|moz|sparktoro|brightlocal|backlinko|searchengineland|hubspot|gartner)\b' "$MAL"

# Bot-, API-, endpoint- och fältnamn (kontrolleras mot leverantörens docs)
grep -rnE '\b[A-Z][A-Za-z-]*(Bot|bot|API|Api)\b|`[a-zA-Z_./-]+`|/v[0-9]+/' "$MAL"

# URL:er: finns sidan kvar, säger den det som påstås?
grep -rnoE 'https?://[^ )>"]+' "$MAL"
```

Mönstren är breda med avsikt. Hellre hundra falska träffar att stryka än ett missat
påstående. Superlativ- och rekommendationsmönstren ger mest brus: läs dem snabbt och
för bara in de rader som påstår något om världen.

**Glöm inte det som inte syns i mönster:** blanka påståenden utan siffror ("AI-crawlers kör
inte JavaScript"), påståenden i tabellrubriker, viktningar i poängmodeller, standardvärden
i skript och argumenthjälp, exempelutdata som ser ut som riktiga data.

## 2. Sök i hela repot efter varje påstående

När en siffra eller regel ska strykas: sök efter den i hela repot, inklusive agenter,
tilläggsmappar, speglade kopior, docstrings, README, PDF-källor och tester.

```bash
grep -rnF '0.737' . --include='*.md' --include='*.py' --include='*.json'
grep -rnEi '134.?167' .
```

## 3. Inventeringstabell

En rad per påstående. Samma påstående på flera ställen: ett ID, alla platser listade.

```markdown
| ID | Plats (fil:rad) | Påstående (ordagrant) | Typ | Angiven källa | Nivå | Status | Primärkälla (URL, datum) | Citat | Åtgärd |
|----|-----------------|-----------------------|-----|---------------|------|--------|--------------------------|-------|--------|
| P01 | SKILL.md:88 | "Optimal passage length: 134-167 words" | regel | ingen | ? | Motsagd | developers.google.com/.../ai-optimization-guide, 2026-07-10 | "There's no ideal page length" | Stryk, till Borttagna |
| P02 | SKILL.md:140; agents/x.md:12 | "92% of AI Overview citations come from top-10 pages" | siffra | "Industry data" | ? | Overifierad | ingen hittad | | Stryk, till Borttagna |
```

**Typ:** siffra, datum, namn (API, bot, fält, produkt), regel (råd som styr betyg),
beskrivning (hur något fungerar), aktör (citerad studie eller firma).

**Status:** Bekräftad, Delvis, Motsagd, Föråldrad, Overifierad. Tom status betyder
ogranskat; tabellen är klar när ingen status är tom.

Tabellen är ett arbetsdokument. Den behöver inte ligga kvar i målskillen; det som ska ligga
kvar hamnar i evidensregistret. Spara den gärna i sessionens anteckningar eller bifoga den
som bilaga till rapporten.

## 4. Fördela arbetet

Över cirka 40 påståenden: dela på subagenter, en per fil eller källdomän. Ge varje
subagent samma tabellhuvud, samma statusvärden och regeln att aldrig fylla i citat ur minnet.
Slå ihop, deduplicera på ordalydelse, och kontrollera stickprov ur varje subagents rader.
