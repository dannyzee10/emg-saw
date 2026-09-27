"""Read-only native BFS-to-BG verification preserving the saved user trace edit."""
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
FROZEN = {
    'ASTRA_CS_FINAL_ADDS.csv': 'b713babdb147ff524d17168a47eff48c87f4089c44e58c4744d79bb6a185ff2e',
    'ASTRA_CS_FINAL_DELS.csv': 'e204cb66ca68241bea0044e2f687120cc8e1f680b081883882b0517d55793e97',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    apply_path = EV / 'ASTRA_APPLY_BG_REBASED.txt'
    apply_lines = delta.read_text(apply_path).splitlines()
    apply_passed = (bool(apply_lines) and apply_lines[-1] == 'COMPLETE'
                    and 'PHASE1_OK|TRACKS=82|VIAS=12|DELETES=48|RULES=0' in apply_lines
                    and 'SAVED' in apply_lines
                    and 'AFTER_REOPEN|NET_TRACKS=2269|VIAS=464|TENTED_BOTH=0|RULES=147' in apply_lines)
    args = argparse.Namespace(before=EV / 'GEOMETRY_C2_6L_BFS.txt',
                              after=EV / 'GEOMETRY_C2_6L_BG.txt',
                              adds=EV / 'ASTRA_CS_FINAL_ADDS.csv',
                              dels=EV / 'ASTRA_CS_FINAL_DELS.csv',
                              tol_mm=.00015, allow_move=[])
    adds, dels = delta.plan(args.adds, True), delta.plan(args.dels, False)
    expected_nets = {'WIFI_SPI_RDY', 'MCU_SPI_MOSI', 'GND', 'VSYS', 'WIFI_SPI_CS',
                     'MCU_SWDIO', 'WIFI_CHIP_EN', '3V3_DIG', 'MCU_SPI_MISO',
                     'WIFI_UART_TX', 'SYS_EN'}
    frozen_passed = all(sha(EV / name) == digest for name, digest in FROZEN.items())
    scope_passed = (frozen_passed
                    and Counter(r['kind'] for r in adds) == {'TRACK': 82, 'VIA': 12}
                    and Counter(r['kind'] for r in dels) == {'TRACK': 40, 'VIA': 8}
                    and {r['net'] for r in adds + dels} == expected_nets
                    and all(r['kind'] == 'VIA' or r['layer'] in
                            {'Top Layer', 'Mid Layer 2', 'Mid Layer 4', 'Bottom Layer'} for r in adds)
                    and all(r['values'][4] == .4 for r in adds
                            if r['net'] in {'3V3_DIG', 'VSYS'} and r['kind'] == 'TRACK'))
    graph_path = EV / 'ASTRA_BFS_CS_FINAL_GRAPH.json'
    graph = json.loads(graph_path.read_text(encoding='utf-8-sig'))
    current_hashes = {str(p): sha(p) for p in (args.before, args.adds, args.dels)}
    graph_passed = (graph['passed'] and len(graph['inputs']) == 3
                    and all(current_hashes.get(r['path']) == r['sha256'] for r in graph['inputs'])
                    and all(r['retained_connectivity_at_original_width_thresholds_preserved']
                            for r in graph['power_width_path_preservation'].values()))
    geometry = delta.verify(args)
    live_user_path = EV / 'GEOMETRY_UNSAVED_BEFORE_BG.txt'
    user_adds_path = EV / 'ASTRA_USER_EDIT_OBSERVED_ADDS.csv'
    user_rows = delta.plan(user_adds_path, True)
    live_user, saved_before, saved_after = (delta.geometry(p) for p in
                                          (live_user_path, args.before, args.after))
    saved_user_baseline_passed = (all(live_user[key] == saved_before[key] for key in ('pads', 'comps', 'fixed'))
                                  and Counter(o['source'] for o in live_user['free'])
                                  == Counter(o['source'] for o in saved_before['free']))
    user_track_matches = [
        {'user_track': row, 'before_match_count': sum(delta.match_error(row, o, .00015) is not None
                                                     for o in saved_before['free']),
         'after_match_count': sum(delta.match_error(row, o, .00015) is not None
                                 for o in saved_after['free'])} for row in user_rows]
    user_edit_preserved = (saved_user_baseline_passed and len(user_rows) == 7
                           and all(row['kind'] == 'TRACK' and row['net'] == 'NetJ_FPC1_8'
                                   and row['layer'] == 'Top Layer' and row['values'][4] == .2
                                   for row in user_rows)
                           and all(r['before_match_count'] == r['after_match_count'] == 1
                                   for r in user_track_matches)
                           and all(r['net'] != 'NetJ_FPC1_8' for r in adds + dels))
    before, after = drc(EV / 'DRC_C2_6L_BFS.txt.html'), drc(EV / 'DRC_C2_6L_BG.txt.html')
    old_details, new_details = Counter(before['details']), Counter(after['details'])
    old_opens = Counter({r: n for r, n in old_details.items() if r.startswith('Un-Routed Net Constraint:')})
    new_opens = Counter({r: n for r, n in new_details.items() if r.startswith('Un-Routed Net Constraint:')})
    target = Counter({r: n for r, n in old_opens.items()
                      if r.startswith('Un-Routed Net Constraint: Net WIFI_SPI_CS Between ')})
    resolved_only = sum(target.values()) == 1 and new_opens == old_opens - target
    only_target_violation_changed = new_details == old_details - target
    critical = ('Clearance Constraint', 'Short-Circuit Constraint', 'Width Constraint',
                'Component Clearance Constraint', 'Routing Layers Constraint')
    critical_rows = [(name, count) for name, count in after['summary'] if name.startswith(critical) and count]
    coverage_names = critical + ('Routing Via Style Constraint',)
    category_coverage = {
        prefix: {'present_in_native_summary': any(name.startswith(prefix) for name, _ in after['summary']),
                 'violation_count': sum(count for name, count in after['summary'] if name.startswith(prefix))
                 if any(name.startswith(prefix) for name, _ in after['summary']) else None}
        for prefix in coverage_names}
    core_drc_coverage = all(category_coverage[prefix]['present_in_native_summary'] for prefix in critical[:4])
    old_snapshot = structure.snapshot(EV / 'ASTRA_BFS_BEFORE_BG_20260927/EMG_MainBoard_Layout.PcbDoc')
    new_snapshot = structure.snapshot(PCB)
    streams = structure.compare(old_snapshot, new_snapshot)
    component_diagnostic = {}
    try:
        old_parameters, old_count = structure.board_parameters(old_snapshot['streams']['Components6/Data'])
        new_parameters, new_count = structure.board_parameters(new_snapshot['streams']['Components6/Data'])
        changed_fields = []
        for key in sorted(set(old_parameters) | set(new_parameters)):
            a, b = old_parameters.get(key, []), new_parameters.get(key, [])
            if a != b:
                changed_fields.append({'key': key, 'before_count': len(a), 'after_count': len(b),
                                       'different_values': [{'record_index': i, 'before': x, 'after': y}
                                                            for i, (x, y) in enumerate(zip(a, b)) if x != y],
                                       'removed_values': a[len(b):], 'added_values': b[len(a):]})
        design_fields_unchanged = (old_count == new_count == 231
                                  and all(r['key'] == 'SELECTION' and r['before_count'] == r['after_count'] == 231
                                          and not r['removed_values'] and not r['added_values']
                                          and all(v['before'] in ('TRUE', 'FALSE') and v['after'] in ('TRUE', 'FALSE')
                                                  for v in r['different_values']) for r in changed_fields))
        component_diagnostic = {'before_record_count': old_count, 'after_record_count': new_count,
                                'changed_fields': changed_fields,
                                'design_parameters_identical_except_ui_selection': design_fields_unchanged,
                                'note': 'Exact UI selection-only disposition. Every other parsed parameter is equal; raw stream difference remains recorded.'}
    except ValueError as exc:
        component_diagnostic = {'error': str(exc)}
    documents = []
    manifest = EV / 'ASTRA_BFS_BEFORE_BG_20260927/BEFORE_HASHES.json'
    for record in json.loads(manifest.read_text(encoding='utf-8-sig')):
        source = Path(record.get('Path', record.get('Name', '')))
        if source.suffix.lower() in ('.schdoc', '.prjpcb'):
            current = PCB.parent / source.name
            expected_hash = record.get('Hash', record.get('SHA256', '')).lower()
            current_hash = sha(current)
            documents.append({'path': str(current), 'before_sha256': expected_hash,
                              'after_sha256': current_hash, 'unchanged': current_hash == expected_hash})
    documents_passed = len(documents) == 9 and all(r['unchanged'] for r in documents)
    protected_scope = (all(value for key, value in streams['separate_invariants'].items()
                           if key != 'components_bytes_unchanged')
                       and component_diagnostic.get('design_parameters_identical_except_ui_selection', False)
                       and documents_passed)
    authorized_delta_passed = (apply_passed and scope_passed and graph_passed and geometry['passed']
                               and user_edit_preserved and resolved_only and not critical_rows
                               and core_drc_coverage and protected_scope)
    report = {
        'passed': bool(authorized_delta_passed and only_target_violation_changed),
        'authorized_copper_delta_and_saved_design_scope_passed': bool(authorized_delta_passed),
        'native_apply_save_reopen_passed': apply_passed,
        'frozen_plan_hashes_match': frozen_passed, 'plan_scope_passed': scope_passed,
        'prewrite_graph_and_power_inputs_match': graph_passed, 'native_geometry_delta': geometry,
        'user_edit_preservation': {'passed': user_edit_preserved,
                                   'saved_bfs_matches_complete_unsaved_export_excluding_polygon_generation': saved_user_baseline_passed,
                                   'all_seven_user_tracks': user_track_matches},
        'native_drc': {
            'before_total': before['total'], 'after_total': after['total'],
            'before_open_count': sum(old_opens.values()), 'after_open_count': sum(new_opens.values()),
            'only_wifi_spi_cs_resolved_other_opens_identical': resolved_only,
            'only_target_violation_changed': only_target_violation_changed,
            'removed_open_details': list((old_opens - new_opens).elements()),
            'added_open_details': list((new_opens - old_opens).elements()),
            'remaining_open_details': list(new_opens.elements()),
            'critical_nonzero_summary_rows': critical_rows,
            'category_coverage': category_coverage,
            'missing_routing_categories': [prefix for prefix in coverage_names
                                            if not category_coverage[prefix]['present_in_native_summary']],
            'removed_all_violation_details': list((old_details - new_details).elements()),
            'added_all_violation_details': list((new_details - old_details).elements())},
        'saved_structure': streams, 'component_field_diagnostic': component_diagnostic,
        'schematics_and_project': documents,
        'inputs': [{'path': str(p), 'sha256': sha(p)} for p in
                   (args.before, args.after, args.adds, args.dels, graph_path, live_user_path, user_adds_path, apply_path,
                    EV / 'DRC_C2_6L_BFS.txt.html', EV / 'DRC_C2_6L_BG.txt.html')],
        'limits': ['Raw pad/text/body protected-stream differences remain reported separately; native exported pad/component geometry must be identical.',
                   'Native DRC and geometry verify this copper delta, not full finishing or electromagnetic performance.',
                   'A missing native DRC summary category is unverified, never a checked zero. Routing-layer and via-style batch coverage must be completed separately when absent.',
                   'Power preservation uses the original track-width connectivity thresholds, not a current-capacity or copper-junction analysis.',
                   'This checker performs no CAD writes, routing or native application operations.']}
    out = EV / 'ASTRA_BG_INDEPENDENT_REVIEW.json'
    out.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'passed': report['passed'], 'plan_scope': scope_passed,
                      'authorized_copper_delta_and_saved_design_scope_passed': bool(authorized_delta_passed),
                      'native_apply_save_reopen_passed': apply_passed,
                      'graph_and_power_inputs_match': graph_passed, 'geometry_passed': geometry['passed'],
                      'saved_user_edit_preserved': user_edit_preserved,
                      'native_drc': report['native_drc'], 'structure_invariants': streams['separate_invariants'],
                      'raw_structure_errors': streams['errors'],
                      'component_field_diagnostic': component_diagnostic,
                      'schematics_and_project_unchanged': documents_passed, 'evidence': str(out)}, indent=2))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
