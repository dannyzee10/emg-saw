"""Parse an Altium batch-DRC HTML report: rule-summary counts + every violation text.
usage: python parse_drc.py report.html [out.json]"""
import html, json, re, sys
from collections import Counter

t = open(sys.argv[1], encoding='utf-8', errors='replace').read()
summary = []
for name, cnt in re.findall(r'<td class="column1"><a href="#ID\w+">(.*?)</a></td>\s*<td class="column2">(\d+)</td>', t):
    summary.append((html.unescape(name), int(cnt)))
details = [html.unescape(x).strip() for x in re.findall(r'<acronym title="dxpprocess[^"]*">(.*?)</acronym>', t, re.S)]
total = re.search(r'Rule Violations:</td>\s*<td class="DRC_summary_header_col2"></td>\s*<td class="DRC_summary_header_col3"[^>]*>(\d+)', t)
kinds = Counter(d.split(':')[0] for d in details)
print('TOTAL', total.group(1) if total else '?', '| rules', len(summary), '| detail rows', len(details))
for k, v in kinds.most_common():
    print(f'  {v:5d}  {k}')
nonzero = [(n, c) for n, c in summary if c]
print('non-zero rules:')
for n, c in nonzero:
    print(f'  {c:5d}  {n[:150]}')
if len(sys.argv) > 2:
    json.dump({'total': total.group(1) if total else None, 'summary': summary, 'details': details}, open(sys.argv[2], 'w'), indent=1)
