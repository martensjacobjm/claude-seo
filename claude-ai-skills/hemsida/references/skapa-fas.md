# Skapa: faserna i detalj

Varje fas har mål, steg och en leverans. Vilken skill som tar fasen djupare står i
`skill-karta.md`; stegen här räcker när ingen skill finns. Taggar enligt SKILL.md.

## Fas 0 Brief och fakta

Mål: veta vad sajten ska uppnå och ha alla fakta om företaget från ägaren.

1. Ställ briefens frågor i `faktablad-mall.md`, samlat och en gång.
2. Fyll i faktabladet med källa per rad. Uppgifter utan underlag markeras "ej styrkt".
3. Avgör läge: finns en befintlig sajt som ska ersättas gäller även `renovera.md`.

Leverans: faktablad, listan Saknas, en mening om sajtens mål.

## Fas 1 Strategi

Mål: en sidkarta där varje sida har ett tydligt jobb.

1. **Målgrupp och avsikt.** Skriv för varje tjänst vad kunden söker och varför:
   informativ, jämförande, kommersiell, brådskande eller lokal avsikt.
2. **Sökord.** Utgå från kundens språk och ägarens erfarenhet. Sökvolym tas bara från ett
   verktyg (DataForSEO, Keyword Planner, Search Console för en befintlig sajt). Finns inget
   verktyg: ange ingen volym, rangordna efter affärsvärde.
3. **Arkitektur.** En sida per huvudtjänst, en per verklig ort, om oss, kontakt,
   integritet. Korta URL:er med bindestreck [H]. Viktiga sidor inom tre klick [H].
4. **Flera språk?** Planera URL-struktur per språk och hreflang redan nu [V].
5. **Många liknande sidor?** Varje sida måste ha eget innehåll. Byt-ortnamn-testet [H].

Leverans: sidkarta som tabell (URL, sidtyp, avsikt, målgrupp, tjänst eller ort, H1-förslag).

## Fas 2 Innehåll

Mål: text som bara det här företaget kunde ha skrivit.

1. **Det unika först.** Egna uppdrag, egna foton, konkreta beslut och utfall [V].
2. **Varje faktapåstående** pekar på en rad i faktabladet. Inget "över 500 nöjda kunder"
   utan källa.
3. **Omdömen** bara verkliga, med namn eller källa och samtycke.
4. **Titel och metabeskrivning** per sida, unika [V]; längder enligt tumregel [H].
5. **Rubriker** som beskriver innehållet, en H1 per sida [V].
6. **Förtroendesidor**: om oss med verkliga personer, kontakt, integritetspolicy.
7. **Människa granskar** all AI-skriven text innan publicering [V].

Leverans: text per sida med titel, metabeskrivning och H1, plus en lista över påståenden
som väntar på underlag.

## Fas 3 Bygge

Mål: snabb, tillgänglig, mobilvänlig sajt där allt viktigt finns i första HTML-svaret.

1. **Teknikval.** Innehållssajt: statisk generering (till exempel Astro) [H]. App med
   inloggning: React eller Vue med SSR eller SSG. Ren klientrendering ger tom initial HTML
   för crawlers som inte kör JavaScript [H]. Befintligt CMS: behåll om ägaren kan det.
2. **Semantisk HTML**: `header`, `nav`, `main`, `footer`, rubriknivåer i ordning [V].
3. **Prestandabudget** [H], mät i labb nu och i fält efter lansering:
   - LCP-bilden under 200 kB, i WebP eller AVIF, utan `loading="lazy"`
   - Så lite JavaScript som möjligt före innehållet; inga tunga skript i `head`
   - Typsnitt: högst två familjer, `font-display: swap`
   - `width` och `height` på alla bilder och inbäddningar mot CLS [V]
4. **Tillgänglighet** med WCAG 2.2 AA som mål [H]: kontrast, fokusmarkering, tangentbord,
   etiketter på fält, alt-text. E-handel kan omfattas av lagen om vissa produkters och
   tjänsters tillgänglighet (gäller sedan 2025-06-28, mikroföretag med tjänster undantagna).
   Det är juridik; låt ägaren bekräfta.
5. **Mobil**: viewport, ingen horisontell scroll, tryckytor runt 48 px [H], samma innehåll
   som på dator [V].
6. **Testmiljö** bakom lösenord, inte bara `noindex` eller robots.txt [V].

Leverans: körbar kod, budgeten ifylld med labbvärden, lista över kända avvikelser.

## Fas 4 Teknisk SEO och AI-sök

1. **robots.txt** enligt mallen i SKILL.md och ägarens beslut om träning.
2. **XML-sitemap** med bara indexerbara, kanoniska URL:er som svarar 200; nämn den i
   robots.txt [V].
3. **Canonical** på varje sida, självrefererande om inget annat är avsett [V].
4. **En värdversion**: https, www eller utan, övriga 301 [V].
5. **404-sida** som svarar med status 404, inte 200 [V].
6. **hreflang** bara vid flera språk: självreferens, ömsesidiga länkar, `x-default` [V].
7. **JSON-LD** med bara faktabladets värden: Organization och WebSite på startsidan,
   LocalBusiness (mest specifika undertyp) för lokala företag, BreadcrumbList, Service
   eller Product där det passar, Article för artiklar.
8. **Validera**: `python3 scripts/validate_schema.py <fil> --json` på varje sida. Både
   `block` och `warn` ska vara borta före lansering. Därefter Rich Results Test.
9. **Utdrag**: ingen `nosnippet` eller `max-snippet:0` på sidor som ska synas [V].
10. **Open Graph** (`og:title`, `og:description`, `og:image`, `og:url`) för delning [H].

Leverans: robots.txt, sitemap.xml, JSON-LD per sidtyp, valideringsutdata.

## Fas 5 Lokalt

Bara för företag med kunder på en plats eller inom ett område.

1. **NAP-tabell**: ett namn, en adress, ett telefonnummer, exakt lika överallt.
2. **Google Business Profile**: anspråk, verifiering, huvudkategori, tjänster, öppettider,
   egna foton. Tar företaget inte emot kunder på adressen: ange serviceområde och dölj
   adressen enligt Googles riktlinjer [V].
3. **Bing Places for Business** och **Apple Business**: anspråk [V].
4. **Recensioner**: be alla kunder lika, ingen recensionsgrind, svara på omdömen [V].
5. **Platssidor** bara för verkliga orter med eget innehåll [H].

Leverans: NAP-tabell, checklista per profil med status.

## Fas 6 Konvertering och mätning

1. **Ett tydligt nästa steg** per sida: ring, boka, skicka förfrågan.
2. **Formulär som når fram**: verklig mottagare, bekräftelse till besökaren, skydd mot
   skräp (till exempel ett dolt honungsfält), testat hela vägen. Aldrig `action="#"`.
3. **Telefon** som `tel:`-länk, e-post synlig.
4. **Mätplan**: vilka händelser (formulär skickat, klick på telefon) och var de syns.
5. **Samtycke**: analyskakor som inte är nödvändiga kräver samtycke enligt lagen om
   elektronisk kommunikation. Juridik; låt ägaren välja lösning.
6. **Search Console**: domänegendom via DNS, sitemap inskickad [V]. Inställningen Search
   generative AI på "Include" (ägaren bekräftar).
7. **Bing Webmaster Tools**: importera från Search Console, IndexNow [V].

Leverans: formulärtest med datum och mottagen testförfrågan, mätplan, verifierade konton.

## Fas 7 QA-grind

Gå igenom `qa-grind.md` rad för rad. Varje rad får pass, fail eller "ej tillämplig" med
belägg (kommandoutdata, skärmdump, URL). En blockerande fail stoppar lanseringen.

Leverans: ifylld QA-tabell.

## Fas 8 Lansering och uppföljning

**Lanseringsdagen**
1. Deploya en fastlåst commit eller version; spara vad som låg ute innan.
2. Kontrollera direkt på produktionsadressen: robots.txt, meta robots, canonical, sitemap,
   https-omdirigering, formulär. Testmiljöns `noindex` får inte ha följt med.
3. Skicka in sitemap i Search Console och Bing Webmaster Tools [V].
4. Begär indexering för startsidan och de viktigaste sidorna via URL-inspektion [V].
   Indexing API gäller bara JobPosting och BroadcastEvent [V].
5. IndexNow för Bing och andra motorer som stöder det [V].
6. Renovering: kontrollera att varje gammal URL ger 301 till rätt ny.

**Första veckorna**
- Följ indexeringsrapporten (Sidor) i Search Console, varje vecka första månaden [H].
- Rätta sidor som är "Crawlad men inte indexerad" genom att förbättra innehållet, inte
  genom att skicka in dem igen.
- CrUX-fältdata kommer först när sajten har tillräckligt med trafik [V]; till dess gäller
  labbvärden.

**Baslinje och sedan löpande**
- Exportera rapporten för generativ AI och Bing AI Performance vid lansering och sedan
  månadsvis [H]. Bara visningar respektive citeringar; ingen rankning.
- Följ upp företagsprofiler, recensioner och formulärinflöde.
- Ny granskning efter tre månader med granskningsläget [H].

Leverans: lanseringslogg (datum, commit, kontroller, inskick), baslinjeexporter, plan för
uppföljning med datum.
