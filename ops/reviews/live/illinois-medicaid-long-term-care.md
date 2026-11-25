# Accuracy audit: illinois-medicaid-long-term-care (live)

- Page: main 4dc2468, /guides/illinois-medicaid-long-term-care/ (last reviewed 23 Oct 2026). Audited 2026-11-25, session cse_014eaiSaeYoez1bK3E9MFwz4, task ACQ-074.
- Rules: procedure v4.3.2 review rules (wording, scope, figures, could-not-find sentences, links, advice).
- Quotation checker: `quotecheck.py --site /tmp/main --slug illinois-medicaid-long-term-care`: 3 quotations, 3 FOUND; 5 cited pages, 0 unreadable. (The heading term "spend-down" is the guide's own spelling, not a quotation.)

## Sources (fetched 2026-11-25)

1. HFS, Long Term Care (for clients), hfs.illinois.gov/medicalclients/ltc. Scope: payment for nursing home services by the State of Illinois.
2. HFS, Long Term Care provider programs. Scope: categories of LTC service reimbursed "to Medicaid-eligible residents".
3. HFS 591SP, Spenddown brochure. Scope: people with too much income or assets "to qualify for other HFS Medical Programs"; Pay-in Spenddown only for "Persons enrolled in spenddown who are aged, blind or have a disability, and live in the community".
4. HFS Provider Notice 22 Jan 2026, Prevention of Spousal Impoverishment Standards for 2026. Scope: LTC facility residents with a community spouse, effective 1 Jan 2026.
5. HFS, Persons who are Elderly waiver.
6. (Not cited by the page; found during the could-not-find check) HFS Provider Notice 25 Jan 2024, "Personal Needs Allowance (PNA) Increase in Skilled Nursing Facilities Effective January 1, 2024".

## Scope table

| # | Guide's claim | Guide's scope | Source's scope (heading / context) | Result |
|---|---|---|---|---|
| 1 | "payment for long-term nursing home services may be available from the state of Illinois"; apply through DHS and get a needs screening (DoA or DHS) | nursing home care paid by Illinois | Src 1, "Long Term Care" | same |
| 2 | Five reimbursed LTC categories (SNF, ICF, ICF/DD incl. SLC, pediatric skilled nursing, SLF) | Medicaid-eligible residents | Src 2 | same |
| 3 | Spenddown "a little like an insurance deductible"; monthly amount based on income and assets | people over the income or asset limit | Src 3, "What is the Spenddown Program?" | same |
| 4 | Spenddown met by showing a DHS caseworker unpaid medical bills | spenddown enrollees | Src 3, "How do I meet spenddown using medical expenses?" (bills or receipts) | same |
| 5 | Pay-in spenddown for people who are aged, blind or have a disability and live in the community | as source | Src 3, "How do I sign up for Pay-in Spenddown?" | same |
| 6 | "the monthly spend-down amount for someone in a facility is often met immediately by the facility's own bill. Spenddown is frequently the route by which a long nursing home stay ends up Medicaid-covered" | nursing home residents generally | Src 3 says only that bills for "Nursing home services" count toward spenddown; no source on the page says how often, or that spenddown is the usual route for a facility resident | UNSUPPORTED GENERALISATION (consequential: how a family expects a nursing home stay to be paid). Correction C1. |
| 7 | CSRA standard $143,172; maximum, actual = standard minus community spouse's nonexempt resources | couples, 2026 | Src 4 | same |
| 8 | CSMNA standard $4,066.50 a month; actual = standard minus community spouse's gross income | couples, 2026 | Src 4 | same |
| 9 | "Both standards change every year ... check the current HFS notice" | every couple | Src 4: "The CSRA determination only occurs once. If the CSRA was already determined at application or long term care determination, then the previously determined amount will not be updated." | SCOPE DEFECT (advice): the annual-change advice is right for a new application but not for a couple whose CSRA is already determined. Correction C2. |
| 10 | Personal needs allowance: "could not read a verifiable number off that document ... this guide leaves it out" | Medicaid nursing facility residents | Src 6: PNA increased "from $30 per month to $60 per month for nursing home residents who reside in a nursing facility licensed under the Nursing Home Care Act and who are determined to be eligible for Medical Assistance", effective 1 Jan 2024 | COULD-NOT-FIND SENTENCE CONTRADICTED by an official source. Correction C3. |

Links: does-medicare-pay-for-senior-care, assisted-living-cost-illinois, levels-of-senior-care-explained, illinois-supportive-living-program, illinois-medicaid-estate-recovery, illinois-nursing-home-preadmission-screening all live on main. Advice otherwise right for an Illinois family: caseworker decides, no subtraction done for the reader. No community ranking, no Westminster Place claim or price.

## Required corrections

C1. "What spend-down actually means", third paragraph. Was: "This is the detail families miss: nursing home care is expensive enough that the monthly spend-down amount for someone in a facility is often met immediately by the facility's own bill. Spenddown is frequently the route by which a long nursing home stay ends up Medicaid-covered even when the same person would not have qualified for Medicaid the month before they were admitted." Now: "HFS lists bills for nursing home services among the medical expenses that count toward spenddown. How spenddown and your parent's own income apply to a nursing home stay is worked out by the DHS caseworker; ask before assuming the facility's bill settles it." Source sentence (Src 3): "These include bills or receipts for: Doctor services; Hospital services; Nursing home services; ..."

C2. "Protecting a spouse who stays at home", last paragraph. Add after "...ask the DHS caseworker handling the case.": "One exception, in HFS's words: 'The CSRA determination only occurs once.' If it was already determined at application, the amount is not updated when the standard rises." Source sentence (Src 4): "The CSRA determination only occurs once. If the CSRA was already determined at application or long term care determination, then the previously determined amount will not be updated."

C3. "A figure this guide will not publish". Replace the section with a sourced figure, heading "The personal needs allowance": "Illinois protects a small part of a Medicaid nursing home resident's income for personal spending. An HFS notice of 25 January 2024 states that, effective 1 January 2024, the Personal Needs Allowance increased 'from $30 per month to $60 per month for nursing home residents who reside in a nursing facility licensed under the Nursing Home Care Act and who are determined to be eligible for Medical Assistance.' Ask the facility's business office or the DHS caseworker whether a later change applies." Add the notice to the page's sources. Source: Src 6, quoted above.

Quotations checked: 3. Claims scope-checked: 10. Scope defects: 3. Corrections required: 3.

Verdict: corrections required (C1 removes an unsupported claim about how nursing home stays get paid; C2 limits the annual-change advice; C3 replaces a could-not-find paragraph contradicted by HFS's own notice). Corrections go to the rolling accuracy pull request.

Corrections applied: C1 and C2 in branch claude/accuracy-20261125 (PR #89), 2026-11-25, cse_014eaiSaeYoez1bK3E9MFwz4 (build 36 URLs; test.js 768/768; check-guides 2696/0; quotecheck 4/4 found). C3 NOT applied: check-guides.js line 1029 asserts "the personal needs allowance is still refused", an owner gate; changing it is Joseph's decision (owner_review_needed).

Corrections verified (C1, C2): 2026-11-25, main chat for Joseph (second reader): commit d396ad4 read; HFS 591SP lists 'Nursing home services' among the bills that count toward spenddown; HFS's notice of 22 January 2026 reads 'The CSRA determination only occurs once' and gives $143,172 and $4,066.50.

C3 applied: branch claude/accuracy-20261125 (PR #89), commit d4bed8b, 2026-11-25, main chat for Joseph. The paragraph quotes HFS's provider notice of 25 January 2024 with its scope, the notice is in the sources, the review date is 2026-11-25, and two assertions in check-guides.js were re-pinned (the allowance one now requires the notice's words, scope, link and the ask-about-later-changes advice; the date one now pins 25 November 2026). Both are listed at the top of #89 for Joseph. Library date kept by 50fa120 ("listed": 2026-10-23). build 36 URLs; test.js 768/768; check-guides 2696/0; quotecheck 5/5 found. Verification queued for the worker: ACQ-078.
