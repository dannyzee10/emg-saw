"""Small fixed-BF inward MCU92 escape scan; no router or CAD writes."""
import csv
import hashlib
import json
import math
import os
import time
from collections import Counter
from pathlib import Path

EV = Path(__file__).resolve().parent.parent / 'evidence'
GEOM = EV / 'GEOMETRY_C2_6L_BF.txt'
REPORT = EV / 'ASTRA_BF_MCU92_INWARD_SITES.json'
SEED = EV / 'ASTRA_BF_MCU92_INWARD_SEED_ADDS.csv'
os.environ['GEOM_FILE'] = str(GEOM)
os.environ['BOARD_BOX'] = '12,12,67.1,44'
import geom as G
from shapely.geometry import Point


def details(items):
    return [{'kind': q.kind, 'net': q.net, 'ref': q.comp, 'pin': q.name,
             'gap_mm': gap, 'required_mm': need, 'native_record': q.src}
            for q, gap, need in items]


def main():
    begin = time.monotonic()
    source_hash = hashlib.sha256(GEOM.read_bytes()).hexdigest()
    objects, _, keepouts = G.load()
    index = G.Index(objects)
    net = 'MCU_WIFI_UART_TX'
    pad = next(q for q in objects if q.kind == 'PAD' and q.comp == 'U_MCU1' and q.name == '92')
    assert pad.net == net
    start = tuple(map(float, pad.src[5:7]))
    allowed = G.BOARD.buffer(-G.EDGE)
    xs = sorted(set([round(55.7 + i * .05, 4) for i in range(15)] + [start[0]]))
    ys = [round(42.3 - i * .05, 4) for i in range(31)]
    sites = sorted(((x, y) for x in xs for y in ys), key=lambda p: math.dist(p, start))
    checked, legal, blockers = [], [], Counter()
    for point in sites:
        via = G.via(net, *point, .45, .20)
        copper = index.violations(via)
        # Build the candidate drill circle once; use the existing hole tree.
        hole = Point(*point).buffer(.10)
        holes = []
        if index.htree is not None:
            for item in index.htree.query(hole.buffer(.45)):
                other = index.holes[item]
                if other.geom.distance(hole) < G.hole_gap(other) - 1e-6:
                    holes.append(other.src)
        edge = allowed.contains(via.geom)
        keepout = any(k.intersects(via.geom) for k in keepouts)
        row = {'point': point, 'via_copper_blockers': details(copper),
               'hole_blockers': holes, 'edge_clear': edge, 'keepout_intersection': keepout}
        for other, _, _ in copper:
            blockers[(other.kind, other.net, other.comp, other.name)] += 1
        if not copper and not holes and edge and not keepout:
            paths = [('direct', [start, point])]
            dx = abs(point[0] - start[0])
            elbow = (start[0], round(point[1] + dx, 6))
            # Leave the inner end of the pad vertically before a 45-degree leg.
            if dx > 1e-9 and elbow[1] <= pad.geom.bounds[1] + 1e-9:
                paths.append(('vertical_then_45', [start, elbow, point]))
            row['stub_checks'] = []
            for width in (.20, .15):
                for name, path in paths:
                    segments = [G.track(net, 'Top Layer', [a, b], width)
                                for a, b in zip(path, path[1:]) if a != b]
                    hits = [hit for segment in segments for hit in index.violations(segment)]
                    passed = not hits and all(allowed.contains(s.geom) for s in segments)
                    passed = passed and not any(k.intersects(s.geom) for k in keepouts for s in segments)
                    check = {'path_type': name, 'points': path, 'width_mm': width,
                             'passed': passed, 'blockers': details(hits)}
                    row['stub_checks'].append(check)
                    if passed:
                        result = {'point': point, 'diameter_mm': .45, 'hole_mm': .20,
                                  'path_type': name, 'points': path, 'width_mm': width,
                                  'own_pad_overlap': via.geom.intersects(pad.geom)}
                        legal.append(result)
                        if len(legal) == 1:
                            print('FIRST_LEGAL ' + json.dumps(result), flush=True)
                        break
                if legal and legal[-1]['point'] == point:
                    break
        checked.append(row)
    report = {'geometry': str(GEOM), 'sha256': source_hash, 'source_pad': pad.src,
              'grid': {'x_mm': [55.7, 56.4], 'y_mm': [40.8, 42.3], 'step_mm': .05,
                       'extra_x_at_pad_center': start[0]},
              'checked_count': len(checked), 'legal_count': len(legal), 'legal': legal,
              'via_blocker_frequency': [{'object': key, 'count': count} for key, count in blockers.most_common()],
              'checked': checked, 'elapsed_seconds': time.monotonic() - begin,
              'limits': ['All fixed BF exported copper retained; no router or CAD operation.',
                         'Via on or near own-net pad requires filled/capped VIP process.',
                         'Only local via and Top stub checked; not a complete connection.',
                         'Poured-plane topology, return path, and native DRC remain unverified.']}
    REPORT.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    if legal:
        selected = legal[0]
        x, y = selected['point']
        common = dict(group='ASTRA_BF_MCU92_INWARD VIP', net=net,
                      conn='U_MCU1.92 inward fixed-BF escape', relax=0)
        rows = [dict(common, kind='VIA', layer='Multi Layer', x1=x, y1=y, d=.45, h=.20)]
        rows += [dict(common, kind='TRACK', layer='Top Layer', x1=a[0], y1=a[1],
                      x2=b[0], y2=b[1], w=selected['width_mm'])
                 for a, b in zip(selected['points'], selected['points'][1:]) if a != b]
        with SEED.open('w', newline='') as handle:
            writer = csv.DictWriter(handle, fieldnames=['kind', 'group', 'net', 'layer',
                'x1', 'y1', 'x2', 'y2', 'w', 'd', 'h', 'conn', 'relax'])
            writer.writeheader()
            writer.writerows(rows)
    print(json.dumps({'checked': len(checked), 'legal': len(legal),
                      'seconds': report['elapsed_seconds'], 'sha256': source_hash,
                      'report': str(REPORT), 'seed_written': bool(legal)}), flush=True)


if __name__ == '__main__':
    main()
