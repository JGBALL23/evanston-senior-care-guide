#!/usr/bin/env python3
"""quotecheck: check every quotation in a built guide against the pages the guide cites.

Why it exists (24 Nov 2026): a review compared quotations by reading, and a draft passed with a sentence
that was word-perfect but applied only to people in a Medicare health plan. This tool makes the wording
check mechanical and prints, for every quotation, where it sits in the source (the heading above it and
the text before and after), so that the reviewer's attention goes to SCOPE: who and what the source
sentence applies to. It does not judge scope; the reviewer does, from the context printed here.

Usage
  python3 quotecheck.py --site DIR --slug SLUG [--slug SLUG ...] [--json] [--cache DIR] [--context N]
  python3 quotecheck.py --site DIR --all [--json]

  DIR is a clone of the site (drafts or main); the tool reads DIR/_dist/guides/SLUG/index.html.

Result for each quotation of four or more words
  FOUND            the words are in a cited page (quote marks, list bullets, dashes, capitals and spacing
                   are not compared; a comma or full stop just inside the closing quote may be the guide's own)
  NOT FOUND        the words are in none of the cited pages that could be read: a required correction,
                   unless a cited page could not be read (then check that page by hand)
  Shorter quotations are terms; they are listed, and a missing one is only a note.

Exit code: 0 when every quotation of four or more words was found, 1 when any was not, 2 on a usage error.
Standard library only (pdftotext is used for PDF pages when it is installed). Network: curl.
"""
import argparse
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
from html.parser import HTMLParser

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
OWN = ("evanstonseniorcareguide.com",)
BLOCK = {"p", "li", "td", "th", "dd", "dt", "blockquote", "h1", "h2", "h3", "h4", "h5", "figcaption", "summary", "div"}
HEAD = {"h1", "h2", "h3", "h4", "h5"}
SKIP = {"script", "style", "noscript", "svg", "template"}


def norm(s):
    s = html.unescape(s)
    s = s.replace("­", "").replace("​", "")
    for a, b in (("‘", "'"), ("’", "'"), ("“", '"'), ("”", '"'), ("–", "-"), ("—", "-"),
                 ("‐", "-"), ("‑", "-"), (" ", " "), ("…", "..."), (" ", " "), (" ", " ")):
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s).strip()


DROP = set("'\"`\u2022\u25cf\u25e6\u25aa\u25a0\u00b7\u2023\uf0b7")


def squeeze(s):
    """Text as compared: quote marks and list bullets removed (a guide turns a source's double quotes into
    single ones inside a quotation, and runs a bulleted list on as a sentence), spacing collapsed, lower case.
    Returns the compared text and, for each of its characters, the position in the text given."""
    out, idx, prev_space = [], [], True
    for i, ch in enumerate(s):
        if ch in DROP:
            continue
        if ch == " ":
            if prev_space:
                continue
            prev_space = True
        else:
            prev_space = False
        out.append(ch.lower())
        idx.append(i)
    return "".join(out), idx


class Blocks(HTMLParser):
    """Text of a page as a list of blocks, each with the heading above it and the links inside it."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks, self.buf, self.links, self.skip, self.heading, self.tag = [], [], [], 0, "", ""

    def flush(self, tag=""):
        text = re.sub(r"\s+", " ", "".join(self.buf)).strip()
        if text:
            if self.tag in HEAD:
                self.heading = text
            self.blocks.append({"text": text, "heading": self.heading, "links": self.links, "tag": self.tag})
        self.buf, self.links, self.tag = [], [], tag

    def handle_starttag(self, tag, attrs):
        if tag in SKIP:
            self.skip += 1
        elif tag in BLOCK or tag == "br":
            if tag != "br":
                self.flush(tag)
            else:
                self.buf.append(" ")
        elif tag == "a":
            href = dict(attrs).get("href") or ""
            if href.startswith("http"):
                self.links.append(href)

    def handle_endtag(self, tag):
        if tag in SKIP and self.skip:
            self.skip -= 1
        elif tag in BLOCK:
            self.flush("")

    def handle_data(self, data):
        if not self.skip:
            self.buf.append(data)


def blocks_of(markup):
    p = Blocks()
    p.feed(markup)
    p.flush()
    return p.blocks


def fetch(url, cache):
    """Return (kind, text_or_blocks, note). kind: html | pdf | unreadable."""
    os.makedirs(cache, exist_ok=True)
    path = os.path.join(cache, hashlib.sha256(url.encode()).hexdigest()[:24])
    if not (os.path.exists(path) and os.path.getsize(path) > 0):
        cmd = ["curl", "-sS", "-L", "--compressed", "--max-time", "45", "-A", UA, "-o", path, "-w", "%{http_code}", url.split("#")[0]]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=70)
            code = (r.stdout or "").strip()[-3:]
        except (OSError, subprocess.SubprocessError) as e:
            return "unreadable", "", "curl failed: %s" % e
        if code != "200":
            if os.path.exists(path):
                os.remove(path)
            return "unreadable", "", "HTTP %s" % (code or "none")
    with open(path, "rb") as f:
        raw = f.read()
    if raw[:5] == b"%PDF-":
        if shutil.which("pdftotext"):
            try:
                r = subprocess.run(["pdftotext", "-q", path, "-"], capture_output=True, timeout=120)
                text = r.stdout.decode("utf-8", "replace")
                if text.strip():
                    return "pdf", text, ""
            except (OSError, subprocess.SubprocessError):
                pass
        try:
            import pypdf  # optional
            text = "\n".join((pg.extract_text() or "") for pg in pypdf.PdfReader(path).pages)
            if text.strip():
                return "pdf", text, ""
        except Exception:
            pass
        return "unreadable", "", "PDF and neither pdftotext nor pypdf is available: read it with a web fetch tool"
    try:
        markup = raw.decode("utf-8")
    except UnicodeDecodeError:
        markup = raw.decode("latin-1", "replace")
    return "html", blocks_of(markup), ""


class Source:
    def __init__(self, url, kind, payload, note):
        self.url, self.kind, self.note = url, kind, note
        self.flat, self.marks = "", []          # marks: (offset in flat, heading)
        if kind == "html":
            parts, pos = [], 0
            for b in payload:
                t = norm(b["text"])
                if not t:
                    continue
                self.marks.append((pos, norm(b["heading"])))
                parts.append(t)
                pos += len(t) + 1
            self.flat = " ".join(parts)
        elif kind == "pdf":
            # PDF text breaks lines mid-sentence and hyphenates: join them
            t = re.sub(r"(\w)-\n(\w)", r"\1\2", payload)
            self.flat = norm(t)
        self.low, self.idx = squeeze(self.flat)

    def find(self, needle):
        """Position and length of the needle in the page text as displayed, or (-1, 0)."""
        key = squeeze(needle)[0].strip()
        if not key:
            return -1, 0
        j = self.low.find(key)
        if j < 0:
            return -1, 0
        a, b = self.idx[j], self.idx[j + len(key) - 1]
        return a, b - a + 1

    def heading_at(self, i):
        h = ""
        for pos, head in self.marks:
            if pos > i:
                break
            h = head
        return h

    def context(self, i, n, width):
        a, b = max(0, i - width), min(len(self.flat), i + n + width)
        return self.flat[a:i].strip(), self.flat[i + n:b].strip()


def quotations(block_text):
    """Quotations in a guide block: text between curly double quotes."""
    return [m.group(1) for m in re.finditer(r"“([^”]{2,900})”", block_text)]


def fragments(q):
    """A quotation with an ellipsis is checked piece by piece."""
    q = norm(q)
    parts = [p.strip() for p in re.split(r"\s*(?:\[\s*\.\.\.\s*\]|\.\.\.)\s*", q) if p.strip()]
    return parts or [q]


def locate(frag, sources):
    """Find one fragment; a comma, semicolon or full stop just inside the closing quote may be the guide's own."""
    tries = [frag]
    if frag[-1:] in ".,;:":
        tries.append(frag[:-1].rstrip())
    for n, t in enumerate(tries):
        if len(t) < 2:
            continue
        for s in sources:
            if not s.flat:
                continue
            i, width = s.find(t)
            if i >= 0:
                return s, i, width, n == 1
    return None, -1, 0, False


def check_slug(site, slug, cache, width):
    page = os.path.join(site, "_dist", "guides", slug, "index.html")
    if not os.path.exists(page):
        return {"slug": slug, "error": "no built page at " + page}
    markup = open(page, encoding="utf-8").read()
    m = re.search(r"<main\b.*?</main>", markup, re.S)
    blocks = blocks_of(m.group(0) if m else markup)
    urls = []
    for b in blocks:
        for u in b["links"]:
            if not any(o in u for o in OWN) and u not in urls:
                urls.append(u)
    sources = []
    for u in urls:
        kind, payload, note = fetch(u, cache)
        sources.append(Source(u, kind, payload, note))
    unread = [{"url": s.url, "why": s.note} for s in sources if s.kind == "unreadable"]
    rows, seen = [], set()
    for b in blocks:
        for q in quotations(b["text"]):
            key = norm(q)
            if key in seen:
                continue
            seen.add(key)
            words = len(key.split())
            frs = fragments(q)
            hits, missing, trimmed = [], [], False
            for fr in frs:
                # prefer the pages linked from the same block, then every cited page
                near = [s for s in sources if s.url in b["links"]]
                s, i, n, trim = locate(fr, near + [x for x in sources if x not in near])
                if s is None:
                    missing.append(fr)
                else:
                    before, after = s.context(i, n, width)
                    hits.append({"source": s.url, "heading": s.heading_at(i), "before": before, "after": after})
                    trimmed = trimmed or trim
            status = "FOUND" if not missing else "NOT FOUND"
            rows.append({"quotation": key, "words": words, "kind": "quotation" if words >= 4 else "term",
                         "status": status, "final_punctuation_is_the_guides": trimmed,
                         "guide_heading": norm(b["heading"]), "guide_sentence": norm(b["text"])[:700],
                         "found": hits, "missing_fragments": missing})
    long_rows = [r for r in rows if r["kind"] == "quotation"]
    bad = [r for r in long_rows if r["status"] != "FOUND"]
    return {"slug": slug, "cited_pages": [{"url": s.url, "kind": s.kind, "chars": len(s.flat), "note": s.note} for s in sources],
            "unreadable_pages": unread, "quotations": len(long_rows), "found": len(long_rows) - len(bad),
            "not_found": len(bad), "terms": len(rows) - len(long_rows),
            "terms_not_found": sum(1 for r in rows if r["kind"] == "term" and r["status"] != "FOUND"),
            "rows": rows}


def show(res, width):
    if res.get("error"):
        print("%s: %s" % (res["slug"], res["error"]))
        return
    print("=" * 100)
    print("%s: %d quotations, %d found, %d NOT FOUND; %d short terms (%d not found); %d cited pages, %d unreadable"
          % (res["slug"], res["quotations"], res["found"], res["not_found"], res["terms"], res["terms_not_found"],
             len(res["cited_pages"]), len(res["unreadable_pages"])))
    for u in res["unreadable_pages"]:
        print("  UNREADABLE PAGE (check by hand): %s (%s)" % (u["url"], u["why"]))
    for n, r in enumerate(res["rows"], 1):
        if r["kind"] == "term" and r["status"] == "FOUND":
            continue
        print("-" * 100)
        print("%d. [%s%s] “%s”" % (n, r["status"], "" if r["kind"] == "quotation" else ", short term", r["quotation"]))
        print("   GUIDE, under “%s”: %s" % (r["guide_heading"], r["guide_sentence"]))
        for h in r["found"]:
            print("   SOURCE %s" % h["source"])
            print("     under the heading: %s" % (h["heading"] or "(no heading read; PDF or top of page)"))
            print("     before: ...%s" % h["before"][-width:])
            print("     after:  %s..." % h["after"][:width])
        for fr in r["missing_fragments"]:
            print("   NOT IN ANY READABLE CITED PAGE: %s" % fr)
        if r["final_punctuation_is_the_guides"]:
            print("   note: the final punctuation inside the quotation marks is not in the source")
    print()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--site", required=True)
    ap.add_argument("--slug", action="append", default=[])
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--cache", default="/tmp/quotecheck-cache")
    ap.add_argument("--context", type=int, default=260)
    a = ap.parse_args()
    slugs = list(a.slug)
    if a.all:
        root = os.path.join(a.site, "_dist", "guides")
        slugs = sorted(d for d in os.listdir(root) if os.path.exists(os.path.join(root, d, "index.html")))
    if not slugs:
        print("give --slug SLUG or --all", file=sys.stderr)
        sys.exit(2)
    results = [check_slug(a.site, s, a.cache, a.context) for s in slugs]
    if a.json:
        print(json.dumps(results, indent=1, ensure_ascii=False))
    else:
        for r in results:
            show(r, a.context)
        print("SUMMARY: " + "; ".join("%s %s/%s found%s" % (r["slug"], r.get("found", "?"), r.get("quotations", "?"),
                                                              (", %d unreadable page(s)" % len(r["unreadable_pages"])) if r.get("unreadable_pages") else "")
                                       for r in results))
    sys.exit(1 if any(r.get("error") or r.get("not_found") for r in results) else 0)


if __name__ == "__main__":
    main()
