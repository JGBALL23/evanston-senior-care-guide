# -*- coding: utf-8 -*-
"""
publish.py — the one command that puts approved guides in front of families.

    python tools/publish.py --dry-run     # show what WOULD ship, change nothing
    python tools/publish.py               # deploy, verify, notify IndexNow

WHY THIS FILE EXISTS. Until now "the publishing workflow" was a human typing
a netlify command into a chat window. That worked, and it also meant the
--site flag was retyped every time — and this machine's Netlify CLI resolves
an unflagged deploy from this directory to the NORVEN site (norvenph.com),
not Evanston. One forgotten flag publishes a senior-care site over a massage
business. The site ID is baked in below and asserted against the name the
API returns before anything is uploaded.

ORDER OF OPERATIONS, and every step is a gate:

  1. Refuse unless on `main`, clean, and level with origin/main. Deploying a
     dirty tree ships files nobody reviewed.
  2. Rebuild and run the full suites. A red suite stops the deploy.
  3. Snapshot the OTHER Netlify site's published deploy id. Compare it again
     at the end. That is the only hard proof norvenph.com was untouched.
  4. Deploy to the Evanston site id, explicitly.
  5. Verify each changed URL returns 200 on the real domain before telling a
     search engine it exists. Submitting a 404 is worse than not submitting.
  6. Submit ONLY changed URLs to IndexNow, then record what was sent.

WHAT COUNTS AS CHANGED. data/indexnow-ledger.json maps each URL to a hash of
the HTML actually published. A guide is submitted when its hash is new or
different. Rewording one article does not re-submit the other nine, and a
rebuild that produces identical bytes submits nothing at all.

THE DAILY ROUTINE NEVER REACHES THIS FILE. It pushes to `drafts`, is
forbidden from touching `main` or calling Netlify, and nothing here runs on a
schedule. Drafts are never submitted to IndexNow because drafts are never
deployed.
"""
import argparse, hashlib, io, json, os, re, shutil, subprocess, sys, time
import urllib.error, urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

SITE_ID = "e25a95a5-7a87-4d1c-bae7-8c35d496dded"   # evanston-senior-care-guide
SITE_NAME = "evanston-senior-care-guide"
OTHER_SITE_ID = "6b245f3a-1d94-43c9-b7fa-e71f5513d7a6"   # norven — must not move
HOST = "evanstonseniorcareguide.com"
BASE = "https://" + HOST
LEDGER = os.path.join("data", "indexnow-ledger.json")
LEDGER_REL = "data/indexnow-ledger.json"   # git wants forward slashes
INDEXNOW_ENDPOINT = "https://api.indexnow.org/IndexNow"



def _key_from_generator():
    """Read the key out of build-guides.py rather than repeating it here.

    build-guides.py cannot be imported (the hyphen is not a valid module
    name), so the constant is parsed. One definition, one place to change
    it, and no chance of this file and the generator disagreeing about
    which key the site is serving."""
    src = io.open(os.path.join(ROOT, "build-guides.py"), encoding="utf-8").read()
    m = re.search(r'^INDEXNOW_KEY = "([0-9a-f]{8,128})"', src, re.M)
    if not m:
        raise SystemExit("could not read INDEXNOW_KEY from build-guides.py")
    return m.group(1)


INDEXNOW_KEY = _key_from_generator()
INDEXNOW_KEY_FILE = INDEXNOW_KEY + ".txt"


def sh(cmd, check=True):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if check and r.returncode != 0:
        die("command failed: %s\n%s%s" % (cmd, r.stdout, r.stderr))
    return (r.stdout + r.stderr).strip()


def die(msg):
    print("\n  STOP: " + msg)
    sys.exit(1)


CURL = shutil.which("curl") or shutil.which("curl.exe")


def _curl(args, data=None, timeout=45):
    """One HTTP round trip through curl, returning (status, body).

    curl is preferred over urllib because urllib's bundled CA store in this
    environment contains an expired root: every https request raised
    CERTIFICATE_VERIFY_FAILED, so a live page that answers 200 was read as
    'HTTP 0'. That is not a cosmetic bug -- it stopped the run one step
    AFTER a successful production deploy, and it would have made the
    IndexNow POST unsendable too. curl uses the operating system's trust
    store instead.

    Certificate verification stays ON. No flag that skips it is ever passed
    here, and a gate in check-guides.js fails the build if one appears. A
    certificate error must stop the publish, not be waved through."""
    cmd = [CURL, "-s", "-L", "--max-time", str(timeout),
           "-A", "evanston-publish/1.0", "-w", "\n%{http_code}"] + args
    r = subprocess.run(cmd, capture_output=True, input=data, shell=False)
    raw = r.stdout or b""
    i = raw.rfind(b"\n")
    if i < 0:
        return 0, (r.stderr or raw)[:300]
    try:
        return int(raw[i + 1:].strip()), raw[:i]
    except ValueError:
        return 0, (r.stderr or raw)[:300]


def head(url, timeout=30):
    if CURL:
        return _curl([url], timeout=timeout)
    req = urllib.request.Request(url, method="GET",
                                 headers={"User-Agent": "evanston-publish/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, b""
    except Exception as e:
        return 0, str(e).encode()


NPX = shutil.which("npx") or shutil.which("npx.cmd")


def netlify(args, check=True):
    """Run the Netlify CLI as an ARGUMENT LIST, never through a shell.

    The first version of this file passed JSON to the CLI inside single
    quotes through shell=True. On Windows that shell is cmd.exe, which does
    not treat ' as a quote, so the CLI received a literal '{site_id:... and
    died on invalid JSON. Both the site-identity assertion and the
    norven-did-not-move proof ran through that call, which means the
    publisher would have stopped dead one step before the deploy. No shell,
    no quoting, nothing for a platform to reinterpret."""
    if not NPX:
        die("npx is not on PATH — cannot reach the Netlify CLI.")
    r = subprocess.run([NPX, "--no-install", "netlify"] + args,
                       capture_output=True, text=True,
                       encoding="utf-8", errors="replace", shell=False)
    out = ((r.stdout or "") + (r.stderr or "")).strip()
    if check and r.returncode != 0:
        die("netlify %s failed:\n%s" % (" ".join(args), out))
    return out


def netlify_json(args):
    """Decode the FIRST JSON object the CLI prints and ignore the rest.

    json.loads on everything from the first brace onward raised
    'Extra data' the moment the CLI appended anything after the object --
    an update notice, a second document, a stray warning. raw_decode stops
    at the end of the first value, so trailing noise cannot break a deploy."""
    out = netlify(args)
    i = out.find("{")
    if i < 0:
        die("netlify %s returned no JSON:\n%s" % (" ".join(args), out))
    try:
        return json.JSONDecoder().raw_decode(out, i)[0]
    except ValueError as e:
        die("netlify %s returned unparseable JSON (%s):\n%s"
            % (" ".join(args), e, out[:400]))


def netlify_site(site_id):
    return netlify_json(["api", "getSite",
                         "--data", json.dumps({"site_id": site_id})])


LEDGER_VERSION = 2

LEDGER_NOTE = (
    "kind=submitted means IndexNow accepted this URL and the status field is "
    "the real HTTP code it answered. kind=baseline means the URL was already "
    "live and discoverable through the sitemap before IndexNow existed; it "
    "was recorded so it stops counting as new, and it was NEVER submitted. A "
    "baseline entry carries no status, because no request was ever made."
)


def load_ledger():
    """Read the ledger, upgrading the v1 shape in memory.

    v1 was {"submitted": {url: {...}}} -- one bucket, which could not say
    whether an entry represented a real submission or merely a URL we had
    decided not to announce. v2 keeps one map and tags every entry with
    `kind`, so a baseline can never be mistaken for a successful request."""
    if not os.path.isfile(LEDGER):
        return {"version": LEDGER_VERSION, "note": LEDGER_NOTE, "entries": {}}
    led = json.load(io.open(LEDGER, encoding="utf-8"))
    if "entries" in led:
        led.setdefault("version", LEDGER_VERSION)
        led["note"] = LEDGER_NOTE
        return led
    entries = {}
    for url, row in (led.get("submitted") or {}).items():
        row = dict(row)
        row["kind"] = "submitted"       # v1 only ever held real submissions
        entries[url] = row
    return {"version": LEDGER_VERSION, "note": LEDGER_NOTE, "entries": entries}


def known_hash(led, url):
    return (led["entries"].get(url) or {}).get("hash")


def baseline_row(content_hash, stamp, live_sha):
    """Build a baseline entry. Deliberately has NO status field: no HTTP
    request was made, so inventing a code would be a false receipt."""
    return {
        "hash": content_hash,
        "kind": "baseline",
        "at": stamp,
        "live_text_sha": live_sha,
        "why": ("already live and in the sitemap before IndexNow existed; "
                "recorded so it is not treated as new. Never submitted."),
    }


def live_text_sha(body):
    """Fingerprint a live page by its visible text, not its bytes.

    Raw bytes cannot be compared against _dist, because Netlify rewrites the
    HTML it serves: it converts href="/privacy.html" to href='/privacy',
    swaps attribute quoting, and injects a RUM script whose token embeds the
    DEPLOY ID. That token changes on every single deploy, so a live-byte
    hash would mark all eleven pages as changed after any publish -- the
    exact false positive this ledger exists to prevent.

    Stripping tags and collapsing whitespace survives all of that while
    still catching a real editorial change, which is what we actually care
    about verifying. Markup-only changes still move the _dist hash, which is
    what drives submission."""
    text = body.decode("utf-8", "replace")
    text = re.sub(r"(?is)<script\b.*?</script>", " ", text)
    text = re.sub(r"(?is)<style\b.*?</style>", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def local_text_sha(path):
    return live_text_sha(io.open(path, "rb").read())


def save_ledger(led):
    os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
    io.open(LEDGER, "w", encoding="utf-8", newline="\n").write(
        json.dumps(led, indent=2, sort_keys=True) + "\n")


def commit_ledger(stamp):
    """A ledger is only a duplicate-guard if it OUTLIVES the session that
    wrote it. Writing it to disk is not enough: an uncommitted ledger means a
    fresh clone re-submits every URL it has already announced, and it leaves
    the tree dirty so the NEXT run's own clean-gate refuses to start. So the
    ledger is committed and pushed as the last act of a successful run."""
    if not sh("git status --porcelain -- " + LEDGER_REL, check=False).strip():
        return "unchanged"
    sh("git add -- " + LEDGER_REL)
    sh('git -c core.editor=true commit -q -m "IndexNow ledger: recorded '
       'submissions at %s" -- %s' % (stamp, LEDGER_REL))
    sh("git push -q origin main")
    return sh("git rev-parse --short HEAD")


def suite_green(tail):
    """Prove a suite passed. Exactly two summary shapes are recognised and
    NOTHING else -- an unreadable tail is a failure, not a pass.

    The gate this replaces only searched for the word 'fail'. A red test.js
    summarises as "<ran>/<total> passed" with the two numbers unequal, which
    contains no 'fail' at all, so it sailed straight through. That gate also
    carried a literal pass-count exemption, which is the hardcoded-inventory
    mistake this project has already paid for twice. Counts are compared
    against each other here, never against a constant. The cases are pinned
    in tools/test_publish.py."""
    m = re.match(r"^(\d+)/(\d+) passed$", tail)
    if m:
        ran, total = int(m.group(1)), int(m.group(2))
        return (ran == total and ran > 0), "%d of %d passed" % (ran, total)
    m = re.search(r"(\d+) passed, (\d+) failed", tail)
    if m:
        passed, failed = int(m.group(1)), int(m.group(2))
        return (failed == 0 and passed > 0), "%d failed" % failed
    return False, "unrecognised summary line"


def published_paths():
    """Every published URL mapped to the file in _dist that serves it.

    Derived by walking _dist, never from a list. A guide added by the daily
    routine appears here the moment it is built, which is what makes the
    submission automatic with no URL to pick by hand."""
    out = {}
    gdir = os.path.join("_dist", "guides")
    for name in sorted(os.listdir(gdir)):
        p = os.path.join(gdir, name, "index.html")
        if os.path.isfile(p):
            out["%s/guides/%s/" % (BASE, name)] = p
    idx = os.path.join(gdir, "index.html")
    if os.path.isfile(idx):
        out["%s/guides/" % BASE] = idx
    return out


def published_urls():
    """Every published URL with a hash of the built HTML. Read from _dist,
    which is exactly what Netlify uploads."""
    return dict((u, hashlib.sha256(io.open(p, "rb").read()).hexdigest())
                for u, p in published_paths().items())


def submit(urls):
    """POST to IndexNow and translate the status into something actionable."""
    payload = json.dumps({
        "host": HOST,
        "key": INDEXNOW_KEY,
        "keyLocation": "%s/%s" % (BASE, INDEXNOW_KEY_FILE),
        "urlList": urls,
    }).encode("utf-8")
    if CURL:
        status, body = _curl(
            ["-X", "POST", "-H", "Content-Type: application/json; charset=utf-8",
             "--data-binary", "@-", INDEXNOW_ENDPOINT], data=payload)
        return status, body.decode("utf-8", "replace")[:300]
    req = urllib.request.Request(
        INDEXNOW_ENDPOINT, data=payload, method="POST",
        headers={"Content-Type": "application/json; charset=utf-8",
                 "User-Agent": "evanston-publish/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            return r.status, r.read().decode("utf-8", "replace")[:300]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")[:300]
    except Exception as e:
        return 0, str(e)[:300]


MEANING = {
    200: "OK — URLs accepted.",
    202: "Accepted — URLs received, key validation still pending. Normal on a first submission.",
    400: "Bad request — the JSON payload is malformed. Nothing was accepted.",
    403: "Forbidden — the key file could not be read, or does not contain the key.",
    422: "Unprocessable — a URL does not belong to this host, or the key does not match.",
    429: "Too many requests — throttled. Wait and retry; do not loop.",
    0:   "No response — network error reaching the endpoint.",
}


def do_baseline(ledger, now, paths):
    """Record already-live URLs so they stop counting as new. Submits nothing.

    WHY THIS EXISTS. IndexNow arrived after ten guides were already live and
    in the sitemap. Against an empty ledger all of them read as 'changed',
    so the next ordinary publish would have announced eleven URLs when only
    one was new -- and the owner's standing instruction is not to resubmit
    unchanged guides. The alternative was passing --only by hand forever,
    which is not automation, it is a chore with a deadline.

    WHAT IT WILL NOT DO. It never calls IndexNow, never deploys, and never
    writes a status field. It refuses to baseline a URL it cannot prove is
    live right now, and it refuses to touch a URL already in the ledger, so
    a real submission can never be overwritten by a baseline."""
    fresh = [u for u in sorted(now) if u not in ledger["entries"]]
    print("\n  [B] baseline: %d of %d URLs are not yet recorded"
          % (len(fresh), len(now)))
    if not fresh:
        print("      nothing to baseline — every URL is already recorded")
        return 0, []

    bad = []
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    for u in fresh:
        code, body = head(u)
        live = live_text_sha(body) if code == 200 else None
        mine = local_text_sha(paths[u])
        ok = code == 200 and live == mine
        print("      %-4s %-7s %s" % (code, "match" if ok else "MISMATCH",
                                      u[len(BASE):]))
        if not ok:
            bad.append((u, code))
            continue
        ledger["entries"][u] = baseline_row(now[u], stamp, live)
    if bad:
        die("%d URL(s) could not be proven live and identical, so they were\n"
            "        NOT baselined: %s\n"
            "        A baseline must describe reality or it is a lie in a file."
            % (len(bad), ", ".join("%s (%s)" % (u[len(BASE):], c)
                                   for u, c in bad)))
    return len(fresh), fresh


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="report what would ship and submit; change nothing")
    ap.add_argument("--skip-deploy", action="store_true",
                    help="site is already deployed; verify and submit only")
    ap.add_argument("--only", metavar="URL", default=None,
                    help="submit just this one changed URL; the rest stay "
                         "unrecorded and go out on the next run")
    ap.add_argument("--baseline", action="store_true",
                    help="one-time: record already-live URLs as baseline so "
                         "they stop counting as new. Deploys nothing and "
                         "submits nothing.")
    args = ap.parse_args()

    print("=" * 70)
    print("PUBLISH  ->  %s   (site %s)" % (HOST, SITE_ID))
    print("=" * 70)

    # 1 ----------------------------------------------------- repo preconditions
    branch = sh("git rev-parse --abbrev-ref HEAD")
    if branch != "main":
        die("on branch '%s'. Publishing happens from main only." % branch)
    dirty = [l for l in sh("git status --porcelain", check=False).splitlines()
             if l and not l.startswith("??")]
    if dirty:
        die("working tree is dirty:\n    " + "\n    ".join(dirty))
    sh("git fetch -q origin")
    if sh("git rev-parse HEAD") != sh("git rev-parse origin/main"):
        die("main and origin/main disagree. Push or pull first.")
    commit = sh("git rev-parse --short HEAD")
    print("\n  [1] main is clean and level at %s" % commit)

    # 2 ------------------------------------------------------------- the gates
    print("  [2] rebuilding and running the suites")
    sh("python build-guides.py")
    drift = [l for l in sh("git status --porcelain", check=False).splitlines()
             if l and not l.startswith("??")]
    if drift:
        die("rebuilding changed committed files — commit the rebuild first:\n    "
            + "\n    ".join(drift))
    for cmd in ("node test.js", "node check-guides.js",
                "python tools/test_publish.py"):
        out = sh(cmd, check=False)
        tail = out.strip().splitlines()[-1] if out.strip() else ""
        ok, why = suite_green(tail)
        print("      %-24s %s" % (cmd, tail))
        if not ok:
            die("%s is not provably green (%s). Nothing ships on a red suite."
                % (cmd, why))

    # key file must exist in what we are about to upload
    keypath = os.path.join("_dist", INDEXNOW_KEY_FILE)
    if not os.path.isfile(keypath) or io.open(keypath, encoding="utf-8").read().strip() != INDEXNOW_KEY:
        die("IndexNow key file missing or wrong in _dist/")
    print("      IndexNow key file       present in _dist/")

    # 3 ------------------------------------------- what changed since last time
    ledger = load_ledger()
    now = published_urls()

    if args.baseline:
        if args.only:
            die("--baseline and --only are different jobs. Pick one.")
        added, urls = do_baseline(ledger, now, published_paths())
        if added:
            save_ledger(ledger)
            print("\n  Baselined %d URL(s). NOTHING was submitted to IndexNow"
                  " and nothing was deployed." % added)
            print("  committed as %s" % commit_ledger(
                time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())))
        kinds = {}
        for row in ledger["entries"].values():
            kinds[row.get("kind")] = kinds.get(row.get("kind"), 0) + 1
        print("  ledger now holds %s"
              % ", ".join("%d %s" % (n, k) for k, n in sorted(kinds.items())))
        return

    changed = [u for u, h in sorted(now.items()) if known_hash(ledger, u) != h]
    print("\n  [3] %d of %d published URLs changed since the last submission"
          % (len(changed), len(now)))
    for u in changed:
        print("      %s" % u)
    if args.only:
        if args.only not in changed:
            die("--only %s is not in the changed list. Refusing to invent a\n"
                "        submission for a URL that did not change." % args.only)
        held = len(changed) - 1
        changed = [args.only]
        print("      --only: submitting 1, holding %d for the next run" % held)
    if not changed:
        print("      nothing to notify — IndexNow will not be called")

    # 4 -------------------------------------------------- the other site, before
    other_before = (netlify_site(OTHER_SITE_ID).get("published_deploy") or {}).get("id")
    print("\n  [4] norven published deploy before: %s" % other_before)

    if args.dry_run:
        print("\n  DRY RUN — no deploy, no submission. Nothing changed.")
        return

    # 5 ------------------------------------------------------------- the deploy
    if args.skip_deploy:
        print("\n  [5] --skip-deploy: using the site as already published")
    else:
        site = netlify_site(SITE_ID)
        if site.get("name") != SITE_NAME:
            die("site %s is named '%s', expected '%s'. Refusing to deploy."
                % (SITE_ID, site.get("name"), SITE_NAME))
        print("\n  [5] deploying to %s (%s)" % (site.get("name"), SITE_ID))
        d = netlify_json(["deploy", "--prod", "--dir=_dist",
                          "--functions=netlify/functions",
                          "--site", SITE_ID,
                          "--message", "publish %s" % commit, "--json"])
        if d.get("site_id") != SITE_ID:
            die("deploy reported site_id %s — expected %s" % (d.get("site_id"), SITE_ID))
        print("      deploy_id %s" % d.get("deploy_id"))

    # 6 ------------------------------------------- the other site, after
    other_after = (netlify_site(OTHER_SITE_ID).get("published_deploy") or {}).get("id")
    print("  [6] norven published deploy after : %s   %s"
          % (other_after, "UNCHANGED" if other_after == other_before else "!! MOVED !!"))
    if other_after != other_before:
        die("the other site's published deploy moved. Investigate before anything else.")

    # 7 --------------------------------------------- key file, live and readable
    code, body = head("%s/%s" % (BASE, INDEXNOW_KEY_FILE))
    ok_key = code == 200 and body.decode("utf-8", "replace").strip() == INDEXNOW_KEY
    print("  [7] key file live: HTTP %s, contents %s"
          % (code, "match" if ok_key else "MISMATCH"))
    if not ok_key:
        die("the key file is not publicly readable. IndexNow would answer 403.")

    # 8 ---------------------------------------- every URL must be live first
    if not changed:
        print("\n  Nothing changed. No IndexNow request made.")
        return
    live, dead = [], []
    for u in changed:
        c, _ = head(u)
        (live if c == 200 else dead).append((u, c))
        print("      %-4s %s" % (c, u))
    if dead:
        print("\n  %d URL(s) are not live and will NOT be submitted." % len(dead))
    live_urls = [u for u, _ in live]
    if not live_urls:
        die("no changed URL returned 200. Nothing submitted.")

    # 9 ------------------------------------------------------------- submit
    print("\n  [9] submitting %d URL(s) to IndexNow" % len(live_urls))
    status, body = submit(live_urls)
    print("      HTTP %s — %s" % (status, MEANING.get(status, "unexpected status")))
    if body.strip():
        print("      body: %s" % body.strip())

    if status in (200, 202):
        stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        for u in live_urls:
            ledger["entries"][u] = {"hash": now[u], "kind": "submitted",
                                    "at": stamp, "status": status}
        save_ledger(ledger)
        print("\n  Ledger updated — these URLs will not be re-submitted unchanged.")
        print("  %s" % LEDGER)
        print("  committed as %s — the guard now survives this session"
              % commit_ledger(stamp))
    else:
        print("\n  Ledger NOT updated. A failed submission must be retryable,")
        print("  so nothing is recorded as sent.")
        sys.exit(2)

    print("\nDone. %s is live and %d URL(s) were notified." % (HOST, len(live_urls)))


if __name__ == "__main__":
    main()
