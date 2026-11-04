# Evanston Senior Care Guide: Project Control Center

**The single source of truth for site development and organic SEO. Read it before proposing work.**

| | |
|---|---|
| Last verified | 2026-11-03 14:57 Chicago (20:57 UTC), read-only |
| Checked against | GitHub, Netlify, the live site, Search Console emails, owner-reported Search Console figures |
| This document | `DRAFT` on `feature/project-control-center`. Not merged. Not approved. |

**Labels.** `VERIFIED`: checked at the source on the date shown. `OWNER-REPORTED`: read by the owner, not independently checked. `HISTORICAL`: true for its date, not current. `APPROVED`: the owner said yes, on the date shown. `RECOMMENDED`: proposed, not approved.

## Operating rules

1. **Before proposing work,** read this file and check whether the task was already completed, attempted, rejected or deferred (Sections 5 and 6).
2. **Closed decisions stay closed** without new evidence. Name the evidence when reopening one.
3. **One primary SEO improvement at a time** (Section 4).
4. **Verify before writing.** Facts come from GitHub, Netlify or the live site. Search Console and business figures come only from the owner or a direct read, with a date and a source. Never estimate them. Never present a historical metric as current.
5. **Recommendations are not approvals.** Merges, deployments, IndexNow submissions, consent changes and changes to the drafts routine each need the owner's separate approval.
6. **Update this file** after every approved merge or deployment and after every scheduled SEO review.
7. **Append only.** Deployment History and the Decision Log are never edited or deleted. A correction is a new entry pointing to the old one.
8. **This repository is public.** Never record inquiry details, personal data or credentials here.

---

## 1. Current production state

### Production (`VERIFIED` 2026-11-03)

| Item | State |
|---|---|
| `main` | `4ce3249`, merge of PR #9, 2026-11-01 20:47 UTC |
| Production deploy | `6ae7a5a0661074563afe0c14`, published 2026-11-01 20:48:49 UTC, state `ready` |
| Does it match `main`? | Yes, by direct comparison. Netlify records no commit for upload deploys, so 32 public files were fetched from production and compared with `_dist` at `4ce3249`: 15 identical, 17 different only by Netlify's rewrite of `/privacy.html` links to `/privacy`. Beacon files under `/t/` were not fetched, to keep the counts clean. |
| On `main` but not live | Nothing a visitor can see |
| Rollback point | `6ae63476b0ea0ed172f267a5`, state `ready` |
| How deploys work | One approved upload of `_dist`, the functions and `netlify.toml`. There is no Git link: a push to GitHub publishes nothing, and `docs/` never reaches the site. |

### Published pages and systems (`VERIFIED` 2026-11-03)

| Area | Live state |
|---|---|
| Pages | Homepage (Simple First), `/guides/` index, 15 guides, privacy notice dated 1 November 2026. Sitemap: 18 URLs. |
| Assessment | Six questions. Result order: answer, costs, how to pay, optional Westminster Place inquiry. |
| Payment Navigator | Workflow #5, live. |
| Inquiry | Result-page form and direct tour inquiry (Workflow #4). `plan-visit` stores the record and notifies the operator; nothing reaches Westminster Place automatically. Consent version `2026-10-26d`. `GET /api/plan-visit` returns 405. |
| Records | `plan-visit-export` needs the owner's token (401 without it). `retention` and `retention-daily` delete records after 180 days; the daily job ran in the last 24 hours. All functions run on Node 24. |
| Measurement | First-party step files under `/t/`, counted from Netlify's request log. No cookie, no analytics service. Netlify RUM is off: live pages match `_dist`, so no script is injected. |
| Search basics | `robots.txt` allows everything except `/t/`. `www` and `.netlify.app` redirect (301) to the primary domain. |

<details>
<summary>The 15 published guides</summary>

`assisted-living-cost-illinois`, `check-illinois-inspection-records`, `does-medicare-pay-for-senior-care`, `illinois-care-facility-complaint`, `illinois-community-care-program`, `illinois-family-caregiver-support-program`, `illinois-medicaid-estate-recovery`, `illinois-medicaid-long-term-care`, `illinois-senior-health-insurance-program`, `illinois-supportive-living-program`, `independent-living-evanston`, `levels-of-senior-care-explained`, `medicare-hospice-benefit-explained`, `va-aid-and-attendance-benefit`, `va-veteran-directed-care-program`

</details>

### Live versus elsewhere (`VERIFIED` 2026-11-03)

| Where | What | Live? |
|---|---|---|
| Production and `main` | Everything above | Yes |
| [PR #10](https://github.com/JGBALL23/evanston-senior-care-guide/pull/10), head `bca3f0b` | Illinois Life Plan guide, related-link swaps, citation allowlist | No, URL returns 404 |
| `drafts`, head `f72ff6f` | 5 unpublished guides (Section 5) | No, all 5 URLs return 404 |
| Claude Docs memos | Research and recommendations | No |

`drafts` has diverged from `main` (12 commits ahead, 25 behind) and lacks PRs #6 to #9. Never merge it wholesale. Publish a guide through a release branch cut from `main`, as PR #5 did.

### Known unresolved issues

| # | Issue | Evidence | Status |
|---|---|---|---|
| U1 | **Nothing shows the inquiry chain working on the current release.** The last notification email is a test from 2026-10-22. Functions moved from Node 20 to Node 24 on 2026-10-30. | Netlify deploy records; notification inbox; [plan](../INQUIRY-E2E-TEST-PLAN.md) marked "Not executed" | One labeled test, needs separate approval |
| U2 | **No current Search Console data exists.** At the last reading, at most 6 of 18 sitemap pages were indexed. | Section 3 | Section 7 |
| U3 | **The Search Console review is partial.** Unread: Page indexing URL lists, Sitemaps report, Links report, queries for every page except the independent-living guide, and which page earned the one click. | Failure-focused audit, 2026-10-31 | Owner read needed |
| U4 | **IndexNow is behind.** Last submission 2026-10-28. All 16 tracked `/guides/` URLs have changed since, 3 of them were never submitted, and the homepage is not tracked at all. IndexNow reaches Bing, not Google. | `data/indexnow-ledger.json` compared with `_dist` | Needs separate approval |
| U5 | **Funnel counts expire after 24 hours.** Only hand-taken readings survive. | [Funnel baseline](../data/funnel-baseline.md) | Scheduled snapshot proposed, not approved |
| U6 | **A confirmed tour cannot be recorded yet.** A private ledger keyed by reference ID was proposed, not built. No Admissions hand-back exists. | Gap analysis, 2026-10-31 | Priority 3, not started |
| U7 | **`data/guide-queue.md` is out of date.** It says the routine is paused and lists the Life Plan guide as not yet written. The routine is enabled and picks its own topics, and the guide is in PR #10. | Scheduled-task record; file on `main` | Correct when approved |
| U8 | **Sitemap `lastmod` is stale.** No entry is later than 2026-10-29, although Netlify shows 17 pages changed on 31 October and 18 on 1 November. | `_dist/sitemap.xml`; deploy summaries | Ride-along fix, `RECOMMENDED` |
| U9 | **Minor:** `/privacy` and `/privacy.html` both return 200. Live links use the first; the canonical tag and sitemap use the second. | Live check | Negligible, audit 2026-10-31 |
| U10 | **Housekeeping:** two preview sites remain online (`esc-preview-d9ed1ac`, `esc-preview-simple-first`). Both are `noindex` and block crawlers. | Netlify; live headers | Owner may delete |

---

## 2. Our business objective

**Objective:** qualified Westminster Place tour inquiries through organic SEO. Traffic alone is not the goal.

**Geography:** Evanston-first, Illinois-supported. Evanston is the primary market. Illinois and federal programs, laws and costs support what Evanston families are told. "Illinois" is not blindly replaced with "Evanston".

**Method:** inversion + local specialization + organic SEO. Ask what would make each page fail, learn from successful competitors, start narrow, prove results, build authority, then expand.

**Funnel:** Helpful guides → Assessment → Optional Westminster Place inquiry → Confirmed tour

| Stage | What counts | Who can establish it |
|---|---|---|
| Helpful guide | A Search Console click, or a recorded `landed` event | Search Console; host log |
| Assessment | A recorded `assessment-completed` event. Answers are not stored. | Host log |
| Inquiry | A stored record with consent and a reference ID | Server record |
| Confirmed tour | Admissions confirms it by reference ID | Westminster Place only |

A click is not an inquiry. An inquiry is not a tour. A beacon is never a business result.

**Disclosures and consent that must stay accurate:**

- The site says its author works at Westminster Place, that it is not an official Westminster Place website, and that no referral fees are received.
- The Westminster Place inquiry stays optional. The assessment asks for no name, email or phone number.
- Consent is one required, unticked box. Its sentence and version change only with the owner's separate approval, and the privacy notice changes with them.
- The guide stays independent. It never ranks or compares Westminster Place against other communities.
- No claim that an inquiry became a tour without Admissions confirmation.

---

## 3. SEO performance baseline

> **No current Search Console reading exists.** Every Search Console figure below is `HISTORICAL` and predates the 31 October SEO release. Claude has no Search Console connection, so these figures are `OWNER-REPORTED`.

### Dated readings

| ID | Reported | Covers | Source |
|---|---|---|---|
| R1 | 2026-10-31 | First impressions (2026-10-21) to before the 31 October release. Exact end date not recorded. | Search Console Performance, owner |
| R2 | 2026-10-31 | Page indexing report. Date of the report's last update not recorded. | Search Console Page indexing, owner |
| R3 | 2026-11-01 | Same period as R1 | Search Console queries for the independent-living guide, owner |

### Performance by search type

| Type | Basis | Impressions | Clicks | CTR | Avg. position | Reading |
|---|---|---|---|---|---|---|
| All searches | Whole property | 289 | 1 | 0.35% (calculated) | 67.6 | R1 |
| Evanston/local | The 4 visible queries for the independent-living guide | 6 | 0 | 0% (calculated) | Not reported by query | R3 |
| Statewide | **Not separated.** Nearest proxy by page topic: inspection-records guide | 8 | Not reported | Unknown | 15.8 | R1 |
| National | **Not separated.** Nearest proxy by page topic: Medicare guide | 150 | Not reported | Unknown | 87.2 | R1 |

Only the Evanston row is based on actual queries. The statewide and national rows are classified by page topic because those queries are unread. Page rows and the whole-property row are counted differently, so they need not add up.

**Independent-living guide, whole page (R1):** 7 impressions, average position 41.1. It had been live for 5 days at most.

**Visible queries (R3):**

| Query | Impressions | Clicks |
|---|---|---|
| independent living communities evanston il | 3 | 0 |
| independent living in evanston | 1 | 0 |
| independent living evanston il | 1 | 0 |
| independent living community evanston il | 1 | 0 |

The seventh impression's query is withheld by Search Console.

### Indexing (R2)

| Status | URLs |
|---|---|
| Indexed | 6 |
| Page with redirect | 3 |
| Discovered, currently not indexed | 2 |
| Crawled, currently not indexed | 0 |

These 11 URLs do not account for the 18 sitemap URLs: the report also counts URLs outside the sitemap. At most 6 sitemap pages were indexed. The redirects are not assumed to be a problem.

### Dated events from Search Console emails (`VERIFIED`)

| Date | Event |
|---|---|
| 2026-10-18 | Domain property verified (email date) |
| 2026-10-21 | Google began collecting impressions (email of 2026-10-23) |
| 2026-10-25 | New indexing reason reported: "Page with redirect" (email date) |

### Google page-one check (`HISTORICAL`, not a Search Console metric)

2026-11-02, in the owner's Chrome, page one only: the site appeared on none of the 7 searches checked. Results vary by place, person and day. Source: Evanston-first memo.

### Funnel counts (`VERIFIED` from Netlify's request log)

Definitions are in the [funnel baseline](../data/funnel-baseline.md). These are recorded events, not people.

| Window (UTC) | `landed` | Assessment started / completed | Form views | `inquiry-submitted` |
|---|---|---|---|---|
| 2026-10-31 00:30 to 13:35 | 0 | 0 / 0 | 0 | 0 |
| 2026-11-02 20:57 to 2026-11-03 20:57 | 8 (all direct, 0 from Google) | 0 / 0 | 1 `plan-visit`, 1 `direct-inquiry` | 0 |

The second row is new in this document and is not yet in the funnel baseline file.

### Business outcomes

| Metric | State | Source and date |
|---|---|---|
| Stored inquiries | **Not read.** The export needs the owner's token. Exclude test records from any count. | 2026-11-03 |
| Inquiry notification emails | Tests only. The latest is from 2026-10-22, none since. | Notification inbox, checked 2026-11-03 |
| Confirmed tours | None recorded. No reporting process exists. | U6 |

**Not available and never to be estimated:** search volumes, keyword difficulty, conversion rates, local statistics, community prices.

**Review dates (`RECOMMENDED`, no scheduled task exists):** 4 weeks after the 31 October release is 2026-11-28; 8 weeks is 2026-12-26.

---

## 4. Active experiment

**None is running. No experiment has been approved.**

### Experiment 1: Evanston costs (`RECOMMENDED`, awaiting the owner)

| Field | Detail |
|---|---|
| Source | [Evanston-first memo](https://claude.ai/artifact/Tug4p2g1hKg7BXffcL1157), 2026-11-02 |
| Change | Rewrite only the "What this means in Evanston" section of `/guides/assisted-living-cost-illinois/`. The title, short answer, sources, disclosures, assessment and optional inquiry stay as they are. No community names or prices. |
| Hypothesis | Google's page one lacks a current, sourced, neutral answer on Evanston costs. A section explaining why published figures disagree, what the sourced figure is and is not, and how to read a quote will earn Evanston impressions and clicks for this page. |
| Baseline | **Not captured.** The page's indexing status and queries are unread. Record them before any change (Section 7). |
| Intended result | Impressions, average position and clicks rise for this page's queries containing "Evanston", compared with guides left unchanged. Stored inquiries are counted from server records. |
| Review date | 8 weeks after release. No release date exists yet. |
| Stop condition | If the page is not indexed, indexing comes first and the experiment waits. |

**Decision criteria at 8 weeks:**

| Result | Decision |
|---|---|
| No Evanston impressions | Stop. Check indexing and links. Write nothing more. |
| Impressions without clicks | Test the description, with separate approval. |
| Clicks without onward use | Revisit the next-step link. |
| Impressions and clicks | The inspection-records guide becomes Experiment 2. |

**Could change the order:** if the inspection guide's queries are local and the cost guide has none, swap the two.

**Overlap to account for:** the 31 October release is still inside its own review window. R1 is its baseline, and its 8-week mark is 2026-12-26.

---

## 5. Completed / In progress / Blocked

### Completed: merged PRs

| PR | Merged | Merge commit | Into | What | Live in |
|---|---|---|---|---|---|
| #1 | 2026-10-29 | `88ab7ba` | `drafts` | Workflow #5 Payment Navigator | Via #2 |
| #2 | 2026-10-29 | `d9ed1ac` | `main` | Workflow #5 and three guides | `6ae4a354` |
| #3 | 2026-10-29 | `9bcf253` | `drafts` | Sync of factual corrections | Not applicable |
| #4 | 2026-10-30 | `a87b1b5` | `drafts` | Simple First | Via #5 |
| #5 | 2026-10-30 | `e38d627` | `main` | Simple First release, guide 16 excluded | `6ae52797` |
| #6 | 2026-10-31 | `685c7c8` | `main` | Tagged test harnesses, retired beacons, funnel baseline | `6ae63476` |
| #7 | 2026-10-31 | `65e30a7` | `main` | Related guides by topic, crawlable homepage links, shorter metadata | `6ae63476` |
| #8 | 2026-10-31 | `c3bba2f` | `main` | Privacy notice corrections | `6ae63476` |
| #9 | 2026-11-01 | `4ce3249` | `main` | Inquiry disclosure wording | `6ae7a5a0` |

### Deployment History (append only)

Netlify records no commit for these deploys. The source commit comes from each approved release record.

| Published (UTC) | Deploy ID | Source | What shipped |
|---|---|---|---|
| 2026-10-28 14:17:49 | `6ae20405f331d561ae40cdc6` | `028447c` | Last deploy through `publish.py`, on Node 20 |
| 2026-10-30 14:02:11 | `6ae4a35428df7531ed6b6b3e` | `d9ed1ac` | Workflow #5, all 15 guides, assessment. First upload deploy, on Node 24 |
| 2026-10-30 23:26:26 | `6ae52797c8ded650cba8bbbc` | `e38d627` | Simple First |
| 2026-10-31 18:33:41 | `6ae63476b0ea0ed172f267a5` | `c3bba2f` | PRs #6, #7, #8 |
| 2026-11-01 20:48:49 | `6ae7a5a0661074563afe0c14` | `4ce3249` | PR #9. **Current production** |

### Completed research (do not repeat)

| Date | Work | Use it for |
|---|---|---|
| 2026-10-30 | [Organic SEO audit](https://claude.ai/artifact/ABVmhZyh63JhC9cCtpXHi1) | Original ranked plan and the options it rejected |
| 2026-10-31 | [Simple First + SEO gap analysis](https://claude.ai/artifact/JLKo3iVY3Ex7vgQjv7RhDV) | Priorities, attribution ledger proposal |
| 2026-10-31 | [Failure-focused SEO audit](https://claude.ai/artifact/YTqrWxxYQDvNnxV5sd2mWe) | Search Console evidence, ranking hypotheses, the review checklist |
| 2026-11-01 | [Competitive intelligence research](https://claude.ai/artifact/QZxfKtRJ3DdtyuL5rYk8VY) | Competitors, AI search evidence, Google rules, local link prospects |
| 2026-11-01 | [Life Plan guide review draft](https://claude.ai/artifact/BYmnSgmwfbR4U9CEBiDo4j) | Sources, inversion and measurement for PR #10 |
| 2026-11-02 | [Evanston-first memo](https://claude.ai/artifact/Tug4p2g1hKg7BXffcL1157) | Five ranked opportunities and Experiment 1 |
| 2026-11-03 | Draft quality review of #16 to #20 (Section 5 of this file) | Fact-checks, production compatibility and ranking. Redo only for a draft that changes |

Repository documents from before 2026-10-29 (`ACQUISITION-*.md`, `TOP-PRIORITIES.md`, `WHAT-I-CAN-PROVE.md`, `LAUNCH-CHECKLIST.md`, `VISIT-ATTRIBUTION.md`) are `HISTORICAL`. Where they conflict with this file, this file wins.

### In progress

| Item | State | Waiting on |
|---|---|---|
| [PR #10](https://github.com/JGBALL23/evanston-senior-care-guide/pull/10) | Open, mergeable, unreviewed. 3 commits, 10 files, head `bca3f0b`. Left untouched since 2026-11-02. | See Blocked |
| Daily drafts routine | `EVANSTON-DAILY-GUIDE-DRAFTS`, enabled. 6 AM Chicago. Last run succeeded 2026-11-03 12:02 UTC. Writes to `drafts` only and never publishes. | Owner chooses what is published |
| Search Console review | Partial (U3) | Section 7 |

### Unpublished guides on `drafts` (`VERIFIED` 2026-11-03)

| Draft | Slug | Commit | Written |
|---|---|---|---|
| #16 | `illinois-medicare-savings-program` | `780f59c` | 2026-10-30 |
| #17 | `illinois-advance-directive-power-of-attorney` | `d3c0000` | 2026-10-31 |
| #18 | `illinois-benefit-access-program` | `6ee6a60` | 2026-11-01 |
| #19 | `illinois-home-delivered-meals` | `b929efc` | 2026-11-02 |
| #20 | `illinois-elder-abuse-reporting` | `f72ff6f` | 2026-11-03 |

All five need separate publication approval. All are statewide topics, and none is part of Experiment 1. The routine can add up to two guides a day.

### Draft quality review (2026-11-03)

**Reviews completed: 5 of 5. Corrections completed: 0. Approved for publication: none.** Each claim listed below was compared with the primary source it relies on, read on 2026-11-03 (`VERIFIED`). Ranks and actions are `RECOMMENDED` (D-017), not approved. Nothing on `drafts` was changed. Production (`6ae7a5a0`), `main` (`4ce3249`), `drafts` (`f72ff6f`) and PR #10 (`bca3f0b`) were unchanged when the review finished.

| Rank | Draft | Accuracy | Evanston information verified | Fit with the goal | Action (`RECOMMENDED`) |
|---|---|---|---|---|---|
| 1 | #19 Home-delivered meals | 3 material errors | CJE SeniorLife delivers state-funded meals to ZIPs 60201 to 60204, 60208 and 60209 after an assessment by North Shore Senior Center. Meals on Wheels Northeastern Illinois lists Evanston: $10 a meal, with a sliding scale. The Levy Center's group meal program closed in August 2026. | Families arranging help at home. Search demand unmeasured. | Revise before consideration. Improve first. |
| 2 | #17 Power of attorney for health care | 4 statutory errors, 3 minor. No not-legal-advice notice. | The City's resource list names the Center for Disability and Elder Law, CJE Legal Desk and North Suburban Legal Aid. | Families planning a parent's care. Strong statewide competition. | Revise before consideration, then an Illinois attorney's review. |
| 3 | #20 Elder abuse reporting | 3 material errors, 1 omission | Metropolitan Family Services (Skokie) is Evanston's APS provider. The City of Evanston is the regional long-term care ombudsman. | Crisis intent. A tour prompt fits poorly. | Hold. Candidate for supporting content once corrected. |
| 4 | #16 Medicare Savings Programs | 2 material errors, 2 minor | Thin. The IDHS office for Evanston is in Lincolnwood. The Levy Center offers Medicare counseling (SHIP). | Mostly benefit seekers, with incomes under about $1,800 a month for one person. | Hold |
| 5 | #18 Benefit Access Program | 3 material errors, 1 missing step | Thin. The Levy Center books application appointments (847-866-2919). | Mostly benefit seekers, with incomes under $33,562 a year for one person. | Hold |

**Errors found. None has been corrected.**

- **#19:** (1) Treats age 60 as the only test. An assessment of frailty or being homebound is required ([89 Ill. Adm. Code 230.255](https://www.ilga.gov/ftp/JCAR/AdminCode/089/089002300C02550R.html); the state's provider locator). (2) Credits the Senior HelpLine route to the state's nutrition page, which says to contact the Area Agency on Aging or a provider ([IDoA](https://ilaging.illinois.gov/programs/nutrition.html)). (3) Says the agency serving Evanston cannot be identified. The state's list names AgeOptions, and the locator names North Shore Senior Center as the Care Coordination Unit ([AAA list](https://ilaging.illinois.gov/forprofessionals/aaa-list.html)). Local sources: [CJE](https://cje.net/supportiveservices/foodservices/), [Meals on Wheels Northeastern Illinois](https://mealsonwheelsnei.org/faq), [Levy Center](https://www.cityofevanston.org/departments/prcs/facilities/levy_senior_center/senior_social_services.php).
- **#17:** (1) Says two doctors must certify incapacity before a surrogate acts. The attending physician decides, and a second practitioner must concur only before life-sustaining treatment is forgone ([755 ILCS 40/20](https://www.ilga.gov/Documents/legislation/ilcs/documents/075500400K20.htm)). (2) Says only the agent cannot witness the power of attorney. Relatives of the principal or agent, the principal's clinicians, and the facility's owners or operators are also excluded ([755 ILCS 45/4-10](https://www.ilga.gov/Documents/legislation/ilcs/documents/075500450K4-10.htm)). (3) Bars health professionals as living-will witnesses, which the statute does not. Its form excludes heirs and anyone financially responsible for the care ([755 ILCS 35/3](https://ilga.gov/legislation/ilcs/documents/075500350K3.htm)). (4) Says a court-appointed guardian escapes the surrogate limits. A guardian is treated as a surrogate (40/20). Minor: an APRN, PA or resident can also sign a POLST; IDoA does not host every form named; IDPH names no "moral or religious" grounds for objecting. Nine claims need an Illinois attorney.
- **#20:** (1) Says IDoA publishes no response times. It gives 24 hours, 72 hours and up to 7 days by type of report ([IDoA](https://ilaging.illinois.gov/protectionadvocacy/abuse-after-report.html)). (2) Says APS never covers facility residents. The statute covers abuse by family or other non-staff and exploitation by non-employees ([320 ILCS 20/2](https://ilga.gov/legislation/ilcs/ilcs3.asp?ActID=1452)); a specialist should confirm. (3) Omits the HFS Supportive Living complaint line, 1-844-528-8444 ([HFS](https://hfs.illinois.gov/medicalprograms/slf/complaintprocess.html)). It also says the law's mandated reporters are not stated; IDoA lists them and their immunity. Verified as written: APS 1-866-800-1409, 24 hours; IDPH complaints 1-800-252-4343.
- **#16:** (1) Says to add the $25 disregard to income. The first $25 of non-SSI income is subtracted, once per person ([IDHS](https://www.dhs.state.il.us/page.aspx?item=14179)). (2) The SLMB and QI limits do not match the IDHS 2026 table ([IDHS](https://www.dhs.state.il.us/page.aspx?item=21741)). Minor: a Medicare.gov quote is reworded, and the programs differ by income band, not "mainly" procedure. Verified as written: the QMB limits and the online application.
- **#18:** (1) Reports an age-rule discrepancy that does not exist. (2) Says "legally separated" where the rule says "permanently separated" ([IDoA FAQ](https://ilaging.illinois.gov/benefitsaccess/eligibility-20and-20frequently-asked-questions.html)). (3) Says the Secretary of State sets the plate fee. Statute sets it, at $10 since 1 January 2023 ([IDoA](https://ilaging.illinois.gov/press-release.25844.html)). Omits NITA's separate Ride Free application ([NITA](https://nita.illinois.gov/riders/free-and-reduced-fare-programs)). Verified as written: the income limits.

**Compatibility with production (`VERIFIED` against `main`):** all five use the guide template from before PRs #7 and #9. Published as built, each would bring back the footer wording about Westminster Place that PR #9 replaced and the related-guides block that PR #7 replaced. As written, every description (205 to 349 characters) fails `check-guides.js`, whose limit is 160. The Benefit Access title is 73 characters, over the limit of 70. `main` requires a `RELATED` entry and links from two other guides, so any release edits two live guides (`RECOMMENDED`: not the cost guide while Experiment 1 is pending). `drafts` does not have PRs #6 to #9 and must never be merged into `main` (D-001). The layout, assessment and inquiry flow stay as they are only if just the guide's content is moved to a fresh branch from `main`. A corrected #17 that cites statutes needs `ilga.gov` on the citation allowlist, which exists only in unmerged PR #10.

### Blocked

| Item | Blocked by | Who |
|---|---|---|
| PR #10 merge | Section 396.50 comparison needs Illinois Register Vol. 50, Issue 38, PDF pages 256 to 275 attached, because the Register blocks automated tools. Legal review recommended. Merge, deploy and IndexNow each need approval. | Owner |
| Experiment 1 | Section 7, then the owner's approval | Owner |
| End-to-end inquiry test (U1) | Separate approval | Owner |
| IndexNow catch-up (U4) | Separate approval. The ledger commit touches `main`. | Owner |
| Tour attribution (U6) | A proposal for review and a process with Admissions | Owner |
| Drafts #16 to #20 | Owner review, and a demonstrated gap. Since 2026-11-03, factual corrections come first (Draft quality review). | Owner |

### Pending verification

- [ ] One labeled end-to-end inquiry test on the current release
- [ ] Cost guide: indexed or not, and its queries
- [ ] Page indexing URL lists and Sitemaps report status
- [ ] Links report: top linking sites
- [ ] Queries for the Medicare and inspection-records guides
- [ ] Which page earned the one click
- [ ] A logged-out Google check from Evanston
- [ ] Section 396.50 against the Life Plan guide

---

## 6. Decision Log (append only)

**Nothing labeled `RECOMMENDED` is authorized.** Today that means D-011, D-015, D-016 and D-017. Revisit conditions are proposed unless the owner set them. Decisions before 2026-10-29 are in the `HISTORICAL` documents listed in Section 5.

### D-001 · 2026-10-29 · `APPROVED` · Releases go through a release branch and PR
- **Why:** `main` is production, and `drafts` holds work awaiting review.
- **Evidence:** PRs #2 and #5.
- **Rejected or deferred:** merging `drafts` into `main` wholesale.
- **Revisit:** not planned.

### D-002 · 2026-10-30 · `APPROVED` · Simple First
- **Decided:** result order is answer, costs, how to pay, optional Westminster Place inquiry.
- **Why:** complete beginners leave when they meet a wall of text.
- **Evidence:** owner review of the final design; `SIMPLE-FIRST.md`.
- **Rejected or deferred:** none recorded.
- **Revisit:** when funnel counts show a specific drop-off.

### D-003 · 2026-10-30 · `APPROVED` · Drafts need separate publication approval
- **Decided:** guides on `drafts` stay unpublished until the owner reviews each one. No additional articles without a demonstrated gap (2026-10-31).
- **Why:** publishing is the owner's step.
- **Evidence:** PR #5.
- **Rejected or deferred:** publishing guide 16 with the Simple First release.
- **Revisit:** guide by guide.

### D-004 · 2026-10-31 · `APPROVED` · Priority order for the SEO and lead-generation phase
- **Decided:** (1) measurement and reliability, (2) internal linking, titles and descriptions, (3) private inquiry and tour attribution by reference ID, (4) Life Plan contracts guide.
- **Why:** measure first, and fix what exists before adding content.
- **Evidence:** Simple First + SEO gap analysis.
- **Rejected or deferred:** a new homepage redesign, chatbot, pop-ups.
- **State:** (1) partial, (2) shipped in PR #7, (3) not started, (4) in PR #10.
- **Revisit:** when priority 1 evidence is complete.

### D-005 · 2026-10-31 · `APPROVED` · Netlify RUM disabled
- **Why:** keep first-party counting and the privacy notice accurate.
- **Evidence:** the owner disabled it; live pages matched `_dist` on 2026-11-03.
- **Rejected or deferred:** keeping RUM and adding a sentence to the privacy notice.
- **Revisit:** only for a measured need, with the privacy notice updated at the same time.

### D-006 · 2026-10-31 · `APPROVED` · `ilga.gov` allowed as a legal research source
- **Decided:** cross-check against IDPH and current Public Acts. Never treat its text as certified law. No guarantees about contracts or refunds.
- **Why:** the statute is published there, and IDPH's own FAQ link was dead.
- **Evidence:** gap analysis; IDPH page opened 2026-10-30.
- **Rejected or deferred:** none recorded.
- **Revisit:** if a certified source becomes usable.

### D-007 · 2026-10-31 · `APPROVED` · The daily drafts routine stays running, unchanged
- **Why:** it only adds drafts, and the owner decides what is published.
- **Evidence:** owner instruction; the scheduled task's settings are unchanged since 2026-10-23.
- **Rejected or deferred:** pausing it (this reverses the approval given earlier that day). Running it from an approved topic queue is deferred.
- **Revisit:** owner's call. Any change needs approval.

### D-008 · 2026-10-31 · `APPROVED` · SEO work is failure-focused
- **Decided:** aim at genuine inquiries and confirmed tours, not traffic. Choose the first fix only after the indexing, backlink and per-page query review.
- **Why:** find what is failing before changing anything.
- **Evidence:** R1. Low rankings do not prove any specific cause.
- **Rejected or deferred:** continuously adding improvements.
- **Revisit:** after the review (U3).

### D-009 · 2026-10-31 · `APPROVED` · Evanston stays in the independent-living guide's title
- **Decided:** no title change until queries are examined. Redirects are not assumed to be a problem.
- **Why:** a title decision should follow actual queries.
- **Evidence:** R2; R3 later showed every visible query contains "Evanston".
- **Rejected or deferred:** removing Evanston from the title.
- **Revisit:** at the 8-week read.

### D-010 · 2026-11-01 · `APPROVED` · Inquiry disclosure wording corrected, task closed
- **Decided:** the inquiry wording, privacy notice and validation messages now describe the optional, manual hand-off.
- **Why:** disclosures must say what the code and the consent actually do.
- **Evidence:** PR #9; deploy `6ae7a5a0`.
- **Rejected or deferred:** any change to the consent sentence, its version, or what is collected, stored or shared.
- **Revisit:** consent changes only with separate approval.

### D-011 · 2026-11-01 · `RECOMMENDED` · No community list; independent-living rebuild on hold
- **Recommended:** keep the page and title, do not aim the page at list searches.
- **Why:** the visible queries ask for communities. A neutral page cannot meet that without listing every one, the demand is unknown, and Illinois has no register of rental communities to prove a list complete.
- **Evidence:** R3; failure-focused audit.
- **Rejected or deferred:** a community list now; the page rebuild.
- **Revisit:** at the 8-week read. If decision questions appear, the rebuild returns.

### D-012 · 2026-11-01 · `APPROVED` · Inversion-based organic SEO; Life Plan guide first
- **Decided:** return to inversion-based organic SEO. Prepare the Illinois Life Plan contracts guide for review only. One focused SEO improvement at a time.
- **Why:** page one had no plain-English Illinois answer for this decision-stage topic.
- **Evidence:** competitive intelligence research.
- **Rejected or deferred (by the audits, `RECOMMENDED`):** town-by-town pages, a page about Westminster Place, competing for head terms, listings, rankings, awards, reviews, price gates.
- **Revisit:** at the guide's 8-week read, if published.

### D-013 · 2026-11-02 · `APPROVED` · Life Plan guide built for review, not publication
- **Decided:** correction pass, feature branch, independent-living and levels-of-care related links, and `ilga.gov`, `gao.gov` and `ssa.gov` as citation hosts in PR #10.
- **Why:** the owner approved the guide's direction after reviewing the draft.
- **Evidence:** PR #10 description.
- **Rejected or deferred:** merge, deployment and IndexNow are not approved.
- **Revisit:** after the Section 396.50 check and the recommended legal review.

### D-014 · 2026-11-02 · `APPROVED` · Evanston-first, Illinois-supported
- **Decided:** Evanston is the primary market. The strategy is inversion + local specialization + organic SEO. PR #10 may remain statewide supporting content.
- **Why:** start narrow, prove results, build authority, expand.
- **Evidence:** competitive research and the Search Console evidence in R1 and R3.
- **Rejected or deferred:** mass renaming or rewriting, blindly replacing "Illinois" with "Evanston", new directories, features or redesigns, restarting the broad competitor audit.
- **Revisit:** after Experiment 1's 8-week decision.

### D-015 · 2026-11-02 · `RECOMMENDED` · First experiment: Evanston costs
- **Recommended:** Experiment 1 (Section 4).
- **Why:** the only one of five opportunities where a neutral guide can add a current, sourced answer without naming or ranking communities.
- **Evidence:** seven Google page-one checks; R1 and R3.
- **Rejected or deferred:** a community list or ranking, a new memory-care or Life Plan page for Evanston, national topics such as Medicare.
- **Revisit:** after the Section 7 reading.

### D-016 · 2026-11-03 · `RECOMMENDED` · This file becomes the single source of truth
- **Why:** research and changes were being repeated because completed work was hard to track.
- **Evidence:** the owner's request of 2026-11-03.
- **Rejected or deferred:** none.
- **Revisit:** if this file stops being kept current. Becomes `APPROVED` only when the owner merges it.

### D-017 · 2026-11-03 · `RECOMMENDED` · Draft review: improve the meals guide first, hold three
- **Recommended:** correct #19 (home-delivered meals) first, on a fresh branch from `main`, for review only. Correct #17 (power of attorney) next and have an Illinois attorney review it before any publication. Hold #20, #16 and #18. No draft is ready for publication review.
- **Why:** all five contain material factual errors. #19 has the most verified Evanston information that statewide pages lack, and correcting it needs no legal review. #16 and #18 mostly reach people seeking a benefit. #20 is read in a crisis, where a tour prompt fits poorly.
- **Evidence:** the Draft quality review in Section 5 and the primary sources linked there.
- **Rejected or deferred:** publishing any draft as written; merging `drafts`; renaming statewide topics to Evanston; any change to Experiment 1 or Section 7.
- **Revisit:** when the owner reviews a corrected draft. Publication would still need D-003's demonstrated gap. The verified gap is informational, and search demand for these topics is unmeasured.

---

## 7. Next action

**Exactly one action: take the first dated Search Console reading for the cost guide.**

| | |
|---|---|
| Who | Owner, about 10 minutes in Search Console. No code and no site change. Report the figures in chat and Claude records them here. |
| Page | `https://evanstonseniorcareguide.com/guides/assisted-living-cost-illinois/` |
| Why it matters | Every Search Console figure here predates the 31 October release, and the cost guide's own data has never been read. It decides whether Experiment 1 can start, and it gives the experiment a baseline. Without it, any change would be unmeasurable. |

**Evidence needed:**

1. **URL Inspection:** indexed or not, Google-selected canonical, last crawl date.
2. **Performance, filtered to this page, 2026-10-21 to the reading date:** impressions, clicks, CTR, average position, and the visible queries.
3. **Whole property, same dates:** impressions, clicks, CTR, average position.
4. **Only if the cost guide has no Evanston queries:** the inspection-records guide's queries, which decide whether Experiments 1 and 2 swap.

**Definition of done:**

- [ ] Section 3 has a new dated reading (R4 onward), with each query tagged Evanston, statewide or national. Nothing older is overwritten.
- [ ] The cost guide is recorded as indexed or not indexed.
- [ ] Section 4 has the captured baseline.
- [ ] The Decision Log records one outcome: the owner approves Experiment 1, declines it, or indexing comes first.
- [ ] Section 7 names the next single action.
