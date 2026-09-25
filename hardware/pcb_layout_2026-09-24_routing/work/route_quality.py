"""Route-quality review of a native geometry export (offline, not signoff).
Per net: routed length by layer, via count, pads, minimum-spanning-tree length of its pads (ideal), and the
detour ratio. Flags: analog/reference/ADC nets with big detours or on L3/L4, SPI nets not on L1/L3, and
L2 usage (must be zero). usage: python route_quality.py GEOMETRY.txt [out.csv]"""
import csv, math, sys
from collections import defaultdict

geom = sys.argv[1]
rows = [l.rstrip('\n').split('|') for l in open(geom, encoding='utf-8', errors='replace')]
CLS = r'C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\pcb_layout_2026-09-24_routing\evidence\inputs\CLASSES.txt'
cls = defaultdict(set)
for l in open(CLS, encoding='utf-8', errors='replace'):
    f = l.rstrip('\n').split('|')
    if f[0] == 'MEMBER' and f[1].startswith('EMG_'):
        cls[f[2]].add(f[1])
length = defaultdict(lambda: defaultdict(float)); vias = defaultdict(int); pads = defaultdict(list)
for r in rows:
    if r[0] == 'TRACK' and r[1] in ('Top Layer', 'Mid Layer 1', 'Mid Layer 2', 'Bottom Layer') and r[2] not in ('-', ''):
        length[r[2]][r[1]] += math.dist((float(r[3]), float(r[4])), (float(r[5]), float(r[6])))
    elif r[0] == 'VIA' and r[1] not in ('-', ''):
        vias[r[1]] += 1
    elif r[0] == 'PAD' and r[3] not in ('-', ''):
        pads[r[3]].append((float(r[5]), float(r[6])))


def mst(pts):
    if len(pts) < 2:
        return 0.0
    inside = {0}; total = 0.0
    d = {i: math.dist(pts[0], pts[i]) for i in range(1, len(pts))}
    while d:
        j = min(d, key=d.get); total += d.pop(j); inside.add(j)
        for k in d:
            d[k] = min(d[k], math.dist(pts[j], pts[k]))
    return total


out = []
for net in sorted(set(length) | set(pads)):
    if net == 'GND':
        continue
    L = sum(length[net].values()); ideal = mst(pads[net])
    out.append({'net': net, 'class': ';'.join(sorted(cls.get(net, []))), 'pads': len(pads[net]), 'routed_mm': round(L, 2),
                'ideal_mm': round(ideal, 2), 'ratio': round(L / ideal, 2) if ideal > 0.5 else '',
                'L1': round(length[net]['Top Layer'], 1), 'L2': round(length[net]['Mid Layer 1'], 1),
                'L3': round(length[net]['Mid Layer 2'], 1), 'L4': round(length[net]['Bottom Layer'], 1), 'vias': vias[net]})
if len(sys.argv) > 2:
    with open(sys.argv[2], 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
tot = defaultdict(float)
for o in out:
    for k in ('L1', 'L2', 'L3', 'L4'):
        tot[k] += o[k]
print('total routed mm by layer (non-GND):', {k: round(v) for k, v in tot.items()}, '| vias (non-GND):', sum(o['vias'] for o in out))
print('L2 usage (must be 0):', [o['net'] for o in out if o['L2'] > 0])
sens = [o for o in out if any(c in o['class'] for c in ('EMG_ANALOG', 'EMG_REFERENCE', 'EMG_ADC'))]
print('\nworst analog/reference/ADC detours (ratio, routed, ideal, layers):')
for o in sorted([o for o in sens if o['ratio'] != ''], key=lambda o: -o['ratio'])[:15]:
    print(f"  {o['net']:16s} {o['class']:32s} ratio {o['ratio']:5} routed {o['routed_mm']:6} ideal {o['ideal_mm']:6} L1 {o['L1']} L3 {o['L3']} L4 {o['L4']} vias {o['vias']}")
spi = [o for o in out if 'EMG_SPI' in o['class']]
print('\nSPI nets:')
for o in spi:
    print(f"  {o['net']:16s} routed {o['routed_mm']:6} ideal {o['ideal_mm']:6} L1 {o['L1']} L3 {o['L3']} L4 {o['L4']} vias {o['vias']}")
unrouted_like = [o for o in out if o['pads'] > 1 and o['routed_mm'] == 0]
print('\nnets with pads but no copper (likely unrouted or via-only):', [o['net'] for o in unrouted_like][:40])
