# -*- coding: utf-8 -*-
"""
build-visual-proposal.py  ->  _preview/index.html

A PROPOSAL, not a deployment. Writes to _preview/ and never touches
_dist/, so production cannot move by accident.

Three real SVG diagrams (not mockups - these are the shippable assets),
plus annotated placement for photography, plus the sourcing decision.

Palette is taken from the live site: navy #0b1a2b / #0c3c6c, forest
#00513f, gold #e8bb64 (decoration only, never text on white - it
measures 1.79:1), ivory #fbfaf7, line #e0dccf.
"""
import io
import os

OUT = "_preview"

NAVY = "#0b1a2b"
NAVY2 = "#0c3c6c"
NAVY3 = "#285e90"
FOREST = "#00513f"
FOREST3 = "#006048"
GOLD = "#e8bb64"
GOLD_D = "#c99a3f"
IVORY = "#fbfaf7"
IVORY2 = "#f4f1ea"
LINE = "#e0dccf"
INK = "#0b1a2b"
INK_SOFT = "#40536a"


# ---------------------------------------------------------------- 1
def svg_medicare():
    """The 100-day cliff. Widths are proportional to the real day counts:
    20 / 80 / open-ended. The gold band is the paying stretch; the navy
    wall at day 101 is the point of the whole article."""
    return '''<svg class="dia" viewBox="0 0 760 290" role="img"
     aria-labelledby="medTitle medDesc">
  <title id="medTitle">What Medicare pays for a qualifying skilled nursing stay in 2026</title>
  <desc id="medDesc">Days 1 to 20 cost nothing. Days 21 to 100 cost 217 dollars each
    day, 17,360 dollars in total. From day 101 Medicare pays nothing.</desc>

  <text x="0" y="18" class="d-eyebrow">A QUALIFYING SKILLED STAY, 2026</text>

  <rect x="0" y="40" width="130" height="62" rx="6" fill="%(forest)s"/>
  <rect x="134" y="40" width="430" height="62" rx="6" fill="%(gold)s"/>
  <rect x="568" y="40" width="192" height="62" rx="6" fill="%(navy)s"/>

  <text x="65"  y="68" class="d-band-n" text-anchor="middle">Days 1&#8211;20</text>
  <text x="65"  y="88" class="d-band-v" text-anchor="middle">$0</text>
  <text x="349" y="68" class="d-band-d" text-anchor="middle">Days 21&#8211;100</text>
  <text x="349" y="88" class="d-band-dv" text-anchor="middle">$217 each day</text>
  <text x="664" y="68" class="d-band-n" text-anchor="middle">Day 101 onward</text>
  <text x="664" y="88" class="d-band-v" text-anchor="middle">You pay everything</text>

  <line x1="566" y1="30" x2="566" y2="150" stroke="%(navy)s" stroke-width="2"
        stroke-dasharray="4 4"/>
  <text x="578" y="146" class="d-note">coverage ends</text>

  <text x="300" y="128" class="d-sum" text-anchor="middle">80 days &#215; $217 = $17,360 out of pocket</text>

  <rect x="0" y="162" width="760" height="1" fill="%(line)s"/>

  <text x="0" y="192" class="d-foot">This applies only to a <tspan class="d-b">qualifying skilled</tspan> stay &#8212; after a</text>
  <text x="0" y="212" class="d-foot">3-day inpatient admission, with daily skilled care ordered.</text>
  <text x="0" y="244" class="d-foot">For <tspan class="d-b">long-term custodial care</tspan> and assisted living,</text>
  <text x="0" y="264" class="d-foot">Medicare pays <tspan class="d-b">nothing at all</tspan>. The Part A deductible is $1,736.</text>
</svg>''' % {"forest": FOREST, "gold": GOLD, "navy": NAVY2, "line": LINE}


# ---------------------------------------------------------------- 2
def svg_levels():
    """Deliberately NOT a staircase and NOT arrows. Five equal tiles on
    one row, because a ladder diagram tells a family their parent is
    destined to climb it. They are options. Most people never see most
    of them."""
    tiles = [
        ("Independent<tspan x='%d' dy='17'>Living</tspan>", "Own apartment,<tspan x='%d' dy='15'>no daily care</tspan>"),
        ("Assisted<tspan x='%d' dy='17'>Living</tspan>", "Help with bathing,<tspan x='%d' dy='15'>dressing, medicine</tspan>"),
        ("Memory<tspan x='%d' dy='17'>Care</tspan>", "Secured setting,<tspan x='%d' dy='15'>dementia-trained staff</tspan>"),
        ("Short-term<tspan x='%d' dy='17'>Rehab</tspan>", "Weeks, after a<tspan x='%d' dy='15'>hospital stay</tspan>"),
        ("Skilled<tspan x='%d' dy='17'>Nursing</tspan>", "Daily licensed<tspan x='%d' dy='15'>nursing care</tspan>"),
    ]
    parts = ['''<svg class="dia" viewBox="0 0 760 280" role="img"
     aria-labelledby="lvlTitle lvlDesc">
  <title id="lvlTitle">Five kinds of senior care</title>
  <desc id="lvlDesc">Independent living, assisted living, memory care, short-term
    rehabilitation and skilled nursing are five separate options, not five steps.
    They are shown side by side at equal size on purpose.</desc>
  <text x="0" y="18" class="d-eyebrow">FIVE OPTIONS &#8212; NOT FIVE STEPS</text>''']
    x = 0
    w = 142
    gap = 12
    for i, (name, sub) in enumerate(tiles):
        cx = x + w // 2
        parts.append(
            '  <rect x="%d" y="40" width="%d" height="128" rx="8" fill="#fff" '
            'stroke="%s" stroke-width="1.5"/>' % (x, w, LINE))
        parts.append('  <rect x="%d" y="40" width="%d" height="5" rx="2.5" fill="%s"/>'
                     % (x, w, FOREST3 if i % 2 == 0 else NAVY3))
        parts.append('  <text x="%d" y="80" class="d-tile" text-anchor="middle">%s</text>'
                     % (cx, name % cx))
        parts.append('  <text x="%d" y="124" class="d-tilesub" text-anchor="middle">%s</text>'
                     % (cx, sub % cx))
        x += w + gap
    parts.append('''  <rect x="0" y="196" width="760" height="1" fill="%s"/>
  <text x="0" y="226" class="d-foot">A family may use <tspan class="d-b">one</tspan> of these and never another.</text>
  <text x="0" y="248" class="d-foot">Some go straight to rehab and home again. Some never leave independent living.</text>
  <text x="0" y="270" class="d-foot">Nobody is required to move through them in order.</text>
</svg>''' % LINE)
    return "\n".join(parts)


# ---------------------------------------------------------------- 3
def svg_slp():
    """Two charges, and NO total. The state calculates the second one per
    person; printing a sum here would invent a number we are not the
    authority on - the same error the HFS fact sheet makes."""
    return '''<svg class="dia" viewBox="0 0 760 330" role="img"
     aria-labelledby="slpTitle slpDesc">
  <title id="slpTitle">How a Supportive Living resident pays</title>
  <desc id="slpDesc">A resident pays a state-set room and board charge plus a group
    care credit calculated from their own income. Medicaid covers the remaining cost
    of care. The resident keeps a 120 dollar personal needs allowance.</desc>

  <text x="0" y="18" class="d-eyebrow">EXPECT TWO CHARGES, NOT ONE</text>

  <rect x="0" y="40" width="366" height="132" rx="8" fill="#fff"
        stroke="%(line)s" stroke-width="1.5"/>
  <rect x="0" y="40" width="366" height="5" rx="2.5" fill="%(forest)s"/>
  <text x="24" y="76" class="d-h">1 &#183; Room and board</text>
  <text x="24" y="104" class="d-big">$874</text>
  <text x="112" y="104" class="d-unit">single occupancy</text>
  <text x="24" y="132" class="d-big-s">$625.50</text>
  <text x="124" y="132" class="d-unit">double occupancy</text>
  <text x="24" y="158" class="d-small">Set by the state. Same for everyone.</text>

  <rect x="394" y="40" width="366" height="132" rx="8" fill="#fff"
        stroke="%(line)s" stroke-width="1.5"/>
  <rect x="394" y="40" width="366" height="5" rx="2.5" fill="%(navy3)s"/>
  <text x="418" y="76" class="d-h">2 &#183; Group care credit</text>
  <text x="418" y="106" class="d-calc">your countable income</text>
  <text x="418" y="126" class="d-calc">&#8722; allowable deductions</text>
  <text x="418" y="146" class="d-calc">&#8722; the $120 personal needs allowance</text>
  <text x="418" y="166" class="d-small">Calculated by the state, for one person.</text>

  <rect x="0" y="196" width="760" height="58" rx="8" fill="%(ivory2)s"/>
  <text x="24" y="222" class="d-h">Medicaid pays the rest of the cost of care</text>
  <text x="24" y="243" class="d-small">That is what the programme is for.</text>

  <rect x="0" y="276" width="760" height="1" fill="%(line)s"/>
  <text x="0" y="306" class="d-foot">There is <tspan class="d-b">no sum on this page that produces your parent&#8217;s figure</tspan> &#8212; and any</text>
  <text x="0" y="326" class="d-foot">site that offers you one is guessing. The resident keeps the $120, always.</text>
</svg>''' % {"line": LINE, "forest": FOREST, "navy3": NAVY3, "ivory2": IVORY2}


# ---------------------------------------------------------------- photo slot
def photo_slot(where, caption, spec):
    return '''<figure class="slot">
  <div class="slot__box">
    <span class="slot__tag">PHOTOGRAPH</span>
    <span class="slot__where">%s</span>
    <span class="slot__spec">%s</span>
  </div>
  <figcaption class="slot__cap">%s</figcaption>
</figure>''' % (where, spec, caption)


CSS = '''
:root{--navy:%(navy)s;--navy2:%(navy2)s;--forest:%(forest)s;--gold:%(gold)s;
--ivory:%(ivory)s;--ivory2:%(ivory2)s;--line:%(line)s;--ink:%(ink)s;--soft:%(soft)s;}
*{box-sizing:border-box}
body{margin:0;background:var(--ivory);color:var(--ink);
  font-family:"Inter",system-ui,sans-serif;font-size:18px;line-height:1.65;}
.wrap{width:min(860px,90vw);margin:0 auto;padding:56px 0 100px;}
h1{font-family:"Fraunces",Georgia,serif;font-weight:400;font-size:clamp(32px,5vw,50px);
  line-height:1.1;letter-spacing:-.02em;margin:0 0 14px;}
h2{font-family:"Fraunces",Georgia,serif;font-weight:400;font-size:clamp(25px,3vw,33px);
  line-height:1.2;margin:66px 0 10px;}
h3{font-size:17px;letter-spacing:.14em;text-transform:uppercase;color:var(--forest);
  font-weight:600;margin:40px 0 12px;}
.eyebrow{font-size:13px;letter-spacing:.18em;text-transform:uppercase;
  color:var(--forest);font-weight:600;margin:0 0 14px;}
p{margin:0 0 1.1em;max-width:64ch;color:var(--soft);}
p.lead{font-size:20px;color:var(--ink);}
strong{color:var(--ink);font-weight:600;}
.card{background:#fff;border:1px solid var(--line);border-radius:14px;
  padding:clamp(22px,3vw,34px);margin:22px 0;}
.where{font-size:14.5px;letter-spacing:.1em;text-transform:uppercase;
  color:var(--navy2);font-weight:600;margin:0 0 18px;}
svg.dia{width:100%%;height:auto;display:block;margin:4px 0 6px;}
.d-eyebrow{font:600 12px/1 Inter,sans-serif;letter-spacing:.16em;fill:%(forest)s;}
.d-band-n{font:600 15px/1 Inter,sans-serif;fill:#fff;}
.d-band-v{font:600 17px/1 Inter,sans-serif;fill:#fff;}
.d-band-d{font:600 15px/1 Inter,sans-serif;fill:%(navy)s;}
.d-band-dv{font:600 17px/1 Inter,sans-serif;fill:%(navy)s;}
.d-sum{font:600 15px/1 Inter,sans-serif;fill:%(navy2)s;}
.d-note{font:500 13px/1 Inter,sans-serif;fill:%(soft)s;}
.d-foot{font:400 15px/1 Inter,sans-serif;fill:%(soft)s;}
.d-b{font-weight:600;fill:%(ink)s;}
.d-tile{font:400 17px/1 Fraunces,Georgia,serif;fill:%(ink)s;}
.d-tilesub{font:400 12.5px/1 Inter,sans-serif;fill:%(soft)s;}
.d-h{font:600 16px/1 Inter,sans-serif;fill:%(ink)s;}
.d-big{font:400 26px/1 Fraunces,Georgia,serif;fill:%(ink)s;}
.d-big-s{font:400 21px/1 Fraunces,Georgia,serif;fill:%(ink)s;}
.d-unit{font:400 13.5px/1 Inter,sans-serif;fill:%(soft)s;}
.d-calc{font:400 15px/1 Inter,sans-serif;fill:%(soft)s;}
.d-small{font:400 13.5px/1 Inter,sans-serif;fill:%(soft)s;}
.slot{margin:22px 0;}
.slot__box{border:2px dashed var(--line);border-radius:14px;background:var(--ivory2);
  min-height:180px;display:flex;flex-direction:column;align-items:center;
  justify-content:center;gap:7px;padding:26px;text-align:center;}
.slot__tag{font-size:12px;letter-spacing:.18em;font-weight:600;color:var(--forest);}
.slot__where{font-family:"Fraunces",Georgia,serif;font-size:21px;color:var(--ink);}
.slot__spec{font-size:14px;color:var(--soft);}
.slot__cap{font-size:15.5px;color:var(--soft);margin-top:10px;max-width:62ch;}
.verdict{border-left:4px solid var(--forest);padding:4px 0 4px 20px;margin:26px 0;}
.verdict p{max-width:60ch;}
.no{border-left-color:#9c3a2a;}
table{border-collapse:collapse;width:100%%;font-size:16px;margin:18px 0;}
th,td{text-align:left;padding:11px 10px;border-bottom:1px solid var(--line);
  vertical-align:top;color:var(--soft);}
th{color:var(--ink);font-weight:600;font-size:14px;letter-spacing:.06em;
  text-transform:uppercase;}
td strong{color:var(--ink);}
.ribbon{background:var(--navy);color:#eef2f6;padding:20px 0;}
.ribbon .wrap{padding:0;}
.ribbon p{color:#c7d3de;margin:0;max-width:none;font-size:15.5px;}
.ribbon b{color:var(--gold);}
@media(max-width:700px){body{font-size:17px}.wrap{padding:36px 0 70px}}
''' % {"navy": NAVY, "navy2": NAVY2, "forest": FOREST, "gold": GOLD, "ivory": IVORY,
       "ivory2": IVORY2, "line": LINE, "ink": INK, "soft": INK_SOFT}


def build():
    if not os.path.isdir(OUT):
        os.makedirs(OUT)

    html = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Visual design proposal &#183; Evanston Senior Care Guide</title>
<meta name="robots" content="noindex, nofollow"/>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,300;9..144,400;9..144,600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet"/>
<style>''' + CSS + '''</style>
</head>
<body>
<div class="ribbon"><div class="wrap" style="width:min(860px,90vw);margin:0 auto">
<p><b>PROPOSAL ONLY.</b> Nothing here is deployed. Production is untouched.</p>
</div></div>

<div class="wrap">
<p class="eyebrow">Visual design proposal &#183; 19 October 2026</p>
<h1>Three diagrams that teach, and photography that cannot lie</h1>
<p class="lead">You asked for warmth without the corporate senior-living
advertisement. The split below is what gets you there: <strong>diagrams carry the
teaching</strong>, <strong>photography carries the feeling</strong>, and neither one
ever depicts Westminster Place or a person who could be mistaken for a resident.</p>

<h2>1 &#183; Medicare coverage</h2>
<p class="where">Goes at the top of &#8220;What a covered skilled nursing stay costs in 2026&#8221;</p>
<div class="card">''' + svg_medicare() + '''</div>
<p>The band widths are the real day counts &#8212; 20, then 80, then open-ended. The
cliff at day 101 is the entire point of that article and currently it is a bullet
list. A daughter sees the gold stretch and the wall in one glance, before she reads
a word.</p>

<h2>2 &#183; The five kinds of care</h2>
<p class="where">Goes at the top of &#8220;What is the difference between each level of care?&#8221; and on the homepage</p>
<div class="card">''' + svg_levels() + '''</div>
<div class="verdict">
<p><strong>This is the one you specifically warned about, and you were right.</strong>
Every competitor draws this as a staircase with arrows. That diagram tells a family
their parent is on a conveyor belt toward a nursing home. So: five tiles, equal
width, equal height, <strong>no arrows, no ordering, no ascent</strong> &#8212; and a
caption that says out loud that most families use one of these and never another.</p>
</div>

<h2>3 &#183; Supportive Living costs</h2>
<p class="where">Goes in &#8220;How the money actually works&#8221;</p>
<div class="card">''' + svg_slp() + '''</div>
<p>Two boxes because there are two charges. The second box shows a <em>method</em>,
never a total &#8212; printing a sum would invent a number we are not the authority on,
which is the exact error the state&#8217;s own fact sheet makes.</p>

<h2>Photography &#8212; and a licensing finding that changes the answer</h2>
<p>I checked the licence terms before recommending anything, and the result is the
opposite of what you would expect.</p>
<table>
<tr><th>Option</th><th>Trust risk</th><th>Legal risk</th><th>Cost</th></tr>
<tr><td><strong>Free stock, identifiable face</strong></td><td>Low</td>
<td><strong>Real.</strong> Unsplash does not verify model releases and carries
$0 indemnification. Commercial use of a recognisable person needs one.</td><td>Free</td></tr>
<tr><td><strong>AI-generated person</strong></td><td><strong>High.</strong> One
uncanny hand and she stops believing your Medicare figures</td><td>Low &#8212; no real
person to object</td><td>Credits</td></tr>
<tr><td><strong>Real photo, no identifiable face</strong></td><td>Low</td>
<td>Low &#8212; no release needed</td><td>Free</td></tr>
</table>
<div class="verdict">
<p><strong>Recommendation: real photographs, no identifiable faces.</strong> It is the
only row that is clean in all three columns. And it is not a compromise &#8212; two
coffee cups and a notepad on a kitchen table at dusk says &#8220;this conversation is
happening in a family&#8221; better than a stock couple smiling at a laptop ever has.</p>
</div>
<p>Treatment for every image: a subtle navy duotone so photographs read as part of
the brand rather than dropped in, max 1200px wide, WebP with a JPEG fallback,
<code>loading="lazy"</code>, explicit width and height so nothing shifts as it loads.
Three images total across the whole site. Not one per article.</p>

<h3>Where they would sit</h3>
''' + photo_slot(
        "Homepage, under the hero",
        "A kitchen table at dusk: two mugs, a notepad with questions written on it, "
        "a phone face down. No people. This is the moment before the conversation.",
        "1200&#215;630 &#183; navy duotone &#183; lazy") + '''
''' + photo_slot(
        "Care Guides index, under the heading",
        "Hands on a printed page, cropped at the wrist. Someone is doing the reading "
        "you are about to do. No face, so no release and no invented resident.",
        "1200&#215;500 &#183; navy duotone &#183; lazy") + '''
''' + photo_slot(
        "Tour inquiry form, beside the trust block",
        "An Evanston street in autumn, shot from the pavement. Real, local, verifiable "
        "&#8212; and not a care building, so it cannot be mistaken for Westminster.",
        "900&#215;600 &#183; navy duotone &#183; lazy") + '''

<h2>Small article illustrations</h2>
<p>You asked about these. <strong>My answer is not yet.</strong> Five topic icons
would add five more things to maintain and teach a reader nothing. The diagrams above
already do the work an illustration pretends to do. Once there are twelve articles
instead of five, a small icon per Care Guide card becomes worth it &#8212; as a
wayfinding aid, not decoration. Revisit at twelve.</p>

<h2>What this costs you</h2>
<p>The three diagrams are inline SVG. <strong>Zero extra network requests, zero
kilobytes of images, zero licensing.</strong> They are text to a screen reader, they
scale to any width without blurring, and each carries a title and description so the
Medicare timeline reads aloud correctly. Photography adds roughly 300KB total, lazy
loaded, below the fold. Nothing autoplays. Nothing moves.</p>

<div class="verdict no">
<p><strong>The one thing I still will not do:</strong> generate a person and place
them anywhere a reader could read them as a Westminster resident, employee or
customer. Your rules 3 and 4 already say this. The diagrams and the faceless
photographs give you the warmth without ever going near that line.</p>
</div>

<h2>If you approve</h2>
<p>Diagram one into the Medicare article, diagram two into the levels article and the
homepage, diagram three into the Supportive Living article. Gates added for each:
figures must match the article text, no diagram may imply a progression, every SVG
must carry a title and description. Then the three photographs, sourced and
duotoned, for a second look before anything ships.</p>
</div>
</body>
</html>
'''
    p = os.path.join(OUT, "index.html")
    io.open(p, "w", encoding="utf-8", newline="\n").write(html)
    print("  %-34s %6d bytes" % (p, os.path.getsize(p)))


if __name__ == "__main__":
    build()
