"""C2 limited routing trial input: Altium's own unrouted list (DRC_C2_CHECKPOINT.json) minus
  * GND and the two supply nets (3V3_DIG, 3V0_ANA: planned as pours/planes, not routed in the trial)
  * connections with a BK13 socket pad end (their 0.13 mm zone escapes were proven on the 24 Sep routing copy)
Writes evidence/DRC_C2_TRIAL_INPUT.json (same format the router reads) and a per-net count."""
import json, os, re
from collections import Counter
EV = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'evidence')
d = json.load(open(os.path.join(EV, 'DRC_C2_CHECKPOINT.json')))
keep, drop = [], Counter()
for s in d['details']:
    if not s.startswith('Un-Routed'):
        continue
    m = re.match(r'Un-Routed Net Constraint: Net (\S+) Between (.*) And (.*)$', s.strip())
    net = m.group(1)
    if net in ('GND', '3V3_DIG', '3V0_ANA'):
        drop[net] += 1; continue
    if 'J_FPC' in m.group(2) or 'J_FPC' in m.group(3):
        drop['BK13 socket pad'] += 1; continue
    keep.append(s)
json.dump({'total': len(keep), 'summary': {}, 'details': keep}, open(os.path.join(EV, 'DRC_C2_TRIAL_INPUT.json'), 'w'))
nets = Counter(re.match(r'Un-Routed Net Constraint: Net (\S+)', s).group(1) for s in keep)
print('trial connections %d on %d nets; excluded %s' % (len(keep), len(nets), dict(drop)))
print(', '.join('%s %d' % kv for kv in sorted(nets.items())))
