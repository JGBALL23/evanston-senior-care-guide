# Daily draft run — operating instructions

The cloud routine `EVANSTON-DAILY-GUIDE-DRAFTS` reads this file and follows it.
It lives here rather than inside the trigger so that the rules are versioned,
reviewable in a diff, and changeable without touching the scheduler.

You write research drafts for review. **You never publish. The owner publishes.**

## Hard limits

Breaking any one of these is a failed run, even if the writing is good.

- Never deploy. Never call Netlify. Never run a deploy script. Never set or
  read a Netlify token.
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

and end the run. Do not fetch, do not research, do not write, do not commit.

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
- Prefer `hfs.illinois.gov`, `medicare.gov`, `cms.gov`, `ilaging.illinois.gov`,
  `dph.illinois.gov`.
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

## Step 4 — write it

Add a dict at the end of `GUIDES` in `build-guides.py`, matching the existing
shape: `slug`, `title`, `h1`, `desc`, `intent`, `answer`, `sources`, `body`.

- Add `"reviewed": "<today's date, YYYY-MM-DD>"`. This is a factual claim
  about the day you read the sources. Never reuse another guide's date and
  never touch the global `REVIEWED` default.
- Add the `CARDS` entry.
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

## Final report — under 250 words

- The clock-gate result (Chicago local time, and that it was 06:xx).
- Confirmation you were on `origin/drafts`, and the guide count you found.
- The topic, and why it is a real gap.
- Every URL you actually fetched and read.
- **At least one claim you refused to publish, and why.** If you refused
  nothing, say that explicitly — it is unusual and worth the owner knowing.
- The five suite result lines, verbatim.
- The pushed commit hash, and the `main` hash proving it did not move.

Never claim you read a page unless a tool returned its text to you.
