"""Offline twin of a rip: remove the DEL rows (TRACK/VIA) from a native geometry export and add the ripped connections back to a
router input JSON (rebuilt from the plan rows' 'conn' field: net|endA|endB).  The same DEL rows are later written natively
with build_ops --del, so the router works on exactly the board that will exist.
usage: python apply_rip_offline.py GEOM_IN GEOM_OUT DEL.csv ROUTER_IN.json ROUTER_OUT.json"""
import csv, json, sys
gin, gout, dcsv, rin, rout = sys.argv[1:6]
rows = list(csv.DictReader(open(dcsv)))
dk = set()
for r in rows:
    if r['kind'] == 'TRACK':
        dk.add(('T', r['net'], r['layer'], frozenset(((round(float(r['x1']), 3), round(float(r['y1']), 3)), (round(float(r['x2']), 3), round(float(r['y2']), 3))))))
    else:
        dk.add(('V', r['net'], round(float(r['x1']), 3), round(float(r['y1']), 3)))
kept, n = [], 0
for l in open(gin, encoding='utf-8', errors='replace'):
    f = l.rstrip('\n').split('|')
    key = None
    if f[0] == 'TRACK' and len(f) > 7:
        key = ('T', f[2], f[1], frozenset(((round(float(f[3]), 3), round(float(f[4]), 3)), (round(float(f[5]), 3), round(float(f[6]), 3)))))
    elif f[0] == 'VIA':
        key = ('V', f[1], round(float(f[2]), 3), round(float(f[3]), 3))
    if key in dk:
        n += 1; continue
    kept.append(l)
open(gout, 'w', encoding='utf-8').writelines(kept)
data = json.load(open(rin))
conns = sorted({r['conn'] for r in rows if r.get('conn')})
for c in conns:
    net, a, b = c.split('|')
    data['details'].append(f'Un-Routed Net Constraint: Net {net} Between {a} And {b}')
data['total'] = len(data['details'])
json.dump(data, open(rout, 'w'))
print(f'removed {n} geometry lines of {len(rows)} DEL rows; added {len(conns)} connections -> {rout} ({data["total"]})')
