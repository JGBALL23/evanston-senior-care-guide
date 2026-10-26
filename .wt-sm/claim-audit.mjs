/* ============================================================
   CLAIM AUDIT  —  node claim-audit.mjs
   ============================================================
   The standard: every factual claim a family, a nurse or an
   executive could challenge must be either (a) sourced, or
   (b) hedged so it is not a claim at all.

   This pulls every number and every absolute statement out of
   the SHIPPED copy — index.html body and the assessment engine —
   and prints them for a human to read. It is a magnifying glass,
   not a gate: it does not decide what is defensible, it makes
   sure nothing is defended by being overlooked.

   The citations block is excluded on purpose: it lists sources,
   it does not make claims.
   ============================================================ */
import { readFileSync } from "node:fs";

const html = readFileSync("index.html", "utf8");
const body = html.replace(/<details class="src"[\s\S]*?<\/details>/, " ");
const pageText = body
  .replace(/<script[\s\S]*?<\/script>/g, " ")
  .replace(/<style[\s\S]*?<\/style>/g, " ")
  .replace(/<[^>]+>/g, " ")
  .replace(/&mdash;/g, "—").replace(/&rsquo;/g, "’")
  .replace(/&ldquo;|&rdquo;/g, '"').replace(/&amp;/g, "&")
  .replace(/&[a-z]+;/g, " ")
  .replace(/\s+/g, " ")
  .trim();

const { CARE_LEVELS, QUESTIONS } = await import("./assessment.js").then(
  (m) => m.default || m, () => ({}));

const engineText = Object.values(CARE_LEVELS || {})
  .map((l) => [l.summary, (l.looksLike || []).join(" "), (l.nextSteps || []).join(" "),
    l.cost ? [l.cost.label, l.cost.basis, l.cost.survey, l.cost.note].join(" ") : ""].join(" "))
  .join(" ");

const sentences = (text) => text.split(/(?<=[.?!])\s+/).filter((s) => s.trim().length > 3);

/* ---- 1. every number that behaves like a statistic ----
   Spelled-out numbers were in the first version and buried the real
   findings under prose: "four kinds of care", "six questions", "one
   more". A word is not a statistic. Only currency, percentages and
   multi-digit figures are hunted now — those are the claims a nurse
   or an executive can look up and contradict. */
const NUMBER = /\$[0-9][0-9,]*(?:\.[0-9]{2})?|\b[0-9]+(?:\.[0-9]+)?\s?%|\b[0-9]{3,}\b/;
const SOURCED_NEAR = /carescout|medicare|medicaid|illinois hfs|hfs|idph|dph\.illinois|survey|median|published 20|part a/i;
const HEDGED = /\bmay\b|\busually\b|\btypically\b|\boften\b|\bgenerally\b|\bcan\b|\bvaries\b|\bdepends\b|\bestimate|\babout\b|\broughly\b|\bapproximately\b/i;

function audit(label, text) {
  console.log("\n============ " + label + " ============");
  let flagged = 0;
  sentences(text).forEach((s) => {
    const t = s.trim();
    if (!NUMBER.test(t)) return;
    /* A number that sits beside its source, or inside a hedge, is
       not the kind of claim this audit is hunting. */
    const ok = SOURCED_NEAR.test(t) || HEDGED.test(t);
    if (!ok) {
      flagged++;
      console.log("  UNSOURCED+UNHEDGED: " + t.slice(0, 150));
    }
  });
  if (flagged === 0) console.log("  every numeric claim is sourced or hedged");
  return flagged;
}

/* ---- 2. absolute statements that read as fact about a person ---- */
const ABSOLUTE = [
  "always", "never", "guaranteed", "guarantee", "all communities",
  "every community", "no community", "will be", "is the best",
  "proven", "scientifically", "studies show", "research shows",
  "experts agree", "doctors recommend", "clinically"
];

function absolutes(label, text) {
  console.log("\n------------ absolutes: " + label + " ------------");
  let flagged = 0;
  sentences(text).forEach((s) => {
    const t = s.trim();
    const hit = ABSOLUTE.filter((w) => t.toLowerCase().includes(w));
    if (hit.length === 0) return;
    /* A denial is not a claim: "does not guarantee placement" is the
       protection, not a breach of it. */
    if (/\bnot\b|\bno\b|\bnever\s+(?:shared|sent|sold)\b|cannot/i.test(t)) return;
    flagged++;
    console.log("  CHECK [" + hit.join(",") + "]: " + t.slice(0, 140));
  });
  if (flagged === 0) console.log("  no unqualified absolutes");
  return flagged;
}

let total = 0;
total += audit("PAGE BODY", pageText);
total += audit("ASSESSMENT ENGINE", engineText);
total += absolutes("PAGE BODY", pageText);
total += absolutes("ASSESSMENT ENGINE", engineText);

console.log("\n" + (total === 0
  ? "CLAIM AUDIT: nothing to defend that is not already sourced or hedged"
  : "CLAIM AUDIT: " + total + " statement(s) need a human decision"));
