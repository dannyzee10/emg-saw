"""Offline routing with explicit, separately checked fixed seed copper.

No CAD writes. The derived geometry is labeled planning-only; DRC endpoints
always come from the real saved base state. Check combined output against the
REAL base geometry with build_ops before any native operation.
usage: python astra_route_seed.py STATE TAG SEED.csv [KEY=VALUE ...]
"""
import ast
import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

state, tag, seed = sys.argv[1:4]
if not all(c.isalnum() or c == '_' for c in tag + state):
    raise SystemExit('State/tag must be simple names')
ev = Path('../evidence')
out = ev / (tag + '_PLANNING_ONLY')
out.mkdir(exist_ok=False)
base = ev / f'GEOMETRY_C2_6L_{state}.txt'
drc = ev / f'DRC_C2_6L_{state}.json'
seed = Path(seed)
tree = ast.parse(Path('run_repair.py').read_text())
settings = {n.targets[0].id: ast.literal_eval(n.value)
            for n in tree.body if isinstance(n, ast.Assign)
            and isinstance(n.targets[0], ast.Name)
            and n.targets[0].id in ('PLANS', 'ENV')}
with seed.open(newline='') as f:
    seed_rows = list(csv.DictReader(f))
lines = []
for r in seed_rows:
    if r['kind'] == 'VIA':
        lines.append('|'.join(['VIA', r['net'], r['x1'], r['y1'], r['d'], r['h']]))
    elif r['kind'] == 'TRACK':
        lines.append('|'.join(['TRACK', r['layer'], r['net'], r['x1'], r['y1'],
                              r['x2'], r['y2'], r['w'], 'INCOMP=False',
                              'INPOLY=False', 'KEEPOUT=False']))
    else:
        raise SystemExit('Only seed vias/tracks supported')
derived = out / 'PLANNING_GEOMETRY_NOT_NATIVE.txt'
derived.write_text('PLANNING_ONLY: base native geometry plus proposed fixed seed copper\n'
                   + base.read_text(encoding='utf-8') + '\n' + '\n'.join(lines) + '\n', encoding='utf-8')
manifest = {'native_base': str(base.resolve()), 'native_drc': str(drc.resolve()),
            'seed': str(seed.resolve()), 'seed_rows': len(seed_rows),
            'hashes': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in (base, drc, seed)},
            'warning': 'Derived geometry is not a native export and proves no native connectivity.'}
env = dict(os.environ, **settings['ENV'])
for arg in sys.argv[4:]:
    k, v = arg.split('=', 1)
    env[k] = v
extra = [p for p in env.get('EXTRA_PLANS', '').split(',') if p]
if any(p in ('.', '..') or any(c in p for c in '/\\:') or Path(p).name != p for p in extra):
    raise SystemExit('EXTRA_PLANS entries must be simple basenames without paths')
routed_plans = settings['PLANS'] + extra
manifest['routed_plans'] = routed_plans
(out / 'MANIFEST.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
env['GEOM_FILE'] = str(derived)
adds, dels = ev / (tag + '_ADDS.csv'), ev / (tag + '_DELS.csv')
for p in (adds, dels):
    if p.exists():
        raise SystemExit('Refusing to overwrite ' + str(p))
cmd = [sys.executable, '-u', 'repair.py', str(drc), str(adds), str(dels)]
cmd += [str(ev / (p + '.csv')) for p in routed_plans]
print('PLANNING ONLY: explicit seed copper; native board unchanged', flush=True)
result = subprocess.run(cmd, env=env)
if result.returncode:
    raise SystemExit(result.returncode)
if not adds.exists():
    raise SystemExit('No accepted routing output; no combined plan emitted')
with adds.open(newline='') as f:
    reader = csv.DictReader(f)
    fields, rows = reader.fieldnames, list(reader)
if not rows:
    raise SystemExit('No accepted route; seed must not be applied alone')
combined = ev / (tag + '_WITH_SEED_ADDS.csv')
with combined.open('x', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fields, restval='', extrasaction='ignore')
    writer.writeheader()
    writer.writerows(seed_rows + rows)
print(f'Candidate only: {combined}; exact check against native base required', flush=True)
