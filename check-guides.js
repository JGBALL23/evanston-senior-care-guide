/* ============================================================
   check-guides.js  —  gates for the /guides/ article library
   Run:  node check-guides.js
   These checks were ephemeral once. Written down 2026-10-18,
   after the owner caught a reproduced arithmetic error that no
   gate was holding.
   ============================================================ */
const fs = require("fs");
const path = require("path");

const DIST = path.join(__dirname, "_dist");

/* SLUGS is DERIVED from build-guides.py, not typed out here.
   It used to be a hand-written list of five, and so were the card
   count and the sitemap URL count. That meant the act of adding a
   sixth guide broke the suite that was supposed to approve it - the
   author would have had to edit three numbers in this file to make a
   correct change pass. A daily routine cannot be asked to maintain
   its own grading constants; it would either fail forever or learn to
   edit the gate.
   Reading the generator keeps build-guides.py the single source of
   truth for what SHOULD exist, so the gate still catches a guide that
   quietly vanished from _dist - it just no longer hardcodes how many
   there are. */
const GEN = fs.readFileSync(path.join(__dirname, "build-guides.py"), "utf8");
const SLUGS = (GEN.match(/^\s*"slug":\s*"([a-z0-9-]+)"/gm) || [])
  .map((m) => m.replace(/.*"slug":\s*"/, "").replace(/"$/, ""));
if (SLUGS.length < 5) {
  console.log("  FAIL  could not read the slug list out of build-guides.py");
  process.exit(1);
}

/* ---- WHAT COUNTS AS A PRIMARY SOURCE ----
   va.gov added 2026-10-25 on the owner's approval, after the daily routine
   researched VA Aid & Attendance, fetched five va.gov pages successfully,
   and then THREW THE TOPIC AWAY because this gate would have rejected the
   citations. It refused to edit the gate. Correct call - so the owner
   widened the list instead.

   The old test was a bare regex run against the whole href:
       /(medicare\.gov|cms\.gov|hfs\.illinois\.gov|illinois\.gov|...)/
   That matches anywhere in the string, so `https://evil.example.com/
   ?ref=illinois.gov` passed it. Adding a domain to that pattern would have
   widened a hole as well as a list. This parses the HOST and matches it
   exactly or as a true subdomain, which is strictly tighter than before
   even though it now allows more sources.

   Everything else about evidence is unchanged: the source must still be
   fetched and READ, the claim must still come off the page, and
   check-citations.sh must still resolve the URL over the network. A wider
   allowlist is not a lower bar. */
const PRIMARY_HOSTS = [
  "medicare.gov",      // Medicare coverage and cost pages
  "cms.gov",           // CMS rules, fact sheets, manuals
  "illinois.gov",      // HFS, Dept on Aging, IDPH, report card
  "va.gov",            // VA pension, Aid & Attendance, survivors
  "assets.carescout.com", // the Cost of Care Survey PDF, exact host only
];
function isPrimarySource(href) {
  const m = /^https?:\/\/([^/"?#]+)/.exec(String(href).replace(/^href="/, ""));
  if (!m) return false;
  const host = m[1].toLowerCase().replace(/:\d+$/, "");
  return PRIMARY_HOSTS.some((d) => host === d || host.endsWith("." + d));
}

let pass = 0, fail = 0;
function check(name, ok, detail) {
  if (ok) { pass++; }
  else { fail++; console.log("  FAIL  " + name + (detail ? "   [" + detail + "]" : "")); }
}
const read = (p) => fs.readFileSync(p, "utf8");
const page = {};
SLUGS.forEach((s) => { page[s] = read(path.join(DIST, "guides", s, "index.html")); });
const indexPage = read(path.join(DIST, "guides", "index.html"));
const sitemap = read(path.join(DIST, "sitemap.xml"));
const all = SLUGS.map((s) => page[s]).join("\n");
const flat = (s) => s.replace(/\s+/g, " ");
const lc = (s) => flat(s).toLowerCase();

/* ---------------- TECHNICAL ---------------- */
SLUGS.forEach((s) => {
  const h = page[s];
  check("canonical: " + s,
    h.indexOf('rel="canonical" href="https://evanstonseniorcareguide.com/guides/' + s + '/"') !== -1);
  check("single h1: " + s, (h.match(/<h1[\s>]/g) || []).length === 1);
  check("title present: " + s, /<title>[^<]{20,}<\/title>/.test(h));
  check("meta description: " + s, /name="description" content="[^"]{60,}"/.test(h));
  check("stylesheet linked: " + s, h.indexOf("styles.css") !== -1);
  check("privacy link: " + s, h.indexOf("/privacy.html") !== -1);
  const ld = h.match(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/);
  let ok = false;
  try { JSON.parse(ld[1]); ok = true; } catch (e) { ok = false; }
  check("JSON-LD parses: " + s, ok);
});

/* ---------------- FACTUAL FIGURES ---------------- */
const FIG = {
  "$6,219": "assisted-living-cost-illinois",
  "$8,304": "assisted-living-cost-illinois",
  "$9,216": "assisted-living-cost-illinois",
  "$1,736": "does-medicare-pay-for-senior-care",
  "$217": "does-medicare-pay-for-senior-care",
  "$17,360": "does-medicare-pay-for-senior-care",
  "$120": "illinois-supportive-living-program",
  "$874": "illinois-supportive-living-program",
  "$625.50": "illinois-supportive-living-program",
};
Object.keys(FIG).forEach((f) => {
  check("figure present " + f + " in " + FIG[f], page[FIG[f]].indexOf(f) !== -1);
});
check("SNF arithmetic holds: 80 x 217 = 17,360", 80 * 217 === 17360);

/* ---- OWNER FINDING 1, 2026-10-18: the state's own example is inconsistent ----
   The HFS resident fact sheet prints 2,400 - 240 - 874 - 120 = 1,197.
   That subtraction equals 1,166. A guide that repeats a source's
   arithmetic inherits its error, and a family plans around a number that
   is wrong on either reading. The METHOD is reproducible; the example is
   not. Never print the derived figure, and never silently substitute a
   corrected one either - we are not the authority on what they owe. */
check("the erroneous group-care-credit figure is absent", all.indexOf("1,197") === -1);
check("the corrected total is not substituted either", all.indexOf("1,166") === -1);
check("no reproduced worked example", lc(all).indexOf("worked example") === -1);
check("group care credit is named",
  lc(page["illinois-supportive-living-program"]).indexOf("group care credit") !== -1);
check("patient liability named as the alias",
  lc(page["illinois-supportive-living-program"]).indexOf("patient liability") !== -1);
check("the method is explained rather than a number",
  lc(page["illinois-supportive-living-program"]).indexOf("countable income after allowable deductions") !== -1);
check("the credit is stated as individually determined",
  lc(page["illinois-supportive-living-program"]).indexOf("determined by the state for that individual") !== -1);
check("the guide refuses to promise an individual's cost",
  lc(page["illinois-supportive-living-program"]).indexOf("no sum on this page that produces your parent") !== -1);
check("two charges, not one",
  lc(page["illinois-supportive-living-program"]).indexOf("expect two charges, not one") !== -1);
check("room and board is dated",
  lc(page["illinois-supportive-living-program"]).indexOf("effective 1 january 2026") !== -1);
check("room and board cites the HFS provider notice",
  page["illinois-supportive-living-program"].indexOf("notice.prn251126a.html") !== -1);

/* ---- OWNER FINDING 2, 2026-10-18: no unsourced local cost claim ----
   "North-shore suburbs sit above the statewide median" had nothing behind
   it. CareScout publishes no Evanston or north-shore median, and the
   Chicago-metro figure circulating on lead-generation sites could not be
   traced to the survey itself. Absent a source, the guide says it does
   not know. */
[/north[- ]shore suburbs (generally )?sit above/i,
 /above the statewide median/i,
 /above a statewide (middle|median)/i,
 /above the illinois average/i,
 /costs run above/i,
 /expect local quotes to land at or above/i].forEach((re, i) => {
  check("no unsourced local-cost claim, pattern " + (i + 1), !re.test(all), String(re));
});
check("the absence of a local median is stated plainly",
  lc(page["assisted-living-cost-illinois"]).indexOf("publishes no") !== -1 &&
  lc(page["assisted-living-cost-illinois"]).indexOf("it does not know") !== -1);
check("the statewide median is labelled statewide",
  lc(page["assisted-living-cost-illinois"]).indexOf("statewide figure, not an evanston figure") !== -1);

/* ---- OWNER FINDING 3, 2026-10-18: skilled coverage is not custodial ---- */
const med = page["does-medicare-pay-for-senior-care"];
check("custodial care is named in the answer", lc(med).indexOf("long-term custodial") !== -1);
check("skilled is defined by who must perform it",
  lc(med).indexOf("under the supervision of licensed professionals") !== -1);
check("custodial is defined by the tasks",
  lc(med).indexOf("bathing, dressing, eating") !== -1);
check("Medicare pays nothing toward custodial care is explicit",
  /pays <strong>nothing<\/strong>\s+toward custodial care/i.test(flat(med)));
check("the same-bed distinction is made",
  lc(med).indexOf("it is not the building that decides this") !== -1 &&
  lc(med).indexOf("same bed") !== -1);
check("assisted living is identified as custodial",
  lc(med).indexOf("assisted living is custodial care") !== -1);
check("the cost schedule is scoped to skilled stays only",
  lc(med).indexOf("nothing below applies to long-term custodial care") !== -1);
["qualifying inpatient hospital stay", "3 days in a row",
 "within 30 days", "daily skilled care", "medicare-certified"].forEach((c) => {
  check("coverage condition stated: " + c, lc(med).indexOf(c) !== -1);
});
check("observation hours do not count is stated",
  lc(med).indexOf("under observation") !== -1 &&
  lc(med).indexOf("do not count toward the three") !== -1);
check("the 3-day waivers are mentioned",
  lc(med).indexOf("3-day rule waiver") !== -1 &&
  lc(med).indexOf("medicare advantage") !== -1);

/* ---- OWNER FINDING 4, 2026-10-18: there is no Improvement Standard ----
   The page said benefits can end because a resident "is no longer
   improving". That is the myth the Jimmo v. Sebelius settlement exists to
   kill. CMS confirmed coverage turns on the NEED FOR SKILLED CARE, not on
   potential to improve: skilled services are covered where they are needed
   to maintain a condition or prevent/slow deterioration, even with no
   expected improvement. Coverage ends when the skilled-care requirements
   stop being met - a different test. Repeating the myth would have taught
   a family to accept a wrongful denial. */
check("the improvement myth is named as a myth",
  /that is not the standard/i.test(flat(med)));
check("Jimmo is named", med.indexOf("Jimmo") !== -1);
check("no Improvement Standard is stated",
  lc(med).indexOf("no &ldquo;improvement standard&rdquo;") !== -1 ||
  lc(med).indexOf("there is no improvement standard") !== -1 ||
  /no\s+&ldquo;improvement standard/i.test(flat(med)));
check("maintenance coverage is stated",
  lc(med).indexOf("maintain") !== -1 &&
  lc(med).indexOf("prevent or slow further deterioration") !== -1);
check("coverage despite no expected improvement is explicit",
  lc(med).indexOf("even when no improvement is expected") !== -1);
check("the correct ending test is given",
  lc(med).indexOf("requirements for skilled care are no longer met") !== -1);
check("non-skilled staff is named as the real trigger",
  lc(med).indexOf("non-skilled staff") !== -1);
check("the family is told how to push back",
  lc(med).indexOf("ask how to appeal") !== -1);
check("the improvement claim is not stated as fact anywhere",
  !/benefits can end on the grounds/i.test(flat(all)));
check("CMS Jimmo fact sheet is cited",
  med.indexOf("jimmo-factsheet.pdf") !== -1);

/* ---- OWNER FINDING 5, 2026-10-18: dates must be the real date ----
   Pages claimed a 19 October 2026 review date on 18 October 2026. A review
   date is a factual claim about when a human or a tool looked, and it is the
   one claim a reader uses to judge every other figure.

   REWRITTEN 2026-10-23. This gate used to pin a literal "18 October 2026"
   and demand every page carry it. That made the date a constant someone had
   to hand-edit, and it forced one global stamp onto pages researched on
   different days - so the only way to add a guide dated today was to re-date
   six pages nobody had re-checked. The intent survives; the implementation
   does not. What actually matters is: a date exists, it is not in the
   future, and the page's three renderings of it agree with each other. */
const MONTHS = ["January", "February", "March", "April", "May", "June", "July",
  "August", "September", "October", "November", "December"];
function isoOf(human) {
  const m = /^([0-9]{1,2}) ([A-Za-z]+) ([0-9]{4})$/.exec(human || "");
  if (!m) return null;
  const mi = MONTHS.indexOf(m[2]);
  if (mi < 0) return null;
  return m[3] + "-" + String(mi + 1).padStart(2, "0")
    + "-" + m[1].padStart(2, "0");
}
const BUILD_DAY = new Date().toISOString().slice(0, 10);
const reviewedOf = {};
SLUGS.concat(["__index"]).forEach((s) => {
  const h = s === "__index" ? indexPage : page[s];
  const human = (h.match(/Last reviewed ([0-9]{1,2} [A-Za-z]+ [0-9]{4})\./) || [])[1];
  const iso = isoOf(human);
  reviewedOf[s] = iso;
  check("prints a parseable review date: " + s, !!iso, String(human));
  check("review date is not in the future: " + s, !!iso && iso <= BUILD_DAY,
    iso + " vs build day " + BUILD_DAY);
});
SLUGS.forEach((s) => {
  const human = (page[s].match(
    /read from the source listed above on ([0-9]{1,2} [A-Za-z]+ [0-9]{4})\./) || [])[1];
  check("verification date matches the review date: " + s,
    isoOf(human) === reviewedOf[s], human + " vs " + reviewedOf[s]);
  check("dateModified matches the review date: " + s,
    page[s].indexOf('"dateModified": "' + reviewedOf[s] + '"') !== -1,
    reviewedOf[s]);
});
/* The index and the sitemap describe the whole library, so they carry the
   newest date in it - never an older one, which would understate freshness,
   and never a newer one, which would be a claim about a page that does not
   exist. */
const NEWEST = SLUGS.map((s) => reviewedOf[s]).sort().slice(-1)[0];
check("the guides index carries the newest review date in the library",
  reviewedOf["__index"] === NEWEST, reviewedOf["__index"] + " vs " + NEWEST);
check("sitemap lastmod is the newest review date",
  sitemap.indexOf(NEWEST) !== -1, NEWEST);
check("no sitemap lastmod is in the future",
  (sitemap.match(/<lastmod>([0-9-]+)<\/lastmod>/g) || [])
    .every((m) => m.replace(/<\/?lastmod>/g, "") <= BUILD_DAY));

/* ---- OWNER FINDING 6, 2026-10-18: turnover is a question, not a prophecy ----
   The page predicted a resident "meets a new caregiver every few weeks" in
   a high-turnover community. An annual building-level rate does not predict
   one resident's week. Explain why it matters; refuse to forecast. */
const insp = page["check-illinois-inspection-records"];
check("the every-few-weeks prediction is gone",
  !/meets a new caregiver every few weeks/i.test(flat(all)));
check("no prediction of an individual's experience",
  !/your parent (will|would) meet/i.test(flat(all)));
check("turnover is scoped to the building over a year",
  lc(insp).indexOf("describes the staff of a building over a year") !== -1);
check("the limit of the number is stated",
  lc(insp).indexOf("does not tell you how often one resident will meet someone new") !== -1);
check("both directions of the caveat are given",
  lc(insp).indexOf("can still have a stable team") !== -1 &&
  lc(insp).indexOf("rotate your parent") !== -1);
check("turnover is turned into visit questions",
  lc(insp).indexOf("a question, not a verdict") !== -1 &&
  lc(insp).indexOf("weekday morning") !== -1);

/* ---- OWNER FINDING 7, 2026-10-18: citations must be clickable AND live ----
   One citation pointed at www.carescout.com; the PDF is served from
   assets.carescout.com and the www host returns 404. A dead citation is
   worse than none - it looks verified. Resolution is checked by
   check-citations.sh against the network; shape is checked here. */
SLUGS.forEach((s) => {
  const m = page[s].match(/<h2 class="res__h">Sources<\/h2>([\s\S]*?)<\/ul>/);
  check("sources block present: " + s, !!m);
  const hrefs = (m ? m[1] : "").match(/href="https?:\/\/[^"]+"/g) || [];
  check("has at least two citations: " + s, hrefs.length >= 2, String(hrefs.length));
  check("every citation opens safely: " + s,
    ((m ? m[1] : "").match(/rel="noopener" target="_blank"/g) || []).length === hrefs.length);
  check("every citation is a primary source: " + s,
    hrefs.every((h) => isPrimarySource(h)), hrefs.join(" "));
  check("no lead-generation citation: " + s,
    !/(caring\.com|aplaceformom|seniorly|seniorliving\.org|brevy|realcostreport)/i.test(page[s]));
});
check("the dead CareScout host is not cited",
  all.indexOf("www.carescout.com/x/") === -1);
check("the live CareScout host is cited",
  page["assisted-living-cost-illinois"].indexOf("assets.carescout.com") !== -1);

/* ---------------- HONESTY ---------------- */
["best nursing home", "top rated", "top-rated", "award-winning", "guaranteed",
 "we recommend", "studies show", "experts agree", "proven to", "world-class",
 "westminster is the", "westminster offers the"].forEach((b) => {
  check("banned claim absent: " + b, lc(all + indexPage).indexOf(b) === -1);
});
SLUGS.forEach((s) => {
  check("employment disclosure: " + s,
    /(by an employee of|works? at) westminster place/i.test(flat(page[s])));
  check("not-official disclosure: " + s,
    lc(page[s]).indexOf("not an official westminster place website") !== -1);
  check("no-referral-fees disclosure: " + s,
    lc(page[s]).indexOf("no referral fees") !== -1);
  check("advice disclaimer: " + s,
    lc(page[s]).indexOf("not medical, legal or financial advice") !== -1);
});
check("the inspection guide tells families to check Westminster too",
  lc(page["check-illinois-inspection-records"]).indexOf("westminster place up too") !== -1);

/* ---- OWNER FINDING 8, 2026-10-18: the index read as a list of links ----
   Every article title on /guides/ was <h2 class="res__h">, and .res__h is a
   13.5px uppercase letter-spaced --ink-faint SECTION LABEL, not a heading.
   Five articles therefore rendered as five tiny faint identical links. A
   worried family could not tell them apart or see what was clickable.
   Cards now, one tab stop each. These gates hold the usability
   properties, not the taste. */
const css = read(path.join(DIST, "styles.css"));
const home = read(path.join(DIST, "index.html"));

/* the label a visitor reads */
check("nav says Care Guides on the index", indexPage.indexOf(">Care Guides<") !== -1);
check("nav says Care Guides on the homepage", home.indexOf(">Care Guides<") !== -1);
SLUGS.forEach(function (s2) {
  check("nav says Care Guides: " + s2, page[s2].indexOf(">Care Guides<") !== -1);
});
check("the bare Guides label is gone everywhere",
  (all + indexPage + home).indexOf(">Guides<") === -1);

/* the heading and the welcome */
check("h1 is the plain question", /<h1[^>]*>Find answers about senior care<\/h1>/.test(indexPage));
check("a welcoming lead invites a choice",
  lc(indexPage).indexOf("pick the question that is on your mind") !== -1);
check("the lead has its own readable style", indexPage.indexOf('class="topics__lead"') !== -1);

/* the cards */
check("cards are a semantic list", /<ul class="topics">[\s\S]*<\/ul>/.test(indexPage));
check("there is one card per guide, no more and no fewer",
  (indexPage.match(/<li class="topic"[\s>]/g) || []).length === SLUGS.length,
  (indexPage.match(/<li class="topic"[\s>]/g) || []).length + " cards for "
    + SLUGS.length + " guides");
check("the old faint-label title style is gone from the index",
  indexPage.indexOf('res__h"><a') === -1);

var cardBlocks = indexPage.split(/<li class="topic"[\s>]/).slice(1);
check("card blocks parsed", cardBlocks.length === SLUGS.length);
cardBlocks.forEach(function (c, i) {
  var n = i + 1;
  check("card " + n + " has a category label", /class="topic__cat">[^<]{3,}</.test(c));
  check("card " + n + " has a linked title", /class="topic__h"><a href="\/guides\/[a-z-]+\/">[^<]{20,}</.test(c));
  check("card " + n + " has a description", /class="topic__p">[^<]{60,}</.test(c));
  check("card " + n + " shows Read article", c.indexOf('class="topic__go">Read article') !== -1);
  check("card " + n + " has an arrow hidden from screen readers",
    c.indexOf('class="topic__arrow" aria-hidden="true">&rarr;') !== -1);
  check("card " + n + " is ONE link, not several",
    (c.split("</li>")[0].match(/<a /g) || []).length === 1,
    String((c.split("</li>")[0].match(/<a /g) || []).length));
  check("card " + n + " title is not shouted",
    !/class="topic__h"><a[^>]*>[A-Z ,'’-]{18,}</.test(c));
});

/* the whole surface is clickable, and focus frames the card */
check("cards are a grid", /\.topics\s*\{[^}]*display:\s*grid/.test(css));
check("card is a positioned surface", /\.topic\s*\{[^}]*position:\s*relative/.test(css));
check("the link is stretched over the whole card",
  /\.topic__h a::after\s*\{[^}]*position:\s*absolute[^}]*inset:\s*0/.test(css));
check("keyboard focus frames the card, not the words",
  /\.topic__h a:focus-visible::after\s*\{[^}]*outline:\s*3px solid/.test(css));
check("the default inner ring is suppressed so there is only one",
  /\.topic__h a:focus-visible\s*\{\s*outline:\s*none/.test(css));

/* comfortable for an older reader */
check("body text stays at 19px", /font-size:\s*19px/.test(css));
check("card description is at least 17px",
  /\.topic__p\s*\{[^}]*font-size:\s*17\.5px/.test(css));
check("card title is a large serif",
  /\.topic__h\s*\{[^}]*Fraunces[\s\S]{0,200}?font-size:\s*clamp\(23px/.test(css));
check("cards have generous padding",
  /\.topic\s*\{[^}]*padding:\s*clamp\(26px/.test(css));
/* CONTRAST - the brand layer redefines --clay and --accent as --sun
   (#e8bb64), which measures 1.79:1 on white. Readable decoration,
   unreadable text. These two gates stop a token rename from turning
   the one call-to-action on the page invisible. */
check("Read article is not painted with the gold token",
  !/\.topic__go\s*\{[^}]*color:\s*var\(--(clay|accent|sun)/.test(css));
check("Read article uses the high-contrast navy",
  /\.topic__go\s*\{[^}]*color:\s*var\(--navy-2/.test(css));
check("the category label uses the high-contrast green",
  /\.topic__cat\s*\{[^}]*color:\s*var\(--sage-deep\)/.test(css));
check("card title is never uppercased",
  !/\.topic__h\s*\{[^}]*text-transform:\s*uppercase/.test(css));

/* responsive and considerate */
check("single column on a phone",
  /@media \(max-width:\s*760px\)\s*\{\s*\.topics\s*\{[^}]*grid-template-columns:\s*1fr/.test(css));
check("desktop columns are balanced and self-fitting",
  /grid-template-columns:\s*repeat\(auto-fit,\s*minmax\(324px/.test(css));
check("motion is optional",
  /@media \(prefers-reduced-motion: reduce\)[\s\S]{0,200}\.topic/.test(css));

/* SEO SURVIVED THE REDESIGN - this is the gate that matters most */
check("index canonical intact",
  indexPage.indexOf('rel="canonical" href="https://evanstonseniorcareguide.com/guides/"') !== -1);
check("index meta description intact", /name="description" content="[^"]{60,}"/.test(indexPage));
check("index JSON-LD is still a CollectionPage", indexPage.indexOf('"CollectionPage"') !== -1);
SLUGS.forEach(function (s2) {
  check("index still links the permanent URL: " + s2,
    indexPage.indexOf('href="/guides/' + s2 + '/"') !== -1);
});
check("no article URL changed",
  SLUGS.every(function (s2) {
    return page[s2].indexOf('href="https://evanstonseniorcareguide.com/guides/' + s2 + '/"') !== -1;
  }));

/* ---- OWNER FINDING 9, 2026-10-19: no way to reach the articles on a phone ----
   styles.css hides every nav link but the CTA below 880px, so a phone
   showed a logo and a Start button. The guides were unreachable from the
   homepage. nav.js + a visible Menu button restore Home / Care Guides /
   Start assessment. Behaviour is proven by check-mobile-nav.py, which
   drives real device metrics - chrome --window-size does NOT give a 375px
   viewport, it clamps to 485. Shape is proven here. */
var navPages = SLUGS.map(function (s2) { return page[s2]; })
  .concat([indexPage, home]);
navPages.forEach(function (h, i) {
  var tag = "page " + (i + 1);
  check("Menu button present: " + tag, h.indexOf('id="navToggle"') !== -1);
  check("Menu button is labelled Menu: " + tag, /id="navToggle"[\s\S]{0,300}?Menu/.test(h));
  check("Menu button declares its state: " + tag,
    /id="navToggle"[\s\S]{0,200}?aria-expanded="false"/.test(h));
  check("Menu button points at its panel: " + tag,
    /aria-controls="navMenu"/.test(h));
  check("panel present and closed by default: " + tag,
    /id="navMenu"[^>]*hidden/.test(h));
  check("panel offers Home: " + tag, /id="navMenu"[\s\S]{0,400}?href="\/">Home</.test(h));
  check("panel offers Care Guides: " + tag,
    /id="navMenu"[\s\S]{0,400}?href="\/guides\/">Care Guides</.test(h));
  check("panel offers Start assessment: " + tag,
    /id="navMenu"[\s\S]{0,500}?href="\/#assessment">Start assessment</.test(h));
  check("nav.js is loaded: " + tag, /src="\/?nav\.js"/.test(h));
  check("decorative bars hidden from screen readers: " + tag,
    h.indexOf('class="nav__toggle-bars" aria-hidden="true"') !== -1);
});
check("nav.js is published", fs.existsSync(path.join(DIST, "nav.js")));
check("nav.js binds the toggle", read(path.join(DIST, "nav.js")).indexOf("navToggle") !== -1);
check("Menu button only appears on small screens",
  /@media \(max-width: 880px\)\s*\{[^}]*\.nav__toggle\s*\{\s*display:\s*inline-flex/.test(css));
check("the panel can never survive into desktop width",
  /@media \(min-width: 881px\)\s*\{\s*\.nav__menu\s*\{\s*display:\s*none\s*!important/.test(css));
check("touch target is at least 44px by construction",
  /\.nav__toggle\s*\{[\s\S]*?padding:\s*14px 18px/.test(css));
check("menu rows are generous",
  /\.nav__menu a\s*\{[\s\S]*?padding:\s*17px 0[\s\S]*?font-size:\s*18px/.test(css));
check("the narrow-width overflow fix is present",
  /@media \(max-width: 480px\)\s*\{\s*\.brand__name\s*\{\s*display:\s*none/.test(css));
check("the brand link keeps an accessible name", /aria-label="Evanston Senior Care Guide, home"/.test(home));

/* ---- OWNER FINDING 10, 2026-10-19: diagrams and photographs ----
   Three diagrams, approved as design, shipped as HTML/CSS rather than
   SVG: a 760-wide SVG scales its own text down with the viewport, so
   five tiles read at 60px on a 375px phone. CSS reflows. Real text is
   also selectable, translatable and read in order by a screen reader.
   Two photographs, licensed, with no identifiable face. */
const slp = page["illinois-supportive-living-program"];
const lev = page["levels-of-senior-care-explained"];

/* each diagram lands on exactly one article, and nowhere else */
check("Medicare diagram is on the Medicare guide", med.indexOf('class="mbar"') !== -1);
check("levels diagram is on the levels guide", lev.indexOf('class="lev"') !== -1);
check("Supportive Living diagram is on its guide", slp.indexOf('class="slp"') !== -1);
check("no diagram leaked into the cost guide",
  page["assisted-living-cost-illinois"].indexOf('class="dia"') === -1);
check("no diagram leaked into the inspection guide",
  page["check-illinois-inspection-records"].indexOf('class="dia"') === -1);
check("exactly one diagram per article that has one",
  (med.match(/class="dia"/g) || []).length === 1 &&
  (lev.match(/class="dia"/g) || []).length === 1 &&
  (slp.match(/class="dia"/g) || []).length === 1);

/* OWNER REQUIREMENT: days 1-20 are $0 COINSURANCE, and the Part A
   deductible may still apply. A bare "$0" told a family the stay was
   free. It is not. */
check("the band says coinsurance, not a bare $0",
  med.indexOf("$0 coinsurance") !== -1);
check("the deductible caveat is stated",
  lc(med).indexOf("is not &ldquo;free&rdquo;") !== -1 ||
  lc(med).indexOf("is not “free”") !== -1 ||
  /\$0 coinsurance[\s\S]{0,900}?deductible of <strong>\$1,736<\/strong> may still apply/.test(flat(med)));
check("the deductible figure is in the diagram",
  /class="dia"[\s\S]*?\$1,736[\s\S]*?<\/figure>/.test(flat(med)));
check("the benefit-period double-charge point survives",
  lc(med).indexOf("you do not pay it twice") !== -1);
check("the diagram still scopes itself to a qualifying stay",
  /class="dia"[\s\S]*?qualifying skilled[\s\S]*?<\/figure>/.test(flat(med)));
check("the diagram repeats that custodial care gets nothing",
  /class="dia"[\s\S]*?pays <strong>nothing at all<\/strong>[\s\S]*?<\/figure>/.test(flat(med)));
check("the coinsurance total is labelled as coinsurance",
  med.indexOf("in coinsurance") !== -1);

/* OWNER REQUIREMENT: alternatives, never a sequence */
check("five options are shown", (lev.match(/class="lev__t"/g) || []).length === 5,
  String((lev.match(/class="lev__t"/g) || []).length));
check("the diagram says not five steps",
  lc(lev).indexOf("five options &mdash; not five steps") !== -1 ||
  lc(lev).indexOf("five options — not five steps") !== -1);
check("the no-order rule is stated outright",
  lc(lev).indexOf("nobody is required to move through them in order") !== -1);
check("the one-level-only case is stated",
  lc(lev).indexOf("may use <strong>one</strong> of these and never another") !== -1);
check("no arrows anywhere in the levels diagram",
  !/class="dia"[\s\S]*?(&rarr;|&#8594;|→|➡)[\s\S]*?<\/figure>/.test(flat(lev)));
["staircase", "next step", "progress to", "move up", "the next level"].forEach(function (b) {
  check("no progression language: " + b, lc(lev).indexOf(b) === -1);
});

/* OWNER REQUIREMENT: no misleading Supportive Living arithmetic */
check("still two charges, not one",
  lc(slp).indexOf("expect two charges, not one") !== -1);
check("both room and board figures are in the diagram",
  /class="slp"[\s\S]*?\$874[\s\S]*?\$625\.50[\s\S]*?<\/figure>/.test(flat(slp)));
check("the diagram shows a method, not a total",
  /class="slp"[\s\S]*?allowable deductions[\s\S]*?<\/figure>/.test(flat(slp)));
check("the diagram prints no invented total",
  flat(slp).indexOf("1,197") === -1 && flat(slp).indexOf("1,166") === -1);
check("the refusal to produce a figure is repeated in the diagram",
  /class="dia"[\s\S]*?no sum on this page that produces your parent[\s\S]*?<\/figure>/.test(flat(slp)));
check("the $120 is stated as kept either way",
  lc(slp).indexOf("keeps the <strong>$120</strong> either way") !== -1);

/* ACCESSIBILITY + WEIGHT */
[["medicare", med], ["levels", lev], ["supportive living", slp]].forEach(function (pair) {
  check("diagram is a labelled figure: " + pair[0],
    /<figure class="dia" aria-labelledby="dia[A-Za-z]+">/.test(pair[1]));
  check("diagram is real text, not an image: " + pair[0],
    !/class="dia"[\s\S]*?<img[\s\S]*?<\/figure>/.test(flat(pair[1])));
});
check("the bar stacks on a phone",
  /@media \(max-width: 620px\)\s*\{[\s\S]*?\.mbar\s*\{\s*flex-direction:\s*column/.test(css));
check("the option grid collapses to one column",
  /@media \(max-width: 620px\)[\s\S]*?\.lev\s*\{\s*grid-template-columns:\s*1fr/.test(css));
check("gold is a band fill only, never diagram text on white",
  !/\.dia__[a-z]+\s*\{[^}]*color:\s*var\(--(sun|clay|accent)\)/.test(css));

/* ---- PHOTOGRAPHY: A STANDARD, NOT A BAN (owner clarified 2026-10-19) ----
   Two photographs were built and rejected - a Lake Michigan shoreline and
   an Evanston park. The rejection was about USEFULNESS, not photography:
   scenery unrelated to an aging-parent decision, carrying a credit line
   that bought nothing. The rule that came out of it:

     a visual earns its place only if it helps a visitor UNDERSTAND
     something, FEEL SUPPORTED, or DECIDE.

   Future imagery of families navigating aging-parent decisions,
   caregiving, or evaluating care options is WELCOME. These gates keep the
   two rejected files out and hold anything new to a standard. They do not
   forbid images. */
check("the rejected shoreline photograph stays out",
  (all + indexPage + home).indexOf("lakeshore-leaf") === -1);
check("the rejected park photograph stays out",
  (all + indexPage + home).indexOf("dawes-lagoon") === -1);
check("neither rejected credit line survives",
  !/(Anthony Ginsbrook|Bohao Zhao)/.test(all + indexPage + home));
check("the rejected image files are not published",
  !fs.existsSync(path.join(DIST, "img", "lakeshore-leaf.jpg")) &&
  !fs.existsSync(path.join(DIST, "img", "dawes-lagoon.jpg")));

/* ANY future image must clear these - they are a standard, not a ban */
const imgs = (all + indexPage + home).match(/<img [^>]*>/g) || [];
imgs.forEach(function (tag, i) {
  if (tag.indexOf("brand__logo") !== -1) { return; }   /* the nav logo is exempt */
  check("image " + i + " carries real alt text", /alt="[^"]{25,}"/.test(tag), tag.slice(0, 90));
  check("image " + i + " declares its dimensions",
    /width="\d+"/.test(tag) && /height="\d+"/.test(tag), tag.slice(0, 90));
  check("image " + i + " loads lazily", /loading="lazy"/.test(tag), tag.slice(0, 90));
});
check("no image claims to show Westminster",
  !/alt="[^"]*Westminster[^"]*"/i.test(all + indexPage + home));
check("no image implies a resident or a testimonial",
  !/alt="[^"]*(resident|testimonial|our client|our customer)[^"]*"/i.test(all + indexPage + home));

/* the diagrams must have survived untouched */
check("Medicare diagram still present", med.indexOf('class="mbar"') !== -1);
check("levels diagram still present", lev.indexOf('class="lev"') !== -1);
check("Supportive Living diagram still present", slp.indexOf('class="slp"') !== -1);
[med, lev, slp].forEach(function (h, i) {
  check("diagram is still text, never an image: " + i,
    !/class="dia"[\s\S]*?<img[\s\S]*?<\/figure>/.test(flat(h)));
});

/* ---- the 3-day rule, stated honestly, inside the diagram itself ---- */
check("the diagram says the 3-day rule is the USUAL case",
  /class="dia"[\s\S]*?<strong>Usually<\/strong>[\s\S]*?<\/figure>/.test(flat(med)));
check("the diagram counts inpatient days, not hospital days",
  /class="dia"[\s\S]*?3 days in a row as an inpatient[\s\S]*?<\/figure>/.test(flat(med)));
check("the diagram excludes the discharge day",
  /class="dia"[\s\S]*?not counting the discharge day[\s\S]*?<\/figure>/.test(flat(med)));
check("the diagram warns that observation hours do not count",
  /class="dia"[\s\S]*?observation or in the emergency room do not count[\s\S]*?<\/figure>/.test(flat(med)));
check("the diagram states the rule is not absolute",
  /class="dia"[\s\S]*?3-day rule is not absolute[\s\S]*?<\/figure>/.test(flat(med)));
check("the diagram names the ACO waiver",
  /class="dia"[\s\S]*?Skilled Nursing Facility 3-Day Rule Waiver[\s\S]*?<\/figure>/.test(flat(med)));
check("the diagram names the Medicare Advantage waiver",
  /class="dia"[\s\S]*?Medicare Advantage plans waive it[\s\S]*?<\/figure>/.test(flat(med)));
check("the diagram never states the rule as unconditional",
  !/class="dia"[\s\S]*?after a 3-day inpatient admission, with daily[\s\S]*?<\/figure>/.test(flat(med)));

check("nothing autoplays and no video was added",
  !/<video|autoplay|<iframe/i.test(all + indexPage + home));

/* ---------------- LINKS + SITEMAP ---------------- */
const internal = (all + indexPage).match(/href="(\/[^"#]*)"/g) || [];
const bad = [];
internal.forEach((h) => {
  const u = h.slice(6, -1);
  if (u === "/") return;
  const f = u.endsWith("/") ? path.join(DIST, u, "index.html") : path.join(DIST, u);
  if (!fs.existsSync(f)) bad.push(u);
});
check("no broken internal links", bad.length === 0, bad.join(", "));
SLUGS.forEach((s) => {
  check("sitemap lists " + s, sitemap.indexOf("/guides/" + s + "/") !== -1);
});
/* home + /guides/ + one per guide + /privacy.html */
/* ---- OWNER FINDING 5, 2026-10-23: a ceiling is not an entitlement ----
   The first cloud-written draft said the CSRA was the maximum transferable
   "before the resident's own eligibility is assessed". HFS says no such
   thing. What HFS does say is that the ACTUAL amount is the standard MINUS
   what the at-home spouse already holds - so a reader who treats $143,172
   or $4,066.50 as an amount they will receive is reading a ceiling as a
   promise, and plans a parent's finances around it. */
const mcd = page["illinois-medicaid-long-term-care"];
check("the unsupported eligibility-sequencing phrase is gone",
  all.indexOf("before the resident's own eligibility is") === -1 &&
  all.indexOf("before the resident&rsquo;s own eligibility is") === -1);
check("both spousal figures are labelled standards, not entitlements",
  /neither figure is an amount anyone is promised/i.test(flat(mcd)) &&
  lc(mcd).indexOf("both are ceilings") !== -1);
check("the CSRA deduction rule is quoted from HFS",
  lc(mcd).indexOf("deducting nonexempt resources of the community spouse "
    + "from the standard") !== -1);
check("the CSMNA deduction rule is quoted from HFS",
  lc(mcd).indexOf("deducting any gross income of the community spouse "
    + "from the standard") !== -1);
check("the guide refuses to do the spousal subtraction itself",
  lc(mcd).indexOf("does not do that subtraction for you") !== -1);
check("the personal needs allowance is still refused",
  lc(mcd).indexOf("could not read a verifiable number") !== -1);

/* ---- OWNER FINDING 6, 2026-10-23: a review date is a factual claim ----
   REVIEWED used to be one global constant stamped onto every page. Adding a
   guide researched today would have re-dated six pages nobody re-checked.
   Dates are per-guide now; this gate proves they did not collapse back into
   one. */
const dates = SLUGS.map((s) =>
  (page[s].match(/Last reviewed ([0-9]+ [A-Za-z]+ [0-9]{4})\./) || [])[1]);
check("every guide prints a review date", dates.every(Boolean), String(dates));
check("review dates are per-guide, not one global stamp",
  new Set(dates).size > 1, dates.join(" | "));
check("the Medicaid guide is dated the day it was researched",
  dates[SLUGS.indexOf("illinois-medicaid-long-term-care")] === "23 October 2026",
  String(dates[SLUGS.indexOf("illinois-medicaid-long-term-care")]));
check("its JSON-LD dateModified agrees with its printed date",
  mcd.indexOf('"dateModified": "2026-10-23"') !== -1);
check("the original five keep their own 2026-10-18 date",
  dates[SLUGS.indexOf("assisted-living-cost-illinois")] === "18 October 2026",
  String(dates[SLUGS.indexOf("assisted-living-cost-illinois")]));

/* ---- OWNER RULE, 2026-10-23: the assessment is the conversion goal ----
   Every guide exists to answer a question honestly AND to put the
   six-question assessment in front of someone who now realises they do not
   know which level of care applies. A guide that teaches and then dead-ends
   is a leak. The daily routine writes guides unsupervised, so this is a gate
   rather than a note in a file: a new guide cannot reach the owner without
   the assessment block on it. */
SLUGS.forEach((s) => {
  const h = page[s];
  check("assessment CTA block present: " + s,
    h.indexOf('class="res__block plan plan--primary"') !== -1);
  check("assessment CTA is a real link: " + s,
    /<a class="btn btn--primary" href="\/#assessment">Take the free\s+assessment<\/a>/.test(flat(h)));
  check("assessment promise is repeated at the CTA: " + s,
    lc(h).indexOf("no name, no email and no phone number") !== -1);
});

/* ---- OWNER RULE, 2026-10-24: the article must bridge to the assessment ----
   Measured before this change: the first mention of the assessment sat in
   section 6 of 7, 7 of 8 and 8 of 9 across the library. A reader whose
   question was answered in section 2 left having never seen it. Every guide
   now carries ONE bridge after the first section, and the generator refuses
   to build a guide without one - so these gates check the shape and the
   restraint, not whether somebody remembered. */
SLUGS.forEach((s) => {
  const h = page[s];
  const f = flat(h);

  check("has exactly one mid-article bridge: " + s,
    (h.match(/<aside class="bridge">/g) || []).length === 1,
    String((h.match(/<aside class="bridge">/g) || []).length));

  /* It must come BEFORE the sources block, i.e. inside the article, not
     bolted on at the end next to the CTA that already exists. */
  const iBridge = h.indexOf('<aside class="bridge">');
  const iSources = h.indexOf('<h2 class="res__h">Sources</h2>');
  const iCta = h.indexOf('class="res__block plan plan--primary"');
  check("bridge sits inside the article, above Sources: " + s,
    iBridge > 0 && iBridge < iSources, iBridge + " vs " + iSources);
  check("bridge comes before the final CTA: " + s,
    iBridge > 0 && iCta > 0 && iBridge < iCta);

  /* A link, never a second button. Two buttons reads as a sales page. */
  const bridgeHtml = h.slice(iBridge, h.indexOf("</aside>", iBridge));
  check("bridge offers a link, not a button: " + s,
    bridgeHtml.indexOf('class="btn') === -1 && /<a href="\/#assessment">/.test(bridgeHtml));
  check("bridge links to the assessment exactly once: " + s,
    (bridgeHtml.match(/href="\/#assessment"/g) || []).length === 1);

  /* The promise must be identical everywhere it appears. */
  check("bridge repeats the full privacy promise: " + s,
    lc(bridgeHtml).indexOf("no name, no email and no phone number") !== -1 &&
    lc(bridgeHtml).indexOf("never leave your device") !== -1);
  check("bridge says it is not a diagnosis: " + s,
    lc(bridgeHtml).indexOf("not a diagnosis") !== -1);
  check("bridge states the time cost: " + s,
    lc(bridgeHtml).indexOf("about two minutes") !== -1);

  /* Each bridge must be written for ITS topic, not pasted. */
  const lead = (bridgeHtml.match(/<p class="bridge__p">([\s\S]*?)<\/p>/) || [])[1] || "";
  check("bridge has its own opening sentence: " + s, lead.trim().length >= 40,
    String(lead.trim().length));

  /* EXACTLY two routes to the assessment inside the article: the bridge
     and the final CTA. Fewer means a reader can finish without a next step;
     more is a repeated sales pitch. The site nav carries its own "Start
     assessment" link in both the desktop bar and the mobile menu - those are
     navigation, not persuasion, so the count is scoped to the article. */
  const aStart = h.indexOf("<h1");
  const aEnd = h.indexOf("<footer") === -1 ? h.length : h.indexOf("<footer");
  const inArticle = (h.slice(aStart, aEnd).match(/href="\/#assessment"/g) || []).length;
  check("exactly two assessment links in the article: " + s, inArticle === 2,
    String(inArticle));

  check("no sticky or popup CTA: " + s,
    !/position:\s*(fixed|sticky)/i.test(h) && h.indexOf("<dialog") === -1 &&
    lc(h).indexOf("modal") === -1);
});

/* Every bridge opening must be unique across the library. */
const leads = SLUGS.map((s) => {
  const h = page[s];
  const i = h.indexOf('<aside class="bridge">');
  return ((h.slice(i).match(/<p class="bridge__p">([\s\S]*?)<\/p>/) || [])[1] || "").trim();
});
check("every bridge is written for its own topic",
  new Set(leads).size === SLUGS.length,
  new Set(leads).size + " unique of " + SLUGS.length);

/* No manufactured urgency, anywhere on any page. */
[/\bact now\b/i, /\bdon'?t miss\b/i, /\blimited time\b/i, /\bhurry\b/i,
 /\bonly \d+ (spots?|places?|left)\b/i, /\bbefore it'?s too late\b/i,
 /\bspaces? (are )?filling\b/i, /\burgent(ly)?\b/i,
 /\bdon'?t wait\b/i, /\brisk (losing|missing)\b/i].forEach((re, i) => {
  check("no manufactured urgency, pattern " + (i + 1),
    !re.test(all + indexPage), String(re));
});

/* ---- ASSET DRIFT, 2026-10-24 ----
   styles.css, app.js, assessment.js and nav.js each exist at the repo root
   AND in _dist. Netlify publishes _dist, so a root-only edit reaches nobody.
   They drifted 43 lines the first time a rule was added. build-guides.py now
   copies them; this proves the copy actually happened. */
["styles.css", "app.js", "assessment.js", "nav.js"].forEach((a) => {
  const root = path.join(__dirname, a), dist = path.join(DIST, a);
  const both = fs.existsSync(root) && fs.existsSync(dist);
  check("published copy matches source: " + a,
    both && read(root) === read(dist));
});

/* ---- THE LIBRARY MUST SURVIVE WITHOUT JAVASCRIPT, 2026-10-25 ----
   Search, chips and Show more are enhancements layered over server-rendered
   cards. The failure mode worth guarding is a future change that renders the
   list from JS: the page would still look right in a browser and vanish from
   Google. These gates read the shipped HTML, which is exactly what a crawler
   sees with scripting off. */
check("every guide is a card in the static HTML",
  (indexPage.match(/<li class="topic"[\s>]/g) || []).length === SLUGS.length,
  String((indexPage.match(/<li class="topic"[\s>]/g) || []).length));
SLUGS.forEach((s) => {
  check("crawlable link present without JS: " + s,
    indexPage.indexOf('href="/guides/' + s + '/"') !== -1);
});
check("no card is hidden in the shipped HTML",
  indexPage.indexOf('<li class="topic" hidden') === -1 &&
  !/<li class="topic"[^>]*\shidden/.test(indexPage));

/* The toolbar ships hidden and JS reveals it, so a no-JS visitor never sees
   a search box that cannot search or a chip that cannot filter. */
check("toolbar ships hidden for the no-JS case",
  /<div class="lib" id="libTools" hidden>/.test(indexPage));
check("Show more ships hidden",
  /id="libMore" hidden/.test(indexPage));

/* Search terms and categories are generated, never hand-written. */
SLUGS.forEach((s) => {
  const card = (indexPage.split(/<li class="topic"[\s>]/)[
    SLUGS.indexOf(s) + 1] || "");
  check("card carries a category: " + s, /data-cat="[^"]{3,}"/.test(card));
  check("card carries search terms: " + s, /data-terms="[^"]{30,}"/.test(card));
});

/* Chips are derived from the categories actually in use, so an empty chip -
   a dead end for the visitor - can never render. */
const chipCats = (indexPage.match(/class="chip" data-cat="([^"]+)"/g) || [])
  .map((m) => m.replace(/.*data-cat="/, "").replace(/"$/, ""));
const cardCats = (indexPage.match(/<li class="topic" data-cat="([^"]+)"/g) || [])
  .map((m) => m.replace(/.*data-cat="/, "").replace(/"$/, ""));
check("every chip has at least one guide behind it",
  chipCats.every((c) => cardCats.indexOf(c) !== -1), chipCats.join(" | "));
check("every category in use has a chip",
  cardCats.every((c) => chipCats.indexOf(c) !== -1), cardCats.join(" | "));
check("there is an All chip", /class="chip chip--on" data-cat=""/.test(indexPage));
check("chip counts are rendered", /class="chip__n"/.test(indexPage));

/* The library keeps the assessment, placed after the guides rather than
   above them - a reference page that leads with a call to action reads as a
   landing page. */
check("library carries the assessment block",
  indexPage.indexOf('class="res__block plan plan--primary"') !== -1);
check("assessment sits AFTER the guides, not above them",
  indexPage.indexOf('class="res__block plan plan--primary"') >
    indexPage.lastIndexOf('<li class="topic"'));
check("library assessment repeats the privacy promise",
  lc(indexPage).indexOf("no name, no email and no phone number") !== -1);
check("library has no second call to action",
  (indexPage.match(/href="\/#assessment"/g) || []).length <= 3,
  String((indexPage.match(/href="\/#assessment"/g) || []).length));

check("guides.js is loaded on the library page",
  indexPage.indexOf('src="/guides.js"') !== -1);
check("no animation library or inline keyframes crept in",
  !/@keyframes|animation:/i.test(indexPage));

/* ---- INDEXNOW, 2026-10-25 ----
   The key file is PUBLIC by design: IndexNow proves ownership by fetching
   https://<host>/<key>.txt. It is NOT the Bing Webmaster API key, which
   authenticates an account and must never appear in this repository.
   These gates protect the three ways this quietly breaks: the file drops
   out of the build, the key drifts from the constant, or someone pastes a
   real secret in next to it. */
const GEN_KEY = (GEN.match(/^INDEXNOW_KEY = "([0-9a-f]{8,128})"/m) || [])[1];
check("generator defines an IndexNow key", !!GEN_KEY, String(GEN_KEY));
const KEYFILE = path.join(DIST, GEN_KEY + ".txt");
check("key file is in the publish directory", fs.existsSync(KEYFILE));
check("key file contains exactly the key",
  fs.existsSync(KEYFILE) && read(KEYFILE).trim() === GEN_KEY);
check("key file holds nothing but the key",
  fs.existsSync(KEYFILE) && read(KEYFILE).trim().length === GEN_KEY.length);
check("no second key-like file shipped",
  fs.readdirSync(DIST).filter((f) => /^[0-9a-f]{16,}\.txt$/.test(f)).length === 1,
  fs.readdirSync(DIST).filter((f) => /^[0-9a-f]{16,}\.txt$/.test(f)).join(" "));

/* The publisher must target Evanston explicitly and must never carry the
   other site's id as a deploy target. An unflagged netlify deploy from this
   directory resolves to norvenph.com. */
const PUB = path.join(__dirname, "tools", "publish.py");
check("publisher exists", fs.existsSync(PUB));
if (fs.existsSync(PUB)) {
  const p = read(PUB);
  check("publisher hardcodes the Evanston site id",
    p.indexOf('SITE_ID = "e25a95a5-7a87-4d1c-bae7-8c35d496dded"') !== -1);
  /* The deploy command is assembled from concatenated Python string
     literals, so collapse quotes and whitespace before looking for the
     flag. A gate that fails on formatting is a gate nobody trusts. */
  var flatP = p.replace(/["']/g, "").replace(/\s+/g, " ");
  check("publisher passes --site on every deploy",
    /netlify deploy.{0,200}--site %s/.test(flatP),
    (flatP.match(/netlify deploy.{0,120}/) || [""])[0]);
  check("publisher asserts the site NAME before uploading",
    p.indexOf('site.get("name") != SITE_NAME') !== -1);
  check("publisher never deploys to the other site",
    !/deploy[^\n]*OTHER_SITE_ID/.test(p));
  check("publisher verifies URLs are live before submitting",
    p.indexOf("no changed URL returned 200") !== -1);
  check("publisher handles 202 as success",
    /status in \(200, 202\)/.test(p));
  check("publisher does not record a failed submission",
    p.indexOf("Ledger NOT updated") !== -1);
  check("publisher reads the key from the generator, not a copy",
    p.indexOf("_key_from_generator") !== -1 &&
    p.indexOf('"f7fdf3f8') === -1);
}

check("sitemap has one url per page",
  (sitemap.match(/<url>/g) || []).length === SLUGS.length + 3,
  (sitemap.match(/<url>/g) || []).length + " urls for "
    + SLUGS.length + " guides");
check("guides index links every guide",
  SLUGS.every((s) => indexPage.indexOf("/guides/" + s + "/") !== -1));
check("Guides is in the main nav",
  read(path.join(DIST, "index.html")).indexOf("/guides/") !== -1);

/* ---------------- QUALITY ---------------- */
const descs = SLUGS.map((s) => (page[s].match(/name="description" content="([^"]+)"/) || [])[1]);
check("all descriptions unique", new Set(descs).size === SLUGS.length);
const titles = SLUGS.map((s) => (page[s].match(/<title>([^<]+)<\/title>/) || [])[1]);
check("all titles unique", new Set(titles).size === SLUGS.length);
SLUGS.forEach((s) => {
  const words = page[s].replace(/<[^>]+>/g, " ").split(/\s+/).filter(Boolean).length;
  check("substantial body: " + s, words > 400, words + " words");
});
check("no control bytes", !/[\x00-\x08\x0b\x0c\x0e-\x1f]/.test(all));

console.log("\n  " + pass + " passed, " + fail + " failed   (" + (pass + fail) + " checks)");
process.exit(fail === 0 ? 0 : 1);
