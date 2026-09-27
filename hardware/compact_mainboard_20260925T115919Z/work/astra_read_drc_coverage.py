"""Read saved Altium batch coverage and rules; never writes an OLE/CAD file."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import struct

import olefile
from astra_verify_pcb_structure import board_parameters


def rules(data):
    result, position = [], 0
    while position < len(data):
        if position + 6 > len(data):
            raise ValueError('Truncated Rules6 prefix')
        kind, length = struct.unpack_from('<HI', data, position)
        position += 6
        if not length or position + length > len(data):
            raise ValueError(f'Unsupported Rules6 framing at {position - 6}')
        raw = data[position:position + length].rstrip(b'\0')
        position += length
        if not raw.startswith(b'|') or b'\0' in raw:
            raise ValueError('Unsupported Rules6 text record')
        fields = dict(field.split('=', 1) for field in raw.decode('latin1').split('|')[1:] if field)
        result.append({'kind_id': kind, **fields})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pcb', type=Path, required=True)
    parser.add_argument('--sdk', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--require-batch', default='')
    args = parser.parse_args()
    if args.output.suffix.lower() != '.json' or args.output.resolve() in (args.pcb.resolve(), args.sdk.resolve()):
        parser.error('Output must be a separate JSON evidence file')
    data = args.pcb.read_bytes()
    with olefile.OleFileIO(io.BytesIO(data)) as document:
        option_data = document.openstream('Design Rule Checker Options6/Data').read()
        rule_data = document.openstream('Rules6/Data').read()
    parameters, _ = board_parameters(option_data)
    if any(len(parameters.get(key, [])) != 1 for key in ('RULESETTOCHECK', 'ONLINERULESETTOCHECK')):
        raise ValueError('Expected one batch and online rule set')
    batch = {int(value) for value in parameters['RULESETTOCHECK'][0].split(',') if value}
    online = {int(value) for value in parameters['ONLINERULESETTOCHECK'][0].split(',') if value}
    enums = {int(value): name for name, value in re.findall(r'^(eRule_\w+)=(\d+)$', args.sdk.read_text().replace('\r', ''), re.M)}
    native_rules = rules(rule_data)
    for rule in native_rules:
        rule['kind_name'] = enums.get(rule['kind_id'], 'UNKNOWN')
        rule['batch_selected'] = rule['kind_id'] in batch
        rule['online_selected'] = rule['kind_id'] in online
    required = {int(value) for value in args.require_batch.split(',') if value}
    report = {
        'pcb': str(args.pcb.resolve()), 'pcb_sha256': hashlib.sha256(data).hexdigest(),
        'options_sha256': hashlib.sha256(option_data).hexdigest(),
        'rules_sha256': hashlib.sha256(rule_data).hexdigest(),
        'batch': {str(value): enums.get(value, 'UNKNOWN') for value in sorted(batch)},
        'online_only': {str(value): enums.get(value, 'UNKNOWN') for value in sorted(online - batch)},
        'enabled_rules_not_in_batch': [r for r in native_rules if r.get('ENABLED', '').upper() == 'TRUE' and not r['batch_selected']],
        'native_rules': native_rules,
        'required_batch_missing': sorted(required - batch),
        'options': parameters,
        'scope': 'Saved batch selection and rule records only; no native DRC was executed.',
    }
    args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    summary = {key: report[key] for key in ('pcb_sha256', 'online_only', 'required_batch_missing')}
    summary['enabled_rules_not_in_batch'] = [{key: rule.get(key) for key in ('kind_id', 'kind_name', 'NAME')}
                                            for rule in report['enabled_rules_not_in_batch']]
    print(json.dumps(summary, indent=2))
    return 1 if required - batch else 0


if __name__ == '__main__':
    raise SystemExit(main())
