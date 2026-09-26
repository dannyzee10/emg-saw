"""Self-test of c2lib against native truth: rebuild B's flipped/translated groups from baseline A and compare every pad
with B's saved native geometry (GEOMETRY_B_PLACED.txt = state right after the native placement write)."""
import sys
from c2lib import load_b, group_transform, place

A = load_b('BASELINE_COMPONENTS.csv', 'GEOMETRY_A_BASELINE.txt')
B = load_b('PLAN_B_COMPONENTS.csv', 'GEOMETRY_B_PLACED.txt')
GROUPS = {
    'PB_CTRL': (['U_EN1', 'C1_EN1', 'C2_EN1', 'C3_EN1', 'R_EN1_1', 'R_KILL_PU', 'R_INT_PULLUP', 'Q_SHDN', 'R_SHDN_PD', 'R_SHDN_G'], ('F', 70.0, 42.0)),
    'GAUGE': (['UP4', 'CU6_1', 'R_AL', 'R_SDA', 'R_SCL'], ('F', 22.0, 36.5)),
    'SUPERVISOR': (['U_UV1', 'C_UV_BYPASS', 'R_EN'], ('F', 27.8, 46.2)),
    'MCU': (['U_MCU1', 'C_MCU_VDD1', 'MCU_VCAP', 'C_NRST'], ('T', -2.0, 0.0)),
}
worst = 0.0; n = 0
for g, (mem, t) in GROUPS.items():
    out = group_transform(A, mem, *t)
    for d, rec in out.items():
        bp = {(q['num']): q for q in B[d]['pads']}
        for q in rec['pads']:
            b = bp[q['num']]
            e = max(abs(q['x'] - b['x']), abs(q['y'] - b['y']))
            worst = max(worst, e); n += 1
            if e > 0.005 or q['layer'] != b['layer']:
                print('MISMATCH', g, d, q['num'], round(q['x'], 4), round(q['y'], 4), q['layer'], 'native', b['x'], b['y'], b['layer'])
        if abs((rec['rot'] - B[d]['rot']) % 360) > 0.01 and d not in ('R_PGOOD',):
            print('ROT', d, rec['rot'], 'native', B[d]['rot'])
print('pads compared', n, 'worst error mm', round(worst, 5))
