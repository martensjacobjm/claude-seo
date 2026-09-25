---
name: skill-evidens
description: Evidensgranskning av en Claude-skill. Inventerar varje faktapåstående, siffra, datum, API- och verktygsnamn och rekommendation, graderar dem med evidensnivåer ([V] leverantör, [R] forskning, [H] tumregel), verifierar mot primärkällor, rättar eller stryker det som inte håller, bygger ett evidensregister med listan Borttagna påståenden, levererar exempel och tester, kör adversariell granskning och avslutar med changelog, versionshöjning, paketering och grön CI. Använd ALLTID när någon vill evidensgranska, faktagranska en skill, källgranska, verifiera påståenden, uppdatera en skill med ny data eller nya källor, eller städa bort okällbelagd statistik. Trigga även på engelska, till exempel skill audit, fact-check a skill, evidence review, verify claims in a skill, update a skill with new data, source check.
---

# Evidensgranskning av skills

Processen för att gå igenom en skill påstående för påstående och se till att allt den
säger går att spåra till en källa som faktiskt säger det. Arbetsflödet är generaliserat
från evidensgranskningen av claude-seo (2026-09-24 och 2026-09-25), där seo-geo byggdes
om på Googles AI-optimeringsguide och ett tjugotal okällbelagda siffror ströks.

Grundregeln: **en skill får inte påstå mer än källorna säger.** Hellre en kortare skill
med tre belagda råd än en lång med tjugo rykten. Hittar du ingen källa: säg det rakt ut,
stryk eller märk påståendet, och hitta aldrig på en siffra, ett datum eller ett citat.

## Referenser: läs när momentet kommer

| Fil | Läs när |
|-----|---------|
| `references/inventering.md` | Steg 1. Sökmönster och inventeringstabell |
| `references/evidensnivaer.md` | Steg 2 till 4. Nivåer, allvarlighetsregel, källhierarki, registermall |
| `references/exempel-claude-seo.md` | Före steg 4 och 5. Det verkliga fallet, fel mot rätt formulering |
| `references/rapportmall.md` | Steg 8. Rapporten till användaren |
| `references/checklista.md` | Före leverans. Bocka av varje rad |

## Intake: avgör omfånget först

Fråga bara det som är obesvarat:

1. **Vilken skill?** Sökväg till källmappen (inte ett installerat paket; en session kan inte
   ändra en installerad skill, bara källan).
2. **Hela skillen eller en del?** En sub-skill, en referensfil, eller allt inklusive agenter,
   skript och README.
3. **Finns en utlösande källa?** En ny guide, ett changelog-inlägg, en studie. Den läses först,
   den styr ofta vad som måste rivas.
4. **Vilken konvention gäller för version och changelog?** Leta själv i repot först
   (`CHANGELOG.md`, `plugin.json`, `metadata.version` i SKILL.md). Fråga bara om det saknas.

Är uppdraget oklart: fråga. "Kolla skillen" kan betyda en snabb titt eller en full granskning.

## Steg 1: inventera

Lista **varje** kontrollerbart påstående i målskillen innan något rättas. Rättar du medan
du läser missar du hälften, och du kan inte visa vad som granskades.

- Kör sökmönstren i `references/inventering.md` över alla filer i skillen: SKILL.md,
  references/, agenter, skript (docstrings och kommentarer), README, mallar och exempel.
- Fånga: procent och andelar, multiplar ("3x"), korrelationer, intervall ("134-167 ord"),
  årtal och datum, versionsnummer, API-, endpoint-, fält- och botnamn, citerade aktörer
  ("enligt Ahrefs"), "studier visar", superlativ och absoluta ord (alltid, aldrig, enda,
  optimal, bäst), och varje rekommendation som styr ett betyg eller en allvarlighetsgrad.
- Läs dessutom texten. Mönster hittar siffror, men ett påstående som "AI-crawlers kör inte
  JavaScript" har ingen siffra.
- Skriv in allt i inventeringstabellen (mall i `references/inventering.md`) med ID, fil:rad,
  påståendet ordagrant, typ och eventuell angiven källa.

Är skillen stor: dela inventeringen på subagenter per fil eller katalog, och slå ihop
tabellerna. Dubbletter av samma påstående i flera filer får samma ID; de ska rättas överallt.

## Steg 2: gradera med evidensnivåer

Varje påstående får en nivå. Full definition och gränsfall i `references/evidensnivaer.md`.

| Tagg | Nivå | Exempel |
|------|------|---------|
| [V] | Leverantör eller officiell dokumentation | Google Search Central, Bing Webmaster-bloggen, OpenAI:s botsida, en API-referens, en standard |
| [R-peer] | Referentgranskad forskning | Konferens- eller tidskriftsartikel |
| [R-preprint] | Förtryck, inte granskat | arXiv utan publicering |
| [H] | Praktikers tumregel | Viktningar, redaktionella prioriteringar, erfarenhetsråd |

I löptext räcker [R] som paraply, men registret skiljer alltid peer från preprint.

**Allvarlighetsregeln:** bara [V] får driva Critical eller High (eller motsvarande
högsta nivåer i skillens egen skala). [R] och [H] får vara Medium eller lägre, och [H]
ska bära ordet "tumregel" (eller "heuristic") i skillens utdata. Skälet: en användare som
får "Critical" agerar direkt, och det ska bara hända när den som äger systemet har sagt det.

Leverantörsuttalande om **någon annans** system är inte [V]. En SEO-byrås studie om Google
är [H] eller [R], aldrig [V].

## Steg 3: verifiera mot primärkällan

För varje påstående i tabellen:

1. **Hämta källan.** Använd webbhämtning (WebFetch, web_fetch, Firecrawl eller vad miljön har).
   Läs den faktiska sidan, inte sökresultatets sammanfattning.
2. **Bloggar och nyhetsartiklar är bara vägvisare.** Följ länken till primärkällan
   (dokumentationen, studien, domstolshandlingen, changeloggen) och citera den. Finns ingen
   primärkälla bakom bloggen: påståendet är overifierat.
3. **Anteckna** URL, sidans datum ("senast uppdaterad" eller publiceringsdatum), hämtdatum
   och ett ordagrant citat som bär påståendet. Citatet ska kunna hittas med Ctrl+F på sidan.
4. **Sätt status:** Bekräftad, Delvis (källan säger mindre eller annat), Motsagd (källan
   säger emot), Föråldrad (stämde en gång), Overifierad (ingen primärkälla hittad eller
   sidan gick inte att nå).
5. **Märk slutsatser som slutsatser.** "API:t har inget värde för X" är ofta en slutsats av
   att värdet saknas i en enum. Skriv "slutsats av frånvaro" i registret. Gäller en källa
   bara produkt A och skillen påstår det om produkt B: skriv "slutsats" och varför.

Aldrig:

- fylla i en siffra, ett datum eller ett citat ur minnet när hämtningen misslyckas;
- runda av, "uppdatera" eller extrapolera en siffra som källan inte anger;
- behålla ett påstående för att det "låter rimligt" eller för att det står i många bloggar.

Går sidan inte att nå (blockerad, 403, inloggning): status Overifierad, notera varför, och
säg det i rapporten. Saknar miljön helt webbåtkomst: säg det rakt ut innan du börjar, och
leverera då bara inventering och gradering, inga rättelser byggda på minnet.

Många påståenden: dela verifieringen på parallella subagenter, en per källdomän eller
per fil. Varje subagent lämnar rader till registret med URL, datum, citat och status.

## Steg 4: rätta

Rätta skillen utifrån statusen. Behåll skillens syfte, struktur och röst: granskningen ska
göra skillen sannare, den ska inte skriva om den till en annan skill.

| Status | Åtgärd |
|--------|--------|
| Bekräftad | Behåll. Lägg till nivåtagg och källa (i texten eller i registret) |
| Delvis | Skriv om till exakt det källan säger. Citera hellre än parafrasera |
| Motsagd | Stryk eller vänd, och skriv vad källan säger i stället |
| Föråldrad | Ersätt med aktuell uppgift och datum, eller stryk |
| Overifierad | Stryk. Är rådet ändå värdefullt: behåll som [H] utan siffra, med ordet tumregel |

Bygg sedan **evidensregistret**, en referensfil i målskillen (t.ex.
`references/<ämne>-evidence.md` eller `references/evidensregister.md`, följ skillens
språk och namngivning). Mall i `references/evidensnivaer.md`. Registret innehåller:

- nivådefinitionerna och allvarlighetsregeln;
- en källtabell per leverantör eller område: källa med URL, datum, vilket påstående den bär;
- forskning med peer eller preprint utskrivet och författarnas egna förbehåll;
- **Borttagna påståenden**: varje struken siffra och regel, ordagrant, med datum och kort
  skäl ("motsagd av Google 2026-07-10", "ingen primärkälla"). Listan finns för att en
  framtida uppdatering, människa eller modell, inte ska lägga tillbaka samma rykte. Rubriken
  börjar med "Återinför inte utan hämtad primärkälla";
- tumreglerna som finns kvar och varför.

Lägg in en rad i målskillens SKILL.md som pekar på registret och säger att varje nytt
faktapåstående måste ha en rad där först.

Sök efter samma påstående i **hela** repot, inte bara i målskillen. I claude-seo låg
"0.737"-korrelationen kvar i en annan skill, ett tilläggs-spegelexemplar och en docstring
efter första rundan.

## Steg 5: skriv exempel, alltid

Leverera exempel **i samma leverans** som rättelsen. I claude-seo fick användaren be om
exemplen efteråt; det ska inte behövas. En regel utan exempel tolkas fel av nästa modell.

Skapa eller uppdatera en exempelfil i målskillen (t.ex. `references/<ämne>-examples.md`) med:

1. **Fel mot rätt**: en tabell där varje borttagen regel står bredvid den formulering
   skillen ska använda nu, med nivåtagg och allvarlighetsgrad. Exempel i
   `references/exempel-claude-seo.md`.
2. **Ett utdraget utdata-exempel**: hur skillens rapport eller svar ser ut efter rättelsen,
   med taggar och tumregelsmärkning synliga.
3. **Leverantörens eget exempel** när källan har ett (Googles "7 Tips for First-Time
   Homebuyers" mot "Why We Waived the Inspection..."). Det är det starkaste beviset.
4. **Påhittade data märkta som påhittade**: `example.com`, uppfunna siffror, och en rad som
   säger det rakt ut.

## Steg 6: tester för varje medföljande skript

Har skillen skript (Python, shell, hooks) som granskningen rört eller som bär påståenden:

- Skriv tester (pytest, bara standardbiblioteket om möjligt) mot **syntetiska fixtures**.
- Märk fixtures tydligt: en README i fixture-mappen som säger att filerna är syntetiska,
  att siffrorna är uppfunna och vilket format de efterliknar. Aldrig riktiga kunddata.
- Testa både lyckad väg och kantfall: tom fil, saknad fil, oväntade kolumnnamn, fel typ.
- **Kör testerna** och visa utfallet. Ett test som inte körts är inte ett test.
- Hittar testerna ett fel i skriptet: rätta skriptet och notera det under Fixed i
  changeloggen. I claude-seo hittade första testkörningen att parsern kastade
  `FileNotFoundError` i stället för att returnera en varning.
- Finns CI: se till att testerna körs där (ett steg `python -m pytest tests -q`).

Har skillen inga skript: skriv det i rapporten och hoppa över steget.

## Steg 7: adversariell granskning

Granska ditt eget arbete med två linser innan leverans. Har miljön subagenter: kör dem
parallellt med färsk kontext, så att de inte ärver dina antaganden. Saknas subagenter:
gör två separata genomläsningar och skriv ner fynden per lins.

**Faktalinsen.** Uppdrag till granskaren:
- Välj varje [V]-påstående, hämta källan igen och kontrollera att citatet finns ordagrant,
  att datumet stämmer och att påståendet inte säger mer än citatet.
- Kontrollera att inget påstående på listan Borttagna påståenden finns kvar någonstans i
  repot (grep på nyckelsiffror och nyckelord).
- Kontrollera allvarlighetsregeln: ingen [R] eller [H] är Critical eller High.
- Leta efter nya okällbelagda påståenden som rättelsen själv har fört in.

**Kod- och konventionslinsen.** Uppdrag till granskaren:
- Testerna går gröna, skripten kompilerar, CI-konfigurationen kör testerna.
- Frontmatter validerar; SKILL.md under 500 rader, referensfiler under repots gräns.
- Alla filvägar och länkar i skillen pekar på filer som finns.
- Changeloggen stämmer mot diffen: varje påstående i changeloggen om vad som ändrats är sant
  (stryk "borttaget överallt" om det ligger kvar någonstans).
- Repots konventioner följs: namngivning, versionsfält, säkerhetsregler, språk.

Rätta **bekräftade** fynd. Avvisa fynd som inte håller, men skriv ner varför i rapporten.
Ett fynd från granskaren är ett påstående som allt annat: kontrollera det innan du agerar.

## Steg 8: leverera

1. **Changelog.** Ny post under `[Unreleased]` (eller skillens motsvarighet) med datum,
   uppdelad i Added, Changed, Fixed och Removed. Varje ny faktauppgift har sin URL.
   Nämn registret och exempelfilen.
2. **Versionshöjning** enligt skillens konvention. Följ det som finns (semver i
   `plugin.json`, `metadata.version` i SKILL.md, datumversion). Höj alla ställen som bär
   versionen samtidigt; en tre-vägs versionsglidning är ett eget fel. Är konventionen att
   samla i Unreleased till nästa release: följ den och säg det.
3. **Paketera om** om skillen är en claude.ai-skill: bygg `.skill`-paketet på nytt (repots
   byggskript om det finns, annars skill-creators `package_skill.py`), och påminn användaren
   om att ladda upp paketet i claude.ai (Inställningar, Skills). En uppladdad skill uppdateras
   inte av att källan ändras.
4. **Commit och push.** Pusha allt, inklusive exempel, tester och register, innan PR eller
   merge. **Vänta på grön CI** innan merge. Pusha aldrig medan en merge pågår: i claude-seo
   förlorades en commit som pushades under mergen. Efter merge: kontrollera att varje commit
   finns på huvudgrenen (`git log origin/main --oneline`), och öppna en ny PR för det som
   saknas.
5. **Rapport** till användaren enligt `references/rapportmall.md`: vad som granskades, vad
   som bekräftades, rättades och ströks, vad som är overifierat, testutfall, granskningsfynd
   och vad som återstår.
6. **Checklistan** i `references/checklista.md` bockas av före rapporten.

Fanns inget att rätta: säg det rakt ut, leverera inventeringen och registret, och hitta
inte på ändringar för att visa att arbete gjorts.

## Det verkliga fallet i korthet

I claude-seo påstod seo-geo att den optimala passagelängden för AI-citat var "134-167 ord"
och rekommenderade att skapa `llms.txt`. Googles "Guide to Optimizing for Generative AI
Features on Google Search" (senast uppdaterad 2026-07-10,
https://developers.google.com/search/docs/fundamentals/ai-optimization-guide) säger att det
inte finns någon ideal sidlängd, inget krav på chunkning och att llms.txt inte används av
Google Search. Båda reglerna ströks, fördes in under Removed claims i `geo-evidence.md`, och
llms.txt blev en informativ statuskontroll utan poäng. Hela genomgången, med fel mot rätt
formulering och registerutdrag, finns i `references/exempel-claude-seo.md`.

## Skrivregler för svensk text

Gäller skillens egen text, rapporten och svenskspråkiga skills som granskas:

- Inga tankstreck (em dash eller en dash) som skiljetecken. Använd kolon, komma, punkt
  eller parentes. Bindestreck i intervall (134-167) är tillåtet.
- Inga konstruktioner av typen "Det handlar inte om X utan om Y". Säg vad det är.
- Behåll målskillens språk: en engelsk skill rättas på engelska, en svensk på svenska.
