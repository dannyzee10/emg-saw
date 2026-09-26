"""Rip list for a placement nudge: every routed plan group whose copper ON THE PART'S FACE (or a via) touches a pad of the
given parts, plus native orphan copper on that face touching those pads.  Top/inner traffic passing over the pads is kept.
usage: GEOM_FILE=... python rip_attached.py OUT_DEL.csv REF[,REF...] PLAN.csv [...]"""
import csv, sys
import geom as G

out_del, refs, plans = sys.argv[1], set(sys.argv[2].split(',')), sys.argv[3:]
objs, comps, keepouts = G.load()
pads = [o for o in objs if o.kind == 'PAD' and o.comp in refs]
face = {l for p in pads for l in p.layers}


def k_row(r):
    if r['kind'] == 'TRACK':
        return ('T', r['net'], r['layer'], frozenset(((round(float(r['x1']), 3), round(float(r['y1']), 3)), (round(float(r['x2']), 3), round(float(r['y2']), 3)))))
    return ('V', r['net'], round(float(r['x1']), 3), round(float(r['y1']), 3))


def k_src(o):
    s = o.src
    if o.kind == 'TRACK':
        return ('T', s[2], s[1], frozenset(((round(float(s[3]), 3), round(float(s[4]), 3)), (round(float(s[5]), 3), round(float(s[6]), 3)))))
    return ('V', s[1], round(float(s[2]), 3), round(float(s[3]), 3))


native = {k_src(o): o for o in objs if o.kind in ('TRACK', 'VIA') and o.src is not None}
touching = set()
for o in objs:
    if o.kind not in ('TRACK', 'VIA') or o.src is None:
        continue
    if o.kind == 'TRACK' and not (o.layers & face):
        continue
    if any(p.net == o.net and p.geom.distance(o.geom) < 0.002 for p in pads):
        touching.add(k_src(o))
rows, seen, groups = [], set(), set()
for p in plans:
    tag = p.replace('\\', '/').rsplit('/', 1)[-1]
    if tag.startswith(('BK13_ESCAPE', 'STITCH')):
        continue
    by_group = {}
    for r in csv.DictReader(open(p)):
        by_group.setdefault(r['group'], []).append(r)
    for g, rs in by_group.items():
        if g.split(':')[0].startswith('S'):
            continue
        ks = [k_row(r) for r in rs]
        if any(k in touching for k in ks):
            groups.add(tag + '|' + g)
            for r, k in zip(rs, ks):
                if k in native and k not in seen:
                    seen.add(k); rows.append(r)
orph = [k for k in touching if k not in seen]
for k in orph:
    o = native[k]; s = o.src
    if o.kind == 'TRACK':
        rows.append({'kind': 'TRACK', 'group': 'ORPHAN', 'net': s[2], 'layer': s[1], 'x1': s[3], 'y1': s[4], 'x2': s[5], 'y2': s[6], 'w': s[7]})
    else:
        rows.append({'kind': 'VIA', 'group': 'ORPHAN', 'net': s[1], 'layer': 'Multi Layer', 'x1': s[2], 'y1': s[3], 'd': s[4], 'h': s[5]})
    seen.add(k)
fields = ['kind', 'group', 'net', 'layer', 'x1', 'y1', 'x2', 'y2', 'w', 'd', 'h', 'conn', 'relax']
with open(out_del, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore', restval=''); w.writeheader(); w.writerows(rows)
print(f'parts {sorted(refs)} face {sorted(face)}: groups {len(groups)}, orphan objects {len(orph)} -> {len(rows)} rows')
for g in sorted(groups):
    print('  ', g)
