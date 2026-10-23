/* Capture the plan-visit form and the saved-visit confirmation.
   Clips to the element's own box so the shot is the component, not
   wherever the page happened to be scrolled.

   node --experimental-websocket shoot-plan.mjs [url] */
const URL_UNDER_TEST = process.argv[2] || "https://evanston-senior-care-guide.netlify.app/";
const PORT = 9361;
const EDGE = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";

import { spawn } from "node:child_process";
import { writeFileSync, mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const profile = mkdtempSync(join(tmpdir(), "edge-plan-"));
const edge = spawn(EDGE, ["--headless=new", `--remote-debugging-port=${PORT}`,
  `--user-data-dir=${profile}`, "--disable-gpu", "--no-first-run",
  "--hide-scrollbars"], { stdio: "ignore" });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
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
  ws.addEventListener("message", (ev) => {
    const m = JSON.parse(ev.data);
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

  const evaluate = async (expression) => {
    const r = await p("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true });
    if (r.exceptionDetails) throw new Error(r.exceptionDetails.text + " :: " +
      (r.exceptionDetails.exception && r.exceptionDetails.exception.description || ""));
    return r.result.value;
  };

  /* Wait for app.js to have actually rendered the first question
     before clicking. The earlier shot missed because it clicked too
     soon, the setup threw, and the page simply stayed at the top. */
  const waitFor = async (selector, tries = 40) => {
    for (let i = 0; i < tries; i++) {
      const n = await evaluate(`document.querySelectorAll(${JSON.stringify(selector)}).length`);
      if (n > 0) return true;
      await sleep(300);
    }
    throw new Error("never appeared: " + selector);
  };

  const shoot = async (name, width, height, mobile, after) => {
    await p("Emulation.setDeviceMetricsOverride",
      { width, height, deviceScaleFactor: mobile ? 2 : 1, mobile });
    await p("Page.navigate", { url: URL_UNDER_TEST });
    await sleep(2500);
    await waitFor(".opt");
    for (const i of [2, 0, 1, 1, 0, 2]) {
      await evaluate(`document.querySelectorAll('.opt')[${i}].click()`);
      await sleep(220);
    }
    await waitFor("#plan-form");
    if (after) { await after(evaluate); }

    const box = await evaluate(`
      (() => {
        const el = document.querySelector('.res__cost');
        const r = el.getBoundingClientRect();
        return JSON.stringify({
          x: r.left + window.scrollX, y: r.top + window.scrollY,
          w: r.width, h: r.height
        });
      })()`);
    const b = JSON.parse(box);
    const shot = await p("Page.captureScreenshot", {
      format: "png",
      captureBeyondViewport: true,
      clip: { x: b.x, y: b.y, width: b.w, height: b.h, scale: 1 }
    });
    writeFileSync(name, Buffer.from(shot.data, "base64"));
    console.log("wrote", name, Math.round(b.w) + "x" + Math.round(b.h));
  };

  await shoot("v-cost-mobile.png", 390, 900, true);
  await shoot("v-cost-desktop.png", 1440, 1000, false);

  /* And the confirmation state, which is what a visitor is left
     looking at. Uses an obviously-marked test identity. */
  await shoot("v-plan-saved-mobile.png", 390, 900, true, async (evaluate) => {
    await evaluate(`
      (() => {
        const f = document.getElementById('plan-form');
        const set = (n, v) => { f.elements[n].value = v;
          f.elements[n].dispatchEvent(new Event('input', { bubbles: true })); };
        set('firstName', 'Screenshot');
        set('lastName', 'Harness');
        set('email', 'screenshot.harness@example.com');
        set('phone', '847-555-0188');
        f.elements.consent.click();
      })()`);
    await evaluate("document.querySelector('.plan__submit').click()");
    await sleep(6000);
  });

  ws.close(); edge.kill(); process.exit(0);
}
main().catch((e) => { console.error("ERR", e.message); edge.kill(); process.exit(1); });
