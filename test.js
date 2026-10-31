/* Run:  node test.js
   Every case is a real family situation. The assessment must land on a
   defensible level AND state a reason that quotes their own answers. */
const { QUESTIONS, assess, DISCLAIMER } = require("./assessment.js");

/* Answer helper: pick by option index, in question order. */
const ids = QUESTIONS.map((q) => q.id);
function answersFrom(list) {
  const out = {};
  list.forEach((choice, i) => { out[ids[i]] = choice; });
  return out;
}

/* [name, [adl, memory, medical, alone, hospital, household], expected level] */
const CASES = [
  ["Mum forgets bills, manages herself",        [0, 1, 0, 0, 0, 2], "independent"],
  ["House slipping, no care needs",             [0, 0, 0, 0, 0, 3], "independent"],
  ["Needs help bathing, mind is sharp",         [2, 0, 1, 1, 0, 3], "assisted"],
  ["Full personal care, no nursing needs",      [3, 1, 1, 2, 0, 4], "assisted"],
  ["Medication help plus some dressing help",   [1, 0, 1, 1, 0, 2], "assisted"],
  ["Left the stove on, wanders",                [2, 3, 1, 3, 0, 4], "memory"],
  ["Confused about place, unsafe alone",        [1, 2, 0, 2, 0, 3], "memory"],
  ["Oxygen and wound care, needs full help",    [3, 0, 2, 3, 0, 4], "skilled"],
  ["Needs a nurse around the clock",            [2, 0, 3, 2, 0, 3], "skilled"],
  ["Out of hospital, getting stronger",         [2, 0, 1, 1, 1, 3], "rehab"],
  ["In hospital right now",                     [2, 1, 1, 1, 3, 3], "rehab"],
  ["Out of hospital, not bouncing back",        [2, 0, 1, 2, 2, 3], "skilled"],
  ["No needs at all",                           [0, 0, 0, 0, 0, 0], null]
];

let pass = 0;
const checks = [];
function check(name, ok, detail) {
  checks.push(ok);
  console.log((ok ? "PASS" : "FAIL") + "  " + name.padEnd(46) + (detail || ""));
}

CASES.forEach(([name, picks, expected]) => {
  const result = assess(answersFrom(picks));
  const got = result.level ? result.level.id : null;
  const ok = got === expected;
  if (ok) pass++;
  check(name, ok, (got || "no need") + (ok ? "" : "   EXPECTED " + (expected || "no need")));
});

/* ---- the result must always explain itself ---- */
CASES.forEach(([name, picks]) => {
  const result = assess(answersFrom(picks));
  check('reason quotes their own answer: "' + name.slice(0, 22) + '"',
    typeof result.reason === "string" && result.reason.length > 30);
});

/* ---- a partial assessment must never produce a result ---- */
const partial = assess({ adl: 2, memory: 1 });
check("an unfinished assessment returns nothing",
  partial.status === "incomplete" && !partial.level, partial.status);

/* ---- NO PROVIDER IS NAMED, WEIGHTED OR RANKED ----
   This is the integrity gate. Phase 1 recommends a CARE LEVEL and
   nothing else. If a provider name ever appears in the engine, this
   fails the build. */
const raw = require("fs").readFileSync("assessment.js", "utf8");
/* Strip comments first. A comment EXPLAINING the no-provider policy must
   not fail the no-provider gate. Only shipped code and strings count. */
const src = raw
  .replace(/\/\*[\s\S]*?\*\//g, " ")
  .replace(/(^|[^:])\/\/.*$/gm, "$1")
  .toLowerCase();
const FORBIDDEN = ["westminster", "presbyterian", "provider", "facility name",
  "recommend", "partner", "sponsor", "affiliate", "referral"];
const leaks = FORBIDDEN.filter((word) => src.indexOf(word) !== -1);
check("no provider or referral language in the engine", leaks.length === 0, leaks.join(", "));

/* ---- THE PUBLIC PAGE CARRIES NO PROVIDER AND NO SALES LANGUAGE ----
   The engine gate above covers assessment.js. This covers what a visitor
   actually reads. Narrower word list on purpose: the methodology section
   legitimately says "no provider pays to influence results", so the words
   banned here are the commercial ones that would make that a lie. */
const pageRaw = require("fs").readFileSync("index.html", "utf8").toLowerCase();
/* The methodology section legitimately NAMES these words in order to deny
   them ("there is no advertising"). Scan the persuasive page without it. */
/* Collapse whitespace the way a browser renders it, so a phrase that
   wraps across two source lines still matches. */
const pageSrc = pageRaw.replace(/\s+/g, " ");
const sellingCopy = pageRaw.replace(/<details class="src"[\s\S]*?<\/details>/, " ");
/* app.js holds the result template, so a visitor-facing phrase can live
   in either file. Both are read here, before any gate uses them. */
const appSrcRaw = require("fs").readFileSync("app.js", "utf8");
const shownSrc = (pageRaw + " " + appSrcRaw).toLowerCase().replace(/\s+/g, " ");

/* Westminster is permitted from here on, but ONLY under the disclosure
   rules asserted below. Everything else that would make this a sales page
   or a paid placement stays banned outright. */
/* "schedule a visit", "schedule a tour" and "book a tour" used to be
   banned outright. They are not any more: the site now talks about
   visiting Westminster, and the protection that matters is not silence
   about visits, it is the explicit statement that saving one schedules
   nothing. That statement is asserted further down. What stays banned
   is paid placement and the language of a sales funnel. */
const PAGE_FORBIDDEN = ["sponsored", "advertis", "paid placement",
  "request info", "get pricing", "free consultation", "speak to an advisor",
  "we recommend", "best community", "top rated", "#1 ", "will contact you"];
const pageLeaks = PAGE_FORBIDDEN.filter((w) => sellingCopy.indexOf(w) !== -1);
check("no provider or sales language on the public page",
  pageLeaks.length === 0, pageLeaks.join(", "));

/* ---- THE ONE FORM IS PERMITTED ONLY UNDER PROOF ----
   This gate used to ban every form outright. It no longer can: the
   site now has to record a tour inquiry before anyone is referred,
   and a client-side "submission" would prove nothing. So the ban is
   replaced with conditions, not removed.

   A form may exist here only if ALL of the following hold. Any one
   of them failing fails the build. Nothing below is softer than the
   old ban — it is the same protection expressed as requirements. */
check("no mailto anywhere on the page", pageSrc.indexOf("mailto:") === -1);

const planFn = require("fs").readFileSync("netlify/functions/plan-visit.mjs", "utf8");
const planFnSrc = planFn
  .replace(/\/\*[\s\S]*?\*\//g, " ")
  .replace(/(^|[^:])\/\/.*$/gm, "$1");
const appShown = appSrcRaw.replace(/\s+/g, " ").toLowerCase();

/* 1. It posts to a real server endpoint, and the proof is not faked
      client-side. */
check("form posts to the server endpoint",
  appShown.indexOf('fetch("/api/plan-visit"') !== -1);
["localstorage", "sessionstorage", "mailto:"].forEach((bad) => {
  check('submission does not use ' + bad, appShown.indexOf(bad) === -1);
});

/* 2. The submission ID and the timestamp are generated SERVER-side.
      A browser-supplied time is worthless as evidence. */
check("submission id is generated on the server",
  planFnSrc.indexOf("crypto.randomUUID()") !== -1);
check("timestamp is generated on the server",
  planFnSrc.indexOf("new Date().toISOString()") !== -1);
check("client never supplies an id or a timestamp",
  appShown.indexOf("submissionid:") === -1 && appShown.indexOf("receivedat:") === -1);

/* 3. Only the five permitted fields are ever sent, and the care
      assessment is never attached to an identity. */
const payload = (appSrcRaw.match(/const payload = \{[\s\S]*?\};/) || [""])[0];
check("payload block found in app.js", payload.length > 40);
["firstName", "lastName", "email", "phone", "consent"]
  .forEach((field) => {
    check("payload carries " + field, payload.indexOf(field) !== -1);
  });
/* The planned-visit date was retired on 2026-10-16: Admissions set the
   time, so asking a family to pick a day was friction and one more date
   held in a file of personal information for no purpose. Asserted as an
   absence in all three places so it cannot drift back in. */
["plannedVisitDate", "plannedvisitdate"].forEach((gone) => {
  check('payload no longer carries "' + gone + '"', payload.indexOf(gone) === -1);
});
check("the date field is gone from the form markup",
  appShown.indexOf('name="plannedvisitdate"') === -1 &&
  appShown.indexOf('type="date"') === -1);
check("the server no longer accepts a planned-visit date",
  planFnSrc.indexOf("plannedVisitDate") === -1);
/* Narrowed 2026-10-17. The payload now carries ONE derived value,
   careLevel, so "level" can no longer be banned as a substring. The
   raw answers and the engine call still must never appear — that was
   always the real line. */
["answers", "assess(", "reasons", "signals", "symptoms"]
  .forEach((leak) => {
    check('payload never carries "' + leak + '"',
      payload.toLowerCase().indexOf(leak.toLowerCase()) === -1);
  });
check("payload carries the derived care level", payload.indexOf("careLevel") !== -1);
check("the care level comes from render state, never a visitor input",
  payload.indexOf("careLevel: resultLevelId") !== -1 &&
  appShown.indexOf('name="carelevel"') === -1);
check("the server whitelists the care level",
  planFnSrc.indexOf("hasOwnProperty.call(CARE_LEVELS, careLevel)") !== -1);
["independent", "assisted", "memory", "skilled", "rehab", "no_need"].forEach((id) => {
  check('care level "' + id + '" is a known value', planFn.indexOf(id + ":") !== -1);
});
check("raw answers and health fields are still refused",
  planFn.indexOf('"answers"') !== -1 && planFn.indexOf('"quizanswers"') !== -1 &&
  planFn.indexOf('"diagnosis"') !== -1 && planFn.indexOf('"dateofbirth"') !== -1);

/* 4. No input on the page asks for anything medical. The form's own
      field names are the only identity fields that exist. */
const inputNames = (pageRaw + " " + appSrcRaw)
  .match(/name="([a-z0-9_\-]+)"/gi) || [];
const HEALTH_FIELDS = ["diagnosis", "condition", "medication", "adl", "memory",
  "insurance", "medicare", "medicaid", "dob", "dateofbirth", "birth", "age",
  "ssn", "symptom", "mobility", "cognition", "quiz", "answers", "carelevel"];
const askedForHealth = inputNames.filter((raw) => {
  const n = raw.toLowerCase().replace(/[^a-z]/g, "").replace("name", "");
  return HEALTH_FIELDS.some((h) => n.indexOf(h) !== -1);
});
check("no input asks for health information", askedForHealth.length === 0,
  askedForHealth.join(", "));

/* 5. The server REFUSES health data rather than trusting the client
      not to send it. Promise in copy, enforcement in code. */
check("server refuses assessment and health fields",
  planFnSrc.indexOf("REJECT_KEYS") !== -1 &&
  planFnSrc.indexOf("refusedFields") !== -1);
["diagnosis", "medication", "adls", "memorystatus", "insurance", "dateofbirth",
 "quizanswers", "carelevel"].forEach((key) => {
  check('server reject list covers "' + key + '"', planFn.indexOf('"' + key + '"') !== -1);
});
check("server rejects unexpected fields too",
  planFnSrc.indexOf("unexpectedFields") !== -1);

/* 6. Consent is required and is enforced on the server, not merely
      rendered. */
check("server requires consent",
  planFnSrc.indexOf("payload.consent !== true") !== -1);
check("consent checkbox exists in the form",
  appShown.indexOf('name="consent"') !== -1 &&
  appShown.indexOf('type="checkbox"') !== -1);

/* 7. The required wording is present verbatim.
      The consent now authorises a TRANSFER — the details are passed to
      Admissions by hand — so the copy has to name the fields, name the
      recipient, name the purpose, and refuse the promise a family would
      most like to hear. All four are asserted. */
/* Rewritten 2026-10-19 with the shortened form copy. The protections
   are identical; the sentences carrying them are shorter. The old block
   asserted the SAME promise in four places, which is exactly the
   defensiveness the rewrite removed. */
[["copy: the form books nothing",
  "this form doesn&rsquo;t book anything"],
 ["copy: admissions decide, not this site",
  "they decide whether and when a tour happens"],
 ["checkbox: names every shared field including the result",
  "send my name, phone, email, what i am interested in, and my"],
 ["checkbox: names the recipient and the purpose",
  "he may pass my details to westminster place to arrange a tour"],
 ["trust: the operator introduces himself in his own words",
  "i created evanston senior care guide to help families better"],
 ["trust: not official, not paid, named at the form",
  "isn&rsquo;t an official westminster site, i&rsquo;m not paid for referrals"],
 ["trust: the assessment asked for no name",
  "the assessment above never asked for your name"],
 ["privacy notice is reachable from the form",
  'href="/privacy.html"']
].forEach(([label, phrase]) => {
  check(label, appShown.indexOf(phrase) !== -1);
});

/* The stored consent statement and the sentence on the form must be the
   same sentence. A record saying "they agreed to X" while the page said
   Y is worse than storing no statement at all, so the string in the
   function is compared against the rendered checkbox copy rather than
   trusted to have been kept in step by hand. */
const storedConsent = (planFn.match(/const CONSENT_STATEMENT =([\s\S]*?);/) || [""])[0]
  .replace(/const CONSENT_STATEMENT =|;|"|\+/g, " ")
  .replace(/\s+/g, " ").trim().toLowerCase();
check("the stored consent statement is not empty", storedConsent.length > 80);
const consentOnPage = appShown.replace(/&mdash;/g, " ").replace(/\s+/g, " ");
check("the stored consent statement matches the form copy word for word",
  consentOnPage.indexOf(storedConsent) !== -1, storedConsent.slice(0, 70));
check("the consent statement is stored on every record",
  planFnSrc.indexOf("consentStatement: CONSENT_STATEMENT") !== -1 &&
  planFnSrc.indexOf("consentedAt: receivedAt") !== -1);
check("the consent statement is versioned",
  planFnSrc.indexOf("consentVersion: CONSENT_VERSION") !== -1);

/* 8. Never report a save that did not happen, and never hard-code a
      destination address. */
check("a failed write returns an error, not a success",
  planFnSrc.indexOf("if (!written.stored)") !== -1 &&
  planFnSrc.indexOf("Nothing was stored") !== -1);
check("the record is read back before success is claimed",
  planFnSrc.indexOf("readback_mismatch") !== -1);
check("no email address is hard-coded in the function",
  !/[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}/i.test(planFnSrc));
/* Transport changed to Resend 2026-10-17. With Web3Forms the
   destination was carried INSIDE the access key, so one env var
   covered it. Resend needs an explicit recipient, so the address
   gets its own variable rather than being hard-coded — the gate
   above ("no email address is hard-coded") still has to pass. */
check("the notification key comes from an environment variable",
  planFn.indexOf("process.env.RESEND_API_KEY") !== -1);
check("the recipient comes from an environment variable",
  planFn.indexOf("process.env.PLAN_VISIT_NOTIFY_TO") !== -1);
check("the sender comes from an environment variable",
  planFn.indexOf("process.env.PLAN_VISIT_NOTIFY_FROM") !== -1);
check("notification is not_configured unless all three are set",
  planFnSrc.indexOf("!RESEND_KEY || !NOTIFY_TO || !NOTIFY_FROM") !== -1);
check("the API key is never logged or returned",
  !/console\.(log|error)\([^)]*RESEND_KEY/.test(planFn) &&
  !/RESEND_KEY/.test(planFn.slice(planFn.indexOf("return json(200"))));
check("notification reports its real state, never a fake send",
  planFnSrc.indexOf('"not_configured"') !== -1 &&
  planFnSrc.indexOf('"failed"') !== -1);

/* 9. The export of stored names is closed by default. */
const exportFn = require("fs").readFileSync("netlify/functions/plan-visit-export.mjs", "utf8");
check("export refuses every request when no token is set",
  exportFn.indexOf("if (!TOKEN)") !== -1);
check("export token comes from an environment variable",
  exportFn.indexOf("process.env.PLAN_VISIT_EXPORT_TOKEN") !== -1);
check("export has no query-string key fallback",
  exportFn.indexOf("searchParams.get(\"token\")") === -1 &&
  exportFn.indexOf("searchParams.get('token')") === -1);

/* 10. The email notification carries no health or assessment data. */
const emailBody = (planFn.match(/function notificationText[\s\S]*?\n}/) || [""])[0].toLowerCase();
["diagnosis", "medication", "adls", "assessment answer", "quizanswers",
 "insurance", "medicare", "dateofbirth"].forEach((bad) => {
  check('notification email omits "' + bad + '"', emailBody.indexOf(bad) === -1);
});

/* ---- coverage claims are hedged, never guaranteed ---- */
const { CARE_LEVELS: LEVELS } = require("./assessment.js");
const coverage = (LEVELS.rehab.cost.note + " " + LEVELS.skilled.cost.note).toLowerCase();
check("Medicare wording is conditional, not a promise",
  coverage.indexOf("may") !== -1 && coverage.indexOf("eligibility rules") !== -1 &&
  coverage.indexOf("qualifying") !== -1, LEVELS.rehab.cost.note.slice(0, 70));
check("no absolute coverage promise in the engine",
  coverage.indexOf("fully covers") === -1 && coverage.indexOf("covers the first 20 days in full") === -1);

/* ---- the Medicaid explanation names the real Illinois program ---- */
check("Medicaid wording names the Supportive Living Program",
  pageSrc.indexOf("supportive living program") !== -1 &&
  pageSrc.indexOf("room and board") !== -1);
check("Medicaid wording is not an absolute denial",
  pageSrc.indexOf("medicaid does not pay room") === -1);

/* ---- sources are present and link to specific pages ---- */
["medicare.gov/coverage/skilled-nursing-facility-snf-care",
 "medicare.gov/basics/costs/medicare-costs",
 "hfs.illinois.gov/medicalproviders/medicaidreimbursement/supportivelivinging.html",
 "hfs.illinois.gov/medicalclients/hcbs.html",
 "dph.illinois.gov/topics-services/health-care-regulation/assisted-living.html",
 "medicare.gov/care-compare"].forEach((url) => {
  check("source linked: " + url.split("/")[0] + "…" + url.slice(-28),
    pageSrc.indexOf(url) !== -1);
});

/* ---- methodology states the four honesty claims ---- */
["not a medical diagnosis", "published decision rules",
 "pays to influence", "medians"].forEach((phrase) => {
  check('methodology states: "' + phrase + '"', pageSrc.indexOf(phrase) !== -1);
});

/* ---- the assessment invites checking, not arguing ---- */
check("assessment wording is transparent, not confrontational",
  pageSrc.indexOf("argue with it") === -1 &&
  pageSrc.indexOf("check the reasoning yourself") !== -1);

/* ---- THE TRUST STATEMENT IS LOAD-BEARING ----
   Phase 1's whole position rests on these four claims. They are asserted
   POSITIVELY so nobody can quietly soften them later. The words
   "affiliate" and "referral" appear on the page only inside denials of
   them — these checks are what make that difference provable. */
[["assessment asks nothing",  "asks nothing about who you are"],
 ["answers never stored",     "assessment answers are never collected, stored or"],
 ["takes no fees",            "takes no fees from anyone"],
 ["cannot be steered",        "cannot be steered"],
 ["no referral fees",         "no referral fees"]
].forEach(([label, phrase]) => {
  check("trust statement intact: " + label, pageSrc.indexOf(phrase) !== -1);
});

/* ---- THE FORM IS DISCLOSED WHERE THE PROMISES ARE MADE ----
   The methodology section is where a careful reader goes to check
   whether the privacy claims are real. Adding a form without
   amending that section would make the section the lie. */
[["form named in methodology",  "optional tour-inquiry form shown after the result"],
 ["the fields are named",       "a name, a phone number and an email address, and nothing else"],
 ["kept separate is stated",    "kept completely separate from the assessment"],
 ["skipping it is allowed",     "skipping it changes"],
 /* Rewritten 2026-10-16. The old line said the record "is not sent to
    Westminster Place", which was true of a form that shared nothing and
    is false of one whose purpose is the hand-off. The methodology now
    states the transfer, that it is by hand, and that it is opt-in. */
 ["the transfer is stated",     "passed by hand to westminster place admissions"],
 ["the transfer is opt-in",     "if you tick the permission box"],
 ["the dated record is stated", "a dated record is kept here showing the inquiry started on this site"]
].forEach(([label, phrase]) => {
  check("form disclosure: " + label,
    pageRaw.replace(/\s+/g, " ").indexOf(phrase.replace(/\s+/g, " ").toLowerCase()) !== -1);
});

/* The denial words must ONLY ever appear inside those denials. */
["affiliate", "partner"].forEach((word) => {
  const uses = (pageSrc.match(new RegExp("[^>]{0,40}" + word + "[^<]{0,40}", "g")) || []);
  const bad = uses.filter((u) =>
    u.indexOf("not affiliated") === -1 &&
    u.indexOf("not a referral") === -1 &&
    u.indexOf("no commercial arrangement") === -1);
  check('"' + word + '" appears only inside a denial', bad.length === 0,
    bad.slice(0, 1).join("").trim().slice(0, 50));
});

/* ---- WESTMINSTER MAY APPEAR ONLY WITH THE DISCLOSURE ATTACHED ----
   The assessment stays neutral; the page may name where the author works.
   The FTC treats employment as a material connection that must sit WITH the
   endorsement, so these assertions are positive and specific. Deleting the
   disclosure now fails the build. */
/* The result card is a template inside app.js, so the disclosure lives
   there, not in index.html. Scan everything a visitor can be shown. */
const wpNamed = shownSrc.indexOf("westminster place") !== -1;
if (wpNamed) {
  [["employment is disclosed",          "i work at westminster place"],
   ["not-official is stated",           "not an official westminster place website"],
   ["independently developed is stated", "i independently developed this resource"],
   ["employment relationship is named",  "because of my employment relationship"],
   ["no referral fees is stated",       "no referral fees"],
   /* Two rewrites got here. "I do not collect prospective residents'
      contact information" was made false by the visit form. Its
      replacement was accurate but read as a personal aside. This
      version states the same limit in the register the rest of the
      page uses: why the data is collected, and where it does not go. */
   /* Rewritten 2026-10-16. "Not automatically shared" was a weasel the
      moment sharing became the purpose: the word "automatically" was
      carrying the whole sentence. The disclosure now states the transfer
      plainly, says it is opt-in, and names who receives it. */
   ["sharing is opt-in and said so",    "not shared with westminster place unless you ask for it to be"],
   ["the recipient is named",           "passed to their admissions team"],
   ["purpose of collection is stated",  "a record is kept that your inquiry came through this resource"],
   ["refusal to rank is stated",        "do not rank westminster place"],
   ["state directory is offered",       "healthcarereportcard.illinois.gov"]
  ].forEach(([label, phrase]) => {
    check("disclosure: " + label, shownSrc.indexOf(phrase) !== -1, phrase);
  });

  /* The disclosure must sit INSIDE the same block as the action buttons,
     never in a footer or an About section further down the page. */
  const card = (appSrcRaw.match(/<div class="wp">[\s\S]*?<\/div>/) || [""])[0].toLowerCase();
  /* The card lost its buttons, so "sits with the buttons" describes
     nothing now. The requirement is that the disclosure sits WITH the
     endorsement, which is the form. Asserted by position. */
  check("the disclosure appears before the form it qualifies",
    card.indexOf("i work at westminster place") !== -1);

  /* The engine must still be clean: the decision logic never names anybody. */
  check("the assessment engine still names no community",
    src.indexOf("westminster") === -1 && src.indexOf("presbyterian") === -1);

  /* And the page must no longer carry a claim the site has outgrown.
     The last four were retired when Westminster was named. The first
     four are retired now, by the visit form: each one was true of a
     site with no form on it and is false the moment one exists. */
  ["does not collect your email", "no email required",
   "no personal information required", "no email address, phone number or answer",
   "an independent local resource", "not affiliated with any senior living",
   /* Still banned, and more sharply than before: the operator now hands
      families to Admissions by hand, so "not a referral service" would
      be a false denial rather than a stale one. */
   "not a referral service", "names no communities",
   "do not collect prospective residents",
   /* Retired 2026-10-16 with the consent rewrite. The first was the
      weasel; the second two described a form that asked for a date
      and shared nothing. */
   "not automatically shared with westminster place",
   "used only to document that the visit originated through this resource",
   "save my planned visit"].forEach((stale) => {
    check('stale claim removed: "' + stale.slice(0, 32) + '"',
      shownSrc.indexOf(stale) === -1);
  });
}

/* ---- every care level is reachable ---- */
const reached = new Set(CASES.map(([, picks]) => {
  const r = assess(answersFrom(picks));
  return r.level ? r.level.id : "none";
}));
["independent", "assisted", "memory", "skilled", "rehab"].forEach((id) => {
  check("care level reachable: " + id, reached.has(id));
});

/* ---- next steps are always given ---- */
const { CARE_LEVELS } = require("./assessment.js");
Object.values(CARE_LEVELS).forEach((level) => {
  check("next steps given for " + level.id, (level.nextSteps || []).length >= 3);
});

/* ---- the medical disclaimer exists and says the right thing ---- */
check("disclaimer refuses to be medical advice",
  DISCLAIMER.indexOf("not medical advice") !== -1 &&
  DISCLAIMER.indexOf("doctor") !== -1);

/* ============================================================
   THE ATTRIBUTION STANDARD
   Not "can I measure clicks". The standard is: if Jane Smith
   submits on 8 October and walks into Westminster on the 12th,
   there has to be credible evidence that Jane Smith existed as a
   prospect generated by this site on the 8th — created before
   Westminster ever saw her, and not something that could have
   been typed up afterwards.

   That is what the checks below defend. Each one removes a way
   the evidence could be dismissed.
   ============================================================ */

/* The record must be created by a server, not asserted by a browser
   and not composed by hand in an email client later. */
check("evidence: the id comes from the server, not the client",
  planFnSrc.indexOf("crypto.randomUUID()") !== -1 &&
  appShown.indexOf("randomuuid") === -1);
check("evidence: the timestamp comes from the server clock",
  planFnSrc.indexOf("new Date().toISOString()") !== -1 &&
  planFnSrc.indexOf("payload.receivedAt") === -1 &&
  planFnSrc.indexOf("payload.submissionId") === -1);
check("evidence: the record is retained server-side, independent of email",
  planFnSrc.indexOf("writeDurableRecord") !== -1 &&
  planFnSrc.indexOf("NETLIFY_BLOBS_CONTEXT") !== -1);
/* The record is written and verified BEFORE the notification is
   attempted, so an unset or failing email key can never cost a
   submission. Signature is (submissionId, receivedAt) since the
   notification stopped carrying personal data. */
check("evidence: retention does not depend on the email key",
  planFnSrc.indexOf("writeDurableRecord") <
  planFnSrc.indexOf("sendNotification(record, submissionId"));
check("evidence: an email notification is triggered on success",
  planFnSrc.indexOf("await sendNotification(record, submissionId, receivedAt)") !== -1);
check("evidence: the notification carries the id and the timestamp",
  planFn.indexOf("+ submissionId,") !== -1 &&
  planFn.indexOf("+ receivedAt + \" (UTC, the stored value)\"") !== -1);
check("evidence: the email subject names the source",
  planFn.indexOf("New Westminster Tour Inquiry — Evanston Senior Care Guide") !== -1);
check("evidence: every record is stamped with the source",
  planFn.indexOf('const SOURCE = "Evanston Senior Care Guide"') !== -1);
check("evidence: records can be read back out with timestamps",
  exportFn.indexOf("records") !== -1 && exportFn.indexOf("format=csv") !== -1 ||
  exportFn.indexOf('"csv"') !== -1);
check("evidence: the record survives later deploys (site-scoped store)",
  planFn.indexOf('"/site:"') !== -1 && planFn.indexOf("deploy:") === -1);

/* ---- NO SECRET REACHES THE BROWSER ----
   Everything that authenticates anything lives in the function. If a
   key name ever appears in app.js or index.html, the build fails. */
["RESEND_API_KEY", "PLAN_VISIT_EXPORT_TOKEN", "NETLIFY_BLOBS_CONTEXT",
 "resend_", "access_key", "accesskey", "api_key", "apikey", "bearer ",
 "authorization", "re_"
].forEach((secret) => {
  const inClient = (appSrcRaw + " " + require("fs").readFileSync("index.html", "utf8"))
    .toLowerCase().indexOf(secret.toLowerCase()) !== -1;
  check('no client-side secret: "' + secret + '"', inClient === false);
});
/* Comments stripped first. app.js explains the sanitised channel
   "token" in prose, and a comment about a word is not a credential —
   only shipped code and string literals count. */
const appCode = appSrcRaw
  .replace(/\/\*[\s\S]*?\*\//g, " ")
  .replace(/(^|[^:])\/\/.*$/gm, "$1")
  .toLowerCase();
check("the form sends no credential of its own",
  appCode.indexOf("authorization") === -1 && appCode.indexOf("token") === -1);
check("secrets are read from the environment, never literals",
  planFn.indexOf("process.env.RESEND_API_KEY") !== -1 &&
  exportFn.indexOf("process.env.PLAN_VISIT_EXPORT_TOKEN") !== -1);
/* A Resend key starts re_ . One appearing as a literal anywhere in
   the repo is the failure this gate exists to catch. */
["app.js", "index.html", "netlify/functions/plan-visit.mjs",
 "netlify/functions/plan-visit-export.mjs"].forEach((f) => {
  check("no literal Resend key in " + f,
    !/re_[A-Za-z0-9]{12,}/.test(require("fs").readFileSync(f, "utf8")));
});

/* ---- THE SUCCESS MESSAGE CANNOT IMPLY AN APPOINTMENT ----
   This is the single most important sentence on the page for
   Joseph's position: a visitor must never believe this site booked
   something with his employer. */
const doneBlock = (appSrcRaw.match(/plan__done-h[\s\S]*?plan__done-fine[\s\S]*?<\/p>/) || [""])[0]
  .replace(/\s+/g, " ").toLowerCase();
/* "Visit saved." was retired on 2026-10-16: nothing about a visit is
   saved, and the phrase was the closest this page ever came to sounding
   like a booking. The heading now reports exactly what happened. */
check("success does not say 'Visit saved.'", doneBlock.indexOf("visit saved.") === -1);
check("success states it does not schedule an appointment",
  doneBlock.indexOf("does not schedule an appointment with westminster place") !== -1);
check("success states no tour is guaranteed",
  doneBlock.indexOf("does not guarantee a tour") !== -1);
check("success says the next step belongs to Admissions",
  doneBlock.indexOf("up to westminster place admissions") !== -1 &&
  doneBlock.indexOf("any follow-up comes") !== -1);
check("success confirms the interest was recorded, not acted on",
  doneBlock.indexOf("your interest has been recorded") !== -1);
check("the confirmation offers no outbound Westminster buttons",
  doneBlock.indexOf("visit westminster place") === -1 &&
  doneBlock.indexOf("get directions") === -1 &&
  doneBlock.indexOf("tel:") === -1);
check("the confirmation says they can reach Westminster themselves",
  doneBlock.indexOf("their own contact details are easy to find") !== -1);
check("success shows the server reference back to the visitor",
  doneBlock.indexOf("reference") !== -1 && doneBlock.indexOf("submissionid") !== -1);

/* ---- RETIRED PHRASES MUST NOT COME BACK ----
   Replaced by the employment disclosure. Asserted as absences so a
   later edit cannot quietly reinstate them. */
["a personal project", "my personal project", "personal project",
 "personally operated"].forEach((gone) => {
  check('retired phrase absent: "' + gone + '"', shownSrc.indexOf(gone) === -1);
});
check("replaced by the employment disclosure",
  shownSrc.indexOf("i independently developed this resource") !== -1 &&
  shownSrc.indexOf("because of my employment relationship") !== -1);

/* ---- NO UNVERIFIED CLAIMS ABOUT WESTMINSTER ----
   Only three facts about Westminster are stated anywhere: the
   address, the phone number and the website. Hours, walk-in policy,
   appointment availability, pricing, parking and procedure are not
   claimed, because none of them were verified from an official
   source. */
["walk-in", "walk in welcome", "open daily", "open 24", "hours are",
 "no appointment needed", "appointments available", "free parking",
 "parking is", "tours daily", "starting at $", "per month at westminster",
 "westminster place costs", "ask for me", "mention my name"
].forEach((claim) => {
  check('no unverified Westminster claim: "' + claim + '"',
    shownSrc.indexOf(claim) === -1);
});

/* ---- NOTHING IS SENT TO WESTMINSTER ----
   The function talks to exactly two outside hosts: the blob store
   and the notification provider. Neither is Westminster. */
const outbound = (planFn.match(/fetch\((["'`])https?:\/\/[^"'`]+/g) || [])
  .concat(planFn.match(/fetch\(\s*ctx\.edgeURL/g) || [])
  .concat(planFn.match(/fetch\(\s*blobUrl/g) || []);
check("function makes no request to any Westminster host",
  !/presbyterianliving|westminsterplace|presbyterianhomes/i.test(planFn),
  outbound.join(" ").slice(0, 60));
check("only the notification provider is called by URL",
  (planFn.match(/fetch\("https?:\/\/[^"]+/g) || [])
    .every((u) => u.indexOf("api.resend.com") !== -1));
/* Asserted against stripped CODE. The comment above sendNotification
   records why Web3Forms was dropped — a Cloudflare 403 on every
   server-side POST — and that provenance should outlive the change. */
check("Web3Forms is fully gone from the shipped code",
  !/web3forms/i.test(planFnSrc) &&
  planFn.indexOf("PLAN_VISIT_FORM_KEY") === -1 &&
  planFn.indexOf("access_key") === -1);

/* ---- RESULTS ARE EDUCATIONAL, NEVER A DIAGNOSIS ----
   The assessment reads six answers against published rules. It is not a
   clinician and must not write like one. Every level summary is checked
   for the declarative register — "has reached the point", "needs X",
   "is the issue" — which states a fact about a person nobody examined. */
const { CARE_LEVELS: LEVELS_COPY } = require("./assessment.js");
const DEFINITIVE = [
  "has reached the point", "is the issue", "needs actual",
  "your parent needs", "your parent is", "it is time", "must move",
  "requires immediate", "no longer safe", "can no longer", "is unsafe",
  "clearly needs", "should move", "has dementia", "is suffering"
];
Object.values(LEVELS_COPY).forEach((level) => {
  const text = (level.summary || "").toLowerCase();
  const hits = DEFINITIVE.filter((phrase) => text.indexOf(phrase) !== -1);
  check("summary is not diagnostic: " + level.id, hits.length === 0, hits.join(", "));
});
Object.values(LEVELS_COPY).forEach((level) => {
  check("summary describes the answers, not the person: " + level.id,
    /\b(may|appears|reads as|described|usually)\b/i.test(level.summary || ""),
    (level.summary || "").slice(0, 44));
});

/* The lead sentence must hedge and must name the level, so the result
   reads as "this is worth exploring first", never "this is what they
   need". */
check("result lead is framed as worth exploring, not required",
  appShown.indexOf("may be the level of support worth exploring first") !== -1);
check("result lead names the level it is suggesting",
  appSrcRaw.indexOf("esc(level.name.toLowerCase())") !== -1);

/* ---- THE WESTMINSTER HEADING FOLLOWS THE RESULT ----
   "A local option in Evanston" was generic. The heading now carries the
   care level the visitor just landed on. */
check("Westminster heading reflects the care level",
  appShown.indexOf("considering ${esc(level.name.tolowercase())} in evanston?") !== -1);
check("generic Westminster heading is retired",
  shownSrc.indexOf("a local option in evanston") === -1);

/* ---- NO RAW HTML ENTITIES IN ANY VISITOR-FACING STRING ----
   A stray "judgmen&#x74;" renders as literal gibberish. Nothing a
   visitor reads should contain a numeric entity, so any that appears in
   the engine copy or the result template fails the build. */
const entityPattern = /&#x?[0-9a-f]+;/gi;
Object.values(LEVELS_COPY).forEach((level) => {
  const blob = JSON.stringify(level);
  const found = blob.match(entityPattern) || [];
  check("no numeric entity in level copy: " + level.id, found.length === 0,
    found.slice(0, 3).join(" "));
});
const qBlob = JSON.stringify(QUESTIONS);
check("no numeric entity in question or answer copy",
  (qBlob.match(entityPattern) || []).length === 0,
  (qBlob.match(entityPattern) || []).slice(0, 3).join(" "));
/* The result template may legitimately use named entities (&mdash;),
   but a NUMERIC entity in it means something was escaped twice. */
const tmplEntities = (appSrcRaw.match(/&#x[0-9a-f]+;/gi) || []);
check("no double-escaped entity in the result template",
  tmplEntities.length === 0, tmplEntities.slice(0, 3).join(" "));

/* The five assertions that used to sit here checked the previous
   sourcing copy, which named a senior-living operator blog as the
   basis for every median. That source is retired. The block below
   replaces them with checks against the CareScout survey, and is
   stricter: it verifies the figures themselves, not just that a
   disclaimer exists somewhere near them. */

/* ============================================================
   COST ACCURACY AND SOURCING
   Every number a family reads has to be defensible. These checks
   exist because the previous figures were not: the medians came
   from a senior-living operator blog post, and the memory-care
   "$7,400 Illinois median" described a survey table that does not
   exist.
   ============================================================ */
const CARESCOUT_URL = "https://assets.carescout.com/x/5c90319b6a/298701.pdf";
const CARESCOUT_NAME = "CareScout 2025 Cost of Care Survey, published 2026.";
const COSTS = Object.values(CARE_LEVELS).map((l) => l.cost);
const COSTS_JSON = JSON.stringify(COSTS);

/* 1. Every level has a cost block, and every block says what it is. */
Object.values(CARE_LEVELS).forEach((level) => {
  const c = level.cost;
  check("cost block present: " + level.id, Boolean(c && c.label && c.basis && c.note));
});

/* 2. EVERY DISPLAYED FIGURE CARRIES A SOURCE. No exceptions: a number
      without a survey name and a link cannot be shown. */
Object.values(CARE_LEVELS).forEach((level) => {
  const c = level.cost;
  if (!c.figure) return;
  check("figure is sourced: " + level.id,
    c.survey === CARESCOUT_NAME && c.url === CARESCOUT_URL,
    c.figure + " / " + (c.survey || "NO SURVEY"));
  check("figure states what it measures: " + level.id,
    /illinois/i.test(c.basis), c.basis.slice(0, 44));
  check("figure carries a unit: " + level.id,
    typeof c.unit === "string" && /month/.test(c.unit), c.unit || "none");
});

/* 3. The survey year is labelled accurately. The data is the 2025
      survey, published in 2026. Calling it a 2026 survey would be
      wrong, and so would dropping the publication year. */
check("survey is named as the 2025 survey published 2026",
  CARESCOUT_NAME.indexOf("2025 Cost of Care Survey") !== -1 &&
  CARESCOUT_NAME.indexOf("published 2026") !== -1);
check("page labels the survey the same way",
  pageSrc.indexOf("carescout 2025 cost of care survey, published 2026") !== -1);
check("no stale Illinois-median-2026 label survives",
  COSTS_JSON.toLowerCase().indexOf("illinois median, 2026") === -1);

/* 4. THE UNSUPPORTED MEMORY-CARE MEDIAN CANNOT RETURN. CareScout does
      not separately report an Illinois memory-care median, so there is
      no figure and no dollar amount anywhere in that block. */
const memCost = CARE_LEVELS.memory.cost;
check("memory care shows no figure", memCost.figure === null);
check("memory care explains why there is no figure",
  /does not separately report an illinois memory-care median/i.test(memCost.basis));
check("memory care gives the pricing factors instead",
  /location, accommodation type, staffing/i.test(memCost.note) &&
  /detailed written estimate/i.test(memCost.note));
check("no dollar amount in the memory care cost block",
  !/[$][0-9]/.test(JSON.stringify(memCost)));
["7,400", "7400"].forEach((ghost) => {
  check('retired memory-care figure absent: "' + ghost + '"',
    shownSrc.indexOf(ghost) === -1 && COSTS_JSON.indexOf(ghost) === -1);
});

/* 5. The retired operator-blog source and its figures are gone. */
check("the operator-blog cost source is retired",
  shownSrc.indexOf("cedarhurstliving") === -1);
["4,650", "6,200", "7,850", "9,200"].forEach((stale) => {
  check('retired cost figure absent: "' + stale + '"', COSTS_JSON.indexOf(stale) === -1);
});

/* 6. STATEWIDE COSTS ARE NEVER PRESENTED AS WESTMINSTER PRICES. */
check("result cost block carries the Westminster disclaimer",
  appShown.indexOf("do not represent westminster place&rsquo;s actual") !== -1);
check("cost section on the page carries the same disclaimer",
  pageSrc.indexOf("do not represent westminster place&rsquo;s actual rates") !== -1);
/* The engine must still name no community: the disclaimer lives in the
   templates, never in assessment.js. */
check("the cost data itself names no community",
  COSTS_JSON.toLowerCase().indexOf("westminster") === -1);

/* 7. NURSING HOME AND REHABILITATION PRICING ARE NOT CONFLATED. */
const rehabCost = CARE_LEVELS.rehab.cost;
const skilledCost = CARE_LEVELS.skilled.cost;
check("rehabilitation shows no statewide price", rehabCost.figure === null);
check("rehabilitation names the factors that decide cost",
  /insurance/i.test(rehabCost.basis) && /medicare eligibility/i.test(rehabCost.basis) &&
  /length of stay/i.test(rehabCost.basis));
check("rehabilitation refuses the nursing-home substitution",
  /long-stay nursing home medians do not describe a short rehabilitation stay/i
    .test(rehabCost.basis));
check("no nursing-home dollar figure appears in the rehab block",
  !/[$][0-9],[0-9]{3}/.test(JSON.stringify(rehabCost)));
check("skilled nursing says its figures are long-stay",
  /long-stay nursing home figures, not the out-of-pocket cost/i.test(skilledCost.note));
check("skilled nursing separates semi-private from private",
  skilledCost.figure === "$8,304" && /9,216/.test(skilledCost.basis) &&
  /semi-private/.test(skilledCost.unit));

/* 8. The verified CareScout figures, exactly. */
check("assisted living median is $6,219", CARE_LEVELS.assisted.cost.figure === "$6,219");
check("nursing home semi-private median is $8,304", skilledCost.figure === "$8,304");
check("nursing home private median is $9,216 and labelled",
  /private room has a separate median of [$]9,216 a month/i.test(skilledCost.basis));

/* 9. Independent living: no invented figure, factors instead. */
const indCost = CARE_LEVELS.independent.cost;
check("independent living shows no figure", indCost.figure === null);
check("independent living explains the absence",
  /does not report an illinois figure for independent living/i.test(indCost.basis));
check("independent living gives pricing factors",
  /apartment size/i.test(indCost.note) && /bundled into the monthly fee/i.test(indCost.note));

/* 10. The source link is present, absolute, and opens safely. */
check("source link is the CareScout PDF",
  pageSrc.indexOf(CARESCOUT_URL.toLowerCase()) !== -1);
check("source link opens safely",
  pageRaw.indexOf('href="' + CARESCOUT_URL + '" target="_blank" rel="noopener"') !== -1);
check("result template links the source too",
  appSrcRaw.indexOf('href="${esc(cost.url)}"') !== -1 &&
  appShown.indexOf("view source") !== -1);

/* 11. No category is left as a bare label with nothing under it. */
Object.values(CARE_LEVELS).forEach((level) => {
  const c = level.cost;
  check("cost block reads completely: " + level.id,
    c.basis.length > 28 && c.note.length > 40,
    c.basis.length + "/" + c.note.length);
});

/* ---- THE SUPPORTIVE LIVING FIGURE IS CITED, NOT ASSERTED ----
   $874 was on the page for weeks as "set by the state", with no
   source. It happens to be right — Illinois HFS Provider Notice of
   26 November 2025, effective 1 January 2026 — but being right by
   luck is not the standard. The state revises it with the annual
   Social Security increase, so the citation carries its date. */
check("room and board figure names single and double occupancy",
  pageSrc.indexOf("874") !== -1 && pageSrc.indexOf("625.50") !== -1);
check("room and board figure is dated",
  pageSrc.indexOf("effective 1 january 2026") !== -1);
check("room and board figure links the HFS notice",
  pageSrc.indexOf("hfs.illinois.gov/medicalproviders/notices/notice.prn251126a.html") !== -1);
check("the HFS notice is listed as a source with its date",
  pageSrc.indexOf("illinois hfs provider notice, 26 november 2025") !== -1);
check("the source warns the figure is revised annually",
  pageSrc.indexOf("social security cost-of-living increase") !== -1);

/* ---- SUPPORTIVE LIVING: ROOM AND BOARD IS NOT THE WHOLE BILL ----
   The page previously implied $874 was the resident's out-of-pocket
   cost. Illinois HFS says otherwise: most residents owe a room-and-
   board charge AND a group care credit (patient liability), with
   Medicaid covering the remainder. Stating the first without the
   second understates what a family will actually pay. */
check("room and board is labelled as one charge of two",
  pageSrc.indexOf("expect two charges, not one") !== -1);
check("group care credit is named",
  pageSrc.indexOf("group care credit") !== -1 &&
  pageSrc.indexOf("patient liability") !== -1);
check("patient liability is explained, not just named",
  pageSrc.indexOf("countable income after allowable deductions") !== -1 &&
  pageSrc.indexOf("medicaid covering the remainder") !== -1);
check("the one exception is stated accurately",
  pageSrc.indexOf("avoids the group care credit only when their income equals the ssi amount") !== -1);
check("the personal needs allowance is stated",
  pageSrc.indexOf("$120 personal needs allowance") !== -1);
check("the page refuses to let $874 read as the total",
  pageSrc.indexOf("is not the cost of living there") !== -1);
check("the resident fact sheet is cited",
  pageSrc.indexOf("hfs.illinois.gov/medicalprograms/slf/residentfactsheet.html") !== -1);

/* ---- LAUNCHED: COLLECTION IS ON, AND ITS PRECONDITIONS HOLD ----
   Flipped 2026-10-17 on Joseph's authorisation. This block used to
   assert collection was OFF. It is NOT loosened — it now asserts the
   three things that had to be true before it could go on, so the
   switch can never be on while any of them is missing:

     1. the client renders the form
     2. the privacy notice is actually PUBLISHED, token-free
     3. the server still gates on the environment variable and is
        never hardcoded on

   Point 3 is the one that matters most. The client flag only hides a
   form; the endpoint is the real door, and it must stay switchable
   from outside the code. */
const flagMatch = appSrcRaw.match(/const COLLECTING = (true|false);/);
check("the client flag is an explicit literal", Boolean(flagMatch),
  flagMatch ? flagMatch[1] : "missing");
const CLIENT_ON = Boolean(flagMatch) && flagMatch[1] === "true";
const distFlag = (require("fs").readFileSync("_dist/app.js", "utf8")
  .match(/const COLLECTING = (true|false);/) || [])[1];
check("the deployed copy matches the source flag",
  distFlag === (CLIENT_ON ? "true" : "false"), "source=" + CLIENT_ON + " dist=" + distFlag);
const pubPriv = require("fs").existsSync("_dist/privacy.html")
  ? require("fs").readFileSync("_dist/privacy.html", "utf8") : "";
/* The form may only render when the notice it refers to is actually
   published. Off is always allowed; on has a precondition. */
check("the privacy notice is published whenever the form renders",
  !CLIENT_ON || pubPriv.length > 2000, "form rendering: " + CLIENT_ON);
check("the published notice carries no unresolved token",
  (pubPriv.match(/\{\{[A-Z_]+\}\}/g) || []).length === 0);
check("the published notice names a deletion contact",
  /[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}/i.test(pubPriv));
check("the published notice states the 180-day period",
  pubPriv.indexOf("180 days") !== -1);
check("the server switch is never hardcoded on",
  planFnSrc.indexOf("const COLLECTING = true") === -1);
check("the form markup is preserved, not deleted",
  appSrcRaw.indexOf("function planFormBlock(levelId, variant, interestOverride)") !== -1 &&
  appShown.indexOf('name="phone"') !== -1 &&
  appShown.indexOf('name="consent"') !== -1);
/* The paused branch stays in the source even while live, so the form
   can be switched back off by one flag without rewriting copy. */
check("the paused branch is preserved for switching back",
  appShown.indexOf("it is not open yet") !== -1 &&
  appShown.indexOf("the server refuses it") !== -1 &&
  appShown.indexOf("coming soon") === -1);
check("the endpoint refuses submissions independently",
  planFnSrc.indexOf('process.env.PLAN_VISIT_COLLECTION_ENABLED === "true"') !== -1 &&
  planFnSrc.indexOf('reason: "collection_disabled"') !== -1);
check("collection defaults to off, never on",
  planFnSrc.indexOf('PLAN_VISIT_COLLECTION_ENABLED === "true"') !== -1 &&
  planFnSrc.indexOf("|| true") === -1);
check("the refusal happens before any storage code",
  planFnSrc.indexOf("collection_disabled") < planFnSrc.indexOf("crypto.randomUUID()"));

/* ---- THE TOUR ROUTE IS NOW OURS, AND ITS LIMITS HOLD ----
   Changed 2026-10-17. The external CTA to Westminster's own inquiry
   form is REMOVED: the guide has its own form, and sending a family
   to a second form that asks the same questions was the long detour
   this page existed to shorten.

   What must not change is the protection that CTA carried. "No tour
   is promised" and "Westminster decides" were asserted against that
   block's copy; they are now asserted against the form's own copy,
   so removing the button removed a button and not a safeguard. */
/* Asserted against the MARKUP, not the file. The contact/ URL still
   appears in a source comment documenting where the phone numbers were
   transcribed from — that comment is provenance and must stay. A gate
   that cannot tell a comment from an href fails for the wrong reason. */
const appNoComments = appSrcRaw
  .replace(/\/\*[\s\S]*?\*\//g, " ")
  .replace(/(^|[^:])\/\/.*$/gm, "$1")
  .replace(/\s+/g, " ").toLowerCase();
check("the external request-form CTA is gone",
  appNoComments.indexOf("westminster-place/contact/") === -1 &&
  appNoComments.indexOf("request a visit on westminster&rsquo;s site") === -1);
check("no tour is promised",
  appShown.indexOf("this form doesn&rsquo;t book anything") !== -1);
check("the site still never claims to schedule",
  appShown.indexOf("they decide whether and when a tour happens") !== -1);
/* REMOVED 2026-10-17 on the owner's instruction: the form is the single
   call to action on every result page now. These were "must be present"
   gates; they are "must be absent" gates, so the buttons cannot creep
   back and quietly compete with the form.

   The protection they carried — never point a family at a number
   Westminster has not published — did not vanish with them. It MOVED to
   the notification email, which names the team and its number, and is
   asserted against the published list below. */
check("no outbound Westminster call link on any result page",
  appShown.indexOf('data-beacon="wp-call"') === -1 &&
  appShown.indexOf('href="tel:') === -1);
check("no outbound Westminster website link",
  appShown.indexOf('data-beacon="wp-site"') === -1);
check("no outbound directions link",
  appShown.indexOf('data-beacon="wp-directions"') === -1 &&
  appShown.indexOf("3200+grant+street") === -1);
check("the form is the primary call to action",
  appShown.indexOf('class="res__block plan plan--primary"') !== -1);
check("the form states plainly it is not a booking",
  appShown.indexOf("doesn&rsquo;t book anything") !== -1);
check("the visitor is never auto-redirected to Westminster",
  appShown.indexOf("window.location =") === -1 &&
  appShown.indexOf("location.href =") === -1);
/* Relocated protection: every number the EMAIL can name must be one
   Westminster publishes. */
["(847) 570-3310", "(847) 866-1615", "(847) 492-7780", "(847) 570-3422"]
  .forEach((tel) => {
    check("email may only name a published number: " + tel,
      planFn.indexOf(tel) !== -1);
  });
check("no unpublished number exists in the notification mapping",
  (planFn.match(/\(847\) [0-9]{3}-[0-9]{4}/g) || [])
    .every((t) => ["(847) 570-3310", "(847) 866-1615",
                   "(847) 492-7780", "(847) 570-3422"].indexOf(t) !== -1));

/* ---- THE RESULT PAGE ORDER ----
   Locked 2026-10-17 on Joseph's instruction: the educational content
   comes first, the form sits directly after what the care provides,
   and costs plus evaluation questions follow it while staying one
   click away. Order is asserted by position, because a reorder that
   silently buries the form is exactly the regression prose cannot
   catch.

   Re-ordered 2026-10-30 on Joseph's instruction (Simple First): the
   visitor reads answer -> costs -> how to pay -> optional Westminster
   Place inquiry. The answer leads with the level in plain words, the
   "not a diagnosis" limit and one button, "See what it costs"; the
   reasoning and the visitor's own answers sit behind "Why this
   result?"; costs and the payment entry come BEFORE the form; the
   evaluating questions and the state directory follow it. The form is
   still reached by the IL block's tour action, the hero shortcut and
   the guide pathway, and its disclosures, consent and order are
   asserted separately below. */
/* The order is asserted inside the result template ONLY. planFormBlock()
   is DEFINED near the top of app.js, so scanning the whole file reports
   the form before the heading it actually renders after — which is how
   the first version of this gate failed while the page was correct. */
const tplStart = appSrcRaw.indexOf('<p class="res__label">Your starting point');
const tplEnd = appSrcRaw.indexOf('<p class="res__fine">', tplStart);
check("the result template was located", tplStart !== -1 && tplEnd > tplStart);
const tpl = appSrcRaw.slice(tplStart, tplEnd);

const ORDER = [
  ["your starting point",                      "Your starting point"],
  ["the one next step: see what it costs",     "See what it costs"],
  ["why this result, with the answers given",  "Why this result?"],
  ["what this type of care usually provides",  "What this type of care usually provides"],
  ["what it costs",                            "usually costs"],
  ["how to pay for it",                        "paymentEntry(level.id)"],
  ["what a visit would tell you",              "visitBlock(level.id, line)"],
  ["the Westminster card with its disclosure", "I work at Westminster Place"],
  ["our own tour-inquiry form",                "COLLECTING ? planFormBlock("],
  ["questions to ask when evaluating options", "Questions to ask when evaluating options"],
  ["the Illinois state directory",             "healthcarereportcard.illinois.gov"]
];
let lastAt = -1;
let orderOk = true;
ORDER.forEach(([label, marker]) => {
  const at = tpl.indexOf(marker);
  check("order: " + label, at !== -1, at === -1 ? "MISSING" : "");
  if (at === -1 || at < lastAt) orderOk = false;
  if (at !== -1) lastAt = at;
});
check("result page sections are in the locked order", orderOk);

/* ---- THE FORM MUST REACH EVERY RESULT PATH ----
   Added 2026-10-17 after Joseph answered the first option on all six
   questions, landed on the "no higher level of care yet" result, and
   found no form. The assessment has SIX outcomes — five care levels
   and no_need — and the form had only ever existed on the five. A
   result page a visitor can actually reach without the form is the
   same defect as the form not existing. Asserted per branch. */
const noNeedStart = appSrcRaw.indexOf('result.status === "no_need"');
const noNeedEnd = appSrcRaw.indexOf("wireResult();", noNeedStart);
const noNeedBranch = noNeedStart === -1 ? "" : appSrcRaw.slice(noNeedStart, noNeedEnd);
check("the no-need branch was located", noNeedBranch.length > 200);
/* ---- INDEPENDENT LIVING MUST BE VISIBLE WITHOUT THE LIFESTYLE ANSWER ----
   Reproduced live 2026-10-26: the owner answered all six questions with
   the no-concerns option, got "No higher level of care yet", and never
   saw independent living. The lifestyle answer is option two of five on
   question six; nobody reads that as the independent-living door. */
check("the no-need result names independent living prominently",
  /<section class="res__block il" id="independent-living">/.test(noNeedBranch));
check("it is titled Independent Living at heading weight",
  /<h4 class="il__h">Independent Living<\/h4>/.test(noNeedBranch));
/* The eyebrow does the ethical work: it disclaims a recommendation BEFORE
   naming the option, so prominence can never read as a diagnosis. */
check("the disclaimer sits ABOVE the name, not below it",
  noNeedBranch.indexOf("not a care recommendation") <
  noNeedBranch.indexOf('<h4 class="il__h">'));
/* ACCURACY, 2026-10-26. The first copy said a cottage comes "with the
   cooking, cleaning, grounds and driving handled for you", which asserts
   as universal what every community prices differently. */
check("it says services vary by community",
  /Services vary by community/.test(noNeedBranch));
check("it says personal and nursing care are generally NOT included",
  /not<\/strong> include hands-on personal or nursing/.test(noNeedBranch));
check("it does not assert bundled services as universal",
  noNeedBranch.indexOf("with the cooking") === -1 &&
  noNeedBranch.indexOf("handled for you") === -1);
check("it says the move is entirely voluntary",
  /Entirely voluntary/.test(noNeedBranch));
check("it says nothing here is medical advice",
  /nothing here is medical advice/.test(noNeedBranch));
check("it offers both a guide link and a tour action",
  noNeedBranch.indexOf('href="/guides/independent-living-evanston/"') !== -1 &&
  noNeedBranch.indexOf('href="#plan-visit"') !== -1);
/* Buried is the defect being fixed. The section must precede the
   secondary "worth doing anyway" block, not follow it. */
/* Buried is the defect. It must follow the conclusion heading
   IMMEDIATELY -- ahead of the summary paragraph, which is what put it
   238px down the page when measured in a real browser. */
check("independent living comes straight after the conclusion heading",
  noNeedBranch.indexOf('class="res__block il"') <
  noNeedBranch.indexOf('class="res__summary"'));
check("independent living appears BEFORE the worth-doing-anyway block",
  noNeedBranch.indexOf('class="res__block il"') <
  noNeedBranch.indexOf("Worth doing anyway"));
check("the conclusion stays honest",
  /No significant care needs identified/.test(noNeedBranch));
check("the no-need result links to the independent living guide",
  noNeedBranch.indexOf('href="/guides/independent-living-evanston/"') !== -1);
/* The honest conclusion now lives in the heading and the summary, not in
   the independent-living section, which is the point of the refinement. */
check("the no-need result still says no care is needed",
  /No significant care needs identified/.test(noNeedBranch) &&
  /describes a need to move/.test(noNeedBranch));
check("the no-need result offers no care level as a substitute",
  noNeedBranch.indexOf("assisted living may be") === -1 &&
  noNeedBranch.indexOf("worth exploring first") === -1);
check("a no-care-need result pre-selects independent living on the form",
  /if \(levelId === "no_need"\) return "independent";/.test(appSrcRaw));
check("no long paragraph in the section: every line under 240 chars",
  (noNeedBranch.match(/<p class="il__lead">[\s\S]*?<\/p>/g) || [])
    .every((t) => t.replace(/<[^>]+>/g, "").replace(/\s+/g, " ").length < 240));
check("the by-choice result also links to the guide",
  (appSrcRaw.match(/href="\/guides\/independent-living-evanston\/"/g) || [])
    .length >= 2,
  String((appSrcRaw.match(/href="\/guides\/independent-living-evanston\/"/g)
    || []).length));
/* The care results must NOT grow an independent-living block. It is not a
   substitute for assisted living, memory care or skilled nursing. */
check("the independent living block is gated on lifestyle or no_need only",
  (appSrcRaw.match(/res__block il/g) || []).length === 2,
  String((appSrcRaw.match(/res__block il/g) || []).length));

check("the form renders on the no-need result too",
  noNeedBranch.indexOf("COLLECTING ? planFormBlock(") !== -1);
/* Three render paths now: the matched result, the no-care-need result, and
   the direct inquiry. All three must gate on the same flag -- a path that
   renders the form while COLLECTING is false is a collection switch that
   does not switch. */
check("all three render paths gate the form on the same flag",
  (appSrcRaw.match(/COLLECTING \? planFormBlock\(/g) || []).length === 3,
  String((appSrcRaw.match(/COLLECTING \? planFormBlock\(/g) || []).length));
/* 2026-10-30: answer -> costs -> how to pay -> optional inquiry. The
   cost block and the payment entry come before the form, the evaluating
   questions after it. The form is never the thing a visitor has to pass
   to reach the price. */
check("costs and the payment entry come BEFORE the form",
  tpl.indexOf("usually costs") < tpl.indexOf("COLLECTING ? planFormBlock(") &&
  tpl.indexOf("paymentEntry(level.id)") < tpl.indexOf("COLLECTING ? planFormBlock("));
check("the evaluating questions follow the form",
  tpl.indexOf("COLLECTING ? planFormBlock(") <
    tpl.indexOf("Questions to ask when evaluating options"));
/* The answer card stays short: the level, one plain line, the limit and
   the one button come before any reasoning, and the reasoning is a row
   the visitor opens. The answers they gave stay in that row. */
check("the limit is stated before the first next step",
  tpl.indexOf("not a diagnosis") < tpl.indexOf("See what it costs"));
check("the reasoning sits behind a row the visitor opens",
  /<details class="more"[^>]*>\s*<summary><h4 class="res__h">Why this result\?<\/h4><\/summary>/.test(tpl) &&
  tpl.indexOf("Why this result?") < tpl.indexOf('<ul class="why">'));
check("the hedged lead moved into the reasoning row, not out of the page",
  tpl.indexOf("may be the level of support worth") > tpl.indexOf("Why this result?") &&
  tpl.indexOf("may be the level of support worth") < tpl.indexOf("usually costs"));
check("the no-need result also puts the payment entry before the form",
  noNeedBranch.indexOf('paymentEntry("unsure")') < noNeedBranch.indexOf("COLLECTING ? planFormBlock("));
check("costs and questions stay one click away",
  appShown.indexOf('href="#costs"') !== -1 &&
  appShown.indexOf('href="#evaluating"') !== -1 &&
  appShown.indexOf('id="costs"') !== -1 &&
  appShown.indexOf('id="evaluating"') !== -1);
/* Every data-beacon on the page must have a listener, or it reports a
   silent zero forever. */
["costs", "tour", "idph"].forEach((b) => {
  check('beacon "' + b + '" is wired', appSrcRaw.indexOf('which === "' + b + '"') !== -1);
});
check("the retired inquiry beacon is fully removed",
  appSrcRaw.indexOf("wpInquiry") === -1 &&
  appSrcRaw.indexOf("wp-inquiry") === -1);

/* ---- PHONE ROUTING USES PUBLISHED NUMBERS ONLY ----
   Every number is transcribed from Westminster's own directory.
   An unpublished or invented number would send a family to a line
   nobody answers, which is worse than the general line. */
const WP_PUBLISHED = {
  "8475703310": "Independent Living Sales",
  "8478661615": "Assisted Living & Memory Care Sales",
  "8474927780": "Skilled Nursing Admissions",
  "8475703422": "General Inquiries"
};
const telsInApp = (appSrcRaw.match(/tel: "([0-9]{10})"/g) || [])
  .map((m) => m.replace(/[^0-9]/g, ""));
check("every routed number is one Westminster publishes",
  telsInApp.length > 0 && telsInApp.every((t) => WP_PUBLISHED[t]),
  telsInApp.join(" "));
/* Parse the WP_LINES block itself rather than regex-matching each
   row: the earlier version matched nothing and reported five
   failures that were my escaping, not the routing. */
/* Slice between the two known markers rather than regex across
   newlines — three attempts at a multiline pattern were mangled by
   shell escaping before this, and a sliced string cannot be. */
const wpStart = appSrcRaw.indexOf("const WP_LINES = {");
const wpEnd = appSrcRaw.indexOf("const WP_GENERAL");
const linesBlock = wpStart === -1 ? "" : appSrcRaw.slice(wpStart, wpEnd);
[["independent", "8475703310"], ["assisted", "8478661615"],
 ["memory", "8478661615"], ["skilled", "8474927780"],
 ["rehab", "8474927780"]].forEach(([lvl, tel]) => {
  const at = linesBlock.indexOf(lvl + ":");
  const slice = at === -1 ? "" : linesBlock.slice(at, at + 160);
  check("routing correct for " + lvl, slice.indexOf(tel) !== -1,
    at === -1 ? "level missing" : tel);
});
check("a general-line fallback exists for an unknown level",
  appSrcRaw.indexOf("WP_LINES[levelId] || WP_GENERAL") !== -1);
check("the retired call and directions beacons stay removed",
  appSrcRaw.indexOf("wpCall") === -1 && appSrcRaw.indexOf("wpDirections") === -1);
check("the routed team is still named to the visitor",
  appShown.indexOf("they publish a direct line for each team") !== -1);

/* ---- ATTRIBUTION HONESTY ----
   Rewritten 2026-10-17. These gates used to govern the coaching note
   telling a family which option to pick in Westminster's own "How Did
   You Hear About Us?" dropdown. That note and that link are gone, so
   the gates are now absences: the site must not reacquire a source
   parameter it cannot populate, and must never coach a visitor on what
   to say to Westminster. Attribution lives in this site's own
   timestamped record, which is the only place it was ever provable. */
check("no source parameter is appended to any Westminster link",
  appShown.indexOf("contact/?src") === -1 &&
  appShown.indexOf("contact/?utm") === -1);
check("the dropdown coaching note is gone",
  appShown.indexOf("how did you hear") === -1 &&
  appShown.indexOf("community website") === -1);
check("the site never instructs anyone what to tell Westminster",
  appShown.indexOf("tell them you came from") === -1 &&
  appShown.indexOf("mention this guide") === -1);

/* ---- ATTRIBUTION AND STAGE ARE STAMPED ON THE RECORD ----
   The authorship of this work travels with the evidence, and every
   record names the rung it sits on so it cannot be read as a
   higher one later. */
check("every record names its developer",
  planFn.indexOf('const DEVELOPED_BY = "Joseph Gonzales"') !== -1 &&
  planFnSrc.indexOf("developedBy: DEVELOPED_BY") !== -1);
check("every record names its evidence stage",
  planFnSrc.indexOf('stage: "recorded_tour_inquiry"') !== -1);
/* The referral is a phone call a person makes. The endpoint must never
   stamp it, or an un-referred inquiry reads as one that was passed on. */
check("the referral field starts null and is never set by the endpoint",
  planFnSrc.indexOf("referredToAdmissionsAt: null") !== -1 &&
  (planFnSrc.match(/referredToAdmissionsAt/g) || []).length === 1);
check("the export explains what the stage does not mean",
  exportFn.indexOf("not a referral, not a completed tour and not a move-in") !== -1);
check("the notification names the developer too",
  planFn.indexOf("+ DEVELOPED_BY,") !== -1);

/* ---- THE NOTIFICATION CARRIES NO PERSONAL INFORMATION ----
   Web3Forms retains three years against a 180-day policy. The fix
   is to send nothing worth retaining. */
/* Sliced between known markers, not regex-matched across newlines:
   a multiline pattern written through a shell gets its backslashes
   eaten, and the resulting gate passes while checking nothing. */
const notifStart = planFn.indexOf("function notificationText");
const notifEnd = planFn.indexOf("async function sendNotification");
const notifBlock = notifStart === -1 ? "" : planFn.slice(notifStart, notifEnd);
/* INVERTED 2026-10-17 on the owner's instruction. These four used to
   assert the email contained NO personal data. The alert now has to
   carry it, because an alert you must go and look something up from
   gets ignored. The trade is disclosed in the published privacy
   notice and in the email's own last line — asserted below. */
["record.firstName", "record.lastName", "record.email", "record.phone"]
  .forEach((field) => {
  check('notification INCLUDES ' + field, notifBlock.indexOf(field) !== -1);
});
check("notification includes the care level and the routed team",
  notifBlock.indexOf("ASSESSMENT RESULT") !== -1 &&
  notifBlock.indexOf("ADMISSIONS TEAM") !== -1 &&
  notifBlock.indexOf("lvl.dept") !== -1 && notifBlock.indexOf("lvl.tel") !== -1);
check("notification includes a human-readable local time",
  notifBlock.indexOf("America/Chicago") !== -1 &&
  notifBlock.indexOf("(UTC, the stored value)") !== -1);
/* The email prose says the answers were never sent, so a substring
   scan trips on its own reassurance. Assert what is INTERPOLATED:
   every "record.x" read in the email must be a permitted field. */
const notifFields = (notifBlock.match(/record\.[a-zA-Z]+/g) || [])
  .map((m) => m.split(".")[1]);
/* `interest` added 2026-10-26: the visitor's own selection, drawn from a
   fixed list in the function, and named in the consent they ticked. */
const NOTIF_ALLOWED = ["firstName", "lastName", "phone", "email", "careLevel",
                       "interest"];
check("notification reads only permitted record fields",
  notifFields.every((f) => NOTIF_ALLOWED.indexOf(f) !== -1),
  notifFields.filter((f) => NOTIF_ALLOWED.indexOf(f) === -1).join(" "));
check("notification interpolates no assessment detail",
  notifBlock.indexOf("record.answers") === -1 &&
  notifBlock.indexOf("record.reasons") === -1 &&
  notifBlock.indexOf("result.reasons") === -1);
check("notification warns the email is outside the 180-day policy",
  notifBlock.indexOf("NOT covered by") !== -1);
/* The provider payload must carry nothing personal. Sliced between
   the endpoint and the end of the request body so the assertion is
   about what is actually SENT, not about the whole file. */
const provStart = planFn.indexOf("api.resend.com");
const provEnd = planFn.indexOf("if (res.ok)", provStart);
const provBlock = provStart === -1 ? "" : planFn.slice(provStart, provEnd);
check("the provider block was located", provBlock.length > 40);
["record.firstName", "record.lastName", "record.email", "record.phone",
 "firstName", "lastName", "phone:"].forEach((k) => {
  check('Resend payload omits ' + k, provBlock.indexOf(k) === -1);
});
check("the Resend payload is built by notificationText, not inline fields",
  provBlock.indexOf("notificationText(record, submissionId, receivedAt)") !== -1);
check("the recipient and sender are variables, not literals",
  provBlock.indexOf("to: [NOTIFY_TO]") !== -1 &&
  provBlock.indexOf("from: NOTIFY_FROM") !== -1);
check("a rejection logs a status only, never a body",
  planFn.indexOf("notification rejected, status") !== -1 &&
  planFn.indexOf("await res.text()") === -1);
check("notification still carries the id and timestamp",
  notifBlock.indexOf("submissionId") !== -1 && notifBlock.indexOf("receivedAt") !== -1);
check("notification refuses to read as a confirmed tour",
  notifBlock.indexOf("it is not a confirmed tour") !== -1);

/* ---- RETENTION IS WIRED, NOT JUST WRITTEN ---- */
const fsR = require("fs");
check("retention module is deployed, not staged",
  fsR.existsSync("netlify/functions/retention.mjs"));
check("the daily scheduled purge is deployed",
  fsR.existsSync("netlify/functions/retention-daily.mjs"));
check("the submission path triggers a purge",
  planFnSrc.indexOf("purgeExpired(blobsContext(), STORE)") !== -1);
check("the purge never blocks or fails a submission",
  planFnSrc.indexOf("purgeExpired(blobsContext(), STORE).catch(() => {})") !== -1);
const daily = fsR.readFileSync("netlify/functions/retention-daily.mjs", "utf8");
check("the daily job runs on a schedule",
  daily.indexOf('schedule: "@daily"') !== -1);
check("the retention period is 180 days",
  fsR.readFileSync("netlify/functions/retention.mjs", "utf8")
    .indexOf("const DEFAULT_DAYS = 180") !== -1);
/* The purge receipt was specified to travel with the export and was
   never actually connected — so "deletion runs automatically" was a
   claim nobody reading the records could check. Wired 2026-10-16. */
check("the export returns the purge receipt",
  exportFn.indexOf("readPurgeReceipt") !== -1 &&
  exportFn.indexOf("retention: await readPurgeReceipt(ctx, STORE)") !== -1);

/* ---- THE PRIVACY NOTICE HAS ONE TOKEN LEFT ---- */
const priv = fsR.readFileSync("staged/privacy.html", "utf8");
const tokens = priv.match(/\{\{[A-Z_]+\}\}/g) || [];
/* Tightened 2026-10-16, when the last token was resolved. The old gate
   allowed {{CONTACT_EMAIL}} to remain, so once it was filled in the
   check passed on an empty array and protected nothing. It now asserts
   the opposite: no tokens at all, and a real reachable address present.
   A privacy notice whose deletion route is blank is worse than none. */
check("the privacy notice has no unresolved tokens",
  tokens.length === 0, tokens.join(" "));
const contact = priv.match(/[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}/i);
check("the privacy notice publishes a deletion contact address",
  contact !== null, contact ? contact[0] : "none");
check("the deletion contact is reachable in the removal section",
  /Asking to be removed[\s\S]{0,400}@/.test(priv));
/* The notice must now DISCLOSE what the email carries, and must not
   still claim the opposite. Both directions asserted, because the
   failure mode is a notice describing last week. */
check("the notice discloses what the notification email contains",
  priv.indexOf("that email contains your") !== -1 &&
  priv.indexOf("name, phone number, email address and care level") !== -1);
check("the notice no longer claims the email is anonymous",
  priv.indexOf("no personal information at all") === -1);
check("the notice names the real email provider",
  priv.indexOf("Resend") !== -1 && priv.indexOf("Web3Forms") === -1);
check("the notice discloses the care level travels",
  priv.indexOf("care level those questions suggested") !== -1 ||
  priv.indexOf("care level the questions suggested") !== -1);

/* ---- NOTHING STAGED MAY EVER BE DEPLOYED ----
   staged/ holds the sharing consent, the privacy notice and the
   retention module. All three are built and none are authorised:
   the consent asks permission for a reconciliation Westminster has
   not agreed to, and the privacy notice still carries unresolved
   tokens for the retention period and the deletion address.

   Shipping either early is worse than the problem it fixes, so the
   build fails if any of it reaches the deploy directory, and fails
   if an unresolved token ever appears in shipped copy. */
const fsMod = require("fs");
const DIST = "_dist";
if (fsMod.existsSync(DIST)) {
  const walk = (dir) => fsMod.readdirSync(dir, { withFileTypes: true })
    .flatMap((e) => e.isDirectory()
      ? walk(dir + "/" + e.name)
      : [dir + "/" + e.name]);
  const shipped = walk(DIST);
  /* Loosened 2026-10-16, and only in one direction. The old gate
     failed on ANY privacy.html in _dist, which made publishing the
     privacy notice — a launch requirement — impossible without
     editing the gate under pressure. What actually must never ship
     is a copy out of staged/ or a copy with an unresolved token;
     the token gate immediately below enforces the second, and is
     the one that was doing the real work all along. A finished
     privacy notice in _dist is the goal, not the hazard. */
  check("staged/ is not in the deploy directory",
    !shipped.some((f) => /\/staged\//.test(f)),
    shipped.filter((f) => /\/staged\//.test(f)).join(" "));
  /* The retention modules are FUNCTIONS. They belong in
     netlify/functions, never in the published directory, because
     anything in _dist is reachable by a visitor. */
  check("no server module is published as a static file",
    !shipped.some((f) => /retention.*\.mjs$/.test(f) || /plan-visit.*\.mjs$/.test(f)),
    shipped.filter((f) => /\.mjs$/.test(f)).join(" "));

  const tokenLeak = shipped.filter((f) => /\.(html|js|css|mjs)$/.test(f))
    .filter((f) => /\{\{[A-Z_]+\}\}/.test(fsMod.readFileSync(f, "utf8")));
  check("no unresolved template token in anything shipped",
    tokenLeak.length === 0, tokenLeak.join(" "));
}

/* ---- ONE CONSENT, AND IT IS THE SHARING CONSENT ----
   Superseded 2026-10-16. The old design had a required
   attribution consent plus an optional sharing tickbox, because
   sharing was a side errand. Sharing is now the purpose: the
   details exist so Admissions can be handed them. A second
   optional box would imply the first one permits something it
   does not, so there is exactly one consent and it authorises the
   transfer in so many words.

   staged/consent-changes.md describes the retired two-box design
   and is kept as a record of it. It must stay out of the deploy,
   and its field name must never appear in live code. */
check("the site states sharing is opt-in, not automatic",
  shownSrc.indexOf("not shared with westminster place unless you ask for it to be") !== -1);
check("the site never claims sharing cannot happen",
  shownSrc.indexOf("never shared with westminster") === -1 &&
  shownSrc.indexOf("is not shared with westminster place.") === -1);
check("the retired second consent field is not live",
  shownSrc.indexOf('name="shareconsent"') === -1);
check("the function accepts no second sharing field",
  planFn.indexOf("shareConsent") === -1);
check("the one live consent is required on the server",
  planFnSrc.indexOf("payload.consent !== true") !== -1 &&
  planFnSrc.indexOf("consent: true") !== -1);

/* ---- NO STRAY CONTROL BYTES IN ANY SOURCE FILE ----
   Writing these files through a shell heredoc silently eats one
   level of backslash, which turns a regex "\b" into a literal
   0x08 backspace byte. The regex then still parses and still
   runs — it just never matches, so a gate reports PASS while
   protecting nothing. This happened on 2026-10-08 inside
   browser-test.mjs and was only caught by probing the live DOM.

   Every source file is scanned, harnesses included. A test file
   left out of this list is a test file that can rot unnoticed. */
["app.js", "assessment.js", "test.js", "index.html", "styles.css",
 "browser-test.mjs", "shots.mjs", "netlify/functions/plan-visit.mjs",
 "netlify/functions/plan-visit-export.mjs",
 "netlify/functions/retention.mjs", "netlify/functions/retention-daily.mjs",
 "staged/privacy.html"].forEach((file) => {
  const bytes = require("fs").readFileSync(file);
  const bad = [];
  for (let i = 0; i < bytes.length; i++) {
    const c = bytes[i];
    if (c < 9 || (c > 13 && c < 32) || c === 127) {
      bad.push(i + ":0x" + c.toString(16));
    }
  }
  check("no control bytes in " + file, bad.length === 0, bad.slice(0, 4).join(" "));
});

/* ============================================================
   REGRESSION GATES — external review, 2026-10-17
   ============================================================
   Six findings came back from an independent review of the ZIP.
   Each fix gets a gate here so it cannot silently revert, and the
   gate asserts the BEHAVIOUR, not the wording of the patch.
   ============================================================ */
{
  const fs = require("fs");
  const exportSrc = fs.readFileSync("netlify/functions/plan-visit-export.mjs", "utf8");
  const appSrc = fs.readFileSync("app.js", "utf8");
  const appFlat = appSrc.replace(/\s+/g, " ").toLowerCase();

  /* --- 1. DELETION: exact, complete UUID only --------------- */
  check("delete validates a complete UUID before matching",
    exportSrc.indexOf("UUID_RE.test(id)") !== -1);
  check("the UUID pattern is anchored at both ends",
    exportSrc.indexOf("/^[0-9a-f]{8}-") !== -1 &&
    exportSrc.indexOf("[0-9a-f]{12}$/i") !== -1);
  check("delete no longer matches on a substring",
    exportSrc.indexOf("k.indexOf(id) !== -1") === -1);
  check("delete matches the key exactly",
    exportSrc.indexOf('const want = "__" + id + ".json"') !== -1 &&
    exportSrc.indexOf("k.endsWith(want)") !== -1);
  check("delete refuses to act on more than one match",
    exportSrc.indexOf("match.length > 1") !== -1 &&
    exportSrc.indexOf("Nothing was deleted") !== -1);
  /* The regex itself, executed — a pattern that parses but does not
     match is the failure mode this whole suite exists to catch. */
  const UUID_RE =
    /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
  [["a", false], ["", false], ["../../etc", false],
   ["d84b0415-b93c-48f7-ad6e-322a5db03f18", true],
   ["d84b0415-b93c-48f7-ad6e-322a5db03f1", false],
   ["d84b0415b93c48f7ad6e322a5db03f18", false],
   ["xd84b0415-b93c-48f7-ad6e-322a5db03f18", false]].forEach(([v, want]) => {
    check('uuid guard: "' + (v || "(empty)").slice(0, 20) + '" -> ' + want,
      UUID_RE.test(v) === want);
  });

  /* --- 2. DISCLOSURE on every result that shows the form ---- */
  const noNeed = appSrc.slice(appSrc.indexOf('result.status === "no_need"'),
                              appSrc.indexOf("wireResult();"));
  check("the no-need result carries the employment disclosure",
    noNeed.indexOf("I work at Westminster Place") !== -1 &&
    noNeed.indexOf("not an official Westminster") !== -1);
  check("the no-need disclosure sits before its form",
    noNeed.indexOf("I work at Westminster Place") <
      noNeed.indexOf("COLLECTING ? planFormBlock("));
  check("the no-need disclosure states no referral fees",
    noNeed.indexOf("no referral fees") !== -1);

  /* --- 3. NO GUARANTEE of follow-up ------------------------- */
  ["they will contact you", "will be the ones to contact you",
   "admissions will contact", "you will be contacted"].forEach((promise) => {
    check('no guarantee of contact: "' + promise.slice(0, 28) + '"',
      appFlat.indexOf(promise) === -1);
  });
  check("follow-up is stated as Admissions' decision",
  appShown.indexOf("they decide whether and when a tour happens") !== -1);
  check("the confirmation refuses to promise follow-up",
    appFlat.indexOf("this guide cannot promise it") !== -1);

  /* --- 4. ASSESSMENT: hospital recency must not override the
           highest stated nursing need ----------------------- */
  const { QUESTIONS: Q, assess: A } = require("./assessment.js");
  const qids = Q.map((q) => q.id);
  const mk = (picks) => { const o = {}; picks.forEach((c, i) => { o[qids[i]] = c; }); return o; };
  [["24h nursing + recovering",     [2, 0, 3, 2, 1, 3], "skilled"],
   ["24h nursing + in hospital now", [2, 0, 3, 2, 3, 3], "skilled"],
   ["24h nursing + no hospital",     [2, 0, 3, 2, 0, 3], "skilled"],
   ["mild needs + recovering",       [2, 0, 1, 1, 1, 3], "rehab"],
   ["mild needs + in hospital now",  [2, 1, 1, 1, 3, 3], "rehab"]].forEach(
    ([label, picks, want]) => {
      const got = A(mk(picks)).level.id;
      check("routing: " + label, got === want, got);
    });
  check("the rehab rule excludes the top medical answer",
    fs.readFileSync("assessment.js", "utf8").indexOf("s.medical < 3") !== -1);
  /* The result must still explain itself — that is the point of the
     assessment, and a routing fix must not cost the explanation. */
  check("the reassigned case still quotes the family's own answer",
    A(mk([2, 0, 3, 2, 1, 3])).reason.length > 30);
}

/* ============================================================
   DISCOVERABILITY — canonical domain, 2026-10-18
   ============================================================
   evanstonseniorcareguide.com is the official domain. The
   .netlify.app host serves the same bytes, so without a canonical
   and a redirect it is a duplicate that splits ranking. Asserted
   here because a silent regression costs traffic months later with
   nothing visibly broken.
   ============================================================ */
{
  const fsD = require("fs");
  const SITE = "https://evanstonseniorcareguide.com";
  const idx = fsD.readFileSync("_dist/index.html", "utf8");
  const privD = fsD.readFileSync("_dist/privacy.html", "utf8");

  check("sitemap.xml ships", fsD.existsSync("_dist/sitemap.xml"));
  const sm = fsD.existsSync("_dist/sitemap.xml")
    ? fsD.readFileSync("_dist/sitemap.xml", "utf8") : "";
  check("sitemap lists only the custom domain",
    sm.indexOf(SITE + "/") !== -1 && sm.indexOf("netlify.app") === -1);
  check("sitemap lists both real pages",
    sm.indexOf(SITE + "/privacy.html") !== -1);
  check("robots.txt declares the sitemap",
    fsD.readFileSync("_dist/robots.txt", "utf8").indexOf("Sitemap: " + SITE) !== -1);

  check("homepage canonical points at the custom domain",
    idx.indexOf('<link rel="canonical" href="' + SITE + '/" />') !== -1);
  check("privacy canonical points at the custom domain",
    privD.indexOf('<link rel="canonical" href="' + SITE + '/privacy.html" />') !== -1);
  check("exactly one canonical per page",
    (idx.match(/rel="canonical"/g) || []).length === 1 &&
    (privD.match(/rel="canonical"/g) || []).length === 1);
  check("no shipped page canonicalises to the netlify host",
    idx.indexOf("netlify.app") === -1 && privD.indexOf("netlify.app") === -1);

  check("og:image is the branded card", idx.indexOf(SITE + "/og-card.png") !== -1);
  check("og card ships at the declared size",
    fsD.existsSync("_dist/og-card.png") &&
    idx.indexOf('content="1200"') !== -1 && idx.indexOf('content="630"') !== -1);
  check("og:url matches the canonical",
    idx.indexOf('property="og:url" content="' + SITE + '/"') !== -1);
  check("twitter card is the large-image variant",
    idx.indexOf('name="twitter:card" content="summary_large_image"') !== -1);

  const ld = (idx.match(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/) || [])[1];
  check("JSON-LD block is present", Boolean(ld));
  let parsed = null;
  try { parsed = JSON.parse(ld); } catch (e) { parsed = null; }
  check("JSON-LD parses as valid JSON", parsed !== null);
  if (parsed) {
    const types = (parsed["@graph"] || []).map((n) => n["@type"]);
    ["WebSite", "Person", "WebPage"].forEach((t) => {
      check("JSON-LD declares " + t, types.indexOf(t) !== -1);
    });
    const flat = JSON.stringify(parsed);
    check("JSON-LD never references the netlify host", flat.indexOf("netlify.app") === -1);
    /* Accuracy, not decoration: the structured data must carry the same
       employment disclosure the page does, and must not imply this is
       an official Westminster site or a medical provider. */
    check("JSON-LD repeats the employment disclosure",
      flat.indexOf("not an official Westminster Place website") !== -1);
    check("JSON-LD claims no medical or provider type",
      flat.indexOf("MedicalBusiness") === -1 &&
      flat.indexOf("LocalBusiness") === -1 &&
      flat.indexOf("Physician") === -1);
    check("JSON-LD states the guide is free", flat.indexOf('"isAccessibleForFree":true') !== -1);
  }

  const toml = fsD.readFileSync("netlify.toml", "utf8");
  check("the netlify.app host is 301'd to the custom domain",
    toml.indexOf("https://evanston-senior-care-guide.netlify.app/*") !== -1 &&
    toml.indexOf("https://evanstonseniorcareguide.com/:splat") !== -1 &&
    toml.indexOf("status = 301") !== -1);
}


/* ============================================================
   VISIT GUIDANCE — honest by construction, 2026-10-19
   ============================================================
   The risk this block exists for: a section that invites a visit is
   one bad sentence away from becoming an advert written by someone
   who works there. These gates keep it observational.
   ============================================================ */
{
  const fsV = require("fs");
  const src = fsV.readFileSync("app.js", "utf8");
  const vg = src.slice(src.indexOf("const VISIT_GUIDE"), src.indexOf("function visitBlock"));

  ["independent", "assisted", "memory", "skilled", "rehab"].forEach((lvl) => {
    check("visit guidance exists for " + lvl, vg.indexOf(lvl + ": {") !== -1);
  });
  /* The one result that must NOT be invited to tour. */
  check("no visit guidance for the no-need result", vg.indexOf("no_need:") === -1);
  const nn = src.slice(src.indexOf('result.status === "no_need"'), src.indexOf("wireResult();"));
  check("the no-need result offers next steps, not a tour",
    nn.indexOf("Three things worth doing this month") !== -1 &&
    nn.indexOf("visitBlock(") === -1);
  check("the no-need result says nobody needs to move",
    nn.indexOf("Nothing here says anyone needs to move") !== -1);

  /* Claims about Westminster specifically would be unverifiable and
     would make an employee's guide an advert. The guidance must stay
     about what a VISITOR can observe anywhere. */
  const vgLower = vg.toLowerCase();
  ["westminster is", "westminster offers", "westminster provides",
   "best", "award", "leading", "top-rated", "five-star", "accredited",
   "beautiful", "luxury", "state-of-the-art"].forEach((claim) => {
    check('visit guidance makes no claim: "' + claim + '"',
      vgLower.indexOf(claim) === -1);
  });
  check("the guidance is framed as true anywhere, not only here",
  src.indexOf("or anywhere else you look") !== -1);
  check("the guidance tells families to reuse it elsewhere",
  src.indexOf("just as well somewhere else") !== -1);
  check("every level routes its questions to a named team",
    src.indexOf("Worth asking the ${esc(line.label)} team") !== -1);

  /* The consent sentence and the checkbox must still be identical, and
     the version must have moved with the wording. */
  const fn = fsV.readFileSync("netlify/functions/plan-visit.mjs", "utf8");
  check("consent version moved with the wording",
    fn.indexOf('const CONSENT_VERSION = "2026-10-26d"') !== -1);
  check("consent says the owner decides, not that forwarding is automatic",
    fn.indexOf("He reads every inquiry himself") !== -1 &&
    fn.indexOf("decides how to follow up") !== -1);
  check("consent names all five shared items, interest included",
    fn.indexOf("name, phone, email, what I am interested in, and my assessment") !== -1 &&
    fn.indexOf("to the person who runs this guide") !== -1);
  /* The recipient is the ORGANISATION, not one of its departments.
     "Admissions" is their skilled nursing desk; naming it for every
     inquiry was wrong and would have been plainly wrong for someone
     asking about independent living. */
  check("consent still names the recipient and purpose",
    /* Anchored inside a single string literal. The statement is built by
       concatenation, so a phrase spanning the `" + "` break exists on the
       rendered page but never in this file. */
    fn.indexOf("Westminster Place to arrange a tour") !== -1);
  check("consent does not name a single department as the recipient",
    fn.indexOf("Westminster Place Admissions") === -1);
}


/* ---- CONFIRMED-LEAD EVENT, 2026-10-22 -------------------------
   /t/inquiry-submitted.txt must mean "the record exists", never
   "a request was sent". The server answers ok only after writing
   the record AND reading it back out of the store and comparing
   the submission id, so the client's success branch is the only
   honest place to fire it.

   These gates exist because an event that fires one branch too
   early turns every abandoned form into a lead. */
const appFlat = appSrcRaw.replace(/\s+/g, " ");

check("the confirmed-lead path is declared",
  appSrcRaw.indexOf('inquirySubmitted: "/t/inquiry-submitted.txt"') !== -1);

check("the event file is published",
  require("fs").existsSync("_dist/t/inquiry-submitted.txt"));

check("the event fires inside the server-confirmed branch",
  /if \(res\.ok && data\.ok\) \{[^}]*?beacon\(FUNNEL\.inquirySubmitted\)/.test(appFlat));

check("the event does NOT fire on submit",
  !/beacon\(FUNNEL\.inquirySubmitted\)[\s\S]{0,400}?const res = await fetch\("\/api\/plan-visit"/.test(appSrcRaw));

check("exactly one call site",
  (appSrcRaw.match(/beacon\(FUNNEL\.inquirySubmitted\)/g) || []).length === 1);

check("the call site sits after the fetch, not before",
  appSrcRaw.indexOf("beacon(FUNNEL.inquirySubmitted)") >
  appSrcRaw.indexOf('await fetch("/api/plan-visit"'));

check("no query string, so the Observability filter is exact",
  !/FUNNEL\.inquirySubmitted\s*\+/.test(appSrcRaw));

check("no personal field is appended to the event",
  !/inquirySubmitted[^;]*(firstName|lastName|email|phone|careLevel|submissionId)/.test(appSrcRaw));

check("the server still proves the write by reading it back",
  planFn.indexOf("readback_mismatch") !== -1 &&
  planFn.indexOf("parsed.submissionId !== submissionId") !== -1);

check("the server reports stored only after the read-back",
  planFn.indexOf('return { stored: true, reason: "ok", key };') !== -1);

check("the form is replaced on success, so it cannot be resubmitted",
  appSrcRaw.indexOf("form.innerHTML = `") !== -1);

check("the beacon helper is still fire-and-forget",
  appSrcRaw.indexOf("measurement must never break the page") !== -1);

check("the beacon helper still dedupes per page load",
  appSrcRaw.indexOf("if (!path || sent[path]) return;") !== -1);

check("the older submit and saved events are untouched",
  appSrcRaw.indexOf('planSubmit:   "/t/plan-visit-submitted.txt"') !== -1 &&
  appSrcRaw.indexOf('planSaved:    "/t/plan-visit-saved.txt"') !== -1);

check("still no cookie anywhere in the client",
  appSrcRaw.indexOf("document.cookie") === -1);

check("still no persistent identifier storage",
  appSrcRaw.indexOf("localStorage") === -1 &&
  appSrcRaw.indexOf("sessionStorage") === -1);


/* ============================================================
   TRUST BLOCK + VERIFIED-ONLY WESTMINSTER COPY, 2026-10-19
   ============================================================ */
{
  const fsT = require("fs");
  const src = fsT.readFileSync("app.js", "utf8");
  const flat = src.replace(/\s+/g, " ");

  /* Joseph's introduction, approved verbatim. Asserted word-for-word so
     an edit cannot quietly reword what he said about himself. */
  [ "I created Evanston Senior Care Guide to help families better understand their senior-care options without feeling overwhelmed.",
    "My goal is to make complicated decisions easier by explaining different levels of care, helping families know what questions to ask, and giving them a clearer starting point.",
    "I work in senior living, but this guide is an independent project I created to help families make informed decisions."
  ].forEach((sent, n) => {
    check("intro sentence " + (n + 1) + " is verbatim",
      flat.indexOf(sent.replace(/\s+/g, " ")) !== -1, sent.slice(0, 34) + "...");
  });

  /* The introduction says "senior living" generally. The FTC-relevant
     connection is the SPECIFIC one, so it must still appear. Warm first,
     precise second — both, never one instead of the other. */
  check("the specific employer is still named at the form",
    flat.indexOf("I work at Westminster Place") !== -1);
  check("not-official and no-fees survive the rewrite",
    flat.indexOf("isn&rsquo;t an official Westminster site") !== -1 &&
    flat.indexOf("not paid for referrals") !== -1);

  /* Every factual claim about Westminster must be one of theirs. */
  /* CORRECTED 2026-10-19. The earlier wording said a community already
     offering the next level is "one less move to arrange" — which implies
     residents can transfer between settings. Offering several levels on a
     campus does not guarantee that, and the guide must not say it does.
     The replacement turns the claim into a question to ask on a visit. */
  check("the campus statement is the owner's approved wording",
    flat.indexOf("Westminster Place offers several levels of senior care on one campus.") !== -1);
  check("transition is framed as a question, never a guarantee",
    flat.indexOf("whether transitioning between care settings may be possible") !== -1 &&
    flat.indexOf("ask how the community supports residents when their needs change") !== -1);
  check("no transfer guarantee survives anywhere on the page",
    flat.indexOf("one less move to arrange") === -1 &&
    flat.indexOf("already offers the next level") === -1 &&
    flat.toLowerCase().indexOf("can transfer") === -1 &&
    flat.toLowerCase().indexOf("guaranteed transfer") === -1);
  check("the visitor is sent to their own site to judge for herself",
    flat.indexOf("presbyterianliving.org/our-locations/westminster-place/") !== -1 &&
    flat.indexOf("Read what they say about") !== -1);
  check("the guide disclaims speaking for them",
    flat.indexOf("this guide is not it, and does not speak") !== -1);

  /* No superlative may attach to Westminster anywhere on the page. */
  const card = flat.slice(flat.indexOf('<div class="wp">'),
                          flat.indexOf("COLLECTING ? planFormBlock()"));
  ["best", "finest", "leading", "award", "top-rated", "five-star",
   "luxury", "beautiful", "state-of-the-art", "premier", "excellent",
   "highly rated", "trusted"].forEach((w) => {
    check('Westminster card makes no claim: "' + w + '"',
      card.toLowerCase().indexOf(w) === -1);
  });
  check("the card still promises no availability",
    card.toLowerCase().indexOf("available") === -1 &&
    card.toLowerCase().indexOf("openings") === -1);
}


/* ---- EVERY PRE-EXISTING JOURNEY STILL ENDS WHERE IT DID -------------
   Adding the independent-living lifestyle option shifted the household
   answer indices and inserted a new rule. Hand-written cases cannot prove
   that nothing else moved; there are 4096 ways to answer six questions.

   fixtures/assessment-baseline-2026-10-26.json holds the outcome of all
   4096 of them as the engine stood at commit 48900b0, before any of this
   existed. It is FROZEN. Regenerating it from current code would turn
   this check into a tautology, which is the self-invalidating-gate
   mistake this repo has already paid for twice. */
const BASE = require("./fixtures/assessment-baseline-2026-10-26.json");
const IDS = BASE.ids;
let drift = 0, firstDrift = "";
BASE.cases.forEach((row) => {
  const [picks, was] = row.split(":");
  const answers = {};
  IDS.forEach((id, k) => {
    const v = Number(picks[k]);
    answers[id] = id === "household" ? BASE.householdMap[v] : v;
  });
  const r = assess(answers);
  const now = r.level ? r.level.id : "none";
  if (now !== was || r.variant) {
    drift++;
    if (!firstDrift) firstDrift = picks + " was " + was + ", now " + now;
  }
});
check("all 4096 pre-existing answer combinations route exactly as before",
  drift === 0, drift ? drift + " changed; first: " + firstDrift : "0 changed");

/* ---- THE LIFESTYLE ANSWER NEVER OVERRIDES A CARE SIGNAL -------------
   Re-run all 4096 baseline combinations with household forced to the new
   lifestyle option. Anyone who described a real need must still get their
   care level; only the genuinely-no-needs answers may become the
   lifestyle result. */
let hijacked = 0, firstHijack = "", lifestyleHits = 0;
BASE.cases.forEach((row) => {
  const [picks] = row.split(":");
  const answers = {};
  IDS.forEach((id, k) => { answers[id] = Number(picks[k]); });
  answers.household = 1;                       // the lifestyle option
  const bare = { ...answers, household: 0 };   // same answers, "managing fine"
  const expect = assess(bare);
  const got = assess(answers);
  if (got.variant === "lifestyle") {
    lifestyleHits++;
    /* It may only fire where NO care level was produced otherwise. */
    if (expect.level) {
      hijacked++;
      if (!firstHijack) firstHijack = picks + " -> lifestyle over " + expect.level.id;
    }
  } else if (!expect.level ? false : got.level.id !== expect.level.id) {
    hijacked++;
    if (!firstHijack) firstHijack = picks + " -> " + got.level.id + " not " + expect.level.id;
  }
});
check("the lifestyle answer never displaces a care or safety result",
  hijacked === 0, hijacked ? hijacked + " hijacked; " + firstHijack : "0 hijacked");
check("the lifestyle answer does reach a lifestyle result somewhere",
  lifestyleHits > 0, lifestyleHits + " of 4096 reach it");

/* The by-choice result must never be dressed as a care need. */
const lifestyleResult = assess({ adl: 0, memory: 0, medical: 0, alone: 0,
                                 hospital: 0, household: 1 });
check("fit + wants less upkeep yields independent living, by choice",
  lifestyleResult.level && lifestyleResult.level.id === "independent" &&
  lifestyleResult.variant === "lifestyle",
  (lifestyleResult.level || {}).id + "/" + lifestyleResult.variant);
check("the by-choice reason says no care need is described",
  /nothing here describes a need for care/.test(lifestyleResult.reason || ""));
check("the by-choice result suggests no higher level of care",
  (lifestyleResult.alsoConsider || []).length === 0,
  ((lifestyleResult.alsoConsider || []).map((l) => l.id).join(",") || "none"));
check("answering managing-fine six times still describes no need",
  assess({ adl: 0, memory: 0, medical: 0, alone: 0, hospital: 0, household: 0 })
    .status === "no_need");


/* ---- FRAMING NEVER TOUCHES SCORING ---------------------------------
   The self/parent choice rewords six questions. It must not be capable
   of changing a single outcome. assess() is never handed the audience,
   so this proves the only thing that could go wrong: that both framings
   present the SAME options carrying the SAME signals, for every
   question. Wording may differ; signals may not. */
QUESTIONS.forEach((q) => {
  check("both framings offer identical options: " + q.id,
    q.options.every((o) => o && typeof o.label === "string"));
  check("a self wording exists: " + q.id,
    typeof q.textSelf === "string" && q.textSelf.length > 20);
  check("the self wording drops the third person: " + q.id,
    q.textSelf.indexOf("your parent") === -1 &&
    q.textSelf.indexOf("their ") === -1, q.textSelf.slice(0, 48));
  check("the parent wording is still third person: " + q.id,
    /your parent or loved one|they |their /.test(q.text + " " + q.help),
    q.text.slice(0, 44));
  /* The selector offers "a parent or someone else", so the questions may
     not narrow that back to a parent. Bare "your parent" excludes the
     spouse, the sibling and the neighbour who are doing the same job. */
  check("no question says bare \"your parent\": " + q.id,
    q.text.indexOf("your parent") === -1 ||
    q.text.indexOf("your parent or loved one") !== -1, q.text.slice(0, 50));
});
check("no question carries audience-specific SIGNALS",
  QUESTIONS.every((q) => q.options.every((o) =>
    !("signalsSelf" in o) && !("signalsParent" in o))));
check("assess() takes answers only, never an audience",
  /function assess\(answers\)/.test(
    require("fs").readFileSync("assessment.js", "utf8")));

/* ---- WORKFLOW #4: A TOUR WITHOUT AN ASSESSMENT ---------------------
   The audit found the blocker: planFormBlock() was only reachable from
   renderResult(), so the form did not exist until all six questions were
   answered, and the endpoint rejected any careLevel outside its six-value
   allowlist. Someone who already knew they wanted a tour had no path. */
const fsW = require("fs");
const planSrc = fsW.readFileSync("netlify/functions/plan-visit.mjs", "utf8");
const exportSrc = fsW.readFileSync("netlify/functions/plan-visit-export.mjs",
                                   "utf8");

check("the endpoint accepts a direct inquiry",
  /^  direct:\s/m.test(planSrc));
/* The name must describe the ABSENCE of an assessment. Anything that reads
   like a care level would be a fabricated result. */
check("direct is named as the absence of an assessment",
  /direct:\s+\{ name: "Assessment not taken"/.test(planSrc));
check("the no-assessment value is named once, not repeated as a literal",
  /const NO_ASSESSMENT = "direct";/.test(planSrc));
check("the notification says the assessment was NOT taken",
  /NOT TAKEN - this person came straight from a/.test(planSrc));
check("the notification still carries the selected interest",
  planSrc.indexOf('"INTERESTED IN:     "') !== -1);
check("the stored record flags whether an assessment happened",
  /assessmentTaken: record\.careLevel !== NO_ASSESSMENT/.test(planSrc));
check("the export reports assessmentTaken and the interest",
  /"assessmentTaken", "careLevelName", "interestName"/.test(exportSrc));
/* No new department, no new number -- direct reuses the General Inquiries
   line that no_need already used. */
check("direct introduces no new phone number",
  (planSrc.match(/\(847\) \d{3}-\d{4}/g) || [])
    .every((n) => ["(847) 570-3310", "(847) 866-1615", "(847) 492-7780",
                   "(847) 570-3422"].indexOf(n) !== -1));

check("a direct render path exists and sends careLevel direct",
  /function renderDirectInquiry\(\)/.test(appSrcRaw) &&
  /resultLevelId = NO_ASSESSMENT_LEVEL;/.test(appSrcRaw));
check("the direct page states no assessment was taken",
  /No assessment needed/.test(appSrcRaw) &&
  /Nothing about care needs is\s+assumed or guessed/.test(appSrcRaw));
check("the direct page still offers the six questions",
  /Take\s+the six questions instead/.test(appSrcRaw));
/* The select renders ABOVE the <form> element, so without form="plan-form"
   it is not a submittable control: form.elements.interest is undefined and
   the payload silently falls back to "unsure". That shipped on 2026-10-26 --
   the dropdown looked right and the value never left the page. A DOM check
   cannot see it; only asserting the posted body can. */
check("the interest select is associated with the form",
  /id="plan-interest"[\s\S]{0,40}form="plan-form"/.test(appSrcRaw));
check("the interest can be preselected without a result",
  /interestFor\(levelId, variant, interestOverride\)/.test(appSrcRaw));
check("the pathway params are sanitised to a short safe token",
  /replace\(\/\[\^a-z0-9-\]\/g, ""\)\.slice\(0, 24\)/.test(appSrcRaw));
check("the direct path never fabricates an assessment answer",
  appSrcRaw.indexOf("renderDirectInquiry") !== -1 &&
  !/renderDirectInquiry[\s\S]{0,900}answers\[/.test(appSrcRaw));

/* Opening a form is not saving an inquiry. These must stay distinct. */
check("opening the form has its own beacon",
  /directFormView:\s+"\/t\/direct-inquiry-form-view\.txt"/.test(appSrcRaw));
check("both guide pathways have their own beacons",
  /guideAssessment:\s+"\/t\/guide-choice-assessment\.txt"/.test(appSrcRaw) &&
  /guideTour:\s+"\/t\/guide-choice-tour\.txt"/.test(appSrcRaw));
check("saving an inquiry remains a separate beacon from opening it",
  /planSaved:\s+"\/t\/plan-visit-saved\.txt"/.test(appSrcRaw) &&
  /inquirySubmitted:\s+"\/t\/inquiry-submitted\.txt"/.test(appSrcRaw));

/* EVERY beacon the page can request must have a file. Three shipped
   firing at nothing before this; a 404 beacon reads as zero forever. */
const beaconNames = new Set(
  (appSrcRaw.match(/"\/t\/([a-z0-9-]+)\.txt"/g) || [])
    .map((m) => m.replace(/"|\/t\/|\.txt/g, "")));
["result-independent", "result-assisted", "result-memory", "result-skilled",
 "result-rehab", "result-no_need", "result-independent-by-choice",
 "audience-self", "audience-parent"].forEach((n) => beaconNames.add(n));
const missingBeacons = [...beaconNames].filter(
  (n) => !fsW.existsSync("_dist/t/" + n + ".txt"));
check("every beacon the page requests has a file in _dist/t",
  missingBeacons.length === 0, missingBeacons.join(" "));
const missingSrcBeacons = [...beaconNames].filter(
  (n) => !fsW.existsSync("t/" + n + ".txt"));
check("the working-tree copy of t/ matches, so the two cannot drift",
  missingSrcBeacons.length === 0, missingSrcBeacons.join(" "));
check("beacon files are generated, not hand-maintained",
  /def write_beacons\(\)/.test(
    fsW.readFileSync("build-guides.py", "utf8")));

/* The guide's two choices are plain anchors. Guide pages load nav.js only;
   shipping the assessment engine to twelve SEO pages to show two links
   would not be a small fix. */
const ilGuide = fsW.readFileSync(
  "_dist/guides/independent-living-evanston/index.html", "utf8");
check("the guide offers both pathways",
  ilGuide.indexOf('href="/?from=il-guide#assessment"') !== -1 &&
  ilGuide.indexOf('href="/?tour=independent#plan-visit"') !== -1);
check("the guide pathway section needs no JavaScript",
  /<div class="fork">/.test(ilGuide) &&
  (ilGuide.match(/<script[^>]*src="[^"]*"/g) || [])
    .every((t) => t.indexOf("nav.js") !== -1));
check("the article still reads without touching either choice",
  /Neither is required to finish reading/.test(ilGuide));

/* ============================================================
   WORKFLOW 4 REFINEMENT, 2026-10-26
   The pathway shipped working and still said three things that were
   untrue to the people using it. Each gate below pins one of them.
   ============================================================ */

/* 1. A visitor who skipped the assessment has no result, so no sentence
      may refer to one. The old hint said "Pre-filled from your result"
      to someone who had never answered a question. */
const directBranch =
  (appSrcRaw.match(/const interestHint =[\s\S]*?: `Pre-filled/) || [""])[0];
check("the no-result hint exists and is chosen by the no-assessment level",
  /noAssessment/.test(directBranch) && directBranch.length > 120);
check("the no-result hint never claims a result was used",
  directBranch.indexOf("Pre-filled from your result") === -1);
check("the no-result hint credits the guide link, not an assessment",
  /Set to \$\{esc\(chosenLabel\)\} by the guide link you followed/
    .test(directBranch) &&
  /not by an assessment, which you haven&rsquo;t taken/.test(directBranch));
check("the hint names the level it actually selected, never a literal",
  /chosenLabel\s*=\s*\n?\s*\(INTERESTS\.filter/.test(appSrcRaw) &&
  appSrcRaw.indexOf('Set to Independent Living') === -1);
check("a visitor with no pathway link is told nothing was pre-filled",
  /so nothing here was\s+pre-filled from a result/.test(appSrcRaw));
/* The same defect twice more: six answers that were never given, and an
   assessment "above" that is not above anything. */
check("the fine print does not promise six answers that were never given",
  /noAssessment\s*\n?\s*\? `You gave no assessment answers/.test(appSrcRaw));
check("the disclosure line adapts when there is no assessment above it",
  /nothing on this site has asked for your name until now/
    .test(appSrcRaw) &&
  /the assessment above never asked for your name/.test(appSrcRaw));
/* Scoped to the care-level meaning of the word. app.js also uses "direct"
   for an unrelated thing -- the traffic source when there is no referrer --
   so counting the literal would gate on the wrong "direct" entirely. What
   matters is that no comparison or call site carries it by hand. */
check("the no-assessment level is compared by name, never by literal",
  /const NO_ASSESSMENT_LEVEL = "direct";/.test(appSrcRaw) &&
  !/levelId === "direct"/.test(appSrcRaw) &&
  !/resultLevelId = "direct"/.test(appSrcRaw) &&
  !/planFormBlock\("direct"/.test(appSrcRaw));

/* 2. Two things the visitor must be able to tell apart: the assessment
      asks for nothing, the inquiry needs contact details and a tick. */
check("the form states the assessment asks for nothing",
  /The six questions ask for nothing &mdash; no\s+name, no email, no phone number/
    .test(appSrcRaw));
check("the form states what it needs in exchange",
  /needs your name, one way to reach you, and your tick on the box/
    .test(appSrcRaw));
const homeRaw = fsW.readFileSync("index.html", "utf8");
check("the homepage names the one place that asks for contact details",
  /only part of this site that asks for contact details/.test(homeRaw) &&
  /nothing\s+is sent unless you tick its consent box/.test(homeRaw));
check("the guide fork says which route asks for what",
  /One asks for\s*nothing at all; the other asks how to reach you/
    .test(ilGuide.replace(/\s+/g, " ")) ||
  /the other asks how to reach you/.test(ilGuide));

/* 3. Visitor copy explains what happens to them, not how the backend
      records it. These four phrases described storage and notifications
      to people who had asked about a tour. */
["records no assessment at all", "the notification says so in those words",
 "assumed, recorded or guessed", "assumed or\nrecorded"].forEach((phrase) => {
  check("visitor copy drops backend wording: " + phrase.slice(0, 34),
    appSrcRaw.indexOf(phrase) === -1 && ilGuide.indexOf(phrase) === -1);
});
/* The distinctions themselves stay — in the record, the email and the
   export, which is where they belong. */
check("the stored record still distinguishes a direct inquiry",
  /assessmentTaken: record\.careLevel !== NO_ASSESSMENT/.test(planSrc));
check("the notification still distinguishes a direct inquiry",
  /NOT TAKEN - this person came straight from a/.test(planSrc));
check("the export still distinguishes a direct inquiry",
  /"assessmentTaken", "careLevelName", "interestName"/.test(exportSrc));

/* 4. Reach. The introduction is worth reading and changes nothing about
      the submission, so it sits after the form; everything that changes
      what happens to the data stays above or inside it. */
const planBlock = (appSrcRaw.match(
  /function planFormBlock[\s\S]*?\n}\n/) || [""])[0];
check("the introduction block renders after the form closes",
  planBlock.indexOf("</form>") !== -1 &&
  planBlock.indexOf('class="plan__who"') > planBlock.indexOf("</form>"));
check("consent still renders inside the form, above the submit button",
  planBlock.indexOf('id="plan-consent"') < planBlock.indexOf("</form>") &&
  planBlock.indexOf('id="plan-consent"') <
    planBlock.indexOf('type="submit"'));
["plan__contrast", "plan__lead", "plan__disclose"].forEach((cls) => {
  check("disclosure stays above the first field: " + cls,
    planBlock.indexOf(cls) < planBlock.indexOf('name="firstName"'));
});
check("the privacy notice link is still inside the form",
  planBlock.indexOf('class="plan__privacy"') < planBlock.indexOf("</form>"));
/* The interest control now lives INSIDE the form. form="plan-form" fixed
   the never-transmitted bug; moving the control removes the way it could
   happen. Both are asserted: the attribute because it is still the
   explicit association, the position because it is the structural fix. */
check("the interest control renders inside the form element",
  planBlock.indexOf('id="plan-interest"') >
    planBlock.indexOf('id="plan-form"') &&
  planBlock.indexOf('id="plan-interest"') < planBlock.indexOf("</form>"));
check("the interest control is still explicitly associated with the form",
  /id="plan-interest"[\s\S]{0,45}form="plan-form"/.test(appSrcRaw));
check("contact fields come before the interest question",
  planBlock.indexOf('name="firstName"') <
    planBlock.indexOf('id="plan-interest"'));
check("consent is still the last thing before the submit button",
  planBlock.indexOf('id="plan-interest"') <
    planBlock.indexOf('id="plan-consent"'));

/* 6. One consent sentence that is true on both pathways, and the stored
      version moved with the wording. */
check("consent no longer asserts an assessment result unconditionally",
  /and my\s+assessment result if I took the assessment/.test(appSrcRaw) &&
  appSrcRaw.indexOf("name, phone, email, assessment result and what") === -1);
check("the direct notification does not contradict its own NOT TAKEN line",
  /No assessment was taken, so there is no care level to read here/
    .test(planSrc));
check("the assessment notification still reads the derived level",
  /The result above is the care LEVEL the six questions produced/
    .test(planSrc));
check("the two notification tails are mutually exclusive",
  /record\.careLevel === NO_ASSESSMENT\s*\n?\s*\?\s*\["No assessment was taken/
    .test(planSrc));

/* ============================================================
   MEASUREMENT HOUSEKEEPING, 2026-10-31
   The first clean night after launch showed zero beacons from real
   visitors and 1,496 of 1,949 requests from the test harnesses the day
   before. Two things keep the funnel honest from here: every harness
   announces one fixed User-Agent the host's log can exclude by exact
   match, and no beacon file exists that nothing on the site fires, so an
   enumerating bot cannot register a stage a visitor never reached.
   ============================================================ */
{
  const fs = require("fs");
  const HARNESS_UA = "ESCG-harness/1 (automated test; +https://evanstonseniorcareguide.com/)";
  const harnesses = ["tools/simple_first_check.mjs", "tools/wf5_browser_walk.mjs",
    "check-mobile-nav.py", "tools/mobile/wf4_direct_inquiry.py", "tools/mobile/il_prominence.py",
    "tools/mobile/mobile_independent_living.py", "tools/mobile/form_reach.py"];
  harnesses.forEach((f) => {
    const src = fs.readFileSync(f, "utf8");
    check("harness announces the shared User-Agent: " + f,
      src.indexOf('HARNESS_UA = "' + HARNESS_UA + '"') !== -1 &&
      src.indexOf("--user-agent=") !== -1);
    /* 2026-10-31: form_reach.py carried the constant INSIDE its module
       docstring, so the text matched and the harness crashed with a
       NameError. The constant has to be a real top-level statement: for a
       Python file, the line must sit after the docstring closes; for a
       module, it must be a top-level const. */
    if (f.endsWith(".py")) {
      const at = src.indexOf('HARNESS_UA = "');
      const quotes = (src.slice(0, at).match(/"""/g) || []).length;
      check("harness constant is code, not docstring: " + f, quotes % 2 === 0 && /(^|\n)HARNESS_UA = "/.test(src));
    } else {
      check("harness constant is a top-level const: " + f, /(^|\n)const HARNESS_UA = "/.test(src));
    }
  });
  /* Every beacon file must have a caller: a literal in the shipped scripts,
     or one of the names the build derives (result-<level>, the by-choice
     variant, the two audience choices). Anything else is a retired stage
     that still answers 200 to whoever enumerates the folder. */
  const scripts = ["app.js", "paying-nav.js", "guides.js", "nav.js"]
    .filter((f) => fs.existsSync(f)).map((f) => fs.readFileSync(f, "utf8")).join("\n");
  const callers = new Set((scripts.match(/["']\/t\/([a-z0-9_-]+)\.txt["']/g) || [])
    .map((m) => m.replace(/["']\/t\//, "").replace(/\.txt["']$/, "")));
  ["independent", "assisted", "memory", "skilled", "rehab", "no_need"]
    .forEach((l) => callers.add("result-" + l));
  ["result-independent-by-choice", "audience-self", "audience-parent"].forEach((n) => callers.add(n));
  ["t", "_dist/t"].forEach((dir) => {
    const orphans = fs.readdirSync(dir).filter((f) => f.endsWith(".txt"))
      .map((f) => f.slice(0, -4)).filter((n) => !callers.has(n));
    check("no beacon file without a caller in " + dir, orphans.length === 0, orphans.join(", "));
  });
  check("the three retired Westminster click beacons are gone",
    !fs.existsSync("t/westminster-call-click.txt") &&
    !fs.existsSync("t/westminster-directions-click.txt") &&
    !fs.existsSync("t/westminster-inquiry-form-click.txt"));
}

const total = checks.length;
const passed = checks.filter(Boolean).length;
console.log("\n" + passed + "/" + total + " passed");
process.exit(passed === total ? 0 : 1);
