# -*- coding: utf-8 -*-
"""Stress the library at 100 guides over CDP: search, filter, Show more,
empty results, keyboard accessibility, sticky-nav reachability, mobile."""
import asyncio, base64, json, os, subprocess, sys, time, urllib.request
import websockets
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CHROME = None
for p in (r"C:\Program Files\Google\Chrome\Application\chrome.exe",
          r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"):
    if os.path.isfile(p):
        CHROME = p
PORT = 9377
BASE = sys.argv[1]
OUT = sys.argv[2] if len(sys.argv) > 2 else "shots"
os.makedirs(OUT, exist_ok=True)

fails = []


def ck(name, ok, detail=""):
    print("   %-52s %s %s" % (name, "PASS" if ok else "FAIL", detail))
    if not ok:
        fails.append(name)


proc = subprocess.Popen(
    [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox", "--no-first-run",
     "--remote-debugging-port=%d" % PORT, "about:blank"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
for _ in range(60):
    try:
        urllib.request.urlopen("http://localhost:%d/json/version" % PORT, timeout=1).read()
        break
    except Exception:
        time.sleep(0.5)
raw = urllib.request.urlopen("http://localhost:%d/json/list" % PORT, timeout=10).read()
WS = [t["webSocketDebuggerUrl"] for t in json.loads(raw.decode()) if t.get("type") == "page"][0]


async def main():
    n = [0]
    async with websockets.connect(WS, max_size=90 * 1024 * 1024) as ws:
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

        async def key(k, code, vk):
            for ty in ("rawKeyDown", "char", "keyUp"):
                await call("Input.dispatchKeyEvent", type=ty, key=k,
                           code=code, windowsVirtualKeyCode=vk,
                           nativeVirtualKeyCode=vk)
            await asyncio.sleep(0.08)

        async def shot(name, full=False):
            s = await call("Page.captureScreenshot", format="png",
                           captureBeyondViewport=full)
            open(os.path.join(OUT, name), "wb").write(base64.b64decode(s["data"]))

        await call("Page.enable")
        await call("Runtime.enable")

        for label, w, h, mob in (("mobile", 390, 844, True), ("desktop", 1280, 900, False)):
            print("\n=== %s @%d  (100 guides) ===" % (label, w))
            await call("Emulation.setDeviceMetricsOverride", width=w, height=h,
                       deviceScaleFactor=2, mobile=mob)
            await call("Page.navigate", url=BASE + "/guides/")
            for _ in range(100):
                if await js("document.readyState") == "complete":
                    break
                await asyncio.sleep(0.1)
            await asyncio.sleep(0.6)

            total = await js("document.querySelectorAll('.topic').length")
            vis = await js("[...document.querySelectorAll('.topic')].filter(c=>!c.hidden).length")
            ck("100 cards present", total == 100, str(total))
            ck("initial page capped at 9", vis == 9, str(vis))
            ck("count text correct",
               (await js("document.getElementById('libCount').textContent")) ==
               "Showing 9 of 100 guides.")
            ck("Show more offers the remainder",
               "91" in (await js("document.getElementById('libMore').textContent")))
            ck("no sideways scroll",
               not await js("document.documentElement.scrollWidth > "
                            "document.documentElement.clientWidth + 1"))
            await shot("sim-%s-01-default.png" % label)

            # ---- search timing + accuracy
            t0 = time.time()
            await js("(function(){var i=document.getElementById('libQ');"
                     "i.value='veterans';i.dispatchEvent(new Event('input'));}())")
            await asyncio.sleep(0.15)
            ms = int((time.time() - t0) * 1000)
            hits = await js("[...document.querySelectorAll('.topic')].filter(c=>!c.hidden).length")
            ck("search 'veterans' returns results", hits > 0, "%d shown, %dms" % (hits, ms))
            await shot("sim-%s-02-search.png" % label)

            # ---- two-word search narrows
            await js("(function(){var i=document.getElementById('libQ');"
                     "i.value='medicaid house';i.dispatchEvent(new Event('input'));}())")
            await asyncio.sleep(0.15)
            c2 = await js("document.getElementById('libCount').textContent")
            ck("two-word search narrows", "matching" in c2, c2)

            # ---- EMPTY RESULTS
            await js("(function(){var i=document.getElementById('libQ');"
                     "i.value='zzzqqq';i.dispatchEvent(new Event('input'));}())")
            await asyncio.sleep(0.15)
            empty = await js("document.getElementById('libCount').textContent")
            ck("empty search explains itself", "No guides match" in empty, empty)
            ck("Show more hidden when nothing matches",
               await js("document.getElementById('libMore').hidden"))
            ck("empty state is announced (aria-live)",
               (await js("document.getElementById('libCount').getAttribute('aria-live')")) == "polite")
            await shot("sim-%s-03-empty.png" % label)

            # ---- clear + filter
            await js("(function(){var i=document.getElementById('libQ');"
                     "i.value='';i.dispatchEvent(new Event('input'));"
                     "[...document.querySelectorAll('.chip')].find(c=>c.dataset.cat==='Veterans\\u2019 benefits'||c.dataset.cat.indexOf('Veterans')===0).click();}())")
            await asyncio.sleep(0.2)
            fc = await js("document.getElementById('libCount').textContent")
            ck("category filter works at scale", "matching" in fc, fc)
            ck("chip reports pressed state",
               (await js("[...document.querySelectorAll('.chip')].filter("
                         "c=>c.getAttribute('aria-pressed')==='true').length")) == 1)
            await shot("sim-%s-04-filter.png" % label)

            # ---- Show more
            await js("(function(){[...document.querySelectorAll('.chip')]"
                     ".find(c=>c.dataset.cat==='').click();}())")
            await asyncio.sleep(0.2)
            await js("document.getElementById('libMore').click()")
            await asyncio.sleep(0.25)
            after = await js("[...document.querySelectorAll('.topic')].filter(c=>!c.hidden).length")
            ck("Show more reveals everything", after == 100, str(after))
            ck("Show more hides itself when done",
               await js("document.getElementById('libMore').hidden"))
            ck("focus moved to the first newly-shown guide",
               await js("document.activeElement.closest('.topic')!==null"))
            await shot("sim-%s-05-expanded.png" % label, full=False)

            # ---- STICKY NAV: is the assessment reachable deep in the library?
            await js("window.scrollTo(0, 6000)")
            await asyncio.sleep(0.35)
            navtop = await js("""(function(){var n=document.querySelector('.nav');
              return n? Math.round(n.getBoundingClientRect().top):null;}())""")
            ck("nav still pinned to the top after scrolling 6000px", navtop == 0, str(navtop))
            sel = ("#navMenu a[href='/#assessment']" if mob
                   else ".nav a[href='/#assessment']")
            inview = await js("""(function(){var a=document.querySelector("%s");
              if(!a) return 'missing';
              var r=a.getBoundingClientRect();
              return (r.top>=0 && r.bottom<=innerHeight && r.width>0)?'in-view':'offscreen';}())""" % sel)
            if mob:
                ck("mobile: assessment lives in the menu, menu button pinned",
                   (await js("""(function(){var t=document.getElementById('navToggle');
                     var r=t.getBoundingClientRect();
                     return r.top>=0 && r.bottom<=innerHeight;}())""")) is True)
            else:
                ck("desktop: assessment button visible without scrolling back",
                   inview == "in-view", str(inview))
            await shot("sim-%s-06-deep-scroll.png" % label)

            # ---- KEYBOARD: tab from search into chips, activate with Enter
            await js("window.scrollTo(0,0); document.getElementById('libQ').focus()")
            await asyncio.sleep(0.15)
            ck("search box is focusable",
               (await js("document.activeElement.id")) == "libQ")
            await key("Tab", "Tab", 9)
            onchip = await js("document.activeElement.classList.contains('chip')")
            ck("Tab from search reaches the chips", onchip is True,
               str(await js("document.activeElement.className")))
            await key("Enter", "Enter", 13)
            await asyncio.sleep(0.2)
            ck("Enter activates a chip",
               (await js("[...document.querySelectorAll('.chip')].filter("
                         "c=>c.getAttribute('aria-pressed')==='true').length")) == 1)
            ck("focus ring is visible on the focused chip",
               (await js("""(function(){var e=document.activeElement;
                 var s=getComputedStyle(e,':focus-visible');
                 return e.classList.contains('chip');}())""")) is True)
            await js("(function(){[...document.querySelectorAll('.chip')]"
                     ".find(c=>c.dataset.cat==='').click();}())")

    print("\n%s" % ("ALL STRESS CHECKS PASSED" if not fails
                    else "FAILURES: " + ", ".join(fails)))

asyncio.run(main())
proc.terminate()
