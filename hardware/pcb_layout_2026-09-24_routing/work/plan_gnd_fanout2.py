"""GND fanout v2 on the shared rule model (true copper, rule priorities, BK13 plan as existing copper).

For every top-side GND pad not already tied to a GND via: short top stub from the pad edge to a new
0.6/0.3 GND via, or (fallback) a straight tie to an existing/planned GND via within 2.5 mm.
Exposed-pad devices: UP1 pins 4/5/8/15 -> EP17 (EP already has 4 vias), UP4 pins 1/4/6 -> EP9 + one
0.45/0.2 EP via (same treatment Astra used for UP1's EP). BK13 sockets are handled by plan_bk13_escape.
Writes evidence/GND_FANOUT_PLAN2.csv (same row format as the BK13 plan).
"""
import csv, math
from shapely.geometry import LineString, Point
import geom as G

objs, comps, keepouts = G.load()
# existing + BK13 plan copper
bk = list(csv.DictReader(open(G.HERE + 'evidence/BK13_ESCAPE_PLAN.csv')))
zones = list(csv.DictReader(open(G.HERE + 'evidence/BK13_ZONES.csv')))
from shapely.geometry import box
for z in zones:
    G.ZONES.append((box(float(z['x0']), float(z['y0']), float(z['x1']), float(z['y1'])), set(z['nets'].split(';')), z['ref']))
idx = G.Index(objs)
for r in bk:
    if r['kind'] == 'TRACK':
        idx.add(G.track(r['net'], r['layer'], [(float(r['x1']), float(r['y1'])), (float(r['x2']), float(r['y2']))], float(r['w'])))
    else:
        idx.add(G.via(r['net'], float(r['x1']), float(r['y1'])))
        idx.add(G.Obj(Point(float(r['x1']), float(r['y1'])).buffer(0.15), r['net'], 'HOLE', set()))

pads = [o for o in objs if o.kind == 'PAD']
all_pads_geom = [o.geom for o in pads]
from shapely.strtree import STRtree
_ptree = STRtree(all_pads_geom)


def near_pad(g):
    return any(all_pads_geom[i].intersects(g) for i in _ptree.query(g))
existing_vias = [o for o in objs if o.kind == 'VIA' and o.net == 'GND'] + [o for o in idx.extra if o.kind == 'VIA' and o.net == 'GND']
gnd_top_tracks = [o for o in objs if o.kind == 'TRACK' and o.net == 'GND' and 'Top Layer' in o.layers]


def connected(p):
    """pad already reaches a GND via directly or through an existing top GND track."""
    for v in existing_vias:
        if p.geom.intersects(v.geom.centroid.buffer(0.05)):
            return True
    for t in gnd_top_tracks:
        if t.geom.intersects(p.geom) and any(t.geom.intersects(v.geom.centroid.buffer(0.01)) for v in existing_vias):
            return True
    return False


EP_TIE = {('UP1', '4'): '17', ('UP1', '5'): '17', ('UP1', '8'): '17', ('UP1', '15'): '17',
          ('UP4', '1'): '9', ('UP4', '4'): '9', ('UP4', '6'): '9'}
rows, problems = [], []


def add_track(net, pts, w, group):
    for a, b in zip(pts, pts[1:]):
        rows.append({'kind': 'TRACK', 'group': group, 'net': net, 'layer': 'Top Layer', 'x1': round(a[0], 4), 'y1': round(a[1], 4),
                     'x2': round(b[0], 4), 'y2': round(b[1], 4), 'w': w, 'd': '', 'h': ''})
        idx.add(G.track(net, 'Top Layer', [a, b], w))


def add_via(net, x, y, group, d=0.6, h=0.3):
    rows.append({'kind': 'VIA', 'group': group, 'net': net, 'layer': 'Multi Layer', 'x1': round(x, 4), 'y1': round(y, 4), 'x2': '', 'y2': '', 'w': '', 'd': d, 'h': h})
    v = G.via(net, x, y, d, h); idx.add(v); existing_vias.append(v)
    idx.add(G.Obj(Point(x, y).buffer(h / 2), net, 'HOLE', set()))


# --- exposed-pad ties
padmap = {(o.comp, o.name): o for o in pads if 'Top Layer' in o.layers}
ep9 = padmap[('UP4', '9')]
c9 = ep9.geom.centroid
add_via('GND', c9.x, c9.y, 'UP4-9 EP via', 0.45, 0.2)
for (comp, pin), ep in EP_TIE.items():
    p, e = padmap[(comp, pin)], padmap[(comp, ep)]
    a = p.geom.centroid
    eb = e.geom.bounds
    pb = p.geom.bounds
    horiz = (pb[2] - pb[0]) > (pb[3] - pb[1])        # pad long axis
    if horiz:   # left/right column: run along x into the EP, then along y if the pin row is outside the EP
        xe = min(max(a.x, eb[0] + 0.15), eb[2] - 0.15)
        ye = min(max(a.y, eb[1] + 0.12), eb[3] - 0.12)
        pts = [(a.x, a.y), (xe, a.y)] + ([(xe, ye)] if abs(ye - a.y) > 1e-6 else [])
    else:
        ye = min(max(a.y, eb[1] + 0.15), eb[3] - 0.15)
        xe = min(max(a.x, eb[0] + 0.12), eb[2] - 0.12)
        pts = [(a.x, a.y), (a.x, ye)] + ([(xe, ye)] if abs(xe - a.x) > 1e-6 else [])
    w = 0.15 if comp == 'UP4' else 0.2
    bad = []
    for s0, s1 in zip(pts, pts[1:]):
        bad += idx.violations(G.track('GND', 'Top Layer', [s0, s1], w))
    if bad:
        problems.append(f'EP tie {comp}.{pin}->{ep}: ' + '; '.join(f'{o.comp}.{o.name} {o.net} {d}<{rq}' for o, d, rq in bad[:3]))
        continue
    add_track('GND', pts, w, f'EP tie {comp}.{pin}')

# --- generic fanout
todo = [p for p in pads if p.net == 'GND' and p.layers == {'Top Layer'} and not p.comp.startswith('J_FPC')
        and (p.comp, p.name) not in EP_TIE and p is not ep9 and not connected(p)]


def search(p, d_via, h_via):
    """first VALID via position along each of 24 rays (true copper, rule model); best by stub length."""
    c = p.geom.centroid
    b = p.geom.bounds
    narrow = min(b[2] - b[0], b[3] - b[1])
    w = 0.15 if narrow < 0.45 else min(0.3, narrow * 0.9)
    best = None
    for ang in range(0, 360, 15):
        dx, dy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        for k in range(1, 61):
            d = 0.05 * k
            if best and d >= best[0]:
                break
            vx, vy = c.x + dx * d, c.y + dy * d
            vo = G.via('GND', vx, vy, d_via, h_via)
            vg = vo.geom.buffer(0.1)  # keep >=0.1 mm mask web between any via and any pad copper
            if vg.intersects(p.geom) or near_pad(vg):
                continue
            if not G.edge_ok(vo.geom) or any(k_.intersects(vo.geom) for k_ in keepouts):
                break
            ray = LineString([(c.x, c.y), (vx, vy)])
            ex = p.geom.exterior.intersection(ray)
            if ex.is_empty:
                continue
            ex = ex if ex.geom_type == 'Point' else list(ex.geoms)[0]
            stub = G.track('GND', 'Top Layer', [(ex.x, ex.y), (vx, vy)], w)
            if idx.violations(vo) or idx.violations(stub) or not idx.hole_ok(Point(vx, vy), h_via / 2):
                continue
            best = (d, vx, vy, w, (ex.x, ex.y), d_via, h_via)
            break
    return best


def hardness(p):
    near = [o for o in idx.near(p.geom, 0.6) if o.kind == 'PAD' and o.net != 'GND']
    return -len(near)


order = sorted(todo, key=hardness)
failed = []
for p in order:
    best = search(p, 0.6, 0.3) or search(p, 0.45, 0.2)
    if best:
        d, vx, vy, w, ex, dv, hv = best
        add_track('GND', [ex, (vx, vy)], w, f'{p.comp}-{p.name}')
        add_via('GND', vx, vy, f'{p.comp}-{p.name}', dv, hv)
        continue
    # fallback: tie to an existing/planned GND via
    c = p.geom.centroid
    b = p.geom.bounds; w = 0.15 if min(b[2] - b[0], b[3] - b[1]) < 0.45 else 0.2
    done = False
    for v in sorted(existing_vias, key=lambda v: v.geom.centroid.distance(c)):
        vc = v.geom.centroid
        if vc.distance(c) > 2.5:
            break
        ray = LineString([(c.x, c.y), (vc.x, vc.y)])
        ex = p.geom.exterior.intersection(ray)
        if ex.is_empty:
            continue
        ex = ex if ex.geom_type == 'Point' else list(ex.geoms)[0]
        stub = G.track('GND', 'Top Layer', [(ex.x, ex.y), (vc.x, vc.y)], w)
        if not idx.violations(stub):
            add_track('GND', [(ex.x, ex.y), (vc.x, vc.y)], w, f'{p.comp}-{p.name} tie')
            done = True; break
    if not done:
        failed.append(f'{p.comp}-{p.name}')

# --- enclosed op-amp bypass caps: L-tie over the neighbouring cap to a GND point that has a via
L_TIES = {'CU_11-1': ('FREE', 'TP_GND_ANA'), 'CU_12-1': ('CU_22', '2'), 'CU_14-1': ('CU_24', '2')}
for key, (tc, tp) in L_TIES.items():
    if key not in failed:
        continue
    comp, pin = key.split('-')
    p = padmap[(comp, pin)]
    t = [o for o in pads if o.comp == tc and o.name == tp][0]
    a, b = p.geom.centroid, t.geom.centroid
    top = p.geom.bounds[3]
    tx = b.x if tc != 'FREE' else t.geom.bounds[2] - 0.2
    done = False
    for k in range(25, 60):
        yt = top + 0.01 * k
        pts = [(a.x, a.y), (a.x, yt), (tx, yt), (tx, b.y if tc != 'FREE' else yt)]
        pts = [q for i, q in enumerate(pts) if i == 0 or q != pts[i - 1]]
        segs = [G.track('GND', 'Top Layer', [s0, s1], 0.15) for s0, s1 in zip(pts, pts[1:])]
        if all(not idx.violations(sg) for sg in segs):
            add_track('GND', pts, 0.15, f'{key} L-tie to {tc}.{tp}')
            failed.remove(key); done = True
            break
    if not done:
        problems.append(f'L-tie {key} not found')

with open(G.HERE + 'evidence/GND_FANOUT_PLAN2.csv', 'w', newline='') as f:
    wr = csv.DictWriter(f, fieldnames=['kind', 'group', 'net', 'layer', 'x1', 'y1', 'x2', 'y2', 'w', 'd', 'h'])
    wr.writeheader(); wr.writerows(rows)
print('pads considered', len(todo), 'tracks', sum(r['kind'] == 'TRACK' for r in rows), 'vias', sum(r['kind'] == 'VIA' for r in rows))
print('FAILED', len(failed), failed)
print('PROBLEMS', problems)
