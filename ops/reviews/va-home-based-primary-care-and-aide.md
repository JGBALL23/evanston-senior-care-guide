# Review packet: va-home-based-primary-care-and-aide

- Date: 2026-11-25
- Reviewer: ESCG worker, session cse_014eaiSarrUfj6PScmQNGxys (task ACQ-062, key rereview:va-home-based-primary-care-and-aide)
- Draft reviewed: drafts cf6aaf8 (as corrected by 7defb27 on 2026-11-23, C1–C13 of the earlier packet, which had no scope table or counts line)
- Rules: procedure v4.3.2 review rules
- Quotation checker: 13 quotations, 13 FOUND, 0 NEAR MATCH, 0 NOT FOUND; 2 short terms found; 6 cited pages, 0 unreadable.

## Sources (fetched 2026-11-25)

1. VA.gov Geriatrics, Home Based Primary Care. Eligibility: "all enrolled Veterans are eligible IF they meet the clinical need for the service and it is available."
2. VA.gov Geriatrics, Homemaker and Home Health Aide Care. Eligibility: "All enrolled Veterans are eligible … If they are eligible for community care and meet the clinical criteria for the service and it is available."
3. VA.gov Geriatrics, VA Long Term Care Services ("Services at Home and in the Community").
4. VHA Notice 2024-01, Purchased Home and Community-Based Services Programs (linked from Src 2 as "Purchased Home & Community Based Services Programs Notice").
5. VA.gov Geriatrics, Veteran Directed Care.
6. VA.gov, "How are the 2 VA caregiver support programs different?"

## Scope table

| # | Guide's claim | Guide's scope | Source's scope (heading / context) | Result |
|---|---|---|---|---|
| 1 | Answer: both need enrollment, clinical need or criteria, availability; aide adds community care eligibility | enrolled veterans | Src 1 and Src 2 "Am I eligible…" | same |
| 2 | Overview lists five services at home, for "all enrolled Veterans" with clinical need and local availability; HBPC not listed | enrolled veterans | Src 3 | same; the guide then reports the aide page's extra condition instead of flattening it |
| 3 | HBPC: care at home for ongoing diseases; homebound not required; isolated or caregiver burden | veterans | Src 1 "What is Home Based Primary Care?" | same |
| 4 | HBPC team and services (physician/NP/PA visits, care management, social work, rehab, psychology, nutrition, pharmacy) | veterans | Src 1 "What services can I get?" | same |
| 5 | HBPC copay per medical visit, "the same as if you went to a VA clinic", by service-connected status and financial information; 10-10EC via social worker | veterans | Src 1 | same |
| 6 | Aide: not a nurse, RN-supervised; any age; isolated or caregiver burden; listed daily activities; several times a week or occasionally; as long as needed | veterans | Src 2 | same |
| 7 | Aide copay by service-connected disability status; aide works for a VA-contracted organisation | veterans | Src 2 | same |
| 8 | "eligible for community care" explained by VHA Notice 2024-01 (PHCBS; MISSION Act criteria) | H/HHA recipients | Src 4 | same |
| 9 | Availability varies; social worker or physician confirms locally | veterans | Src 1 ("Your VA physician or social worker can tell you if … available in your area"); Src 2 ("Services may vary by location") | same |
| 10 | Veteran Directed Care: budget, hire own worker, including a family member | VDC participants | Src 5 ("hiring workers (which might include their own family member or neighbor)") | same |
| 11 | PCAFC "pays an eligible family caregiver a monthly stipend" | any eligible family caregiver | Src 6: "Eligible primary family caregivers may also receive … A monthly stipend" | SCOPE DEFECT (person): only primary family caregivers. Corrected (C1). |
| 12 | Both pages: "can be used in combination with other Home and Community Based Services" | veterans | Src 1 and Src 2 | same |
| 13 | Neither page gives a dollar copay, a visit frequency or maximum aide hours | n/a | Src 1, Src 2 | holds |
| 14 | First step: VA social worker or case manager; Decision Aid and Caregiver Self-Assessment | veterans | Src 1, Src 2 | same |

Links: assisted-living-cost-illinois, does-medicare-pay-for-senior-care, illinois-supportive-living-program, va-aid-and-attendance-benefit, va-caregiver-support-program, va-nursing-home-and-respite-care, va-veteran-directed-care-program are live on main. Advice: talk to the VA social worker, confirm enrollment and community care eligibility; right for a veteran's family. No community ranking, no Westminster Place claim. Note: the "to a family member" stipend wording seen in va-caregiver-support-program is only in the drafts branch's older copy; main already says "primary family caregiver" (confirmed by audit ACQ-069, ops/reviews/live/va-caregiver-support-program.md).

## Required corrections

C1. "Not Veteran Directed Care…" section. Was: "pays an eligible family caregiver a monthly stipend." Now: "pays an eligible primary family caregiver a monthly stipend." Source sentence (Src 6): "Eligible primary family caregivers may also receive these benefits: A monthly stipend (payment)."

Corrections applied: drafts 38ba709, 2026-11-25, cse_014eaiSarrUfj6PScmQNGxys (build 42 URLs; test.js 669/669 passed; check-guides 2570 passed, 0 failed; citations all 103 resolve; mobile-nav skipped, websockets not installed; quotecheck 13/13 found). Verification queued for a later session: verify:va-home-based-primary-care-and-aide:38ba709.

Quotations checked: 13. Claims scope-checked: 14. Scope defects: 1. Corrections required: 1.

Verdict: publish-ready after corrections (one word restoring the primary-caregiver limit; packaging waits for "Corrections verified")
