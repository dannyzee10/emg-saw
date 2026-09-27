"""Delete rows for a dead track chain (DRC 'Net Antennae'): start at the dangling end of NET at X,Y and walk track by track
while the chain is a simple path (each joint touches exactly two tracks of the net and nothing else: no pad, via,
fill or other copper of the net).  Stops BEFORE the first real junction; the tracks walked are the dead stub.
usage: GEOM_FILE=... python prune_chain.py OUT_DEL.csv NET X Y"""
import csv, sys
from shapely.geometry import Point
import geom as G

out, net, x, y = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
objs, comps, keepouts = G.load()
cu = [o for o in objs if o.net == net and o.kind in ('TRACK', 'VIA', 'PAD', 'ARC', 'FILL', 'REGION')]


def touching(pt, layers):
    P = Point(pt).buffer(0.01)
    return [o for o in cu if (o.layers & layers) and o.geom.intersects(P)]


dead, pt, prev = [], (x, y), None
while True:
    t = [o for o in touching(pt, set(G.COPPER)) if o is not prev]
    tracks = [o for o in t if o.kind == 'TRACK']
    if len(t) != 1 or len(tracks) != 1:
        break                                   # junction, pad, via, pour or nothing: stop
    tr = tracks[0]
    s = tr.src                                  # ('TRACK', layer, net, x1, y1, x2, y2, w)
    a, b = (float(s[3]), float(s[4])), (float(s[5]), float(s[6]))
    far = b if Point(a).distance(Point(pt)) < 0.01 else a
    dead.append(tr)
    prev, pt = tr, far
    # the far end: stop if anything besides this track touches it (a real junction) -> keep going only on a simple path
    others = [o for o in touching(pt, tr.layers) if o is not tr]
    if len(others) != 1 or others[0].kind != 'TRACK':
        break
rows = []
for tr in dead:
    s = tr.src
    rows.append({'kind': 'TRACK', 'group': 'PRUNE', 'net': net, 'layer': s[1], 'x1': s[3], 'y1': s[4], 'x2': s[5], 'y2': s[6],
                 'w': s[7]})
fields = ['kind', 'group', 'net', 'layer', 'x1', 'y1', 'x2', 'y2', 'w', 'd', 'h', 'conn', 'relax']
with open(out, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore', restval=''); w.writeheader(); w.writerows(rows)
print(f'{len(rows)} dead tracks, stopped at {pt}')
for r in rows:
    print('  ', r['layer'], r['x1'], r['y1'], r['x2'], r['y2'], r['w'])
