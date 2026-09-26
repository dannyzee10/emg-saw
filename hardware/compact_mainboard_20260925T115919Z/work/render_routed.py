"""Render of the routed C2 board FROM THE SAVED NATIVE GEOMETRY EXPORT (not an Altium screenshot):
  OUT_xray.png   all copper layers overlaid (x-ray)
  OUT_layers.png one panel per copper layer L1..L6 (pads, tracks, vias; pours shown as outlines)
usage: GEOM_FILE=... python render_routed.py OUT_PREFIX "title" """
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MP, Rectangle
import geom as G

out, title = sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else ''
objs, comps, keepouts = G.load()
LAY = [('Top Layer', 'L1 Top (parts/signal)', '#d62728'), ('Mid Layer 1', 'L2 GND plane', '#7f7f7f'),
       ('Mid Layer 2', 'L3 signal', '#ff7f0e'), ('Mid Layer 3', 'L4 GND plane', '#7f7f7f'),
       ('Mid Layer 4', 'L5 power/signal', '#9467bd'), ('Bottom Layer', 'L6 Bottom (parts/signal)', '#1f77b4')]
regions = [l.rstrip('\n').split('|') for l in open(G.GEOM, encoding='utf-8', errors='replace') if l.startswith('REGION|')]


def frame(ax, t):
    ax.add_patch(MP(list(G.BOARD.exterior.coords), fill=False, ec='k', lw=1.2))
    for k in keepouts:
        if k.area > 5:
            ax.add_patch(MP(list(k.exterior.coords), fill=False, ec='m', hatch='//', lw=0.6))
    ax.set_xlim(9.5, 69.6); ax.set_ylim(9.5, 46.5); ax.set_aspect('equal'); ax.set_title(t, fontsize=10)
    ax.set_xticks([]); ax.set_yticks([])


def draw_layer(ax, L, col, alpha=0.8):
    for r in regions:
        if r[1] == L and r[-3] == 'INPOLY=True':
            x0, y0, x1, y1 = map(float, r[3:7])
            if (x1 - x0) * (y1 - y0) > 50:
                ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, ec=col, lw=0.8, ls='--'))
    for o in objs:
        if o.kind == 'TRACK' and L in o.layers:
            ax.add_patch(MP(list(o.geom.exterior.coords), fc=col, alpha=alpha, lw=0))
        elif o.kind == 'PAD' and L in o.layers and len(o.layers) == 1:
            ax.add_patch(MP(list(o.geom.exterior.coords), fc=col, alpha=0.45, ec='k', lw=0.15))
        elif (o.kind == 'VIA') or (o.kind == 'PAD' and len(o.layers) > 2):
            if L in ('Top Layer', 'Bottom Layer') or o.kind == 'VIA':
                ax.add_patch(MP(list(o.geom.exterior.coords), fc='#2ca02c', alpha=0.7, lw=0))


fig, ax = plt.subplots(figsize=(24, 15))
for L, name, col in [LAY[5], LAY[4], LAY[2], LAY[0]]:
    draw_layer(ax, L, col, 0.55)
frame(ax, f'{title} - x-ray: red L1 Top, orange L3, purple L5, blue L6 Bottom, green vias (render of the native export)')
plt.savefig(out + '_xray.png', dpi=110, bbox_inches='tight'); plt.close(fig)
fig, axs = plt.subplots(3, 2, figsize=(24, 22))
for a, (L, name, col) in zip(axs.flat, LAY):
    draw_layer(a, L, col)
    frame(a, name)
fig.suptitle(title + ' - per copper layer (render of the native export)', fontsize=13)
plt.savefig(out + '_layers.png', dpi=90, bbox_inches='tight'); plt.close(fig)
print('saved', out + '_xray.png', out + '_layers.png')
