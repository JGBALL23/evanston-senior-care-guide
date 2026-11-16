/* Offline regression test: the free tour-checklist click beacon.

   Run:  node tools/test_checklist_click.mjs   (serves _dist on 127.0.0.1)

   Uses the preinstalled Playwright Chromium. Touches no live site, submits
   no form and sends nothing anywhere: every request goes to the local
   server. It proves only what the page REQUESTS. The beacon counts CLICKS
   on the homepage checklist link: not completed downloads, not PDF opens,
   not verified humans, not inquiries or tours. Bots and test runs cannot
   be told apart here.

   Covers: tagged (utm_source, ref, referrer) and direct arrivals,
   sanitisation, repeat clicks counted once per page load, reload counted
   again, no-JS (link still downloads, nothing requested), failed beacon
   requests (download still works, no page errors), and no checklist
   request without a click. */
import { createServer } from "node:http";
import { existsSync, readFileSync, statSync } from "node:fs";
import { join, extname, resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";

const HARNESS_UA = "ESCG-harness/1 (automated test; +https://evanstonseniorcareguide.com/)";
const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const { chromium } = createRequire(import.meta.url)("playwright");

const TYPES = { ".html": "text/html; charset=utf-8", ".css": "text/css", ".js": "text/javascript",
  ".txt": "text/plain", ".png": "image/png", ".ico": "image/x-icon", ".svg": "image/svg+xml" };
function serveDist() {
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
  return new Promise((ok) => server.listen(0, "127.0.0.1", () => ok(server)));
}

let pass = 0, fail = 0;
function check(name, ok, detail = "") {
  ok ? pass++ : fail++;
  console.log(`${ok ? "PASS" : "FAIL"}  ${name.padEnd(64)} ${detail}`);
}

const server = await serveDist();
const BASE = `http://127.0.0.1:${server.address().port}`;
const browser = await chromium.launch();

const TOKEN = "/t/checklist-click.txt";
const LINK = 'a.dl-link[data-beacon="checklist"]';

async function visit(query, { abortBeacons = false, referer, js = true } = {}) {
  const ctx = await browser.newContext({ userAgent: HARNESS_UA, viewport: { width: 390, height: 844 },
    acceptDownloads: true, javaScriptEnabled: js });
  const page = await ctx.newPage();
  const clicks = [];
  const errors = [];
  let landed = null;
  page.on("pageerror", (e) => errors.push(String(e)));
  page.on("request", (r) => {
    const u = new URL(r.url());
    if (u.pathname === TOKEN) clicks.push(u.search);
    if (u.pathname === "/t/landed.txt") landed = u.searchParams.get("s");
  });
  if (abortBeacons) await page.route("**/t/**", (route) => route.abort("failed"));
  await page.goto(BASE + "/" + query, { waitUntil: "load", referer });
  return { ctx, page, clicks, errors, landedSource: () => landed };
}
/* Click the link the way a visitor would and wait for the browser's
   download: proof the link still does its job. */
async function clickChecklist(page) {
  const link = page.locator(LINK);
  await link.evaluate((a) => { const d = a.closest("details"); if (d) d.open = true; });
  await link.scrollIntoViewIfNeeded();
  const [dl] = await Promise.all([page.waitForEvent("download", { timeout: 5000 }), link.click()]);
  const path = await dl.path();
  const head = path ? readFileSync(path).subarray(0, 5).toString("latin1") : "";
  return { name: dl.suggestedFilename(), isPdf: head === "%PDF-" };
}
const settle = (page) => page.waitForTimeout(300);

/* 0. The link exists once, and nothing is requested without a click. */
{
  const v = await visit("?utm_source=facebook");
  check("homepage has exactly one checklist link with the beacon", (await v.page.locator(LINK).count()) === 1);
  await settle(v.page);
  check("no checklist request on page load", v.clicks.length === 0, JSON.stringify(v.clicks));
  await v.ctx.close();
}

/* 1. Arrival tags. */
const ARRIVALS = [
  ["?utm_source=facebook", "facebook", undefined],
  ["?ref=nextdoor", "nextdoor", undefined],
  ["", "direct", undefined],
  ["", "example-referrer", "https://www.example-referrer.org/some/path?x=1"],
  /* Sanitised exactly like the landing beacon. */
  ["?utm_source=" + encodeURIComponent("Face Book<script>_Group!!-2026-abcdefghij"), "facebookscriptgroup-2026", undefined]
];
for (const [query, want, referer] of ARRIVALS) {
  const label = (query || "(direct)") + (referer ? " via referrer" : "");
  const v = await visit(query, { referer });
  const dl = await clickChecklist(v.page);
  await settle(v.page);
  check(`click tags checklist beacon: ${label}`, v.clicks.length === 1 && v.clicks[0] === "?s=" + want, JSON.stringify(v.clicks));
  check(`checklist tag matches landing tag: ${label}`, v.landedSource() === want, String(v.landedSource()));
  check(`PDF still downloads: ${label}`, dl.isPdf && dl.name === "Senior-Living-Tour-Checklist.pdf", dl.name);
  check(`no page errors: ${label}`, v.errors.length === 0, v.errors.join(" | "));
  await v.ctx.close();
}

/* 2. Repeat clicks in one page load count once; a reload counts again. */
{
  const v = await visit("?utm_source=facebook");
  let ok = 0;
  for (let k = 0; k < 3; k++) if ((await clickChecklist(v.page)).isPdf) ok++;
  await settle(v.page);
  check("three clicks, three downloads, one beacon", ok === 3 && v.clicks.length === 1, `${ok} downloads, ${JSON.stringify(v.clicks)}`);
  await v.page.reload({ waitUntil: "load" });
  await clickChecklist(v.page);
  await settle(v.page);
  check("reload counts a new click (one per page load)", v.clicks.length === 2 && v.clicks.every((s) => s === "?s=facebook"),
    JSON.stringify(v.clicks));
  check("no untagged checklist request", v.clicks.every((s) => s.startsWith("?s=")), JSON.stringify(v.clicks));
  await v.ctx.close();
}

/* 3. JavaScript off: the plain link still downloads; nothing is counted. */
{
  const v = await visit("?utm_source=facebook", { js: false });
  const dl = await clickChecklist(v.page);
  await settle(v.page);
  check("no-JS: PDF still downloads", dl.isPdf && dl.name === "Senior-Living-Tour-Checklist.pdf", dl.name);
  check("no-JS: no checklist request", v.clicks.length === 0, JSON.stringify(v.clicks));
  await v.ctx.close();
}

/* 4. Every beacon request fails: the download still works. */
{
  const v = await visit("?utm_source=facebook", { abortBeacons: true });
  const dl = await clickChecklist(v.page);
  await settle(v.page);
  check("failed beacon: PDF still downloads", dl.isPdf && dl.name === "Senior-Living-Tour-Checklist.pdf", dl.name);
  check("failed beacon: attempted once, tagged", v.clicks.length === 1 && v.clicks[0] === "?s=facebook", JSON.stringify(v.clicks));
  check("failed beacon: no page errors", v.errors.length === 0, v.errors.join(" | "));
  await v.ctx.close();
}

await browser.close();
server.close();
console.log(`\n${pass}/${pass + fail} checklist-click checks passed`);
process.exit(fail ? 1 : 0);
