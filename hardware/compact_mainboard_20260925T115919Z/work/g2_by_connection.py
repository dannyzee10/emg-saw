"""G2 per routed connection, judged against the NATIVE board state (all rounds written): a connection is G2-clean when none
of its L3 (Mid Layer 2) tracks has non-GND L4 copper / via antipads inside the track band (same rule and band as audit_plan.py;
the connection's own layer-change vias are excluded).
usage: GEOM_FILE=native_export python g2_by_connection.py PLAN_OK.csv [more.csv ...]   -> evidence/C2_G2_BY_CONNECTION.txt"""
import csv, os, sys
from collections import defaultdict
from shapely.geometry import LineString, box
from shapely.ops import unary_union
from shapely.strtree import STRtree
import geom as G

G2_BAND = 0.2
objs, comps, keepouts = G.load()
classes = defaultdict(set)
for l in open(G.CLASSES, encoding='utf-8', errors='replace'):
    f = l.rstrip('\n').split('|')
    if f[0] == 'MEMBER' and f[1].startswith('EMG_'):
        classes[f[2]].add(f[1])
ANALOG = {n for n, c in classes.items() if c & {'EMG_ANALOG', 'EMG_ADC', 'EMG_REFERENCE'}}

# STACK=6: L3's reference is Mid Layer 3 (the L4 GND plane of JLC06121H-3313); 4-layer: the Bottom layer
REF_L3 = 'Mid Layer 3' if os.environ.get('STACK', '4') == '6' else 'Bottom Layer'
l4 = [o for o in objs if REF_L3 in o.layers and o.net != 'GND' and o.kind in ('PAD', 'TRACK', 'ARC', 'REGION', 'FILL', 'VIA')]
tree = STRtree([o.geom for o in l4])


def seg(r):
    return LineString([(float(r['x1']), float(r['y1'])), (float(r['x2']), float(r['y2']))])


groups = defaultdict(list)
for p in sys.argv[1:]:
    for r in csv.DictReader(open(p)):
        groups[(os.path.basename(p), r['group'])].append(r)
res = []
for (plan, g), rows in groups.items():
    net = rows[0]['net']
    own = unary_union([G.via(v['net'], float(v['x1']), float(v['y1']), float(v['d']), float(v['h'])).geom.buffer(0.05)
                       for v in rows if v['kind'] == 'VIA'] or [box(0, 0, 0, 0)])
    area = 0.0
    for r in rows:
        if r['kind'] != 'TRACK' or r['layer'] != 'Mid Layer 2':
            continue
        band = seg(r).buffer(float(r['w']) / 2 + G2_BAND)
        for k in tree.query(band):
            o = l4[int(k)]
            if o.net == net and o.kind == 'VIA':
                continue          # same-net via on the route = the layer change itself
            hit = band.intersection(o.geom).difference(own)
            area += hit.area
    res.append((plan, g, net, net in ANALOG, area))
dirty = [t for t in res if t[4] > 1e-4]
out = ['connections checked %d | G2-clean %d | G2 hit %d (analog %d)' % (len(res), len(res) - len(dirty), len(dirty),
                                                                        sum(1 for t in dirty if t[3]))]
for plan, g, net, an, a in sorted(dirty, key=lambda t: -t[4]):
    out.append('  %-34s %-18s %s %.3f mm2' % (plan, g, 'ANALOG' if an else '      ', a))
EV = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'evidence')
open(os.path.join(EV, 'C2_G2_BY_CONNECTION.txt'), 'w').write('\n'.join(out) + '\n')
print('\n'.join(out))
