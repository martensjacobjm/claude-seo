# QA-grind före lansering (fas 7)

Varje rad får **pass**, **fail** eller **ej tillämplig**, med belägg: kommandoutdata,
skärmdump eller URL. Kolumnen Blockerar säger om en fail stoppar lanseringen. Kör mot
testmiljön och sedan igen mot produktionsadressen på lanseringsdagen.

## Tabell

| ID | Kontroll | Blockerar | Hur |
|----|----------|-----------|-----|
| Q1 | Alla sidor i sidkartan svarar 200 | ja | curl eller länkkontroll |
| Q2 | Inga trasiga interna länkar | ja | Länkkontroll |
| Q3 | Ingen oavsiktlig `noindex` eller `Disallow: /` | ja | Läs robots.txt och `<meta name="robots">` |
| Q4 | Googlebot, bingbot och valda söktokens tillåtna i robots.txt | ja | Läs robots.txt mot tabellen i SKILL.md |
| Q5 | Canonical finns och pekar rätt på varje sida | ja | Läs HTML |
| Q6 | Titel, metabeskrivning och H1 finns och är unika | ja | Läs HTML |
| Q7 | `validate_schema.py` utan `block` på alla sidor | ja | Kör skriptet |
| Q8 | `validate_schema.py` utan varning om exempeldata (exempeldomän, nollor i telefon, lorem ipsum); en FAQPage-varning betyder att markupen inte ska läggas till i ett nybygge | ja | Kör skriptet |
| Q9 | Inga `REPLACE_ME`, `lorem ipsum` eller platshållare i text eller kod | ja | Sök i byggutdata |
| Q10 | Varje faktapåstående och omdöme finns i faktabladet med källa | ja | Jämför text mot faktabladet |
| Q11 | NAP identiskt i sidfot, kontaktsida och JSON-LD | ja | Jämför |
| Q12 | Formulär skickar och testförfrågan kommer fram | ja | Skicka på riktigt |
| Q13 | Inga inloggningsuppgifter i repo eller på sajten | ja | Se `renovera.md` |
| Q14 | Sitemap giltig, bara 200-URL:er, nämnd i robots.txt | ja | Läs sitemap.xml |
| Q15 | https överallt, en värdversion, övriga 301 | ja | curl -I mot varianterna |
| Q16 | 404-sida svarar 404 | ja | curl mot en påhittad URL |
| Q17 | Viktigt innehåll finns i första HTML-svaret | ja | curl, inte webbläsaren |
| Q18 | Viewport, ingen horisontell scroll i 360 px bredd | ja | Skärmdump i mobilbredd |
| Q19 | Lighthouse Performance, LCP, CLS och TBT (labbproxy för INP) inom budget | nej | Lighthouse eller PageSpeed Insights |
| Q20 | Tillgänglighet: kontrast, fokus, etiketter, alt | nej | Lighthouse Accessibility plus manuell tangentbordstest |
| Q21 | Bilder med alt, width, height, modernt format | nej | Läs HTML |
| Q22 | Inga fel i webbläsarkonsolen | nej | Playwright eller webbläsarens konsol |
| Q23 | Open Graph-taggar och OG-bild | nej | Läs HTML |
| Q24 | hreflang korrekt (bara vid flera språk) | ja | Läs HTML |
| Q25 | Samtycke före analyskakor | ja | Ladda sidan utan att godkänna och se vilka kakor som sätts |
| Q26 | Search Console och Bing Webmaster Tools verifierade | nej | Ägaren bekräftar |

Lighthouse är labbdata och används för att hitta problem [V]. Poängen är ingen
rankningssignal; budgetvärdena är tumregler [H].

## Kommandon

**Status och omdirigeringar**
```
curl -sI https://www.example.se/ | head -1
curl -sI http://example.se/ | grep -i -E '^(HTTP|location)'
curl -s -o /dev/null -w '%{http_code}\n' https://www.example.se/finns-inte-xyz
```

**Initial HTML och meta**
```
curl -s https://www.example.se/tjanst/ | grep -i -E '<title|name="robots"|rel="canonical"|<h1'
```

**Strukturerad data**
```
python3 scripts/validate_schema.py dist/index.html --json
for f in $(find dist -name '*.html'); do python3 scripts/validate_schema.py "$f" --json; done
```
I Claude Code med claude-seo installerat körs samma kontroll som hook vid varje
filändring. Kör ändå hela byggutdata här.

**Platshållare**
```
grep -rn -E 'REPLACE_ME|lorem ipsum|\[(Phone|Address|Business Name)\]' dist/
```

**Länkar** (välj det som finns)
```
lychee --no-progress dist/
npx linkinator https://staging.example.se --recurse
```
Finns inget verktyg: hämta sitemap.xml, begär varje URL med curl och lista allt som inte
svarar 200.

**Lighthouse**
```
npx lighthouse https://staging.example.se/ --only-categories=performance,accessibility,seo,best-practices --form-factor=mobile --output=json --output-path=lh.json
```
Alternativ: PageSpeed Insights i webbläsaren, eller `/seo google pagespeed <url>` i Claude
Code med claude-seo.

**Formulär och konsol** med `webapp-testing` (Playwright) om den finns: fyll i och skicka
formuläret, kontrollera svaret, samla konsolfel, ta skärmdump i 360 px bredd.

## I claude.ai

Utan nätåtkomst går kommandona mot URL:er inte att köra. Gör det som går på filerna
(schemavalidering, platshållare, HTML-läsning) och lämna resten som en checklista till
ägaren med exakt vad som ska kontrolleras. Markera sådana rader "kräver ägaren", aldrig pass.

## Resultat

```markdown
# QA-grind: example.se (ÅÅÅÅ-MM-DD, miljö: test/produktion, commit abc1234)
| ID | Resultat | Belägg |
|----|----------|--------|
| Q1 | pass | 12 av 12 URL:er svarar 200 |
| Q8 | fail | warn: example.se i Organization.url |
...
**Beslut:** lansera / lansera inte. Blockerande fail: Q8.
```
