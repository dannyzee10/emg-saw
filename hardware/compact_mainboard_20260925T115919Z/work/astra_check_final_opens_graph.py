"""Small read-only candidate graph check; no routing or CAD writes.

Besides normal connectivity, compare retained power-copper connectivity after
excluding tracks narrower than each original width threshold and 0.40 mm. This catches a replacement branch that
reaches its source only through a previously unrelated thin pad feed. It does
not prove effective junction width, current capacity, or complete pour geometry.
"""
import argparse
from collections import defaultdict
import hashlib
import json
import os
from pathlib import Path
import astra_verify_routing_delta as D
from shapely.strtree import STRtree

ENDPOINTS = {
    'MCU_WIFI_UART_TX': (('R_WIFI_UART_TX_LINK', '2'), ('U_MCU1', '92')),
    'WIFI_SPI_CS': (('U_WIFI1', '24'), ('R_WIFI_CS_PD', '1'), ('R_SPI_CS', '1')),
}


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
            if j > i:
                q = entries[j][1]
                if o.layers & q.layers and o.geom.distance(q.geom) <= .00015:
                    parent[find(j)] = find(i)
    return {identity: find(i) for i, (identity, _) in enumerate(entries)}


def preserved(old, new, removed):
    before, after = partitions(old), partitions(new)
    connected = defaultdict(list)
    for identity, _ in old:
        if identity not in removed:
            connected[before[identity]].append(identity)
    splits = [ids for ids in connected.values() if len({after[i] for i in ids}) > 1]
    return before, after, splits


def describe(identity, objects):
    o = objects[identity]
    return {'id': identity, 'kind': o.kind, 'net': o.net, 'ref': o.comp, 'pin': o.name,
            'native_record': o.src, 'bounds': list(o.geom.bounds)}


def power_thresholds(old, widths):
    return sorted({.4} | {round(widths[i], 6) for i, o in old if o.kind == 'TRACK'})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--before', required=True, type=Path)
    parser.add_argument('--adds', required=True, type=Path)
    parser.add_argument('--dels', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--require-net', action='append', choices=sorted(ENDPOINTS), required=True)
    args = parser.parse_args()
    os.environ['GEOM_FILE'] = str(args.before.resolve())
    import geom as G

    D.geometry(args.before)  # Require a complete native export before using G.
    adds, dels = D.plan(args.adds, True), D.plan(args.dels, False)
    nets = sorted({o['net'] for o in adds+dels} | set(args.require_net))
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
    widths = {i: float(o.src[7]) for i, o in objects if o.kind == 'TRACK'}
    for i, row in enumerate(adds):
        v = row['values']
        o = (G.track(row['net'], row['layer'], [(v[0], v[1]), (v[2], v[3])], v[4])
             if row['kind'] == 'TRACK' else G.via(row['net'], *v))
        identity = 'new_' + str(i)
        after.append((identity, o))
        if row['kind'] == 'TRACK':
            widths[identity] = v[4]
    power_nets = set()
    for line in Path(G.CLASSES).read_text(encoding='utf-8', errors='replace').splitlines():
        fields = line.split('|')
        if len(fields) >= 3 and fields[0] == 'MEMBER' and fields[1] == 'EMG_POWER':
            power_nets.add(fields[2])
    lookup = dict(objects+after)
    graphs, power = {}, {}
    all_preserved = True
    for net in nets:
        old = [(i, o) for i, o in objects if o.net == net]
        new = [(i, o) for i, o in after if o.net == net]
        before_components, after_components, splits = preserved(old, new, removed)
        attached = {after_components[i] for i, o in remaining if o.net == net}
        detached = [i for i, _ in new if isinstance(i, str) and after_components[i] not in attached]
        pads = [{'ref': o.comp, 'pin': o.name, 'component_after': after_components[i]}
                for i, o in old if o.kind == 'PAD']
        row = {'before_component_count': len(set(before_components.values())),
               'after_component_count': len(set(after_components.values())),
               'all_retained_copper_connections_preserved': not splits,
               'split_retained_objects': [[describe(i, lookup) for i in group] for group in splits],
               'detached_additions': detached, 'pads': pads}
        if net in args.require_net:
            endpoint_ids = []
            for ref, pin in ENDPOINTS[net]:
                matches = [i for i, o in old if o.kind == 'PAD' and o.comp == ref and o.name == pin]
                if len(matches) != 1:
                    raise ValueError('Endpoint not unique: ' + repr((net, ref, pin)))
                endpoint_ids.extend(matches)
            row['requested_endpoints_connected_after'] = len({after_components[i] for i in endpoint_ids}) == 1
            all_preserved &= row['requested_endpoints_connected_after']
        all_preserved &= not splits and not detached
        graphs[net] = row
        if net in power_nets:
            checks = []
            source_ids=[i for i,o in old if net=='3V3_DIG' and o.kind=='PAD' and o.comp=='UP2' and o.name=='1']
            source_paths={i:{'ref':o.comp,'pin':o.name,'before_maximum_track_threshold_mm':0.0,'after_maximum_track_threshold_mm':0.0}
                          for i,o in old if o.kind=='PAD' and i not in source_ids}
            for threshold in power_thresholds(old, widths):
                wide_old = [(i, o) for i, o in old if o.kind != 'TRACK' or widths[i] >= threshold-.00015]
                wide_new = [(i, o) for i, o in new if o.kind != 'TRACK' or widths[i] >= threshold-.00015]
                before_wide, after_wide, power_splits = preserved(wide_old, wide_new, removed)
                if len(source_ids)==1:
                    source=source_ids[0]
                    for identity,r in source_paths.items():
                        if before_wide[identity]==before_wide[source]: r['before_maximum_track_threshold_mm']=threshold
                        if after_wide[identity]==after_wide[source]: r['after_maximum_track_threshold_mm']=threshold
                fragments=[]
                for group in power_splits:
                    pieces=defaultdict(list)
                    for identity in group: pieces[after_wide[identity]].append(identity)
                    fragments.append([{'retained_object_count':len(ids),
                                       'pads':[describe(i,lookup) for i in ids if lookup[i].kind=='PAD'],
                                       'vias':[describe(i,lookup) for i in ids if lookup[i].kind=='VIA'],
                                       'tracks':[describe(i,lookup) for i in ids if lookup[i].kind=='TRACK']}
                                      for ids in pieces.values()])
                checks.append({'minimum_track_width_mm':threshold, 'retained_connectivity_preserved':not power_splits,
                               'split_retained_objects':[[describe(i,lookup) for i in group] for group in power_splits],
                               'after_fragments':fragments})
            power[net] = {
                'retained_connectivity_at_original_width_thresholds_preserved':all(r['retained_connectivity_preserved'] for r in checks),
                'threshold_checks':checks,
                'source_pad': 'UP2.1' if len(source_ids)==1 else None,
                'source_to_pad_thresholds':list(source_paths.values()) if len(source_ids)==1 else [],
                'regressed_source_to_pad_thresholds':[r for r in source_paths.values()
                    if len(source_ids)==1 and r['after_maximum_track_threshold_mm']<r['before_maximum_track_threshold_mm']-.00015],
                'new_sub040_tracks': [r for r in adds if r['net'] == net and r['kind'] == 'TRACK' and r['values'][4] < .4-.00015],
            }
            all_preserved &= power[net]['retained_connectivity_at_original_width_thresholds_preserved']
    report = {'passed': bool(all_preserved), 'requested_nets': args.require_net,
              'graphs': graphs, 'power_width_path_preservation': power,
              'deletions_matched': len(removed), 'additions': len(adds),
              'inputs': [{'path': str(p.resolve()), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
                         for p in (args.before, args.adds, args.dels)],
              'limits': ['No router/native operation; affected-net copper graphs only.',
                         'Exported copper shapes use 0.00015 mm contact tolerance; pour geometry is incomplete.',
                         'Power threshold comparison detects newly required thin tracks, not effective junction widths or current capacity.',
                         'Native exact geometry, DRC and protected structure checks remain required.']}
    args.output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'passed': report['passed'], 'additions': len(adds), 'deletions': len(removed),
                      'graphs': {n: {k: v for k, v in r.items() if k not in ('pads','split_retained_objects')} for n, r in graphs.items()},
                      'power_width_path_preservation': {n:{'passed':r['retained_connectivity_at_original_width_thresholds_preserved'],
                          'thresholds':[{'minimum_track_width_mm':t['minimum_track_width_mm'],
                                         'passed':t['retained_connectivity_preserved'],
                                         'split_group_count':len(t['split_retained_objects'])} for t in r['threshold_checks']],
                          'new_sub040_track_count':len(r['new_sub040_tracks'])} for n,r in power.items()},
                      'output': str(args.output)}, indent=2))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
