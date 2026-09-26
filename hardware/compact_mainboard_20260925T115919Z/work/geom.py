"""Shared offline geometry/rule model for planning and pre-write verification.

Source: evidence/GEOMETRY.txt (native read-only export) + the drl revision's native class export.
Pads use TRUE copper (size x rotation), not Altium's mask-inflated bounding box.
Clearance model mirrors the saved rule priorities that matter for new copper:
  escape zones (new scoped rules) 0.13  >  CLR_PADS_<comp>_010 pad-pad 0.10
  >  CLR_POWER_025 / CLR_ANALOG_025 0.25  >  CLR_GENERAL_020 0.20
Nothing here writes to Altium; Altium DRC remains the authority.
"""
import math
from shapely.geometry import LineString, Point, Polygon, box
from shapely.strtree import STRtree
from shapely import affinity

HERE = __file__.rsplit('work', 1)[0]
import os
GEOM = os.environ.get('GEOM_FILE', HERE + 'evidence/GEOMETRY.txt')
CLASSES = HERE + 'evidence/inputs/CLASSES.txt'
BOARD = box(*[float(v) for v in os.environ.get('BOARD_BOX', '12,12,83,48').split(',')]).buffer(2, 16)   # default: candidate B 75 x 40, r = 2
EDGE = 0.5
COPPER = ('Top Layer', 'Mid Layer 1', 'Mid Layer 2', 'Mid Layer 3', 'Mid Layer 4', 'Bottom Layer')   # C2 6L: L1..L6 (Mid3 = L4 GND, Mid4 = L5)
PAD_PAIR_010 = {'J_FPC1', 'J_FPC2', 'J_FPC3', 'J_FPC4', 'J_FPC5', 'UP4', 'UP2', 'UP1', 'U_MCU1'}

WIDE = set()
for l in open(CLASSES, encoding='utf-8', errors='replace'):
    f = l.rstrip('\n').split('|')
    if f[0] == 'MEMBER' and f[1] in ('EMG_POWER', 'EMG_ANALOG', 'EMG_ADC', 'EMG_REFERENCE'):
        WIDE.add(f[2])

# escape zones: list of (polygon, allowed_nets, allowed_component)
ZONES = []
# CLR_FINE_ESCAPE_<ref> regions, filled by load(): ref -> box(pads bbox + 1 mm)
FINE_ESC = {'U_MCU1', 'UP1', 'UP2', 'UP4', 'U_DRL1', 'C_DRL_DEC'}
FINE_REGIONS = {}


def base_clr(net):
    return 0.25 if net in WIDE else 0.2


class Obj:
    __slots__ = ('geom', 'net', 'kind', 'layers', 'comp', 'name', 'src')

    def __init__(self, geom, net, kind, layers, comp='', name='', src=None):
        self.geom, self.net, self.kind, self.layers, self.comp, self.name, self.src = geom, net, kind, layers, comp, name, src


def pad_poly(r):
    x, y = float(r[5]), float(r[6])
    rot = float(r[12].split('=')[1]); sx = float(r[13].split('=')[1]); sy = float(r[14].split('=')[1])
    shape = r[15]
    if shape == 'SHAPE=1' and abs(sx - sy) < 1e-6:
        return Point(x, y).buffer(sx / 2, 32)
    p = box(x - sx / 2, y - sy / 2, x + sx / 2, y + sy / 2)
    if shape == 'SHAPE=1':  # oblong: stadium along the long axis
        r_ = min(sx, sy) / 2
        a = (x - sx / 2 + r_, y) if sx >= sy else (x, y - sy / 2 + r_)
        b = (x + sx / 2 - r_, y) if sx >= sy else (x, y + sy / 2 - r_)
        p = LineString([a, b]).buffer(r_, 32)
    if abs(rot) % 360 > 1e-6:
        p = affinity.rotate(p, rot, origin=(x, y))
    return p


def load():
    rows = [l.rstrip('\n').split('|') for l in open(GEOM, encoding='utf-8', errors='replace')]
    objs, comps, keepouts = [], {}, []
    for r in rows:
        k = r[0]
        if k == 'PAD':
            layer = r[4]
            if layer not in COPPER + ('Multi Layer',):
                continue
            lay = set(COPPER) if layer == 'Multi Layer' else {layer}
            objs.append(Obj(pad_poly(r), r[3], 'PAD', lay, r[1], r[2], r))
            hole = float(r[11].split('=')[1])
            if hole > 0:
                objs.append(Obj(Point(float(r[5]), float(r[6])).buffer(hole / 2), r[3], 'HOLE', set(), r[1], r[2], r))
        elif k == 'VIA':
            c = Point(float(r[2]), float(r[3]))
            objs.append(Obj(c.buffer(float(r[4]) / 2, 24), r[1], 'VIA', set(COPPER), src=r))
            objs.append(Obj(c.buffer(float(r[5]) / 2), r[1], 'HOLE', set(), src=r))
        elif k == 'TRACK':
            if r[-1] == 'KEEPOUT=True' or r[1] == 'Keep Out Layer':
                g = LineString([(float(r[3]), float(r[4])), (float(r[5]), float(r[6]))]).buffer(float(r[7]) / 2)
                keepouts.append(g)
                continue
            if r[1] not in COPPER:
                continue
            g = LineString([(float(r[3]), float(r[4])), (float(r[5]), float(r[6]))]).buffer(float(r[7]) / 2, 16)
            objs.append(Obj(g, r[2], 'TRACK', {r[1]}, src=r))
        elif k == 'ARC':
            if r[1] in COPPER and r[-2] != 'INPOLY=True':
                objs.append(Obj(box(*map(float, r[3:7])), r[2], 'ARC', {r[1]}, src=r))
        elif k == 'REGION':
            if r[-2] == 'KEEPOUT=True' or r[1] == 'Keep Out Layer':
                keepouts.append(box(*map(float, r[3:7])))
            elif r[1] in COPPER and r[-3] != 'INPOLY=True' and r[-1] == 'KIND=0':
                objs.append(Obj(box(*map(float, r[3:7])), r[2], 'REGION', {r[1]}, src=r))
        elif k == 'FILL':
            if r[1] in COPPER:
                objs.append(Obj(box(*map(float, r[3:7])), r[2], 'FILL', {r[1]}, src=r))
        elif k == 'COMP':
            comps[r[1]] = r
    for c in FINE_ESC:
        ps = [o.geom for o in objs if o.kind == 'PAD' and o.comp == c]
        if ps:
            FINE_REGIONS[c] = box(min(p.bounds[0] for p in ps) - 1.0, min(p.bounds[1] for p in ps) - 1.0,
                                  max(p.bounds[2] for p in ps) + 1.0, max(p.bounds[3] for p in ps) + 1.0)
    # owning component of each keepout (for component-scoped rules such as the BK13 zones)
    pads_by_comp = {}
    for o in objs:
        if o.kind == 'PAD' and o.comp and o.comp != 'FREE':
            pads_by_comp.setdefault(o.comp, []).append(o.geom)
    from shapely.ops import unary_union
    hulls = {c: unary_union(v).envelope.buffer(0.3) for c, v in pads_by_comp.items()}
    for kg in keepouts:
        owner = ''
        for c, h in hulls.items():
            if h.contains(kg):
                owner = c; break
        objs.append(Obj(kg, '', 'KEEPOUT', set(COPPER), owner, 'keepout'))
    return objs, comps, keepouts


def _inside(poly, o):
    # Altium InRegionAbsolute: the object's bounding rectangle must lie completely inside the region
    return poly.contains(box(*o.geom.bounds))


def in_zone(o):
    for poly, nets, comp in ZONES:
        if (o.net in nets or o.comp == comp) and _inside(poly, o):
            return True
    return False


def required(a, b):
    """clearance between two objects of different nets (rule-priority order); keepouts included."""
    for poly, nets, comp in ZONES:
        if all((o.net in nets or o.comp == comp) and _inside(poly, o) for o in (a, b)):
            return 0.13
    if a.kind == 'PAD' and b.kind == 'PAD' and a.comp and a.comp == b.comp and a.comp in PAD_PAIR_010:
        return 0.10
    for p, t in ((a, b), (b, a)):
        if p.kind == 'PAD' and p.comp in FINE_REGIONS and t.kind == 'TRACK' and FINE_REGIONS[p.comp].contains(box(*t.geom.bounds)):
            return 0.15
    if 'KEEPOUT' in (a.kind, b.kind):
        o = b if a.kind == 'KEEPOUT' else a
        if o.kind == 'KEEPOUT':
            return 0.0
        return base_clr(o.net)
    return max(base_clr(a.net), base_clr(b.net))


class Index:
    def __init__(self, objs):
        self.objs = [o for o in objs if o.kind != 'HOLE']
        self.holes = [o for o in objs if o.kind == 'HOLE']
        self.tree = STRtree([o.geom for o in self.objs])
        self.htree = STRtree([o.geom for o in self.holes]) if self.holes else None
        self.extra = []  # objects added during planning

    def add(self, o):
        if o.kind == 'HOLE':
            self.holes.append(o)
        else:
            self.extra.append(o)

    def near(self, geom, d=0.4):
        for i in self.tree.query(geom.buffer(d)):
            yield self.objs[i]
        for o in self.extra:
            if o.geom.distance(geom) < d:
                yield o

    def violations(self, cand, ignore=()):
        """list of (other, distance, required) for cand vs existing copper (same layer, different net)."""
        out = []
        for o in self.near(cand.geom):
            if o is cand or o in ignore or (o.kind != 'KEEPOUT' and o.net == cand.net and cand.net not in ('-', '')):
                continue
            if not (o.layers & cand.layers):
                continue
            req = required(cand, o)
            d = cand.geom.distance(o.geom)
            if d < req - 1e-6:
                out.append((o, round(d, 4), req))
        return out

    def hole_ok(self, center, hole_r, hh=0.254):
        for o in self.holes:
            if o.geom.distance(center.buffer(hole_r)) < hh - 1e-6:
                return False
        return True


def edge_ok(geom):
    return BOARD.buffer(-EDGE).contains(geom)


def track(net, layer, pts, w):
    return Obj(LineString(pts).buffer(w / 2, 16), net, 'TRACK', {layer})


def via(net, x, y, d=0.6, h=0.3):
    return Obj(Point(x, y).buffer(d / 2, 24), net, 'VIA', set(COPPER))
