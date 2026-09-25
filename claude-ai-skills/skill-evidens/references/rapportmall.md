# Rapportmall: evidensgranskning

Steg 8 i SKILL.md. Rapporten går till användaren som svar i chatten, eller som fil om
användaren vill det. Skriv på svenska om inte användaren skriver på annat språk. Håll den
kort: siffror och listor, inga utfyllnadsstycken. Tomma avsnitt skrivs ut med "Inga." så att
det syns att de kontrollerats.

```markdown
# Evidensgranskning: <skillens namn> (ÅÅÅÅ-MM-DD)

## Sammanfattning
- Granskat: <filer och kataloger>, <antal> påståenden inventerade.
- Bekräftade: <n>. Delvis, omskrivna: <n>. Motsagda: <n>. Föråldrade: <n>. Overifierade: <n>.
- Strukna: <n>, alla förda till "Borttagna påståenden" i `<registerfil>`.
- Utlösande källa: <titel>, <URL>, <datum>. (Eller: ingen, rutingranskning.)
- Tester: <n> tester, <n> gröna, <n> röda. (Eller: skillen har inga skript.)
- Leverans: version <gammal> till <ny>, changelog uppdaterad, paket ombyggt: ja/nej/ej tillämpligt,
  CI: grön/röd/ej körd.

## Viktigaste ändringarna
1. <Det som ändrar skillens beteende mest, med källa.>
2. ...
3. ...

## Strukna påståenden
| Påstående (ordagrant) | Var | Skäl |
|-----------------------|-----|------|
| "..." | fil:rad | Motsagd av <källa, datum> / ingen primärkälla |

## Omskrivna påståenden
| Före | Efter | Nivå | Källa |
|------|-------|------|-------|
| "..." | "..." | [V] | <URL, datum> |

## Overifierat som ligger kvar
Påståenden som inte kunde kontrolleras men behölls som tumregel [H], med skäl.
Sidor som inte gick att nå (403, inloggning, borta) och vad som hänger på dem.

## Allvarlighetsregeln
- [V]-påståenden som får driva Critical/High: <n>.
- [R]/[H] som tidigare drev Critical/High och sänktes: <lista>.

## Nya filer
- `<registerfil>`: evidensregister med <n> källor och <n> borttagna påståenden.
- `<exempelfil>`: fel mot rätt, utdataexempel, <övrigt>.
- `tests/...`: <n> tester, fixtures i `<mapp>` (syntetiska, märkta).

## Adversariell granskning
| Lins | Fynd | Bedömning | Åtgärd |
|------|------|-----------|--------|
| Fakta | "..." | Bekräftat / Avvisat: <skäl> | Rättat i <fil> / ingen |
| Kod och konventioner | "..." | ... | ... |

## Kvar att göra
- <Det som inte gjordes, och varför. Till exempel: källa bakom inloggning, beslut som kräver
  användaren, skript utan testbar yta.>
- Ladda upp `<paket>.skill` i claude.ai (Inställningar, Skills) om skillen är en claude.ai-skill.
```

## Skrivregler för rapporten

- Varje siffra i rapporten ska gå att hitta i inventeringen eller i testutfallet.
- Citera källan ordagrant när ordalydelsen avgör; parafrasera annars kort.
- "Overifierad" betyder att ingen primärkälla hittades. Skriv inte "falsk" om det inte finns
  en källa som säger emot.
- Inga tankstreck som skiljetecken och inga "inte X utan Y"-konstruktioner.
- Fanns inget att rätta: skriv det i sammanfattningen och lämna resten kort.
