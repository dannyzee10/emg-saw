"""Gloss / straighten router copper (the "professional look" pass).

For every net and copper layer, the tracks that belong to routed plan groups (never BK13 escapes, stitches or placement
copper) are split into CHAINS between anchors: pads, vias, branch points, chain ends, and any point where other copper of
the net (fixed copper, other layers' pads, pours are not modelled) touches.  Each chain is replaced by the simplest
octilinear path between its two anchors that passes the exact checks (clearance by rule class incl. BK13 escape zones,
board edge, keep-outs, L5 reservation):  1 segment (straight / 45 deg), 2 segments (straight + 45 deg, both orders),
3 segments (straight - 45 - straight, several splits).  Longer chains are string-pulled: from each anchor the farthest
point of the chain that can be reached by such a simple path is taken.  A replacement is kept only when it has fewer
segments than the original (or is >= 5 % shorter with the same count).  Width = the chain's own width.

usage: GEOM_FILE=... BOARD_BOX=... [BK13_ZONES=...] [L5_RESERVED=...] [WINDOW=x0,y0,x1,y1]
       python gloss.py OUT_ADDS.csv OUT_DELS.csv PLAN.csv [PLAN.csv ...]
Writes build_ops-format ADDS (new tracks, groups 'G<k>:<net>') and DELS (the replaced native tracks)."""
import csv, math, os, sys
from collections import defaultdict
from shapely.geometry import LineString, Point, box
import geom as G

out_adds, out_dels, plans = sys.argv[1], sys.argv[2], sys.argv[3:]
objs, comps, keepouts = G.load()
if os.environ.get('BK13_ZONES'):
    for z in csv.DictReader(open(os.environ['BK13_ZONES'])):
        G.ZONES.append((box(float(z['x0']), float(z['y0']), float(z['x1']), float(z['y1'])), set(z['nets'].split(';')), z['ref']))
L5_RES = []
for t in os.environ.get('L5_RESERVED', '').split(';'):
    if t.strip():
        n_, c_ = t.split(':'); v_ = [float(q) for q in c_.split(',')]
        L5_RES.append((n_, box(*v_)))
WINDOW = box(*[float(v) for v in os.environ['WINDOW'].split(',')]) if os.environ.get('WINDOW') else None
R3 = lambda v: round(float(v), 3)


def k_src(o):
    s = o.src
    return ('T', s[2], s[1], frozenset(((R3(s[3]), R3(s[4])), (R3(s[5]), R3(s[6])))))


def k_row(r):
    return ('T', r['net'], r['layer'], frozenset(((R3(r['x1']), R3(r['y1'])), (R3(r['x2']), R3(r['y2'])))))


# ---- which native tracks are router copper (may be moved)
routed = set()
for p in plans:
    tag = p.replace('\\', '/').rsplit('/', 1)[-1]
    if tag.startswith(('BK13_ESCAPE', 'STITCH')):
        continue
    for r in csv.DictReader(open(p)):
        if r['kind'] == 'TRACK' and not r['group'].split(':')[0].startswith('S'):
            routed.add(k_row(r))
tracks = [o for o in objs if o.kind == 'TRACK' and o.src is not None and k_src(o) in routed]
movable = {id(o) for o in tracks}
print(f'router tracks: {len(tracks)} of {sum(1 for o in objs if o.kind == "TRACK")}')

EX = G.Index(objs)
removed = set()


def legal(net, layer, w, pts, ignore_ids):
    for a, b in zip(pts, pts[1:]):
        o = G.track(net, layer, [a, b], w)
        if not G.edge_ok(o.geom) or any(k.intersects(o.geom) for k in keepouts):
            return False
        if layer == 'Mid Layer 4' and any(rn != net and rg.intersects(o.geom) for rn, rg in L5_RES):
            return False
        for other, d, req in EX.violations(o):
            if id(other) not in ignore_ids and id(other) not in removed:
                return False
    return True


def octi_paths(a, b):
    """simple octilinear candidates from a to b (lists of points), fewest segments first"""
    (x0, y0), (x1, y1) = a, b
    dx, dy = x1 - x0, y1 - y0
    adx, ady = abs(dx), abs(dy)
    sx, sy = (1 if dx >= 0 else -1), (1 if dy >= 0 else -1)
    out = []
    if adx < 1e-6 or ady < 1e-6 or abs(adx - ady) < 1e-6:
        return [[a, b]]
    d = min(adx, ady)
    if adx > ady:                                   # straight part along x, 45 deg part length d
        out.append([a, (x0 + sx * (adx - d), y0), b])            # straight then 45
        out.append([a, (x0 + sx * d, y1), b])                    # 45 then straight
        for f in (0.5, 0.25, 0.75):
            s1 = (adx - d) * f
            p1 = (x0 + sx * s1, y0); p2 = (p1[0] + sx * d, y1)
            out.append([a, p1, p2, b])
    else:
        out.append([a, (x0, y0 + sy * (ady - d)), b])
        out.append([a, (x1, y0 + sy * d), b])
        for f in (0.5, 0.25, 0.75):
            s1 = (ady - d) * f
            p1 = (x0, y0 + sy * s1); p2 = (x1, p1[1] + sy * d)
            out.append([a, p1, p2, b])
    return out


def plen(pts):
    return sum(math.dist(p, q) for p, q in zip(pts, pts[1:]))


# ---- chains per (net, layer)
pt = lambda p: (round(p[0], 4), round(p[1], 4))
by_nl = defaultdict(list)
for o in tracks:
    s = o.src
    by_nl[(s[2], s[1])].append(o)
anchors_other = defaultdict(list)                   # net -> geometries of copper that is NOT a movable track
for o in objs:
    if o.kind in ('PAD', 'VIA', 'TRACK', 'ARC', 'FILL', 'REGION') and id(o) not in movable:
        anchors_other[o.net].append(o)

adds, dels, k, gain_seg = [], [], 0, 0
for (net, layer), tl in sorted(by_nl.items()):
    adj = defaultdict(list)
    ends = {}
    for o in tl:
        s = o.src
        a, b = pt((float(s[3]), float(s[4]))), pt((float(s[5]), float(s[6])))
        if a == b:
            continue
        ends[id(o)] = (a, b)
        adj[a].append(o); adj[b].append(o)

    def is_anchor(p):
        if len(adj[p]) != 2:
            return True
        P = Point(p).buffer(0.01)
        for q in anchors_other[net]:
            if (layer in q.layers or q.kind == 'VIA') and q.geom.intersects(P):
                return True
        return False
    anchor = {p: is_anchor(p) for p in adj}
    used = set()
    for start in [p for p in adj if anchor[p]]:
        for o0 in adj[start]:
            if id(o0) in used:
                continue
            chain, pts, cur, o = [], [start], start, o0
            while True:
                used.add(id(o)); chain.append(o)
                a, b = ends[id(o)]
                nxt = b if a == cur else a
                pts.append(nxt)
                if anchor.get(nxt, True):
                    break
                cand = [q for q in adj[nxt] if id(q) not in used]
                if not cand:
                    break
                cur, o = nxt, cand[0]
            if len(chain) < 2 and len(pts) == 2:
                (x0, y0), (x1, y1) = pts
                dxa, dya = abs(x1 - x0), abs(y1 - y0)
                if dxa < 1e-6 or dya < 1e-6 or abs(dxa - dya) < 1e-6:
                    continue                            # a single octilinear segment is already clean
            if WINDOW is not None and not WINDOW.intersects(LineString(pts)):
                continue
            widths = {round(float(c.src[7]), 4) for c in chain}
            if len(widths) != 1:
                continue
            w = widths.pop()
            ign = {id(c) for c in chain}
            # string pulling over the chain's own vertices with octilinear candidates
            new, i = [pts[0]], 0
            ok_all = True
            while i < len(pts) - 1:
                best = None
                for j in range(len(pts) - 1, i, -1):
                    for cp in octi_paths(pts[i], pts[j]):
                        if legal(net, layer, w, cp, ign):
                            best = (j, cp); break
                    if best:
                        break
                if best is None:
                    ok_all = False; break
                j, cp = best
                new += cp[1:]; i = j
            if not ok_all:
                continue
            # drop collinear interior points
            simp = [new[0]]
            for q in range(1, len(new) - 1):
                a_, b_, c_ = simp[-1], new[q], new[q + 1]
                if abs((b_[0] - a_[0]) * (c_[1] - b_[1]) - (b_[1] - a_[1]) * (c_[0] - b_[0])) > 1e-9:
                    simp.append(b_)
            simp.append(new[-1])
            n_old, n_new = len(chain), len(simp) - 1
            if not (n_new < n_old or (n_new == n_old and plen(simp) < 0.95 * plen(pts))):
                continue
            k += 1; gain_seg += n_old - n_new
            for c in chain:
                s = c.src
                dels.append({'kind': 'TRACK', 'group': 'GLOSS_DEL', 'net': net, 'layer': layer, 'x1': s[3], 'y1': s[4],
                             'x2': s[5], 'y2': s[6], 'w': s[7]})
                removed.add(id(c))
            for a_, b_ in zip(simp, simp[1:]):
                adds.append({'kind': 'TRACK', 'group': f'G{k}:{net}', 'net': net, 'layer': layer, 'x1': round(a_[0], 4),
                             'y1': round(a_[1], 4), 'x2': round(b_[0], 4), 'y2': round(b_[1], 4), 'w': w, 'd': '', 'h': '',
                             'conn': 'gloss', 'relax': 0})
                EX.add(G.track(net, layer, [a_, b_], w))
fields = ['kind', 'group', 'net', 'layer', 'x1', 'y1', 'x2', 'y2', 'w', 'd', 'h', 'conn', 'relax']
for path_, rows_ in ((out_adds, adds), (out_dels, dels)):
    with open(path_, 'w', newline='') as f:
        wr = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore', restval=''); wr.writeheader(); wr.writerows(rows_)
print(f'glossed chains {k}: segments removed {gain_seg}; adds {len(adds)} rows, dels {len(dels)} rows')
