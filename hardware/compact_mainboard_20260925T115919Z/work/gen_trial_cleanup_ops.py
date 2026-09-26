"""After the C2 trial write: (1) the catch-all Width rule gets the routing revision's proven setting (0.15/0.2/0.5 mm; class
rules for power/switch/reference keep their own), (2) the dangling stubs Altium reports as Net Antennae are deleted.
Writes work/OPS_C2_TRIAL_CLEANUP.txt for apply_ops_T.pas."""
import csv, json, os, re
here = os.path.dirname(os.path.abspath(__file__)); EV = os.path.join(os.path.dirname(here), 'evidence')
LAY = {'L1 TOP': 'Top Layer', 'L3 POWER SIGNAL': 'Mid Layer 2', 'L4 BOTTOM GND': 'Bottom Layer'}
plan = list(csv.DictReader(open(os.path.join(EV, 'ROUTE_PLAN_C2TRIAL_OK.csv'))))
ops = ['SET_WIDTH|Width|0.15|0.2|0.5']
for s in json.load(open(os.path.join(EV, 'DRC_C2_TRIAL.json')))['details']:
    if not s.startswith('Net Antennae: Track'):
        continue
    m = re.search(r'Track \(([-0-9.]+)mm,([-0-9.]+)mm\)\(([-0-9.]+)mm,([-0-9.]+)mm\) on (.+)$', s.strip())
    x1, y1, x2, y2 = map(float, m.groups()[:4]); lay = LAY[m.group(5).strip()]
    hit = [r for r in plan if r['kind'] == 'TRACK' and r['layer'] == lay and
           ((abs(float(r['x1']) - x1) < .002 and abs(float(r['y1']) - y1) < .002 and abs(float(r['x2']) - x2) < .002 and abs(float(r['y2']) - y2) < .002) or
            (abs(float(r['x1']) - x2) < .002 and abs(float(r['y1']) - y2) < .002 and abs(float(r['x2']) - x1) < .002 and abs(float(r['y2']) - y1) < .002))]
    assert len(hit) == 1, (s, len(hit))
    r = hit[0]
    ops.append('DEL_TRACK|%s|%s|%s|%s|%s|%s' % (r['net'], lay, r['x1'], r['y1'], r['x2'], r['y2']))
    print('stub', r['net'], lay, r['conn'][:90])
open(os.path.join(here, 'OPS_C2_TRIAL_CLEANUP.txt'), 'w').write('\n'.join(ops) + '\n')
print(len(ops), 'ops')
