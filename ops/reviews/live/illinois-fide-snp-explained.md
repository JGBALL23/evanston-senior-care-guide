# Accuracy audit: illinois-fide-snp-explained (live, main 4dc2468)

Audited 2026-11-26 by the ESCG worker (ACQ-134, cse_014eaiSf2v59RahpHN2G6JvZ). Sources read today (all 200): HFS MMAI End Date, HFS Fully Integrated Dual Eligible Special Needs Plans in Illinois, HFS How To Enroll in a FIDE SNP, HFS Managed Care (clients). Search Console read 25 Nov: 8 impressions, position 32.4.

quotecheck: 18 quotations, 18 FOUND, 4 short terms found, 0 unreadable; seven "final punctuation" notes, six are commas or periods where the guide's sentence continues or ends; one (quotation 7) closes the quotation with a period where the source continues with the clause about LTSS (C2).

| Guide's claim | Guide's scope | Source's scope (heading) | Result |
|---|---|---|---|
| MMAI ended 31 Dec 2025; CMS requiring conversion to D-SNP; FIDE SNPs the only D-SNP model | Illinois | MMAI End Date page | same |
| FIDE SNP "a type of Medicare Advantage plan", Medicare and Medicaid through one plan; "they provide the same level of care coordination" | Illinois FIDE SNPs | FIDE SNP page | same |
| "Medicaid wraps around Medicare by helping with Medicare premiums and cost sharing." | dual members | FIDE SNP page; the sentence continues ", and by covering some services that Medicare does not cover, such as long-term services and supports (LTSS)." | C2 (wording: the quotation ends where the source does not, dropping the LTSS clause the next section depends on) |
| Aetna, Humana, Meridian, Molina MMAI members auto-enrolled 1 Jan 2026; no action needed; could choose other coverage | those MMAI members | Enrol page, "MMAI Members" | same |
| BCBS no FIDE SNP for 2026; no choice by 31 Dec 2025 -> Original Medicare + drug plan; LTSS -> BCBS HealthChoice IL MLTSS; others FFS; 3 Nov letter "should not have been sent by BCBS." | BCBS MMAI members | Enrol page, BCBS bullets | same |
| Eligibility list (full Medicaid AABD or FamilyCare, 21+, Parts A and B, service area, citizen or lawfully present); exclusions incl. spend-down | FIDE SNP | FIDE SNP page, "Who is eligible" / "Who is not eligible" | same |
| "referred to as the MLTSS population" | dual adults receiving certain LTSS | Managed Care page, HealthChoice Illinois | same |
| Members receiving LTSS "must be enrolled in a HealthChoice IL Managed Long-Term Services and Support (MLTSS) plan"; switch via CEB 1-877-912-8880 | presented for every dually eligible parent in a nursing home or on a waiver | Enrol page, heading "Dual Members Who Do Not Choose a FIDE SNP" > "Medicaid Coverage" > "Members Receiving LTSS Services" | SCOPE DEFECT (C1) |
| Three ways to enrol (Find Plans Now with "Medicaid"; plan; 1-800-MEDICARE, TTY 1-877-486-2048) | FIDE SNP enrolment | Enrol page, "Follow these steps to enroll" | same |
| OEP "October 15 - December 7 of each year,"; coverage 1 Jan if received by 7 Dec | Medicare | Enrol page, Key Medicare Enrollment Events | same |
| Integrated Care SEP once a month, coverage first of next month; Dual/LIS SEP back to Original Medicare + PDP or switch PDPs once a month; "won't allow enrollment into non-D-SNP Medicare Advantage Plans." | dual members, from 1 Jan 2026 | Enrol page, SEPs ("Beginning January 1, 2026 ...") | same |
| No dollar figure for a FIDE SNP on HFS pages | | none of the four pages gives a premium or copay | same |
| Links: illinois-medicaid-long-term-care, illinois-senior-health-insurance-program, illinois-medicare-savings-program, illinois-home-care-ombudsman-program | | on main | same |

## Required corrections

- C1 (scope). The guide presents the MLTSS enrolment rule as the rule for every dually eligible parent receiving LTSS. HFS states it under "Dual Members Who Do Not Choose a FIDE SNP": "Members must be enrolled in a HealthChoice IL Managed Long-Term Services and Support (MLTSS) plan for LTSS services." For a FIDE SNP member, HFS's FIDE SNP page says the plan "provides both Medicare and Medicaid benefits through a single managed care plan" and that Medicaid covers "some services that Medicare does not cover, such as long-term services and supports (LTSS)". Corrected sentence: "If your parent is in a FIDE SNP, those Medicaid services come through that one plan, which HFS says provides both Medicare and Medicaid benefits. For dually eligible members who do not choose a FIDE SNP, HFS's enrolment page says members receiving LTSS "must be enrolled in a HealthChoice IL Managed Long-Term Services and Support (MLTSS) plan" for those services, and adds: "Currently, to switch plans, members must call the HFS Client Enrollment Broker at 1-877-912-8880.""
- C2 (wording). Quote the source sentence through its end: "Medicaid wraps around Medicare by helping with Medicare premiums and cost sharing, and by covering some services that Medicare does not cover, such as long-term services and supports (LTSS)."

Applied in PR #89 commit 004938c (only this page changes; test.js 768/768; check-guides 2697/0; all tools suites pass; quotecheck 18/18). Awaiting an independent reader (task verify-live:illinois-fide-snp-explained:004938c).

Recommended additions: none.

Quotations checked: 18. Claims scope-checked: 13. Scope defects: 1. Corrections required: 2.
Verdict: corrections required (C1 scope of the MLTSS rule, C2 quotation cut short); everything else holds.

## Reader check 2026-11-26

Independent reader, commit 004938c on claude/accuracy-20261125 (build-guides.py and _dist page agree; only this page changed). quotecheck: 18/18 FOUND, 0 NEAR MATCH, 0 NOT FOUND, 0 unreadable; all four HFS pages also fetched by the reader today. No links in the changed sentences.
- "It adds that “Medicaid wraps around Medicare by helping with Medicare premiums and cost sharing, and by covering some services that Medicare does not cover, such as long-term services and supports (LTSS).”" | Source, HFS FIDE SNP page, "What is a FIDE SNP?": "Medicaid wraps around Medicare by helping with Medicare premiums and cost sharing, and by covering some services that Medicare does not cover, such as long-term services and supports (LTSS)." (said of dually eligible members in Illinois) | word for word, full sentence; same scope (C2 fixed).
- "If your parent is in a FIDE SNP, those Medicaid services come through that one plan, which HFS says provides both Medicare and Medicaid benefits." | Source, same page, "What is a FIDE SNP?": "A FIDE SNP ... is a type of Medicare Advantage plan that provides both Medicare and Medicaid benefits through a single managed care plan." with LTSS named as a Medicaid service in the next sentences, and "a contract with HFS to cover Medicaid benefits" | same scope (Illinois FIDE SNP members).
- "For dually eligible members who do not choose a FIDE SNP, HFS’s enrolment page says members receiving LTSS “must be enrolled in a HealthChoice IL Managed Long-Term Services and Support (MLTSS) plan” for those services, and adds: “Currently, to switch plans, members must call the HFS Client Enrollment Broker at 1-877-912-8880.”" | Source, How To Enroll in a FIDE SNP, heading "Dual Members Who Do Not Choose a FIDE SNP" > "Medicaid Coverage" > "Members Receiving LTSS Services": "Members must be enrolled in a HealthChoice IL Managed Long-Term Services and Support (MLTSS) plan for LTSS services. ... Currently, to switch plans, members must call the HFS Client Enrollment Broker at 1-877-912-8880." | same scope; the guide now names the heading's group in the same sentence (C1 fixed).
Corrections verified
Reader: agent in cse_014eaiSf2v59RahpHN2G6JvZ

## Scope check 2026-11-27 (new evidence)

- Reviewer: ESCG worker, session cse_014eaiSeGWreJzfEyfVMTtWN (task ACQ-202); not the builder of this page.
- Trigger: HFS's page on the 2025 federal law (read 27 Nov 2026) states a Medicare eligibility change for noncitizens with a fixed end date.

| # | Guide's claim | Guide's scope | Source's scope with heading | Result |
|---|---|---|---|---|
| A1 | "Who can join a FIDE SNP": conditions include "having Medicare Part A and Part B" and "being a United States citizen or lawfully present in the United States" (HFS FIDE SNP page) | the plan's own enrolment conditions | HFS "How will Federal changes impact Medicaid?", FAQ "Does this new law affect Medicare?": "For new Medicare applicants on or after July 4, 2025, only these noncitizens can be eligible: Lawful permanent residents (Green Card holders), Cubans or Haitians, with a range of current or past statuses, and People from Micronesia, Palau, or the Marshall Islands living in the U.S." and "If you were already enrolled in Medicare as of July 4, 2025, you can keep your coverage until January 4, 2027, when it ends." (federal, noncitizens) | same as quoted, but the guide leaves out that Medicare itself, a condition of the plan, narrows for noncitizens and ends for some on 4 Jan 2027 |

## Recommended additions

R1: after the eligibility paragraph, state HFS's two sentences on Medicare for noncitizens (quoted, with the three groups named), and that a parent lawfully present in another status may lose Medicare, and so a FIDE SNP, on 4 January 2027. Source: HFS federal-changes FAQ (hfs.illinois.gov, allowed host). Scope: federal Medicare rule, noncitizens.

Quotations checked: 2. Claims scope-checked: 1. Scope defects: 0. Corrections required: 0.

Verdict: holds (recommended addition R1)

Corrections applied: R1 on accuracy PR #89 as 3d922fa, 2026-11-27, cse_014eaiSeGWreJzfEyfVMTtWN
