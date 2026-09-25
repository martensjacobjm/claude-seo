<!-- Updated: 2026-09-25 -->
# Local Schema Types & Industry-Specific Patterns

Sources: Google's [LocalBusiness structured data doc](https://developers.google.com/search/docs/appearance/structured-data/local-business)
(last updated 2026-09-08), schema.org (current vocabulary, fetched 2026-09-25) and Google
Business Profile guidelines. Register and removed claims: `local-eeat-evidence.md`.
Tags: [V] vendor-documented, [H] heuristic.

Google documents structured data as making a page eligible for a feature, with no guarantee:
"Using structured data enables a feature to be present, it does not guarantee that it will be
present." A structured data manual action "doesn't affect how the page ranks in Google web
search." Google names no ranking benefit; do not promise one. [V]

---

## LocalBusiness Subtypes (schema.org)

Google: "Use the most specific LocalBusiness sub-type possible." If a business has several
types, give them as an array (`additionalType` isn't supported). [V]

| Vertical | Types (schema.org) | Notes |
|----------|--------------------|-------|
| Food & dining | `Restaurant`, `CafeOrCoffeeShop`, `BarOrPub`, `Bakery`, `FastFoodRestaurant`, `IceCreamShop` | Generic parent: `FoodEstablishment` |
| Healthcare | `MedicalClinic`, `Hospital`, `Dentist`, `Physician`, `Optician`, `Pharmacy` | Generic parent: `MedicalBusiness`. `Physician` has subtypes `IndividualPhysician` (a doctor) and `PhysiciansOffice` |
| Legal | `LegalService` | `Attorney` is deprecated: "LegalService is more inclusive and less ambiguous" |
| Home services | `Plumber`, `Electrician`, `HVACBusiness`, `RoofingContractor`, `GeneralContractor`, `HousePainter`, `Locksmith`, `MovingCompany` | Generic parent: `HomeAndConstructionBusiness` |
| Real estate | `RealEstateAgent` | schema.org has no `RealEstateBrokerage` type (inference from absence) |
| Automotive | `AutoDealer`, `AutoRepair`, `AutoPartsStore` | Parent: `AutomotiveBusiness` |

### Other Common Local Types

`AnimalShelter`, `BeautySalon`, `ChildCare`, `DaySpa`, `DryCleaningOrLaundry`, `EmergencyService`, `EmploymentAgency`, `EntertainmentBusiness`, `FinancialService`, `FireStation`, `FurnitureStore`, `GasStation`, `GolfCourse`, `GovernmentOffice`, `HealthClub`, `Hotel`, `InsuranceAgency`, `Library`, `LodgingBusiness`, `NightClub`, `PetStore`, `PoliceStation`, `PostOffice`, `RecyclingCenter`, `ShoppingCenter`, `SkiResort`, `SportsActivityLocation`, `Store`, `TouristInformationCenter`, `TravelAgency`

`VeterinaryCare` exists but is a `MedicalOrganization`, not a `LocalBusiness` subtype.

---

## Google Required vs Recommended Properties [V]

### Required

| Property | Type | Notes |
|----------|------|-------|
| `name` | Text | The name of the business |
| `address` | PostalAddress | "Include as many properties as possible" (streetAddress, addressLocality, addressRegion, postalCode, addressCountry) |

### Recommended

| Property | Type | Google's note |
|----------|------|---------------|
| `geo` | GeoCoordinates | Latitude and longitude: "The precision must be at least 5 decimal places" |
| `openingHoursSpecification` | OpeningHoursSpecification | opens/closes in hh:mm:ss; validFrom/validThrough for seasonal closures |
| `telephone` | Text | Primary contact number; include country and area code |
| `url` | URL | "The fully-qualified URL of the specific business location" |
| `priceRange` | Text | "must be shorter than 100 characters" or Google won't show it |
| `department` | LocalBusiness | Nested department, named "{store name} {department name}" |
| `menu` | URL | Food establishments. schema.org now supersedes `menu` with `hasMenu`; Google's doc still lists `menu` |
| `servesCuisine` | Text | Restaurants |
| `aggregateRating`, `review` | AggregateRating, Review | **Only for sites that review other local businesses** (see below) |

**Self-serving reviews [V]:** "If the entity that's being reviewed controls the reviews about
itself, their pages that use LocalBusiness or any other type of Organization structured data
are ineligible for star review feature." This includes embedded Google or Facebook review
widgets. Also: "Don't aggregate reviews or ratings from other websites." A business's own
`aggregateRating` is therefore Info at most, never a recommendation.

`image` is not in Google's LocalBusiness list (it is required only for the limited-access
restaurant carousel). It is still valid schema.org. [V]

### Service-Area Businesses

| Property | Notes |
|----------|-------|
| `areaServed` | schema.org property (replaces the superseded `serviceArea`). Not in Google's LocalBusiness list. Naming cities, optionally with `sameAs` to Wikidata, is a heuristic [H] |

GBP guideline: a service-area business "should hide your business address from customers";
hybrid businesses may show a staffed storefront plus a service area. [V]

---

## Industry-Specific Schema Patterns [H]

Patterns built from schema.org types and properties. Only the LocalBusiness properties above
are Google-documented; the rest describe the business without a documented search feature.

### Restaurant
```
Restaurant (or specific subtype)
  + hasMenu (schema.org) or menu URL (Google) > Menu > MenuSection > MenuItem (offers, nutrition, suitableForDiet)
  + potentialAction: ReserveAction (bookings), OrderAction (ordering)
  + servesCuisine, acceptsReservations
```

### Healthcare
```
MedicalClinic (or Hospital, Dentist)
  + IndividualPhysician pages (or Person): medicalSpecialty, hospitalAffiliation, hasCredential
  + sameAs: official registry or licensing board entry where one exists
```
**Review responses [V]:** HHS OCR settled with Manasa Health Center for $30,000 (announced
2023-06-05) over "impermissible disclosures of patient protected health information in
response to negative online reviews." Never disclose patient information in a reply.

### Legal
```
LegalService (not Attorney, deprecated)
  + Person on attorney bio pages: jobTitle, worksFor, alumniOf, hasCredential (bar admissions)
  + makesOffer > Service (one per practice area)
```
GBP practitioner rules [V]: a public-facing practitioner may have their own profile; with
several practitioners at one location the organization gets a separate profile and the
practitioner profile carries only the practitioner's name; a solo practitioner at a branded
location shares one profile named "[brand/company]: [practitioner name]".

### Home Services
```
Specific subtype (Plumber, Electrician, etc.)
  + areaServed: named cities
  + Service on individual service pages, linked via provider
  + hasOfferCatalog for service listings
```

### Real Estate
```
RealEstateAgent (agents and brokerages)
  + Person on agent pages: memberOf (brokerage), hasCredential
  + RealEstateListing (a pending schema.org type) + SingleFamilyResidence/Apartment + Offer
```

### Automotive
```
AutoDealer (sales)
  + Car: vehicleIdentificationNumber, mileageFromOdometer, fuelType, vehicleTransmission
  + Offer: price, priceCurrency, availability
  + Service and parts: separate AutoRepair / AutoPartsStore entities (GBP department rules)
```
Google's vehicle listing rich result was phased out: announced 2025-06-12, docs removed
2025-09-09. `Car` + `Offer` markup remains valid schema.org but has no Google Search feature. [V]

---

## Industry Citation Sources [H]

Directories commonly used per vertical. Listing here is a practitioner heuristic; no traffic,
authority or ranking figures are claimed. Claim the profiles your customers actually use.

| Vertical | Directories |
|----------|-------------|
| Restaurant | Yelp, Tripadvisor, OpenTable, delivery platforms, Foursquare |
| Healthcare | Healthgrades, Zocdoc, WebMD, Vitals, Doximity, US NPI Registry, state medical boards |
| Legal | FindLaw, Martindale-Hubbell, Avvo, Justia, Super Lawyers, state bar directories |
| Home services | Thumbtack, BBB, Nextdoor, Yelp, Angi, Houzz |
| Real estate | Zillow, Homes.com, Realtor.com, Redfin, local MLS sites |
| Automotive | Cars.com, Autotrader, CarGurus, DealerRater, Edmunds, Kelley Blue Book, manufacturer dealer locators |

---

## Multi-Location Schema Pattern

```json
// Homepage: Organization
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "@id": "https://example.com/#org",
  "name": "Brand Name",
  "url": "https://example.com"
}

// Each location page: individual LocalBusiness
{
  "@context": "https://schema.org",
  "@type": "Dentist",
  "@id": "https://example.com/locations/downtown/#location",
  "name": "Brand Name - Downtown",
  "parentOrganization": { "@id": "https://example.com/#org" },
  "address": { ... },
  "geo": { "@type": "GeoCoordinates", "latitude": 40.71234, "longitude": -74.00567 },
  "telephone": "+1-555-123-4567",
  "openingHoursSpecification": [ ... ]
}
```

Use a unique `@id` per location. `branchOf` is superseded by `parentOrganization` in
schema.org [V]. A subdirectory structure (`example.com/locations/city-name/`) is a heuristic
for crawlable, consolidated location pages [H].

---

## Deprecated/Retired Local Markup [V]

| Type | Status | Date | Note |
|------|--------|------|------|
| `Attorney` | Deprecated by schema.org | n/a | Use `LegalService` (+ `Person`) |
| `branchOf`, `serviceArea`, `menu` | Superseded in schema.org | n/a | `parentOrganization`, `areaServed`, `hasMenu` |
| Vehicle listing (Google feature) | Phased out | Announced 2025-06-12, docs removed 2025-09-09 | No replacement feature |
| `SpecialAnnouncement` | Google feature deprecated | 2025-07-31; docs removed 2025-09-09 | None |
| `HowTo` | Rich result no longer shown | Docs removed 2023-09-14 | None |
