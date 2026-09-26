"""Move every stitch via (and its stub's far end) D mm further out along the stub, so the 0.1 mm via-to-pad gap survives the
4-decimal rounding of the plan.  usage: python nudge_stitch.py IN.csv OUT.csv [D=0.012]"""
import csv, math, sys
src, dst = sys.argv[1], sys.argv[2]
D = float(sys.argv[3]) if len(sys.argv) > 3 else 0.012
rows = list(csv.DictReader(open(src)))
by = {}
for r in rows:
    by.setdefault(r['group'], []).append(r)
for g, rs in by.items():
    t = [r for r in rs if r['kind'] == 'TRACK']
    v = [r for r in rs if r['kind'] == 'VIA']
    if len(t) != 1 or len(v) != 1:
        continue
    t, v = t[0], v[0]
    x1, y1, x2, y2 = (float(t[k]) for k in ('x1', 'y1', 'x2', 'y2'))
    L = math.hypot(x2 - x1, y2 - y1)
    if L < 1e-6:
        continue
    nx, ny = x2 + (x2 - x1) / L * D, y2 + (y2 - y1) / L * D
    t['x2'], t['y2'] = round(nx, 4), round(ny, 4)
    v['x1'], v['y1'] = round(nx, 4), round(ny, 4)
with open(dst, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)
print('nudged', sum(1 for g, rs in by.items() if len(rs) == 2), 'stubs by', D, 'mm ->', dst)
