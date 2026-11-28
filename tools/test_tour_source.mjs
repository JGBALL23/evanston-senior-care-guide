/* Offline regression test: the tour-questions beacon carries the channel.

   Run:  node tools/test_tour_source.mjs     (serves _dist on 127.0.0.1)

   Uses the preinstalled Playwright Chromium. Touches no live site, submits
   no form and sends nothing anywhere: every request goes to the local
   server. It proves only what the page REQUESTS. viewed-tour-questions
   counts the tour section scrolling into view (or a data-beacon="tour"
   click): section exposure or navigation intent, not proof of reading, a
   person, an inquiry or a tour. Bots and test runs cannot be told apart.

   Covers: tagged (utm_source, ref, referrer) and direct arrivals,
   sanitisation, observer-first and click-first ordering counted once,
   repeat visibility and clicks counted once, reload counted again, no
   untagged tour request ever, and failed beacon requests never breaking
   the #tour jump or its content. */
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

async function visit(query, { abortBeacons = false, referer } = {}) {
  const ctx = await browser.newContext({ userAgent: HARNESS_UA, viewport: { width: 390, height: 844 } });
  const page = await ctx.newPage();
  const tours = [];
  const errors = [];
  let landed = null;
  page.on("pageerror", (e) => errors.push(String(e)));
  page.on("request", (r) => {
    const u = new URL(r.url());
    if (u.pathname === "/t/viewed-tour-questions.txt") tours.push(u.search);
    if (u.pathname === "/t/landed.txt") landed = u.searchParams.get("s");
  });
  if (abortBeacons) await page.route("**/t/**", (route) => route.abort("failed"));
  await page.goto(BASE + "/" + query, { waitUntil: "load", referer });
  return { ctx, page, tours, errors, landedSource: () => landed };
}
const settle = (page) => page.waitForTimeout(400);
const scrollToTour = async (page) => {
  await page.evaluate(() => document.getElementById("tour").scrollIntoView({ behavior: "instant" }));
  await settle(page);
};
const scrollTop = async (page) => {
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: "instant" }));
  await settle(page);
};
/* No shipped markup carries data-beacon="tour" today, so the click
   handler is exercised with a fixed test-only button that does not
   scroll, keeping click-first ordering honest. */
const addTourButton = (page) => page.evaluate(() => {
  const b = document.createElement("button");
  b.type = "button"; b.id = "test-tour-btn"; b.dataset.beacon = "tour"; b.textContent = "t";
  b.style.cssText = "position:fixed;top:0;left:0;z-index:99999";
  document.body.appendChild(b);
});

/* 0. Nothing is requested before the section is seen. */
{
  const v = await visit("?utm_source=facebook");
  await settle(v.page);
  check("no tour beacon on load (section off screen)", v.tours.length === 0, JSON.stringify(v.tours));
  await v.ctx.close();
}

/* 1. Arrival tags via the observer path. */
const ARRIVALS = [
  ["?utm_source=facebook", "facebook"],
  ["?ref=nextdoor", "nextdoor"],
  ["", "direct"],
  ["?utm_source=" + encodeURIComponent("Face Book<script>_Group!!-2026-abcdefghij"), "facebookscriptgroup-2026"]
];
for (const [query, want] of ARRIVALS) {
  const v = await visit(query);
  await scrollToTour(v.page);
  check(`section view tags tour: ${query || "(direct)"}`,
    v.tours.length === 1 && v.tours[0] === "?s=" + want, JSON.stringify(v.tours));
  check(`tour tag matches landing tag: ${query || "(direct)"}`, v.landedSource() === want, String(v.landedSource()));
  check(`no page errors: ${query || "(direct)"}`, v.errors.length === 0, v.errors.join(" | "));
  await v.ctx.close();
}

/* 2. Referrer-derived channel. */
{
  const v = await visit("", { referer: "https://www.example-referrer.org/some/path?x=1" });
  await scrollToTour(v.page);
  check("referrer host becomes the tour tag (no path, no query)",
    v.tours.length === 1 && v.tours[0] === "?s=example-referrer", JSON.stringify(v.tours));
  await v.ctx.close();
}

/* 3. Observer first, then repeat visibility and clicks: one request. */
{
  const v = await visit("?utm_source=facebook");
  await scrollToTour(v.page);
  await scrollTop(v.page);
  await scrollToTour(v.page);
  await addTourButton(v.page);
  for (let k = 0; k < 3; k++) await v.page.click("#test-tour-btn");
  await settle(v.page);
  check("observer first, then re-views and 3 clicks: one tagged",
    v.tours.length === 1 && v.tours[0] === "?s=facebook", JSON.stringify(v.tours));
  await v.ctx.close();
}

/* 4. Click first, then the section comes into view: one request. */
{
  const v = await visit("?ref=nextdoor");
  await addTourButton(v.page);
  await v.page.click("#test-tour-btn");
  await settle(v.page);
  check("click first fires one tagged tour", v.tours.length === 1 && v.tours[0] === "?s=nextdoor", JSON.stringify(v.tours));
  await v.page.click("#test-tour-btn");
  await scrollToTour(v.page);
  check("click first, then click again and view: still one", v.tours.length === 1, JSON.stringify(v.tours));
  await v.ctx.close();
}

/* 5. The shipped nav link (#tour; collapsed at phone width, so clicked
      in the page) counts once and stays tagged. */
{
  const v = await visit("?utm_source=facebook");
  const jump = () => v.page.evaluate(() => document.querySelector('a[href="#tour"]').click());
  /* The jump scrolls smoothly; give it time to arrive. */
  await jump();
  await v.page.waitForTimeout(2000);
  await scrollTop(v.page);
  await jump();
  await v.page.waitForTimeout(2000);
  check("nav jump to #tour twice: one tagged request",
    v.tours.length === 1 && v.tours[0] === "?s=facebook", JSON.stringify(v.tours));
  check("nav jump lands on #tour", await v.page.evaluate(() => location.hash) === "#tour");
  check("no untagged tour request was ever made", v.tours.every((s) => s.startsWith("?s=")), JSON.stringify(v.tours));
  await v.ctx.close();
}

/* 6. Reload is a new page load and a new count. */
{
  const v = await visit("?utm_source=facebook");
  await scrollToTour(v.page);
  await v.page.reload({ waitUntil: "load" });
  await scrollToTour(v.page);
  check("reload counts again (one per page load)",
    v.tours.length === 2 && v.tours.every((s) => s === "?s=facebook"), JSON.stringify(v.tours));
  await v.ctx.close();
}

/* 7. Every beacon request fails: the jump and the content still work. */
{
  const v = await visit("?utm_source=facebook", { abortBeacons: true });
  await v.page.goto(BASE + "/?utm_source=facebook#tour", { waitUntil: "load" });
  await settle(v.page);
  await addTourButton(v.page);
  await v.page.click("#test-tour-btn");
  await settle(v.page);
  const state = await v.page.evaluate(() => {
    const t = document.getElementById("tour");
    const r = t.getBoundingClientRect();
    const rows = [...t.querySelectorAll("details[data-open-on-jump]")];
    return { hash: location.hash, onScreen: r.top < innerHeight && r.bottom > 0,
      opened: rows.length > 0 && rows.every((d) => d.open),
      h2: (t.querySelector("h2") || {}).textContent || "" };
  });
  check("failed beacons: #tour jump lands and shows content",
    state.hash === "#tour" && state.onScreen && state.opened && /questions/i.test(state.h2), JSON.stringify(state));
  check("failed beacons: no page errors", v.errors.length === 0, v.errors.join(" | "));
  await v.ctx.close();
}

/* 8. The tour-request click keeps the arrival tag. "Ask about a tour here"
      is /?tour=form#plan-visit, a full reload; the second load must still
      count under the arrival channel, not "direct". The exact P-1120-01
      landing URL is used. Nothing is submitted. */
async function clickTourAsk(query, opts) {
  const v = await visit(query, opts);
  const landings = [];
  v.page.on("request", (r) => {
    const u = new URL(r.url());
    if (u.pathname === "/t/landed.txt") landings.push(u.searchParams.get("s"));
  });
  await settle(v.page);
  await v.page.click("#tour .tour-ask a");
  await v.page.waitForLoadState("load");
  await settle(v.page);
  const url = new URL(v.page.url());
  return { v, url, landings };
}
{
  const { v, url, landings } = await clickTourAsk("?ref=fb-wnk-1120#tour");
  check("tour ask from tagged landing keeps ref",
    url.searchParams.get("ref") === "fb-wnk-1120" && url.searchParams.get("tour") === "form" && url.hash === "#plan-visit", url.href);
  check("tour form load counts under the arrival tag", landings.join() === "fb-wnk-1120", JSON.stringify(landings));
  check("tour form renders after the tagged click",
    await v.page.evaluate(() => !!document.getElementById("plan-visit")));
  check("tagged tour click: no page errors", v.errors.length === 0, v.errors.join(" | "));
  await v.ctx.close();
}
{
  const { v, url } = await clickTourAsk("#tour");
  check("direct arrival: tour ask link unchanged (no ref added)",
    !url.searchParams.has("ref") && url.search === "?tour=form", url.href);
  await v.ctx.close();
}
{
  const { v, url } = await clickTourAsk("#tour", { referer: "https://www.example-referrer.org/p" });
  check("referrer-derived channel carried as the same token", url.searchParams.get("ref") === "example-referrer", url.href);
  await v.ctx.close();
}
{
  const { v, url } = await clickTourAsk("?utm_source=" + encodeURIComponent("Face Book<x>") + "#tour");
  check("carried tag is the sanitised token only", url.searchParams.get("ref") === "facebookx", url.href);
  await v.ctx.close();
}

await browser.close();
server.close();
console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
