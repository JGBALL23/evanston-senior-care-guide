# Review packet: illinois-nursing-home-responsible-party

- Date: 2026-11-23
- Reviewer: ESCG worker (session cse_014eaiSbQh9aYSa5vTbwv5wK)
- Draft: `/tmp/drafts/build-guides.py` (GUIDES entry, slug `illinois-nursing-home-responsible-party`), rendered at `/tmp/drafts/_dist/guides/illinois-nursing-home-responsible-party/index.html`
- Rules applied: `/tmp/drafts/ROUTINE.md`, "Step 3 — rules of evidence" and "Quotation and paraphrase integrity"

## Sources fetched

| # | SRC key | URL | HTTP status | Local text |
|---|---|---|---|---|
| 1 | cms_qso2514_nh | https://www.cms.gov/files/document/qso-25-14-nh.pdf | 200 (application/pdf; memo Ref QSO-25-14-NH, dated March 10, 2025, with advance copy of Appendix PP attached) | /tmp/reviews/src-rp-1.txt (pdftotext -layout), src-rp-1.raw.txt |
| 2 | medicare_nh_guide | https://www.medicare.gov/publications/12217-your-guide-to-living-in-a-nursing-home | 200 after a 301 redirect to /publication/12217-your-guide-to-living-in-a-nursing-home.pdf (a two-page PDF fact sheet titled "Your guide to living in a nursing home") | /tmp/reviews/src-rp-2.txt |
| 3 | idoa_resident_rights_brochure | https://ilaging.illinois.gov/content/dam/soi/en/web/aging/resources/newsandpublications/publications/documents/ltc-resrights.pdf | 200 (application/pdf; IL-402-1444 (9/25)) | /tmp/reviews/src-rp-3.txt |

All three hosts are on the allowed list (cms.gov, medicare.gov, *.illinois.gov).

## Quote audit

I checked the quotes with a script that compared each one with the extracted PDF text. Before comparing, it collapsed whitespace, treated curly and straight apostrophes as the same, ignored nested quote marks and removed trailing punctuation. I then read every miss by hand. The script found 22 quotation spans. 21 match and 1 does not.

| # | Quote (≤80 chars) | Source | Match |
|---|---|---|---|
| 1 | Responsible Party (title) | 1 ("responsible party;") | yes |
| 2 | responsible party (desc) | 1 | yes |
| 3 | must not request or require a third party guarantee of payment to the facility… | 1 (§483.15(a)(3) regulation text) | yes |
| 4 | Make a third party (like your family) pay your nursing home bill. | 2 | yes |
| 5 | The facility must not request or require a third party guarantee of payment… | 1 | yes |
| 6 | The prohibition against third-party guarantees applies to all residents and pros… | 1 | yes |
| 7 | the facility may request and require a resident representative with legal access… | 1 (guidance text under §483.15(a)(3)) | yes |
| 8 | guarantee (section heading) | 1 | yes |
| 9 | guarantee. | 1 | yes |
| 10 | language can be noncompliant even if it does not specifically reference a 'guara… | 1 | yes. The source has a double-quoted “guarantee” here and the draft a single-quoted one (a nested-quote difference only). The source sentence begins "Also, language can be…" and the draft quotes from the middle of it, which is acceptable. |
| 11 | breach of an obligation in the agreement, | 1 | yes |
| 12 | implies the resident could be discharged if the representative does not voluntar… | 1 | yes |
| 13 | if it appears in the main document that a facility uses as its admission agreeme… | 1 | yes |
| 14 | cannot use such language in agreements regarding a resident's continued stay | 1 | yes |
| 15 | Read your admission agreement carefully | 2 (heading) | yes |
| 16 | You aren't required to agree to everything. For example, a nursing home isn't al… | 2 | yes. The script missed it only because of the bullet glyph "•" before "Make a third party". With the bullet removed, every word matches in order. |
| 17 | isn't allowed to | 2 | yes |
| 18 | cross out the item with a pen or marker before signing to show you don't agree. | 2 | yes |
| 19 | Your facility must not require anyone else to sign an agreement stating they wil… | 3 | yes |
| 20 | legal access | 1, 2 | yes |
| 21 | responsible party (assisted-living section) | 1 | yes |
| 22 | guarantor (assisted-living section) | none: the word "guarantor" does not appear in any of the three fetched sources | **no** |

## Claim checks

| Claim in draft | Result | Source's own wording |
|---|---|---|
| 42 CFR 483.15(a)(3) is the regulation | holds | Src 1: "§483.15(a)(3) The facility must not request or require a third party guarantee…"; the same document refers to "42 CFR Part 483, Subpart B" |
| It "binds every Medicare- or Medicaid-certified nursing facility" / applies regardless of payment source; "ability to private-pay does not remove this protection" | holds | Src 1: "applies to all residents and prospective residents in all certified long term care facilities, regardless of payment source." |
| "The requirement sits in the Medicare and Medicaid **conditions of participation**" | does not hold as named | Src 1 calls them the "Long-term Care Requirements for Participation". "Conditions of participation" is the hospital term (e.g. "Conditions of Participation for Hospitals"). |
| "CMS's current surveyor guidance (QSO-25-14-NH)" | holds for the memo number. "Current" cannot be verified from the page. | Src 1: "Ref: QSO-25-14-NH … DATE: March 10, 2025 … Effective Date: … April 28, 2025". (This is a note only. Dropping "current" would be safer, but I have not listed it as a required correction.) |
| A facility may only ask a representative with legal access to use the resident's own money to pay, without personal liability | holds | Src 1: "may request and require this representative to sign a contract, without incurring personal liability, to provide the facility with payment from the resident's income or assets." Src 2: "It may only ask your family to use your money to pay the bills (if your family has legal access to your funds)." |
| "CMS's guidance continues:" (before quote 7) | holds, though loosely | In Src 1 the quoted sentence comes before the "prohibition … applies to all residents" sentence, not after it. The wording is accurate. Only the word "continues" describes the order loosely. |
| Bullet: joint responsibility of resident and representative is noncompliant; naming the resident alone is allowed | holds | Src 1: "holds both (1) the resident and (2) the representative or other individual jointly responsible for any sums due … (however, language that holds the resident solely responsible without joining the representative is allowable)." |
| Bullet: personal liability for breach "such as not applying for Medicaid in time" | holds (a fair shortening) | Src 1: "such as (1) failing to apply for Medicaid in a timely and complete manner or (2) …" |
| Bullet: implied discharge threat | holds | Src 1 (quoted exactly) |
| Bullet: liability for not supplying accurate financial info / not reporting a change | holds | Src 1: "did not provide accurate financial information or notify the facility of changes in the resident's financial information." |
| The rule covers other documents signed at admission and continued-stay agreements | holds | Src 1 (quoted exactly) |
| Medicare: a nursing home isn't allowed to require binding arbitration "as a condition of admission or care" | holds | Src 2: "Require you to sign an agreement to resolve issues outside of state or federal courts (known as “binding arbitration”) to be admitted or get care." |
| Medicare suggests asking a lawyer to review first, if you have one | holds | Src 2: "If you have a lawyer, you can also ask them to review the agreement before you sign." |
| Answer: "Illinois's own residents' rights brochure adds a **state-law version** of the same limit" | **does not hold** | Src 3 never says that its contract statement comes from Illinois law. It cites no Act or statute for it. Its only mention of an Act is the Older Americans Act, in connection with ombudsman funding. |
| Heading "Illinois adds its own version of the same limit" | does not hold as framed: it implies a state-law rule the source does not state | Src 3: "Your facility must not require anyone else to sign an agreement stating they will pay for your bill unless they are your court appointed guardian." |
| Illinois exception is "a **narrower exception** than the federal rule" | **does not hold** (the draft's own interpretation) | Neither source compares the two exceptions. The draft itself goes on to say it is "reporting that difference rather than resolving it", and "narrower" contradicts that. |
| Brochure published by Illinois Department on Aging, for long-term care facilities | holds | Src 3: "Residents' Rights for People in Long-Term Care Facilities … Illinois Department on Aging" |
| Ask "the Long-Term Care Ombudsman" | holds | Src 3: "Seek assistance from the Illinois Long-Term Care Ombudsman Program" |
| The federal rule applies "to Medicare- and Medicaid-certified nursing facilities, not to assisted living or shared housing establishments, **which are licensed under a separate Illinois law and are not nursing homes**" | **does not hold** (no source cited for it) | None of the three sources mentions assisted living licensing, shared housing establishments or a separate Illinois law. Src 1 gives the scope only as "all certified long term care facilities". |
| "This guide searched for an equivalent Illinois government page addressing responsible-party or guarantor language specifically in assisted living contracts and did not find one on an allowed host" | holds | The three fetched pages contain no assisted-living contract language. I ran two web searches, one of them limited to site:illinois.gov. The only results were Illinois Administrative Code and ILCS text on ilga.gov (77 Ill. Adm. Code 295.2030; 210 ILCS 9/90), which is not an allowed host, and nursing-home rules (77 Ill. Adm. Code 300 and 350) that the search summary says require a defined "responsible party" or "guarantor" signature line. I could not open the ilga.gov pages (HTTP 503 or no response), so I have not verified that summary. The draft's statement is accurate as worded ("on an allowed host"). Editor's note: if the ilga.gov rules say what the summary says, Illinois nursing-home rules allow a "responsible party" or "guarantor" signature line, with the liability defined. That is a further reason not to describe the brochure as a "state-law version of the same limit". |

## Link check

All internal guide links resolve to slugs that are live in `/tmp/site/build-guides.py`:

- /guides/illinois-nursing-home-resident-rights/: live (line 2638)
- /guides/illinois-advance-directive-power-of-attorney/: live (line 3188)
- Related links added by the template (/guides/assisted-living-cost-illinois/, /guides/does-medicare-pay-for-senior-care/, /guides/illinois-supportive-living-program/): all live
- /guides/ and / (the assessment): fine

The draft links to no draft-only guide. The only external links on the page are the three Sources URLs.

## Rule checks

- Ranking or recommending communities: none.
- Westminster Place: the name appears only in the standard site-wide author disclosure (in the JSON-LD and the footer). The page gives no prices and makes no claims about Westminster Place.
- Marketing urgency: none. The bridge and closing CTA follow the fixed assessment wording ("no name, no email and no phone number … never leave your device").
- Unverified medical, legal, financial or benefits claims: three found. The "state-law version" claim, the "narrower exception" interpretation and the "licensed under a separate Illinois law" claim are all unsupported (see corrections 2–5). Everything else traces to a sentence in a fetched source.
- Sources are on allowed hosts only: yes.

## Required corrections

1. **Quotation not on any source page (quote #22).**
   - Current: `read any signature line labelled &ldquo;responsible party&rdquo; or &ldquo;guarantor&rdquo; carefully`
   - Replacement: `read carefully any signature line that would make you a responsible party or guarantor`
   - Source basis: the word "guarantor" appears in none of the three fetched sources, so it cannot sit inside quotation marks. Used as a plain word, it describes what Src 1 prohibits: "language that specifically requests a third party to personally guarantee payment to a facility is noncompliant."

2. **Unsupported "state-law" claim (answer).**
   - Current: `and Illinois&rsquo;s own residents&rsquo; rights brochure adds a state-law version of the same limit.`
   - Replacement: `and the Illinois Department on Aging&rsquo;s residents&rsquo; rights brochure states a similar limit in its own words.`
   - Source sentence (Src 3): "Your facility must not require anyone else to sign an agreement stating they will pay for your bill unless they are your court appointed guardian." The brochure cites no Illinois law for this.

3. **Heading implies a state-law rule.**
   - Current: `("Illinois adds its own version of the same limit", [`
   - Replacement: `("How Illinois's residents' rights brochure puts it", [`
   - Source basis: as for correction 2. The source is a brochure statement, not a cited statute.

4. **Added interpretation ("narrower").**
   - Current: `"the same protection in its own words, with a narrower "` / `"exception than the federal rule: &ldquo;Your facility must "`
   - Replacement: `"the same protection in its own words, with a differently "` / `"worded exception from the federal rule: &ldquo;Your facility must "`
   - Source sentences: Src 3, "unless they are your court appointed guardian"; Src 1, "a resident representative with legal access to the resident's funds". Neither source says one exception is narrower than the other, and the draft's next sentence says the guide is not resolving the difference.

5. **Unsourced licensing claim (assisted-living section).**
   - Current: `"its own terms to Medicare- and Medicaid-certified "` / `"<strong>nursing facilities</strong>, not to assisted living "` / `"or shared housing establishments, which are licensed under a "` / `"separate Illinois law and are not nursing homes. This guide "`
   - Replacement: `"its own terms to &ldquo;all certified long term care "` / `"facilities&rdquo;; none of the three sources this guide read "` / `"addresses assisted living or shared housing contracts. This guide "`
   - Source sentence (Src 1): "The prohibition against third-party guarantees applies to all residents and prospective residents in all certified long term care facilities, regardless of payment source." No fetched source mentions assisted living licensing or a separate Illinois law.

6. **Wrong programme name.**
   - Current: `"must meet. CMS's current surveyor guidance (QSO-25-14-NH) "` is preceded by `"<p>The requirement sits in the Medicare and Medicaid "` / `"conditions of participation every certified nursing facility "`
   - Replacement: `"<p>The requirement sits in the Medicare and Medicaid "` / `"requirements for participation every certified nursing facility "`
   - Source sentence (Src 1): "…how they will demonstrate compliance with the Long-term Care Requirements for Participation…"

Optional (not required): drop "current" from "CMS's current surveyor guidance" and from "CMS's own current guidance" in the desc. The memo is dated March 10, 2025, and this review did not confirm that no later revision exists.

Verdict: publish-ready after corrections
