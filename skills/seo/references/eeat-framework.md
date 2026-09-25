<!-- Updated: 2026-09-25 -->
# E-E-A-T Evaluation Framework

Based on Google's Search Quality Rater Guidelines (edition dated September 11, 2025) and
Google Search Central. Sources and removed claims: `local-eeat-evidence.md`.
Tags: [V] Google-documented, [H] heuristic (practitioner rule of thumb, label it
"heuristic" in output, never above Medium).

## Overview

E-E-A-T = **E**xperience, **E**xpertise, **A**uthoritativeness, **T**rustworthiness

- **Trust is the most important member.** QRG: "Trust is the most important member of the
  E-E-A-T family because untrustworthy pages have low E-E-A-T no matter how Experienced,
  Expert, or Authoritative they may seem." Search Central: "Of these aspects, trust is most
  important." [V]
- **E-E-A-T is not a ranking factor by itself.** Search Central: "While E-E-A-T itself isn't
  a specific ranking factor, using a mix of factors that can identify content with good
  E-E-A-T is useful." Google's systems give "even more weight" to content with strong E-E-A-T
  on YMYL topics. [V]
- **Rater scores do not move pages.** QRG: "No single rating can directly impact how a
  particular webpage, website, or result appears in Google Search." Use the QRG as a
  description of what Google's systems aim for, not as a ranking formula. [V]

## YMYL (Your Money or Your Life)

Topics that "could significantly impact the health, financial stability, or safety of
people, or the welfare or well-being of society." The 2025-09-11 QRG lists four types [V]:

- **YMYL Health or Safety**: mental, physical and emotional health, physical and online safety
- **YMYL Financial Security**: a person's ability to support themselves and their families
- **YMYL Government, Civics & Society**: groups of people, issues of public interest, trust in
  public institutions, election and voting information
- **YMYL Other**: topics that could hurt people or the welfare of society

The QRG adds: "Many or most topics are not YMYL." YMYL is a spectrum; clear YMYL pages get
the most scrutiny. [V]

---

## Scoring Weights [H]

The weights below (Experience 20%, Expertise 25%, Authoritativeness 25%, Trustworthiness 30%)
are this skill's editorial heuristic. Google publishes no weights. Trust is weighted highest
because Google names it the most important member.

## Experience (Weight: 20%)

First-hand knowledge and personal involvement with the topic. The QRG asks raters to
"consider the extent to which the content creator has the necessary first-hand or life
experience for the topic." [V]

### Signals to Check [H]
- [ ] Author has demonstrable first-hand experience with the topic
- [ ] Content includes original photos, screenshots, or data
- [ ] Case studies or real-world examples with specific details
- [ ] Personal process documentation or methodology descriptions
- [ ] Before/after results or outcome data
- [ ] Specific anecdotes that couldn't be fabricated

### Scoring
- **Strong**: Multiple first-hand experience signals, original content
- **Moderate**: Some personal experience evident
- **Weak**: Generic information, no personal touch
- **None**: Copied or paraphrased content with no added value (QRG 4.6.6)

## Expertise (Weight: 25%)

Knowledge or skill relevant to the topic.

### Signals to Check [H]
- [ ] Author credentials relevant to topic (bio, certifications)
- [ ] Technical accuracy and depth appropriate for audience
- [ ] Claims supported by evidence or sources
- [ ] Specialized vocabulary used correctly
- [ ] Up-to-date with current developments in the field
- [ ] Byline with author name and credentials visible

### Scoring
- **Strong**: Verified credentials, deep technical accuracy
- **Moderate**: Demonstrable knowledge, some credentials
- **Weak**: Surface-level information, no credentials
- **None**: Factual errors, misinformation

## Authoritativeness (Weight: 25%)

Recognition by others as a go-to source. The QRG asks raters to look at "what others say
about the website or content creators" (independent reviews, references, news). [V]

### Signals to Check [H]
- [ ] Site recognized as authority in its niche
- [ ] Author recognized as expert (external citations, speaking, publications)
- [ ] Content cited by other authoritative sources
- [ ] Industry awards, certifications, or accreditations
- [ ] Consistent publication history in the topic area
- [ ] Featured in reputable media outlets
- [ ] Professional affiliations

### Scoring
- **Strong**: Widely recognized authority, cited by others
- **Moderate**: Growing recognition, some external validation
- **Weak**: No external recognition
- **None**: Negative reputation, known for misinformation

## Trustworthiness (Weight: 30%)

Overall reliability and transparency. The QRG (section 2.5.2 and 2.5.3) asks raters to find
who is responsible for the website, who created the content, and About, contact and
customer service information. [V]

### Signals to Check [H]
- [ ] Clear contact information (physical address, phone, email)
- [ ] Privacy policy and terms of service
- [ ] HTTPS with valid certificate
- [ ] Transparent about who creates content and why
- [ ] Customer reviews and testimonials (genuine, not incentivized without disclosure)
- [ ] Corrections and update history visible
- [ ] No deceptive practices (hidden ads, clickbait)
- [ ] Secure payment processing (for e-commerce)
- [ ] Return/refund policy visible

### Scoring
- **Strong**: Full transparency, verified business, positive reputation
- **Moderate**: Good trust signals, minor gaps
- **Weak**: Missing key trust signals
- **None**: Deceptive practices, scam indicators

## Generative AI Content [V]

- Search Central: using generative AI "to generate many pages without adding value for
  users may violate Google's spam policy on scaled content abuse."
- QRG 4.6.6: "the use of Generative AI tools alone does not determine the level of effort or
  Page Quality rating." The Lowest rating applies if all or almost all main content is
  "copied, paraphrased, embedded, auto or AI generated, or reposted from other sources with
  little to no effort, little to no originality, and little to no added value for visitors
  to the website."
- What matters is effort, originality and added value, regardless of how content was made.

### Markers of Low-Effort Content [H]
- Generic phrasing without specificity
- No original insight, data or first-hand experience
- Factual inaccuracies
- Repetitive structure across many pages
- Leftover tool phrasing such as "As an AI language model" (QRG example)

## Spam Policies Relevant to E-E-A-T [V]

Added to Google's spam policies on 2024-03-05 (Search Central changelog) and covered in QRG
sections 4.6.3 to 4.6.5:

- **Expired domain abuse**: an expired domain "purchased and repurposed primarily to
  manipulate search rankings by hosting content that provides little to no value to users"
- **Site reputation abuse** (now titled "Site reputation policy" in the spam policies, with a
  separate enforcement approach in the EEA): third-party content published on a host site
  "mainly because of that host's already-established ranking signals"
- **Scaled content abuse**: "many pages are generated for the primary purpose of manipulating
  search rankings and not helping users", "no matter how it's created"

## Content Licensing (context only)

RSL 1.0 is a machine-readable licensing standard for AI use (recommendation published
2025-12-10). See `skills/seo-geo/references/geo-evidence.md`. It is not an E-E-A-T signal.

---

## Overall Scoring Guide [H]

| Score | Description |
|-------|-------------|
| 90-100 | Exceptional E-E-A-T, authority site, recognized expert, full transparency |
| 70-89 | Strong E-E-A-T, demonstrated expertise, good trust signals |
| 50-69 | Moderate E-E-A-T, some signals, room for improvement |
| 30-49 | Weak E-E-A-T, minimal signals, significant gaps |
| 0-29 | Very low E-E-A-T, no visible signals, potential trust issues |

## Improvement Recommendations by Score [H]

Score bands describe the page. Severity of an individual finding still follows the evidence
rule: only a Google-documented issue (for example deceptive practices, scaled content abuse)
may be Critical or High.

| Score | Priorities |
|-------|------------|
| 0-29 | Add contact information and about page; Establish author identity with credentials; Implement HTTPS; Remove deceptive elements |
| 30-49 | Add author bios with credentials; Include first-hand experience content; Get external citations/mentions; Add genuine customer testimonials |
| 50-69 | Deepen content with original research; Build topical authority through content clusters; Pursue industry recognition; Document processes and methodologies |
| 70-89 | Update content when facts change (change dates only for real changes); Expand author presence across platforms; Pursue speaking/publication opportunities; Add video/multimedia demonstrating expertise |
| 90-100 | Continue publishing high-quality content; Monitor and respond to reputation issues; Keep credentials and certifications current |
