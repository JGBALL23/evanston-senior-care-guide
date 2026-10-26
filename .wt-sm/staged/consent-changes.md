# SUPERSEDED 2026-10-16 — kept as a record of the retired design

**Do not implement anything in this file.** It describes a two-consent
design: a required attribution consent plus an *optional* tickbox allowing
Westminster to be given a name and a submission date, so visits could be
reconciled after the fact.

That was built for a workflow where nothing was ever handed over. The
workflow changed: the form now exists **so that** the family's name, phone
and email are passed to Westminster Place Admissions, who contact them about
a tour. Sharing is the purpose, not a side errand, so there is exactly one
consent and it authorises the transfer in plain words. A second optional box
would imply the first one permits less than it does.

What carried forward from this file, and still holds:

- Name the exact fields that move. "Limited information" means nothing.
- Name it as a transfer. The word "automatically" was doing too much work.
- Say what is *not* shared, because the omission is the reassurance.
- The notification email carries no personal information at all — that
  decision came from here and is live in `plan-visit.mjs`.

What did NOT carry forward: the optional checkbox, `shareConsent` as a
stored field, and the `?format=reconcile` export view. `test.js` asserts
`shareConsent` appears nowhere in live code.

The original text follows, unedited.

---

# The optional sharing consent — exact copy and exact code

Not deployed. See `README.md` for the three conditions.

## What the visitor sees

The existing consent stays exactly as it is and remains **required**. A second
checkbox is added below it, **optional and unchecked by default**.

> ### Optional: help confirm this guide actually works
>
> ☐ **You may share my name and the date I submitted this form with
> Westminster Place, for the sole purpose of confirming whether I visited.**
>
> Leave this unticked and nothing is ever shared. Your planned visit is still
> recorded, you can still visit, and nothing about your experience changes.
>
> **If you tick it, here is exactly what happens.** Your **first name, last
> name and submission date** — nothing else — may be given to an authorised
> member of Westminster Place staff, who checks whether that name appears in
> their own records and tells me only **whether it does**. Your email address
> and phone number are never shared. Your assessment answers are never shared;
> they never left your device in the first place. No health information is
> shared, because none was ever collected.
>
> **To be plain about what this is:** your name and submission date would be
> included in a short list given to Westminster Place staff. It is a transfer
> of your information to them, limited to those two things and to people who
> ticked this box. It is not anonymous, and this notice is not telling you
> otherwise.
>
> This happens at most once per submission, no sooner than 30 days after your
> planned visit date, and only while Westminster Place has authorised the
> process. You can withdraw this permission at any time by writing to the
> address in the privacy notice.

## Why the wording is shaped this way

- **"may share"**, not "will share". Sharing also requires employer
  authorisation. Promising it unconditionally would be a second contradiction.
- **The exact fields are listed.** "Limited information" means nothing to a
  reader. First name, last name, submission date — a reader can picture it.
- **What is NOT shared is listed too**, because the omission is the reassurance.
- **It is named as a transfer.** An earlier draft of this described it as
  Westminster merely answering yes or no, with "no record transferred". That
  was wrong: handing over a list of names *is* transferring personal
  information, however short the list. Softening that is the same failure as
  the word "automatically" this consent exists to fix.
- **Declining costs the visitor nothing**, and that is said plainly. A consent
  that feels load-bearing is not freely given.

## Code changes

### 1. `app.js` — the field

Inside `#plan-form`, directly after the existing `.plan__check` block:

```html
<div class="plan__optional">
  <p class="plan__optional-h">Optional: help confirm this guide actually works</p>
  <label class="plan__check">
    <input type="checkbox" name="shareConsent" id="plan-share">
    <span>You may share my name and the date I submitted this form with
      Westminster Place, for the sole purpose of confirming whether I
      visited.</span>
  </label>
  <p class="plan__optional-note"><!-- the three paragraphs above, verbatim --></p>
</div>
```

And in the payload, one added line:

```js
shareConsent: form.elements.shareConsent.checked
```

### 2. `netlify/functions/plan-visit.mjs` — accept and store it

```js
const ALLOWED_KEYS = [
  "firstName", "lastName", "email", "phone", "plannedVisitDate",
  "consent", "shareConsent"
];
```

In the stored row:

```js
shareConsent: payload.shareConsent === true,
shareConsentAt: payload.shareConsent === true ? receivedAt : null,
```

`shareConsent` is **not** required. Unlike `consent`, a missing or false value
is valid and simply means no sharing. It must never be defaulted to `true`,
and there must be no code path that infers it.

### 3. `netlify/functions/plan-visit-export.mjs` — a reconciliation view

Add `?format=reconcile`, which returns **only rows where `shareConsent` is
true**, and **only three fields**: first name, last name, submission date.

```js
if (format === "reconcile") {
  const rows = records
    .filter((r) => r.shareConsent === true)
    .map((r) => ({
      firstName: r.firstName,
      lastName: r.lastName,
      submittedOn: r.receivedAt.slice(0, 10)
    }));
  return json(200, { ok: true, count: rows.length, rows });
}
```

This matters more than it looks. It means the list you hand to Westminster is
produced **by code that physically cannot include** an email address, a phone
number, or a person who did not consent. You are not trusted to remember —
the endpoint cannot do otherwise.

It does not make the hand-over zero-transfer. It bounds it.

### 4. `test.js` — the gates to add

- `shareConsent` defaults to false and is never required
- a submission without `shareConsent` stores `shareConsent: false`
- `?format=reconcile` returns only consented rows
- the reconcile output contains no email, no phone, no care level, no answers
- the consent copy names the three shared fields verbatim
- the copy states that declining changes nothing
- the live page says sharing is **not** automatic and **not** default

## The live wording that changes at the same time

Current, in the Westminster disclosure:

> It is not automatically shared with Westminster Place.

Becomes:

> It is not shared with Westminster Place unless you specifically allow it on
> the form below, and that box is unticked by default.

The weasel word goes. The promise gets stronger and stays true.


---

## Notification email: reduced to a pointer

**Decided 2026-10-09.** The notification carries no personal information at
all. Not the name, not the email, not the phone number.

```
Subject: New Westminster Visit Lead — Evanston Senior Care Guide

A new visit intention was submitted through the Evanston Senior
Care Guide.

Submission ID: 56670960-6a74-4995-9953-ade7f830e2c4
Submitted: 2026-10-08T15:47:53.854Z
Source: Evanston Senior Care Guide

No personal information is included in this message by design.
Retrieve the name, contact details and planned visit date from the
authorised export using the submission ID above.
```

`notificationText()` in `plan-visit.mjs` drops the name, email, phone and
planned-visit lines, and the Web3Forms payload drops `name`, `email`, `phone`
and `planned_visit`. What remains is an identifier and a timestamp — which
identify a record, not a person, to anyone without the export token.

**The complete original submission is unaffected.** Name, email, phone,
planned visit date, server ID and server timestamp all stay in the Netlify
store, retrievable through the authorised export. The timestamped evidence is
not weakened by this; it is simply no longer duplicated into two systems that
do not expire on your schedule.

### Why this is not optional

Web3Forms' published retention, checked 2026-10-09:

| | |
|---|---|
| Default retention | **3 years** from submission |
| Shortest configurable | 7 days per form |
| Dashboard history, free plan | 30 days — **separate from retention**; data persists after it leaves the dashboard view |
| Account information | Kept for the life of the account |

Three years against a 180-day policy. Every notification containing a name and
phone number would outlive the record it describes by **more than six times
the retention period**, in a system whose deletion you do not control.

Sending only an ID and a timestamp resolves it at the source: there is no
personal information in their systems to retain, so the mismatch cannot arise.

### Provider limitation to disclose

Even with the minimal notification, Web3Forms processes and retains the
message metadata — destination address, timestamps, delivery status — under
their terms, not this site's. The privacy notice states this rather than
implying the 180-day rule governs every system involved.

**Also set, belt and braces:** in the Web3Forms dashboard, set this form's
retention to the shortest available period. The design means there is nothing
sensitive to expire, and it costs nothing to shorten it anyway.

### Gates to add with it

- the notification body contains no `@`
- the notification body contains no run of seven or more digits
- the notification body contains neither `record.firstName` nor `record.lastName`
- the Web3Forms payload carries no `email`, `phone` or `name` key
- the stored record still contains all six fields — minimisation applies to
  the notification only, never to the evidence
