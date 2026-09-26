"""Top-layer copper that crosses the STM32 (U_MCU1) pin-ring interior without belonging to an MCU pin's own fan-out.
The LQFP interior on L1 is the fan-out area for the pins; through-traffic there blocks the pin escapes.  Lists each such
track with its routing connection (plan CSV group) so the whole connection can be ripped and re-routed on inner layers.
usage: GEOM_FILE=... python mcu_through_traffic.py OUT_DEL.csv PLAN.csv [...]"""
import csv, sys
from shapely.geometry import box
import geom as G

out_del, plans = sys.argv[1], sys.argv[2:]
objs, comps, keepouts = G.load()
mp = [o for o in objs if o.kind == 'PAD' and o.comp == 'U_MCU1']
x0 = min(p.geom.bounds[0] for p in mp); y0 = min(p.geom.bounds[1] for p in mp)
x1 = max(p.geom.bounds[2] for p in mp); y1 = max(p.geom.bounds[3] for p in mp)
inner = box(x0 + 1.6, y0 + 1.6, x1 - 1.6, y1 - 1.6)        # inside the pad ring (pads are ~1.5 mm long)
mcu_nets = {p.net for p in mp}
tr = [o for o in objs if o.kind == 'TRACK' and 'Top Layer' in o.layers and o.src is not None and 'INCOMP=False' in o.src]
hits = [o for o in tr if o.geom.intersects(inner) and o.net not in mcu_nets]
print(f'MCU pad-ring interior {inner.bounds}; Top through-traffic tracks: {len(hits)}')


def k(r):
    return (r['net'], r['layer'], frozenset(((round(float(r['x1']), 3), round(float(r['y1']), 3)), (round(float(r['x2']), 3), round(float(r['y2']), 3)))))


def ko(o):
    s = o.src
    return (s[2], s[1], frozenset(((round(float(s[3]), 3), round(float(s[4]), 3)), (round(float(s[5]), 3), round(float(s[6]), 3)))))


grp, rows = {}, {}
for p in plans:
    for r in csv.DictReader(open(p)):
        if r['kind'] == 'TRACK':
            grp[k(r)] = p.rsplit('/', 1)[-1] + '|' + r['group']
        rows.setdefault(p.rsplit('/', 1)[-1] + '|' + r['group'], []).append(r)
native_t = {ko(o) for o in tr}
native_v = {(o.src[1], round(float(o.src[2]), 3), round(float(o.src[3]), 3)) for o in objs if o.kind == 'VIA' and o.src is not None}
gs = sorted({grp.get(ko(o), '?') for o in hits})
for o in hits:
    print('  ', o.net, [round(float(v), 3) for v in o.src[3:8]], grp.get(ko(o), 'NOT IN A PLAN'))
out = []
for g in gs:
    if g == '?':
        continue
    for r in rows[g]:
        if (r['kind'] == 'TRACK' and k(r) in native_t) or (r['kind'] == 'VIA' and (r['net'], round(float(r['x1']), 3), round(float(r['y1']), 3)) in native_v):
            out.append(dict(r, group=g))
with open(out_del, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['kind', 'group', 'net', 'layer', 'x1', 'y1', 'x2', 'y2', 'w', 'd', 'h', 'conn'], extrasaction='ignore')
    w.writeheader(); w.writerows(out)
print('connections to rip:', [g for g in gs if g != '?'], '->', len(out), 'objects')
