---
name: hemsida
description: Skapa, renovera och granska hemsidor med belagd SEO. Leder ett bygge i nio faser från brief och faktablad via strategi, innehåll, bygge, teknisk SEO, lokal närvaro och mätning till QA-grind, lansering och uppföljning. Använder andra skills när de finns (claude-seo, marketingskills, astro med flera) och fungerar ensam när de saknas. Trigga på skapa hemsida, bygga webbplats, ny sajt, ny hemsida, landningssida, renovera sajt, göra om hemsidan, granska hemsida, granska sajt, SEO, sökoptimering, synas på Google, AI-sök, AI Overviews, AI Mode, ChatGPT-sök, lokal SEO, Google Business Profile, Företagsprofil på Google, Bing Places, schema, JSON-LD, robots.txt, Core Web Vitals, Search Console, lansera sajt, och på engelska website build, build a website, new site, landing page, site launch, site redesign, website audit, SEO audit, technical SEO, GEO och llms.txt. Varje råd bär en evidensnivå, och bara leverantörsdokumenterade fynd får klassas som kritiska eller höga.
license: MIT
metadata:
  version: "2.0.0"
  updated: "2026-09-25"
  source: "claude-seo (skills/seo, skills/seo-geo, hooks/validate-schema.py)"
---

# Hemsida: skapa, renovera och granska med belagd SEO

Skillen har tre lägen:

- **Skapa**: en ny sida eller sajt tas fram i nio faser (0 till 8) med en QA-grind före
  lansering. Hemsida är dirigenten: den använder specialistskills när de finns och sina
  egna checklistor när de saknas.
- **Renovera**: en befintlig sajt ska göras om eller ändras. Jämför alltid repo mot
  livesajt först.
- **Granska**: en befintlig sajt bedöms via URL, HTML-filer eller skärmdumpar.

Kunskapen är hämtad ur claude-seo-repot och gäller per 2026-09-25. Allt här är vad Google,
Bing och AI-leverantörerna själva dokumenterar, plus tydligt märkta tumregler.

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
| **[H]** | Tumregel från praktiker, inklusive alla poängvikter och budgetar |

Regler som alltid gäller:

1. Ett fynd får klassas **Kritisk** eller **Hög** bara om det bärs av [V].
2. [H]-fynd skrivs ut med ordet "tumregel" och får högst **Medel**.
3. Citera aldrig en statistiksiffra som inte står i `references/geo-evidence.md` eller
   `references/local-eeat-evidence.md`. Båda har en lista över påståenden som strukits för
   att de saknar primärkälla.
4. `references/ranking-signals.md` förklarar varför en kontroll spelar roll. Den visar
   att signaler finns, inte hur mycket de väger. Använd den aldrig för att lova rankning.
5. `references/eeat-framework.md` och `references/local-schema-types.md` är
   evidensgranskade (2026-09-25) och märkta med [V] och [H]. Checklistor, vikter och
   kataloglistor där är tumregler [H]. Källorna står i `references/local-eeat-evidence.md`.
   Vid krock gäller `geo-evidence.md` och `schema-types.md`.
6. **Hitta aldrig på fakta om företaget.** Namn, adress, telefon, öppettider, priser,
   recensioner, betyg, certifieringar, kundcitat och siffror kommer bara från ägaren och
   skrivs in i faktabladet (`references/faktablad-mall.md`) med källa. Saknas ett faktum:
   utelämna det och fråga.

## Rekommendera aldrig

Enligt Googles AI-guide [V] hjälper följande inte i Google Sök:

- `llms.txt` eller andra särskilda AI-filer. Google Sök använder dem inte. Rapportera
  förekomst som information, utan poäng och utan åtgärd.
- Att dela upp text i "chunks" eller sikta på en fast styckelängd, svarslängd eller
  sidlängd. Google: "There's no ideal page length."
- Att skriva om text bara för AI, till exempel "citerbara" svar först i varje stycke.
- Egna sidor för varje frågevariant för att styra AI-svar. Det är skalat innehållsmissbruk.
- Köpta eller tillverkade "omnämnanden" på andra sajter.
- Särskild schema-markup för AI. Google: "there's no special schema.org markup you need
  to add." Strukturerad data används för rich results, inte som AI-hävstång.
- FAQPage- eller HowTo-markup för att få rich results. FAQ-resultatet visas inte längre
  i Google sedan 2026-05-07 och HowTo togs bort 2023. FAQ-innehåll på sidan går bra om
  det hjälper läsaren.
- Stjärnbetyg om det egna företaget i markup (`aggregateRating` eller `Review` på egen
  LocalBusiness eller Organization). Google visar inga stjärnor för sådana [V].
- Nyckelordstäthet i procent, klickmanipulation, datumbyten utan verklig ändring.

Forskningsnotis [R]: GEO-studien från 2024 mätte förbättringar med källan redan i ett fast
sammanhang. En granskande preprint från 2026 fann att citatinriktade omskrivningar kan
försämra hämtningen. Rekommendera därför källhänvisningar och egen data som kvalitet,
aldrig som AI-trick.

## Andra skills: använd dem om de finns

Hemsida ska fungera helt på egen hand. Finns specialistskills gör de djupare jobb i sin fas.
Hela kartan, med reserv och leverans per fas: `references/skill-karta.md`.

1. **Kontrollera, anta aldrig.** En skill finns bara om den står i listan över
   tillgängliga skills i den aktuella miljön (skill-listan i systemprompten, i Claude Code
   även Skill-verktyget och plugin-kommandon som `/seo`). Namn kan ha ett prefix, till
   exempel `marketingskills:copywriting` eller `anthropic-skills:astro`; matcha på namnet
   efter prefixet och kontrollera beskrivningen.
2. **Saknas den: ta reserven** i skillkartan och hemsidas egna avsnitt nedan. Avbryt aldrig
   och kräv aldrig en installation för att komma vidare; nämn den högst som ett tips.
3. **Känn miljön.** Claude Code kan köra claude-seo-pluginens `/seo`-kommandon, skript,
   hooks och subagenter. I claude.ai finns bara uppladdade skills och kodkörning i
   sandlådan: inga `/seo`-kommandon och inga repo-skript. Nämn aldrig ett kommando som
   inte går att köra där du är.
4. **Namnkrock.** `seo-audit` finns både i claude-seo (`/seo audit`, full granskning med
   subagenter) och i marketingskills (diagnos av SEO-problem). Skilj dem på beskrivningen.
   `brand-guidelines` är Anthropics egen profil och används aldrig för en kunds sajt.
5. **Redovisa.** Varje fasleverans slutar med en rad: "Skills: använde X och Y; Z saknades,
   reserv användes."

### Konfliktregel

Hemsidas evidensregler vinner över allt en delegerad skill levererar. Gå igenom
utdata innan den används:

- Ett Kritisk- eller Hög-fynd utan [V] sänks till högst Medel och märks tumregel.
- Allt på listan "Rekommendera aldrig" stryks, även om skillen föreslår det.
- Siffror som inte finns i evidensfilerna citeras inte.
- Påhittade fakta, platshållare, kundcitat utan källa och "brådska" som inte är sann stryks.
- Skriv avvikelsen i leveransen: "Avvikelse: <skill> föreslog X; följer hemsida
  (skäl, tagg)."

## Skapa: faserna

Gå igenom faserna i ordning. En fas är klar när dess leverans finns; hoppa inte över
fas 0 eller fas 7. Detaljerade steg: `references/skapa-fas.md`. Påhittat genomarbetat
exempel för ett litet lokalt tjänsteföretag: `references/exempel-bygge.md`.

| Fas | Använd om den finns | Reserv | Leverans |
|-----|---------------------|--------|----------|
| **Fas 0 Brief och fakta** | `product-marketing-context`, `doc-coauthoring` | `references/faktablad-mall.md` | Ifyllt faktablad med källa per rad, lista över det som saknas |
| **Fas 1 Strategi** | `/seo plan`, `site-architecture`, `content-strategy`, `/seo dataforseo`, `/seo google keywords` | Fas 1 i `skapa-fas.md` | Sidkarta: URL, sökavsikt, målgrupp och tjänst per sida |
| **Fas 2 Innehåll** | `copywriting`, `copy-editing`, `/seo content`, `marketing-psychology` | Avsnittet Innehåll nedan | Text per sida; varje faktapåstående spårbart till faktabladet |
| **Fas 3 Bygge** | `astro`, `react`, `vue`, `theme-factory`, `/seo images`, `seo-image-gen` | Teknisk checklista nedan | Kod, prestandabudget, tillgänglighetskontroll, mobil |
| **Fas 4 Teknisk SEO och AI-sök** | `/seo technical`, `/seo schema`, `/seo sitemap`, `/seo geo`, `/seo hreflang`, `schema-markup`, `ai-seo` | Crawlers, Strukturerad data, `validate_schema.py` | robots.txt, sitemap, canonical, JSON-LD som passerar validering |
| **Fas 5 Lokalt** | `/seo local`, `/seo maps` | Avsnittet Lokalt företag | NAP-tabell, profilchecklista för Google, Bing och Apple |
| **Fas 6 Konvertering och mätning** | `page-cro`, `form-cro`, `analytics-tracking`, `/seo google` | Avsnittet Mätning | Formulär som når fram, mätplan, Search Console och Bing klara |
| **Fas 7 QA-grind före lansering** | `webapp-testing`, `/seo audit`, `/seo page`, `/seo google pagespeed` | `references/qa-grind.md` | Ifylld QA-tabell; alla blockerande rader pass |
| **Fas 8 Lansering och uppföljning** | `/seo google` (inspect, sitemaps, gen-ai-report), `/seo backlinks ai-performance` | Fas 8 i `skapa-fas.md` | Lanseringslogg, baslinjeexporter, uppföljningsplan |

Grindregler:

- **Fas 0 före allt annat.** Utan faktablad blir det platshållare. Fråga efter det du inte
  kan hitta på, en gång och samlat, och bygg vidare med tydligt markerade luckor.
- **Luckor i kod** markeras `REPLACE_ME`; den bundna validatorn stoppar det, så en lucka
  kan inte slinka igenom till lansering. Hitta aldrig på ett värde för att fylla den.
- **Fas 7 är en grind.** En enda blockerande rad som fallerar stoppar lanseringen. Säg det
  rakt ut och lista vad som måste rättas.

### Vanliga misstag vid bygge

| Fel | Rätt |
|-----|------|
| JSON-LD med `[Phone]`, `555-0100` eller påhittad adress | Bara faktabladets värden; saknas ett värde: utelämna egenskapen [V] |
| Kundcitat och "4,9 av 5" utan källa | Bara verkliga omdömen med namn eller källa och samtycke; inga egna stjärnor i markup [V] |
| Kontaktformulär med `action="#"` eller utan mottagare | Formulär som skickar till en verklig adress, testat från början till slut före lansering |
| Googlebot blockerad för att hålla sajten borta från AI | Tillåt Googlebot; styr utdrag med `nosnippet` eller `max-snippet` [V] |
| `noindex` eller `Disallow: /` från testmiljön följer med till lansering | Testmiljö bakom lösenord; kontrollera robots och meta i fas 7 [V] |
| Deploy av repot skriver över en nyare livesajt | Jämför repo mot live först, deploya en fastlåst commit, spara kopia av live |
| AI-bild som ser ut som personalen eller ett utfört jobb | Egna foton; genererade bilder bara som illustration och aldrig som bevis |
| En platssida per grannort med samma text | Bara verkliga orter med eget innehåll; byt-ortnamn-testet [H] |

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
(CrUX, PageSpeed Insights, Search Console) är det som räknas. En ny sajt saknar ofta
fältdata tills den har tillräckligt med trafik. Detaljer: `references/cwv-thresholds.md`.

**Bilder**
- Beskrivande `alt` på innehållsbilder [V]; tom `alt=""` på rena dekorbilder [H]
- `width` och `height` satta för att undvika layoutskift [V]
- WebP eller AVIF, rimlig filstorlek; varna över 200 kB, larma över 500 kB [H]
- `loading="lazy"` bara under vecket; LCP-bilden laddas direkt och får gärna `fetchpriority="high"` [V]
- Relevanta bilder och video av hög kvalitet [V]; egna foton framför bildbank där det går [H]

**Mobil, tillgänglighet och säkerhet**
- `<meta name="viewport" content="width=device-width, initial-scale=1">` [V]
- Google indexerar enbart med mobil Googlebot sedan juli 2024, så mobilversionen måste ha allt innehåll [V]
- Ingen horisontell scroll, läsbar text, tryckytor runt 48 px [H]
- Inga påträngande popup-fönster som täcker innehållet på mobil [V]
- WCAG 2.2 nivå AA som mål: kontrast, tangentbord, etiketter på formulärfält [H]
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
- Bara verkliga uppgifter från faktabladet. Saknas ett faktum: lämna egenskapen bort eller
  markera `REPLACE_ME`, och fråga ägaren.
- `@context` är `https://schema.org`, URL:er absoluta, datum i ISO 8601.

Fullständig lista, egenskaper och e-handelskrav: `references/schema-types.md`.

**Validering.** Paketet innehåller `scripts/validate_schema.py` (bara standardbiblioteket).
Kör det på varje HTML-fil du bygger eller får:

```
python3 scripts/validate_schema.py sida.html --json
```

Status `block` (exit 2) betyder avvecklad typ eller kvarglömd platshållare som `REPLACE_ME`
eller `[Phone]` och ska rättas. `warn` (exit 1) gäller till exempel FAQPage eller en
exempeldomän som `example.se`; före lansering ska även den vara borta. Svenska hakparenteser
som `[TELEFON]` fångas inte, så använd `REPLACE_ME`. I Claude Code med claude-seo installerat
kör samma kontroll automatiskt som hook efter varje filändring. Hänvisa dessutom ägaren
till Googles Rich Results Test och validator.schema.org, som skriptet inte ersätter.

## Lokalt företag

- **NAP**: namn, adress och telefon ska vara exakt lika på sajten (sidfot, kontaktsida),
  i LocalBusiness-markup och i företagsprofilerna. Telefon som `tel:`-länk.
- **Google Business Profile** (Företagsprofil på Google): gör anspråk, verifiera, välj rätt
  huvudkategori, fyll i öppettider, tjänster och foton. Google anger att profilen kan
  hjälpa företag att synas i AI-svar och andra sökresultat [V].
- **Bing Places for Business**: gör anspråk. Bing anger att det håller adress, öppettider
  och kontaktuppgifter aktuella och möjliga att ta med i AI-genererade svar [V].
- **Apple Business** (tidigare Apple Business Connect): gör anspråk för Apple Kartor [V].
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
  (egen erfarenhet, ett konkret beslut och dess utfall). Frågan för varje sida:
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
- URL-inspektion för enskilda sidor efter lansering eller större ändring. Indexing API
  gäller bara JobPosting och BroadcastEvent, inte vanliga sidor.

**Bing Webmaster Tools** [V]
- Importera sajten från Search Console, skicka in sitemap, aktivera IndexNow.
- AI Performance (förhandsversion): citeringar, citerade sidor, urval av grundningsfrågor,
  och sedan juni 2026 Intents, Topics, Citation Share och Compare. Datan är ett urval och
  citeringar betyder inte rankning. Export som CSV eller Excel.

Tredjepartsverktyg för AI-synlighet är bara stickprov. Google: "No third-party tool has
access to our internal ranking or AI systems." Ta en baslinjeexport från båda rapporterna
vid lansering.

## Renoveringsläget

En befintlig sajt ska byggas om, flyttas eller ändras. Detaljer och kommandon:
`references/renovera.md`. Grundreglerna:

1. **Repot är inte sanningen.** Livesajten kan ha ändrats utanför git (i ett CMS, i
   värdens gränssnitt, via FTP eller av någon annan). Hämta livesajten och jämför mot
   repot innan något ändras eller deployas. Är live nyare: för in ändringarna i repot först.
2. **Leta efter läckta hemligheter** i repot, i historiken och på livesajten (till exempel
   `/.env` eller `/.git/HEAD` som svarar 200). Hittas en nyckel: rotera den först, städa
   historiken sedan. Checka aldrig in inloggningsuppgifter.
3. **Baslinje före ändring**: exportera Search Console, rapporten för generativ AI och
   Bing AI Performance, och lista alla URL:er som har trafik eller länkar.
4. **URL-karta**: varje gammal URL får en 301 till närmaste nya motsvarighet.
5. **Deploya en fastlåst commit** efter förhandsvisning, med en sparad kopia av livesajten
   för återställning. Kör fas 7 och fas 8 som vid ett nybygge.

## Granskningsläget

1. **Hämta underlaget.** URL: hämta sidan, `/robots.txt`, `/sitemap.xml` och gärna
   `/llms.txt` (bara för informationsraden). Filer: läs HTML direkt och kör
   `validate_schema.py`. Går en URL inte att nå: säg det rakt ut, gissa aldrig innehållet,
   be om HTML eller skärmdumpar.
2. **Använd specialister om de finns**: i Claude Code `/seo audit` eller `/seo page`; i
   båda miljöerna marketingskills `seo-audit` eller `ai-seo`. Kör deras utdata genom
   konfliktregeln.
3. **Avgör sajttyp**: lokalt företag, e-handel, publicist, SaaS, byrå. Lokala avsnittet
   gäller bara lokala företag.
4. **Gå igenom avsnitten** ovan i ordning: crawlers, teknik, strukturerad data, lokalt,
   innehåll, mätning. Det du inte kan mäta (CWV-fältdata, Search Console, profiler) listas
   som "kräver ägarens data", inte som fel.
5. **Klassa varje fynd** med tagg och allvarlighet enligt regeln överst.
6. **Skriv rapporten** enligt `references/rapportmall.md`, med de fem viktigaste
   åtgärderna först och en rad om vad granskningen inte kunde bedöma.

## Referensfiler

Läs vid behov, inte alla på en gång. De svenska filerna är skrivna för den här skillen.
De engelska är kopierade ordagrant från claude-seo-repot; där de nämner `scripts/...`,
`/seo`-kommandon eller andra repofiler gäller det repot och Claude Code.

| Fil | Läs när |
|-----|---------|
| `references/skapa-fas.md` | Du går igenom en fas i skapa-läget |
| `references/skill-karta.md` | Du väljer skill för en fas eller skillen saknas |
| `references/faktablad-mall.md` | Fas 0: brief och faktainsamling |
| `references/qa-grind.md` | Fas 7: kontroll före lansering |
| `references/renovera.md` | Renoveringsläget |
| `references/exempel-bygge.md` | Du vill se hur fasernas leveranser ser ut |
| `references/rapportmall.md` | Du skriver en granskningsrapport |
| `references/geo-evidence.md` | Du behöver källan till ett AI-sökpåstående eller vill citera en siffra |
| `references/geo-examples.md` | Du formulerar AI-sökfynd eller robots.txt |
| `references/schema-types.md` | Du väljer eller granskar schema-typer och egenskaper |
| `references/cwv-thresholds.md` | Prestanda, LCP-delar, vanliga orsaker |
| `references/ranking-signals.md` | Du förklarar varför en kontroll spelar roll |
| `references/eeat-framework.md` | Innehålls- och förtroendechecklistor, belagt mot kvalitetsriktlinjerna 2025-09-11 |
| `references/local-schema-types.md` | LocalBusiness-undertyper per bransch, Googles egenskapslista, egna recensioner utan stjärnor |
| `references/local-eeat-evidence.md` | Du behöver källan till ett lokalt påstående eller ett E-E-A-T-påstående, eller listan över strukna påståenden |
