<!-- Updated: 2026-09-24 -->
# Schema.org Types: Status & Recommendations (September 2026)

**Schema.org Version:** 30.1 (September 16, 2026). Previous: 30.0 (March 19, 2026), 29.4 (December 8, 2025). Source: https://schema.org/docs/releases.html

**Google sources:** Search Central changelog (https://developers.google.com/search/updates) and search gallery (https://developers.google.com/search/docs/appearance/structured-data/search-gallery, last updated 2026-06-15).

## Format Preference
Always use **JSON-LD** (`<script type="application/ld+json">`).
Google's documentation explicitly recommends JSON-LD over Microdata and RDFa.

**AI Search Note:** Google: "Structured data isn't required for generative AI search, and there's no special schema.org markup you need to add." Keep using it for rich-result eligibility (https://developers.google.com/search/docs/fundamentals/ai-optimization-guide, updated 2026-07-10).

---

## Active: Recommend freely

Key properties for gallery types below are taken from Google's doc examples for each feature.

| Type | Use Case | Key Properties |
|------|----------|----------------|
| Organization | Company info | name, url, logo, contactPoint, sameAs; hasMerchantReturnPolicy / shipping policy for merchants |
| LocalBusiness | Physical businesses | name, address, telephone, openingHours, geo, priceRange |
| SoftwareApplication | Desktop/mobile apps | name, operatingSystem, applicationCategory, offers, aggregateRating |
| WebApplication | Browser-based SaaS | name, applicationCategory, offers, browserRequirements, featureList |
| Product | Physical/digital products | name, image, description, sku, brand, offers, review, category, hasCertification |
| Offer | Pricing | price, priceCurrency, availability, url, validFrom, validThrough / priceValidUntil |
| Service | Service businesses | name, provider, areaServed, description, offers |
| Article | Blog posts, news | headline, author, datePublished, dateModified, image, publisher |
| BlogPosting | Blog content | Same as Article + blog-specific context |
| NewsArticle | News content | Same as Article + news-specific context |
| Review | Individual reviews | reviewRating, author, itemReviewed, reviewBody (see Review snippet guidelines below) |
| AggregateRating | Rating summaries | ratingValue, reviewCount, bestRating, worstRating (see Review snippet guidelines below) |
| BreadcrumbList | Navigation | itemListElement with position, name, item |
| WebSite | Site-level | name, alternateName, url (used for site names: https://developers.google.com/search/docs/appearance/site-names; sitelinks search box removed Nov 29, 2024: https://developers.google.com/search/updates) |
| WebPage | Page-level | name, description, datePublished, dateModified |
| Person | Author/team | name, jobTitle, url, sameAs, image, worksFor |
| ContactPage | Contact pages | name, url |
| VideoObject | Video content | Required: name, thumbnailUrl, uploadDate. Rec.: contentUrl/embedUrl, description, duration, creator (or author), interactionStatistic (WatchAction/LikeAction/CommentAction/ShareAction) |
| ImageObject | Image content | contentUrl, caption, creator, copyrightHolder |
| Event | Events | name, startDate, endDate, location, organizer, offers |
| JobPosting | Job listings | title, description, datePosted, hiringOrganization, jobLocation |
| Course | Educational content (Course list) | name, description, provider, hasCourseInstance |
| DiscussionForumPosting | Forum threads | author, datePublished, text/image/video; rec. comment, commentCount, creativeWorkStatus, digitalSourceType, interactionStatistic, isPartOf, sharedContent |
| ProductGroup | Variant products | name, productGroupID, variesBy, hasVariant |
| ProfilePage | Author/creator profiles | mainEntity (Person), name, url, description, sameAs |
| Recipe | Recipes | name, image, recipeIngredient, recipeInstructions |
| QAPage | Single-question Q&A pages | mainEntity (Question) with answerCount, acceptedAnswer / suggestedAnswer |
| Quiz | Education Q&A (flashcards) | hasPart (Question) |
| MathSolver | Math solver tools | `@type` ["MathSolver","LearningResource"], url, usageInfo, learningResourceType "Math Solver" (required, fixed value), potentialAction (SolveMathAction with target and required mathExpression-input); `assesses` when paired with a HowTo (https://developers.google.com/search/docs/appearance/structured-data/math-solvers) |
| EmployerAggregateRating | Employer ratings | itemReviewed (Organization), ratingValue, ratingCount |
| VacationRental | Vacation rental listings | containsPlace, identifier, image, latitude, longitude, name |
| Movie | Movie carousel | name, image, dateCreated, director |
| Dataset | Dataset pages | Used by Google **Dataset Search only**, not Google Search (clarified Nov 5, 2025; https://developers.google.com/search/docs/appearance/structured-data/dataset) |
| Book (Book actions) | Feed-based book actions | Still supported; deprecation banner removed Nov 5, 2025 "as there's still a feature using the markup" (https://developers.google.com/search/updates) |

Gallery features listed on the search gallery but not detailed here: Carousel, Image metadata, Local business, Speakable, Subscription and paywalled content. Merchant-only docs: Loyalty program, Merchant return policy, Merchant shipping policy, Variants.

---

## Phasing out: Info only, don't recommend adding

| Type | Status | Source |
|------|--------|--------|
| ClaimReview | "We're phasing out support for ClaimReview markup in Google Search. However, this markup remains supported by the Factcheck Explorer Tool." Banner added June 12, 2025; doc still live | https://developers.google.com/search/docs/appearance/structured-data/factcheck |

---

## No Google rich result (valid schema.org type)

| Type | Status | Source |
|------|--------|--------|
| FAQPage | FAQ rich result no longer shown in Google Search starting **May 7, 2026** (deprecation notice May 8, 2026); docs removed **June 15, 2026** | https://developers.google.com/search/updates#deprecating-the-faq-rich-result-feature, https://developers.google.com/search/updates#removing-faq-rich-result |

> The earlier Aug 2023 gov/health restriction is superseded: no site gets FAQ rich results now.
> - **Existing FAQPage**: Flag at Info priority. The markup is valid schema.org and harmless; removal is optional.
> - **Adding new FAQPage**: Don't recommend it for Google. Claims that FAQPage improves AI/LLM citations (ChatGPT, Perplexity, AI Overviews) are **unverified**; for Google they are contradicted by the AI optimization guide quoted above.

---

## Deprecated: Never recommend

| Type / Feature | Status | Since | Notes |
|----------------|--------|-------|-------|
| HowTo | Rich results fully removed | September 2023 | Doc URL now redirects to https://developers.google.com/search/updates#how-to-deprecation |
| SpecialAnnouncement | Deprecated | July 31, 2025 | Docs removed Sep 9, 2025 |
| CourseInfo (course info) | No longer shown | Banner June 12, 2025 | Docs removed Sep 9, 2025. Google feature name, not a schema.org type (the Course list feature remains active) |
| EstimatedSalary (estimated salary) | No longer shown | Banner June 12, 2025 | Docs removed Sep 9, 2025. Google feature name, not a schema.org type |
| LearningVideo (learning video) | No longer shown | Banner June 12, 2025 | Docs removed Sep 9, 2025. Google feature name; use plain VideoObject |
| VehicleListing (vehicle listing) | No longer shown | Banner June 12, 2025 | Docs removed Sep 9, 2025. Google feature name, not a schema.org type |
| Practice problem | No longer shown | Deprecated Nov 5, 2025 | Docs removed Jan 6, 2026 (https://developers.google.com/search/updates#removing-practice-problems) |
| FAQ rich result (FAQPage) | No longer shown | May 7, 2026 | Docs removed June 15, 2026 (see section above) |

Source for Sep 9, 2025 removals: https://developers.google.com/search/updates ("These structured data types are no longer shown in Google Search results").

---

## Recent Google Changes (2025-2026)

All dates from https://developers.google.com/search/updates unless noted.

| Change | Date | Notes |
|--------|------|-------|
| VideoObject `creator` (or `author`) + supported `interactionStatistic` types | 2026-09-24 | creator is Person/Organization with name or alternateName; creator.url recommended. interactionType: WatchAction, LikeAction, CommentAction, ShareAction (https://developers.google.com/search/docs/appearance/structured-data/video) |
| Review snippet: no fake or undisclosed incentivized reviews | 2026-07-24 | Applies to on-page reviews and structured data |
| Product.category accepts Text and CategoryCode | 2026-07-07 | CategoryCode: inCodeSet = Google Product Taxonomy URL, codeValue = GPC ID |
| Merchant listing "Sale duration" section | 2026-07-07 | Sale start: validFrom; sale end: validThrough or priceValidUntil |
| `hasAdultConsideration` (AdultOrientedEnumeration) | 2026-05-20 | Merchant listing + Product variant docs; must label adult-oriented products; Google Search only supports `https://schema.org/SexualContentConsideration` |
| More supported Discussion Forum / QA Page properties | 2026-03-24 | Changelog does not itemize which; see current Discussion forum doc |
| Merchant-level shipping policy markup (Organization) | 2025-11-12 | https://developers.google.com/search/docs/appearance/structured-data/shipping-policy |
| Review snippet: avoid multiple ways of indicating what's reviewed | 2025-11-12 | Clarified nesting in reviews and aggregate ratings |
| Product Certification markup | April 2025 | Replaced EnergyConsumptionDetails (see E-commerce requirements) |
| LoyaltyProgram | June 2025 | Member pricing, loyalty card structured data |

## Schema.org Vocabulary Changes (no Google feature documented)

Source: https://schema.org/docs/releases.html. Valid vocabulary, but no Google rich result is documented for these as of 2026-09-24. Don't promise Search benefits.

| Release | Additions |
|---------|-----------|
| 30.1 (2026-09-16) | DigitalProductPassport + hasDigitalProductPassport (Product, Offer); EnvironmentalProductDeclaration and DeclarationOfConformity (Certification subtypes); authorizedRepresentative; importer, recycledContentPercentage, substanceOfConcern, consumerNotice, isOftenBoughtWith, specification (Product); itemPopularity (Offer); minimumOrderValue (ShippingRateSettings); MaximumRetailPrice (PriceTypeEnumeration) |
| 30.0 (2026-03-19) | Credential class (hasCredential); Error class + errorCode; jobDuration (JobPosting); floorLevel (LocalBusiness, Residence); Quantity now inherits from DataType; GS1/Dublin Core/Open Graph equivalence annotations |
| 29.4 (2025-12-08) | ConferenceEvent, PerformingArtsEvent, SequentialArt (GraphicNovel deprecated), OperatingSystem and RuntimePlatform (SoftwareApplication subtypes) |

## Review Snippet Guidelines (2025-2026)

Source: https://developers.google.com/search/docs/appearance/structured-data/review-snippet
- Don't include fake or undisclosed incentivized reviews on the page or in markup (reviews not based on genuine experience, or written for money, discounts, vouchers or free products without clear, prominent disclosure). Added 2026-07-24.
- Avoid using multiple ways of indicating what's being reviewed (2025-11-12).
- Recommendation: only accept ratings accompanied by a review comment and author name (2025-01-15).
- Self-serving reviews: LocalBusiness/Organization review snippets are only supported "for sites that capture reviews about other" businesses/organizations, not about themselves.

## E-commerce Requirements

Source: https://developers.google.com/search/docs/appearance/structured-data/merchant-listing and https://developers.google.com/search/docs/appearance/structured-data/return-policy

| Requirement | Status |
|-------------|--------|
| MerchantReturnPolicy | Required: Option A `applicableCountry` + `returnPolicyCategory` (+ `merchantReturnDays` if finite window) OR Option B `merchantReturnLink` |
| `returnPolicyCountry` | **Recommended** in the current return-policy doc (updated 2026-09-08). Google's 2025-03-14 changelog entry called it required; the current doc supersedes that |
| OfferShippingDetails | Required: `deliveryTime`, `shippingDestination` (DefinedRegion with addressCountry), `shippingRate` |
| Certification | Required: `issuedBy` (supported names: EC / European_Commission, ADEME, BMWK) and `name` (EPREL, Vehicle_CO2_Class, Vehicle_CO2_Class_Discharged_Battery). `certificationIdentification` recommended; required for EU energy labels |
| Product variant structured data | ProductGroup + hasVariant + variesBy |

> **Note:** Content API for Shopping was sunset on August 18, 2026; requests progressively error from September 1, 2026. Use Merchant API (https://developers.google.com/merchant/api/guides/compatibility/overview).

> **JavaScript:** Dynamically generated Product markup "can make Shopping crawls less frequent and less reliable" (https://developers.google.com/search/docs/appearance/structured-data/generate-structured-data-with-javascript). Put Product/Offer JSON-LD in server-rendered HTML.

---

## Validation Checklist

For any schema block, verify:

1. ✅ `@context` is `"https://schema.org"` (not http)
2. ✅ `@type` is a valid, non-deprecated type
3. ✅ All required properties are present
4. ✅ Property values match expected data types
5. ✅ No placeholder text (e.g., "[Business Name]")
6. ✅ URLs are absolute, not relative
7. ✅ Dates are in ISO 8601 format
8. ✅ Images have valid URLs
9. ✅ Review markup contains no fake or undisclosed incentivized reviews

## Testing Tools

- [Google Rich Results Test](https://search.google.com/test/rich-results)
- [Schema.org Validator](https://validator.schema.org/)
