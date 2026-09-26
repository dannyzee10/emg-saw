"""C2 evidence tables from the SAVED NATIVE state (GEOMETRY_C2_PLACED.txt, BODIES_C2_PLACED.txt) and candidate B:
  C2_COMPONENT_LEDGER.csv, C2_TOP_INVENTORY.csv, C2_BOTTOM_INVENTORY.csv, C2_SUMMARY.txt"""
import csv, os
from c2lib import load_b, EV
B = load_b()
comps = {}
for l in open(os.path.join(EV, 'GEOMETRY_C2_PLACED.txt'), encoding='utf-8', errors='replace'):
    f = l.rstrip('\n').split('|')
    if f[0] == 'COMP':
        comps[f[1]] = ('Bottom' if f[2].startswith('Bottom') else 'Top', float(f[3]), float(f[4]), float(f[5]))
h = {}
for l in open(os.path.join(EV, 'BODIES_C2_PLACED.txt'), encoding='utf-8', errors='replace'):
    f = l.rstrip('\n').split('|')
    if f[0] == 'BODYC':
        kv = dict(p.split('=', 1) for p in f[3:] if '=' in p)
        h[f[1]] = float(kv.get('HMAX', 0) or 0)
SERVICE = {'J_SWD': 'EMG_TC2030_NL', 'JP_WIFI_BOOT': 'EMG_SJ_2P_NO'}
STAGE1 = ('J_FPC', 'INA', 'RDD', 'CCU', 'RH_', 'RL_')
STAGE2 = ('U1', 'U2', 'U3', 'Cservo', 'Rservo', 'RG_', 'CH_', 'RGN_', 'CL_', 'CU_')


def reason(d, side):
    g = B[d]['group']
    if d.startswith('TP_') or d in SERVICE:
        return 'approved service change: flat footprint (Tag-Connect / probe pad / solder jumper), Not Fitted in PROTO_1_REMOTE_NTC'
    if g == 'AFE':
        if d.startswith(STAGE1) and side == 'Top':
            return 'channel input stage: B template translated to the 10.8 mm BK13 pitch (Top, unchanged internally)'
        if d.startswith(STAGE2):
            return 'op-amp package-aware group on Bottom directly under its channels (servo/post-amp at their pins)'
        if d.startswith(('R_DRL', 'C_DRL', 'U_DRL')):
            return 'DNP DRL provision kept physically, Bottom under the sockets / J_REF'
        if d.startswith(('RV', 'Cdiv', 'R_ref')):
            return 'reference divider/filter beside U1 VREF-buffer pins (Bottom); R_ref by J_REF'
        return 'analog shared reference/branch parts in the analog band'
    return {'WIFI': 'ST67 block: B local layout, rigid translation (antenna edge)',
            'MCU': 'STM32 block: B local layout incl. ADC/VCAP/bypass, rigid translation',
            'ADC_RC': 'ADC RC networks: rigid with the STM32 block',
            'USB_IN': 'USB-C + protection: rigid, left edge',
            'CHARGER': 'charger cell on Bottom; UP1 exposed-pad vias under the grounded USB-C shell',
            'CONVERTER': 'TPS631000 cell flipped whole (B hot loop) under the STM32, clear of ST67 vias/crystal/antenna/ADC corner',
            'LDO': 'TPS7A2030 cell flipped whole to the power/analog boundary',
            'GAUGE': 'fuel gauge (Bottom) near the battery header',
            'SUPERVISOR': 'supervisor (Bottom) beside the converter',
            'PB_CTRL': 'pushbutton controller (Bottom) under the STM32, rigid with it',
            'PULLS_PWR': 'noncritical pull at its IC (Bottom)',
            'BUTTON': 'button (Top) below USB-C',
            'BATTERY': 'battery header + remote-NTC terminals in the service column (Top)',
            'SERVICE': 'UART link / boot override beside the ST67 pins (Bottom)'}.get(g, g)


rows = []
for d in sorted(comps):
    s, x, y, r = comps[d]; b = B[d]
    rows.append({'designator': d, 'src_uid': b['src_uid'], 'group': b['group'], 'sheet': b['sheet'],
                 'b_side': b['side'], 'b_x': round(b['x'], 4), 'b_y': round(b['y'], 4), 'b_rot': round(b['rot'], 3),
                 'c2_side': s, 'c2_x': x, 'c2_y': y, 'c2_rot': r, 'side_changed': 'Y' if s != b['side'] else '',
                 'footprint': SERVICE.get(d, 'EMG_TP_FLAT_1R2' if d.startswith('TP_') else b['footprint']),
                 'footprint_changed': 'Y' if (d in SERVICE or d.startswith('TP_')) else '', 'height_mm': h.get(d, ''), 'reason': reason(d, s)})
with open(os.path.join(EV, 'C2_COMPONENT_LEDGER.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
for side in ('Top', 'Bottom'):
    with open(os.path.join(EV, 'C2_%s_INVENTORY.csv' % side.upper()), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['designator', 'footprint', 'x', 'y', 'rot', 'height_mm', 'group'])
        for r in rows:
            if r['c2_side'] == side:
                w.writerow([r['designator'], r['footprint'], r['c2_x'], r['c2_y'], r['c2_rot'], r['height_mm'], r['group']])
top = [r for r in rows if r['c2_side'] == 'Top']; bot = [r for r in rows if r['c2_side'] == 'Bottom']
summary = ['C2 summary (saved native state)',
           'components %d: top %d, bottom %d; side changed vs B %d; footprints changed %d' % (
               len(rows), len(top), len(bot), sum(r['side_changed'] == 'Y' for r in rows), sum(r['footprint_changed'] == 'Y' for r in rows)),
           'max height top %.2f mm (%s), bottom %.2f mm' % (max(float(r['height_mm'] or 0) for r in top),
                                                             max(top, key=lambda r: float(r['height_mm'] or 0))['designator'],
                                                             max(float(r['height_mm'] or 0) for r in bot))]
open(os.path.join(EV, 'C2_SUMMARY.txt'), 'w').write('\n'.join(summary) + '\n')
print('\n'.join(summary))
