"""Why does a connection fail?  Imports router5 (same env as a routing run) and, per unrouted connection of a DRC json,
reports: endpoint copper found?, entry cells per layer at each end (6 mm window, preferred width), legal via cells within
1 mm of each end, and whether the two ends fall in one connected free region (layers joined where vias are legal).
usage: <router env> python diag_route.py DRC.json [net,net,...]"""
import json, sys
import numpy as np
from scipy import ndimage
sys.argv = [sys.argv[0]] + sys.argv[1:]
import router5 as R

data = json.load(open(sys.argv[1]))
only = set(sys.argv[2].split(',')) if len(sys.argv) > 2 and sys.argv[2] else None
conns = [c for c in (R.parse_conn(d) for d in data['details'] if d.startswith('Un-Routed')) if c]
if only:
    conns = [c for c in conns if c[0] in only]
for net, a, b in conns:
    ga, la = R.end_copper(a, net); gb, lb = R.end_copper(b, net)
    if ga is None or gb is None:
        print(f'{net:16s} ENDPOINT NOT MATCHED  {a["text"][:40]} | {b["text"][:40]}'); continue
    w = R.widths(net)[-1]
    W = R.window(ga, gb, 6.0)
    free, via_ok = R.maps(net, w, W)
    allowed = R.allowed_layers(net)
    ca = R.component(net, ga) if net != 'GND' else [(ga, la)]
    cb = R.component(net, gb) if net != 'GND' else [(gb, lb)]
    s = R.comp_nodes(ca, free, W, allowed); t = R.comp_nodes(cb, free, W, allowed)
    per = lambda nodes: {R.LAYERS[L][:6]: sum(1 for n in nodes if n[0] == L) for L in range(len(R.LAYERS)) if any(n[0] == L for n in nodes)}
    # connectivity: label each layer's free cells, then union labels through legal via cells
    labs, offs, tot = [], [], 0
    for L in R.LAYERS:
        f = free[L] if L in allowed else np.zeros_like(via_ok)
        lab, n = ndimage.label(f, structure=np.ones((3, 3)))
        labs.append(np.where(lab > 0, lab + tot, 0)); tot += n
    par = list(range(tot + 1))

    def fd(x):
        while par[x] != x:
            par[x] = par[par[x]]; x = par[x]
        return x
    vy, vx = np.nonzero(via_ok)
    for y, x in zip(vy, vx):
        ids = [int(lab[y, x]) for lab in labs if lab[y, x] > 0]
        for i in ids[1:]:
            par[fd(i)] = fd(ids[0])
    sa = {fd(int(labs[n[0]][n[2], n[1]])) for n in s if labs[n[0]][n[2], n[1]] > 0}
    sb = {fd(int(labs[n[0]][n[2], n[1]])) for n in t if labs[n[0]][n[2], n[1]] > 0}
    iy0, iy1, ix0, ix1 = W

    def vias_near(g):
        c = g.centroid
        cx, cy = int((c.x - R.X0) / R.RES) - ix0, int((R.Y1 - c.y) / R.RES) - iy0
        r = int(1.0 / R.RES)
        return int(via_ok[max(0, cy - r):cy + r, max(0, cx - r):cx + r].sum())
    verdict = 'CONNECTED-REGION (budget?)' if sa & sb else ('A BOXED' if not s else ('B BOXED' if not t else 'SEPARATED'))
    print(f'{net:16s} {verdict:26s} A{per(s)} vias@A {vias_near(ga)} | B{per(t)} vias@B {vias_near(gb)}  '
          f'{a["text"][:34]} -> {b["text"][:34]}')
