# Accuracy audit: medicare-hospice-benefit-explained (live)

Audited 2026-11-26 by the ESCG worker (ACQ-150, cse_014eaiSan3kSKEb4rtUHknYk) on main 4dc2468, under the review rules (scope rule included). Sources read 2026-11-26: Medicare.gov "Hospice care" (https://www.medicare.gov/coverage/hospice-care, including its "What if I'm in a Medicare Advantage Plan or other Medicare health plan?" drawer) and Medicare.gov "Medicare costs" (https://www.medicare.gov/basics/costs/medicare-costs). Quotation checker: 1/1 FOUND, both cited pages readable.

| Guide's claim | Guide's scope | Source's scope (heading) | Result |
|---|---|---|---|
| "end-of-life care for people with illnesses that can't be cured" | everyone | Description | same (FOUND) |
| Medicare pays $0 for covered hospice care (short answer, desc, "What the hospice benefit actually pays for") | the family's cost | Costs: "You pay nothing for hospice care if you get your care from a Medicare-approved hospice provider." | DEFECT: the $0 is what the person pays, not what Medicare pays. Corrected to "Your parent pays $0" / "You pay $0". |
| Eligibility: Part A; hospice doctor and own doctor certify 6 months or less; comfort care; Hospice Election Statement before services | everyone with Original Medicare | Who's eligible | same |
| Recertification after 6 months by "a hospice doctor or nurse practitioner ... after a face-to-face visit" | everyone | Provider requirements: "as long as the hospice medical director or hospice doctor recertifies (after a face-to-face meeting with the hospice doctor or hospice nurse practitioner)" | DEFECT: the nurse practitioner holds the face-to-face meeting; the medical director or hospice doctor recertifies. Corrected. |
| Not covered once hospice starts: cure, curative drugs, non-hospice provider, room and board, hospital/ambulance unless arranged or unrelated | everyone | Coverage details | same (the room-and-board item sits under "unless the hospice team arranges it") |
| Room and board in a facility "not paid by the hospice benefit at all" (What it costs) and in the short answer | facility residents | Coverage details: "If the hospice team determines that you need short-term inpatient or respite care services that they arrange, Medicare will cover your stay in the facility." | SCOPE DEFECT: the source's exception for an arranged inpatient or respite stay was dropped. Corrected in both places. |
| $5 per prescription copay; 5% of the Medicare-approved amount for inpatient respite; copay "can't be more than the inpatient deductible amount" | everyone | Costs | same |
| Part A deductible $1,736 per benefit period | 2026 | Medicare costs: "$1,736 ($1,776 in 2027)" | holds for 2026; the 2027 move is already queued as ACQ-043 (key technical:medicare-2027-figures, not before 8 Dec), which edits the shared F block. |
| Unrelated problems still covered with ordinary deductibles and coinsurance | Original Medicare | Costs: "Original Medicare will still pay ... but you'll owe any deductible and coinsurance amounts that apply." | same |
| Usually at home or where your parent lives incl. assisted living/nursing home; inpatient hospice facility when conditions are met | everyone | Facility | same |
| Two 90-day periods, then unlimited 60-day; change provider once per benefit period | everyone | How often; Provider requirements | same |

Required corrections (applied in accuracy PR #89):
1. "Medicare pays $0" -> "Your parent pays $0" (answer, body) and "You pay $0" (desc). Source: "You pay nothing for hospice care if you get your care from a Medicare-approved hospice provider." (Costs)
2. Recertification: "as long as the hospice medical director or hospice doctor recertifies that your parent is still terminally ill, after a face-to-face meeting with the hospice doctor or hospice nurse practitioner." Source: Provider requirements sentence above.
3. Room and board: the arranged short-term inpatient or respite stay exception added to the short answer and to the cost list. Source: "If the hospice team determines that you need short-term inpatient or respite care services that they arrange, Medicare will cover your stay in the facility." (Coverage details)

Recommended additions (applied in #89):
- Medicare Advantage: "Original Medicare will cover everything you need related to your terminal illness once your hospice benefit starts, even if you stay in your plan." "Your plan must help you locate a Medicare-approved hospice provider in your area." "Your plan can still cover services that aren't part of your terminal illness and related conditions." (drawer "What if I'm in a Medicare Advantage Plan or other Medicare health plan?"; scope: people in a Medicare Advantage Plan or other Medicare health plan)

LIBRARY DATE: reviewed 2026-11-26 with "listed": "2026-10-25"; _dist/guides/index.html unchanged; sitemap.xml differs only in this guide's lastmod.

Quotations checked: 1. Claims scope-checked: 11. Scope defects: 3. Corrections required: 3.
Verdict: corrections listed (applied to accuracy PR #89; reader check pending)
