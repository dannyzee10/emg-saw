"""Rule evidence on the SAVED NATIVE C2 state: separations between noise/heat sources and sensitive circuits, and the nets that
cross between the Top input stages and the Bottom op-amp modules (with their pad-to-pad span)."""
import math, os
from collections import defaultdict
from c2lib import load_b, EV
B = load_b()
comp, pads = {}, defaultdict(list)
for l in open(os.path.join(EV, 'GEOMETRY_C2_PLACED.txt'), encoding='utf-8', errors='replace'):
    f = l.rstrip('\n').split('|')
    if f[0] == 'COMP':
        comp[f[1]] = ('Bottom' if f[2].startswith('Bottom') else 'Top', float(f[6]), float(f[7]), float(f[8]), float(f[9]))
    elif f[0] == 'PAD' and f[1] != 'FREE' and f[4] in ('Top Layer', 'Bottom Layer', 'Multi Layer'):
        pads[f[3]].append((f[1], f[4], float(f[5]), float(f[6])))


def gap(a, b):
    A, Bb = comp[a], comp[b]
    dx = max(A[1] - Bb[3], Bb[1] - A[3], 0); dy = max(A[2] - Bb[4], Bb[2] - A[4], 0)
    return math.hypot(dx, dy)


def min_gap(src, targets):
    return min(((gap(s, t), s, t) for s in src for t in targets), key=lambda v: v[0])


ANALOG = [d for d in comp if B[d]['group'] == 'AFE']
REFS = [d for d in comp if d.startswith(('RV', 'Cdiv', 'R_VREF', 'R_ref', 'U1'))]
INPUTS = [d for d in comp if d.startswith(('RDD', 'INA', 'J_FPC'))]
CONV = [d for d in comp if B[d]['group'] == 'CONVERTER']
lines = ['C2 separation evidence (x-ray, component extents, saved native geometry)']
for name, src, dst in (('converter cell -> any analog part', CONV, ANALOG), ('converter cell -> electrode inputs (RDD/INA/BK13)', CONV, INPUTS),
                       ('converter cell -> references (divider/VREF/U1)', CONV, REFS), ('converter L1/UP2 -> ST67 32 kHz crystal', ['L1', 'UP2'], ['X_WIFI_32K']),
                       ('charger UP1 -> references', ['UP1'], REFS), ('charger UP1 -> electrode inputs', ['UP1'], INPUTS),
                       ('USB-C -> electrode inputs', ['J_USB_C'], INPUTS), ('button -> electrode inputs (ESD)', ['PWR_BTN_N'], INPUTS)):
    g, s, t = min_gap(src, dst)
    lines.append('  %-52s %5.2f mm  (%s .. %s)' % (name, g, s, t))
lines.append('Nets joining Top analog input-stage pads and Bottom op-amp-module pads (cross the board through vias):')
for net, ps in sorted(pads.items()):
    sides = {('Top' if l == 'Top Layer' else 'Bottom' if l == 'Bottom Layer' else 'Multi') for _, l, _, _ in ps}
    refs = {r for r, _, _, _ in ps}
    if not any(B[r]['group'] == 'AFE' for r in refs) or not {'Top', 'Bottom'} <= sides:
        continue
    xs = [p[2] for p in ps]; ys = [p[3] for p in ps]
    lines.append('  %-16s span %5.1f x %4.1f mm  parts %s' % (net, max(xs) - min(xs), max(ys) - min(ys), ' '.join(sorted(refs))[:110]))
open(os.path.join(EV, 'C2_RULE_EVIDENCE.txt'), 'w').write('\n'.join(lines) + '\n')
print('\n'.join(lines))
