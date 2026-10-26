# staged/ — built, reviewed, NOT deployed

Nothing here is live. It is not in `_dist`, not in any deploy, and `test.js`
fails the build if any of it reaches the deploy directory or if an unresolved
`{{TOKEN}}` appears in shipped copy.

**Updated 2026-10-16.** Two of the three files here have moved on:

- `retention.mjs` / `retention-daily.mjs` — **now deployed** in
  `netlify/functions/`. The copies here are byte-identical; they are no longer
  the live ones.
- `consent-changes.md` — **superseded.** The optional second consent was
  retired when sharing became the form's purpose. Kept as a record.
- `privacy.html` — **still staged**, still the real thing, still one token
  short.

Still blocking deployment:

1. **Westminster authorization** — permission to promote as an employee, and
   Admissions' agreement to receive referrals.
2. **The deletion contact address** — you supply it; nothing is invented here.
3. **The two Netlify environment variables** — a deletion request cannot be
   honoured while the export token is unset.

---

## A correction to what I wrote before

My earlier note said reconciliation meant "no record transfers." **That was
wrong, and you were right to call it.**

Handing Westminster a list of names and submission dates **is** a transfer of
personal information. It is a small one, limited to consenting people and three
fields, but calling it zero transfer is the same weasel as "not *automatically*
shared." The staged copy now says what actually happens:

> A limited list — first name, last name and submission date, for those who
> ticked the optional box and no one else — is provided to authorised
> Westminster Place staff, who compare it against their own records.

That is a disclosure, not a reassurance, and it belongs in that register.

---

## What counts as proof, and what does not

Your stated goal: **written, independently verifiable confirmation** that named
prospects, tours or move-ins originated through this guide. Four things get
confused here, and they are not interchangeable.

| | What you would hold | Strength |
|---|---|---|
| Recorded visit intention | Your own timestamped record, server-generated | **Proves only** that a named person said they planned to visit, before visiting |
| Aggregate count | "7 of your 20 names appear in our records" | A signal. **Not** proof any particular person visited, and not attribution |
| Named written confirmation | A signed or emailed statement from an authorised person naming individuals and what happened | **This is the goal.** Independently verifiable |
| Causal attribution | "This person moved in *because of* your website" | Nobody can produce this. A person who used your guide and moved in may have moved in anyway |

**An aggregate count is not proof a particular person moved in because of the
site, and must never be presented as one.** The honest strongest claim an
aggregate supports is: *"Of 20 people who recorded an intention through the
guide, 7 appear in Westminster's records over the same period."* That is a
real, checkable sentence. It is also not a causal claim, and stretching it into
one is how the whole thing gets dismissed.

Pursue the named written confirmation. Treat the count as the interim measure
while authorization is pending.

---

## The copies you cannot delete from your own system

This is the part that automatic deletion does not solve, and it needs your
decision too.

The 180-day purge removes the record from the Netlify store. It does **not**
remove:

| Where | What it holds | Who controls deletion |
|---|---|---|
| Your email inbox | Notifications carrying **only** a submission ID and timestamp — no name, email or phone. Option 1 below was taken | You. Manually |
| Web3Forms | Their own copy of every submission they relayed, in their dashboard and backups | Them, under their retention terms |
| Netlify function logs | The submission ID and the stored/failed status. No names — the function logs state, never fields | Netlify's log retention |

So "we delete after 180 days" is **false** unless the inbox and Web3Forms are
handled too. Two ways to make it true:

**Option 1 — minimise what leaves the building (recommended).**
Change the notification email to carry **first name, last name, planned visit
date and submission ID only**. No email address, no phone number. When you
actually need to contact someone, pull it from the export, which is the copy
that expires on schedule.

Standing personal information in two third parties drops to a name and a date.
It also means a leaked mailbox exposes far less. The cost is one extra lookup
on the rare occasion you need the contact details, which for a system whose
purpose is attribution rather than outreach is close to no cost at all.

**Option 2 — keep the full email and commit to clearing it.**
A standing 180-day sweep of the notification folder, plus a deletion request to
Web3Forms. This depends on you remembering, every time, forever. It is the
weaker option and it is the one that quietly fails.

The privacy notice states whichever you choose. It cannot promise deletion that
does not happen.

---

## Files

| File | What it is |
|---|---|
| `privacy.html` | The privacy notice. **Live-bound.** One `{{CONTACT_EMAIL}}` token remains |
| `consent-changes.md` | **Superseded 2026-10-16.** The retired two-consent design, kept as a record |
| `retention.mjs` | **Already deployed** to `netlify/functions/`. This copy is a byte-identical leftover, not the live one |

## Merging, when the three blockers clear

Only `privacy.html` is left to merge, and it is one step: resolve
`{{CONTACT_EMAIL}}`, copy it to `_dist/privacy.html`, run `node test.js`,
deploy. The retention modules are already live and the consent work is done
in `app.js` and `plan-visit.mjs`.
