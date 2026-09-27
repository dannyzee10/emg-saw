"""Small rule-selection regressions; no PCB file, CAD, router or geometry engine."""
import struct
import unittest

import astra_audit_trace_rules as audit


def rule(kind, name, priority=1, scope='All', **fields):
    return dict(kind_id=kind, NAME=name, PRIORITY=str(priority), ENABLED='TRUE',
                SCOPE1EXPRESSION=scope, SCOPE2EXPRESSION='All', **fields)


def track(net='SIG', layer='Top Layer', width=.18):
    return dict(kind='TRACK', net=net, layer=layer, values=(0, 0, 1, 0, width), source='synthetic track')


def via(diameter, hole):
    return dict(kind='VIA', net='SIG', layer='', values=(0, 0, diameter, hole), source='synthetic via')


WIDTH = rule(2, 'Width', MINLIMIT='0.15mm', MAXLIMIT='0.5mm')
LAYER = rule(9, 'Layers', **{'TOP LAYER_V5': 'TRUE', 'BOTTOM LAYER_V5': 'TRUE'})
VIA = rule(11, 'Via', MINWIDTH='0.6mm', MAXWIDTH='0.6mm', MINHOLEWIDTH='0.3mm', MAXHOLEWIDTH='0.3mm', VIASTYLE='Through Hole')


class NativeTraceRuleTests(unittest.TestCase):
    def run_checks(self, items, rules, classes=None):
        return audit.audit(items, rules, classes or {}, .00015)[0]

    def test_higher_priority_native_class_rule_wins(self):
        specific = rule(2, 'Switch', 1, "InNetClass('SWITCH')", MINLIMIT='0.2mm', MAXLIMIT='1mm')
        fallback = dict(WIDTH, PRIORITY='2')
        rows = self.run_checks([track('SW')], [fallback, specific, LAYER], {'SWITCH': {'SW'}})
        self.assertEqual('Switch', rows[0]['rule'])
        self.assertEqual('failed', rows[0]['status'])
        self.assertEqual('passed', rows[1]['status'])

    def test_layer_specific_limits_override_global_width(self):
        width = dict(WIDTH, TOPLAYER_MINWIDTH='0.3mm', TOPLAYER_MAXWIDTH='0.4mm')
        rows = self.run_checks([track(), track(layer='Bottom Layer')], [width, LAYER])
        self.assertEqual(['failed', 'passed', 'passed', 'passed'], [r['status'] for r in rows])

    def test_forbidden_layer_fails_and_missing_layer_is_unresolved(self):
        rows = self.run_checks([track(layer='Bottom Layer')], [WIDTH, dict(LAYER, **{'BOTTOM LAYER_V5': 'FALSE'})])
        self.assertEqual('failed', rows[1]['status'])
        rows = self.run_checks([track(layer='Mid Layer 1')], [WIDTH, LAYER])
        self.assertEqual('unresolved', rows[1]['status'])

    def test_unknown_higher_scope_cannot_fall_back_to_all(self):
        unknown = dict(WIDTH, NAME='Unknown', SCOPE1EXPRESSION="InRegionAbsolute(0,0,1,1)")
        rows = self.run_checks([track()], [unknown, dict(WIDTH, PRIORITY='2'), LAYER])
        self.assertEqual('unresolved', rows[0]['status'])
        self.assertIn('Unsupported scope', rows[0]['reason'])
        rows = self.run_checks([track()], [WIDTH, dict(unknown, PRIORITY='2'), LAYER])
        self.assertEqual('passed', rows[0]['status'])

    def test_ambiguous_priority_and_unknown_class_are_unresolved(self):
        for conflicting in (dict(WIDTH, NAME='Other'), dict(WIDTH, SCOPE1EXPRESSION="InNetClass('MISSING')")):
            with self.subTest(scope=conflicting['SCOPE1EXPRESSION']):
                rows = self.run_checks([track()], [WIDTH, conflicting, LAYER])
                self.assertEqual('unresolved', rows[0]['status'])

    def test_native_class_member_keys_and_duplicate_membership(self):
        def record(name, member):
            raw = f'|NAME={name}|KIND=0|SUPERCLASS=FALSE|M0={member}\0'.encode('ascii')
            return struct.pack('<I', len(raw)) + raw
        native = record('CONTROL', 'SIG') + record('CONTROL', 'SIG')
        classes = audit.net_classes(audit.text_records(native))
        self.assertEqual({'SIG'}, classes['CONTROL'])
        conflict = audit.net_classes(audit.text_records(native + record('CONTROL', 'OTHER')))
        self.assertIsNone(conflict['CONTROL'])
        with self.assertRaisesRegex(ValueError, 'unsupported native net class'):
            audit.scope_matches("InNetClass('CONTROL')", 'SIG', conflict)

    def test_via_envelope_reports_current_mismatch_and_aligned_fixture(self):
        items = [via(.45, .2), via(.5, .3), via(.6, .3)]
        rows = self.run_checks(items, [VIA])
        self.assertEqual(['failed', 'failed', 'passed'], [r['status'] for r in rows])
        aligned_fixture = dict(VIA, MINWIDTH='0.45mm', MINHOLEWIDTH='0.2mm')
        self.assertEqual(['passed'] * 3, [r['status'] for r in self.run_checks(items, [aligned_fixture])])

    def test_mil_conversion_and_unsupported_dimension(self):
        self.assertAlmostEqual(.1499997, audit.mm('5.9055mil'))
        with self.assertRaisesRegex(ValueError, 'Unsupported native dimension'):
            audit.mm('0.2')

    def test_netless_copper_uses_default_rules(self):
        rows = self.run_checks([track(net='-')], [WIDTH, LAYER])
        self.assertEqual(['passed', 'passed'], [row['status'] for row in rows])
        self.assertEqual('Width', rows[0]['rule'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
