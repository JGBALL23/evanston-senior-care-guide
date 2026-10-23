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

set -u
cd "$(dirname "$0")" || exit 1

python -c "
import io, re, os
S = ['assisted-living-cost-illinois', 'does-medicare-pay-for-senior-care',
     'illinois-supportive-living-program', 'check-illinois-inspection-records',
     'levels-of-senior-care-explained']
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
  code=$(curl.exe -s -o /dev/null -L --max-time 35 -A "Mozilla/5.0" -w '%{http_code}' "$u")
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
