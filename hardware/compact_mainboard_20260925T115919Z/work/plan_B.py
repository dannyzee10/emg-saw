"""Offline placement planner for candidate B (4-layer, selective two-sided, 70 x 40 mm first target).

Whole functional groups move rigidly.  A group sent to Bottom is mirrored in X about its own centre
(exactly what flipping that sub-assembly through the laminate does), each member is flipped, and the group is
then translated.  Output: evidence/PLAN_B_COMPONENTS.csv (new side/x/y/rot/bbox per designator),
evidence/BOTTOM_MOVE_PLAN_DRAFT.csv, and a same-side overlap / board-edge report.  Offline planning aid only;
the native Altium move, save/reopen readback and DRC are the evidence.
usage: python plan_B.py [W H]   (board is (10,10)-(10+W,10+H), R2 corners, default 70 40)"""
import csv, math, os, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = (float(sys.argv[1]), float(sys.argv[2])) if len(sys.argv) > 2 else (70.0, 40.0)
X0, Y0 = 10.0, 10.0
X1, Y1 = X0 + W, Y0 + H
rows = {r['designator']: r for r in csv.DictReader(open(os.path.join(HERE, 'evidence', 'BASELINE_COMPONENTS.csv')))}
for r in rows.values():
    for k in ('x', 'y', 'bx0', 'by0', 'bx1', 'by1'):
        r[k] = float(r[k])

# ------------------------------------------------------------------ groups (R2 section 6)
G = {}
def grp(name, members, reason, risk):
    for m in members:
        assert m in rows, m
        assert m not in G, (m, G.get(m))
        G[m] = name
    GROUPS[name] = {'members': list(members), 'reason': reason, 'risk': risk}
GROUPS = {}
grp('PB_CTRL', ['U_EN1', 'C1_EN1', 'C2_EN1', 'C3_EN1', 'R_EN1_1', 'R_KILL_PU', 'R_INT_PULLUP', 'Q_SHDN', 'R_SHDN_PD', 'R_SHDN_G'],
    'LTC2954 pushbutton controller with its timing caps, kill/interrupt pull-ups and Q_SHDN shutdown switch (R2 s6 Bottom candidate)',
    'timing nodes kept local to U_EN1; keep away from LX/inductor on Bottom; PWR_BTN_N stays Top for actuation')
grp('GAUGE', ['UP4', 'CU6_1', 'R_AL', 'R_SDA', 'R_SCL'],
    'MAX17048 fuel gauge with CELL/VDD bypass, ALRT and I2C pull-ups (R2 s6 Bottom candidate)',
    'battery sense kept short and quiet; not beneath LX/inductor or charger thermal pad')
grp('SUPERVISOR', ['U_UV1', 'C_UV_BYPASS', 'R_EN'],
    'TPS3808 VSYS supervisor (CT open) with bypass and SYS_EN pull-up (R2 s6 Bottom candidate)',
    'sense node away from switching and clock coupling')
grp('PULLS_PWR', ['R_PGOOD', 'R_EN_PD'],
    'non-critical USB_PGOOD_N pull-up and AFE_EN pull-down (R2 s6 noncritical pulls)', 'each kept near its IC')
grp('USB_IN', ['J_USB_C', 'D_VBUS', 'C_VBUS', 'D_CC_ESD', 'RJ1', 'RJ2'], 'charge-only USB-C with VBUS/CC protection', 'Top, left edge')
grp('CHARGER', ['UP1', 'C_IN_', 'C_OUT_', 'C_BAT', 'RISET', 'R_LIM', 'R_TMR', 'R_TS_TOP', 'R_TS_BOTTOM', 'R_TS_SER', 'R_EN1_BIAS',
                'LED_CHG', 'R_CHG_LED'], 'BQ24072T charger cell with ISET/ILIM/TMR/TS network and charge LED', 'Top, coherent')
grp('CONVERTER', ['UP2', 'L1', 'CUP4', 'CUP4_1', 'RUP_3', 'RUP_4', 'CUP4_FB'], 'TPS631000 switching cell', 'Top, unchanged internally')
grp('LDO', ['UP3', 'CUP5_1', 'CUP5_2', 'CUP5_3', 'CUP5_5'], 'TPS7A2030 with its capacitors', 'Top, power/analog boundary')
grp('BUTTON', ['PWR_BTN_N'], 'pushbutton actuation', 'Top, accessible')
grp('BATTERY', ['J_Li-Po', 'R_TH_BAT'], 'battery header and remote-NTC wire termination', 'Top, wire access')
grp('WIFI', ['U_WIFI1', 'C_WIFI_VDDIO2_HF', 'C_WIFI_VDDIO2', 'C_WIFI_BULK', 'R_WIFI_CS_PD', 'R_WIFI_EN_PD', 'C_WIFI_EN', 'R_WIFI_X32_OUT',
             'R_WIFI_X32_IN', 'C_WIFI_VDDIO1_HF', 'C_WIFI_VDD33_HF', 'C_WIFI_VDDIO1', 'C_WIFI_VDD33', 'X_WIFI_32K', 'C_WIFI_X32_OUT',
             'C_WIFI_X32_IN', 'R_WIFI_BOOT_PD', 'R_SPI_MISO'], 'ST67 module, supply decoupling, 32 kHz crystal network', 'Top, antenna edge')
grp('MCU', ['U_MCU1', 'C_MCU_VDD1', 'C_MCU_VDD2', 'C_MCU_VDD3', 'C_MCU_VDD4', 'C_MCU_VDD5', 'C_VDDUSB', 'C_VBAT', 'C_MCU_BULK',
            'MCU_VCAP', 'R_NRST', 'C_NRST', 'R_MCU_BOOT0_PD', 'C1_MCU', 'C2_MCU', 'C3_MCU', 'C4_MCU', 'R_SPI_SCK', 'R_SPI_MOSI',
            'R_SPI_CS'], 'STM32U575 with VCAP/VDD/VDDA/VREF bypass, NRST, BOOT0, SPI source resistors', 'Top')
grp('ADC_RC', [f'{p}_ADC{n}' for n in range(1, 6) for p in ('R', 'C')], 'five 330R/10nF ADC input networks at the MCU pins', 'Top with MCU')
grp('SERVICE', ['J_SWD', 'JP_WIFI_BOOT', 'R_WIFI_BOOT_OVR', 'R_WIFI_UART_TX_LINK', 'R_WIFI_UART_RX_LINK', 'TP_WIFI_UART_RX',
                'TP_WIFI_UART_TX', 'TP_GND', 'TP_WIFI_BOOT', 'TP_MCU_BOOT0', 'TP_WIFI_CHIP_EN'],
    'SWD header, radio boot jumper, UART recovery links and 5021 test points', 'accessible edge')
for d, r in rows.items():
    if d not in G:
        s = r['sheet']
        name = 'AFE' if s.startswith('AFE_Channel') or s == 'Analog_Shared' else 'OTHER_' + s
        G[d] = name
        GROUPS.setdefault(name, {'members': [], 'reason': 'five AFE channels + shared references + DNP DRL provision (bottom)',
                                 'risk': 'analog feedback groups unchanged internally'})['members'].append(d)
assert not [g for g in GROUPS if g.startswith('OTHER_')], [g for g in GROUPS if g.startswith('OTHER_')]

# ------------------------------------------------------------------ transforms
# ('T', dx, dy) translate on its current side;  ('B', cx, cy) flip whole group to Bottom, mirrored about its own
# bbox centre, then place that centre at (cx, cy);  ('TR', dx, dy, members-subset override) not used.
TRANSFORM = {
    'AFE': ('T', -2.0, 0.0),
    'MCU': ('T', -2.0, 0.0),
    'ADC_RC': ('T', -2.0, 0.0),
    'WIFI': ('T', -3.0, -5.0),
    'USB_IN': ('T', 0.0, -3.6),
    'CHARGER': ('T', 0.0, -3.6),
    'CONVERTER': ('T', 0.0, -4.25),
    'LDO': ('T', -2.0, -0.8),
    'BUTTON': ('T', 0.0, -5.0),
    'BATTERY': ('T', 0.0, -2.0),
    'PB_CTRL': ('B', 70.0, 42.0),      # under the MCU: next to its KILL/INT/SHUTDOWN pins, clear of LX/L1 and the ADC corner
    'GAUGE': ('B', 22.0, 36.5),        # below the charger: short VBAT sense, clear of UP1 thermal pad and USB-C stakes
    'SUPERVISOR': ('B', 27.8, 46.2),   # under the charger/LED area, >= 2.3 mm from L1
    'PULLS_PWR': ('T', 0.0, 0.0),   # members placed individually on Bottom via overrides
    'SERVICE': ('T', 0.0, 0.0),
}
override = {}   # designator -> (x, y, rot) explicit single-part placements after group moves (filled in iterations)
if os.path.exists(os.path.join(HERE, 'work', 'plan_B_overrides.csv')):
    for r in csv.DictReader(open(os.path.join(HERE, 'work', 'plan_B_overrides.csv'))):
        override[r['designator']] = (float(r['x']), float(r['y']), r['rot'], r.get('side', ''))


def rot_swap(rot):
    return rot in ('90', '270', '90.0', '270.0')


out = {}
for g, info in GROUPS.items():
    t = TRANSFORM.get(g, ('T', 0.0, 0.0))
    mem = [rows[m] for m in info['members']]
    gx0 = min(r['bx0'] for r in mem); gx1 = max(r['bx1'] for r in mem)
    gy0 = min(r['by0'] for r in mem); gy1 = max(r['by1'] for r in mem)
    gcx, gcy = (gx0 + gx1) / 2, (gy0 + gy1) / 2
    for r in mem:
        n = dict(r)
        if t[0] == 'T':
            dx, dy = t[1], t[2]
            n['x'] += dx; n['y'] += dy
            n['bx0'] += dx; n['bx1'] += dx; n['by0'] += dy; n['by1'] += dy
        else:
            # mirror about group centre x, then move group centre to (cx, cy)
            cx, cy = t[1], t[2]
            nx = 2 * gcx - r['x']; b0 = 2 * gcx - r['bx1']; b1 = 2 * gcx - r['bx0']
            n['x'] = nx - gcx + cx; n['bx0'] = b0 - gcx + cx; n['bx1'] = b1 - gcx + cx
            n['y'] = r['y'] - gcy + cy; n['by0'] = r['by0'] - gcy + cy; n['by1'] = r['by1'] - gcy + cy
            n['side'] = 'Bottom' if r['side'] == 'Top' else 'Top'
        n['group'] = g
        out[r['designator']] = n
for d, (x, y, rot, side) in override.items():
    if d.startswith('FP:'):
        continue   # free pads are placed in their own block below
    n = out[d]; w, h = n['bx1'] - n['bx0'], n['by1'] - n['by0']
    if (not rot) or rot == n['rot']:
        # same rotation: keep the origin-to-bbox offsets (connectors often have their origin at pad 1)
        ox0, ox1, oy0, oy1 = n['bx0'] - n['x'], n['bx1'] - n['x'], n['by0'] - n['y'], n['by1'] - n['y']
        n['x'], n['y'] = x, y; n['bx0'], n['bx1'], n['by0'], n['by1'] = x + ox0, x + ox1, y + oy0, y + oy1
    else:
        if rot_swap(rot) != rot_swap(n['rot']):
            w, h = h, w
        n['x'], n['y'] = x, y; n['bx0'], n['bx1'], n['by0'], n['by1'] = x - w / 2, x + w / 2, y - h / 2, y + h / 2
    if rot:
        n['rot'] = rot
    if side:
        n['side'] = side

# ------------------------------------------------------------------ free pads (native bare test pads, not components)
FREEPAD_GROUP = {'TP_GND_ANA': 'AFE', 'TP_VREF_B_SRC': 'AFE', 'TP_VREF_A': 'AFE', 'TP_VOUT_1': 'ADC_RC', 'TP_VOUT_2': 'ADC_RC',
                 'TP_VOUT_3': 'ADC_RC', 'TP_VOUT_4': 'ADC_RC', 'TP_VOUT_5': 'ADC_RC', 'TP_3V0_ANA': 'LDO', 'TP_VSYS': 'CHARGER',
                 'TP_VBUS': 'CHARGER', 'TP_GND_DIG': 'MCU', 'TP_GND_PWR': 'BATTERY', 'TP_VBAT_CELL': 'BATTERY', 'TP_3V3_DIG': 'CONVERTER'}
HR = 0.6   # 1.0 mm round pad + 0.1 margin; copper clearance itself is checked by native DRC
for l in open(os.path.join(HERE, 'evidence', 'GEOMETRY_A_BASELINE.txt'), encoding='utf-8', errors='replace'):
    f = l.rstrip('\n').split('|')
    if f[0] == 'PAD' and f[1] == 'FREE':
        name, x, y = f[2], float(f[5]), float(f[6])
        g = FREEPAD_GROUP[name]; t = TRANSFORM.get(g, ('T', 0, 0))
        dx, dy = (t[1], t[2]) if t[0] == 'T' else (0.0, 0.0)
        d = 'FP:' + name
        base_row = {'designator': d, 'sheet': 'FREEPAD', 'footprint': 'free pad 1.0 mm', 'side': 'Top', 'x': x, 'y': y, 'rot': '0',
                    'bx0': x - HR, 'by0': y - HR, 'bx1': x + HR, 'by1': y + HR, 'w': 2 * HR, 'h': 2 * HR, 'area_mm2': 0,
                    'pads': 1, 'nets': f[3], 'src_uid': ''}
        rows[d] = base_row
        n = dict(base_row); n['x'] += dx; n['y'] += dy; n['bx0'] += dx; n['bx1'] += dx; n['by0'] += dy; n['by1'] += dy; n['group'] = 'FREEPAD_' + g
        if d in override:
            ox, oy = override[d][0], override[d][1]
            n['x'], n['y'], n['bx0'], n['bx1'], n['by0'], n['by1'] = ox, oy, ox - HR, ox + HR, oy - HR, oy + HR
        out[d] = n

# ------------------------------------------------------------------ checks
EDGE_OK ={'J_USB_C', 'U_WIFI1', 'J_SWD', 'JP_WIFI_BOOT'} | {f'J_FPC{i}' for i in range(1, 6)}   # intended edge overhang
problems = []
for d, n in out.items():
    if d in EDGE_OK:
        continue
    m = 0.1   # courtyard/pad bbox vs outline; native DRC (0.5 mm copper setback) is authoritative
    if n['bx0'] < X0 + m or n['bx1'] > X1 - m or n['by0'] < Y0 + m or n['by1'] > Y1 - m:
        problems.append(f"EDGE {d} ({n['group']}) bbox {n['bx0']:.2f},{n['by0']:.2f}-{n['bx1']:.2f},{n['by1']:.2f}")
ov = defaultdict(list)
items = list(out.values())
for i, a in enumerate(items):
    for b in items[i + 1:]:
        if a['side'] != b['side']:
            continue
        ix = min(a['bx1'], b['bx1']) - max(a['bx0'], b['bx0']); iy = min(a['by1'], b['by1']) - max(a['by0'], b['by0'])
        if ix > 0.1 and iy > 0.1:
            # pre-existing overlaps in baseline are allowed only if both parts kept the same relative position
            ra, rb = rows[a['designator']], rows[b['designator']]
            bx = min(ra['bx1'], rb['bx1']) - max(ra['bx0'], rb['bx0']); by = min(ra['by1'], rb['by1']) - max(ra['by0'], rb['by0'])
            same_move = all(abs((a[k] - ra[k]) - (b[k] - rb[k])) < 1e-6 for k in ('x', 'y')) and a['side'] == ra['side'] and b['side'] == rb['side']
            flipped_together = a['group'] == b['group'] and TRANSFORM.get(a['group'], ('T',))[0] == 'B'
            pre = ra['side'] == rb['side'] and bx > 0.05 and by > 0.05 and (same_move or flipped_together)
            if not pre:
                ov[(a['group'], b['group'])].append(f"{a['designator']}/{b['designator']} {ix:.2f}x{iy:.2f}")
# through-hole pads exist on both sides: parts on the opposite side must not sit on them
tht = []
for l in open(os.path.join(HERE, 'evidence', 'GEOMETRY_A_BASELINE.txt'), encoding='utf-8', errors='replace'):
    f = l.rstrip('\n').split('|')
    if f[0] == 'PAD' and f[4] == 'Multi Layer' and float(f[11].split('=')[1]) > 0 and f[1] in out:
        ref = f[1]; r0, n = rows[ref], out[ref]
        dx, dy = float(f[5]) - r0['x'], float(f[6]) - r0['y']
        if n['side'] != r0['side']:
            dx = -dx
        hr = max(float(f[13].split('=')[1]), float(f[14].split('=')[1])) / 2
        tht.append((ref, n['x'] + dx - hr, n['y'] + dy - hr, n['x'] + dx + hr, n['y'] + dy + hr, n['side']))
for ref, a0, b0, a1, b1, side in tht:
    for d, n in out.items():
        if d == ref or n['side'] == side:
            continue
        ix = min(a1, n['bx1']) - max(a0, n['bx0']); iy = min(b1, n['by1']) - max(b0, n['by0'])
        if ix > 0.05 and iy > 0.05:
            r0 = rows[d]
            moved = n['side'] != r0['side'] or abs(n['x'] - r0['x']) > 1e-6 or abs(n['y'] - r0['y']) > 1e-6
            if moved or ref in override:
                ov[('THT:' + out[ref]['group'], n['group'])].append(f'{ref} pad vs {d} ({n["side"]})')
print(f'board {W}x{H}  ({X0},{Y0})-({X1},{Y1})')
print('edge problems', len(problems)); [print('  ', p) for p in problems]
print('same-side overlaps (new):', sum(len(v) for v in ov.values()))
for k, v in sorted(ov.items(), key=lambda t: -len(t[1])):
    print(f'  {k[0]} x {k[1]}: {len(v)}  ' + '; '.join(v[:6]))
top = sum((n['bx1'] - n['bx0']) * (n['by1'] - n['by0']) for n in out.values() if n['side'] == 'Top')
bot = sum((n['bx1'] - n['bx0']) * (n['by1'] - n['by0']) for n in out.values() if n['side'] == 'Bottom')
area = W * H - 4 * (4 - math.pi)
print(f'top bbox area {top:.0f} mm2 ({100 * top / area:.0f}% of {area:.0f}), bottom {bot:.0f} mm2; top parts {sum(n["side"] == "Top" for n in out.values())}, bottom {sum(n["side"] == "Bottom" for n in out.values())}')
fields = list(next(iter(rows.values())).keys()) + ['group']
with open(os.path.join(HERE, 'evidence', 'PLAN_B_COMPONENTS.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
    for d in sorted(out):
        w.writerow({k: (round(v, 4) if isinstance(v, float) else v) for k, v in out[d].items() if k in fields})
with open(os.path.join(HERE, 'evidence', 'BOTTOM_MOVE_PLAN_DRAFT.csv'), 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['designator', 'src_uid', 'group', 'old_side', 'new_side', 'old_x', 'old_y', 'new_x', 'new_y', 'old_rot', 'new_rot', 'reason', 'risk'])
    for d in sorted(out):
        n, r = out[d], rows[d]
        if n['side'] != r['side'] or abs(n['x'] - r['x']) > 1e-6 or abs(n['y'] - r['y']) > 1e-6:
            w.writerow([d, r['src_uid'], n['group'], r['side'], n['side'], r['x'], r['y'], round(n['x'], 4), round(n['y'], 4), r['rot'],
                        n['rot'], GROUPS.get(n['group'], {'reason': 'native free test pad moved with its group', 'risk': 'same test node and net'})['reason'], GROUPS.get(n['group'], {'risk': 'same test node and net'})['risk']])
