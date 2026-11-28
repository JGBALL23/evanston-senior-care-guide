#!/usr/bin/env python3
"""Add one disclosed, optional tour-request line to the tour checklist PDF.

Why (ACQ-007; owner's request, 22 Nov 2026): the checklist is what
genuine visitors use most (3 of the first 4 opened it), it is what
referral partners are offered, and it is printed and carried on tours.
Until now it had no route to the site's optional Westminster Place tour
request, so the page families used most was a dead end for that step.

What this adds, and nothing else:

  * one printed line under the footer disclosure, as its fifth line:
        Want a tour of Westminster Place, where the author works? Ask online.
    It sits in the paragraph that already says the checklist was
    "Independently developed by an employee of Westminster Place", that
    there are "no referral fees" and that it "ranks no community".
  * a hairline under its last two words, "Ask online.", so that on a
    phone they read as something to tap.
  * one borderless /Link annotation over that line, pointing to the
    site's own tour-request form, the same address as the homepage's
    "Ask about a tour here" link. No tracking tag is added to it.

How: the line is set in the Inter Regular subset that is already
embedded in the file (page font resource /F6), at the size (9pt), grey
and line spacing of the disclosure above it. Nothing is embedded and
nothing is re-compressed: the original page content stream is kept
byte for byte. That stream leaves its page transform open, so /Contents
becomes [q, original, Q + the new line] and the new line is drawn in
plain page coordinates.

The sentence can only use characters that subset contains. It has no
capital T, O, J, K, Q, U, X or Z, no j or z, and no "/" or "#", which is
why the line does not start with "Touring" or "Optional" and prints no
web path. The script stops rather than draw a missing glyph, and it
stops if the line would run past the table's right edge.

On paper the line cannot be tapped: the site address and QR code beside
it are the route, and the homepage's tour section has the same link.

Run after tools/link_checklist_pdf.py (the three source links must be
there first, so the annotation order is stable). Idempotent: a file that
already has the tour link is left byte-for-byte unchanged.

Usage: python3 tools/tour_line_checklist_pdf.py [path]
"""
import re
import sys
import zlib

PATH = "_dist/downloads/senior-living-tour-checklist.pdf"
# The homepage's own tour-request address (index.html: href="/?tour=form#plan-visit").
TOUR_URI = "https://evanstonseniorcareguide.com/?tour=form#plan-visit"
LINE = "Want a tour of Westminster Place, where the author works? Ask online."
DESC = "Optional Westminster Place tour request"

FONT_RES = b"F6"            # /CAAAAA+Inter-Regular in the page's /Font resources
FONT_BASE = b"Inter-Regular"
SIZE = 9                    # pt; the disclosure is 12 CSS px at .75pt per px
X = 265.5                   # left edge of the disclosure block (354px)
BASELINE = 27               # 792 - 1020px * .75: one 17px line below its last line
COLOR = b".2745 .3373 .3569"  # the disclosure's grey
RIGHT_EDGE = 579            # the table's right edge; the line must end before it
UNDERLINED = "Ask online."  # the words that read as the link; must end LINE
# Links the line must come after (added by link_checklist_pdf.py).
REQUIRED = (b"https://evanstonseniorcareguide.com/",
            b"https://www.medicare.gov/care-compare/",
            b"https://dph.illinois.gov/topics-services/health-care-regulation/assisted-living.html")


def stream_data(obj):
    s = obj.index(b"stream") + 6
    s += 2 if obj[s:s + 2] == b"\r\n" else 1
    return zlib.decompress(obj[s:obj.rindex(b"endstream")])


def char_to_cid(tounicode):
    """Unicode character -> CID, from the font's ToUnicode CMap (first mapping wins)."""
    t = tounicode.decode("latin1")
    m = {}
    for blk in re.findall(r"beginbfchar(.*?)endbfchar", t, re.S):
        for cid, uni in re.findall(r"<([0-9A-Fa-f]{4})>\s*<([0-9A-Fa-f]{4})>", blk):
            m.setdefault(chr(int(uni, 16)), int(cid, 16))
    for blk in re.findall(r"beginbfrange(.*?)endbfrange", t, re.S):
        for a, b, uni in re.findall(r"<([0-9A-Fa-f]{4})>\s*<([0-9A-Fa-f]{4})>\s*<([0-9A-Fa-f]{4})>", blk):
            for cid in range(int(a, 16), int(b, 16) + 1):
                m.setdefault(chr(int(uni, 16) + cid - int(a, 16)), cid)
    return m


def cid_widths(cidfont):
    """CID -> advance width in 1/1000 em, from the CIDFont's /W array."""
    w = re.search(rb"/W \[(.*)\]\s*/DW", cidfont, re.S).group(1).decode("latin1")
    toks = re.findall(r"\[[^\]]*\]|[\d.]+", w)
    out, i = {}, 0
    while i < len(toks):
        first = int(toks[i])
        if toks[i + 1].startswith("["):
            for k, v in enumerate(toks[i + 1][1:-1].split()):
                out[first + k] = float(v)
            i += 2
        else:
            for cid in range(first, int(toks[i + 1]) + 1):
                out[cid] = float(toks[i + 2])
            i += 3
    return out


def num(v):
    """A short, stable PDF number: 264, 569.4."""
    s = ("%.1f" % v).rstrip("0").rstrip(".")
    return s.encode()


def main(path):
    d = open(path, "rb").read()
    if b"/URI (" + TOUR_URI.encode() + b")" in d:
        print("already has the tour line:", path)
        return 0
    for uri in REQUIRED:
        if b"/URI (" + uri + b")" not in d:
            sys.exit("run tools/link_checklist_pdf.py first: missing link " + uri.decode())
    objs = {}
    for m in re.finditer(rb"(?m)^(\d+) 0 obj\b", d):
        n = int(m.group(1))
        end = d.index(b"endobj", m.end()) + len(b"endobj")
        objs[n] = d[m.start():end]
    header = d[: min(d.index(o) for o in objs.values())]
    size = int(re.search(rb"/Size (\d+)", d[d.rindex(b"trailer"):]).group(1))
    page_ids = [n for n, b in objs.items() if re.search(rb"/Type\s*/Page(?![a-zA-Z])", b)]
    if len(page_ids) != 1:
        sys.exit("unexpected structure: pages=%r" % page_ids)
    pid = page_ids[0]
    page = objs[pid]

    # The embedded regular font, its character map and its widths.
    fm = re.search(rb"/" + FONT_RES + rb" (\d+) 0 R", page)
    if not fm:
        sys.exit("page has no /%s font resource" % FONT_RES.decode())
    font = objs[int(fm.group(1))]
    if FONT_BASE not in font:
        sys.exit("/%s is not %s" % (FONT_RES.decode(), FONT_BASE.decode()))
    cmap = char_to_cid(stream_data(objs[int(re.search(rb"/ToUnicode (\d+) 0 R", font).group(1))]))
    widths = cid_widths(objs[int(re.search(rb"/DescendantFonts \[(\d+) 0 R\]", font).group(1))])
    missing = sorted(set(ch for ch in LINE if ch not in cmap or cmap[ch] not in widths))
    if missing:
        sys.exit("the embedded font has no glyph for: " + " ".join(repr(c) for c in missing))
    cids = [cmap[ch] for ch in LINE]
    width = sum(widths[c] for c in cids) / 1000.0 * SIZE
    if X + width > RIGHT_EDGE:
        sys.exit("the line is %.1fpt wide and would pass the right edge" % width)

    # The original stream must be balanced, so one q before and one Q after isolate it.
    cm = re.search(rb"/Contents (\d+) 0 R", page)
    if not cm:
        sys.exit("unexpected /Contents (already wrapped?)")
    toks = stream_data(objs[int(cm.group(1))]).split()
    if toks.count(b"q") != toks.count(b"Q"):
        sys.exit("original content stream is not q/Q balanced")

    if not LINE.endswith(UNDERLINED):
        sys.exit("UNDERLINED must be the end of LINE")
    lead = sum(widths[c] for c in cids[: len(LINE) - len(UNDERLINED)]) / 1000.0 * SIZE
    open_id, line_id, link_id = size, size + 1, size + 2
    text = b"".join(b"%04X" % c for c in cids)
    draw = (b"Q\nq\n" + COLOR + b" rg\nBT\n/" + FONT_RES + b" %d Tf\n1 0 0 1 %s %s Tm\n<" % (SIZE, num(X), num(BASELINE))
            + text + b"> Tj\nET\n"
            + COLOR + b" RG\n.5 w\n%s %s m\n%s %s l\nS\nQ\n" % (
                num(X + lead), num(BASELINE - 1.4), num(X + width), num(BASELINE - 1.4)))
    for oid, data in ((open_id, b"q\n"), (line_id, draw)):
        objs[oid] = b"%d 0 obj\n<</Length %d>>\nstream\n%sendstream\nendobj" % (oid, len(data), data)
    # Link box: the line's words with 1.5pt at the sides; 24..37 clears the
    # line above (its words end at y=37.6) and covers ascenders and descenders.
    rect = b" ".join(num(v) for v in (X - 1.5, BASELINE - 3, X + width + 1.5, BASELINE + 10))
    objs[link_id] = (
        b"%d 0 obj\n<</Type /Annot\n/Subtype /Link\n/Rect [%s]\n/Border [0 0 0]\n"
        b"/Contents (%s)\n"
        b"/A <</Type /Action\n/S /URI\n/URI (%s)>>>>\nendobj" % (link_id, rect, DESC.encode(), TOUR_URI.encode())
    )
    page, k1 = re.subn(rb"/Contents (\d+) 0 R",
                       lambda m: b"/Contents [%d 0 R %s 0 R %d 0 R]" % (open_id, m.group(1), line_id), page, count=1)
    page, k2 = re.subn(rb"/Annots \[([^\]]*)\]", lambda m: b"/Annots [" + m.group(1) + b" %d 0 R]" % link_id, page, count=1)
    if k1 != 1 or k2 != 1:
        sys.exit("could not place /Contents or /Annots")
    objs[pid] = page

    size += 3
    trailer_extra = re.search(rb"trailer\s*<<(.*?)>>\s*startxref", d, re.S).group(1)
    trailer_extra = re.sub(rb"/Size \d+", b"/Size %d" % size, trailer_extra)
    out = bytearray(header)
    offs = {}
    for n in sorted(objs):
        offs[n] = len(out)
        out += objs[n] + b"\n"
    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % size
    for n in range(1, size):
        out += (b"%010d 00000 n \n" % offs[n]) if n in offs else b"0000000000 65535 f \n"
    out += b"trailer\n<<" + trailer_extra + b">>\nstartxref\n%d\n%%%%EOF\n" % xref
    open(path, "wb").write(bytes(out))
    print("tour line added:", path, len(out), "bytes; line width %.1fpt" % width)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else PATH))
