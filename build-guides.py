#!/usr/bin/env python3
"""
BUILD-GUIDES  —  the article library, generated from one file.

Why a generator and not five hand-written pages: the owner asked for an
SEO foundation built once and maintained occasionally. Every page shares a
head, a nav, a footer, a sources block and a sitemap entry. Hand-editing
five copies of that is how a site drifts — one page keeps a stale figure,
another loses its canonical, and nobody notices for a year.

Here, each guide is a dict. Adding one means adding a dict. The sitemap,
the /guides/ index, the internal links and the "last reviewed" dates all
follow automatically.

EVERY FIGURE IN THIS FILE WAS READ FROM THE PRIMARY SOURCE on 2026-10-18:
  - medicare.gov/basics/costs/medicare-costs        (Part A deductible, SNF)
  - medicare.gov/coverage/skilled-nursing-facility-snf-care
  - hfs.illinois.gov/medicalprograms/slf/residentfactsheet.html  (PNA, GCC)
  - CareScout 2025 Cost of Care Survey, published 2026 — the same PDF the
    assessment already cites, so the guides and the result pages can never
    disagree about a number.

Nothing here is from a lead-generation aggregator. If a figure cannot be
read from a government or survey primary source, it does not go on a page.

Run:  python build-guides.py
Writes: _dist/guides/*.html, _dist/guides/index.html, _dist/sitemap.xml
"""

import io, os, re, datetime

SITE = "https://evanstonseniorcareguide.com"
REVIEWED = "2026-10-18"
REVIEWED_HUMAN = "18 October 2026"
OUT = "_dist/guides"

# --------------------------------------------------------------------------
# VERIFIED FIGURES — one definition each, reused everywhere.
# An annual refresh edits this block and nothing else.
# --------------------------------------------------------------------------
F = {
    "al_median": "$6,219",
    "nh_semi": "$8,304",
    "nh_private": "$9,216",
    "partA_deductible": "$1,736",
    "snf_coins": "$217",
    "snf_total_80": "$17,360",
    "pna": "$120",
    "hfs_room_board": "$874",
    "hfs_double": "$625.50",
    "ccp_assets": "$17,500",
    "ccp_line": "1-800-252-8966",
    "csra_2026": "$143,172",
    "csmna_2026": "$4,066.50",
}

SRC = {
    "carescout": ('CareScout 2025 Cost of Care Survey, published 2026',
                  'https://assets.carescout.com/x/5c90319b6a/298701.pdf'),
    "mcosts": ('Medicare.gov — Medicare costs',
               'https://www.medicare.gov/basics/costs/medicare-costs'),
    "msnf": ('Medicare.gov — Skilled nursing facility (SNF) care',
             'https://www.medicare.gov/coverage/skilled-nursing-facility-snf-care'),
    "jimmo": ('CMS — Jimmo v. Sebelius Settlement Agreement Fact Sheet',
              'https://www.cms.gov/medicare/medicare-fee-for-service-payment/snfpps/downloads/jimmo-factsheet.pdf'),
    "mcompare": ('Medicare.gov — Care Compare',
                 'https://www.medicare.gov/care-compare/'),
    "hfs_slf": ('Illinois HFS — Supportive Living Program Resident Fact Sheet',
                'https://hfs.illinois.gov/medicalprograms/slf/residentfactsheet.html'),
    "hfs_hcbs": ('Illinois HFS — Home and Community Based Services waivers',
                 'https://hfs.illinois.gov/medicalclients/hcbs.html'),
    "hfs_rb": ('Illinois HFS Provider Notice, 26 November 2025 — Supportive Living room and board',
               'https://hfs.illinois.gov/medicalproviders/notices/notice.prn251126a.html'),
    "hfs_slp_rates": ('Illinois HFS — Supportive Living reimbursement',
                      'https://hfs.illinois.gov/medicalproviders/medicaidreimbursement/supportivelivinging.html'),
    "idph": ('Illinois Department of Public Health — Health Care Report Card',
             'https://healthcarereportcard.illinois.gov/'),
    "idoa_ccp": ('Illinois Department on Aging — Community Care Program',
                 'https://ilaging.illinois.gov/programs/ccp.html'),
    "hfs_elderly": ('Illinois HFS — Persons who are Elderly waiver',
                    'https://hfs.illinois.gov/medicalclients/hcbs/elderly.html'),
    "hfs_ltc_clients": ('Illinois HFS — Long Term Care (for clients)',
                        'https://hfs.illinois.gov/medicalclients/ltc'),
    "hfs_ltc_providers": ('Illinois HFS — Long Term Care provider programs',
                          'https://hfs.illinois.gov/medicalproviders/providerprograms/longtermcare.html'),
    "hfs_spenddown": ('Illinois HFS — Spenddown brochure (HFS 591SP)',
                      'https://hfs.illinois.gov/info/brochures-and-forms/brochures/hfs591sp.html'),
    "hfs_spousal2026": ('Illinois HFS Provider Notice, 22 January 2026 — 2026 spousal impoverishment standards',
                        'https://hfs.illinois.gov/medicalproviders/notices/notice.prn260122a.html'),
}


def srcs(*keys):
    return [SRC[k] for k in keys]


# --------------------------------------------------------------------------
# THE GUIDES
# --------------------------------------------------------------------------
GUIDES = [
    {
        "slug": "assisted-living-cost-illinois",
        "title": "What Assisted Living Actually Costs in Evanston and Illinois",
        "h1": "What assisted living actually costs in Evanston and Illinois",
        "desc": ("Illinois assisted living runs a median of " + F["al_median"] +
                 " a month. Here is what that figure includes, what it leaves out, "
                 "and the costs that appear after you move in."),
        "intent": "cost research",
        "answer": ("The median cost of assisted living in Illinois is <strong>" +
                   F["al_median"] + " a month</strong>, according to the CareScout 2025 "
                   "Cost of Care Survey. That number is a starting point, not a quote. "
                   "What a family actually pays depends on the level of care assessed, "
                   "whether a second person is living in the apartment, and a one-time "
                   "community fee that the monthly figure never includes."),
        "sources": srcs("carescout", "hfs_slf"),
        "body": [
            ("What the median actually measures", [
                "<p>A median is the middle of a range. Half of Illinois communities "
                "charge more than " + F["al_median"] + " a month and half charge less. "
                "It is a statewide figure, not an Evanston figure. CareScout publishes no "
                "separate median for Evanston or for the north-shore suburbs, so this "
                "guide will not tell you how local prices compare — it does not know. "
                "Treat the statewide median as the number that tells you whether a quote "
                "is roughly normal, not as the number you will pay.</p>",
                "<p>For comparison, the same survey puts the Illinois nursing home "
                "median at <strong>" + F["nh_semi"] + " a month</strong> for a "
                "semi-private room and <strong>" + F["nh_private"] + "</strong> for a "
                "private room. Those are different levels of care, not different prices "
                "for the same thing.</p>",
                "<p>There is no Illinois median published for independent living, and "
                "this guide does not invent one. Where a reliable figure does not exist, "
                "saying so is more useful than filling the gap.</p>",
            ]),
            ("The four costs that surprise families", [
                "<p><strong>A community fee.</strong> A one-time charge at move-in, "
                "separate from rent. Ask for the amount in writing and ask whether any "
                "part of it is refundable if your parent leaves within a few months.</p>",
                "<p><strong>Care levels.</strong> Most communities assess a resident and "
                "assign a care tier that is billed on top of the base rate. The tier can "
                "change after a fall, a hospital stay, or a medication change. Ask what "
                "each tier costs, what moves someone between tiers, and who decides.</p>",
                "<p><strong>A second person.</strong> If both parents move in, there is "
                "almost always a second-occupant fee. It is rarely on the brochure.</p>",
                "<p><strong>The annual increase.</strong> Ask what the rate rose by in "
                "each of the last three years. A community that cannot answer that "
                "question has told you something.</p>",
            ]),
            ("What this means in Evanston", [
                "<p>A statewide median cannot tell you what any one Evanston community "
                "charges, and the spread between communities is wider than a single "
                "number suggests. Rather than guess at a local average, get the actual "
                "numbers from the actual buildings — there are not many of them, and they "
                "will quote you.</p>",
                "<p>The practical move is to collect three written quotes that each "
                "itemise base rent, the current care tier, the community fee and the "
                "second-person fee. Comparing all-in monthly totals is the only "
                "comparison that means anything.</p>",
            ]),
            ("If paying privately is not realistic", [
                "<p>Illinois runs a Medicaid programme that pays for care in approved "
                "assisted-living-style settings, called the Supportive Living Program. "
                "It is not the same as private-pay assisted living and not every "
                "community participates. It is explained in detail in "
                '<a href="/guides/illinois-supportive-living-program/">Illinois '
                "Supportive Living Program, explained</a>.</p>",
                "<p>Medicare does not pay for assisted living. That surprises most "
                "families, and the reason is worth understanding before you plan around "
                'it — see <a href="/guides/does-medicare-pay-for-senior-care/">Does '
                "Medicare pay for assisted living or nursing home care?</a></p>",
            ]),
        ],
    },

    {
        "slug": "does-medicare-pay-for-senior-care",
        "title": "Does Medicare Pay for Assisted Living or Nursing Home Care?",
        "h1": "Does Medicare pay for assisted living or nursing home care?",
        "desc": ("Medicare does not pay for assisted living. It pays for a qualifying "
                 "skilled nursing stay — " + F["snf_coins"] + " a day for days 21 to 100 "
                 "in 2026. Here is exactly what is and is not covered."),
        "intent": "coverage question",
        "answer": ("<strong>Medicare does not pay for assisted living</strong>, and it "
                   "does not pay for <strong>long-term custodial</strong> nursing home "
                   "care. It pays only for short-term "
                   "<em>skilled</em> nursing care after a qualifying hospital stay: days "
                   "1&ndash;20 cost <strong>$0</strong>, days 21&ndash;100 cost "
                   "<strong>" + F["snf_coins"] + " each day</strong> in 2026, and from "
                   "day 101 you pay everything."),
        "sources": srcs("mcosts", "msnf", "jimmo"),
        "body": [
            ("The distinction that decides everything", [
                "<p>Medicare divides care into <em>skilled</em> and <em>custodial</em>, "
                "and that single distinction decides whether it pays anything at all.</p>",
                "<p><strong>Skilled care</strong> is nursing or therapy that, in "
                "Medicare's own words, can only be safely and effectively performed by "
                "or under the supervision of licensed professionals — intravenous "
                "medication, wound care, physical therapy after a fracture. "
                "<strong>Custodial care</strong> is help with bathing, dressing, eating, "
                "getting to the toilet, medication reminders and supervision.</p>",
                "<p>Medicare pays for skilled care, short-term, under conditions listed "
                "below. It pays <strong>nothing</strong> toward custodial care, however "
                "much of it someone needs and however long they paid into the system. "
                "Assisted living is custodial care. That is the whole reason Medicare "
                "does not cover it.</p>",
                "<p><strong>It is not the building that decides this — it is the stay.</strong> "
                "The same nursing home room can be covered one month and not the next. "
                "A qualifying short-term rehabilitation stay in a Medicare-certified "
                "facility is covered. If that same resident stays on in that same bed "
                "because they can no longer live alone, the stay has become long-term "
                "custodial care and Medicare pays none of it. Families who were told "
                "\"Medicare is covering mom’s nursing home\" are almost always "
                "describing the first situation and planning for the second.</p>",
            ]),
            ("The five conditions, all of which must hold", [
                "<p>Medicare requires every one of these for a skilled nursing stay to "
                "be covered. One missing condition is enough to make the whole stay "
                "private-pay:</p>",
                "<ul class=\"res__list\">"
                "<li>A <strong>qualifying inpatient hospital stay</strong> — at least "
                "3 days in a row, counting from the day of inpatient admission and not "
                "counting the day of discharge</li>"
                "<li>Admission to the facility <strong>generally within 30 days</strong> "
                "of leaving the hospital</li>"
                "<li>A doctor&rsquo;s decision that <strong>daily skilled care</strong> "
                "is needed</li>"
                "<li>The care given in a <strong>Medicare-certified</strong> skilled "
                "nursing facility</li>"
                "<li>Skilled services for a condition treated during that hospital stay, "
                "or one that arose while being treated for it</li></ul>",
                "<p><strong>The trap inside the first condition.</strong> Hours spent "
                "under observation or in the emergency room do not count toward the three "
                "days, even if your parent was in a hospital bed overnight. A family can "
                "spend four days in a hospital and have zero qualifying days. Ask, out "
                "loud, on the first day: <em>has my parent been admitted as an inpatient, "
                "or are they under observation?</em> Then ask again, because the status "
                "can be changed.</p>",
                "<p>Two exceptions exist. A doctor in an Accountable Care Organization "
                "with a Skilled Nursing Facility 3-Day Rule Waiver may not need the three "
                "days, and Medicare Advantage plans may waive it too. Ask the hospital "
                "and ask the plan — neither will volunteer it.</p>",
            ]),
            ("What a covered skilled nursing stay costs in 2026", [
                "<p>These are the costs of a <em>qualifying skilled</em> stay only. "
                "Nothing below applies to long-term custodial care, assisted living or "
                "memory care, where the Medicare share is zero. On a covered stay, Part A "
                "pays on this schedule:</p>",
                "<ul class=\"res__list\">"
                "<li><strong>Days 1&ndash;20:</strong> $0 coinsurance each day. The Part A "
                "deductible of " + F["partA_deductible"] + " may still apply for the "
                "benefit period &mdash; &ldquo;$0 coinsurance&rdquo; is not "
                "&ldquo;free&rdquo;</li>"
                "<li><strong>Days 21&ndash;100:</strong> " + F["snf_coins"] +
                " each day</li>"
                "<li><strong>Day 101 and beyond:</strong> you pay all costs</li></ul>",
                "<p>You do not pay the Part A deductible twice. If it was already paid "
                "during the hospital stay in the same benefit period, it is not charged "
                "again for the skilled nursing stay.</p>",
                "<p>Run the arithmetic before you rely on the 100 days. A full run of "
                "days 21 to 100 is <strong>" + F["snf_total_80"] + " out of pocket</strong>, "
                "and coverage stops entirely at day 101.</p>",
                "<p>If your parent has a Medicare Advantage plan rather than Original "
                "Medicare, the rules differ — some plans charge copayments during the "
                "first 20 days. Ask the plan directly, in writing.</p>",
            ]),
            ("Coverage can end early — but not for the reason you will be told", [
                "<p>Coverage can stop before day 100. Families are often told it is "
                "ending because their parent <em>has stopped improving</em>. "
                "<strong>That is not the standard.</strong></p>",
                "<p>Under the <em>Jimmo v. Sebelius</em> settlement, CMS confirmed there "
                "is no &ldquo;Improvement Standard&rdquo;. Coverage does not turn on "
                "whether someone has potential to get better. It turns on whether they "
                "need skilled care. Skilled nursing and skilled therapy are covered "
                "where those services are needed to <strong>maintain</strong> the "
                "person&rsquo;s current condition, or to prevent or slow further "
                "deterioration, safely and effectively — even when no improvement "
                "is expected at all.</p>",
                "<p>Coverage <em>does</em> properly end when the requirements for skilled "
                "care are no longer met — for example, when the care a resident "
                "needs can be delivered safely and effectively by non-skilled staff, or "
                "when the 100 covered days in the benefit period run out. That is a "
                "different test, and it is the correct one.</p>",
                "<p>So the practical move is two sentences long. Ask the discharge "
                "planner on day one what length of covered stay is expected, and ask to "
                "be told in writing the moment that assessment changes. If the reason "
                "given is that your parent is no longer improving, say the word "
                "<em>Jimmo</em>, ask for the decision in writing, and ask how to appeal. "
                "A written notice is what gives you weeks instead of days.</p>",
            ]),
            ("So who does pay for assisted living?", [
                "<p>Three realistic sources. Private funds, including savings, pension "
                "income and the proceeds of a house. A long-term care insurance policy, "
                "if one was bought years ago. Or Illinois Medicaid, through the "
                '<a href="/guides/illinois-supportive-living-program/">Supportive Living '
                "Program</a>, which does pay for care in approved settings.</p>",
                "<p>For what private payment actually costs in this state, see "
                '<a href="/guides/assisted-living-cost-illinois/">What assisted living '
                "actually costs in Evanston and Illinois</a>.</p>",
            ]),
        ],
    },

    {
        "slug": "illinois-supportive-living-program",
        "title": "Illinois Supportive Living Program Explained",
        "h1": "Illinois Supportive Living Program, explained",
        "desc": ("Illinois Medicaid pays for care in approved Supportive Living "
                 "facilities. It covers services, not room and board. Expect two "
                 "charges, and a " + F["pna"] + " monthly personal needs allowance."),
        "intent": "Illinois Medicaid programme",
        "answer": ("The Supportive Living Program is how Illinois Medicaid pays for "
                   "assisted-living-style care. It covers the <strong>cost of "
                   "services</strong> in an approved Supportive Living facility. The "
                   "resident pays a state-set room and board charge, plus a "
                   "<strong>group care credit</strong> calculated from their own income, "
                   "and keeps a personal needs allowance of <strong>" + F["pna"] +
                   " a month</strong>."),
        "sources": srcs("hfs_slf", "hfs_rb", "hfs_hcbs", "hfs_slp_rates"),
        "body": [
            ("What it is, and what it is not", [
                "<p>A Supportive Living facility is not the same thing as a private-pay "
                "assisted living community, and it is not a nursing home. It is a "
                "separate category of setting, approved by the state, where Medicaid pays "
                "for the care a resident receives.</p>",
                "<p>Not every assisted living community in Illinois participates. A "
                "community can be excellent and still not be a Supportive Living "
                "facility. Ask directly, early, because it decides whether a place is "
                "financially possible at all.</p>",
            ]),
            ("How the money actually works", [
                "<p><strong>Expect two charges, not one.</strong> The first is room "
                "and board, which stays the resident's responsibility. Illinois sets it "
                "statewide and adjusts it each year with the Social Security "
                "cost-of-living increase: <strong>" + F["hfs_room_board"] + " a month"
                "</strong> for single occupancy and <strong>" + F["hfs_double"] +
                "</strong> for double occupancy, effective 1 January 2026.</p>",
                "<p>The second is the <strong>group care credit</strong>, also called "
                "patient liability. It is not a fixed price and it is not the same for "
                "two residents of the same building. The state calculates it from that "
                "resident's own countable income after allowable deductions — health "
                "insurance premiums, certain medical expenses, the room and board "
                "portion, and the " + F["pna"] + " personal needs allowance. Whatever "
                "remains is paid monthly toward the cost of care, and Medicaid covers "
                "the rest.</p>",
                "<p>So there is no sum on this page that produces your parent's figure, "
                "and any site that offers you one is guessing. The amount owed is "
                "determined by the state for that individual, from documents you have "
                "not filed yet. What you can know in advance is the method, the two "
                "charges, and the one thing that is fixed: the <strong>" + F["pna"] +
                " personal needs allowance</strong> a resident keeps for everything "
                "personal — clothing, haircuts, a phone, gifts for grandchildren. Most "
                "residents owe both charges; a resident avoids the group care credit "
                "only when their income equals the SSI amount.</p>",
            ]),
            ("Questions worth asking before you apply", [
                "<ul class=\"res__list\">"
                "<li>Is this specific community an approved Supportive Living facility?</li>"
                "<li>Is there a waiting list, and how long is it in practice?</li>"
                "<li>What is the room and board amount at this facility?</li>"
                "<li>What happens if my parent's needs exceed what this setting "
                "provides?</li>"
                "<li>Who at the facility helps with the application, and what do we need "
                "to gather first?</li></ul>",
                "<p>Eligibility rules, income tests and asset limits change, and they "
                "are decided by the state rather than by any community. Confirm current "
                "figures with Illinois HFS or a benefits counsellor before making any "
                "financial decision. This guide explains how the programme works; it is "
                "not an eligibility determination.</p>",
            ]),
            ("How this fits the rest of the picture", [
                "<p>If you are comparing this against paying privately, "
                '<a href="/guides/assisted-living-cost-illinois/">What assisted living '
                "actually costs in Evanston and Illinois</a> has the private-pay "
                "medians.</p>",
                "<p>If you are hoping Medicare will cover some of it, read "
                '<a href="/guides/does-medicare-pay-for-senior-care/">Does Medicare pay '
                "for assisted living or nursing home care?</a> first. It does not, and "
                "planning around the belief that it might costs families months.</p>",
            ]),
        ],
    },

    {
        "slug": "check-illinois-inspection-records",
        "title": "How to Check Illinois Nursing Home Inspection Records",
        "h1": "How to check an Illinois care community's inspection record",
        "desc": ("Illinois publishes inspection and complaint records for licensed "
                 "facilities, and Medicare publishes staffing and quality data. Here is "
                 "how to look up any community before you visit."),
        "intent": "how-to / due diligence",
        "answer": ("Two free public tools. The <strong>Illinois Department of Public "
                   "Health Health Care Report Card</strong> publishes inspection and "
                   "complaint information for licensed Illinois facilities. "
                   "<strong>Medicare Care Compare</strong> publishes staffing levels, "
                   "inspection findings and quality measures for Medicare-certified "
                   "nursing homes. Check both before you tour anywhere."),
        "sources": srcs("idph", "mcompare"),
        "body": [
            ("Start with the state", [
                "<p>The Illinois Department of Public Health licenses and inspects "
                "long-term care facilities in this state and publishes what it finds. "
                "Search the Health Care Report Card by facility name or location.</p>",
                "<p>What you are looking for is not a perfect record — almost nobody has "
                "one. You are looking for <em>patterns</em>. A single citation three "
                "years ago that was corrected is noise. The same category of problem "
                "appearing in consecutive inspections is a signal.</p>",
            ]),
            ("Then check Medicare Care Compare", [
                "<p>Medicare Care Compare covers Medicare-certified nursing homes and "
                "publishes something the state tool does not emphasise: reported staffing "
                "levels, including registered nurse hours per resident per day, and "
                "staff turnover.</p>",
                "<p>Staffing is the measure most closely tied to daily experience, "
                "and turnover is worth understanding rather than predicting. A turnover "
                "rate describes the staff of a building over a year. It does not tell "
                "you how often one resident will meet someone new, and this guide will "
                "not pretend otherwise — a high-turnover community can still have a "
                "stable team on one floor, and a low-turnover one can rotate your "
                "parent&rsquo;s aide weekly.</p>",
                "<p>What the number is genuinely useful for is as a question, not a "
                "verdict. Bring it to the visit. Ask who would be caring for your parent "
                "on a weekday morning, how long those specific people have worked there, "
                "how shifts are assigned, and how often agency staff fill in. Compare the "
                "answers to the published figure. A community whose answers match its "
                "data has told you something real; so has one where they do not.</p>",
                "<p>Note the scope limit honestly: Care Compare covers nursing homes. "
                "Assisted living is licensed by the state rather than Medicare-certified, "
                "so for assisted living the Illinois tool is the one that applies.</p>",
            ]),
            ("Reading a record without panicking", [
                "<ul class=\"res__list\">"
                "<li><strong>Check the date.</strong> A finding from four years ago under "
                "different management is weaker evidence than one from last quarter.</li>"
                "<li><strong>Check severity.</strong> Citations are scaled. A paperwork "
                "deficiency is not a resident-harm finding.</li>"
                "<li><strong>Check whether it recurred.</strong> Correction is normal. "
                "Repetition is the problem.</li>"
                "<li><strong>Take it with you.</strong> Print the record and ask the "
                "community about a specific finding on your visit. How they answer tells "
                "you as much as the finding did.</li></ul>",
            ]),
            ("Check every community, including ours", [
                "<p>This guide is written by someone who works at Westminster Place. "
                "That is exactly why this page exists and why it names the tools plainly: "
                "<strong>look Westminster Place up too.</strong> Run the same searches, "
                "read the same records, and ask the same questions there that you would "
                "ask anywhere else.</p>",
                "<p>A resource that tells you how to check everyone except the author's "
                "own employer would not be worth reading.</p>",
                "<p>For what to look at with your own eyes once you are inside a "
                'building, the <a href="/">free six-question assessment</a> ends with '
                "observations and questions specific to the level of care your parent may "
                "need.</p>",
            ]),
        ],
    },

    {
        "slug": "levels-of-senior-care-explained",
        "title": "Assisted Living vs. Memory Care vs. Skilled Nursing vs. Rehabilitation",
        "h1": "Assisted living, memory care, skilled nursing and rehabilitation &mdash; what is the difference?",
        "desc": ("Four phrases used as if they mean the same thing. They do not. Here is "
                 "what each one provides, who it is for, and how to tell which your "
                 "parent may need."),
        "intent": "definitional comparison",
        "answer": ("<strong>Assisted living</strong> is daily help with bathing, dressing "
                   "and medication, in a resident's own apartment. <strong>Memory "
                   "care</strong> is a secured setting with dementia-trained staff, where "
                   "the question is safety rather than help. <strong>Skilled "
                   "nursing</strong> is licensed nursing care around the clock. "
                   "<strong>Short-term rehabilitation</strong> is therapy after a hospital "
                   "stay, measured in weeks, with going home as the goal."),
        "sources": srcs("carescout", "msnf", "idph"),
        "body": [
            ("Assisted living", [
                "<p>Hands-on help with the things that happen every day — bathing, "
                "dressing, medications — while someone keeps their own apartment and as "
                "much independence as possible. Services vary enormously between "
                "communities, which is why two places with the same label can be very "
                "different.</p>",
                "<p>Illinois median: <strong>" + F["al_median"] + " a month</strong>. "
                "Medicare does not cover it.</p>",
            ]),
            ("Memory care", [
                "<p>Structured support for significant memory or cognitive change, "
                "usually in a secured area with staff trained in dementia care. The "
                "deciding question is not how much help someone needs but whether they "
                "are safe — wandering, leaving the stove on, not recognising where they "
                "are.</p>",
                "<p>CareScout does not publish a separate Illinois memory care median, "
                "so this guide does not state one. In practice it is generally priced "
                "above assisted living in the same community; ask for the specific "
                "figure in writing.</p>",
            ]),
            ("Skilled nursing", [
                "<p>Licensed nursing available 24 hours a day, for medical and physical "
                "needs beyond what assisted living provides. A medical setting — usually "
                "a room rather than an apartment.</p>",
                "<p>Illinois median: <strong>" + F["nh_semi"] + " a month</strong> "
                "semi-private, <strong>" + F["nh_private"] + "</strong> private. Medicare "
                "covers a <em>short</em> skilled stay after a qualifying hospital "
                "admission, not long-term residence.</p>",
            ]),
            ("Short-term rehabilitation", [
                "<p>Physical, occupational and speech therapy after illness, surgery or "
                "a hospital stay. A stay measured in weeks, with going home as the goal. "
                "It is delivered in a skilled nursing setting, which is why the two get "
                "confused.</p>",
                "<p>This is the one Medicare may cover, under conditions. The schedule "
                "and the limits are set out in "
                '<a href="/guides/does-medicare-pay-for-senior-care/">Does Medicare pay '
                "for assisted living or nursing home care?</a></p>",
            ]),
            ("How to tell which one applies", [
                "<p>The honest answer is that it depends on specifics — what someone can "
                "still do alone, what has changed recently, whether there has been a "
                "hospital stay, and whether safety is the concern rather than help.</p>",
                "<p>The <a href=\"/\">free six-question assessment</a> on this site walks "
                "through those specifics and shows which level the answers point to, "
                "along with the reasoning and the exact answers that produced it. It asks "
                "for no name, no email and no phone number, and nothing you enter leaves "
                "your device.</p>",
                "<p>It is an educational starting point, not a diagnosis. A doctor, a "
                "hospital discharge planner or a geriatric care manager can assess things "
                "no website can.</p>",
            ]),
        ],
    },

    {
        "slug": "illinois-community-care-program",
        "title": "Can My Parent Get Paid Help at Home in Illinois?",
        "h1": "Can my parent get paid help at home in Illinois?",
        "desc": ("Illinois pays for homemaker help, adult day service and emergency "
                 "response for some older adults who would otherwise need a nursing "
                 "home. Here is who qualifies and how to start."),
        "intent": "staying at home",
        "answer": ("Possibly. Illinois runs the <strong>Community Care Program</strong>, "
                   "which the Department on Aging describes as helping older adults "
                   "&ldquo;who might otherwise need nursing home care to remain in their "
                   "homes.&rdquo; It is for people <strong>60 or older</strong> with "
                   "<strong>non-exempt assets of " + F["ccp_assets"] + " or less</strong> "
                   "and an assessed need for long-term care. A house, a car and personal "
                   "furnishings are exempt from that asset figure. You start by calling "
                   "the Senior HelpLine on <strong>" + F["ccp_line"] + "</strong>."),
        "sources": srcs("idoa_ccp", "hfs_elderly"),
        "body": [
            ("What the programme actually provides", [
                "<p>The Community Care Program was established in 1979 by Public Act "
                "81-202. The Illinois Department on Aging lists five services under it: "
                "comprehensive care coordination, in-home service, adult day service, "
                "emergency home response service, and automated medication dispenser "
                "service.</p>",
                "<p><strong>In-home service</strong> is the one most families are "
                "picturing. The state describes it as help with household tasks — "
                "cleaning, planning and preparing meals, laundry, shopping and errands — "
                "and says homecare aides also assist with personal care such as "
                "dressing, bathing, grooming and following special diets.</p>",
                "<p><strong>Adult day service</strong> is for someone who wants to stay "
                "in the community but cannot be home alone during the day. It also gives "
                "a family caregiver hours back, which matters if you are the one holding "
                "this together from a job.</p>",
                "<p><strong>Emergency home response</strong> is a 24-hour link to help "
                "outside the home, for people with documented health and safety needs "
                "and mobility limitations. <strong>Automated medication dispenser "
                "service</strong> dispenses or prompts non-liquid oral medication and "
                "notifies a responsible party about a missed dose.</p>",
            ]),
            ("Who qualifies", [
                "<p>The Department on Aging lists these requirements. A person must be "
                "60 years old or older; a resident of Illinois; either a U.S. citizen or "
                "an eligible non-citizen within the specific categories; have non-exempt "
                "assets of <strong>" + F["ccp_assets"] + " or less</strong>; have an "
                "assessed need for long-term care; and apply for Medicaid and enrol if "
                "eligible.</p>",
                "<p>The asset figure is narrower than it sounds. The state states "
                "plainly that a home, a car and personal furnishings are classified as "
                "<em>exempt</em> assets, so owning the house your parent lives in does "
                "not by itself put them over the line.</p>",
                "<p>The need test is run with a state tool called the Determination of "
                "Need, or DON, which measures whether someone is at risk of nursing "
                "facility placement. This guide does not publish a passing score. The "
                "threshold is set by the state and applied by an assessor, and a number "
                "copied off a website is not the number that will decide your parent's "
                "case. Ask the assessor what the current threshold is.</p>",
            ]),
            ("The part that confuses everyone: two agencies, one programme", [
                "<p>You will see this called the Community Care Program in one place and "
                "the <strong>Persons who are Elderly waiver</strong> in another. They are "
                "not two programmes. Illinois HFS — the state Medicaid agency — states "
                "that the Persons who are Elderly waiver &ldquo;is a component of the "
                "Community Care Program (CCP) provided through the Illinois Department on "
                "Aging.&rdquo; HFS administers and oversees it; the Department on Aging "
                "runs it day to day.</p>",
                "<p>HFS also names the target groups inside that waiver: people who are "
                "aged, 65 and older, and people who are physically disabled, ages 60 "
                "through 64. And it lists two conditions the Aging page does not — that "
                "the estimated cost to the state for home care is less than the estimated "
                "cost of institutional care, and that the person can be safely maintained "
                "at home with the services in the plan of care.</p>",
                "<p>Read that second condition carefully, because it is the honest limit "
                "of this programme. It pays for help at home while home is still safe. It "
                "is not a promise that home will always be the answer.</p>",
            ]),
            ("How to start", [
                "<p>Call the <strong>Senior HelpLine</strong> on <strong>"
                + F["ccp_line"] + "</strong>. HFS instructs callers to choose a language "
                "and then press 4. Office hours are Monday to Friday, 8:30 to 5:00. For "
                "deaf and speech-impaired callers, Illinois Relay is <strong>711</strong>."
                "</p>",
                "<p>Assessments are carried out locally by organisations the state calls "
                "<strong>Care Coordination Units</strong>. The Department on Aging "
                "publishes a map tool for finding the one that covers your area, and that "
                "unit is who actually visits and scores the assessment. If your parent is "
                "already in a Medicaid managed care plan, HFS says to contact that plan's "
                "care coordinator about in-home services rather than going around them — "
                "and if you do call the local unit directly, tell them the plan name and "
                "have the identification number ready.</p>",
                "<p>One thing to know before you plan around any of this: HFS lists a "
                "proposed amendment to the waiver with an effective date of 1 January "
                "2027. Rules in this programme change. Confirm the current ones on the "
                "call rather than trusting a page — including this one.</p>",
            ]),
            ("When home help is not enough", [
                "<p>This programme and a move are not rivals, and plenty of families use "
                "one then the other. If the concern has shifted from <em>help</em> to "
                "<em>safety</em> — wandering, the stove, not recognising the house — "
                "homemaker hours are not the tool. "
                '<a href="/guides/levels-of-senior-care-explained/">Assisted living, '
                "memory care, skilled nursing and rehabilitation &mdash; what is the "
                "difference?</a> sets out what each setting actually provides.</p>",
                "<p>If the money is the obstacle rather than the care level, Illinois also "
                "pays for assisted-living-style care in approved buildings through a "
                "separate programme, explained in "
                '<a href="/guides/illinois-supportive-living-program/">Illinois '
                "Supportive Living Program, explained</a>.</p>",
                "<p>If you are not sure which of those two sentences describes your "
                'parent, the <a href="/">free six-question assessment</a> on this site '
                "walks through the specifics and shows you the reasoning behind its "
                "answer. It asks for no name, no email and no phone number to see your "
                "results.</p>",
            ]),
        ],
    },

    {
        "slug": "illinois-medicaid-long-term-care",
        "title": "How Illinois Medicaid Pays for Long-Term Care (and What Spend-Down Means)",
        "h1": "How Illinois Medicaid pays for long-term care, and what spend-down means",
        "desc": ("Illinois Medicaid can pay for nursing home and other long-term care. "
                 "Here is what it actually covers, how to apply, and what a "
                 "&ldquo;spend-down&rdquo; is for a family whose income or assets are "
                 "too high to qualify outright."),
        "intent": "paying for care",
        "answer": ("Yes, through the state's Medical Assistance Program. Illinois HFS "
                   "states plainly that &ldquo;payment for long-term nursing home "
                   "services may be available from the state of Illinois.&rdquo; To get "
                   "it, you apply for medical benefits through the <strong>Department of "
                   "Human Services (DHS)</strong> and get a needs screening through the "
                   "<strong>Department on Aging</strong> or DHS. If your income or assets "
                   "are above the limit, you may still qualify through "
                   "<strong>spenddown</strong> &mdash; a program HFS describes as working "
                   "&ldquo;a little like an insurance deductible,&rdquo; where medical "
                   "bills above a set monthly amount count toward eligibility."),
        "sources": srcs("hfs_ltc_clients", "hfs_ltc_providers", "hfs_spenddown",
                        "hfs_spousal2026", "hfs_elderly"),
        "body": [
            ("What Illinois Medicaid actually pays for", [
                "<p>Medicaid is not one single long-term-care benefit. The Illinois "
                "Medical Assistance Program reimburses long-term care facilities for "
                "specific categories of service, which HFS lists as: skilled nursing "
                "facility services, intermediate care facility services, intermediate "
                "care for people with developmental disabilities (including specialized "
                "living centers), pediatric skilled nursing, and supportive living "
                "facility services.</p>",
                "<p>In plain terms, that spans a licensed nursing home at one end and the "
                "state's assisted-living-style Supportive Living Program at the other. "
                "They are not interchangeable, and not every building accepts every "
                "category. "
                '<a href="/guides/illinois-supportive-living-program/">Illinois '
                "Supportive Living Program, explained</a> covers that middle option in "
                "its own right, and Illinois also pays for care at home through the "
                '<a href="/guides/illinois-community-care-program/">Community Care '
                "Program and the Persons who are Elderly waiver</a> rather than in a "
                "facility at all.</p>",
            ]),
            ("How to apply", [
                "<p>HFS sets out two separate steps, and both have to happen. You "
                "<strong>apply for medical benefits through the Department of Human "
                "Services (DHS)</strong>, and you <strong>obtain a needs screening "
                "through the Department on Aging (DoA) or DHS</strong>. One is the "
                "financial side of eligibility; the other confirms the person actually "
                "needs the level of care being paid for. HFS points applicants to its "
                "HFS 3191 brochure for the detailed eligibility steps.</p>",
                "<p>This is a state process run by caseworkers, not an online form you "
                "fill in once and forget. Expect to provide income and asset "
                "documentation, and expect a caseworker, not a website, to tell you "
                "exactly what is required in your parent's case.</p>",
            ]),
            ("What &ldquo;spend-down&rdquo; actually means", [
                "<p>Spend-down exists for people who would otherwise be turned away for "
                "having too much income or too many assets. HFS describes it this way: "
                "&ldquo;Spenddown works a little like an insurance deductible.&rdquo; "
                "Each month, you are responsible for the cost of medical care up to a "
                "set amount, based on your income and assets, before Medicaid coverage "
                "for that month applies.</p>",
                "<p>You do not necessarily have to pay that amount out of pocket in "
                "cash. HFS says a person can meet the monthly spenddown by showing a DHS "
                "caseworker <strong>unpaid medical bills</strong> &mdash; the bills "
                "themselves count toward the figure. Some recipients can also use "
                "&ldquo;pay-in&rdquo; spenddown, paying the amount directly to HFS "
                "instead of submitting bills; HFS describes this option as available to "
                "people enrolled in spenddown who are aged, blind, or have a disability "
                "and live in the community.</p>",
                "<p>This is the detail families miss: nursing home care is expensive "
                "enough that the monthly spend-down amount for someone in a facility is "
                "often met immediately by the facility's own bill. Spenddown is "
                "frequently the route by which a long nursing home stay ends up "
                "Medicaid-covered even when the same person would not have qualified for "
                "Medicaid the month before they were admitted.</p>",
            ]),
            ("Protecting a spouse who stays at home", [
                "<p>Federal and state rules exist specifically so that one spouse "
                "entering a nursing home does not force the other into poverty. Illinois "
                "HFS publishes updated dollar figures for this every year. For 2026, "
                "effective January 1, 2026, the <strong>Community Spouse Resource "
                "Allowance</strong> is <strong>" + F["csra_2026"] + "</strong> &mdash; "
                "the HFS notice describes this as the maximum amount of resources a "
                "resident may transfer to a community spouse, or to another for that "
                "spouse's sole benefit, before the resident's own eligibility is "
                "assessed. Alongside it, HFS sets a <strong>Community Spouse "
                "Maintenance Needs Allowance</strong> of <strong>" + F["csmna_2026"] +
                " a month</strong>, which protects a share of income for the spouse "
                "still living at home.</p>",
                "<p>These two figures change every year, and HFS reissues the notice "
                "each time. Do not rely on a figure copied from any article, including "
                "this one, once a year has passed &mdash; check the current HFS notice "
                "or ask the DHS caseworker handling the case.</p>",
            ]),
            ("A figure this guide will not publish", [
                "<p>Illinois law sets a monthly personal needs allowance for Medicaid "
                "nursing facility residents &mdash; a small amount of their own income "
                "protected for personal spending rather than put toward the cost of "
                "care. This guide went looking for the current figure on the HFS public "
                "notice that sets it, and could not read a verifiable number off that "
                "document. Rather than repeat a figure picked up secondhand, this guide "
                "leaves it out. Ask the nursing facility's business office or the DHS "
                "caseworker what the current personal needs allowance is before "
                "assuming any number you have seen elsewhere.</p>",
            ]),
            ("Where to go from here", [
                "<p>If the person you are helping is not yet in a facility and the "
                "question is whether they need to be, start with "
                '<a href="/guides/levels-of-senior-care-explained/">Assisted living, '
                "memory care, skilled nursing and rehabilitation &mdash; what is the "
                "difference?</a> If the question is what care costs before Medicaid "
                'enters the picture at all, see <a href="/guides/assisted-living-cost-illinois/">'
                "What assisted living actually costs in Evanston and Illinois</a> and "
                "Medicare's own limited role in "
                '<a href="/guides/does-medicare-pay-for-senior-care/">Does Medicare pay '
                "for senior care?</a></p>",
                "<p>If you are not sure which of those questions you are actually asking, "
                'the <a href="/">free six-question assessment</a> on this site walks '
                "through the specifics and shows the reasoning behind its answer. It "
                "asks for no name, no email and no phone number to see your results.</p>",
            ]),
        ],
    },
]


# --------------------------------------------------------------------------
# TEMPLATE
# --------------------------------------------------------------------------
HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{title} | Evanston Senior Care Guide</title>
<meta name="description" content="{desc}" />
<meta name="theme-color" content="#001e44" />
<link rel="canonical" href="{canon}" />
<meta property="og:title" content="{title}" />
<meta property="og:description" content="{desc}" />
<meta property="og:type" content="article" />
<meta property="og:url" content="{canon}" />
<meta property="og:site_name" content="Evanston Senior Care Guide" />
<meta property="og:image" content="{site}/og-card.png" />
<meta name="twitter:card" content="summary_large_image" />
<link rel="icon" href="/favicon.ico" sizes="any" />
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png" />
<link rel="apple-touch-icon" sizes="180x180" href="/favicon-180.png" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;0,9..144,600;1,9..144,300&family=Inter:wght@400;500;600&display=swap" rel="stylesheet" />
<link rel="stylesheet" href="/styles.css" />
{jsonld}
</head>
<body>

<nav class="nav" aria-label="Primary">
  <div class="wrap nav__inner">
    <a class="brand" href="/" aria-label="Evanston Senior Care Guide, home">
      <span class="brand__mark" aria-hidden="true">
        <img class="brand__logo" src="/favicon-180.png" width="34" height="34"
             alt="" decoding="async" />
      </span>
      <span class="brand__text">
        <span class="brand__name">Evanston Senior Care</span>
        <span class="brand__sub">Evanston, Illinois</span>
      </span>
    </a>
    <div class="nav__links">
      <a href="/guides/">Care Guides</a>
      <button class="nav__toggle" id="navToggle" type="button"
              aria-expanded="false" aria-controls="navMenu">
        <span class="nav__toggle-bars" aria-hidden="true"><span></span><span></span><span></span></span>
        Menu
      </button>
      <a class="nav__cta" href="/#assessment"><span class="nav__cta-long">Start assessment</span><span class="nav__cta-short">Start</span></a>
    </div>
  </div>
  <div class="nav__menu" id="navMenu" hidden>
    <div class="wrap">
      <a href="/">Home</a>
      <a href="/guides/">Care Guides</a>
      <a href="/#assessment">Start assessment</a>
    </div>
  </div>
</nav>

<main class="band">
  <div class="wrap {wrapcls}">
"""

FOOT = """  </div>
</main>

<footer class="foot">
  <div class="wrap">
    <p class="foot__name">Evanston Senior Care Guide</p>
    <p>Independently developed by an employee of Westminster Place. This is not
      an official Westminster Place website. I receive no referral fees from
      Westminster Place. If you ask to be contacted about a tour, your details
      are passed to their Admissions team because that is what you asked for;
      nothing is passed on unless you tick that permission box.</p>
    <p class="foot__fine">These guides are educational and are not medical,
      legal or financial advice. Confirm anything that matters with the agency,
      plan or provider directly. <a class="foot__link" href="/privacy.html">Privacy
      notice</a></p>
  </div>
</footer>

<script src="/nav.js"></script>
</body>
</html>
"""


def article_jsonld(g, canon):
    return ('<script type="application/ld+json">\n{\n'
            '  "@context": "https://schema.org",\n'
            '  "@type": "Article",\n'
            '  "headline": %s,\n'
            '  "description": %s,\n'
            '  "url": %s,\n'
            '  "inLanguage": "en-US",\n'
            '  "isAccessibleForFree": true,\n'
            '  "dateModified": "%s",\n'
            '  "author": {\n'
            '    "@type": "Person",\n'
            '    "name": "Joseph Gonzales",\n'
            '    "description": "Independent developer of the Evanston Senior Care '
            'Guide. Employed at Westminster Place; the guide is not an official '
            'Westminster Place website and receives no referral fees."\n'
            '  },\n'
            '  "publisher": { "@type": "Person", "name": "Joseph Gonzales" },\n'
            '  "about": { "@type": "Thing", "name": "Senior care in Evanston, Illinois" }\n'
            '}\n</script>') % (
        js(g["title"]), js(strip_tags(g["desc"])), js(canon), REVIEWED)


def js(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


def strip_tags(s):
    return re.sub(r"<[^>]+>", "", s)


def related(g):
    others = [x for x in GUIDES if x["slug"] != g["slug"]][:3]
    items = "".join(
        '<li><a href="/guides/%s/">%s</a></li>' % (o["slug"], o["h1"].replace("&mdash;", "—"))
        for o in others)
    return ('<section class="res__block">\n'
            '<h2 class="res__h">Related guides</h2>\n'
            '<ul class="res__list">%s</ul>\n</section>' % items)


def sources_block(g):
    items = "".join(
        '<li><a href="%s" rel="noopener" target="_blank">%s</a></li>' % (url, name)
        for name, url in g["sources"])
    return ('<section class="res__block">\n'
            '<h2 class="res__h">Sources</h2>\n'
            '<ul class="res__list">%s</ul>\n'
            '<p class="visit__fine">Every figure on this page was read from the '
            'source listed above on %s. Figures change; the review date tells you '
            'how fresh this page is.</p>\n</section>' % (items, REVIEWED_HUMAN))


def build_guide(g):
    canon = "%s/guides/%s/" % (SITE, g["slug"])
    parts = [HEAD.format(title=g["title"], desc=strip_tags(g["desc"]),
                         canon=canon, site=SITE, jsonld=article_jsonld(g, canon),
                         wrapcls="narrow")]
    parts.append('<p class="eyebrow"><a href="/guides/">Care Guides</a></p>\n')
    parts.append('<h1 class="h2">%s</h1>\n' % g["h1"])
    parts.append('<div class="res__why">\n<p class="res__why-label">Short answer</p>\n'
                 '<p>%s</p>\n</div>\n' % g["answer"])
    lead = DIAGRAMS.get((g["slug"], None))
    if lead:
        parts.append(lead + "\n")
    for heading, paras in g["body"]:
        dia = DIAGRAMS.get((g["slug"], strip_tags(heading)))
        body = "\n".join(paras) + (("\n" + dia) if dia else "")
        parts.append('<section class="res__block">\n<h2 class="res__h">%s</h2>\n%s\n</section>\n'
                     % (heading, body))
    parts.append(sources_block(g) + "\n")
    parts.append(related(g) + "\n")
    parts.append('<section class="res__block plan plan--primary">\n'
                 '<h2 class="res__h plan__h">Not sure which level of care applies?</h2>\n'
                 '<p class="plan__lead">Six questions, about two minutes. It asks for no '
                 'name, no email and no phone number, and your answers never leave your '
                 'device.</p>\n'
                 '<p><a class="btn btn--primary" href="/#assessment">Take the free '
                 'assessment</a></p>\n</section>\n')
    parts.append('<p class="visit__fine">Last reviewed %s.</p>\n' % REVIEWED_HUMAN)
    parts.append(FOOT)
    return "".join(parts)


from diagrams import DIAGRAMS


CARDS = {
    "assisted-living-cost-illinois": (
        "Costs",
        "What assisted living actually costs in Illinois",
        "The statewide median, what it does and does not include, and the "
        "four charges that appear after you move in."),
    "does-medicare-pay-for-senior-care": (
        "Medicare",
        "Does Medicare pay for assisted living or nursing home care?",
        "What Medicare covers, what it never covers, and the one reason "
        "families are most often given wrongly when coverage ends."),
    "illinois-supportive-living-program": (
        "Paying with Medicaid",
        "Illinois Supportive Living Program, explained",
        "How Illinois Medicaid pays for assisted-living-style care, and the "
        "two separate charges a resident should expect."),
    "check-illinois-inspection-records": (
        "Checking a community",
        "How to check a community\u2019s inspection record",
        "Two free public tools, where to find them, and how to read what you "
        "find without panicking."),
    "levels-of-senior-care-explained": (
        "Getting oriented",
        "What is the difference between each level of care?",
        "Assisted living, memory care, skilled nursing and rehabilitation in "
        "plain English, so you know what you are comparing."),
    "illinois-community-care-program": (
        "Staying at home",
        "Can my parent get paid help at home in Illinois?",
        "Illinois pays for homemaker help, adult day service and emergency "
        "response for some older adults. Who qualifies, and how to start."),
    "illinois-medicaid-long-term-care": (
        "Paying with Medicaid",
        "How Illinois Medicaid pays for long-term care",
        "What Medicaid actually covers, how to apply, and what "
        "“spend-down” means if income or assets are too high to "
        "qualify outright."),
}


def topic_card(g):
    """One card. The anchor sits on the title and its ::after is stretched
    over the whole surface, so the card is clickable with ONE tab stop and
    one accessible name - no duplicate links for a crawler or a screen
    reader to wade through, and the crawlable href never moves."""
    cat, title, blurb = CARDS[g["slug"]]
    return ('<li class="topic">\n'
            '  <p class="topic__cat">%s</p>\n'
            '  <h2 class="topic__h"><a href="/guides/%s/">%s</a></h2>\n'
            '  <p class="topic__p">%s</p>\n'
            '  <p class="topic__go">Read article '
            '<span class="topic__arrow" aria-hidden="true">&rarr;</span></p>\n'
            '</li>\n' % (cat, g["slug"], title, blurb))


def build_index():
    canon = SITE + "/guides/"
    cards = ('<ul class="topics">\n'
             + "".join(topic_card(g) for g in GUIDES)
             + '</ul>\n')
    jsonld = ('<script type="application/ld+json">\n{\n'
              '  "@context": "https://schema.org",\n'
              '  "@type": "CollectionPage",\n'
              '  "name": "Senior care guides for Evanston families",\n'
              '  "url": %s,\n'
              '  "inLanguage": "en-US",\n'
              '  "isAccessibleForFree": true\n}\n</script>') % js(canon)
    head = HEAD.format(
        title="Senior care guides for Evanston families",
        desc=("Plain-English guides to the cost of assisted living in Illinois, what "
              "Medicare covers, the Supportive Living Program, and how to check a "
              "community's inspection record."),
        canon=canon, site=SITE, jsonld=jsonld, wrapcls="")
    return (head
            + '<p class="eyebrow">Care Guides</p>\n'
            + '<h1 class="h2">Find answers about senior care</h1>\n'
            + '<p class="topics__lead">Pick the question that is on your mind. Each '
              'one is a short, plain-English answer to something families ask when a '
              'parent needs more help \u2014 and every figure in them is read from a '
              'government or survey source and dated, so you can see how current it '
              'is.</p>\n'
            + cards
            + '<p class="visit__fine">Last reviewed %s.</p>\n' % REVIEWED_HUMAN
            + FOOT)


def build_sitemap():
    """Generated from the GUIDES list — adding a guide updates the sitemap."""
    urls = [(SITE + "/", "1.0", "monthly"),
            (SITE + "/guides/", "0.8", "monthly")]
    urls += [(SITE + "/guides/%s/" % g["slug"], "0.7", "yearly") for g in GUIDES]
    urls.append((SITE + "/privacy.html", "0.3", "yearly"))
    body = "".join(
        "  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n"
        "    <changefreq>%s</changefreq>\n    <priority>%s</priority>\n  </url>\n"
        % (loc, REVIEWED, freq, pri) for loc, pri, freq in urls)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<!-- Generated by build-guides.py. Do not hand-edit: adding a guide to\n'
            '     the GUIDES list regenerates this file. -->\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + body + '</urlset>\n')


def main():
    os.makedirs(OUT, exist_ok=True)
    for g in GUIDES:
        d = os.path.join(OUT, g["slug"])
        os.makedirs(d, exist_ok=True)
        p = os.path.join(d, "index.html")
        io.open(p, "w", encoding="utf-8", newline="").write(build_guide(g))
        print("  %-42s %6d bytes" % ("/guides/%s/" % g["slug"],
                                     os.path.getsize(p)))
    p = os.path.join(OUT, "index.html")
    io.open(p, "w", encoding="utf-8", newline="").write(build_index())
    print("  %-42s %6d bytes" % ("/guides/", os.path.getsize(p)))
    io.open("_dist/sitemap.xml", "w", encoding="utf-8", newline="").write(build_sitemap())
    io.open("sitemap.xml", "w", encoding="utf-8", newline="").write(build_sitemap())
    print("  sitemap.xml regenerated with %d URLs" % (len(GUIDES) + 3))


if __name__ == "__main__":
    main()
