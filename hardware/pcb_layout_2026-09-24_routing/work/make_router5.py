"""Build router5.py from router4.py (router4 stays unchanged for reproducibility of pass 1).

router5 changes:
 1. Component targets: start/goal cells are ALL copper already connected to each end (same net, touching,
    shared layer; vias/through pads join layers), not just the two objects Altium's ratsnest names.
    A connection whose ends are already joined by earlier routes is reported 'already connected'.
 2. Scoped relaxed fallback: when the strict model (0.25 mm for EMG_POWER/ANALOG/ADC/REFERENCE) finds no path,
    retry with 0.20 mm for this connection's new copper only.  Such rows carry relax=1; they must be covered by
    a scoped Altium rule '(IsTrack Or IsVia) And InNet(net) And InRegionAbsolute(bbox)' vs All = 0.20 mm
    (layout brief s7: 0.25 mm 'where feasible'; narrowly scoped exceptions, never a board-wide relaxation).
    In relaxed mode fine-pitch pads are also kept at 0.20 (the new priority-1 rule overrides the 0.15 rule).
 3. Cheaper failure: small windows first, bounded budgets, big windows last.
"""
import re
src = open('router4.py', encoding='utf-8').read()

# ---- maps(): relaxed mode
old = """def maps(net, w, W, vd=VIA_D, vh=VIA_H):
    iy0, iy1, ix0, ix1 = W
    nid = NID[net]
    c = G.base_clr(net); hw = w / 2"""
new = """def maps(net, w, W, vd=VIA_D, vh=VIA_H, relax=False):
    iy0, iy1, ix0, ix1 = W
    nid = NID[net]
    c = 0.2 if relax else G.base_clr(net); hw = w / 2
    cw = 0.2 if relax else 0.25          # vs other nets' EMG_POWER/ANALOG/ADC/REFERENCE copper
    cf = 0.2 if relax else None          # vs fine-pitch pads (None: 0.15 in escape regions, else 0.25)"""
assert old in src; src = src.replace(old, new)
old = """        ok = (dn >= c + hw + MARGIN) & (dw >= 0.25 + hw + MARGIN) & (df >= np.where(fr, 0.15, 0.25) + hw + MARGIN)"""
new = """        ok = (dn >= c + hw + MARGIN) & (dw >= cw + hw + MARGIN) & (df >= (cf if cf is not None else np.where(fr, 0.15, 0.25)) + hw + MARGIN)"""
assert old in src; src = src.replace(old, new)
old = """        via_ok &= (dn >= c + r + MARGIN) & (dw >= 0.25 + r + MARGIN) & (df >= 0.25 + r + MARGIN)"""
new = """        via_ok &= (dn >= c + r + MARGIN) & (dw >= cw + r + MARGIN) & (df >= (cf if cf is not None else 0.25) + r + MARGIN)"""
assert old in src; src = src.replace(old, new)

# ---- component helpers + new route_one
old = src[src.index('def route_one(net, a, b):'):src.index('def prio(c):')]
new = '''def component(net, seed):
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


'''
src = src.replace(old, new)

# ---- run_pass: relax column, already-connected handling
src = src.replace("""        segs, vias, w, vd, vh = res
        new = []""", """        segs, vias, w, vd, vh, relax = res
        rx = 1 if relax else 0
        if why == 'already connected':
            done.add(ck); continue
        new = []""")
src = src.replace("""'w': w, 'd': '', 'h': '', 'conn': ck})""", """'w': w, 'd': '', 'h': '', 'conn': ck, 'relax': rx})""")
src = src.replace("""'w': '', 'd': vd, 'h': vh, 'conn': ck})""", """'w': '', 'd': vd, 'h': vh, 'conn': ck, 'relax': rx})""")
src = src.replace("""fieldnames=['kind', 'group', 'net', 'layer', 'x1', 'y1', 'x2', 'y2', 'w', 'd', 'h', 'conn']""",
                  """fieldnames=['kind', 'group', 'net', 'layer', 'x1', 'y1', 'x2', 'y2', 'w', 'd', 'h', 'conn', 'relax']""")
src = src.replace('"""Deterministic, rule-aware grid router v3', '"""router5 (see make_router5.py for the changes vs router4).  Deterministic, rule-aware grid router v3', 1)
assert src.count("'relax': rx") == 2 and src.count("'conn', 'relax']") == 2, 'patch count'
open('router5.py', 'w', encoding='utf-8').write(src)
print('router5.py written')
