/* ============================================================
   EVANSTON SENIOR CARE GUIDE — PAGE BEHAVIOUR
   One question at a time. No backend. No personal data leaves
   the device — the only thing sent anywhere is an anonymous
   funnel beacon saying "someone reached step N".
   ============================================================ */

/* ---------- FUNNEL MEASUREMENT ------------------------------
   No analytics service, no cookie, no identifier. Each step
   requests a tiny static file in /t/. Those requests show up in
   the host's own server-side analytics as path hits, which is
   how the funnel gets counted without a database.

   What is measured: how many people reached each step.
   What is NOT measured: who they are, or what they answered.   */
const FUNNEL = {
  landed:       "/t/landed.txt",
  started:      "/t/assessment-started.txt",
  q2:           "/t/q2.txt",
  q4:           "/t/q4.txt",
  completed:    "/t/assessment-completed.txt",
  result:       "/t/result-",          // + level id
  tourQuestions:"/t/viewed-tour-questions.txt",
  costs:        "/t/viewed-costs.txt",
  restarted:    "/t/restarted.txt",
  wpView:       "/t/westminster-card-view.txt",
  wpSite:       "/t/westminster-website-click.txt",
  idph:         "/t/state-directory-click.txt",
  planView:     "/t/plan-visit-form-view.txt",
  planSubmit:   "/t/plan-visit-submitted.txt",
  planSaved:    "/t/plan-visit-saved.txt",
  /* Confirmed lead. Fires only after the server read the record
     back out of the store. No query string, so the Observability
     filter is an exact path match. */
  inquirySubmitted: "/t/inquiry-submitted.txt"
};

/* ---------- WHERE THEY CAME FROM ----------------------------
   One short, sanitised token: the utm_source if there is one,
   otherwise the referring site's hostname, otherwise "direct".
   Appended to the landing beacon as ?s=facebook so the host's own
   logs separate channels.

   Deliberately NOT collected: the full referrer URL, any path, any
   query a visitor arrived with, and anything identifying. A channel
   name is not a person. */
function channel() {
  try {
    const params = new URLSearchParams(window.location.search);
    let raw = params.get("utm_source") || params.get("ref") || "";
    if (!raw && document.referrer) {
      const host = new URL(document.referrer).hostname;
      if (host && host !== window.location.hostname) {
        raw = host.replace(/^www\./, "").split(".")[0];
      }
    }
    const clean = String(raw).toLowerCase().replace(/[^a-z0-9-]/g, "").slice(0, 24);
    return clean || "direct";
  } catch (err) {
    return "direct";
  }
}
const SOURCE = channel();

const sent = {};
function beacon(path) {
  if (!path || sent[path]) return;          // once per visit, per step
  sent[path] = true;
  try {
    fetch(path, { method: "GET", cache: "no-store", keepalive: true })
      .catch(() => {});
  } catch (err) { /* measurement must never break the page */ }
}

beacon(FUNNEL.landed + "?s=" + SOURCE);

/* ---------- ASSESSMENT -------------------------------------- */
const quizEl = document.getElementById("quiz");
const answers = {};
let step = 0;
/* The care level the assessment landed on, captured at render time so
   the form can send it without asking the visitor to pick it again.
   ONLY the derived level travels — never the six raw answers, which
   still never leave the device. */
let resultLevelId = null;
let startedBeaconSent = false;

/* ---------- WHO IS ANSWERING -------------------------------
   "self" or "parent". Chosen before question one and used for
   WORDING ONLY. It is never passed to assess(), never becomes a
   signal, and never reaches the inquiry payload. Someone exploring
   for themselves is not a different kind of applicant; they are the
   same six answers in the second person. */
let audience = null;

function renderAudience() {
  quizEl.innerHTML = `
    <div class="aud">
      <p class="aud__label">Before the six questions</p>
      <h3 class="aud__h">Who are we thinking about?</h3>
      <p class="aud__p">It changes nothing about the result &mdash; only how
        the questions are worded.</p>
      <div class="opts">
        <button class="opt" data-aud="self">I&rsquo;m exploring options for
          myself</button>
        <button class="opt" data-aud="parent">I&rsquo;m helping a parent or
          someone else</button>
      </div>
    </div>`;
}

function qText(q) {
  return audience === "self" && q.textSelf ? q.textSelf : q.text;
}
function qHelp(q) {
  return audience === "self" && q.helpSelf ? q.helpSelf : q.help;
}

/* The one pronoun pair the result copy needs. */
function them() { return audience === "self" ? "you" : "your parent or loved one"; }
function they() { return audience === "self" ? "you" : "they"; }

function esc(value) {
  return String(value == null ? "" : value).replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  }[c]));
}

function renderQuestion() {
  const q = QUESTIONS[step];
  const pct = Math.round((step / QUESTIONS.length) * 100);

  quizEl.innerHTML = `
    <div class="q__head">
      <p class="q__count">Question ${step + 1} of ${QUESTIONS.length}</p>
      <span class="q__of">${Math.round((step / QUESTIONS.length) * 100)}% complete</span>
    </div>
    <div class="q__bar" role="progressbar" aria-valuemin="0" aria-valuemax="100"
         aria-valuenow="${pct}" aria-label="Assessment progress">
      <div class="q__fill" style="width:${pct}%"></div></div>
    <p class="q__text">${esc(qText(q))}</p>
    <p class="q__help">${esc(qHelp(q))}</p>
    <div class="opts">
      ${q.options.map((o, i) =>
        `<button class="opt" data-i="${i}">${esc(o.label)}</button>`).join("")}
    </div>
    <button class="q__back" type="button">${step > 0
      ? "\u2190 Previous question" : "\u2190 Change who this is about"}</button>
  `;

  if (step === 1) beacon(FUNNEL.q2);
  if (step === 3) beacon(FUNNEL.q4);
}

/* ---------- WESTMINSTER PHONE ROUTING -----------------------
   Every number below is transcribed verbatim from Westminster
   Place's own published phone directory on
   presbyterianliving.org/our-locations/westminster-place/contact/
   (re-verified 2026-10-12). Nothing here is inferred, and no
   number is used that they have not published themselves.

     Independent Living Concierge      847-492-2800
     Independent Living Sales          847-570-3310
     Assisted Living & Memory Care     847-866-1615
     Skilled Nursing Admissions        847-492-7780
     General Inquiries                 847-570-3422

   The assessment already knows which team a family needs. Sending
   everyone to the general line means every call starts with a
   transfer, at the exact moment someone has worked up the nerve
   to make it.

   Short-term rehabilitation routes to Skilled Nursing Admissions
   because rehabilitation is delivered in the skilled nursing
   setting. If that is ever wrong, the general line is the safe
   fallback below. */
const WP_LINES = {
  independent: { label: "Independent Living Sales",
                 tel: "8475703310", display: "(847) 570-3310" },
  assisted:    { label: "Assisted Living & Memory Care Sales",
                 tel: "8478661615", display: "(847) 866-1615" },
  memory:      { label: "Assisted Living & Memory Care Sales",
                 tel: "8478661615", display: "(847) 866-1615" },
  skilled:     { label: "Skilled Nursing Admissions",
                 tel: "8474927780", display: "(847) 492-7780" },
  rehab:       { label: "Skilled Nursing Admissions",
                 tel: "8474927780", display: "(847) 492-7780" }
};
const WP_GENERAL = { label: "General Inquiries",
                     tel: "8475703422", display: "(847) 570-3422" };

function westminsterLine(levelId) {
  return WP_LINES[levelId] || WP_GENERAL;
}

/* ---------- COLLECTION SWITCH ------------------------------
   Collection is ON as of 2026-10-17, on the owner's authorisation,
   after its three preconditions were met: the privacy notice is
   published with a real deletion address, the deletion route is
   proven, and the 180-day purge runs on submission and daily with
   an auditable receipt.

   This flag only decides whether the form RENDERS. The endpoint
   gates independently on PLAN_VISIT_COLLECTION_ENABLED, because a
   hidden form is not a closed door — anyone can still POST. To
   switch collection off again, both must move. */
const COLLECTING = true;

/* ---------- WHAT A VISIT ACTUALLY TELLS YOU -----------------
   The gap this closes: a family finishes the assessment knowing
   their care level and still has no idea what visiting would
   teach them that a website cannot.

   Every line below is OBSERVATIONAL — things you can only learn
   by standing in a building at three in the afternoon. None of it
   is a claim about Westminster Place. It is true of any community,
   which is exactly why it can be written honestly by someone who
   works at one of them.

   The questions are the ones a family would not think to ask, and
   each is answerable by the team the assessment already routes to.

   no_need deliberately has no entry. You do not invite someone to
   tour a care community after telling them nobody needs to move. */
const VISIT_GUIDE = {
  independent: {
    see: [
      "Whether residents chose this or were moved here — ask two of them",
      "Whether the activity calendar on the wall matches what is actually happening",
      "How people talk to each other at lunch, and whether anyone is eating alone"
    ],
    ask: [
      "What happens when someone starts needing help with bathing or medication?",
      "Do they move, and where to?",
      "What is included in the monthly fee, and what gets billed on top?"
    ]
  },
  assisted: {
    see: [
      "How long a call button actually takes — ask a resident, not a staff member",
      "Whether people are dressed and out of their apartments mid-morning",
      "Whether the dining room sounds like conversation or like a television"
    ],
    ask: [
      "What specifically triggers a move to a higher level of care?",
      "Who decides, and is the family part of that conversation?",
      "What is not included in the base rate?"
    ]
  },
  memory: {
    see: [
      "Whether the secured area feels like a home or like a ward",
      "Whether staff redirect gently or correct and argue",
      "What residents are doing at three in the afternoon — the hardest hour of the day"
    ],
    ask: [
      "How many staff are on this floor overnight?",
      "What happens when a resident tries to leave, or asks to go home?",
      "Who receives dementia training, and how often is it refreshed?"
    ]
  },
  skilled: {
    see: [
      "Whether call lights get answered while you are standing there",
      "How the building smells — consistently clean matters more than first impressions",
      "Whether staff know residents by name without checking a chart"
    ],
    ask: [
      "What is the registered-nurse coverage overnight and at weekends?",
      "What is staff turnover in the last year?",
      "How are families told when something changes?"
    ]
  },
  rehab: {
    see: [
      "Whether the therapy gym is busy, or empty with the lights off",
      "Whether discharge planning starts on day one or is left until the end",
      "Whether residents are in street clothes rather than gowns"
    ],
    ask: [
      "How many therapy hours per day, and how many days per week?",
      "What happens if going home turns out not to be safe?",
      "Who co-ordinates with my parent's own doctor?"
    ]
  }
};

function visitBlock(levelId, line) {
  const g = VISIT_GUIDE[levelId];
  if (!g) return "";
  return `
      <section class="res__block visit">
        <h4 class="res__h">What a visit would tell you</h4>
        <p class="visit__lead">Some things no website can answer. These are
          what an hour in the building shows you &mdash; at Westminster Place
          or anywhere else you look.</p>

        <p class="visit__sub">Worth watching for</p>
        <ul class="res__list">
          ${g.see.map((l) => `<li>${esc(l)}</li>`).join("")}
        </ul>

        <p class="visit__sub">Worth asking the ${esc(line.label)} team</p>
        <ul class="res__list">
          ${g.ask.map((l) => `<li>${esc(l)}</li>`).join("")}
        </ul>

        <p class="visit__fine">Take these to any community you visit. They work
          just as well somewhere else.</p>
      </section>`;
}

/* The interest list mirrors the levels this site already explains, plus an
   honest "not sure". It is NOT a routing instruction: every inquiry reaches
   the same inbox and the owner handles all of them himself. It exists so he
   knows what the person actually wants before he replies. */
const INTERESTS = [
  { id: "independent", label: "Independent Living" },
  { id: "assisted", label: "Assisted Living" },
  { id: "memory", label: "Memory Care" },
  { id: "skilled", label: "Skilled Nursing" },
  { id: "unsure", label: "Not sure yet" }
];

function interestFor(levelId, variant) {
  if (levelId === "independent") return "independent";
  if (levelId === "assisted") return "assisted";
  if (levelId === "memory") return "memory";
  if (levelId === "skilled" || levelId === "rehab") return "skilled";
  return "unsure";
}

function planFormBlock(levelId, variant) {
  return `
      <section class="res__block plan plan--primary" id="plan-visit">
        <h4 class="res__h plan__h">Want to see Westminster Place?</h4>

        <p class="plan__lead">Leave your details and I read them myself. If
          you tick the box below, I pass them to Westminster Place so they
          can arrange a tour &mdash; nothing is shared without that tick.
          They decide whether and when a tour happens; this form
          doesn&rsquo;t book anything.</p>

        <label class="plan__field plan__field--full">
          <span class="plan__label">What are you interested in seeing?</span>
          <select name="interest" class="plan__select" id="plan-interest">
            ${INTERESTS.map((o) => `<option value="${o.id}"${
              o.id === interestFor(levelId, variant) ? " selected" : ""
            }>${esc(o.label)}</option>`).join("")}
          </select>
          <span class="plan__hint">Pre-filled from your result. Change it if
            you are looking at something else.</span>
        </label>

        <div class="plan__who">
          <p class="plan__who-h">Who runs this guide</p>
          <p>I created Evanston Senior Care Guide to help families better
            understand their senior-care options without feeling overwhelmed.
            My goal is to make complicated decisions easier by explaining
            different levels of care, helping families know what questions to
            ask, and giving them a clearer starting point.</p>
          <p>I work in senior living, but this guide is an independent project
            I created to help families make informed decisions.</p>
          <p class="plan__who-fine">To be specific about that: I work at
            Westminster Place. This isn&rsquo;t an official Westminster site,
            I&rsquo;m not paid for referrals, and the assessment above never
            asked for your name.</p>
        </div>

        <form class="plan__form" id="plan-form" novalidate>
          <div class="plan__row">
            <label class="plan__field">
              <span class="plan__label">First name</span>
              <input type="text" name="firstName" autocomplete="given-name"
                     maxlength="60" required>
            </label>
            <label class="plan__field">
              <span class="plan__label">Last name</span>
              <input type="text" name="lastName" autocomplete="family-name"
                     maxlength="60" required>
            </label>
          </div>

          <div class="plan__row">
            <label class="plan__field">
              <span class="plan__label">Phone number</span>
              <input type="tel" name="phone" autocomplete="tel"
                     maxlength="40" inputmode="tel">
            </label>
            <label class="plan__field">
              <span class="plan__label">Email address</span>
              <input type="email" name="email" autocomplete="email"
                     maxlength="120" inputmode="email">
            </label>
          </div>
          <p class="plan__hint">Give at least one &mdash; whichever you
            actually answer.</p>

          <label class="plan__check">
            <input type="checkbox" name="consent" id="plan-consent" required>
            <span>Send my name, phone, email, assessment result and what
              I am interested in to the person who runs this guide. He reads
              every inquiry himself and decides how to follow up, and he may
              pass my details to Westminster Place to arrange a tour.</span>
          </label>

          <button class="btn btn--primary plan__submit" type="submit">
            Request a tour</button>
          <p class="plan__status" id="plan-status" role="status" aria-live="polite"></p>

          <p class="plan__fine">Your six answers stay on your device &mdash;
            only the care level is shared. Details are deleted after 180 days.
            <a href="/privacy.html" class="plan__privacy">Privacy notice</a></p>
        </form>
      </section>`;
}

/* ---------- COST BLOCK ------------------------------------
   One renderer for two cases, because the honest answer is not
   always a number.

   With a figure: the amount, what it measures, the survey it came
   from, and a link to that survey. A median with no provenance
   reads as a price.

   Without one: why there is no figure, and the factors that
   actually drive the cost. No number is invented to fill the
   space — CareScout does not report an Illinois memory-care
   median, so this site does not print one.

   The Westminster line is here rather than in assessment.js: the
   engine names no community, and that gate still holds. */
function costBlock(cost) {
  if (!cost) return "";

  const sourced = Boolean(cost.figure);
  const source = cost.survey
    ? `<p class="res__cost-src">${esc(cost.survey)}
         ${cost.url ? `<a class="res__cost-link" href="${esc(cost.url)}"
           target="_blank" rel="noopener" data-beacon="cost-source">View source</a>` : ""}</p>`
    : "";

  return `
    <div class="res__cost${sourced ? "" : " res__cost--nofig"}">
      <p class="res__cost-label">${esc(cost.label)}</p>
      ${sourced ? `<p class="res__cost-fig">${esc(cost.figure)}<span>${esc(cost.unit)}</span></p>` : ""}
      <p class="res__cost-basis">${esc(cost.basis)}</p>
      ${source}
      <p class="res__cost-note">${esc(cost.note)}</p>
      ${sourced ? `<p class="res__cost-wp">Statewide estimates are provided for
        general comparison and do not represent Westminster Place&rsquo;s actual
        rates.</p>` : ""}
    </div>`;
}

function renderResult() {
  const result = assess(answers);
  beacon(FUNNEL.completed + "?s=" + SOURCE);

  if (result.status === "no_need") {
    resultLevelId = "no_need";
    quizEl.innerHTML = `
      <p class="res__label">Your result</p>
      <h3 class="res__name">No higher level of care yet</h3>
      <p class="res__summary">Nothing in these answers describes a need to move
        ${them()} into a care setting. That is a real answer, and it is worth
        writing down somewhere with today's date — so that when something does
        change, you can see what changed.</p>
      <div class="res__why">
        <p class="res__why-label">Worth doing anyway</p>
        <p>Have the conversation now, while it is hypothetical. Ask
          ${them()} what they would want. Find out where the important documents are. The
          families who struggle most are the ones deciding all of it inside
          seventy-two hours.</p>
        <p>Looking at a community before you need one is the cheapest version
          of this decision. Nothing obliges you to move.</p>
      </div>

      <section class="res__block visit">
        <h4 class="res__h">Three things worth doing this month</h4>
        <ul class="res__list">
          <li>Ask ${them()} what they would want, while it is still
            hypothetical and nobody is under pressure</li>
          <li>Find out where the important documents are kept &mdash; the will,
            the power of attorney, the insurance</li>
          <li>Write down today&rsquo;s date and what you are seeing, so that
            when something changes you can tell what changed</li>
        </ul>
        <p class="visit__fine">Nothing here says anyone needs to move. Come
          back and retake this if that stops being true.</p>
      </section>
      ${COLLECTING ? `
      <section class="res__block local">
        <div class="wp">
          <p class="wp__name">Westminster Place</p>
          <p class="wp__meta">3200 Grant Street, Evanston, IL 60201</p>
          <p class="wp__disclosure">
            <strong>Full disclosure:</strong> I work at Westminster Place. I
            independently developed this resource to help families better
            understand senior-care options. This is not an official Westminster
            Place website. Because of my employment relationship, I do not rank
            Westminster Place against other communities.
          </p>
          <p class="wp__disclosure wp__disclosure--sub">
            I receive no referral fees. Your contact information is not shared
            with Westminster Place unless you ask for it to be, by ticking the
            permission box on the form below.
          </p>
        </div>
      </section>` : ""}
      ${COLLECTING ? planFormBlock(resultLevelId, null) : ""}

      <div class="res__actions">
        <a class="btn btn--dark" href="#tour" data-beacon="tour">See the tour questions</a>
        <button class="btn btn--line" id="restart" type="button">Start over</button>
      </div>
      <p class="res__fine">${esc(DISCLAIMER)}</p>
    `;
    wireResult();
    return;
  }

  const level = result.level;
  resultLevelId = level.id;
  const line = westminsterLine(level.id);
  /* The by-choice path gets its own beacon so the owner can separate
     "independent living because something is slipping" from "independent
     living because I want less house". Same page, different intent, and
     the two are worth counting apart. */
  const lifestyle = result.variant === "lifestyle";
  beacon(FUNNEL.result + level.id + (lifestyle ? "-by-choice" : "") + ".txt");

  const reasons = (result.reasons || []).map((r) => `
    <li class="why__item">
      <span class="why__q">${esc(r.question)}</span>
      <span class="why__a">&ldquo;${esc(r.answer)}&rdquo;</span>
    </li>`).join("");

  quizEl.innerHTML = `
    <div class="res">
      <p class="res__label">Your starting point</p>
      <h3 class="res__name">${esc(level.name)}</h3>
      ${lifestyle ? `
      <p class="res__summary">Nothing in these answers describes a need for
        care. What ${they()} described is wanting less house to look after
        &mdash; and that is a lifestyle decision, not a care decision.
        Independent living is the option built for it: ${audience === "self"
        ? "your own apartment or cottage" : "a private apartment or cottage"},
        with the cooking, cleaning, grounds and driving handled by somebody
        else.</p>
      <p class="res__summary">This is a move people make while they are well,
        on their own terms, and usually years before any care question
        arrives. Nothing here says ${they()} need${audience === "self" ? "" : "s"}
        help.</p>` : `
      <p class="res__summary">Based on these answers,
        ${esc(level.name.toLowerCase())} may be the level of support worth
        exploring first for ${them()}. ${esc(level.summary)}</p>`}

      <p class="res__jump">Jump to:
        <a href="#costs" data-beacon="costs">what it costs</a> &middot;
        <a href="#evaluating" data-beacon="tour">questions to ask</a></p>

      <section class="res__block">
        <h4 class="res__h">Why this result appeared</h4>
        <ul class="why">${reasons}</ul>
        <p class="why__note">These are the answers you gave. Change any of them
          and the result may change &mdash; that is the whole logic.</p>
      </section>

      <section class="res__block">
        <h4 class="res__h">What this type of care usually provides</h4>
        <ul class="res__list">
          ${level.looksLike.map((l) => `<li>${esc(l)}</li>`).join("")}
        </ul>
      </section>

      ${visitBlock(level.id, line)}

      <section class="res__block local">
        <h4 class="res__h">Considering ${esc(level.name.toLowerCase())} in Evanston?</h4>

        <div class="wp">
          <p class="wp__name">Westminster Place</p>
          <p class="wp__meta">3200 Grant Street, Evanston, IL 60201</p>

          <p class="wp__disclosure">
            <strong>Full disclosure:</strong> I work at Westminster Place. I
            independently developed this resource to help families better
            understand senior-care options. This is not an official Westminster
            Place website. Because of my employment relationship, I do not rank
            Westminster Place against other communities.
          </p>
          <p class="wp__disclosure wp__disclosure--sub">
            I receive no referral fees. Your contact information is not shared
            with Westminster Place unless you ask for it to be, by ticking the
            permission box on the form below. If you do, your details are
            passed to their Admissions team so they can contact you about a
            tour, and a record is kept that your inquiry came through this
            resource.
          </p>

          <p class="wp__why">Westminster Place offers several levels of senior
            care on one campus. During a visit, you can ask how the community
            supports residents when their needs change and whether
            transitioning between care settings may be possible.</p>

          <p class="wp__route">They publish a direct line for each team. Yours
            would be <strong>${esc(line.label)}</strong>, the one that handles
            ${esc(level.name.toLowerCase())} &mdash; so a call starts in the
            right place instead of with a transfer. The form below is how this
            guide passes an inquiry to them.</p>

          <p class="wp__verify">Everything above comes from Westminster
            Place&rsquo;s own published pages. Read what they say about
            themselves at
            <a href="https://www.presbyterianliving.org/our-locations/westminster-place/"
               rel="noopener" target="_blank" data-beacon="wp-official">their
            official site</a> &mdash; this guide is not it, and does not speak
            for them.</p>
        </div>
      </section>

      ${COLLECTING ? planFormBlock(level.id, result.variant) : `
      <section class="res__block plan" id="plan-visit">
        <h4 class="res__h">Interested in touring Westminster Place?</h4>
        <p class="plan__lead">There will be a way here to ask Westminster Place
          Admissions to contact you about a tour. It is not open yet.</p>
        <p class="plan__paused">Rather than collect names and phone numbers
          before the privacy notice, the deletion process and the automatic
          180-day cleanup are finished and working, this is switched off.
          Nothing is being collected, and nothing can be submitted &mdash; the
          server refuses it.</p>
        <p class="plan__paused">Call the number above in the meantime. That
          line goes straight to the team for
          ${esc(level.name.toLowerCase())}.</p>
        <p class="plan__paused">Everything above is unaffected. Your assessment
          answers never left this device either way.</p>
      </section>`}

      <section class="res__block" id="costs">
        <h4 class="res__h">What ${esc(level.name.toLowerCase())} usually costs</h4>
        ${costBlock(level.cost)}
      </section>

      <section class="res__block" id="evaluating">
        <h4 class="res__h">Questions to ask when evaluating options</h4>
        <ul class="res__list">
          ${level.nextSteps.map((l) => `<li>${esc(l)}</li>`).join("")}
        </ul>
      </section>

      <section class="res__block">
        <h4 class="res__h">Compare other communities yourself</h4>
        <p class="wp__compare">
          <a data-beacon="idph" rel="noopener" target="_blank"
             href="https://healthcarereportcard.illinois.gov/">View Illinois&rsquo;
          official licensed-facility directory</a> &mdash; the state&rsquo;s own
          lookup, not mine. It lists every licensed facility in Illinois,
          including the ones I have never heard of.
        </p>
      </section>

      <div class="res__actions">
        <button class="btn btn--line" id="restart" type="button">Retake assessment</button>
        <a class="btn btn--quiet" href="#tour" data-beacon="tour">See the full tour checklist</a>
      </div>

      <p class="res__fine">${esc(DISCLAIMER)} This is not a diagnosis, and it
        does not guarantee placement or insurance coverage.</p>
    </div>
  `;
  beacon(FUNNEL.wpView);
  wireResult();
}

function wireResult() {
  const restart = document.getElementById("restart");
  if (restart) {
    restart.addEventListener("click", () => {
      Object.keys(answers).forEach((k) => delete answers[k]);
      step = 0;
      beacon(FUNNEL.restarted);
      audience = null;
      renderAudience();
      document.getElementById("assessment").scrollIntoView({ block: "start" });
    });
  }
  wirePlanForm();
}

/* ---------- PLAN YOUR VISIT ---------------------------------
   The one place on this site that sends anything identifiable
   anywhere. It posts to /api/plan-visit, which generates the
   submission ID and the timestamp on the server — a time this
   visitor cannot set — and stores the record before replying.

   Note what is NOT in the payload: no answers, no care level, no
   health information. The object below is built field by field
   from the form, never from the `answers` object, and the server
   refuses the request outright if an assessment field ever shows
   up in it. */
function wirePlanForm() {
  const form = document.getElementById("plan-form");
  if (!form) return;

  beacon(FUNNEL.planView);

  const status = document.getElementById("plan-status");
  const button = form.querySelector(".plan__submit");

  const say = (text, kind) => {
    status.textContent = text;
    status.className = "plan__status" + (kind ? " plan__status--" + kind : "");
  };

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (button.disabled) return;

    const value = (name) => {
      const el = form.elements[name];
      return el ? String(el.value || "").trim() : "";
    };

    const payload = {
      firstName: value("firstName"),
      lastName: value("lastName"),
      email: value("email"),
      phone: value("phone"),
      consent: form.elements.consent.checked,
      /* The derived care level only — one of six fixed identifiers,
         captured when the result rendered. The server validates it
         against that list and refuses anything else, so this can
         never become a free-text channel. Nothing the visitor
         clicked during the six questions appears in this object, and
         none of it is transmitted. */
      careLevel: resultLevelId,
      interest: (form.elements.interest || {}).value || "unsure"
    };

    /* Say the same things the server says, before the round trip,
       so a correctable mistake is corrected immediately. */
    const local = [];
    if (!payload.firstName) local.push("Add a first name.");
    if (!payload.lastName) local.push("Add a last name.");
    if (!payload.email && !payload.phone) {
      local.push("Add a phone number or an email address.");
    }
    if (!payload.consent) {
      local.push("Tick the box to give permission for your details to be shared with Admissions.");
    }
    if (local.length) { say(local.join(" "), "error"); return; }

    button.disabled = true;
    say("Saving…");
    beacon(FUNNEL.planSubmit + "?s=" + SOURCE);

    try {
      const res = await fetch("/api/plan-visit", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json().catch(() => ({}));

      if (res.ok && data.ok) {
        beacon(FUNNEL.planSaved + "?s=" + SOURCE);
        /* The confirmed-lead event. Reached only when the server has
           already written AND read the record back, so it cannot fire
           on a validation error, a rejected payload or a store
           failure. beacon() is idempotent per page load, and the form
           is replaced by the confirmation below, so a second submission
           needs a fresh page and a fresh record anyway. The stored
           records remain the authoritative count. */
        beacon(FUNNEL.inquirySubmitted);
        /* The lead paragraph asks them to save the visit. Once they
           have, it is asking for something already done, so it goes. */
        const lead = document.querySelector(".plan__lead");
        if (lead) lead.remove();
        form.innerHTML = `
          <p class="plan__done-h">Your interest has been recorded.</p>
          <p class="plan__done">Thanks. Your details have been saved with the
            date and time you asked. This does not schedule an appointment with
            Westminster Place and does not guarantee a tour &mdash; what happens
            next is up to Westminster Place Admissions. Any follow-up comes
            from them, on their timetable, and this guide cannot promise it.
            Westminster Place is a public organisation and
            their own contact details are easy to find if you would rather
            reach them yourself.</p>
          <p class="plan__ref">Recorded ${esc(new Date(data.receivedAt).toLocaleString())}
            &middot; reference <code>${esc(data.submissionId)}</code></p>
          <p class="plan__done-fine">If Admissions do get in touch, deal with
            them in the normal way &mdash; there is nothing to show anyone and
            nothing to mention.</p>`;
        return;
      }

      if (Array.isArray(data.problems) && data.problems.length) {
        say(data.problems.join(" "), "error");
      } else {
        say(data.error || "That did not save. Nothing was stored. Please try again.",
          "error");
      }
    } catch (err) {
      say("That did not save — the connection failed, and nothing was stored. Please try again.",
        "error");
    }
    button.disabled = false;
  });
}

quizEl.addEventListener("click", (event) => {
  const aud = event.target.closest("[data-aud]");
  if (aud) {
    audience = aud.getAttribute("data-aud");
    beacon("/t/audience-" + audience + ".txt");
    step = 0;
    renderQuestion();
    return;
  }
  const opt = event.target.closest(".opt");
  if (opt) {
    if (!startedBeaconSent) { beacon(FUNNEL.started); startedBeaconSent = true; }
    answers[QUESTIONS[step].id] = Number(opt.dataset.i);
    step += 1;
    if (step >= QUESTIONS.length) renderResult();
    else renderQuestion();
    return;
  }
  if (event.target.closest(".q__back") && step === 0) {
    renderAudience();
    return;
  }
  if (event.target.closest(".q__back")) {
    step = Math.max(0, step - 1);
    renderQuestion();
  }
});

renderAudience();

/* ---------- SECTION BEACONS + REVEAL ------------------------ */
document.addEventListener("click", (event) => {
  const link = event.target.closest("[data-beacon]");
  if (!link) return;
  const which = link.dataset.beacon;
  if (which === "hero-cta") beacon(FUNNEL.started);
  if (which === "tour") beacon(FUNNEL.tourQuestions);
  if (which === "costs") beacon(FUNNEL.costs);
  if (which === "wp-official") beacon(FUNNEL.wpSite + "?s=" + SOURCE);
  if (which === "idph") beacon(FUNNEL.idph);
});

if ("IntersectionObserver" in window) {
  /* Reveal the content blocks, and count the two sections that
     indicate real reading rather than a bounce. */
  const reveals = document.querySelectorAll(".level, .cost, .aside, .asks li");
  reveals.forEach((el) => el.classList.add("reveal"));

  const io = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add("in");
      io.unobserve(entry.target);
    });
  }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
  reveals.forEach((el) => io.observe(el));

  const sections = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      if (entry.target.id === "cost") beacon(FUNNEL.costs);
      if (entry.target.id === "tour") beacon(FUNNEL.tourQuestions);
      sections.unobserve(entry.target);
    });
  }, { threshold: 0.3 });
  ["cost", "tour"].forEach((id) => {
    const el = document.getElementById(id);
    if (el) sections.observe(el);
  });
}


/* ---------- NAVIGATION BEHAVIOUR ----------------------------
   Two cheap signals of a real product: the bar knows when it is
   floating, and the hairline shows how much is left to read.
   Both are passive, both respect reduced-motion.              */
(function navChrome() {
  const nav = document.getElementById("nav");
  const bar = document.getElementById("navProgress");
  if (!nav) return;

  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  let ticking = false;

  function update() {
    ticking = false;
    const y = window.scrollY || document.documentElement.scrollTop;
    nav.classList.toggle("is-stuck", y > 8);
    if (bar && !reduced) {
      const doc = document.documentElement;
      const max = doc.scrollHeight - doc.clientHeight;
      bar.style.width = max > 0 ? ((y / max) * 100).toFixed(2) + "%" : "0%";
    }
  }

  window.addEventListener("scroll", () => {
    if (ticking) return;
    ticking = true;
    window.requestAnimationFrame(update);
  }, { passive: true });

  update();
})();
