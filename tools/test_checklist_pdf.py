#!/usr/bin/env python3
"""Offline test: the tour checklist PDF's printed address, source names and tour line are working links.

Needs poppler-utils (pdfinfo, pdftotext). Checks: one US Letter page;
exactly four links (homepage, Medicare Care Compare, IDPH assisted
living page, the optional tour request), in that order; only the tour
request has a query string, and it is the homepage's own tour-request
address with no tracking tag; each link box covers its printed words
and no other words; the official URLs match the ones the guides cite;
the earlier printed text is unchanged; the tour line names the
employment link, sits under the disclosure and stays inside the page;
the original page content stream is untouched; both scripts are
idempotent; poppler parses it with no warnings. Exit 0 on pass.
"""
import html, os, re, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(ROOT, "_dist", "downloads", "senior-living-tour-checklist.pdf")
sys.path.insert(0, os.path.join(ROOT, "tools"))
from link_checklist_pdf import LINKS  # noqa: E402
from tour_line_checklist_pdf import LINE, TOUR_URI, UNDERLINED  # noqa: E402
URI = "https://evanstonseniorcareguide.com/"
CARE_COMPARE = "https://www.medicare.gov/care-compare/"
IDPH_AL = "https://dph.illinois.gov/topics-services/health-care-regulation/assisted-living.html"
# printed words each link must cover (and nothing else)
COVERS = {URI: ["evanstonseniorcareguide.com"],
          CARE_COMPARE: ["Medicare", "Care", "Compare."],
          IDPH_AL: ["IDPH's", "online", "list."],
          TOUR_URI: LINE.split()}
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
check("exactly four links: homepage, Care Compare, IDPH, tour request",
      rows == [["1", "Annotation", u] for u in (URI, CARE_COMPARE, IDPH_AL, TOUR_URI)], rows)
check("link script targets the same three URLs", [l[0] for l in LINKS] == [URI, CARE_COMPARE, IDPH_AL])
raw = open(PDF, "rb").read()
uris = [u.decode() for u in re.findall(rb"/URI \(([^)]*)\)", raw)]
check("no query string or fragment on any link but the tour request",
      [u for u in uris if re.search(r"[?#]", u)] == [TOUR_URI], uris)
home = open(os.path.join(ROOT, "_dist", "index.html"), encoding="utf-8").read()
check("the tour request is the homepage's own tour-request address",
      TOUR_URI.startswith(URI) and 'href="/' + TOUR_URI[len(URI):] + '"' in home, TOUR_URI)
check("the tour request carries no tracking tag",
      re.search(r"[?&](ref|utm_[a-z]+|s|src|source)=", TOUR_URI) is None and TOUR_URI == URI + "?tour=form#plan-visit")
check("every link is borderless", raw.count(b"/Subtype /Link") == raw.count(b"/Border [0 0 0]") == 4)
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
          "no referral fees", "Educational only, not legal or financial advice.", LINE]:
    check("still prints: " + s, s in text)
# The tour line (owner's request, 22 Nov 2026): disclosed, optional in tone,
# the last line of the disclosure paragraph, and inside the page.
check("tour line names the employment link", "where the author works" in LINE and "Westminster Place" in LINE)
check("tour line is a question, not an instruction", LINE.startswith("Want ") and "?" in LINE)
check("tour line ends with the underlined link words", LINE.endswith(UNDERLINED))
flat = " ".join(text.split())
check("tour line is the last line of the disclosure paragraph",
      flat.endswith("Checked November 2026. " + LINE), flat[-140:])
tour_words = [w for t, w in words if w[1] > 755.5]
check("tour line is the only text below the disclosure",
      [t for t, w in words if w[1] > 755.5] == LINE.split())
check("tour line starts at the disclosure's left edge and ends inside the table width",
      bool(tour_words) and abs(min(w[0] for w in tour_words) - 265.5) < 0.2 and max(w[2] for w in tour_words) <= 579)
check("tour line keeps at least 0.3in of bottom margin",
      bool(tour_words) and max(w[3] for w in tour_words) <= 792 - 21.6)
contents = re.search(rb"/Contents \[(\d+) 0 R (\d+) 0 R (\d+) 0 R\]", raw)
check("page content is [q, original stream, tour line]", contents is not None)


def obj(data, n):
    m = re.search(rb"(?m)^%d 0 obj\b.*?endobj" % n, data, re.S)
    return m.group(0) if m else None


if contents:
    a, orig, b = (int(x) for x in contents.groups())
    check("the opening stream is a bare q", b"stream\nq\nendstream" in (obj(raw, a) or b""))
    new = obj(raw, b) or b""
    check("the tour line stream restores the page state, draws one text run and one hairline",
          b"stream\nQ\nq\n" in new and new.count(b" Tj") == 1 and new.count(b"\nS\n") == 1 and new.rstrip().endswith(b"Q\nendstream\nendobj"))
    check("the tour line uses the embedded regular font at the disclosure's size and grey",
          b"/F6 9 Tf" in new and b".2745 .3373 .3569 rg" in new)
    check("no font was added", len(re.findall(rb"/Type /Font\b", raw)) == 8 and raw.count(b"/FontFile2") == 4)
with tempfile.TemporaryDirectory() as t:
    cp = os.path.join(t, "c.pdf")
    shutil.copy(PDF, cp)
    subprocess.run([sys.executable, os.path.join(ROOT, "tools", "link_checklist_pdf.py"), cp], capture_output=True)
    check("link script is idempotent on the committed file", open(cp, "rb").read() == raw)
    subprocess.run([sys.executable, os.path.join(ROOT, "tools", "tour_line_checklist_pdf.py"), cp], capture_output=True)
    check("tour line script is idempotent on the committed file", open(cp, "rb").read() == raw)
    # The committed file is exactly what the two scripts make, in order,
    # from the pre-link original (single address link, or none) and from
    # the three-link file that was published before the tour line
    # (fd99d55), if git has them.
    for rev in ("e90ef77", "6970ce9", "fd99d55"):
        src = subprocess.run(["git", "-C", ROOT, "show", rev + ":_dist/downloads/senior-living-tour-checklist.pdf"],
                             capture_output=True)
        if src.returncode == 0:
            op = os.path.join(t, rev + ".pdf")
            open(op, "wb").write(src.stdout)
            for script in ("link_checklist_pdf.py", "tour_line_checklist_pdf.py"):
                subprocess.run([sys.executable, os.path.join(ROOT, "tools", script), op], capture_output=True)
            check("scripts' output from %s equals the committed file" % rev, open(op, "rb").read() == raw)
            if rev == "fd99d55" and contents:
                check("the original page content stream is byte-for-byte the published one",
                      obj(src.stdout, int(contents.group(2))) == obj(raw, int(contents.group(2))))
print("\n  %d failed" % fails)
sys.exit(1 if fails else 0)
