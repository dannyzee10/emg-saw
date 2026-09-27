"""Read-only verification of a routing CSV delta against native geometry exports.

Example: python astra_verify_routing_delta.py --before AZ.txt --after BA.txt
    --adds MERGE_I_ADDS_OK.csv --dels MERGE_I_DELS_OK.csv --output delta.json
For an authorized translation, also pass --allow-move CL_4:-3.1:0.
For one named free pad, pass --allow-free-pad-move TP_GND_DIG:0.2:0.

No CAD files are written. Only the requested JSON evidence file is written.
This export cannot attest net objects, rules, stackup, or via layer spans; freeze
those separately using native inventory or the saved board's binary streams.
"""
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import sys


def read_text(path):
    data = Path(path).read_bytes()
    if data.startswith((b'\xff\xfe', b'\xfe\xff')):
        return data.decode('utf-16')
    try:
        return data.decode('utf-8-sig')
    except UnicodeDecodeError:
        return data.decode('cp1252')


def number(value):
    result = float(value)
    if not math.isfinite(result):
        raise ValueError('Non-finite geometry value: ' + str(value))
    return result


def primitive(kind, net, layer, values, source):
    return {'kind': kind, 'net': net, 'layer': layer,
            'values': tuple(number(v) for v in values), 'source': source}


def geometry(path):
    lines = [line.strip() for line in read_text(path).splitlines() if line.strip()]
    if not lines or lines[-1] != 'READ_ONLY; COMPLETE':
        raise ValueError('Incomplete native geometry export: ' + str(path))
    free, fixed, pads, comps = [], Counter(), Counter(), Counter()
    polygon_count = 0
    for line in lines:
        fields = line.split('|')
        kind = fields[0]
        if kind in ('ENTER', 'READ_ONLY; COMPLETE'):
            continue
        flags = {f.split('=', 1)[0]: f.split('=', 1)[1].lower()
                 for f in fields if '=' in f}
        if flags.get('INPOLY') == 'true':
            polygon_count += 1
            continue
        if kind == 'PAD':
            pads[line] += 1
        elif kind == 'COMP':
            comps[line] += 1
        elif kind == 'VIA':
            if len(fields) != 6:
                raise ValueError('Unexpected via export record: ' + line)
            free.append(primitive(kind, fields[1], '', fields[2:6], line))
        elif kind == 'TRACK' and flags.get('INCOMP') == 'false' and flags.get('KEEPOUT') == 'false':
            free.append(primitive(kind, fields[2], fields[1], fields[3:8], line))
        else:
            # Includes footprint copper, keepouts, nonpolygon arcs/regions/fills,
            # and any future export record whose changes are not authorized.
            fixed[line] += 1
    if not pads or not comps:
        raise ValueError('Export is missing pads or components: ' + str(path))
    return {'free': free, 'fixed': fixed, 'pads': pads, 'comps': comps,
            'polygon_records': polygon_count}


def plan(path, addition):
    result = []
    for rownum, row in enumerate(csv.DictReader(io.StringIO(read_text(path))), 2):
        kind = row['kind']
        if kind not in ('TRACK', 'VIA'):
            raise ValueError(f'{path}:{rownum}: unsupported kind {kind}')
        names = ('x1', 'y1', 'x2', 'y2', 'w') if kind == 'TRACK' else ('x1', 'y1', 'd', 'h')
        required = names if addition else names[:4] if kind == 'TRACK' else names[:2]
        for name in required:
            if row.get(name, '') == '':
                raise ValueError(f'{path}:{rownum}: missing {name}')
        values = tuple(number(row[n]) if row.get(n, '') != '' else None for n in names)
        if any(v is not None and v <= 0 for v in values[4:] if kind == 'TRACK'):
            raise ValueError(f'{path}:{rownum}: nonpositive track width')
        if kind == 'VIA' and any(v is not None and v <= 0 for v in values[2:]):
            raise ValueError(f'{path}:{rownum}: nonpositive via diameter/hole')
        result.append({'kind': kind, 'net': row['net'],
                       'layer': row['layer'] if kind == 'TRACK' else '',
                       'values': values, 'source': f'{path}:{rownum}',
                       'group': row.get('group', '')})
    return result


def key(item):
    return item['kind'], item['net'], item['layer']


def match_error(a, b, tolerance):
    if key(a) != key(b):
        return None
    variants = [b['values']]
    if a['kind'] == 'TRACK':
        x1, y1, x2, y2, width = b['values']
        variants.append((x2, y2, x1, y1, width))
    best = None
    for values in variants:
        diffs = [abs(av - bv) for av, bv in zip(a['values'], values) if av is not None]
        if diffs and max(diffs) <= tolerance:
            error = sum(diffs)
            if best is None or error < best:
                best = error
    return best


def counter_difference(before, after):
    return {'removed': list((before - after).elements()),
            'added': list((after - before).elements())}


def counts(items):
    return dict(sorted(Counter(i['kind'] for i in items).items()))


def translation_spec(value):
    """Parse an explicit component translation, never a rotation or side swap."""
    try:
        ref, dx, dy = value.split(':')
        if not ref.strip() or ref != ref.strip() or '|' in ref:
            raise ValueError('invalid component reference')
        dx, dy = number(dx), number(dy)
        if dx == 0 and dy == 0:
            raise ValueError('translation must be nonzero')
        return ref, dx, dy
    except ValueError as exc:
        raise argparse.ArgumentTypeError('expected REF:DX_MM:DY_MM: ' + str(exc)) from exc


def translation_matches(before, after, kind, dx, dy, tolerance):
    """Compare original native rows directly; all non-coordinate fields stay exact."""
    old, new = before.split('|'), after.split('|')
    if len(old) != len(new):
        return False
    if kind == 'PAD':
        offsets = {5: dx, 6: dy, 7: dx, 8: dy, 9: dx, 10: dy}
        minimum_fields = 16
    else:
        offsets = {3: dx, 4: dy, 6: dx, 7: dy, 8: dx, 9: dy}
        minimum_fields = 10
    if len(old) < minimum_fields or old[0] != kind or new[0] != kind:
        return False
    for index, (a, b) in enumerate(zip(old, new)):
        if index in offsets:
            if abs(number(a) + offsets[index] - number(b)) > tolerance:
                return False
        elif a != b:
            return False
    return True


def check_translations(before, after, specifications, tolerance):
    moves = {}
    for ref, dx, dy in specifications:
        if ref in moves:
            raise ValueError('Duplicate --allow-move for ' + ref)
        moves[ref] = (dx, dy)
    results = {}
    for ref, (dx, dy) in moves.items():
        result = {'translation_mm': [dx, dy], 'passed': True, 'records': {}}
        for label, kind in (('comps', 'COMP'), ('pads', 'PAD')):
            old = [row for row in before[label].elements() if row.split('|')[1] == ref]
            actual = [row for row in after[label].elements() if row.split('|')[1] == ref]
            remaining = list(actual)
            missing = []
            for row in old:
                match = next((i for i, candidate in enumerate(remaining)
                              if translation_matches(row, candidate, kind, dx, dy, tolerance)), None)
                if match is None:
                    missing.append(row)
                else:
                    remaining.pop(match)
            count_ok = len(old) == len(actual) and (len(old) == 1 if kind == 'COMP' else bool(old))
            passed = count_ok and not missing and not remaining
            result['records'][label] = {
                'passed': passed, 'before_count': len(old), 'after_count': len(actual),
                'before_native_records': old, 'after_native_records': actual,
                'missing_translation_matches': missing, 'unexpected_after_records': remaining}
            result['passed'] = result['passed'] and passed
        results[ref] = result
    return moves, results


def check_free_pad_translations(before, after, specifications, tolerance):
    """Check exactly one FREE pad with this name in each native export."""
    moves, results = {}, {}
    for name, dx, dy in specifications:
        if name in moves:
            raise ValueError('Duplicate --allow-free-pad-move for ' + name)
        moves[name] = (dx, dy)
        old = [row for row in before['pads'].elements() if row.split('|')[1:3] == ['FREE', name]]
        actual = [row for row in after['pads'].elements() if row.split('|')[1:3] == ['FREE', name]]
        unique = len(old) == len(actual) == 1
        passed = unique and translation_matches(old[0], actual[0], 'PAD', dx, dy, tolerance)
        results[name] = {
            'translation_mm': [dx, dy], 'passed': passed, 'unique_free_pad': unique,
            'before_count': len(old), 'after_count': len(actual),
            'before_native_records': old, 'after_native_records': actual}
    return moves, results


def verify(args):
    before, after = geometry(args.before), geometry(args.after)
    adds, dels = plan(args.adds, True), plan(args.dels, False)
    moves, translations = check_translations(before, after, getattr(args, 'allow_move', []), args.tol_mm)
    free_pad_moves, free_pad_translations = check_free_pad_translations(
        before, after, getattr(args, 'allow_free_pad_move', []), args.tol_mm)
    errors = []
    unchanged = {}
    raw_native_changes = {}
    for label in ('pads', 'comps', 'fixed'):
        original_before, original_after = before[label], after[label]
        raw_native_changes[label] = counter_difference(original_before, original_after)
        # Exclude only rows whose explicit ref is independently validated above.
        # No rewritten geometry export or projected rows are presented as native.
        if label in ('pads', 'comps'):
            def separately_checked(row):
                fields = row.split('|')
                return fields[1] in moves or (label == 'pads' and fields[1] == 'FREE'
                                             and fields[2] in free_pad_moves)
            checked_before = Counter({row: count for row, count in original_before.items()
                                      if not separately_checked(row)})
            checked_after = Counter({row: count for row, count in original_after.items()
                                     if not separately_checked(row)})
        else:
            checked_before, checked_after = original_before, original_after
        diff = counter_difference(checked_before, checked_after)
        unchanged[label] = {'passed': not any(diff.values()),
                            'comparison_scope': 'all records except separately checked allowed translations'
                            if (moves and label != 'fixed') or (free_pad_moves and label == 'pads') else 'all records',
                            'before_count': sum(checked_before.values()),
                            'after_count': sum(checked_after.values()), **diff}
        if not unchanged[label]['passed']:
            errors.append(label + ' changed')
    for ref, result in translations.items():
        if not result['passed']:
            errors.append('Authorized translation does not match native pad/component records: ' + ref)
    for name, result in free_pad_translations.items():
        if not result['passed']:
            errors.append('Authorized free-pad translation does not match one unique native FREE pad: ' + name)

    expected = list(before['free'])
    deleted = []
    for item in dels:
        matches = [i for i, old in enumerate(expected)
                   if match_error(item, old, args.tol_mm) is not None]
        if len(matches) != 1:
            errors.append(f"Deletion {item['source']} has {len(matches)} exact identity/dimension matches")
        else:
            deleted.append(expected.pop(matches[0]))
    expected.extend(adds)

    # Match each expected primitive to one actual primitive. Same-net touching
    # tracks are still distinct records; extra duplicates therefore fail.
    actual_groups = defaultdict(dict)
    for index, item in enumerate(after['free']):
        actual_groups[key(item)][index] = item
    missing = []
    for item in expected:
        candidates = actual_groups[key(item)]
        best = None
        for index, actual in candidates.items():
            error = match_error(item, actual, args.tol_mm)
            if error is not None and (best is None or error < best[0]):
                best = error, index
                if error == 0:
                    break
        if best is None:
            missing.append(item)
        else:
            del candidates[best[1]]
    unexpected = [item for group in actual_groups.values() for item in group.values()]
    if missing:
        errors.append(f'{len(missing)} expected free copper primitives missing')
    if unexpected:
        errors.append(f'{len(unexpected)} unexpected free copper primitives present')
    return {
        'passed': not errors, 'errors': errors, 'tolerance_mm': args.tol_mm,
        'counts': {'before': counts(before['free']), 'after': counts(after['free']),
                   'expected_after': counts(expected), 'planned_adds': counts(adds),
                   'planned_deletes': counts(dels), 'matched_deletes': counts(deleted)},
        'unchanged': unchanged, 'missing': missing, 'unexpected': unexpected,
        'allowed_component_translations': translations,
        'allowed_free_pad_translations': free_pad_translations,
        'raw_native_record_changes': raw_native_changes,
        'deletion_checks': {'width_and_hole_checked_when_provided': True,
                            'ambiguous_matches_allowed': False},
        'ignored_polygon_records': {'before': before['polygon_records'],
                                    'after': after['polygon_records']},
        'limitations': [
            'Native exports omit net objects, rules, layer stack and via spans; verify separately.',
            'Only the pad/primitive fields present in the native export are compared.',
            'Allowed moves translate centers and bounding boxes only; all exported net, layer, rotation, size and other fields stay exact.',
            'Polygon-generated primitives may change after repour.',
            'This verifies the requested copper delta, not electrical completion or DRC.'
        ]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('before', 'after', 'adds', 'dels', 'output'):
        parser.add_argument('--' + name, required=True, type=Path)
    parser.add_argument('--tol-mm', type=float, default=0.00015,
                        help='Maximum coordinate/dimension difference (default 0.00015 mm)')
    parser.add_argument('--allow-move', action='append', type=translation_spec, default=[],
                        metavar='REF:DX_MM:DY_MM',
                        help='Allow exactly this translation of one component and all its pads; repeat for separate components')
    parser.add_argument('--allow-free-pad-move', action='append', type=translation_spec, default=[],
                        metavar='NAME:DX_MM:DY_MM',
                        help='Allow exactly this translation of one uniquely named FREE pad; all other pads stay protected')
    args = parser.parse_args()
    if not math.isfinite(args.tol_mm) or args.tol_mm <= 0:
        parser.error('--tol-mm must be positive and finite')
    # The output must never overwrite a supplied input or any CAD artifact.
    inputs = (args.before, args.after, args.adds, args.dels)
    if args.output.resolve() in {p.resolve() for p in inputs} or args.output.suffix.lower() != '.json':
        parser.error('--output must be a separate .json file')
    try:
        result = verify(args)
    except (ValueError, KeyError, IndexError, OSError, csv.Error) as exc:
        result = {'passed': False, 'errors': [str(exc)]}
    result['inputs'] = {}
    for path in inputs:
        entry = {'path': str(path.resolve())}
        if path.is_file():
            entry['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        result['inputs'][str(path)] = entry
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'passed': result['passed'], 'errors': result['errors'],
                      'evidence': str(args.output.resolve()), 'counts': result.get('counts')}, indent=2))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
