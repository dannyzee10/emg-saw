"""Scan two geometry exports with clearance_scan's model and print only the findings that are NEW in the second one
(pre-existing hand-placed escapes etc. cancel out).  usage: BK13_ZONES=... python clearance_diff.py OLD_GEOM NEW_GEOM"""
import os, subprocess, sys, json

code = r'''
import json, geom as G
objs, comps, keepouts = G.load()
EX = G.Index(objs)
out, seen = [], set()
for o in objs:
    if o.kind not in ('TRACK', 'VIA'):
        continue
    for other, d, req in EX.violations(o):
        k = tuple(sorted((id(o), id(other))))
        if k in seen:
            continue
        seen.add(k)
        a, b = o.geom.centroid, other.geom.centroid
        out.append([o.kind, o.net, sorted(o.layers)[0] if o.layers else '', round(a.x, 2), round(a.y, 2),
                    other.kind, other.net, other.comp, other.name, round(b.x, 2), round(b.y, 2), round(d, 3), req])
print(json.dumps(out))
'''
res = {}
for tag, g in (('old', sys.argv[1]), ('new', sys.argv[2])):
    env = dict(os.environ, GEOM_FILE=g)
    r = subprocess.run([sys.executable, '-c', code], env=env, capture_output=True, text=True)
    res[tag] = json.loads(r.stdout.strip().splitlines()[-1])
key = lambda v: (v[0], v[1], v[2], v[3], v[4], v[5], v[6], v[9], v[10])
old = {key(v) for v in res['old']}
new = [v for v in res['new'] if key(v) not in old]
print(f"old {len(res['old'])} findings, new state {len(res['new'])}; NEW in the second state: {len(new)}")
for v in sorted(new, key=lambda v: v[11] - v[12]):
    print('  ', v)
