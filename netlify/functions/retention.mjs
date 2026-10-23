/* ============================================================
   RETENTION  —  automatic deletion after 180 days
   ============================================================
   DEPLOYED and wired. Called on every submission by plan-visit.mjs
   and daily by retention-daily.mjs; the receipt it writes is
   returned by plan-visit-export.mjs so the policy can be audited
   from outside. The header used to say NOT DEPLOYED and was left
   behind by the merge, which is its own small lesson about trusting
   a comment over a call site.

   Why this is code and not a sentence: a retention policy written
   in a privacy notice and enforced by someone remembering to tidy
   up is not a policy, it is an intention. This deletes expired
   records on every submission, so the stated period is the period
   that actually happens.

   Why it also writes a receipt: "it deletes automatically" is a
   claim. A purge that records when it last ran, how many records
   it examined and how many it removed, is evidence. Without the
   receipt there is no way to tell a working purge from a purge
   that silently stopped running — which is the failure mode that
   matters, because nothing visibly breaks when deletion quietly
   stops.

   INTEGRATION (done)

   plan-visit.mjs calls purgeExpired(blobsContext(), STORE) after the
   record is stored and verified, deliberately NOT awaited: a
   visitor's submission must never be slowed down, and must never
   fail, because of housekeeping. A failed purge runs again on the
   next submission.

   plan-visit-export.mjs returns readPurgeReceipt(ctx, STORE) in its
   JSON, so whoever reads the records sees when deletion last ran at
   the moment they read them.

   CONFIGURATION

     PLAN_VISIT_RETENTION_DAYS   Defaults to 180.
                                 Set to 0 to disable deletion
                                 entirely — which must be a
                                 deliberate act, never a default.
   ============================================================ */

const DEFAULT_DAYS = 180;
const RAW = process.env.PLAN_VISIT_RETENTION_DAYS;
export const DAYS = RAW === undefined || RAW === ""
  ? DEFAULT_DAYS
  : Number(RAW);

const RECEIPT_KEY = "_retention/last-purge.json";

/* Keys are written as visits/<iso-with-colons-replaced>__<uuid>.json,
   so the submission date is recoverable from the key without
   fetching the record. A purge therefore costs one list call, not
   one fetch per record. */
export function submittedAtFromKey(key) {
  const stamp = String(key).replace(/^visits\//, "").split("__")[0];
  /* 2026-10-09T16-28-46-835Z -> 2026-10-09T16:28:46.835Z */
  const iso = stamp.replace(
    /^(\d{4}-\d{2}-\d{2})T(\d{2})-(\d{2})-(\d{2})-(\d{3})Z$/,
    "$1T$2:$3:$4.$5Z");
  const ms = Date.parse(iso);
  return Number.isNaN(ms) ? null : ms;
}

export function isExpired(key, now = Date.now(), days = DAYS) {
  if (!days || days <= 0) return false;          // 0 means keep
  const at = submittedAtFromKey(key);
  /* An unparseable key is never deleted. Deletion code that guesses
     is deletion code that eventually guesses wrong. */
  if (at === null) return false;
  return now - at > days * 24 * 60 * 60 * 1000;
}

function blobBase(ctx, store) {
  return ctx.edgeURL + "/" + ctx.siteID + "/site:" + store;
}

/* The receipt. Small enough to read at a glance, specific enough to
   prove the policy is live: if lastRunAt is weeks old, the purge has
   stopped and the privacy notice has become false. */
export async function readPurgeReceipt(ctx, store) {
  if (!ctx) return null;
  try {
    const res = await fetch(blobBase(ctx, store) + "/" + RECEIPT_KEY, {
      headers: { authorization: "Bearer " + ctx.token }
    });
    if (!res.ok) return { policyDays: DAYS, lastRunAt: null, note: "never run" };
    const r = await res.json();
    return Object.assign({ policyDays: DAYS }, r);
  } catch (err) {
    return null;
  }
}

async function writePurgeReceipt(ctx, store, receipt) {
  try {
    await fetch(blobBase(ctx, store) + "/" + RECEIPT_KEY, {
      method: "PUT",
      headers: {
        authorization: "Bearer " + ctx.token,
        "content-type": "application/json"
      },
      body: JSON.stringify(receipt)
    });
  } catch (err) { /* a lost receipt must not fail a submission */ }
}

/* Records whose submission date cannot be read from the key. They
   are never auto-deleted — deleting on a guess is worse than
   keeping — but they are never silently kept forever either. The
   daily job reports them so a human decides. */
export async function quarantineReport(ctx, store) {
  if (!ctx) return [];
  try {
    const res = await fetch(
      blobBase(ctx, store) + "?prefix=visits/",
      { headers: { authorization: "Bearer " + ctx.token } });
    if (!res.ok) return [];
    const { blobs = [] } = await res.json();
    return blobs.map((b) => b.key).filter((k) => submittedAtFromKey(k) === null);
  } catch (err) {
    return [];
  }
}

/* Returns the keys removed. Never throws: housekeeping must not be
   able to break a submission. */
export async function purgeExpired(ctx, store, now = Date.now()) {
  if (!ctx) return [];
  const base = blobBase(ctx, store);
  const auth = { authorization: "Bearer " + ctx.token };
  const removed = [];
  let examined = 0;
  let oldestRemainingDays = null;
  let unreadable = 0;

  try {
    const listed = await fetch(base + "?prefix=visits/", { headers: auth });
    if (!listed.ok) return [];
    const { blobs = [] } = await listed.json();
    examined = blobs.length;

    if (DAYS > 0) {
      for (const b of blobs) {
        if (!isExpired(b.key, now)) continue;
        const res = await fetch(base + "/" + b.key, { method: "DELETE", headers: auth });
        if (res.ok || res.status === 404) removed.push(b.key);
      }
    }

    /* The age of the oldest record still held. This is the number
       that proves the policy: if it ever exceeds the retention
       period, deletion is not working, whatever the receipt says
       about having run. */
    const kept = blobs.filter((b) => removed.indexOf(b.key) === -1);
    unreadable = kept.filter((b) => submittedAtFromKey(b.key) === null).length;
    const survivors = kept
      .map((b) => submittedAtFromKey(b.key))
      .filter((t) => t !== null);
    oldestRemainingDays = survivors.length
      ? Math.floor((now - Math.min(...survivors)) / 86400000)
      : 0;
  } catch (err) {
    return removed;
  }

  /* Written on every run, including runs that removed nothing. A
     receipt that only appears when something was deleted cannot
     distinguish "nothing was due" from "the purge is dead". */
  await writePurgeReceipt(ctx, store, {
    lastRunAt: new Date(now).toISOString(),
    policyDays: DAYS,
    examined,
    removed: removed.length,
    oldestRemainingDays,
    unreadableDates: unreadable,
    withinPolicy: DAYS <= 0 || oldestRemainingDays === null
      ? null
      : oldestRemainingDays <= DAYS
  });

  if (removed.length) {
    console.log("retention: removed " + removed.length + " of " + examined);
  }
  return removed;
}
