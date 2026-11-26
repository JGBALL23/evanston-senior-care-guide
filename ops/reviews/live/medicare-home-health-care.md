# Accuracy audit: medicare-home-health-care (live, main 4dc2468)

Audited 2026-11-26 by the ESCG worker (ACQ-111, cse_014eaiSdvHByATtNdterRhh7). Sources read today: Medicare.gov Home health services (https://www.medicare.gov/coverage/home-health-services, 200) and Medicare.gov Medicare costs. Search Console read 25 Nov: 44 impressions, position 47.6.

quotecheck: 5 quotations, 5 FOUND; "no longer improving" is a phrase in another guide's sentence, not a quotation here.

| Guide's claim | Guide's scope | Source's scope (heading) | Result |
|---|---|---|---|
| "medically necessary part-time or intermittent skilled nursing care," with examples | Medicare | Coverage details | same |
| Aide care "only if you're also getting skilled nursing care." (quoted with a full stop) | Medicare | Coverage details: "(only if you're also getting skilled nursing care, physical therapy, speech-language pathology services, or occupational therapy at the same time)" | SCOPE DEFECT: the quotation stops mid-sentence and drops the therapies, so it reads as nursing only: C1 |
| Not covered: 24-hour care, meal delivery, homemaker services, custodial care when it is the only care | Medicare | Coverage details | same |
| Homebound: both conditions; leaving for treatment or short infrequent absences; adult day care | Medicare | Who's eligible | same |
| In-person visit and order by a doctor or provider; Medicare-certified agency; OT may continue on its own | Medicare | Provider requirements | same |
| "You pay nothing for covered home health services."; 20% for DME after the Part B deductible ($283 in 2026) | stated for everyone | Costs; Medicare costs page: Part B deductible "$283 ($292 in 2027)". The Costs section adds: "If you get your Medicare benefits through a Medicare Advantage Plan (Part C) or another Medicare health plan, check with your plan for more information about your home health benefits." | SCOPE: the guide never says these are Original Medicare terms and that a plan member checks with the plan: C2 |
| ABN before non-covered services | Medicare | Costs | same |
| Unlimited visits; up to 8 hours a day and 28 a week combined; short-term under 8 a day and up to 35 a week | Medicare | How often | same |
| Links: does-medicare-pay-for-senior-care, medicare-hospice-benefit-explained, illinois-community-care-program, / | | on main | same |

Required corrections
- C1. The aide quotation becomes the source's full condition: "only if you're also getting skilled nursing care, physical therapy, speech-language pathology services, or occupational therapy at the same time". Source (Coverage details), as above.
- C2. Add to "What it costs": "If your parent gets Medicare through a Medicare Advantage plan or another Medicare health plan, Medicare.gov says to check with the plan about its home health benefits." Source (Costs), as above.

Watch: Medicare.gov's page carries a note for home health agencies in Florida, Illinois, Ohio, North Carolina and Texas whose text sits in a collapsed panel this audit could not read; a later audit should open it (Illinois families are directly concerned). The 2027 Part B deductible ($292) is due on 1 January 2027.

Quotations checked: 5. Claims scope-checked: 12. Scope defects: 2. Corrections required: 2.
Verdict: corrections required (C1, C2); figures hold.

Corrections applied: claude/accuracy-20261125 f91038b, 2026-11-26, cse_014eaiSdvHByATtNdterRhh7 (C1, C2; reviewed date unchanged)

## Reader check 2026-11-26

Independent reader, clone of claude/accuracy-20261125 at f91038b (/tmp/reader-medicare-home-health-care). quotecheck: 5 quotations, 5 FOUND, 0 NEAR MATCH, 0 NOT FOUND, 0 unreadable cited pages; Medicare.gov Home health services re-read today (200). The commit adds no links.

- C1, "What the home health benefit actually covers": Home health aide services, part-time or intermittent, in Medicare.gov's words "only if you're also getting skilled nursing care, physical therapy, speech-language pathology services, or occupational therapy at the same time". Source (Coverage details): "Part-time or intermittent home health aide care (only if you're also getting skilled nursing care, physical therapy, speech-language pathology services, or occupational therapy at the same time), like: Help with walking Bathing or grooming ...". FOUND character for character; same scope (Medicare's home health benefit, all four qualifying services now listed); the full stop now sits outside the quotation marks.
- C2, "What it costs": "These are the terms of Original Medicare. If your parent gets Medicare through a Medicare Advantage plan or another Medicare health plan, Medicare.gov says to check with the plan about its home health benefits." Source (Costs): "If you get your Medicare benefits through a Medicare Advantage Plan (Part C) or another Medicare health plan, check with your plan for more information about your home health benefits." Same scope: the cost terms above ($0 for covered services, 20% for equipment after the Part B deductible, the ABN) are now limited to Original Medicare, and plan members are sent to their plan, as the source does. Paraphrase, not quoted, so no wording issue.
Corrections verified

Corrections verified: 2026-11-26, agent in cse_014eaiSdvHByATtNdterRhh7
Reader: agent in cse_014eaiSdvHByATtNdterRhh7

## Addendum 2026-11-26 (ACQ-162, cse_014eaiSan3kSKEb4rtUHknYk): payer of the $0

Found while checking the site for the payer error the hospice audit found (ops/reviews/live/medicare-hospice-benefit-explained.md). Medicare.gov "Home health services", Costs, read 2026-11-26: "You pay nothing for covered home health services." The page's description and short answer said "Medicare pays $0", which tells a family that Medicare pays nothing.

| Guide's claim | Guide's scope | Source's scope (heading) | Result |
|---|---|---|---|
| "Medicare pays $0 for covered home health visits" (desc, short answer) | the family's cost | Costs: "You pay nothing for covered home health services." | DEFECT: wrong payer. Corrected to "Your parent pays $0". |

Open, not applied here: the guide's card text in CARDS ("Medicare pays $0 for a covered home health visit ...") has the same error. Changing it rebuilds /guides/ and every related-guide card, which the library-date rule keeps out of this pull request while publish batch #90 is open; it is applied after package #91 merges (task in the queue).

Review date left at 2026-11-17 (only this sentence was re-read).

Quotations checked: 5. Claims scope-checked: 1. Scope defects: 1. Corrections required: 1 (applied) + 1 (card, after #91).
