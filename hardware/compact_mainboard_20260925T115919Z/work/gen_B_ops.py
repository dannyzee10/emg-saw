"""Generate work/B_OPS.txt for apply_B.pas from the verified plan (PLAN_B_COMPONENTS.csv, COPPER_PLAN.csv,
native baseline geometry and the checkpoint's saved rules).  Ops (pipe separated):
  COMP|ref|srcuid|old_side|flip(0/1)|x|y|setrot(0/1)|rot
  TMOVE|net|layer|x1|y1|x2|y2|dx|dy        TDEL|net|layer|x1|y1|x2|y2
  VMOVE|net|x|y|dx|dy                      VDEL|net|x|y
  MMOVE|layer|x1|y1|x2|y2|dx|dy            MDEL|layer|x1|y1|x2|y2      (free mechanical tracks)
  KMOVE|x0|y0|x1|y1|dx|dy                  (free keep-out region, located by its bbox)
  RULE|name|scope(1/2)|new expression      (InRegionAbsolute translated by the owning group's vector, mils)
  OUTLINE|W|H                              POLY|name|x0|y0|x1|y1
Also writes evidence/B_OPS_SUMMARY.txt."""
import csv, math, os, re, sys
from collections import Counter, defaultdict
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EV = os.path.join(HERE, 'evidence')
W, H = 75.0, 40.0
MIL = 1 / 0.0254
plan = {r['designator']: r for r in csv.DictReader(open(os.path.join(EV, 'PLAN_B_COMPONENTS.csv')))}
base = {r['designator']: r for r in csv.DictReader(open(os.path.join(EV, 'BASELINE_COMPONENTS.csv')))}
over = {r['designator']: r for r in csv.DictReader(open(os.path.join(HERE, 'work', 'plan_B_overrides.csv')))}
ops, summ = [], Counter()

def gvec(ref):
    """translation vector of a component that stays on its side, else None"""
    p, b = plan[ref], base[ref]
    if p['side'] != b['side']:
        return None
    return (float(p['x']) - float(b['x']), float(p['y']) - float(b['y']))

# ---- components
for ref in sorted(plan):
    p, b = plan[ref], base[ref]
    flip = int(p['side'] != b['side'])
    moved = flip or abs(float(p['x']) - float(b['x'])) > 1e-6 or abs(float(p['y']) - float(b['y'])) > 1e-6 or p['rot'] != b['rot']
    if not moved:
        summ['COMP unchanged'] += 1
        continue
    setrot = int((not flip) and p['rot'] != b['rot'])
    ops.append(f"COMP|{ref}|{b['src_uid']}|{b['side']}|{flip}|{float(p['x']):.4f}|{float(p['y']):.4f}|{setrot}|{p['rot']}")
    summ['COMP flip' if flip else ('COMP move+rot' if setrot else 'COMP move')] += 1

# ---- free copper
for r in csv.DictReader(open(os.path.join(EV, 'COPPER_PLAN.csv'))):
    if r['action'] == 'KEEP':
        summ[r['kind'] + ' keep'] += 1; continue
    if r['kind'] == 'TRACK':
        if r['action'] == 'MOVE':
            ops.append(f"TMOVE|{r['net']}|{r['layer']}|{r['x1']}|{r['y1']}|{r['x2']}|{r['y2']}|{r['dx']}|{r['dy']}")
        else:
            ops.append(f"TDEL|{r['net']}|{r['layer']}|{r['x1']}|{r['y1']}|{r['x2']}|{r['y2']}")
    elif r['kind'] == 'VIA':
        if r['action'] == 'MOVE':
            ops.append(f"VMOVE|{r['net']}|{r['x1']}|{r['y1']}|{r['dx']}|{r['dy']}")
        else:
            ops.append(f"VDEL|{r['net']}|{r['x1']}|{r['y1']}")
    summ[f"{r['kind']} {r['action']}"] += 1

# ---- free mechanical tracks (Mech 5 assembly leaders from component origins; Mech 4 BK13 flex-exit lines)
origins = {ref: (float(b['x']), float(b['y'])) for ref, b in base.items()}
for l in open(os.path.join(EV, 'GEOMETRY_A_BASELINE.txt'), encoding='utf-8', errors='replace'):
    f = l.rstrip('\n').split('|')
    if f[0] != 'TRACK' or not f[1].startswith('Mechanical') or 'INCOMP=False' not in f:
        continue
    x1, y1, x2, y2 = map(float, f[3:7])
    owner = None
    if f[1] == 'Mechanical Layer 4':
        cand = [r for r in (f'J_FPC{i}' for i in range(1, 6))]
        owner = min(cand, key=lambda r: abs(origins[r][0] - x1))
    else:
        for ref, (ox, oy) in origins.items():
            if math.dist((ox, oy), (x1, y1)) < 0.06 or math.dist((ox, oy), (x2, y2)) < 0.06:
                owner = ref; break
    v = gvec(owner) if owner else None
    if owner and v is not None and plan[owner]['rot'] == base[owner]['rot']:
        if abs(v[0]) > 1e-9 or abs(v[1]) > 1e-9:
            ops.append(f"MMOVE|{f[1]}|{f[3]}|{f[4]}|{f[5]}|{f[6]}|{v[0]:.4f}|{v[1]:.4f}")
            summ['MECH move'] += 1
        else:
            summ['MECH keep'] += 1
    else:
        ops.append(f"MDEL|{f[1]}|{f[3]}|{f[4]}|{f[5]}|{f[6]}")
        summ['MECH delete (owner flipped/rotated/unknown)'] += 1

# ---- antenna keep-out moves with the radio
wv = gvec('U_WIFI1')
ops.append(f"KMOVE|44.19|54.44|56.47|59.44|{wv[0]:.4f}|{wv[1]:.4f}")
summ['KEEPOUT move'] += 1

# ---- region-scoped rules
RULES = r'C:\Users\PMLS\Desktop\emg-saw\hardware\pcb_layout_2026-09-23_drl\evidence\NATIVE_FINAL_20260924T015854610Z\RULES.txt'
pat = re.compile(r'InRegionAbsolute\(([-\d.]+),([-\d.]+),([-\d.]+),([-\d.]+)\)')
for l in open(RULES, encoding='utf-8', errors='replace'):
    f = l.rstrip('\n').split('|')
    if f[0] != 'RULE' or 'InRegionAbsolute' not in l:
        continue
    name = f[1]
    sc = {k: v for k, v in (x.split('=', 1) for x in f if x.startswith('SCOPE'))}
    refs = re.findall(r"Name = '([A-Za-z0-9_]+)-", l) + re.findall(r"InComponent\('([A-Za-z0-9_]+)'\)", l)
    owner = next((r for r in refs if r in plan), None)
    if owner is None:   # track-track rules: owner = component whose baseline bbox contains the region centre
        m = pat.search(l); cx = (float(m.group(1)) + float(m.group(3))) / 2 / MIL; cy = (float(m.group(2)) + float(m.group(4))) / 2 / MIL
        inside = [r for r, b in base.items() if float(b['bx0']) - 1 <= cx <= float(b['bx1']) + 1 and float(b['by0']) - 1 <= cy <= float(b['by1']) + 1]
        owner = min(inside, key=lambda r: math.dist((cx, cy), (float(base[r]['x']), float(base[r]['y'])))) if inside else None
    v = gvec(owner) if owner else None
    if v is None:
        summ['RULE unresolved'] += 1; print('UNRESOLVED RULE', name, owner); continue
    for key, idx in (('SCOPE1', 1), ('SCOPE2', 2)):
        e = sc.get(key, '')
        if 'InRegionAbsolute' not in e:
            continue
        ne = pat.sub(lambda m: 'InRegionAbsolute(%.6f,%.6f,%.6f,%.6f)' % (float(m.group(1)) + v[0] * MIL, float(m.group(2)) + v[1] * MIL,
                                                                        float(m.group(3)) + v[0] * MIL, float(m.group(4)) + v[1] * MIL), e)
        ops.append(f"RULE|{name}|{idx}|{ne}")
    summ[f'RULE translate ({plan[owner].get("group", "")})'] += 1

# ---- outline + polygons
ops.append(f"OUTLINE|{W}|{H}")
for pname in ('EMG_L2_COMMON_GND', 'EMG_L4_COMMON_GND'):
    ops.append(f"POLY|{pname}|10.5|10.5|{10 + W - 0.5}|{10 + H - 0.5}")
# merge near-duplicate copper/mechanical ops (same object type, net, layer, coordinates within 2 um): one op with a
# count; the writer then requires exactly that many native matches and moves/deletes all of them once
def ckey(op):
    f = op.split('|')
    if f[0] in ('TMOVE', 'TDEL', 'MMOVE', 'MDEL'):
        k = 3 if f[0][0] == 'T' else 2
        return (f[0], f[1], f[2] if f[0][0] == 'T' else '') + tuple(round(float(x) / 0.004) for x in f[k:k + 4])
    if f[0] in ('VMOVE', 'VDEL'):
        return (f[0], f[1]) + tuple(round(float(x) / 0.004) for x in f[2:4])
    return None
merged, seen = [], {}
for op in ops:
    k = ckey(op)
    if k is None:
        merged.append(op); continue
    if k in seen:
        seen[k][1] += 1; summ['near-duplicate merged'] += 1; continue
    seen[k] = [len(merged), 1]; merged.append(op)
for k, (i, n) in seen.items():
    merged[i] = merged[i] + f'|N={n}'
ops = merged
open(os.path.join(HERE, 'work', 'B_OPS.txt'), 'w').write('\n'.join(ops) + '\n')
txt = '\n'.join(f'{k}: {v}' for k, v in sorted(summ.items()))
open(os.path.join(EV, 'B_OPS_SUMMARY.txt'), 'w').write(txt + f'\nTOTAL OPS {len(ops)}\n')
print(txt); print('TOTAL OPS', len(ops))
