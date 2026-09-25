# Renoveringsläget

För en sajt som redan finns och ska byggas om, flyttas eller ändras. Lärdomen från ett
verkligt fall: git-repot och livesajten kan skilja sig åt. Någon hade ändrat live utanför
repot, och en deploy av repot hade skrivit över de nyare ändringarna. Jämför därför alltid
innan något ändras eller deployas.

## Steg 1: inventera repo och live

1. **Var ligger sanningen?** Fråga ägaren: CMS, värdens gränssnitt, FTP, byggtjänst,
   flera personer? Vem deployade senast och hur?
2. **Hämta livesajten**: startsida, alla URL:er i sitemap.xml, robots.txt. Spara som
   ögonblicksbild med datum.
3. **Bygg repot lokalt** och jämför sida för sida mot live:
   ```
   curl -s https://www.example.se/ > live/index.html
   diff <(sed 's/[[:space:]]\+/ /g' live/index.html) <(sed 's/[[:space:]]\+/ /g' dist/index.html)
   ```
   Jämför också listan över URL:er: finns sidor live som saknas i repot, eller tvärtom?
4. **Senaste ändring**: `git log -1 --format='%H %ci'` mot värdens senaste deploy och mot
   `Last-Modified` eller synliga datum live.
5. **Är live nyare**: för in ändringarna i repot och committa dem innan något annat görs.
   Säg till ägaren vad som skilde.

Leverans: tabell över skillnader (sida, live, repo, åtgärd).

## Steg 2: leta efter läckta hemligheter

I repot och historiken:
```
git ls-files | grep -i -E '\.env|secret|credential|\.pem$|\.key$|token'
git log --all --oneline -- '*.env' '*secret*' '*.pem' '*credential*'
git grep -n -I -E '(api[_-]?key|secret|passw(or)?d|token)["'\'' ]*[:=]' $(git rev-list --all | head -200)
```
Finns `gitleaks` eller `trufflehog`: kör dem också (`gitleaks detect`, `trufflehog git file://.`).

På livesajten:
```
for p in .env .git/HEAD .git/config config.json wp-config.php.bak; do
  printf '%s ' "$p"; curl -s -o /dev/null -w '%{http_code}\n' "https://www.example.se/$p"; done
```
Allt annat än 404 eller 403 undersöks. Läs också byggda JavaScript-filer efter nycklar.
Publika nycklar som är avsedda för webbläsaren (till exempel en kartnyckel begränsad till
domänen) är normala; hemliga nycklar är det inte.

Hittas en hemlighet:
1. **Rotera den först** hos tjänsten. En nyckel som legat i git ska räknas som läckt, även
   om den tas bort.
2. Ta bort den ur koden, lägg filnamnet i `.gitignore`, använd miljövariabler.
3. Städa historiken (till exempel med `git filter-repo`) först efter rotation, och bara
   med ägarens godkännande eftersom det skriver om historiken.

Checka aldrig in `.env`, `client_secret*.json`, tokenfiler eller lösenord.

## Steg 3: baslinje före ändring

- Search Console: exportera resultat (sidor och frågor) för minst tre månader och
  indexeringsrapporten.
- Rapporten för generativ AI och Bing AI Performance: exportera.
- Lista URL:er med trafik, externa länkar (om `/seo backlinks` finns) och bokmärkta sidor.
- Kör granskningsläget på den gamla sajten så att förbättringen går att visa.

## Steg 4: URL-karta och omdirigeringar

| Gammal URL | Ny URL | Typ |
|------------|--------|-----|
| /tjanster.html | /tjanster/ | 301 |
| /gammal-kampanj | /kampanjer/ | 301 |

- Varje gammal URL med trafik eller länkar får en 301 till närmaste motsvarighet [H].
- Inga kedjor; peka direkt på slutmålet [H].
- Sidor som tas bort utan ersättare får 404 eller 410, inte en omdirigering till startsidan.
- Byts domän: använd flyttverktyget (Change of Address) i Search Console [V].

## Steg 5: ändra och deploya säkert

1. Små steg, en commit per ändring med tydligt meddelande.
2. Kör faserna som berörs (oftast 2, 3, 4 och 6) och hela QA-grinden.
3. **Fastlåst deploy**: deploya en bestämd commit eller tagg, aldrig "senaste från
   arbetskatalogen". Förhandsvisa först om värden stöder det.
4. **Spara en kopia av live** omedelbart före deploy, så att det går att återställa.
5. Efter deploy: jämför live mot det du deployade, kör fas 8.

## Fel mot rätt

| Fel | Rätt |
|-----|------|
| Deploya repot direkt för att "det är senaste versionen" | Jämför repo mot live, för in skillnader, deploya en fastlåst commit |
| Radera `.env` ur repot och gå vidare | Rotera nyckeln först, sedan städa |
| Alla gamla URL:er till startsidan | 301 till närmaste motsvarighet, annars 404 eller 410 |
| Ingen export före bytet | Baslinje från Search Console och Bing före första ändringen |
