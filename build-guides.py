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

2026-11-04 (Experiment 1): the cost guide was re-verified against the same
CareScout PDF, and its "What this means in Evanston" section was rewritten
from CareScout's 2025 methodology PDF, the Assisted Living and Shared
Housing Act (210 ILCS 9/15, 9/85 and 9/90 on ilga.gov, an approved legal
source, cross-checked against Public Act 104-0589) and IDPH's assisted
living page. Four listing websites were read only to describe what kind of
number they publish; no figure from any of them is printed. An independent
fact-check of the section ran before review.

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


def listed_iso(g):
    """The date a guide joined the library: its review date, unless it was
    re-reviewed later, in which case "listed" keeps the original date."""
    return g.get("listed", reviewed_iso(g))


def newest_listed():
    """The /guides/ footer and the sitemap's library-level entries (homepage,
    /guides/, privacy notice) carry the most recent date a guide was ADDED.
    A re-review changes only that guide's own page, JSON-LD and sitemap entry:
    re-dating one guide must not tell crawlers that pages which did not change
    were rewritten that day (owner, 2026-11-04)."""
    return max(listed_iso(g) for g in GUIDES)

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
    # 2026 Part B deductible, Medicare.gov costs page, read 17 Nov 2026.
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
    "medicare_nh_choosing": ('Medicare.gov — Your Guide to Choosing a Nursing Home or Other '
                             'Long-Term Services & Supports (publication 02174)',
                             'https://www.medicare.gov/care-compare/en/assets/resources/'
                             'nursing-home/02174-nursing-home-other-long-term-services.pdf'),
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
    # 2026-11-06, the independent-living guide's Evanston section. Each page
    # was read that day. NITA is the RTA's new name; Reduced Fare covers
    # riders 65+, Ride Free covers Benefit Access enrollees. Access Evanston:
    # 65+ (or under 65 with a disability), income up to $35,000 for one person
    # or $60,000 for two, a choice of $5 one-way taxi coupons within Evanston
    # or a City-matched transportation debit card, applications at the City's
    # community centers. HACC does not run the Evanston building; it
    # subsidizes rent there (62+, very low income; the resident pays 30% of
    # income and HACC the rest). Its October 2021 waitlist for that building
    # was online only and open three days. HACC's November 2023 senior notice
    # was dropped after the fact-check: it covers no Evanston building.
    "nita_fares": ('Northern Illinois Transit Authority \u2014 free and reduced fare '
                   'programs',
                   'https://nita.illinois.gov/riders/free-and-reduced-fare-programs'),
    "evanston_access": ('City of Evanston \u2014 Access Evanston Program',
                        'https://www.cityofevanston.org/accessevanston'),
    "hacc_evanston": ('Housing Authority of Cook County \u2014 senior apartments in '
                      'Evanston',
                      'https://thehacc.org/property/ann-rainey-apartments/'),
    "hacc_waitlist_2021": ('Housing Authority of Cook County \u2014 Evanston senior '
                           'waitlist notice, October 2021',
                           'https://thehacc.org/app/uploads/2021/10/Project-Based-Voucher-'
                           'Wait-List-Opening-Ann-Rainey-Apartments.pdf.pdf'),
    "medicare_ltc": ('Medicare.gov \u2014 Long-term care coverage',
                     'https://www.medicare.gov/coverage/long-term-care'),
    # CareScout's own methodology for the 2025 survey (document 131168,
    # 03/02/26): one-bedroom private-pay rates "as they ranged from basic care
    # to more substantial care", the midpoint used where a range was given,
    # community or entrance fees recorded separately, 434 regions based on
    # 387 metropolitan areas. Read from the PDF on 2026-11-04.
    "carescout_method": ('CareScout 2025 Cost of Care Survey \u2014 Methodology',
                         'https://assets.carescout.com/x/e3933bfcf1/131168.pdf'),
    # The cost guide's one published Evanston example (owner-approved
    # 2026-11-12). Both pages are the community's own, read 12 November 2026.
    "trulee_plans": ('Trulee Evanston \u2014 Floor plans (assisted living prices, read 12 November 2026)',
                     'https://truleeevanston.com/floor-plans/'),
    "trulee_care": ('Trulee Evanston \u2014 Your Choice care program (read 12 November 2026)',
                    'https://truleeevanston.com/your-choice/'),
    # The Assisted Living and Shared Housing Act, read on ilga.gov 2026-11-04.
    # Section 15 was amended by P.A. 104-0589, and the compiled page has not
    # caught up, so both are cited. The sentences relied on here (assessment
    # before admission, at least yearly and after a significant change, the
    # service plan as a basis for the contract) read the same in that Act.
    # Sections 85 and 90 are unamended since 2005.
    "ilcs_al_15": ('Assisted Living and Shared Housing Act, 210 ILCS 9/15 \u2014 '
                   'assessment and service plan',
                   'https://www.ilga.gov/legislation/ilcs/documents/021000090K15.htm'),
    "pa_104_0589": ('Public Act 104-0589 \u2014 amends 210 ILCS 9/15',
                    'https://ilga.gov/Legislation/PublicActs/View/104-0589'),
    "ilcs_al_85": ('Assisted Living and Shared Housing Act, 210 ILCS 9/85 \u2014 '
                   'contract requirements',
                   'https://www.ilga.gov/legislation/ilcs/documents/021000090K85.htm'),
    "ilcs_al_90": ('Assisted Living and Shared Housing Act, 210 ILCS 9/90 \u2014 '
                   'contents of the contract',
                   'https://www.ilga.gov/legislation/ilcs/documents/021000090K90.htm'),
    # 2026-11-05: this site is the Illinois Hospital Report Card. It covers
    # hospitals and surgery centres only, not nursing homes or assisted living.
    # The inspection guide no longer cites it (Experiment 2).
    "idph": ('Illinois Department of Public Health — Health Care Report Card',
             'https://healthcarereportcard.illinois.gov/'),
    # Experiment 2, 2026-11-05: where each kind of Illinois inspection record is
    # kept. Every page below was read on 2026-11-05. The quarterly reports list
    # IDPH's actions under the Nursing Home Care Act, one entry per facility
    # with its name, address, survey date, violation types and fines. The
    # Type "AA" page is cited on lig.ilga.gov because the web tool could read
    # it there; the other three types were read on ilga.gov.
    "idph_nh": ('Illinois Department of Public Health — Nursing Homes',
                'https://dph.illinois.gov/topics-services/health-care-regulation/nursing-homes.html'),
    "idph_nh_quarterly": ('Illinois Department of Public Health — Quarterly Reports '
                          'of Nursing Home Violators',
                          'https://dph.illinois.gov/topics-services/health-care-regulation/'
                          'nursing-homes/violator-quarterly-reports.html'),
    "ilcs_nh_3_210": ('Nursing Home Care Act, 210 ILCS 45/3-210 — records a facility '
                      'keeps for public inspection',
                      'https://ilga.gov/legislation/ilcs/documents/021000450K3-210.htm'),
    "ilcs_nh_aa": ('Nursing Home Care Act, 210 ILCS 45/1-128.5 — Type “AA” '
                   'violation',
                   'https://lig.ilga.gov/legislation/ilcs/documents/021000450K1-128.5.htm'),
    "ilcs_nh_a": ('Nursing Home Care Act, 210 ILCS 45/1-129 — Type “A” violation',
                  'https://ilga.gov/legislation/ilcs/documents/021000450K1-129.htm'),
    "ilcs_nh_b": ('Nursing Home Care Act, 210 ILCS 45/1-130 — Type “B” violation',
                  'https://ilga.gov/legislation/ilcs/documents/021000450K1-130.htm'),
    "ilcs_nh_c": ('Nursing Home Care Act, 210 ILCS 45/1-132 — Type “C” violation',
                  'https://ilga.gov/legislation/ilcs/documents/021000450K1-132.htm'),
    # 9/10 excludes nursing homes from "assisted living establishment" but lets
    # a nursing home convert distinct parts, and a life care facility convert
    # sections, to assisted living: one campus, more than one licence.
    "ilcs_al_10": ('Assisted Living and Shared Housing Act, 210 ILCS 9/10 — '
                   'definitions',
                   'https://ilga.gov/legislation/ilcs/documents/021000090K10.htm'),
    "ilcs_al_110": ('Assisted Living and Shared Housing Act, 210 ILCS 9/110 — powers '
                    'and duties of the Department',
                    'https://www.ilga.gov/legislation/ilcs/documents/021000090K110.htm'),
    "iac_al_1020": ('Illinois Administrative Code, 77 Ill. Adm. Code 295.1020 — '
                    'information to be made available to the resident',
                    'https://ilga.gov/ftp/JCAR/AdminCode/077/077002950A10200R.html'),
    # 4/10 defines "facility" to include nursing homes, assisted living and
    # shared housing, life care facilities and supportive living.
    "ilcs_alz_15": ('Alzheimer’s Disease and Related Dementias Special Care '
                    'Disclosure Act, 210 ILCS 4/15 — disclosure requirements',
                    'https://ilga.gov/legislation/ilcs/documents/021000040K15.htm'),
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
    "idoa_resident_rights_brochure": ('Illinois Department on Aging — "Residents’ Rights '
                                      'for People in Long-Term Care Facilities" (brochure, printed 9/25)',
                                      'https://ilaging.illinois.gov/content/dam/soi/en/web/aging/resources/'
                                      'newsandpublications/publications/documents/ltc-resrights.pdf'),
    "hfs_ltc_brochure": ('Illinois HFS — Long Term Care Services brochure (HFS 3191)',
                         'https://hfs.illinois.gov/info/brochures-and-forms/brochures/hfs3191.html'),
    "hfs_preadmission_notice": ('Illinois HFS Provider Notice, 4 April 2017 — '
                                'Pre-admission screening (PASRR and Determination of Need)',
                                'https://hfs.illinois.gov/medicalproviders/notices/notice.prn170404a.html'),
    "idoa_hco": ('Illinois Department on Aging — The Home Care Ombudsman Program',
                'https://ilaging.illinois.gov/programs/ltcombudsman/the-home-care-ombudsman-program.html'),
    "idph_adv_directives": ('Illinois Department of Public Health — Advance Directives',
                            'https://dph.illinois.gov/topics-services/health-care-regulation/nursing-homes/advance-directives.html'),
    "ilaging_adv_directives": ('Illinois Department on Aging — Advance Directives',
                               'https://ilaging.illinois.gov/aboutus/legal-adv-directives.html'),
    "ilaging_legal_assistance": ('Illinois Department on Aging — Legal Assistance',
                                 'https://ilaging.illinois.gov/programs/legalassistance.html'),
    "hfs_qmb": ('Illinois HFS — Qualified Medicare Beneficiary (QMB) Program brochure (HFS 3352)',
               'https://hfs.illinois.gov/info/brochures-and-forms/brochures/hfs3352.html'),
    "ilaging_msp_chart": ('Illinois Department on Aging — 2026 Medicare Savings Programs chart (QMB, SLMB, QI-1)',
                         'https://ilaging.illinois.gov/content/dam/soi/en/web/aging/ship/documents/medicare-savings-program-chart.pdf'),
    "mmsp": ('Medicare.gov — Medicare Savings Programs',
             'https://www.medicare.gov/medicare-savings-programs'),
    "hfs_pace": ('Illinois HFS — Program of All-Inclusive Care for the Elderly (PACE)',
                'https://hfs.illinois.gov/medicalproviders/pace.html'),
    "hfs_pace_orgs": ('Illinois HFS — Designated PACE Organizations',
                'https://hfs.illinois.gov/medicalproviders/pace/designatedpaceorganizations.html'),
    "hfs_pace_zip": ('Illinois HFS — PACE zip code search',
                'https://hfs.illinois.gov/medicalproviders/pace/zipsearch.html'),
    "mpace": ('Medicare.gov — PACE (Program of All-Inclusive Care for the Elderly)',
             'https://www.medicare.gov/health-drug-plans/health-plans/your-coverage-options/other-medicare-health-plans/PACE'),
    "mhha": ('Medicare.gov — Home health services',
             'https://www.medicare.gov/coverage/home-health-services'),
    "extra_help": ('Medicare.gov — Costs for prescription drug coverage (Extra Help)',
                   'https://www.medicare.gov/basics/costs/help/drug-costs'),
    "msp_extra_help_link": ('Medicare.gov — Medicare Savings Programs',
                            'https://www.medicare.gov/basics/costs/help/medicare-savings-programs'),
    "idoa_aaa": ('Illinois Department on Aging — Area Agencies on Aging',
                'https://ilaging.illinois.gov/forprofessionals/areaagenciesonaging.html'),
    "idoa_nutrition": ('Illinois Department on Aging — Senior Nutrition Program',
                       'https://ilaging.illinois.gov/programs/nutrition.html'),
    "idoa_aps_definitions": ('Illinois Department on Aging — APS Definitions',
                            'https://ilaging.illinois.gov/protectionadvocacy/aps-definitions.html'),
    "idoa_aps_program": ('Illinois Department on Aging — Adult Protective Services (APS)',
                        'https://ilaging.illinois.gov/programs/adult-protective-services-aps-.html'),
    "idoa_engage": ('Illinois Department on Aging — Engage2Change (what happens after a report)',
                    'https://ilaging.illinois.gov/engage.html'),
    "idoa_benefit_access": ('Illinois Department on Aging — Benefit Access Program',
                            'https://ilaging.illinois.gov/benefitsaccess.html'),
    "idoa_benefit_access_faq": ('Illinois Department on Aging — Benefit Access, Eligibility and Frequently Asked Questions',
                                'https://ilaging.illinois.gov/benefitsaccess/eligibility-20and-20frequently-asked-questions.html'),
    "idoa_benefit_access_ridefree": ('Illinois Department on Aging — Benefit Access, Ride Free Transit Benefit',
                                     'https://ilaging.illinois.gov/benefitsaccess/ride-free-transit-benefit.html'),
    "mdme_canes": ('Medicare.gov — Canes',
                  'https://www.medicare.gov/coverage/canes'),
    "mdme_commodes": ('Medicare.gov — Commode chairs',
                      'https://www.medicare.gov/coverage/commode-chairs'),
    "mdme_hospitalbeds": ('Medicare.gov — Hospital beds',
                         'https://www.medicare.gov/coverage/hospital-beds'),
    "mdme_walkers": ('Medicare.gov — Walkers',
                     'https://www.medicare.gov/coverage/walkers'),
    "mdme_wheelchairs": ('Medicare.gov — Wheelchairs & scooters',
                        'https://www.medicare.gov/coverage/wheelchairs-scooters'),
    "idph_vet_homes": ("Illinois Department of Public Health — Veterans' Homes",
                       'https://dph.illinois.gov/topics-services/health-care-regulation/nursing-homes/veterans-homes.html'),
    "idva_homes": ('Illinois Department of Veterans’ Affairs — Illinois’ Veterans’ Homes',
        'https://veterans.illinois.gov/services-benefits/homes/homes.html'),
    "va_clc": ('VA.gov — VA Community Living Centers',
              'https://www.va.gov/geriatrics/pages/VA_Community_Living_Centers.asp'),
    "va_ltc_new": ('VA.gov — Long-term care',
                   'https://www.va.gov/health-care/about-va-health-benefits/long-term-care/'),
    "va_ltc_overview": ('VA.gov — VA Long Term Care Services',
                        'https://www.va.gov/geriatrics/pages/VA_Long_Term_Care_Services.asp'),
    "va_respite": ('VA.gov — Respite Care',
                  'https://www.va.gov/geriatrics/pages/Respite_Care.asp'),
    "dph_hcwr": ('Illinois Department of Public Health — Health Care Worker Registry',
                'https://dph.illinois.gov/topics-services/health-care-regulation/health-care-worker-registry.html'),
    "dph_home_services": ('Illinois Department of Public Health — Home Services Agencies',
        'https://dph.illinois.gov/topics-services/health-care-regulation/health-care-facilities/home-services.html'),
    "dph_home_services_faq": ('Illinois Department of Public Health — Home Services Agency licensing FAQ',
                              'https://dph.illinois.gov/topics-services/health-care-regulation/health-care-facilities/home-services/faq.html'),
    "idoa_inhome": ('Illinois Department on Aging — In-Home Care for Seniors',
                    'https://ilaging.illinois.gov/programs/caregiver/in-home-care.html'),
    "va_csp_pgcss": ('VA Caregiver Support Program — Program of General Caregiver Support Services (PGCSS)',
        'https://www.caregiver.va.gov/care_caregivers.asp'),
    "va_pcafc": ('VA.gov — Program of Comprehensive Assistance for Family Caregivers',
                'https://www.va.gov/family-and-caregiver-benefits/health-and-disability/comprehensive-assistance-for-family-caregivers/'),
    "va_pcafc_stipend": ('VA Caregiver Support Program — PCAFC Monthly Stipend fact sheet (updated 5 November 2024)',
        'https://www.caregiver.va.gov/pdfs/FactSheets/Monthly-Caregiver-Stipend-Factsheet.pdf'),
    "va_pgcss_res": ('VA.gov — The Program of General Caregiver Support Services',
        'https://www.va.gov/resources/the-program-of-general-caregiver-support-services/'),
    "hfs_fide_enroll": ('Illinois HFS — How To Enroll in a FIDE SNP',
                        'https://hfs.illinois.gov/medicalproviders/cc/mmai/howtoenrollinafidesnp'),
    "hfs_fide_info": ('Illinois HFS — Fully Integrated Dual Eligible Special Needs Plans in Illinois',
                      'https://hfs.illinois.gov/medicalproviders/cc/mmai/fullyintegdesnpii.html'),
    "hfs_managedcare": ('Illinois HFS — Managed Care (for clients)',
                        'https://hfs.illinois.gov/medicalclients/managedcare.html'),
    "hfs_mmai_end": ('Illinois HFS — Medicare Medicaid Alignment Initiative (MMAI) End Date',
                     'https://hfs.illinois.gov/medicalproviders/cc/mmai.html'),
    "hfs_slp_cook": ('Illinois HFS — Cook County Supportive Living Program sites',
                     'https://hfs.illinois.gov/medicalprograms/slf/cook.html'),
    "hfs_slp_resident": ('Illinois HFS — Supportive Living Program resident fact sheet',
                         'https://hfs.illinois.gov/medicalprograms/slf/residentfactsheet.html'),
    "idph_dementia_2025": ('Illinois Department of Public Health — Dementia Annual Report: Dementia Capability in Illinois 2025',
                           'https://dph.illinois.gov/content/dam/soi/en/web/idph/publications/idph/topics-and-services/diseases-and-conditions/alzheimers/dementia-capability-report-2025.pdf'),
    "idph_al_itr_form": ('Illinois Department of Public Health — Assisted Living and '
                         'Shared Housing Involuntary Termination of Residency, Appeal '
                         'and Facility Representative Disclosure forms',
                         'https://dph.illinois.gov/content/dam/soi/en/web/idph/files/'
                         'forms/itrformwithhearingrequestrevised20200221.pdf'),
    "idoa_ltc_rights_page": ('Illinois Department on Aging — Residents’ Rights in '
                             'Long-Term Care Facilities',
                             'https://ilaging.illinois.gov/programs/ltcombudsman/'
                             'residents-rights-in-long-term-care-facilities1.html'),
    "cms_qso2514_nh": ('CMS — QSO-25-14-NH, Revised Long-Term Care Surveyor Guidance '
                       '(Admission Agreements, §483.15(a)(3))',
                       'https://www.cms.gov/files/document/qso-25-14-nh.pdf'),
    "medicare_nh_guide": ('Medicare.gov — Your Guide to Living in a Nursing Home '
                          '(publication 12217)',
                          'https://www.medicare.gov/publications/'
                          '12217-your-guide-to-living-in-a-nursing-home'),
    "hfs_3191": ('Illinois HFS — HFS 3191, Long Term Services & Information for Couples (brochure)',
                 'https://hfs.illinois.gov/info/brochures-and-forms/brochures/hfs3191.html'),
    "hfs_abe_ltc_faq": ('Illinois HFS — Frequently Asked Questions About Medicaid Eligibility '
                        'for Long Term Supports and Services',
                        'https://hfs.illinois.gov/content/dam/soi/en/web/hfs/sitecollectiondocuments/'
                        'ltc_faq.pdf'),
    "hfs_pe_faq": ('Illinois HFS — Provisional Eligibility Process, Questions and Answers',
                   'https://hfs.illinois.gov/content/dam/soi/en/web/hfs/sitecollectiondocuments/'
                   'provisionaleligibilityfaq9122018.pdf'),
    "hfs_pe_notice_2023": ('Illinois HFS Provider Notice, 27 November 2023 — Long Term Care '
                           'facilities: Provisional Eligibility reimplemented',
                           'https://hfs.illinois.gov/medicalproviders/notices/notice.prn231127a.html'),
    "oag_ltc_2025": ('Illinois Auditor General — Performance Audit of Medicaid Eligibility '
                     'Determinations for Long-Term Care (July 2025)',
                     'https://www.auditor.illinois.gov/Audit-Reports/Performance-Special-Multi/'
                     'Performance-Audits/2025_Releases/25-Medicaid-LTC-Eligibility-Perf-Full.pdf'),
    "idoa_money_mgmt": ('Illinois Department on Aging — Money Management (Volunteer Money Management Program)',
                        'https://ilaging.illinois.gov/programs/money-mgmt.html'),
    "idoa_money_mgmt_sites": ('Illinois Department on Aging — Volunteer Money Management Program Site/Agency List (FY27, 22 October 2026)',
                              'https://ilaging.illinois.gov/content/dam/soi/en/web/aging/programs/documents/ivmmp-programsitelist.pdf'),
    "gac_fact_sheet": ('Illinois Guardianship and Advocacy Commission — Office of State Guardian, '
                       'Guardianship fact sheet',
                       'https://gac.illinois.gov/osg/guardianship-fact-sheet.html'),
    "gac_faq": ('Illinois Guardianship and Advocacy Commission — Frequently Asked Questions '
                'About Guardianship',
                'https://gac.illinois.gov/aboutus/guard-faq.html'),
    "medicare_discharge_checklist": ('Medicare.gov — Your discharge planning checklist '
                                     '(publication 11376)',
                                     'https://www.medicare.gov/publications/'
                                     '11376-your-discharge-planning-checklist.pdf'),
    "medicare_fast_appeals": ('Medicare.gov — Fast appeals',
                              'https://www.medicare.gov/providers-services/'
                              'claims-appeals-complaints/appeals/fast-appeals'),
    "va_caregiver_compare": ('VA.gov — How are the 2 VA caregiver support programs different?',
                'https://www.va.gov/resources/how-are-the-2-va-caregiver-support-programs-different/'),
    "va_hbpc": ('VA.gov — Home Based Primary Care',
               'https://www.va.gov/geriatrics/pages/Home_Based_Primary_Care.asp'),
    "va_hhha": ('VA.gov — Homemaker and Home Health Aide Care',
               'https://www.va.gov/geriatrics/pages/Homemaker_and_Home_Health_Aide_Care.asp'),
    "va_phcbs_notice": ('VA.gov — VHA Notice 2024-01, Purchased Home and Community-Based Services Programs',
                        'https://www.va.gov/vhapublications/ViewPublication.asp?pub_ID=11687'),
    "idoi_ltc": ('Illinois Department of Insurance — Long-Term Care Insurance',
                 'https://idoi.illinois.gov/consumers/consumerinsurance/lifeannuities/long-term-care.html'),
    "idoi_complaints": ('Illinois Department of Insurance — Understanding the Consumer Complaint Process',
                        'https://idoi.illinois.gov/consumers/understanding-complaint-process.html'),
    "ship_ltc_shoppers_guide": ('NAIC, A Shopper\u2019s Guide to Long-Term Care Insurance (revised 2019), '
                                'posted by the Illinois Department on Aging (SHIP)',
                                'https://ilaging.illinois.gov/content/dam/soi/en/web/aging/ship/documents/'
                                'shoppers-guide-ltc-insur.pdf'),
    "ship_ltc": ('Illinois Department on Aging — SHIP, Long-Term Care Insurance',
                 'https://ilaging.illinois.gov/ship/long-term-care-insurance.html'),
    "hfs_slp": ('Illinois HFS — Supportive Living Program',
                'https://hfs.illinois.gov/medicalprograms/slf.html'),
    "idph_alz_plan": ('Illinois Department of Public Health \u2014 State of Illinois Alzheimer\u2019s Disease Plan 2026\u20132029',
                      'https://dph.illinois.gov/content/dam/soi/en/web/idph/publications/idph/topics-and-services/diseases-and-conditions/alzheimers/alzheimers-state-plan-20262029.pdf'),
    "medicare_awv": ('Medicare.gov — Yearly "Wellness" visits',
                     'https://www.medicare.gov/coverage/yearly-wellness-visits'),
    "medicare_cog": ('Medicare.gov — Cognitive assessment & care plan services',
                     'https://www.medicare.gov/coverage/cognitive-assessment-care-plan-services'),
    "idoa_helpline": ('Illinois Department on Aging — Senior HelpLine',
                      'https://ilaging.illinois.gov/resources/helpline-main.html'),
    "idoa_aaa_list": ('Illinois Department on Aging — Area Agencies on Aging list',
                      'https://ilaging.illinois.gov/forprofessionals/aaa-list.html'),
    "medicare_ltc_cov": ('Medicare.gov — Long-term care',
                         'https://www.medicare.gov/coverage/long-term-care'),
}


def srcs(*keys):
    return [SRC[k] for k in keys]


# One published Evanston price example for the cost guide, approved by the
# owner on 2026-11-12: neutral, sourced, no ranking, and no Westminster
# Place price. Read from Trulee Evanston's own pages on 12 November 2026:
# assisted living one-bedroom "Prices starting at $9,475" (floor plans) and
# the Your Choice care program at "$1,850* per month", footnoted "*does not
# include monthly rental rate". Advertised rates change: the same care page
# read $1,700 earlier that day. Re-read both pages before changing a figure;
# the total is computed, never typed. Owner refinement the same day: say the
# rent-plus-care package is not directly comparable with the survey median,
# because the two are priced differently, rather than setting them side by
# side as if they were.
TRULEE = {"rent_1br": 9475, "care": 1850, "read": "12 November 2026"}
TRULEE_EXAMPLE = (
    "<p><strong>One Evanston example.</strong> On " + TRULEE["read"] + ", "
    "Trulee Evanston&rsquo;s website listed assisted living rent for a "
    "one-bedroom apartment starting at ${:,} a month, and its ".format(TRULEE["rent_1br"]) +
    "&ldquo;all-inclusive&rdquo; care program at ${:,} a month, which ".format(TRULEE["care"]) +
    "it says does not include rent. That is a combined starting figure of "
    "${:,} a month. It is not directly comparable with the ".format(TRULEE["rent_1br"] + TRULEE["care"]) +
    F["al_median"] + " statewide median, because the two are priced "
    "differently: the survey used a midpoint wherever a community quoted a "
    "range of care prices, while this is one community&rsquo;s advertised "
    "starting rent plus its care program. It is not an Evanston average "
    "either. Advertised rates can change at any time, so ask each community "
    "for a current written quote.</p>")


# The free tour checklist (owner-approved PDF, 2026-11-11): one quiet,
# tappable download link, never a button class, so the gold assessment
# button stays each page's only primary action. Shared by the homepage's
# tour section (index.html, same markup), the three guides whose
# advice the checklist is built from, and the complaint guide (a family
# reporting a facility may be about to compare others). No email, no sign-up, no script.
TOUR_CHECKLIST = (
    '<p class="dl-cta"><a class="dl-link" '
    'href="/downloads/senior-living-tour-checklist.pdf" '
    'download="Senior-Living-Tour-Checklist.pdf">'
    '<svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" '
    'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
    'stroke-linejoin="round"><path d="M12 4v11"/><path d="m7 10 5 5 5-5"/>'
    '<path d="M5 20h14"/></svg>Download Free Tour Checklist</a>'
    '<span class="dl-cta__note">A one-page PDF to print and take on every '
    'tour. No email or sign-up.</span></p>')

# For a reader already planning visits, one quiet sentence under the
# checklist on the cost, inspection-record, complaint and Medicare guides: the homepage's own
# "Ask about a tour" shortcut, with the affiliation stated in the sentence.
# A plain link, never a button; same form, same consent, nothing new counted.
# (The independent-living guide has its own tour block and does not use it.)
TOUR_ASK = ('<p class="narrow-p tour-ask">Visiting Westminster Place in Evanston, '
            'where I work? <a href="/?tour=form#plan-visit">Ask about a tour '
            'here</a>.</p>')


# --------------------------------------------------------------------------
# THE GUIDES
# --------------------------------------------------------------------------
GUIDES = [
    {
        "slug": "assisted-living-cost-illinois",
        "after_section": {"The four costs that surprise families": TOUR_CHECKLIST + TOUR_ASK},
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
        # Re-verified 2026-11-04 when the Evanston section was rewritten: the
        # three CareScout figures were read again from the PDF, so this guide
        # now carries its own date instead of the original five's default.
        "reviewed": "2026-11-04",
        # One of the original five: it joined the library on 2026-10-18. The
        # re-review moves this page's own date only (see newest_listed).
        "listed": "2026-10-18",
        "sources": srcs("carescout", "carescout_method", "idph_al_div",
                        "ilcs_al_15", "pa_104_0589", "ilcs_al_85", "ilcs_al_90",
                        "hfs_slf", "trulee_plans", "trulee_care"),
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
            # Rewritten 2026-11-04 for Experiment 1 (docs/PROJECT_STATUS.md,
            # Section 4). Only this section changed: title, description, short
            # answer, disclosures, assessment and inquiry are untouched. The one
            # figure here is the CareScout survey median. Listing-site figures
            # are described, never printed, and no community is named.
            # Simplified for phones on 2026-11-04 at the owner's request: shorter
            # sentences and paragraphs, with every fact, qualification, the
            # checklist and the citations kept.
            # 2026-11-12, owner-approved: one neutral, sourced example of a
            # published Evanston starting price (TRULEE_EXAMPLE) follows the
            # "starting price" paragraph. It is the only community named here,
            # and no Westminster Place price appears.
            ("What this means in Evanston", [
                "<p>No survey we know of publishes an assisted living median for "
                "Evanston itself. The figures you will find are usually one of three "
                "kinds. They disagree because they measure different things, and "
                "none of them is your parent&rsquo;s bill.</p>",
                "<p><strong>A statewide survey median.</strong> The " +
                F["al_median"] + " figure above is CareScout&rsquo;s 2025 median "
                "monthly assisted living rate for a private one-bedroom in Illinois, "
                "from rates collected July to November 2025. Where a community "
                "quoted a range, from basic care to more substantial care, CareScout "
                "used the midpoint. It noted separately whether a community charges "
                "a non-refundable community or entrance fee. Its PDF tables are "
                "statewide and its regional figures follow metropolitan areas, so "
                "none covers Evanston alone.</p>",
                "<p><strong>A website&rsquo;s estimate.</strong> Listing and referral "
                "websites publish their own &ldquo;Evanston&rdquo; figures. On "
                "4 November 2026 we checked four that come up in a web search for "
                "Evanston assisted living costs. None explained how its figure was "
                "calculated. All four counted communities in other towns, including "
                "Chicago, as Evanston results. One is run by CareScout, but its "
                "&ldquo;Evanston area&rdquo; average is not one of the "
                "survey&rsquo;s published figures.</p>",
                "<p><strong>A starting price.</strong> A &ldquo;from&rdquo; or "
                "&ldquo;starting at&rdquo; price is the lowest price shown, "
                "sometimes for one apartment type. It shows where prices begin, not "
                "what your parent&rsquo;s apartment and care will cost.</p>",
                TRULEE_EXAMPLE,
                "<p><strong>The figure that counts is in the contract.</strong> "
                "Before anyone moves into a licensed assisted living establishment, "
                "Illinois requires a comprehensive assessment. It is repeated at "
                "least once a year and after a significant change in condition. The "
                "service plan built from it is a basis for the contract.</p>",
                "<p>The contract must state the base rate and what it includes. It "
                "must describe the services that cost extra and set out their fees. "
                "It must also say whether there is a community fee, how much it is "
                "and whether it is refundable. The resident or their representative "
                "must get a complete copy, including later changes.</p>",
                "<p>Once the assessment is done and the community has proposed a "
                "service plan, ask it for these figures in writing:</p>",
                '<ul class="res__list">'
                "<li>the base rate for the apartment your parent would actually "
                "take</li>"
                "<li>the fee for each extra service your parent will use, including "
                "those in the service plan</li>"
                "<li>any second-person fee</li>"
                "<li>the community fee, and whether any of it is refundable</li>"
                "</ul>",
                "<p>Convert the first three to monthly amounts and add them up. That "
                "total is the figure to compare between communities. Ask when the "
                "community fee is due.</p>",
                "<p>The statewide median is only a rough check against that total. "
                "The survey used a midpoint wherever a community quoted a range of "
                "care prices, and it does not itemise charges.</p>",
                "<p>A listing website&rsquo;s results are not an official list. The "
                "Illinois Department of Public Health licenses assisted living and "
                "publishes a list of assisted living and shared housing "
                'establishments. <a href="/guides/check-illinois-inspection-records/">'
                "How to check an Illinois care community&rsquo;s inspection "
                "record</a> explains how to look up each one&rsquo;s record.</p>",
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
        "after_section": {"So who does pay for assisted living?": TOUR_CHECKLIST + TOUR_ASK},
        "bridge": ("Knowing what Medicare covers is a different question from knowing "
               "what kind of care your parent actually needs. Coverage follows the "
               "care; it does not decide it."),
        "title": "Does Medicare Pay for Assisted Living or Nursing Home Care?",
        "h1": "Does Medicare pay for assisted living or nursing home care?",
        "desc": ("Medicare does not pay for assisted living. It pays for a qualifying "
                 "skilled nursing stay — " + F["snf_coins"] + " a day for days 21 to 100 "
                 "in 2026. What is and is not covered."),
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
            ("Coverage can end early — but not just because someone stopped improving", [
                "<p>Coverage can stop before day 100, and you may be told the reason "
                "is that your parent <em>has stopped improving</em>. "
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
        "desc": ("Illinois Medicaid pays for care, not room and board, in approved "
                 "Supportive Living facilities. Expect two charges, and a " + F["pna"] +
                 " monthly personal needs allowance."),
        "intent": "Illinois Medicaid programme",
        "answer": ("The Supportive Living Program is how Illinois Medicaid pays for "
                   "assisted-living-style care. It covers the <strong>cost of "
                   "services</strong> in an approved Supportive Living facility. The "
                   "resident pays a state-set room and board charge, plus a "
                   "<strong>group care credit</strong> calculated from their own income, "
                   "and keeps a personal needs allowance of <strong>" + F["pna"] +
                   " a month</strong>."),
        "sources": srcs("hfs_slf", "hfs_rb", "hfs_hcbs", "hfs_slp_rates", "hfs_slp_cook", "hfs_slp_resident", "idph_dementia_2025"),
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
            ("If your parent has dementia: dementia care settings", [
                "<p>Some Supportive Living facilities are certified as "
                "<strong>dementia care settings</strong>. HFS&rsquo;s Cook County "
                "list marks each one with the note &ldquo;Dementia care setting "
                "that serves residents age 65+&rdquo;. The Illinois Department of "
                "Public Health&rsquo;s 2025 dementia report says &ldquo;the DCS "
                "must provide three daily well-being checks and at least three "
                "daily scheduled activities,&rdquo; and that twenty Supportive "
                "Living sites are certified dementia care settings, with more "
                "than 520 apartments.</p>",
                "<p>Near Evanston the choice is narrow. HFS&rsquo;s Cook County "
                "list, read on 17 November 2026, shows no Supportive Living site "
                "in Evanston, Skokie, Wilmette, Niles, Morton Grove, "
                "Lincolnwood, Glenview or Park Ridge. It marks six Cook County "
                "sites as dementia care settings: the closest to Evanston is "
                "Asbury Court in Des Plaines, and the other five are on "
                "Chicago&rsquo;s far South Side or in the south suburbs. The "
                "Supportive Living sites it lists on Chicago&rsquo;s North Side "
                "are not marked as dementia care settings.</p>",
                "<p>Lists change, so confirm the current one before ruling a "
                "setting in or out. HFS&rsquo;s resident fact sheet points "
                "families to its Bureau of Long-Term Care: 217-782-0545, or "
                "844-528-8444 toll free.</p>",
            ]),
            ("Questions worth asking before you apply", [
                "<ul class=\"res__list\">"
                "<li>Is this specific community an approved Supportive Living facility?</li>"
                "<li>If my parent has dementia, is this a certified dementia care "
                "setting?</li>"
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
        "after_section": {"Check every community, including ours": TOUR_CHECKLIST + TOUR_ASK},
        "bridge": ("An inspection record tells you how well a community does its job. "
               "It cannot tell you whether that is the job your parent needs doing "
               "in the first place."),
        # Experiment 2, 2026-11-05. The page sent families to the "Health Care
        # Report Card", which is the Illinois Hospital Report Card: hospitals
        # and surgery centres only. Rewritten to say where each kind of record
        # is kept, with an Evanston section that checks a campus part by part.
        # The title is kept until Search Console shows the queries this page
        # earns; a title change needs its own approval.
        "reviewed": "2026-11-05",
        "listed": "2026-10-18",
        "title": "How to Check Illinois Nursing Home Inspection Records",
        "h1": "How to check an Illinois care community's inspection record",
        "desc": ("How to find Illinois nursing home and assisted living inspection "
                 "records, what the violation types mean, and what to ask an Evanston "
                 "community to show you."),
        "intent": "how-to / due diligence",
        "answer": ("It depends on what each part of the community is licensed as. For "
                   "a <strong>nursing home</strong>, <strong>Medicare Care "
                   "Compare</strong> publishes inspection, staffing and quality data. "
                   "The <strong>Illinois Department of Public Health</strong> "
                   "publishes quarterly reports of the nursing home violations it has "
                   "acted on. For <strong>assisted living</strong>, ask the community "
                   "to show you its most recent state survey. Illinois rules require it "
                   "to make the results available for residents to review, so ask "
                   "before your parent becomes one."),
        "sources": srcs("mcompare", "idph_nh", "idph_nh_quarterly", "ilcs_nh_3_210",
                        "ilcs_nh_aa", "ilcs_nh_a", "ilcs_nh_b", "ilcs_nh_c",
                        "ilcs_al_10", "idph_al_div", "ilcs_al_110", "iac_al_1020",
                        "ilcs_alz_15"),
        "body": [
            ("Start with what each part is licensed as", [
                "<p>Illinois licenses nursing homes and assisted living under "
                "different laws. Their records are kept in different places. One "
                "campus can hold more than one licence. So first ask what each part "
                "of a community is licensed as. The answer tells you where to "
                "look.</p>",
                "<p>What you are looking for is not a perfect record — almost nobody has "
                "one. You are looking for <em>patterns</em>. A single citation three "
                "years ago that was corrected is noise. The same category of problem "
                "appearing in consecutive inspections is a signal.</p>",
            ]),
            ("For a nursing home, check Medicare Care Compare", [
                "<p>Medicare Care Compare covers nursing homes certified by Medicare "
                "or Medicaid. "
                "Besides inspection results, it publishes reported staffing levels, "
                "including registered nurse hours per resident per day, and staff "
                "turnover.</p>",
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
                "<p>Note the scope limit honestly: Care Compare covers nursing homes "
                "certified by Medicare or Medicaid. "
                "Assisted living is licensed by the state rather than Medicare-certified, "
                "so Care Compare has no record of it. The Evanston section below shows "
                "where its record is.</p>",
            ]),
            ("How to check an Evanston community's record", [
                "<p>Ask each Evanston community you are considering what each part of "
                "it is licensed as. Then check each part where its record is kept.</p>",
                '<ul class="res__list">'
                "<li><strong>Nursing care.</strong> This means a nursing home, or the "
                "nursing part of a larger campus. Look it up on Medicare Care Compare. "
                "If it is not there, ask whether it is certified by Medicare or "
                "Medicaid. Then open the latest of the Illinois Department of Public "
                "Health&rsquo;s quarterly reports of nursing home violators. Search it "
                "for &ldquo;Evanston&rdquo; and check the facility city on each match, "
                "because an owner based in Evanston can match too. Each entry gives "
                "the facility&rsquo;s name and address, the survey date, the type of "
                "each violation and any fine. On your visit, ask to see the inspection "
                "reports. Illinois requires a nursing home to keep every state "
                "inspection report and every state or court order from the past five "
                "years for public inspection.</li>"
                "<li><strong>Assisted living.</strong> The Illinois Department of "
                "Public Health licenses it, and the law calls for an unannounced state "
                "visit to each establishment every year. Check that the community "
                "appears on the department&rsquo;s online list of licensed establishments, "
                "linked from its assisted living page. Then ask to see its most recent "
                "state survey results and any statement of correction still in "
                "effect. Illinois rules require it to make these available for review. "
                "The rule is written for residents, so a community may not have to "
                "show a family before move-in. Ask anyway, and ask how each finding "
                "was corrected.</li>"
                "<li><strong>Memory care.</strong> Ask which licence it operates under, "
                "and check that record as above. Then ask for the written dementia-care "
                "disclosure. Illinois requires a facility with an Alzheimer&rsquo;s "
                "special care unit to set out certain facts in writing for a potential "
                "resident or their representative. They include its admission and "
                "discharge procedures, its minimum and maximum staffing ratios, its "
                "activities, the family&rsquo;s role and its costs.</li>"
                "<li><strong>Independent living.</strong> This site found no Illinois "
                "care licence for it, so it has no state inspection record of this "
                "kind. If the campus also has assisted living or nursing care your "
                "parent might need later, check those records now. The "
                '<a href="/guides/independent-living-evanston/">independent living '
                "guide</a> explains why.</li>"
                "</ul>",
                "<p>The same steps work anywhere in Illinois. Only the town you search "
                "for changes.</p>",
            ]),
            ("What the Illinois nursing home violation types mean", [
                "<p>The quarterly reports label each violation with a type. The "
                "Nursing Home Care Act defines four:</p>",
                '<ul class="res__list">'
                "<li><strong>Type AA:</strong> a violation that proximately caused a "
                "resident&rsquo;s death.</li>"
                "<li><strong>Type A:</strong> one that created a substantial "
                "probability of death or serious physical or mental harm to a "
                "resident, or that caused actual physical or mental harm.</li>"
                "<li><strong>Type B:</strong> one more likely than not to cause more "
                "than minimal physical or mental harm.</li>"
                "<li><strong>Type C:</strong> one with a substantial probability of "
                "causing less than minimal physical or mental harm.</li>"
                "</ul>",
                "<p>These four types come from the nursing home law. They do not "
                "describe assisted living findings.</p>",
            ]),
            ("Reading a record without panicking", [
                "<ul class=\"res__list\">"
                "<li><strong>Check the date.</strong> A finding from four years ago under "
                "different management is weaker evidence than one from last quarter.</li>"
                "<li><strong>Check severity.</strong> Citations are scaled. A paperwork "
                "deficiency is not a resident-harm finding. For a nursing home, the "
                "violation type tells you which you are reading.</li>"
                "<li><strong>Check whether it recurred.</strong> Correction is normal. "
                "Repetition is the problem.</li>"
                "<li><strong>Read absence carefully.</strong> A community missing from "
                "one quarter&rsquo;s report had no state action listed that quarter. "
                "That is not the same as a clean record.</li>"
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
        "title": "Assisted Living vs. Memory Care vs. Skilled Nursing vs. Rehab",
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
        "desc": ("Illinois pays for homemaker help and adult day service for some "
                 "older adults who would otherwise need a nursing home. Who qualifies, "
                 "and how to start."),
        "intent": "staying at home",
        "answer": ("Possibly. Illinois runs the <strong>Community Care Program</strong>, "
                   "which the Department on Aging describes as helping older adults "
                   "&ldquo;who might otherwise need nursing home care to remain in their "
                   "homes.&rdquo; It is for people <strong>60 or older</strong> with "
                   "<strong>non-exempt assets of " + F["ccp_assets"] + " or less</strong> "
                   "and an assessed need for long-term care. A house, a car and personal "
                   "furnishings are exempt from that asset figure. You start by calling "
                   "the Senior HelpLine on <strong><a href=\"tel:+1" + F["ccp_line"][2:].replace("-", "") + "\">"
                   + F["ccp_line"] + "</a></strong>."),
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
                "<p>Call the <strong>Senior HelpLine</strong> on <strong><a href=\"tel:+1"
                + F["ccp_line"][2:].replace("-", "") + "\">" + F["ccp_line"]
                + "</a></strong>. HFS instructs callers to choose a language "
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
        "title": "How Illinois Medicaid Pays for Long-Term Care and Spend-Down",
        "h1": "How Illinois Medicaid pays for long-term care, and what spend-down means",
        "desc": ("Illinois Medicaid can pay for nursing home and other long-term care. "
                 "What it covers, how to apply, and what &ldquo;spend-down&rdquo; means "
                 "if income or assets are too high."),
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
        "after_section": {"Where this fits with the rest of this site": TOUR_CHECKLIST + TOUR_ASK},
        "bridge": ("Some concerns are a problem with the care being given. Others are a "
               "sign the setting itself no longer matches what your parent needs. "
               "Those two look alike from the outside."),
        "reviewed": "2026-10-23",
        "title": "How to Report a Problem at an Illinois Nursing Home or Assisted Living",
        "h1": "How to report a problem at an Illinois care facility",
        "desc": ("A concern about an Illinois nursing home or assisted living has two "
                 "channels: an advocate who works it with you, a regulator who "
                 "investigates. Which to call."),
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
        "sources": srcs("idoa_ombudsman", "idoa_ombudsman_contact", "idph_ccr", "idoa_aps_program"),
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
            ("The other number on the Ombudsman page", [
                "<p>The Ombudsman Program's own page also carries a navigation link "
                "reading &ldquo;Report Abuse: 1-866-800-1409.&rdquo; The Department on "
                "Aging's Adult Protective Services page identifies that number as "
                "&ldquo;the statewide, 24-hour Adult Protective Services Hotline,&rdquo; "
                "and Adult Protective Services covers adults living in the community, "
                "not residents of a care facility. For a parent who lives at home, see "
                '<a href="/guides/illinois-elder-abuse-reporting/">What to do about '
                "suspected elder abuse or neglect at home in Illinois</a>. For a concern "
                "inside a facility, use the two channels above.</p>",
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
        "title": "Illinois Medicaid Estate Recovery: Will the State Take the House?",
        "h1": "Will Illinois take my parent&rsquo;s house after Medicaid pays for care?",
        "desc": ("Illinois can claim against a Medicaid recipient's estate after death, "
                 "never against heirs personally, and the first $25,000 is protected. "
                 "What it can reach."),
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
                 "doctor certifies six months or less to live and comfort care is chosen "
                 "over a cure. What is and is not covered."),
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
        # 2026-11-06, owner's request: more useful for Evanston families
        # considering a move, and the optional tour inquiry easy to find
        # without the assessment. Adds an Evanston section (what three listing
        # sites showed on 6 November, local transport and housing help) and
        # two plain tour links, one under the short answer and one after the
        # visiting advice; the fork keeps the full explanation. No community
        # is named or ranked. Title and H1 unchanged (D-009).
        "reviewed": "2026-11-06",
        "listed": "2026-10-26",
        "title": "Independent Living in Evanston and the North Shore, Explained",
        "h1": "Independent living in Evanston and the North Shore, explained",
        "desc": ("Independent living is housing with services, not care. What the "
                 "monthly fee covers, what Evanston listing sites leave out, and "
                 "local transport and housing help."),
        # Owner, 2026-11-06 (D-024): a clear button under the short answer,
        # with a concise employment disclosure. It uses the existing dark
        # button; the gold "one action colour" stays with the assessment, and
        # the link is the existing tour pathway, so consent is unchanged.
        "after_answer": (
            '<div class="tour-cta">'
            '<p><a class="btn btn--dark" href="/?tour=independent#plan-visit">'
            # Non-breaking spaces keep the name together if the label wraps
            # on a narrow phone: "Request a / Westminster Place Tour".
            'Request a Westminster&nbsp;Place&nbsp;Tour</a></p>'
            '<p class="tour-cta__note">No assessment needed. The person who runs '
            'this guide works at Westminster Place. <a href="#two-ways">How a '
            'request is handled</a>.</p>'
            '</div>'),
        # The listing-website figures in "Looking in Evanston" were read from
        # those websites, which this guide deliberately does not link to, so
        # the sources footnote says so rather than claim every figure came
        # from the list above.
        "figures_except": ("the listing-website figures under &ldquo;Looking in "
                           "Evanston&rdquo;, which were read from those websites "
                           "the same day"),
        # The tour line's "how a request is handled" link lands here.
        "section_ids": {"Two ways to go from here": "two-ways"},
        "after_section": {"Visiting, and what a brochure cannot tell you": TOUR_CHECKLIST},
        "intent": "lifestyle question",
        "answer": ("<strong>Independent living is housing with services, not "
                   "care.</strong> A private apartment, cottage or townhouse, with "
                   "some combination of meals, housekeeping, grounds and transport "
                   "folded into one monthly fee. Generally <strong>no hands-on help "
                   "with bathing or dressing, and generally no nursing staff on the "
                   "floor</strong>. Nobody has to need anything to move in, which is "
                   "the point: most people who do it are well, and they do it while "
                   "they still get to choose."),
        # 2026-11-06: "mcosts" replaced by Medicare's long-term care page,
        # which is the one that says Medicare does not pay for it.
        "sources": srcs("idph_al_div", "medicare_ltc", "carescout", "nita_fares",
                        "evanston_access", "hacc_evanston", "hacc_waitlist_2021"),
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
                "July 2002, under regulations adopted in December 2001. IDPH "
                "publishes the list of licensed establishments.</p>",
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
                "insurance; independent living is housing. Medicare does not pay "
                "for assisted living either. The everyday personal help it provides "
                "is long-term care, and Medicare doesn&rsquo;t pay for long-term "
                "care.</p>"
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
                '<span class="fork__h">I&rsquo;d like to explore a tour of '
                'Westminster Place</span>'
                '<span class="fork__p">Skip the questions entirely. This one '
                'asks for your name and one way to reach you, and sends '
                'nothing until you tick the box. It reaches the person who '
                'runs this guide, who reads every one himself. He works at '
                'Westminster Place and may pass your details to them to '
                'arrange a tour.</span></a>'
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
            ("Looking in Evanston: what the lists leave out", [
                "<p>Search for independent living in Evanston and listing websites "
                "come up alongside the communities themselves. This guide checked "
                "three of them on 6 November 2026.</p>",
                '<ul class="res__list">'
                "<li><strong>Most of a list may not be in Evanston.</strong> One "
                "site said Evanston offers 22 independent living communities; of "
                "the 20 on its first page, two had Evanston addresses. Another "
                "promised the &ldquo;10 best&rdquo; in Evanston, and its own count "
                "of 41 included 37 elsewhere. The third listed four in Evanston and "
                "showed 20 more separately as nearby. Check the street address of "
                "anything on a list.</li>"
                "<li><strong>The phone number may not be the community&rsquo;s."
                "</strong> On one site, every community showed the same phone "
                "number, so it cannot be each community&rsquo;s own line. The other "
                "two gave no number for any community, only the site&rsquo;s own. "
                "To reach a community, use the number on its own website.</li>"
                "<li><strong>No price came with a method.</strong> One site gave an "
                "Evanston &ldquo;average&rdquo;, another a starting price for each "
                "community, and the third no price at all. Neither the average nor "
                "the starting prices came with an explanation on the page of how "
                "they were worked out. Ask each community for the written fee "
                "schedule described above.</li>"
                "<li><strong>No list can be complete.</strong> This guide found no "
                "state licence for independent living as such, so no state register "
                "lists every community.</li></ul>",
                "<p>Two kinds of local help are worth knowing about before a "
                "move.</p>"
                '<ul class="res__list">'
                "<li><strong>Getting around without the car.</strong> Riders 65 or "
                "older can get a reduced-fare permit for CTA, Metra and Pace from "
                "the Northern Illinois Transit Authority, formerly the RTA. Those "
                "enrolled in the state&rsquo;s Benefit Access program can ride free "
                "instead, after applying to the authority&rsquo;s Ride Free "
                "program. In Evanston, the City&rsquo;s Access Evanston program "
                "helps residents 65 or older, or over 18 with a disability. Income "
                "must be $35,000 or less for one person, or $60,000 or less for "
                "two. Members choose between taxi coupons that cost $5 each, one "
                "per one-way ride within Evanston, and a transportation debit card. "
                "The City "
                "matches money loaded onto the card, up to a monthly limit. "
                "Applications are available at the Levy Senior Center and the "
                "City&rsquo;s other community centers.</li>"
                "<li><strong>If market-rate independent living is out of reach."
                "</strong> The Housing Authority of Cook County subsidizes rent in "
                "an income-restricted building in Evanston for people 62 or older on "
                "very low incomes. In the units it subsidizes, the resident pays 30% "
                "of their income toward rent and the Housing Authority pays the "
                "rest. When its waitlist for that building opened in October 2021, "
                "it took applications online only, from the morning of 13 October "
                "to the afternoon of 15 October. Check the Housing "
                "Authority&rsquo;s website often.</li></ul>",
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
                "decision. Nothing obliges anyone to move.</p>",
                "<p>If one of those visits is to Westminster Place, where the person "
                "who runs this guide works, you can "
                '<a href="/?tour=independent#plan-visit">ask about a tour</a> '
                "without the six questions.</p>"
            ]),
            ("Where this fits with the rest of this site", [
                "<p>If the question is whether someone needs help rather than wants "
                "less house, start with "
                "<a href=\"/guides/levels-of-senior-care-explained/\">the levels of "
                "care explained</a>. If the question is cost, "
                "<a href=\"/guides/assisted-living-cost-illinois/\">what assisted "
                "living actually costs in Illinois</a> carries the figures this page "
                "deliberately does not. For a veteran or surviving spouse who gets "
                "a VA pension, "
                "<a href=\"/guides/va-aid-and-attendance-benefit/\">VA Aid and "
                "Attendance</a> raises that pension for someone who needs help with "
                "daily activities such as bathing or dressing, or meets one of "
                "VA&rsquo;s other conditions. Living in a nursing home is not "
                "required.</p>",
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
        "desc": ("A wartime veteran with no dependents can get at most "
                 + F["va_mapr_aa_single"] + " a year with Aid and Attendance &mdash; the "
                 "whole pension at that rate, less their income. Who qualifies."),
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
        "desc": ("Veteran Directed Care lets an eligible veteran set a spending plan "
                 "and hire their own help at home, including family. Who qualifies, "
                 "how to start, per VA.gov."),
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
        "title": "Illinois Family Caregiver Support Program, Explained",
        "h1": "Is there help for the caregiver, not just the parent, in Illinois?",
        "desc": ("Illinois&rsquo;s Family Caregiver Support Program serves the person "
                 "doing the caring: respite, counselling, training and a local "
                 "resource centre. What it covers."),
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
        "title": "Who Helps My Parent Choose a Medicare Plan for Free in Illinois?",
        "h1": "Who can help my parent choose a Medicare plan for free in Illinois?",
        "desc": ("SHIP is Illinois's free, unbiased Medicare counselling service. "
                 "What the Department on Aging says it does, what it does not say, "
                 "and how to reach a counsellor."),
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
        "slug": "illinois-nursing-home-resident-rights",
        "bridge": ("Knowing what rights your parent has on paper is a "
               "different question from knowing whether the facility "
               "they are in is still the right level of care for them."),
        "reviewed": "2026-11-17",
        "title": "What Rights Does Your Parent Have in an Illinois Care Facility?",
        "h1": "What rights does your parent have in an Illinois nursing home or care facility?",
        "desc": ("What an Illinois nursing home cannot take away: your parent&rsquo;s "
                 "rights on money, privacy, contracts, discharge and appeals, "
                 "from the state&rsquo;s own brochure."),
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
                "resident's room, and the facility may not give information "
                "about a resident or their care to an unauthorized person "
                "without permission. Visits and phone calls "
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
                "written discharge notice already issued, and that if a "
                "hospital stay lasts more than 10 days, the facility must "
                "let the resident return when it has a bed available. A private-pay "
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
        "slug": "illinois-nursing-home-preadmission-screening",
        "bridge": ("Knowing that a screening is required is a different "
               "question from knowing whether a nursing home is even the "
               "setting your parent actually needs."),
        "reviewed": "2026-11-17",
        "title": "Pre-Admission Screening for an Illinois Nursing Home, Explained",
        "h1": "Does my parent need to be screened before moving into an Illinois nursing home?",
        "desc": ("Illinois screens everyone before a nursing home admission, even "
                 "private pay. The two checks (DON and PASRR), who does them, and "
                 "what happens if one is skipped."),
        "intent": "how-to / process",
        "answer": ("<strong>Yes.</strong> An Illinois HFS provider notice states that "
                   "&ldquo;state statutes require that all persons age 18 or older "
                   "seeking admission to a nursing facility must be screened,&rdquo; and "
                   "says this applies regardless of income, assets, or funding source "
                   "&mdash; a private-pay admission is not exempt. Two separate checks "
                   "are involved: a <strong>Determination of Need (DON)</strong> "
                   "assessment of the functional need for nursing-facility-level care, "
                   "and a <strong>PASRR Level I screen</strong> for serious mental "
                   "illness or an intellectual/developmental disability. Both must be "
                   "completed before admission."),
        "sources": srcs("hfs_preadmission_notice", "hfs_ltc_brochure", "idoa_ccp"),
        "body": [
            ("Two different checks, not one", [
                "<p>Families researching this usually find the word "
                "&ldquo;screening&rdquo; used loosely, as if it were one step. The "
                "Illinois Department of Healthcare and Family Services (HFS) provider "
                "notice this guide read describes two separate checks that both apply "
                "before a nursing facility admission.</p>",
                "<p>The first is a <strong>Determination of Need (DON)</strong> "
                "assessment &mdash; a functional evaluation of whether the person "
                "actually needs the level of care a nursing facility provides. The "
                "second is a <strong>PASRR Level I screen</strong> (sometimes called an "
                "OBRA Level I screen), which checks for serious mental illness or an "
                "intellectual/developmental disability. The notice states that this "
                "preliminary screen applies to &ldquo;all applicants to "
                "Medicaid-certified nursing facilities&rdquo;. Someone flagged at Level "
                "I is referred on for a more detailed Level II evaluation.</p>",
            ]),
            ("Who actually does the screening", [
                "<p>The notice names several different screeners, depending on what "
                "is being assessed. <strong>Care Coordination Units (CCUs)</strong> "
                "&mdash; local organizations that the Illinois Department on "
                "Aging&rsquo;s Community Care Program page describes as part of its "
                "&ldquo;Aging Network&rdquo; &mdash; conduct the majority of Level "
                "I screens, and they and DHS Division of Rehabilitation Services "
                "staff carry out the DON assessment.</p>",
                "<p>Hospital discharge planning staff can also carry out an OBRA "
                "Level I screen directly. For someone with a serious mental illness "
                "or a developmental disability, the notice says the level-of-care "
                "decision is made by a DHS Mental Health PASRR agent or an "
                "Independent Service Coordination entity of the Division of "
                "Developmental Disabilities, using a different tool from the "
                "DON.</p>",
                "<p>None of this is a single office or a single phone call. Which "
                "screener is the right one depends on where your parent is &mdash; "
                "still at home, or already in hospital awaiting discharge &mdash; and "
                "that is worth confirming with a hospital social worker or the local CCU "
                "rather than guessing from this list.</p>",
            ]),
            ("Private pay does not exempt you from the screening itself", [
                "<p>This is the detail that most surprises families who intend to pay "
                "privately and assume Medicaid rules do not apply to them. The "
                "screening requirement is a state statute covering <strong>every</strong> "
                "nursing facility admission &mdash; the HFS notice is explicit that it "
                "applies &ldquo;regardless of income, assets, or funding source&rdquo;. "
                "Paying the full bill out of pocket does not remove the requirement to "
                "be screened before moving in.</p>",
                "<p>HFS's own consumer brochure on long-term care frames the same rule "
                "from the other direction, for someone applying for Medicaid: "
                "&ldquo;the screening must show that you need nursing home care or the "
                "state will not pay for it.&rdquo; So the screening does two different "
                "jobs depending on who is asking &mdash; a legal precondition to "
                "admission for everyone, and a payment precondition specifically for "
                "Medicaid.</p>",
                "<p>One reassurance worth knowing: the brochure also states that a "
                "person has the right to enter or remain in a nursing home as long "
                "as they are able to pay for their care, <strong>even if the state "
                "finds they could live safely in the community</strong>. So a "
                "screening result that points to home-based care does not, by "
                "itself, stop a private-pay admission; it mainly decides whether "
                "Medicaid will pay, and it is also the moment a care coordinator "
                "may raise home and community-based alternatives worth hearing out "
                "before deciding.</p>",
            ]),
            ("Timing, and what happens if it is skipped", [
                "<p>Both screens have to happen <strong>before</strong> admission to the "
                "nursing facility, not afterward as paperwork to catch up on. The HFS "
                "notice sets out minimum timelines for the hospital-discharge case: "
                "discharge planners must contact the CCU &ldquo;at least 24 hours in "
                "advance of a pending discharge,&rdquo; and the notice states that, "
                "since 1 January 2017, &ldquo;CCUs must complete the screening within "
                "one day of the request.&rdquo; This guide is reading a 2017 notice to "
                "providers, not a page that states today's timeline, so treat those two "
                "figures as the rule as written then and confirm the current turnaround "
                "with the CCU rather than assuming nothing has changed since.</p>",
                "<p>The consequence of skipping it is stated plainly: the notice says "
                "the state &ldquo;will continue to reject claims for reimbursement of "
                "LTC services provided prior to the completion&rdquo; of the required "
                "screenings, and that Medicaid payment authorization is not allowable "
                "until pre-admission screening is complete. For a family counting on "
                "Medicaid to eventually cover a stay that starts as private pay, an "
                "admission that happened without the screening is not a detail to sort "
                "out later.</p>",
            ]),
            ("If your parent is already living in the nursing home", [
                "<p>The process is different for someone who is already a resident and "
                "only now applying for medical benefits. HFS's brochure states that if "
                "you already live in a nursing home when you apply for medical "
                "benefits, and you entered the facility on or after 1 July 1996, "
                "&ldquo;a special needs screening is completed by Healthcare and Family "
                "Services (HFS)&rdquo; itself, rather than by a CCU before admission. "
                "That is a different screening route from everything described above, "
                "run by a different state agency, for a different situation.</p>",
            ]),
            ("What this guide could not verify", [
                "<p>The state's own screening-results form (HFS 2536, the Interagency "
                "Certification of Screening Results) is the document that would state "
                "how long a completed screening remains valid before a new one is "
                "needed. This guide opened that form and could not read a verifiable "
                "figure off it &mdash; the document did not render as text this guide "
                "could confirm, as opposed to a page it could read directly. Rather than "
                "repeat a number picked up secondhand, this guide will not publish a "
                "validity period. Ask the local CCU or the admitting facility's "
                "admissions office how long your parent's specific screening result is "
                "good for before it needs to be redone.</p>",
            ]),
            ("How to start", [
                "<p>If your parent is still at home, the Illinois Department on Aging's "
                "Community Care Program page describes CCUs as the local point of "
                "contact and directs families to its own map tool to find the right "
                "one &mdash; the same CCU that performs the DON assessment also "
                "coordinates in-home services, covered in full in "
                '<a href="/guides/illinois-community-care-program/">Can my parent get '
                "paid help at home in Illinois?</a> If your parent is currently in "
                "hospital and a nursing home admission is being discussed as part "
                "of discharge planning, HFS&rsquo;s brochure says to ask the nurse "
                "to have someone from the hospital&rsquo;s social service "
                "department come to the room; that person arranges the "
                "screening.</p>",
            ]),
            ("Where this fits with the rest of this site", [
                "<p>If the open question is whether a nursing home is even the right "
                "level of care, rather than how to clear the paperwork to get into one, "
                "see "
                '<a href="/guides/levels-of-senior-care-explained/">Assisted living, '
                "memory care, skilled nursing and rehabilitation &mdash; what is the "
                "difference?</a> If the question is how Medicaid pays once admission is "
                "settled, including what spend-down means, see "
                '<a href="/guides/illinois-medicaid-long-term-care/">How Illinois '
                "Medicaid pays for long-term care, and what spend-down means</a>.</p>",
                "<p>If you are not sure which of those questions you are actually "
                'asking, the <a href="/">free six-question assessment</a> on this site '
                "walks through the specifics and shows the reasoning behind its answer. "
                "It asks for no name, no email and no phone number to see your results, "
                "and your answers never leave your device.</p>",
            ]),
        ],
    },
    {
        "slug": "illinois-medicaid-look-back-period",
        "bridge": ("Whether a past gift still counts against your parent today is "
               "a different question from whether assisted living, memory care "
               "or skilled nursing is the right fit for them now."),
        "reviewed": "2026-11-17",
        "title": "Illinois Medicaid's Five-Year Look-Back and Transfer Penalties",
        "h1": "Will giving money away affect my parent&rsquo;s Illinois Medicaid eligibility?",
        "desc": ("Illinois Medicaid looks back five years for gifts and below-value "
                 "sales before paying for care. What triggers a penalty, "
                 "what does not, and when it starts."),
        "intent": "worry / paying for care",
        "answer": ("<strong>It can.</strong> Illinois HFS reviews the "
                   "<strong>60 months (five years)</strong> before your parent "
                   "applies for nursing home, Supportive Living, or Department on "
                   "Aging in-home waiver services, and a gift or a sale for less "
                   "than something was worth during that window can trigger a "
                   "<strong>penalty period</strong> &mdash; a stretch of time "
                   "Medicaid will not pay toward long-term care. Not every transfer "
                   "counts: HFS says a transfer to a spouse, or a small gift "
                   "consistent with your parent&rsquo;s past giving, will not "
                   "trigger one."),
        "sources": srcs("hfs_ltc_brochure", "hfs_ltc_clients"),
        "body": [
            ("The 60-month look-back, and what it looks back at", [
                "<p>Illinois HFS's own brochure for long-term care applicants, "
                "&ldquo;Long Term Services &amp; Information for Couples&rdquo; "
                "(HFS 3191), states that transfers made &ldquo;within 60 months "
                "(5 years) of the date you apply for medical coverage&rdquo; can "
                "affect eligibility for three kinds of Medicaid-paid long-term "
                "care: a <strong>nursing home</strong>, a "
                '<a href="/guides/illinois-supportive-living-program/">Supportive '
                "Living Facility</a>, and the Department on Aging&rsquo;s in-home "
                "waiver services. The brochure also states that this window used "
                "to be shorter &mdash; 36 months &mdash; until the 60-month rule "
                "took effect on 1 January 2012.</p>",
                "<p>The look-back is not a separate application your parent has to "
                "make. It is something a caseworker checks as part of the same "
                "eligibility process covered in "
                '<a href="/guides/illinois-medicaid-long-term-care/">How Illinois '
                "Medicaid pays for long-term care, and what spend-down "
                "means</a> &mdash; so a transfer made years before anyone was "
                "thinking about a nursing home can still surface the first time "
                "your parent applies.</p>",
            ]),
            ("What counts as a penalised transfer", [
                "<p>HFS states plainly that &ldquo;giving away or selling your resources for less than what they are worth may affect your eligibility,&rdquo; and that the penalty period is &ldquo;the length of time the state will not pay for your long term care services in a nursing home, SLF or home and community-based services.&rdquo; "
                "The brochure illustrates this with an example: Joe gave $80,000 "
                "to his grandchildren for college within the 60-month window, and "
                "&ldquo;may have a penalty period based on the transfers.&rdquo; "
                "The point of the example is not the dollar figure &mdash; it is "
                "that a gift made with good intentions, and no thought of Medicaid "
                "at all, is treated the same as any other transfer for less than "
                "fair value.</p>",
            ]),
            ("Transfers that do not trigger a penalty", [
                "<p>HFS carves out specific exceptions, rather than leaving the "
                "question to judgment call:</p>",
                "<ul class=\"res__list\">"
                "<li><strong>Small, consistent gifts.</strong> The brochure's own "
                "example: Martha's $15 birthday gift was not penalised because it "
                "was &ldquo;a minimal amount consistent with her past "
                "behavior.&rdquo; A pattern of modest giving kept up over years "
                "reads differently from a gift that appears only once, near an "
                "application.</li>"
                "<li><strong>Transfers to a spouse.</strong> HFS states: &ldquo;You may transfer this other property to your spouse or to someone else for the sole benefit of your spouse,&rdquo; and that when a person goes into a nursing home, the spouse may keep the home, the car and the household furnishings.</li>"
                "<li><strong>Returning the property.</strong> HFS states a "
                "penalty can be eliminated by getting the transferred property "
                "back.</li></ul>",
                "<p>This guide is not going to put a current dollar ceiling on "
                "the spousal exception &mdash; see below for why.</p>",
            ]),
            ("When the penalty starts, and how long it lasts", [
                "<p>HFS sets the start date as &ldquo;the month of application "
                "or the month you transferred the resources, whichever is "
                "later.&rdquo; A transfer made long before anyone applies does "
                "not start a clock running early; the penalty only begins once "
                "your parent has actually applied.</p>",
                "<p>The length is tied to what the transfer would have bought: "
                "HFS states the penalty lasts while &ldquo;the uncompensated "
                "value of the transferred property would meet the monthly cost "
                "of nursing care at the private rate.&rdquo; If a second, "
                "separate transfer is found and penalised while an earlier "
                "penalty is still running, HFS states the new penalty &ldquo;begins with the month following the month the previous penalty period ends&rdquo; rather than running at the same time. HFS also states: &ldquo;You will still be entitled to other medical services during the penalty period, if you are eligible&rdquo; "
                "&mdash; it is specifically long-term-care payment that stops, "
                "not all of Medicaid. Your local Family Community Resource Center "
                "(FCRC) &mdash; the same office handling the application &mdash; "
                "is who tells you the actual length in a given case; this guide "
                "deliberately does not attempt that calculation.</p>",
            ]),
            ("A hardship option if the penalty would leave your parent without care", [
                "<p>HFS states your parent can apply for a hardship exception if "
                "a penalty would leave them without &ldquo;food, shelter, "
                "clothing or necessary medical care.&rdquo; The brochure does not "
                "set out the hardship application process in the same page this "
                "guide read, so ask the FCRC handling the application how to "
                "request one rather than assuming the process works the same way "
                "as the separate hardship waiver that exists for "
                '<a href="/guides/illinois-medicaid-estate-recovery/">estate '
                "recovery</a> after death &mdash; that is a different request, to "
                "a different part of HFS.</p>",
            ]),
            ("Figures this guide will not publish", [
                "<p>The HFS 3191 brochure itself illustrates the spousal transfer "
                "exception and a related income-diversion rule with dollar "
                "figures &mdash; but the copy this guide read dates those figures "
                "to 2015, and the brochure says of the spousal limit, &ldquo;The amount may increase each year.&rdquo; Eleven years on, this guide has no way "
                "to confirm those 2015 numbers still apply, so it will not repeat "
                "them. For the amount a spouse at home can currently keep, see "
                "the Community Spouse Resource Allowance and Community Spouse "
                "Maintenance Needs Allowance figures in "
                '<a href="/guides/illinois-medicaid-long-term-care/">How Illinois '
                "Medicaid pays for long-term care</a>, which this library "
                "verified against HFS's current 2026 notice &mdash; that is a "
                "related but legally separate rule from the transfer exception "
                "on this page, so ask the FCRC which one applies to a specific "
                "transfer.</p>",
            ]),
            ("Where this fits with the rest of this site", [
                "<p>This page only covers whether a past transfer can delay "
                "Medicaid paying for care &mdash; not whether your parent needs "
                "that level of care yet, and not what happens to a home after a "
                "Medicaid recipient dies. For the first question, see "
                '<a href="/guides/levels-of-senior-care-explained/">Assisted '
                "living, memory care, skilled nursing and rehabilitation &mdash; "
                "what is the difference?</a> For the second, "
                '<a href="/guides/illinois-medicaid-estate-recovery/">Will '
                "Illinois take my parent's house after Medicaid pays for "
                "care?</a> covers that separately.</p>",
                "<p>If you are not yet sure which level of care applies, the "
                '<a href="/">free six-question assessment</a> on this site walks '
                "through that question and shows its reasoning. It asks for no "
                "name, no email and no phone number, and your answers never "
                "leave your device.</p>",
            ]),
        ],
    },
    {
        "slug": "illinois-home-care-ombudsman-program",
        "bridge": ("Knowing who to call when a paid home-care plan is going wrong "
               "is a different question from knowing whether your parent should "
               "still be living at home at all."),
        "reviewed": "2026-11-17",
        "title": "Illinois Home Care Ombudsman: Help When Home Care Isn't Working",
        "h1": "What to do when your parent's in-home care isn't working in Illinois",
        "desc": ("Illinois has an ombudsman for people getting paid help at home "
                 "through Medicaid, not only in a facility. Who it serves, what it "
                 "does, how to reach it."),
        "intent": "how-to / advocacy",
        "answer": ("If your parent gets home care through an Illinois Medicaid "
                   "managed care plan (a D-SNP) or one of four Home and Community "
                   "Based Services waivers &mdash; Persons who are Elderly, Persons "
                   "with Disabilities, Persons with Brain Injury, or Persons with "
                   "HIV or AIDS &mdash; the Illinois Department on Aging's "
                   "<strong>Home Care Ombudsman Program</strong> is an advocate for exactly this situation: a denial or "
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
                "page on it states that in 2013 the Illinois Act on Aging authorized the Ombudsman Program to provide &ldquo;advocacy services outside of the long-term care setting,&rdquo; and that the program began "
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
                "different situation. It advocates "
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
    {
        "slug": "illinois-advance-directive-power-of-attorney",
        "bridge": ("Naming who decides your parent&rsquo;s medical care is a "
               "different question from knowing what kind of care they "
               "actually need right now."),
        "reviewed": "2026-11-17",
        "title": "Power of Attorney for Health Care in Illinois, Explained",
        "h1": "Does my parent need a power of attorney for health care in Illinois?",
        "desc": ("Illinois doesn&rsquo;t require a health care power of attorney, "
                 "but without one the law picks a decision-maker in a fixed order. "
                 "The four directives, explained."),
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
                "say so themselves (Illinois Living Will Act)</li>"
                "<li><strong>Mental Health Treatment Preference Declaration</strong> "
                "&mdash; records consent to, or refusal of, specific mental health "
                "treatments in advance (Mental Health Treatment Preference "
                "Declaration Act)</li>"
                "<li><strong>Practitioner Orders for Life-Sustaining Treatment "
                "(POLST)</strong> &mdash; a medical order, signed by a doctor as "
                "well as your parent, setting out which life-sustaining "
                "treatments to use or withhold</li>"
                "</ul>",
                "<p>None of the four is required. The Illinois Department of "
                "Public Health states plainly that &ldquo;no health care facility, health care professional or insurer can make you execute an advance directive.&rdquo; In its words: &ldquo;It is entirely your decision.&rdquo;</p>",
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
                "<p>Free standard forms, including a &ldquo;Power of Attorney for Health Care&rdquo;, are published by both the Illinois Department of Public Health (which also offers Spanish versions) and the Illinois Department on Aging.</p>",
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
                "<p>That order has real limits built into it, too. A surrogate <strong>cannot</strong> tell your parent&rsquo;s health care professional to withdraw or withhold life-sustaining treatment unless your parent has a qualifying condition &mdash; a terminal condition, permanent unconsciousness, or an incurable or irreversible condition. A surrogate other than a court-appointed guardian also cannot consent to electroconvulsive therapy, psychotropic medication, or admission to a mental health facility; a surrogate may petition a court for those. A Power of Attorney for Health Care is what lets your parent choose their own decision-maker instead of relying on this default order.</p>",
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
                "<p>The Illinois Department of Public Health says information about the right to make an advance directive is given &ldquo;upon admission to a facility or when provision of care begins.&rdquo; No health care facility can make your parent sign one.</p>",
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
        "slug": "illinois-medicare-savings-program",
        "bridge": ("Qualifying for help with a Medicare premium says nothing "
               "about what kind of care your parent actually needs, or "
               "whether assisted living is even the right next step."),
        "reviewed": "2026-11-17",
        "title": "Illinois Medicare Savings Programs: QMB, SLMB and QI Explained",
        "h1": "Can Illinois help pay my parent's Medicare premium? QMB, SLMB and QI, explained",
        "desc": ("Three Illinois programs (QMB, SLMB, QI) use Medicaid to pay "
                 "Medicare premiums. What each covers, the 2026 income and asset "
                 "limits, and how to apply."),
        "intent": "how-to / eligibility",
        "answer": ("<strong>Illinois runs three Medicare Savings Programs &mdash; QMB, "
                   "SLMB and QI &mdash; that use Medicaid to pay part or all of a "
                   "Medicare beneficiary's premium, and QMB also pays Medicare's "
                   "deductibles and coinsurance.</strong> A caseworker decides which "
                   "of the three a person qualifies for, against income and asset "
                   "limits the state republishes every April. Medicare.gov's own "
                   "advice to anyone unsure: &ldquo;Even if you don&rsquo;t think you qualify, you should still apply.&rdquo;"),
        "sources": srcs("mmsp", "ilaging_msp_chart", "hfs_qmb"),
        "body": [
            ("Three programmes that pay Medicare costs through Medicaid", [
                "<p>The Illinois Department on Aging's own chart describes the "
                "Medicare Savings Program plainly: it &ldquo;is a State Medicaid program that can help to pay Medicare premiums&rdquo; and, depending on the program, deductibles and coinsurance for Medicare beneficiaries who qualify. It is not a separate pension or a "
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
                "coinsurance. Medicare.gov adds a practical consequence for people in QMB: &ldquo;Medicare providers aren&rsquo;t allowed to bill you for services and items Medicare covers, including deductibles, coinsurance, and copayments.&rdquo;</p>",
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
                "April&rdquo;; Illinois automatically disregards $25 of income (the chart&rsquo;s note: &ldquo;Add $25 to incomes because Illinois automatically disregards $25&rdquo;), so the first $25 a month is not counted against the limits above; and the asset limits shown &ldquo;do not include an additional $1,500/$3000 burial allowance deduction.&rdquo;</p>",
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
                "<p>Medicare.gov says people in QMB, SLMB or QI also get <strong>Extra Help</strong>, the "
                "federal programme that caps what a beneficiary pays toward Part D "
                "prescription drug costs. For 2026, Medicare.gov gives that cap as "
                "<strong>no more than $12.65 for each covered drug</strong>. So a parent approved for one of the three also gets help with prescription drug costs.</p>",
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
        "slug": "illinois-pace-program",
        "bridge": ("PACE is worth understanding even where it does not yet reach, "
               "because the question it answers &mdash; can my parent get full "
               "medical and personal care without leaving home &mdash; is the "
               "same question every setting on this site is trying to answer."),
        "reviewed": "2026-11-17",
        "title": "What Is PACE, and Can a Parent in Evanston Use It?",
        "h1": "What is PACE, and can a parent in Evanston use it?",
        "desc": ("PACE coordinates full medical and personal care so an older adult "
                 "can stay at home. Illinois runs it in five regions so far; "
                 "Evanston isn&rsquo;t one yet."),
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
                "they need. The page names prescription drugs, adult day primary care (including meals and recreational therapy), and transportation to the PACE centre "
                "and to medical appointments among the services included.</p>",
                "<p>Cost depends on what the participant already has. With Medicaid, there is <strong>no monthly premium</strong> for PACE. With Medicare but no Medicaid, a participant pays a monthly premium for the long-term-care part of the benefit plus a premium for Part D drugs. "
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
                "Health at Stella's Place for East St. Louis. The page&rsquo;s only date is a launch &ldquo;scheduled to begin in June 2024,&rdquo; and it describes Kinship specifically as &ldquo;a "
                "new entrant into the Illinois health care delivery system&rdquo; "
                "&mdash; so a family calling any of these should ask directly whether it "
                "is actually taking participants yet, rather than assume active service "
                "from being named on the list.</p>",
                "<p>HFS's own zip-code search is how the state tells a family whether "
                "PACE reaches them, and the tool itself warns up front that PACE "
                "&ldquo;may not be available in your area.&rdquo; This guide checked it "
                "directly: none of Evanston's residential zip codes &mdash; 60201, "
                "60202, 60203 and 60208 &mdash; appear on that list. Southern Cook County is the nearest named region, and none of the zip codes on the state&rsquo;s list is an Evanston one.</p>",
            ]),
            ("A figure this guide will not guess at", [
                "<p>Families will want to know what the Medicare-only premium actually "
                "costs. Medicare.gov says a Medicare-only participant pays a monthly premium for the long-term-care part plus a Part D premium, but gives no dollar figure or formula for either one. A premium that varies by "
                "organisation and by an individual's own Medicare status is not a "
                "number this guide can publish responsibly, so it will not estimate "
                "one. Ask the specific PACE organisation "
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
        "slug": "medicare-home-health-care",
        "bridge": ("Qualifying for Medicare&rsquo;s home health benefit turns on a "
               "doctor&rsquo;s definition of &ldquo;skilled&rdquo; and "
               "&ldquo;homebound&rdquo; &mdash; not on whether your parent is safe "
               "to leave alone, which is usually the real question a family is "
               "asking."),
        "reviewed": "2026-11-17",
        "title": "Does Medicare Pay for a Home Health Aide or Nurse at Home?",
        "h1": "Does Medicare pay for a home health aide or nurse at home?",
        "desc": ("Medicare pays $0 for covered home health visits, but only for "
                 "skilled care while a parent is homebound. A home health aide on "
                 "its own is not covered."),
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
                "intermittent, and, in Medicare.gov&rsquo;s words, <strong>&ldquo;only if you&rsquo;re also getting skilled nursing care.&rdquo;</strong> Examples given are bathing or grooming, feeding and help with walking</li>"
                "<li><strong>Injectable osteoporosis drugs</strong> for women who meet "
                "certain criteria</li>"
                "<li><strong>Durable medical equipment and medical supplies</strong> "
                "for use at home</li></ul>",
                "<p>Read that aide line again: aide help is covered <strong>only alongside</strong> skilled care. The next two sections explain why that one condition decides so much of what follows.</p>",
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
                "parent is normally unable to leave home, and leaving takes a lot of effort. Leaving for medical treatment, or for short, infrequent non-medical reasons, is allowed, and so is attending adult day care</li>"
                "<li><strong>A face-to-face encounter.</strong> A doctor or health care provider (like a nurse practitioner) &ldquo;must see you in person and confirm you need home health care&rdquo;</li>"
                "<li><strong>A doctor&rsquo;s order</strong>, carried out by a "
                "Medicare-certified home health agency</li></ul>",
                "<p>Occupational therapy has its own rule worth knowing: a doctor or health care provider must first order it along with nursing care, physical therapy or speech-language pathology, and after that, Medicare.gov says, &ldquo;you can keep getting occupational therapy on its own.&rdquo;</p>",
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
                "<p>Before giving your parent a service Medicare won&rsquo;t cover, the agency should give an Advance Beneficiary Notice (ABN) saying so. Ask for it in writing before agreeing to "
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
        "slug": "medicare-extra-help-prescription-drug-costs",
        "bridge": ("Paying less for a parent's prescriptions says nothing "
                   "about whether assisted living, home care or a nursing "
                   "home is the level of care they actually need."),
        "reviewed": "2026-11-17",
        "title": "Medicare Extra Help: Lowering a Parent's Prescription Drug Costs",
        "h1": "Does your parent qualify for Extra Help with Medicare drug costs?",
        "desc": ("Extra Help lowers Medicare Part D costs for people with limited "
                 "income. Who qualifies automatically, the 2026 limits, 2027 "
                 "copays, and how to apply."),
        "intent": "eligibility / how-to",
        "answer": ("<strong>Extra Help is a Medicare program that pays some or "
                   "all of a Part D prescription drug plan's premium, "
                   "deductible and copays for someone with limited income and "
                   "resources.</strong> Medicare.gov states that &ldquo;some "
                   "people qualify for Extra Help automatically, and other "
                   "people have to apply&rdquo; &mdash; automatic qualification "
                   "comes with full Medicaid, a Medicare Savings Program, or "
                   "Supplemental Security Income (SSI). Anyone else is compared "
                   "against an income and resource limit the page restates "
                   "every year."),
        "sources": srcs("extra_help", "msp_extra_help_link"),
        "body": [
            ("What Extra Help actually pays for", [
                "<p>Medicare.gov describes &ldquo;Extra Help&rdquo; as "
                "&ldquo;a Medicare program to help people with limited income "
                "and resources pay Medicare drug coverage (Part D)&rdquo; "
                "costs, specifically premiums, deductibles, coinsurance and "
                "other costs. It is not a separate drug plan &mdash; it "
                "reduces what a parent already owes on whatever Part D plan "
                "they are enrolled in, and someone receiving it does not pay "
                "the Part D late enrollment penalty that otherwise applies to "
                "people who delay signing up.</p>",
            ]),
            ("Who qualifies automatically, and who has to apply", [
                "<p>The page states plainly: &ldquo;Some people qualify for "
                "Extra Help automatically, and other people have to "
                "apply.&rdquo; Automatic qualification comes from any one of "
                "three things: full-benefit Medicaid, state help paying a "
                "Part B premium through a Medicare Savings Program (QMB, SLMB "
                "or QI &mdash; see "
                '<a href="/guides/illinois-medicare-savings-program/">Can '
                "Illinois help pay my parent's Medicare premium?</a>), or "
                "Supplemental Security Income (SSI). If none of those apply, "
                "Medicare.gov is direct about the alternative: &ldquo;In most "
                "cases, to qualify for Extra Help, you must have income and "
                "resources below a certain limit.&rdquo;</p>",
                "<p>Medicare.gov's own page on Medicare Savings Programs "
                "confirms the link from the other direction: under each of "
                "QMB, SLMB and QI it states, &ldquo;You'll also get Extra "
                "Help paying for your prescription drugs,&rdquo; framed as "
                "something that comes with qualifying for the premium "
                "programme rather than a second application to fill out.</p>",
            ]),
            ("The 2026 income and resource limits", [
                "<p>For someone applying on income and resources rather than "
                "qualifying automatically, Medicare.gov's 2026 figures are: "
                "for one person, an income limit of <strong>$23,940</strong> "
                "and a resource limit of <strong>$18,090</strong>; for a "
                "married couple, an income limit of <strong>$32,460</strong> "
                "and a resource limit of <strong>$36,100</strong>. The page asks separately about Alaska and Hawaii without giving figures for them, and links out to its own "
                "definitions of what counts as income and what counts as a "
                "resource &mdash; this guide did not open those linked pages, "
                "so treat the categories, not just the totals, as worth "
                "checking directly before assuming a parent is over or under "
                "the line.</p>",
            ]),
            ("What it actually costs once you qualify, for 2027", [
                "<p>Medicare.gov lists these as the costs under Extra Help "
                "for 2027: a plan premium of <strong>$0</strong>, a plan "
                "deductible of <strong>$0</strong>, and at a plan's "
                "participating pharmacies, <strong>up to $5.80 for each "
                "generic drug</strong> and <strong>up to $14.40 for each "
                "brand-name drug</strong>. Once total drug costs &mdash; "
                "including certain payments made on a person's behalf, such "
                "as through Extra Help itself &mdash; reach "
                "<strong>$2,400</strong>, the page states a parent will "
                "&ldquo;pay $0 for each covered drug&rdquo; for the rest of "
                "the year. Someone who also has full Medicaid coverage and is "
                "enrolled in the Qualified Medicare Beneficiary (QMB) program "
                "pays even less: the page gives that figure as <strong>no "
                "more than $4.90 for each covered drug</strong>.</p>",
                "<p>These are the figures as published for 2027; the income "
                "and resource limits above are the ones the same page "
                "currently states for 2026. Confirm both against the live "
                "page before relying on either, since Medicare republishes "
                "both sets of numbers on its own schedule.</p>",
            ]),
            ("How to apply, and what happens once you do", [
                "<p>Medicare.gov is specific about the route: &ldquo;If you "
                "don't get Extra Help automatically, you can apply for "
                "it&rdquo; through Social Security, and the page's own "
                "application link points to ssa.gov. This guide did not "
                "independently open the Social Security site to verify what "
                "the application screens look like, so treat "
                "ssa.gov/medicare/part-d-extra-help as a name and address to "
                "go to, not a page this guide can describe first-hand. "
                "Illinois's own "
                '<a href="/guides/illinois-senior-health-insurance-program/">'
                "Senior Health Insurance Program counselors</a> can point you to the state&rsquo;s Extra Help chart and answer questions before you apply.</p>",
                "<p>Applying for Extra Help and a Medicare Savings Program "
                "can happen at the same time: the page states that Social "
                "Security &ldquo;will send information to your state to "
                "initiate an MSP application&rdquo; unless the applicant says "
                "not to on the Extra Help form itself. Once approved, Extra Help runs through 31 December even if income changes mid-year, and someone who still meets the limits keeps it into the next year; if no notice comes from Medicare or Social Security, Extra Help and the same plan simply continue. Anyone can reapply at any time if "
                "income or resources change.</p>",
            ]),
            ("If a pharmacy charges the wrong amount, or there is a gap before coverage starts", [
                "<p>Medicare.gov's advice if a pharmacy charges more than the "
                "Extra Help amount is to contact the drug plan directly, "
                "which may ask for proof of Extra Help, and to tell the plan "
                "how many days of medication are left on hand; "
                "1-800-MEDICARE (1-800-633-4227, TTY 1-877-486-2048) is the "
                "number the page gives if the plan does not resolve it.</p>",
                "<p>For the gap between qualifying and actually being "
                "enrolled in a Part D plan, the page describes Medicare's "
                "Limited Income Newly Eligible Transition (LI NET) Program as "
                "giving &ldquo;temporary Medicare Part D drug coverage to "
                "people who qualify for Extra Help or Medicaid but who "
                "aren't enrolled in a Medicare drug plan yet,&rdquo; with "
                "money back available for covered drugs bought after the "
                "qualifying date if receipts are kept. The number given for "
                "LI NET is <strong>1-800-783-1307</strong> (TTY 711), "
                "8 a.m. to 7 p.m. Eastern.</p>",
            ]),
            ("Where this fits with the rest of this site", [
                "<p>Extra Help only ever touches a Part D drug plan's "
                "premium and copays &mdash; it has nothing to do with paying "
                "for assisted living, home care or a nursing home. For help "
                "with a Medicare premium itself, see "
                '<a href="/guides/illinois-medicare-savings-program/">Can '
                "Illinois help pay my parent's Medicare premium? QMB, SLMB "
                "and QI, explained</a>, and for the much larger question of "
                "Medicaid paying for long-term care, see "
                '<a href="/guides/illinois-medicaid-long-term-care/">How '
                "Illinois Medicaid pays for long-term care</a>.</p>",
                "<p>If the real question is what level of care your parent "
                'needs in the first place, the <a href="/">free six-question '
                "assessment</a> on this site walks through that separately. "
                "It asks for no name, no email and no phone number, and your "
                "answers never leave your device.</p>",
            ]),
        ],
    },
    {
        "slug": "illinois-home-delivered-meals",
        "bridge": ("Knowing your parent can get a meal delivered to the door is a "
               "different question from knowing whether living alone, even "
               "well-fed, is still safe."),
        "reviewed": "2026-11-17",
        "title": "Can My Parent Get Home-Delivered Meals in Illinois?",
        "h1": "Can my parent get home-delivered meals in Illinois?",
        "desc": ("Illinois funds home-delivered meals and group dining for adults "
                 "60 and over. What the program provides, what its page does not "
                 "say, and how to reach it."),
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
                   "provider in your area; the department&rsquo;s map tool finds both, and its Senior HelpLine is listed on the same page."),
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
                "recommended dietary allowances. The department also links a nutrition screening, available in Spanish too, and lists education, counselling, cooking classes and other nutrition-related activities.</p>",
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
                "receiving meals once contacted. This guide will not predict your parent's wait from a "
                "state webpage that does not address it. Ask the local agency "
                "directly when you call.</p>",
            ]),
            ("Finding the agency that covers Evanston", [
                "<p>Illinois delivers this programme through a network of "
                "<strong>Area Agencies on Aging</strong>, each covering a "
                "Planning and Service Area the department has drawn across "
                "the state. The department's own Area Agencies on Aging page "
                "lets you find yours by clicking a map, browsing a list, or opening a list of counties &mdash; and it lists "
                "Cook County twice, once for the City of Chicago and once "
                "for suburban Cook County, so Evanston families need to pick "
                "the entry that actually matches a north-suburban address, "
                "not the Chicago one.</p>",
                "<p>The department's map-based lookup tool is not something "
                "this guide can read and quote text from, so it will not "
                "name a specific agency, address or direct phone number here "
                "that it did not itself verify on the page. The department&rsquo;s nutrition page says to contact your Area Agency on Aging or a nutrition provider in your area, and it also lists the <strong>Senior HelpLine</strong> at <strong>1-800-252-8966 (711 TRS)</strong> if you would rather ask by phone.</p>",
            ]),
            ("Where this fits with the rest of this site", [
                "<p>This is a different programme from the one most families "
                "find first. "
                '<a href="/guides/illinois-community-care-program/">Can my '
                "parent get paid help at home in Illinois?</a> covers "
                "homemaker help, adult day service and emergency response "
                "through the Community Care Program, which runs on its own "
                "asset and need test. The nutrition programme described here is a separate programme, and its page states no income test, unlike the Community Care Program.</p>",
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
        "reviewed": "2026-11-17",
        "title": "What to Do About Suspected Elder Abuse or Neglect at Home in Illinois",
        "h1": "What to do about suspected elder abuse or neglect at home in Illinois",
        "desc": ("Illinois Adult Protective Services takes reports of abuse, "
                 "neglect, exploitation and self-neglect at home, 24 hours a day. "
                 "Who it covers and what happens next."),
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
                "<p>The same page lists <strong>self-neglect</strong> among the allegations it covers, but the page this guide read does not itself spell out a definition for that term. A "
                "family worried that a parent living alone is no longer "
                "managing &mdash; not eating, not taking medication, not "
                "keeping the home safe &mdash; does not need a suspect to "
                "call; self-neglect on its own is a reportable concern.</p>",
            ]),
            ("How to report, and what the state says happens next", [
                "<p>The hotline is <strong>1-866-800-1409</strong>, which the department&rsquo;s APS page calls &ldquo;the statewide, 24-hour Adult Protective Services Hotline&rdquo;; for deaf and speech-impaired callers, the same page says to dial Illinois Relay at <strong>711</strong>. The department's Engage page, aimed "
                "at explaining the process to someone thinking about calling, "
                "says &ldquo;Anonymous reports are accepted&rdquo; and &ldquo;Your name as the reporter is confidential&rdquo; &mdash; it adds "
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
                "in a single success story, that APS worked with a State&rsquo;s Attorney in one case, nothing on the pages read states a general "
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
        "slug": "illinois-benefit-access-program",
        "bridge": ("A cheaper license plate and free transit rides are a "
               "different question from whether your parent can still get "
               "around safely enough to use either one."),
        "reviewed": "2026-11-17",
        "title": "Illinois Benefit Access: Free Transit and a Cheaper License Plate",
        "h1": "Illinois Benefit Access Program: free transit and a cheaper license plate",
        "desc": ("Illinois seniors and people with disabilities under an income limit "
                 "can ride transit free and get a cheaper license plate. Who "
                 "qualifies and how to apply."),
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
                "disabilities ride free on local public transit, and the Department says to &ldquo;contact your local public transit system to find out what their requirements are.&rdquo; The second is a <strong>license plate "
                "discount</strong>, administered through the Secretary of "
                "State&rsquo;s Office once a certificate of eligibility is "
                "presented there.</p>",
                "<p>The Department&rsquo;s pages describe no separate cash payment or rebate &mdash; the benefit is the "
                "transit ride and the plate discount themselves, not a "
                "cheque.</p>",
            ]),
            ("Who qualifies", [
                "<p>Age or disability: the Department&rsquo;s main Benefit "
                "Access page says an applicant must be &ldquo;65 years of "
                "age or older before January 1 of the current year&rdquo; "
                "or must become 65 during the year, and the Department&rsquo;s FAQ page puts the same rule as 65 or older &ldquo;by December 31 of the current year.&rdquo; Both "
                "pages agree on the alternative path: at least 16 before "
                "January 1 of the current year and determined &ldquo;totally "
                "and permanently disabled&rdquo; before that date. In practice, a parent who turns 65 at any point this year meets the age rule.</p>",
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
                "1/1/2020,&rdquo; and gives no later change. A "
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
                "need to be a U.S. citizen to qualify, but does need a Social Security number to complete the application.</p>",
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
                "<p>The FAQ states eligibility &ldquo;is good for <strong>two years</strong>,&rdquo; and that an applicant may "
                "reapply beginning 90 days before it expires &mdash; "
                "consistent with the Ride Free page&rsquo;s instruction to "
                "submit a new application &ldquo;every other year.&rdquo;</p>",
                "<p>For help with the application, the Department&rsquo;s pages list the Senior HelpLine at "
                "<strong>" + F["ccp_line"] + "</strong> (711 TRS for deaf and speech-impaired callers).</p>",
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
        "slug": "medicare-durable-medical-equipment-coverage",
        "bridge": ("Knowing Medicare will pay most of the cost of a wheelchair or a "
               "hospital bed is a different question from knowing whether your "
               "parent's needs have already moved past what a piece of equipment "
               "at home can solve."),
        "reviewed": "2026-11-17",
        "title": "Does Medicare Pay for a Wheelchair, Walker or Hospital Bed?",
        "h1": "Does Medicare pay for a wheelchair, walker or hospital bed at home?",
        "desc": ("Medicare Part B covers a wheelchair, walker or hospital bed at home "
                 "with a doctor's order and an enrolled supplier. Power wheelchairs "
                 "need extra steps."),
        "intent": "coverage question",
        "answer": ("<strong>Yes, with conditions.</strong> Medicare Part B covers "
                   "durable medical equipment — including wheelchairs, scooters, "
                   "walkers, hospital beds, canes and commode chairs — when a "
                   "doctor or other health care provider orders it for use in your "
                   "parent's home. After the Part B deductible (" +
                   F["partB_deductible"] + " in 2026), you pay 20% of the "
                   "Medicare-approved amount, and only if the supplier is enrolled "
                   "in Medicare and accepts assignment. Power wheelchairs and "
                   "scooters need a face-to-face exam and a written prescription "
                   "first, and some require Medicare's prior approval before you "
                   "buy or rent."),
        "sources": srcs("mdme_wheelchairs", "mdme_hospitalbeds", "mdme_walkers",
                        "mdme_canes", "mdme_commodes"),
        "body": [
            ("The rule that applies to all of it", [
                "<p>Medicare.gov states the same condition on its walker, cane and commode-chair pages: &ldquo;Part B covers medically "
                "necessary DME if your doctor or other health care provider orders "
                "it for use in your home.&rdquo; The wheelchair page adds that Part B covers power wheelchairs and scooters &ldquo;only when they&rsquo;re medically necessary&rdquo; &mdash; no order, no coverage, regardless of how "
                "obviously your parent needs the item.</p>",
                "<p>Once that order exists, the cost-sharing is also the same "
                "across every item: &ldquo;After you meet the Part B deductible, "
                "you pay 20% of the Medicare-approved amount (if your supplier "
                "accepts assignment).&rdquo; The Part B deductible is " +
                F["partB_deductible"] + " for 2026. That last clause &mdash; "
                "&ldquo;if your supplier accepts assignment&rdquo; &mdash; is not "
                "a formality, which is why it gets its own section below.</p>",
            ]),
            ("What is actually covered, item by item", [
                "<ul class=\"res__list\">"
                "<li><strong>Wheelchairs and scooters</strong> &mdash; Medicare.gov: "
                "&ldquo;Medicare Part B (Medical Insurance) covers wheelchairs and "
                "power-operated vehicles (scooters) if you're eligible,&rdquo; but "
                "only &ldquo;when they're medically necessary&rdquo;</li>"
                "<li><strong>Walkers, including rollators</strong> &mdash; "
                "&ldquo;Medicare Part B (Medical Insurance) covers walkers, "
                "including rollators if you're eligible&rdquo;</li>"
                "<li><strong>Hospital beds</strong> &mdash; &ldquo;Medicare Part B "
                "(Medical Insurance) may cover hospital beds, if you're "
                "eligible&rdquo;</li>"
                "<li><strong>Canes</strong> &mdash; covered, with one named "
                "exception: &ldquo;Medicare doesn't cover white canes for the "
                "blind&rdquo;</li>"
                "<li><strong>Commode chairs</strong> &mdash; &ldquo;Medicare Part B (Medical Insurance) covers commode chairs,&rdquo; on the same doctor&rsquo;s-order and home-use terms</li></ul>",
                "<p>That cane exclusion is worth sitting with for a moment. Two "
                "items that look alike to a family &mdash; a mobility cane and a "
                "cane for someone who is blind &mdash; are covered differently "
                "because Medicare classifies one as DME and the other as an aid "
                "for a different purpose. The lesson is not about canes "
                "specifically; it is that &ldquo;covered&rdquo; is decided item "
                "by item, on each item's own Medicare.gov page, not by a general "
                "sense that medical equipment is covered.</p>",
            ]),
            ("The supplier matters as much as the doctor's order", [
                "<p>Medicare.gov is direct about this, repeated near-verbatim "
                "across its equipment pages: &ldquo;Medicare will only pay for DME "
                "items if you get them from suppliers who are enrolled in "
                "Medicare.&rdquo; An order from your parent's own doctor does not "
                "help if the equipment comes from a supplier Medicare has not "
                "enrolled &mdash; the claim is not covered, full stop.</p>",
                "<p>Enrollment alone is not the end of it. The walkers page adds: "
                "&ldquo;If a supplier participates in Medicare, they must accept "
                "assignment,&rdquo; and for anything rented rather than bought, "
                "&ldquo;make sure the supplier is willing to accept assignment for "
                "all rental months.&rdquo; The hospital-beds page spells out the risk: &ldquo;If a DME supplier doesn&rsquo;t participate in Medicare or won&rsquo;t accept assignment, you may be charged more.&rdquo; Ask "
                "the question before the equipment is ordered, not after the first "
                "bill arrives.</p>",
            ]),
            ("Wheelchairs and scooters have an extra step", [
                "<p>Power wheelchairs and scooters carry a requirement the other "
                "items on this page do not. Medicare.gov's wheelchairs and "
                "scooters page states you must have &ldquo;a face-to-face "
                "examination and a written prescription from a treating "
                "provider&rdquo; before Medicare will cover one.</p>",
                "<p>On top of that, the page states you &ldquo;may have to get "
                "prior approval&rdquo; for &ldquo;certain types of power "
                "wheelchairs,&rdquo; and says &ldquo;your DME supplier will usually submit a prior authorization request and all documentation to Medicare on your behalf.&rdquo; "
                "Medicare can still say no &mdash; the page describes a denial when &ldquo;Medicare finds you don&rsquo;t medically require a power wheelchair&rdquo; or &ldquo;Medicare doesn&rsquo;t get enough information to make a decision.&rdquo; A "
                "family that orders a power wheelchair expecting the same process "
                "as a cane or a walker can be caught out by this extra step; ask "
                "the supplier, before anything ships, whether prior authorization "
                "applies to the specific model being ordered.</p>",
            ]),
            ("Rent or buy is not always your choice", [
                "<p>Medicare.gov describes renting and buying as both normal, "
                "without settling in advance which applies to which item: "
                "&ldquo;You may need to rent the equipment&rdquo; and separately "
                "&ldquo;you may need to buy the equipment,&rdquo; and in some "
                "cases &ldquo;you may be able to choose whether to rent or buy the "
                "equipment.&rdquo; None of the equipment pages this guide read "
                "states which rule applies to a wheelchair versus a hospital bed "
                "specifically &mdash; that is a question for the supplier before "
                "you commit, not an assumption to make from this page.</p>",
                "<p>One detail softens a long rental: &ldquo;Some items become "
                "your property after you've made a certain number of rental "
                "payments.&rdquo; If your parent will need an item for years "
                "rather than months, ask the supplier directly how many rental "
                "payments that conversion takes for the specific equipment being "
                "ordered.</p>",
            ]),
            ("Where this fits with the rest of this site", [
                "<p>A wheelchair, a hospital bed or a grab-bar-height commode "
                "chair is often how a family first notices that staying at home "
                "is getting harder, not easier &mdash; see "
                '<a href="/guides/levels-of-senior-care-explained/">Assisted '
                "living, memory care, skilled nursing and rehabilitation &mdash; "
                "what is the difference?</a> for how to tell whether equipment is "
                "still the right answer or whether the level of care itself has "
                "changed. Take the "
                '<a href="/">free six-question assessment</a> on this site for '
                "that question specifically &mdash; it asks for no name, no "
                "email and no phone number, and your answers never leave your "
                "device.</p>",
            ]),
        ],
    },
    {
        "slug": "va-nursing-home-and-respite-care",
        "bridge": ("Knowing which settings VA can provide is a different question "
                   "from knowing which kind of care your veteran parent needs "
                   "now: help at home, a respite stay, assisted living or a "
                   "nursing home."),
        "reviewed": "2026-11-17",
        "title": "VA Nursing Home Care and Respite Care, Explained",
        "h1": "Can the VA provide nursing home care, or give a family caregiver a break?",
        "desc": ("What VA.gov says about VA nursing homes, contracted community "
                 "nursing homes, State Veterans Homes and Respite Care, and the "
                 "room and board VA does not pay."),
        "intent": "benefits question",
        "answer": ("<strong>Yes, for enrolled veterans who meet VA&rsquo;s "
                   "criteria &mdash; through VA health care, a different path "
                   "from the Veterans Pension.</strong> VA.gov describes three "
                   "nursing home settings: VA Community Living Centers, "
                   "community nursing homes that VA contracts with, and State "
                   "Veterans Homes. It also describes Respite Care, which pays "
                   "for short-term care so a family caregiver can take a break. "
                   "For a VA nursing home or a contracted community nursing "
                   "home, VA ties eligibility to enrollment in VA health care, "
                   "clinical need and criteria involving service-connected "
                   "status, level of disability and income. One limit many "
                   "families miss: VA says it does not pay room and board in "
                   "assisted living or adult family homes."),
        "sources": srcs("va_ltc_new", "va_clc", "va_respite", "va_ltc_overview",
                        "idva_homes", "idph_vet_homes"),
        "body": [
            ("Three nursing home settings VA describes", [
                "<p>Many families assume VA help with long-term care means a "
                "pension cheque. VA.gov&rsquo;s long-term care page describes "
                "three nursing home settings a veteran may be able to use: a "
                "VA <strong>Community Living Center</strong>, one of the "
                "&ldquo;VA nursing centers that are designed to feel like "
                "home&rdquo;; a <strong>community nursing home</strong>, a "
                "non-VA nursing home that VA contracts with so a veteran can "
                "get care nearer home and family; and a <strong>State "
                "Veterans Home</strong>, which VA.gov describes as owned and "
                "managed by the state.</p>",
                "<p>VA&rsquo;s Community Living Center page is direct: "
                "&ldquo;A Community Living Center (CLC) is a VA Nursing "
                "Home.&rdquo; It offers nursing-home-level care, including "
                "help with activities of daily living and 24-hour skilled "
                "nursing care, and the page says a CLC &ldquo;resembles "
                "&lsquo;home&rsquo; as much as possible,&rdquo; with "
                "family-friendly places for visiting, rooms veterans are "
                "invited to decorate, and pets allowed to visit or live "
                "there.</p>",
                "<p>For a Community Living Center or a community nursing "
                "home, VA&rsquo;s long-term care overview says VA provides the "
                "care &ldquo;IF you meet certain eligibility criteria "
                "involving your service-connected status, level of "
                "disability, and income.&rdquo; The Community Living Center "
                "page adds: &ldquo;You must first be enrolled in the VA health "
                "system, and be medically and psychiatrically stable,&rdquo; "
                "and it says eligibility also depends on clinical need and "
                "whether a place is available. None of this guarantees a "
                "particular setting. State Veterans Homes are run by the "
                "states; Illinois&rsquo;s are covered below.</p>",
            ]),
            ("Respite care: a break for the family caregiver", [
                "<p>VA.gov&rsquo;s long-term care page says a veteran "
                "&ldquo;may be able to get a service called respite care as "
                "part of your VA healthcare benefits.&rdquo; It pays for a "
                "person to come into the home, or for the veteran to go to a "
                "programme outside the home, while the family caregiver takes "
                "a break. VA&rsquo;s Geriatrics and Extended Care page says "
                "the programme is for veterans who need help with activities "
                "of daily living, and also for veterans who are isolated or "
                "whose caregiver is experiencing burden.</p>",
                "<p>It comes in two forms. <strong>Home Respite "
                "Care</strong> &ldquo;pays for a person to come to a "
                "Veteran&rsquo;s home,&rdquo; or for the veteran to attend an "
                "adult day health care programme while the family caregiver "
                "takes a break or runs errands. <strong>Nursing Home Respite "
                "Care</strong> &ldquo;pays for a Veteran to go to a nursing "
                "home&rdquo; while the family is away for a few days, and "
                "VA.gov notes: &ldquo;This type of respite should be scheduled "
                "in advance.&rdquo;</p>",
                "<p>VA.gov&rsquo;s eligibility rule: &ldquo;All enrolled "
                "Veterans are eligible for Respite Care IF they meet the "
                "clinical criteria for the service and it is "
                "available.&rdquo; Services vary by location, and if the "
                "respite is provided by a community agency, an adult day "
                "health care centre or a nursing home rather than by VA "
                "itself, the veteran also needs to meet community care "
                "eligibility.</p>",
                "<p>A copay may apply: &ldquo;A copay for Respite Care may be "
                "charged based on your VA service-connected disability status "
                "and financial information.&rdquo; Neither VA.gov page this "
                "guide read states an annual day limit for Respite Care, so "
                "this guide does not publish one. Ask your VA social worker or "
                "case manager what is available near your parent.</p>",
            ]),
            ("What VA will not pay for: room and board in assisted living", [
                "<p>This is the limit that catches families off guard. "
                "VA&rsquo;s long-term care overview says: &ldquo;The VA does "
                "not pay for room and board in residential settings such as "
                "Assisted Living or Adult Family Homes.&rdquo; It adds that "
                "residential settings and nursing homes each have their own "
                "eligibility requirements, and that a veteran may still "
                "receive some of VA&rsquo;s home and community services while "
                "living in a residential setting.</p>",
                "<p>VA.gov&rsquo;s newer long-term care page says of these "
                "settings: &ldquo;These places are not run, staffed, or paid "
                "for by VA, but we do inspect and approve each one.&rdquo; VA "
                "benefits may still help pay for extra services there, such as "
                "visits from a VA health care provider.</p>",
                '<p>This is where the <a href="/guides/'
                'va-aid-and-attendance-benefit/">Aid and Attendance</a> rate '
                "of the VA pension comes in for veterans and surviving spouses "
                "who qualify: it is money a family can put toward care costs "
                'such as the <a href="/guides/assisted-living-cost-illinois/">'
                "cost of assisted living</a>. As that guide explains, it is a "
                "contribution toward care costs, not a programme that pays for "
                "assisted living.</p>",
            ]),
            ("Help at home that VA names", [
                "<p>VA&rsquo;s long-term care overview lists Geriatric "
                "Evaluation, Adult Day Health Care, Homemaker and Home Health "
                "Aide Care, Respite Care and Skilled Home Health Care, and "
                "says: &ldquo;All enrolled Veterans are eligible for these "
                "services.&rdquo; To get one, the veteran must have a clinical "
                "need for it and it must be available where they live.</p>",
                "<p>VA.gov&rsquo;s newer page describes several of them. "
                "<strong>Adult Day Health Care</strong> is a programme a "
                "veteran can go to during the day for &ldquo;social "
                "activities, companionship, and recreation&rdquo; as well as "
                "care and support. A <strong>homemaker or home health "
                "aide</strong> is &ldquo;A trained caregiver (supervised by a "
                "registered nurse) who comes into your home to help you care "
                "for yourself.&rdquo; <strong>Skilled home health "
                "care</strong> sends providers from a community-based home "
                "health agency to the house for care such as wound care, "
                "physical therapy, social work support and help with daily "
                "tasks. <strong>Home-Based Primary Care</strong> is &ldquo;A "
                "VA healthcare team, led by a VA doctor, who provides "
                "services&rdquo; such as nursing care and physical therapy in "
                "the home.</p>",
            ]),
            ("What it costs", [
                "<p>VA&rsquo;s long-term care overview states: &ldquo;Long "
                "term care copays are not charged until the 22nd day of "
                "care.&rdquo; After that, the Community Living Center page "
                "says &ldquo;A copay may be charged for CLC care based on your "
                "VA service-connected disability status and financial "
                "information,&rdquo; and the application described below is "
                "what sets the amount.</p>",
                "<p>Hospice care is treated differently: &ldquo;Copays are NOT "
                "charged for Hospice Care provided in any setting.&rdquo; For "
                "services VA health care does not cover, VA.gov&rsquo;s newer "
                "page says families may be able to pay through Medicaid, "
                "Medicare or private insurance.</p>",
                "<p>This guide has not verified how a VA pension interacts "
                "with a Community Living Center copay. That depends on income "
                "and disability rules only VA can apply to one person&rsquo;s "
                "file, so ask the VA social worker handling the "
                "application.</p>",
            ]),
            ("How to apply", [
                "<p>VA.gov gives the same instruction for Community Living "
                "Center care and for Respite Care: contact your VA social "
                "worker or case manager to complete <strong>VA Form 10-10EC, "
                "Application for Extended Care Benefits</strong>, which also "
                "tells you the amount of your copay. The veteran must already "
                "be enrolled in VA health care, and VA&rsquo;s overview warns: "
                "&ldquo;Receiving financial compensation for a VA disability "
                "does NOT automatically enroll you in VA health care.&rdquo;</p>",
            ]),
            ("Illinois runs five State Veterans Homes", [
                "<p>The Illinois Department of Veterans&rsquo; Affairs lists "
                "five Illinois Veterans&rsquo; Homes, in Anna, Chicago, "
                "LaSalle, Manteno and Quincy, serving &ldquo;Illinois veterans "
                "and eligible spouses seeking skilled and domiciliary "
                "care.&rdquo; It says the Anna and Quincy homes offer care to "
                "qualifying spouses. The Illinois Department of Public Health "
                "states: &ldquo;Each Home is licensed by IDPH and certified by "
                "the US Department of Veterans Affairs Medical Center of "
                "jurisdiction.&rdquo;</p>",
                "<p>IDPH also describes a protection under Public Act "
                "100-0632: if two or more residents of an Illinois Veterans "
                "Home are diagnosed with an infectious disease within one "
                "month or less, the home must, within 24 hours of being "
                "notified of the second diagnosis, notify each resident and "
                "their emergency contact or next of kin in writing, post a "
                "notice near its main entrance, and notify the Department of "
                "Veterans&rsquo; Affairs and the Department of Public "
                "Health.</p>",
                "<p>This guide has not verified the homes&rsquo; costs or "
                "admission rules. The Illinois Department of Veterans&rsquo; "
                "Affairs publishes an admission application for the homes; "
                "contact it directly before relying on a figure found "
                "elsewhere.</p>",
            ]),
            ("Where this fits with the rest of this site", [
                "<p>This site covers three VA paths, and they are not "
                "interchangeable. "
                '<a href="/guides/va-aid-and-attendance-benefit/">Aid and '
                "Attendance</a> is an increased monthly rate of the VA pension "
                "for veterans and some surviving spouses who already qualify "
                'for a pension. <a href="/guides/va-veteran-directed-care-program/">'
                "Veteran Directed Care</a> gives a veteran who qualifies a "
                "budget to hire their own help at home. This guide is the "
                "third: care VA provides or pays for itself, under its own "
                "eligibility rules rather than a pension calculation.</p>",
                "<p>If the open question in your family is which level of "
                "care your parent needs, rather than which VA programme pays "
                'for it, the <a href="/">free six-question assessment</a> on '
                "this site walks through that separately. It asks for no name, "
                "no email and no phone number, and your answers never leave "
                "your device.</p>",
            ]),
        ],
    },
    {
        "slug": "illinois-home-caregiver-background-check",
        "bridge": ("Checking that a worker is eligible for this work is a "
                   "different question from knowing whether paid help at home "
                   "is the right level of care for your parent at all."),
        "reviewed": "2026-11-17",
        "title": "Is It Safe to Hire a Caregiver Directly for Your Parent in Illinois?",
        "h1": "Is it safe to hire a caregiver directly for your parent in Illinois?",
        "desc": ("An Illinois home care agency runs the background check for "
                 "you. Hire someone directly and the state tells you to check "
                 "its Health Care Worker Registry yourself."),
        "intent": "how-to / safety",
        "answer": ("<strong>It can be, but if you skip an agency, Illinois puts "
                   "the check on you.</strong> The Illinois Department on Aging "
                   "says that for an agency-employed caregiver, &ldquo;the "
                   "agency is responsible for background checks, training, and "
                   "supervision of the caregiver.&rdquo; For a caregiver you "
                   "hire directly, it says &ldquo;you should check the IDPH "
                   "Healthcare Worker Registry to ensure the caregiver is "
                   "eligible to work in-home care.&rdquo; That registry, kept "
                   "by the Illinois Department of Public Health, lists people "
                   "who have had a background check under the Health Care "
                   "Worker Background Check Act and displays administrative "
                   "findings of abuse, neglect or misappropriation of "
                   "property."),
        "sources": srcs("idoa_inhome", "dph_hcwr", "dph_home_services",
                        "dph_home_services_faq", "idph_ccr"),
        "body": [
            ("Two ways to bring a caregiver into the house", [
                "<p>The Illinois Department on Aging&rsquo;s page on in-home "
                "care says &ldquo;some caregivers are employed by an agency "
                "and assigned to you and others are hired directly by "
                "you,&rdquo; and the difference is who vets the person who "
                "will be alone with your parent. For an <strong>agency-employed "
                "caregiver</strong>: &ldquo;the agency is responsible for "
                "background checks, training, and supervision of the "
                "caregiver.&rdquo; For a caregiver a family <strong>hires "
                "directly</strong>, the page says &ldquo;you should check the "
                "IDPH Healthcare Worker Registry to ensure the caregiver is "
                "eligible to work in-home care.&rdquo;</p>",
                "<p>Neither arrangement is wrong. Only one of them comes with "
                "the check already done for you.</p>",
            ]),
            ("Three kinds of licensed home care agency", [
                "<p>The same page describes three kinds of agency licensed by "
                "the Illinois Department of Public Health (IDPH), and they are "
                "not interchangeable. A <strong>Home Services Agency</strong> "
                "employs home care aides for personal care and help with daily "
                "living, for clients of any age, and the page says "
                "&ldquo;Clients served by Home Services Agencies pay "
                "out-of-pocket for care.&rdquo; A <strong>Home Nursing "
                "Agency</strong> provides skilled nursing &ldquo;as prescribed "
                "by an individual&rsquo;s healthcare professional.&rdquo; A "
                "<strong>Home Health Agency</strong> provides &ldquo;skilled "
                "nursing, physical, occupational and speech therapy in the "
                "home,&rdquo; and depending on the circumstances, Medicare, "
                "Medicaid or private insurance may cover those services.</p>",
                "<p>IDPH&rsquo;s own Home Services Agencies page adds: "
                "&ldquo;Home services are not medical.&rdquo; Its licensing "
                "FAQ tells applicants to review the &ldquo;Home Health, Home "
                "Services, and Home Nursing Agency Code, 77 Ill. Adm. Code "
                "245.&rdquo;</p>",
                "<p>This is a separate question from the "
                '<a href="/guides/illinois-community-care-program/">Community '
                "Care Program</a>, through which Illinois pays for in-home "
                "services for some older adults who qualify. The Department "
                "on Aging&rsquo;s page says a family member or friend can work "
                "as a caregiver under that program only if they meet its "
                "qualifications, pass a background check, complete 24 hours "
                "of pre-service training, and are hired and supervised by an "
                "in-home services agency.</p>",
            ]),
            ("If you hire directly, the check is yours to make", [
                "<p>IDPH says the Health Care Worker Registry &ldquo;lists "
                "individuals with a background check conducted pursuant to the "
                "Health Care Worker Background Check Act.&rdquo; It also shows "
                "training information for certified nursing assistants and "
                "other health care workers, and IDPH says it &ldquo;displays "
                "administrative findings of abuse, neglect or "
                "misappropriations of property.&rdquo;</p>",
                "<p>The Act covers the roles a family is most likely to hire "
                "for. IDPH says it applies to unlicensed people employed or "
                "retained by a health care employer as &ldquo;home health care "
                "aides, nurse aides, personal care assistants, private duty "
                "nurse aides,&rdquo; among other direct-care roles. People "
                "with disqualifying convictions &ldquo;are prohibited from "
                "working in any of the above positions unless a waiver has "
                "been granted&rdquo; by IDPH, and &ldquo;A health care employer "
                "must verify registry status of an individual applying for the "
                "above positions prior to employment.&rdquo; The Department on "
                "Aging&rsquo;s page tells a family hiring directly to make the "
                "same registry check.</p>",
                "<p>IDPH says the check can be made by contacting the "
                "department or through its website, where the link reads "
                "&ldquo;Search the Health Care Worker Registry.&rdquo;</p>",
            ]),
            ("What this guide could not verify", [
                "<p>IDPH&rsquo;s registry page describes what the registry "
                "contains but does not explain how to read a search result, "
                "and this guide did not use the search tool itself, so it does "
                "not describe its screens. Read what the tool shows literally, "
                "and contact IDPH if a result is unclear.</p>",
                "<p>To check an agency rather than an individual worker, "
                "IDPH&rsquo;s Home Services Agencies page links to a "
                "&ldquo;Home Services Directory&rdquo; on the state&rsquo;s "
                "open data portal. This guide has not checked what that "
                "directory contains or how current it is, so also ask the "
                "agency for its licence details.</p>",
            ]),
            ("If something goes wrong after you hire someone", [
                "<p>IDPH&rsquo;s complaint page lists the Central Complaint "
                "Registry Hotline, 800-252-4343, Monday to Friday from 8:30 "
                "a.m. to 4:30 p.m., and names home health agencies among the "
                "providers it covers. IDPH&rsquo;s Home Services Agencies page "
                "also points to that complaint section.</p>",
                "<p>Suspected abuse, neglect or exploitation of a parent who "
                "lives at home is a different channel, covered in "
                '<a href="/guides/illinois-elder-abuse-reporting/">What to do '
                "about suspected elder abuse or neglect at home in "
                "Illinois</a>.</p>",
            ]),
            ("Where this fits with the rest of this site", [
                "<p>Checking a caregiver is a narrower question than choosing "
                "how your parent gets help at home. For the state-funded route "
                "and who qualifies, see "
                '<a href="/guides/illinois-community-care-program/">Can my '
                "parent get paid help at home in Illinois?</a> If staying at "
                "home no longer covers what your parent needs, "
                '<a href="/guides/levels-of-senior-care-explained/">Assisted '
                "living, memory care, skilled nursing and rehabilitation "
                "&mdash; what is the difference?</a> sets out the "
                "alternatives.</p>",
                "<p>If you are not sure which of those describes your parent, "
                'the <a href="/">free six-question assessment</a> on this site '
                "walks through it. It asks for no name, no email and no phone "
                "number, and your answers never leave your device.</p>",
            ]),
        ],
    },
    {
        "slug": "va-caregiver-support-program",
        "bridge": ("Whether VA will pay a family caregiver says nothing about "
                   "whether the care a parent needs has moved past what one "
                   "caregiver can safely provide at home."),
        "reviewed": "2026-11-17",
        "title": "Can a Family Caregiver Be Paid by the VA to Care for a Veteran?",
        "h1": "Can a family caregiver get paid by the VA to care for a veteran at home?",
        "desc": ("Who qualifies for VA's monthly caregiver stipend (PCAFC), what "
                 "it includes and how it is set, and the VA caregiver support "
                 "open to everyone else."),
        "intent": "benefits question",
        "answer": ("<strong>Sometimes, through the Program of Comprehensive "
                   "Assistance for Family Caregivers (PCAFC).</strong> It pays "
                   "a monthly stipend to an approved primary family caregiver "
                   "of a veteran who, among other requirements, has a VA "
                   "disability rating of 70% or higher, needs at least six "
                   "months of continuous, in-person personal care, and is "
                   "enrolled in VA health care. A caregiver who does not "
                   "qualify can still get support, without a stipend, through "
                   "VA&rsquo;s Program of General Caregiver Support Services "
                   "(PGCSS)."),
        "sources": srcs("va_pcafc", "va_pcafc_stipend", "va_pgcss_res",
                        "va_csp_pgcss"),
        "body": [
            ("Two programmes, and only one of them pays the caregiver", [
                "<p>Families researching VA help often find "
                '<a href="/guides/va-aid-and-attendance-benefit/">Aid and '
                "Attendance</a> first, an increased rate of a VA pension. "
                "VA&rsquo;s caregiver programmes are different. The "
                "<strong>Program of Comprehensive Assistance for Family "
                "Caregivers (PCAFC)</strong> is the one with a monthly "
                "stipend, and it has requirements for both the veteran and "
                "the caregiver. The <strong>Program of General Caregiver "
                "Support Services (PGCSS)</strong> offers training and support "
                "instead. VA.gov says family caregivers of veterans who are "
                "not eligible for PCAFC &ldquo;may still be able to get "
                "support&rdquo; and resources through PGCSS.</p>",
            ]),
            ("What the veteran has to meet, for PCAFC", [
                "<p>VA.gov says: &ldquo;All of these must be true for the "
                "Veteran you&rsquo;re caring for.&rdquo;</p>",
                '<ul class="res__list"><li>&ldquo;The Veteran has a VA '
                "disability rating (individual or combined) of 70% or "
                "higher&rdquo;</li><li>&ldquo;The Veteran was discharged from "
                "the U.S. military or has a date of medical "
                "discharge&rdquo;</li><li>&ldquo;The Veteran needs at least 6 "
                "months of continuous, in-person personal care "
                "services&rdquo;</li><li>&ldquo;The Veteran needs to be "
                "enrolled in VA healthcare&rdquo;</li></ul>",
                "<p>VA.gov says &ldquo;Personal care services are services the "
                "Veteran needs from another person,&rdquo; and lists three "
                "kinds: health and well-being; everyday personal needs, like "
                "feeding, bathing and dressing; and safety, protection or "
                "instruction in their daily living environment.</p>",
                "<p>Active-duty service members undergoing a medical "
                "discharge &ldquo;will need to apply for VA healthcare,&rdquo; "
                "and VA.gov says they can do that before or after submitting "
                "their application for caregiver assistance.</p>",
            ]),
            ("Who can be the paid caregiver", [
                "<p>VA.gov&rsquo;s requirement for the caregiver: &ldquo;You "
                "must be at least 18 years old. And at least 1 of these must "
                "be true for you:&rdquo;</p>",
                '<ul class="res__list"><li>&ldquo;You&rsquo;re a spouse, son, '
                "daughter, parent, stepfamily member, or extended family "
                "member of the Veteran, or&rdquo;</li><li>&ldquo;You live full "
                "time with the Veteran, or you&rsquo;re willing to live full "
                "time with the Veteran&rdquo; if VA designates you as a family "
                "caregiver</li></ul>",
                "<p>Because only one of the two has to be true, someone "
                "outside the listed family relationships can qualify by living "
                "with the veteran full time, or being willing to. The stipend "
                "goes to the caregiver VA designates as the primary family "
                "caregiver; a secondary family caregiver gets a shorter list "
                "of benefits.</p>",
            ]),
            ("What a primary family caregiver can receive", [
                "<p>VA.gov lists these benefits for both primary and "
                "secondary family caregivers:</p>",
                '<ul class="res__list"><li>Caregiver education and '
                "training</li><li>Mental health counseling</li><li>&ldquo;Certain "
                "travel benefits when traveling with the Veteran to receive "
                "care&rdquo;</li></ul>",
                "<p>A <strong>primary</strong> family caregiver may also "
                "get:</p>",
                '<ul class="res__list"><li>A monthly stipend '
                "(payment)</li><li>Health care through CHAMPVA, the Civilian "
                "Health and Medical Program of the Department of Veterans "
                "Affairs, for a caregiver who does not already qualify for "
                "care or services under another health plan</li><li>&ldquo;Free "
                "legal and financial planning assistance related to the needs "
                "of the injured Veteran.&rdquo;</li><li>&ldquo;At least 30 days "
                "of respite care per year.&rdquo;</li><li>Telehealth therapy "
                "sessions through VA&rsquo;s virtual psychotherapy programme "
                "for caregivers</li><li>Access to military commissaries, "
                "exchanges and recreation retail facilities</li></ul>",
                "<p>VA.gov adds: &ldquo;You must be enrolled in direct deposit "
                "using the VA customer engagement portal to get your monthly "
                "stipend.&rdquo;</p>",
            ]),
            ("How the stipend is set", [
                "<p>VA&rsquo;s PCAFC page says the stipend exists but not how "
                "much it is. VA&rsquo;s Monthly Caregiver Stipend fact sheet, "
                "updated 5 November 2024, explains the formula. It starts from "
                "the Office of Personnel Management&rsquo;s General Schedule "
                "annual rate for grade 4, step 1, &ldquo;based on the locality "
                "pay area in which the eligible Veteran resides, divided by "
                "12.&rdquo; At Level One that monthly figure is multiplied by "
                "0.625. At Level Two, which applies if VA determines the "
                "veteran meets the definition of &ldquo;unable to self-sustain "
                "in the community,&rdquo; it is multiplied by 1.00.</p>",
                "<p>The fact sheet says OPM may, but will not necessarily, update "
                "the General Schedule pay tables each year, and that an update "
                "takes effect on the first of the month after the month OPM "
                "announces it. This guide does not calculate an amount for "
                "any family. Ask the caregiver support team at your VA facility "
                "what the current figure would be.</p>",
            ]),
            ("If PCAFC does not fit: general caregiver support", [
                "<p>VA.gov says PGCSS may be right for a caregiver if all of "
                "these are true: &ldquo;You care for a Veteran who is enrolled "
                "in VA health care,&rdquo; &ldquo;You provide personal care "
                "services to the Veteran,&rdquo; and &ldquo;You want to connect "
                "with other caregivers, get more support from a professional "
                "care team, or grow your skills as a caregiver.&rdquo; It adds: "
                "&ldquo;You don&rsquo;t need to be a relative or live with the "
                "Veteran to be considered a general caregiver.&rdquo; The page "
                "lists no disability-rating requirement and no stipend.</p>",
                "<p>What it offers: peer support mentoring, skills training, "
                "coaching, telephone support, online programmes, and referrals "
                "to available resources. To start, VA.gov says to contact the "
                "caregiver support team or caregiver support coordinator at "
                "your nearest VA facility, or to ask the veteran&rsquo;s VA "
                "health care team for a referral. &ldquo;The Veteran must agree "
                "to receive care from you and have you listed as their "
                "caregiver in their health care record.&rdquo;</p>",
            ]),
            ("How to apply for PCAFC", [
                "<p>VA.gov says &ldquo;You and the Veteran will need to apply "
                "together,&rdquo; and both of you sign and date &ldquo;a joint "
                "Application for the Program of Comprehensive Assistance for "
                "Family Caregivers (VA Form 10-10CG).&rdquo; It can be submitted "
                "online, by mail to the 10-10CG Evidence Intake Center, PO Box "
                "5154, Janesville, WI 53547-5154, or in person: &ldquo;Bring "
                "your completed VA Form 10-10CG to the caregiver support team "
                "at your nearest VA medical center.&rdquo; VA.gov also says: "
                "&ldquo;Don&rsquo;t send medical records along with your "
                "application.&rdquo;</p>",
                "<p>VA.gov sets its own deadline: &ldquo;We&rsquo;ll assign "
                "you as a caregiver no later than 90 days after we get your "
                "application.&rdquo; For approved caregivers, VA.gov says "
                "wellness contacts happen &ldquo;at least once every 120 days, "
                "with 1 annual visit to the Veteran&rsquo;s home.&rdquo; If you "
                "disagree with a decision, &ldquo;you have options to appeal or "
                "request a review of the decision.&rdquo;</p>",
                "<p>For questions about either programme, VA&rsquo;s Caregiver "
                "Support Line is 1-855-260-3274 (TTY: 711), Monday to Friday, "
                "8:00 a.m. to 8:00 p.m. Eastern time.</p>",
            ]),
            ("Where this fits with the rest of this site", [
                "<p>This site covers four VA paths, and they are not "
                "interchangeable. "
                '<a href="/guides/va-aid-and-attendance-benefit/">Aid and '
                "Attendance</a> is an increased monthly rate of the VA pension "
                "for veterans and some surviving spouses who already qualify "
                'for a pension. <a href="/guides/va-veteran-directed-care-program/">'
                "Veteran Directed Care</a> gives a veteran who qualifies a "
                "budget to hire their own help at home. "
                '<a href="/guides/va-nursing-home-and-respite-care/">VA nursing '
                "home and respite care</a> is care VA provides or pays for "
                "itself. This guide covers the programme that can pay a family "
                "caregiver directly. It has not verified whether a household "
                "can use more than one of these at once, so ask a VA social "
                "worker about your situation.</p>",
                "<p>Illinois also runs a caregiver support programme that is "
                "not limited to veterans&rsquo; families: see "
                '<a href="/guides/illinois-family-caregiver-support-program/">'
                "Is there help for the caregiver, not just the parent, in "
                "Illinois?</a></p>",
                "<p>If the open question in your family is whether a "
                "parent&rsquo;s care needs have moved past what one caregiver "
                'can provide at home, the <a href="/">free six-question '
                "assessment</a> on this site walks through that separately. It "
                "asks for no name, no email and no phone number, and your "
                "answers never leave your device.</p>",
            ]),
        ],
    },
    {
        "slug": "illinois-fide-snp-explained",
        "bridge": ("Knowing which plan now handles your parent&rsquo;s Medicare "
                   "and Medicaid coverage is a different question from knowing "
                   "whether the care it arranges is still the right amount of "
                   "help."),
        "reviewed": "2026-11-17",
        "title": "Illinois FIDE SNP: What Replaced MMAI for Dual-Eligible Seniors",
        "h1": "What happened to my parent&rsquo;s MMAI plan, and what is a FIDE SNP?",
        "desc": ("Illinois ended MMAI on 31 December 2025. What a FIDE SNP is, "
                 "who can join one, what happened to MMAI members, and when a "
                 "parent can switch plans."),
        "intent": "benefits question / policy change",
        "answer": ("If your parent has both Medicare and full Illinois Medicaid "
                   "(&ldquo;dually eligible&rdquo;), the combined plan Illinois "
                   "called MMAI ended on <strong>31 December 2025</strong>. "
                   "Illinois now offers <strong>FIDE SNPs</strong> (fully "
                   "integrated dual eligible special needs plans), a type of "
                   "Medicare Advantage plan that provides Medicare and "
                   "Medicaid benefits through one managed care plan. MMAI "
                   "members of Aetna, Humana, Meridian and Molina were moved "
                   "automatically into those companies&rsquo; FIDE SNPs on 1 "
                   "January 2026; Blue Cross Blue Shield did not offer one. "
                   "Not every dually eligible person can join, and the annual "
                   "Medicare Open Enrollment Period runs from 15 October to 7 "
                   "December."),
        "sources": srcs("hfs_mmai_end", "hfs_fide_info", "hfs_fide_enroll",
                        "hfs_managedcare"),
        "body": [
            ("MMAI ended on 31 December 2025", [
                "<p>Illinois HFS states: &ldquo;The Illinois Medicare-Medicaid "
                "Alignment Initiative (MMAI) program will end December 31, "
                "2025.&rdquo; HFS says the reason is that &ldquo;the Centers "
                "for Medicare &amp; Medicaid Services (CMS) is requiring states "
                "with a MMAI program to convert to the D-SNP model,&rdquo; and "
                "that &ldquo;FIDE SNPs will be the only type of D-SNP model "
                "available in Illinois&rdquo;.</p>",
                "<p>HFS describes a FIDE SNP as &ldquo;a type of Medicare "
                "Advantage plan&rdquo; that provides both Medicare and "
                "Medicaid benefits through one managed care plan, and says "
                "FIDE SNPs are the most like MMAI plans because &ldquo;they "
                "provide the same level of care coordination&rdquo;. It adds "
                "that &ldquo;Medicaid wraps around Medicare by helping with "
                "Medicare premiums and cost sharing.&rdquo;</p>",
            ]),
            ("What happened to MMAI members", [
                "<p>HFS&rsquo;s enrolment page says that for &ldquo;Members of "
                "an MMAI plan offered by Aetna, Humana, Meridian, and "
                "Molina,&rdquo; &ldquo;CMS will automatically enroll these "
                "members in the Illinois FIDE SNP offered by these "
                "companies&rdquo; with a start date of 1 January 2026. Those "
                "members did not need to do anything, and could choose other "
                "coverage instead.</p>",
                "<p>Blue Cross Blue Shield was different: &ldquo;Blue Cross Blue "
                "Shield will not be offering a FIDE SNP for 2026.&rdquo; HFS "
                "says BCBS MMAI members who made no choice before 31 December "
                "2025 were automatically enrolled by CMS in Original Medicare "
                "with a Medicare drug plan from 1 January 2026. For their "
                "Medicaid benefits, members receiving long-term services and "
                "supports were automatically enrolled in the BCBS HealthChoice "
                "Illinois MLTSS plan, and other members receive services in "
                "the HFS fee-for-service program. HFS also says a BCBS letter "
                "dated 3 November 2025, which told members they could stay in "
                "BCBS MMAI, &ldquo;should not have been sent by BCBS.&rdquo;</p>",
            ]),
            ("Who can join a FIDE SNP, and who cannot", [
                "<p>HFS&rsquo;s eligibility list requires &ldquo;Receiving full "
                "Illinois Medicaid benefits&rdquo; in the Aid to the Aged, "
                "Blind, and Disabled (AABD) or FamilyCare category, being 21 or "
                "older at enrolment, having Medicare Part A and Part B, living "
                "in the plan&rsquo;s service area, and being a United States "
                "citizen or lawfully present in the United States.</p>",
                "<p>HFS says a person is not eligible if they are under 21, "
                "receive developmental disability institutional services or "
                "take part in the HCBS waiver for Adults with Developmental "
                "Disabilities, are &ldquo;In the Medicaid Spend-down "
                "population,&rdquo; are in the Illinois Medicaid Breast and "
                "Cervical Cancer program, are enrolled in partial-benefit "
                "Medicaid programs, or receive Comprehensive Third Party "
                "Insurance. If your parent qualifies for Medicaid through "
                "spend-down, explained in "
                '<a href="/guides/illinois-medicaid-long-term-care/">How '
                "Illinois Medicaid pays for long-term care, and what spend-down "
                "means</a>, a FIDE SNP is not open to them.</p>",
            ]),
            ("If your parent is in a nursing home or on a waiver", [
                "<p>Care in a nursing facility, or under one of Illinois&rsquo;s "
                "Home and Community Based Services waivers, falls under what "
                "HFS calls long-term services and supports (LTSS); its managed "
                "care page says dual-eligible adults receiving certain of these "
                "services are &ldquo;referred to as the MLTSS population&rdquo;. "
                "HFS&rsquo;s enrolment page says members receiving LTSS "
                "&ldquo;must be enrolled in a HealthChoice IL Managed Long-Term "
                "Services and Support (MLTSS) plan&rdquo; for those services, "
                "and adds: &ldquo;Currently, to switch plans, members must call "
                "the HFS Client Enrollment Broker at 1-877-912-8880.&rdquo;</p>",
                "<p>This guide has not researched HealthChoice Illinois MLTSS "
                "plans themselves. Ask your parent&rsquo;s care coordinator, "
                "or the HFS Client Enrollment Broker, which plan your parent is "
                "in now and what changing it would mean.</p>",
            ]),
            ("How and when to enrol or switch", [
                "<p>HFS&rsquo;s enrolment page names three ways to enrol in a "
                "FIDE SNP: use the &ldquo;Find Plans Now&rdquo; tool on "
                "Medicare.gov and select &ldquo;Medicaid&rdquo; when asked if "
                "you get help with your Medicare health or drug costs; call "
                "the plan or visit its website; or call 1-800-MEDICARE "
                "(1-800-633-4227), TTY 1-877-486-2048.</p>",
                "<p>The Medicare <strong>Open Enrollment Period</strong> runs "
                "&ldquo;October 15 - December 7 of each year,&rdquo; and "
                "coverage chosen then starts on 1 January, as long as the plan "
                "gets the request by 7 December. Outside that window, HFS says "
                "&ldquo;members eligible for a FIDE SNP can enroll "
                "once-per-month in a FIDE SNP using the Integrated Care "
                "SEP,&rdquo; with coverage starting the first of the month "
                "after the plan gets the request. A separate Dual/LIS special "
                "enrolment period lets a dually eligible member go back to "
                "Original Medicare with a standalone prescription drug plan, or "
                "switch drug plans, once a month. HFS says these special "
                "enrolment periods &ldquo;won&rsquo;t allow enrollment into "
                "non-D-SNP Medicare Advantage Plans.&rdquo;</p>",
                "<p>For free help choosing a plan, see "
                '<a href="/guides/illinois-senior-health-insurance-program/">'
                "Who can help my parent choose a Medicare plan for free in "
                "Illinois?</a></p>",
            ]),
            ("What this guide could not verify", [
                "<p>HFS&rsquo;s pages give no premium, copay or other dollar "
                "figure for a FIDE SNP, so this guide does not publish one. "
                "Compare plans&rsquo; costs on Medicare.gov or with the plan "
                "itself. Several HFS pages still describe the change in the "
                "future tense, as written before it took effect; this guide "
                "reports what they say happened on 1 January 2026.</p>",
            ]),
            ("Where this fits with the rest of this site", [
                "<p>A FIDE SNP is one way a dually eligible parent&rsquo;s "
                "Medicare and Medicaid are delivered. Whether Illinois helps "
                "pay a Medicare premium at all is a separate question, covered "
                'in <a href="/guides/illinois-medicare-savings-program/">Can '
                "Illinois help pay my parent&rsquo;s Medicare premium?</a> If "
                "your parent gets home care through a dual eligible special "
                "needs plan and something is going wrong, "
                '<a href="/guides/illinois-home-care-ombudsman-program/">What '
                "to do when your parent&rsquo;s in-home care isn&rsquo;t "
                "working in Illinois</a> covers the free advocate.</p>",
                "<p>None of this decides what level of care your parent "
                "needs; a plan arranges and pays for care, it does not decide "
                'how much is right. The <a href="/">free six-question '
                "assessment</a> on this site walks through that. It asks for "
                "no name, no email and no phone number, and your answers never "
                "leave your device.</p>",
            ]),
        ],
    },

    {
        "slug": "illinois-assisted-living-involuntary-move-out",
        "bridge": ("Knowing the notice and appeal process is a different question "
               "from knowing whether your parent actually needs a higher level of "
               "care than this community can give."),
        "reviewed": "2026-11-23",
        "title": "Can an Illinois Assisted Living Make Your Parent Move Out?",
        "h1": "Can an Illinois assisted living make your parent move out, and how much notice must it give?",
        "desc": ("IDPH's form requires 30 days' written notice and a right to "
                 "appeal before an Illinois assisted living can end a stay. The "
                 "process, from the state's paperwork."),
        "intent": "worry / resident rights",
        "answer": ("<strong>Only through a formal process &mdash; not simply by "
                   "being asked to leave.</strong> The Illinois Department of "
                   "Public Health's own Involuntary Termination of Residency form "
                   "states that a <strong>30-day prior written notice</strong> "
                   "must go to the resident, the resident&rsquo;s representative, "
                   "or both, and to the long-term care ombudsman, and that a "
                   "resident who appeals the termination &ldquo;has the right to "
                   "continue to reside in the "
                   "establishment until a decision is rendered.&rdquo; The Illinois "
                   "Department on Aging&rsquo;s residents&rsquo; rights brochure, "
                   "which it says is &ldquo;appropriate for nursing homes and "
                   "assisted living&rdquo;, lists four reasons a facility can make "
                   "a resident leave &mdash; see below."),
        "sources": srcs("idph_al_itr_form", "idoa_ltc_rights_page", "idoa_resident_rights_brochure", "idph_al_div", "idoa_ombudsman", "idoa_ombudsman_contact"),
        "body": [
            ("What IDPH's own form requires before a move-out", [
                "<p>When a family searches for whether an Illinois assisted "
                "living or shared housing establishment can make a resident "
                "leave, the most direct answer is the state's own paperwork for "
                "it. The Illinois Department of Public Health (IDPH) publishes "
                "an <em>Assisted Living and Shared Housing Involuntary "
                "Termination of Residency</em> form, and the form itself states "
                "the rule in one sentence: &ldquo;A 30-day prior written notice "
                "must be provided to the resident, resident&rsquo;s "
                "representative, or both, and to the long-term care "
                "ombudsman.&rdquo; The same form adds: &ldquo;The establishment "
                "must notify the Illinois Department of Public Health when it "
                "initiates the termination process.&rdquo; So a termination is "
                "not a private matter between the resident "
                "and the establishment; the state is notified too.</p>",
                "<p>The form itself has a line the establishment must fill in, "
                "labelled &ldquo;Reason for Residency Termination&rdquo;. "
                "The Department on Aging&rsquo;s residents&rsquo; rights brochure "
                "adds that the written notice must include why the resident is "
                "being asked to move.</p>",
            ]),
            ("The right to appeal, and what happens while you wait", [
                "<p>The same IDPH form sets out exactly how a resident "
                "contests a termination: by calling IDPH's Division of "
                "Assisted Living at <strong>217-782-2448</strong>, or by "
                "sending a signed Appeal Hearing Request form to IDPH. The "
                "accompanying "
                "Hearing Request form gives the deadline in capital letters: "
                "&ldquo;Please submit completed forms within 10 DAYS after "
                "receiving the Involuntary Termination of Residency form from "
                "the facility.&rdquo;</p>",
                "<p>Filing on time matters, because of what the form says "
                "happens next: &ldquo;The resident has the right to continue to "
                "reside in the establishment until a decision is rendered.&rdquo; "
                "The Hearing Request form can be mailed or faxed to "
                "217-557-2432, to the Illinois Department of Public Health, "
                "Division of Assisted Living, 525 West Jefferson Street, 5th "
                "Floor, Springfield, Illinois 62761. The termination form also "
                "has a line naming the person at the establishment who will "
                "assist with relocation.</p>",
            ]),
            ("What reasons can be given", [
                "<p>The question families actually ask is broader than notice "
                "periods: can an establishment end a stay because a parent's "
                "care needs have grown? The Illinois Department on Aging's "
                "brochure <em>Residents&rsquo; Rights for People in Long-Term "
                "Care Facilities</em>, which the Department's residents' rights "
                "page describes as &ldquo;appropriate for nursing homes and "
                "assisted living&rdquo;, says a facility can make a resident "
                "leave because the bill has not been paid, the resident is "
                "dangerous to themselves or others, their medical needs cannot "
                "be met, or the facility closes.</p>",
                "<p>The full assisted living rules are in Part 295 of the "
                "Illinois Administrative Code, which IDPH's Assisted Living "
                "page links to as &ldquo;Assisted Living and Shared Housing - "
                "295 Administrative Code&rdquo;.</p>",
                "<p>Practically, that means: ask the establishment to point to "
                "the specific reason it wrote on your parent's notice, and call "
                "IDPH's Division of Assisted Living (217-782-2448) or the "
                "Long-Term Care Ombudsman Program to ask whether that reason "
                "matches a recognised ground for termination before deciding "
                "whether to appeal.</p>",
            ]),
            ("Your parent's broader rights as a resident", [
                "<p>The Illinois Department on Aging's page on residents' "
                "rights in long-term care facilities states that care facility "
                "residents keep certain rights, protections and privileges "
                "under both Illinois and federal law. The Long-Term Care "
                "Ombudsman Program &mdash; which "
                "the involuntary termination notice must also be sent to "
                "&mdash; is reached by calling the Department on Aging&rsquo;s "
                "<strong>Senior HelpLine at 1-800-252-8966 (711 TRS)</strong>, "
                "and the Department lists involuntary transfers or discharges "
                "among the reasons to contact an ombudsman.</p>",
            ]),
            ("Where this fits with the rest of this site", [
                "<p>This page covers assisted living and shared housing "
                "establishments specifically, which IDPH&rsquo;s Division of "
                "Assisted Living licenses, and whose notice and appeal forms are "
                "the ones described above. For the wider set of residents&rsquo; "
                "rights Illinois publishes for nursing homes and other care "
                "facilities, see "
                '<a href="/guides/illinois-nursing-home-resident-rights/">What '
                "rights does your parent have in an Illinois nursing home or "
                "care facility?</a> To report a live concern rather than "
                "appeal a termination notice, see "
                '<a href="/guides/illinois-care-facility-complaint/">How to '
                "report a problem at an Illinois care facility</a>.</p>",
                "<p>If a termination notice cites care needs your parent's "
                "current setting cannot meet, the "
                '<a href="/">free six-question assessment</a> on this site can '
                "help you think through what level of care fits now. It asks "
                "for no name, no email and no phone number, and your answers "
                "never leave your device.</p>",
            ]),
        ],
    },

    {
        "slug": "illinois-nursing-home-responsible-party",
        "bridge": ("Signing paperwork at admission is a different moment from "
               "knowing whether a nursing home is even the right level of care "
               "for your parent in the first place."),
        "reviewed": "2026-11-23",
        "title": "Should You Sign a Nursing Home Contract as Responsible Party?",
        "h1": "Should I sign my parent's nursing home admission contract as the responsible party?",
        "desc": ("Federal law bars a certified nursing home from making you "
                 "personally pay your parent's bill. What responsible-party "
                 "language can and cannot ask of you."),
        "intent": "worry / legal",
        "answer": ("<strong>Not as a personal guarantee of payment &mdash; and "
                   "a Medicare- or Medicaid-certified nursing home is not "
                   "allowed to make you.</strong> Federal "
                   "regulation 42 CFR 483.15(a)(3), which binds every Medicare- "
                   "or Medicaid-certified nursing facility, states the facility "
                   '&ldquo;must not request or require a third party guarantee '
                   "of payment to the facility as a condition of admission or "
                   "expedited admission, or continued stay in the "
                   "facility.&rdquo; Medicare's own consumer guide lists, among "
                   "things a nursing home isn&rsquo;t allowed to do: "
                   "&ldquo;Make a third party (like your family) pay your "
                   "nursing home bill.&rdquo; It may only ask a representative "
                   "with legal access to your parent&rsquo;s own money to use "
                   "that money to pay, and the Illinois Department on Aging&rsquo;s "
                   "residents&rsquo; rights brochure states a similar limit in "
                   "its own words."),
        "sources": srcs("cms_qso2514_nh", "medicare_nh_guide", "idoa_resident_rights_brochure"),
        "body": [
            ("The federal rule, in the regulation's own words", [
                "<p>The requirement sits in the Medicare and Medicaid "
                "requirements for participation every certified nursing facility "
                "must meet. CMS's current surveyor guidance (QSO-25-14-NH) "
                "quotes the regulation directly: &ldquo;The facility must not "
                "request or require a third party guarantee of payment to the "
                "facility as a condition of admission or expedited admission, "
                "or continued stay in the facility.&rdquo; The same guidance "
                "states plainly who that protects: &ldquo;The prohibition "
                "against third-party guarantees applies to all residents and "
                "prospective residents in all certified long term care "
                "facilities, regardless of payment source.&rdquo; Your "
                "parent's ability to private-pay does not remove this "
                "protection.</p>",
                "<p>What is still allowed is narrow and specific. CMS's "
                "guidance continues: &ldquo;the facility may request and "
                "require a resident representative with legal access to the "
                "resident&rsquo;s funds available to pay for facility care to "
                "access and use the resident&rsquo;s money or other assets to "
                "pay for care, as authorized by law. The facility may request "
                "and require this representative to sign a contract, without "
                "incurring personal liability, to provide the facility with "
                "payment from the resident&rsquo;s income or assets.&rdquo; "
                "That is a promise to pay from <em>your parent's</em> money if "
                "you control it &mdash; not a promise to pay from "
                "<em>yours</em>.</p>",
            ]),
            ("Language that counts as noncompliant, even without the word &ldquo;guarantee&rdquo;", [
                "<p>CMS's guidance is explicit that a facility cannot get "
                "around the rule by avoiding the word &ldquo;guarantee.&rdquo; "
                "It states: &ldquo;language can be noncompliant even if it does "
                "not specifically reference a &lsquo;guarantee&rsquo; by a "
                "third party. Any language contained in an agreement that "
                "seeks to hold a third party personally responsible for paying "
                "the facility would violate this requirement.&rdquo; The "
                "guidance lists examples of what that covers, including:</p>",
                "<ul class=\"res__list\">"
                "<li>Language that holds both the resident and a "
                "representative or other individual jointly responsible for "
                "sums due to the facility (naming the resident alone is "
                "allowed).</li>"
                "<li>Language that holds a representative personally liable "
                "for &ldquo;breach of an obligation in the agreement,&rdquo; "
                "such as not applying for Medicaid in time.</li>"
                "<li>Language that does not mention a guarantee but "
                "&ldquo;implies the resident could be discharged if the "
                "representative does not voluntarily agree to personally pay "
                "to prevent the discharge.&rdquo;</li>"
                "<li>Language that holds a representative personally liable "
                "for unpaid amounts because they did not supply accurate "
                "financial information or report a change in the "
                "resident&rsquo;s finances.</li></ul>",
                "<p>CMS's guidance also states this is not limited to the "
                "main admission agreement: noncompliant language is a problem "
                "&ldquo;if it appears in the main document that a facility "
                "uses as its admission agreement or in other documents that "
                "are signed at admission,&rdquo; and a facility &ldquo;cannot "
                "use such language in agreements regarding a resident&rsquo;s "
                "continued stay&rdquo; after admission either.</p>",
            ]),
            ("What Medicare tells families directly", [
                "<p>Medicare's own consumer guide, <em>Your Guide to Living in "
                "a Nursing Home</em>, puts the same rule in plain language "
                "under the heading &ldquo;Read your admission agreement "
                "carefully&rdquo;: &ldquo;You aren&rsquo;t required to agree "
                "to everything. For example, a nursing home isn&rsquo;t "
                "allowed to: Make a third party (like your family) pay your "
                "nursing home bill. It may only ask your family to use your "
                "money to pay the bills (if your family has legal access to "
                "your funds).&rdquo; The same guide also flags a separate "
                "clause worth watching for: a nursing home &ldquo;isn&rsquo;t "
                "allowed to&rdquo; require you to sign a binding-arbitration "
                "agreement, resolving disputes outside court, as a condition "
                "of admission or care.</p>",
                "<p>Medicare's practical advice if something in the agreement "
                "concerns you: &ldquo;cross out the item with a pen or marker "
                "before signing to show you don&rsquo;t agree.&rdquo; It also "
                "suggests asking a lawyer to review the agreement first, if "
                "you have one.</p>",
            ]),
            ("How Illinois's residents' rights brochure puts it", [
                "<p>Illinois&rsquo;s Department on Aging publishes a residents&rsquo; "
                "rights brochure for long-term care facilities that states "
                "the same protection in its own words, with a differently "
                "worded exception from the federal rule: &ldquo;Your facility must "
                "not require anyone else to sign an agreement stating they "
                "will pay for your bill unless they are your court appointed "
                "guardian.&rdquo; Notice the difference from the federal "
                "exception above: Illinois&rsquo;s brochure names a <strong>court "
                "appointed guardian</strong>, while the federal rule speaks "
                "more broadly of a representative with &ldquo;legal access&rdquo; "
                "to a resident's funds. This guide read both documents as "
                "written and is reporting that difference rather than "
                "resolving it &mdash; which one applies to a specific "
                "representative (an agent under a power of attorney, for "
                "example, versus a court-appointed guardian) is a question for "
                "the facility, the Long-Term Care Ombudsman, or an elder law "
                "attorney, not something this guide will guess at.</p>",
            ]),
            ("A gap this guide could not close: assisted living", [
                "<p>CMS&rsquo;s guidance says the federal rule above, 42 CFR "
                "483.15(a)(3), applies to &ldquo;all certified long term care "
                "facilities&rdquo;; none of the three sources this guide read "
                "addresses assisted living or shared housing contracts. This guide "
                "searched for an equivalent Illinois government page "
                "addressing responsible-party or guarantor language "
                "specifically in assisted living contracts and did not find "
                "one on an allowed host. If your parent is moving into "
                "assisted living rather than a nursing home, do not assume "
                "the same federal protection applies &mdash; read carefully any "
                "signature line that would make you a responsible party or "
                "guarantor, and ask the establishment "
                "in writing what liability it creates before signing.</p>",
            ]),
            ("Where this fits with the rest of this site", [
                "<p>This page is about one clause in an admission agreement, "
                "not the rest of a resident's rights once admitted. For the "
                "fuller list &mdash; money, privacy, discharge and grievances "
                "&mdash; see "
                '<a href="/guides/illinois-nursing-home-resident-rights/">What '
                "rights does your parent have in an Illinois nursing home or "
                "care facility?</a> For a decision about health care "
                "authority rather than payment, see "
                '<a href="/guides/illinois-advance-directive-power-of-attorney/">'
                "Does your parent need a power of attorney for health "
                "care?</a>, which covers a different kind of document "
                "entirely.</p>",
                "<p>If you are still weighing whether a nursing home is the "
                "right setting at all, the "
                '<a href="/">free six-question assessment</a> on this site '
                "walks through that separately. It asks for no name, no "
                "email and no phone number, and your answers never leave "
                "your device.</p>",
            ]),
        ],
    },
    {
        "slug": "illinois-medicaid-pending-nursing-home",
        "bridge": ("Getting the application decided is a different question from "
                   "knowing whether a nursing home is the right level of care for "
                   "your parent in the first place."),
        "reviewed": "2026-11-24",
        "title": "Medicaid Pending in an Illinois Nursing Home: Who Pays, How Long",
        "h1": "My parent is in an Illinois nursing home and Medicaid is still pending. What happens now?",
        "desc": ("How long Illinois has to decide a long-term care Medicaid "
                 "application, what Provisional Eligibility is, and what your "
                 "parent may owe while it is pending."),
        "intent": "admission / Medicaid",
        "answer": ("<strong>Illinois is meant to decide most long-term care "
                   "Medicaid applications within 45 days, and when the state "
                   "runs late, HFS can let the nursing home bill Medicaid before "
                   "the final decision.</strong> HFS calls this Provisional "
                   "Eligibility; its November 2023 notice states that "
                   "&ldquo;The Provisional Eligibility process will occur monthly "
                   "as long as eligibility determinations exceed the 45 day "
                   "threshold.&rdquo; Meanwhile, the HFS brochure for nursing "
                   "home applicants says eligibility &ldquo;usually begins with "
                   "the month you apply&rdquo; and can reach back up to three "
                   "months before it, and that your parent &ldquo;may also be "
                   "responsible to pay for some of your long term care "
                   "services.&rdquo;"),
        "sources": srcs("oag_ltc_2025", "hfs_pe_notice_2023", "hfs_pe_faq",
                        "hfs_3191", "hfs_abe_ltc_faq", "hfs_ltc_clients",
                        "idoa_resident_rights_brochure"),
        "body": [
            ("How long Illinois has to decide, and how long it really takes", [
                "<p>A parent who moves into a nursing home before Medicaid has "
                "approved them is often described as <em>Medicaid "
                "pending</em>. HFS&rsquo;s page for long-term care clients "
                "says that if you want the state to pay for nursing home care, "
                "you must apply for medical benefits through the Department of "
                "Human Services (DHS) and obtain a needs screening through the "
                "Department on Aging or DHS.</p>",
                "<p>The Illinois Auditor General&rsquo;s July 2025 audit of "
                "long-term care Medicaid decisions sets out the deadlines: "
                "under the federal rules and the Illinois Administrative Code, "
                "a decision is due within <strong>45 days</strong> for "
                "applicants who are not applying on the basis of a disability; "
                "for applicants who are, the federal limit is 90 days and "
                "Illinois sets 60. The audit also records that "
                "&ldquo;The applicant, his or her spouse, an approved "
                "representative, or the facility in which the applicant lives "
                "may request a 30-day extension to provide verification of "
                "current resources or resources transferred during the "
                "look-back period,&rdquo; and that a second 30-day extension "
                "may be allowed on request.</p>",
                "<p>In practice, the auditors tested a sample of 50 "
                "applications submitted in 2023 and found that 11 of them "
                "(22%) were pending past the required number of days. The "
                "report states: &ldquo;For the 50 applications "
                "sampled, it took on average 41 days from receipt of "
                "application to decision.&rdquo; Applications sent to the HFS "
                "Office of Inspector General for an asset investigation took "
                "longer: &ldquo;The applications that were referred to HFS OIG "
                "spent on average 58 days at the OIG.&rdquo;</p>",
            ]),
            ("Provisional Eligibility: what happens when the state is late", [
                "<p>HFS first set up Provisional Eligibility in 2018. Its "
                "provider notice of 27 November 2023 explains that delays grew "
                "again after the COVID-19 emergency ended, and that &ldquo;HFS "
                "has reimplemented the assignment of Provisional Eligibility "
                "for LTC applications which meet the criteria "
                "requirements.&rdquo; Citing the Public Aid Code, the notice "
                "states that &ldquo;individuals given Provisional Eligibility "
                "are entitled to receive the same services as individuals with "
                "regular Medicaid eligibility regardless of fee-for-service or "
                "Managed Care Organization (MCO) plan enrollment.&rdquo;</p>",
                "<p>HFS&rsquo;s questions-and-answers document on the process "
                "makes four points a family should know:</p>",
                "<ul class=\"res__list\">"
                "<li><strong>Nobody has to ask for it.</strong> &ldquo;Provisional "
                "Eligibility is not requested.&rdquo; HFS reviews applications "
                "and nursing home admissions pending more than 45 days each "
                "month.</li>"
                "<li><strong>Delays the family causes do not count.</strong> "
                "&ldquo;State delays in excess of 45 days in processing "
                "submission of a complete application do not include delays "
                "caused by incomplete applications or applicant requests for "
                "extensions in timeframes to submit required "
                "verifications.&rdquo;</li>"
                "<li><strong>A spend-down is not &lsquo;pending&rsquo;.</strong> "
                "&ldquo;Cases in resource spenddown status are not considered "
                "pending and will not be eligible for Provisional "
                "Eligibility.&rdquo;</li>"
                "<li><strong>It is not the final decision.</strong> DHS "
                "caseworkers continue to process the application, and the "
                "document states that &ldquo;Questions regarding the status of "
                "a pending Medicaid application should be sent to the "
                "appropriate DHS office.&rdquo;</li></ul>",
            ]),
            ("What your parent may owe while the application is pending", [
                "<p>The HFS brochure for people applying for nursing home "
                "coverage (HFS 3191, revised February 2015 and still linked "
                "from HFS&rsquo;s long-term care page) states that if the "
                "application is approved, &ldquo;your eligibility for medical "
                "benefits usually begins with the month you apply, as long as "
                "you meet all the eligibility requirements,&rdquo; and that "
                "&ldquo;you may be eligible for medical benefits for up to "
                "three months before the month you apply.&rdquo;</p>",
                "<p>The same brochure advises: &ldquo;If possible, do not pay "
                "your medical bills until you learn whether or not you are "
                "eligible for medical benefits from the state.&rdquo; It "
                "immediately adds that, depending on income and resources, it "
                "may be necessary to pay part of those bills, and that "
                "&ldquo;You may also be responsible to pay for some of your long "
                "term care services.&rdquo; Once a case is decided, "
                "&ldquo;Your local FCRC will tell you how much of your own money "
                "you will have to pay to the nursing home or SLF each "
                "month.&rdquo; (An FCRC is a DHS Family Community Resource "
                "Center.)</p>",
                "<p>None of the HFS pages read for this guide sets out what a "
                "nursing home may bill a resident while an application is "
                "pending. Ask the facility&rsquo;s business office to put in "
                "writing what it will charge each month until the decision, "
                "and what happens to any payment if Medicaid is later approved "
                "for those months. If the application is refused or a penalty "
                "period is imposed for gifts made in the five-year look-back, "
                "Medicaid will not pay for those months; "
                "<a href=\"/guides/illinois-medicaid-look-back-period/\">the "
                "look-back guide</a> explains how a penalty is worked out, and "
                "<a href=\"/guides/illinois-medicaid-long-term-care/\">the "
                "long-term care Medicaid guide</a> explains spend-down.</p>",
            ]),
            ("Contracts, guarantees and being asked to leave", [
                "<p>The Department on Aging&rsquo;s residents&rsquo; rights "
                "brochure states that a facility &ldquo;must not require anyone "
                "else to sign an agreement stating they will pay for your bill "
                "unless they are your court appointed guardian.&rdquo; Read any "
                "admission agreement before a family member signs it.</p>",
                "<p>The brochure lists an unpaid bill as one of four reasons a "
                "facility can make a resident leave, alongside danger to "
                "themselves or others, medical needs the facility cannot meet, "
                "and the facility closing. A written notice is required, and "
                "it must say why, explain how to appeal and include a "
                "self-addressed envelope to the Illinois Department of Public "
                "Health. A resident has the right to appeal within "
                "<strong>10 days</strong>, and the brochure says to call the "
                "Department on Aging at <strong>1-800-252-8966</strong> for help "
                "with an involuntary discharge notice. HFS&rsquo;s brochure adds "
                "that &ldquo;If you receive medical benefits, the nursing home "
                "cannot make you leave even if it decides to stop taking care of "
                "patients who receive medical benefits.&rdquo; "
                "<a href=\"/guides/illinois-nursing-home-resident-rights/\">The "
                "residents&rsquo; rights guide</a> covers the rest of the "
                "brochure.</p>",
            ]),
            ("Keeping the application moving", [
                "<p>Most of the delay a family can control is paperwork. HFS&rsquo;s "
                "long-term care application FAQ, written for facilities that file "
                "online, states: &ldquo;Yes, the application may be submitted "
                "without verifications. DHS caseworkers will attempt to verify "
                "income information electronically. If that is not possible, the "
                "caseworker will send a request for the information. An "
                "application cannot be processed without all necessary "
                "verifications.&rdquo;</p>",
                "<ul class=\"res__list\">"
                "<li>Find out who filed the application &mdash; the family or the "
                "nursing home &mdash; and the date it was entered, since HFS "
                "counts the 45 days for Provisional Eligibility from the date "
                "an application is entered online.</li>"
                "<li>Answer every caseworker request by its due date, and if "
                "bank or transfer records will take longer, ask for the 30-day "
                "extension in writing rather than letting the request lapse. "
                "Remember that an extension you ask for is not counted as a "
                "state delay.</li>"
                "<li>Make sure the needs screening has been done; "
                "<a href=\"/guides/illinois-nursing-home-preadmission-screening/\">the "
                "pre-admission screening guide</a> explains it.</li>"
                "<li>Ask the facility whether a pending application has passed "
                "45 days and been picked up for Provisional Eligibility.</li>"
                "</ul>",
            ]),
            ("Before your parent moves in", [
                "<p>If a move is still being planned, it is worth asking each "
                "nursing home how it handles a resident whose Medicaid "
                "application is pending, and asking for its answer in writing, "
                "before choosing. And if you are not yet sure a nursing home is "
                "the right level of care, the "
                "<a href=\"/\">free six-question assessment</a> on the home "
                "page can help you think it through before you apply.</p>",
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
        "desc": ("Volunteers trained by Illinois-contracted agencies help "
                 "older adults budget and pay bills, but only on two "
                 "eligibility paths and where a Program Site reaches."),
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
        "sources": srcs("idoa_money_mgmt", "idoa_money_mgmt_sites", "idoa_resident_rights_brochure"),
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
                "<p>The department's page describes a service, not a legal "
                "arrangement, and says nothing about how it relates to "
                "<a href=\"/guides/illinois-advance-directive-power-of-attorney/\">"
                "a power of attorney</a> or a guardianship. Local Program Sites "
                "recruit, select, train, match and monitor the volunteers; the "
                "department administers the programme and monitors the Program "
                "Sites.</p>",
            ]),
            ("Who qualifies &mdash; and where", [
                "<p>The department's page gives exactly two eligibility paths. "
                "The programme is &ldquo;available to Community Care Program "
                "(CCP) participants&rdquo; &mdash; see "
                '<a href="/guides/illinois-community-care-program/">Can my '
                "parent get paid help at home in Illinois?</a> for what CCP "
                "itself requires &mdash; or to &ldquo;individuals who have a "
                "substantiated Adult Protective Services (APS) case in certain "
                "areas of the State&rdquo;. For what Adult Protective Services investigates and how to report, see "
                '<a href="/guides/illinois-elder-abuse-reporting/">What to do '
                "about suspected elder abuse or neglect at home in "
                "Illinois</a>.</p>",
                "<p>Both paths carry the same catch: &ldquo;in certain areas of "
                "the State&rdquo; is doing real work in that sentence. This is "
                "not a programme every Illinois county runs &mdash; it operates through contracted local Program Sites, and whether "
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
                "family wondering how a parent's Social Security benefit gets managed: &ldquo;Volunteers also "
                "serve as Representative Payees, persons designated by the "
                "Social Security Administration to manage the monthly benefits "
                "of certain beneficiaries.&rdquo; That is the same role the "
                "Illinois Department on Aging's own resident-rights brochure "
                "warns a care facility may not take on &ldquo;without your "
                "permission&rdquo; &mdash; this programme is one way to have that role filled by a trained volunteer from a Program Site the department monitors.</p>",
            ]),
            ("What this guide could not verify, and will not guess at", [
                "<p>The department's page does not state what the programme "
                "costs a family, does not describe how a volunteer is screened beyond saying Program Sites &ldquo;recruit, select, train, match and monitor the volunteers&rdquo;, and does not explain what "
                "happens if a volunteer mishandles money beyond saying the "
                "department &ldquo;monitors&rdquo; Program Sites. This guide "
                "will not guess at a fee, a background-check standard, or a "
                "complaint process the page itself does not spell out. Ask the "
                "Program Site named for your area, or the Senior HelpLine, "
                "directly.</p>",
            ]),
            ("Is a Program Site actually near Evanston?", [
                "<p>The department publishes the current roster as a PDF, "
                "&ldquo;Find Your Local Program Site/Agency&rdquo;, organised by numbered PSA. The copy this "
                "guide read, dated 22 October 2026, lists two Program Sites under PSA 13: Kenneth W. Young Centers "
                "for Elk Grove and Schaumburg Townships, and Oak Park Township "
                "Senior Services for Oak Park and River Forest Townships. "
                "Neither covers Evanston Township, and this guide found no "
                "separate listing for the City of Chicago or the rest of Cook "
                "County on that document.</p>",
                "<p>That is a fact about one dated PDF, not a permanent answer. "
                "Program Site lists change, and the department's page itself tells families to contact their local Care Coordination Unit, found with its map tool, to find out if they are eligible. Call the Senior HelpLine at <strong>1-800-252-8966 "
                "(711 TRS)</strong> and ask directly whether a Program Site "
                "currently serves Evanston Township, rather than relying on "
                "either this guide or an out-of-date list found elsewhere.</p>",
            ]),
            ("How to find out, for your specific parent", [
                "<p>Start with your parent's local Care Coordination Unit, "
                "found through the department's map tool: the department's page "
                "says to contact it to learn more about this programme and find "
                "out if you are eligible. Ask there whether your parent's "
                "situation &mdash; already on CCP, or with a substantiated APS "
                "case &mdash; qualifies, and whether a Program Site reaches "
                "where your parent lives. The department's Senior HelpLine is "
                "<strong>1-800-252-8966 (711 TRS)</strong>.</p>",
            ]),
            ("Where this fits with the rest of this site", [
                "<p>This is a narrow tool for a narrow problem: bills going unpaid or a benefit cheque with nobody to manage it. If the honest picture "
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
        "slug": "illinois-parent-refuses-to-move-guardianship",
        "bridge": ("Whether the law lets you decide for your parent is a separate "
                   "question from what level of care your parent actually needs."),
        "reviewed": "2026-11-24",
        "title": "Parent Refuses to Move? Illinois Options and Guardianship",
        "h1": "My parent isn't safe at home but refuses to move. What can we do in Illinois?",
        "desc": ("Illinois presumes an adult can make their own decisions. What "
                 "the state's Guardianship and Advocacy Commission says to try "
                 "first, and when guardianship applies."),
        "intent": "decision / legal",
        "answer": ("<strong>In Illinois, an adult parent decides where they live "
                   "unless a court appoints a guardian.</strong> The state&rsquo;s "
                   "Guardianship and Advocacy Commission states that &ldquo;The "
                   "law presumes that an adult eighteen years of age or older is "
                   "capable of handling his/her own affairs,&rdquo; and that "
                   "&ldquo;In Illinois, the only way someone can be a guardian for "
                   "a person who is eighteen years old or older is to be appointed "
                   "by the circuit court.&rdquo; A guardian of the person can make "
                   "decisions about residential placement, but the Commission "
                   "calls guardianship a last resort and says that where possible, "
                   "alternatives should be pursued first."),
        "sources": srcs("gac_fact_sheet", "gac_faq", "idoa_aps_program"),
        "body": [
            ("Where Illinois law starts", [
                "<p>The Commission&rsquo;s Office of State Guardian is plain that "
                "age or illness alone is not enough: &ldquo;Without more, a "
                "mental, physical or developmental disability is not sufficient "
                "for the appointment of a guardian.&rdquo; Guardianship, its fact "
                "sheet says, &ldquo;is needed when a person is unable to make and "
                "communicate responsible decisions regarding his personal care or "
                "finances due to a mental, physical or developmental "
                "disability.&rdquo;</p>",
                "<p>A parent who makes a choice the family thinks is unwise has not "
                "met that test. The Commission&rsquo;s questions-and-answers page "
                "states: &ldquo;Making incorrect or ill-advised decisions on a "
                "periodic basis is not the test. Rather, it is an inability to "
                "engage in the decision making in the first place which is "
                "important.&rdquo; It suggests four practical questions:</p>",
                "<ul class=\"res__list\">"
                "<li>&ldquo;Does the person understand that a particular decision "
                "needs to be made?&rdquo;</li>"
                "<li>&ldquo;Does the person understand the options available in "
                "any decision?&rdquo;</li>"
                "<li>&ldquo;Does the person understand the consequences of each "
                "option?&rdquo;</li>"
                "<li>&ldquo;Is the person able to properly inform appropriate "
                "parties once the decision has been made?&rdquo;</li></ul>",
                "<p>The same page says that an inability to make sound decisions "
                "about matters including where to live and when to seek medical "
                "care is an indication that a person may need some guardianship "
                "services.</p>",
            ]),
            ("What the state says to try first", [
                "<p>The Commission states: &ldquo;All possible alternatives "
                "should be explored before instituting guardianship "
                "proceedings.&rdquo; It names representative or protective payees, "
                "financial counselling and bill-paying assistance programmes, "
                "living trusts, and homemaker and other in-home support programmes "
                "as ways that may avoid the need for guardianship.</p>",
                "<p>It also points to arrangements a parent can make while they "
                "still can. Under the Illinois Power of Attorney Act, the page "
                "says, a person can appoint an agent to make property or personal "
                "and health care decisions, and &ldquo;The execution of the form "
                "requires no court involvement, and forms are readily "
                "available.&rdquo; Under the Health Care Surrogate Act, a relative "
                "or friend can make some medical decisions for a person who lacks "
                "capacity without a court appointment. "
                "<a href=\"/guides/illinois-advance-directive-power-of-attorney/\">The "
                "power of attorney guide</a> covers those documents.</p>",
            ]),
            ("If you are worried about self-neglect", [
                "<p>When a parent living at home is not managing food, medicine or "
                "safety, the Illinois Department on Aging&rsquo;s Adult Protective "
                "Services programme is another route. Its page states that it "
                "&ldquo;investigates reports of abuse, neglect, exploitation, and "
                "self-neglect of adults age 60 or older, and adults age 18-59 with "
                "disabilities living in the community,&rdquo; and gives a "
                "statewide, 24-hour hotline: <strong>1-866-800-1409</strong>. "
                "<a href=\"/guides/illinois-elder-abuse-reporting/\">The elder "
                "abuse and neglect guide</a> explains what happens after a "
                "report.</p>",
            ]),
            ("What guardianship involves", [
                "<p>The fact sheet describes two kinds. A &ldquo;guardian of the "
                "person&rdquo; is appointed when someone cannot make or "
                "communicate responsible decisions about personal care, and "
                "&ldquo;This guardian will make decisions about medical treatment, "
                "residential placement, social services and other needs.&rdquo; A "
                "&ldquo;guardian of the estate&rdquo; handles money and property. "
                "Either can be <strong>limited</strong>, covering only the "
                "decisions the court specifies, or <strong>plenary</strong>, "
                "covering all of them.</p>",
                "<ul class=\"res__list\">"
                "<li><strong>The report.</strong> Before going to court, the "
                "Commission says, one must obtain a report certifying that the "
                "person is disabled and needs a guardian, signed by a licensed "
                "physician, based on evaluations performed within 3 months of "
                "filing and including a recommendation on the most suitable "
                "living arrangement.</li>"
                "<li><strong>The petition and hearing.</strong> An "
                "&ldquo;interested person&rdquo; files a petition in the circuit "
                "court of the county where your parent lives, and the fact sheet "
                "states: &ldquo;Guardianship hearings are set within 30 days of a "
                "petition being filed with the court.&rdquo;</li>"
                "<li><strong>Your parent&rsquo;s rights.</strong> &ldquo;A person "
                "facing a guardianship adjudication has the right to a court "
                "appointed attorney and a trial by a jury of six persons.&rdquo; "
                "Most counties also appoint a guardian ad litem to advise the "
                "court independently.</li>"
                "<li><strong>Emergencies.</strong> A temporary guardian can be "
                "appointed while the case is pending, and the fact sheet says "
                "temporary guardianship &ldquo;lasts no longer than 60 "
                "days&rdquo; and is used &ldquo;only where a demonstrated harm or "
                "emergency exists.&rdquo;</li>"
                "<li><strong>Time and cost.</strong> &ldquo;Once the case is "
                "filed, it usually takes from 14 days to two months for a decision "
                "to be reached by the court.&rdquo; The petitioner usually pays "
                "filing fees, sheriff&rsquo;s fees for serving the summons, and "
                "attorney&rsquo;s fees; the fact sheet adds that "
                "&ldquo;Guardianship can be costly and complicated.&rdquo;</li>"
                "<li><strong>Who serves.</strong> &ldquo;Family members are not "
                "automatically named the legal guardian for their disabled "
                "relative.&rdquo; The judge decides. The Office of State Guardian "
                "serves only when no other suitable person is willing.</li></ul>",
                "<p>For Cook County, the Commission notes that the rules are in "
                "Part 12 of the general rules of practice for the Circuit Court of "
                "Cook County, and that the Probate Court Clerk can usually supply the "
                "physician&rsquo;s report form. The Office of State Guardian&rsquo;s "
                "toll-free intake number is <strong>1-866-274-8023</strong>.</p>",
            ]),
            ("Before you file", [
                "<p>The fact sheet ends with a warning worth reading twice: "
                "guardianship &ldquo;should never be used in a retaliatory manner "
                "or as a convenience for a health care provider or a family "
                "member.&rdquo; The Commission also says that once established, a "
                "guardianship can be extremely difficult to revoke. Talking to an "
                "attorney before filing is sensible; the Commission says an Office "
                "of State Guardian attorney or a legal assistance agency can be "
                "consulted by a family filing without one.</p>",
                "<p>Often the more useful first step is a calm conversation about "
                "what kind of help would actually make home safe, or which kind of "
                "setting would. If you are trying to work that out, the "
                "<a href=\"/\">free six-question assessment</a> on the home page "
                "is a private place to start.</p>",
            ]),
        ],
    },
    {
        "slug": "medicare-fast-appeal-hospital-rehab-discharge",
        "bridge": ("Winning a few more covered days is a different question from "
               "knowing what level of care your parent will need once those days "
               "run out."),
        "reviewed": "2026-11-23",
        "title": "Discharged Too Soon? How a Medicare Fast Appeal Works",
        "h1": "My parent is being discharged from the hospital or from rehab too soon. Can we appeal?",
        "desc": ("Medicare gives patients leaving a hospital or a skilled nursing "
                 "(rehab) stay the right to a fast appeal: the two notices, the "
                 "deadlines and who pays."),
        "intent": "deadline / Medicare",
        "answer": ("<strong>Yes, if Medicare is paying for the stay, you can ask "
                   "for a fast appeal &mdash; but the deadline is short.</strong> "
                   "Medicare.gov states you &ldquo;may have the right to ask for a "
                   "fast appeal if you think your services are ending too soon (or "
                   "that you&rsquo;re being discharged too soon)&rdquo; from a "
                   "hospital, a skilled nursing facility and three other kinds of "
                   "provider. An independent reviewer, the Beneficiary and Family "
                   "Centered Care-Quality Improvement Organization (BFCC-QIO), "
                   "decides. In a hospital the request is due &ldquo;no later than "
                   "the day you&rsquo;re scheduled to be discharged from the "
                   "hospital&rdquo;; in a skilled nursing facility, &ldquo;no later "
                   "than noon the day before the termination date listed on the "
                   "notice.&rdquo; The notice your parent is given tells you how to "
                   "ask."),
        "sources": srcs("medicare_fast_appeals", "medicare_discharge_checklist"),
        "body": [
            ("Two settings, two notices", [
                "<p>Everything turns on a written notice, and which one your "
                "parent should receive depends on where they are.</p>",
                "<ul class=\"res__list\">"
                "<li><strong>In a hospital:</strong> Medicare.gov states that "
                "within 2 days of admission and before discharge, a patient "
                "should get a notice called &ldquo;An Important Message from "
                "Medicare about Your Rights,&rdquo; which it says &ldquo;is "
                "sometimes called the Important Message from Medicare or the "
                "IM.&rdquo; If the hospital gave it more than 2 days before the "
                "discharge day, the page states the hospital &ldquo;must give you "
                "a copy of your original, signed IM or give you a new one (that "
                "you must sign) before you&rsquo;re discharged.&rdquo;</li>"
                "<li><strong>In a skilled nursing facility (and with home health, "
                "hospice or a comprehensive outpatient rehabilitation "
                "facility):</strong> the notice is called the &ldquo;Notice of "
                "Medicare Non-Coverage,&rdquo; and Medicare.gov states you should "
                "get it &ldquo;at least 2 days before covered services "
                "end.&rdquo;</li></ul>",
                "<p>For both, Medicare.gov's instruction is the same: &ldquo;If "
                "you don&rsquo;t get this notice, ask for it.&rdquo; Medicare's "
                "discharge planning checklist adds: &ldquo;Read the notice "
                "carefully because it contains information about your fast appeal "
                "rights.&rdquo; Both notices include, where it applies, the date "
                "your parent's covered services will end; in a skilled nursing "
                "facility the deadline below is counted from that date, and in a "
                "hospital from the day your parent is scheduled to be "
                "discharged.</p>",
            ]),
            ("The deadlines, in Medicare's own words", [
                "<p><strong>Hospital.</strong> Follow the directions on the "
                "Important Message from Medicare &ldquo;no later than the day "
                "you&rsquo;re scheduled to be discharged from the hospital.&rdquo; "
                "Medicare.gov then states: &ldquo;If you ask for your appeal "
                "within this time frame, you can stay in the hospital while you "
                "wait to get the BFCC-QIO&rsquo;s decision. You won&rsquo;t have "
                "to pay for your stay (except for applicable coinsurance or "
                "deductibles).&rdquo; Miss it, and a late request is still "
                "possible: &ldquo;If you miss the deadline for a fast appeal, you "
                "can still ask the BFCC-QIO to review your case, but different "
                "rules and time frames apply, and you might be responsible for the "
                "cost of the hospital stay past the original day the hospital "
                "tries to discharge you.&rdquo; If the hospital deadline has "
                "passed, call the BFCC-QIO named on the notice straight away.</p>",
                "<p><strong>Skilled nursing facility (rehab).</strong> Follow the "
                "instructions on the Notice of Medicare Non-Coverage &ldquo;no "
                "later than noon the day before the termination date listed on "
                "the notice.&rdquo; If that deadline is missed and your parent "
                "is in a Medicare health plan, such as a Medicare Advantage Plan, "
                "Medicare.gov states &ldquo;you can request "
                "a fast reconsideration from your plan, but services will only be "
                "covered if there&rsquo;s a decision issued in your favor.&rdquo; "
                "The page does not say what applies after a missed deadline with "
                "Original Medicare: ask the BFCC-QIO named on the notice, or "
                "1-800-MEDICARE, straight away.</p>",
                "<p>Right after its warning about a missed hospital deadline, "
                "Medicare.gov adds, for a parent in a Medicare Advantage Plan: "
                "&ldquo;you can ask your plan for an "
                "appeal, but different rules apply.&rdquo; Read the notice your "
                "parent was given, and ask the plan which route applies before "
                "the deadline passes.</p>",
            ]),
            ("Who to call", [
                "<p>The appeal goes to the BFCC-QIO, which Medicare's checklist "
                "describes as &ldquo;an independent reviewer under contract with "
                "Medicare.&rdquo; The notice itself carries the contact details. "
                "Medicare.gov states the BFCC-QIO &ldquo;is administered for "
                "Medicare by Commence or Acentra, depending on what state you live "
                "in,&rdquo; and the checklist adds: &ldquo;You can also call "
                "1-800-MEDICARE to get the phone number for your BFCC-QIO.&rdquo; "
                "This guide does not print a number for Illinois: use the one on "
                "your parent's notice, or the one 1-800-MEDICARE gives you.</p>",
            ]),
            ("What happens after you call", [
                "<p>Medicare.gov describes the same sequence in both settings, "
                "with different timing:</p>",
                "<ul class=\"res__list\">"
                "<li>The BFCC-QIO notifies the hospital (and your parent's plan, if "
                "they have a Medicare health plan) or the facility.</li>"
                "<li>The provider gives your parent a detailed written "
                "explanation: in a hospital a &ldquo;Detailed Notice of "
                "Discharge,&rdquo; by noon the day after the hospital is "
                "notified; elsewhere a &ldquo;Detailed Explanation of "
                "Non-Coverage,&rdquo; by the end of the day the provider is "
                "notified. Both state why the services are no longer covered and "
                "the coverage rule being applied.</li>"
                "<li>The BFCC-QIO asks why you believe coverage should continue "
                "and looks at the medical records.</li>"
                "<li>It decides: in a hospital &ldquo;Within one day of getting "
                "the requested information&rdquo;; elsewhere &ldquo;By close of "
                "business the day after it gets the information it needs to make "
                "a decision.&rdquo;</li></ul>",
                "<p>Medicare.gov also states: &ldquo;You can also ask for copies of "
                "any of the materials that were sent to the BFCC-QIO.&rdquo;</p>",
            ]),
            ("What the decision means for the bill", [
                "<p><strong>If the reviewer agrees services are ending too "
                "soon:</strong> in a hospital, for a parent with Original "
                "Medicare, Medicare.gov states Medicare &ldquo;will continue to "
                "cover your hospital stay as long as medically necessary (except "
                "for applicable coinsurance or deductibles).&rdquo; For a parent "
                "in a Medicare health plan, such as a Medicare Advantage Plan, the "
                "page attaches a condition to the same hospital rule: Medicare "
                "will continue to cover the stay as long as medically necessary "
                "&ldquo;if your plan previously authorized coverage of the "
                "inpatient admission,&rdquo; or if the admission was for emergency "
                "care or the other kind of care the page names beside it. Where "
                "neither applies, it states that you &ldquo;may need to appeal the "
                "denial of coverage for your plan to pay&rdquo;. Ask the plan "
                "which applies to your parent&rsquo;s admission. In a skilled "
                "nursing facility, the page is more guarded: &ldquo;Depending on "
                "your care needs, Medicare may continue to cover&rdquo; the "
                "care.</p>",
                "<p><strong>If the reviewer agrees services should end:</strong> "
                "in a hospital, provided the deadline was met, Medicare.gov "
                "states &ldquo;you won&rsquo;t be responsible for paying the "
                "hospital charges (except for applicable coinsurance or "
                "deductibles) incurred through noon of the day after the BFCC-QIO "
                "gives you its decision.&rdquo; In a skilled nursing facility: "
                "&ldquo;You won&rsquo;t be responsible for paying for any SNF, "
                "HHA, CORF, or hospice services provided before the coverage end "
                "date on the &lsquo;Notice of Medicare Non-Coverage.&rsquo; If you "
                "continue to get services after the coverage end date, you may "
                "have to pay for those services.&rdquo;</p>",
                "<p>Read that before deciding whether your parent stays on while "
                "the appeal is decided: in a skilled nursing facility, a lost "
                "appeal leaves the days after the end date on the notice "
                "potentially your parent's to pay.</p>",
            ]),
            ("A different problem: inpatient changed to observation", [
                "<p>Medicare.gov describes a separate case: &ldquo;You can ask for "
                "a fast appeal while you&rsquo;re still in the hospital if you "
                "were admitted to the hospital as an inpatient and the hospital "
                "changed your status to &lsquo;outpatient getting observation "
                "services.&rsquo;&rdquo; It points to a separate appeal process "
                "for that. See "
                '<a href="/guides/does-medicare-pay-for-senior-care/">Does '
                "Medicare pay for assisted living or nursing home care?</a> for "
                "what Medicare covers after a hospital stay, and what it never "
                "covers.</p>",
            ]),
            ("Where this fits with the rest of this site", [
                "<p>A fast appeal can buy time; it does not answer where your "
                "parent will live and get care afterwards. Medicare's discharge "
                "checklist suggests asking &ldquo;where you&rsquo;ll get care "
                "after you&rsquo;re discharged&rdquo; and whether you have options "
                "&ldquo;(like home health care)&rdquo; &mdash; see "
                '<a href="/guides/medicare-home-health-care/">Medicare home health '
                "care</a> for that route, and "
                '<a href="/guides/levels-of-senior-care-explained/">the levels of '
                "senior care</a> for the others. For free, unbiased help with "
                "Medicare questions, see "
                '<a href="/guides/illinois-senior-health-insurance-program/">'
                "Illinois&rsquo;s Senior Health Insurance Program</a>.</p>",
                "<p>If you are deciding what comes after the discharge, the "
                '<a href="/">free six-question assessment</a> on this site '
                "looks at that question directly. It asks for no name, no email "
                "and no phone number, and your answers never leave your "
                "device.</p>",
            ]),
        ],
    },
    {
        "slug": "va-home-based-primary-care-and-aide",
        "bridge": ("Knowing which VA programme sends help to the house is a "
               "different question from knowing whether a house, even with "
               "help, is still the safest place for your veteran parent."),
        "reviewed": "2026-11-23",
        "title": "VA Home-Based Primary Care and Home Health Aide Care, Explained",
        "h1": "Can the VA send a doctor or a home health aide to your veteran&rsquo;s house?",
        "desc": ("VA.gov names two separate home programmes for an eligible "
                 "veteran: a medical team that visits for ongoing care, and "
                 "a trained aide for daily activities."),
        "intent": "benefits question",
        "answer": ("<strong>Yes &mdash; VA runs two separate home programmes, "
                   "and they are not the same thing.</strong> <strong>Home "
                   "Based Primary Care</strong> sends a VA team of health care professionals to the veteran's own home, including primary care visits by a physician, nurse practitioner or physician assistant. "
                   "<strong>Homemaker and Home Health Aide Care</strong> "
                   "sends a trained aide, supervised by a registered nurse, "
                   "to help with daily activities such as bathing, dressing "
                   "and grocery shopping. For both, the veteran must be enrolled in VA health care, meet the clinical need or criteria for the service, and the service must be available. The aide programme adds one more condition: the veteran must also be eligible for community care."),
        "sources": srcs("va_hbpc", "va_hhha", "va_ltc_overview", "va_phcbs_notice", "va_vdc", "va_caregiver_compare"),
        "body": [
            ("Two different kinds of help, not one", [
                "<p>VA.gov's own overview of its long-term care services "
                "lists five things under &ldquo;Services at Home and in the "
                "Community&rdquo;, available to &ldquo;all enrolled "
                "Veterans&rdquo; who have a clinical need and local "
                "availability: Geriatric Evaluation, Adult Day Health Care, "
                "Homemaker and Home Health Aide Care, Respite Care, and "
                "Skilled Home Health Care. That overview page names Homemaker and Home Health Aide Care without describing it, and does not list Home Based Primary Care at all. This guide read VA's own dedicated pages for each "
                "one instead of guessing.</p>",
                "<p>The two are easy to confuse because both send someone to "
                "the house, but they are different services with different "
                "staff. One is <strong>medical care from a VA clinical "
                "team</strong>. The other is <strong>personal-care help from "
                "a trained aide</strong>. A veteran parent could plausibly "
                "need either, both, or neither &mdash; this guide covers "
                "each on its own terms below.</p>",
            ]),
            ("Home Based Primary Care, in VA.gov's own words", [
                "<p>VA.gov describes Home Based Primary Care (HBPC) as "
                "&ldquo;health care services provided to Veterans in their "
                "home&rdquo;, aimed at veterans who need team-based in-home support for &ldquo;ongoing diseases and illnesses that affect their health and daily activities&rdquo;. The "
                "page is explicit that a veteran does not have to be "
                "homebound to qualify &mdash; it also names veterans who are "
                "isolated, or whose caregiver is under strain, as people the "
                "programme is meant to serve.</p>",
                "<p>A team reviews the veteran's needs and provides care for "
                "the veteran and the caregiver together. The page lists "
                "in-home primary care visits from a physician, nurse "
                "practitioner or physician assistant, plus care management, "
                "social work, rehabilitation, psychology, nutrition and "
                "pharmacy support.</p>",
                "<p>On cost, the page says a basic copay may apply each time a VA staff team member comes to the home for a medical visit, &ldquo;the same as if you went to a VA clinic&rdquo;, "
                "based on the veteran's service-connected disability status "
                "and financial information &mdash; it gives no dollar "
                "figure. It points families toward a VA social worker or "
                "case manager and the Application for Extended Care "
                "Benefits, VA Form 10-10EC, to learn the amount of the copay, rather than describing a separate HBPC application of its own.</p>",
            ]),
            ("Homemaker and Home Health Aide Care, in VA.gov's own words", [
                "<p>VA.gov's page states the eligibility rule in one line: "
                "&ldquo;All enrolled Veterans are eligible for Homemaker "
                "Home Health Aide Care&rdquo; if they are also eligible for "
                "community care, meet the clinical criteria, and the "
                "service is available where they live. It serves veterans "
                "&ldquo;of any age&rdquo;, including those who are isolated "
                "or whose caregiver is under strain &mdash; the same framing "
                "HBPC uses.</p>",
                "<p>The aide is not a nurse. VA.gov is specific that a "
                "registered nurse supervises the aide, who comes to help the veteran &ldquo;take care of themselves and their daily activities&rdquo;: eating, "
                "dressing, grooming, bathing, toileting, moving between "
                "places, and grocery shopping. &ldquo;Services are based on "
                "your assessed needs&rdquo;, the page says, and a visit "
                "schedule can run from several times a week to "
                "occasionally, continuing &ldquo;for as long as you need extra help with your daily activities&rdquo;.</p>",
                "<p>A copay &ldquo;may be charged based on your VA "
                "service-connected disability status&rdquo;, again with no "
                "dollar figure published. The page does not compare this "
                "programme with hiring a caregiver privately; it only says "
                "the aide works for an organisation that holds a contract "
                "with VA, which is the one fact this guide found distinguishing "
                "it from a family hiring someone itself.</p>",
            ]),
            ("Similar gates, with one real difference", [
                "<p>Both pages require enrollment in VA health care, a clinical need for the specific service, and local availability; the aide page adds a fourth condition. Neither page "
                "promises the service exists at every VA medical centre "
                "&mdash; both say availability depends on where the veteran "
                "lives, and point to a VA social worker or physician to "
                "confirm it locally rather than assuming a name found on a "
                "website applies everywhere.</p>",
                "<p>One wording difference is worth noticing rather than "
                "flattening: the Homemaker and Home Health Aide page adds "
                "that the veteran must be &ldquo;eligible for community "
                "care&rdquo;, a phrase the Home Based Primary Care page does "
                "not use. VA&rsquo;s own policy notice on purchased home and community-based services (VHA Notice 2024-01), linked from the aide page, explains it: homemaker and home health aide care is one of the purchased home and community-based services (PHCBS) it covers, and &ldquo;To receive PHCBS care, Veterans must satisfy one of the eligibility criteria for the Veterans Community Care Program established by the VA MISSION Act of 2018&rdquo;. Home Based Primary Care visits are made by VA&rsquo;s own staff team. Ask the VA social worker handling the case whether the veteran meets the community care criteria.</p>",
            ]),
            ("Not Veteran Directed Care, and not the caregiver stipend", [
                "<p>Two other VA programmes, covered separately on this site, also involve help at home, and "
                "it is worth being precise about how all four differ. "
                '<a href="/guides/va-veteran-directed-care-program/">Veteran '
                "Directed Care</a> hands the veteran a budget and lets them "
                "hire their own worker, including a family member. Home "
                "Based Primary Care and Homemaker and Home Health Aide Care, "
                "by contrast, are both VA-arranged: a VA team or a "
                "VA-contracted aide comes to the veteran, rather than the "
                "veteran directing their own hire.</p>",
                "<p>Separately again, "
                '<a href="/guides/va-caregiver-support-program/">the VA '
                "caregiver programmes</a> support the family member doing the caring, and one of them, the Program of Comprehensive Assistance for Family Caregivers, pays an eligible primary family caregiver a monthly stipend. Neither involves an outside aide or clinician visiting the veteran. Both VA pages say their service &ldquo;can be used in combination with other Home and Community Based Services&rdquo;. Ask the VA social worker which combination fits the veteran's assessed needs.</p>",
            ]),
            ("What this guide could not verify", [
                "<p>Neither VA.gov page this guide read gives a dollar "
                "copay figure, a typical visit frequency, or a maximum "
                "number of aide hours. Both describe "
                "the amount and shape of help as set by an individual "
                "clinical assessment, not a published rate. This guide will "
                "not invent a number neither page states &mdash; ask the VA "
                "social worker handling the case what the assessed plan "
                "would actually look like.</p>",
            ]),
            ("How to start", [
                "<p>Both pages point to the same first step: talk to a VA "
                "social worker or case manager. For Home Based Primary Care, the page says to contact a VA social worker or case manager to complete the Application for Extended Care Benefits, VA Form 10-10EC, to learn the amount of the copay, and that a VA physician or social worker can say whether the programme is available locally. For Homemaker and "
                "Home Health Aide Care, VA.gov simply says: &ldquo;Talk "
                "with a VA social worker to find out what specific help you "
                "may be able to receive&rdquo;, and mentions a Veteran "
                "Decision Aid and a Caregiver Self-Assessment as tools that "
                "can help weigh the options first.</p>",
                "<p>A veteran who is not yet enrolled in VA health care has "
                "to clear that step before either programme applies. "
                '<a href="/guides/va-veteran-directed-care-program/">This '
                "site's guide to Veteran Directed Care</a> sets out the ways "
                "to apply for VA health care itself, since the enrollment "
                "step is identical across all of VA's home programmes.</p>",
            ]),
            ("Where this fits with the rest of this site", [
                "<p>If the open question is money rather than who shows up "
                "at the house, see "
                '<a href="/guides/va-aid-and-attendance-benefit/">Does the '
                "VA pay for senior care? Aid and Attendance, explained</a>, "
                "a cash pension benefit that is separate from everything on "
                "this page. If a facility, rather than help at home, has "
                "become the real question, see "
                '<a href="/guides/va-nursing-home-and-respite-care/">Can the '
                "VA provide nursing home care, or give a family caregiver a "
                "break?</a></p>",
                "<p>If the real question is whether home, even with "
                "clinical or aide support, is still the right setting for "
                'your veteran parent, the <a href="/">free six-question '
                "assessment</a> on this site walks through that separately. "
                "It asks for no name, no email and no phone number, and "
                "your answers never leave your device.</p>",
            ]),
        ],
    },
    {
        "slug": "long-term-care-insurance-assisted-living-illinois",
        "bridge": ("Whether a policy will pay is a separate question from which "
                   "level of care your parent actually needs now."),
        "reviewed": "2026-11-25",
        "title": "Long-Term Care Insurance and Assisted Living in Illinois",
        "h1": "My parent has long-term care insurance. Will it pay for assisted living?",
        "desc": ("Benefit triggers, the elimination period, facility rules and "
                 "what to do if a claim stalls, read off the Illinois Department "
                 "of Insurance."),
        "intent": "paying / insurance",
        "answer": ("<strong>It can, if the policy covers assisted living, your "
                   "parent meets its benefit triggers and the elimination period "
                   "has run.</strong> The Illinois Department of Insurance lists "
                   "&ldquo;care in an assisted living facility&rdquo; among "
                   "long-term care services, and states that &ldquo;Long-term care "
                   "insurance will pay for some or all of your long-term care.&rdquo; "
                   "Whether it pays for your parent depends on the words of "
                   "their own policy, so the first step is to find it and read "
                   "three parts: who qualifies, where care is covered and when "
                   "payments start."),
        "sources": srcs("idoi_ltc", "ship_ltc_shoppers_guide", "idoi_complaints", "ship_ltc", "hfs_slp"),
        "body": [
            ("Start with the policy, not the sales brochure", [
                "<p>The Department of Insurance tells policyholders to read the "
                "policy and make certain they understand it, and adds: &ldquo;If "
                "you have questions about your insurance policy, contact your "
                "insurance agent for clarification. If you still have questions, "
                "turn to your state insurance department or insurance counseling "
                "program.&rdquo; It also states that &ldquo;Medicare, Medicare "
                "supplement insurance and health insurance you may have at work "
                "usually will not pay for long-term care,&rdquo; so a long-term "
                "care policy is a separate document from your parent&rsquo;s "
                "Medicare card or supplement.</p>",
                "<p>The rest of this guide draws on the National Association of "
                "Insurance Commissioners&rsquo; <em>Shopper&rsquo;s Guide to "
                "Long-Term Care Insurance</em> (revised 2019), which the Illinois "
                "Department on Aging posts on its SHIP pages. It describes how "
                "policies are commonly written, not what your parent&rsquo;s "
                "policy says. Where the two differ, the policy decides.</p>",
            ]),
            ("Does the policy cover assisted living at all?", [
                "<p>Policies differ on where care is covered. The Shopper&rsquo;s "
                "Guide warns: &ldquo;If you&rsquo;re not in the right type of "
                "facility (described in your policy), the insurance company can "
                "refuse to pay for your care.&rdquo; Some policies pay in any "
                "state-licensed facility, some only in certain ones, and some list "
                "facilities they exclude. It adds that &ldquo;many states, "
                "companies and policies define assisted living facilities "
                "differently,&rdquo; and that if a policy lists kinds of facilities "
                "you should check whether it requires the facility to have a "
                "license or certification from a government agency.</p>",
                "<p>Before a move, ask the insurer in writing whether the "
                "community you are considering meets the policy&rsquo;s "
                "definition, and ask the community for its Illinois licence "
                "details to send with the question. The guide advises checking "
                "with the insurance company before making plans for care.</p>",
            ]),
            ("Does your parent meet the benefit triggers?", [
                "<p>&ldquo;Benefit triggers&rdquo; are how the insurer decides "
                "your parent is eligible. The guide says to look for the section "
                "the policy calls &ldquo;Eligibility for the Payment of "
                "Benefits&rdquo; or &ldquo;Eligibility for Benefits.&rdquo; It "
                "describes three kinds:</p>",
                "<ul class=\"res__list\">"
                "<li><strong>Help with daily activities.</strong> The most common "
                "test, the guide says, is that &ldquo;you are expected to be unable "
                "to do two ADLs without human assistance for 90 days. Most "
                "policies use six ADLs: bathing; continence; dressing; eating; "
                "toileting; and transferring.&rdquo; Some policies require "
                "hands-on help with the activity; others count stand-by help from "
                "someone nearby. Which one your parent&rsquo;s policy uses "
                "matters when you describe their needs.</li>"
                "<li><strong>Cognitive impairment.</strong> &ldquo;Coverage of "
                "cognitive impairment is especially important if you develop "
                "Alzheimer&rsquo;s disease or other dementia.&rdquo;</li>"
                "<li><strong>A doctor&rsquo;s certification.</strong> Some "
                "policies require a doctor to order or certify that care is "
                "medically necessary; the guide notes that tax-qualified policies "
                "cannot use this trigger.</li></ul>",
                "<p>Keep copies of the doctor&rsquo;s notes, any assessment a "
                "community has done and a plain record of the help your parent "
                "needs each day: they are the evidence you can offer against "
                "whichever test the policy uses.</p>",
            ]),
            ("When payments start: the elimination period", [
                "<p>Many policies do not pay from the first day. The Shopper&rsquo;s "
                "Guide states that the elimination period &ldquo;can be 20, 30, 60, "
                "90 or 100 days before benefits begin,&rdquo; and that &ldquo;you "
                "must pay for your own care during the elimination period before "
                "benefits can begin. Companies don&rsquo;t pay for care provided by "
                "family members during or after the elimination period.&rdquo;</p>",
                "<p>How the days are counted matters. Under a calendar-day method, "
                "every day your parent meets the triggers counts, though the guide "
                "notes that &ldquo;many coverages will not start counting those "
                "days until you incur costs.&rdquo; Under the other method, "
                "&ldquo;only the days that you pay for professional care services "
                "covered by the policy count toward the elimination period.&rdquo; "
                "Ask the insurer which method applies, whether days already spent "
                "with paid help at home count, and, in the guide&rsquo;s words, "
                "&ldquo;if the insurance company requires another elimination "
                "period for a second stay.&rdquo;</p>",
                "<p>Budget for the elimination period as a private-pay stretch. "
                "<a href=\"/guides/assisted-living-cost-illinois/\">The assisted "
                "living cost guide</a> gives the published monthly figures for "
                "Illinois.</p>",
            ]),
            ("Two policy features to check on day one", [
                "<ul class=\"res__list\">"
                "<li><strong>Waiver of premium.</strong> &ldquo;Premium waiver "
                "lets you stop paying the premium once you&rsquo;re eligible and "
                "the insurance company starts to pay benefits.&rdquo; The guide "
                "adds: &ldquo;Some companies waive the premium as soon as they make "
                "the first benefit payment. Others wait until you&rsquo;ve received "
                "benefits for 60 to 90 days.&rdquo; Keep paying until the insurer "
                "confirms in writing that the premium is waived.</li>"
                "<li><strong>Third-party notice.</strong> A policyholder can name "
                "someone the insurer must contact before coverage ends for unpaid "
                "premiums. The guide explains why: &ldquo;Without this notice, "
                "people with cognitive impairments who forget to pay the premium "
                "might lose their coverage when they need it the most.&rdquo; If "
                "your parent has not named you, ask the insurer how to add a "
                "contact.</li></ul>",
            ]),
            ("If the claim stalls or is refused", [
                "<p>The Department of Insurance&rsquo;s complaint page sets out "
                "the order. First: &ldquo;Contact the insurance company or agent "
                "and bring the problem to their attention. Document your phone "
                "calls by noting the name of the person you speak to, the date of "
                "the call and a brief summary of the conversation. Keep copies of "
                "all written communications.&rdquo;</p>",
                "<p>If that does not resolve it, the Department handles complaints "
                "that &ldquo;may include coverage issues, claim disputes, premiums, "
                "policy cancellations, refunds, and sales "
                "misrepresentations.&rdquo; Its Consumer Assistance line is "
                "<strong>(866) 445-5364</strong>, but complaints must be made in "
                "writing: online through the "
                "<a href=\"https://idoihelpcenter.illinois.gov/s/\">IDOI Help "
                "Center</a>, by email to DOI.complaints@illinois.gov, or by post. "
                "The page states that &ldquo;Illinois law allows 21 days for an "
                "insurer or agent to respond to a complaint.&rdquo;</p>",
                "<p>Know its limits before you write. Among the things the page "
                "says the Department cannot do are &ldquo;Make medical "
                "judgments&rdquo; and &ldquo;Act as your lawyer or give you legal "
                "advice.&rdquo; A dispute about whether the insurer followed the "
                "policy is its business; a dispute about how impaired your parent "
                "is may need the doctor&rsquo;s evidence, or a lawyer.</p>",
            ]),
            ("Where the policy fits in the bigger picture", [
                "<p>A policy pays only up to the limits written in it, so it may "
                "not settle the whole question of paying for care. If savings "
                "may run out later, Medicaid does not simply pick up an assisted "
                "living bill. One Illinois Medicaid route into this kind of "
                "residence is the Supportive Living Program, which HFS describes "
                "as &ldquo;an alternative to nursing home care for low-income older "
                "persons and persons with physical disabilities under "
                "Medicaid&rdquo;; there, HFS says, &ldquo;The resident is "
                "responsible for paying the cost of room and board at the "
                "facility.&rdquo; "
                "<a href=\"/guides/illinois-supportive-living-program/\">The "
                "Supportive Living Program guide</a> explains it, and "
                "<a href=\"/guides/illinois-medicaid-long-term-care/\">the Illinois "
                "Medicaid long-term care guide</a> covers nursing home care and "
                "care at home. The Illinois Department on Aging&rsquo;s SHIP page on "
                "long-term care insurance lists its Senior HelpLine, "
                "<strong>1-800-252-8966</strong>.</p>",
                "<p>If you are still working out whether assisted living is the "
                "right level of care, the <a href=\"/\">free six-question "
                "assessment</a> on the home page is a private place to start.</p>",
            ]),
        ],
    },
    {
        "slug": "illinois-memory-care-assisted-living",
        "bridge": ("Knowing what Illinois requires of a memory care setting is a "
                   "different question from knowing whether your parent needs one yet."),
        "reviewed": "2026-11-26",
        "title": "Memory Care in Illinois Assisted Living: What the State Requires",
        "h1": "What does Illinois require of memory care in an assisted living community?",
        "desc": ("Who licenses memory care in Illinois assisted living, the dementia "
                 "training staff must take, the program disclosure, and what to ask "
                 "on a tour."),
        "intent": "choosing a community",
        "answer": ("<strong>Memory care in an Illinois assisted living community is "
                   "licensed and surveyed by the state, not by Medicare.</strong> The "
                   "Illinois Department of Public Health (IDPH) calls assisted living "
                   "&ldquo;a state licensure program with no federal oversight&rdquo;. "
                   "Its 2026&ndash;2029 Alzheimer&rsquo;s plan says staff serving people "
                   "with dementia in an assisted living facility providing "
                   "Alzheimer&rsquo;s or dementia services must take "
                   "&ldquo;six hours of initial dementia training and three hours of "
                   "annual dementia training thereafter&rdquo;, and that settings "
                   "offering specialised dementia care must disclose information "
                   "about their program to the agency that licenses them. Those are "
                   "the facts you can check before a tour."),
        "sources": srcs("idph_alz_plan", "idph_al_div"),
        "body": [
            ("Who licenses memory care in Illinois assisted living", [
                "<p>IDPH&rsquo;s Division of Assisted Living is "
                "&ldquo;responsible for all state licensure and survey processes for "
                "Assisted Living and Shared Housing establishments.&rdquo; Every "
                "establishment must send IDPH an annual renewal application with its "
                "licence fee.</p>",
                "<p>IDPH&rsquo;s Alzheimer&rsquo;s plan describes the same division as "
                "conducting annual and complaint surveys, incident report "
                "investigations and follow-up surveys, and adds why there is no "
                "federal oversight: &ldquo;This is a state licensure program with no federal "
                "oversight, as the residents in both assisted living and memory care "
                "areas are private pay through an establishment contract.&rdquo;</p>",
                "<p>The plan is also plain about the rules themselves: &ldquo;There are "
                "basic dementia provisions in the regulations for ALFs&rdquo;. The "
                "more detailed Special Care Unit regulations it names apply to "
                "skilled nursing and intermediate care facilities, not to assisted "
                "living. This guide does not summarise the assisted living dementia "
                "provisions themselves, because their text is published outside the "
                "state agency pages this library cites; IDPH&rsquo;s Assisted Living "
                "page links to it under Laws &amp; Rules.</p>",
            ]),
            ("The training staff must have", [
                "<p>According to IDPH&rsquo;s plan, staff serving people with "
                "Alzheimer&rsquo;s disease or a related dementia in a skilled nursing "
                "facility, assisted living facility, home health provider or hospice "
                "program that provides Alzheimer&rsquo;s or dementia services are required "
                "to take &ldquo;six hours of initial dementia training and three hours "
                "of annual dementia training thereafter.&rdquo;</p>",
                "<p>The person in charge of the dementia program has a higher bar: "
                "&ldquo;Alzheimer&rsquo;s services supervisors in skilled nursing "
                "facilities and assisted living facilities are required to take 12 "
                "hours of annual dementia training&rdquo;. The plan adds that the "
                "training topics are prescribed in statute and associated rules.</p>",
            ]),
            ("The program disclosure", [
                "<p>IDPH&rsquo;s plan states that Illinois has an Alzheimer&rsquo;s "
                "Disease and Related Dementias Special Care Disclosure Act that "
                "&ldquo;requires licensed residential care settings that provide "
                "specialized care to individuals with dementia to disclose information "
                "about their program to the state agency responsible for licensing of "
                "that setting&rdquo;. A licensed community that provides specialised "
                "dementia care is, in other words, required to have disclosed "
                "information about its program to the state.</p>",
            ]),
            ("Check the licence and the record before you visit", [
                "<p>IDPH&rsquo;s Assisted Living page links to its list of licensed "
                "Assisted Living and Shared Housing establishments "
                "(<a href=\"https://llcs.dph.illinois.gov/s/?language=en_US\">IDPH "
                "licensing search</a>). For how to read what the state has found at a "
                "community, see "
                '<a href="/guides/check-illinois-inspection-records/">How to check an '
                "Illinois care community&rsquo;s inspection record</a>, and if "
                "something goes wrong after a move, "
                '<a href="/guides/illinois-care-facility-complaint/">How to report a '
                "problem at an Illinois care facility</a>.</p>",
            ]),
            ("Questions to ask on a memory care tour", [
                "<p>Each of these follows from a rule above, so a community should be "
                "able to answer it plainly:</p>",
                "<ul class=\"res__list\">"
                "<li>Is this memory care area part of a licence from IDPH&rsquo;s "
                "Division of Assisted Living, and under what name is it listed?</li>"
                "<li>May we see the description of your dementia program that you "
                "disclosed to the state?</li>"
                "<li>How many hours of dementia training have the staff who would care "
                "for my parent completed, and when was their last annual "
                "training?</li>"
                "<li>Who is your Alzheimer&rsquo;s services supervisor, and how is "
                "their annual training kept up to date?</li>"
                "<li>What does the establishment contract say my parent will pay, and "
                "what changes the price?</li>"
                "</ul>",
            ]),
            ("If private pay is not possible, and when to plan", [
                "<p>Because assisted living memory care is private pay through an "
                "establishment contract, one option for a family that cannot pay "
                "privately is Illinois&rsquo; Supportive Living Program, which IDPH&rsquo;s "
                "plan describes as an alternative to nursing home care for low-income "
                "older people, paid through a Medicaid waiver obtained by the "
                "Department of Healthcare and Family Services, with the resident still "
                "paying room and board. IDPH&rsquo;s plan "
                "says &ldquo;There are currently 20 SLP dementia care settings with "
                "approximately 520 apartments.&rdquo; See "
                '<a href="/guides/illinois-supportive-living-program/">Illinois '
                "Supportive Living Program, explained</a> for how it works.</p>",
                "<p>The same plan is candid that supply is short: &ldquo;the "
                "availability of even costly assisted living facilities (ALFs) with "
                "dementia care does not meet the demand.&rdquo; If memory care is "
                "likely, it is worth visiting communities early.</p>",
            ]),
            ("Where this fits with the rest of this site", [
                "<p>For how memory care differs from assisted living and skilled "
                "nursing, see "
                '<a href="/guides/levels-of-senior-care-explained/">Assisted living, '
                "memory care, skilled nursing and rehabilitation &mdash; what is the "
                "difference?</a>. If you are still working out which level of care "
                'your parent actually needs, the free <a href="/">six-question '
                "assessment</a> on this site walks through that question and shows "
                "its reasoning. It asks for no name, no email and no phone number, "
                "and your answers never leave your device.</p>",
            ]),
        ],
    },
    {
        "slug": "hospital-discharge-not-safe-to-go-home",
        "bridge": ("Getting through the discharge itself is a different question "
                   "from knowing which level of care your parent needs once "
                   "they leave the hospital."),
        "reviewed": "2026-11-26",
        "title": "Hospital Discharge When Your Parent Can't Safely Go Home",
        "h1": "The hospital says my parent is ready to leave, but they can't safely go home. What now?",
        "desc": ("What Medicare's own discharge materials tell a family to do when "
                 "home is not safe: the planning team, rehab or a nursing home, "
                 "and a fast appeal."),
        "intent": "decision at hospital discharge",
        "answer": ("<strong>Say so to the hospital staff before the discharge "
                   "date, not on the day.</strong> Medicare&rsquo;s discharge "
                   "planning checklist says the doctor and staff &ldquo;will work "
                   "with you to plan for your discharge&rdquo; and that a family "
                   "caregiver is one of the &ldquo;important members of the "
                   "planning team.&rdquo; It tells a caregiver to make sure they can "
                   "give the help needed and to talk to the staff about getting "
                   "help before discharge. If the next step is a nursing home, "
                   "Medicare&rsquo;s nursing home guide says the hospital&rsquo;s "
                   "staff should be able to help find one and help with the "
                   "transfer. If your parent has Medicare and you think the "
                   "discharge is too soon, Medicare.gov describes a fast appeal "
                   "that must be requested no later than the scheduled discharge "
                   "day."),
        "sources": srcs("medicare_discharge_checklist", "medicare_nh_choosing",
                        "msnf", "medicare_fast_appeals"),
        "body": [
            ("You are part of the discharge planning team", [
                "<p>Medicare&rsquo;s publication <em>Your discharge planning "
                "checklist</em> is written for patients and their caregivers "
                "preparing to leave a hospital, nursing home or other care "
                "setting. It says: &ldquo;You and your caregiver (a family member "
                "or friend who may be helping you) are important members of the "
                "planning team.&rdquo; Its first instruction is to use the "
                "checklist &ldquo;throughout your stay&rdquo;, and it names the "
                "people to talk to: the doctor and staff &ldquo;like a discharge "
                "planner, social worker, ombudsman, or nurse&rdquo;.</p>",
                "<p>The checklist also says: &ldquo;Ask where you&rsquo;ll get "
                "care after you&rsquo;re discharged. Do you have options (like "
                "home health care)? Tell the staff what you prefer.&rdquo; If "
                "home is not a safe option, that is the moment to say so, while "
                "there is still time to arrange something else.</p>",
            ]),
            ("Tell the staff plainly what help is, and is not, there at home", [
                "<p>The checklist asks the patient to circle the activities they "
                "need help with and to &ldquo;discuss your concerns with the "
                "staff&rdquo;: bathing, dressing, using the bathroom and climbing "
                "stairs; cooking, food shopping, house cleaning and paying bills; "
                "driving to doctors&rsquo; appointments and picking up "
                "prescriptions.</p>",
                "<p>It has a separate section for the family caregiver. It says: "
                "&ldquo;Make sure you can give the person you&rsquo;re caring for "
                "the help they need.&rdquo; It asks what tasks the caregiver "
                "needs help with and whether they need education or training, "
                "and it says to &ldquo;Talk to the staff about getting the help "
                "you need before discharge.&rdquo; If you cannot provide the care "
                "your parent will need at home, this checklist is the "
                "hospital&rsquo;s own Medicare material telling you to raise it "
                "with the staff before the discharge happens.</p>",
                "<p>For questions about money, the checklist says to talk to a "
                "social worker or your health plan &ldquo;if you have questions "
                "about what your insurance will cover and how much you&rsquo;ll "
                "have to pay.&rdquo;</p>",
            ]),
            ("If the next step is a nursing home or rehab", [
                "<p>Medicare&rsquo;s <em>Your Guide to Choosing a Nursing Home or "
                "Other Long-Term Services &amp; Supports</em> (revised October "
                "2019) says: &ldquo;If you&rsquo;re in the hospital, ask your "
                "social worker about discharge planning as early in your hospital "
                "stay as possible. The hospital&rsquo;s staff should be able to "
                "help you find a nursing home that meets your needs and help with "
                "your transfer when you&rsquo;re ready to be discharged.&rdquo;</p>",
                "<p>The same guide covers the case where the only nursing home "
                "with a bed is one you do not want. The hospital discharge planner "
                "or doctor &ldquo;may be able to help you find a more suitable "
                "nursing home or arrange for other care, like short-term home "
                "health care, until a bed is available at another nursing home "
                "you choose.&rdquo; It adds a warning: &ldquo;But you may be "
                "responsible for paying the bill for any additional days you stay "
                "in the hospital.&rdquo;</p>",
                "<p>To compare the quality of nursing homes, home health agencies "
                "and inpatient rehabilitation facilities near you, the checklist "
                "points to Medicare&rsquo;s Care Compare tool at "
                "Medicare.gov/care-compare, or 1-800-MEDICARE "
                "(1-800-633-4227; TTY 1-877-486-2048).</p>",
            ]),
            ("Whether Original Medicare will pay for a rehab stay in a nursing home", [
                "<p>Medicare.gov&rsquo;s skilled nursing facility page says "
                "Medicare will only cover care in a skilled nursing facility "
                "(SNF) if your parent first has a qualifying inpatient hospital "
                "stay: a medically necessary &ldquo;inpatient hospital stay of at "
                "least 3 days in a row (starting the day you were admitted as an "
                "inpatient, but not including the day you leave the "
                "hospital).&rdquo; Time under observation or in the emergency "
                "room before admission does not count, &ldquo;even if "
                "you&rsquo;re there overnight.&rdquo; The page also requires that "
                "a doctor or other health care provider has decided your parent "
                "needs daily skilled care, given in a Medicare-certified SNF, "
                "entered within a short time (generally 30 days) of leaving the "
                "hospital. If the hospital has its own SNF, the page says: &ldquo;If "
                "the hospital you&rsquo;re in has its own SNF, and a bed is "
                "available, you may choose to stay there.&rdquo;</p>",
                "<p>What Original Medicare&rsquo;s Part A charges for SNF care in "
                "each benefit period in 2026, on the same page: days 1 to 20, &ldquo;You pay $0 each day "
                "after you pay the $1,736&rdquo; deductible (none if it was already "
                "paid for a hospital stay in the same benefit period); days 21 to "
                "100, &ldquo;You pay $217 each day ($222 in 2027).&rdquo; From day "
                "101, &ldquo;You pay all costs.&rdquo; The page adds: &ldquo;Part A "
                "limits SNF coverage to 100 days in each benefit period.&rdquo; "
                "So a parent who already used SNF days in the same benefit period "
                "does not start again at day 1. In a Medicare Advantage "
                "plan, the page says, &ldquo;you may be charged copayments during "
                "the first 20 days.&rdquo;</p>",
                "<p>The page names exceptions to the 3-day rule: a doctor in an "
                "Accountable Care Organization approved for a &ldquo;Skilled "
                "Nursing Facility 3-Day Rule Waiver&rdquo;, and Medicare Advantage "
                "plans, which &ldquo;may also waive the 3-day minimum inpatient "
                "hospital stay.&rdquo; Its advice is: &ldquo;Always ask your doctor "
                "or hospital staff if Medicare will cover your SNF stay.&rdquo; "
                "Without a qualifying stay, it says to ask about care in other "
                "settings, like home health care, or whether other programs, like "
                "Medicaid or Veterans&rsquo; benefits, can cover SNF care. For "
                "what Medicare pays and never pays in a nursing home or assisted "
                "living, see "
                '<a href="/guides/does-medicare-pay-for-senior-care/">Does '
                "Medicare pay for assisted living or nursing home care?</a>; for "
                "care at home, see "
                '<a href="/guides/medicare-home-health-care/">Medicare home health '
                "care</a>. Before a move into an Illinois nursing home, the state "
                "has its own screening step, explained in "
                '<a href="/guides/illinois-nursing-home-preadmission-screening/">'
                "Illinois nursing home pre-admission screening</a>.</p>",
            ]),
            ("If you think the discharge is too soon", [
                "<p>Medicare.gov&rsquo;s fast appeals page says that in a "
                "hospital, within 2 days of admission and before discharge, your "
                "parent should get a notice called the Important Message from "
                "Medicare, and &ldquo;If you don&rsquo;t get this notice, ask for "
                "it.&rdquo; To appeal, follow its directions &ldquo;no later than "
                "the day you&rsquo;re scheduled to be discharged from the "
                "hospital.&rdquo; The appeal goes to an independent reviewer, the "
                "Beneficiary and Family Centered Care Quality Improvement "
                "Organization (BFCC-QIO); the checklist says 1-800-MEDICARE can "
                "give you its phone number.</p>",
                "<p>In a hospital, the page says that if your parent asks in time "
                "&ldquo;you can stay in the hospital while you wait to get the "
                "BFCC-QIO&rsquo;s decision. You won&rsquo;t have to pay for your "
                "stay (except for applicable coinsurance or deductibles).&rdquo; "
                "The page does not limit this to Original Medicare: it says that "
                "in a hospital, &ldquo;If you have a Medicare health plan, the "
                "BFCC-QIO will notify your plan and the hospital.&rdquo; If the "
                "reviewer decides the stay should end and you met the deadline, "
                "your parent won&rsquo;t pay hospital charges, other than "
                "coinsurance or deductibles, &ldquo;incurred through noon of the "
                "day after the BFCC-QIO gives you its decision.&rdquo; Miss the "
                "deadline and &ldquo;you can still ask the BFCC-QIO to review your "
                "case, but different rules and time frames apply&rdquo;, and your "
                "parent &ldquo;might be responsible for the cost of the hospital "
                "stay past the original day the hospital tries to discharge "
                "you.&rdquo;</p>",
                "<p>For a parent in a Medicare Advantage plan, the page says that "
                "if the BFCC-QIO decides the stay should continue, Medicare keeps "
                "covering it if the plan had previously authorised the inpatient "
                "admission, or if the admission was for emergency care or for "
                "other care needed right away; "
                "otherwise, it says, you may need to appeal the plan&rsquo;s "
                "denial of coverage. Right after the rule "
                "for a missed deadline, it adds: &ldquo;If you&rsquo;re in a "
                "Medicare Advantage Plan, you can ask your plan for an appeal, but "
                "different rules apply.&rdquo; For free help with an appeal, Medicare&rsquo;s checklist lists "
                "the State Health Insurance Assistance Programs, which "
                "&ldquo;help with claims, billing, and appeals&rdquo;; "
                "1-800-MEDICARE can give you the local number.</p>",
                "<p>An appeal decides whether Medicare keeps covering "
                "the hospital stay; it does not by itself arrange the care your "
                "parent needs afterwards, so keep the planning conversation going "
                "with the staff at the same time.</p>",
            ]),
            ("Where this fits with the rest of this site", [
                "<p>A discharge that home cannot absorb is often the point where "
                "a family has to decide on a different level of care for good, "
                "not just for a few weeks. For the differences between those "
                "levels, see "
                '<a href="/guides/levels-of-senior-care-explained/">Assisted '
                "living, memory care, skilled nursing and rehabilitation &mdash; "
                "what is the difference?</a>. If you are still working out which "
                'level your parent needs, the free <a href="/">six-question '
                "assessment</a> on this site walks through that question. It asks "
                "for no name, no email and no phone number, and your answers never "
                "leave your device.</p>",
            ]),
        ],
    },
    {
        "slug": "noticed-changes-in-parent-holiday-visit",
        "bridge": ("Seeing that something has changed is a different question from "
                   "knowing what kind of help your parent now needs."),
        "reviewed": "2026-11-27",
        "title": "Noticed Changes in a Parent Over the Holidays? Next Steps",
        "h1": "You noticed changes in your parent during a holiday visit. What should you do next?",
        "desc": ("A first-week plan for Illinois families: what to write down, the "
                 "Medicare Wellness visit and its memory check, and who to call "
                 "first."),
        "intent": "first steps after noticing a decline",
        "answer": ("<strong>Write down what you saw, book an appointment with your "
                   "parent&rsquo;s doctor about it, and, if your parent lives in "
                   "Illinois, make one call to the Illinois Department on "
                   "Aging&rsquo;s Senior HelpLine.</strong> "
                   "Medicare Part B covers a yearly &ldquo;Wellness&rdquo; visit in "
                   "which the provider will &ldquo;Perform a cognitive assessment to "
                   "look for signs of dementia, including Alzheimer&rsquo;s "
                   "disease.&rdquo; The Illinois Department on Aging&rsquo;s Senior "
                   "HelpLine, 1-800-252-8966, says its staff can &ldquo;evaluate your "
                   "needs and answer your questions&rdquo; and connect you with local "
                   "care coordination services. If you fear that your parent, aged 60 or "
                   "older and living in their own home in Illinois, is being abused, "
                   "neglected or exploited or is neglecting themselves, the statewide "
                   "24-hour Adult Protective Services Hotline is 1-866-800-1409; for a "
                   "parent in a nursing home, the guide to reporting elder abuse covers "
                   "the other hotline."),
        "sources": srcs("medicare_awv", "medicare_cog", "idoa_helpline",
                        "idoa_aaa", "idoa_aaa_list", "idoa_ccp", "idoa_inhome", "idoa_aps_program"),
        "body": [
            ("Start with what you saw, in writing", [
                "<p>If you do not see your parent every week, a holiday visit can "
                "show changes all at once. Before you call anyone, write down what you "
                "noticed and when: the things your parent found hard, what was "
                "different from your last visit, and anything that worried you about "
                "safety. Keep it factual and short. It gives the doctor and anyone "
                "else you speak to something concrete to work from, and it lets "
                "brothers and sisters who were not there see the same picture.</p>",
                "<p>Medicare.gov lists the kinds of change a provider looks for in a "
                "memory check: &ldquo;Signs of cognitive impairment include trouble "
                "remembering, learning new things, concentrating, managing finances, "
                "and making decisions about your everyday life.&rdquo; Those are "
                "useful headings for your notes. A list is not a diagnosis, and only "
                "a clinician can say what is behind a change.</p>",
            ]),
            ("Book the doctor: the yearly Wellness visit and its memory check", [
                "<p>Medicare Part B covers a yearly &ldquo;Wellness&rdquo; visit "
                "once every 12 months. Medicare.gov says of it: &ldquo;It isn&rsquo;t "
                "a routine physical exam.&rdquo; During the visit, the provider will "
                "&ldquo;Perform a cognitive assessment to look for signs of dementia, "
                "including Alzheimer&rsquo;s disease.&rdquo; The page adds that if "
                "the provider thinks there may be cognitive impairment, &ldquo;Medicare "
                "covers a separate visit to do a more thorough review of your "
                "cognitive function and check for conditions like dementia, "
                "depression, anxiety, or delirium.&rdquo;</p>",
                "<p>On cost, the Wellness visit page says: &ldquo;You pay nothing if "
                "your provider accepts assignment.&rdquo; It also says your parent "
                "may have to pay coinsurance, and the Part B deductible may apply, "
                "if the provider performs additional tests or services during the "
                "same visit that this preventive benefit does not cover. For the "
                "separate cognitive assessment visit, Medicare.gov says: &ldquo;After "
                "you meet the Part B deductible, you pay 20% of the Medicare-approved "
                "amount.&rdquo; Both pages describe Medicare Part B; they do not say "
                "what a Medicare Advantage plan charges, so a parent in one of those "
                "plans should ask the plan.</p>",
                "<p>Medicare.gov also says that a first Wellness visit cannot take "
                "place within 12 months of Part B enrollment or the &ldquo;Welcome to "
                "Medicare&rdquo; preventive visit, and that &ldquo;If you have "
                "specific concerns about your health, you should schedule a separate "
                "appointment to discuss those&rdquo;. What you noticed is a specific "
                "concern, so ask for a separate appointment to discuss it rather than "
                "relying on the Wellness visit alone. For a parent with Medicare Part "
                "B, the cognitive assessment page says Part B covers a separate visit "
                "with a health care provider to fully review cognitive function and "
                "develop a care plan; after the Part B deductible, your parent pays "
                "20% of the Medicare-approved amount.</p>",
                "<p>Medicare.gov also says that if the provider performs tests or "
                "services Medicare doesn&rsquo;t cover during the Wellness visit, "
                "&ldquo;like a routine physical exam&rdquo;, your parent may have to "
                "pay the full amount. Some people living with dementia and their "
                "unpaid caregivers may be able to get extra support through a "
                "Medicare pilot program called the Guiding an Improved Dementia "
                "Experience (GUIDE) Model; Medicare.gov says to ask the provider "
                "whether they take part.</p>",
                "<p>You can go too. The cognitive assessment page says: &ldquo;When "
                "you have an assessment, you can bring someone with you (like a "
                "spouse, friend, or caregiver) to help listen to information and "
                "answer questions.&rdquo; Your written notes are most useful "
                "there.</p>",
            ]),
            ("Make one call: the Senior HelpLine", [
                "<p>The HelpLine and the other programs below are Illinois programs for "
                "people who live in Illinois. For a parent in another state, the "
                "HelpLine page says: &ldquo;To get information about services in "
                "another state, please visit the Eldercare Locator for helpful "
                "resources and contacts.&rdquo;</p>",
                "<p>The Illinois Department on Aging runs a Senior HelpLine at "
                "1-800-252-8966, Monday through Friday, from 8:30 a.m. to 5:00 p.m.; "
                "people who are deaf or have speech impairments can dial 711 "
                "(Illinois Relay). The Department says: &ldquo;We can help you locate "
                "services in your community, evaluate your needs and answer your "
                "questions, connect you with local care coordination services, and "
                "provide helpful information, assistance, and literature.&rdquo; Its "
                "staff write referrals for care coordination services, the Long-Term "
                "Care Ombudsman program, legal services, transportation, employment "
                "and nutrition services, and they also handle abuse intake.</p>",
                "<p>The HelpLine page lists what it is helpful to have when you call: "
                "your parent&rsquo;s name, age and address, the services they already "
                "receive, and daytime telephone numbers.</p>",
                "<p>Illinois is divided into 13 areas, each served by an Area Agency "
                "on Aging. For suburban Cook County, the Department&rsquo;s list names "
                "AgeOptions, Inc., at 1-800-699-9043 (for the suburban Cook County "
                "area only) or 708-383-0258; for a parent in the City of Chicago, it names "
                "the Chicago Department of Family and Support Services, 312-746-5682. "
                "The Department notes that Area Agencies "
                "&ldquo;are not, as a rule, direct service providers&rdquo;: they "
                "contract with local agencies that serve older people in their own "
                "communities.</p>",
            ]),
            ("If your parent wants to stay at home", [
                "<p>The Department on Aging&rsquo;s Community Care Program "
                "&ldquo;helps older adults who might otherwise need nursing home care "
                "to remain in their homes by providing in-home and community-based "
                "services.&rdquo; Its services include in-home help with household "
                "and personal care tasks, adult day services, emergency home response "
                "and automated medication dispensers. To be eligible, the Department "
                "lists: age 60 or older; U.S. citizen or eligible non-citizen; an "
                "Illinois resident; non-exempt assets of $17,500 or less (the home, "
                "car and personal furnishings are exempt); an assessed need for "
                "long-term care, measured by the Determination of Need assessment; "
                "and applying for and, if eligible, enrolling in Medicaid. The "
                "Department&rsquo;s in-home care page says people who meet the "
                "criteria and enroll &ldquo;receive services at no out-of-pocket "
                "cost.&rdquo; The program is arranged through local Care Coordination "
                "Units. See "
                '<a href="/guides/illinois-community-care-program/">the guide to the '
                "Community Care Program</a> for more.</p>",
                "<p>Families can also pay for help privately. The same page says the "
                "Illinois Department of Public Health licenses Home Services Agencies "
                "to employ home care aides for help with daily activities and "
                "personal care, and that &ldquo;Clients served by Home Services "
                "Agencies pay out-of-pocket for care.&rdquo;</p>",
                "<p>If a relative would rather give the care, the same page says the "
                "Community Care Program allows a family member, including a spouse, "
                "to be paid, once they meet its qualifications, pass a background "
                "check, complete 24 hours of pre-service training and are hired and "
                "supervised by an In-Home Services agency.</p>",
            ]),
            ("If you are worried about safety right now", [
                "<p>The Department on Aging&rsquo;s Adult Protective Services program "
                "investigates reports of &ldquo;abuse, neglect, exploitation, and "
                "self-neglect of adults age 60 or older, and adults age 18-59 with "
                "disabilities living in the community.&rdquo; To report, the "
                "statewide, 24-hour Adult Protective Services Hotline is "
                "1-866-800-1409, and the Department lists Illinois Relay at 711 for "
                "deaf and speech-impaired callers. "
                '<a href="/guides/illinois-elder-abuse-reporting/">The guide to '
                "reporting elder abuse in Illinois</a> explains what happens after a "
                "report.</p>",
            ]),
            ("Where this fits with the rest of this site", [
                "<p>Notes, a doctor&rsquo;s visit and one phone call are a first "
                "week, not a decision. If what you saw points towards more help than "
                "home can give, "
                '<a href="/guides/levels-of-senior-care-explained/">Assisted living, '
                "memory care, skilled nursing and rehabilitation &mdash; what is the "
                "difference?</a> sets out what each kind of care provides, and "
                '<a href="/guides/assisted-living-cost-illinois/">the Illinois '
                "assisted living cost guide</a> covers what it costs. The Wellness "
                "visit is also a moment to talk about advance directives, which "
                '<a href="/guides/illinois-advance-directive-power-of-attorney/">the '
                "guide to Illinois advance directives</a> explains. If you are still "
                'working out which level of care fits, the free <a href="/">six-question '
                "assessment</a> on this site walks through that question. It asks for "
                "no name, no email and no phone number, and your answers never leave "
                "your device.</p>",
            ]),
        ],
    },
    {
        "slug": "home-care-or-assisted-living-illinois",
        "bridge": ("Comparing what each option costs is a different question from "
                   "knowing how much help your parent needs, and when."),
        "reviewed": "2026-11-27",
        "title": "Home Care or Assisted Living in Illinois? Costs and Who Pays",
        "h1": "Home care or assisted living for a parent in Illinois: what each costs and what pays for it",
        "desc": ("Illinois medians for in-home care, adult day and assisted living, "
                 "what Medicare and Illinois programs pay for, and the questions "
                 "that decide it."),
        "intent": "comparing more help at home with a move to assisted living",
        "answer": ("<strong>It depends mostly on how many hours of help your parent "
                   "needs, and whether that includes nights.</strong> CareScout&rsquo;s "
                   "2025 Cost of Care Survey puts the Illinois median for a non-medical "
                   "caregiver at home at $36 an hour; its monthly figure of $6,864 is "
                   "based on 44 hours of care a week. The same survey&rsquo;s Illinois "
                   "median for assisted living is $6,219 a month for a private, "
                   "one-bedroom unit. Original Medicare does not fill the gap at home: among "
                   "the things Medicare.gov says Medicare doesn&rsquo;t pay for are "
                   "&ldquo;24-hour-a-day care at your home&rdquo; and personal care when "
                   "that is the only care your parent needs, and its long-term care page "
                   "says Medicare doesn&rsquo;t pay for long-term care; a parent in a "
                   "Medicare Advantage Plan or another Medicare health plan should check "
                   "with the plan about its home health benefits. For a parent aged 60 or "
                   "older who lives in Illinois, is a U.S. citizen or an eligible "
                   "non-citizen, has non-exempt assets of $17,500 or less, is assessed as at risk of "
                   "nursing facility placement and applies for Medicaid, Illinois&rsquo;s "
                   "Community Care Program can pay for help at home; for a parent aged 65 "
                   "or older who qualifies for Medicaid and would otherwise need nursing "
                   "facility care, the Supportive Living Program is the state&rsquo;s "
                   "assisted-living-style alternative to a nursing home."),
        "sources": srcs("carescout", "mhha", "medicare_ltc_cov", "idoa_ccp",
                        "idoa_inhome", "dph_home_services_faq", "hfs_slp", "hfs_slf"),
        "body": [
            ("What the Illinois figures say", [
                "<p>CareScout&rsquo;s Cost of Care Survey 2025 collected prices from "
                "July through November 2025 and publishes a median for each state and "
                "type of care. These are the Illinois figures, as the survey&rsquo;s "
                "own tables state them:</p>",
                "<ul>"
                "<li><strong>A non-medical caregiver at home (in-home care):</strong> "
                "$36 an hour. The survey&rsquo;s monthly figure, $6,864, is not a "
                "price anyone quoted; it is based on 44 hours of care a week for 52 "
                "weeks, divided by 12.</li>"
                "<li><strong>Adult day health care:</strong> $91 a day. The monthly "
                "figure, $1,977, is based on 5 days a week for 52 weeks.</li>"
                "<li><strong>Assisted living:</strong> $6,219 a month, the monthly "
                "rate as reported for a private, one-bedroom unit.</li>"
                "</ul>",
                "<p>Read the two monthly figures with their bases. The in-home figure "
                "buys 44 hours of a caregiver&rsquo;s time a week; the assisted living "
                "figure is the community&rsquo;s monthly rate. Neither tells you what "
                "your parent would pay, and both are statewide medians, not Evanston "
                "prices. The <a href=\"/guides/assisted-living-cost-illinois/\">guide "
                "to what assisted living costs in Illinois</a> explains what the "
                "assisted living median measures and the charges that appear after a "
                "move.</p>",
                "<p>When you put the options side by side, list the costs of keeping "
                "your parent&rsquo;s home running (housing, utilities, food) next to "
                "the in-home figure, because the survey&rsquo;s in-home rate is a "
                "price for a caregiver&rsquo;s hours. Then ask each assisted living "
                "community for its written fee schedule, so you can see what its "
                "monthly rate covers.</p>",
            ]),
            ("What Medicare pays for at home, and what it does not", [
                "<p>Medicare.gov says Original Medicare (Part A and Part B) covers "
                "certain home health services for a person who needs part-time or "
                "intermittent skilled services and is &ldquo;homebound&rdquo;. Covered "
                "services include part-time or intermittent skilled nursing care; "
                "physical therapy, occupational therapy and speech-language pathology "
                "services if your parent meets certain conditions; and part-time or "
                "intermittent home health aide care only if your parent is also "
                "getting skilled nursing care or therapy at the same time. In most "
                "cases, the page says, part-time or intermittent means skilled nursing "
                "and home health aide services &ldquo;up to 8 hours a day (combined), "
                "for a maximum of 28 hours a week.&rdquo; It adds that your parent may be "
                "able to get more frequent care for a short time (less than 8 hours a "
                "day and up to 35 hours a week) if the provider decides it is "
                "necessary. For covered home health services under Original Medicare, "
                "Medicare.gov says: &ldquo;You pay nothing for covered home health "
                "services.&rdquo; For a parent in a Medicare Advantage Plan or another "
                "Medicare health plan, the page says to check with the plan about its "
                "home health benefits. The page also notes that a home health agency "
                "in Illinois may be part of a Medicare demonstration in which the "
                "agency may ask Medicare for a pre-claim review of coverage, which helps "
                "the family and the agency know earlier whether Medicare is likely to "
                "cover the services.</p>",
                "<p>The same page lists what Original Medicare doesn&rsquo;t pay for, "
                "including &ldquo;24-hour-a-day care at your home&rdquo;, homemaker "
                "services unrelated to your parent&rsquo;s care plan, and &ldquo;Custodial "
                "or personal care that helps you with daily living activities (like "
                "bathing, dressing, or using the bathroom), when this is the only care "
                "you need&rdquo;.</p>",
                "<p>Medicare.gov&rsquo;s long-term care page is headed &ldquo;Medicare "
                "doesn&rsquo;t pay for long-term care&rdquo;, and says non-medical "
                "long-term care services can be had &ldquo;at home, in the community, "
                "in an assisted living facility, or in a nursing home.&rdquo; So the "
                "everyday help that makes up most of either option, at home or in "
                "assisted living, is not something Medicare pays for. The long-term "
                "care page says this of Medicare and most health insurance, including "
                "Medicare Supplement Insurance (Medigap). It adds that a person may be "
                "eligible for long-term care through Medicaid, if they meet their "
                "state&rsquo;s eligibility requirements, or can choose to buy private "
                "long-term care insurance. The <a "
                "href=\"/guides/medicare-home-health-care/\">guide to Medicare home "
                "health care</a> covers who qualifies and how it starts.</p>",
                "<p>The home health page also says: &ldquo;You can still get home "
                "health care if you attend adult day care.&rdquo;</p>",
            ]),
            ("What Illinois pays for at home: the Community Care Program", [
                "<p>The Illinois Department on Aging&rsquo;s Community Care Program "
                "&ldquo;helps older adults who might otherwise need nursing home care "
                "to remain in their homes by providing in-home and community-based "
                "services.&rdquo; Its services include care coordination, adult day "
                "services, in-home services, emergency home response services and an "
                "automated medication dispenser service.</p>",
                "<p>The Department lists who is eligible: people 60 or older; U.S. "
                "citizens or eligible non-citizens within specific categories; "
                "residents of Illinois; with non-exempt assets of $17,500 or less (the "
                "home, car and personal furnishings are exempt); with an assessed need "
                "for long-term care, measured by the Determination of Need (DON) "
                "assessment; and who apply for and, if eligible, enroll in "
                "Medicaid.</p>",
                "<p>On cost, the Department&rsquo;s in-home care page says: "
                "&ldquo;Persons who meet CCP eligibility criteria and enroll in the "
                "program receive services at no out-of-pocket cost.&rdquo; It describes "
                "the program&rsquo;s In-Home Service as delivered by home care aides on "
                "a daily or weekly basis. Services are arranged through local Care "
                "Coordination Units, which the Department&rsquo;s <a "
                "href=\"https://ilaging.illinois.gov/programs/ccp/maps.html\">map "
                "tool</a> finds; the Department&rsquo;s Senior HelpLine is "
                "1-800-252-8966 (711 TRS). A family member (including a spouse) or a "
                "friend can be paid as the caregiver only after "
                "meeting the program&rsquo;s qualifications, passing a background "
                "check, completing 24 hours of pre-service training and being hired "
                "and supervised by an In-Home Services agency. The <a "
                "href=\"/guides/illinois-community-care-program/\">guide to the "
                "Community Care Program</a> covers the assessment and how to "
                "apply.</p>",
            ]),
            ("If your parent pays for help at home", [
                "<p>The Illinois Department of Public Health licenses Home Services "
                "Agencies to employ home care aides for help with daily living and "
                "personal care, and the Department on Aging says: &ldquo;Clients served "
                "by Home Services Agencies pay out-of-pocket for care.&rdquo; IDPH&rsquo;s "
                "licensing questions and answers list the payers a Home Services "
                "license can accept as private pay (out of pocket) or private "
                "insurance, with Medicaid clients served through the Community Care "
                "Program or the Department of Human Services&rsquo; Division of "
                "Rehabilitation Services.</p>",
                "<p>Skilled care at home is licensed separately: IDPH licenses Home "
                "Nursing Agencies and Home Health Agencies, and the Department on "
                "Aging says that, depending on the circumstance, Medicare, Medicaid "
                "and/or private insurance may cover those services. If you hire a "
                "caregiver directly instead of through an agency, the Department says "
                "to check the IDPH Health Care Worker Registry to ensure the caregiver "
                "is eligible to work in home care; the <a "
                "href=\"/guides/illinois-home-caregiver-background-check/\">guide to "
                "checking a home caregiver</a> explains how.</p>",
            ]),
            ("What Illinois pays for in an assisted living setting: Supportive Living", [
                "<p>Illinois runs the Supportive Living Program, which the Department "
                "of Healthcare and Family Services "
                "describes as an alternative to nursing home care for low-income older "
                "persons and persons with physical disabilities under Medicaid. Its "
                "resident fact sheet calls it an &ldquo;Affordable assisted living "
                "model&rdquo; for people 65 or older, or 22 to 64 with physical "
                "disabilities, who would otherwise need nursing facility care.</p>",
                "<p>Residents choose from a menu of services that includes personal "
                "care, medication oversight, meals and snacks, housekeeping, laundry, "
                "intermittent nursing services and 24-hour response and security. "
                "Medicaid pays for the services; HFS says: &ldquo;The resident is "
                "responsible for paying the cost of room and board at the "
                "facility.&rdquo; The fact sheet adds that most residents have both a "
                "room and board charge and a monthly share of the cost of care, worked "
                "out from their income. Certified Supportive Living providers are "
                "exempt from the Assisted Living and Shared Housing Act, the law under "
                "which IDPH licenses assisted living establishments. HFS also says each "
                "Medicaid-eligible resident must have income at least equal to the "
                "current SSI amount and must contribute all but $120 each month to the "
                "provider for lodging and meals, and that certified providers can "
                "charge a different rate to residents who pay privately. "
                "The <a href=\"/guides/illinois-supportive-living-program/\">guide to "
                "the Supportive Living Program</a> covers eligibility and the monthly "
                "charges.</p>",
            ]),
            ("The questions that decide it", [
                "<ul>"
                "<li><strong>How many hours of help a day, and on which days?</strong> "
                "The survey&rsquo;s in-home monthly figure assumes 44 hours a week. "
                "Count the hours your parent actually needs before comparing it with "
                "a monthly rate.</li>"
                "<li><strong>Does your parent need someone at night?</strong> "
                "Medicare.gov says Original Medicare doesn&rsquo;t pay for 24-hour-a-day "
                "care at home, so overnight help at home is paid for some other way; a "
                "parent in a Medicare Advantage Plan or another Medicare health plan "
                "should ask the plan what its home health benefits include.</li>"
                "<li><strong>Is the need mainly during the day?</strong> The Community "
                "Care Program describes adult day service as being for older adults "
                "who cannot be home alone during the day, and as respite for family "
                "caregivers, especially those who are employed outside the home.</li>"
                "<li><strong>Could your parent qualify for the Community Care Program "
                "or for Medicaid?</strong> The asset limit, the assessment and the "
                "Medicaid application above decide which public programs are open.</li>"
                "</ul>",
                "<p>If the real question is which level of care fits your parent, the "
                "free <a href=\"/\">six-question assessment</a> on this site walks "
                "through it. It asks for no name, no email and no phone number, and "
                "your answers never leave your device.</p>",
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
<a class="skip" href="#main">Skip to main content</a>

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

<main class="band" id="main">
  <div class="wrap {wrapcls}">
"""

FOOT = """  </div>
</main>

<footer class="foot">
  <div class="wrap">
    <p class="foot__name">Evanston Senior Care Guide</p>
    <p>Independently developed by an employee of Westminster Place. This is not
      an official Westminster Place website. I receive no referral fees from
      Westminster Place. Nothing is passed to them unless you tick the
      permission box on the tour form.</p>
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
        js(unescape(g["title"])), js(unescape(strip_tags(g["desc"]))), js(canon), reviewed_iso(g))


def js(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


def unescape(s):
    """JSON-LD is JSON, not HTML: an entity such as &mdash; inside it is six
    literal characters to a structured-data parser. Decode before quoting."""
    import html
    return html.unescape(s)


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


# --------------------------------------------------------------------------
# RELATED GUIDES — chosen by topic, not by position.
#
# Until 2026-10-31 related() took the first three guides in file order, so
# every page pointed at the same three (costs, Medicare, Supportive Living)
# and eleven guides were never named by any other. The map below is the
# reader's next question, in order: three guides, each an answer to what a
# person who has just read THIS page is likely to ask next.
#
# Rules, enforced by check_related() at build time and by check-guides.js on
# the output:
#   - exactly three per guide, no guide names itself, every slug exists;
#   - every guide is named by at least two others, so no page depends on the
#     library index alone to be found;
#   - the independent-living guide is named from the costs guide and the
#     levels guide, the two pages a planning-stage family reads first.
# The link text and the one-line reason are the library card's own title and
# blurb (CARDS below), so no new factual claim is introduced here.
# --------------------------------------------------------------------------
RELATED = {
    "assisted-living-cost-illinois": [
        "does-medicare-pay-for-senior-care",
        "independent-living-evanston",
        "long-term-care-insurance-assisted-living-illinois"],
    "does-medicare-pay-for-senior-care": [
        "medicare-home-health-care",
        "medicare-durable-medical-equipment-coverage",
        "medicare-fast-appeal-hospital-rehab-discharge"],
    "illinois-supportive-living-program": [
        "illinois-pace-program",
        "long-term-care-insurance-assisted-living-illinois",
        "illinois-medicaid-look-back-period"],
    "check-illinois-inspection-records": [
        "illinois-care-facility-complaint",
        "illinois-assisted-living-involuntary-move-out",
        "illinois-memory-care-assisted-living"],
    "levels-of-senior-care-explained": [
        "independent-living-evanston",
        "illinois-memory-care-assisted-living",
        "illinois-parent-refuses-to-move-guardianship"],
    "illinois-community-care-program": [
        "illinois-money-management-program",
        "va-veteran-directed-care-program",
        "illinois-nursing-home-preadmission-screening"],
    "illinois-medicaid-long-term-care": [
        "illinois-medicaid-estate-recovery",
        "illinois-nursing-home-responsible-party",
        "illinois-medicaid-pending-nursing-home"],
    "illinois-care-facility-complaint": [
        "check-illinois-inspection-records",
        "illinois-elder-abuse-reporting",
        "illinois-nursing-home-resident-rights"],
    "illinois-medicaid-estate-recovery": [
        "illinois-medicaid-long-term-care",
        "illinois-medicaid-look-back-period",
        "illinois-supportive-living-program"],
    "medicare-hospice-benefit-explained": [
        "illinois-advance-directive-power-of-attorney",
        "illinois-family-caregiver-support-program",
        "illinois-senior-health-insurance-program"],
    "independent-living-evanston": [
        "levels-of-senior-care-explained",
        "assisted-living-cost-illinois",
        "check-illinois-inspection-records"],
    "va-aid-and-attendance-benefit": [
        "va-veteran-directed-care-program",
        "assisted-living-cost-illinois",
        "va-nursing-home-and-respite-care"],
    "va-veteran-directed-care-program": [
        "va-home-based-primary-care-and-aide",
        "va-nursing-home-and-respite-care",
        "va-caregiver-support-program"],
    "illinois-family-caregiver-support-program": [
        "illinois-community-care-program",
        "illinois-home-care-ombudsman-program",
        "illinois-home-caregiver-background-check"],
    "illinois-senior-health-insurance-program": [
        "illinois-fide-snp-explained",
        "medicare-hospice-benefit-explained",
        "illinois-medicare-savings-program"],
    "illinois-nursing-home-resident-rights": [
        "illinois-care-facility-complaint",
        "illinois-assisted-living-involuntary-move-out",
        "illinois-advance-directive-power-of-attorney"],
    "illinois-nursing-home-preadmission-screening": [
        "hospital-discharge-not-safe-to-go-home",
        "illinois-pace-program",
        "illinois-community-care-program"],
    "illinois-medicaid-look-back-period": [
        "illinois-medicaid-long-term-care",
        "illinois-medicaid-estate-recovery",
        "illinois-supportive-living-program"],
    "illinois-home-care-ombudsman-program": [
        "illinois-elder-abuse-reporting",
        "illinois-care-facility-complaint",
        "medicare-home-health-care"],
    "illinois-advance-directive-power-of-attorney": [
        "illinois-money-management-program",
        "medicare-hospice-benefit-explained",
        "illinois-nursing-home-responsible-party"],
    "illinois-medicare-savings-program": [
        "illinois-senior-health-insurance-program",
        "illinois-fide-snp-explained",
        "medicare-extra-help-prescription-drug-costs"],
    "illinois-pace-program": [
        "illinois-community-care-program",
        "illinois-supportive-living-program",
        "illinois-home-delivered-meals"],
    "medicare-home-health-care": [
        "medicare-fast-appeal-hospital-rehab-discharge",
        "medicare-durable-medical-equipment-coverage",
        "illinois-home-caregiver-background-check"],
    "medicare-extra-help-prescription-drug-costs": [
        "illinois-medicare-savings-program",
        "illinois-senior-health-insurance-program",
        "illinois-benefit-access-program"],
    "illinois-home-delivered-meals": [
        "illinois-benefit-access-program",
        "illinois-family-caregiver-support-program",
        "illinois-home-care-ombudsman-program"],
    "illinois-elder-abuse-reporting": [
        "illinois-parent-refuses-to-move-guardianship",
        "illinois-home-care-ombudsman-program",
        "illinois-family-caregiver-support-program"],
    "illinois-benefit-access-program": [
        "illinois-medicare-savings-program",
        "medicare-extra-help-prescription-drug-costs",
        "illinois-home-delivered-meals"],
    "medicare-durable-medical-equipment-coverage": [
        "does-medicare-pay-for-senior-care",
        "medicare-home-health-care",
        "levels-of-senior-care-explained"],
    "va-nursing-home-and-respite-care": [
        "va-aid-and-attendance-benefit",
        "va-caregiver-support-program",
        "check-illinois-inspection-records"],
    "illinois-home-caregiver-background-check": [
        "illinois-community-care-program",
        "illinois-home-care-ombudsman-program",
        "illinois-elder-abuse-reporting"],
    "va-caregiver-support-program": [
        "va-aid-and-attendance-benefit",
        "va-nursing-home-and-respite-care",
        "va-home-based-primary-care-and-aide"],
    "illinois-fide-snp-explained": [
        "illinois-medicare-savings-program",
        "illinois-senior-health-insurance-program",
        "illinois-medicaid-long-term-care"],
    "illinois-assisted-living-involuntary-move-out": [
        "illinois-nursing-home-resident-rights",
        "illinois-care-facility-complaint",
        "levels-of-senior-care-explained"],
    "illinois-nursing-home-responsible-party": [
        "illinois-nursing-home-resident-rights",
        "illinois-advance-directive-power-of-attorney",
        "illinois-medicaid-pending-nursing-home"],
    "illinois-medicaid-pending-nursing-home": [
        "illinois-medicaid-long-term-care",
        "illinois-medicaid-look-back-period",
        "illinois-nursing-home-preadmission-screening"],
    "illinois-money-management-program": [
        "illinois-advance-directive-power-of-attorney",
        "illinois-community-care-program",
        "illinois-elder-abuse-reporting"],
    "illinois-parent-refuses-to-move-guardianship": [
        "illinois-advance-directive-power-of-attorney",
        "noticed-changes-in-parent-holiday-visit",
        "illinois-money-management-program"],
    "medicare-fast-appeal-hospital-rehab-discharge": [
        "does-medicare-pay-for-senior-care",
        "medicare-home-health-care",
        "hospital-discharge-not-safe-to-go-home"],
    "va-home-based-primary-care-and-aide": [
        "va-aid-and-attendance-benefit",
        "va-caregiver-support-program",
        "va-veteran-directed-care-program"],
    "long-term-care-insurance-assisted-living-illinois": [
        "assisted-living-cost-illinois",
        "illinois-supportive-living-program",
        "home-care-or-assisted-living-illinois"],
    "illinois-memory-care-assisted-living": [
        "levels-of-senior-care-explained",
        "check-illinois-inspection-records",
        "noticed-changes-in-parent-holiday-visit"],
    "hospital-discharge-not-safe-to-go-home": [
        "does-medicare-pay-for-senior-care",
        "medicare-fast-appeal-hospital-rehab-discharge",
        "home-care-or-assisted-living-illinois"],
    "noticed-changes-in-parent-holiday-visit": [
        "levels-of-senior-care-explained",
        "illinois-community-care-program",
        "illinois-elder-abuse-reporting"],
    "home-care-or-assisted-living-illinois": [
        "assisted-living-cost-illinois",
        "illinois-community-care-program",
        "illinois-supportive-living-program"],
}

RELATED_MIN_INBOUND = 2
IL_SLUG = "independent-living-evanston"
IL_NAMED_FROM = ["assisted-living-cost-illinois", "levels-of-senior-care-explained"]


def check_related():
    """Stop the build on a map that would leave a guide unreachable."""
    slugs = [g["slug"] for g in GUIDES]
    problems = []
    for s in slugs:
        picks = RELATED.get(s)
        if picks is None:
            problems.append("%s: no RELATED entry" % s)
            continue
        if len(picks) != 3 or len(set(picks)) != 3:
            problems.append("%s: needs exactly three distinct related guides" % s)
        if s in picks:
            problems.append("%s: names itself" % s)
        for p in picks:
            if p not in slugs:
                problems.append("%s: unknown related slug %s" % (s, p))
    for extra in set(RELATED) - set(slugs):
        problems.append("RELATED names a guide that is not built: %s" % extra)
    inbound = {s: 0 for s in slugs}
    for s in slugs:
        for p in RELATED.get(s, []):
            if p in inbound:
                inbound[p] += 1
    for s, n in inbound.items():
        if n < RELATED_MIN_INBOUND:
            problems.append("%s is named by only %d other guide(s)" % (s, n))
    for s in IL_NAMED_FROM:
        if IL_SLUG not in RELATED.get(s, []):
            problems.append("%s does not name the independent-living guide" % s)
    if problems:
        raise SystemExit("build-guides.py: RELATED map rejected:\n  " + "\n  ".join(problems))


def related(g):
    items = "".join(
        '<li><a href="/guides/%s/">%s</a>'
        '<span class="related__why">%s</span></li>' % (s, CARDS[s][1], CARDS[s][2])
        for s in RELATED[g["slug"]])
    return ('<section class="res__block related">\n'
            '<h2 class="res__h">Related guides</h2>\n'
            '<ul class="res__list related__list">%s</ul>\n%s</section>' % (items, pay_nav_line(g)))


def sources_block(g):
    items = "".join(
        '<li><a href="%s" rel="noopener" target="_blank">%s</a></li>' % (url, name)
        for name, url in g["sources"])
    return ('<section class="res__block">\n'
            '<h2 class="res__h">Sources</h2>\n'
            '<ul class="res__list">%s</ul>\n'
            '<p class="visit__fine">Every figure on this page was read from the '
            'source listed above on %s%s. Figures change; the review date tells you '
            'how fresh this page is.</p>\n</section>'
            % (items, reviewed_human(g),
               # Optional (independent living, 2026-11-06): names any figures
               # that did NOT come from the listed sources. Without the key the
               # sentence renders exactly as before.
               (", except " + g["figures_except"]) if g.get("figures_except") else ""))


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
    # Optional, one guide only so far (independent living, 2026-11-06): a
    # plain line straight under the short answer. A guide without the key
    # renders exactly as before.
    if g.get("after_answer"):
        parts.append(g["after_answer"] + "\n")
    lead = DIAGRAMS.get((g["slug"], None))
    if lead:
        parts.append(lead + "\n")
    for i, (heading, paras) in enumerate(g["body"]):
        dia = DIAGRAMS.get((g["slug"], strip_tags(heading)))
        body = "\n".join(paras) + (("\n" + dia) if dia else "")
        # Optional (tour checklist, 2026-11-11): a block appended to the end
        # of one named section. A guide without "after_section" renders
        # exactly as before.
        extra = g.get("after_section", {}).get(strip_tags(heading))
        if extra:
            body += "\n" + extra
        # Optional (independent living, 2026-11-06): an id on one section so
        # an in-page link lands on its heading; .res__block[id] already has a
        # scroll margin for the sticky nav. A guide without "section_ids"
        # renders exactly as before.
        sid = g.get("section_ids", {}).get(strip_tags(heading))
        parts.append('<section class="res__block"%s>\n<h2 class="res__h">%s</h2>\n%s\n</section>\n'
                     % ((' id="%s"' % sid) if sid else "", heading, body))
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
        "What Medicare covers, what it never covers, and why “no longer "
        "improving” is not by itself a reason for coverage to end."),
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
    "illinois-nursing-home-resident-rights": (
        "Checking a community",
        "What rights does your parent have in a care facility?",
        "The Illinois Department on Aging's own brochure, read in full: "
        "money, privacy, discharge and grievance rights a facility "
        "cannot override."),
    "illinois-nursing-home-preadmission-screening": (
        "Paying with Medicaid",
        "Does my parent need to be screened before a nursing home?",
        "Illinois law requires a screening before any adult is admitted to "
        "a nursing facility, however they pay — what it checks, who "
        "performs it, and what happens if it is skipped."),
    "illinois-medicaid-look-back-period": (
        "Paying with Medicaid",
        "Will giving money away affect Medicaid eligibility?",
        "Illinois reviews the five years before a long-term-care application "
        "for gifts and underpriced transfers — what triggers a penalty, what "
        "does not, and when it actually starts, read off HFS's own brochure."),
    "illinois-home-care-ombudsman-program": (
        "Staying at home",
        "What to do when in-home care isn't working in Illinois",
        "The state's advocate for a denial letter, an unresponsive care "
        "coordinator or a grievance, for home care arranged through a "
        "Medicaid managed care plan or waiver."),
    "illinois-advance-directive-power-of-attorney": (
        "Legal and planning",
        "Does my parent need a power of attorney for health care?",
        "Illinois does not require one, but without it the state still "
        "names a decision-maker in a fixed order you do not get to "
        "choose — what each of Illinois's four advance directives does."),
    "illinois-medicare-savings-program": (
        "Paying with Medicaid",
        "Can Illinois help pay my parent's Medicare premium?",
        "QMB, SLMB and QI are three Medicaid-run tiers that pay part or "
        "all of a Medicare premium — what each covers, the state's dated "
        "2026 limits, and the older figures this guide would not use."),
    "illinois-pace-program": (
        "Staying at home",
        "Is PACE available for a parent in Evanston?",
        "A joint Medicare and Medicaid programme pays for full medical and "
        "personal care so an older adult can avoid a nursing home — but "
        "Illinois runs it in only five regions, and this guide checked "
        "whether Evanston is one of them."),
    "medicare-home-health-care": (
        "Medicare",
        "Does Medicare pay for a home health aide or nurse at home?",
        "Medicare pays $0 for a covered home health visit — but only "
        "while a doctor-ordered skilled need and homebound status both "
        "hold, and a home health aide alone is never covered."),
    "medicare-extra-help-prescription-drug-costs": (
        "Medicare",
        "Does your parent qualify for Extra Help with drug costs?",
        "A Medicare program that can bring a Part D premium and "
        "deductible to $0 and cap the copay for each drug — who "
        "qualifies automatically, the 2026 limits, and how to apply."),
    "illinois-home-delivered-meals": (
        "Staying at home",
        "Can my parent get home-delivered meals in Illinois?",
        "A state-funded nutrition programme delivers meals to adults "
        "60 and over at home — what it covers, and who to call."),
    "illinois-elder-abuse-reporting": (
        "Staying at home",
        "What to do about suspected elder abuse at home",
        "A statewide Adult Protective Services hotline covers abuse, "
        "neglect, exploitation and self-neglect of an older adult living "
        "at home — a different line from the one for a care facility."),
    "illinois-benefit-access-program": (
        "Costs",
        "Free transit and a cheaper license plate for seniors",
        "A state programme gives income-eligible seniors free public "
        "transit rides and a discounted vehicle registration — the "
        "income limits and how to apply, read off the Department on "
        "Aging's own page."),
    "medicare-durable-medical-equipment-coverage": (
        "Medicare",
        "Does Medicare pay for a wheelchair or hospital bed?",
        "Part B covers home medical equipment with a doctor's order and "
        "an enrolled supplier, and a power wheelchair needs a face-to-face "
        "exam and a written prescription first."),
    "va-nursing-home-and-respite-care": (
        "Veterans' benefits",
        'Can the VA provide nursing home care, or give a caregiver a break?',
        'VA nursing homes, respite stays and help at home that VA provides or pays for directly, not a pension cheque, and the room and board VA.gov says it does not pay.'),
    "illinois-home-caregiver-background-check": (
        'Staying at home',
        'Is it safe to hire a caregiver directly in Illinois?',
        'What a licensed agency checks for you, the state registry Illinois tells families to check themselves, and where to raise a problem.'),
    "va-caregiver-support-program": (
        "Veterans' benefits",
        'Can a family caregiver be paid by the VA?',
        "Who qualifies for VA's monthly caregiver stipend, how the stipend is set, and the VA caregiver support open to everyone else."),
    "illinois-fide-snp-explained": (
        'Medicare',
        'What replaced MMAI for parents with Medicare and Medicaid?',
        'Illinois ended MMAI on 31 December 2025. What a FIDE SNP is, who can join one, and when a dually eligible parent can switch plans.'),
    "illinois-assisted-living-involuntary-move-out": (
        "Checking a community",
        "Can an assisted living make your parent move out?",
        "IDPH's own form requires 30 days' written notice and a right to "
        "appeal before a stay can be ended — the process, read off the "
        "state's own paperwork."),
    "illinois-nursing-home-responsible-party": (
        "Legal and planning",
        "Should you sign as a nursing home's “responsible party”?",
        "Federal law bars a certified nursing home from making you "
        "personally pay your parent's bill — what “responsible "
        "party” language can and cannot legally ask of you."),
    "illinois-medicaid-pending-nursing-home": (
        "Paying with Medicaid",
        "Medicaid pending in an Illinois nursing home?",
        "How long the state has to decide, what Provisional Eligibility is, "
        "and what your parent may owe while you wait, read off HFS and the "
        "Auditor General."),
    "illinois-money-management-program": (
        "Legal and planning",
        "Who can help my parent pay bills in Illinois?",
        "A state-run volunteer can budget, pay bills and even act as "
        "Social Security representative payee — but only through two "
        "eligibility paths, and only where a Program Site actually "
        "reaches."),
    "illinois-parent-refuses-to-move-guardianship": (
        "Legal and planning",
        "Parent refuses to move? Illinois options and guardianship",
        "Illinois presumes an adult decides where they live. What the state "
        "says to try first, when guardianship applies and how the court "
        "process works, read off the Guardianship and Advocacy Commission."),
    "medicare-fast-appeal-hospital-rehab-discharge": (
        "Medicare",
        "Discharged too soon? How a Medicare fast appeal works",
        "The two notices, the deadlines and who pays while you wait when a "
        "hospital or rehab stay is ending, read off Medicare.gov."),
    "va-home-based-primary-care-and-aide": (
        "Veterans' benefits",
        "Can the VA send a doctor or an aide to your veteran's house?",
        "Two separate VA home programmes, in VA.gov's own words — a "
        "medical team, and a trained aide — and how each differs from "
        "Veteran Directed Care and the caregiver stipend."),
    "long-term-care-insurance-assisted-living-illinois": (
        "Costs",
        "Long-term care insurance and assisted living",
        "Benefit triggers, the elimination period, which facilities a policy "
        "covers and what to do if a claim stalls, read off the Illinois "
        "Department of Insurance."),
    "illinois-memory-care-assisted-living": (
        "Checking a community",
        "Memory care in Illinois assisted living",
        "Who licenses it, the dementia training staff must take, the program "
        "disclosure and what to ask on a tour, read off IDPH."),
    "hospital-discharge-not-safe-to-go-home": (
        "Medicare",
        "When your parent can't safely go home from hospital",
        "The discharge planning team, a nursing home or rehab bed, the 3-day "
        "rule and the fast appeal, read off Medicare's own materials."),
    "noticed-changes-in-parent-holiday-visit": (
        "Getting oriented",
        "Noticed changes in a parent over the holidays",
        "What to write down, the Medicare Wellness visit and its memory check, "
        "and who to call first in Illinois, read off Medicare.gov and IDoA."),
    "home-care-or-assisted-living-illinois": (
        "Costs",
        "Home care or assisted living in Illinois?",
        "Illinois medians for in-home care, adult day and assisted living, and "
        "what Medicare, the Community Care Program and Supportive Living pay for."),
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
            + '<p class="visit__fine">Last reviewed %s.</p>\n' % reviewed_human({"reviewed": newest_listed()})
            + FOOT.replace("</body>", '<script src="/guides.js"></script>\n</body>'))


def build_sitemap():
    """Generated from the GUIDES list — adding a guide updates the sitemap."""
    # lastmod is PER URL. Stamping every page with today's date because one
    # guide changed tells a crawler that six unchanged pages were rewritten -
    # untrue, and the fastest way to teach it to ignore the field entirely.
    # A guide's lastmod is its own review date.
    newest = newest_listed()
    urls = [(SITE + "/", "1.0", "monthly", newest),
            (SITE + "/guides/", "0.8", "monthly", newest)]
    urls += [(SITE + "/guides/%s/" % g["slug"], "0.7", "yearly", reviewed_iso(g))
             for g in GUIDES]
    urls.append((SITE + "/assisted-living-evanston/", "0.8", "monthly", "2026-11-21"))
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
                 "guides.js", "index.html", "paying-nav.js",
                 "assisted-living-evanston/index.html"]


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
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copyfile(name, dest)
            copied.append(name)
    return copied


def main():
    check_categories()
    check_related()
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
    print("  sitemap.xml regenerated with %d URLs" % (len(GUIDES) + 4))


if __name__ == "__main__":
    main()
