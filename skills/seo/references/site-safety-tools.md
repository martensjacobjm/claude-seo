# Site Safety Tools (pre-deploy checks)

Three offline-friendly scripts that catch the two ways a small-business site
repo hurts its owner, plus one international-SEO validator:

| Script | Catches | Network |
|--------|---------|---------|
| `scripts/secret_scan.py` | Passwords, tokens and keys committed to the repo (incl. deleted ones in git history) | none |
| `scripts/repo_live_diff.py` | A repo that is older than (or diverged from) the live site, so an upload would overwrite newer content | read-only GETs to the site |
| `scripts/hreflang_check.py` | Broken hreflang: bad codes, missing self/return links, canonical conflicts, relative URLs, dead targets | read-only GETs |

Origin: a real case (Sep 2026). A static site deployed by SFTP had its repo
10 months behind the live site, and the SFTP password sat in plaintext in 7
tracked files of a public GitHub repo. Running the repo's upload script would
have replaced the newer live site with the old one.

## When to run

- **Before any deploy, upload script or renovation** of a site whose repo you
  did not maintain yourself: run `secret_scan.py --git-history` and
  `repo_live_diff.py`. Stop if either exits 1.
- **When taking over a client site** or starting `/seo audit` on a site whose
  repo is available locally.
- **After an international launch or URL migration**: `hreflang_check.py`.
- In CI or a deploy script as a gate (exit codes below).

## 1. `secret_scan.py <path>`

```bash
python scripts/secret_scan.py ./site                       # working tree
python scripts/secret_scan.py ./site --git-history         # + every commit (git log -p --all)
python scripts/secret_scan.py ./site --git-history --max-commits 2000 --text
```

Rules: GitHub tokens (`ghp_`, `github_pat_`), Google API keys (`AIza...`),
AWS key IDs/secret keys, Slack tokens/webhooks, Stripe keys, private key
blocks, JWTs; generic `password/passwd/pwd/pass/secret/api_key/token = ...`
assignments (also Swedish/Norwegian/German words such as `Lösenord`,
`passord`, `Passwort`) in sh, bat, ps1, py, js, json, yaml, .env, ini and
Markdown; `scheme://user:pass@host` connection strings; `curl -u user:pass`,
`sshpass -p`, `lftp -u user,pass`, `pscp/plink -pw`, WinSCP `/password=`;
`curl --insecure`/`-k` as a warning. Generic values are graded with Shannon
entropy; placeholders (`your_password`, `${VAR}`, `%PASS%`, `xxx`, `...`) and
code (`password = get_password()`) are skipped.

Output: file, line, commit + date (history), rule, severity, masked value
(first 2 + last 2 characters; values under 8 characters fully masked) and a
per-run `secret_id` so the same value in several files is visible without
printing it. `secrets_only_in_history` lists values that were deleted from
files but remain in commits. The git remote is inspected: a GitHub remote
triggers advice to check repository visibility (no API call is made);
credentials embedded in a remote URL are reported, never printed.

Ignore: `.secretscanignore` (glob per line, `dir/` for directories) in the
scanned directory; a line containing `secretscan:allow` is skipped. `.git`,
`node_modules`, virtualenvs, binary files and files > 1 MB are skipped.

If it finds a live credential: **rotate it first** (a public repo means it is
already compromised), then remove it from files and history
(`git filter-repo` / BFG) and force-push.

## 2. `repo_live_diff.py <local_dir> <base_url>`

```bash
python scripts/repo_live_diff.py ./site https://example.com --text
python scripts/repo_live_diff.py ./site https://example.com --clean-urls --delay 2
```

- Maps `index.html` -> `/`, `dir/index.html` -> `/dir/`, `foo.html` ->
  `/foo.html` (`--clean-urls`: `/foo` first, then `/foo.html`).
- Per page: live status, title, meta description, canonical, H1, JSON-LD
  types, visible-text hash, difflib similarity, Last-Modified, ETag.
- Reads robots.txt `Sitemap:` lines and `/sitemap.xml` (indexes followed) and
  lists live URLs with no local file (`only_live`).
- Date evidence: live Last-Modified (or sitemap `<lastmod>`) vs
  `git log -1 --format=%cI -- file` (or mtime), plus the latest year mentioned
  in the visible text on each side. Commit dates show when a file was
  committed, not when its content was written; read them as evidence only.
- Verdict: `in sync`, `repo appears older`, `repo appears newer`,
  `diverged`. `signals` counts live-newer vs repo-newer evidence, so a
  diverged result still shows which side is mostly ahead.
- Polite: 1 s between requests by default (`--delay`), 5 MB body cap.

## 3. `hreflang_check.py <url> [--crawl-sitemap]`

```bash
python scripts/hreflang_check.py https://example.com/en/
python scripts/hreflang_check.py https://example.com/ --crawl-sitemap --max-pages 100
```

Collects hreflang from HTML `<link>`, HTTP `Link:` headers and sitemap
`xhtml:link`, then follows the alternates (bounded) and checks: ISO 639-1
language, optional ISO 15924 script, ISO 3166-1 alpha-2 region (tables in the
script; `es-419`, region-only, `UK`/`EU`/`UN` flagged), `x-default` (info:
recommended, not required), self-reference, return links, duplicate codes,
relative URLs, hreflang on non-canonical pages, alternates that redirect,
404 or canonicalise elsewhere, links after `<body>`, `media` combined with
hreflang, mixed protocols and inconsistent sets. Rules follow Google's
[localized versions](https://developers.google.com/search/docs/specialty/international/localized-versions)
page (verified 2026-09-28); canonical/redirect checks are heuristics.

## Exit codes

| Script | 0 | 1 | 2 |
|--------|---|---|---|
| `secret_scan.py` | no high findings | at least one high finding | bad path / not a git repo with `--git-history` |
| `repo_live_diff.py` | in sync (or newer with `--allow-newer`) | older, newer or diverged | base URL blocked/unreachable |
| `hreflang_check.py` | no error-level issues | at least one error | start URL blocked/unreachable |

Deploy gate example:

```bash
python scripts/secret_scan.py . --git-history --min-severity high >/dev/null &&
python scripts/repo_live_diff.py . https://example.com --allow-newer >/dev/null &&
./upload-to-server.sh
```

## Safety

- All user URLs and every redirect hop pass `validate_url()` from
  `google_auth.py` plus a resolved-IP check (private, loopback, link-local,
  metadata addresses such as `169.254.169.254` are refused).
- Shared implementation: `scripts/safe_fetch.py` (`validate_public_url()`,
  `SafeFetcher`), also used by `fetch_page.py`, `verify_backlinks.py`,
  `nlp_analyze.py` and `site_crawl.py`. Any resolved address that is private,
  loopback, link-local, reserved, multicast or an IPv4-mapped/6to4/NAT64 form
  of one blocks the URL. `python scripts/safe_fetch.py check <url>` explains
  a refusal.
- DNS rebinding: direct connections are pinned to the IP that passed the
  check (SNI, certificate and Host header keep the hostname). Behind an
  HTTP(S) proxy the proxy resolves the target, so only the pre-request check
  applies; the Playwright scripts filter browser requests by URL only.
- Output is JSON by default (`--text` for a readable summary on the first two).
- Secrets are never printed unmasked, including in `--text` mode.
- Only scan sites and repos you own or have permission to check.
