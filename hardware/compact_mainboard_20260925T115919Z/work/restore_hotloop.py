"""Carry candidate B's designed TPS631000 hot-loop copper (LX/VIN/VOUT/FB tracks + the two cap GND vias) into C2 with exactly
the converter cell's transform (flip about the B group centre, move to the C2 centre; Top copper -> Bottom copper).
Output: evidence/ROUTE_PLAN_C2_HOTLOOP.csv in the router plan format (checked by build_ops.py like any routed copper)."""
import csv, os, pickle
from c2lib import load_b, EV, HERE
B = load_b()
plan = pickle.load(open(os.path.join(HERE, 'work', 'plan_C2.pkl'), 'rb'))['out']
mem = [d for d in B if B[d]['group'] == 'CONVERTER']
gx = (min(B[d]['bx0'] for d in mem) + max(B[d]['bx1'] for d in mem)) / 2
gy = (min(B[d]['by0'] for d in mem) + max(B[d]['by1'] for d in mem)) / 2
# plan centre = transformed group centre: recover it from UP2's origin (x'' = cx + gx - x ; y'' = y - gy + cy)
cx = plan['UP2']['x'] - gx + B['UP2']['x']
cy = plan['UP2']['y'] - B['UP2']['y'] + gy
T = lambda x, y: (cx + gx - x, y - gy + cy)
box = (min(B[d]['bx0'] for d in mem) - 0.3, min(B[d]['by0'] for d in mem) - 0.3, max(B[d]['bx1'] for d in mem) + 0.3, max(B[d]['by1'] for d in mem) + 0.3)
NETS = {'NetL1_1', 'NetL1_2', 'NetCUP4_FB_1', 'VSYS', '3V3_DIG'}
rows, seen = [], set()
for l in open(os.path.join(EV, 'GEOMETRY_B_TRIAL.txt'), encoding='utf-8', errors='replace'):
    f = l.rstrip('\n').split('|')
    if f[0] == 'TRACK' and f[1] == 'Top Layer' and f[2] in NETS:
        x1, y1, x2, y2, w = map(float, f[3:8])
        if not all(box[0] <= x <= box[2] and box[1] <= y <= box[3] for x, y in ((x1, y1), (x2, y2))):
            continue
        a, b = T(x1, y1), T(x2, y2)
        key = (f[2], tuple(sorted([(round(a[0], 3), round(a[1], 3)), (round(b[0], 3), round(b[1], 3))])))
        if key in seen:
            continue
        seen.add(key)
        rows.append({'kind': 'TRACK', 'group': 'HOTLOOP_' + f[2], 'net': f[2], 'layer': 'Bottom Layer', 'x1': '%.4f' % a[0], 'y1': '%.4f' % a[1],
                     'x2': '%.4f' % b[0], 'y2': '%.4f' % b[1], 'w': '%.3f' % w, 'd': '', 'h': '', 'conn': 'HOTLOOP|' + f[2], 'relax': ''})
    elif f[0] == 'VIA' and f[1] == 'GND':
        x, y = float(f[2]), float(f[3])
        if box[0] <= x <= box[2] and box[1] <= y <= box[3]:
            a = T(x, y)
            rows.append({'kind': 'VIA', 'group': 'HOTLOOP_GND', 'net': 'GND', 'layer': '', 'x1': '%.4f' % a[0], 'y1': '%.4f' % a[1], 'x2': '', 'y2': '',
                         'w': '', 'd': f[4], 'h': f[5], 'conn': 'HOTLOOP|GND', 'relax': ''})
with open(os.path.join(EV, 'ROUTE_PLAN_C2_HOTLOOP.csv'), 'w', newline='') as fo:
    w = csv.DictWriter(fo, fieldnames=['kind', 'group', 'net', 'layer', 'x1', 'y1', 'x2', 'y2', 'w', 'd', 'h', 'conn', 'relax'])
    w.writeheader(); w.writerows(rows)
print('group centre B (%.3f,%.3f) -> C2 (%.3f,%.3f); rows: %d tracks, %d vias' % (gx, gy, cx, cy, sum(r['kind'] == 'TRACK' for r in rows),
      sum(r['kind'] == 'VIA' for r in rows)))
