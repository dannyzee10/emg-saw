"""Split a verified route plan into write batches by net class (whole connections stay together).

usage: python split_plan.py PLAN.csv PREFIX
Writes PREFIX_A.csv (analog / ADC / reference / crystal), PREFIX_P.csv (power / switch / GND),
PREFIX_D.csv (SPI, control and everything else).  Offline only.
"""
import csv, sys
from collections import defaultdict
import geom as G

cls = defaultdict(set)
for l in open(G.CLASSES, encoding='utf-8', errors='replace'):
    f = l.rstrip('\n').split('|')
    if f[0] == 'MEMBER' and f[1].startswith('EMG_'):
        cls[f[2]].add(f[1])


def bucket(net):
    c = cls[net]
    if c & {'EMG_ANALOG', 'EMG_ADC', 'EMG_REFERENCE', 'EMG_CRYSTAL'}:
        return 'A'
    if c & {'EMG_POWER', 'EMG_SWITCH'} or net == 'GND':
        return 'P'
    return 'D'


rows = list(csv.DictReader(open(sys.argv[1])))
out = defaultdict(list)
for r in rows:
    out[bucket(r['net'])].append(r)
for k in 'APD':
    with open(f'{sys.argv[2]}_{k}.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(out[k])
    print(k, 'rows', len(out[k]), 'connections', len({r['group'] for r in out[k]}))
