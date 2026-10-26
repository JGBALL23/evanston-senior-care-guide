/* Read the cost block every care level renders on the LIVE site.
   A figure can pass a unit test and still reach a family wrong. */
const URL_UNDER_TEST = process.argv[2] || "https://evanston-senior-care-guide.netlify.app/";
const PORT = 9357;
const EDGE = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
import { spawn } from "node:child_process";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const SCENARIOS = [
  ["independent", [0, 1, 0, 0, 0, 1]],
  ["assisted",    [2, 0, 1, 1, 0, 2]],
  ["memory",      [2, 3, 1, 3, 0, 3]],
  ["skilled",     [3, 0, 2, 3, 0, 3]],
  ["rehab",       [2, 0, 1, 1, 1, 2]]
];

const prof = mkdtempSync(join(tmpdir(), "cost-"));
const edge = spawn(EDGE, ["--headless=new", `--remote-debugging-port=${PORT}`,
  `--user-data-dir=${prof}`, "--disable-gpu", "--no-first-run",
  "--hide-scrollbars"], { stdio: "ignore" });
const sleep = (m) => new Promise((r) => setTimeout(r, m));
let id = 0;

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

  let bad = 0;
  for (const [label, picks] of SCENARIOS) {
    await p("Page.navigate", { url: URL_UNDER_TEST });
    await sleep(3200);
    for (const i of picks) {
      await ev(`document.querySelectorAll('.opt')[${i}].click()`);
      await sleep(200);
    }
    const out = await ev(`
      (() => {
        const c = document.querySelector('.res__cost');
        if (!c) return JSON.stringify({ missing: true });
        const link = c.querySelector('a');
        return JSON.stringify({
          text: c.innerText.replace(/\\s+/g, ' ').trim(),
          href: link ? link.getAttribute('href') : null
        });
      })()`);
    const o = JSON.parse(out);
    console.log("\n--- " + label + " ---");
    console.log("  " + (o.text || "MISSING"));
    console.log("  source link: " + (o.href || "(none)"));

    const t = (o.text || "");
    if (label === "memory" && /\$\d/.test(t)) { console.log("  !! FIGURE PRESENT"); bad++; }
    if (label === "independent" && /\$\d/.test(t)) { console.log("  !! FIGURE PRESENT"); bad++; }
    if (label === "rehab" && /\$\d,\d{3}/.test(t)) { console.log("  !! NURSING FIGURE LEAKED"); bad++; }
    if ((label === "assisted" || label === "skilled")) {
      if (!o.href) { console.log("  !! SOURCED FIGURE WITH NO LINK"); bad++; }
      if (!/CareScout 2025 Cost of Care Survey, published 2026/.test(t)) {
        console.log("  !! SURVEY NOT NAMED"); bad++;
      }
      if (!/do not represent Westminster Place/.test(t)) {
        console.log("  !! WESTMINSTER DISCLAIMER MISSING"); bad++;
      }
    }
  }
  console.log("\n" + (bad === 0 ? "LIVE COST AUDIT: clean" : "LIVE COST AUDIT: " + bad + " problems"));
  edge.kill();
  process.exit(bad === 0 ? 0 : 1);
}
main().catch((e) => { console.error("ERR", e.message); edge.kill(); process.exit(2); });
