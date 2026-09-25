"""Render a placement (component bboxes coloured by schematic sheet, designators, board outline) from a
components CSV (BASELINE_COMPONENTS.csv or a candidate plan).  Offline planning aid, not native CAD evidence.
usage: python render_placement.py COMPONENTS.csv OUT.png [board_x0 board_y0 board_x1 board_y1] [title]"""
import csv, sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch

rows = list(csv.DictReader(open(sys.argv[1])))
out = sys.argv[2]
bx = list(map(float, sys.argv[3:7])) if len(sys.argv) >= 7 else [10, 10, 90, 55]
title = sys.argv[7] if len(sys.argv) > 7 else ''
COL = {'AFE_Channel_1': '#4e79a7', 'AFE_Channel_2': '#59a14f', 'AFE_Channel_3': '#9c755f', 'AFE_Channel_4': '#f28e2b',
       'AFE_Channel_5': '#edc948', 'Analog_Shared': '#b07aa1', 'MCU_sheet': '#e15759', 'Power_tree_design': '#76b7b2'}
fig, axes = plt.subplots(1, 2, figsize=(22, 7.5), dpi=110)
for ax, side in zip(axes, ('Top', 'Bottom')):
    ax.add_patch(FancyBboxPatch((bx[0], bx[1]), bx[2] - bx[0], bx[3] - bx[1], boxstyle='round,pad=0,rounding_size=2',
                                fill=False, lw=2, ec='black'))
    for r in rows:
        on = r['side'] == side
        x0, y0, x1, y1 = (float(r[k]) for k in ('bx0', 'by0', 'bx1', 'by1'))
        c = COL.get(r['sheet'], '#999999')
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc=c if on else 'none', ec=c, alpha=0.55 if on else 0.25,
                               lw=0.6, ls='-' if on else ':'))
        if on:
            ax.text((x0 + x1) / 2, (y0 + y1) / 2, r['designator'], fontsize=3.4, ha='center', va='center')
    ax.set_xlim(min(bx[0], 5) - 1, max(bx[2], 95) + 1); ax.set_ylim(min(bx[1], 5) - 1, max(bx[3], 62) + 1)
    ax.set_aspect('equal'); ax.grid(lw=0.2)
    ax.set_title(f'{title} {side} side (filled = on this side; dotted = other side)', fontsize=10)
    if side == 'Bottom':
        ax.invert_xaxis()
        ax.set_title(f'{title} Bottom side, VIEWED FROM BOTTOM (x mirrored)', fontsize=10)
handles = [Rectangle((0, 0), 1, 1, fc=c, alpha=0.55) for c in COL.values()]
fig.legend(handles, COL.keys(), loc='lower center', ncol=8, fontsize=8)
plt.tight_layout(rect=(0, 0.05, 1, 1)); plt.savefig(out); print('saved', out)
