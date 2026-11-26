# Accuracy audit: medicare-durable-medical-equipment-coverage (live, main 4dc2468)

Audited 2026-11-26 by the ESCG worker (ACQ-114, cse_014eaiSdDK6VjczHrPrWrgM1). Sources read today (all 200): Medicare.gov Wheelchairs & scooters, Hospital beds, Walkers, Canes, Commode chairs (https://www.medicare.gov/coverage/<page>). Also read: Medicare.gov Durable medical equipment coverage (not cited; it says nothing about Medicare Advantage either). Search Console read 25 Nov: 25 impressions, position 40.5.

quotecheck: 24 quotations, 24 FOUND, 0 NEAR MATCH, 0 unreadable; "no longer improving" is a related-guide card's text, not a quotation here. Seven "final punctuation not in the source" notes: six are commas or a list-item full stop where the source runs on without changing meaning; one (rental months) drops the consequence clause: C3.

| Guide's claim | Guide's scope | Source's scope (heading) | Result |
|---|---|---|---|
| "Part B covers medically necessary DME if your doctor or other health care provider orders it for use in your home." on walker, cane, commode pages | Part B DME | Who's eligible (same sentence also on hospital beds) | same |
| Power wheelchairs and scooters "only when they're medically necessary" | Part B | Wheelchairs: Who's eligible | same |
| "After you meet the Part B deductible, you pay 20% ... (if your supplier accepts assignment)."; deductible $283 for 2026 | Part B | Costs, every page; $283 checked in prior audit against Medicare costs | same |
| Item list: wheelchairs/scooters "if you're eligible," walkers incl. rollators, hospital beds "may cover", canes except white canes for the blind, commode chairs | Part B | each page's header / Coverage details | same |
| White cane covered differently "because Medicare classifies one as DME and the other as an aid for a different purpose" | Medicare | Canes, Coverage details: "Medicare doesn't cover white canes for the blind." (no reason given) | DEFECT (c): reason not on the cited page: C2 |
| "Medicare will only pay for DME items if you get them from suppliers who are enrolled in Medicare." | Medicare | Provider requirements, every page | same |
| "If a supplier participates in Medicare, they must accept assignment," | Medicare | Costs | same |
| "make sure the supplier is willing to accept assignment for all rental months." (full stop inside the marks) | rented DME | Costs: "... for all rental months, otherwise you'll have to pay the full cost of your DME upfront. If this happens, Medicare will pay you later ..." | WORDING/(e): sentence cut before the consequence a family would act on: C3 |
| "If a DME supplier doesn't participate ... you may be charged more." | Medicare | Hospital beds, Costs | same |
| Power wheelchair/scooter: face-to-face exam and written prescription | power wheelchairs and scooters | Wheelchairs: Who's eligible | same |
| Answer: power wheelchairs and scooters ... "some require Medicare's prior approval" | power wheelchairs and scooters | Wheelchairs, Provider requirements: "prior approval ... for certain types of power wheelchairs" | SCOPE DEFECT: prior authorization named for certain power wheelchairs only, not scooters: C1 |
| Body: prior approval for "certain types of power wheelchairs,"; supplier submits; denial reasons | power wheelchairs | Provider requirements | same |
| Rent / buy / choose; ownership after rental payments | DME | Coverage details | same |
| Links: levels-of-senior-care-explained, / | | on main | same |

Required corrections
- C1. Answer: "Power wheelchairs and scooters need a face-to-face exam and a written prescription first, and certain types of power wheelchairs need Medicare's prior approval before Medicare will cover them." Source (Wheelchairs & scooters, Provider requirements): "You may have to get prior approval (known as "prior authorization") for certain types of power wheelchairs before Medicare will cover the wheelchair cost."
- C2. Cane paragraph: "... are covered differently, and Medicare.gov's cane page states the exclusion without giving a reason for it." Source (Canes, Coverage details): "Medicare doesn't cover white canes for the blind."
- C3. Quote through the consequence: "make sure the supplier is willing to accept assignment for all rental months, otherwise you'll have to pay the full cost of your DME upfront." Source (Walkers, Costs): "For rented DME, make sure the supplier is willing to accept assignment for all rental months, otherwise you'll have to pay the full cost of your DME upfront."

Watch: none of the five cited pages mentions Medicare Advantage; a later audit could cite an official Medicare.gov sentence on plan members' DME costs if one is found (no source found today, so no claim added).

Quotations checked: 24. Claims scope-checked: 16. Scope defects: 1. Corrections required: 3.
Verdict: corrections required (C1, C2, C3).

Corrections applied: claude/accuracy-20261125 63284d5, 2026-11-26, cse_014eaiSdDK6VjczHrPrWrgM1 (C1, C2, C3; reviewed date unchanged)

## Reader check 2026-11-26

Independent reader, claude/accuracy-20261125 at 63284d5 (clone /tmp/reader-medicare-durable-medical-equipment-coverage). quotecheck: 24/24 FOUND, 0 NEAR MATCH, 0 NOT FOUND, 5 cited pages, 0 unreadable (the one short term not found, "no longer improving", is a related-guide card's text). All five cited Medicare.gov pages refetched today (200); changed sentences checked against them. No links in the changed sentences.

- C1 (Short answer): "Power wheelchairs and scooters need a face-to-face exam and a written prescription first, and certain types of power wheelchairs need Medicare's prior approval before Medicare will cover them." Source, Wheelchairs & scooters, Who's eligible: "You must have a face-to-face examination and a written prescription from a treating provider before Medicare covers a power wheelchair or scooter."; Provider requirements: "You may have to get prior approval (known as "prior authorization") for certain types of power wheelchairs before Medicare will cover the wheelchair cost." Same scope: exam/prescription for power wheelchairs and scooters, prior approval for certain power wheelchairs only (scooters no longer included); payer Part B, as the sentence before says ("Medicare Part B covers ..."), the same as the page.
- C2 (cane paragraph): "... are covered differently, and Medicare.gov's cane page states the exclusion without giving a reason for it." Source, Canes, Coverage details: "Medicare doesn't cover white canes for the blind." The page as it reads today gives no reason anywhere. Same scope; the unsourced reason is gone.
- C3 (supplier section): "... for anything rented rather than bought, "make sure the supplier is willing to accept assignment for all rental months, otherwise you'll have to pay the full cost of your DME upfront."" Source, Walkers, Costs (same on Wheelchairs & scooters): "For rented DME, make sure the supplier is willing to accept assignment for all rental months, otherwise you'll have to pay the full cost of your DME upfront." Copied exactly (FOUND, curly apostrophe matches) and attributed correctly to the walkers page. Same scope: rented DME under Part B.

Recommended addition (not a defect, does not block publish-ready): C3 now tells the family they'll pay the full cost upfront but not what happens next. The source's next sentence (Walkers, Costs; scope: rented DME from a supplier that won't accept assignment for every rental month, Original Medicare/Part B) is: "If this happens, Medicare will pay you later for the amount it covers after your claims have been submitted and processed by Medicare." Suggest adding it after the C3 quotation.

Outstanding from the packet's "Watch" line, not part of C1-C3: none of the five cited pages mentions Medicare Advantage, and the guide nowhere says that its deductible, 20% coinsurance, assignment and prior-approval terms are Original Medicare (Part B) terms, or that a parent in a Medicare Advantage plan should check the plan's own costs, supplier network and prior-authorization rules. Owner rule (b) says the guide should say that plainly. A sibling guide got this fix in f91038b (medicare-home-health-care). It does not reopen C1-C3, which match their sources' scope, but the next review of this page should handle it.

Corrections verified

Corrections verified: 2026-11-26, agent in cse_014eaiSdDK6VjczHrPrWrgM1
Reader: agent in cse_014eaiSdDK6VjczHrPrWrgM1

Recommended additions applied: claude/accuracy-20261125 c160353, 2026-11-26, cse_014eaiSdDK6VjczHrPrWrgM1 (A1 rental pay-back sentence, walkers page Costs; A2 Original Medicare terms named and Medicare Advantage members per Medicare publication 11045 (2/2025), "What if I need DME, and I'm in a Medicare Advantage Plan?"; reviewed date unchanged)
