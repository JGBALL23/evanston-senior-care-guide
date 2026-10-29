/* Workflow #5: optional Payment Options Navigator.
   Three answers stay in the browser. No income, diagnosis, name, eligibility
   decision, ranking of providers, or lead collection. A "yes" only changes
   the order of the same fixed funding explanations. */
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
  const BASE_ORDER = Object.freeze({
    unsure:      ["medicaid", "medicare", "private", "va", "ltci"],
    independent: ["private", "ltci", "va", "medicaid", "medicare"],
    assisted:    ["medicaid", "private", "ltci", "va", "medicare"],
    memory:      ["medicaid", "private", "ltci", "va", "medicare"],
    skilled:     ["medicaid", "medicare", "private", "ltci", "va"],
    rehab:       ["medicare", "medicaid", "private", "ltci", "va"]
  });
  const ROUTES = Object.freeze({
    medicare: {
      title: "Medicare",
      link: "https://www.medicare.gov/coverage/long-term-care",
      linkText: "Medicare: long-term care coverage",
      guide: "/guides/does-medicare-pay-for-senior-care/",
      guideText: "What Medicare pays for",
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
      link: "https://hfs.illinois.gov/medicalclients/ltc.html",
      linkText: "Illinois HFS: long-term care",
      guide: "/guides/illinois-medicaid-long-term-care/",
      guideText: "Illinois Medicaid long-term care guide",
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
      guideText: "VA Aid and Attendance guide",
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
      link: "/guides/assisted-living-cost-illinois/",
      linkText: "Understanding care costs",
      guide: null,
      guideText: null,
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
  function normalizeCare(id) {
    if (id === "no_need" || id === "direct" || id == null) return "unsure";
    return Object.prototype.hasOwnProperty.call(CARE, id) ? id : "unsure";
  }
  function getRoutes(care, veteran, policy) {
    const id = normalizeCare(care);
    const keys = BASE_ORDER[id].slice();
    function promote(key) {
      const i = keys.indexOf(key);
      if (i >= 0) { keys.splice(i, 1); keys.unshift(key); }
    }
    if (veteran === "yes") promote("va");
    if (policy === "yes") promote("ltci");
    return keys.map(key => ({
      id: key,
      title: ROUTES[key].title,
      summary: ROUTES[key].summary[id],
      link: ROUTES[key].link,
      linkText: ROUTES[key].linkText,
      guide: ROUTES[key].guide,
      guideText: ROUTES[key].guideText
    }));
  }
  function renderCards(care, veteran, policy) {
    return getRoutes(care, veteran, policy).map((r, i) =>
      '<li class="paynav__route">' +
      '<p class="paynav__rank">OPTION ' + (i + 1) + '</p>' +
      '<h4>' + r.title + '</h4><p>' + r.summary + '</p>' +
      '<p class="paynav__links"><a href="' + r.link + '"' +
      (r.link.charAt(0) === "/" ? "" : ' target="_blank" rel="noopener"') +
      '>' + r.linkText + '</a>' +
      (r.guide ? ' · <a href="' + r.guide + '">' + r.guideText + '</a>' : '') +
      '</p></li>'
    ).join("");
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
  function beacon(name) {
    if (emitted[name]) return;
    emitted[name] = true;
    if (root && typeof root.fetch === "function") {
      try { root.fetch("/t/" + name + ".txt", {cache:"no-store",keepalive:true}).catch(() => {}); }
      catch (e) { /* analytics never blocks the tool */ }
    }
  }
  function render() {
    if (!widget) return;
    const step = stage;
    const question = QUESTIONS[step];
    if (question) {
      widget.innerHTML =
        '<div class="paynav__progress">Question ' + (step + 1) + ' of 3</div>' +
        '<h3 class="paynav__question" tabindex="-1">' + question.question + '</h3>' +
        (step === 0 ? '<p class="paynav__hint">Not sure is a complete answer. No care setting will be assumed.</p>' : '') +
        '<div class="paynav__choices">' +
        question.choices.map(c =>
          '<button type="button" class="paynav__choice" data-pay-value="' + c.id + '">' +
          c.label + '</button>').join("") + '</div>' +
        (step > 0 ? '<button type="button" class="paynav__back" data-pay-back>Back</button>' : '') +
        '<p class="paynav__fine">These answers stay on this device. No account or contact details.</p>';
    } else {
      widget.innerHTML =
        '<p class="paynav__progress">Your payment starting points</p>' +
        '<h3 class="paynav__question" tabindex="-1">' +
        (state.care === "unsure" ? 'Nothing assumed about the type of care' : CARE[state.care]) + '</h3>' +
        '<p class="paynav__hint">All five options remain visible. A “yes” may move an option higher, but never changes what it covers. This is not an eligibility decision.</p>' +
        '<ol class="paynav__routes">' +
        renderCards(state.care, state.veteran, state.policy) + '</ol>' +
        '<p class="paynav__fine">Coverage, eligibility, benefit amounts and whether a particular community accepts a program must be confirmed directly with the agency, insurer or community.</p>' +
        '<div class="paynav__actions"><button type="button" class="paynav__back" data-pay-back>Back</button>' +
        '<button type="button" class="paynav__restart" data-pay-restart>Start again</button></div>';
    }
    const heading = widget.querySelector(".paynav__question");
    if (heading) heading.focus({preventScroll:true});
  }
  function start(care) {
    if (!widget && root && root.document) widget = root.document.getElementById("paying-nav-widget");
    if (!widget) return false;
    const known = care != null && CARE[care] && care !== "unsure";
    state = {care:known ? care : null, veteran:null, policy:null};
    stage = known ? 1 : 0;
    beacon("pay-nav-started"); // also for assessment-prefilled starts
    render();
    return true;
  }
  function init() {
    if (!root || !root.document) return false;
    widget = root.document.getElementById("paying-nav-widget");
    if (!widget) return false;
    state = {care:null,veteran:null,policy:null};
    stage = 0;
    render();
    widget.addEventListener("click", function(event) {
      const choice = event.target.closest("[data-pay-value]");
      const back = event.target.closest("[data-pay-back]");
      const restart = event.target.closest("[data-pay-restart]");
      if (choice && stage < 3) {
        const q = QUESTIONS[stage];
        const value = choice.getAttribute("data-pay-value");
        if (!q.choices.some(c => c.id === value)) return;
        if (stage === 0) beacon("pay-nav-started");
        state[q.key] = value;
        stage += 1;
        if (stage === 3) beacon("pay-nav-completed");
        render();
      } else if (back) {
        stage = Math.max(0, stage - 1);
        if (stage === 0) state.care = null; // back from a prefill is editable
        render();
      } else if (restart) {
        state = {care:null,veteran:null,policy:null};
        stage = 0;
        render();
      }
    });
    root.document.addEventListener("click", function(event) {
      const link = event.target.closest("[data-pay-nav-care]");
      if (!link) return;
      event.preventDefault();
      const id = normalizeCare(link.getAttribute("data-pay-nav-care"));
      start(id);
      root.location.hash = "paying-nav";
    });
    return true;
  }
  const api = {normalizeCare, getRoutes, renderCards, init, start, CARE, ROUTES};
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  if (root && root.document) { root.PaymentNavigator = api; init(); }
})(typeof window !== "undefined" ? window : null);
