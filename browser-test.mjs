/* Real browser test over the Chrome DevTools Protocol.
   Run:  node --experimental-websocket browser-test.mjs <url>

   Drives actual Edge: clicks through all six questions, captures every
   console message and every network request, screenshots mobile and
   desktop, and asserts the funnel beacons genuinely fired.
   Nothing here is simulated. */

const URL_UNDER_TEST = process.argv[2] || "https://evanston-senior-care-guide.netlify.app/";
const WIDTH = Number(process.argv[3]) || 390;
const PORT = 9333 + (WIDTH % 7);
const EDGE = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";

import { spawn } from "node:child_process";
import { writeFileSync, mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const results = [];
const check = (name, ok, detail = "") => {
  results.push({ name, ok, detail });
  console.log(`${ok ? "PASS" : "FAIL"}  ${name.padEnd(52)} ${detail}`);
};

const profile = mkdtempSync(join(tmpdir(), "edge-test-"));
const edge = spawn(EDGE, [
  "--headless=new",
  `--remote-debugging-port=${PORT}`,
  `--user-data-dir=${profile}`,
  "--disable-gpu", "--no-first-run", "--no-default-browser-check",
  "--hide-scrollbars", "--mute-audio"
], { stdio: "ignore" });

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function targetWs() {
  for (let i = 0; i < 40; i++) {
    try {
      const res = await fetch(`http://127.0.0.1:${PORT}/json/version`);
      const json = await res.json();
      if (json.webSocketDebuggerUrl) return json.webSocketDebuggerUrl;
    } catch { /* not up yet */ }
    await sleep(250);
  }
  throw new Error("Edge did not expose a debugging socket");
}

let id = 0;
function makeClient(ws) {
  const pending = new Map();
  const events = [];
  ws.addEventListener("message", (ev) => {
    const msg = JSON.parse(ev.data);
    if (msg.id && pending.has(msg.id)) {
      const { resolve, reject } = pending.get(msg.id);
      pending.delete(msg.id);
      msg.error ? reject(new Error(JSON.stringify(msg.error))) : resolve(msg.result);
    } else if (msg.method) {
      events.push(msg);
    }
  });
  const send = (method, params = {}, sessionId) =>
    new Promise((resolve, reject) => {
      const myId = ++id;
      pending.set(myId, { resolve, reject });
      ws.send(JSON.stringify({ id: myId, method, params, sessionId }));
      setTimeout(() => {
        if (pending.has(myId)) { pending.delete(myId); reject(new Error(method + " timed out")); }
      }, 30000);
    });
  return { send, events };
}

function openSocket(url) {
  return new Promise((resolve, reject) => {
    const ws = new WebSocket(url);
    ws.addEventListener("open", () => resolve(ws));
    ws.addEventListener("error", (e) => reject(new Error("socket error " + e.message)));
  });
}

async function main() {
  const wsUrl = await targetWs();
  const browserWs = await openSocket(wsUrl);
  const browser = makeClient(browserWs);

  const { targetId } = await browser.send("Target.createTarget", { url: "about:blank" });
  const { sessionId } = await browser.send("Target.attachToTarget", { targetId, flatten: true });
  const page = {
    send: (m, p = {}) => browser.send(m, p, sessionId),
    events: browser.events
  };

  await page.send("Page.enable");
  await page.send("Runtime.enable");
  await page.send("Log.enable");
  await page.send("Network.enable");

  /* ---- mobile viewport first: that is where families read this ---- */
  await page.send("Emulation.setDeviceMetricsOverride",
    { width: WIDTH, height: 844, deviceScaleFactor: 2, mobile: true });

  await page.send("Page.navigate", { url: URL_UNDER_TEST });
  await sleep(4000);

  const requests = () => page.events
    .filter((e) => e.method === "Network.requestWillBeSent")
    .map((e) => e.params.request.url);

  const consoleProblems = () => page.events
    .filter((e) =>
      (e.method === "Log.entryAdded" && ["error", "warning"].includes(e.params.entry.level)) ||
      (e.method === "Runtime.exceptionThrown"))
    .map((e) => e.params.entry
      ? `${e.params.entry.level}: ${e.params.entry.text}`
      : `exception: ${e.params.exceptionDetails?.text}`);

  const evaluate = async (expression) => {
    const r = await page.send("Runtime.evaluate",
      { expression, returnByValue: true, awaitPromise: true });
    if (r.exceptionDetails) throw new Error(r.exceptionDetails.text);
    return r.result.value;
  };

  /* ---- 1. page loaded and rendered ---- */
  const title = await evaluate("document.title");
  check("page loads", typeof title === "string" && title.includes("Evanston"), title.slice(0, 48));

  const landedFired = requests().some((u) => u.includes("/t/landed.txt"));
  check("tracking: landed beacon fired", landedFired);

  /* ---- 2. first question rendered by app.js ---- */
  const q1 = await evaluate("document.querySelector('.q__text')?.textContent || ''");
  check("assessment renders question 1", q1.length > 20, q1.slice(0, 46) + "…");

  const optCount = await evaluate("document.querySelectorAll('.opt').length");
  check("question 1 has four options", optCount === 4, "got " + optCount);

  /* ---- 3. nothing is asked for before the result ----
     The visit form exists, but only after a result has been shown.
     Up to that point there must be no field of any kind, so nobody
     is asked for anything in exchange for using the guide. */
  const inputs = await evaluate(
    "document.querySelectorAll('input,textarea,select,form').length");
  check("no form or input before the result", inputs === 0, "found " + inputs);

  /* ---- 4. click the real buttons through a real scenario ----
     "Left the stove on, wanders" → must reach Memory Care.          */
  const scenario = [2, 3, 1, 3, 0, 3];
  for (const pick of scenario) {
    await evaluate(`document.querySelectorAll('.opt')[${pick}].click()`);
    await sleep(260);
  }
  const resultName = await evaluate("document.querySelector('.res__name')?.textContent || ''");
  check("clicking through 6 questions reaches a result", resultName.length > 3, resultName);
  check("scenario 'stove left on' lands on Memory Care",
    resultName.trim() === "Memory Care", resultName);

  /* ---- the result must show 2-4 reasons in the family's own words ---- */
  const reasonCount = await evaluate("document.querySelectorAll('.why__item').length");
  check("result shows between 2 and 4 reasons",
    reasonCount >= 2 && reasonCount <= 4, "got " + reasonCount);

  const firstAnswer = await evaluate(
    "document.querySelector('.why__a')?.textContent || ''");
  check("each reason quotes the answer they chose",
    firstAnswer.includes("“") && firstAnswer.length > 12, firstAnswer.slice(0, 46));

  const headings = await evaluate(
    "JSON.stringify([...document.querySelectorAll('.res__h')].map(h=>h.textContent.trim()))");
  const hs = JSON.parse(headings || "[]");
  check("result follows the required hierarchy",
    hs[0] === "Why this result appeared" &&
    hs[1] === "What this type of care usually provides" &&
    hs[2] === "Questions to ask when evaluating options", hs.join(" / "));

  /* The Westminster heading carries the care level the visitor just
     landed on, instead of the old generic "A local option in Evanston". */
  check("Westminster heading names the care level",
    hs[3] === "Considering " + resultName.trim().toLowerCase() + " in Evanston?",
    hs[3]);
  check("generic Westminster heading is gone",
    !hs.some((h) => h.toLowerCase() === "a local option in evanston"));

  /* ---- the result must read as guidance, not as a diagnosis ---- */
  const summaryText = (await evaluate(
    "document.querySelector('.res__summary')?.textContent || ''"))
    .replace(/\s+/g, " ").trim().toLowerCase();
  check("result is hedged, not declarative",
    summaryText.includes("based on your answers") &&
    summaryText.includes("may be the level of support worth exploring first"),
    summaryText.slice(0, 58));
  ["has reached the point", "is the issue", "your parent needs",
   "needs actual", "can no longer", "no longer safe"].forEach((hard) => {
    check('result avoids diagnostic phrasing: "' + hard + '"',
      !summaryText.includes(hard));
  });

  /* ---- no numeric HTML entity may survive into rendered text ---- */
  const entityLeak = await evaluate(`
    (() => {
      const res = document.querySelector('.res');
      if (!res) return 'no result';
      const found = (res.innerText.match(/&#x?[0-9a-f]+;/gi) || []);
      return found.slice(0, 3).join(' ');
    })()`);
  check("no raw HTML entity in the rendered result", entityLeak === "",
    entityLeak || "clean");

  /* ---- the cost figure cannot be mistaken for Westminster's price ---- */
  const costBlock = (await evaluate(
    "document.querySelector('.res__cost')?.innerText || ''"))
    .replace(/\s+/g, " ").toLowerCase();
  /* Two shapes are legitimate, and which one appears depends on
     whether a credible survey figure exists for this level. The rule
     is conditional, and stricter than the old pair it replaces:

       a figure  -> must name the survey, link it, and say it is not
                    Westminster's rate
       no figure -> must explain the absence, and must carry no
                    dollar amount at all

     This scenario lands on Memory Care, which CareScout does not
     separately report, so the no-figure branch is the one exercised
     here. Both branches are asserted so neither can rot. */
  const hasFigure = /\$[0-9],[0-9]{3}/.test(costBlock);
  if (hasFigure) {
    check("sourced figure names the survey",
      costBlock.includes("carescout 2025 cost of care survey, published 2026"),
      costBlock.slice(0, 70));
    check("sourced figure links the survey",
      await evaluate(
        "Boolean(document.querySelector('.res__cost a[href*=\"carescout.com\"]'))") === true);
    check("sourced figure disclaims Westminster pricing",
      costBlock.includes("do not represent westminster place’s actual rates") ||
      costBlock.includes("do not represent westminster place's actual rates"),
      costBlock.slice(-70));
  } else {
    check("unsourced block explains why there is no figure",
      /does not (separately )?report an illinois/.test(costBlock) ||
      costBlock.includes("no statewide price is shown"),
      costBlock.slice(0, 70));
    check("unsourced block invents no dollar figure",
      !/\$[0-9],[0-9]{3}/.test(costBlock), costBlock.slice(0, 60));
  }

  /* Whichever branch rendered, a long-stay nursing median must never
     be presented as the cost of a short rehabilitation stay. */
  check("nursing and rehabilitation costs are not conflated",
    !(costBlock.includes("rehabilitation") && /\$[89],[0-9]{3}/.test(costBlock)),
    costBlock.slice(0, 60));

  /* Now exercise the OTHER branch for real. Assisted Living is the
     level CareScout does report, so this is the sourced path, and a
     conditional assertion that only ever runs one side is not a test. */
  await page.send("Page.navigate", { url: URL_UNDER_TEST });
  await sleep(3000);
  for (const pick of [2, 0, 1, 1, 0, 2]) {
    await evaluate(`document.querySelectorAll('.opt')[${pick}].click()`);
    await sleep(230);
  }
  const sourcedBlock = (await evaluate(
    "document.querySelector('.res__cost')?.innerText || ''"))
    .replace(/\s+/g, " ").toLowerCase();
  check("assisted living shows the verified CareScout figure",
    sourcedBlock.includes("$6,219"), sourcedBlock.slice(0, 56));
  check("the figure says what it measures",
    sourcedBlock.includes("illinois assisted living median"));
  check("the figure names the survey and its years",
    sourcedBlock.includes("carescout 2025 cost of care survey, published 2026"));
  const srcHref = await evaluate(
    "document.querySelector('.res__cost a')?.getAttribute('href') || ''");
  check("the source link points at the CareScout survey",
    srcHref === "https://assets.carescout.com/x/5c90319b6a/298701.pdf", srcHref);
  check("the source link opens in a new tab safely",
    await evaluate(`
      (() => {
        const a = document.querySelector('.res__cost a');
        return Boolean(a && a.target === '_blank' && /noopener/.test(a.rel));
      })()`) === true);
  check("the statewide figure is not presented as Westminster's rate",
    sourcedBlock.includes("do not represent westminster place’s actual rates") ||
    sourcedBlock.includes("do not represent westminster place's actual rates"),
    sourcedBlock.slice(-64));
  check("no retired cost figure appears anywhere on screen",
    !["7,400", "4,650", "7,850", "9,200"].some((stale) =>
      sourcedBlock.includes(stale)), sourcedBlock.slice(0, 50));

  const starting = await evaluate(
    "document.querySelector('.res__label')?.textContent || ''");
  check("result is framed as a starting point",
    starting.toLowerCase().includes("starting point"), starting);

  const fine = await evaluate("document.querySelector('.res__fine')?.textContent || ''");
  check("result refuses diagnosis, placement and coverage claims",
    fine.includes("not a diagnosis") && fine.includes("guarantee placement"),
    fine.slice(0, 44));

  const retake = await evaluate(
    "document.getElementById('restart')?.textContent || ''");
  check("retake assessment action present",
    retake.toLowerCase().includes("retake"), retake);

  /* ---- THE LOCAL OPTION, DISCLOSED ---- */
  const wpName = await evaluate("document.querySelector('.wp__name')?.textContent || ''");
  check("local option appears after the result",
    wpName.trim() === "Westminster Place", wpName);

  /* The disclosure is two paragraphs: the employment statement, then
     the fee and data statements. Both are read — a check that only
     saw the first would miss half of what is being promised. */
  const disclosure = await evaluate(
    "[...document.querySelectorAll('.wp__disclosure')].map(p => p.textContent).join(' ')");
  const d = disclosure.toLowerCase().replace(/\s+/g, " ");
  check("disclosure states the employment",
    d.includes("i work at westminster place"), d.slice(0, 48));
  check("disclosure states it is not official",
    d.includes("not an official westminster place website"));
  check("disclosure states no referral fees",
    d.includes("no referral fees") || d.includes("receive no referral"));
  /* Was "do not collect prospective residents' contact information".
     The visit form made that false, so the assertion now demands the
     narrower thing that is still true: the record is not passed on. */
  check("disclosure states why the information is collected",
    d.includes("used only to document that the visit originated through this resource"));
  check("disclosure states it is not shared with Westminster",
    d.includes("not automatically shared with westminster place"));
  check("disclosure states no referral fees",
    d.includes("i receive no referral fees"));
  check("disclosure states it was independently developed",
    d.includes("i independently developed this resource"));
  check("disclosure names the employment relationship",
    d.includes("because of my employment relationship"));
  check("disclosure states refusal to rank",
    d.includes("do not rank westminster place"));

  /* The disclosure must be in the same card as the buttons, and readable —
     not fine print. */
  const sameCard = await evaluate(`
    (() => {
      const card = document.querySelector('.wp');
      if (!card) return false;
      return Boolean(card.querySelector('.wp__disclosure')) &&
             Boolean(card.querySelector('a[href^="tel:"]'));
    })()`);
  check("disclosure sits with the action buttons", sameCard === true);

  const discSize = await evaluate(`
    parseFloat(getComputedStyle(document.querySelector('.wp__disclosure')).fontSize)`);
  check("disclosure is readable, not fine print", discSize >= 15.5, discSize + "px");

  /* The three actions must point at real, verified destinations. */
  const hrefs = await evaluate(`
    JSON.stringify([...document.querySelectorAll('.wp__actions a')].map(a => a.getAttribute('href')))`);
  const wpLinks = JSON.parse(hrefs || "[]");
  check("visit link points at the official community page",
    wpLinks.some((h) => h.includes("presbyterianliving.org/our-locations/westminster-place")),
    wpLinks[0]);
  /* The call link is no longer one fixed number. It routes to the
     team Westminster publishes for the assessed care level, so the
     assertion is that it is ONE OF their published lines — and, for
     this scenario (Memory Care), specifically the AL & Memory Care
     Sales line rather than the general switchboard. */
  const WP_PUBLISHED_TELS = [
    "tel:+18475703310",  // Independent Living Sales
    "tel:+18478661615",  // Assisted Living & Memory Care Sales
    "tel:+18474927780",  // Skilled Nursing Admissions
    "tel:+18475703422"   // General Inquiries (fallback only)
  ];
  const calls = wpLinks.filter((h) => h.startsWith("tel:"));
  check("call link is one of Westminster's published lines",
    calls.length === 1 && WP_PUBLISHED_TELS.includes(calls[0]), calls.join(" "));
  check("Memory Care routes to the AL & Memory Care team, not the general line",
    calls[0] === "tel:+18478661615", calls[0]);

  /* The external inquiry CTA was removed 2026-10-17. The guide has its
     own form; routing a family to a second form that asks the same
     questions was the detour this page exists to shorten. Asserted as
     an absence so it cannot quietly return. */
  check("no link to Westminster's own request form",
    !wpLinks.some((h) => h.includes("/westminster-place/contact/")),
    wpLinks.find((h) => h.includes("contact/")) || "absent");
  check("no source parameter on any Westminster link",
    !wpLinks.some((h) => /contact\/\?(src|utm)/.test(h)));
  check("the dropdown coaching note is gone from the DOM",
    (await evaluate("document.querySelectorAll('.wp__hear').length")) === 0);
  /* The direct contact options Joseph kept: phone, website, directions. */
  check("their own website is still linked",
    wpLinks.some((h) => h === "https://www.presbyterianliving.org/our-locations/westminster-place/"),
    wpLinks.join(" ").slice(0, 60));
  check("directions link uses the verified address",
    wpLinks.some((h) => h.includes("3200+Grant+Street+Evanston+IL+60201")), wpLinks[2]);

  /* And the state's own directory must be offered alongside. */
  const compare = await evaluate(
    "document.querySelector('.wp__compare a')?.getAttribute('href') || ''");
  check("state licensed-facility directory is offered",
    compare.includes("healthcarereportcard.illinois.gov"), compare);

  /* ---- the three Westminster actions must each fire a beacon ---- */
  /* Strip target and href first: the goal is to prove the tracking handler
     fires, not to open three tabs that steal the page out from under us. */
  await evaluate(`
    ['wp-call','idph'].forEach(name => {
      const el = document.querySelector('[data-beacon="' + name + '"]');
      if (el) { el.removeAttribute('target'); el.setAttribute('href', '#'); el.click(); }
    })`);
  await sleep(600);
  const wpUrls = requests();
  check("tracking: westminster card view fired",
    wpUrls.some((u) => u.includes("westminster-card-view")));
  check("tracking: westminster call click fired",
    wpUrls.some((u) => u.includes("westminster-call-click")));
  check("tracking: state directory click fired",
    wpUrls.some((u) => u.includes("state-directory-click")));

  /* The assessment itself must still never name a community. */
  const quizText = await evaluate(`
    (() => {
      const s = document.querySelector('.res__summary')?.textContent || '';
      const w = document.querySelector('.why')?.textContent || '';
      return (s + ' ' + w).toLowerCase();
    })()`);
  check("the result verdict itself names no community",
    quizText.indexOf("westminster") === -1, quizText.slice(0, 40));

  /* ---- 5. completion + result beacons actually hit the network ---- */
  await sleep(900);
  const urls = requests();
  check("tracking: assessment-started fired", urls.some((u) => u.includes("assessment-started")));
  check("tracking: q2 fired", urls.some((u) => u.includes("/t/q2.txt")));
  check("tracking: q4 fired", urls.some((u) => u.includes("/t/q4.txt")));
  check("tracking: assessment-completed fired", urls.some((u) => u.includes("assessment-completed")));
  check("tracking: result-memory fired", urls.some((u) => u.includes("result-memory")));

  const beaconStatuses = page.events
    .filter((e) => e.method === "Network.responseReceived" &&
                   e.params.response.url.includes("/t/"))
    .map((e) => e.params.response.status);
  check("every beacon returned 200",
    beaconStatuses.length > 0 && beaconStatuses.every((s) => s === 200),
    beaconStatuses.join(","));

  /* ---- 6. nothing personal is transmitted anywhere ---- */
  /* A tel: link and the destinations a visitor deliberately clicks are not
     third-party tracking. Only unrequested calls count. */
  const offsite = urls.filter((u) =>
    !u.startsWith(new URL(URL_UNDER_TEST).origin) &&
    !u.startsWith("tel:") && !u.startsWith("mailto:") &&
    /* input[type=date] makes Edge inline its own calendar icon as a
       data: URI. A data URI is bytes already in the page, not a call. */
    !u.startsWith("data:") && !u.startsWith("blob:") &&
    !u.includes("fonts.googleapis.com") &&
    !u.includes("fonts.gstatic.com") &&
    !u.includes("presbyterianliving.org") &&
    !u.includes("healthcarereportcard.illinois.gov") &&
    !u.includes("google.com/maps"));
  check("no third-party calls beyond the webfont", offsite.length === 0, offsite.join(" ") || "none");

  const postBodies = page.events
    .filter((e) => e.method === "Network.requestWillBeSent" &&
                   e.params.request.method !== "GET");
  check("no POST or PUT request is ever made", postBodies.length === 0,
    postBodies.map((e) => e.params.request.method).join(","));

  /* ---- 7. second scenario, verifying a different branch ---- */
  await evaluate("document.getElementById('restart').click()");
  await sleep(400);
  const rehab = [2, 0, 1, 1, 1, 2];
  for (const pick of rehab) {
    await evaluate(`document.querySelectorAll('.opt')[${pick}].click()`);
    await sleep(220);
  }
  const second = await evaluate("document.querySelector('.res__name')?.textContent || ''");
  check("scenario 'out of hospital, improving' lands on rehab",
    second.trim() === "Short-Term Rehabilitation", second);

  /* ---- 8. no provider or community name in the RENDERED dom ---- */
  const renderedText = await evaluate("document.body.innerText.toLowerCase()");
  const banned = ["sponsored", "schedule a tour", "schedule a visit",
    "book a tour", "paid placement", "we recommend", "best community"];
  /* The consent copy has to say the form "does not schedule a visit with
     Westminster Place" — saying so is the protection, so a phrase inside
     a denial does not count as an offer. Only an un-negated use counts. */
  const found = banned.filter((w) => {
    let from = 0;
    for (;;) {
      const at = renderedText.indexOf(w, from);
      if (at === -1) return false;
      const before = renderedText.slice(Math.max(0, at - 30), at);
      if (!/\b(does not|do not|doesn.t|never|no|not)\s*$/.test(before)) return true;
      from = at + w.length;
    }
  });
  check("no sales or sponsorship language in rendered page", found.length === 0, found.join(", "));
  check("if Westminster is named, the disclosure is on screen",
    !renderedText.includes("westminster place") ||
    renderedText.includes("i work at westminster place"));

  /* ---- 9. the trust statement survived the edits ---- */
  check("trust statement intact: takes no fees",
    renderedText.includes("no fees"));
  check("trust statement intact: cannot be steered",
    renderedText.includes("cannot be steered"));
  /* "does not collect your email" was retired by the visit form. What
     is still true, and now asserted instead: the assessment itself asks
     nothing, and assessment answers are never stored. */
  check("trust statement intact: assessment asks nothing about you",
    renderedText.includes("asks nothing about who you are"));

  /* The methodology claims sit inside a collapsed <details>, so
     innerText cannot see them. Read the element itself — a claim
     a visitor can open and read still has to be there. */
  const methodology = (await evaluate(
    "document.querySelector('details.src')?.textContent || ''")).toLowerCase();
  check("methodology states answers are never stored",
    methodology.includes("assessment answers are never collected, stored or"));
  check("methodology discloses the one form that collects anything",
    methodology.includes("planning to visit") &&
    methodology.includes("completely separate from the assessment"));
  check("methodology says skipping the form changes nothing",
    methodology.includes("skipping it changes"));
  /* "personally operated" was retired and replaced by the employment
     disclosure. The retired phrases are asserted as absences so a
     later edit cannot quietly reinstate them. */
  check("employment disclosure is rendered",
    renderedText.includes("i independently developed this resource") &&
    renderedText.includes("because of my employment relationship"));
  ["a personal project", "my personal project", "personally operated"]
    .forEach((gone) => {
      check('retired phrase absent on screen: "' + gone + '"',
        !renderedText.includes(gone));
    });
  check("stale independence claim is gone",
    !renderedText.includes("not a referral service") &&
    !renderedText.includes("an independent local resource"));

  /* ---- 10. sources section opens and the links are real ---- */
  await evaluate("document.querySelector('.src').setAttribute('open','')");
  await sleep(300);
  const srcLinks = await evaluate(
    "JSON.stringify([...document.querySelectorAll('.src__links a')].map(a=>a.href))");
  const links = JSON.parse(srcLinks || "[]");
  check("sources section lists at least 6 links", links.length >= 6, String(links.length));
  check("every source link is a deep link, not a homepage",
    links.every((u) => new URL(u).pathname.length > 2), links.length + " checked");

  /* ---- 11. mobile layout: nothing overflows the viewport ---- */
  const overflow = await evaluate(
    "document.documentElement.scrollWidth - document.documentElement.clientWidth");
  check("no horizontal overflow at " + WIDTH + "px", overflow <= 1, "overflow " + overflow + "px");

  const tapTargets = await evaluate(`
    [...document.querySelectorAll('a.btn,button.btn,.opt')]
      .map(el => Math.round(el.getBoundingClientRect().height))
      .filter(h => h > 0 && h < 44).length`);
  check("every tap target is at least 44px tall", tapTargets === 0, tapTargets + " too small");

  /* Diagnostic artefacts, not assertions. A full-page capture at
     deviceScaleFactor 2 grew past the 30s CDP timeout once the page
     got longer, and took the whole suite down with it — a failed
     screenshot was reported as a failed test run. Half scale keeps it
     readable, and the try/catch keeps an artefact from ever again
     deciding whether the site passed. */
  const snap = async (name, params) => {
    try {
      const shot = await page.send("Page.captureScreenshot", params);
      writeFileSync(name, Buffer.from(shot.data, "base64"));
    } catch (err) {
      console.log("note: screenshot skipped (" + name + "): " + err.message);
    }
  };
  await snap("shot-mobile-" + WIDTH + ".png", {
    format: "png",
    captureBeyondViewport: true,
    clip: {
      x: 0, y: 0, scale: 0.5,
      width: WIDTH,
      height: await evaluate("document.documentElement.scrollHeight")
    }
  });

  /* ---- 12. desktop layout ---- */
  await page.send("Emulation.setDeviceMetricsOverride",
    { width: 1280, height: 900, deviceScaleFactor: 1, mobile: false });
  await sleep(700);
  const overflowD = await evaluate(
    "document.documentElement.scrollWidth - document.documentElement.clientWidth");
  check("no horizontal overflow at 1280px", overflowD <= 1, "overflow " + overflowD + "px");
  await snap("shot-desktop.png", { format: "png" });

  /* ---- 14. KEYBOARD: the whole assessment without a mouse ---- */
  await page.send("Emulation.setDeviceMetricsOverride",
    { width: 1280, height: 900, deviceScaleFactor: 1, mobile: false });
  await page.send("Page.navigate", { url: URL_UNDER_TEST });
  await sleep(2600);

  /* rawKeyDown alone does not activate a button in Chromium — a real
     key press carries text. Tab needs no text; Enter and Space do. */
  const pressKey = async (key, code, keyCode, text) => {
    await page.send("Input.dispatchKeyEvent", Object.assign(
      { type: text ? "keyDown" : "rawKeyDown", key, code,
        windowsVirtualKeyCode: keyCode, nativeVirtualKeyCode: keyCode },
      text ? { text, unmodifiedText: text } : {}));
    await page.send("Input.dispatchKeyEvent",
      { type: "keyUp", key, code, windowsVirtualKeyCode: keyCode });
    await sleep(140);
  };

  /* Tab until an answer button has focus, then activate it with Enter. */
  let reachedOption = false;
  for (let i = 0; i < 25 && !reachedOption; i++) {
    await pressKey("Tab", "Tab", 9);
    reachedOption = await evaluate(
      "document.activeElement && document.activeElement.classList.contains('opt')");
  }
  check("every answer is reachable by keyboard", reachedOption === true,
    reachedOption ? "focused an option" : "never reached an option");

  const focusRing = await evaluate(`
    (() => {
      const el = document.activeElement;
      if (!el) return "none";
      const s = getComputedStyle(el);
      return s.outlineStyle + " " + s.outlineWidth;
    })()`);
  check("focused control shows a visible outline",
    focusRing.indexOf("none") === -1 && parseFloat(focusRing.split(" ")[1]) >= 2,
    focusRing);

  await pressKey("Enter", "Enter", 13, "\r");
  await sleep(300);
  const advanced = await evaluate(
    "document.querySelector('.q__count')?.textContent || ''");
  check("Enter advances the assessment", advanced.includes("2 of 6"), advanced);

  await evaluate("document.querySelector('.opt').focus()");
  await pressKey(" ", "Space", 32, " ");
  await sleep(260);
  const spaced = await evaluate("document.querySelector('.q__count')?.textContent || ''");
  check("Space also advances the assessment", spaced.includes("3 of 6"), spaced);

  /* Back out with the keyboard too — a dead end is an accessibility bug. */
  const backReachable = await evaluate(
    "Boolean(document.querySelector('.q__back'))");
  check("a keyboard user can go back", backReachable === true);

  /* ---- 15. CHANNEL TRACKING: utm_source and referrer ---- */
  await page.send("Page.navigate", { url: URL_UNDER_TEST + "?utm_source=facebook" });
  await sleep(2600);
  const tagged = requests().filter((u) => u.includes("landed.txt?s="));
  check("utm_source is captured on the landing beacon",
    tagged.some((u) => u.includes("s=facebook")),
    tagged.slice(-1)[0] || "no tagged beacon");

  const taggedStatus = page.events
    .filter((e) => e.method === "Network.responseReceived" &&
                   e.params.response.url.includes("landed.txt?s="))
    .map((e) => e.params.response.status);
  check("tagged beacon still returns 200",
    taggedStatus.length > 0 && taggedStatus.every((s) => s === 200),
    taggedStatus.join(","));

  const noPersonal = await evaluate(`
    (() => {
      const u = new URL(performance.getEntriesByType("resource")
        .map(r => r.name).filter(n => n.includes("/t/"))[0] || "https://x/");
      return u.search.replace("?s=", "");
    })()`);
  check("channel token carries no personal data",
    /^[a-z0-9-]{0,24}$/.test(noPersonal), noPersonal || "(empty)");

  /* ---- 16. PLAN YOUR VISIT ----
     Two legitimate states, and the suite must cover whichever is
     live rather than assuming one. Collection is currently OFF, so
     the paused branch is the one that runs; the collecting branch
     is kept intact and runs the moment the flag flips. Deleting it
     while it is unused is how a test suite quietly stops covering
     the thing it was written for. */
  await page.send("Page.navigate", { url: URL_UNDER_TEST });
  await sleep(3000);
  for (const pick of [2, 0, 1, 1, 0, 2]) {
    await evaluate(`document.querySelectorAll('.opt')[${pick}].click()`);
    await sleep(240);
  }

  const collecting = await evaluate(
    "Boolean(document.getElementById('plan-form'))");

  /* Snapshot the console BEFORE the deliberate refusal probes below.
     Those probes POST on purpose and are answered 503 on purpose,
     which the browser logs as a failed resource. Judging the page by
     errors this harness caused would be measuring the harness. */
  const consoleBeforeProbes = consoleProblems().length;

  if (!collecting) {
    /* ---- PAUSED: nothing may be collected, anywhere ---- */
    const paused = (await evaluate(
      "document.getElementById('plan-visit')?.innerText || ''"))
      .replace(/\s+/g, " ").toLowerCase();

    check("plan-visit section still explains itself while paused",
      paused.includes("interested in touring westminster place?"), paused.slice(0, 50));
    check("paused notice says collection is not open",
      paused.includes("it is not open yet"), paused.slice(0, 60));
    check("paused notice says the server refuses submissions",
      paused.includes("the server refuses it"));
    check("paused notice does not tease a launch",
      !paused.includes("coming soon") && !paused.includes("check back"));
    check("paused notice reassures about the assessment",
      paused.includes("never left this device"));
    check("paused notice points at the phone line, not their form",
      paused.includes("call the number above") &&
      !paused.includes("own form"));

    const anyField = await evaluate(
      "document.querySelectorAll('input,textarea,select,form').length");
    check("no field of any kind exists on the page", anyField === 0,
      "found " + anyField);

    /* The endpoint must refuse independently of the missing form. */
    const refusal = await evaluate(`
      fetch("/api/plan-visit", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          firstName: "Harness", lastName: "Paused",
          email: "harness.paused@example.com",
          consent: true
        })
      }).then(r => r.status + " " + JSON.stringify(r.ok))`);
    check("the live endpoint refuses a crafted submission",
      refusal.startsWith("503"), refusal);

    const body = await evaluate(`
      fetch("/api/plan-visit", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ firstName: "A", lastName: "B", consent: true })
      }).then(r => r.json()).then(j => j.reason + "|" + j.error)`);
    check("the refusal names the reason and says nothing was stored",
      body.startsWith("collection_disabled") && body.includes("Nothing was stored"),
      body.slice(0, 70));
  } else {
    /* ---- 16. PLAN YOUR VISIT: the real form, really submitted ----
       The whole conversion strategy rests on this producing a
       server-side record. So it is clicked, not simulated: the
       fields are typed into, the button is pressed, and the live
       endpoint's answer is read back off the wire. */
    await page.send("Page.navigate", { url: URL_UNDER_TEST });
    await sleep(3000);
    for (const pick of [2, 0, 1, 1, 0, 2]) {
      await evaluate(`document.querySelectorAll('.opt')[${pick}].click()`);
      await sleep(240);
    }

    const planHeading = await evaluate(
      "document.querySelector('#plan-visit .res__h')?.textContent.trim() || ''");
    check("plan-visit section follows the result",
      planHeading === "Interested in touring Westminster Place?", planHeading);

    const planViewBeacon = requests().some((u) => u.includes("plan-visit-form-view.txt"));
    check("plan-visit form view beacon fired", planViewBeacon);

    /* Exactly the permitted fields, and nothing medical. */
    const fields = await evaluate(`
      JSON.stringify([...document.querySelectorAll('#plan-form input')]
        .map(i => i.name + ':' + i.type))`);
    const fieldList = JSON.parse(fields || "[]");
    check("form collects only the five permitted fields",
      fieldList.length === 5 &&
      fieldList.includes("firstName:text") &&
      fieldList.includes("lastName:text") &&
      fieldList.includes("email:email") &&
      fieldList.includes("phone:tel") &&
      fieldList.includes("consent:checkbox") &&
      !fieldList.some((f) => f.endsWith(":date")),
      fieldList.join(" "));

    const HEALTHY = ["diagnosis", "medication", "memory", "adl", "insurance",
      "dob", "birth", "condition", "quiz", "answer", "level"];
    check("no field asks for health or assessment data",
      !fieldList.some((f) => HEALTHY.some((h) => f.toLowerCase().includes(h))),
      fieldList.join(" "));

    /* Consent must be visible, unticked by default, and required. */
    const consentState = await evaluate(`
      (() => {
        const box = document.getElementById('plan-consent');
        const copy = document.querySelector('.plan__consent-copy');
        const label = document.querySelector('.plan__check span');
        const cs = getComputedStyle(copy);
        return JSON.stringify({
          checked: box.checked,
          copySize: parseFloat(cs.fontSize),
          copy: copy.textContent.replace(/\\s+/g, ' ').trim(),
          label: label.textContent.replace(/\\s+/g, ' ').trim()
        });
      })()`);
    const cons = JSON.parse(consentState);
    check("consent box is unticked by default", cons.checked === false);
    check("consent copy refuses the tour promise",
      cons.copy.includes("does not schedule a tour and does not guarantee one"));
    check("consent copy says Admissions decide",
      cons.copy.includes("Westminster Place Admissions decide whether and when a tour happens"));
    check("consent label names the three shared fields",
      cons.label.includes("my name, phone number and email address"));
    check("consent label names the recipient and the purpose",
      cons.label.includes("shared with Westminster Place Admissions so they can contact me about a tour"));
    check("consent label refuses the tour promise",
      cons.label.includes("does not schedule or guarantee a tour"));
    check("consent copy is readable, not fine print",
      cons.copySize >= 15.5, cons.copySize + "px");

    /* Inputs must be reachable and large enough for an older hand. */
    const inputBoxes = await evaluate(`
      Math.min(...[...document.querySelectorAll('#plan-form input[type=text],#plan-form input[type=email],#plan-form input[type=tel]')]
        .map(i => i.getBoundingClientRect().height))`);
    check("input tap targets are at least 44px", inputBoxes >= 44, inputBoxes + "px");

    /* Submitting empty must fail locally and send nothing. */
    const postsBefore = requests().filter((u) => u.includes("/api/plan-visit")).length;
    await evaluate("document.querySelector('.plan__submit').click()");
    await sleep(500);
    const emptyStatus = await evaluate(
      "document.getElementById('plan-status')?.textContent || ''");
    check("empty submit is refused before any request",
      emptyStatus.length > 10 &&
      requests().filter((u) => u.includes("/api/plan-visit")).length === postsBefore,
      emptyStatus.slice(0, 44));

    /* Now a genuine submission. */
    await evaluate(`
      (() => {
        const f = document.getElementById('plan-form');
        const set = (n, v) => {
          f.elements[n].value = v;
          f.elements[n].dispatchEvent(new Event('input', { bubbles: true }));
        };
        set('firstName', 'Browser');
        set('lastName', 'Harness ${WIDTH}');
        set('email', 'browser.harness@example.com');
        set('phone', '847-555-0101');
        f.elements.consent.click();
      })()`);

    await evaluate("document.querySelector('.plan__submit').click()");
    await sleep(5000);

    const posted = page.events
      .filter((e) => e.method === "Network.requestWillBeSent" &&
                     e.params.request.url.includes("/api/plan-visit"))
      .map((e) => e.params.request);
    check("submitting really posts to the server endpoint", posted.length >= 1,
      posted.length + " request(s)");
    check("the post is a POST, not a navigation",
      posted.every((r) => r.method === "POST"));

    const bodies = posted.map((r) => String(r.postData || ""));
    check("request body carries no assessment or health data",
      bodies.every((b) => !/(answers|carelevel|care_level|diagnosis|medication|memory|adls|signals|reasons)/i.test(b)),
      bodies[0] ? bodies[0].slice(0, 70) : "(no body)");
    check("request body carries the five fields",
      bodies.some((b) => b.includes("firstName") && b.includes("lastName") &&
                         b.includes("phone") && b.includes("consent")));
    check("request body no longer carries a planned-visit date",
      bodies.every((b) => !b.includes("plannedVisitDate")));

    const apiStatus = page.events
      .filter((e) => e.method === "Network.responseReceived" &&
                     e.params.response.url.includes("/api/plan-visit"))
      .map((e) => e.params.response.status);
    check("the server accepted the submission",
      apiStatus.includes(200), apiStatus.join(",") || "no response seen");

    /* The visitor must be shown a real server reference, not a vibe. */
    const confirmed = await evaluate(`
      (() => {
        const flat = (el) => el ? el.textContent.replace(/\\s+/g, ' ').trim() : '';
        const acts = [...document.querySelectorAll('.plan__actions a')];
        return JSON.stringify({
          heading: flat(document.querySelector('.plan__done-h')),
          body: flat(document.querySelector('.plan__done')).toLowerCase(),
          ref: flat(document.querySelector('.plan__ref code')),
          fine: flat(document.querySelector('.plan__done-fine')),
          actions: acts.map(a => flat(a).toLowerCase()).join(' | '),
          actionHrefs: acts.map(a => a.getAttribute('href'))
        });
      })()`);
    const conf = JSON.parse(confirmed);
    check("the visitor is told their interest was recorded",
      conf.heading === "Your interest has been recorded.", conf.heading);
    check("a server-generated reference is shown",
      /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/.test(conf.ref),
      conf.ref);
    check("confirmation states it does not schedule an appointment",
      conf.body.includes("does not schedule an appointment with westminster place"),
      conf.body.slice(0, 58));
    check("confirmation states no tour is guaranteed",
      conf.body.includes("does not guarantee a tour"), conf.body.slice(0, 58));
    check("confirmation says the next step belongs to Admissions",
      conf.body.includes("up to westminster place admissions") &&
      conf.body.includes("they will be the ones to contact you"),
      conf.body.slice(0, 80));
    check("confirmation offers website, phone and directions",
      conf.actions.includes("visit westminster place") &&
      conf.actions.includes("call (847) 570-3422") &&
      conf.actions.includes("get directions"),
      conf.actions);
    check("the three Westminster actions still work after saving",
      conf.actionHrefs.includes("https://www.presbyterianliving.org/our-locations/westminster-place/") &&
      conf.actionHrefs.includes("tel:+18475703422") &&
      conf.actionHrefs.some((h) => h.includes("3200+Grant+Street")),
      conf.actionHrefs.length + " links");
    check("confirmation tells them to walk in normally",
      conf.fine.includes("nothing to show anyone"));

    const savedBeacon = requests().some((u) => u.includes("plan-visit-saved.txt"));
    check("plan-visit saved beacon fired", savedBeacon);

  }

  /* ---- 13. console must be clean ---- */
  const problems = consoleProblems();
  /* The browser logs a failed resource without naming the path, so
     the entry cannot be matched on "plan-visit". A 503 is excluded
     outright instead: the only 503 reachable on this site is the
     collection refusal, and the probes above are what trigger it.
     consoleBeforeProbes is the real guard — it is the page's own
     console, recorded before this harness touched the endpoint. */
  const pageProblems = problems.filter((p) => !/status of 503/.test(p));
  check("no console errors or warnings from the page itself",
    consoleBeforeProbes === 0 && pageProblems.length === 0,
    "before probes: " + consoleBeforeProbes + " | " +
    (pageProblems.slice(0, 2).join(" | ") || "clean"));
  check("the only console errors are the harness's own refusal probes",
    problems.length === 0 ||
    problems.every((p) => /status of 503/.test(p)),
    problems.length + " entries");

  await browser.send("Target.closeTarget", { targetId });
  browserWs.close();
  edge.kill();

  const passed = results.filter((r) => r.ok).length;
  console.log(`\n${passed}/${results.length} browser checks passed`);
  process.exit(passed === results.length ? 0 : 1);
}

main().catch((err) => {
  console.error("HARNESS ERROR:", err.message);
  edge.kill();
  process.exit(2);
});
