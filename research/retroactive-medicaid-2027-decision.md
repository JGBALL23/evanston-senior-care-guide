# 2027 retroactive Medicaid change: page or no page?

Project PJ04, step 1 (investigate) and its decision. ESCG worker, 28 Nov 2026, session cse_014eaiSeLUyuyJkYCTLw4xJi.

## Evidence (read 28 Nov 2026)

- **The rule.** Illinois HFS, "How will Federal changes impact Medicaid?" (hfs.illinois.gov/info/fedresctr/faqshowwillfedchimpactmedicaid.html) says "Beginning January 2027, Medicaid will only provide two months of retroactive coverage" and "retroactive coverage will be decreased from 3 months to 2 months for all Illinois Medicaid customers". The page shows no update date.
- **Live guides on main (4dc2468).** No live guide states how many months of retroactive coverage apply.
  - The word "retroactive" appears once, in the estate-recovery guide's lien section, about Public Act 102-1037, which is unrelated.
  - The live Medicaid long-term care guide and the look-back guide say nothing about when coverage starts after an application.
  - So no live page carries a wrong figure, and no live correction is needed.
- **Drafts and the batch.** The guide illinois-medicaid-pending-nursing-home already gives both rules: the HFS 3191 three-month rule for applications before 2027, and HFS's two-month rule from 1 January 2027.
  - It was corrected on drafts (dad7c20) and verified by an independent reader (ACQ-199).
  - It was ported into publish batch #90 as 4815ca1, which is newer than package #91's cut. It reaches the site through the next package.
- **Search demand.** The Make Search Console read of 25 Nov 2026 has no query about retroactive Medicaid, backdating, or when Medicaid coverage starts. The site's Medicaid queries are "qmb medicaid" (4 impressions) and the Medicare-cluster queries.

## Decision

- **No dedicated page.** There are no searches for it, and the existing page answers it in full, sourced. A second page would split the same answer.
- **The asset is illinois-medicaid-pending-nursing-home.** It serves as angle A of the local press plan (research/local-press-pitch-plan.md), pitched once it is live.
- **One live-page improvement, after that page is live.** In illinois-medicaid-long-term-care, the live guide families read when they start an application, add one sourced sentence and a link:
  - "Apply as soon as the need is clear: from 1 January 2027, Illinois Medicaid covers at most two months before the month of application" (HFS quotation as above).
  - The link goes to the pending guide.
  - This is a small review pull request against main. It waits for the pending guide to be live, because links go only to live guides.
- **Watch** for HFS provider notices or a revised HFS 3191 brochure that change the rule's wording before 1 January 2027. A searched query about it in a Make read reopens the page question.
