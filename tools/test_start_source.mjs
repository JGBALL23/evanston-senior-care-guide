/* Offline regression test: the assessment-start beacon carries the channel.

   Run:  node tools/test_start_source.mjs     (serves _dist on 127.0.0.1)

   Uses the preinstalled Playwright Chromium. Touches no live site, submits
   no form and sends nothing anywhere: every request goes to the local
   server. It proves only what the page REQUESTS. A start is a hero-CTA
   click or a first answer, so it counts intent, not humans and not
   completed assessments; bots and test runs cannot be told apart here.

   Covers: tagged (utm_source and ref) and direct arrivals, sanitisation,
   hero CTA then first answer counted once, repeat clicks counted once, no
   untagged start ever requested, and failed beacon requests never
   blocking the assessment. */
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

/* Assisted living: [adl, memory, medical, alone, hospital, household]. */
const PICKS = [2, 0, 1, 1, 0, 3];

const server = await serveDist();
const BASE = `http://127.0.0.1:${server.address().port}`;
const browser = await chromium.launch();

async function visit(query, { abortBeacons = false, referer } = {}) {
  const ctx = await browser.newContext({ userAgent: HARNESS_UA, viewport: { width: 390, height: 844 } });
  const page = await ctx.newPage();
  const starts = [];
  const errors = [];
  let landed = null;
  page.on("pageerror", (e) => errors.push(String(e)));
  page.on("request", (r) => {
    const u = new URL(r.url());
    if (u.pathname === "/t/assessment-started.txt") starts.push(u.search);
    if (u.pathname === "/t/landed.txt") landed = u.searchParams.get("s");
  });
  if (abortBeacons) await page.route("**/t/**", (route) => route.abort("failed"));
  await page.goto(BASE + "/" + query, { waitUntil: "load", referer });
  return { ctx, page, starts, errors, landedSource: () => landed };
}
async function answerAll(page) {
  await page.click('#quiz .opt[data-aud="parent"]');
  for (const i of PICKS) await page.click(`#quiz .opt[data-i="${i}"]`);
  await page.waitForSelector("#quiz .res__name");
}
const settle = (page) => page.waitForTimeout(300);

/* 1. Arrival tags: first answer only (no hero click). */
const ARRIVALS = [
  ["?utm_source=facebook", "facebook"],
  ["?ref=nextdoor", "nextdoor"],
  ["", "direct"],
  /* Sanitised exactly like the landing beacon: lower-cased, only
     [a-z0-9-], at most 24 characters. */
  ["?utm_source=" + encodeURIComponent("Face Book<script>_Group!!-2026-abcdefghij"), "facebookscriptgroup-2026"]
];
for (const [query, want] of ARRIVALS) {
  const v = await visit(query);
  await answerAll(v.page);
  await settle(v.page);
  check(`first answer tags start: ${query || "(direct)"}`,
    v.starts.length === 1 && v.starts[0] === "?s=" + want, JSON.stringify(v.starts));
  check(`start tag matches landing tag: ${query || "(direct)"}`, v.landedSource() === want, String(v.landedSource()));
  check(`no page errors: ${query || "(direct)"}`, v.errors.length === 0, v.errors.join(" | "));
  await v.ctx.close();
}

/* 2. Referrer-derived channel reaches the start beacon too. */
{
  const v = await visit("", { referer: "https://www.example-referrer.org/some/path?x=1" });
  await answerAll(v.page);
  await settle(v.page);
  check("referrer host becomes the start tag (no path, no query)",
    v.starts.length === 1 && v.starts[0] === "?s=example-referrer", JSON.stringify(v.starts));
  await v.ctx.close();
}

/* 3. Hero CTA, repeat clicks, then the first answer: one start, tagged. */
{
  const v = await visit("?utm_source=facebook");
  const ctas = v.page.locator('[data-beacon="hero-cta"]:visible');
  const n = await ctas.count();
  for (let k = 0; k < 3; k++) for (let j = 0; j < n; j++) await ctas.nth(j).click();
  await settle(v.page);
  check("hero CTA alone fires one tagged start", v.starts.length === 1 && v.starts[0] === "?s=facebook",
    `${n} visible CTA(s), clicked 3x each: ${JSON.stringify(v.starts)}`);
  await answerAll(v.page);
  await settle(v.page);
  check("hero CTA then first answer still one start", v.starts.length === 1, JSON.stringify(v.starts));
  /* Start again and answer once more: still the same page load. */
  const restarted = (await v.page.locator("#restart").count()) === 1;
  if (restarted) {
    await v.page.click("#restart");
    await answerAll(v.page);
    await settle(v.page);
  }
  check("restart and re-answer adds no start", restarted && v.starts.length === 1, JSON.stringify(v.starts));
  check("no untagged start was ever requested", v.starts.every((s) => s.startsWith("?s=")), JSON.stringify(v.starts));
  await v.ctx.close();
}

/* 4. A new page load is a new count (per-page-load deduplication). */
{
  const v = await visit("?utm_source=facebook");
  await answerAll(v.page);
  await v.page.reload({ waitUntil: "load" });
  await answerAll(v.page);
  await settle(v.page);
  check("reload counts a new start (one per page load)", v.starts.length === 2 && v.starts.every((s) => s === "?s=facebook"),
    JSON.stringify(v.starts));
  await v.ctx.close();
}

/* 5. Every beacon request fails: the assessment still works. */
{
  const v = await visit("?utm_source=facebook", { abortBeacons: true });
  await v.page.locator('[data-beacon="hero-cta"]:visible').first().click();
  await answerAll(v.page);
  const name = (await v.page.textContent("#quiz .res__name")) || "";
  check("failed beacons do not block the assessment", /assisted living/i.test(name), name.trim());
  check("failed beacons raise no page errors", v.errors.length === 0, v.errors.join(" | "));
  check("start was attempted once, tagged, despite failure", v.starts.length === 1 && v.starts[0] === "?s=facebook",
    JSON.stringify(v.starts));
  await v.ctx.close();
}

await browser.close();
server.close();
console.log(`\n${pass}/${pass + fail} assessment-start source checks passed`);
process.exit(fail ? 1 : 0);
