"""Check a fixed, hand-specified Vc_1 L5 polyline; no routing or CAD writes."""
import csv
import hashlib
import json
import math
import os
from pathlib import Path

EV = Path(__file__).resolve().parent.parent / 'evidence'
GEOM = EV / 'GEOMETRY_C2_6L_BC.txt'
os.environ['GEOM_FILE'] = str(GEOM)
os.environ['BOARD_BOX'] = '12,12,67.1,44'
import geom as G
from shapely.geometry import box


def main():
    objects, _, _ = G.load()
    for row in csv.DictReader((EV / 'BK13_ZONES_C2.csv').open(newline='')):
        G.ZONES.append((box(*(float(row[k]) for k in ('x0', 'y0', 'x1', 'y1'))),
                        set(row['nets'].split(';')), row['ref']))
    index = G.Index(objects)
    points = [(15.9, 11.2), (16.175, 10.925), (20.5, 10.925),
              (21.55, 11.975), (22.5, 11.975), (24.725, 14.2),
              (24.725, 18.775), (24.175, 19.325)]
    larger_gap = [(15.9, 11.2), (16.175, 10.925), (20.675, 10.925),
                  (21.675, 11.925), (22.55, 11.925), (24.725, 14.1),
                  (24.725, 18.775), (24.175, 19.325)]
    results = []
    for label, width, route in [('initial', .20, points), ('initial', .15, points),
                                 ('larger_keepout_gap', .20, larger_gap)]:
        segments = []
        for a, b in zip(route, route[1:]):
            candidate = G.track('Vc_1', 'Mid Layer 4', [a, b], width)
            nearby = []
            for other in index.near(candidate.geom, .65):
                if not other.layers & candidate.layers or (other.kind != 'KEEPOUT' and other.net == candidate.net):
                    continue
                distance, required = candidate.geom.distance(other.geom), G.required(candidate, other)
                nearby.append({'kind': other.kind, 'net': other.net, 'ref': other.comp, 'pin': other.name,
                               'distance_mm': round(distance, 7), 'required_mm': required,
                               'margin_mm': round(distance - required, 7), 'source': other.src,
                               'bounds_mm': list(other.geom.bounds)})
            nearby.sort(key=lambda r: r['margin_mm'])
            blockers = [r for r in nearby if r['margin_mm'] < -1e-6]
            segments.append({'from': a, 'to': b, 'edge_ok': G.edge_ok(candidate.geom),
                             'blockers': blockers, 'nearest': nearby[:2]})
        result = {'name': label, 'width_mm': width, 'length_mm': sum(math.dist(a, b) for a, b in zip(route, route[1:])),
                  'model_clear': all(not s['blockers'] and s['edge_ok'] for s in segments), 'segments': segments}
        results.append(result)
        print(json.dumps(result), flush=True)
    report = {'geometry': str(GEOM), 'geometry_sha256': hashlib.sha256(GEOM.read_bytes()).hexdigest(),
              'net': 'Vc_1', 'layer': 'Mid Layer 4', 'paths': results,
              'limits': ['Only fixed hand-specified segments checked, no routing search or CAD changes.',
                         'No existing copper, component, via, pad or keepout is removed or moved.',
                         'J_FPC1 escape-zone clearance is modeled; native DRC must confirm exact applicability.',
                         'Existing polygon copper is incompletely represented and needs native repour/DRC.',
                         'No routing-width-rule approval or actual PCB connectivity result is asserted.']}
    (EV / 'ASTRA_VC1_L5_MANUAL_PATH_BC.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
