# G14 — Facebook-first playbook (owner review only)

**Status: DRAFT ONLY. Nothing has been published, posted, submitted or sent.** Publishing needs the owner's direct, specific approval and the venue's permission. This file is not part of the live site: the site deploys from `_dist/` only.

Checked on 16 Nov 2026, 22:25 UTC: the live homepage returns 200 and still says "6 quick questions", "About two minutes" and "No email needed". It also says the result is "an educational starting point, not a medical diagnosis".

## 1. Offer comparison

| | North Shore post (live since 16 Nov 04:42 UTC) | G14 pilot |
|---|---|---|
| Offer | Printable tour-questions checklist (PDF) | Free six-question care assessment |
| Who it helps | Families who already plan to tour | Families who aren't yet sure what level of help a parent needs, an earlier and larger group |
| What the visitor does | Download, then possibly leave | Answer six questions on the page, see a result, and only then see the optional tour inquiry |
| Measured by existing beacons | `checklist click` | `assessment-started` and `assessment-completed`, both tagged with `?s=<channel>` |
| First ten hours (Claude-reported, historical) | 1 genuine visitor, 1 checklist click, 0 assessment starts | Not posted |

**Why test it:** the checklist asks families to have decided to tour already. The assessment meets them one step earlier, and it is the site's main path. **Run it as a separate post at a later date, in a different venue or on the owner's own profile. Never repost in North Shore** while its window is open (until 23 Nov 04:42 UTC).

## 2. Draft post (about 110 words)

> **"Mom says she's fine." If you're not so sure, here's a calm way to think it through.**
>
> Many of us in Evanston and the North Shore are trying to work out whether a parent needs a little help at home, assisted living, memory care or more. The options and the vocabulary are confusing.
>
> I built a free, independent guide with a six-question check. It takes about two minutes, asks about everyday things like personal care, memory, medical needs, safety and cooking or bills, and suggests which level of care to look into first. Your answers stay in your browser. There's no sign-up and no email.
>
> It's a starting point, not a diagnosis: https://evanstonseniorcareguide.com/#assessment
>
> *[Disclosure: paste the affiliation sentence exactly as it appears on the site's About section.]*

**Alternate hook, for a later iteration only:** "Is it time for more help for Mom or Dad? Six everyday questions, about two minutes, no email, and you get a plain-English starting point."

Rules for the copy: use the plain URL with no added parameters. Don't name or compare communities. Don't promise eligibility, placement or savings. Don't use stock images of frail seniors; the site's own link preview (og-card) is enough.

## 3. Where permission is checked (before every post)

1. **Owner's own profile or Page.** The owner decides. Include the disclosure, and confirm the post's audience setting.
2. **A group.** Read the group's pinned rules and the About section for posting, link and promotion rules, *on the day you post*. Proceed only if the rules explicitly allow resource links or self-promotion, or an admin has granted permission. **Silence or the absence of a rule is not permission.** Don't join groups just to post. One post per group per window. If the group sends posts to moderation, wait and never resubmit.
3. **Disclosure** goes in the post body itself, not only on the site.
4. Record the venue name, date, rule checked and approval status in the owner's **private** tally, not on GitHub.

## 4. SOP: approve → post → moderate → observe → iterate

1. **Approve:** the owner approves the exact text and venue directly in chat. The text is frozen from then on.
2. **Post:** the owner posts it, or Claude posts it in the owner's session after a fresh "post it". Note the UTC time.
3. **Moderation:** check once at about 12 h and once at about 48 h. If the post is pending, record "pending" and do nothing else. If it is rejected, record that and don't resubmit. The 7-day clock starts when the post becomes **visible**.
4. **Observe for 7 days:** no daily nudging, no bumping, no comment-farming. Reply only to genuine questions, with facts and no pitch.
5. **Score and decide** using section 5, then change **one** variable at a time (hook, offer or venue).

## 5. Measurement (existing instruments only, nothing new)

Use Netlify's server-side path counts for `/t/` beacons, which the owner reads. Corrected by G15 after reading the source on main `6f32217`.

**How the channel tag is made** (`app.js` lines 61-77): `utm_source`, else `ref`, else the **first label** of the referrer's hostname after dropping `www.`, lowercased, at most 24 characters, else `direct`. It is recomputed on every page load and never stored.

| Referrer host | Tag | Facebook only? |
|---|---|---|
| `facebook.com`, `www.facebook.com` | `facebook` | Yes |
| `lm.facebook.com` | `lm` | Yes in practice; no other common host starts with `lm.` |
| `l.facebook.com` | `l` | **No.** `l.instagram.com`, `l.messenger.com` and `l.threads.net` give `l` too |
| `m.facebook.com` | `m` | **No.** `m.youtube.com` and other mobile sites give `m` too |
| `mbasic.`, `web.`, `touch.facebook.com` | `mbasic`, `web`, `touch` | Yes, but not in the PR #29 list |
| Referrer stripped (in-app browser, privacy setting) | `direct` | Unknown |

**Which events carry the tag:**

| Event (`/t/...`) | Tagged? | Source line |
|---|---|---|
| `landed.txt` | Yes | `app.js:116` |
| `assessment-started.txt` | Yes | `app.js:1109`, `1141` |
| `assessment-completed.txt` | Yes | `app.js:670` |
| `plan-visit-submitted.txt` (attempt) | Yes | `app.js:1038` |
| `plan-visit-saved.txt` (record saved) | Yes | `app.js:1049` |
| `inquiry-submitted.txt` | **No**, by design (exact-path filter) | `app.js:35`, `1057` |
| Stored inquiry record | **No channel field.** `source` is the fixed site name | `plan-visit.mjs:73`, `334` |
| Confirmed tour | **No instrument** | (none) |

**Supported reporting rule:**
- **Facebook (confirmed):** `s=facebook` + `s=lm` + `s=mbasic` + `s=web` + `s=touch`.
- **Facebook-possible (ambiguous):** `s=l` and `s=m`. Report them on a separate line and never add them to the Facebook count. Compare them with the 7 days before the post. Only a clear rise during the window counts as Facebook-likely, and with Instagram on hold, a rise in `s=l` is most plausibly Facebook.
- **Unattributed:** `s=direct`. It is never counted as Facebook.
- **Same-tab loss:** a visitor who opens a guide and then returns to the homepage gets a fresh tag of `direct`, because the referrer is now the site itself. So Facebook starts and completions are a **floor**.
- **Inquiries:** only `plan-visit-saved.txt?s=<Facebook tags>` links a saved record to Facebook, as an aggregate count. A specific record cannot be tied to a channel.
- **Tours:** they cannot be attributed to any channel with existing instruments. Report the total only.
- Beacons fire from JavaScript, so link-preview crawlers that don't run scripts fire none. The harness user agent is still excluded.
- **Owner option (not applied):** adding `?utm_source=facebook` to the post link uses existing, tested code (`tools/test_start_source.mjs:80`) and would make every click read `s=facebook`, ending the ambiguity. It changes the copy rule in section 2, so it is the owner's call.

| Metric | Source | Note |
|---|---|---|
| Reach, reactions, comments | Facebook post insights, if the owner shares them | Aggregates only |
| Facebook landings | `landed.txt`, confirmed tags, with `l`/`m` reported apart | A floor |
| Assessment starts and completions | `assessment-started` and `assessment-completed`, same split | A floor; directional only |
| Opt-in inquiries | `plan-visit-saved.txt`, same split | An aggregate count only; records carry no channel |
| Confirmed tours | Owner's private total | Not attributable to Facebook |

A missing figure is reported as **unverified, not zero**. Report small numbers as counts, not rates.

**First keep/change gate (at day 7):**
- **Keep the offer and try a second permitted venue:** at least 3 confirmed-tag Facebook landings **and** at least 1 confirmed-tag assessment completion, or any `plan-visit-saved` with a confirmed tag. Ambiguous `l`/`m` counts never decide the gate alone.
- **Change the hook (alternate) and keep the venue type:** the post had visible reach or reactions, but fewer than 3 Facebook landings.
- **Change the venue:** reach was negligible, or the post was held or rejected.
- **Change the offer:** at least 3 landings but 0 assessment starts. Look at the landing page before writing more copy.

With samples this small, none of these results proves cause. "Facebook established" still needs more than one authorized post and a clear keep/change decision (Issue #25).
