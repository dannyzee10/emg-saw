"""Geometry kernel for candidate C2 planning (offline aid; native Altium readback/DRC is the evidence).

Loads candidate B's verified saved state (PLAN_B_COMPONENTS.csv + GEOMETRY_B_TRIAL.txt pads) and re-derives every
pad / bbox of a part from its final (origin, rotation, side), using Altium's conventions proven on B:
  top    world = o + R(rot) . local
  bottom world = o + R(rot) . My . local          (My: y -> -y)
  FlipComponent sets rot -> (180 - rot) mod 360; the writer then sets X/Y (and Rotation when a turn is planned).
"""
import csv, math, os
from collections import defaultdict

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EV = os.path.join(HERE, 'evidence')


def R(deg, x, y):
    a = math.radians(deg)
    c, s = round(math.cos(a), 12), round(math.sin(a), 12)
    return c * x - s * y, s * x + c * y


def load_b(comp_csv='PLAN_B_COMPONENTS.csv', geom='GEOMETRY_B_TRIAL.txt'):
    parts = {}
    for r in csv.DictReader(open(os.path.join(EV, comp_csv))):
        for k in ('x', 'y', 'bx0', 'by0', 'bx1', 'by1'):
            r[k] = float(r[k])
        r['rot'] = float(r['rot'])
        r['pads'] = []
        parts[r['designator']] = r
    lines = [l.rstrip('\n').split('|') for l in open(os.path.join(EV, geom), encoding='utf-8', errors='replace')]
    for f in lines:
        # native origin / rotation / side are authoritative (plan CSVs keep the pre-flip rotation of flipped parts)
        if f[0] == 'COMP' and f[1] in parts:
            r = parts[f[1]]
            r['x'], r['y'], r['rot'] = float(f[3]), float(f[4]), float(f[5])
            r['side'] = 'Bottom' if f[2].startswith('Bottom') else 'Top'
    for f in lines:
        if f[0] != 'PAD':
            continue
        if f[1] == 'FREE':
            ref, num, net, layer = 'FP:' + f[2], '1', f[3], f[4]
        else:
            ref, num, net, layer = f[1], f[2], f[3], f[4]
        x, y, x0, y0, x1, y1 = map(float, f[5:11])
        kv = dict(p.split('=') for p in f[11:] if '=' in p)
        if ref not in parts:
            continue
        parts[ref]['pads'].append({'num': num, 'net': net, 'layer': layer, 'x': x, 'y': y, 'bx0': x0, 'by0': y0, 'bx1': x1, 'by1': y1,
                                   'hole': float(kv.get('HOLE', 0))})
    # 3D body extents (native export of the placed B state); parts without a body get a pad-extent proxy
    bf = os.path.join(EV, 'BODIES_B_PLACED.txt')
    for l in open(bf, encoding='utf-8', errors='replace'):
        f = l.rstrip('\n').split('|')
        if f[0] != 'BODYC' or f[1] not in parts:
            continue
        kv = dict(p.split('=', 1) for p in f[3:] if '=' in p)
        boxes = []
        for seg in kv.get('BODYLAYERS', '').split(';'):
            if '@' in seg:
                c = [float(v) for v in seg.split('@')[1].split(',')]
                boxes.append(c)
        parts[f[1]]['bodies'] = boxes
        parts[f[1]]['hmax'] = float(kv.get('HMAX', 0) or 0)
    for r in parts.values():
        r.setdefault('bodies', [])
        r.setdefault('hmax', 0.0)
        r['proxy'] = not r['bodies']
        if r['designator'].startswith('FP:'):
            r['bodies'] = []      # bare copper test pad: no body
            continue
        if not r['bodies'] and r['pads']:
            # no 3D model: Altium's component clearance then uses the component extent, so use the courtyard/pad bbox
            r['bodies'] = [[r['bx0'], r['by0'], r['bx1'], r['by1']]]
    return parts


def to_local(p, x, y):
    """world point of part p (B state) -> part-local coordinates"""
    dx, dy = x - p['x'], y - p['y']
    lx, ly = R(-p['rot'], dx, dy)
    if p['side'] == 'Bottom':
        ly = -ly
    return lx, ly


def to_world(o, rot, side, lx, ly):
    if side == 'Bottom':
        ly = -ly
    wx, wy = R(rot, lx, ly)
    return o[0] + wx, o[1] + wy


def swap_layer(layer):
    pairs = {'Top Layer': 'Bottom Layer', 'Top Paste': 'Bottom Paste', 'Top Solder': 'Bottom Solder', 'Top Overlay': 'Bottom Overlay'}
    pairs.update({v: k for k, v in list(pairs.items())})
    return pairs.get(layer, layer)


def place(p, ox, oy, rot, side):
    """return a new record for part p at final origin/rot/side with re-derived bbox and pads"""
    n = {k: v for k, v in p.items() if k not in ('pads', 'bodies')}
    n['x'], n['y'], n['rot'], n['side'] = ox, oy, rot % 360, side

    def box(b):
        xs, ys = [], []
        for cx, cy in ((b[0], b[1]), (b[2], b[1]), (b[0], b[3]), (b[2], b[3])):
            wx, wy = to_world((ox, oy), rot, side, *to_local(p, cx, cy))
            xs.append(wx); ys.append(wy)
        return [min(xs), min(ys), max(xs), max(ys)]
    n['bx0'], n['by0'], n['bx1'], n['by1'] = box((p['bx0'], p['by0'], p['bx1'], p['by1']))
    n['bodies'] = [box(b) for b in p.get('bodies', [])]
    n['pads'] = []
    flip = side != p['side']
    for q in p['pads']:
        m = dict(q)
        m['x'], m['y'] = to_world((ox, oy), rot, side, *to_local(p, q['x'], q['y']))
        cs = [to_world((ox, oy), rot, side, *to_local(p, a, b)) for a, b in ((q['bx0'], q['by0']), (q['bx1'], q['by1']))]
        m['bx0'], m['bx1'] = min(c[0] for c in cs), max(c[0] for c in cs)
        m['by0'], m['by1'] = min(c[1] for c in cs), max(c[1] for c in cs)
        if flip:
            m['layer'] = swap_layer(q['layer'])
        n['pads'].append(m)
    return n


def group_transform(parts, members, kind, *args):
    """rigid group move of B-state members.
       ('T', dx, dy)            translate
       ('F', cx, cy)            flip whole group to the other side: mirror in X about the group bbox centre, centre -> (cx, cy)
       ('R', deg, cx, cy)       rotate CCW about the group bbox centre, centre -> (cx, cy)
       ('FR', deg, cx, cy)      flip then rotate (both about the centre), centre -> (cx, cy)
    returns {designator: placed record}"""
    mem = [parts[m] for m in members]
    gx = (min(r['bx0'] for r in mem) + max(r['bx1'] for r in mem)) / 2
    gy = (min(r['by0'] for r in mem) + max(r['by1'] for r in mem)) / 2
    out = {}
    for r in mem:
        if kind == 'T':
            dx, dy = args
            out[r['designator']] = place(r, r['x'] + dx, r['y'] + dy, r['rot'], r['side'])
            continue
        if kind == 'F':
            deg, cx, cy = 0.0, args[0], args[1]
        elif kind == 'R':
            deg, cx, cy = args
        else:
            deg, cx, cy = args
        px, py = r['x'] - gx, r['y'] - gy
        side, rot = r['side'], r['rot']
        if kind in ('F', 'FR'):
            px = -px
            side = 'Bottom' if side == 'Top' else 'Top'
            rot = (180 - rot) % 360
        px, py = R(deg, px, py)
        out[r['designator']] = place(r, cx + px, cy + py, rot + deg, side)
    return out


def render(recs, path, window=None, outline=None, zones=(), title='', label=True, sides=('Top', 'Bottom'), scale=18):
    """recs: {designator: record}; draws bbox (courtyard proxy) + pads; top grey/blue, bottom green/red (x-ray from top)"""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    if window is None:
        b = bbox_of(list(recs.values()))
        window = (b[0] - 1, b[1] - 1, b[2] + 1, b[3] + 1)
    wx0, wy0, wx1, wy1 = window
    fig, ax = plt.subplots(figsize=((wx1 - wx0) / 25.4 * scale / 2.2, (wy1 - wy0) / 25.4 * scale / 2.2))
    for zx0, zy0, zx1, zy1, col, name in zones:
        ax.add_patch(Rectangle((zx0, zy0), zx1 - zx0, zy1 - zy0, fill=False, hatch='///', ec=col, lw=0.8, alpha=0.6, label=name))
    if outline:
        x0, y0, x1, y1 = outline
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, ec='k', lw=1.6))
    for d, r in recs.items():
        if r['side'] not in sides:
            continue
        top = r['side'] == 'Top'
        ax.add_patch(Rectangle((r['bx0'], r['by0']), r['bx1'] - r['bx0'], r['by1'] - r['by0'], fill=not top,
                               fc='#9fd49f' if not top else 'none', ec='#666' if top else '#2a7a2a', lw=0.6, alpha=0.55 if not top else 1))
        for q in r['pads']:
            c = '#c9a227' if q['layer'] == 'Multi Layer' else ('#3b6fd6' if q['layer'] == 'Top Layer' else '#d64b3b')
            ax.add_patch(Rectangle((q['bx0'], q['by0']), q['bx1'] - q['bx0'], q['by1'] - q['by0'], fc=c, ec='none', alpha=0.75))
        if label and wx0 <= r['x'] <= wx1 and wy0 <= r['y'] <= wy1:
            fs = 4.5 if (r['bx1'] - r['bx0']) * (r['by1'] - r['by0']) < 20 else 6
            ax.text((r['bx0'] + r['bx1']) / 2, (r['by0'] + r['by1']) / 2, d, fontsize=fs, ha='center', va='center',
                    color='#000' if top else '#0b3d0b', fontweight='bold' if not top else 'normal')
    ax.set_xlim(wx0, wx1); ax.set_ylim(wy0, wy1); ax.set_aspect('equal'); ax.grid(alpha=0.25)
    ax.set_title(title, fontsize=8)
    if zones:
        ax.legend(loc='upper left', fontsize=5)
    fig.tight_layout(); fig.savefig(path, dpi=150); plt.close(fig)


def bbox_of(recs):
    return (min(r['bx0'] for r in recs), min(r['by0'] for r in recs), max(r['bx1'] for r in recs), max(r['by1'] for r in recs))
