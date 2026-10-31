# One end-to-end test of the inquiry system — plan only

Written 2026-10-31. **Not executed.** It runs once, by the owner's separate
approval, and never again without another.

## Why one test

The live form has never been submitted since Simple First shipped. Every
part of it is byte-identical to the build that was tested before launch —
the form markup, the function, the consent sentence — but identical code is
not a received email. One labelled submission proves the whole chain in
production: browser → `/api/plan-visit` → durable record → notification →
beacon → export.

## The submission

| Field | Value | Why |
| --- | --- | --- |
| First name | `TEST` | Unmistakable in the inbox and the export |
| Last name | `DO-NOT-CONTACT` | Nobody at Admissions should act on it, and the owner never passes it on |
| Phone | blank | One contact method is enough; fewer personal details stored |
| Email | the owner's own address (the one in `PLAN_VISIT_NOTIFY_TO`) | The only address that may receive anything |
| Interest | whatever the result pre-fills | Tests the pre-fill path |
| Consent | ticked | Required; the test proves the consent record, not the hand-off |
| Path | the full assessment, parent audience, the assisted-living answers used by the harnesses | Tests `careLevel` and `assessmentTaken: true` |

Done from a normal phone browser on the live site, not from a harness, so
the beacons count it as one verified visitor — and the baseline row for that
day notes it.

## What must be true afterwards

1. The page shows "Your interest has been recorded." with a reference ID.
2. The notification email arrives at `PLAN_VISIT_NOTIFY_TO`, from the
   configured sender, naming the care level, the interest, the Admissions
   team and number for that level, the consent version, and the reference.
3. The log shows, for that visit only: `plan-visit-form-view`,
   `plan-visit-submitted`, `plan-visit-saved`, `inquiry-submitted`, each
   once, from a `browser`-class agent.
4. `GET /api/plan-visit-export` (bearer token, owner only) lists the record
   with `stage = recorded_tour_inquiry` and `referredToAdmissionsAt` empty.
5. The record is never referred: the owner does not pass `TEST DO-NOT-CONTACT`
   to anyone.

## Cleaning up

`DELETE /api/plan-visit-export?id=<reference>` with the bearer token removes
the record. If the owner has no tool at hand to send an authenticated
request, the record purges itself after 180 days like any other; the name
makes it harmless in the meantime. The notification email is deleted by the
owner.

## What this test does not prove

That a family would do the same, that Admissions received anything, or that
a tour happened. It proves the machine works.
