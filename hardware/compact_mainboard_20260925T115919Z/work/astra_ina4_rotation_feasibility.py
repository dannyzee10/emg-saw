"""Read-only local INA4 footprint rotation check; never edits CAD or deletes copper."""
import hashlib
import json
import math
import os
from pathlib import Path
import runpy
import sys

EV = Path(__file__).resolve().parent.parent / 'evidence'
GEOM = EV / 'GEOMETRY_C2_6L_BB.txt'
BODIES = EV / 'ASTRA_CL4_BODY_OBSTACLES_BB.txt'
os.environ['GEOM_FILE'] = str(GEOM)
os.environ['BODIES_FILE'] = str(BODIES)
os.environ['BOARD_BOX'] = '12,12,67.1,44'
import geom as G
from shapely import affinity
from shapely.strtree import STRtree


def main():
    old_argv = sys.argv
    try:
        sys.argv = ['place_part.py']
        state = runpy.run_path(str(Path(__file__).with_name('place_part.py')))
    finally:
        sys.argv = old_argv
    objects, comps, keepouts = state['objs'], state['comps'], state['keepouts']
    lp, body, side = state['local']('INA4')
    body_refs = [ref for ref, row in comps.items() if ref != 'INA4' and row[2] == side]
    bodies = [state['body_abs'](ref) for ref in body_refs]
    bodytree = STRtree(bodies)
    fixed_pads = [o for o in objects if o.kind == 'PAD' and o.comp != 'INA4' and side in o.layers]
    padtree = STRtree([p.geom for p in fixed_pads])
    comp_holes = [o for o in objects if o.kind == 'HOLE' and o.comp and o.comp != 'INA4']
    free = [o for o in objects if o.kind != 'PAD' and o.kind != 'HOLE' and o.kind != 'KEEPOUT'
            and side in o.layers and o.src is not None and 'INCOMP=True' not in o.src
            and 'INPOLY=True' not in o.src]
    copper = G.Index(free)

    def pose(x, y, rotation, details=False):
        wb = affinity.translate(affinity.rotate(body, rotation, origin=(0, 0)), x, y)
        blockers = []
        for i in bodytree.query(wb.buffer(.2, join_style=2)):
            i = int(i)
            distance = wb.distance(bodies[i])
            if distance < .2 - 1e-6:
                blockers.append({'kind': 'body', 'ref': body_refs[i], 'distance_mm': round(distance, 6),
                                 'overlap_mm2': round(wb.intersection(bodies[i]).area, 6), 'required_mm': .2})
        if blockers and not details:
            return False
        moved = []
        for name, net, geometry in lp:
            w = affinity.translate(affinity.rotate(geometry, rotation, origin=(0, 0)), x, y)
            p = G.Obj(w, net, 'PAD', {side}, 'INA4', name)
            moved.append(p)
            for i in padtree.query(w.buffer(.6)):
                q = fixed_pads[int(i)]
                if q.net == net and net not in ('', '-'):
                    continue
                required = G.required(p, q) + .02
                distance = w.distance(q.geom)
                if distance < required - 1e-6:
                    blockers.append({'kind': 'pad', 'pin': name, 'net': net, 'ref': q.comp,
                                     'other_pin': q.name, 'other_net': q.net,
                                     'distance_mm': round(distance, 6), 'required_mm': required})
            if not G.edge_ok(w):
                blockers.append({'kind': 'edge', 'pin': name})
            for k in keepouts:
                if k.distance(w) < G.base_clr(net) + .02 - 1e-6:
                    blockers.append({'kind': 'keepout', 'pin': name})
            for h in comp_holes:
                if h.geom.distance(w) < .3 - 1e-6:
                    blockers.append({'kind': 'component_hole', 'pin': name, 'ref': h.comp, 'other_pin': h.name})
        if not details:
            return not blockers
        route_conflicts = []
        for p in moved:
            for q in copper.near(p.geom, .6):
                if q.net == p.net:
                    continue
                required = G.required(p, q) + .02
                distance = p.geom.distance(q.geom)
                if distance < required - 1e-6:
                    route_conflicts.append({'pin': p.name, 'kind': q.kind, 'net': q.net,
                                            'distance_mm': round(distance, 6), 'required_mm': required, 'source': q.src})
        return {'x_mm': x, 'y_mm': y, 'rotation_deg': rotation, 'footprint_clear': not blockers,
                'body_bounds_mm': list(wb.bounds), 'fixed_footprint_blockers': blockers,
                'free_copper_conflicts': route_conflicts,
                'free_copper_conflict_nets': sorted({q['net'] for q in route_conflicts}),
                'pads': [{'pin': p.name, 'net': p.net, 'center_mm': [p.geom.centroid.x, p.geom.centroid.y],
                          'bounds_mm': list(p.geom.bounds)} for p in moved]}

    orientations = []
    for rotation in (90, 270):
        center = pose(51.1, 18.2, rotation, True)
        chosen = None
        trials = 0
        for step in range(31):
            radius = .05 * step
            for angle in range(0, 360, 15 if step else 360):
                x = round(51.1 + radius * math.cos(math.radians(angle)), 3)
                y = round(18.2 + radius * math.sin(math.radians(angle)), 3)
                trials += 1
                if pose(x, y, rotation):
                    chosen = pose(x, y, rotation, True)
                    break
            if chosen:
                break
        orientations.append({'rotation_deg': rotation, 'center': center, 'first_footprint_clear': chosen,
                             'tested_positions': trials, 'search_radius_mm': 1.5, 'radial_step_mm': .05,
                             'angular_step_deg': 15})
        print(json.dumps({'rotation': rotation, 'center_blockers': center['fixed_footprint_blockers'],
                          'first_clear': None if chosen is None else {k: chosen[k] for k in (
                              'x_mm', 'y_mm', 'rotation_deg', 'free_copper_conflict_nets')}, 'tested': trials}), flush=True)
    out = EV / 'ASTRA_INA4_ROTATION_FOOTPRINT_BB.json'
    report = {'geometry': str(GEOM), 'geometry_sha256': hashlib.sha256(GEOM.read_bytes()).hexdigest(),
              'body_geometry': str(BODIES), 'orientations': orientations,
              'limits': ['No CAD mutations or deletion files; this tests rotation on the same Top Layer only.',
                         'All other component bodies, pads and component holes remain fixed.',
                         'Footprint pass uses 0.2 mm body gap and modeled pad clearance plus 0.02 mm guard.',
                         'Existing free copper conflicts are reported separately, not removed; all moved INA4 pins need reconnection.',
                         'Via drill conflicts, track routing, silkscreen and polygon repour are not solved by this footprint-only test.',
                         'Bodies use previously validated matching native exports, conservative current COMP boxes otherwise.',
                         'Native placement and copper DRC must validate any accepted candidate.']}
    out.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(str(out))


if __name__ == '__main__':
    main()
