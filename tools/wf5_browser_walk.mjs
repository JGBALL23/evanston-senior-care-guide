/* Workflow #5 real-browser walk over the Chrome DevTools Protocol.

   Run:   node tools/wf5_browser_walk.mjs            (serves _dist locally)
          node tools/wf5_browser_walk.mjs <url>      (walks a live site)
   Node 22+ has WebSocket built in; on Node 20/21 add --experimental-websocket.

   Finds Edge or Chrome on Windows, Chrome/Chromium on macOS and Linux, or
   the binary named in BROWSER_BIN. Submits NOTHING: the navigator never
   calls /api, and the assessment is completed only to reach its result.

   What it proves that tools/test_paying_nav.js cannot: the DOM order of the
   five options matches getRoutes for all 54 answer combinations, Back and
   Start again behave at every stage, both beacons fire exactly once per
   visit, every assessment level hands its care type across and shows it,
   "Not sure" after a prefill never produces a care level, the assessment's
   own result DOM and resultLevelId are untouched by the navigator, page
   load does not steal focus, the entry link scrolls the navigator into view
   on a second click, and touch targets are at least 44px on a phone. */
import { spawn } from "node:child_process";
import { existsSync, readFileSync, readdirSync, statSync, mkdtempSync } from "node:fs";
import { tmpdir, homedir } from "node:os";
import { createServer } from "node:http";
import { join, extname, resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(HERE, "..");
const P = createRequire(import.meta.url)(join(ROOT, "paying-nav.js"));

/* ---------- browser ---------- */
function findBrowser() {
  const cands = [process.env.BROWSER_BIN,
    "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
    "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/usr/bin/google-chrome", "/usr/bin/google-chrome-stable", "/usr/bin/chromium", "/usr/bin/chromium-browser",
    "/snap/bin/chromium"].filter(Boolean);
  for (const c of cands) if (existsSync(c)) return c;
  /* Playwright's own Chromium, if it is installed anywhere usual. */
  for (const base of ["/opt/pw-browsers", join(homedir(), ".cache", "ms-playwright")]) {
    try {
      for (const d of readdirSync(base)) {
        for (const tail of ["chrome-linux64/chrome", "chrome-linux/chrome", "chrome-mac/Chromium.app/Contents/MacOS/Chromium", "chrome-win/chrome.exe"]) {
          const f = join(base, d, tail);
          if (existsSync(f)) return f;
        }
      }
    } catch { /* not there */ }
  }
  return null;
}

/* ---------- static server for _dist ---------- */
const TYPES = { ".html": "text/html; charset=utf-8", ".css": "text/css", ".js": "text/javascript", ".txt": "text/plain",
  ".png": "image/png", ".ico": "image/x-icon", ".xml": "application/xml", ".webp": "image/webp", ".svg": "image/svg+xml" };
function serveDist(port) {
  const dist = join(ROOT, "_dist");
  const server = createServer((req, res) => {
    let p = decodeURIComponent(new URL(req.url, "http://x").pathname);
    if (p.endsWith("/")) p += "index.html";
    let f = join(dist, p);
    if (!f.startsWith(dist)) { res.writeHead(403); return res.end(); }
    if (existsSync(f) && statSync(f).isDirectory()) f = join(f, "index.html");
    if (!existsSync(f)) { res.writeHead(404); return res.end("not found"); }
    res.writeHead(200, { "Content-Type": TYPES[extname(f)] || "application/octet-stream", "Cache-Control": "no-store" });
    res.end(readFileSync(f));
  });
  return new Promise((ok) => server.listen(port, "127.0.0.1", () => ok(server)));
}

/* ---------- CDP client (same shape as browser-test.mjs) ---------- */
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let id = 0;
function makeClient(ws) {
  const pending = new Map(); const events = [];
  ws.addEventListener("message", (ev) => {
    const msg = JSON.parse(ev.data);
    if (msg.id && pending.has(msg.id)) { const { resolve, reject } = pending.get(msg.id); pending.delete(msg.id); msg.error ? reject(new Error(JSON.stringify(msg.error))) : resolve(msg.result); }
    else if (msg.method) events.push(msg);
  });
  const send = (method, params = {}, sessionId) => new Promise((resolve, reject) => {
    const myId = ++id; pending.set(myId, { resolve, reject });
    ws.send(JSON.stringify({ id: myId, method, params, sessionId }));
    setTimeout(() => { if (pending.has(myId)) { pending.delete(myId); reject(new Error(method + " timed out")); } }, 30000);
  });
  return { send, events };
}
function openSocket(url) {
  return new Promise((resolve, reject) => {
    const ws = new WebSocket(url);
    ws.addEventListener("open", () => resolve(ws));
    ws.addEventListener("error", (e) => reject(new Error("socket error " + (e.message || ""))));
  });
}

/* ---------- checks ---------- */
const results = []; let ctx = "";
function check(name, ok, detail = "") {
  results.push({ name: ctx + " " + name, ok, detail });
  if (!ok) console.log(`FAIL  ${ctx} ${name}  ${detail}`);
}
const LEVEL_ANSWERS = { independent: [0, 0, 0, 0, 0, 3], assisted: [2, 0, 1, 1, 0, 3], memory: [2, 3, 1, 3, 0, 4],
  skilled: [3, 0, 2, 3, 0, 4], rehab: [2, 0, 1, 1, 1, 3], no_need: [0, 0, 0, 0, 0, 0] };

async function main() {
  const BIN = findBrowser();
  if (!BIN) { console.log("SKIP: no Chrome, Edge or Chromium found; set BROWSER_BIN"); process.exit(2); }
  const PORT = 8937, CDP = 9397;
  let base = process.argv[2] || "";
  let server = null;
  if (!base) { server = await serveDist(PORT); base = `http://127.0.0.1:${PORT}`; }
  base = base.replace(/\/$/, "");
  console.log("BROWSER: " + BIN + "\nTARGET:  " + base);

  const profile = mkdtempSync(join(tmpdir(), "wf5-walk-"));
  const proc = spawn(BIN, ["--headless=new", `--remote-debugging-port=${CDP}`, `--user-data-dir=${profile}`,
    "--disable-gpu", "--no-sandbox", "--no-first-run", "--no-default-browser-check", "--hide-scrollbars", "--mute-audio"], { stdio: "ignore" });
  let wsUrl = null;
  for (let i = 0; i < 60 && !wsUrl; i++) {
    try { const j = await (await fetch(`http://127.0.0.1:${CDP}/json/version`)).json(); wsUrl = j.webSocketDebuggerUrl; } catch { await sleep(250); }
  }
  if (!wsUrl) throw new Error("browser did not expose a debugging socket");
  const browser = makeClient(await openSocket(wsUrl));

  try {
    for (const [name, width, height, mobile] of [["desktop", 1280, 800, false], ["mobile-390", 390, 844, true]]) {
      ctx = `[${name}]`;
      const { targetId } = await browser.send("Target.createTarget", { url: "about:blank" });
      const { sessionId } = await browser.send("Target.attachToTarget", { targetId, flatten: true });
      const send = (m, p = {}) => browser.send(m, p, sessionId);
      await send("Page.enable"); await send("Runtime.enable"); await send("Network.enable");
      await send("Emulation.setDeviceMetricsOverride", { width, height, deviceScaleFactor: mobile ? 2 : 1, mobile });
      if (mobile) await send("Emulation.setTouchEmulationEnabled", { enabled: true });

      const ev = async (expression) => {
        const r = await send("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true });
        if (r.exceptionDetails) throw new Error(r.exceptionDetails.text + " " + (r.exceptionDetails.exception || {}).description);
        return r.result.value;
      };
      const seen = () => browser.events.filter((e) => e.method === "Network.requestWillBeSent" && e.sessionId === sessionId)
        .map((e) => { try { return new URL(e.params.request.url).pathname; } catch { return ""; } }).filter((p) => p.startsWith("/t/"));
      const fresh = async () => {
        browser.events.length = 0;
        await send("Page.navigate", { url: base + "/" }); await sleep(1500);
      };
      const W = "document.getElementById('paying-nav-widget')";
      const heading = () => ev(`(${W}.querySelector('.paynav__question')||{}).textContent||''`);
      /* Scroll the control into view first, the way a finger or a mouse
         must, so the page's own focus and scroll handling is exercised. */
      const click = (sel) => ev(`(function(){var e=${W}.querySelector(${JSON.stringify(sel)}); if(!e) return false; e.scrollIntoView({block:'center',behavior:'instant'}); e.click(); return true;})()`);
      const choose = (v) => click(`[data-pay-value="${v}"]`);
      const routeTitles = () => ev(`Array.from(${W}.querySelectorAll('.paynav__route h4')).map(h=>h.textContent)`);
      const count = (sel) => ev(`${W}.querySelectorAll(${JSON.stringify(sel)}).length`);
      const headingInView = () => ev(`(function(){var h=${W}.querySelector('.paynav__question'); if(!h) return false; var r=h.getBoundingClientRect(); var n=document.querySelector('nav'); var nh=n?n.getBoundingClientRect().height:0; return r.top>=nh-1 && r.bottom<=window.innerHeight;})()`);
      const sectionTop = () => ev(`Math.round(document.getElementById('paying-nav').getBoundingClientRect().top)`);
      const completeAssessment = async (answers) => {
        await ev(`document.querySelector('#quiz [data-aud="parent"]').click()`); await sleep(120);
        for (const i of answers) { await ev(`document.querySelector('#quiz .opt[data-i="${i}"]').click()`); await sleep(120); }
        for (let t = 0; t < 40 && !(await ev(`!!document.querySelector('#quiz .res__name')`)); t++) await sleep(100);
      };

      /* 1. initial state */
      await fresh();
      check("widget renders question 1", (await heading()).includes("What kind of care"));
      check("six care choices", await count(".paynav__choice") === 6);
      check("page load does not move focus into the navigator", !String(await ev(`(document.activeElement&&document.activeElement.className)||'body'`)).includes("paynav"));
      check("no beacon fired before interaction", !seen().some((b) => b.includes("pay-nav")));
      check("no-JS fallback text replaced", !(await ev(`${W}.textContent`)).includes("Enable JavaScript"));

      /* 2. all 54 combinations */
      await fresh();
      let combos = 0, orderOk = 0, countOk = 0, headingOk = 0;
      for (const care of Object.keys(P.CARE)) for (const vet of ["yes", "no", "unsure"]) for (const pol of ["yes", "no", "unsure"]) {
        if (!(await heading()).includes("What kind of care")) await click("[data-pay-restart]");
        await choose(care);
        if (mobile && combos === 0) check("mobile: question 2 heading is in view after answering question 1", await headingInView());
        await choose(vet); await choose(pol);
        const titles = await routeTitles();
        combos++;
        if (titles.length === 5) countOk++;
        if (JSON.stringify(titles) === JSON.stringify(P.getRoutes(care, vet, pol).map((r) => r.title))) orderOk++;
        const h = (await heading()).trim();
        if (h === (care === "unsure" ? "Nothing assumed about the type of care" : P.CARE[care])) headingOk++;
        if (mobile && combos === 1) check("mobile: results heading is in view after answering question 3", await headingInView());
      }
      check("54 combinations walked", combos === 54, String(combos));
      check("every result shows exactly 5 options", countOk === 54, countOk + "/54");
      check("DOM order matches getRoutes for every combination", orderOk === 54, orderOk + "/54");
      check("results heading names the chosen care, or says nothing was assumed", headingOk === 54, headingOk + "/54");
      check("start beacon fired exactly once for the visit", seen().filter((b) => b === "/t/pay-nav-started.txt").length === 1, seen().filter((b) => b.includes("started")).length + "x");
      check("completed beacon fired exactly once for the visit", seen().filter((b) => b === "/t/pay-nav-completed.txt").length === 1, seen().filter((b) => b.includes("completed")).length + "x");
      const links = await ev(`Array.from(${W}.querySelectorAll('.paynav__links a')).map(a=>({href:a.getAttribute('href'),target:a.getAttribute('target'),rel:a.getAttribute('rel')}))`);
      check("external links open in a new tab with noopener", links.filter((l) => l.href.startsWith("http")).every((l) => l.target === "_blank" && /noopener/.test(l.rel || "")));
      check("site links stay in the same tab", links.filter((l) => l.href.startsWith("/")).every((l) => !l.target));
      check("no 404 among the pages the navigator links to", await ev(`(async()=>{var hs=${JSON.stringify(links.filter((l) => l.href.startsWith("/") && !l.href.startsWith("/#")).map((l) => l.href))}; for (var h of hs){ var r=await fetch(h,{method:'GET',cache:'no-store'}); if(!r.ok) return h+' -> '+r.status; } return 'ok';})()`) === "ok");

      /* 2b. the order is explained, never asserted; links fit the care type */
      await fresh();
      await choose("unsure"); await choose("no"); await choose("no");
      let wtext = await ev(`${W}.textContent`);
      check("'Not sure' results say they are in no particular order", wtext.includes("In no particular order"));
      check("'Not sure' results mark nothing as worth checking first", !wtext.includes("Worth checking first") && !wtext.includes("Start here") && await count(".paynav__route--lead") === 0);
      check("'Not sure' results carry the reason for the order", wtext.includes("nothing here is ranked"));
      await click("[data-pay-restart]");
      await choose("unsure"); await choose("yes"); await choose("no");
      wtext = await ev(`${W}.textContent`);
      check("a 'yes' on 'Not sure' moves VA up and says why, in the visitor's own answer", (await routeTitles())[0] === "VA benefits" && wtext.includes("Moved up because you answered Yes") && await count(".paynav__route--lead") === 1);
      await click("[data-pay-restart]");
      await choose("skilled"); await choose("no"); await choose("no");
      wtext = await ev(`${W}.textContent`);
      const skilledHrefs = await ev(`Array.from(${W}.querySelectorAll('.paynav__links a')).map(a=>a.getAttribute('href'))`);
      check("skilled nursing: nothing links to assisted-living costs", !skilledHrefs.includes("/guides/assisted-living-cost-illinois/"), skilledHrefs.join(" "));
      check("skilled nursing: private pay names the nursing-home figures", wtext.includes("What a nursing home usually costs"));
      check("skilled nursing: Medicare links its skilled-nursing-facility page", skilledHrefs.some((h) => /skilled-nursing-facility/.test(h)));
      check("skilled nursing: the first card is 'worth checking first', not 'start here'", wtext.includes("Worth checking first") && !wtext.includes("Start here"));
      check("skilled nursing: the order is explained for this care type", wtext.includes("Ordered for skilled nursing") && wtext.includes("Long-stay nursing-home care"));
      await click("[data-pay-restart]");
      await choose("rehab"); await choose("no"); await choose("no");
      const rehabHrefs = await ev(`Array.from(${W}.querySelectorAll('.paynav__links a')).map(a=>a.getAttribute('href'))`);
      check("rehabilitation: nothing links to assisted-living costs", !rehabHrefs.includes("/guides/assisted-living-cost-illinois/"));
      check("rehabilitation: the cost-section link resolves on this page", await ev(`!!document.getElementById('cost')`) && rehabHrefs.includes("/#cost"));

      /* 2c. discoverable from the site without a second call to action */
      await fresh();
      const menu = await ev(`Array.from(document.querySelectorAll('#navMenu a')).map(a=>a.textContent.trim())`);
      check("home page menu offers 'Paying for care' before 'Start assessment'", menu.indexOf("Paying for care") > 0 && menu.indexOf("Paying for care") < menu.indexOf("Start assessment"), menu.join(" | "));
      check("the nav's one call-to-action is still the assessment", await ev(`document.querySelector('.nav__cta').getAttribute('href')`) === "#assessment");
      await send("Page.navigate", { url: base + "/guides/illinois-medicaid-long-term-care/" }); await sleep(1200);
      const gmenu = await ev(`Array.from(document.querySelectorAll('#navMenu a')).map(a=>a.textContent.trim())`);
      check("a guide's menu offers 'Paying for care'", gmenu.includes("Paying for care"), gmenu.join(" | "));
      check("a paying guide carries one quiet payment line and still exactly one button", await ev(`document.querySelectorAll('.related__pay').length`) === 1 && await ev(`document.querySelectorAll('.btn.btn--primary').length`) === 1);
      check("the guide's payment link is a link, not a button", await ev(`(function(){var a=document.querySelector('.related__pay a'); return a && !a.className.includes('btn');})()`));
      browser.events.length = 0;
      await ev(`document.querySelector('.related__pay a').click()`); await sleep(2500);
      check("guide -> navigator: lands on the home page at the navigator", (await ev(`location.pathname + location.hash`)) === "/#paying-nav");
      const gtop = await sectionTop();
      check("guide -> navigator: section is in view", gtop > -40 && gtop < 200, String(gtop));
      check("guide -> navigator: the navigator is at its own question one, nothing assumed", (await heading()).includes("What kind of care"));
      check("guide -> navigator: counted as the third guide pathway, not as the assessment", seen().includes("/t/guide-choice-pay.txt") && !seen().includes("/t/guide-choice-assessment.txt") && !seen().includes("/t/guide-choice-tour.txt"));
      check("guide -> navigator: the six questions still open as usual", await ev(`!!document.querySelector('#quiz [data-aud="parent"]')`));
      await send("Page.navigate", { url: base + "/guides/check-illinois-inspection-records/" }); await sleep(1000);
      check("a guide that is not about paying carries no payment line", await ev(`document.querySelectorAll('.related__pay').length`) === 0);

      /* 3. Back at every stage, Change, restart, keyboard */
      await fresh();
      check("question 1 has no Back control", await count("[data-pay-back]") === 0);
      await choose("memory");
      check("question 2 shows the chosen care type", (await ev(`${W}.textContent`)).includes("Memory Care"));
      await click("[data-pay-back]");
      check("Back from question 2 returns to question 1", (await heading()).includes("What kind of care"));
      check("the earlier answer is still marked on question 1", await ev(`!!${W}.querySelector('[data-pay-value="memory"][aria-pressed="true"]')`));
      await choose("skilled"); await choose("yes");
      await click("[data-pay-back]");
      check("Back from question 3 returns to question 2", (await heading()).includes("Veteran"));
      check("the earlier Veteran answer is still marked", await ev(`!!${W}.querySelector('[data-pay-value="yes"][aria-pressed="true"]')`));
      await choose("no"); await choose("unsure");
      check("results shown", await count(".paynav__route") === 5);
      await click("[data-pay-back]");
      check("Back from results returns to question 3", (await heading()).includes("long-term-care insurance"));
      await choose("yes");
      check("changing question 3 after Back changes the result", (await routeTitles())[0] === "Long-term-care insurance");
      await fresh(); await choose("assisted");
      await click("[data-pay-change]");
      check("Change on question 2 returns to question 1 with the care marked", (await heading()).includes("What kind of care") && await ev(`!!${W}.querySelector('[data-pay-value="assisted"][aria-pressed="true"]')`));
      await choose("rehab"); await choose("no"); await choose("no");
      await click("[data-pay-restart]");
      check("Start again returns to question 1 with nothing marked", (await heading()).includes("What kind of care") && await count('[aria-pressed="true"]') === 0);
      await ev(`${W}.querySelector('[data-pay-value="assisted"]').focus()`);
      await send("Input.dispatchKeyEvent", { type: "keyDown", key: "Enter", code: "Enter", windowsVirtualKeyCode: 13, text: "\r" });
      await send("Input.dispatchKeyEvent", { type: "keyUp", key: "Enter", code: "Enter", windowsVirtualKeyCode: 13 });
      await sleep(150);
      check("keyboard Enter activates a choice", (await heading()).includes("Veteran"));

      /* 4. prefill from every assessment level; invariance */
      for (const [level, answers] of Object.entries(LEVEL_ANSWERS)) {
        await fresh();
        await completeAssessment(answers);
        const before = await ev(`document.getElementById('quiz').innerHTML`);
        const levelBefore = await ev(`resultLevelId`);
        const expectCare = level === "no_need" ? "unsure" : level;
        check(`${level}: the result offers the payment entry`, await ev(`document.querySelectorAll('#quiz [data-pay-nav-care]').length`) === 1);
        check(`${level}: the entry carries only the care id`, await ev(`document.querySelector('#quiz [data-pay-nav-care]').getAttribute('data-pay-nav-care')`) === expectCare);
        await ev(`document.querySelector('#quiz [data-pay-nav-care]').click()`); await sleep(1800);
        check(`${level}: hash moved to #paying-nav`, await ev(`location.hash`) === "#paying-nav");
        const top = await sectionTop();
        check(`${level}: navigator scrolled into view`, top > -40 && top < 200, String(top));
        const h = await heading();
        if (expectCare === "unsure") check(`${level}: starts at question 1, nothing assumed`, h.includes("What kind of care"), h.trim());
        else {
          check(`${level}: skips to question 2`, h.includes("Veteran"), h.trim());
          check(`${level}: the carried-over care type is visible`, (await ev(`${W}.textContent`)).includes(P.CARE[level]));
          check(`${level}: the carried-over care type can be changed`, await count("[data-pay-change]") === 1);
        }
        check(`${level}: start beacon fired on prefill`, seen().includes("/t/pay-nav-started.txt"));
        if (expectCare === "unsure") await choose("unsure");
        await choose("unsure"); await choose("unsure");
        check(`${level}: results rendered`, await count(".paynav__route") === 5);
        check(`${level}: assessment result DOM unchanged by the navigator`, (await ev(`document.getElementById('quiz').innerHTML`)) === before);
        check(`${level}: resultLevelId unchanged (${levelBefore})`, (await ev(`resultLevelId`)) === levelBefore);
        if (expectCare !== "unsure") {
          await click("[data-pay-back]"); await click("[data-pay-back]"); await click("[data-pay-back]");
          check(`${level}: Back reaches question 1 with the result's care marked`, (await heading()).includes("What kind of care") && await ev(`!!${W}.querySelector('[data-pay-value="${level}"][aria-pressed="true"]')`));
          await choose("unsure"); await choose("unsure"); await choose("unsure");
          check(`${level}: 'Not sure' after a prefill yields 'nothing assumed', not ${level}`, (await heading()).trim() === "Nothing assumed about the type of care");
          check(`${level}: resultLevelId still unchanged after 'Not sure'`, (await ev(`resultLevelId`)) === levelBefore);
        }
        await ev(`window.scrollTo(0,0)`); await sleep(200);
        await ev(`document.querySelector('#quiz [data-pay-nav-care]').click()`); await sleep(1800);
        const top2 = await sectionTop();
        check(`${level}: a second click on the entry still scrolls to the navigator`, top2 > -40 && top2 < 200, String(top2));
      }

      /* 5. phone ergonomics */
      if (mobile) {
        await fresh();
        const sizes = await ev(`Array.from(${W}.querySelectorAll('button')).map(b=>({t:b.textContent.trim().slice(0,20),h:b.getBoundingClientRect().height}))`);
        check("every choice is at least 44px tall", sizes.every((s) => s.h >= 44), JSON.stringify(sizes.filter((s) => s.h < 44)));
        await choose("assisted");
        const back = await ev(`(function(){var b=${W}.querySelector('[data-pay-back]');var r=b.getBoundingClientRect();return {h:r.height,w:r.width};})()`);
        check("Back is at least 44px tall and full width", back.h >= 44 && back.w >= 300, JSON.stringify(back));
        await choose("no"); await choose("no");
        const acts = await ev(`Array.from(${W}.querySelectorAll('.paynav__actions button')).map(b=>({t:b.textContent.trim(),h:b.getBoundingClientRect().height}))`);
        check("result action controls are at least 44px tall", acts.every((a) => a.h >= 44), JSON.stringify(acts));
        check("no horizontal overflow on the results view", !(await ev(`document.documentElement.scrollWidth > window.innerWidth + 1`)));
      }
      await send("Page.close").catch(() => {});
    }
  } finally {
    proc.kill();
    if (server) server.close();
  }
  const failed = results.filter((r) => !r.ok);
  console.log(`\n${results.length - failed.length}/${results.length} Workflow #5 browser checks passed`);
  for (const f of failed) console.log("  FAIL " + f.name + (f.detail ? "   " + f.detail : ""));
  process.exit(failed.length ? 1 : 0);
}
main().catch((e) => { console.error(e); process.exit(1); });
