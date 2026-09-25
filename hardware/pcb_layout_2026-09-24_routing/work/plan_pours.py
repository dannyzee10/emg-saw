"""Plan the pour stage (offline; Altium DRC is the authority).

Emits evidence/POUR_OPS.txt (POLY/CUTOUT ops for apply_ops_v6.pas) and evidence/STITCH_PLAN.csv (GND vias,
plan format for build_ops.py):
  * GND polygons on L1 (Top) and L3 (Mid Layer 2), outline = board outline inset 0.5 mm (edge setback),
    same settings as the existing L2/L4 pours (solid, pour over same net, remove dead copper, 0.2 mm necks).
  * Polygon cutouts on all four copper layers over the ST67W611M1 antenna keep-out (DS14784 s6.2 item 2:
    no copper or traces in the antenna area on any layer), in addition to the existing keep-out region.
  * GND stitching vias (0.6/0.3, as the project default) on a staggered grid, at the board perimeter and
    around the radio module body, wherever the via clears other-net copper on every layer, keepouts,
    the antenna zone and the edge.  L2/L4 are continuous GND planes, so every such via ties L1/L3 fill down.
usage: GEOM_FILE=... python plan_pours.py [grid_mm]
"""
import csv, math, sys
import numpy as np
from shapely.geometry import JOIN_STYLE, Point, box
import router4 as R
import geom as G

GRID = float(sys.argv[1]) if len(sys.argv) > 1 else 2.5
ANT = box(44.19, 54.44, 56.47, 59.44)          # project antenna keep-out (matches ST antenna portion)
ANT_CLEAR = ANT.buffer(1.0)                    # no stitching vias within 1 mm of the antenna zone
outline = G.BOARD.buffer(-0.5, join_style=JOIN_STYLE.mitre)
pts = ';'.join(f'{x:.4f},{y:.4f}' for x, y in list(outline.exterior.coords)[:-1])
ops = [f'POLY|EMG_L1_COMMON_GND|GND|Top Layer|{pts}', f'POLY|EMG_L3_COMMON_GND|GND|Mid Layer 2|{pts}']
cut = box(44.19, 54.44, 56.47, 55.5)            # on-board part of the antenna zone (board edge y = 55)
cpts = ';'.join(f'{x:.4f},{y:.4f}' for x, y in list(cut.exterior.coords)[:-1])
for L in ('Top Layer', 'Mid Layer 1', 'Mid Layer 2', 'Bottom Layer'):
    ops.append(f'CUTOUT|{L}|{cpts}')
open(G.HERE + 'evidence/POUR_OPS.txt', 'w').write('\n'.join(ops) + '\n')

# via sites: GND via must clear everything that is not GND on all layers (router4 via model incl. mask web,
# hole-to-hole, keepouts and edge), plus the antenna zone
W = (0, R.NY, 0, R.NX)
free, via_ok = R.maps('GND', 0.2, W, 0.6, 0.3)
own_gnd_pad = np.zeros_like(via_ok)
cand = []
for j, y in enumerate(np.arange(10.8, 54.3, GRID)):
    for x in np.arange(10.8 + (GRID / 2 if j % 2 else 0), 89.3, GRID):
        cand.append((round(x, 3), round(y, 3)))
# perimeter ring (1.3 mm in from the edge) and a ring around the radio module body
ring = G.BOARD.buffer(-1.3, join_style=JOIN_STYLE.mitre).exterior
cand += [(round(p.x, 3), round(p.y, 3)) for p in (ring.interpolate(d) for d in np.arange(0, ring.length, 1.5))]
wifi = [o.geom for o in R.objs if o.kind == 'PAD' and o.comp == 'U_WIFI1']
if wifi:
    from shapely.ops import unary_union
    body = unary_union(wifi).envelope.buffer(0.9, join_style=JOIN_STYLE.mitre).exterior
    cand += [(round(p.x, 3), round(p.y, 3)) for p in (body.interpolate(d) for d in np.arange(0, body.length, 1.2))]
def site_ok(x, y, chosen, spacing):
    if ANT_CLEAR.contains(Point(x, y)):
        return False
    ix = int((x - R.X0) / R.RES); iy = int((R.Y1 - y) / R.RES)
    if not (0 <= ix < R.NX and 0 <= iy < R.NY) or not via_ok[iy, ix]:
        return False
    return not any(math.dist((x, y), c) < spacing for c in chosen)


# 1) return vias first (report check G5): every signal via gets a GND via within about 1 mm, so return current
#    can change reference plane with the signal
gnd_vias = [(o.geom.centroid.x, o.geom.centroid.y) for o in R.objs if o.kind == 'VIA' and o.net == 'GND']
sig_vias = [(o.geom.centroid.x, o.geom.centroid.y) for o in R.objs if o.kind == 'VIA' and o.net not in ('GND', '', '-')]
chosen, g5_missing = [], []
for sx, sy in sig_vias:
    if any(math.dist((sx, sy), g) <= 1.05 for g in gnd_vias + chosen):
        continue
    placed = False
    for rr in (0.9, 1.0, 1.1, 1.25, 1.4):
        for a in range(0, 360, 20):
            x, y = round(sx + rr * math.cos(math.radians(a)), 3), round(sy + rr * math.sin(math.radians(a)), 3)
            if site_ok(x, y, chosen, 0.9):
                chosen.append((x, y)); placed = True; break
        if placed:
            break
    if not placed:
        g5_missing.append((round(sx, 3), round(sy, 3)))
n_return = len(chosen)
# 2) grid, perimeter and module-ring stitching
for x, y in cand:
    if site_ok(x, y, chosen, 1.2):
        chosen.append((x, y))
print('signal vias', len(sig_vias), 'return vias added', n_return, 'signal vias without a GND via within 1.4 mm', len(g5_missing), g5_missing[:20])
with open(G.HERE + 'evidence/STITCH_PLAN.csv', 'w', newline='') as f:
    wr = csv.DictWriter(f, fieldnames=['kind', 'group', 'net', 'layer', 'x1', 'y1', 'x2', 'y2', 'w', 'd', 'h'])
    wr.writeheader()
    for k, (x, y) in enumerate(chosen):
        wr.writerow({'kind': 'VIA', 'group': f'STITCH{k}', 'net': 'GND', 'layer': 'Multi Layer', 'x1': x, 'y1': y,
                     'x2': '', 'y2': '', 'w': '', 'd': 0.6, 'h': 0.3})
print('pour ops', len(ops), 'candidates', len(cand), 'stitch vias', len(chosen))
