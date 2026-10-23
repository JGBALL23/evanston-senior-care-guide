# -*- coding: utf-8 -*-
"""Fresh-session production trace of the beacon funnel.

Launches Chrome with a THROWAWAY user-data-dir so there is no cache, no
storage and no prior state, drives the real assessment on the live
domain, and records every /t/ request with its response status, whether
it was served from cache, and the Netlify request id.

Prints UTC timestamps so the events can be matched against an
Observability window.
"""
import asyncio, datetime, json, os, shutil, subprocess, sys, tempfile, time
import urllib.request, websockets

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORT = 9341
BASE = "https://evanstonseniorcareguide.com"


def utc():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


async def main():
    profile = tempfile.mkdtemp(prefix="esg-fresh-")
    p = subprocess.Popen(
        [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox", "--no-first-run",
         "--user-data-dir=" + profile, "--disable-extensions",
         "--remote-debugging-port=%d" % PORT, "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(60):
        try:
            urllib.request.urlopen("http://localhost:%d/json/version" % PORT, timeout=1).read()
            break
        except Exception:
            time.sleep(0.5)
    raw = urllib.request.urlopen("http://localhost:%d/json/list" % PORT, timeout=10).read()
    ws_url = [t["webSocketDebuggerUrl"] for t in json.loads(raw) if t.get("type") == "page"][0]

    reqs = {}          # requestId -> url
    events = []        # (url, status, fromCache, nfid)
    n = [0]

    print("  fresh profile: %s" % profile)
    print("  START (UTC): %s" % utc())

    async with websockets.connect(ws_url, max_size=50 * 1024 * 1024) as ws:
        async def pump(msg):
            m = msg.get("method")
            pr = msg.get("params", {})
            if m == "Network.requestWillBeSent":
                u = pr["request"]["url"]
                if "/t/" in u:
                    reqs[pr["requestId"]] = u
            elif m == "Network.responseReceived":
                rid = pr.get("requestId")
                if rid in reqs:
                    r = pr["response"]
                    hdrs = {k.lower(): v for k, v in (r.get("headers") or {}).items()}
                    events.append((reqs[rid], r.get("status"),
                                   bool(r.get("fromDiskCache") or r.get("fromPrefetchCache")),
                                   hdrs.get("x-nf-request-id", "-"),
                                   hdrs.get("cache-status", "-")))
            elif m == "Network.loadingFailed":
                rid = pr.get("requestId")
                if rid in reqs:
                    events.append((reqs[rid], "FAILED:" + str(pr.get("errorText")),
                                   False, "-", "-"))

        async def call(mth, **params):
            n[0] += 1
            i = n[0]
            await ws.send(json.dumps({"id": i, "method": mth, "params": params}))
            while True:
                msg = json.loads(await ws.recv())
                await pump(msg)
                if msg.get("id") == i:
                    return msg.get("result", {})

        async def js(e):
            r = await call("Runtime.evaluate", expression=e, returnByValue=True)
            return r.get("result", {}).get("value")

        async def settle(sec):
            end = time.time() + sec
            while time.time() < end:
                try:
                    msg = json.loads(await asyncio.wait_for(ws.recv(), timeout=0.25))
                    await pump(msg)
                except asyncio.TimeoutError:
                    pass

        await call("Network.enable")
        await call("Page.enable")
        await call("Runtime.enable")
        await call("Network.setCacheDisabled", cacheDisabled=False)   # realistic
        await call("Emulation.setDeviceMetricsOverride", width=390, height=844,
                   deviceScaleFactor=2, mobile=True)

        await call("Page.navigate", url=BASE + "/")
        for _ in range(90):
            if await js("document.readyState") == "complete":
                break
            await settle(0.2)
        await settle(1.5)

        print("  clicking the hero CTA ...")
        await js("document.querySelector('.hero .btn--primary').click()")
        await settle(1.0)

        for i in range(8):
            got = await js("""(function(){
              var o=document.querySelector('#quiz .opt:not([hidden])');
              if(!o){return 'none';} o.click(); return 'ok';})()""")
            await settle(0.7)
            if got == "none":
                break

        await settle(2.5)

        done = await js("""(function(){
          var r=document.querySelector('#result,.res');
          return r? (r.offsetParent!==null) : false;})()""")
        print("  result section visible: %s" % done)

    print("  END (UTC): %s" % utc())
    print("\n  %-46s %-8s %-6s %s" % ("PATH", "STATUS", "CACHE", "NF-REQUEST-ID"))
    seen = set()
    for u, st, cached, nfid, cs in events:
        path = u.replace(BASE, "")
        if path in seen:
            continue
        seen.add(path)
        print("  %-46s %-8s %-6s %s" % (path[:46], st, "YES" if cached else "no", nfid))
    print("\n  distinct /t/ requests: %d" % len(seen))

    p.terminate()
    time.sleep(1)
    shutil.rmtree(profile, ignore_errors=True)


asyncio.run(main())
