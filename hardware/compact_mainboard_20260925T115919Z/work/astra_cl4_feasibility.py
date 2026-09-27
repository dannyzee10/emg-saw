"""Offline CL_4 placement feasibility using place_part.py; never edits CAD."""
import contextlib
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import runpy
import sys

EV = Path(__file__).resolve().parent.parent / 'evidence'
GEOMETRY = EV / 'GEOMETRY_C2_6L_BB.txt'
DELETIONS = EV / 'ASTRA_CL4_HYPOTHETICAL_DELS_BB.csv'
BODIES = EV / 'ASTRA_CL4_BODY_OBSTACLES_BB.txt'


def records(path, kind):
    return [line.split('|') for line in path.read_text(encoding='utf-8-sig').splitlines()
            if line.startswith(kind + '|')]


def main():
    comps = {r[1]: r for r in records(GEOMETRY, 'COMP')}
    old_comps = {r[1]: r for r in records(EV / 'GEOMETRY_C2_PLACED.txt', 'COMP')}
    old_bodies = {r[1]: r for r in records(EV / 'BODIES_C2_PLACED.txt', 'BODYC')}
    body_lines, native_refs, fallback_refs = [], [], []
    for ref, comp in comps.items():
        old = old_bodies.get(ref)
        old_comp = old_comps.get(ref)
        same_pose = old and all(abs(float(old[i].split('=')[1]) - float(comp[i])) < .0001
                               for i in (3, 4, 5))
        same_envelope = old_comp and old_comp[2:] == comp[2:]
        if same_pose and same_envelope and '@' in old[-1]:
            body_lines.append('|'.join(old))
            native_refs.append(ref)
        else:
            # place_part otherwise falls back to pad envelopes. Explicitly use
            # current conservative COMP envelopes for absent/stale body data.
            body_lines.append(f'BODYC|{ref}|{comp[2]}|X={comp[3]}|Y={comp[4]}|ROT={comp[5]}|'
                              + 'BODYLAYERS=CONSERVATIVE_COMP@' + ','.join(comp[6:10]) + ';')
            fallback_refs.append(ref)
    BODIES.write_text('\n'.join(body_lines) + '\n', encoding='utf-8')

    nets = {'NetCL_4_1', 'INA_OUT_4'}
    rows, deleted_sources = [], set()
    for line in GEOMETRY.read_text(encoding='utf-8-sig').splitlines():
        r = line.split('|')
        if r[0] == 'TRACK' and r[2] in nets and 'INCOMP=False' in r and 'INPOLY=False' in r and 'KEEPOUT=False' in r:
            rows.append(dict(kind='TRACK', group='CL4_HYPOTHETICAL_RIP', net=r[2], layer=r[1],
                             x1=r[3], y1=r[4], x2=r[5], y2=r[6], w=r[7]))
            deleted_sources.add(tuple(r))
        elif r[0] == 'VIA' and r[1] in nets:
            rows.append(dict(kind='VIA', group='CL4_HYPOTHETICAL_RIP', net=r[1], layer='',
                             x1=r[2], y1=r[3], x2=r[2], y2=r[3], d=r[4], h=r[5]))
            deleted_sources.add(tuple(r))
    with DELETIONS.open('w', newline='') as target:
        writer = csv.DictWriter(target, fieldnames=['kind', 'group', 'net', 'layer', 'x1', 'y1', 'x2', 'y2', 'w', 'd', 'h'], restval='')
        writer.writeheader()
        writer.writerows(rows)

    os.environ['GEOM_FILE'] = str(GEOMETRY)
    os.environ['BOARD_BOX'] = '12,12,67.1,44'
    os.environ['BODIES_FILE'] = str(BODIES)
    specs = ['CL_4:47.0,16.05,180:2', 'CL_4:47.0,18.0,180:2', 'CL_4:47.0,16.05,90:2']
    attempts, chosen = [], None
    saved_argv = sys.argv
    try:
        for spec in specs:
            sys.argv = ['place_part.py', '--del', str(DELETIONS), spec]
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                state = runpy.run_path(str(Path(__file__).with_name('place_part.py')))
            attempts.append({'spec': spec, 'output': output.getvalue().strip()})
            if state['best']:
                x, y, rotation = state['best'][:3]
                x, y = round(x, 3), round(y, 3)
                result, reason = state['legal'](x, y, rotation)
                if result is None:
                    attempts[-1]['rounded_coordinates_failed'] = reason
                    continue
                chosen = {'x_mm': x, 'y_mm': y, 'rotation_deg': rotation, 'body': result[0], 'pads': result[1]}
                break
    finally:
        sys.argv = saved_argv

    report = {'geometry': str(GEOMETRY), 'geometry_sha256': hashlib.sha256(GEOMETRY.read_bytes()).hexdigest(),
              'hypothetical_deletion_csv': str(DELETIONS), 'deletion_counts': {
                  'tracks': sum(r['kind'] == 'TRACK' for r in rows),
                  'vias': sum(r['kind'] == 'VIA' for r in rows)},
              'body_source': str(EV / 'BODIES_C2_PLACED.txt'), 'native_body_refs': native_refs,
              'conservative_current_comp_fallback_refs': fallback_refs, 'attempts': attempts, 'chosen': None}
    if chosen:
        import geom as G
        from shapely.geometry import Point
        objects, _, keepouts = G.load()
        remaining = [o for o in objects if o.comp != 'CL_4' and (o.src is None or tuple(o.src) not in deleted_sources)]
        remaining.extend(chosen['pads'])
        index = G.Index(remaining)
        via = G.via('NetINA4_3', 51.4251, 15.65, .45, .20)
        blocked = [{'kind': o.kind, 'net': o.net, 'ref': o.comp, 'name': o.name,
                    'distance_mm': via.geom.distance(o.geom), 'required_mm': req, 'source': o.src}
                   for o, _, req in index.violations(via)]
        chosen['body_bounds_mm'] = list(chosen.pop('body').bounds)
        chosen['pad_bounds_mm'] = [{'name': p.name, 'net': p.net, 'bounds': list(p.geom.bounds)} for p in chosen.pop('pads')]
        chosen['via_site'] = {'x_mm': 51.4251, 'y_mm': 15.65, 'blockers': blocked,
                              'hole_ok': index.hole_ok(Point(51.4251, 15.65), .1),
                              'edge_ok': G.edge_ok(via.geom),
                              'keepout_overlap': any(k.intersects(via.geom) for k in keepouts)}
        report['chosen'] = chosen
    report['limits'] = ['Hypothetical only: no CAD/CSV operations were applied.',
                        'The two ripped nets still require complete reconnection.',
                        'Body exports are reused only for matching pose and COMP envelope; other parts use current conservative COMP boxes.',
                        'Native component clearance, repour and DRC are required after any actual edit.']
    out = EV / 'ASTRA_CL4_FEASIBILITY_BB.json'
    out.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'deletion_counts': report['deletion_counts'], 'attempts': attempts, 'chosen': chosen,
                      'native_body_count': len(native_refs), 'fallback_count': len(fallback_refs), 'evidence': str(out)}, indent=2))
    return 0 if chosen and not chosen['via_site']['blockers'] and chosen['via_site']['hole_ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
