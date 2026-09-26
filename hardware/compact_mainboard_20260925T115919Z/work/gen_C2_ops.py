"""Generate work/C2_OPS.txt for apply_C2.pas from the audited plan (plan_C2.pkl) and the native state of the C2 copy
(= candidate B's saved geometry + the verified service-footprint swap, SVC_SWAP_C2_LOG.txt).

Op formats (fields separated by |):
  COMP|ref|srcUID|curSide|flip(0/1)|x|y|setrot(1)|rot          final origin/rotation/side (FlipComponent first when flip=1)
  PMOVE|name|x|y|dx|dy                                         native free test pad, MoveByXY
  TDEL|net|layer|x1|y1|x2|y2[|N=k]                             free copper track removed (routing is redone for C2)
  VMOVE|net|x|y|dx|dy[|N=k] / VDEL|net|x|y[|N=k]               exposed-pad thermal vias travel with their part; others removed
  MMOVE|layer|x1|y1|x2|y2|dx|dy / MDEL|layer|x1|y1|x2|y2       BK13 flex/pin-1 markers move with their socket; assembly leaders removed
  KMOVE|x0|y0|x1|y1|dx|dy                                      ST67 antenna keep-out moves with the module
  RULE|name|scopeNo|expression                                 region-scoped exceptions follow their anchor part's exact transform
  RULE_PASTE|name|expression|expansion_mm                      new paste-mask rule (no paste on the flat service pads)
  OUTLINE|W|H  and  POLY|name|x0|y0|x1|y1"""
import os, pickle, re, sys
from collections import Counter, defaultdict
from c2lib import load_b, to_local, to_world, EV, HERE

S = pickle.load(open(os.path.join(HERE, 'work', 'plan_C2.pkl'), 'rb'))
out = S['out']; X0, Y0, X1, Y1 = S['OUTLINE']
B = load_b()
geo = [l.rstrip('\n').split('|') for l in open(os.path.join(EV, 'GEOMETRY_B_TRIAL.txt'), encoding='utf-8', errors='replace')]
SERVICE = {'J_SWD', 'JP_WIFI_BOOT', 'TP_GND', 'TP_MCU_BOOT0', 'TP_WIFI_BOOT', 'TP_WIFI_CHIP_EN', 'TP_WIFI_UART_RX', 'TP_WIFI_UART_TX'}
ops = []
f4 = lambda v: '%.4f' % v

# ---------------------------------------------------------------- components
for d in sorted(out):
    if d.startswith('FP:'):
        continue
    r, b = out[d], B[d]
    cur_side = b['side']                       # service parts were rebuilt Top, rot 0 at the same origin
    flip = 1 if r['side'] != cur_side else 0
    ops.append('COMP|%s|%s|%s|%d|%s|%s|1|%s' % (d, b['src_uid'], cur_side, flip, f4(r['x']), f4(r['y']), '%.3f' % (r['rot'] % 360)))

# ---------------------------------------------------------------- free test pads
for d in sorted(out):
    if d.startswith('FP:'):
        r, b = out[d], B[d]
        q = b['pads'][0]
        ops.append('PMOVE|%s|%s|%s|%s|%s' % (d[3:], f4(q['x']), f4(q['y']), f4(r['x'] - b['x']), f4(r['y'] - b['y'])))

# ---------------------------------------------------------------- free copper tracks: removed (C2 is re-routed)
COPPER = ('Top Layer', 'Mid Layer 1', 'Mid Layer 2', 'Bottom Layer')
tk = Counter(); rep_of = {}
for f in geo:
    if f[0] == 'TRACK' and f[1] in COPPER and 'INCOMP=False' in f:
        # near-duplicates (within the native finder's 0.002 mm tolerance, either direction) resolve as one op with N=k
        e1, e2 = sorted([(round(float(f[3]), 3), round(float(f[4]), 3)), (round(float(f[5]), 3), round(float(f[6]), 3))])
        key = (f[2], f[1], e1, e2)
        tk[key] += 1
        rep_of.setdefault(key, (f[3], f[4], f[5], f[6]))
for key, n in sorted(tk.items()):
    net, lay = key[0], key[1]
    a, b_, c, e = rep_of[key]
    ops.append('TDEL|%s|%s|%s|%s|%s|%s' % (net, lay, a, b_, c, e) + ('|N=%d' % n if n > 1 else ''))

# ---------------------------------------------------------------- vias: exposed-pad thermal vias move with their part
def owner_pad(vx, vy, net):
    for d, p in B.items():
        if d.startswith('FP:') or d in SERVICE:
            continue
        for q in p['pads']:
            if q['net'] == net and q['bx0'] - 1e-6 <= vx <= q['bx1'] + 1e-6 and q['by0'] - 1e-6 <= vy <= q['by1'] + 1e-6 and \
                    (q['bx1'] - q['bx0']) * (q['by1'] - q['by0']) > 1.0:
                return d
    return None


vk = Counter(); vmove = {}
for f in geo:
    if f[0] == 'VIA':
        key = (f[1], f[2], f[3]); vk[key] += 1
        own = owner_pad(float(f[2]), float(f[3]), f[1])
        if own:
            p, r = B[own], out[own]
            nx, ny = to_world((r['x'], r['y']), r['rot'], r['side'], *to_local(p, float(f[2]), float(f[3])))
            vmove[key] = (own, nx - float(f[2]), ny - float(f[3]))
vias_kept = defaultdict(list)
for key, n in sorted(vk.items()):
    net, x, y = key
    if key in vmove:
        own, dx, dy = vmove[key]
        vias_kept[own].append(key)
        ops.append('VMOVE|%s|%s|%s|%s|%s' % (net, x, y, f4(dx), f4(dy)) + ('|N=%d' % n if n > 1 else ''))
    else:
        ops.append('VDEL|%s|%s|%s' % (net, x, y) + ('|N=%d' % n if n > 1 else ''))

# ---------------------------------------------------------------- free mechanical lines
sock = {n: (out['J_FPC%d' % n]['x'] - B['J_FPC%d' % n]['x'], out['J_FPC%d' % n]['y'] - B['J_FPC%d' % n]['y']) for n in range(1, 6)}
mk = Counter()
for f in geo:
    if f[0] == 'TRACK' and f[1].startswith('Mechanical') and 'INCOMP=False' in f:
        mk[(f[1], f[3], f[4], f[5], f[6])] += 1
n_mmove = n_mdel = 0
for (lay, a, b_, c, e), n in sorted(mk.items()):
    xm = (float(a) + float(c)) / 2
    tail = '|N=%d' % n if n > 1 else ''
    if lay == 'Mechanical Layer 4':
        k = min(range(1, 6), key=lambda k: abs(B['J_FPC%d' % k]['x'] - xm))
        ops.append('MMOVE|%s|%s|%s|%s|%s|%s|%s' % (lay, a, b_, c, e, f4(sock[k][0]), f4(sock[k][1])) + tail); n_mmove += n
    else:
        ops.append('MDEL|%s|%s|%s|%s|%s' % (lay, a, b_, c, e) + tail); n_mdel += n

# ---------------------------------------------------------------- antenna keep-out (moves with the ST67 block)
for f in geo:
    if f[0] == 'REGION' and f[1] == 'Keep Out Layer' and 'INCOMP=False' in f:
        x0, y0, x1, y1 = map(float, f[3:7])
        dx, dy = out['U_WIFI1']['x'] - B['U_WIFI1']['x'], out['U_WIFI1']['y'] - B['U_WIFI1']['y']
        ops.append('KMOVE|%s|%s|%s|%s|%s|%s' % (f4(x0), f4(y0), f4(x1), f4(y1), f4(dx), f4(dy)))

# ---------------------------------------------------------------- region-scoped rule exceptions follow their anchor part
MIL = 0.0254
rules = [l.rstrip('\n').split('|', 3) for l in open(os.path.join(HERE, 'work', 'B_OPS.txt')) if l.startswith('RULE|')]
rule_log = []
for _, name, no, expr in rules:
    m = re.search(r'InRegionAbsolute\(([-0-9.]+),([-0-9.]+),([-0-9.]+),([-0-9.]+)\)', expr)
    x0, y0, x1, y1 = (float(v) * MIL for v in m.groups())
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    comp = re.search(r"InComponent\('([^']+)'\)", expr)
    nets = re.findall(r"InNet\('([^']+)'\)", expr)
    if 'Keep-Out' in expr:
        anchor = 'U_WIFI1'
    elif comp:
        anchor = comp.group(1)
    else:
        best = None
        for d, p in B.items():
            if d.startswith('FP:'):
                continue
            for q in p['pads']:
                if nets and q['net'] not in nets:
                    continue
                dist = abs((q['bx0'] + q['bx1']) / 2 - cx) + abs((q['by0'] + q['by1']) / 2 - cy)
                if best is None or dist < best[0]:
                    best = (dist, d)
        anchor = best[1]
    p, r = B[anchor], out[anchor]
    cs = [to_world((r['x'], r['y']), r['rot'], r['side'], *to_local(p, a, b_)) for a, b_ in ((x0, y0), (x1, y1))]
    nx0, nx1 = sorted((cs[0][0], cs[1][0])); ny0, ny1 = sorted((cs[0][1], cs[1][1]))
    new = expr[:m.start()] + 'InRegionAbsolute(%.6f,%.6f,%.6f,%.6f)' % (nx0 / MIL, ny0 / MIL, nx1 / MIL, ny1 / MIL) + expr[m.end():]
    ops.append('RULE|%s|%s|%s' % (name, no, new))
    rule_log.append('%s scope%s anchor %s (%s)' % (name, no, anchor, 'flipped' if r['side'] != p['side'] else 'same side'))

# ---------------------------------------------------------------- new paste rule, outline, pours
svc_scope = ' Or '.join("InComponent('%s')" % d for d in sorted(SERVICE))
ops.append('RULE_PASTE|PASTE_NONE_SERVICE_PADS|IsPad And (%s)|-1.0' % svc_scope)
ops.append('OUTLINE|%.1f|%.1f' % (X1 - X0, Y1 - Y0))
for pn in ('EMG_L2_COMMON_GND', 'EMG_L4_COMMON_GND'):
    ops.append('POLY|%s|%s|%s|%s|%s' % (pn, f4(X0 + 0.5), f4(Y0 + 0.5), f4(X1 - 0.5), f4(Y1 - 0.5)))

open(os.path.join(HERE, 'work', 'C2_OPS.txt'), 'w').write('\n'.join(ops) + '\n')
kinds = Counter(o.split('|')[0] for o in ops)
summary = ['C2_OPS summary', 'ops by kind: ' + ', '.join('%s %d' % kv for kv in sorted(kinds.items())),
           'components flipped: %d' % sum(1 for o in ops if o.startswith('COMP|') and o.split('|')[4] == '1'),
           'thermal vias kept with their part: ' + ', '.join('%s %d' % (k, len(v)) for k, v in sorted(vias_kept.items())),
           'mechanical: %d socket marker lines moved, %d assembly leader lines removed' % (n_mmove, n_mdel)] + rule_log
open(os.path.join(EV, 'C2_OPS_SUMMARY.txt'), 'w').write('\n'.join(summary) + '\n')
print('\n'.join(summary))
