/* ============================================================
   PLAN-VISIT-EXPORT  —  reading the inquiry records back
   ============================================================

   A record nobody can retrieve is not evidence. This endpoint is
   how the stored submissions come back out: oldest first, with
   the server-generated submission ID and timestamp that make them
   worth anything.

   It is also the only place the names and contact details exist in
   readable form — the notification email deliberately carries none
   — so this is where the details come from when a family is passed
   to Admissions by phone.

   ACCESS
   Refused unless PLAN_VISIT_EXPORT_TOKEN is set on the site AND
   the request carries it as a bearer token. Unset = every request
   is refused, which is the correct default for a file of names
   and phone numbers. There is no fallback, no query-string key,
   and no partial-credit mode.

   ?format=csv returns a spreadsheet instead of JSON.
   ============================================================ */

import { readPurgeReceipt } from "./retention.mjs";

const TOKEN = process.env.PLAN_VISIT_EXPORT_TOKEN || "";
const STORE = "visit-attribution";

/* A submission id is a crypto.randomUUID() value: 8-4-4-4-12 hex with
   the version-4 nibble and the RFC 4122 variant. Matched whole, with
   anchors, so no prefix or suffix can smuggle anything past it. */
const UUID_RE =
  /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

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

/* Constant-time-ish comparison. The token is short and the
   endpoint is rate-limited by the platform, but there is no
   reason to leak length or prefix through timing. */
function tokenMatches(presented) {
  if (!TOKEN || !presented) return false;
  if (presented.length !== TOKEN.length) return false;
  let diff = 0;
  for (let i = 0; i < TOKEN.length; i++) {
    diff |= TOKEN.charCodeAt(i) ^ presented.charCodeAt(i);
  }
  return diff === 0;
}

function csvCell(value) {
  const text = String(value == null ? "" : value);
  return /[",\n]/.test(text) ? '"' + text.replace(/"/g, '""') + '"' : text;
}

export default async (request) => {
  const presented = (request.headers.get("authorization") || "")
    .replace(/^Bearer\s+/i, "");

  if (!TOKEN) {
    return new Response(
      JSON.stringify({ ok: false, error: "Export is not enabled on this site." }),
      { status: 503, headers: { "content-type": "application/json" } });
  }
  if (!tokenMatches(presented)) {
    return new Response(JSON.stringify({ ok: false, error: "Not authorised." }),
      { status: 401, headers: { "content-type": "application/json" } });
  }

  const ctx = blobsContext();
  if (!ctx) {
    return new Response(JSON.stringify({ ok: false, error: "Store unavailable." }),
      { status: 503, headers: { "content-type": "application/json" } });
  }

  const auth = { authorization: "Bearer " + ctx.token };
  const base = ctx.edgeURL + "/" + ctx.siteID + "/site:" + STORE;

  /* DELETE /api/plan-visit-export?id=<submissionId>
     A file of real names and phone numbers has to have a way out.
     This covers a test record, a mistake, and anyone who asks to be
     removed. It deletes by submission ID, one record at a time. */
  if (request.method === "DELETE") {
    const id = new URL(request.url).searchParams.get("id");
    if (!id) {
      return new Response(JSON.stringify({ ok: false, error: "Pass ?id=<submissionId>." }),
        { status: 400, headers: { "content-type": "application/json" } });
    }
    /* The id must be a complete submission UUID, validated before it
       is allowed anywhere near a key comparison. Anything shorter,
       longer or malformed is refused outright rather than matched
       leniently. */
    if (!UUID_RE.test(id)) {
      return new Response(JSON.stringify({ ok: false,
        error: "That is not a complete submission id. Nothing was deleted." }),
        { status: 400, headers: { "content-type": "application/json" } });
    }
    const all = await fetch(base + "?prefix=visits/", { headers: auth });
    if (!all.ok) {
      return new Response(JSON.stringify({ ok: false, error: "Could not list records." }),
        { status: 502, headers: { "content-type": "application/json" } });
    }
    /* EXACT MATCH ONLY. This used to be an indexOf substring test,
       which meant a short or partial id matched every key containing
       it — "?id=a" would have selected most of the store, and the
       loop below would have deleted all of them. A deletion route is
       the one place a loose match is unforgivable.

       Keys are visits/<timestamp>__<uuid>.json, so an exact record is
       the one whose key ends with __<uuid>.json and nothing else. */
    const want = "__" + id + ".json";
    const match = ((await all.json()).blobs || [])
      .map((b) => b.key)
      .filter((k) => k.endsWith(want));
    if (match.length === 0) {
      return new Response(JSON.stringify({ ok: false, error: "No record with that id." }),
        { status: 404, headers: { "content-type": "application/json" } });
    }
    /* Two keys cannot legitimately carry the same UUID. If it ever
       happens, something is wrong upstream and deleting both on a
       guess is worse than deleting neither. */
    if (match.length > 1) {
      return new Response(JSON.stringify({ ok: false,
        error: "That id matches more than one record. Nothing was deleted.",
        matched: match.length }),
        { status: 409, headers: { "content-type": "application/json" } });
    }
    const removed = [];
    for (const key of match) {
      const res = await fetch(base + "/" + key, { method: "DELETE", headers: auth });
      if (res.ok || res.status === 404) removed.push(key);
    }
    return new Response(JSON.stringify({ ok: true, deleted: removed.length, keys: removed }),
      { status: 200, headers: { "content-type": "application/json" } });
  }

  const listed = await fetch(base + "?prefix=visits/", { headers: auth });
  if (!listed.ok) {
    return new Response(JSON.stringify({ ok: false, error: "Could not list records." }),
      { status: 502, headers: { "content-type": "application/json" } });
  }
  const { blobs = [] } = await listed.json();

  /* Keys are timestamp-prefixed, so sorting the keys sorts the
     records into the order the submissions actually arrived. */
  const keys = blobs.map((b) => b.key).sort();

  const records = [];
  for (const key of keys) {
    const res = await fetch(base + "/" + key, { headers: auth });
    if (res.ok) records.push(await res.json());
  }

  const format = new URL(request.url).searchParams.get("format");

  if (format === "csv") {
    /* assessmentTaken and interestName added 2026-10-26 with the direct
       inquiry path. Without them a direct row exports as a blank-looking
       careLevel and reads like a data fault rather than a real visitor who
       simply never took the assessment. careLevelName carries
       "Assessment not taken" for those rows. */
    const header = ["submissionId", "receivedAt", "firstName", "lastName",
      "email", "phone", "assessmentTaken", "careLevelName", "interestName",
      "admissionsDept", "admissionsPhone",
      "source", "stage", "referredToAdmissionsAt"];
    const rows = [header.join(",")].concat(
      records.map((r) => header.map((h) => csvCell(r[h])).join(",")));
    return new Response(rows.join("\n"), {
      status: 200,
      headers: {
        "content-type": "text/csv; charset=utf-8",
        "content-disposition": 'attachment; filename="westminster-visit-leads.csv"',
        "cache-control": "no-store"
      }
    });
  }

  /* count is a snapshot taken at read time. The store's listing is
     eventually consistent, so a submission made in the last second
     or two may not appear yet. Labelled rather than hidden. */
  /* The purge receipt travels with the export so the 180-day claim can
     be audited from outside, by whoever is reading the records, at the
     moment they read them. If lastRunAt is weeks old the deletion
     policy has stopped and the privacy notice has become false —
     which is invisible otherwise, because a dead purge breaks nothing
     a visitor can see. */
  return new Response(JSON.stringify({
    ok: true,
    count: records.length,
    countIs: "snapshot at read time; a submission made seconds ago may not be listed yet",
    stageIs: "recorded_tour_inquiry means this family asked to be contacted. " +
      "It is not a referral, not a completed tour and not a move-in.",
    retention: await readPurgeReceipt(ctx, STORE),
    records
  }, null, 2), {
    status: 200,
    headers: { "content-type": "application/json", "cache-control": "no-store" }
  });
};

export const config = { path: "/api/plan-visit-export" };
