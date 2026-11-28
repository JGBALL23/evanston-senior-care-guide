# Medicare page search study: what Google's top results answer that ours does not

Project PJ01 ("Medicare page to Google's first page"), step 1 (investigate) and step 2 (strategy).
Written by the ESCG worker, 28 Nov 2026, session cse_014eaiSeLUyuyJkYCTLw4xJi. Research only: nothing here is published or sent.

## Evidence and dates

- **Search Console**, read by Make on 25 Nov 2026 (period 26 Oct to 22 Nov 2026; only 16 to 22 Nov have rows). /guides/does-medicare-pay-for-senior-care/ had 781 impressions, 0 clicks and an average position of 32.5. The whole site had 1,242 impressions.
- **The trend in that read:** daily impressions for the site rose from 38 (16 Nov) to 397 (22 Nov), and the weighted position improved from 47.4 to 28.3. The Medicare page drives most of that rise, so the page is still climbing on its own. Any change has to be judged against that rise, not against a flat baseline.
- **The query cluster:** 32 Medicare and assisted-living queries with 579 impressions (weighted position 33.0), and 15 Medicare and nursing-home queries with 120 impressions (position 31.7).
  - The 10 biggest: "does medicare cover assisted living" 87 impressions at position 36.7; "medicare assisted living" 46 at 27.9; "how much does medicare pay for assisted living" 44 at 45.7; "does medicare cover assisted living costs" 43 at 25.8; "does medicare pay for assisted living" 42 at 33.6; "medicare and assisted living costs" 28 at 15.8; "how to pay for assisted living with medicare" 26 at 35.4; "medicare pay for assisted living" 24 at 24.1; "does medicare cover assisted living facilities" 23 at 26.4; "does medicare pay for nursing home care" 22 at 28.7.
  - Cost-worded queries ("how much", "cost") add up to 208 impressions. "how much does medicare pay for assisted living" (44) and "... facility" (19) rank worst, at 45.7 and 61.4.
  - Already on page 2 (position 20 or better): "medicare senior living" 12.0, "how much does medicare pay for nursing home stay" 12.5, "assisted living costs and medicare" 13.0, "does medicare assist with assisted living" 14.8, "medicare and assisted living costs" 15.8, "does medicare cover assisted living facility" 16.4, "how much does medicare cover for assisted living" 19.9.
  - Local: "does medicare pay for assisted living in illinois" 7 impressions at position 52.6. Out-of-state variants also appear: "... in florida" 7 at 41.7 and "... in california" 3 at 46.3.
- **Search results read on 28 Nov 2026** (web search for "does medicare cover assisted living", "how much does medicare pay for assisted living", "how to pay for assisted living with medicare", "does medicare pay for nursing home care for the elderly" and "does medicare pay for assisted living in illinois"). The same sites lead every set:
  - AARP (3 URLs)
  - NCOA
  - Healthline
  - Humana (2 URLs)
  - Care.com
  - NerdWallet
  - GoodRx
  - Caring.com
  - UnitedHealthcare
  - Aetna
  - Mutual of Omaha
  - WTOP
  - Medicare.gov, for the nursing-home queries
  - For the Illinois query: Caring.com, Nolo and Illinois Legal Aid Online, plus several directories
- **Pages read in full on 28 Nov 2026:**
  - NCOA's "Does Medicare Pay for Assisted Living?" (dated 7 Apr 2026, about 1,400 words)
  - Healthline's "Medicare and Assisted Living: Does Medicare Pay?" (updated 1 Jul 2025, about 900 words)
  - Medicare.gov's "Nursing home care" coverage page
  - AARP's FAQ page refused the request (HTTP 403), so it was not read.
- **Our page as built on main and on the package branch** claude/package-20261125 (pull request #91, not yet merged). The package version is about 2,580 words. It adds the section "Choosing or changing a Medicare plan when a move may be coming" (#93) and carries the #89 accuracy corrections. The title and description have not changed since 23 Oct 2026.

## What the top results do that our page does not

1. **They say what Medicare still pays for while someone lives in assisted living.** Every result read has this section:
   - doctor visits and therapy under Part B
   - prescriptions under Part D
   - durable medical equipment
   - home health visits
   - hospital stays

   Our page explains skilled versus custodial care and skilled nursing facility (SNF) coverage, but never says what is covered while living in assisted living. "Hospice" appears 0 times and "Part D" once (package version). This is the main reading of "medicare assisted living" (46 impressions), "what does medicare cover for assisted living" (7) and "assisted living with medicare" (14).
2. **They answer "how much" with a number in the first lines.** The answer is that Original Medicare pays $0 toward rent, meals and personal care in assisted living. Our short answer says "does not pay", but the dollar figure in our description and first sentence is the $217 SNF coinsurance. That fits the nursing-home queries but not the 208 impressions of cost-worded assisted-living queries, which are our worst-ranked group.
3. **They have question headings that match the searches, and a short FAQ.**
   - NCOA has 3 FAQ questions and Healthline has 3.
   - Their headings include "Does Medicare Part B pay for assisted living?", "How much will Medicare pay for assisted living?" and "Does Medicare pay for assisted living for dementia?"
   - We rank for "does medicare part b pay for assisted living" (9 impressions at 25.7) with no Part B heading.
   - Dementia appears 0 times on our page.
4. **They cover Medicare Advantage extra benefits.** Some plans offer limited non-medical help (meals, transportation, help with daily activities), but none pays room and board. NCOA and Healthline both cover this. Our package version mentions Medicare Advantage only in the new plan-change section, not as an answer to "will my plan pay for assisted living".
5. **They list where the money actually comes from:** Medicaid waivers, VA, long-term care insurance, home equity and, in some results, PACE. Our "So who does pay for assisted living?" section names three sources. It does not link our own live guides on:
   - the Illinois PACE program
   - VA nursing home and respite care
   - the Medicaid long-term care rules
   - the payment navigator (linked only in the related cards)

What our page does better, and must keep:
- the exact 2026 SNF figures from Medicare.gov
- the five conditions
- the Jimmo improvement-standard point
- the "same bed, different stay" explanation
- the Illinois Supportive Living Program
- a review date

None of the national results read gives an Illinois answer. That is our only real edge.

## What this study cannot tell us

- **Authority:** the head terms are led by AARP, NCOA, Medicare.gov and Medicare insurers. On a health-and-money topic, Google weights site authority heavily, and a new site will not displace them on "does medicare cover assisted living" through content alone. The realistic targets are the seven queries already on page 2, the cost-worded group, the Part B, dementia and Medicare Advantage questions, and the Illinois variant.
- **Freshness:** only 7 days of rows exist. The 25 Nov read is the baseline. The first change should be measured against the next two weekly Make reads before a second one is made (the project's kill rule).

## Recommendation (strategy, step 2)

Make one review pull request against main for this page only, after package #91 is merged. The page's dict is changed inside #91 (#89 and #93), so a branch from today's main would conflict with it, and the procedure forbids a second change to an element that is pending. The pull request should contain:

1. **Description and first sentence:** answer the cost question with "$0". For example, the description becomes: "Original Medicare pays $0 toward assisted living rent, meals and personal care. It pays for medical care there and for a qualifying skilled nursing stay ($217 a day for days 21 to 100 in 2026)." Keep the title: it already matches the two biggest query forms, and changing it as well would mix two effects in one measurement.
2. **A new section, "What Medicare still pays for if your parent lives in assisted living":**
   - Part B doctor visits and therapy
   - Part D prescriptions
   - durable medical equipment (link the live DME guide)
   - home health under its homebound rule (link the live home-health guide)
   - hospice
   - hospital stays

   Each item is cited to its Medicare.gov coverage page, with the payer named in the same sentence (Original Medicare; plans differ).
3. **A short "Questions families ask" section** with question headings and one-paragraph answers, each sourced:
   - Does Medicare Part B pay for assisted living?
   - Does a Medicare Advantage plan pay for assisted living?
   - Does Medicare pay for memory care or assisted living for dementia?
   - Does Medicare pay for assisted living in Illinois?

   The last answer is the Illinois answer: the Supportive Living Program, PACE, VA and Medicaid long-term care, each linked to our live guide.
4. **Internal links:** add a link to this page from the live guides whose readers ask the same question and do not already link it. Today 14 built pages link it. Check the PACE, Supportive Living, VA nursing-home and Medicaid long-term care guides. Use the anchor text families search with ("does Medicare pay for assisted living").
5. **Out of scope:** no FAQ schema markup. Google shows FAQ rich results only for a few authoritative government and health sites, so it would not help and adds a test surface. No change to the tour path, the checklist block or the bridge. No new page: every query group above is answered on this page, and a second Medicare page would compete with it.

**Build conditions:** the review rules (scope rule included), an independent reader, all suites passing. The pull request enters the daily package after its check.

**Measure:**
- Make's weekly Search Console reads after the deploy: position and clicks for the 10 queries above, the cost-worded group and the 7 page-2 queries.
- Genuine search visitors to the page, and checklist opens from it.

**Second iteration:** decide from what moved after 6 weeks, per the project's kill rule.
