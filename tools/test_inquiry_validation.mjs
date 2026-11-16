/* Offline regression test: what a tap on "Request a tour" does when the
   inquiry form is incomplete, on a 390x844 phone.

   Run:  node tools/test_inquiry_validation.mjs   (serves _dist on 127.0.0.1)

   Uses the preinstalled Playwright Chromium. Touches no live site and sends
   nothing anywhere: every request goes to the local server, and the one
   POST the form can make is answered by a stub inside the browser. No
   consent wording, payload field or endpoint is changed by the fix this
   tests; it only marks the missing fields and moves focus to the first.

   Found 2026-11-16: the error message renders below the button, so on a
   phone it sat just under the bottom edge and an incomplete tap looked
   like nothing happened. */
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

async function openForm(path) {
  const ctx = await browser.newContext({ userAgent: HARNESS_UA, viewport: { width: 390, height: 844 },
    isMobile: true, hasTouch: true });
  const page = await ctx.newPage();
  const posts = [];
  const errors = [];
  page.on("pageerror", (e) => errors.push(String(e)));
  await page.route("**/api/plan-visit", (route) => {
    posts.push(route.request().postData());
    route.fulfill({ status: 200, contentType: "application/json",
      body: JSON.stringify({ ok: true, receivedAt: "2026-11-16T00:00:00Z", submissionId: "test-stub" }) });
  });
  await page.goto(BASE + path, { waitUntil: "load" });
  await page.waitForSelector("#plan-form");
  return { ctx, page, posts, errors };
}

const state = (page) => page.evaluate(() => {
  const inView = (el) => { const r = el.getBoundingClientRect(); return r.top >= 0 && r.bottom <= innerHeight; };
  const f = document.getElementById("plan-form");
  const s = document.getElementById("plan-status");
  const a = document.activeElement;
  return {
    active: a && a.name,
    activeInView: a && a.name ? inView(a) : false,
    statusInView: inView(s),
    status: s.textContent,
    statusError: s.classList.contains("plan__status--error"),
    invalid: [...f.querySelectorAll('[aria-invalid="true"]')].map((e) => e.name).join(","),
    describedBy: [...f.querySelectorAll('[aria-invalid="true"]')].every((e) => e.getAttribute("aria-describedby") === "plan-status"),
    borderRed: (() => { const e = f.elements.firstName; return getComputedStyle(e).borderTopColor; })()
  };
});

async function tapSubmit(page) {
  await page.tap("#plan-form .plan__submit");
  await page.waitForTimeout(250);
}

for (const path of ["/?tour=form#plan-visit", "/?tour=independent#plan-visit"]) {
  const { ctx, page, posts, errors } = await openForm(path);
  const tag = path.split("#")[0];

  /* 1. Empty form, tapped with the button at the bottom of the screen. */
  await page.locator("#plan-form .plan__submit").scrollIntoViewIfNeeded();
  await tapSubmit(page);
  let s = await state(page);
  check(`${tag} empty: error message set`, s.statusError && /first name/.test(s.status), s.status.slice(0, 40));
  check(`${tag} empty: focus on first name`, s.active === "firstName", s.active);
  check(`${tag} empty: focused field is on screen`, s.activeInView);
  check(`${tag} empty: all five marked invalid`, s.invalid === "firstName,lastName,phone,email,consent", s.invalid);
  check(`${tag} empty: marked fields described by the message`, s.describedBy);
  check(`${tag} empty: missing field drawn in the error colour`, s.borderRed === "rgb(140, 58, 40)", s.borderRed);
  check(`${tag} empty: nothing sent`, posts.length === 0);

  /* 2. Typing a first name clears only that mark. */
  await page.fill('#plan-form input[name="firstName"]', "Test");
  s = await state(page);
  check(`${tag} first name filled: its mark cleared`, s.invalid === "lastName,phone,email,consent", s.invalid);

  /* 3. Only consent missing: focus lands on the box, message visible too. */
  await page.fill('#plan-form input[name="lastName"]', "Case");
  await page.fill('#plan-form input[name="email"]', "test@example.invalid");
  s = await state(page);
  check(`${tag} email filled: phone and email both cleared`, s.invalid === "consent", s.invalid);
  await tapSubmit(page);
  s = await state(page);
  check(`${tag} no consent: focus on the consent box`, s.active === "consent", s.active);
  check(`${tag} no consent: box on screen`, s.activeInView);
  check(`${tag} no consent: message on screen`, s.statusInView, s.status.slice(0, 40));
  check(`${tag} no consent: only consent marked`, s.invalid === "consent", s.invalid);
  check(`${tag} no consent: nothing sent`, posts.length === 0);

  /* 4. Complete: sent once to the stub, no marks left. */
  await page.check("#plan-consent");
  s = await state(page);
  check(`${tag} consent ticked: mark cleared`, s.invalid === "", s.invalid);
  await tapSubmit(page);
  await page.waitForSelector(".plan__done-h");
  check(`${tag} complete: sent exactly once`, posts.length === 1);
  const body = JSON.parse(posts[0] || "{}");
  check(`${tag} complete: payload unchanged in shape`,
    JSON.stringify(Object.keys(body).sort()) ===
    JSON.stringify(["careLevel", "consent", "email", "firstName", "interest", "lastName", "phone"]),
    Object.keys(body).join(","));
  check(`${tag} no page errors`, errors.length === 0, errors.join(" | "));
  await ctx.close();
}

await browser.close();
server.close();
console.log(`\n${pass}/${pass + fail} inquiry-validation checks passed`);
process.exit(fail ? 1 : 0);
