"""Small exact local CS detour trials with moved testpad and fixed TX escape."""
import csv
import hashlib
import json
import os
import time
from pathlib import Path

EV = Path(__file__).resolve().parent.parent / 'evidence'
GEOM = EV / 'GEOMETRY_C2_6L_BF.txt'
ADDS = EV / 'ASTRA_BF_CS_INSPECT_WIDE_BRIDGE_ADDS.csv'
DELS = EV / 'ASTRA_BF_CS_INSPECT_PRUNED_DELS.csv'
OUT = EV / 'ASTRA_BF_CS_TX_DETOUR_ADDS.csv'
SEED = EV / 'ASTRA_BF_TX_PADMOVE_SEED_ADDS.csv'
REPORT = EV / 'ASTRA_BF_CS_TX_DETOUR_CHECK.json'
os.environ['GEOM_FILE'] = str(GEOM)
os.environ['BOARD_BOX'] = '12,12,67.1,44'
import geom as G
import astra_verify_routing_delta as D
from shapely import affinity
from shapely.geometry import Point


def describe(q):
    return {'kind': q.kind, 'net': q.net, 'ref': q.comp, 'pin': q.name, 'record': q.src}


def main():
    begun = time.monotonic()
    objects, _, keepouts = G.load()
    removed, deleted_vias = set(), []
    for row in D.plan(DELS, False):
        matches = []
        for i, q in enumerate(objects):
            if i in removed or q.src is None:
                continue
            s = q.src
            if q.kind == 'TRACK' and 'INCOMP=False' in s and 'INPOLY=False' in s:
                primitive = D.primitive('TRACK', s[2], s[1], s[3:8], s)
            elif q.kind == 'VIA':
                primitive = D.primitive('VIA', s[1], '', s[2:6], s)
            else:
                continue
            if D.match_error(row, primitive, .00015) is not None:
                matches.append(i)
        if len(matches) != 1:
            raise ValueError('Nonunique delete: ' + repr(row))
        removed.add(matches[0])
        if objects[matches[0]].kind == 'VIA':
            deleted_vias.append(objects[matches[0]].src)
    after = [q for i, q in enumerate(objects) if i not in removed and
             not (q.kind == 'HOLE' and q.src in deleted_vias)]
    pad = next(q for q in after if q.kind == 'PAD' and q.name == 'TP_GND_DIG')
    pad.geom = affinity.translate(pad.geom, .20, 0)
    pad.src = list(pad.src) + ['PLANNED_MOVE_X=+0.20']
    rows = list(csv.DictReader(ADDS.open(encoding='utf-8-sig')))
    selected = [r for r in rows if r['kind'] == 'TRACK' and r['net'] == 'WIFI_SPI_CS'
                and r['layer'] == 'Bottom Layer' and
                tuple(float(r[k]) for k in ('x1', 'y1', 'x2', 'y2', 'w')) == (53.275, 44.025, 58.525, 44.025, .18)]
    assert len(selected) == 1
    old = selected[0]
    for r in rows:
        if r is old:
            continue
        x, y = float(r['x1']), float(r['y1'])
        if r['kind'] == 'TRACK':
            q = G.track(r['net'], r['layer'], [(x, y), (float(r['x2']), float(r['y2']))], float(r['w']))
            q.src = ['TRACK', r['layer'], r['net'], r['x1'], r['y1'], r['x2'], r['y2'], r['w'], 'PENDING_CS']
            after.append(q)
        else:
            q = G.via(r['net'], x, y, float(r['d']), float(r['h']))
            q.src = ['VIA', r['net'], r['x1'], r['y1'], r['d'], r['h'], 'PENDING_CS']
            after.extend([q, G.Obj(Point(x, y).buffer(float(r['h']) / 2), q.net, 'HOLE', set(), src=q.src)])
    txvia = G.via('MCU_WIFI_UART_TX', 56.08, 44.30, .45, .20)
    txvia.src = ['VIA', 'MCU_WIFI_UART_TX', '56.08', '44.30', '0.45', '0.20', 'TX_SEED']
    txstub = G.track('MCU_WIFI_UART_TX', 'Top Layer', [(56.08, 43.238), (56.08, 44.30)], .20)
    txstub.src = ['TRACK', 'Top Layer', 'MCU_WIFI_UART_TX', '56.08', '43.238', '56.08', '44.30', '0.20', 'TX_SEED']
    sourcevia = G.via('MCU_WIFI_UART_TX', 44.026, 40.805, .45, .20)
    sourcevia.src = ['VIA', 'MCU_WIFI_UART_TX', '44.026', '40.805', '0.45', '0.20', 'TX_SEED_FILLED_CAPPED_VIP']
    index_before_tx = G.Index(after)
    initial_tx_hits = [hit for q in (txvia, txstub, sourcevia) for hit in index_before_tx.violations(q)]
    assert not initial_tx_hits, repr([(q.net, gap, need) for q, gap, need in initial_tx_hits])
    seed_holes = []
    for q, p in ((sourcevia, (44.026, 40.805)), (txvia, (56.08, 44.30))):
        drill = Point(p).buffer(.1)
        if index_before_tx.htree is not None:
            for i in index_before_tx.htree.query(drill.buffer(.45)):
                other = index_before_tx.holes[i]
                assert other.geom.distance(drill) >= G.hole_gap(other) - 1e-6, repr(other.src)
        assert G.edge_ok(q.geom) and not any(k.intersects(q.geom) for k in keepouts)
        seed_holes.append(G.Obj(drill, q.net, 'HOLE', set(), src=q.src))
    after.extend([sourcevia, txvia, txstub, *seed_holes])
    index = G.Index(after)
    allowed = G.BOARD.buffer(-G.EDGE)
    trials, passes = [], []
    for y in (43.75, 43.725, 43.70):
        dy = 44.025 - y
        for left in (55.3, 55.35, 55.4, 55.45, 55.5, 55.55, 55.6):
            for right in (56.5, 56.55, 56.6, 56.65, 56.7, 56.75, 56.8):
                points = [(53.275, 44.025), (left, 44.025), (round(left + dy, 6), y),
                          (round(right - dy, 6), y), (right, 44.025), (58.525, 44.025)]
                if points[2][0] >= points[3][0]:
                    continue
                tracks = [G.track('WIFI_SPI_CS', 'Bottom Layer', [a, b], .18) for a, b in zip(points, points[1:])]
                blockers = [dict(describe(q), gap=gap, required=need, segment=[a, b])
                            for a, b, t in zip(points, points[1:], tracks) for q, gap, need in index.violations(t)]
                edge = all(allowed.contains(t.geom) for t in tracks)
                keepout = any(k.intersects(t.geom) for k in keepouts for t in tracks)
                trial = {'points': points, 'width': .18, 'passed': not blockers and edge and not keepout,
                         'edge_clear': edge, 'keepout': keepout, 'blockers': blockers,
                         'minimum_TX_via_gap_mm': min(t.geom.distance(txvia.geom) for t in tracks)}
                trials.append(trial)
                if trial['passed']:
                    passes.append(trial)
    chosen = max(passes, key=lambda t: (t['points'][2][1], t['minimum_TX_via_gap_mm'])) if passes else None
    if chosen:
        newrows = [r for r in rows if r is not old]
        for a, b in zip(chosen['points'], chosen['points'][1:]):
            r = dict(old)
            r.update(group='ASTRA_CS_TX_LOCAL_DETOUR', x1=a[0], y1=a[1], x2=b[0], y2=b[1])
            newrows.append(r)
        with OUT.open('w', newline='') as handle:
            writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(newrows)
        seed_rows = [dict(kind='VIA', group='ASTRA_TX_PADMOVE_SEED_FILLED_CAPPED_VIP', net='MCU_WIFI_UART_TX',
                         layer='Multi Layer', x1=x, y1=y, x2='', y2='', w='', d=.45, h=.20,
                         conn='requires TP_GND_DIG to 56.871,44.829 and CS local detour', relax=0)
                     for x, y in ((44.026, 40.805), (56.08, 44.30))]
        seed_rows.append(dict(kind='TRACK', group='ASTRA_TX_PADMOVE_SEED', net='MCU_WIFI_UART_TX',
                             layer='Top Layer', x1=56.08, y1=43.238, x2=56.08, y2=44.30, w=.20, d='', h='',
                             conn='requires TP_GND_DIG to 56.871,44.829 and CS local detour', relax=0))
        with SEED.open('w', newline='') as handle:
            writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(seed_rows)
    report = {'inputs': [{'path': str(p), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in (GEOM, ADDS, DELS)],
              'exact_deleted_primitives': len(removed), 'original_additions': len(rows),
              'pad_move': {'name': 'TP_GND_DIG', 'from': [56.671, 44.829], 'to': [56.871, 44.829]},
              'fixed_TX_seed': [sourcevia.src, txvia.src, txstub.src], 'trials': trials, 'chosen': chosen,
              'trials_count': len(trials), 'passes_count': len(passes), 'seconds': time.monotonic() - begun,
              'candidate_csv': str(OUT) if chosen else None,
              'tx_seed_csv': str(SEED) if chosen else None,
              'limits': ['Local Bottom CS detour collision check only; no router or CAD write.',
                         'Output changes only the one CS segment; pad move and TX seed are required separate operations.',
                         'Full candidate verification and native DRC remain required.']}
    REPORT.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: report[k] for k in ('trials_count', 'passes_count', 'chosen', 'seconds', 'candidate_csv', 'tx_seed_csv')}), flush=True)


if __name__ == '__main__':
    main()
