"""Re-plan the GND fanout of specific pads (keepout-aware model), keeping every other planned object.
usage: GEOM_FILE=... python replan_pads.py in_plan.csv out_plan.csv PAD[,PAD...] [other_plan.csv ...]"""
import csv, math, sys
from shapely.geometry import LineString, Point, box
from shapely.strtree import STRtree
import geom as G

inp, outp, names = sys.argv[1], sys.argv[2], sys.argv[3].split(',')
others = sys.argv[4:]
objs, comps, keepouts = G.load()
for z in csv.DictReader(open(G.HERE + 'evidence/BK13_ZONES.csv')):
    G.ZONES.append((box(float(z['x0']), float(z['y0']), float(z['x1']), float(z['y1'])), set(z['nets'].split(';')), z['ref']))
idx = G.Index(objs)
rows = list(csv.DictReader(open(inp)))
keep = [r for r in rows if r['group'] not in names]
dropped = [r for r in rows if r['group'] in names]


def add(r):
    if r['kind'] == 'TRACK':
        idx.add(G.track(r['net'], r['layer'], [(float(r['x1']), float(r['y1'])), (float(r['x2']), float(r['y2']))], float(r['w'])))
    else:
        idx.add(G.via(r['net'], float(r['x1']), float(r['y1']), float(r['d']), float(r['h'])))
        idx.add(G.Obj(Point(float(r['x1']), float(r['y1'])).buffer(float(r['h']) / 2), r['net'], 'HOLE', set()))


for r in keep:
    add(r)
for p in others:
    for r in csv.DictReader(open(p)):
        add(r)
pads = [o for o in objs if o.kind == 'PAD']
ptree = STRtree([o.geom for o in pads])
new = []
for name in names:
    comp, pin = name.rsplit('-', 1)
    p = [o for o in pads if o.comp == comp and o.name == pin][0]
    c = p.geom.centroid
    b = p.geom.bounds
    w = 0.15 if min(b[2] - b[0], b[3] - b[1]) < 0.45 else min(0.3, min(b[2] - b[0], b[3] - b[1]) * 0.9)
    best = None
    for dv, hv in ((0.6, 0.3), (0.45, 0.2)):
        for ang in range(0, 360, 10):
            dx, dy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
            for k in range(1, 61):
                d = 0.05 * k
                if best and d >= best[0]:
                    break
                vx, vy = c.x + dx * d, c.y + dy * d
                vo = G.via('GND', vx, vy, dv, hv)
                vg = vo.geom.buffer(0.1)
                if any(pads[i].geom.intersects(vg) for i in ptree.query(vg)):
                    continue
                if not G.edge_ok(vo.geom):
                    break
                ray = LineString([(c.x, c.y), (vx, vy)])
                ex = p.geom.exterior.intersection(ray)
                if ex.is_empty:
                    continue
                ex = ex if ex.geom_type == 'Point' else list(ex.geoms)[0]
                stub = G.track('GND', 'Top Layer', [(ex.x, ex.y), (vx, vy)], w)
                if idx.violations(vo) or idx.violations(stub) or not idx.hole_ok(Point(vx, vy), hv / 2):
                    continue
                best = (d, vx, vy, (ex.x, ex.y), dv, hv)
                break
        if best:
            break
    if not best:
        print('NO SOLUTION for', name); continue
    d, vx, vy, ex, dv, hv = best
    tr = {'kind': 'TRACK', 'group': name, 'net': 'GND', 'layer': 'Top Layer', 'x1': round(ex[0], 4), 'y1': round(ex[1], 4), 'x2': round(vx, 4), 'y2': round(vy, 4), 'w': w, 'd': '', 'h': ''}
    vi = {'kind': 'VIA', 'group': name, 'net': 'GND', 'layer': 'Multi Layer', 'x1': round(vx, 4), 'y1': round(vy, 4), 'x2': '', 'y2': '', 'w': '', 'd': dv, 'h': hv}
    new += [tr, vi]; add(tr); add(vi)
    print(f'{name}: via {dv}/{hv} at ({vx:.3f},{vy:.3f}) stub {d:.2f} mm')
with open(outp, 'w', newline='') as f:
    wr = csv.DictWriter(f, fieldnames=list(rows[0].keys())); wr.writeheader(); wr.writerows(keep + new)
with open(outp.replace('.csv', '_DROPPED.csv'), 'w', newline='') as f:
    wr = csv.DictWriter(f, fieldnames=list(rows[0].keys())); wr.writeheader(); wr.writerows(dropped)
print('kept', len(keep), 'dropped', len(dropped), 'new', len(new))
