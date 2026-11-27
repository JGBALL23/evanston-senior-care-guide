# Accuracy audit: assisted-living-cost-illinois (live on main 4dc2468)

Audited 2026-11-27 by the ESCG worker, session cse_014eaiSaU9VKyTkRhekq5VFJ (task ACQ-188). The worker did not build this page.
Quotation checker on main: 0 quotations, 6 short terms (2 not found: "Evanston area", a listing site's own label, dated observation of 4 Nov 2026; "no longer improving", a Related-guides card of another guide, not a claim of this page), 10 cited pages, 4 unreadable.
Unreadable from this environment: the four ilga.gov pages (210 ILCS 9/15, Public Act 104-0589, 210 ILCS 9/85, 210 ILCS 9/90). WebFetch returned HTTP 503 on 27 Nov 2026; a direct fetch was refused by a permission check and not retried. Claims cited only to those pages are listed as NOT CHECKED, not as holding.

| # | Guide's claim | Guide's scope | Source and its scope (heading) | Result |
|---|---|---|---|---|
| 1 | Illinois assisted living median $6,219 a month | Illinois, statewide, private pay, assisted living | CareScout 2025 Cost of Care Survey PDF, table "Assisted Living Community": Illinois $74,628 annual, $6,219 monthly, $204 daily; "Cost of Care Survey, July through November 2025" | same |
| 2 | Illinois nursing home median $8,304 semi-private, $9,216 private | Illinois, statewide, nursing home | same PDF, tables "Nursing Home - Semi-Private Room" ($99,645 / $8,304) and "Nursing Home - Private Room" ($110,595 / $9,216) | same |
| 3 | Survey rate is for a private one-bedroom; rates collected July to November 2025; midpoint used where a range was quoted | assisted living survey method | Methodology PDF, "Assisted Living Communities (ALC)": "monthly private pay rates as they ranged from basic care to more substantial care for a one-bedroom unit"; "Where a rate range was provided, the average of the high and low was used"; survey "by phone or online between July and November" | same |
| 4 | CareScout noted separately whether a community charges a non-refundable community or entrance fee | survey method | Methodology, same heading: "Surveyors also determined whether the facility charges a non-refundable community or entrance fee." | same |
| 5 | Regional figures follow metropolitan areas; none covers Evanston alone; no separate Evanston median | Evanston | Methodology regions list Illinois areas by metropolitan area ("Chicago, Naperville, Elgin" etc.); no Evanston row | same |
| 6 | No Illinois median published for independent living | Illinois | Survey PDF tables: no independent living table | same |
| 7 | Trulee Evanston one-bedroom assisted living "starting at" $9,475 a month (read 12 Nov 2026) | one community, advertised | truleeevanston.com/floor-plans/, Assisted Living, 1 Bedroom: "Prices starting at $9,475" (read 27 Nov 2026) | same |
| 8 | Trulee "all-inclusive" care program $1,850 a month, does not include rent; combined $11,325 | one community, advertised | truleeevanston.com/your-choice/: "For just $1,850* per month, our all-inclusive Your Choice program"; footnote "does not include monthly rental rate" (read 27 Nov 2026). The page also offers a $2,000 lifetime-rate option for the same services; not a defect | same |
| 9 | IDPH licenses assisted living and publishes a list of assisted living and shared housing establishments | Illinois | IDPH Assisted Living page: "responsible for all state licensure and survey processes for Assisted Living and Shared Housing establishments"; "View the list of Assisted Living and Shared Housing establishments" | same |
| 10 | Supportive Living Program is an Illinois Medicaid programme paying for care in assisted-living-style settings; not every community participates | Illinois Medicaid | HFS SLP Resident Fact Sheet, "What": "Affordable assisted living model administered by ... HFS"; "Who Can be a SLP Provider": open to providers meeting application criteria and certified | same |
| 11 | Comprehensive assessment before move-in, repeated at least yearly and after a significant change; service plan a basis for the contract | Illinois licensed assisted living | 210 ILCS 9/15 and PA 104-0589 on ilga.gov | NOT CHECKED (source unreadable) |
| 12 | Contract must state base rate, extra services and fees, community fee and refundability; complete copy to resident or representative | Illinois licensed assisted living | 210 ILCS 9/85, 9/90 on ilga.gov | NOT CHECKED (source unreadable) |
| 13 | "Every figure on this page was read from the source listed above on 4 November 2026." | the whole page | The page itself dates the Trulee figures "On 12 November 2026" and its two Trulee source lines say "read 12 November 2026" | DEFECT (date) |

## Required corrections

C1. Sources footer: the sentence says every figure was read on 4 November 2026, but the Trulee Evanston figures were read on 12 November 2026 (the page's own "One Evanston example" paragraph and its source lines). Corrected sentence: "Every figure on this page was read from the source listed above on 4 November 2026, except Trulee Evanston's advertised prices, read on 12 November 2026. Figures change; the review date tells you how fresh this page is." (build-guides.py: add "figures_except" to this guide's dict; the key already exists for this purpose.)

## Recommended additions

None.

Quotations checked: 0. Claims scope-checked: 13. Scope defects: 0. Corrections required: 1.
Claims not checked (ilga.gov unreadable): 2 (rows 11, 12); a later session or the supervising chat with a reader for ilga.gov should check them.
Verdict: corrections listed (C1)

Corrections applied: claude/accuracy-20261125 166f2d1 (PR #89), 2026-11-27, cse_014eaiSaU9VKyTkRhekq5VFJ. Tests changed: check-guides.js footnote-exception assertion re-pinned to exactly two guides; one new check pins the corrected sentence. Reviewed date unchanged.
