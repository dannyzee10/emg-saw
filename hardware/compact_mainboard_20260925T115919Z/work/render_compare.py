"""Same-scale baseline-vs-candidate renders and an X-ray projection, from saved native geometry exports.
RENDERS from the saved CAD state's exported coordinates (not native Altium screen captures).
Outputs: evidence/views/RENDER_A_vs_B_same_scale.png, evidence/views/RENDER_B_xray_projection.png"""
import csv, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EV = os.path.join(HERE, 'evidence')
A = [r for r in csv.DictReader(open(os.path.join(EV, 'BASELINE_COMPONENTS.csv')))]
B = [r for r in csv.DictReader(open(os.path.join(EV, 'PLAN_B_COMPONENTS.csv'))) if not r['designator'].startswith('FP:')]
COL = {'AFE_Channel_1': '#4e79a7', 'AFE_Channel_2': '#59a14f', 'AFE_Channel_3': '#9c755f', 'AFE_Channel_4': '#f28e2b',
       'AFE_Channel_5': '#edc948', 'Analog_Shared': '#b07aa1', 'MCU_sheet': '#e15759', 'Power_tree_design': '#76b7b2'}

def board(ax, x1, y1):
    ax.add_patch(FancyBboxPatch((10, 10), x1 - 10, y1 - 10, boxstyle='round,pad=0,rounding_size=2', fill=False, lw=2, ec='k'))

def draw(ax, rows, side, title, x1, y1, mirror=False):
    board(ax, x1, y1)
    for r in rows:
        if r['side'] != side:
            continue
        x0, y0, xa, ya = (float(r[k]) for k in ('bx0', 'by0', 'bx1', 'by1'))
        ax.add_patch(Rectangle((x0, y0), xa - x0, ya - y0, fc=COL.get(r['sheet'], '#999'), ec='k', lw=0.2, alpha=0.7))
    ax.set_xlim(5, 95); ax.set_ylim(5, 62); ax.set_aspect('equal'); ax.grid(lw=0.2); ax.set_title(title, fontsize=9)
    if mirror:
        ax.invert_xaxis()

fig, axs = plt.subplots(2, 2, figsize=(18, 11), dpi=110)
draw(axs[0][0], A, 'Top', 'Baseline A 80 x 45 - TOP', 90, 55)
draw(axs[0][1], A, 'Bottom', 'Baseline A 80 x 45 - BOTTOM (viewed from bottom)', 90, 55, True)
draw(axs[1][0], B, 'Top', 'Candidate B 75 x 40 - TOP', 85, 50)
draw(axs[1][1], B, 'Bottom', 'Candidate B 75 x 40 - BOTTOM (viewed from bottom)', 85, 50, True)
fig.legend([Rectangle((0, 0), 1, 1, fc=c, alpha=0.7) for c in COL.values()], COL.keys(), loc='lower center', ncol=8, fontsize=8)
fig.suptitle('Same physical scale. Rendered from saved native geometry exports (not native screen captures).', fontsize=10)
plt.tight_layout(rect=(0, 0.04, 1, 0.97)); plt.savefig(os.path.join(EV, 'views', 'RENDER_A_vs_B_same_scale.png'))

# X-ray: top outlines, bottom filled, sensitive top zones hatched
fig, ax = plt.subplots(figsize=(14, 8.5), dpi=120)
board(ax, 85, 50)
zones = {'AFE inputs / RDD / INA (band)': (10.5, 10.5, 79.5, 23.5), 'ADC corner (R/C_ADC, MCU pins 21-30)': (54.5, 27.0, 62.5, 38.5),
         'converter L1 / LX': (32.0, 39.0, 36.0, 44.5), 'charger UP1 thermal pad': (20.5, 39.3, 25.1, 43.9),
         'ST67 antenna keep-out': (41.19, 49.44, 53.47, 54.44)}
for (name, (x0, y0, x1, y1)), c in zip(zones.items(), ('#1f77b4', '#9467bd', '#d62728', '#ff7f0e', '#e377c2')):
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, hatch='//', ec=c, lw=1.2, label=name))
for r in B:
    x0, y0, xa, ya = (float(r[k]) for k in ('bx0', 'by0', 'bx1', 'by1'))
    if r['side'] == 'Top':
        ax.add_patch(Rectangle((x0, y0), xa - x0, ya - y0, fill=False, ec='#888', lw=0.3))
    else:
        ax.add_patch(Rectangle((x0, y0), xa - x0, ya - y0, fc='#2ca02c' if r['group'] != 'AFE' else '#b07aa1', ec='k', lw=0.4, alpha=0.8))
        ax.text((x0 + xa) / 2, (y0 + ya) / 2, r['designator'], fontsize=4, ha='center', va='center')
ax.set_xlim(8, 88); ax.set_ylim(8, 56); ax.set_aspect('equal'); ax.grid(lw=0.2); ax.legend(loc='upper left', fontsize=7)
ax.set_title('Candidate B X-ray (viewed from TOP): top parts outlined grey, BOTTOM parts filled '
             '(green = moved support groups, purple = existing DNP DRL provision); hatched = sensitive/hot top zones', fontsize=9)
plt.tight_layout(); plt.savefig(os.path.join(EV, 'views', 'RENDER_B_xray_projection.png'))
print('saved renders')
