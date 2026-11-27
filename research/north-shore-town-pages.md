# North Shore town pages: do they qualify?

Research report by the ESCG worker, 27 Nov 2026 (frontier question F06, session cse_014eaiSbgkYkmzevMK2yQoyV). Counts and public pages only.

## Question

For the nearest towns and neighbourhoods (Wilmette, Skokie, Winnetka, Glenview, Northbrook, Lincolnwood, Rogers Park, Edgewater), what do searches for "assisted living <town>" and "assisted living <town> cost" show, and would a page like /assisted-living-evanston/ for a town meet this site's rules?

## Evidence (read 27 Nov 2026)

| Search | What ranks | Independent explainer from official sources? |
|---|---|---|
| assisted living Skokie IL | seniorliving.org, Seniorly, A Place for Mom, Caring.com, Checkbook, Mirador, seniors.fyi | No |
| assisted living Wilmette IL cost | Seniorly, A Place for Mom, seniorliving.org, Caring.com, seniors.fyi | No |
| assisted living Glenview / Northbrook IL | seniorliving.org, A Place for Mom, Caring.com, Seniorly, AgingCare, payingforseniorcare.com | No |
| assisted living Rogers Park / Edgewater Chicago | A Place for Mom (Rogers Park), an aggregator, Shirley Ryan AbilityLab's list of Chicago-area facilities, Checkbook, Caring.com, ConsumerAffairs | No |
| assisted living Winnetka / Lincolnwood IL cost | Caring.com, seniorsite.org, A Place for Mom, Seniorly, seniorliving.org | No |

Every results page is held by referral directories and listing sites; their town cost figures (about $5,400 to $6,070 a month) are averages of advertised starting prices and disagree with each other.

Search Console (Make read of 25 Nov 2026, 28 days): one query names a town, "assisted living cost evanston il" (5 impressions). No query names any of the eight towns above.

How /assisted-living-evanston/ is sourced: the Illinois Department of Public Health facility lookup and assisted-living page, the CareScout 2025 Cost of Care Survey (statewide median only, stated as "not an Evanston quote"), and links to this site's guides. Nothing on it is specific to Evanston except the name and the disclosed local tour option.

## Findings

1. **A copy of the Evanston page per town would be a keyword variant.** Under the sources this site allows (check-guides.js PRIMARY_HOSTS), a town page could cite only the same IDPH and CareScout pages, so its content would match the Evanston page with the town name changed. ROUTINE.md and the worker procedure forbid near-duplicates and keyword variants.
2. **What would make a town page genuinely local is not citable today.** The local first calls for these towns are township and village offices (for example Niles Township's offices in Skokie for Lincolnwood, Skokie, Golf and parts of Niles, Morton Grove and Glenview; New Trier and Northfield Townships; village senior services). Their websites are not on the allowed host list (only cityofevanston.org and thehacc.org are local hosts there), and adding a host is the owner's decision.
3. **No measured demand yet.** Search Console shows no impressions for any of these towns, so a page would be a bet on demand, not a response to it.

## Verdict and build order

- **All eight towns: WATCH.** Build nothing now.
- **Reopen** when either (a) Search Console shows a query naming one of these towns with impressions for this site, or (b) the owner approves township and village websites as citation hosts. Then the first page to build is a single North Shore page (not one per town): how to check a community's licence with IDPH, and which township office serves each town, sourced from each office's own page. Order: Skokie and Lincolnwood (Niles Township, nearest to Evanston), then Wilmette and Winnetka (New Trier Township), then Glenview and Northbrook (Northfield Township). Rogers Park and Edgewater are in Chicago and are served by the City of Chicago's senior services, a different source set.
- Never a ranking or a recommendation of communities.
