"""Fab-capability check of the native geometry export against JLCPCB multilayer limits (numbers from
jlcpcb.com/capabilities/pcb-capabilities, read 27 Sep 2026).  Reports the worst cases, not DRC.
usage: GEOM_FILE=... BOARD_BOX=... python fab_check.py"""
import sys
from collections import Counter, defaultdict
from shapely.strtree import STRtree
import geom as G

JLC = {'trace_w': 0.09, 'trace_gap': 0.09, 'via_hole': 0.15, 'via_dia': 0.25, 'via_to_track': 0.2, 'pad_to_track': 0.1,
       'smd_pad_gap': 0.15, 'via_hole_to_hole': 0.2, 'pad_hole_to_hole': 0.45, 'edge': 0.2, 'mask_dam': 0.10}
objs, comps, keepouts = G.load()
cu = [o for o in objs if o.kind in ('TRACK', 'VIA', 'PAD')]
tree = STRtree([o.geom for o in cu])
worst = defaultdict(lambda: (9.0, None))


def note(key, d, a, b):
    if d < worst[key][0]:
        worst[key] = (d, (a.kind, a.net, a.comp, a.name, b.kind, b.net, b.comp, b.name,
                          round(a.geom.centroid.x, 3), round(a.geom.centroid.y, 3)))


for i, a in enumerate(cu):
    for j in tree.query(a.geom.buffer(0.3)):
        j = int(j)
        if j <= i:
            continue
        b = cu[j]
        if a.net == b.net and a.net not in ('', '-'):
            continue
        if not (a.layers & b.layers):
            continue
        d = a.geom.distance(b.geom)
        kinds = {a.kind, b.kind}
        if kinds == {'TRACK'}:
            note('trace_gap', d, a, b)
        elif kinds == {'VIA', 'TRACK'}:
            note('via_to_track', d, a, b)
        elif kinds == {'PAD', 'TRACK'}:
            note('pad_to_track', d, a, b)
        elif kinds == {'VIA'} or kinds == {'VIA', 'PAD'}:
            note('via_to_via_or_pad', d, a, b)
        elif kinds == {'PAD'} and len(a.layers) == 1 and len(b.layers) == 1:
            note('smd_pad_gap_same_comp' if a.comp == b.comp and a.comp not in ('FREE', '') else 'smd_pad_gap_diff_comp', d, a, b)
holes = [o for o in objs if o.kind == 'HOLE']
ht = STRtree([h.geom for h in holes])
for i, a in enumerate(holes):
    for j in ht.query(a.geom.buffer(0.6)):
        j = int(j)
        if j <= i:
            continue
        b = holes[j]
        d = a.geom.distance(b.geom)
        kind = 'via_hole_to_hole' if (a.src and a.src[0] == 'VIA' and b.src and b.src[0] == 'VIA') else 'pad_or_mixed_hole_to_hole'
        if d < worst[kind][0]:
            worst[kind] = (d, (a.net, b.net, round(a.geom.centroid.x, 3), round(a.geom.centroid.y, 3)))
tw = Counter(round(float(o.src[7]), 3) for o in objs if o.kind == 'TRACK' and o.src is not None)
vs = Counter((float(o.src[4]), float(o.src[5])) for o in objs if o.kind == 'VIA' and o.src is not None)
print('track widths:', sorted(tw.items()))
print('vias (dia, hole):', dict(vs))
edge = min((G.BOARD.exterior.distance(o.geom) for o in cu), default=9)
print(f'min copper to board edge: {edge:.3f}  (JLC >= {JLC["edge"]})')
for k, (d, info) in sorted(worst.items()):
    print(f'{k:28s} min {d:.3f}   {info}')
print('JLC limits:', JLC)
