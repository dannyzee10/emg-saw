"""Read-only saved-board verification of the authorized BH-to-BI rule edit.

Allows exactly VIA_STD_060_030 minima 0.60/0.30 -> 0.45/0.20 mm and batch
category additions 9 and 11. All other design streams must remain identical.
Explicit save/view metadata and cached DRC changes are reported separately.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import struct

from astra_audit_trace_rules import mm
from astra_verify_pcb_structure import (
    SAVE_METADATA, board_group, board_parameters, sha, snapshot)


def text_records(data, rule=False):
    records, position = [], 0
    size = 6 if rule else 4
    while position < len(data):
        if position + size > len(data):
            raise ValueError('Truncated text record prefix')
        if rule:
            kind, length = struct.unpack_from('<HI', data, position)
        else:
            kind, length = None, struct.unpack_from('<I', data, position)[0]
        position += size
        if not length or position + length > len(data):
            raise ValueError('Invalid text record length')
        raw = data[position:position + length]
        position += length
        text = raw.rstrip(b'\0')
        if not text.startswith(b'|') or b'\0' in text:
            raise ValueError('Unsupported text record')
        parts = [part.split('=', 1) for part in text.decode('latin1').split('|')[1:] if part]
        if any(len(part) != 2 for part in parts) or len({p[0] for p in parts}) != len(parts):
            raise ValueError('Malformed or duplicate text fields')
        records.append((kind, dict(parts), raw))
    return records


def masked(raw, fields):
    for field in fields:
        pattern = rb'(?<=\|)' + re.escape(field.encode('ascii')) + rb'=[^|\x00]*'
        raw, count = re.subn(pattern, field.encode('ascii') + b'=<AUTHORIZED>', raw)
        if count != 1:
            raise ValueError('Expected one field: ' + field)
    return raw


def verify_rules(before, after):
    old, new = text_records(before, True), text_records(after, True)
    if len(old) != len(new):
        raise ValueError('Rule record count changed')
    targets = [[i for i, row in enumerate(records) if row[1].get('NAME') == 'VIA_STD_060_030']
               for records in (old, new)]
    if len(targets[0]) != 1 or targets[0] != targets[1]:
        raise ValueError('Expected one unchanged-position VIA_STD_060_030 rule')
    allowed = {'MINWIDTH': (.60, .45), 'MINHOLEWIDTH': (.30, .20)}
    changes = []
    for index, (a, b) in enumerate(zip(old, new)):
        if index != targets[0][0]:
            if a != b:
                raise ValueError('Other rule record changed: ' + a[1].get('NAME', str(index)))
            continue
        if a[0] != 11 or b[0] != 11:
            raise ValueError('Target rule kind is not RoutingViaStyle')
        for key, (expected_old, expected_new) in allowed.items():
            if abs(mm(a[1][key]) - expected_old) > .00001 or abs(mm(b[1][key]) - expected_new) > .00001:
                raise ValueError('Unexpected target rule limit: ' + key)
            changes.append(dict(rule='VIA_STD_060_030', field=key, before=a[1][key], after=b[1][key]))
        if masked(a[2], allowed) != masked(b[2], allowed):
            raise ValueError('Target rule changed beyond the two authorized minima')
    return dict(passed=True, record_count=len(old), changes=changes,
                all_other_rule_bytes_preserved=True)


def selection(value):
    if not re.fullmatch(r'\d+(?:,\d+)*,?', value):
        raise ValueError('Unexpected batch selection syntax')
    values = [int(x) for x in value.split(',') if x]
    if len(values) != len(set(values)):
        raise ValueError('Duplicate batch category')
    return set(values)


def verify_options(before, after):
    old, new = text_records(before), text_records(after)
    if len(old) != len(new):
        raise ValueError('DRC option record count changed')
    targets = [[i for i, row in enumerate(records) if 'RULESETTOCHECK' in row[1]] for records in (old, new)]
    if len(targets[0]) != 1 or targets[0] != targets[1]:
        raise ValueError('Expected one unchanged-position batch selection field')
    for index, (a, b) in enumerate(zip(old, new)):
        if index != targets[0][0]:
            if a != b:
                raise ValueError('Other DRC option record changed')
            continue
        av, bv = selection(a[1]['RULESETTOCHECK']), selection(b[1]['RULESETTOCHECK'])
        if bv - av != {9, 11} or av - bv:
            raise ValueError('Batch selection did not add exactly 9 and 11')
        if masked(a[2], ['RULESETTOCHECK']) != masked(b[2], ['RULESETTOCHECK']):
            raise ValueError('DRC options changed beyond batch selection')
    return dict(passed=True, added=[9, 11], removed=[], all_other_option_bytes_preserved=True)


def byte_diagnostic(before, after):
    result = dict(before_size=len(before), after_size=len(after), same_length=len(before) == len(after))
    if len(before) == len(after):
        offsets = [i for i, (a, b) in enumerate(zip(before, after)) if a != b]
        transitions = Counter(f'{before[i]:02x}->{after[i]:02x}' for i in offsets)
        result.update(changed_byte_count=len(offsets),
                      distinct_byte_transition_count=len(transitions),
                      most_common_byte_transitions=dict(transitions.most_common(16)),
                      first_changed_offsets=offsets[:24],
                      first_contexts=[dict(offset=i, before=before[max(0, i-5):i+6].hex(),
                                           after=after[max(0, i-5):i+6].hex()) for i in offsets[:6]])
    result['note'] = 'Diagnostic only; unknown binary differences remain failures.'
    return result


def framed_binary_records(data, header):
    """Diagnostic only: accept observed tag/u32-length framing iff header agrees."""
    if len(header) != 4:
        raise ValueError('Unfamiliar binary header')
    expected = struct.unpack('<I', header)[0]
    records, position, tags = [], 0, set()
    while position < len(data):
        if position + 5 > len(data):
            raise ValueError('Incomplete binary record prefix')
        tag, size = struct.unpack_from('<BI', data, position)
        end = position + 5 + size
        if not size or end > len(data):
            raise ValueError('Unfamiliar binary record framing')
        records.append(data[position:end])
        tags.add(tag)
        position = end
    if len(records) != expected or len(tags) != 1:
        raise ValueError('Binary record framing does not agree with native header')
    return records


def compare(before, after):
    old, new = before['streams'], after['streams']
    errors, changes, metadata = [], [], []
    checks = {}
    special = {'Rules6/Data': verify_rules, 'Design Rule Checker Options6/Data': verify_options}
    for name, check in special.items():
        try:
            checks[name] = check(old[name], new[name])
        except (ValueError, KeyError) as exc:
            errors.append(name + ': ' + str(exc))
            checks[name] = dict(passed=False, error=str(exc))
    required = {'Board6/Data', 'Rules6/Header', 'Design Rule Checker Options6/Header',
                'Pads6/Data', 'Components6/Data', 'Nets6/Data', 'Classes6/Data', 'Tracks6/Data', 'Vias6/Data'}
    for name in sorted(required):
        if name not in old or name not in new:
            errors.append('Required stream missing: ' + name)
    same = 0
    for name in sorted(set(old) | set(new)):
        a, b = old.get(name), new.get(name)
        if a == b:
            same += 1
            continue
        row = dict(stream=name, before_sha256=sha(a) if a is not None else None,
                   after_sha256=sha(b) if b is not None else None)
        if name in special:
            row['classification'] = 'authorized_change_verified' if checks[name]['passed'] else 'unexpected'
        elif name == 'Board6/Data' and a is not None and b is not None:
            try:
                pa, na = board_parameters(a)
                pb, nb = board_parameters(b)
                if na != nb:
                    errors.append('Board6 record count changed')
                row['parameters'] = [dict(key=k, before=pa.get(k), after=pb.get(k), group=board_group(k))
                                     for k in sorted(set(pa) | set(pb)) if pa.get(k) != pb.get(k)]
                bad = [p for p in row['parameters'] if p['group'] != 'save_or_view_metadata']
                if bad:
                    errors.append('Protected Board6 parameters changed: ' + ', '.join(p['key'] for p in bad))
                row['classification'] = 'unexpected' if bad else 'save_or_view_metadata'
                metadata.extend(row['parameters'])
            except ValueError as exc:
                errors.append('Board6: ' + str(exc))
                row['classification'] = 'unexpected'
        elif name.split('/')[0] in SAVE_METADATA:
            row['classification'] = 'save_metadata'
        elif name.split('/')[0].startswith('T') and name.split('/')[0].endswith('Violation'):
            row['classification'] = 'cached_drc_results'
        else:
            row['classification'] = 'unexpected'
            errors.append('Other saved stream changed: ' + name)
            if a is not None and b is not None:
                row['byte_diagnostic'] = byte_diagnostic(a, b)
                header = name.rsplit('/', 1)[0] + '/Header'
                try:
                    aa = framed_binary_records(a, old[header])
                    bb = framed_binary_records(b, new[header])
                    row['binary_record_diagnostic'] = dict(
                        before_count=len(aa), after_count=len(bb),
                        entire_record_multisets_identical=Counter(aa) == Counter(bb),
                        unchanged_entire_records=sum((Counter(aa) & Counter(bb)).values()),
                        note='Observed tag/length framing exactly exhausts Data and agrees with Header; no binary field semantics inferred.')
                except (KeyError, ValueError) as exc:
                    row['binary_record_diagnostic'] = dict(unresolved=str(exc))
        changes.append(row)
    return dict(passed=not errors, errors=errors, checks=checks,
                before={k: v for k, v in before.items() if k != 'streams'},
                after={k: v for k, v in after.items() if k != 'streams'},
                identical_stream_count=same, changed_streams=changes,
                reported_board_save_view_changes=metadata,
                limitations=['OLE allocation/directory timestamps are container metadata and are not compared.',
                             'Listed save/view metadata and cached DRC result streams may change; every other stream is exact.'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('before', 'after', 'output'):
        parser.add_argument('--' + name, required=True, type=Path)
    args = parser.parse_args()
    if args.output.suffix.lower() != '.json' or args.output.resolve() in (args.before.resolve(), args.after.resolve()):
        parser.error('Output must be a separate JSON evidence file')
    result = compare(snapshot(args.before), snapshot(args.after))
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ('passed', 'errors', 'checks', 'identical_stream_count')}, indent=2))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
