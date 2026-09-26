"""Layer-aware copper connectivity per net on a native geometry export: every connected group of free tracks/vias that joins
fewer than two pads is dangling -> DEL_TRACK / DEL_VIA ops.  usage: GEOM_FILE=... python find_dangling.py OUT_OPS.txt"""
import os, sys
from collections import defaultdict
from shapely.geometry import LineString, Point
from shapely.strtree import STRtree
EV = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'evidence')
geo = [l.rstrip('\n').split('|') for l in open(os.environ['GEOM_FILE'], encoding='utf-8', errors='replace')]
CU = {'Top Layer', 'Mid Layer 2', 'Bottom Layer', 'Mid Layer 1'}
items = []    # (kind, net, layers:set, geom, src)
for f in geo:
    if f[0] == 'TRACK' and f[1] in CU and 'INCOMP=False' in f:
        x1, y1, x2, y2, w = map(float, f[3:8])
        items.append(('TRACK', f[2], {f[1]}, LineString([(x1, y1), (x2, y2)]).buffer(w / 2, 8), f))
    elif f[0] == 'VIA':
        items.append(('VIA', f[1], set(CU), Point(float(f[2]), float(f[3])).buffer(float(f[4]) / 2, 12), f))
    elif f[0] == 'PAD' and f[4] in CU | {'Multi Layer'}:
        net = f[3]
        lay = set(CU) if f[4] == 'Multi Layer' else {f[4]}
        x0, y0, x1, y1 = map(float, f[7:11])
        from shapely.geometry import box
        items.append(('PAD', net, lay, box(x0, y0, x1, y1), f))
bynet = defaultdict(list)
for i, it in enumerate(items):
    if it[1] not in ('', '-', 'GND'):      # GND connects through the L2/L4 pours (not in the export): never "dangling"
        bynet[it[1]].append(i)
parent = list(range(len(items)))


def find(a):
    while parent[a] != a:
        parent[a] = parent[parent[a]]; a = parent[a]
    return a


for net, idx in bynet.items():
    geoms = [items[i][3] for i in idx]
    tree = STRtree(geoms)
    for k, i in enumerate(idx):
        for j in tree.query(geoms[k]):
            jj = idx[int(j)]
            if jj <= i or not (items[i][2] & items[jj][2]):
                continue
            if geoms[k].intersects(items[jj][3]):
                parent[find(i)] = find(jj)
groups = defaultdict(list)
for net, idx in bynet.items():
    for i in idx:
        groups[find(i)].append(i)
ops, n_t, n_v = [], 0, 0
for g, mem in groups.items():
    pads = [i for i in mem if items[i][0] == 'PAD']
    free = [i for i in mem if items[i][0] != 'PAD']
    if free and len(pads) < 2:
        for i in free:
            kind, net, lay, _, f = items[i]
            if kind == 'TRACK':
                ops.append('DEL_TRACK|%s|%s|%s|%s|%s|%s' % (net, f[1], f[3], f[4], f[5], f[6])); n_t += 1
            else:
                ops.append('DEL_VIA|%s|%s|%s' % (net, f[2], f[3])); n_v += 1
# spurs: repeatedly remove free tracks with an end that touches no other same-net copper on its layer
dead = {i for g, mem in groups.items() if [x for x in mem if items[x][0] != 'PAD'] and len([x for x in mem if items[x][0] == 'PAD']) < 2
        for i in mem if items[i][0] != 'PAD'}
n_spur = 0
while True:
    removed = False
    for net, idx in bynet.items():
        live = [i for i in idx if i not in dead]
        for i in live:
            kind, _, lay, g, f = items[i]
            if kind == 'VIA':
                # a via reaching at most one other piece of its net is a dead end (layer change to nowhere)
                if sum(1 for j in live if j != i and items[j][3].intersects(g)) <= 1:
                    dead.add(i); removed = True; n_spur += 1
                    ops.append('DEL_VIA|%s|%s|%s' % (net, f[2], f[3]))
                continue
            if kind != 'TRACK':
                continue
            for ex, ey in ((float(f[3]), float(f[4])), (float(f[5]), float(f[6]))):
                p = Point(ex, ey)

                def touches(j):
                    kj, _, lj, gj, fj = items[j]
                    if j == i or not (lj & lay):
                        return False
                    if kj == 'TRACK':   # routed chains join end-to-end or at a T on the centreline
                        return LineString([(float(fj[3]), float(fj[4])), (float(fj[5]), float(fj[6]))]).distance(p) <= 0.005
                    return gj.intersects(p)
                if not any(touches(j) for j in live):
                    dead.add(i); removed = True; n_spur += 1
                    ops.append('DEL_TRACK|%s|%s|%s|%s|%s|%s' % (net, f[1], f[3], f[4], f[5], f[6]))
                    break
    if not removed:
        break
print('spur segments pruned: %d' % n_spur)
open(sys.argv[1], 'w').write('\n'.join(ops) + '\n')
print('dangling groups %d: %d tracks, %d vias' % (sum(1 for m in groups.values() if [i for i in m if items[i][0] != 'PAD'] and
      len([i for i in m if items[i][0] == 'PAD']) < 2), n_t, n_v))
