"""Check / clean a router4 ROUTE_PARTIAL csv (NUL bytes, stray rows from another writer, k order).
usage: python clean_partial.py IN.csv [OUT.csv]   -> prints stats; writes a cleaned copy if OUT is given"""
import csv, io, sys

raw = open(sys.argv[1], 'rb').read()
print('bytes', len(raw), 'NULs', raw.count(b'\x00'))
rows = list(csv.DictReader(io.StringIO(raw.replace(b'\x00', b'').decode('utf-8', 'replace'))))
good, bad = [], []
last = -1
for r in rows:
    try:
        k = int(r['group'].split(':')[0][1:])
        ok = r['kind'] in ('TRACK', 'VIA') and r['conn'] and k >= last
    except Exception:
        ok = False
    if ok:
        good.append(r); last = k
    else:
        bad.append(r)
print('rows', len(rows), 'kept', len(good), 'dropped', len(bad), 'last k', last, 'connections', len({r['conn'] for r in good}))
if len(sys.argv) > 2:
    with open(sys.argv[2], 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['kind', 'group', 'net', 'layer', 'x1', 'y1', 'x2', 'y2', 'w', 'd', 'h', 'conn'])
        w.writeheader(); w.writerows(good)
    print('written', sys.argv[2])
