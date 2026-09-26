"""Make a repair.py result write-safe: run build_ops' exact check; for every dropped repair P<k> also drop its victim
re-routes (P<k>v) and keep the victims it would have deleted (their rows leave DELS); repeat until the check is clean.
usage: <build_ops env> python consistent_repair.py ADDS.csv DELS.csv OUT_ADDS.csv OUT_DELS.csv [EXTRA_PLAN.csv ...]
EXTRA_PLAN rows (e.g. plane stitches computed on the same geometry) are checked together with the repair rows."""
import csv, os, re, subprocess, sys
adds_in, dels_in, out_a, out_d = sys.argv[1:5]
extra = sys.argv[5:]
adds = list(csv.DictReader(open(adds_in)))
dels = list(csv.DictReader(open(dels_in)))
pid = lambda g: re.sub(r'v$', '', g.split(':')[0])
fields = ['kind', 'group', 'net', 'layer', 'x1', 'y1', 'x2', 'y2', 'w', 'd', 'h', 'conn', 'relax']
tmp_a, tmp_d = out_a + '.tmp.csv', out_d + '.tmp.csv'
for it in range(8):
    for p, rows in ((tmp_a, adds), (tmp_d, dels)):
        with open(p, 'w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore', restval=''); w.writeheader(); w.writerows(rows)
    r = subprocess.run([sys.executable, 'build_ops.py', tmp_a] + extra + ['--del', tmp_d, '--drop-bad', out_a + '.chk.csv'],
                       capture_output=True, text=True)
    drops = [l.split('DROP ')[1].strip() for l in r.stdout.splitlines() if l.strip().startswith('DROP ')]
    bad_del = 'delete match' in r.stdout
    print(f'iteration {it}: dropped groups {len(drops)}' + (' (delete mismatch!)' if bad_del else ''))
    if not drops:
        break
    ids = {pid(g) for g in drops if g.startswith('P')}
    victims = {r_['conn'].split('|', 1)[1].split('|', 1)[1] for r_ in adds if pid(r_['group']) in ids and r_['conn'].startswith('repair|')}
    adds = [r_ for r_ in adds if pid(r_['group']) not in ids and r_['group'] not in drops]
    dels = [r_ for r_ in dels if r_['group'] not in victims]
    # a dropped extra-plan group (stitch) is simply removed from its plan copy
    for i, p in enumerate(extra):
        rows = [r_ for r_ in csv.DictReader(open(p)) if r_['group'] not in drops]
        q = out_a.replace('.csv', f'.extra{i}.csv')
        with open(q, 'w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore', restval=''); w.writeheader(); w.writerows(rows)
        extra[i] = q
    print(f'  removed repairs {sorted(ids)}; victims kept {len(victims)}')
for p, rows in ((out_a, adds), (out_d, dels)):
    with open(p, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore', restval=''); w.writeheader(); w.writerows(rows)
print(f'final: adds {len(adds)} rows, dels {len(dels)} rows; extra plans: {extra}')
