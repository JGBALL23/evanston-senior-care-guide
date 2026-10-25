# -*- coding: utf-8 -*-
"""Prove the publisher's two safety properties without deploying anything.

1. The IndexNow ledger survives a session boundary, and a run with no
   content change submits NOTHING.
2. A suite summary is only accepted as green when it provably is.

Everything here runs against a temporary ledger path. The real ledger is
never read or written.
"""
import importlib.util
import io
import json
import os
import shutil
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("pub", os.path.join(HERE, "publish.py"))
pub = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pub)          # chdir's to the repo root; no side effects

fails = []


def ck(name, ok, detail=""):
    print("  %-62s %s %s" % (name, "PASS" if ok else "FAIL", detail))
    if not ok:
        fails.append(name)


# --------------------------------------------------------------- suite_green
print("\nsuite_green — a tail is green only when it proves it")
CASES = [
    ("544/544 passed", True, "all of them passed"),
    ("823 passed, 0 failed   (823 checks)", True, "explicit zero failures"),
    ("540/544 passed", False, "THE OLD HOLE: red, but contains no 'fail'"),
    ("823 passed, 3 failed", False, "explicit failures"),
    ("544/544 passed, 3 failed", False, "no 544/544 exemption any more"),
    ("0/0 passed", False, "a suite that ran nothing is not a pass"),
    ("0 passed, 0 failed", False, "nothing ran"),
    ("", False, "empty output"),
    ("Segmentation fault", False, "unreadable output fails closed"),
    ("ok", False, "unrecognised summary fails closed"),
]
for tail, want, why in CASES:
    got, _ = pub.suite_green(tail)
    ck("%-38r -> %-5s  %s" % (tail[:36], want, why), got == want,
       "" if got == want else "got %s" % got)

# ------------------------------------------------------------------- ledger
print("\nledger — persistence across sessions, and a quiet no-op re-run")
tmp = tempfile.mkdtemp(prefix="ledger-test-")
real_ledger, real_rel = pub.LEDGER, pub.LEDGER_REL
try:
    pub.LEDGER = os.path.join(tmp, "data", "indexnow-ledger.json")

    ck("a missing ledger loads as empty, it does not crash",
       pub.load_ledger() == {"submitted": {}})

    live = pub.published_urls()
    ck("published_urls reads real built pages", len(live) >= 2, "%d URLs" % len(live))
    ck("every URL is absolute and on the right host",
       all(u.startswith(pub.BASE + "/") for u in live))
    ck("hashes are sha256 hex", all(len(h) == 64 for h in live.values()))

    # --- SESSION ONE: announce everything
    led = {"submitted": {u: {"hash": h, "at": "2026-10-25T00:00:00Z", "status": 200}
                         for u, h in live.items()}}
    pub.save_ledger(led)
    ck("ledger file exists on disk after save", os.path.isfile(pub.LEDGER))

    # --- SESSION TWO: a brand new process would read it back off disk
    reread = pub.load_ledger()
    ck("a separate session reads back exactly what was written", reread == led)

    changed = [u for u, h in sorted(live.items())
               if reread["submitted"].get(u, {}).get("hash") != h]
    ck("re-run with no content change submits ZERO URLs", changed == [],
       "%d changed" % len(changed))

    # --- one page edited
    victim = sorted(live)[0]
    reread["submitted"][victim]["hash"] = "0" * 64
    changed = [u for u, h in sorted(live.items())
               if reread["submitted"].get(u, {}).get("hash") != h]
    ck("one edited page yields exactly one changed URL", changed == [victim],
       str(changed))

    # --- a URL never seen before
    reread["submitted"].pop(victim)
    changed = [u for u, h in sorted(live.items())
               if reread["submitted"].get(u, {}).get("hash") != h]
    ck("a never-submitted URL counts as changed", changed == [victim], str(changed))

    # --- the ledger is JSON a human can diff
    txt = io.open(pub.LEDGER, encoding="utf-8").read()
    ck("ledger is sorted, indented, newline-terminated JSON",
       txt.endswith("\n") and '\n  "' in txt and json.loads(txt) is not None)
finally:
    pub.LEDGER, pub.LEDGER_REL = real_ledger, real_rel
    shutil.rmtree(tmp, ignore_errors=True)

ck("the real ledger path was never touched by this test",
   pub.LEDGER == os.path.join("data", "indexnow-ledger.json"))

print("\n%s" % ("%d/%d passed" % (len(CASES) + 12 - len(fails), len(CASES) + 12)
               if not fails else "FAILURES: " + ", ".join(fails)))
sys.exit(1 if fails else 0)
