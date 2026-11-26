# Accuracy audit: independent-living-evanston (live)

Audited 2026-11-26 by the ESCG worker (ACQ-159, cse_014eaiSan3kSKEb4rtUHknYk) on main 4dc2468 under the review rules (scope rule included). Sources read 2026-11-26: IDPH Assisted Living; Medicare.gov Long-term care; CareScout 2025 Cost of Care Survey (PDF); NITA free and reduced fare programs; City of Evanston Access Evanston Program; HACC Ann Rainey Apartments page and its October 2021 waitlist notice (PDF). Quotation checker: 1/1 FOUND. The listing-website figures (read 6 Nov from three listing sites) were not re-read: they are dated in the page and are not a cited source. The tour path and how Westminster Place is presented were not reviewed (not the worker's to change).

| Guide's claim | Guide's scope | Source's scope (heading) | Result |
|---|---|---|---|
| IDPH quotation; licensing since July 2002 under December 2001 regulations | Illinois AL | IDPH Assisted Living: "Regulations were adopted in December of 2001 and IDPH began licensing establishments in July of 2002." | same |
| CareScout IL assisted living median $6,219/month; no IL independent-living median | Illinois | CareScout survey table "Assisted Living Community", Illinois $74,628 / $6,219; no independent-living table | same |
| Medicare doesn't pay for long-term care | Original Medicare | Medicare.gov: "Medicare doesn't pay for long-term care" | same |
| Reduced fare for riders 65+; Ride Free for Benefit Access enrollees after applying; NITA formerly RTA | region | NITA: "All individuals 65 years old and over who are ineligible for the NITA Ride Free Program are eligible to receive a reduced fare permit."; Ride Free Permits paragraph; "formerly the Regional Transportation Authority" | same |
| Access Evanston: residents 65+ or over 18 with a disability; "Income must be $35,000 or less for one person, or $60,000 or less for two" | all Evanston residents; transportation help | City page: "The Access Evanston Program is available to individuals residing in zip codes 60201 and 60202."; transportation groups "income of less than $17,500/year (1-person household)" and "between $17,501-$35,000/year (1-person household)"; the $60,000 figure appears only under "Access Evanston Wheel Tax Discount": "$35,000 or less (1 person) $60,000 or less (2 people)" | SCOPE DEFECT: the two-person limit belongs to the wheel-tax discount, and the program is limited to two zip codes. Corrected. |
| $5 coupon per one-way ride within Evanston; City-matched debit card up to a monthly limit; apply at Levy and other community centers | Access Evanston members | City page, Subsidized Taxicab Coupons; Transportation Debit Card; Where To Apply | same |
| HACC subsidizes rent in an Evanston building for 62+; resident pays 30%; October 2021 waitlist online only, 13 Oct morning to 15 Oct afternoon | Ann Rainey Apartments | HACC property page ("MUST be 62 years of age or older"; "pays 30% of his/her income"); notice ("beginning on Wednesday, October 13, 2021 at 10:00 a.m.", "submitted electronically ... no other form", "close at 4:00 p.m. on Friday, October 15, 2021") | same |
| Links (/guides/levels-of-senior-care-explained/, /guides/assisted-living-cost-illinois/, /guides/va-aid-and-attendance-benefit/, checklist PDF) | main | live on main | same |

Required corrections (applied in accuracy PR #89):
1. "In Evanston, the City's Access Evanston program, for residents of the 60201 and 60202 zip codes, helps residents 65 or older, or over 18 with a disability. For its transportation help, income must be $35,000 or less for a one-person household; the City's page gives no figure for a larger household." Source sentences as in the table.

Tests changed (check-guides.js, two assertions re-pinned with a dated comment, none removed): "IL guide: no listing-site price is printed" (its allowed-figure string) and "IL guide: transport help is stated as the agencies state it" (the Access Evanston sentence).

Review date: left at 6 November 2026, because the page's footnote says the listing-website figures were read "the same day" as the sources and those were not re-read; no listed date needed; sitemap and /guides/ unchanged.

Quotations checked: 1. Claims scope-checked: 9. Scope defects: 1. Corrections required: 1.
Verdict: corrections listed (applied to accuracy PR #89; reader check pending)

## Reader check 2026-11-26

Independent reader, branch claude/accuracy-20261125 at commit 8b2b0cd, cloned to /tmp/reader-independent-living-evanston. quotecheck: 1/1 FOUND, 7 cited pages, 0 unreadable (the 4 short terms are the guide's own phrases, not quotations). City of Evanston Access Evanston page (https://www.cityofevanston.org/accessevanston) fetched and read 2026-11-26; the link is the one already on main.

- "In Evanston, the City's Access Evanston program, for residents of the 60201 and 60202 zip codes, helps residents 65 or older, or over 18 with a disability." Source, under "Residency Requirement": "The Access Evanston Program is available to individuals residing in zip codes 60201 and 60202."; under "Subsidized Transportation": "The City of Evanston offers a choice of two special low-cost transportation options to Evanston seniors over the age of 65, and residents with disabilities over the age of 18 and are enrolled in the Access Evanston program." (and the eligibility heading "Individuals 65 and Over or Under 65 with a Disability" lists "Subsidized Transportation Program"). Same scope: Evanston residents of those two zip codes, the transportation program.
- "For its transportation help, income must be $35,000 or less for a one-person household; the City's page gives no figure for a larger household." Source, under "Subsidized Taxicab Coupons" and "Transportation Debit Card": "Group One: Program users with an income of less than $17,500/year (1-person household) ..." and "Group Two: Program users with an income between $17,501-$35,000/year (1-person household) ..."; no transportation figure for a larger household appears anywhere on the page. The $60,000 figure appears only under "Access Evanston Wheel Tax Discount" ("$35,000 or less (1 person) $60,000 or less (2 people)"), which the guide no longer attaches to transportation. Same scope.
Corrections verified

Reader: agent in cse_014eaiSan3kSKEb4rtUHknYk
Corrections verified: 2026-11-26, agent in cse_014eaiSan3kSKEb4rtUHknYk (#89 8b2b0cd)
