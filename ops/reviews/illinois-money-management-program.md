# Review packet: illinois-money-management-program

- Date: 2026-11-23
- Reviewer: ESCG worker (session cse_014eaiSbQh9aYSa5vTbwv5wK)
- Draft: GUIDES entry `illinois-money-management-program` in /tmp/drafts/build-guides.py (rendered: /tmp/drafts/_dist/guides/illinois-money-management-program/index.html)

## Sources fetched

| # | URL | Status | Local copy |
|---|-----|--------|-----------|
| 1 | https://ilaging.illinois.gov/programs/money-mgmt.html (cited: idoa_money_mgmt) | 200 | /tmp/reviews/src-mm-1.html, text src-mm-1.txt |
| 2 | https://ilaging.illinois.gov/content/dam/soi/en/web/aging/programs/documents/ivmmp-programsitelist.pdf (cited: idoa_money_mgmt_sites; footer "IVMMP Agency List – FY27- October 22, 2026") | 200 | src-mm-2.pdf / .txt |
| 3 | https://ilaging.illinois.gov/content/dam/soi/en/web/aging/resources/newsandpublications/publications/documents/ltc-resrights.pdf (NOT cited by the draft, but the draft quotes it; SRC key idoa_resident_rights_brochure exists) | 200 | src-mm-3.pdf / .txt |
| 4 | https://hfs.illinois.gov/content/dam/soi/en/web/hfs/sitecollectiondocuments/IDoA%20-%20IVMMP.MCO%20policy%2001.01.18.pdf (checked for "could not find" claims only) | 200 | src-mm-4.pdf / .txt |
| 5 | https://omb.illinois.gov/public/gata/csfa/Program.aspx?CSFA=1480 (CSFA 1480, IVMMP; checked for "could not find" claims only) | 200 | src-mm-5.html / .txt |

Web search run: "Illinois Volunteer Money Management Program fee cost volunteer background check complaint" (used only to find sources 4 and 5).

## Quote audit

Script: extracted every “…” from the rendered HTML, normalised whitespace, apostrophes and quote marks, and looked for each as a substring of each fetched source text. 15 quotes, 15 matched.

| Quote (≤80 chars) | Source | Match |
|---|---|---|
| a protective service that assists low-income older persons who have difficulty m… | 1 | yes |
| keeping track of banking records, intervening with creditors, completing medical… | 1 | yes |
| setting up a budget, writing checks, balancing a checkbook | 1 | yes |
| assisting with large purchases | 1 | yes |
| available to Community Care Program (CCP) participants | 1 | yes |
| individuals who have a substantiated Adult Protective Services (APS) case in cer… | 1 | yes |
| in certain areas of the State | 1 | yes |
| Local Program Sites, contracted by the Illinois Department on Aging, recruit, se… | 1 | yes |
| administers the program and monitors the local Program Sites | 1 | yes |
| organizing, reviewing, and paying bills | 1 | yes |
| Volunteers also serve as Representative Payees, persons designated by the Social… | 1 | yes |
| without your permission | 3 (brochure, not in the guide's Sources block) | yes, but the source is not cited |
| trained | 1 ("matches trained volunteers") | yes |
| monitors | 1 | yes |
| Find Your Local Program Site/Agency | 1 (link text on page) | yes |

## Claim checks

| Claim | Result | Source's own wording |
|---|---|---|
| Programme name "Volunteer Money Management Program" | holds | Page 1: "The Illinois Volunteer Money Management Demonstration Program is a protective service…". PDF: "Illinois Volunteer Money Management Program Site/Agency List". (The page calls it a "Demonstration" programme; the draft leaves that out. That is acceptable but worth noting.) |
| Two eligibility paths: CCP participants, or a substantiated APS case | holds | "This program is available to Community Care Program (CCP) participants and individuals who have a substantiated Adult Protective Services (APS) case in certain areas of the State." |
| Answer: "a parent already approved for the Community Care Program" | holds (close paraphrase of "participants") | "Community Care Program (CCP) participants" |
| Both paths are geographically limited | holds (supported by the page's county/township list) | "Expand Program Counties & Townships to View Counties Served" |
| Desc: "Illinois trains volunteers" | does not hold as worded | "Local Program Sites, contracted by the Illinois Department on Aging, recruit, select, train, match and monitor the volunteers." |
| "This sits below a Power of Attorney and short of a court guardianship. Nobody signs away legal authority to make this work" | does not hold: an unsupported legal claim. Neither source mentions POA, guardianship or legal authority, and a representative payee is an SSA designation | "persons designated by the Social Security Administration to manage the monthly benefits of certain beneficiaries" |
| "under a programme the state recruits, trains and monitors" | does not hold: the roles are inverted. Program Sites recruit, train and monitor volunteers; the department monitors the Program Sites | "Local Program Sites … recruit, select, train, match and monitor the volunteers. The Illinois Department on Aging administers the program and monitors the local Program Sites." |
| Link text "For what counts as a substantiated APS case, see [elder-abuse guide]" | does not hold: the live elder-abuse guide never uses the word "substantiated" (searched its source in /tmp/site/build-guides.py). It covers definitions and reporting | n/a |
| "operates through a fixed list of contracted Program Sites" | does not hold ("fixed" is added, and the draft later says "Program Site lists change") | "Local Program Sites, contracted by the Illinois Department on Aging" |
| Volunteers matched for "organizing, reviewing, and paying bills" | holds | "The program matches trained volunteers with older persons who need help with tasks such as organizing, reviewing, and paying bills" |
| Representative payee role | holds | "Volunteers also serve as Representative Payees…" |
| "a parent's Social Security or other federal benefit cheque" | does not hold ("other federal benefit" is added) | "persons designated by the Social Security Administration to manage the monthly benefits of certain beneficiaries" |
| Brochure: a facility may not take on the payee role "without your permission" | holds against source 3, but source 3 is missing from the guide's Sources block | "Your facility may not become your money manager nor your Social Security representative payee without your permission." |
| "this programme is a vetted, state-monitored way to fill that role with someone other than the facility, a stranger, or nobody at all" | does not hold: "vetted" and the "stranger / nobody at all" framing are not on any source; the state monitors Program Sites, not volunteers directly | "The Illinois Department on Aging administers the program and monitors the local Program Sites." |
| Page does not state cost to a family | holds for page 1 (no fee or cost text). Source 5 mentions only a provider "fee for service agreement", nothing charged to participants | "Once an applicant is approved as an IVMMP provider, a fee for service agreement will be executed." (source 5) |
| Page does not describe screening "beyond being &ldquo;trained&rdquo;" | does not hold as worded: the page also says Program Sites "select" volunteers | "recruit, select, train, match and monitor the volunteers" |
| Page does not explain what happens if a volunteer mishandles money | holds for page 1, which is the page the sentence names. Advisory: source 5 (omb.illinois.gov, an allowed host) says "Applicant agrees to obtain their own insurance to protect the participant funds." It could be cited if the author wants it; nothing must change | (page 1 silent) |
| PDF "organised by the state's Planning and Service Areas" | does not hold as worded: the PDF prints only "PSA 01", "PSA 13" etc. and never spells out the term | "PSA 13" |
| PDF dated 22 October 2026 | holds | "IVMMP Agency List – FY27- October 22, 2026" |
| PDF "lists two Program Sites covering parts of Chicago's suburbs: Kenneth W. Young Centers … Oak Park Township Senior Services" | does not hold: the PDF also lists DuPage County Senior Services (DuPage County) and Catholic Charities, Diocese of Joliet (Kankakee, Grundy and Will Counties), which are also Chicago suburbs. The two named sites are the PSA 13 entries | "PSA 13 / Kenneth W Young Centers … Elk Grove and Schaumburg Townships / Oak Park Township Senior Services … Oak Park and River Forest Townships" |
| Neither covers Evanston Township; no City of Chicago or rest-of-Cook listing | holds (PDF and page 1 county list: no Evanston, Chicago or other Cook townships) | page 1 list includes "Elk Grove Township", "Oak Park Township", "River Forest Township", "Schaumburg Township" and no others in Cook |
| Answer: "Its own current site list does not show a Program Site reaching Evanston Township" | holds | as above |
| Service Locator "built for Care Coordination Units rather than this programme specifically — may turn up a more current answer" | does not hold: speculative, and the page gives no basis for it. The page sends families to their CCU via the map tool | "To learn more about this program and find out if you are eligible, contact your local Care Coordination Unit (CCU) using our map tool." |
| Senior HelpLine 1-800-252-8966 (711 TRS) | holds (number printed on page 1 header) | "Senior HelpLine: 1-800-252-8966 (711 TRS)" |
| "Either [HelpLine or CCU] can tell you whether your parent's situation … qualifies" | does not hold for the HelpLine: the page names only the CCU for eligibility, and source 5 says CCUs determine IVMMP eligibility | "contact your local Care Coordination Unit (CCU) … find out if you are eligible"; source 5: "local Care Coordination Units (CCUs) who determine CCP and IVMMP eligibility" |
| "while your parent still lives independently" | does not hold (added condition; no source states it) | n/a |
| Note (no action): page 1's county list also names counties absent from the PDF (Clay, Edwards, Effingham, Fayette, Hamilton, Jefferson, Marion, Wabash, Wayne, White). The two official documents disagree, but neither includes Evanston, so the guide's conclusion is unaffected | n/a | n/a |

## Link check

Internal links in the rendered page, checked against /tmp/site/build-guides.py (main):
- /guides/illinois-advance-directive-power-of-attorney/: live
- /guides/illinois-community-care-program/: live
- /guides/illinois-elder-abuse-reporting/: live (but see the link-text correction below)
- /guides/levels-of-senior-care-explained/: live
- /guides/assisted-living-cost-illinois/, /guides/does-medicare-pay-for-senior-care/, /guides/illinois-supportive-living-program/ (related links): live

No links to draft-only guides. External citations are only on ilaging.illinois.gov, an allowed host.

## Rule checks

- Ranking or recommending communities: none.
- Westminster Place: not mentioned.
- Marketing urgency: none.
- Unverified legal or benefits claims: the POA/guardianship and "no legal authority" claim, "other federal benefit", "vetted", the HelpLine determining eligibility and "lives independently" are unsupported. All are covered by the corrections below.
- Every quotation is cited: fails for "without your permission" (brochure not in the Sources block).
- Bridge and CTA count: unchanged pattern (bridge plus closing assessment paragraph).
- No private individuals named in the guide. The PDF lists staff names, and the draft correctly omits them.

## Required corrections

1. **Desc.** Current: "Illinois trains volunteers to budget, pay bills and even act as a Social Security representative payee". Replacement: "Local agencies contracted by Illinois train volunteers to budget, pay bills and even act as a Social Security representative payee". Source: "Local Program Sites, contracted by the Illinois Department on Aging, recruit, select, train, match and monitor the volunteers."

2. **POA/guardianship paragraph.** Current: "This sits below <a …>a Power of Attorney</a> and short of a court guardianship. Nobody signs away legal authority to make this work &mdash; a trained volunteer simply does the paperwork your parent can no longer keep up with, under a programme the state recruits, trains and monitors." Replacement: "The department's page describes a service, not a legal arrangement, and says nothing about how it relates to <a href=\"/guides/illinois-advance-directive-power-of-attorney/\">a power of attorney</a> or a guardianship. Local Program Sites recruit, select, train, match and monitor the volunteers; the department administers the programme and monitors the Program Sites." Source: "Local Program Sites, contracted by the Illinois Department on Aging, recruit, select, train, match and monitor the volunteers. The Illinois Department on Aging administers the program and monitors the local Program Sites."

3. **Elder-abuse link text.** Current: "For what counts as a substantiated APS case, see". Replacement: "For what Adult Protective Services investigates and how to report, see". Basis: the linked live guide never defines or mentions "substantiated". It covers the APS definitions and reporting.

4. **"fixed list".** Current: "it operates through a fixed list of contracted Program Sites". Replacement: "it operates through contracted local Program Sites". Source: "Local Program Sites, contracted by the Illinois Department on Aging".

5. **Benefit type.** Current: "how a parent's Social Security or other federal benefit cheque gets managed". Replacement: "how a parent's Social Security benefit gets managed". Source: "persons designated by the Social Security Administration to manage the monthly benefits of certain beneficiaries."

6. **Brochure citation and "vetted".** Current sources: `srcs("idoa_money_mgmt", "idoa_money_mgmt_sites")`. Replacement: `srcs("idoa_money_mgmt", "idoa_money_mgmt_sites", "idoa_resident_rights_brochure")`. Brochure source: "Your facility may not become your money manager nor your Social Security representative payee without your permission." Also current: "this programme is a vetted, state-monitored way to fill that role with someone other than the facility, a stranger, or nobody at all." Replacement: "this programme is one way to have that role filled by a trained volunteer from a Program Site the department monitors." Source: "The program matches trained volunteers…"; "The Illinois Department on Aging administers the program and monitors the local Program Sites."

7. **Screening.** Current: "does not describe how a volunteer is screened beyond being &ldquo;trained&rdquo;". Replacement: "does not describe how a volunteer is screened beyond saying Program Sites &ldquo;recruit, select, train, match and monitor the volunteers&rdquo;". Source: the same sentence, matched word for word on page 1.

8. **PSA wording.** Current: "organised by the state's Planning and Service Areas". Replacement: "organised by numbered PSA". Source: the PDF prints only "PSA 01" … "PSA 13".

9. **Suburbs claim.** Current: "lists two Program Sites covering parts of Chicago's suburbs: Kenneth W. Young Centers for Elk Grove and Schaumburg Townships, and Oak Park Township Senior Services for Oak Park and River Forest Townships." Replacement: "lists two Program Sites under PSA 13: Kenneth W. Young Centers for Elk Grove and Schaumburg Townships, and Oak Park Township Senior Services for Oak Park and River Forest Townships." Source: "PSA 13 / Kenneth W Young Centers … Elk Grove and Schaumburg Townships / Oak Park Township Senior Services … Oak Park and River Forest Townships". The PDF also lists "DuPage County Senior Services … DuPage County" and "Catholic Charities, Diocese of Joliet … Kankakee, Grundy and Will Counties".

10. **Service Locator speculation.** Current: "Program Site lists change, and the department's Service Locator tool &mdash; built for Care Coordination Units rather than this programme specifically &mdash; may turn up a more current answer than this guide's single reading of one document." Replacement: "Program Site lists change, and the department's page itself tells families to contact their local Care Coordination Unit, found with its map tool, to find out if they are eligible." Source: "To learn more about this program and find out if you are eligible, contact your local Care Coordination Unit (CCU) using our map tool."

11. **Who decides eligibility.** Current: "Start with the Senior HelpLine at <strong>1-800-252-8966 (711 TRS)</strong>, or a local Care Coordination Unit found through the department's online Service Locator. Either can tell you whether your parent's situation &mdash; already on CCP, or with a substantiated APS case &mdash; qualifies, and whether a Program Site actually reaches where your parent lives, before you assume either answer yourself." Replacement: "Start with your parent's local Care Coordination Unit, found through the department's map tool: the department's page says to contact it to learn more about this programme and find out if you are eligible &mdash; already on CCP, or with a substantiated APS case &mdash; and whether a Program Site reaches where your parent lives. The department's Senior HelpLine is <strong>1-800-252-8966 (711 TRS)</strong>." Source: "To learn more about this program and find out if you are eligible, contact your local Care Coordination Unit (CCU) using our map tool." and "Senior HelpLine: 1-800-252-8966 (711 TRS)".

12. **Added condition.** Current: "bills going unpaid or a benefit cheque with nobody to manage it, while your parent still lives independently." Replacement: "bills going unpaid or a benefit cheque with nobody to manage it." Basis: no source limits the programme to people living independently.

Verdict: publish-ready after corrections

Corrections applied: drafts 4f57bd8, 2026-11-23 (all twelve; correction 11 reworded slightly so the eligibility clause reads as a question to ask the CCU; 15/15 quotations re-matched; ESCG worker ACQ-049).
