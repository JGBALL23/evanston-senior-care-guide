/* Verify, on the LIVE site, that every care level routes to the
   phone line Westminster publishes for that team — and that the
   inquiry CTA is present and honest on all five.

   node --experimental-websocket probe-routing.mjs */
const URL_UNDER_TEST = process.argv[2] || "https://evanston-senior-care-guide.netlify.app/";
const PORT = 9367;
const EDGE = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
import { spawn } from "node:child_process";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

/* level → the number Westminster publishes for that team */
const EXPECT = {
  independent: ["tel:+18475703310", "Independent Living Sales"],
  assisted:    ["tel:+18478661615", "Assisted Living & Memory Care Sales"],
  memory:      ["tel:+18478661615", "Assisted Living & Memory Care Sales"],
  skilled:     ["tel:+18474927780", "Skilled Nursing Admissions"],
  rehab:       ["tel:+18474927780", "Skilled Nursing Admissions"]
};
const SCENARIOS = [
  ["independent", [0, 1, 0, 0, 0, 1]],
  ["assisted",    [2, 0, 1, 1, 0, 2]],
  ["memory",      [2, 3, 1, 3, 0, 3]],
  ["skilled",     [3, 0, 2, 3, 0, 3]],
  ["rehab",       [2, 0, 1, 1, 1, 2]]
];

const prof = mkdtempSync(join(tmpdir(), "route-"));
const edge = spawn(EDGE, ["--headless=new", `--remote-debugging-port=${PORT}`,
  `--user-data-dir=${prof}`, "--disable-gpu", "--no-first-run",
  "--hide-scrollbars"], { stdio: "ignore" });
const sleep = (m) => new Promise((r) => setTimeout(r, m));
let id = 0, bad = 0;

async function main() {
  let wsUrl;
  for (let i = 0; i < 40; i++) {
    try {
      const r = await fetch(`http://127.0.0.1:${PORT}/json/version`);
      wsUrl = (await r.json()).webSocketDebuggerUrl;
      if (wsUrl) break;
    } catch { /* not up */ }
    await sleep(250);
  }
  const ws = await new Promise((res, rej) => {
    const w = new WebSocket(wsUrl);
    w.addEventListener("open", () => res(w));
    w.addEventListener("error", rej);
  });
  const pend = new Map();
  ws.addEventListener("message", (e) => {
    const m = JSON.parse(e.data);
    if (m.id && pend.has(m.id)) { const { resolve } = pend.get(m.id); pend.delete(m.id); resolve(m.result); }
  });
  const send = (method, params = {}, sessionId) => new Promise((resolve) => {
    const i = ++id; pend.set(i, { resolve });
    ws.send(JSON.stringify({ id: i, method, params, sessionId }));
  });
  const { targetId } = await send("Target.createTarget", { url: "about:blank" });
  const { sessionId } = await send("Target.attachToTarget", { targetId, flatten: true });
  const p = (m, pr = {}) => send(m, pr, sessionId);
  await p("Page.enable"); await p("Runtime.enable");
  const ev = async (e) => {
    const r = await p("Runtime.evaluate", { expression: e, returnByValue: true, awaitPromise: true });
    if (r.exceptionDetails) throw new Error(r.exceptionDetails.text);
    return r.result.value;
  };
  await p("Emulation.setDeviceMetricsOverride",
    { width: 390, height: 900, deviceScaleFactor: 2, mobile: true });

  for (const [label, picks] of SCENARIOS) {
    await p("Page.navigate", { url: URL_UNDER_TEST });
    await sleep(3200);
    for (const i of picks) {
      await ev(`document.querySelectorAll('.opt')[${i}].click()`);
      await sleep(200);
    }
    const out = JSON.parse(await ev(`
      (() => {
        const tel = document.querySelector('.wp__actions a[href^="tel:"]');
        const cta = document.querySelector('.wp__actions a[href*="/contact/"]');
        const t = (s) => { const e = document.querySelector(s);
          return e ? e.innerText.replace(/\\s+/g, ' ').trim() : ''; };
        return JSON.stringify({
          name: t('.res__name'),
          tel: tel ? tel.getAttribute('href') : '',
          telText: tel ? tel.innerText.trim() : '',
          ctaHref: cta ? cta.getAttribute('href') : '',
          ctaText: cta ? cta.innerText.trim() : '',
          route: t('.wp__route'),
          fine: t('.wp__fine'),
          hear: t('.wp__hear')
        });
      })()`));

    const [wantTel, wantTeam] = EXPECT[label];
    console.log("\n--- " + label + " (" + out.name + ") ---");
    console.log("  phone : " + out.tel + "  " + out.telText);
    console.log("  team  : " + (out.route.match(/Place's ([^l]+?) line/) || ["", "?"])[1].trim());
    console.log("  CTA   : " + out.ctaText);

    if (out.tel !== wantTel) { console.log("  !! WRONG NUMBER, expected " + wantTel); bad++; }
    if (!out.route.includes(wantTeam)) { console.log("  !! TEAM NOT NAMED: " + wantTeam); bad++; }
    if (!out.ctaHref.includes("presbyterianliving.org/our-locations/westminster-place/contact/")) {
      console.log("  !! CTA does not point at their official form"); bad++;
    }
    if (/\?(src|utm)/.test(out.ctaHref)) { console.log("  !! source param appended — it cannot be captured"); bad++; }
    if (!/does not guarantee a tour/i.test(out.fine)) { console.log("  !! missing no-guarantee statement"); bad++; }
    if (!/belongs to Westminster Place/i.test(out.fine)) { console.log("  !! missing form-ownership statement"); bad++; }
    if (!/Community website/i.test(out.hear)) { console.log("  !! missing how-did-you-hear note"); bad++; }
  }

  console.log("\n" + (bad === 0 ? "LIVE ROUTING AUDIT: clean" : "LIVE ROUTING AUDIT: " + bad + " problems"));
  edge.kill();
  process.exit(bad === 0 ? 0 : 1);
}
main().catch((e) => { console.error("ERR", e.message); edge.kill(); process.exit(2); });
