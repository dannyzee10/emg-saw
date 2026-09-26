"""Which trial connections are missing from a router plan/partial CSV?  usage: python trial_failures.py <plan.csv>"""
import csv, json, os, re, sys
from collections import Counter
EV = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'evidence')
rows = list(csv.DictReader(open(sys.argv[1])))
done = {r['conn'] for r in rows if r.get('conn')}
conns = []
for s in json.load(open(os.path.join(EV, 'DRC_C2_TRIAL_INPUT.json')))['details']:
    m = re.match(r'Un-Routed Net Constraint: Net (\S+) Between (.*) And (.*)$', s.strip())
    conns.append((m.group(1), m.group(2), m.group(3)))
print('plan rows %d, distinct conn ids %d, tracks %d, vias %d' % (len(rows), len(done), sum(r['kind'] == 'TRACK' for r in rows),
                                                                  sum(r['kind'] == 'VIA' for r in rows)))
print('sample conn ids:', list(done)[:3])
layers = Counter(r['layer'] for r in rows if r['kind'] == 'TRACK')
print('track segments by layer:', dict(layers))
failed = [c for c in conns if '%s|%s|%s' % c not in done and '%s|%s|%s' % (c[0], c[2], c[1]) not in done]
print('failed %d:' % len(failed))
for n, a, b in sorted(failed):
    short = lambda t: re.sub(r'\(([-0-9.]+)mm,([-0-9.]+)mm\).*', r' (\1,\2)', t.replace('Pad ', ''))
    print('  %-18s %s  ->  %s' % (n, short(a), short(b)))
