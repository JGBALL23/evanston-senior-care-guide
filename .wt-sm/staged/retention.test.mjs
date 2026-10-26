/* ============================================================
   RETENTION TESTS  —  node --experimental-vm-modules is not needed
   Run:  node staged/retention.test.mjs
   ============================================================
   The requirement these exist for: expired records must be deleted
   even when no new submissions arrive. A purge that only runs on
   write is indistinguishable from a working one until the site
   goes quiet, which is exactly when nobody is looking.

   These run against an in-memory fake of the blob store, so they
   prove the logic without touching production data.
   ============================================================ */

import { purgeExpired, quarantineReport, isExpired, submittedAtFromKey, DAYS }
  from "./retention.mjs";

let passed = 0;
let failed = 0;
const check = (name, ok, detail = "") => {
  console.log((ok ? "PASS" : "FAIL") + "  " + name.padEnd(56) + detail);
  ok ? passed++ : failed++;
};

/* ---- an in-memory stand-in for Netlify Blobs ---- */
function fakeStore(initial = {}) {
  const data = Object.assign({}, initial);
  const ctx = { edgeURL: "https://fake", siteID: "site", token: "t" };

  global.fetch = async (url, opts = {}) => {
    const u = String(url);
    const method = (opts.method || "GET").toUpperCase();
    const path = u.replace("https://fake/site/site:visit-attribution", "");

    if (method === "GET" && path.startsWith("?prefix=")) {
      const prefix = decodeURIComponent(path.replace("?prefix=", ""));
      return {
        ok: true,
        json: async () => ({
          blobs: Object.keys(data)
            .filter((k) => k.startsWith(prefix))
            .map((k) => ({ key: k }))
        })
      };
    }
    const key = path.replace(/^\//, "");
    if (method === "DELETE") {
      const existed = key in data;
      delete data[key];
      return { ok: existed, status: existed ? 200 : 404 };
    }
    if (method === "PUT") {
      data[key] = opts.body;
      return { ok: true };
    }
    if (key in data) {
      return { ok: true, json: async () => JSON.parse(data[key]) };
    }
    return { ok: false, status: 404 };
  };

  return { ctx, data };
}

const keyFor = (iso, id) =>
  "visits/" + iso.replace(/[:.]/g, "-") + "__" + id + ".json";

const NOW = Date.parse("2026-10-09T12:00:00.000Z");
const daysAgo = (n) => new Date(NOW - n * 86400000).toISOString();

/* ---- 1. the policy ---- */
check("retention period is 180 days by default", DAYS === 180, String(DAYS));

/* ---- 2. age boundary ---- */
check("a 179-day-old record is kept",
  isExpired(keyFor(daysAgo(179), "a"), NOW) === false);
check("a 181-day-old record is expired",
  isExpired(keyFor(daysAgo(181), "b"), NOW) === true);

/* ---- 3. THE REQUIREMENT: deletion with zero new submissions ----
   Nothing is written here. purgeExpired is called on a store that
   has received no traffic, exactly as the daily schedule will. */
{
  const old1 = keyFor(daysAgo(200), "old-1");
  const old2 = keyFor(daysAgo(365), "old-2");
  const fresh = keyFor(daysAgo(10), "fresh-1");
  const { ctx, data } = fakeStore({
    [old1]: JSON.stringify({ submissionId: "old-1" }),
    [old2]: JSON.stringify({ submissionId: "old-2" }),
    [fresh]: JSON.stringify({ submissionId: "fresh-1" })
  });

  const removed = await purgeExpired(ctx, "visit-attribution", NOW);

  check("expired records are deleted with no new submission",
    removed.length === 2, removed.length + " removed");
  check("the 200-day record is gone", !(old1 in data));
  check("the 365-day record is gone", !(old2 in data));
  check("the 10-day record survives", fresh in data);

  const receipt = JSON.parse(data["_retention/last-purge.json"] || "{}");
  check("a receipt was written", Boolean(receipt.lastRunAt), receipt.lastRunAt || "none");
  check("the receipt reports what it removed", receipt.removed === 2);
  check("the receipt reports the oldest survivor's age",
    receipt.oldestRemainingDays === 10, String(receipt.oldestRemainingDays));
  check("the receipt confirms the policy is being met",
    receipt.withinPolicy === true);
}

/* ---- 4. a quiet store still produces a receipt ----
   A run that deletes nothing must still prove it ran, otherwise a
   dead schedule looks identical to a tidy one. */
{
  const fresh = keyFor(daysAgo(3), "only");
  const { ctx, data } = fakeStore({ [fresh]: JSON.stringify({ submissionId: "only" }) });
  const removed = await purgeExpired(ctx, "visit-attribution", NOW);
  const receipt = JSON.parse(data["_retention/last-purge.json"] || "{}");
  check("a purge that removes nothing still writes a receipt",
    removed.length === 0 && Boolean(receipt.lastRunAt));
  check("the empty run still records the examined count",
    receipt.examined === 1, String(receipt.examined));
}

/* ---- 5. malformed records are flagged, never silently kept ---- */
{
  const bad1 = "visits/not-a-date__xyz.json";
  const bad2 = "visits/garbage.json";
  const old = keyFor(daysAgo(400), "old");
  const { ctx, data } = fakeStore({
    [bad1]: JSON.stringify({ submissionId: "xyz" }),
    [bad2]: JSON.stringify({ submissionId: "???" }),
    [old]: JSON.stringify({ submissionId: "old" })
  });

  check("an unreadable key parses to null",
    submittedAtFromKey(bad1) === null && submittedAtFromKey(bad2) === null);

  const removed = await purgeExpired(ctx, "visit-attribution", NOW);
  check("malformed records are NOT auto-deleted",
    bad1 in data && bad2 in data, removed.join(" "));
  check("the genuinely expired record IS deleted", !(old in data));

  const receipt = JSON.parse(data["_retention/last-purge.json"] || "{}");
  check("the receipt counts the unreadable records",
    receipt.unreadableDates === 2, String(receipt.unreadableDates));

  const flagged = await quarantineReport(ctx, "visit-attribution");
  check("quarantine report names them for review",
    flagged.length === 2 && flagged.includes(bad1) && flagged.includes(bad2),
    flagged.join(" "));
}

/* ---- 6. disabling deletion must be deliberate, never accidental ---- */
check("an unparseable key is never expired at any age",
  isExpired("visits/whatever.json", NOW) === false);

console.log("\n" + passed + "/" + (passed + failed) + " retention checks passed");
process.exit(failed === 0 ? 0 : 1);
