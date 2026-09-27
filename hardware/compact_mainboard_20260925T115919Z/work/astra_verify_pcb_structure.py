"""Read-only protected-stream comparison for a saved Altium routing-only edit.

Uses olefile. Writes only --output JSON; never opens an OLE file in write mode.
Usage: python astra_verify_pcb_structure.py --before saved_AZ.PcbDoc
    --after saved_BA.PcbDoc --output structure.json
"""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
import struct
import sys

import olefile


# Full bytes, including headers, are frozen. Any change requires investigation;
# the tool does not guess which bytes in opaque records might be transient.
PROTECTED = {
    'Nets6', 'Rules6', 'Pads6', 'Components6', 'Classes6', 'SignalClasses',
    'Models', 'ModelsNoEmbed', 'ComponentBodies6', 'ShapeBasedComponentBodies6',
    'LayerKindMapping', 'BoardRegions', 'ConstraintManager', 'DifferentialPairs6',
    'EmbeddedBoards6', 'Embeddeds6', 'EmbeddedFonts6', 'Textures',
    'PadViaLibrary', 'PadViaLibraryCache', 'PadViaLibraryLinks',
    'Pin Swap Options6', 'PinPairsSection', 'Coordinates6', 'Dimensions6',
    'Texts', 'Texts6', 'WideStrings6', 'Design Rule Checker Options6',
    'Advanced Placer Options6', 'SmartUnions', 'UnionNames', 'WaivedViolations',
}
REQUIRED = {'Nets6/Data', 'Rules6/Data', 'Pads6/Data', 'Components6/Data',
            'Classes6/Data', 'Board6/Data', 'LayerKindMapping/Data', 'Models/Data'}
COPPER_AND_ROUTING_METADATA = {
    'Tracks6', 'Vias6', 'Arcs6', 'Fills6', 'Regions6', 'ShapeBasedRegions6',
    'Polygons6', 'Connections6', 'FromTos6', 'PrimitiveParameters',
    'UniqueIDPrimitiveInformation', 'ExtendedPrimitiveInformation',
}
SAVE_METADATA = {'FileHeader', 'FileHeaderSix', 'FileVersionInfo'}
VOLATILE_BOARD_KEYS = {
    'DATE', 'TIME', 'SELECTION', 'CURRENT2D3DVIEWSTATE',
    'ZOOMMULT', 'BOARDINSIGHTVIEWCONFIGURATIONNAME', 'VIEWPORTSAREVISIBLE',
}
VOLATILE_BOARD_PREFIXES = ('VP.', 'LOOKAT.', 'EYEROTATION.', 'VIEWSIZE.',
                           '2DCONFIG', '3DCONFIG')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def snapshot(path):
    data = Path(path).read_bytes()
    # Read one immutable in-memory snapshot, so native saves cannot interleave
    # individual stream reads. Parent must still compare after native save.
    import io
    with olefile.OleFileIO(io.BytesIO(data)) as document:
        streams = {'/'.join(name): document.openstream(name).read()
                   for name in document.listdir(streams=True, storages=False)}
    return {'path': str(Path(path).resolve()), 'sha256': sha(data),
            'size': len(data), 'streams': streams}


def board_parameters(data):
    """Parse the observed Board6 length-prefixed pipe-delimited text records.

    Keep duplicate keys as ordered value lists. Reject unfamiliar framing,
    malformed fields, or interior NULs instead of silently dropping content.
    """
    position = 0
    params = defaultdict(list)
    records = 0
    while position < len(data):
        if len(data) - position < 4:
            raise ValueError('Board6 has a truncated length prefix')
        length = struct.unpack_from('<I', data, position)[0]
        position += 4
        if length == 0 or position + length > len(data):
            raise ValueError('Board6 has an invalid text record length')
        raw = data[position:position + length]
        position += length
        raw = raw.rstrip(b'\x00')
        if not raw.startswith(b'|') or b'\x00' in raw:
            raise ValueError('Board6 record is not the supported pipe text format')
        for field in raw.decode('latin1').split('|')[1:]:
            if not field:
                continue
            if '=' not in field:
                raise ValueError('Board6 field lacks an equals sign: ' + field[:80])
            key, value = field.split('=', 1)
            if not key or any(ord(c) < 32 for c in key):
                raise ValueError('Board6 field has an invalid key')
            params[key].append(value)
        records += 1
    return dict(params), records


def board_group(key):
    if key in VOLATILE_BOARD_KEYS or key.startswith(VOLATILE_BOARD_PREFIXES):
        return 'save_or_view_metadata'
    if (key.startswith(('V9_', 'LAYER', 'LAYERV7_', 'PLANE', 'TOP', 'BOTTOM',
                        'SHOWTOPDIELECTRIC', 'SHOWBOTTOMDIELECTRIC', 'MECHPAIR'))):
        return 'stack_and_layer_configuration'
    if key in ('ORIGINX', 'ORIGINY'):
        return 'origin'
    if re.fullmatch(r'(KIND|VX|VY|CX|CY|SA|EA|R)\d+', key) or key.startswith('OUTLINEMODEL'):
        return 'outline'
    return 'other_protected_board_parameter'


def stream_reason(name):
    root = name.split('/')[0]
    if root in COPPER_AND_ROUTING_METADATA:
        return 'Expected routing/repour stream; native geometry delta and DRC must verify it.'
    if root.startswith('T') and root.endswith('Violation'):
        return 'Cached native DRC violations; compare the fresh native DRC report separately.'
    if root in SAVE_METADATA:
        return 'Document format/save history metadata; reported but not interpreted.'
    return None


def body_diagnostic(before, after):
    """Explain model metadata differences without waiving raw-byte failures."""
    fields = re.compile(rb'\|MODELID=([^|]+)\|MODEL.CHECKSUM=([^|]+)'
                        rb'\|MODEL.EMBED=([^|]+)(.*?)\|MODEL.MODELTYPE=([^|]+)', re.S)
    old, new = list(fields.finditer(before)), list(fields.finditer(after))
    ids_and_checksums = re.compile(rb'(?<=MODELID=)[{][0-9A-Fa-f-]{36}[}]'
                                  rb'|(?<=MODEL[.]CHECKSUM=)[0-9]+')
    changed = [(a, b) for a, b in zip(old, new)
               if a.group(1, 2) != b.group(1, 2)]
    return {
        'before_model_record_count': len(old), 'after_model_record_count': len(new),
        'changed_model_record_count': len(changed),
        'only_model_id_and_checksum_fields_differ': bool(old) and len(old) == len(new)
            and ids_and_checksums.sub(b'VALUE', before) == ids_and_checksums.sub(b'VALUE', after),
        'all_changed_models_are_nonembedded_extrusions': bool(changed)
            and all(a.group(3) == b.group(3) == b'FALSE'
                    and a.group(5) == b.group(5) == b'0' for a, b in changed),
        'note': 'Diagnostic only. Raw stream changes remain recorded and are not waived.'
    }


def compare(before, after):
    old, new = before['streams'], after['streams']
    errors, protected, changed_other = [], [], []
    for name in sorted(REQUIRED):
        if name not in old or name not in new:
            errors.append('Required stream missing: ' + name)
    for name in sorted(set(old) | set(new)):
        if name == 'Board6/Data':
            continue
        a, b = old.get(name), new.get(name)
        identical = a == b
        row = {'stream': name, 'unchanged': identical,
               'before_size': len(a) if a is not None else None,
               'after_size': len(b) if b is not None else None,
               'before_sha256': sha(a) if a is not None else None,
               'after_sha256': sha(b) if b is not None else None}
        if name.split('/')[0] in PROTECTED or name == 'Board6/Header':
            if not identical and name in ('ComponentBodies6/Data', 'ShapeBasedComponentBodies6/Data') and a is not None and b is not None:
                row['semantic_diagnostic'] = body_diagnostic(a, b)
            protected.append(row)
            if not identical:
                errors.append('Protected stream changed: ' + name)
        elif not identical:
            reason = stream_reason(name)
            row['reason'] = reason or 'Unclassified changed stream; requires investigation.'
            changed_other.append(row)
            if reason is None:
                errors.append('Unclassified stream changed: ' + name)

    board = {'passed': False, 'changes': [], 'ignored_changes': [], 'group_counts': {}}
    if 'Board6/Data' in old and 'Board6/Data' in new:
        try:
            a, na = board_parameters(old['Board6/Data'])
            b, nb = board_parameters(new['Board6/Data'])
            board.update({'before_sha256': sha(old['Board6/Data']),
                          'after_sha256': sha(new['Board6/Data']),
                          'whole_stream_unchanged': old['Board6/Data'] == new['Board6/Data'],
                          'before_record_count': na, 'after_record_count': nb})
            groups = defaultdict(int)
            for key in sorted(set(a) | set(b)):
                group = board_group(key)
                groups[group] += 1
                if a.get(key) != b.get(key):
                    row = {'key': key, 'group': group,
                           'before': a.get(key), 'after': b.get(key)}
                    target = 'ignored_changes' if group == 'save_or_view_metadata' else 'changes'
                    board[target].append(row)
            board['group_counts'] = dict(groups)
            for group in ('stack_and_layer_configuration', 'origin', 'outline'):
                if not groups[group]:
                    errors.append('Missing Board6 protected parameter group: ' + group)
            if not all(key in a and key in b for key in ('ORIGINX', 'ORIGINY')):
                errors.append('Missing Board6 origin coordinate')
            if board['changes']:
                errors.append(f"{len(board['changes'])} protected Board6 parameters changed")
            board['passed'] = not board['changes'] and all(groups[g] for g in
                ('stack_and_layer_configuration', 'origin', 'outline'))
        except ValueError as exc:
            errors.append(str(exc))
    return {
        'passed': not errors, 'errors': errors,
        'before': {k: v for k, v in before.items() if k != 'streams'},
        'after': {k: v for k, v in after.items() if k != 'streams'},
        'protected_streams': protected, 'board6': board,
        'separate_invariants': {
            'rules_bytes_unchanged': all(old.get(n) == new.get(n) and n in old
                                       for n in ('Rules6/Data', 'Rules6/Header')),
            'nets_bytes_unchanged': all(old.get(n) == new.get(n) and n in old
                                      for n in ('Nets6/Data', 'Nets6/Header')),
            'components_bytes_unchanged': all(old.get(n) == new.get(n) and n in old
                                            for n in ('Components6/Data', 'Components6/Header')),
            'stack_outline_origin_and_other_board_parameters_unchanged': board['passed'],
        },
        'other_changed_streams': changed_other,
        'limitations': [
            'Schematic symbol files are not inputs; this verifies PCB component/pad/model streams.',
            'Opaque protected streams use byte equality; serializer-only changes also require investigation.',
            'Routing/repour streams require the separate native geometry delta check and native DRC.',
            'Only the explicitly listed Board6 save/view parameters may change without failing.',
            'OLE container layout, allocation and directory timestamps are not design content and are ignored.'
        ]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('before', 'after', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    if (args.output.suffix.lower() != '.json' or args.output.resolve() in
            {args.before.resolve(), args.after.resolve()}):
        parser.error('--output must be a separate .json file')
    try:
        result = compare(snapshot(args.before), snapshot(args.after))
    except (OSError, ValueError, struct.error) as exc:
        result = {'passed': False, 'errors': [str(exc)]}
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'passed': result['passed'], 'errors': result['errors'],
                      'protected_stream_count': len(result.get('protected_streams', [])),
                      'board6': result.get('board6', {}),
                      'evidence': str(args.output.resolve())}, indent=2))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
