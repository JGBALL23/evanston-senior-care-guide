# -*- coding: utf-8 -*-
"""Prove independent living is immediately visible on a no-care-need
result, in both perspectives, and that the tour action really navigates to
the inquiry form with Independent Living preselected. Submits nothing."""
import asyncio, base64, functools, http.server, json, os, socketserver
import subprocess, sys, threading, time, urllib.request
import websockets
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PORT, CDP = 8901, 9383
os.makedirs("shots", exist_ok=True)
fails = []


def ck(n, ok, d=""):
    print("   %-54s %s %s" % (n, "PASS" if ok else "FAIL", d))
    if not ok:
        fails.append(n)


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


# Pass a base URL to run the same walk against production.
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
            open(os.path.join("shots", name), "wb").write(base64.b64decode(s["data"]))

        await call("Page.enable")
        await call("Runtime.enable")
        await call("Emulation.setDeviceMetricsOverride", width=390, height=844,
                   deviceScaleFactor=2, mobile=True)
        await call("Emulation.setTouchEmulationEnabled", enabled=True)

        for aud in ("self", "parent"):
            print("\n=== %s: finish with no care needs @390x844 ===" % aud.upper())
            await call("Page.navigate", url=BASE + "/")
            for _ in range(120):
                if await js("document.readyState") == "complete":
                    break
                await asyncio.sleep(0.1)
            await asyncio.sleep(0.5)
            await js("document.querySelector('a[href=\"#assessment\"]').click()")
            await asyncio.sleep(0.4)
            await js("document.querySelector('[data-aud=\"%s\"]').click()" % aud)
            await asyncio.sleep(0.35)
            for _ in range(6):
                await js("document.querySelectorAll('.opt')[0].click()")
                await asyncio.sleep(0.3)

            head = (await js("(document.querySelector('.res__name')||{})"
                             ".textContent") or "").strip()
            ck("%s: conclusion stays honest" % aud,
               head == "No significant care needs identified", head)
            ck("%s: section titled Independent Living" % aud,
               (await js("(document.querySelector('.il__h')||{}).textContent"))
               == "Independent Living")
            eyebrow = await js("(document.querySelector('.il__eyebrow')||{})"
                               ".textContent")
            ck("%s: disclaimed as a lifestyle option, above the name" % aud,
               "not a care recommendation" in (eyebrow or ""), eyebrow or "MISSING")

            # distance from the result heading to the section: the buried test
            gap = await js("""(function(){
              var h=document.querySelector('.res__name');
              var il=document.querySelector('.res__block.il');
              if(!h||!il) return -1;
              return Math.round(il.getBoundingClientRect().top
                              - h.getBoundingClientRect().bottom);}())""")
            ck("%s: sits within 160px of the conclusion" % aud,
               0 <= (gap or -1) <= 160, "%spx below the heading" % gap)

            # is it in the first viewport without scrolling?
            await js("document.querySelector('#quiz').scrollIntoView({block:'start'})")
            await asyncio.sleep(0.4)
            inview = await js("""(function(){
              var il=document.querySelector('.res__block.il');
              var r=il.getBoundingClientRect();
              return r.top < innerHeight && r.bottom > 0;}())""")
            ck("%s: visible in the first screen of the result" % aud, inview is True)

            words = await js("""(function(){
              return [...document.querySelectorAll('.il__lead')]
                .map(e=>e.innerText.trim().split(/\\s+/).length);}())""")
            ck("%s: no long paragraphs (each under 45 words)" % aud,
               all(w < 45 for w in (words or [999])), str(words))

            btns = await js("""(function(){
              return [...document.querySelectorAll('.il__btn')]
                .map(b=>b.innerText.trim()+' ['+Math.round(
                  b.getBoundingClientRect().height)+'px]');}())""")
            ck("%s: two visible actions, both 48px+" % aud,
               len(btns or []) == 2 and all("[4" in b or "[5" in b or "[6" in b
                                            for b in btns),
               " | ".join(btns or []))
            await shot("il-prom-%s-result.png" % aud)

            # the tour action must actually reach the form
            await js("document.querySelector('.il__btn[href=\"#plan-visit\"]').click()")
            await asyncio.sleep(0.8)
            reached = await js("""(function(){
              var f=document.getElementById('plan-visit');
              if(!f) return 'missing';
              var r=f.getBoundingClientRect();
              return (r.top < innerHeight && r.bottom > 0) ? 'in-view' : 'offscreen';}())""")
            ck("%s: tour action navigates to the inquiry form" % aud,
               reached == "in-view", reached)
            ck("%s: form preselects Independent Living" % aud,
               (await js("(document.getElementById('plan-interest')||{}).value"))
               == "independent")
            ck("%s: consent still unticked and required" % aud,
               (await js("(document.getElementById('plan-consent')||{}).checked"))
               is False and
               (await js("(document.getElementById('plan-consent')||{}).required"))
               is True)
            await shot("il-prom-%s-form.png" % aud)

    print("\n%s" % ("ALL PROMINENCE CHECKS PASSED" if not fails
                    else "FAILURES: " + "; ".join(fails)))


try:
    asyncio.run(main())
finally:
    proc.terminate()
    if srv:
        srv.shutdown()
sys.exit(1 if fails else 0)
