# Status — live, approved, collecting

**Development phase closed 2026-10-18.** Final production deploy
`6ad50fa299f049a6db257f95`. Next phase is traffic, not code.

Rewritten 2026-10-17 after the external review. This file previously
described a site waiting to launch. **It launched.** Everything below is
the deployed state, verified against production rather than source.

## Live now

- **https://evanstonseniorcareguide.com** and
  **https://evanston-senior-care-guide.netlify.app** serve the same site.
  The custom domain was connected outside this work.
- **Collection is ON.** `COLLECTING = true` in `app.js`,
  `PLAN_VISIT_COLLECTION_ENABLED = true` in Netlify. Both must move to turn
  it off again.
- **Privacy notice published** at `/privacy.html`, dated 17 October 2026.
- **Four environment variables set in the Netlify UI** and confirmed reaching
  the functions: `RESEND_API_KEY`, `PLAN_VISIT_NOTIFY_TO`,
  `PLAN_VISIT_NOTIFY_FROM`, `PLAN_VISIT_EXPORT_TOKEN`.
  Variables written by `netlify env:set` do **not** reach function runtime —
  use the dashboard.
- **Export token rotated** 2026-10-17. The previous token returns `401`.

## What happens on a submission

1. Family completes six questions and sees their care level.
2. The form takes first name, last name, phone, email, and one required
   consent. The care level is captured automatically from the rendered
   result — never re-selected by the visitor.
3. The server validates the level against a fixed list of six, writes the
   record, then **re-reads it** before reporting success.
4. Resend emails the operator: name, phone, email, care level, routed
   Admissions team and number, timestamp in Chicago and UTC, submission ID.
5. The operator phones Admissions. **Nothing is sent to Westminster
   automatically**, and `referredToAdmissionsAt` starts `null` and is only
   ever set by hand.

## Still open

Nothing. The store was cleared to **0 records** on 2026-10-18, after the
owner's final test record was deleted. **The next record will be a real
family.**

## Employment-policy question — UNVERIFIED, not a blocker

Logged here once so it is on the record, and not raised again.

**No specific Westminster policy requiring prior approval for an
employee-operated independent website has been identified.** None was ever
cited. What was cited — the FTC Endorsement Guides — governs *disclosure* of
a material connection, and this site satisfies that: the employment
relationship is stated on every result page that names Westminster, the site
states it is not official, and it states no referral fees are received.

Treat this as an unverified question a careful operator would eventually
answer for his own protection, in his own time. **It is not an established
rule and it does not gate launch.** If a specific written policy or legal
requirement is ever identified, it goes here with the citation — until then,
this section stays closed.

## Standing obligations

- `norvenph@gmail.com` must stay monitored. The published notice promises a
  deletion or disclosure answer within 30 days.
- **Notification emails carry personal data and the 180-day purge cannot
  reach them.** Clear them from the mailbox after each referral call. This
  is deliberate and disclosed in the notice — see below.
- Resend domain verification is **not** required while the sandbox sender
  delivers to your own Resend account address. It is only needed to notify a
  different address: one env var, no code.

## Verified by test, not by memory

`node test.js` → **528/528**. `node staged/retention.test.mjs` → **19/19**.
Plus 27 live production checks on 2026-10-18, all passing.

Gates that would catch a regression of the external review's findings:
deletion requires a complete anchored UUID and an exact key match and refuses
any multi-match; the employment disclosure renders on all six results
including "no higher level of care yet"; no copy anywhere promises Admissions
will make contact; a stated need for around-the-clock nursing is never
overridden by hospital recency.

## The data decision, stated plainly

Sending the family's name, phone, email and care level through Resend is
**intentional**, instructed 2026-10-17, and was made because an alert you
must go and look something up from gets ignored. The trade is that this
personal data sits in a mailbox and at Resend, outside the 180-day purge.

The published privacy notice says exactly that — it names Resend, lists the
care level among collected fields, and states the email limit in its own
section. The consent checkbox names all four shared items and is versioned
`2026-10-19`. **Nothing about what is shared changes without that notice
changing in the same commit.**

## What this system proves, and what it never will

| Rung | Can this prove it |
|---|---|
| A family asked, on this site, at this time | **Yes.** Server UUID + server timestamp + stored consent wording |
| You referred them to Admissions | Only by your own note — `referredToAdmissionsAt` is set by hand |
| They completed a tour | **No.** Westminster's records only |
| They moved in | **No.** Westminster's records only |

A submitted form is never a completed tour. The defensible sentence is
*"N families asked through the guide; tours and move-ins confirmed separately
by Westminster."*

## Care-continuity wording — owner-approved, 2026-10-19

The site says, verbatim:

> Westminster Place offers several levels of senior care on one campus.
> During a visit, you can ask how the community supports residents when their
> needs change and whether transitioning between care settings may be
> possible.

Earlier wording implied a resident could move between levels. Offering
several levels does not guarantee that. `test.js` asserts this sentence and
bans the old phrasing.
