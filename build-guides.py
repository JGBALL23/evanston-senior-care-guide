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

EVERY FIGURE IN THIS FILE WAS READ FROM A PRIMARY SOURCE. The original five
guides were verified on 2026-10-18 against:
  - medicare.gov/basics/costs/medicare-costs        (Part A deductible, SNF)
  - medicare.gov/coverage/skilled-nursing-facility-snf-care
  - hfs.illinois.gov/medicalprograms/slf/residentfactsheet.html  (PNA, GCC)
  - CareScout 2025 Cost of Care Survey, published 2026 — the same PDF the
    assessment already cites, so the guides and the result pages can never
    disagree about a number.

Guides added later carry their own "reviewed" date and their own sources;
2026-10-23 added the Community Care Program and the Medicaid long-term-care
guide, the latter verified against four HFS pages including the 22 January
2026 spousal impoverishment notice.

Nothing here is from a lead-generation aggregator. If a figure cannot be
read from a government or survey primary source, it does not go on a page.

Run:  python build-guides.py
Writes: _dist/guides/*.html, _dist/guides/index.html, _dist/sitemap.xml
"""

import io, os, re, datetime

SITE = "https://evanstonseniorcareguide.com"
OUT = "_dist/guides"

# REVIEWED is the date the ORIGINAL five were verified against their sources.
# It is the default, not a global stamp. A guide written later carries its own
# "reviewed" key and prints its own date.
#
# Why this is per-guide: the date on a page is a factual claim about when a
# human or a tool last read the source. Bumping one global constant because
# ONE new guide was researched today would silently re-date six pages that
# nobody re-checked - exactly the kind of quiet, confident falsehood the rest
# of this file exists to prevent. A daily routine adding a guide must stamp
# only the guide it actually researched.
REVIEWED = "2026-10-18"
REVIEWED_HUMAN = "18 October 2026"


def reviewed_iso(g):
    return g.get("reviewed", REVIEWED)


def reviewed_human(g):
    d = datetime.date(*[int(x) for x in reviewed_iso(g).split("-")])
    return "%d %s %d" % (d.day, d.strftime("%B"), d.year)


def newest_reviewed():
    """The index and the sitemap describe the whole library, so they carry the
    most recent review date in it, not the oldest."""
    return max(reviewed_iso(g) for g in GUIDES)

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
    "hospice_zero": "$0",
    "hospice_rx_copay": "$5",
    "hospice_respite_coins": "5%",
    "va_mapr_basic_single": "$17,441",
    "va_mapr_hb_single": "$21,313",
    "va_mapr_aa_single": "$29,093",
    "va_mapr_basic_1dep": "$22,839",
    "va_mapr_hb_1dep": "$26,710",
    "va_mapr_aa_1dep": "$34,488",
    "va_networth_limit": "$163,699",
    "va_nh_medicaid_rate": "$90",
    "va_survivor_basic_single": "$11,699",
    "va_survivor_hb_single": "$14,298",
    "va_survivor_aa_single": "$18,697",
    "va_survivor_basic_1dep": "$15,311",
    "va_survivor_hb_1dep": "$17,902",
    "va_survivor_aa_1dep": "$22,304",
}

# DERIVED, never typed. VA publishes the Aid and Attendance rate annually; a
# family comparing it against a monthly care bill has to divide by twelve, and
# a hand-typed monthly figure is exactly the kind of number that drifts when
# the December COLA moves the annual one. Computed from the annual figure so
# the two can never disagree, and floored rather than rounded up so the
# comparison never overstates what VA pays.
F["va_mapr_aa_single_month"] = "$%s" % format(
    int(F["va_mapr_aa_single"].lstrip("$").replace(",", "")) // 12, ",")

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
    "idph_al_div": ('Illinois Department of Public Health \u2014 Assisted Living',
                    'https://dph.illinois.gov/topics-services/health-care-regulation/assisted-living.html'),
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
    "idoa_ombudsman": ('Illinois Department on Aging — Long-Term Care Ombudsman Program',
                       'https://ilaging.illinois.gov/programs/ltcombudsman.html'),
    "idoa_ombudsman_contact": ('Illinois Department on Aging — Office of the State Long-Term Care Ombudsman, contact information',
                               'https://ilaging.illinois.gov/programs/ltcombudsman/contact-information--office-of-the-state-long-term-care-ombudsma.html'),
    "idph_ccr": ('Illinois Department of Public Health — Health care facility complaints',
                'https://dph.illinois.gov/topics-services/health-care-regulation/complaints.html'),
    "hfs_estate_guide": ('Illinois HFS — Guide to the Medicaid Estate Recovery Program',
                        'https://hfs.illinois.gov/medicalclients/medicaidestaterecovery/guidetothemedicaidestaterecoveryprogram.html'),
    "hfs_estate_faq": ('Illinois HFS — Medicaid Estate Recovery, Frequently Asked Questions',
                       'https://hfs.illinois.gov/medicalclients/medicaidestaterecovery/faqs.html'),
    "hfs_estate_liens": ('Illinois HFS — Liens and Estate Recovery',
                        'https://hfs.illinois.gov/medicalclients/medicaidestaterecovery/liensandestaterecovery.html'),
    "mhospice": ('Medicare.gov — Hospice care',
                'https://www.medicare.gov/coverage/hospice-care'),
    "va_elig": ('VA.gov — Veterans Pension eligibility',
               'https://www.va.gov/pension/eligibility/'),
    "va_rates": ('VA.gov — Veterans Pension rates',
                'https://www.va.gov/pension/veterans-pension-rates/'),
    "va_aa": ('VA.gov — Aid and Attendance and Housebound benefits',
             'https://www.va.gov/pension/aid-attendance-housebound/'),
    "va_survivors": ('VA.gov — Survivors Pension',
                     'https://www.va.gov/pension/survivors-pension/'),
    "va_survivors_rates": ('VA.gov — Survivors Pension rates',
                           'https://www.va.gov/pension/survivors-pension-rates/'),
    "va_apply": ('VA.gov — How to apply for Veterans Pension benefits',
                'https://www.va.gov/pension/how-to-apply/'),
}


def srcs(*keys):
    return [SRC[k] for k in keys]


# --------------------------------------------------------------------------
# THE GUIDES
# --------------------------------------------------------------------------
GUIDES = [
    {
        "slug": "assisted-living-cost-illinois",
        "bridge": ("A price only means something once you know which kind of care "
               "you are pricing. The same parent can be quoted wildly different "
               "monthly figures depending on the level of care a community "
               "assesses them into."),
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
        "bridge": ("Knowing what Medicare covers is a different question from knowing "
               "what kind of care your parent actually needs. Coverage follows the "
               "care; it does not decide it."),
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
        "bridge": ("Supportive Living is one setting among several, and it only helps "
               "if it is the setting your parent needs. The programme cannot tell "
               "you whether it is."),
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
        "bridge": ("An inspection record tells you how well a community does its job. "
               "It cannot tell you whether that is the job your parent needs doing "
               "in the first place."),
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
        "bridge": ("Definitions are the easy half. Working out which of these four "
               "describes your own parent, with their particular habits and recent "
               "changes, is the harder one."),
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
        "bridge": ("This programme is built around staying at home, which is the right "
               "answer right up until it is not. The hard part is noticing which "
               "side of that line your parent is on."),
        # Researched on this date, not on the library's original review date.
        "reviewed": "2026-10-23",
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
        "bridge": ("Working out who pays is a separate problem from working out what "
               "your parent needs paying for. Most families end up doing both, and "
               "the second one usually comes first."),
        # Researched and verified in the cloud routine's own run on this date,
        # not on the library's original 2026-10-18 review date.
        "reviewed": "2026-10-23",
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
                "HFS publishes updated dollar figures for this every year, and for 2026, "
                "effective 1 January 2026, it sets two of them.</p>",
                "<p><strong>Neither figure is an amount anyone is promised.</strong> "
                "Both are ceilings. HFS calls each one a <em>standard</em> and a "
                "<em>maximum</em>, and in both cases the amount that actually applies to "
                "a particular couple is worked out by subtracting what the at-home "
                "spouse already has.</p>",
                "<p>The <strong>Community Spouse Resource Allowance</strong> standard is "
                "<strong>" + F["csra_2026"] + "</strong>. HFS describes it as the "
                "maximum amount of resources a resident may transfer to a community "
                "spouse, or to another for that spouse's sole benefit, and states that "
                "<q>the actual amount a resident may transfer is determined by deducting "
                "nonexempt resources of the community spouse from the standard</q>. So a "
                "spouse who already holds countable resources of their own can transfer "
                "less than " + F["csra_2026"] + " &mdash; possibly much less.</p>",
                "<p>The <strong>Community Spouse Maintenance Needs Allowance</strong> "
                "standard is <strong>" + F["csmna_2026"] + " a month</strong>. HFS "
                "describes it as the maximum monthly income a resident may give to a "
                "community spouse, and states that <q>the actual amount a resident may "
                "give is determined by deducting any gross income of the community "
                "spouse from the standard</q>. A spouse with their own pension or Social "
                "Security therefore receives the difference, not the full "
                + F["csmna_2026"] + ".</p>",
                "<p>This guide deliberately does not do that subtraction for you. It "
                "depends on which of a household's resources and income the state counts "
                "and which it exempts, and that determination belongs to the DHS "
                "caseworker, not to a website.</p>",
                "<p>Both standards change every year, and HFS reissues the notice each "
                "time. Do not rely on a figure copied from any article, including this "
                "one, once a year has passed &mdash; check the current HFS notice or ask "
                "the DHS caseworker handling the case.</p>",
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

    {
        "slug": "illinois-care-facility-complaint",
        "bridge": ("Some concerns are a problem with the care being given. Others are a "
               "sign the setting itself no longer matches what your parent needs. "
               "Those two look alike from the outside."),
        "reviewed": "2026-10-23",
        "title": "How to Report a Problem at an Illinois Nursing Home or Assisted Living Facility",
        "h1": "How to report a problem at an Illinois care facility",
        "desc": ("Illinois runs two separate channels for a concern about a nursing home "
                 "or assisted living community: a resident advocate who works the problem "
                 "with you, and a state regulator who investigates it. Here is which to "
                 "call, and when."),
        "intent": "how-to / advocacy",
        "answer": ("Two different state contacts, for two different jobs. The "
                   "<strong>Long-Term Care Ombudsman Program</strong>, run by the Illinois "
                   "Department on Aging, is a free, confidential, resident-directed "
                   "advocate &mdash; call the Senior HelpLine at <strong>1-800-252-8966 "
                   "(711 TRS)</strong>. The <strong>Illinois Department of Public Health's "
                   "Central Complaint Registry</strong> is the state regulator that "
                   "investigates facilities &mdash; call <strong>800-252-4343</strong>, "
                   "Monday&ndash;Friday 8:30 a.m. to 4:30 p.m. You do not have to choose "
                   "just one."),
        "sources": srcs("idoa_ombudsman", "idoa_ombudsman_contact", "idph_ccr"),
        "body": [
            ("Two kinds of help, and when to use each", [
                "<p>Families searching for how to complain about a care community "
                "usually find one of two very different state contacts, and the "
                "difference matters. One is an <strong>advocate</strong> who works for "
                "the resident and tries to resolve the problem informally. The other is "
                "a <strong>regulator</strong> who investigates and can act against the "
                "facility's licence. Neither replaces the other, and you can use both at "
                "once.</p>",
            ]),
            ("The Long-Term Care Ombudsman Program", [
                "<p>The Illinois Department on Aging describes its Long-Term Care "
                "Ombudsman Program as a &ldquo;resident-directed advocacy program,&rdquo; "
                "mandated by the federal Older Americans Act and the Illinois Act on "
                "Aging. Ombudsmen advocate for better care in Illinois long-term care "
                "facilities, help residents speak up for themselves, explain residents' "
                "rights, and investigate complaints to try to resolve them to the "
                "resident's satisfaction.</p>",
                "<p>Two things are worth knowing before you call. First, the program "
                "states plainly that its work is <em>directed by the resident</em> "
                "&mdash; it is not a service a family member sets in motion and then "
                "runs. Second, it keeps information confidential and will not disclose "
                "it without the individual's permission. The department's page lists "
                "current and former residents, their friends and relatives, facility "
                "staff, and anyone considering placement as people who may contact an "
                "ombudsman, and the service is free.</p>",
                "<p>To reach the program, call the Senior HelpLine at "
                "<strong>1-800-252-8966 (711 TRS)</strong> or email "
                "<strong>Aging.SLTCOProgram@illinois.gov</strong>. The department's "
                "contact page also lists direct numbers for the State Long-Term Care "
                "Ombudsman and deputy staff, but a family with a new concern should start "
                "with the HelpLine rather than guessing which named contact to use.</p>",
            ]),
            ("The Illinois Department of Public Health's Central Complaint Registry", [
                "<p>IDPH licenses and regulates health care facilities in Illinois, and "
                "its Central Complaint Registry is the channel for reporting a concern "
                "that may call for a state investigation rather than informal advocacy. "
                "The department's complaints page gives the hotline as "
                "<strong>800-252-4343</strong>, with hours of "
                "<strong>Monday&ndash;Friday 8:30 a.m. to 4:30 p.m.</strong></p>",
                "<p>The same page states that for a long-term care complaint "
                "specifically, that same number reaches the department's Bureau of "
                "Long-Term Care. Besides the phone line, the page lists three other ways "
                "to file: online through the OHCR Portal, by fax at 217-524-8885, or by "
                "e-mail to DPH.CCR@illinois.gov using the Health Care Facilities "
                "Complaint Form. Written complaints can also go by mail to the Illinois "
                "Department of Public Health, Office of Health Care Regulation, Central "
                "Complaint Registry, 525 W. Jefferson St., Ground Floor, Springfield, IL "
                "62761-0001.</p>",
                "<p>IDPH says your identity is not disclosed to the facility, and you "
                "may file anonymously or leave contact information to receive written "
                "notice of the outcome. Describing who, what, when, where and how gives "
                "investigators the most to work with.</p>",
            ]),
            ("A number this guide will not publish", [
                "<p>The Ombudsman Program's own page carries a separate navigation link "
                "reading &ldquo;Report Abuse: 1-866-800-1409,&rdquo; but the page itself "
                "never states what that line reaches or how it relates to the HelpLine "
                "number above it. Rather than guess at an unexplained number on a "
                "government page, this guide leaves it out. If you come across it "
                "elsewhere, confirm what it connects to with the Department on Aging "
                "before relying on it.</p>",
            ]),
            ("If someone is in immediate danger", [
                "<p>None of the above is the right channel for an emergency. If a "
                "resident's life or safety is at risk right now, call 911 first and make "
                "the state reports afterward.</p>",
            ]),
            ("Where this fits with the rest of this site", [
                "<p>Reporting a live concern is a different task from researching a "
                "community before you move in. For the latter, see "
                '<a href="/guides/check-illinois-inspection-records/">How to check an '
                "Illinois care community's inspection record</a>, which covers the public "
                "tools that publish a facility's inspection history before you need to "
                "report anything yourself.</p>",
            ]),
        ],
    },

    {
        "slug": "illinois-medicaid-estate-recovery",
        "bridge": ("Estate recovery is a question about money after the fact. It sits "
               "downstream of a more immediate one: what level of care your parent "
               "needs now."),
        "reviewed": "2026-10-24",
        "title": "Will Illinois Take My Parent's House After Medicaid Pays for Care?",
        "h1": "Will Illinois take my parent&rsquo;s house after Medicaid pays for care?",
        "desc": ("Illinois can file a claim against a Medicaid recipient's estate after "
                 "they die, but only against the estate &mdash; never against heirs "
                 "personally &mdash; and the first $25,000 of every estate is protected "
                 "by law. Here is what the state can and cannot reach."),
        "intent": "worry / paying for care",
        "answer": ("Not automatically, and never from your own pocket. Illinois HFS can "
                   "file a claim against a Medicaid recipient's <strong>estate</strong> "
                   "after death to recover what it paid for long-term care &mdash; "
                   "but it &ldquo;will never ask for more money than it paid for "
                   "services,&rdquo; it cannot touch the "
                   "<strong>first $25,000</strong> of any estate with a death on or "
                   "after 1 July 2022, and it does not pursue a claim at all while a "
                   "spouse, a child under 21, or a disabled child survives. Heirs are "
                   "never required to pay a claim from their own money."),
        "sources": srcs("hfs_estate_guide", "hfs_estate_faq", "hfs_estate_liens"),
        "body": [
            ("What estate recovery actually is", [
                "<p>Every state's Medicaid program is required to run an estate recovery "
                "program, and Illinois HFS describes why plainly: Medicaid is "
                "&ldquo;a State and Federally funded program,&rdquo; and after a "
                "recipient of long-term services and supports &mdash; care at home or in "
                "a long-term care facility &mdash; dies, the state asks their "
                "<strong>estate</strong> to repay what it spent. HFS's Bureau of "
                "Collections runs the program together with the Illinois Department of "
                "Human Services.</p>",
                "<p>One limit holds regardless of anything else: HFS states it "
                "&ldquo;will never ask for more money than it paid for services.&rdquo; "
                "A claim is always capped at what the state actually spent on that "
                "person's care &mdash; it is never a penalty, and it is never calculated "
                "any other way.</p>",
                "<p>The claim is against the <strong>estate</strong>, not against any "
                "living person. HFS is direct about this: family members &ldquo;are not "
                "required to pay from their own money.&rdquo; Nobody inherits a Medicaid "
                "bill.</p>",
            ]),
            ("The protections that apply automatically", [
                "<p>HFS lists several situations in which it will not seek recovery at "
                "all, without anyone having to ask:</p>",
                "<ul class=\"res__list\">"
                "<li>A <strong>surviving spouse</strong> is alive</li>"
                "<li>There is a <strong>child under 21</strong></li>"
                "<li>There is a <strong>child of any age</strong> who is blind or "
                "permanently and totally disabled under Social Security's rules</li>"
                "<li>The estate is worth <strong>$25,000 or less</strong></li>"
                "<li>Selling the property would <strong>cost more than it is "
                "worth</strong></li>"
                "<li>Recovery would cause the heirs <strong>undue hardship</strong></li>"
                "</ul>",
                "<p>On top of that list, a separate rule protects part of "
                "<em>every</em> estate, regardless of who survives. For deaths on or "
                "after <strong>1 July 2022</strong>, HFS will not collect against the "
                "first <strong>$25,000</strong> of estate value at all. HFS illustrates "
                "this with its own figures: a $40,000 estate exposes only the $15,000 "
                "above that threshold to a claim. If a claim is larger than the estate can "
                "cover, the unpaid balance simply stays open in case more assets turn up "
                "later &mdash; nobody is chased for the difference.</p>",
                "<p>Debts come out of the estate before a Medicaid claim does, too: HFS "
                "says funeral costs, legal costs and any mortgage on the home are paid "
                "first. And HFS does not offer instalments on what remains &mdash; "
                "its own FAQ states flatly, &ldquo;HFS does not allow payment "
                "plans.&rdquo;</p>",
            ]),
            ("What counts as the estate &mdash; and what does not", [
                "<p>HFS defines the estate as property &mdash; money, a house, other "
                "valuables &mdash; that a person leaves to heirs at death, which in "
                "practice means the <strong>probate</strong> estate. Anything that "
                "passes to a named beneficiary outside probate is outside the state's "
                "reach. HFS gives two examples directly: a life insurance policy that "
                "names who receives the payment, and a bank account that is payable on "
                "death to someone else. Its FAQ adds more of the same kind: IRAs, "
                "pension plans, jointly held accounts with survivorship rights, mutual "
                "funds and deferred compensation plans are generally outside the probate "
                "estate and outside a claim.</p>",
                "<p>Property anywhere counts, not just in Illinois &mdash; HFS says a "
                "claim can reach estate property regardless of location. And if the "
                "same person received Medicaid in more than one state, more than one "
                "state can file a claim; HFS says the probate court decides how the "
                "estate is divided between them.</p>",
            ]),
            ("Liens are a separate, narrower tool", [
                "<p>A <strong>lien</strong> is not the same thing as an estate claim. A "
                "lien attaches to real property &mdash; land and whatever is built on it "
                "&mdash; while someone is still alive, rather than after death. HFS "
                "describes two situations where one can be filed: cash assistance "
                "combined with medical assistance produces a lien equal to the cash "
                "assistance received, and medical-assistance-only recipients in a "
                "long-term care facility can face a lien, equal to all medical "
                "assistance paid before and during the stay, but only after "
                "<strong>120 consecutive days</strong> in the facility. No lien is filed "
                "if the home is occupied by a spouse, a child under 21, a disabled "
                "child of any age, or in some cases a sibling, and a lien is released if "
                "the resident is discharged home.</p>",
                "<p>This tool has also been narrowed by law. HFS states that "
                "<strong>Public Act 102-1037</strong>, effective <strong>2 June "
                "2022</strong>, restricts the filing of <em>new</em> liens on real "
                "property as a collection method. Liens already filed before that date "
                "are still pursued &mdash; the change is forward-looking, not "
                "retroactive.</p>",
            ]),
            ("Will the home actually have to be sold?", [
                "<p>HFS says the state does not take physical possession of a home. But "
                "it is equally direct that the property &ldquo;may have to be sold in "
                "order to satisfy the HFS' claim&rdquo; once a claim is filed and no "
                "exemption applies. Heirs who want to keep the property can instead pay "
                "the claim from other funds. And as above, if selling would cost more "
                "than the property is worth, HFS will not pursue a sale at all.</p>",
            ]),
            ("The hardship waiver, and a deadline this guide could not verify", [
                "<p>Heirs can ask HFS to waive a claim on grounds of undue hardship. Its "
                "guide gives examples of what that can look like: the property was a "
                "family business, farm or ranch that provided the heirs' main income for "
                "at least 12 months before death; paying the claim would mean the heirs "
                "need government financial help they do not currently need; or paying it "
                "would cause them to lose government help they currently receive. The "
                "application is available on the HFS site in six languages, and the "
                "heir must request the waiver and supply the proof HFS asks for.</p>",
                "<p><strong>This guide went looking for how long heirs have to request "
                "that waiver after being notified, and could not find a deadline stated "
                "on either HFS page it read.</strong> Secondary sources online quote a "
                "60-day window, but that figure was not read off a primary HFS page, so "
                "it does not appear here. If a hardship waiver matters to your family, "
                "ask HFS directly &mdash; the Department of Human Services Helpline is "
                "<strong>1-800-843-6154</strong> (TTY 1-866-324-5553), Monday to Friday "
                "&mdash; or ask an elder law attorney, rather than relying on a deadline "
                "repeated secondhand.</p>",
            ]),
            ("Where this fits with the rest of this site", [
                "<p>Estate recovery is a question about what happens <em>after</em> "
                "Medicaid has already been paying for care, not about whether it will. "
                "For how Illinois Medicaid qualifies someone for long-term care in the "
                "first place, including what &ldquo;spend-down&rdquo; means, see "
                '<a href="/guides/illinois-medicaid-long-term-care/">How Illinois '
                "Medicaid pays for long-term care, and what spend-down means</a>.</p>",
                "<p>If you are still working out which level of care your parent "
                'actually needs, the <a href="/">free six-question assessment</a> on '
                "this site walks through that question and shows its reasoning. It asks "
                "for no name, no email and no phone number, and your answers never leave "
                "your device.</p>",
            ]),
        ],
    },

    {
        "slug": "medicare-hospice-benefit-explained",
        "bridge": ("Hospice rules say what is covered once a doctor certifies six months "
               "or less to live. They say nothing about which kind of care your parent "
               "needs before that point is reached."),
        "reviewed": "2026-10-25",
        "title": "Does Medicare Pay for Hospice Care at Home?",
        "h1": "Does Medicare pay for hospice care at home?",
        "desc": ("Medicare pays " + F["hospice_zero"] + " for covered hospice care once a "
                 "doctor certifies six months or less to live and your parent chooses "
                 "comfort care over a cure. Here is exactly what that does and does not "
                 "include."),
        "intent": "coverage question",
        "answer": ("<strong>Yes, for the hospice benefit itself.</strong> Medicare pays "
                   "<strong>" + F["hospice_zero"] + "</strong> for covered hospice care "
                   "once a hospice doctor and your parent&rsquo;s own doctor (if they have "
                   "one) certify a life expectancy of six months or less, and your parent "
                   "chooses comfort care instead of treatment to cure the illness. You may "
                   "still pay <strong>up to " + F["hospice_rx_copay"] + "</strong> per "
                   "prescription for pain and symptom drugs, and <strong>" +
                   F["hospice_respite_coins"] + "</strong> coinsurance for a short inpatient "
                   "respite stay. What it does not pay is room and board if your parent "
                   "lives in a facility, or anything meant to cure the terminal illness."),
        "sources": srcs("mhospice", "mcosts"),
        "body": [
            ("What the hospice benefit actually pays for", [
                "<p>Medicare describes hospice as &ldquo;end-of-life care for people with "
                "illnesses that can&rsquo;t be cured,&rdquo; delivered under Part A. It is "
                "not a different, better version of regular treatment &mdash; it is a "
                "different goal. Once your parent elects hospice, the aim shifts from "
                "curing the terminal illness to managing pain and symptoms and being "
                "comfortable.</p>",
                "<p>For <strong>covered</strong> hospice care from a Medicare-approved "
                "hospice provider, Medicare pays <strong>" + F["hospice_zero"] +
                "</strong>. That is the headline figure, and it is real &mdash; but "
                "&ldquo;covered hospice care&rdquo; is a narrower category than most "
                "families assume, and the next two sections set out exactly where its "
                "edges are.</p>",
            ]),
            ("The four things that must all be true", [
                "<p>Medicare lists conditions for electing the hospice benefit, and all of "
                "them have to hold:</p>",
                "<ul class=\"res__list\">"
                "<li>Your parent has <strong>Medicare Part A</strong></li>"
                "<li>A <strong>hospice doctor and your parent&rsquo;s own doctor</strong> "
                "(if they have one) certify a life expectancy of <strong>six months or "
                "less</strong> if the illness runs its normal course</li>"
                "<li>Your parent <strong>accepts comfort care</strong> &mdash; palliative "
                "care for the terminal illness &mdash; instead of care intended to cure "
                "it</li>"
                "<li>Your parent <strong>signs a Hospice Election Statement</strong>, "
                "which must be completed before any hospice services begin</li></ul>",
                "<p>Six months is not a deadline on the care itself. If your parent is "
                "still alive after six months, hospice continues as long as a hospice "
                "doctor or nurse practitioner recertifies eligibility after a face-to-face "
                "visit. People do come off hospice &mdash; because they improve, or "
                "because they or their family decide to go back to curative treatment "
                "&mdash; and electing hospice does not forfeit that choice.</p>",
            ]),
            ("What stops being covered the moment hospice starts", [
                "<p>Electing hospice changes what Medicare will pay for related to the "
                "terminal illness. Medicare states plainly that once the hospice benefit "
                "starts, it will not cover any of the following for that illness unless "
                "the hospice team arranges it:</p>",
                "<ul class=\"res__list\">"
                "<li>Treatment intended to <strong>cure</strong> the terminal illness</li>"
                "<li>Prescription drugs meant to cure it, rather than to control pain or "
                "symptoms</li>"
                "<li>Care from a provider that was not arranged by the hospice team</li>"
                "<li><strong>Room and board</strong> &mdash; at home, in a nursing home, or "
                "in an inpatient hospice facility</li>"
                "<li>Hospital outpatient or inpatient care, or ambulance transport, unless "
                "the hospice team arranges it or it is unrelated to the terminal "
                "illness</li></ul>",
                "<p>That last condition cuts both ways. A health problem that has nothing "
                "to do with the terminal diagnosis is still covered under Medicare&rsquo;s "
                "ordinary rules, with its ordinary deductibles and coinsurance. Hospice "
                "replaces coverage for the terminal illness; it does not replace Medicare "
                "for everything else. Before any service outside what the hospice team has "
                "arranged, ask the hospice team first &mdash; Medicare is explicit that it "
                "will not pay for it otherwise.</p>",
            ]),
            ("What it costs", [
                "<p>Four cost lines, all from Medicare&rsquo;s own cost pages for the "
                "current year:</p>",
                "<ul class=\"res__list\">"
                "<li><strong>Covered hospice care itself:</strong> " + F["hospice_zero"] +
                "</li>"
                "<li><strong>Prescription drugs for pain and symptom control:</strong> a "
                "copayment of up to " + F["hospice_rx_copay"] + " per prescription</li>"
                "<li><strong>Inpatient respite care</strong> &mdash; a short stay that "
                "gives a family caregiver a break: <strong>" +
                F["hospice_respite_coins"] + "</strong> of the Medicare-approved amount"
                "</li>"
                "<li><strong>Room and board</strong> in a facility: not paid by the "
                "hospice benefit at all</li></ul>",
                "<p><strong>There is a ceiling on the respite copayment.</strong> "
                "Medicare states that for inpatient respite care, <q>your copayment "
                "can&rsquo;t be more than the inpatient deductible amount</q>. The Part A "
                "inpatient hospital deductible is <strong>" + F["partA_deductible"] +
                "</strong> for each benefit period, so that is the most 5% can add up to "
                "&mdash; not a figure most respite stays will come near, but a real limit "
                "rather than an open bill.</p>",
                "<p><strong>A figure this guide will not publish.</strong> Secondary sites "
                "describe the respite coinsurance as capped at a specific dollar amount "
                "<em>per day</em>. That is a different claim from the limit above, and the "
                "Medicare page this guide read states no daily figure, so none appears "
                "here. Ask the hospice provider what a respite stay will actually cost "
                "before agreeing to one.</p>",
            ]),
            ("Where care happens, and how long it can continue", [
                "<p>Hospice is a service, not a building. Medicare says it is usually "
                "provided at home or wherever your parent already lives &mdash; including "
                "an assisted living or nursing home &mdash; and that inpatient hospice "
                "facilities are available when certain conditions are met. The same idea "
                "applies here as with a skilled nursing stay: it is not the address that "
                "decides what is covered, it is whether the hospice benefit has been "
                "elected and the services were arranged by the hospice team.</p>",
                "<p>Benefit periods run in a fixed pattern: two 90-day periods, then an "
                "unlimited number of 60-day periods, with recertification required before "
                "each one past the first six months. Your parent can also change which "
                "hospice provider they use once per benefit period.</p>",
            ]),
            ("Where this fits with the rest of this site", [
                "<p>Hospice answers a different question from the one in "
                '<a href="/guides/does-medicare-pay-for-senior-care/">Does Medicare pay '
                "for assisted living or nursing home care?</a> That guide covers short-term "
                "<em>skilled</em> care aimed at recovery after a hospital stay. Hospice is "
                "for when the goal has shifted from recovery to comfort, and it can be "
                "elected in any of the settings "
                '<a href="/guides/levels-of-senior-care-explained/">that guide to the '
                "levels of care</a> describes.</p>",
                "<p>If the question in your family right now is not yet about hospice, but "
                'about which level of care your parent needs, the <a href="/">free '
                "six-question assessment</a> on this site walks through that question and "
                "shows its reasoning. It asks for no name, no email and no phone number, "
                "and your answers never leave your device.</p>",
            ]),
        ],
    },
    {
        "slug": "independent-living-evanston",
        "bridge": ("Independent living is the one option on this site that is not "
                   "care. That makes it the easiest to choose, and the easiest to "
                   "choose too late."),
        "reviewed": "2026-10-26",
        "title": "Independent Living in Evanston and the North Shore, Explained",
        "h1": "Independent living in Evanston and the North Shore, explained",
        "desc": ("Independent living is housing with services, not care. What is in "
                 "the monthly fee, how it differs from licensed assisted living, and "
                 "why no Illinois median figure appears on this page."),
        "intent": "lifestyle question",
        "answer": ("<strong>Independent living is housing with services, not "
                   "care.</strong> A private apartment, cottage or townhouse, with "
                   "some combination of meals, housekeeping, grounds and transport "
                   "folded into one monthly fee. Generally <strong>no hands-on help "
                   "with bathing or dressing, and generally no nursing staff on the "
                   "floor</strong>. Nobody has to need anything to move in, which is "
                   "the point: most people who do it are well, and they do it while "
                   "they still get to choose."),
        "sources": srcs("idph_al_div", "mcosts", "carescout"),
        "body": [
            ("What you are actually buying", [
                "<p>Three things, and it helps to price them separately.</p>"
                '<ul class="res__list">'
                "<li><strong>The home.</strong> An apartment, cottage or townhouse "
                "you live in on your own terms.</li>"
                "<li><strong>The work you stop doing.</strong> Cooking, cleaning, "
                "the roof, the gutters, the lawn, the snow, the driving. For most "
                "people this is the real purchase.</li>"
                "<li><strong>The people.</strong> A dining room, a calendar, and "
                "neighbours on the other side of the door. Easy to dismiss from a "
                "brochure, and the thing residents mention first.</li></ul>",
                "<p>What you are <em>not</em> buying is care. If someone needs help "
                "getting dressed, or medications handed to them, or a nurse within "
                "reach, independent living is the wrong setting, and a good "
                "community will say so rather than take the deposit.</p>"
            ]),
            ("How it differs from assisted living, in one line", [
                "<p>Assisted living is a <strong>licensed category in "
                "Illinois</strong>. Independent living is not.</p>",
                "<p>The Illinois Department of Public Health runs a Division of "
                "Assisted Living which, in its own words, &ldquo;is responsible for "
                "all state licensure and survey processes for Assisted Living and "
                "Shared Housing establishments&rdquo;, and has licensed them since "
                "regulations were adopted in December 2001. IDPH publishes the list "
                "of licensed establishments.</p>",
                "<p><strong>Independent living does not appear on that licence list, "
                "and this guide found no state care-licence category for it in "
                "Illinois.</strong> That is not a loophole and not a warning &mdash; "
                "it follows from no personal care being provided. It does mean the "
                "state inspection records that exist for assisted living and nursing "
                "facilities do not exist in the same form here, so the usual way of "
                "checking a care community does not apply. Ask any community exactly "
                "what it is licensed as, and for which parts of its campus.</p>"
            ]),
            ("What it costs, and the figure this guide will not give you", [
                "<p>The CareScout Cost of Care Survey is the source this site uses "
                "for Illinois senior-living costs. It reports a statewide median for "
                "assisted living of <strong>" + F["al_median"] + " a month</strong>. "
                "<strong>It reports no Illinois median for independent "
                "living.</strong></p>",
                "<p>So there is no honest statewide number to print, and this guide "
                "will not invent one. Anyone quoting a precise Illinois "
                "independent-living average is working from something other than "
                "that survey.</p>",
                "<p>What moves the price is the shape of the contract. Ask for a "
                "<strong>written fee schedule</strong> that separates four things:</p>"
                '<ul class="res__list">'
                "<li>Any entrance fee or deposit &mdash; and exactly what is "
                "refundable, to whom, and when.</li>"
                "<li>The monthly fee, and which services sit inside it.</li>"
                "<li>What is billed on top: a second meal, a guest room, parking, "
                "transport beyond a set radius.</li>"
                "<li>How the monthly fee moved in each of the last five years. Ask "
                "for the history, not the policy.</li></ul>",
                "<p><strong>Medicare pays none of this.</strong> Medicare is health "
                "insurance; independent living is housing. The same is true of "
                "assisted living, which is the misunderstanding most families "
                "arrive with.</p>"
            ]),
            ("Two ways to go from here", [
                "<p>Neither is required to finish reading, and nothing below "
                "asks for a name.</p>"
                '<div class="fork">'
                '<a class="fork__opt" href="/?from=il-guide#assessment">'
                '<span class="fork__h">Help me explore my options</span>'
                '<span class="fork__p">Six questions, about two minutes. It '
                'suggests which level of living fits and explains why. No '
                'name, no email, no phone number, and your answers never '
                'leave your device.</span></a>'
                '<a class="fork__opt" href="/?tour=independent#plan-visit">'
                '<span class="fork__h">I&rsquo;d like to explore a tour</span>'
                '<span class="fork__p">Skip the questions entirely. The '
                'request reaches the person who runs this guide, who reads '
                'every one himself. Nothing about care needs is assumed or '
                'recorded.</span></a>'
                '</div>',
                "<p>The second route records no assessment at all, and the "
                "notification says so in those words. Choosing it asserts "
                "nothing about anyone&rsquo;s health.</p>"
            ]),
            ("Who it tends to suit", [
                "<p>There is no eligibility test to pass. Communities set their own "
                "minimum age and financial requirements, and some run a health "
                "screen to confirm a person does not need more care than the "
                "community is licensed to give. Those are the community&rsquo;s "
                "rules, not the state&rsquo;s.</p>",
                "<p>In practice it suits someone managing fine who has started "
                "resenting the building they live in &mdash; the maintenance, the "
                "stairs, the winter. If the honest answer to &ldquo;why now&rdquo; "
                "is the house rather than the health, this is the category that "
                "answers it.</p>",
                "<p>It also suits planning ahead. Many Evanston and North Shore "
                "campuses have assisted living and skilled nursing on the same site, "
                "which makes one question matter more than any amenity: "
                "<strong>what happens if care needs change?</strong> Ask whether a "
                "resident can stay, what triggers a move, who decides, whether a "
                "place in the care building is held for residents or waitlisted, and "
                "what the fee becomes. Get the answer in writing.</p>"
            ]),
            ("Visiting, and what a brochure cannot tell you", [
                "<p>Go at a mealtime rather than a scheduled tour slot. The dining "
                "room answers more than the model apartment does.</p>"
                '<ul class="res__list">'
                "<li>Ask two residents whether they chose this or were moved here. "
                "The answers differ, and the difference is the culture.</li>"
                "<li>Check whether the activity calendar on the wall matches what is "
                "actually happening that afternoon.</li>"
                "<li>Notice whether anyone is eating alone, and whether anyone does "
                "anything about it.</li>"
                "<li>Ask what last year&rsquo;s turnover was, and where people "
                "went.</li></ul>",
                "<p>Visiting before you need to is the cheapest version of this "
                "decision. Nothing obliges anyone to move.</p>"
            ]),
            ("Where this fits with the rest of this site", [
                "<p>If the question is whether someone needs help rather than wants "
                "less house, start with "
                "<a href=\"/guides/levels-of-senior-care-explained/\">the levels of "
                "care explained</a>. If the question is cost, "
                "<a href=\"/guides/assisted-living-cost-illinois/\">what assisted "
                "living actually costs in Illinois</a> carries the figures this page "
                "deliberately does not. For a wartime veteran or a surviving spouse, "
                "<a href=\"/guides/va-aid-and-attendance-benefit/\">VA Aid and "
                "Attendance</a> is a cash benefit that can go toward any setting, "
                "including this one.</p>",
                "<p>This guide did not research entrance-fee refund law, Life Plan or "
                "continuing-care contract regulation in Illinois, or how an entrance "
                "fee interacts with Medicaid eligibility later. Those are real "
                "questions and they are not answered here &mdash; ask a lawyer who "
                "practises elder law in Illinois before signing anything carrying an "
                "entrance fee.</p>"
            ])
        ]
    },
    {
        "slug": "va-aid-and-attendance-benefit",
        "bridge": ("Qualifying for a VA pension tells you that your parent can get help "
               "paying for care. It does not tell you which level of care their health "
               "actually calls for."),
        "reviewed": "2026-10-26",
        "title": "Does the VA Pay for Senior Care? Aid and Attendance, Explained",
        "h1": "Does the VA pay for senior care? Aid and Attendance, explained",
        "desc": ("VA Aid and Attendance can add up to " + F["va_mapr_aa_single"] +
                 " a year on top of a wartime veteran&rsquo;s pension. Here is who "
                 "actually qualifies, why the published rate is a ceiling rather than a "
                 "cheque, and how a surviving spouse&rsquo;s own pension differs."),
        "intent": "benefits question",
        "answer": ("<strong>Yes, for veterans and some surviving spouses who already "
                   "qualify for a VA pension.</strong> Aid and Attendance and Housebound "
                   "are not stand-alone benefits &mdash; they are increased monthly rates "
                   "added to the <strong>Veterans Pension</strong>, or to a surviving "
                   "spouse&rsquo;s <strong>Survivors Pension</strong>, for someone who "
                   "needs help with daily activities, is bedridden, is a nursing home "
                   "patient because of a disability, or has severely limited eyesight. "
                   "The published figure is a <strong>maximum annual rate</strong>, not a "
                   "flat cheque: VA pays the difference between that ceiling and the "
                   "person&rsquo;s own countable income, so this guide will not calculate "
                   "what any one family would actually receive."),
        "sources": srcs("va_aa", "va_elig", "va_rates", "va_survivors",
                        "va_survivors_rates", "va_apply"),
        "body": [
            ("What Aid and Attendance and Housebound actually are", [
                "<p>Many Evanston families have a veteran parent and no idea this exists, "
                "because VA.gov describes Aid and Attendance and Housebound as something "
                "you can only get <q>if you get a VA pension</q> &mdash; they sit on top "
                "of a pension, rather than standing on their own. Mixing the two up with "
                "the base pension is the most common way a real benefit gets missed.</p>",
                "<p>VA pays the <strong>Aid and Attendance</strong> rate to someone who "
                "meets at least one of these, quoted directly from VA.gov:</p>",
                "<ul class=\"res__list\">"
                "<li>&ldquo;You need another person to help you perform daily activities, "
                "like bathing, feeding, and dressing&rdquo;</li>"
                "<li>&ldquo;You have to stay in bed&mdash;or spend a large portion of the "
                "day in bed&mdash;because of illness&rdquo;</li>"
                "<li>&ldquo;You&rsquo;re a patient in a nursing home due to the loss of "
                "mental or physical abilities related to a disability&rdquo;</li>"
                "<li>&ldquo;Your eyesight is limited (even with glasses or contact lenses "
                "you have only 5/200 or less in both eyes; or concentric contraction of "
                "the visual field to 5 degrees or less)&rdquo;</li></ul>",
                "<p>The <strong>Housebound</strong> rate is separate: it is for someone "
                "who, in VA.gov&rsquo;s words, will &ldquo;spend most of your time in "
                "your home because of a permanent disability (a disability that "
                "doesn&rsquo;t go away).&rdquo; VA.gov is explicit that a person cannot receive both "
                "at the same time &mdash; it is one increased rate or the other, never "
                "both stacked together.</p>",
            ]),
            ("Who qualifies for the pension underneath it", [
                "<p>Before either add-on can apply, the veteran has to qualify for the "
                "Veterans Pension itself. Two things must both be true. The first is "
                "the discharge, and the bar is lower than most families assume: VA.gov "
                "requires only that the veteran &ldquo;didn&rsquo;t receive a "
                "dishonorable discharge&rdquo; &mdash; <strong>not</strong> that the "
                "discharge was honourable. An other-than-honorable or bad-conduct "
                "discharge may still make a claim ineligible, and VA.gov describes two "
                "routes in that case: asking for a discharge upgrade, or requesting a "
                "Character of Discharge review. Do not rule a parent out because the "
                "paperwork does not say &ldquo;honorable.&rdquo; The second is income "
                "and net worth within limits Congress sets.</p>",
                "<p>The service record then has to clear <strong>one</strong> of three "
                "bars, and which one depends on when active duty began:</p>"
                "<ul class=\"res__list\">"
                "<li><strong>Started before 8 September 1980:</strong> at least 90 days "
                "of active duty, with at least one day during a wartime period.</li>"
                "<li><strong>Enlisted, started after 7 September 1980:</strong> at least "
                "24 months, or the full period ordered, with at least one wartime "
                "day.</li>"
                "<li><strong>An officer who started after 16 October 1981:</strong> had "
                "not previously served at least 24 months on active duty.</li></ul>",
                "<p>The wartime periods VA recognises include:</p>"
                "<ul class=\"res__list\">"
                "<li>World War II &mdash; 7 December 1941 to 31 December 1946</li>"
                "<li>Korean conflict &mdash; 27 June 1950 to 31 January 1955</li>"
                "<li>Vietnam era &mdash; 1 November 1955 to 7 May 1975 for service in the "
                "Republic of Vietnam; 5 August 1964 to 7 May 1975 for service "
                "elsewhere</li>"
                "<li>Gulf War &mdash; 2 August 1990 through a future date to be set by "
                "law or presidential proclamation</li></ul>",
                "<p>Separately, the veteran must meet at least one of: aged 65 or older; a "
                "permanent and total disability; a long-term nursing home patient because "
                "of a disability; or already receiving Social Security Disability Insurance "
                "or Supplemental Security Income.</p>",
            ]),
            ("The published rate is a ceiling, not a cheque", [
                "<p>VA.gov&rsquo;s rate tables (current as of the cost-of-living increase "
                "effective 1 December 2025) give the <strong>Maximum Annual Pension "
                "Rate</strong>, or MAPR &mdash; the most a veteran with no dependents can "
                "be paid, before their own income is subtracted:</p>",
                "<ul class=\"res__list\">"
                "<li><strong>Pension alone:</strong> " + F["va_mapr_basic_single"] +
                " a year with no dependents, " + F["va_mapr_basic_1dep"] +
                " with one</li>"
                "<li><strong>Housebound:</strong> " + F["va_mapr_hb_single"] +
                " a year with no dependents, " + F["va_mapr_hb_1dep"] +
                " with one</li>"
                "<li><strong>Aid and Attendance:</strong> " + F["va_mapr_aa_single"] +
                " a year with no dependents, " + F["va_mapr_aa_1dep"] +
                " with one</li></ul>",
                "<p>That is a ceiling, not an entitlement. VA.gov is explicit that pension "
                "pays the gap between the MAPR and the veteran&rsquo;s own countable annual "
                "income, which it defines as including wages, Social Security benefits, "
                "investment income and a dependent&rsquo;s income. Unreimbursed medical "
                "expenses can reduce that countable income, but only the portion above 5% "
                "of the MAPR counts as deductible &mdash; VA.gov&rsquo;s own words are that "
                "these expenses &ldquo;may reduce your income for VA purposes.&rdquo; This "
                "guide will not do that subtraction for a hypothetical family; the real "
                "figure depends on income and medical expenses only VA can verify.</p>",
                "<p>Worth sizing honestly before you plan around it. The highest Aid and "
                "Attendance rate for a veteran with no dependents, " +
                F["va_mapr_aa_single"] + " a year, works out to roughly " +
                F["va_mapr_aa_single_month"] + " a month &mdash; against a median "
                "Illinois assisted living cost of " + F["al_median"] + " a month, from "
                "<a href=\"/guides/assisted-living-cost-illinois/\">this site&rsquo;s "
                "cost guide</a>. At the ceiling it covers a useful share of the bill, "
                "not the bill. Aid and Attendance is a contribution toward care costs, "
                "and it is not a programme that pays for assisted living.</p>",
                "<p>Net worth is capped separately, at <strong>" + F["va_networth_limit"] +
                "</strong> for the period running 1 December 2025 through 30 November "
                "2026, and it includes a spouse&rsquo;s net worth too. A house, a car and "
                "most home furnishings are excluded.</p>",
                "<p>One figure worth knowing even though it is not the MAPR: a veteran "
                "with no dependents who is already a patient in a Medicaid-covered nursing "
                "facility has their pension reduced to <strong>" +
                F["va_nh_medicaid_rate"] + " a month</strong>. That is a real VA.gov figure, "
                "but it describes a different situation from the Aid and Attendance rate "
                "above &mdash; do not read the two as the same benefit.</p>",
            ]),
            ("Surviving spouses: the Survivors Pension and its own Aid and Attendance", [
                "<p>A surviving spouse who has not remarried, and who generally lived with "
                "the veteran from marriage until death (VA.gov allows exceptions for "
                "separations caused by health, work, or the veteran&rsquo;s misconduct), "
                "can claim a <strong>Survivors Pension</strong> if the veteran&rsquo;s "
                "service met the same wartime rules and income and net worth again fall "
                "within the limits Congress sets &mdash; the same " +
                F["va_networth_limit"] + " net worth limit applies.</p>",
                "<p>Its MAPR figures, for the same period, are lower than a veteran&rsquo;s "
                "own pension:</p>",
                "<ul class=\"res__list\">"
                "<li><strong>Basic Survivors Pension:</strong> " +
                F["va_survivor_basic_single"] + " a year with no dependents, " +
                F["va_survivor_basic_1dep"] + " with one child</li>"
                "<li><strong>Housebound:</strong> " + F["va_survivor_hb_single"] +
                " with no dependents, " + F["va_survivor_hb_1dep"] + " with one child</li>"
                "<li><strong>Aid and Attendance:</strong> " + F["va_survivor_aa_single"] +
                " with no dependents, " + F["va_survivor_aa_1dep"] + " with one child</li>"
                "</ul>",
                "<p>As with the veteran&rsquo;s own pension, these are ceilings reduced by "
                "the survivor&rsquo;s countable income, not flat payments.</p>",
            ]),
            ("How to apply", [
                "<p>VA.gov lists five ways to apply for the underlying pension:</p>"
                "<ul class=\"res__list\">"
                "<li>Apply online.</li>"
                "<li>Fill out VA Form 21P-527EZ and upload it through the QuickSubmit "
                "tool.</li>"
                "<li>Fill out VA Form 21P-527EZ and post it to: Department of Veterans "
                "Affairs, Pension Intake Center, PO Box 5365, Janesville, WI "
                "53547-5365.</li>"
                "<li>Bring the completed form to a VA regional office in person.</li>"
                "<li>Get help from an accredited attorney, claims agent, or Veterans "
                "Service Organization representative.</li></ul>",
                "<p>Aid and Attendance or Housebound specifically also needs VA Form "
                "21-2680, &ldquo;Examination for Housebound Status or Permanent Need for "
                "Regular Aid and Attendance,&rdquo; completed in part by a medical "
                "examiner. A veteran who already lives in a nursing home must also submit "
                "VA Form 21-0779, Request for Nursing Home Information in Connection with "
                "Claim for Aid and Attendance.</p>",
                "<p>Applying online while signed in with an identity-verified account sets "
                "the claim&rsquo;s effective date automatically. Applying by mailed form "
                "or an unverified account does not get that automatic date, so VA.gov "
                "suggests filing an intent to file first to protect it. Either way, be "
                "ready with a Social Security number, military and marital history, "
                "household income and asset figures, and unreimbursed medical "
                "expenses.</p>",
            ]),
            ("Where this fits with the rest of this site", [
                "<p>A VA pension answers a different question from "
                '<a href="/guides/does-medicare-pay-for-senior-care/">Does Medicare pay '
                "for assisted living or nursing home care?</a> Medicare is federal health "
                "insurance and never pays for custodial assisted living; a VA pension is a "
                "needs-based cash benefit that a family can put toward any level of care, "
                "including assisted living. The two can apply to the same parent at the "
                "same time.</p>",
                "<p>This guide has not verified how a VA pension interacts with eligibility "
                "for <a href=\"/guides/illinois-medicaid-long-term-care/\">Illinois "
                "Medicaid&rsquo;s long-term care programme</a> &mdash; that depends on "
                "income counting rules this guide did not read, so it will not guess at "
                "the answer. Ask Illinois HFS directly if your parent may need both.</p>",
                "<p>If the open question in your family is which level of care your "
                'parent actually needs, rather than how to pay for it, the <a href="/">'
                "free six-question assessment</a> on this site walks through that "
                "separately. It asks for no name, no email and no phone number, and your "
                "answers never leave your device.</p>",
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
      are passed to Westminster Place because that is what you asked for;
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
        js(g["title"]), js(strip_tags(g["desc"])), js(canon), reviewed_iso(g))


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
            'how fresh this page is.</p>\n</section>' % (items, reviewed_human(g)))


BRIDGE_MISSING = """
build-guides.py: the guide "%s" has no "bridge".

Every guide needs ONE short, topic-specific invitation to the assessment,
placed after the first section - the moment the reader has their answer and
is most likely to leave. It is not a sales pitch and not a second button: it
is one sentence naming the question THIS article cannot answer, then a link.

Add a "bridge" key to the guide dict, for example:

    "bridge": ("Knowing what Medicare covers is a different question from "
               "knowing what kind of care your parent actually needs."),

Write it fresh for the topic. Never reuse another guide's wording. No
urgency, no scarcity, no "act now", no promise about what the result will
say. Name the gap the article leaves, then step back.
"""


def bridge_block(g):
    """The mid-article invitation.

    Required on every guide. A missing one stops the build rather than
    silently shipping a page whose only route to the assessment is a CTA at
    the bottom that most readers never scroll to - measured 2026-10-24: the
    first assessment mention sat in section 6 of 7, 7 of 8 and 8 of 9 across
    the library, so a reader whose question was answered in section 2 left
    without ever seeing it.

    The invitation is a link, not a button. The page already ends with one
    button; a second would read as a sales page rather than a guide."""
    text = g.get("bridge")
    if not text or len(strip_tags(text).strip()) < 40:
        raise SystemExit(BRIDGE_MISSING % g["slug"])
    return ('<aside class="bridge">\n'
            '<p class="bridge__p">%s</p>\n'
            '<p class="bridge__go"><a href="/#assessment">Try the free '
            'six-question assessment</a> &mdash; about two minutes, no name, '
            'no email and no phone number, and your answers never leave your '
            'device. It is educational guidance, not a diagnosis.</p>\n'
            '</aside>' % text)


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
    for i, (heading, paras) in enumerate(g["body"]):
        dia = DIAGRAMS.get((g["slug"], strip_tags(heading)))
        body = "\n".join(paras) + (("\n" + dia) if dia else "")
        parts.append('<section class="res__block">\n<h2 class="res__h">%s</h2>\n%s\n</section>\n'
                     % (heading, body))
        # The bridge sits after the FIRST section — the moment the reader
        # has their answer and is most likely to leave. One quiet link,
        # never a second button.
        if i == 0:
            parts.append(bridge_block(g) + "\n")
    parts.append(sources_block(g) + "\n")
    parts.append(related(g) + "\n")
    parts.append('<section class="res__block plan plan--primary">\n'
                 '<h2 class="res__h plan__h">Not sure which level of care applies?</h2>\n'
                 '<p class="plan__lead">Six questions, about two minutes. It asks for no '
                 'name, no email and no phone number, and your answers never leave your '
                 'device.</p>\n'
                 '<p><a class="btn btn--primary" href="/#assessment">Take the free '
                 'assessment</a></p>\n</section>\n')
    parts.append('<p class="visit__fine">Last reviewed %s.</p>\n' % reviewed_human(g))
    parts.append(FOOT)
    return "".join(parts)


from diagrams import DIAGRAMS


# --------------------------------------------------------------------------
# CATEGORIES — the filter chips on /guides/ are built from this list, in this
# order, showing only the ones that actually have guides.
#
# It is a CLOSED list on purpose. Chips derived from whatever strings happen
# to be in CARDS would sprawl into twenty near-duplicates ("Costs", "Cost",
# "Paying") the moment a routine invents one, and a filter bar nobody can
# scan is worse than no filter bar. A closed list keeps the bar short at 100
# guides; the build refuses an unknown category and prints the valid ones, so
# the routine cannot silently invent a twentieth.
#
# Adding a genuinely new category is a deliberate edit here, not an accident
# in a guide dict.
# --------------------------------------------------------------------------
CATEGORIES = [
    "Getting oriented",
    "Costs",
    "Medicare",
    "Paying with Medicaid",
    "Staying at home",
    "Checking a community",
    "Veterans' benefits",
    "Legal and planning",
]

CATEGORY_UNKNOWN = """
build-guides.py: guide "%s" uses the category "%s", which is not in CATEGORIES.

The /guides/ filter bar is built from a closed list so it stays scannable at
100 guides. Pick the closest existing category:

%s

If the guide genuinely belongs to none of them, add ONE new category to
CATEGORIES in build-guides.py and say so in the commit message. Do not invent
a near-duplicate of a category that already exists.
"""


def check_categories():
    for g in GUIDES:
        cat = CARDS[g["slug"]][0]
        if cat not in CATEGORIES:
            listing = "\n".join("  - " + c for c in CATEGORIES)
            raise SystemExit(CATEGORY_UNKNOWN % (g["slug"], cat, listing))


def used_categories():
    """Categories that actually have guides, in CATEGORIES order. An empty
    chip is a dead end, so a category with nothing in it never renders."""
    present = {CARDS[g["slug"]][0] for g in GUIDES}
    return [c for c in CATEGORIES if c in present]


def category_count(cat):
    return sum(1 for g in GUIDES if CARDS[g["slug"]][0] == cat)


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
    "illinois-care-facility-complaint": (
        "Checking a community",
        "How to report a problem at an Illinois care facility",
        "The resident advocate who works the problem with you, and the "
        "state regulator who investigates it — and which to call first."),
    "illinois-medicaid-estate-recovery": (
        "Paying with Medicaid",
        "Will Illinois take my parent’s house after Medicaid pays?",
        "What the state can and cannot reach after a Medicaid recipient "
        "dies, the automatic protections, and the $25,000 every estate "
        "keeps."),
    "independent-living-evanston": (
        "Getting oriented",
        "Independent living in Evanston and the North Shore",
        "Housing with services, not care \u2014 what sits in the monthly fee, "
        "how it differs from licensed assisted living, and why no Illinois "
        "median appears here."),
    "medicare-hospice-benefit-explained": (
        "Medicare",
        "Does Medicare pay for hospice care at home?",
        "What the hospice benefit actually covers, the four conditions "
        "that must all be met, and the one figure this guide would not "
        "guess at."),
    "va-aid-and-attendance-benefit": (
        "Veterans' benefits",
        "Does the VA pay for senior care? Aid and Attendance, explained",
        "Who actually qualifies for a VA pension and its Aid and "
        "Attendance or Housebound add-on, and why the published rate is "
        "a ceiling, not a cheque."),
}


def esc_attr(s):
    return (s.replace("&", "&amp;").replace('"', "&quot;")
             .replace("<", "&lt;").replace(">", "&gt;"))


def library_toolbar():
    """Search box and category chips for /guides/.

    PROGRESSIVE ENHANCEMENT, deliberately. The toolbar ships with `hidden`
    on it and guides.js removes that attribute on load. Without JavaScript a
    visitor — or a crawler — gets the complete, unfiltered list of every
    guide in plain HTML, with no controls that would do nothing if clicked.
    With JavaScript they get search, filters and Show more.

    That ordering is the whole SEO argument: the cards are server-rendered
    and always in the document. Nothing here hides an article from Google,
    and no guide URL changes."""
    chips = "".join(
        '<button type="button" class="chip" data-cat="%s">%s '
        '<span class="chip__n">%d</span></button>\n'
        % (esc_attr(c), c, category_count(c)) for c in used_categories())
    return (
        '<div class="lib" id="libTools" hidden>\n'
        '  <div class="lib__search">\n'
        '    <label class="lib__label" for="libQ">Search the guides</label>\n'
        '    <input type="search" id="libQ" class="lib__input" autocomplete="off"\n'
        '           placeholder="hospice, Medicaid, costs…"\n'
        '           aria-describedby="libCount">\n'
        '  </div>\n'
        '  <div class="lib__chips" role="group" aria-label="Filter by topic">\n'
        '    <button type="button" class="chip chip--on" data-cat="">'
        'All <span class="chip__n">%d</span></button>\n'
        '%s'
        '  </div>\n'
        '  <p class="lib__count" id="libCount" role="status" aria-live="polite"></p>\n'
        '</div>\n' % (len(GUIDES), chips))


def library_assessment():
    """The assessment panel on the library page.

    Placed AFTER the guides, not above them. Someone who lands on a library
    page is looking for a specific answer; putting the call to action first
    makes a reference page read as a landing page. It uses the same block as
    every guide, so it reads as part of the site rather than an insert."""
    return ('<section class="res__block plan plan--primary">\n'
            '<h2 class="res__h plan__h">Not sure which guide applies?</h2>\n'
            '<p class="plan__lead">Six questions, about two minutes, and the '
            'result points you at the level of care your answers describe — '
            'along with the reasoning. It asks for no name, no email and no '
            'phone number, and your answers never leave your device.</p>\n'
            '<p><a class="btn btn--primary" href="/#assessment">Take the free '
            'assessment</a></p>\n</section>\n')


def topic_card(g):
    """One card. The anchor sits on the title and its ::after is stretched
    over the whole surface, so the card is clickable with ONE tab stop and
    one accessible name - no duplicate links for a crawler or a screen
    reader to wade through, and the crawlable href never moves."""
    cat, title, blurb = CARDS[g["slug"]]
    # data-terms is what the search box matches against: the card title, the
    # category, the blurb, the article's own h1, its search intent and the
    # words in its slug. Built here from fields that already exist, so a new
    # guide becomes findable the moment the routine writes it — nobody ever
    # maintains a keyword list.
    raw = " ".join(strip_tags(x) for x in
                   (title, cat, blurb, g["h1"], g.get("intent", ""),
                    g["slug"].replace("-", " ")))
    terms = re.sub(r"[^a-z0-9 ]+", " ", raw.lower())
    terms = " ".join(sorted(set(w for w in terms.split() if len(w) > 2)))
    return ('<li class="topic" data-cat="%s" data-terms="%s">\n'
            '  <p class="topic__cat">%s</p>\n'
            '  <h2 class="topic__h"><a href="/guides/%s/">%s</a></h2>\n'
            '  <p class="topic__p">%s</p>\n'
            '  <p class="topic__go">Read article '
            '<span class="topic__arrow" aria-hidden="true">&rarr;</span></p>\n'
            '</li>\n' % (esc_attr(cat), esc_attr(terms), cat, g["slug"],
                         title, blurb))


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
            + library_toolbar()
            + cards
            + '<p class="lib__more-wrap"><button type="button" '
              'class="btn btn--quiet" id="libMore" hidden></button></p>\n'
            + library_assessment()
            + '<p class="visit__fine">Last reviewed %s.</p>\n' % reviewed_human({"reviewed": newest_reviewed()})
            + FOOT.replace("</body>", '<script src="/guides.js"></script>\n</body>'))


def build_sitemap():
    """Generated from the GUIDES list — adding a guide updates the sitemap."""
    # lastmod is PER URL. Stamping every page with today's date because one
    # guide changed tells a crawler that six unchanged pages were rewritten -
    # untrue, and the fastest way to teach it to ignore the field entirely.
    # A guide's lastmod is its own review date.
    newest = newest_reviewed()
    urls = [(SITE + "/", "1.0", "monthly", newest),
            (SITE + "/guides/", "0.8", "monthly", newest)]
    urls += [(SITE + "/guides/%s/" % g["slug"], "0.7", "yearly", reviewed_iso(g))
             for g in GUIDES]
    urls.append((SITE + "/privacy.html", "0.3", "yearly", newest))
    body = "".join(
        "  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n"
        "    <changefreq>%s</changefreq>\n    <priority>%s</priority>\n  </url>\n"
        % (loc, mod, freq, pri) for loc, pri, freq, mod in urls)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<!-- Generated by build-guides.py. Do not hand-edit: adding a guide to\n'
            '     the GUIDES list regenerates this file. -->\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + body + '</urlset>\n')


# --------------------------------------------------------------------------
# INDEXNOW
# --------------------------------------------------------------------------
# The key file is PUBLIC BY DESIGN. IndexNow verifies ownership by fetching
# https://<host>/<key>.txt and checking it contains the key, so the value
# below is meant to be world-readable and belongs in the repository.
#
# It is NOT the Bing Webmaster Tools API key. Those are different
# credentials with different rules: the Bing API key authenticates an
# account and must stay secret, this one identifies a site and must be
# served openly. Never store the Bing key here.
#
# Generated by the build so a rebuild can never drop it. check-guides.js
# fails if the file is missing or its contents drift from the constant.
INDEXNOW_KEY = "f7fdf3f8b3d44e90910b129126f4ac3d"
INDEXNOW_KEY_FILE = INDEXNOW_KEY + ".txt"


def write_indexnow_key():
    """Write the key file into the publish directory.

    `_dist` is what Netlify serves, so the file has to be here rather than
    at the repo root - a key file that only exists in the working tree
    verifies nothing."""
    p = os.path.join("_dist", INDEXNOW_KEY_FILE)
    before = io.open(p, encoding="utf-8").read() if os.path.isfile(p) else None
    if before != INDEXNOW_KEY:
        io.open(p, "w", encoding="utf-8", newline="").write(INDEXNOW_KEY)
        return True
    return False


# index.html added 2026-10-26. The homepage existed as TWO hand-maintained
# copies, root and _dist, with nothing keeping them in step: editing the
# root one and rebuilding left the published homepage untouched, silently.
# Exactly the drift that already bit styles.css. The generator syncs it now
# and check-guides fails the build if the two ever disagree.
SHARED_ASSETS = ["styles.css", "app.js", "assessment.js", "nav.js",
                 "guides.js", "index.html"]


BEACON_LEVELS = ["independent", "assisted", "memory", "skilled", "rehab",
                 "no_need"]


def write_beacons():
    """Every /t/*.txt the page can request, emitted from app.js itself.

    These were hand-made files, and three were simply never created:
    audience-self, audience-parent and result-independent-by-choice shipped
    firing at nothing. A beacon that 404s is not a quiet failure -- Netlify
    counts it in the not-found bucket rather than the path report, so that
    funnel step reads as zero forever.

    Parsed from the literals in app.js plus the two prefixes it builds at
    runtime, so adding a beacon in code creates its file on the next build
    and nobody has to remember."""
    src = io.open("app.js", encoding="utf-8").read()
    names = set(re.findall(r'"/t/([a-z0-9-]+)\.txt"', src))
    for lvl in BEACON_LEVELS:
        names.add("result-" + lvl)
    names.add("result-independent-by-choice")
    names.add("audience-self")
    names.add("audience-parent")
    # OUT is "_dist/guides", NOT the publish root -- using it here put the
    # beacons in _dist/guides/t/ where nothing ever requests them. They live
    # at the site root, and BOTH copies are hand-maintained: t/ in the
    # working tree and _dist/t/ in the publish directory. Write both, or the
    # next build drifts them apart the way index.html already did once.
    made = []
    for root in ("t", os.path.join("_dist", "t")):
        if not os.path.isdir(root):
            os.makedirs(root)
        for n in sorted(names):
            f = os.path.join(root, n + ".txt")
            if not os.path.isfile(f):
                io.open(f, "w", encoding="utf-8", newline="").write(n + "\n")
                made.append(os.path.join(root, n + ".txt"))
    return made


def sync_assets():
    """Copy the hand-edited root assets into _dist.

    Why this exists: styles.css, app.js, assessment.js and nav.js each
    existed TWICE - once at the repo root and once in _dist - with nothing
    keeping them in step. Netlify publishes _dist, so a change to the root
    copy reached nobody. Found 2026-10-24 when styles.css drifted 43 lines
    out of sync the moment a stylesheet rule was added.

    A daily routine cannot be expected to remember to copy a file. The
    build does it, and check-guides.js fails if the two ever differ."""
    import shutil
    copied = []
    for name in SHARED_ASSETS:
        if not os.path.isfile(name):
            continue
        dest = os.path.join("_dist", name)
        a = io.open(name, encoding="utf-8").read()
        b = io.open(dest, encoding="utf-8").read() if os.path.isfile(dest) else None
        if a != b:
            shutil.copyfile(name, dest)
            copied.append(name)
    return copied


def main():
    check_categories()
    os.makedirs(OUT, exist_ok=True)
    for name in sync_assets():
        print("  synced to _dist: %s" % name)
    for b in write_beacons():
        print("  beacon file created: %s" % b)
    if write_indexnow_key():
        print("  wrote IndexNow key file: %s" % INDEXNOW_KEY_FILE)
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
