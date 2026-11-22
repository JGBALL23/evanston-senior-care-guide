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

Write commands (edit the working copy only; committing and pushing is the caller's job)
  lock RUN                          take the session lock (exit 3 if a live session holds it)
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

LOCK_STALE_MIN = 75
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

    future.sort()
    next_due = future[0][0] if future else None
    eligible = len(ready) + len(recheck) + len(open_items) + len(scouts_due)
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
        "eligible": eligible,
        "work_now": eligible > 0 or mon_due,
        "next_due_utc": fmt(next_due) if next_due else None,
        "wake_minutes": wake_minutes(fmt(next_due) if next_due else None, now),
        "next_due": [{"utc": fmt(w), "what": i} for w, i in future[:6]],
        "counts": {"queue": len(queue), "completed": len(d.get("completed") or []),
                   "map_items": len(om.get("items") or []), "owner_review_needed": len(d.get("owner_review_needed") or [])},
    }


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
    for step in [p for p in path.split("/") if p]:
        m = STEP.match(step)
        if not m:
            fail("bad path step: " + step)
        name, sel, val = m.groups()
        if name is not None:
            if not isinstance(node, dict):
                fail("not an object at: " + step)
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
    a = p.parse_args()

    now = parse_ts(a.now) if a.now else dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    if now is None:
        fail("bad --now")
    target = a.file or a.loop
    d = load(target)
    cmd, args = a.cmd, a.args

    if cmd == "status":
        out(compute(d, now, a.monitor_hours))

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
        out({"ok": not problems, "problems": problems,
             "counts": compute(d, now, a.monitor_hours)["counts"], "scouts": len(scouts)}, 0 if not problems else 4)

    if cmd == "lock":
        run = args[0]
        c = controller(d)
        st = compute(d, now, a.monitor_hours)["lock"]
        if st["live"] and st["holder"] != run:
            out({"locked": True, "holder": st["holder"], "age_min": st["age_min"]}, 3)
        took_over = None
        if st["holder"] and st["holder"] != run:
            took_over = st["holder"]
            c["sessions"].insert(0, {"run": st["holder"], "start_utc": st["utc"], "end_utc": None,
                                     "outcome": "abandoned: no close recorded; lock taken over by " + run})
        c["lock"] = {"holder": run, "utc": fmt(now)}
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

    if cmd == "close":
        run = args[0]
        c = controller(d)
        st = compute(d, now, a.monitor_hours)
        progress = (a.done + a.changed) > 0
        nxt = "yes" if (st["eligible"] > 0 and progress) else "no"
        if nxt == "yes":
            wake = None
        elif st["eligible"] > 0:
            wake = WAKE_RETRY
        else:
            wake = wake_minutes(st["next_due_utc"], now)
        start = c["lock"].get("utc") if c["lock"].get("holder") == run else None
        c["sessions"].insert(0, {"run": run, "start_utc": start, "end_utc": fmt(now), "launch": a.launch,
                                 "outcome": a.outcome, "done": a.done, "changed": a.changed, "tasks": a.tasks,
                                 "next": nxt, "wake_minutes": wake, "next_due_utc": st["next_due_utc"]})
        del c["sessions"][30:]
        if c["lock"].get("holder") in ("", run):
            c["lock"] = {"holder": "", "utc": ""}
        c["next"] = {"written_utc": fmt(now), "eligible_now": st["eligible"], "next_due": st["next_due"]}
        d["last_run"] = {"utc": fmt(now), "event": "Make controller: " + (a.launch or "start"),
                         "picked": a.tasks or "none", "why": a.outcome}
        save(target, d)
        out({"next": nxt, "wake_minutes": wake, "done": a.done, "eligible_left": st["eligible"],
             "next_due_utc": st["next_due_utc"]})

    fail("unknown command: " + cmd)


if __name__ == "__main__":
    main()
