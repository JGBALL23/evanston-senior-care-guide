# Local press as an acquisition channel: routes, rules and the two angles to pitch

Project PJ02, step 1 (investigate) and step 2 (strategy). ESCG worker, 28 Nov 2026, session cse_014eaiSeLUyuyJkYCTLw4xJi. Research and preparation only: nothing here has been sent. This plan builds on research/local-news-senior-care-stories.md (27 Nov 2026), which found the story types the two Evanston newsrooms ran in the last twelve months.

## Published routes, read 28 Nov 2026

| Outlet | Route | Published rules that matter |
|---|---|---|
| Evanston RoundTable (contact-us page) | Story tips: tips@ address. Press releases and other items: news@ address or the page's form. | No stated length for tips. |
| Evanston RoundTable (submit-a-letter-to-the-editor page) | Letters: the page's form or the letters@ address. | Real name required, and the writer's affiliation is published. Evanston-specific topics only. About 400 words. No attachments, slides or links. Longer pieces are "considered for publication as guest essays". 30 days between letters from the same person or group. Small, largely volunteer staff, so replies are slow. |
| Evanston Now (contact page, got-news-share-it page) | Tips, press releases and letters go through the contact form; a staff@ address is listed. | "All items are reviewed by an editor before they are published." Events outside Evanston are generally not listed. |
| Evanston Now (guest-essays page) | Guest essays: full draft text through the contact form. | Essays must be "original works that have not been published and are not under consideration for publication elsewhere." |

Neither outlet publishes a beat list of reporters for health or aging. The bylines of the 27 Nov report's story types are a matter of public record, but this file names none: a pitch goes to the outlet's published route, not to a person.

**What this means:**
- Joseph's Evanston Now guest essay (with him since 22 Nov; map item D7) must not also be offered to the RoundTable while it is under consideration.
- The RoundTable is reached through tips and news items, not a second essay.
- A letter needs his name and an affiliation line, so it is his own decision and voice, never a prepared item.

## The two strongest angles

Ranked by expected local reach times the chance that the outlet uses it, with the guide's sourced page behind each.

### A. Retroactive Medicaid coverage falls from three months to two on 1 January 2027

**Why it fits:**
- Benefit changes from the 2025 federal law are a story type both outlets already ran: Evanston Now on 19 Jan and 2 Sep 2026, the RoundTable on 9 Jun 2026.
- None of those stories linked a family-facing explainer.
- This change is concrete, dated and checkable. It lands on the families of people who enter a nursing home and apply for Medicaid late.

**Source, read again 28 Nov 2026:** Illinois HFS, "How will Federal changes impact Medicaid?" (hfs.illinois.gov/info/fedresctr/faqshowwillfedchimpactmedicaid.html). It says "retroactive coverage will be decreased from 3 months to 2 months for all Illinois Medicaid customers" and "Beginning January 2027, Medicaid will only provide two months of retroactive coverage".

**Asset:** the guide illinois-medicaid-pending-nursing-home. Its corrected text (drafts dad7c20, corrections verified 27 Nov) is in publish batch #90 as commit 4815ca1. That commit is newer than package #91's cut of 27 Nov 09:48 UTC, so it reaches the live site only through the next package.

**Timing:** the pitch is worth most in December, before the change takes effect, and only once the page is live with the two-month text.

### B. After the holidays: what to do when a visit shows a parent is not managing

**Why it fits:**
- Seasonal service stories and senior-centre notices recur in the RoundTable: 5 Oct, 9 Nov and 10 Nov 2026 (dementia support and benefit-help items).
- The weeks after Thanksgiving and the December holidays are when adult children see changes in person.

**Asset:** the guide noticed-changes-in-parent-holiday-visit (built 27 Nov, reader-reviewed, in publish batch #90 and in package #91).

**Timing:** from the day #91 is live until early January.

### Considered and not chosen now

- **State enforcement at a licensed facility** (seven stories in eleven months, the only story that recurs about one subject). The page to offer would be check-illinois-inspection-records. Its accuracy audit is still blocked: its Illinois statute sources on ilga.gov could not be read on 28 Nov 2026 (curl: "SSL certificate problem: unable to get local issuer certificate"; web fetch: HTTP 503). Verdict: watch. It reopens when ilga.gov can be read and the audit says "holds". A reporter must not be pointed at an unaudited legal page.
- **Medicare Open Enrollment ends 7 December.** The new Medicare section (#93) is not live, and a tip would arrive too close to the deadline to be used. Drop for this year. Reopen for the 2027 enrollment period, 15 Oct to 7 Dec.

## Strategy

1. **Nothing goes out before the asset is live.** Each pitch waits until its page shows the right text on evanstonseniorcareguide.com.
   - A waits for the package after #91 that carries 4815ca1.
   - B waits for #91 itself.
2. **One tip per angle, to the RoundTable's published tips route.** The operator sends them, never the worker. Evanston Now's form is left to Joseph's essay.
   - At most three proposals in this new class before a response is seen.
   - One follow-up after 14 days, then stop.
   - The project's kill rule: three well-founded pitches, no use within six weeks.
3. **Each tip:**
   - is under 150 words
   - names the official source first and the guide page second
   - offers nothing for sale and no community
   - ends with the standard disclosure ("Disclosure: I work at Westminster Place in Evanston. The guide is my own independent project, it includes an optional way to request a tour there, and I receive no referral fees.")
   - carries a ref tag (?ref=em-<MMDD><letter>) on the guide link, so that a published mention can be measured
4. **Measurement:** referrals from evanstonroundtable.com, and visitors by ref tag in the monitor's per_tag counts. A mention without a link is still recorded, by date, as an outcome.

## Prepared tip texts (for the operator, after the condition above; not sent)

**A. Subject: Illinois Medicaid's retroactive coverage drops to two months on Jan. 1**

> From 1 January 2027, Illinois Medicaid will cover at most two months before the month of application instead of three. Illinois HFS says so in its federal-changes FAQ: "retroactive coverage will be decreased from 3 months to 2 months for all Illinois Medicaid customers." For Evanston families whose parent enters a nursing home and applies late, that can mean a month of private-pay charges nobody planned for. A plain-language explainer of what "Medicaid pending" means, who pays meanwhile and what changes in January, sourced to HFS, is here: <guide link with ref tag>. Happy to point you to the official sources.
> Disclosure: (standard text above)

**B. Subject: A practical checklist for families after the holiday visit**

> Holiday visits are often when adult children first notice a parent struggling: unopened mail, missed medications, a fall nobody mentioned. Our free, independent guide sets out next steps in order and points to official Illinois resources: the free Senior Health Insurance Program counselling line, the Department on Aging's services and what Medicare does and does not pay for. It names no community and sells nothing: <guide link with ref tag>. It may be useful for a seasonal service note.
> Disclosure: (standard text above)

**Before either text is drafted into Gmail,** the session preparing it re-reads the live page and the cited source on that day. Any figure or quotation that differs is corrected first.
