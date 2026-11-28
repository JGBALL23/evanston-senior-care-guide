#!/usr/bin/env python3
"""loopctl: small helper for the ESCG loop state files.

It exists so that a worker session never has to print or hand-edit the large
state files: it prints compact JSON and makes the routine edits itself.
Standard library only. It never touches the network and never runs git.

Read commands
  status   [--monitor-hours N] [--run RUN]
                                    what is due now and when the next thing is due; with --run, ready tasks
                                    that this session may not work (not_run) are listed under ready_next_session
  show ID                           one queue task, completed task, map item or scout
  dupes                             one line per known task and map item, for duplicate checks
  validate                          parse and sanity-check the state files
  plan                              planner view: pipeline, lanes (owner WIP, cooldown), whether planning is due
  outcomes [--days N] [--record]    qualified visitors, inquiries, referrals and tours from cloud.json's
                                    scoreboard, by week; --record stores the newest full week in planner/outcomes

Write commands (edit the working copy only; committing and pushing is the caller's job)
  lock RUN                          take the session lock (exit 3 if a live session holds it);
                                    the holder runs it again before each task as a heartbeat
  plan-done LANE --added N --result TEXT [--cooldown-hours H]
  start WHAT                        mark what the session works on now (a task id, angle:ID or plan:LANE);
                                    also a heartbeat. finish / sweep-done add its minutes to productive time
  sweep-done ANGLE --added N --result TEXT [--recheck-hours H]
                                    record one sweep angle checked (N tasks added; 0 is a complete result)
  metrics [--days N]                productive time, deliverables, stop reasons and outcomes for N days
                                    record a planning pass; N = 0 puts the lane on cooldown (no filler)
  add --from FILE                   add a queue task from a JSON file; assigns the next ACQ id
  update ID --from FILE             merge fields from a JSON file into a queue task
  finish ID --from FILE [--status done|dropped]   move a queue task to completed
  set PATH JSON [--file F]          set one value, e.g. opportunity_map/items[id=D13]/status '"watch"'
  append PATH JSON [--file F] [--front] [--keep N]   add to a list
  monitor-done                      record that the monitoring pass ran now
  explore KEY --avenue needs|search|channels|quality|frontier --added N --result TEXT [--candidates N]
              [--lane L] [--new-evidence TEXT] [--verdict act|watch|drop]
                                    record one avenue of independent backlog discovery (procedure step 7).
                                    Exit 5 if the same KEY was explored inside its recheck window (14 days)
                                    and nothing new is named: pick a different question, source or segment.
                                    --avenue frontier answers one open question of planner/frontier/questions
                                    (KEY frontier:<id>, --verdict required) and marks it explored
  frontier-add --from FILE          add a genuinely new opportunity question (question, lever, evidence,
                                    output, why); exit 5 for a repeat or a rewording of an existing one
  project-add --from FILE           start a growth project (name, goal, metric, why = the dated evidence, plan,
                                    next_step, kill_when); exit 5 when a project already covers it
  project-step ID --run RUN --result TEXT --new-evidence NEXT [--resume-when UTC] [--lane STAGE]
               [--verdict waiting|won|failed|parked]
                                    record one step of a project and its next step (start project:ID before
                                    the work, so that its minutes count as productive time)
  project-discover LENS --result TEXT [--from FILE]
                                    record the session's one project-discovery assignment (status shows it
                                    under project_discovery when no project step is due and no frontier
                                    question is open): with --from it starts the project found, without it
                                    it records why this evidence holds none. Exit 5 for a second one in the
                                    same session or for a lens examined inside its cadence
  close RUN --done N --changed M --outcome TEXT [--launch TEXT] [--tasks TEXT] [--monitor-hours N]
            [--stop-reason R --considered TEXT --resume-when TEXT] [--fallback-skipped TEXT]
            [--package-skipped TEXT]
                                    write the session record, release the lock, print next/wake.
                                    Exit 6 (nothing written) while status shows package.due (the daily approval
                                    package has not been cut inside its window): cut it, or say with
                                    --package-skipped why not.
                                    Exit 6 likewise while status shows package.recut_due (work that belongs in
                                    the package was finished after its cut and the window is still open): cut
                                    once more, or say with --package-skipped why not.
                                    Exit 6 (nothing written) when the stop reason is no-worthwhile-work while
                                    backlog discovery is due and this session recorded fewer than three avenue
                                    classes with explore; explore more, or say with --fallback-skipped why not.
                                    Exit 6 likewise while status shows frontier.due (an open frontier question
                                    and none answered in this session): an empty queue, a cooldown or a pending
                                    approval does not end the search for genuinely new opportunities
                                    Exit 6 likewise while status shows project_discovery.due (every project
                                    waits, no frontier question is open and this session has not done its
                                    discovery assignment).
                                    A rest of backlog discovery follows only a conclusion that found nothing:
                                    a session whose explorations added tasks leaves it due (28 Nov 2026).

Due times have a grace (30 minutes): what falls due within it counts as due now, so that one session takes
what comes due close together. The wake time is the first moment at which a session would really find work
(Make's timer looks every 15 minutes since 27 Nov 2026).

Common options: --loop PATH (default ops/esc-tour-loop.json), --now ISO (tests only).
"""
import argparse
import datetime as dt
import json
import math
import os
import re
import sys

LOCK_STALE_MIN = 90
PLAN_LOW_WATER, PLAN_MIN_SCORE, PLAN_COOLDOWN_H = 3, 2.0, 24
WORKSTREAM_LANE = {"build": "build", "assets": "build", "content": "build", "publish": "publish",
                   "search_acquisition": "search", "local_seo": "search", "conversion": "conversion",
                   "referral_distribution": "partnerships", "referral_partnerships": "partnerships",
                   "qualified_audience": "distribution", "distribution": "distribution",
                   "demand": "demand", "technical": "technical", "measurement": "measurement",
                   "discovery": "discovery", "system_test": "system"}
WAKE_MIN, WAKE_MAX, WAKE_DEFAULT, WAKE_RETRY = 30, 2880, 720, 120
DUE_GRACE_MIN = 30
FB_AVENUES = ("needs", "search", "channels", "quality", "frontier")
FR_MIN_SESSION, FR_PER_DAY, FR_MAX_OPEN = 1, 4, 60
FR_VERDICTS = ("act", "watch", "drop")
FB_MIN_AVENUES, FB_RECHECK_DAYS, FB_BASE_H, FB_MAX_H, FB_LOG_KEEP = 3, 14, 12, 96, 150
HANDOFF_SESSIONS_24H = None   # no cap on sessions in 24 hours unless planner/handoff_sessions_24h sets one
PKG_WINDOW = ("05:00", "10:30")
NO_WORK_REASONS = ("no-worthwhile-work", "approval-pending")
TS = re.compile(r"^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})(?::(\d{2})(?:\.\d+)?)?Z$")
DATE_KEYS = ("not_before_utc", "recheck_utc")
WAIT_KEYS = ("not_before", "waiting_for", "why_blocked", "depends_on", "done_when")
READY, WAIT_DATA, WAIT_OWNER = "ready", "waiting_on_data", "waiting_on_owner"


def parse_ts(value):
    if not isinstance(value, str):
        return None
    m = TS.match(value.strip())
    if not m:
        return None
    y, mo, d, h, mi, s = (int(x) if x else 0 for x in m.groups())
    try:
        return dt.datetime(y, mo, d, h, mi, s, tzinfo=dt.timezone.utc)
    except ValueError:
        return None


def fmt(t):
    return t.strftime("%Y-%m-%dT%H:%MZ")


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(path, data):
    text = json.dumps(data, indent=1, ensure_ascii=False) + "\n"
    json.loads(text)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def out(obj, code=0):
    print(json.dumps(obj, indent=1, ensure_ascii=False))
    sys.exit(code)


def fail(message, code=2):
    print(json.dumps({"error": message}, ensure_ascii=False))
    sys.exit(code)


def short(value, n=110):
    s = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    s = " ".join(s.split())
    return s if len(s) <= n else s[: n - 1] + "…"


def title_of(task):
    for k in ("task", "hypothesis", "opportunity", "title"):
        if task.get(k):
            return short(task[k])
    return ""


def controller(d):
    c = d.setdefault("controller", {})
    c.setdefault("lock", {"holder": "", "utc": ""})
    c.setdefault("monitor", {"last_utc": ""})
    c.setdefault("sessions", [])
    return c


def task_date(task):
    for k in DATE_KEYS:
        t = parse_ts(task.get(k))
        if t:
            return t
    return None


def lane_of(task):
    if task.get("lane"):
        return task["lane"]
    return WORKSTREAM_LANE.get(task.get("workstream") or "", "other")


def package_inside(d):
    """Pull requests that reach Joseph inside the open daily package: together they are ONE decision (one
    merge), so they count once against a lane's owner limit (planner/package/counts_as_one). Joseph, 24 Nov
    2026: "a pending approval blocks only the affected action, not independent business work"; 26 Nov 2026:
    a pending approval "should not prevent you from exploring genuinely new opportunities". Read only."""
    pk = (d.get("controller") or {}).get("package")
    cfg = (d.get("planner") or {}).get("package")
    if not isinstance(pk, dict) or not isinstance(cfg, dict) or not cfg.get("counts_as_one") or not pk.get("pr"):
        return set()
    nums = [pk.get("pr"), pk.get("batch"), pk.get("accuracy")] + list(pk.get("contains") or [])
    return {n for n in nums if isinstance(n, int) and not isinstance(n, bool)}


def as_one(n, packed):
    return n if packed <= 0 or n <= 0 else max(1, n - packed + 1)


def plan_view(d, now, pipeline):
    """Planner state. Read only: never changes d."""
    pl = d.get("planner") or {}
    low = int(pl.get("low_water", PLAN_LOW_WATER))
    queue = d.get("queue") or []
    inside = package_inside(d)
    lanes = []
    for ln in sorted(pl.get("lanes") or [], key=lambda x: (x.get("order", 99), str(x.get("id")))):
        lid = ln.get("id")
        waiting = sum(1 for t in queue if t.get("status") == WAIT_OWNER and lane_of(t) == lid)
        packed = len({p for p in (ln.get("open_prs") or []) if isinstance(p, int) and not isinstance(p, bool) and p in inside})
        wip = max(as_one(waiting, packed), as_one(int(ln.get("owner_open") or 0), packed))
        limit = int(ln.get("owner_wip_limit", 3))
        cool = parse_ts(ln.get("cooldown_until_utc"))
        cooling = cool is not None and cool > now
        live = sum(1 for t in queue if t.get("status") in (READY, WAIT_DATA) and lane_of(t) == lid)
        lanes.append({"id": lid, "order": ln.get("order"), "enabled": bool(ln.get("enabled", True)),
                      "owner_wip": wip, "wip_limit": limit, "in_package": packed,
                      "saturated": wip >= limit, "cooling_until": fmt(cool) if cooling else None,
                      "live_tasks": live, "last_planned_utc": ln.get("last_planned_utc") or None,
                      "plannable": bool(ln.get("enabled", True)) and wip < limit and not cooling,
                      "_cool": cool if cooling else None})
    plannable = [x["id"] for x in lanes if x["plannable"]]
    due = bool(pl.get("enabled", True)) and pipeline < low and bool(plannable)
    wake = None
    if pl.get("enabled", True) and pipeline < low and not plannable:
        ends = [x["_cool"] for x in lanes if x["_cool"] and not x["saturated"]]
        wake = min(ends) if ends else None
    for x in lanes:
        x.pop("_cool", None)
    return {"enabled": bool(pl.get("enabled", True)), "low_water": low, "pipeline": pipeline, "due": due,
            "plannable": plannable, "saturated": [x["id"] for x in lanes if x["saturated"]],
            "lanes": lanes, "_wake": wake}


def sweep_view(d, now, lanes_info):
    """Sweep angles: specific evidence sources the session checks before it may stop (continue by default).
    An angle is due when its recheck time has passed and its lane is not waiting on Joseph. Read only."""
    pl = d.get("planner") or {}
    sat = {x["id"] for x in lanes_info if x.get("saturated")}
    due, waiting, later = [], [], []
    for ang in sorted(pl.get("angles") or [], key=lambda x: (x.get("priority", 9), str(x.get("id")))):
        if not isinstance(ang, dict) or not ang.get("enabled", True):
            continue
        if ang.get("lane") in sat:
            waiting.append(ang.get("id"))
            continue
        nxt = parse_ts(ang.get("next_check_utc"))
        if nxt is None or nxt <= now:
            due.append({"id": ang.get("id"), "lane": ang.get("lane"), "priority": ang.get("priority"),
                        "question": short(ang.get("question") or "", 150)})
        else:
            later.append((nxt, "sweep angle " + str(ang.get("id"))))
    return {"due": due, "waiting_on_owner": waiting, "_later": later}


def grace(d):
    v = (d.get("planner") or {}).get("due_grace_minutes", DUE_GRACE_MIN)
    ok = isinstance(v, (int, float)) and not isinstance(v, bool) and 0 <= v <= 120
    return dt.timedelta(minutes=v if ok else DUE_GRACE_MIN)


def fallback_view(d, now, soon, pipeline, plan, room=True):
    """Independent backlog discovery (procedure step 7). It is due while the pipeline is below the low-water
    mark, some enabled lane can still take work, and no session has just concluded that the avenues are
    exhausted (planner/fallback/exhausted_until_utc). Read only.
    SINCE 28 NOV 2026 a rest follows only a conclusion that found NOTHING. Until then close set the base
    rest (12 hours) after every conclusion: the session that ended at 08:39 UTC that day had found two tasks
    and was rested until 20:39 UTC all the same. A rest left by such a productive conclusion is ignored here.
    Because nothing else would now end a productive chain before it used the hours kept for monitoring and
    the daily package, backlog discovery counts as due only while the usage reserve has room, like the
    frontier and the projects (discovery_room)."""
    pl = d.get("planner") or {}
    fb = pl.get("fallback") or {}
    enabled = bool(fb.get("enabled")) and bool(pl.get("enabled", True))
    open_lanes = [x["id"] for x in plan["lanes"] if x.get("enabled", True) and not x["saturated"]]
    until = parse_ts(fb.get("exhausted_until_utc"))
    lc = fb.get("last_conclusion") if isinstance(fb.get("last_conclusion"), dict) else {}
    lc_added = lc.get("tasks_added")
    productive_last = isinstance(lc_added, int) and not isinstance(lc_added, bool) and lc_added > 0
    resting = until is not None and until > soon and not productive_last
    wanted = enabled and pipeline < plan["low_water"] and bool(open_lanes)
    days = fb.get("explore_recheck_days", FB_RECHECK_DAYS)
    days = days if isinstance(days, (int, float)) and not isinstance(days, bool) and days > 0 else FB_RECHECK_DAYS
    since = now - dt.timedelta(days=days)
    recent = [e for e in (fb.get("log") or []) if isinstance(e, dict) and (parse_ts(e.get("utc")) or since) > since]
    need = fb.get("min_avenues", FB_MIN_AVENUES)
    need = need if isinstance(need, int) and not isinstance(need, bool) and 1 <= need <= len(FB_AVENUES) else FB_MIN_AVENUES
    return {"enabled": enabled, "due": wanted and not resting and bool(room), "wanted": wanted, "room": bool(room),
            "resting_until": fmt(until) if resting else None, "open_lanes": open_lanes,
            "min_avenues": need, "recheck_days": days,
            "recent": [{"key": e.get("key"), "avenue": e.get("avenue"), "utc": e.get("utc"), "added": e.get("added")}
                       for e in recent[:40]],
            "_until": until if (wanted and resting) else None}


FR_ROOM_SHARE = 0.75


def discovery_room(bud):
    """True while the worker's usage reserve has room for discovery: below FR_ROOM_SHARE of its limit for
    24 hours and for 7 days. The last quarter stays for what must not wait: monitoring, the daily package,
    ready tasks."""
    for used_key, min_key, lim_key in (("used_hours_24h", "used_minutes_24h", "limit_hours_per_day"),
                                       ("used_hours_7d", "used_minutes_7d", "limit_hours_per_week")):
        lim = bud.get(lim_key)
        if not lim:
            continue
        used = bud[min_key] / 60.0 if isinstance(bud.get(min_key), (int, float)) else (bud.get(used_key) or 0)
        if used >= FR_ROOM_SHARE * lim:
            return False
    return True


def session_spans(d, now, extra_start=None, extra_end=None):
    """(start, end) of every recorded worker session, plus the session that is closing now if given."""
    spans = []
    for s in (d.get("controller") or {}).get("sessions") or []:
        a, b = parse_ts(s.get("start_utc")), parse_ts(s.get("end_utc"))
        if a and b and b >= a:
            spans.append((a, b))
    if extra_start and extra_start < now:
        spans.append((extra_start, min(extra_end or now, now)))
    return spans


def room_free_at(d, now, extra_start=None, extra_end=None):
    """The moment at which the usage reserve has room for discovery again (below FR_ROOM_SHARE of both limits),
    if no further session runs; None when it has room now. It lets a session wake for discovery, project steps
    and frontier questions as soon as capacity allows (Joseph, 26 Nov 2026: "Automatically resume meaningful
    work whenever resources permit")."""
    pl = d.get("planner") or {}
    spans_all = session_spans(d, now, extra_start, extra_end)
    when = None
    for key, days in (("budget_hours_per_day", 1), ("budget_hours_per_week", 7)):
        limit = pl.get(key)
        if not (isinstance(limit, (int, float)) and not isinstance(limit, bool) and limit > 0):
            continue
        since = now - dt.timedelta(days=days)
        spans = sorted((max(a, since), b) for a, b in spans_all if b > since)
        need = sum((b - a).total_seconds() for a, b in spans) - FR_ROOM_SHARE * limit * 3600
        if need < 0:
            continue
        free = None
        for a, b in spans:
            dur = (b - a).total_seconds()
            if dur > need:
                free = a + dt.timedelta(days=days, seconds=need + 120)
                break
            need -= dur
        if free is None:
            free = (spans[-1][1] if spans else now) + dt.timedelta(days=days, seconds=120)
        when = free if when is None else max(when, free)
    return when


def frontier_view(d, now, run=None, room=True):
    """Standing list of genuinely new opportunity questions (planner/frontier/questions). Joseph, 26 Nov 2026:
    "an empty queue, discovery cooldown, or pending approval should not prevent you from exploring genuinely
    new opportunities." And 27 Nov 2026, after Make went to its Core plan and he refreshed the Claude
    allowance: "Make productive use of the refreshed capacity. Prioritize customer acquisition, SEO, business
    development, conversion improvements and discovering new growth opportunities."
    more: an open question exists and the last 24 hours hold fewer than per_day answers.
    SINCE 27 NOV 2026 open questions are eligible work (starts_sessions) while the usage reserve has room
    (discovery_room): they wake a session and keep the chain going, and they are due for a running session as
    long as that holds. When the reserve is in its last quarter, the older rule applies: due only until this
    session has answered min_per_session, and not counted in eligible. Read only."""
    pl = d.get("planner") or {}
    fr = pl.get("frontier") if isinstance(pl.get("frontier"), dict) else {}
    enabled = bool(fr.get("enabled")) and bool(pl.get("enabled", True))

    def num(v, default):
        return v if isinstance(v, int) and not isinstance(v, bool) and v >= 0 else default

    qs = [q for q in (fr.get("questions") or []) if isinstance(q, dict)]
    open_q = [q for q in qs if q.get("status") == "open"
              and (parse_ts(q.get("not_before_utc")) is None or parse_ts(q.get("not_before_utc")) <= now)]
    open_q.sort(key=lambda q: (num(q.get("priority"), 9), str(q.get("id"))))
    log = [e for e in ((pl.get("fallback") or {}).get("log") or []) if isinstance(e, dict) and e.get("avenue") == "frontier"]
    day = [e for e in log if (parse_ts(e.get("utc")) or now) > now - dt.timedelta(hours=24)]
    mine = [e for e in log if run and e.get("run") == run]
    need, cap = num(fr.get("min_per_session"), FR_MIN_SESSION), num(fr.get("per_day"), FR_PER_DAY)
    more = enabled and bool(open_q) and len(day) < cap
    times = sorted(t_ for t_ in (parse_ts(e.get("utc")) for e in day) if t_)
    slot = (times[len(day) - cap] + dt.timedelta(hours=24, minutes=1)) if (enabled and open_q and len(day) >= cap and len(times) == len(day) and cap > 0) else None
    return {"enabled": enabled, "due": more and (len(mine) < need or bool(room)),
            "more": more, "room": bool(room), "starts_sessions": more and bool(room), "_slot": slot,
            "open": len(open_q), "explored": sum(1 for q in qs if q.get("status") == "explored"),
            "this_session": len(mine), "last_24h": len(day), "min_per_session": need, "per_day": cap,
            "next": [{"id": q.get("id"), "lever": q.get("lever"), "question": short(q.get("question") or "", 220)}
                     for q in open_q[:3]]}


PJ_STATUSES = ("active", "waiting", "won", "failed", "parked")


def projects_view(d, now, run=None, room=True):
    """Growth projects (planner/projects). Joseph, 27 Nov 2026: "Treat growth opportunities as projects worth
    developing, not checkboxes to complete." "Investigate promising opportunities thoroughly, develop actionable
    strategies, build useful assets, and pursue authorized execution. When an opportunity genuinely fails,
    document why and discover another." "Stop optimizing for finishing the queue and start optimizing for
    growing the business."
    A project is active until it is won or failed. Its next step is due when its not_before_utc has passed; a
    waiting project names the event it waits for and is due again when that time passes. Due projects are
    eligible work while the usage reserve has room, before frontier questions. Read only."""
    pl = d.get("planner") or {}
    pj = [p for p in (pl.get("projects") or []) if isinstance(p, dict)]
    live = [p for p in pj if p.get("status") in ("active", "waiting")]
    due = []
    for p in live:
        nb = parse_ts(p.get("not_before_utc"))
        if nb is None or nb <= now:
            due.append(p)
    due.sort(key=lambda p: (p.get("priority") if isinstance(p.get("priority"), int) else 9, str(p.get("id"))))
    nxt = [parse_ts(p.get("not_before_utc")) for p in live if parse_ts(p.get("not_before_utc")) and parse_ts(p.get("not_before_utc")) > now]
    steps = [s for p in pj for s in (p.get("log") or []) if isinstance(s, dict) and run and s.get("run") == run]
    return {"enabled": bool(pl.get("projects_enabled", True)), "active": len(live), "due": [
                {"id": p.get("id"), "name": p.get("name"), "stage": p.get("stage"), "next_step": short(p.get("next_step") or "", 300)}
                for p in due[:4]],
            "starts_sessions": bool(pl.get("projects_enabled", True)) and bool(due) and bool(room),
            "this_session": len(steps), "_next": min(nxt) if nxt else None,
            "won": sum(1 for p in pj if p.get("status") == "won"), "failed": sum(1 for p in pj if p.get("status") == "failed")}


# PROJECT DISCOVERY (28 Nov 2026). Joseph: "When all frontier questions are exhausted and existing projects are
# waiting, there is no guaranteed independent project-discovery assignment. Implement a bounded, evidence-based
# discovery assignment that remains eligible independently of existing project and lane cooldowns, within our
# usage reserve." A lens is one kind of evidence in which the next growth project is looked for. Its cadence is
# how often that evidence changes: reading the same evidence again sooner would repeat exhausted research.
# A lens with a marker is also due as soon as its evidence HAS changed: the search lens when ops/cloud.json holds
# a newer Search Console read than the one it examined (EVIDENCE is filled once in main).
PD_RESULT_MIN, PD_LOG_KEEP, PD_CADENCE_H = 300, 60, 168
EVIDENCE = {}
PD_HOW = (
    "PROJECT DISCOVERY: one assignment per session, worked deeply. Its result is a growth project, or a documented "
    "reason why this evidence holds none today. (1) python3 ops/loopctl.py start discover:<lens id>. (2) Read the "
    "lens's evidence yourself, today. First read planner/projects (live, won and failed, with their logs), "
    "project_discovery.recent and the frontier answers on the same subject, and build on them: never repeat what "
    "they established. (3) Develop two or three candidate opportunities. For each: whom it reaches (Evanston and "
    "North Shore families at or near a senior-living decision) and roughly how many; the dated evidence; what can "
    "be executed inside ROLE AND LIMITS; which results wait for Joseph's merge and which do not; the effort; how "
    "success would be measured. (4) Choose at most one: the strongest evidence of qualified local reach and, "
    "between equals, the one whose first results do not wait for his merge. (5) If one qualifies, write the project "
    "file (name, goal, metric, why = the dated evidence, plan with its stages, next_step, kill_when) and record it: "
    "project-discover <lens id> --from FILE --result \"<sources read with dates; the candidates; why this one>\". "
    "Then develop it in this same session: start project:<id> before each step, project-step after it; a new "
    "project waits only for a named event outside your control. If none qualifies: project-discover <lens id> "
    "--result \"<sources read with dates; each candidate and why it failed>\". That is a complete result: never "
    "stretch a weak finding into a project. Legitimate waits stay as they are: a measurement that needs time, a "
    "decision that is Joseph's, a source you cannot read.")
PD_LENSES = (
    {"id": "objectives", "cadence_hours": 168, "name": "Objectives of the quarter without a project",
     "evidence": "strategy (north_star, baseline, the current quarter's objectives and the programs) against "
                 "planner/projects and the measured scoreboard in ops/cloud.json (daily rows, totals, search_console).",
     "question": "Which objective of the current quarter has no live project behind it and no measured movement? "
                 "What is the strongest project that would move it within this quarter?"},
    {"id": "intermediaries", "cadence_hours": 168, "name": "Who already meets these families",
     "evidence": "opportunity_map (items with their verdicts, channel_yield), ops/growth.json (prepared, shipped, "
                 "answered), ops/state.json (the operator's results, read only), the frontier answers on hospitals, "
                 "professionals, employers and congregations, and the public pages of every institution you consider.",
     "question": "Which class of intermediary that meets Evanston and North Shore families at the decision point "
                 "shows evidence of reach and has a published route that has not been developed into a project? Has "
                 "the event that reopens a watch verdict happened? A class with eight or more shipped actions and "
                 "no response stays closed."},
    {"id": "search-demand", "cadence_hours": 168, "marker": "search_console_read",
     "name": "Search demand the site already touches",
     "evidence": "The newest Search Console read in ops/cloud.json (scoreboard.search_console_queries and "
                 "search_console_pages; Make reads weekly) and, for the two or three clusters you consider, today's "
                 "first results page, read by you.",
     "question": "Which cluster of queries or which page that no live project covers has real impressions and a "
                 "reachable gain (a page ranking 8 to 40, or a page inside the top 10 without clicks)? A cluster "
                 "that names Evanston or a North Shore town outweighs a national one of the same size."},
    {"id": "local-intent", "cadence_hours": 336, "name": "What families near Evanston search and find",
     "evidence": "For Evanston, Skokie, Wilmette, Winnetka, Glenview and Northbrook: today's first results page and "
                 "its related questions for the decisions the guide covers (cost, how to choose, paying, Medicaid and "
                 "supportive living, memory care, respite, moving a parent), read by you; the public pages of the "
                 "city, township and county agencies those results send families to.",
     "question": "Which local question has no independent, sourced answer in those results that this guide could "
                 "give inside its rules (never ranking or recommending communities, no Westminster Place prices)? "
                 "Which one would bring the most families who could actually tour?"},
    {"id": "visitors", "cadence_hours": 168, "name": "Who actually came",
     "evidence": "ops/cloud.json scoreboard.daily and metrics (sources, ref tags, landing pages, checklist opens, "
                 "assessment starts, tour-form views) since this lens was last examined, and the Netlify "
                 "observability tool for the last 24 hours.",
     "question": "Which source or page already brings genuine local visitors and deserves a project that multiplies "
                 "it? Which page receives visitors and offers them no next step toward the tour path? A conversion "
                 "change waits until 30 genuine visitors have reached the step; measuring it does not."},
    {"id": "calendar", "cadence_hours": 336, "name": "Dated moments in the next 75 days",
     "evidence": "strategy/calendar and the official pages that set dates in the next 75 days (enrollment periods, "
                 "benefit and rule changes on 1 January, tax season, winter and holiday patterns), read by you today.",
     "question": "Which dated moment will send local families looking for help, has no asset or outreach plan of "
                 "ours yet, and leaves enough time to build, review and hand it to the operator or the package?"},
    {"id": "assets", "cadence_hours": 336, "name": "What is already built",
     "evidence": "The live guides and those waiting in the package (build-guides.py on main and on the package "
                 "branch), the checklist PDF and the research reports on drafts (research/), each with its measured "
                 "search and visitor numbers.",
     "question": "Which existing asset could reach families through a new format or route without new research (a "
                 "printable, a one-page summary an intermediary can hand out, a bundle of guides for one decision), "
                 "and who would distribute it? Which pages inside Google's top 10 get no clicks because of their "
                 "title or description?"},
    {"id": "benchmarks", "cadence_hours": 672, "name": "What works for those who win these searches and referrals",
     "evidence": "Five sites that win the local searches or referrals this guide wants (national directories, local "
                 "agencies, hospital and city resource pages), read by you today: what they offer a family at the "
                 "decision point, how they are found and who links to them.",
     "question": "What do they do that works and that this guide can do inside its rules and without paid placement? "
                 "Name the one practice with the best evidence and the first test of it."},
)


def pd_lenses(pdc):
    custom = [dict(l) for l in (pdc.get("lenses") or []) if isinstance(l, dict) and l.get("id")] if isinstance(pdc, dict) else []
    return custom or [dict(l) for l in PD_LENSES]


def project_discovery_view(d, now, run=None, room=True, projects_due=False, frontier_waits=False):
    """The guaranteed discovery assignment. It is eligible (starts_sessions) while some lens is due, no project
    step is due (development comes before discovery), no frontier question is open and the usage reserve has
    room. It does not look at lanes, lane cooldowns, owner limits or the waits of existing projects.
    BOUNDS: one lens per cadence (the evidence has to have had time to change); one assignment per session
    (due is false for the run that recorded one, so that it develops what it found; the next session takes
    the next lens at once). A failed project reopens the lens examined longest ago for its replacement.
    Read only."""
    pl = d.get("planner") or {}
    pdc = pl.get("project_discovery") if isinstance(pl.get("project_discovery"), dict) else {}
    enabled = bool(pl.get("enabled", True)) and bool(pl.get("projects_enabled", True)) and bool(pdc.get("enabled", True))
    state = pdc.get("state") if isinstance(pdc.get("state"), dict) else {}
    log = [e for e in (pdc.get("log") or []) if isinstance(e, dict)]
    due_l, later, seen = [], [], []
    for l in pd_lenses(pdc):
        s = state.get(l["id"]) if isinstance(state.get(l["id"]), dict) else {}
        last = parse_ts(s.get("last_utc"))
        cad = l.get("cadence_hours")
        cad = cad if isinstance(cad, (int, float)) and not isinstance(cad, bool) and cad > 0 else PD_CADENCE_H
        mark = EVIDENCE.get(l.get("marker")) if l.get("marker") else None
        if last is None or last + dt.timedelta(hours=cad) <= now or (mark and s.get("marker") and mark != s.get("marker")):
            due_l.append(l)
        else:
            later.append((last + dt.timedelta(hours=cad), l["id"]))
            seen.append((last, l))
    rf = pdc.get("replace_failed") if isinstance(pdc.get("replace_failed"), dict) else None
    if rf and not due_l and seen:
        oldest = min(seen, key=lambda x: x[0])[1]
        due_l.append(oldest)
        later = [x for x in later if x[1] != oldest["id"]]
    mine = [e for e in log if run and e.get("run") == run]
    wanted = enabled and bool(due_l)
    why_not = None
    if wanted:
        if projects_due:
            why_not = "a project step is due: develop what exists before looking for more"
        elif frontier_waits:
            why_not = "open frontier questions come first"
        elif not room:
            why_not = "the usage reserve is in its last quarter (kept for monitoring, the daily package and ready tasks)"
    starts = wanted and why_not is None
    first = due_l[0] if due_l else None
    for_me = starts and not mine
    return {"enabled": enabled, "due": for_me, "starts_sessions": starts, "waiting_for": why_not,
            "this_session": len(mine),
            "lens": ({"id": first["id"], "name": first.get("name"), "evidence": first.get("evidence"),
                      "question": first.get("question")} if (for_me and first) else None),
            "how": PD_HOW if for_me else None,
            "lenses_due": [l["id"] for l in due_l],
            "replaces_failed": (rf or {}).get("project") if rf else None,
            "recent": [{"utc": e.get("utc"), "lens": e.get("lens"), "project": e.get("project"),
                        "result": short(e.get("result") or "", 240 if not for_me else 700)} for e in log[:3]],
            "_later": later}


def eligible_work(st):
    """What a new session would find to do, in the order it is taken: for the session record and the report."""
    w = []
    if st["package"]["due"]:
        w.append("daily package cut")
    if st.get("ready"):
        w.append("ready tasks: " + ", ".join(str(t.get("id")) for t in st["ready"][:6]))
    if st.get("recheck_due"):
        w.append("rechecks: " + ", ".join(str(t.get("id")) for t in st["recheck_due"][:6]))
    if st.get("open_items"):
        w.append("open map items: %d" % len(st["open_items"]))
    if st.get("scouts_due"):
        w.append("scouts: " + ", ".join(str(s.get("id")) for s in st["scouts_due"][:4]))
    if st["projects"]["starts_sessions"]:
        w.append("project steps: " + ", ".join(str(p.get("id")) for p in st["projects"]["due"]))
    if st["frontier"].get("starts_sessions"):
        w.append("frontier questions: %s" % st["frontier"]["open"])
    if st["project_discovery"]["starts_sessions"]:
        w.append("project discovery: lens " + ", ".join(st["project_discovery"]["lenses_due"][:8]))
    if st["plan"]["due"]:
        w.append("planning: " + ", ".join(str(x) for x in (st["plan"].get("plannable") or [])[:4]))
    if st["sweep"]["due"]:
        w.append("sweep angles: " + ", ".join(str(x.get("id")) for x in st["sweep"]["due"][:6]))
    if st["fallback"]["due"]:
        w.append("backlog discovery")
    if st["monitor"]["due"]:
        w.append("monitoring pass")
    return w


def strategy_view(d, now):
    """The 12-month plan (strategy). Its monthly review is due from reviews/first_due_utc on, in every month
    that has no task keyed strategy-review:YYYYMM in the queue or among the completed tasks. Read only."""
    s = d.get("strategy") if isinstance(d.get("strategy"), dict) else {}
    enabled = bool(s.get("enabled"))
    key = "strategy-review:" + now.strftime("%Y%m")
    want = norm_key(key)

    def has(pool):
        return any(isinstance(t, dict) and norm_key(t.get("key") or "") == want for t in (d.get(pool) or []))

    first = parse_ts((s.get("reviews") or {}).get("first_due_utc")) if isinstance(s.get("reviews"), dict) else None
    queued = has("queue")
    return {"enabled": enabled, "review_due": enabled and (first is None or now >= first) and not queued and not has("completed"),
            "review_key": key, "review_queued": queued}


def package_view(d, now):
    """The daily approval package (procedure step 7, DAILY PACKAGE). One cut per UTC date, inside a window that
    ends before Joseph's morning report, recorded as a task keyed package:YYYYMMDD. Due while the window is
    open and no such task is finished. Outside the window nothing is cut: the package stays as the report
    showed it. Read only. (25 Nov 2026: the first unattended session after the rule was written closed
    without cutting, because nothing in the status asked for it.)"""
    pl = d.get("planner") or {}
    pk = pl.get("package") if isinstance(pl.get("package"), dict) else {}
    enabled = bool(pk.get("enabled")) and bool(pl.get("enabled", True))

    def hm(v, default):
        try:
            h, m = str(v).split(":")
            h, m = int(h), int(m)
            if 0 <= h < 24 and 0 <= m < 60:
                return h, m
        except (ValueError, AttributeError):
            pass
        return default

    win = pk.get("window_utc")
    win = win if isinstance(win, list) and len(win) == 2 else list(PKG_WINDOW)
    h0, m0 = hm(win[0], (5, 0))
    h1, m1 = hm(win[1], (10, 30))
    day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start = day + dt.timedelta(hours=h0, minutes=m0)
    end = day + dt.timedelta(hours=h1, minutes=m1)
    if end <= start:
        start, end = day + dt.timedelta(hours=5), day + dt.timedelta(hours=10, minutes=30)
    key = "package:" + now.strftime("%Y%m%d")
    want = norm_key(key)
    settled = [t for t in (d.get("completed") or []) if isinstance(t, dict) and norm_key(t.get("key") or "") == want]
    queued = [t for t in (d.get("queue") or []) if isinstance(t, dict) and norm_key(t.get("key") or "") == want]
    in_window = start <= now <= end
    due = enabled and in_window and not settled
    stale = [t.get("id") for t in (d.get("queue") or []) if isinstance(t, dict)
             and re.match(r"^package-\d{8}$", norm_key(t.get("key") or ""))
             and (norm_key(t.get("key") or "") != want or now > end)]
    if not enabled:
        nxt = None
    elif now < start and not settled:
        nxt = start
    else:
        nxt = start + dt.timedelta(days=1)
    # A SECOND CUT (27 Nov 2026: the session that cut at 06:29Z then finished a holiday guide, a verified
    # Medicare section for a 7 Dec deadline and a verified correction, and left all three for the next day's
    # package although the window was open). Work that belongs in the package and was finished after the
    # recorded cut makes a second cut due until controller/package/cut_utc is newer than that work.
    recut_for = []
    cpk = (d.get("controller") or {}).get("package")
    cut = parse_ts(cpk.get("cut_utc")) if isinstance(cpk, dict) else None
    if enabled and in_window and settled and cut is not None:
        for t in (d.get("completed") or []):
            if not isinstance(t, dict):
                continue
            done = parse_ts(t.get("done_utc"))
            if done is None or done <= cut:
                continue
            k = norm_key(t.get("key") or "")
            dl = t.get("deliverable") if isinstance(t.get("deliverable"), dict) else {}
            if k.startswith("package-") or t.get("status") == "dropped":
                continue
            if dl.get("type") in ("publish_pr", "pr") or k.startswith("verify-live-"):
                recut_for.append(t.get("id"))
    return {"enabled": enabled, "due": due, "key": key, "task": queued[0].get("id") if queued else None,
            "done_today": bool(settled), "ahead_today": bool(enabled and not settled and now < start),
            "recut_due": bool(recut_for), "recut_for": recut_for[:12],
            "window_utc": ["%02d:%02d" % (h0, m0), "%02d:%02d" % (h1, m1)],
            "stale_tasks": stale, "next_due_utc": fmt(nxt) if nxt else None, "_next": nxt}


ADDENDA_MAX, ADDENDA_CHARS = 8, 900


def addenda_view(d, now):
    """Dated rules of the supervising session (controller/addenda): each {"utc", "by": "supervisor", "rule"} and
    optionally "until_utc" or "retired": true. The procedure tells the worker to follow them like its own
    sentences; they can add to or tighten it and never widen ROLE AND LIMITS. Read only."""
    rows = (d.get("controller") or {}).get("addenda")
    out_rows = []
    for e in (rows if isinstance(rows, list) else []):
        if not isinstance(e, dict) or e.get("retired") or not e.get("rule"):
            continue
        until = parse_ts(e.get("until_utc"))
        if until is not None and until <= now:
            continue
        out_rows.append({"utc": e.get("utc"), "rule": str(e.get("rule"))[:ADDENDA_CHARS]})
    return out_rows[-ADDENDA_MAX:]


def end_current(c, what, now, deliverable=None):
    """Close the item marked by start: add its minutes to the session's productive time."""
    lk = c.get("lock") or {}
    cur = lk.get("current") or {}
    minutes = None
    if cur.get("what") == what:
        t0 = parse_ts(cur.get("since_utc"))
        if t0 is not None:
            minutes = max(0, int(round((now - t0).total_seconds() / 60)))
        lk["productive_min"] = int(lk.get("productive_min") or 0) + (minutes or 0)
        lk.pop("current", None)
    if deliverable:
        lk.setdefault("deliverables", []).append(short(str(deliverable), 120))
    return minutes


def compute(d, now, monitor_hours, run=None, _probe=False, closing=None):
    c = d.get("controller") or {}
    lock = c.get("lock") or {}
    lock_t = parse_ts(lock.get("utc"))
    lock_age = None if not lock_t else int((now - lock_t).total_seconds() // 60)
    lock_live = bool(lock.get("holder")) and lock_age is not None and lock_age < LOCK_STALE_MIN

    g = grace(d)
    soon = now + g
    queue = d.get("queue") or []
    ready, recheck, events, future = [], [], [], []
    for t in queue:
        st = t.get("status")
        if st == READY:
            ready.append(t)
        elif st == WAIT_DATA:
            when = task_date(t)
            if when is None:
                events.append(t)
            elif when <= soon:
                recheck.append(t)
            else:
                future.append((when, t.get("id")))
        elif st == WAIT_OWNER:
            events.append(t)
    ready.sort(key=lambda t: (t.get("priority", 99), str(t.get("id"))))

    live = [t for t in queue if t.get("status") in (READY, WAIT_DATA)]
    queued_items = {t.get("map_item") for t in live if t.get("map_item")}
    queued_scouts = {t.get("scout") for t in live if t.get("scout")}

    om = d.get("opportunity_map") or {}
    lanes = om.get("lane_order") or []
    open_items = [i for i in (om.get("items") or []) if i.get("status") == "open" and i.get("id") not in queued_items]
    open_items.sort(key=lambda i: (lanes.index(i["lane"]) if i.get("lane") in lanes else 99, str(i.get("id"))))

    scouts_due = []
    for s in ((om.get("discovery") or {}).get("scouts") or []):
        when = parse_ts(s.get("next_due_utc"))
        if when is None:
            continue
        if when <= soon:
            if s.get("id") not in queued_scouts:
                scouts_due.append(s)
        else:
            future.append((when, s.get("id")))
    scouts_due.sort(key=lambda s: s.get("next_due_utc") or "")

    mon_t = parse_ts((c.get("monitor") or {}).get("last_utc"))
    mon_age = None if not mon_t else round((now - mon_t).total_seconds() / 3600, 1)
    mon_due = mon_t is None or (soon - mon_t) >= dt.timedelta(hours=monitor_hours)
    if mon_t is not None and not mon_due:
        future.append((mon_t + dt.timedelta(hours=monitor_hours), "monitor"))

    # Tasks that the asking session may not work (not_run names it: the review of a page it built, the check
    # of a correction it applied) are work for the NEXT session. They keep the chain going (eligible) but do
    # not fill this session's pipeline: with only those left, this session still plans and looks for new work
    # instead of closing early. (25 Nov 2026: a session closed after 26 minutes with four hand-offs waiting.)
    handoff = [t for t in ready if run and run in (t.get("not_run") or [])]
    pipeline = len(ready) - len(handoff) + len(recheck) + len(open_items) + len(scouts_due)
    plan = plan_view(d, soon, pipeline)
    if plan["_wake"] is not None:
        future.append((plan["_wake"], "planner cooldown ends"))
    plan.pop("_wake", None)
    sweep = sweep_view(d, soon, plan["lanes"])
    future.extend(sweep.pop("_later"))
    # closing = (start, end) of the session that is closing now: its time counts against the reserve at once,
    # so that a chain is not continued into a reserve that this very session has used up.
    bud_now = budget_view(d, now, *(closing or ()))
    room = discovery_room(bud_now)
    fbv = fallback_view(d, now, soon, pipeline, plan, room)
    frv = frontier_view(d, now, run, room)
    pjv = projects_view(d, now, run, room)
    pdv = project_discovery_view(d, now, run, room, bool(pjv["due"]), bool(frv["starts_sessions"]))
    for when_, lens_id in pdv.pop("_later"):
        future.append((when_, "project discovery: lens " + lens_id))
    if not room and (fbv["wanted"] or frv["more"] or pjv["due"] or pdv["lenses_due"]):
        free = room_free_at(d, now, *(closing or ()))
        if free is not None and free > now:
            future.append((free, "usage reserve has room for discovery again"))
    if pjv["_next"] is not None:
        future.append((pjv["_next"], "project step"))
    pjv.pop("_next", None)
    if frv["_slot"] is not None:
        future.append((frv["_slot"], "frontier: next question"))
    frv.pop("_slot", None)
    if fbv["_until"] is not None:
        future.append((fbv["_until"], "backlog discovery"))
    fbv.pop("_until", None)
    pkv = package_view(d, now)
    if pkv["_next"] is not None:
        future.append((pkv["_next"], "daily package cut"))
    pkv.pop("_next", None)

    future.sort(key=lambda x: x[0])
    next_due = future[0][0] if future else None
    eligible = (pipeline + len(handoff) + (1 if plan["due"] else 0) + len(sweep["due"]) + (1 if fbv["due"] else 0)
                + (1 if pkv["due"] else 0) + (1 if frv["starts_sessions"] else 0) + len(pjv["due"] if pjv["starts_sessions"] else [])
                + (1 if pdv["starts_sessions"] else 0))
    # The wake time is the first moment at which a session would really find work. Since 27 Nov 2026 Make's
    # timer looks every 15 minutes (Core plan), so a wake set one grace before something that has no grace
    # (the package window) would start a session that finds nothing due. Candidates: every due time and
    # every due time minus the grace; the first at which work_now holds wins.
    wake_m = wake_minutes(fmt(next_due - g) if next_due else None, now)
    wake_t = (next_due - g) if next_due else None
    if not _probe and future:
        for w in sorted({x - g for x, _ in future} | {x for x, _ in future}):
            if w <= now:
                continue
            if compute(d, w, monitor_hours, run, _probe=True, closing=closing)["work_now"]:
                wake_m, wake_t = wake_minutes(fmt(w), now), w
                break

    def ready_row(t):
        row = {"id": t.get("id"), "priority": t.get("priority"), "workstream": t.get("workstream"),
               "map_item": t.get("map_item"), "scout": t.get("scout"), "title": title_of(t)}
        if t.get("not_run"):
            row["not_run"] = t.get("not_run")
        return row

    return {
        "now": fmt(now),
        "lock": {"holder": lock.get("holder", ""), "utc": lock.get("utc", ""), "age_min": lock_age, "live": lock_live},
        "ready": [ready_row(t) for t in ready],
        "recheck_due": [{"id": t.get("id"), "not_before_utc": fmt(task_date(t)), "title": title_of(t)} for t in recheck],
        "open_items": [{"id": i.get("id"), "lane": i.get("lane"), "class": short(i.get("class", ""), 80)} for i in open_items],
        "scouts_due": [{"id": s.get("id"), "name": s.get("name"), "next_due_utc": s.get("next_due_utc")} for s in scouts_due],
        "event_waits": [{"id": t.get("id"), "status": t.get("status"),
                         "waiting_for": short(next((t[k] for k in WAIT_KEYS if t.get(k)), ""), 150)} for t in events],
        "monitor": {"last_utc": (c.get("monitor") or {}).get("last_utc", ""), "age_hours": mon_age, "due": mon_due},
        "plan": {k: plan[k] for k in ("due", "pipeline", "low_water", "plannable", "saturated")},
        "handoff_waiting": len(handoff),
        "sweep": sweep,
        "fallback": fbv,
        "projects": pjv,
        "project_discovery": pdv,
        "frontier": frv,
        "strategy": strategy_view(d, now),
        "package": pkv,
        "addenda": addenda_view(d, now),
        "budget": bud_now,
        "eligible": eligible,
        "work_now": eligible > 0 or mon_due,
        "grace_minutes": int(g.total_seconds() // 60),
        "next_due_utc": fmt(next_due) if next_due else None,
        "wake_minutes": wake_m,
        "wake_utc": fmt(wake_t) if wake_t else None,
        "next_due": [{"utc": fmt(w), "what": i} for w, i in future[:6]],
        "counts": {"queue": len(queue), "completed": len(d.get("completed") or []),
                   "map_items": len(om.get("items") or []), "owner_review_needed": len(d.get("owner_review_needed") or [])},
    }


def chicago_date(t):
    try:
        from zoneinfo import ZoneInfo
        return t.astimezone(ZoneInfo("America/Chicago")).date()
    except Exception:
        return (t - dt.timedelta(hours=6)).date()


def num(v):
    return v if isinstance(v, (int, float)) and not isinstance(v, bool) else None


def outcomes_view(cloud, now, days):
    """Outcome counts from cloud.json's scoreboard: the last DAYS Chicago dates and the DAYS before them."""
    sb = cloud.get("scoreboard") or {}
    rows = {r.get("date_chicago"): r for r in (sb.get("daily") or []) if isinstance(r, dict)}
    today = chicago_date(now)
    fields = ("genuine_visitors", "tour_form_views", "checklist_opens", "assessment_starts", "tour_requests")

    def window(end_offset):
        dates = [(today - dt.timedelta(days=end_offset + i)).isoformat() for i in range(days)]
        tot = {f: 0 for f in fields}
        src = {}
        unknown = {f: 0 for f in fields}
        have = 0
        for day in dates:
            r = rows.get(day)
            if not r:
                continue
            have += 1
            for f in fields:
                v = num(r.get(f))
                if v is None:
                    unknown[f] += 1
                else:
                    tot[f] += v
            for k, v in (r.get("by_source") or {}).items():
                if num(v) is not None:
                    src[k] = src.get(k, 0) + v
        return {"from": dates[-1], "to": dates[0], "days_with_rows": have, "qualified_visitors": tot["genuine_visitors"],
                "by_source": src, "tour_form_views": tot["tour_form_views"], "checklist_opens": tot["checklist_opens"],
                "assessment_starts": tot["assessment_starts"], "inquiries": tot["tour_requests"],
                "unreadable_days": {f: n for f, n in unknown.items() if n}}

    cur, prev = window(0), window(days)
    totals = sb.get("totals") or {}
    sc = sb.get("search_console") or []
    src = cur["by_source"]
    return {"window": cur, "previous": prev,
            "referrals": {"org_replies": totals.get("org_replies"), "placements_live": totals.get("placements_live"),
                          "referral_emails_sent": totals.get("referral_emails_sent")},
            "tours_confirmed": totals.get("tours_confirmed"),
            "search_console_latest": sc[0] if sc else None,
            "lane_visitors": {"distribution": src.get("facebook", 0), "partnerships": src.get("referral", 0),
                              "search": src.get("search", 0), "other": src.get("other", 0)},
            "note": "Counts come only from the monitor's scoreboard rows; a date without a row is unmeasured, not zero."}


def budget_view(d, now, extra_start=None, extra_end=None):
    """Worker session time against the usage reserve in planner: budget_hours_per_day (rolling 24 hours)
    and budget_hours_per_week (rolling 7 days); a missing or zero value means no limit for that window.
    extra_start: start time of the session that is closing now, counted up to extra_end (default: now)."""
    pl = d.get("planner") or {}
    spans_all = session_spans(d, now, extra_start, extra_end)
    res = {"over": False, "resume_utc": None, "wake_minutes": None}
    resume = None
    for key, days in (("budget_hours_per_day", 1), ("budget_hours_per_week", 7)):
        limit = pl.get(key)
        limit = limit if isinstance(limit, (int, float)) and not isinstance(limit, bool) and limit > 0 else None
        since = now - dt.timedelta(days=days)
        spans = [(max(a, since), b) for a, b in spans_all if b > since]
        used = sum((b - a).total_seconds() for a, b in spans) / 3600
        tag = "day" if days == 1 else "week"
        res["limit_hours_per_" + tag] = limit
        res["used_hours_" + ("24h" if days == 1 else "7d")] = round(used, 1)
        res["used_minutes_" + ("24h" if days == 1 else "7d")] = round(used * 60, 1)
        if limit is not None and used >= limit:
            res["over"] = True
            need = (used - limit) * 3600
            wake = None
            for a, b in sorted(spans):
                dur = (b - a).total_seconds()
                if dur >= need:
                    wake = a + dt.timedelta(days=days, seconds=need + 60)
                    break
                need -= dur
            wake = max(wake or now + dt.timedelta(hours=12), now + dt.timedelta(minutes=60))
            resume = wake if resume is None else max(resume, wake)
    if resume:
        res["resume_utc"] = fmt(resume)
        res["wake_minutes"] = wake_minutes(fmt(resume), now)
    return res


def norm_key(s):
    return re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-")


def wake_minutes(next_due_utc, now):
    t = parse_ts(next_due_utc)
    if t is None:
        return WAKE_DEFAULT
    return max(WAKE_MIN, min(WAKE_MAX, math.ceil((t - now).total_seconds() / 60)))


def all_ids(d):
    ids = []
    for key in ("queue", "completed", "blocked"):
        ids += [str(t.get("id")) for t in (d.get(key) or []) if isinstance(t, dict)]
    return ids


def next_id(d):
    nums = [int(m.group(1)) for i in all_ids(d) for m in [re.match(r"^ACQ-(\d+)$", i)] if m]
    return "ACQ-%03d" % ((max(nums) if nums else 0) + 1)


STEP = re.compile(r"^([^\[\]]+)?(?:\[([^\]=]+)(?:=([^\]]*))?\])?$")


def walk(root, path):
    """Return (parent, key) for PATH such as opportunity_map/items[id=D13]/status."""
    parent, key, node = None, None, root
    steps = [p for p in path.split("/") if p]
    for n, step in enumerate(steps):
        m = STEP.match(step)
        if not m:
            fail("bad path step: " + step)
        name, sel, val = m.groups()
        if name is not None:
            if not isinstance(node, dict):
                fail("not an object at: " + step)
            if name not in node and sel is None and n < len(steps) - 1:
                node[name] = {}
            parent, key = node, name
            node = node.get(name)
        if sel is not None:
            if not isinstance(node, list):
                fail("not a list at: " + step)
            if val is None:
                idx = int(sel)
            else:
                hits = [n for n, e in enumerate(node) if isinstance(e, dict) and str(e.get(sel)) == val]
                if len(hits) != 1:
                    fail("%d matches for %s" % (len(hits), step))
                idx = hits[0]
            parent, key = node, idx
            node = node[idx]
    if parent is None:
        fail("empty path")
    return parent, key


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("cmd")
    p.add_argument("args", nargs="*")
    p.add_argument("--loop", default="ops/esc-tour-loop.json")
    p.add_argument("--file")
    p.add_argument("--from", dest="src")
    p.add_argument("--now")
    p.add_argument("--monitor-hours", type=float, default=12)
    p.add_argument("--status", default="done")
    p.add_argument("--done", type=int, default=0)
    p.add_argument("--changed", type=int, default=0)
    p.add_argument("--outcome", default="")
    p.add_argument("--launch", default="")
    p.add_argument("--tasks", default="")
    p.add_argument("--front", action="store_true")
    p.add_argument("--keep", type=int)
    p.add_argument("--added", type=int, default=0)
    p.add_argument("--result", default="")
    p.add_argument("--cooldown-hours", type=float)
    p.add_argument("--days", type=int, default=7)
    p.add_argument("--record", action="store_true")
    p.add_argument("--cloud", default="ops/cloud.json")
    p.add_argument("--allow-repeat", action="store_true")
    p.add_argument("--recheck-hours", type=float)
    p.add_argument("--stop-reason", default="")
    p.add_argument("--considered", default="")
    p.add_argument("--resume-when", default="")
    p.add_argument("--run", default="")
    p.add_argument("--avenue", default="")
    p.add_argument("--lane", default="")
    p.add_argument("--candidates", type=int, default=0)
    p.add_argument("--new-evidence", default="")
    p.add_argument("--verdict", default="")
    p.add_argument("--fallback-skipped", default="")
    p.add_argument("--package-skipped", default="")
    a = p.parse_args()

    now = parse_ts(a.now) if a.now else dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    if now is None:
        fail("bad --now")
    target = a.file or a.loop
    d = load(target)
    try:
        with open(a.cloud, encoding="utf-8") as fh:
            rows_ = ((json.load(fh).get("scoreboard") or {}).get("search_console") or [])
        reads_ = sorted(str(r.get("read_utc")) for r in rows_ if isinstance(r, dict) and r.get("read_utc"))
        EVIDENCE["search_console_read"] = reads_[-1] if reads_ else None
    except Exception:
        pass
    cmd, args = a.cmd, a.args

    if cmd == "status":
        st = compute(d, now, a.monitor_hours, a.run or None)
        if a.run:
            st["ready_next_session"] = [r for r in st["ready"] if a.run in (r.get("not_run") or [])]
            st["ready"] = [r for r in st["ready"] if a.run not in (r.get("not_run") or [])]
        out(st)

    if cmd == "plan":
        st = compute(d, now, a.monitor_hours)
        pv = plan_view(d, now + grace(d), st["plan"]["pipeline"])
        pv.pop("_wake", None)
        pl = d.get("planner") or {}
        pv["min_score"] = float(pl.get("min_score", PLAN_MIN_SCORE))
        pv["recent_plans"] = (pl.get("log") or [])[:6]
        out(pv)

    if cmd == "outcomes":
        try:
            cloud = load(a.cloud)
        except (OSError, ValueError) as e:
            fail("cannot read %s: %s" % (a.cloud, e))
        view = outcomes_view(cloud, now, max(1, a.days))
        if a.record:
            pl = d.setdefault("planner", {})
            rows = pl.setdefault("outcomes", [])
            w = view["window"]
            row = {"to": w["to"], "days": a.days, "days_with_rows": w["days_with_rows"],
                   "qualified_visitors": w["qualified_visitors"], "by_source": w["by_source"],
                   "inquiries": w["inquiries"], "tour_form_views": w["tour_form_views"],
                   "org_replies_total": view["referrals"]["org_replies"],
                   "placements_live_total": view["referrals"]["placements_live"],
                   "tours_confirmed": view["tours_confirmed"], "recorded_utc": fmt(now)}
            rows[:] = [r for r in rows if not (r.get("to") == w["to"] and r.get("days") == a.days)]
            rows.insert(0, row)
            del rows[26:]
            save(target, d)
            view["recorded"] = True
        out(view)

    if cmd == "plan-done":
        if not args:
            fail("usage: plan-done LANE --added N --result TEXT [--cooldown-hours H]")
        pl = d.get("planner")
        if not isinstance(pl, dict):
            fail("no planner block in " + target)
        hits = [ln for ln in pl.get("lanes") or [] if ln.get("id") == args[0]]
        if len(hits) != 1:
            fail("unknown lane: " + args[0])
        ln = hits[0]
        ln["last_planned_utc"] = fmt(now)
        ln["last_plan_result"] = short(a.result or "(no result given)", 300)
        if a.added <= 0:
            hours = a.cooldown_hours if a.cooldown_hours is not None else float(ln.get("plan_cooldown_hours", PLAN_COOLDOWN_H))
            ln["cooldown_until_utc"] = fmt(now + dt.timedelta(hours=max(1.0, hours)))
        else:
            ln["cooldown_until_utc"] = ""
        log = pl.setdefault("log", [])
        log.insert(0, "%s %s +%d: %s" % (fmt(now), args[0], max(0, a.added), short(a.result or "", 160)))
        del log[40:]
        save(target, d)
        out({"lane": args[0], "added": a.added, "cooldown_until_utc": ln["cooldown_until_utc"] or None})

    if cmd == "show":
        want = args[0]
        om = d.get("opportunity_map") or {}
        pools = [("queue", d.get("queue")), ("completed", d.get("completed")), ("blocked", d.get("blocked")),
                 ("map_item", om.get("items")), ("scout", (om.get("discovery") or {}).get("scouts")),
                 ("channel_yield", om.get("channel_yield"))]
        found = [{"where": w, "value": e} for w, pool in pools for e in (pool or [])
                 if isinstance(e, dict) and str(e.get("id", e.get("class"))) == want]
        out(found if found else {"error": "not found: " + want}, 0 if found else 2)

    if cmd == "dupes":
        om = d.get("opportunity_map") or {}
        for key in ("queue", "completed", "blocked"):
            for t in d.get(key) or []:
                print("%s %s [%s] %s%s" % (key, t.get("id"), t.get("status"),
                                           ("(%s) " % (t.get("map_item") or t.get("scout"))) if (t.get("map_item") or t.get("scout")) else "",
                                           title_of(t)))
        for i in om.get("items") or []:
            print("map %s [%s] %s | %s" % (i.get("id"), i.get("status"), short(i.get("class", ""), 70), short(i.get("note", ""), 90)))
        sys.exit(0)

    if cmd == "validate":
        problems = []
        ids = all_ids(d)
        problems += ["duplicate task id " + i for i in sorted({i for i in ids if ids.count(i) > 1})]
        for key in ("queue", "completed", "owner_review_needed", "opportunity_map"):
            if key not in d:
                problems.append("missing " + key)
        om = d.get("opportunity_map") or {}
        item_ids = [i.get("id") for i in om.get("items") or []]
        problems += ["duplicate map item " + str(i) for i in sorted({i for i in item_ids if item_ids.count(i) > 1})]
        scouts = (om.get("discovery") or {}).get("scouts") or []
        for s in scouts:
            if parse_ts(s.get("next_due_utc")) is None:
                problems.append("scout %s has no readable next_due_utc" % s.get("id"))
        for t in d.get("queue") or []:
            if t.get("status") == "done":
                problems.append("task %s is done but still in the queue" % t.get("id"))
            if t.get("map_item") and t["map_item"] not in item_ids:
                problems.append("task %s names unknown map item %s" % (t.get("id"), t["map_item"]))
        pl = d.get("planner")
        if pl is not None:
            lane_ids = [ln.get("id") for ln in (pl.get("lanes") or [])]
            problems += ["duplicate lane " + str(i) for i in sorted({i for i in lane_ids if lane_ids.count(i) > 1})]
            for ln in pl.get("lanes") or []:
                if not isinstance(ln.get("owner_wip_limit", 3), int):
                    problems.append("lane %s owner_wip_limit is not a whole number" % ln.get("id"))
                if ln.get("cooldown_until_utc") and parse_ts(ln["cooldown_until_utc"]) is None:
                    problems.append("lane %s has an unreadable cooldown_until_utc" % ln.get("id"))
            for t in d.get("queue") or []:
                if t.get("source") == "plan" and t.get("lane") not in lane_ids:
                    problems.append("task %s names unknown lane %s" % (t.get("id"), t.get("lane")))
            angle_ids = [x.get("id") for x in pl.get("angles") or []]
            problems += ["duplicate sweep angle " + str(i) for i in sorted({i for i in angle_ids if angle_ids.count(i) > 1})]
            for x in pl.get("angles") or []:
                if x.get("lane") not in lane_ids:
                    problems.append("sweep angle %s names unknown lane %s" % (x.get("id"), x.get("lane")))
                if x.get("next_check_utc") and parse_ts(x["next_check_utc"]) is None:
                    problems.append("sweep angle %s has an unreadable next_check_utc" % x.get("id"))
        warnings = []
        if pl is not None:
            fbk = pl.get("fallback")
            if fbk is not None:
                if not isinstance(fbk, dict):
                    problems.append("planner/fallback is not an object")
                else:
                    if fbk.get("exhausted_until_utc") and parse_ts(fbk["exhausted_until_utc"]) is None:
                        problems.append("planner/fallback/exhausted_until_utc is unreadable")
                    for e in fbk.get("log") or []:
                        if not isinstance(e, dict) or e.get("avenue") not in FB_AVENUES or parse_ts(e.get("utc")) is None:
                            problems.append("planner/fallback/log has a malformed entry: " + short(e, 60))
                            break
            frk = pl.get("frontier")
            if frk is not None:
                if not isinstance(frk, dict) or not isinstance(frk.get("questions", []), list):
                    problems.append("planner/frontier is not an object with a questions list")
                else:
                    seen = set()
                    for q in frk.get("questions") or []:
                        if not (isinstance(q, dict) and q.get("id") and q.get("question")
                                and q.get("status") in ("open", "explored", "dropped")):
                            problems.append("planner/frontier/questions has a malformed entry: " + short(q, 60))
                            break
                        if norm_key(q["id"]) in seen:
                            problems.append("planner/frontier/questions repeats the id " + str(q["id"]))
                            break
                        seen.add(norm_key(q["id"]))
            pdk = pl.get("project_discovery")
            if pdk is not None:
                if not isinstance(pdk, dict) or not isinstance(pdk.get("state", {}), dict) or not isinstance(pdk.get("log", []), list):
                    problems.append("planner/project_discovery is not an object with a state object and a log list")
                else:
                    ids = [norm_key(l.get("id")) for l in pd_lenses(pdk)]
                    if len(ids) != len(set(ids)):
                        problems.append("planner/project_discovery/lenses repeats an id")
                    for k, s_ in pdk.get("state", {}).items():
                        if not isinstance(s_, dict) or (s_.get("last_utc") and parse_ts(s_["last_utc"]) is None):
                            problems.append("planner/project_discovery/state/%s is malformed" % k)
                            break
        for t in d.get("queue") or []:
            if t.get("not_run") is not None and not (isinstance(t["not_run"], list) and all(isinstance(x, str) for x in t["not_run"])):
                problems.append("task %s: not_run must be a list of run ids" % t.get("id"))
        n_owner = len(d.get("owner_review_needed") or [])
        if n_owner > 8:
            warnings.append("owner_review_needed has %d lines; keep at most 8, one line per decision, most valuable first" % n_owner)
        out({"ok": not problems, "problems": problems, "warnings": warnings,
             "counts": compute(d, now, a.monitor_hours)["counts"], "scouts": len(scouts)}, 0 if not problems else 4)

    if cmd == "lock":
        run = args[0]
        c = controller(d)
        st = compute(d, now, a.monitor_hours)["lock"]
        if st["live"] and st["holder"] != run:
            out({"locked": True, "holder": st["holder"], "age_min": st["age_min"]}, 3)
        prev = c.get("lock") or {}
        if not prev.get("holder") and any(isinstance(s_, dict) and s_.get("run") == run and s_.get("end_utc")
                                          for s_ in (c.get("sessions") or [])[:10]):
            # this run has already closed: a heartbeat before its end commit must not take the lock again,
            # or the next session Make starts would find a live lock and stop with "Lock held"
            out({"locked": False, "holder": "", "closed": True,
                 "note": "this run already closed; the lock stays free"})
        took_over = None
        if st["holder"] and st["holder"] != run:
            took_over = st["holder"]
            c["sessions"].insert(0, {"run": st["holder"], "start_utc": prev.get("since_utc") or st["utc"], "end_utc": None,
                                     "outcome": "abandoned: no close recorded; lock taken over by " + run})
        if prev.get("holder") == run:
            # heartbeat: refresh the time other sessions see; keep the start and the session's tallies
            prev["since_utc"] = prev.get("since_utc") or prev.get("utc") or fmt(now)
            prev["utc"] = fmt(now)
            c["lock"] = prev
        else:
            c["lock"] = {"holder": run, "utc": fmt(now), "since_utc": fmt(now)}
        save(target, d)
        out({"locked": False, "holder": run, "took_over": took_over})

    if cmd in ("add", "update", "finish"):
        if not a.src:
            fail("--from FILE is required")
        patch = load(a.src)
        if not isinstance(patch, dict):
            fail("the file must hold one JSON object")
        queue = d.setdefault("queue", [])
        if cmd == "add":
            need = ("task", "workstream", "evidence", "expected_tour_acquisition_value", "executor", "done_when")
            missing = [k for k in need if not patch.get(k)]
            if missing:
                fail("task is missing: " + ", ".join(missing))
            lane = patch.get("lane") or WORKSTREAM_LANE.get(patch.get("workstream") or "")
            if lane:
                patch["lane"] = lane
            if patch.get("source") == "plan":
                missing = [k for k in ("lane", "key", "impact", "confidence", "effort") if patch.get(k) in (None, "")]
                if missing:
                    fail("a planned task also needs: " + ", ".join(missing))
                try:
                    impact, conf, effort = (int(patch[k]) for k in ("impact", "confidence", "effort"))
                except (TypeError, ValueError):
                    fail("impact, confidence and effort must be whole numbers from 1 to 5")
                if not all(1 <= v <= 5 for v in (impact, conf, effort)):
                    fail("impact, confidence and effort must be whole numbers from 1 to 5")
                score = round(impact * conf / effort, 2)
                floor = float((d.get("planner") or {}).get("min_score", PLAN_MIN_SCORE))
                if score < floor:
                    out({"rejected": True, "reason": "score %.2f is below %.2f: not worth a session" % (score, floor)}, 5)
                patch["score"] = score
                lanes = {x["id"]: x for x in plan_view(d, now, 0)["lanes"]}
                if lane not in lanes:
                    fail("unknown lane: %s (known: %s)" % (lane, ", ".join(sorted(lanes))))
                if lanes[lane]["saturated"]:
                    out({"rejected": True, "reason": "lane %s already has %d of %d items waiting on Joseph or the operator"
                         % (lane, lanes[lane]["owner_wip"], lanes[lane]["wip_limit"])}, 5)
            if patch.get("key") and not a.allow_repeat:
                k = norm_key(patch["key"])
                for pool in ("queue", "completed", "blocked"):
                    for t in d.get(pool) or []:
                        if isinstance(t, dict) and t.get("key") and norm_key(t["key"]) == k:
                            out({"rejected": True, "reason": "same key as %s (%s, %s)" % (t.get("id"), pool, t.get("status"))}, 5)
            patch.setdefault("status", READY)
            patch.setdefault("priority", 2)
            patch.setdefault("found_utc", fmt(now))
            ordered = {"id": patch.pop("id", None) or next_id(d)}
            if ordered["id"] in all_ids(d):
                fail("id already used: " + ordered["id"])
            ordered.update(patch)
            for key, field, pool in (("map_item", "map_item", "items"), ("scout", "scout", "scouts")):
                ref = ordered.get(field)
                if ref and any(t.get(field) == ref and t.get("status") in (READY, WAIT_DATA) for t in queue):
                    fail("a live task already exists for %s %s" % (key, ref))
            queue.append(ordered)
            save(target, d)
            out({"added": ordered["id"]})
        hits = [n for n, t in enumerate(queue) if str(t.get("id")) == args[0]]
        if len(hits) != 1:
            fail("%d queue tasks with id %s" % (len(hits), args[0]))
        task = queue[hits[0]]
        patch.pop("id", None)
        task.update(patch)
        if cmd == "update":
            save(target, d)
            out({"updated": task["id"], "status": task.get("status")})
        task["status"] = a.status
        task["done_utc"] = fmt(now)
        deliv = task.get("deliverable")
        if isinstance(deliv, dict):
            deliv = "%s:%s" % (deliv.get("type") or "item", deliv.get("ref") or task["id"])
        mins = end_current(controller(d), str(task["id"]), now, deliv if deliv else None)
        if mins is not None:
            task["minutes"] = mins
        d.setdefault("completed", []).append(queue.pop(hits[0]))
        d["last_verified_action"] = "%s %s %s: %s" % (task["id"], a.status, fmt(now), short(task.get("result", title_of(task)), 160))
        save(target, d)
        out({"finished": task["id"], "status": a.status, "done_utc": task["done_utc"]})

    if cmd in ("set", "append"):
        if len(args) != 2:
            fail("usage: %s PATH JSON" % cmd)
        try:
            value = json.loads(args[1])
        except ValueError:
            fail("the value must be JSON (quote strings: '\"text\"')")
        if args[0].strip("/").startswith("controller/addenda") and os.environ.get("ESCG_SUPERVISOR") != "1":
            fail("controller/addenda is written by the supervising session only")
        parent, key = walk(d, args[0])
        if cmd == "set":
            parent[key] = value
        else:
            lst = parent[key] if (isinstance(parent, list) or key in parent) else None
            if lst is None:
                lst = parent[key] = []
            if not isinstance(lst, list):
                fail("not a list: " + args[0])
            if a.front:
                lst.insert(0, value)
            else:
                lst.append(value)
            if a.keep and len(lst) > a.keep:
                if a.front:
                    del lst[a.keep:]
                else:
                    del lst[: len(lst) - a.keep]
        save(target, d)
        out({"ok": True, "path": args[0]})

    if cmd == "monitor-done":
        controller(d)["monitor"]["last_utc"] = fmt(now)
        save(target, d)
        out({"monitor_last_utc": fmt(now)})

    if cmd == "explore":
        if not args:
            fail("usage: explore KEY --avenue needs|search|channels|quality --added N --result TEXT "
                 "[--candidates N] [--lane L] [--new-evidence TEXT]")
        pl = d.get("planner")
        if not isinstance(pl, dict):
            fail("no planner block in " + target)
        c = controller(d)
        run = c["lock"].get("holder")
        if not run:
            fail("no session holds the lock")
        avenue = a.avenue.strip().lower()
        if avenue not in FB_AVENUES:
            fail("--avenue must be one of: " + ", ".join(FB_AVENUES))
        key = norm_key(args[0])
        if not key:
            fail("KEY names the question or segment explored, e.g. needs:paying-for-memory-care")
        if not a.result.strip():
            fail("--result is required: the sources read with their dates, what qualified, what did not and why")
        fq, verdict = None, ""
        if avenue == "frontier":
            fr = pl.get("frontier") if isinstance(pl.get("frontier"), dict) else {}
            for q in fr.get("questions") or []:
                if isinstance(q, dict) and norm_key("frontier:" + str(q.get("id"))) == key:
                    fq = q
                    break
            if fq is None or fq.get("status") != "open":
                out({"rejected": True, "reason": "a frontier exploration answers an open question of planner/frontier/"
                     "questions and its KEY is frontier:<id>"
                     + ("" if fq is None else " (%s is already %s)" % (fq.get("id"), fq.get("status"))),
                     "next": frontier_view(d, now, run)["next"]}, 5)
            verdict = a.verdict.strip().lower()
            if verdict not in FR_VERDICTS:
                fail("--verdict act|watch|drop is required for a frontier question: act (tasks, an asset, a handoff or a "
                     "lettered decision came out of it), watch (--result names the event or date that reopens it) or "
                     "drop (--result gives the reason)")
        fb = pl.setdefault("fallback", {})
        log = fb.setdefault("log", [])
        days = fb.get("explore_recheck_days", FB_RECHECK_DAYS)
        days = days if isinstance(days, (int, float)) and not isinstance(days, bool) and days > 0 else FB_RECHECK_DAYS
        if not a.new_evidence.strip():
            for e in log:
                t = parse_ts(e.get("utc")) if isinstance(e, dict) else None
                if t is not None and e.get("key") == key and (now - t) < dt.timedelta(days=days):
                    out({"rejected": True, "reason": "%s was explored at %s (%s). Pick a different question, source or "
                         "segment, or pass --new-evidence saying what changed since then"
                         % (key, e.get("utc"), short(e.get("result") or "", 110))}, 5)
        entry = {"utc": fmt(now), "run": run, "key": key, "avenue": avenue, "lane": a.lane or None,
                 "candidates": max(0, a.candidates), "added": max(0, a.added), "result": short(a.result, 320)}
        if a.new_evidence.strip():
            entry["new_evidence"] = short(a.new_evidence, 160)
        if fq is not None:
            entry["verdict"] = verdict
            fq.update({"status": "explored", "verdict": verdict, "explored_utc": fmt(now), "run": run,
                       "added": max(0, a.added), "result": short(a.result, 600)})
        log.insert(0, entry)
        del log[FB_LOG_KEEP:]
        if a.added > 0:
            fb["empty_streak"] = 0
            fb["exhausted_until_utc"] = ""
        mins = end_current(c, "explore:" + args[0], now)
        if mins is None:
            mins = end_current(c, "explore:" + key, now)
        save(target, d)
        mine = [e for e in log if isinstance(e, dict) and e.get("run") == run]
        classes = sorted({e.get("avenue") for e in mine})
        need = fb.get("min_avenues", FB_MIN_AVENUES)
        need = need if isinstance(need, int) and not isinstance(need, bool) else FB_MIN_AVENUES
        out({"explored": key, "avenue": avenue, "added": max(0, a.added), "minutes": mins,
             "this_session": {"explorations": len(mine), "avenue_classes": classes,
                              "tasks_added": sum(int(e.get("added") or 0) for e in mine)},
             "classes_still_needed_before_no_worthwhile_work": max(0, need - len(classes)),
             "frontier": ({k: v for k, v in frontier_view(d, now, run, discovery_room(budget_view(d, now))).items()
                           if k != "_slot"} if avenue == "frontier" else None)})

    def new_project(pj, new, added_by, lens=None):
        """Checks a project file and appends it. The cap of eight live projects (v4.7) is gone: it counted
        projects that legitimately wait for a measurement, so that waiting projects blocked new ones. What
        bounds new projects now: development comes first (discovery is due only when no project step is due),
        one discovery per session and per lens cadence, the dated evidence each project needs, and this
        duplicate check."""
        need = ("name", "goal", "metric", "why", "plan", "next_step", "kill_when")
        if not isinstance(new, dict) or not all(str(new.get(k) or "").strip() for k in need):
            fail("the project file needs " + ", ".join(need) + " (why = the dated evidence)")
        words = set(re.findall(r"[a-z]{4,}", (str(new["name"]) + " " + str(new["goal"])).lower()))
        for p in pj:
            w2 = set(re.findall(r"[a-z]{4,}", (str(p.get("name")) + " " + str(p.get("goal"))).lower()))
            if words and len(words & w2) / max(1, len(words)) >= 0.6:
                out({"rejected": True, "reason": "project %s already covers this (%s: %s). Develop that project "
                     "instead (project-step); if this was a discovery assignment, record the lens without --from "
                     "and name it in the result." % (p.get("id"), p.get("status"), short(p.get("name") or "", 80))}, 5)
        taken = {str(p.get("id")) for p in pj}
        n = len(pj) + 1
        while "PJ%02d" % n in taken:
            n += 1
        new.update({"id": "PJ%02d" % n, "status": "active", "stage": new.get("stage") or "investigate",
                    "added_utc": fmt(now), "added_by": added_by or "worker", "log": []})
        if lens:
            new["lens"] = lens
        pj.append(new)
        return new["id"]

    if cmd == "project-discover":
        pl = d.setdefault("planner", {})
        c = controller(d)
        run = c["lock"].get("holder")
        if not run:
            fail("no session holds the lock")
        pdc = pl.setdefault("project_discovery", {})
        lenses = pd_lenses(pdc)
        if not args:
            fail("usage: project-discover LENS --result TEXT [--from FILE]; lenses: " + ", ".join(l["id"] for l in lenses))
        lens = next((l for l in lenses if norm_key(l["id"]) == norm_key(args[0])), None)
        if lens is None:
            fail("unknown lens %s; the lenses are: %s" % (args[0], ", ".join(l["id"] for l in lenses)))
        room = discovery_room(budget_view(d, now))
        pdv = project_discovery_view(d, now, run, room)
        if pdv["this_session"] > 0:
            out({"rejected": True, "reason": "this session has recorded its discovery assignment. One per session, so "
                 "that it is worked deeply (27 Nov 2026: thirteen questions were answered in 29 minutes when the "
                 "list was open-ended). Develop the project you found; the next session takes the next lens at once.",
                 "lenses_due": pdv["lenses_due"]}, 5)
        if lens["id"] not in pdv["lenses_due"]:
            last = ((pdc.get("state") or {}).get(lens["id"]) or {}).get("last_utc")
            out({"rejected": True, "reason": "lens %s was examined at %s and its evidence has not had time to change "
                 "(cadence %s hours). Take a lens that is due." % (lens["id"], last, lens.get("cadence_hours") or PD_CADENCE_H),
                 "lenses_due": pdv["lenses_due"]}, 5)
        if len(a.result.strip()) < PD_RESULT_MIN:
            fail("--result needs the sources you read with their dates, the candidates you compared and why each was "
                 "chosen or rejected (at least %d characters): it is what the next discovery builds on" % PD_RESULT_MIN)
        new_id = new_project(pl.setdefault("projects", []), load(a.src), run, lens["id"]) if a.src else None
        entry = {"utc": fmt(now), "run": run, "lens": lens["id"], "added": 1 if new_id else 0, "project": new_id,
                 "result": short(a.result, 1500)}
        pdc.setdefault("state", {})[lens["id"]] = {"last_utc": fmt(now), "run": run, "project": new_id,
                                                   "result": short(a.result, 600),
                                                   "marker": EVIDENCE.get(lens.get("marker")) if lens.get("marker") else None}
        log = pdc.setdefault("log", [])
        log.insert(0, entry)
        del log[PD_LOG_KEEP:]
        pdc.pop("replace_failed", None)
        deliverable = ("project:%s found (lens %s)" % (new_id, lens["id"])) if new_id else ("discovery:%s no project" % lens["id"])
        mins = end_current(c, "discover:" + args[0], now, deliverable)
        if mins is None:
            mins = end_current(c, "discover:" + lens["id"], now)
        save(target, d)
        left = project_discovery_view(d, now, run, room)["lenses_due"]
        out({"ok": True, "lens": lens["id"], "project": new_id, "minutes": mins, "lenses_due_left": left,
             "now": ("develop %s in this session: start project:%s, do its first step, project-step %s --run %s --result ... "
                     "--new-evidence \"<next step>\"" % (new_id, new_id, new_id, run)) if new_id else
                    "recorded: this evidence holds no project today. Do not start another discovery in this session; "
                    "close when nothing else is due for you, and the next session takes the next lens."})

    if cmd in ("project-step", "project-add"):
        pl = d.setdefault("planner", {})
        pj = pl.setdefault("projects", [])
        if cmd == "project-add":
            new_id = new_project(pj, load(a.src) if a.src else None, a.run or (controller(d)["lock"].get("holder") or "worker"))
            save(a.loop, d)
            out({"ok": True, "added": new_id})
        pid = args[0] if args else ""
        p = next((x for x in pj if x.get("id") == pid), None)
        if p is None:
            fail("no project %s" % pid)
        if not a.result.strip():
            fail("project-step needs --result: what was done, with the sources read and their dates, and the artifact (commit, file, pull request, prepared handoff)")
        st_ = (a.verdict or p.get("status") or "active").strip()
        if st_ not in PJ_STATUSES:
            fail("--verdict must be one of " + ", ".join(PJ_STATUSES))
        if st_ in ("active", "waiting") and not a.new_evidence.strip():
            fail("a live project needs its next step: --new-evidence \"<the next concrete step>\" (and --resume-when \"<UTC time>\" when it waits)")
        nxt_txt = (a.new_evidence or "").lower()
        if st_ == "waiting" and re.search(r"\bmerge[sd]?\b|\bmerging\b|package (#?\d+ )?(is |gets )?(merged|live)", nxt_txt) and (a.lane or p.get("stage")) != "measure":
            fail("Joseph's merge is not a reason to wait (owner rule of 24 Nov 2026: a pending approval blocks only the "
                 "affected action). Build now on a branch cut from the open package branch (or from main), open the "
                 "review pull request, and let it enter the next package; keep the project active with that as its next step.", 5)
        if st_ == "failed" and len(a.result) < 200:
            fail("a failed project needs the evidence of why it failed (at least a few sentences with sources): document why, then discover another")
        p.setdefault("log", []).append({"utc": fmt(now), "run": a.run or (args[1] if len(args) > 1 else ""), "result": short(a.result, 1500),
                                        "stage": a.lane or p.get("stage")})
        p["log"] = p["log"][-30:]
        p["status"] = st_
        if a.lane:
            p["stage"] = a.lane
        p["next_step"] = a.new_evidence.strip() or None
        p["not_before_utc"] = a.resume_when.strip() or None
        p["updated_utc"] = fmt(now)
        if st_ == "failed":
            # "When an opportunity genuinely fails, document why and discover another" (Joseph, 27 Nov 2026):
            # the replacement is looked for at once, in the evidence examined longest ago.
            pl.setdefault("project_discovery", {})["replace_failed"] = {"utc": fmt(now), "project": pid}
        c_ = controller(d)
        if c_["lock"].get("holder"):
            cur = str((c_["lock"].get("current") or {}).get("what") or "")
            end_current(c_, cur if pid.lower() in cur.lower() else "\0", now,
                        "project:%s %s" % (pid, a.lane or p.get("stage") or "step"))
        save(a.loop, d)
        out({"ok": True, "project": pid, "status": st_, "stage": p.get("stage"), "next_step": p.get("next_step"), "not_before_utc": p.get("not_before_utc")})

    if cmd == "frontier-add":
        pl = d.get("planner")
        if not a.src or not isinstance(pl, dict):
            fail("usage: frontier-add --from FILE (JSON object: question, lever, evidence, output, why "
                 "[, id, priority 1-5, not_before_utc])")
        new = load(a.src)
        if not isinstance(new, dict) or not all(str(new.get(k) or "").strip() for k in ("question", "lever", "evidence", "output", "why")):
            fail("the file needs question, lever, evidence, output and why (the evidence that suggested the question)")
        fr = pl.setdefault("frontier", {"enabled": True, "questions": []})
        qs = fr.setdefault("questions", [])

        def words(t):
            return set(re.findall(r"[a-z0-9]{4,}", str(t).lower()))

        nw = words(new["question"])
        for q in qs:
            if not isinstance(q, dict):
                continue
            ow = words(q.get("question") or "")
            if new.get("id") and norm_key(new["id"]) == norm_key(q.get("id") or ""):
                out({"rejected": True, "reason": "id %s exists" % q.get("id")}, 5)
            if nw and ow and len(nw & ow) / float(len(nw | ow)) >= 0.6:
                out({"rejected": True, "reason": "too close to %s (%s): a frontier question is a genuinely new one, never "
                     "a rewording" % (q.get("id"), q.get("status")), "existing": short(q.get("question") or "", 200)}, 5)
        if sum(1 for q in qs if isinstance(q, dict) and q.get("status") == "open") >= FR_MAX_OPEN:
            out({"rejected": True, "reason": "%d questions are open already: explore those first" % FR_MAX_OPEN}, 5)
        nums = [int(m.group(1)) for m in (re.match(r"^F(\d+)$", str(q.get("id") or "")) for q in qs if isinstance(q, dict)) if m]
        qid = str(new.get("id") or "F%02d" % ((max(nums) if nums else 0) + 1))
        pr = new.get("priority")
        row = {"id": qid, "priority": pr if isinstance(pr, int) and not isinstance(pr, bool) and 1 <= pr <= 5 else 3,
               "lever": short(new["lever"], 40), "question": short(new["question"], 700),
               "evidence": short(new["evidence"], 500), "output": short(new["output"], 400), "why": short(new["why"], 300),
               "status": "open", "added_utc": fmt(now), "added_by": (controller(d)["lock"].get("holder") or "supervisor")}
        if new.get("not_before_utc"):
            if parse_ts(new["not_before_utc"]) is None:
                fail("not_before_utc is unreadable")
            row["not_before_utc"] = new["not_before_utc"]
        qs.append(row)
        save(target, d)
        out({"added": qid, "open": sum(1 for q in qs if isinstance(q, dict) and q.get("status") == "open")})

    if cmd == "start":
        if not args:
            fail("usage: start WHAT (a task id, angle:ID, plan:LANE or explore:KEY)")
        c = controller(d)
        if not c["lock"].get("holder"):
            fail("no session holds the lock")
        c["lock"]["utc"] = fmt(now)
        c["lock"]["current"] = {"what": args[0], "since_utc": fmt(now)}
        save(target, d)
        out({"started": args[0], "utc": fmt(now)})

    if cmd == "sweep-done":
        if not args:
            fail("usage: sweep-done ANGLE --added N --result TEXT [--recheck-hours H]")
        pl = d.get("planner")
        if not isinstance(pl, dict):
            fail("no planner block in " + target)
        hits = [x for x in pl.get("angles") or [] if x.get("id") == args[0]]
        if len(hits) != 1:
            fail("unknown sweep angle: " + args[0])
        ang = hits[0]
        hours = a.recheck_hours if a.recheck_hours is not None else float(ang.get("recheck_hours", 24))
        ang["last_checked_utc"] = fmt(now)
        ang["next_check_utc"] = fmt(now + dt.timedelta(hours=max(1.0, hours)))
        ang["last_added"] = max(0, a.added)
        ang["last_result"] = short(a.result or "(no result given)", 300)
        log = pl.setdefault("sweep_log", [])
        log.insert(0, "%s %s +%d: %s" % (fmt(now), args[0], max(0, a.added), short(a.result or "", 160)))
        del log[60:]
        c = controller(d)
        mins = end_current(c, "angle:" + args[0], now) if c["lock"].get("holder") else None
        save(target, d)
        out({"angle": args[0], "added": a.added, "next_check_utc": ang["next_check_utc"], "minutes": mins})

    if cmd == "metrics":
        days = max(1, a.days)
        since = now - dt.timedelta(days=days)
        rows, active, productive = [], 0.0, 0
        from collections import Counter
        launches, stops, deliverables = Counter(), Counter(), Counter()
        for s_ in (d.get("controller") or {}).get("sessions") or []:
            b = parse_ts(s_.get("end_utc"))
            if b is None or b < since:
                continue
            a0 = parse_ts(s_.get("start_utc")) or b
            active += max(0.0, (b - max(a0, since)).total_seconds() / 60)
            productive += int(s_.get("productive_min") or 0)
            la = (s_.get("launch") or "").lower()
            launches["timer" if la.startswith("timer") else "controller chain" if la.startswith("completion") else "manual or other"] += 1
            stops[s_.get("stop_reason") or "not recorded"] += 1
            for x in s_.get("deliverables") or []:
                deliverables[str(x).split(":")[0]] += 1
            rows.append(s_.get("run"))
        done = [t for t in d.get("completed") or [] if (parse_ts(t.get("done_utc")) or since) > since]
        view = {"days": days, "sessions": len(rows), "launches": dict(launches), "active_hours": round(active / 60, 2),
                "productive_hours": round(productive / 60, 2), "tasks_completed": len(done),
                "deliverables": dict(deliverables), "stop_reasons": dict(stops)}
        fbl = [e for e in (((d.get("planner") or {}).get("fallback") or {}).get("log") or [])
               if isinstance(e, dict) and (parse_ts(e.get("utc")) or since) > since]
        view["backlog_discovery"] = {"explorations": len(fbl), "tasks_added": sum(int(e.get("added") or 0) for e in fbl),
                                     "by_avenue": dict(Counter(str(e.get("avenue")) for e in fbl))}
        view["chain_sessions"] = launches.get("controller chain", 0)
        try:
            view["outcomes"] = outcomes_view(load(a.cloud), now, days)
        except (OSError, ValueError):
            view["outcomes"] = "cloud.json not readable"
        out(view)

    if cmd == "close":
        run = args[0]
        c = controller(d)
        start0 = parse_ts((c["lock"].get("since_utc") or c["lock"].get("utc")) if c["lock"].get("holder") == run else None)
        closing = (start0, now) if start0 else None
        st = compute(d, now, a.monitor_hours, run, closing=closing)
        pl = d.get("planner") if isinstance(d.get("planner"), dict) else {}
        fb = pl.get("fallback") if isinstance(pl.get("fallback"), dict) else {}
        mine = [e for e in (fb.get("log") or []) if isinstance(e, dict) and e.get("run") == run]
        classes = sorted({str(e.get("avenue")) for e in mine})
        fb_note = None
        pkg_skipped = a.package_skipped.strip()
        pkg_due_at_close = bool(st["package"]["due"])
        if pkg_due_at_close and not pkg_skipped:
            out({"refused": True, "wrote": "nothing",
                 "reason": "the daily package cut is due (procedure step 7, DAILY PACKAGE): no task keyed %s is "
                           "finished. Add it if the queue does not hold it yet (add --from), do the cut, finish "
                           "the task, then close again. If the session is out of time, or a usage limit, a store "
                           "error or a refused permission prevents the cut, repeat close with --package-skipped "
                           "\"<the reason>\"." % st["package"]["key"],
                 "package": st["package"]}, 6)
        if st["package"].get("recut_due") and not pkg_skipped:
            out({"refused": True, "wrote": "nothing",
                 "reason": "work that belongs in today's package was finished after its cut (%s) and the cut window "
                           "is still open: cut once more before closing (procedure step 7, DAILY PACKAGE, A SECOND "
                           "CUT: the same steps on the same pull request, no new task; then RECORD again with the "
                           "new head, cut_utc and contains, and rewrite line 1 of owner_review_needed). What is "
                           "time-critical for families must not wait a day. If the session is out of time, or a "
                           "usage limit, a store error or a refused permission prevents it, repeat close with "
                           "--package-skipped \"<the reason>\"." % ", ".join(str(x) for x in st["package"]["recut_for"]),
                 "package": st["package"]}, 6)
        if a.stop_reason in NO_WORK_REASONS and st["projects"]["due"] and st["projects"]["starts_sessions"] and not a.fallback_skipped.strip():
            out({"refused": True, "wrote": "nothing",
                 "reason": "growth projects have a due next step (%s): work it (THE PROJECTS rule in controller/addenda), record it with "
                           "project-step, then close; or close with --stop-reason time when out of time." % ", ".join(str(x["id"]) for x in st["projects"]["due"]),
                 "projects": st["projects"]}, 6)
        if a.stop_reason in NO_WORK_REASONS and st["frontier"]["due"] and not a.fallback_skipped.strip():
            out({"refused": True, "wrote": "nothing",
                 "reason": "open frontier questions wait (planner/frontier): an empty queue, a cooldown or a pending "
                           "approval does not end the search for genuinely new opportunities (Joseph, 26 Nov 2026). "
                           "Before closing with %s, answer the first one: start explore:frontier:<id>, do the research "
                           "its evidence field names, add what passes the gate, then explore frontier:<id> --avenue "
                           "frontier --verdict act|watch|drop --candidates N --added N --result TEXT, and work what it "
                           "added. If time, a usage limit, a store error or a refused permission prevents it, repeat "
                           "close with --fallback-skipped \"<the reason>\"; if the session is out of time, close with "
                           "--stop-reason time instead." % a.stop_reason,
                 "next": st["frontier"]["next"]}, 6)
        if a.stop_reason in NO_WORK_REASONS and st["project_discovery"]["due"] and not a.fallback_skipped.strip():
            out({"refused": True, "wrote": "nothing",
                 "reason": "PROJECT DISCOVERY is due: every project waits, no frontier question is open and this "
                           "session has not looked for the next growth project (Joseph, 28 Nov 2026: a guaranteed, "
                           "bounded, evidence-based discovery assignment, independent of project and lane cooldowns). "
                           "Before closing with %s, do the assignment for the lens below as project_discovery.how "
                           "says and record it with project-discover. If time, a usage limit, a store error or a "
                           "refused permission prevents it, repeat close with --fallback-skipped \"<the reason>\"; "
                           "if the session is out of time, close with --stop-reason time instead." % a.stop_reason,
                 "lens": st["project_discovery"]["lens"], "how": st["project_discovery"]["how"],
                 "recent": st["project_discovery"]["recent"]}, 6)
        pd_done = st["project_discovery"]["this_session"] > 0
        if a.stop_reason in NO_WORK_REASONS and st["fallback"]["due"] and pd_done:
            # the session did the deeper form of discovery: three avenue classes are not asked of it as well,
            # and backlog discovery neither rests nor counts an empty conclusion
            fb_note = {"utc": fmt(now), "run": run, "covered_by": "project discovery", "rest_hours": 0}
        elif a.stop_reason in NO_WORK_REASONS and st["fallback"]["due"]:
            need = st["fallback"]["min_avenues"]
            skipped = a.fallback_skipped.strip()
            if len(classes) < need and not skipped:
                out({"refused": True, "wrote": "nothing",
                     "reason": "backlog discovery is due and this session recorded %d of %d avenue classes (%s). "
                               "Before closing with %s: explore more avenues (start explore:KEY, then explore KEY "
                               "--avenue ... --added N --result TEXT) and work what they add; or, if time, budget, "
                               "permissions or a real lack of applicable avenues prevents it, repeat close with "
                               "--fallback-skipped \"<the reason>\". If the session is out of time, close with "
                               "--stop-reason time instead."
                               % (len(classes), need, ", ".join(classes) or "none", a.stop_reason),
                     "open_lanes": st["fallback"]["open_lanes"],
                     "explored_recently": [r["key"] for r in st["fallback"]["recent"]][:20]}, 6)
            streak = fb.get("empty_streak", 0)
            streak = streak if isinstance(streak, int) and not isinstance(streak, bool) and streak >= 0 else 0
            added = sum(int(e.get("added") or 0) for e in mine)
            base = fb.get("exhausted_base_hours", FB_BASE_H)
            base = base if isinstance(base, (int, float)) and not isinstance(base, bool) and base >= 1 else FB_BASE_H
            top = fb.get("exhausted_max_hours", FB_MAX_H)
            top = top if isinstance(top, (int, float)) and not isinstance(top, bool) and top >= base else FB_MAX_H
            # 28 NOV 2026: the rest is the answer to a conclusion that found NOTHING (12 hours, doubling with each
            # further empty conclusion). Until v4.7.1 this line read "hours = base if added > 0 else ...": the
            # session that closed at 08:39 UTC on 28 Nov had found two tasks and was rested for 12 hours.
            hours = 0 if added > 0 else min(top, base * (2 ** min(streak, 6)))
            fb = pl.setdefault("fallback", fb)
            fb["exhausted_until_utc"] = fmt(now + dt.timedelta(hours=hours)) if hours else ""
            fb["empty_streak"] = 0 if added > 0 else streak + 1
            fb["last_conclusion"] = {"utc": fmt(now), "run": run, "explorations": len(mine), "avenue_classes": classes,
                                     "tasks_added": added, "skipped": short(skipped, 200) if skipped else None,
                                     "rest_hours": hours}
            fb_note = fb["last_conclusion"]
            st = compute(d, now, a.monitor_hours, run, closing=closing)
        # an answered frontier question or another recorded exploration is progress too (a watch or a drop adds
        # no task and no change, and must not break the chain or cause a retry wait)
        progress = ((a.done + a.changed) > 0 or bool(mine) or st["projects"]["this_session"] > 0
                    or st["project_discovery"]["this_session"] > 0)
        next_work = eligible_work(st)
        start = (c["lock"].get("since_utc") or c["lock"].get("utc")) if c["lock"].get("holder") == run else None
        bud = budget_view(d, now, parse_ts(start) if start else None)
        # Work that only a different session may do (not_run names this run). Joseph, 25 Nov 2026: "If those
        # tasks require an independent session, Make should coordinate that session automatically." So NEXT is
        # yes and Make starts that session at once, with two exceptions that keep Make inside its free
        # operations and keep the daily package: (1) before the package cut of the UTC day, the session that
        # cuts the package takes the work, so it waits for that session; (2) when today's sessions have used
        # the day's budget of Make operations (planner/make_ops_per_day; see below), it waits for the day's
        # last session or for the next day. Without make_ops_per_day the older limit applies (sessions in
        # 24 hours). Since 26 Nov 2026 the same budget also ends an ordinary chain (ops_wait).
        blocked_here = [t for t in (d.get("queue") or []) if t.get("status") == READY and run in (t.get("not_run") or [])]
        handoff_only = st["eligible"] > 0 and st["eligible"] == len(blocked_here)
        day_ago = now - dt.timedelta(hours=24)
        sessions_24h = 1 + sum(1 for s_ in c["sessions"] if isinstance(s_, dict) and s_.get("run") != run
                               and (parse_ts(s_.get("end_utc")) or parse_ts(s_.get("start_utc")) or day_ago) > day_ago)
        cap = pl.get("handoff_sessions_24h", HANDOFF_SESSIONS_24H)
        cap = cap if isinstance(cap, int) and not isinstance(cap, bool) and cap >= 1 else HANDOFF_SESSIONS_24H
        # SINCE 27 NOV 2026 (Make Core, 10,000 credits a month, timer every 15 minutes): session starts are no
        # longer scarce. planner/make_ops_per_day and planner/handoff_sessions_24h are absent, so nothing
        # below holds a chain or a handoff back for Make's sake: NEXT is yes whenever eligible work remains,
        # the session made progress and the usage reserve allows it, and the wake time is simply when the
        # next thing is due. The budget code stays for the case that either setting is given again (a free
        # plan). What still limits sessions: the usage reserve (budget_view), Make's hourly limit and its
        # monthly ceiling, the lock, and work actually being due.
        mops = pl.get("make_ops_per_day")
        mops = mops if isinstance(mops, int) and not isinstance(mops, bool) and mops >= 10 else None
        # Make's free operations are the scarce resource, so they are budgeted per day here (26 Nov 2026: a
        # night chain of four sessions left one operation for the session that cuts the daily package). The
        # budget day starts with the package window, so the first session of a day is the one that cuts.
        # Make counts 3 operations per session start and 2 per closing report that does not chain. With 13 a
        # day: the cutting session, one chained session, and a last session at the next monitoring pass.
        # planner/make_ops_per_day must stay below ops_per_day in Make's record V3 (the hard allowance), or
        # Make holds sessions back at times this helper does not expect.
        pkw = st["package"]
        try:
            h0, m0 = [int(x) for x in pkw["window_utc"][0].split(":")] if pkw.get("enabled") else (0, 0)
        except Exception:
            h0, m0 = 0, 0
        day0 = now.replace(hour=h0, minute=m0, second=0, microsecond=0)
        if now < day0:
            day0 -= dt.timedelta(days=1)
        day_end = day0 + dt.timedelta(days=1)
        earlier_today = [s_ for s_ in c["sessions"] if isinstance(s_, dict) and s_.get("run") != run
                         and (parse_ts(s_.get("start_utc")) or day_ago) >= day0]
        ops_today = (3 * (len(earlier_today) + (1 if (parse_ts(start) if start else now) >= day0 else 0))
                     + 2 * sum(1 for s_ in earlier_today if s_.get("next") != "yes"))
        hold_cut = bool(st["package"]["ahead_today"]) and mops is not None
        # A chained start (3) and its closing report (2) are allowed only while a further whole session (5)
        # still fits afterwards: that one carries the second monitoring pass of the day.
        chain_room = (ops_today + 5 + 5 <= mops) if mops is not None else True
        another_fits = (ops_today + 2 + 5 <= mops) if mops is not None else True
        one_after_next = (ops_today + 2 + 5 + 5 <= mops) if mops is not None else True
        hold_ops = (not chain_room) if mops is not None else (cap is not None and sessions_24h >= cap)
        handoff_wait = handoff_only and (hold_cut or hold_ops)
        ops_wait = bool(mops is not None and not chain_room and st["eligible"] > 0 and not handoff_wait)
        handoff_why = None
        if handoff_wait:
            handoff_why = ("the session that cuts the daily package takes it (window from %s UTC)" % st["package"]["window_utc"][0]
                           if hold_cut else
                           ("Make's operations for today are used by its sessions (about %d of %d)" % (ops_today, mops)
                            if mops is not None else "%d sessions in 24 hours (limit %s)" % (sessions_24h, cap)))
        nxt = "yes" if (st["eligible"] > 0 and progress and not bud["over"] and not handoff_wait and not ops_wait) else "no"
        if nxt == "yes":
            wake = None
        elif bud["over"] and st["eligible"] > 0:
            wake = wake_minutes(bud["resume_utc"], now)
        elif handoff_wait:
            wake = st["wake_minutes"]
        elif ops_wait:
            wake = WAKE_RETRY
        elif st["eligible"] > 0:
            wake = WAKE_RETRY
        else:
            wake = st["wake_minutes"]
        ops_why = None
        if nxt == "no" and mops is not None and not another_fits:
            # nothing more fits today: the next session is the one that opens the next budget day
            to_day_end = max(WAKE_MIN, min(WAKE_MAX, math.ceil((day_end - now).total_seconds() / 60) + 1))
            wake = to_day_end if pkw.get("enabled") else max(int(wake or 0), to_day_end)
            ops_why = ("Make's operations for this day are used (about %d of %d, counting this report); the next session "
                       "opens the next day at %s UTC" % (ops_today + 2, mops, fmt(day_end)))
        elif nxt == "no" and mops is not None and not one_after_next:
            # exactly one more session fits today. It is the day's last, so it waits for the next monitoring
            # pass and does the waiting work then (never later than the next package window): otherwise an
            # early sweep or a retry would use it up and the site would go a whole day without a check.
            mon_t = parse_ts((c.get("monitor") or {}).get("last_utc"))
            mon_due = mon_t + dt.timedelta(hours=a.monitor_hours) - grace(d) if mon_t else None
            # ...unless today's package cut is still open (skipped with a reason at this close): then the
            # last session comes as soon as it is due, because the cut has a window and the second check has not.
            mon_ahead = bool(mon_due and mon_due > now) and not st["package"]["due"]
            if mon_ahead:
                wake = max(int(wake or 0), wake_minutes(fmt(mon_due), now))
            if pkw.get("enabled") and pkw.get("next_due_utc"):
                wake = min(int(wake or WAKE_DEFAULT), wake_minutes(pkw["next_due_utc"], now))
            ops_why = ("Make's operations allow one more session today (about %d of %d used); %s%s"
                       % (ops_today + 2, mops,
                          "it is kept for the next monitoring pass" if mon_ahead else "it starts when the next thing is due",
                          " and does the waiting work then" if st["eligible"] > 0 else ""))
        if ops_why and bud["over"] and st["eligible"] > 0:
            # never earlier than the usage reserve allows: a start before that would only spend operations
            wake = max(int(wake or 0), wake_minutes(bud["resume_utc"], now))
        c["sessions"].insert(0, {"run": run, "start_utc": start, "end_utc": fmt(now), "launch": a.launch,
                                 "outcome": a.outcome, "done": a.done, "changed": a.changed, "tasks": a.tasks,
                                 "next": nxt, "wake_minutes": wake, "next_due_utc": st["next_due_utc"],
                                 "plan_due": st["plan"]["due"], "saturated": st["plan"]["saturated"],
                                 "budget_used_hours_24h": bud["used_hours_24h"], "budget_used_hours_7d": bud["used_hours_7d"],
                                 "productive_min": int(c["lock"].get("productive_min") or 0) if c["lock"].get("holder") == run else 0,
                                 "deliverables": (c["lock"].get("deliverables") or [])[:25] if c["lock"].get("holder") == run else [],
                                 "stop_reason": a.stop_reason or ("continuing" if nxt == "yes" else "not recorded"),
                                 "considered": short(a.considered, 700), "resume_when": short(a.resume_when, 240),
                                 "sweep_due_left": [x["id"] for x in st["sweep"]["due"]],
                                 "sessions_24h": sessions_24h,
                                 "handoff": {"tasks_for_next_session": [t.get("id") for t in blocked_here],
                                             "waits_for_next_due_session": handoff_wait, "why": handoff_why,
                                             "make_ops_today_estimate": ops_today} if blocked_here else None,
                                 "make_ops": {"day_from_utc": fmt(day0), "used_estimate": ops_today + (0 if nxt == "yes" else 2),
                                              "per_day": mops, "chain_held": ops_wait, "why": ops_why} if mops is not None else None,
                                 "package": {"due_at_close": pkg_due_at_close, "recut_due_at_close": bool(st["package"].get("recut_due")),
                                             "skipped": short(pkg_skipped, 200) or None,
                                             "done_today": st["package"]["done_today"]} if st["package"]["enabled"] else None,
                                 "backlog_discovery": {"explorations": len(mine), "avenue_classes": classes,
                                                       "tasks_added": sum(int(e.get("added") or 0) for e in mine),
                                                       "concluded": fb_note},
                                 "frontier": {"explored": [e.get("key") for e in mine if e.get("avenue") == "frontier"],
                                              "open_left": st["frontier"]["open"]} if st["frontier"]["enabled"] else None,
                                 "project_discovery": {"recorded": [{"lens": e.get("lens"), "project": e.get("project")}
                                                                    for e in ((pl.get("project_discovery") or {}).get("log") or [])
                                                                    if isinstance(e, dict) and e.get("run") == run],
                                                       "lenses_due_left": st["project_discovery"]["lenses_due"],
                                                       "waiting_for": st["project_discovery"]["waiting_for"]}
                                 if st["project_discovery"]["enabled"] else None,
                                 "projects_stepped": st["projects"]["this_session"],
                                 "next_work": next_work,
                                 "discovery_room": bool(st["fallback"]["room"])})
        del c["sessions"][80:]
        if c["lock"].get("holder") in ("", run):
            c["lock"] = {"holder": "", "utc": ""}
        c["next"] = {"written_utc": fmt(now), "eligible_now": st["eligible"], "next_due": st["next_due"]}
        d["last_run"] = {"utc": fmt(now), "event": "Make controller: " + (a.launch or "start"),
                         "picked": a.tasks or "none", "why": a.outcome}
        save(target, d)
        out({"next": nxt, "wake_minutes": wake, "done": a.done, "eligible_left": st["eligible"],
             "next_work": next_work, "wake_utc": st.get("wake_utc"),
             "project_discovery": {k: st["project_discovery"][k] for k in ("lenses_due", "waiting_for", "this_session")},
             "discovery_room": bool(st["fallback"]["room"]),
             "next_due_utc": st["next_due_utc"], "budget": bud, "sessions_24h": sessions_24h,
             "handoff_tasks_for_next_session": [t.get("id") for t in blocked_here],
             "handoff_waits_for_next_due_session": handoff_wait, "handoff_why": handoff_why,
             "make_ops_today_estimate": ops_today, "make_ops_per_day": mops, "make_ops_why": ops_why,
             "backlog_discovery": fb_note,
             "warning": None if (nxt == "yes" or a.stop_reason) else "stopping without --stop-reason, --considered and --resume-when"})

    fail("unknown command: " + cmd)


if __name__ == "__main__":
    main()
