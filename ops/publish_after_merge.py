#!/usr/bin/env python3
"""Checks around publishing main after Joseph's merge (Evanston Senior Care Guide).

Used by the Claude task "ESCG publish after merge". This script never deploys:
the task runs the Netlify connector's command between `check` and `verify`.

  check    is there a commit on main that Joseph merged and that is not live?
           If so: every new commit is a pull request merged by him, the build
           reproduces _dist, the test suites pass, and the folder to deploy is
           prepared. Prints a JSON plan with "action": none | record | publish | hold.
  verify   compare the live site with the commit in the plan, page by page.
  record   write ops/live.json on branch ops/operator-state (what is live now).
  hold     record a commit that was not published and why (so it is reported once).
  selftest run check against the previous merge (as if the newest one were not
           live yet) and verify against the live site; changes nothing.

Rules it enforces: only main; only commits that are pull requests merged by
OWNER (or a commit that touches nothing that is published); never anything on a
failed build or test.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request

REPO = "JGBALL23/evanston-senior-care-guide"
URL = "https://github.com/" + REPO
SITE = "https://evanstonseniorcareguide.com"
SITE_ID = "e25a95a5-7a87-4d1c-bae7-8c35d496dded"
OWNER = "JGBALL23"
STATE_BRANCH = "ops/operator-state"
LIVE_FILE = "ops/live.json"
WORK = os.environ.get("PUBLISH_WORK", "/tmp/publish")
PUBLISHED = ["_dist", "netlify", "netlify.toml"]
BOOKKEEPING = {"data/indexnow-ledger.json"}
NOT_SERVED = {"_dist/_headers", "_dist/_redirects"}  # Netlify settings files: applied, never served
UA = "ESCG-publish-check"
MAX_PAGES = 60


def now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")


def run(cmd, cwd=None, timeout=900, env=None, check=False):
    p = subprocess.run(cmd, cwd=cwd, timeout=timeout, env=env, shell=isinstance(cmd, str),
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors="replace")
    if check and p.returncode != 0:
        raise RuntimeError("%s failed (%s): %s" % (cmd, p.returncode, p.stdout[-600:]))
    return p.returncode, p.stdout


def out(obj, code=0):
    print(json.dumps(obj, indent=1, ensure_ascii=False))
    sys.exit(code)


def api(path):
    """GitHub REST, with gh when it is there (authenticated), else anonymous."""
    if shutil.which("gh"):
        rc, o = run(["gh", "api", path], timeout=60)
        if rc == 0:
            return json.loads(o)
    req = urllib.request.Request("https://api.github.com/" + path,
                                 headers={"Accept": "application/vnd.github+json", "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def main_head():
    rc, o = run(["git", "ls-remote", URL, "refs/heads/main"], timeout=120, check=True)
    return o.split()[0]


def state_dir():
    d = os.path.join(WORK, "state")
    if not os.path.isdir(os.path.join(d, ".git")):
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(WORK, exist_ok=True)
        run(["git", "clone", "-q", "--depth", "5", "--single-branch", "--branch", STATE_BRANCH, URL, d],
            timeout=300, check=True)
    else:
        run(["git", "fetch", "-q", "origin", STATE_BRANCH], cwd=d, timeout=300, check=True)
        run(["git", "reset", "-q", "--hard", "FETCH_HEAD"], cwd=d, check=True)
    return d


def read_live():
    d = state_dir()
    f = os.path.join(d, LIVE_FILE)
    if not os.path.exists(f):
        return {}
    return json.load(open(f))


def write_live(change, message):
    """Apply `change(dict)` to ops/live.json and push; retried once if the branch moved."""
    for attempt in (1, 2, 3):
        d = state_dir()
        f = os.path.join(d, LIVE_FILE)
        live = json.load(open(f)) if os.path.exists(f) else {}
        change(live)
        with open(f, "w") as fh:
            fh.write(json.dumps(live, indent=1, ensure_ascii=False) + "\n")
        run(["git", "add", LIVE_FILE], cwd=d, check=True)
        rc, o = run(["git", "-c", "user.name=ESCG publish", "-c", "user.email=noreply@anthropic.com",
                     "commit", "-q", "-m", message], cwd=d)
        if rc != 0 and "nothing to commit" in o:
            return "unchanged"
        rc, o = run(["git", "push", "-q", "origin", "HEAD:" + STATE_BRANCH], cwd=d, timeout=300)
        if rc == 0:
            rc2, sha = run(["git", "rev-parse", "--short", "HEAD"], cwd=d)
            return sha.strip()
        last = o
        time.sleep(3)
    raise RuntimeError("could not push %s: %s" % (LIVE_FILE, last[-400:]))


def site_clone(head):
    d = os.path.join(WORK, "site")
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(WORK, exist_ok=True)
    run(["git", "clone", "-q", "--depth", "400", "--single-branch", "--branch", "main", URL, d],
        timeout=600, check=True)
    rc, o = run(["git", "rev-parse", "HEAD"], cwd=d, check=True)
    if o.strip() != head:
        run(["git", "fetch", "-q", "origin", head], cwd=d, timeout=300, check=True)
        run(["git", "checkout", "-q", "--detach", head], cwd=d, check=True)
    return d


def merged_by_owner(sha):
    """The pull request whose merge put this commit on main, if OWNER merged it."""
    try:
        prs = api("repos/%s/commits/%s/pulls" % (REPO, sha))
    except Exception as e:  # network or rate limit: never guess
        return None, "could not ask GitHub about %s: %s" % (sha[:7], e)
    for pr in prs:
        if not pr.get("merged_at") or (pr.get("base") or {}).get("ref") != "main":
            continue
        if pr.get("merge_commit_sha") != sha:
            continue
        full = api("repos/%s/pulls/%s" % (REPO, pr["number"]))
        who = (full.get("merged_by") or {}).get("login")
        if full.get("merged") and who == OWNER:
            return {"sha": sha, "pr": pr["number"], "merged_by": who, "merged_at": full.get("merged_at"),
                    "title": (full.get("title") or "")[:120]}, None
        return None, "pull request #%s was merged by %s, not by %s" % (pr["number"], who, OWNER)
    return None, "commit %s is not the merge of a pull request into main" % sha[:7]


def url_of(path):
    """_dist/x/index.html -> /x/ ; _dist/x.html -> /x.html ; other files as they are."""
    rel = path[len("_dist/"):]
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return "/" + rel[:-len("index.html")]
    return "/" + rel


ATAG = re.compile(r"<a\b[^>]*>", re.I)
SQUOTE = re.compile(r"""([\w:-]+)='([^']*)'""")
HREF = re.compile(r'href="(/[^"#?]*?)(?:index\.html|\.html)?((?:[#?][^"]*)?)"')


def _norm_tag(m):
    t = SQUOTE.sub(r'\1="\2"', m.group(0))
    return HREF.sub(lambda h: 'href="%s%s"' % (h.group(1), h.group(2)), t)


def norm_html(b):
    """Netlify rewrites internal links to pretty URLs and re-quotes that tag
    (<a class="x" href="/privacy.html"> becomes <a class='x' href='/privacy'>).
    Compare pages with their link tags brought to one form; everything else must be identical."""
    return ATAG.sub(_norm_tag, b.decode("utf-8", "replace")).encode()


def fetch(url, tries=1, wait=10):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Cache-Control": "no-cache"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            last = (e.code, b"")
        except Exception as e:
            last = (0, str(e).encode())
        if i + 1 < tries:
            time.sleep(wait)
    return last


def compare(site_dir, paths, tries=1):
    """Each published file against the live URL. HTML with links normalised, the rest byte for byte."""
    rows, ok = [], True
    for p in paths:
        local = os.path.join(site_dir, p)
        u = url_of(p)
        if not os.path.exists(local):  # removed by the merge: it must be gone
            st, _ = fetch(SITE + u, tries)
            good = st == 404
            rows.append({"url": u, "expect": "gone", "status": st, "same": good})
            ok = ok and good
            continue
        want = open(local, "rb").read()
        st, got = fetch(SITE + u, 1)
        is_html = p.endswith(".html")
        same = st == 200 and ((norm_html(want) == norm_html(got)) if is_html else (want == got))
        n = 1
        while not same and n < tries:  # the CDN may still serve the old copy for a moment
            time.sleep(10)
            st, got = fetch(SITE + u, 1)
            same = st == 200 and ((norm_html(want) == norm_html(got)) if is_html else (want == got))
            n += 1
        rows.append({"url": u, "status": st, "same": same,
                     "sha_main": hashlib.sha256(want).hexdigest()[:12],
                     "sha_live": hashlib.sha256(got).hexdigest()[:12] if got else None})
        ok = ok and same
    return ok, rows


def suites(site_dir):
    """Build, then every test suite the repository has. Returns (ok, results)."""
    env = dict(os.environ)
    os.makedirs("/tmp/bin", exist_ok=True)
    if not shutil.which("python") and not os.path.exists("/tmp/bin/python"):
        os.symlink(shutil.which("python3"), "/tmp/bin/python")
    env["PATH"] = "/tmp/bin:" + env.get("PATH", "")
    for cand in ("/usr/local/lib/node_modules_global", "/usr/local/lib/node_modules", "/usr/lib/node_modules"):
        if os.path.isdir(os.path.join(cand, "playwright")):
            env["NODE_PATH"] = cand + (":" + env["NODE_PATH"] if env.get("NODE_PATH") else "")
            break
    res = []
    rc, o = run([sys.executable, "build-guides.py"], cwd=site_dir, env=env, timeout=900)
    rc2, st = run(["git", "status", "--porcelain"], cwd=site_dir)
    built = rc == 0 and st.strip() == ""
    res.append({"suite": "build-guides.py reproduces the committed _dist", "ok": built,
                "last": (st.strip().splitlines()[:5] if st.strip() else o.strip().splitlines()[-1:])})
    if not built:
        return False, res
    cmds = [["node", "test.js"], ["node", "check-guides.js"], ["node", "tools/test_paying_nav.js"]]
    tools = os.path.join(site_dir, "tools")
    names = sorted(os.listdir(tools)) if os.path.isdir(tools) else []
    cmds += [["node", "tools/" + n] for n in names if n.startswith("test_") and n.endswith(".mjs")]
    cmds += [[sys.executable, "tools/" + n] for n in names if n.startswith("test_") and n.endswith(".py")]
    if "direct_inquiry_consistency.mjs" in names:
        cmds.append(["node", "tools/direct_inquiry_consistency.mjs"])
    ok = True
    for c in cmds:
        if not os.path.exists(os.path.join(site_dir, c[1])):
            continue
        try:
            rc, o = run(c, cwd=site_dir, env=env, timeout=900)
        except subprocess.TimeoutExpired:
            rc, o = 124, "timed out"
        last = [l for l in o.strip().splitlines() if l.strip()][-1:] or [""]
        cannot_start = rc != 0 and re.search(
            r"Cannot find module|Cannot find package|Executable doesn't exist|browserType\.launch|ModuleNotFoundError|ERR_MODULE_NOT_FOUND", o)
        state = "pass" if rc == 0 else ("not run here" if cannot_start else "FAIL")
        res.append({"suite": " ".join(os.path.basename(x) if x == sys.executable else x for x in c),
                    "ok": rc == 0, "state": state, "last": last[0][:200]})
        if state == "FAIL":
            ok = False
    core = [r for r in res if r["suite"] in ("node test.js", "node check-guides.js")]
    if len(core) != 2 or not all(r["ok"] for r in core):
        ok = False
    return ok, res


def build_plan(live_sha, head, record_holds=True):
    site = site_clone(head)
    rc, _ = run(["git", "cat-file", "-e", live_sha + "^{commit}"], cwd=site)
    if rc != 0:
        run(["git", "fetch", "-q", "--deepen", "3000", "origin", "main"], cwd=site, timeout=600)
    rc, _ = run(["git", "merge-base", "--is-ancestor", live_sha, head], cwd=site)
    if rc != 0:
        return {"action": "hold", "main": head, "live": live_sha,
                "reason": "the commit recorded as live is not an ancestor of main (history changed)"}
    rc, o = run(["git", "rev-list", "--first-parent", "--reverse", live_sha + ".." + head], cwd=site, check=True)
    commits = o.split()
    merges, skipped = [], []
    for c in commits:
        rc, files = run(["git", "diff", "--name-only", c + "^", c], cwd=site, check=True)
        names = set(files.split())
        if names and names <= BOOKKEEPING:
            skipped.append({"sha": c, "why": "publishing ledger only"})
            continue
        m, why = merged_by_owner(c)
        if not m:
            return {"action": "hold", "main": head, "live": live_sha, "commit": c,
                    "reason": "main holds a commit that is not a pull request merged by %s: %s" % (OWNER, why)}
        merges.append(m)
    rc, o = run(["git", "diff", "--name-status", live_sha, head, "--"] + PUBLISHED, cwd=site, check=True)
    changed = [l.split("\t") for l in o.strip().splitlines() if l.strip()]
    paths = [c[-1] for c in changed]
    plan = {"main": head, "live": live_sha, "merges": merges, "skipped": skipped,
            "changed_files": len(paths),
            "functions_changed": any(p.startswith("netlify") or p in NOT_SERVED for p in paths),
            "site_dir": site}
    if not paths:
        plan.update(action="record", reason="nothing that is published changed between the live commit and main")
        return plan
    pages = [p for p in paths if p.startswith("_dist/") and p not in NOT_SERVED]
    check_paths = pages[:MAX_PAGES]
    for must in ("_dist/index.html", "_dist/sitemap.xml"):
        if must not in check_paths:
            check_paths.append(must)
    plan["check_paths"] = check_paths
    same, rows = compare(site, check_paths)
    if same and not plan["functions_changed"]:
        plan.update(action="record", reason="the live site already serves this commit (someone deployed it)",
                    compared=len(rows))
        return plan
    ok, res = suites(site)
    plan["suites"] = res
    if not ok:
        bad = [r for r in res if not r["ok"] and r.get("state") != "not run here"]
        plan.update(action="hold", reason="not published: %s" % "; ".join(
            "%s: %s" % (r["suite"], (r["last"] if isinstance(r["last"], str) else " ".join(r["last"]))[:140]) for r in bad[:3]))
        return plan
    dep = os.path.join(WORK, "deploy")
    shutil.rmtree(dep, ignore_errors=True)
    os.makedirs(dep)
    run("git archive %s %s | tar -x -C %s" % (head, " ".join(PUBLISHED), dep), cwd=site, check=True)
    os.makedirs(os.path.join(dep, ".netlify"), exist_ok=True)
    with open(os.path.join(dep, ".netlify", "state.json"), "w") as fh:
        fh.write(json.dumps({"siteId": SITE_ID}) + "\n")
    rc, cnt = run("find . -type f | wc -l", cwd=dep)
    plan.update(action="publish", deploy_dir=dep, deploy_files=int(cnt.strip()), site_id=SITE_ID,
                reason="%d commit(s) merged by %s are not live" % (len(merges), OWNER))
    return plan


def cmd_check(a):
    head = main_head()
    live = read_live()
    live_sha = a.live or live.get("main")
    if not live_sha:
        out({"action": "hold", "main": head, "reason": "ops/live.json does not say which commit is live"}, 2)
    if head == live_sha:
        out({"action": "none", "main": head, "reason": "main is live"})
    held = live.get("held") or {}
    plan = build_plan(live_sha, head)
    plan["already_reported"] = bool(plan["action"] == "hold" and held.get("main") == head)
    os.makedirs(WORK, exist_ok=True)
    json.dump(plan, open(os.path.join(WORK, "plan.json"), "w"), indent=1)
    out(plan)


def cmd_verify(a):
    plan = json.load(open(os.path.join(WORK, "plan.json")))
    ok, rows = compare(plan["site_dir"], plan.get("check_paths", ["_dist/index.html", "_dist/sitemap.xml"]), tries=a.tries)
    extra = []
    for u in ("/?tour=form", "/guides/", "/privacy.html"):
        st, body = fetch(SITE + u, 2)
        extra.append({"url": u, "status": st, "bytes": len(body or b"")})
        ok = ok and st == 200
    res = {"verified": ok, "main": plan["main"], "pages": len(rows),
           "different": [r for r in rows if not r["same"]][:10], "also_loaded": extra, "utc": now()}
    json.dump(res, open(os.path.join(WORK, "verify.json"), "w"), indent=1)
    out(res, 0 if ok else 1)


def cmd_record(a):
    plan = json.load(open(os.path.join(WORK, "plan.json")))
    vf = os.path.join(WORK, "verify.json")
    ver = json.load(open(vf)) if os.path.exists(vf) else None
    if plan["action"] == "publish" and not (ver and ver.get("verified") and ver.get("main") == plan["main"]):
        out({"recorded": False, "reason": "verify has not passed for this commit; nothing recorded"}, 1)

    def change(live):
        hist = live.get("history") or []
        if live.get("main"):
            hist.insert(0, {k: live.get(k) for k in ("main", "deploy_id", "published_utc", "by", "how") if live.get(k)})
        live.update({"about": "Which commit of main is live on evanstonseniorcareguide.com. Written by the task 'ESCG publish after merge' (and by hand when someone else deployed).",
                     "main": plan["main"], "deploy_id": a.deploy_id or None, "published_utc": now(),
                     "by": a.by, "how": plan["action"] if plan["action"] != "publish" else "deployed after merge",
                     "merges": [{"pr": m["pr"], "merged_at": m["merged_at"]} for m in plan.get("merges", [])],
                     "pages_checked": (ver or {}).get("pages"), "history": hist[:20]})
        live.pop("held", None)
    sha = write_live(change, "Live: main %s (%s)" % (plan["main"][:7], a.deploy_id or plan["action"]))
    out({"recorded": True, "commit": sha, "main": plan["main"]})


def cmd_hold(a):
    plan = json.load(open(os.path.join(WORK, "plan.json")))

    def change(live):
        live["held"] = {"main": plan["main"], "reason": a.reason or plan.get("reason"), "utc": now(), "by": a.by}
    sha = write_live(change, "Not published: main %s (%s)" % (plan["main"][:7], (a.reason or plan.get("reason") or "")[:60]))
    out({"held": True, "commit": sha})


def cmd_selftest(a):
    """As if the newest merge were not live: the whole check, then the comparison with the live site."""
    head = main_head()
    site = site_clone(head)
    rc, o = run(["git", "rev-list", "--first-parent", "-n", "2", head], cwd=site, check=True)
    prev = o.split()[1]
    global compare
    real_compare = compare
    compare = lambda *x, **k: (False, [])  # pretend the site still serves the previous commit
    plan = build_plan(prev, head)
    compare = real_compare
    ok, rows = real_compare(site, plan.get("check_paths", ["_dist/index.html", "_dist/sitemap.xml"]))
    res = {"selftest": True, "utc": now(), "main": head, "pretended_live": prev, "action": plan["action"],
           "reason": plan.get("reason"), "merges": plan.get("merges"),
           "suites": [{"suite": r["suite"], "state": r.get("state", "pass" if r["ok"] else "FAIL")} for r in plan.get("suites", [])],
           "deploy_dir": plan.get("deploy_dir"), "deploy_files": plan.get("deploy_files"),
           "live_matches_main": ok, "pages_compared": len(rows), "different": [r for r in rows if not r["same"]][:5]}
    os.makedirs(WORK, exist_ok=True)
    json.dump(res, open(os.path.join(WORK, "selftest.json"), "w"), indent=1)
    out(res, 0 if (plan["action"] == "publish" and ok) else 1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("check"); s.add_argument("--live"); s.set_defaults(f=cmd_check)
    s = sub.add_parser("verify"); s.add_argument("--tries", type=int, default=12); s.set_defaults(f=cmd_verify)
    s = sub.add_parser("record"); s.add_argument("--deploy-id", default=""); s.add_argument("--by", default="ESCG publish after merge"); s.set_defaults(f=cmd_record)
    s = sub.add_parser("hold"); s.add_argument("--reason", default=""); s.add_argument("--by", default="ESCG publish after merge"); s.set_defaults(f=cmd_hold)
    s = sub.add_parser("selftest"); s.set_defaults(f=cmd_selftest)
    a = ap.parse_args()
    try:
        a.f(a)
    except SystemExit:
        raise
    except Exception as e:
        out({"action": "error", "error": str(e)[:600]}, 3)
