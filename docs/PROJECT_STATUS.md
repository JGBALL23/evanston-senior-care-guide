# Evanston Senior Care Guide: Project Control Center

**The single source of truth for site development and organic SEO. Read it before proposing work.**

| | |
|---|---|
| Last verified | 2026-11-05 11:50 Chicago (17:50 UTC): GitHub, Netlify and the live site, after the PR #12 release. Search Console as of R4. |
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

### Production (`VERIFIED` 2026-11-05, after the PR #12 release)

| Item | State |
|---|---|
| `main` | `84b9e6b`, merge of PR #12, 2026-11-05 17:44 UTC (11:44 Chicago) |
| Production deploy | `6aecc09906b589d0932fe784`, published 2026-11-05 17:45:11 UTC, state `ready`. 4 functions, identical to the previous release; 1 redirect rule; 5 header rules; 68 files uploaded, secret scan clean. |
| Does it match `main`? | Yes, by direct comparison. Netlify records no commit for upload deploys, so 32 public files were fetched from production and compared with `_dist` at `84b9e6b`: 15 identical, 17 different only by Netlify's rewrite of `/privacy.html` links to `/privacy`. Beacon files under `/t/` were not fetched, to keep the counts clean. Only `app.js`, the homepage, the inspection guide and `sitemap.xml` differ from the previous release. |
| On `main` but not live | Nothing a visitor can see |
| Rollback point | `6aebd5efd56ee67f5aba491d` (the PR #11 release, `971b14a`), state `ready`. The one before it, `6ae7a5a0661074563afe0c14`, is also still `ready`. |
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
| `drafts`, head `5be93b6` (`VERIFIED` 2026-11-04) | 6 unpublished guides (Section 5). The routine added #21 on 2026-11-04. | No, all 6 URLs return 404 |
| [PR #11](https://github.com/JGBALL23/evanston-senior-care-guide/pull/11), merged as `971b14a` (`VERIFIED` 2026-11-04) | Experiment 1: the cost guide's rewritten Evanston section | Yes, since deploy `6aebd5ef` |
| [PR #12](https://github.com/JGBALL23/evanston-senior-care-guide/pull/12), merged as `84b9e6b` (`VERIFIED` 2026-11-05) | Experiment 2: the inspection guide corrected, with its Evanston section; the assessment's compare link | Yes, since deploy `6aecc099` |
| Claude Docs memos | Research and recommendations | No |

`drafts` has diverged from `main` (12 commits ahead, 25 behind) and lacks PRs #6 to #9. Never merge it wholesale. Publish a guide through a release branch cut from `main`, as PR #5 did.

### Known unresolved issues

| # | Issue | Evidence | Status |
|---|---|---|---|
| U1 | **Nothing shows the inquiry chain working on the current release.** The last notification email is a test from 2026-10-22. Functions moved from Node 20 to Node 24 on 2026-10-30. | Netlify deploy records; notification inbox; [plan](../INQUIRY-E2E-TEST-PLAN.md) marked "Not executed" | **Closed 2026-11-05: one labeled test passed on deploy `6aebd5ef` (D-020).** |
| U2 | **No current Search Console data exists.** At the last reading, at most 6 of 18 sitemap pages were indexed. | Section 3 | Section 7. Partly closed 2026-11-04: R4 covers the cost guide only. |
| U3 | **The Search Console review is partial.** Unread: Page indexing URL lists, Sitemaps report, Links report, queries for every page except the independent-living guide, and which page earned the one click. | Failure-focused audit, 2026-10-31 | Owner read needed |
| U4 | **IndexNow is behind.** Last submission 2026-10-28. All 16 tracked `/guides/` URLs have changed since, 3 of them were never submitted, and the homepage is not tracked at all. IndexNow reaches Bing, not Google. | `data/indexnow-ledger.json` compared with `_dist` | Needs separate approval. The PR #11 release (2026-11-04) changed the cost guide and the sitemap; nothing was submitted. |
| U5 | **Funnel counts expire after 24 hours.** Only hand-taken readings survive. | [Funnel baseline](../data/funnel-baseline.md) | Scheduled snapshot proposed, not approved |
| U6 | **A confirmed tour cannot be recorded yet.** A private ledger keyed by reference ID was proposed, not built. No Admissions hand-back exists. | Gap analysis, 2026-10-31 | Priority 3, not started |
| U7 | **`data/guide-queue.md` is out of date.** It says the routine is paused and lists the Life Plan guide as not yet written. The routine is enabled and picks its own topics, and the guide is in PR #10. | Scheduled-task record; file on `main` | Correct when approved |
| U8 | **Sitemap `lastmod` is stale.** No entry is later than 2026-10-29, although Netlify shows 17 pages changed on 31 October and 18 on 1 November. | `_dist/sitemap.xml`; deploy summaries | Ride-along fix, `RECOMMENDED`. Partly fixed by PR #11 (owner, 2026-11-04): a re-review now re-dates only the guide reviewed, so only the cost guide moved to 2026-11-04. The homepage, `/guides/` and the privacy notice still show 2026-10-29, although they changed on 31 October and 1 November. That original gap remains. |
| U9 | **Minor:** `/privacy` and `/privacy.html` both return 200. Live links use the first; the canonical tag and sitemap use the second. | Live check | Negligible, audit 2026-10-31 |
| U10 | **Housekeeping:** two preview sites remain online (`esc-preview-d9ed1ac`, `esc-preview-simple-first`). Both are `noindex` and block crawlers. Since 2026-11-04 a third, `esc-preview-evanston-costs`, holds the review copy of PR #11: static files only, no functions, `noindex`, `robots.txt` blocks everything. | Netlify; live headers | Owner may delete all three. PR #11 is released, so the third is no longer needed. |
| U11 | **`ilga.gov` fails the citation checker.** `ilga.gov` sends its certificate without the intermediate, so `check-citations.sh` (curl) reports every `ilga.gov` URL as dead (code 000), although browsers open them. This affects PR #10 and PR #11. The daily routine runs `check-citations.sh` on `drafts` and stops on any dead citation, so `ilga.gov` citations must not reach `drafts` before this is handled. | `openssl s_client`, 2026-11-04: "unable to verify the first certificate" for `ilga.gov`, `www.ilga.gov`, `lrb.ilga.gov` and `witnessslips.ilga.gov`; `beta.ilga.gov` verifies | Owner decision. `RECOMMENDED`: make the checker supply the missing intermediate for `ilga.gov` only. Documented in `check-citations.sh` on `main` since PR #11, with certificate validation left on. On `main`, 41 of 45 citations resolve; the 4 failures are the cost guide's `ilga.gov` URLs, all opened in a browser tool on 2026-11-04. |
| U12 | **CareScout disagrees with itself on the Illinois assisted living figure.** Its Illinois press release (2 March 2026) gives $72,645 a year. Both 2025 data-table PDFs give $74,628 a year and $6,219 a month ("As reported, monthly rate, private, one bedroom"). | Press release on Business Wire; PDFs 298701 and 282102, read 2026-11-04 | The site uses $6,219, the monthly figure both tables print. No page change. Ask CareScout only if the annual figure is ever used |
| U13 | **Three places send families to a hospital-only state site.** `healthcarereportcard.illinois.gov` is the Illinois Hospital Report Card: hospitals and surgery centres, no nursing homes, no assisted living. (1) The live inspection guide tells families to search it for a care community's record. (2) The assessment result's "Compare other communities yourself" link (`app.js`) calls it "Illinois' official licensed-facility directory" that "lists every licensed facility in Illinois"; every visitor who finishes the assessment sees it. (3) The levels-of-care guide lists it among its sources; its text makes no claim from it. | The site read 2026-11-05: title "Illinois Hospital Report Card", scope hospitals and surgery centres | (1) and (2) **fixed and live since deploy `6aecc099` (2026-11-05, D-022)**: the guide is rewritten, and the result card now links the corrected guide. (3) Open: drop the citation at that guide's next review. |

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

> **R4 (2026-11-04) is the only current reading, and it covers the cost guide only.** Every other Search Console figure below is `HISTORICAL` and predates the 31 October SEO release. Claude has no Search Console connection, so these figures are `OWNER-REPORTED`.

### Dated readings

| ID | Reported | Covers | Source |
|---|---|---|---|
| R1 | 2026-10-31 | First impressions (2026-10-21) to before the 31 October release. Exact end date not recorded. | Search Console Performance, owner |
| R2 | 2026-10-31 | Page indexing report. Date of the report's last update not recorded. | Search Console Page indexing, owner |
| R3 | 2026-11-01 | Same period as R1 | Search Console queries for the independent-living guide, owner |
| R4 | 2026-11-04 | Date range not stated by the owner | Search Console, cost guide only (`/guides/assisted-living-cost-illinois/`), owner |

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

**Cost guide (R4, `OWNER-REPORTED` 2026-11-04).** This is Experiment 1's baseline (Section 4).

| Measure | Value |
|---|---|
| Indexed | Yes |
| Impressions | 19 |
| Clicks | 0 |
| CTR | 0% (calculated) |
| Average position | 40.6 |
| Visible query | "assisted living cost evanston il" (Evanston). Its own impression count was not reported. |
| Date range | Not stated. Section 7 had asked for 2026-10-21 to the reading date. |

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

**Changed meaning, from deploy `6aecc099` (2026-11-05 17:45 UTC):** the `state-directory-click` count (beacon `idph`) now counts clicks from the result card to the inspection guide. Before that it counted clicks to the hospital-only Report Card (U13). Do not add the two periods together.

### Business outcomes

| Metric | State | Source and date |
|---|---|---|
| Stored inquiries | **Not read.** The export needs the owner's token. Exclude test records from any count, including the labeled test "TEST DO-NOT-CONTACT" of 2026-11-05 16:07 UTC. | 2026-11-05 |
| Inquiry notification emails | Tests only. The latest is the labeled test of 2026-11-05. | Notification inbox, checked 2026-11-05 |
| Confirmed tours | None recorded. No reporting process exists. | U6 |

**Not available and never to be estimated:** search volumes, keyword difficulty, conversion rates, local statistics, community prices.

**Review dates (`RECOMMENDED`, no scheduled task exists):** 4 weeks after the 31 October release is 2026-11-28; 8 weeks is 2026-12-26.

---

## 4. Active experiment

**Experiment 1 is running. It was released on 2026-11-04, and its implementation phase is closed (D-019). The page is measured, not modified, until the 8-week review on 2026-12-30. The one exception is correcting a factual error.**

**Experiment 2 was released on 2026-11-05 (D-022) and is now measured, not modified.** It is the first improvement of the owner's 30-day Evanston SEO Growth Sprint (2026-11-05 to 2026-12-05). It changes a different page, so Experiment 1 stays untouched and measurable.

### Experiment 1: Evanston costs (`APPROVED` 2026-11-04; released 2026-11-04; implementation closed)

| Field | Detail |
|---|---|
| Source | [Evanston-first memo](https://claude.ai/artifact/Tug4p2g1hKg7BXffcL1157), 2026-11-02 |
| Change | Rewrite only the "What this means in Evanston" section of `/guides/assisted-living-cost-illinois/`. The title, short answer, sources, disclosures, assessment and optional inquiry stay as they are. No community names or prices. |
| Hypothesis | Google's page one lacks a current, sourced, neutral answer on Evanston costs. A section explaining why published figures disagree, what the sourced figure is and is not, and how to read a quote will earn Evanston impressions and clicks for this page. |
| Built (`VERIFIED` 2026-11-04) | [PR #11](https://github.com/JGBALL23/evanston-senior-care-guide/pull/11), branch `feature/evanston-costs-section`, head `1c4833c`, cut from `main` `4ce3249`. Only the Evanston section's text changed. It now relies on CareScout's 2025 methodology, 210 ILCS 9/15 (with Public Act 104-0589), 9/85 and 9/90, and IDPH, so the sources list grew from 2 to 8, `ilga.gov` joined the citation allowlist, and the page's review date moved to 4 November 2026. An independent fact-check found six sentences to fix; all six are fixed in `1c4833c`. The title, description, short answer, other sections, disclosures, assessment and inquiry are unchanged. |
| Baseline | **Captured (R4, Section 3):** indexed; 19 impressions, 0 clicks, average position 40.6; visible query "assisted living cost evanston il". The date range was not stated. |
| Released (`VERIFIED` 2026-11-04) | The owner approved it after reviewing PR #11 and the review copy. Final cleanup `9c44edb`: the sitemap re-dates only the cost guide, and the section was simplified for phones (longest sentence 39 → 25 words) with every fact, qualification, the checklist and the citations kept. Merge commit `971b14a`. Deploy `6aebd5efd56ee67f5aba491d`, published 2026-11-05 01:03:59 UTC (19:03 Chicago, 4 November). Rollback point `6ae7a5a0661074563afe0c14`. IndexNow not submitted. |
| Release baseline | Recorded: release commit `971b14a`, deploy `6aebd5ef`, publish time above. **Still needed:** the release-day Search Console reading for this page, with its date range stated (Section 7). The 8-week result is measured against that reading, with R4 as the earlier reference. |
| Intended result | Impressions, average position and clicks rise for this page's queries containing "Evanston", compared with guides left unchanged. Stored inquiries are counted from server records. |
| Review date | **2026-12-30**, 8 weeks after the 2026-11-04 release. |
| Stop condition | If the page is not indexed, indexing comes first and the experiment waits. R4 reports it indexed. |

**Decision criteria at 8 weeks:**

| Result | Decision |
|---|---|
| No Evanston impressions | Stop. Check indexing and links. Write nothing more. |
| Impressions without clicks | Test the description, with separate approval. |
| Clicks without onward use | Revisit the next-step link. |
| Impressions and clicks | The inspection-records guide becomes Experiment 2. |

**Could change the order:** if the inspection guide's queries are local and the cost guide has none, swap the two.

**Overlap to account for:** the 31 October release is still inside its own review window. R1 is its baseline, and its 8-week mark is 2026-12-26.

### Experiment 2: Evanston inspection records (`APPROVED` 2026-11-05; released 2026-11-05)

| Field | Detail |
|---|---|
| Source | The owner's 30-day sprint request, 2026-11-05 (D-021). The decision table above already named this guide as Experiment 2. |
| Change | `/guides/check-illinois-inspection-records/` only. The Hospital Report Card (U13) is replaced with where each kind of record is kept. A new section, "How to check an Evanston community's record", covers nursing care, assisted living, memory care and independent living. Also new: the Nursing Home Care Act's four violation types. The short answer, the description and the Care Compare scope paragraph are corrected. No community names and no fines. Added at release (D-022): the assessment result's "Compare other communities yourself" link now opens this guide, and the homepage sentence describing that link matches. Title, H1, disclosures, the assessment's questions and the inquiry are unchanged. |
| Hypothesis | A family vetting an Evanston community before a tour searches for its inspection record. A page that says where each part's record is, and what to ask for on the visit, will earn impressions and clicks for inspection queries, including Evanston ones, and send those readers on to the assessment. |
| Built (`VERIFIED` 2026-11-05) | [PR #12](https://github.com/JGBALL23/evanston-senior-care-guide/pull/12), branch `feature/evanston-inspection-records`, head `c2767bc`, cut from `main` `971b14a`. Sources: 2 to 13, all read 2026-11-05. `check-guides.js`: 1382 to 1418 checks, and 16 mutation tests each fail their intended check. An independent fact-check found no error and six qualifications; all six are applied. Review date 5 November 2026. Only this guide's sitemap date moves; `/guides/` is byte-identical to `main`. Review copy on `esc-preview-evanston-costs` (deploy `6aecbbe3c1d1fc9903728d6c`, `noindex`, no functions). |
| Baseline | **Not captured yet.** R6 (Section 7): Search Console for this page, with a date range ending 2026-11-05, so it shows the page before the release. Search Console keeps that history, so it can still be read. |
| Released (`VERIFIED` 2026-11-05) | The owner approved merge and deploy, and added the assessment's compare-link fix to PR #12 (D-022). Head `9f552ba`; all 13 suites passed on it. Merge commit `84b9e6b`. Deploy `6aecc09906b589d0932fe784`, published 2026-11-05 17:45:11 UTC (11:45 Chicago). Rollback point `6aebd5efd56ee67f5aba491d`. IndexNow not submitted. The facility-lookup check was not done: the owner chose not to be interrupted. The page makes no claim about it either way. |
| Intended result | Impressions, average position and clicks rise for this page, especially for queries naming Evanston, inspections or violations. Stored inquiries are counted from server records. |
| Review | Sprint read on 2026-12-05 (indexing and early impressions only). **8-week review on 2026-12-31.** |
| Stop condition | If the page is not indexed, indexing comes first. |

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
| #11 | 2026-11-04 | `971b14a` | `main` | Experiment 1: the cost guide's Evanston section; a re-review re-dates only that guide in the sitemap; the `ilga.gov` checker limitation documented | `6aebd5ef` |
| #12 | 2026-11-05 | `84b9e6b` | `main` | Experiment 2: the inspection guide corrected, with its Evanston section; the assessment's compare link and the homepage sentence describing it now point to that guide | `6aecc099` |

### Deployment History (append only)

Netlify records no commit for these deploys. The source commit comes from each approved release record.

| Published (UTC) | Deploy ID | Source | What shipped |
|---|---|---|---|
| 2026-10-28 14:17:49 | `6ae20405f331d561ae40cdc6` | `028447c` | Last deploy through `publish.py`, on Node 20 |
| 2026-10-30 14:02:11 | `6ae4a35428df7531ed6b6b3e` | `d9ed1ac` | Workflow #5, all 15 guides, assessment. First upload deploy, on Node 24 |
| 2026-10-30 23:26:26 | `6ae52797c8ded650cba8bbbc` | `e38d627` | Simple First |
| 2026-10-31 18:33:41 | `6ae63476b0ea0ed172f267a5` | `c3bba2f` | PRs #6, #7, #8 |
| 2026-11-01 20:48:49 | `6ae7a5a0661074563afe0c14` | `4ce3249` | PR #9. **Current production** |
| 2026-11-05 01:03:59 | `6aebd5efd56ee67f5aba491d` | `971b14a` | PR #11, Experiment 1. Owner-approved, one upload of `_dist`, the 4 functions and `netlify.toml` (68 files). Rollback point: `6ae7a5a0661074563afe0c14`. **Current production** |
| 2026-11-05 17:45:11 | `6aecc09906b589d0932fe784` | `84b9e6b` | PR #12, Experiment 2, with the assessment's compare-link fix. Owner-approved, one upload of `_dist`, the 4 functions and `netlify.toml` (68 files, secret scan clean). Rollback point: `6aebd5efd56ee67f5aba491d`. **Current production** |

The newest row is current production. The "Current production" labels on the 2026-11-01 and 2026-11-05 01:03:59 rows are historical: rows here are never edited (rule 7).

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
| 2026-11-04 | Evanston cost figures, done while building Experiment 1 ([PR #11](https://github.com/JGBALL23/evanston-senior-care-guide/pull/11)) | What the CareScout median measures; what four listing websites publish for Evanston and how; what 210 ILCS 9/15, 9/85 and 9/90 require of the contract |
| 2026-11-05 | Illinois inspection records, done while building Experiment 2 ([PR #12](https://github.com/JGBALL23/evanston-senior-care-guide/pull/12)), with an independent fact-check | Where nursing home and assisted living records are kept; what IDPH's quarterly violator reports contain (latest: April to June 2026); 210 ILCS 45/3-210 and the four violation types; 210 ILCS 9/10 and 9/110; 77 Ill. Adm. Code 295.1020; 210 ILCS 4/15; the Hospital Report Card's real scope. Open: whether IDPH's facility lookup shows assisted living inspection history (no tool here could load it) |
| 2026-11-05 | Evanston listing and link opportunities (owner's request; nothing sent) | **Viable, with a published way to submit:** (1) Evanston Public Library's [Programming Proposal](https://epl.org/programming-proposal/) form (Senior 65+ audience, 8 weeks' notice, a reference required, reply only if accepted); (2) Evanston RoundTable letters and guest essays (form, or `letters@evanstonroundtable.com`; Evanston topics; name, email and phone required; 30 days between pieces); (3) the Daily Herald's Evanston submitted-content section (free account at `dailyherald.com/share/article/`; terms ban solicitations and ads). Outreach drafts were given to the owner in chat. **Ruled out:** EPL's old community organizations directory now returns 404 (so ACQUISITION-EXECUTION item 2.4 is obsolete). The City's Senior Resources list has no website links and no listing process. The domain `evanstoncarenetwork.org` now shows a parking page. The City's and Erie's partner lists name service providers only and have no submission route. |
| 2026-11-05 | Rob Hoffman, "The Most Valuable SEO & AI SEO Training You'll Ever Watch" (YouTube, 15 Oct 2026), studied from the full transcript the owner supplied | **Rejected:** competitor alternatives, versus, review and best-of pages (they would mean ranking named communities); 30-day re-dating without re-verification; more calls to action, since guides already have a sticky Start button and about 10 links to the assessment. **Already done:** pre-tour pages (Experiments 1 and 2), a short-answer box, original checks. **Gaps found:** no comparison tables on any guide; no FAQ sections; "Last reviewed" and the author appear only at the foot of each guide; query-to-page mapping and cannibalization never checked; no AI-visibility tracking (Claude cannot query ChatGPT, Perplexity or AI Overviews from its environment). **Recommended, not approved:** a cannibalization check and page map from one Search Console export; an Experiment 3 candidate (a comparison table and FAQ on the levels-of-care guide, plus U13 item 3); a refresh calendar tied to real source updates; optional owner decisions on a LinkedIn article and a screen-recorded YouTube walkthrough. |

Repository documents from before 2026-10-29 (`ACQUISITION-*.md`, `TOP-PRIORITIES.md`, `WHAT-I-CAN-PROVE.md`, `LAUNCH-CHECKLIST.md`, `VISIT-ATTRIBUTION.md`) are `HISTORICAL`. Where they conflict with this file, this file wins.

### In progress

| Item | State | Waiting on |
|---|---|---|
| [PR #10](https://github.com/JGBALL23/evanston-senior-care-guide/pull/10) | Open, mergeable, unreviewed. 3 commits, 10 files, head `bca3f0b`. Left untouched since 2026-11-02. | See Blocked |
| Daily drafts routine | `EVANSTON-DAILY-GUIDE-DRAFTS`, enabled. 6 AM Chicago. Last run succeeded 2026-11-03 12:02 UTC. Writes to `drafts` only and never publishes. | Owner chooses what is published |
| Search Console review | Partial (U3). Cost guide read 2026-11-04 (R4). | Owner |
| Experiment 1 | Released 2026-11-04 (deploy `6aebd5ef`). Implementation closed (D-019); measuring. | The release-day reading (Section 7), then the 8-week review on 2026-12-30 |
| Experiment 2 ([PR #12](https://github.com/JGBALL23/evanston-senior-care-guide/pull/12)) | Released 2026-11-05 (deploy `6aecc099`, D-022); measuring | R6 (Section 7), the sprint read on 2026-12-05, then the 8-week review on 2026-12-31 |

### Unpublished guides on `drafts` (`VERIFIED` 2026-11-03)

| Draft | Slug | Commit | Written |
|---|---|---|---|
| #16 | `illinois-medicare-savings-program` | `780f59c` | 2026-10-30 |
| #17 | `illinois-advance-directive-power-of-attorney` | `d3c0000` | 2026-10-31 |
| #18 | `illinois-benefit-access-program` | `6ee6a60` | 2026-11-01 |
| #19 | `illinois-home-delivered-meals` | `b929efc` | 2026-11-02 |
| #20 | `illinois-elder-abuse-reporting` | `f72ff6f` | 2026-11-03 |
| #21 | `illinois-nursing-home-resident-rights` | `5be93b6` | 2026-11-04 (added to this table 2026-11-04, not reviewed) |

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
| Further changes to the cost guide | Closed until the 8-week review on 2026-12-30 (D-019), except to correct a factual error | Owner |
| Further changes to the inspection guide | Closed until the 8-week review on 2026-12-31 (D-022), except to correct a factual error, or to point families to IDPH's facility lookup if it proves to show inspection history | Owner |
| End-to-end inquiry test (U1) | Done 2026-11-05, passed (D-020) | Owner |
| IndexNow catch-up (U4) | Separate approval. The ledger commit touches `main`. | Owner |
| Tour attribution (U6) | A proposal for review and a process with Admissions | Owner |
| Drafts #16 to #20 | Owner review, and a demonstrated gap. Since 2026-11-03, factual corrections come first (Draft quality review). | Owner |

### Pending verification

- [x] One labeled end-to-end inquiry test on the current release (2026-11-05, passed, D-020)
- [x] Cost guide: indexed or not, and its queries (R4, 2026-11-04)
- [ ] Cost guide reading on release day, with its date range stated (Section 4)
- [ ] Page indexing URL lists and Sitemaps report status
- [ ] Links report: top linking sites
- [ ] Queries for the Medicare and inspection-records guides (the inspection guide's is Experiment 2's baseline)
- [ ] Whether IDPH's facility lookup shows assisted living inspection history (owner, normal browser; PR #12)
- [ ] Which page earned the one click
- [ ] A logged-out Google check from Evanston
- [ ] Section 396.50 against the Life Plan guide

---

## 6. Decision Log (append only)

**Nothing labeled `RECOMMENDED` is authorized.** Today that means D-011, D-016 and D-017. D-015 was approved by D-018. Revisit conditions are proposed unless the owner set them. Decisions before 2026-10-29 are in the `HISTORICAL` documents listed in Section 5.

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

### D-018 · 2026-11-04 · `APPROVED` · Experiment 1 approved for implementation
- **Decided:** build Experiment 1 (D-015) on a fresh branch from `main`. The cost guide's "What this means in Evanston" section explains why local estimates differ, what each kind of figure includes or leaves out, and how a family reaches the real monthly cost, using attributed, verifiable information. Run the tests, provide a working preview, and record the status and release baseline here.
- **Why:** the cost guide is indexed and Google has shown it for "assisted living cost evanston il" (R4).
- **Evidence:** the owner's instruction of 2026-11-04; R4.
- **Rejected or deferred:** a directory, rankings, sponsored recommendations, misleading comparisons and an invented Evanston median; merging or deploying without approval; any change to PR #10 or the daily drafts routine.
- **Revisit:** 8 weeks after release (Section 4).

### D-019 · 2026-11-04 · `APPROVED` · Experiment 1 released; its implementation phase is closed
- **Decided:** a final cleanup first: only the cost guide is re-dated in the sitemap, the Evanston section is simplified for phones, and the `ilga.gov` checker limitation is documented without turning off certificate validation. Then merge PR #11 and deploy it to production once, through the established upload process. Preserve the rollback point and record the release here. The implementation phase then closes: the results are measured, and the page is not modified again before the 8-week review.
- **Why:** the owner reviewed PR #11 and its review copy and approved the improvement.
- **Evidence:** the owner's instruction of 2026-11-04; merge commit `971b14a`; deploy `6aebd5efd56ee67f5aba491d`; live verification in Section 1.
- **Rejected or deferred:** IndexNow (still not approved, U4); further edits to the cost guide before 2026-12-30, except factual corrections; any change to PR #10, the daily drafts routine, the inquiry system or consent.
- **Revisit:** at the 8-week review on 2026-12-30, using the decision criteria in Section 4.

### D-020 · 2026-11-05 · `APPROVED` · One labeled end-to-end inquiry test: passed
- **Decided:** run one production test of the inquiry chain, as described to and approved by the owner. A phone-size browser labeled as the site's test harness took the assessment (Assisted Living) and submitted the tour inquiry once as "TEST DO-NOT-CONTACT", with the owner's own inbox as the email and no phone.
- **Result (`VERIFIED` 2026-11-05):** PASS.
  - The server answered stored and verified (the record is written and read back), and the page showed "Your interest has been recorded." with the reference.
  - The notification reached the operator inbox within a second, with the same reference, addressed to that inbox only.
  - The browser contacted only this site and Google Fonts.
  - The function's only outbound calls are the site's own store and the email service.
  - Nothing went to Westminster Place.
- **Why:** U1. Nothing had shown the chain working since the 2026-10-30 move to Node 24.
- **Rejected or deferred:** reading or deleting the stored record. That needs the owner's export token, which was not requested. The record deletes itself after 180 days. The test's beacons carry the harness user agent, so they are excluded from visitor counts.
- **Revisit:** after any change to the inquiry form, the function, consent or the email setup.

### D-021 · 2026-11-05 · `APPROVED` (build only) · 30-day Evanston SEO Growth Sprint; Experiment 2 built for review
- **Decided:** the inquiry test is closed (D-020, U1). The owner opened a 30-day Evanston SEO Growth Sprint (2026-11-05 to 2026-12-05). He asked for one high-impact improvement, built on a separate branch, with no merge or deploy without his approval. Chosen and built: Experiment 2, the inspection-records guide (Section 4, [PR #12](https://github.com/JGBALL23/evanston-senior-care-guide/pull/12)).
- **Why this page:** Section 4's decision table already named it as the next experiment. It is the guide a family uses to vet a community before a tour, which is the step nearest a tour inquiry. Building it showed the live page sends families to a hospital-only site (U13), so it also corrects a factual error.
- **Why before Experiment 1's review:** the owner's sprint asked for the next build now. It is a different page, so the cost guide stays unchanged and measurable. Correcting a factual error is the stated exception to waiting.
- **Evidence:** the Hospital Report Card's own title and scope, read 2026-11-05; the statutes, rule and IDPH pages listed in Section 5's research row; the independent fact-check in PR #12.
- **Rejected or deferred:**
  - a title change, which needs the page's own queries and separate approval;
  - the assessment's link to the same site (U13), which is a separate approval;
  - publishing drafts or adding new pages during the sprint;
  - any change to the cost guide, PR #10, the daily drafts routine, the inquiry system or consent;
  - IndexNow (U4).
- **Revisit:** at the sprint read on 2026-12-05, and 8 weeks after release.

### D-022 · 2026-11-05 · `APPROVED` · Experiment 2 released, with the assessment's compare-link fix
- **Decided:**
  - Fix the assessment result's compare link inside PR #12 by pointing it at the corrected inspection guide (U13).
  - Verify the official links where possible and run every test.
  - If everything passes, merge and deploy once through the established upload, with no IndexNow.
- **Done (`VERIFIED` 2026-11-05):**
  - **The fix:** `9f552ba` changes the link and its test pins. It also corrects the one homepage sentence that described the old link. The beacon and its count file are unchanged; Section 3 notes the count's new meaning.
  - **Tests:** all 13 suites passed on `9f552ba`. A browser run of the assessment confirmed the new link opens the guide and fires its beacon.
  - **Links:** Care Compare and the IDPH pages return 200. The `ilga.gov` sources were read with the web tool that day (U11 stops the checker).
  - **Release:** merge `84b9e6b`, deploy `6aecc09906b589d0932fe784`. All 32 public files match `main`, apart from Netlify's privacy-link rewrite.
- **Why:** the owner's instruction of 2026-11-05.
- **Rejected or deferred:**
  - IndexNow (U4);
  - the facility-lookup check (the owner chose not to be interrupted; still in Pending verification);
  - the levels-of-care citation (U13 item 3);
  - any other change.
- **Revisit:** at the sprint read on 2026-12-05 and the 8-week review on 2026-12-31.

---

## 7. Next action

Completed on 2026-11-04: PR #11 merged as `971b14a` and released in deploy `6aebd5ef` (D-019); review on 2026-12-30. Completed on 2026-11-05: PR #12 merged as `84b9e6b` and released in deploy `6aecc099` with the assessment's compare-link fix (D-022); review on 2026-12-31.

**Exactly one action, when the owner has 10 minutes: one Search Console sitting for both experiment pages.** Nothing is blocked on it.

| | |
|---|---|
| Who | Owner. No site change. Report the figures in chat and Claude records them here as R5 and R6. |
| Pages | `https://evanstonseniorcareguide.com/guides/assisted-living-cost-illinois/` (R5) and `https://evanstonseniorcareguide.com/guides/check-illinois-inspection-records/` (R6) |
| Read | For each page, Performance filtered to the page: impressions, clicks, CTR, average position and the visible queries. For R6, set the date range to end on 2026-11-05, the release day, and add URL Inspection: indexed or not, and the last crawl date. |
| Why | R5 is Experiment 1's release baseline (R4's date range was not recorded). R6 is Experiment 2's before-release baseline. Search Console keeps the history, so both can still be read. |

After that both experiments only wait, and their pages stay unchanged until their reviews (2026-12-30 and 2026-12-31), except to correct a factual error. The sprint read on 2026-12-05 checks indexing and early impressions for both.

**Definition of done:**

- [ ] Section 3 has R5 and R6, each with its date range, and each visible query tagged Evanston, statewide or national.
- [ ] Section 4's baseline rows name R5 and R6.
- [ ] Section 7 names the sprint read on 2026-12-05 as the next action.
