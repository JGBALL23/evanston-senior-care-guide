/* Workflow #5: deterministic, no-browser regression checks.
   Run: node tools/test_paying_nav.js

   What this guards: the five funding routes are always all present, a
   "yes" only reorders them, "Not sure" is neutral, every link and beacon
   the navigator can request exists in the publish directory, and the
   navigator collects nothing. The browser walk lives in
   tools/wf5_browser_walk.mjs; this file is what runs anywhere.
*/
"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const p = require("../paying-nav.js");
let count = 0;
function check(desc, cb) { try {cb();count++;} catch(e) { console.error("FAIL: " + desc); throw e;} }
const careTypes = Object.keys(p.CARE);
const yn = ["yes","no","unsure"];
for (const care of careTypes) {
  for (const veteran of yn) {
    for (const policy of yn) {
      const rs = p.getRoutes(care, veteran, policy);
      check(care + " " + veteran + " " + policy + ": five unique options", () => {
        assert.equal(rs.length,5);
        assert.equal(new Set(rs.map(x=>x.id)).size,5);
        assert(rs.some(x => x.id === "medicaid"));
      });
      check(care + " " + veteran + " " + policy + ": yes changes order only", () => {
        const baseline = p.getRoutes(care,"no","no");
        const expected = new Map(baseline.map(x=>[x.id,{title:x.title,summary:x.summary,link:x.link,guide:x.guide,more:x.more}]));
        for(const item of rs) assert.deepEqual(
          {title:item.title,summary:item.summary,link:item.link,guide:item.guide,more:item.more},expected.get(item.id));
      });
      check(care + " " + veteran + " " + policy + ": source links", () => {
        for(const item of rs) assert(item.link.startsWith("/") || item.link.startsWith("https://"));
      });
    }
  }
}
check("not sure is neutral, never assisted by default", () => {
  assert.equal(p.normalizeCare("unsure"),"unsure");
  assert.equal(p.normalizeCare("no_need"),"unsure");
  assert.equal(p.normalizeCare("direct"),"unsure");
  assert.equal(p.normalizeCare("unexpected"),"unsure");
  assert.equal(p.normalizeCare(null),"unsure");
  assert(p.getRoutes("unsure","no","no").every(x=>!x.summary.includes("traditional assisted-living bill")));
});
check("veteran yes promotes VA", () =>
  assert.equal(p.getRoutes("skilled","yes","no")[0].id,"va"));
check("policy yes promotes long-term-care insurance", () =>
  assert.equal(p.getRoutes("rehab","no","yes")[0].id,"ltci"));
check("both yes: policy first, VA second, nothing dropped", () => {
  const ids = p.getRoutes("assisted","yes","yes").map(x=>x.id);
  assert.deepEqual(ids.slice(0,2), ["ltci","va"]);
  assert.equal(ids.length, 5);
});
check("no and not sure are indistinguishable in the order", () => {
  for (const care of careTypes) {
    assert.deepEqual(p.getRoutes(care,"no","no").map(x=>x.id), p.getRoutes(care,"unsure","unsure").map(x=>x.id));
    assert.deepEqual(p.getRoutes(care,"no","unsure").map(x=>x.id), p.getRoutes(care,"unsure","no").map(x=>x.id));
  }
});
check("no policy leaves the policy wording unchanged", () =>
  assert.equal(
    p.getRoutes("memory","yes","yes").find(x=>x.id==="ltci").summary,
    p.getRoutes("memory","no","no").find(x=>x.id==="ltci").summary));

/* ---- no promises: wording stays hedged for every care type ---- */
/* A sentence that denies coverage ("does not guarantee", "is not covered")
   is the opposite of a promise, so each pattern counts only in a sentence
   with no negation. Figures and percentages count regardless. */
const PROMISES = [/will cover/i, /will pay/i, /guarantee[ds]?\b/i, /you qualify/i, /you are eligible/i,
  /\b(is|are) covered\b/i, /\bfree of charge\b/i];
const FIGURES = [/\$\s?\d/, /\d+\s?%/];
function promises(text) {
  const sentences = text.split(/[.;]/);
  return sentences.some((s) => !/\b(not|never|no)\b/i.test(s) && PROMISES.some((re) => re.test(s)))
    || FIGURES.some((re) => re.test(text));
}
for (const care of careTypes) {
  for (const r of p.getRoutes(care,"no","no")) {
    check(care + "/" + r.id + ": no promise of coverage, eligibility or an amount", () =>
      assert(!promises(r.summary), r.summary));
  }
}

/* ---- every page the navigator links to exists in the publish directory ---- */
const root = path.join(__dirname,"..");
const dist = path.join(root,"_dist");
const hrefs = new Set();
for (const key of Object.keys(p.ROUTES)) {
  const r = p.ROUTES[key];
  for (const h of [r.link, r.guide, r.more]) if (h && h.startsWith("/")) hrefs.add(h);
}
check("navigator links at least four site guides", () => assert(hrefs.size >= 4, [...hrefs].join(", ")));
for (const h of hrefs) {
  check("site link exists in _dist: " + h, () =>
    assert(fs.existsSync(path.join(dist, h.replace(/^\//,""), "index.html")), h));
}
check("external links are https and agency domains only", () => {
  for (const key of Object.keys(p.ROUTES)) {
    const l = p.ROUTES[key].link;
    if (l.startsWith("/")) continue;
    assert(/^https:\/\/(www\.medicare\.gov|hfs\.illinois\.gov|www\.va\.gov|idoi\.illinois\.gov)\//.test(l), l);
  }
});

/* ---- beacons: literal paths, and a file behind every one of them ---- */
const html = fs.readFileSync(path.join(root,"index.html"),"utf8");
const app = fs.readFileSync(path.join(root,"app.js"),"utf8");
const nav = fs.readFileSync(path.join(root,"paying-nav.js"),"utf8");
const literals = [...nav.matchAll(/"\/t\/([a-z0-9-]+)\.txt"/g)].map(m=>m[1]);
check("beacon paths are string literals the build can read", () => {
  assert.deepEqual(literals.sort(), ["pay-nav-completed","pay-nav-started"]);
  assert(!nav.includes('"/t/" +'), "beacon path built at runtime");
});
check("every beacon literal maps to a BEACONS entry", () =>
  assert.deepEqual(Object.values(p.BEACONS).sort(), literals.map(n=>"/t/"+n+".txt").sort()));
for (const n of literals) {
  for (const dir of ["t", path.join("_dist","t")]) {
    check("beacon file exists: " + path.join(dir, n + ".txt"), () =>
      assert.equal(fs.readFileSync(path.join(root, dir, n + ".txt"),"utf8").trim(), n));
  }
}
check("beacon fetches are cache-busted and never block", () =>
  assert(nav.includes('cache:"no-store"') && nav.includes("keepalive:true") && nav.includes(".catch(() => {})")));

/* ---- page wiring ---- */
check("dedicated navigator section id", () =>
  assert.equal((html.match(/id="paying-nav"/g)||[]).length,1));
check("widget container exists once, with no live region (focus is managed instead)", () => {
  assert.equal((html.match(/id="paying-nav-widget"/g)||[]).length,1);
  assert(!/id="paying-nav-widget"[^>]*aria-live/.test(html));
});
check("section is labelled by its heading", () =>
  assert(/<section[^>]*id="paying-nav"[^>]*aria-labelledby="paying-nav-title"/.test(html) && html.includes('id="paying-nav-title"')));
check("no-JS fallback names all five routes", () => {
  const m = html.match(/id="paying-nav-widget"[^>]*>\s*<p>([\s\S]*?)<\/p>/);
  assert(m, "fallback paragraph missing");
  for (const w of ["Medicare","Medicaid","VA","long-term-care insurance","private payment"]) assert(m[1].includes(w), w);
});
check("script loads before app", () =>
  assert(html.indexOf('src="paying-nav.js"') < html.indexOf('src="app.js"')));
check("results link reuses the care type", () =>
  assert(app.includes('paymentEntry(level.id)') && app.includes('paymentEntry("unsure")')));
check("entry link is a styled button carrying only the care id", () => {
  assert(app.includes('class="paynav__entry-btn"'));
  assert(app.includes('data-pay-nav-care="\' + esc(care)'));
  assert(!/data-pay-nav-care[^>]*answers/.test(app));
});
check("page load renders without moving focus; interaction renders with focus", () => {
  const initBody = nav.slice(nav.indexOf("function init("));
  const firstRender = initBody.match(/render\((true|false)\)/);
  assert(firstRender && firstRender[1] === "false", "the page-load render in init must be render(false)");
  assert((nav.match(/render\(true\)/g)||[]).length >= 4, "every interaction path renders with focus");
});
check("back keeps earlier answers so they stay highlighted", () => {
  assert(nav.includes("stage = Math.max(0, stage - 1)"));
  assert(!nav.includes("state.care = null; // back"));
});
check("the carried-over care type is shown with a Change control", () => {
  assert(nav.includes("data-pay-change"));
  assert(nav.includes("Care type: <strong>' + CARE[state.care]"));
});
check("the current answer is marked for assistive tech and sight", () =>
  assert(nav.includes('aria-pressed') && nav.includes("is-selected")));
check("entry click scrolls even when the hash is unchanged", () =>
  assert(nav.includes('root.location.hash = "paying-nav"') && nav.includes('section.scrollIntoView({block:"start"})')));
check("start beacon fires from prefilling too", () =>
  assert(nav.includes('beacon("pay-nav-started"); // also for assessment-prefilled starts')));
check("the navigator never touches the assessment", () => {
  const code = nav.replace(/\/\*[\s\S]*?\*\//g, "");
  for (const ident of ["assess(", "answers[", "answers.", "resultLevelId", "QUESTIONS[step].id", "plan-form", "getElementById(\"quiz\")"]) assert(!code.includes(ident), ident);
});
check("no contact or private answer collection in navigator", () => {
  assert(!nav.includes('localStorage'));
  assert(!nav.includes('sessionStorage'));
  assert(!nav.includes('XMLHttpRequest'));
  assert(!nav.includes('fetch("/api/'));
  assert(!nav.includes('document.cookie'));
  assert(!/<input|<form|<textarea/.test(nav));
});
check("external links open in a new tab with noopener; site links do not", () =>
  assert(nav.includes("target=\"_blank\" rel=\"noopener\"") && nav.includes('href.charAt(0) !== "/"')));
console.log(count + "/" + count + " Workflow #5 checks passed");
