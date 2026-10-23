# Attribution, growth model, and the 30-day plan

Written 2026-10-11. Companion to `ACQUISITION-PLAN.md`.

---

## 0. The finding that changes the order of everything

**There is no measurement on this site, and there never has been.**

Checked today: `analytics_instance_id: None`. Netlify Analytics is not enabled.
The funnel beacons in `/t/` all return 200 — they fire correctly — but nothing
has ever counted them. They were built to be read from the host's server logs,
and that log access does not exist on this plan.

So: **zero visitors recorded, zero assessment completions recorded, zero
baseline.** Not "low traffic" — *unmeasured* traffic. Those are different, and
only one of them can be fixed this week.

Everything in section 5 is therefore an assumption, labelled as one. Week 1
exists to replace assumptions with measurements.

---

## 4. Attribution — your name on the evidence

### What every record must carry

```
source:        "Evanston Senior Care Guide"
developedBy:   "Joseph Gonzales"
submissionId:  <server-generated UUID>
receivedAt:    <server timestamp>
stage:         "recorded_intention"
```

`developedBy` is a new constant in `plan-visit.mjs` and in the notification.
It costs nothing, adds no friction, and means every artefact that ever reaches
leadership names you without anyone having to remember to say it.

### The four stages, and the wall between them

| Stage | What it means | Who can establish it | Status |
|---|---|---|---|
| **1. Consented inquiry** | Someone gave their details voluntarily, with consent recorded | **You** — the existing architecture already does this | Built, switched off |
| **2. Recorded intention** | They said they plan to visit, timestamped before the visit | **You** | Built, switched off |
| **3. Verified completed tour** | They physically toured | **Westminster only** | Needs authorization |
| **4. Verified move-in** | They became a resident | **Westminster only** | Needs authorization |

**Stages 1–2 are yours. Stages 3–4 are not, and no amount of software changes
that.** The system must label every record with its stage and must never let a
stage-2 record be counted or displayed as stage 3.

Three sentences never to write:

- A planned visit is not a completed tour.
- An anonymous click is not a verified lead.
- A lead is not revenue.

### Attribution without friction

The strongest attribution available that costs a family nothing:

1. **The timestamped record** — already built. The strength is that it exists
   *before* the visit; that is the part nobody can reconstruct afterwards.
2. **A dedicated landing path.** When the Westminster card links to their
   official contact form, append a plain source parameter:
   `?src=evanston-senior-care-guide`. If their form captures it, you have a
   second independent trail. If it does not, you have lost nothing.
3. **"How did you hear about us?"** — if Westminster's form has that field,
   the ask on your page is one sentence: *"If they ask how you heard about
   them, mentioning this guide helps me show it's worth keeping up."* No code,
   no pass, nothing to carry, and a family can ignore it with no consequence.

**No referral codes. No visitor passes. No coworker ever handles anything.**
That constraint is correct and it is not negotiable.

---

## 5. The growth model

### Every rate below is ASSUMED. Zero are measured.

There is no baseline. These are ordinary ranges for an informational site with
a local service intent, used to size the problem, not to predict your results.

| Step | Conservative | Moderate | Optimistic |
|---|---|---|---|
| Relevant visitor → completes assessment | 15% | 25% | 35% |
| Completion → qualified inquiry *(calls, or opens Westminster's form)* | 5% | 10% | 18% |
| Qualified inquiry → tour request submitted | 40% | 55% | 70% |
| Tour request → **completed** tour | 50% | 65% | 80% |
| **Visitor → completed tour** | **0.15%** | **0.89%** | **3.53%** |
| **Visitors needed per tour** | **~667** | **~112** | **~28** |

### What each target requires, in monthly relevant visitors

| Goal | Conservative | Moderate | Optimistic |
|---|---|---|---|
| **1 tour / month** | ~670 | ~112 | ~28 |
| 5 tours / month | ~3,300 | ~560 | ~140 |
| **30 tours / month** (1/day) | **~20,000** | **~3,400** | **~850** |
| **45 tours / month** (1.5/day) | **~30,000** | **~5,100** | **~1,300** |

### Is the target realistic?

**Not in 30 days. Not organically in 90.** Thirty tours a month needs between
850 and 20,000 relevant visitors a month on a site that currently has no
domain, no index presence and no measurement. The low end of that range is
only reachable with conversion rates at the top of what this kind of site ever
achieves.

**What is realistic:** 1–5 completed tours per month within 90 days, through
distribution rather than search. That requires 112–3,300 visitors a month —
the bottom of which a few active caregiver groups can produce.

**30–60/month is a 12-to-18-month destination, and it needs paid acquisition or
a genuine search position — neither of which exists yet.** Say that to
leadership before someone else does the arithmetic. A promotion case built on
"I generated the first four verified tours and here is the system that did it"
survives scrutiny. One built on a projection does not.

### The data needed to replace these guesses

1. **Visitors and sessions** — Cloudflare Web Analytics, free, cookieless.
2. **Search impressions, clicks and actual queries** — Google Search Console,
   free. This also tells you which long-tail pages to write next.
3. **Funnel steps** — the `/t/` beacons, once something counts them.
4. **Outbound clicks** — to Westminster's form and the phone links.
5. **Stage 3 and 4** — Westminster, under authorization. Nothing else can.

Items 1–4 are free and installable this week. Until then every number in this
section stays labelled an assumption.

---

## 6. The 30-day plan

Built for someone working long shifts. Nothing here needs a phone call, a
meeting, or more than 90 minutes in one sitting.

### Week 1 — Measure, and unblock the funnel
*Theme: you cannot improve what nothing counts.*

| # | Action | Why | Cost | Time | Needs Westminster? | Measured by |
|---|---|---|---|---|---|---|
| 1.1 | Install **Cloudflare Web Analytics** | The only way to get a baseline. Cookieless, so no consent banner | Free | 20 min | No | Visitor count exists at all |
| 1.2 | Verify in **Google Search Console**, submit a sitemap | Shows real queries and whether Google has indexed anything | Free | 30 min | No | Impressions reported within ~7 days |
| 1.3 | Generate `sitemap.xml`, add canonical + `og:url` + JSON-LD | Without these, nothing gets crawled properly | Free | 45 min | No | Pages indexed in GSC |
| 1.4 | **Link Westminster's official contact form** from the result card | The biggest conversion hole. Verified live today | Free | 30 min | **No** — public page | Outbound clicks |
| 1.5 | **Route the phone number by care level** | Removes a transfer from every call. Published numbers only | Free | 30 min | No | Calls by line |
| 1.6 | Buy a domain | `.netlify.app` costs trust with families and with search | ~$12/yr | 15 min | No | — |
| 1.7 | Add `developedBy: "Joseph Gonzales"` to the record schema | Your name on every artefact, permanently | Free | 10 min | No | Appears in export |

**Week 1 total: about 3 hours.** Items 1.4 and 1.5 are the only ones that touch
what a visitor sees, and both are small.

### Week 2 — First channels and first content
*Theme: traffic, not features.*

| # | Action | Why | Cost | Time | Needs Westminster? | Measured by |
|---|---|---|---|---|---|---|
| 2.1 | Write **"Does Medicaid pay for assisted living in Illinois?"** | High intent, badly served, and you already did the research | Free | 90 min | No | GSC impressions for that query |
| 2.2 | Message **3 caregiver Facebook group admins** asking permission | Asynchronous, free, exactly your audience | Free | 30 min | No | Replies, then referral traffic |
| 2.3 | Post in **Nextdoor Evanston** with the disclosure up front | Most geographically precise free channel | Free | 20 min | No | Referral traffic |
| 2.4 | Email **Evanston Public Library + Levy Senior Center** to be listed | They maintain caregiver resource lists | Free | 30 min | No | A link, or a reply |
| 2.5 | Answer 3 real questions on Reddit / caregiver forums | Compounds, builds authority, costs nothing | Free | 45 min | No | Referral traffic |

**Week 2 total: about 3.5 hours.**

### Week 3 — Expand what works, fix what leaks
*Theme: double down on the channel that actually sent people.*

| # | Action | Why | Cost | Time | Needs Westminster? | Measured by |
|---|---|---|---|---|---|---|
| 3.1 | Read Week 2 data. **Drop the dead channels** | Most will produce nothing. Cutting them is the win | Free | 30 min | No | Visitors by referrer |
| 3.2 | Triple down on the single best channel | Concentration beats spread at this size | Free | 60 min | No | Visitors from it |
| 3.3 | Write article #2, chosen from **real GSC queries** | Data-selected, not guessed | Free | 90 min | No | Impressions |
| 3.4 | Find the biggest drop-off in the beacon funnel and fix one thing | By now there is actual funnel data | Free | 45 min | No | Step-to-step rate |
| 3.5 | **Ask Westminster for the two authorizations** | Stages 3–4 are impossible without it, and it takes time | Free | 45 min | **Yes** | A written answer |

**Week 3 total: about 4.5 hours.**

### Week 4 — Judge it honestly, then decide
*Theme: what is the measured truth, and what does it justify.*

| # | Action | Why | Cost | Time | Needs Westminster? | Measured by |
|---|---|---|---|---|---|---|
| 4.1 | Compile the real numbers against the assumed table above | Replaces every guess in section 5 | Free | 45 min | No | A table with no assumptions |
| 4.2 | If privacy items are resolved, **turn collection on** and verify end to end | Stage 1–2 evidence starts accumulating | Free | 60 min | Privacy, not Westminster | A real record, correctly staged |
| 4.3 | Write the one-page summary for leadership | Measured results only, stages never conflated | Free | 45 min | No | It survives questions |
| 4.4 | Pick the single Month-2 lever from the data | Avoids restarting from scratch | Free | 30 min | No | One decision, written down |

**Week 4 total: about 3 hours.**

**Whole month: roughly 14 hours.** Under four hours a week.

---

## 7. Independent vs permission-dependent

### A. Do without asking anyone
Educational content, performance, SEO, sitemap, structured data, the domain,
analytics, copy, the assessment, linking to Westminster's **public** pages and
published phone numbers, and distributing a disclosed independent resource in
community spaces where the host permits it.

**Every item in Weeks 1 and 2 is in this bucket.** None of it requires
representing Westminster or touching their data.

### B. Keep staged until authorized
The sharing consent, the reconciliation, any transfer of prospect data, any
integration with Westminster systems, verifying tours or move-ins, and anything
that reads as official marketing.

**Already staged and not deployed.** It stays that way.

### The line that keeps you safe
You are the author of an independent resource that *discloses* you work at
Westminster. You are not Westminster's marketing department, and nothing on the
site may imply it. That distinction is what makes Bucket A genuinely free to
move on — and it is why the disclosure is an asset rather than a cost.

---

## 8. Development stops here

No new features unless they serve acquisition, conversion, credibility or
attribution. By that test:

**Justified** — the Westminster form link (conversion), care-level phone
routing (conversion), analytics (measurement, which gates every other
decision), sitemap and structured data (acquisition), `developedBy` in the
schema (attribution).

**Not justified, not being built** — anything else. No dashboards, no new
tooling, no refactors, no more audits.

**Preserved exactly as-is:** the assessment and its scoring, the educational
content, the CareScout-sourced costs and Supportive Living explanation, the
employment disclosure, and the timestamped attribution architecture.

Every public change gets tested before deployment, as before. Collection stays
off until privacy, deletion and employer-policy items are resolved.

---

## What I need from you to start Week 1

1. **Yes or no on the domain** (~$12/yr).
2. **Yes or no on Cloudflare Analytics** — free, cookieless, but it changes the
   privacy notice's "no analytics service" line, so the staged notice updates
   with it.
3. **Which of items 1.4 and 1.5 to implement first** — or say "both" and they
   ship together, tested, in one pass.
