"""Render the BK13 band (both faces, x-ray) from a native geometry export: pads, free tracks per layer, vias, keepouts,
component bounding boxes.  usage: GEOM_FILE=... python render_bk13_band.py OUT.png [x0,y0,x1,y1]"""
import os, sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon as MP
import geom as G

win = [float(v) for v in (sys.argv[2] if len(sys.argv) > 2 else '10,10,69.1,20').split(',')]
objs, comps, keepouts = G.load()
fig, ax = plt.subplots(figsize=(26, 26 * (win[3] - win[1]) / (win[2] - win[0]) + 1))
col = {'Top Layer': '#d33', 'Mid Layer 2': '#e90', 'Mid Layer 4': '#a3c', 'Bottom Layer': '#36c'}
for ref, r in comps.items():
    x0, y0, x1, y1 = map(float, r[6:10]) if len(r) > 9 else (0, 0, 0, 0)
    if x1 < win[0] or x0 > win[2] or y1 < win[1] or y0 > win[3]:
        continue
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, ec='#3a3' if r[2] == 'Top Layer' else '#06c', lw=0.6, ls='--'))
    ax.text((x0 + x1) / 2, y1 + 0.05, ref, fontsize=5, ha='center', color='#060' if r[2] == 'Top Layer' else '#036')
for o in objs:
    b = o.geom.bounds
    if b[2] < win[0] or b[0] > win[2] or b[3] < win[1] or b[1] > win[3]:
        continue
    g = o.geom
    if o.kind == 'PAD':
        c = '#c44' if 'Top Layer' in o.layers and len(o.layers) == 1 else ('#48c' if len(o.layers) == 1 else '#888')
        ax.add_patch(MP(list(g.exterior.coords), fc=c, alpha=0.55, ec='k', lw=0.2))
        ax.text(g.centroid.x, g.centroid.y, o.net[:8], fontsize=3.2, ha='center', va='center')
    elif o.kind == 'TRACK':
        L = next(iter(o.layers))
        ax.add_patch(MP(list(g.exterior.coords), fc=col.get(L, '#999'), alpha=0.5, lw=0))
    elif o.kind == 'VIA':
        ax.add_patch(MP(list(g.exterior.coords), fc='#0a0', alpha=0.7, lw=0))
    elif o.kind == 'KEEPOUT':
        ax.add_patch(MP(list(g.exterior.coords), fc='none', ec='m', hatch='///', lw=0.5))
ax.set_xlim(win[0], win[2]); ax.set_ylim(win[1], win[3]); ax.set_aspect('equal'); ax.grid(lw=0.2)
ax.set_title('BK13 band x-ray: red=Top pads, blue=Bottom pads, orange=L3, purple=L5, blue tracks=L6, green=vias, magenta=keepout')
plt.savefig(sys.argv[1], dpi=160, bbox_inches='tight')
print('saved', sys.argv[1])
