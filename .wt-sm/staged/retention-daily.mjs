/* ============================================================
   RETENTION-DAILY  —  scheduled cleanup, independent of traffic
   ============================================================
   NOT DEPLOYED. Staged with the rest of the retention work.

   Why this exists separately from the purge-on-submission:
   purging only when a new submission arrives means a quiet month
   is a month of expired records sitting in storage. The policy
   says 180 days; traffic does not get a vote in that. This runs
   every day whether anybody visits the site or not.

   Netlify Scheduled Functions invoke this on the cron below. It
   takes no request body, returns no data, and exposes nothing —
   it cannot be triggered usefully from outside.

   DEPLOYMENT NOTE
   Scheduled functions run on Netlify's infrastructure, so the
   schedule only exists once this file is deployed. Until then
   "daily cleanup" is a plan, not a behaviour, and the privacy
   notice must not claim it.

   VERIFYING IT ACTUALLY RUNS
   Each run writes the purge receipt (see retention.mjs). Read it
   through the export:

     curl -H "Authorization: Bearer <token>" \
       https://evanston-senior-care-guide.netlify.app/api/plan-visit-export \
       | grep -A6 '"retention"'

   If lastRunAt is more than ~25 hours old, the schedule has
   stopped and the retention claim is no longer true. That is the
   failure this receipt exists to make visible, because a dead
   cron breaks nothing a visitor can see.
   ============================================================ */

import { purgeExpired, quarantineReport, DAYS } from "./retention.mjs";

const STORE = "visit-attribution";

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

export default async () => {
  const ctx = blobsContext();
  if (!ctx) {
    console.error("retention-daily: no store context; nothing done");
    return new Response("no store context", { status: 500 });
  }

  const removed = await purgeExpired(ctx, STORE);
  const flagged = await quarantineReport(ctx, STORE);

  console.log("retention-daily: policy " + DAYS + "d, removed " +
    removed.length + ", flagged " + flagged.length);

  /* Anything unparseable is reported loudly rather than deleted.
     Deleting a record whose date cannot be read is guessing with
     somebody's data; keeping it silently forever is the other way
     to get it wrong. Flagging is the only honest third option. */
  if (flagged.length) {
    console.error("retention-daily: NEEDS REVIEW — " + flagged.length +
      " record(s) have an unreadable submission date and were NOT " +
      "deleted: " + flagged.join(", "));
  }

  return new Response(JSON.stringify({
    ok: true,
    policyDays: DAYS,
    removed: removed.length,
    flaggedForReview: flagged.length
  }), { headers: { "content-type": "application/json" } });
};

export const config = { schedule: "@daily" };
