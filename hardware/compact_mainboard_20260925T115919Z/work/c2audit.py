"""Offline placement audit for C2 (conservative screening; native Altium DRC is authoritative).

Checks (per side, x-ray aware):
  PAD      copper pads of different parts on a shared copper layer closer than PAD_GAP (Multi Layer = both sides)
  BODY     3D bodies (or pad-extent proxy) of different parts on the same side closer than BODY_GAP
  PADBODY  a pad under another part's body on the same side
  THT      a through-hole pad/hole vs a body on the OPPOSITE side (lead protrusion) closer than THT_GAP
  EDGE     pad copper closer than EDGE_CU to the outline, or a body outside it (edge parts exempt)
  ZONE     functional-zone rules (analog quiet bank, converter/charger keep-away, antenna exclusion)
"""
import math

PAD_GAP, BODY_GAP, THT_GAP, EDGE_CU = 0.25, 0.20, 0.25, 0.50     # C2 native DRC: EMG_POWER 0.25, component clearance 0.2
THT_PAD_GAP = 0.30                                                   # mask openings around through-hole pads (sliver rule 0.1)


def gap(a, b):
    dx = max(a[0] - b[2], b[0] - a[2])
    dy = max(a[1] - b[3], b[1] - a[3])
    if dx > 0 and dy > 0:
        return math.hypot(dx, dy)
    return max(dx, dy)


def pad_layers(q):
    return ('Top', 'Bottom') if q['layer'] == 'Multi Layer' else (('Top',) if q['layer'] == 'Top Layer' else ('Bottom',))


def _padbox(q):
    return (q['bx0'], q['by0'], q['bx1'], q['by1'])


def audit(out, outline, edge_exempt=(), holes=(), zones=None, ref=None):
    """ref: the native-verified B placement; a pair whose clearance is not worse than in B (i.e. kept together rigidly
    or moved apart) inherits B's native DRC acceptance and is not re-flagged"""
    probs = []
    X0, Y0, X1, Y1 = outline
    items = list(out.values())
    refpad = {}
    if ref:
        for r in ref.values():
            for q in r['pads']:
                refpad[(r['designator'], q['num'], round(q['x'], 3), round(q['y'], 3))] = q
        refidx = {(r['designator'], q['num']): q for r in ref.values() for q in r['pads']}

    def inherited_pad(da, qa, db, qb, g):
        if not ref:
            return False
        a, b = refidx.get((da, qa['num'])), refidx.get((db, qb['num']))
        if a is None or b is None:
            return False
        la, lb = pad_layers(a), pad_layers(b)
        if not set(la) & set(lb):
            return False
        return g >= gap(_padbox(a), _padbox(b)) - 1e-3

    def inherited_body(a, b, g):
        if not ref or a['designator'] not in ref or b['designator'] not in ref:
            return False
        ra, rb = ref[a['designator']], ref[b['designator']]
        if ra['side'] != rb['side']:
            return False
        g0 = min((gap(x, y) for x in ra['bodies'] for y in rb['bodies']), default=9)
        return g >= g0 - 1e-3
    pads = []
    for r in items:
        for q in r['pads']:
            pads.append((r['designator'], q, (q['bx0'], q['by0'], q['bx1'], q['by1'])))
    # PAD
    for i in range(len(pads)):
        da, qa, ba = pads[i]
        la = pad_layers(qa)
        for j in range(i + 1, len(pads)):
            db, qb, bb = pads[j]
            if da == db:
                continue
            if not set(la) & set(pad_layers(qb)):
                continue
            tht = qa.get('hole', 0) > 0 or qb.get('hole', 0) > 0
            if qa['net'] and qa['net'] == qb['net'] and qa['net'] != '-' and not tht:
                continue
            g = gap(ba, bb)
            if g < (THT_PAD_GAP if tht else PAD_GAP) and not inherited_pad(da, qa, db, qb, g):
                probs.append(('PAD', da, db, round(g, 3), '%s.%s/%s.%s' % (da, qa['num'], db, qb['num'])))
    # BODY / PADBODY / THT
    for i, a in enumerate(items):
        for b in items[i + 1:]:
            if a['designator'] == b['designator']:
                continue
            if gap((a['bx0'] - 3, a['by0'] - 3, a['bx1'] + 3, a['by1'] + 3), (b['bx0'], b['by0'], b['bx1'], b['by1'])) > 0:
                continue
            if a['side'] == b['side']:
                g = min((gap(x, y) for x in a['bodies'] for y in b['bodies']), default=9)
                if g < BODY_GAP and not inherited_body(a, b, g):
                    probs.append(('BODY', a['designator'], b['designator'], round(g, 3), a['side']))
                for s, t in ((a, b), (b, a)):
                    if t['proxy']:
                        continue
                    for q in s['pads']:
                        if q['layer'] == 'Multi Layer' or (q['layer'] == 'Top Layer') == (t['side'] == 'Top'):
                            for k, y in enumerate(t['bodies']):
                                g = gap(_padbox(q), y)
                                if g >= -0.05:
                                    continue
                                if ref and s['designator'] in ref and t['designator'] in ref and ref[s['designator']]['side'] == s['side'] \
                                        and ref[t['designator']]['side'] == t['side']:
                                    q0 = refidx.get((s['designator'], q['num']))
                                    y0 = ref[t['designator']]['bodies'][k] if k < len(ref[t['designator']]['bodies']) else None
                                    if q0 is not None and y0 is not None and g >= gap(_padbox(q0), y0) - 1e-3:
                                        continue
                                probs.append(('PADBODY', s['designator'], t['designator'], round(g, 3), q['num']))
            else:
                for s, t in ((a, b), (b, a)):
                    for q in s['pads']:
                        if q['layer'] == 'Multi Layer' and q.get('hole', 0) > 0:
                            for y in t['bodies']:
                                g = gap((q['bx0'], q['by0'], q['bx1'], q['by1']), y)
                                if g < THT_GAP:
                                    probs.append(('THT', s['designator'], t['designator'], round(g, 3), q['num']))
    for hx0, hy0, hx1, hy1, name in holes:
        for r in items:
            for y in r['bodies']:
                if gap((hx0, hy0, hx1, hy1), y) < THT_GAP:
                    probs.append(('HOLE', name, r['designator'], round(gap((hx0, hy0, hx1, hy1), y), 3), r['side']))
    # EDGE
    for r in items:
        if r['designator'] in edge_exempt:
            continue
        for q in r['pads']:
            e = min(q['bx0'] - X0, q['by0'] - Y0, X1 - q['bx1'], Y1 - q['by1'])
            if e < EDGE_CU:
                probs.append(('EDGE', r['designator'], q['num'], round(e, 3), 'pad copper'))
        for y in r['bodies']:
            e = min(y[0] - X0, y[1] - Y0, X1 - y[2], Y1 - y[3])
            if e < 0:
                probs.append(('EDGE', r['designator'], 'body', round(e, 3), 'outside'))
    # ZONES: zones = list of (name, side or '*', rect, predicate(designator)->allowed)
    for name, side, rect, allowed in (zones or []):
        for r in items:
            if side != '*' and r['side'] != side:
                continue
            if allowed(r):
                continue
            for y in r['bodies'] + [[q['bx0'], q['by0'], q['bx1'], q['by1']] for q in r['pads']]:
                if gap(rect, y) < 0:
                    probs.append(('ZONE', name, r['designator'], round(gap(rect, y), 3), r['side']))
                    break
    return probs


def summarize(probs, limit=12):
    from collections import defaultdict
    by = defaultdict(list)
    for p in probs:
        by[p[0]].append(p)
    lines = []
    for k in ('PAD', 'BODY', 'PADBODY', 'THT', 'HOLE', 'EDGE', 'ZONE'):
        v = by.get(k, [])
        lines.append('%-8s %d' % (k, len(v)))
        for p in sorted(v, key=lambda p: p[3])[:limit]:
            lines.append('    ' + ' | '.join(str(x) for x in p))
    return '\n'.join(lines)
