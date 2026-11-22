/* Offline regression test: a tagged arrival on a GUIDE keeps its channel
   when the reader follows the guide's tour (or other homepage) link.

   Run:  node tools/test_guide_ref_carry.mjs     (serves _dist on 127.0.0.1)

   Why: guide pages load nav.js only, so they fire no beacon. A family who
   lands on /guides/<x>/?ref=em-skokie-1120 and taps "Ask about a tour
   here" (/?tour=form#plan-visit) arrives on the homepage with no ref and
   a same-site referrer, so app.js counts the landing, the form view's
   neighbours and the plan-visit submission as "direct". The referral that
   earned the inquiry is invisible.

   Uses the preinstalled Playwright Chromium. Touches no live site, submits
   no form and sends nothing anywhere: every request goes to the local
   server. It proves only what the page REQUESTS, not a person or a tour. */
import { createServer } from "node:http";
import { existsSync, readFileSync, statSync } from "node:fs";
import { join, extname, resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";

const HARNESS_UA = "ESCG-harness/1 (automated test; +https://evanstonseniorcareguide.com/)";
const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const { chromium } = createRequire(import.meta.url)("playwright");

const TYPES = { ".html": "text/html; charset=utf-8", ".css": "text/css", ".js": "text/javascript",
  ".txt": "text/plain", ".png": "image/png", ".ico": "image/x-icon", ".svg": "image/svg+xml",
  ".pdf": "application/pdf" };
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
  console.log(`${ok ? "PASS" : "FAIL"}  ${name.padEnd(66)} ${detail}`);
}

const server = await serveDist();
const BASE = `http://127.0.0.1:${server.address().port}`;
const browser = await chromium.launch();

async function open(path, { referer } = {}) {
  const ctx = await browser.newContext({ userAgent: HARNESS_UA, viewport: { width: 390, height: 844 } });
  const page = await ctx.newPage();
  const errors = [];
  const landed = [];
  page.on("pageerror", (e) => errors.push(String(e)));
  page.on("request", (r) => {
    const u = new URL(r.url());
    if (u.pathname === "/t/landed.txt") landed.push(u.searchParams.get("s"));
  });
  await page.goto(BASE + path, { waitUntil: "load", referer });
  return { ctx, page, errors, landed };
}
async function follow(v, selector) {
  await Promise.all([v.page.waitForNavigation({ waitUntil: "load" }), v.page.click(selector)]);
  await v.page.waitForTimeout(300);
  return new URL(v.page.url());
}

const MEDICARE = "/guides/does-medicare-pay-for-senior-care/";
const TOUR = 'a[href^="/?tour=form"]';

/* 1. The exact referral case: tagged guide landing -> tour link. */
{
  const v = await open(MEDICARE + "?ref=em-skokie-1120");
  const u = await follow(v, TOUR);
  check("guide tour link keeps ref (em-skokie-1120)", u.searchParams.get("ref") === "em-skokie-1120", u.search);
  check("guide tour link keeps tour=form and #plan-visit",
    u.searchParams.get("tour") === "form" && u.hash === "#plan-visit", u.search + u.hash);
  check("homepage landing counted as the referral, not direct",
    v.landed.length === 1 && v.landed[0] === "em-skokie-1120", JSON.stringify(v.landed));
  check("no page errors (tagged tour click)", v.errors.length === 0, v.errors.join(" | "));
  await v.ctx.close();
}

/* 2. utm_source arrival and sanitisation use the same rule as app.js. */
{
  const v = await open(MEDICARE + "?utm_source=" + encodeURIComponent("Face Book<script>_Group!!-2026-abcdefghij"));
  const u = await follow(v, TOUR);
  check("utm_source carried as the sanitised token", u.searchParams.get("ref") === "facebookscriptgroup-2026", u.search);
  check("homepage landing matches the token", v.landed[0] === "facebookscriptgroup-2026", JSON.stringify(v.landed));
  await v.ctx.close();
}

/* 3. External referrer (e.g. search) carried as its host token only. */
{
  const v = await open(MEDICARE, { referer: "https://www.google.com/search?q=private" });
  const u = await follow(v, TOUR);
  check("search referrer carried as host token only", u.searchParams.get("ref") === "google", u.search);
  check("no referrer path or query leaks", u.search.indexOf("private") === -1 && u.search.indexOf("search") === -1, u.search);
  await v.ctx.close();
}

/* 4. Direct arrivals are left untouched. */
{
  const v = await open(MEDICARE);
  const u = await follow(v, TOUR);
  check("direct guide visit adds no ref", !u.searchParams.has("ref"), u.search);
  check("direct homepage landing stays direct", v.landed[0] === "direct", JSON.stringify(v.landed));
  await v.ctx.close();
}

/* 5. Guide -> guide -> tour keeps the tag (multi-page reading). */
{
  const v = await open(MEDICARE + "?ref=em-niles-1120");
  const g = await follow(v, 'main a[href="/guides/assisted-living-cost-illinois/"]');
  check("guide-to-guide link keeps ref", g.searchParams.get("ref") === "em-niles-1120", g.pathname + g.search);
  const t = await v.page.$(TOUR) ? await follow(v, TOUR) : await follow(v, 'a[href^="/#assessment"]');
  check("second guide's homepage link keeps ref", t.searchParams.get("ref") === "em-niles-1120", t.search + t.hash);
  check("homepage landing counted as em-niles-1120", v.landed[0] === "em-niles-1120", JSON.stringify(v.landed));
  await v.ctx.close();
}

/* 6. A link that already carries a tag is not overwritten; the PDF and
      off-site links are never touched. */
{
  const v = await open(MEDICARE + "?ref=em-skokie-1120");
  const hrefs = await v.page.evaluate(() => {
    const a = document.createElement("a");
    a.id = "pre"; a.href = "/?ref=other#plan-visit"; a.textContent = "x";
    document.body.appendChild(a);
    const ev = (el) => { el.addEventListener("click", (e) => e.preventDefault()); el.click(); return el.getAttribute("href"); };
    const pdf = document.querySelector('a[href^="/downloads/"]');
    const ext = document.querySelector('a[href^="http"]:not([href*="127.0.0.1"])');
    return { pre: ev(a), pdf: pdf ? ev(pdf) : null, ext: ext ? ev(ext) : null };
  });
  check("existing ref on a link is kept", hrefs.pre === "/?ref=other#plan-visit", hrefs.pre);
  check("checklist PDF link untouched", hrefs.pdf === "/downloads/senior-living-tour-checklist.pdf", String(hrefs.pdf));
  check("off-site link untouched", hrefs.ext === null || hrefs.ext.indexOf("ref=") === -1, String(hrefs.ext));
  await v.ctx.close();
}

/* 7. On the homepage nav.js must NOT turn same-page anchors into reloads. */
{
  const v = await open("/?ref=fb-wnk-1120");
  const href = await v.page.evaluate(() => {
    const a = document.createElement("a");
    a.href = "/#assessment"; a.textContent = "x";
    document.body.appendChild(a);
    a.addEventListener("click", (e) => e.preventDefault());
    a.click();
    return a.getAttribute("href");
  });
  check("homepage /#anchor links are left alone by nav.js", href === "/#assessment", href);
  check("no page errors (homepage)", v.errors.length === 0, v.errors.join(" | "));
  await v.ctx.close();
}

await browser.close();
server.close();
console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
