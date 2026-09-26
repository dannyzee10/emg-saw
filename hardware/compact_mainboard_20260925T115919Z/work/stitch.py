"""Plane stitching for C2 6L: every copper group of GND that reaches no via / through-hole pad (i.e. no L2 / L4 plane) gets a
short stub + via; every 3V0_ANA group inside the L5 analog pour region gets a stub + via landing inside that region.
Candidates ring each pad of the group (0.6/0.3 via first, then 0.45/0.2; stub 0.25 -> 0.2 -> 0.15 mm); a candidate must pass
the same exact checks as build_ops.py (clearance by rule class, board edge 0.5, keepouts, hole-to-hole 0.254, no via within
0.1 mm of any pad).  GND stitch vias of parts outside the converter cell keep 0.8 mm from the hot loop (report P7).

usage: GEOM_FILE=... python stitch.py OUT_PLAN.csv [--del DEL.csv] [--extra PLAN.csv ...]
  --del    native copper that will be deleted first (rip list)     --extra  fixed plans written in the same batch
env R_ANA="x,y;x,y;..." (3V0_ANA pour polygon), BK13_ZONES (escape zones for the 0.13 mm rule)
"""
import csv, os, sys
from collections import defaultdict
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union
import geom as G

args = sys.argv[1:]
out_path = args[0]
dels = args[args.index('--del') + 1] if '--del' in args else None
extras = [a for i, a in enumerate(args) if i > 0 and args[i - 1] == '--extra']
R_ANA = Polygon([tuple(map(float, p.split(','))) for p in os.environ['R_ANA'].split(';')])
HOT_PARTS = {'UP2', 'L1', 'CUP4', 'CUP4_1', 'CUP4_FB', 'C_UV_BYPASS'}

objs, comps, keepouts = G.load()
for z in csv.DictReader(open(os.environ.get('BK13_ZONES', G.HERE + 'evidence/BK13_ZONES.csv'))):
    G.ZONES.append((box(float(z['x0']), float(z['y0']), float(z['x1']), float(z['y1'])), set(z['nets'].split(';')), z['ref']))


def tkey(net, lay, x1, y1, x2, y2):
    return ('T', net, lay, frozenset(((round(float(x1), 3), round(float(y1), 3)), (round(float(x2), 3), round(float(y2), 3)))))


if dels:
    dk = set()
    for r in csv.DictReader(open(dels)):
        dk.add(tkey(r['net'], r['layer'], r['x1'], r['y1'], r['x2'], r['y2']) if r['kind'] == 'TRACK'
               else ('V', r['net'], round(float(r['x1']), 3), round(float(r['y1']), 3)))

    def ok(o):
        s = o.src
        if s is None:
            return True
        if o.kind == 'TRACK':
            return tkey(s[2], s[1], s[3], s[4], s[5], s[6]) not in dk
        if s[0] == 'VIA':
            return ('V', s[1], round(float(s[2]), 3), round(float(s[3]), 3)) not in dk
        return True
    objs = [o for o in objs if ok(o)]
for p in extras:
    for r in csv.DictReader(open(p)):
        if r['kind'] == 'TRACK':
            objs.append(G.track(r['net'], r['layer'], [(float(r['x1']), float(r['y1'])), (float(r['x2']), float(r['y2']))], float(r['w'])))
        else:
            d, h = float(r['d'] or 0.6), float(r['h'] or 0.3)
            v = G.via(r['net'], float(r['x1']), float(r['y1']), d, h); v.src = ('VIA', r['net'], r['x1'], r['y1'])
            objs.append(v)
            objs.append(G.Obj(Point(float(r['x1']), float(r['y1'])).buffer(h / 2), r['net'], 'HOLE', set()))
idx = G.Index(objs)
pads = [o for o in objs if o.kind == 'PAD']
hot = unary_union([o.geom for o in pads if o.comp in HOT_PARTS]).envelope
from shapely.strtree import STRtree
PAD_TREE = STRtree([o.geom for o in pads])


def near_pad(g):
    """any pad (any net, own pad included) within 0.1 mm of g - build_ops' 'via on pad' test"""
    return any(pads[int(i)].geom.distance(g) < 0.1 - 1e-6 for i in PAD_TREE.query(g.buffer(0.1)))


def groups(net):
    items = [o for o in objs if o.net == net and o.kind in ('PAD', 'TRACK', 'VIA', 'ARC')]
    par = list(range(len(items)))

    def f(a):
        while par[a] != a:
            par[a] = par[par[a]]; a = par[a]
        return a
    from shapely.strtree import STRtree
    tr = STRtree([o.geom for o in items])
    for i, o in enumerate(items):
        for j in tr.query(o.geom.buffer(0.001)):
            j = int(j)
            if j > i and items[j].layers & o.layers and items[j].geom.distance(o.geom) < 0.001:
                par[f(i)] = f(j)
    g = defaultdict(list)
    for i, o in enumerate(items):
        g[f(i)].append(o)
    return list(g.values())


def anchored(grp, net):
    for o in grp:
        if net == 'GND' and (o.kind == 'VIA' or (o.kind == 'PAD' and len(o.layers) > 2)):
            return True
        if net == '3V0_ANA' and o.kind == 'VIA' and R_ANA.buffer(-0.4).contains(o.geom.centroid):
            return True
    return False


MODE2 = os.environ.get('STITCH_MODE', '1') == '2'   # retry pass: longer stubs, then via-in-pad (POFV) on pads >= 0.5 mm


def via_in_pad(p, net):
    """0.45/0.2 via at the pad centre (filled + capped, POFV); the pad must be >= 0.5 mm in both directions."""
    b = p.geom.minimum_rotated_rectangle
    xs = [pt for pt in b.exterior.coords]
    e = sorted({round(Point(xs[i]).distance(Point(xs[i + 1])), 4) for i in range(4)})
    if min(e) < 0.5:
        return None
    c = p.geom.centroid
    vg = G.via(net, c.x, c.y, 0.45, 0.2)
    if any(k.intersects(vg.geom) for k in keepouts) or not G.edge_ok(vg.geom):
        return None
    others = [pads[int(i)] for i in PAD_TREE.query(vg.geom.buffer(0.1)) if pads[int(i)] is not p]
    if any(o.geom.distance(vg.geom) < 0.1 - 1e-6 for o in others):
        return None
    if idx.violations(vg) or not idx.hole_ok(c, 0.1):
        return None
    return (0.0, (c.x, c.y), (c.x, c.y), 0, 0.45, 0.2, next(iter(p.layers)))


def try_pad(p, net, allow_hot):
    lay = next(iter(p.layers))
    c = p.geom.centroid
    best = None
    for vd, vh in ((0.6, 0.3), (0.45, 0.2)):
        for ring in [0.105 + vd / 2 + 0.07 * k for k in range(0, 30 if MODE2 else 18)]:
            outline = p.geom.buffer(ring, 16).exterior
            n = max(12, int(outline.length / 0.1))
            for i in range(n):
                q = outline.interpolate(i / n, normalized=True)
                if best and c.distance(q) >= best[0]:
                    continue
                vg = G.via(net, q.x, q.y, vd, vh)
                if net == '3V0_ANA' and not R_ANA.buffer(-0.4).contains(q):
                    continue
                if net == 'GND' and not allow_hot and hot.distance(q) < 0.8:
                    continue
                if not G.edge_ok(vg.geom) or any(k.intersects(vg.geom) for k in keepouts):
                    continue
                if near_pad(vg.geom):
                    continue
                if idx.violations(vg) or not idx.hole_ok(q, vh / 2):
                    continue
                for w in (0.25, 0.2, 0.15):
                    tg = G.track(net, lay, [(c.x, c.y), (q.x, q.y)], w)
                    if not G.edge_ok(tg.geom) or idx.violations(tg):
                        continue
                    best = (c.distance(q), (c.x, c.y), (q.x, q.y), w, vd, vh, lay)
                    break
        if best:
            return best
    return None


ONLY = None   # env ONLY_DRC=parsed DRC json: stitch only groups holding a pad Altium still lists as unrouted (pours are seen)
if os.environ.get('ONLY_DRC'):
    import json, re
    ONLY = set()
    for s in json.load(open(os.environ['ONLY_DRC']))['details']:
        m = re.match(r'Un-Routed Net Constraint: Net (GND|3V0_ANA) Between (.*)$', s.strip())
        if m:
            for comp, pin in re.findall(r'Pad (\S+?)-(\S+?)\(', m.group(2)):
                ONLY.add((m.group(1), comp, pin))
rows, failed, k = [], [], 0
for net in ('GND', '3V0_ANA'):
    for grp in groups(net):
        if anchored(grp, net):
            continue
        gpads = [o for o in grp if o.kind == 'PAD' and len(o.layers) == 1 and o.comp]
        if not gpads:
            continue
        if ONLY is not None and not any((net, o.comp if o.comp != 'FREE' else o.name, o.name if o.comp != 'FREE' else 'TP') in ONLY
                                        or (net, o.comp, o.name) in ONLY for o in gpads):
            continue
        if net == '3V0_ANA' and not all(R_ANA.contains(o.geom.centroid) for o in gpads):
            continue           # outside the analog pour (MCU VDDA branch): left to the router
        allow_hot = any(o.comp in HOT_PARTS for o in gpads)
        cands = [b for b in (try_pad(p, net, allow_hot) for p in sorted(gpads, key=lambda o: -o.geom.area)[:6]) if b]
        label = ','.join(sorted({f'{o.comp}.{o.name}' for o in gpads}))[:120]
        vip = False
        if not cands and MODE2 and (net == 'GND' or all(R_ANA.buffer(-0.4).contains(o.geom.centroid) for o in gpads)):
            cands = [b for b in (via_in_pad(p, net) for p in sorted(gpads, key=lambda o: -o.geom.area)) if b][:1]
            vip = bool(cands)
        if not cands:
            failed.append((net, label)); continue
        d, a, b, w, vd, vh, lay = min(cands)
        grp_name = f'S{k}:{net}' + (' VIP' if vip else ''); k += 1
        if not vip:
            rows.append({'kind': 'TRACK', 'group': grp_name, 'net': net, 'layer': lay, 'x1': round(a[0], 4), 'y1': round(a[1], 4),
                         'x2': round(b[0], 4), 'y2': round(b[1], 4), 'w': w, 'd': '', 'h': '', 'conn': label, 'relax': 0})
        rows.append({'kind': 'VIA', 'group': grp_name, 'net': net, 'layer': 'Multi Layer', 'x1': round(b[0], 4), 'y1': round(b[1], 4),
                     'x2': '', 'y2': '', 'w': '', 'd': vd, 'h': vh, 'conn': label, 'relax': 0})
        vg = G.via(net, b[0], b[1], vd, vh)
        if not vip:
            idx.add(G.track(net, lay, [a, b], w))
        idx.add(vg); idx.add(G.Obj(Point(*b).buffer(vh / 2), net, 'HOLE', set()))
        if k % 5 == 0:
            print(f'  {k} stitched, {len(failed)} failed', flush=True)
with open(out_path, 'w', newline='') as f:
    wr = csv.DictWriter(f, fieldnames=['kind', 'group', 'net', 'layer', 'x1', 'y1', 'x2', 'y2', 'w', 'd', 'h', 'conn', 'relax'])
    wr.writeheader(); wr.writerows(rows)
print(f'stitched groups {k}: vias {sum(r["kind"] == "VIA" for r in rows)} (0.45 mm: {sum(r["kind"] == "VIA" and float(r["d"]) < 0.5 for r in rows)}); failed {len(failed)}')
for net, label in failed:
    print('  FAILED', net, label)
