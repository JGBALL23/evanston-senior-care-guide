# -*- coding: utf-8 -*-
"""Behavioural test for /t/inquiry-submitted.txt.

Runs against an ISOLATED deploy whose blob store is
`visit-attribution-TEST`, so nothing here touches the authoritative
production lead records.

Asserts the event is silent on: form view, client-side validation
failure, and a server-rejected payload. Asserts it fires exactly once on
a server-confirmed save.
"""
import asyncio, datetime, json, shutil, subprocess, sys, tempfile, time
import urllib.request, websockets

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORT = 9343
BASE = sys.argv[1]
EVENT = "/t/inquiry-submitted.txt"

passed = 0
failed = 0


def check(name, ok, detail=""):
    global passed, failed
    if ok:
        passed += 1
        print("  PASS  " + name)
    else:
        failed += 1
        print("  FAIL  %s   %s" % (name, detail))


def utc():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M:%SZ")


async def main():
    profile = tempfile.mkdtemp(prefix="inq-")
    p = subprocess.Popen(
        [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox", "--no-first-run",
         "--user-data-dir=" + profile, "--remote-debugging-port=%d" % PORT, "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(60):
        try:
            urllib.request.urlopen("http://localhost:%d/json/version" % PORT, timeout=1).read()
            break
        except Exception:
            time.sleep(0.5)
    raw = urllib.request.urlopen("http://localhost:%d/json/list" % PORT, timeout=10).read()
    ws_url = [t["webSocketDebuggerUrl"] for t in json.loads(raw) if t.get("type") == "page"][0]

    hits = []
    n = [0]
    async with websockets.connect(ws_url, max_size=50 * 1024 * 1024) as ws:
        def pump(msg):
            if msg.get("method") == "Network.requestWillBeSent":
                u = msg["params"]["request"]["url"]
                if "/t/" in u:
                    hits.append(u.replace(BASE, ""))

        async def call(mth, **params):
            n[0] += 1
            i = n[0]
            await ws.send(json.dumps({"id": i, "method": mth, "params": params}))
            while True:
                msg = json.loads(await ws.recv())
                pump(msg)
                if msg.get("id") == i:
                    return msg.get("result", {})

        async def js(e):
            r = await call("Runtime.evaluate", expression=e, returnByValue=True, awaitPromise=True)
            return r.get("result", {}).get("value")

        async def settle(sec):
            end = time.time() + sec
            while time.time() < end:
                try:
                    pump(json.loads(await asyncio.wait_for(ws.recv(), timeout=0.25)))
                except asyncio.TimeoutError:
                    pass

        await call("Network.enable")
        await call("Page.enable")
        await call("Runtime.enable")

        async def to_form():
            await call("Page.navigate", url=BASE + "/")
            for _ in range(90):
                if await js("document.readyState") == "complete":
                    break
                await settle(0.2)
            await settle(1.2)
            await js("document.querySelector('.hero .btn--primary').click()")
            await settle(0.8)
            for _ in range(8):
                g = await js("(function(){var o=document.querySelector('#quiz .opt:not([hidden])');"
                             "if(!o)return 'none';o.click();return 'ok';})()")
                await settle(0.6)
                if g == "none":
                    break
            await settle(2.0)

        # ---------- 1. form view only ----------
        print("\n  [1] open the form, submit nothing   %s" % utc())
        hits.clear()
        await to_form()
        has_form = await js("!!document.querySelector('#planForm,form.plan__form,.plan form')")
        check("the inquiry form rendered", bool(has_form), str(has_form))
        check("viewing the form fires NO confirmed-lead event", EVENT not in hits, str(hits))

        # ---------- 2. client-side validation failure ----------
        print("\n  [2] submit with required fields empty   %s" % utc())
        hits.clear()
        await js("""(function(){
          var f=document.querySelector('#planForm,form.plan__form,.plan form');
          if(!f) return 'noform';
          var b=f.querySelector('button[type=submit],button');
          if(b){b.click();}
          return 'clicked';})()""")
        await settle(2.0)
        check("validation failure fires NO confirmed-lead event", EVENT not in hits, str(hits))

        # ---------- 3. server rejection ----------
        print("\n  [3] server-rejected payload   %s" % utc())
        hits.clear()
        rej = await js("""(async function(){
          var r = await fetch('/api/plan-visit',{method:'POST',
            headers:{'content-type':'application/json'},
            body: JSON.stringify({firstName:'A',lastName:'B',email:'a@b.co',
                                  consent:true, careLevel:'NOT_A_LEVEL'})});
          return r.status;})()""")
        await settle(1.5)
        check("the server rejected the bad payload", rej == 400, "status %s" % rej)
        check("server rejection fires NO confirmed-lead event", EVENT not in hits, str(hits))

        # ---------- 4. confirmed save ----------
        print("\n  [4] valid fake submission (isolated TEST store)   %s" % utc())
        hits.clear()
        res = await js("""(function(){
          var f=document.querySelector('#planForm,form.plan__form,.plan form');
          if(!f) return 'noform';
          function set(sel,v){var e=f.querySelector(sel); if(!e) return false;
            e.value=v; e.dispatchEvent(new Event('input',{bubbles:true})); return true;}
          var ok1=set('[name=firstName],#firstName','Testrun');
          var ok2=set('[name=lastName],#lastName','Isolated');
          var ok3=set('[name=email],#email','testrun@example.invalid');
          var c=f.querySelector('input[type=checkbox]');
          if(c && !c.checked){c.click();}
          return JSON.stringify({ok1:ok1,ok2:ok2,ok3:ok3,consent:!!(c&&c.checked)});})()""")
        print("      filled: %s" % res)
        await js("""(function(){
          var f=document.querySelector('#planForm,form.plan__form,.plan form');
          var b=f.querySelector('button[type=submit],button');
          if(b) b.click();})()""")
        await settle(6.0)

        confirmed = await js("document.body.innerText.indexOf('Your interest has been recorded')!==-1")
        check("the server confirmed the save", bool(confirmed), str(confirmed))
        check("confirmed save FIRES the event", EVENT in hits, str(hits))
        check("it fires exactly once", hits.count(EVENT) == 1, str(hits.count(EVENT)))

        ref = await js("""(function(){var e=document.querySelector('.plan__ref code');
          return e?e.textContent.trim():null;})()""")
        print("      isolated TEST record id: %s" % ref)

    print("\n  %d passed, %d failed" % (passed, failed))
    p.terminate()
    time.sleep(1)
    shutil.rmtree(profile, ignore_errors=True)
    sys.exit(0 if failed == 0 else 1)


asyncio.run(main())
