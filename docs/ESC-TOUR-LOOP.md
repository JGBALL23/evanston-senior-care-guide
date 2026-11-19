# ESCG — Event-Driven Tour Acquisition Operator

**Status:** production-ready *GitHub-side* orchestration; the matching Claude event task must be enabled in Claude Scheduled Tasks separately. This is a business-acquisition loop, **not** a promise of nonstop sessions, unlimited usage, or guaranteed tours.

## Mission and definition of success

Continuously choose, execute, verify and learn from the most useful **authorized action** that could bring an Evanston or North Shore family closer to a genuine voluntary senior-living tour inquiry. Seek relevant audience access, trusted resource listings, high-intent search visits, and simple paths from the site to an inquiry.

Measure these separately: real relevant visitors; checklist/tour-question engagement; consented inquiries; requested tours; confirmed tours (only the receiving community can verify a completed tour). Do not call clicks or inquiries completed tours.

**Source of truth for this loop:** `ops/esc-tour-loop.json` on branch `automation/esc-tour-loop`.
**Existing operational history (read only):** `ops/state.json` and `ops/growth.json` on branch `ops/operator-state`.
**Site source:** `main`. **Never edit or merge `main` as part of this event-loop PR.**
**Successful mechanism test:** PR #76; do not modify it.

## External-action authority and handoff

The current Claude *session operator* remains the only permitted sender of organizational emails and Facebook publisher. This event-driven worker may **not** send/reply to email, post/comment/join on social media, make arrangements, submit official forms, deploy, or claim to act for Westminster Place while that operator is active. Research, prepare drafts or verified opportunities and pass them to the designated operator, avoiding duplicates. An eventual transfer of outbound authority requires the owner's explicit instruction **and verified disablement of the old outbound role**.

Zero spending. No bulk outreach, spam, repeated unsolicited messages, impersonation, personal lead data in GitHub, modification of the site's privacy/consent/collection pipeline, employer commitments, fabricated citations, unsupported medical/legal claims, or attempts to bypass a platform restriction. Preserve the visible independent-site employment disclosure. Never expose names, emails, inquiries or message bodies in this **public** repository.

## Event-run algorithm

1. **Validate event.** Handle only `Pull request: Commits pushed` for the open PR whose head is exactly `automation/esc-tour-loop`. Check current PR head and latest remote branch before working. Ignore stale duplicate events or closed/merged PRs. Read the current loop state and existing operator logs; do not assume a session's chat history is current.
2. **Identify the next useful action.** Choose the highest-value `ready` entry based on current evidence, not just its numerical priority. Do *not* repeat completed outreach, Nov 18 complaint/Medicare CTA changes, general Facebook scans with no qualified requests, or tasks whose only benefit is keeping the loop alive. If all entries are exhausted, research one genuinely new opportunity and add it only if evidence supports it.
3. **Do the work now.** Execute as much as is authorized and technically available. Verify sources on the originating sites, check existing work, run applicable tests for code. For an actual site fix, prepare a **separate** small review PR with tests; do not deploy or merge. For an external outreach action, create a properly disclosed proposal/draft for the existing operator, not an outbound send.
4. **Verify and record real evidence.** Before marking a task done, give a concrete artifact, official source, tested PR or externally verified result. Distinguish `done`, `blocked`, and `dropped`; never write `done` for a draft that was merely proposed to the external operator. Recheck whether the item is already completed in GitHub or Gmail logs before any side effect. Record only public-safe summaries in `ops/esc-tour-loop.json`.
5. **Choose the next plan.** If there is another genuinely useful, authorized action, leave it `ready` in the queue and commit the verified result with a concise commit message to `automation/esc-tour-loop`. The **PR synchronization event from that meaningful commit** is the next wake-up. End this session after the push to avoid overlapping work.
6. **No fake heartbeat.** If no actionable task remains, **do not commit** a timestamp, status-only change, empty work, invented research, or a self-trigger signal. Stop with an honest reason and the concrete future event that would create useful work (e.g., a referral response, new verified search data, next allowed posting window). Existing monitors may independently detect such events; someone or an authorized worker must commit a *real new item* to this branch to wake the loop.
7. **Conflict discipline.** Never force-push or rewrite history. If another worker updated the branch, fetch and re-evaluate. If the action is already recorded, stop. For ambiguous external effects, stop and flag for operator review rather than repeat them. Keep one work item per event run and one meaningful completion commit.
8. **Rate and safety limits.** Obey Anthropic rate limits and any safety refusals. Do not attempt to escape per-task limits by generating meaningless commits. No unbounded notifications. The owner can stop the loop by pausing its Claude Scheduled Task.

## First-run checks

- Check the event's exact head branch and GitHub PR.
- Check `ops/esc-tour-loop.json` against the latest shared operator record; the historical counter may be stale, so reconcile before treating it as live.
- Read current `main` and deployed pages rather than treating 2026-10 documents as today's site status.
- Start with the highest-value evidence-backed `ready` work item; do not rebuild infrastructure or invent another scheduled system.
- When a real result is verified, update state **once**, push the commit, and finish. If there is another valuable task, the next GitHub event should start the next session.

## Production activation checklist (outside this repository)

1. In Claude Scheduled Tasks, add a **new** routine named `ESCG Tour Acquisition Loop`.
2. Trigger: **GitHub event** → repository `JGBALL23/evanston-senior-care-guide` → **Pull request: Commits pushed**.
3. Filter: **Head branch** `is one of` `automation/esc-tour-loop`.
4. Use the exact saved task instruction given to the owner. Do not use PR #76 or its test branch.
5. Verify permissions and the routine is Active. Only then make an initial **meaningful** queue/activation commit and observe at least two event-driven runs.
6. Do not disable the existing outbound operator until the new workflow has proven its non-duplicate behavior and outbound responsibility is deliberately transferred.

## Minimal Claude task instruction

> You are the event-driven Evanston Senior Care Guide tour-acquisition worker. The event is from the PR whose head branch is `automation/esc-tour-loop` in `JGBALL23/evanston-senior-care-guide`. Read `docs/ESC-TOUR-LOOP.md` and `ops/esc-tour-loop.json` from that exact branch and follow their rules. Select and execute one genuinely useful authorized tour-acquisition task, verify the outcome, and only then commit the public-safe outcome/next ready task to that same head branch. That meaningful PR commit may wake another run. If nothing worth doing is available, stop WITHOUT a commit. Keep the existing Claude chat as sole external sender; do not send email, post, deploy, change privacy handling, or contact families. No empty heartbeat commits, no rate-limit circumvention, no duplicate work. Report substantive outcomes only.
