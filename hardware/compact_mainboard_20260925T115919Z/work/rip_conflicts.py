"""Which existing router copper blocks a planned fixed pattern?  Every free (non-component) track/via of the native export
that violates clearance / hole spacing against the NEW plan is mapped back to its routing-trial connection (group) through
the trial plan CSVs; the whole connection is ripped (all of its rows still present natively), so nothing is left dangling.
Copper that is not in any trial plan (restored hot loop, thermal vias, placement copper) is never ripped: it is reported.

usage: GEOM_FILE=... python rip_conflicts.py NEW_PLAN.csv OUT_DEL.csv TRIAL_PLAN.csv [TRIAL_PLAN.csv ...]
OUT_DEL.csv rows: kind (TRACK/VIA), group, net, layer, x1, y1, x2, y2, w, d, h, conn  -> feed to plan_to_ops (DEL mode).
"""
import csv, sys
from collections import defaultdict
from shapely.geometry import Point
import geom as G

new_plan, out_del, trials = sys.argv[1], sys.argv[2], sys.argv[3:]
objs, comps, keepouts = G.load()
free = [o for o in objs if o.kind in ('TRACK', 'VIA') and o.src is not None and not (o.kind == 'TRACK' and 'INCOMP=True' in o.src)]


def key_of(o):
    s = o.src
    if o.kind == 'TRACK':
        a = (round(float(s[3]), 3), round(float(s[4]), 3)); b = (round(float(s[5]), 3), round(float(s[6]), 3))
        return ('TRACK', s[2], s[1], frozenset((a, b)))
    return ('VIA', s[1], round(float(s[2]), 3), round(float(s[3]), 3))


def key_row(r):
    if r['kind'] == 'TRACK':
        a = (round(float(r['x1']), 3), round(float(r['y1']), 3)); b = (round(float(r['x2']), 3), round(float(r['y2']), 3))
        return ('TRACK', r['net'], r['layer'], frozenset((a, b)))
    return ('VIA', r['net'], round(float(r['x1']), 3), round(float(r['y1']), 3))


group_of, rows_of = {}, defaultdict(list)
for p in trials:
    for r in csv.DictReader(open(p)):
        g = p.rsplit('/', 1)[-1] + '|' + r['group']
        group_of[key_row(r)] = g
        rows_of[g].append(r)
native = {key_of(o): o for o in free}

idx = G.Index([o for o in objs])
hits = set()
for r in csv.DictReader(open(new_plan)):
    if r['kind'] == 'TRACK':
        o = G.track(r['net'], r['layer'], [(float(r['x1']), float(r['y1'])), (float(r['x2']), float(r['y2']))], float(r['w']))
    else:
        o = G.via(r['net'], float(r['x1']), float(r['y1']), float(r['d'] or 0.6), float(r['h'] or 0.3))
    for other, d, req in idx.violations(o):
        if other.kind in ('TRACK', 'VIA') and other in free:
            hits.add(key_of(other))
    if r['kind'] == 'VIA':   # hole spacing against existing vias
        c = Point(float(r['x1']), float(r['y1']))
        for v in free:
            if v.kind == 'VIA' and v.net != r['net'] and Point(float(v.src[2]), float(v.src[3])).distance(c) < 0.3 + 0.254 + 0.3:
                hits.add(key_of(v))
rip, orphan = set(), []
for k in hits:
    g = group_of.get(k)
    if g:
        rip.add(g)
    else:
        orphan.append(k)
out = []
for g in sorted(rip):
    for r in rows_of[g]:
        if key_row(r) in native:          # rows removed earlier (antenna pruning) are not deleted twice
            out.append(dict(r, group=g))
with open(out_del, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['kind', 'group', 'net', 'layer', 'x1', 'y1', 'x2', 'y2', 'w', 'd', 'h', 'conn'], extrasaction='ignore')
    w.writeheader(); w.writerows(out)
print(f'blocking objects {len(hits)} -> trial connections ripped {len(rip)} ({len(out)} native objects); not in any trial plan {len(orphan)}')
for g in sorted(rip):
    print('  RIP', g)
for k in orphan:
    print('  KEEP (not trial copper)', k[:3])
