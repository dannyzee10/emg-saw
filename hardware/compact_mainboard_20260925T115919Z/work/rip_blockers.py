"""Rip-up for re-route: for every unrouted connection of a DRC json, find ROUTED copper (rows of the given plan CSVs that
still exist natively) within R mm of either end, on the end's layer or as a via, and rip the whole routed connection.
Fixed copper is never ripped: groups whose name starts with 'S' (plane stitches), BK13 fan-out, hot loop, placement copper.
Writes DEL.csv (native rows) for apply_rip_offline.py / build_ops --del, and FIRST.txt (the unrouted connection keys, to be
routed before the ripped ones).
usage: GEOM_FILE=... python rip_blockers.py DRC.json DEL.csv FIRST.txt R PLAN.csv [PLAN.csv ...]  [--extra-del OPS.txt]"""
import csv, json, re, sys
from shapely.geometry import LineString, Point
import geom as G

args = sys.argv[1:]
extra = args[args.index('--extra-del') + 1] if '--extra-del' in args else None
args = [a for a in args if a not in ('--extra-del', extra)]
drc, out_del, out_first, R = args[0], args[1], args[2], float(args[3])
plans = args[4:]
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
native = {k_obj(o): o for o in free}
grp, rows_of = {}, {}
for p in plans:
    for r in csv.DictReader(open(p)):
        g = p.replace('\\', '/').rsplit('/', 1)[-1] + '|' + r['group']
        if r['group'].split(':')[0].startswith('S'):
            continue                                        # plane stitch: fixed
        grp[k_row(r)] = g
        rows_of.setdefault(g, []).append(r)
first, rip = [], set()
for s in json.load(open(drc))['details']:
    m = re.match(r'Un-Routed Net Constraint: Net (\S+) Between (.*) And (.*)$', s.strip())
    if not m:
        continue
    first.append(s.strip())
    for part in (m.group(2), m.group(3)):
        pts = [(float(a), float(b)) for a, b in re.findall(r'\(([-\d.]+)mm,\s*([-\d.]+)mm\)', part)]
        g = LineString(pts) if part.startswith('Track') and len(pts) == 2 else Point(pts[0])
        lay = 'Bottom Layer' if ('L6 BOTTOM' in part or 'L4 BOTTOM' in part) else ('Top Layer' if 'L1 TOP' in part else None)
        zone = g.buffer(R)
        for o in free:
            if o.net == m.group(1):
                continue
            if o.kind == 'TRACK' and lay and next(iter(o.layers)) != lay:
                continue
            if o.geom.intersects(zone):
                gname = grp.get(k_obj(o))
                if gname:
                    rip.add(gname)
dl = []
for g in sorted(rip):
    for r in rows_of[g]:
        if k_row(r) in native:
            dl.append(dict(r, group=g))
if extra:                                              # e.g. antenna pruning ops (DEL_TRACK / DEL_VIA lines)
    seen = {k_row(r) for r in dl}
    for l in open(extra):
        f = l.strip().split('|')
        if f[0] == 'DEL_TRACK':
            r = {'kind': 'TRACK', 'group': 'PRUNE', 'net': f[1], 'layer': f[2], 'x1': f[3], 'y1': f[4], 'x2': f[5], 'y2': f[6], 'w': '', 'd': '', 'h': '', 'conn': ''}
        elif f[0] == 'DEL_VIA':
            r = {'kind': 'VIA', 'group': 'PRUNE', 'net': f[1], 'layer': 'Multi Layer', 'x1': f[2], 'y1': f[3], 'x2': '', 'y2': '', 'w': '', 'd': '', 'h': '', 'conn': ''}
        else:
            continue
        if k_row(r) not in seen:
            dl.append(r); seen.add(k_row(r))
with open(out_del, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['kind', 'group', 'net', 'layer', 'x1', 'y1', 'x2', 'y2', 'w', 'd', 'h', 'conn'], extrasaction='ignore')
    w.writeheader(); w.writerows(dl)
open(out_first, 'w').write('\n'.join(first) + '\n')
print(f'unrouted {len(first)} -> routed connections ripped {len(rip)} ({len(dl)} native objects incl. pruning)')
