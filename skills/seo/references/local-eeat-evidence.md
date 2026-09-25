<!-- Updated: 2026-09-25 -->
# Local SEO and E-E-A-T Evidence Register

Every factual claim in `eeat-framework.md`, `local-schema-types.md`, `local-seo-signals.md`,
`skills/seo-local/SKILL.md` and `agents/seo-local.md` must trace to a row here. Add a source
only after fetching the primary document. AI search claims live in
`skills/seo-geo/references/geo-evidence.md`. All sources fetched 2026-09-25 unless noted.

## 1. Evidence Levels

| Tag | Level | Severity cap |
|-----|-------|--------------|
| [V] | Vendor documentation (Google, Bing, Apple, schema.org) or law and regulators (eCFR, FTC, HHS) | Any |
| [H survey] | Practitioner survey with published method (Whitespark, BrightLocal) | Medium, labeled "practitioner survey" |
| [H] | Practitioner heuristic, including all scoring weights | Medium, labeled "heuristic" |

A vendor's statement about another company's system is not [V]. Blog posts and news
articles are used only to locate primary sources.

## 2. Vendor and Official Sources [V]

### Google Search Central and Quality Rater Guidelines

| Source | Date | Claim used |
|--------|------|------------|
| [Search Quality Rater Guidelines](https://guidelines.raterhub.com/searchqualityevaluatorguidelines.pdf) | Edition 2025-09-11 | "Trust is the most important member of the E-E-A-T family"; four YMYL types incl. "YMYL Government, Civics & Society" (election and voting information); "Many or most topics are not YMYL"; "No single rating can directly impact" a page; Experience = "first-hand or life experience"; 4.6.3 to 4.6.5 spam types; 4.6.6 Lowest for content "auto or AI generated ... with little to no effort"; "the use of Generative AI tools alone does not determine the level of effort"; "As an AI language model" example |
| [Creating helpful content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content) | Last updated 2025-12-10 | "trust is most important"; "E-E-A-T itself isn't a specific ranking factor"; more weight for strong E-E-A-T on YMYL; do not change dates to seem fresh |
| [Guidance on generative AI content](https://developers.google.com/search/docs/fundamentals/using-gen-ai-content) | Last updated 2025-12-10 | Many AI pages without added value may violate the scaled content abuse policy |
| [Spam policies](https://developers.google.com/search/docs/essentials/spam-policies) | Last updated 2026-08-28 | Doorway abuse (city pages funnelling to one page, substantially similar pages); expired domain abuse; scaled content abuse; "Site reputation policy" (EEA enforcement change) |
| [Search Central changelog](https://developers.google.com/search/updates) | 2026 | 2024-03-05 three new spam policies; 2023-09-14 HowTo docs removed; SpecialAnnouncement deprecated from 2025-07-31; 2025-06-12 retirement banners; 2025-09-09 vehicle listing and special announcement docs removed |
| [Simplifying the search results page](https://developers.google.com/search/blog/2025/06/simplifying-search-results) | 2025-06-12, update 2025-09-08 | Vehicle Listing, Special Announcement and others phased out; "won't affect how pages are ranked" |
| [LocalBusiness structured data](https://developers.google.com/search/docs/appearance/structured-data/local-business) | Last updated 2026-09-08 | Required `address`, `name`; recommended list; geo "at least 5 decimal places"; priceRange "shorter than 100 characters"; "most specific LocalBusiness sub-type possible"; arrays, not `additionalType`; `image` only in the restaurant carousel |
| [Review snippet](https://developers.google.com/search/docs/appearance/structured-data/review-snippet) | Last updated 2026-09-08 | Self-serving LocalBusiness/Organization reviews ineligible for stars (incl. embedded widgets); "Don't aggregate reviews or ratings from other websites"; no fake or undisclosed incentivized reviews |
| [Structured data policies](https://developers.google.com/search/docs/appearance/structured-data/sd-policies) | Last updated 2026-07-10 | "enables a feature to be present, it does not guarantee"; manual action "doesn't affect how the page ranks" |
| [Link best practices](https://developers.google.com/search/docs/crawling-indexing/links-crawlable) | Last updated 2025-12-10 | Descriptive anchor text |
| [Search Status Dashboard, Ranking](https://status.search.google.com/products/rGHU1u87FJnkP6W2GwMi/history) | Fetched 2026-09-25 | Update start dates and durations 2025 to 2026 |

### Google Business Profile, Maps and Local Services

| Source | Date | Claim used |
|--------|------|------------|
| [Tips to improve your local ranking (7091)](https://support.google.com/business/answer/7091) | Fetched 2026-09-25 | "mainly based on relevance, distance, and popularity"; prominence from links and reviews; "no way to request or pay"; recommended actions. No mention of directories (inference from absence; the earlier wording was not re-fetched) |
| [Guidelines for representing your business (3038177)](https://support.google.com/business/answer/3038177) | Fetched 2026-09-25 | Real-world name; unnecessary info in name "isn't permitted"; SAB hides address; "about 2 hours of driving time"; departments; individual practitioners; "[brand/company]: [practitioner name]" |
| [Fake engagement policy (7400114)](https://support.google.com/contributionpolicy/answer/7400114) | Fetched 2026-09-25 | No incentives; do not "Discourage or prohibit negative reviews, or selectively solicit positive reviews from customers" |
| [Chat and call history (14919056)](https://support.google.com/business/answer/14919056) | Fetched 2026-09-25 | Both removed as of 2024-07-31 |
| [GBP API sunset dates](https://developers.google.com/my-business/content/sunset-dates) | Last updated 2026-08-28 | Q&A API support ended 2025-09-15, discontinued 2025-11-03; Business Calls API deprecated 2023-05-30 |
| [About Google Verified badge (16498018)](https://support.google.com/localservices/answer/16498018) | Fetched 2026-09-25 | Single LSA badge for all advertisers; Money Back Guarantee discontinued (claims before 2025-12-07) |
| [Tips for business-specific photos (6123536)](https://support.google.com/business/answer/6123536) | Fetched 2026-09-25 | Photo advice; contains no performance statistics |
| [Google Maps fake reviews, 2024](https://blog.google/products-and-platforms/products/maps/google-business-profiles-ai-fake-reviews/) | 2025-04-07 | "more than 240 million policy-violating reviews from 2024" |
| [New ways we're protecting businesses on Maps](https://blog.google/products-and-platforms/products/maps/new-ways-were-protecting-businesses-on-maps/) | 2026-04-16 | "over 292 million policy-violating reviews" in 2025 |

### schema.org, Apple, Bing, US law

| Source | Date | Claim used |
|--------|------|------------|
| [schema.org vocabulary](https://schema.org/version/latest/schemaorg-all-https.jsonld) | Fetched 2026-09-25 | Types and parents in `local-schema-types.md`; `Attorney` deprecated; `branchOf` to `parentOrganization`, `menu` to `hasMenu`, `serviceArea` to `areaServed` superseded; `RealEstateListing` pending; no `RealEstateBrokerage` or `VehicleListing` type (absence); `VeterinaryCare` is a MedicalOrganization |
| [Apple Business](https://business.apple.com/) | Fetched 2026-09-25 | businessconnect.apple.com redirects here; "Put your business on the map"; Custom Actions; Insights |
| Bing Places | 2026-02-10 | Entry in `geo-evidence.md` (AI Performance blog post) |
| [16 CFR Part 465](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-D/part-465) and [Federal Register 2024-18519](https://www.federalregister.gov/documents/2024/08/22/2024-18519/trade-regulation-rule-on-the-use-of-consumer-reviews-and-testimonials) | Published 2024-08-22, effective 2024-10-21 | Fake reviews, sentiment-conditioned incentives (465.4), review suppression (465.7) |
| [16 CFR 1.98](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-A/part-1/subpart-L/section-1.98) | Current eCFR | 45(m)(1)(A) penalty $53,088 |
| [OMB M-26-11](https://www.whitehouse.gov/wp-content/uploads/2026/04/M-26-11-Cancellation-of-Penalty-Inflation-Adjustments-for-2026-Regarding-the-Federal-Civil-Penalties-Inflation-Adjustment-Act-Improvements-Act-of-2015.pdf) | 2026-04-17 | No 2026 cost-of-living multiplier ("there will be no updated cost-of-living adjustment multiplier for 2026"), so $53,088 stands |
| [FTC: Soliciting and paying for online reviews](https://www.ftc.gov/business-guidance/resources/soliciting-paying-online-reviews-guide-marketers) | 2022 | "Don't ask for reviews only from customers you think will leave positive ones" (read via WebFetch; direct fetch returned 403) |
| [HHS OCR: Manasa Health Center](https://www.hhs.gov/hipaa/for-professionals/compliance-enforcement/agreements/manasa/index.html) | 2023-06-05 | $30,000; PHI disclosed in responses to negative online reviews |

## 3. Practitioner Surveys [H survey]

- **Whitespark, Local Search Ranking Factors 2026**
  ([link](https://whitespark.ca/local-search-ranking-factors/)), published 2025-11-06. 47
  invited experts scored 187 factors 0 to 5; "None of the experts have special access to the
  internal workings of Google's local search algorithm." Group weights read from the chart
  image `ranking-factor-groups.png`. Scores used: Primary GBP Category 227, proximity 225,
  keywords in GBP title 223, open at search 189, Dedicated Page for Each Service 210 (organic),
  Incorrect Primary Category 214 (negative #2). AI-visibility scores not used.
- **BrightLocal, Local Consumer Review Survey 2026**
  ([link](https://www.brightlocal.com/research/local-consumer-review-survey/)), published
  2026-02-11, 1,002 US adults (SurveyMonkey panel). Figures used: 41% "always" read (29% in
  2025), 31% 4.5+ stars (17%), 68% 4+ stars (55%), 74% last three months, 6 review sites, 42%
  unlikely to use a business that never replies, Apple Maps 27% (14%).

## 4. Removed Claims (2026-09-25)

Do not re-introduce these without a fetched primary source:

- E-E-A-T: "December 2025 core update ... watershed moment"; "E-E-A-T now applies to ALL competitive queries"; traffic drops "Affiliate 71%", "Health/YMYL 67%", "E-commerce 52%"; December 2025 "elevated the Experience dimension" (Google published no such description)
- E-E-A-T: "Elections and civic trust" / "Democratic processes" "added Sept 2025" (current QRG has one "Government, Civics & Society" type; the addition date was not verified)
- E-E-A-T: "Raters now formally evaluate whether content appears AI-generated"; "AI Overview Evaluation" section (not found in the QRG text); spam types called "New" in the Sept 2025 QRG (they date from 2024-03-05)
- RSL "Backed by Reddit, Yahoo, Medium, Quora, Cloudflare, Akamai, Creative Commons" (already in geo-evidence.md)
- Schema: "43% CTR increase, Webstix case study"; "Confirmed: John Mueller, Gary Illyes" (replaced by Google docs); `MedicalClinic`/`Hospital`/`Dentist` "eligible for rich results"; `image` as a Google-recommended LocalBusiness property; `aggregateRating` as a recommendation for a business's own site
- Schema: "VehicleListing deprecated June 12, 2025 ... Use Car + Offer instead" (no such schema.org type; the Google feature was phased out); "Feed-based Vehicle Listings via Merchant Center still functional"; "Google Food Ordering discontinued June 2024" (no primary source found); `branchOf` as the location link (superseded)
- Schema: "Bruce Clay study: 50%+ traffic lift" for subdirectories; "HIPAA ... Cannot confirm/deny reviewer is a patient" (replaced by the HHS wording); "Reviews follow practitioner listing"; "Service area in GBP does NOT currently impact rankings (Sterling Sky)"
- Citations: TripAdvisor "1B+ reviews"; Healthgrades "50% of Americans"; Doximity "80% of US physicians"; FindLaw "DA~91", Martindale "DA~84", Justia "DA~70", Super Lawyers "top 5%"; Internet Brands/Thomson Reuters ownership; Thumbtack "$400M revenue", "ChatGPT/Alexa/Zillow"; Angi "-30%"; Porch/Houzz pivots; Zillow "44% of RE search traffic", "integrated into ChatGPT Oct 2025"; Homes.com "100M monthly visitors"; Redfin acquisition; DealerRater syndication
- Ranking factors: Whitespark scores "193", "181", "176" (actual 227/223/214); "Incorrect primary category ... #1 negative factor" (it is #2); links "~26% of local organic" (survey: 24%); "Review Signals up from ~16% in 2023"; "3 of top 5 AI visibility factors are citation-related"
- Search Atlas ML study (proximity "55.2%", reviews "19.2%", "92-93% of variance")
- Sterling Sky: "Magic 10" reviews; "18-Day Rule"; "Diversity Update"; do not link GBP to strongest page; AI local packs "32% fewer businesses"; local pack ads "1% to 22%"; "ChatGPT traffic ~2%"
- BrightLocal: Google "71%" (from 83%), Instagram "37%", TikTok "29%" (not found in the survey text); "88% would use business that responds"; "optimal: 4 additional categories"
- Enforcement: "40% increase over 2023"; "Review deletion rates up 600%+ ... 38% were 5-star (GMBapi.com)"
- GBP: Q&A removed "Dec 3, 2025", "replaced by Ask Maps (Gemini AI)", "no export"; "GBP-hosted websites discontinued" (help page no longer available); "School reviews Apr 30, 2025"; Local Lists "Local Gems, Trending, Top List" (SOCi); "Google Verified badge (replaced Guaranteed/Screened Oct 2025)" as a GBP feature
- GBP insights: posts "No direct ranking impact (WebFX)"; photos "45% more direction requests" (Agency Jet); geotagging "NO impact"; attribute impact claims (WebFX/Sterling Sky)
- Updates: impact descriptions ("Emphasized E-E-A-T, penalized thin/AI content", "behavioral signal weighting", "favored local expertise", "Local Pack often stable"); "June 2025 Core Jun-Jul 17"
- Voice: "58% of voice searches are for local" (BusinessDasher); "4-7 words"; "80%+ of Google Assistant answers from top 3"; assistant data-source table (Siri "+ Yelp", Alexa "Bing Places + Yelp")
- AI local (also in geo-evidence.md): BrightLocal "45%"; Seer "15.9%", "1.76%", "+35%"; Whitespark "Up to 68%" AIO; Ahrefs "-58%" CTR; ChatGPT source list; Perplexity "21.87 citations", "40% more" (Qwairy)
- Local pack: "Standard 3 results"; zero-click "up to 78%" (Similarweb)
- Behavior: "46% of all Google searches seek local information"; "76% of mobile near-me searches lead to visit within 24 hours" (Google's live page no longer carries it); "900% increase in near me searches"; proximity "urban 1-2 miles, rural 5-10+ miles"
- Aggregators and platforms: Foursquare "Powers Uber, Nextdoor, Yahoo, ChatGPT. 500M+ devices"; Neustar "80+ platform partnerships"; Data Axle "Google, Bing, Apple"; Apple "1B+ iPhone users"; Apple Business Connect "usage nearly doubled" (the survey measures Apple Maps use, not Business Connect)
- seo-local: Chamber of Commerce "high Trust Flow, ~80% more consumer visits" (GlueUp); "Google uses BBB for business verification"; "5-10 quality local links/month"; "2-5 contextual internal links per 1,000 words"; HVAC "lost 80% rankings + 63% traffic"; "July 2025 documentation update removed directories" (date not verifiable)

## 5. Heuristics Kept [H]

| Heuristic | Rationale |
|-----------|-----------|
| E-E-A-T weights 20/25/25/30 and score bands | Editorial; Trust highest because Google names it most important |
| Local score weights 25/20/20/15/10/10 | Editorial prioritization |
| >60-70% unique location content, swap test | Operationalizes Google's doorway policy; no threshold documented |
| 30+/50+ location page gates | Orchestrator quality gate |
| NAP consistency across page, schema, GBP | Supports Google's "complete and accurate info"; no consistency metric documented |
| Industry directory lists | Where customers look; no reach figures claimed |
| `areaServed` with named cities; subdirectory location URLs | Clear, crawlable structure; not Google-documented for local |
