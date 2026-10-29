/* Workflow #5: optional Payment Options Navigator.
   Three answers stay in the browser. No income, diagnosis, name, eligibility
   decision, ranking of providers, or lead collection. A "yes" only changes
   the order of the same fixed funding explanations.

   It never reads or writes the assessment: not `answers`, not
   `resultLevelId`, not the scoring. A care level arrives only as the id on
   the result's entry link, and "Not sure" is always a complete answer.

   The order is explained, never asserted. Each care type carries one
   sentence saying why its routes sit in that order; a route moved up by a
   "yes" says so on the card, in terms of the visitor's own answer; and when
   no care type was chosen the five are presented in no particular order,
   with nothing marked as the place to start. */
(function (root) {
  "use strict";
  const CARE = Object.freeze({
    unsure: "Not sure yet",
    independent: "Independent Living",
    assisted: "Assisted Living",
    memory: "Memory Care",
    skilled: "Skilled Nursing / long-term nursing home",
    rehab: "Short-Term Rehabilitation"
  });
  /* Assisted living and memory care in Illinois are usually private-pay
     (the page's own cost section says so, citing HFS), so the quote comes
     first for them and Medicaid sits where its one route, the Supportive
     Living Program, belongs. Nursing-home care is where Medicaid does most
     of its paying. A short rehab stay is the one setting Medicare may cover. */
  const BASE_ORDER = Object.freeze({
    unsure:      ["medicaid", "medicare", "private", "va", "ltci"],
    independent: ["private", "ltci", "va", "medicaid", "medicare"],
    assisted:    ["private", "ltci", "medicaid", "va", "medicare"],
    memory:      ["private", "ltci", "medicaid", "va", "medicare"],
    skilled:     ["medicaid", "medicare", "private", "ltci", "va"],
    rehab:       ["medicare", "medicaid", "private", "ltci", "va"]
  });
  /* Why the routes sit in that order, in one hedged sentence per care type.
     Shown above the list. None of these decides anything. */
  const ORDER_WHY = Object.freeze({
    unsure: "No type of care was chosen, so nothing here is ranked: the two public programs first because they are the most often misunderstood, then private payment, then the two that depend on the person's own circumstances.",
    independent: "Independent living is housing rather than care, so it is almost always paid privately. A long-term-care policy or a VA pension supplement only comes into play when care needs exist, and neither Medicaid nor Medicare pays the rent.",
    assisted: "Assisted living in Illinois is usually private-pay, so the written quote comes first. A policy may help; Medicaid pays only through the certified Supportive Living Program; Medicare does not pay for it.",
    memory: "Memory care is usually private-pay, so the written quote comes first. A policy may help; Medicaid pays only in certified Supportive Living dementia-care settings; Medicare does not pay for ongoing care.",
    skilled: "Long-stay nursing-home care is the setting Illinois Medicaid most often pays for, under its clinical and financial rules, and Medicare pays only for a time-limited skilled stay. Those two come first, then the private rate.",
    rehab: "A short rehabilitation stay is the one setting Medicare may pay for, under its conditions, so it comes first. The rest is what families fall back on when the covered days end or the conditions are not met."
  });
  /* A field may be one value for every care type, or an object keyed by care
     type with "*" as the fallback. Links differ by care type so that someone
     exploring a nursing home is never sent to assisted-living prices. */
  const COST_SECTION = "/#cost";
  const ROUTES = Object.freeze({
    medicare: {
      title: "Medicare",
      link: { "*": "https://www.medicare.gov/coverage/long-term-care",
              skilled: "https://www.medicare.gov/coverage/skilled-nursing-facility-snf-care",
              rehab: "https://www.medicare.gov/coverage/skilled-nursing-facility-snf-care" },
      linkText: { "*": "Medicare: long-term care coverage",
                  skilled: "Medicare: skilled nursing facility care",
                  rehab: "Medicare: skilled nursing facility care" },
      guide: "/guides/does-medicare-pay-for-senior-care/",
      guideText: "What Medicare pays for, and what it never pays for",
      more: "/guides/illinois-senior-health-insurance-program/",
      moreText: "Free Medicare counselling in Illinois (SHIP)",
      summary: {
        unsure: "Check whether the need is short-term skilled nursing or rehabilitation. Medicare does not pay for most ongoing custodial long-term care.",
        independent: "Medicare does not pay the usual housing or lifestyle costs of independent living. Qualifying medical services are a separate question.",
        assisted: "Medicare does not pay for routine assisted living, including room and board or ongoing personal care. A separate qualifying skilled-care episode is different.",
        memory: "Medicare does not pay for ongoing custodial memory care or its room and board. Some separately qualifying medical care may be covered.",
        skilled: "Medicare may cover a time-limited skilled nursing facility stay if its conditions are met. It does not pay indefinitely for custodial nursing-home care.",
        rehab: "Medicare may cover a time-limited skilled nursing or rehabilitation stay when its conditions are met. Ask the plan and discharge team to confirm coverage."
      }
    },
    medicaid: {
      title: "Illinois Medicaid",
      link: { "*": "https://hfs.illinois.gov/medicalclients/ltc.html",
              assisted: "https://hfs.illinois.gov/medicalprograms/slf.html",
              memory: "https://hfs.illinois.gov/medicalprograms/slf.html" },
      linkText: { "*": "Illinois HFS: long-term care",
                  assisted: "Illinois HFS: Supportive Living Program",
                  memory: "Illinois HFS: Supportive Living Program" },
      guide: { "*": "/guides/illinois-medicaid-long-term-care/",
               assisted: "/guides/illinois-supportive-living-program/",
               memory: "/guides/illinois-supportive-living-program/",
               independent: "/guides/illinois-community-care-program/" },
      guideText: { "*": "How Illinois Medicaid pays for long-term care",
                   assisted: "The Supportive Living Program, explained",
                   memory: "The Supportive Living Program, explained",
                   independent: "Paid help at home: the Community Care Program" },
      more: { "*": "/guides/illinois-supportive-living-program/",
              assisted: "/guides/illinois-medicaid-long-term-care/",
              memory: "/guides/illinois-medicaid-long-term-care/",
              skilled: "/guides/illinois-medicaid-estate-recovery/",
              rehab: null },
      moreText: { "*": "The Supportive Living Program, explained",
                  assisted: "If needs grow: nursing-home Medicaid and spend-down",
                  memory: "If needs grow: nursing-home Medicaid and spend-down",
                  skilled: "Will Illinois take the house after Medicaid pays?",
                  rehab: null },
      summary: {
        unsure: "Eligibility and services depend on the actual setting. Illinois nursing-home Medicaid and the certified Supportive Living Program have different rules.",
        independent: "Medicaid does not ordinarily pay independent-living rent. Ask Illinois HFS about services in an eligible setting if care needs change.",
        assisted: "A certified Illinois Supportive Living Program may cover eligible care services; this is not the same as Medicaid paying a traditional assisted-living bill. Room and board remain a resident cost.",
        memory: "Some certified Illinois Supportive Living dementia-care settings may cover eligible care services. That does not mean ordinary private memory care is covered; room and board remain a resident cost.",
        skilled: "Illinois Medicaid may help pay eligible long-stay nursing-facility care, subject to clinical and financial requirements and facility participation.",
        rehab: "Check whether Illinois Medicaid applies to the specific facility, services, and plan. Long-stay nursing-home rules do not establish coverage for a short rehab stay."
      }
    },
    va: {
      title: "VA benefits",
      link: "https://www.va.gov/pension/aid-attendance-housebound/",
      linkText: "VA: Aid and Attendance",
      guide: "/guides/va-aid-and-attendance-benefit/",
      guideText: "VA Aid and Attendance, explained",
      more: { "*": null,
              unsure: "/guides/va-veteran-directed-care-program/",
              independent: "/guides/va-veteran-directed-care-program/" },
      moreText: { "*": null,
                  unsure: "VA-paid care at home (Veteran-Directed Care)",
                  independent: "VA-paid care at home (Veteran-Directed Care)" },
      summary: {
        unsure: "A qualifying Veteran or survivor who receives a VA pension may be eligible for extra Aid and Attendance or Housebound payments. This is not automatic payment of a care bill.",
        independent: "A qualifying Veteran or survivor receiving a VA pension may get extra payments if benefit conditions are met. Independent living by itself does not establish eligibility.",
        assisted: "Some eligible Veterans or survivors receiving a VA pension may receive Aid and Attendance or Housebound payments to help with costs. Benefits depend on the individual.",
        memory: "Some eligible Veterans or survivors receiving a VA pension may receive additional Aid and Attendance or Housebound payments. A memory-care setting alone does not guarantee eligibility.",
        skilled: "Eligible Veterans or survivors receiving a VA pension may qualify for additional Aid and Attendance or Housebound payments. This is distinct from VA health-care facility coverage.",
        rehab: "A Veteran or survivor may have VA-related benefit options, but a pension supplement is not the same as coverage for a specific rehabilitation admission."
      }
    },
    ltci: {
      title: "Long-term-care insurance",
      link: "https://idoi.illinois.gov/consumers/consumerinsurance/lifeannuities/long-term-care.html",
      linkText: "Illinois Department of Insurance: policy guide",
      guide: null,
      guideText: null,
      more: null,
      moreText: null,
      summary: {
        unsure: "An existing policy may pay for specified long-term-care services. Read the policy's covered settings, benefit triggers, waiting period, limits and exclusions.",
        independent: "A long-term-care policy usually has benefit triggers tied to care needs, not a voluntary lifestyle move. Ask the insurer for written confirmation.",
        assisted: "An existing policy may help with assisted-living services if that setting and the care needs meet the contract's terms. Confirm limits in writing.",
        memory: "An existing policy may help with memory-care costs, depending on the policy's covered facilities and benefit triggers. Confirm in writing.",
        skilled: "An existing policy may contribute to nursing-home care if the contract's benefit triggers and limits are satisfied. Confirm in writing.",
        rehab: "An existing policy may have relevant benefits, but it is not a substitute for verifying Medicare or other coverage for rehabilitation."
      }
    },
    private: {
      title: "Private payment and a written quote",
      /* The cost section on this page carries one card per level of care,
         including the honest "no statewide figure" ones, so it is the
         destination for every level. The assisted-living cost guide is
         about assisted living only, so only assisted living links to it. */
      link: { "*": COST_SECTION,
              assisted: "/guides/assisted-living-cost-illinois/",
              independent: "/guides/independent-living-evanston/" },
      linkText: { "*": "What each level of care usually costs in Illinois",
                  assisted: "What assisted living actually costs in Illinois",
                  memory: "Memory-care costs in Illinois, and why no median is shown",
                  skilled: "What a nursing home usually costs in Illinois",
                  rehab: "Short-term rehabilitation costs in Illinois",
                  independent: "What independent living includes, and what it costs" },
      guide: { "*": null, assisted: COST_SECTION, independent: COST_SECTION },
      guideText: { "*": null, assisted: "Cost figures for every level of care", independent: "Cost figures for every level of care" },
      more: null,
      moreText: null,
      summary: {
        unsure: "Ask each community for a written breakdown of housing, personal care, medical services, added fees and increases. Costs vary by setting.",
        independent: "Ask for apartment or cottage fees, any entrance fee, included services, optional extras and annual increases. A statewide independent-living median is not available here.",
        assisted: "Ask for base rent, the assessed care tier, medication charges, one-time fees and how increases are calculated. Compare the total rather than base rent alone.",
        memory: "Ask for a written memory-care quote covering housing, supervision, care tiers, medication support and changes in needs.",
        skilled: "Ask for the full nursing-home rate, what it includes, how costs change after any temporary coverage ends, and whether Medicaid is accepted.",
        rehab: "Ask the provider and insurer for an estimate covering the expected stay, daily coinsurance, therapy and anything outside the benefit."
      }
    }
  });
  const REASON_TEXT = Object.freeze({
    veteran: "Moved up because you answered Yes: the person is a Veteran or surviving spouse.",
    policy: "Moved up because you answered Yes: the person already has long-term-care insurance."
  });
  function normalizeCare(id) {
    if (id === "no_need" || id === "direct" || id == null) return "unsure";
    return Object.prototype.hasOwnProperty.call(CARE, id) ? id : "unsure";
  }
  function pick(field, care) {
    if (field === null || typeof field !== "object") return field;
    return Object.prototype.hasOwnProperty.call(field, care) ? field[care] : field["*"];
  }
  function getRoutes(care, veteran, policy) {
    const id = normalizeCare(care);
    const keys = BASE_ORDER[id].slice();
    const reason = {};
    function promote(key, why) {
      const i = keys.indexOf(key);
      if (i >= 0) { keys.splice(i, 1); keys.unshift(key); reason[key] = why; }
    }
    if (veteran === "yes") promote("va", "veteran");
    if (policy === "yes") promote("ltci", "policy");
    return keys.map(key => ({
      id: key,
      title: ROUTES[key].title,
      summary: ROUTES[key].summary[id],
      link: pick(ROUTES[key].link, id),
      linkText: pick(ROUTES[key].linkText, id),
      guide: pick(ROUTES[key].guide, id),
      guideText: pick(ROUTES[key].guideText, id),
      more: pick(ROUTES[key].more, id),
      moreText: pick(ROUTES[key].moreText, id),
      reason: reason[key] || null
    }));
  }
  function anchor(href, text) {
    const external = href.charAt(0) !== "/";
    return '<a href="' + href + '"' + (external ? ' target="_blank" rel="noopener"' : '') + '>' +
      text + (external ? ' <span class="paynav__ext" aria-hidden="true">&#8599;</span>' : '') + '</a>';
  }
  function rankLabel(i, care, reason) {
    const n = "Option " + (i + 1);
    if (reason) return n + " &middot; Moved up by your answer";
    if (i === 0 && care !== "unsure") return n + " &middot; Worth checking first";
    return n;
  }
  function renderCards(care, veteran, policy) {
    const id = normalizeCare(care);
    return getRoutes(id, veteran, policy).map((r, i) => {
      const lead = r.reason || (i === 0 && id !== "unsure");
      return '<li class="paynav__route' + (lead ? ' paynav__route--lead' : '') + '">' +
        '<p class="paynav__rank">' + rankLabel(i, id, r.reason) + '</p>' +
        '<h4>' + r.title + '</h4>' +
        (r.reason ? '<p class="paynav__why">' + REASON_TEXT[r.reason] + '</p>' : '') +
        '<p>' + r.summary + '</p>' +
        '<p class="paynav__links">' + anchor(r.link, r.linkText) +
        (r.guide ? anchor(r.guide, r.guideText) : '') +
        (r.more ? anchor(r.more, r.moreText) : '') +
        '</p></li>';
    }).join("");
  }
  let widget = null, stage = 0, state = null, emitted = {};
  const QUESTIONS = [
    { question: "What kind of care are you exploring?", key: "care",
      choices: Object.keys(CARE).map(id => ({ id: id, label: CARE[id] })) },
    { question: "Is the person a Veteran or surviving spouse?", key: "veteran",
      choices: [{id:"yes",label:"Yes"},{id:"no",label:"No"},{id:"unsure",label:"Not sure"}] },
    { question: "Does the person already have long-term-care insurance?",
      key: "policy", choices: [{id:"yes",label:"Yes"},{id:"no",label:"No"},{id:"unsure",label:"Not sure"}] }
  ];
  /* Literal paths, not built at runtime: build-guides.py's write_beacons()
     reads these string literals and creates the matching file in /t/ on
     the next build, so a new beacon can never fire at a 404. */
  const BEACONS = Object.freeze({
    "pay-nav-started":   "/t/pay-nav-started.txt",
    "pay-nav-completed": "/t/pay-nav-completed.txt"
  });
  function beacon(name) {
    const path = BEACONS[name];
    if (!path || emitted[name]) return;
    emitted[name] = true;
    if (root && typeof root.fetch === "function") {
      try { root.fetch(path, {cache:"no-store",keepalive:true}).catch(() => {}); }
      catch (e) { /* analytics never blocks the tool */ }
    }
  }
  function carriedLine() {
    /* The care type in play, shown on questions 2 and 3 whether it came
       from the assessment result or from question 1, with a way to change
       it. A visitor should never have to wonder what the tool assumed. */
    if (!state || !state.care) return '';
    return '<p class="paynav__carried">Care type: <strong>' + CARE[state.care] + '</strong> ' +
      '<button type="button" class="paynav__change" data-pay-change>Change</button></p>';
  }
  function resultsHint(care) {
    return (care === "unsure"
      ? 'In no particular order. '
      : 'Ordered for ' + CARE[care].toLowerCase() + '. ') +
      'A &ldquo;yes&rdquo; moves an option up but never changes what it covers. Nothing here decides eligibility &mdash; the agency, insurer or community does.';
  }
  function render(moveFocus) {
    if (!widget) return;
    const step = stage;
    const question = QUESTIONS[step];
    if (question) {
      const picked = state ? state[question.key] : null;
      widget.innerHTML =
        '<div class="paynav__progress">Question ' + (step + 1) + ' of 3</div>' +
        (step > 0 ? carriedLine() : '') +
        '<h3 class="paynav__question" tabindex="-1">' + question.question + '</h3>' +
        (step === 0 ? '<p class="paynav__hint">Not sure is a complete answer. No care setting will be assumed.</p>' : '') +
        '<div class="paynav__choices">' +
        question.choices.map(c =>
          '<button type="button" class="paynav__choice' + (picked === c.id ? ' is-selected' : '') +
          '" data-pay-value="' + c.id + '" aria-pressed="' + (picked === c.id ? 'true' : 'false') + '">' +
          c.label + '</button>').join("") + '</div>' +
        (step > 0 ? '<div class="paynav__actions"><button type="button" class="paynav__back" data-pay-back>&larr; Back</button></div>' : '') +
        '<p class="paynav__fine">These answers stay on this device. No account or contact details.</p>';
    } else {
      const care = normalizeCare(state.care);
      widget.innerHTML =
        '<p class="paynav__progress">Your payment starting points</p>' +
        '<h3 class="paynav__question" tabindex="-1">' +
        (care === "unsure" ? 'Nothing assumed about the type of care' : CARE[care]) + '</h3>' +
        '<p class="paynav__hint">' + resultsHint(care) + '</p>' +
        '<p class="paynav__order">' + ORDER_WHY[care] + '</p>' +
        '<ol class="paynav__routes">' +
        renderCards(care, state.veteran, state.policy) + '</ol>' +
        '<p class="paynav__fine">Coverage, eligibility, benefit amounts and whether a particular community accepts a program must be confirmed directly with the agency, insurer or community. This page is educational guidance, not financial or legal advice.</p>' +
        '<div class="paynav__actions"><button type="button" class="paynav__back" data-pay-back>&larr; Back</button>' +
        '<button type="button" class="paynav__restart" data-pay-restart>Start again</button></div>';
    }
    /* Focus the new heading only after the visitor did something. On page
       load the widget just appears; stealing focus there would drop every
       keyboard and screen-reader user into the middle of the page. */
    if (!moveFocus) return;
    const heading = widget.querySelector(".paynav__question");
    if (!heading) return;
    try { heading.focus({preventScroll:true}); } catch (e) { heading.focus(); }
    keepHeadingVisible(heading);
  }
  function keepHeadingVisible(heading) {
    /* After answering the last choice on a long question, the next heading
       can sit above the sticky nav on a short phone screen. Nudge it down
       only when it is actually hidden; never scroll otherwise. */
    try {
      const nav = root.document.querySelector("nav");
      const navH = nav ? nav.getBoundingClientRect().height : 0;
      const top = heading.getBoundingClientRect().top;
      if (top < navH + 8) root.scrollBy({top: top - navH - 16, left: 0});
    } catch (e) { /* layout queries are best-effort */ }
  }
  function start(care) {
    if (!widget && root && root.document) widget = root.document.getElementById("paying-nav-widget");
    if (!widget) return false;
    const known = care != null && CARE[care] && care !== "unsure";
    state = {care:known ? care : null, veteran:null, policy:null};
    stage = known ? 1 : 0;
    beacon("pay-nav-started"); // also for assessment-prefilled starts
    render(true);
    return true;
  }
  function init() {
    if (!root || !root.document) return false;
    widget = root.document.getElementById("paying-nav-widget");
    if (!widget) return false;
    state = {care:null,veteran:null,policy:null};
    stage = 0;
    render(false);
    widget.addEventListener("click", function(event) {
      const choice = event.target.closest("[data-pay-value]");
      const back = event.target.closest("[data-pay-back]");
      const change = event.target.closest("[data-pay-change]");
      const restart = event.target.closest("[data-pay-restart]");
      if (choice && stage < 3) {
        const q = QUESTIONS[stage];
        const value = choice.getAttribute("data-pay-value");
        if (!q.choices.some(c => c.id === value)) return;
        if (stage === 0) beacon("pay-nav-started");
        state[q.key] = value;
        stage += 1;
        if (stage === 3) beacon("pay-nav-completed");
        render(true);
      } else if (back) {
        /* Earlier answers are kept and shown highlighted, including a care
           type that arrived from the assessment result: Back reaches
           question 1 with that choice marked, and any choice replaces it. */
        stage = Math.max(0, stage - 1);
        render(true);
      } else if (change) {
        stage = 0;
        render(true);
      } else if (restart) {
        state = {care:null,veteran:null,policy:null};
        stage = 0;
        render(true);
      }
    });
    root.document.addEventListener("click", function(event) {
      const link = event.target.closest("[data-pay-nav-care]");
      if (!link) return;
      event.preventDefault();
      const id = normalizeCare(link.getAttribute("data-pay-nav-care"));
      start(id);
      /* Setting the hash scrolls only when it changes. The second visit from
         the same result page needs the explicit scroll. */
      root.location.hash = "paying-nav";
      const section = root.document.getElementById("paying-nav");
      if (section && typeof section.scrollIntoView === "function") section.scrollIntoView({block:"start"});
    });
    return true;
  }
  const api = {normalizeCare, getRoutes, renderCards, init, start, CARE, ROUTES, BEACONS, ORDER_WHY, REASON_TEXT, BASE_ORDER};
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  if (root && root.document) { root.PaymentNavigator = api; init(); }
})(typeof window !== "undefined" ? window : null);
