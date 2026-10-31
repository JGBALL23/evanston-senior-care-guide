# -*- coding: utf-8 -*-
"""Workflow #4 walkthrough: both guide pathways, mobile and desktop.

Submits NOTHING to production. The form's client-side validation is
exercised against the real DOM; fetch is stubbed before the document
loads, so every POST is captured in the page and none can leave it.

Asserts the POSTED BODY, not the rendered DOM. That distinction is the
whole reason this file exists: the interest dropdown rendered correctly,
preselected correctly, and silently posted "unsure" for every visitor
between 2026-10-26 and the form="plan-form" fix, because it sits outside
the <form> element. A DOM check cannot see that. Every interest value is
now walked end to end, not just the preselected one.

Usage: wf4_direct_inquiry.py [base-url]   (default: local _dist server)"""
import asyncio, base64, functools, http.server, json, os, socketserver
import subprocess, sys, threading, time, urllib.request
import websockets

# Every harness announces itself with one fixed User-Agent so the host's
# request log can exclude it by exact match. A test run must never be
# counted as a family. The string is identical in every harness; test.js
# checks that it stays so.
HARNESS_UA = "ESCG-harness/1 (automated test; +https://evanstonseniorcareguide.com/)"

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
PORT, CDP = 8903, 9385
os.makedirs("shots", exist_ok=True)
fails = []

# Every option in the dropdown, and what careLevel each pathway sends
# alongside it. Read from app.js rather than typed here, so adding an
# option to the site cannot leave this harness testing a stale list.
APP = open("app.js", encoding="utf-8").read()
_block = APP.split("const INTERESTS = [")[1].split("];")[0]
INTEREST_IDS = [line.split('id: "')[1].split('"')[0]
                for line in _block.splitlines() if 'id: "' in line]
assert len(INTEREST_IDS) >= 4, INTEREST_IDS


def ck(n, ok, d=""):
    print("   %-58s %s %s" % (n, "PASS" if ok else "FAIL", d))
    if not ok:
        fails.append(n)


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


LIVE = sys.argv[1] if len(sys.argv) > 1 else ""
srv = None
if LIVE:
    BASE = LIVE.rstrip("/")
else:
    srv = socketserver.TCPServer(("127.0.0.1", PORT),
                                 functools.partial(Quiet, directory="_dist"))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    BASE = "http://127.0.0.1:%d" % PORT
print("TARGET: %s" % BASE)
print("INTERESTS UNDER TEST: %s" % ", ".join(INTEREST_IDS))

CHROME = None
for p in (r"C:\Program Files\Google\Chrome\Application\chrome.exe",
          r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"):
    if os.path.isfile(p):
        CHROME = p
proc = subprocess.Popen(
    [CHROME, "--headless=new", "--user-agent=" + HARNESS_UA, "--disable-gpu", "--no-sandbox", "--no-first-run",
     "--remote-debugging-port=%d" % CDP, "about:blank"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
for _ in range(60):
    try:
        urllib.request.urlopen("http://localhost:%d/json/version" % CDP, timeout=1).read()
        break
    except Exception:
        time.sleep(0.5)
raw = urllib.request.urlopen("http://localhost:%d/json/list" % CDP, timeout=10).read()
WS = [t["webSocketDebuggerUrl"] for t in json.loads(raw.decode())
      if t.get("type") == "page"][0]

# Every POST is captured, never sent. Nothing can reach production.
STUB = """
window.__posts = [];
window.__beacons = [];
window.fetch = function (url, opts) {
  var u = String(url);
  if (opts && opts.method === 'POST') {
    window.__posts.push({ url: u, body: (opts && opts.body) || '' });
    return Promise.resolve(new Response(
      JSON.stringify({ ok: true, stored: true, submissionId: 'TEST-LOCAL' }),
      { status: 200, headers: { 'content-type': 'application/json' } }));
  }
  window.__beacons.push(u);
  return Promise.resolve(new Response('', { status: 200 }));
};
"""

FILL = """(function (interest) {
  var f = document.querySelector('#plan-visit form');
  f.elements.firstName.value = 'Test';
  f.elements.lastName.value = 'Visitor';
  f.elements.email.value = 't@example.com';
  f.elements.phone.value = '';
  if (interest) document.getElementById('plan-interest').value = interest;
  document.getElementById('plan-consent').checked = true;
  f.querySelector('button[type=submit]').click();
}(%s))"""

# Distance a thumb travels past the disclosures before it can type.
# Gated against the viewport rather than a pixel budget nobody maintains:
# the first contact field has to be reachable inside one screen of the
# section top. It was 1199px down an 844px screen before this.
REACH = """(function () {
  var sec = document.getElementById('plan-visit');
  var first = document.querySelector('#plan-form input[name=firstName]');
  var consent = document.getElementById('plan-consent');
  var who = document.querySelector('.plan__who');
  if (!sec || !first) return null;
  var top = sec.getBoundingClientRect().top;
  var o = function (el) {
    return el ? Math.round(el.getBoundingClientRect().top - top) : -1; };
  return { firstName: o(first), consent: o(consent), who: o(who),
           viewport: window.innerHeight };
}())"""

# The hint that belongs to the interest control, reached THROUGH the
# control rather than by position. There are two .plan__hint nodes in the
# section now -- the other one says "Give at least one" under the contact
# fields -- and querySelector returned that one after the restructure.
# A positional selector made one assertion pass vacuously: a check that
# the hint does not mention a result trivially held for a hint about
# phone numbers. Returns null if the control is absent, so a missing
# hint fails rather than reading as empty.
HINT = """(function () {
  var sel = document.getElementById('plan-interest');
  if (!sel) return null;
  var h = sel.closest('label').querySelector('.plan__hint');
  return h ? h.textContent.replace(/\s+/g, ' ').trim() : null;
}())"""

DEVICES = [("mobile", 390, 844, True), ("desktop", 1280, 900, False)]


async def main():
    n = [0]
    async with websockets.connect(WS, max_size=70 * 1024 * 1024) as ws:
        async def call(m, **p):
            n[0] += 1
            i = n[0]
            await ws.send(json.dumps({"id": i, "method": m, "params": p}))
            while True:
                r = json.loads(await ws.recv())
                if r.get("id") == i:
                    return r.get("result", {})

        async def js(e):
            r = await call("Runtime.evaluate", expression=e,
                           returnByValue=True, awaitPromise=True)
            return r.get("result", {}).get("value")

        async def shot(name):
            s = await call("Page.captureScreenshot", format="png")
            open(os.path.join("shots", name), "wb").write(
                base64.b64decode(s["data"]))

        async def goto(path):
            """Always lands on a genuinely fresh document.

            Navigating to a URL identical to the current one -- which the
            interest loop does five times -- is a same-document fragment
            change in Chrome. The page does not reload, the init script
            does not re-run, and window.__posts keeps the PREVIOUS
            iteration's body. Four checks read that stale entry and
            reported the first iteration's value as every iteration's
            value. about:blank forces the document swap; the assertion
            below makes a stale read fail loudly instead of passing by
            coincidence."""
            await call("Page.navigate", url="about:blank")
            await asyncio.sleep(0.15)
            await call("Page.navigate", url=BASE + path)
            for _ in range(120):
                if await js("document.readyState") == "complete":
                    break
                await asyncio.sleep(0.1)
            await asyncio.sleep(0.6)
            stale = await js("window.__posts ? window.__posts.length : -1")
            assert stale == 0, (
                "not a fresh document: %r posts already buffered at %s"
                % (stale, path))

        async def walk_assessment(choices):
            await js("document.querySelector('[data-aud=" + chr(34) + "parent"
                     + chr(34) + "]').click()")
            await asyncio.sleep(0.35)
            for c in choices:
                await js("document.querySelectorAll('.opt')[%d].click()" % c)
                await asyncio.sleep(0.28)

        await call("Page.enable")
        await call("Runtime.enable")
        await call("Page.addScriptToEvaluateOnNewDocument", source=STUB)

        for label, w, h, mob in DEVICES:
            await call("Emulation.setDeviceMetricsOverride", width=w, height=h,
                       deviceScaleFactor=2 if mob else 1, mobile=mob)
            await call("Emulation.setTouchEmulationEnabled", enabled=mob)

            print("\n=== %s: the guide offers two ways ===" % label.upper())
            await goto("/guides/independent-living-evanston/")
            opts = await js("[...document.querySelectorAll('.fork__opt')]"
                            ".map(a=>a.getAttribute('href'))")
            ck("%s: two pathway links on the guide" % label,
               sorted(opts or []) == ["/?from=il-guide#assessment",
                                      "/?tour=independent#plan-visit"],
               ",".join(opts or []))
            ck("%s: both are 48px+ targets" % label,
               await js("(function(){var a=document.querySelectorAll('.fork__opt');"
                        "var m=99;for(var i=0;i<a.length;i++){var r=a[i]"
                        ".getBoundingClientRect();if(r.height<m)m=r.height;}"
                        "return m>=48;}())"))
            body = await js("document.body.innerText")
            ck("%s: article reads without touching either" % label,
               "Neither is required to finish reading" in (body or ""))
            ck("%s: the guide says which route asks for what" % label,
               "asks how to reach you" in (body or ""))
            ck("%s: the guide explains no backend record-keeping" % label,
               "notification" not in (body or "") and
               "records no assessment" not in (body or ""))
            ck("%s: no horizontal scroll" % label,
               not await js("document.documentElement.scrollWidth > "
                            "document.documentElement.clientWidth + 1"))
            await js("document.querySelector('.fork')"
                     ".scrollIntoView({behavior:'instant'})")
            await asyncio.sleep(0.4)
            await shot("wf4-%s-01-guide-fork.png" % label)

            print("\n=== %s: pathway 2, straight to the form ===" % label.upper())
            await goto("/?tour=independent#plan-visit")
            ck("%s: no assessment is shown" % label,
               (await js("document.querySelectorAll('.opt[data-i]').length")) == 0)
            ck("%s: the page says no assessment is needed" % label,
               (await js("(document.querySelector('.res__name')||{})"
                         ".textContent")) == "No assessment needed")
            quiz = await js("document.getElementById('quiz').innerText")
            ck("%s: it states nothing is assumed or guessed" % label,
               "assumed or guessed" in (quiz or ""))
            ck("%s: no backend wording in visitor copy" % label,
               "recorded" not in (quiz or "") and
               "notification" not in (quiz or ""),
               "")
            ck("%s: the form is present without any answers" % label,
               await js("!!document.getElementById('plan-visit')"))
            ck("%s: interest preselected to Independent Living" % label,
               (await js("(document.getElementById('plan-interest')||{}).value"))
               == "independent")
            hint = await js(HINT)
            ck("%s: the interest hint was actually found" % label,
               bool(hint) and len(hint) > 30, repr(hint)[:70])
            ck("%s: the hint does not claim a result was used" % label,
               bool(hint) and "from your result" not in hint, (hint or "")[:60])
            ck("%s: the hint credits the guide link instead" % label,
               bool(hint) and "guide link you followed" in hint)
            await js("document.getElementById('plan-interest')"
                     ".scrollIntoView({block:'center',behavior:'instant'})")
            await asyncio.sleep(0.4)
            await shot("wf4-%s-06-interest-no-result.png" % label)
            ck("%s: the fine print claims no six answers" % label,
               "no assessment answers" in
               (await js("(document.querySelector('.plan__fine')||{})"
                         ".textContent") or ""))
            ck("%s: consent unticked and required" % label,
               (await js("(document.getElementById('plan-consent')||{}).checked"))
               is False and
               (await js("(document.getElementById('plan-consent')||{}).required"))
               is True)
            ck("%s: consent does not assert an assessment was taken" % label,
               "if I took the assessment" in
               (await js("(document.querySelector('.plan__check')||{})"
                         ".textContent") or ""))
            b = await js("window.__beacons.join(' ')")
            ck("%s: guide-tour and direct-form-view beacons fired" % label,
               "guide-choice-tour.txt" in (b or "") and
               "direct-inquiry-form-view.txt" in (b or ""),
               (b or "").replace(BASE, "")[:90])
            ck("%s: no save beacon fired merely by opening" % label,
               "plan-visit-saved" not in (b or "") and
               "inquiry-submitted" not in (b or ""))

            print("\n--- %s: reach to the first contact field ---" % label.upper())
            r = await js(REACH)
            ck("%s: First name is inside one screen of the section top" % label,
               bool(r) and r["firstName"] < r["viewport"],
               "%dpx into a %dpx viewport" % (r["firstName"], r["viewport"]))
            ck("%s: the consent tick is still above the introduction" % label,
               bool(r) and r["who"] > r["consent"],
               "consent %dpx, introduction %dpx" % (r["consent"], r["who"]))
            await js("document.getElementById('plan-visit')"
                     ".scrollIntoView({behavior:'instant'})")
            await asyncio.sleep(0.4)
            await shot("wf4-%s-02-direct-form.png" % label)

            print("\n=== %s: validation failures (nothing sent) ===" % label.upper())
            # consent rejection
            await js("""(function(){
              var f=document.querySelector('#plan-visit form');
              f.elements.firstName.value='Test';
              f.elements.lastName.value='Visitor';
              f.elements.email.value='t@example.com';
              document.getElementById('plan-consent').checked=false;
              f.querySelector('button[type=submit]').click();}())""")
            await asyncio.sleep(0.6)
            ck("%s: unticked consent blocks the submission" % label,
               (await js("window.__posts.length")) == 0,
               await js("(document.getElementById('plan-status')||{}).textContent"))
            # no contact details at all
            await js("""(function(){
              var f=document.querySelector('#plan-visit form');
              f.elements.email.value=''; f.elements.phone.value='';
              document.getElementById('plan-consent').checked=true;
              f.querySelector('button[type=submit]').click();}())""")
            await asyncio.sleep(0.6)
            ck("%s: no contact details blocks the submission" % label,
               (await js("window.__posts.length")) == 0,
               await js("(document.getElementById('plan-status')||{}).textContent"))
            # no name
            await js("""(function(){
              var f=document.querySelector('#plan-visit form');
              f.elements.firstName.value=''; f.elements.lastName.value='';
              f.elements.email.value='t@example.com';
              f.querySelector('button[type=submit]').click();}())""")
            await asyncio.sleep(0.6)
            ck("%s: a missing name blocks the submission" % label,
               (await js("window.__posts.length")) == 0,
               await js("(document.getElementById('plan-status')||{}).textContent"))
            await shot("wf4-%s-03-validation.png" % label)

            print("\n=== %s: EVERY interest value, on the wire ===" % label.upper())
            for iid in INTEREST_IDS:
                await goto("/?tour=independent#plan-visit")
                await js(FILL % json.dumps(iid))
                await asyncio.sleep(0.9)
                posts = await js("window.__posts.length")
                body = await js("(window.__posts[0]||{}).body || ''")
                try:
                    sent = json.loads(body or "{}")
                except ValueError:
                    sent = {}
                ck("%s: interest=%s posts once, as itself" % (label, iid),
                   posts == 1 and sent.get("interest") == iid,
                   "%s POST(s), interest=%r" % (posts, sent.get("interest")))
                ck("%s: interest=%s still carries careLevel direct" % (label, iid),
                   sent.get("careLevel") == "direct", repr(sent.get("careLevel")))
                ck("%s: interest=%s reaches the existing endpoint only"
                   % (label, iid),
                   (await js("(window.__posts[0]||{}).url || ''"))
                   .endswith("/api/plan-visit"))
                ck("%s: interest=%s sends no assessment answers" % (label, iid),
                   "adl" not in (body or "") and "household" not in (body or ""))
            await shot("wf4-%s-04-submitted.png" % label)

            print("\n=== %s: pathway 1, the assessment is untouched ==="
                  % label.upper())
            await goto("/?from=il-guide#assessment")
            ck("%s: the audience chooser opens" % label,
               await js("!!document.querySelector('.aud__h')"))
            b = await js("window.__beacons.join(' ')")
            ck("%s: guide-assessment beacon fired" % label,
               "guide-choice-assessment.txt" in (b or ""))
            ck("%s: no direct-form beacon on this path" % label,
               "direct-inquiry-form-view" not in (b or ""))
            await walk_assessment([2, 0, 1, 1, 0, 3])
            ck("%s: care-level scoring still correct (assisted)" % label,
               (await js("(document.querySelector('.res__name')||{})"
                         ".textContent")) == "Assisted Living")
            ck("%s: that result's careLevel is NOT direct" % label,
               (await js("(document.getElementById('plan-interest')||{}).value"))
               == "assisted")
            hint = await js(HINT)
            ck("%s: this path DOES say pre-filled from your result" % label,
               bool(hint) and "Pre-filled from your result" in hint,
               (hint or "")[:60])
            await js("document.getElementById('plan-interest')"
                     ".scrollIntoView({block:'center',behavior:'instant'})")
            await asyncio.sleep(0.4)
            await shot("wf4-%s-07-interest-from-result.png" % label)
            r = await js(REACH)
            ck("%s: First name reachable on the assessment path too" % label,
               bool(r) and r["firstName"] < r["viewport"],
               "%dpx into a %dpx viewport" % (r["firstName"], r["viewport"]))
            # a changed interest must travel on this pathway as well
            await js(FILL % json.dumps("memory"))
            await asyncio.sleep(0.9)
            body = await js("(window.__posts[0]||{}).body || ''")
            try:
                sent = json.loads(body or "{}")
            except ValueError:
                sent = {}
            ck("%s: a changed interest travels after an assessment" % label,
               sent.get("interest") == "memory", repr(sent.get("interest")))
            ck("%s: the derived care level travels with it" % label,
               sent.get("careLevel") == "assisted", repr(sent.get("careLevel")))
            await shot("wf4-%s-05-assessment-path.png" % label)

    print("\n%s" % ("ALL WORKFLOW 4 CHECKS PASSED" if not fails
                    else "FAILURES: " + "; ".join(fails)))


try:
    asyncio.run(main())
finally:
    proc.terminate()
    if srv:
        srv.shutdown()
sys.exit(1 if fails else 0)
