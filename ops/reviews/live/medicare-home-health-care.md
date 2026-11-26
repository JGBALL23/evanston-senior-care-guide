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

## Reader check 2026-11-26

Independent reader, clone of claude/accuracy-20261125 at 7cfef07 (/tmp/reader-medicare-home-health-care), checking the sentences 7cfef07 changed (description, og:description and JSON-LD description, which are one sentence; and the short answer). quotecheck: 5 quotations, 5 FOUND, 0 NEAR MATCH, 0 NOT FOUND, 0 unreadable cited pages ("no longer improving" is a related-guide card phrase, not a quotation). Medicare.gov Home health services re-read today (200). The commit adds and changes no links.

- Description: "Your parent pays $0 for covered home health visits, but only for skilled care while a parent is homebound. A home health aide on its own is not covered." Source (Costs): "You pay nothing for covered home health services." ... "If you get your Medicare benefits through a Medicare Advantage Plan (Part C) or another Medicare health plan, check with your plan for more information about your home health benefits." Payer now right (the $0 is what the person pays). Still wrong: SCOPE DEFECT. The $0 is Original Medicare's term; the source sends plan members to their plan, and the sentence states $0 for every parent with no limit in the same sentence (the Original Medicare qualifier exists only in "What it costs"). Corrected sentence: "With Original Medicare, your parent pays $0 for covered home health visits, but only for skilled care while homebound (a Medicare Advantage plan sets its own terms). A home health aide on its own is not covered."
- Short answer: "Your parent pays $0 for a covered home health visit from a Medicare-certified agency, but it will only start one when a doctor who has examined your parent in person orders intermittent, skilled nursing or therapy and confirms your parent is homebound." Same source sentences (Costs), plus Provider requirements: "a doctor or health care provider (like a nurse practitioner) must see you in person and confirm you need home health care. They must also order your care, and a Medicare-certified home health agency must provide it." Still wrong: (1) SCOPE DEFECT as above, $0 stated for everyone though the source limits it to Original Medicare and sends Medicare Advantage / other plan members to the plan; (2) the edit left "it will only start one" with no antecedent (it used to be "Medicare"; it now reads as if the parent starts the visit). Corrected sentence: "With Original Medicare, your parent pays <strong>$0</strong> for a covered home health visit from a Medicare-certified agency (in a Medicare Advantage or other Medicare health plan, check with the plan), but Medicare covers one only when a doctor or other provider who has seen your parent in person orders <em>intermittent, skilled</em> nursing or therapy and confirms your parent is homebound."
- Not part of 7cfef07, still open as the addendum says: the CARDS text at build-guides.py line 5956, "Medicare pays $0 for a covered home health visit", has the wrong payer and the same missing Original Medicare limit; its correction should carry both.

Quotations checked: 5. Claims scope-checked: 2. Scope defects: 2. Corrections required: 2.
Reopened: the $0 in the description and short answer is stated for every parent although Medicare.gov's Costs section limits it to Original Medicare and sends Medicare Advantage and other Medicare health plan members to their plan; and the short answer's "it will only start one" lost its antecedent (Medicare). Corrected sentences above.

Reader: agent in cse_014eaiSan3kSKEb4rtUHknYk

Corrections applied: #89 7a71f92, 2026-11-26, cse_014eaiSan3kSKEb4rtUHknYk (per the reader check above; desc kept under 160 characters)

## Reader check 2026-11-26

Independent reader, clone of claude/accuracy-20261125 at 7a71f92 (/tmp/reader-medicare-home-health-care-2), checking the sentences 7a71f92 changed: the description (meta, og:description and JSON-LD carry the same two sentences) and the short answer. quotecheck: 5 quotations, 5 FOUND, 0 NEAR MATCH, 0 NOT FOUND, 2 cited pages, 0 unreadable ("no longer improving" is a related-guide card phrase, not a quotation). Medicare.gov Home health services re-read today (200). The commit adds and changes no links.

- Description, sentence 1: "With Original Medicare, your parent pays $0 for covered home health visits, only for skilled care while homebound." Source (Costs): "You pay nothing for covered home health services." ... "If you get your Medicare benefits through a Medicare Advantage Plan (Part C) or another Medicare health plan, check with your plan for more information about your home health benefits."; (Who's eligible): "You must need part-time or intermittent skilled services and you're "homebound,"". Same scope: the $0 is now limited to Original Medicare in the same sentence; it no longer claims anything for plan members (the short answer and "What it costs" send them to the plan).
- Description, sentence 2: "A home health aide alone is not covered." Source (Coverage details): "Part-time or intermittent home health aide care (only if you're also getting skilled nursing care, physical therapy, speech-language pathology services, or occupational therapy at the same time)". Same scope (Medicare's home health benefit, read with sentence 1's "With Original Medicare"); wording change only.
- Short answer: "With Original Medicare, your parent pays $0 for a covered home health visit from a Medicare-certified agency (in a Medicare Advantage or other Medicare health plan, check with the plan), but Medicare will only start one when a doctor who has examined your parent in person orders intermittent, skilled nursing or therapy and confirms your parent is homebound." Source (Costs), as above; (Provider requirements): "Before you can get home health services, a doctor or health care provider (like a nurse practitioner) must see you in person and confirm you need home health care. They must also order your care, and a Medicare-certified home health agency must provide it." The $0 scope is now right (Original Medicare, plan members to the plan, as the source) and Medicare is again the subject. Still wrong: SCOPE DEFECT (person). The sentence says only "a doctor who has examined your parent in person" can order and confirm the care, but the source gives the same role to "a doctor or health care provider (like a nurse practitioner)"; a family whose parent is followed by a nurse practitioner would read that a doctor's visit is needed first. The guide's own body ("The test that decides it") already says "A doctor or health care provider (like a nurse practitioner)". Also "Medicare will only start one" is loose (the agency starts the visit; Medicare covers it). Corrected sentence: "With Original Medicare, your parent pays <strong>$0</strong> for a covered home health visit from a Medicare-certified agency (in a Medicare Advantage or other Medicare health plan, check with the plan), but Medicare covers one only when a doctor or other health care provider (like a nurse practitioner) who has seen your parent in person orders <em>intermittent, skilled</em> nursing or therapy and confirms your parent is homebound."
- Not part of 7a71f92, still open as the addendum says: the CARDS text ("Medicare pays $0 for a covered home health visit ...") has the wrong payer and no Original Medicare limit.

Reader: agent in cse_014eaiSan3kSKEb4rtUHknYk

Quotations checked: 5. Claims scope-checked: 3. Scope defects: 1. Corrections required: 1.
Reopened: the short answer says only "a doctor who has examined your parent in person" orders and confirms home health care, but Medicare.gov's Provider requirements give that role to "a doctor or health care provider (like a nurse practitioner)"; corrected sentence above.

Reader: agent in cse_014eaiSan3kSKEb4rtUHknYk

Corrections applied: #89 9d57bf0, 2026-11-26, cse_014eaiSan3kSKEb4rtUHknYk (per the reader check of 7a71f92)
