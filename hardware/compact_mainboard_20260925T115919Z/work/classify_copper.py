"""Classify candidate B's free copper (net tracks/arcs/vias, not component primitives) against the plan:
each connected cluster (same net, touching, shared layer; vias join layers) is attached to the pads it touches.
  * all touched pads in ONE group that is purely translated (Top->Top)  -> MOVE by that group's vector
  * touches pads of groups with different vectors / flipped groups / overrides -> REMOVE (stale after the move)
  * touches no pad (e.g. stitching via in a plane)                          -> keep unless inside moved area
Writes evidence/COPPER_PLAN.csv (kind,net,layer,coords..., action, dx, dy, reason).  Offline; applied natively."""
import csv, os
from collections import defaultdict
from shapely.geometry import LineString, Point, box
from shapely.strtree import STRtree

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EV = os.path.join(HERE, 'evidence')
COPPER = ('Top Layer', 'Mid Layer 1', 'Mid Layer 2', 'Bottom Layer')
plan = {r['designator']: r for r in csv.DictReader(open(os.path.join(EV, 'PLAN_B_COMPONENTS.csv')))}
base = {r['designator']: r for r in csv.DictReader(open(os.path.join(EV, 'BASELINE_COMPONENTS.csv')))}
over = {r['designator'] for r in csv.DictReader(open(os.path.join(HERE, 'work', 'plan_B_overrides.csv')))}

def vec(ref):
    p, b = plan[ref], base[ref]
    if p['side'] != b['side'] or ref in over:
        return None
    return (round(float(p['x']) - float(b['x']), 4), round(float(p['y']) - float(b['y']), 4))

pads, items = [], []
for l in open(os.path.join(EV, 'GEOMETRY_A_BASELINE.txt'), encoding='utf-8', errors='replace'):
    f = l.rstrip('\n').split('|')
    if f[0] == 'PAD':
        hr = max(float(f[13].split('=')[1]), float(f[14].split('=')[1])) / 2
        lay = set(COPPER) if f[4] == 'Multi Layer' else {f[4]}
        pads.append((Point(float(f[5]), float(f[6])).buffer(hr), f[3], lay, f[1]))
    elif f[0] == 'TRACK' and f[1] in COPPER and f[-1] != 'KEEPOUT=True' and f[2] not in ('', '-'):
        if 'INCOMP=True' in f:
            continue
        g = LineString([(float(f[3]), float(f[4])), (float(f[5]), float(f[6]))]).buffer(float(f[7]) / 2)
        items.append({'kind': 'TRACK', 'net': f[2], 'layer': f[1], 'g': g, 'raw': f})
    elif f[0] == 'VIA':
        items.append({'kind': 'VIA', 'net': f[1], 'layer': 'Multi Layer', 'g': Point(float(f[2]), float(f[3])).buffer(float(f[4]) / 2), 'raw': f})
    elif f[0] == 'ARC' and f[1] in COPPER and 'INCOMP=True' not in f and f[2] not in ('', '-'):
        items.append({'kind': 'ARC', 'net': f[2], 'layer': f[1], 'g': box(*map(float, f[3:7])), 'raw': f})
print('free copper items', len(items), {k: sum(i['kind'] == k for i in items) for k in ('TRACK', 'VIA', 'ARC')})
lay_of = lambda it: set(COPPER) if it['kind'] == 'VIA' else {it['layer']}
# union-find clusters of free copper
parent = list(range(len(items)))
def find(a):
    while parent[a] != a:
        parent[a] = parent[parent[a]]; a = parent[a]
    return a
tree = STRtree([it['g'] for it in items])
for i, it in enumerate(items):
    for j in tree.query(it['g'].buffer(0.002)):
        j = int(j)
        if j > i and items[j]['net'] == it['net'] and lay_of(it) & lay_of(items[j]) and it['g'].distance(items[j]['g']) < 0.002:
            parent[find(i)] = find(j)
clusters = defaultdict(list)
for i in range(len(items)):
    clusters[find(i)].append(i)
ptree = STRtree([p[0] for p in pads])
rows = []
stats = defaultdict(int)
for cid, idx in clusters.items():
    refs = set()
    for i in idx:
        it = items[i]
        for j in ptree.query(it['g'].buffer(0.002)):
            p = pads[int(j)]
            if p[1] == it['net'] and p[2] & lay_of(it) and p[0].distance(it['g']) < 0.002:
                refs.add(p[3])
    vecs = {vec(r) for r in refs}
    groups = sorted({plan[r].get('group', '') for r in refs})
    if not refs:
        action, v, why = 'KEEP', (0, 0), 'touches no pad'
    elif len(vecs) == 1 and None not in vecs:
        v = vecs.pop(); action = 'MOVE' if v != (0, 0) else 'KEEP'; why = 'all pads in ' + '/'.join(groups)
    else:
        action, v, why = 'REMOVE', (0, 0), 'pads with different moves: ' + ','.join(sorted(refs))[:120]
    for i in idx:
        it = items[i]; f = it['raw']
        stats[(it['kind'], action)] += 1
        if it['kind'] == 'TRACK':
            coords = f[3:8]
        elif it['kind'] == 'VIA':
            coords = [f[2], f[3], '', '', f[4]]
        else:
            coords = f[3:7] + ['']
        rows.append([it['kind'], it['net'], it['layer']] + coords + [action, v[0], v[1], why, cid])
with open(os.path.join(EV, 'COPPER_PLAN.csv'), 'w', newline='') as fh:
    w = csv.writer(fh)
    w.writerow(['kind', 'net', 'layer', 'x1', 'y1', 'x2', 'y2', 'w_or_d', 'action', 'dx', 'dy', 'reason', 'cluster'])
    w.writerows(rows)
for k in sorted(stats):
    print(k, stats[k])
rem = defaultdict(int)
for r in rows:
    if r[8] == 'REMOVE':
        rem[r[1]] += 1
print('REMOVE by net:', dict(sorted(rem.items(), key=lambda t: -t[1])))
