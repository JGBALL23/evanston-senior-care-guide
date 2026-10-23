# Tour inquiry — production readiness audit

> **Updated 2026-10-16.** The form became a tour-inquiry request: the
> planned-visit-date field is gone, and the single required consent now
> authorises passing the family's name, phone and email to Westminster Place
> Admissions. Rows below that were verified against the live site on
> 2026-10-09 describe the *previous* form; the mechanism they verify
> (server UUID, server clock, read-back, refusal paths, locked export) is
> unchanged and still asserted by `test.js`. Re-verify against the live
> deployment after the next deploy before quoting any of it.

Audited 2026-10-09 against the live deployment, not against source.
Site: https://evanston-senior-care-guide.netlify.app
Netlify project `evanston-senior-care-guide` (`e25a95a5-7a87-4d1c-bae7-8c35d496dded`)

Every line below that says "verified" was produced by a real request to the
live URL on the date shown. Nothing here is inferred from reading code.

---

## The four states, and why they are not the same thing

This is the most important section. Conflating these is how an attribution
claim gets destroyed in a meeting.

| State | What it means | Can this system prove it today |
|---|---|---|
| **Recorded tour inquiry** | A named person asked, on this site, to be contacted about a tour, and the wording they consented to is stored with it | **Yes.** Server-generated UUID + server timestamp + stored consent text |
| **Referred to Admissions** | You passed their details on by phone | **Only by your own note.** `referredToAdmissionsAt` starts `null` and the endpoint never sets it |
| **Verified walk-in** | That person physically entered Westminster Place | **No.** The site has no way to observe this |
| **Completed tour** | They were shown the community by staff | **No.** Westminster's own records only |
| **Move-in** | They became a resident | **No.** Westminster's own records only |

What this system produces is **one** of those rungs: a timestamped record that
a named person asked to be contacted, created before any referral. That is
genuinely useful — it is the half nobody else can produce after the fact — but
it is not a walk-in, not a tour, and not a move-in.

**Never report an inquiry count as a tour count.** If 10 people submit and 3
actually tour, the honest sentence is "10 recorded inquiries; tours not
independently verified." Anything stronger will be checked and will fail.

---

## Operational now (verified on the live site, 2026-10-09)

| Capability | Evidence |
|---|---|
| Form accepts a submission | `POST /api/plan-visit` → `200`, `{"ok":true}` |
| Server-generated submission ID | `40a2fea4-b0b8-41e6-b637-f67694070382` — `crypto.randomUUID()`, never from the browser |
| Server-generated timestamp | `2026-10-09T16:28:46.835Z` — server clock; the function ignores any client-supplied time |
| Consent wording stored verbatim | `consentStatement` holds the exact sentence shown; `test.js` asserts it matches the form copy word for word |
| Record is stored | Netlify Blobs, site-scoped store `visit-attribution`; survives deploys |
| Storage is confirmed before success | Function writes, then **re-reads** the record and compares the ID. `verified:true` only after the round trip |
| Failure never reports success | If the write fails the endpoint returns `503` and says nothing was stored |
| Health and quiz data refused | `422` + `refusedFields` when any assessment field is present. Nothing stored |
| Unexpected fields refused | `422`. Only the five permitted fields are accepted |
| Consent enforced server-side | `400` when `consent` is not `true` |
| Contact method enforced | `400` when neither phone nor email is supplied |
| Export locked | `503` with no token, `503` with a wrong token, for JSON, CSV and DELETE |
| No public data path | `/t/`, `/api/`, `/visits`, `/visits.json`, `/.netlify/blobs`, `/.netlify/functions/plan-visit-export` all `404` |
| No secret in the browser | Asserted against `app.js` and `index.html` by the test suite |
| Site never claims to schedule | Confirmation reads "This does not schedule an appointment with Westminster Place" — asserted in the browser at 375/390/430 |

---

## NOT operational

### 1. Email notification — not configured
Live response field reads `"notification":"not_configured"`. The endpoint does
not pretend otherwise and never has. **No email has ever been sent by this
system.** Records are still stored when email is off, so nothing is lost — but
you will not be told a submission happened.

### 2. Retrieval — unproven end to end
This is the gap that matters most. Storage is proven. **Getting the data back
out is not**, because the export requires a token that is not set, so the
endpoint correctly refuses every request including mine.

Right now the system is **write-only from your side.** A record exists; you
cannot read it. That is safe, and it is not finished.

### 3. Data retention — written and deployed; the route out needs one address
Resolved since this was audited. The 180-day purge runs on every submission
and daily on a schedule, writes a receipt proving it ran, and that receipt is
returned by the export so the policy can be checked rather than trusted. The
deletion *mechanism* exists (`DELETE /api/plan-visit-export?id=…`).

What is still missing is the published address a visitor writes to, which is
the `{{CONTACT_EMAIL}}` token in `staged/privacy.html`. That is a decision
from you, not code from me — and the build fails if the notice ships without
it.

---

## What you need to configure (two values, one dashboard visit)

Netlify → project `evanston-senior-care-guide` → **Project configuration →
Environment variables**. Neither value ever reaches the browser.

**`PLAN_VISIT_FORM_KEY`** — turns email on.
Get a free access key at https://web3forms.com by entering the address you want
notifications sent to. The key carries the destination, which is why no address
of yours appears anywhere in this repository.

**`PLAN_VISIT_EXPORT_TOKEN`** — lets you read records back.
Generate one:
```
node -e "console.log(require('crypto').randomBytes(24).toString('hex'))"
```

Redeploy after setting them (environment variables are read at function
invocation, but a redeploy guarantees it):
```
npx netlify deploy --prod --dir=_dist --functions=netlify/functions \
  --site=e25a95a5-7a87-4d1c-bae7-8c35d496dded
```

---

## How to verify the system yourself, end to end

**Step 1 — submit a clearly labelled test.**
Open the site, run the six questions, and fill the form with:

- First name: `TEST-DELETE-ME`
- Last name: `<today's date>`
- Phone: a number you control
- Email: an address you control

Tick the permission box and submit. The page shows **Your interest has been
recorded.** and a reference ID. Write that ID down.

**Step 2 — confirm the email arrives.** Only works once `PLAN_VISIT_FORM_KEY`
is set. Subject will read:
`New Westminster Tour Inquiry — Evanston Senior Care Guide`

The body carries only the submission ID and timestamp — by design. If it
contains a name or a phone number, something is wrong; stop and check.

**Step 3 — confirm the record is retrievable.**
```
curl -H "Authorization: Bearer <your-export-token>" \
  https://evanston-senior-care-guide.netlify.app/api/plan-visit-export
```
Your test record appears with the same submission ID and timestamp the page
showed you. **That match is the whole proof.** The page and the server agree,
and neither number came from the browser.

**Step 4 — confirm it is locked to you.** Run the same command without the
header. It must return `401` or `503`. If it ever returns data, stop.

**Step 5 — delete the test.**
```
curl -X DELETE -H "Authorization: Bearer <your-export-token>" \
  "https://evanston-senior-care-guide.netlify.app/api/plan-visit-export?id=<submission-id>"
```
Returns `{"ok":true,"deleted":1}`. Re-run step 3 to confirm it is gone.

**Existing test records to delete once the token is set.** These were created
by me and by the automated browser suite. They are not real people:

- `TEST-DELETE-ME Audit 2026-10-09` — `40a2fea4-b0b8-41e6-b637-f67694070382`
- `Jane Smith` — `015cd5f5-a212-46ec-a276-579d33021211`
- `Margaret Holloway` — `56670960-6a74-4995-9953-ade7f830e2c4`
- `Dan Reyes` — `3b358c5c-77e1-4a38-bf78-6956b07ce0af`
- `Harness Probe` — `55d9de07-9b69-45ce-9b96-88e69ce81bba`
- plus several `Browser Harness <width>` and `Screenshot Harness` rows from
  test runs — list them all with step 3 and delete each by ID.

---

## What requires Westminster's authorization

You cannot close the loop from intention to move-in on your own, and you should
not try to.

**Needs authorization:**
1. **Any confirmation that a named person visited.** Prospect identity is
   Westminster's information, not yours. Asking a colleague to check a name
   against the visitor log without authorization is exactly the thing that
   turns a good initiative into a personnel problem.
2. **Any confirmation that a person toured or moved in.** Same reasoning, higher
   stakes — a move-in means they are a resident, and resident information is
   protected.
3. **Permission to promote Westminster as an employee.** Still outstanding. The
   FTC guidance you cited says employees should confirm their employer permits
   this kind of promotion. This has not been done.

**The clean way to ask.** Do not request access to any system. Request a
**reconciliation**: you hand over a list of names and submission dates, and an
authorized person tells you how many of those names appear in Westminster's
own intake over the same period. You receive a **count**, not records. You
never see anyone's information, and Westminster never gives you any.

That framing is the difference between "he built a lead source" and "he was
querying prospect data." Use it.

---

## Must be done before accepting real submissions

1. **Set both environment variables.** Until the export token exists, a real
   person's data goes into a store you cannot read — which also means you
   cannot honour a deletion request.
2. **Run the five-step verification above and delete every test record.**
3. **Publish a retention and deletion statement.** Decide: how long records are
   kept, and how someone asks to be removed. A deletion route needs a contact
   address — which means publishing one, or deciding the form is not collected
   until you have one.
4. **Check Westminster's employee and marketing policy.** Outstanding since the
   Westminster card shipped. This is now larger, because the site holds
   prospect contact details rather than merely linking to a website.

Until 1–4 are done, the honest status is: **the system records correctly and
cannot yet return what it records.**
