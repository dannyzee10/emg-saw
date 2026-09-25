"""Batch 2 ops: v1 -> v2 BK13 escape tracks, U_WIFI1-32 via relocation, tent all ordinary vias.
Reads the current native export (GEOMETRY.txt = after batch 1). Writes work/OPS.txt."""
import csv
from shapely.geometry import Point
import geom as G

objs, comps, keep = G.load()
pads = [o for o in objs if o.kind == 'PAD']
v1 = [r for r in csv.DictReader(open(G.HERE + 'evidence/BK13_ESCAPE_PLAN.csv'))]
v2 = [r for r in csv.DictReader(open(G.HERE + 'evidence/BK13_ESCAPE_PLAN_V2.csv'))]
drop = list(csv.DictReader(open(G.HERE + 'evidence/GND_FANOUT_PLAN3_DROPPED.csv')))
plan3 = list(csv.DictReader(open(G.HERE + 'evidence/GND_FANOUT_PLAN3.csv')))
newwifi = [r for r in plan3 if r['group'] == 'U_WIFI1-32']
assert sorted((r['net'], r['x1'], r['y1']) for r in v1 if r['kind'] == 'VIA') == sorted((r['net'], r['x1'], r['y1']) for r in v2 if r['kind'] == 'VIA'), 'BK13 vias moved'
out = []
for r in v1:
    if r['kind'] == 'TRACK':
        out.append(f"DEL_TRACK|{r['net']}|{r['layer']}|{r['x1']}|{r['y1']}|{r['x2']}|{r['y2']}")
for r in drop:
    if r['kind'] == 'TRACK':
        out.append(f"DEL_TRACK|{r['net']}|{r['layer']}|{r['x1']}|{r['y1']}|{r['x2']}|{r['y2']}")
    else:
        out.append(f"DEL_VIA|{r['net']}|{r['x1']}|{r['y1']}")
for r in v2:
    if r['kind'] == 'TRACK':
        out.append(f"TRACK|{r['net']}|{r['layer']}|{r['x1']}|{r['y1']}|{r['x2']}|{r['y2']}|{r['w']}")
for r in newwifi:
    if r['kind'] == 'TRACK':
        out.append(f"TRACK|{r['net']}|{r['layer']}|{r['x1']}|{r['y1']}|{r['x2']}|{r['y2']}|{r['w']}")
    else:
        out.append(f"VIA|{r['net']}|{r['x1']}|{r['y1']}|{r['d']}|{r['h']}|T")
# tent every existing via that is not inside pad copper (EP/thermal vias keep their treatment)
dropped_vias = {(round(float(r['x1']), 4), round(float(r['y1']), 4)) for r in drop if r['kind'] == 'VIA'}
n_skip = 0
for o in objs:
    if o.kind != 'VIA':
        continue
    c = o.geom.centroid
    key = (round(float(o.src[2]), 4), round(float(o.src[3]), 4))
    if key in dropped_vias:
        continue
    if any(p.geom.contains(c) for p in pads):
        n_skip += 1
        continue
    out.append(f"TENT_VIA|{o.src[2]}|{o.src[3]}|1|1")
open(G.HERE + 'work/OPS.txt', 'w').write('\n'.join(out) + '\n')
from collections import Counter
print(Counter(l.split('|')[0] for l in out), 'EP/in-pad vias left as-is:', n_skip)
