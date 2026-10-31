/* Simple first, details when needed: the real-browser gate.

   Run:   node tools/simple_first_check.mjs            (serves _dist locally)
          node tools/simple_first_check.mjs <url>      (checks a live site)
          SHOTS=/some/dir node tools/simple_first_check.mjs   (also saves screenshots)
   Node 22+ has WebSocket built in; on Node 20/21 add --experimental-websocket.

   Finds Edge or Chrome on Windows, Chrome/Chromium on macOS and Linux, or
   the binary named in BROWSER_BIN. Submits NOTHING: the inquiry form is
   never posted, and the assessment is completed only to reach its result.

   What it proves, on a phone (390x844) and a desktop (1280x800):
     - the homepage's one question and one button are on the first screen,
       and the words a visitor sees without tapping anything stay under the
       budget (details rows closed, menus closed);
     - a result page keeps its budget too, leads with the level in plain
       words, and puts "See what it costs" within reach;
     - every "More" row is a real <details> element, at least 48px tall, and
       opens and closes from the keyboard with Enter;
     - a link that lands inside a closed row opens it (#tour, #evaluating);
     - the text a visitor must read is 18px or larger, buttons 56px or taller;
     - Westminster Place is named in the tour form's heading, and the
       homepage's "Ask about a tour" shortcut counts as a form view, not as
       a guide pathway;
     - the payment navigator's question 1 explains each choice in plain
       words and each result card leads with one plain line;
     - no beacon path named in app.js or paying-nav.js is missing from _dist/t;
     - nothing scrolls sideways. */
import { spawn } from "node:child_process";
import { existsSync, readFileSync, readdirSync, statSync, mkdtempSync, writeFileSync, mkdirSync } from "node:fs";
import { tmpdir, homedir } from "node:os";
import { createServer } from "node:http";
import { join, extname, resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

/* Every harness announces itself with one fixed User-Agent so the host's
   request log can exclude it by exact match. A test run must never be
   counted as a family. The string is identical in every harness; test.js
   checks that it stays so. */
const HARNESS_UA = "ESCG-harness/1 (automated test; +https://evanstonseniorcareguide.com/)";
const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(HERE, "..");

/* Word budgets: the words a visitor sees without tapping anything, with
   every details row closed. Measured 2026-10-30 at about 710 on the
   homepage (down from 2,284) and about 710 on a result (down from roughly
   3,000). The result count includes the inquiry form, its three
   disclosures and the consent sentence, which stay word for word, and the
   homepage count includes the navigator's six explained choices. The
   budgets sit just above those figures so a paragraph added above the fold
   fails here before anyone sees it. */
const BUDGET = { home: 760, result: 760 };

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

/* ---------- CDP client ---------- */
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

/* The words a visitor sees without tapping anything: text nodes that
   have a rendered box, are not inside a closed details row (its summary
   still counts), and are not hidden by display:none or visibility. A
   closed <details> keeps its text in the DOM, and Chromium's innerText
   still reports it, so innerText cannot be the measure. */
const VISIBLE_WORDS_IN = (rootSel) => `(function(){
  var root = document.querySelector(${JSON.stringify(rootSel)}); if (!root) return -1;
  var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  var words = 0, node;
  while ((node = walker.nextNode())) {
    var text = node.nodeValue.trim(); if (!text) continue;
    var el = node.parentElement, ok = true, cur = el;
    while (cur && cur !== root.parentElement) {
      if (cur.tagName === 'DETAILS' && !cur.open) {
        var sum = cur.querySelector(':scope > summary');
        if (!sum || !sum.contains(node)) { ok = false; break; }
      }
      if (cur.tagName === 'SCRIPT' || cur.tagName === 'STYLE' || cur.tagName === 'NOSCRIPT') { ok = false; break; }
      cur = cur.parentElement;
    }
    if (!ok) continue;
    var cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden' || !el.getClientRects().length) continue;
    words += text.split(/\\s+/).length;
  }
  return words; }())`;
const VISIBLE_WORDS = VISIBLE_WORDS_IN("body");
const OPEN_ROWS = `document.querySelectorAll('details[open]').length`;
const IN_VIEW = (sel) => `(function(){ var e=document.querySelector(${JSON.stringify(sel)}); if(!e) return 'missing';
  var r=e.getBoundingClientRect(); return (r.top >= 0 && r.bottom <= innerHeight) ? 'in' : ('out:' + Math.round(r.top) + '/' + Math.round(r.bottom)); }())`;
const HEIGHTS = (sel) => `Array.from(document.querySelectorAll(${JSON.stringify(sel)})).map(function(e){ var r=e.getBoundingClientRect(); return Math.round(r.height); })`;
const FONTS = (sel) => `Array.from(document.querySelectorAll(${JSON.stringify(sel)})).filter(function(e){ return e.getClientRects().length; }).map(function(e){ return parseFloat(getComputedStyle(e).fontSize); })`;
const NO_SIDEWAYS = `!(document.documentElement.scrollWidth > document.documentElement.clientWidth + 1)`;

async function main() {
  const BIN = findBrowser();
  if (!BIN) { console.log("SKIP: no Chrome, Edge or Chromium found; set BROWSER_BIN"); process.exit(2); }
  const PORT = 8941, CDP = 9401;
  let base = process.argv[2] || "";
  let server = null;
  if (!base) { server = await serveDist(PORT); base = `http://127.0.0.1:${PORT}`; }
  base = base.replace(/\/$/, "");
  const SHOTS = process.env.SHOTS || "";
  if (SHOTS) mkdirSync(SHOTS, { recursive: true });
  console.log("BROWSER: " + BIN + "\nTARGET:  " + base);

  /* beacons: every literal in the two scripts has a file behind it */
  ctx = "[beacons]";
  const literals = new Set();
  for (const f of ["app.js", "paying-nav.js"]) {
    for (const m of readFileSync(join(ROOT, f), "utf8").matchAll(/"\/t\/([a-z0-9-]+)\.txt"/g)) literals.add(m[1]);
  }
  for (const n of literals) check("file behind /t/" + n + ".txt", existsSync(join(ROOT, "_dist", "t", n + ".txt")));
  check("the result beacons still exist per level", ["independent", "assisted", "memory", "skilled", "rehab", "no_need"]
    .every((l) => existsSync(join(ROOT, "_dist", "t", "result-" + l + ".txt"))));

  const profile = mkdtempSync(join(tmpdir(), "simple-first-"));
  const proc = spawn(BIN, ["--headless=new", `--user-agent=${HARNESS_UA}`, `--remote-debugging-port=${CDP}`, `--user-data-dir=${profile}`,
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
      /* Jumps are judged by where they land, not by the animation: with
         reduced motion the page's own CSS makes every scroll instant. */
      await send("Emulation.setEmulatedMedia", { features: [{ name: "prefers-reduced-motion", value: "reduce" }] });

      const ev = async (expression) => {
        const r = await send("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true });
        if (r.exceptionDetails) throw new Error(r.exceptionDetails.text + " " + (r.exceptionDetails.exception || {}).description);
        return r.result.value;
      };
      const seen = () => browser.events.filter((e) => e.method === "Network.requestWillBeSent" && e.sessionId === sessionId)
        .map((e) => { try { return new URL(e.params.request.url).pathname; } catch { return ""; } }).filter((p) => p.startsWith("/t/"));
      const goto = async (path) => {
        browser.events.length = 0;
        await send("Page.navigate", { url: "about:blank" }); await sleep(150);
        await send("Page.navigate", { url: base + path }); await sleep(1400);
      };
      const shot = async (file) => {
        if (!SHOTS) return;
        const { data } = await send("Page.captureScreenshot", { format: "png" });
        writeFileSync(join(SHOTS, `${name}-${file}.png`), Buffer.from(data, "base64"));
      };
      /* smooth scrolling takes a moment; wait for a condition rather than a clock */
      const settles = async (expression) => {
        for (let t = 0; t < 30; t++) { if (await ev(expression)) return true; await sleep(100); }
        return await ev(expression);
      };
      const pressEnterOn = async (sel) => {
        await ev(`document.querySelector(${JSON.stringify(sel)}).focus()`);
        await send("Input.dispatchKeyEvent", { type: "keyDown", key: "Enter", code: "Enter", windowsVirtualKeyCode: 13, text: "\r" });
        await send("Input.dispatchKeyEvent", { type: "keyUp", key: "Enter", code: "Enter", windowsVirtualKeyCode: 13 });
        await sleep(120);
      };
      const rowsOperable = async (label) => {
        const n = await ev(`document.querySelectorAll('details.more').length`);
        let operable = 0, tall = 0, closedAtStart = 0;
        for (let i = 0; i < n; i++) {
          const sel = `details.more:nth-of-type(1)`;
          const was = await ev(`document.querySelectorAll('details.more')[${i}].open`);
          if (!was) closedAtStart++;
          const h = await ev(`Math.round(document.querySelectorAll('details.more')[${i}].querySelector('summary').getBoundingClientRect().height)`);
          if (h >= 48) tall++;
          await ev(`document.querySelectorAll('details.more')[${i}].querySelector('summary').focus()`);
          await send("Input.dispatchKeyEvent", { type: "keyDown", key: "Enter", code: "Enter", windowsVirtualKeyCode: 13, text: "\r" });
          await send("Input.dispatchKeyEvent", { type: "keyUp", key: "Enter", code: "Enter", windowsVirtualKeyCode: 13 });
          await sleep(60);
          const opened = await ev(`document.querySelectorAll('details.more')[${i}].open`);
          await send("Input.dispatchKeyEvent", { type: "keyDown", key: "Enter", code: "Enter", windowsVirtualKeyCode: 13, text: "\r" });
          await send("Input.dispatchKeyEvent", { type: "keyUp", key: "Enter", code: "Enter", windowsVirtualKeyCode: 13 });
          await sleep(60);
          const closed = await ev(`document.querySelectorAll('details.more')[${i}].open`);
          if (opened === !was && closed === was) operable++;
          void sel;
        }
        check(`${label}: every More row opens and closes with Enter`, n > 0 && operable === n, `${operable}/${n}`);
        check(`${label}: every More row is at least 48px tall`, tall === n, `${tall}/${n}`);
        return { n, closedAtStart };
      };

      /* ---------- 1. the homepage ---------- */
      await goto("/");
      check("no sideways scroll on the homepage", await ev(NO_SIDEWAYS));
      check("every More row starts closed", (await ev(OPEN_ROWS)) === 0, String(await ev(OPEN_ROWS)));
      const homeWords = await ev(VISIBLE_WORDS);
      check(`homepage shows ${homeWords} words before any tap (budget ${BUDGET.home})`, homeWords <= BUDGET.home);
      check("the one question is the h1", (await ev(`document.querySelector('h1').textContent`)).replace(/\s+/g, " ").includes("Not sure what kind of help"));
      check("the h1 is inclusive, not parent-only", (await ev(`document.querySelector('h1').textContent`)).includes("you or someone you love"));
      check("the h1 is on the first screen", (await ev(IN_VIEW("h1"))) === "in", await ev(IN_VIEW("h1")));
      check("the one button is on the first screen", (await ev(IN_VIEW(".hero__actions .btn--primary"))) === "in", await ev(IN_VIEW(".hero__actions .btn--primary")));
      check("the button says what happens next", (await ev(`document.querySelector('.hero__actions .btn--primary').textContent`)).includes("Start the 6 questions"));
      check("the hero button is at least 56px tall", (await ev(HEIGHTS(".hero__actions .btn--primary")))[0] >= 56);
      check("the hero offers the three shortcuts", await ev(`!!document.querySelector('.hero__skip a[href="#cost"]') && !!document.querySelector('.hero__skip a[href="#paying-nav"]') && !!document.querySelector('.hero__skip a[href="/?tour=form#plan-visit"]')`));
      check("how-it-works has three numbered steps", (await ev(`document.querySelectorAll('.steps__list li').length`)) === 3);
      check("the reading text is 18px or larger", (await ev(FONTS(".hero__lede, .hero__meta--lead, .steps__list p, .quiz__intro, .quiz__privacy, .cat__desc, .cost__plain, .paynav__intro, .lead__p, .about__lead, .more > summary, .narrow-p"))).every((f) => f >= 18));
      check("the hero lede is 20px or larger", (await ev(FONTS(".hero__lede")))[0] >= 20);
      check("five kinds of living, independent living first", JSON.stringify(await ev(`Array.from(document.querySelectorAll('.cat__name')).map(function(e){return e.textContent.trim();})`)).startsWith('["Independent Living"') && (await ev(`document.querySelectorAll('.cat__name').length`)) === 5);
      check("the money words are explained one tap away", (await ev(`(document.querySelector('.words') || {}).textContent || ''`)).includes("Medicaid") && (await ev(`(document.querySelector('.words') || {}).textContent || ''`)).includes("Supportive Living"));
      check("the twelve tour questions are kept, one tap away", (await ev(`document.querySelectorAll('#tour .asks li').length`)) === 12);
      check("the Supportive Living explanation is kept, one tap away", (await ev(`document.querySelector('#cost').textContent`)).includes("Expect two charges, not one"));
      await shot("01-home");
      const homeRows = await rowsOperable("homepage");
      check("homepage More rows are all closed on load", homeRows.closedAtStart === homeRows.n);
      /* a link into a closed row opens it */
      await ev(`document.querySelector('.nav__links a[href="#tour"]') ? document.querySelector('.nav__links a[href="#tour"]').click() : (function(){ location.hash = 'tour'; })()`);
      await sleep(300);
      check("a jump to #tour opens the twelve questions", await ev(`document.querySelector('#tour details').open === true`));
      check("the opened questions are in view", await settles(`(function(){ var r=document.querySelector('#tour .asks li').getBoundingClientRect(); return r.top >= 0 && r.top < innerHeight; }())`));
      /* the payment navigator's first question explains each choice */
      check("navigator question 1 explains every choice in plain words", (await ev(`document.querySelectorAll('#paying-nav-widget .paynav__choice-sub').length`)) === 6);
      check("navigator choices are at least 56px tall", (await ev(HEIGHTS("#paying-nav-widget .paynav__choice"))).every((h) => h >= 56));
      /* tap the last choice with it sitting low on the screen, the way a
         thumb does, so the next question would render under the bar if
         nothing kept it visible */
      await ev(`(function(){ var b=document.querySelector('#paying-nav-widget [data-pay-value="rehab"]'); b.scrollIntoView({block:'end'}); }())`); await sleep(200);
      await ev(`document.querySelector('#paying-nav-widget [data-pay-value="rehab"]').click()`); await sleep(400);
      check("navigator question 2 renders with its top line below the sticky bar", await ev(`document.getElementById('paying-nav-widget').firstElementChild.getBoundingClientRect().top >= document.getElementById('nav').getBoundingClientRect().bottom - 1`), String(await ev(`Math.round(document.getElementById('paying-nav-widget').firstElementChild.getBoundingClientRect().top - document.getElementById('nav').getBoundingClientRect().bottom)`)));
      await ev(`document.querySelector('#paying-nav-widget [data-pay-change]').click()`); await sleep(200);
      await ev(`document.querySelector('#paying-nav-widget [data-pay-value="assisted"]').click()`); await sleep(150);
      await ev(`document.querySelector('#paying-nav-widget [data-pay-value="no"]').click()`); await sleep(150);
      await ev(`(function(){ var b=document.querySelector('#paying-nav-widget [data-pay-value="no"]'); b.scrollIntoView({block:'end'}); }())`); await sleep(200);
      await ev(`document.querySelector('#paying-nav-widget [data-pay-value="no"]').click()`); await sleep(400);
      check("each result card leads with one plain line", (await ev(`document.querySelectorAll('#paying-nav-widget .paynav__plain').length`)) === 5);
      check("three full cards, then two compact rows under one quiet line", (await ev(`document.querySelectorAll('#paying-nav-widget .paynav__route--rest').length`)) === 2 && (await ev(`document.querySelectorAll('#paying-nav-widget .paynav__rest-h').length`)) === 1 && (await ev(`Array.from(document.querySelectorAll('#paying-nav-widget .paynav__route')).map(function(li,i){ return li.classList.contains('paynav__route--rest') === (i >= 3); }).every(Boolean)`)));
      check("the compact rows keep their plain line, their More row and their links", await ev(`Array.from(document.querySelectorAll('#paying-nav-widget .paynav__route--rest')).every(function(li){ return li.querySelector('.paynav__plain') && li.querySelector('details.more') && li.querySelectorAll('.paynav__links a').length >= 1; })`));
      check("the compact rows' plain lines stay readable (17px+)", (await ev(FONTS("#paying-nav-widget .paynav__route--rest .paynav__plain"))).every((f) => f >= 17));
      check("the compact rows' More rows are at least 44px tall", (await ev(HEIGHTS("#paying-nav-widget .paynav__route--rest details.more > summary"))).every((h) => h >= 44));
      check("a compact row still states a limitation plainly (Medicare on assisted living)", /does not pay for assisted living/.test(await ev(`(Array.from(document.querySelectorAll('#paying-nav-widget .paynav__route--rest')).find(function(li){ return /Medicare/.test(li.querySelector('h4').textContent); }) || {}).textContent || ''`)));
      const NAV_BOTTOM = `document.getElementById('nav').getBoundingClientRect().bottom`;
      check("the navigator's top line sits below the sticky bar after the last answer", await ev(`document.getElementById('paying-nav-widget').firstElementChild.getBoundingClientRect().top >= ${NAV_BOTTOM} - 1`), String(await ev(`Math.round(document.getElementById('paying-nav-widget').firstElementChild.getBoundingClientRect().top - (${NAV_BOTTOM}))`)));
      check("each result card keeps its full text and links one tap away", (await ev(`document.querySelectorAll('#paying-nav-widget .paynav__route details.more .paynav__links a').length`)) >= 5);
      check("the reason for the order is one tap away", (await ev(`document.querySelector('#paying-nav-widget').textContent`)).includes("Assisted living in Illinois is usually private-pay"));
      check("navigator More rows are at least 48px tall", (await ev(HEIGHTS("#paying-nav-widget details.more > summary"))).every((h) => h >= 48));
      check("navigator card plain lines are 18px or larger", (await ev(FONTS("#paying-nav-widget .paynav__plain"))).every((f) => f >= 18));
      await shot("02-navigator-result");

      /* ---------- 2. a result for every level ---------- */
      for (const [level, answers] of Object.entries(LEVEL_ANSWERS)) {
        await goto("/#assessment");
        await ev(`document.querySelector('#quiz [data-aud="parent"]').click()`); await sleep(120);
        check(`${level}: answer buttons are at least 56px tall`, (await ev(HEIGHTS("#quiz .opt"))).every((h) => h >= 56));
        let underBar = 0;
        for (const i of answers) {
          /* tap with the option low on the screen, the way a thumb does */
          await ev(`(function(){ var b=document.querySelector('#quiz .opt[data-i="${i}"]'); b.scrollIntoView({block:'end'}); }())`); await sleep(120);
          await ev(`document.querySelector('#quiz .opt[data-i="${i}"]').click()`); await sleep(260);
          if (await ev(`document.getElementById('quiz').getBoundingClientRect().top < document.getElementById('nav').getBoundingClientRect().bottom - 1`)) underBar++;
        }
        for (let t = 0; t < 40 && !(await ev(`!!document.querySelector('#quiz .res__name')`)); t++) await sleep(100);
        await sleep(200);
        check(`${level}: each question and the result render with the box top below the sticky bar`, underBar === 0, underBar + " under the bar");
        const words = await ev(VISIBLE_WORDS_IN("#quiz"));
        check(`${level}: result shows ${words} words before any tap (budget ${BUDGET.result})`, words <= BUDGET.result);
        check(`${level}: every More row on the result starts closed`, (await ev(`document.querySelectorAll('#quiz details[open]').length`)) === 0);
        check(`${level}: the form is headed by the community's name`, (await ev(`(document.querySelector('#plan-visit .plan__h')||{}).textContent||''`)).includes("Ask Westminster Place about a tour"));
        check(`${level}: the form is marked optional`, (await ev(`(document.querySelector('#plan-visit .plan__optional')||{}).textContent||''`)).includes("Optional"));
        check(`${level}: the limits stay in plain view`, (await ev(`(document.querySelector('#quiz .res__limit')||{}).textContent||''`)).includes("not a diagnosis"));
        check(`${level}: no sideways scroll`, await ev(NO_SIDEWAYS));
        if (level !== "no_need") {
          check(`${level}: the result leads with the level in plain words`, (await ev(`((document.querySelector('#quiz .res__plain')||{}).textContent||'').length`)) > 20);
          check(`${level}: the reasoning and the visitor's answers sit behind "Why this result?", closed`, await ev(`(function(){ var d=document.querySelector('#why-this-result details'); return !!d && !d.open && d.querySelector('summary').textContent.trim() === 'Why this result?' && d.querySelectorAll('.why__item').length >= 1; }())`));
          check(`${level}: the hedged lead is inside that row`, /may be the level of support worth\s+exploring first/.test(await ev(`document.querySelector('#why-this-result').textContent`)) || level === "independent");
          check(`${level}: page order is answer, costs, how to pay, then the optional inquiry`, await ev(`(function(){ var q=document.getElementById('quiz'); var order=['.res__next-btn','#costs .res__cost-basis','#costs .paynav__entry-btn','#plan-visit']; var tops=order.map(function(s){ var e=q.querySelector(s); return e ? e.getBoundingClientRect().top : NaN; }); return tops.every(function(t,i){ return !isNaN(t) && (i===0 || t > tops[i-1]); }); }())`));
          check(`${level}: the form keeps its disclosures, consent and privacy link`, await ev(`(function(){ var f=document.getElementById('plan-visit'); return !!f.querySelector('.plan__contrast') && !!f.querySelector('.plan__disclose') && !!f.querySelector('#plan-consent') && !!f.querySelector('.plan__privacy'); }())`));
          check(`${level}: the plain line is 20px or larger`, (await ev(FONTS("#quiz .res__plain")))[0] >= 20);
          await ev(`document.getElementById('quiz').scrollIntoView({block:'start'})`); await sleep(200);
          const btnTop = await ev(`(function(){ var b=document.querySelector('#quiz .res__next-btn'); return b ? Math.round(b.getBoundingClientRect().top) : -1; }())`);
          check(`${level}: "See what it costs" is within two screens of the result`, btnTop >= 0 && btnTop < innerHeightOf(height) * 2, btnTop + "px");
          check(`${level}: the next-step button is at least 56px tall`, (await ev(HEIGHTS("#quiz .res__next-btn")))[0] >= 56);
          await shot(`03-result-${level}`);
          /* the next step reaches the costs, and the evaluating link opens its row */
          await ev(`document.querySelector('#quiz .res__next-btn').click()`);
          check(`${level}: the next step lands on the costs`, await settles(`(function(){ var r=document.getElementById('costs').getBoundingClientRect(); return r.top > -40 && r.top < innerHeight; }())`));
          check(`${level}: the cost figure or its honest absence stays in view, the source one tap away`, await ev(`!!document.querySelector('#costs .res__cost-basis') && !!document.querySelector('#costs details.more')`));
          check(`${level}: the payment entry is a tall button`, (await ev(HEIGHTS("#costs .paynav__entry-btn")))[0] >= 56);
          await ev(`document.querySelector('#quiz a[href="#evaluating"]').click()`); await sleep(500);
          check(`${level}: the evaluating link opens its questions`, await ev(`document.querySelector('#evaluating details').open === true`));
        } else {
          check(`${level}: independent living stays in the first screen (unchanged)`, await ev(`!!document.querySelector('#quiz .res__block.il .il__h')`));
          await shot(`03-result-${level}`);
        }
        const rows = await rowsOperable(level + " result");
        check(`${level}: the form's own disclosures stay above the first field`, await ev(`(function(){ var s=document.getElementById('plan-visit'); var f=s.querySelector('input[name=firstName]'); var d=s.querySelector('.plan__disclose'); return d.getBoundingClientRect().top < f.getBoundingClientRect().top; }())`));
        check(`${level}: consent stays unticked and required`, await ev(`(function(){ var c=document.getElementById('plan-consent'); return c && !c.checked && c.required; }())`));
        void rows;
      }

      /* ---------- 3. the homepage shortcut to the form ---------- */
      await goto("/?tour=form#plan-visit");
      check("the shortcut opens the form with no assessment", await ev(`!!document.getElementById('plan-visit') && document.querySelectorAll('#quiz .opt[data-i]').length === 0`));
      const hint = await ev(`(function(){ var s=document.getElementById('plan-interest'); var h=s && s.closest('label').querySelector('.plan__hint'); return h ? h.textContent.replace(/\\s+/g,' ').trim() : ''; }())`);
      check("the shortcut says nothing was pre-filled, and credits no guide", hint.includes("nothing here was pre-filled") && !hint.includes("guide link"), hint.slice(0, 80));
      check("the shortcut counts as a form view, not as a guide pathway", seen().includes("/t/direct-inquiry-form-view.txt") && !seen().includes("/t/guide-choice-tour.txt"), seen().join(" "));
      check("a guide's own link still counts as the guide pathway", await (async () => { await goto("/?tour=independent#plan-visit"); return seen().includes("/t/guide-choice-tour.txt"); })());
      await shot("04-direct-form");

      await send("Page.close").catch(() => {});
    }
  } finally {
    proc.kill();
    if (server) server.close();
  }

  const passed = results.filter((r) => r.ok).length;
  console.log(`\n${passed}/${results.length} Simple First checks passed`);
  process.exit(passed === results.length ? 0 : 1);
}
function innerHeightOf(h) { return h; }

main().catch((e) => { console.error(e); process.exit(1); });
