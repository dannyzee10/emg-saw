"""Move the 15 DNP DRL input resistors (R_DRL_VAn/VBn/VCn) out of the BK13 socket keep-outs.

Altium applies the J_FPCn footprint keep-out (Keep-Out layer) to tracks and vias on EVERY layer (probe
DRC_KEEPOUT_PROBE), so pad 1 of these Bottom resistors, placed under the sockets in C2, cannot be connected.
Each is re-placed on the Bottom in the free gap right of its socket, pad 1 facing the socket.  A spot is legal when
  - every pad (true copper) keeps the rule clearance (geom.required + 0.02 margin) to all Bottom copper and all vias
    of other nets, 0.25 mm + margin to every keep-out, 0.5 mm to the board edge;
  - its courtyard box (native COMP bbox, rotated) does not overlap another Bottom component's box.
Copper attached to the old pads is taken out by removing whole routing-trial connections (plan CSVs) that touch them.
usage: GEOM_FILE=... python relocate_drl.py OUT_COMP_OPS.txt OUT_DEL.csv TRIAL_PLAN.csv [...]
"""
import csv, math, sys
from shapely.geometry import box, Point
from shapely import affinity
import geom as G

out_ops, out_del, trials = sys.argv[1], sys.argv[2], sys.argv[3:]
objs, comps, keepouts = G.load()
pads = [o for o in objs if o.kind == 'PAD']
REFS = [f'R_DRL_V{k}{n}' for n in range(1, 6) for k in 'ABC']
moving = set(REFS)
uid = {}
for l in open(G.GEOM, encoding='utf-8', errors='replace'):
    f = l.rstrip('\n').split('|')
    if f[0] == 'COMP' and f[1] in moving:
        uid[f[1]] = f
bot_copper = [o for o in objs if o.kind in ('PAD', 'TRACK', 'ARC', 'REGION', 'FILL', 'VIA') and
              ('Bottom Layer' in o.layers or o.kind == 'VIA') and o.comp not in moving]
from shapely.strtree import STRtree
tree = STRtree([o.geom for o in bot_copper])
others_box = [(r, box(*map(float, r[6:10]))) for ref, r in comps.items() if r[2] == 'Bottom Layer' and ref not in moving]
placed_boxes = []


def local_pads(ref):
    """pad copper polygons in the component frame (origin at the component centre, rotation removed)"""
    r = comps[ref]; cx, cy, rot = float(r[3]), float(r[4]), float(r[5])
    out = []
    for p in pads:
        if p.comp == ref:
            g = affinity.rotate(affinity.translate(p.geom, -cx, -cy), -rot, origin=(0, 0))
            out.append((p.name, p.net, g))
    x0, y0, x1, y1 = map(float, r[6:10])
    cb = affinity.rotate(affinity.translate(box(x0, y0, x1, y1), -cx, -cy), -rot, origin=(0, 0))
    return out, cb


def legal(ref, x, y, rot):
    lp, cb = local_pads(ref)
    wb = affinity.translate(affinity.rotate(cb, rot, origin=(0, 0)), x, y)
    wg = wb.buffer(0.2, join_style=2)   # Altium component clearance 0.2 mm between bodies
    if any(wg.intersects(b) for r, b in others_box) or any(wg.intersects(b) for b in placed_boxes):
        return None
    wp = []
    for name, net, g in lp:
        w = affinity.translate(affinity.rotate(g, rot, origin=(0, 0)), x, y)
        if not G.edge_ok(w):
            return None
        o = G.Obj(w, net, 'PAD', {'Bottom Layer'}, ref, name)
        for k in keepouts:
            if k.distance(w) < G.base_clr(net) + 0.02:
                return None
        for i in tree.query(w.buffer(0.5)):
            q = bot_copper[int(i)]
            if q.net == net and net not in ('', '-'):
                continue
            if q.geom.distance(w) < G.required(o, q) + 0.02:
                return None
        wp.append((name, net, w))
    return wb, wp


ops, moved = [], {}
for n in range(1, 6):
    jx = float(comps[f'J_FPC{n}'][3])
    for j, k in enumerate('ABC'):
        ref = f'R_DRL_V{k}{n}'
        tx, ty = jx + 5.4, 11.0 + 1.7 * j
        best = None
        for rad in [0.1 * i for i in range(0, 80)]:
            for a in range(0, 360, 15 if rad else 360):
                x, y = tx + rad * math.cos(math.radians(a)), ty + rad * math.sin(math.radians(a))
                for rot in (0, 180, 90, 270):
                    res = legal(ref, x, y, rot)
                    if res:
                        # pad 1 should face the socket (smaller x) - prefer rot 0
                        best = (rad + (0 if rot == 0 else 0.3), x, y, rot, res); break
                if best:
                    break
            if best:
                break
        if not best:
            print('NO SPOT', ref); continue
        _, x, y, rot, (wb, wp) = best
        placed_boxes.append(wb)
        for name, net, w in wp:   # new pads are obstacles for the next resistors
            bot_copper.append(G.Obj(w, net, 'PAD', {'Bottom Layer'}, ref, name))
        tree = STRtree([o.geom for o in bot_copper])
        f = uid[ref]
        moved[ref] = (x, y, rot)
        print(f'{ref}: ({float(f[3]):.3f},{float(f[4]):.3f}) rot {float(f[5]):.0f} -> ({x:.3f},{y:.3f}) rot {rot}')
print('moved', len(moved), 'of', len(REFS))
# source UIDs are not in the geometry export: take them from the component ledger
src = {}
for r in csv.DictReader(open(G.HERE + 'evidence/C2_COMPONENT_LEDGER.csv')):
    d = r.get('designator') or r.get('Designator') or r.get('ref')
    if d in moved:
        src[d] = r.get('src_uid') or r.get('SourceUniqueId') or r.get('uid')
with open(out_ops, 'w') as f:
    for ref, (x, y, rot) in moved.items():
        f.write(f'COMP|{ref}|{src.get(ref, "?")}|Bottom|0|{x:.4f}|{y:.4f}|1|{rot:.3f}\n')
# trial copper touching the old pads -> whole trial connections to delete
old = [p for p in pads if p.comp in moving]
free = [o for o in objs if o.kind in ('TRACK', 'VIA') and o.src is not None and not (o.kind == 'TRACK' and 'INCOMP=True' in o.src)]
hit = [o for o in free if any(o.net == p.net and o.geom.intersects(p.geom) and (o.layers & p.layers) for p in old)]


def kr(r):
    if r['kind'] == 'TRACK':
        return ('T', r['net'], r['layer'], frozenset(((round(float(r['x1']), 3), round(float(r['y1']), 3)), (round(float(r['x2']), 3), round(float(r['y2']), 3)))))
    return ('V', r['net'], round(float(r['x1']), 3), round(float(r['y1']), 3))


def ko(o):
    s = o.src
    if o.kind == 'TRACK':
        return ('T', s[2], s[1], frozenset(((round(float(s[3]), 3), round(float(s[4]), 3)), (round(float(s[5]), 3), round(float(s[6]), 3)))))
    return ('V', s[1], round(float(s[2]), 3), round(float(s[3]), 3))


native = {ko(o) for o in free}
grp, rows_of = {}, {}
for p in trials:
    for r in csv.DictReader(open(p)):
        g = p.rsplit('/', 1)[-1] + '|' + r['group']
        grp[kr(r)] = g; rows_of.setdefault(g, []).append(r)
rip = {grp[ko(o)] for o in hit if ko(o) in grp}
orphan = [ko(o) for o in hit if ko(o) not in grp]
dl = [dict(r, group=g) for g in sorted(rip) for r in rows_of[g] if kr(r) in native]
with open(out_del, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['kind', 'group', 'net', 'layer', 'x1', 'y1', 'x2', 'y2', 'w', 'd', 'h', 'conn'], extrasaction='ignore')
    w.writeheader(); w.writerows(dl)
print('copper on the old pads:', len(hit), 'objects -> trial connections ripped', len(rip), f'({len(dl)} objects); not trial copper: {len(orphan)}')
for o in orphan:
    print('  ORPHAN', o[:3])
