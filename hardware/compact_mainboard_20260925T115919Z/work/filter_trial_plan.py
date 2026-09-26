"""Drop router rows made stale by the post-trial placement tweaks or superseded by the restored hot loop.
usage: python filter_trial_plan.py IN.csv OUT.csv"""
import csv, re, sys
MOVED = {'R_DRL_OUT2', 'R_DRL_SEL', 'TP_WIFI_CHIP_EN'} | {'R_DRL_V%s%d' % (s, n) for s in 'ABC' for n in range(1, 6)}
CONV = {'UP2', 'L1', 'CUP4', 'CUP4_1', 'RUP_3', 'RUP_4', 'CUP4_FB'}
rows = list(csv.DictReader(open(sys.argv[1])))
keep, dropped = [], set()
for r in rows:
    refs = set(re.findall(r'Pad ([A-Za-z0-9_\-]+?)-[A-Za-z0-9_]+\(', r['conn'])) | set(re.findall(r'Free-([A-Za-z0-9_]+)\(', r['conn']))
    if refs & MOVED or (refs and refs <= CONV):
        dropped.add(r['conn']); continue
    keep.append(r)
with open(sys.argv[2], 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(keep)
print('rows %d -> %d; connections dropped %d' % (len(rows), len(keep), len(dropped)))
for c in sorted(dropped):
    print('  ', c[:140])
