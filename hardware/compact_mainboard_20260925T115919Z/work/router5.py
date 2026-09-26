"""router5 (see make_router5.py for the changes vs router4).  Deterministic, rule-aware grid router v3 (offline planner; Altium DRC is the authority).

Copper model: per-layer net-ownership rasters at 0.05 mm (L1 Top, L3 Mid Layer 2, L4 Bottom; L2 is never
routed), built once from the native geometry export and updated incrementally with every routed segment.
Per connection: window crop -> distance fields to other-net copper split by rule class -> free maps ->
A* (8 directions, via moves, per-net layer costs, mild turn penalty) -> 45-degree segments, split at the
CLR_FINE_ESCAPE region boundaries so the 0.15 mm escape rule really applies to the segments it was used for.

Rules modelled: class clearance (0.25 EMG_POWER/ANALOG/ADC/REFERENCE, else 0.20), 0.15 track-to-pad of
fine-pitch parts inside their escape regions, keepouts, 0.5 mm board edge, vias 0.6/0.3 mm with no via on
any pad and 0.254 mm hole-to-hole. MARGIN absorbs rasterisation error; build_ops.py re-checks exactly.

usage: GEOM_FILE=... python router3.py DRC.json [netA,netB,...]
Writes evidence/ROUTE_PLAN.csv, evidence/ROUTE_FAILED.txt
"""
import csv, heapq, json, math, os, re, sys, time
import numpy as np
from scipy import ndimage
from PIL import Image, ImageDraw
from shapely.geometry import LineString, Point, box
import geom as G

RES = 0.05
_g = [float(v) for v in os.environ.get('GRID', '9.5,9.5,90.5,55.5').split(',')]
X0, Y1 = _g[0], _g[3]
NX, NY = int(round((_g[2] - X0) / RES)), int(round((Y1 - _g[1]) / RES))
LAYERS = ['Top Layer', 'Mid Layer 2', 'Bottom Layer']
MARGIN = 0.06
VIA_D, VIA_H = 0.6, 0.3
VIA_COST = 1.5
TURN = 0.06

objs, comps, keepouts = G.load()
net_names = sorted({o.net for o in objs if o.net not in ('', '-')})
NID = {n: i + 1 for i, n in enumerate(net_names)}
IS_WIDE = np.zeros(len(net_names) + 2, bool)
for n, i in NID.items():
    IS_WIDE[i] = n in G.WIDE
classes = {}
for l in open(G.CLASSES, encoding='utf-8', errors='replace'):
    f = l.rstrip('\n').split('|')
    if f[0] == 'MEMBER' and f[1].startswith('EMG_'):
        classes.setdefault(f[2], set()).add(f[1])
bottom_nets = {o.net for o in objs if o.kind == 'PAD' and o.layers == {'Bottom Layer'}}
DRL_TAPS = {f'{v}_{n}' for v in ('Va', 'Vb', 'Vc') for n in range(1, 6)}


def cls(net):
    return classes.get(net, set())


def widths(net):
    c = cls(net)
    if 'EMG_SWITCH' in c:
        return [0.3, 0.2]
    if 'EMG_POWER' in c:
        return [0.4, 0.25, 0.15]
    if net == 'GND':
        return [0.3, 0.2, 0.15]
    if 'EMG_SPI' in c:
        return [0.18, 0.15]
    return [0.2, 0.15]


def layer_cost(net):
    c = cls(net)
    if net in DRL_TAPS:
        return {'Top Layer': 1.3, 'Mid Layer 2': 1.0, 'Bottom Layer': 2.0}
    if c & {'EMG_ANALOG', 'EMG_ADC', 'EMG_REFERENCE', 'EMG_CRYSTAL'}:
        return {'Top Layer': 1.0, 'Mid Layer 2': 1.8, 'Bottom Layer': 3.0}
    if 'EMG_SPI' in c:
        return {'Top Layer': 1.0, 'Mid Layer 2': 1.0, 'Bottom Layer': 3.0}
    if 'EMG_POWER' in c:
        return {'Top Layer': 1.0, 'Mid Layer 2': 1.1, 'Bottom Layer': 2.5}
    return {'Top Layer': 1.0, 'Mid Layer 2': 1.2, 'Bottom Layer': 3.0}


NO_VIA = {'NetL1_1', 'NetL1_2', 'MCU_VCAP'}   # report P2 (LX: no vias) and M2 (VCAP: no via)


def allowed_layers(net):
    if net in NO_VIA:
        return {'Top Layer'}
    return set(LAYERS) if net in bottom_nets else {'Top Layer', 'Mid Layer 2'}


# ------------------------------------------------------------------ rasters
def polys(g):
    return [g] if g.geom_type == 'Polygon' else [p for p in getattr(g, 'geoms', []) if p.geom_type == 'Polygon']


def patch(g, grow=1):
    b = g.bounds
    ix0 = max(0, int(math.floor((b[0] - X0) / RES)) - grow); ix1 = min(NX, int(math.ceil((b[2] - X0) / RES)) + grow + 1)
    iy0 = max(0, int(math.floor((Y1 - b[3]) / RES)) - grow); iy1 = min(NY, int(math.ceil((Y1 - b[1]) / RES)) + grow + 1)
    if ix1 <= ix0 or iy1 <= iy0:
        return None, None
    img = Image.new('1', (ix1 - ix0, iy1 - iy0), 0)
    d = ImageDraw.Draw(img)
    for p in polys(g):
        if not p.is_empty:
            d.polygon([((x - X0) / RES - 0.5 - ix0, (Y1 - y) / RES - 0.5 - iy0) for x, y in p.exterior.coords], fill=1, outline=1)
    return (iy0, iy1, ix0, ix1), np.array(img, bool)


def cell_xy(ix, iy):
    return X0 + (ix + 0.5) * RES, Y1 - (iy + 0.5) * RES


own = {L: np.zeros((NY, NX), np.int32) for L in LAYERS}
finepad = {L: np.zeros((NY, NX), bool) for L in LAYERS}
anypad = np.zeros((NY, NX), bool)
holes = np.zeros((NY, NX), bool)
keep = np.zeros((NY, NX), bool)
fine_region = np.zeros((NY, NX), bool)
copper_objs = []   # (geom, net, layers) incl. new copper, for endpoint matching


def stamp(g, net, layers, is_fine=False, is_pad=False):
    win, m = patch(g)
    if win is None:
        return
    iy0, iy1, ix0, ix1 = win
    nid = NID.get(net, 0)
    for L in layers:
        if L in own:
            sub = own[L][iy0:iy1, ix0:ix1]
            if nid:
                sub[m] = nid
            else:
                sub[m] = len(net_names) + 1  # net-less copper: obstacle to everyone
            if is_fine:
                finepad[L][iy0:iy1, ix0:ix1] |= m
    if is_pad:
        anypad[iy0:iy1, ix0:ix1] |= m


for o in objs:
    if o.kind in ('PAD', 'TRACK', 'VIA', 'ARC', 'REGION', 'FILL'):
        stamp(o.geom, o.net, o.layers, is_fine=(o.kind == 'PAD' and o.comp in G.FINE_REGIONS), is_pad=(o.kind == 'PAD'))
        copper_objs.append((o.geom, o.net, set(o.layers) & set(LAYERS) if o.kind != 'VIA' else set(LAYERS)))
    elif o.kind == 'HOLE':
        win, m = patch(o.geom)
        if win:
            holes[win[0]:win[1], win[2]:win[3]] |= m
    elif o.kind == 'KEEPOUT':
        win, m = patch(o.geom)
        if win:
            keep[win[0]:win[1], win[2]:win[3]] |= m
for r in G.FINE_REGIONS.values():
    win, m = patch(r, grow=0)
    fine_region[win[0]:win[1], win[2]:win[3]] |= m
inside = np.zeros((NY, NX), bool)
win, m = patch(G.BOARD, grow=0)
inside[win[0]:win[1], win[2]:win[3]] |= m
D_EDGE = ndimage.distance_transform_edt(inside) * RES
INIT = ({L: own[L].copy() for L in LAYERS}, holes.copy(), len(copper_objs))


def reset_state():
    for L in LAYERS:
        own[L][:] = INIT[0][L]
    holes[:] = INIT[1]
    del copper_objs[INIT[2]:]
D_KEEP = ndimage.distance_transform_edt(~keep) * RES
D_ANYPAD = ndimage.distance_transform_edt(~anypad) * RES


def edt(mask):
    if not mask.any():
        return np.full(mask.shape, 99.0)
    return ndimage.distance_transform_edt(~mask) * RES


def maps(net, w, W, vd=VIA_D, vh=VIA_H, relax=False):
    iy0, iy1, ix0, ix1 = W
    nid = NID[net]
    c = 0.2 if relax else G.base_clr(net); hw = w / 2
    cw = 0.2 if relax else 0.25          # vs other nets' EMG_POWER/ANALOG/ADC/REFERENCE copper
    cf = 0.2 if relax else None          # vs fine-pitch pads (None: 0.15 in escape regions, else 0.25)
    fr = fine_region[iy0:iy1, ix0:ix1]
    free = {}
    via_ok = np.ones((iy1 - iy0, ix1 - ix0), bool)
    for L in LAYERS:
        o = own[L][iy0:iy1, ix0:ix1]
        other = (o != 0) & (o != nid)
        fp = other & finepad[L][iy0:iy1, ix0:ix1]
        wd = other & IS_WIDE[np.clip(o, 0, len(IS_WIDE) - 1)] & ~fp
        nm = other & ~wd & ~fp
        dn, dw, df = edt(nm), edt(wd), edt(fp)
        ok = (dn >= c + hw + MARGIN) & (dw >= cw + hw + MARGIN) & (df >= (cf if cf is not None else np.where(fr, 0.15, 0.25)) + hw + MARGIN)
        ok &= (D_KEEP[iy0:iy1, ix0:ix1] >= c + hw + MARGIN) & (D_EDGE[iy0:iy1, ix0:ix1] >= 0.5 + hw + MARGIN)
        free[L] = ok
        r = vd / 2
        via_ok &= (dn >= c + r + MARGIN) & (dw >= cw + r + MARGIN) & (df >= (cf if cf is not None else 0.25) + r + MARGIN)
    via_ok &= (D_KEEP[iy0:iy1, ix0:ix1] >= c + vd / 2 + MARGIN) & (D_EDGE[iy0:iy1, ix0:ix1] >= 0.5 + vd / 2 + MARGIN)
    via_ok &= D_ANYPAD[iy0:iy1, ix0:ix1] >= vd / 2 + 0.05 + MARGIN
    via_ok &= edt(holes[iy0:iy1, ix0:ix1]) >= vh / 2 + 0.254 + MARGIN
    return free, via_ok


# ------------------------------------------------------------------ connections
def parse_conn(s):
    m = re.match(r'Un-Routed Net Constraint: Net (\S+) Between (.*) And (.*)$', s.strip())
    if not m:
        return None
    ends = []
    for part in (m.group(2), m.group(3)):
        pts = [(float(a), float(b)) for a, b in re.findall(r'\(([-\d.]+)mm,\s*([-\d.]+)mm\)', part)]
        ends.append({'kind': part.split()[0], 'pts': pts, 'text': part.strip()})
    return m.group(1), ends[0], ends[1]


def end_copper(end, net):
    probe = LineString(end['pts']) if end['kind'] == 'Track' and len(end['pts']) == 2 else Point(end['pts'][0])
    best = None
    for g, n, ls in copper_objs:
        if n != net:
            continue
        b = g.bounds
        if b[0] > probe.bounds[2] + 0.3 or b[2] < probe.bounds[0] - 0.3 or b[1] > probe.bounds[3] + 0.3 or b[3] < probe.bounds[1] - 0.3:
            continue
        d = g.distance(probe)
        if best is None or d < best[0]:
            best = (d, g, ls)
    if best is None or best[0] > 0.2:
        return None, set()
    return best[1], best[2]


def end_nodes(g, layers, free, W, allowed, relax=False):
    iy0, iy1, ix0, ix1 = W
    inner = g.buffer(-0.02) if g.area > 0.02 else g
    win, m = patch(inner if not inner.is_empty else g, grow=0)
    out = []
    if win is None:
        return out
    a0, a1, b0, b1 = max(win[0], iy0), min(win[1], iy1), max(win[2], ix0), min(win[3], ix1)
    if a1 <= a0 or b1 <= b0:
        return out
    mm = m[a0 - win[0]:a1 - win[0], b0 - win[2]:b1 - win[2]]
    for L in layers:
        if L not in allowed:
            continue
        f = free[L][a0 - iy0:a1 - iy0, b0 - ix0:b1 - ix0]
        sel = mm & f if not relax else mm
        ys, xs = np.nonzero(sel)
        out += [(LAYERS.index(L), int(x) + b0 - ix0, int(y) + a0 - iy0) for x, y in zip(xs, ys)]
    return out


DIRS = [(1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0), (1, 1, 1.4142), (1, -1, 1.4142), (-1, 1, 1.4142), (-1, -1, 1.4142)]
IDX_BITS = 24                      # 3 layers x full-board window (1620 x 920) = 4.47 M cells < 2**24
IDX_MASK = (1 << IDX_BITS) - 1
FQ = 100000                        # f quantum 1e-5 cost units in the packed heap key


def astar(free, via_ok, starts, goals, lcost, allowed, max_expand=None):
    """A* over (layer, x, y) cells of the window.  State lives in flat numpy arrays; each heap entry is one
    int, (quantised f << IDX_BITS) | idx, so a full-budget search stays small.  g and the arrival direction
    are read back from best[] / dirs[]: an entry is only pushed on improvement, so the first pop of a cell
    carries its current best g, and closed[] drops the stale duplicates."""
    ny, nx = via_ok.shape
    plane = ny * nx
    assert len(LAYERS) * plane < 1 << IDX_BITS
    if max_expand is None:
        max_expand = min(1200000, 8 * plane)
    gx = sum(g[1] for g in goals) / len(goals); gy = sum(g[2] for g in goals) / len(goals)
    lc = [lcost[L] for L in LAYERS]
    minc = min(lc[i] for i, L in enumerate(LAYERS) if L in allowed)
    hk = RES * minc * 0.95
    frees = [free[L] for L in LAYERS]
    lays = [i for i, L in enumerate(LAYERS) if L in allowed]
    best = np.full(len(LAYERS) * plane, np.inf, np.float32)
    parent = np.full(len(LAYERS) * plane, -1, np.int32)
    dirs = np.full(len(LAYERS) * plane, -1, np.int8)
    closed = np.zeros(len(LAYERS) * plane, bool)
    goal = np.zeros(len(LAYERS) * plane, bool)
    for L, ix, iy in goals:
        goal[L * plane + iy * nx + ix] = True
    openq = []
    for L, ix, iy in starts:
        i = L * plane + iy * nx + ix
        best[i] = 0.0
        heapq.heappush(openq, (int(math.hypot(ix - gx, iy - gy) * hk * FQ) << IDX_BITS) | i)
    n = 0
    while openq:
        i = heapq.heappop(openq) & IDX_MASK
        if closed[i]:
            continue
        closed[i] = True
        g = float(best[i]); d_in = int(dirs[i])
        if goal[i]:
            path = []
            while i >= 0:
                L, r = divmod(int(i), plane); iy, ix = divmod(r, nx)
                path.append((L, ix, iy)); i = parent[i]
            return path[::-1]
        n += 1
        if n > max_expand:
            return None
        L, r = divmod(int(i), plane); iy, ix = divmod(r, nx)
        fr = frees[L]; mult = lc[L]; base = L * plane
        for k, (dx, dy, c) in enumerate(DIRS):
            jx, jy = ix + dx, iy + dy
            if 0 <= jx < nx and 0 <= jy < ny and fr[jy, jx]:
                if dx and dy and not (fr[iy, jx] and fr[jy, ix]):
                    continue
                j = base + jy * nx + jx
                if closed[j]:
                    continue
                ng = g + c * RES * mult + (TURN if (d_in >= 0 and k != d_in) else 0.0)
                if ng < best[j]:
                    best[j] = ng; parent[j] = i; dirs[j] = k
                    heapq.heappush(openq, (int((ng + math.hypot(jx - gx, jy - gy) * hk) * FQ) << IDX_BITS) | j)
        if via_ok[iy, ix]:
            for L2 in lays:
                if L2 != L and frees[L2][iy, ix]:
                    j = L2 * plane + iy * nx + ix
                    ng = g + VIA_COST
                    if not closed[j] and ng < best[j]:
                        best[j] = ng; parent[j] = i; dirs[j] = -1
                        heapq.heappush(openq, (int((ng + math.hypot(ix - gx, iy - gy) * hk) * FQ) << IDX_BITS) | j)
    return None


def to_segments(path, W):
    iy0, iy1, ix0, ix1 = W
    segs, vias, run = [], [], [path[0]]
    for a, b in zip(path, path[1:]):
        if a[0] != b[0]:
            if len(run) > 1:
                segs.append(run)
            vias.append(cell_xy(a[1] + ix0, a[2] + iy0)); run = [b]; continue
        run.append(b)
    if len(run) > 1:
        segs.append(run)
    out = []
    for pts in segs:
        simp = [pts[0]]
        for i in range(1, len(pts) - 1):
            d1 = (pts[i][1] - simp[-1][1], pts[i][2] - simp[-1][2]); d2 = (pts[i + 1][1] - pts[i][1], pts[i + 1][2] - pts[i][2])
            if d1[0] * d2[1] - d1[1] * d2[0] != 0:
                simp.append(pts[i])
        simp.append(pts[-1])
        out.append((LAYERS[pts[0][0]], [cell_xy(p[1] + ix0, p[2] + iy0) for p in simp]))
    return out, vias


def split_at_regions(p, q):
    """split a segment where it crosses a fine-escape region boundary (so every piece is inside or outside)."""
    ln = LineString([p, q]); cuts = [0.0, 1.0]
    for r in G.FINE_REGIONS.values():
        inter = ln.intersection(r.exterior)
        for g in ([inter] if inter.geom_type == 'Point' else list(getattr(inter, 'geoms', []))):
            if g.geom_type == 'Point':
                cuts.append(ln.project(g, normalized=True))
    cuts = sorted(set(round(c, 6) for c in cuts))
    pts = [ln.interpolate(c, normalized=True) for c in cuts]
    return [((a.x, a.y), (b.x, b.y)) for a, b in zip(pts, pts[1:]) if a.distance(b) > 1e-4]


def window(ga, gb, pad):
    b = ga.union(gb).bounds
    x0, y0, x1, y1 = b[0] - pad, b[1] - pad, b[2] + pad, b[3] + pad
    ix0 = max(0, int((x0 - X0) / RES)); ix1 = min(NX, int(math.ceil((x1 - X0) / RES)))
    iy0 = max(0, int((Y1 - y1) / RES)); iy1 = min(NY, int(math.ceil((Y1 - y0) / RES)))
    return (iy0, iy1, ix0, ix1)


def component(net, seed):
    """copper objects (geom, layers) electrically joined to seed: same net, touching, sharing a layer."""
    objs = [(g, ls) for g, n, ls in copper_objs if n == net]
    idx = next((i for i, (g, ls) in enumerate(objs) if g is seed), None)
    if idx is None:
        return [(seed, set(LAYERS))]
    from shapely.strtree import STRtree
    tree = STRtree([g for g, ls in objs])
    seen = {idx}; todo = [idx]
    while todo:
        i = todo.pop(); gi, li = objs[i]
        for j in tree.query(gi.buffer(0.002)):
            j = int(j)
            if j in seen:
                continue
            gj, lj = objs[j]
            if li & lj and gi.distance(gj) < 0.002:
                seen.add(j); todo.append(j)
    return [objs[i] for i in seen]


def comp_nodes(comp, free, W, allowed):
    out = set()
    for g, ls in comp:
        out.update(end_nodes(g, ls, free, W, allowed))
    return list(out)


def route_one(net, a, b):
    ga, la = end_copper(a, net); gb, lb = end_copper(b, net)
    if ga is None or gb is None:
        return None, 'endpoint not matched'
    if net == 'GND':
        ca, cb = [(ga, la)], [(gb, lb)]          # plane connectivity is not modelled for GND
    else:
        ca = component(net, ga)
        if any(g is gb for g, ls in ca):
            return ([], [], 0, 0, 0, False), 'already connected'
        cb = component(net, gb)
    allowed = allowed_layers(net); lcost = layer_cost(net)
    ws = widths(net); w0, wm = ws[0], ws[-1]
    wide = net in G.WIDE
    plan = [(w0, 0.6, 0.3, 2.0, False, 150000)]
    if wm != w0:
        plan.append((wm, 0.6, 0.3, 2.0, False, 150000))
    plan += [(wm, 0.45, 0.2, 2.0, False, 150000),
             (w0, 0.6, 0.3, 6.0, False, 400000), (wm, 0.45, 0.2, 6.0, False, 400000)]
    if wide:
        plan += [(wm, 0.45, 0.2, 2.0, True, 150000), (wm, 0.45, 0.2, 6.0, True, 400000)]
    plan += [(wm, 0.45, 0.2, 15.0, False, 600000)]
    if wide:
        plan += [(wm, 0.45, 0.2, 15.0, True, 600000)]
    last = 'no path'
    for w, vd, vh, pad, relax, budget in plan:
        W = window(ga, gb, pad)
        free, via_ok = maps(net, w, W, vd, vh, relax)
        s = comp_nodes(ca, free, W, allowed); t = comp_nodes(cb, free, W, allowed)
        if not s:
            s = end_nodes(ga, la, free, W, allowed, relax=True)
        if not t:
            t = end_nodes(gb, lb, free, W, allowed, relax=True)
        if not s or not t:
            last = f'no entry nodes (s {len(s)}, t {len(t)})'; continue
        for st in s:
            free[LAYERS[st[0]]][st[2], st[1]] = True
        for st in t:
            free[LAYERS[st[0]]][st[2], st[1]] = True
        path = astar(free, via_ok, s, t, lcost, allowed, budget)
        if path:
            segs, vias = to_segments(path, W)
            return (segs, vias, w, vd, vh, relax), ('ok relaxed' if relax else 'ok')
    return None, last


def prio(c):
    net, a, b = c
    cl = cls(net); d = math.dist(a['pts'][0], b['pts'][0])
    if cl & {'EMG_SWITCH', 'EMG_CRYSTAL'}:
        r = 0
    elif cl & {'EMG_ANALOG', 'EMG_ADC', 'EMG_REFERENCE'} and d < 5:
        r = 1
    elif 'EMG_POWER' in cl:
        r = 2
    elif cl & {'EMG_ANALOG', 'EMG_ADC', 'EMG_REFERENCE'}:
        r = 3
    elif 'EMG_SPI' in cl:
        r = 4
    elif net == 'GND':
        r = 6
    else:
        r = 5
    return (r, d)


def stamp_rows(rows):
    for r in rows:
        if r['kind'] == 'TRACK':
            w = float(r['w'])
            g = LineString([(float(r['x1']), float(r['y1'])), (float(r['x2']), float(r['y2']))]).buffer(w / 2, 8)
            stamp(g, r['net'], [r['layer']]); copper_objs.append((g, r['net'], {r['layer']}))
        else:
            x, y, vd, vh = float(r['x1']), float(r['y1']), float(r['d']), float(r['h'])
            g = Point(x, y).buffer(vd / 2, 16)
            stamp(g, r['net'], LAYERS); copper_objs.append((g, r['net'], set(LAYERS)))
            win, m = patch(Point(x, y).buffer(vh / 2, 12))
            holes[win[0]:win[1], win[2]:win[3]] |= m


def run_pass(conns, partial_path, preload=()):
    reset_state()
    rows, failed = list(preload), []
    done = {r['conn'] for r in preload}
    stamp_rows(preload)
    t0 = time.time()
    pf = open(partial_path, 'w', newline='')
    pw = csv.DictWriter(pf, fieldnames=['kind', 'group', 'net', 'layer', 'x1', 'y1', 'x2', 'y2', 'w', 'd', 'h', 'conn', 'relax'])
    pw.writeheader(); pw.writerows(rows); pf.flush()
    for k, (net, a, b) in enumerate(conns):
        ck = '|'.join(key((net, a, b)))
        if ck in done:
            continue
        res, why = route_one(net, a, b)
        if not res:
            failed.append((net, a, b, why)); continue
        segs, vias, w, vd, vh, relax = res
        rx = 1 if relax else 0
        if why == 'already connected':
            done.add(ck); continue
        new = []
        for L, pts in segs:
            for p, q in zip(pts, pts[1:]):
                for pp, qq in split_at_regions(p, q):
                    new.append({'kind': 'TRACK', 'group': f'R{k}:{net}', 'net': net, 'layer': L, 'x1': round(pp[0], 4), 'y1': round(pp[1], 4), 'x2': round(qq[0], 4), 'y2': round(qq[1], 4), 'w': w, 'd': '', 'h': '', 'conn': ck, 'relax': rx})
        for x, y in vias:
            new.append({'kind': 'VIA', 'group': f'R{k}:{net}', 'net': net, 'layer': 'Multi Layer', 'x1': round(x, 4), 'y1': round(y, 4), 'x2': '', 'y2': '', 'w': '', 'd': vd, 'h': vh, 'conn': ck, 'relax': rx})
        stamp_rows(new)
        rows += new
        pw.writerows(new); pf.flush()
        if k % 25 == 0:
            print(f'  {k + 1}/{len(conns)} failed {len(failed)} t={time.time() - t0:.0f}s', flush=True)
    pf.close()
    return rows, failed


def key(c):
    return (c[0], c[1]['text'], c[2]['text'])


def main():
    data = json.load(open(sys.argv[1]))
    only = set(sys.argv[2].split(',')) if len(sys.argv) > 2 and sys.argv[2] else None
    passes = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    conns = [c for c in (parse_conn(d) for d in data['details'] if d.startswith('Un-Routed')) if c]
    if only:
        conns = [c for c in conns if c[0] in only]
    conns.sort(key=prio)
    best = None
    hard = []
    tag = os.environ.get('OUT_TAG', '')
    preload = []
    if os.environ.get('RESUME'):
        preload = [r for r in csv.DictReader(open(os.environ['RESUME'])) if r.get('conn')]
        print(f'resume: {len(preload)} rows / {len({r["conn"] for r in preload})} connections pre-loaded', flush=True)
    for p in range(passes):
        hk = {key(c) for c in hard}
        order = [c for c in conns if key(c) in hk] + [c for c in conns if key(c) not in hk]
        t0 = time.time()
        rows, failed = run_pass(order, G.HERE + f'evidence/ROUTE_PARTIAL{tag}_p{p + 1}.csv', preload if p == 0 else ())
        print(f'PASS {p + 1}: routed {len(conns) - len(failed)}/{len(conns)} failed {len(failed)} ({time.time() - t0:.0f}s)', flush=True)
        if best is None or len(failed) < len(best[1]):
            best = (rows, failed)
        if not failed:
            break
        newhard = [(n, a, b) for n, a, b, w in failed]
        hard = newhard + [c for c in hard if key(c) not in {key(x) for x in newhard}]
    rows, failed = best
    with open(G.HERE + f'evidence/ROUTE_PLAN{tag}.csv', 'w', newline='') as f:
        wr = csv.DictWriter(f, fieldnames=['kind', 'group', 'net', 'layer', 'x1', 'y1', 'x2', 'y2', 'w', 'd', 'h', 'conn', 'relax'])
        wr.writeheader(); wr.writerows(rows)
    with open(G.HERE + f'evidence/ROUTE_FAILED{tag}.txt', 'w') as f:
        for n, a, b, why in failed:
            f.write(f"{n} | {why} | {a['text']} | {b['text']}" + '\n')
    print(f'BEST: routed {len(conns) - len(failed)}/{len(conns)} failed {len(failed)} tracks {sum(r["kind"] == "TRACK" for r in rows)} vias {sum(r["kind"] == "VIA" for r in rows)}')


if __name__ == '__main__':
    main()
