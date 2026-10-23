# -*- coding: utf-8 -*-
"""The three approved diagrams, as HTML/CSS components.

NOT SVG. A 760-wide SVG shrinks its own text on a phone; CSS reflows.
Real text also means selectable, translatable, and read in order by a
screen reader - and zero bytes of image to download.
"""

MEDICARE = """<figure class="dia" aria-labelledby="diaMedH">
<p class="dia__eyebrow" id="diaMedH">A qualifying skilled stay, 2026</p>
<div class="mbar">
  <div class="mbar__seg mbar__seg--free" style="flex-grow:20">
    <span class="mbar__d">Days 1&ndash;20</span>
    <span class="mbar__v">$0 coinsurance</span>
  </div>
  <div class="mbar__seg mbar__seg--pay" style="flex-grow:80">
    <span class="mbar__d">Days 21&ndash;100</span>
    <span class="mbar__v">$217 each day</span>
  </div>
  <div class="mbar__seg mbar__seg--none" style="flex-grow:34">
    <span class="mbar__d">Day 101 onward</span>
    <span class="mbar__v">You pay everything</span>
  </div>
</div>
<p class="dia__sum">80 days &times; $217 = <strong>$17,360</strong> in coinsurance</p>
<ul class="dia__notes">
  <li><strong>&ldquo;$0 coinsurance&rdquo; is not &ldquo;free&rdquo;.</strong> Days
    1&ndash;20 carry no daily coinsurance on a covered stay, but the Part A
    deductible of <strong>$1,736</strong> may still apply for the benefit period.
    You do not pay it twice if the hospital stay already did.</li>
  <li>This applies only to a <strong>qualifying skilled</strong> stay. <strong>Usually</strong>
    that means a hospital stay of <strong>3 days in a row as an inpatient</strong>,
    counting from admission and not counting the discharge day, plus daily
    skilled care ordered, in a Medicare-certified facility. <strong>Hours under
    observation or in the emergency room do not count</strong>, even overnight.</li>
  <li><strong>The 3-day rule is not absolute.</strong> A doctor in an Accountable
    Care Organization holding a Skilled Nursing Facility 3-Day Rule Waiver may not
    need it, and some Medicare Advantage plans waive it too. Ask the hospital,
    and ask the plan.</li>
  <li>For <strong>long-term custodial care</strong> and assisted living, Medicare
    pays <strong>nothing at all</strong>.</li>
</ul>
<figcaption class="dia__cap">Band widths are the real day counts. Figures from
  Medicare.gov, read 18 October 2026.</figcaption>
</figure>"""

LEVELS = """<figure class="dia" aria-labelledby="diaLevH">
<p class="dia__eyebrow" id="diaLevH">Five options &mdash; not five steps</p>
<ul class="lev">
  <li class="lev__t"><span class="lev__n">Independent Living</span>
    <span class="lev__s">Own apartment, no daily care</span></li>
  <li class="lev__t"><span class="lev__n">Assisted Living</span>
    <span class="lev__s">Help with bathing, dressing, medicine</span></li>
  <li class="lev__t"><span class="lev__n">Memory Care</span>
    <span class="lev__s">Secured setting, dementia-trained staff</span></li>
  <li class="lev__t"><span class="lev__n">Short-term Rehab</span>
    <span class="lev__s">Weeks, after a hospital stay</span></li>
  <li class="lev__t"><span class="lev__n">Skilled Nursing</span>
    <span class="lev__s">Daily licensed nursing care</span></li>
</ul>
<ul class="dia__notes">
  <li>A family may use <strong>one</strong> of these and never another.</li>
  <li>Some go straight to rehab and home again. Some never leave independent
    living. <strong>Nobody is required to move through them in order.</strong></li>
</ul>
<figcaption class="dia__cap">Shown side by side at equal size on purpose. This is
  not a sequence.</figcaption>
</figure>"""

SLP = """<figure class="dia" aria-labelledby="diaSlpH">
<p class="dia__eyebrow" id="diaSlpH">Expect two charges, not one</p>
<div class="slp">
  <div class="slp__card slp__card--a">
    <p class="slp__h">1 &middot; Room and board</p>
    <p class="slp__fig">$874 <span>single occupancy</span></p>
    <p class="slp__fig slp__fig--s">$625.50 <span>double occupancy</span></p>
    <p class="slp__note">Set by the state, effective 1 January 2026. The same for
      everyone.</p>
  </div>
  <div class="slp__card slp__card--b">
    <p class="slp__h">2 &middot; Group care credit</p>
    <p class="slp__calc">your countable income</p>
    <p class="slp__calc">&minus; allowable deductions</p>
    <p class="slp__calc">&minus; the $120 personal needs allowance</p>
    <p class="slp__note">Calculated by the state, for one person. Also called
      patient liability.</p>
  </div>
</div>
<p class="slp__rest">Medicaid pays the rest of the cost of care.</p>
<ul class="dia__notes">
  <li>There is <strong>no sum on this page that produces your parent&rsquo;s
    figure</strong>, and any site that offers you one is guessing.</li>
  <li>The resident keeps the <strong>$120</strong> either way. Most residents owe
    both charges; the group care credit is avoided only when income equals the SSI
    amount.</li>
</ul>
<figcaption class="dia__cap">Figures from Illinois HFS, read 18 October 2026.</figcaption>
</figure>"""

DIAGRAMS = {
    ("does-medicare-pay-for-senior-care",
     "What a covered skilled nursing stay costs in 2026"): MEDICARE,
    ("levels-of-senior-care-explained", None): LEVELS,
    ("illinois-supportive-living-program",
     "How the money actually works"): SLP,
}
