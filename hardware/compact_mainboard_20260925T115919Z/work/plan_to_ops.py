"""Router-format plan CSV -> apply_ops_T ops (TRACK|net|layer|x1|y1|x2|y2|w, VIA|net|x|y|d|h).
usage: python plan_to_ops.py plan.csv OUT_OPS.txt"""
import csv, sys
rows = list(csv.DictReader(open(sys.argv[1])))
ops = []
for r in rows:
    if r['kind'] == 'TRACK':
        ops.append('TRACK|%s|%s|%s|%s|%s|%s|%s' % (r['net'], r['layer'], r['x1'], r['y1'], r['x2'], r['y2'], r['w']))
    elif r['kind'] == 'VIA':
        ops.append('VIA|%s|%s|%s|%s|%s' % (r['net'], r['x1'], r['y1'], r['d'], r['h']))
open(sys.argv[2], 'w').write('\n'.join(ops) + '\n')
print(len(ops), 'ops ->', sys.argv[2])
