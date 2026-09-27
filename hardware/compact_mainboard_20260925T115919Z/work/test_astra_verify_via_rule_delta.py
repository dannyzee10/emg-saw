import struct
import unittest

from astra_verify_via_rule_delta import compare, verify_options, verify_rules


def record(fields, kind=None):
    raw = ('|' + '|'.join(k + '=' + v for k, v in fields.items())).encode('ascii') + b'\0'
    return (struct.pack('<I', len(raw)) if kind is None else struct.pack('<HI', kind, len(raw))) + raw


RULE = dict(NAME='VIA_STD_060_030', SCOPE1EXPRESSION='All', SCOPE2EXPRESSION='All', ENABLED='TRUE',
            PRIORITY='1', MINWIDTH='0.60mm', MINHOLEWIDTH='0.30mm', MAXWIDTH='0.60mm', UID='UNCHANGED')
OPTIONS = dict(RULESETTOCHECK='0,2,15', ONLINERULESETTOCHECK='0,2,9,11,15', OTHER='UNCHANGED')


class ViaRuleDeltaTests(unittest.TestCase):
    def board_pair(self):
        streams = {name: b'unchanged' for name in (
            'Rules6/Header', 'Design Rule Checker Options6/Header', 'Pads6/Data',
            'Components6/Data', 'Nets6/Data', 'Classes6/Data', 'Tracks6/Data', 'Vias6/Data')}
        streams.update({'Rules6/Data': record(RULE, 11),
                        'Design Rule Checker Options6/Data': record(OPTIONS),
                        'Board6/Data': record(dict(ORIGINX='0', ORIGINY='0', TIME='12:00'))})
        after = dict(streams)
        after['Rules6/Data'] = record(dict(RULE, MINWIDTH='0.45mm', MINHOLEWIDTH='0.20mm'), 11)
        after['Design Rule Checker Options6/Data'] = record(dict(OPTIONS, RULESETTOCHECK='0,2,9,11,15'))
        return dict(streams=streams), dict(streams=after)

    def test_only_two_minima_and_exact_batch_additions_pass(self):
        new = dict(RULE, MINWIDTH='17.7165mil', MINHOLEWIDTH='7.874mil')
        self.assertTrue(verify_rules(record(RULE, 11), record(new, 11))['passed'])
        self.assertTrue(verify_options(record(OPTIONS), record(dict(OPTIONS, RULESETTOCHECK='0,2,9,11,15')))['passed'])

    def test_scope_enabled_preferred_or_other_rule_change_fails(self):
        new = dict(RULE, MINWIDTH='0.45mm', MINHOLEWIDTH='0.20mm')
        for key, value in [('SCOPE1EXPRESSION', "InNet('GND')"), ('ENABLED', 'FALSE'),
                           ('MAXWIDTH', '0.8mm'), ('UID', 'DIFFERENT')]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                verify_rules(record(RULE, 11), record(dict(new, **{key: value}), 11))
        with self.assertRaises(ValueError):
            verify_rules(record(RULE, 11) + record(dict(NAME='Width', MIN='0.2mm'), 2),
                         record(new, 11) + record(dict(NAME='Width', MIN='0.1mm'), 2))

    def test_ambiguous_duplicate_named_rule_or_field_fails(self):
        new = dict(RULE, MINWIDTH='0.45mm', MINHOLEWIDTH='0.20mm')
        with self.assertRaises(ValueError):
            verify_rules(record(RULE, 11) * 2, record(new, 11) * 2)
        raw = b'|NAME=VIA_STD_060_030|NAME=OTHER\0'
        with self.assertRaises(ValueError):
            verify_rules(struct.pack('<HI', 11, len(raw)) + raw, record(new, 11))

    def test_extra_missing_or_removed_batch_selection_and_other_option_fail(self):
        for batch in ('0,2,9,11,15,17', '0,2,9,15', '0,2,9,11'):
            with self.subTest(batch=batch), self.assertRaises(ValueError):
                verify_options(record(OPTIONS), record(dict(OPTIONS, RULESETTOCHECK=batch)))
        with self.assertRaises(ValueError):
            verify_options(record(OPTIONS), record(dict(OPTIONS, RULESETTOCHECK='0,2,9,11,15', OTHER='CHANGED')))

    def test_geometry_binary_changes_are_never_waived(self):
        before, after = self.board_pair()
        self.assertTrue(compare(before, after)['passed'])
        after['streams']['Pads6/Data'] = b'changed but presumed harmless'
        result = compare(before, after)
        self.assertFalse(result['passed'])
        self.assertIn('Other saved stream changed: Pads6/Data', result['errors'])

    def test_only_explicit_board_view_metadata_is_allowed(self):
        before, after = self.board_pair()
        after['streams']['Board6/Data'] = record(dict(ORIGINX='0', ORIGINY='0', TIME='12:01'))
        self.assertTrue(compare(before, after)['passed'])
        after['streams']['Board6/Data'] = record(dict(ORIGINX='1', ORIGINY='0', TIME='12:01'))
        self.assertFalse(compare(before, after)['passed'])


if __name__ == '__main__':
    unittest.main()
