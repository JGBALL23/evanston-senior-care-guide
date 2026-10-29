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
const externals = new Set();
for (const care of careTypes) {
  for (const r of p.getRoutes(care, "no", "no")) {
    for (const h of [r.link, r.guide, r.more]) {
      if (!h) continue;
      if (h.startsWith("/")) hrefs.add(h); else externals.add(h);
    }
    check(care + "/" + r.id + ": every link has text, and no text without a link", () => {
      assert(r.link && r.linkText);
      assert(!!r.guide === !!r.guideText);
      assert(!!r.more === !!r.moreText);
    });
  }
}
check("navigator links at least six site pages", () => assert(hrefs.size >= 6, [...hrefs].join(", ")));
const indexHtml = fs.readFileSync(path.join(dist, "index.html"), "utf8");
for (const h of hrefs) {
  check("site link exists in _dist: " + h, () => {
    if (h.startsWith("/#")) assert(indexHtml.includes('id="' + h.slice(2) + '"'), "no section " + h);
    else assert(fs.existsSync(path.join(dist, h.replace(/^\//,""), "index.html")), h);
  });
}
check("external links are https and agency domains only", () => {
  for (const l of externals)
    assert(/^https:\/\/(www\.medicare\.gov|hfs\.illinois\.gov|www\.va\.gov|idoi\.illinois\.gov)\//.test(l), l);
});

/* ---- relevance: each care type is sent to information about that care type ---- */
const route = (care, id) => p.getRoutes(care, "no", "no").find((x) => x.id === id);
const AL_COST = "/guides/assisted-living-cost-illinois/";
for (const care of ["skilled", "rehab", "memory", "independent", "unsure"]) {
  check(care + ": private pay never points at assisted-living costs", () => {
    const r = route(care, "private");
    for (const h of [r.link, r.guide, r.more]) assert(h !== AL_COST, care + " -> " + h);
  });
}
check("assisted: private pay points at the assisted-living cost guide and the cost figures", () => {
  const r = route("assisted", "private");
  assert.equal(r.link, AL_COST); assert.equal(r.guide, "/#cost");
});
check("independent: private pay points at the independent-living guide", () =>
  assert.equal(route("independent", "private").link, "/guides/independent-living-evanston/"));
for (const care of ["skilled", "rehab", "memory", "unsure"]) {
  check(care + ": private pay points at the per-level cost figures", () =>
    assert.equal(route(care, "private").link, "/#cost"));
}
check("the private-pay link text names the level it is about", () => {
  assert(/nursing home/i.test(route("skilled", "private").linkText));
  assert(/rehabilitation/i.test(route("rehab", "private").linkText));
  assert(/memory/i.test(route("memory", "private").linkText));
  assert(/independent living/i.test(route("independent", "private").linkText));
  assert(/each level/i.test(route("unsure", "private").linkText));
});
for (const care of ["skilled", "rehab"]) {
  check(care + ": Medicare points at the skilled-nursing-facility page", () =>
    assert(/skilled-nursing-facility/.test(route(care, "medicare").link)));
}
for (const care of ["assisted", "memory"]) {
  check(care + ": Medicaid points at the Supportive Living Program page and guide", () => {
    assert(/slf\.html$/.test(route(care, "medicaid").link));
    assert.equal(route(care, "medicaid").guide, "/guides/illinois-supportive-living-program/");
  });
}
check("independent: Medicaid points at paid help at home, not nursing-home Medicaid", () =>
  assert.equal(route("independent", "medicaid").guide, "/guides/illinois-community-care-program/"));
check("skilled: Medicaid also offers the estate-recovery guide", () =>
  assert.equal(route("skilled", "medicaid").more, "/guides/illinois-medicaid-estate-recovery/"));
check("Veteran-Directed Care (care at home) is offered only where the person may be at home", () => {
  for (const care of careTypes) {
    const vdc = route(care, "va").more === "/guides/va-veteran-directed-care-program/";
    assert.equal(vdc, care === "unsure" || care === "independent", care);
  }
});
check("SHIP counselling is offered on every Medicare card", () => {
  for (const care of careTypes) assert.equal(route(care, "medicare").more, "/guides/illinois-senior-health-insurance-program/");
});

/* ---- ordering is explained, never asserted ---- */
check("every care type has a hedged reason for its order", () => {
  for (const care of careTypes) {
    const why = p.ORDER_WHY[care];
    assert(why && why.length > 60, care);
    assert(!promises(why), why);
    assert(!/\b(recommend|should|must|best option|guaranteed)\b/i.test(why), why);
  }
});
check("assisted living and memory care put the private quote first, Medicare last", () => {
  for (const care of ["assisted", "memory"]) {
    const ids = p.getRoutes(care, "no", "no").map((x) => x.id);
    assert.equal(ids[0], "private"); assert.equal(ids[4], "medicare");
  }
});
check("a moved route carries the visitor's own answer as the reason; nothing else does", () => {
  for (const care of careTypes) {
    for (const r of p.getRoutes(care, "no", "no")) assert.equal(r.reason, null);
    for (const r of p.getRoutes(care, "unsure", "unsure")) assert.equal(r.reason, null);
    const v = p.getRoutes(care, "yes", "no");
    assert.equal(v[0].id, "va"); assert.equal(v[0].reason, "veteran");
    assert(v.slice(1).every((r) => r.reason === null));
    const b = p.getRoutes(care, "yes", "yes");
    assert.equal(b[0].reason, "policy"); assert.equal(b[1].reason, "veteran");
  }
  for (const k of ["veteran", "policy"]) assert(/Moved up because you answered Yes/.test(p.REASON_TEXT[k]));
});
check("'Not sure' results mark nothing as the place to start", () => {
  const html = p.renderCards("unsure", "no", "no");
  assert(!html.includes("Worth checking first"));
  assert(!html.includes("Start here"));
  assert(!html.includes("paynav__route--lead"));
  assert(!html.includes("paynav__why"));
});
check("a chosen care type marks only the first card, and says it is worth checking, not a verdict", () => {
  const html = p.renderCards("assisted", "no", "no");
  assert.equal((html.match(/paynav__route--lead/g) || []).length, 1);
  assert(html.startsWith('<li class="paynav__route paynav__route--lead">'));
  assert.equal((html.match(/Worth checking first/g) || []).length, 1);
  assert(!html.includes("Start here"));
});
check("a 'yes' marks the moved card with the visitor's answer, even for 'Not sure'", () => {
  const html = p.renderCards("unsure", "yes", "no");
  assert(html.startsWith('<li class="paynav__route paynav__route--lead">'));
  assert(html.includes("Moved up by your answer"));
  assert(html.includes("Veteran or surviving spouse"));
  assert(!html.includes("Worth checking first"));
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
check("the navigator is in the menu on the home page, after the guides and before the assessment", () => {
  const menu = html.slice(html.indexOf('id="navMenu"'), html.indexOf("</nav>"));
  const i = menu.indexOf('href="/guides/">Care Guides'), j = menu.indexOf('href="/#paying-nav">Paying for care'), k = menu.indexOf('href="/#assessment">Start assessment');
  assert(i > 0 && j > i && k > j, menu);
});
check("the navigator is in the visible desktop bar on the home page, before Start", () => {
  const bar = html.slice(html.indexOf('class="nav__links"'), html.indexOf('id="navMenu"'));
  const i = bar.indexOf('href="#paying-nav"'), j = bar.indexOf('class="nav__cta"');
  assert(i > 0 && j > i, bar);
  assert(bar.includes('<span class="nav__long">Paying for care</span><span class="nav__short">How to pay</span>'));
  assert.equal((bar.match(/nav__cta"/g) || []).length, 1, "one call to action in the bar");
});
const css = fs.readFileSync(path.join(root, "styles.css"), "utf8");
check("the bar has a compact band so six items never wrap or overflow above 880px", () => {
  assert(css.includes(".nav__short { display: none; }"));
  const band = css.slice(css.indexOf("@media (min-width: 881px) and (max-width: 1139px) {"));
  assert(band.includes(".nav__links { gap: 16px; }") && band.includes("white-space: nowrap") && band.includes(".nav__short { display: inline; }"), "compact band");
  assert(/@media \(min-width: 881px\) and \(max-width: 1019px\) \{\s*\.brand__name, \.brand__sub \{ display: none; \}/.test(css), "wordmark band");
});
check("the assessment keeps the only call-to-action button in the nav", () => {
  const navBar = html.slice(html.indexOf("<nav"), html.indexOf("</nav>"));
  assert.equal((navBar.match(/nav__cta/g) || []).length >= 1, true);
  assert(!/nav__cta[^>]*paying-nav/.test(navBar));
});
check("arriving from a guide is counted apart from the other two pathways", () => {
  assert(app.includes('guidePay:        "/t/guide-choice-pay.txt"'));
  assert(app.includes('const PAY_PARAM = param("pay");'));
  assert(app.includes('if (PAY_PARAM === "guide") beacon(FUNNEL.guidePay);'));
  for (const dir of ["t", path.join("_dist", "t")])
    assert.equal(fs.readFileSync(path.join(root, dir, "guide-choice-pay.txt"), "utf8").trim(), "guide-choice-pay");
});
const buildSrc = fs.readFileSync(path.join(root, "build-guides.py"), "utf8");
const payGuides = [...buildSrc.slice(buildSrc.indexOf("PAY_NAV_GUIDES = ["), buildSrc.indexOf("]", buildSrc.indexOf("PAY_NAV_GUIDES = ["))).matchAll(/"([a-z0-9-]+)"/g)].map((m) => m[1]);
check("the guide line is restricted to guides about paying", () => {
  assert(payGuides.length >= 6 && payGuides.length <= 10, payGuides.join(","));
  for (const s of ["independent-living-evanston", "check-illinois-inspection-records", "illinois-care-facility-complaint", "levels-of-senior-care-explained", "illinois-family-caregiver-support-program"])
    assert(!payGuides.includes(s), s + " should not carry the payment line");
});
for (const d of fs.readdirSync(path.join(dist, "guides"), { withFileTypes: true }).filter((e) => e.isDirectory()).map((e) => e.name)) {
  const page = fs.readFileSync(path.join(dist, "guides", d, "index.html"), "utf8");
  check("guide " + d + ": nav offers Paying for care, and the payment line appears only if it is a paying guide", () => {
    assert(page.includes('href="/#paying-nav">Paying for care</a>'));
    const bar = page.slice(page.indexOf('class="nav__links"'), page.indexOf('id="navMenu"'));
    assert(bar.indexOf('href="/#paying-nav">Paying for care</a>') > 0 && bar.indexOf('href="/#paying-nav"') < bar.indexOf('class="nav__cta"'), "desktop bar");
    assert.equal((bar.match(/nav__cta"/g) || []).length, 1, "one call to action in the bar");
    assert.equal(page.includes('class="related__pay"'), payGuides.includes(d), d);
    assert.equal((page.match(/related__pay/g) || []).length <= 1, true);
    if (payGuides.includes(d)) assert(page.includes('href="/?pay=guide#paying-nav"'));
    assert.equal((page.match(/class="btn btn--primary"/g) || []).length, 1, "a guide keeps exactly one button");
  });
}
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
