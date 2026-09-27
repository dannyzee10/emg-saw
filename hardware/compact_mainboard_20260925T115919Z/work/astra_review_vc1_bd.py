"""Independent read-only review of the authorized seven-track BC-to-BD delta."""
import argparse
from collections import Counter
import hashlib
import html
import json
from pathlib import Path
import re

import astra_verify_routing_delta as delta
import astra_verify_pcb_structure as structure

EV = Path(__file__).resolve().parent.parent / 'evidence'
PCB = EV.parent / 'C2_COMPACT_4L_2SIDE/MainBoard/EMG_MainBoard_Layout.PcbDoc'


def drc(path):
    text = path.read_text(encoding='utf-8', errors='replace')
    summary = [(html.unescape(name), int(count)) for name, count in re.findall(
        r'<td class="column1"><a href="#ID\w+">(.*?)</a></td>\s*<td class="column2">(\d+)</td>', text)]
    details = [html.unescape(row).strip() for row in re.findall(
        r'<acronym title="dxpprocess[^"]*">(.*?)</acronym>', text, re.S)]
    total = re.search(r'Rule Violations:</td>\s*<td class="DRC_summary_header_col2"></td>\s*'
                      r'<td class="DRC_summary_header_col3"[^>]*>(\d+)', text)
    if not total or not summary or int(total[1]) != len(details) or sum(n for _, n in summary) != len(details):
        raise ValueError('Incomplete or internally inconsistent native DRC report: ' + str(path))
    return {'total': int(total[1]), 'summary': summary, 'details': details}


def main():
    args = argparse.Namespace(before=EV / 'GEOMETRY_C2_6L_BC.txt', after=EV / 'GEOMETRY_C2_6L_BD.txt',
                              adds=EV / 'ASTRA_VC1_READY_ADDS.csv', dels=EV / 'ASTRA_VC1_READY_DELS.csv',
                              tol_mm=.00015, allow_move=[])
    additions, deletions = delta.plan(args.adds, True), delta.plan(args.dels, False)
    points = [(15.9, 11.2), (16.175, 10.925), (20.675, 10.925), (21.675, 11.925),
              (22.55, 11.925), (24.725, 14.1), (24.725, 18.775), (24.175, 19.325)]
    expected = [('TRACK', 'Vc_1', 'Mid Layer 4', (*a, *b, .2)) for a, b in zip(points, points[1:])]
    actual = [(r['kind'], r['net'], r['layer'], r['values']) for r in additions]
    planned_scope = actual == expected and not deletions
    geometry = delta.verify(args)
    before = drc(EV / 'DRC_C2_6L_BC.txt.html')
    after = drc(EV / 'DRC_C2_6L_BD.txt.html')
    old_opens = Counter(row for row in before['details'] if row.startswith('Un-Routed Net Constraint:'))
    new_opens = Counter(row for row in after['details'] if row.startswith('Un-Routed Net Constraint:'))
    vc1 = Counter({row: count for row, count in old_opens.items()
                   if row.startswith('Un-Routed Net Constraint: Net Vc_1 Between ')})
    expected_opens = old_opens - vc1
    only_vc1_resolved = sum(vc1.values()) == 1 and new_opens == expected_opens
    critical = ('Clearance Constraint', 'Short-Circuit Constraint', 'Width Constraint',
                'Component Clearance Constraint', 'Routing Layers Constraint')
    critical_violations = [(name, count) for name, count in after['summary']
                           if name.startswith(critical) and count]
    streams = structure.compare(structure.snapshot(EV / 'ASTRA_BD_BEFORE_20260927/EMG_MainBoard_Layout.PcbDoc'),
                                structure.snapshot(PCB))
    protected_scope = all(streams['separate_invariants'].values())
    documents = []
    manifest = EV / 'ASTRA_BD_BEFORE_20260927/BEFORE_HASHES.json'
    for record in json.loads(manifest.read_text(encoding='utf-8-sig')):
        source = Path(record['Path'])
        if source.suffix.lower() not in ('.schdoc', '.prjpcb'):
            continue
        current = PCB.parent / source.name
        expected_hash = record['Hash'].lower()
        actual_hash = hashlib.sha256(current.read_bytes()).hexdigest()
        documents.append({'path': str(current), 'before_sha256': expected_hash,
                          'after_sha256': actual_hash, 'unchanged': expected_hash == actual_hash})
    documents_passed = len(documents) == 9 and all(row['unchanged'] for row in documents)
    artifacts = [args.before, args.after, args.adds, args.dels,
                 EV / 'DRC_C2_6L_BC.txt.html', EV / 'DRC_C2_6L_BD.txt.html']
    report = {
        'passed': planned_scope and geometry['passed'] and only_vc1_resolved and not critical_violations
                  and protected_scope and documents_passed,
        'authorized_csv_matches_exact_seven_segment_path': planned_scope,
        'native_geometry_delta': geometry,
        'native_drc': {'before_total': before['total'], 'after_total': after['total'],
                       'before_open_count': sum(old_opens.values()), 'after_open_count': sum(new_opens.values()),
                       'only_vc1_resolved_and_all_other_opens_identical': only_vc1_resolved,
                       'removed_open_details': list((old_opens - new_opens).elements()),
                       'added_open_details': list((new_opens - old_opens).elements()),
                       'remaining_open_details': list(new_opens.elements()),
                       'critical_nonzero_summary_rows': critical_violations,
                       'removed_all_violation_details': list((Counter(before['details']) - Counter(after['details'])).elements()),
                       'added_all_violation_details': list((Counter(after['details']) - Counter(before['details'])).elements())},
        'saved_structure': streams,
        'schematics_and_project': {'passed': documents_passed, 'manifest': str(manifest), 'files': documents},
        'inputs': [{'path': str(p.resolve()), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in artifacts],
        'limitations': ['Raw opaque protected-stream differences remain reported even when separate invariants pass.',
                        'DRC comparison establishes the change in reported opens and checked violations; it is not a full fabrication release.',
                        'No native rule, component, pad or copper edit was performed by this reviewer.']}
    out = EV / 'ASTRA_BD_INDEPENDENT_REVIEW.json'
    out.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'passed': report['passed'], 'plan_scope': planned_scope,
                      'geometry_passed': geometry['passed'], 'drc': report['native_drc'],
                      'structure_invariants': streams['separate_invariants'], 'raw_structure_errors': streams['errors'],
                      'schematics_and_project_unchanged': documents_passed,
                      'evidence': str(out)}, indent=2))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
