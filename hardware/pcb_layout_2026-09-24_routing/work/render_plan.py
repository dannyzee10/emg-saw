"""Preview renderer (offline, not CAD evidence): pads, top copper, vias, planned GND fanout."""
import csv, sys, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
xlim = (9, 91); ylim = (9, 56)
if len(sys.argv) > 1:
    xlim = tuple(map(float, sys.argv[1:3])); ylim = tuple(map(float, sys.argv[3:5]))
out = sys.argv[5] if len(sys.argv) > 5 else 'evidence/GND_FANOUT_PLAN.png'
R = [l.rstrip('\n').split('|') for l in open('evidence/GEOMETRY.txt', encoding='utf-8', errors='replace')]
fig, ax = plt.subplots(figsize=(22, 13), dpi=110)
for r in R:
    if r[0] == 'PAD' and r[4] in ('Top Layer', 'Multi Layer'):
        x1, y1, x2, y2 = map(float, r[7:11])
        ax.add_patch(Rectangle((x1, y1), x2 - x1, y2 - y1, color='green' if r[3] == 'GND' else '#c33', alpha=.6, lw=0))
    if r[0] == 'TRACK' and r[1] == 'Top Layer':
        ax.plot([float(r[3]), float(r[5])], [float(r[4]), float(r[6])], color='#e90', lw=1)
    if r[0] == 'VIA':
        ax.add_patch(Circle((float(r[2]), float(r[3])), 0.3, color='blue'))
for p in csv.DictReader(open('evidence/GND_FANOUT_PLAN.csv')):
    ax.plot([float(p['px']), float(p['vx'])], [float(p['py']), float(p['vy'])], color='lime', lw=1.5)
    if p['tie_only'] == '0':
        ax.add_patch(Circle((float(p['vx']), float(p['vy'])), 0.3, color='cyan', ec='k', lw=.3))
ax.plot([12, 88, 90, 90, 88, 12, 10, 10, 12], [10, 10, 12, 53, 55, 55, 53, 12, 10], 'k')
ax.set_xlim(*xlim); ax.set_ylim(*ylim); ax.set_aspect('equal'); ax.grid(alpha=.2)
plt.tight_layout(); plt.savefig(out)
