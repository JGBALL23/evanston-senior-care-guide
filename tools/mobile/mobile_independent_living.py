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

        print("\n=== WHO IS ANSWERING (the step before question one) ===")
        await js("document.querySelector('a[href=\"#assessment\"]').click()")
        await asyncio.sleep(0.6)
        ck("chooser appears before question one",
           await js("!!document.querySelector('.aud__h')"))
        auds = await js("[...document.querySelectorAll('[data-aud]')]"
                        ".map(b=>b.getAttribute('data-aud'))")
        ck("both perspectives offered", sorted(auds or []) == ["parent", "self"],
           ",".join(auds or []))
        ck("chooser says it changes nothing about the result",
           "changes nothing about the result" in
           (await js("document.querySelector('.aud').innerText")))
        ck("chooser buttons are 44px+ tap targets",
           await js("(function(){var b=document.querySelectorAll('[data-aud]');"
                    "var m=99;for(var i=0;i<b.length;i++){var r=b[i]"
                    ".getBoundingClientRect();if(r.height<m)m=r.height;}"
                    "return m>=44;}())"))
        await shot("il-mobile-02-chooser.png")

        seen = {}
        for aud in ("self", "parent"):
            label = "SELF" if aud == "self" else "PARENT"
            print("\n=== %s: six questions, lifestyle path ===" % label)
            await goto(BASE + "/")
            await js("document.querySelector('a[href=\"#assessment\"]').click()")
            await asyncio.sleep(0.5)
            await js("document.querySelector('[data-aud=\"%s\"]').click()" % aud)
            await asyncio.sleep(0.45)

            q1 = await js("(document.querySelector('.q__text')||{}).textContent")
            if aud == "self":
                ck("%s: Q1 speaks to the visitor, not about a parent" % label,
                   "your parent" not in (q1 or "") and (q1 or "").startswith("Do you"),
                   (q1 or "")[:52])
            else:
                ck("%s: Q1 is inclusive, not parent-only" % label,
                   "your parent or loved one" in (q1 or ""), (q1 or "")[:58])

            picks = [0, 0, 0, 0, 0, 1]
            for i, choice in enumerate(picks):
                cnt = await js("(document.querySelector('.q__count')||{}).textContent")
                opts = await js("document.querySelectorAll('.opt').length")
                tap = await js("(function(){var b=document.querySelectorAll('.opt');"
                               "var m=99;for(var i=0;i<b.length;i++){var r=b[i]"
                               ".getBoundingClientRect();if(r.height<m)m=r.height;}"
                               "return m;}())")
                ck("%s: Q%d renders, %d options, min tap %spx"
                   % (label, i + 1, opts or 0, tap),
                   (opts or 0) >= 4 and (tap or 0) >= 44, (cnt or "?").strip())
                if i == 0 and aud == "self":
                    await shot("il-mobile-03-self-q1.png")
                if i == 0 and aud == "parent":
                    await shot("il-mobile-04-parent-q1.png")
                await js("document.querySelectorAll('.opt')[%d].click()" % choice)
                await asyncio.sleep(0.4)

            name = await js("(document.querySelector('.res__name')||{}).textContent")
            body = await js("document.getElementById('quiz').innerText")
            seen[aud] = (name or "").strip()
            ck("%s: result is Independent Living" % label,
               (name or "").strip() == "Independent Living", (name or "none").strip())
            ck("%s: framed as a lifestyle decision" % label,
               "not a care decision" in (body or ""))
            ck("%s: suggests no higher level of care" % label,
               "Also worth looking at" not in (body or ""))
            if aud == "self":
                ck("SELF: result speaks to the visitor",
                   "says you need help" in (body or ""),
                   "second person" if "says you need help" in (body or "") else "MISSING")
            else:
                ck("PARENT: result speaks about them inclusively",
                   "says they need" in (body or "") or
                   "your parent or loved one" in (body or ""))
            ck("%s: no horizontal scroll on the result" % label,
               not await js("document.documentElement.scrollWidth > "
                            "document.documentElement.clientWidth + 1"))

            ck("%s: inquiry form present" % label,
               await js("!!document.getElementById('plan-visit')"))
            ck("%s: interest pre-filled to Independent Living" % label,
               (await js("(document.getElementById('plan-interest')||{}).value"))
               == "independent")
            ck("%s: consent unticked and required" % label,
               (await js("(document.getElementById('plan-consent')||{}).checked"))
               is False and
               (await js("(document.getElementById('plan-consent')||{}).required"))
               is True)
            consent = await js("(function(){var c=document.getElementById('plan-consent');"
                               "return c? c.closest('label').innerText : '';}())")
            ck("%s: consent says the owner reads it and decides" % label,
               "reads every inquiry himself" in (consent or "") and
               "decides how to follow up" in (consent or ""))
            ck("%s: consent does not promise automatic forwarding" % label,
               "may pass my details" in (consent or "") and
               "will be sent to Westminster" not in (consent or ""))
            ck("%s: inputs and select are 44px+" % label,
               await js("(function(){var f=document.querySelectorAll("
                        "'#plan-visit input[type=text],#plan-visit input[type=email],"
                        "#plan-visit input[type=tel],#plan-visit select');var m=99;"
                        "for(var i=0;i<f.length;i++){var r=f[i].getBoundingClientRect();"
                        "if(r.height&&r.height<m)m=r.height;}return m>=44;}())"))
            await js("document.getElementById('plan-visit').scrollIntoView()")
            await asyncio.sleep(0.4)
            await shot("il-mobile-05-%s-form.png" % aud)

        ck("both perspectives reach the SAME result",
           seen.get("self") == seen.get("parent") == "Independent Living",
           "%s vs %s" % (seen.get("self"), seen.get("parent")))

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
        await shot("il-mobile-06-guide.png")

    print("\n%s" % ("ALL MOBILE CHECKS PASSED" if not fails
                    else "FAILURES: " + "; ".join(fails)))


try:
    asyncio.run(main())
finally:
    proc.terminate()
    srv.shutdown()
sys.exit(1 if fails else 0)
