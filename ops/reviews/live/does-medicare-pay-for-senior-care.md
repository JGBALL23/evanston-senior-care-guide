# Accuracy audit: does-medicare-pay-for-senior-care (live, main 4dc2468)

Audited 2026-11-26 by the ESCG worker (ACQ-097, cse_014eaiSdvHByATtNdterRhh7). Sources read today: Medicare.gov Skilled nursing facility care (https://www.medicare.gov/coverage/skilled-nursing-facility-snf-care, now redirecting to /coverage/skilled-nursing-facility-care), Medicare.gov Medicare costs, CMS Jimmo v. Sebelius fact sheet (PDF, text extracted), and Medicare.gov Long-term care (https://www.medicare.gov/coverage/long-term-care, not yet cited). Search Console read 25 Nov: 781 of the site's 1,242 impressions.

quotecheck: 0 quotations in curly quotes besides "Improvement Standard" (FOUND in the Jimmo fact sheet); every figure checked by hand below.

| Guide's claim | Guide's scope | Source's scope (heading) | Result |
|---|---|---|---|
| Medicare does not pay for assisted living or long-term custodial nursing home care | everyone with Medicare | Long-term care page: "Medicare doesn't pay for long-term care"; custodial care; "in an assisted living facility, or in a nursing home". None of the three cited pages says it (Medicare costs page has no custodial or assisted-living text) | CITATION DEFECT: claim true but its source is not cited; add Medicare.gov Long-term care to sources (C2) |
| Days 1-20 $0 after the Part A deductible $1,736 | Original Medicare, 2026 | SNF care, Costs: "Days 1-20: You pay $0 each day after you pay the $1,736 deductible ($1,776 in 2027)" | same |
| Deductible not charged twice in one benefit period | same | SNF care, Costs: "You don't have to pay the Part A deductible ... if you already paid it ... during the same benefit period" | same |
| Days 21-100 $217 a day in 2026; $17,360 for days 21-100 | Original Medicare, 2026 | SNF care, Costs: "Days 21-100: You pay $217 each day ($222 in 2027)"; 80 x $217 = $17,360 | same |
| Day 101 onward you pay all costs; 100 days per benefit period | same | SNF care, Costs: "Days 101 and beyond: You pay all costs. Part A limits SNF coverage to 100 days in each benefit period." | same |
| Medicare Advantage plans may charge copayments in days 1-20 | MA | SNF care, Costs: "If you're in a Medicare Advantage Plan, you may be charged copayments during the first 20 days" | same |
| 3-day inpatient stay, counting from inpatient admission, not the discharge day; observation/ER time does not count | Original Medicare | SNF care, Coverage details | same |
| ACO 3-Day Rule Waiver; MA plans may waive | same | SNF care, Coverage details | same |
| "Ask the hospital and ask the plan, neither will volunteer it" | everyone | SNF care: "Always ask your doctor or hospital staff if Medicare will cover your SNF stay." ... "Contact your plan for more information." Nothing says they will not volunteer it | UNSOURCED CLAIM: C3 |
| Entry generally within 30 days; daily skilled care decided by the doctor; Medicare-certified SNF; condition treated in the hospital stay or arising during SNF care | Original Medicare | SNF care, Who's eligible | same |
| Skilled care, "in Medicare's own words, can only be safely and effectively performed by or under the supervision of licensed professionals" | everyone | SNF care, Description: "can only be safely and effectively performed by, or under the supervision of, professionals or technical personnel" | WORDING DEFECT: attributed as Medicare's words but changes them ("licensed"; drops "technical personnel"): C1 |
| No "Improvement Standard"; skilled care covered to maintain or to prevent or slow deterioration | SNF and other skilled care | Jimmo fact sheet | same |
| Coverage properly ends when non-skilled staff can give the care safely and effectively | same | Jimmo fact sheet: "coverage ... would not be available in a situation where the beneficiary's care needs can be addressed safely and effectively through the use of nonskilled personnel" | same |
| Links: /guides/illinois-supportive-living-program/, /guides/assisted-living-cost-illinois/ | | both on main | same |

Required corrections
- C1. "in Medicare's own words, can only be safely and effectively performed by or under the supervision of licensed professionals" becomes "in Medicare's words, can only be safely and effectively performed by, or under the supervision of, professionals or technical personnel". Source (SNF care, Description): "Skilled care is nursing and therapy care that can only be safely and effectively performed by, or under the supervision of, professionals or technical personnel."
- C2. Add Medicare.gov Long-term care to the sources. Source: "Medicare doesn't pay for long-term care" ... "Long-term care (also called "custodial care" ...)" ... "You can get non-medical long-term care services at home, in the community, in an assisted living facility, or in a nursing home."
- C3. "Ask the hospital and ask the plan — neither will volunteer it." becomes "Medicare.gov's advice is to always ask your doctor or hospital staff whether Medicare will cover the stay, and to contact the plan." Source (SNF care, Coverage details): "Always ask your doctor or hospital staff if Medicare will cover your SNF stay." / "Contact your plan for more information."

Recommended additions
- A1 (a parent without a qualifying 3-day stay, whom the guide addresses in "The trap inside the first condition"). Source (SNF care, Coverage details): "If you don't have a 3-day qualifying inpatient hospital stay and you need care after your discharge from a hospital, ask if you can get care in other settings (like home health care) or if any other programs (like Medicaid or Veterans' benefits) can cover your SNF care." and "If you're a Medicare patient who was admitted to the hospital as an inpatient, and the hospital changed your status to "outpatient getting observation services," you may be able to appeal the denial of Part A (Hospital Insurance) inpatient coverage that came from the change in your status." Scope: Original Medicare inpatient whose status was changed.
- Watch (not a correction): Medicare.gov already prints the 2027 figures ($1,776 deductible, $222 a day). On 1 January 2027 the page's 2026 figures go out of date: a figure refresh is due then.

Quotations checked: 1. Claims scope-checked: 14. Scope defects: 0. Corrections required: 3.
Verdict: corrections required (C1 wording, C2 citation, C3 unsourced claim); figures hold.

Corrections applied: claude/accuracy-20261125 28073a0, 2026-11-26, cse_014eaiSdvHByATtNdterRhh7 (C1-C3 and A1; reviewed 2026-11-26, listed 2026-10-18; two check-guides.js assertions re-pinned)
