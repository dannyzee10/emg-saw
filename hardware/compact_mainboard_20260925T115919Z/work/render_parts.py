"""Placement-only view of one face in a window: pads (with net + pin), component boxes, board edge, keepouts, holes.
usage: GEOM_FILE=... python render_parts.py OUT.png "x0,y0,x1,y1" "Bottom Layer"|"Top Layer" """
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MP, Rectangle
import geom as G

out, win, side = sys.argv[1], [float(v) for v in sys.argv[2].split(',')], sys.argv[3]
objs, comps, keepouts = G.load()
fig, ax = plt.subplots(figsize=(14, 14 * (win[3] - win[1]) / (win[2] - win[0])))
for ref, r in comps.items():
    if r[2] != side:
        continue
    x0, y0, x1, y1 = map(float, r[6:10])
    if x1 < win[0] or x0 > win[2] or y1 < win[1] or y0 > win[3]:
        continue
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, ec='#06c', lw=0.8, ls='--'))
    ax.text((x0 + x1) / 2, y1 + 0.06, ref, fontsize=8, ha='center', color='#036')
for o in objs:
    b = o.geom.bounds
    if b[2] < win[0] or b[0] > win[2] or b[3] < win[1] or b[1] > win[3]:
        continue
    if o.kind == 'PAD' and (side in o.layers or len(o.layers) > 2):
        c = '#48c' if len(o.layers) == 1 else '#999'
        ax.add_patch(MP(list(o.geom.exterior.coords), fc=c, alpha=0.6, ec='k', lw=0.3))
        ax.text(o.geom.centroid.x, o.geom.centroid.y, f'{o.name}\n{o.net[:10]}', fontsize=5, ha='center', va='center')
    elif o.kind == 'HOLE':
        ax.add_patch(MP(list(o.geom.exterior.coords), fc='w', ec='k', lw=0.5))
    elif o.kind == 'KEEPOUT':
        ax.add_patch(MP(list(o.geom.exterior.coords), fc='none', ec='m', hatch='///', lw=0.5))
ax.add_patch(MP(list(G.BOARD.exterior.coords), fill=False, ec='k', lw=1.2))
ax.add_patch(MP(list(G.BOARD.buffer(-0.5).exterior.coords), fill=False, ec='r', lw=0.6, ls=':'))
ax.set_xlim(win[0], win[2]); ax.set_ylim(win[1], win[3]); ax.set_aspect('equal'); ax.grid(lw=0.2)
ax.set_title(f'{side} placement (x-ray off), window {win}')
plt.savefig(out, dpi=150, bbox_inches='tight')
print('saved', out)
