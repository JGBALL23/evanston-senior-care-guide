# Accuracy audit: illinois-care-facility-complaint (live on main)

Audited 2026-11-25 by the ESCG worker (ACQ-085, session cse_014eaiSeZV5K4aUnZndensii) in a clone of main (reviewed date on main: 2026-10-23). Why now: the only search-referred visit of 24-25 Nov (Google, 03:00Z) landed on this guide.

Sources read today: Src 1 IDoA Long-Term Care Ombudsman Program (ilaging.illinois.gov/programs/ltcombudsman.html); Src 2 IDoA Office of the State LTC Ombudsman contact page; Src 3 IDPH File a Health Care Complaint (dph.illinois.gov/.../complaints.html); Src 4 IDPH Health Care Facility Complaint Form (healthcarefacilitycomplaintform20210625.pdf, linked from Src 3); Src 5 IDPH Who Regulates Nursing Homes? (read for context); APS page (cited, unchanged claims). Quotation checker on main: 1/1 FOUND, 2 short terms found, 4 cited pages readable.

| # | Guide's claim | Guide's scope | Source's scope (heading) | Result |
|---|---|---|---|---|
| 1 | Ombudsman program is a "resident-directed advocacy program", mandated by the Older Americans Act and the Illinois Act on Aging | Illinois LTC facility residents | Src 1, intro | same |
| 2 | Ombudsman work is directed by the resident; information not disclosed without permission; free; who may contact | same | Src 1, How the program works / Services | same |
| 3 | Contact: Senior HelpLine 1-800-252-8966 (711 TRS), Aging.SLTCOProgram@illinois.gov | same | Src 1, How to contact an Ombudsman | same |
| 4 | CCR hotline 800-252-4343, Mon-Fri 8:30 a.m.-4:30 p.m. | IDPH complaints | Src 3, Ways to File a Complaint | same (but Src 4 says 24/7: see C2) |
| 5 | "for a long-term care complaint specifically, that same number reaches the department's Bureau of Long-Term Care" | filing a complaint | Src 3 FAQ "Who should I contact to check the status of my complaint?": "To check the status of a long-term care complaint, contact the Department's Bureau of Long-Term Care at 800-252-4343." | SCOPE DEFECT (status check, not filing): C1 |
| 6 | Three other ways to file from the complaints page: OHCR Portal, fax, e-mail with the complaint form; mail address | care facility (nursing home, assisted living) | Src 3: "Complaints submitted to this site are limited to hospitals, home health agencies, hospices, ... and health maintenance organizations (HMOs)" (no nursing homes or assisted living); Src 4 form: covers "nursing homes, skilled nursing homes, licensed facilities for individuals with intellectual disability, and assisted living facilities" | SCOPE DEFECT (the page's own online-filing scope excludes the guide's readers; the form includes them): C2 |
| 7 | Identity not disclosed to the facility; anonymous filing; contact details needed for written outcome | IDPH complaints | Src 3 FAQ | same |
| 8 | who/what/when/where/how | IDPH complaints | Src 3 FAQ | same |
| 9 | "Report Abuse: 1-866-800-1409" link on the Ombudsman page; APS hotline; APS covers adults in the community | community | Src 1 header; APS page | same |
| 10 | 911 first in an emergency | all | advice, no source claim | same; Src 4 adds its own urgent-risk line (folded into C2) |

Links: illinois-elder-abuse-reporting, check-illinois-inspection-records, / are live on main. Advice: the two-channel advice holds; after C1-C2 a family is pointed to the routes IDPH says cover nursing homes and assisted living.

## Required corrections

C1. Was: "The same page states that for a long-term care complaint specifically, that same number reaches the department's Bureau of Long-Term Care." Now: "The same page gives that number, for the department's Bureau of Long-Term Care, as the one to call to check the status of a long-term care complaint." Source (Src 3, FAQ): "To check the status of a long-term care complaint, contact the Department's Bureau of Long-Term Care at 800-252-4343."

C2. Was: "Besides the phone line, the page lists three other ways to file: online through the OHCR Portal, by fax at 217-524-8885, or by e-mail to DPH.CCR@illinois.gov using the Health Care Facilities Complaint Form. Written complaints can also go by mail to ..." Now: the written route is the IDPH Health Care Facility Complaint Form (Src 4, linked from Src 3), quoted for its coverage of "nursing homes, skilled nursing homes, licensed facilities for individuals with intellectual disability, and assisted living facilities", with its fax, e-mail and mail routes; a sentence that the complaints page's own list for complaints submitted through the site does not name nursing homes or assisted living, so use the phone line or the form; and a short paragraph that the form gives the hotline as "Available 24 hours a day - 7 days per week" while the page gives weekday hours, its line "If a resident's immediate health and/or safety are at risk please call 800-252-4343 to speak with an IDPH representative.", and that forms sent after 4:30 p.m. are not seen until the next business day. Sources: Src 3 "Complaints submitted to this site are limited to hospitals, home health agencies, hospices, end-stage renal dialysis units, ..., alternative health care delivery and health maintenance organizations (HMOs)"; Src 4 "Complaints submitted on this form are limited to occurrences in hospitals, ... nursing homes, skilled nursing homes, licensed facilities for individuals with intellectual disability, and assisted living facilities." and "Emails, facsimiles, and mailed complaint forms that are sent/received after 4:30p.m. will not be seen until next business day." The two IDPH documents disagree on hours; both are stated, neither is chosen.

Quotations checked: 4. Claims scope-checked: 10. Scope defects: 2. Corrections required: 2.

Corrections applied: claude/accuracy-20261125 (PR #89) commit 1cc1b98, 2026-11-25, cse_014eaiSeZV5K4aUnZndensii (reviewed 2026-11-25, listed 2026-10-23 kept; /guides/ index unchanged vs main; sitemap differs from main only in lastmod of corrected guides). Checks: test.js 768/768; check-guides 2696/0; test_paying_nav 331/331; direct_inquiry_consistency 29/29; test_*.mjs and test_*.py pass; citations 15 dead, all ilga.gov (unreachable here) or truleeevanston.com 403, none in this guide; quotecheck 4/4 FOUND. Verification queued for a later session.

## Recommended additions

A1. Supportive living facilities (found 25 Nov in a search-results check: other pages that rank for this question give a separate complaint line for supportive living). The guide covers nursing homes and assisted living but not Supportive Living Program facilities, which HFS runs. Source (HFS Supportive Living Program Resident Fact Sheet, already a source on main): "Complaints concerning a Supportive Living Program provider may be directed to the SLP complaint hotline: 1-844-528-8444". Scope: SLP providers only. Applied as a short section with a link to the live illinois-supportive-living-program guide: PR #89 commit 5bf3b46 (only this page changes; test.js 768/768; check-guides 2696/0; all tools suites pass; quotecheck 5/5).

Verdict: corrections required (2 scope defects; C1 and C2 applied in PR #89, awaiting verification)
