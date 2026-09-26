"""Region rip-up: every ROUTED connection (group of the given plan CSVs) with copper inside one of the boxes is ripped whole
(all of its rows still present natively).  Fixed copper (plane stitches = groups 'S..', BK13 fan-out, hot loop, placement
copper) is never ripped.  Native-orphan copper (free copper inside a box that belongs to no plan) is listed and ripped too
only when --orphans is given (it is usually left-overs of earlier partial rips).
usage: GEOM_FILE=... python rip_region.py OUT_DEL.csv "x0,y0,x1,y1;x0,y0,x1,y1" PLAN.csv [...] [--orphans]"""
import csv, sys
from shapely.geometry import box
import geom as G

args = [a for a in sys.argv[1:] if a != '--orphans']
orph = '--orphans' in sys.argv
out_del, boxes, plans = args[0], [box(*map(float, b.split(','))) for b in args[1].split(';')], args[2:]
objs, comps, keepouts = G.load()


def k_row(r):
    if r['kind'] == 'TRACK':
        return ('T', r['net'], r['layer'], frozenset(((round(float(r['x1']), 3), round(float(r['y1']), 3)), (round(float(r['x2']), 3), round(float(r['y2']), 3)))))
    return ('V', r['net'], round(float(r['x1']), 3), round(float(r['y1']), 3))


def k_obj(o):
    s = o.src
    if o.kind == 'TRACK':
        return ('T', s[2], s[1], frozenset(((round(float(s[3]), 3), round(float(s[4]), 3)), (round(float(s[5]), 3), round(float(s[6]), 3)))))
    return ('V', s[1], round(float(s[2]), 3), round(float(s[3]), 3))


free = [o for o in objs if o.kind in ('TRACK', 'VIA') and o.src is not None and not (o.kind == 'TRACK' and 'INCOMP=True' in o.src)]
native = {k_obj(o) for o in free}
grp, rows_of, fixed = {}, {}, set()
for p in plans:
    for r in csv.DictReader(open(p)):
        if r['group'].split(':')[0].startswith('S') or p.replace('\\', '/').endswith('BK13_ESCAPE_PLAN_C2.csv'):
            fixed.add(k_row(r)); continue
        g = p.replace('\\', '/').rsplit('/', 1)[-1] + '|' + r['group']
        grp[k_row(r)] = g
        rows_of.setdefault(g, []).append(r)
rip, orphans = set(), []
for o in free:
    if not any(o.geom.intersects(b) for b in boxes):
        continue
    k = k_obj(o)
    if k in grp:
        rip.add(grp[k])
    elif k not in fixed:
        orphans.append((o, k))
dl, seen = [], set()
for g in sorted(rip):
    for r in rows_of[g]:
        kr = k_row(r)
        if kr in native and kr not in seen:
            dl.append(dict(r, group=g)); seen.add(kr)
if orph:
    for o, k in orphans:
        if k in seen:
            continue
        s = o.src
        if o.kind == 'TRACK':
            dl.append({'kind': 'TRACK', 'group': 'ORPHAN', 'net': s[2], 'layer': s[1], 'x1': s[3], 'y1': s[4], 'x2': s[5], 'y2': s[6], 'w': s[7], 'd': '', 'h': '', 'conn': ''})
        else:
            dl.append({'kind': 'VIA', 'group': 'ORPHAN', 'net': s[1], 'layer': 'Multi Layer', 'x1': s[2], 'y1': s[3], 'x2': '', 'y2': '', 'w': '', 'd': s[4], 'h': s[5], 'conn': ''})
        seen.add(k)
with open(out_del, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['kind', 'group', 'net', 'layer', 'x1', 'y1', 'x2', 'y2', 'w', 'd', 'h', 'conn'], extrasaction='ignore')
    w.writeheader(); w.writerows(dl)
print(f'connections ripped {len(rip)} -> {len(dl)} objects; orphan objects in boxes {len(orphans)} ({"ripped" if orph else "kept"})')
from collections import Counter
print('  nets:', dict(Counter(g.split('|')[1].split(':')[1].replace(' VIP', '') for g in rip)))
