"""Local rip-up-and-repair loop on top of router5 (same env as a routing run).

For every unrouted connection (DRC json):
  1. try to route it as is;
  2. otherwise pick 'victims' = routed connections (groups of the plan CSVs, never stitches / BK13 fan-out / placement copper)
     whose copper lies in the corridor between its two ends (straight segment buffered by CORRIDOR mm) or near either end,
     closest first, at most MAXV;
  3. unstamp the victims, route the blocked connection, then re-route every victim between the points where its copper
     touched the rest of its net;
  4. keep the change only if the blocked connection AND every victim routed (strict gain of one connection); else roll back.
Passes repeat until a pass gains nothing.  Output: ADDS.csv (new copper rows, build_ops format) and DELS.csv (victim rows).
usage: <router env> python repair.py DRC.json ADDS.csv DELS.csv PLAN.csv [PLAN.csv ...]
env: CORRIDOR (0.6), MAXV (6), PASSES (2)
"""
import csv, json, os, re, sys, time
import numpy as np
from shapely.geometry import LineString, Point
from shapely.ops import unary_union

drc, out_adds, out_dels, plans = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]
sys.argv = [sys.argv[0]]
import router5 as R
G = R.G
CORRIDOR = float(os.environ.get('CORRIDOR', '0.6'))
MAXV = int(os.environ.get('MAXV', '6'))
PASSES = int(os.environ.get('PASSES', '2'))

# ---------------------------------------------------------------- map native copper -> copper_objs entries and plan groups
cu_src = []                     # parallel to R.copper_objs for the initially loaded objects
for o in R.objs:
    if o.kind in ('PAD', 'TRACK', 'VIA', 'ARC', 'REGION', 'FILL'):
        cu_src.append(o)
assert len(cu_src) <= len(R.copper_objs)
hole_geoms = [o.geom for o in R.objs if o.kind == 'HOLE']


def k_row(r):
    if r['kind'] == 'TRACK':
        return ('T', r['net'], r['layer'], frozenset(((round(float(r['x1']), 3), round(float(r['y1']), 3)), (round(float(r['x2']), 3), round(float(r['y2']), 3)))))
    return ('V', r['net'], round(float(r['x1']), 3), round(float(r['y1']), 3))


def k_src(o):
    s = o.src
    if o.kind == 'TRACK':
        return ('T', s[2], s[1], frozenset(((round(float(s[3]), 3), round(float(s[4]), 3)), (round(float(s[5]), 3), round(float(s[6]), 3)))))
    if o.kind == 'VIA':
        return ('V', s[1], round(float(s[2]), 3), round(float(s[3]), 3))
    return None


key2idx = {}
for i, o in enumerate(cu_src):
    if o.kind in ('TRACK', 'VIA') and o.src is not None:
        key2idx[k_src(o)] = i
groups = {}                     # name -> {'rows': [...], 'entries': [copper_obj tuples], 'net': net}
for p in plans:
    tag = p.replace('\\', '/').rsplit('/', 1)[-1]
    if tag.startswith(('BK13_ESCAPE', 'STITCH')):
        continue
    for r in csv.DictReader(open(p)):
        if r['group'].split(':')[0].startswith('S'):
            continue
        k = k_row(r)
        if k not in key2idx:
            continue            # not native any more
        g = groups.setdefault(tag + '|' + r['group'], {'rows': [], 'entries': [], 'net': r['net']})
        g['rows'].append(r)
        g['entries'].append(R.copper_objs[key2idx[k]])
entry_group = {}
for name, g in groups.items():
    for e in g['entries']:
        entry_group[id(e)] = name
print(f'routed groups mapped: {len(groups)}', flush=True)


# ---------------------------------------------------------------- stamping helpers
def restamp_window(win, net=None):
    """re-stamp every live copper object touching the window (after cells were cleared)"""
    iy0, iy1, ix0, ix1 = win
    x0, y1_ = R.cell_xy(ix0, iy0); x1, y0 = R.cell_xy(ix1, iy1)
    from shapely.geometry import box as _b
    wb = _b(min(x0, x1) - 0.1, min(y0, y1_) - 0.1, max(x0, x1) + 0.1, max(y0, y1_) + 0.1)
    for g, n, ls in R.copper_objs:
        if net is not None and n != net:
            continue
        if g.intersects(wb):
            R.stamp(g, n, ls)


def unstamp(entries):
    """remove copper entries (geom, net, layers) from the rasters and from copper_objs"""
    ids = {id(e) for e in entries}
    R.copper_objs[:] = [e for e in R.copper_objs if id(e) not in ids]
    for g, n, ls in entries:
        win, m = R.patch(g)
        if win is None:
            continue
        iy0, iy1, ix0, ix1 = win
        nid = R.NID.get(n, 0)
        for L in ls:
            if L in R.own:
                sub = R.own[L][iy0:iy1, ix0:ix1]
                sub[m & (sub == nid)] = 0
        restamp_window(win, n)


def unstamp_holes(pts_h):
    for (x, y, h) in pts_h:
        hg = Point(x, y).buffer(h / 2, 12)
        win, m = R.patch(hg)
        if win is None:
            continue
        R.holes[win[0]:win[1], win[2]:win[3]] &= ~m
        for g in hole_geoms:
            if g.intersects(hg.buffer(0.5)):
                w2, m2 = R.patch(g)
                if w2:
                    R.holes[w2[0]:w2[1], w2[2]:w2[3]] |= m2


def stamp_rows(rows):
    """stamp new plan rows; returns (entries, holes) for a later unstamp"""
    ents, hs = [], []
    for r in rows:
        if r['kind'] == 'TRACK':
            g = LineString([(float(r['x1']), float(r['y1'])), (float(r['x2']), float(r['y2']))]).buffer(float(r['w']) / 2, 8)
            e = (g, r['net'], {r['layer']})
        else:
            x, y, vd, vh = float(r['x1']), float(r['y1']), float(r['d']), float(r['h'])
            g = Point(x, y).buffer(vd / 2, 16)
            e = (g, r['net'], set(R.LAYERS))
            hg = Point(x, y).buffer(vh / 2, 12)
            win, m = R.patch(hg)
            if win:
                R.holes[win[0]:win[1], win[2]:win[3]] |= m
            hole_geoms.append(hg); hs.append((x, y, vh))
        R.stamp(e[0], e[1], e[2]); R.copper_objs.append(e); ents.append(e)
    return ents, hs


def remove_rows(ents, hs):
    unstamp(ents)
    for (x, y, h) in hs:
        hg = [g for g in hole_geoms if abs(g.centroid.x - x) < 1e-6 and abs(g.centroid.y - y) < 1e-6]
        for g in hg:
            hole_geoms.remove(g)
    unstamp_holes(hs)


def rows_for(net, res, tag, conn_key):
    segs, vias, w, vd, vh, relax = res
    out = []
    for L, pts in segs:
        for p, q in zip(pts, pts[1:]):
            for pp, qq in R.split_at_regions(p, q):
                out.append({'kind': 'TRACK', 'group': tag, 'net': net, 'layer': L, 'x1': round(pp[0], 4), 'y1': round(pp[1], 4),
                            'x2': round(qq[0], 4), 'y2': round(qq[1], 4), 'w': w, 'd': '', 'h': '', 'conn': conn_key, 'relax': 0})
    for x, y in vias:
        out.append({'kind': 'VIA', 'group': tag, 'net': net, 'layer': 'Multi Layer', 'x1': round(x, 4), 'y1': round(y, 4),
                    'x2': '', 'y2': '', 'w': '', 'd': vd, 'h': vh, 'conn': conn_key, 'relax': 0})
    if R.VIP and any(R._in_own_pad(net, x, y, vd) for x, y in vias):
        for r in out:
            r['group'] = tag + ' VIP'
    return out


def pt_end(p):
    return {'kind': 'Via', 'pts': [p], 'text': f'Point ({p[0]:.3f}mm,{p[1]:.3f}mm)'}


def touch_points(name):
    """points where a group's copper touches same-net copper outside the group (its two logical ends)"""
    g = groups[name]
    own_ids = {id(e) for e in g['entries']}
    others = [e for e in R.copper_objs if e[1] == g['net'] and id(e) not in own_ids]
    pts = []
    for r in g['rows']:
        cand = [(float(r['x1']), float(r['y1']))] + ([(float(r['x2']), float(r['y2']))] if r['kind'] == 'TRACK' else [])
        lay = {r['layer']} if r['kind'] == 'TRACK' else set(R.LAYERS)
        for c in cand:
            P = Point(c).buffer(0.01)
            if any(ls & lay and ge.intersects(P) for ge, n, ls in others):
                pts.append(c)
    uniq = []
    for p in pts:
        if all(abs(p[0] - q[0]) > 0.02 or abs(p[1] - q[1]) > 0.02 for q in uniq):
            uniq.append(p)
    if len(uniq) < 2:
        return uniq
    best = max(((a, b) for i, a in enumerate(uniq) for b in uniq[i + 1:]), key=lambda t: (t[0][0] - t[1][0]) ** 2 + (t[0][1] - t[1][1]) ** 2)
    return list(best)


# ---------------------------------------------------------------- main loop
conns = [c for c in (R.parse_conn(d) for d in json.load(open(drc))['details'] if d.startswith('Un-Routed')) if c]
adds, dels, gained, k = [], [], 0, 0
dead_groups = set()
t0 = time.time()
for ps in range(PASSES):
    todo, gain_pass = list(conns), 0
    conns = []
    for net, a, b in todo:
        k += 1
        ck = '|'.join(R.key((net, a, b)))
        res, why = R.route_one(net, a, b)
        if res and why == 'already connected':
            gained += 1; gain_pass += 1; continue
        if res:
            rows = rows_for(net, res, f'P{k}:{net}', ck); stamp_rows(rows); adds += rows; gained += 1; gain_pass += 1
            print(f'  [{time.time() - t0:.0f}s] direct {net}', flush=True); continue
        # victims in the corridor / near the ends
        pa, pb = a['pts'][0], b['pts'][0]
        zone = LineString([pa, pb]).buffer(CORRIDOR) if pa != pb else Point(pa).buffer(CORRIDOR)
        zone = zone.union(Point(pa).buffer(CORRIDOR)).union(Point(pb).buffer(CORRIDOR))
        vict = {}
        for e in R.copper_objs:
            nm = entry_group.get(id(e))
            if nm and nm not in dead_groups and e[1] != net and e[0].intersects(zone):
                d = e[0].distance(LineString([pa, pb]) if pa != pb else Point(pa))
                vict[nm] = min(vict.get(nm, 9e9), d)
        vl = sorted(vict, key=vict.get)[:MAXV]
        if not vl:
            conns.append((net, a, b)); continue
        ends = {nm: touch_points(nm) for nm in vl}
        saved = {nm: list(groups[nm]['entries']) for nm in vl}
        vias_of = {nm: [(float(r['x1']), float(r['y1']), float(r['h'] or 0.3)) for r in groups[nm]['rows'] if r['kind'] == 'VIA'] for nm in vl}
        for nm in vl:
            unstamp(saved[nm]); unstamp_holes(vias_of[nm])
            for (x, y, h) in vias_of[nm]:
                for g in [g for g in hole_geoms if abs(g.centroid.x - x) < 1e-6 and abs(g.centroid.y - y) < 1e-6]:
                    hole_geoms.remove(g)
        res, why = R.route_one(net, a, b)
        new_blocks, ok = [], bool(res)
        if res and why != 'already connected':
            rows = rows_for(net, res, f'P{k}:{net}', ck); new_blocks.append(stamp_rows(rows) + (rows,))
        if ok:
            for nm in vl:
                e2 = ends[nm]
                if len(e2) < 2:
                    continue            # dangling piece: simply dropped
                r2, w2 = R.route_one(groups[nm]['net'], pt_end(e2[0]), pt_end(e2[1]))
                if not r2:
                    ok = False; break
                if w2 != 'already connected':
                    rows = rows_for(groups[nm]['net'], r2, f'P{k}v:{groups[nm]["net"]}', 'repair|' + nm)
                    new_blocks.append(stamp_rows(rows) + (rows,))
        if ok:
            for nm in vl:
                dels += groups[nm]['rows']; dead_groups.add(nm)
            for ents, hs, rows in new_blocks:
                adds += rows
            gained += 1; gain_pass += 1
            print(f'  [{time.time() - t0:.0f}s] repaired {net} (victims {len(vl)})', flush=True)
        else:
            for ents, hs, rows in reversed(new_blocks):
                remove_rows(ents, hs)
            for nm in vl:                                   # restore the victims exactly
                for e in saved[nm]:
                    R.stamp(e[0], e[1], e[2]); R.copper_objs.append(e)
                for (x, y, h) in vias_of[nm]:
                    hg = Point(x, y).buffer(h / 2, 12); hole_geoms.append(hg)
                    win, m = R.patch(hg)
                    if win:
                        R.holes[win[0]:win[1], win[2]:win[3]] |= m
            conns.append((net, a, b))
    print(f'PASS {ps + 1}: gained {gain_pass}, still failing {len(conns)} ({time.time() - t0:.0f}s)', flush=True)
    if gain_pass == 0:
        break
fields = ['kind', 'group', 'net', 'layer', 'x1', 'y1', 'x2', 'y2', 'w', 'd', 'h', 'conn', 'relax']
with open(out_adds, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore', restval=''); w.writeheader(); w.writerows(adds)
with open(out_dels, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore', restval=''); w.writeheader(); w.writerows(dels)
print(f'GAINED {gained} connections; adds {len(adds)} rows, dels {len(dels)} rows; still failing {len(conns)}')
