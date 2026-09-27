"""Read-only native BD-to-BE UART delta, DRC and scope review."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

import astra_verify_routing_delta as delta
import astra_verify_pcb_structure as structure
from astra_review_vc1_bd import drc

EV = Path(__file__).resolve().parent.parent / 'evidence'
PCB = EV.parent / 'C2_COMPACT_4L_2SIDE/MainBoard/EMG_MainBoard_Layout.PcbDoc'


def main():
    args = argparse.Namespace(before=EV / 'GEOMETRY_C2_6L_BD.txt', after=EV / 'GEOMETRY_C2_6L_BE.txt',
                              adds=EV / 'ASTRA_UART_READY_ADDS.csv', dels=EV / 'ASTRA_UART_READY_DELS.csv',
                              tol_mm=.00015, allow_move=[])
    adds, dels = delta.plan(args.adds, True), delta.plan(args.dels, False)
    expected_nets = {'WIFI_UART_RX', 'WIFI_UART_TX', 'WIFI_BOOT', 'VSYS', 'SYS_EN', 'MCU_SPI_MISO'}
    plan_scope = (Counter(r['kind'] for r in adds) == {'TRACK': 18, 'VIA': 1}
                  and Counter(r['kind'] for r in dels) == {'TRACK': 15}
                  and {r['net'] for r in adds+dels} == expected_nets
                  and all(r['kind'] == 'TRACK' and r['values'][4] == .4 for r in adds if r['net'] == 'VSYS'))
    graph = json.loads((EV / 'ASTRA_UART_READY_GRAPH_REVIEW.json').read_text(encoding='utf-8'))
    current_hashes = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in (args.before, args.adds, args.dels)}
    graph_inputs_match = graph['passed'] and all(current_hashes.get(r['path']) == r['sha256'] for r in graph['inputs'])
    geometry = delta.verify(args)
    via_identity = ('VSYS', (43.125, 41.625, .45, .2))
    original_via = all(sum(o['kind'] == 'VIA' and (o['net'], o['values']) == via_identity
                           for o in delta.geometry(p)['free']) == 1 for p in (args.before, args.after))
    before, after = drc(EV / 'DRC_C2_6L_BD.txt.html'), drc(EV / 'DRC_C2_6L_BE.txt.html')
    old_opens = Counter(row for row in before['details'] if row.startswith('Un-Routed Net Constraint:'))
    new_opens = Counter(row for row in after['details'] if row.startswith('Un-Routed Net Constraint:'))
    target = Counter({row: count for row, count in old_opens.items()
                      if row.startswith('Un-Routed Net Constraint: Net WIFI_UART_RX Between ')})
    resolved_only = sum(target.values()) == 1 and new_opens == old_opens - target
    critical = ('Clearance Constraint', 'Short-Circuit Constraint', 'Width Constraint', 'Component Clearance Constraint')
    violations = [(name, count) for name, count in after['summary'] if name.startswith(critical) and count]
    streams = structure.compare(structure.snapshot(EV / 'ASTRA_BE_BEFORE_20260927/EMG_MainBoard_Layout.PcbDoc'),
                                structure.snapshot(PCB))
    documents = []
    manifest = EV / 'ASTRA_BE_BEFORE_20260927/BEFORE_HASHES.json'
    for record in json.loads(manifest.read_text(encoding='utf-8-sig')):
        source = Path(record['Path'])
        if source.suffix.lower() not in ('.schdoc', '.prjpcb'):
            continue
        current = PCB.parent / source.name
        actual = hashlib.sha256(current.read_bytes()).hexdigest()
        documents.append({'path': str(current), 'before_sha256': record['Hash'].lower(),
                          'after_sha256': actual, 'unchanged': actual == record['Hash'].lower()})
    scope = all(streams['separate_invariants'].values()) and len(documents) == 9 and all(r['unchanged'] for r in documents)
    report = {'passed': plan_scope and graph_inputs_match and geometry['passed'] and original_via and resolved_only
                         and not violations and scope,
              'plan_scope_passed': plan_scope, 'prewrite_graph_inputs_match': graph_inputs_match,
              'original_vsys_via_retained': original_via, 'native_geometry_delta': geometry,
              'native_drc': {'before_total': before['total'], 'after_total': after['total'],
                             'before_open_count': sum(old_opens.values()), 'after_open_count': sum(new_opens.values()),
                             'only_wifi_uart_rx_resolved_other_opens_identical': resolved_only,
                             'removed_open_details': list((old_opens-new_opens).elements()),
                             'added_open_details': list((new_opens-old_opens).elements()),
                             'remaining_open_details': list(new_opens.elements()),
                             'critical_nonzero_summary_rows': violations,
                             'removed_all_violation_details': list((Counter(before['details'])-Counter(after['details'])).elements()),
                             'added_all_violation_details': list((Counter(after['details'])-Counter(before['details'])).elements())},
              'saved_structure': streams, 'schematics_and_project': documents,
              'inputs': [{'path': str(p), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
                         for p in (args.before, args.after, args.adds, args.dels, EV / 'DRC_C2_6L_BD.txt.html', EV / 'DRC_C2_6L_BE.txt.html')],
              'limits': ['Opaque pad/text protected-stream differences remain retained and are not waived.',
                         'Native DRC and geometry validate this delta, not the remaining board completion work.',
                         'No CAD modifications, router or native application operations performed by this checker.']}
    out = EV / 'ASTRA_BE_INDEPENDENT_REVIEW.json'
    out.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'passed': report['passed'], 'plan_scope': plan_scope, 'graph_inputs_match': graph_inputs_match,
                      'geometry_passed': geometry['passed'], 'original_vsys_via_retained': original_via,
                      'native_drc': report['native_drc'], 'structure_invariants': streams['separate_invariants'],
                      'raw_structure_errors': streams['errors'], 'schematics_and_project_unchanged': scope,
                      'evidence': str(out)}, indent=2))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
