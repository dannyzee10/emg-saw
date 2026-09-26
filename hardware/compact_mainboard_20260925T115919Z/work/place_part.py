"""Legal-spot search / check for single parts on one face (placement nudges).
A spot is legal when every pad keeps geom.required()+0.02 to all other copper on that face and to all vias (copper listed in
IGNORE_DEL rows is treated as already removed), 0.25+0.02 to keep-outs, 0.3 to through-hole pads/holes, 0.5 to the edge, and
the part's native box (COMP bbox, rotated) keeps 0.2 mm from other parts' boxes on that face (conservative stand-in for the
3D-body component clearance; Altium DRC is the judge).
usage: GEOM_FILE=... python place_part.py [--del DEL.csv] REF:x,y,rot[:search_radius] [REF:x,y,rot ...]
  parts are placed in the given order (each later part sees the earlier ones); prints the chosen spot of each and writes
  nothing - the caller turns the result into COMP ops."""
import csv, math, sys
from shapely.geometry import box, Point
from shapely import affinity
from shapely.strtree import STRtree
import geom as G

args = sys.argv[1:]
dels = args[args.index('--del') + 1] if '--del' in args else None
specs = [a for i, a in enumerate(args) if a != '--del' and (i == 0 or args[i - 1] != '--del')]
objs, comps, keepouts = G.load()
moving = {s.split(':')[0] for s in specs}
dk = set()
if dels:
    for r in csv.DictReader(open(dels)):
        dk.add(('T', r['net'], r['layer'], frozenset(((round(float(r['x1']), 3), round(float(r['y1']), 3)), (round(float(r['x2']), 3), round(float(r['y2']), 3))))) if r['kind'] == 'TRACK'
               else ('V', r['net'], round(float(r['x1']), 3), round(float(r['y1']), 3)))


def gone(o):
    s = o.src
    if s is None:
        return False
    if o.kind == 'TRACK':
        return ('T', s[2], s[1], frozenset(((round(float(s[3]), 3), round(float(s[4]), 3)), (round(float(s[5]), 3), round(float(s[6]), 3))))) in dk
    if o.kind in ('VIA', 'HOLE') and s[0] == 'VIA':
        return ('V', s[1], round(float(s[2]), 3), round(float(s[3]), 3)) in dk
    return False


pads = [o for o in objs if o.kind == 'PAD']
# env BODIES_FILE: native 3D-body export (BODYC rows) = what Altium's component clearance checks; parts without a body use
# the envelope of their pads.  Without it the (courtyard-sized) COMP bbox is used.
import os
from shapely.ops import unary_union
BODY = {}
if os.environ.get('BODIES_FILE'):
    for l in open(os.environ['BODIES_FILE'], encoding='utf-8', errors='replace'):
        f = l.rstrip('\n').split('|')
        if f[0] != 'BODYC':
            continue
        bx = [box(*map(float, t.split('@')[1].split(','))) for t in f[-1].split('BODYLAYERS=')[-1].split(';') if '@' in t]
        BODY[f[1]] = (float(f[3].split('=')[1]), float(f[4].split('=')[1]), float(f[5].split('=')[1]), unary_union(bx) if bx else None)


def body_abs(ref):
    b = BODY.get(ref)
    if b and b[3] is not None:
        return b[3]
    ps = [p.geom for p in pads if p.comp == ref]
    return unary_union(ps).envelope if ps else box(*map(float, comps[ref][6:10]))


def local(ref):
    r = comps[ref]; cx, cy, rot = float(r[3]), float(r[4]), float(r[5])
    lp = [(p.name, p.net, affinity.rotate(affinity.translate(p.geom, -cx, -cy), -rot, origin=(0, 0)))
          for p in pads if p.comp == ref]
    if BODY:
        cb = affinity.rotate(affinity.translate(body_abs(ref), -cx, -cy), -rot, origin=(0, 0))
    else:
        cb = affinity.rotate(affinity.translate(box(*map(float, r[6:10])), -cx, -cy), -rot, origin=(0, 0))
    return lp, cb, r[2]


placed = {}
for spec in specs:
    f = spec.split(':')
    ref = f[0]; x0, y0, rot0 = map(float, f[1].split(',')); rad = float(f[2]) if len(f) > 2 else 0.0
    lp, cb, side = local(ref)
    face = [o for o in objs if not gone(o) and o.comp not in moving and
            (o.kind == 'VIA' or (o.kind in ('PAD', 'TRACK', 'ARC', 'REGION', 'FILL') and side in o.layers))]
    face += [q for v in placed.values() for q in v[1]]
    holes = [o for o in objs if o.kind == 'HOLE' and not gone(o)]
    tree = STRtree([o.geom for o in face])
    boxes = [(body_abs(k2) if BODY else box(*map(float, r[6:10]))) for k2, r in comps.items() if r[2] == side and k2 not in moving] + \
            [v[0] for v in placed.values()]

    def legal(x, y, rot):
        wb = affinity.translate(affinity.rotate(cb, rot, origin=(0, 0)), x, y)
        if any(wb.buffer(0.2, join_style=2).intersects(b) for b in boxes):
            return None, 'body'
        out = []
        for name, net, g in lp:
            w = affinity.translate(affinity.rotate(g, rot, origin=(0, 0)), x, y)
            if not G.edge_ok(w):
                return None, 'edge'
            o = G.Obj(w, net, 'PAD', {side}, ref, name)
            if any(k.distance(w) < G.base_clr(net) + 0.02 for k in keepouts):
                return None, 'keepout'
            if any(h.geom.distance(w) < 0.3 for h in holes):
                return None, 'hole'
            for i in tree.query(w.buffer(0.6)):
                q = face[int(i)]
                if q.net == net and net not in ('', '-'):
                    continue
                if q.geom.distance(w) < G.required(o, q) + 0.02:
                    return None, f'{q.kind} {q.comp}.{q.name} {q.net}'
            out.append(o)
        return (wb, out), 'ok'
    best, why0 = None, None
    for r_ in [0.05 * i for i in range(int(rad / 0.05) + 1)]:
        for a in range(0, 360, 15 if r_ else 360):
            x, y = x0 + r_ * math.cos(math.radians(a)), y0 + r_ * math.sin(math.radians(a))
            res, why = legal(x, y, rot0)
            if why0 is None:
                why0 = why
            if res:
                best = (x, y, rot0, res); break
        if best:
            break
    if not best:
        print(f'{ref}: NO legal spot within {rad} mm of ({x0},{y0}) rot {rot0}; at the target: {why0}'); continue
    x, y, rot, res = best
    placed[ref] = res
    r = comps[ref]
    print(f'{ref}: ({float(r[3]):.3f},{float(r[4]):.3f}) rot {float(r[5]):.0f} -> ({x:.3f},{y:.3f}) rot {rot:.0f}  [{side}]')
