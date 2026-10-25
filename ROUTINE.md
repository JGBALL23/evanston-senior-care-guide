# Daily draft run — operating instructions

The cloud routine `EVANSTON-DAILY-GUIDE-DRAFTS` reads this file and follows it.
It lives here rather than inside the trigger so that the rules are versioned,
reviewable in a diff, and changeable without touching the scheduler.

You write research drafts for review. **You never publish. The owner publishes.**

## Hard limits

Breaking any one of these is a failed run, even if the writing is good.

- Never deploy. Never call Netlify. Never run a deploy script. Never set or
  read a Netlify token.
- **Never announce anything to a search engine.** Do not run
  `tools/publish.py`, do not call IndexNow, and never submit a URL to any
  ping or indexing endpoint. A draft has no live URL, so announcing one
  would point a crawler at a 404. Announcing is part of publishing, and
  publishing is the owner's step, not yours.
- **Never touch `main`.** Do not check it out, merge into it, or push to it.
  `main` is what the owner deploys from; this routine's entire output is
  commits on `drafts` awaiting review.
- Never read, move or touch lead records or form submissions.
- Never edit a test or a gate to make your own work pass. A failing suite
  means the content is wrong, not the gate. If you believe a gate is genuinely
  wrong, say so in the report and leave it alone.
- **Never destroy earlier work.** See *Never clobber* below.
- **At most two guides.** One excellent guide beats two thin ones. Shipping
  **zero** and explaining why is a valid, good outcome — a day with no
  well-sourced topic is a real day.

## Step 0 — the clock gate. Do this before anything else.

```sh
TZ=America/Chicago date '+%Y-%m-%d %H:%M %Z'
date -u '+%Y-%m-%dT%H:%M:%SZ'
```

**If the Chicago hour is not `06`, stop immediately.** Print:

    CLOCK GATE: skipping. Chicago local time is <time>, not 06:xx.

and end the run. Do not fetch, do not research, do not write, do not commit,
**and send no notification** — see Step 7.

This is not a nicety. The schedule is a fixed UTC cron and the trigger API
stores no timezone, so the only way to hold 6 AM Chicago across daylight
saving is to fire the cron at **both** candidate UTC hours and let this gate
discard the wrong one. 06:00 Chicago is 11:00 UTC under CDT and 12:00 UTC
under CST, so the cron is `2 11,12 * * *` and exactly one of the two firings
survives this gate every day of the year — including 1 November 2026 and
8 March 2027, when the surviving hour swaps without anyone editing anything.

The skipped firing costs one short sandbox start and no work. That is the
price of a correct wall-clock time on a UTC-only scheduler, and it is worth
paying: the alternative is an owner editing a cron twice a year forever.

## Step 1 — get on the latest `drafts`

The repository is cloned fresh for every run and lands on the **default
branch**, which is `main`. `main` is deliberately behind — it is the published
site. Everything this routine needs, including the file you are reading, lives
on `drafts`. So fetch and switch before reading anything else:

```sh
git fetch origin --prune
git checkout -B drafts origin/drafts
git log --oneline -1
```

`checkout -B` points the local branch at `origin/drafts` whatever state it was
in, so a stale local branch from a cached workspace can never shadow the real
one.

**Confirm you are actually on the latest before continuing:**

```sh
test "$(git rev-parse HEAD)" = "$(git rev-parse origin/drafts)" \
  && echo "ON LATEST origin/drafts" || echo "NOT ON LATEST - STOP"
ls _dist/guides/
grep -c '"slug"' build-guides.py
```

If you are not on `origin/drafts`, stop and report it. If `ROUTINE.md` is
absent, stop and report that — do not improvise a run.

## Step 2 — pick a gap

Run `grep -n '"slug"' build-guides.py` and read each existing `h1`.

Choose a genuinely new topic that a family in Evanston would type into a
search box when a parent needs more help. No duplicates, no near-duplicates,
no keyword variants of a guide that already exists.

## Step 3 — rules of evidence

This is the whole job. The library's value is that every number on it was
read off a government page, not absorbed from a search result.

- Every factual claim must come from a page you **fetched and read** with
  WebFetch. A WebSearch snippet is **not** a source — use search only to find
  a URL, then fetch that URL and read it.
- Allowed citation hosts, enforced by a gate in `check-guides.js`:
  `medicare.gov`, `cms.gov`, any `*.illinois.gov` (HFS, Department on Aging,
  IDPH, the Health Care Report Card), any `*.va.gov`, and `assets.carescout.com`.
  Nothing else may appear in a Sources block.
- **`va.gov` is open as of 2026-10-25**, so VA Aid & Attendance, Veterans
  Pension, Survivors Pension and related veterans' senior-care benefits are
  researchable topics. Many Evanston families have a veteran parent and no
  idea the benefit exists. Cite the va.gov pages you actually read; rate
  tables carry an effective date range, so quote the date with the figure
  and never carry a rate past its stated period.
- **If a figure cannot be read off a primary page, do not publish it.** Say
  the figure is set by the state and tell the reader who to ask. Omitting an
  unverifiable number is a pass, not a gap. Saying "this guide could not
  verify that" is better writing than a confident wrong number.
- A published figure that is a **maximum or a standard is not an entitlement**.
  If the source says an actual amount is derived by deducting something, quote
  that rule and refuse to do the arithmetic yourself.
- Never cite a page you did not open. Guessed URLs 404.
- No claims about Westminster Place. No invented local figures. No marketing
  language. Plain British-English prose, matching the existing guides.

## The conversion goal

The six-question assessment is **the** conversion goal of this site. Every
guide has two jobs: answer the question honestly, and leave the reader better
placed to take the assessment.

There are exactly **two** routes to it inside an article: the `bridge` after
the first section, and the CTA at the end. A gate enforces that count. Do not
add a third, do not make the bridge a button, and never add a pop-up, a
sticky bar or a modal — gates fail on all of those.

- `build_guide` already appends the assessment block to every page, and
  `check-guides.js` now fails if it is missing from any guide. Do not remove,
  reword or relocate it.
- Where the guide's subject naturally raises "which level of care does my
  parent actually need?", link to `/` in the body too — the existing guides do
  this in their closing section. Once is right. Do not stuff it.
- The assessment's promise is fixed: no name, no email and no phone number to
  see results, and answers never leave the device. Never soften, never
  contradict, never add a condition to it.
- Never invent a different call to action. No newsletter, no "contact us", no
  phone capture, no gated download.

## Step 4 — write it

Add a dict at the end of `GUIDES` in `build-guides.py`, matching the existing
shape: `slug`, `title`, `h1`, `desc`, `intent`, `answer`, `sources`, `body`.

- Add `"reviewed": "<today's date, YYYY-MM-DD>"`. This is a factual claim
  about the day you read the sources. Never reuse another guide's date and
  never touch the global `REVIEWED` default.
- **Add a `"bridge"`.** This is required — the build refuses to produce a
  guide without one and prints instructions if you forget. It is ONE sentence
  naming the question *this* article cannot answer, shown after the first
  section, where a reader who has their answer is most likely to leave. The
  generator appends the link, the timing, the privacy promise and the
  not-a-diagnosis line itself; you write only the sentence.
  - Write it fresh for the topic. Never reuse or lightly reword another
    guide's bridge — a gate fails if two are identical.
  - Name the gap, then step back. No urgency, no scarcity, no "act now", no
    promise about what the result will say.
  - Good: *"Knowing what Medicare covers is a different question from knowing
    what kind of care your parent actually needs."*
  - Bad: *"Don't wait — find out what your parent needs today!"*
- Add the `CARDS` entry. Its first element is the **category**, and it must
  be one of the values in `CATEGORIES` in `build-guides.py` — the build
  refuses an unknown one and prints the valid list. The /guides/ filter chips
  and the search index are generated from it, so a new guide becomes
  browsable and findable with nobody editing the library page.
  - Pick the closest existing category. Do not invent a near-duplicate of one
    that already exists ("Costs" vs "Cost" vs "Paying").
  - If a guide genuinely belongs to none of them, add ONE category to
    `CATEGORIES` and say so in the commit message.
- Register any new source in `SRC`.

## Never clobber

Every earlier commit on `drafts` is either approved work or work awaiting the
owner's review. Both are irreplaceable; neither is yours to discard.

- **Append only.** Add a new guide dict. Do not rewrite, reword, retitle,
  re-date or delete an existing guide, and do not "tidy" `build-guides.py`.
- **Never** `git push --force`, `--force-with-lease`, `git rebase`,
  `git commit --amend`, `git reset --hard` onto a published commit, or
  `git checkout -- <file>` over someone else's change.
- Never delete a file you did not create in this run.
- If `git push` is **rejected** because `drafts` moved while you worked:
  run `git pull --rebase=false --ff-only origin drafts`, and if that fails,
  `git pull --no-rebase origin drafts` to make a merge commit. Resolve by
  **keeping both sides**. If you cannot merge cleanly, stop, push nothing, and
  report it. Never resolve a conflict by discarding the other side.
- Before committing, run `git status --porcelain` and read it. Anything with
  `D` (deleted) or an unexpected `M` on a file you did not intend to touch is
  a mistake — restore it before committing.

## Report failures. Never route around them.

A failed check is information the owner needs, not an obstacle to clear.

- If research fails — a source will not load, a page does not say what you
  needed, a figure cannot be verified — **cut the claim, or cut the guide.**
  Report what failed and why.
- If a citation will not resolve, the guide does not ship with it. Find a
  live primary source or drop the section.
- If a suite fails and you cannot fix the *content* to pass honestly, **push
  nothing** and report the failure verbatim.
- A run that ships nothing and explains exactly what stopped it is a good
  run. A run that ships something questionable is a bad one, every time.

Never weaken a claim just enough to slip past a gate. If the evidence is not
there, say the evidence is not there.

## Step 5 — run every check

Quote the final line of each, verbatim, in your report:

```sh
python build-guides.py
node test.js
node check-guides.js
sh check-citations.sh
python check-mobile-nav.py     # may SKIP — report the printed reason
```

A skip is not a failure. A failure is a failure: fix the content and re-run.
The suites derive their slug list from `build-guides.py`, so they grow on
their own — you never need to update a count anywhere.

## Step 6 — commit and push

```sh
git -c user.name=evanston-cloud -c user.email=cloud@evanston.local commit -m "..."
git push origin drafts        # never --force, never any other branch
```

Then prove you left the rest alone:

```sh
git rev-parse --short main origin/main    # must be unchanged and equal
git log --oneline origin/drafts -3
```

## Step 7 — notify the owner

Send **exactly one** push with the `PushNotification` tool, at the very end,
after the push to `drafts` has succeeded or definitively failed.

**Keep the message under 200 characters.** Mobile operating systems truncate
longer text, and a truncated notification that loses the link is useless. If
the guide titles will not fit, shorten the titles — never the link, never the
pass/fail word.

The link is always:

    https://github.com/JGBALL23/evanston-senior-care-guide/compare/main...drafts

That link is **76 characters**, so you have about **123 characters** for
everything else. Two full guide titles will not fit — shorten them to the
distinguishing words ("Illinois Medicaid long-term care", not "How Illinois
Medicaid pays for long-term care, and what spend-down means"). Count the
characters before sending. A notification that fits is worth more than one
that is complete and cut off mid-URL.

### When a run created guides

Say how many, name them, state whether everything passed, give the link.

    Evanston: 2 new drafts — Illinois Medicaid long-term care; Reporting a
    care facility. All checks + citations passed. <link>

If any check or citation failed, you did not push the guide — so that case is
a failure notification, not this one. Never write "all checks passed" unless
every suite returned zero failures and every citation resolved. A SKIPPED
browser suite is not a failure; say "checks passed (browser suite skipped)".

### When a run created nothing

Still notify, and say why in plain words — not a stack trace.

    Evanston: 0 drafts today. HFS page for the figure would not load, so the
    claim could not be verified. Nothing pushed. <link>

Zero guides is a legitimate outcome. The notification exists so the owner
knows the routine ran and chose not to ship, rather than wondering whether it
is broken.

### When the run itself failed

Same rule. Name the step that broke and what it said.

    Evanston: run FAILED at the citation check — 2 dead URLs. Nothing pushed,
    main untouched. <link>

### NEVER notify for the clock-gate skip

If Step 0 ended the run because the Chicago hour was not `06`, **send no
notification at all.** That firing is scheduling plumbing — the cron fires at
two UTC hours so one of them lands at 6 AM, and the owner must never be
pinged about the one that gets discarded. A silent skip is the correct and
complete behaviour.

### Report what delivery actually did

`PushNotification` returns delivery details, including whether a push was
really sent or why it was skipped. Quote that result verbatim in the final
report. "Mobile push requested" is a request, not a delivery — never describe
it as a notification the owner received.

## Final report — under 250 words

- The clock-gate result (Chicago local time, and that it was 06:xx).
- Confirmation you were on `origin/drafts`, and the guide count you found.
- The topic, and why it is a real gap.
- Every URL you actually fetched and read.
- **At least one claim you refused to publish, and why.** If you refused
  nothing, say that explicitly — it is unusual and worth the owner knowing.
- The five suite result lines, verbatim.
- The pushed commit hash, and the `main` hash proving it did not move.
- The notification you sent, quoted, and the delivery result the
  `PushNotification` tool returned — or, for a clock-gate skip, nothing at
  all, because that run ends at Step 0.

Never claim you read a page unless a tool returned its text to you.
