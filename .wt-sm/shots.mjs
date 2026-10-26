/* Targeted screenshots for design review.
   node --experimental-websocket shots.mjs <url> */
import { spawn } from "node:child_process";
import { writeFileSync, mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const URL_UNDER_TEST = process.argv[2] || "https://evanston-senior-care-guide.netlify.app/";
const PORT = 9334;
const EDGE = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const profile = mkdtempSync(join(tmpdir(), "edge-shot-"));
const edge = spawn(EDGE, ["--headless=new", `--remote-debugging-port=${PORT}`,
  `--user-data-dir=${profile}`, "--disable-gpu", "--no-first-run",
  "--hide-scrollbars"], { stdio: "ignore" });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

let id = 0;
function client(ws) {
  const pending = new Map();
  ws.addEventListener("message", (ev) => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) {
      const { resolve, reject } = pending.get(m.id); pending.delete(m.id);
      m.error ? reject(new Error(JSON.stringify(m.error))) : resolve(m.result);
    }
  });
  return (method, params = {}, sessionId) => new Promise((resolve, reject) => {
    const myId = ++id; pending.set(myId, { resolve, reject });
    ws.send(JSON.stringify({ id: myId, method, params, sessionId }));
    setTimeout(() => { if (pending.has(myId)) { pending.delete(myId); reject(new Error(method)); } }, 25000);
  });
}

const main = async () => {
  let wsUrl;
  for (let i = 0; i < 40; i++) {
    try {
      const r = await fetch(`http://127.0.0.1:${PORT}/json/version`);
      wsUrl = (await r.json()).webSocketDebuggerUrl; if (wsUrl) break;
    } catch {}
    await sleep(250);
  }
  const ws = await new Promise((res, rej) => {
    const w = new WebSocket(wsUrl);
    w.addEventListener("open", () => res(w));
    w.addEventListener("error", rej);
  });
  const send = client(ws);
  const { targetId } = await send("Target.createTarget", { url: "about:blank" });
  const { sessionId } = await send("Target.attachToTarget", { targetId, flatten: true });
  const p = (m, pr = {}) => send(m, pr, sessionId);
  await p("Page.enable"); await p("Runtime.enable");

  const shoot = async (name, w, h, mobile, setup) => {
    await p("Emulation.setDeviceMetricsOverride",
      { width: w, height: h, deviceScaleFactor: mobile ? 2 : 1, mobile });
    await p("Page.navigate", { url: URL_UNDER_TEST });
    await sleep(3200);
    if (setup) {
      await p("Runtime.evaluate", { expression: setup, awaitPromise: true });
      await sleep(900);
    }
    const shot = await p("Page.captureScreenshot", { format: "png" });
    writeFileSync(name, Buffer.from(shot.data, "base64"));
    console.log("wrote", name);
  };

  await shoot("v-hero-desktop.png", 1440, 900, false);
  await shoot("v-hero-mobile.png", 390, 844, true);
  await shoot("v-quiz-desktop.png", 1440, 900, false,
    "document.getElementById('assessment').scrollIntoView()");
  await shoot("v-result-mobile.png", 390, 844, true, `
    (async () => {
      document.getElementById('assessment').scrollIntoView();
      const picks = [2,3,1,3,0,3];
      for (const i of picks) {
        document.querySelectorAll('.opt')[i].click();
        await new Promise(r => setTimeout(r, 180));
      }
      document.getElementById('assessment').scrollIntoView();
    })()`);
  await shoot("v-westminster-mobile.png", 390, 844, true, `
    (async () => {
      document.getElementById('assessment').scrollIntoView();
      const picks = [2,0,1,1,0,2];
      for (const i of picks) {
        document.querySelectorAll('.opt')[i].click();
        await new Promise(r => setTimeout(r, 170));
      }
      document.querySelector('.wp').scrollIntoView({block:'center'});
    })()`);

  /* The plan-visit form and its saved state are shot by
     shoot-plan.mjs instead. That script waits for the questions to
     exist before clicking and clips to the element's own box — this
     one fires on a fixed timer and silently caught the hero instead
     of the form when the click landed too early. */

  ws.close(); edge.kill(); process.exit(0);
};
main().catch((e) => { console.error("ERR", e.message); edge.kill(); process.exit(1); });
