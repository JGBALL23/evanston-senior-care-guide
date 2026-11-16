#!/usr/bin/env python3
"""Offline test: the tour checklist PDF's printed address is a working link.

Needs poppler-utils (pdfinfo, pdftotext). Checks: one US Letter page;
exactly one link, to the homepage, with no query string; the link box
covers the printed "evanstonseniorcareguide.com"; the printed text is
unchanged; the link script is idempotent; poppler parses it with no
warnings. Exit 0 on pass.
"""
import os, re, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(ROOT, "_dist", "downloads", "senior-living-tour-checklist.pdf")
URI = "https://evanstonseniorcareguide.com/"
fails = 0


def check(name, ok, info=""):
    global fails
    print(("  ok    " if ok else "  FAIL  ") + name + (("  (" + str(info) + ")") if info and not ok else ""))
    if not ok:
        fails += 1


def run(*a):
    p = subprocess.run(a, capture_output=True, text=True)
    return p.stdout, p.stderr


info, err = run("pdfinfo", PDF)
check("pdfinfo parses it without warnings", err.strip() == "", err)
check("exactly one page", re.search(r"^Pages:\s+1$", info, re.M) is not None)
check("US Letter", "612 x 792 pts" in info)
urls, _ = run("pdfinfo", "-url", PDF)
rows = [l.split() for l in urls.splitlines()[1:] if l.strip()]
check("exactly one link, to the homepage", rows == [["1", "Annotation", URI]], rows)
raw = open(PDF, "rb").read()
check("no query string or fragment on any link", re.search(rb"/URI \([^)]*[?#]", raw) is None)
check("one /Type /Page object (not an incremental update)",
      len(re.findall(rb"/Type\s*/Page(?![a-zA-Z])", raw)) == 1)
bbox, _ = run("pdftotext", "-bbox", PDF, "-")
w = re.search(r'xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">evanstonseniorcareguide\.com<', bbox)
r = re.search(rb"/Subtype /Link\s*/Rect \[([\d. ]+)\]", raw)
if w and r:
    x0, y0, x1, y1 = map(float, w.groups())
    a, b, c, d = map(float, r.group(1).split())
    check("link box covers the printed address",
          a <= x0 and c >= x1 and b <= 792 - y1 and d >= 792 - y0, (w.groups(), r.group(1)))
else:
    check("link box covers the printed address", False, "address or rect not found")
text, _ = run("pdftotext", "-layout", PDF, "-")
for s in ["Senior Living Tour Checklist", "evanstonseniorcareguide.com",
          "Independently developed by an employee of Westminster Place",
          "no referral fees", "Educational only, not legal or financial advice."]:
    check("still prints: " + s, s in text)
with tempfile.TemporaryDirectory() as t:
    cp = os.path.join(t, "c.pdf")
    shutil.copy(PDF, cp)
    subprocess.run([sys.executable, os.path.join(ROOT, "tools", "link_checklist_pdf.py"), cp], capture_output=True)
    check("link script is idempotent on the committed file", open(cp, "rb").read() == raw)
print("\n  %d failed" % fails)
sys.exit(1 if fails else 0)
