"""Generate the R2 evidence tables for candidate B from the saved native exports (no Altium needed).
Inputs (evidence/): GEOMETRY_A_BASELINE.txt, GEOMETRY_B_TRIAL.txt (native, after placement + trial routes),
BODIES_EXPORT.txt of A (BODIES_A = first export, top-only layers) and BODIES_B_PLACED.txt (all layers),
PLAN_B_COMPONENTS.csv, BASELINE_COMPONENTS.csv, APPLY_B_LOG.txt, DRC_*.json, B_OPS_SUMMARY.txt.
Outputs: BOTTOM_MOVE_PLAN.csv, COMPONENT_MOVE_LEDGER.csv, BASELINE_VS_COMPACT.csv, TOP_INVENTORY_B.csv,
BOTTOM_INVENTORY_B.csv, BOARD_PARTITION_MANIFEST.csv."""
import csv, json, math, os
from collections import Counter, defaultdict
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EV = os.path.join(HERE, 'evidence')
P = lambda n: os.path.join(EV, n)

def comps(fn):
    out = {}
    for l in open(fn, encoding='utf-8', errors='replace'):
        f = l.rstrip('\n').split('|')
        if f[0] == 'COMP':
            out[f[1]] = {'side': 'Bottom' if f[2].startswith('Bottom') else 'Top', 'x': float(f[3]), 'y': float(f[4]), 'rot': f[5],
                         'bbox': tuple(map(float, f[6:10]))}
    return out
def bodies(fn):
    out = {}
    for l in open(fn, encoding='utf-8', errors='replace'):
        if l.startswith('BODYC|'):
            f = l.rstrip('\n').split('|'); kv = {x.split('=', 1)[0]: x.split('=', 1)[1] for x in f[3:] if '=' in x}
            out[f[1]] = (int(kv['BODIES']), float(kv['HMAX']))
    return out
A, B = comps(P('GEOMETRY_A_BASELINE.txt')), comps(P('GEOMETRY_B_TRIAL.txt'))
HB = bodies(P('BODIES_B_PLACED.txt'))
plan = {r['designator']: r for r in csv.DictReader(open(P('PLAN_B_COMPONENTS.csv')))}
base = {r['designator']: r for r in csv.DictReader(open(P('BASELINE_COMPONENTS.csv')))}
GROUP_WHY = {
    'PB_CTRL': ('LTC2954 pushbutton controller + timing/kill/interrupt network + Q_SHDN (R2 s6 Bottom candidate)',
                'under MCU: short to MCU KILL/INT/SHUTDOWN pins, clear of LX/L1 and ADC corner; button line and SYS_EN become long (~37-39 mm)'),
    'GAUGE': ('MAX17048 + CELL bypass + ALRT/I2C pull-ups (R2 s6 Bottom candidate)', 'below charger, short VBAT sense; clear of UP1 thermal vias and USB-C stakes'),
    'SUPERVISOR': ('TPS3808 + bypass + SYS_EN pull-up (R2 s6 Bottom candidate)', 'under charger/LED area, >= 2.3 mm from L1; not under LX'),
    'PULLS_PWR': ('non-critical pull (R2 s6)', 'placed under its own IC'),
    'WIFI': ('DNP 47 uF radio bulk provision', 'kept at radio supply entry; not in antenna zone'),
    'SERVICE': ('non-critical jumper pull-up', 'beside JP_WIFI_BOOT'),
}
# ---- bottom move plan (side changes) + full ledger
with open(P('BOTTOM_MOVE_PLAN.csv'), 'w', newline='') as fb, open(P('COMPONENT_MOVE_LEDGER.csv'), 'w', newline='') as fl:
    wb, wl = csv.writer(fb), csv.writer(fl)
    hdr = ['designator', 'src_uid', 'group', 'old_side', 'new_side', 'old_x', 'old_y', 'new_x', 'new_y', 'old_rot', 'new_rot',
           'model_height_mm', 'reason', 'risk', 'verification']
    wb.writerow(hdr); wl.writerow(hdr)
    for d in sorted(A):
        a, b = A[d], B[d]; g = plan[d].get('group', '')
        ok = (b['side'] == plan[d]['side'] and abs(b['x'] - float(plan[d]['x'])) < 0.002 and abs(b['y'] - float(plan[d]['y'])) < 0.002)
        ver = ('native save/reopen readback matches plan; pad-net map unchanged' if ok else 'MISMATCH vs plan')
        why, risk = GROUP_WHY.get(g, ('group translated rigidly with its functional block', 'internal geometry of the block unchanged'))
        row = [d, base[d]['src_uid'], g, a['side'], b['side'], a['x'], a['y'], b['x'], b['y'], a['rot'], b['rot'],
               HB.get(d, (0, 0))[1] if HB.get(d, (0, 0))[0] else 'no 3D body', why, risk, ver]
        moved = a['side'] != b['side'] or abs(a['x'] - b['x']) > 1e-6 or abs(a['y'] - b['y']) > 1e-6 or a['rot'] != b['rot']
        if moved:
            wl.writerow(row)
        if a['side'] != b['side']:
            wb.writerow(row)
# ---- inventories
for side in ('Top', 'Bottom'):
    with open(P(f'{side.upper()}_INVENTORY_B.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['designator', 'sheet', 'footprint', 'x', 'y', 'rot', 'model_height_mm', 'src_uid'])
        for d in sorted(B):
            if B[d]['side'] == side:
                w.writerow([d, base[d]['sheet'], base[d]['footprint'], B[d]['x'], B[d]['y'], B[d]['rot'],
                            HB.get(d, (0, 0))[1] if HB.get(d, (0, 0))[0] else 'no 3D body', base[d]['src_uid']])
with open(P('BOARD_PARTITION_MANIFEST.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['sheet', 'components', 'top_A', 'bottom_A', 'top_B', 'bottom_B'])
    by = defaultdict(list)
    for d in base:
        by[base[d]['sheet']].append(d)
    for s, ds in sorted(by.items()):
        w.writerow([s, len(ds), sum(A[d]['side'] == 'Top' for d in ds), sum(A[d]['side'] == 'Bottom' for d in ds),
                    sum(B[d]['side'] == 'Top' for d in ds), sum(B[d]['side'] == 'Bottom' for d in ds)])
# ---- comparison metrics
def env(C):
    xs = [v for c in C.values() for v in (c['bbox'][0], c['bbox'][2])]; ys = [v for c in C.values() for v in (c['bbox'][1], c['bbox'][3])]
    return min(xs), min(ys), max(xs), max(ys)
ea, eb = env(A), env(B)
area_a, area_b = 80 * 45 - 4 * (4 - math.pi), 75 * 40 - 4 * (4 - math.pi)
def drc(fn):
    d = json.load(open(P(fn)))['details']; c = Counter(x.split(':')[0] for x in d); return c
da, db = None, drc('DRC_B_CHECKPOINT.json')
hb_top = max(h for d, (n, h) in HB.items() if n and B[d]['side'] == 'Top')
hb_bot = max(h for d, (n, h) in HB.items() if n and B[d]['side'] == 'Bottom')
rows = [
    ('board bounding box', 'mm', '80.0 x 45.0', '75.0 x 40.0', 'native BoardOutline readback (APPLY_B_LOG READBACK_OUTLINE)'),
    ('board polygon area', 'mm2', f'{area_a:.1f}', f'{area_b:.1f}', 'native outline: rectangle minus 4 x r=2 mm corner areas'),
    ('area reduction vs measured baseline', '%', '-', f'{100 * (area_a - area_b) / area_a:.1f}', '(A - B) / A'),
    ('area reduction vs 70 x 40 first target', '-', '-', '75 x 40 reached; 70 x 40 not reached', 'limiting objects: J_SWD edge header, 6 THT 5021 test points, JP_WIFI_BOOT (see audit)'),
    ('installed XY envelope (all component bboxes incl. overhangs)', 'mm',
     f'{ea[2] - ea[0]:.1f} x {ea[3] - ea[1]:.1f}', f'{eb[2] - eb[0]:.1f} x {eb[3] - eb[1]:.1f}',
     'native component bounding rectangles; includes USB-C, J_SWD and ST67 antenna overhang, not mated flex/cable envelopes'),
    ('components top / bottom', 'count', f"{sum(c['side'] == 'Top' for c in A.values())} / {sum(c['side'] == 'Bottom' for c in A.values())}",
     f"{sum(c['side'] == 'Top' for c in B.values())} / {sum(c['side'] == 'Bottom' for c in B.values())}", 'native component layer'),
    ('components moved to Bottom in B', 'count', '-', str(sum(A[d]['side'] != B[d]['side'] for d in A)), 'BOTTOM_MOVE_PLAN.csv'),
    ('max model height Top', 'mm', '5.08', f'{hb_top:.2f}', '3D body OverallHeight as stored (5021 test points); verify vs datasheets'),
    ('max model height Bottom', 'mm', '1.45 (DNP U_DRL1)', f'{hb_bot:.2f}', '3D bodies on Mechanical 23 (Bottom 3D Body)'),
    ('parts without 3D body', 'count', '45', str(sum(1 for d in B if not HB.get(d, (0, 0))[0])), 'explicit list in BODIES_B_PLACED.txt'),
    ('stack', '-', 'JLC04121H-3313 4L', 'unchanged 4L (L1 sig/parts, L2 GND, L3 power+signal, L4 GND+Bottom parts)', 'STACK.txt; option A of R2 s8'),
    ('electrical preservation (pad-net per component, nets, free pads)', '-', 'reference', 'PASS 231/231 comps, 791 pads, 136 nets, 15 free pads', 'compare_pads.py A vs B'),
    ('DRC shorts / clearance / component clearance', 'count', '0 / 0 / 0 (drl DRC07)', f"{db['Short-Circuit Constraint']} / {db['Clearance Constraint']} / {db['Component Clearance Constraint']}", 'native batch DRC_B_CHECKPOINT'),
    ('DRC unrouted connections', 'count', '510 (drl placement checkpoint)', str(db['Un-Routed Net Constraint']), 'placement checkpoint; 37 trial connections routed in B'),
    ('DRC silkscreen (silk-mask / silk-silk / text-edge)', 'count', '0 / 0 / 0',
     f"{db['Silk To Solder Mask Clearance Constraint']} / {db['Silk To Silk Clearance Constraint']} / {db['Board Outline Clearance(Outline Edge)']}", 'open: legibility pass'),
    ('limited routing trial', 'connections', '-', '37 of 50 routed (147 tracks, 33 vias), 13 open', 'ROUTE_PLAN_TRIAL.csv, ROUTE_FAILED_TRIAL.txt'),
]
with open(P('BASELINE_VS_COMPACT.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['metric', 'unit', 'baseline_A', 'candidate_B', 'method']); w.writerows(rows)
for r in rows:
    print(' | '.join(map(str, r)))
