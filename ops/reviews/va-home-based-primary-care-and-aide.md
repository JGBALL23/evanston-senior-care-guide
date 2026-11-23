# Review packet: va-home-based-primary-care-and-aide

- Date: 2026-11-23
- Reviewer: ESCG worker (session cse_014eaiSbQh9aYSa5vTbwv5wK)
- Draft: `GUIDES` entry `"slug": "va-home-based-primary-care-and-aide"` in /tmp/drafts/build-guides.py (reviewed date in draft: 2026-11-13); rendered page /tmp/drafts/_dist/guides/va-home-based-primary-care-and-aide/index.html

## Sources fetched

Cited sources (the guide's `srcs(...)`):

| # | URL | HTTP | Local text | Page's own "Last updated" |
|---|-----|------|-----------|---------------------------|
| 1 | https://www.va.gov/geriatrics/pages/Home_Based_Primary_Care.asp (`va_hbpc`) | 200 | /tmp/reviews/src-va-1.txt | June 3, 2025 |
| 2 | https://www.va.gov/geriatrics/pages/Homemaker_and_Home_Health_Aide_Care.asp (`va_hhha`) | 200 | /tmp/reviews/src-va-2.txt | **November 16, 2026** (after the draft's reviewed date of 2026-11-13) |
| 3 | https://www.va.gov/geriatrics/pages/VA_Long_Term_Care_Services.asp (`va_ltc_overview`) | 200 | /tmp/reviews/src-va-3.txt | February 7, 2025 |

Fetched to check claims the guide makes without citing a source, and its "could not find" sentences:

| # | URL | HTTP | Local text |
|---|-----|------|-----------|
| 4 | https://www.va.gov/geriatrics/pages/veteran-directed_care.asp (`va_vdc`) | 200 | /tmp/reviews/src-va-4.txt |
| 5 | https://www.va.gov/resources/how-are-the-2-va-caregiver-support-programs-different/ (`va_caregiver_compare`) | 200 | /tmp/reviews/src-va-5.txt |
| 6 | https://www.va.gov/vhapublications/ViewPublication.asp?pub_ID=11687 (VHA Notice 2024-01, Purchased Home and Community-Based Services Programs, 12 Feb 2024; PDF, linked from source 2 as "Purchased Home & Community Based Services Programs Notice") | 200 | /tmp/reviews/src-va-6.txt (pdftotext -layout) |
| 7 | https://www.va.gov/geriatrics/pages/Home_and_Community_Based_Services.asp | 200 | /tmp/reviews/src-va-7.txt (index of services only) |

WebSearch was run twice (va.gov only): on the "eligible for community care" difference and on how the home programmes combine. Both searches led to source 6 and source 2.

## Quote audit

Checked by script (/tmp/claude-0/-home-user-evanston-senior-care-guide/222b6e4e-5d6f-597f-abd0-c621f2f4c577/scratchpad/qa.py) against the rendered page. Before matching, the script normalised whitespace, case, curly vs straight quotes and trailing punctuation. I then checked every miss by eye. **13 quotations, 9 matched, 4 not matched.**

| Quote (≤80 chars) | Source | Match |
|---|---|---|
| Services at Home and in the Community | 3 | yes |
| all enrolled Veterans | 3 (also 1, 2) | yes |
| health care services provided to Veterans in their home | 1 | yes |
| ongoing illnesses that affect their health and daily activities | 1 | **no**. Page: "ongoing diseases and illnesses that affect their health and daily activities" |
| similar to a VA clinic visit | 1 | **no**. Page: "(the same as if you went to a VA clinic)" |
| All enrolled Veterans are eligible for Homemaker Home Health Aide Care | 2 | yes |
| of any age | 2 | yes |
| self-care and daily activities | 2 | **no**. Page: "help the Veteran take care of themselves and their daily activities". "self-care" does not appear |
| Services are based on your assessed needs | 2 | yes |
| as long as extra help is needed | 2 | **no**. Page: "for as long as you need extra help with your daily activities" |
| may be charged based on your VA service-connected disability status | 2 (also 1) | yes |
| eligible for community care | 2 | yes |
| talk with a VA social worker to find out what specific help you may be able to receive | 2 | yes |

## Claim checks

| Claim (draft) | Result | Source's own wording |
|---|---|---|
| HBPC sends a VA medical team "led by a doctor, nurse practitioner or physician assistant" (answer box) | **does not hold**: the page never says who leads the team | 1: "HBPC provides a team of experienced health care professionals… Primary care visits at home by a physician, nurse practitioner, or physician's assistant" |
| HHHA sends a trained aide, supervised by an RN, for daily activities such as bathing, dressing and grocery shopping | holds | 2: "a trained person who can come to a Veterans home…"; "supervised by a registered nurse"; list includes Bathing, Getting dressed, Grocery Shopping |
| "VA.gov states the same basic gate for each": enrolled, clinical need, available (answer box) | **does not hold**: HHHA has a fourth condition | 2: "All enrolled Veterans are eligible for Homemaker Home Health Aide Care If they are eligible for community care and meet the clinical criteria…"; 1: "all enrolled Veterans are eligible IF they meet the clinical need for the service and it is available" |
| Overview lists five services under "Services at Home and in the Community" for all enrolled veterans with clinical need and local availability | holds | 3: "All enrolled Veterans are eligible for these services. However, to get the service you must have a clinical need for it, and the service must be available in your location." The five items match |
| "That overview page names two of them without describing what either involves" | **does not hold**: the overview names HHHA but does not list Home Based Primary Care at all | 3: list = Geriatric Evaluation, Adult Day Health Care, Homemaker and Home Health Aide Care, Respite Care, Skilled Home Health Care |
| HBPC: a veteran does not have to be homebound; it also serves veterans who are isolated or whose caregiver is under strain | holds | 1: "often homebound, but that is not required"; "also for Veterans who are isolated, or their caregiver is experiencing burden" |
| HBPC team reviews needs and cares for the veteran and the caregiver; services list | holds | 1: "review the Veterans health care needs and offer treatments and support for the Veteran and his/her caregivers"; list matches |
| HBPC copay may apply to each in-home visit, based on SC status and financial information; no dollar figure | holds (but see quote miss) | 1: "You may have a basic copay each time a VA staff team member comes to your home for a medical visit" |
| HBPC page points to a social worker or case manager and VA Form 10-10EC | holds as stated. The page gives the purpose of the form, which the draft omits | 1: "Contact your VA social worker/case manager to complete the Application for Extended Care Benefits (VA Form 10-10EC) to learn the amount of your copay." |
| "For Home Based Primary Care, that conversation runs through the Application for Extended Care Benefits, VA Form 10-10EC" (How to start) | **does not hold**: the page names the form only for working out the copay, not as the way to start HBPC | 1: as above; availability: "Your VA physician or social worker can tell you if a Home Based Primary Care program is available in your area." |
| HHHA eligibility: enrolled + community care + clinical criteria + availability | holds | 2: see above; "Services may vary by location." |
| HHHA serves veterans of any age, isolated, caregiver under strain | holds | 2: "can serve Veterans of any age"; "isolated, or their caregiver is experiencing burden" |
| Aide is not a nurse; supervised by an RN; list of daily activities | holds | 2: "Homemakers and Home Health Aides are not nurses, but they are supervised by a registered nurse"; Eating, Getting dressed, Personal grooming, Bathing, Using the bathroom, Moving from one place to another, Grocery Shopping |
| Visit schedule from several times a week to occasionally | holds (the page gives this as an example) | 2: "For example, an aide may be able to come to your house several times a week or just once in a while." |
| HHHA copay may be charged, no dollar figure | holds | 2: "A copay for Homemaker and Home Health Aide services may be charged based on your VA service-connected disability status." |
| Aide works for an organisation that holds a contract with VA | holds | 2: "Homemaker Home Health Aides work for an organization that has a contract with VA." |
| Both pages make availability depend on location and point to a social worker or physician | holds | 1: "Your VA physician or social worker can tell you…"; 2: "Services may vary by location." / "your VA social worker can help you make arrangements" |
| "Both pages come back to the same three conditions" / "The same gate, worded slightly differently each time" | **does not hold**: HHHA has the extra community-care condition, and VA policy explains it (next row) | 2 and 1 as above |
| "This guide did not find a VA.gov page stating whether that is a meaningful legal distinction or simply different drafting…" (could-not-find) | **does not hold**: VHA Notice 2024-01, linked from the HHHA page itself, states it. HHHA is a purchased (community-provider) service, and HBPC visits are by VA staff (source 1: "VA staff team member") | 6: "To receive PHCBS care, Veterans must satisfy one of the eligibility criteria for the Veterans Community Care Program established by the VA MISSION Act of 2018"; 6 lists "Homemaker/Home Health Aide (H/HHA)" among the PHCBS programs |
| "Families researching VA help at home often land on…" | **does not hold**: the frequency "often" has no source (ROUTINE bars it) | none |
| Veteran Directed Care gives the veteran a budget and lets them hire their own worker, including a family member | holds against source 4, but source 4 is not in this guide's Sources | 4: "Veterans in this program are given a budget for services…"; "hiring workers (which might include their own family member or neighbor)" |
| "the VA caregiver programmes pay and support the family member doing the caring" | **does not hold** as written: only PCAFC pays a stipend. PGCSS gives support without one. No caregiver source is cited | 5: PCAFC: "A monthly stipend (payment)."; "Family caregivers of Veterans who aren't eligible for this program may still be able to get support and resources through the Program of General Caregiver Support Services (PGCSS)." |
| "this guide found no VA.gov page describing how they interact" (could-not-find) | **does not hold**: both cited pages say the services can be combined, and VHA Notice 2024-01 §7 covers concurrent services | 1: "Home Based Primary Care can be used in combination with other Home and Community Based Services."; 2: "Homemaker and Home Health Aide services can be used in combination with other Home and Community Based Services."; 6 §7 "CONCURRENT SERVICES AND DUPLICATION OF SERVICES" |
| Neither page gives a dollar copay, a typical visit frequency, or a maximum number of aide hours | holds for sources 1 and 2. Note: source 6 sets a cost ceiling ("may not exceed 65 percent of the annual cost per patient in a VA Community Living Center") but no hours figure | 1, 2 |
| Amount of help set by individual clinical assessment | holds for HHHA; HBPC only says the team reviews needs | 2: "Services are based on your assessed needs." |
| Veteran Decision Aid and Caregiver Self-Assessment | holds | 2 (and 1): "Veteran Decision Aid for Care at Home or in the Community"; "Caregiver Self-Assessment" |
| A veteran must be enrolled in VA health care before either programme applies | holds | 3: "Veterans must be enrolled in VA health care before applying for VA long term care services" |
| Live VDC guide sets out the ways to apply for VA health care | holds | /tmp/site/build-guides.py VDC entry: "VA.gov lists four ways to apply for VA health care…" |
| Aid and Attendance is a cash pension benefit, separate from everything on this page | holds against the live A&A guide; consistent with 6 §7a: "The receipt of Aid and Attendance is not to be considered when ordering or authorizing PHCBS services" | 6 |
| Programme names (Home Based Primary Care, Homemaker and Home Health Aide Care, VA Form 10-10EC, Application for Extended Care Benefits) | holds | 1, 2 |
| Phone numbers, rates, dollar figures | none in the guide | n/a |
| Assessment promise ("no name, no email and no phone number… never leave your device") | holds (fixed site wording, unchanged) | ROUTINE |

## Link check

The draft uses these internal guide links, and each one is live on main (/tmp/site/build-guides.py):
- /guides/va-veteran-directed-care-program/: live
- /guides/va-caregiver-support-program/: live
- /guides/va-aid-and-attendance-benefit/: live. The link text matches the live h1 "Does the VA pay for senior care? Aid and Attendance, explained"
- /guides/va-nursing-home-and-respite-care/: live. The link text matches the live h1 "Can the VA provide nursing home care, or give a family caregiver a break?"
- Auto-generated related links on the rendered page (/guides/assisted-living-cost-illinois/, /guides/does-medicare-pay-for-senior-care/, /guides/illinois-supportive-living-program/): live
- /, /#assessment, /#paying-nav, /guides/, /privacy.html: site pages

No links to draft-only guides. All three external source links returned 200.

## Rule checks

- Ranking or recommending communities: none.
- Westminster Place prices or claims: none.
- Marketing urgency: none.
- Allowed citation hosts: all three sources are on va.gov. Pass.
- Unverified benefits claims: the answer box's "same basic gate" and "led by a doctor…", the "pay and support" line about caregiver programmes, the 10-10EC framing and two could-not-find sentences are unsupported or contradicted. Corrections C5 to C11 below fix them.
- Frequencies: "often land on" has no source (C8).
- Uncited claims: the Veteran Directed Care and caregiver-programme statements have no source in this guide's Sources block (C12).
- Freshness: the HHHA page was updated 16 Nov 2026, after the draft's reviewed date of 2026-11-13. The four quote misses may come from an earlier version. Either way, they are not on the live page (C13).

## Required corrections

**C1. Quote not on page (HBPC section)**
- Current: `aimed at veterans with &ldquo;ongoing illnesses that affect their health and daily activities&rdquo;.`
- Replace: `aimed at veterans who need team-based in-home support for &ldquo;ongoing diseases and illnesses that affect their health and daily activities&rdquo;.`
- Source (1): "The program is for Veterans who need team based in-home support for ongoing diseases and illnesses that affect their health and daily activities."

**C2. Quote not on page (HBPC cost)**
- Current: `a copay may apply to each in-home visit, &ldquo;similar to a VA clinic visit&rdquo;, based on…`
- Replace: `a basic copay may apply each time a VA staff team member comes to the home for a medical visit, &ldquo;the same as if you went to a VA clinic&rdquo;, based on…`
- Source (1): "You may have a basic copay each time a VA staff team member comes to your home for a medical visit (the same as if you went to a VA clinic)."

**C3. Quote not on page (HHHA section)**
- Current: `who comes to help with &ldquo;self-care and daily activities&rdquo;: eating,`
- Replace: `who comes to help the veteran &ldquo;take care of themselves and their daily activities&rdquo;: eating,`
- Source (2): "a trained person who can come to a Veterans home and help the Veteran take care of themselves and their daily activities."

**C4. Quote not on page (HHHA section)**
- Current: `continuing &ldquo;as long as extra help is needed&rdquo;.`
- Replace: `continuing &ldquo;for as long as you need extra help with your daily activities&rdquo;.`
- Source (2): "You can continue to receive an aide's services for as long as you need extra help with your daily activities."

**C5. Answer box: added condition and wrong gate**
- Current: `sends a VA medical team, led by a doctor, nurse practitioner or physician assistant, to provide primary care in the veteran's own home.`
- Replace: `sends a VA team of health care professionals to the veteran's own home, including primary care visits by a physician, nurse practitioner or physician assistant.`
- Source (1): "HBPC provides a team of experienced health care professionals… Primary care visits at home by a physician, nurse practitioner, or physician's assistant"
- Current: `VA.gov states the same basic gate for each: the veteran must be enrolled in VA health care, meet the clinical need for the service, and the service must actually be available where they live.`
- Replace: `For both, the veteran must be enrolled in VA health care, meet the clinical need or criteria for the service, and the service must be available. The aide programme adds one more condition: the veteran must also be eligible for community care.`
- Sources: (1) "all enrolled Veterans are eligible IF they meet the clinical need for the service and it is available"; (2) "All enrolled Veterans are eligible for Homemaker Home Health Aide Care If they are eligible for community care and meet the clinical criteria for the service and it is available."

**C6. Overview misdescribed (section "Two different kinds of help, not one")**
- Current: `That overview page names two of them without describing what either involves beyond its title.`
- Replace: `That overview page names Homemaker and Home Health Aide Care without describing it, and does not list Home Based Primary Care at all.`
- Source (3): "Services in the VA Standard Benefits Package include: Geriatric Evaluation… Adult Day Health Care, Homemaker and Home Health Aide Care, Respite Care, Skilled Home Health Care". HBPC is absent.

**C7. Gate section: wrong "same three conditions" framing and refuted could-not-find**
- Current heading: `The same gate, worded slightly differently each time`. Replace: `Similar gates, with one real difference`.
- Current: `Both pages come back to the same three conditions: enrollment in VA health care, a clinical need for the specific service, and local availability.`
- Replace: `Both pages require enrollment in VA health care, a clinical need for the specific service, and local availability; the aide page adds a fourth condition.`
- Current: `This guide did not find a VA.gov page stating whether that is a meaningful legal distinction or simply different drafting between two pages written at different times. Ask the VA social worker handling the case which gate actually applies, rather than assuming the two programmes are gated identically because this guide treats them side by side.`
- Replace: `VA's own policy notice on purchased home and community-based services, linked from the aide page, explains it. Homemaker and home health aide care is one of the services VA buys from outside providers, and &ldquo;To receive PHCBS care, Veterans must satisfy one of the eligibility criteria for the Veterans Community Care Program established by the VA MISSION Act of 2018&rdquo;. Home Based Primary Care visits are made by VA's own staff. Ask the VA social worker handling the case whether the veteran meets the community care criteria.` Add VHA Notice 2024-01 (https://www.va.gov/vhapublications/ViewPublication.asp?pub_ID=11687) to SRC and to this guide's Sources.
- Sources: (6) "To receive PHCBS care, Veterans must satisfy one of the eligibility criteria for the Veterans Community Care Program established by the VA MISSION Act of 2018"; (6) "(2) Homemaker/Home Health Aide. Homemaker/Home Health Aide (H/HHA) is a personal care services (PCS)…"; (1) "each time a VA staff team member comes to your home".

**C8. Unsupported frequency**
- Current: `Families researching VA help at home often land on one of two other programmes this site covers separately,`
- Replace: `Two other VA programmes, covered separately on this site, also involve help at home,`
- Source: none states a frequency (ROUTINE: no "often").

**C9. Caregiver programmes: not all pay**
- Current: `the VA caregiver programmes</a> pay and support the family member doing the caring, not an outside aide or clinician visiting the veteran.`
- Replace: `the VA caregiver programmes</a> support the family member doing the caring, and one of them, the Program of Comprehensive Assistance for Family Caregivers, pays an eligible family caregiver a monthly stipend. Neither involves an outside aide or clinician visiting the veteran.`
- Source (5): "A monthly stipend (payment)." (under PCAFC); "Family caregivers of Veterans who aren't eligible for this program may still be able to get support and resources through the Program of General Caregiver Support Services (PGCSS)."

**C10. Refuted could-not-find on interaction**
- Current: `A veteran parent's household could in principle touch more than one of these at once; this guide found no VA.gov page describing how they interact, and will not guess at it.`
- Replace: `Both VA pages say their service &ldquo;can be used in combination with other Home and Community Based Services&rdquo;. Ask the VA social worker which combination fits the veteran's assessed needs.`
- Sources: (1) "Home Based Primary Care can be used in combination with other Home and Community Based Services."; (2) "Homemaker and Home Health Aide services can be used in combination with other Home and Community Based Services."

**C11. 10-10EC framing (How to start)**
- Current: `For Home Based Primary Care, that conversation runs through the Application for Extended Care Benefits, VA Form 10-10EC.`
- Replace: `For Home Based Primary Care, the page says the social worker or case manager will help complete the Application for Extended Care Benefits, VA Form 10-10EC, to learn the amount of the copay, and that a VA physician or social worker can say whether the programme is available locally.`
- Source (1): "Contact your VA social worker/case manager to complete the Application for Extended Care Benefits (VA Form 10-10EC) to learn the amount of your copay." / "Your VA physician or social worker can tell you if a Home Based Primary Care program is available in your area."
- Also align the HBPC section sentence `It points families toward a VA social worker or case manager and the Application for Extended Care Benefits, VA Form 10-10EC, rather than describing a separate HBPC application of its own.` so that it adds "…VA Form 10-10EC, to learn the amount of the copay".

**C12. Uncited claims about other programmes**
- Current: `"sources": srcs("va_hbpc", "va_hhha", "va_ltc_overview"),`
- Replace: `"sources": srcs("va_hbpc", "va_hhha", "va_ltc_overview", "va_vdc", "va_caregiver_compare", <new key for VHA Notice 2024-01>),`
- Source (4): "Veterans in this program are given a budget for services…"; "hiring workers (which might include their own family member or neighbor)"; source 5 as in C9.

**C13. Reviewed date**
- Current: `"reviewed": "2026-11-13",`
- Replace: the date these corrections are applied and re-checked against the live pages. Source 2 shows "Last updated November 16, 2026", which is after the current reviewed date.

Verdict: publish-ready after corrections
