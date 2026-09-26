"""C2 fix pass: ops from the SAVED NATIVE state (GEOMETRY_C2_PLACED.txt) to the re-audited plan (plan_C2.pkl).
  COMP  only for components whose side / origin / rotation differ (current side taken from the native state)
  PMOVE only for free test pads that moved
  VMOVE the charger (UP1) thermal vias from where they natively are to where they belong (the first write moved them twice:
        FlipComponent dragged them with UP1, then the explicit via move applied again)
  RULE  all 27 region exceptions recomputed from B for the new anchor positions (absolute, idempotent)"""
import os, pickle, re
from c2lib import load_b, to_local, to_world, EV, HERE

plan = pickle.load(open(os.path.join(HERE, 'work', 'plan_C2.pkl'), 'rb'))['out']
B = load_b()
cgeo = [l.rstrip('\n').split('|') for l in open(os.path.join(EV, 'GEOMETRY_C2_PLACED.txt'), encoding='utf-8', errors='replace')]
bgeo = [l.rstrip('\n').split('|') for l in open(os.path.join(EV, 'GEOMETRY_B_TRIAL.txt'), encoding='utf-8', errors='replace')]
ops = []; moved = []
nat = {f[1]: ('Bottom' if f[2].startswith('Bottom') else 'Top', float(f[3]), float(f[4]), float(f[5])) for f in cgeo if f[0] == 'COMP'}
for d in sorted(plan):
    if d.startswith('FP:'):
        continue
    r = plan[d]; side, x, y, rot = nat[d]
    drot = abs((rot - r['rot'] + 180) % 360 - 180)
    if side != r['side'] or abs(x - r['x']) > 0.001 or abs(y - r['y']) > 0.001 or drot > 0.01:
        ops.append('COMP|%s|%s|%s|%d|%.4f|%.4f|1|%.3f' % (d, B[d]['src_uid'], side, 1 if side != r['side'] else 0, r['x'], r['y'], r['rot'] % 360))
        moved.append(d)
fp_nat = {f[2]: (float(f[5]), float(f[6])) for f in cgeo if f[0] == 'PAD' and f[1] == 'FREE'}
for d in sorted(plan):
    if d.startswith('FP:'):
        q = plan[d]['pads'][0]; nx, ny = fp_nat[d[3:]]
        if abs(nx - q['x']) > 0.001 or abs(ny - q['y']) > 0.001:
            ops.append('PMOVE|%s|%.4f|%.4f|%.4f|%.4f' % (d[3:], nx, ny, q['x'] - nx, q['y'] - ny)); moved.append(d)
# UP1 thermal vias: expected positions from B's EP vias through the planned UP1 transform
exp = []
for f in bgeo:
    if f[0] == 'VIA':
        vx, vy = float(f[2]), float(f[3])
        if any(q['net'] == f[1] and q['bx0'] <= vx <= q['bx1'] and q['by0'] <= vy <= q['by1'] and (q['bx1'] - q['bx0']) * (q['by1'] - q['by0']) > 1
               for q in B['UP1']['pads']):
            r = plan['UP1']
            exp.append(to_world((r['x'], r['y']), r['rot'], r['side'], *to_local(B['UP1'], vx, vy)))
nvias = [(float(f[2]), float(f[3])) for f in cgeo if f[0] == 'VIA']
wifi_ok = []
for f in bgeo:
    if f[0] == 'VIA':
        vx, vy = float(f[2]), float(f[3])
        if any(q['net'] == f[1] and q['bx0'] <= vx <= q['bx1'] and q['by0'] <= vy <= q['by1'] and (q['bx1'] - q['bx0']) * (q['by1'] - q['by0']) > 1
               for q in B['U_WIFI1']['pads']):
            r = plan['U_WIFI1']
            wifi_ok.append(to_world((r['x'], r['y']), r['rot'], r['side'], *to_local(B['U_WIFI1'], vx, vy)))
stray = [v for v in nvias if min(abs(v[0] - w[0]) + abs(v[1] - w[1]) for w in wifi_ok + exp) > 0.002]
todo = [e for e in exp if min(abs(v[0] - e[0]) + abs(v[1] - e[1]) for v in nvias) > 0.002]
assert len(stray) == len(todo), (stray, todo)
for (sx, sy), (ex, ey) in zip(sorted(stray), sorted(todo)):
    ops.append('VMOVE|GND|%.4f|%.4f|%.4f|%.4f' % (sx, sy, ex - sx, ey - sy))
# rule regions (same algorithm as gen_C2_ops.py)
MIL = 0.0254
for l in open(os.path.join(HERE, 'work', 'B_OPS.txt')):
    if not l.startswith('RULE|'):
        continue
    _, name, no, expr = l.rstrip('\n').split('|', 3)
    m = re.search(r'InRegionAbsolute\(([-0-9.]+),([-0-9.]+),([-0-9.]+),([-0-9.]+)\)', expr)
    x0, y0, x1, y1 = (float(v) * MIL for v in m.groups())
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    comp = re.search(r"InComponent\('([^']+)'\)", expr); nets = re.findall(r"InNet\('([^']+)'\)", expr)
    if 'Keep-Out' in expr:
        anchor = 'U_WIFI1'
    elif comp:
        anchor = comp.group(1)
    else:
        anchor = min(((abs((q['bx0'] + q['bx1']) / 2 - cx) + abs((q['by0'] + q['by1']) / 2 - cy), d) for d, p in B.items()
                      if not d.startswith('FP:') for q in p['pads'] if not nets or q['net'] in nets))[1]
    p, r = B[anchor], plan[anchor]
    cs = [to_world((r['x'], r['y']), r['rot'], r['side'], *to_local(p, a, b)) for a, b in ((x0, y0), (x1, y1))]
    nx0, nx1 = sorted((cs[0][0], cs[1][0])); ny0, ny1 = sorted((cs[0][1], cs[1][1]))
    ops.append('RULE|%s|%s|%s' % (name, no, expr[:m.start()] + 'InRegionAbsolute(%.6f,%.6f,%.6f,%.6f)' % (nx0 / MIL, ny0 / MIL, nx1 / MIL, ny1 / MIL) + expr[m.end():]))
open(os.path.join(HERE, 'work', 'C2_FIX_OPS.txt'), 'w').write('\n'.join(ops) + '\n')
print('fix ops: %d components, %d free pads, %d vias, %d rules' % (sum(o.startswith('COMP') for o in ops), sum(o.startswith('PMOVE') for o in ops),
      sum(o.startswith('VMOVE') for o in ops), sum(o.startswith('RULE') for o in ops)))
print('moved:', ' '.join(moved))
