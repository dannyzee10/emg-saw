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
                        h.geom.distance(c.buffer(hr)) < 0.254 - 1e-6:
                    return _fail('hole-hole')
    for i, (ra, a) in enumerate(new):
        for rb, b in new[i + 1:]:
            if a.net != b.net and a.layers & b.layers and a.geom.distance(b.geom) < G.required(a, b) - 1e-6:
                return _fail('new-new clearance')
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
    finally:
        R.MARGIN, R.widths = m0, wf
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
            if q == pts[0]:
                return False, blocks_
            r2, w2 = _route_checked(net_, pt_end(pts[0]), e, tag, 'repair|' + nm, rem)
            if not r2:
                return False, blocks_
            if w2 != 'already connected':
                rows = rows_for(net_, r2, tag, 'repair|' + nm)
                blocks_.append(stamp_rows(rows) + (rows,))
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
        for m in members[1:]:
            ends_cache[m] = []



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
    for w in R.widths(net):
        W = R.window(g, g, PLANE_WIN)
        free, via_ok = R.maps(net, w, W, 0.45, 0.2)
        if net == '3V0_ANA' or PLANE_DEAD:
            iy0, iy1, ix0, ix1 = W
            ys, xs = np.nonzero(via_ok)
            for y, x in zip(ys, xs):
                cx, cy = R.cell_xy(x + ix0, y + iy0)
                if (net == '3V0_ANA' and not _ANA_IN.contains(Point(cx, cy))) or (net == 'GND' and _dead(cx, cy)):
                    via_ok[y, x] = False
        for L in [L for L in R.LAYERS if L in ls]:
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


def route_conn(net, a, b):
    if PLANE and net in ('GND', '3V0_ANA'):
        e = plane_end(net, a, b)
        if e is not None:
            res, why = route_plane(net, e)
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
                if abs(h.geom.centroid.x - c.x) < 1.2 and abs(h.geom.centroid.y - c.y) < 1.2 and h.geom.distance(o.geom) < 0.254 - 1e-6:
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
                stamp_rows(rows); commit_exact(rows, []); adds += rows; gained += 1; gain_pass += 1
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
        if not vl:
            conns.append((net, a, b)); continue
        set_ends(vl)
        saved = {nm: list(groups[nm]['entries']) for nm in vl}
        vias_of = {nm: [(float(r['x1']), float(r['y1']), float(r['h'] or 0.3)) for r in groups[nm]['rows'] if r['kind'] == 'VIA'] for nm in vl}
        for nm in vl:
            unstamp(saved[nm]); unstamp_holes(vias_of[nm])
            for (x, y, h) in vias_of[nm]:
                for g in [g for g in hole_geoms if abs(g.centroid.x - x) < 1e-6 and abs(g.centroid.y - y) < 1e-6]:
                    hole_geoms.remove(g)
        _rem = [o for nm in vl for o in objs_of_group(nm)]
        # attempt order: target first, then the victims; when a victim cannot be reconnected, undo and retry with that
        # victim routed BEFORE the target (it keeps its corridor and the target finds another way), up to REORDER times
        first_v, tries = [], 0
        while True:
            new_blocks, ok, fail_at, failed_v = [], True, '', None
            for nm in first_v:
                okv, bl = reconnect(nm, f'P{k}v:{groups[nm]["net"]}', _rem)
                new_blocks += bl
                if not okv:
                    ok = False; fail_at = f'victim-first {nm}'; break
            if ok:
                res, why = route_conn_safe(net, a, b, lambda r_: exact_ok(rows_for(net, r_, 'chk', ck), _rem))
                if not res:
                    ok = False; fail_at = f'target ({why})'
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
            for ents, hs, rows in reversed(new_blocks):
                remove_rows(ents, hs)
            first_v.append(failed_v); tries += 1
        if DEBUG and not ok:
            print(f'  repair fail {net} {ck[:70]}: victims {[groups[v]["net"] for v in vl]} -> {fail_at}', flush=True)
        if ok:
            for nm in vl:
                dels += groups[nm]['rows']; dead_groups.add(nm)
            for ents, hs, rows in new_blocks:
                adds += rows
            commit_exact(all_rows, removed_o)
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
