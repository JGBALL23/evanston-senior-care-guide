/* ============================================================
   EVANSTON SENIOR CARE GUIDE — CARE-LEVEL ASSESSMENT
   Deterministic rules. No AI, no API, no backend, no tracking
   of personal answers. Nothing a family types leaves the device.

   The result must be DEFENSIBLE: every outcome names the exact
   answers that produced it. No provider is recommended, ranked,
   or weighted anywhere in this file.
   ============================================================ */

/* ---------- 1. QUESTIONS ------------------------------------
   Six questions, plain language, one idea each. Written the way
   an adult child describes a parent, not the way a clinician
   charts one. Each option carries the signals it implies.      */
const QUESTIONS = [
  {
    id: "adl",
    short: "Help with bathing, dressing or the bathroom",
    text: "Does your parent or loved one need hands-on help with bathing, dressing or using the bathroom?",
    textSelf: "Do you need hands-on help with bathing, dressing or using the bathroom?",
    helpSelf: "These are the tasks that most often decide what level of care a community can provide.",
    help: "These are the tasks that most often decide what level of care a community can provide.",
    options: [
      { label: "No help needed", signals: {} },
      { label: "A little help — mostly reminders or standby", signals: { adl: 1 } },
      { label: "Real hands-on help with one or two of these", signals: { adl: 2 } },
      { label: "Hands-on help with all of them", signals: { adl: 3 } }
    ]
  },
  {
    id: "memory",
    short: "Memory and judgment",
    text: "How is your parent or loved one's memory and judgment?",
    textSelf: "How is your memory and judgment?",
    helpSelf: "Answer about the last few months, not your worst single day.",
    help: "Answer about the last few months, not their worst single day.",
    options: [
      { label: "No real concerns", signals: {} },
      { label: "Forgetful, but still safe and aware", signals: { memory: 1 } },
      { label: "Gets confused about time, place or people", signals: { memory: 2 } },
      { label: "Has wandered, left the stove on, or been unsafe alone", signals: { memory: 3, unsafe: 1 } }
    ]
  },
  {
    id: "medical",
    short: "Day-to-day medical needs",
    text: "What medical help does your parent or loved one need day to day?",
    textSelf: "What medical help do you need day to day?",
    helpSelf: "Think about what a nurse would have to do, not what a doctor prescribes.",
    help: "Think about what a nurse would have to do, not what a doctor prescribes.",
    options: [
      { label: "Nothing beyond normal check-ups", signals: {} },
      { label: "Medications managed or reminded", signals: { medical: 1 } },
      { label: "Wound care, injections, oxygen, catheter or feeding tube", signals: { medical: 2 } },
      { label: "A nurse available around the clock", signals: { medical: 3 } }
    ]
  },
  {
    id: "alone",
    short: "Safe to be alone",
    text: "Is it safe for your parent or loved one to be alone?",
    textSelf: "Is it safe for you to be on your own?",
    helpSelf: "This question decides more than almost any other.",
    help: "This question decides more than almost any other.",
    options: [
      { label: "Yes, for days at a time", signals: {} },
      { label: "Yes, but only for a few hours", signals: { supervision: 1 } },
      { label: "Not really — something would go wrong", signals: { supervision: 2 } },
      { label: "No, someone needs to be there always", signals: { supervision: 3, unsafe: 1 } }
    ]
  },
  {
    id: "hospital",
    short: "Hospital in the last 30 days",
    text: "Has your parent or loved one been in the hospital in the last 30 days?",
    textSelf: "Have you been in the hospital in the last 30 days?",
    helpSelf: "A recent stay often changes the answer completely, and it is usually temporary.",
    help: "A recent stay often changes the answer completely, and it is usually temporary.",
    options: [
      { label: "No", signals: {} },
      { label: "Yes, and they are getting stronger", signals: { recent: 1, recovering: 1 } },
      { label: "Yes, and they are not bouncing back", signals: { recent: 1, declining: 1 } },
      { label: "They are in the hospital right now", signals: { recent: 1, inHospital: 1 } }
    ]
  },
  {
    id: "household",
    short: "Cooking, cleaning, driving, bills",
    text: "How are the everyday things going — cooking, cleaning, driving, bills?",
    textSelf: "How are the everyday things going \u2014 cooking, cleaning, driving, bills?",
    helpSelf: "Most people hand these over long before they need help bathing or dressing.",
    help: "People usually lose these before they lose bathing and dressing.",
    /* The lifestyle option, added 2026-10-26, is the only answer in the
       whole assessment that describes a WANT rather than a need. It exists
       because the six questions measured deficits only: someone fit and
       independent who is simply tired of the house answered "managing
       fine" six times, matched no rule at all, and was told nothing here
       describes a need for care. True, and a dead end for exactly the
       person independent living is built for.

       It sits at index 1 so the list still reads from most to least
       capable. Shifting the iadl options down by one is safe: answers are
       held in memory for one session and nothing persists an index. */
    options: [
      { label: "Managing fine", signals: {} },
      { label: "Managing fine — but the house and yard are more work than I want",
        signals: { lifestyle: 1 } },
      { label: "Slipping — meals skipped, mail piling up", signals: { iadl: 1 } },
      { label: "Needs help with most of it", signals: { iadl: 2 } },
      { label: "Cannot do these at all anymore", signals: { iadl: 3 } }
    ]
  }
];

/* ---------- 1b. WHO IS ANSWERING ---------------------------
   Framing only. Every question below carries a second wording for
   someone answering about themselves, because the original six were
   written in the third person about someone else, and an independent
   older adult reading "does your parent need help" is being told in the
   first line that the page is not for them. The parent framing also says
   "or loved one", because the selector offers "a parent or someone else"
   and plenty of people doing this are a spouse, a sibling or a
   neighbour.

   `textSelf` and `helpSelf` change NOTHING about scoring. The
   signals live on the options, the options are identical in both
   framings, and `assess()` never sees the audience. A test pins
   that: both framings must produce byte-identical results across
   all 4096 answer combinations.                                  */

/* ---------- 2. CARE LEVELS ----------------------------------
   Illinois median monthly costs, 2026. Ranges, because a single
   number is always wrong for somebody.                          */
const CARE_LEVELS = {
  independent: {
    id: "independent",
    name: "Independent Living",
    summary: "What appears to be slipping is the running of the house rather than personal care itself.",
    looksLike: [
      "A private apartment, with meals, housekeeping and transport included",
      "Generally no hands-on personal care, and typically no nursing staff on the floor",
      "Activities, dining and neighbours — which is often the actual need"
    ],
    cost: {
      label: "Independent Living Costs",
      figure: null,
      unit: null,
      basis: "No statewide median is shown here because the CareScout survey does not report an Illinois figure for independent living. Publishing one anyway would mean inventing it.",
      survey: null,
      url: null,
      note: "Pricing depends on apartment size, the community, and which services are bundled into the monthly fee rather than billed on top. Ask for a written fee schedule showing what is included and what is extra."
    },
    nextSteps: [
      "Ask what happens if care needs increase later — can they stay, or must they move?",
      "Ask whether meals, housekeeping, and transport are included or billed separately",
      "Visit at a mealtime. The dining room tells you more than the brochure"
    ]
  },
  assisted: {
    id: "assisted",
    name: "Assisted Living",
    summary: "The help described is hands-on support with daily personal care, rather than around-the-clock nursing.",
    looksLike: [
      "Staff typically help with bathing, dressing, toileting and medications",
      "A private apartment, with meals and housekeeping",
      "Care staff on site at all hours; generally not licensed as a medical facility"
    ],
    cost: {
      label: "Estimated Illinois Cost",
      figure: "$6,219",
      unit: "per month",
      basis: "Illinois assisted living median.",
      survey: "CareScout 2025 Cost of Care Survey, published 2026.",
      url: "https://assets.carescout.com/x/5c90319b6a/298701.pdf",
      note: "A statewide median. The Chicago metro generally runs higher than downstate, and base rates usually exclude care tiers — ask what the rate becomes at the level actually needed."
    },
    nextSteps: [
      "Ask exactly which tasks are included at the base rate and which add cost",
      "Ask how they reassess care levels, and how often the price changes as a result",
      "Ask the staff-to-resident ratio overnight, not during the day"
    ]
  },
  memory: {
    id: "memory",
    name: "Memory Care",
    summary: "Safety may now be as important to consider as day-to-day assistance.",
    looksLike: [
      "Usually a secured area, designed so someone cannot wander out unnoticed",
      "Staff trained specifically in dementia care",
      "Smaller groups, simpler routines, structured days"
    ],
    cost: {
      label: "Memory Care Costs",
      figure: null,
      unit: null,
      basis: "The CareScout survey does not separately report an Illinois memory-care median, so no figure is shown here.",
      survey: null,
      url: null,
      note: "Memory care costs vary depending on location, accommodation type, staffing, and the level of assistance required. Request a detailed written estimate from communities you are considering."
    },
    nextSteps: [
      "Ask what their staff does when a resident becomes agitated or tries to leave",
      "Ask about staff turnover in the memory unit specifically",
      "Visit late afternoon. Dementia symptoms often peak then, and so does the real staffing picture"
    ]
  },
  skilled: {
    id: "skilled",
    name: "Skilled Nursing",
    summary: "The needs described are clinical ones, which usually call for nursing available around the clock.",
    looksLike: [
      "Licensed nursing care available around the clock",
      "Wound care, IV medication, oxygen, feeding tubes, complex conditions",
      "A medical setting, usually a room rather than an apartment"
    ],
    cost: {
      label: "Estimated Illinois Cost",
      figure: "$8,304",
      unit: "per month, semi-private room",
      basis: "Illinois nursing home median. A private room has a separate median of $9,216 a month.",
      survey: "CareScout 2025 Cost of Care Survey, published 2026.",
      url: "https://assets.carescout.com/x/5c90319b6a/298701.pdf",
      note: "These are long-stay nursing home figures, not the out-of-pocket cost of a short rehabilitation stay. Illinois Medicaid may cover this level for those who meet eligibility rules."
    },
    nextSteps: [
      "Ask whether they accept Medicaid, and what happens when private funds run out",
      "Look up the facility on Medicare's Care Compare before you visit",
      "Ask how many residents each nurse covers on the night shift"
    ]
  },
  rehab: {
    id: "rehab",
    name: "Short-Term Rehabilitation",
    summary: "This reads as a temporary need rather than a permanent move — recovery first, then a longer-term decision.",
    looksLike: [
      "Physical, occupational and speech therapy, typically daily",
      "A stay measured in weeks, with going home as the goal",
      "May be covered by Medicare after a qualifying hospital stay — eligibility rules apply"
    ],
    cost: {
      label: "Short-Term Rehabilitation Costs",
      figure: null,
      unit: null,
      basis: "No statewide price is shown here, because what a family actually pays depends on insurance, Medicare eligibility, length of stay and which services are delivered. Long-stay nursing home medians do not describe a short rehabilitation stay and are not used as a substitute.",
      survey: null,
      url: null,
      note: "Under Original Medicare, a qualifying stay may carry $0 daily coinsurance for days 1–20, then $217 a day for days 21–100 in 2026, after the applicable Part A deductible. Eligibility rules apply, and Medicare Advantage plans may have different requirements and cost-sharing. Confirm with the hospital discharge planner and your plan."
    },
    nextSteps: [
      "Talk to the hospital discharge planner TODAY — this window is short and it closes",
      "Ask how many therapy days per week, and for how long",
      "Ask what the plan is if they cannot safely go home afterward"
    ]
  }
};

/* ---------- 3. THE RULES ------------------------------------
   Ordered, and the order IS the reasoning. The first rule that
   fires wins, and it records why. A family can read the reason
   and check it against their own answers.                       */
const RULES = [
  {
    /* Rehab is evaluated first because a recent hospital stay usually
       IS the whole story, and a family in that window should not be
       told to make a permanent decision.

       NARROWED 2026-10-17. It used to fire regardless of how much
       nursing was described, so a family answering "needs a nurse
       around the clock" was routed to Short-Term Rehabilitation
       purely because of the hospital question. That silently
       overrode the single most serious thing they had told us.

       Around-the-clock nursing (medical >= 3) now falls through to
       the skilled rule, which is also where rehabilitation is
       delivered — so the family still reads about recovery, and the
       explanation quotes the answer they actually gave. Lower
       medical answers are unaffected: recovery still leads. */
    level: "rehab",
    cites: ["hospital", "adl", "medical"],
    when: (s) => s.recent && (s.recovering || s.inHospital) &&
                 !s.unsafe && s.medical < 3,
    because: (a) => 'a hospital stay in the last 30 days with signs of recovery — "' +
      a.hospital + '" — usually points to rehabilitation first, before any permanent decision'
  },
  {
    level: "memory",
    cites: ["memory", "alone", "adl"],
    when: (s) => s.memory >= 3 || (s.memory >= 2 && s.supervision >= 2),
    because: (a) => 'the answer on memory and judgment — "' + a.memory +
      '" — together with how safe it is to be alone — "' + a.alone +
      '" — describes a safety problem rather than a help problem'
  },
  {
    level: "skilled",
    cites: ["medical", "adl", "hospital"],
    when: (s) => s.medical >= 3 || (s.medical >= 2 && s.adl >= 2) || (s.declining && s.adl >= 2),
    because: (a) => 'the medical needs described — "' + a.medical +
      '" — are the kind that require licensed nurses on duty, not care staff'
  },
  {
    level: "assisted",
    cites: ["adl", "alone", "household"],
    when: (s) => s.adl >= 2 || s.supervision >= 2 || (s.adl >= 1 && s.iadl >= 2),
    because: (a) => 'hands-on help with daily personal care — "' + a.adl +
      '" — without round-the-clock nursing needs is what assisted living exists for'
  },
  {
    level: "assisted",
    cites: ["medical", "adl"],
    when: (s) => s.medical >= 1 && s.adl >= 1,
    because: (a) => 'medication help — "' + a.medical +
      '" — alongside some personal care is normally handled in assisted living'
  },
  {
    level: "independent",
    cites: ["household", "memory", "adl"],
    when: (s) => s.iadl >= 1 || s.memory >= 1,
    because: (a) => 'the everyday things are slipping — "' + a.household +
      '" — while personal care is still managed, which is the independent living picture'
  },
  {
    /* INDEPENDENT LIVING BY CHOICE — added 2026-10-26, and deliberately
       LAST so it can never displace a safety rule. Every rule above fires
       on a care or safety signal; this one fires only when none of them
       did, and only when the person said the upkeep of the house is more
       work than they want.

       The `when` re-states the absence of every deficit signal rather
       than trusting rule order alone. Order already protects this, but a
       rule that quietly becomes reachable after someone reorders the list
       is the kind of bug that routes a person who needs help to a
       lifestyle page. Two locks, not one.

       variant: "lifestyle" tells the result page to frame this as a move
       someone is choosing, not a level of care someone needs. */
    level: "independent",
    variant: "lifestyle",
    cites: ["household", "adl", "alone"],
    when: (s) => s.lifestyle >= 1 &&
                 !s.adl && !s.memory && !s.medical && !s.supervision &&
                 !s.iadl && !s.unsafe && !s.recent,
    because: (a) => 'nothing here describes a need for care — the answer on ' +
      'the everyday things, "' + a.household + '", describes wanting less ' +
      'house to look after, which is the question independent living answers'
  }
];

/* ---------- 4. SCORING -------------------------------------- */

/* answers: { questionId: optionIndex }. Returns the level, the
   reason, and every signal, so the result can be audited. */
/* TWO TO FOUR SPECIFIC REASONS, drawn from what they actually chose.
   Each one names the question and quotes their own answer, so the result
   can be audited rather than believed. Answers that carry no signal are
   skipped — "No help needed" explains nothing. */
function reasonsFor(rule, answers, chosen) {
  const byId = {};
  QUESTIONS.forEach((q) => { byId[q.id] = q; });

  const cited = (rule.cites || []).map((id) => {
    const q = byId[id];
    if (!q || !chosen[id]) return null;
    const picked = q.options[answers[id]];
    const carries = picked && Object.keys(picked.signals || {}).length > 0;
    return carries ? { question: q.short || q.text, answer: chosen[id] } : null;
  }).filter(Boolean);

  /* Fewer than two? Add the next most telling answer so the result always
     shows its work. */
  if (cited.length < 2) {
    QUESTIONS.forEach((q) => {
      if (cited.length >= 2) return;
      if ((rule.cites || []).indexOf(q.id) !== -1) return;
      const picked = q.options[answers[q.id]];
      if (picked && Object.keys(picked.signals || {}).length > 0) {
        cited.push({ question: q.short || q.text, answer: chosen[q.id] });
      }
    });
  }
  return cited.slice(0, 4);
}

function assess(answers) {
  const signals = {};
  const chosen = {};

  QUESTIONS.forEach((q) => {
    const pick = q.options[answers[q.id]];
    if (!pick) return;
    chosen[q.id] = pick.label;
    Object.keys(pick.signals).forEach((key) => {
      signals[key] = Math.max(signals[key] || 0, pick.signals[key]);
    });
  });

  const answered = Object.keys(chosen).length;
  if (answered < QUESTIONS.length) {
    return { status: "incomplete", answered, total: QUESTIONS.length };
  }

  const rule = RULES.find((r) => r.when(signals));

  /* Nothing fired: no care need was described. Saying so is the
     honest answer, and it is a real outcome, not a failure. */
  if (!rule) {
    return {
      status: "no_need",
      signals,
      chosen,
      level: null,
      reason: "nothing in these answers describes a need for a higher level of care yet"
    };
  }

  return {
    status: "matched",
    level: CARE_LEVELS[rule.level],
    /* "lifestyle" only on the by-choice independent living rule. Absent
       everywhere else, so no care result can be rendered as a lifestyle
       move by accident. */
    variant: rule.variant || null,
    reason: rule.because(chosen),
    reasons: reasonsFor(rule, answers, chosen),
    signals,
    chosen,
    /* Everything else worth looking at, so a family is not boxed in. */
    alsoConsider: nearbyLevels(rule.level, signals)
  };
}

/* The honest neighbours of a result. A family deciding this is
   rarely choosing between one option and nothing. */
function nearbyLevels(levelId, signals) {
  const near = [];
  if (levelId === "assisted" && signals.memory >= 1) near.push(CARE_LEVELS.memory);
  if (levelId === "assisted" && signals.medical >= 2) near.push(CARE_LEVELS.skilled);
  if (levelId === "memory") near.push(CARE_LEVELS.assisted);
  if (levelId === "skilled" && signals.recent) near.push(CARE_LEVELS.rehab);
  if (levelId === "independent" && signals.adl >= 1) near.push(CARE_LEVELS.assisted);
  if (levelId === "rehab") near.push(CARE_LEVELS.skilled);
  return near;
}

/* ---------- 5. WHAT THIS IS NOT ----------------------------- */
const DISCLAIMER =
  "This is a general guide, not medical advice and not a clinical assessment. " +
  "Only a doctor, nurse or licensed care assessor can determine what level of " +
  "care someone needs. Use this to understand the options and ask better " +
  "questions — then confirm with a professional who has examined the " +
  "person this is about.";

if (typeof module !== "undefined") {
  module.exports = { QUESTIONS, CARE_LEVELS, RULES, assess, DISCLAIMER };
}
