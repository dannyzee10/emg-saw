"""Brief fixed-BF via-site/stub scan for final CS and MCU92 escapes; no router."""
import hashlib
import json
import math
import os
from pathlib import Path

EV = Path(__file__).resolve().parent.parent / 'evidence'
GEOM = EV / 'GEOMETRY_C2_6L_BF.txt'
os.environ['GEOM_FILE'] = str(GEOM)
os.environ['BOARD_BOX'] = '12,12,67.1,44'
import geom as G
from shapely.geometry import Point


def main():
    objects, _, _ = G.load()
    index = G.Index(objects)
    results = {}
    targets = [('WIFI_SPI_CS', 'R_SPI_CS', '1', (58.48, 25.538)),
               ('MCU_WIFI_UART_TX', 'U_MCU1', '92', (56.08, 43.238))]
    for net, ref, pin_number, start in targets:
        pad = next(o for o in objects if o.kind == 'PAD' and o.comp == ref and o.name == pin_number)
        if net == 'WIFI_SPI_CS':
            sites = [start] + [(round(start[0]+i*.05, 4), round(start[1]+j*.05, 4))
                               for i in range(-6, 7) for j in range(-12, 7) if i or j]
        else:
            sites = [start] + [(round(start[0]+i*.05, 4), round(44.075+j*.05, 4))
                               for i in range(-5, 6) for j in range(16)]
        sites.sort(key=lambda p: math.dist(p, start))
        legal, blocked = [], []
        for point in sites:
            via = G.via(net, *point, .45, .2)
            violations = [{'kind': q.kind, 'net': q.net, 'ref': q.comp, 'pin': q.name,
                           'gap_mm': round(gap, 5), 'required_mm': need, 'native_record': q.src}
                          for q, gap, need in index.violations(via)]
            holes = [q for q in index.holes if q.geom.distance(Point(*point).buffer(.1)) < G.hole_gap(q)-1e-6]
            edge = G.edge_ok(via.geom)
            if violations or holes or not edge:
                blocked.append({'point': point, 'copper_blockers': violations,
                                'hole_blockers': [q.src for q in holes], 'edge_clear': edge})
                continue
            stub_checks = {}
            for width in (.20, .18, .15):
                if point == start:
                    stub_checks[str(width)] = True
                else:
                    stub = G.track(net, 'Top Layer', [start, point], width)
                    stub_checks[str(width)] = G.edge_ok(stub.geom) and not index.violations(stub)
            row = {'point': point, 'own_pad_overlap': via.geom.intersects(pad.geom),
                   'fully_inside_pad': pad.geom.covers(via.geom), 'direct_top_stub_clear': stub_checks}
            legal.append(row)
            if any(stub_checks.values()) and not any(any(r['direct_top_stub_clear'].values()) for r in legal[:-1]):
                print('FIRST_LEGAL ' + net + ' ' + json.dumps(row), flush=True)
        results[net] = {'source_pad': pad.src, 'checked': len(sites), 'legal': legal,
                        'blocked': blocked, 'via_and_stub_legal_count': sum(any(r['direct_top_stub_clear'].values()) for r in legal)}
        print('RESULT ' + net + ' ' + json.dumps({k: v for k, v in results[net].items() if k not in ('blocked', 'source_pad')}), flush=True)
    report = {'geometry': str(GEOM), 'sha256': hashlib.sha256(GEOM.read_bytes()).hexdigest(), 'results': results,
              'limits': ['All BF exported fixed copper retained; no router or CAD process.',
                         'Only via sites and one straight Top stub are checked, not a completed route.',
                         'Own-pad overlap requires filled/capped VIP process and explicit group tagging.',
                         'Native planes/repour and final DRC remain required.']}
    (EV / 'ASTRA_BF_FINAL_ESCAPE_SITES.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main()
