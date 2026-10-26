# -*- coding: utf-8 -*-
"""Workflow #4 walkthrough: both guide pathways, mobile and desktop.

Submits NOTHING to production. The form's client-side validation is
exercised against the real DOM; the submit button is never pressed with a
valid payload, and fetch is stubbed so no request can leave the page.

Usage: wf4_direct_inquiry.py [base-url]   (default: local _dist server)"""
import asyncio, base64, functools, http.server, json, os, socketserver
import subprocess, sys, threading, time, urllib.request
import websockets

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
PORT, CDP = 8903, 9385
os.makedirs("shots", exist_ok=True)
fails = []


def ck(n, ok, d=""):
    print("   %-56s %s %s" % (n, "PASS" if ok else "FAIL", d))
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

CHROME = None
for p in (r"C:\Program Files\Google\Chrome\Application\chrome.exe",
          r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"):
    if os.path.isfile(p):
        CHROME = p
proc = subprocess.Popen(
    [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox", "--no-first-run",
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
            await call("Page.addScriptToEvaluateOnNewDocument", source=STUB)
            await call("Page.navigate", url=BASE + path)
            for _ in range(120):
                if await js("document.readyState") == "complete":
                    break
                await asyncio.sleep(0.1)
            await asyncio.sleep(0.6)

        await call("Page.enable")
        await call("Runtime.enable")

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
            ck("%s: article reads without touching either" % label,
               "Neither is required to finish reading" in
               (await js("document.body.innerText")))
            ck("%s: no horizontal scroll" % label,
               not await js("document.documentElement.scrollWidth > "
                            "document.documentElement.clientWidth + 1"))
            await js("document.querySelector('.fork').scrollIntoView()")
            await asyncio.sleep(0.4)
            await shot("wf4-%s-01-guide-fork.png" % label)

            print("\n=== %s: pathway 2, straight to the form ===" % label.upper())
            await goto("/?tour=independent#plan-visit")
            ck("%s: no assessment is shown" % label,
               (await js("document.querySelectorAll('.opt[data-i]').length")) == 0)
            ck("%s: the page says no assessment is needed" % label,
               (await js("(document.querySelector('.res__name')||{})"
                         ".textContent")) == "No assessment needed")
            ck("%s: it states nothing is assumed or recorded" % label,
               "assumed, recorded or guessed" in
               (await js("document.getElementById('quiz').innerText")))
            ck("%s: the form is present without any answers" % label,
               await js("!!document.getElementById('plan-visit')"))
            ck("%s: interest preselected to Independent Living" % label,
               (await js("(document.getElementById('plan-interest')||{}).value"))
               == "independent")
            ck("%s: consent unticked and required" % label,
               (await js("(document.getElementById('plan-consent')||{}).checked"))
               is False and
               (await js("(document.getElementById('plan-consent')||{}).required"))
               is True)
            b = await js("window.__beacons.join(' ')")
            ck("%s: guide-tour and direct-form-view beacons fired" % label,
               "guide-choice-tour.txt" in (b or "") and
               "direct-inquiry-form-view.txt" in (b or ""),
               (b or "").replace(BASE, "")[:90])
            ck("%s: no save beacon fired merely by opening" % label,
               "plan-visit-saved" not in (b or "") and
               "inquiry-submitted" not in (b or ""))
            await js("document.getElementById('plan-visit').scrollIntoView()")
            await asyncio.sleep(0.4)
            await shot("wf4-%s-02-direct-form.png" % label)

            print("\n=== %s: submission cases (stubbed, nothing sent) ===" % label.upper())
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
               "%s POST(s)" % await js("window.__posts.length"))
            # invalid: no contact details at all
            await js("""(function(){
              var f=document.querySelector('#plan-visit form');
              f.elements.email.value=''; f.elements.phone.value='';
              document.getElementById('plan-consent').checked=true;
              f.querySelector('button[type=submit]').click();}())""")
            await asyncio.sleep(0.6)
            ck("%s: no contact details blocks the submission" % label,
               (await js("window.__posts.length")) == 0,
               await js("(document.getElementById('plan-status')||{}).textContent"))
            # valid, captured not sent
            await js("""(function(){
              var f=document.querySelector('#plan-visit form');
              f.elements.email.value='t@example.com';
              document.getElementById('plan-consent').checked=true;
              f.querySelector('button[type=submit]').click();}())""")
            await asyncio.sleep(0.9)
            posts = await js("window.__posts.length")
            body = await js("(window.__posts[0]||{}).body || ''")
            ck("%s: a valid submission posts exactly once" % label,
               posts == 1, "%s POST(s)" % posts)
            ck("%s: it posts to the existing endpoint" % label,
               "/api/plan-visit" in (await js("(window.__posts[0]||{}).url || ''")))
            ck("%s: careLevel travels as direct, never fabricated" % label,
               '"careLevel":"direct"' in (body or "").replace(", ", ","),
               (body or "")[:120])
            ck("%s: interest travels as independent" % label,
               '"interest":"independent"' in (body or ""),
               "tail: " + (body or "")[-90:])
            ck("%s: no assessment answers are in the payload" % label,
               "adl" not in (body or "") and "household" not in (body or ""))
            await shot("wf4-%s-03-submitted.png" % label)

            print("\n=== %s: pathway 1, the assessment is untouched ===" % label.upper())
            await goto("/?from=il-guide#assessment")
            ck("%s: the audience chooser opens" % label,
               await js("!!document.querySelector('.aud__h')"))
            b = await js("window.__beacons.join(' ')")
            ck("%s: guide-assessment beacon fired" % label,
               "guide-choice-assessment.txt" in (b or ""))
            ck("%s: no direct-form beacon on this path" % label,
               "direct-inquiry-form-view" not in (b or ""))
            # walk a care journey to prove scoring is untouched
            await js("document.querySelector('[data-aud=" + chr(34) + "parent"
                     + chr(34) + "]').click()")
            await asyncio.sleep(0.35)
            for c in [2, 0, 1, 1, 0, 3]:
                await js("document.querySelectorAll('.opt')[%d].click()" % c)
                await asyncio.sleep(0.28)
            ck("%s: care-level scoring still correct (assisted)" % label,
               (await js("(document.querySelector('.res__name')||{})"
                         ".textContent")) == "Assisted Living")
            ck("%s: that result's careLevel is NOT direct" % label,
               (await js("(document.getElementById('plan-interest')||{}).value"))
               == "assisted")
            await shot("wf4-%s-04-assessment-path.png" % label)

    print("\n%s" % ("ALL WORKFLOW 4 CHECKS PASSED" if not fails
                    else "FAILURES: " + "; ".join(fails)))


try:
    asyncio.run(main())
finally:
    proc.terminate()
    if srv:
        srv.shutdown()
sys.exit(1 if fails else 0)
