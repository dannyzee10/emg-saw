"""Topology audit of a route plan against the report's stop-the-line checks that DRC cannot see.

reports/EMG main board routing requirements.md:
  G1  L2 (Mid Layer 1) carries no trace          -> any plan copper on Mid Layer 1
  G2  L4 is solid under every L3 trace            -> L3 track footprint over non-GND Bottom copper
  R1  antenna zone bare on all four layers        -> plan copper touching the antenna keep-out box
  P2  LX (switch node) has no vias, M2 VCAP no via -> vias on NetL1_1 / NetL1_2 / MCU_VCAP
  analog detour: routed length / straight end-to-end distance per connection (EMG_ANALOG/ADC/REFERENCE)

usage: GEOM_FILE=... python audit_plan.py PLAN.csv [more.csv ...]
Read-only; prints a summary and writes evidence/AUDIT_<plan stem>.txt.
"""
import csv, math, os, sys
from collections import defaultdict
from shapely.geometry import LineString, box
from shapely.ops import unary_union
import geom as G

ANT = box(*[float(v) for v in os.environ.get('ANT_BOX', '41.19,49.44,53.47,54.44').split(',')])   # default: B's antenna keep-out
NO_VIA = {'NetL1_1', 'NetL1_2', 'MCU_VCAP'}
G2_BAND = 0.2          # half-width margin around an L3 track that must see solid L4 (derived: ~2x L3-L4 prepreg)
# STACK=6 (C2 JLC06121H-3313): the planes are L2 = Mid Layer 1 and L4 = Mid Layer 3; L3 (Mid Layer 2) references L4 across
# the 0.1164 mm 2116 prepreg, so G2 is judged against Mid Layer 3 (only non-GND vias / through-hole pads make voids there).
SIX = os.environ.get('STACK', '4') == '6'
PLANES = ('Mid Layer 1', 'Mid Layer 3') if SIX else ('Mid Layer 1',)
REF_L3 = 'Mid Layer 3' if SIX else 'Bottom Layer'

objs, comps, keepouts = G.load()
classes = defaultdict(set)
for l in open(G.CLASSES, encoding='utf-8', errors='replace'):
    f = l.rstrip('\n').split('|')
    if f[0] == 'MEMBER' and f[1].startswith('EMG_'):
        classes[f[2]].add(f[1])
ANALOG = {n for n, c in classes.items() if c & {'EMG_ANALOG', 'EMG_ADC', 'EMG_REFERENCE'}}

rows = []
for p in sys.argv[1:]:
    rows += list(csv.DictReader(open(p)))
tracks = [r for r in rows if r['kind'] == 'TRACK']
vias = [r for r in rows if r['kind'] == 'VIA']
out = []


def seg(r):
    return LineString([(float(r['x1']), float(r['y1'])), (float(r['x2']), float(r['y2']))])


# G1
g1 = [r for r in tracks if r['layer'] in PLANES]
out.append(f'G1 plan tracks on the GND plane layer(s) {"/".join(PLANES)}: {len(g1)}')

# G2: non-GND copper on L3's reference layer (existing pads/tracks/vias are through-all, so vias count as antipads too)
l4_other = [o.geom for o in objs if REF_L3 in o.layers and o.net not in ('GND',) and o.kind in ('PAD', 'TRACK', 'ARC', 'REGION', 'FILL', 'VIA')]
l4_other += [seg(r).buffer(float(r['w']) / 2) for r in tracks if r['layer'] == REF_L3 and r['net'] != 'GND']
l4_other += [G.via(r['net'], float(r['x1']), float(r['y1']), float(r['d']), float(r['h'])).geom for r in vias if r['net'] != 'GND']
L4 = unary_union(l4_other)
g2 = defaultdict(float)
for r in tracks:
    if r['layer'] != 'Mid Layer 2':
        continue
    band = seg(r).buffer(float(r['w']) / 2 + G2_BAND)
    hit = band.intersection(L4)
    if not hit.is_empty and hit.area > 1e-4:
        # exclude the track's own vias (a via of the same net at a segment end is the layer change itself)
        own = unary_union([G.via(v['net'], float(v['x1']), float(v['y1']), float(v['d']), float(v['h'])).geom
                           for v in vias if v['net'] == r['net'] and v['group'] == r['group']] or [box(0, 0, 0, 0)])
        a = hit.difference(own.buffer(0.05)).area
        if a > 1e-4:
            g2[r['net']] += a
out.append(f'G2 L3 track bands over non-GND L4 copper/antipads: {len(g2)} nets, {sum(g2.values()):.3f} mm2')
for n, a in sorted(g2.items(), key=lambda t: -t[1])[:25]:
    out.append(f'   {n:22s} {a:.3f} mm2')

# R1
r1 = [r for r in tracks if seg(r).buffer(float(r['w']) / 2).intersects(ANT)] + [r for r in vias if ANT.distance(G.via(r['net'], float(r['x1']), float(r['y1']), float(r['d']), float(r['h'])).geom) == 0]
out.append(f'R1 plan copper in antenna zone: {len(r1)}')

# P2 / M2
nv = [(r['net'], r['x1'], r['y1']) for r in vias if r['net'] in NO_VIA]
out.append(f'P2/M2 vias on switch node / VCAP: {len(nv)} {nv[:10]}')

# detours + via counts per connection
by = defaultdict(list)
for r in rows:
    by[r.get('conn') or r['group']].append(r)
det, viac = [], defaultdict(int)
for k, rs in by.items():
    net = rs[0]['net']
    L = sum(seg(r).length for r in rs if r['kind'] == 'TRACK')
    nvia = sum(r['kind'] == 'VIA' for r in rs)
    cl = 'ANALOG' if net in ANALOG else ('POWER' if 'EMG_POWER' in classes[net] else ('SPI' if 'EMG_SPI' in classes[net] else 'OTHER'))
    viac[cl] += nvia
    pts = [(float(r['x1']), float(r['y1'])) for r in rs if r['kind'] == 'TRACK'] + [(float(r['x2']), float(r['y2'])) for r in rs if r['kind'] == 'TRACK']
    if not pts:
        continue
    # straight distance between the two most distant track endpoints approximates pad-to-pad span
    span = max(math.dist(a, b) for a in pts for b in pts) if len(pts) < 200 else L
    if net in ANALOG and span > 0.5 and L / span > 1.8:
        det.append((L / span, net, round(L, 2), round(span, 2), nvia))
out.append('vias per class: ' + ', '.join(f'{k} {v}' for k, v in sorted(viac.items())))
det.sort(reverse=True)
out.append(f'analog connections with length/span > 1.8: {len(det)}')
for d in det[:20]:
    out.append(f'   ratio {d[0]:.2f} {d[1]:18s} len {d[2]} span {d[3]} vias {d[4]}')
l3a = sum(seg(r).length for r in tracks if r['layer'] == 'Mid Layer 2' and r['net'] in ANALOG)
out.append(f'analog length on L3: {l3a:.1f} mm; total plan tracks {len(tracks)} vias {len(vias)}')
txt = '\n'.join(out)
print(txt)
stem = os.path.splitext(os.path.basename(sys.argv[1]))[0]
open(G.HERE + f'evidence/AUDIT_{stem}.txt', 'w').write(txt + '\n')
