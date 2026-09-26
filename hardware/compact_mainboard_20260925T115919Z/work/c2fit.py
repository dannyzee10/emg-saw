"""Incremental legality check + spot search for C2 planning (uses the c2audit criteria)."""
import math
from c2audit import gap, pad_layers, PAD_GAP, BODY_GAP, THT_GAP, EDGE_CU, THT_PAD_GAP


def _pb(q):
    return (q['bx0'], q['by0'], q['bx1'], q['by1'])


def conflicts(cand, out, outline, zones=(), vias=(), holes=(), edge_exempt=(), ignore=(), stop_at_first=False):
    """list of conflicts of the placed records in `cand` (dict) against `out` (dict), zones, through vias and holes"""
    X0, Y0, X1, Y1 = outline
    res = []
    others = [r for d, r in out.items() if d not in cand and d not in ignore]
    for c in cand.values():
        cb = (c['bx0'] - 4, c['by0'] - 4, c['bx1'] + 4, c['by1'] + 4)
        near = [r for r in others if gap(cb, (r['bx0'], r['by0'], r['bx1'], r['by1'])) <= 0]
        for r in near:
            for qa in c['pads']:
                la = set(pad_layers(qa))
                for qb in r['pads']:
                    if not la & set(pad_layers(qb)):
                        continue
                    if qa['net'] and qa['net'] == qb['net'] and qa['net'] != '-' and not (qa.get('hole', 0) or qb.get('hole', 0)):
                        continue
                    need = THT_PAD_GAP if (qa.get('hole', 0) > 0 or qb.get('hole', 0) > 0) else PAD_GAP
                    if gap(_pb(qa), _pb(qb)) < need:
                        res.append(('PAD', c['designator'], r['designator']))
                        if stop_at_first:
                            return res
            if c['side'] == r['side']:
                if min((gap(x, y) for x in c['bodies'] for y in r['bodies']), default=9) < BODY_GAP:
                    res.append(('BODY', c['designator'], r['designator']))
                    if stop_at_first:
                        return res
                for s, t in ((c, r), (r, c)):
                    for q in s['pads']:
                        if q['layer'] == 'Multi Layer' or (q['layer'] == 'Top Layer') == (t['side'] == 'Top'):
                            if any(gap(_pb(q), y) < 0.05 for y in t['bodies']):
                                res.append(('PADBODY', s['designator'], t['designator']))
                                if stop_at_first:
                                    return res
            else:
                for s, t in ((c, r), (r, c)):
                    for q in s['pads']:
                        if q['layer'] == 'Multi Layer' and q.get('hole', 0) > 0 and any(gap(_pb(q), y) < THT_GAP for y in t['bodies']):
                            res.append(('THT', s['designator'], t['designator']))
                            if stop_at_first:
                                return res
        # through vias (x, y, dia, net, owner): pads of other nets on either side must clear them
        for vx, vy, vd, vnet, owner in vias:
            if owner == c['designator']:
                continue
            vb = (vx - vd / 2, vy - vd / 2, vx + vd / 2, vy + vd / 2)
            for q in c['pads']:
                if q['net'] != vnet and gap(_pb(q), vb) < PAD_GAP:
                    res.append(('VIA', c['designator'], owner))
                    if stop_at_first:
                        return res
        for hb, name in holes:
            if any(gap(hb, y) < THT_GAP for y in c['bodies']) or any(gap(hb, _pb(q)) < 0.3 for q in c['pads']):
                res.append(('HOLE', c['designator'], name))
                if stop_at_first:
                    return res
        if c['designator'] not in edge_exempt:
            for q in c['pads']:
                if min(q['bx0'] - X0, q['by0'] - Y0, X1 - q['bx1'], Y1 - q['by1']) < EDGE_CU:
                    res.append(('EDGE', c['designator'], q['num']))
                    if stop_at_first:
                        return res
            for y in c['bodies']:
                if min(y[0] - X0, y[1] - Y0, X1 - y[2], Y1 - y[3]) < 0:
                    res.append(('EDGE', c['designator'], 'body'))
                    if stop_at_first:
                        return res
        for name, side, rect, allowed in zones:
            if (side == '*' or c['side'] == side) and not allowed(c):
                if any(gap(rect, y) < 0 for y in c['bodies'] + [list(_pb(q)) for q in c['pads']]):
                    res.append(('ZONE', c['designator'], name))
                    if stop_at_first:
                        return res
    return res


def spiral(cx, cy, rmax, step):
    yield cx, cy
    r = step
    while r <= rmax + 1e-9:
        n = max(8, int(2 * math.pi * r / step))
        for k in range(n):
            a = 2 * math.pi * k / n
            yield cx + r * math.cos(a), cy + r * math.sin(a)
        r += step


def find_spot(make, out, outline, target, rmax=6.0, step=0.2, rots=(0, 90, 180, 270), **kw):
    """make(x, y, rot) -> {designator: record}; returns (records, x, y, rot) of the nearest legal spot to target"""
    for x, y in spiral(target[0], target[1], rmax, step):
        for rot in rots:
            cand = make(x, y, rot)
            if not conflicts(cand, out, outline, stop_at_first=True, **kw):
                return cand, x, y, rot
    return None
