# Review: assisted-living-evanston (commit 5161afa, branch claude/al-evanston-memory-care)

Reader: independent reader, 28 November 2026. Clone: /tmp/reader-assisted-living-evanston (nothing changed, committed or pushed).

Scope of review: the sentences 5161afa changed: the new section `#memory-care` ("If your parent may need memory care in Evanston", three paragraphs), two new source-list entries, and the review-date line. The _dist copy is identical to the source page for this section.

Checker note: quotecheck.py reads `_dist/guides/<slug>/index.html`, but this page is built at `_dist/assisted-living-evanston/index.html`. The first run said "no built page". I copied the built file, unchanged, into a scratch mirror at `_dist/guides/assisted-living-evanston/index.html` and ran the checker on that copy. Result: 5 quotations, 5 FOUND, 0 NEAR MATCH, 0 NOT FOUND. It read all 8 cited pages. I also read both new sources myself: the IDPH plan PDF (pdftotext, pages 26 to 31) and the City of Evanston page (fetched 28 Nov 2026, HTTP 200).

## Table

| # | Guide's claim | Guide's scope | Source's scope (heading) | Result |
|---|---|---|---|---|
| Q1 | "This is a state licensure program with no federal oversight, as the residents in both assisted living and memory care areas are private pay through an establishment contract." | Illinois; IDPH Division of Assisted Living; residents of licensed assisted living and its memory care areas | IDPH plan 2026–2029, "Assisted Living Facilities": the IDPH Division of Assisted Living's ~570 establishments licensed under 77 Ill. Adm. Code 295; Illinois | FOUND; same |
| Q2 | staff ... required to take "six hours of initial dementia training and three hours of annual dementia training thereafter." | Illinois; staff serving people with dementia in an assisted living facility providing Alzheimer's or dementia services | "Dementia-Specific Training Requirements": "Staff serving clients with ADRD within a skilled nursing facility, assisted living facility, home health provider, or hospice program providing Alzheimer's or dementia services" (410 ILCS 406); Illinois | FOUND; same (the guide names one of the four settings the source lists) |
| Q3 | "There are currently 20 SLP dementia care settings with approximately 520 apartments." + "That figure is for the whole state." | Illinois statewide; Supportive Living Program; as of the 2026–2029 plan | "Residential Options for Persons with Dementia" (Illinois) and "Supportive Living Program Settings" ("Among these are 20 dementia sites with 520 apartments"; "The SLP operates statewide"); the plan's "currently" | FOUND; same. It is consistent with main's SLP guide (IDPH 2025 report: twenty sites, more than 520 apartments) |
| Q4 | Evanston Virtual Memory Café meets "Weekly on Thursdays from 2-3pm" | City of Evanston listing, virtual café | "Activities, Events, and Newsletters" > Memory Cafés > Evanston Virtual Memory Café | FOUND; same |
| Q5 | in-person memory café at Robert Crown Community Center, "Monthly on 3rd Saturday from 1 pm – 2 pm" | City of Evanston listing, in-person café | same heading > "OAsis In-person Memory Café that also includes other Older Adults", Location Robert Crown Community Center, Rms. B-C | FOUND (the source and the guide both use an en dash); same |
| C1 | "In Illinois, the state licenses assisted living, memory care areas included." | Illinois licensed assisted living | "Assisted Living Facilities": state licensure under 77 Ill. Adm. Code 295, residents "in both assisted living and memory care areas" | same |
| C2 | Tour advice: ask whether the memory care area is part of the state licence, look it up in the IDPH facility lookup, ask about staff dementia-training hours | family touring an Illinois assisted living community | follows from Q1, Q2 and C1 (Illinois ALF); the lookup link returns HTTP 200 | same |
| C3 | SLP is "an alternative to nursing home care for low-income older people" | Illinois; a low-income older parent | "Supportive Living Program Settings": "alternative to nursing home care for low-income older people and people with physical disabilities ages 22-64" | same (the guide names only the part of the source that fits its reader) |
| C4 | "with Medicaid waiver funding for services and the resident paying room and board" | Illinois SLP residents | "HFS has obtained a 'waiver' to allow payment for services not routinely covered by Medicaid ... The resident is responsible for paying the cost of room and board to the SLP provider." | same |
| C5 | "It says supply for dementia care is short" | Illinois, SLP dementia settings | "Residential Options for Persons with Dementia": "The need for affordable Supportive Living Program (SLP) settings that are appropriate for people with dementia is especially acute and the availability of even costly assisted living facilities (ALFs) with dementia care does not meet the demand." | same |
| C6 | Virtual café "needs no registration" | virtual café | "No registration is required" (under the virtual café entry) | same |
| C7 | in-person café: "registration by phone at 847-448-8630 or online" | in-person café | "Register: Call 847-448-8630 or Register Here" (under the OAsis entry) | same |
| C8 | page "also lists adult day services, caregiver support groups and links on choosing and paying for long-term care" | City of Evanston page | Headings "Adult Day Services" (CJE; House of Welcome), "Caregiver & Family Support Groups and Information", "Long-term care/residential care" (level of care, compare options, "How will you pay for long-term care?") | same |
| C9 | "Reviewed 21 November 2026; memory care section added 28 November 2026." | page metadata | commit date 28 Nov 2026 | same |

Links (d), checked against origin/main:
- `/guides/illinois-supportive-living-program/` exists on main (`_dist/guides/illinois-supportive-living-program/index.html`).
- `/guides/levels-of-senior-care-explained/` exists on main. It is not new in this commit.
- `/#assessment` exists in main's index.
- External links, all HTTP 200 on 28 Nov 2026: the IDPH facility lookup, the IDPH Alzheimer's plan PDF and the City of Evanston Dementia Friendly Evanston resources page.

Figures and dates (c):
- 6 + 3 hours, 20 settings / ~520 apartments, 2026–2029, Thursdays 2–3pm, 3rd Saturday 1–2 pm and 847-448-8630 all match the sources as they read today.
- The section has no "could not find" sentence.

Advice (e): the reader the section addresses is a family in Evanston whose parent may need memory care. The advice fits that reader:
- the tour questions;
- the IDPH lookup;
- SLP if private pay is not possible, marked as statewide, with a link to the SLP guide (main's SLP guide adds that no SLP site is in Evanston and the nearest dementia care setting is in Des Plaines);
- the free city memory cafés.

No advice is wrong for this reader.

## Required corrections

None. Every quotation is FOUND, and every claim's scope matches its source's scope.

## Recommended additions (not defects; apply as Improve, verify in a later session)

1. Supervisor training, on the same Illinois ALF scope as Q2. Source, IDPH plan, "Dementia-Specific Training Requirements": "Alzheimer's services supervisors in skilled nursing facilities and assisted living facilities are required to take 12 hours of annual dementia training". Scope: Illinois assisted living (and SNF) Alzheimer's services supervisors. It gives families a second tour question: ask how many hours of annual dementia training the memory care supervisor has completed.
2. Dementia program disclosure. Source, IDPH plan, "Quality Care Measures": "Illinois has an Alzheimer's Disease and Related Dementias Special Care Disclosure Act that requires licensed residential care settings that provide specialized care to individuals with dementia to disclose information about their program to the state agency responsible for licensing of that setting". Scope: Illinois licensed residential care settings that offer specialized dementia care, which includes an assisted living memory care area. On a tour, a family can ask to see what the community has disclosed to IDPH about its dementia program.

Quotations checked: 5. Claims scope-checked: 14. Scope defects: 0. Corrections required: 0.
Verdict: publish-ready

Corrections verified: 2026-11-28, agent in cse_014eaiSciSmPDNJW5sH6Zuua (commit 5161afa)
Reader: agent in cse_014eaiSciSmPDNJW5sH6Zuua

Corrections applied: claude/al-evanston-memory-care 8cfea0f, 2026-11-28, cse_014eaiSciSmPDNJW5sH6Zuua (recommended additions 1 and 2)
