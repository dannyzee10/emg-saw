"""Bounded read-only contact and removal review of four new BG antenna tracks."""
import hashlib
import json
import math
import os
import time
from pathlib import Path
from collections import defaultdict

EV = Path(__file__).resolve().parent.parent / 'evidence'
BG = EV / 'GEOMETRY_C2_6L_BG.txt'
BFS = EV / 'GEOMETRY_C2_6L_BFS.txt'
os.environ['GEOM_FILE'] = str(BG)
os.environ['BOARD_BOX'] = '12,12,67.1,44'
import geom as G
from astra_check_final_opens_graph import partitions, preserved
from shapely.geometry import Point

TARGETS = [
    ('Top Layer', '3V3_DIG', (44.775, 41.625, 46.225, 41.625)),
    ('Mid Layer 2', 'WIFI_CHIP_EN', (45.975, 34.975, 48.6045, 34.975)),
    ('Mid Layer 2', 'WIFI_UART_TX', (48.6045, 41.925, 48.9019, 41.925)),
    ('Mid Layer 4', '3V3_DIG', (51.025, 33.675, 51.025, 37.075)),
]


def desc(q):
    return {'kind': q.kind, 'net': q.net, 'ref': q.comp, 'pin': q.name, 'record': q.src}


def main():
    begin = time.monotonic()
    objects, _, _ = G.load()
    index = G.Index(objects)
    native_before = set(BFS.read_text(encoding='utf-8-sig', errors='replace').splitlines())
    target_objects = []
    for layer, net, coords in TARGETS:
        matches = [q for q in objects if q.kind == 'TRACK' and q.net == net and layer in q.layers
                   and tuple(map(float, q.src[3:7])) == coords]
        assert len(matches) == 1, (layer, net, coords)
        target_objects.append(matches[0])
    records = []
    for q in target_objects:
        x1, y1, x2, y2, width = map(float, q.src[3:8])
        length = math.hypot(x2-x1, y2-y1)
        ux, uy = (x2-x1)/length, (y2-y1)/length
        contacts = []
        for other in index.near(q.geom, .00015):
            if other is q or other.net != q.net or not (q.layers & other.layers):
                continue
            gap = q.geom.distance(other.geom)
            if gap > .00015:
                continue
            intersection = q.geom.intersection(other.geom)
            bounds = intersection.bounds
            interval = None
            if bounds:
                bx1, by1, bx2, by2 = bounds
                projections = [(x-x1)*ux+(y-y1)*uy for x in (bx1,bx2) for y in (by1,by2)]
                interval = [min(projections), max(projections)]
            contacts.append(dict(desc(other), gap=gap, projected_contact_interval_mm=interval,
                                 covers_start=other.geom.buffer(.00015).covers(Point(x1,y1)),
                                 covers_end=other.geom.buffer(.00015).covers(Point(x2,y2))))
        old = [(i, other) for i, other in enumerate(objects) if other.net == q.net and other.kind not in ('HOLE','KEEPOUT')]
        removed = {i for i, other in old if other is q}
        new = [(i, other) for i, other in old if i not in removed]
        _, _, splits = preserved(old, new, removed)
        records.append({'target': q.src, 'retained_from_BFS': '|'.join(q.src) in native_before,
                        'length_mm': length, 'width_mm': width, 'contacts': contacts,
                        'whole_removal_preserves_retained_contacts': not splits,
                        'split_groups': [[desc(objects[i]) for i in group] for group in splits]})
    adjacent = []
    for q in target_objects[:3]:
        for other in index.near(q.geom, .00015):
            if other is q or other.net != q.net or not (q.layers & other.layers) or q.geom.distance(other.geom) > .00015:
                continue
            neighbors = [desc(n) for n in index.near(other.geom,.00015) if n is not other
                         and n.net == other.net and n.layers & other.layers and n.geom.distance(other.geom) <= .00015]
            adjacent.append({'neighbor':desc(other),'contacts':neighbors})
    combined = {}
    for net in sorted({q.net for q in target_objects}):
        old = [(i,q) for i,q in enumerate(objects) if q.net == net and q.kind not in ('HOLE','KEEPOUT')]
        removed = {i for i,q in old if any(q is target for target in target_objects)}
        new = [(i,q) for i,q in old if i not in removed]
        _, _, splits = preserved(old,new,removed)
        combined[net] = {'whole_removal_preserves_retained_connections': not splits,
                         'split_groups': [[desc(objects[i]) for i in group] for group in splits]}
    report = {'inputs': [{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in (BFS,BG)],
              'tracks': records, 'adjacent_contacts':adjacent, 'combined_removal': combined, 'seconds':time.monotonic()-begin,
              'limits':['Exported copper contact graphs only; polygon geometry and native DRC remain separate.',
                        'No CAD edits, router or native operations.']}
    (EV/'ASTRA_BG_ANTENNA_CONTACTS.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'tracks':[{k:v for k,v in row.items() if k!='split_groups'} for row in records],
                      'adjacent_contacts':adjacent,'seconds':report['seconds']}),flush=True)


if __name__ == '__main__':
    main()
