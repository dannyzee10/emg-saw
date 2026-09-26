"""Trial result from Altium's own unrouted list: excluded (GND / supplies / BK13 socket pads) vs trial signal connections."""
import json, os, re, sys
from collections import Counter
EV = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'evidence')
d = json.load(open(os.path.join(EV, sys.argv[1] if len(sys.argv) > 1 else 'DRC_C2_TRIAL5.json')))['details']
exc, sig = Counter(), []
for s in d:
    m = re.match(r'Un-Routed Net Constraint: Net (\S+) Between (.*) And (.*)$', s.strip())
    if not m:
        continue
    n = m.group(1)
    if n in ('GND', '3V3_DIG', '3V0_ANA'):
        exc[n] += 1
    elif 'J_FPC' in m.group(2) or 'J_FPC' in m.group(3):
        exc['BK13 socket pad'] += 1
    else:
        sig.append((n, m.group(2), m.group(3)))
trial = json.load(open(os.path.join(EV, 'DRC_C2_TRIAL_INPUT.json')))['total']
print('unrouted total %d = excluded %d %s + trial signal %d' % (sum(exc.values()) + len(sig), sum(exc.values()), dict(exc), len(sig)))
print('trial signal connections routed: %d / %d = %.0f %%' % (trial - len(sig), trial, 100.0 * (trial - len(sig)) / trial))
cat = Counter()
for n, a, b in sig:
    c = ('DRL (DNP provision)' if n.startswith('DRL') or 'R_DRL' in a + b else
         'charger local' if n in ('TS', 'BAT_TEMP', 'NetR_TMR_2', 'NetR_EN1_BIAS_2', 'NetRISET_1', 'NetR_LIM_2', 'NetLED_CHG_C', 'NetLED_CHG_A') else
         'analog cross-side / feedback' if re.match(r'(Vservo|INA_OUT|NetCH|NetCL|NetCservo|NetINA|VOUT|VREF|VDiv|Va_|Vb_|Vc_)', n) else
         'long control / digital' if re.match(r'(I2C|FG_ALRT|MCU_|SYS_EN|USB_PGOOD|NetPWR_BTN|WIFI_|KILL|AFE_EN|NetQ_SHDN|NetC\d_EN1|MCU_SW)', n) else
         'power (VSYS/VBUS/VBAT)' if n in ('VSYS', 'VBUS', 'VBAT_CELL') else 'other')
    cat[c] += 1
for k, v in cat.most_common():
    print('  %-32s %d' % (k, v))
open(os.path.join(EV, 'C2_TRIAL_UNROUTED.txt'), 'w').write('\n'.join('%s | %s | %s' % t for t in sorted(sig)) + '\n')
