/* ============================================================
   "Assessment not taken" — proven by execution, in all three places
   ============================================================

   A direct tour inquiry has to read as "no assessment happened" in
   three artefacts that are built by three different pieces of code:

     1. the durable record written to Netlify Blobs
     2. the notification email the owner reads
     3. the CSV the export endpoint hands back

   A regex over the source can show the constant is referenced. It
   cannot show the three agree. This runs the real builders from the
   real function source and asserts the output.

   Nothing is posted anywhere. No store, no mail transport, no network:
   the two production modules are copied into a scratch directory with
   their own `export default` handler neutralised, so only the pure
   builders are reachable. The scratch directory is removed afterwards,
   and it is never inside netlify/functions, so nothing here can ever
   be deployed as a function.
   ============================================================ */
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { pathToFileURL } from "node:url";

const FN = "netlify/functions";
const checks = [];
function check(label, ok, detail) {
  checks.push(ok);
  console.log("  " + (ok ? "PASS" : "FAIL") + "  " + label +
    (detail === undefined ? "" : "   " + detail));
}

/* The handler is what talks to the network, so it is what gets removed.
   Named exports are appended instead, which is the only change: the
   builder bodies are the production bodies, byte for byte. */
function probeSource(file, exports) {
  const src = fs.readFileSync(path.join(FN, file), "utf8")
    .replace(/export default async \(request\) => \{/,
             "const __handler_removed = async (request) => {")
    .replace(/export const config = /, "const __config_removed = ");
  if (/export (default|const config)/.test(src)) {
    throw new Error("a live export survived the rewrite in " + file);
  }
  return src + "\nexport { " + exports.join(", ") + " };\n";
}

const dir = fs.mkdtempSync(path.join(os.tmpdir(), "esg-consistency-"));
let mod, exportMod;
try {
  fs.copyFileSync(path.join(FN, "retention.mjs"),
                  path.join(dir, "retention.mjs"));
  const a = path.join(dir, "plan-visit.probe.mjs");
  const b = path.join(dir, "plan-visit-export.probe.mjs");
  fs.writeFileSync(a, probeSource("plan-visit.mjs",
    ["durableRow", "notificationText", "CARE_LEVELS", "NO_ASSESSMENT",
     "INTERESTS", "CONSENT_STATEMENT", "CONSENT_VERSION"]));
  fs.writeFileSync(b, probeSource("plan-visit-export.mjs", ["csvCell"]));
  mod = await import(pathToFileURL(a).href);
  exportMod = await import(pathToFileURL(b).href);

  const AT = "2026-10-26T14:30:00.000Z";
  const ID = "probe-0001";
  const base = {
    firstName: "Dana", lastName: "Okafor",
    email: "dana@example.com", phone: "", consent: true
  };
  const direct = { ...base, careLevel: mod.NO_ASSESSMENT,
                   interest: "independent" };
  const assessed = { ...base, careLevel: "assisted", interest: "memory" };

  /* ---- 1. the stored record ---- */
  const rowD = mod.durableRow(direct, ID, AT);
  const rowA = mod.durableRow(assessed, ID, AT);
  check("storage: a direct row names it 'Assessment not taken'",
    rowD.careLevelName === "Assessment not taken", rowD.careLevelName);
  check("storage: a direct row flags assessmentTaken false",
    rowD.assessmentTaken === false, String(rowD.assessmentTaken));
  check("storage: an assessed row flags assessmentTaken true",
    rowA.assessmentTaken === true, String(rowA.assessmentTaken));
  check("storage: an assessed row keeps its real care level",
    rowA.careLevelName === "Assisted Living", rowA.careLevelName);
  check("storage: a direct row keeps the interest the visitor chose",
    rowD.interestName === "Independent Living", rowD.interestName);
  check("storage: interest and care level stay separate fields",
    rowA.interestName === "Memory Care" &&
    rowA.careLevelName === "Assisted Living",
    rowA.interestName + " / " + rowA.careLevelName);
  check("storage: a direct row introduces no new department or number",
    rowD.admissionsDept === "General Inquiries" &&
    rowD.admissionsPhone === "(847) 570-3422",
    rowD.admissionsDept + " " + rowD.admissionsPhone);
  check("storage: no assessment answer reaches the record",
    !JSON.stringify(rowD).match(/adl|household|alone|mobility|diagnos/i));
  check("storage: the stored consent is the versioned statement",
    rowD.consentStatement === mod.CONSENT_STATEMENT &&
    rowD.consentVersion === mod.CONSENT_VERSION, rowD.consentVersion);
  check("storage: consent wording is true with no assessment",
    /if I took the assessment/.test(rowD.consentStatement));
  check("storage: both paths record the same pre-referral stage",
    rowD.stage === "recorded_tour_inquiry" &&
    rowA.stage === "recorded_tour_inquiry" &&
    rowD.referredToAdmissionsAt === null);

  /* ---- 2. the notification ---- */
  const noteD = mod.notificationText(direct, ID, AT);
  const noteA = mod.notificationText(assessed, ID, AT);
  check("email: a direct inquiry says the assessment was NOT TAKEN",
    /ASSESSMENT:\s+NOT TAKEN/.test(noteD));
  check("email: it says plainly that nothing is known about care needs",
    /Nothing is known about their care needs/.test(noteD));
  check("email: it does NOT also claim a derived care level",
    noteD.indexOf("the care LEVEL the six questions produced") === -1);
  check("email: it points the reader at the one thing they did say",
    /No assessment was taken, so there is no care level/.test(noteD) &&
    /INTERESTED IN:\s+Independent Living/.test(noteD));
  check("email: an assessed inquiry still reports its result",
    /ASSESSMENT RESULT:\s+Assisted Living/.test(noteA) &&
    /the care LEVEL the six questions produced/.test(noteA));
  check("email: an assessed inquiry is not labelled NOT TAKEN",
    noteA.indexOf("NOT TAKEN") === -1);
  check("email: the two tails are mutually exclusive",
    (/NOT TAKEN/.test(noteD) !== /NOT TAKEN/.test(noteA)) &&
    (/six questions produced/.test(noteD) !==
     /six questions produced/.test(noteA)));
  check("email: a direct inquiry routes to the same General Inquiries line",
    /ADMISSIONS TEAM:\s+General Inquiries - \(847\) 570-3422/.test(noteD));
  check("email: neither carries an assessment answer",
    !/\b(adl|household|mobility aid|diagnosis)\b/i.test(noteD + noteA));

  /* ---- 3. the export ---- */
  const header = ["submissionId", "receivedAt", "firstName", "lastName",
    "email", "phone", "assessmentTaken", "careLevelName", "interestName",
    "admissionsDept", "admissionsPhone",
    "source", "stage", "referredToAdmissionsAt"];
  const exportSrc = fs.readFileSync(path.join(FN, "plan-visit-export.mjs"),
                                    "utf8");
  check("export: the header under test is the header in the endpoint",
    header.every((h) => exportSrc.indexOf('"' + h + '"') !== -1) &&
    exportSrc.indexOf('"assessmentTaken", "careLevelName", "interestName"')
      !== -1);
  const csv = (row) => header.map((h) => exportMod.csvCell(row[h])).join(",");
  const lineD = csv(rowD);
  const lineA = csv(rowA);
  check("export: a direct row carries 'Assessment not taken'",
    lineD.indexOf("Assessment not taken") !== -1, lineD.slice(0, 96));
  check("export: a direct row reads false for assessmentTaken",
    lineD.split(",")[6] === "false", lineD.split(",")[6]);
  check("export: an assessed row reads true and names its level",
    lineA.split(",")[6] === "true" &&
    lineA.indexOf("Assisted Living") !== -1);
  check("export: a direct row is not an empty-looking data fault",
    lineD.split(",")[7].trim().length > 0 &&
    lineD.split(",")[8].trim().length > 0,
    lineD.split(",").slice(7, 9).join(" | "));
  check("export: no row exports as un-referred-but-blank",
    lineD.endsWith(",") === false || rowD.referredToAdmissionsAt === null);

  /* ---- the invariant behind all three ---- */
  check("all three derive the distinction from one named constant",
    mod.NO_ASSESSMENT === "direct" &&
    rowD.assessmentTaken === (direct.careLevel !== mod.NO_ASSESSMENT) &&
    /NOT TAKEN/.test(noteD) === (direct.careLevel === mod.NO_ASSESSMENT));
  check("'Assessment not taken' is never printed as a care LEVEL anywhere",
    !/ASSESSMENT RESULT:\s+Assessment not taken/.test(noteD + noteA));
} finally {
  fs.rmSync(dir, { recursive: true, force: true });
  const leaked = fs.readdirSync(FN).filter((f) => f.indexOf("probe") !== -1);
  if (leaked.length) {
    console.log("  FAIL  no probe file left in netlify/functions   " +
                leaked.join(" "));
    checks.push(false);
  } else {
    console.log("  PASS  no probe file left in netlify/functions");
    checks.push(true);
  }
}

const passed = checks.filter(Boolean).length;
console.log("\n" + passed + "/" + checks.length + " passed");
process.exit(passed === checks.length ? 0 : 1);
