"""Tiny BF planning scan: translate only TP_GND_DIG, retaining every track."""
import hashlib
import json
import math
import os
import sys
import time
from pathlib import Path

EV = Path(__file__).resolve().parent.parent / 'evidence'
SOURCE = EV / 'GEOMETRY_C2_6L_BF.txt'
REPORT = EV / 'ASTRA_BF_TP_GND_DIG_MOVE_SCAN.json'
INCLUDE_CS = '--cs' in sys.argv
ADDS = EV / 'ASTRA_BF_CS_INSPECT_WIDE_BRIDGE_ADDS.csv'
DELS = EV / 'ASTRA_BF_FINAL_LOCAL_DELS.csv'
if INCLUDE_CS:
    REPORT = EV / 'ASTRA_BF_CS_TP_GND_DIG_MOVE_SCAN.json'
os.environ['GEOM_FILE'] = str(SOURCE)
os.environ['BOARD_BOX'] = '12,12,67.1,44'
import geom as G
from shapely import affinity
from shapely.geometry import Point, box


def describe(q):
    return {'kind': q.kind, 'net': q.net, 'ref': q.comp, 'pin': q.name, 'record': q.src}


def hits(rows):
    return [dict(describe(q), gap_mm=gap, required_mm=required) for q, gap, required in rows]


def main():
    begin = time.monotonic()
    objects, comps, keepouts = G.load()
    delta_counts = None
    if INCLUDE_CS:
        import astra_verify_routing_delta as D
        removed = set()
        deleted_via_sources = []
        for row in D.plan(DELS, False):
            matches = []
            for i, q in enumerate(objects):
                if i in removed or q.src is None:
                    continue
                s = q.src
                if q.kind == 'TRACK' and 'INCOMP=False' in s and 'INPOLY=False' in s:
                    primitive = D.primitive('TRACK', s[2], s[1], s[3:8], s)
                elif q.kind == 'VIA':
                    primitive = D.primitive('VIA', s[1], '', s[2:6], s)
                else:
                    continue
                if D.match_error(row, primitive, .00015) is not None:
                    matches.append(i)
            if len(matches) != 1:
                raise ValueError('Nonunique delete: ' + repr(row))
            removed.add(matches[0])
            if objects[matches[0]].kind == 'VIA':
                deleted_via_sources.append(objects[matches[0]].src)
        after = [q for i, q in enumerate(objects) if i not in removed
                 and not (q.kind == 'HOLE' and q.src in deleted_via_sources)]
        additions = D.plan(ADDS, True)
        for row in additions:
            v = row['values']
            if row['kind'] == 'TRACK':
                q = G.track(row['net'], row['layer'], [(v[0], v[1]), (v[2], v[3])], v[4])
                q.src = ['TRACK', row['layer'], row['net'], *map(str, v), 'CS_CANDIDATE']
                after.append(q)
            else:
                q = G.via(row['net'], *v)
                q.src = ['VIA', row['net'], *map(str, v), 'CS_CANDIDATE']
                after.append(q)
                after.append(G.Obj(Point(v[0], v[1]).buffer(v[3] / 2), row['net'], 'HOLE', set(), src=q.src))
        objects = after
        delta_counts = {'deleted_primitives': len(removed), 'added_primitives': len(additions)}
    tp = next(q for q in objects if q.kind == 'PAD' and q.name == 'TP_GND_DIG')
    mcu = next(q for q in objects if q.kind == 'PAD' and q.comp == 'U_MCU1' and q.name == '92')
    assert tp.comp == 'FREE' and tp.net == 'GND' and tp.layers == {'Top Layer'}
    index = G.Index([q for q in objects if q is not tp])
    allowed = G.BOARD.buffer(-G.EDGE)
    origin = tuple(map(float, tp.src[5:7]))
    start = tuple(map(float, mcu.src[5:7]))
    attached = [q for q in objects if q is not tp and q.kind != 'HOLE' and
                q.net == tp.net and 'Top Layer' in q.layers and q.geom.intersects(tp.geom)]
    top_bboxes = [(name, box(*map(float, row[6:10]))) for name, row in comps.items()
                  if row[2] == 'Top Layer']
    pad_envelopes = [(q, box(*map(float, q.src[7:11]))) for q in objects if q is not tp
                     and q.kind == 'PAD' and 'Top Layer' in q.layers]
    via_rows, legal_vias = [], []
    xs = sorted(set([round(55.5 + i * .1, 4) for i in range(10)] + [56.08]))
    ys = sorted(set([round(44.0 + i * .05, 4) for i in range(21)] + [44.275]))
    for point in sorted(((x, y) for x in xs for y in ys), key=lambda p: math.dist(p, (56.08, 44.3))):
        via = G.via(mcu.net, *point, .45, .20)
        blockers = index.violations(via)
        drill = Point(point).buffer(.1)
        hole_hits = []
        if index.htree is not None:
            for item in index.htree.query(drill.buffer(.45)):
                q = index.holes[item]
                if q.geom.distance(drill) < G.hole_gap(q) - 1e-6:
                    hole_hits.append(describe(q))
        row = {'point': point, 'copper_blockers': hits(blockers), 'hole_blockers': hole_hits,
               'edge_clear': allowed.contains(via.geom), 'keepout': any(k.intersects(via.geom) for k in keepouts)}
        row['stub_checks'] = []
        if not blockers and not hole_hits and row['edge_clear'] and not row['keepout']:
            paths = [('direct', [start, point])]
            dx = abs(point[0] - start[0])
            elbow = (start[0], round(point[1] - dx, 6))
            if dx > 1e-9 and elbow[1] >= mcu.geom.bounds[3] - 1e-9:
                paths.append(('vertical_then_45', [start, elbow, point]))
            for width in (.20, .15):
                found = False
                for name, path in paths:
                    segments = [G.track(mcu.net, 'Top Layer', [a, b], width) for a, b in zip(path, path[1:])]
                    stub_hits = [h for s in segments for h in index.violations(s)]
                    okay = not stub_hits and all(allowed.contains(s.geom) for s in segments)
                    okay = okay and not any(k.intersects(s.geom) for s in segments for k in keepouts)
                    row['stub_checks'].append({'width': width, 'path_type': name, 'path': path,
                                               'passed': okay, 'blockers': hits(stub_hits)})
                    if okay:
                        legal_vias.append({'point': point, 'width': width, 'path_type': name, 'path': path,
                                           'via': via, 'segments': segments})
                        found = True
                        break
                if found:
                    break
        via_rows.append(row)
    # Preserve the original true pad and exported bounding envelope dimensions.
    original_envelope = box(*map(float, tp.src[7:11]))
    trial_centers = [(56.671 + dx, 44.829) for dx in (.15, .20, .225, .25, .30, .40, .50, 1.0)]
    trial_centers += [(x, y) for x in (56.9, 57.0, 57.2, 57.4, 57.6, 57.8, 58.0, 58.2)
                      for y in (44.8, 44.9)]
    if INCLUDE_CS:
        trial_centers += [(x, y) for x in (56.671, 56.771, 56.821, 56.871, 56.921, 56.971, 57.071)
                          for y in (44.825, 44.875, 44.925, 44.95)]
    pad_rows, combinations = [], []
    for x, y in trial_centers:
        dx, dy = x - origin[0], y - origin[1]
        moved = G.Obj(affinity.translate(tp.geom, dx, dy), tp.net, tp.kind, tp.layers, tp.comp, tp.name)
        envelope = affinity.translate(original_envelope, dx, dy)
        copper_hits = index.violations(moved)
        overlapping_holes = [describe(q) for q in index.holes if q.geom.intersects(moved.geom)]
        envelope_holes = [describe(q) for q in index.holes if q.geom.intersects(envelope)]
        body_hits = [name for name, footprint in top_bboxes if footprint.intersects(envelope)]
        mask_envelope_hits = [describe(q) for q, other in pad_envelopes if other.intersects(envelope)]
        retained_contacts = [describe(q) for q in attached if q.geom.intersects(moved.geom)]
        keepout_hit = any(k.intersects(envelope) for k in keepouts)
        row = {'center': [round(x, 6), round(y, 6)], 'copper_blockers': hits(copper_hits),
               'copper_edge_clear': allowed.contains(moved.geom),
               'bounding_envelope_edge_clear': allowed.contains(envelope), 'keepout': keepout_hit,
               'copper_overlapping_drills': overlapping_holes, 'bounding_envelope_overlapping_drills': envelope_holes,
               'top_component_envelope_overlap': body_hits, 'other_pad_envelope_overlap': mask_envelope_hits,
               'retained_original_contact': retained_contacts,
               'minimum_drill_gap_to_copper_mm': min(q.geom.distance(moved.geom) for q in index.holes),
               'minimum_drill_gap_to_bounding_envelope_mm': min(q.geom.distance(envelope) for q in index.holes)}
        # Serviceability is conservatively screened with the exported envelope;
        # it is not claimed to be an explicit native mask or probe clearance.
        row['conservative_placement_pass'] = bool(not copper_hits and allowed.contains(envelope)
            and not keepout_hit and not envelope_holes and not body_hits and not mask_envelope_hits and retained_contacts)
        if row['conservative_placement_pass']:
            for candidate in legal_vias:
                conflicts = []
                for shape in [candidate['via']] + candidate['segments']:
                    gap = shape.geom.distance(moved.geom)
                    required = G.required(shape, moved)
                    if gap < required - 1e-6:
                        conflicts.append({'kind': shape.kind, 'gap': gap, 'required': required})
                if not conflicts:
                    combinations.append({'pad_center': row['center'],
                        'via_point': candidate['point'], 'diameter': .45, 'hole': .20,
                        'stub_width': candidate['width'], 'stub_path': candidate['path'],
                        'via_pad_copper_gap_mm': candidate['via'].geom.distance(moved.geom),
                        'stub_pad_copper_gap_mm': min(s.geom.distance(moved.geom) for s in candidate['segments']),
                        'pad_minimum_drill_gap_mm': row['minimum_drill_gap_to_copper_mm'],
                        'retained_contacts': retained_contacts})
        pad_rows.append(row)
    report = {'source': str(SOURCE), 'sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              'cs_candidate_included': INCLUDE_CS, 'delta_counts': delta_counts,
              'delta_inputs': [{'path': str(p), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
                               for p in (ADDS, DELS)] if INCLUDE_CS else [],
              'original_pad': tp.src, 'mcu_pad': mcu.src, 'attached_top_nonpolygon_copper': [describe(q) for q in attached],
              'all_fixed_objects_retained_except_original_pad': True, 'vias_checked': len(via_rows),
              'via_and_stub_clear_without_pad': len(legal_vias), 'combinations': combinations,
              'pad_placements': pad_rows, 'via_checks': via_rows,
              'seconds': time.monotonic() - begin,
              'limitations': ['No native or CAD operations; this is a local escape and pad-placement check.',
                'Native exported pad bounding rectangle is preserved and screened, but its exact mask expansion is not exported.',
                'Top component bounding rectangles screen access; no separate probe diameter or fixture specification is invented.',
                'Polygon fill connectivity, native DRC, and full TX route are not established by this check.']}
    REPORT.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'vias_checked': len(via_rows), 'via_and_stub_clear_without_pad': len(legal_vias),
                      'combinations': len(combinations), 'first_combinations': combinations[:4],
                      'pad_passes': [r['center'] for r in pad_rows if r['conservative_placement_pass']],
                      'seconds': report['seconds'], 'report': str(REPORT)}), flush=True)


if __name__ == '__main__':
    main()
