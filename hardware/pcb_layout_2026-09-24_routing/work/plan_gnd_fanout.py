"""Plan GND fanout: one short top-layer stub + 0.6/0.3 via per unconnected top-side GND pad.

Reads evidence/GEOMETRY.txt (native read-only export), writes evidence/GND_FANOUT_PLAN.csv.
All clearances are checked against other-net copper using true pad rectangles (bbox),
existing tracks/vias, bottom/multilayer pads (vias go through all layers), keepouts,
board edge and previously planned vias. Nothing is written to Altium here.
"""
import csv, math, sys
from shapely.geometry import LineString, Point, Polygon, box
from shapely.strtree import STRtree

GEOM = 'evidence/GEOMETRY.txt'
OUT = 'evidence/GND_FANOUT_PLAN.csv'
VIA_D, VIA_H = 0.6, 0.3
CLR = 0.25          # conservative: max of general 0.20 and analog/power 0.25
HOLE_HOLE = 0.254   # HoleToHoleClearance rule
EDGE = 0.5          # brief: copper-to-routed-edge 0.50 mm
BOARD = Polygon([(12, 10), (88, 10), (90, 12), (90, 53), (88, 55), (12, 55), (10, 53), (10, 12)])
COPPER = {'Top Layer', 'Bottom Layer', 'Mid Layer 1', 'Mid Layer 2', 'Multi Layer'}

rows = [l.rstrip('\n').split('|') for l in open(GEOM, encoding='utf-8', errors='replace')]
pads = [r for r in rows if r[0] == 'PAD']
vias = [r for r in rows if r[0] == 'VIA']
tracks = [r for r in rows if r[0] == 'TRACK']
regions = [r for r in rows if r[0] == 'REGION']
comps = {r[1]: r for r in rows if r[0] == 'COMP'}

CLS = 'evidence/inputs/CLASSES.txt'
WIDE = set()  # nets whose class rule asks 0.25 mm (CLR_POWER_025 / CLR_ANALOG_025)
for l in open(CLS, encoding='utf-8', errors='replace'):
    f = l.rstrip('\n').split('|')
    if f[0] == 'MEMBER' and f[1] in ('EMG_POWER', 'EMG_ANALOG', 'EMG_ADC', 'EMG_REFERENCE'):
        WIDE.add(f[2])

def clr_for(net):
    return 0.25 if net in WIDE else 0.2

# Fine-pitch parts get a scoped escape rule (created natively): track/via to THEIR pads = 0.12 mm.
FINE = {'J_FPC1', 'J_FPC2', 'J_FPC3', 'J_FPC4', 'J_FPC5', 'U_MCU1', 'UP1', 'UP2', 'UP4', 'U_WIFI1',
        'U1', 'U2', 'U3', 'INA1', 'INA2', 'INA3', 'INA4', 'INA5', 'U_UV1', 'U_EN1', 'UP3', 'Q_SHDN'}
CLR_ESC = 0.12

def clr_obs(net, src):
    if src[0] == 'PAD' and src[1] in FINE:
        return CLR_ESC
    return clr_for(net)

def padrect(p):
    return box(float(p[7]), float(p[8]), float(p[9]), float(p[10]))

# obstacles per layer: (geometry, net)
top, via_obs, gnd_holes = [], [], []
for p in pads:
    g = padrect(p)
    if p[4] in ('Top Layer', 'Multi Layer'):
        top.append((g, p[3], p))
    if p[4] in ('Bottom Layer', 'Multi Layer', 'Top Layer'):
        via_obs.append((g, p[3], p))
    if p[4] == 'Multi Layer' and float(p[11].split('=')[1]) > 0:
        gnd_holes.append((Point(float(p[5]), float(p[6])), float(p[11].split('=')[1]) / 2))
for t in tracks:
    if t[1] not in COPPER or t[-1] == 'KEEPOUT=True':
        continue
    seg = LineString([(float(t[3]), float(t[4])), (float(t[5]), float(t[6]))]).buffer(float(t[7]) / 2)
    if t[1] == 'Top Layer':
        top.append((seg, t[2], t))
    via_obs.append((seg, t[2], t)) if t[1] in ('Top Layer', 'Bottom Layer') else None
for v in vias:
    c = Point(float(v[2]), float(v[3]))
    top.append((c.buffer(float(v[4]) / 2), v[1], v))
    via_obs.append((c.buffer(float(v[4]) / 2), v[1], v))
    gnd_holes.append((c, float(v[5]) / 2))
keepouts = [box(float(r[3]), float(r[4]), float(r[5]), float(r[6])) for r in regions if r[-2] == 'KEEPOUT=True']

def index(obstacles):
    obs = [o for o in obstacles if o[1] != 'GND']
    return (STRtree([o[0] for o in obs]), obs)

def clear(geom, idx, own_pad):
    tree, obs = idx
    for i in tree.query(geom.buffer(CLR)):
        g, net, src = obs[i]
        if src is own_pad:
            continue
        if geom.distance(g) < clr_obs(net, src) - 1e-6:
            return False
    return True

def in_other_body(pt, own):
    for name, c in comps.items():
        if name == own:
            continue
        b = box(float(c[6]), float(c[7]), float(c[8]), float(c[9]))
        if b.contains(pt):
            return True
    return False

# which top GND pads are already via-connected (same test as the audit)
def connected(p):
    r = padrect(p).buffer(0.05)
    if any(r.contains(Point(float(v[2]), float(v[3]))) for v in vias):
        return True
    for t in tracks:
        if t[1] != 'Top Layer' or t[2] != 'GND':
            continue
        a, b = (float(t[3]), float(t[4])), (float(t[5]), float(t[6]))
        for e, o in ((a, b), (b, a)):
            if padrect(p).buffer(0.01).contains(Point(e)) and any(abs(float(v[2]) - o[0]) < .05 and abs(float(v[3]) - o[1]) < .05 for v in vias):
                return True
    return False

gnd_top_tracks = [t for t in tracks if t[1] == 'Top Layer' and t[2] == 'GND']
tracks_all = tracks
tracks = gnd_top_tracks  # connected() only needs top GND tracks
EP_TIE = {('UP1', '4'): '17', ('UP1', '5'): '17', ('UP1', '8'): '17', ('UP1', '15'): '17',
          ('UP4', '1'): '9', ('UP4', '4'): '9', ('UP4', '6'): '9'}
todo = [p for p in pads if p[3] == 'GND' and p[4] == 'Top Layer' and not connected(p) and (p[1], p[2]) not in EP_TIE]
top_idx, via_idx = index(top), index(via_obs)
planned, failed = [], []
tie_only = set()
for p in todo:
    cx, cy = float(p[5]), float(p[6])
    pr = padrect(p)
    narrow = min(pr.bounds[2] - pr.bounds[0], pr.bounds[3] - pr.bounds[1])
    w = 0.15 if narrow < 0.45 else min(0.3, narrow * 0.9)
    owner = p[1]
    best = None
    for ang in range(0, 360, 15):
        dx, dy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        # start just outside the pad
        for k in range(0, 60):
            d = 0.05 * k
            vx, vy = cx + dx * d, cy + dy * d
            vp = Point(vx, vy)
            vc = vp.buffer(VIA_D / 2)
            if pr.buffer(0.0).intersects(vp.buffer(VIA_H / 2 + 0.05)):
                continue  # no via-in-pad for ordinary pads
            if not BOARD.buffer(-EDGE).contains(vc):
                continue
            if any(ko.intersects(vc) for ko in keepouts):
                continue
            if any(vp.distance(h) < r + VIA_H / 2 + HOLE_HOLE for h, r in gnd_holes):
                continue
            ray = LineString([(cx, cy), (vx, vy)])
            outside = ray.difference(pr)
            if outside.is_empty:
                continue
            ex = pr.exterior.intersection(ray)
            ex = ex if ex.geom_type == 'Point' else list(getattr(ex, 'geoms', [ex]))[0]
            exit_pt = (ex.x, ex.y) if ex.geom_type == 'Point' else (cx, cy)
            stub = LineString([exit_pt, (vx, vy)]).buffer(w / 2, cap_style=2)
            if not clear(vc, via_idx, p) or not clear(stub, top_idx, p):
                continue
            score = d + (1.0 if in_other_body(vp, owner) else 0)
            if best is None or score < best[0]:
                best = (score, vx, vy, w, d, exit_pt[0], exit_pt[1])
            break
    if best is None:
        # fallback: short straight tie to an existing/planned GND via (no new via)
        for (h, r) in sorted(gnd_holes, key=lambda hr: hr[0].distance(Point(cx, cy))):
            if h.distance(Point(cx, cy)) > 2.5:
                break
            ray = LineString([(cx, cy), (h.x, h.y)])
            ex = pr.exterior.intersection(ray)
            if ex.is_empty or ex.geom_type != 'Point':
                continue
            stub = LineString([(ex.x, ex.y), (h.x, h.y)]).buffer(w / 2, cap_style=2)
            if clear(stub, top_idx, p):
                best = (0, h.x, h.y, w, h.distance(Point(cx, cy)), ex.x, ex.y)
                tie_only.add(p[1] + '-' + p[2])
                break
    if best is None:
        failed.append(p[1] + '-' + p[2])
        continue
    _, vx, vy, w, d, _, _ = best
    planned.append({'tie_only': int(p[1] + '-' + p[2] in tie_only), 'pad': p[1] + '-' + p[2], 'px': round(best[5], 4), 'py': round(best[6], 4), 'vx': round(vx, 4), 'vy': round(vy, 4), 'w': round(w, 3), 'len': round(d, 3)})
    if p[1] + '-' + p[2] not in tie_only:
        gnd_holes.append((Point(vx, vy), VIA_H / 2))

with open(OUT, 'w', newline='') as f:
    wr = csv.DictWriter(f, fieldnames=['tie_only', 'pad', 'px', 'py', 'vx', 'vy', 'w', 'len'])
    wr.writeheader()
    wr.writerows(planned)
print('planned', len(planned), 'failed', len(failed))
print('FAILED:', failed)
print('max stub', max((r['len'] for r in planned), default=0))
