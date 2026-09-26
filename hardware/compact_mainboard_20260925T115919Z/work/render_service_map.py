"""Where did the old right-edge service strip go?  Top and bottom (x-ray) of C2 with the service parts highlighted."""
import os, pickle
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
here = os.path.dirname(os.path.abspath(__file__))
S = pickle.load(open(os.path.join(here, 'plan_C2.pkl'), 'rb'))
out = S['out']; X0, Y0, X1, Y1 = S['OUTLINE']
SVC = {'J_SWD': 'Tag-Connect TC2030-NL (was J_SWD header)', 'JP_WIFI_BOOT': 'solder jumper (was JP header)',
       'TP_GND': 'flat pad', 'TP_MCU_BOOT0': 'flat pad', 'TP_WIFI_BOOT': 'flat pad', 'TP_WIFI_CHIP_EN': 'flat pad',
       'TP_WIFI_UART_RX': 'flat pad', 'TP_WIFI_UART_TX': 'flat pad', 'R_WIFI_BOOT_OVR': '', 'J_Li-Po': 'battery header',
       'R_TH_BAT': 'NTC wires', 'LED_CHG': 'charge LED'}
fig, axes = plt.subplots(1, 2, figsize=(22, 8.2))
for ax, side in zip(axes, ('Top', 'Bottom')):
    ax.add_patch(Rectangle((X0, Y0), X1 - X0, Y1 - Y0, fill=False, ec='k', lw=2))
    for d, r in out.items():
        if r['side'] != side:
            continue
        hot = d in SVC
        ax.add_patch(Rectangle((r['bx0'], r['by0']), r['bx1'] - r['bx0'], r['by1'] - r['by0'], fill=hot,
                               fc='#ffcc00' if hot else 'none', ec='#d00' if hot else '#bbb', lw=1.6 if hot else 0.5, alpha=0.9 if hot else 1))
        for q in r['pads']:
            ax.add_patch(Rectangle((q['bx0'], q['by0']), q['bx1'] - q['bx0'], q['by1'] - q['by0'],
                                   fc='#d00' if hot else '#9ab', ec='none', alpha=0.9 if hot else 0.5))
        if hot:
            ax.annotate('%s\n%s' % (d, SVC[d]) if SVC[d] else d, ((r['bx0'] + r['bx1']) / 2, (r['by0'] + r['by1']) / 2),
                        xytext=(8, 8), textcoords='offset points', fontsize=8, color='#900', fontweight='bold',
                        arrowprops=dict(arrowstyle='-', color='#900', lw=0.6))
    ax.set_xlim(X0 - 2, X1 + 2); ax.set_ylim(Y0 - 2, Y1 + 2); ax.set_aspect('equal'); ax.grid(alpha=0.2)
    ax.set_title('C2 %s side%s - service parts in red/yellow' % (side, ' (x-ray, seen from top)' if side == 'Bottom' else ''), fontsize=11)
fig.suptitle('Where the old right-edge J_SWD header / 5021 test points / JP_WIFI_BOOT went (C2, 59.1 x 36 mm)', fontsize=13)
fig.tight_layout()
p = os.path.join(os.path.dirname(here), 'evidence', 'views', 'C2_SERVICE_PARTS_MAP.png')
os.makedirs(os.path.dirname(p), exist_ok=True)
fig.savefig(p, dpi=110)
print(p)
