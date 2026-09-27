"""Small read-only 0.45/0.20 mm via-site scan along INA4 pin 3; no routing."""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--geometry', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--target-rdd4', action='store_true',
                        help='Scan the channel-4 RDD10/RDD12 target pads and connecting track instead')
    args = parser.parse_args()
    if args.output.suffix.lower() != '.json' or args.output.resolve() == args.geometry.resolve():
        parser.error('--output must be a separate JSON path')
    os.environ['GEOM_FILE'] = str(args.geometry.resolve())
    os.environ['BOARD_BOX'] = '12,12,67.1,44'
    import geom as G
    from shapely.geometry import Point, box
    from shapely.ops import unary_union
    objects, _, keepouts = G.load()
    zones = Path(G.HERE) / 'evidence/BK13_ZONES_C2.csv'
    with zones.open(newline='') as source:
        for zone in csv.DictReader(source):
            G.ZONES.append((box(*(float(zone[k]) for k in ('x0', 'y0', 'x1', 'y1'))),
                            set(zone['nets'].split(';')), zone['ref']))
    index = G.Index(objects)
    pads = [o for o in objects if o.kind == 'PAD']
    pin = next(o for o in pads if o.comp == 'INA4' and o.name == '3')
    target_pads = [o for o in pads if o.name == '2' and o.comp in ('RDD10', 'RDD12')] if args.target_rdd4 else [pin]
    target_copper = unary_union([p.geom for p in target_pads])
    sites = ([(57.412, 16.8), (57.412, 18.6)]
             + [(57.375, round(17.025 + .05 * i, 4)) for i in range(28)]) if args.target_rdd4 else [
                 (51.4251, round(15.30 + .05 * i, 4)) for i in range(23)]
    def item(other, distance, required):
        return {'kind': other.kind, 'net': other.net, 'component': other.comp,
                'name': other.name, 'layers': sorted(other.layers),
                'distance_mm': round(distance, 7), 'required_mm': required,
                'margin_mm': round(distance - required, 7), 'source': other.src}
    candidates = []
    for x, y in sites:
        via = G.via(pin.net, x, y, 0.45, 0.20)
        hole = Point(x, y).buffer(0.10, 32)
        copper = [item(o, via.geom.distance(o.geom), G.required(via, o))
                  for o in index.near(via.geom, .6)
                  if (o.net != pin.net or o.kind == 'KEEPOUT') and o.layers & via.layers]
        copper.sort(key=lambda o: o['margin_mm'])
        blockers = [item(o, via.geom.distance(o.geom), required)
                    for o, _, required in index.violations(via)]
        holes = [item(o, hole.distance(o.geom), max(.254, G.hole_gap(o))) for o in index.holes]
        holes.sort(key=lambda o: o['margin_mm'])
        hole_blockers = [o for o in holes if o['margin_mm'] < -1e-6]
        nearby_pads = [o for o in pads if o.geom.distance(via.geom) < .1 - 1e-6]
        vip_allowed = bool(nearby_pads) and all(o.net == pin.net for o in nearby_pads)
        edge_ok = G.edge_ok(via.geom)
        keepout_overlap = any(k.intersects(via.geom) for k in keepouts)
        candidates.append({'x_mm': x, 'y_mm': y, 'diameter_mm': .45, 'hole_mm': .20,
            'model_clear': not blockers and not hole_blockers and edge_ok and not keepout_overlap,
            'build_ops_same_net_vip_gate': vip_allowed, 'edge_ok': edge_ok,
            'keepout_overlap': keepout_overlap, 'pin_copper_overlap': via.geom.intersects(target_copper),
            'whole_via_inside_pin': target_copper.covers(via.geom),
            'hole_inside_pin': target_copper.covers(hole), 'blockers': blockers,
            'hole_blockers': hole_blockers, 'nearest_copper': copper[:3],
            'nearest_holes': holes[:2],
            'pads_within_vip_gate': [f'{o.comp}.{o.name}:{o.net}' for o in nearby_pads]})
    result = {'geometry': str(args.geometry.resolve()),
        'geometry_sha256': hashlib.sha256(args.geometry.read_bytes()).hexdigest(),
        'net': pin.net, 'pins': [p.src for p in target_pads], 'candidate_count': len(candidates),
        'clear_count': sum(c['model_clear'] for c in candidates), 'candidates': candidates,
        'limitations': ['No copper is ripped or moved; every modeled existing object stays fixed.',
                        'Poured polygon copper is not fully represented in geom.py; native repour/DRC is still needed.',
                        'This is only a via-site test, not a complete route or a manufacturing release.',
                        'Any via-in-pad requires filled/capped treatment matching the order.']}
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print('CLEAR', result['clear_count'], 'OF', len(candidates))
    for c in candidates:
        closest = c['nearest_copper'][0] if c['nearest_copper'] else {}
        print(json.dumps({'x': c['x_mm'], 'y': c['y_mm'], 'clear': c['model_clear'],
                          'hole_inside_pin': c['hole_inside_pin'],
                          'nearest': {k: closest[k] for k in ('kind', 'net', 'component', 'name', 'distance_mm', 'required_mm') if k in closest},
                          'blockers': [(b['kind'], b['component'], b['name'], b['net'], b['distance_mm']) for b in c['blockers']],
                          'hole_blockers': len(c['hole_blockers'])}))


if __name__ == '__main__':
    main()
