"""Render router4's view of one unrouted connection: free cells per layer, entry cells, pads, and which
clearance class blocks each cell.
usage: GEOM_FILE=... [PRELOAD=plan.csv] python debug_conn.py DRC.json NET MATCH [width] [pad_mm]
MATCH selects the connection whose text contains it (e.g. 'CU_21-1').  PRELOAD stamps a (partial) plan first,
so the picture shows the board as the router saw it at that point of a pass.
Colours: light = free for this net/width, dark grey = blocked by clearance only, red = other-net copper,
green = own-net copper, blue tint = via allowed, bright green = start cells, magenta = goal cells."""
import csv, json, os, sys
import numpy as np
from PIL import Image
import router4 as R

data = json.load(open(sys.argv[1]))
net = sys.argv[2]; match = sys.argv[3]
w = float(sys.argv[4]) if len(sys.argv) > 4 else 0.15
padmm = float(sys.argv[5]) if len(sys.argv) > 5 else 1.5
if os.environ.get('PRELOAD'):
    rows = [r for r in csv.DictReader(open(os.environ['PRELOAD'])) if r.get('kind') in ('TRACK', 'VIA')]
    R.stamp_rows(rows)
    print('preloaded', len(rows), 'rows')
conns = [c for c in (R.parse_conn(d) for d in data['details'] if d.startswith('Un-Routed')) if c and c[0] == net]
conns = [c for c in conns if match in c[1]['text'] or match in c[2]['text']]
net, a, b = conns[0]
print('connection:', a['text'], '->', b['text'])
ga, la = R.end_copper(a, net); gb, lb = R.end_copper(b, net)
print('end layers', la, lb)
W = R.window(ga, gb, padmm)
free, via_ok = R.maps(net, w, W)
allowed = R.allowed_layers(net)
s = R.end_nodes(ga, la, free, W, allowed); t = R.end_nodes(gb, lb, free, W, allowed)
print('window', W, 'starts', len(s), 'goals', len(t), 'allowed', sorted(allowed), 'clearance', R.G.base_clr(net))
iy0, iy1, ix0, ix1 = W
SC = 8
imgs = []
for L in R.LAYERS:
    if L not in allowed:
        continue
    o = R.own[L][iy0:iy1, ix0:ix1]
    rgb = np.zeros(o.shape + (3,), np.uint8)
    rgb[free[L]] = (235, 235, 235)
    rgb[(~free[L]) & (o == 0)] = (90, 90, 90)
    rgb[(o != 0) & (o != R.NID[net])] = (200, 60, 60)
    rgb[o == R.NID[net]] = (60, 160, 60)
    rgb[via_ok & free[L]] = rgb[via_ok & free[L]] // 2 + np.array([0, 0, 110], np.uint8)
    for st in s:
        if R.LAYERS[st[0]] == L:
            rgb[st[2], st[1]] = (0, 255, 0)
    for st in t:
        if R.LAYERS[st[0]] == L:
            rgb[st[2], st[1]] = (255, 0, 255)
    imgs.append(Image.fromarray(rgb).resize((rgb.shape[1] * SC, rgb.shape[0] * SC), Image.NEAREST))
tot_w = sum(i.width for i in imgs) + 20 * (len(imgs) - 1)
out = Image.new('RGB', (tot_w, max(i.height for i in imgs)), (255, 255, 255))
x = 0
for i in imgs:
    out.paste(i, (x, 0)); x += i.width + 20
fn = R.G.HERE + f'evidence/debug_{net}_{match.replace("-", "_")}.png'
out.save(fn)
print('saved', fn, 'layers left->right', [L for L in R.LAYERS if L in allowed],
      'window mm x', round(R.X0 + ix0 * R.RES, 2), round(R.X0 + ix1 * R.RES, 2), 'y', round(R.Y1 - iy1 * R.RES, 2), round(R.Y1 - iy0 * R.RES, 2))
