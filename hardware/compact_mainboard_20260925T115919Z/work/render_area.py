"""Offline preview of an area: true pad copper (labelled), existing top copper, vias, planned CSV copper.
usage: python render_area.py x0 x1 y0 y1 out.png [plan.csv ...]   (preview only, not CAD evidence)"""
import csv, sys, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MP, Circle
import geom as G

x0, x1, y0, y1 = map(float, sys.argv[1:5]); out = sys.argv[5]; plans = sys.argv[6:]
objs, comps, keep = G.load()
fig, ax = plt.subplots(figsize=(18, 18 * (y1 - y0) / (x1 - x0) + 0.5), dpi=90)
MM = 18 * 90 / (x1 - x0) * 0.72 / 90 * 72 / 72  # points per mm (approx for linewidth)
ppm = fig.dpi * 18 / (x1 - x0) * 0.72  # pixels per mm, rough


def lw(w):
    return w * ppm * 72 / fig.dpi


def inview(g):
    b = g.bounds
    return not (b[2] < x0 or b[0] > x1 or b[3] < y0 or b[1] > y1)


for o in objs:
    if not inview(o.geom):
        continue
    if o.kind == 'PAD' and o.layers & {'Top Layer'}:
        ax.add_patch(MP(list(o.geom.exterior.coords), color='green' if o.net == 'GND' else '#d44', alpha=.45, lw=0))
        ax.text(o.geom.centroid.x, o.geom.centroid.y, f'{o.comp}.{o.name}\n{o.net[:10]}', fontsize=4.5, ha='center', va='center')
    elif o.kind == 'TRACK' and 'Top Layer' in o.layers:
        ax.add_patch(MP(list(o.geom.exterior.coords), color='#e90', alpha=.8, lw=0))
    elif o.kind == 'VIA':
        ax.add_patch(MP(list(o.geom.exterior.coords), color='blue', alpha=.6, lw=0))
for k in keep:
    if inview(k):
        ax.add_patch(MP(list(k.exterior.coords), fill=False, ec='m', hatch='//', lw=.5))
for pth in plans:
    for r in csv.DictReader(open(pth)):
        if r['kind'] == 'TRACK':
            g = G.track(r['net'], r['layer'], [(float(r['x1']), float(r['y1'])), (float(r['x2']), float(r['y2']))], float(r['w'])).geom
            if inview(g):
                ax.add_patch(MP(list(g.exterior.coords), color='lime' if r['net'] == 'GND' else 'cyan', alpha=.8, lw=0))
        else:
            c = (float(r['x1']), float(r['y1']))
            ax.add_patch(Circle(c, float(r['d']) / 2, color='lime' if r['net'] == 'GND' else 'cyan', ec='k', lw=.4))
ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_aspect('equal'); ax.grid(alpha=.3)
ax.set_xticks([round(x0 + i * 0.5, 2) for i in range(int((x1 - x0) / 0.5) + 1)]); ax.tick_params(labelsize=5)
plt.tight_layout(); plt.savefig(out)
