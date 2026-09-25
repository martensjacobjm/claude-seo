# Evidensnivåer, allvarlighetsregel och registermall

Steg 2 till 4 i SKILL.md.

## 1. Nivåerna

| Tagg | Nivå | Räknas hit | Räknas inte hit |
|------|------|------------|-----------------|
| [V] | Leverantör eller officiell dokumentation | Systemägarens docs, hjälpsidor, officiell blogg och changelog, API-referens, ratificerad standard, domstolshandling om systemet | En byrås blogg om systemet, en konferenspresentation av en utomstående |
| [R-peer] | Referentgranskad forskning | Tidskrift, konferensbidrag med granskning (KDD, ACL, SIGIR) | Workshopabstrakt utan granskning |
| [R-preprint] | Förtryck | arXiv, SSRN, en forskargrupps rapport utan granskning | Leverantörens whitepaper (det är [V] om egen produkt, annars [H]) |
| [H] | Praktikers tumregel | Viktningar, erfarenhetsråd, branschstudier med okänd metod, korrelationsstudier från verktygsleverantörer | |

Leverantörssuffix som [V Google] eller [V Bing] namnger bara källan och räknas som [V].
I löptext räcker [R] som paraply; registret skriver alltid ut peer eller preprint.

### Gränsfall

- **Leverantör om egen produkt** är [V]. Leverantör om **konkurrentens** produkt är [H].
- **Förslag till standard** (llmstxt.org) är ett förslag, inte en standard. Skriv "förslag"
  och vem som står bakom. Att förslaget finns är [V]; att någon använder det kräver egen källa.
- **Läckta dokument** (t.ex. Content Warehouse-läckan 2024) visar att ett attribut finns,
  inte hur det viktas. Gradera existensen, aldrig vikten.
- **Domstolshandlingar** är [V] för det de faktiskt säger, med dokumentnummer.
- **Mätdata från tredje part** (HTTP Archive Web Almanac) är [V] för vad som mättes, med
  mätdatum. De säger inget om effekt.
- **Slutsats av frånvaro** (ett enum-värde saknas, en sida nämner inte X) märks "slutsats" i
  registret och får aldrig ensam driva Critical eller High.

## 2. Allvarlighetsregeln

- Bara [V] får driva Critical eller High (eller skillens två högsta nivåer).
- [R] får vara högst Medium, och forskarnas egna förbehåll följer med.
- [H] får vara högst Medium och ska bära ordet "tumregel" eller "heuristic" i utdata.
- Informativa kontroller (finns filen, vilket värde har fältet) får vara Info oavsett nivå.

Skälet: allvarlighetsgraden är det användaren agerar på. En hög grad ska betyda att den som
äger systemet har sagt det, inte att någon har gissat det.

## 3. Källhierarki vid verifiering

1. Systemägarens aktuella dokumentation (kolla "senast uppdaterad").
2. Systemägarens changelog och officiella blogg.
3. Standard eller specifikation.
4. Referentgranskad forskning.
5. Förtryck.
6. Tredjepartsmätning med redovisad metod.
7. Bloggar, nyhetsartiklar, sociala medier: **bara som vägvisare** till 1 till 6.

Säger två [V]-källor emot varandra (t.ex. changelog mot aktuell doc): återge båda med datum
och följ den nyaste, och skriv det i registret.

## 4. Mall för evidensregistret

Filen läggs i målskillens `references/`. Skriv den på målskillens språk. Uppdatera
datumraden varje gång.

```markdown
<!-- Updated: ÅÅÅÅ-MM-DD -->
# Evidensregister: <ämne>

Varje faktapåstående i `SKILL.md` (och agenter, skript) ska kunna spåras till en rad här.
Lägg till en källa först när primärdokumentet är hämtat och läst.

## 1. Evidensnivåer
<tabellen från avsnitt 1 i kortform>
Bara [V] får driva Critical eller High. [R] och [H] märks i utdata.
Bloggar används bara för att hitta primärkällor.

## 2. Leverantörskällor [V]
### <Leverantör>
| Källa | Datum | Påstående som används |
|-------|-------|-----------------------|
| [Titel](URL) | Senast uppdaterad ÅÅÅÅ-MM-DD | Kort, med citat där ordalydelsen bär |

## 3. Forskning [R]
- **Författare, "Titel"**, publiceringsställe år, [arXiv-id](URL) [R-peer / R-preprint].
  Vad som mättes, huvudresultat, författarnas förbehåll.

## 4. Mätdata
- Källa, mätdatum, siffra, vad den inte säger.

## 5. Borttagna påståenden (ÅÅÅÅ-MM-DD)
Återinför inte utan hämtad primärkälla:
- "<ordagrant påstående>" (skäl: motsagd av X ÅÅÅÅ-MM-DD / ingen primärkälla / föråldrad)

## 6. Tumregler som finns kvar [H]
| Tumregel | Motivering |
|----------|------------|
```

## 5. Hur en registerrad ser ut när den är bra

Bra: `[Guide to Optimizing for Generative AI Features](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide) | Last updated 2026-07-10 | no chunking requirement, "no ideal page length"; llms.txt not used by Google Search`

Dåligt: `Google guide | 2026 | Google says content length doesn't matter` (ingen URL, inget
exakt datum, parafras som säger mer än källan).

## 6. Hämtningslogg (valfri men nyttig)

Vid större granskningar: för en logg med URL, hämtdatum, HTTP-status och om sidan krävde
inloggning. Den gör faktalinsen i steg 7 snabb, och den visar vad som var overifierbart och
varför.
