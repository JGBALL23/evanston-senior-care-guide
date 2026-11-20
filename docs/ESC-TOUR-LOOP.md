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

## Acquisition optimization principle

Optimize for actual qualified tour inquiries, not commits, task counts, email volume, or generic page output. On each run identify the biggest evidenced bottleneck, choose a reversible, authorized action, verify its real-world status, learn from the result, and prefer higher-value experiments over repeating low-yield channels. Track proposals, sent messages, site changes, visitors, inquiries, and confirmed tours as distinct states. The event-triggered chain can progress automatically when useful work is completed, but is not an unlimited always-running process. An existing hourly monitor should reactivate the chain when *new* relevant evidence makes more work worthwhile. No duplicate sends, artificial activity, or use of GitHub commits to circumvent model limits.

## Hourly compounding acquisition backlog

The owner wants a cumulative, prioritized **hourly growth-work queue**, not a three-item checklist or an artificial endless ping loop. **Use the already-running `ESCG cloud operator (hourly, 24/7)` as the queue builder; do not create another scheduled task.** This section supersedes older instructions that restricted all new discovery to a handful of fixed restart events. Fresh, verified, previously unqueued opportunities may justify work even without an email reply.

**Hourly queue-builder algorithm (cloud monitor):**

1. Read `ops/esc-tour-loop.json` on `automation/esc-tour-loop`, historical `ops/state.json` and `ops/growth.json` on `ops/operator-state`, recent PRs, and available live acquisition evidence. Recheck latest remote head before a write.
2. **Search for approximately 10 candidate actions every scheduled hour**, varying across distribution/referrals, caregiver audiences, high-intent search, conversion friction, partnership follow-through, and measurement. Compare each candidate with the existing queue, completed, dropped, blocked, operator actions, Gmail Sent when accessible, and the external-action permissions. Research actual concrete targets; do not repeat low-fit classes already examined or assume old information is fresh.
3. **Add up to 10 NEW, genuinely worthwhile, unique tasks per hour**; fewer (including zero) is correct if evidence is weak. Never manufacture 10 tasks to hit a number. Each queued task needs a stable ID, a specific action and target, `workstream`, `status`, source/evidence, why it can move qualified families toward a voluntary tour inquiry, assigned executor, `done_when`, and any dependency or `not_before_utc`. Use `ready` only when it is immediately authorized and executable. Clearly mark `waiting_on_data`, `delegated`, or `blocked` where appropriate.
4. **Carry forward all unfinished work across hours**. Do not replace or reset the queue on every hourly cycle. Prefer completing tasks to endlessly accumulating ideas. Target a practical maximum of 100 pending items; above that, cleanly reprioritize and close proven-stale/duplicate/low-fit items, preserving their outcomes, instead of adding more. Public repository may contain only public-safe summaries, not private addresses, personal leads or confidential messages.
5. Rank outstanding ready work by expected contribution to qualified reach/inquiries, verifiable evidence, feasibility, urgency and effort. **One high-impact completed action beats ten research notes.** Keep the designated outreach operator responsible for authorized sending/social activity; the queue builder and event-loop worker do not inherit those permissions.
6. If **at least one** meaningful new task or verified outcome is added, make **one consolidated substantive commit per hourly queue-building cycle** to `automation/esc-tour-loop`; verify the pushed PR #77 head. This gives the existing event-triggered acquisition task a natural opportunity to consume work. A change to `ops/operator-state`, a commit on another branch, or merely editing Claude's instructions does NOT activate PR #77.
7. If there is no genuinely new work, **do not commit a timestamp or pretend to have completed something**; perform the next hourly evaluation normally. Respect Claude/GitHub limits, no duplicate triggers, and the independent hourly schedule. If a push conflicts with another session, re-read and reconcile rather than force-pushing.

**Consumption (GitHub acquisition loop):** On a PR #77 event, prioritize the highest-value `ready` item, do an authorized and verified business action, record outcome accurately, discover better next work as appropriate, and push **a meaningful completion/next-action commit** to the same head branch. Distinguish researched, prepared, delegated, sent, published, visitor, inquiry and confirmed tour. A task transferred to the external operator is `delegated`, not a sent email or completed tour. If no ready authorized tasks exist, do independent discovery once; otherwise leave the queue for the next hourly cycle rather than committing a fake heartbeat.

**Business measure:** track verified qualified visitors, engagement, opt-in inquiries, tour requests and independently verified tours, not number of generated tasks, commits or unexecuted proposals. The system is available across all hours, but Claude's sessions are discrete and may be idle when no useful authorized action exists.

## Event-run algorithm

1. **Validate event.** Handle only `Pull request: Commits pushed` for the open PR whose head is exactly `automation/esc-tour-loop`. Check current PR head and latest remote branch before working. Ignore stale duplicate events or closed/merged PRs. Read the current loop state and existing operator logs; do not assume a session's chat history is current.
2. **Discover and choose the next useful action.** Choose the highest-value `ready` entry based on current evidence, not just its numerical priority. Do *not* repeat completed outreach, Nov 18 complaint/Medicare CTA changes, general Facebook scans with no qualified requests, or tasks whose only benefit is keeping the loop alive. **An empty queue is a discovery trigger, not completion of the mission:** read fresh evidence, independently identify the current acquisition bottleneck, evaluate multiple candidate actions, execute the strongest genuinely valuable authorized action when feasible, and replenish only evidence-backed work. Do not require Joseph to provide the next task.
3. **Do the work now.** Execute as much as is authorized and technically available. Verify sources on the originating sites, check existing work, run applicable tests for code. For an actual site fix, prepare a **separate** small review PR with tests; do not deploy or merge. For an external outreach action, create a properly disclosed proposal/draft for the existing operator, not an outbound send.
4. **Verify and record real evidence.** Before marking a task done, give a concrete artifact, official source, tested PR or externally verified result. Distinguish `done`, `blocked`, and `dropped`; never write `done` for a draft that was merely proposed to the external operator. Recheck whether the item is already completed in GitHub or Gmail logs before any side effect. Record only public-safe summaries in `ops/esc-tour-loop.json`.
5. **Learn, plan, and hand off.** Record whether the action improved qualified reach, meaningful engagement, conversion, or follow-through; identify what to improve in the next experiment. Before each meaningful completion commit, reassess the bottleneck and discover credible next opportunities even if the former queue is empty. Leave the next genuinely useful authorized action `ready` when supported by evidence. Commit the verified result/next plan to `automation/esc-tour-loop`; the **PR synchronization event from that substantive commit** wakes the next session. Finish after the push to avoid overlapping work.
6. **No fake heartbeat; autonomous reactivation.** Exhaust independent, evidence-based opportunity discovery before declaring genuine idle. If nothing worthwhile is currently authorized, **do not commit** a timestamp, status-only change, empty work, invented research, or self-trigger signal. Stop with an honest reason and the specific future evidence that could enable work. The existing hourly `ESCG cloud operator (hourly, 24/7)` is responsible for checking for fresh actionable signals and committing **a real, non-duplicate evidence-backed new task** to this branch when warranted, thereby reawakening the PR event loop without Joseph manually supplying tasks. It is a monitor/reactivator, not a second outbound sender. No GitHub event occurs just because a Claude task's text was edited.
7. **Conflict discipline.** Never force-push or rewrite history. If another worker updated the branch, fetch and re-evaluate. If the action is already recorded, stop. For ambiguous external effects, stop and flag for operator review rather than repeat them. Keep one work item per event run and one meaningful completion commit.
8. **Rate and safety limits.** Obey Anthropic rate limits and any safety refusals. Do not attempt to escape per-task limits by generating meaningless commits. No unbounded notifications. The owner can stop the loop by pausing its Claude Scheduled Task.

## Mandatory end-of-session GitHub handoff (required on every execution)

A GitHub PR **commits-pushed** trigger only fires when a new commit is successfully pushed to the exact standing PR head branch. Ending a Claude response or editing scheduled-task text does not trigger anything. Therefore, **do not finish an execution that completed substantive new work without attempting the GitHub handoff**:

1. **Reflect and discover:** evaluate the work just done against actual acquisition outcomes, identify the biggest remaining bottleneck, and independently research the next credible authorized task. An empty or waiting queue means discovery is required; it does not mean the growth mission is over.
2. **Persist:** record the real verified result (or material new finding), status, evidence, learned lesson, dependencies, and next evidence-backed task in `ops/esc-tour-loop.json`. Keep all content safe for the public repository. The next task can be a handoff to the designated outreach operator, but record it as proposed, not sent.
3. **Commit and push:** fetch/check the latest remote head; write the state change as one nonempty, substantive commit to **`automation/esc-tour-loop`** (head of open PR #77), and push it. Do not merely commit a separate work branch or `ops/operator-state`: those do **not** match the Claude event trigger. Do not force-push or merge the standing PR.
4. **Verify delivery:** read the GitHub PR head after the push and ensure its latest SHA is the commit just pushed. Only then report that the next GitHub event has been **generated**. The next Claude run is not confirmed until observed in Claude history or by its own subsequent commit.
5. **End the session** after the verified push so that the event-triggered next execution can resume. Never keep working concurrently after handing off.

**Real idle exception:** If, after serious independent discovery, nothing new or authorized is worth doing and no material result or state change exists, do not create a status-only/heartbeat commit to force another run. Record the reason in the session report, and let the already existing hourly cloud monitor reawaken the loop only upon genuine new evidence. Usage caps, unavailable GitHub permissions, and failed pushes must be reported as blockers, not bypassed. Never claim a trigger was fired unless the remote commit was verified.

## First-run checks

- Check the event's exact head branch and GitHub PR.
- Check `ops/esc-tour-loop.json` against the latest shared operator record; the historical counter may be stale, so reconcile before treating it as live.
- Read current `main` and deployed pages rather than treating 2026-10 documents as today's site status.
- Start with the highest-value evidence-backed `ready` work item; if the queue is empty, independently discover and evaluate new worthwhile acquisition work before deciding idle. Do not rebuild infrastructure or invent another scheduled system.
- When a real result is verified, update state **once**, identify the strongest warranted next action, push the substantive commit, and finish. The next GitHub event should start the next session. When genuinely idle, await fresh evidence through the existing hourly monitor, not a fake commit.

## Production activation checklist (outside this repository)

1. In Claude Scheduled Tasks, add a **new** routine named `ESCG Tour Acquisition Loop`.
2. Trigger: **GitHub event** → repository `JGBALL23/evanston-senior-care-guide` → **Pull request: Commits pushed**.
3. Filter: **Head branch** `is one of` `automation/esc-tour-loop`.
4. Use the exact saved task instruction given to the owner. Do not use PR #76 or its test branch.
5. Verify permissions and the routine is Active. Only then make an initial **meaningful** queue/activation commit and observe at least two event-driven runs.
6. Do not disable the existing outbound operator until the new workflow has proven its non-duplicate behavior and outbound responsibility is deliberately transferred.

## Minimal Claude task instruction

> You are the event-driven Evanston Senior Care Guide tour-acquisition worker. The event is from the PR whose head branch is `automation/esc-tour-loop` in `JGBALL23/evanston-senior-care-guide`. Read `docs/ESC-TOUR-LOOP.md` and `ops/esc-tour-loop.json` from that exact branch and follow their rules. Select and execute one genuinely useful authorized tour-acquisition task, verify the outcome, and only then commit the public-safe outcome/next ready task to that same head branch. A substantive completed action requires an end-of-session handoff: update the shared public-safe state, push one substantive commit to the PR #77 head branch, then verify that GitHub shows that commit as the new PR head before reporting the next trigger was generated. When the queue is empty, actively discover the next evidence-backed acquisition opportunity rather than relying on user-supplied tasks. If truly no valuable authorized action exists after discovery, stop WITHOUT a commit and let the hourly monitor detect fresh evidence for reactivation. Keep the existing Claude chat as sole external sender; do not send email, post, deploy, change privacy handling, or contact families. No empty heartbeat commits, no rate-limit circumvention, no duplicate work. Report substantive outcomes only.
