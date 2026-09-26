"""Plane access by search: for every unrouted GND / 3V0_ANA connection of a DRC json, each end whose copper island has no
plane access (GND: no via / through-hole pad; 3V0_ANA: no via inside the L5 analog pour R_ANA) is routed ON ITS OWN LAYER to
the nearest cell where a via is legal (router5 masks: clearances by class, holes, edge, keep-outs, L5 reservation, via-in-pad
rules), and a via is dropped there.  Unlike stitch.py (fixed rings around each pad) the stub may wind up to WIN mm away.
usage: <router env> R_ANA="x,y;..." python plane_route.py DRC.json OUT_PLAN.csv
env WIN (2.5 mm search window around the end), VIA (0.45,0.2)"""
import csv, json, os, sys
import numpy as np
from shapely.geometry import Point, Polygon

drc, out_path = sys.argv[1], sys.argv[2]
sys.argv = [sys.argv[0]]
import router5 as R
G = R.G

R_ANA = Polygon([tuple(map(float, p.split(','))) for p in os.environ['R_ANA'].split(';')])
WIN = float(os.environ.get('WIN', '2.5'))
VD, VH = map(float, os.environ.get('VIA', '0.45,0.2').split(','))
NETS = ('GND', '3V0_ANA')


def has_access(net, comp):
    for g, ls in comp:
        if len(ls) >= len(R.LAYERS):              # via or through-hole pad (all routing layers)
            if net == 'GND' or R_ANA.contains(g.centroid):
                return True
    return False


def ana_mask(W):
    iy0, iy1, ix0, ix1 = W
    m = np.zeros((iy1 - iy0, ix1 - ix0), bool)
    inner = R_ANA.buffer(-VD / 2 - 0.05)
    for iy in range(iy0, iy1):
        for ix in range(ix0, ix1):
            x, y = R.cell_xy(ix, iy)
            m[iy - iy0, ix - ix0] = inner.contains(Point(x, y))
    return m


conns = [c for c in (R.parse_conn(d) for d in json.load(open(drc))['details'] if d.startswith('Un-Routed')) if c]
conns = [c for c in conns if c[0] in NETS]
rows, done, k = [], set(), 0
for net, a, b in conns:
    for end in (a, b):
        g, ls = R.end_copper(end, net)
        if g is None:
            print(f'  {net} {end["text"][:50]}: endpoint not matched'); continue
        comp = R.component(net, g)
        if has_access(net, comp):
            continue
        key = id(comp[0][0]) if comp else id(g)
        if any(any(gg is d for gg, _ in comp) for d in done):
            continue
        ok = False
        for w in R.widths(net):
            W = R.window(g, g, WIN)
            free, via_ok = R.maps(net, w, W, VD, VH)
            if net == '3V0_ANA':
                via_ok &= ana_mask(W)
            for L in [L for L in R.LAYERS if L in ls]:
                s = R.comp_nodes([(gg, lls) for gg, lls in comp if L in lls], free, W, [L])
                if not s:
                    continue
                goals = [(R.LAYERS.index(L), int(x), int(y)) for y, x in zip(*np.nonzero(via_ok & free[L]))]
                if not goals:
                    continue
                path = R.astar(free, via_ok, s, goals, R.layer_cost(net), [L], 400000)
                if os.environ.get('DEBUG'):
                    from scipy import ndimage as _nd
                    lab, _ = _nd.label(free[L], structure=np.ones((3, 3)))
                    reach = set(lab[y, x] for _, x, y in s) - {0}
                    rc = int(np.isin(lab, list(reach)).sum()) if reach else 0
                    print(f'    dbg {L} w {w}: starts {len(s)} goals {len(goals)} reachable cells {rc} path {bool(path)}')
                if not path:
                    continue
                segs, _ = R.to_segments(path, W) if len(path) > 1 else ([], [])
                vx, vy = R.cell_xy(path[-1][1] + W[2], path[-1][2] + W[0])
                k += 1; tag = f'Q{k}:{net}'
                new = []
                for LL, pts in segs:
                    for p, q in zip(pts, pts[1:]):
                        new.append({'kind': 'TRACK', 'group': tag, 'net': net, 'layer': LL, 'x1': round(p[0], 4), 'y1': round(p[1], 4),
                                    'x2': round(q[0], 4), 'y2': round(q[1], 4), 'w': w, 'd': '', 'h': '', 'conn': 'plane|' + end['text'][:60], 'relax': 0})
                new.append({'kind': 'VIA', 'group': tag, 'net': net, 'layer': 'Multi Layer', 'x1': round(vx, 4), 'y1': round(vy, 4),
                            'x2': '', 'y2': '', 'w': '', 'd': VD, 'h': VH, 'conn': 'plane|' + end['text'][:60], 'relax': 0})
                if R.VIP and R._in_own_pad(net, vx, vy, VD):
                    for r in new:
                        r['group'] = tag + ' VIP'
                R.stamp_rows(new)
                rows += new; done.add(g); ok = True
                print(f'  {net} {end["text"][:60]}: via at ({vx:.3f},{vy:.3f}) on {L}, stub {len(new) - 1} segs, w {w}')
                break
            if ok:
                break
        if not ok:
            print(f'  {net} {end["text"][:60]}: NO legal via site within {WIN} mm')
fields = ['kind', 'group', 'net', 'layer', 'x1', 'y1', 'x2', 'y2', 'w', 'd', 'h', 'conn', 'relax']
with open(out_path, 'w', newline='') as f:
    wr = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore', restval=''); wr.writeheader(); wr.writerows(rows)
print(f'plane_route: {k} ends stitched, {len(rows)} rows -> {out_path}')
