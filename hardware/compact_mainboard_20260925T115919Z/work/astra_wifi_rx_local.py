"""Small fixed via-site/stub checks for WIFI_UART_RX; no router or CAD writes."""
import csv
import hashlib
import json
import math
import os
from pathlib import Path

EV = Path(__file__).resolve().parent.parent / 'evidence'
GEOM = EV / 'GEOMETRY_C2_6L_BD.txt'
os.environ['GEOM_FILE'] = str(GEOM)
os.environ['BOARD_BOX'] = '12,12,67.1,44'
import geom as G
from shapely.geometry import Point


def main():
    objects, _, keepouts = G.load()
    index = G.Index(objects)
    net = 'WIFI_UART_RX'
    pin = next(o for o in objects if o.kind == 'PAD' and o.comp == 'U_WIFI1' and o.name == '23')
    start, target = (42.126, 42.475), (43.525, 40.075)
    sites = [start] + [(round(start[0] + i*.05, 4), round(start[1] + j*.05, 4))
                       for i in range(-7, 13) for j in range(-12, 13) if i or j]
    sites.sort(key=lambda p: math.dist(p, start))
    blocked, legal, found = [], [], None
    def violations(o):
        return [{'kind': q.kind, 'net': q.net, 'ref': q.comp, 'pin': q.name,
                 'gap_mm': round(o.geom.distance(q.geom), 7), 'required_mm': req,
                 'source': q.src} for q, _, req in index.violations(o)]
    def clear_tracks(points, layer, width):
        return all(G.edge_ok(t) and not index.violations(o)
                   for a, b in zip(points, points[1:]) if a != b
                   for o in [G.track(net, layer, [a, b], width)] for t in [o.geom])
    for point in sites:
        via = G.via(net, *point, .45, .20)
        blockers = violations(via)
        if blockers:
            blocked.append({'point': point, 'blockers': blockers})
            continue
        hole_ok = index.hole_ok(Point(*point), .1)
        if not hole_ok or not G.edge_ok(via.geom) or any(k.intersects(via.geom) for k in keepouts):
            blocked.append({'point': point, 'hole_edge_or_keepout': True})
            continue
        top_clear = {w: clear_tracks([start, point], 'Top Layer', w) for w in (.2, .15)}
        row = {'point': point, 'inside_pin': pin.geom.covers(via.geom),
               'top_stub_clear': top_clear, 'overlaps_pin': pin.geom.intersects(via.geom)}
        legal.append(row)
        if not any(top_clear.values()):
            continue
        print('LEGAL_VIA', json.dumps(row), flush=True)
        dx, dy = target[0]-point[0], target[1]-point[1]
        diagonal = min(abs(dx), abs(dy))
        sx, sy = (1 if dx >= 0 else -1), (1 if dy >= 0 else -1)
        routes = [[point, target], [point, (target[0], point[1]), target],
                  [point, (point[0], target[1]), target],
                  [point, (point[0]+sx*diagonal, point[1]+sy*diagonal), target],
                  [point, (target[0]-sx*diagonal, target[1]-sy*diagonal), target]]
        for layer in ('Mid Layer 2', 'Mid Layer 4', 'Bottom Layer'):
            for width in (.2, .15):
                if not top_clear[width]:
                    continue
                for route in routes:
                    if clear_tracks(route, layer, width):
                        found = {'via': row, 'width_mm': width, 'layer': layer, 'top_stub': [start, point], 'route': route}
                        break
                if found: break
            if found: break
        if found: break
    direct = []
    for width in (.2, .15):
        o = G.track(net, 'Top Layer', [start, target], width)
        direct.append({'width_mm': width, 'blockers': violations(o)})
    report = {'geometry': str(GEOM), 'sha256': hashlib.sha256(GEOM.read_bytes()).hexdigest(),
              'sites_checked': len(blocked)+len(legal), 'legal_vias': legal,
              'pin_center': next((r for r in blocked if tuple(r['point']) == start), None),
              'blocked_sites': blocked, 'direct_top': direct, 'found': found,
              'limits': ['No CAD or routing search, only fixed via-site and straight/octilinear stub checks.',
                         'Polygon copper needs native repour and DRC.',
                         'All existing copper and components remain fixed.']}
    (EV / 'ASTRA_WIFI_RX_LOCAL_BD.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'sites_checked': report['sites_checked'], 'legal_via_count': len(legal),
                      'pin_center': report['pin_center'], 'direct_top': direct, 'found': found}), flush=True)
    if found:
        group = 'WIFI_RX_LOCAL VIP' if found['via']['overlaps_pin'] else 'WIFI_RX_LOCAL'
        x, y = found['via']['point']
        rows = [dict(kind='VIA', group=group, net=net, layer='', x1=x, y1=y, d=.45, h=.20)]
        for layer, points in [('Top Layer', found['top_stub']), (found['layer'], found['route'])]:
            for a, b in zip(points, points[1:]):
                if a != b:
                    rows.append(dict(kind='TRACK', group=group, net=net, layer=layer,
                                     x1=a[0], y1=a[1], x2=b[0], y2=b[1], w=found['width_mm']))
        with (EV / 'ASTRA_WIFI_RX_LOCAL_BD_ADDS.csv').open('w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['kind','group','net','layer','x1','y1','x2','y2','w','d','h'])
            writer.writeheader(); writer.writerows(rows)


if __name__ == '__main__':
    main()
