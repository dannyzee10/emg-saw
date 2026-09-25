"""Summarise evidence/BODIES_EXPORT.txt: per-side max height, parts without 3D bodies, body layers used.
Heights are the native 3D body OverallHeight as stored in the PCB (model-reported), not measured parts."""
import os, re, sys
from collections import Counter, defaultdict
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fn = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'evidence', 'BODIES_EXPORT.txt')
recs = []
for l in open(fn, encoding='utf-8', errors='replace'):
    if l.startswith('BODYC|'):
        f = l.rstrip('\n').split('|')
        d = {'ref': f[1], 'side': 'Bottom' if f[2].startswith('Bottom') else 'Top'}
        for kv in f[3:]:
            if '=' in kv:
                k, v = kv.split('=', 1); d[k] = v
        d['BODIES'] = int(d['BODIES']); d['HMAX'] = float(d['HMAX'])
        d['layers'] = [b.split('@')[0] for b in d.get('BODYLAYERS', '').split(';') if b]
        recs.append(d)
print('components', len(recs))
for side in ('Top', 'Bottom'):
    rs = [r for r in recs if r['side'] == side]
    tall = sorted(rs, key=lambda r: -r['HMAX'])[:8]
    print(f"{side}: {len(rs)} parts, with bodies {sum(r['BODIES'] > 0 for r in rs)}, max model height {max([r['HMAX'] for r in rs] + [0]):.2f} mm;",
          'tallest:', ', '.join(f"{r['ref']} {r['HMAX']:.2f}" for r in tall))
    print('   body layers:', dict(Counter(l for r in rs for l in r['layers'])))
nob = [r['ref'] for r in recs if r['BODIES'] == 0]
print('without 3D body:', len(nob), ' '.join(nob))
