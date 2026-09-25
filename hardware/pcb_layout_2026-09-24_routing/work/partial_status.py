"""Which connections a running router4 pass has failed so far (light: no rasters).
usage: python partial_status.py DRC.json PARTIAL.csv [upto_index]"""
import csv, json, math, re, sys
from collections import Counter

HERE = __file__.rsplit('work', 1)[0]
classes = {}
for l in open(HERE + 'evidence/inputs/CLASSES.txt', encoding='utf-8', errors='replace'):
    f = l.rstrip('\n').split('|')
    if f[0] == 'MEMBER' and f[1].startswith('EMG_'):
        classes.setdefault(f[2], set()).add(f[1])


def parse_conn(s):
    m = re.match(r'Un-Routed Net Constraint: Net (\S+) Between (.*) And (.*)$', s.strip())
    if not m:
        return None
    ends = []
    for part in (m.group(2), m.group(3)):
        pts = [(float(a), float(b)) for a, b in re.findall(r'\(([-\d.]+)mm,\s*([-\d.]+)mm\)', part)]
        ends.append({'pts': pts, 'text': part.strip()})
    return m.group(1), ends[0], ends[1]


def prio(c):
    net, a, b = c
    cl = classes.get(net, set()); d = math.dist(a['pts'][0], b['pts'][0])
    if cl & {'EMG_SWITCH', 'EMG_CRYSTAL'}:
        r = 0
    elif cl & {'EMG_ANALOG', 'EMG_ADC', 'EMG_REFERENCE'} and d < 5:
        r = 1
    elif 'EMG_POWER' in cl:
        r = 2
    elif cl & {'EMG_ANALOG', 'EMG_ADC', 'EMG_REFERENCE'}:
        r = 3
    elif 'EMG_SPI' in cl:
        r = 4
    elif net == 'GND':
        r = 6
    else:
        r = 5
    return (r, d)


conns = [c for c in (parse_conn(d) for d in json.load(open(sys.argv[1]))['details'] if d.startswith('Un-Routed')) if c]
conns.sort(key=prio)
done = {r['conn'] for r in csv.DictReader(open(sys.argv[2]))}
upto = int(sys.argv[3]) if len(sys.argv) > 3 else len(conns)
failed = [c for c in conns[:upto] if '|'.join((c[0], c[1]['text'], c[2]['text'])) not in done]
print('routed', len(done), 'failed in first', upto, ':', len(failed))
print(Counter(c[0] for c in failed).most_common())
for n, a, b in failed:
    print(f'  {n:14s} {math.dist(a["pts"][0], b["pts"][0]):6.2f} mm  {a["text"][:48]}  ->  {b["text"][:48]}')
