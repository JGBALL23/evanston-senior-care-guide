# What can be proved, and what cannot

2026-10-12. Deploy `6acd49c12262f7d4b99f2b0d`.

---

## The attribution finding — tested, not assumed

You asked whether a source parameter can actually be captured by Westminster's
form. I pulled the form and read its fields. The answer is **no**, and here is
the evidence.

| What I checked | What I found |
|---|---|
| Does their form have a "How did you hear about us?" field | **Yes** — `input_24`, labelled *"How Did You Hear About Us?"*, and it is **required** |
| What kind of field is it | A **dropdown with ten fixed options**: Referral from friend / family / resident / a professional, Newspaper, Internet search, Direct Mail, Community website, Other |
| Is "Evanston Senior Care Guide" an option | **No** |
| Can a URL parameter populate it | **No.** `gform_field_values` is present but **empty**, and `allowsPrepopulate` and `inputName` appear **zero times** in the page. No field is configured for dynamic population |
| Would `?src=evanston-senior-care-guide` do anything | **Nothing.** It would be ignored, and a free-text value could not enter a fixed-option dropdown anyway |

**So: submissions made on Westminster's official form, and phone calls placed
from this site, cannot be credited to the guide at the individual-prospect
level.** Not currently, and not by any change I can make on my side.

No source parameter was added to the link, because adding one would create the
appearance of tracking that does not exist.

### The one honest partial signal

Their dropdown does contain **"Community website"**, which is an accurate
description of where a visitor from this guide came from. The site now says so
plainly, as information rather than instruction, and notes that picking it
changes nothing about how they are treated.

If Westminster later reports a rise in "Community website" responses, that is
**corroborating** evidence. It is not proof, and it is not per-prospect. It
will never name you.

---

## The four stages, and what each one is worth

### 1. Visitor clicked Westminster's official inquiry link — **PROVABLE**
A beacon fires on `/t/westminster-inquiry-form-click.txt`, carrying the channel
token only.

**What it proves:** someone on the guide chose to open Westminster's request
form. **What it does not prove:** that they submitted it, that Westminster
received anything, or that a person exists behind the click. An outbound click
is **not a lead** and must never be reported as one.

*Caveat:* the beacon is live, but **nothing counts it yet** — no analytics is
installed. Until that changes, even the click is unmeasured.

### 2. Visitor submitted a verified inquiry originating through the guide — **NOT CURRENTLY PROVABLE**
Two separate reasons, and both must be fixed before this stage exists:

- **Their form cannot carry the source** (the finding above). An inquiry
  submitted on Westminster's site is, from your side, anonymous.
- **Your own named-submission architecture is switched off** — deliberately,
  until privacy, deletion, secure export, consent and employer-policy items are
  resolved. It is built, tested, and preserved exactly as it was.

When it is switched on, it proves something narrower and stronger than their
form could: **a named person recorded an intention, with a server-generated ID
and timestamp, before any visit.** That is yours, and it pre-dates the walk-in.

### 3. Westminster confirmed a completed tour — **ONLY THEY CAN ESTABLISH THIS**
Requires an authorized process. No software on your side can produce it, and no
amount of click data substitutes.

### 4. Westminster confirmed a move-in — **ONLY THEY CAN ESTABLISH THIS**
Same, with higher stakes: a move-in means a resident, and resident information
is protected.

**These four never collapse into each other.** A click is not an inquiry. An
inquiry is not a tour. A tour is not a move-in. And none of them is revenue.

---

## What shipped today

**Conversion**
- A prominent CTA from every result to Westminster's **own** inquiry form,
  stating in the card that the form belongs to Westminster and that submitting
  it **does not guarantee a tour or confirm a time**
- Phone routing by assessed care level, using only numbers Westminster
  publishes in its own directory:

| Result | Line called | Number |
|---|---|---|
| Independent Living | Independent Living Sales | (847) 570-3310 |
| Assisted Living | Assisted Living & Memory Care Sales | (847) 866-1615 |
| Memory Care | Assisted Living & Memory Care Sales | (847) 866-1615 |
| Skilled Nursing | Skilled Nursing Admissions | (847) 492-7780 |
| Short-Term Rehabilitation | Skilled Nursing Admissions | (847) 492-7780 |

Each re-verified verbatim from their contact page on 2026-10-12. An unknown
level falls back to General Inquiries, (847) 570-3422.

**Unchanged, as instructed:** quiz scoring, sourced costs, educational content,
and the disclosure that you work at Westminster Place and developed this
resource independently. Nothing implies company endorsement.

**Still staged, untouched:** the sharing consent, privacy notice, 180-day
purge, and named-submission collection.

**Verified:** 307 unit checks · 103 browser checks at 375, 390 and 430 · a live
routing audit walking all five care levels on the deployed site.

---

## Measurement — your point 6 was right

Cloudflare Web Analytics gives pageviews and referrers. It has **no custom
events**, so it cannot count assessment completions or CTA clicks. Installing
it alone would leave the funnel unmeasured.

What the beacons need is a counter that sees **requests for specific paths**.
Three options that do that:

| Option | Cost | Counts `/t/*` paths |
|---|---|---|
| **Netlify Analytics** | $9/mo, server-side logs | **Yes** — it reads the request log, which is exactly what the beacons were built for |
| **GoatCounter** | Free | Yes, via explicit event calls |
| **Plausible, self-hosted** | Free + a server | Yes, custom events |

**Netlify Analytics is the honest recommendation** at $9/month: the beacon
architecture was designed for server-log counting, it requires no script, no
cookie, and no change to the privacy notice's "no analytics service" line,
because there is no client-side tracker.

Pair it with Google Search Console, which is free and shows real queries.

**Decide this before distribution starts.** Sending traffic at an unmeasured
funnel produces no evidence of anything.
