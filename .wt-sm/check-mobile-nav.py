# -*- coding: utf-8 -*-
"""
check-mobile-nav.py — real device-width verification of the mobile menu.

WHY THIS EXISTS: `chrome --headless --window-size=375,900` does NOT give you
a 375px viewport. Chrome clamps it; measured clientWidth was 485 at every
requested width from 375 to 430. Every "mobile screenshot" taken that way is
a 485px render cropped to look narrow. This drives Chrome over the DevTools
Protocol and sets real device metrics instead, so 375 means 375.

Verifies, at each width: the Menu button is visible and >= 44px tall, the
menu opens on click, every expected destination is present, Escape closes it
and returns focus, clicking a link closes it, and the page does not scroll
sideways.

Usage:  python check-mobile-nav.py [base_url]
Exit 0 = every assertion passed.
"""
import asyncio
import json
import os
import subprocess
import sys
import time
import urllib.request

# websockets is NOT imported at module level on purpose. The cloud
# runner does not have it, and a top-level import crashes with a
# traceback before any guard can run - which is exactly what happened
# on the first cloud test. A missing dependency is a SKIP, not a
# failing site. It is imported inside main(), after the guards.

def _find_chrome():
    """The cloud routine runs on Linux, where this path does not exist.
    Check the usual Linux binaries and the two Windows install
    locations, and say so plainly rather than failing on a missing
    file."""
    import shutil
    for name in ("google-chrome", "google-chrome-stable", "chromium",
                 "chromium-browser", "chrome"):
        found = shutil.which(name)
        if found:
            return found
    for p in (r"C:\Program Files\Google\Chrome\Application\chrome.exe",
              r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"):
        if os.path.isfile(p):
            return p
    return None


CHROME = _find_chrome()
PORT = 9333
BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8731"
SHOTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shots")

WIDTHS = [375, 390]
# Every guide is checked, not a sample of one. A routine that adds a guide
# a day would otherwise never test the page it just wrote. The list comes
# from build-guides.py so it grows on its own.
def _slugs():
    import io
    import re
    gen = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "build-guides.py")
    src = io.open(gen, encoding="utf-8").read()
    return re.findall(r'^\s+"slug": "([a-z0-9-]+)"', src, re.M)


PAGES = ([("home", "/"), ("guides", "/guides/")]
         + [(s, "/guides/%s/" % s) for s in _slugs()])
EXPECTED_LINKS = ["/", "/guides/", "/#assessment"]

passed = 0
failed = 0


def check(name, ok, detail=""):
    global passed, failed
    if ok:
        passed += 1
    else:
        failed += 1
        print("  FAIL  %s   %s" % (name, detail))


class CDP(object):
    def __init__(self, ws):
        self.ws = ws
        self.n = 0

    async def call(self, method, **params):
        self.n += 1
        mid = self.n
        await self.ws.send(json.dumps({"id": mid, "method": method, "params": params}))
        while True:
            msg = json.loads(await self.ws.recv())
            if msg.get("id") == mid:
                if "error" in msg:
                    raise RuntimeError(method + ": " + json.dumps(msg["error"]))
                return msg.get("result", {})

    async def js(self, expr):
        r = await self.call("Runtime.evaluate", expression=expr,
                            returnByValue=True, awaitPromise=True)
        return r.get("result", {}).get("value")


def launch():
    p = subprocess.Popen(
        [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
         "--no-first-run", "--disable-extensions",
         "--remote-debugging-port=%d" % PORT, "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(60):
        try:
            urllib.request.urlopen("http://localhost:%d/json/version" % PORT, timeout=1).read()
            return p
        except Exception:
            time.sleep(0.5)
    p.terminate()
    raise SystemExit("chrome did not expose the debugging port")


def new_tab():
    # /json/new needs PUT in current Chrome; the launched about:blank tab
    # is already there, so take it rather than opening a second one.
    raw = urllib.request.urlopen(
        "http://localhost:%d/json/list" % PORT, timeout=10).read()
    for t in json.loads(raw.decode("utf-8")):
        if t.get("type") == "page" and t.get("webSocketDebuggerUrl"):
            return t["webSocketDebuggerUrl"]
    raise SystemExit("no page target available")


async def run_page(cdp, label, path, width):
    tag = "%s @%d" % (label, width)

    await cdp.call("Emulation.setDeviceMetricsOverride",
                   width=width, height=812, deviceScaleFactor=2, mobile=True)
    await cdp.call("Page.navigate", url=BASE + path)

    for _ in range(80):
        if await cdp.js("document.readyState") == "complete":
            break
        await asyncio.sleep(0.1)
    await asyncio.sleep(0.4)

    vw = await cdp.js("document.documentElement.clientWidth")
    check("viewport really is %d: %s" % (width, tag), vw == width, "got %s" % vw)

    check("no sideways scrolling: " + tag,
          await cdp.js("document.documentElement.scrollWidth <= "
                       "document.documentElement.clientWidth + 1"))

    check("Menu button is visible: " + tag,
          await cdp.js("(function(){var t=document.getElementById('navToggle');"
                       "return !!t && t.offsetParent!==null;})()"))

    h = await cdp.js("(function(){var t=document.getElementById('navToggle');"
                     "return t?Math.round(t.getBoundingClientRect().height):0;})()")
    check("touch target >= 44px: " + tag, h >= 44, "%spx" % h)

    check("menu starts closed: " + tag,
          await cdp.js("document.getElementById('navMenu').hasAttribute('hidden')"))

    # OPEN
    await cdp.js("document.getElementById('navToggle').click()")
    await asyncio.sleep(0.15)
    check("click opens the menu: " + tag,
          await cdp.js("document.getElementById('navToggle')"
                       ".getAttribute('aria-expanded')==='true'"))
    check("panel is revealed: " + tag,
          await cdp.js("!document.getElementById('navMenu').hasAttribute('hidden')"))

    hrefs = await cdp.js(
        "Array.prototype.map.call(document.querySelectorAll('#navMenu a'),"
        "function(a){return a.getAttribute('href');}).join(',')")
    got = (hrefs or "").split(",")
    for want in EXPECTED_LINKS:
        check("menu offers %s: %s" % (want, tag), want in got, hrefs)

    labels = await cdp.js(
        "Array.prototype.map.call(document.querySelectorAll('#navMenu a'),"
        "function(a){return a.textContent.trim();}).join('|')")
    for want in ["Home", "Care Guides", "Start assessment"]:
        check("menu names %s: %s" % (want, tag), want in (labels or ""), labels)

    rows = await cdp.js(
        "Math.round(Math.min.apply(null,Array.prototype.map.call("
        "document.querySelectorAll('#navMenu a'),function(a){"
        "return a.getBoundingClientRect().height;})))")
    check("menu rows >= 44px: " + tag, rows >= 44, "%spx" % rows)

    if width == WIDTHS[0] and label in ("home", "guides"):
        shot = await cdp.call("Page.captureScreenshot", format="png",
                              captureBeyondViewport=True)
        import base64
        out = os.path.join(SHOTS, "menu-open-%s-%d.png" % (label, width))
        with open(out, "wb") as f:
            f.write(base64.b64decode(shot["data"]))
        print("  shot  " + out)

    # ESCAPE closes and restores focus
    await cdp.js("document.dispatchEvent(new KeyboardEvent('keydown',"
                 "{key:'Escape',bubbles:true}))")
    await asyncio.sleep(0.15)
    check("Escape closes the menu: " + tag,
          await cdp.js("document.getElementById('navMenu').hasAttribute('hidden')"))
    check("Escape returns focus to the button: " + tag,
          await cdp.js("document.activeElement===document.getElementById('navToggle')"))

    # clicking a destination closes it
    await cdp.js("document.getElementById('navToggle').click()")
    await asyncio.sleep(0.1)
    await cdp.js("document.querySelector('#navMenu a').click()")
    await asyncio.sleep(0.2)
    check("choosing a destination closes the menu: " + tag,
          await cdp.js("document.getElementById('navMenu').hasAttribute('hidden')"))

    # and it must not survive a rotation to desktop width
    await cdp.call("Emulation.setDeviceMetricsOverride",
                   width=1280, height=800, deviceScaleFactor=1, mobile=False)
    await asyncio.sleep(0.1)
    await cdp.js("window.dispatchEvent(new Event('resize'))")
    await asyncio.sleep(0.15)
    check("menu cannot survive into desktop width: " + tag,
          await cdp.js("document.getElementById('navMenu').hasAttribute('hidden')"))
    check("Menu button hides on desktop: " + tag,
          await cdp.js("document.getElementById('navToggle').offsetParent===null"))


def _have_websockets():
    import importlib.util
    return importlib.util.find_spec("websockets") is not None


async def main():
    import websockets
    if not os.path.isdir(SHOTS):
        os.makedirs(SHOTS)
    proc = launch()
    try:
        async with websockets.connect(new_tab(), max_size=40 * 1024 * 1024) as ws:
            cdp = CDP(ws)
            await cdp.call("Page.enable")
            await cdp.call("Runtime.enable")
            for width in WIDTHS:
                for label, path in PAGES:
                    await run_page(cdp, label, path, width)
    finally:
        proc.terminate()

    print("\n  %d passed, %d failed   (%d assertions)" % (passed, failed, passed + failed))
    sys.exit(0 if failed == 0 else 1)


if not _have_websockets():
    print("  SKIPPED: the `websockets` package is not installed here.")
    print("  This suite drives a real browser over the DevTools Protocol;")
    print("  the portable suites are test.js, check-guides.js and")
    print("  build-guides.py.")
    sys.exit(0)

if CHROME is None:
    print("  SKIPPED: no Chrome or Chromium on this machine.")
    print("  This suite drives a real browser; the portable suites are")
    print("  test.js, check-guides.js and build-guides.py.")
    sys.exit(0)

asyncio.run(main())
