# Funnel baseline — how visitors are counted, and the first clean reading

Started 2026-10-31. One file, appended to, never rewritten: a row is a
measurement, and a measurement that was wrong stays in the record with a
note, so a later reader can see what was believed and when.

## What counts as what

The site has no analytics service, no cookie and no identifier. Each step a
visitor reaches requests one tiny file under `/t/`, and the host's request
log is where those requests are counted. That log classes every request by
user-agent category: `browser`, `tooling`, `crawler`, `ai-agent`,
`page-preview`, `other`.

Three kinds of number, never mixed:

- **VERIFIED visitor** — a request for `/t/landed.txt` (it only fires when
  JavaScript ran, so a scanner never sends it) whose user agent is not a
  harness, not `tooling`, `crawler` or `ai-agent`. This is the closest
  thing to a person the site can count, and it is still not proof of one.
- **VERIFIED stage** — the same filter applied to any later beacon
  (`assessment-started`, `assessment-completed`, `result-*`,
  `plan-visit-form-view`, `inquiry-submitted`, `pay-nav-*`). A stage count
  can never exceed the `landed` count for the same window; if it does, the
  window is contaminated and the row says so.
- **ESTIMATE** — page requests by `browser`-class agents. Scanners probing
  `/wp-admin/install.php` and `.env` paths are classed `browser` too, so
  this number is an upper bound on page views, not a count of people.

What is never a business outcome: a beacon, a form view, a click to any
Westminster page. An inquiry is a stored record with consent. A tour is only
what Admissions confirms, by reference ID, and that is recorded elsewhere
(see the attribution proposal).

## Excluding our own test traffic

Every browser harness in this repository launches Chrome with one fixed
User-Agent, `ESCG-harness/1 (automated test; +https://evanstonseniorcareguide.com/)`,
and `test.js` fails if any harness drops it. Filter the log on that exact
string (the log's `UserAgent` filter is an exact match) and the harness
traffic disappears from every count. Before 2026-10-31 the harnesses ran as
ordinary headless Chrome and were classed `tooling`; rows before that date
are excluded by category instead, which is coarser.

The three beacon files that nothing on the site fires any more
(`westminster-call-click`, `westminster-directions-click`,
`westminster-inquiry-form-click`) were removed the same day, because an
enumerating bot had fetched each of them once and they would have read as
visitors reaching a stage that no longer exists.

## Readings

| Window (UTC) | Verified `landed` | Verified assessment started / completed | Verified form views / inquiries | Estimate: homepage requests (browser class) | Notes |
| --- | --- | --- | --- | --- | --- |
| 2026-10-30 00:05 – 2026-10-31 00:05 | not usable | not usable | not usable | 67 | Contaminated: 1,496 of 1,949 requests were the test harnesses (classed `tooling`); the 27 completions and 31 form views are the harness runs. Recorded so nobody reads it as a day of visitors. |
| 2026-10-31 00:30 – 13:35 | **0** | 0 / 0 | 0 / 0 | 48 | First clean window since launch, no harness runs. 495 requests: 366 `browser` (84 were `/wp-admin/install.php` probes, a run of `.env` probes), 84 `other`, 32 `tooling`, 10 `crawler`, 3 `ai-agent`. Not one beacon fired. Two fetches of the levels guide were the only page reads beyond `/`. |

Proof the exclusion works: a tagged harness run against the live site at
14:17–14:19 UTC on 2026-10-31 produced 374 requests, every one carrying the
exact User-Agent above and nothing else in that window but a scanner; a
reading taken with the `UserAgent` filter set to that string drops all 374.

The free hosting plan keeps 24 hours of log, so a row must be taken at least
daily or the window is lost. Until a scheduled snapshot exists (proposed,
not approved), rows are taken by hand during a working session.
