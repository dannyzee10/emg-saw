"""Small native-export fixtures exercise the authorized translation boundary."""
import argparse
import contextlib
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import astra_verify_routing_delta as verifier


class TranslationVerification(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.before_rows = [
            'COMP|CL_4|Bottom Layer|51.3000|16.0500|180|49.1000|14.8000|53.5000|17.3000',
            'PAD|CL_4|1|NetCL_4_1|Bottom Layer|52.2500|16.0500|51.5500|15.3000|52.9500|16.8000|HOLE=0.0000|ROT=180|SX=1.4000|SY=1.5000|SHAPE=2',
            'PAD|CL_4|2|INA_OUT_4|Bottom Layer|50.3500|16.0500|49.6500|15.3000|51.0500|16.8000|HOLE=0.0000|ROT=180|SX=1.4000|SY=1.5000|SHAPE=2',
            'COMP|U1|Top Layer|20.0000|20.0000|0|19.0000|19.0000|21.0000|21.0000',
            'PAD|U1|1|GND|Top Layer|20.0000|20.0000|19.5000|19.5000|20.5000|20.5000|HOLE=0.0000|ROT=0|SX=1.0000|SY=1.0000|SHAPE=2',
            'TRACK|Top Layer|GND|20.0000|20.0000|21.0000|20.0000|0.2000|INCOMP=False|INPOLY=False|KEEPOUT=False',
        ]
        # Independent explicit after coordinates, not the implementation's transform.
        self.after_rows = [
            'COMP|CL_4|Bottom Layer|48.2000|16.0500|180|46.0000|14.8000|50.4000|17.3000',
            'PAD|CL_4|1|NetCL_4_1|Bottom Layer|49.1500|16.0500|48.4500|15.3000|49.8500|16.8000|HOLE=0.0000|ROT=180|SX=1.4000|SY=1.5000|SHAPE=2',
            'PAD|CL_4|2|INA_OUT_4|Bottom Layer|47.2500|16.0500|46.5500|15.3000|47.9500|16.8000|HOLE=0.0000|ROT=180|SX=1.4000|SY=1.5000|SHAPE=2',
        ] + self.before_rows[3:]
        self.args = argparse.Namespace(before=self.root / 'NATIVE_BB.txt', after=self.root / 'NATIVE_BC.txt',
                                       adds=self.root / 'adds.csv', dels=self.root / 'dels.csv',
                                       output=self.root / 'result.json', tol_mm=.00015,
                                       allow_move=[verifier.translation_spec('CL_4:-3.1:0')])
        for path in (self.args.adds, self.args.dels):
            path.write_text('kind,group,net,layer,x1,y1,x2,y2,w,d,h\n', encoding='utf-8')
        self.write_exports()

    def write_exports(self):
        for path, rows in ((self.args.before, self.before_rows), (self.args.after, self.after_rows)):
            path.write_text('\n'.join(rows + ['READ_ONLY; COMPLETE']) + '\n', encoding='utf-8')

    def check(self):
        self.write_exports()
        return verifier.verify(self.args)

    def test_exact_move_passes_and_retains_native_evidence(self):
        result = self.check()
        self.assertTrue(result['passed'], result['errors'])
        moved = result['allowed_component_translations']['CL_4']
        self.assertEqual(moved['records']['pads']['before_native_records'], self.before_rows[1:3])
        self.assertEqual(moved['records']['pads']['after_native_records'], self.after_rows[1:3])
        self.assertEqual(len(result['raw_native_record_changes']['pads']['removed']), 2)
        self.assertEqual(result['unchanged']['pads']['before_count'], 1)

    def test_move_fails_without_allowance(self):
        self.args.allow_move = []
        self.assertFalse(self.check()['passed'])

    def test_changed_net_on_moved_pad_fails(self):
        self.after_rows[1] = self.after_rows[1].replace('|NetCL_4_1|', '|GND|')
        self.assertFalse(self.check()['passed'])

    def test_another_component_or_pad_move_fails(self):
        for row_index in (3, 4):
            with self.subTest(row_index=row_index):
                original = self.after_rows[row_index]
                self.after_rows[row_index] = original.replace('20.0000', '20.1000')
                self.assertFalse(self.check()['passed'])
                self.after_rows[row_index] = original

    def test_wrong_delta_or_rotation_size_layer_fails(self):
        for index, old, new in ((0, '|48.2000|', '|48.2100|'), (1, '|ROT=180|', '|ROT=90|'),
                                (1, '|SX=1.4000|', '|SX=1.5000|'),
                                (1, '|Bottom Layer|', '|Top Layer|'), (0, '|180|', '|90|')):
            with self.subTest(index=index, field=old):
                original = self.after_rows[index]
                self.after_rows[index] = original.replace(old, new)
                self.assertFalse(self.check()['passed'])
                self.after_rows[index] = original

    def test_missing_or_duplicated_pad_fails(self):
        original = list(self.after_rows)
        self.after_rows.pop(1)
        self.assertFalse(self.check()['passed'])
        self.after_rows = original + [original[1]]
        self.assertFalse(self.check()['passed'])

    def test_unknown_reference_and_duplicate_allowance_fail(self):
        self.args.allow_move = [('UNKNOWN', -3.1, 0)]
        self.assertFalse(self.check()['passed'])
        self.args.allow_move = [('CL_4', -3.1, 0), ('CL_4', -3.1, 0)]
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            self.check()

    def test_unplanned_copper_change_still_fails(self):
        self.after_rows[-1] = self.after_rows[-1].replace('|0.2000|', '|0.2500|')
        self.assertFalse(self.check()['passed'])

    def test_cli_preserves_files_labels_and_hashes(self):
        files = [self.args.before, self.args.after, self.args.adds, self.args.dels]
        originals = {p: p.read_bytes() for p in files}
        argv = ['verify']
        for flag in ('before', 'after', 'adds', 'dels', 'output'):
            argv += ['--' + flag, str(getattr(self.args, flag))]
        argv += ['--allow-move', 'CL_4:-3.1:0']
        with mock.patch('sys.argv', argv), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(verifier.main(), 0)
        report = json.loads(self.args.output.read_text(encoding='utf-8'))
        for path, data in originals.items():
            self.assertEqual(path.read_bytes(), data)
            self.assertEqual(report['inputs'][str(path)]['path'], str(path.resolve()))
            self.assertEqual(report['inputs'][str(path)]['sha256'], hashlib.sha256(data).hexdigest())


class FreePadTranslationVerification(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.before_rows = [
            'COMP|U1|Top Layer|20.0000|20.0000|0|19.0000|19.0000|21.0000|21.0000',
            # A component pad with the same name is not the authorized FREE pad.
            'PAD|U1|TP_GND_DIG|GND|Top Layer|20.0000|20.0000|19.5000|19.5000|20.5000|20.5000|HOLE=0.0000|ROT=0|SX=1.0000|SY=1.0000|SHAPE=2',
            'PAD|FREE|TP_GND_DIG|GND|Top Layer|56.6710|44.8290|56.1210|44.2790|57.2210|45.3790|HOLE=0.0000|ROT=0|SX=1.0000|SY=1.0000|SHAPE=1',
            'PAD|FREE|TP_OTHER|GND|Top Layer|30.0000|30.0000|29.4500|29.4500|30.5500|30.5500|HOLE=0.0000|ROT=0|SX=1.0000|SY=1.0000|SHAPE=1',
        ]
        self.after_rows = list(self.before_rows)
        # Independent explicit expected coordinates: +0.2 mm X, no Y change.
        self.after_rows[2] = 'PAD|FREE|TP_GND_DIG|GND|Top Layer|56.8710|44.8290|56.3210|44.2790|57.4210|45.3790|HOLE=0.0000|ROT=0|SX=1.0000|SY=1.0000|SHAPE=1'
        self.args = argparse.Namespace(before=self.root / 'before.txt', after=self.root / 'after.txt',
                                       adds=self.root / 'adds.csv', dels=self.root / 'dels.csv',
                                       output=self.root / 'result.json', tol_mm=.00015, allow_move=[],
                                       allow_free_pad_move=[verifier.translation_spec('TP_GND_DIG:0.2:0')])
        for path in (self.args.adds, self.args.dels):
            path.write_text('kind,group,net,layer,x1,y1,x2,y2,w,d,h\n', encoding='utf-8')

    def check(self):
        for path, rows in ((self.args.before, self.before_rows), (self.args.after, self.after_rows)):
            path.write_text('\n'.join(rows + ['READ_ONLY; COMPLETE']) + '\n', encoding='utf-8')
        return verifier.verify(self.args)

    def test_named_free_pad_exact_translation_passes(self):
        result = self.check()
        self.assertTrue(result['passed'], result['errors'])
        moved = result['allowed_free_pad_translations']['TP_GND_DIG']
        self.assertTrue(moved['unique_free_pad'])
        self.assertEqual([self.before_rows[2]], moved['before_native_records'])
        self.assertEqual([self.after_rows[2]], moved['after_native_records'])
        self.assertEqual(2, result['unchanged']['pads']['before_count'])
        self.assertEqual('all records', result['unchanged']['comps']['comparison_scope'])

    def test_net_size_layer_hole_rotation_and_shape_changes_fail(self):
        original = self.after_rows[2]
        for old, new in (('|GND|', '|3V3_DIG|'), ('SX=1.0000', 'SX=1.1000'),
                         ('SY=1.0000', 'SY=1.1000'), ('|Top Layer|', '|Bottom Layer|'),
                         ('HOLE=0.0000', 'HOLE=0.2000'), ('ROT=0', 'ROT=90'), ('SHAPE=1', 'SHAPE=2')):
            with self.subTest(field=old):
                self.after_rows[2] = original.replace(old, new)
                self.assertFalse(self.check()['passed'])
        self.after_rows[2] = original

    def test_wrong_center_or_bbox_translation_fails(self):
        original = self.after_rows[2]
        for old, new in (('56.8710', '56.8810'), ('56.3210', '56.1210'),
                         ('57.4210', '57.2210'), ('44.8290', '44.8390')):
            with self.subTest(field=old):
                self.after_rows[2] = original.replace(old, new)
                self.assertFalse(self.check()['passed'])
        self.after_rows[2] = original

    def test_second_free_pad_and_same_named_component_pad_stay_protected(self):
        for index, old, new in ((3, '30.0000', '30.2000'), (1, '20.0000', '20.2000')):
            with self.subTest(index=index):
                original = self.after_rows[index]
                self.after_rows[index] = original.replace(old, new)
                result = self.check()
                self.assertFalse(result['passed'])
                self.assertIn('pads changed', result['errors'])
                self.after_rows[index] = original

    def test_ambiguous_target_before_or_after_fails(self):
        for target in (self.before_rows, self.after_rows):
            with self.subTest(export='before' if target is self.before_rows else 'after'):
                target.append(target[2])
                result = self.check()
                self.assertFalse(result['passed'])
                self.assertFalse(result['allowed_free_pad_translations']['TP_GND_DIG']['unique_free_pad'])
                target.pop()

    def test_missing_renamed_or_component_owned_target_fails(self):
        original = self.after_rows[2]
        for old, new in (('|TP_GND_DIG|', '|RENAMED|'), ('|FREE|', '|U1|')):
            with self.subTest(field=old):
                self.after_rows[2] = original.replace(old, new)
                self.assertFalse(self.check()['passed'])
        self.after_rows.pop(2)
        self.assertFalse(self.check()['passed'])

    def test_missing_allowance_or_duplicate_specification_fails(self):
        self.args.allow_free_pad_move = []
        self.assertFalse(self.check()['passed'])
        self.args.allow_free_pad_move = [('TP_GND_DIG', .2, 0)] * 2
        with self.assertRaisesRegex(ValueError, 'Duplicate --allow-free-pad-move'):
            self.check()

    def test_new_cli_flag_accepts_only_named_free_pad_move(self):
        self.check()
        argv = ['verify']
        for flag in ('before', 'after', 'adds', 'dels', 'output'):
            argv += ['--' + flag, str(getattr(self.args, flag))]
        argv += ['--allow-free-pad-move', 'TP_GND_DIG:0.2:0']
        with mock.patch('sys.argv', argv), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(0, verifier.main())
        report = json.loads(self.args.output.read_text(encoding='utf-8'))
        self.assertEqual(['TP_GND_DIG'], list(report['allowed_free_pad_translations']))
        self.assertEqual({}, report['allowed_component_translations'])


if __name__ == '__main__':
    unittest.main()
