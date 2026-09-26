"""Merge plan CSVs, verify ALL new copper together, emit work/OPS.txt for apply_ops.pas.

usage: python build_ops.py plan1.csv [plan2.csv ...] [--rules bk13] [--del del.csv] [--drop-bad OUT.csv]
Refuses to write OPS.txt if any check fails.  --drop-bad instead writes OUT.csv = the plan minus every
connection (group) involved in a problem, lists the dropped groups, and exits without writing OPS.txt.
"""
import csv, os, sys
from shapely.geometry import Point, box
import geom as G

args = sys.argv[1:]
plans = [a for a in args if a.endswith('.csv') and not a.startswith('--')]
with_rules = '--rules' in args
drop_out = args[args.index('--drop-bad') + 1] if '--drop-bad' in args else None
plans = [p for p in plans if p != drop_out]
bad = set()
dels = []
if '--del' in args:
    dels = list(csv.DictReader(open(args[args.index('--del') + 1])))
    plans = [p for p in plans if p != args[args.index('--del') + 1]]

objs, comps, keepouts = G.load()
for z in csv.DictReader(open(os.environ.get('BK13_ZONES', G.HERE + 'evidence/BK13_ZONES.csv'))):
    G.ZONES.append((box(float(z['x0']), float(z['y0']), float(z['x1']), float(z['y1'])), set(z['nets'].split(';')), z['ref']))
# deletions: drop matching existing tracks from the model before checking
def same(r, o):
    s = o.src
    return (o.kind == 'TRACK' and s[2] == r['net'] and s[1] == r['layer'] and
            ((abs(float(s[3]) - float(r['x1'])) < .002 and abs(float(s[4]) - float(r['y1'])) < .002 and abs(float(s[5]) - float(r['x2'])) < .002 and abs(float(s[6]) - float(r['y2'])) < .002) or
             (abs(float(s[3]) - float(r['x2'])) < .002 and abs(float(s[4]) - float(r['y2'])) < .002 and abs(float(s[5]) - float(r['x1'])) < .002 and abs(float(s[6]) - float(r['y1'])) < .002)))
def same_via(r, o):
    s = o.src
    return (o.kind in ('VIA', 'HOLE') and s is not None and s[0] == 'VIA' and s[1] == r['net'] and
            abs(float(s[2]) - float(r['x1'])) < .002 and abs(float(s[3]) - float(r['y1'])) < .002)


problems = []
for r in dels:
    if r['kind'] == 'VIA':        # a via is two model objects (copper + hole)
        m = [o for o in objs if same_via(r, o)]
        if len([o for o in m if o.kind == 'VIA']) != 1:
            problems.append(f"via delete match {len(m)} for {r}")
    else:
        m = [o for o in objs if same(r, o)]
        if len(m) != 1:
            problems.append(f"delete match {len(m)} for {r}")
    objs = [o for o in objs if o not in m]
idx = G.Index(objs)
pads = [o for o in objs if o.kind == 'PAD']
# C2 6L: L5 regions reserved for one net's pour (same env format as router5.py)
L5_RESERVED = [(t.split(':')[0], box(*[float(v) for v in t.split(':')[1].split(',')]))
               for t in os.environ.get('L5_RESERVED', '').split(';') if t.strip()]
rows = []
for p in plans:
    rows += list(csv.DictReader(open(p)))
new = []
for r in rows:
    if r['kind'] == 'TRACK':
        o = G.track(r['net'], r['layer'], [(float(r['x1']), float(r['y1'])), (float(r['x2']), float(r['y2']))], float(r['w']))
    else:
        o = G.via(r['net'], float(r['x1']), float(r['y1']), float(r['d']), float(r['h']))
    o.name = f"{r['group']}|{r['kind']}|{r['net']}"
    new.append((r, o))
for r, o in new:
    for other, d, req in idx.violations(o):
        problems.append(f'{o.name} vs existing {other.kind} {other.comp}.{other.name} {other.net}: {d} < {req}'); bad.add(r['group'])
    if not G.edge_ok(o.geom):
        problems.append(f'{o.name} edge setback'); bad.add(r['group'])
    if any(k.intersects(o.geom) for k in keepouts):
        problems.append(f'{o.name} keepout'); bad.add(r['group'])
    if r['kind'] == 'TRACK' and r['layer'] == 'Mid Layer 4':
        for rnet, rg in L5_RESERVED:
            if rnet != r['net'] and rg.intersects(o.geom):
                problems.append(f'{o.name} on L5 inside the {rnet} reserved pour region'); bad.add(r['group'])
    if r['kind'] == 'VIA':
        onpads = [f'{q.comp}.{q.name}' for q in pads if q.geom.distance(o.geom) < 0.1 - 1e-6]
        # 'VIP' = planned via-in-pad (filled + capped, POFV): allowed only inside its own same-net pad
        vip_ok = r['group'].endswith(' VIP') and all(q.net == r['net'] for q in pads if q.geom.distance(o.geom) < 0.1 - 1e-6)
        if onpads and not r['group'].endswith('EP via') and not vip_ok:
            problems.append(f'{o.name} via on pad {onpads}'); bad.add(r['group'])
# new vs new (spatially indexed)
from shapely.strtree import STRtree
ntree = STRtree([o.geom for r, o in new])
for i, (ra, a) in enumerate(new):
    for j in ntree.query(a.geom.buffer(0.3)):
        if j <= i:
            continue
        b = new[j][1]
        if a.net == b.net or not (a.layers & b.layers):
            continue
        if a.geom.distance(b.geom) < G.required(a, b) - 1e-6:
            problems.append(f'new-new {a.name} vs {b.name}: {a.geom.distance(b.geom):.4f} < {G.required(a, b)}'); bad.update((ra['group'], new[j][0]['group']))
# holes
nv = [(r, Point(float(r['x1']), float(r['y1'])), float(r['h']) / 2) for r, o in new if r['kind'] == 'VIA']
for i, (r, c, h) in enumerate(nv):
    if not idx.hole_ok(c, h):
        problems.append(f"hole-to-hole vs existing at {r['group']}"); bad.add(r['group'])
    for r2, c2, h2 in nv[i + 1:]:
        if abs(c.x - c2.x) < 1.0 and abs(c.y - c2.y) < 1.0 and c.distance(c2) - h - h2 < 0.254 - 1e-6:
            problems.append(f"hole-to-hole new {r['group']} / {r2['group']}"); bad.update((r['group'], r2['group']))
print('rows', len(rows), 'tracks', sum(r['kind'] == 'TRACK' for r in rows), 'vias', len(nv), 'deletes', len(dels))
print('PROBLEMS', len(problems))
for p in problems[:60]:
    print(' ', p)
if drop_out:
    keep = [r for r in rows if r['group'] not in bad]
    fields = list(dict.fromkeys(k for r in rows for k in r.keys()))   # plans may carry different extra columns
    with open(drop_out, 'w', newline='') as f:
        wr = csv.DictWriter(f, fieldnames=fields, restval='')
        wr.writeheader(); wr.writerows(keep)
    print('DROPPED_GROUPS', len(bad), 'kept rows', len(keep), 'of', len(rows))
    for g in sorted(bad):
        print('  DROP', g)
    sys.exit(0)
if problems:
    sys.exit(1)
MIL = 1 / 0.0254
with open(os.environ.get('OPS_OUT', G.HERE + 'work/OPS.txt'), 'w') as f:
    if with_rules:
        for z in csv.DictReader(open(os.environ.get('BK13_ZONES', G.HERE + 'evidence/BK13_ZONES.csv'))):
            n = z['ref'][-1]
            reg = f"InRegionAbsolute({float(z['x0'])*MIL:.4f},{float(z['y0'])*MIL:.4f},{float(z['x1'])*MIL:.4f},{float(z['y1'])*MIL:.4f})"
            nets = ' Or '.join(f"InNet('{x}')" for x in sorted(z['nets'].split(';')))
            sc = f"{reg} And (InComponent('{z['ref']}') Or {nets})"
            f.write(f"RULE_CLR|CLR_BK13_ESCAPE_{z['ref']}|0.13|{sc}|{sc}\n")
    for r in dels:
        if r['kind'] == 'VIA':
            f.write(f"DEL_VIA|{r['net']}|{r['x1']}|{r['y1']}\n")
        else:
            f.write(f"DEL_TRACK|{r['net']}|{r['layer']}|{r['x1']}|{r['y1']}|{r['x2']}|{r['y2']}\n")
    for r in rows:
        if r['kind'] == 'TRACK':
            f.write(f"TRACK|{r['net']}|{r['layer']}|{r['x1']}|{r['y1']}|{r['x2']}|{r['y2']}|{r['w']}\n")
        else:
            f.write(f"VIA|{r['net']}|{r['x1']}|{r['y1']}|{r['d']}|{r['h']}\n")
print('OPS.txt written')
