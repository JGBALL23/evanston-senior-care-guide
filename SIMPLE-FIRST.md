# Simple first, details when needed — the visitor journey

Proposal, 2026-10-30. Branch `feature/simple-first`. Nothing here is live.

## The problem, measured

A first visit today shows **2,284 words** on the homepage before anyone
taps anything. The levels section alone is 359 words and sits *above* the
assessment. A result page renders roughly **3,000 words** in one go: the
answer, the reasons, what the care provides, the Westminster disclosure,
the inquiry form (637 words by itself), costs, questions to ask, and the
state directory. Someone who hates reading never finds the one sentence
they came for.

Every one of those words earned its place for a careful reader. The fix
is not to delete them. It is to show one thing at a time and keep the rest
one tap away.

## Rules for every screen

- One question, one answer, one next step. Nothing else above the fold.
- Sentences under 15 words where possible. Everyday words first; the
  technical term in brackets after, once, then the plain word.
- Anything a careful reader needs — citations, eligibility rules, the
  full disclosure, the twelve tour questions — stays on the page inside a
  tappable "More" row (`<details>`). Nothing is removed from the site.
- Type 19px or larger. Buttons at least 56px tall, full width on phones.
  One primary button per screen. Tap rows for "More" at least 48px.
- Nothing changes in `assessment.js` (questions, scoring, rules), in the
  functions, in the privacy wording, or in the beacons. Those are the
  parts that are already right.

## The journey

```
1 Hero           "Not sure what kind of help your parent needs?"   [Start the 6 questions]
2 How it works   three lines: answer → see what fits → see costs and how people pay
3 Questions      one at a time, "Question 2 of 6", big buttons, Back
4 Your answer    one card: the level, in plain words, and why (your own answers)
5 Next step      [See what it costs]   then   [How people pay for it]   then   [Ask Westminster Place about a tour]
6 Everything else collapsed below: what the words mean, 12 tour questions, who made this, sources
```

The order on the homepage changes to match: hero, how it works,
assessment, costs, paying, then the reference material. Today the
reference material comes first.

## Sample wording

### 1. Hero (today: 68 words + 5 chips)

> **Not sure what kind of help your parent needs?**
> Answer 6 quick questions. Get a clear starting point.
> Free. Private. No email needed.
> **[ Start the 6 questions ]**
> Already know what you want? *Ask about a tour instead* (small link)

### 2. How it works (new, ~40 words)

> **1.** Answer 6 questions about daily life. About two minutes.
> **2.** See which kind of care fits, and why.
> **3.** See what it costs, and how people pay for it.
> Then, only if you want, ask one Evanston community about a tour.

### 3. The questions (shell only; the six questions stay word for word)

> Who is this for?   **[ My parent or someone else ]**   **[ Myself ]**
> *It only changes how the questions are worded.*
>
> **Question 2 of 6**
> How is your parent's memory and judgment?
> *Think about the last few months, not the worst single day.*
> [ No real concerns ] [ Forgetful, but safe ] [ Confused about time, place or people ] [ Has wandered or been unsafe alone ]
> ← Back

Option labels stay as they are; they are part of the tested engine. The
privacy paragraph above the questions becomes two lines plus a "Why this
is private" row holding today's full text.

### 4. Your answer (today: ~3,000 words at once)

> **Your starting point: Assisted Living**
> An apartment with help for daily things — bathing, dressing, medicines.
>
> **Why?** You said: "Real hands-on help with one or two of these" · "Not really — something would go wrong"
> *Change an answer and the result may change. That is the whole idea.*
>
> **[ See what it costs ]**
>
> ▸ What assisted living usually provides
> ▸ Questions to ask when you look at places
> ▸ Compare every licensed community yourself (state directory)
> ▸ This is a guide, not a diagnosis — the full note

### 5. Costs and paying (today: 538 words)

> **Assisted living in Illinois: about $6,219 a month**
> That is the typical price. Each place charges its own way.
> ▸ Where this number comes from
>
> **[ How people pay for it ]**  → opens the payment navigator with "Assisted Living" already chosen

### 6. Ask about a tour (the one place a name is asked)

> **Ask Westminster Place about a tour**
> One community in Evanston. I work there. This is not their website, and I am not paid for referrals.
> This form books nothing — their Admissions team decides whether and when a tour happens.
> ▸ The full disclosure, and what I keep
> [ First name ] [ Last name ] [ Phone or email ] …
> ☐ *consent, word for word as today*
> **[ Send to Westminster Place ]**

The form's own order — disclosures above the first field, consent last —
is pinned by the Workflow #4 harness and does not change. Westminster
Place is named in the heading, the first line and the button, so nobody
can send an inquiry without knowing who gets it.

### 7. Payment navigator

Question 1 gains one plain line under each choice:

> **Independent Living** — an apartment with meals and chores handled, no personal care
> **Assisted Living** — an apartment with help for daily things
> **Memory Care** — a secure home with staff trained for dementia
> **Skilled Nursing** — a nursing home, with nurses day and night
> **Short-Term Rehab** — a few weeks of therapy after a hospital stay
> **Not sure yet** — that is a fine answer

Each result card shows one line, with today's full text behind "More":

> **Option 1 · Worth checking first**
> **Illinois Medicaid** — the state program that can pay for a nursing home if income and savings are low.
> ▸ More, and where to read the rules

### 8. What the words mean (today's "Five kinds of senior living", moved below the fold)

> ▸ **Skilled nursing** = a nursing home. Nurses on duty day and night.
> ▸ **Memory care** = a secure home for people with dementia, with trained staff.
> ▸ **Medicaid** = Illinois's health program for people with low income and savings. It can pay for a nursing home.
> ▸ **Medicare** = the health insurance most people get at 65. It pays for short rehab stays, not years of care.
> ▸ **Supportive Living** = Illinois's Medicaid version of assisted living.
> ▸ **Aid and Attendance** = a higher VA pension rate for veterans who need daily help.

## What is measured before this merges

- Words visible by default: homepage under 450, a result under 250.
- Every existing gate passes unchanged: `test.js`, `check-guides.js`,
  `claim-audit`, consistency, publisher, `check-mobile-nav.py`, the four
  mobile harnesses, the Workflow #5 walk — all of them, against the new
  pages.
- A new `tools/simple_first_check.mjs`: visible word counts, 19px body
  text, 56px buttons, every "More" row keyboard-operable, Westminster
  Place named at the form, no beacon lost.

## Not in this round

The sixteen guides keep their current shape. The routine writes them and
its gates grade them; simplifying their template is a second project
once the homepage journey has visitor data behind it.

## What was built (2026-10-30, same branch)

Built as proposed, with the owner's adjustments: the hero asks about
"you or someone you love", the form is headed "Ask Westminster Place
about a tour" and marked optional, the limits stay in plain view on
every result ("A starting point, not a diagnosis"), and the hero carries
three shortcuts (costs, how people pay, ask about a tour) under the one
button. Nothing changed in `assessment.js`, the functions, the privacy
wording, the consent sentence or the beacons.

Measured in a real browser with every "More" row closed, phone and
desktop (`node tools/simple_first_check.mjs`):

| screen | before | now |
| --- | --- | --- |
| homepage, words before any tap | 2,284 | about 710 |
| a result, words before any tap | about 3,000 | 700–750 |
| first screen of the homepage | five cards, two paragraphs | the question and one button |
| first screen of a result | level + reasons + what it provides | level, one plain line, the limits, "See what it costs" |

The 450 / 250 targets above were written before counting the copy that
has to stay word for word: the three disclosures above the form, the
consent sentence, the Westminster disclosure and the full disclaimer
are about 330 words on every result, and the navigator's six explained
choices are about 80 on the homepage. The gate's budgets (760 / 760)
sit just above the measured figures so that a paragraph added above
the fold fails the build rather than quietly undoing this.

One thing the proposal drew differently: the inquiry form still sits
before the cost section in a result's page order, because `test.js`
locks that order ("the form comes BEFORE costs"). The visitor's first
next step is still the costs — the "See what it costs" button is the
first thing under the answer and jumps past the form — so the journey
reads answer → costs → paying → optional tour. Putting the cost block
physically above the form would need that gate changed, which is the
owner's call.

Also changed on this branch:
- `/?tour=form#plan-visit` (the hero's "Ask about a tour") opens the
  existing direct-inquiry form. It counts as a form view only; the
  guide-pathway beacon fires only when the link carries a recognised
  interest, as a guide's own link does.
- A link that lands inside a closed "More" row opens it (`#tour`,
  `#evaluating`), so nothing that is linked to is ever hidden.
