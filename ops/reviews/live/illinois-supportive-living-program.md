# Accuracy audit: illinois-supportive-living-program (live, main 4dc2468)

Audited 2026-11-26 by the ESCG worker (ACQ-133, cse_014eaiSf2v59RahpHN2G6JvZ). Sources read today (all 200): HFS SLP Resident Fact Sheet, HFS Provider Notice 21 Nov 2025 (prn251126a, room and board for 2026), HFS HCBS waivers page, HFS Supportive Living reimbursement page, HFS Cook County SLP sites, IDPH Dementia Capability in Illinois 2025 (PDF). Search Console read 25 Nov: 12 impressions, position 8.0.

quotecheck: 2 quotations, 2 FOUND, 0 unreadable; one "final punctuation" note is a comma where the guide's sentence continues.

| Guide's claim | Guide's scope | Source's scope (heading) | Result |
|---|---|---|---|
| Medicaid pays the cost of services in an approved SLF; resident pays room and board and a group care credit; keeps $120 PNA | Medicaid SLP resident | Fact sheet, "Resident's Cost of Care Liability" and "Rates" ("must contribute all but $120 (PNA)") | same |
| Room and board $874 single, $625.50 double, effective 1 January 2026 | all SLP residents, 2026 | Provider notice 21 Nov 2025 "Room and Board Amounts for 2026" | same |
| Adjusted each year with the Social Security increase | statewide | Notice: "based on the 2026 Social Security Income (SSI) increases"; fact sheet: "based on the annual Supplemental Security Income (SSI)" | same |
| Group care credit = countable income minus health insurance premiums, medical expenses, room and board, PNA; Medicaid pays the rest | Medicaid SLP resident | Fact sheet, cost of care liability | same |
| Most residents owe both; no GCC only when income equals SSI | SLP resident | Fact sheet: "The only time a SLP resident will not have a GCC is when their income is equal to the SSI amount." | same |
| "Dementia care setting that serves residents age 65+" | Cook County list | HFS Cook County, Operational SLF | same |
| "the DCS must provide three daily well-being checks and at least three daily scheduled activities,"; twenty DCS, more than 520 apartments | Illinois SLP DCS | IDPH 2025 report | same |
| No SLF in Evanston, Skokie, Wilmette, Niles, Morton Grove, Lincolnwood, Glenview, Park Ridge | Cook County list | Cook County page (0 matches for each town today) | same |
| Six Cook DCS; closest Asbury Court, Des Plaines; others far South Side or south suburbs; North Side sites not DCS | Cook County list | Cook page: Des Plaines, Tinley Park, Crestwood, Chicago Heights, 10450 S Michigan (Chicago), Hazel Crest | same |
| Bureau of Long-Term Care 217-782-0545, 844-528-8444 | | Fact sheet, Additional Information | same |
| Links: assisted-living-cost-illinois, does-medicare-pay-for-senior-care, illinois-pace-program, estate recovery, look-back | | on main | same |

## Recommended additions (not defects; applied as Improve)

- A1 (a family deciding whether the programme fits). Fact sheet, "What": "Affordable assisted living model administered by the Department of Healthcare and Family Services (HFS) that offers older persons (65 +) or persons with physical disabilities (ages 22-64) services to remain in a community setting." Scope: all SLP residents. The guide never says who the programme serves.
- A2 (a parent with savings). Fact sheet, "Resident's Cost of Care Liability": "Additionally, all excess resources will be counted towards the cost of care." Scope: Medicaid SLP resident. The guide's method counts income only.
- A3 (a parent with low income). Fact sheet, same heading: "The minimum income that a SLP participant can have should be equal to the SSI amount. This is to ensure they can pay for the room and board amount and receive their PNA." Scope: SLP participant. The guide says SSI is where the GCC ends, not that it is the floor.

Applied in PR #89 commit b95d5b2 (only this page changes; test.js 768/768; check-guides 2697/0; all tools suites pass; quotecheck 5/5). Awaiting an independent reader (task verify-live:illinois-supportive-living-program:b95d5b2).

Watch (not a correction): HFS published the 2026 room and board notice on 21 Nov 2025; no 2027 notice was found today. When it appears, the $874 and $625.50 figures and "effective 1 January 2026" need a figure refresh. The fact sheet (DCS rates "127%") and the reimbursement page ("150%") disagree; the guide states neither.

Quotations checked: 2. Claims scope-checked: 11. Scope defects: 0. Corrections required: 0.
Verdict: holds (three recommended additions applied for an independent reader to verify)
