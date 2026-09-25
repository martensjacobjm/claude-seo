# Rapportmall för granskning

Mall för granskningsläget. Skriv på svenska om inget annat önskas. Varje fynd har
allvarlighet, evidenstagg och en konkret åtgärd. Kritisk och Hög kräver [V]. [H]-fynd
får högst Medel och skrivs ut med ordet "tumregel".

## Allvarlighet

| Nivå | Betyder | Kräver |
|------|---------|--------|
| Kritisk | Hindrar indexering eller visning helt (noindex, blockerad Googlebot, 5xx) | [V] |
| Hög | Påverkar synlighet tydligt (blockerad sökcrawler, fel canonical, avvecklad markup, falska recensioner) | [V] |
| Medel | Förbättring med dokumenterad eller rimlig effekt | [V] eller [H] |
| Låg | Finputs | valfri |
| Info | Rapporteras utan åtgärd (llms.txt, FAQPage, träningstokens) | valfri |

## Mall

```markdown
# Granskning: example.se (ÅÅÅÅ-MM-DD)

**Sajttyp:** lokalt företag / e-handel / publicist / SaaS / byrå
**Underlag:** URL hämtad / HTML-filer / skärmdumpar
**Kunde inte bedömas:** CWV-fältdata, Search Console, företagsprofiler (kräver ägarens data)

## Sammanfattning
Tre till fem meningar: hur sajten står sig och vad som ger mest effekt först.

## De fem viktigaste åtgärderna
1. [Nivå] [Tagg] Åtgärd. Varför, i en mening.
2. ...

## Crawlers och robots.txt
| Token | Typ | robots.txt | Effekt |
|-------|-----|-----------|--------|
| Googlebot | sök | tillåten | kan visas i Sök och AI-funktioner |
| OAI-SearchBot | sök | blockerad | visas inte i ChatGPT-sök [V] |
| GPTBot | träning | blockerad | affärsbeslut, ingen sökeffekt [V] |

## Teknik
- Indexering och utdrag
- Canonical, omdirigeringar, värdversion
- Titel, metabeskrivning, rubriker
- Core Web Vitals (fältdata om ägaren har den, annars risker sedda i koden)
- Bilder
- Mobil och HTTPS

## Strukturerad data
| Block | Typ | Status | Problem |
|-------|-----|--------|---------|
Utdata från `scripts/validate_schema.py` och förslag på JSON-LD med bara verkliga uppgifter.

## Lokalt (bara lokala företag)
- NAP: sajt, markup och profiler jämförda
- Google Business Profile, Bing Places, Apple Business Connect
- Recensionshantering
- Platssidor

## Innehåll
- Icke-kommodifierat innehåll: vad sajten har som ingen annan har
- Författare, datum, källor, förtroendesidor

## Mätning
- Search Console, rapporten för generativ AI, inställningen Search generative AI
- Bing Webmaster Tools, AI Performance, IndexNow

## Information (ingen åtgärd)
- /llms.txt: finns / saknas (404). Google Sök använder den inte.
```

## Formuleringar

| Läge | Fel | Rätt |
|------|-----|------|
| `/llms.txt` saknas | "Kritisk: skapa llms.txt" | "Info: /llms.txt saknas. Google Sök använder den inte; andra motorers användning är obekräftad. Ingen åtgärd." |
| Lång guide | "Dela upp i korta svarsblock" | Inget fynd. Google: ingen ideal sidlängd [V] |
| Generisk lista | "Skriv om för att bli citerad av AI" | "Hög [V]: sidan upprepar allmänna råd. Lägg till egen erfarenhet eller egen data." |
| OAI-SearchBot blockerad | "Låg: överväg att tillåta AI-botar" | "Hög [V]: OAI-SearchBot är blockerad, så sajten kan inte visas i ChatGPT-sök. Tillåt den om det önskas." |
| GPTBot blockerad | "Hög: avblockera GPTBot" | "Info: GPTBot (träning) är blockerad. Ingen effekt på ChatGPT-sök enligt OpenAI." |
| FAQPage finns | "Lägg till FAQ-schema för AI" | "Info [V]: FAQ-resultat visas inte i Google sedan 2026-05-07. Behåll innehållet om det hjälper läsaren." |
| HowTo finns | "Utöka HowTo-markupen" | "Hög [V]: HowTo ger inga rich results sedan 2023. Ta bort markupen, behåll instruktionerna." |
| Ingen författare | "Kritisk: lägg till E-E-A-T" | "Medel [H] (tumregel): lägg till synlig författare och datum." |
| NAP skiljer sig | "Kritisk: NAP-fel" | "Medel [H] (tumregel): telefonnumret i sidfoten skiljer sig från markupen. Använd samma nummer överallt." |
| Stjärnbetyg om egna företaget i markup | "Lägg till aggregateRating för stjärnor" | "Info [V]: Google visar inga stjärnor för recensioner ett företag markerar upp om sig självt." |

## Avslutning

Avsluta med vad ägaren själv behöver kontrollera: inställningen Search generative AI,
Search Console-data, företagsprofilernas uppgifter, och en baslinjeexport av rapporten för
generativ AI och Bing AI Performance.
