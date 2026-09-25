"""Compare the native post-save/reopen READBACK lines of an apply_B log with PLAN_B_COMPONENTS.csv.
usage: python compare_readback.py LOG.txt   -> prints mismatches (side / x / y beyond 2 um / uid) and a summary."""
import csv, os, sys
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
plan = {r['designator']: r for r in csv.DictReader(open(os.path.join(HERE, 'evidence', 'PLAN_B_COMPONENTS.csv')))}
seen, bad = set(), []
for l in open(sys.argv[1], encoding='utf-8', errors='replace'):
    if not l.startswith('READBACK|'):
        continue
    f = l.rstrip('\n').split('|')
    ref = f[1]; side = 'Bottom' if f[2].startswith('Bottom') else 'Top'
    kv = {x.split('=', 1)[0]: x.split('=', 1)[1] for x in f[3:] if '=' in x}
    seen.add(ref)
    p = plan.get(ref)
    if p is None:
        bad.append(f'{ref}: not in plan'); continue
    if side != p['side']:
        bad.append(f'{ref}: side {side} != plan {p["side"]}')
    if abs(float(kv['X']) - float(p['x'])) > 0.002 or abs(float(kv['Y']) - float(p['y'])) > 0.002:
        bad.append(f'{ref}: xy ({kv["X"]},{kv["Y"]}) != plan ({float(p["x"]):.4f},{float(p["y"]):.4f})')
    if kv.get('UID') != p['src_uid']:
        bad.append(f'{ref}: uid {kv.get("UID")} != {p["src_uid"]}')
missing = sorted(set(plan) - seen)
print(f'readback components {len(seen)} / plan {len(plan)}; missing {len(missing)} {missing[:10]}; mismatches {len(bad)}')
for b in bad[:40]:
    print('  ', b)
print('TOP', sum(1 for r in plan.values() if r['side'] == 'Top'), 'BOTTOM', sum(1 for r in plan.values() if r['side'] == 'Bottom'))
