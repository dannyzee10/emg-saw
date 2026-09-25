"""Deterministic, rule-aware grid router v3 (offline planner; Altium DRC is the authority).

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
import csv, heapq, json, math, re, sys, time
import numpy as np
from scipy import ndimage
from PIL import Image, ImageDraw
from shapely.geometry import LineString, Point, box
import geom as G

RES = 0.05
X0, Y1 = 9.5, 55.5
NX, NY = int(round((90.5 - X0) / RES)), int(round((Y1 - 9.5) / RES))
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


def allowed_layers(net):
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
D_KEEP = ndimage.distance_transform_edt(~keep) * RES
D_ANYPAD = ndimage.distance_transform_edt(~anypad) * RES


def edt(mask):
    if not mask.any():
        return np.full(mask.shape, 99.0)
    return ndimage.distance_transform_edt(~mask) * RES


def maps(net, w, W):
    iy0, iy1, ix0, ix1 = W
    nid = NID[net]
    c = G.base_clr(net); hw = w / 2
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
        ok = (dn >= c + hw + MARGIN) & (dw >= 0.25 + hw + MARGIN) & (df >= np.where(fr, 0.15, 0.25) + hw + MARGIN)
        ok &= (D_KEEP[iy0:iy1, ix0:ix1] >= c + hw + MARGIN) & (D_EDGE[iy0:iy1, ix0:ix1] >= 0.5 + hw + MARGIN)
        free[L] = ok
        r = VIA_D / 2
        via_ok &= (dn >= c + r + MARGIN) & (dw >= 0.25 + r + MARGIN) & (df >= 0.25 + r + MARGIN)
    via_ok &= (D_KEEP[iy0:iy1, ix0:ix1] >= c + VIA_D / 2 + MARGIN) & (D_EDGE[iy0:iy1, ix0:ix1] >= 0.5 + VIA_D / 2 + MARGIN)
    via_ok &= D_ANYPAD[iy0:iy1, ix0:ix1] >= VIA_D / 2 + 0.05 + MARGIN
    via_ok &= edt(holes[iy0:iy1, ix0:ix1]) >= VIA_H / 2 + 0.254 + MARGIN
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


def astar(free, via_ok, starts, goals, lcost, allowed, max_expand=1500000):
    gset = set(goals)
    gx = sum(g[1] for g in goals) / len(goals); gy = sum(g[2] for g in goals) / len(goals)
    ny, nx = via_ok.shape
    lc = [lcost[L] for L in LAYERS]
    minc = min(lc[i] for i, L in enumerate(LAYERS) if L in allowed)
    h = lambda ix, iy: math.hypot(ix - gx, iy - gy) * RES * minc * 0.95
    frees = [free[L] for L in LAYERS]
    lays = [i for i, L in enumerate(LAYERS) if L in allowed]
    openq, best, parent, arr = [], {}, {}, {}
    for s in starts:
        best[s] = 0.0; arr[s] = -1; heapq.heappush(openq, (h(s[1], s[2]), 0.0, s, None, -1))
    n = 0
    while openq:
        f, g, node, par, d_in = heapq.heappop(openq)
        if node in parent:
            continue
        parent[node] = par
        if node in gset:
            path = []
            while node is not None:
                path.append(node); node = parent[node]
            return path[::-1]
        n += 1
        if n > max_expand:
            return None
        L, ix, iy = node
        fr = frees[L]; mult = lc[L]
        for k, (dx, dy, c) in enumerate(DIRS):
            jx, jy = ix + dx, iy + dy
            if 0 <= jx < nx and 0 <= jy < ny and fr[jy, jx]:
                if dx and dy and not (fr[iy, jx] and fr[jy, ix]):
                    continue
                nd = (L, jx, jy)
                ng = g + c * RES * mult + (TURN if (d_in >= 0 and k != d_in) else 0.0)
                if ng < best.get(nd, 1e18):
                    best[nd] = ng; heapq.heappush(openq, (ng + h(jx, jy), ng, nd, node, k))
        if via_ok[iy, ix]:
            for L2 in lays:
                if L2 != L and frees[L2][iy, ix]:
                    nd = (L2, ix, iy); ng = g + VIA_COST
                    if ng < best.get(nd, 1e18):
                        best[nd] = ng; heapq.heappush(openq, (ng + h(ix, iy), ng, nd, node, -1))
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


def route_one(net, a, b):
    ga, la = end_copper(a, net); gb, lb = end_copper(b, net)
    if ga is None or gb is None:
        return None, 'endpoint not matched'
    allowed = allowed_layers(net); lcost = layer_cost(net)
    last = 'no path'
    for w in widths(net):
        for pad in (2.0, 6.0, 15.0, 90.0):
            W = window(ga, gb, pad)
            free, via_ok = maps(net, w, W)
            s = end_nodes(ga, la, free, W, allowed); t = end_nodes(gb, lb, free, W, allowed)
            if not s:
                s = end_nodes(ga, la, free, W, allowed, relax=True)
            if not t:
                t = end_nodes(gb, lb, free, W, allowed, relax=True)
            if not s or not t:
                last = f'no entry nodes (s {len(s)}, t {len(t)})'; continue
            for st in s:  # relaxed entry cells must be walkable
                free[LAYERS[st[0]]][st[2], st[1]] = True
            for st in t:
                free[LAYERS[st[0]]][st[2], st[1]] = True
            path = astar(free, via_ok, s, t, lcost, allowed)
            if path:
                segs, vias = to_segments(path, W)
                return (segs, vias, w), 'ok'
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


def main():
    data = json.load(open(sys.argv[1]))
    only = set(sys.argv[2].split(',')) if len(sys.argv) > 2 and sys.argv[2] else None
    conns = [c for c in (parse_conn(d) for d in data['details'] if d.startswith('Un-Routed')) if c]
    if only:
        conns = [c for c in conns if c[0] in only]
    conns.sort(key=prio)
    rows, failed = [], []
    t0 = time.time()
    for k, (net, a, b) in enumerate(conns):
        res, why = route_one(net, a, b)
        if not res:
            failed.append((net, why, a['text'], b['text'])); continue
        segs, vias, w = res
        for L, pts in segs:
            for p, q in zip(pts, pts[1:]):
                for pp, qq in split_at_regions(p, q):
                    rows.append({'kind': 'TRACK', 'group': f'R{k}:{net}', 'net': net, 'layer': L, 'x1': round(pp[0], 4), 'y1': round(pp[1], 4), 'x2': round(qq[0], 4), 'y2': round(qq[1], 4), 'w': w, 'd': '', 'h': ''})
                g = LineString([p, q]).buffer(w / 2, 8)
                stamp(g, net, [L]); copper_objs.append((g, net, {L}))
        for x, y in vias:
            rows.append({'kind': 'VIA', 'group': f'R{k}:{net}', 'net': net, 'layer': 'Multi Layer', 'x1': round(x, 4), 'y1': round(y, 4), 'x2': '', 'y2': '', 'w': '', 'd': VIA_D, 'h': VIA_H})
            g = Point(x, y).buffer(VIA_D / 2, 16)
            stamp(g, net, LAYERS); copper_objs.append((g, net, set(LAYERS)))
            win, m = patch(Point(x, y).buffer(VIA_H / 2, 12))
            holes[win[0]:win[1], win[2]:win[3]] |= m
        if k % 25 == 0:
            print(f'{k + 1}/{len(conns)} failed {len(failed)} t={time.time() - t0:.0f}s', flush=True)
    with open(G.HERE + 'evidence/ROUTE_PLAN.csv', 'w', newline='') as f:
        wr = csv.DictWriter(f, fieldnames=['kind', 'group', 'net', 'layer', 'x1', 'y1', 'x2', 'y2', 'w', 'd', 'h'])
        wr.writeheader(); wr.writerows(rows)
    with open(G.HERE + 'evidence/ROUTE_FAILED.txt', 'w') as f:
        for x in failed:
            f.write(' | '.join(map(str, x)) + '\n')
    print(f'connections {len(conns)} routed {len(conns) - len(failed)} failed {len(failed)} tracks {sum(r["kind"] == "TRACK" for r in rows)} vias {sum(r["kind"] == "VIA" for r in rows)} time {time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
