# Accuracy audit: illinois-medicaid-look-back-period (live)

- Page: main 4dc2468, `_dist/guides/illinois-medicaid-look-back-period/` (reviewed date on page: 17 November 2026).
- Audited: 2026-11-25, ESCG worker task ACQ-089, session cse_014eaiScJVcYfw9RjXT6F5Km.
- Method: `ops/quotecheck.py --site <main clone> --slug illinois-medicaid-look-back-period`: 13 quotations, 13 FOUND, 0 NEAR MATCH, 0 NOT FOUND; 1 short term ("spend-down", the title of a linked guide, not a quotation of a source); 2 cited pages, 0 unreadable. Whole output read. HFS 3191 re-fetched 2026-11-25; HFS Provider Notice of 22 January 2026 (notice.prn260122a, cited by the live Medicaid long-term care guide) fetched 2026-11-25.

## Claims table

| # | Guide's claim | Guide's scope | Source's scope (heading) | Result |
|---|---|---|---|---|
| 1 | Brochure title "Long Term Services & Information for Couples" (HFS 3191) | | HFS 3191 page title | same |
| 2 | Transfers "within 60 months (5 years) of the date you apply for medical coverage" affect nursing home, SLF and DoA in-home waiver services | applicant for those three services | HFS 3191, Transfer of Resources to Qualify for Medical Benefits: "... and are living in a nursing home, SLF or you apply for or receive in-home care services through DoA" | same |
| 3 | 36 months before; 60-month rule from 1 January 2012 | | same heading: "went into effect January 1, 2012. Before 2012, the rules were based on 36 months (3 years.)" | same |
| 4 | "giving away or selling your resources for less than what they are worth may affect your eligibility" | | same heading | same |
| 5 | Penalty period definition (nursing home, SLF, HCBS) | | same heading | same |
| 6 | Joe example, $80,000, "may have a penalty period based on the transfers." | | same heading | same |
| 7 | Martha example, "a minimal amount consistent with her past behavior." | | same heading | same |
| 8 | Short answer: "HFS says a transfer to a spouse ... will not trigger one" | any transfer to a spouse, any amount, any of the three services | HFS 3191, Protecting Property for Your Community Spouse: "When you go into a nursing home ... You may transfer this other property to your spouse ... Depending on how much property your spouse already has ..., you may give your spouse property valued up to $109,560 for 2015.* The amount may increase each year. Your FCRC caseworker will tell you the actual amount you may give to your spouse." | SCOPE DEFECT: the source limits the spousal transfer to an annual amount less what the spouse already has, and states it for a parent going into a nursing home (correction 1) |
| 9 | "Transfers to a spouse" bullet quotes "You may transfer this other property to your spouse ... sole benefit of your spouse," and lists home, car, furnishings | presented as a penalty-free exception without limit | same heading; the limit sentence follows in the same paragraph | SCOPE DEFECT: the quoted sentence is cut before the limit the source attaches to it (correction 2) |
| 10 | Returning the property eliminates a penalty | | HFS 3191: "You may eliminate a penalty by getting back the property that was transferred" | same |
| 11 | Penalty starts "the month of application or the month you transferred the resources, whichever is later." | | HFS 3191 | same |
| 12 | Length: "the uncompensated value ... at the private rate." | | HFS 3191 | same |
| 13 | Second penalty "begins with the month following the month the previous penalty period ends" | | HFS 3191 | same |
| 14 | "You will still be entitled to other medical services during the penalty period, if you are eligible" | | HFS 3191 | same |
| 15 | Hardship if penalty would leave parent without "food, shelter, clothing or necessary medical care." | | HFS 3191: "if it can be proven that the penalty would cause you to be without" | same |
| 16 | The FCRC tells the penalty length | | HFS 3191: "your local FCRC will inform you of the penalty period" | same |
| 17 | Brochure's figures dated 2015; "The amount may increase each year."; "Eleven years on" | | HFS 3191 | same |
| 18 | The CSRA/CSMNA in the Medicaid LTC guide are "a related but legally separate rule from the transfer exception on this page" | | HFS Provider Notice 22 Jan 2026: the CSRA "is the maximum amount of resources a resident may transfer to a community spouse or to another for the sole benefit of a community spouse. The actual amount a resident may transfer is determined by deducting nonexempt resources of the community spouse from the standard of $143,172.00." | WRONG: HFS describes the CSRA as the very ceiling on the spousal transfer this page discusses (correction 3) |
| 19 | Internal links: SLP, Medicaid LTC, estate recovery, levels of care, /, /#assessment | | all live on main | same |
| 20 | Source links hfs3191.html and medicalclients/ltc | | both HTTP 200 on 2026-11-25 | same |

## Required corrections

1. Short answer, last sentence. Now: "Not every transfer counts: HFS says a transfer to a spouse, or a small gift consistent with your parent's past giving, will not trigger one." Corrected: "Not every transfer counts: HFS says a small gift consistent with your parent's past giving will not trigger one, and a parent going into a nursing home may transfer property to a spouse up to a yearly limit that the caseworker works out."
   Source (HFS 3191, Protecting Property for Your Community Spouse): "Depending on how much property your spouse already has (not counting things like the house and the car), you may give your spouse property valued up to $109,560 for 2015.* The amount may increase each year. Your FCRC caseworker will tell you the actual amount you may give to your spouse."

2. "Transfers to a spouse" bullet: keep the quotation and add the limit in the same bullet, scoped to a nursing home: "When a parent goes into a nursing home, HFS states the spouse may keep the home, the car and the household furnishings, and that 'You may transfer this other property to your spouse or to someone else for the sole benefit of your spouse.' The same paragraph limits it: 'Depending on how much property your spouse already has (not counting things like the house and the car), you may give your spouse property' up to a yearly amount, and 'Your FCRC caseworker will tell you the actual amount you may give to your spouse.'" Replace the line "This guide is not going to put a current dollar ceiling on the spousal exception — see below for why." with one that points to the current figure (correction 3).
   Source: as in 1.

3. "Figures this guide will not publish": replace "that is a related but legally separate rule from the transfer exception on this page, so ask the FCRC which one applies to a specific transfer." with: "HFS's 2026 notice describes that allowance as the maximum amount of resources a resident may transfer to a community spouse, less what the spouse already holds, so it is the current ceiling on the spousal transfer above; the FCRC confirms the amount for a specific couple." Add the notice to SRC (hfs_spousal2026, already defined in build-guides.py).
   Source (HFS Provider Notice, 22 January 2026, Prevention of Spousal Impoverishment Standards for 2026): "This is the maximum amount of resources a resident may transfer to a community spouse or to another for the sole benefit of a community spouse. The actual amount a resident may transfer is determined by deducting nonexempt resources of the community spouse from the standard of $143,172.00."

Quotations checked: 13. Claims scope-checked: 20. Scope defects: 2. Corrections required: 3.

Verdict: corrections required (3), listed above; they go into the rolling accuracy pull request.
