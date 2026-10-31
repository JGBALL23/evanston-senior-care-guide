# -*- coding: utf-8 -*-
"""How far a visitor must scroll to reach the first contact field.

Measures, does not judge. The number it prints is the vertical distance
from the top of the inquiry section to the top of the First name input,
which is the distance a thumb has to travel past the disclosures before
it can type anything. Run on both pathways and both viewports.

Submits nothing: fetch is stubbed before the document loads.

Usage: form_reach.py [base-url]"""

# Every harness announces itself with one fixed User-Agent so the host's
# request log can exclude it by exact match. A test run must never be
# counted as a family. The string is identical in every harness; test.js
# checks that it stays so.
HARNESS_UA = "ESCG-harness/1 (automated test; +https://evanstonseniorcareguide.com/)"
import asyncio, base64, functools, http.server, json, os, socketserver
import subprocess, sys, threading, time, urllib.request
import websockets

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
PORT, CDP = 8904, 9386
os.makedirs("shots", exist_ok=True)

LIVE = sys.argv[1] if len(sys.argv) > 1 else ""
srv = None
if LIVE:
    BASE = LIVE.rstrip("/")
else:
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
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
    [CHROME, "--headless=new", "--user-agent=" + HARNESS_UA, "--disable-gpu", "--no-sandbox", "--no-first-run",
     "--remote-debugging-port=%d" % CDP, "about:blank"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
for _ in range(60):
    try:
        urllib.request.urlopen("http://localhost:%d/json/version" % CDP,
                               timeout=1).read()
        break
    except Exception:
        time.sleep(0.5)
raw = urllib.request.urlopen("http://localhost:%d/json/list" % CDP,
                             timeout=10).read()
WS = [t["webSocketDebuggerUrl"] for t in json.loads(raw.decode())
      if t.get("type") == "page"][0]

STUB = """
window.fetch = function (url, opts) {
  return Promise.resolve(new Response('{"ok":true}', { status: 200,
    headers: { 'content-type': 'application/json' } }));
};
"""

MEASURE = """(function () {
  var sec = document.getElementById('plan-visit');
  if (!sec) return null;
  var first = document.querySelector('#plan-form input[name=firstName]');
  var consent = document.getElementById('plan-consent');
  var who = document.querySelector('.plan__who');
  var top = sec.getBoundingClientRect().top;
  function off(el) {
    return el ? Math.round(el.getBoundingClientRect().top - top) : -1;
  }
  return {
    sectionHeight: Math.round(sec.getBoundingClientRect().height),
    firstName: off(first),
    consent: off(consent),
    who: off(who),
    viewport: window.innerHeight
  };
}())"""


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

        await call("Page.enable")
        await call("Runtime.enable")

        async def goto(path):
            await call("Page.addScriptToEvaluateOnNewDocument", source=STUB)
            await call("Page.navigate", url=BASE + path)
            for _ in range(120):
                if await js("document.readyState") == "complete":
                    break
                await asyncio.sleep(0.1)
            await asyncio.sleep(0.6)

        for label, w, h, mob in [("mobile", 390, 844, True),
                                 ("desktop", 1280, 900, False)]:
            await call("Emulation.setDeviceMetricsOverride", width=w, height=h,
                       deviceScaleFactor=2 if mob else 1, mobile=mob)

            await goto("/?tour=independent#plan-visit")
            m = await js(MEASURE)
            print("\n%s  direct inquiry   %s" % (label.upper(), m))

            # the assessment pathway, walked to a result
            await goto("/#assessment")
            await js("document.querySelector('[data-aud=\\'parent\\']').click()")
            await asyncio.sleep(0.3)
            for c in [2, 0, 1, 1, 0, 3]:
                await js("document.querySelectorAll('.opt')[%d].click()" % c)
                await asyncio.sleep(0.25)
            m = await js(MEASURE)
            print("%s  after assessment %s" % (label.upper(), m))


try:
    asyncio.run(main())
finally:
    proc.terminate()
    if srv:
        srv.shutdown()
