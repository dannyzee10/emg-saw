"""Zoomed x-ray of one window from the native geometry export: copper per layer (colour), vias, pad net labels,
component boxes, and the unrouted connections of a DRC json as dashed lines.
usage: GEOM_FILE=... python render_window.py OUT.png "x0,y0,x1,y1" [DRC.json] """
import json, re, sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MP, Rectangle
from shapely.geometry import box
import geom as G

out, win = sys.argv[1], [float(v) for v in sys.argv[2].split(',')]
drc = sys.argv[3] if len(sys.argv) > 3 else None
objs, comps, keepouts = G.load()
W = box(*win)
COL = {'Top Layer': '#d62728', 'Mid Layer 2': '#ff7f0e', 'Mid Layer 4': '#9467bd', 'Bottom Layer': '#1f77b4'}
fig, ax = plt.subplots(figsize=(14, 14 * (win[3] - win[1]) / (win[2] - win[0])))
for L in ('Bottom Layer', 'Mid Layer 4', 'Mid Layer 2', 'Top Layer'):
    for o in objs:
        if L not in o.layers or not o.geom.intersects(W):
            continue
        if o.kind == 'TRACK':
            ax.add_patch(MP(list(o.geom.exterior.coords), fc=COL[L], alpha=0.55, lw=0))
        elif o.kind == 'PAD' and len(o.layers) == 1:
            ax.add_patch(MP(list(o.geom.exterior.coords), fc=COL[L], alpha=0.35, ec='k', lw=0.3))
            c = o.geom.centroid
            ax.text(c.x, c.y, f'{o.name}\n{o.net}', fontsize=5, ha='center', va='center', clip_on=True)
for o in objs:
    if (o.kind == 'VIA' or (o.kind == 'PAD' and len(o.layers) > 2)) and o.geom.intersects(W):
        ax.add_patch(MP(list(o.geom.exterior.coords), fc='#2ca02c', alpha=0.7, lw=0))
        if o.kind == 'VIA':
            c = o.geom.centroid
            ax.text(c.x, c.y, o.net, fontsize=4, ha='center', va='center', clip_on=True)
for ref, r in comps.items():
    x0, y0, x1, y1 = map(float, r[6:10])
    if x1 < win[0] or x0 > win[2] or y1 < win[1] or y0 > win[3]:
        continue
    ls = '--' if r[2].startswith('Bottom') else '-'
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, ec='#06c', lw=0.6, ls=ls))
    ax.text((x0 + x1) / 2, y1 + 0.04, ref, fontsize=6, ha='center', color='#036', clip_on=True)
if drc:
    for d in json.load(open(drc))['details']:
        if not d.startswith('Un-Routed'):
            continue
        pts = [tuple(map(float, p)) for p in re.findall(r'\(([\d.]+)mm,([\d.]+)mm\)', d)]
        if len(pts) >= 2:
            a, b = pts[0], pts[-1]
            ax.plot([a[0], b[0]], [a[1], b[1]], 'k--', lw=0.8)
ax.set_xlim(win[0], win[2]); ax.set_ylim(win[1], win[3]); ax.set_aspect('equal')
ax.set_title('red L1 Top, orange L3, purple L5, blue L6 Bottom, green vias; dashed = unrouted', fontsize=9)
plt.savefig(out, dpi=130, bbox_inches='tight'); plt.close(fig)
print('saved', out)
