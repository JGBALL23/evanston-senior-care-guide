#!/usr/bin/env python3
"""Make the printed site address and source names in the tour checklist PDF tappable.

The one-page checklist prints "evanstonseniorcareguide.com" in its footer,
but the PDF had no link annotation, so a caregiver who opens it on a phone
or computer cannot tap through to the guide. This adds exactly one plain
/Link annotation over that printed address, pointing to the homepage. No
query string, no tracking: the same URL that is printed. Nothing visible
changes (the annotation has no border), and the file stays one page.

The file is rewritten with a fresh cross-reference table (not an
incremental update), so it keeps exactly one /Type /Page object.
Source links (GP-20261116-164537Z): the "Licence and inspection record"
question names Medicare Care Compare and IDPH's online list but did not
link them. Two more borderless /Link annotations go over those printed
names, pointing to the same official pages the guides already cite
(the inspection-records guide says the IDPH list is "linked from its
assisted living page"). Printed text is unchanged.

Idempotent: links already present are left alone; a file that already
has all three is left byte-for-byte unchanged.

Usage: python3 tools/link_checklist_pdf.py [path]
"""
import re
import sys

PATH = "_dist/downloads/senior-living-tour-checklist.pdf"
# (uri, rect in PDF user space, description). Rects come from
# pdftotext -bbox on the 792pt-high page, padded ~1-2pt, not overlapping
# neighbouring words.
LINKS = [
    # "evanstonseniorcareguide.com": x 99.0-250.1, top-down y 710.9-723.2
    ("https://evanstonseniorcareguide.com/", "97 67 252 83",
     "Evanston Senior Care Guide website"),
    # "Medicare Care Compare": x 282.5-389.1, top-down y 146.5-157.4
    ("https://www.medicare.gov/care-compare/", "281 633 390 647",
     "Medicare Care Compare"),
    # "IDPH's online list": x 457.9-532.1, top-down y 146.5-157.4
    ("https://dph.illinois.gov/topics-services/health-care-regulation/assisted-living.html",
     "457 633 534 647",
     "Illinois Department of Public Health assisted living page"),
]
URI = LINKS[0][0]


def main(path):
    d = open(path, "rb").read()
    todo = [l for l in LINKS if b"/URI (" + l[0].encode() + b")" not in d]
    if not todo:
        print("already linked:", path)
        return 0
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
    new_ids = list(range(size, size + len(todo)))
    refs = b" ".join(b"%d 0 R" % n for n in new_ids)
    if b"/Annots" in objs[pid]:
        objs[pid], k = re.subn(rb"/Annots \[([^\]]*)\]", lambda m: b"/Annots [" + m.group(1) + b" " + refs + b"]", objs[pid], 1)
    else:
        objs[pid], k = objs[pid].replace(b"/Tabs /S", b"/Annots [" + refs + b"]\n/Tabs /S", 1), 1
    if k != 1 or b"/Annots" not in objs[pid]:
        sys.exit("could not place /Annots")
    for aid, (uri, rect, desc) in zip(new_ids, todo):
        objs[aid] = (
            b"%d 0 obj\n<</Type /Annot\n/Subtype /Link\n/Rect [%s]\n/Border [0 0 0]\n"
            b"/Contents (%s)\n"
            b"/A <</Type /Action\n/S /URI\n/URI (%s)>>>>\nendobj" % (aid, rect.encode(), desc.encode(), uri.encode())
        )
    size += len(todo) - 1
    trailer_extra = re.search(rb"trailer\s*<<(.*?)>>\s*startxref", d, re.S).group(1)
    trailer_extra = re.sub(rb"/Size \d+", b"/Size %d" % (size + 1), trailer_extra)
    out = bytearray(header)
    offs = {}
    for n in sorted(objs):
        offs[n] = len(out)
        out += objs[n] + b"\n"
    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (size + 1)
    for n in range(1, size + 1):
        out += (b"%010d 00000 n \n" % offs[n]) if n in offs else b"0000000000 65535 f \n"
    out += b"trailer\n<<" + trailer_extra + b">>\nstartxref\n%d\n%%%%EOF\n" % xref
    open(path, "wb").write(bytes(out))
    print("linked:", path, len(out), "bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else PATH))
