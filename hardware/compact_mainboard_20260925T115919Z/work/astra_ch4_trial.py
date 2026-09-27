"""Offline CL_4 relocation + explicit input via + complete affected-net repair.

Planning-only outputs. Does not open or modify Altium. The final combined
candidate must pass build_ops against MOVED_ONLY_GEOMETRY with full deletions,
then native placement, connectivity and DRC verification.
"""
import ast
import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ev = Path('../evidence')
tag = sys.argv[1]
if not tag.replace('_', '').isalnum():
    raise SystemExit('Simple tag required')
folder = ev / (tag + '_PLANNING_ONLY')
folder.mkdir(exist_ok=False)
base = ev / 'GEOMETRY_C2_6L_BB.txt'
base_drc = ev / 'DRC_C2_6L_BB.json'
report = json.loads((ev / 'ASTRA_CL4_FEASIBILITY_BB.json').read_text())
if hashlib.sha256(base.read_bytes()).hexdigest() != report['geometry_sha256']:
    raise SystemExit('Placement model hash mismatch')
chosen = report['chosen']
if (chosen['x_mm'], chosen['y_mm'], chosen['rotation_deg']) != (48.2, 16.05, 180):
    raise SystemExit('Unexpected placement')
if chosen['via_site']['blockers'] or not chosen['via_site']['hole_ok']:
    raise SystemExit('Via site check failed')
with (ev / 'ASTRA_CL4_HYPOTHETICAL_DELS_BB.csv').open(newline='') as f:
    initial_dels = list(csv.DictReader(f))

def key(r):
    if r[0] == 'TRACK':
        return ('T', r[2], r[1], frozenset(((round(float(r[3]), 3), round(float(r[4]), 3)),
                                           (round(float(r[5]), 3), round(float(r[6]), 3)))))
    if r[0] == 'VIA':
        return ('V', r[1], round(float(r[2]), 3), round(float(r[3]), 3))
    return None

keys = set()
for r in initial_dels:
    f = (['TRACK', r['layer'], r['net'], r['x1'], r['y1'], r['x2'], r['y2']]
         if r['kind'] == 'TRACK' else ['VIA', r['net'], r['x1'], r['y1']])
    keys.add(key(f))
dx = -3.1
moved, prepared, pads = [], [], []
removed = 0
for line in base.read_text(encoding='utf-8').splitlines():
    f = line.split('|')
    if f[0] == 'PAD' and f[1] == 'CL_4':
        for i in (5, 7, 9):
            f[i] = f'{float(f[i]) + dx:.4f}'
        line = '|'.join(f)
    elif f[0] == 'COMP' and f[1] == 'CL_4':
        for i in (3, 6, 8):
            f[i] = f'{float(f[i]) + dx:.4f}'
        line = '|'.join(f)
    if f[0] == 'PAD':
        pads.append(f)
    moved.append(line)
    if key(f) in keys:
        removed += 1
    else:
        prepared.append(line)
if removed != len(initial_dels):
    raise SystemExit('Deletion count mismatch')
seed = dict(kind='VIA', group='CH4_INPUT_SEED VIP', net='NetINA4_3', layer='',
            x1='51.4251', y1='15.6500', x2='', y2='', w='', d='0.45', h='0.20',
            conn='manual checked local input escape', relax='0')
seed_line = 'VIA|NetINA4_3|51.4251|15.6500|0.4500|0.2000'
target_scan = json.loads((ev / 'ASTRA_CH4_TARGET_VIA_SCAN_LOCAL2.json').read_text())
target_point = next(c for c in target_scan['candidates']
                    if c['x_mm'] == 57.375 and c['y_mm'] == 17.125)
if not target_point['model_clear'] or not target_point['build_ops_same_net_vip_gate']:
    raise SystemExit('Target-side via check failed')
target_seed = dict(seed, group='CH4_RDD_SEED VIP', x1='57.3750', y1='17.1250')
seed_rows = [seed, target_seed]
header = 'PLANNING_ONLY: hypothetical CL_4 relocation; not a native export\n'
move_file = folder / 'MOVED_ONLY_GEOMETRY.txt'
move_file.write_text(header + '\n'.join(moved) + '\n', encoding='utf-8')
prepared_file = folder / 'PREPARED_GEOMETRY_WITH_SEED.txt'
# Keep terminal marker at end only for the native-derived parser format. Header
# and directory explicitly identify this as a planning projection, not evidence.
prepared.insert(len(prepared) - 1, seed_line)
prepared.insert(len(prepared) - 1, 'VIA|NetINA4_3|57.3750|17.1250|0.4500|0.2000')
prepared_file.write_text(header + '\n'.join(prepared) + '\n', encoding='utf-8')
data = json.loads(base_drc.read_text())
data['planning_only'] = True
data['native_base_drc'] = str(base_drc.resolve())
layers = {'Top Layer': 'L1 TOP', 'Bottom Layer': 'L6 BOTTOM'}
def endpoint(p):
    return f'Pad {p[1]}-{p[2]}({float(p[5]):.4f}mm,{float(p[6]):.4f}mm) on {layers[p[4]]}'
for net in ('NetCL_4_1', 'INA_OUT_4'):
    ps = [p for p in pads if p[3] == net]
    expected = ({('CL_4', '1'), ('RGN_4', '1')} if net == 'NetCL_4_1'
                else {('CL_4', '2'), ('Rservo_4', '2'), ('RH_4', '1'), ('INA4', '8')})
    if {(p[1], p[2]) for p in ps} != expected or len(ps) != len(expected):
        raise SystemExit('Unexpected terminal set for ' + net)
    for p in ps[1:]:
        data['details'].append(f'Un-Routed Net Constraint: Net {net} Between {endpoint(ps[0])} And {endpoint(p)}')
drc_file = folder / 'PLANNING_CONNECTION_REQUESTS.json'
drc_file.write_text(json.dumps(data, indent=2), encoding='utf-8')
tree = ast.parse(Path('run_repair.py').read_text())
settings = {n.targets[0].id: ast.literal_eval(n.value) for n in tree.body
            if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name)
            and n.targets[0].id in ('ENV', 'PLANS')}
env = dict(os.environ, **settings['ENV'], GEOM_FILE=str(prepared_file),
           PLANE='1', DEBUG='1', PASSES='2', MAXV='8', REORDER='4', GUIDED='1.0',
           CASCADE='12', ONLY_NETS='NetINA4_3,NetCL_4_1,INA_OUT_4',
           ALLOW_BOTTOM='NetINA4_3,NetINA4_2', FIRST_NETS='NetINA4_3')
for arg in sys.argv[2:]:
    k, v = arg.split('=', 1)
    env[k] = v
adds, dels = ev / (tag + '_ROUTE_ADDS.csv'), ev / (tag + '_ROUTE_DELS.csv')
cmd = [sys.executable, '-u', 'repair.py', str(drc_file), str(adds), str(dels)]
cmd += [str(ev / (p + '.csv')) for p in settings['PLANS']]
manifest = {'base_sha256': report['geometry_sha256'], 'native_base': str(base.resolve()),
            'allowed_move': {'component': 'CL_4', 'delta_x_mm': dx, 'delta_y_mm': 0},
            'initial_deletions': len(initial_dels), 'explicit_seeds': seed_rows,
            'router_command': cmd, 'status': 'planning only; no CAD mutation'}
(folder / 'MANIFEST.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
print('PLANNING ONLY: CL_4 moves left3.1mm;18tracks/3vias removed;2checked escape vias added', flush=True)
rc = subprocess.run(cmd, env=env).returncode
if rc:
    raise SystemExit(rc)
if not adds.exists() or not dels.exists():
    raise SystemExit('No route output; do not apply relocation')
fields = ['kind', 'group', 'net', 'layer', 'x1', 'y1', 'x2', 'y2', 'w', 'd', 'h', 'conn', 'relax']
for kind, initial, source in [('ADDS', seed_rows, adds), ('DELS', initial_dels, dels)]:
    with source.open(newline='') as f:
        rows = list(csv.DictReader(f))
    with (ev / (tag + '_COMBINED_' + kind + '.csv')).open('x', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore', restval='')
        w.writeheader(); w.writerows(initial + rows)
print('Combined candidate emitted; verify ALL5 connection requests succeeded before native write', flush=True)
