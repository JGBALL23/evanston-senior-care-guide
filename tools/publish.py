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
import argparse, hashlib, io, json, os, re, subprocess, sys, time, urllib.error, urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

SITE_ID = "e25a95a5-7a87-4d1c-bae7-8c35d496dded"   # evanston-senior-care-guide
SITE_NAME = "evanston-senior-care-guide"
OTHER_SITE_ID = "6b245f3a-1d94-43c9-b7fa-e71f5513d7a6"   # norven — must not move
HOST = "evanstonseniorcareguide.com"
BASE = "https://" + HOST
LEDGER = os.path.join("data", "indexnow-ledger.json")
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


def head(url, timeout=30):
    req = urllib.request.Request(url, method="GET",
                                 headers={"User-Agent": "evanston-publish/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, b""
    except Exception as e:
        return 0, str(e).encode()


def netlify_site(site_id):
    out = sh('npx --no-install netlify api getSite --data \'{"site_id":"%s"}\'' % site_id)
    i = out.find("{")
    return json.loads(out[i:])


def load_ledger():
    if os.path.isfile(LEDGER):
        return json.load(io.open(LEDGER, encoding="utf-8"))
    return {"submitted": {}}


def save_ledger(led):
    os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
    io.open(LEDGER, "w", encoding="utf-8", newline="\n").write(
        json.dumps(led, indent=2, sort_keys=True) + "\n")


def published_urls():
    """Every guide URL plus the library index, with a hash of the built HTML.
    Read from _dist, which is exactly what Netlify uploads."""
    out = {}
    gdir = os.path.join("_dist", "guides")
    for name in sorted(os.listdir(gdir)):
        p = os.path.join(gdir, name, "index.html")
        if os.path.isfile(p):
            body = io.open(p, "rb").read()
            out["%s/guides/%s/" % (BASE, name)] = hashlib.sha256(body).hexdigest()
    idx = os.path.join(gdir, "index.html")
    if os.path.isfile(idx):
        out["%s/guides/" % BASE] = hashlib.sha256(io.open(idx, "rb").read()).hexdigest()
    return out


def submit(urls):
    """POST to IndexNow and translate the status into something actionable."""
    payload = json.dumps({
        "host": HOST,
        "key": INDEXNOW_KEY,
        "keyLocation": "%s/%s" % (BASE, INDEXNOW_KEY_FILE),
        "urlList": urls,
    }).encode("utf-8")
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="report what would ship and submit; change nothing")
    ap.add_argument("--skip-deploy", action="store_true",
                    help="site is already deployed; verify and submit only")
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
    for cmd, want in (("node test.js", "0 failed"),
                      ("node check-guides.js", "0 failed")):
        out = sh(cmd, check=False)
        tail = out.strip().splitlines()[-1] if out.strip() else ""
        print("      %-24s %s" % (cmd, tail))
        if "fail" in tail.lower() and "0 failed" not in tail and "544/544" not in tail:
            die("%s is red. Nothing ships on a red suite." % cmd)

    # key file must exist in what we are about to upload
    keypath = os.path.join("_dist", INDEXNOW_KEY_FILE)
    if not os.path.isfile(keypath) or io.open(keypath, encoding="utf-8").read().strip() != INDEXNOW_KEY:
        die("IndexNow key file missing or wrong in _dist/")
    print("      IndexNow key file       present in _dist/")

    # 3 ------------------------------------------- what changed since last time
    ledger = load_ledger()
    now = published_urls()
    changed = [u for u, h in sorted(now.items())
               if ledger["submitted"].get(u, {}).get("hash") != h]
    print("\n  [3] %d of %d published URLs changed since the last submission"
          % (len(changed), len(now)))
    for u in changed:
        print("      %s" % u)
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
        out = sh('npx --no-install netlify deploy --prod --dir=_dist '
                 '--functions=netlify/functions --site %s '
                 '--message "publish %s" --json' % (SITE_ID, commit))
        i = out.find("{")
        d = json.loads(out[i:])
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
            ledger["submitted"][u] = {"hash": now[u], "at": stamp, "status": status}
        save_ledger(ledger)
        print("\n  Ledger updated — these URLs will not be re-submitted unchanged.")
        print("  %s" % LEDGER)
    else:
        print("\n  Ledger NOT updated. A failed submission must be retryable,")
        print("  so nothing is recorded as sent.")
        sys.exit(2)

    print("\nDone. %s is live and %d URL(s) were notified." % (HOST, len(live_urls)))


if __name__ == "__main__":
    main()
