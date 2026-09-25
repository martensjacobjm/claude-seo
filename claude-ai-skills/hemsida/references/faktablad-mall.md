# Faktablad och brief (fas 0)

Faktabladet är den enda källan till uppgifter om företaget. Allt som hamnar på sajten, i
JSON-LD och i företagsprofilerna ska gå att spåra hit. Fyll i det tillsammans med ägaren,
en gång och samlat. Kolumnen Källa säger vem som lämnade uppgiften och när.

## Får aldrig hittas på

- Namn, adress, telefon, e-post, organisationsnummer, öppettider
- Priser, rabatter, garantier, leveranstider
- Recensioner, betyg, antal kunder, kundcitat, kundlogotyper
- Certifieringar, behörigheter, medlemskap, försäkringar, utmärkelser
- Personalens namn, foton, erfarenhet i år
- Orter och områden där företaget faktiskt arbetar
- Siffror i text ("200 nöjda kunder", "sedan 1998") och resultat i fallstudier

Saknas en uppgift: skriv "saknas" och fråga. I kod blir den `REPLACE_ME` eller utelämnas.
Uppgifter som ägaren anger men inte kan styrka (till exempel en certifiering utan intyg)
markeras "ej styrkt" och publiceras inte förrän underlaget finns.

## Mall

```markdown
# Faktablad: <företag> (ÅÅÅÅ-MM-DD)

## Företaget
| Uppgift | Värde | Källa |
|---------|-------|-------|
| Juridiskt namn | | ägaren, datum |
| Namn utåt (samma överallt) | | |
| Organisationsnummer | | |
| Gatuadress, postnummer, ort | | |
| Tar emot kunder på adressen? (ja/nej) | | |
| Telefon (ett nummer för sajt och profiler) | | |
| E-post för förfrågningar | | |
| Öppettider per veckodag | | |
| Avvikande öppettider (helger) | | |
| Webbadress (https, med eller utan www) | | |
| Sociala profiler och kataloger (URL) | | |

## Erbjudandet
| Tjänst eller produkt | Kort beskrivning | Pris eller "offert" | Källa |
|----------------------|------------------|---------------------|-------|

## Område
| Ort eller område | Verkliga uppdrag där (ja/nej, exempel) | Källa |
|------------------|----------------------------------------|-------|

## Förtroende
| Uppgift | Värde | Underlag sett (ja/nej) |
|---------|-------|------------------------|
| Certifieringar, behörigheter | | |
| Försäkring | | |
| Medlemskap i branschorganisation | | |
| Omdömen som får citeras (namn, datum, samtycke) | | |
| Egna foton (antal, vem äger rättigheterna) | | |

## Beslut
| Fråga | Svar |
|-------|------|
| Tillåta AI-träning (GPTBot, ClaudeBot, Google-Extended med flera)? | |
| Vem skriver och godkänner texter? | |
| Vem äger domänen, DNS och värdkontot? | |
| Befintlig sajt att ersätta? (ja: renoveringsläget) | |
| Språk och länder | |
| Analysverktyg och samtyckeslösning | |
| Vart ska formulären skickas? | |

## Saknas
- Lista allt som är tomt ovan, med vem som ska ta fram det.
```

## Brief: frågor att ställa

Ställ bara de frågor som inte redan är besvarade.

1. **Mål**: vad ska en besökare göra? Ringa, boka, skicka förfrågan, köpa, läsa.
2. **Målgrupp**: vem är kunden, vilket problem har hen, vad söker hen efter?
3. **Konkurrenter**: två till fem som ägaren själv ser som konkurrenter.
4. **Det unika**: vad kan företaget visa som ingen annan kan? Egna uppdrag, egna foton,
   egna mätningar, en process, en garanti. Det blir kärnan i innehållet.
5. **Omfång och tid**: antal sidor, lansering, budget, vem som underhåller sajten.
6. **Teknik**: finns ett CMS, en värd eller ett repo sedan tidigare?

Leverans: faktabladet ifyllt så långt det går och listan Saknas. Gå vidare till fas 1 med
luckorna öppet redovisade, inte ifyllda med gissningar.
