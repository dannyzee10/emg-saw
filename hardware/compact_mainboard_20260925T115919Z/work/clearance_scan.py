"""Independent whole-board copper clearance scan of a native geometry export (not Altium DRC): every TRACK / VIA against
every other-net copper object (pads, tracks, vias, keep-outs) with the rule model in geom.required (class clearances,
BK13 escape zones, fine-pitch regions; vias 0.2 mm even inside BK13 zones = the stricter JLC-motivated model).
usage: GEOM_FILE=... python clearance_scan.py"""
from collections import Counter
import geom as G

objs, comps, keepouts = G.load()
EX = G.Index(objs)
seen, viol = set(), []
for o in objs:
    if o.kind not in ('TRACK', 'VIA'):
        continue
    for other, d, req in EX.violations(o):
        key = tuple(sorted((id(o), id(other))))
        if key in seen:
            continue
        seen.add(key)
        viol.append((round(req - d, 4), o, other, d, req))
viol.sort(key=lambda v: -v[0])
print(f'copper objects scanned: {sum(1 for o in objs if o.kind in ("TRACK", "VIA"))} tracks/vias; violations: {len(viol)}')
print('by pair kind:', Counter(f'{v[1].kind}-{v[2].kind}' for v in viol))
for short, o, other, d, req in viol[:25]:
    c = o.geom.centroid
    print(f'  {o.kind} {o.net} {sorted(o.layers)[:1]} at ({c.x:.3f},{c.y:.3f}) vs {other.kind} {other.net} {other.comp} '
          f'{other.name}: d={d:.3f} req={req}  (short by {short:.3f})')
