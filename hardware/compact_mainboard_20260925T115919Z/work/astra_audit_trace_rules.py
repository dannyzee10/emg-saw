"""Read-only audit of every exported free copper track and via against saved rules.

Only All, InNet('name') and InNetClass('name') scopes are evaluated. Unsupported
scopes, ambiguous priorities or absent constraints produce unresolved results.
No CAD/router/geometry engine is launched. This does not replace native DRC.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import io
import json
import math
from pathlib import Path
import re
import struct

import olefile
from astra_read_drc_coverage import rules
from astra_verify_routing_delta import geometry


def text_records(data):
    records, position = [], 0
    while position < len(data):
        if position + 4 > len(data):
            raise ValueError('Truncated Classes6 record prefix')
        length = struct.unpack_from('<I', data, position)[0]
        position += 4
        if not length or position + length > len(data):
            raise ValueError('Unsupported Classes6 record framing')
        raw = data[position:position + length].rstrip(b'\0')
        position += length
        if not raw.startswith(b'|') or b'\0' in raw:
            raise ValueError('Unsupported Classes6 text record')
        fields = [field.split('=', 1) for field in raw.decode('latin1').split('|')[1:] if field]
        if any(len(field) != 2 for field in fields) or len({f[0] for f in fields}) != len(fields):
            raise ValueError('Malformed/duplicate class fields')
        records.append(dict(fields))
    return records


def net_classes(records):
    result = {}
    for record in records:
        if record.get('KIND') != '0':
            continue
        name = record['NAME']
        members = None if record.get('SUPERCLASS', '').upper() != 'FALSE' else {
            value for key, value in record.items() if re.fullmatch(r'M\d+', key)}
        # The saved board has duplicate classes with identical membership. That
        # yields the same predicate under either identity; unequal copies remain
        # unresolved, rather than guessing a merge/first-match interpretation.
        if name in result and result[name] != members:
            result[name] = None
        elif name not in result:
            result[name] = members
    return result


def scope_matches(expression, net, classes):
    expression = expression.strip()
    if expression.lower() == 'all':
        return True
    match = re.fullmatch(r"(InNet|InNetClass)\('([^']*)'\)", expression, re.I)
    if not match:
        raise ValueError('Unsupported scope: ' + expression)
    if match[1].lower() == 'innet':
        return net == match[2]
    if match[2] not in classes or classes[match[2]] is None:
        raise ValueError('Missing or unsupported native net class: ' + match[2])
    return net in classes[match[2]]


def choose_rule(native_rules, kind, net, classes):
    priorities = defaultdict(list)
    for rule in native_rules:
        if rule['kind_id'] == kind and rule.get('ENABLED', '').upper() == 'TRUE':
            priorities[int(rule['PRIORITY'])].append(rule)
    for priority in sorted(priorities):
        matches = []
        for rule in priorities[priority]:
            try:
                if not scope_matches(rule['SCOPE1EXPRESSION'], net, classes):
                    continue
                if rule.get('SCOPE2EXPRESSION', '').lower() != 'all':
                    raise ValueError('Unsupported secondary scope')
            except ValueError as exc:
                raise ValueError(rule['NAME'] + ': ' + str(exc)) from exc
            matches.append(rule)
        if len(matches) > 1:
            raise ValueError('Ambiguous matching rule priority ' + str(priority))
        if matches:
            return matches[0]
    raise ValueError('No matching enabled rule')


def mm(value):
    match = re.fullmatch(r'([+-]?(?:\d+(?:\.\d*)?|\.\d+))(mil|mm)', value, re.I)
    if not match:
        raise ValueError('Unsupported native dimension: ' + value)
    return float(match[1]) * (0.0254 if match[2].lower() == 'mil' else 1.0)


def width_limits(rule, layer):
    prefix = layer.replace(' ', '').upper()
    low_key, high_key = prefix + '_MINWIDTH', prefix + '_MAXWIDTH'
    if low_key in rule or high_key in rule:
        if low_key not in rule or high_key not in rule:
            raise ValueError('Incomplete layer width limits')
    else:
        low_key, high_key = 'MINLIMIT', 'MAXLIMIT'
    low, high = mm(rule[low_key]), mm(rule[high_key])
    if low <= 0 or high < low:
        raise ValueError('Invalid width limits')
    return low, high, [low_key, high_key]


def audit(items, native_rules, classes, tolerance):
    results, uses = [], Counter()
    for index, item in enumerate(items):
        checks = ((2, 'width'), (9, 'routing_layer')) if item['kind'] == 'TRACK' else ((11, 'via_envelope'),)
        for kind, check in checks:
            row = {'primitive_index': index, 'check': check, 'net': item['net'], 'layer': item['layer'],
                   'native_record': item['source']}
            try:
                rule = choose_rule(native_rules, kind, item['net'], classes)
                row['rule'] = rule['NAME']
                uses[(check, rule['NAME'])] += 1
                if check == 'width':
                    low, high, keys = width_limits(rule, item['layer'])
                    value = item['values'][4]
                    passed = low - tolerance <= value <= high + tolerance
                    row.update(actual_mm=value, minimum_mm=low, maximum_mm=high, constraint_fields=keys)
                elif check == 'routing_layer':
                    field = item['layer'].upper() + '_V5'
                    allowed = rule[field].upper()
                    if allowed not in ('TRUE', 'FALSE'):
                        raise ValueError('Unsupported routing-layer flag')
                    passed = allowed == 'TRUE'
                    row.update(allowed=passed, constraint_field=field)
                else:
                    if rule.get('VIASTYLE') != 'Through Hole':
                        raise ValueError('Unsupported via rule style')
                    diameter, hole = item['values'][2:4]
                    limits = [mm(rule[key]) for key in ('MINWIDTH', 'MAXWIDTH', 'MINHOLEWIDTH', 'MAXHOLEWIDTH')]
                    if limits[0] <= 0 or limits[2] <= 0 or limits[1] < limits[0] or limits[3] < limits[2]:
                        raise ValueError('Invalid via limits')
                    passed = limits[0] - tolerance <= diameter <= limits[1] + tolerance and limits[2] - tolerance <= hole <= limits[3] + tolerance
                    row.update(actual_diameter_hole_mm=[diameter, hole], diameter_limits_mm=limits[:2], hole_limits_mm=limits[2:])
                row['status'] = 'passed' if passed else 'failed'
            except (ValueError, KeyError, TypeError) as exc:
                row.update(status='unresolved', reason=str(exc))
            results.append(row)
    return results, [{'check': check, 'rule': rule, 'count': count} for (check, rule), count in sorted(uses.items())]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pcb', type=Path, required=True)
    parser.add_argument('--geometry', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--tol-mm', type=float, default=0.00015)
    args = parser.parse_args()
    if not math.isfinite(args.tol_mm) or args.tol_mm <= 0:
        parser.error('Tolerance must be positive and finite')
    if args.output.suffix.lower() != '.json' or args.output.resolve() in (args.pcb.resolve(), args.geometry.resolve()):
        parser.error('Output must be a separate JSON file')
    data = args.pcb.read_bytes()
    with olefile.OleFileIO(io.BytesIO(data)) as document:
        rule_data = document.openstream('Rules6/Data').read()
        class_data = document.openstream('Classes6/Data').read()
    native_rules = rules(rule_data)
    class_records = text_records(class_data)
    classes = net_classes(class_records)
    class_counts = Counter(record['NAME'] for record in class_records if record.get('KIND') == '0')
    exported = geometry(args.geometry)
    is_copper = lambda layer: bool(re.fullmatch(r'Top Layer|Bottom Layer|Mid Layer [1-9]\d*', layer))
    items = [item for item in exported['free'] if item['kind'] == 'VIA' or is_copper(item['layer'])]
    non_copper_tracks = [item for item in exported['free'] if item['kind'] == 'TRACK' and not is_copper(item['layer'])]
    unresolved_arcs = [row for row in exported['fixed'].elements() if row.startswith('ARC|')
                       and is_copper(row.split('|')[1]) and '|INCOMP=False|' in row and '|INPOLY=False|' in row]
    checks, uses = audit(items, native_rules, classes, args.tol_mm)
    status_counts = Counter(row['status'] for row in checks)
    report = {
        'passed': not (status_counts['failed'] or status_counts['unresolved'] or unresolved_arcs),
        'inputs': {'pcb': str(args.pcb.resolve()), 'geometry': str(args.geometry.resolve()),
                   'pcb_sha256': hashlib.sha256(data).hexdigest(), 'geometry_sha256': hashlib.sha256(args.geometry.read_bytes()).hexdigest(),
                   'rules_sha256': hashlib.sha256(rule_data).hexdigest(), 'classes_sha256': hashlib.sha256(class_data).hexdigest()},
        'primitive_counts': dict(Counter(item['kind'] for item in items)),
        'netless_copper_track_count': sum(item['kind'] == 'TRACK' and item['net'] in ('', '-') for item in items),
        'excluded_non_copper_free_tracks': {'count': len(non_copper_tracks),
                                          'layers': dict(Counter(item['layer'] for item in non_copper_tracks)),
                                          'native_records': [item['source'] for item in non_copper_tracks]},
        'check_counts': dict(status_counts), 'rule_usage': uses,
        'failures': [row for row in checks if row['status'] == 'failed'],
        'unresolved': [row for row in checks if row['status'] == 'unresolved'],
        'unresolved_free_copper_arcs': unresolved_arcs,
        'net_classes': {name: sorted(members) if members is not None else None for name, members in classes.items()},
        'duplicate_net_class_records': {name: {'count': count, 'identical_membership': classes[name] is not None}
                                        for name, count in class_counts.items() if count > 1},
        'tolerance_mm': args.tol_mm,
        'limitations': [
            'Caller must pair a saved native PCB and its matching complete native geometry export.',
            'Checks every exported free copper TRACK and VIA, independently of routing-plan provenance.',
            'Footprint tracks, polygon-generated copper, pads, regions and fills are outside this free-trace audit.',
            'Free copper ARC exports omit width/path data and make this audit unresolved if present.',
            'Only saved unary All/InNet/InNetClass scopes and explicit width/layer/via-envelope fields are evaluated.',
            'Unsupported higher-priority scopes are unresolved; no lower-priority fallback is guessed.',
            'Via layer spans, internal padstacks, clearances, connectivity, impedance and current capacity are not verified here.',
            'Native DRC with proven batch coverage remains required.'
        ],
    }
    args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: report[key] for key in ('passed', 'primitive_counts', 'check_counts', 'rule_usage')}, indent=2))
    print('Unresolved free copper arcs:', len(unresolved_arcs))
    return 0 if report['passed'] else 2 if status_counts['unresolved'] or unresolved_arcs else 1


if __name__ == '__main__':
    raise SystemExit(main())
