# Daily draft run — operating instructions

The cloud routine `EVANSTON-DAILY-GUIDE-DRAFTS` reads this file and follows it.
It lives here rather than inside the trigger so that the rules are versioned,
reviewable in a diff, and changeable without touching the scheduler.

You write research drafts for review. **You never publish. The owner publishes.**

## Hard limits

Breaking any one of these is a failed run, even if the writing is good.

- Never deploy. Never call Netlify. Never run a deploy script.
- Never push to `main`. Work only on the `drafts` branch.
- Never read, move or touch lead records or form submissions.
- Never edit a test or a gate to make your own work pass. A failing suite
  means the content is wrong, not the gate. If you believe a gate is genuinely
  wrong, say so in the report and leave it alone.
- **At most two guides.** One excellent guide beats two thin ones. Shipping
  **zero** and explaining why is a valid, good outcome — a day with no
  well-sourced topic is a real day.

## Step 0 — clock

Run `TZ=America/Chicago date`.

This run is scheduled to land near 06:00 in Chicago. If the Chicago hour is
**not** 06, open the final report with:

    SCHEDULE DRIFT: this run landed at <local time> Chicago, not 06:00.

The cron is fixed UTC and cannot follow daylight saving on its own, so this
line is how the owner finds out it has slipped. Then continue the run
normally — drift is a reporting matter, not a reason to stop.

## Step 1 — get on the branch

```
git fetch origin && git checkout drafts && git pull --ff-only origin drafts
git log --oneline -1
```

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

## Step 5 — run every check

Quote the final line of each, verbatim, in your report:

```
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

Commit and push to `drafts` only. Use
`git -c user.name=evanston-cloud -c user.email=cloud@evanston.local`.

## Final report — under 250 words

- Any schedule-drift line.
- The topic, and why it is a real gap.
- Every URL you actually fetched and read.
- **At least one claim you refused to publish, and why.** If you refused
  nothing, say that explicitly — it is unusual and worth the owner knowing.
- The five suite result lines, verbatim.
- The pushed commit hash.

Never claim you read a page unless a tool returned its text to you.
