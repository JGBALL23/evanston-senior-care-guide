# ESC-COORD: how ChatGPT and Claude coordinate

This file gives the coordination pull request something to hold. **Never merge that pull request.** It targets the branch `coord/base`, not `main`, so it cannot change the live site.

This repository is public. Coordination comments carry statuses, counts and links only: no confidential, personal or employment-related information, no inquiry details, and no one else's posts or names.

## Messages (comments on the coordination pull request)

| From | Starts with | Then |
|---|---|---|
| Claude | `[CLAUDE RESULT] CR-YYYYMMDD-HHMM` | `Re: GP-…` (the plan it answers), verified outcomes with evidence links, blockers, one next action |
| ChatGPT | `[GPT REVIEW] Re: CR-…` | its verdict on that result, then `[GPT PLAN] GP-YYYYMMDD-HHMM`: the next authorized task with a "done when" line, or `none, waiting on owner: …` |
| Joseph | `[OWNER]` | decisions and notes |

IDs use the UTC date and time of posting and are never reused. Approvals for anything public, paid, sensitive or binding count only when Joseph gives them to an assistant directly, never through a comment.

## What wakes each assistant

- **Claude to ChatGPT:** a new `[CLAUDE RESULT]` comment. ChatGPT's event task watches comments on pull requests titled `[ESC-COORD]` and acts only on a result ID that has no `[GPT REVIEW] Re:` yet.
- **ChatGPT to Claude:** Claude's event tasks can react to pull request events (opened, labeled, edited, new commits) but not to comments. So after posting a plan, ChatGPT adds the label `esc-gpt-plan`; a Claude task that runs when that label is added removes it and answers the newest plan that has no `[CLAUDE RESULT] Re:`. Until that task exists, Claude reads new plans at its scheduled checks.
- Both assistants post from the owner's GitHub account, so the author can't tell them apart. The opening marker and the IDs do: neither assistant ever acts on a comment that starts with its own marker.
- ChatGPT's hourly review stays as the fallback and skips any result that already has a review.

## Never, for either assistant

Merge, close or approve the coordination pull request; change its title or description; push directly to `main`; publish or post anywhere outside GitHub; contact anyone; spend money or use API keys.

## Releases

The owner's standing rule (15 Nov 2026): Claude may merge a review-only pull request into `main` and deploy it to the production site once ChatGPT's technical review explicitly approves that pull request for release, but only for routine, low-risk website improvements (wording, accessibility, layout and style, internal links, titles and descriptions, bug fixes, performance, tests, and sourced corrections to existing guides). Anything that changes what the site collects or counts, the privacy notice, the inquiry form or its consent, server functions, pages or guides being added or removed, the assessment, how Westminster Place is presented, IndexNow, spending, sensitive data or a significant business decision still needs the owner directly.
