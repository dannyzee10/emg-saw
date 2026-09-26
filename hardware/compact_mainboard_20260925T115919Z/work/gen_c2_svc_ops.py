"""Service-only COMP ops: after the corrected re-swap the 8 service components are new Top, rot-0 components at their
current (already planned) origin; flip/rotate/place them exactly as the audited plan says."""
import os, pickle
here = os.path.dirname(os.path.abspath(__file__))
svc = {'J_SWD', 'JP_WIFI_BOOT', 'TP_GND', 'TP_MCU_BOOT0', 'TP_WIFI_BOOT', 'TP_WIFI_CHIP_EN', 'TP_WIFI_UART_RX', 'TP_WIFI_UART_TX'}
plan = pickle.load(open(os.path.join(here, 'plan_C2.pkl'), 'rb'))['out']
lines = []
for l in open(os.path.join(here, 'C2_OPS.txt')):
    f = l.rstrip('\n').split('|')
    if f[0] == 'COMP' and f[1] in svc:
        f[3] = 'Top'
        f[4] = '1' if plan[f[1]]['side'] == 'Bottom' else '0'
        lines.append('|'.join(f))
open(os.path.join(here, 'C2_SVC_OPS.txt'), 'w').write('\n'.join(lines) + '\n')
print('\n'.join(lines))
