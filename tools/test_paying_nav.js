/* Workflow #5: deterministic, no-browser regression checks.
   Run: node tools/test_paying_nav.js
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
        const expected = new Map(baseline.map(x=>[x.id,{title:x.title,summary:x.summary,link:x.link}]));
        for(const item of rs) assert.deepEqual(
          {title:item.title,summary:item.summary,link:item.link},expected.get(item.id));
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
  assert.equal(p.normalizeCare("unexpected"),"unsure");
  assert(p.getRoutes("unsure","no","no").every(x=>!x.summary.includes("traditional assisted-living bill")));
});
check("veteran yes promotes VA", () =>
  assert.equal(p.getRoutes("skilled","yes","no")[0].id,"va"));
check("policy yes promotes long-term-care insurance", () =>
  assert.equal(p.getRoutes("rehab","no","yes")[0].id,"ltci"));
check("no policy leaves the policy wording unchanged", () =>
  assert.equal(
    p.getRoutes("memory","yes","yes").find(x=>x.id==="ltci").summary,
    p.getRoutes("memory","no","no").find(x=>x.id==="ltci").summary));
const root = path.join(__dirname,"..");
const html = fs.readFileSync(path.join(root,"index.html"),"utf8");
const app = fs.readFileSync(path.join(root,"app.js"),"utf8");
const nav = fs.readFileSync(path.join(root,"paying-nav.js"),"utf8");
check("dedicated navigator section id", () =>
  assert.equal((html.match(/id="paying-nav"/g)||[]).length,1));
check("script loads before app", () =>
  assert(html.indexOf('src="paying-nav.js"') < html.indexOf('src="app.js"')));
check("results link reuses the care type", () =>
  assert(app.includes('paymentEntry(level.id)') && app.includes('paymentEntry("unsure")')));
check("back from prefill allows changing care", () =>
  assert(nav.includes('if (stage === 0) state.care = null')));
check("start beacon fires from prefilling too", () =>
  assert(nav.includes('beacon("pay-nav-started"); // also for assessment-prefilled starts')));
check("no contact or private answer collection in navigator", () => {
  assert(!nav.includes('localStorage'));
  assert(!nav.includes('sessionStorage'));
  assert(!nav.includes('XMLHttpRequest'));
  assert(!nav.includes('fetch("/api/'));
});
console.log(count + "/" + count + " Workflow #5 checks passed");
