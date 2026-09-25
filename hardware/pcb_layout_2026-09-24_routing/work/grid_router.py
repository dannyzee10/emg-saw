"""Rule-aware windowed grid router for the remaining connections (offline planner; Altium DRC is the authority).

Inputs : GEOM_FILE (native export) + an Altium DRC JSON (Un-Routed Net Constraint rows = Altium's ratsnest).
Output : evidence/ROUTE_PLAN.csv (TRACK/VIA rows, plan format used by build_ops.py), evidence/ROUTE_FAILED.txt
Layers : L1 (Top) and L3 (Mid Layer 2); L4 (Bottom) only for nets that own bottom-side pads; L2 never.
Rules  : per-net class clearance (0.25 power/analog/ADC/reference, else 0.20) to other-net copper,
         0.15 track-to-pad for fine-pitch parts inside their escape regions (CLR_FINE_ESCAPE_*), keepouts,
         0.5 mm board edge, vias 0.6/0.3 with 0.1 mm mask web to any pad and 0.254 hole-to-hole.
Grid 0.05 mm with a quantisation margin; every result is re-checked exactly by build_ops.py.
usage: GEOM_FILE=... python grid_router.py DRC.json [net1,net2,...]
"""
import csv, heapq, json, math, re, sys, time
import numpy as np
from scipy import ndimage
from PIL import Image, ImageDraw
from shapely.geometry import LineString, Point, box
from shapely.strtree import STRtree
import geom as G

RES = 0.05
MARGIN = 0.06
LAYERS = ['Top Layer', 'Mid Layer 2', 'Bottom Layer']
VIA_D, VIA_H = 0.6, 0.3
VIA_COST = 1.2
L4_COST = 1.6
FINE = {'U_MCU1', 'UP1', 'UP2', 'UP4', 'U_DRL1', 'C_DRL_DEC'}
WIDTH = {'EMG_POWER': 0.25, 'EMG_GND': 0.25, 'EMG_SWITCH': 0.3, 'EMG_SPI': 0.18, 'EMG_CRYSTAL': 0.2}
DIRS = [(1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0), (1, 1, 1.4142), (1, -1, 1.4142), (-1, 1, 1.4142), (-1, -1, 1.4142)]

objs, comps, keepouts = G.load()
bottom_nets = {o.net for o in objs if o.kind == 'PAD' and o.layers == {'Bottom Layer'}}
classes = {}
for l in open(G.CLASSES, encoding='utf-8', errors='replace'):
    f = l.rstrip('\n').split('|')
    if f[0] == 'MEMBER' and f[1].startswith('EMG_'):
        classes.setdefault(f[2], set()).add(f[1])


def width_for(net):
    for c, w in WIDTH.items():
        if c in classes.get(net, ()):
            return w
    return 0.2


# ---------------------------------------------------------------- copper store
class Store:
    """all copper as (geom, net, layerset, wide, finepad) with a spatial index; new copper appended."""
    def __init__(self):
        self.items = []
        for o in objs:
            if o.kind in ('PAD', 'TRACK', 'VIA', 'ARC', 'REGION', 'FILL'):
                self.items.append((o.geom, o.net, set(o.layers), o.net in G.WIDE, o.kind == 'PAD' and o.comp in FINE, o.kind == 'PAD'))
        self.keep = [o.geom for o in objs if o.kind == 'KEEPOUT']
        self.holes = [o.geom for o in objs if o.kind == 'HOLE']
        self.fine_regions = []
        for ref in FINE:
            ps = [o.geom for o in objs if o.kind == 'PAD' and o.comp == ref]
            if ps:
                self.fine_regions.append(box(min(p.bounds[0] for p in ps) - 1.0, min(p.bounds[1] for p in ps) - 1.0,
                                             max(p.bounds[2] for p in ps) + 1.0, max(p.bounds[3] for p in ps) + 1.0))
        self._rebuild()

    def _rebuild(self):
        self.tree = STRtree([it[0] for it in self.items])
        self.htree = STRtree(self.holes)

    def add(self, g, net, layers):
        self.items.append((g, net, set(layers), net in G.WIDE, False, False))

    def add_hole(self, g):
        self.holes.append(g)

    def query(self, region):
        return [self.items[i] for i in self.tree.query(region)] + self.items[len(self.tree.geometries):]


# ---------------------------------------------------------------- window rasterisation
class Win:
    def __init__(self, x0, y0, x1, y1):
        self.x0, self.y0 = x0, y0
        self.nx, self.ny = int(math.ceil((x1 - x0) / RES)), int(math.ceil((y1 - y0) / RES))
        self.y1 = y0 + self.ny * RES

    def px(self, x, y):
        return ((x - self.x0) / RES, (self.y1 - y) / RES)

    def xy(self, ix, iy):
        return self.x0 + (ix + 0.5) * RES, self.y1 - (iy + 0.5) * RES

    def ras(self, geoms):
        img = Image.new('1', (self.nx, self.ny), 0)
        d = ImageDraw.Draw(img)
        for g in geoms:
            for p in ([g] if g.geom_type == 'Polygon' else list(getattr(g, 'geoms', []))):
                if not p.is_empty:
                    d.polygon([self.px(x, y) for x, y in p.exterior.coords], fill=1)
        return np.array(img, dtype=bool)

    def edt(self, geoms):
        if not geoms:
            return np.full((self.ny, self.nx), 99.0)
        return ndimage.distance_transform_edt(~self.ras(geoms)) * RES


def maps(store, win, net, w, region):
    c = G.base_clr(net); hw = w / 2
    near = [it for it in store.query(region.buffer(1.2))]
    keep = [k for k in store.keep if k.intersects(region.buffer(1.2))]
    holes = [store.holes[i] for i in store.htree.query(region.buffer(1.2))] + store.holes[len(store.htree.geometries):]
    inside = win.ras([G.BOARD])
    d_edge = ndimage.distance_transform_edt(inside) * RES
    d_keep = win.edt(keep)
    d_pad = win.edt([g for g, n, ls, wd, fp, ispad in near if ispad])
    fine = win.ras([r for r in store.fine_regions if r.intersects(region)])
    free, via_ok = {}, np.ones((win.ny, win.nx), bool)
    for L in LAYERS:
        items = [(g, wd, fp) for g, n, ls, wd, fp, ispad in near if n != net and L in ls]
        dn = win.edt([g for g, wd, fp in items if not wd and not fp])
        dw = win.edt([g for g, wd, fp in items if wd and not fp])
        df = win.edt([g for g, wd, fp in items if fp])
        freq = np.where(fine, 0.15, 0.25)
        ok = (dn >= c + hw + MARGIN) & (dw >= 0.25 + hw + MARGIN) & (df >= freq + hw + MARGIN)
        ok &= (d_keep >= c + hw + MARGIN) & (d_edge >= G.EDGE + hw + MARGIN)
        free[L] = ok
        r = VIA_D / 2
        via_ok &= (dn >= c + r + MARGIN) & (dw >= 0.25 + r + MARGIN) & (df >= 0.25 + r + MARGIN)
    via_ok &= (d_keep >= c + VIA_D / 2 + MARGIN) & (d_edge >= G.EDGE + VIA_D / 2 + MARGIN)
    via_ok &= d_pad >= VIA_D / 2 + 0.1 + MARGIN
    via_ok &= win.edt(holes) >= VIA_H / 2 + 0.254 + 0.15 + MARGIN
    return free, via_ok


# ---------------------------------------------------------------- connections
def parse_conn(s):
    m = re.match(r'Un-Routed Net Constraint: Net (\S+) Between (.*) And (.*)$', s.strip())
    if not m:
        return None
    ends = []
    for part in (m.group(2), m.group(3)):
        pts = [(float(a), float(b)) for a, b in re.findall(r'\(([-\d.]+)mm,\s*([-\d.]+)mm\)', part)]
        ends.append({'kind': part.split()[0], 'pts': pts, 'text': part.strip()})
    return m.group(1), ends[0], ends[1]


def end_copper(store, end, net):
    x, y = end['pts'][0]
    probe = LineString(end['pts']) if end['kind'] == 'Track' and len(end['pts']) == 2 else Point(x, y)
    best = None
    for g, n, ls, wd, fp, ispad in store.query(probe.buffer(0.3)):
        if n != net:
            continue
        d = g.distance(probe)
        if best is None or d < best[0]:
            best = (d, g, ls)
    if best is None or best[0] > 0.2:
        return None, set()
    return best[1], set(best[2]) & set(LAYERS)


def astar(win, free, via_ok, starts, goals, allowed, max_expand=400000):
    gset = set(goals)
    gx = sum(g[1] for g in goals) / len(goals); gy = sum(g[2] for g in goals) / len(goals)
    h = lambda ix, iy: math.hypot(ix - gx, iy - gy) * RES * 0.9
    openq, best, parent = [], {}, {}
    for s in starts:
        best[s] = 0.0; heapq.heappush(openq, (h(s[1], s[2]), 0.0, s, None))
    lays = [i for i, L in enumerate(LAYERS) if L in allowed]
    n = 0
    while openq:
        f, g, node, par = heapq.heappop(openq)
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
        fr = free[LAYERS[L]]
        mult = L4_COST if LAYERS[L] == 'Bottom Layer' else 1.0
        for dx, dy, c in DIRS:
            jx, jy = ix + dx, iy + dy
            if 0 <= jx < win.nx and 0 <= jy < win.ny and fr[jy, jx]:
                if dx and dy and not (fr[iy, jx] and fr[jy, ix]):
                    continue
                nd = (L, jx, jy); ng = g + c * RES * mult
                if ng < best.get(nd, 1e18):
                    best[nd] = ng; heapq.heappush(openq, (ng + h(jx, jy), ng, nd, node))
        if via_ok[iy, ix]:
            for L2 in lays:
                if L2 != L and free[LAYERS[L2]][iy, ix]:
                    nd = (L2, ix, iy); ng = g + VIA_COST
                    if ng < best.get(nd, 1e18):
                        best[nd] = ng; heapq.heappush(openq, (ng + h(ix, iy), ng, nd, node))
    return None


def end_nodes(win, geom, layers, free, allowed):
    m = win.ras([geom.buffer(-0.02) if geom.area > 0.01 else geom.buffer(RES)])
    out = []
    for L in layers:
        if L in allowed:
            ys, xs = np.nonzero(m & free[L])
            out += [(LAYERS.index(L), int(x), int(y)) for x, y in zip(xs, ys)]
    return out


def to_segments(win, path):
    segs, vias, run = [], [], [path[0]]
    for a, b in zip(path, path[1:]):
        if a[0] != b[0]:
            if len(run) > 1:
                segs.append(run)
            vias.append(win.xy(a[1], a[2])); run = [b]; continue
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
        out.append((LAYERS[pts[0][0]], [win.xy(p[1], p[2]) for p in simp]))
    return out, vias


def route_one(store, net, a, b, w, pad_mm):
    ga, la = end_copper(store, a, net); gb, lb = end_copper(store, b, net)
    if ga is None or gb is None:
        return None, 'endpoint not matched'
    allowed = {'Top Layer', 'Mid Layer 2'} | ({'Bottom Layer'} if net in bottom_nets else set())
    bb = ga.union(gb).bounds
    region = box(max(10.0, bb[0] - pad_mm), max(10.0, bb[1] - pad_mm), min(90.0, bb[2] + pad_mm), min(55.0, bb[3] + pad_mm))
    win = Win(*region.bounds)
    free, via_ok = maps(store, win, net, w, region)
    starts = end_nodes(win, ga, la, free, allowed); goals = end_nodes(win, gb, lb, free, allowed)
    if not starts or not goals:
        return None, f'no free entry (starts {len(starts)}, goals {len(goals)})'
    path = astar(win, free, via_ok, starts, goals, allowed)
    if path is None:
        return None, 'no path'
    return to_segments(win, path), 'ok'


def main():
    data = json.load(open(sys.argv[1]))
    only = set(sys.argv[2].split(',')) if len(sys.argv) > 2 and sys.argv[2] else None
    conns = [c for c in (parse_conn(d) for d in data['details'] if d.startswith('Un-Routed')) if c]
    if only:
        conns = [c for c in conns if c[0] in only]
    def prio(c):
        net, a, b = c
        cl = classes.get(net, set())
        rank = 0 if cl & {'EMG_ANALOG', 'EMG_REFERENCE', 'EMG_ADC', 'EMG_CRYSTAL'} else 1 if cl & {'EMG_SPI', 'EMG_SWITCH'} else 3 if net == 'GND' else 2
        return (rank, math.dist(a['pts'][0], b['pts'][0]))
    conns.sort(key=prio)
    store = Store()
    rows, failed = [], []
    t0 = time.time()
    for k, (net, a, b) in enumerate(conns):
        res, why = None, ''
        for w in sorted({width_for(net), 0.15}, reverse=True):
            for pad in (3.0, 8.0, 25.0):
                res, why = route_one(store, net, a, b, w, pad)
                if res:
                    break
            if res:
                break
        if not res:
            failed.append((net, why, a['text'], b['text'])); continue
        (segs, vias) = res
        for L, pts in segs:
            for p, q in zip(pts, pts[1:]):
                rows.append({'kind': 'TRACK', 'group': f'R{k}:{net}', 'net': net, 'layer': L, 'x1': round(p[0], 4), 'y1': round(p[1], 4), 'x2': round(q[0], 4), 'y2': round(q[1], 4), 'w': w, 'd': '', 'h': ''})
                store.add(LineString([p, q]).buffer(w / 2, 8), net, [L])
        for x, y in vias:
            rows.append({'kind': 'VIA', 'group': f'R{k}:{net}', 'net': net, 'layer': 'Multi Layer', 'x1': round(x, 4), 'y1': round(y, 4), 'x2': '', 'y2': '', 'w': '', 'd': VIA_D, 'h': VIA_H})
            store.add(Point(x, y).buffer(VIA_D / 2, 16), net, LAYERS)
            store.add_hole(Point(x, y).buffer(VIA_H / 2, 12))
        if k % 20 == 0:
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
