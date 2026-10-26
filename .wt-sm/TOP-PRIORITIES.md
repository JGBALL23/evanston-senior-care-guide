# The five opportunities, the three actions, and a correction

2026-10-11. Decision document. Companions: `ACQUISITION-PLAN.md` (funnel
assessment), `ACQUISITION-EXECUTION.md` (growth model, 30-day plan).

The test applied to every item below: **will this help Joseph Gonzales generate
real prospective residents and completed tours for Westminster Place, and will
there be credible evidence his work produced them?** Anything that failed that
test is not here.

---

## A correction to my own earlier plan

In `ACQUISITION-PLAN.md` I listed Facebook caregiver groups, Nextdoor, Reddit
and library listings as channels. **I had not verified a single one of them.**
No membership figures, no confirmation those groups exist, no evidence any
would accept a post. You told me not to invent audience reach, and naming
channels I had not checked is the same failure in a quieter form.

What follows separates what I actually verified from what remains a
hypothesis.

### Verified today, by fetching the source

| Fact | Evidence |
|---|---|
| Westminster has an official request form | `presbyterianliving.org/our-locations/westminster-place/contact/` → 200, carries `gform_29` class `communityForm` |
| Westminster publishes phone lines by care type | Same page: General 847-570-3422 · IL Concierge 847-492-2800 · IL Sales 847-570-3310 · **AL & Memory Care Sales 847-866-1615** · SNF Admissions 847-492-7780 |
| The guide links to none of it | Live HTML search for "schedule a tour", "request a tour", "book a tour", "tour request" → **0 matches** |
| City of Evanston runs Senior Services at the Levy Center | `cityofevanston.org/departments/prcs/facilities/levy_senior_center/senior_resources.php` → 200 |
| It publishes an email contact | **`aging@cityofevanston.org`**, found on that page's own HTML |
| The city links Evanston Public Library as a resource | Outbound link to `epl.org` on the same page |
| The site has no measurement | `analytics_instance_id: None` |
| The site has no sitemap | `/sitemap.xml` → 404 |

### NOT verified — treat as hypotheses until tested

- Any specific Facebook caregiver group: existence, size, or willingness
- Nextdoor Evanston reach
- Whether EPL accepts external resource listings (their old community
  organizations directory now returns **404 — page no longer exists**)
- Whether hospital discharge planners would respond
- Search volume for any keyword — I have no keyword tool and did not guess one

**No conversion rate anywhere in these documents is measured. Every one is an
assumption, labelled as such.**

---

## The five highest-impact opportunities

Ranked by tours generated per hour of your time.

### 1. Link Westminster's official request form from the result
A family who reads the guide, trusts it, and wants to visit currently has **no
path**. They get a general phone number and a link to a community homepage.
The form exists and is public.

*Impact:* this is the conversion event. Without it the funnel has no exit.
*Cost:* free. *Time:* 30 min. *Authorization:* **none** — a public page.
*Evidence produced:* outbound clicks, and a tour request that lands in
Westminster's own system.

### 2. Route the phone number by assessed care level
The assessment determines the care level, then hands all five results the same
general line. A memory-care family should reach **847-866-1615** directly.

*Impact:* removes a transfer from every call, at the exact moment intent is
highest. *Cost:* free. *Time:* 30 min. *Authorization:* none — published
numbers. *Evidence:* calls by line.

### 3. Install measurement — Cloudflare Analytics + Google Search Console
Both free. Right now **every beacon fires into nothing** and no decision after
this week can be made on evidence.

*Impact:* indirect but gating. Without it, items 4 and 5 cannot be judged.
*Cost:* free. *Time:* 50 min. *Authorization:* none. *Evidence:* a baseline
that replaces the assumptions in the growth model.

### 4. Email `aging@cityofevanston.org` — the one verified channel
The City of Evanston's Senior Services division publishes this address on its
own Senior Resources page. One honest email: who you are, that you work at
Westminster Place, that you built a free independent guide, and would they
consider listing it.

*Impact:* if listed, it is pre-qualified local traffic from a trusted
municipal source — the highest-quality free referral available.
*Cost:* free. *Time:* 20 min. *Authorization:* none — you are not
representing Westminster, you are disclosing that you work there.
*Evidence:* a reply, then referral traffic in analytics.
*Honest note:* I verified the address and the page. I have **no evidence** they
list external resources. The email costs twenty minutes to find out.

### 5. Write the Illinois Medicaid / Supportive Living article
You already did the hardest research: the group care credit, the $874 and
$625.50 room-and-board figures, the HFS citations. Almost nothing on page one
explains it properly, because the directory sites earn referral fees, not
explanations.

*Impact:* the only durable organic asset in this list. Slow, compounding.
*Cost:* free. *Time:* 90 min. *Authorization:* none.
*Evidence:* Search Console impressions for those queries.
*Honest note:* I did not measure search volume for these terms and will not
guess at it. Search Console will tell you within weeks, for free.

---

## The three actions to complete immediately

**1. Link the Westminster request form + route the phone by care level.**
One change, one test pass, one deploy. About an hour. No permission needed.
This is the difference between a guide and a funnel.

**2. Install Cloudflare Web Analytics and verify Google Search Console.**
Fifty minutes, free. Everything after this week depends on having numbers.
*Note:* this changes the staged privacy notice's "there is no analytics
service" line — the notice updates in the same change, which is why they ship
together.

**3. Send one email to `aging@cityofevanston.org`.**
Twenty minutes. The only verified distribution channel in the entire plan.
Asynchronous, no call, no meeting.

**Total: about two hours.** All three are independent work.

---

## Independent vs requires authorization

### Independent — start now, ask nobody
Opportunities 1 through 5, all of it. Content, SEO, sitemap, analytics, the
domain, copy, linking Westminster's **public** pages and **published** phone
numbers, and distributing a disclosed independent resource where the host
permits it. You are the author of an independent guide that discloses your
employment. That is not marketing on Westminster's behalf.

### Requires Westminster authorization — stays staged
Sharing prospect data, the reconciliation, integration with their systems,
verifying tours or move-ins against their records, and anything that reads as
official marketing. Already built, already switched off, stays that way.

### Requires you, not Westminster
Turning collection back on: the privacy notice, deletion contact, and the two
environment variables. Those block stages 1–2 evidence, and no one else can
clear them.

---

## The website improvements worth making, in order

1. **Westminster request-form link** — conversion. The missing exit.
2. **Care-level phone routing** — conversion. Removes a transfer.
3. **Analytics + Search Console** — measurement. Gates every later decision.
4. **sitemap.xml, canonical, og:url, JSON-LD** — acquisition. Nothing is
   crawled properly without them.
5. **`developedBy: "Joseph Gonzales"` in the record schema** — attribution.
   Ten minutes, and your name is on every artefact permanently.
6. **A real domain** (~$12/yr) — credibility with families and with search.

**Not being built:** anything else. No dashboards, no new tooling, no further
audits. The assessment, the educational content, the sourced costs, the
disclosure and the attribution architecture are preserved exactly as they are.

**Items 1 and 2 are roughly fifty lines of code between them.** Say go and they
ship together, tested at 375/390/430, verified live.
