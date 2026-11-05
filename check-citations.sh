#!/bin/sh
# check-citations.sh — resolves every citation in the five guides against
# the live internet. check-guides.js verifies a citation's SHAPE; only the
# network verifies that it is not dead.
#
# Written 2026-10-18 after one citation was found pointing at
# www.carescout.com, which returns 404. The PDF lives on
# assets.carescout.com. A dead citation is worse than no citation: it reads
# as verified.
#
# Usage:  sh check-citations.sh        (exit 0 = every citation resolves)
#
# KNOWN LIMITATION (recorded 2026-11-04): ilga.gov sends its server
# certificate without the intermediate certificate. Browsers fetch the
# missing intermediate themselves, so the pages open normally, but curl
# cannot complete the chain and this script reports every ilga.gov URL as
# FAIL 000 ("unable to get local issuer certificate"). Checked with
# `openssl s_client` for ilga.gov, www.ilga.gov, lrb.ilga.gov and
# witnessslips.ilga.gov; beta.ilga.gov verifies.
#
# Do NOT work around this by turning certificate validation off (-k,
# --insecure, or an empty CA bundle): a citation this script cannot verify
# must stay a failure. Until the script is taught to supply ilga.gov's
# missing intermediate, open each ilga.gov citation in a browser and record
# the date in the pull request. The daily drafts routine stops on any FAIL,
# so ilga.gov citations must not reach the drafts branch before then.
# Tracked as U11 in the Project Control Center.

set -u
cd "$(dirname "$0")" || exit 1

# Git Bash on Windows aliases `curl` to Invoke-WebRequest in some shells,
# so this project has always called curl.exe explicitly. That name does
# not exist on Linux, where the cloud routine runs. Pick whichever is
# actually present instead of hardcoding either.
if command -v curl.exe >/dev/null 2>&1; then
  CURL() { curl.exe "$@"; }
elif command -v curl >/dev/null 2>&1; then
  CURL() { curl "$@"; }
else
  echo "  no curl available - cannot resolve citations"
  exit 1
fi

# The slug list is DERIVED from build-guides.py. It used to be five names
# typed in here, which meant a sixth guide's citations were silently never
# resolved - the suite printed 'all 10 citations resolve' while two new
# government URLs went unchecked. A gate that does not grow with the
# library is a gate that stops being a gate.
python -c "
import io, re, os
GEN = io.open('build-guides.py', encoding='utf-8').read()
S = re.findall(r'^\s+\"slug\": \"([a-z0-9-]+)\"', GEN, re.M)
if len(S) < 5:
    raise SystemExit('could not read the slug list out of build-guides.py')
print('SLUGS %d' % len(S), file=__import__('sys').stderr)
seen = []
for s in S:
    t = io.open(os.path.join('_dist', 'guides', s, 'index.html'), encoding='utf-8').read()
    m = re.search(r'(?is)<h2 class=\"res__h\">Sources</h2>(.*?)</ul>', t)
    if not m:
        raise SystemExit('no sources block in ' + s)
    for h in re.findall(r'href=\"(https?://[^\"]+)\"', m.group(1)):
        if h not in seen:
            seen.append(h)
io.open('.cites.txt', 'w', encoding='utf-8', newline='\n').write('\n'.join(seen) + '\n')
print(len(seen))
" > .cite-count || exit 1

total=$(cat .cite-count)
fail=0
echo "  resolving $total unique citations"

while IFS= read -r u; do
  [ -z "$u" ] && continue
  code=$(CURL -s -o /dev/null -L --max-time 35 -A "Mozilla/5.0" -w '%{http_code}' "$u")
  case "$code" in
    200|301|302) printf "  %-4s %s\n" "$code" "$u" ;;
    *) printf "  FAIL %-4s %s\n" "$code" "$u"; fail=$((fail + 1)) ;;
  esac
done < .cites.txt

rm -f .cite-count
if [ "$fail" -eq 0 ]; then
  echo ""
  echo "  all $total citations resolve"
  exit 0
fi
echo ""
echo "  $fail dead citation(s)"
exit 1
