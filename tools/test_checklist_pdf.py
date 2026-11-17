#!/usr/bin/env python3
"""Offline test: the tour checklist PDF's printed address and source names are working links.

Needs poppler-utils (pdfinfo, pdftotext). Checks: one US Letter page;
exactly three links (homepage, Medicare Care Compare, IDPH assisted
living page), in that order, none with a query string; each link box
covers its printed words and no other words; the official URLs match
the ones the guides cite; the printed text is unchanged; the link
script is idempotent; poppler parses it with no warnings. Exit 0 on pass.
"""
import html, os, re, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(ROOT, "_dist", "downloads", "senior-living-tour-checklist.pdf")
sys.path.insert(0, os.path.join(ROOT, "tools"))
from link_checklist_pdf import LINKS  # noqa: E402
URI = "https://evanstonseniorcareguide.com/"
CARE_COMPARE = "https://www.medicare.gov/care-compare/"
IDPH_AL = "https://dph.illinois.gov/topics-services/health-care-regulation/assisted-living.html"
# printed words each link must cover (and nothing else)
COVERS = {URI: ["evanstonseniorcareguide.com"],
          CARE_COMPARE: ["Medicare", "Care", "Compare."],
          IDPH_AL: ["IDPH's", "online", "list."]}
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
check("exactly three links: homepage, Care Compare, IDPH",
      rows == [["1", "Annotation", u] for u in (URI, CARE_COMPARE, IDPH_AL)], rows)
check("link script targets the same three URLs", [l[0] for l in LINKS] == [URI, CARE_COMPARE, IDPH_AL])
raw = open(PDF, "rb").read()
check("no query string or fragment on any link", re.search(rb"/URI \([^)]*[?#]", raw) is None)
check("every link is borderless", raw.count(b"/Subtype /Link") == raw.count(b"/Border [0 0 0]") == 3)
check("one /Type /Page object (not an incremental update)",
      len(re.findall(rb"/Type\s*/Page(?![a-zA-Z])", raw)) == 1)
# Official destinations must be ones the built guides already cite.
cited = set()
for dp, _, fs in os.walk(os.path.join(ROOT, "_dist", "guides")):
    for f in fs:
        if f.endswith(".html"):
            cited |= set(re.findall(r'href="(https://[^"]+)"', open(os.path.join(dp, f), encoding="utf-8").read()))
for u in (CARE_COMPARE, IDPH_AL):
    check("guides already cite " + u, u in cited)
bbox, _ = run("pdftotext", "-bbox", PDF, "-")
words = [(html.unescape(t), tuple(map(float, b)))
         for *b, t in re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)<', bbox)]
annots = re.findall(rb"/Subtype /Link\s*/Rect \[([\d. ]+)\][^>]*?/URI \(([^)]*)\)", raw, re.S)
for uri, want in COVERS.items():
    m = [r for r, u in annots if u.decode() == uri]
    if len(m) != 1:
        check("one link box for " + uri, False, m)
        continue
    a, b, c, d = map(float, m[0].split())
    inside = lambda w: a <= w[0] and c >= w[2] and b <= 792 - w[3] and d >= 792 - w[1]
    touches = lambda w: not (w[2] <= a or w[0] >= c or 792 - w[1] <= b or 792 - w[3] >= d)
    hit = [t for t, w in words if touches(w)]
    check("link box for %s covers %s" % (uri, " ".join(want)),
          all(any(t == x and inside(w) for t, w in words) for x in want), hit)
    check("link box for %s touches no other words" % uri, sorted(hit) == sorted(want), hit)
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
    # The committed file is exactly what the script makes from the
    # pre-link original (single address link, or none), if git has it.
    for rev in ("e90ef77", "6970ce9"):
        src = subprocess.run(["git", "-C", ROOT, "show", rev + ":_dist/downloads/senior-living-tour-checklist.pdf"],
                             capture_output=True)
        if src.returncode == 0:
            op = os.path.join(t, rev + ".pdf")
            open(op, "wb").write(src.stdout)
            subprocess.run([sys.executable, os.path.join(ROOT, "tools", "link_checklist_pdf.py"), op], capture_output=True)
            check("script output from %s equals the committed file" % rev, open(op, "rb").read() == raw)
print("\n  %d failed" % fails)
sys.exit(1 if fails else 0)
