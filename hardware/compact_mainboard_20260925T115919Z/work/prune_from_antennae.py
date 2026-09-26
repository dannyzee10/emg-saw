"""Remove dangling copper seeded ONLY by Altium's own Net Antennae list (the DRC is the judge), walking each dead branch back
until it reaches a pad or copper that is still connected at both ends.  Connectivity = copper overlap (touching counts, as in
Altium), layer-aware; vias span all copper layers.  GND is never pruned (pours are not in the export).
usage: GEOM_FILE=... python prune_from_antennae.py DRC.json OUT_OPS.txt"""
import json, os, re, sys
from collections import defaultdict
from shapely.geometry import LineString, Point, box
geo = [l.rstrip('\n').split('|') for l in open(os.environ['GEOM_FILE'], encoding='utf-8', errors='replace')]
CU = {'Top Layer', 'Mid Layer 2', 'Bottom Layer', 'Mid Layer 1', 'Mid Layer 3', 'Mid Layer 4'}
LAY = {'L1 TOP': 'Top Layer', 'L3 POWER SIGNAL': 'Mid Layer 2', 'L4 BOTTOM GND': 'Bottom Layer', 'L2 GND': 'Mid Layer 1',
       # C2 6-layer names (JLC06121H-3313)
       'L3 SIGNAL': 'Mid Layer 2', 'L4 GND': 'Mid Layer 3', 'L5 POWER SIGNAL': 'Mid Layer 4', 'L6 BOTTOM': 'Bottom Layer'}
items = []
for f in geo:
    if f[0] == 'TRACK' and f[1] in CU and 'INCOMP=False' in f:
        x1, y1, x2, y2, w = map(float, f[3:8])
        items.append(dict(kind='TRACK', net=f[2], lay={f[1]}, g=LineString([(x1, y1), (x2, y2)]).buffer(w / 2, 8),
                          ends=[Point(x1, y1), Point(x2, y2)], f=f))
    elif f[0] == 'VIA':
        items.append(dict(kind='VIA', net=f[1], lay=set(CU), g=Point(float(f[2]), float(f[3])).buffer(float(f[4]) / 2, 12), f=f))
    elif f[0] == 'PAD' and (f[4] in CU or f[4] == 'Multi Layer'):
        items.append(dict(kind='PAD', net=f[3], lay=set(CU) if f[4] == 'Multi Layer' else {f[4]}, g=box(*map(float, f[7:11])), f=f))
bynet = defaultdict(list)
for i, it in enumerate(items):
    if it['net'] not in ('', '-', 'GND'):
        bynet[it['net']].append(i)
dead = set()


def nbrs(i):
    it = items[i]
    return [j for j in bynet[it['net']] if j != i and j not in dead and items[j]['lay'] & it['lay'] and items[j]['g'].intersects(it['g'])]


def end_free(i, p):
    it = items[i]; pb = p.buffer(0.001)
    return not any(items[j]['g'].intersects(pb) for j in bynet[it['net']] if j != i and j not in dead and items[j]['lay'] & it['lay'])


def is_dead(i):
    it = items[i]
    if it['kind'] == 'PAD':
        return False
    if it['kind'] == 'VIA':
        return len(nbrs(i)) <= 1
    return any(end_free(i, p) for p in it['ends'])


seeds = []
for s in json.load(open(sys.argv[1]))['details']:
    if not s.startswith('Net Antennae'):
        continue
    m = re.search(r'Track \(([-0-9.]+)mm,([-0-9.]+)mm\)\(([-0-9.]+)mm,([-0-9.]+)mm\) on (.+)$', s.strip())
    if m:
        x1, y1, x2, y2 = map(float, m.groups()[:4]); lay = LAY[m.group(5).strip()]
        for i, it in enumerate(items):
            f = it['f']
            if it['kind'] == 'TRACK' and f[1] == lay and {(round(float(f[3]), 3), round(float(f[4]), 3)), (round(float(f[5]), 3), round(float(f[6]), 3))} == \
                    {(round(x1, 3), round(y1, 3)), (round(x2, 3), round(y2, 3))}:
                seeds.append(i)
        continue
    m = re.search(r'Via \(([-0-9.]+)mm,([-0-9.]+)mm\)', s)
    if m:
        for i, it in enumerate(items):
            if it['kind'] == 'VIA' and abs(float(it['f'][2]) - float(m.group(1))) < .002 and abs(float(it['f'][3]) - float(m.group(2))) < .002:
                seeds.append(i)
frontier = [i for i in dict.fromkeys(seeds) if items[i]['net'] not in ('GND',)]
for i in frontier:
    dead.add(i)
while frontier:
    x = frontier.pop()
    for y in [j for j in bynet[items[x]['net']] if j not in dead and items[j]['lay'] & items[x]['lay'] and items[j]['g'].intersects(items[x]['g'])]:
        if is_dead(y):
            dead.add(y); frontier.append(y)
ops = []
for i in sorted(dead):
    it, f = items[i], items[i]['f']
    ops.append(('DEL_TRACK|%s|%s|%s|%s|%s|%s' % (it['net'], f[1], f[3], f[4], f[5], f[6])) if it['kind'] == 'TRACK'
               else ('DEL_VIA|%s|%s|%s' % (it['net'], f[2], f[3])))
open(sys.argv[2], 'w').write('\n'.join(ops) + '\n')
print('seeds %d -> removing %d objects' % (len(seeds), len(ops)))
print('\n'.join(ops))
