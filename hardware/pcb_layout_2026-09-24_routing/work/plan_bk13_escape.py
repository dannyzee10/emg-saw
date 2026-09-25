"""BK13 (0.35 mm pitch) socket escape pattern, identical for J_FPC1..5.

Top row  1 GND | 2 Va | 3 GND | 4 Vb | 5 GND   (+P1_1 3V0_ANA left, P2_1 GND right)
Edge row 6 Vc  | 7 GND| 8 VREF| 9 GND| 10 GND  (+P1_3 left, P2_3 right); keepout between rows.
Scheme (local mm, socket centre origin):
  pin5->P2_1, pins9/10->P2_3 at pad level; P2_1/P2_3 -> P2_2 -> GND via right.
  pin3 -> right between Vb (below) and Va (above) -> GND via.  pin1 -> GND via up-left.
  Va/Vb continue right to their RDD pads on TOP.
  pin8 VREF -> edge strip right -> via to L3.  pin6 Vc -> edge strip left -> via to L3.
  pin7 GND -> lower edge lane left (under Vc) -> GND via.  P1 lands tied -> 3V0_ANA via.
Writes evidence/BK13_ESCAPE_PLAN.csv and evidence/BK13_ZONES.csv; prints every verification failure.
"""
import csv, sys
from shapely.geometry import Point, box
import geom as G

objs, comps, keepouts = G.load()

W = 0.15   # escape width
WE = 0.12  # edge-lane width (two lanes must fit the 0.625 mm strip)
ZONE_LOCAL = (-4.0, -1.8, 3.1, 2.9)


def pattern(n):
    """v2: keepout-clearance-correct (0.13 mm to the between-row keepout), 0.15 mm edge lanes."""
    va, vb, vc, vr = f'Va_{n}', f'Vb_{n}', f'Vc_{n}', f'NetJ_FPC{n}_8'
    T, V = [], []
    t = lambda net, pts, w=W: T.append((net, pts, w))
    v = lambda net, x, y: V.append((net, x, y))
    t('GND', [(-0.7, 1.03), (-0.7, 1.7), (-1.0, 2.0)]); v('GND', -1.0, 2.0)                 # pin 1
    t(va, [(-0.35, 1.03), (-0.35, 2.75)])                                                  # pin 2 Va
    t('GND', [(0.0, 1.03), (0.0, 1.85), (2.4, 1.85), (2.4, 2.1)]); v('GND', 2.4, 2.1)      # pin 3
    t(vb, [(0.35, 1.03), (0.35, 1.4)])                                                     # pin 4 Vb
    t('GND', [(0.7, 1.03), (1.435, 1.03), (2.12, 1.03), (2.12, 0.4)])                      # pin5 -> P2_1 -> P2_2
    t('GND', [(0.35, -1.03), (1.435, -1.03), (2.12, -1.03), (2.12, -0.4)])                 # pins9/10 -> P2_3 -> P2_2
    t('GND', [(2.2, 0.0), (2.65, 0.0)], 0.25); v('GND', 2.65, 0.0)                          # P2_2 -> via
    t(vr, [(0.0, -1.03), (0.0, -1.35), (2.6, -1.35)]); v(vr, 2.6, -1.35)                   # pin 8 VREF
    t(vc, [(-0.7, -1.03), (-0.7, -1.32), (-2.7, -1.32), (-2.7, -1.0)]); v(vc, -2.7, -1.0)  # pin 6 Vc (upper lane)
    t('GND', [(-0.35, -1.03), (-0.35, -1.60), (-3.6, -1.60), (-3.6, -1.3)]); v('GND', -3.6, -1.3)  # pin 7 (lower lane)
    t('3V0_ANA', [(-1.435, 1.03), (-2.12, 1.03), (-2.12, 0.4)])                            # P1_1 -> P1_2
    t('3V0_ANA', [(-1.435, -1.03), (-2.12, -1.03), (-2.12, -0.4)])                         # P1_3 -> P1_2
    t('3V0_ANA', [(-2.2, 0.35), (-2.75, 0.35)], 0.25); v('3V0_ANA', -2.75, 0.35)           # P1_2 -> via
    return T, V


def expected_pads(n):
    return {'1': ('GND', -0.7, 0.8875), '2': (f'Va_{n}', -0.35, 0.8875), '3': ('GND', 0, 0.8875), '4': (f'Vb_{n}', 0.35, 0.8875),
            '5': ('GND', 0.7, 0.8875), '6': (f'Vc_{n}', -0.7, -0.8875), '7': ('GND', -0.35, -0.8875), '8': (f'NetJ_FPC{n}_8', 0, -0.8875),
            '9': ('GND', 0.35, -0.8875), '10': ('GND', 0.7, -0.8875)}


rows, zones, problems = [], [], []
for n in range(1, 6):
    ref = f'J_FPC{n}'
    c = comps[ref]
    cx, cy, rot = float(c[3]), float(c[4]), float(c[5])
    if abs(rot) > 1e-6:
        problems.append(f'{ref} rotated {rot}; pattern assumes 0'); continue
    pads = {o.name: o for o in objs if o.kind == 'PAD' and o.comp == ref}
    for num, (net, lx, ly) in expected_pads(n).items():
        p = pads[num].geom.centroid
        if pads[num].net != net or abs(p.x - cx - lx) > 1e-3 or abs(p.y - cy - ly) > 1e-3:
            problems.append(f'{ref}.{num} mismatch net={pads[num].net} at {p.x - cx:.4f},{p.y - cy:.4f}')
    T, V = pattern(n)
    # extend Va / Vb to their RDD pads on TOP (horizontal then 45 deg)
    for net, start in ((f'Va_{n}', (-0.35, 2.75)), (f'Vb_{n}', (0.35, 1.4))):
        tgt = [o for o in objs if o.kind == 'PAD' and o.net == net and o.comp.startswith('RDD')]
        if len(tgt) != 1:
            problems.append(f'{net}: expected one RDD pad, got {[o.comp for o in tgt]}'); continue
        P = tgt[0].geom.centroid
        sx, sy = cx + start[0], cy + start[1]
        dy = P.y - sy
        xt = P.x - abs(dy)
        split = cx + 3.0  # keep the lane corner inside the escape zone; continue outside
        pts = [(sx, sy), (split, sy), (xt, sy), (P.x, P.y)] if xt > split else [(sx, sy), (P.x, P.y)]
        T.append((net, [(x - cx, y - cy) for x, y in pts], W))
    zpoly = box(cx + ZONE_LOCAL[0], cy + ZONE_LOCAL[1], cx + ZONE_LOCAL[2], cy + ZONE_LOCAL[3])
    znets = {'GND', '3V0_ANA', f'Va_{n}', f'Vb_{n}', f'Vc_{n}', f'NetJ_FPC{n}_8'}
    G.ZONES.append((zpoly, znets, ref))
    zones.append((ref, *zpoly.bounds, ';'.join(sorted(znets))))
    for net, pts, w in T:
        ab = [(round(cx + x, 4), round(cy + y, 4)) for x, y in pts]
        for a, b in zip(ab, ab[1:]):
            rows.append({'kind': 'TRACK', 'group': ref, 'net': net, 'layer': 'Top Layer', 'x1': a[0], 'y1': a[1], 'x2': b[0], 'y2': b[1], 'w': w, 'd': '', 'h': ''})
    for net, x, y in V:
        rows.append({'kind': 'VIA', 'group': ref, 'net': net, 'layer': 'Multi Layer', 'x1': round(cx + x, 4), 'y1': round(cy + y, 4), 'x2': '', 'y2': '', 'w': '', 'd': 0.6, 'h': 0.3})

# ---- verification of the new copper against existing copper and against itself
idx = G.Index(objs)
new = []
for r in rows:
    if r['kind'] == 'TRACK':
        o = G.track(r['net'], r['layer'], [(r['x1'], r['y1']), (r['x2'], r['y2'])], r['w'])
    else:
        o = G.via(r['net'], r['x1'], r['y1'])
    o.name = f"{r['group']}:{r['kind']}:{r['net']}"
    new.append(o)
for o in new:
    for other, d, req in idx.violations(o):
        problems.append(f'{o.name} vs existing {other.kind} {other.comp}.{other.name} {other.net}: {d} < {req}')
    if not G.edge_ok(o.geom):
        problems.append(f'{o.name} edge setback {G.BOARD.exterior.distance(o.geom):.3f}')
for i, a in enumerate(new):
    for b in new[i + 1:]:
        if a.net == b.net or not (a.layers & b.layers):
            continue
        d = a.geom.distance(b.geom); req = G.required(a, b)
        if d < req - 1e-6:
            problems.append(f'self {a.name} vs {b.name}: {d:.4f} < {req}')
# via hole spacing
vias = [r for r in rows if r['kind'] == 'VIA']
for i, a in enumerate(vias):
    pa = Point(a['x1'], a['y1'])
    if not idx.hole_ok(pa, 0.15):
        problems.append(f"via {a['group']} {a['net']} hole-to-hole vs existing")
    for b in vias[i + 1:]:
        if pa.distance(Point(b['x1'], b['y1'])) < 0.3 + 0.254 - 1e-6:
            problems.append(f"via pair {a['net']}/{b['net']} hole spacing")

with open(G.HERE + 'evidence/BK13_ESCAPE_PLAN_V2.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
with open(G.HERE + 'evidence/BK13_ZONES.csv', 'w', newline='') as f:
    csv.writer(f).writerows([('ref', 'x0', 'y0', 'x1', 'y1', 'nets')] + zones)
print('tracks', sum(r['kind'] == 'TRACK' for r in rows), 'vias', len(vias))
print('PROBLEMS', len(problems))
for p in problems:
    print(' ', p)
