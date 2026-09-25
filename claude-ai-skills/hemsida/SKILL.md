---
name: hemsida
description: Skapa och granska hemsidor med belagd SEO. Använd när Jacob vill bygga en ny hemsida, webbplats, landningssida eller sida för ett lokalt företag så att den blir sökoptimerad från början, och när en befintlig sajt ska granskas via URL, HTML-filer eller skärmdumpar. Trigga på hemsida, webbplats, sajt, SEO, sökoptimering, granska sajt, granska hemsida, bygga hemsida, synas på Google, AI-sök, AI Overviews, AI Mode, ChatGPT-sök, Perplexity, Copilot, robots.txt, strukturerad data, schema, JSON-LD, Core Web Vitals, sidhastighet, Google Business Profile, Företagsprofil på Google, Bing Places, lokal SEO, Search Console, website audit, site review, SEO audit, build a website, technical SEO, GEO och llms.txt. Varje råd bär en evidensnivå, och bara leverantörsdokumenterade fynd får klassas som kritiska eller höga.
license: MIT
metadata:
  version: "1.0.0"
  updated: "2026-09-25"
  source: "claude-seo (skills/seo, skills/seo-geo, hooks/validate-schema.py)"
---

# Hemsida: bygga och granska med belagd SEO

Skillen har två lägen. **Byggläget** används när en ny sida eller sajt ska tas fram och
ska vara rätt från början. **Granskningsläget** används när en befintlig sajt ska
bedömas, via URL, uppladdade filer eller skärmdumpar. Kunskapen är hämtad ur
claude-seo-repot och gäller per 2026-09-25. Allt här är vad Google, Bing och
AI-leverantörerna själva dokumenterar, plus tydligt märkta tumregler.

Grundsatsen, från Googles guide för generativa AI-funktioner (uppdaterad 2026-07-10):
AI Overviews och AI Mode vilar på samma ranknings- och kvalitetssystem som vanlig sökning.
"Optimizing for generative AI search is optimizing for the search experience, and thus
still SEO." Bra SEO är därför också grunden för AI-sök.

## Evidensnivåer och allvarlighetsregel

Varje fynd och varje råd får en tagg.

| Tagg | Betyder |
|------|---------|
| **[V]** | Leverantörsdokumenterat: Google, Bing, OpenAI, Anthropic, Perplexity, Apple |
| **[R]** | Forskning (GEO-studien KDD 2024, en granskande preprint 2026) |
| **[H]** | Tumregel från praktiker, inklusive alla poängvikter |

Regler som alltid gäller:

1. Ett fynd får klassas **Kritisk** eller **Hög** bara om det bärs av [V].
2. [H]-fynd skrivs ut med ordet "tumregel" och får högst **Medel**.
3. Citera aldrig en statistiksiffra som inte står i `references/geo-evidence.md`.
   Avsnitt 5 där listar påståenden som strukits för att de saknar primärkälla.
4. `references/ranking-signals.md` förklarar varför en kontroll spelar roll. Den visar
   att signaler finns, inte hur mycket de väger. Använd den aldrig för att lova rankning.
5. `references/eeat-framework.md` och `references/local-schema-types.md` är äldre
   praktikerfiler. Använd deras checklistor och typlistor, men citera inga siffror
   därifrån. Vid krock gäller `geo-evidence.md` och `schema-types.md`.

## Rekommendera aldrig

Enligt Googles AI-guide [V] hjälper följande inte i Google Sök:

- `llms.txt` eller andra särskilda AI-filer. Google Sök använder dem inte. Rapportera
  förekomst som information, utan poäng och utan åtgärd.
- Att dela upp text i "chunks" eller sikta på en viss styckelängd eller sidlängd.
  Google: "There's no ideal page length."
- Att skriva om text bara för AI, till exempel "citerbara" svar först i varje stycke.
- Egna sidor för varje frågevariant för att styra AI-svar. Det är skalat innehållsmissbruk.
- Köpta eller tillverkade "omnämnanden" på andra sajter.
- Särskild schema-markup för AI. Google: "there's no special schema.org markup you need
  to add." Strukturerad data används för rich results, inte som AI-hävstång.
- FAQPage- eller HowTo-markup för att få rich results. FAQ-resultatet visas inte längre
  i Google sedan 2026-05-07 och HowTo togs bort 2023. FAQ-innehåll på sidan går bra om
  det hjälper läsaren.
- Nyckelordstäthet i procent, klickmanipulation, datumbyten utan verklig ändring.

Forskningsnotis [R]: GEO-studien från 2024 mätte förbättringar med källan redan i ett fast
sammanhang. En granskande preprint från 2026 fann att citatinriktade omskrivningar kan
försämra hämtningen. Rekommendera därför källhänvisningar och egen data som kvalitet,
aldrig som AI-trick.

## Crawlers och robots.txt

| Token | Styr | Effekt av Disallow |
|-------|------|--------------------|
| Googlebot | Google Sök inklusive AI Overviews och AI Mode | Sidan försvinner ur Google Sök helt |
| Google-Extended | Gemini-träning och grundning (ingen egen crawler) | Påverkar inte Sök eller rankning |
| bingbot | Bings index, Copilot, AI-sammanfattningar i Bing | Försvinner ur Bing |
| OAI-SearchBot | ChatGPT-sök | Visas inte i ChatGPT-sök (cirka ett dygn) |
| GPTBot | OpenAI-träning | Bara träning |
| ChatGPT-User | Hämtningar som användaren startar | robots.txt "may not apply" |
| PerplexityBot | Perplexitys sökresultat | Crawlas inte för Perplexity-sök |
| Perplexity-User | Hämtningar som användaren startar | Ignorerar i regel robots.txt |
| Claude-SearchBot | Claudes sökindex | Indexeras inte för Claude-sök |
| Claude-User | Hämtningar som användaren startar | Kan minska synlighet |
| ClaudeBot | Anthropic-träning | Bara träning |
| Applebot | Spotlight, Siri, Safari | Försvinner ur Apples sökfunktioner |
| Applebot-Extended | Apple-träning | Bara träning |
| CCBot | Common Crawl | Utesluts ur framtida crawlningar |

Alla rader är [V]. Sök- och användartokens ska vara tillåtna om sajten vill synas i
AI-sök. Att blockera träningstokens är ett affärsbeslut utan dokumenterad effekt på
synlighet. Vill någon hålla en sida borta från AI Overviews: blockera aldrig Googlebot,
använd `nosnippet`, `data-nosnippet` eller `max-snippet`. För Bing styr
`<meta name="bingbot" content="noarchive">` eller `nocache` användningen i chattsvar.

Standardfil när sajten vill synas i AI-sök men inte bidra till träning:

```
User-agent: Googlebot
User-agent: bingbot
User-agent: OAI-SearchBot
User-agent: PerplexityBot
User-agent: Claude-SearchBot
User-agent: Claude-User
User-agent: Applebot
Allow: /

User-agent: GPTBot
User-agent: ClaudeBot
User-agent: Google-Extended
User-agent: Applebot-Extended
User-agent: CCBot
Disallow: /

User-agent: *
Allow: /

Sitemap: https://www.example.se/sitemap.xml
```

Vill ägaren tillåta träning: ta bort Disallow-blocket. Lägg aldrig till `anthropic-ai`,
`Bytespider` eller `cohere-ai` på eget initiativ; deras syfte är inte verifierat.

## Teknisk checklista

**Indexering och crawlning**
- Viktiga sidor svarar 200, har ingen oavsiktlig `noindex` och är inte blockerade i robots.txt [V]
- Sidan får visas med utdrag: ingen `nosnippet`, `max-snippet:0` eller `data-nosnippet` på huvudinnehållet [V]
- Canonical pekar på sidan själv eller på avsedd URL, och är samma i server-HTML och efter JavaScript [V]
- `noindex`, canonical, titel, metabeskrivning och strukturerad data finns i den första HTML-responsen. Google renderar inte JavaScript på sidor som svarar annat än 200 [V]
- Kritiskt innehåll finns i initial HTML, eftersom OpenAI, Anthropic och Perplexity inte dokumenterar rendering [H]
- XML-sitemap finns, är giltig och nämns i robots.txt [V]
- Viktiga sidor nås inom tre klick från startsidan [H]
- Omdirigeringar: 301 för permanenta flyttar, inga kedjor [H]
- En värdversion: https och antingen www eller utan, övriga omdirigeras [V]
- Flera språk: korrekt hreflang med självreferens och ömsesidiga länkar [V]
- IndexNow för Bing och andra motorer utom Google [V]

**Titel, beskrivning och rubriker**
- Unik `<title>` per sida som beskriver sidan och matchar sökavsikten [V]; ungefär 50 till 60 tecken [H]
- Unik metabeskrivning som sammanfattar sidan; ungefär 150 till 160 tecken [H]
- En tydlig H1 och logisk H2/H3-struktur med beskrivande rubriker [V]
- Semantisk HTML (`main`, `article`, `nav`, `header`, `footer`) är bra men inget krav [V]
- Beskrivande, korta URL:er med bindestreck [H]

**Core Web Vitals** (fältdata, 75:e percentilen, per sida och per origin) [V]

| Mått | Bra | Behöver förbättras | Dåligt |
|------|-----|--------------------|--------|
| LCP | högst 2,5 s | 2,5 till 4,0 s | över 4,0 s |
| INP | högst 200 ms | 200 till 500 ms | över 500 ms |
| CLS | högst 0,1 | 0,1 till 0,25 | över 0,25 |

INP ersatte FID 2024. Nämn aldrig FID. Labbdata (Lighthouse) är för felsökning; fältdata
(CrUX, PageSpeed Insights, Search Console) är det som räknas. Detaljer och vanliga orsaker:
`references/cwv-thresholds.md`.

**Bilder**
- Beskrivande `alt` på innehållsbilder [V]; tom `alt=""` på rena dekorbilder [H]
- `width` och `height` satta för att undvika layoutskift [V]
- WebP eller AVIF, rimlig filstorlek; varna över 200 kB, larma över 500 kB [H]
- `loading="lazy"` bara under vecket; LCP-bilden laddas direkt och får gärna `fetchpriority="high"` [V]
- Relevanta bilder och video av hög kvalitet [V]; egna foton framför bildbank där det går [H]

**Mobil och säkerhet**
- `<meta name="viewport" content="width=device-width, initial-scale=1">` [V]
- Google indexerar enbart med mobil Googlebot sedan juli 2024, så mobilversionen måste ha allt innehåll [V]
- Ingen horisontell scroll, läsbar text, tryckytor runt 48 px [H]
- HTTPS överallt, inget blandat innehåll [V]

## Strukturerad data

- Använd JSON-LD i server-renderad HTML [V]. Produktmarkup via JavaScript kan göra
  Shopping-crawlningar mer sällsynta och mindre pålitliga [V].
- Stödda typer att föreslå: Organization, LocalBusiness (mest specifika undertypen),
  WebSite (sajtnamn), BreadcrumbList, Article/BlogPosting, Person, ProfilePage,
  Product med Offer, Service, Event, VideoObject, Recipe, JobPosting, Course,
  DiscussionForumPosting, QAPage.
- Ingen rich result i Google: FAQPage (sedan 2026-05-07). Befintlig markup är ofarlig,
  rapportera som Info.
- Avvecklade, föreslå aldrig: HowTo, SpecialAnnouncement, CourseInfo, EstimatedSalary,
  LearningVideo, VehicleListing, Practice problem. ClaimReview fasas ut.
- Recensioner: inga falska eller odeklarerat ersatta recensioner, varken på sidan eller i
  markup [V, 2026-07-24]. Ett företag som märker upp recensioner om sig självt får ingen
  stjärnvisning i Google [V].
- Bara verkliga uppgifter. Hittar du inte ett faktum: lämna egenskapen bort eller markera
  den tydligt som att fylla i, och fråga ägaren.
- `@context` är `https://schema.org`, URL:er absoluta, datum i ISO 8601.

Fullständig lista, egenskaper och e-handelskrav: `references/schema-types.md`.

**Validering.** Paketet innehåller `scripts/validate_schema.py` (bara standardbiblioteket).
Kör det på varje HTML-fil du bygger eller får:

```
python3 scripts/validate_schema.py sida.html --json
```

Status `block` betyder avvecklad typ eller kvarglömd platshållare och ska rättas. `warn`
gäller till exempel FAQPage. Hänvisa dessutom ägaren till Googles Rich Results Test och
validator.schema.org, som skriptet inte ersätter.

## Lokalt företag

- **NAP**: namn, adress och telefon ska vara exakt lika på sajten (sidfot, kontaktsida),
  i LocalBusiness-markup och i företagsprofilerna. Telefon som `tel:`-länk.
- **Google Business Profile** (Företagsprofil på Google): gör anspråk, verifiera, välj rätt
  huvudkategori, fyll i öppettider, tjänster och foton. Google anger att profilen kan
  hjälpa företag att synas i AI-svar och andra sökresultat [V].
- **Bing Places for Business**: gör anspråk. Bing anger att det håller adress, öppettider
  och kontaktuppgifter aktuella och möjliga att ta med i AI-genererade svar [V].
- **Apple Business Connect**: gör anspråk för Apple Kartor och Siri [H].
- **LocalBusiness-markup**: mest specifika undertyp (till exempel `Plumber`, `Dentist`,
  `Restaurant`), `name`, `address` som PostalAddress, `telephone`, `url`,
  `openingHoursSpecification`, `geo` med fem decimaler, `image`, `@id` per plats.
  Bara verkliga fakta. Typlista per bransch: `references/local-schema-types.md`.
- **Recensioner**: aldrig falska, köpta eller odeklarerat ersatta recensioner, och ingen
  recensionsgrind som sållar missnöjda kunder innan de skickas till Google [V]. Be alla
  kunder lika, svara på recensioner.
- **Platssidor**: en sida per verklig ort eller tjänst med eget innehåll (lokala bilder,
  personal, uppdrag). Byt-ortnamn-testet: går texten att använda för en annan stad efter
  att bara ortnamnet bytts är det en dörrsida [H]. Fler än 30 platssidor kräver extra
  granskning, fler än 50 kräver att ägaren motiverar dem [H].

## Innehåll

- **Icke-kommodifierat innehåll** [V]. Googles egen kontrast: "7 Tips for First-Time
  Homebuyers" (samma råd som alla andra) mot "Why We Waived the Inspection & Saved Money"
  (egen erfarenhet, ett konkret beslut och dess utfall). Granskningsfrågan för varje sida:
  vad finns här som ingen annan sida på webben har?
- **Egen erfarenhet och egen data**: fallstudier, egna foton, mätningar, priser, processer [V].
- **E-E-A-T** är ingen rankningsfaktor i sig (Google) men sammanfattar vad kvalitetssystemen
  letar efter. Checklistor: `references/eeat-framework.md`.
- **Författarskap**: synlig författare med kort presentation och länk till en
  författarsida; Person-markup med `sameAs` till verkliga profiler [H].
- **Datum**: synligt publicerings- och uppdateringsdatum som stämmer med
  `datePublished`/`dateModified`. Ändra datum bara vid verklig ändring; Google kallar
  datumbyten för att verka färsk en varningssignal [V].
- **Förtroende**: kontaktuppgifter, om oss, organisationsnummer, integritetspolicy,
  villkor, tydliga priser och returvillkor för e-handel [H, i linje med Googles riktlinjer].
- **Källor**: hänvisa till verifierbara källor; Bing: "Examples, data, and cited sources
  help build trust" [V].
- **Struktur för läsaren**: rubriker, stycken, listor och tabeller där de hjälper [V].
- AI-skriven text är tillåten om den tillför verkligt värde och granskas av en människa [V].
  Generisk text utan egen insikt är svag oavsett hur den skrivits.

Mer om hur Googles system väger kvalitet: `references/ranking-signals.md`.

## Mätning

**Google Search Console** [V]
- Verifiera domänen (DNS), skicka in sitemap, följ indexeringsrapporten (Sidor) och Core Web Vitals.
- Resultatrapporten (webbsökning) räknar även AI Overviews och AI Mode.
- Rapporten för generativ AI (alla sajter sedan 2026-08-31): bara visningar, med
  dimensionerna sidor, länder, enheter och datum. Inga sökfrågor, inga klick, max 1 000
  rader, datum i Stillahavstid. Finns inte i API:t; exportera från gränssnittet.
- Inställningar > Search generative AI ska stå på "Include" (standard). Skillen kan inte
  läsa det; be ägaren bekräfta.
- URL-inspektion för enskilda sidor efter lansering eller större ändring.

**Bing Webmaster Tools** [V]
- Importera sajten från Search Console, skicka in sitemap, aktivera IndexNow.
- AI Performance (förhandsversion): citeringar, citerade sidor, urval av grundningsfrågor,
  och sedan juni 2026 Intents, Topics, Citation Share och Compare. Datan är ett urval och
  citeringar betyder inte rankning. Export som CSV eller Excel.

Tredjepartsverktyg för AI-synlighet är bara stickprov. Google: "No third-party tool has
access to our internal ranking or AI systems." Ta en baslinjeexport från båda rapporterna
vid lansering.

## Byggläget

Fråga först efter det du inte kan hitta på: företagsnamn, adress, telefon, öppettider,
tjänster, orter, priser, egna bilder, vem som skriver texterna, och om AI-träning ska
tillåtas. Bygg sedan i den här ordningen och bocka av innan leverans:

1. Sidstruktur: en sida per tjänst, en per verklig ort, om oss, kontakt, integritet. Korta URL:er.
2. Varje sida: unik title, metabeskrivning, en H1, logiska rubriker, canonical till sig själv.
3. Innehåll med egen erfarenhet, egna bilder, författare och datum där det passar.
4. Bilder med alt, width/height, moderna format; LCP-bilden utan lazy loading.
5. Viewport, responsiv layout, HTTPS, inga tunga skript före innehållet.
6. JSON-LD: Organization och WebSite på startsidan, LocalBusiness på kontakt eller
   platssida, BreadcrumbList, Article/BlogPosting för artiklar. Kör `validate_schema.py`.
7. robots.txt enligt mallen ovan, XML-sitemap, 404-sida som svarar 404.
8. Open Graph (`og:title`, `og:description`, `og:image`, `og:url`) för delning [H].
9. Efter lansering: Search Console, Bing Webmaster Tools, Google Business Profile,
   Bing Places, baslinjeexport.

Leverera koden med en kort lista över vad som ännu måste fyllas i av ägaren.

## Granskningsläget

1. **Hämta underlaget.** URL: hämta sidan, `/robots.txt`, `/sitemap.xml` och gärna
   `/llms.txt` (bara för informationsraden). Filer: läs HTML direkt och kör
   `validate_schema.py`. Går en URL inte att nå: säg det rakt ut, gissa aldrig innehållet,
   be om HTML eller skärmdumpar.
2. **Avgör sajttyp**: lokalt företag, e-handel, publicist, SaaS, byrå. Lokala avsnittet
   gäller bara lokala företag.
3. **Gå igenom avsnitten** ovan i ordning: crawlers, teknik, strukturerad data, lokalt,
   innehåll, mätning. Det du inte kan mäta (CWV-fältdata, Search Console, profiler) listas
   som "kräver ägarens data", inte som fel.
4. **Klassa varje fynd** med tagg och allvarlighet enligt regeln överst.
5. **Skriv rapporten** enligt `references/rapportmall.md`, med de fem viktigaste
   åtgärderna först och en rad om vad granskningen inte kunde bedöma.

## Referensfiler

Läs vid behov, inte alla på en gång. Filerna är kopierade ordagrant från claude-seo-repot
och är på engelska. Där de nämner `scripts/...`, `/seo`-kommandon eller andra repofiler
gäller det repot; de finns inte här.

| Fil | Läs när |
|-----|---------|
| `references/rapportmall.md` | Du skriver en granskningsrapport |
| `references/geo-evidence.md` | Du behöver källan till ett AI-sökpåstående eller vill citera en siffra |
| `references/geo-examples.md` | Du formulerar AI-sökfynd eller robots.txt |
| `references/schema-types.md` | Du väljer eller granskar schema-typer och egenskaper |
| `references/cwv-thresholds.md` | Prestanda, LCP-delar, vanliga orsaker |
| `references/ranking-signals.md` | Du förklarar varför en kontroll spelar roll |
| `references/eeat-framework.md` | Innehålls- och förtroendechecklistor (siffrorna där är inte belagda) |
| `references/local-schema-types.md` | LocalBusiness-undertyper per bransch (siffrorna där är inte belagda) |
