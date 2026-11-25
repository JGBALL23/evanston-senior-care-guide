# Accuracy audit: va-veteran-directed-care-program (live on main)

Audited 2026-11-25 by the ESCG worker (cse_014eaiSbgoXSGhv7gxJtBvna), task ACQ-079, in a clone of main. Quotation checker run first (10 FOUND, 1 NEAR MATCH, 0 NOT FOUND; 4 cited pages, all readable), then the review rules including the scope rule, against each source as it read on 2026-11-25.

Sources: Src 1 VA.gov Veteran Directed Care (www.va.gov/geriatrics/pages/veteran-directed_care.asp). Src 2 VA.gov Eligibility for community care outside VA (www.va.gov/resources/eligibility-for-community-care-outside-va/). Src 3 VA.gov How to apply for VA health care (www.va.gov/health-care/how-to-apply/). Src 4 VA.gov Aid and Attendance and Housebound (www.va.gov/pension/aid-attendance-housebound/).

| # | Guide's claim | Guide's scope | Source's scope (heading) | Result |
|---|---|---|---|---|
| 1 | VDC gives "Veterans of all ages the opportunity to receive the Home and Community Based Services they need in a consumer-directed way." | veterans generally | Src 1, "What is Veteran Directed Care?" | same |
| 2 | Same quotation split in two in the first section | same | same | same |
| 3 | Workers may include "their own family member or neighbor" | VDC participants | Src 1, "What services can I get?" | same |
| 4 | List of daily activities; aimed at veterans needing personal care, isolated, or caregiver under strain | VDC | Src 1, "What is..." and "What services..." | same (paraphrase of "caregiver is experiencing burden") |
| 5 | "All enrolled Veterans are eligible ... if they are eligible for community care," "meet the clinical criteria for the service, and it is available"; services vary by location | enrolled veterans | Src 1, "Am I eligible...?" | same |
| 6 | Community care: two basic requirements, quoted | community care | Src 2, "Eligibility requirements" | same |
| 7 | "plus at least one of several further conditions, such as needing a service VA does not provide at any facility or living somewhere without a full-service VA facility nearby" | any veteran; distance | Src 2: "You live in a state or territory that doesn't have a full-service VA health facility" (state level); separate drive/wait-time standard | SCOPE DEFECT (C2) |
| 8 | Guide cannot confirm community-care rules apply to VDC exactly; ask a social worker | could-not-find | Src 1 has no cross-link | same (still true) |
| 9 | Aid and Attendance is an increased rate added to the pension; no VA.gov page found on drawing both | A&A | Src 4: "monthly payments added to the amount of a monthly VA pension" | same |
| 10 | Decision Aid quotation | VDC | Src 1, "How do I decide...?" | same |
| 11 | "If Veteran Directed Care seems right for you, ..." | VDC | Src 1 reads "Veteran-Directed Care" | NEAR MATCH: wording correction (C1) |
| 12 | "VA.gov lists four ways to apply for VA health care: online, by phone, by mail, in person" | VA health care | Src 3, "How do I apply?": "You can apply online right now. You can also apply in any of these 4 ways": phone, mail, in person, with the help of a trained professional | figure wrong (C3) |
| 13 | Phone 877-222-8387, Mon-Fri 8:00 a.m. to 8:00 p.m. ET; Health Eligibility Center, PO Box 5207, Janesville, WI 53547-5207; in person with signed 10-10EZ | VA health care | Src 3, Options 1-3 | same |
| 14 | No published national VDC budget figure; assessment-based | VDC | Src 1: "Services are based on your assessed needs" | same (could-not-find still true) |
| 15 | Illinois's own in-home programme funded through Medicaid rather than VA | CCP | ops/reviews/live/illinois-community-care-program.md (HFS Persons who are Elderly waiver = the Medicaid waiver component of CCP) | same |

Links: /guides/va-aid-and-attendance-benefit/, /guides/illinois-community-care-program/ and / are all on main.

## Required corrections

C1 (wording). "How to start": the quotation becomes "If Veteran-Directed Care seems right for you, talk with your VA social worker and find out if it is available". Source (Src 1): "If Veteran-Directed Care seems right for you, talk with your VA social worker and find out if it is available in your location."

C2 (scope). "Who qualifies": "living somewhere without a full-service VA facility nearby" becomes "living in a state or territory that has no full-service VA health facility at all, or VA being unable to provide the care within its own standards for drive and wait times. Living some distance from a VA facility is not, by itself, one of the conditions." Source (Src 2): "You live in a state or territory that doesn't have a full-service VA health facility, or ... We can't provide the care you need within our standards for drive and wait times". An Illinois reader is in a state with full-service VA facilities, so the old wording pointed them at a condition that does not apply.

C3 (figure). "How to start": online plus four other ways, adding "with the help of an accredited attorney, claims agent or Veterans Service Organization representative". Source (Src 3): "You can apply online right now. You can also apply in any of these 4 ways ... Option 4: With the help of a trained professional. You can work with an accredited attorney, claims agent, or Veterans Service Organization (VSO) representative".

Quotations checked: 11. Claims scope-checked: 15. Scope defects: 1. Corrections required: 3.

Verdict: corrections listed above (one quotation hyphen, one community-care condition overstated, one count of ways to apply; no wrong deadline, dollar figure or phone number).

Corrections applied: branch claude/accuracy-20261125 (PR #89), commit 3cd72d7, 2026-11-25, cse_014eaiSbgoXSGhv7gxJtBvna (build 36 URLs; test.js 768/768; check-guides 2696/0; quotecheck 11/11 found; va.gov citations 200; reviewed 2026-11-25 with listed 2026-10-27; test-merged with #90 in both orders: clean, rebuild empty, tests pass). Verification queued for a later session.

Corrections verified: 2026-11-25, main chat for Joseph (second reader, not the session that wrote them): commit 3cd72d7 read. VA.gov's community care page gives the condition as "We don't have a full-service VA health facility in your state or territory" (its example names Alaska, Hawaii, New Hampshire and the territories) and a separate "Drive and wait time standards" example, so the corrected sentence states VA's conditions and no longer lets distance alone count. VA.gov's how-to-apply page reads "You can also apply in any of these 4 ways" with "Option 4: With the help of a trained professional" (accredited attorney, claims agent or VSO representative); phone 877-222-8387 and the Janesville address are on the page. The quotation carries VA's hyphen. On the branch at 3cd72d7: rebuild leaves git status empty; test.js 768/768; check-guides.js 2696 passed, 0 failed; quotecheck 11/11 found; sitemap.xml differs from main only in the lastmod of the five corrected guides; _dist/guides/index.html unchanged from main. Every commit in #89 is verified.
