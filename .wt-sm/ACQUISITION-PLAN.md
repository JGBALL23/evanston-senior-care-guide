# Acquisition, tours, and verifiable results

Written 2026-10-11. Every external fact here was checked against the live
source on that date, not recalled.

---

## The number first, because it decides everything else

Target: 30–60 additional completed tours per month.

Working backwards with ordinary rates — 1–3% of visitors become a qualified
inquiry, 30–50% of qualified inquiries become a completed tour — one tour
needs roughly **60 to 300 relevant visitors**. Thirty tours a month needs
somewhere around **2,000–9,000 relevant visitors a month**.

The site currently has no domain authority, no sitemap, no backlinks and a
`.netlify.app` subdomain. Its realistic organic traffic today is close to zero.

**This is not an argument against the target. It is an argument about where the
work goes.** Nothing you change in the copy produces 2,000 visitors. The
constraint is distribution, and almost every hour should go there.

The milestone that matters next is not 30 tours. It is **one verified tour**,
traced end to end. That single receipt is what makes the case for promotion;
thirty unverified ones make no case at all.

---

## PART 1 — The site as an acquisition system

### How families would discover it today: they would not

| Signal | State | Consequence |
|---|---|---|
| `robots.txt` | Allows crawling | Fine |
| `sitemap.xml` | **404** | Nothing tells Google what exists |
| Canonical tag | **None** | Duplicate-URL risk |
| Structured data (JSON-LD) | **None** | No rich result, no entity understanding |
| `og:url` | **Missing** | Shared links render worse on Facebook |
| Domain | `.netlify.app` subdomain | Weak trust signal to families and to search |
| Inbound links | None | No authority, nothing to rank on |

Page one for "assisted living Evanston" is held by A Place for Mom, Seniorly,
Care.com, SeniorLiving.org, Yelp and SeniorHomes. **Competing on that head term
is not winnable** and should not be attempted.

### The content is genuinely good, and it is the asset

2,188 words, five H2s, a working H1, an assessment, Illinois-specific cost
figures sourced to CareScout, and the Supportive Living mechanics explained
properly with the group care credit. **The aggregators do not produce this.**
They publish thin directory pages because their money is in the referral fee,
not in the explanation. That gap is the opening.

### The conversion gap, in order of impact

**1. There is no tour route on the page at all.** I searched the live HTML for
"schedule a tour", "request a tour", "book a tour", "tour request" — zero
matches. A family who reads everything, trusts it, and wants to visit has no
path. They get a phone number and a link to a community homepage.

**Westminster has an official request form**, verified today:
`https://www.presbyterianliving.org/our-locations/westminster-place/contact/`
It carries a real submission form (`gform_29`, class `communityForm`) under the
heading *"Get in touch. Let us know how we can serve you and your family."*
Your site does not link to it. **This is the single biggest hole.**

**2. Everyone gets the same phone number.** The site assesses a care level and
then hands all five outcomes `847-570-3422`. Westminster's own contact page
publishes a directory by care type:

| Published line | Number |
|---|---|
| General Inquiries | **847-570-3422** ← what the site uses for everyone |
| Independent Living Concierge | 847-492-2800 |
| Independent Living Sales | 847-570-3310 |
| **Assisted Living & Memory Care Sales** | **847-866-1615** |
| Skilled Nursing Admissions | 847-492-7780 |

A family routed to Memory Care currently calls a general line and waits to be
transferred to the people at 847-866-1615. **The assessment already knows which
line they need.** Routing by result uses only officially published numbers,
invents nothing, and removes a transfer from every call. This is the highest
return-per-hour change on the entire site.

*(Your current number is correct — it is labelled General Inquiries on their
page. The problem is that it is the only one.)*

**3. The capture form is switched off.** Right now there is no next step of any
kind. That was the right call while privacy was unresolved, and it means the
funnel presently ends in a dead end.

**4. Westminster appears only after six questions.** Someone who already knows
they want memory care in Evanston never sees it.

### Priority order

1. Link the official contact form from the Westminster card — **highest impact,
   lowest effort, no permission needed, it is a public page**
2. Route the phone number by assessed care level
3. `sitemap.xml`, canonical, `og:url`, JSON-LD — a day's work, prerequisite to
   any search traffic ever arriving
4. A real domain (~$12/year) — not an unnecessary expense; it is the floor for
   local trust
5. Turn the capture form back on, once the privacy items clear
6. A direct path to the Westminster section for people who skip the assessment

**None of this is a redesign.** Items 1 and 2 are a handful of lines each.

---

## PART 2 — Where qualified families actually come from

Head terms are lost. These are not.

### A. Long-tail questions the aggregators answer badly

They publish directory pages. They do not explain Illinois. Each of these is a
page you can genuinely win because almost nobody has written it properly:

- "does medicaid pay for assisted living in illinois"
- "illinois supportive living program room and board cost"
- "what is a group care credit illinois"
- "difference between assisted living and memory care"
- "when is it time for memory care"
- "mom can't live alone anymore what are my options"
- "how much does memory care cost in illinois"
- "medicare 100 days skilled nursing rules"
- "questions to ask on a nursing home tour"

You already own the hardest research for most of these. The group care credit
explanation is better than anything on page one right now.

**Why this converts:** someone searching "when is it time for memory care" is
earlier and more winnable than someone searching "assisted living Evanston",
who is already three directory sites deep and about to be sold a referral.

### B. Distribution that does not need search, a domain, or months

This is where the near-term tours come from.

**Facebook caregiver groups.** "Caring for Elderly Parents", "Dementia
Caregivers Support Group", Illinois and Chicago-area caregiver groups.
Message the admin first, state plainly who you are and that you work at a
senior living community, and ask whether a free non-commercial resource is
welcome. Some will say no. The ones that say yes have exactly your audience,
and they are asynchronous — you answer when you have time, never on a call.

**Nextdoor, Evanston and adjacent neighbourhoods.** The single most
geographically precise free channel available for this. People ask about care
for a parent constantly.

**Reddit:** r/Evanston, r/ChicagoSuburbs, r/CaregiverSupport, r/dementia.
Answer questions properly and link the specific page that helps. Never drop a
link alone.

**Evanston Public Library and the Levy Senior Center.** Both maintain
caregiver resource lists. A short, honest email asking to be listed. No
meeting, no call.

**Hospital discharge planners and social workers** at NorthShore/Endeavor
Evanston. They are the highest-intent referral point that exists — they meet
families on the worst day, with hours to decide. A one-page email introducing a
free resource. Expect a low response rate and a very high value when it lands.

**Township and senior services offices** in Evanston, Skokie, Wilmette.
Email, asynchronous, free.

**Answer questions where families already ask them** — Quora, Caring.com
community threads, Alzheimer's Association forums. Slow, compounding, free.

**What not to do, and you already said it:** no mass unsolicited messages, no
fake reviews, no posting without admin permission, and never any implication
you speak for Westminster. One violation ends the whole project and the job
with it.

### C. The disclosure is an asset here, not a liability

Every aggregator ranking above you is paid by communities. You are not, and you
say so. In caregiver groups, "I work at a senior living community and built
this; here is exactly what I get out of it" outperforms a polished anonymous
resource. Lead with it.

---

## PART 3 — The funnel

Desired path: search → guide → trust → interest → **official Westminster
request** → completed tour → move-in.

Two things move that are not a redesign:

**Route to the right people.** The assessment produces a care level. The care
level should produce the matching published phone line and a direct link to
Westminster's official contact form. Today it produces a general number and a
homepage link.

**Make the request route obvious and honest.** Something close to:

> **Ready to look at Westminster Place?**
> Request a visit through Westminster Place directly →
> *(their official form; this guide does not schedule appointments)*
> Or call Assisted Living & Memory Care Sales: 847-866-1615

That is a real next step. It routes to an authorized channel, it schedules
nothing here, it claims nothing, and the employment disclosure sits directly
above it unchanged.

**The attribution record and the tour request are different things and should
both exist.** The official form is how a tour actually gets booked. Your
timestamped record is the evidence it started here. One does not replace the
other.

---

## What I need from you

1. **Does Westminster's employee and marketing policy permit this?** Still
   outstanding, and now it gates real traffic rather than a dormant page.
2. **Will you buy a domain?** ~$12/year. Everything in Part 2A depends on it.
3. **Which channel in Part 2B do you want first?** Pick one. I will prepare the
   exact message, and you send it — no calls, no meetings.

**Nothing in Part 1 or Part 3 has been changed yet.** You said not to redesign
automatically, so the analysis is here and the code is untouched. Say which
items to implement and they go in.
