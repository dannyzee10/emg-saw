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
RIP_BK13 = os.environ.get('RIP_BK13') == '1'   # hand-placed socket escapes become rippable (see bk13_group)


def bk13_groups(rows):
    """split a socket's escape rows: each via + the tracks that touch it = one group ('<socket>:<net>:via@x,y'), the
    remaining tracks of the net = '<socket>:<net>'.  The router cannot redo the in-socket tracks (they use the 0.13 mm
    BK13 zone clearance next to the socket keep-out), but it can move an escape via and its stub."""
    vias = [(r['group'], r['net'], float(r['x1']), float(r['y1']), float(r['d'] or 0.6)) for r in rows if r['kind'] == 'VIA']
    out = []
    for r in rows:
        name = f"{r['group']}:{r['net']}"
        if r['kind'] == 'VIA':
            name += f":via@{float(r['x1']):g},{float(r['y1']):g}"
        else:
            ends = [(float(r['x1']), float(r['y1'])), (float(r['x2']), float(r['y2']))]
            for g_, n_, vx, vy, vd in vias:
                if g_ == r['group'] and n_ == r['net'] and any(math.hypot(ex - vx, ey - vy) < vd / 2 for ex, ey in ends):
                    name += f":via@{vx:g},{vy:g}"; break
        out.append(dict(r, group=name))
    return out


import math
for p in plans:
    tag = p.replace('\\', '/').rsplit('/', 1)[-1]
    bk13 = tag.startswith('BK13_ESCAPE')
    if tag.startswith('STITCH') or (bk13 and not RIP_BK13):
        continue
    rows_p = list(csv.DictReader(open(p)))
    if bk13:                    # DELS rows carry the split group name
        rows_p = bk13_groups(rows_p)
    for r in rows_p:
        if not bk13 and r['group'].split(':')[0].startswith('S'):
            continue
        if bk13 and ':via@' not in r['group']:
            continue            # in-socket escape tracks stay fixed (0.13 mm zone clearance the router cannot redo)
        if bk13 and os.environ.get('RIP_BK13_ONLY') and \
                not any(r['group'].startswith(p_ + ':via@') for p_ in os.environ['RIP_BK13_ONLY'].split(',')):
            continue            # only the named socket vias may move (a hand-placed via elsewhere may be unplaceable)
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


# ---------------------------------------------------------------- exact validation (same checks as build_ops.py)
EXACT = os.environ.get('EXACT', '1') == '1'
if os.environ.get('BK13_ZONES'):
    from shapely.geometry import box as _bx
    for z in csv.DictReader(open(os.environ['BK13_ZONES'])):
        G.ZONES.append((_bx(float(z['x0']), float(z['y0']), float(z['x1']), float(z['y1'])), set(z['nets'].split(';')), z['ref']))
EX = G.Index([o for o in R.objs])
EX_PADS = [o for o in R.objs if o.kind == 'PAD']
EX_HOLES = [o for o in R.objs if o.kind == 'HOLE']
removed_ids = set()                 # ids of Obj (initial model objects) deleted by accepted repairs
entry_obj = {id(R.copper_objs[i]): cu_src[i] for i in range(len(cu_src))}
hole_obj = {}
for o in EX_HOLES:
    if o.src is not None and o.src[0] == 'VIA':
        hole_obj[('V', o.src[1], round(float(o.src[2]), 3), round(float(o.src[3]), 3))] = o


def objs_of_group(nm):
    out = [entry_obj[id(e)] for e in groups[nm]['entries'] if id(e) in entry_obj]
    for r in groups[nm]['rows']:
        if r['kind'] == 'VIA':
            h = hole_obj.get(('V', r['net'], round(float(r['x1']), 3), round(float(r['y1']), 3)))
            if h is not None:
                out.append(h)
    return out


LAST_FAIL = ['']


def _fail(msg):
    LAST_FAIL[0] = msg
    return False


def exact_ok(rows, extra_removed=()):
    """rows: new plan rows of one repair (all of them); extra_removed: model objects deleted by this repair"""
    if not EXACT:
        return True
    rem = removed_ids | {id(o) for o in extra_removed}
    new = []
    for r in rows:
        if r['kind'] == 'TRACK':
            o = G.track(r['net'], r['layer'], [(float(r['x1']), float(r['y1'])), (float(r['x2']), float(r['y2']))], float(r['w']))
        else:
            o = G.via(r['net'], float(r['x1']), float(r['y1']), float(r['d']), float(r['h']))
        new.append((r, o))
    for r, o in new:
        for other, d, req in EX.violations(o):
            if id(other) not in rem:
                return _fail(f'clearance {r["net"]} {r["kind"]} {r["layer"]} ({r["x1"]},{r["y1"]})-({r["x2"]},{r["y2"]}) w{r["w"]} d{r["d"]} vs {other.net} {other.kind} {other.comp} {other.name} at ({other.geom.centroid.x:.3f},{other.geom.centroid.y:.3f}) d={d:.3f} req={req}')
        if not G.edge_ok(o.geom) or any(k.intersects(o.geom) for k in R.keepouts):
            return _fail('edge/keepout')
        if r['kind'] == 'TRACK' and r['layer'] == 'Mid Layer 4':
            for rnet, rg in R.L5_RESERVED:
                if rnet != r['net'] and rg.intersects(o.geom):
                    return _fail('L5 reserved')
        if r['kind'] == 'VIA':
            near = [q for q in EX_PADS if q.geom.distance(o.geom) < 0.1 - 1e-6]
            vip = r['group'].endswith(' VIP') and all(q.net == r['net'] for q in near)
            if near and not vip:
                return _fail('via near pad')
            c = Point(float(r['x1']), float(r['y1'])); hr = float(r['h']) / 2
            for h in EX_HOLES:
                if id(h) not in rem and abs(h.geom.centroid.x - c.x) < 1.2 and abs(h.geom.centroid.y - c.y) < 1.2 and \
                        h.geom.distance(c.buffer(hr)) < G.hole_gap(h) - 1e-6:
                    return _fail('hole-hole')
    for i, (ra, a) in enumerate(new):
        for rb, b in new[i + 1:]:
            if a.net != b.net and a.layers & b.layers and a.geom.distance(b.geom) < G.required(a, b) - 1e-6:
                return _fail(f'new-new clearance {a.net} {ra["kind"]} ({ra["x1"]},{ra["y1"]}) vs {b.net} {rb["kind"]} '
                             f'({rb["x1"]},{rb["y1"]}) d={a.geom.distance(b.geom):.3f} req={G.required(a, b)}')
        if ra['kind'] == 'VIA':
            for rb, b in new[i + 1:]:
                if rb['kind'] == 'VIA' and Point(float(ra['x1']), float(ra['y1'])).distance(Point(float(rb['x1']), float(rb['y1']))) \
                        < float(ra['h']) / 2 + float(rb['h']) / 2 + 0.254 - 1e-6:
                    return _fail('new hole-hole')
    return True


def commit_exact(rows, removed_objs):
    """make accepted rows / removals part of the exact model"""
    for o in removed_objs:
        removed_ids.add(id(o))
    for r in rows:
        if r['kind'] == 'TRACK':
            o = G.track(r['net'], r['layer'], [(float(r['x1']), float(r['y1'])), (float(r['x2']), float(r['y2']))], float(r['w']))
        else:
            o = G.via(r['net'], float(r['x1']), float(r['y1']), float(r['d']), float(r['h']))
            EX_HOLES.append(G.Obj(Point(float(r['x1']), float(r['y1'])).buffer(float(r['h']) / 2), r['net'], 'HOLE', set()))
        EX.add(o)


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
    # the ripped holes themselves must not be re-stamped (callers drop them from hole_geoms only afterwards)
    gone = [(x, y) for (x, y, h) in pts_h]
    for (x, y, h) in pts_h:
        hg = Point(x, y).buffer(h / 2, 12)
        win, m = R.patch(hg)
        if win is None:
            continue
        R.holes[win[0]:win[1], win[2]:win[3]] &= ~m
        for g in hole_geoms:
            if any(abs(g.centroid.x - gx) < 1e-6 and abs(g.centroid.y - gy) < 1e-6 for gx, gy in gone):
                continue
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


def snap():
    """exact snapshot of the router state for rollbacks: per-layer net-id rasters, via-hole raster, copper and hole lists.
    (Piecewise undo is not exact: one net id per cell, and holes are re-stamped from approximate circles.)"""
    return ({L: a.copy() for L, a in R.own.items()}, R.holes.copy(), list(R.copper_objs), list(hole_geoms))


def restore(s):
    for L, a in s[0].items():
        R.own[L][...] = a
    R.holes[...] = s[1]
    R.copper_objs[:] = s[2]
    hole_geoms[:] = s[3]


def rip_names(names):
    for nm in names:
        unstamp(list(groups[nm]['entries']))
        vh = [(float(r['x1']), float(r['y1']), float(r['h'] or 0.3)) for r in groups[nm]['rows'] if r['kind'] == 'VIA']
        unstamp_holes(vh)
        for (x, y, h) in vh:
            for g in [g for g in hole_geoms if abs(g.centroid.x - x) < 1e-6 and abs(g.centroid.y - y) < 1e-6]:
                hole_geoms.remove(g)


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
    return touch_points_multi([name])


def touch_points_multi(names):
    """points where the copper of one group (or of a cluster of touching same-net groups ripped together) touches same-net
    copper outside it: every row end that lands on other copper AND every place where other copper touches it anywhere
    along it (T-junctions onto a track's middle, pads the track passes over) -- every one must be reconnected"""
    ents = [e for nm in names for e in groups[nm]['entries']]
    rows_ = [r for nm in names for r in groups[nm]['rows']]
    net_ = groups[names[0]]['net']
    own_ids = {id(e) for e in ents}
    others = [e for e in R.copper_objs if e[1] == net_ and id(e) not in own_ids]
    g = {'entries': ents, 'rows': rows_}
    pts = []
    for r in g['rows']:
        cand = [(float(r['x1']), float(r['y1']))] + ([(float(r['x2']), float(r['y2']))] if r['kind'] == 'TRACK' else [])
        lay = {r['layer']} if r['kind'] == 'TRACK' else set(R.LAYERS)
        for c in cand:
            P = Point(c).buffer(0.01)
            if any(ls & lay and ge.intersects(P) for ge, n, ls in others):
                pts.append(c)
    for mg, mn, ml in g['entries']:
        mb = mg.bounds
        for ge, n, ls in others:
            if not (ls & ml):
                continue
            b = ge.bounds
            if b[0] > mb[2] + 0.01 or b[2] < mb[0] - 0.01 or b[1] > mb[3] + 0.01 or b[3] < mb[1] - 0.01:
                continue
            if ge.distance(mg) < 0.002:
                inter = ge.intersection(mg.buffer(0.003))
                p = inter.representative_point() if not inter.is_empty else ge.representative_point()
                pts.append((p.x, p.y))
    uniq = []
    for p in pts:
        if all(abs(p[0] - q[0]) > 0.05 or abs(p[1] - q[1]) > 0.05 for q in uniq):
            uniq.append(p)
    return uniq                 # ALL touch points: a branched group must be reconnected at every branch end


STRICT_VICTIMS = os.environ.get('STRICT_VICTIMS', '1') == '1'


def _route_checked(net_, ea, eb, tag, key, rem):
    """route_one, then (when rem is given) exact-check the rows; on failure retry at SAFE_MARGIN, then at the net's
    minimum width (route ends are forced free, so a wide track ending next to other copper can break clearance)"""
    r2, w2 = R.route_one(net_, ea, eb)
    if rem is None or not r2 or w2 == 'already connected' or exact_ok(rows_for(net_, r2, tag, key), rem):
        return r2, w2
    m0, wf = R.MARGIN, R.widths
    try:
        R.MARGIN = SAFE_MARGIN
        r3, w3 = R.route_one(net_, ea, eb)
        if r3 and exact_ok(rows_for(net_, r3, tag, key), rem):
            return r3, w3
        R.widths = lambda n, _f=wf: _f(n)[-1:]
        r3, w3 = R.route_one(net_, ea, eb)
        if r3 and exact_ok(rows_for(net_, r3, tag, key), rem):
            return r3, w3
        R.MARGIN = 0.10
        r3, w3 = R.route_one(net_, ea, eb)
        if r3 and exact_ok(rows_for(net_, r3, tag, key), rem):
            return r3, w3
    finally:
        R.MARGIN, R.widths = m0, wf
    if STRICT_VICTIMS:
        return None, 'exact fail after retries: ' + LAST_FAIL[0]     # a failed victim -> reorder / cascade can react
    return r2, w2


def reconnect(nm, tag, rem=None):
    """re-route a ripped group: join every touch point to the first one; returns (ok, blocks).
    PLANE=1 and a plane net (GND / 3V0_ANA): each touch point only needs plane access -- an island that has none gets a
    stub + via to the nearest legal via site; only when that fails is it joined to the first point by copper"""
    pts, net_, blocks_ = ends_cache[nm], groups[nm]['net'], []
    if PLANE and net_ in ('GND', '3V0_ANA'):
        for q in pts:
            e = pt_end(q)
            g, ls = R.end_copper(e, net_)
            if g is None:
                return False, blocks_
            if _has_access(net_, R.component(net_, g)):
                continue
            r2, w2 = route_plane(net_, e)
            rows = rows_for(net_, r2, tag, 'repair|' + nm) if r2 else None
            if r2 and (rem is None or exact_ok(rows, rem)):
                blocks_.append(stamp_rows(rows) + (rows,)); continue
            # no plane via site for this island: join it by copper to ANY other touch point of the group (the router
            # places the via wherever it is legal), pts[0] first
            joined = False
            for o in [p_ for p_ in pts if p_ != q]:
                r2, w2 = _route_checked(net_, pt_end(o), e, tag, 'repair|' + nm, rem)
                if not r2:
                    continue
                if w2 != 'already connected':
                    rows = rows_for(net_, r2, tag, 'repair|' + nm)
                    blocks_.append(stamp_rows(rows) + (rows,))
                joined = True
                break
            if not joined:
                return False, blocks_
        return True, blocks_
    for q in pts[1:]:
        r2, w2 = _route_checked(net_, pt_end(pts[0]), pt_end(q), tag, 'repair|' + nm, rem)
        if not r2:
            return False, blocks_
        if w2 != 'already connected':
            rows = rows_for(net_, r2, tag, 'repair|' + nm)
            blocks_.append(stamp_rows(rows) + (rows,))
    return True, blocks_


ends_cache = {}
cluster_of = {}                 # cluster head -> all ripped groups it reconnects (set_ends)


def set_ends(vl):
    """touch points for a victim list: same-net victims whose copper touches are merged into one cluster (the touch point
    between them disappears when both are ripped); the cluster's external touch points go to its first member, the other
    members get none (they are reconnected through the first)"""
    parent = {nm: nm for nm in vl}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    for i, a in enumerate(vl):
        for b in vl[i + 1:]:
            if groups[a]['net'] != groups[b]['net'] or find(a) == find(b):
                continue
            if any(ea[2] & eb[2] and ea[0].distance(eb[0]) < 0.002 for ea in groups[a]['entries'] for eb in groups[b]['entries']):
                parent[find(b)] = find(a)
    cl = {}
    for nm in vl:
        cl.setdefault(find(nm), []).append(nm)
    for members in cl.values():
        members.sort(key=vl.index)
        ends_cache[members[0]] = touch_points_multi(members)
        cluster_of[members[0]] = list(members)
        for m in members[1:]:
            ends_cache[m] = []
            cluster_of[m] = []



# ---------------------------------------------------------------- plane access (PLANE=1): GND / 3V0_ANA ends reach a via site
PLANE = os.environ.get('PLANE') == '1'
R_ANA = None
if PLANE:
    from shapely.geometry import Polygon as _Poly
    R_ANA = _Poly([tuple(map(float, p_.split(','))) for p_ in os.environ['R_ANA'].split(';')])
    _ANA_IN = R_ANA.buffer(-0.225 - 0.05)
PLANE_WIN = float(os.environ.get('PLANE_WIN', '3.0'))
# isolated plane-pour fragments (x0,y0,x1,y1;...): a GND via inside one does not reach the main L2/L4 plane
PLANE_DEAD = [tuple(map(float, b_.split(','))) for b_ in os.environ.get('PLANE_DEAD', '').split(';') if b_]


def _dead(x, y):
    return any(b_[0] <= x <= b_[2] and b_[1] <= y <= b_[3] for b_ in PLANE_DEAD)


def _has_access(net, comp):
    for g, ls in comp:
        c_ = g.centroid
        if len(ls) >= len(R.LAYERS) and (net == 'GND' or R_ANA.contains(c_)) and not (net == 'GND' and _dead(c_.x, c_.y)):
            return True
    return False


def plane_end(net, a, b):
    """the end (dict) of a GND / 3V0_ANA connection whose copper island has no plane access, or None"""
    for end in (a, b):
        g, ls = R.end_copper(end, net)
        if g is not None and not _has_access(net, R.component(net, g)):
            return end
    return None


def route_plane(net, end):
    g, ls = R.end_copper(end, net)
    comp = R.component(net, g)
    isl = unary_union([gg for gg, _ in comp])       # search around the whole island when it is small (its vias count)
    ib = isl.bounds
    anchor = isl if (ib[2] - ib[0]) < 12 and (ib[3] - ib[1]) < 12 else g
    for w in R.widths(net):
        W = R.window(anchor, anchor, PLANE_WIN)
        free, via_ok = R.maps(net, w, W, 0.45, 0.2)
        if os.environ.get('DEBUG_PLANE'):
            iy0, iy1, ix0, ix1 = W
            print(f'    [plane {net} w{w} W{W}] via_ok {int(via_ok.sum())} holes {int(R.holes[iy0:iy1, ix0:ix1].sum())} '
                  + ' '.join(f'{L[:3]}{L[-1]}:{int((R.own[L][iy0:iy1, ix0:ix1] != 0).sum())}' for L in R.LAYERS), flush=True)
        if net == '3V0_ANA' or PLANE_DEAD:
            iy0, iy1, ix0, ix1 = W
            ys, xs = np.nonzero(via_ok)
            for y, x in zip(ys, xs):
                cx, cy = R.cell_xy(x + ix0, y + iy0)
                if (net == '3V0_ANA' and not _ANA_IN.contains(Point(cx, cy))) or (net == 'GND' and _dead(cx, cy)):
                    via_ok[y, x] = False
        for L in [L for L in R.LAYERS if any(L in lls for gg, lls in comp)]:   # any layer the island has copper on (its vias reach all)
            s = R.comp_nodes([(gg, lls) for gg, lls in comp if L in lls], free, W, [L])
            goals = [(R.LAYERS.index(L), int(x), int(y)) for y, x in zip(*np.nonzero(via_ok & free[L]))]
            if not s or not goals:
                continue
            path = R.astar(free, via_ok, s, goals, R.layer_cost(net), [L], 400000)
            if not path:
                continue
            segs, _ = R.to_segments(path, W) if len(path) > 1 else ([], [])
            return (segs, [R.cell_xy(path[-1][1] + W[2], path[-1][2] + W[0])], w, 0.45, 0.2, False), 'ok plane'
    return None, 'no plane via site'


LAST_PLANE = ['']


def route_conn(net, a, b):
    LAST_PLANE[0] = ''
    if PLANE and net in ('GND', '3V0_ANA'):
        e = plane_end(net, a, b)
        LAST_PLANE[0] = 'plane end ' + (e['text'][:40] if e is not None else 'none (both islands have access)')
        if e is not None:
            res, why = route_plane(net, e)
            LAST_PLANE[0] += f' -> {why}'
            if res:
                return res, why
    return R.route_one(net, a, b)


SAFE_MARGIN = float(os.environ.get('SAFE_MARGIN', '0.06'))
REORDER = int(os.environ.get('REORDER', '2'))


def route_conn_safe(net, a, b, rows_check):
    """route; if the raster path fails the exact check (raster can be one cell optimistic at a copper edge), re-route the
    same connection at SAFE_MARGIN.  rows_check(res) -> bool.  Returns (res, why)."""
    res, why = route_conn(net, a, b)
    if not res or why == 'already connected' or rows_check(res):
        return res, why
    m0 = R.MARGIN
    R.MARGIN = SAFE_MARGIN
    try:
        res2, why2 = route_conn(net, a, b)
    finally:
        R.MARGIN = m0
    if res2 and rows_check(res2):
        return res2, why2 + ' (safe margin)'
    return res, why

# ---------------------------------------------------------------- main loop
conns = [c for c in (R.parse_conn(d) for d in json.load(open(drc))['details'] if d.startswith('Un-Routed')) if c]
if os.environ.get('ONLY_NETS'):
    conns = [c for c in conns if c[0] in os.environ['ONLY_NETS'].split(',')]
if os.environ.get('ONLY_BOX'):     # parallel rounds: keep only connections with an end inside one of these boxes (x1,y1,x2,y2;...)
    _obx = [tuple(map(float, b.split(','))) for b in os.environ['ONLY_BOX'].split(';')]
    conns = [c for c in conns if any(b[0] <= e_['pts'][0][0] <= b[2] and b[1] <= e_['pts'][0][1] <= b[3] for b in _obx for e_ in c[1:])]
print(f'connections to repair: {len(conns)} {sorted({c[0] for c in conns})}', flush=True)
DEBUG = os.environ.get('DEBUG') == '1'
adds, dels, gained, k = [], [], 0, 0
dead_groups = set()
t0 = time.time()


def restore_group(nm, saved_entries, vias):
    """put a ripped group's ORIGINAL copper back if it is still legal against everything now in the exact model
    (new routes included); returns True when restored"""
    own = objs_of_group(nm)
    own_ids = {id(o) for o in own}
    for o in own:
        for other, d, req in EX.violations(o):
            if id(other) in own_ids or (id(other) in removed_ids and not any(other is q for q in EX.extra)):
                continue
            return False
        if o.kind == 'HOLE':
            c = o.geom.centroid
            for h in EX_HOLES:
                if h is o or id(h) in own_ids or (id(h) in removed_ids):
                    continue
                if abs(h.geom.centroid.x - c.x) < 1.2 and abs(h.geom.centroid.y - c.y) < 1.2 and h.geom.distance(o.geom) < max(G.hole_gap(h), G.hole_gap(o)) - 1e-6:
                    return False
    removed_ids.difference_update(own_ids)
    for e in saved_entries:
        R.stamp(e[0], e[1], e[2]); R.copper_objs.append(e)
    for (x, y, h) in vias:
        hg = Point(x, y).buffer(h / 2, 12); hole_geoms.append(hg)
        win, m = R.patch(hg)
        if win:
            R.holes[win[0]:win[1], win[2]:win[3]] |= m
    return True


def save_outputs():
    """write ADDS / DELS now (called after every accepted gain: a killed run keeps its exact-checked progress)"""
    fl = ['kind', 'group', 'net', 'layer', 'x1', 'y1', 'x2', 'y2', 'w', 'd', 'h', 'conn', 'relax']
    for path_, rows_ in ((out_adds, adds), (out_dels, dels)):
        with open(path_, 'w', newline='') as f_:
            w_ = csv.DictWriter(f_, fieldnames=fl, extrasaction='ignore', restval=''); w_.writeheader(); w_.writerows(rows_)


def region_pass(box_, first):
    """rip every routed group touching box_, route the unrouted connections with an end in box_ (FIRST_NETS order) and then
    the ripped groups; keep only if more unrouted connections were closed than ripped groups were lost"""
    global k, gained, conns
    from shapely.geometry import box as _box
    rb = _box(*box_)
    vl = sorted({entry_group[id(e)] for e in R.copper_objs if id(e) in entry_group and entry_group[id(e)] not in dead_groups
                 and e[0].intersects(rb)})
    inside = [c for c in conns if any(rb.buffer(0.3).contains(Point(e_['pts'][0])) for e_ in c[1:])]
    rank = lambda c: next((i for i, p in enumerate(first) if c[0].startswith(p)), len(first))
    inside.sort(key=rank)
    set_ends(vl)
    saved = {nm: list(groups[nm]['entries']) for nm in vl}
    vias_of = {nm: [(float(r['x1']), float(r['y1']), float(r['h'] or 0.3)) for r in groups[nm]['rows'] if r['kind'] == 'VIA'] for nm in vl}

    def rip(nm):
        unstamp(saved[nm]); unstamp_holes(vias_of[nm])
        for (x, y, h) in vias_of[nm]:
            for g in [g for g in hole_geoms if abs(g.centroid.x - x) < 1e-6 and abs(g.centroid.y - y) < 1e-6]:
                hole_geoms.remove(g)
    for nm in vl:
        rip(nm)
    # tentative exact model: victims removed now, each new route exact-checked and committed as it is made
    snap = (len(EX.extra), len(EX_HOLES), set(removed_ids))
    removed_o = [o for nm in vl for o in objs_of_group(nm)]
    pre = []                        # groups routed BEFORE the targets (lost in an earlier try)
    for attempt in range(REORDER + 1):
        removed_ids.update(id(o) for o in removed_o)
        st = {'blocks': [], 'lost': 0}
        won, closed, restored, lost_names = 0, [], set(), []

        def do_victim(nm):
            global k
            if len(ends_cache[nm]) < 2:
                return
            k += 1
            okv, bl = reconnect(nm, f'P{k}v:{groups[nm]["net"]}', ())
            vrows = [r for ents, hs, rows in bl for r in rows]
            if okv and exact_ok(vrows):
                st['blocks'] += bl; commit_exact(vrows, [])
            else:
                for ents, hs, rows in reversed(bl):
                    remove_rows(ents, hs)
                if restore_group(nm, saved[nm], vias_of[nm]):
                    restored.add(nm)
                else:
                    st['lost'] += 1; lost_names.append(nm)
        for nm in pre:
            do_victim(nm)
        for net, a, b in inside:
            k += 1
            res, why = route_conn(net, a, b)
            if res:
                if why == 'already connected':
                    won += 1; closed.append((net, a, b)); continue
                rows = rows_for(net, res, f'P{k}:{net}', '|'.join(R.key((net, a, b))))
                if exact_ok(rows):
                    st['blocks'].append(stamp_rows(rows) + (rows,)); commit_exact(rows, [])
                    won += 1; closed.append((net, a, b))
        for nm in vl:
            if nm not in pre:
                do_victim(nm)
        for nm in vl:               # dangling pieces / groups without two ends: keep them when still legal
            if len(ends_cache[nm]) < 2 and nm not in restored and restore_group(nm, saved[nm], vias_of[nm]):
                restored.add(nm)
        blocks, lost = st['blocks'], st['lost']
        print(f'REGION {box_} try {attempt}: ripped {len(vl)}, unrouted inside {len(inside)} -> closed {won}, ripped not '
              f're-routed {lost}, restored as they were {len(restored)}'
              + (f'; lost {[groups[n]["net"] for n in lost_names]}' if DEBUG else ''), flush=True)
        if won > lost:
            for nm in vl:
                if nm in restored:
                    continue
                dels.extend(groups[nm]['rows']); dead_groups.add(nm)
            for ents, hs, rows in blocks:
                adds.extend(rows)
            cs = {R.key(c) for c in closed}
            conns = [c for c in conns if R.key(c) not in cs]
            gained += won - lost
            print(f'  accepted: net gain {won - lost}', flush=True)
            save_outputs()
            return won - lost
        # undo this try completely: new copper, tentative exact model, groups restored in this try
        for ents, hs, rows in reversed(blocks):
            remove_rows(ents, hs)
        del EX.extra[snap[0]:]; del EX_HOLES[snap[1]:]
        removed_ids.clear(); removed_ids.update(snap[2])
        for nm in restored:
            rip(nm)
        if not lost_names or attempt == REORDER:
            break
        pre = pre + [n for n in lost_names if n not in pre]
    for nm in vl:                   # roll back: every ripped group as it was
        for e in saved[nm]:
            R.stamp(e[0], e[1], e[2]); R.copper_objs.append(e)
        for (x, y, h) in vias_of[nm]:
            hg = Point(x, y).buffer(h / 2, 12); hole_geoms.append(hg)
            win, m = R.patch(hg)
            if win:
                R.holes[win[0]:win[1], win[2]:win[3]] |= m
    print('  rejected (rolled back)', flush=True)
    return 0


GUIDED = float(os.environ.get('GUIDED', '0'))    # >0: victims = groups hit by the fixed-copper-only path (rip box margin, mm)
PARTIAL = float(os.environ.get('PARTIAL', '0'))  # >0: rip only the part of a victim within PARTIAL mm of the path
LAST_PATH = [None]
_nsplit = [0]


def split_group(nm, zone, dist=None):
    """partial rip-up: move the rows / copper of group nm that lie within PARTIAL of zone into a new group
    '<nm>#p<k>' (rows renamed too, so DELS / consistent_repair keep working); the rest stays routed and the new
    group's touch points (where it meets the kept part) are reconnected.  Returns the name to rip."""
    d_ = PARTIAL if dist is None else dist
    if not d_ or zone is None:
        return nm
    g = groups[nm]
    idx = [i for i, e in enumerate(g['entries']) if e[0].distance(zone) < d_]
    if not idx or len(idx) == len(g['entries']):
        return nm
    _nsplit[0] += 1
    sfx = f'#p{_nsplit[0]}'
    new = nm + sfx
    ids = set(idx)
    rows_new = [dict(g['rows'][i], group=g['rows'][i]['group'] + sfx) for i in idx]
    ents_new = [g['entries'][i] for i in idx]
    g['rows'] = [r for i, r in enumerate(g['rows']) if i not in ids]
    g['entries'] = [e for i, e in enumerate(g['entries']) if i not in ids]
    groups[new] = {'rows': rows_new, 'entries': ents_new, 'net': g['net']}
    for e in ents_new:
        entry_group[id(e)] = new
    return new
CASCADE = int(os.environ.get('CASCADE', '0'))     # >0: a victim that cannot be re-routed pulls in its own blockers (max victims)


def fixed_path_victims(net, a, b, box_):
    """rip every live routed group of another net touching box_, route (net, a, b) against what is left (pads, holes,
    native copper, same-net copper), then restore the exact state.  Returns (victim names or None, why, rows): the victims
    are the ripped groups the path comes near, verified by re-routing with ONLY them ripped (tolerance widened as needed)."""
    from shapely.geometry import box as _box
    rb = _box(*box_)
    vl = sorted({entry_group[id(e)] for e in R.copper_objs if id(e) in entry_group and e[1] != net
                 and entry_group[id(e)] not in dead_groups and e[0].intersects(rb)})
    s0 = snap()
    LAST_PATH[0] = None
    try:
        rip_names(vl)
        res, why = route_conn(net, a, b)
        rows, hits = [], None
        if res and why != 'already connected':
            rows = rows_for(net, res, 'diag', 'diag')
            cands = [G.track(net, r['layer'], [(r['x1'], r['y1']), (r['x2'], r['y2'])], float(r['w'])) if r['kind'] == 'TRACK'
                     else G.via(net, r['x1'], r['y1'], float(r['d']), float(r['h'])) for r in rows]
            gob = {nm: objs_of_group(nm) for nm in vl}
            dmin = {nm: min([c.geom.distance(o.geom) - G.required(c, o) for o in gob[nm] for c in cands if o.layers & c.layers]
                            or [9e9]) for nm in vl}
            for tol in (0.12, 0.25, 0.4, 0.7):
                hits = sorted(nm for nm in vl if dmin[nm] < tol)
                restore(s0); rip_names(hits)
                r2, w2 = route_conn(net, a, b)
                if r2:
                    # Partial rip-up must follow the route verified with only hits removed.
                    rows = rows_for(net, r2, 'diag', 'diag')
                    cands = [G.track(net, r['layer'], [(r['x1'], r['y1']), (r['x2'], r['y2'])], float(r['w'])) if r['kind'] == 'TRACK'
                             else G.via(net, r['x1'], r['y1'], float(r['d']), float(r['h'])) for r in rows]
                    LAST_PATH[0] = unary_union([c.geom for c in cands]) if cands else None
                    why = f'{why} [{LAST_PLANE[0]}]; verified with {len(hits)} ripped (tol {tol}): {w2}'
                    break
            else:
                hits, why = None, why + '; NOT reproducible with the hits only'
        elif res:
            hits = []
    finally:
        restore(s0)
    return hits, why, rows


def conn_box(a, b, m):
    xs = [p[0] for e_ in (a, b) for p in e_['pts']]
    ys = [p[1] for e_ in (a, b) for p in e_['pts']]
    return (min(xs) - m, min(ys) - m, max(xs) + m, max(ys) + m)


if os.environ.get('DIAG_FIXED'):
    # diagnostic only (writes nothing): per connection, rip every routed group of other nets in the box, route against
    # the fixed copper only.  'no path' = blocked by pads / holes / native copper -> needs a placement or pin change;
    # a path = rip-up problem, and the routed groups that path collides with are listed.
    dbox = tuple(map(float, os.environ['DIAG_FIXED'].split(',')))
    for net, a, b in conns:
        hits, why, rows = fixed_path_victims(net, a, b, dbox)
        if hits is None:
            print(f'DIAG {net}: {why}  (fixed obstacles only)', flush=True); continue
        print(f'DIAG {net}: {why}; path {len(rows)} objs, {len([r for r in rows if r["kind"] == "VIA"])} vias; collides with '
              f'{[groups[nm]["net"] + "(" + nm.split("|")[0] + ")" for nm in hits]}', flush=True)
        for r in rows:
            print('     ', r['kind'], r['layer'], r['x1'], r['y1'], r['x2'], r['y2'], r['w'] or r['d'], flush=True)
    sys.exit(0)
if os.environ.get('NEGOTIATE'):
    # Negotiated-congestion re-route of ONE dense box (PathFinder style).  Every routed piece inside the box is ripped
    # (groups crossing the edge are split there), then all of those nets plus the unrouted connections with an end in
    # the box are routed together.  Other tasks' copper is allowed but penalised: the penalty zone is computed exactly
    # like the router's free map (distance transform of the other nets' copper vs class clearance + own half width),
    # cost = (1 + pres * in_zone + history).  Every pass re-routes every task (shuffled order); cells still shared grow
    # history; pres rises to a cap.  Converged = no task's centre line / via inside another net's zone.  The result goes
    # through the same exact check and is written as ONE repair unit (P<k> / P<k>v rows).
    import random
    from shapely.geometry import box as _box
    from scipy import ndimage as _nd
    nb = tuple(map(float, os.environ['NEGOTIATE'].split(',')))
    rb = _box(*nb)
    NITER = int(os.environ.get('NEG_ITER', '60'))
    NMARG = float(os.environ.get('NEG_MARGIN', '0.05'))   # inter-task margin (raster is one cell coarse)
    PCAP = float(os.environ.get('NEG_PCAP', '40'))
    HINC = float(os.environ.get('NEG_HINC', '1.0'))
    VD, VH = 0.45, 0.2
    rng = random.Random(int(os.environ.get('NEG_RNG', '7')))
    targets = [c for c in conns if any(rb.contains(Point(e_['pts'][0])) for e_ in c[1:])]
    tnets = {c[0] for c in targets}
    names = sorted({entry_group[id(e)] for e in R.copper_objs if id(e) in entry_group and e[1] not in tnets
                    and entry_group[id(e)] not in dead_groups and e[0].intersects(rb)})
    vl = [split_group(nm, rb, dist=1e-4) for nm in names]
    set_ends(vl)
    ripped_objs = [o for nm in vl for o in objs_of_group(nm)]
    s_before = snap()
    rip_names(vl)
    span = unary_union([rb] + [e[0] for nm in vl for e in groups[nm]['entries']])
    W = R.window(span, span, 0.6)
    wy0, wy1, wx0, wx1 = W
    shp = (wy1 - wy0, wx1 - wx0)
    print(f'NEGOTIATE box {nb}: ripped {len(vl)} pieces, targets {[c[0] for c in targets]}, window {shp}', flush=True)

    def plane_sites(net, via_ok):
        ok = via_ok.copy()
        ys, xs = np.nonzero(ok)
        for y_, x_ in zip(ys, xs):
            cx, cy = R.cell_xy(x_ + wx0, y_ + wy0)
            if (net == '3V0_ANA' and not _ANA_IN.contains(Point(cx, cy))) or (net == 'GND' and _dead(cx, cy)):
                ok[y_, x_] = False
        return ok

    k += 1
    K_NEG = k
    tasks = []
    def no_access(net, gs_):
        out_ = []
        for g_ in gs_:
            if g_ is not None and not _has_access(net, R.component(net, g_)):
                out_.append(g_)
        return out_
    for net, a, b in targets:
        key = '|'.join(R.key((net, a, b)))
        ga, la = R.end_copper(a, net); gb, lb = R.end_copper(b, net)
        if PLANE and net in ('GND', '3V0_ANA'):
            gs_ = no_access(net, [ga, gb])
            if gs_:
                tasks.append({'kind': 'ptree', 'net': net, 'gs': gs_, 'tag': f'P{K_NEG}:{net}', 'key': key})
            continue
        tasks.append({'kind': 'conn', 'net': net, 'ga': ga, 'gb': gb, 'tag': f'P{K_NEG}:{net}', 'key': key})
    for nm in vl:
        pts, net = ends_cache[nm], groups[nm]['net']
        tag, key = f'P{K_NEG}v:{net}', 'repair|' + nm
        if PLANE and net in ('GND', '3V0_ANA'):
            gs_ = no_access(net, [R.end_copper(pt_end(q), net)[0] for q in pts])
            if gs_:
                tasks.append({'kind': 'ptree', 'net': net, 'gs': gs_, 'tag': tag, 'key': key, 'nm': nm})
        elif len(pts) >= 2:
            gs = [R.end_copper(pt_end(q), net)[0] for q in pts]
            if all(g is not None for g in gs):
                tasks.append({'kind': 'tree', 'net': net, 'gs': gs, 'tag': tag, 'key': key, 'nm': nm})
    cache, ownfix, accm = {}, {}, {}
    FIXM = float(os.environ.get('NEG_FIX_MARGIN', '0.035'))
    fixm = {}                       # per-net extra margin vs fixed copper after an exact-check near miss

    def access_mask(net):
        """cells (per layer) of this net's fixed copper whose island already has plane access"""
        if net not in accm:
            m_ = {L: np.zeros(shp, bool) for L in R.LAYERS}
            wbox = _box(*R.cell_xy(wx0, wy1 - 1), *R.cell_xy(wx1 - 1, wy0))
            seen_ok = {}
            for g_, n_, ls_ in R.copper_objs:
                if n_ != net or not g_.intersects(wbox):
                    continue
                if id(g_) not in seen_ok:
                    comp_ = R.component(net, g_)
                    ok_ = _has_access(net, comp_)
                    for gg, _ in comp_:
                        seen_ok[id(gg)] = ok_
                if not seen_ok[id(g_)]:
                    continue
                win_, mm_ = R.patch(g_, grow=0)
                if win_ is None:
                    continue
                a0, a1 = max(win_[0], wy0), min(win_[1], wy1); b0, b1 = max(win_[2], wx0), min(win_[3], wx1)
                if a1 <= a0 or b1 <= b0:
                    continue
                sub = mm_[a0 - win_[0]:a1 - win_[0], b0 - win_[2]:b1 - win_[2]]
                for L in ls_:
                    if L in m_:
                        m_[L][a0 - wy0:a1 - wy0, b0 - wx0:b1 - wx0] |= sub
            accm[net] = m_
        return accm[net]

    def fmaps(net):
        if net not in cache:
            # dense boxes: minimum widths (short pieces); the high-current rails keep 0.25 (width pass widens later)
            w = 0.25 if net in ('VSYS', 'VBUS', 'VBAT_CELL', '3V3_DIG') else R.widths(net)[-1]
            m0_ = R.MARGIN
            R.MARGIN = FIXM + fixm.get(net, 0.0)     # vs FIXED copper: a little above the repair margin (raster rounding)
            try:
                free, via_ok = R.maps(net, w, W, VD, VH)
            finally:
                R.MARGIN = m0_
            cache[net] = (w, free, via_ok, plane_sites(net, via_ok) if net in ('GND', '3V0_ANA') else None)
            nid_ = R.NID.get(net, -1)       # the net's own fixed copper (pads, kept tracks): a path over it is not new copper
            ownfix[net] = {L: R.own[L][wy0:wy1, wx0:wx1] == nid_ for L in R.LAYERS}
        return cache[net]

    _disks = {}

    def disk(r):
        n_ = max(0, int(math.ceil(r / R.RES - 0.5)))
        if n_ not in _disks:
            yy, xx = np.mgrid[-n_:n_ + 1, -n_:n_ + 1]
            _disks[n_] = (xx * xx + yy * yy) <= (n_ + 0.5) ** 2
        return _disks[n_]

    INF = np.full(shp, 1e9, np.float32)
    xmarg = {}                      # per-task extra margin after an exact-check near miss
    res_of = {}                     # task -> (w, centre cells per layer (bool), via cells (bool), copper per layer, segs, vias)
    hist = {L: np.zeros(shp, np.float32) for L in R.LAYERS}
    hist_v = np.zeros(shp, np.float32)

    def zones(i):
        """penalty zones for task i from every OTHER net's current copper: (track zone per layer, via zone)"""
        net = tasks[i]['net']
        w = fmaps(net)[0]
        c, cw = G.base_clr(net), 0.25
        zt, zv = {}, np.zeros(shp, bool)
        for L in R.LAYERS:
            un = np.zeros(shp, bool); uw = np.zeros(shp, bool)
            for j, rj in res_of.items():
                if tasks[j]['net'] == net:
                    continue
                (uw if tasks[j]['net'] in G.WIDE else un)[:] |= rj[3][L]
            dn = _nd.distance_transform_edt(~un) * R.RES if un.any() else INF
            dw = _nd.distance_transform_edt(~uw) * R.RES if uw.any() else INF
            m_ = NMARG + xmarg.get(i, 0.0)
            zt[L] = (dn < c + w / 2 + m_) | (dw < cw + w / 2 + m_)
            zv |= (dn < c + VD / 2 + m_) | (dw < cw + VD / 2 + m_)
        return zt, zv

    def route_task(i, pres):
        t = tasks[i]; net = t['net']
        w, free0, via_ok, sites = fmaps(net)
        allowed = R.allowed_layers(net); lcost = R.layer_cost(net)
        zt, zv = zones(i)
        pen = {L: (pres * zt[L] + hist[L]).astype(np.float32) for L in R.LAYERS}
        for L in R.LAYERS:
            pen[L][ownfix[net][L]] = 0.0
        pen['VIA'] = (pres * zv + hist_v).astype(np.float32)
        free = {L: free0[L].copy() for L in R.LAYERS}
        segs_all, vias_all, cells = [], [], []
        if t['kind'] == 'conn':
            ca = R.component(net, t['ga']); cb = R.component(net, t['gb'])
            s = R.comp_nodes(ca, free, W, allowed) or R.end_nodes(t['ga'], set(R.LAYERS), free, W, allowed, relax=True)
            gl = R.comp_nodes(cb, free, W, allowed) or R.end_nodes(t['gb'], set(R.LAYERS), free, W, allowed, relax=True)
            if not s or not gl:
                return None
            for st in list(s) + list(gl):
                free[R.LAYERS[st[0]]][st[2], st[1]] = True
            p = R.astar(free, via_ok, s, gl, lcost, allowed, 500000, pen=pen)
            if not p:
                return None
            cells += p
            sg, vs = R.to_segments(p, W) if len(p) > 1 else ([], [])
            segs_all += sg; vias_all += vs
        elif t['kind'] == 'ptree':
            # plane-aware tree: every island reaches the plane - through a new via site, copper that already has plane
            # access, or the tree grown so far (which itself reached the plane first)
            am = access_mask(net)
            site_g = {(R.LAYERS.index(L), int(x_), int(y_)) for L in allowed for y_, x_ in zip(*np.nonzero(sites & free[L]))}
            acc_g = {(R.LAYERS.index(L), int(x_), int(y_)) for L in allowed for y_, x_ in zip(*np.nonzero(am[L]))}
            tree = set()
            for g in t['gs']:
                s = R.comp_nodes(R.component(net, g), free, W, allowed) or R.end_nodes(g, set(R.LAYERS), free, W, allowed, relax=True)
                if not s:
                    return None
                ss = set(s)
                if ss & tree:
                    continue
                goals = (tree | acc_g | site_g) - ss
                if not goals:
                    return None
                for st in ss | tree | acc_g:
                    free[R.LAYERS[st[0]]][st[2], st[1]] = True
                p = R.astar(free, via_ok, s, list(goals), lcost, allowed, 500000, pen=pen)
                if not p:
                    return None
                end = p[-1]
                cells += p
                sg, vs = R.to_segments(p, W) if len(p) > 1 else ([], [])
                segs_all += sg; vias_all += vs
                if end not in tree and end not in acc_g:          # ended on a new via site: the plane via itself
                    vias_all.append(R.cell_xy(end[1] + wx0, end[2] + wy0))
                tree |= ss | set(p)
        else:                       # tree: grow from the first touch point's copper
            tree = set(R.comp_nodes(R.component(net, t['gs'][0]), free, W, allowed))
            if not tree:
                return None
            for g in t['gs'][1:]:
                s = R.comp_nodes(R.component(net, g), free, W, allowed) or R.end_nodes(g, set(R.LAYERS), free, W, allowed, relax=True)
                if not s:
                    return None
                if tree & set(s):
                    continue
                for st in list(s) + list(tree):
                    free[R.LAYERS[st[0]]][st[2], st[1]] = True
                p = R.astar(free, via_ok, s, list(tree), lcost, allowed, 500000, pen=pen)
                if not p:
                    return None
                cells += p; tree |= set(p)
                sg, vs = R.to_segments(p, W) if len(p) > 1 else ([], [])
                segs_all += sg; vias_all += vs
        cen = {L: np.zeros(shp, bool) for L in R.LAYERS}
        for L_, x_, y_ in cells:
            cen[R.LAYERS[L_]][y_, x_] = True
        for L in R.LAYERS:
            cen[L] &= ~ownfix[net][L]      # path cells inside the net's own pads / kept copper are not new copper
        vm = np.zeros(shp, bool)
        for x_, y_ in vias_all:
            ix_ = int(round((x_ - R.X0) / R.RES - 0.5)) - wx0; iy_ = int(round((R.Y1 - y_) / R.RES - 0.5)) - wy0
            if 0 <= ix_ < shp[1] and 0 <= iy_ < shp[0]:
                vm[iy_, ix_] = True
        dt, dv = disk(w / 2), disk(VD / 2)
        vcu = _nd.binary_dilation(vm, dv) if vm.any() else vm
        cu = {L: (_nd.binary_dilation(cen[L], dt) if cen[L].any() else cen[L]) | vcu for L in R.LAYERS}
        return w, cen, vm, cu, segs_all, vias_all

    ok_all, accepted_rows = False, None
    NEG_EXACT_AT = int(os.environ.get('NEG_EXACT_AT', '4'))
    SEED = os.environ.get('NEG_SEED') == '1'

    def or_patch(mask, g_):
        win_, mm_ = R.patch(g_, grow=0)
        if win_ is None:
            return
        a0, a1 = max(win_[0], wy0), min(win_[1], wy1); b0, b1 = max(win_[2], wx0), min(win_[3], wx1)
        if a1 > a0 and b1 > b0:
            mask[a0 - wy0:a1 - wy0, b0 - wx0:b1 - wx0] |= mm_[a0 - win_[0]:a1 - win_[0], b0 - win_[2]:b1 - win_[2]]

    def orig_result(i):
        """a victim task's ORIGINAL copper as its current result (seeded negotiation); segs None = keep original"""
        t_ = tasks[i]; net_ = t_['net']; w_ = fmaps(net_)[0]
        cen_ = {L: np.zeros(shp, bool) for L in R.LAYERS}; cu_ = {L: np.zeros(shp, bool) for L in R.LAYERS}
        vm_ = np.zeros(shp, bool)
        for m_ in (cluster_of.get(t_['nm']) or [t_['nm']]):
            for r_ in groups[m_]['rows']:
                if r_['kind'] == 'TRACK':
                    ln = LineString([(float(r_['x1']), float(r_['y1'])), (float(r_['x2']), float(r_['y2']))])
                    if r_['layer'] in cen_:
                        or_patch(cen_[r_['layer']], ln.buffer(0.02))
                        or_patch(cu_[r_['layer']], ln.buffer(float(r_['w']) / 2))
                else:
                    pt_ = Point(float(r_['x1']), float(r_['y1']))
                    or_patch(vm_, pt_.buffer(0.02))
                    for L in R.LAYERS:
                        or_patch(cu_[L], pt_.buffer(float(r_['d'] or 0.6) / 2))
        for L in R.LAYERS:
            cen_[L] &= ~ownfix[net_][L]
        return w_, cen_, vm_, cu_, None, None

    in_task = set()
    for t_ in tasks:
        if 'nm' in t_:
            in_task |= set(cluster_of.get(t_['nm']) or [t_['nm']])
    notask = [nm for nm in vl if nm not in in_task]
    if SEED and notask:
        # pieces nobody has to reconnect (dangling / already on the plane): keep them where they are
        for nm in notask:
            for e in groups[nm]['entries']:
                R.stamp(e[0], e[1], e[2]); R.copper_objs.append(e)
            for r_ in groups[nm]['rows']:
                if r_['kind'] == 'VIA':
                    hg = Point(float(r_['x1']), float(r_['y1'])).buffer(float(r_['h'] or 0.3) / 2, 12); hole_geoms.append(hg)
                    win_, mm_ = R.patch(hg)
                    if win_:
                        R.holes[win_[0]:win_[1], win_[2]:win_[3]] |= mm_
        print(f'  seed: {len(notask)} pieces without a task kept in place', flush=True)
    reroute = set(range(len(tasks)))
    if SEED:
        reroute = {i for i, t_ in enumerate(tasks) if 'nm' not in t_}
        for i, t_ in enumerate(tasks):
            if 'nm' in t_:
                res_of[i] = orig_result(i)

    def rows_now():
        out_ = []
        for i_, t_ in enumerate(tasks):
            w_, cen_, vm_, cu_, sg_, vs_ = res_of[i_]
            if sg_ is None:
                continue            # kept original copper: not re-added
            out_ += rows_for(t_['net'], (sg_, vs_, w_, VD, VH, False), t_['tag'], t_['key'])
        return out_

    def kept_groups():
        k_ = set(notask) if SEED else set()
        for i_, t_ in enumerate(tasks):
            if i_ in res_of and res_of[i_][4] is None and 'nm' in t_:
                k_ |= set(cluster_of.get(t_['nm']) or [t_['nm']])
        return k_
    for it in range(NITER):
        pres = min(PCAP, 0.5 * 1.5 ** it)
        order = list(range(len(tasks)))
        rng.shuffle(order)
        missing = 0
        for i in order:
            if i not in reroute:
                continue
            res_of.pop(i, None)
            r_ = route_task(i, pres)
            if r_ is None:
                missing += 1
                print(f'  it {it}: task {i} {tasks[i]["kind"]} {tasks[i]["net"]} has no path at all', flush=True)
                continue
            res_of[i] = r_
        n_conf, bad, conf_i = 0, [], set()
        for i in list(res_of):
            zt, zv = zones(i)
            w, cen, vm, cu, sg, vs = res_of[i]
            hit = False
            for L in R.LAYERS:
                cc = cen[L] & zt[L]
                if cc.any():
                    hit = True; hist[L][cc] += HINC
            vv = vm & zv
            if vv.any():
                hit = True; hist_v[vv] += HINC
            if hit:
                n_conf += 1; bad.append(tasks[i]['net'])
                conf_i.add(i)
        n_orig = sum(1 for i_ in res_of if res_of[i_][4] is None)
        print(f'  it {it}: pres {pres:.1f}, in conflict {n_conf}/{len(tasks)} {sorted(set(bad))}, no path {missing}'
              + (f', still original {n_orig}' if SEED else ''), flush=True)
        reroute = (conf_i | {i for i in range(len(tasks)) if i not in res_of}) if SEED else set(range(len(tasks)))
        if SEED and it + 1 < int(os.environ.get('NEG_HOLD', '6')):
            # hold phase: the new connections adapt first (rising price); original copper only moves afterwards
            held = {i for i in reroute if 'nm' in tasks[i] and i in res_of and res_of[i][4] is None}
            reroute -= held
        if missing == 0 and n_conf <= NEG_EXACT_AT:
            # the raster zone is deliberately conservative (NMARG): the exact model is the judge
            rows_try = rows_now()
            kg = kept_groups()
            if exact_ok(rows_try, [o for nm in vl if nm not in kg for o in objs_of_group(nm)]):
                ok_all, accepted_rows = True, rows_try
                print(f'  it {it}: exact check PASSED with {n_conf} raster conflicts', flush=True)
                break
            print(f'  it {it}: exact check: {LAST_FAIL[0][:160]}', flush=True)
            # near miss: the new copper named in the failure gets a wider zone and is re-routed next pass
            msg = LAST_FAIL[0].split()
            fnets = set()
            if msg[:2] == ['new-new', 'clearance']:
                fnets = {msg[2], msg[msg.index('vs') + 1]}
            elif msg and msg[0] == 'clearance':
                fnets = {msg[1]}
                fixm[msg[1]] = fixm.get(msg[1], 0.0) + 0.025     # the miss is against fixed copper: widen its maps
                cache.pop(msg[1], None)
            for i_, t_ in enumerate(tasks):
                if t_['net'] in fnets and i_ in res_of and res_of[i_][4] is not None:
                    xmarg[i_] = xmarg.get(i_, 0.0) + 0.025
                    reroute.add(i_)
            if n_conf == 0:
                NMARG += 0.025      # raster says clean, exact disagrees: widen the raster zone and keep going
                print(f'  it {it}: raster clean but exact not -> NEG_MARGIN {NMARG:.3f}', flush=True)
        if it == NITER - 1:         # where the last conflicts are (world mm, layer) -> placement / policy decisions
            for i in list(res_of):
                zt, zv = zones(i)
                w, cen, vm, cu, sg, vs = res_of[i]
                pts_ = []
                for L in R.LAYERS:
                    ys_, xs_ = np.nonzero(cen[L] & zt[L])
                    pts_ += [(L, *[round(v, 2) for v in R.cell_xy(x_ + wx0, y_ + wy0)]) for y_, x_ in zip(ys_, xs_)]
                ys_, xs_ = np.nonzero(vm & zv)
                pts_ += [('VIA', *[round(v, 2) for v in R.cell_xy(x_ + wx0, y_ + wy0)]) for y_, x_ in zip(ys_, xs_)]
                if pts_:
                    print(f'   conflict {tasks[i]["kind"]} {tasks[i]["net"]}: {len(pts_)} cells, e.g. {pts_[:: max(1, len(pts_) // 6)][:6]}',
                          flush=True)
    if ok_all:
        rows_all = accepted_rows
        kg = kept_groups()
        moved = [nm for nm in vl if nm not in kg]
        for nm in moved:
            dels.extend(groups[nm]['rows']); dead_groups.add(nm)
        adds.extend(rows_all)
        gained += len(targets)
        save_outputs()
        print(f'NEGOTIATE accepted: {len(targets)} targets, {len(tasks)} tasks ({len(kg)} pieces kept as they were), '
              f'adds {len(rows_all)} rows, dels {sum(len(groups[nm]["rows"]) for nm in moved)} rows', flush=True)
    else:
        print('NEGOTIATE did not converge', flush=True)
        restore(s_before)
    sys.exit(0)
if os.environ.get('REGIONS'):
    first = [p for p in os.environ.get('FIRST_NETS', '').split(',') if p]
    for bx in os.environ['REGIONS'].split(';'):
        region_pass(tuple(map(float, bx.split(','))), first)
    if os.environ.get('REGION_ONLY'):
        PASSES = 0
for ps in range(PASSES):
    todo, gain_pass = list(conns), 0
    conns = []
    for net, a, b in todo:
        k += 1
        ck = '|'.join(R.key((net, a, b)))
        res, why = route_conn_safe(net, a, b, lambda r_: exact_ok(rows_for(net, r_, 'chk', ck)))
        if res and why == 'already connected':
            gained += 1; gain_pass += 1; continue
        if res:
            rows = rows_for(net, res, f'P{k}:{net}', ck)
            if exact_ok(rows):
                stamp_rows(rows); commit_exact(rows, []); adds += rows; gained += 1; gain_pass += 1; save_outputs()
                print(f'  [{time.time() - t0:.0f}s] direct {net}', flush=True); continue
        if DEBUG:
            print(f'  direct fail {net} {R.key((net, a, b))}: {why if not res else "exact check: " + LAST_FAIL[0]}', flush=True)
        # victims in the corridor / near the ends
        pe = plane_end(net, a, b) if PLANE and net in ('GND', '3V0_ANA') else None
        pa, pb = (pe['pts'][0], pe['pts'][0]) if pe else (a['pts'][0], b['pts'][0])
        zone = LineString([pa, pb]).buffer(CORRIDOR) if pa != pb else Point(pa).buffer(CORRIDOR)
        zone = zone.union(Point(pa).buffer(CORRIDOR)).union(Point(pb).buffer(CORRIDOR))
        vict = {}
        for e in R.copper_objs:
            nm = entry_group.get(id(e))
            if nm and nm not in dead_groups and e[1] != net and e[0].intersects(zone):
                d = e[0].distance(LineString([pa, pb]) if pa != pb else Point(pa))
                vict[nm] = min(vict.get(nm, 9e9), d)
        vl = sorted(vict, key=vict.get)[:MAXV]
        if GUIDED:
            gv, gwhy, _ = fixed_path_victims(net, a, b, conn_box(a, b, GUIDED))
            if DEBUG:
                print(f'  guided {net}: {gwhy}; victims {[groups[v]["net"] for v in gv] if gv is not None else None}', flush=True)
            if gv:
                vl = [split_group(nm, LAST_PATH[0]) for nm in gv]
        if not vl:
            conns.append((net, a, b)); continue
        set_ends(vl)
        s_before = snap()
        rip_names(vl)
        s_ripped = snap()
        _rem = [o for nm in vl for o in objs_of_group(nm)]
        # attempt order: target first, then the victims; when a victim cannot be reconnected, undo and retry with that
        # victim routed BEFORE the target (it keeps its corridor and the target finds another way), up to REORDER times
        first_v, tries = [], 0
        while True:
            new_blocks, ok, fail_at, failed_v = [], True, '', None
            if os.environ.get('DEBUG_TRY'):
                _t = route_conn(net, a, b)
                print(f'    [try {tries}] victims {len(vl)} first_v {len(first_v)} own '
                      f'{[int((R.own[L] != 0).sum()) for L in R.LAYERS]} holes {int(R.holes.sum())} cu {len(R.copper_objs)} '
                      f'hg {len(hole_geoms)} -> target alone: {_t[1]}', flush=True)
            for nm in first_v:
                okv, bl = reconnect(nm, f'P{k}v:{groups[nm]["net"]}', _rem)
                new_blocks += bl
                if not okv:
                    ok = False; fail_at = f'victim-first {nm}'; break
            if ok:
                res, why = route_conn_safe(net, a, b, lambda r_: exact_ok(rows_for(net, r_, 'chk', ck), _rem))
                if not res:
                    ok = False; fail_at = f'target ({why}) [{LAST_PLANE[0]}]'
                    if CASCADE and first_v and tries < REORDER:
                        # reverse cascade: the victims routed first now block the target -> the groups blocking the
                        # target around them (measured in place) become victims too; keep the victim-first order
                        hv, _w, _r = fixed_path_victims(net, a, b, conn_box(a, b, GUIDED or 2.0))
                        extra = {split_group(h, LAST_PATH[0]) for h in (hv or [])
                                 if h not in vl and h not in dead_groups and groups[h]['net'] != net}
                        if extra and len(vl) + len(extra) <= CASCADE:
                            restore(s_before)
                            vl = vl + sorted(extra)
                            set_ends(vl)
                            rip_names(vl)
                            s_ripped = snap()
                            _rem = [o for nm in vl for o in objs_of_group(nm)]
                            if DEBUG:
                                print(f'    reverse cascade (target blocked by victim-first): + '
                                      f'{[groups[h]["net"] for h in sorted(extra)]}', flush=True)
                            tries += 1
                            continue
                elif why != 'already connected':
                    rows = rows_for(net, res, f'P{k}:{net}', ck); new_blocks.append(stamp_rows(rows) + (rows,))
            if ok:
                for nm in vl:
                    if nm in first_v or len(ends_cache[nm]) < 2:
                        continue            # dangling piece: simply dropped
                    okv, bl = reconnect(nm, f'P{k}v:{groups[nm]["net"]}', _rem)
                    new_blocks += bl
                    if not okv:
                        ok = False; failed_v = nm; fail_at = f'victim {nm} ({len(ends_cache[nm])} touch points)'; break
            if ok:
                all_rows = [r for ents, hs, rows in new_blocks for r in rows]
                removed_o = [o for nm in vl for o in objs_of_group(nm)]
                ok = exact_ok(all_rows, removed_o)
                if not ok:
                    fail_at = 'exact: ' + LAST_FAIL[0]
            if ok or failed_v is None or tries >= REORDER:
                break
            cascaded = False
            extra = set()
            if CASCADE:
                # rip-up cascade: the groups blocking the failed victim become victims too.  Measured NOW, with the target
                # and the victims routed so far in place (new copper belongs to no group = fixed), so the blockers found
                # are the ones that matter around the target's route; then restart from the exact pre-rip state.
                vp, vnet = ends_cache[failed_v], groups[failed_v]['net']
                for q in vp[1:]:
                    ea, eb = pt_end(vp[0]), pt_end(q)
                    hv, _w, _r = fixed_path_victims(vnet, ea, eb, conn_box(ea, eb, GUIDED or 2.0))
                    extra |= {split_group(h, LAST_PATH[0]) for h in (hv or [])
                              if h not in vl and h not in dead_groups and groups[h]['net'] != net}
            restore(s_ripped)
            if CASCADE:
                if extra and len(vl) + len(extra) <= CASCADE:
                    restore(s_before)
                    vl = vl + sorted(extra)
                    set_ends(vl)
                    rip_names(vl)
                    s_ripped = snap()
                    _rem = [o for nm in vl for o in objs_of_group(nm)]
                    cascaded = True
                    if DEBUG:
                        print(f'    cascade from {groups[failed_v]["net"]}: + {[groups[h]["net"] for h in sorted(extra)]}', flush=True)
            if not cascaded:                # a cascade gives the failed victim new room: retry target-first
                first_v.append(failed_v)
            tries += 1
        if DEBUG and not ok:
            print(f'  repair fail {net} {ck[:70]}: victims {[groups[v]["net"] for v in vl]} -> {fail_at}', flush=True)
        if ok:
            for nm in vl:
                dels += groups[nm]['rows']; dead_groups.add(nm)
            for ents, hs, rows in new_blocks:
                adds += rows
            commit_exact(all_rows, removed_o)
            gained += 1; gain_pass += 1; save_outputs()
            print(f'  [{time.time() - t0:.0f}s] repaired {net} (victims {len(vl)})', flush=True)
        else:
            restore(s_before)                               # victims back exactly, attempt copper gone
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
