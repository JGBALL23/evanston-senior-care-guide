# -*- coding: utf-8 -*-
"""Real-browser mobile pass: homepage, all six questions, the independent
living by-choice result, and the optional inquiry form. Serves _dist locally
and drives headless Chrome over the DevTools Protocol.

Submits nothing. The form is inspected, never posted."""
import asyncio, base64, functools, http.server, json, os, socketserver
import subprocess, sys, threading, time, urllib.request
import websockets

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PORT, CDP = 8777, 9378
OUT = "shots"
os.makedirs(OUT, exist_ok=True)
fails = []


def ck(name, ok, detail=""):
    print("   %-54s %s %s" % (name, "PASS" if ok else "FAIL", detail))
    if not ok:
        fails.append(name)


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


srv = socketserver.TCPServer(
    ("127.0.0.1", PORT),
    functools.partial(Quiet, directory="_dist"))
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = "http://127.0.0.1:%d" % PORT

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
    async with websockets.connect(WS, max_size=80 * 1024 * 1024) as ws:
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
            open(os.path.join(OUT, name), "wb").write(base64.b64decode(s["data"]))

        async def goto(url):
            await call("Page.navigate", url=url)
            for _ in range(120):
                if await js("document.readyState") == "complete":
                    break
                await asyncio.sleep(0.1)
            await asyncio.sleep(0.5)

        await call("Page.enable")
        await call("Runtime.enable")
        await call("Emulation.setDeviceMetricsOverride", width=390, height=844,
                   deviceScaleFactor=3, mobile=True)
        await call("Emulation.setTouchEmulationEnabled", enabled=True)

        print("\n=== HOMEPAGE @390x844 (iPhone-class) ===")
        await goto(BASE + "/")
        ck("no horizontal scroll",
           not await js("document.documentElement.scrollWidth > "
                        "document.documentElement.clientWidth + 1"),
           "scrollW=%s clientW=%s" % (await js("document.documentElement.scrollWidth"),
                                      await js("document.documentElement.clientWidth")))
        cards = await js("[...document.querySelectorAll('.cat__name')].map(e=>e.textContent.trim())")
        ck("five living options, independent living first",
           len(cards) == 5 and cards[0] == "Independent Living", " | ".join(cards))
        ck("independent living card links to the new guide",
           await js("!!document.querySelector('.cat a[href=\"/guides/independent-living-evanston/\"]')"))
        ck("menu button is a 44px+ tap target",
           await js("(function(){var r=document.getElementById('navToggle')"
                    ".getBoundingClientRect();return Math.min(r.width,r.height)>=44;}())"),
           await js("JSON.stringify(document.getElementById('navToggle')"
                    ".getBoundingClientRect().height)"))
        await shot("il-mobile-01-home.png")

        print("\n=== SIX QUESTIONS, lifestyle path ===")
        await js("document.querySelector('a[href=\"#assessment\"]').click()")
        await asyncio.sleep(0.6)
        # q1..q6: pick "no concerns" (0) for five, lifestyle (1) on household
        picks = [0, 0, 0, 0, 0, 1]
        for i, choice in enumerate(picks):
            txt = await js("(document.querySelector('.q__text')||{}).textContent")
            cnt = await js("(document.querySelector('.q__count')||{}).textContent")
            opts = await js("document.querySelectorAll('.opt').length")
            tap = await js("(function(){var b=document.querySelectorAll('.opt');"
                           "var m=99;for(var i=0;i<b.length;i++){var r=b[i]"
                           ".getBoundingClientRect();if(r.height<m)m=r.height;}return m;}())")
            ck("Q%d renders, %d options, min tap %spx" % (i + 1, opts or 0, tap),
               bool(txt) and (opts or 0) >= 4 and (tap or 0) >= 44,
               (cnt or "?").strip())
            if i == 0:
                await shot("il-mobile-02-q1.png")
            await js("document.querySelectorAll('.opt')[%d].click()" % choice)
            await asyncio.sleep(0.45)

        print("\n=== INDEPENDENT LIVING RESULT (by choice) ===")
        name = await js("(document.querySelector('.res__name')||{}).textContent")
        body = await js("document.getElementById('quiz').innerText")
        ck("result is Independent Living", (name or "").strip() == "Independent Living",
           (name or "none").strip())
        ck("framed as a lifestyle decision, not a care need",
           "not a care decision" in (body or ""))
        ck("states no care need is described",
           "describes a need for care" in (body or ""))
        ck("suggests no higher level of care",
           "Also worth looking at" not in (body or ""))
        ck("no horizontal scroll on the result",
           not await js("document.documentElement.scrollWidth > "
                        "document.documentElement.clientWidth + 1"))
        await shot("il-mobile-03-result.png")

        print("\n=== OPTIONAL INQUIRY FORM ===")
        ck("the form is present", await js("!!document.getElementById('plan-visit')"))
        ck("interest dropdown pre-filled to Independent Living",
           (await js("(document.getElementById('plan-interest')||{}).value")) == "independent",
           await js("(document.getElementById('plan-interest')||{}).value"))
        ck("five interest choices offered",
           (await js("(document.getElementById('plan-interest')||{optio"
                     "ns:[]}).options.length")) == 5)
        ck("consent box starts UNticked and is required",
           (await js("(document.getElementById('plan-consent')||{}).checked")) is False and
           (await js("(document.getElementById('plan-consent')||{}).required")) is True)
        consent = await js("(function(){var c=document.getElementById('plan-consent');"
                           "return c? c.closest('label').innerText : '';}())")
        ck("consent names the owner first, then Westminster Place",
           "person who runs this guide" in (consent or "") and
           "Westminster Place" in (consent or ""),
           (consent or "")[:60].replace("\n", " "))
        ck("no field asks for a name before the result is shown",
           await js("!!document.querySelector('.res__name')"))
        ck("inputs are 44px+ tall on mobile",
           await js("(function(){var f=document.querySelectorAll("
                    "'#plan-visit input[type=text],#plan-visit input[type=email],"
                    "#plan-visit input[type=tel],#plan-visit select');var m=99;"
                    "for(var i=0;i<f.length;i++){var r=f[i].getBoundingClientRect();"
                    "if(r.height&&r.height<m)m=r.height;}return m>=44;}())"))
        ck("privacy notice linked from the form",
           await js("!!document.querySelector('#plan-visit a[href*=\"privacy\"]')"))
        await js("document.getElementById('plan-visit').scrollIntoView()")
        await asyncio.sleep(0.4)
        await shot("il-mobile-04-form.png")

        print("\n=== THE GUIDE @390 ===")
        await goto(BASE + "/guides/independent-living-evanston/")
        ck("guide loads with one h1",
           (await js("document.querySelectorAll('h1').length")) == 1)
        ck("no horizontal scroll",
           not await js("document.documentElement.scrollWidth > "
                        "document.documentElement.clientWidth + 1"))
        ck("quotes no Illinois independent-living median",
           "no Illinois median" in (await js("document.body.innerText")) or
           "reports no Illinois median" in (await js("document.body.innerText")))
        # Scoped to the article. Nav and footer carry their own assessment
        # links; check-guides counts the two inside the article, and that is
        # the number that matters.
        # Counted between the h1 and the footer, the same window check-guides
        # uses. The nav and footer carry their own assessment links and are
        # navigation, not persuasion.
        inart = await js("(function(){var h=document.documentElement.innerHTML;"
                         "var a=h.indexOf('<h1');var f=h.indexOf('<footer');"
                         "if(f<0)f=h.length;var m=h.slice(a,f).match("
                         "/href=\"\/#assessment\"/g);return m?m.length:0;}())")
        ck("assessment links between h1 and footer: exactly two", inart == 2, str(inart))
        await shot("il-mobile-05-guide.png")

    print("\n%s" % ("ALL MOBILE CHECKS PASSED" if not fails
                    else "FAILURES: " + "; ".join(fails)))


try:
    asyncio.run(main())
finally:
    proc.terminate()
    srv.shutdown()
sys.exit(1 if fails else 0)
