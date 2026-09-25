<!-- Updated: 2026-09-24 -->
# Google Ranking Signals: Disclosed Systems and Leaked Attributes

This file maps Google systems and attributes to the checks in this repo. The sources are
Google's own documentation, the *US v. Google* record (D.D.C. No. 20-cv-3010, Judge Mehta),
and the 2024 Content Warehouse API leak. Use it to explain **why** a check matters. Do not
use it to score pages, assign weights, or promise ranking outcomes. Read the Caveats first.

## Evidence Legend

| Code | Evidence type | Default confidence |
|------|---------------|--------------------|
| OD | Official Google documentation (Search Central, How Search Works) | High |
| CO | Court opinion finding of fact (Mehta: liability, Aug 5 2024, Doc 1033; remedies, Sep 2 2025, Doc 1436) | High for existence and description |
| ST | Sworn trial testimony, as cited in an opinion | High for existence as of trial date |
| EX | Trial exhibit that is not sworn testimony (e.g. PXR0356, notes of a 2025-02-18 call with a Google engineer) | Medium |
| LK | Leaked internal API docs (Content Warehouse v0.4.0, March 2024) | Existence High, use and weight **Unknown** |

## A. Systems Confirmed in Court or by Google

| System | What it is | Evidence | Confidence | Audit implication |
|--------|-----------|----------|------------|-------------------|
| NavBoost | "Pairs queries and documents through memorizing user click data". Trained on 13 months of user data since 2017 (18 months before that). Called "one of the most power ranking components historically" in an exhibit quoted by the court | CO + ST (Doc 1033 ¶96, Nayak; ¶102) | High | SERP click satisfaction matters. Title and snippet must match intent and the page must deliver on it (seo-page). **Never** recommend click manipulation. The leaked click data has an IP-based prior field (`unscaledIpPriorBadFraction`, "used to assign a prior based on IP address", scaled in `craps-penalty.cc`); weight unknown |
| Glue | A "super query log" that includes clicks, hovers and duration on the SERP. "Glue is just another name for [N]avboost that includes all of the other features on the page" | CO + ST (Doc 1436 p.157, Nayak) | High | SERP features (images, video, rich results) compete for interaction. Eligibility work matters (seo-schema, seo-images) |
| QBST (Query-based Salient Terms) | Identifies words and word pairs that "should appear prominently on web pages that are relevant to that query". A "memorization system" | CO + ST (Doc 1033 ¶95, Lehman) | High | Key entities and co-occurring terms belong in title, H1 and early body. This is about **prominence**, not keyword density (seo-page, seo-content) |
| RankBrain, DeepRank, RankEmbed / RankEmbedBERT, RankBERT, MUM | "Generalization" systems that rely less on user data. RankEmbed(BERT) is trained on search logs plus human-rater scores. The court found "the more recent LLM signals" (MUM is an LLM, ¶99) "did not replace Navboost and QBST" and did not render the generalization systems obsolete | CO + ST (Doc 1033 ¶¶97-99, ¶102; Doc 1436 p.158); RankBrain, MUM also OD | High | Write naturally for semantic matching; cover the long tail and related questions (seo-content) |
| Top-level quality and popularity signals | Top-level signals "measuring a web page's quality and popularity" feed the final score. RankEmbed is also top-level. The court found "quality measures" are "constructed largely from sources other than user data". PageRank ("distance from a known good source") is "an input to the Quality score" (PXR0356). The popularity signal (P\*) "uses Chrome data" (PXR0356); "the number of anchors" as a popularity input comes from PXR0171. The court calls both only what "two exhibits suggest" | CO (Doc 1436 pp.142, 147-148) quoting EX (PXR0356, PXR0171) | High (existence); Medium (details) | Site- and page-level quality work (seo-content), link equity (seo-backlinks), internal linking (seo-technical) |
| Q\* / T\* / ABC | Exhibit shorthand. Q\* = "page quality (i.e., the notion of trustworthiness)", "largely static and largely related to the site rather than the query". T\* (topicality) combines Anchors, Body and Clicks. "Clicks (C)" is described as, historically, how long a user stayed on the linked page before returning to the SERP | EX (PXR0356), not sworn | Medium | Anchor text, on-page terms and click satisfaction together decide relevance (seo-page, seo-backlinks). Do not claim current dwell-time weighting |
| Crawl prioritization | "Quality and popularity signals ... help Google determine how frequently to crawl web pages", as does the spam score | CO (Doc 1436 p.142) | High | Inference (not a court finding): low-quality or spammy sections may be recrawled less often. Tie into crawl-budget advice (seo-technical) |
| FastSearch | Built on RankEmbed signals; used to ground Gemini models | CO (Doc 1436 p.39 ¶44) | High | Context for seo-geo only. Do not claim it is how AI Overviews rank |

### Google-documented ranking systems (OD, ranking-systems guide, updated 2025-12-10)

Google: "Our ranking systems are designed to work on the page level ... Site-wide signals and
classifiers are also used and contribute to our understanding of pages."

| System (Google's name) | Audit hook |
|------------------------|------------|
| Original content systems ("including original reporting ... support of a special canonical markup") | Originality checks (seo-content); canonical correctness (seo-technical) |
| Link analysis systems and PageRank ("continues to be part of our core ranking systems") | seo-backlinks; internal link structure (seo-technical) |
| Reviews system ("insightful analysis and original research") | Review-page quality (seo-content, seo-schema review guidelines) |
| Deduplication and site diversity ("generally won't show more than two web page listings from the same site in our top results") | Near-duplicates and cannibalization (seo-technical) |
| Exact match domain system | Do not recommend keyword domains as a ranking tactic |
| Freshness systems | Date accuracy, not date bumping (seo-content, seo-page) |
| Passage ranking ("identify individual sections") | Descriptive section headings (seo-page) |
| Removal-based demotion; spam detection (SpamBrain) | Legal/DMCA history; spam-policy checks |

Related OD statements: "Core Web Vitals are used by our ranking systems" and systems "generally
evaluate content on a page-specific basis ... However, we do have some site-wide assessments"
(page-experience doc). "E-E-A-T itself isn't a specific ranking factor" (creating-helpful-content).
"We use aggregated and anonymized interaction data to assess whether search results are relevant
to queries" (How Search Works).

## B. Leaked Attributes (Content Warehouse API docs v0.4.0)

Evidence type for every row: **LK**. Existence: High. Current use and weight: **Unknown**.
These modules appear in package docs v0.2.0-v0.4.0 (March 2024; v0.4.0, released 2024-03-28, is
used as the base URL); 0.5.0+ (2024-05-07) removed them, which says nothing about production use.
Base URL:
`https://google-api-content-warehouse.hexdocs.pm/0.4.0/GoogleApi.ContentWarehouse.V1.Model.<Module>.html`

### Site-level quality

| Attribute (Module) | Doc text (quoted) | Audit implication |
|--------------------|-------------------|-------------------|
| `siteAuthority` (CompressedQualitySignals) | "converted from quality_nsr.SiteAuthority, applied in Qstar" | Site-wide reputation and trust work, not only per-page fixes (seo-content) |
| `siteQualityStddev` (QualityNsrNsrData) | "spread of the page-level PQ ratings of a site" | Sample pages across sections; report quality variance; improve or prune weak clusters |
| `chardEncoded` (QualityNsrNsrData); `chard`, `tofu`, `vlq` (QualityNsrPQData) | "Site-level chard score: site quality predictor based on content"; URL-level chard/tofu/VLQ predictions | Content-derived quality predictors exist at site and URL level |
| `siteFocusScore`, `siteRadius` (QualityAuthorityTopicEmbeddingsVersionedItem) | "how much a site is focused on one topic"; "how far page_embeddings deviate from the site_embedding" | Flag off-topic sections and drift from the site's core topic (seo-content, seo-plan) |
| `pandaDemotion`, `babyPandaV2Demotion`, `lowQuality`, `unauthoritativeScore`, `scamness`, `serpDemotion`, `navDemotion` (CompressedQualitySignals) | "encoding of Panda fields"; "S2V low quality score"; "Unauthoritative score ... web page quality qstar signals"; "Scam model score" | Quality, trust and navigation demotion fields exist. Pair with thin-content, trust-page and UX checks |
| `clutterScore` (QualityNsrNsrData) | "penalizing sites with a large number of distracting/annoying resources loaded by the site" | Flag ad density, interstitials and heavy third-party clutter (seo-technical, seo-performance) |
| `smallPersonalSite`, `chromeInTotal` (QualityNsrNsrData) | "small personal site promotion"; "Site-level Chrome views" | Context only; nothing to audit directly |

### Page-level effort and originality

| Attribute (Module) | Doc text (quoted) | Audit implication |
|--------------------|-------------------|-------------------|
| `contentEffort` (QualityNsrPQData) | "LLM-based effort estimation for article pages" | Look for effort evidence: original data, first-hand media, process detail, depth that is hard to replicate (seo-content) |
| `OriginalContentScore` (PerDocData) | "Only pages with little content have this field" | Short pages still need unique content; flag short boilerplate or copied pages |
| `ugcDiscussionEffortScore` (CompressedQualitySignals) | "UGC page quality signals" | Forum/UGC sections: moderation and substantive discussion |
| `productReviewPUhqPage`, `productReviewPReviewPage`, `productReviewPDemoteSite` (CompressedQualitySignals) | "possibility of a page being a high quality review page"; "Product review demotion/promotion confidences" | Review pages: first-hand testing evidence, comparisons, pros/cons |

### Spam and relevance hygiene

| Attribute (Module) | Doc text (quoted) | Audit implication |
|--------------------|-------------------|-------------------|
| `KeywordStuffingScore`, `GibberishScore` (PerDocData) | "The keyword stuffing score ..."; "The gibberish score ..." | Keep the keyword-stuffing and nonsense-text checks |
| `spamrank` (PerDocData) | "likelihood that this document links to known spammers" | Audit outbound links (seo-content External Linking) |
| `exactMatchDomainDemotion`, `anchorMismatchDemotion` (CompressedQualitySignals) | "converted from QualityBoost.emd.boost"; "converted from QualityBoost.mismatched.boost" | Anchor text should match target content (seo-backlinks); no EMD tactics |
| `titlematchScore` (QualityNsrNsrData) | "Titlematch score of the site, a signal that tells how well titles are matching user queries" | Site-level score. Review title-to-intent match across the site's templates, not only one page (seo-page, seo-content) |

### Dates, structure, experience, clicks, classifiers

| Attribute (Module) | Doc text (quoted) | Audit implication |
|--------------------|-------------------|-------------------|
| `bylineDate` (QualityTimebasedSyntacticDate); `semanticDate`, `lastSignificantUpdate` (PerDocData) | byline date is kept when "different from the 'date' field"; date estimated "based on the contents of the document ..., anchors and related documents"; "Last significant update of the document" | Keep visible dates and schema `dateModified` consistent; change them only for substantive updates (OD: "changing the date of pages to make them seem fresh" is a warning sign) |
| `onsiteProminence`, `homepagePagerankNs` (PerDocData) | "propagating simulated traffic from the homepage and high craps click pages"; "page-rank of the homepage of the site" | Internal linking and crawl depth from the homepage (seo-technical) |
| `numOffdomainAnchors`, `linkIncoming` (QualityNsrPQData) | "total number of offdomain anchors seen by the NSR pipeline for this page" | Page-level backlink coverage (seo-backlinks) |
| `voltData` (PerDocData) → `mobileCwv`, `desktopCwv`, `displayUrlIsHttps` (IndexingMobileVoltVoltPerDocData) | "page UX signals for VOLT ranking change"; `lcp`, `cls`, `inp`, `fid` (IndexingMobileVoltCoreWebVitals) | CWV (mobile and desktop separately) and HTTPS checks. FID is a legacy field; report INP only |
| `goodClicks`, `badClicks`, `lastLongestClicks`, `impressions` (QualityNavboostCrapsCrapsData) | "clicks that were last and longest in related user queries"; sliced by country, device, language | Evaluate mobile SERP presentation separately; never suggest artificial clicks |
| `hostAge` (PerDocData) | "used in twiddler to sandbox fresh spam in serving time" | Context only. Do not claim a general "domain age factor" |
| `ymylHealthScore`, `ymylNewsScore` (PerDocData) | "scores of ymyl health classifier"; ymyl news classifier | Apply stricter E-E-A-T checks to health and news pages |
| `authorObfuscatedGaiaStr` (PerDocData) | no description | An author-identifier field exists. Confidence Low. Do **not** claim an "author reputation score" |

## C. Quick Map by Skill

- **seo-content**: top-level quality (A), site-level quality and topical focus (B), effort/originality (B), dates, YMYL classifiers, reviews system.
- **seo-technical**: crawl prioritization (A), deduplication/site diversity, `onsiteProminence`, `voltData`, `clutterScore`, canonical markup for original content.
- **seo-page**: NavBoost/Glue click satisfaction, QBST prominence, `bylineDate`, passage ranking; `titlematchScore` is site-level (title quality across templates).
- **seo-backlinks**: PageRank as input to quality, P\* anchor counts, `anchorMismatchDemotion`, `spamrank`, `numOffdomainAnchors`.
- **seo-geo**: FastSearch as context only.

## D. Caveats (read before citing anything above)

- **The leak shows that attributes exist, not weights or current use.** It is an internal API
  schema as of the March 2024 docs. It does not show thresholds, how signals combine, or whether
  a field is used in production today. Some fields are marked deprecated or experimental.
- Google confirmed the documents are authentic on 2024-05-29, cautioning against "inaccurate
  assumptions about Search based on out-of-context, outdated, or incomplete information"
  (spokesperson statement reported by The Verge; there is no Google-hosted statement).
- Court findings describe systems as of the 2023 liability trial and the 2025 remedies hearing.
  PXR0356 is notes of a call prepared for Google's side, not sworn testimony.
- Q\*, P\* and T\* are internal shorthand from exhibits and leak descriptions. Only "popularity
  signal (P\*)" is quoted in an opinion. Google has not published these names.
- "E-E-A-T itself isn't a specific ranking factor" (Google). Never present a leaked attribute as
  a confirmed ranking factor to optimize directly. Never recommend click manipulation.
- Do not add unverified third-party claims (for example leak "feature counts", or blog claims
  about Quality Rater Guidelines updates after the 2025-09-11 version).

## Sources

- Leak (v0.4.0 hexdocs; module names appended to the base URL in section B): CompressedQualitySignals, PerDocData, QualityNsrPQData, QualityNsrNsrData, QualityAuthorityTopicEmbeddingsVersionedItem, QualityNavboostCrapsCrapsData, QualityTimebasedSyntacticDate, IndexingMobileVoltVoltPerDocData, IndexingMobileVoltCoreWebVitals
- Liability opinion (Aug 5 2024): https://storage.courtlistener.com/recap/gov.uscourts.dcd.223205/gov.uscourts.dcd.223205.1033.0.pdf
- Remedies opinion (Sep 2 2025): https://storage.courtlistener.com/recap/gov.uscourts.dcd.223205/gov.uscourts.dcd.223205.1436.0.pdf
- PXR0356 (remedies exhibit): https://www.justice.gov/atr/media/1398871/dl ; DOJ case page: https://www.justice.gov/atr/case/us-and-plaintiff-states-v-google-llc
- https://developers.google.com/search/docs/appearance/ranking-systems-guide
- https://developers.google.com/search/docs/fundamentals/creating-helpful-content
- https://developers.google.com/search/docs/appearance/page-experience
- https://www.google.com/search/howsearchworks/how-search-works/ranking-results/
- News report of Google's confirmation: https://www.theverge.com/2024/5/29/24167407/google-search-algorithm-documents-leak-confirmation
