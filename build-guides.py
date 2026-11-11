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
    "partB_deductible": "$283",
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
    "va_vdc": ('VA.gov — Veteran Directed Care',
              'https://www.va.gov/geriatrics/pages/veteran-directed_care.asp'),
    "va_cc_elig": ('VA.gov — Eligibility for community care outside VA',
                  'https://www.va.gov/resources/eligibility-for-community-care-outside-va/'),
    "va_health_apply": ('VA.gov — How to apply for VA health care benefits',
                        'https://www.va.gov/health-care/how-to-apply/'),
    "va_90": ('VA.gov — $90 VA pension rate in a Medicaid-covered nursing facility',
              'https://www.va.gov/resources/90-va-pension-rate-if-youre-in-a-medicaid-covered-nursing-facility/'),
    "va_ltc_new": ('VA.gov — Long-term care',
                   'https://www.va.gov/health-care/about-va-health-benefits/long-term-care/'),
    "va_clc": ('VA.gov — VA Community Living Centers',
              'https://www.va.gov/geriatrics/pages/VA_Community_Living_Centers.asp'),
    "va_respite": ('VA.gov — Respite Care',
                  'https://www.va.gov/geriatrics/pages/Respite_Care.asp'),
    "va_ltc_overview": ('VA.gov — VA Long Term Care Services',
                        'https://www.va.gov/geriatrics/pages/VA_Long_Term_Care_Services.asp'),
    "idph_vet_homes": ("Illinois Department of Public Health — Veterans' Homes",
                       'https://dph.illinois.gov/topics-services/health-care-regulation/nursing-homes/veterans-homes.html'),
    "idoa_caregiver": ('Illinois Department on Aging — Family Caregiver Support Program',
                       'https://ilaging.illinois.gov/programs/caregiver/program.html'),
    "idoa_crc": ('Illinois Department on Aging — Family and Caregiver Resource Centers',
                'https://ilaging.illinois.gov/programs/caregiver/crc.html'),
    "idoa_caregiver_links": ('Illinois Department on Aging — Family and Caregiver Services',
                             'https://ilaging.illinois.gov/programs/caregiver/caregiver-links.html'),
    "idoa_ship": ('Illinois Department on Aging — Senior Health Insurance Program (SHIP)',
                 'https://ilaging.illinois.gov/ship.html'),
    "idoa_ship_about": ('Illinois Department on Aging — About SHIP',
                        'https://ilaging.illinois.gov/ship/aboutship.html'),
    "mtools": ('Medicare.gov — Helpful tools',
              'https://www.medicare.gov/basics/get-started-with-medicare/using-medicare/helpful-tools'),
    "mmsp": ('Medicare.gov — Medicare Savings Programs',
             'https://www.medicare.gov/medicare-savings-programs'),
    "ilaging_msp_chart": ('Illinois Department on Aging — 2026 Medicare Savings Programs chart (QMB, SLMB, QI-1)',
                         'https://ilaging.illinois.gov/content/dam/soi/en/web/aging/ship/documents/medicare-savings-program-chart.pdf'),
    "hfs_qmb": ('Illinois HFS — Qualified Medicare Beneficiary (QMB) Program brochure (HFS 3352)',
               'https://hfs.illinois.gov/info/brochures-and-forms/brochures/hfs3352.html'),
    "idph_adv_directives": ('Illinois Department of Public Health — Advance Directives',
                            'https://dph.illinois.gov/topics-services/health-care-regulation/nursing-homes/advance-directives.html'),
    "ilaging_adv_directives": ('Illinois Department on Aging — Advance Directives',
                               'https://ilaging.illinois.gov/aboutus/legal-adv-directives.html'),
    "ilaging_legal_assistance": ('Illinois Department on Aging — Legal Assistance',
                                 'https://ilaging.illinois.gov/programs/legalassistance.html'),
    "idoa_benefit_access": ('Illinois Department on Aging — Benefit Access Program',
                            'https://ilaging.illinois.gov/benefitsaccess.html'),
    "idoa_benefit_access_faq": ('Illinois Department on Aging — Benefit Access, Eligibility and Frequently Asked Questions',
                                'https://ilaging.illinois.gov/benefitsaccess/eligibility-20and-20frequently-asked-questions.html'),
    "idoa_benefit_access_ridefree": ('Illinois Department on Aging — Benefit Access, Ride Free Transit Benefit',
                                     'https://ilaging.illinois.gov/benefitsaccess/ride-free-transit-benefit.html'),
    "idoa_nutrition": ('Illinois Department on Aging — Senior Nutrition Program',
                       'https://ilaging.illinois.gov/programs/nutrition.html'),
    "idoa_aaa": ('Illinois Department on Aging — Area Agencies on Aging',
                'https://ilaging.illinois.gov/forprofessionals/areaagenciesonaging.html'),
    "idoa_aps_program": ('Illinois Department on Aging — Adult Protective Services (APS)',
                        'https://ilaging.illinois.gov/programs/adult-protective-services-aps-.html'),
    "idoa_aps_definitions": ('Illinois Department on Aging — APS Definitions',
                            'https://ilaging.illinois.gov/protectionadvocacy/aps-definitions.html'),
    "idoa_aps_abuse": ('Illinois Department on Aging — Abuse, Neglect and Exploitation',
                       'https://ilaging.illinois.gov/protectionadvocacy/abuse.html'),
    "idoa_engage": ('Illinois Department on Aging — Engage2Change (what happens after a report)',
                    'https://ilaging.illinois.gov/engage.html'),
    "idoa_resident_rights_brochure": ('Illinois Department on Aging — "Residents’ Rights '
                                      'for People in Long-Term Care Facilities" (brochure, printed 9/25)',
                                      'https://ilaging.illinois.gov/content/dam/soi/en/web/aging/resources/'
                                      'newsandpublications/publications/documents/ltc-resrights.pdf'),
    "mhha": ('Medicare.gov — Home health services',
             'https://www.medicare.gov/coverage/home-health-services'),
    "va_pcafc": ('VA.gov — Program of Comprehensive Assistance for Family Caregivers',
                'https://www.va.gov/family-and-caregiver-benefits/health-and-disability/comprehensive-assistance-for-family-caregivers/'),
    "va_pgcss": ('VA.gov — The Program of General Caregiver Support Services',
                'https://www.va.gov/the-program-of-general-caregiver-support-services/'),
    "va_caregiver_compare": ('VA.gov — How are the 2 VA caregiver support programs different?',
                'https://www.va.gov/resources/how-are-the-2-va-caregiver-support-programs-different/'),
    "va_caregiver_benefits": ('VA.gov — Family and caregiver benefits',
                'https://www.va.gov/family-and-caregiver-benefits/'),
    "hfs_pace": ('Illinois HFS — Program of All-Inclusive Care for the Elderly (PACE)',
                'https://hfs.illinois.gov/medicalproviders/pace.html'),
    "hfs_pace_zip": ('Illinois HFS — PACE zip code search',
                'https://hfs.illinois.gov/medicalproviders/pace/zipsearch.html'),
    "hfs_pace_orgs": ('Illinois HFS — Designated PACE Organizations',
                'https://hfs.illinois.gov/medicalproviders/pace/designatedpaceorganizations.html'),
    "mpace": ('Medicare.gov — PACE (Program of All-Inclusive Care for the Elderly)',
             'https://www.medicare.gov/health-drug-plans/health-plans/your-coverage-options/other-medicare-health-plans/PACE'),
    "idoa_inhome": ('Illinois Department on Aging — In-Home Care for Seniors',
                    'https://ilaging.illinois.gov/programs/caregiver/in-home-care.html'),
    "dph_hcwr": ('Illinois Department of Public Health — Health Care Worker Registry',
                'https://dph.illinois.gov/topics-services/health-care-regulation/health-care-worker-registry.html'),
    "dph_home_services_faq": ('Illinois Department of Public Health — Home Services Agency licensing FAQ',
                              'https://dph.illinois.gov/topics-services/health-care-regulation/health-care-facilities/home-services/faq.html'),
    "idoa_money_mgmt": ('Illinois Department on Aging — Money Management (Volunteer Money Management Program)',
                        'https://ilaging.illinois.gov/programs/money-mgmt.html'),
    "idoa_money_mgmt_sites": ('Illinois Department on Aging — Volunteer Money Management Program Site/Agency List (FY27, 22 October 2026)',
                              'https://ilaging.illinois.gov/content/dam/soi/en/web/aging/programs/documents/ivmmp-programsitelist.pdf'),
    "idoa_hco": ('Illinois Department on Aging — The Home Care Ombudsman Program',
                'https://ilaging.illinois.gov/programs/ltcombudsman/the-home-care-ombudsman-program.html'),
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
                "<p>Neither is required to finish reading. One asks for "
                "nothing at all; the other asks how to reach you.</p>"
                '<div class="fork">'
                '<a class="fork__opt" href="/?from=il-guide#assessment">'
                '<span class="fork__h">Help me explore my options</span>'
                '<span class="fork__p">Six questions, about two minutes. It '
                'suggests which level of living fits and explains why. No '
                'name, no email, no phone number, and your answers never '
                'leave your device.</span></a>'
                '<a class="fork__opt" href="/?tour=independent#plan-visit">'
                '<span class="fork__h">I&rsquo;d like to explore a tour</span>'
                '<span class="fork__p">Skip the questions entirely. This one '
                'asks for your name and one way to reach you, and sends '
                'nothing until you tick the box. It reaches the person who '
                'runs this guide, who reads every one himself.</span></a>'
                '</div>',
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
        "reviewed": "2026-10-29",
        "title": "Does the VA Pay for Senior Care? Aid and Attendance, Explained",
        "h1": "Does the VA pay for senior care? Aid and Attendance, explained",
        "desc": ("The most a wartime veteran with no dependents can receive with Aid "
                 "and Attendance is " + F["va_mapr_aa_single"] + " a year &mdash; the "
                 "whole pension at that rate, not an extra payment, and a ceiling reduced "
                 "by the veteran&rsquo;s own income. Here is who actually qualifies, and "
                 "how a surviving spouse&rsquo;s own pension differs."),
        "intent": "benefits question",
        "answer": ("<strong>Yes, for veterans and some surviving spouses who already "
                   "qualify for a VA pension.</strong> Aid and Attendance and Housebound "
                   "are not stand-alone benefits &mdash; they are increased monthly rates "
                   "added to the <strong>Veterans Pension</strong>, or to a surviving "
                   "spouse&rsquo;s <strong>Survivors Pension</strong>, for someone who "
                   "needs help with daily activities, is bedridden, is a nursing home "
                   "patient because of a disability, or has severely limited eyesight. "
                   "The published figure is a <strong>maximum annual rate for the whole "
                   "pension at that level</strong> &mdash; not an amount paid on top of "
                   "the pension, and not a flat cheque: VA pays the difference between "
                   "that ceiling and the person&rsquo;s own countable income, so this "
                   "guide will not calculate what any one family would actually "
                   "receive."),
        "sources": srcs("va_aa", "va_elig", "va_rates", "va_survivors",
                        "va_survivors_rates", "va_apply", "va_90"),
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
                "<p>Worth sizing honestly before you plan around it. The Aid and "
                "Attendance ceiling for a veteran with no dependents &mdash; " +
                F["va_mapr_aa_single"] + " a year, the whole pension at that level "
                "rather than a sum added to it &mdash; works out to roughly " +
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
                F["va_nh_medicaid_rate"] + " a month</strong>. VA.gov states that rate on "
                "its own page for that situation (&ldquo;if you&rsquo;re living in a "
                "Medicaid-covered nursing facility and you have no dependents&rdquo;), and "
                "it describes a different situation from the Aid and Attendance rate "
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

    {
        "slug": "va-veteran-directed-care-program",
        "bridge": ("Knowing that the VA will fund help at home answers how your "
               "veteran parent might pay for it. It does not answer whether help "
               "at home, rather than a higher level of care, is actually enough."),
        "reviewed": "2026-10-27",
        "title": "Can a Veteran Get Paid In-Home Care Through the VA?",
        "h1": "Can a veteran get paid in-home care through the VA?",
        "desc": ("VA.gov describes a consumer-directed benefit called Veteran "
                 "Directed Care that lets an eligible veteran set a spending plan "
                 "and hire their own help at home, including a family member. "
                 "Here is who qualifies and how to start, in VA.gov&rsquo;s own "
                 "words."),
        "intent": "benefits question",
        "answer": ("<strong>Sometimes, through a programme called Veteran "
                   "Directed Care, which is separate from the VA pension this "
                   "site covers elsewhere.</strong> VA.gov describes it as giving "
                   "&ldquo;Veterans of all ages the opportunity to receive the "
                   "Home and Community Based Services they need in a "
                   "consumer-directed way.&rdquo; A veteran who qualifies gets a "
                   "budget and help building a spending plan, then hires their "
                   "own workers &mdash; who can include a family member or a "
                   "neighbour &mdash; rather than being assigned an agency "
                   "worker. It depends on clinical need, enrollment in VA health "
                   "care, and whether the local VA offers it at all."),
        "sources": srcs("va_vdc", "va_cc_elig", "va_health_apply", "va_aa"),
        "body": [
            ("What Veteran Directed Care actually is", [
                "<p>This is easy to miss because it sits inside VA.gov&rsquo;s "
                "Geriatrics and Extended Care pages rather than beside the "
                "pension material most families find first. VA.gov&rsquo;s own "
                "description: Veteran Directed Care &ldquo;gives Veterans of all "
                "ages the opportunity to receive the Home and Community Based "
                "Services&rdquo; they need &ldquo;in a consumer-directed "
                "way.&rdquo;</p>",
                "<p>&ldquo;Consumer-directed&rdquo; is the operative word. "
                "Instead of VA (or an agency VA contracts with) choosing and "
                "scheduling an aide, the veteran or their representative "
                "receives help developing a spending plan, then hires workers "
                "themselves &mdash; and VA.gov is explicit that this can include "
                "&ldquo;their own family member or neighbor&rdquo; &mdash; to "
                "help the veteran live independently in the community.</p>",
                "<p>VA.gov lists examples of the daily activities the hired help "
                "can cover: eating, getting dressed, personal grooming, bathing, "
                "using the bathroom, moving from one place to another, and "
                "grocery shopping. It also names who the programme is aimed at: "
                "veterans who need personal care and help with daily activities, "
                "and veterans who are isolated or whose caregiver is under "
                "strain.</p>",
            ]),
            ("Who qualifies, in VA.gov's own words", [
                "<p>VA.gov states the rule in one sentence: &ldquo;All enrolled "
                "Veterans are eligible for Veteran Directed Care if they are "
                "eligible for community care,&rdquo; &ldquo;meet the clinical "
                "criteria for the service, and it is available&rdquo; where they "
                "live. That is three separate gates, and the page is explicit "
                "that services vary by location &mdash; this is not a benefit "
                "every VA medical centre necessarily offers.</p>",
                "<p>The Veteran Directed Care page does not itself spell out what "
                "&ldquo;eligible for community care&rdquo; means, so this guide "
                "read VA.gov's own community care eligibility page rather than "
                "guess. That page sets two basic requirements that must both be "
                "true &mdash; &ldquo;you're enrolled in or eligible for VA health "
                "care&rdquo; and &ldquo;you have approval from your VA health "
                "care team before you get care from a community provider&rdquo; "
                "&mdash; plus at least one of several further conditions, such as "
                "needing a service VA does not provide at any facility or living "
                "somewhere without a full-service VA facility nearby.</p>",
                "<p>This guide has not confirmed, on any VA.gov page, that the "
                "general community-care eligibility rules apply to Veteran "
                "Directed Care exactly as written for an outside specialist "
                "referral &mdash; the Veteran Directed Care page simply says "
                "&ldquo;eligible for community care&rdquo; without cross-linking "
                "the detail. Rather than assume the two pages mean exactly the "
                "same thing in every case, ask a VA social worker whether your "
                "veteran parent clears this gate before ruling the programme in "
                "or out.</p>",
            ]),
            ("This is not Aid and Attendance", [
                "<p>Families researching VA help with senior care usually find "
                '<a href="/guides/va-aid-and-attendance-benefit/">VA Aid and '
                "Attendance</a> first, and it is easy to assume Veteran Directed "
                "Care is the same thing under another name. It is not.</p>",
                "<p>Aid and Attendance is an increased rate added to the "
                "Veterans Pension or Survivors Pension &mdash; a cash benefit, "
                "administered on the benefits side of VA, that a family can put "
                "toward care in any setting. Veteran Directed Care is a health "
                "care service, administered through VA's geriatrics and "
                "extended-care programme, that pays for a defined package of "
                "in-home help rather than handing the veteran cash. One pays a "
                "monthly amount against the veteran's own countable income; the "
                "other funds a spending plan for specific hired help. This guide "
                "found no VA.gov page confirming whether a veteran can draw on "
                "both at once, so it will not guess &mdash; ask a VA social "
                "worker about your specific situation.</p>",
            ]),
            ("How to start", [
                "<p>VA.gov does not describe a separate application form for "
                "Veteran Directed Care itself. What it says instead is to use "
                "the Veteran Decision Aid for Care at Home or in the Community "
                "&ldquo;to help you figure out what home care services or long "
                "term care services may best meet your needs&rdquo; now or in "
                "the future, and then: &ldquo;If Veteran Directed Care seems "
                "right for you, talk with your VA social worker and find out if "
                "it is available&rdquo; in your location.</p>",
                "<p>A veteran who is not yet enrolled in VA health care has to "
                "clear that step first, since enrollment is one of the stated "
                "gates above. VA.gov lists four ways to apply for VA health "
                "care: online, by phone at <strong>877-222-8387</strong> "
                "(Monday&ndash;Friday, 8:00 a.m. to 8:00 p.m. ET), by mailing a "
                "signed VA Form 10-10EZ to the Health Eligibility Center, PO Box "
                "5207, Janesville, WI 53547-5207, or in person at the nearest VA "
                "medical centre or clinic with the same signed form in hand.</p>",
            ]),
            ("A figure this guide will not guess at", [
                "<p>Families will want to know the size of the budget a veteran "
                "actually receives. This guide looked for that figure on VA.gov "
                "and did not find a published national amount &mdash; the page "
                "describes the spending plan as based on an individual "
                "assessment, not a fixed rate. Anything quoting a specific "
                "dollar figure for Veteran Directed Care is not working from a "
                "VA.gov page this guide could locate. Ask the VA social worker "
                "handling the case what the assessed budget would actually "
                "be.</p>",
            ]),
            ("Where this fits with the rest of this site", [
                "<p>If the money question is the pension itself rather than this "
                'programme, see <a href="/guides/va-aid-and-attendance-benefit/">'
                "Does the VA pay for senior care? Aid and Attendance, "
                "explained</a>, which covers the " + F["va_mapr_aa_single"] +
                " ceiling &mdash; the whole pension at the Aid and Attendance rate, "
                "not an amount added to it &mdash; and who qualifies for the pension "
                "underneath it. "
                "Illinois runs its own, separate in-home programme funded "
                'through Medicaid rather than VA &mdash; see <a '
                'href="/guides/illinois-community-care-program/">Can my parent '
                "get paid help at home in Illinois?</a> A veteran parent could "
                "in principle have both a state and a federal route into paid "
                "help at home; this guide has not researched how the two "
                "interact and will not guess.</p>",
                "<p>If the open question is whether your parent needs help at "
                "home at all, rather than how any particular programme pays for "
                'it, the <a href="/">free six-question assessment</a> on this '
                "site walks through that separately. It asks for no name, no "
                "email and no phone number, and your answers never leave your "
                "device.</p>",
            ]),
        ],
    },
    {
        "slug": "illinois-family-caregiver-support-program",
        "bridge": ("Finding help for yourself as the caregiver is a different "
               "question from knowing whether your parent's needs have moved "
               "past what any amount of help at home can cover."),
        "reviewed": "2026-10-29",
        "title": "Is There Help for the Caregiver, Not Just the Parent, in Illinois?",
        "h1": "Is there help for the caregiver, not just the parent, in Illinois?",
        "desc": ("Illinois runs a Family Caregiver Support Program built around "
                 "the person doing the caring, not the person being cared for "
                 "&mdash; respite, counselling, training and a local resource "
                 "centre. Here is what the Department on Aging&rsquo;s own pages "
                 "say it covers, and what they do not say."),
        "intent": "caregiver support",
        "answer": ("<strong>Yes &mdash; Illinois funds a Family Caregiver "
                   "Support Program aimed at the caregiver rather than the "
                   "older adult.</strong> The Illinois Department on Aging "
                   "describes a family caregiver as &ldquo;an adult family "
                   "member or another individual who is an informal provider "
                   "of in-home and community care&rdquo; to an older person, "
                   "and says the programme can connect that caregiver to "
                   "counselling, support groups, training, <strong>respite "
                   "care</strong> and limited supplemental services. It is "
                   "delivered locally through a network of Caregiver Resource "
                   "Centers and the 13 Area Agencies on Aging, not a single "
                   "statewide office &mdash; so the way in is the Senior "
                   "HelpLine, not a form."),
        "sources": srcs("idoa_caregiver", "idoa_crc", "idoa_caregiver_links"),
        "body": [
            ("What the programme actually is", [
                "<p>The Illinois Department on Aging says this programme grew "
                "out of 2000 amendments to the federal Older Americans Act, "
                "which created a National Family Caregiver Support Program; "
                "Illinois &ldquo;was given $4.7 million to develop&rdquo; its "
                "own version with the state&rsquo;s Area Agencies on Aging and "
                "local community-service providers. That is a historical "
                "development figure, not a per-family benefit amount, and this "
                "guide found no current statewide budget figure published "
                "anywhere on the Department&rsquo;s site.</p>",
                "<p>The Department&rsquo;s own definition of who counts as a "
                "&ldquo;family caregiver&rdquo; is broader than a spouse or "
                "adult child: it names &ldquo;an adult family member or "
                "another individual who is an informal provider of in-home "
                "and community care&rdquo; to an older person, and separately "
                "covers grandparents raising grandchildren. &ldquo;Informal "
                "caregiving,&rdquo; in the Department&rsquo;s words, means "
                "unpaid care and support given by family or friends to someone "
                "with a chronic illness or disability.</p>",
            ]),
            ("What it can connect you to", [
                "<p>The Department lists five things the programme does for a "
                "caregiver: provides information about available services; "
                "helps a caregiver get access to those services; connects a "
                "caregiver to individual counselling, support groups or "
                "caregiver training; connects a caregiver to <strong>respite "
                "care</strong>, so that caregivers can be &ldquo;temporarily "
                "relieved from their caregiving responsibilities&rdquo;; and "
                "provides supplemental services &ldquo;on a limited "
                "basis&rdquo; to complement the care a family already "
                "gives.</p>",
                "<p>A separate Department page on its Family and Caregiver "
                "Resource Centers adds detail to that list: each centre can "
                "help locate adult day service, home-delivered meals, "
                "housekeeping assistance, home modification and assistive "
                "device help, transportation, financial and legal "
                "information, caregiver training, case management assistance "
                "and employment programmes &mdash; on top of the counselling "
                "and respite already named.</p>",
            ]),
            ("Respite, in the Department's own words", [
                "<p>Respite is the service most caregivers are actually "
                "looking for, and the Department's Family and Caregiver "
                "Services page describes it plainly: &ldquo;Respite services "
                "are intended to provide caregivers with short-term "
                "relief.&rdquo; It says the length and setting vary &mdash; "
                "respite &ldquo;may be provided for an afternoon, several "
                "days, at home, or in a facility-based setting.&rdquo;</p>",
                "<p>The same page says Area Agencies on Aging assess a "
                "caregiver's own needs using an assessment tool it calls "
                "TCARE, and may refer a caregiver on from there to named "
                "programmes such as Savvy Caregiver or the Stress-Busting "
                "Program for Family Caregivers, as well as support groups, "
                "counselling and what it calls &ldquo;gap-filling "
                "services.&rdquo;</p>",
            ]),
            ("What this guide could not pin down", [
                "<p>None of the three Department pages this guide read states "
                "an income limit for the Family Caregiver Support Program, a "
                "cost to the caregiver, a cap on respite hours, or a formal "
                "application form. The Resource Centers page lists services "
                "and regional contacts and nothing about eligibility or fees "
                "at all. The Department&rsquo;s own answer to &ldquo;Where can "
                "I find out about services nearest to me?&rdquo; is to "
                "&ldquo;inquire at your local Caregiver Resource Center or "
                "your local Area Agency on Aging,&rdquo; or to call the "
                "Senior HelpLine.</p>",
                "<p>This guide will not guess at any of those figures on the "
                "Department's behalf. If a cost, an income test or a waiting "
                "list applies in your case, that answer lives with your local "
                "Area Agency on Aging or Caregiver Resource Center, not on a "
                "page written in Springfield.</p>",
            ]),
            ("How to start", [
                "<p>Call the <strong>Senior HelpLine</strong> on "
                "<strong>1-800-252-8966</strong> (711 TRS for deaf and "
                "speech-impaired callers). The Department also publishes a "
                "provider search tool for finding the Caregiver Resource "
                "Center or Area Agency on Aging that covers your parent's "
                "address, since services are organised locally rather than "
                "from one statewide office.</p>",
                "<p>If your parent lives outside Illinois, the Department's "
                "own guidance is to contact the Caregiver Resource Center "
                "nearest to <em>your parent</em>, not to you &mdash; the "
                "service follows the older adult's location.</p>",
            ]),
            ("Where this fits with the rest of this site", [
                "<p>This programme supports the person doing the caring. It "
                "is not the same thing as Illinois paying for help at home "
                "for the older adult, which is a separate Medicaid-funded "
                'programme covered in <a '
                'href="/guides/illinois-community-care-program/">Can my '
                "parent get paid help at home in Illinois?</a> A family can "
                "in principle use both at once; this guide found no "
                "Department page describing how the two interact, and will "
                "not guess.</p>",
                "<p>If the real question is whether home, with or without "
                "extra help, is still the right setting for your parent, the "
                '<a href="/">free six-question assessment</a> on this site '
                "walks through that separately. It asks for no name, no "
                "email and no phone number, and your answers never leave "
                "your device.</p>",
            ]),
        ],
    },

    {
        "slug": "illinois-senior-health-insurance-program",
        "bridge": ("Picking the right Medicare plan is a different question "
               "from knowing whether Medicare will ever pay for the kind of "
               "care your parent eventually needs."),
        "reviewed": "2026-10-29",
        "title": "Who Can Help My Parent Choose a Medicare Plan for Free in Illinois?",
        "h1": "Who can help my parent choose a Medicare plan for free in Illinois?",
        "desc": ("Illinois runs a free, unbiased Medicare counselling service "
                 "called SHIP. What the Department on Aging's own pages say "
                 "it actually does, what it does not say, and how to reach a "
                 "counsellor directly."),
        "intent": "how-to / free local help",
        "answer": ("<strong>Call the Illinois Senior Health Insurance Program "
                   "(SHIP) on 1-800-252-8966 (711 TRS).</strong> It is a free, "
                   "statewide counselling service for Medicare beneficiaries "
                   "and their caregivers, run by the Illinois Department on "
                   "Aging. SHIP is not affiliated with any insurance company, "
                   "and its counsellors do not sell or solicit insurance of "
                   "any kind &mdash; the advice is not trying to sell your "
                   "parent anything."),
        "sources": srcs("idoa_ship", "idoa_ship_about", "mtools"),
        "body": [
            ("A free, unbiased place to start", [
                "<p>The Illinois Department on Aging describes the Senior "
                "Health Insurance Program, SHIP, as &ldquo;a free statewide "
                "health insurance counseling service for Medicare "
                "beneficiaries and their caregivers.&rdquo; It moved to the "
                "Department on Aging from the Illinois Department of "
                "Insurance in April 2013, and the programme itself dates back "
                "to 1988.</p>",
                "<p>The Department states plainly that &ldquo;SHIP is not "
                "affiliated with any insurance company&rdquo; and that "
                "&ldquo;SHIP counselors do not sell or solicit any type of "
                "insurance.&rdquo; Medicare's own site makes the same point "
                "about the national SHIP network: &ldquo;SHIPs aren't "
                "connected to any insurance companies or health plans.&rdquo; "
                "That independence is the whole reason to call a SHIP "
                "counsellor before calling a plan's own sales line.</p>",
            ]),
            ("What a SHIP counsellor actually does", [
                "<p>The Department's SHIP pages describe volunteer counsellors "
                "as the programme's &ldquo;backbone,&rdquo; trained and "
                "supported by the Department, with local sponsoring "
                "organisations providing office space, and reached "
                "&ldquo;through the Area Agency on Aging network of offices "
                "throughout the state.&rdquo; What a counsellor can help "
                "with, in the Department's own words, includes: educating "
                "consumers and answering questions about Medicare, Medicare "
                "Supplement insurance, long-term care insurance, Medicare "
                "HMOs and other health insurance; analysing Medicare "
                "Supplement and long-term care policies; organising and "
                "assisting with Medicare and Medicare Supplement claims; and "
                "one-on-one confidential counselling, with advocacy and "
                "referrals where appropriate. The Department also publishes "
                "an annual Medicare Choices Guide.</p>",
                "<p>The SHIP page also lists related Department resources a "
                "counsellor can point a caller toward, without stating "
                "figures here: a Medicare Savings Programs chart, an Extra "
                "Help chart, and information on Medicaid income and asset "
                "limits. Ask the counsellor directly whether your parent's "
                "situation fits any of those &mdash; this guide is not going "
                "to estimate an income limit on the Department's behalf.</p>",
            ]),
            ("Medicare's own comparison tool, and where SHIP fits around it", [
                "<p>Medicare.gov's own &ldquo;Helpful tools&rdquo; page "
                "points to its plan-comparison tool at "
                "medicare.gov/plan-compare, where you can &ldquo;find and "
                "compare Medicare Advantage Plans (Part C),&rdquo; other "
                "Medicare health plans and Medicare drug plans, review costs "
                "and services, and enter a parent's actual prescriptions to "
                "estimate what each plan would cost. A separate tool at "
                "medicare.gov/medigap-supplemental-insurance-plans finds "
                "Medicare Supplement (Medigap) policies and premiums by ZIP "
                "code.</p>",
                "<p>The same Medicare.gov page names SHIP directly as the "
                "free, no-strings-attached help for using those tools: "
                "&ldquo;Get free personalized health insurance counseling. "
                "SHIPs aren't connected to any insurance companies or health "
                "plans,&rdquo; and says SHIP counsellors can help with "
                "comparing and joining plans. In other words, the self-serve "
                "comparison lives on Medicare.gov; the person who will sit "
                "with your parent and go through it is SHIP.</p>",
                "<p>Medicare.gov also lists 1-800-MEDICARE (1-800-633-4227, "
                "TTY 1-877-486-2048) as a federal line available around the "
                "clock except some holidays, and a live-chat option for "
                "finding local help. Neither replaces SHIP &mdash; they are "
                "simply other doors into the same federal programme.</p>",
            ]),
            ("What this guide could not pin down", [
                "<p>Neither Department on Aging SHIP page this guide read "
                "states the counselling programme's hours, a typical wait "
                "for an appointment, or a list of named local counsellors by "
                "address. The Department instead points callers to a "
                "&ldquo;Volunteers in Your Area by County&rdquo; listing and "
                "a service locator rather than publishing that detail on the "
                "page itself.</p>",
                "<p>This guide also will not quote a dollar figure for the "
                "Medicare Savings Programs or Extra Help, since doing so "
                "would mean reading it off a chart this guide did not open. "
                "Ask a SHIP counsellor directly whether either applies to "
                "your parent's income.</p>",
            ]),
            ("How to reach a counsellor", [
                "<p>Call the <strong>Senior HelpLine</strong> on "
                "<strong>1-800-252-8966</strong> (711 TRS for deaf and "
                "speech-impaired callers), or email "
                "<strong>Aging.SHIP@illinois.gov</strong>. That is the same "
                "statewide number the Department publishes for its other "
                "aging programmes, so one call can also raise anything else "
                "covered on this site, from home care to caregiver "
                "support.</p>",
            ]),
            ("Where this fits with the rest of this site", [
                "<p>A SHIP counsellor can help your parent pick the right "
                "Medicare plan. It cannot tell you whether Medicare will pay "
                "for the care your parent eventually needs &mdash; for that "
                'distinction, see <a '
                'href="/guides/does-medicare-pay-for-senior-care/">Does '
                "Medicare pay for assisted living or nursing home care?</a></p>",
                "<p>If the real question is what level of care fits your "
                'parent at all, the <a href="/">free six-question '
                "assessment</a> on this site walks through that separately. "
                "It asks for no name, no email and no phone number, and your "
                "answers never leave your device.</p>",
            ]),
        ],
    },

    {
        "slug": "illinois-medicare-savings-program",
        "bridge": ("Qualifying for help with a Medicare premium says nothing "
               "about what kind of care your parent actually needs, or "
               "whether assisted living is even the right next step."),
        "reviewed": "2026-10-30",
        "title": "Illinois Medicare Savings Programs: QMB, SLMB and QI Explained",
        "h1": "Can Illinois help pay my parent's Medicare premium? QMB, SLMB and QI, explained",
        "desc": ("Illinois runs three Medicare Savings Programs that use "
                 "Medicaid to pay part or all of a Medicare premium. What "
                 "QMB, SLMB and QI each cover, the state's dated 2026 "
                 "income and asset limits, and how to apply."),
        "intent": "how-to / eligibility",
        "answer": ("<strong>Illinois runs three Medicare Savings Programs &mdash; QMB, "
                   "SLMB and QI &mdash; that use Medicaid to pay part or all of a "
                   "Medicare beneficiary's premium, and QMB also pays Medicare's "
                   "deductibles and coinsurance.</strong> A caseworker decides which "
                   "of the three a person qualifies for, against income and asset "
                   "limits the state republishes every April. Medicare.gov's own "
                   "advice to anyone unsure: &ldquo;Even if you don't think you "
                   "qualify, you should still apply.&rdquo;"),
        "sources": srcs("mmsp", "ilaging_msp_chart", "hfs_qmb"),
        "body": [
            ("Three programmes that pay Medicare costs through Medicaid", [
                "<p>The Illinois Department on Aging's own chart describes the "
                "Medicare Savings Program plainly: it &ldquo;is a State Medicaid "
                "program that can help to pay Medicare premiums, and possibly "
                "deductibles, and coinsurance for Medicare beneficiaries (elderly "
                "or disabled) who qualify.&rdquo; It is not a separate pension or a "
                "new Medicare benefit &mdash; it is Medicaid money covering part of "
                "what Medicare already charges.</p>",
                "<p>Medicare.gov describes three tiers a state runs: the "
                "<strong>Qualified Medicare Beneficiary (QMB)</strong> programme, "
                "the <strong>Specified Low-Income Medicare Beneficiary (SLMB)</strong> "
                "programme, and the <strong>Qualifying Individual (QI)</strong> "
                "programme. QMB has the widest coverage and the lowest income limit; "
                "SLMB and QI pay for less but allow higher income. Medicare.gov also "
                "lists a fourth, narrower programme called Qualified Disabled and "
                "Working Individual (QDWI), limited to a specific group of people "
                "with disabilities who returned to work and lost premium-free Part "
                "A. The Illinois chart this guide relied on for state figures does "
                "not cover QDWI, so neither does this guide.</p>",
            ]),
            ("What each programme actually pays for", [
                "<p>Illinois's own QMB brochure states that the programme covers "
                "&ldquo;payment of Medicare Part A monthly premiums when "
                "applicable,&rdquo; the Part A deductible and coinsurance, the Part "
                "B monthly premium and annual deductible, and the Part B 20 percent "
                "coinsurance. Medicare.gov adds a practical consequence: once "
                "enrolled in QMB, &ldquo;your provider isn't allowed to bill you&rdquo; "
                "for the services and items Medicare covers, beyond a small Medicaid "
                "copayment in some cases.</p>",
                "<p>SLMB and QI are narrower &mdash; both pay the Part B premium "
                "only, nothing toward deductibles or coinsurance. The difference "
                "between them is mainly procedural: Medicare.gov describes QI as "
                "&ldquo;only available for people who don't qualify for any other "
                "Medicaid coverage or benefits,&rdquo; and says it requires a fresh "
                "application every year, approved first-come, first-served, with "
                "priority given to people who received it the previous year. SLMB "
                "carries no such annual reapplication requirement on the Medicare.gov "
                "page.</p>",
            ]),
            ("Illinois's income and asset limits for 2026", [
                "<p>The Department on Aging's 2026 chart gives these monthly income "
                "and resource limits: <strong>QMB</strong>, set at 100% of the "
                "federal poverty level, is <strong>$1,330 a month for one person or "
                "$1,803 for a couple</strong>, with an asset limit of $9,950 for one "
                "person or $14,910 for a couple. <strong>SLMB</strong>, at 120% FPL, "
                "is <strong>$1,596 for one person or $2,164 for a couple</strong>, "
                "same asset limits. <strong>QI</strong>, at 135% FPL, is "
                "<strong>$1,796 for one person or $2,435 for a couple</strong>, same "
                "asset limits again.</p>",
                "<p>The chart adds three notes worth repeating rather than "
                "smoothing over: the figures are &ldquo;estimates based on the "
                "Federal Poverty Level percentages,&rdquo; with the exact figures "
                "posted by the Illinois Department of Human Services each &ldquo;Early "
                "April&rdquo;; Illinois automatically disregards $25 of income, so "
                "$25 should be added to a household's income before comparing it "
                "against the limits above; and the asset limits shown do not yet "
                "include an additional $1,500 (single) or $3,000 (couple) burial "
                "allowance deduction a household may also claim.</p>",
            ]),
            ("A set of figures this guide will not use", [
                "<p>Illinois's own QMB brochure (HFS 3352) states a monthly income "
                "limit of $1,073 for one person or $1,452 for a couple, and an asset "
                "limit of $7,970 or $11,960 with dependents &mdash; figures well "
                "below the Department on Aging's dated 2026 chart above. The "
                "brochure says these limits &ldquo;change every April&rdquo; but "
                "never states which year its own numbers reflect, which, set "
                "against a chart that is both dated and self-described as the "
                "current year's estimate, reads as an older page left live rather "
                "than a second current figure. This guide uses the dated chart and "
                "leaves the undated brochure numbers out. Confirm your parent's "
                "exact current limits when you apply, rather than relying on either "
                "number once more time has passed.</p>",
            ]),
            ("The extra benefit that comes bundled in: Extra Help", [
                "<p>Medicare.gov states that qualifying for QMB, SLMB or QI brings "
                "automatic qualification for <strong>Extra Help</strong>, the "
                "federal programme that caps what a beneficiary pays toward Part D "
                "prescription drug costs. For 2026, Medicare.gov gives that cap as "
                "<strong>no more than $12.65 for each covered drug</strong>. A "
                "household applying for one of the three Medicare Savings Programs "
                "is therefore applying for drug-cost help at the same time, without "
                "a separate form.</p>",
            ]),
            ("How to apply", [
                "<p>Illinois's QMB brochure directs applicants to their nearest "
                "Illinois Department of Human Services <strong>Family Community "
                "Resource Center (FCRC)</strong>, where a caseworker can help "
                "complete the application; bring a Medicare card, or a letter "
                "stating Medicare eligibility, and the FCRC will notify you in "
                "writing whether you qualify. Questions can go to the DHS Helpline "
                "on <strong>1-800-843-6154</strong> (TTY 1-866-324-5553, relay 11), "
                "Monday&ndash;Friday 8:30 a.m. to 5:00 p.m., excluding state "
                "holidays.</p>",
                "<p>The Department on Aging's 2026 chart names a second route: it "
                "tells applicants &ldquo;you can apply at: "
                "https://abe.illinois.gov/,&rdquo; the state's online Application "
                "for Benefits Eligibility portal. This guide did not independently "
                "open that site to describe what the application screens look like, "
                "so treat it as a name and address to go to, not a description this "
                "guide can vouch for beyond what the chart itself says.</p>",
            ]),
            ("Where this fits with the rest of this site", [
                "<p>A Medicare Savings Program only ever touches a Medicare "
                "premium, deductible or coinsurance &mdash; it has nothing to do "
                "with paying for assisted living, memory care or a nursing home. "
                "For that much larger kind of Medicaid help, see "
                '<a href="/guides/illinois-medicaid-long-term-care/">How Illinois '
                "Medicaid pays for long-term care</a>, and for what Medicare itself "
                "will and will not cover, see "
                '<a href="/guides/does-medicare-pay-for-senior-care/">Does Medicare '
                "pay for assisted living or nursing home care?</a></p>",
                "<p>If the real question is what level of care your parent needs in "
                'the first place, the <a href="/">free six-question assessment</a> '
                "on this site walks through that separately. It asks for no name, "
                "no email and no phone number, and your answers never leave your "
                "device.</p>",
            ]),
        ],
    },
    {
        "slug": "illinois-advance-directive-power-of-attorney",
        "bridge": ("Naming who decides your parent&rsquo;s medical care is a "
               "different question from knowing what kind of care they "
               "actually need right now."),
        "reviewed": "2026-10-31",
        "title": "Power of Attorney for Health Care in Illinois, Explained",
        "h1": "Does my parent need a power of attorney for health care in Illinois?",
        "desc": ("Illinois does not require a power of attorney for health care, "
                 "but without one state law still appoints a decision-maker for "
                 "your parent, in a fixed order you do not get to choose. What "
                 "each of Illinois&rsquo;s four advance directives does, and who "
                 "decides if your parent has none."),
        "intent": "legal planning question",
        "answer": ("<strong>No Illinois law requires one</strong>, but if your "
                   "parent never signs a Power of Attorney for Health Care, "
                   "Illinois law still appoints someone to decide for them "
                   "&mdash; in a fixed order you do not get to pick, running from "
                   "a court-appointed guardian through a spouse, adult children, "
                   "parents, siblings and grandchildren before it ever reaches a "
                   "close friend. A Power of Attorney for Health Care lets your "
                   "parent name that person themselves, while they still can."),
        "sources": srcs("idph_adv_directives", "ilaging_adv_directives",
                        "ilaging_legal_assistance"),
        "body": [
            ("The four advance directives Illinois recognises", [
                "<p>The Illinois Department of Public Health describes four "
                "separate documents, each answering a different question, and "
                "each with its own state law behind it:</p>",
                "<ul class=\"res__list\">"
                "<li><strong>Power of Attorney for Health Care</strong> &mdash; "
                "names an agent to make health care decisions when your parent "
                "cannot (Illinois Power of Attorney Act)</li>"
                "<li><strong>Living Will Declaration</strong> &mdash; states, in "
                "advance, whether to withhold or withdraw death-delaying "
                "procedures if your parent has a terminal condition and cannot "
                "say so themselves (Illinois Living Will Act, 755 ILCS 35/1)</li>"
                "<li><strong>Mental Health Treatment Preference Declaration</strong> "
                "&mdash; records consent to, or refusal of, specific mental health "
                "treatments in advance (Mental Health Treatment Preference "
                "Declaration Act, 755 ILCS 43/10)</li>"
                "<li><strong>Practitioner Orders for Life-Sustaining Treatment "
                "(POLST)</strong> &mdash; a medical order, signed by a doctor as "
                "well as your parent, setting out which life-sustaining "
                "treatments to use or withhold (Health Care Surrogate Act)</li>"
                "</ul>",
                "<p>None of the four is required. The Illinois Department of "
                "Public Health states plainly that no facility, health care "
                "professional or insurer can require your parent to execute any "
                "of them as a condition of receiving treatment or insurance: "
                "&ldquo;It is entirely your decision.&rdquo;</p>",
            ]),
            ("What a Power of Attorney for Health Care actually does", [
                "<p>Your parent (the <strong>principal</strong>) names an "
                "<strong>agent</strong> to make personal and health care "
                "decisions on their behalf, under the Illinois Power of Attorney "
                "Act. The Illinois Department of Public Health sets out what that "
                "agent can and cannot do:</p>",
                "<ul class=\"res__list\">"
                "<li>The agent must follow your parent&rsquo;s specific "
                "instructions, including on life-sustaining treatment and "
                "anatomical gifts</li>"
                "<li>The agent <strong>cannot be your parent&rsquo;s own health "
                "care professional or other health care provider</strong></li>"
                "<li>Unless your parent sets a time limit, the power lasts from "
                "signing until death</li>"
                "<li>Your parent can name a backup agent, and can cancel the "
                "document at any time &mdash; changes must be made in "
                "writing</li>"
                "<li>Someone other than the agent should witness the "
                "signing</li>"
                "<li>Illinois accepts an electronic copy if the signed original "
                "is unavailable</li></ul>",
                "<p>Free forms &mdash; a &ldquo;Power of Attorney for Health "
                "Care&rdquo; document and a Spanish-language version &mdash; are "
                "published by both the Illinois Department of Public Health and "
                "the Illinois Department on Aging.</p>",
            ]),
            ("If there is no Power of Attorney, Illinois still picks someone "
             "&mdash; just not who your family might choose", [
                "<p>This is the part most families never learn until they need "
                "it. If your parent has no Power of Attorney for Health Care and "
                "loses the ability to decide, Illinois does not leave the "
                "decision to whichever relative is in the room. Under the "
                "Health Care Surrogate Act, <strong>two doctors must first "
                "certify</strong> that your parent cannot make their own "
                "decisions. Only then is a surrogate decision-maker identified "
                "&mdash; and the law picks that person from a fixed order, not "
                "from family agreement:</p>",
                "<ol class=\"res__list\">"
                "<li>Guardian of the person</li>"
                "<li>Spouse</li>"
                "<li>Adult children</li>"
                "<li>Either parent</li>"
                "<li>Adult siblings</li>"
                "<li>Adult grandchildren</li>"
                "<li>A close friend</li>"
                "<li>Guardian of the estate</li></ol>",
                "<p>That order has real limits built into it, too. A surrogate "
                "who is not a court-appointed guardian <strong>cannot</strong> "
                "direct the withdrawal or withholding of life-sustaining "
                "treatment unless two doctors certify a qualifying condition "
                "&mdash; a terminal condition, permanent unconsciousness, or an "
                "incurable or irreversible condition. The same surrogate also "
                "cannot consent to electroconvulsive treatment, psychotropic "
                "medication, or admission to a mental health facility, without "
                "a court&rsquo;s approval. A Power of Attorney for Health Care "
                "is what lets your parent choose their own decision-maker "
                "instead of relying on this default order, and lets that chosen "
                "agent act without those extra restrictions.</p>",
            ]),
            ("The living will and the POLST answer narrower questions", [
                "<p>A <strong>Living Will</strong> only applies if your parent "
                "has a terminal condition <em>and</em> cannot state their own "
                "wishes &mdash; it does nothing before then. Illinois requires "
                "two witnesses, neither of whom can be your parent&rsquo;s own "
                "health care professional, and the Illinois Department of Public "
                "Health states that food and water cannot be withdrawn under a "
                "living will if doing so would be the only cause of death. It "
                "also does not take effect if your parent is pregnant and the "
                "treating provider believes a live birth is possible. If your "
                "parent has both a living will and a Power of Attorney for "
                "Health Care, the named agent decides &mdash; the living will "
                "only governs if that agent is unavailable.</p>",
                "<p>A <strong>POLST</strong> is different in kind, not just in "
                "name: it is a medical order, not only a statement of wishes. It "
                "needs your parent&rsquo;s signature (or an authorised "
                "representative&rsquo;s) <em>and</em> the attending "
                "practitioner&rsquo;s, and the Illinois Department of Public "
                "Health states it will not be entered into the medical record "
                "without every required signature. It can record, among other "
                "things, that cardiopulmonary resuscitation should not be "
                "attempted if your parent&rsquo;s heart or breathing stops.</p>",
            ]),
            ("What a nursing home or hospital must do — and must never do", [
                "<p>Under the federal Patient Self-Determination Act, Medicare "
                "and Medicaid providers &mdash; including nursing facilities "
                "&mdash; must tell your parent about the right to make an "
                "advance directive, in the Illinois Department of Public "
                "Health&rsquo;s words, &ldquo;upon admission to a facility or "
                "when provision of care begins.&rdquo; No facility can condition "
                "treatment on actually signing one.</p>",
                "<p>If a facility objects to following your parent&rsquo;s "
                "directive on moral or religious grounds, the Illinois "
                "Department of Public Health states it must say so and must "
                "keep providing care until your parent can be transferred to a "
                "provider who will follow it. It cannot simply stop caring for "
                "your parent while that objection stands.</p>",
            ]),
            ("Where to get the forms, and free help filling them out", [
                "<p>The Illinois Department on Aging and the Illinois Department "
                "of Public Health both publish free forms for a Power of "
                "Attorney for Health Care, a Living Will, a Mental Health "
                "Treatment Preference Declaration and a POLST. The POLST form is "
                "available in English, Arabic, Simplified and Traditional "
                "Chinese, French, Hindi, Korean, Polish and Spanish.</p>",
                "<p>Filling one out does not have to mean hiring a lawyer. The "
                "Illinois Department on Aging funds local Area Agencies on "
                "Aging to contract with legal aid representatives who, in the "
                "Department&rsquo;s own words, &ldquo;may help with a wide "
                "variety of civil law issues.&rdquo; Find the agency covering "
                "Evanston through the Department&rsquo;s AAA map tool or its "
                "provider Service Locator, or call the Senior HelpLine on "
                "<strong>" + F["ccp_line"] + "</strong> (711 TRS) to ask where to "
                "start.</p>",
            ]),
            ("Where this fits with the rest of this site", [
                "<p>None of this decides what kind of care is right for your "
                "parent &mdash; it only decides who gets to make that call, and "
                "under what rules, once a decision has to be made. For the "
                "differences between the levels of care those decisions are "
                "actually about, see "
                '<a href="/guides/levels-of-senior-care-explained/">Assisted '
                "living, memory care, skilled nursing and rehabilitation "
                "&mdash; what is the difference?</a></p>",
                "<p>If the open question in your family is what level of care "
                'your parent needs in the first place, the <a href="/">free '
                "six-question assessment</a> on this site walks through that "
                "separately. It asks for no name, no email and no phone number, "
                "and your answers never leave your device.</p>",
            ]),
        ],
    },

    {
        "slug": "illinois-benefit-access-program",
        "bridge": ("A cheaper license plate and free transit rides are a "
               "different question from whether your parent can still get "
               "around safely enough to use either one."),
        "reviewed": "2026-11-01",
        "title": "Illinois Benefit Access Program: Free Transit and a Cheaper License Plate",
        "h1": "Illinois Benefit Access Program: free transit and a cheaper license plate",
        "desc": ("A state programme, formerly called Circuit Breaker, gives "
                 "income-eligible seniors and people with disabilities free "
                 "rides on public transit and a discounted vehicle "
                 "registration &mdash; here is the Illinois Department on "
                 "Aging&rsquo;s own eligibility rule, income limits and how "
                 "to apply."),
        "intent": "benefits assistance",
        "answer": ("<strong>Yes &mdash; the Illinois Department on Aging runs "
                   "the Benefit Access Program</strong>, which gives "
                   "qualifying seniors and people with disabilities two "
                   "things: free rides on local public transit, and a "
                   "discounted license plate sticker through the Secretary "
                   "of State. To qualify, a person must be 65 or older "
                   "before January 1 of the current year (or turning 65 "
                   "this year), live in Illinois, and have had gross "
                   "household income below a published limit for the last "
                   "closed tax year &mdash; <strong>$33,562</strong> for one "
                   "person, <strong>$44,533</strong> for two, or "
                   "<strong>$55,500</strong> for three, as stated on the "
                   "Department&rsquo;s own page. Applications are online "
                   "only, and eligibility can take up to eight weeks to "
                   "determine."),
        "sources": srcs("idoa_benefit_access", "idoa_benefit_access_faq",
                        "idoa_benefit_access_ridefree"),
        "body": [
            ("What the programme actually gives you", [
                "<p>The Illinois Department on Aging describes Benefit "
                "Access as two separate benefits bundled under one "
                "application. The first is a <strong>Ride Free Transit "
                "benefit</strong>: approved seniors and people with "
                "disabilities ride free on local public transit, though the "
                "Department says the rider must still &ldquo;contact your "
                "local public transit system to find out what their "
                "requirements are&rdquo; before the free ride works in "
                "practice. The second is a <strong>license plate "
                "discount</strong>, administered through the Secretary of "
                "State&rsquo;s Office once a certificate of eligibility is "
                "presented there.</p>",
                "<p>This programme was formerly known as the Circuit "
                "Breaker programme; the Department&rsquo;s current pages use "
                "the name Benefit Access Program throughout and describe no "
                "separate cash payment or rebate &mdash; the benefit is the "
                "transit ride and the plate discount themselves, not a "
                "cheque.</p>",
            ]),
            ("Who qualifies", [
                "<p>Age or disability: the Department&rsquo;s main Benefit "
                "Access page says an applicant must be &ldquo;65 years of "
                "age or older before January 1 of the current year&rdquo; "
                "(or turning 65 this year), while the Department&rsquo;s own "
                "FAQ page states it slightly differently, as 65 or older "
                "&ldquo;by December 31 of the current year.&rdquo; Both "
                "pages agree on the alternative path: at least 16 before "
                "January 1 of the current year and determined &ldquo;totally "
                "and permanently disabled&rdquo; before that date. This "
                "guide read both pages and is reporting the discrepancy "
                "rather than picking one &mdash; if your parent&rsquo;s "
                "birthday falls between those two dates, confirm directly "
                "with the Senior HelpLine before assuming either way.</p>",
                "<p>The FAQ page lists what counts as proof of disability: a "
                "determination from the Social Security Administration, the "
                "Veterans Administration, Civil Service or Railroad "
                "Retirement; or a Class 2 disability card from the Illinois "
                "Secretary of State&rsquo;s office; or a completed "
                "&ldquo;Attachment A Physician&rsquo;s Statement&rdquo; "
                "meeting the Social Security Administration&rsquo;s total "
                "disability criteria.</p>",
                "<p>Residency: the applicant must live in Illinois at the "
                "time of filing.</p>",
                "<p>Income: the Department&rsquo;s pages set <strong>total "
                "gross income for the last closed tax year</strong> below "
                "<strong>$33,562</strong> for a one-person household (the "
                "applicant only); <strong>$44,533</strong> for a two-person "
                "household (the applicant and a spouse, or the applicant "
                "and one &ldquo;Qualified Additional Resident&rdquo;); or "
                "<strong>$55,500</strong> for a three-person household "
                "(applicant, spouse and one Qualified Additional Resident, "
                "or the applicant and two Qualified Additional Residents). "
                "The FAQ page is explicit that this is not a fresh annual "
                "figure: it notes &ldquo;income limit increase effective "
                "1/1/2020,&rdquo; meaning these three thresholds have been "
                "unchanged since 2020 rather than adjusted since. A "
                "spouse&rsquo;s income counts if the couple was married and "
                "living together on December 31 of the prior year; a "
                "surviving spouse files as single using only their own "
                "income; and a Qualified Additional Resident&rsquo;s income "
                "is explicitly excluded.</p>",
                "<p>A Qualified Additional Resident, per the FAQ, is someone "
                "other than a spouse who lived with the applicant for the "
                "relevant period, received more than half their financial "
                "support from the applicant (or the applicant and spouse), "
                "and is not filing their own Benefit Access Application. "
                "Qualified Additional Residents do not themselves receive "
                "benefits &mdash; they only affect the household size used "
                "to set the applicant&rsquo;s income limit.</p>",
                "<p>Citizenship: the FAQ states a person does <strong>not</strong> "
                "need to be a U.S. citizen to qualify, but does need a Social "
                "Security number to complete the application &mdash; and, if "
                "married, both spouses need their own.</p>",
            ]),
            ("How to apply, what happens after, and how long it lasts", [
                "<p>The Department is explicit that the <strong>Benefit "
                "Access Application must be filed online</strong> &mdash; "
                "&ldquo;Paper applications are not available.&rdquo; A "
                "married couple living together files one joint application "
                "reporting combined income, except where one or both live "
                "in a nursing home, or where the couple is legally separated "
                "and living at different addresses, in which case the FAQ "
                "describes filing separately (with proof of separation in "
                "the latter case). Once submitted, an applicant can check "
                "status on the Department&rsquo;s site 48 hours later. "
                "Processing to determine eligibility &ldquo;may take up to "
                "8 weeks, depending on documentation.&rdquo;</p>",
                "<p>After approval, the applicant prints a certificate of "
                "eligibility. For the license plate discount, the Department "
                "says it &ldquo;will be available 10 business days after "
                "approval,&rdquo; for presentation to the Secretary of "
                "State&rsquo;s Office. For the transit benefit, the separate "
                "Ride Free Transit Benefit page says that benefit instead "
                "&ldquo;will be available to the transit district the "
                "following day you are approved&rdquo; &mdash; a different, "
                "faster timeline than the plate discount, before the rider "
                "then contacts their local transit system about its own "
                "requirements.</p>",
                "<p>The FAQ states eligibility is good for <strong>two "
                "years</strong> from approval, and that an applicant may "
                "reapply beginning 90 days before it expires &mdash; "
                "consistent with the Ride Free page&rsquo;s instruction to "
                "submit a new application &ldquo;every other year.&rdquo;</p>",
                "<p>For help with the application, the Department points "
                "people to a local Senior Health Assistance Program office "
                "or Area Agency on Aging, or the Senior HelpLine at "
                "<strong>" + F["ccp_line"] + "</strong> (711 TRS for deaf and "
                "speech-impaired callers). The Department advises having a "
                "Social Security number ready when calling.</p>",
            ]),
            ("What this guide did not find", [
                "<p>None of the three Department pages this guide read "
                "states a specific dollar value for the license plate "
                "discount itself &mdash; that fee is set by the Secretary of "
                "State, not the Department on Aging, and this guide will "
                "not borrow a figure from a page it did not read. The pages "
                "also do not describe how the Ride Free transit benefit "
                "interacts with any separate paratransit programme a county "
                "or transit district might run; the only instruction given "
                "is to ask the local transit system directly.</p>",
            ]),
            ("Where this fits with the rest of this site", [
                "<p>Benefit Access is about the cost of getting around and "
                "the cost of registering a car &mdash; it has nothing to do "
                "with paying for assisted living, home care or a nursing "
                "home. If the bigger question in your family is how "
                "Illinois helps pay for actual care, see "
                '<a href="/guides/illinois-medicaid-long-term-care/">How '
                "Illinois Medicaid pays for long-term care</a> or "
                '<a href="/guides/illinois-community-care-program/">Can my '
                "parent get paid help at home in Illinois?</a></p>",
                "<p>If the real question is whether your parent can still "
                "get around safely enough for a free bus or train ride to "
                'matter, the <a href="/">free six-question assessment</a> '
                "on this site walks through that separately. It asks for no "
                "name, no email and no phone number, and your answers never "
                "leave your device.</p>",
            ]),
        ],
    },

    {
        "slug": "illinois-home-delivered-meals",
        "bridge": ("Knowing your parent can get a meal delivered to the door is a "
               "different question from knowing whether living alone, even "
               "well-fed, is still safe."),
        "reviewed": "2026-11-02",
        "title": "Can My Parent Get Home-Delivered Meals in Illinois?",
        "h1": "Can my parent get home-delivered meals in Illinois?",
        "desc": ("Illinois funds a Senior Nutrition Program that delivers meals "
                 "to older adults who cannot easily cook or shop for themselves "
                 "&mdash; what it actually covers, who it is for, and how to "
                 "reach the agency that runs it where you live."),
        "intent": "staying at home",
        "answer": ("Likely yes. The Illinois Department on Aging funds a "
                   "<strong>Senior Nutrition Program</strong> that pays local "
                   "providers to deliver meals to the homes of older adults, "
                   "alongside group dining at community sites. The "
                   "department's own page states this is for "
                   "<strong>older adults age 60 and up</strong> &mdash; it does "
                   "not publish an income limit or a fee for the service. You "
                   "do not apply to the state directly; you contact your local "
                   "<strong>Area Agency on Aging</strong> or a nutrition "
                   "provider, and the easiest way to be connected to the "
                   "right one is the Senior HelpLine."),
        "sources": srcs("idoa_nutrition", "idoa_aaa"),
        "body": [
            ("What the Senior Nutrition Program actually provides", [
                "<p>The Illinois Department on Aging funds local providers "
                "under what it calls the Senior Nutrition Program, with two "
                "main services. <strong>Home-delivered meals</strong> are "
                "brought to an older adult's home, largely by volunteers. "
                "<strong>Group, or congregate, dining</strong> happens at "
                "around 400 sites statewide &mdash; senior centres, churches, "
                "senior housing, community buildings, and in some areas "
                "restaurants and food trucks.</p>",
                "<p>The department states that every meal served under the "
                "programme must provide at least one-third of the daily "
                "recommended dietary allowances. Providers also offer "
                "nutrition screening &mdash; a nutritional-risk checklist "
                "available in English and Spanish &mdash; plus nutrition "
                "education, counselling and cooking classes in some areas.</p>",
                "<p>A related benefit on the same page is the "
                "<strong>Senior Farmers Market Nutrition Program</strong>: "
                "in 37 counties, eligible seniors receive checks, distributed "
                "at local senior facilities, that can be redeemed for fresh "
                "produce at participating farmers' markets during a season "
                "the department runs from 10 July to 31 October. Ask your "
                "local Area Agency on Aging whether your county is one of "
                "the 37 and whether your parent qualifies.</p>",
            ]),
            ("Who qualifies, and what this guide will not publish", [
                "<p>The department's nutrition page states home-delivered "
                "meals are for <strong>older adults age 60+</strong>. It does "
                "not state an income test for either home-delivered meals or "
                "group dining, and it does not state a fee or a suggested "
                "donation amount on that page. Rather than guess at a cost or "
                "an income cut-off the state's own page does not give, this "
                "guide leaves both out &mdash; ask the provider you are "
                "referred to what, if anything, is asked of your household "
                "when you sign up.</p>",
                "<p>The page also does not say whether a waiting list exists "
                "in any given area, or how long it typically takes to start "
                "receiving meals once contacted. Demand for Older Americans "
                "Act services can outrun funding in a given county in a given "
                "year; this guide will not predict your parent's wait from a "
                "state webpage that does not address it. Ask the local agency "
                "directly when you call.</p>",
            ]),
            ("Finding the agency that covers Evanston", [
                "<p>Illinois delivers this programme through a network of "
                "<strong>Area Agencies on Aging</strong>, each covering a "
                "Planning and Service Area the department has drawn across "
                "the state. The department's own Area Agencies on Aging page "
                "lets you find yours by clicking a map, browsing a list, or "
                "picking your county from a drop-down &mdash; and it lists "
                "Cook County twice, once for the City of Chicago and once "
                "for suburban Cook County, so Evanston families need to pick "
                "the entry that actually matches a north-suburban address, "
                "not the Chicago one.</p>",
                "<p>The department's map-based lookup tool is not something "
                "this guide can read and quote text from, so it will not "
                "name a specific agency, address or direct phone number here "
                "that it did not itself verify on the page. The reliable "
                "route is the same one the department gives on its nutrition "
                "page: call the <strong>Senior HelpLine</strong> at "
                "<strong>1-800-252-8966 (711 TRS)</strong> and ask to be "
                "connected to the nutrition provider or Area Agency on Aging "
                "that covers your parent's address.</p>",
            ]),
            ("Where this fits with the rest of this site", [
                "<p>This is a different programme from the one most families "
                "find first. "
                '<a href="/guides/illinois-community-care-program/">Can my '
                "parent get paid help at home in Illinois?</a> covers "
                "homemaker help, adult day service and emergency response "
                "through the Community Care Program, which runs on its own "
                "asset and need test. The nutrition programme described here "
                "is funded separately, under the federal Older Americans Act, "
                "and is not means-tested on this page the way the Community "
                "Care Program is.</p>",
                "<p>If the person who needs support is the one doing the "
                "caring rather than the one being cared for, see "
                '<a href="/guides/illinois-family-caregiver-support-program/">Is '
                "there help for the caregiver, not just the parent?</a></p>",
                "<p>If the open question in your family is whether home is "
                "still the right setting at all, rather than whether a meal "
                'can get delivered to it, the <a href="/">free six-question '
                "assessment</a> on this site walks through that separately. "
                "It asks for no name, no email and no phone number, and your "
                "answers never leave your device.</p>",
            ]),
        ],
    },

    {
        "slug": "illinois-elder-abuse-reporting",
        "bridge": ("Reporting a suspected problem is a different question from "
               "deciding whether the living situation that let it happen can "
               "still be made safe."),
        "reviewed": "2026-11-03",
        "title": "What to Do About Suspected Elder Abuse or Neglect at Home in Illinois",
        "h1": "What to do about suspected elder abuse or neglect at home in Illinois",
        "desc": ("Illinois runs a statewide Adult Protective Services hotline for "
                 "abuse, neglect, exploitation and self-neglect of an older adult "
                 "living in the community &mdash; a different line from the one "
                 "that covers a nursing home or assisted living facility. Here is "
                 "who it covers, what the state's own pages say happens after you "
                 "call, and the line it does not reach."),
        "intent": "how-to / safety",
        "answer": ("Call the Illinois <strong>Adult Protective Services (APS) "
                   "hotline at 1-866-800-1409</strong>, 24 hours a day (711 for "
                   "Illinois Relay). The Illinois Department on Aging says APS "
                   "&ldquo;investigates reports of abuse, neglect, exploitation, "
                   "and self-neglect of adults age 60 or older, and adults age "
                   "18-59 with disabilities living in the community.&rdquo; That "
                   "last phrase matters: APS is for someone living at home or in "
                   "the community, not in a nursing home or assisted living "
                   "facility &mdash; a suspected problem there goes to the Long-"
                   "Term Care Ombudsman or the Illinois Department of Public "
                   "Health instead."),
        "sources": srcs("idoa_aps_program", "idoa_aps_definitions", "idoa_engage"),
        "body": [
            ("Two different hotlines, and this guide is about one of them", [
                "<p>Illinois splits elder-safety reporting the same way it "
                "splits facility complaints: by where the person lives. If "
                "your parent lives in their own home, an apartment, or with "
                "family &mdash; anywhere outside a licensed care facility "
                "&mdash; the Illinois Department on Aging's <strong>Adult "
                "Protective Services</strong> program is the state channel. "
                "Its own programme page states it &ldquo;investigates reports "
                "of abuse, neglect, exploitation, and self-neglect of adults "
                "age 60 or older, and adults age 18-59 with disabilities "
                "living in the community.&rdquo;</p>",
                "<p>A concern about a nursing home or assisted living "
                "community is a different problem with a different number "
                "&mdash; the Long-Term Care Ombudsman Program or the Illinois "
                "Department of Public Health's Central Complaint Registry, "
                "both covered in "
                '<a href="/guides/illinois-care-facility-complaint/">How to '
                "report a problem at an Illinois care facility</a>. That "
                "guide notes an unexplained number &mdash; "
                "<strong>1-866-800-1409</strong> &mdash; sitting on the "
                "Ombudsman Program's page without any description of what it "
                "reaches. Having now read the Department on Aging's own APS "
                "page, that number is the Adult Protective Services hotline "
                "described here, not a facility line.</p>",
            ]),
            ("What counts as abuse, neglect, exploitation and self-neglect", [
                "<p>The Department on Aging's APS Definitions page gives "
                "short, plain definitions for each term it investigates. "
                "<strong>Abuse</strong> &ldquo;means causing any physical, "
                "mental, or sexual injury to an eligible adult,&rdquo; and the "
                "department folds financial harm into the same word: abuse "
                "includes &ldquo;exploitation of such adult's financial "
                "resources.&rdquo; <strong>Neglect</strong> is defined as "
                "&ldquo;another individual's failure to provide an eligible "
                "adult with or willful withholding from an eligible adult&rdquo; "
                "the basic necessities of life, &ldquo;including, but not "
                "limited to, food, clothing, shelter, or health care.&rdquo; "
                "<strong>Financial exploitation</strong> is &ldquo;use of an "
                "eligible adult's resources by another to the disadvantage of "
                "that adult&rdquo; or for &ldquo;the profit or advantage of a "
                "person other than that adult.&rdquo;</p>",
                "<p>The same page lists <strong>self-neglect</strong> as its "
                "own allegation type &mdash; a report that an older adult's "
                "own inability to care for themselves, with no one else at "
                "fault, has put them at risk &mdash; but the page this guide "
                "read does not itself spell out a definition for that term. A "
                "family worried that a parent living alone is no longer "
                "managing &mdash; not eating, not taking medication, not "
                "keeping the home safe &mdash; does not need a suspect to "
                "call; self-neglect on its own is a reportable concern.</p>",
            ]),
            ("How to report, and what the state says happens next", [
                "<p>The hotline is <strong>1-866-800-1409</strong>, which the "
                "department's APS Definitions page gives as the number "
                "&ldquo;to report abuse, neglect, or exploitation,&rdquo; "
                "alongside <strong>711</strong> for Illinois Relay for deaf and "
                "speech-impaired callers. The department's Engage page, aimed "
                "at explaining the process to someone thinking about calling, "
                "says a report can be made anonymously and that &ldquo;your "
                "name as the reporter is confidential&rdquo; &mdash; it adds "
                "that your identity is not disclosed without your written "
                "permission or a court order.</p>",
                "<p>That same page describes what happens after a report "
                "reaches a local agency: &ldquo;a trained caseworker responds "
                "within a specified time period depending on the severity of "
                "the case,&rdquo; then talks with the older adult about the "
                "risks and what services in the community could lower them "
                "&mdash; naming caregiver support, housing help and training "
                "as examples. The programme page adds that APS is &ldquo;"
                "locally coordinated through 36 provider agencies,&rdquo; with "
                "caseworkers &ldquo;trained and certified by the Illinois "
                "Department on Aging.&rdquo;</p>",
            ]),
            ("What this guide will not state as a fixed rule", [
                "<p>The department's own pages do not give a specific response "
                "time &mdash; only that it varies with how serious the "
                "caseworker judges the situation to be, so this guide will not "
                "invent a number of hours or days. Nor do the pages this guide "
                "read state who, by law, is required to report &mdash; a "
                "<strong>mandated reporter</strong> page exists and is linked "
                "from the department's site, but this guide did not fetch it, "
                "so it will not describe mandated-reporter rules on the "
                "strength of a link alone. And while the Engage page mentions, "
                "in a single success story, that a case was referred to a "
                "State's Attorney, nothing on the pages read states a general "
                "rule for when or whether law enforcement gets involved "
                "&mdash; that single anecdote is not a stated procedure, and "
                "this guide will not present it as one.</p>",
                "<p>If a resident's life or safety is at risk right now, call "
                "911 first. Reporting to APS afterward is still worth doing, "
                "but it is not built to be an emergency response line.</p>",
            ]),
            ("Where this fits with the rest of this site", [
                "<p>Suspecting abuse or neglect at home often surfaces a "
                "harder question underneath it: whether living alone, even "
                "with the concern addressed, is still realistic for your "
                "parent. If the real question is whether the current setting "
                "still fits, the "
                '<a href="/">free six-question assessment</a> on this site '
                "walks through that separately. It asks for no name, no "
                "email and no phone number, and your answers never leave your "
                "device.</p>",
                "<p>If the person who needs support is the one doing the "
                "caring, not the one being cared for, see "
                '<a href="/guides/illinois-family-caregiver-support-program/">Is '
                "there help for the caregiver, not just the parent, in "
                "Illinois?</a></p>",
            ]),
        ],
    },

    {
        "slug": "illinois-nursing-home-resident-rights",
        "bridge": ("Knowing what rights your parent has on paper is a "
               "different question from knowing whether the facility "
               "they are in is still the right level of care for them."),
        "reviewed": "2026-11-04",
        "title": "What Rights Does Your Parent Have in an Illinois Care Facility?",
        "h1": "What rights does your parent have in an Illinois nursing home or care facility?",
        "desc": ("The Illinois Department on Aging publishes a plain-language "
                 "brochure of residents' rights for long-term care facilities "
                 "&mdash; on money, privacy, discharge and grievances. Here is "
                 "what it actually says, read off the document itself."),
        "intent": "informational / advocacy",
        "answer": ("Illinois residents of nursing homes and other long-term "
                   "care facilities keep legal rights that the facility cannot "
                   "override: a say in their own care, privacy, control of "
                   "their own money, a written contract, and protection from "
                   "being discharged except for one of four stated reasons. "
                   "The Illinois Department on Aging sets these out in a "
                   "brochure called <em>Residents&rsquo; Rights for People in "
                   "Long-Term Care Facilities</em>. It is a summary, not the "
                   "full statute &mdash; the brochure itself says to ask your "
                   "ombudsman for the complete list."),
        "sources": srcs("idoa_resident_rights_brochure", "idoa_ombudsman"),
        "body": [
            ("Where this list comes from", [
                "<p>Every nursing home and long-term care facility resident "
                "in Illinois keeps rights the facility cannot take away "
                "simply because they now live there. The Illinois Department "
                "on Aging publishes a brochure, <em>Residents&rsquo; Rights "
                "for People in Long-Term Care Facilities</em>, that sets out "
                "what those rights are in plain language, grouped under "
                "headings such as safety and good care, participating in "
                "your own care, privacy, money management, contract "
                "information, Medicaid and Medicare information, and the "
                "right to stay in the facility. This guide reports what that "
                "document says, heading by heading.</p>",
                "<p>One limit stated plainly on the brochure's own back "
                "page: &ldquo;For a full list of rights, talk to your "
                "ombudsman.&rdquo; This guide will not claim to be the "
                "complete statutory list &mdash; it reports what the "
                "Department on Aging's own summary document says, and no "
                "more.</p>",
            ]),
            ("Safety, dignity and a say in your own care", [
                "<p>The brochure states a resident &ldquo;must not be abused "
                "by anyone &mdash; physically, verbally, mentally, "
                "financially, or sexually.&rdquo; On care itself, the "
                "facility &ldquo;must develop a written care plan that "
                "states all the services it provides&rdquo; and &ldquo;must "
                "make reasonable arrangements to meet your needs and "
                "choices.&rdquo; A resident has the right to choose their "
                "own doctor, to receive information about their medical "
                "condition and treatment in a language they understand, and "
                "to see their medical records within 24 hours of asking. The "
                "brochure also lists the right to make a Durable Power of "
                "Attorney for Health Care, a Living Will, a Declaration for "
                "Mental Health, and a Do Not Resuscitate order.</p>",
                "<p>On privacy, the brochure says medical and personal care "
                "information is private, staff must knock before entering a "
                "resident's room, and the facility may not share information "
                "about a resident without permission. Visits and phone calls "
                "are private unless a doctor has ordered limited visits for "
                "medical reasons, and a married couple has the right to "
                "share a room if one is available.</p>",
            ]),
            ("Money, contracts and what the facility cannot do with either", [
                "<p>A resident has the right to manage their own money, and "
                "the brochure says the facility &ldquo;may not become your "
                "money manager nor your Social Security representative "
                "payee without your permission.&rdquo; A resident may see "
                "their own financial record at any time, and the facility "
                "&ldquo;must give you an itemized statement at least once "
                "every 3 months.&rdquo;</p>",
                "<p>On contracts, a resident must be given a document "
                "stating what services are provided and how much they cost, "
                "and the facility &ldquo;must not require anyone else to "
                "sign an agreement stating they will pay for your bill "
                "unless they are your court appointed guardian.&rdquo; On "
                "Medicaid and Medicare, a resident has the right to apply "
                "for either, the facility must give information on how to "
                "apply &mdash; including for spousal impoverishment "
                "protections &mdash; and, the brochure states, &ldquo;if you "
                "receive Medicaid, the facility cannot make you pay for "
                "anything for which Medicaid pays.&rdquo;</p>",
            ]),
            ("Being asked to leave: the only four reasons, and the right to appeal", [
                "<p>The brochure states a resident has the right to keep "
                "living in their facility, and that it &ldquo;can force you "
                "to leave&rdquo; only because the bill has not been paid, "
                "the resident is dangerous to themselves or others, their "
                "medical needs cannot be met there, or the facility closes. "
                "A written notice is required, and it must state why the "
                "resident is being asked to move, how to appeal, and include "
                "a self-addressed envelope to the Illinois Department of "
                "Public Health. A resident has the right to appeal a "
                "discharge within <strong>10 days</strong>, and the brochure "
                "directs anyone needing help with an involuntary discharge "
                "notice to call the Illinois Department on Aging at "
                "<strong>1-800-252-8966</strong>.</p>",
                "<p>On returning after a hospital stay, the brochure says "
                "that in most cases a Medicaid resident must be allowed to "
                "return to the facility after a hospital stay, even with a "
                "written discharge notice already issued, and that a "
                "facility must hold a bed for a resident hospitalized more "
                "than 10 days once one becomes available. A private-pay "
                "resident, the brochure says, must be told in writing what "
                "they need to do to hold their bed while hospitalized. A "
                "resident also has the right to be told in advance if their "
                "room or roommate is changing.</p>",
            ]),
            ("Rights that do not disappear at the door", [
                "<p>The brochure is explicit that a resident keeps their "
                "rights as a citizen of Illinois and the United States. It "
                "lists the right to vote, to take part in social and "
                "community activities, to participate in the facility's "
                "Resident Council, and to meet with the Long-Term Care "
                "Ombudsman, community organisations, legal advocates and "
                "members of the public who visit. A resident has the right "
                "to present grievances and get a prompt response, and the "
                "brochure states the facility &ldquo;may not threaten or "
                "punish you in any way for asserting your rights or "
                "presenting grievances.&rdquo;</p>",
            ]),
            ("If a right is not being respected", [
                "<p>The brochure's own suggested order is: write down what "
                "happened, with dates, times and who was involved; raise it "
                "with facility staff through the grievance procedure; bring "
                "it to the Resident Council; and contact the Illinois "
                "Long-Term Care Ombudsman Program, which the Department on "
                "Aging describes elsewhere as a free, confidential, "
                "<strong>resident-directed</strong> advocate &mdash; reach it "
                "through the Senior HelpLine at <strong>1-800-252-8966 (711 "
                "TRS)</strong>. The brochure separately names the Central "
                "Complaint Registry, <strong>800-252-4343</strong>, as the "
                "Illinois Department of Public Health's channel for a formal "
                "complaint. A full walk-through of both channels, including "
                "hours and how to file in writing, is in "
                '<a href="/guides/illinois-care-facility-complaint/">How to '
                "report a problem at an Illinois care facility</a>.</p>",
                "<p>One Evanston-specific detail from the brochure's own "
                "contact page: the Ombudsman region covering the city "
                "lists a direct number for <strong>City of Evanston: "
                "1-847-448-8696</strong>, separate from the number listed "
                "for the rest of that region.</p>",
            ]),
            ("Where this fits with the rest of this site", [
                "<p>Rights on paper are a different question from whether a "
                "specific facility is the right setting at all. The "
                '<a href="/">free six-question assessment</a> on this site '
                "walks through that separately, asking for no name, no "
                "email and no phone number, with answers that never leave "
                "your device.</p>",
            ]),
        ],
    },

    {
        "slug": "va-nursing-home-and-respite-care",
        "bridge": ("Knowing that the VA will provide or pay for nursing home and "
               "respite care answers how your veteran parent gets that care. It "
               "does not answer whether a VA pension is still the better way to "
               "pay for assisted living instead."),
        "reviewed": "2026-11-05",
        "title": "VA Nursing Home Care and Respite Care, Explained",
        "h1": "Can the VA provide nursing home care, or give a family caregiver a break?",
        "desc": ("VA.gov describes three nursing home settings a veteran can use "
                 "directly, plus a Respite Care benefit that gives a family "
                 "caregiver a break &mdash; a different path from the Veterans "
                 "Pension. What VA will and will not pay for, in VA.gov's own "
                 "words."),
        "intent": "benefits question",
        "answer": ("<strong>Yes, through VA's own long-term care programme "
                   "&mdash; a different path from the Veterans Pension.</strong> "
                   "VA.gov describes three nursing home settings a veteran can "
                   "use (VA Community Living Centers, VA-contracted Community "
                   "Nursing Homes, and state-run Veterans Homes), plus a Respite "
                   "Care benefit that pays for short-term care so a family "
                   "caregiver can rest. Eligibility turns on enrolment in VA "
                   "health care, clinical need, and &mdash; for nursing home "
                   "care specifically &mdash; service-connected disability "
                   "status and income. VA.gov is explicit about one limit many "
                   "families miss: it does not pay room and board for assisted "
                   "living or an adult family home."),
        "sources": srcs("va_ltc_new", "va_clc", "va_respite", "va_ltc_overview",
                        "idph_vet_homes"),
        "body": [
            ("Three places VA provides nursing home care directly", [
                "<p>Many families assume VA only ever writes a pension cheque. "
                "VA.gov&rsquo;s long-term care page instead describes three "
                "separate nursing home settings a veteran can actually live in, "
                "each arranged differently: a VA-run <strong>Community Living "
                "Center</strong>, &ldquo;designed to feel like home&rdquo;; a "
                "<strong>Community Nursing Home</strong> &mdash; a non-VA "
                "facility that VA contracts with; and a <strong>State Veterans "
                "Home</strong>, which is state-owned and managed.</p>",
                "<p>VA&rsquo;s own page for the first of these is direct about "
                "what it is: &ldquo;A Community Living Center (CLC) is a VA "
                "Nursing Home.&rdquo; It offers nursing-home-level care, "
                "including skilled nursing and help with daily activities, and "
                "the page says CLCs aim to resemble &ldquo;home&rdquo; as much "
                "as possible, with family-friendly visiting, room decorating "
                "and pets allowed.</p>",
                "<p>Eligibility for any of the three runs through the same "
                "gate. VA.gov states that nursing home care is provided "
                "&ldquo;IF you meet certain eligibility criteria involving "
                "your service-connected status, level of disability, and "
                "income,&rdquo; on top of being enrolled in the VA health "
                "system and &ldquo;medically and psychiatrically "
                "stable.&rdquo; Clinical need and whether a bed is actually "
                "available where your parent lives both factor in too "
                "&mdash; none of this is a guarantee of a particular "
                "setting.</p>",
            ]),
            ("Respite care: a break for the family caregiver, not just the veteran", [
                "<p>VA.gov&rsquo;s newer page describes Respite Care simply as "
                "a benefit a veteran &ldquo;may be able to get&rdquo; that "
                "&ldquo;gives your family caregiver a break.&rdquo; Its older "
                "Geriatrics and Extended Care page is more specific about who "
                "it is for: veterans who need help with daily activities, or "
                "whose caregiver is isolated or under strain.</p>",
                "<p>It comes in two forms. <strong>Home Respite Care</strong> "
                "covers &ldquo;a person to come to a Veteran&rsquo;s "
                "home,&rdquo; or the veteran attending an adult day health "
                "care programme instead. <strong>Nursing Home Respite "
                "Care</strong> is a stay &ldquo;in a VA Community Living "
                "Center or a community nursing home,&rdquo; which VA.gov says "
                "&ldquo;should be scheduled in advance.&rdquo;</p>",
                "<p>VA.gov&rsquo;s eligibility rule: &ldquo;All enrolled "
                "Veterans are eligible for Respite Care IF they meet the "
                "clinical criteria for the service and it is "
                "available.&rdquo; Availability varies by location, and if "
                "the respite is delivered by a community agency, adult day "
                "health centre or nursing home rather than VA itself, the "
                "veteran also has to meet separate community care "
                "eligibility rules.</p>",
                "<p>This guide could not find a stated annual day limit for "
                "Respite Care on either VA.gov page it read, so it will not "
                "publish one. Ask your VA social worker or case manager what "
                "is actually available at your parent&rsquo;s facility before "
                "assuming a figure you may have seen elsewhere.</p>",
            ]),
            ("What VA will not pay for: assisted living and adult family homes", [
                "<p>This is the limit that catches families off guard. VA.gov "
                "states it without qualification: &ldquo;The VA does not pay "
                "for room and board in residential settings such as Assisted "
                "Living or Adult Family Homes.&rdquo; Those settings have "
                "their own, separate eligibility rules, and a veteran living "
                "in one may still be able to receive some of VA&rsquo;s home "
                "and community-based services there.</p>",
                "<p>VA.gov adds that it does not run, staff or pay for these "
                "settings, but it does inspect and approve each one it refers "
                "a veteran to, and VA benefits may still help pay for extra "
                "services received there, such as a visit from a VA provider "
                "&mdash; a narrower role than VA plays for a Community Living "
                "Center, where VA is the licensed operator.</p>",
                '<p>This is exactly the gap <a href="/guides/'
                'va-aid-and-attendance-benefit/">Aid and Attendance</a> is '
                "built to fill: a cash pension a family can put toward the "
                '<a href="/guides/assisted-living-cost-illinois/">cost of '
                "assisted living</a> that VA itself will not cover "
                "directly.</p>",
            ]),
            ("Other home and community services VA names", [
                "<p>VA&rsquo;s older long-term care overview lists &ldquo;"
                "Services at Home and in the Community&rdquo; available to "
                "&ldquo;all enrolled Veterans&rdquo; who have a clinical need "
                "and local availability: Geriatric Evaluation, Adult Day "
                "Health Care, Homemaker and Home Health Aide Care, Respite "
                "Care, and Skilled Home Health Care.</p>",
                "<p>Its newer page describes two of these in more detail. "
                "<strong>Adult Day Health Care</strong> is a daytime "
                "programme offering &ldquo;social activities, companionship, "
                "and recreation&rdquo; along with care and support. "
                "<strong>Home-Based Primary Care</strong> sends &ldquo;a VA "
                "healthcare team, led by a VA doctor, who provides "
                "services&rdquo; in the home, such as nursing care and "
                "physical therapy.</p>",
                "<p>Neither VA.gov page this guide read describes what "
                "Homemaker and Home Health Aide Care or Skilled Home Health "
                "Care actually involve beyond their names, so this guide will "
                "not guess. Ask a VA social worker which of these are "
                "available near your parent.</p>",
            ]),
            ("What it costs", [
                "<p>VA.gov&rsquo;s long-term care overview states one date "
                "plainly: &ldquo;Long term care copays are not charged until "
                "the 22nd day of care.&rdquo; After that, a Community Living "
                "Center stay can mean a copay &ldquo;based on your VA "
                "service-connected disability status and financial "
                "information,&rdquo; and a VA social worker or case manager "
                "can tell you the amount.</p>",
                "<p>Hospice care is treated differently wherever it is "
                "delivered: VA.gov states &ldquo;Copays are NOT charged for "
                "Hospice Care provided in any setting.&rdquo; For anything VA "
                "does not cover, its newer page points families toward "
                "Medicaid, Medicare, or their own private insurance.</p>",
                "<p>This guide has not verified how a VA pension interacts "
                "with a Community Living Center copay &mdash; that depends on "
                "income and disability rules only VA can apply to one "
                "person&rsquo;s file, so it will not guess at the result. Ask "
                "the social worker handling the Application for Extended Care "
                "Benefits.</p>",
            ]),
            ("How to apply", [
                "<p>VA.gov&rsquo;s instruction is the same across Community "
                "Living Center care, community nursing home care and Respite "
                "Care: contact your VA social worker or case manager and "
                "complete <strong>VA Form 10-10EC, Application for Extended "
                "Care Benefits</strong>. That is what sets the copay amount, "
                "and the social worker can also help find a facility and make "
                "arrangements.</p>",
            ]),
            ("Illinois also runs its own State Veterans Homes", [
                "<p>The &ldquo;State Veterans Home&rdquo; option on VA&rsquo;s "
                "own list has a local version. The Illinois Department of "
                "Public Health states that the Illinois Department of "
                "Veterans&rsquo; Affairs runs &ldquo;all four Illinois "
                "Veterans&rsquo; Homes,&rdquo; and that &ldquo;each Home is "
                "licensed by IDPH and certified by the US Department of "
                "Veterans Affairs Medical Center of jurisdiction.&rdquo; IDPH "
                "describes the homes as &ldquo;fully staffed by long-term "
                "care professionals and volunteers from veteran service "
                "organizations and the local community,&rdquo; coordinating "
                "with the local health care community for each resident&rsquo;"
                "s health needs.</p>",
                "<p>One protection IDPH names specifically: under Public Act "
                "100-0632, if two or more residents in a home are diagnosed "
                "with an infectious disease within a month or less, the home "
                "must notify residents, their emergency contacts, the "
                "Illinois Department of Veterans&rsquo; Affairs and IDPH "
                "within 24 hours of the second diagnosis, and post a notice "
                "near its main entrance.</p>",
                "<p>This guide could not verify the homes&rsquo; locations, "
                "admission requirements or cost &mdash; the Illinois "
                "Department of Veterans&rsquo; Affairs&rsquo;s own site did "
                "not load while researching this guide, and the IDPH page "
                "does not restate that detail. Contact the Illinois "
                "Department of Veterans&rsquo; Affairs directly before "
                "assuming a location or a figure found elsewhere.</p>",
            ]),
            ("Where this fits with the rest of this site", [
                "<p>This site now covers three separate VA paths, and they "
                "are not interchangeable. "
                '<a href="/guides/va-aid-and-attendance-benefit/">Aid and '
                "Attendance</a> is a cash pension a veteran or surviving "
                "spouse spends on any kind of care, including assisted "
                'living. <a href="/guides/va-veteran-directed-care-program/">'
                "Veteran Directed Care</a> is a budget a veteran controls to "
                "hire their own help at home. This guide is the third: VA "
                "directly providing or paying for nursing home, respite and "
                "other care itself, under its own eligibility rules rather "
                "than a pension calculation.</p>",
                "<p>If the open question in your family is which level of "
                "care your parent actually needs, rather than which VA "
                'programme pays for it, the <a href="/">free six-question '
                "assessment</a> on this site walks through that separately. "
                "It asks for no name, no email and no phone number, and your "
                "answers never leave your device.</p>",
            ]),
        ],
    },

    {
        "slug": "medicare-home-health-care",
        "bridge": ("Qualifying for Medicare&rsquo;s home health benefit turns on a "
               "doctor&rsquo;s definition of &ldquo;skilled&rdquo; and "
               "&ldquo;homebound&rdquo; &mdash; not on whether your parent is safe "
               "to leave alone, which is usually the real question a family is "
               "asking."),
        "reviewed": "2026-11-06",
        "title": "Does Medicare Pay for a Home Health Aide or Nurse at Home?",
        "h1": "Does Medicare pay for a home health aide or nurse at home?",
        "desc": ("Medicare pays $0 for a covered home health visit, but only while a "
                 "doctor-ordered skilled need and homebound status both hold &mdash; "
                 "and a home health aide alone, with no skilled care alongside it, is "
                 "never covered. Here is exactly what qualifies."),
        "intent": "coverage question",
        "answer": ("<strong>Only for skilled care, and only while your parent is "
                   "homebound.</strong> Medicare pays <strong>$0</strong> for a "
                   "covered home health visit from a Medicare-certified agency, but it "
                   "will only start one when a doctor who has examined your parent in "
                   "person orders <em>intermittent, skilled</em> nursing or therapy "
                   "and confirms your parent is homebound. A home health aide for "
                   "bathing, feeding or help walking is covered only alongside that "
                   "skilled care &mdash; Medicare does not pay for an aide, or for "
                   "ongoing personal care, by itself."),
        "sources": srcs("mhha", "mcosts"),
        "body": [
            ("What the home health benefit actually covers", [
                "<p>Medicare.gov describes home health as a defined set of services "
                "delivered at home by a <strong>Medicare-certified home health "
                "agency</strong>, not a general-purpose way to pay for help at home. "
                "What is covered:</p>",
                "<ul class=\"res__list\">"
                "<li><strong>Skilled nursing care</strong> &mdash; &ldquo;medically "
                "necessary part-time or intermittent skilled nursing care,&rdquo; such "
                "as wound care, injections, IV or nutrition therapy, and monitoring an "
                "unstable health condition</li>"
                "<li><strong>Physical, occupational and speech-language therapy</strong> "
                "&mdash; if certain conditions are met</li>"
                "<li><strong>Medical social services</strong></li>"
                "<li><strong>Home health aide services</strong> &mdash; part-time or "
                "intermittent, and <strong>only while you are also receiving</strong> "
                "skilled nursing or therapy. Examples given are bathing, feeding and "
                "help with walking</li>"
                "<li><strong>Injectable osteoporosis drugs</strong> for women who meet "
                "certain criteria</li>"
                "<li><strong>Durable medical equipment and medical supplies</strong> "
                "for use at home</li></ul>",
                "<p>Read that aide line again: it is covered <strong>only while</strong> "
                "skilled nursing, physical therapy, speech-language pathology or "
                "occupational therapy is also happening. The next two sections explain "
                "why that single word decides so much of what follows.</p>",
            ]),
            ("The test that decides it: skilled need and homebound, both at once", [
                "<p>Medicare.gov sets out conditions that all have to hold before a "
                "home health visit is covered:</p>",
                "<ul class=\"res__list\">"
                "<li><strong>A skilled need.</strong> Your parent needs part-time or "
                "intermittent skilled nursing or therapy &mdash; not an ongoing, "
                "open-ended need for help</li>"
                "<li><strong>Homebound status, both parts at once.</strong> Leaving "
                "home is not recommended, or your parent has trouble leaving without "
                "help, because of an illness or injury; <strong>and</strong> your "
                "parent is normally unable to leave home, and leaving takes a "
                "considerable and taxing effort. Medical treatment and short, "
                "infrequent non-medical absences &mdash; the page gives religious "
                "services as an example &mdash; are allowed without losing homebound "
                "status, and so is adult day care</li>"
                "<li><strong>A face-to-face encounter.</strong> &ldquo;A doctor or "
                "other provider (like a nurse practitioner) must see you in person and "
                "confirm you need home health care&rdquo; &mdash; this cannot be done "
                "by chart review alone</li>"
                "<li><strong>A doctor&rsquo;s order</strong>, carried out by a "
                "Medicare-certified home health agency</li></ul>",
                "<p>Occupational therapy has its own rule worth knowing: it &ldquo;must "
                "first be ordered along with nursing, physical therapy, or "
                "speech-language pathology&rdquo; &mdash; but once that has happened, "
                "it &ldquo;can continue on its own&rdquo; even after the service that "
                "started it ends.</p>",
            ]),
            ("What it has never covered, however much the need", [
                "<p>Medicare.gov lists this explicitly as not covered by the home "
                "health benefit:</p>",
                "<ul class=\"res__list\">"
                "<li><strong>24-hour-a-day care</strong> at home</li>"
                "<li><strong>Home meal delivery</strong></li>"
                "<li><strong>Homemaker services</strong> &mdash; shopping, cleaning "
                "&mdash; that are unrelated to the care plan</li>"
                "<li><strong>Custodial or personal care, such as help with bathing or "
                "dressing, when that is the only care needed</strong></li></ul>",
                "<p>That last line is the one families run into. A home health aide is "
                "part of this benefit only as long as skilled nursing or therapy is "
                "also underway. The moment the skilled need ends &mdash; a wound heals, "
                "a therapy goal is met &mdash; the aide visits built around it generally "
                "end too, even if the bathing or dressing help your parent needs has "
                "not gone anywhere. Ongoing, non-medical personal care at home in "
                "Illinois is a different programme with a different eligibility test: "
                'see <a href="/guides/illinois-community-care-program/">Can my parent '
                "get paid help at home in Illinois?</a></p>",
            ]),
            ("What it costs", [
                "<p>Medicare.gov states the cost of the core benefit in five words: "
                "&ldquo;You pay nothing for covered home health services.&rdquo; That "
                "is $0 coinsurance and $0 copayment for a qualifying visit &mdash; not "
                "a reduced rate.</p>",
                "<p>The exception is equipment, not care. For Medicare-covered durable "
                "medical equipment supplied as part of home health, you pay <strong>20% "
                "of the Medicare-approved amount</strong> after you meet the Part B "
                "deductible, which is <strong>" + F["partB_deductible"] +
                "</strong> for 2026.</p>",
                "<p>Before giving you anything outside the covered benefit, the agency "
                "is required to tell you &mdash; verbally and in writing, in advance "
                "&mdash; what Medicare will not pay for, using a notice called an "
                "Advance Beneficiary Notice. Ask for it in writing before agreeing to "
                "anything the agency describes as extra.</p>",
            ]),
            ("How much care, and how often", [
                "<p>If your parent qualifies, Medicare.gov says visits are "
                "<strong>unlimited</strong> &mdash; there is no cap on the number of "
                "home health visits over time, only on the intensity of any single "
                "period of care.</p>",
                "<p>That intensity cap: skilled nursing and home health aide services "
                "combined generally run up to <strong>8 hours a day and 28 hours a "
                "week</strong>. A short-term increase &mdash; under 8 hours a day, up "
                "to 35 hours a week &mdash; is allowed if your parent&rsquo;s provider "
                "decides it is necessary. Both figures explain the line above about "
                "24-hour care: this benefit is built around scheduled, intermittent "
                "visits, not a presence in the home around the clock, at any "
                "funding level.</p>",
            ]),
            ("Where this fits with the rest of this site", [
                "<p>This site now covers three different ways Medicare pays for care, "
                "and they answer three different questions. "
                '<a href="/guides/does-medicare-pay-for-senior-care/">Does Medicare pay '
                "for assisted living or nursing home care?</a> covers a short-term "
                "skilled stay <em>inside a facility</em> after a qualifying hospital "
                "stay. "
                '<a href="/guides/medicare-hospice-benefit-explained/">Does Medicare pay '
                "for hospice care at home?</a> covers comfort care once a doctor "
                "certifies six months or less to live. This guide is the third: skilled "
                "nursing or therapy visits <em>at home</em>, for a parent who is "
                "homebound but not terminally ill and not in a facility.</p>",
                "<p>If what your parent actually needs is ongoing help with bathing, "
                "meals or supervision &mdash; rather than a nurse or therapist &mdash; "
                "none of Medicare&rsquo;s coverage answers that. The "
                '<a href="/">free six-question assessment</a> on this site asks about '
                "that kind of need directly. It asks for no name, no email and no phone "
                "number, and your answers never leave your device.</p>",
            ]),
        ],
    },

    {
        "slug": "va-caregiver-support-program",
        "bridge": ("Qualifying for a VA caregiver stipend is a question about the "
               "family&rsquo;s own finances. It says nothing about whether the care "
               "a parent needs has already moved past what one caregiver, paid or "
               "not, can safely provide alone."),
        "reviewed": "2026-11-07",
        "title": "Can a Family Caregiver Get Paid by the VA to Care for a Veteran at Home?",
        "h1": "Can a family caregiver get paid by the VA to care for a veteran at home?",
        "desc": ("VA.gov describes a programme that pays a monthly stipend to a "
                 "family member who is already caring for a veteran at home. Who "
                 "the veteran and the caregiver each have to be, what a stipend "
                 "comes with, and the separate programme for everyone else, in "
                 "VA.gov&rsquo;s own words."),
        "intent": "benefits question",
        "answer": ("<strong>Sometimes, through the Program of Comprehensive Assistance "
                   "for Family Caregivers (PCAFC)</strong> &mdash; a VA programme that "
                   "pays a monthly stipend directly to a family member who provides a "
                   "veteran&rsquo;s personal care at home. It depends on the "
                   "veteran&rsquo;s disability rating and care need, and on who the "
                   "caregiver is. A family caregiver who does not qualify is not shut "
                   "out entirely: VA.gov describes a second, wider programme with no "
                   "stipend but no relationship or disability-rating test either."),
        "sources": srcs("va_pcafc", "va_pgcss", "va_caregiver_compare",
                        "va_caregiver_benefits", "va_aa"),
        "body": [
            ("Two programmes, and only one of them pays the caregiver", [
                "<p>Families researching VA help with senior care usually find "
                '<a href="/guides/va-aid-and-attendance-benefit/">Aid and Attendance</a> '
                "first &mdash; a cash benefit paid to the veteran. This is a different "
                "benefit, paid to the person doing the caregiving. VA.gov runs two "
                "separate caregiver programmes, and the distinction is the whole point "
                "of this guide: the <strong>Program of Comprehensive Assistance for "
                "Family Caregivers (PCAFC)</strong> is the one with a stipend, and it "
                "has real eligibility gates on both sides &mdash; the veteran and the "
                "caregiver. The <strong>Program of General Caregiver Support Services "
                "(PGCSS)</strong> has none of those gates, and none of the stipend "
                "either. VA.gov states plainly that a family caregiver who does not "
                "qualify for PCAFC &ldquo;may still be able to get support and "
                "resources through the Program of General Caregiver Support Services "
                "(PGCSS).&rdquo;</p>",
            ]),
            ("What the veteran has to qualify as, for PCAFC", [
                "<p>VA.gov lists four requirements for the veteran, and the way it is "
                "written, every one of them has to hold:</p>",
                "<ul class=\"res__list\">"
                "<li>&ldquo;The Veteran has a VA disability rating (individual or "
                "combined) of 70% or higher&rdquo;</li>"
                "<li>&ldquo;The Veteran was discharged from the U.S. military or has a "
                "date of medical discharge&rdquo;</li>"
                "<li>&ldquo;The Veteran needs at least 6 months of continuous, "
                "in-person personal care services&rdquo;</li>"
                "<li>&ldquo;The Veteran needs to be enrolled in VA healthcare&rdquo;"
                "</li></ul>",
                "<p>VA.gov describes that personal care need as covering &ldquo;health "
                "and well-being&rdquo;, help with &ldquo;daily needs like feeding, "
                "bathing, and dressing&rdquo;, and &ldquo;safety, protection, or "
                "instruction&rdquo; in the veteran&rsquo;s own environment &mdash; a "
                "wide definition that reaches well beyond a single disabling injury. "
                "Notably, the page does not name a particular injury, illness or era "
                "of service as a requirement; the gate is the disability rating and the "
                "care need, not what caused either one.</p>",
                "<p>An active-duty service member facing a medical discharge does not "
                "have to wait for separation to start the process: VA.gov says that "
                "person &ldquo;must apply for VA health care before or after applying "
                "for caregiver assistance&rdquo; &mdash; the two applications can run in "
                "either order.</p>",
            ]),
            ("Who can be the paid caregiver", [
                "<p>VA.gov&rsquo;s own requirements for the caregiver are short:</p>",
                "<ul class=\"res__list\">"
                "<li>&ldquo;You must be at least 18 years old.&rdquo;</li>"
                "<li>&ldquo;You&rsquo;re a spouse, son, daughter, parent, stepfamily "
                "member, or extended family member of the Veteran, or&rdquo;</li>"
                "<li>&ldquo;You live full time with the Veteran, or you&rsquo;re "
                "willing to live full time with the Veteran&rdquo;</li></ul>",
                "<p>That second bullet is an &ldquo;or&rdquo;, in VA.gov&rsquo;s own "
                "layout, not an &ldquo;and&rdquo; stacked on top of the family "
                "relationship &mdash; someone willing to move in and provide the care "
                "can qualify as a caregiver even outside the listed family "
                "categories. A veteran can also have more than one approved caregiver "
                "at once: VA.gov&rsquo;s benefits list is written for &ldquo;eligible "
                "primary and secondary family caregivers&rdquo;, and the stipend below "
                "is reserved for the one designated primary.</p>",
            ]),
            ("What a primary caregiver actually receives", [
                "<p>VA.gov splits the benefit list in two. Every approved caregiver, "
                "primary or secondary, can receive:</p>",
                "<ul class=\"res__list\">"
                "<li>&ldquo;Caregiver education and training&rdquo;</li>"
                "<li>&ldquo;Mental health counseling&rdquo;</li>"
                "<li>&ldquo;Certain travel benefits when traveling with the Veteran to "
                "receive care&rdquo;</li></ul>",
                "<p>A <strong>primary</strong> family caregiver &mdash; VA.gov&rsquo;s "
                "wording is &ldquo;eligible primary family caregivers may also receive "
                "these benefits&rdquo; &mdash; can additionally get:</p>",
                "<ul class=\"res__list\">"
                "<li>&ldquo;A monthly stipend (payment).&rdquo;</li>"
                "<li>Access to CHAMPVA health coverage, for a caregiver who lacks other "
                "health coverage</li>"
                "<li>&ldquo;Free legal and financial planning assistance related to the "
                "needs of the injured Veteran.&rdquo;</li>"
                "<li>&ldquo;At least 30 days of respite care per year.&rdquo;</li>"
                "<li>&ldquo;Access to telehealth therapy sessions through&rdquo; the "
                "programme&rsquo;s virtual psychotherapy service for caregivers</li>"
                "</ul>",
                "<p>Primary caregivers must also enrol in direct deposit to actually be "
                "paid, through VA&rsquo;s own customer engagement portal.</p>",
            ]),
            ("A figure this guide will not guess at", [
                "<p>Families will want to know how large the stipend actually is. This "
                "guide read VA.gov&rsquo;s own PCAFC page looking for a dollar figure "
                "or a formula, and found neither &mdash; the page states that the "
                "stipend exists and how it is paid, not how it is calculated or what a "
                "typical amount looks like. Anything quoting a specific dollar figure "
                "for this stipend is not coming from the page this guide could find. "
                "Ask the caregiver support team handling the application what the "
                "assessed amount would actually be.</p>",
            ]),
            ("If PCAFC does not fit: the Program of General Caregiver Support Services", [
                "<p>This is the programme for everyone else, and it is far easier to "
                "qualify for. VA.gov&rsquo;s own conditions: &ldquo;You care for a "
                "Veteran who is enrolled in VA health care&rdquo;, &ldquo;You provide "
                "personal care services to the Veteran&rdquo;, and &ldquo;You want to "
                "connect with other caregivers, get more support from a professional "
                "care team, or grow your skills as a caregiver.&rdquo; There is no "
                "disability-rating threshold, no family-relationship requirement and no "
                "stipend.</p>",
                "<p>What it offers instead, in VA.gov&rsquo;s own list: &ldquo;Peer "
                "support mentoring&rdquo;, &ldquo;Skills training&rdquo;, "
                "&ldquo;Coaching&rdquo;, &ldquo;Telephone support&rdquo;, &ldquo;Online "
                "programs&rdquo;, and &ldquo;Referrals to available resources.&rdquo; "
                "To enrol, VA.gov says to contact the caregiver support team or "
                "coordinator at the nearest VA facility, or ask the veteran&rsquo;s VA "
                "health care team for a referral; the veteran has to agree to be cared "
                "for by that person and be listed with them in their health record.</p>",
            ]),
            ("How to apply for PCAFC", [
                "<p>VA.gov describes one joint process for the veteran and the "
                "caregiver together: &ldquo;You and the Veteran will need to apply "
                "together and participate in an application process&rdquo;, filling "
                "out &ldquo;a joint Application for the Program of Comprehensive "
                "Assistance for Family Caregivers (VA Form 10-10CG)&rdquo;, both signed "
                "and dated. VA.gov lists three ways to submit it: online, by mail to "
                "the 10-10CG Evidence Intake Center, PO Box 5154, Janesville, WI "
                "53547-5154, or in person &mdash; &ldquo;bring your completed VA Form "
                "10-10CG to the caregiver support team at your nearest VA medical "
                "center.&rdquo; VA.gov adds one instruction worth repeating exactly: "
                "&ldquo;Don&rsquo;t send medical records along with your "
                "application.&rdquo;</p>",
                "<p>After that, VA.gov sets its own clock: &ldquo;We&rsquo;ll assign "
                "you as a caregiver no later than 90 days after we get your "
                "application&rdquo;, with a home-care assessment and required training "
                "along the way. Once assigned, wellness check-ins happen &ldquo;at "
                "least once every 120 days, with 1 annual visit to the Veteran&rsquo;s "
                "home.&rdquo; A decision an applicant disagrees with can be appealed: "
                "VA.gov states &ldquo;you have options to appeal or request a review of "
                "the decision.&rdquo;</p>",
                "<p>For either programme, VA.gov lists a national Caregiver Support "
                "Line &mdash; <strong>855-260-3274</strong> &mdash; alongside a "
                "Telecommunications Relay Services number for TTY users, "
                "<strong>711</strong>. This guide could not confirm the line&rsquo;s "
                "hours on a VA.gov page it read, so it leaves them out rather than "
                "repeat a number found only on a facility page.</p>",
            ]),
            ("Where this fits with the rest of this site", [
                "<p>This is a fourth, distinct VA path alongside the three this site "
                "already covers. "
                '<a href="/guides/va-aid-and-attendance-benefit/">Aid and Attendance</a> '
                "pays the veteran or surviving spouse a pension they can spend on any "
                "kind of care. "
                '<a href="/guides/va-veteran-directed-care-program/">Veteran Directed '
                "Care</a> gives the veteran a budget to hire outside help, which can "
                "include a family member, but is not itself a caregiver stipend. "
                '<a href="/guides/va-nursing-home-and-respite-care/">VA nursing home '
                "and respite care</a> is VA providing or paying for care directly. This "
                "programme is the one that pays a family caregiver&rsquo;s own stipend "
                "for care they are already giving. This guide has not verified whether "
                "a veteran parent can draw on more than one of these at the same time "
                "&mdash; VA.gov did not state that plainly on any page this guide read, "
                "so it will not guess. Ask a VA social worker about your specific "
                "situation.</p>",
                "<p>Illinois separately runs its own caregiver support programme, open "
                "to any family caregiver regardless of whether the person they care for "
                "is a veteran &mdash; see "
                '<a href="/guides/illinois-family-caregiver-support-program/">Is there '
                "help for the caregiver, not just the parent, in Illinois?</a> The two "
                "are not the same programme and this guide has not checked whether a "
                "household can use both.</p>",
                "<p>If the open question in your family is whether a parent&rsquo;s "
                "care needs have already moved past what one caregiver can provide at "
                'home, rather than how to fund the caregiver, the <a href="/">free '
                "six-question assessment</a> on this site walks through that "
                "separately. It asks for no name, no email and no phone number, and "
                "your answers never leave your device.</p>",
            ]),
        ],
    },

    {
        "slug": "illinois-pace-program",
        "bridge": ("PACE is worth understanding even where it does not yet reach, "
               "because the question it answers &mdash; can my parent get full "
               "medical and personal care without leaving home &mdash; is the "
               "same question every setting on this site is trying to answer."),
        "reviewed": "2026-11-08",
        "title": "What Is PACE, and Can a Parent in Evanston Use It?",
        "h1": "What is PACE, and can a parent in Evanston use it?",
        "desc": ("PACE pays for full medical and personal care so an older adult "
                 "can stay out of a nursing home, but Illinois only runs it in "
                 "five regions so far. What the state's own page says, and "
                 "whether Evanston is one of them."),
        "intent": "benefits availability question",
        "answer": ("<strong>Not yet, if the question is Evanston specifically.</strong> "
                   "PACE &mdash; the <strong>Program of All-Inclusive Care for the "
                   "Elderly</strong> &mdash; is a joint Medicare and Medicaid programme "
                   "that pays for full medical care, prescription drugs, adult day "
                   "service and more so that an older adult who would otherwise need a "
                   "nursing home can stay in the community. Illinois HFS runs it in five "
                   "regions, and its own zip-code tool for finding a local PACE "
                   "organisation does not list any of Evanston's residential zip codes "
                   "(60201, 60202, 60203, 60208) as of this review. The programme is "
                   "still rolling out, so this guide shows where it operates today and "
                   "how to check again yourself."),
        "sources": srcs("hfs_pace", "hfs_pace_zip", "hfs_pace_orgs", "mpace"),
        "body": [
            ("What PACE actually is", [
                "<p>Illinois HFS describes PACE as &ldquo;comprehensive health "
                "services for seniors living in the community&rdquo; who &ldquo;would "
                "otherwise qualify to live in a nursing facility.&rdquo; Medicare.gov "
                "sets out four conditions a person has to meet: be <strong>at least "
                "55</strong>; live in the service area of a PACE organisation, since "
                "PACE is only available in some states that offer it under Medicaid, "
                "and then only in the specific local areas a PACE organisation actually "
                "covers; need a <strong>nursing-home level of care</strong>, which the "
                "state certifies; and be able to <strong>live safely in the "
                "community</strong> with PACE's help.</p>",
                "<p>Each PACE organisation runs a physical centre &mdash; HFS describes "
                "a primary care clinic together with space for recreation, therapy, "
                "socialising, personal care and dining &mdash; and is responsible for "
                "coordinating a participant's care everywhere it happens: at that "
                "centre, at home, or in a hospital or long-term care admission when one "
                "is needed. That round-the-clock coordination, not any single service on "
                "the list, is what makes PACE different from the home-care and "
                "day-service programmes this site already covers.</p>",
            ]),
            ("What it covers, and what it costs", [
                "<p>Medicare.gov says PACE covers all Medicare- and Medicaid-covered "
                "care, plus anything else a participant's own PACE care team decides "
                "they need. The page names prescription drugs, adult day care with "
                "meals and recreational therapy, and transportation to the PACE centre "
                "and to medical appointments among the services included.</p>",
                "<p>Cost depends on what the participant already has. With Medicaid, "
                "there is <strong>no monthly premium</strong> for the long-term-care "
                "part of the benefit. With Medicare but no Medicaid, cost depends on "
                "whether the person has Part A and/or Part B, and includes a premium "
                "for the long-term-care portion plus a separate Part D drug premium. "
                "With neither, a person can pay the PACE organisation's premium "
                "directly. Whichever of those applies, Medicare.gov states that "
                "<strong>no participant pays a deductible, copayment or coinsurance</strong> "
                "for any drug, service or care their PACE team approves.</p>",
                "<p>One trade-off worth knowing before applying: PACE replaces other "
                "Medicare drug coverage rather than sitting alongside it. Medicare.gov "
                "says that enrolling in a separate Medicare drug plan while in PACE gets "
                "a participant disenrolled from PACE &mdash; the two cannot run "
                "together.</p>",
            ]),
            ("Where PACE operates in Illinois today", [
                "<p>HFS names five Illinois regions: <strong>West Chicago, South "
                "Chicago, Southern Cook County, Peoria and East St. Louis</strong>. Its "
                "own page says PACE services &ldquo;began becoming available in some "
                "regions beginning mid-2024&rdquo; &mdash; this is a recent, rolling "
                "launch, not a programme that has covered the whole state for years.</p>",
                "<p>HFS's designated-organisations page names who runs each region: "
                "Kinship PACE of Illinois, LLC and Lawndale Christian Health Center for "
                "West Side Chicago; Habitat Health at Annie's Place and Esperanza "
                "Health Centers for South Side Chicago; BoldAge PACE Illinois for "
                "Southern Cook County; OSF HealthCare System for Peoria; and Habitat "
                "Health at Stella's Place for East St. Louis. The page gives no launch "
                "date for any of them, and describes Kinship specifically as &ldquo;a "
                "new entrant into the Illinois health care delivery system&rdquo; "
                "&mdash; so a family calling any of these should ask directly whether it "
                "is actually taking participants yet, rather than assume active service "
                "from being named on the list.</p>",
                "<p>HFS's own zip-code search is how the state tells a family whether "
                "PACE reaches them, and the tool itself warns up front that PACE "
                "&ldquo;may not be available in your area.&rdquo; This guide checked it "
                "directly: none of Evanston's residential zip codes &mdash; 60201, "
                "60202, 60203 and 60208 &mdash; appear on that list. Southern Cook "
                "County is the nearest named region, but its zip-code listing does not "
                "reach Evanston.</p>",
            ]),
            ("A figure this guide will not guess at", [
                "<p>Families will want to know what the Medicare-only premium actually "
                "costs. Medicare.gov states plainly that it depends on whether a person "
                "has Part A and/or Part B, and that a separate Part D premium applies "
                "too &mdash; but the page gives no dollar figure or formula for either "
                "one, anywhere this guide could find. A premium that varies by "
                "organisation and by an individual's own Medicare status is not a "
                "number this guide can publish responsibly, so it will not estimate "
                "one. The page is also silent on what happens to a separate Medigap "
                "policy if someone joins PACE. Ask the specific PACE organisation "
                "covering your area, before assuming a cost in either direction.</p>",
            ]),
            ("If PACE is not reachable from Evanston yet", [
                "<p>Because the zip-code tool above is literally how the state keeps "
                "this current, and the programme is explicitly still expanding region "
                "by region, it is worth re-checking that page yourself every so often "
                "rather than treating today's answer as permanent &mdash; a page "
                "written this month can be out of date by next year in a way a static "
                "fact rarely is.</p>",
                "<p>In the meantime, two Illinois programmes already reach Evanston. "
                "For paid help at home &mdash; homemaker service, adult day service, "
                "emergency response &mdash; see "
                '<a href="/guides/illinois-community-care-program/">Can my parent get '
                "paid help at home in Illinois?</a> For Medicaid-funded care in an "
                "assisted-living-style setting, which is not limited to PACE's five "
                "regions, see "
                '<a href="/guides/illinois-supportive-living-program/">Illinois '
                "Supportive Living Program, explained</a>. Neither one coordinates care "
                "as tightly as PACE is designed to, but both are available to an "
                "Evanston family now rather than on a future expansion.</p>",
                "<p>If the open question in your family is which of these settings "
                'actually fits your parent, the <a href="/">free six-question '
                "assessment</a> on this site walks through that separately. It asks "
                "for no name, no email and no phone number, and your answers never "
                "leave your device.</p>",
            ]),
        ],
    },

    {
        "slug": "illinois-home-caregiver-background-check",
        "bridge": ("Confirming someone is legally allowed to do this work is a "
               "different question from knowing whether paid help at home is the "
               "right level of care for your parent in the first place."),
        "reviewed": "2026-11-09",
        "title": "Is It Safe to Hire a Caregiver Directly for Your Parent in Illinois?",
        "h1": "Is it safe to hire a caregiver directly for your parent in Illinois?",
        "desc": ("Going through a licensed Illinois home care agency and hiring "
                 "someone directly are not the same arrangement. One runs a "
                 "background check for you. The other, the state says, is on you "
                 "&mdash; and names the free tool that does it."),
        "intent": "how-to / safety",
        "answer": ("<strong>It can be, but Illinois puts the work on you if you skip "
                   "an agency.</strong> The Illinois Department on Aging draws the "
                   "line plainly: an agency-employed caregiver has their background "
                   "check, training and supervision handled by the agency, while a "
                   "family that hires someone directly is told to "
                   "&ldquo;check the IDPH Healthcare Worker Registry before "
                   "hiring.&rdquo; That registry records background-check status and "
                   "any administrative finding of abuse, neglect or misappropriation "
                   "of property against a direct-care worker &mdash; it is free, and "
                   "it is the one check this guide found Illinois actually telling "
                   "families to make themselves."),
        "sources": srcs("idoa_inhome", "dph_hcwr", "dph_home_services_faq"),
        "body": [
            ("Two ways to bring a caregiver into the house", [
                "<p>The Illinois Department on Aging's own page on in-home care "
                "splits this into two arrangements, and the difference is who is "
                "responsible for vetting the person who will be alone with your "
                "parent. For an <strong>agency-employed caregiver</strong>, the page "
                "states plainly: &ldquo;the agency handles background checks, "
                "training, and supervision.&rdquo; For a <strong>directly hired "
                "caregiver</strong> &mdash; someone a family finds and pays without "
                "going through an agency &mdash; the same page's instruction is just "
                "as plain: &ldquo;check the IDPH Healthcare Worker Registry before "
                "hiring.&rdquo;</p>",
                "<p>Neither arrangement is wrong. But only one of them comes with the "
                "check already done for you.</p>",
            ]),
            ("What a licensed Illinois home care agency actually is", [
                "<p>The Department on Aging's page describes three kinds of agency "
                "the Illinois Department of Public Health (IDPH) licenses, and they "
                "are not interchangeable. A <strong>Home Services Agency</strong> "
                "provides non-medical personal care and is paid for out of pocket, "
                "for a client of any age. A <strong>Home Nursing Agency</strong> "
                "provides skilled nursing as prescribed. A <strong>Home Health "
                "Agency</strong> provides skilled nursing plus physical, occupational "
                "and speech therapy, and Medicare, Medicaid or private insurance may "
                "cover it. IDPH's own licensing FAQ for Home Services Agencies "
                "confirms the licence sits under &ldquo;Home Health, Home Services, "
                "and Home Nursing Agency Code, 77 Ill. Adm. Code 245.&rdquo;</p>",
                "<p>This is a separate question from the "
                '<a href="/guides/illinois-community-care-program/">Community Care '
                "Program</a>, which pays an agency to deliver in-home service to an "
                "eligible older adult at no out-of-pocket cost. This guide is about "
                "a family arranging and paying for care itself, inside or outside "
                "that programme.</p>",
            ]),
            ("If you hire directly, the state puts the check on you", [
                "<p>IDPH describes the Health Care Worker Registry as a list of "
                "&ldquo;individuals with a background check conducted pursuant to "
                "the Health Care Worker Background Check Act,&rdquo; 225 ILCS 46. "
                "The registry shows background-check status, training information "
                "for certified nursing assistants and other health care workers, and "
                "&mdash; in IDPH's own words &mdash; &ldquo;displays administrative "
                "findings of abuse, neglect or misappropriations of property.&rdquo;</p>",
                "<p>The Act reaches the specific roles a family is most likely to be "
                "hiring for directly: IDPH names &ldquo;home health care aides, "
                "nurse aides, personal care assistants, private duty nurse "
                "aides,&rdquo; alongside similar direct-care roles and employees of "
                "licensed long-term care facilities who have contact with residents. "
                "Someone with a disqualifying conviction &ldquo;is prohibited from "
                "working in any of the above positions unless a waiver has been "
                "granted&rdquo; by IDPH, and the department states that an employer "
                "&ldquo;must verify registry status of an individual applying for "
                "the above positions&rdquo; before employment. The Department on "
                "Aging's own page extends that same check to a family hiring "
                "directly, not only to a formal employer.</p>",
                "<p>IDPH names the registry's public search as the way to do this, "
                "reachable through the &ldquo;Search the Health Care Worker "
                "Registry&rdquo; link on its own registry page.</p>",
            ]),
            ("What this guide could not verify, and will not guess at", [
                "<p>The IDPH page this guide read describes what the registry "
                "contains, but it does not define what a &ldquo;work eligible&rdquo; "
                "or &ldquo;not work eligible&rdquo; result actually means, and it "
                "does not walk through what information the search tool asks for. "
                "This guide did not open the search tool itself, so it will not "
                "describe its screens or guess at how to read a result. Read "
                "whatever the tool shows you literally, and call IDPH if a result is "
                "unclear rather than assuming what it means.</p>",
                "<p>This guide also could not find a current public list of licensed "
                "Illinois home care agencies to check a company itself against, "
                "separate from checking an individual worker. Ask an agency for its "
                "licence information directly, or confirm it with IDPH, rather than "
                "assuming a name or a listing found elsewhere is current.</p>",
            ]),
            ("If something goes wrong after you have hired someone", [
                "<p>A concern about a licensed Home Services, Home Nursing or Home "
                "Health agency goes to IDPH. A concern about abuse, neglect or "
                "exploitation of a parent living at home &mdash; whether the "
                "caregiver came from an agency or was hired directly &mdash; is a "
                "different channel, covered in full in "
                '<a href="/guides/illinois-elder-abuse-reporting/">What to do about '
                "suspected elder abuse or neglect at home in Illinois</a>. This guide "
                "is about the check you can make before any of that becomes "
                "necessary, not about what to do once it already has.</p>",
            ]),
            ("Where this fits with the rest of this site", [
                "<p>Checking a caregiver is a narrower question than choosing how "
                "your parent gets help at home in the first place. For the "
                "state-funded route and who qualifies for it, see "
                '<a href="/guides/illinois-community-care-program/">Can my parent '
                "get paid help at home in Illinois?</a> If the honest answer is that "
                "staying at home no longer covers what your parent needs, "
                '<a href="/guides/levels-of-senior-care-explained/">Assisted living, '
                "memory care, skilled nursing and rehabilitation &mdash; what is the "
                "difference?</a> sets out the alternatives.</p>",
                "<p>If you are not sure which of those describes your parent, the "
                '<a href="/">free six-question assessment</a> on this site walks '
                "through the specifics and shows the reasoning behind its answer. It "
                "asks for no name, no email and no phone number to see your results."
                "</p>",
            ]),
        ],
    },

    {
        "slug": "illinois-money-management-program",
        "bridge": ("Knowing a volunteer bookkeeper exists is a different question "
               "from knowing whether your parent can still manage living at home "
               "at all."),
        "reviewed": "2026-11-10",
        "title": "Who Can Help My Parent Pay Bills and Manage Money in Illinois?",
        "h1": "Who can help my parent pay bills and manage money in Illinois?",
        "desc": ("Illinois trains volunteers to budget, pay bills and even act as "
                 "a Social Security representative payee for an older adult who "
                 "can no longer manage money alone &mdash; but only through two "
                 "narrow eligibility paths, and only where a local Program Site "
                 "actually reaches. Here is what the state's own page says, and "
                 "what its own site list leaves out."),
        "intent": "benefits question",
        "answer": ("<strong>Yes, through a specific state programme</strong> "
                   "&mdash; but only for two groups: a parent already approved "
                   "for the Community Care Program, or one with a "
                   "<strong>substantiated Adult Protective Services case</strong>, "
                   "and only in the parts of Illinois a local Program Site "
                   "actually covers. The Illinois Department on Aging's "
                   "Volunteer Money Management Program trains, matches and "
                   "monitors volunteers who budget, pay bills, and can be named "
                   "a parent's <strong>Social Security representative "
                   "payee</strong>. Its own current site list does not show a "
                   "Program Site reaching Evanston Township &mdash; call the "
                   "Senior HelpLine to check before assuming it is out of "
                   "reach."),
        "sources": srcs("idoa_money_mgmt", "idoa_money_mgmt_sites"),
        "body": [
            ("What the Volunteer Money Management Program actually does", [
                "<p>The Illinois Department on Aging describes its Volunteer "
                "Money Management Program as &ldquo;a protective service that "
                "assists low-income older persons who have difficulty managing "
                "their personal household budgets, paying bills&rdquo;. Its own "
                "page lists what that covers in practice: &ldquo;keeping track "
                "of banking records, intervening with creditors, completing "
                "medical forms&rdquo;, &ldquo;setting up a budget, writing "
                "checks, balancing a checkbook&rdquo;, and &ldquo;assisting with "
                "large purchases&rdquo;.</p>",
                "<p>This sits below <a href=\"/guides/"
                "illinois-advance-directive-power-of-attorney/\">a Power of "
                "Attorney</a> and short of a court guardianship. Nobody signs "
                "away legal authority to make this work &mdash; a trained "
                "volunteer simply does the paperwork your parent can no longer "
                "keep up with, under a programme the state recruits, trains and "
                "monitors.</p>",
            ]),
            ("Who qualifies &mdash; and where", [
                "<p>The department's page gives exactly two eligibility paths. "
                "The programme is &ldquo;available to Community Care Program "
                "(CCP) participants&rdquo; &mdash; see "
                '<a href="/guides/illinois-community-care-program/">Can my '
                "parent get paid help at home in Illinois?</a> for what CCP "
                "itself requires &mdash; or to &ldquo;individuals who have a "
                "substantiated Adult Protective Services (APS) case in certain "
                "areas of the State&rdquo;. For what counts as a substantiated "
                "APS case, see "
                '<a href="/guides/illinois-elder-abuse-reporting/">What to do '
                "about suspected elder abuse or neglect at home in "
                "Illinois</a>.</p>",
                "<p>Both paths carry the same catch: &ldquo;in certain areas of "
                "the State&rdquo; is doing real work in that sentence. This is "
                "not a programme every Illinois county runs &mdash; it operates "
                "through a fixed list of contracted Program Sites, and whether "
                "one serves your parent's township decides whether any of this "
                "is actually available to them.</p>",
            ]),
            ("Volunteers, training, and acting as a Social Security "
             "representative payee", [
                "<p>The department's page states that &ldquo;Local Program "
                "Sites, contracted by the Illinois Department on Aging, "
                "recruit, select, train, match and monitor the "
                "volunteers&rdquo;, and that the department itself "
                "&ldquo;administers the program and monitors the local Program "
                "Sites&rdquo;. Volunteers are matched to an older adult who "
                "needs help &ldquo;organizing, reviewing, and paying "
                "bills&rdquo;.</p>",
                "<p>One sentence on the page matters more than the rest for a "
                "family wondering how a parent's Social Security or other "
                "federal benefit cheque gets managed: &ldquo;Volunteers also "
                "serve as Representative Payees, persons designated by the "
                "Social Security Administration to manage the monthly benefits "
                "of certain beneficiaries.&rdquo; That is the same role the "
                "Illinois Department on Aging's own resident-rights brochure "
                "warns a care facility may not take on &ldquo;without your "
                "permission&rdquo; &mdash; this programme is a vetted, "
                "state-monitored way to fill that role with someone other than "
                "the facility, a stranger, or nobody at all.</p>",
            ]),
            ("What this guide could not verify, and will not guess at", [
                "<p>The department's page does not state what the programme "
                "costs a family, does not describe how a volunteer is screened "
                "beyond being &ldquo;trained&rdquo;, and does not explain what "
                "happens if a volunteer mishandles money beyond saying the "
                "department &ldquo;monitors&rdquo; Program Sites. This guide "
                "will not guess at a fee, a background-check standard, or a "
                "complaint process the page itself does not spell out. Ask the "
                "Program Site named for your area, or the Senior HelpLine, "
                "directly.</p>",
            ]),
            ("Is a Program Site actually near Evanston?", [
                "<p>The department publishes the current roster as a PDF, "
                "&ldquo;Find Your Local Program Site/Agency&rdquo;, organised "
                "by the state's Planning and Service Areas. The copy this "
                "guide read, dated 22 October 2026, lists two Program Sites "
                "covering parts of Chicago's suburbs: Kenneth W. Young Centers "
                "for Elk Grove and Schaumburg Townships, and Oak Park Township "
                "Senior Services for Oak Park and River Forest Townships. "
                "Neither covers Evanston Township, and this guide found no "
                "separate listing for the City of Chicago or the rest of Cook "
                "County on that document.</p>",
                "<p>That is a fact about one dated PDF, not a permanent answer. "
                "Program Site lists change, and the department's Service "
                "Locator tool &mdash; built for Care Coordination Units rather "
                "than this programme specifically &mdash; may turn up a more "
                "current answer than this guide's single reading of one "
                "document. Call the Senior HelpLine at <strong>1-800-252-8966 "
                "(711 TRS)</strong> and ask directly whether a Program Site "
                "currently serves Evanston Township, rather than relying on "
                "either this guide or an out-of-date list found elsewhere.</p>",
            ]),
            ("How to find out, for your specific parent", [
                "<p>Start with the Senior HelpLine at <strong>1-800-252-8966 "
                "(711 TRS)</strong>, or a local Care Coordination Unit found "
                "through the department's online Service Locator. Either can "
                "tell you whether your parent's situation &mdash; already on "
                "CCP, or with a substantiated APS case &mdash; qualifies, and "
                "whether a Program Site actually reaches where your parent "
                "lives, before you assume either answer yourself.</p>",
            ]),
            ("Where this fits with the rest of this site", [
                "<p>This is a narrow tool for a narrow problem: bills going "
                "unpaid or a benefit cheque with nobody to manage it, while "
                "your parent still lives independently. If the honest picture "
                "is bigger than that &mdash; your parent can no longer manage "
                "daily life safely on their own &mdash; see "
                '<a href="/guides/levels-of-senior-care-explained/">Assisted '
                "living, memory care, skilled nursing and rehabilitation "
                "&mdash; what is the difference?</a> And if the real question "
                "is who should be allowed to make decisions at all, rather "
                "than who can help with this month's bills, see "
                '<a href="/guides/illinois-advance-directive-power-of-attorney/">'
                "Does my parent need a power of attorney for health care in "
                "Illinois?</a></p>",
                "<p>If you are not sure which of those describes your parent, "
                'the <a href="/">free six-question assessment</a> on this site '
                "walks through the specifics. It asks for no name, no email and "
                "no phone number to see your results, and your answers never "
                "leave your device.</p>",
            ]),
        ],
    },

    {
        "slug": "illinois-home-care-ombudsman-program",
        "bridge": ("Knowing who to call when a paid home-care plan is going wrong "
               "is a different question from knowing whether your parent should "
               "still be living at home at all."),
        "reviewed": "2026-11-11",
        "title": "Illinois Home Care Ombudsman Program: Free Help When In-Home Care Isn't Working",
        "h1": "What to do when your parent's in-home care isn't working in Illinois",
        "desc": ("Illinois runs a free advocate for people getting paid help at home "
                 "through Medicaid, not just people living in a facility. Who it "
                 "serves, what it can do, and how to reach it."),
        "intent": "how-to / advocacy",
        "answer": ("If your parent gets home care through an Illinois Medicaid "
                   "managed care plan (a D-SNP) or one of four Home and Community "
                   "Based Services waivers &mdash; Persons who are Elderly, Persons "
                   "with Disabilities, Persons with Brain Injury, or Persons with "
                   "HIV or AIDS &mdash; the Illinois Department on Aging's "
                   "<strong>Home Care Ombudsman Program</strong> is a free, "
                   "confidential advocate for exactly this situation: a denial or "
                   "termination letter, an unresponsive care coordinator, or a "
                   "service that is not being delivered as promised. Call the "
                   "Senior HelpLine at <strong>1-800-252-8966 (711 TRS)</strong>, "
                   "press 4 for &ldquo;other services,&rdquo; and ask for a Home "
                   "Care Ombudsman."),
        "sources": srcs("idoa_hco", "idoa_ombudsman"),
        "body": [
            ("An ombudsman for people who never left home", [
                "<p>Most families who search for an Illinois &ldquo;ombudsman&rdquo; "
                "find the Long-Term Care Ombudsman Program, which advocates for "
                "residents of nursing homes and other care facilities &mdash; "
                "covered in "
                '<a href="/guides/illinois-care-facility-complaint/">How to report '
                "a problem at an Illinois care facility</a>. Fewer families know "
                "there is a separate, parallel program for people who get paid "
                "care at home instead: the Illinois Department on Aging's "
                "<strong>Home Care Ombudsman Program</strong>. The department's "
                "page on it states that the Illinois Act on Aging was amended in "
                "2013 to authorize &ldquo;advocacy services outside of the "
                "long-term care setting,&rdquo; and that the program began "
                "providing that advocacy and assistance in 2014.</p>",
            ]),
            ("Who it actually serves", [
                "<p>This program is not for every family paying for help at home "
                "&mdash; its page describes two specific routes in. The first is "
                "anyone enrolled in a <strong>Dual Eligible Special Needs Plan "
                "(D-SNP)</strong> and receiving services through a managed care "
                "organisation. The second is anyone receiving services through "
                "one of four Illinois Home and Community Based Services (HCBS) "
                "Waiver Programs: <strong>Persons who are Elderly</strong>, "
                "<strong>Persons with Disabilities</strong>, <strong>Persons with "
                "Brain Injury</strong>, or <strong>Persons with HIV or AIDS</strong>. "
                "If your parent's home care is arranged through one of those "
                "routes, this program is built for exactly their situation.</p>",
            ]),
            ("What it can actually do for you", [
                "<p>The department describes home care ombudsmen as people who "
                "answer questions about services, help when a family has received "
                "a letter denying or terminating in-home services, and step in "
                "when a care coordinator cannot be reached. Where a provider has "
                "violated a person's rights, the program states it will "
                "&ldquo;assist in filing a grievance&rdquo; and &ldquo;work to "
                "resolve complaints.&rdquo; That makes it a place to start before "
                "a problem has become a crisis &mdash; a missed visit, a "
                "confusing notice, or a care plan that no longer matches what "
                "your parent actually needs.</p>",
            ]),
            ("How to reach one", [
                "<p>Call the Illinois Department on Aging's Senior HelpLine at "
                "<strong>1-800-252-8966</strong> (711 TRS), press 4 for &ldquo;other "
                "services,&rdquo; and ask for a Home Care Ombudsman. The "
                "department's page also lists a direct email, "
                "<strong>Aging.HCOProgram@illinois.gov</strong>, for the program "
                "itself.</p>",
            ]),
            ("What this program is not", [
                "<p>Three limits are worth knowing before you call. It is built "
                "around the two eligibility routes above &mdash; a caregiver you "
                "found and pay directly, outside Medicaid or a waiver, is a "
                "different situation, covered in "
                '<a href="/guides/illinois-home-caregiver-background-check/">Is it '
                "safe to hire a caregiver directly in Illinois?</a> It advocates "
                "and helps resolve a problem; it does not replace an emergency "
                "response &mdash; if your parent is in immediate danger, call "
                "911 first. And it is a different program, with a different "
                "phone script, from the Long-Term Care Ombudsman Program that "
                "covers facility residents, so naming the right one when you "
                "call the Senior HelpLine gets you to the right advocate "
                "faster.</p>",
            ]),
            ("Where this fits with the rest of this site", [
                "<p>An unresponsive care coordinator is a service problem. It is "
                "worth asking, separately, whether the underlying level of care "
                "is still the right one &mdash; see "
                '<a href="/guides/illinois-community-care-program/">Can my parent '
                "get paid help at home in Illinois?</a> for how that paid help is "
                "arranged in the first place, or take the "
                '<a href="/">free six-question assessment</a> on this site, which '
                "asks for no name, no email and no phone number, and keeps your "
                "answers on your device.</p>",
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
      <a href="/#paying-nav">Paying for care</a>
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
      <a href="/#paying-nav">Paying for care</a>
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


# --------------------------------------------------------------------------
# PAYMENT NAVIGATOR LINE (Workflow #5) — which guides carry it.
#
# One quiet sentence under "Related guides", only on guides whose subject is
# paying for care. It is a link, never a second button: the assessment keeps
# the page's only button, its bridge after section one, and its block at the
# end. Guides about choosing or checking a community, about independent
# living (which has its own two-way fork), and about caregiver support say
# nothing about it; a reader there did not ask how to pay.
#
# The query string carries one fixed token so the index page can count the
# pathway (/t/guide-choice-pay.txt) apart from the two existing ones. It is
# not personal and nothing is rendered differently because of it.
# --------------------------------------------------------------------------
PAY_NAV_GUIDES = [
    "assisted-living-cost-illinois",
    "does-medicare-pay-for-senior-care",
    "illinois-senior-health-insurance-program",
    "illinois-supportive-living-program",
    "illinois-medicaid-long-term-care",
    "illinois-medicaid-estate-recovery",
    "va-aid-and-attendance-benefit",
    "va-veteran-directed-care-program",
    "va-nursing-home-and-respite-care",
    "illinois-medicare-savings-program",
]
PAY_NAV_HREF = "/?pay=guide#paying-nav"


def pay_nav_line(g):
    if g["slug"] not in PAY_NAV_GUIDES:
        return ""
    return ('<p class="related__pay">Comparing ways to pay? '
            '<a href="%s">The payment navigator</a> puts Medicare, Illinois '
            'Medicaid, VA benefits, long-term-care insurance and private payment '
            'in order for a given type of care &mdash; three questions, nothing '
            'decided, nothing collected.</p>\n' % PAY_NAV_HREF)


def related(g):
    others = [x for x in GUIDES if x["slug"] != g["slug"]][:3]
    items = "".join(
        '<li><a href="/guides/%s/">%s</a></li>' % (o["slug"], o["h1"].replace("&mdash;", "—"))
        for o in others)
    return ('<section class="res__block">\n'
            '<h2 class="res__h">Related guides</h2>\n'
            '<ul class="res__list">%s</ul>\n%s</section>' % (items, pay_nav_line(g)))


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
    "va-veteran-directed-care-program": (
        "Veterans' benefits",
        "Can a veteran get paid in-home care through the VA?",
        "A consumer-directed VA budget that can hire a family member or "
        "neighbour, not a pension cheque — who qualifies and how to "
        "start."),
    "illinois-family-caregiver-support-program": (
        "Staying at home",
        "Is there help for the caregiver, not just the parent?",
        "Illinois funds respite, counselling and training for the person "
        "doing the caring, delivered through a local Caregiver Resource "
        "Center — what it covers, and what it does not say."),
    "illinois-senior-health-insurance-program": (
        "Medicare",
        "Free help choosing a Medicare plan in Illinois",
        "SHIP is a free, unbiased state counselling service for Medicare "
        "beneficiaries — what counsellors actually do, and how to reach "
        "one."),
    "illinois-medicare-savings-program": (
        "Paying with Medicaid",
        "Can Illinois help pay my parent's Medicare premium?",
        "QMB, SLMB and QI are three Medicaid-run tiers that pay part or "
        "all of a Medicare premium — what each covers, the state's dated "
        "2026 limits, and the older figures this guide would not use."),
    "illinois-advance-directive-power-of-attorney": (
        "Legal and planning",
        "Does my parent need a power of attorney for health care?",
        "Illinois does not require one, but without it the state still "
        "names a decision-maker in a fixed order you do not get to "
        "choose — what each of Illinois's four advance directives does."),
    "illinois-benefit-access-program": (
        "Costs",
        "Free transit and a cheaper license plate for seniors",
        "A state programme gives income-eligible seniors free public "
        "transit rides and a discounted vehicle registration — the "
        "income limits and how to apply, read off the Department on "
        "Aging's own page."),
    "illinois-home-delivered-meals": (
        "Staying at home",
        "Can my parent get home-delivered meals in Illinois?",
        "A state-funded nutrition programme delivers meals to older "
        "adults who cannot easily cook or shop for themselves — what "
        "it covers, and who to call."),
    "illinois-elder-abuse-reporting": (
        "Staying at home",
        "What to do about suspected elder abuse at home",
        "A statewide Adult Protective Services hotline covers abuse, "
        "neglect, exploitation and self-neglect of an older adult living "
        "at home — a different line from the one for a care facility."),
    "illinois-nursing-home-resident-rights": (
        "Checking a community",
        "What rights does your parent have in a care facility?",
        "The Illinois Department on Aging's own brochure, read in full: "
        "money, privacy, discharge and grievance rights a facility "
        "cannot override."),
    "va-nursing-home-and-respite-care": (
        "Veterans' benefits",
        "Can the VA provide nursing home care, or give a caregiver a break?",
        "A VA-run nursing home, a respite stay, and other care VA provides "
        "or pays for directly, not a pension cheque — and the one "
        "thing, in VA.gov's own words, it will not cover."),
    "medicare-home-health-care": (
        "Medicare",
        "Does Medicare pay for a home health aide or nurse at home?",
        "Medicare pays $0 for a covered home health visit — but only "
        "while a doctor-ordered skilled need and homebound status both "
        "hold, and a home health aide alone is never covered."),
    "va-caregiver-support-program": (
        "Veterans' benefits",
        "Can a family caregiver get paid by the VA?",
        "A VA programme pays a monthly stipend to a qualifying family "
        "caregiver, in VA.gov's own words — who the veteran and the "
        "caregiver each have to be, and the wider programme for "
        "everyone else."),
    "illinois-pace-program": (
        "Staying at home",
        "Is PACE available for a parent in Evanston?",
        "A joint Medicare and Medicaid programme pays for full medical and "
        "personal care so an older adult can avoid a nursing home — but "
        "Illinois runs it in only five regions, and this guide checked "
        "whether Evanston is one of them."),
    "illinois-home-caregiver-background-check": (
        "Staying at home",
        "Is it safe to hire a caregiver directly in Illinois?",
        "An agency runs the background check for you. Hiring directly, "
        "the state says the check is yours to make — and names the free "
        "registry that does it."),
    "illinois-money-management-program": (
        "Legal and planning",
        "Who can help my parent pay bills in Illinois?",
        "A state-run volunteer can budget, pay bills and even act as "
        "Social Security representative payee — but only through two "
        "eligibility paths, and only where a Program Site actually "
        "reaches."),
    "illinois-home-care-ombudsman-program": (
        "Staying at home",
        "What to do when in-home care isn't working in Illinois",
        "A free, confidential advocate for a denial letter, an "
        "unresponsive care coordinator or a grievance — for home care "
        "arranged through a Medicaid managed care plan or waiver."),
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
                 "guides.js", "index.html", "paying-nav.js"]


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
    src = (io.open("app.js", encoding="utf-8").read() + "\n" +
           io.open("paying-nav.js", encoding="utf-8").read())
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
