# Checklista före leverans

Bocka av varje rad. En rad som inte gäller markeras "ej tillämplig" med skäl, den hoppas
inte över i tysthet.

## Inventering
- [ ] Alla filer i skillen är genomsökta: SKILL.md, references/, agenter, skript, README, mallar.
- [ ] Sökmönstren i `inventering.md` är körda, och texten är dessutom läst.
- [ ] Varje påstående har ID, plats, ordagrann lydelse och typ.
- [ ] Ingen rad i inventeringen har tom status.

## Gradering och verifiering
- [ ] Varje påstående har nivå: [V], [R-peer], [R-preprint] eller [H].
- [ ] Varje [V] och [R] har URL, datum och ordagrant citat från en hämtad primärkälla.
- [ ] Bloggar används bara som vägvisare; inget påstående vilar enbart på en blogg.
- [ ] Slutsatser av frånvaro och överförda slutsatser är märkta som slutsatser.
- [ ] Inga siffror, datum eller citat är ifyllda ur minnet.
- [ ] Sidor som inte gick att nå är listade som Overifierade med skäl.

## Rättelse
- [ ] Motsagda och overifierade påståenden är strukna eller omskrivna till [H] utan siffra.
- [ ] Strukna påståenden är sökta i hela repot (speglar, tillägg, docstrings, PDF-källor).
- [ ] Allvarlighetsregeln håller: bara [V] driver Critical eller High; [H] bär "tumregel".
- [ ] Skillens syfte, struktur och röst är kvar.
- [ ] Evidensregistret finns med nivåer, källtabeller, forskning med förbehåll,
      Borttagna påståenden (ordagrant, daterat, med skäl) och kvarvarande tumregler.
- [ ] SKILL.md pekar på registret och kräver en registerrad för nya påståenden.

## Exempel
- [ ] Exempelfil finns i samma leverans som rättelsen.
- [ ] Fel mot rätt-tabell täcker varje borttagen regel som ändrar skillens utdata.
- [ ] Minst ett utdataexempel visar taggar och tumregelsmärkning.
- [ ] Påhittade data är märkta (example.com, uppfunna siffror).

## Tester
- [ ] Varje medföljande skript som rörts har tester, eller "ej tillämplig" med skäl.
- [ ] Fixtures är syntetiska och har en README som säger det.
- [ ] Testerna är körda och utfallet står i rapporten.
- [ ] Fel som testerna hittade är rättade och står under Fixed.
- [ ] CI kör testerna.

## Adversariell granskning
- [ ] Faktalinsen är körd: citat stämmer, borttagna påståenden finns inte kvar, inga nya
      okällbelagda påståenden.
- [ ] Kod- och konventionslinsen är körd: tester, frontmatter, radgränser, länkar,
      changelog mot diff.
- [ ] Bekräftade fynd är rättade; avvisade fynd har skäl i rapporten.

## Leverans
- [ ] Changelog-post med datum och URL för varje ny faktauppgift.
- [ ] Version höjd på alla ställen enligt skillens konvention (eller Unreleased, med skäl).
- [ ] Frontmatter validerad (`quick_validate.py` eller motsvarande).
- [ ] claude.ai-skill: paketet ombyggt, användaren påmind om uppladdning.
- [ ] Allt pushat före PR; ingen push under pågående merge.
- [ ] CI grön före merge; efter merge finns varje commit på huvudgrenen.
- [ ] Rapporten följer `rapportmall.md`.
- [ ] Svensk text: inga tankstreck som skiljetecken, inga "inte X utan Y".
