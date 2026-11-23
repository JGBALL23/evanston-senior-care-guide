# Review packet: illinois-assisted-living-involuntary-move-out

- Date: 2026-11-23
- Reviewer: ESCG worker (session cse_014eaiSbQh9aYSa5vTbwv5wK)
- Draft: `GUIDES` entry in /tmp/drafts/build-guides.py (lines ~5161–5290); rendered page /tmp/drafts/_dist/guides/illinois-assisted-living-involuntary-move-out/index.html
- Cited sources: `idph_al_itr_form`, `idoa_ltc_rights_page`, `idoa_ombudsman_contact`

## Sources fetched

| # | URL | HTTP | Local text |
|---|-----|------|-----------|
| 1 | https://dph.illinois.gov/content/dam/soi/en/web/idph/files/forms/itrformwithhearingrequestrevised20200221.pdf (cited: `idph_al_itr_form`) | 200 (application/pdf, 3 pages) | /tmp/reviews/src-1.txt (pdftotext -layout) |
| 2 | https://ilaging.illinois.gov/programs/ltcombudsman/residents-rights-in-long-term-care-facilities1.html (cited: `idoa_ltc_rights_page`) | 200 | /tmp/reviews/src-2.txt |
| 3 | https://ilaging.illinois.gov/programs/ltcombudsman/contact-information--office-of-the-state-long-term-care-ombudsma.html (cited: `idoa_ombudsman_contact`) | 200 | /tmp/reviews/src-3.txt |
| 4 | https://ilaging.illinois.gov/content/dam/soi/en/web/aging/resources/newsandpublications/publications/documents/ltc-resrights.pdf (not cited; linked from source 2; SRC key `idoa_resident_rights_brochure`) | 200 (PDF) | /tmp/reviews/src-4.txt |
| 5 | https://dph.illinois.gov/topics-services/health-care-regulation/assisted-living.html (not cited; SRC key `idph_al_div`) | 200 | /tmp/reviews/x-7bab21.txt |
| 6 | https://ilaging.illinois.gov/programs/ltcombudsman.html (not cited; SRC key `idoa_ombudsman`) | 200 | /tmp/reviews/x-a62a4d.txt |

I fetched sources 4–6 to test the draft's "could not find" claim and its uncited sentences. All six are on allowed hosts.

## Quote audit

I extracted the quotes with a script (/tmp/reviews/.qa.py) from the rendered `<main>` and matched them against the fetched text after normalising whitespace and apostrophes. 6 quotes checked, 6 matched.

| Quote (excerpt) | Source | Match |
|---|---|---|
| has the right to continue to reside in the establishment until a decision is rendered | src-1 (IDPH ITR form, p.1) | yes |
| A 30-day prior written notice must be provided to the resident, resident's representat… | src-1 p.1 | yes |
| The establishment must notify the Illinois Department of Public Health when it initia… | src-1 p.1 | yes |
| Reason for Residency Termination | src-1 p.1 (field label) | yes |
| Please submit completed forms within 10 DAYS after receiving the Involuntary Terminati… | src-1 p.3 (Hearing Request form) | yes |
| The resident has the right to continue to reside in the establishment until a decisio… | src-1 p.1 | yes |

All quotes match word for word. The problems are in the paraphrase around them (see below).

## Claim checks

| Claim in draft | Result | Source's own wording |
|---|---|---|
| desc/answer: 30-day prior written notice to resident, representative or both, and to the LTC ombudsman | holds | src-1: "A 30-day prior written notice must be provided to the resident, resident's representative, or both, and to the long-term care ombudsman." |
| Form gives a right to appeal | holds | src-1: "The above resident has the right to appeal residency termination." |
| Establishment must notify IDPH | holds | src-1 (quoted) |
| Answer: right to stay until a decision "on a timely appeal"; body: "An appeal filed within the 10-day window … keeps your parent in place" | **does not hold (added condition)** | src-1: "The resident has the right to continue to reside in the establishment until a decision is rendered." The form does not tie this right to filing within 10 days. The 10-day line sits only on the Hearing Request form, as a submission instruction. |
| Form has a "Reason for Residency Termination" line | holds | src-1 field label |
| "IDPH's form does not leave that blank or optional — a reason has to be stated in writing" | **does not hold as sourced (interpretation)** | src-1 has only a blank field, with no words saying it is mandatory. src-4 (IDoA brochure, "appropriate for nursing homes and assisted living") does say: "You must be given a written notice if your facility requests that you leave. This notice must include: …why you are being asked to move" |
| Appeal by calling IDPH Division of Assisted Living 217-782-2448, or by sending a signed Appeal Hearing Request form | holds | src-1: "a) calling IDPH, Division of Assisted Living at 217-782-2448 OR b) sending the signed Appeal Hearing Request form to IDPH" |
| Deadline in capitals, 10 DAYS | holds | src-1 p.3 (quoted) |
| Mail or fax to 217-557-2432; IDPH, Division of Assisted Living, 525 West Jefferson Street, 5th Floor, Springfield, Illinois 62761 | holds | src-1 p.3: "Illinois Department of Public Health Division of Assisted Living, 525 West Jefferson Street, 5th Floor Springfield, Illinois 62761 or fax: 217-557-2432" |
| Form requires the establishment to name "a specific staff person" who will assist with relocation, "so a family is not left to figure out logistics with no one assigned to help" | **partly holds** | src-1: "The person at the establishment who will assist with relocation is: Name of Person ___". The form does not say "staff", and the clause about logistics is the draft's own interpretation. |
| "could not confirm … the specific list of situations that legally justify a termination"; the section saying it searched IDPH/IDoA pages for grounds "comparable to the four stated reasons the Department on Aging publishes for nursing homes … It did not find one" | **does not hold (contradicted by the draft's own cited page)** | src-2 (cited `idoa_ltc_rights_page`), on the "Residents' Rights for People in Long-Term Care Facilities" brochure: "This brochure is appropriate for nursing homes and assisted living." That brochure (src-4) says: "The facility can force you to leave because: …you have not paid your bill, …you are dangerous to yourself or others, …your medical needs cannot be met, or …the facility closes." So the IDoA does publish grounds that it says apply to assisted living, and the four reasons are not "for nursing homes" only. |
| Detailed criteria appear to be in the Illinois Administrative Code, published on the General Assembly site | holds if `idph_al_div` is cited (currently uncited) | src-5 (IDPH Assisted Living page), under "Laws & Rules": "Assisted Living and Shared Housing - 295 Administrative Code", linked to ilga.gov |
| "IDPH regulates under a separate licence from nursing homes, with its own 30-day notice rule" | **does not hold as sourced** | None of the cited pages says this. src-5 says only: "The Division of Assisted Living is responsible for all state licensure and survey processes for Assisted Living and Shared Housing establishments." The 30-day rule is on src-1. |
| IDoA rights page: residents keep certain rights, protections and privileges under Illinois and federal law | holds | src-2: "Care facility residents are guaranteed certain rights, protections, and privileges under Illinois and Federal law." |
| Ombudsman Program reachable through the Senior HelpLine 1-800-252-8966 (711 TRS) | **number holds; attribution to the cited page does not** | src-3 (the cited contact page) lists direct office numbers. The HelpLine appears only in its site header. src-6 says: "How to contact an Ombudsman: Call the Illinois Department on Aging Senior Helpline", and its header gives "Senior HelpLine: 1-800-252-8966 (711 TRS)". src-4 says: "Contact the Illinois Department on Aging for help regarding your involuntary discharge notice. Call 1-800-252-8966." |
| Ombudsman "can advocate for your parent during an appeal, not only after one has already gone wrong" | **does not hold as worded** | src-6 lists "Involuntary transfers or discharges" under "When you should contact an Ombudsman", and says "Long-Term Care Ombudsmen make every reasonable effort to assist, empower, represent and intervene on behalf of the resident." It says nothing specific about appeals. |
| "An elder law attorney can also review the notice against the current regulations directly." | unsupported (generic legal suggestion; no source) | No fetched page mentions an elder law attorney. src-1 p.2 says only that the facility must be represented by counsel at hearings. |
| "Only through a formal process — not simply by being asked to leave." | holds (fair summary of src-1) | src-1 notice and appeal process |

## Link check

The page links internally to /guides/illinois-nursing-home-resident-rights/, /guides/illinois-care-facility-complaint/, /guides/assisted-living-cost-illinois/, /guides/does-medicare-pay-for-senior-care/ and /guides/illinois-supportive-living-program/, plus /, /#assessment, /#paying-nav and /guides/. All five guide slugs are present in /tmp/site/build-guides.py (live on main). No links go to draft-only guides.

## Rule checks

- Ranking or recommending communities: none.
- Westminster Place: no price or claim in the guide body. The only mentions are the standard site-wide author disclosure in the JSON-LD and footer.
- Marketing urgency: none. "Filing on time matters" is a factual reference to the 10-day deadline. The bridge and CTA are the standard two routes.
- Source hosts: all citations are on dph.illinois.gov or ilaging.illinois.gov (allowed).
- Unverified legal claims: the added "timely appeal" condition, the "could not find" claim (contradicted), the "separate licence" sentence, the ombudsman "during an appeal" sentence and the elder-law-attorney sentence. All are covered by the corrections below.

## Required corrections

1. **Added condition on the right to remain (answer).**
   - Current: `establishment until a decision is rendered&rdquo; on a timely appeal.`
   - Replace with: `establishment until a decision is rendered.&rdquo;`
   - Source: src-1, "The resident has the right to continue to reside in the establishment until a decision is rendered."

2. **Added condition on the right to remain (body).**
   - Current: `An appeal filed within the 10-day window does not just register a complaint &mdash; it keeps your parent in place while IDPH decides.`
   - Replace with: `The form does not say what happens to a request sent after the 10 days, so do not let the deadline pass.`
   - Alternative: cut the sentence.
   - Source: src-1, "The resident has the right to continue to reside in the establishment until a decision is rendered." The 10-day deadline (src-1 p.3) is not linked to this right on any page.

3. **"Could not confirm" sentence in the answer is contradicted.**
   - Current: `This guide could not confirm, from a government page it could read and cite, the specific list of situations that legally justify a termination &mdash; see below for why, and who to ask.`
   - Replace with: `The Illinois Department on Aging&rsquo;s residents&rsquo; rights brochure, which it says is &ldquo;appropriate for nursing homes and assisted living&rdquo;, lists four reasons a facility can make a resident leave &mdash; see below.`
   - Add `idoa_resident_rights_brochure` to `sources`.
   - Source: src-2, "This brochure is appropriate for nursing homes and assisted living." src-4, "The facility can force you to leave because: …you have not paid your bill, …you are dangerous to yourself or others, …your medical needs cannot be met, or …the facility closes."

4. **"What this guide could not verify" section (first paragraph) is contradicted.**
   - Current: the whole paragraph beginning `The question families actually ask is broader than notice periods` and ending `so this guide will not quote criteria it read there.`
   - Replace with a paragraph that says:
     - The IDoA's "Residents' Rights for People in Long-Term Care Facilities" brochure, which the IDoA's residents' rights page describes as "appropriate for nursing homes and assisted living", says a facility "can force you to leave" because the bill has not been paid, the resident is dangerous to themselves or others, their medical needs cannot be met, or the facility closes.
     - The full assisted living rules are in Part 295 of the Illinois Administrative Code, which IDPH's Assisted Living page links to on the General Assembly's site.
   - Retitle the section, for example "What reasons can be given".
   - Cite `idoa_resident_rights_brochure` and `idph_al_div`.
   - Sources: src-2 and src-4 as in correction 3. src-5, "Assisted Living and Shared Housing - 295 Administrative Code".

5. **The four reasons are mislabelled as nursing-home-only ("Where this fits" section).**
   - Current: `which IDPH regulates under a separate licence from nursing homes, with its own 30-day notice rule. For the parallel protections Illinois sets out for nursing homes &mdash; including the four stated reasons a nursing home may discharge a resident &mdash; see`
   - Replace with: `which IDPH&rsquo;s Division of Assisted Living licenses, and whose notice and appeal forms are the ones described above. For the wider set of residents&rsquo; rights Illinois publishes for nursing homes and other care facilities, see`
   - Cite `idph_al_div`.
   - Source: src-5, "The Division of Assisted Living is responsible for all state licensure and survey processes for Assisted Living and Shared Housing establishments." src-2 as in correction 3.

6. **The form does not say a reason is mandatory.**
   - Current: `IDPH's form does not leave that blank or optional &mdash; a reason has to be stated in writing, on the notice your parent or their representative receives.`
   - Replace with: `The Department on Aging&rsquo;s residents&rsquo; rights brochure adds that the written notice must include why the resident is being asked to move.`
   - Cite `idoa_resident_rights_brochure`.
   - Source: src-4, "This notice must include: …why you are being asked to move".

7. **"Staff person" and the added interpretation.**
   - Current: `requires the establishment to name a specific staff person who will assist with relocation, so a family is not left to figure out logistics with no one assigned to help.`
   - Replace with: `has a line naming the person at the establishment who will assist with relocation.`
   - Source: src-1, "The person at the establishment who will assist with relocation is: Name of Person".

8. **Ombudsman HelpLine attribution and the "during an appeal" claim.**
   - Current: `is reachable through the <strong>Senior HelpLine at 1-800-252-8966 (711 TRS)</strong>, and can advocate for your parent during an appeal, not only after one has already gone wrong.`
   - Replace with: `is reached by calling the Department on Aging&rsquo;s <strong>Senior HelpLine at 1-800-252-8966 (711 TRS)</strong>, and the Department lists involuntary transfers or discharges among the reasons to contact an ombudsman.`
   - Add `idoa_ombudsman` to `sources`.
   - Source: src-6, "How to contact an Ombudsman: Call the Illinois Department on Aging Senior Helpline", "Senior HelpLine: 1-800-252-8966 (711 TRS)" and "When you should contact an Ombudsman … Involuntary transfers or discharges." src-4, "Contact the Illinois Department on Aging for help regarding your involuntary discharge notice. Call 1-800-252-8966."

9. **Unsourced legal suggestion.**
   - Current: `An elder law attorney can also review the notice against the current regulations directly.`
   - Replace with: nothing (cut it).
   - Source: no fetched page supports it.

10. **Desc and card blurb (consistency check).** These are accurate as written and need no change. Once the answer is changed, confirm that nothing in `desc` or the hub blurb still says the grounds could not be found.

Verdict: publish-ready after corrections

Corrections applied: drafts 3c7bc75, 2026-11-23 (all nine; ESCG worker ACQ-044).
