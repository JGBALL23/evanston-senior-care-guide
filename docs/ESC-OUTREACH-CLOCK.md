# ESCG 24/7 cloud coverage: activating the existing designated outreach operator

**Status: DISABLED BY DEFAULT.** Review-only. The workflow performs no outreach by itself, and cannot launch Claude until enabled using a per-routine token. It never authorizes an additional sender.

## Why this is different from another task list

The existing hourly *cloud operator* checks metrics but cannot send or post. The GitHub-triggered PR #77 acquisition worker proposes website fixes, drafts and discovery but is also not allowed to send. Only the **existing** `ESCG hourly operator` is authorized to send permitted organizational referral emails and community posts. Its last recorded execution was a one-time run, leaving real outbound distribution behind the research loop.

This workflow on GitHub's cloud can **wake that existing routine every hour** via Anthropic's official API trigger, even with the owner's computer off. It does not create a new Claude task, circumvent usage quotas, guarantee new visitors, or keep one AI session alive nonstop. It supplies continuous *availability* through hourly launch attempts, subject to platform scheduling, billing and limits.

## One-time activation (do not share secrets in chats or source files)

1. Review this PR. Scheduled GitHub Actions **only run on the default branch**, so the workflow must be merged into `main` before it can run. It stays disabled until Step 4.
2. At [Claude routines](https://claude.ai/code/routines), open the existing **ESCG hourly operator** (sole authorized sender), click **Edit > Add API trigger > Generate token**. Copy its official API fire URL and the per-routine bearer token. Do not change the sender, prompt, or authorization.
3. GitHub repository **Settings > Secrets and variables > Actions**: create two **Secrets**: `ESCG_OPERATOR_FIRE_URL` (official exact URL) and `ESCG_OPERATOR_FIRE_TOKEN` (starts `sk-ant-oat01-`). Do not put either in a variable, issue, commit or public file.
4. In **Actions > Variables**, set `ESCG_WAKE_ENABLED` to `true` **only if the existing operator is not already on an hourly recurring schedule**. If it is already hourly, use that trigger instead; enabling this workflow would duplicate sessions. The separate cloud analytics monitor can remain hourly.
5. On **Actions > ESCG authorized outreach operator — hourly cloud wake**, use **Run workflow** once and inspect the resulting Claude session. A session start does NOT mean an email or post was actually sent. Confirm that the run reads the existing queues, performs any authorized due action, and records outcomes.
6. Disable instantly by setting `ESCG_WAKE_ENABLED` to `false`. Monitor all actual sends and daily Claude usage. For slower/cheaper execution change the cron cadence after owner review.

## What the AI can—and cannot—do

- Read the existing outreach and acquisition queues, assess which due posts and organizational referral notes are ready, preflight Gmail Sent/replies/declines, and **execute only actions already authorized in the Claude routine**.
- Respond to properly consented inbound inquiries within the original operator's authorization; do not leak personal, medical, or private family information into this public repository.
- Respect every Facebook group's rules and published communication restrictions. No random family DMs, private-group scraping, spam, repeated declined contacts, fake endorsements, or misleading sales claims.
- The website's optional form does not create an open permission to pursue families. Collect only previously disclosed/consented information. Do not publish unreviewed PRs on behalf of the owner.

## Limitations

The official API starts **a new routine session for each POST**, offers no idempotency key, and can return 429 for usage limits. This workflow deliberately does not retry requests and uses concurrency control only for GitHub jobs, not Claude's potentially overlapping sessions. A long Claude run can still overlap the next hourly wake; if that happens, use a slower cadence instead of multiple senders.

Github cron can be delayed. Anthropic's experiment and account usage rules may change. Routine starts consume the **Claude subscription allowance** and may be significantly limited by plan. Do not turn this on without confirming capacity. Operator state must distinguish actual sends, genuine visitors, opt-in inquiries and verified tours from merely successful wake-ups.
