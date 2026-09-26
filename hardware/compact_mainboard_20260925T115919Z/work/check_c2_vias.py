"""Where should each kept thermal via be (owner part transform), and where is it natively?"""
import os, pickle
from c2lib import load_b, to_local, to_world, EV, HERE
plan = pickle.load(open(os.path.join(HERE, 'work', 'plan_C2.pkl'), 'rb'))['out']
B = load_b()
bgeo = [l.rstrip('\n').split('|') for l in open(os.path.join(EV, 'GEOMETRY_B_TRIAL.txt'), encoding='utf-8', errors='replace')]
cgeo = [l.rstrip('\n').split('|') for l in open(os.path.join(EV, 'GEOMETRY_C2_PLACED.txt'), encoding='utf-8', errors='replace')]
native = [(float(f[2]), float(f[3])) for f in cgeo if f[0] == 'VIA']
exp = []
for f in bgeo:
    if f[0] != 'VIA':
        continue
    vx, vy = float(f[2]), float(f[3])
    for d in ('UP1', 'U_WIFI1'):
        p = B[d]
        if any(q['net'] == f[1] and q['bx0'] <= vx <= q['bx1'] and q['by0'] <= vy <= q['by1'] and (q['bx1'] - q['bx0']) * (q['by1'] - q['by0']) > 1 for q in p['pads']):
            r = plan[d]
            exp.append((d, to_world((r['x'], r['y']), r['rot'], r['side'], *to_local(p, vx, vy))))
            break
for d, (x, y) in exp:
    nx, ny = min(native, key=lambda n: abs(n[0] - x) + abs(n[1] - y))
    print('%-8s expected (%.3f,%.3f)  nearest native (%.3f,%.3f)  delta (%.3f,%.3f)' % (d, x, y, nx, ny, nx - x, ny - y))
