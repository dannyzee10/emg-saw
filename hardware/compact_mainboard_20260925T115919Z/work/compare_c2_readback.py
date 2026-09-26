"""Compare APPLY_C2_LOG.txt native readback (after save/close/reopen) with the audited plan (plan_C2.pkl)."""
import os, pickle, re
from c2lib import load_b, EV, HERE
S = pickle.load(open(os.path.join(HERE, 'work', 'plan_C2.pkl'), 'rb'))
out = S['out']
B = load_b()
rows = {}
import sys
for l in open(os.path.join(EV, sys.argv[1] if len(sys.argv) > 1 else 'APPLY_C2_LOG.txt'), encoding='utf-8', errors='replace'):
    f = l.strip().split('|')
    if f[0] == 'READBACK':
        kv = dict(x.split('=', 1) for x in f[3:])
        rows[f[1]] = (f[2], float(kv['X']), float(kv['Y']), float(kv['ROT']), kv['UID'])
    elif f[0] == 'READBACK_FREEPAD':
        kv = dict(x.split('=', 1) for x in f[3:])
        rows['FP:' + f[1]] = (f[2], float(kv['X']), float(kv['Y']), 0.0, '')
bad = []
for d, r in out.items():
    if d not in rows:
        bad.append('MISSING ' + d); continue
    lay, x, y, rot, uid = rows[d]
    side = 'Bottom' if lay.startswith('Bottom') else 'Top'
    if d.startswith('FP:'):
        q = r['pads'][0]
        if abs(x - q['x']) > 0.002 or abs(y - q['y']) > 0.002 or lay != 'Top Layer':
            bad.append('FREEPAD %s native %.4f,%.4f %s plan %.4f,%.4f' % (d, x, y, lay, q['x'], q['y']))
        continue
    dr = abs((rot - r['rot'] + 180) % 360 - 180)
    if side != r['side'] or abs(x - r['x']) > 0.002 or abs(y - r['y']) > 0.002 or dr > 0.01:
        bad.append('COMP %s native %s %.4f,%.4f rot %.2f | plan %s %.4f,%.4f rot %.2f' % (d, side, x, y, rot, r['side'], r['x'], r['y'], r['rot']))
    if uid != B[d]['src_uid']:
        bad.append('UID %s native %s expected %s' % (d, uid, B[d]['src_uid']))
extra = [d for d in rows if d not in out]
print('readback rows %d, plan items %d, extra %d, mismatches %d' % (len(rows), len(out), len(extra), len(bad)))
for b in bad[:40]:
    print('  ' + b)
nb = sum(1 for d, v in rows.items() if not d.startswith('FP:') and v[0].startswith('Bottom'))
print('native sides: top %d, bottom %d components' % (sum(1 for d in rows if not d.startswith('FP:')) - nb, nb))
