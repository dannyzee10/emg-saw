"""Offline baseline measurement from native exports (no Altium needed):
  evidence/GEOMETRY_A_BASELINE.txt (native geometry export of B == A, 25 Sep 20:01)
  drl evidence NATIVE_FINAL_20260924T015854610Z/INVENTORY.txt (native inventory: source sheet, footprint, UID)
Writes evidence/BASELINE_COMPONENTS.csv and prints per-sheet / per-side statistics."""
import csv, os, re
from collections import defaultdict

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INV = r'C:\Users\PMLS\Desktop\emg-saw\hardware\pcb_layout_2026-09-23_drl\evidence\NATIVE_FINAL_20260924T015854610Z\INVENTORY.txt'
GEO = os.path.join(HERE, 'evidence', 'GEOMETRY_A_BASELINE.txt')
U = 1e-4 * 0.0254   # Altium internal unit -> mm

inv = {}
for l in open(INV, encoding='utf-8', errors='replace'):
    f = l.rstrip('\n').split('|')
    if f[0] == 'COMP':
        inv[f[1]] = {'uid': f[2], 'sheet': f[4], 'lib': os.path.basename(f[5]), 'footprint': f[6],
                     'x': int(f[7]) * U, 'y': int(f[8]) * U, 'rot': f[9], 'layer_id': f[10]}
geo, pads, padext = {}, defaultdict(list), {}
for l in open(GEO, encoding='utf-8', errors='replace'):
    f = l.rstrip('\n').split('|')
    if f[0] == 'COMP':
        geo[f[1]] = {'side': 'Bottom' if f[2].startswith('Bottom') else 'Top', 'x': float(f[3]), 'y': float(f[4]),
                     'rot': f[5], 'bbox': tuple(map(float, f[6:10]))}
    elif f[0] == 'PAD':
        pads[f[1]].append((f[2], f[3], f[4]))
        # pad copper extent (conservative: half the larger pad dimension around the pad centre)
        px, py = float(f[5]), float(f[6])
        sx = float(f[13].split('=')[1]); sy = float(f[14].split('=')[1]); hr = max(sx, sy) / 2
        padext.setdefault(f[1], []).append((px - hr, py - hr, px + hr, py + hr))
assert set(geo) == set(inv), (set(geo) ^ set(inv))
rows = []
for d in sorted(geo):
    g, i = geo[d], inv[d]
    x0, y0, x1, y1 = g['bbox']
    for a, b, c, e in padext.get(d, []):
        x0, y0, x1, y1 = min(x0, a), min(y0, b), max(x1, c), max(y1, e)
    nets = sorted({p[1] for p in pads[d] if p[1] not in ('', '-')})
    rows.append({'designator': d, 'sheet': i['sheet'], 'footprint': i['footprint'], 'side': g['side'], 'x': g['x'], 'y': g['y'],
                 'rot': g['rot'], 'bx0': x0, 'by0': y0, 'bx1': x1, 'by1': y1, 'w': round(x1 - x0, 3), 'h': round(y1 - y0, 3),
                 'area_mm2': round((x1 - x0) * (y1 - y0), 3), 'pads': len(pads[d]), 'nets': ';'.join(nets), 'src_uid': i['uid']})
with open(os.path.join(HERE, 'evidence', 'BASELINE_COMPONENTS.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print('components', len(rows), 'top', sum(r['side'] == 'Top' for r in rows), 'bottom', sum(r['side'] == 'Bottom' for r in rows))
by = defaultdict(list)
for r in rows:
    by[r['sheet']].append(r)
print(f"{'sheet':20s} {'n':>4s} {'top':>4s} {'bot':>4s} {'sum bbox mm2':>13s} {'extent (x0,y0)-(x1,y1)':>30s}")
for s, rs in sorted(by.items()):
    ex = (min(r['bx0'] for r in rs), min(r['by0'] for r in rs), max(r['bx1'] for r in rs), max(r['by1'] for r in rs))
    print(f"{s:20s} {len(rs):4d} {sum(r['side']=='Top' for r in rs):4d} {sum(r['side']=='Bottom' for r in rs):4d} {sum(r['area_mm2'] for r in rs):13.1f}   ({ex[0]:.1f},{ex[1]:.1f})-({ex[2]:.1f},{ex[3]:.1f})")
print('total component bbox area (top) %.1f mm2, bottom %.1f mm2, board 3596.6 mm2' % (
    sum(r['area_mm2'] for r in rows if r['side'] == 'Top'), sum(r['area_mm2'] for r in rows if r['side'] == 'Bottom')))
big = sorted(rows, key=lambda r: -r['area_mm2'])[:25]
print('largest bodies:', ', '.join(f"{r['designator']}({r['w']}x{r['h']})" for r in big))
