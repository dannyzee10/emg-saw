"""Pad-level verification of the saved C2 board (GEOMETRY_C2_PLACED.txt, native export after save/reopen):
  1. every native pad sits where the audited plan put it (position, copper layer)
  2. electrical preservation vs candidate B: pad->net per component (service parts by pad designator), net set, free pads
  3. no free copper left except the thermal vias that travel with their part"""
import os, pickle
from collections import defaultdict
from c2lib import load_b, EV, HERE
S = pickle.load(open(os.path.join(HERE, 'work', 'plan_C2.pkl'), 'rb'))
plan = S['out']
B = load_b()
geo = [l.rstrip('\n').split('|') for l in open(os.path.join(EV, 'GEOMETRY_C2_PLACED.txt'), encoding='utf-8', errors='replace')]
nat = defaultdict(list)
for f in geo:
    if f[0] == 'PAD':
        ref = 'FP:' + f[2] if f[1] == 'FREE' else f[1]
        num, net, lay = (('1', f[3], f[4]) if f[1] == 'FREE' else (f[2], f[3], f[4]))
        kv = dict(p.split('=') for p in f[11:] if '=' in p)
        nat[ref].append({'num': num, 'net': net, 'layer': lay, 'x': float(f[5]), 'y': float(f[6]), 'hole': float(kv.get('HOLE', 0))})
SERVICE = {'J_SWD', 'JP_WIFI_BOOT', 'TP_GND', 'TP_MCU_BOOT0', 'TP_WIFI_BOOT', 'TP_WIFI_CHIP_EN', 'TP_WIFI_UART_RX', 'TP_WIFI_UART_TX'}
pos_err = 0.0; n_pads = 0; issues = []
for ref, r in plan.items():
    npads = nat.get(ref, [])
    if len(npads) != len(r['pads']):
        issues.append('PADCOUNT %s native %d plan %d' % (ref, len(npads), len(r['pads'])))
    used = set()
    for q in r['pads']:
        # nearest native pad (same designator where the plan has one)
        cands = [(abs(p['x'] - q['x']) + abs(p['y'] - q['y']), i) for i, p in enumerate(npads) if i not in used and
                 (p['num'] == q['num'] or q['num'].startswith('H') or q['num'] == '')]
        if not cands:
            issues.append('NOPAD %s.%s' % (ref, q['num'])); continue
        dmin, i = min(cands); used.add(i); p = npads[i]
        n_pads += 1; pos_err = max(pos_err, dmin)
        if dmin > 0.005:
            issues.append('POS %s.%s off %.4f mm' % (ref, q['num'], dmin))
        ql = q['layer']
        if ql != p['layer']:
            issues.append('LAYER %s.%s native %s plan %s' % (ref, q['num'], p['layer'], ql))
# electrical preservation vs B
CU = ('Top Layer', 'Bottom Layer', 'Multi Layer')
bnet = {(ref, q['num'], q['layer'] in CU): q['net'] for ref, p in B.items() for q in p['pads']}   # paste-only pads share numbers
net_issues = []
for ref, pads in nat.items():
    for p in pads:
        if ref in SERVICE and p['num'] in ('', ):
            if p['net'] not in ('', '-'):
                net_issues.append('SERVICE blank pad has net %s.%s %s' % (ref, p['num'], p['net']))
            continue
        exp = bnet.get((ref, p['num'], p['layer'] in CU))
        if exp is None:
            net_issues.append('NO B PAD %s.%s' % (ref, p['num']))
        elif exp != p['net']:
            net_issues.append('NET %s.%s native %s B %s' % (ref, p['num'], p['net'], exp))
bnets = {q['net'] for p in B.values() for q in p['pads'] if q['net'] not in ('', '-')}
cnets = {p['net'] for v in nat.values() for p in v if p['net'] not in ('', '-')}
# free copper
free_cu = [f for f in geo if f[0] == 'TRACK' and f[1] in ('Top Layer', 'Mid Layer 1', 'Mid Layer 2', 'Bottom Layer') and 'INCOMP=False' in f]
vias = [f for f in geo if f[0] == 'VIA']
comps = [f for f in geo if f[0] == 'COMP']
lines = ['C2 pad-level verification (native export after save/reopen)',
         'components %d, pads %d (compared to plan %d), worst position error %.4f mm' % (len(comps), sum(len(v) for v in nat.values()), n_pads, pos_err),
         'placement issues: %d' % len(issues)] + ['  ' + i for i in issues[:30]] + \
        ['electrical: net issues %d; nets B %d / C2 %d, only-in-B %s, only-in-C2 %s' % (len(net_issues), len(bnets), len(cnets),
         sorted(bnets - cnets), sorted(cnets - bnets))] + ['  ' + i for i in net_issues[:30]] + \
        ['free pads: %d' % len([k for k in nat if k.startswith('FP:')]),
         'free copper tracks left: %d; vias: %d (nets %s)' % (len(free_cu), len(vias), sorted({f[1] for f in vias}))]
open(os.path.join(EV, 'C2_PAD_VERIFICATION.txt'), 'w').write('\n'.join(lines) + '\n')
print('\n'.join(lines))
