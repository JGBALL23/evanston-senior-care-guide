# Accuracy audit: illinois-advance-directive-power-of-attorney (live, main 4dc2468)

Audited 2026-11-26 by the ESCG worker (ACQ-113, cse_014eaiSdDK6VjczHrPrWrgM1). Sources read today: IDPH Advance Directives (https://dph.illinois.gov/topics-services/health-care-regulation/nursing-homes/advance-directives.html, 200), Illinois Department on Aging Advance Directives (https://ilaging.illinois.gov/aboutus/legal-adv-directives.html, 200), Illinois Department on Aging Legal Assistance (https://ilaging.illinois.gov/programs/legalassistance.html, 200). Search Console read 25 Nov: 26 impressions, position 53.3.

quotecheck: 5 quotations, 5 FOUND, 0 unreadable cited pages; note on quotation 1: "the final punctuation inside the quotation marks is not in the source".

| Guide's claim | Guide's scope | Source's scope (heading) | Result |
|---|---|---|---|
| Four advance directives: POA for Health Care, Living Will, Mental Health Treatment Preference Declaration, POLST | Illinois | IDPH Advance Directives: "Illinois law allows you to make four types of advance directives" | same |
| POLST "a medical order, signed by a doctor as well as your parent" | everyone | IDPH Practitioner Orders For Life-Sustaining Treatment: "requires your signature or that of your authorized legal representative ... as well as the signature of your attending practitioner" | SCOPE DEFECT: signer is the attending practitioner (not only a doctor) and the parent or an authorised representative: C2 |
| "no health care facility, health care professional or insurer can make you execute an advance directive." (full stop inside the quotation) | any requirement | IDPH Final Notes: "No health care facility, health care professional or insurer can make you execute an advance directive as a condition of providing treatment or insurance." | SCOPE DEFECT: the quotation stops mid-sentence and drops the limit (as a condition of treatment or insurance): C1 |
| "It is entirely your decision." | everyone | Final Notes | same |
| Agent makes personal and health care decisions; follows instructions incl. life-sustaining treatment and anatomical gifts; cannot be the parent's health care professional or provider; lasts until death unless time-limited; backup agent; cancel any time, changes in writing; non-agent witness; electronic copy accepted | Illinois POA for Health Care | IDPH Health Care Power of Attorney; IDoA Description of Advance Directives | same |
| Free forms from IDPH (Spanish versions) and IDoA; POLST in English and 8 named languages | Illinois | IDPH Forms; IDoA Advance Directives | same |
| No POA: two doctors certify, then surrogate in fixed order guardian of the person ... guardian of the estate | Illinois | IDPH What Happens If You Cannot Make Health Care Decisions | same |
| Surrogate cannot withdraw/withhold life-sustaining treatment without a qualifying condition (three named); non-guardian surrogate cannot consent to ECT, psychotropic medication, mental health admission; may petition a court | Illinois surrogate | same heading | same |
| Living will: terminal condition and unable to state wishes; two witnesses, not the health care professional; food and water; pregnancy; agent decides unless unavailable | Illinois | IDPH Living Will | same |
| POLST: parent or authorised representative and attending practitioner sign; not entered without all signatures; can record no CPR | Illinois | IDPH POLST | same |
| Information given "upon admission to a facility or when provision of care begins." | nursing home or hospital (section heading) | IDPH Advance Directives: PSDA providers in Medicare and Medicaid: hospitals, nursing facilities, home health, hospice, HMOs | same |
| "No health care facility can make your parent sign one." | any requirement | Final Notes: "... as a condition of providing treatment or insurance." | SCOPE DEFECT (same limit dropped): C1 |
| Facility that objects "on moral or religious grounds" must say so and keep providing care until transfer | objections on moral or religious grounds | Final Notes: "If a health care facility, health care professional or insurer objects to following your advance directive, they must tell you ... They must continue to provide care until you or your decision maker can transfer you" (no ground named) | DEFECT (c): the cited source states no moral or religious condition; the duty applies to any objection: C3 |
| Legal aid through AAAs "may help with a wide variety of civil law issues."; AAA map tool, Service Locator, Senior HelpLine 1-800-252-8966 (711 TRS) | Illinois | IDoA Legal Assistance; IDoA site header "Senior HelpLine: 1-800-252-8966 (711 TRS)" | same |
| Links: levels-of-senior-care-explained, / | | on main | same |

Required corrections
- C1. Quote the sentence in full: "no health care facility, health care professional or insurer can make you execute an advance directive as a condition of providing treatment or insurance." and in "What a nursing home or hospital must do": "No health care facility can make signing one a condition of treating your parent." Source (Final Notes): "No health care facility, health care professional or insurer can make you execute an advance directive as a condition of providing treatment or insurance."
- C2. POLST list item: "a medical order, signed by your parent (or an authorised representative) and by their attending practitioner". Source (Practitioner Orders For Life-Sustaining Treatment): "The Uniform POLST Order requires your signature or that of your authorized legal representative (your legal guardian, health care power of attorney, or health care surrogate), as well as the signature of your attending practitioner."
- C3. "If a facility objects to following your parent's directive, the Illinois Department of Public Health states it must say so ..." (drop "on moral or religious grounds"). Source (Final Notes), as quoted in the table.

Recommended additions: none.

Quotations checked: 5. Claims scope-checked: 15. Scope defects: 3. Corrections required: 3.
Verdict: corrections required (C1, C2, C3).

Corrections applied: claude/accuracy-20261125 d7724d0, 2026-11-26, cse_014eaiSdDK6VjczHrPrWrgM1 (C1, C2, C3; reviewed date unchanged)

## Reader check 2026-11-26

Independent reader, branch claude/accuracy-20261125 at d7724d0 (built page _dist/guides/illinois-advance-directive-power-of-attorney/index.html matches build-guides.py). quotecheck: 5 quotations, 5 FOUND, 0 NEAR MATCH, 0 NOT FOUND, 3 cited pages, 0 unreadable. IDPH page fetched again today (200). The commit changes no link.

- C1a. "The Illinois Department of Public Health states plainly that "no health care facility, health care professional or insurer can make you execute an advance directive as a condition of providing treatment or insurance."" Source (IDPH Advance Directives, Final Notes): "No health care facility, health care professional or insurer can make you execute an advance directive as a condition of providing treatment or insurance." Same scope (the condition of treatment or insurance is now in the quotation; the source's capital N is lower-cased only because the quotation runs into the guide's sentence, and quotecheck reports FOUND).
- C1b. "No health care facility can make signing one a condition of treating your parent." Source: the same Final Notes sentence. Same scope (a narrower true subset: facility and treatment; the source also covers professionals, insurers and insurance, which the first section already quotes in full).
- C2. "Practitioner Orders for Life-Sustaining Treatment (POLST) - a medical order, signed by your parent (or an authorised representative) and by their attending practitioner, setting out which life-sustaining treatments to use or withhold" Source (IDPH, Practitioner Orders For Life-Sustaining Treatment): "The Uniform POLST Order requires your signature or that of your authorized legal representative (your legal guardian, health care power of attorney, or health care surrogate), as well as the signature of your attending practitioner." Same scope.
- C3. "If a facility objects to following your parent's directive, the Illinois Department of Public Health states it must say so and must keep providing care until your parent can be transferred to a provider who will follow it." Source (IDPH, Final Notes): "If a health care facility, health care professional or insurer objects to following your advance directive, they must tell you or the individual responsible for making your health care decisions. They must continue to provide care until you or your decision maker can transfer you to another health care provider who will follow the orders contained in your advance directive." Same scope (no moral or religious condition; the source names none).

Corrections verified

Corrections verified: 2026-11-26, agent in cse_014eaiSdDK6VjczHrPrWrgM1
Reader: agent in cse_014eaiSdDK6VjczHrPrWrgM1
