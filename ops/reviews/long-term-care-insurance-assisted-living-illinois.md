# Review packet: long-term-care-insurance-assisted-living-illinois

- Page: drafts `_dist/guides/long-term-care-insurance-assisted-living-illinois/` (build commit 83fc8f3, ACQ-083, built by cse_014eaiSeZV5K4aUnZndensii).
- Reviewed: 2026-11-25 by ESCG worker task ACQ-084, session cse_014eaiScJVcYfw9RjXT6F5Km (a different session from the build).
- Method: `ops/quotecheck.py` on a fresh clone of drafts (21 quotations, 21 FOUND, 0 NEAR MATCH, 0 NOT FOUND; 3 short terms found; 5 cited pages, 0 unreadable). Whole output read. The Shopper's Guide PDF was also read as text (pdftotext) for every paraphrase; the IDOI complaint page, the IDOI LTC page, the Department on Aging SHIP LTC page and the HFS Supportive Living Program page were fetched 2026-11-25.
- Builder's note checked: every rule taken from the 2019 NAIC Shopper's Guide is framed as how policies are commonly written; the page says so in its own paragraph ("It describes how policies are commonly written, not what your parent's policy says. Where the two differ, the policy decides."). No NAIC rule is presented as Illinois law.

## Claims table

| # | Guide's claim | Guide's scope | Source's scope (heading) | Result |
|---|---|---|---|---|
| 1 | IDOI lists "care in an assisted living facility" among LTC services | general description | IDOI, Long-Term Care Insurance: list of what LTC services may include | same |
| 2 | "Long-term care insurance will pay for some or all of your long-term care." | general; followed at once by "depends on the words of their own policy" | IDOI, You Have Options When Paying for Long-Term Care | same |
| 3 | "If you have questions about your insurance policy, contact your insurance agent ..." | policyholders | IDOI, Review Your Contract Carefully | same |
| 4 | "Medicare, Medicare supplement insurance and health insurance you may have at work usually will not pay for long-term care" | general | IDOI, You Have Options When Paying | same ("usually" kept) |
| 5 | Shopper's Guide is NAIC, revised 2019, posted by IDoA SHIP; describes common policy terms | framing | PDF footer "© 2019 National Association of Insurance Commissioners"; hosted on ilaging.illinois.gov/ship | same |
| 6 | "If you're not in the right type of facility (described in your policy), the insurance company can refuse to pay" | policies generally | PDF p.15, Where Services Are Covered | same |
| 7 | Some policies pay in any state-licensed facility, some only in certain ones, some list exclusions | policies generally | PDF p.15-16: "Some policies may pay for care in any state-licensed facility. Others only pay for care in some state-licensed facilities ... Still others list the types of facilities where services won't be covered" | same |
| 8 | "many states, companies and policies define assisted living facilities differently"; check licence/certification requirement | policies generally | PDF p.16 | same |
| 9 | Check with insurer before making plans for care | advice | PDF p.15: "you always should check with your insurance company before making plans for your care" | same |
| 10 | Section called "Eligibility for the Payment of Benefits" or "Eligibility for Benefits" | policy documents | PDF p.18 | same |
| 11 | Most common trigger: two ADLs, 90 days, six ADLs | commonly written policies ("the guide says") | PDF p.19 Types of Benefit Triggers: "The most common way insurance companies decide ..." | same |
| 12 | Hands-on vs stand-by help | some policies / others | PDF p.19: "Some policies say ... hands-on assistance. Others say ... stand-by assistance" | same |
| 13 | Cognitive impairment quotation | general | PDF p.19 | same |
| 14 | Doctor certification; tax-qualified policies cannot use it | some policies; tax-qualified policies | PDF p.19: "However, tax-qualified policies can't use this benefit trigger." | same |
| 15 | "Most policies do not pay from the first day." | most policies | PDF p.19 When Benefits Start: "With many policies, your benefits won't start the first day" | OVERSTATED: source says "many", not "most" (correction 1) |
| 16 | Elimination period "can be 20, 30, 60, 90 or 100 days" | policies generally | PDF p.20 | same |
| 17 | Pay own care during elimination; no pay for family care | policies generally ("Companies") | PDF p.20 | same |
| 18 | Calendar-day method; "many coverages will not start counting those days until you incur costs" | some policies | PDF p.20 | same |
| 19 | Service-days method quotation | some policies | PDF p.20 | same |
| 20 | Ask "if the insurance company requires another elimination period for a second stay." | advice | PDF p.21 | same |
| 21 | Premium waiver quotations, 60 to 90 days | some/other companies | PDF p.23 Waiver of Premium | same |
| 22 | Third-party notice: policyholder can name someone insurer must contact; quotation on cognitive impairment | policyholder | PDF p.23 Third-Party Notice; glossary | same |
| 23 | First contact the insurer or agent, document calls (quotation) | Illinois insurance complaints | IDOI, The Complaint Process: "Before filing a complaint ..." | same |
| 24 | Department handles complaints that "may include coverage issues, claim disputes ..." | Illinois insurance complaints | IDOI, What types of complaints does the Department handle? | same |
| 25 | Consumer Assistance (866) 445-5364; complaints in writing; online Help Center, email DOI.complaints@illinois.gov, post | Illinois | IDOI, How to file a complaint (online, email, mail to 4800 Wabash Avenue, Springfield; also fax) | same (fax not listed: not a defect) |
| 26 | "Illinois law allows 21 days for an insurer or agent to respond to a complaint." | complaint filed with the Department | IDOI, The Complaint Process: follows "A copy of the complaint will be sent to the insurance company." | same (sentence sits after the Department filing paragraph) |
| 27 | Department cannot "Make medical judgments" / "Act as your lawyer or give you legal advice." | IDOI | IDOI, The Department cannot: | same |
| 28 | SHIP LTC page lists Senior HelpLine 1-800-252-8966 | Illinois | IDoA SHIP Long-Term Care page (header and footer: "Senior HelpLine: 1-800-252-8966") | same |
| 29 | "If savings may run out later, the Illinois Medicaid long-term care guide explains how the state can take over." | a parent in assisted living whose policy runs out | No cited source. HFS, Supportive Living Program: Medicaid pays for services in this kind of residence through the SLP waiver, for services "that are not routinely covered by Medicaid", and "The resident is responsible for paying the cost of room and board at the facility." The linked Medicaid LTC guide does not mention assisted living. | SCOPE DEFECT: implies Medicaid takes over an assisted living bill (correction 2) |
| 30 | Internal links: /guides/assisted-living-cost-illinois/, /guides/illinois-medicaid-long-term-care/, /guides/does-medicare-pay-for-senior-care/, /guides/illinois-supportive-living-program/, /#assessment, / | | all live on main (production /guides/ index and sitemap read 2026-11-25) | same |
| 31 | External link https://idoihelpcenter.illinois.gov/s/ | | HTTP 200 on 2026-11-25; named on the IDOI complaint page | same |

## Required corrections

1. Under "When payments start: the elimination period", change "Most policies do not pay from the first day." to "Many policies do not pay from the first day."
   Source (Shopper's Guide, p.19, When Benefits Start (Elimination Period)): "With many policies, your benefits won't start the first day you go to a nursing home or start using home care."

2. Under "Where the policy fits in the bigger picture", replace "If savings may run out later, the Illinois Medicaid long-term care guide explains how the state can take over." with a sentence that does not say Medicaid takes over an assisted living bill, for example: "If savings may run out later, Medicaid does not simply pick up an assisted living bill. One Illinois Medicaid route into this kind of residence is the Supportive Living Program, where, HFS says, "The resident is responsible for paying the cost of room and board at the facility"; the Supportive Living Program guide explains it, and the Illinois Medicaid long-term care guide covers nursing home care and care at home." Add the HFS page (https://hfs.illinois.gov/medicalprograms/slf.html) to SRC, and link /guides/illinois-supportive-living-program/ there.
   Source (HFS, Supportive Living Program, 2026-11-25): "Illinois developed the Supportive Living Program (SLP) as an alternative to nursing home care for low-income older persons and persons with physical disabilities under Medicaid." "The Department of Healthcare and Family Services has obtained a "waiver" to allow payment for services that are not routinely covered by Medicaid." "The resident is responsible for paying the cost of room and board at the facility."
   Scope: the HFS sentences are about the SLP only; the corrected sentence must not say SLP is the only route or that every assisted living community takes part.

## Recommended additions

- Under "If the claim stalls or is refused", the IDOI page also lists fax, (217) 558-2083, and asks complainants to "Keep your originals and send only copies of information." Scope: Illinois Department of Insurance complaints. Optional.

Quotations checked: 21. Claims scope-checked: 31. Scope defects: 1. Corrections required: 2.

Verdict: publish-ready after corrections

Corrections applied: drafts 2c15ef1, 2026-11-25, cse_014eaiScJVcYfw9RjXT6F5Km
