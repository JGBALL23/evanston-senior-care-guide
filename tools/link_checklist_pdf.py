#!/usr/bin/env python3
"""Make the printed site address in the tour checklist PDF tappable.

The one-page checklist prints "evanstonseniorcareguide.com" in its footer,
but the PDF had no link annotation, so a caregiver who opens it on a phone
or computer cannot tap through to the guide. This adds exactly one plain
/Link annotation over that printed address, pointing to the homepage. No
query string, no tracking: the same URL that is printed. Nothing visible
changes (the annotation has no border), and the file stays one page.

The file is rewritten with a fresh cross-reference table (not an
incremental update), so it keeps exactly one /Type /Page object.
Idempotent: a file that already has the link is left unchanged.

Usage: python3 tools/link_checklist_pdf.py [path]
"""
import re
import sys

PATH = "_dist/downloads/senior-living-tour-checklist.pdf"
URI = "https://evanstonseniorcareguide.com/"
# PDF user-space box over the printed address (pdftotext -bbox gives
# x 99.0-250.1, top-down y 710.9-723.2 on a 792pt page), padded ~2pt.
RECT = "97 67 252 83"


def main(path):
    d = open(path, "rb").read()
    if b"/URI (" + URI.encode() + b")" in d:
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
    if len(page_ids) != 1 or b"/Annots" in objs[page_ids[0]]:
        sys.exit("unexpected structure: pages=%r" % page_ids)
    pid, aid = page_ids[0], size
    objs[pid] = objs[pid].replace(b"/Tabs /S", b"/Annots [%d 0 R]\n/Tabs /S" % aid, 1)
    if b"/Annots" not in objs[pid]:
        sys.exit("could not place /Annots")
    objs[aid] = (
        b"%d 0 obj\n<</Type /Annot\n/Subtype /Link\n/Rect [%s]\n/Border [0 0 0]\n"
        b"/Contents (Evanston Senior Care Guide website)\n"
        b"/A <</Type /Action\n/S /URI\n/URI (%s)>>>>\nendobj" % (aid, RECT.encode(), URI.encode())
    )
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
