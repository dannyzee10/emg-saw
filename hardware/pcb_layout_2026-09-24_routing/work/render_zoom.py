"""Labeled offline preview of a region (pads with designator-pad/net, top copper, vias). Not CAD evidence."""
import sys, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
x0, x1, y0, y1 = map(float, sys.argv[1:5]); out = sys.argv[5]
layers = sys.argv[6].split(',') if len(sys.argv) > 6 else ['Top Layer', 'Multi Layer']
R = [l.rstrip('\n').split('|') for l in open('evidence/GEOMETRY.txt', encoding='utf-8', errors='replace')]
fig, ax = plt.subplots(figsize=(20, 20 * (y1 - y0) / (x1 - x0) + 1), dpi=90)
col = {}
for r in R:
    if r[0] == 'COMP' and r[2] in [l for l in layers]:
        bx0, by0, bx1, by1 = map(float, r[6:10])
        if bx1 < x0 or bx0 > x1 or by1 < y0 or by0 > y1: continue
        ax.add_patch(Rectangle((bx0, by0), bx1 - bx0, by1 - by0, fill=False, ec='#999', lw=.6, ls='--'))
        ax.text(bx0, by1 + .05, r[1], fontsize=8, color='#555')
    if r[0] == 'PAD' and r[4] in layers:
        a, b, c, d = map(float, r[7:11])
        if c < x0 or a > x1 or d < y0 or b > y1: continue
        net = r[3]
        ax.add_patch(Rectangle((a, b), c - a, d - b, color='green' if net == 'GND' else '#d44', alpha=.55, lw=0))
        ax.text((a + c) / 2, (b + d) / 2, r[2] + '\n' + net[:12], fontsize=5.5, ha='center', va='center')
    if r[0] == 'TRACK' and r[1] in layers:
        ax.plot([float(r[3]), float(r[5])], [float(r[4]), float(r[6])], color='#e90', lw=2)
    if r[0] == 'REGION' and r[-2] == 'KEEPOUT=True':
        a, b, c, d = map(float, r[3:7]); ax.add_patch(Rectangle((a, b), c - a, d - b, fill=False, ec='m', hatch='//', lw=.8))
    if r[0] == 'VIA':
        ax.add_patch(Circle((float(r[2]), float(r[3])), float(r[4]) / 2, color='blue', alpha=.7))
ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_aspect('equal'); ax.grid(alpha=.3)
ax.set_xticks([x0 + i * 0.5 for i in range(int((x1 - x0) / 0.5) + 1)]); ax.tick_params(labelsize=6)
plt.tight_layout(); plt.savefig(out)
