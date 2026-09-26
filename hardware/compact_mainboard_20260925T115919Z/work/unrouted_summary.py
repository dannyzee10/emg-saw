"""Unrouted / antenna summary of a parsed DRC (6L routing): counts per net class and lists every antenna.
usage: python unrouted_summary.py DRC.json"""
import json, os, re, sys
from collections import Counter
EV = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'evidence')
d = json.load(open(os.path.join(EV, sys.argv[1])))['details']
nets = Counter()
for s in d:
    m = re.match(r'Un-Routed Net Constraint: Net (\S+) Between', s.strip())
    if m:
        nets[m.group(1)] += 1
print('unrouted', sum(nets.values()))
grp = Counter()
for n, c in nets.items():
    k = n if n in ('GND', '3V3_DIG', '3V0_ANA', 'VSYS') else 'signals'
    grp[k] += c
print(' ', dict(grp))
print('  signal nets:', ', '.join(f'{n}:{c}' for n, c in sorted(nets.items()) if n not in ('GND', '3V3_DIG', '3V0_ANA', 'VSYS')))
for s in d:
    if s.startswith('Net Antennae'):
        print('  ANT', s.strip()[:170])
