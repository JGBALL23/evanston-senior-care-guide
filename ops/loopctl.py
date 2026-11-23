#!/usr/bin/env python3
"""loopctl: small helper for the ESCG loop state files.

It exists so that a worker session never has to print or hand-edit the large
state files: it prints compact JSON and makes the routine edits itself.
Standard library only. It never touches the network and never runs git.

Read commands
  status   [--monitor-hours N]      what is due now and when the next thing is due
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
  close RUN --done N --changed M --outcome TEXT [--launch TEXT] [--tasks TEXT] [--monitor-hours N]
                                    write the session record, release the lock, print next/wake

Common options: --loop PATH (default ops/esc-tour-loop.json), --now ISO (tests only).
"""
import argparse
import datetime as dt
import json
import math
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


def plan_view(d, now, pipeline):
    """Planner state. Read only: never changes d."""
    pl = d.get("planner") or {}
    low = int(pl.get("low_water", PLAN_LOW_WATER))
    queue = d.get("queue") or []
    lanes = []
    for ln in sorted(pl.get("lanes") or [], key=lambda x: (x.get("order", 99), str(x.get("id")))):
        lid = ln.get("id")
        waiting = sum(1 for t in queue if t.get("status") == WAIT_OWNER and lane_of(t) == lid)
        wip = max(waiting, int(ln.get("owner_open") or 0))
        limit = int(ln.get("owner_wip_limit", 3))
        cool = parse_ts(ln.get("cooldown_until_utc"))
        cooling = cool is not None and cool > now
        live = sum(1 for t in queue if t.get("status") in (READY, WAIT_DATA) and lane_of(t) == lid)
        lanes.append({"id": lid, "order": ln.get("order"), "owner_wip": wip, "wip_limit": limit,
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


def compute(d, now, monitor_hours):
    c = d.get("controller") or {}
    lock = c.get("lock") or {}
    lock_t = parse_ts(lock.get("utc"))
    lock_age = None if not lock_t else int((now - lock_t).total_seconds() // 60)
    lock_live = bool(lock.get("holder")) and lock_age is not None and lock_age < LOCK_STALE_MIN

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
            elif when <= now:
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
        if when <= now:
            if s.get("id") not in queued_scouts:
                scouts_due.append(s)
        else:
            future.append((when, s.get("id")))
    scouts_due.sort(key=lambda s: s.get("next_due_utc") or "")

    mon_t = parse_ts((c.get("monitor") or {}).get("last_utc"))
    mon_age = None if not mon_t else round((now - mon_t).total_seconds() / 3600, 1)
    mon_due = mon_t is None or (now - mon_t) >= dt.timedelta(hours=monitor_hours)
    if mon_t is not None and not mon_due:
        future.append((mon_t + dt.timedelta(hours=monitor_hours), "monitor"))

    pipeline = len(ready) + len(recheck) + len(open_items) + len(scouts_due)
    plan = plan_view(d, now, pipeline)
    if plan["_wake"] is not None:
        future.append((plan["_wake"], "planner cooldown ends"))
    plan.pop("_wake", None)
    sweep = sweep_view(d, now, plan["lanes"])
    future.extend(sweep.pop("_later"))

    future.sort()
    next_due = future[0][0] if future else None
    eligible = pipeline + (1 if plan["due"] else 0) + len(sweep["due"])
    return {
        "now": fmt(now),
        "lock": {"holder": lock.get("holder", ""), "utc": lock.get("utc", ""), "age_min": lock_age, "live": lock_live},
        "ready": [{"id": t.get("id"), "priority": t.get("priority"), "workstream": t.get("workstream"),
                   "map_item": t.get("map_item"), "scout": t.get("scout"), "title": title_of(t)} for t in ready],
        "recheck_due": [{"id": t.get("id"), "not_before_utc": fmt(task_date(t)), "title": title_of(t)} for t in recheck],
        "open_items": [{"id": i.get("id"), "lane": i.get("lane"), "class": short(i.get("class", ""), 80)} for i in open_items],
        "scouts_due": [{"id": s.get("id"), "name": s.get("name"), "next_due_utc": s.get("next_due_utc")} for s in scouts_due],
        "event_waits": [{"id": t.get("id"), "status": t.get("status"),
                         "waiting_for": short(next((t[k] for k in WAIT_KEYS if t.get(k)), ""), 150)} for t in events],
        "monitor": {"last_utc": (c.get("monitor") or {}).get("last_utc", ""), "age_hours": mon_age, "due": mon_due},
        "plan": {k: plan[k] for k in ("due", "pipeline", "low_water", "plannable", "saturated")},
        "sweep": sweep,
        "budget": budget_view(d, now),
        "eligible": eligible,
        "work_now": eligible > 0 or mon_due,
        "next_due_utc": fmt(next_due) if next_due else None,
        "wake_minutes": wake_minutes(fmt(next_due) if next_due else None, now),
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


def budget_view(d, now, extra_start=None):
    """Worker session time against the usage reserve in planner: budget_hours_per_day (rolling 24 hours)
    and budget_hours_per_week (rolling 7 days); a missing or zero value means no limit for that window.
    extra_start: start time of the session that is closing now, counted up to now."""
    pl = d.get("planner") or {}
    spans_all = []
    for s in (d.get("controller") or {}).get("sessions") or []:
        a, b = parse_ts(s.get("start_utc")), parse_ts(s.get("end_utc"))
        if a and b and b >= a:
            spans_all.append((a, b))
    if extra_start and extra_start < now:
        spans_all.append((extra_start, now))
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
    a = p.parse_args()

    now = parse_ts(a.now) if a.now else dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    if now is None:
        fail("bad --now")
    target = a.file or a.loop
    d = load(target)
    cmd, args = a.cmd, a.args

    if cmd == "status":
        out(compute(d, now, a.monitor_hours))

    if cmd == "plan":
        st = compute(d, now, a.monitor_hours)
        pv = plan_view(d, now, st["plan"]["pipeline"])
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
        out({"ok": not problems, "problems": problems,
             "counts": compute(d, now, a.monitor_hours)["counts"], "scouts": len(scouts)}, 0 if not problems else 4)

    if cmd == "lock":
        run = args[0]
        c = controller(d)
        st = compute(d, now, a.monitor_hours)["lock"]
        if st["live"] and st["holder"] != run:
            out({"locked": True, "holder": st["holder"], "age_min": st["age_min"]}, 3)
        took_over = None
        prev = c.get("lock") or {}
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

    if cmd == "start":
        if not args:
            fail("usage: start WHAT (a task id, angle:ID or plan:LANE)")
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
        try:
            view["outcomes"] = outcomes_view(load(a.cloud), now, days)
        except (OSError, ValueError):
            view["outcomes"] = "cloud.json not readable"
        out(view)

    if cmd == "close":
        run = args[0]
        c = controller(d)
        st = compute(d, now, a.monitor_hours)
        progress = (a.done + a.changed) > 0
        start = (c["lock"].get("since_utc") or c["lock"].get("utc")) if c["lock"].get("holder") == run else None
        bud = budget_view(d, now, parse_ts(start) if start else None)
        nxt = "yes" if (st["eligible"] > 0 and progress and not bud["over"]) else "no"
        if nxt == "yes":
            wake = None
        elif bud["over"] and st["eligible"] > 0:
            wake = wake_minutes(bud["resume_utc"], now)
        elif st["eligible"] > 0:
            wake = WAKE_RETRY
        else:
            wake = wake_minutes(st["next_due_utc"], now)
        c["sessions"].insert(0, {"run": run, "start_utc": start, "end_utc": fmt(now), "launch": a.launch,
                                 "outcome": a.outcome, "done": a.done, "changed": a.changed, "tasks": a.tasks,
                                 "next": nxt, "wake_minutes": wake, "next_due_utc": st["next_due_utc"],
                                 "plan_due": st["plan"]["due"], "saturated": st["plan"]["saturated"],
                                 "budget_used_hours_24h": bud["used_hours_24h"], "budget_used_hours_7d": bud["used_hours_7d"],
                                 "productive_min": int(c["lock"].get("productive_min") or 0) if c["lock"].get("holder") == run else 0,
                                 "deliverables": (c["lock"].get("deliverables") or [])[:25] if c["lock"].get("holder") == run else [],
                                 "stop_reason": a.stop_reason or ("continuing" if nxt == "yes" else "not recorded"),
                                 "considered": short(a.considered, 700), "resume_when": short(a.resume_when, 240),
                                 "sweep_due_left": [x["id"] for x in st["sweep"]["due"]]})
        del c["sessions"][80:]
        if c["lock"].get("holder") in ("", run):
            c["lock"] = {"holder": "", "utc": ""}
        c["next"] = {"written_utc": fmt(now), "eligible_now": st["eligible"], "next_due": st["next_due"]}
        d["last_run"] = {"utc": fmt(now), "event": "Make controller: " + (a.launch or "start"),
                         "picked": a.tasks or "none", "why": a.outcome}
        save(target, d)
        out({"next": nxt, "wake_minutes": wake, "done": a.done, "eligible_left": st["eligible"],
             "next_due_utc": st["next_due_utc"], "budget": bud,
             "warning": None if (nxt == "yes" or a.stop_reason) else "stopping without --stop-reason, --considered and --resume-when"})

    fail("unknown command: " + cmd)


if __name__ == "__main__":
    main()
