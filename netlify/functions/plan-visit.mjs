/* ============================================================
   PLAN-VISIT  —  server-side tour-inquiry record
   ============================================================

   WHAT THIS EXISTS FOR
   A family uses the Evanston Senior Care Guide, reaches a care
   level, sees Westminster Place disclosed as a local option, and
   asks to be contacted about touring it. That creates a record
   with a server-generated timestamp BEFORE anyone refers them,
   which is the whole point: the record has to pre-date the
   referral to prove the inquiry originated here.

   WHAT IT DELIBERATELY DOES NOT DO
   - It does not schedule or guarantee a tour. Westminster Place
     Admissions decides that, not this site.
   - It does not forward anything to Westminster Place. The
     referral is a manual phone call made by a person, after this
     record exists, and only while that is permitted.
   - It does not submit Westminster's own form on anyone's behalf.
   - It never receives the six raw assessment answers. The
     assessment runs entirely in the browser and those answers are
     never sent anywhere. ONE derived value — the care level, from a
     fixed list of six — is accepted so the notification can name
     the right Admissions team. Every diagnosis, medication,
     insurance and date-of-birth field is still refused outright
     (see REJECT_KEYS), enforced in code rather than promised in
     copy.

   PROOF MODEL (why it is a function and not a mailto)
   1. submissionId  — crypto.randomUUID(), generated on the server
   2. receivedAt    — the server clock, not the visitor's clock
   3. durable record — written to Netlify Blobs, site-scoped, so it
      survives every later deploy and does not depend on email
   4. notification  — an automatic email to the operator carrying the
      name, contact details, derived care level and timestamp, so a
      referral call needs no lookup (changed 2026-10-17)

   A success response is returned ONLY after the durable record is
   accepted. If the record cannot be written, the visitor is told
   plainly and nothing claims to have been saved.
   ============================================================ */

import { purgeExpired } from "./retention.mjs";

/* ---------- configuration -----------------------------------
   Nothing identifying is hard-coded. Both of these are set as
   Netlify environment variables on the site:

   RESEND_API_KEY        Resend API key. Secret. Never logged,
                         never returned, never in the browser.
                         Unset = durable record still written,
                         email reported as not configured.

   PLAN_VISIT_NOTIFY_TO  Where the notification is delivered.
   PLAN_VISIT_NOTIFY_FROM
                         The verified sender it comes from.
                         Both live in the environment rather than
                         this source, so no address is baked into
                         a public repository and either can change
                         without a code edit.

   PLAN_VISIT_EXPORT_TOKEN
                         Bearer token for reading the records back
                         out. Unset = the export endpoint refuses
                         every request, which is the safe default.

   The durable record itself needs neither of these. It is written
   to Netlify Blobs using credentials Netlify injects at runtime,
   so a submission is retained from the first minute this is live. */
const RESEND_KEY = process.env.RESEND_API_KEY || "";
const NOTIFY_TO = process.env.PLAN_VISIT_NOTIFY_TO || "";
const NOTIFY_FROM = process.env.PLAN_VISIT_NOTIFY_FROM || "";
const SOURCE = "Evanston Senior Care Guide";
/* Named on every record and every notification, so the authorship
   of this work is carried by the evidence itself rather than by
   somebody remembering to mention it. */
const DEVELOPED_BY = "Joseph Gonzales";

/* ---------- what must never arrive here ---------------------
   Defence in depth. The browser never sends these. If any of
   them ever appears, something upstream has gone wrong and the
   request is refused rather than quietly stored. */
const REJECT_KEYS = [
  "diagnosis", "condition", "conditions", "medical", "medicalhistory",
  "history", "medication", "medications", "adl", "adls", "memory",
  "memorystatus", "cognition", "mobility", "insurance", "medicare",
  "medicaid", "policynumber", "dob", "dateofbirth", "birthdate",
  "age", "ssn", "answers", "quiz", "quizanswers", "assessment",
  "reasons", "signals", "symptoms",
  "mobilityaid", "hospital", "alone", "household"
];
/* NARROWED 2026-10-17, on the owner's instruction, and narrowed only
   by one field. "carelevel", "level" and "result" used to be refused
   outright. The derived care level is now accepted so the operator's
   notification can name the right Admissions team.
   What is STILL refused, and is the part that mattered: the six raw
   answers, and every diagnosis, medication, insurance and
   date-of-birth field. One derived label travels; the reasoning
   behind it never does. */

/* The only values careLevel may hold. A fixed list, never free text,
   so this cannot become a channel for assessment detail. */
const CARE_LEVELS = {
  independent: { name: "Independent Living",
                 dept: "Independent Living Sales", tel: "(847) 570-3310" },
  assisted:    { name: "Assisted Living",
                 dept: "Assisted Living & Memory Care Sales", tel: "(847) 866-1615" },
  memory:      { name: "Memory Care",
                 dept: "Assisted Living & Memory Care Sales", tel: "(847) 866-1615" },
  skilled:     { name: "Skilled Nursing",
                 dept: "Skilled Nursing Admissions", tel: "(847) 492-7780" },
  rehab:       { name: "Short-Term Rehabilitation",
                 dept: "Skilled Nursing Admissions", tel: "(847) 492-7780" },
  no_need:     { name: "No higher level of care yet",
                 dept: "General Inquiries", tel: "(847) 570-3422" }
};

/* What the visitor SAID they want to see, which is not always what the
   assessment derived. A fixed list for the same reason careLevel is one:
   free text here would turn an inquiry alert into an open channel.

   This is NOT a routing instruction. Every inquiry reaches the same
   inbox and the owner handles all of them himself; this only tells him
   what the person is actually asking about before he replies. */
const INTERESTS = {
  independent: "Independent Living",
  assisted: "Assisted Living",
  memory: "Memory Care",
  skilled: "Skilled Nursing",
  unsure: "Not sure yet"
};

const ALLOWED_KEYS = [
  "firstName", "lastName", "email", "phone", "consent", "careLevel",
  "interest"
];

/* ---------- the consent, stored verbatim --------------------
   This submission authorises a transfer: the name and contact
   details are passed by hand to Westminster Place so
   they can get in touch about a tour. A consent that permits a
   transfer has to be evidenced by what the person actually
   agreed to, not by a boolean on its own — "they ticked a box"
   is not an answer to "what did the box say".

   So the exact sentence shown on the form is stored on every
   record. If the wording ever changes, old records still carry
   the wording their signer saw. The string below and the form
   copy in app.js are asserted identical by test.js, which is
   what stops them drifting apart. */
const CONSENT_STATEMENT =
  "Share my name, phone, email, assessment result and what I am interested " +
  "in with Westminster Place, so they can contact me about a tour.";
/* Bumped 2026-10-26. Two changes, and the permission widened by exactly
   one field, so the version moves with it.

   1. The selected interest is now shared as well. A fifth item, named.
   2. The recipient is now named as the organisation rather than one of
      its departments. The old wording named their SKILLED NURSING desk — their own published
      directory lists Independent Living, Assisted Living & Memory Care and
      Skilled Nursing Admissions as separate teams. Naming one department
      for every inquiry was wrong, and would have been plainly wrong for
      someone asking about independent living. The recipient is the
      organisation; the owner reads every inquiry himself and passes it on.

   Records signed under earlier wording keep their own version, so what
   each person actually agreed to stays recoverable. */
const CONSENT_VERSION = "2026-10-26";

/* ---------- small helpers ----------------------------------- */
const clean = (value, max) =>
  String(value == null ? "" : value).replace(/[\u0000-\u001f\u007f]/g, "").trim().slice(0, max);

const EMAIL_OK = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

function digitsOnly(value) {
  return String(value || "").replace(/[^0-9]/g, "");
}

function json(statusCode, body) {
  return new Response(JSON.stringify(body), {
    status: statusCode,
    headers: {
      "content-type": "application/json",
      "cache-control": "no-store"
    }
  });
}

/* ---------- validation --------------------------------------
   Returns a list of plain-English problems. An empty list means
   the submission is good. The messages are written to be shown
   to a family, not to a developer. */
function validate(payload) {
  const problems = [];

  const firstName = clean(payload.firstName, 60);
  const lastName = clean(payload.lastName, 60);
  const email = clean(payload.email, 120).toLowerCase();
  const phoneRaw = clean(payload.phone, 40);
  const phoneDigits = digitsOnly(phoneRaw);

  if (firstName.length < 1) problems.push("First name is required.");
  if (lastName.length < 1) problems.push("Last name is required.");

  /* At least one reliable way to be reached. Admissions will be the
     ones making contact, so refusing a submission that gives only a
     phone number — or only an email — would turn a usable inquiry
     away for no reason. One is enough; both is better. */
  const hasEmail = email.length > 0;
  const hasPhone = phoneDigits.length > 0;
  if (!hasEmail && !hasPhone) {
    problems.push("Add a phone number or an email address so Admissions can reach you.");
  }
  if (hasEmail && !EMAIL_OK.test(email)) {
    problems.push("That email address does not look complete.");
  }
  if (hasPhone && (phoneDigits.length < 10 || phoneDigits.length > 15)) {
    problems.push("That phone number does not look complete.");
  }

  /* The planned-visit date is gone. It asked a family to commit to a
     day before anyone had told them a tour was available, and the
     referral now runs through Admissions, who set the time. A field
     whose answer nobody uses is friction, and it was one more date
     sitting in a file of personal information for no purpose. */

  /* Refused rather than silently blanked: an unrecognised value means
     something upstream changed, and guessing would put a wrong
     Admissions team in the notification. */
  /* An absent or unrecognised interest falls back to "unsure" rather than
     rejecting the submission. A dropdown this person never touched must
     never be the reason a real inquiry is lost. */
  const rawInterest = clean(payload.interest, 20);
  const interest = Object.prototype.hasOwnProperty.call(INTERESTS, rawInterest)
    ? rawInterest : "unsure";

  const careLevel = clean(payload.careLevel, 20);
  if (!Object.prototype.hasOwnProperty.call(CARE_LEVELS, careLevel)) {
    problems.push("The assessment result could not be read. Retake the six questions.");
  }

  if (payload.consent !== true && payload.consent !== "true" && payload.consent !== "on") {
    problems.push("Tick the box to give permission for your details to be shared with Admissions.");
  }

  return {
    problems,
    record: { firstName, lastName, email, phone: phoneRaw, phoneDigits, careLevel,
              interest }
  };
}

/* ---------- the durable record ------------------------------
   Netlify Blobs. Site-scoped, so a record written today survives
   every later deploy. The store is reached over its REST
   interface using the credentials Netlify injects into the
   function at runtime, which means this works with no account
   setup, no API key of mine, and no third party holding the
   evidence.

   Netlify Forms was the first choice and was rejected on
   measurement: form detection is off on this site (listSiteForms
   returned an empty array, and a direct form POST answered 404),
   so it would have needed a dashboard change before a single
   record could be stored. */
function blobsContext() {
  const raw = process.env.NETLIFY_BLOBS_CONTEXT;
  if (!raw) return null;
  try {
    const parsed = JSON.parse(Buffer.from(raw, "base64").toString("utf8"));
    if (!parsed.edgeURL || !parsed.siteID || !parsed.token) return null;
    return parsed;
  } catch (err) {
    return null;
  }
}

const STORE = "visit-attribution";

function blobUrl(ctx, key) {
  return ctx.edgeURL + "/" + ctx.siteID + "/site:" + STORE + "/" + key;
}

/* Key order matters: prefixing with the timestamp makes the store
   list itself in chronological order, which is the order the
   evidence is read in. */
function recordKey(receivedAt, submissionId) {
  return "visits/" + receivedAt.replace(/[:.]/g, "-") + "__" + submissionId + ".json";
}

async function writeDurableRecord(record, submissionId, receivedAt) {
  const ctx = blobsContext();
  if (!ctx) return { stored: false, reason: "no_store_context" };

  const row = {
    submissionId,
    receivedAt,
    firstName: record.firstName,
    lastName: record.lastName,
    email: record.email,
    phone: record.phone,
    careLevel: record.careLevel,
    interest: record.interest || "unsure",
    interestName: INTERESTS[record.interest] || INTERESTS.unsure,
    careLevelName: (CARE_LEVELS[record.careLevel] || {}).name || "",
    admissionsDept: (CARE_LEVELS[record.careLevel] || {}).dept || "",
    admissionsPhone: (CARE_LEVELS[record.careLevel] || {}).tel || "",
    source: SOURCE,
    developedBy: DEVELOPED_BY,
    /* The evidence ladder has four rungs and this is the first.
       A recorded inquiry is not a referral, not a completed tour,
       and not a move-in. Stamping the stage on the record itself
       is what stops it being read as one of the others later. */
    stage: "recorded_tour_inquiry",
    /* What they agreed to, in the words they were shown, and when.
       A permission to pass someone's details to a third party is
       only as good as the record of what was permitted. */
    consent: true,
    consentStatement: CONSENT_STATEMENT,
    consentVersion: CONSENT_VERSION,
    consentedAt: receivedAt,
    /* Set by hand, never by this endpoint. The referral is a phone
       call a person makes; the record starts life saying it has not
       happened, so an un-referred inquiry can never read as one
       that was passed on. */
    referredToAdmissionsAt: null
  };

  const key = recordKey(receivedAt, submissionId);
  const auth = { authorization: "Bearer " + ctx.token };

  try {
    const res = await fetch(blobUrl(ctx, key), {
      method: "PUT",
      headers: Object.assign({ "content-type": "application/json" }, auth),
      body: JSON.stringify(row)
    });
    if (!res.ok) return { stored: false, reason: "store_http_" + res.status };

    /* READ-BACK. A write that answers 200 is not yet evidence —
       evidence is a record that can be fetched again afterwards.
       The submission is only reported as stored once the store
       hands the same ID back. */
    const back = await fetch(blobUrl(ctx, key), { headers: auth });
    if (!back.ok) return { stored: false, reason: "readback_http_" + back.status };
    const parsed = await back.json();
    if (parsed.submissionId !== submissionId) {
      return { stored: false, reason: "readback_mismatch" };
    }

    return { stored: true, reason: "ok", key };
  } catch (err) {
    return { stored: false, reason: "store_threw" };
  }
}

/* A running total is deliberately NOT returned here. The store's
   listing is eventually consistent, so two submissions a second
   apart can both be told there are two records on file — which
   was observed live on 2026-10-08 and is how this comment came to
   exist. A number that can under-report is worse than no number.
   Counting belongs in the export, where the list is a labelled
   snapshot taken at read time. */

/* ---------- the notification --------------------------------
   Same values as the durable record. No assessment answers, no
   care level, no health information — there is nothing of that
   kind in scope at this point in the code. */
function notificationText(record, submissionId, receivedAt) {
  const lvl = CARE_LEVELS[record.careLevel] || {};
  /* Chicago local time alongside the UTC stamp. The stored evidence
     stays UTC — that is the value that must be unambiguous years
     later — but a human reading an alert wants their own clock. */
  let local = "";
  try {
    local = new Date(receivedAt).toLocaleString("en-US", {
      timeZone: "America/Chicago", dateStyle: "full", timeStyle: "short"
    }) + " (Chicago)";
  } catch (err) { local = "(local time unavailable)"; }

  const lines = [
    "A family asked to be contacted about touring Westminster Place.",
    "",
    "NAME:              " + record.firstName + " " + record.lastName,
    "PHONE:             " + (record.phone || "not given"),
    "EMAIL:             " + (record.email || "not given"),
    "",
    "INTERESTED IN:     " + (INTERESTS[record.interest] || INTERESTS.unsure),
    "ASSESSMENT RESULT: " + (lvl.name || "unknown"),
    "ADMISSIONS TEAM:   " + (lvl.dept || "unknown") + " - " + (lvl.tel || ""),
    "",
    "SUBMITTED:         " + local,
    "                   " + receivedAt + " (UTC, the stored value)",
    "",
    "Submission ID:     " + submissionId,
    "Source:            " + SOURCE,
    "Developed by:      " + DEVELOPED_BY,
    "",
    "The result above is the care LEVEL the six questions produced.",
    "The answers themselves were never sent anywhere and are not held.",
    "",
    "This record was created before any referral. It does not mean a",
    "tour was scheduled, and it is not a confirmed tour. The family",
    "gave permission for these contact details to be passed to",
    "Westminster Place.",
    "",
    "This email contains personal information and is NOT covered by",
    "the site 180-day deletion policy. Clear it from this mailbox",
    "once the referral call is made."
  ];
  return lines.join(String.fromCharCode(10));
}

/* CHANGED 2026-10-17 on the owner's instruction. The notification
   now carries the full name, phone, email and derived care level,
   because an alert you have to look something up from is an alert
   that gets ignored.

   This is a real trade, written down rather than glossed: the email
   leaves personal information in a mailbox and at Resend, neither of
   which the 180-day purge can reach. The email says so in its own
   last line. The store stays the authoritative copy and is the one
   that expires on schedule.

   Transport is Resend, replacing Web3Forms on 2026-10-17. Web3Forms
   was not misconfigured — it sits behind Cloudflare, which answered
   a server-side POST from this function with a 403 challenge page
   on 2026-10-17, with and without a browser user-agent. Their API
   expects a browser-side submission. This endpoint is server-side
   by design, because a client-generated timestamp is not evidence,
   so the provider had to change rather than the architecture.

   Resend also retains far less: there is no three-year default to
   work around, and nothing personal is sent to them regardless.

   Fails CLOSED and SILENT: a notification problem must never cost
   a submission, and must never be reported as a send. The returned
   state is the literal truth of what happened. */
async function sendNotification(record, submissionId, receivedAt) {
  if (!RESEND_KEY || !NOTIFY_TO || !NOTIFY_FROM) return "not_configured";
  try {
    const res = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        /* The key goes in this header and nowhere else. It is never
           logged, never put in a response body, and never reaches
           the browser. */
        authorization: "Bearer " + RESEND_KEY,
        "content-type": "application/json"
      },
      body: JSON.stringify({
        from: NOTIFY_FROM,
        to: [NOTIFY_TO],
        subject: "New Westminster Tour Inquiry — Evanston Senior Care Guide",
        text: notificationText(record, submissionId, receivedAt)
      })
    });
    if (res.ok) return "sent";
    /* The status alone, never the body: a provider error body can
       echo request content back, and this one must stay free of
       anything that could carry a key or an address. */
    console.error("plan-visit: notification rejected, status " + res.status);
    return "failed";
  } catch (err) {
    console.error("plan-visit: notification threw");
    return "failed";
  }
}

/* ---------- handler ----------------------------------------- */
/* ---------- COLLECTION SWITCH ------------------------------
   Collection is OFF unless PLAN_VISIT_COLLECTION_ENABLED is the
   exact string "true". Absent, misspelled or empty all mean off.

   A fail-safe default, deliberately. The privacy notice is not
   published, the retention purge is not deployed, and the export
   token is not set — so a real person's details would go into a
   store nobody can read and no policy covers. Refusing is the
   only honest behaviour until those are resolved.

   This is enforced here rather than only by hiding the form,
   because a hidden form is not a closed door: anyone can still
   POST to the endpoint. */
const COLLECTING = process.env.PLAN_VISIT_COLLECTION_ENABLED === "true";

export default async (request) => {
  if (request.method !== "POST") {
    return json(405, { ok: false, error: "Use POST." });
  }

  if (!COLLECTING) {
    return json(503, {
      ok: false,
      error: "This site is not accepting tour inquiries yet. Nothing was stored.",
      reason: "collection_disabled"
    });
  }

  let payload;
  try {
    payload = await request.json();
  } catch (err) {
    return json(400, { ok: false, error: "Send a JSON body." });
  }
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
    return json(400, { ok: false, error: "Send a JSON object." });
  }

  /* SEPARATION GATE — enforced, not merely stated.
     The identifiable submission and the care assessment are
     different things and must never travel together. */
  const keys = Object.keys(payload);
  const normalised = keys.map((k) => k.toLowerCase().replace(/[^a-z]/g, ""));
  const offending = normalised.filter((k) => REJECT_KEYS.indexOf(k) !== -1);
  if (offending.length > 0) {
    return json(422, {
      ok: false,
      error: "This endpoint refuses health and assessment data. Nothing was stored.",
      refusedFields: offending
    });
  }
  const unexpected = keys.filter((k) => ALLOWED_KEYS.indexOf(k) === -1);
  if (unexpected.length > 0 || keys.length > ALLOWED_KEYS.length) {
    return json(422, {
      ok: false,
      error: "Unexpected fields. Nothing was stored.",
      unexpectedFields: unexpected
    });
  }

  const { problems, record } = validate(payload);
  if (problems.length > 0) {
    return json(400, { ok: false, problems });
  }

  /* Server-generated, not supplied by the browser. These two
     values are the evidence. */
  const submissionId = crypto.randomUUID();
  const receivedAt = new Date().toISOString();

  const written = await writeDurableRecord(record, submissionId, receivedAt);

  if (!written.stored) {
    /* Never report success for something that was not recorded.
       The reason is returned so a failure is diagnosable from the
       outside instead of silently swallowed — it names a state,
       never a credential. */
    console.error("plan-visit: record not stored:", written.reason);
    return json(503, {
      ok: false,
      error: "The visit could not be saved just now. Nothing was stored. Please try again.",
      reason: written.reason
    });
  }

  /* Housekeeping, never awaited: a visitor's submission must not be
     slowed down or failed by a purge. A daily scheduled run covers
     the case where nobody submits for weeks. */
  purgeExpired(blobsContext(), STORE).catch(() => {});

  const email = await sendNotification(record, submissionId, receivedAt);

  return json(200, {
    ok: true,
    submissionId,
    receivedAt,
    stored: true,
    verified: true,
    notification: email,
    source: SOURCE
  });
};

export const config = { path: "/api/plan-visit" };
