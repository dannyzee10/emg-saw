"""Renders FROM THE SAVED NATIVE GEOMETRY (GEOMETRY_*.txt exports), labelled as renders:
  views/RENDER_C2_native_TOP.png, views/RENDER_C2_native_BOTTOM_xray.png, views/RENDER_A_B_C2_same_scale.png"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
here = os.path.dirname(os.path.abspath(__file__)); EV = os.path.join(os.path.dirname(here), 'evidence'); V = os.path.join(EV, 'views')
ANALOG_SHEETS = None


def load(name):
    comps, pads, outline, vias = {}, [], None, []
    for l in open(os.path.join(EV, name), encoding='utf-8', errors='replace'):
        f = l.rstrip('\n').split('|')
        if f[0] == 'COMP':
            comps[f[1]] = ('Bottom' if f[2].startswith('Bottom') else 'Top', float(f[6]), float(f[7]), float(f[8]), float(f[9]))
        elif f[0] == 'PAD':
            pads.append((f[1], f[4], float(f[7]), float(f[8]), float(f[9]), float(f[10])))
        elif f[0] == 'VIA':
            vias.append((float(f[2]), float(f[3]), float(f[4])))
    return comps, pads, vias


def outline_of(tag):
    return {'A': (10, 10, 90, 55), 'B': (10, 10, 85, 50), 'C2': (10, 10, 69.1, 46)}[tag]


def draw(ax, geo, tag, side=None, labels=False, title=''):
    comps, pads, vias = geo
    x0, y0, x1, y1 = outline_of(tag)
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, ec='k', lw=1.8))
    for d, (s, a, b, c, e) in comps.items():
        if side and s != side:
            continue
        ax.add_patch(Rectangle((a, b), c - a, e - b, fill=(s == 'Bottom'), fc='#9fd49f', ec='#2a7a2a' if s == 'Bottom' else '#777',
                               lw=0.5, alpha=0.55 if s == 'Bottom' else 1))
        if labels and (c - a) * (e - b) > 6:
            ax.text((a + c) / 2, (b + e) / 2, d, fontsize=4.5, ha='center', va='center')
    for ref, lay, a, b, c, e in pads:
        if lay == 'Multi Layer':
            col = '#c9a227'
        elif lay == 'Top Layer':
            col = '#3b6fd6'
        elif lay == 'Bottom Layer':
            col = '#d64b3b'
        else:
            continue
        if side == 'Top' and lay == 'Bottom Layer' or side == 'Bottom' and lay == 'Top Layer':
            continue
        ax.add_patch(Rectangle((a, b), c - a, e - b, fc=col, ec='none', alpha=0.8))
    for vx, vy, vd in vias:
        ax.add_patch(plt.Circle((vx, vy), vd / 2, color='#555'))
    ax.set_aspect('equal'); ax.set_xlim(8, 92); ax.set_ylim(8, 57) if not side else None
    ax.set_title(title, fontsize=10); ax.grid(alpha=0.2)


C2 = load('GEOMETRY_C2_PLACED.txt')
for side, fn, t in (('Top', 'RENDER_C2_native_TOP.png', 'C2 TOP (render of saved native geometry) 59.1 x 36 mm'),
                    ('Bottom', 'RENDER_C2_native_BOTTOM_xray.png', 'C2 BOTTOM, x-ray viewed from top (render of saved native geometry)')):
    fig, ax = plt.subplots(figsize=(16, 10.5))
    draw(ax, C2, 'C2', side, labels=True, title=t)
    ax.set_xlim(9, 70.1); ax.set_ylim(9, 52)
    fig.tight_layout(); fig.savefig(os.path.join(V, fn), dpi=140); plt.close(fig)
fig, axes = plt.subplots(1, 3, figsize=(27, 7.5))
for ax, (tag, fn) in zip(axes, (('A', 'GEOMETRY_A_BASELINE.txt'), ('B', 'GEOMETRY_B_TRIAL.txt'), ('C2', 'GEOMETRY_C2_PLACED.txt'))):
    g = C2 if tag == 'C2' else load(fn)
    x0, y0, x1, y1 = outline_of(tag)
    draw(ax, g, tag, None, labels=False, title='%s  %.1f x %.1f mm = %.0f mm2  (top outlined, bottom filled green)' % (
        tag, x1 - x0, y1 - y0, (x1 - x0) * (y1 - y0) - 4 * (4 - 3.14159)))
    ax.set_xlim(8, 92); ax.set_ylim(8, 57)
fig.suptitle('Same scale: baseline A -> candidate B -> candidate C2 (renders of saved native geometry)', fontsize=13)
fig.tight_layout(); fig.savefig(os.path.join(V, 'RENDER_A_B_C2_same_scale.png'), dpi=110); plt.close(fig)
print('renders written')
