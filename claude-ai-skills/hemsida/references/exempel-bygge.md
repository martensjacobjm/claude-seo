# Genomarbetat exempel: litet lokalt tjänsteföretag

**Påhittat exempel.** Företaget, personerna, adressen och alla uppgifter nedan är
uppdiktade för att visa hur fasernas leveranser ser ut. Domänen `example.se` är en
exempeldomän. Använd aldrig något härifrån som fakta om ett verkligt företag.

Uppdrag: "Exempel VVS AB" i Växjö, två anställda, vill ha en ny sajt som ger fler
förfrågningar om badrumsrenovering och akuta läckor. Ingen sajt finns i dag.

## Fas 0 Brief och fakta (utdrag)

| Uppgift | Värde | Källa |
|---------|-------|-------|
| Namn utåt | Exempel VVS | ägaren, 2026-09-20 |
| Adress | Exempelgatan 1, 352 30 Växjö | ägaren, 2026-09-20 |
| Tar emot kunder på adressen? | nej, bara kontor | ägaren |
| Telefon | saknas (nytt nummer beställt) | |
| Öppettider | mån till fre 07.00 till 16.00, akut dygnet runt | ägaren |
| Område | Växjö, Alvesta (verkliga uppdrag båda) | ägaren, jobblista |
| Behörighet | ägaren uppger branschbehörighet | ej styrkt, intyg begärt |
| Omdömen | inga insamlade | |
| Foton | 14 egna bilder från fem badrum | ägaren äger rättigheterna |
| AI-träning | ägaren vill inte bidra | beslut 2026-09-20 |

Saknas: telefon, organisationsnummer, intyg för behörighet, priser.
Skills: använde `product-marketing-context`; `doc-coauthoring` saknades, reserv användes.

## Fas 1 Strategi: sidkarta

| URL | Sidtyp | Avsikt | Tjänst eller ort |
|-----|--------|--------|------------------|
| / | start | kommersiell, lokal | alla |
| /badrumsrenovering/ | tjänst | kommersiell | badrum |
| /akut-vattenlacka/ | tjänst | brådskande | akut |
| /omraden/alvesta/ | ort | lokal | Alvesta, med två egna uppdrag |
| /projekt/badrum-teleborg-2026/ | fallstudie | informativ | badrum |
| /om-oss/, /kontakt/, /integritet/ | förtroende | | |

Sökvolym: inget verktyg fanns, så ingen volym anges; ordningen följer ägarens affärsvärde.
Ingen egen Växjösida: startsidan täcker Växjö, och en ortsida till med samma text vore en
dörrsida.

## Fas 2 Innehåll (utdrag)

- H1 på badrumssidan: "Badrumsrenovering i Växjö och Alvesta".
- Kärnan är fallstudien: vad kunden ville, vad som hittades bakom kakelväggen, hur lång
  tid det tog, foton före och efter, allt från ägarens anteckningar.
- Inga siffror som "hundratals nöjda kunder"; inga omdömen förrän verkliga finns.
- Behörigheten nämns inte förrän intyget är sett.

## Fas 3 Bygge

- Astro, statisk utdata; ett typsnitt; hjältebild 140 kB i AVIF med `fetchpriority="high"`.
- Budget i labb (Lighthouse mobil): LCP 1,9 s, CLS 0,02, TBT 40 ms. Fältdata saknas än.

## Fas 4 Teknisk SEO och AI-sök

- robots.txt: standardfilen i SKILL.md (sök tillåten, träning blockerad enligt beslutet).
- JSON-LD på kontaktsidan, bara faktabladets värden; telefon utelämnad tills den finns:

```json
{"@context": "https://schema.org", "@type": "Plumber", "@id": "https://www.example.se/#foretag",
 "name": "Exempel VVS", "url": "https://www.example.se/",
 "address": {"@type": "PostalAddress", "streetAddress": "Exempelgatan 1",
  "postalCode": "352 30", "addressLocality": "Växjö", "addressCountry": "SE"},
 "areaServed": ["Växjö", "Alvesta"]}
```

- Validering: `warn` för exempeldomän och exempelgata. I ett verkligt bygge ska båda vara
  de riktiga värdena innan fas 7 kan passera.

## Fas 5 Lokalt

- Google Business Profile som serviceområdesföretag, adressen dold eftersom inga kunder tas
  emot där. Bing Places och Apple Business med samma namn och nummer.
- NAP-tabell väntar på telefonnumret; ingen profil publiceras med ett tillfälligt nummer.

## Fas 6 Konvertering och mätning

- Offertformulär till ägarens e-post via värdens formulärtjänst, honungsfält mot skräp,
  testförfrågan mottagen 2026-09-24.
- Klick på telefon och skickat formulär mäts som händelser efter samtycke.
- Search Console via DNS, Bing Webmaster Tools importerat.

## Fas 7 QA-grind (utdrag)

| ID | Resultat | Belägg |
|----|----------|--------|
| Q7 | pass | inga `block` |
| Q8 | fail | exempeldomän och exempelgata (i detta påhittade exempel) |
| Q11 | fail | telefon saknas |
| Q12 | pass | testförfrågan mottagen |

Beslut: lansera inte. Blockerande: Q8, Q11.

## Fas 8 Lansering och uppföljning

Efter rättning: deploy av tagg `v1.0.0`, sitemap inskickad till Google och Bing,
indexering begärd för fem sidor, baslinjeexport av rapporten för generativ AI (tom första
veckan, väntat). Ny granskning planerad tre månader efter lansering.

## Vanliga misstag vid bygge: fel mot rätt

| Situation | Fel | Rätt |
|-----------|-----|------|
| Telefon saknas | Fyll i `555-0100` eller `[Phone]` så att schemat blir komplett | Utelämna `telephone` tills numret finns, eller markera `REPLACE_ME` i utkast; validatorn stoppar båda platshållarna |
| Inga omdömen | Skriv tre exempelomdömen "tills riktiga kommer" | Inga omdömen på sidan; be kunderna efter jobb |
| Betyg | `aggregateRating` 4,9 på egen LocalBusiness | Inga egna stjärnor i markup; Google visar dem inte [V] |
| Kontaktformulär | `<form action="#">` från en mall | Verklig mottagare, testad hela vägen |
| Hålla sajten borta från AI | `User-agent: Googlebot` `Disallow: /` | Tillåt Googlebot; `nosnippet` eller `max-snippet` [V] |
| Testmiljö | `noindex` som följer med vid lansering | Lösenord på testmiljön; Q3 i QA-grinden |
| Deploy | Deploya repot utan att titta på live | Jämför repo mot live, deploya fastlåst tagg |
| Orter | Tolv ortsidor med bytt ortnamn | Bara orter med verkliga uppdrag och eget innehåll [H] |
| Bilder | AI-genererat "team" på om oss-sidan | Egna foton, eller ingen bild |
| AI-sök | Lägg till `llms.txt` och FAQPage "för AI" | Inget av dem hjälper i Google Sök [V]; lägg tiden på fallstudien |
| Behörighet | Nämn certifiering ägaren "tror" att hen har | Publicera först när intyget är sett |
| Brådska | "Bara två tider kvar denna vecka!" som fast text | Bara om det stämmer just då |
