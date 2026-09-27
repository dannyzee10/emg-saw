"""Small read-only connectivity check for the final UART partial reroutes."""
from collections import defaultdict
import hashlib
import json
import os
from pathlib import Path

EV = Path(__file__).resolve().parent.parent / 'evidence'
GEOM = EV / 'GEOMETRY_C2_6L_BD.txt'
ADDS = EV / 'ASTRA_UART_READY_ADDS.csv'
DELS = EV / 'ASTRA_UART_READY_DELS.csv'
os.environ['GEOM_FILE'] = str(GEOM)
import geom as G
import astra_verify_routing_delta as D
from shapely.strtree import STRtree


def partitions(entries):
    if not entries:
        return {}
    tree = STRtree([o.geom for _, o in entries])
    parent = list(range(len(entries)))
    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    for i, (_, o) in enumerate(entries):
        for j in tree.query(o.geom.buffer(.00015)):
            j = int(j)
            if j <= i:
                continue
            q = entries[j][1]
            if o.layers & q.layers and o.geom.distance(q.geom) <= .00015:
                parent[find(j)] = find(i)
    return {identity: find(i) for i, (identity, _) in enumerate(entries)}


def main():
    adds, dels = D.plan(ADDS, True), D.plan(DELS, False)
    nets = sorted({o['net'] for o in adds+dels})
    objects = [(i, o) for i, o in enumerate(G.load()[0])
               if o.net in nets and o.kind not in ('HOLE', 'KEEPOUT')]
    removed = set()
    for row in dels:
        matches = []
        for identity, o in objects:
            if identity in removed or o.src is None:
                continue
            s = o.src
            if o.kind == 'TRACK' and 'INCOMP=False' in s and 'INPOLY=False' in s:
                primitive = D.primitive('TRACK', s[2], s[1], s[3:8], s)
            elif o.kind == 'VIA':
                primitive = D.primitive('VIA', s[1], '', s[2:6], s)
            else:
                continue
            if D.match_error(row, primitive, .00015) is not None:
                matches.append(identity)
        if len(matches) != 1:
            raise ValueError('Deletion has nonunique native match: ' + str(row))
        removed.add(matches[0])
    remaining = [(i, o) for i, o in objects if i not in removed]
    after = list(remaining)
    for i, row in enumerate(adds):
        v = row['values']
        o = (G.track(row['net'], row['layer'], [(v[0], v[1]), (v[2], v[3])], v[4])
             if row['kind'] == 'TRACK' else G.via(row['net'], *v))
        after.append(('new_' + str(i), o))
    graphs = {}
    all_preserved = True
    for net in nets:
        old, new = [(i, o) for i, o in objects if o.net == net], [(i, o) for i, o in after if o.net == net]
        before_components, after_components = partitions(old), partitions(new)
        connected_before = defaultdict(list)
        for identity, _ in old:
            if identity not in removed:
                connected_before[before_components[identity]].append(identity)
        splits = [ids for ids in connected_before.values() if len({after_components[i] for i in ids}) > 1]
        old_ids = {i for i, o in remaining if o.net == net}
        attached = {after_components[i] for i in old_ids}
        detached_additions = [i for i, _ in new if isinstance(i, str) and after_components[i] not in attached]
        pads = [{'ref': o.comp, 'pin': o.name, 'component_after': after_components[i]}
                for i, o in old if o.kind == 'PAD']
        row = {'before_component_count': len(set(before_components.values())),
               'after_component_count': len(set(after_components.values())),
               'all_retained_copper_connections_preserved': not splits,
               'split_retained_object_ids': splits, 'detached_additions': detached_additions, 'pads': pads}
        if net == 'WIFI_UART_RX':
            source = next(i for i, o in old if o.kind == 'PAD' and o.comp == 'U_WIFI1' and o.name == '23')
            target = next(i for i, o in old if o.kind == 'VIA' and o.src[2:4] == ['43.5250', '40.0750'])
            row['requested_endpoints_connected_after'] = after_components[source] == after_components[target]
            all_preserved &= row['requested_endpoints_connected_after']
        all_preserved &= not splits and not detached_additions
        graphs[net] = row
    original_vsys_via_retained = any(o.kind == 'VIA' and o.net == 'VSYS'
        and o.src[2:6] == ['43.1250', '41.6250', '0.4500', '0.2000'] for _, o in remaining)
    power_width = all(r['kind'] == 'TRACK' and r['values'][4] >= .4 for r in adds if r['net'] == 'VSYS')
    report = {'passed': bool(all_preserved and original_vsys_via_retained and power_width),
              'graphs': graphs, 'original_vsys_via_retained': original_vsys_via_retained,
              'all_new_vsys_tracks_at_least_040_mm': power_width,
              'deletions_matched': len(removed), 'additions': len(adds),
              'inputs': [{'path': str(p), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
                         for p in (GEOM, ADDS, DELS)],
              'limits': ['No router or native CAD operation; only six-net copper connectivity graphs.',
                         'Uses native exported copper shapes with 0.00015 mm readback tolerance.',
                         'Pours are not completely represented; native DRC and readback remain required.',
                         'Retained copper overlap proves connectivity, not constant effective junction width.']}
    (EV / 'ASTRA_UART_READY_GRAPH_REVIEW.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
